# Generated by Django 2.0.3 on 2018-11-30 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0006_auto_20181130_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pointstatus',
            name='point',
            field=models.IntegerField(verbose_name='포인트 현황'),
        ),
    ]