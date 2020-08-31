
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.files import temp as tempfile
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from test_plus import TestCase
from PIL import Image

from accounts.tests import UserMixin
from accounts import models as a_models
from contents import models as c_models
from .. import models


user_model = get_user_model()


class TestPostNotificationApi(TestCase, UserMixin):
    def setUp(self):
        call_command('init_perms')
        self.user1_data = {
            'username': 'testuser1',
            'password': 'asdfasdf',
            'level': 'author',
            'email': 'testuser1@lineup.com',
        }
        self.user1 = self._create_user(**self.user1_data)
        self.user2_data = {
            'username': 'testuser2',
            'password': 'asdfasdf',
            'level': 'author',
            'email': 'testuser2@lineup.com',
        }
        self.user2 = self._create_user(**self.user2_data)
        self.user3_data = {
            'username': 'testuser3',
            'password': 'asdfasdf',
            'level': 'regular',
            'email': 'testuser3@lineup.com',
        }
        self.user3 = self._create_user(**self.user3_data)

        self.user1.update_model_permissions()
        self.user2.update_model_permissions()
        self.user3.update_model_permissions()

        a_models.Follower.follow(self.user2, self.user1)

        self.url_prefix = '/api/v1/messaging/'
        self.contents_url_prefix = '/api/v1/contents/'
        self.contents_base_url = f'{self.contents_url_prefix}posts/'
        self.noti_url = f'{self.url_prefix}notifications/'

    def test_create_post(self):
        client = APIClient()
        client2 = APIClient()
        client.force_authenticate(self.user1)
        client2.force_authenticate(self.user2)
        ct = ContentType.objects.get(app_label='contents', model='post')

        post = c_models.Post.objects.create(
            user=self.user1,
            status='drafted',
            content='lorem ipsum',
        )
        self.assertIsNotNone(post)
        post_url = f'{self.contents_base_url}{post.uid}/'

        with tempfile.NamedTemporaryFile(suffix='.jpg') as fp:
            with Image.new('RGB', (800, 800)) as image_fp:
                image_fp.save(fp, format='JPEG')
                fp.seek(0)
                data = {
                    'content': fp,
                    'order': 1,
                }
                res = client.post(f'{post_url}attachments/',
                                  data,
                                  format='multipart')
                self.assertEqual(res.status_code, 201)
        res = client.post(f'{post_url}publish/')
        noti = self.user2.notifications.filter(content_type=ct,
                                               object_id=post.pk,
                                               trigger=self.user1).last()
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(noti)
        self.assertEqual(noti.kind, 'following_new_post')

        res = client2.get(self.noti_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['results'][0]['kind'], noti.kind)

    def test_create_comment(self):
        client1 = APIClient()
        client2 = APIClient()
        client3 = APIClient()
        client1.force_authenticate(self.user1)
        client2.force_authenticate(self.user2)
        client3.force_authenticate(self.user3)
        ct = ContentType.objects.get(app_label='contents', model='comment')
        data = {
            'content': 'hello comment',
        }

        post = c_models.Post.objects.create(
            user=self.user1,
            status='published',
            content='lorem ipsum',
        )
        self.assertIsNotNone(post)
        url = f'{self.contents_base_url}{post.uid}/comments/'

        res = client2.post(url, data)
        self.assertEqual(res.status_code, 201)
        comment = post.comment_set.filter(user=self.user2).last()
        noti = self.user1.notifications.last()
        self.assertIsNotNone(noti)
        self.assertEqual(noti.content_object, comment)
        self.assertEqual(noti.trigger, self.user2)
        self.assertEqual(noti.kind, 'new_comment_user_posted')

        res = client3.post(url, data)
        self.assertEqual(res.status_code, 201)
        comment = post.comment_set.filter(user=self.user3).last()
        self.assertIsNotNone(comment)
        noti = self.user1.notifications.filter(content_type=ct,
                                               object_id=comment.pk,
                                               trigger=self.user3).last()
        self.assertIsNotNone(noti)
        self.assertEqual(noti.kind, 'new_comment_user_posted')

        noti = self.user2.notifications.filter(content_type=ct,
                                               object_id=comment.pk,
                                               trigger=self.user3).last()
        self.assertIsNotNone(noti)
        self.assertEqual(noti.kind, 'new_comment_user_commented')

        res = client1.post(url, data)
        self.assertEqual(res.status_code, 201)
        comment = post.comment_set.filter(user=self.user1).last()
        self.assertIsNotNone(comment)
        exist = self.user1.notifications.filter(
            content_type=ct,
            object_id=comment.pk,
            kind='new_comment_user_posted'
        ).exists()
        self.assertFalse(exist)

        res = client1.get(self.noti_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['results'][0]['kind'], 'new_comment_user_posted')

    def test_create_like(self):
        client1 = APIClient()
        client2 = APIClient()
        client3 = APIClient()
        client1.force_authenticate(self.user1)
        client2.force_authenticate(self.user2)
        client3.force_authenticate(self.user3)
        ct = ContentType.objects.get(app_label='contents', model='like')

        post = c_models.Post.objects.create(
            user=self.user1,
            status='published',
            content='lorem ipsum',
        )
        self.assertIsNotNone(post)
        url = f'{self.contents_base_url}{post.uid}/likes/'

        res = client2.post(url)
        self.assertEqual(res.status_code, 201)
        res = client3.post(url)
        self.assertEqual(res.status_code, 201)
        like = post.like_set.filter(user=self.user3).last()
        self.assertIsNotNone(like)

        noti = self.user2.notifications.filter(content_type=ct,
                                               object_id=like.pk,
                                               trigger=self.user3).last()
        self.assertIsNotNone(noti)
        self.assertEqual(noti.kind, 'new_vote_user_voted')

        res = client2.get(self.noti_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['results'][0]['kind'], 'new_vote_user_voted')
