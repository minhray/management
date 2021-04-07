from django.contrib.auth.backends import ModelBackend
from rest_framework.exceptions import AuthenticationFailed

from sword.models import UserSocialInfo


class SocialBackend(ModelBackend):

    def authenticate(self, request, open_id=None, provider='WeChat', **kwargs):
        try:
            if open_id is None or not open_id:
                raise AuthenticationFailed(
                    "OPEN_ID 不可为空。"
                )
            social_info = UserSocialInfo.objects.select_related(
                'user'
            ).get(
                uid=open_id,
                provider=provider
            )
            user = social_info.user
        except (
                AttributeError, TypeError, ValueError, AuthenticationFailed, UserSocialInfo.DoesNotExist
        ):
            user = None

        return user


class CommonBackend(ModelBackend):

    def authenticate(self, request, phone=None, password=None, **kwargs):
        try:
            if phone is None or not phone or password is None or not password:
                raise AuthenticationFailed(
                    "关键信息不可为空。"
                )
            social_info = UserSocialInfo.objects.select_related(
                'user'
            ).get(
                uid=phone,
                provider='Phone'
            )
            user = social_info.user
            is_correct = user.check_password(password)
            if not is_correct:
                raise AuthenticationFailed(
                    "密码错误"
                )
        except (
                AttributeError, TypeError, ValueError, AuthenticationFailed, UserSocialInfo.DoesNotExist
        ):
            user = None

        return user
