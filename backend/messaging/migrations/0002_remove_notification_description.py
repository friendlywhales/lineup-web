# Generated by Django 2.0.3 on 2018-05-12 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='description',
        ),
    ]
