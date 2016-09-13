# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-19 01:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('antarin', '0011_auto_20160718_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfolder',
            name='parentfolder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='parentfoldername', to='antarin.UserFolder'),
        ),
        migrations.AlterField(
            model_name='useruploadedfiles',
            name='folder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='foldername', to='antarin.UserFolder'),
        ),
    ]
