#coding:utf-8
"""OpgaveManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

import manageerSystem.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
   # 富文本
    url(r"^tinymce/$", include("tinymce.urls")),

    url(r'^index/',  manageerSystem.views.index,name= 'index'),

    #用户登陆列表
    #用户登陆
    url(r'login/',  manageerSystem.views.login, name='login'),
    #用户退出
    url(r'logout/',  manageerSystem.views.logout, name='logout'),
    #密码修改
    url(r'password_change/',  manageerSystem.views.password_change, name='password_change'),

    #任务列表
    url(r'^task_list/', manageerSystem.views.task_list, name='task_list'),
    url(r'^task_add/', manageerSystem.views.task_add, name='task_add'),
    url(r'^task_edit/(?P<pk>\d+)/$', manageerSystem.views.task_edit, name='task_edit'),
    url(r'^task_delete/(?P<pk>\d+)/$', manageerSystem.views.task_delete, name='task_delete'),
    url(r'^task_finish/(?P<pk>\d+)/$',manageerSystem.views.task_finish, name='task_finish'),

    #实施步骤
    url(r'^process_edit/(?P<pk>\d+)/$', manageerSystem.views.process_edit, name='process_edit'),
    url(r'^process_delete/(?P<pk>\d+)/$',manageerSystem.views.process_delete, name='process_delete'),

    #上传附件
    url(r'^upload_file/(?P<pk>\d+)/$',  manageerSystem.views.upload_file, name='upload_file'),


    # 工作日报
    url(r"^daily_list/$", manageerSystem.views.daily_list, name="daily_list"),
    # 添加日报
    url(r"^daily_add/$", manageerSystem.views.daily_add, name="daily_add"),
    # 日报详情
    url(r"^daily_detail/$", manageerSystem.views.daliy_edit, name="daily_detail"),
    # 删除日报
    url(r"^daliy_delete/(?P<pk>\d+)/$", manageerSystem.views.daliy_delete, name="daily_delete"),

    # 创建项目
    url(r"^project_create/$", manageerSystem.views.project_create, name="project_create"),
    # 项目列表
    url(r"^project_list/$", manageerSystem.views.project_list, name="project_list"),
    # 项目详情
    url(r"^project_detail/$", manageerSystem.views.project_detail, name="project_detail"),
    # 编辑项目
    url(r"^project_edit/(?P<pk>\d+)/$", manageerSystem.views.project_edit, name="project_edit"),
    # 删除项目
    url(r"^project_delete/(?P<pk>\d+)/$", manageerSystem.views.project_delete, name="project_delete"),
    # 删除项目
    url(r"^project_finish/(?P<pk>\d+)/$", manageerSystem.views.project_finish, name="project_finish"),
]


#在测试环境中，将
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
