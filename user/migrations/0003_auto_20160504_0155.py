# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-03 17:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20160430_1226'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_accepted', models.BooleanField(default=False)),
                ('notif_date', models.DateTimeField(auto_now=True)),
                ('message', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='post',
            name='usage',
            field=models.PositiveSmallIntegerField(choices=[(0, 'On hiatus'), (1, 'Least used'), (2, 'Moderately used'), (3, 'Most used')]),
        ),
        migrations.AlterField(
            model_name='post',
            name='vis',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Private'), (1, 'Reserved'), (2, 'Public')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='useBg',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='vis',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Private'), (1, 'Public')]),
        ),
        migrations.AddField(
            model_name='notification',
            name='fromuser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User'),
        ),
        migrations.AddField(
            model_name='notification',
            name='touser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notif_touser', to='user.User'),
        ),
        migrations.AddField(
            model_name='connection',
            name='fromuser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User'),
        ),
        migrations.AddField(
            model_name='connection',
            name='touser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connect_touser', to='user.User'),
        ),
    ]
