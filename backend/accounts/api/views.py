
import typing

from django.conf import settings
from django.contrib.auth import login as django_login
from django.utils.translation import ugettext as _
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status as http_status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import exceptions as drf_exc
from rest_framework.authtoken import views as drf_views
from rest_framework.authtoken.models import Token

from apiserver.helpers.rest_framework import permissions as g_permissions
from apiserver.helpers.rest_framework.paginations import DefaultCursorPaginationClass
from apiserver.helpers.images import get_base64_image
from . import serializers
from .. import models


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.filter(is_active=True).exclude(is_staff=True)
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        # permissions.IsAuthenticated,
    )
    lookup_field = 'uid'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        return models.User.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            raise drf_exc.PermissionDenied
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user != obj:
            raise drf_exc.PermissionDenied
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user != obj:
            raise drf_exc.PermissionDenied
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=('POST', ), permission_classes=())
    def signup(self, request, *args, **kwargs):
        from currencies import tasks

        if request.user.is_authenticated:
            raise drf_exc.ValidationError(
                detail=_('로그인 상태에서는 회원가입을 할 수 없습니다.'),
                code='login-status',
            )
        serializer = serializers.SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        inviter = self._get_inviter_by_recommended_code(
            request.data.get('recommended_code')
        )
        serializer.instance.link_inviter(inviter)

        serializer.instance.create_lineup_wallet()

        serializer = serializers.UserSerializer(
            instance=serializer.instance,
            context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        tasks.issue_signup_point(serializer.instance)
        return Response(serializer.data,
                        status=http_status.HTTP_201_CREATED,
                        headers=headers)

    @action(
        detail=False,
        methods=('POST', ),
        url_path='check-recommended-code',
        permission_classes=(),
    )
    def check_recommended_code(self, request, *args, **kwargs):
        self._get_inviter_by_recommended_code(request.data['recommended_code'])
        return Response({})

    def _get_inviter_by_recommended_code(self, code: typing.Optional[str]):
        if not code:
            return
        code = code.strip()
        try:
            if len(code) != 8:
                raise ValueError
            return models.User.objects.get(recommended_code=code)
        except (KeyError, ValueError):
            raise drf_exc.ValidationError({
                'detail': _('유효하지 않은 추천인 코드입니다.'),
                'code': 'invalid-recommended-code',
            })
        except models.User.DoesNotExist:
            raise drf_exc.ValidationError({
                'detail': _('존재하지 않는 추천인 코드입니다.'),
                'code': 'invalid-recommended-code',
            })

    @action(detail=False,
            permission_classes=(
                    permissions.IsAuthenticated,
            ),
            methods=('GET', ))
    def me(self, request):
        if not request.user.is_authenticated:
            raise drf_exc.PermissionDenied
        serializer = self.serializer_class(
            instance=request.user,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=False,
            permission_classes=(
                    permissions.IsAuthenticated,
            ),
            methods=('GET', ))
    def followings(self, request):
        qs = models.Follower.objects.filter(user=request.user)
        serializer = serializers.FollowingSerializer(
            qs,
            many=True,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=False,
            permission_classes=(
                    permissions.IsAuthenticated,
            ),
            methods=('GET', ))
    def followers(self, request):
        qs = models.Follower.objects.filter(target=request.user)
        serializer = serializers.FollowerSerializer(
            qs, many=True,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=False,
            permission_classes=(
                    permissions.IsAuthenticated,
            ),
            methods=('GET', ))
    def collections(self, request, **kwargs):
        from contents.api import serializers as c_serializers
        qs = request.user.collection_set.all()
        serializer = c_serializers.CollectionSerializer(
            qs,
            many=True,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=False, methods=('GET', ), url_path='access-token',
            permission_classes=(permissions.IsAuthenticated, ))
    def access_token(self, request, **kwargs):
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response({'token': token.key, 'username': request.user.username})

    @action(detail=False, url_path='social-connect', methods=('POST', ),
            permission_classes=(permissions.IsAuthenticated, ))
    def social_connect(self, request):
        token = request.data.get('token', '').strip()
        provider = request.data.get('provider', '').strip()
        if not token or not provider:
            raise drf_exc.ValidationError({
                'code': 'invalid-data',
                'detail': _('유효하지 않은 요청 데이터입니다.'),
            })

        try:
            token = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise drf_exc.AuthenticationFailed({
                'code': 'invalid-auth-token',
                'detail': _('유효하지 않은 요청자의 인증 정보입니다.'),
            })

        target = token.user
        current_social_auth = request.user.social_auth.filter(provider=provider).first()

        if not current_social_auth:
            raise drf_exc.ValidationError({
                'code': 'invalid-provider',
                'detail': _('유효하지 않은 소셜 제공자 정보입니다.'),
            })

        target.social_auth.filter(provider=provider).delete()
        current_social_auth.user = target
        current_social_auth.save()
        if not request.user.social_auth.exists():
            request.user.is_active = False
            request.user.save()

        for _backend in settings.AUTHENTICATION_BACKENDS:
            django_login(request, target, backend=_backend)
        serializer = self.serializer_class(
            instance=target,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=False, methods=('POST', ), url_path='profile-image',
            permission_classes=(permissions.IsAuthenticated, ))
    def profile_image(self, request, **kwargs):
        content = request.data.get('content')
        filename = request.data.get('filename')
        image = get_base64_image(content)
        if not content or not filename or not image:
            raise drf_exc.ValidationError({
                'code': 'image-not-found',
                'detail': _('이미지를 업로드 하세요.'),
            })

        try:
            request.user.image = SimpleUploadedFile(filename, image)
            request.user.save()
        except Exception:
            raise drf_exc.ValidationError({
                'code': 'invalid-image',
                'detail': _('잘못된 이미지 형식입니다.'),
            })

        serializer = self.serializer_class(
            instance=request.user,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=False, methods=('POST', ),
            url_path='check-daily-attendance',
            permission_classes=(permissions.IsAuthenticated, ))
    def check_daily_attendance(self, request, **kwargs):
        from currencies import models as c_models
        behaviour = get_object_or_404(c_models.Behaviour, code='login')
        try:
            behaviour.issue_point_to_user(request.user)
        except ValueError as e:
            raise drf_exc.ValidationError(e.args[0], code='daily-login')
        return Response({})

    @action(detail=False,
            permission_classes=(
                    permissions.IsAuthenticated,
            ),
            url_path='notification-tokens',
            methods=('POST', ))
    def notification_tokens(self, request):
        from messaging.models import NotificationToken
        from messaging.api.serializers import NotificationTokenSerializer

        serializer = NotificationTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qs = NotificationToken.objects.filter(
            device=serializer.data['device'],
            token=serializer.data['token'],
        )
        qs2 = qs.exclude(user=request.user)

        if qs2.exists():
            qs2.delete()

        o = qs.filter(user=request.user).first()
        if not o:
            o = NotificationToken.objects.create(
                user=request.user,
                device=serializer.data['device'],
                token=serializer.data['token'],
            )
            is_created = True
        else:
            is_created = False
        status = 200 + is_created

        return Response(
            NotificationTokenSerializer(instance=o).data,
            status=status,
        )

    @action(detail=False,
            permission_classes=(
                    permissions.IsAuthenticated,
            ),
            url_path='notification-settings',
            methods=('PATCH', ))
    def notification_settings(self, request):
        _default = models.default_notification_settings()
        if frozenset(request.data.keys()) - frozenset(_default.keys()):
            raise drf_exc.ValidationError(_('유효하지 않은 설정값입니다.'))

        user = request.user
        for k, v in request.data.items():
            if not isinstance(v, bool):
                continue
            user.notification_settings[k] = v
        user.save()
        serializer = self.serializer_class(
            instance=user,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=False,
            permission_classes=(
                    permissions.IsAuthenticated,
            ),
            url_path='bezant-wallet',
            methods=('POST', ))
    def create_bezant_wallet(self, request):
        user = request.user
        if not request.data.get('password'):
            raise drf_exc.ValidationError(_('지갑 암호가 필요합니다.'))
        user.create_bezant_wallet(request.data['password'])
        serializer = self.serializer_class(
            instance=user,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)


class ProfileViewSet(UserViewSet):
    serializer_class = serializers.ProfilePageSerializer
    lookup_field = 'username'
    lookup_value_regex = r'[a-zA-Z\-\@_0-9.]+'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=('POST', ))
    def follow(self, request, username):
        target = self.get_object()
        qs = models.Follower.objects.filter(user=request.user, target=target)

        if qs.exists():
            result = models.Follower.unfollow(request.user, target)
            if result:
                return Response(status=http_status.HTTP_204_NO_CONTENT)
            raise drf_exc.NotFound

        o = models.Follower.follow(request.user, target, 'auto_approved')
        serializer = serializers.FollowerSerializer(
            instance=o,
            context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        serializer.instance.notify()
        return Response(serializer.data,
                        status=http_status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=True, methods=('GET', ),
            pagination_class=DefaultCursorPaginationClass,)
    def posts(self, request, username):
        from contents.api import serializers as c_serializers

        target = self.get_object()
        qs = target.post_set.filter(status='published')
        paginated = self.paginate_queryset(qs)
        serializer = c_serializers.SimplePostSerializer(
            paginated, many=True,
            context=self.get_serializer_context()
        )
        response = self.get_paginated_response(serializer.data)
        response['LineUp-Total-Number'] = qs.count()
        return response

    @action(detail=True, methods=('GET', ))
    def collections(self, request, **kwargs):
        from contents.api import serializers as c_serializers

        target = self.get_object()
        qs = target.collection_set.all()
        serializer = c_serializers.CollectionSerializer(
            qs,
            many=True,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)


class ObtainAuthToken(drf_views.ObtainAuthToken):
    serializer_class = serializers.AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response


obtain_auth_token = ObtainAuthToken.as_view()

