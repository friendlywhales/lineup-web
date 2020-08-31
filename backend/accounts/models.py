
import os
import random
from uuid import uuid4
from collections import namedtuple

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group
from rest_framework import exceptions as drf_exc
from django_mysql.models.fields import JSONField
from django.db.utils import OperationalError, IntegrityError

from apiserver.helpers.models import DateTimeModel


def _image_upload_to(instance, filename):
    uid = instance.uid.hex
    _, ext = os.path.splitext(filename)
    filename = f'{uid}{ext}'
    return os.path.join('u', uid[0], uid[1], uid[2], uid[3], filename)


def default_notification_settings():
    return {
        'liked_my_post': True,
        'new_comment_user_posted': True,
        'my_new_follower': True,
        'following_new_post': True,
    }


def _default_recommended_code():
    limit = 8
    letters = 'ABEFGHJKMPQRSTWXYZ2345789'
    code = ''
    while True:
        code += random.choice(letters)
        length = len(code)
        if length < limit:
            continue
        code = code[:8]
        if not any([True for f in User._meta.fields if f.name == 'recommended_code']):
            break
        try:
            if not User.objects.filter(recommended_code=code).exists():
                break
        except OperationalError:
            break
        except IntegrityError:
            code = ''
    return code


class User(AbstractUser, DateTimeModel):
    open_statuses = (
        ('private', _('비공개'), ),
        ('public', _('공개'), ),
    )
    levels = (
        ('associate', _('준회원'), ),
        ('corporate', _('기업회원'), ),
        ('regular', _('정회원'), ),
        ('author', _('작가회원'), ),
    )
    signup_routes = (
        ('lineup', _('라인업 직접가입'), ),
        ('steem', _('스팀 계정'), ),
    )
    id = models.BigAutoField(primary_key=True)
    uid = models.UUIDField(default=uuid4, unique=True, editable=False)
    nickname = models.CharField(max_length=50, null=True, blank=False)
    image = models.ImageField(null=True, blank=True, upload_to=_image_upload_to)
    level = models.CharField(_('등급'), max_length=40, choices=levels)
    is_verified = models.BooleanField(_('인증여부'), default=False)
    open_status = models.CharField(_('상태'),
                                   max_length=40,
                                   choices=open_statuses)
    signup_route = models.CharField(_('가입경로'),
                                    max_length=40,
                                    choices=signup_routes,
                                    default='lineup')

    notification_settings = JSONField(default=default_notification_settings)
    recommended_code = models.CharField(
        _('추천인 코드'),
        max_length=8,
        unique=True,
        editable=False,
        default=_default_recommended_code,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('추천인'),
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )

    perm_group_names = namedtuple(
        'PERM_GROUP_NAMES',
        ('associate', 'corporate', 'regular', 'author', )
    )(
        associate='associate-user-permission-group',
        corporate='corporate-user-permission-group',
        regular='regular-user-permission-group',
        author='author-user-permission-group',
    )

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    @property
    def image_url(self):
        try:
            return self.image.url
        except Exception:
            pass
        try:
            social = self.social_auth.filter(provider='steemconnect').first()
            return social.extra_data['account']['json_metadata']['profile']['profile_image']
        except (AttributeError, KeyError):
            return

    def update_model_permissions(self):
        try:
            group_name = getattr(self.perm_group_names, self.level)
        except AttributeError:
            # todo: error logging
            return self
        group, _ = Group.objects.get_or_create(name=group_name)
        self.groups.clear()
        self.groups.add(group)
        return self

    @property
    def is_available_behaviour(self):
        return self.is_active and not self.is_staff

    @classmethod
    def make_temp_username(cls, email):
        while True:
            username = f"{email.split('@')[0]}_{uuid4().hex[:3]}"
            if not cls.objects.filter(username=username).exists():
                return username

    def create_lineup_wallet(self):
        from currencies import models as cr_models

        if self.is_staff or not self.is_active:
            return

        symbol = cr_models.Symbol.objects \
            .get(code=settings.SERVICE_TOKEN_SYMBOL)
        obj, __ = cr_models.Wallet.objects.get_or_create(
            user=self,
            symbol=symbol,
            defaults={
                'deposit_address': uuid4().hex,
                'withdraw_address': uuid4().hex,
            },
        )
        return self

    def create_bezant_wallet(self, password: str):
        from currencies import models as cr_models
        from currencies.tasks import create_bezant_wallet

        address = create_bezant_wallet(password)
        symbol = cr_models.Symbol.objects.get(code='bznt')
        cr_models.Wallet.objects.get_or_create(
            user=self,
            symbol=symbol,
            defaults={
                'default_address': address,
            },
        )
        return self

    @property
    def notification_tokens(self):
        return tuple([
            o[0]
            for o in self.notificationtoken_set.values_list('token').all()
        ])

    @property
    def display_name(self):
        return self.nickname or self.username

    def link_inviter(self, inviter):
        self.invited_by = inviter
        self.save()


class Follower(DateTimeModel):
    statuses = (
        ('requested', _('요청'), ),
        ('approved', _('수락'), ),
        ('auto_approved', _('자동수락'), ),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='following_set',
                             on_delete=models.CASCADE)
    target = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='follower_set',
                               on_delete=models.CASCADE)
    status = models.CharField(_('요청상태'), choices=statuses, max_length=40)

    @classmethod
    def follow(cls, user, target, status='auto_approved'):
        from currencies import tasks

        if not user.has_perm('accounts.add_follower'):
            raise drf_exc.PermissionDenied
        cls.check_self_behaviour(user, target)
        cls.check_available_behaviour(user, _('타인을 팔로잉 할 수 없는 이용자입니다.'))
        cls.check_available_behaviour(target, _('팔로잉 할 수 없는 대상 이용자입니다.'))

        qs = user.following_set.filter(target=target)
        if qs.exists():
            follow = qs.first()
            if follow.status == 'requested':
                raise drf_exc.ValidationError(
                    detail=_('팔로잉 요청 응답을 기다리는 중입니다.'),
                    code='pending'
                )
            else:
                raise drf_exc.ValidationError(
                    detail=_('이미 팔로잉 중입니다.'),
                    code='duplicated'
                )
        o = cls(user=user, target=target, status=status)
        o.save()
        tasks.issue_follow_point(user, target)
        return o

    @classmethod
    def unfollow(cls, user, target) -> bool:
        from currencies import tasks

        if not user.has_perm('accounts.delete_follower'):
            raise drf_exc.PermissionDenied
        follow = user.following_set.filter(target=target).first()
        if follow:
            follow.delete()
            tasks.issue_unfollow_point(user, target)
            return True
        else:
            raise drf_exc.NotFound

    @staticmethod
    def check_self_behaviour(user, target):
        if user == target:
            raise drf_exc.ValidationError(
                detail=_('자기 자신을 팔로잉 할 수 없습니다.'),
                code='not-allowed-self'
            )

    @staticmethod
    def check_available_behaviour(user, msg=None):
        if not user.is_available_behaviour:
            raise drf_exc.ValidationError(
                detail=msg or _('팔로잉 할 수 없는 이용자이거나 대상입니다.'),
                code='invalid-target'
            )

    def notify(self):
        from messaging.models import Notification
        Notification.notify_my_new_follower(self)


class UserPromotionCode(DateTimeModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='promotion_codes',
                             on_delete=models.CASCADE)
    code = models.ForeignKey('operations.PromotionCode',
                             related_name='users',
                             on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'code', )
