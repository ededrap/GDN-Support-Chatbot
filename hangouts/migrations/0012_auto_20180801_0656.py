# Generated by Django 2.0.5 on 2018-08-01 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hangouts', '0011_workitemcreated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='work_item',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='hangouts.WorkItem'),
        ),
    ]