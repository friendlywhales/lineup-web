
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.conf import settings

from ... import models as a_models

user_model = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.init_system_accounts()

        for levelname in user_model.perm_group_names._fields:
            group_name = getattr(user_model.perm_group_names, levelname)
            _models = getattr(self, f'get_perms_of_{levelname}_user_group')()
            o, _ = Group.objects.get_or_create(name=group_name)

            perms = []
            for m in _models:
                ct = ContentType.objects.get_for_model(m)
                perms.extend(list(Permission.objects.filter(content_type=ct)))
            o.permissions.clear()
            o.permissions.set(perms)
            self.stdout.write(f'{group_name} is set')

    @staticmethod
    def get_perms_of_associate_user_group():
        from contents import models as c_models
        return (
            a_models.Follower,
            c_models.Collection,
            c_models.PostCollection,
            a_models.Follower,
        )

    @staticmethod
    def get_perms_of_corporate_user_group():
        from contents import models as c_models
        return (
            a_models.Follower,
            c_models.Collection,
            c_models.Post,
            c_models.Attachment,
            c_models.Tag,
            c_models.Comment,
        )

    @staticmethod
    def get_perms_of_regular_user_group():
        from contents import models as c_models
        return (
            a_models.Follower,
            c_models.Collection,
            c_models.PostCollection,
            c_models.Like,
            c_models.Comment,
            a_models.Follower,
        )

    @staticmethod
    def get_perms_of_author_user_group():
        from accounts import models as a_models
        from contents import models as c_models
        return (
            a_models.Follower,
            c_models.Collection,
            c_models.Post,
            c_models.PostCollection,
            c_models.Attachment,
            c_models.Tag,
            c_models.Like,
            c_models.Comment,
            a_models.Follower,
        )

    @staticmethod
    def init_system_accounts():
        names = (
            settings.SERVICE_ROOT_USERNAME,
            'line-up', 'root', 'system', 'admin',
        )
        for name in names:
            o, _ = user_model.objects.get_or_create(username=name)
            o.is_active = False
            o.set_unusable_password()
            o.save()
