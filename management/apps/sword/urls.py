from django.urls import path, include
from rest_framework import routers

from sword.views import user
from sword.views.user import UserInfoViewSet, SocialInfoLoginViewSets, DeviceInfo

router = routers.SimpleRouter()
router.register(prefix='user_info', viewset=UserInfoViewSet)
router.register(prefix='log_in', viewset=SocialInfoLoginViewSets)
router.register(prefix='device_info', viewset=DeviceInfo)

urlpatterns = [
    path('', include(router.urls)),
    # path('device_info/', user.DeviceInfo.as_view())
]