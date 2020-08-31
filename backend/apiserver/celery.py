import os
from celery import Celery

if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apiserver.settings_prod')

app = Celery('apiserver')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
