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
    phones = serializers.StringRelatedField(many=True, source='social_info', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'creation_date', 'display_name', 'avatar', 'modification_date', 'phones', 'password'
        ]
        read_only_fields = [
            'id'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class GenericImageSerializer(serializers.ModelSerializer):
    pass


class PositionSerializer(serializers.ModelSerializer):
    pass


class DeviceSerializer(serializers.ModelSerializer):
    pass


class WarehouseSerializer(serializers.ModelSerializer):
    pass


class WarehouseLogSerializer(serializers.ModelSerializer):
    pass
