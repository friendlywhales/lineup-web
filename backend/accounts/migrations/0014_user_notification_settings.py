# Generated by Django 2.1.5 on 2019-04-02 13:52

import accounts.models
from django.db import migrations
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20181101_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notification_settings',
            field=django_mysql.models.JSONField(default=accounts.models.default_notification_settings),
        ),
    ]
