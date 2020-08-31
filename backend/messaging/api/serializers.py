
import re

from rest_framework import serializers

from .. import models


class NotificationSerializer(serializers.ModelSerializer):
    trigger = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    content = serializers.SerializerMethodField()
    thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = models.Notification
        fields = (
            'uid', 'trigger', 'kind', 'extra', 'content',
            'thumbnails', 'created_at',
        )
        extra_kwargs = {
            'uid': {
                'read_only': True,
            },
            'kind': {
                'read_only': True,
            },
            'extra': {
                'read_only': True,
            },
            'trigger': {
                'read_only': True,
            },
            'content_object': {
                'read_only': True,
            },
            'created_at': {
                'read_only': True,
            },
        }

    def get_content(self, obj):
        from contents import models as c_models
        from contents.api import serializers as c_serializers

        content = obj.content_object
        if isinstance(content, c_models.Post):
            return c_serializers.SimplePostSerializer(instance=content,
                                                      context=self.context).data
        elif isinstance(content, c_models.Comment):
            return c_serializers.CommentSerializer(instance=content).data
        elif isinstance(content, c_models.Like):
            return c_serializers.LikeSerializer(instance=content).data

    def get_thumbnails(self, obj):
        from contents import models as c_models

        content = obj.content_object
        if isinstance(content, c_models.Post):
            post = content
        elif isinstance(content, c_models.Comment):
            post = content.post
        elif isinstance(content, c_models.Like):
            post = content.post
        else:
            return
        return post.get_thumbnails(request=self.context['request'])


class NotificationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NotificationToken
        fields = ('user', 'device', 'token', )
        extra_kwargs = {
            'user': {
                'read_only': True,
            },
        }
