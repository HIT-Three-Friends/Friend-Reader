# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-14 15:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='upload'),
        ),
    ]
