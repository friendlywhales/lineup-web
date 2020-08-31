from django.contrib import admin

from . import models


@admin.register(models.PromotionCode)
class PromotionCode(admin.ModelAdmin):
    pass
