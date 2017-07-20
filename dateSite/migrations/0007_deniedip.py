# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-05-13 23:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dateSite', '0006_inbox_inbactive'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeniedIp',
            fields=[
                ('dipcode', models.AutoField(primary_key=True, serialize=False)),
                ('diprange', models.CharField(max_length=25)),
                ('dipactive', models.BooleanField(verbose_name='Active',default=True))
            ],
            options={
                'managed': True,
                'db_table': 'deniedip',
            },
        ),
    ]