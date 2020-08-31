
from django.db import models
from django.conf import settings
from django_mysql import models as dm_models
from django.utils import timezone

from apiserver.helpers.exceptions import FrozenPostError


class DateTimeModel(dm_models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PreventDeleteQuerySet(dm_models.QuerySet):
    def delete(self):
        _days = (timezone.now() - self.created_at).days
        if _days > settings.AVAILABLE_DELETION_PERIOD:
            raise FrozenPostError
        self.update(status='deleted')


class PreventDeleteActiveManager(models.Manager):
    def get_queryset(self):
        return PreventDeleteQuerySet(self.model, using=self._db) \
            .exclude(status='deleted')


class PreventDeleteModel(dm_models.Model):
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        if self.status == 'deleted':
            super().delete(*args, **kwargs)
        else:
            self.status = 'deleted'
            self.save()
