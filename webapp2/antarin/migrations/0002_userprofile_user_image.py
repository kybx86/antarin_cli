# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-26 01:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('antarin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='user_image',
            field=models.ImageField(blank=True, null=True, upload_to='user_images'),
        ),
    ]
