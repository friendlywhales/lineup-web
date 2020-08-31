
import os

from corsheaders.defaults import default_headers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '_7xq0m%fbqswvpuu96xj+_ksf8d4_18px2(53thle0sw65&f@&'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_mysql',
    'rest_framework',
    'rest_framework.authtoken',
    'dry_rest_permissions',
    'silk',
    'drf_yasg',
    'corsheaders',
    'social_django',
    'accounts',
    'currencies',
    'contents',
    'messaging',
    'operations',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.social.middlewares.SocialAuthExceptionMiddleware',
    'silk.middleware.SilkyMiddleware',
]

ROOT_URLCONF = 'apiserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'apiserver.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lineupdb',
        'USER': 'root',
        'PASSWORD': '12345678!9',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
        'HOST': '127.0.0.1',
        'PORT': '23306',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.User'

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'staticfiles')

AUTHENTICATION_BACKENDS = (
    'steemconnect.backends.SteemConnectOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PAGINATION_CLASS': 'apiserver.helpers.rest_framework.paginations.DefaultCursorPaginationClass',
    'PAGE_SIZE': 4,
}

MAX_USER_PROMOTION_CODE_NUMBER = 3

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'uploads')

MEDIA_URL = '/media/'

CORS_ORIGIN_ALLOW_ALL = True  # only for DEBUG mode

# CORS_ORIGIN_WHITELIST = (
#     'line-up.me',
#     'localhost:8080',
#     'localhost:8081',
#     'localhost:8082',
# )

CORS_EXPOSE_HEADERS = [
    'LineUp-Total-Number',
    'LineUp-Page-Next-Link',
    'LineUp-Page-Previous-Link',
]


SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    # 'social_core.pipeline.social_auth.social_user',
    'accounts.social.pipeline.steem.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'accounts.social.pipeline.issue_signup_point',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.debug.debug',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'social_core.pipeline.debug.debug',
    'accounts.social.pipeline.steem.user_info',
)

NICKNAME_LENGTH_RANGE = (2, 50, )

SOCIAL_AUTH_STEEMCONNECT_KEY = 'lineup.app'

SOCIAL_AUTH_STEEMCONNECT_DEFAULT_SCOPE = ['vote', 'comment']

LOGIN_REDIRECT_URL = '/social-auth/login/done/'

STEEMCONNECT_SOCIAL_AUTH_RAISE_EXCEPTIONS = True
SOCIAL_AUTH_RAISE_EXCEPTIONS = True
RAISE_EXCEPTIONS = True
SOCIAL_AUTH_SANITIZE_REDIRECTS = False

FRONT_HOSTNAME = 'http://127.0.0.1:8084'
FRONTEND_LOGIN_REDIRECT_URL = f'{FRONT_HOSTNAME}/social-auth/login/done'
FRONTEND_LOGIN_URL = f'{FRONT_HOSTNAME}/login'

INACTIVE_USER_URL = f'{FRONT_HOSTNAME}/login?status=inactive-user'
LOGIN_ERROR_URL = f'{FRONT_HOSTNAME}/login?status=error'
# SESSION_COOKIE_DOMAIN = "127.0.0.1"

# DEFAULT_USER_LEVEL = 'associate'  # 회원 가입시 기본 등급
DEFAULT_USER_LEVEL = 'author'  # 6월 2일 only 전 한정.

DEFAULT_ASSET_REDIRECT_CACHE = 60 * 60 * 24

CORS_ALLOW_CREDENTIALS = False

CORS_ALLOW_HEADERS = default_headers + (
    'access-control-allow-origin',
    'access-control-allow-credentials',
)

CSRF_TRUSTED_ORIGINS = ['beta.line-up.me', 'www.line-up.me', 'line-up.me']

FILE_UPLOAD_PERMISSIONS = 0o644

SERVICE_ROOT_USERNAME = 'lineup'

SERVICE_TOKEN_SYMBOL = 'lineup'

LIMITATION_POINT_PER_DAY = 1_000

AVAILABLE_DELETION_PERIOD = 7  # days

MINIMUM_IMAGE_SIZE = 500  # px.

# AMAZON S3 settings---------------------------------------------------

AWS_STORAGE_BUCKET_NAME = 'lineup-user-assets'

AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY = None

AWS_REGION = 'ap-northeast-2'
AWS_S3_HOST = f's3-{AWS_REGION}.amazonaws.com'
S3_USE_SIGV4 = True

AWS_S3_FILE_OVERWRITE = False

AWS_S3_KEY_PREFIX = 'uploads'
# DEFAULT_FILE_STORAGE = 'apiserver.storages.aws_s3.MediaStorage'

AWS_S3_URL_EXPIRIATION = 60 * 60 * 24 * 30  # seconds

DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 8

FCM_API_KEY = os.environ['LINEUP_FCM_APIKEY']

# celery settings---------------------------------------------------

CELERY_BROKER_URL = 'redis://localhost:26379/0'

CELERY_RESULT_BACKEND = 'redis://localhost:26379/2'

CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_RESULT_SERIALIZER = 'json'

CELERY_TASK_SERIALIZER = 'json'

CELERY_TIMEZONE = 'Asia/Seoul'

CELERY_BEAT_SCHEDULE = {
}

BEZANT_ENDPOINT = 'testnet'

BEZANT_APIKEY = os.environ.get('BEZANT_APIKEY')

FRONTEND_PATH = os.path.join(
    os.path.dirname(BASE_DIR), 'frontend', 'production-dist',
)
