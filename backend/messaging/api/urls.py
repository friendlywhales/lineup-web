
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


app_name = 'messaging-api'

router = DefaultRouter()
router.register(r'notifications',
                views.NotificationViewSet,
                base_name='notification')

urlpatterns = [
    path('', include(router.urls))
]
