
import os
import mimetypes
from io import BytesIO
from uuid import uuid4

from PIL import Image
from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile, File
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse, reverse_lazy
from rest_framework import exceptions as drf_exc
from django.utils import timezone

from apiserver.helpers.models import DateTimeModel
from apiserver.helpers.models import PreventDeleteModel
from apiserver.helpers.models import PreventDeleteActiveManager


def _short_uuid():
    return uuid4().hex[:8]


class Collection(DateTimeModel):
    uid = models.CharField(max_length=8,
                           default=_short_uuid, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(_('이름'), max_length=80)
    posts = models.ManyToManyField(
        'Post',
        through='PostCollection',
        through_fields=('collection', 'post', ),
    )

    def __str__(self):
        return self.uid

    def get_absolute_url(self):
        return reverse('contents-api:collection-detail',
                       kwargs={'uid': self.uid})


class Post(DateTimeModel, PreventDeleteModel):
    statuses = (
        ('drafted', _('임시저장'), ),
        ('published', _('발행'), ),
        ('marked_hidden', _('숨김처리'), ),
        ('deleted', _('삭제대기'), ),
    )
    uid = models.UUIDField(default=uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', verbose_name=_('해시태그'), blank=True)
    fixed_at = models.DateTimeField(_('고정일시'), null=True, blank=True)
    status = models.CharField(_('상태'), max_length=40,
                              default='draft',
                              choices=statuses)
    content = models.TextField(_('본문'), max_length=1000, blank=True)
    notifications = GenericRelation('messaging.Notification')

    objects = PreventDeleteActiveManager()
    full_objects = models.Manager()

    class Meta:
        ordering = ('-pk', '-created_at', )

    def __str__(self):
        return self.uid.hex

    def get_absolute_url(self):
        return reverse('contents-api:post-detail', kwargs={'uid': self.uid})

    @property
    def is_available_for_like(self):
        return self.status == 'published'

    @property
    def is_available_for_comment(self):
        return self.status == 'published'

    @property
    def is_available_for_report(self):
        return self.status == 'published'

    @property
    def is_available_for_deletion(self):
        day = timezone.now() - self.created_at
        return day.days < settings.AVAILABLE_DELETION_PERIOD

    def publish(self):
        from currencies import tasks

        if self.status == 'published':
            raise drf_exc.ValidationError(
                detail=_('이미 발행된 게시물입니다.')
            )
        if not self.attachment_set.exists():
            raise drf_exc.ValidationError(
                detail=_('첨부 파일이 없어서 발행할 수 없습니다.'),
                code='required-attachment'
            )
        self.status = 'published'
        self.save()
        tasks.issue_posting_point(self)

    def notify(self):
        from messaging.models import Notification
        Notification.notify_following_new_post(self)

    def check_available_adding_like(self, user):
        if not self.is_available_for_like:
            raise drf_exc.NotFound
        if not user.has_perm('contents.add_like'):
            raise drf_exc.PermissionDenied

    def check_available_posting_comment(self, user):
        if not self.is_available_for_comment:
            raise drf_exc.NotFound
        if not user.has_perm('contents.add_comment'):
            raise drf_exc.PermissionDenied

    def get_thumbnails(self, request=None):
        qs = self.attachment_set \
            .filter(kind__startswith='thumbnail_').order_by('order')
        return (
            {
                'url': request.build_absolute_uri(o.url) if request else o.url,
                'width': o.width,
                'height': o.height,
            } for o in qs
        )

    @property
    def escaped_content(self):
        return (self.content or '').replace('&', '&amp;') \
            .replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


class PostCollection(DateTimeModel):
    uid = models.UUIDField(default=uuid4, unique=True, editable=False)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE)

    class Meta:
        ordering = ('pk', )
        unique_together = ('collection', 'post', )

    @classmethod
    def add_post_to_collection(cls, collection, post):
        return cls.objects.get_or_create(collection=collection, post=post)[0]


def _upload_to(instance, filename):
    uid = instance.post.uid.hex
    _, ext = os.path.splitext(filename)
    filename = f'{uid[4:]}{ext}'
    return os.path.join('p', uid[0], uid[1], uid[2], uid[3], filename)


def _attachment_uid():
    return uuid4().hex[:20]


class Attachment(DateTimeModel):
    uid = models.UUIDField(default=uuid4, unique=True, editable=False)
    kinds = (
        ('original', _('원본'), ),
        ('thumbnail_640w', _('미리보기 640'), ),
        ('thumbnail_750w', _('미리보기 750'), ),
        ('thumbnail_1080w', _('미리보기 1080'), ),
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.ImageField(_('첨부파일'), upload_to=_upload_to)
    order = models.PositiveSmallIntegerField(default=1)
    kind = models.CharField(_('유형'), max_length=40, choices=kinds, default='original')

    thumbnail_sizes = (
        (640, 640, ),
        (750, 750, ),
        (1080, 1080, ),
    )
    thumbnail_sizes_per_kinds = {
        'thumbnail_640w': (640, 640, ),
        'thumbnail_750w': (750, 750, ),
        'thumbnail_1080w': (1080, 1080, ),
    }

    class Meta:
        ordering = ('post', 'order', )

    def __str__(self):
        return self.uid.hex

    @property
    def url(self):
        return reverse('contents:asset-redirect', kwargs={'uid': self.uid.hex})

    @property
    def width(self):
        dimension = self.thumbnail_sizes_per_kinds.get(self.kind)
        if not dimension:
            return self.content.width
        return dimension[0]

    @property
    def height(self):
        dimension = self.thumbnail_sizes_per_kinds.get(self.kind)
        if not dimension:
            return self.content.height
        return dimension[1]

    @classmethod
    def make_thumbnails(cls, post: Post, file_content: UploadedFile):
        for i, size in enumerate(cls.thumbnail_sizes):
            obj = cls.make_thumbnail_with_uploaded(post, file_content, size, i)
            if not obj:
                continue
            obj.kind = f'thumbnail_{size[0]}w'
            obj.save()
            yield obj

    @classmethod
    def make_thumbnail_with_uploaded(cls, post: Post,
                                     file_content: UploadedFile,
                                     size: tuple,
                                     order: int = 1):
        _, ext = os.path.splitext(file_content.name)
        mimetype = file_content.content_type
        filename = f'{uuid4().hex}{ext}'

        if not mimetype:
            raise drf_exc.ValidationError(
                'invalid uploaded file format',
                'invalid-file-format'
            )

        im = Image.open(file_content)

        base_size = min(im.size)
        min_size = settings.MINIMUM_IMAGE_SIZE
        if base_size < min_size:
            raise drf_exc.ValidationError(
                f'image size requires to be bigger than {min_size}',
                'minimum-image-size'
            )
        if base_size < size[0]:
            return

        file_content.seek(0)

        fp = BytesIO()
        resized = im.crop((0, 0, base_size, base_size))
        resized.thumbnail(size, Image.ANTIALIAS)
        resized.save(fp, format=mimetype.split('/')[-1].upper())

        uploaded = InMemoryUploadedFile(fp, None, filename, mimetype, fp.tell, None)
        thumb = cls(post=post, content=uploaded, order=order)
        thumb.save()
        return thumb


class Tag(DateTimeModel):
    name = models.CharField(_('이름'), max_length=80, unique=True)

    def __str__(self):
        return self.name


class Like(DateTimeModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'post', )

    def notify(self):
        from messaging.models import Notification
        Notification.notify_likes_user_liked(self)
        Notification.notify_liked_my_post(self)

    def issue_point(self):
        from currencies import tasks
        tasks.issue_like_point(self.user, self.post)

    def unissue_point(self):
        from currencies import tasks
        tasks.issue_unlike_point(self.user, self.post)


class Comment(DateTimeModel):
    uid = models.UUIDField(default=uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    reply = models.ForeignKey('self',
                              related_name='replies',
                              null=True, blank=True,
                              on_delete=models.CASCADE,
                              verbose_name=_('댓글 대상 글'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField(_('본문'), max_length=1000)

    class Meta:
        ordering = ('updated_at', )

    def notify(self):
        from messaging.models import Notification
        Notification.notify_new_comment_user_commented(self)

    def issue_point(self):
        from currencies import tasks
        tasks.issue_comment_point(self.user, self.post)


class ReportPost(DateTimeModel):
    _kinds = (
        ('spam', _('스팸'), ),
        ('inappropriate', _('부적절'), ),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    kind = models.CharField(_('유형'), max_length=40, choices=_kinds)
    content = models.TextField(_('본문'), max_length=1000, blank=True, null=True)
