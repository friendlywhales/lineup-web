
from django.conf import settings

from . import models
from .clients.bezant import Client as BezantClient


def _issue_point_to_user(user, behaviour_code, amount=0, reason=None):
    try:
        behaviour = models.Behaviour.objects.get(code=behaviour_code)
    except models.Behaviour.DoesNotExist:
        return

    behaviour.issue_point_to_user(user, amount, reason)


def issue_signup_point(user):
    try:
        if user.invited_by:
            b = models.Behaviour.objects.get(code='signup_for_invitee')
        else:
            b = models.Behaviour.objects.get(code='signup')
    except models.Behaviour.DoesNotExist:
        return

    qs = models.BehaviourPointLog.objects.filter(user=user, behaviour=b)
    if qs.exists():
        return

    if user.invited_by:
        _issue_point_to_user(
            user,
            'signup_for_invitee',
            reason='invited_by_recommended_code',
        )
        _issue_point_to_user(
            user.invited_by,
            'signup_for_inviter',
            reason='invite_user',
        )
    else:
        _issue_point_to_user(user, 'signup')


def issue_login_point(user):
    _issue_point_to_user(user, 'login')


def issue_follow_point(user, target_user):
    if user == target_user:
        return
    if not user.following_set.filter(target=target_user).exists():
        return
    _issue_point_to_user(target_user, 'follow')


def issue_unfollow_point(user, target_user):
    if user == target_user:
        return
    if user.following_set.filter(target=target_user).exists():
        return
    _issue_point_to_user(target_user, 'unfollow')


def issue_like_point(user, target):
    # target == Post 인스턴스

    if user == target.user:
        return
    if target.status != 'published':
        return
    if not target.like_set.filter(user=user).exists():
        return
    _issue_point_to_user(user, 'give-like')
    _issue_point_to_user(target.user, 'take-like')


def issue_unlike_point(user, target):
    # target == Post 인스턴스

    if user == target.user:
        return
    if target.status != 'published':
        return
    if target.like_set.filter(user=user).exists():
        return
    _issue_point_to_user(user, 'give-unlike')
    _issue_point_to_user(target.user, 'take-unlike')


def issue_comment_point(user, target):
    # target == Post 인스턴스

    if user == target.user:
        return
    if target.status != 'published':
        return
    _issue_point_to_user(user, 'comment')


def issue_posting_point(target):
    # target == Post 인스턴스
    _issue_point_to_user(target.user, 'posting')


def issue_unposting_point(target):
    # target == Post 인스턴스
    _issue_point_to_user(target.user, 'unposting')
    try:
        behaviour = models.Behaviour.objects.get(code='take-unlike')
    except models.Behaviour.DoesNotExist:
        return
    likes = target.like_set.count()
    if not likes:
        return
    amount = likes * behaviour.reward * likes
    _issue_point_to_user(
        target.user,
        'take-unlike',
        amount,
        models.BehaviourPointLog.reasons.SUM_UNLIKE_POINT_BY_DELETED_POSTING,
    )


def create_bezant_wallet(password: str) -> str:
    client = BezantClient(
        endpoint=settings.BEZANT_ENDPOINT,
        apikey=settings.BEZANT_APIKEY,
    )
    result = client.create_wallet(password)
    return result['message']['enrollmentID']
