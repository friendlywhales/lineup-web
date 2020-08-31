from django.contrib import admin

from . import models


@admin.register(models.Behaviour)
class UserAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'reward', 'created_at', 'updated_at', )
    list_display_links = ('code', 'description', 'reward', )

