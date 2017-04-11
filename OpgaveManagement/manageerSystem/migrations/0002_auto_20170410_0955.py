# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manageerSystem', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='daily',
            name='daliy_change_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='daily',
            name='daliy_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='progect_change_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='progect_createrime',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='progect_finish_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='progect_is_finish',
            field=models.IntegerField(default=1),
        ),
    ]
