
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
        'HOST': os.environ[''],
        'NAME': '',
        'USER': '',
        'PASSWORD': os.environ[''],
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

AWS_STORAGE_BUCKET_NAME = 'lineup-staging-user-assets'

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    '',
    '',
    '',
)


# celery settings---------------------------------------------------

CELERY_BROKER_URL = ''

CELERY_RESULT_BACKEND = ''

FRONTEND_PATH = ''
