
from django.conf import settings
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Sum
from django.core.files import temp as tempfile
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from rest_framework import exceptions as drf_exc
from test_plus import TestCase
from PIL import Image

from accounts.tests import UserMixin
from .. import tasks
from .. import models


user_model = get_user_model()


class TestIssuePoint(TestCase, UserMixin):
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
        for u in self.users:
            models.PointStatus.objects.get_or_create(
                user=u,
                defaults={
                    'user': u,
                    'point': 0,
                }
            )

    def test_signup_point(self):
        user = self.users[0]
        tasks.issue_signup_point(user)
        behaviour = models.Behaviour.objects.get(code='signup')
        status = models.PointStatus.objects.get(user=user)

        expected = behaviour.reward
        self.assertEqual(expected, status.point)

        # 이미 회원가입 포인트를 받은 뒤엔 중복 지급 안 함.
        tasks.issue_signup_point(user)
        expected = behaviour.reward
        status.refresh_from_db()
        self.assertEqual(expected, status.point)

    def test_login_point(self):
        user = self.users[0]
        tasks.issue_login_point(user)
        behaviour = models.Behaviour.objects.get(code='login')
        status = models.PointStatus.objects.get(user=user)

        self.assertEqual(behaviour.reward, status.point)

        tasks.issue_login_point(user)
        self.assertNotEqual(behaviour.reward * 2, status.point)
        self.assertEqual(behaviour.reward, status.point)

    def test_follow_point(self):
        from accounts import models as a_models

        user = self.users[0]
        status1 = models.PointStatus.objects.get(user=user)
        user2 = self.users[1]
        status2 = models.PointStatus.objects.get(user=user2)
        behaviour = models.Behaviour.objects.get(code='follow')
        behaviour2 = models.Behaviour.objects.get(code='unfollow')

        # follower가 생긴 user2 에게 포인트 지급
        a_models.Follower.follow(user, user2)
        expected = status2.point + behaviour.reward
        status2.refresh_from_db()
        self.assertEqual(expected, status2.point)

        # 중복 following 이므로 포인트 지급 안 함.
        try:
            a_models.Follower.follow(user, user2)
        except drf_exc.ValidationError:
            pass
        expected = status2.point
        status2.refresh_from_db()
        self.assertEqual(expected, status2.point)

        # unfollow 이므로 포인트 차감
        a_models.Follower.unfollow(user, user2)
        expected = status2.point + behaviour2.reward
        status2.refresh_from_db()
        self.assertEqual(expected, status2.point)

        # 중복 unfollow 이므로 변화 없음
        try:
            a_models.Follower.unfollow(user, user2)
        except drf_exc.NotFound:
            pass
        expected = status2.point
        status2.refresh_from_db()
        self.assertEqual(expected, status2.point)

    def test_like_point(self):
        from contents import models as c_models

        user = self.users[0]
        status1 = models.PointStatus.objects.get(user=user)
        user2 = self.users[1]
        status2 = models.PointStatus.objects.get(user=user2)
        user3 = self.users[2]
        status3 = models.PointStatus.objects.get(user=user3)
        post = c_models.Post.objects.create(user=user2, content='lorem')
        behaviour = models.Behaviour.objects.get(code='give-like')
        behaviour2 = models.Behaviour.objects.get(code='give-unlike')
        behaviour3 = models.Behaviour.objects.get(code='take-like')
        behaviour4 = models.Behaviour.objects.get(code='take-unlike')

        # 자기 자신한테 한 행위에 대해서는 포인트 부여 안 함.
        tasks.issue_like_point(user, post)
        status2.refresh_from_db()
        self.assertEqual(0, status2.point)

        # 미 발행 글이므로 포인트 부여 안 함
        tasks.issue_like_point(user, post)
        expected1 = 0
        expected2 = 0
        status1.refresh_from_db()
        status2.refresh_from_db()
        self.assertEqual(expected1, status1.point)
        self.assertEqual(expected2, status2.point)

        # 포인트 부여
        post.status = 'published'
        post.save()
        c_models.Like.objects.create(user=user, post=post)
        tasks.issue_like_point(user, post)
        expected1 = status1.point + behaviour.reward
        expected2 = status2.point + behaviour3.reward
        status1.refresh_from_db()
        status2.refresh_from_db()
        self.assertEqual(expected1, status1.point)
        self.assertEqual(expected2, status2.point)

        # 포인트 부여
        c_models.Like.objects.create(user=user3, post=post)
        tasks.issue_like_point(user3, post)
        expected1 = status3.point + behaviour.reward
        expected2 = status2.point + behaviour3.reward
        status3.refresh_from_db()
        status2.refresh_from_db()
        self.assertEqual(expected1, status3.point)
        self.assertEqual(expected2, status2.point)

        # 포인트 차감
        c_models.Like.objects.get(user=user, post=post).delete()
        tasks.issue_unlike_point(user, post)
        expected1 = status1.point + behaviour2.reward
        expected2 = status2.point + behaviour4.reward
        status1.refresh_from_db()
        status2.refresh_from_db()
        self.assertEqual(expected1, status1.point)
        self.assertEqual(expected2, status2.point)

        # 포인트 차감
        c_models.Like.objects.get(user=user3, post=post).delete()
        tasks.issue_unlike_point(user3, post)
        expected1 = status3.point + behaviour2.reward
        expected2 = status2.point + behaviour4.reward
        status3.refresh_from_db()
        status2.refresh_from_db()
        self.assertEqual(expected1, status3.point)
        self.assertEqual(expected2, status2.point)

    def test_comment_point(self):
        from contents import models as c_models

        user = self.users[0]
        user2 = self.users[1]
        post = c_models.Post.objects.create(user=user, content='lorem')

        behaviour = models.Behaviour.objects.get(code='comment')
        status = models.PointStatus.objects.get(user=user)

        # 미발행 글에 댓글을 달았으므로 적립 안 됨.
        comment = c_models.Comment.objects.create(
            user=user,
            post=post,
            content='lorem'
        )
        comment.issue_point()
        expected = status.point
        status.refresh_from_db()
        self.assertEqual(expected, status.point)

        # 발행 글이지만 자신의 글에 단 댓글 이므로 적립 안 됨.
        post.status = 'published'
        post.save()
        comment.issue_point()
        expected = status.point
        status.refresh_from_db()
        self.assertEqual(expected, status.point)

        # 발행된 글이고 타인이 댓글을 달았으므로 적립 됨.
        post.user = user2
        post.save()
        comment.issue_point()
        expected = behaviour.reward + status.point
        status.refresh_from_db()
        self.assertEqual(expected, status.point)

    def test_posting_point(self):
        from contents import models as c_models

        user = self.users[0]
        post = c_models.Post(user=user)
        tasks.issue_posting_point(post)
        behaviour = models.Behaviour.objects.get(code='posting')
        behaviour2 = models.Behaviour.objects.get(code='unposting')
        status = models.PointStatus.objects.get(user=user)
        self.assertEqual(behaviour.reward, status.point)

        tasks.issue_posting_point(post)
        expected = status.point + behaviour.reward
        status.refresh_from_db()
        self.assertEqual(expected, status.point)

        tasks.issue_unposting_point(post)
        expected = status.point + behaviour2.reward
        status.refresh_from_db()
        self.assertEqual(expected, status.point)

        # 게시물 발행했을 때 포인트 적립되는 지 테스트
        post = c_models.Post.objects.create(user=user, content='lorem')
        self._attach_file_to_post(post)

        expected = status.point
        status.refresh_from_db()
        self.assertEqual(expected, status.point)

        post.publish()
        expected = status.point + behaviour.reward
        status.refresh_from_db()
        self.assertEqual(expected, status.point)

    @staticmethod
    def _attach_file_to_post(post):
        from contents import models as c_models

        with tempfile.NamedTemporaryFile(suffix='.jpg') as fp:
            with Image.new('RGB', (800, 800)) as image_fp:
                image_fp.save(fp, format='JPEG')
                fp.seek(0)

            c_models.Attachment.objects.create(
                post=post,
                content=fp.name,
            )
