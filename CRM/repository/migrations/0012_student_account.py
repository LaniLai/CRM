# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-30 16:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0011_customerinfo_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='account',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='repository.UserProfile'),
        ),
    ]