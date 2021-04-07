from rest_framework import serializers

from sword.models import User, UserSocialInfo

time_format = "%Y年-%m月-%d日  %H:%M:%S"


class UserSocialInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialInfo
        fields = [
            'uid', 'provider'
        ]


class UserSerializers(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format=time_format, read_only=True
    )
    modification_date = serializers.DateTimeField(
        format=time_format, read_only=True
    )
    social_info = UserSocialInfoSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'creation_date', 'display_name', 'avatar', 'modification_date', 'social_info'
        ]
        read_only_fields = [
            'id'
        ]
