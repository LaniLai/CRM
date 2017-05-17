# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-30 02:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0008_classlist_contract_template'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerinfo',
            name='contact',
            field=models.CharField(max_length=64, unique=True, verbose_name='号码'),
        ),
        migrations.AlterField(
            model_name='studentenrollment',
            name='class_grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repository.ClassList', verbose_name='报名班级'),
        ),
    ]