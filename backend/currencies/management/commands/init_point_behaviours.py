
from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        items = (
            {
                'code': 'signup',
                'reward': 300,
            },
            {
                'code': 'signup_for_inviter',
                'reward': 100,
            },
            {
                'code': 'signup_for_invitee',
                'reward': 200,
            },
            {
                'code': 'login',
                'reward': 100,
            },
            {
                'code': 'follow',
                'reward': 50,
            },
            {
                'code': 'unfollow',
                'reward': -50,
            },
            {
                'code': 'take-like',
                'reward': 80,
            },
            {
                'code': 'take-unlike',
                'reward': -80,
            },
            {
                'code': 'give-like',
                'reward': 20,
            },
            {
                'code': 'give-unlike',
                'reward': -20,
            },
            {
                'code': 'comment',
                'reward': 50,
            },
            {
                'code': 'posting',
                'reward': 200,
            },
            {
                'code': 'unposting',
                'reward': -200,
            },
        )

        for item in items:
            o, is_created = models.Behaviour.objects.get_or_create(
                code=item['code'], defaults=item
            )
            self.stdout.write(f'{o.code} is set')
