
from .settings_prod import *

DEBUG = True

FRONT_HOSTNAME = 'https://staging.line-up.me'

INSTALLED_APPS.append('silk')
INSTALLED_APPS.append('drf_yasg')

ALLOWED_HOSTS = [
    'beta.line-up.me', 'line-up.me', 'www.line-up.me', 'api.line-up.me',
    'staging-api.line-up.me', 'staging.line-up.me',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ['LINEUP_DB_HOST'],
        'NAME': 'lineupdb_staging',
        'USER': 'lineup_prod',
        'PASSWORD': os.environ['LINEUP_DB_PW'],
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

AWS_STORAGE_BUCKET_NAME = 'lineup-staging-user-assets'

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    'line-up.me',
    'staging.line-up.me',
    'staging-api.line-up.me',
)


# celery settings---------------------------------------------------

CELERY_BROKER_URL = 'redis://apiserver-redis.0dsmbe.ng.0001.apn2.cache.amazonaws.com:6379/1'

CELERY_RESULT_BACKEND = 'redis://apiserver-redis.0dsmbe.ng.0001.apn2.cache.amazonaws.com:6379/3'

FRONTEND_PATH = '/var/www/beta-staging-frontned'
