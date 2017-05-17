# ！/usr/bin/env python
# -*- coding:utf-8 -*-
# __Author__ Jianer

from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        error_msg = ''
        username = request.POST.get('username')
        password = request.POST.get('password')
        checked = request.POST.get('checked')
        login_user = authenticate(username=username, password=password)
        if login_user:
            login(request, login_user)
            return redirect(request.GET.get('next', '/bossadmin/'))
        else:
            error_msg += '用户名或密码错误'
        return render(request, 'login.html', {'error_msg': error_msg}, )


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/bossadmin/login/')