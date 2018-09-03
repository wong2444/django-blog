#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json

from io import BytesIO
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import redirect
from utils.check_code import create_validate_code
from repository import models
from ..forms.account import LoginForm, RegisterForm
import re


class MenuHelper(object):

    def __init__(self, request, username):
        # 当前请求的request对象
        self.request = request
        # 当前用户名
        self.username = username
        # 获取当前URL
        self.current_url = request.path_info  # /login.html 沒有參數和域名

        # 获取当前用户的所有权限
        self.permission2action_dict = None
        # 获取在菜单中显示的权限
        self.menu_leaf_list = None
        # 获取所有菜单
        self.menu_list = None

        # 取得放到session的資料
        self.session_data()

    def session_data(self):
        permission_dict = self.request.session.get('permission_info')
        if permission_dict:
            self.permission2action_dict = permission_dict['permission2action_dict']
            self.menu_leaf_list = permission_dict['menu_leaf_list']
            self.menu_list = permission_dict['menu_list']
        else:
            # 获取当前用户的角色列表
            role_list = models.Role.objects.filter(user2role__u__username=self.username)

            # 获取当前用户的权限列表（URL+Action）
            # v = [
            #     {'url':'/index.html','code':'GET'},
            #     {'url':'/index.html','code':'POST'},
            #     {'url':'/order.html','code':'PUT'},
            #     {'url':'/order.html','code':'GET'},
            # ]
            # v = {
            #     '/inde.html':['GET']
            # }
            permission2action_list = models.Permission2Action.objects. \
                filter(permission2action2role__r__in=role_list). \
                values('p__pattern', 'a__code').distinct()

            permission2action_dict = {}
            for item in permission2action_list:
                # {'url': '/index.html', 'code': 'GET'},轉為 '/index.html':['GET']
                if item['p__pattern'] in permission2action_dict:
                    permission2action_dict[item['p__pattern']].append(item['a__code'])
                else:
                    permission2action_dict[item['p__pattern']] = [item['a__code'], ]

            # 获取菜单的叶子节点，即：菜单的最后一层应该显示的权限,擊擊跳轉的選項
            # 菜單不能為空
            # 最後一層的菜單
            menu_leaf_list = list(models.Permission2Action.objects. \
                                  filter(permission2action2role__r__in=role_list).exclude(p__menu__isnull=True). \
                                  values('p_id', 'p__url', 'p__caption', 'p__menu', 'p__status').distinct())

            # 获取所有的菜单列表
            menu_list = list(models.Menu.objects.values('id', 'caption', 'parent_id'))

            self.request.session['permission_info'] = {
                'permission2action_dict': permission2action_dict,
                'menu_leaf_list': menu_leaf_list,
                'menu_list': menu_list,
            }

            self.permission2action_list = permission2action_list
            self.menu_leaf_list = menu_leaf_list
            self.menu_list = menu_list

    def menu_data_list(self):

        menu_leaf_dict = {}
        open_leaf_parent_id = None

        # 归并所有的叶子节点,掛載子菜單
        # 權限整理
        for item in self.menu_leaf_list:
            item = {
                'id': item['p_id'],
                'url': item['p__url'],
                'caption': item['p__caption'],
                'parent_id': item['p__menu'],  # 他所屬的菜單
                'child': [],
                'status': item['p__status'],  # 是否显示
                'open': False
            }
            if item['parent_id'] in menu_leaf_dict:
                menu_leaf_dict[item['parent_id']].append(item)
            else:
                menu_leaf_dict[item['parent_id']] = [item, ]

                # 將url視為正則表達式,用match方法匹配
            if re.match(item['url'], self.current_url):
                item['open'] = True
                open_leaf_parent_id = item['parent_id']

        print(
            menu_leaf_dict)  # {4: [{'id': 1, 'url': '^base-info.html$', 'caption': '個人資料', 'parent_id': 4, 'child': [], 'status': False, 'open': False}

        # 获取所有菜单字典
        menu_dict = {}
        for item in self.menu_list:
            item['child'] = []
            item['status'] = False
            item['open'] = False
            menu_dict[item['id']] = item

        # 將叶子节点添加到菜单中
        # 掛襪子,掛的是內存地址
        for k, v in menu_leaf_dict.items():
            # 將叶子节点添加到菜单中
            menu_dict[k]['child'] = v  # k是 menu_leaf_dict的key和 menu_dict的 item id 一樣
            parent_id = k
            # 将后代中有叶子节点的菜单标记为【显示】 status=True
            while parent_id:
                menu_dict[parent_id]['status'] = True
                parent_id = menu_dict[parent_id]['parent_id']

                # 将已经选中的菜单标记为【展开】
        while open_leaf_parent_id:
            menu_dict[open_leaf_parent_id]['open'] = True
            open_leaf_parent_id = menu_dict[open_leaf_parent_id]['parent_id']

        # {1: {'id': 1, 'caption': '文章管理', 'parent_id': None, 'child': [
        #     {'id': 4, 'url': '^article-(?P<article_type_id>\\d+)-(?P<category_id>\\d+).html$', 'caption': '查看文章',
        #      'parent_id'
        #      : 1, 'child': [], 'status': False, 'open': False},
        #     {'id': 5, 'url': '^add-article.html$', 'caption': '增加文章', 'parent_id': 1, 'child': [], 'status': False,
        #      'open': False}, {'id': 6
        #         , 'url': '^edit-article-(?P<nid>\\d+).html$', 'caption': '修改文章', 'parent_id': 1, 'child': [],
        #                       'status': False, 'open': False}, {'id': 7, 'url': '^del-article.html$', 'caption': '
        #                                                         刪除文章', 'parent_id': 1, 'child': [], 'status': False, '
        #                                                         open': False}], 'status': True, 'open': False},
        print(menu_dict)

        # 生成树形结构数据
        result = []
        for row in menu_dict.values():
            if not row['parent_id']:
                result.append(row)
            else:
                menu_dict[row['parent_id']]['child'].append(row)
        # print(result)
        return result

    def menu_content(self, child_list):
        # 遞歸出第二層及之後的節點
        response = ""
        tpl = """
             <div class="item %s">
                <div class="title">%s</div>
                <div class="content">%s</div>
            </div>
            
        """
        for row in child_list:
            if not row['status']:
                continue
            active = ""
            if row['open']:
                active = "active"
            if 'url' in row:
                response += " <a class =\"menu-item\" href=\"%s\" > <i class =\"fa fa-cogs\" aria-hidden=\"true\"></i><span> %s </span></a>" % (
                    row['url'], row['caption'])
            else:
                title = row['caption']
                # 遞歸顯示菜單中所有子節點的內容
                content = self.menu_content(row['child'])
                response += tpl % (active, title, content)
        return response

    def menu_tree(self):

        # 生成目錄的第一層
        response = ""
        tpl = """
        
        """
        for row in self.menu_data_list():
            if not row['status']:
                continue
            active = ""
            if row['open']:
                active = "active"
            # 第一层第一个
            # title = row['caption']
            # 第一层第一个的后代
            # 遞歸顯示菜單中其他子節點的內容
            content = self.menu_content(row['child'])
            # response += tpl % (active, content)
            response += content
        return response

    def actions(self):
        """
        检查当前用户是否对当前URL有权访问，并获取对当前URL有什么权限
        """
        action_list = []
        # 当前所有权限
        # {
        #     '/index.html': ['GET',POST,]
        # }
        for k, v in self.permission2action_dict.items():
            if re.match(k, self.current_url):
                action_list = v  # ['GET',POST,]
                break

        return action_list


def check_code(request):
    """
    验证码
    :param request:
    :return:
    """
    stream = BytesIO()  # 內存文件

    img, code = create_validate_code()  # 生成圖片對象
    img.save(stream, 'PNG')  # 保存圖片到內存中

    request.session['CheckCode'] = code
    print(code)
    # stream.getvalue()將內存的值拿出
    return HttpResponse(stream.getvalue())


def login(request):
    """
    登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        result = {'status': False, 'message': None, 'data': None}
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_info = models.UserInfo.objects. \
                filter(username=username, password=password). \
                values('nid', 'nickname',
                       'username', 'email',
                       'avatar', 'blog__theme',
                       'blog__nid',
                       'blog__site', 'blog__title').first()

            if not user_info:
                # result['message'] = {'__all__': '用户名或密码错误'}
                result['message'] = '用户名或密码错误'
            else:
                result['status'] = True
                request.session['user_info'] = user_info
                obj = MenuHelper(request, user_info['username'])
                request.session['menu_string'] = obj.menu_tree()  # 目錄結構的字符串

                if form.cleaned_data.get('rmb'):  # 拿到是否一個月自動登錄checkbox的值
                    # 設置session的過期時間 單位是秒
                    request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            print(form.errors)
            if 'check_code' in form.errors:
                result['message'] = '验证码错误或者过期'
            else:
                result['message'] = '用户名或密码错误'
        return HttpResponse(json.dumps(result))


def register(request):

    if request.method == 'GET':
        return render(request, 'register.html')

    elif request.method == "POST":
        result = {'status': False, 'message': None, 'data': None}
        form = RegisterForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            title = username + "的博客"
            user = models.UserInfo.objects.create(username=username, password=password, email=email, nickname=username)
            models.Blog.objects.create(title=title, site=username, theme='default', user=user)
            models.User2Role.objects.create(r_id=1, u_id=user.nid)
            result['status'] = True
            # request.session['user_info'] = user

        else:
            error_obj = form.errors.as_json()  # 拿到錯誤信息對象

            result['data'] = error_obj

        return HttpResponse(json.dumps(result))


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    request.session.clear()

    return redirect('/')
