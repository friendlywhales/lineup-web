
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient
from test_plus import TestCase

from accounts.tests import UserMixin


user_model = get_user_model()


class TestProfileApi(TestCase, UserMixin):
    def setUp(self):
        call_command('init_perms')
        call_command('init_symbols')
        self.user1_data = {
            'username': 'testuser1',
            'password': 'asdfasdf',
            'level': 'author',
            'email': 'testuser1@lineup.com',
        }
        self.user1 = self._create_user(**self.user1_data)
        self.user1_socialauth = self.attach_socialauth(
            self.user1, 'steemconnect',
            uid='user1-uid',
            extra_data={
                'id': 1234,
                'access_token': 'access_token_1',
                'username': 'user1',
            }
        )
        self.user2_data = {
            'username': 'testuser2',
            'password': 'asdfasdf',
            'level': 'author',
            'email': 'testuser2@lineup.com',
        }
        self.user2 = self._create_user(**self.user2_data)
        self.user2_socialauth = self.attach_socialauth(
            self.user2, 'steemconnect',
            uid='user2-uid',
            extra_data={
                'id': 9876,
                'access_token': 'access_token_2',
                'username': 'user2',
            }
        )

        self.user1.update_model_permissions()
        self.user2.update_model_permissions()

        self.url_prefix = '/api/v1/accounts/'
        self.base_url = f'{self.url_prefix}profiles/'

    def test_signup(self):
        url = f'{self.url_prefix}users/signup/'
        client = APIClient()

        res = client.get(url)
        self.assertEqual(res.status_code, 405)
        res = client.post(url)
        self.assertEqual(res.status_code, 400)

        data = {
            'email': 'asdfjk@a.com',
            'password': '12345678',
        }
        res = client.post(url, data)
        self.assertEqual(res.status_code, 201)
        user = user_model.objects.get(email=data['email'])
        expected_username = user_model.make_temp_username(data['email'])
        self.assertEqual(user.level, settings.DEFAULT_USER_LEVEL)
        self.assertEqual(len(user.username), len(expected_username))
        self.assertEqual(user.username, res.data['username'])

        client.force_authenticate(self.user1)
        data['email'] = 'fffff@b.com'
        res = client.post(url, data)
        self.assertEqual(res.status_code, 400)

    def test_profile_page(self):
        url = f'{self.base_url}{self.user1.username}/'
        client = APIClient()

        res = client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['username'], self.user1.username)

        self.user1.is_active = False
        self.user1.save()
        res = client.get(url)
        self.assertEqual(res.status_code, 404)
        self.user1.is_active = True
        self.user1.save()

    def test_follow(self):
        url = f'{self.base_url}{self.user2.username}/follow/'
        client = APIClient()
        client.force_authenticate(self.user1)

        self.user1.is_active = False
        self.user1.save()
        res = client.post(url)
        self.assertEqual(res.status_code, 403)

        self.user1.is_active = True
        self.user1.save()
        self.user2.is_active = False
        self.user2.save()
        res = client.post(url)
        self.assertEqual(res.status_code, 404)

        self.user2.is_active = True
        self.user2.save()
        res = client.post(url)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(
            self.user1.following_set.filter(target=self.user2).count(),
            1
        )
        res = client.get(f'{self.base_url}{self.user2.username}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['follower_count'], 1)

        url = f'{self.base_url}{self.user1.username}/follow/'
        res = client.post(url)
        self.assertEqual(res.status_code, 400)
        self.assertIn('not-allowed-self', [d.code for d in res.data])

    def test_unfollow(self):
        url = f'{self.base_url}{self.user2.username}/follow/'
        client = APIClient()
        client.force_authenticate(self.user1)

        self.user1.is_active = False
        self.user1.save()
        res = client.post(url)
        self.assertEqual(res.status_code, 403)

        self.user1.is_active = True
        self.user1.save()
        self.user2.is_active = False
        self.user2.save()
        res = client.post(url)
        self.assertEqual(res.status_code, 404)

        self.user2.is_active = True
        self.user2.save()

        res = client.post(url)
        self.assertEqual(res.status_code, 201)
        res = client.post(url)
        self.assertEqual(res.status_code, 204)
        self.assertEqual(
            self.user1.following_set.filter(target=self.user2).count(),
            0
        )
        res = client.get(f'{self.base_url}{self.user2.username}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['follower_count'], 0)

    def test_nickname(self):
        base_url = f'{self.url_prefix}users/'
        url = f'{base_url}{self.user1.uid}/'

        _length = settings.NICKNAME_LENGTH_RANGE
        client = APIClient()
        client.force_authenticate(self.user2)

        res = client.patch(url, {'nickname': ''})
        self.assertEqual(res.status_code, 403)

        client.force_authenticate(self.user1)
        res = client.patch(url, {'nickname': ''})
        self.assertEqual(res.status_code, 400)

        res = client.patch(url, {'nickname': 'a' * (_length[0]-1)})
        self.assertEqual(res.status_code, 400)

        res = client.patch(url, {'nickname': '1234123'})
        self.assertEqual(res.status_code, 400)

        res = client.patch(url, {'nickname': 'a' * (_length[1]+1)})
        self.assertEqual(res.status_code, 400)

        res = client.patch(url, {'nickname': 'sadf\nsaldjflk'})
        self.assertEqual(res.status_code, 400)

        res = client.patch(url, {'nickname': 'no space'})
        self.assertEqual(res.status_code, 400)

        res = client.patch(url, {'nickname': '한국어-_-닉네임'})
        self.assertEqual(res.status_code, 200)
        res = client.patch(url, {'nickname': '宮本茂'})
        self.assertEqual(res.status_code, 200)
        res = client.patch(url, {'nickname': '宮本茂'})
        self.assertEqual(res.status_code, 400)

    def test_connect_steemconnect(self):
        base_url = f'{self.url_prefix}users/'
        url = f'{base_url}social-connect/'

        client1 = APIClient()
        client1_token = self.user1.auth_token.key
        client2 = APIClient()
        client2_token = self.user2.auth_token.key
        client1.force_authenticate(self.user1, client1_token)
        client2.force_authenticate(self.user2, client2_token)
        client3 = APIClient()

        res = client3.post(url, {})
        self.assertEqual(res.status_code, 401)

        for _data in [{}, {'token': ''}, {'provider': ''}, {'token': '', 'provider': ''}]:
            res = client1.post(url, _data)
            jsondata = res.json()
            self.assertEqual(res.status_code, 400)
            self.assertEqual(jsondata['code'], 'invalid-data')

        data = {
            'token': 'sadf',
            'provider': 'steemconnect',
        }
        res = client1.post(url, data)
        jsondata = res.json()
        self.assertEqual(res.status_code, 401)
        self.assertEqual(jsondata['code'], 'invalid-auth-token')

        data['token'] = client1_token
        data['provider'] = 'sadfasdf'
        res = client2.post(url, data)
        jsondata = res.json()
        self.assertEqual(res.status_code, 400)
        self.assertEqual(jsondata['code'], 'invalid-provider')

        data['provider'] = 'steemconnect'
        res = client2.post(url, data)
        jsondata = res.json()
        self.assertEqual(res.status_code, 200)
        sa = self.user1.social_auth.filter(provider=data['provider']).first()
        sa.refresh_from_db()
        self.assertEqual(sa.pk, self.user2_socialauth.pk)
        self.assertIsNotNone(sa)
        self.assertIn('social_auth', jsondata)
        self.assertIn(data['provider'], jsondata['social_auth'])
        _data = jsondata['social_auth'][data['provider']]
        self.assertEqual(_data['uid'], sa.uid)
        self.assertEqual(_data['access_token'], sa.access_token)
