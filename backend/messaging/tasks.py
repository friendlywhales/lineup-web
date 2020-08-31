
from django.conf import settings
from celery import shared_task
from pyfcm import FCMNotification

from . import models


DEFAULT_NOTIFICATION_BACKGROUND_ICON = 'ic_notification_background'


@shared_task
def push_notification(tokens, title, body=None, data=None, **options):
    notifier = FCMNotification(api_key=settings.FCM_API_KEY)
    result = notifier.notify_multiple_devices(
        registration_ids=tokens,
        message_title=title,
        message_body=body,
        message_icon=DEFAULT_NOTIFICATION_BACKGROUND_ICON,
        data_message=data,
        **options,
    )
    if not result.get('failure'):
        return
    failed_tokens = [
        tokens[i]
        for i, o in enumerate(result.get('results', []))
        if o.get('error')
    ]
    models.NotificationToken.objects.filter(token__in=failed_tokens).delete()
