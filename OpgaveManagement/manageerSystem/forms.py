#coding:utf-8
from django.forms import ModelForm
from django import forms
from .models import *

# 定义TaskForm，但不根据ModelForm来定义
class TaskForm(forms.Form):
    #任务类型的分类
    task_title = forms.CharField(label = '任务名称',max_length = 255)
    #建立联系人，其中的textarea做了规格设定，默认行高为2
    task_contacts = forms.CharField(label = '联系人',widget=forms.Textarea(attrs={'rows': '2'}),required=False)
    #建立一个复选框的实施人员，通过queryset来获取人员列表
    task_member = forms.ModelMultipleChoiceField(label='实施人员',
                                                 queryset=Employee.objects.all(),
                                                 widget=forms.CheckboxSelectMultiple)
    #建立一个处理过程
    process_content = forms.CharField(label = '处理过程',widget=forms.Textarea)


# 建立实施步骤的表单
class ProcessForm(forms.Form):
    process_content = forms.CharField(label = '处理过程',widget=forms.Textarea)


# 立上传附件的FORM
class UploadFileForm(forms.Form):
    #提供一个上传附件的FORM
    file = forms.FileField()


# 建立添加日报的FORM
class DailyForm(forms.Form):
    # 提供一个添加日报的FROM
    # 日报的名称
    daily_title = forms.CharField(label='日报的名称', max_length=255)
    # 日报的简介
    daily_profile = forms.CharField(label='摘要', widget=forms.Textarea(attrs={'rows': '2'}), required=False)
    # 日报的具体的内容
    daily_detail = forms.CharField(label='日报内容', widget=forms.Textarea)

class ProjectForm(forms.Form):
    # 项目和用户之间是多对多的关系
    project_member = forms.ModelMultipleChoiceField(label='实施人员',
                                                 queryset=Employee.objects.all(),
                                                 widget=forms.CheckboxSelectMultiple)
