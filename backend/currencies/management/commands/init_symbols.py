
from django.utils.translation import ugettext as _
from django.core.management.base import BaseCommand
from django.conf import settings

from ... import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        items = (
            {
                'code': settings.SERVICE_TOKEN_SYMBOL,
                'name': _('라인업 코인'),
                'kind': 'token',
            },
            {
                'code': 'steem',
                'name': _('스팀'),
                'kind': 'coin',
            },
            {
                'code': 'sbd',
                'name': _('스팀 달러'),
                'kind': 'coin',
            },
            {
                'code': 'bznt',
                'name': _('베잔트'),
                'kind': 'coin',
            },
        )
        for item in items:
            o, is_created = models.Symbol.objects.get_or_create(
                code=item['code'], defaults=item
            )
            self.stdout.write(f'{o.code} is set')
