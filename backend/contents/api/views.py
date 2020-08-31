
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext as _
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status as http_status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import exceptions as drf_exc
from rest_framework.generics import get_object_or_404

from apiserver.helpers.rest_framework import permissions as g_permissions
from apiserver.helpers.rest_framework import paginations
from . import serializers
from . import permissions as c_permissions
from .. import models


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CollectionSerializer
    queryset = models.Collection.objects.all()
    permission_classes = (
        g_permissions.IsOwnerOrReadOnly,
        c_permissions.IsAllowedUserLevel,
        permissions.DjangoModelPermissionsOrAnonReadOnly,
    )
    lookup_field = 'uid'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=('GET', 'POST', ),
            pagination_class=paginations.DefaultCursorPaginationClass,)
    def posts(self, request, uid):
        c = self.get_object()

        if request.method == 'POST':
            post_collection = self._add_post_to_collection(request, c)

        qs = c.posts.filter(status='published').order_by('-updated_at')
        paginated = self.paginate_queryset(qs)
        serializer = serializers.SimplePostSerializer(
            paginated,
            many=True,
            context={'request': request}
        )
        response = self.get_paginated_response(serializer.data)
        response['LineUp-Total-Number'] = qs.count()
        return response

    def _add_post_to_collection(self, request, collection):
        try:
            post_uid = request.data['post']
            post = models.Post.objects.get(uid=post_uid)
        except KeyError:
            raise drf_exc.ValidationError(
                code='required-post-uid',
            )
        except models.Post.DoesNotExist:
            raise drf_exc.NotFound
        return models.PostCollection.add_post_to_collection(collection, post)

    @action(detail=True, methods=('POST', ), url_path='detach-post',
            pagination_class=paginations.DefaultCursorPaginationClass,)
    def detail_post(self, request, uid):
        c = self.get_object()
        try:
            post_uid = request.data['post']
            post_collection = models.PostCollection.objects.get(
                collection=c,
                collection__user=request.user,
                post__uid=post_uid,
            )
        except KeyError:
            raise drf_exc.ValidationError(
                code='required-post-uid',
            )
        except models.PostCollection.DoesNotExist:
            raise drf_exc.NotFound

        post_collection.delete()
        qs = c.posts.filter(status='published').order_by('-updated_at')
        paginated = self.paginate_queryset(qs)
        serializer = serializers.SimplePostSerializer(
            paginated,
            many=True,
            context={'request': request}
        )
        response = self.get_paginated_response(serializer.data)
        response['LineUp-Total-Number'] = qs.count()
        return response


_post_owner_permission_classes = (
    g_permissions.IsOwnerOrReadOnly,
    c_permissions.IsAllowedUserLevel,
    permissions.DjangoModelPermissionsOrAnonReadOnly,
)
_post_others_permission_classes = (
    c_permissions.IsAllowedUserLevel,
    permissions.DjangoModelPermissionsOrAnonReadOnly,
)
_post_except_associate_level_permission_classes = (
    c_permissions.IsAllowedUserLevel,
)


class PostViewSet(viewsets.ModelViewSet):
    pagination_class = paginations.DefaultCursorPaginationClass
    serializer_class = serializers.PostSerializer
    permission_classes = _post_others_permission_classes
    lookup_field = 'uid'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        qs = models.Post.objects.all()
        if not self.request.user.is_authenticated:
            qs = qs.filter(status='published')
        else:
            q = Q(status='draft') & Q(user=self.request.user)
            q |= Q(status='published')
            qs = qs.filter(q)
        return qs

    def list(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        self._check_deletion_period()
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        self._check_deletion_period()
        return super().destroy(request, *args, **kwargs)

    def _check_deletion_period(self):
        obj = self.get_object()
        if not obj.is_available_for_deletion:
            day = settings.AVAILABLE_DELETION_PERIOD
            raise drf_exc.ValidationError({
                'detail': _(f'{day}일 이상 된 게시물은 수정과 삭제가 불가능합니다.')
            })

    @action(
        detail=False,
        methods=('GET', ),
        url_path='search-all',
        serializer_class=serializers.SearchPostSerializer,
        pagination_class=paginations.SearchCursorPaginationClass,
    )
    def search_all(self, request):
        qs = models.Post.objects.filter(status='published')
        paginated = self.paginate_queryset(qs)
        serializer = self.get_serializer(
            paginated,
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False,
            methods=('GET', ),
            permission_classes=(permissions.IsAuthenticated, ))
    def timeline(self, request):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        qs = self.get_queryset() \
            .filter(status='published') \
            .select_related('user') \
            .prefetch_related('tags')

        if request.user.is_authenticated and \
                request.user.following_set.count() > 0:
            followings = request.user.following_set \
                .values_list('target') \
                .filter(user__is_active=True) \
                .exclude(status='requested')
            qs = qs.filter(user__in=tuple(followings))
        paginated = self.paginate_queryset(qs)
        serializer = self.get_serializer(
            paginated,
            many=True,
            context=self.get_serializer_context()
        )
        response = self.get_paginated_response(serializer.data)
        response['LineUp-Total-Number'] = qs.count()
        return response

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=('POST', ),
            permission_classes=_post_owner_permission_classes)
    def publish(self, request, uid):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        post = self.get_object()
        post.publish()
        post.notify()
        serializer = self.get_serializer(
            instance=post,
            context=self.get_serializer_context()
        )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=http_status.HTTP_200_OK,
                        headers=headers)

    @action(detail=True, methods=('POST', 'HEAD', 'OPTION', ),
            permission_classes=_post_owner_permission_classes)
    def attachments(self, request, uid):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        post = get_object_or_404(
            models.Post.objects.filter(user=request.user),
            uid=uid,
        )

        for i, _content in enumerate(request.data.getlist('content')):
            _data = {
                'order': request.data.getlist('order')[i],
                'content': _content,
            }
            serializer = serializers.AttachmentSerializer(
                data=_data,
                context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(post=post)

        serializer = serializers.AttachmentSerializer(
            post.attachment_set.all(),
            many=True,
            context=self.get_serializer_context(),
        )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=http_status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=True, methods=('POST', ),
            permission_classes=_post_except_associate_level_permission_classes,)
    def likes(self, request, uid):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        from currencies import tasks

        post = self.get_object()
        post.check_available_adding_like(request.user)

        qs = post.like_set.filter(user=request.user)
        if qs.exists():
            like: models.Like = qs.first()
            like.unissue_point()
            like.delete()
            _status = http_status.HTTP_204_NO_CONTENT
            content = None
        else:
            serializer = serializers.LikeSerializer(
                data=request.data,
                context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(post=post, user=request.user)
            _status = http_status.HTTP_201_CREATED
            serializer.instance.notify()
            serializer.instance.issue_point()
            content = serializer.data
            tasks.issue_like_point(request.user, post)

        return Response(content, status=_status)

    @action(detail=True, methods=('POST', ),
            permission_classes=_post_except_associate_level_permission_classes)
    def comments(self, request, uid):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        post = self.get_object()
        post.check_available_posting_comment(request.user)

        serializer = serializers.CommentSerializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, user=request.user)
        serializer.instance.issue_point()
        serializer.instance.notify()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=http_status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=True, methods=('GET', ),
            url_path='has-collected',
            permission_classes=(permissions.IsAuthenticated, ))
    def hasCollected(self, request, uid):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        post = self.get_object()
        qs = models.PostCollection.objects \
            .filter(post=post, collection__user=request.user) \
            .values_list('collection__pk')
        if not qs.exists():
            return Response(status=http_status.HTTP_204_NO_CONTENT)
        collections = models.Collection.objects.filter(pk__in=tuple(qs))
        serializer = serializers.CollectionSerializer(
            collections,
            many=True,
            context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=True, methods=('POST', ),
            serializer_class=serializers.ReportPostSerializer,
            permission_classes=(permissions.IsAuthenticated, ))
    def report(self, request, uid):
        if not self.request.user.is_authenticated:
            raise drf_exc.AuthenticationFailed
        post = self.get_object()
        if not post.is_available_for_report:
            raise drf_exc.NotFound
        qs = models.ReportPost.objects.filter(post=post, user=request.user)
        if qs.exists():
            serializer = self.get_serializer(
                instance=qs.first(),
                data=request.data,
                context=self.get_serializer_context()
            )
        else:
            serializer = self.get_serializer(
                data=request.data,
                context=self.get_serializer_context()
            )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user, post=post)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=http_status.HTTP_200_OK,
                        headers=headers)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()
    permission_classes = (
    )
    lookup_field = 'name'
    http_method_names = ('get', 'head', 'option', )

    def list(self, *args, **kwargs):
        return Response([])

    def retrieve(self, request, *args, **kwargs):
        term = kwargs.get(self.lookup_field, '').strip()
        terms = serializers.PATTERN_HASH_TAG_WITHOUT_HASH.findall(term) or []
        for _t in terms:
            if _t.strip():
                term = _t
                break
        else:
            raise drf_exc.NotFound
        qs = self.get_queryset() \
            .filter(name__icontains=term)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=('GET', ),
            pagination_class=paginations.DefaultCursorPaginationClass,)
    def posts(self, request, name):
        qs = self.get_object().post_set.filter(status='published')
        username = request.GET.get('username')
        if username:
            qs = qs.filter(user__username=username)
        paginated = self.paginate_queryset(qs)
        serializer = serializers.SimplePostSerializer(
            paginated,
            many=True,
            context={'request': request}
        )
        response = self.get_paginated_response(serializer.data)
        response['LineUp-Total-Number'] = qs.count()
        return response


class PostCollectionViewSet(viewsets.ModelViewSet):
    http_method_names = ('delete', 'head', 'option', )
    permission_classes = _post_owner_permission_classes
    serializer_class = serializers.PostCollectionSerializer
    lookup_field = 'uid'

    def get_queryset(self):
        qs = models.PostCollection.objects.all()
        if not self.request.user.is_authenticated:
            return qs.none()
        return qs

