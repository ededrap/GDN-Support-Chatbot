# Generated by Django 2.0.5 on 2018-08-02 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hangouts', '0012_auto_20180801_0656'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='awt_token',
            field=models.CharField(max_length=700, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='refresh_token',
            field=models.CharField(max_length=750, null=True),
        ),
    ]
