from django.contrib.auth import user_logged_in, authenticate
from django.contrib.auth.hashers import make_password
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from core.errcode import PARAM_ERROR, TOKEN_INFO, WE_CHAT_ERROR, USER_INFO
from sword.models import User, UserSocialInfo
from sword.serializsers import UserSerializers
from core.utils.addtinal_rest_framework import CustomizedJWTAuthentication, TenPagination, CustomizedJsonResponse, \
    GeneralViewSet, CommonListMixin


class SocialInfoLoginViewSets(GenericViewSet):
    queryset = User.objects.all()
    authentication_classes = [CustomizedJWTAuthentication]
    permission_classes = [AllowAny]
    serializer_class = UserSerializers
    pagination_class = TenPagination

    def create(self, request):
        data = request.data
        js_code = data.get('code', None)
        open_id = None
        if js_code is not None:
            # open_id = we_chat.code2session(js_code)
            open_id = js_code
            if open_id is None:
                return CustomizedJsonResponse(
                    WE_CHAT_ERROR, http_status=status.HTTP_400_BAD_REQUEST
                )

        phone = data.get('phone', None)
        password = data.get('password', None)
        provider = data.get('provider', 'WeChat')

        user = authenticate(request=request, open_id=open_id, phone=phone, password=password, provider=provider)

        if user is not None:
            pass
        elif open_id is not None or (phone is not None and password is not None):
            display_name = data.get('display_name', None)
            if display_name is None or (phone is not None and UserSocialInfo.objects.filter(
                    provider='Phone',
                    uid=phone
            ).exists()):
                return CustomizedJsonResponse(
                    PARAM_ERROR, http_status=status.HTTP_400_BAD_REQUEST
                )
            if password is not None:
                password = make_password(password)

            user = self.queryset.create(
                display_name=display_name,
                avatar=None,
                password=password
            )

            if open_id is not None:
                UserSocialInfo.objects.create(
                    user=user,
                    uid=open_id,
                    provider=provider
                )
            elif phone is not None:
                UserSocialInfo.objects.create(
                    user=user,
                    uid=phone,
                    provider='Phone'
                )
        else:
            return CustomizedJsonResponse(
                PARAM_ERROR, http_status=status.HTTP_400_BAD_REQUEST
            )

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


class UserInfoViewSet(GeneralViewSet, CommonListMixin):
    queryset = User.objects.prefetch_related(
        Prefetch('social_info', queryset=UserSocialInfo.objects.filter(
            provider='Phone'
        ).all())
    ).all()
    serializer_class = UserSerializers
    errcode = USER_INFO
    pagination_class = TenPagination
    authentication_classes = [CustomizedJWTAuthentication]
    permission_classes = [IsAuthenticated]
