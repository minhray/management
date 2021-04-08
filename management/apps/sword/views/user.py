from django.contrib.auth import user_logged_in, authenticate
from django.contrib.auth.hashers import make_password
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from core.errcode import PARAM_ERROR, TOKEN_INFO, USER_INFO
from sword.models import User, UserSocialInfo
from sword.serializsers import UserSerializers, UserSocialInfoSerializer
from core.utils.addtinal_rest_framework import CustomizedJWTAuthentication, TenPagination, CustomizedJsonResponse, \
    GeneralViewSet, CommonListMixin, CommonPutMixin


class SocialInfoLoginViewSets(GenericViewSet):
    queryset = User.objects.all()
    authentication_classes = [CustomizedJWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = UserSerializers
    pagination_class = TenPagination

    def create(self, request):
        data = request.data
        # js_code = data.get('code', None)
        open_id = None
        # if js_code is not None:
        #     open_id = we_chat.code2session(js_code)
        #     if open_id is None:
        #         return CustomizedJsonResponse(
        #             WE_CHAT_ERROR, http_status=status.HTTP_400_BAD_REQUEST
        #         )

        phone = data.get('phone', None)
        provider = data.get('provider', 'WeChat')
        if open_id is not None:
            data['uid'] = open_id
            data['provider'] = provider
        elif phone is not None:
            data['uid'] = phone
            data['provider'] = 'Phone'

        password = data.get('password', None)
        if (phone is not None and password is None) or (phone is None and password is not None):
            return CustomizedJsonResponse(
                PARAM_ERROR, http_status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request=request, open_id=open_id, phone=phone, password=password, provider=provider)

        if user is not None:
            pass
        else:
            if (phone is not None and UserSocialInfo.objects.filter(
                    provider='Phone',
                    uid=phone
            ).exists()):
                return CustomizedJsonResponse(
                    PARAM_ERROR, data='密码错误', http_status=status.HTTP_400_BAD_REQUEST
                )
            social_info_serializer = UserSocialInfoSerializer(data=data, context=self.get_serializer_context())
            social_info_serializer.is_valid(raise_exception=True)
            if password is not None:
                data['password'] = make_password(password)

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            social_info_serializer.save(user=user)

        # 生成token
        token = RefreshToken.for_user(
            user
        )
        # 发送登录信号
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        data = {
            'access_token': "Bearer {}".format(str(token.access_token)),
            'refresh': "Bearer {}".format(str(token))
        }

        return CustomizedJsonResponse(
            TOKEN_INFO, data
        )


class UserInfoViewSet(GeneralViewSet, CommonListMixin, CommonPutMixin):
    queryset = User.objects.prefetch_related(
        Prefetch('social_info', queryset=UserSocialInfo.objects.filter(
            provider='Phone'
        ).all())
    ).order_by('-id').all()
    serializer_class = UserSerializers
    errcode = USER_INFO
    pagination_class = TenPagination
    authentication_classes = [CustomizedJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self, **kwargs):
        value_list = [
            'id', 'creation_date', 'display_name', 'avatar', 'modification_date'
        ]
        return self.queryset.only(
            *value_list
        ).filter(
            pk=kwargs['request'].user.id
        )
