
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model

user_class = get_user_model()


def social_user(backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            user.delete()
            user = social.user
        elif not user:
            user = social.user
    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': social is None}


def user_info(backend, details, response, user=None, *args, **kwargs):
    if not isinstance(user, user_class) or not user.is_authenticated:
        return
    user.level = settings.DEFAULT_USER_LEVEL
    user.is_verified = True
    user.open_status = 'public'
    user.signup_route = 'steem'
    user.save()
    user.update_model_permissions()
