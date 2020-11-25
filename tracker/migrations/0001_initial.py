# Generated by Django 3.1.3 on 2020-11-22 23:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tracker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('tracker_type', models.CharField(choices=[('H', 'Hhours Spent'), ('B', 'Boolean')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('num_hours', models.IntegerField()),
                ('tracker', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='tracker.tracker')),
            ],
        ),
    ]
