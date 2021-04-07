from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
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

    def clean(self):
        super().clean()


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


class Position(models.Model):
    # todo 职位不同提供了不同的功能条件
    pass


class WareHouse(models.Model):
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
        db_table = 'sword_ware_house'


class WareHouseLog(models.Model):
    ware_house = models.ForeignKey(
        WareHouse,
        db_constraint=False,
        on_delete=models.DO_NOTHING,
        related_name='log'
    )

    class Meta:
        db_table = 'sword_ware_house_log'


class Device(TimestampedModel):
    ware_house = models.ManyToManyField(
        WareHouse,
        through="WareHouseDeviceShip"
    )
    position = models.ManyToManyField(
        Position,
        through="PositionDeviceShip",
    )


class WareHouseDeviceShip(TimestampedModel):
    ware_house = models.ForeignKey(
        WareHouse,
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
        db_table = 'sword_ware_house_device_ship'


class PositionDeviceShip(TimestampedModel):
    position = models.ForeignKey(
        Position,
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
        db_table = 'sword_position_device_ship'

# todo 设计用户 =>
#
# todo 角色模块 => 不同的角色可以进行不同的操作

# todo 仓库模块 =>

# todo 机器模块 =>

# todo 操作模块 =>

# todo
