
import os
import raven

from .settings import *


FRONT_HOSTNAME = 'https://beta.line-up.me'

DEBUG = False

ALLOWED_HOSTS = ['beta.line-up.me', 'line-up.me', 'www.line-up.me', 'api.line-up.me']

INSTALLED_APPS += [
    'raven.contrib.django.raven_compat',
]
try:
    INSTALLED_APPS.remove('silk')
    INSTALLED_APPS.remove('drf_yasg')
    MIDDLEWARE.remove('silk.middleware.SilkyMiddleware')
except Exception:
    pass

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ['LINEUP_DB_HOST'],
        'NAME': '',
        'USER': '',
        'PASSWORD': os.environ['LINEUP_DB_PW'],
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    'line-up.me',
    'beta.line-up.me',
    'api.line-up.me',
)

FRONTEND_LOGIN_REDIRECT_URL = f'{FRONT_HOSTNAME}/social-auth/login/done'
FRONTEND_LOGIN_URL = f'{FRONT_HOSTNAME}/login'

INACTIVE_USER_URL = f'{FRONT_HOSTNAME}/login?type=inactive-user'
LOGIN_ERROR_URL = f'{FRONT_HOSTNAME}/login?type=error'

SESSION_COOKIE_DOMAIN = ".line-up.me"

# DEFAULT_USER_LEVEL = 'associate'  # 회원 가입시 기본 등급
DEFAULT_USER_LEVEL = 'author'  # 6월 2일 only 전 한정.

RAVEN_CONFIG = {
    'dsn': '',
    'release': raven.fetch_git_sha(os.path.abspath(os.pardir)),
}

# AMAZON S3 settings---------------------------------------------------

AWS_STORAGE_BUCKET_NAME = 'lineup-user-assets'

AWS_ACCESS_KEY_ID = os.environ.get('LINEUP_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('LINEUP_AWS_SECRET_ACCESS_KEY')

AWS_REGION = 'ap-northeast-2'
AWS_S3_HOST = f's3-{AWS_REGION}.amazonaws.com'
S3_USE_SIGV4 = True

AWS_S3_FILE_OVERWRITE = False

AWS_S3_KEY_PREFIX = 'uploads'
DEFAULT_FILE_STORAGE = 'apiserver.storages.aws_s3.MediaStorage'

AWS_S3_URL_EXPIRIATION = 60 * 60 * 24 * 30  # seconds

# celery settings---------------------------------------------------

CELERY_BROKER_URL = 'redis://apiserver-redis.0dsmbe.ng.0001.apn2.cache.amazonaws.com:6379/0'

CELERY_RESULT_BACKEND = 'redis://apiserver-redis.0dsmbe.ng.0001.apn2.cache.amazonaws.com:6379/2'

FRONTEND_PATH = '/var/www/beta-frontend'
