
from rest_framework import viewsets
from rest_framework import permissions

from apiserver.helpers.rest_framework.paginations import DefaultCursorPaginationClass
from . import serializers
from .. import models


class NotificationPaginationClass(DefaultCursorPaginationClass):
    ordering = ('-created_at', )


class NotificationViewSet(viewsets.ModelViewSet):
    pagination_class = NotificationPaginationClass
    serializer_class = serializers.NotificationSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    lookup_field = 'uid'
    http_method_names = ('get', 'option', 'head', )

    def get_queryset(self):
        return models.Notification.objects.filter(user=self.request.user)

