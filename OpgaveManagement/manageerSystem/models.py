#coding:utf-8

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from  tinymce.models import  HTMLField

#  建立表不能形成一个环 会造成数据的冗余 通过 项目 可以找到 用户 通过 对应的任务

# 项目和用户是多对多的关系

# 任务和用户是多对多的关系

# 用户和日报是一对多的关系

#建立职员模型，这是对内置user表的扩展
class Employee(models.Model):
    #对应User表，建立一对一的模型，目的是更好地扩展而不影响原user表结构
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #定义user的职责
    responsibility = models.CharField(max_length=100,blank=True)
    # 定义user的职位的权限 1 老师 2 项目组长 3 项目组员
    permissions = models.IntegerField(default=5)
    parent = models.ForeignKey('self',null=True,blank=True) # 采用自关联
    def __unicode__(self):
        return self.user.username

#建立任务表
class Task(models.Model):
    #执行的任务和人员关系是多对多的关系
    task_member = models.ManyToManyField(Employee)
    #任务的流水号
    task_code = models.CharField(max_length=30, default='error_code')
    #任务的名称
    task_title = models.CharField(verbose_name='任务名称',max_length=100)
    #任务的联系人
    task_contacts = models.TextField(verbose_name='联系人',blank=True)
    #任务状态
    task_status = models.CharField(verbose_name='处理中',max_length=20,default='处理中')
    #任务登记人
    task_signer = models.CharField(max_length=30,default='system')
    #任务登记时间
    task_signtime = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return self.task_title


#建立实施步骤
class Process(models.Model):
    #与task表格是一对多的关系，依附于task之上
    task = models.ForeignKey(Task)
    #实施步骤内容
    process_content = models.TextField(blank=True)
    #实施步骤登记时间
    process_signtime = models.DateTimeField(auto_now_add=True)
    #实施步骤登记人
    process_signer = models.CharField(max_length=30,default='system')

    def __unicode__(self):
        return self.process_content

#上传附件
class Upload(models.Model):
    #与task表格是一对多的关系，依附于task之上
    task = models.ForeignKey(Task)
    #上传附件名称
    upload_title = models.CharField(max_length=255)
    #上传附件路径
    upload_path = models.CharField(max_length=255)
    #上传附件时间
    upload_signtime = models.DateTimeField(auto_now_add=True,null=True)

    def __unicode__(self):
        return self.upload_title


# 项目
class Project(models.Model):
    """项目"""
    # 项目和用户之间是多对多的关系
    project_member = models.ManyToManyField(Employee)
    # 项目的名称
    project_title = models.CharField(verbose_name='项目名称',max_length=100)
    # 项目的创建人
    project_creater = models.CharField(max_length=30,default='system')
    # 项目的创建时间
    progect_createrime = models.DateTimeField(auto_now_add=True,null=True)
    # 项目的简介
    project_profile = models.TextField()
    # 项目的详情
    project_detail = HTMLField()
    # 项目的完结时间
    progect_finish_time =  models.DateTimeField(auto_now_add=True,null=True)
    # 项目的修改时间
    progect_change_time =  models.DateTimeField(auto_now_add=True,null=True)
    # 项目的状态 0 全部 1 进行中 2 已完结
    progect_is_finish = models.IntegerField(default=1)
    def __unicode__(self):
        return  self.project_title

# 工作日报
class Daily(models.Model):
    # 与user是一对多的关系依附在user之上
    daliy_user = models.ForeignKey(Employee)
    # 创建者的名字
    daliy_create_name = models.CharField(max_length=20)
    # 日报的名称
    daliy_title = models.CharField(max_length=20)
    # 日报的时间
    daliy_date = models.DateTimeField(auto_now_add=True,null=True)
    # 日报的简介
    daliy_profile = models.TextField()
    # 日报的修改时间
    daliy_change_time = models.DateTimeField(auto_now_add=True,null=True)
    # 日报的详情 存储为富文本
    daliy_detail = HTMLField()

    def __unicode__(self):
        return self.daliy_title


