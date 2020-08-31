
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


app_name = 'operations-api'

router = DefaultRouter()
router.register(r'promotion-codes', views.PromotionCodeViewSet, base_name='promotion_code')

urlpatterns = [
    path('', include(router.urls))
]
