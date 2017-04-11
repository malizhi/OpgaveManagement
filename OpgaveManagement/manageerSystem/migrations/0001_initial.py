# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Daily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('daliy_create_name', models.CharField(max_length=20)),
                ('daliy_title', models.CharField(max_length=20)),
                ('daliy_date', models.DateTimeField(default=False)),
                ('daliy_profile', models.TextField()),
                ('daliy_change_time', models.DateTimeField(default=False)),
                ('daliy_detail', tinymce.models.HTMLField()),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('responsibility', models.CharField(max_length=100, blank=True)),
                ('permissions', models.IntegerField(default=5)),
                ('parent', models.ForeignKey(blank=True, to='manageerSystem.Employee', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('process_content', models.TextField(blank=True)),
                ('process_signtime', models.DateTimeField(auto_now_add=True)),
                ('process_signer', models.CharField(default='system', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_title', models.CharField(max_length=100, verbose_name='\u9879\u76ee\u540d\u79f0')),
                ('project_creater', models.CharField(default='system', max_length=30)),
                ('progect_createrime', models.DateTimeField(auto_now_add=True)),
                ('project_profile', models.TextField()),
                ('project_detail', tinymce.models.HTMLField()),
                ('progect_finish_time', models.DateTimeField(default=False)),
                ('progect_change_time', models.DateTimeField(default=False)),
                ('progect_is_finish', models.BooleanField(default=0)),
                ('project_member', models.ManyToManyField(to='manageerSystem.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_code', models.CharField(default='error_code', max_length=30)),
                ('task_title', models.CharField(max_length=100, verbose_name='\u4efb\u52a1\u540d\u79f0')),
                ('task_contacts', models.TextField(verbose_name='\u8054\u7cfb\u4eba', blank=True)),
                ('task_status', models.CharField(default='\u5904\u7406\u4e2d', max_length=20, verbose_name='\u5904\u7406\u4e2d')),
                ('task_signer', models.CharField(default='system', max_length=30)),
                ('task_signtime', models.DateField(auto_now_add=True)),
                ('task_member', models.ManyToManyField(to='manageerSystem.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_title', models.CharField(max_length=255)),
                ('upload_path', models.CharField(max_length=255)),
                ('upload_signtime', models.DateTimeField(auto_now_add=True, null=True)),
                ('task', models.ForeignKey(to='manageerSystem.Task')),
            ],
        ),
        migrations.AddField(
            model_name='process',
            name='task',
            field=models.ForeignKey(to='manageerSystem.Task'),
        ),
        migrations.AddField(
            model_name='daily',
            name='daliy_user',
            field=models.ForeignKey(to='manageerSystem.Employee'),
        ),
    ]
