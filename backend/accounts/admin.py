from django.contrib import admin

from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    search_fields = (
        'username', 'nickname', 'email',
    )


@admin.register(models.Follower)
class FollowerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserPromotionCode)
class UserPromotionCode(admin.ModelAdmin):
    list_display = ('code', 'user', 'created_at', )
