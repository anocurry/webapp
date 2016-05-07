# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-07 05:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_auto_20160505_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notif_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 7, 13, 54, 16, 770450)),
        ),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
