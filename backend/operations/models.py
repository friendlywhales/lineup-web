
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _
from django_mysql.models.fields import JSONField
from rest_framework import exceptions as drf_exc

from apiserver.helpers.models import DateTimeModel


class PromotionCode(DateTimeModel):
    value = models.CharField(_('프로모션 코드'), max_length=32, unique=True)
    extra = JSONField(default=dict, blank=True)
    is_active = models.BooleanField(_('활성화 상태'), default=True)
    allow_quantity = models.PositiveSmallIntegerField(_('허용 사용 개수'), default=1)
    expired_at = models.DateTimeField(_('만료일시'), null=True, blank=True)

    def __str__(self):
        return self.value

    def add_to_user(self, user):
        from accounts.models import UserPromotionCode
        count = UserPromotionCode.objects.filter(user=user).count()
        if count >= settings.MAX_USER_PROMOTION_CODE_NUMBER:
            raise drf_exc.ValidationError({
                'detail': _('더이상 사용할 수 없습니다.'),
                'code': 'exceeded',
            })

        if self.users.filter(user__pk=user.pk).exists():
            raise drf_exc.ValidationError({
                'detail': _('이미 사용 중입니다.'),
                'code': 'duplicated'
            })

        if not self.is_available:
            raise drf_exc.ValidationError({
                'detail': _('없거나 유효하지 않습니다.'),
                'code': 'unavailable'
            })

        return UserPromotionCode.objects.create(
            user=user,
            code=self,
        )

    @property
    def is_available(self):
        result = self.allow_quantity == 0
        result |= 0 < self.allow_quantity and self.users.count() < self.allow_quantity
        result &= not (self.expired_at and self.expired_at <= timezone.now())
        return self.is_active and result

    @classmethod
    def check_available_value(cls, value):
        try:
            obj = cls.objects.get(value=value)
        except cls.DoesNotExist:
            return False
        return obj.is_available

    @property
    def reward_coin(self) -> Decimal:
        return Decimal(self.extra.get('lineup_coin', '0.0'))
