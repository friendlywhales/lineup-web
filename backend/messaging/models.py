
from uuid import uuid4

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_mysql.models import Model
from django_mysql.models.fields import JSONField


class Channel(Model):
    uid = models.UUIDField(unique=True, default=uuid4, editable=False)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)


class DirectMessage(Model):
    kinds = (
        ('system', _('시스템 메시지')),
        ('user', _('이용자 메시지')),
    )
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='sent_messages',
                               on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 related_name='received_messages',
                                 on_delete=models.CASCADE)
    kind = models.CharField(_('종류'), max_length=40, choices=kinds)
    transaction = models.ForeignKey('currencies.Transaction',
                                    on_delete=models.CASCADE)
    content = models.TextField()
    attachment = models.FileField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(Model):
    uid = models.UUIDField(unique=True, default=uuid4, editable=False)
    kinds = (
        ('following_new_post', _('팔로잉하는 작가의 새 게시물')),
        ('new_vote_user_voted', _('내가 보팅한 글에 타인의 새 보팅')),
        ('new_comment_user_commented', _('내가 댓글단 글에 타인의 새 댓글')),
        ('new_comment_user_posted', _('내가 쓴 글에 타인의 새 댓글')),
        ('liked_my_post', _('내 포스트에 좋아요를 받았을 때')),
        ('my_new_follower', _('누군가 나를 팔로잉 했을 때')),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='notifications',
                             on_delete=models.CASCADE)
    trigger = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='triggered_notifications',
                                on_delete=models.CASCADE)
    kind = models.CharField(_('종류'), max_length=40, choices=kinds)
    extra = JSONField(default=dict)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', )

    @classmethod
    def notify_following_new_post(cls, post):
        from . import tasks

        user_lookups = Q(user__is_active=True)
        user_lookups &= Q(target__is_active=True)
        followers = post.user.follower_set.select_related('user').filter(user_lookups)
        cls.objects.bulk_create([
            cls(
                user=f.user,
                trigger=post.user,
                kind='following_new_post',
                content_object=post,
            ) for f in followers
        ])

        user = post.user
        objs = [None for __ in range(followers.count())]
        tokens = []
        for i, f in enumerate(followers):
            objs[i] = cls(
                user=f.user,
                trigger=post.user,
                kind='following_new_post',
                content_object=post,
            )

            if f.user.notification_settings.get('following_new_post', False):
                tokens.extend(f.user.notification_tokens)

        cls.objects.bulk_create(objs)
        tasks.push_notification.delay(
            tuple(frozenset(tokens)),
            _(f'{user.display_name}님이 새 포스팅을 게시했습니다.'),
        )

    @classmethod
    def notify_new_comment_user_commented(cls, comment):
        from accounts.models import User
        target_pks = comment.post.comment_set.values_list('user__pk')

        user_lookups = Q(is_active=True)
        user_lookups &= Q(pk__in=target_pks)
        qs = User.objects.filter(user_lookups).exclude(pk=comment.user.pk)

        cls.objects.bulk_create([
            cls(
                user=u,
                trigger=comment.user,
                kind='new_comment_user_commented',
                content_object=comment,
            ) for u in qs
        ])
        cls.notify_new_comment_user_posted(comment)

    @classmethod
    def notify_new_comment_user_posted(cls, comment):
        from . import tasks

        if comment.user == comment.post.user:
            return
        user = comment.post.user
        cls.objects.create(
            user=user,
            trigger=comment.user,
            kind='new_comment_user_posted',
            content_object=comment,
        )

        if user.notification_settings.get('new_comment_user_posted', False):
            tasks.push_notification.delay(
                user.notification_tokens,
                _(f'{comment.user.display_name}님이 댓글을 남겼습니다.'),
            )

    @classmethod
    def notify_likes_user_liked(cls, like):
        from accounts.models import User
        target_pks = like.post.like_set.values_list('user__pk')

        user_lookups = Q(is_active=True)
        user_lookups &= Q(pk__in=target_pks)
        qs = User.objects.filter(user_lookups).exclude(pk=like.user.pk)

        cls.objects.bulk_create([
            cls(
                user=u,
                trigger=like.user,
                kind='new_vote_user_voted',
                content_object=like,
            ) for u in qs
        ])

    @classmethod
    def notify_liked_my_post(cls, like):
        from . import tasks

        user = like.post.user
        obj = cls(
            user=user,
            trigger=like.user,
            kind='liked_my_post',
            content_object=like,
        )
        obj.save()

        if user.notification_settings.get('liked_my_post', False):
            tasks.push_notification.delay(
                user.notification_tokens,
                _(f'{like.user.display_name}님이 회원님의 포스팅을 좋아합니다.'),
            )

    @classmethod
    def notify_my_new_follower(cls, follower):
        from . import tasks

        user = follower.target
        obj = cls(
            user=user,
            trigger=follower.user,
            kind='my_new_follower',
            content_object=follower,
        )
        obj.save()

        if user.notification_settings.get('my_new_follower', False):
            tasks.push_notification.delay(
                user.notification_tokens,
                _(f'{follower.user.display_name}님이 회원님을 팔로우 했습니다.'),
            )


class NotificationToken(Model):
    devices = (
        ('android', 'Android', ),
        ('ios', 'iOS', ),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    device = models.CharField(_('기기'), max_length=20, choices=devices)
    token = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'device', 'token', )
