
from django.db import transaction
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from test_plus import TestCase

from accounts.tests import UserMixin
from .. import models


user_model = get_user_model()


class TestCollectionModel(TestCase, UserMixin):
    def setUp(self):
        self.user1 = self._create_user()

    @staticmethod
    def _create_collection(**kwargs):
        return models.Collection.objects.create(**kwargs)

    @staticmethod
    def _create_tag(**kwargs):
        return models.Tag.objects.create(**kwargs)

    @staticmethod
    def _create_post(**kwargs):
        return models.Post.objects.create(**kwargs)

    def test_create_collection(self):
        o = self._create_collection(
            user=self.user1,
            name='test collection'
        )
        self.assertIsNotNone(o.pk)

    def test_create_tag(self):
        o = self._create_tag(name='tag')
        self.assertIsNotNone(o.pk)

    def test_create_post(self):
        o = self._create_post(
            user=self.user1,
            content='lorem ipsum'
        )
        self.assertIsNotNone(o.pk)

        t = self._create_tag(name='tag')
        o.tags.add(t)
        o.tags.add(t)
        o.tags.add(t)
        self.assertEqual(o.tags.count(), 1)

    def test_post_collection(self):
        p1 = self._create_post(
            user=self.user1,
            content='lorem ipsum 1'
        )
        p2 = self._create_post(
            user=self.user1,
            content='lorem ipsum 2'
        )
        c = self._create_collection(
            user=self.user1,
            name='test collection 123'
        )
        models.PostCollection.objects.create(collection=c, post=p2)
        models.PostCollection.objects.create(collection=c, post=p1)

        results = c.posts.order_by('-pk')
        self.assertEqual(results.count(), 2)
        self.assertEqual(results[0], p2)
        self.assertEqual(results[1], p1)

    def test_like(self):
        p1 = self._create_post(
            user=self.user1,
            content='lorem ipsum'
        )
        l = models.Like.objects.create(
            user=self.user1,
            post=p1
        )
        self.assertIsNotNone(l)

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                models.Like.objects.create(
                    user=self.user1,
                    post=p1
            )
