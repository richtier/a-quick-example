# C8000 (migration-model-import)
# Generated by Django 3.0.6 on 2020-05-18 22:49
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.management import create_contenttypes
from django.db import migrations
from django.db.migrations import RunPython


def add(apps, editor):
    app_config = apps.get_app_config('thesis')
    app_config.models_module = app_config.models_module or True
    create_contenttypes(app_config)
    create_permissions(app_config)

    Group.objects.get(name='student').permissions.all().clear()


def remove(apps, editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0001_initial'),
        ('thesis', '0016_auto_20200518_0102'),
    ]

    operations = [
        RunPython(add, remove)
    ]