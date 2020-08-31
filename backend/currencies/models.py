
from collections import namedtuple

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils import timezone
from django_mysql.models import Model


class Symbol(Model):
    kinds = (
        ('coin', 'Coin', ),
        ('token', 'Token', ),
    )
    code = models.CharField(_('화폐코드'), max_length=40, unique=True)
    name = models.CharField(_('화폐명'), max_length=40)
    kind = models.CharField(_('종류'), max_length=40, choices=kinds)
    description = models.CharField(_('설명'),
                                   max_length=250,
                                   null=True, blank=True)

    def __str__(self):
        return self.code


class Wallet(Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    balance = models.DecimalField(default=0.0,
                                  max_digits=32,
                                  decimal_places=18)
    default_address = models.CharField(
        _('공통/기본 주소'),
        max_length=128,
        null=True, blank=True,
    )
    deposit_address = models.CharField(
        _('입금 주소'),
        max_length=128,
        null=True, blank=True,
    )
    withdraw_address = models.CharField(
        _('출금 주소'),
        max_length=128,
        null=True, blank=True,
    )
    password = models.CharField(
        _('비밀번호'),
        max_length=250,
        null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'symbol', )


class Transaction(Model):
    id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='received_transactions',
                               on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 related_name='sent_transactions',
                                 on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet,
                               on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=32, decimal_places=18)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def add(cls, sender, receiver, wallet, amount):
        cls.objects.create(
            sender=sender,
            receiver=receiver,
            wallet=wallet,
            amount=amount
        )
        wallet.balance += amount
        wallet.save()


class Behaviour(Model):
    code = models.CharField(
        _('행동코드'),
        unique=True,
        max_length=80,
        help_text=_('소문자, `_` 기호만 허용.'),
    )
    description = models.CharField(
        _('행동설명'), max_length=250, null=True, blank=True
    )
    reward = models.SmallIntegerField(_('행동 보상 포인트'), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def issue_point_to_user(self, user, amount=0, reason=None):
        point = self.reward if self.reward != 0 else amount
        if not user.is_authenticated:
            return

        attr = getattr(self, f'_check_{self.code}_point', None)
        try:
            callable(attr) and attr(user)
        except ValueError as e:
            # todo: logging
            raise

        if point > 0 and not self.allow_issue_point(user, point):
            reason = BehaviourPointLog.reasons.LIMIT_POINT_PER_DAY
            point = 0
        else:
            reason = None

        obj = BehaviourPointLog.objects.create(
            user=user,
            behaviour=self,
            point=point,
            reason=reason,
        )
        PointStatus.update_point(user, obj.point)
        return obj

    def allow_issue_point(self, user, point):
        today = timezone.now().today()
        if not user.is_authenticated:
            return
        qs = user.behaviourpointlog_set \
            .filter(point__gt=0, created_at__date=today) \
            .aggregate(total=models.Sum('point'))
        return not qs['total'] or \
               qs['total'] + point <= settings.LIMITATION_POINT_PER_DAY

    def _check_login_point(self, user):
        if not user.is_authenticated:
            return False
        today = timezone.now().date()
        qs = user.behaviourpointlog_set.filter(
            behaviour=self,
            # created_at__date=today,
            created_at__startswith=today.isoformat(),  # todo: 임시 구현. mysql sql이 `2019-01-01` 이 아닌 2019-01-01 형식으로 만들어져서 제대로 된 lookup이 안 됨.
        )
        if qs.exists():
            raise ValueError({
                'code': 'daily-limit',
                'detail': _('로그인 포인트 보상은 하루에 한 번만 가능합니다.'),
            })
        return True


class BehaviourPointLog(Model):
    reasons = namedtuple('BehaviourPointReason', (
        'LIMIT_POINT_PER_DAY',
        'SUM_UNLIKE_POINT_BY_DELETED_POSTING',
        'INVITED_BY_RECOMMENDED_CODE',
        'INVITE_USER',
    ))(
        'limit-point-per-day',
        'sum_unlike_point_by_deleted_posting',
        'invited_by_recommended_code',
        'invite_user',
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    behaviour = models.ForeignKey(Behaviour, on_delete=models.DO_NOTHING)
    point = models.SmallIntegerField(
        _('행동 포인트'),
        help_text=_('적립 시점의 포인트'),
    )
    reason = models.CharField(_('사유 코드'), max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PointStatus(Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    point = models.IntegerField(_('포인트 현황'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_user_pointstatus(cls, user):
        obj, _ = cls.objects.get_or_create(
            user=user,
            defaults={'point': 0}
        )
        return obj

    @classmethod
    def update_point(cls, user, amount):
        obj, _ = cls.objects.get_or_create(
            user=user,
            defaults={
                'user': user,
                'point': 0,
            }
        )
        obj.point += amount
        obj.save()

