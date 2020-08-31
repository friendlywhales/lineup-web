
from django.conf import settings
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import exceptions as drf_exc
from test_plus import TestCase

from accounts.tests import UserMixin
from .. import models


user_model = get_user_model()


class TestIssuePointApi(TestCase, UserMixin):
    def setUp(self):
        call_command('init_perms')
        call_command('init_symbols')
        call_command('init_point_behaviours')
        self.users = [
            self._create_user(**{
                'username': f'testuser{i}',
                'password': 'asdfasdf',
                'level': 'author',
                'email': f'testuser{i}@lineup.com',
            }).update_model_permissions().create_lineup_wallet()
            for i in range(1, 4)
        ]
