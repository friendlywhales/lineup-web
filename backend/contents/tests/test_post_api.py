
from django.utils import html as django_html
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.files import temp as tempfile
from rest_framework.test import APIClient
from test_plus import TestCase
from PIL import Image

from accounts.tests import UserMixin
from ..api import serializers
from ..api.serializers import PATTERN_HASH_TAG
from .. import models


user_model = get_user_model()


class TestPostApi(TestCase, UserMixin):
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

        self.user1.update_model_permissions()
        self.user2.update_model_permissions()

        self.url_prefix = '/api/v1/contents/'
        self.base_url = f'{self.url_prefix}posts/'

    def test_create_post(self):
        url = self.base_url
        client = APIClient()
        data = {
            'content': '''해시 태그를 뽑아보자.
        #tag #이것도 #안녕-하하 #반가_워 #1234tag
        해시태그가 총 다섯 개.
        ''',
        }

        res = client.post(url, data)
        self.assertEqual(res.status_code, 401)

        client.login(username=self.user1_data['username'],
                     password=self.user1_data['password'])

        res = client.post(url, {})
        self.assertEqual(res.status_code, 201)

        res = client.post(url, data, format='json')
        expected_tags = frozenset([t['name'] for t in res.data['tags']])
        self.assertEqual(res.status_code, 201)
        post = models.Post.objects.order_by('-pk').first()
        result_tags = frozenset([t.name for t in post.tags.all()])
        self.assertIsNotNone(post)
        self.assertEqual(django_html.linebreaks(post.escaped_content), res.data['content'])
        self.assertEqual(result_tags, expected_tags)

        res = client.get(f'{post.get_absolute_url()}')
        self.assertEqual(res.status_code, 200)

        self._switch_user_level(self.user1, 'regular')
        res = client.post(url, data, format='json')
        self.assertEqual(res.status_code, 403)
        self._switch_user_level(self.user1, 'associate')
        res = client.post(url, data, format='json')
        self.assertEqual(res.status_code, 403)
        self._switch_user_level(self.user1, 'author')

    def test_split_hashtags_in_content(self):
        text = '''해시 태그를 뽑아보자.
        #tag #이것도 #안녕-하하 #반가_워 #1234tag
        해시태그가 총 다섯 개.
        '''
        result = PATTERN_HASH_TAG.findall(text)
        expected = ('tag', '이것도', '안녕-하하', '반가', '1234tag', )
        self.assertEqual(frozenset(result), frozenset(expected))

    def test_post_with_attachment(self):
        client = APIClient()
        thumb_sizes_number = len(models.Attachment.thumbnail_sizes)

        client.force_authenticate(self.user1)

        post = models.Post.objects.create(
            user=self.user1,
            status='drafted',
            content='lorem ipsum',
        )
        self.assertIsNotNone(post)

        url = f'{self.base_url}{post.uid}/attachments/'
        with tempfile.NamedTemporaryFile(suffix='.jpg') as fp:
            with Image.new('RGB', (800, 800)) as image_fp:
                image_fp.save(fp, format='JPEG')
                fp.seek(0)
                data = {
                    'content': fp,
                    'order': 1,
                }
                res = client.post(url, data, format='multipart')
                self.assertEqual(res.status_code, 201)
        post.refresh_from_db()
        self.assertEqual(post.attachment_set.count(), 1 + thumb_sizes_number - 1)

    def test_like(self):
        client = APIClient()

        client.force_authenticate(self.user1)
        post = models.Post.objects.create(
            user=self.user1,
            status='drafted',
            content='lorem ipsum',
        )
        self.assertIsNotNone(post)
        url = f'{self.base_url}{post.uid}/likes/'

        res = client.post(url, {})
        self.assertEqual(res.status_code, 404)

        post.status = 'published'
        post.save()

        res = client.post(url, {})
        self.assertIn(res.status_code, (200, 201, ))
        post.refresh_from_db()
        self.assertEqual(post.like_set.filter(user=self.user1).count(), 1)

        res = client.post(url, {})
        self.assertEqual(res.status_code, 204)
        post.refresh_from_db()
        self.assertEqual(post.like_set.filter(user=self.user1).count(), 0)

    def test_comment(self):
        client = APIClient()
        data = {
            'content': 'hello comment',
        }

        client.force_authenticate(self.user1)
        post = models.Post.objects.create(
            user=self.user1,
            status='drafted',
            content='lorem ipsum',
        )
        self.assertIsNotNone(post)
        url = f'{self.base_url}{post.uid}/comments/'

        res = client.post(url, data)
        self.assertEqual(res.status_code, 404)

        post.status = 'published'
        post.save()

        res = client.post(url, data)
        self.assertEqual(res.status_code, 201)
        post.refresh_from_db()
        self.assertEqual(post.comment_set.count(), 1)

    def test_publish_post(self):
        client = APIClient()
        thumb_sizes_number = len(models.Attachment.thumbnail_sizes)

        client.force_authenticate(self.user1)
        post = models.Post.objects.create(
            user=self.user1,
            status='drafted',
            content='''해시 태그를 뽑아보자.
        #tag #이것도 #안녕-하하 #반가_워 #1234tag
        해시태그가 총 다섯 개.
        '''
        )
        self.assertIsNotNone(post)
        url = f'{self.base_url}{post.uid}/publish/'
        res = client.post(url)
        self.assertEqual(res.status_code, 400)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as fp:
            with Image.new('RGB', (800, 800)) as image_fp:
                image_fp.save(fp, format='JPEG')
                fp.seek(0)
                data = {
                    'content': fp,
                    'order': 1,
                }
                res = client.post(f'{self.base_url}{post.uid}/attachments/',
                                  data,
                                  format='multipart')
                self.assertEqual(res.status_code, 201)
        post.refresh_from_db()
        self.assertEqual(post.attachment_set.count(), 1 + thumb_sizes_number - 1)

        res = client.post(url)
        post.refresh_from_db()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(post.status, 'published')
        expected = django_html.linebreaks(post.escaped_content)
        self.assertEqual(expected, res.data['content'])

        res = client.post(url)
        self.assertEqual(res.status_code, 400)

    def test_report_post(self):
        client = APIClient()
        client.force_authenticate(self.user1)
        post = models.Post.objects.create(
            user=self.user1,
            status='drafted',
            content='''해시 태그를 뽑아보자.
            #tag #이것도 #안녕-하하 #반가_워 #1234tag
            해시태그가 총 다섯 개.
            '''
        )
        self.assertIsNotNone(post)
        url = f'{self.base_url}{post.uid}/report/'
        res = client.post(url)
        self.assertEqual(res.status_code, 404)

        post.status = 'published'
        post.save()

        res = client.post(url)
        self.assertEqual(res.status_code, 400)

        data = {
            'kind': 'spam',
        }
        res = client.post(url, data)
        qs = models.ReportPost.objects.filter(post=post, user=self.user1)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(qs.exists())

        data['kind'] = 'inappropriate'
        res = client.post(url, data)
        obj = qs.first()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(obj.kind, 'inappropriate')
        self.assertEqual(qs.count(), 1)
