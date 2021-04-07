from django.urls import path, include
from rest_framework import routers

from sword.views.user import UserInfoViewSet, SocialInfoLoginViewSets

router = routers.SimpleRouter()
router.register(prefix='user_info', viewset=UserInfoViewSet)
router.register(prefix='log_in', viewset=SocialInfoLoginViewSets)
urlpatterns = [
    path('', include(router.urls)),
]