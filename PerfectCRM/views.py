from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout


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
            return redirect(request.GET.get('next', '/'))
        else:
            error_msg = '用户名或密码错误'

    return render(request, 'login.html', {'error_msg': error_msg})


def acc_logout(request):
    """
    登出
    :param request:
    :return:
    """
    logout(request)
    return redirect('login')


