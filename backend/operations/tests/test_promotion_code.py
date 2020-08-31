
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


class TestPromotionCodeApi(TestCase, UserMixin):
    def setUp(self):
        call_command('init_perms')
        call_command('init_symbols')
        self.users = [
            self._create_user(**{
                'username': f'testuser{i}',
                'password': 'asdfasdf',
                'level': 'author',
                'email': f'testuser{i}@lineup.com',
            }).update_model_permissions().create_lineup_wallet()
            for i in range(1, 4)
        ]
        self.code1 = models.PromotionCode.objects.create(
            value='abcd-00001',
            allow_quantity=1
        )
        self.code2 = models.PromotionCode.objects.create(
            value='abcd-00002',
            allow_quantity=0
        )
        self.code3 = models.PromotionCode.objects.create(
            value='abcd-00003',
            allow_quantity=0
        )
        self.code4 = models.PromotionCode.objects.create(
            value='abcd-00004',
            allow_quantity=0,
        )
        self.code5 = models.PromotionCode.objects.create(
            value='abcd-00005',
            allow_quantity=0,
            expired_at=timezone.now()
        )

    def test_create_by_model(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                models.PromotionCode.objects.create(
                    value=self.code1.value,
                )

    def test_add_to_user(self):
        user_code1 = self.code1.add_to_user(self.users[0])
        self.assertEqual(user_code1.user, self.users[0])
        self.assertEqual(user_code1.code, self.code1)
        with self.assertRaises(drf_exc.ValidationError) as cm:
            self.code1.add_to_user(self.users[0])
        self.assertEqual(cm.exception.detail['code'], 'duplicated')

        self.code2.add_to_user(self.users[0])
        self.code3.add_to_user(self.users[0])
        with self.assertRaises(drf_exc.ValidationError) as cm:
            self.code4.add_to_user(self.users[0])
        self.assertEqual(cm.exception.detail['code'], 'exceeded')

        with self.assertRaises(drf_exc.ValidationError) as cm:
            self.code1.add_to_user(self.users[1])
        self.assertEqual(cm.exception.detail['code'], 'unavailable')

        self.code2.add_to_user(self.users[1])
        self.code3.add_to_user(self.users[1])
        self.assertEqual(self.code2.users.count(), 2)
        self.assertEqual(self.code3.users.count(), 2)
        self.assertEqual(self.users[1].promotion_codes.count(), 2)

        with self.assertRaises(drf_exc.ValidationError) as cm:
            self.code5.add_to_user(self.users[2])
        self.assertEqual(cm.exception.detail['code'], 'unavailable')

    def test_consume_promotion_code(self):
        from currencies import models as cr_models

        root_user = user_model.objects.get(
            username=settings.SERVICE_ROOT_USERNAME
        )
        user = self.users[0]
        wallet = user.wallet_set \
            .filter(symbol__code=settings.SERVICE_TOKEN_SYMBOL) \
            .first()
        code = models.PromotionCode.objects.create(
            value='zxcv-00001',
            allow_quantity=1,
            extra={
                'lineup_coin': '1000',
            }
        )
        code.add_to_user(user)

        cr_models.Transaction.add(
            sender=root_user,
            receiver=user,
            wallet=wallet,
            amount=code.reward_coin
        )
        wallet.refresh_from_db()
        expected = cr_models.Transaction.objects \
            .filter(receiver=user, wallet=wallet) \
            .aggregate(balance=Sum('amount'))

        self.assertEqual(wallet.balance, expected['balance'])
