# Generated by Django 3.1.3 on 2020-12-04 08:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0003_auto_20201125_2003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tracker',
            name='tracker_type',
        ),
        migrations.AlterField(
            model_name='record',
            name='date',
            field=models.DateField(default=datetime.date(2020, 12, 4)),
        ),
    ]