
from django.conf import settings
from django.http import HttpResponseRedirect
from social_django import middleware
from raven.contrib.django.raven_compat.models import client
from social_core.exceptions import AuthCanceled, AuthForbidden, AuthUnreachableProvider


class SocialAuthExceptionMiddleware(middleware.SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if isinstance(exception, KeyError):
            client.captureException()
            url = f'{settings.FRONT_HOSTNAME}/errors/invalid-steem-extra-data'
            return HttpResponseRedirect(url)
        elif isinstance(
                exception,
                (AuthCanceled, AuthForbidden, AuthUnreachableProvider, )
        ):
            client.captureException()
            url = f'{settings.FRONT_HOSTNAME}/errors/failure-from-social-auth'
            return HttpResponseRedirect(url)
        return super().process_exception(request, exception)
