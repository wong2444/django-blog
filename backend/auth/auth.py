#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
import re


def check_login(func):
    def inner(request, *args, **kwargs):
        if request.session.get('user_info'):
            permission_dict = request.session.get('permission_info')
            for k, v in permission_dict['permission2action_dict'].items():
                print(k)
                print(request.path_info)
                if re.match(k, request.path_info):
                    return func(request, *args, **kwargs)
            return HttpResponse("<alert>權限不夠</alert>")


        else:
            return redirect('/login.html')

    return inner
