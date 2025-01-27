# Generated by Django 3.1.4 on 2021-01-18 06:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_auto_20210116_2241'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='pause_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='session',
            name='paused_duration',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AlterField(
            model_name='record',
            name='date',
            field=models.DateField(default=datetime.date(2021, 1, 18)),
        ),
    ]
