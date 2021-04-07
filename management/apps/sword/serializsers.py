from rest_framework import serializers

from sword.models import User, UserSocialInfo


class UserSocialInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialInfo
        fields = [
            'uid', 'provider'
        ]


class UserSerializers(serializers.ModelSerializer):
    social_info = UserSocialInfoSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'creation_date', 'display_name', 'avatar', 'modification_date' 'social_info'
        ]
        read_only_fields = [
            'creation_date', 'modification_date'
        ]
