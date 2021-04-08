from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from core.errcode import TEST_CODE, PARAM_ERROR
from sword.models import User


class PaginationMixin:
    def get_paginated_data(self, data):
        return OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])


class TenPagination(PageNumberPagination, PaginationMixin):
    page_size = 10


class CustomizedJsonResponse(JsonResponse):
    def __init__(self, code_info, data=None, http_status=status.HTTP_200_OK, *args, **kwargs):
        if data is None:
            data = {}
        code_info['data'] = data
        super(CustomizedJsonResponse, self).__init__(
            code_info, json_dumps_params={'ensure_ascii': False}, status=http_status, *args, **kwargs)


class CustomizedJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):
        try:
            check_data = {'id': validated_token['user_id']}
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        user = User.objects.filter(
            **check_data
        ).only(
            'is_active', 'is_staff', 'id', 'display_name', 'avatar'
        ).first()

        if user is None or not user.is_active:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        return user


class CommonListMixin:
    def list(self, request):
        instance = self.get_queryset(request=request)
        return CustomizedJsonResponse(
            self.get_errcode(), data=self.get_page_data(request, instance)
        )


class CommonCreateMixin:
    def create(self, request):
        data = request.data
        serializer = self.get_serializer_class(request=request)(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return CustomizedJsonResponse(
            self.get_errcode(), data=serializer.data, http_status=status.HTTP_201_CREATED
        )


class CommonPutMixin:
    def put(self, request):
        data = request.data
        try:
            instance = self.get_queryset(request=request)
        except ObjectDoesNotExist:
            return CustomizedJsonResponse(
                PARAM_ERROR, http_status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer_class()(data=data)
        serializer.is_valid(raise_exception=True)
        instance.update(**serializer.validated_data)
        return CustomizedJsonResponse(
            self.get_errcode()
        )


class CommonDeleteMixin:
    def delete(self, request):
        try:
            instance = self.get_queryset(request=request)
        except ObjectDoesNotExist:
            return CustomizedJsonResponse(
                PARAM_ERROR, http_status=status.HTTP_404_NOT_FOUND
            )
        instance.delete()
        return CustomizedJsonResponse(
            self.get_errcode()
        )


class GeneralViewSet(GenericViewSet):
    errcode = TEST_CODE

    def get_errcode(self):
        return self.errcode

    def get_queryset(self, **kwargs):
        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def get_serializer_class(self, **kwargs):
        assert self.serializer_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__
        )

        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class(request=self.request)
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_page_data(self, request, instance, serializer=None):
        page = self.paginator
        pages = page.paginate_queryset(queryset=instance, request=request, view=self)
        if serializer is None:
            serializers = self.get_serializer(instance=pages, many=True)
        else:
            serializers = serializer(instance=pages, many=True, context=self.get_serializer_context())

        return page.get_paginated_data(serializers.data)
