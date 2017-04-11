#coding:utf-8
from .models import Task,Process,Upload,Daily,Employee,Project
from django.contrib.auth.models import User
from manageerSystem.forms import TaskForm, ProcessForm,UploadFileForm,DailyForm,ProjectForm
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.db import IntegrityError
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from upload import handle_uploaded_file
import json

from django.contrib.auth import views
from django.contrib.auth.decorators import login_required

import hashlib
import time
# Create your views here.

#显示首页
@login_required
def index(request):
    #获取相应信息
    user_id = request.session.get("user_id")
    context = {
        'page_title': '信息汇总',
        'task_number': 0,
        'task_complete': 0,
        'task_complete_percent': 0,
    }
    try:
        task = Employee.objects.get(id=user_id).task_set.all()
        task_number= task.count()
        # 获取已结单的数量,用于计算任务完成率
        task_complete = task.filter(task_status='已结单').count()
        # 用float可以保留小树，round保留小数点2位
        if task_number:
            task_complete_percent = round(float(task_complete) / task_number * 100, 2)
        else:
            task_complete_percent = 0
    except Exception as e:
        print("error=%s"%e)
        return render(request, 'dashboard.html', context)
    else:
        # 将相关参数传递给dashboard页面
        context = {
            'page_title': '信息汇总',
            'task_number': task_number,
            'task_complete': task_complete,
            'task_complete_percent': task_complete_percent,
        }
        return render(request, 'dashboard.html', context)

#任务的列表显示
@login_required
def task_list(request):
    #如果通过GET来获取了相应参数，那么进行查询
    print "-------555555555"
    if request.method == 'GET':
        query = ''
        #建立过滤条件的键值对
        kwargs = {}
        #默认显示处理中的任务
        kwargs['task_status'] = '处理中'
        #用于分页显示的query
        for key, value in request.GET.iteritems():
            #除去token及page的参数
            if key != 'csrfmiddlewaretoken' and key != 'page':
                #如果查询的是与处理过程相关的，那么需要通过外键跳转至process表格
                if key == 'process_content':
                    if value !='':
                        kwargs['process__process_content__contains'] = value
                elif key == 'process_signer':
                    if value !='':
                        kwargs['process__process_signer__contains'] = value
                #定义任务的开始与结束时间
                elif key == 'task_start':
                    if value != '':
                        kwargs['task_signtime__gte'] = value
                elif key == 'task_end':
                    if value != '':
                        kwargs['task_signtime__lte'] = value
                #定义任务的状态
                elif key == 'task_status':
                    if value == U'处理中':
                        kwargs['task_status'] = '处理中'
                    if value == U'已结单':
                        kwargs['task_status'] = '已结单'
                    #如果选择了所有状态，即对任务状态不进行过滤，那么就删除task_status这个键值对
                    if value == U'全部':
                        del kwargs['task_status']
                #其余的则根据提交过来的键值对进行过滤
                else:
                    kwargs[key + '__contains'] = value
                #建立用于分页的query
                query += '&' + key + '=' + value
        #按照登记时间排序
        data = Task.objects.filter(**kwargs).order_by('task_signtime')
    #如果没有GET提交过来的搜索条件，那么默认按照登记时间排序，并只显示处理中的任务
    else:
        print("hhhhhhhhhhhhhhh")
        data = Task.objects.filter(task_status='处理中').order_by('task_signtime')

    print "query=%s"%query
    #进行分页
    data_list, page_range, count, page_nums = pagination(request, data)
    #构建context字典
    context = {
        'data': data_list,
        'page_range': page_range,
        'query': query,
        'count': count,
        'page_nums': page_nums,
        'page_title': '任务处理',
        'sub_title': '任务列表',
    }
    print "-------6666666"
    return render(request,'task_list.html',context)

#任务列表的相关处理函数

#任务列表的增加
def task_add(request):
    #从TaskForm获取相关信息
    form = TaskForm(request.POST or None)
    if form.is_valid():
        #建立一个task实例
        task_ins = Task()
        #通过时间来建立一个任务流水
        task_ins.task_code = str(int(time.time()))
        #获取task的相关信息
        task_ins.task_title = form.cleaned_data.get('task_title')
        task_ins.task_contacts = form.cleaned_data.get('task_contacts')
        #task建立后默认变成处理中的状态
        task_ins.task_status = '处理中'
        #通过登录用户来辨别任务登记人
        task_ins.task_signer = request.user
        #保存task实例
        task_ins.save()
        #通过当前task_id获取task对象，并将其赋给member_task
        member_task = Task.objects.get(id = task_ins.id)
        #获取members集合
        members = form.cleaned_data.get('task_member')
        print "members%s"%members;
        #获取members集合中的member,并将其添加到member_task中,增添相应实施人员
        for member in members:
            member_task.task_member.add(member)

        #通过task_id获取task对象
        process_task = Task.objects.get(id = task_ins.id)
        #建立一个process的实施步骤实例
        process_ins = Process()
        #将process实例与task绑定
        process_ins.task = process_task
        #获取process相关信息
        process_ins.process_content = form.cleaned_data.get('process_content')
        process_ins.process_signer = request.user
        process_ins.save()

        return redirect('task_list')

    context = {
        'form': form,
        'page_title': '任务处理',
        'sub_title': '新建任务',
        "members":Employee.objects.all(),
    }
    return render(request, 'task_add.html',  context)

#任务的编辑
def task_edit(request, pk):
    #获取相关任务实例
    task_ins = get_object_or_404(Task, pk=pk)
    #如果收到了相应的POST提交
    if request.method == 'POST':
        #任务联系人为可编辑选项，并填充原先的任务联系人
        task_ins.task_contacts = request.POST['task_contacts']
        task_ins.save()

        #通过所在task_id获取task对象
        process_task = Task.objects.get(id = task_ins.id)
        #如果获取的实施步骤内容不为空,建立process对象，并增加相关信息
        if request.POST['process_content'].strip(' ') != '':
            process_ins = Process()
            process_ins.task = process_task
            process_ins.process_content = request.POST['process_content'].strip(' ')
            process_ins.process_signer = request.user
            process_ins.save()

        return redirect('task_edit', pk=task_ins.id)

    context = {
        'task': task_ins,
        'user': str(request.user),
        'page_title': '任务处理',
        'sub_title': '编辑任务',
    }
    return render(request, 'task_edit.html', context)

#任务列表的任务删除
def task_delete(request, pk):
    #获取选定的task实例
    task_ins = get_object_or_404(Task, pk=pk)
    #如果接收到了删除的POST提交，则删除相应条目
    if request.method == 'POST':
        try:
            task_ins.delete()
            #删除成功,则data信息为success
            data = 'success'
        except IntegrityError:
            #如因外键问题，或其他问题，删除失败，则报error
            data = 'error'
        #将最后的data值传递至JS页面，进行后续处理,safe是将对象序列化，否则会报TypeError错误
        return JsonResponse(data, safe=False)

#结束任务功能
def task_finish(request, pk):
    #获取任务实例
    task_ins = get_object_or_404(Task,pk=pk)
    #获得该提交
    if request.method == 'POST':
        try:
            #将task的状态置为已结单
            task_ins.task_status = '已结单'
            task_ins.save()
            #在process增加一条记录，标识某人结束了该项任务
            process_task = Task.objects.get(id = task_ins.id)
            process_ins = Process()
            process_ins.task = process_task
            process_ins.process_content = str(request.user) + u'完成了该项任务并结单'
            process_ins.process_signer = request.user
            process_ins.save()
            #返回JSON值,success
            data = 'success'
        except IntegrityError:
            #返回JSON值,error
            data = 'error'
        #通过json形式返回相关数值
        return HttpResponse(json.dumps(data), content_type = "application/json")

#实施步骤的修改
def process_edit(request, pk):
    #获取相应的实施步骤
    process_ins = get_object_or_404(Process, pk=pk)
    #如果收到了POST提交
    if request.method == 'POST':
        #调用process的form
        form = ProcessForm(request.POST)
        if form.is_valid():
            process_ins.process_content = request.POST['process_content'].strip(' ')
            process_ins.process_signtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            process_ins.save()

            return redirect('task_edit', pk=process_ins.task_id)
    #将之前的process内容放入processform
    form = ProcessForm(initial={'process_content': process_ins.process_content})

    #将相应的context值传递到实施步骤修改页面
    context = {
        'id': process_ins.task_id,
        'form': form,
        'page_title': '任务处理',
        'sub_title': '编辑任务',
    }
    return render(request, 'process_edit.html', context)

#实施步骤删除
def process_delete(request, pk):
    #获取相应的实施步骤
    process_ins = get_object_or_404(Process, pk=pk)
    #如果接收到了POST的提交
    if request.method == 'POST':
        try:
            process_ins.delete()
            #删除成功,则data信息为success
            data = 'success'
        except IntegrityError:
            #如因外键问题，或其他问题，删除失败，则报error
            data = 'error'
        #将最后的data值传递至JS页面，进行后续处理,safe是将对象序列化，否则会报TypeError错误
        return JsonResponse(data, safe=False)

#上传附件函数
def upload_file(request, pk):
    #获得一个任务的实例
    task_ins = get_object_or_404(Task, pk=pk)

    #如果获取到了POST的提交
    if request.method == 'POST':
        #获取form表单，request.FILES是存放文件的地方
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            #通过处理上传文件函数来获得返回值
            uf = handle_uploaded_file(request.FILES['file'])

            #获取上传文件的实例，并补充相应信息至数据库中
            upload_ins = Upload()
            #绑定相应的task id
            upload_ins.task_id = task_ins.id
            #记录相应的文件名
            upload_ins.upload_title = uf[0]
            #记录相应的上传路径
            upload_ins.upload_path = uf[1]
            #保存upload的实例
            upload_ins.save()
            return redirect('task_edit', pk=task_ins.id)
    else:
        form = UploadFileForm()

    #构建相应的context，传递至上传文件页面
    context = {
        'form': form,
        'page_title': '任务处理',
        'sub_title': '上传文件',
    }
    return render(request, 'upload.html', context)

#分页函数
def pagination(request, queryset, display_amount=10, after_range_num = 10,before_range_num = 10):
    #按参数分页
    # print "--------333333333333"
    try:
        #从提交来的页面获得page的值
        page = int(request.GET.get("page", 1))
        print("page==%d"%page)
        #如果page值小于1，那么默认为第一页
        if page < 1:
            page = 1
    #若报异常，则page为第一页
    except ValueError:
            page = 1
    #引用Paginator类
    # print("queryset%s"%queryset)
    paginator = Paginator(queryset, display_amount)
    #总计的数据条目
    count = paginator.count
    #合计页数
    num_pages = paginator.num_pages

    try:
        #尝试获得分页列表
        objects = paginator.page(page)
    #如果页数不存在
    except EmptyPage:
        #获得最后一页
        objects = paginator.page(paginator.num_pages)
    #如果不是一个整数
    except PageNotAnInteger:
        #获得第一页
        objects = paginator.page(1)
    #根据参数配置导航显示范围
    temp_range = paginator.page_range

    #如果页面很小
    if (page - before_range_num) <= 0:
        #如果总页面比after_range_num大，那么显示到after_range_num
        if temp_range[-1] > after_range_num:
            page_range = xrange(1, after_range_num+1)
        #否则显示当前页
        else:
            page_range = xrange(1, temp_range[-1]+1)
    #如果页面比较大
    elif (page + after_range_num) > temp_range[-1]:
        #显示到最大页
        page_range = xrange(page-before_range_num,temp_range[-1]+1)
    #否则在before_range_num和after_range_num之间显示
    else:
        page_range = xrange(page-before_range_num+1, page+after_range_num)
    #返回分页相关参数
    # print "--------44444444444"
    return objects, page_range, count, num_pages

#用户登陆选项，所有的函数将会返回一个template_response的实例，用来描绘页面，同时你也可以在return之前增加一些特定的功能
#用户登陆
def login(request):
    #extra_context是一个字典，它将作为context传递给template，这里告诉template成功后跳转的页面将是/index
    if request.method == "POST":
        info_dic = request.POST
        user_name = info_dic.get("username","")
        password = info_dic.get("password", "")
        try:
            user = User.objects.get(username=user_name)
        except Exception as e:
            pass
        else:
            if user.check_password(password):
                try:
                    employee= Employee.objects.get(user=user)
                except Exception as e:
                    print("error%e"%e)
                else:
                    request.session['user_id'] = employee.id
                    request.session['user_name'] = user_name
                    # 把用户的权限存入
                    request.session['user_permissions'] = user.employee.permissions
    template_response = views.login(request, extra_context={'next': '/index/'})
    return template_response


#用户退出
def logout(request):
    #logout_then_login表示退出即跳转至登陆页面，login_url为登陆页面的url地址
    template_response = views.logout_then_login(request,login_url='/login/')
    # 登出清除session
    request.session.clear()
    return template_response


#密码更改
@login_required
def password_change(request):
    #post_change_redirect表示密码成功修改后将跳转的页面.
    template_response = views.password_change(request,post_change_redirect='/index/')
    return template_response

# 工作日报的列表
@login_required #需要登录
def daily_list(request):
    # print "-------1111111"
    # 获取日报
    user_list = []

    def get_daily(user_id):
        data_list = []
        try:
            print("hhhhhhhhhh")
            emplyee = Employee.objects.get(id=user_id)
        except Exception as e:
            print("error%s" % e)
        else:
            permissions = emplyee.permissions
            if permissions == 1:
                data_list = all_daily(info_dic, user_list)
            if permissions == 2:
                print("走这里")
                em_list = emplyee.employee_set.all()
                # em_list.append(emplyee)
                employee_list = list(em_list)
                employee_list.append(emplyee)
                print "em_list%s"%employee_list
                for em in employee_list:
                    data_list += order_daly(info_dic, em, user_list)
            if permissions > 2:
                data_list = order_daly(info_dic, emplyee, user_list)

        return data_list

    def all_daily(info_dic, user_list):
        # 获取所有的日报
        context_list = []
        em_list = Employee.objects.all()  # 获取所有的用户
        for user in em_list:
            try:
                daily_info = order_daly(info_dic, user, user_list)
            except Exception as e:
                print("error%s" % e)
            else:
                context_list += daily_info

    def order_daly(info_dic, user, user_list):
        user_list.append(user)
        start_date = info_dic.get("start_time", False)
        end_date = info_dic.get("end_time", False)
        kwargs = {}
        # 添加查询的条件
        kwargs["daliy_user"] = user.id
        if start_date:
            kwargs["daliy_date__gte"] = start_date
        if  end_date:
            kwargs["daliy_date__lte"] = end_date
        # 排序
        print("查询条件%s" % kwargs)
        if not int(info_dic.get("reverse", False)):
            # print "升序"
            print(Daily.objects.filter(**kwargs).order_by("-id"))
            return Daily.objects.filter(**kwargs).order_by("id")
        else:
            # print "降序"
            print(Daily.objects.filter(**kwargs).order_by("-id"))
            return Daily.objects.filter(**kwargs).order_by("-id")

    # print "-------22222222222"
    # print request.method
    query = ""
    permissions = 3
    info_dic = {}
    data_list = []
    if request.GET:
        print("进入了1")
        info_dic = request.GET
        # print("info_dic_reverse=%s" %info_dic.get("reverse", False))
        user_id = info_dic.get("user_id")
        print("info_dic=%s"%info_dic)
        for key, value in info_dic.iteritems():
            if key != 'csrfmiddlewaretoken' and key != 'page':
                query = '%s&%s=%s'%(query,key, value)
        if info_dic:
            user_id = request.session.get("user_id", "")
            query = "&user_id=%s" % user_id
        data_list = get_daily(user_id)
        print "data_list ==== %s" % data_list
    else:
        print("进入了2")
        user_id = request.session.get("user_id", "")
        print "user_id=%s"%user_id
        query = "&user_id=%s"%user_id
        data_list = get_daily(user_id)
        print "data_list ==== %s" % data_list

    data_list, page_range, count, page_nums = pagination(request, data_list)

    print user_list

    context = {
        "users":user_list,
        "permissions":permissions,
        'query':query,
        'data': data_list,
        'page_range': page_range,
        'count': count,
        'page_nums': page_nums,
        'page_title': '工作日报',
        'sub_title': '日报列表',
    }
    return render(request, 'daily_list.html', context)

@login_required
def daily_add(request):
    # 从TaskForm获取相关信息
    form = DailyForm(request.POST or None)
    status_code = 99
    status_info = "失败"
    is_update= 0
    user_id = request.session.get("user_id")
    daily_id = request.POST.get("daily_id")
    if form.is_valid():
        # 建立一个日报实例
        try:
            daily_ins = Daily.objects.get(id=daily_id)
            is_update = 1
        except Exception as e:
            print "错误=%s"%e
            daily_ins = Daily()
            is_update = 0
        try:
            daily_ins.daliy_title = form.cleaned_data.get('daily_title')
        except Exception as e:
            # 给前端返回错误的信息'
            status_code = 1
            status_info = "请填写任务的标题"
            print("error%s"%e)

        try:
            daily_ins.daliy_profile = form.cleaned_data.get("daily_profile")
        except Exception as e:
            # 给前端返回错误的信息
            status_code = 2
            status_info = "请填写任务的简介"
            print("error%s"%e)

        try:
            daily_ins.daliy_detail = form.cleaned_data.get("daily_detail")
        except Exception as e:
            status_info = "请填写任务详情"
            status_code = 3
            # 给前端返回错误的信息
            print("erroe=%s" % e)

        if not is_update:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            daily_ins.daliy_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        else:
            daily_ins.daliy_change_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        try:
            user_id = int(user_id)
        except Exception as e:
            status_code = 4
            status_info = "提交失败"
            print("erroe = %s" %e)
            # 给前端返回错误的信息
        else:
            try:
                employee = Employee.objects.get(id=user_id)
            except Exception as e:
                status_code = 5
                status_info = "提交失败"
                print("error%e"%e)
            else:
                status_code = 0
                status_info = "成功"
                daily_ins.daliy_user = employee
                daily_ins.daliy_create_name = employee.user.username #把创建者的名字存入
                daily_ins.save()
                print("提交成功")
                return redirect('daily_list') # 重定向到显示日报类型

    # 添加工作日报
    context = {
        "status_code": status_code,
        "status_info":status_info,
        "form":form,
        'page_title': '工作日报',
        'sub_title': '新建日报',
    }

    return render(request, 'daily_add.html', context)


@login_required
def daliy_edit(request):
    """修改工作日报"""
    daliy_get_dic = request.GET
    print(type(daliy_get_dic ))
    print daliy_get_dic
    daliy_id = daliy_get_dic.get("daily_id")
    print daliy_id
    context = {
        'page_title': '工作日报',
        'sub_title': '修改日报',
    }
    try:
        daliy = Daily.objects.get(id=daliy_id)
        daily_user_id = daliy.daliy_user.id
    except Exception as e:
        # 返回错误的信息
        return JsonResponse({'content':"日报不存在", "status":98})
    else:
        print("daily_user_id%s"%daily_user_id)
        context["daily_user_id"] = daily_user_id
        context["daily_title"] = daliy.daliy_title
        context["daily_profile"] = daliy.daliy_profile
        context["daily_detail"] = daliy.daliy_detail
        context["daily_id"] = daliy.id
        # 添加工作日报
        return render(request, 'daily_detail.html', context)


@login_required
def daliy_delete(request, pk):
    print pk
    """删除工作日报"""
    # 获取选定的task实例
    daily_ins = get_object_or_404(Daily, pk=pk)
    # 如果接收到了删除的POST提交，则删除相应条目
    try:
        daily_ins.delete()
        # 删除成功,则data信息为success
        data = 'success'
    except IntegrityError:
        # 如因外键问题，或其他问题，删除失败，则报error
        data = 'error'
    return redirect('daily_list')


@login_required
def project_create(request):
    """创建项目
    1 创建项目
    2 修改项目
    3 完结项目
    """
    # print request.body
    form = ProjectForm(request.POST or None)
    if request.POST and form.is_valid():
        info_dic = request.POST
        # 建立project的实例
        try:
            project_status = int(info_dic.get("project_status"))
            if project_status == 1:
                project_ins = Project()
            else:
                project_ins = Project.objects.get(id=info_dic.get("project_id"))

            if project_status != 3:
                project_ins.project_title = info_dic.get("project_title", "")
                project_ins.project_profile = info_dic.get("project_profile", "")
                project_ins.project_detail = info_dic.get("project_detail", "")
                user_name = request.session.get("user_name")
                if user_name:
                    project_ins.project_creater = user_name

            project_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            if project_status == 1:
                project_ins.progect_createrime = project_time
            if project_status == 2:
                project_ins.progect_change_time = project_time
            if project_status == 3:
                project_ins.progect_finish_time =  project_time
            project_ins.save()

            if project_status != 3:
                member_project = Project.objects.get(id=project_ins.id)
                # 添加人员
                members = form.cleaned_data.get('project_member')
                print("members=%s" % members)
                if members:
                    # 获取members集合中的member
                    for member in members:
                        member_project.project_member.add(member)

        except Exception as e:
            print("error=%s"%e)
        else:
            return redirect('project_list')

    context = {
        'form':form,
        'page_title': '项目',
        'sub_title': '创建项目',
        "members": Employee.objects.all()
    }
    return render(request, 'project_create.html', context)


@login_required
def project_list(request):
    """项目列表"""
    query = ''
    data = []
    if request.method == 'GET':
        #建立过滤条件的键值对
        kwargs = {}
        #默认显示处理中的任务
        kwargs['progect_is_finish'] = 1
        is_reverse = 0
        try:
            # 用于分页显示的query
            for key, value in request.GET.iteritems():
                # 除去token及page的参数
                if key != 'csrfmiddlewaretoken' and key != 'page':
                    if key == "reverse":
                        if int(value) != '':
                            is_reverse = int(value)
                    if key == 'user_id':
                        if value != '':
                            try:
                                emple = Employee.objects.get(id=int(value))
                            except Exception as e:
                                print("error=%s"%e)
                            else:
                                kwargs['project_creater'] = emple.user.username
                    elif key == 'project_start':
                        if value != '':
                                kwargs['progect_createrime__gte'] = value
                    elif key == 'project_end':
                        if value != '':
                            kwargs['progect_createrime__lte'] = value
                    # 定义任务的状态
                    elif key == 'progect_status':
                        print("value=====%s"%value)
                        if int(value) != 0:
                            kwargs['progect_is_finish'] = int(value)
                        else:
                            del kwargs['progect_is_finish']
                    # 建立用于分页的query
                    query += '&' + key + '=' + value
            # 按照登记时间排序
            if not is_reverse:
                data = Project.objects.filter(**kwargs).order_by('progect_createrime')
            else:
                data = Project.objects.filter(**kwargs).order_by('-progect_createrime')
        except Exception as e:
            print("error=%s"%e)
    else:
        print "执行没有通过get的列表"
        data = Task.objects.filter(progect_is_finish=0).order_by('progect_createrime')

    print "query=%s"%query
    #进行分页
    data_list, page_range, count, page_nums = pagination(request, data)
    context = {
        "users": Employee.objects.all(),
        'data': data_list,
        'page_range': page_range,
        'query': query,
        'count': count,
        'page_nums': page_nums,
        'page_title': '项目',
        'sub_title': '项目列表',
    }
    return render(request, 'project_list.html', context)

@login_required
def add_project_worker(request):
    """给项目添加组员"""
    pass

@login_required
def project_detail(request):
    """项目的详情"""
    pass

@login_required
def project_edit(request, pk):
    """编辑项目"""
    # 可以编辑的选项
    project_ins = get_object_or_404(Project, pk=pk)
    # 如果收到了相应的POST提交
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        info_dic = request.POST
        project_status = int(info_dic.get("project_status"))
        if project_status != 3:
            try:
                if project_status != 3:
                    # 给项目添加需求
                    project_ins.project_detail += info_dic.get("project_detail", "")
                    # 添加成员
                    member_project = Project.objects.get(id=project_ins.id)
                    # 添加人员
                    members = form.cleaned_data.get('project_member')
                    print("members=%s" % members)
                    if members:
                        # 获取members集合中的member
                        for member in members:
                            member_project.project_member.add(member)

                # 更改项目的状态
                project_ins.progect_is_finish = project_status
                project_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                if project_status == 2:
                    project_ins.progect_change_time = project_time
                if project_status == 3:
                    project_ins.progect_finish_time = project_time

                project_ins.save()

            except Exception as e:
                print("error=%s"%e)
            else:
                #成功 返回列表页
                return redirect("project_list")

    print("method=%s"%request.GET)
    if request.method == "GET" and request.GET.get("edit"):
        print("走get请求跳转")
        context = {
            "project": project_ins,
            'form': form,
            'page_title': '项目',
            'sub_title': '创建项目',
            "members": Employee.objects.all()
        }
        return render(request, 'project_create.html', context)

    context = {
        'form': form,
        'project': project_ins,
        "users": Employee.objects.all(),
        'page_title': '项目',
        'sub_title': '编辑项目',
    }
    return render(request, 'project_edit.html', context)

@login_required
def project_delete(request, pk):
    """删除项目"""
    print pk
    """删除工作日报"""
    project_ins = get_object_or_404(Project, pk=pk)
    # 如果接收到了删除的POST提交，则删除相应条目
    try:
        project_ins.delete()
        # 删除成功,则data信息为success
        data = 'success'
    except IntegrityError:
        # 如因外键问题，或其他问题，删除失败，则报error
        data = 'error'
    return redirect('project_list')

@login_required
def project_finish(request, pk):
    info_dic = request.GET
    project_ins = get_object_or_404(Project, pk=pk)
    if info_dic:
        try:
            project_status = int(info_dic.get("project_status"))
            project_ins.progect_is_finish = project_status
            project_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            if project_status == 1:
                project_ins.progect_change_time = project_time
            if project_status == 2:
                project_ins.progect_finish_time = project_time
            project_ins.save()
        except Exception as e:
            print("error%s"%e)
        else:
            return redirect('project_list')

    return  redirect("project_edit")
