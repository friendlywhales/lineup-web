
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


user_model = get_user_model()


@receiver(post_save, sender=user_model)
def update_user_perm_group(sender, **kwargs):
    instance = kwargs['instance']
    instance.update_model_permissions()


@receiver(post_save, sender=user_model)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created and instance:
        Token.objects.create(user=instance)
