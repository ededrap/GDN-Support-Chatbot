# Generated by Django 2.0.5 on 2018-08-03 07:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hangouts', '0013_auto_20180802_0445'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workitemcreated',
            name='user',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='final',
            new_name='is_finished',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='awt_token',
            new_name='jwt_token',
        ),
        migrations.AddField(
            model_name='user',
            name='last_auth',
            field=models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0)),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='WorkItemCreated',
        ),
    ]