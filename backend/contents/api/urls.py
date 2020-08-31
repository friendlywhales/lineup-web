
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


app_name = 'contents-api'

router = DefaultRouter()
router.register(r'collections', views.CollectionViewSet, base_name='collection')
router.register(r'posts', views.PostViewSet, base_name='post')
router.register(r'tags', views.TagViewSet, base_name='tag')
router.register(r'post-collections', views.PostCollectionViewSet, base_name='post-collection')

urlpatterns = [
    path('', include(router.urls))
]
