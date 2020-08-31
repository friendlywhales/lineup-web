
import re
import os

from django.conf import settings
from django.shortcuts import render


js_files = ('manifest', 'vendor', 'app', )
_manifest_pattern = re.compile(r'^manifest\.[0-9a-z]+\.js$')
_vendor_pattern = re.compile(r'^vendor\.[0-9a-z]+\.js$')
_app_pattern = re.compile(r'^app\.[0-9a-z]+\.js$')
_app_css_pattern = re.compile(r'^app\.[0-9a-z]+\.css$')
_post_detail_pattern = re.compile(r'^\/p\/(?P<uid>[a-z0-9A-Z\-]+)$')


def index(request):
    path = os.path.join(settings.FRONTEND_PATH, 'static')
    _js_filenames = _get_filenames(
        os.path.join(path, 'js'),
        {
            'manifest': _manifest_pattern,
            'vendor': _vendor_pattern,
            'app': _app_pattern,
        },
    )
    _css_filenames = _get_filenames(
        os.path.join(path, 'css'),
        {
            'app': _app_css_pattern,
        },
    )

    ctx = {
        'js_files': _js_filenames,
        'css_files': _css_filenames,
        'metainfo': _get_post_page_metainfo(
            request,
            _get_content_detail(request.path),
        ),
    }
    return render(request, 'index.html', ctx)


def _get_content_detail(urlpath):
    from contents.models import Post

    matched = _post_detail_pattern.match(urlpath)
    if not matched:
        return
    try:
        o = Post.objects.select_related('user').get(uid=matched['uid'])
    except (KeyError, ValueError, Post.DoesNotExist):
        return
    return o


def _get_post_page_metainfo(request, post):
    default = {
        'title': 'LineUp',
        'description': '',
        'url': settings.FRONT_HOSTNAME,
        'image': 'https://s3.ap-northeast-2.amazonaws.com/lineup-user-assets/lineup-appicon.png',
        'width': 500,
        'height': 120,
    }
    if not post:
        return default
    images = sorted(post.get_thumbnails(request), key=lambda o: o['width'])
    if not images:
        return default

    if not post.user.nickname:
        title = 'LINEUP'
    else:
        title = f'LINEUP의 {post.user.nickname}'
    return {
        'title': title,
        'description': post.content,
        'url': f'{settings.FRONT_HOSTNAME}{post.get_absolute_url()}',
        'image': images[0]['url'],
        'width': images[0]['width'],
        'height': images[0]['height'],
    }


def _get_filenames(path, patterns):
    _filenames = {
        k: {'filename': None, 'date': 0,}
        for k in patterns
    }

    for _f in os.listdir(path):
        _filepath = f'{path}/{_f}'
        if not os.path.isfile(_filepath):
            continue

        key = None
        for key, pattern in patterns.items():
            if pattern.match(_f):
                break
        else:
            continue

        if key not in _filenames:
            continue

        _date = _file_date(_filepath)
        if _filenames[key]['date'] == 0 or _filenames[key]['date'] < _date:
            _filenames[key]['filename'] = _f
            _filenames[key]['date'] = _date

    return _filenames


def _file_date(path):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    stat = os.stat(path)
    try:
        return stat.st_birthtime
    except AttributeError:
        return stat.st_mtime
