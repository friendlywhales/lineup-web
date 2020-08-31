
from django.db import transaction
from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import exceptions as drf_exc
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.decorators import action
from django.utils.translation import ugettext as _
from ratelimit.mixins import RatelimitMixin

from . import serializers
from .. import models


class PromotionCodeViewSet(RatelimitMixin, viewsets.ModelViewSet):
    serializer_class = serializers.PromotionCodeSerializer
    queryset = models.PromotionCode.objects.filter(is_active=True)
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    lookup_field = 'value'
    http_method_names = ('get', 'post', 'head', 'option', )
    ratelimit_key = 'ip'
    ratelimit_rate = '10/m'
    ratelimit_block = True
    ratelimit_method = 'GET'

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.is_available:
            raise drf_exc.NotFound
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise drf_exc.PermissionDenied(
                detail=_('허용하지 않는 접근입니다.'),
                code='not-allowed',
            )
        qs = request.user.promotion_codes.all()

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        raise drf_exc.NotAcceptable

    @action(detail=True, methods=('POST', ),
            pagination_class=permissions.IsAuthenticated, )
    def consume(self, request, value):
        code = self.get_object()
        code.add_to_user(request.user)
        serializer = self.get_serializer(code)
        return Response(serializer.data, status=http_status.HTTP_201_CREATED)

