# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-28 14:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0005_auto_20170428_1921'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerinfo',
            name='id_num',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='customerinfo',
            name='sex',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, '男'), (1, '女')], null=True),
        ),
        migrations.AlterField(
            model_name='studentenrollment',
            name='contract_agreed',
            field=models.BooleanField(default=False, verbose_name='合同是否同意'),
        ),
        migrations.AlterField(
            model_name='studentenrollment',
            name='contract_approved',
            field=models.BooleanField(default=False, verbose_name='是否审核通过'),
        ),
        migrations.AlterField(
            model_name='studentenrollment',
            name='contract_signed_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='签署时间'),
        ),
    ]
