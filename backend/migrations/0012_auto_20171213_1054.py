# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-13 02:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0011_friendfriend_friendtopic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friendfriend',
            name='time',
        ),
        migrations.AddField(
            model_name='allactivity',
            name='mid',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='users',
            name='token',
            field=models.CharField(default='?', max_length=300),
        ),
    ]
