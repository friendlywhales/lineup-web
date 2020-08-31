
import re

from django.utils import html as django_html
from rest_framework import serializers

from .. import models

_raw_hashtag = r'[^\u2000-\u206F\u2E00-\u2E7F\s\'!"#$%&()*+,.\/:;<=>?@\[\]^_`{|}~]*'
PATTERN_HASH_TAG = re.compile(rf"(?:^|\s)[＃#]{{1}}({_raw_hashtag})", re.UNICODE)
PATTERN_HASH_TAG_WITHOUT_HASH = re.compile(rf"(?:^|\s)({_raw_hashtag})", re.UNICODE)


class CollectionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    title_images = serializers.SerializerMethodField()

    class Meta:
        model = models.Collection
        fields = ('uid', 'user', 'name', 'title_images', )
        extra_kwargs = {
            'uid': {
                'read_only': True,
            },
        }

    def get_title_images(self, obj):
        post = obj.posts.filter(status='published').first()
        if not post:
            return []
        return (
            self.context['request'].build_absolute_uri(o.url)
            for o in post.attachment_set.filter(kind__startswith='thumbnail_')
        )


class TagSerializer(serializers.ModelSerializer):
    post_number = serializers.SerializerMethodField()

    class Meta:
        model = models.Tag
        fields = ('name', 'post_number', )

    def get_post_number(self, obj):
        return obj.post_set.count()


class AttachmentSerializer(serializers.ModelSerializer):
    post = serializers.SlugRelatedField(
        read_only=True,
        slug_field='uid'
    )

    class Meta:
        model = models.Attachment
        fields = ('post', 'content', 'order', 'kind', )
        extra_kwargs = {
            'post': {
                'read_only': True,
            },
        }

    def create(self, validated_data):
        obj = super().create(validated_data)
        try:
            tuple(models.Attachment.make_thumbnails(
                obj.post, validated_data['content']
            ))
        except Exception:
            obj.content.delete(save=False)
            obj.delete()
            raise
        return obj


class LikeSerializer(serializers.ModelSerializer):
    post = serializers.SlugRelatedField(
        read_only=True,
        slug_field='uid'
    )

    class Meta:
        model = models.Like
        fields = ('post', 'user', )
        extra_kwargs = {
            'post': {
                'read_only': True,
            },
            'user': {
                'read_only': True,
            },
        }


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.SlugRelatedField(
        read_only=True,
        slug_field='uid'
    )
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        fields = (
            'uid', 'post', 'user', 'reply', 'content', 'created_at',
            'nickname',
        )
        extra_kwargs = {
            'uid': {
                'read_only': True,
            },
            'post': {
                'read_only': True,
            },
            'user': {
                'read_only': True,
            },
            'reply': {
                'read_only': True,
            },
            'created_at': {
                'read_only': True,
            },
        }

    def get_nickname(self, obj):
        return obj.user.nickname


class BasePostSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    user_image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    thumbnails = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    orig_content = serializers.SerializerMethodField()
    restrict_code = serializers.SerializerMethodField()

    def get_user_image(self, obj):
        if obj.user.image_url:
            return self.context['request'].build_absolute_uri(obj.user.image_url)
        else:
            return

    def get_images(self, obj):
        qs = obj.attachment_set.filter(kind='original').order_by('order')
        return (
            self.context['request'].build_absolute_uri(o.url)
            for o in qs
        )

    def get_thumbnails(self, obj: models.Post):
        images = obj.get_thumbnails(request=self.context['request'])
        return images if images else self.get_images(obj)

    def get_likes(self, obj):
        qs = obj.like_set.select_related('user') \
            .filter() \
            .order_by('-updated_at')
        return (
            o.user.username
            for o in qs
        )

    def get_orig_content(self, obj):
        return obj.escaped_content

    def get_restrict_code(self, obj):
        if not obj.is_available_for_deletion:
            return 'over-period'
        return None

    def to_representation(self, obj):
        result = super().to_representation(obj)
        result['content'] = django_html.linebreaks(obj.escaped_content)
        return result


class PostSerializer(BasePostSerializer):
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = models.Post
        fields = (
            'uid', 'user', 'nickname', 'content', 'tags', 'updated_at',
            'images', 'thumbnails', 'likes', 'comments', 'user_image',
            'orig_content', 'restrict_code',
        )
        extra_kwargs = {
        }

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        self.process_tags_from_content()
        return instance

    def process_tags_from_content(self):
        taglist = PATTERN_HASH_TAG.findall(self.instance.content)
        tags = [models.Tag.objects.get_or_create(name=t)[0] for t in taglist]
        self.instance.tags.clear()
        self.instance.tags.set(tags)
        self.add_default_tags()

    def add_default_tags(self):
        defaults = ('line-up', )
        tags = [models.Tag.objects.get_or_create(name=t)[0] for t in defaults]
        self.instance.tags.add(*tags)

    def get_comments(self, obj):
        return (
            {
                'user': o.user.username,
                'content': o.content,
                'reply': o.reply.user if o.reply else None,
                'created_at': o.created_at.isoformat(),
            }
            for o in obj.comment_set.select_related('user', 'reply').all()
        )

    def get_nickname(self, obj):
        return obj.user.nickname


class SimplePostSerializer(BasePostSerializer):
    tags = TagSerializer(many=True, read_only=True)
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = models.Post
        fields = (
            'uid', 'user', 'nickname', 'images', 'thumbnails',
            'updated_at', 'likes', 'tags',
            'user_image', 'restrict_code',
        )

    def get_tags(self, obj):
        return []

    def get_nickname(self, obj):
        return obj.user.nickname


class PostCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostCollection
        fields = ('uid', 'collection', 'post', )
        extra_kwargs = {
            'uid': {'read_only': True, },
            'collection': {'read_only': True, },
            'post': {'read_only': True, },
        }


class ReportPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReportPost
        fields = ('user', 'post', 'kind', 'content', )
        extra_kwargs = {
            'user': {'read_only': True, },
            'post': {'read_only': True, },
        }


class SearchPostSerializer(BasePostSerializer):

    class Meta:
        model = models.Post
        fields = (
            'uid', 'content', 'updated_at',
            'thumbnails',
        )

