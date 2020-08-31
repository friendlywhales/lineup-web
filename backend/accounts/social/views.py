
import urllib.parse

from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework.authtoken.models import Token


def done(request, backend='steemconnect', *args, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(settings.LOGIN_ERROR_URL)
    token, _ = Token.objects.get_or_create(user=request.user)
    querystring = urllib.parse.urlencode({
        't': token,
        'u': request.user.username,
        'p': backend
    })
    url = f'{settings.FRONTEND_LOGIN_REDIRECT_URL}?{querystring}'
    return HttpResponseRedirect(url)

