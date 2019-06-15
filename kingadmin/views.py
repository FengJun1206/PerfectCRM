from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from kingadmin import app_setup
from kingadmin.sites import site
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from kingadmin import form_handle
import json
from django.contrib.auth.decorators import login_required
from kingadmin.my_primission import permissions

app_setup.kingadmin_auto_discover()

# print(site.enabled_admins)
# {'crm': {'userprofile': <kingadmin.admin_base.BaseKingAdmin object at 0x0000011A05645E48>}}


def index(request):
    """首页"""
    print(request.path)
    # obj = request.user
    # print(obj, type(obj))
    # print(obj.role.all())
    # for i in obj.role.all():
    #     print(i.menus.all())
    #     for i1 in i.menus.all():
    #         print(i1.url_name, i1.name)

    return render(request, 'kingadmin/kingadmin.html', {'site': site})


# def sales_dashboard(request):
#     return render(request, 'kingadmin/sales_dashboard.html')


def get_filter_result(request, data_list):
    filter_conditions = {}  # 过滤条件

    # request.GET = <QueryDict: {'source': ['0'], 'contact_type': ['0'], 'consultant': [''], 'status': [''], 'date__gte': ['']}>
    for k, v in request.GET.items():
        # 对分页信息进行特殊处理，直接退出循环
        if k in ['page', '_o', 'q'] :continue
        if v:
            filter_conditions[k] = v

    # print('filter_conditions', filter_conditions)

    return data_list.filter(**filter_conditions), filter_conditions


def get_orderby_result(request, data_list, admin_class):
    """排序"""
    current_ordered_column = {}
    orderby_index = request.GET.get('_o')       # 0、-0


    #  list_display = ['id', 'name', 'source', 'contact_type', 'contact', 'consultant', 'consult_content', 'status', 'date']
    if orderby_index:
        # 根据排序字段索引去 list_display 中取值
        orderby_key = admin_class.list_display[abs(int(orderby_index))]     # abs('0')  orderby_key='id'
        current_ordered_column[orderby_key] = orderby_index     # {'id', '-0'}、{'id': '0'}

        if orderby_index.startswith('-'):       # '-0'.startswith('-') 返回布尔值，判断字符串是否以 - 开头
            orderby_key = '-' + orderby_key     # -id

        return data_list.order_by(orderby_key), current_ordered_column      # data_list.order_by('-id'),  {'id', '-0'}

    else:
        return data_list, current_ordered_column


def get_searched_result(request, data_list, admin_class):
    """搜索"""
    search_key = request.GET.get('q')       # '127'
    if search_key:
        q = Q()
        q.connector = 'OR'

        for search_field in admin_class.search_fields:
            q.children.append(('%s__contains' % search_field, search_key))

        return data_list.filter(q)
    return data_list


@permissions.check_permission
# @login_required     # table_obj_list = check_permission(table_obj_list)
def table_obj_list(request, app_name, model_name):
    """
    从数据库中取出数据，返回给前端展示
    :param request:
    :return:
    """
    admin_class = site.enabled_admins[app_name][model_name]

    if request.method == 'POST':
        # print(request.POST)     # <QueryDict: {'csrfmiddlewaretoken': ['Pj1kMlLHt7JPOgH26OpSQ0yab8XzzGwJs18cKGPZYrk9ueAmSVO8MmYQjT7EO0Wf'],
    #  'action': ['change_status'], 'selected_ids': ['["7","6","5","4","3","2","1"]']}>
        # 选中的 action
        selected_action = request.POST.get('action')
        # 选中的 option 的 value
        selected_ids = json.loads(request.POST.get('selected_ids'))
        if not selected_action:
            if selected_ids:    # 这些选中的数据都要被删除
                admin_class.model.objects.filter(id__in=selected_ids).delete()
        else:
            # 走 action 流程
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids)
            admin_class_func = getattr(admin_class, selected_action)        # selected_action: delete_selected_objs
            res = admin_class_func(request, selected_objs)
            if res:
                return res

    # sites 中把 model_class 赋值给 admin_class，admin_class.model = model_class，
    # 所以   admin_class.model = model_class

    data_list = admin_class.model.objects.all().order_by('-id')

    data_list, filter_conditions = get_filter_result(request, data_list)
    # 赋值操作
    admin_class.filter_conditions = filter_conditions  # {'source': '1', 'contact_type': '2'}

    # 搜索
    data_list = get_searched_result(request, data_list, admin_class)
    admin_class.search_key = request.GET.get('q', '')       # 将 q 的值返回，q=127，并赋值给 input 的 value 属性，使其刷新值还在

    # 排序
    data_list, sorted_column = get_orderby_result(request, data_list, admin_class)

    # 分页交给 define_paginator() 处理
    data_list = define_paginator(request, data_list, admin_class)

    # 分页
    # paginator = Paginator(data_list, admin_class.list_per_page)  # 每页 2 条数据
    #
    # page = request.GET.get('page')
    # try:
    #     data_list = paginator.get_page(page)
    # # 如果 page 不是整数，则返回第一页
    # except PageNotAnInteger:
    #     data_list = paginator.get_page(1)
    # except EmptyPage:
    #     data_list = paginator.get_page(paginator.num_pages)

    return render(request, 'kingadmin/table_obj_list.html',
                  {
                      'data_list': data_list,
                      'model_name': model_name,
                      'app_name': app_name,
                      'admin_class': admin_class,
                      'sorted_column': sorted_column
                  })


def define_paginator(request, data_list, admin_class):
    """分页"""
    paginator = Paginator(data_list, admin_class.list_per_page)  # 每页 2 条数据

    page = request.GET.get('page')
    try:
        data_list = paginator.get_page(page)
    # 如果 page 不是整数，则返回第一页
    except PageNotAnInteger:
        data_list = paginator.get_page(1)
    except EmptyPage:
        data_list = paginator.get_page(paginator.num_pages)

    return data_list


@permissions.check_permission
@login_required
def table_obj_change(request, app_name, model_name, pk):
    """修改"""
    admin_class = site.enabled_admins[app_name][model_name]
    model_form = form_handle.create_dynamic_model_form(admin_class)
    obj = admin_class.model.objects.get(id=pk)

    if request.method == 'GET':
        form_obj = model_form(instance=obj)
    elif request.method == 'POST':
        form_obj = model_form(instance=obj, data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/kingadmin/%s/%s' % (app_name, model_name))

    return render(request, 'kingadmin/table_obj_change.html', locals())


@permissions.check_permission
@login_required
def table_obj_add(request, app_name, model_name):
    """添加"""
    admin_class = site.enabled_admins[app_name][model_name]
    model_form = form_handle.create_dynamic_model_form(admin_class, form_add=True)

    if request.method == 'GET':
        form_obj = model_form()
        print('----', form_obj)
    elif request.method == 'POST':
        form_obj = model_form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/kingadmin/%s/%s' % (app_name, model_name))

    return render(request, 'kingadmin/table_obj_add.html', locals())


@permissions.check_permission
@login_required
def table_obj_delete(request, app_name, model_name, pk):
    """
    删除
    :param app_name:
    :param model_name:
    :param pk:
    :return:
    """
    admin_class = site.enabled_admins[app_name][model_name]

    objs = admin_class.model.objects.get(id=pk)
    print('objs', objs)
    if request.method == "POST":
        objs.delete()
        return redirect("/kingadmin/{app_name}/{model_name}/".format(app_name=app_name, model_name=model_name))
    return render(request, 'kingadmin/table_obj_delete.html', locals())


@permissions.check_permission
def app_manager(request, app_name):
    """Kingadmin app 页面管理"""
    return render(request, 'kingadmin/app_manager.html', {'site': site, 'app_name': app_name})


def acc_login(request):
    """
    登录
    :param request:
    :return:
    """
    error_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Django 自带验证
        auth = authenticate(username=username, password=password)
        if auth:
            print('验证通过!')
            # 登录
            login(request, auth)
            # return redirect(request.GET.get('next', '/kingadmin/'))
            return redirect('/kingadmin/')
        else:
            error_msg = '用户名或密码错误'

    return render(request, 'kingadmin/login.html', {'error_msg': error_msg})


def acc_logout(request):
    """
    登出
    :param request:
    :return:
    """
    logout(request)
    return redirect('/kingadmin/login/')

