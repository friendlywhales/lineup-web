
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient
from test_plus import TestCase

from accounts.tests import UserMixin
from .. import models


user_model = get_user_model()


class TestCollectionApi(TestCase, UserMixin):
    def setUp(self):
        call_command('init_perms')
        self.user1_data = {
            'username': 'testuser1',
            'password': 'asdfasdf',
            'level': 'regular',
            'email': 'testuser1@lineup.com',
        }
        self.user1 = self._create_user(**self.user1_data)
        self.user2_data = {
            'username': 'testuser2',
            'password': 'asdfasdf',
            'level': 'regular',
            'email': 'testuser2@lineup.com',
        }
        self.user2 = self._create_user(**self.user2_data)

        self.user1.update_model_permissions()
        self.user2.update_model_permissions()

        self.collection1 = models.Collection.objects.create(
            user=self.user1,
            name='test collection',
        )
        self.url_prefix = '/api/v1/contents/'
        self.base_url = f'{self.url_prefix}collections/'

    def test_create_collection(self):
        url = self.base_url
        client = APIClient()
        data = {
            'name': 'qwerrasafqwff@@',
        }

        res = client.post(url, data)
        self.assertEqual(res.status_code, 401)

        client.login(username=self.user1_data['username'],
                     password=self.user1_data['password'])

        res = client.post(url, {})
        self.assertEqual(res.status_code, 400)

        res = client.post(url, data, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertIsNotNone(models.Collection.objects.get(name=data['name']))

        self._switch_user_level(self.user1, 'associate')
        res = client.post(url, data, format='json')
        self.assertEqual(res.status_code, 403)
        self._switch_user_level(self.user1, 'regular')

    def test_update_collection(self):
        o = models.Collection.objects.create(
            user=self.user1,
            name='lorem ipsum'
        )
        url = o.get_absolute_url()
        data = {'name': 'hello'}
        client = APIClient()

        res = client.get(url)
        self.assertEqual(res.status_code, 200)

        res = client.put(url, data=data)
        self.assertEqual(res.status_code, 401)

        client.login(username=self.user2_data['username'],
                     password=self.user2_data['password'])

        res = client.put(url, data=data)
        self.assertEqual(res.status_code, 403)

        client.logout()
        client.login(username=self.user1_data['username'],
                     password=self.user1_data['password'])
        res = client.put(url, data=data)
        self.assertEqual(res.status_code, 200)

        o.refresh_from_db()
        self.assertEqual(o.name, data['name'])

        self._switch_user_level(self.user1, 'associate')
        res = client.put(url, data, format='json')
        self.assertEqual(res.status_code, 403)
        self._switch_user_level(self.user1, 'regular')

    def test_delete_collection(self):
        o = models.Collection.objects.create(
            user=self.user1,
            name='lorem ipsum'
        )
        url = o.get_absolute_url()
        client = APIClient()

        res = client.get(url)
        self.assertEqual(res.status_code, 200)

        res = client.delete(url, follow=False)
        self.assertEqual(res.status_code, 401)

        client.login(username=self.user2_data['username'],
                     password=self.user2_data['password'])

        res = client.delete(url)
        self.assertEqual(res.status_code, 403)

        client.logout()
        client.login(username=self.user1_data['username'],
                     password=self.user1_data['password'])
        res = client.delete(url)
        self.assertEqual(res.status_code, 204)

        self._switch_user_level(self.user1, 'associate')
        res = client.delete(url)
        self.assertEqual(res.status_code, 403)
        self._switch_user_level(self.user1, 'regular')

