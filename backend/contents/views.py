
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from . import models


# @cache_page(settings.DEFAULT_ASSET_REDIRECT_CACHE)
def asset_redirect(request, uid):
    obj = get_object_or_404(models.Attachment, uid=uid)
    return HttpResponseRedirect(obj.content.url)
