
from django.urls import re_path, path

from . import views


app_name = 'contents'

urlpatterns = [
    # re_path(r'^(?P<uid>\w+)/$', views.asset_redirect, name='asset-redirect'),
    path('assets/<str:uid>/', views.asset_redirect, name='asset-redirect'),
]
