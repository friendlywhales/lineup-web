# Generated by Django 2.0.3 on 2018-05-14 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0001_initial'),
        ('accounts', '0009_auto_20180514_1533'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userpromotioncode',
            unique_together={('user', 'code')},
        ),
    ]
