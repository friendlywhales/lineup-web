from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from accounts.api.views import obtain_auth_token
from accounts.social import views as social_auth_views
from operations.views import index


urlpatterns = [
    path('api/v1/accounts/', include('accounts.api.urls')),
    path('api/v1/contents/', include('contents.api.urls')),
    path('api/v1/messaging/', include('messaging.api.urls')),
    path('api/v1/operations/', include('operations.api.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token),
    path('social/', include('social_django.urls')),
    url('^social-auth/login/done/$', social_auth_views.done),
    # url('^social-auth/login/done/(?P<backend>[^/]+)/$', social_auth_views.done),
    path('contents/', include('contents.urls'), name='asset'),
]

if settings.DEBUG:
    schema_view = get_schema_view(
       openapi.Info(
          title="Snippets API",
          default_version='v1',
          description="lineup api",
          terms_of_service="https://www.google.com/policies/terms/",
          contact=openapi.Contact(email="contact@snippets.local"),
          license=openapi.License(name="BSD License"),
       ),
       validators=['flex', 'ssv'],
       public=True,
       permission_classes=(permissions.IsAdminUser,),
    )

    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
    urlpatterns.extend([
        url(r'^silk/', include('silk.urls', namespace='silk')),
        url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    ])

urlpatterns.append(url(r'', index))
