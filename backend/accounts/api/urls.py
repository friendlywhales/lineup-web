
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


app_name = 'accounts-api'

router = DefaultRouter()
router.register(r'users', views.UserViewSet, base_name='user')
router.register(r'profiles', views.ProfileViewSet, base_name='profile')

urlpatterns = [
    path('', include(router.urls))
]
