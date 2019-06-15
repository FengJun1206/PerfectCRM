from django.urls import resolve
from django.shortcuts import render, redirect, HttpResponse
from kingadmin.my_primission.permission_list import perm_dic
from django.conf import settings


"""
args: [get/post, 'crm', 'userprofile']
kwargs
"""

def perm_check(*args, **kwargs):
    request = args[0]                       # get/post

    # 反解 url，得到 url_name
    resolve_url_obj = resolve(request.path)     # /kingadmin/crm/userprofile/
    current_url_name = resolve_url_obj.url_name  # 当前url的url_name : table_obj_list
    print('参数：', args, kwargs)      # (<WSGIRequest: GET '/kingadmin/crm/userprofile/'>, 'crm', 'userprofile') {}
    print('---perm:', request.user, request.user.is_authenticated, current_url_name)    # lila@qq.com True table_obj_list
    # match_flag = False
    match_results = [None, ]
    match_key = None

    # 若没有登录，则让其登录
    if request.user.is_authenticated is False:
        return redirect(settings.LOGIN_URL)

    """
    perm_dic = 'crm_table_list': 
    ['table_obj_list', 'GET', [], {},  ],
    """
    for permission_key, permission_val in perm_dic.items():

        # 请求 url_name
        per_url_name = permission_val[0]    # table_obj_list
        # 请求方法
        per_method = permission_val[1]      # GET
        # 请求参数
        perm_args = permission_val[2]       # []
        perm_kwargs = permission_val[3]     # {}

        # 执行 permission_hook.view_my_own_customers
        perm_hook_func = permission_val[4] if len(permission_val) > 4 else None

        if per_url_name == current_url_name:  # 匹配请求当前 url
            if per_method == request.method:  # 匹配请求当前方法
                # if not  perm_args: #if no args defined in perm dic, then set this request to passed perm

                # 逐个匹配参数，看每个参数时候都能对应的上。
                args_matched = False  # for args only
                print('perm_args', perm_args)
                # 匹配 args
                for item in perm_args:
                    request_method_func = getattr(request, per_method)  # request.GET/POST
                    print(request_method_func)
                    if request_method_func.get(item, None):  # request字典中有此参数
                        args_matched = True
                    else:
                        print("arg not match......")
                        args_matched = False
                        break  # 有一个参数不能匹配成功，则判定为假，退出该循环。
                else:  # 当列表为空的时候才走这里
                    args_matched = True

                # 匹配有特定值的参数，# 匹配 kwargs
                kwargs_matched = False
                for k, v in perm_kwargs.items():
                    request_method_func = getattr(request, per_method)
                    arg_val = request_method_func.get(k, None)  # request字典中有此参数
                    print("perm kwargs check:", arg_val, type(arg_val), v, type(v))
                    if arg_val == str(v):  # 匹配上了特定的参数 及对应的 参数值， 比如，需要request 对象里必须有一个叫 user_id=3的参数
                        kwargs_matched = True
                    else:
                        kwargs_matched = False
                        break  # 有一个参数不能匹配成功，则判定为假，退出该循环。
                # 字典为空时
                else:
                    kwargs_matched = True

                # 开始匹配自定义权限钩子函数
                perm_hook_matched = False
                if perm_hook_func:
                    perm_hook_matched = perm_hook_func(request)
                else:
                    perm_hook_matched = True

                match_results = [args_matched, kwargs_matched, perm_hook_matched]
                print("--->match_results ", match_results)
                if all(match_results):  # 都匹配上了
                    match_key = permission_key
                    break

    if all(match_results):
        app_name, *per_name = match_key.split('_')
        print("--->matched ", match_results, match_key)
        print(app_name, *per_name)
        perm_obj = '%s.%s' % (app_name, match_key)
        print("perm str:", perm_obj)

        print('当前用户所有权限', request.user.get_all_permissions())       # {'crm.crm_table_list', 'crm.crm_table_list_view'}
        if request.user.has_perm(perm_obj):
            print('当前用户有此权限')
            return True
        else:
            print('当前用户没有该权限')
            return False

    else:
        print("未匹配到权限项，当前用户无权限")


def check_permission(func):         # table_obj_list = check_permission(table_obj_list)
    def inner(*args, **kwargs):     # args: (<WSGIRequest: GET '/kingadmin/crm/userprofile/'>, 'crm', 'userprofile')  kwagrs: {}
        if not perm_check(*args, **kwargs):
            request = args[0]
            return render(request, 'kingadmin/page_403.html')
        return func(*args, **kwargs)

    return inner
