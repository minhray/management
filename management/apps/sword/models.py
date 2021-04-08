from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from management.apps.core.models import TimestampedModel


class AbstractUser(AbstractBaseUser):
    password = models.CharField(
        max_length=128,
        null=True
    )
    is_staff = models.BooleanField(
        default=False
    )
    is_active = models.BooleanField(
        default=True
    )
    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        abstract = True


class GenericImage(TimestampedModel):
    image = models.URLField()
    content_type = models.ForeignKey(
        ContentType,
        db_constraint=False,
        on_delete=models.DO_NOTHING,
    )
    status = models.CharField(
        default='active',
        max_length=25
    )
    object_id = models.PositiveIntegerField()
    image_content = GenericForeignKey()

    class Meta:
        db_table = 'sword_generic_image'


class GenericType(TimestampedModel):
    type = models.CharField(
        max_length=40
    )
    group = models.CharField(
        max_length=40
    )

    class Meta:
        db_table = 'sword_generic_type'
        unique_together = [
            'type', 'group'
        ]


class GenericValue(TimestampedModel):
    generic_type = models.ForeignKey(
        GenericType,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='general_value'
    )
    value = models.CharField(
        max_length=40
    )
    status = models.CharField(
        default='active',
        max_length=20
    )

    class Meta:
        db_table = 'sword_generic_value'


class Position(TimestampedModel):
    name = models.CharField(
        max_length=25
    )
    description = models.CharField(
        max_length=400
    )
    department = models.CharField(
        max_length=45
    )


class User(AbstractUser, TimestampedModel):
    # user 登录表 查看用户登录有效状态绑定多表关系
    display_name = models.CharField(
        max_length=20,
        help_text="展示名字"
    )
    avatar = models.URLField(
        help_text="用户头像",
        null=True
    )
    position = models.ForeignKey(
        Position,
        db_constraint=False,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name='user'
    )
    USERNAME_FIELD = 'id'

    def __str__(self):
        return str(self.id)


class UserSocialInfo(TimestampedModel):
    user = models.ForeignKey(
        User,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='social_info'
    )
    uid = models.CharField(
        help_text='账户验证信息',
        max_length=40
    )
    provider = models.CharField(
        help_text='账户提供方',
        max_length=15
    )

    class Meta:
        db_table = 'sword_user_social_info'


class AccountConfirmation(TimestampedModel):
    user = models.ForeignKey(
        User,
        db_constraint=False,
        on_delete=models.CASCADE,
        related_name='account_confirmation'
    )
    verification_account = models.CharField(
        max_length=20,
        help_text='验证账户'
    )
    verification_credential = models.CharField(
        max_length=20,
        help_text='验证凭证'
    )
    credential_expiration_date = models.DateTimeField(
        help_text='凭证过期时间'
    )
    credential_group = models.CharField(
        max_length=20,
        help_text='凭证分组'
    )

    class Meta:
        db_table = 'sword_account_confirmation'


class Warehouse(models.Model):
    name = models.CharField(
        max_length=45
    )
    units = models.IntegerField(
        default=0
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    volume = models.DecimalField(
        max_digits=10,
        decimal_places=4
    )

    class Meta:
        db_table = 'sword_warehouse'


class WarehouseLog(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        db_constraint=False,
        on_delete=models.DO_NOTHING,
        related_name='log'
    )

    class Meta:
        db_table = 'sword_warehouse_log'


class Device(TimestampedModel):
    warehouse = models.ManyToManyField(
        Warehouse,
        through="WarehouseDeviceShip"
    )
    user = models.ManyToManyField(
        User,
        through="UserDeviceShip",
    )
    images = GenericRelation(
        GenericImage,
        related_name='device'
    )
    group = models.CharField(
        max_length=45
    )
    name = models.CharField(
        max_length=45
    )
    inventory = models.JSONField(
        default={}
    )


class WarehouseDeviceShip(TimestampedModel):
    warehouse = models.ForeignKey(
        Warehouse,
        db_constraint=False,
        on_delete=models.CASCADE
    )
    device = models.ForeignKey(
        Device,
        db_constraint=False,
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        default='laid-up',
        max_length=20
    )

    class Meta:
        db_table = 'sword_warehouse_device_ship'


class UserDeviceShip(TimestampedModel):
    user = models.ForeignKey(
        User,
        db_constraint=False,
        on_delete=models.CASCADE,
    )
    device = models.ForeignKey(
        Device,
        db_constraint=False,
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        default='active',
        max_length=20
    )

    class Meta:
        db_table = 'sword_user_device_ship'
