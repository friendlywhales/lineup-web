
import re
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.compat import authenticate

from .. import models

_raw_nickname = r'[^\u2000-\u206F\u2E00-\u2E7F\s\'!"#$%&()*+,.\/:;<=>?@\[\]`{|}~]*'
PATTERN_NICKNAME = re.compile(rf"(?:^|\s)({_raw_nickname})", re.UNICODE)


class UserSerializer(serializers.ModelSerializer):
    has_promotion_codes = serializers.SerializerMethodField()
    social_auth = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    lineup_points = serializers.SerializerMethodField()
    has_daily_attendance = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = (
            'username', 'nickname', 'email', 'uid', 'image',
            'level', 'is_verified', 'open_status', 'signup_route',
            'has_promotion_codes', 'social_auth',
            'fullname', 'image',
            'post_count', 'following_count', 'follower_count',
            'lineup_points', 'has_daily_attendance',
            'notification_settings', 'recommended_code',
        )
        extra_kwargs = {
        }

    def validate_nickname(self, value):
        if value is None:
            return

        _range = settings.NICKNAME_LENGTH_RANGE
        if not value:
            raise serializers.ValidationError(_('빈 값은 허용하지 않습니다.'))
        if value.isdigit():
            raise serializers.ValidationError(_('숫자로만 조합할 수 없습니다.'))
        if not (_range[0] <= len(value) <= _range[1]):
            raise serializers.ValidationError(
                _('문자/숫자 혼합 2글자 이상 50글자 이하만 입력 가능합니다.')
            )
        matched = PATTERN_NICKNAME.match(value)
        if not matched or matched.group() != value:
            raise serializers.ValidationError(_('유효하지 않은 문자가 존재합니다.'))
        if models.User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError(_('중복된 유저네임입니다.'))
        return value

    def get_has_promotion_codes(self, obj):
        return obj.promotion_codes.exists()

    def get_social_auth(self, obj):
        return {
            o.provider: {
                'expires': datetime.now() + o.expiration_timedelta(),
                'access_token': o.access_token,
                'username': o.uid,
                'uid': o.uid,
            }
            for o in obj.social_auth.all()
        }

    def get_fullname(self, obj):
        return obj.get_full_name()

    def get_image(self, obj):
        return self.context['request'].build_absolute_uri(obj.image_url)

    def get_post_count(self, obj):
        return obj.post_set.filter(status='published').count()

    def get_following_count(self, obj):
        return obj.following_set.count()

    def get_follower_count(self, obj):
        return obj.follower_set.count()

    def get_lineup_points(self, obj):
        from currencies.models import BehaviourPointLog, PointStatus

        qs = BehaviourPointLog.objects.filter(user=obj)
        qss = {
            'posting': qs.filter(behaviour__code__in=('posting', 'unposting', )),
            'comment': qs.filter(behaviour__code__in=('comment', )),
            'follow': qs.filter(behaviour__code__in=('follow', 'unfollow', )),
            'login': qs.filter(behaviour__code='login'),
            'signup': qs.filter(behaviour__code='signup'),
            'like': qs.filter(behaviour__code__in=(
                'take-like', 'take-unlike', 'give-like', 'give-unlike'
            )),
        }
        sums = {
            k: v.aggregate(point=Sum('point'))['point'] or 0
            for k, v in qss.items()
        }

        sums.update({
            'total': PointStatus.get_user_pointstatus(obj).point,
        })
        return sums

    def get_has_daily_attendance(self, obj):
        from currencies import models as c_models
        behaviour = c_models.Behaviour.objects.get(code='login')
        try:
            return not behaviour._check_login_point(obj)
        except ValueError as e:
            if e.args \
                    and isinstance(e.args[0], dict) \
                    and e.args[0].get('code') == 'daily-limit':
                return True
            return


class ProfilePageSerializer(UserSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = (
            'username', 'uid', 'level',
            'is_verified', 'open_status',
            'fullname', 'image', 'nickname',
            'post_count', 'following_count', 'follower_count',
        )
        extra_kwargs = {
        }

    def get_image(self, obj):
        if obj.image_url:
            return self.context['request'].build_absolute_uri(obj.image_url)
        return


class FollowingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.username

    def get_target(self, obj):
        return obj.target.username

    class Meta:
        model = models.Follower
        fields = ('user', 'target', 'status', )
        extra_kwargs = {
            'user': {
                'read_only': True,
            },
            'target': {
                'read_only': True,
            },
            'status': {
                'read_only': True,
            },
        }


class FollowerSerializer(FollowingSerializer):
    def get_user(self, obj):
        return obj.target.username

    def get_target(self, obj):
        return obj.user.username


class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    _email_validator = EmailValidator()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        qs = models.User.objects.order_by('pk').filter(is_active=True)
        try:
            self._email_validator(username)
            user = qs.get(email=username)
            username = user.username
        except (DjangoValidationError, models.User.DoesNotExist):
            pass
        except MultipleObjectsReturned:
            user = qs.last()
            qs.filter(email=username, pk__lt=user.pk).update(is_active=False)
            username = user.username

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            if not user:
                msg = _('토큰을 발행할 유효한 이용자가 없습니다.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('계정과 비밀번호가 필요합니다.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            'email', 'password',
        )

    def create(self, validated_data):
        email = validated_data['email']
        validated_data['username'] = models.User.make_temp_username(email)
        validated_data['level'] = settings.DEFAULT_USER_LEVEL
        validated_data['open_status'] = 'public'

        obj = models.User.objects.create_user(**validated_data)
        obj.update_model_permissions()
        return obj


