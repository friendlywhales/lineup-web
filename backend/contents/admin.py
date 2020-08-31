from django.contrib import admin
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.urls import reverse

from . import models


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('uid', 'user', 'name', 'created_at', 'updated_at', )


def make_hidden_status(modeladmin, request, queryset):
    queryset.update(status='marked_hidden')

make_hidden_status.short_description = _('숨김 상태로 변경')


def make_published_status(modeladmin, request, queryset):
    queryset.update(status='published')

make_published_status.short_description = _('발행 상태로 변경')


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('uid', 'user', 'status', 'report_count', 'created_at', 'updated_at', )
    list_filter = ('status', )
    actions = [make_hidden_status, make_published_status]

    def report_count(self, obj: models.Post):
        count = obj.reportpost_set.count()
        pk = obj.pk
        url = reverse('admin:contents_reportpost_changelist')
        if not count:
            return f'{count}'
        return mark_safe(f'<a href="{url}?post__id__exact={pk}">{count}</a>')
    report_count.short_description = _('신고 수')


@admin.register(models.Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('uid', 'kind', 'post', 'created_at', 'updated_at', )
    list_filter = ('kind', )


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', )


@admin.register(models.PostCollection)
class PostCollectionAdmin(admin.ModelAdmin):
    list_display = ('uid', 'collection', 'post', )


@admin.register(models.Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at', 'updated_at', )


def make_hidden_post_status(modeladmin, request, queryset):
    models.Post.objects \
        .filter(pk__in=queryset.values_list('post__pk')) \
        .update(status='marked_hidden')

make_hidden_post_status.short_description = _('선택한 신고 대상 게시물을 숨김 상태로 변경')


@admin.register(models.ReportPost)
class ReportPostAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'post', 'post_status', 'kind', 'created_at', 'updated_at',
    )
    list_filter = ('post', )
    actions = [make_hidden_post_status]

    def post_status(self, obj: models.ReportPost):
        return obj.post.get_status_display()
    post_status.short_description = _('발행 상태')
