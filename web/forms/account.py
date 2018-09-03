#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.core.exceptions import ValidationError
from django import forms as django_forms
from django.forms import fields as django_fields
from django.forms import widgets as django_widgets

from repository import models

from .base import BaseForm


class LoginForm(BaseForm, django_forms.Form):
    # username = django_fields.CharField(
    # min_length=6,
    # max_length=20,
    #     error_messages={'required': '用户名不能为空.', 'min_length': "用户名长度不能小于6个字符", 'max_length': "用户名长度不能大于32个字符"}
    # )
    username = django_fields.CharField()

    # password = django_fields.RegexField(
    #     '^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$\%\^\&\*\(\)])[0-9a-zA-Z!@#$\%\^\&\*\(\)]{8,32}$',
    #     min_length=12,
    #     max_length=32,
    #     error_messages={'required': '密码不能为空.',
    #                     'invalid': '密码必须包含数字，字母、特殊字符',
    #                     'min_length': "密码长度不能小于8个字符",
    #                     'max_length': "密码长度不能大于32个字符"}
    # )
    password = django_fields.CharField()
    rmb = django_fields.IntegerField(required=False)

    check_code = django_fields.CharField(
        error_messages={'required': '验证码不能为空.'}
    )

    def clean_check_code(self):
        if self.request.session.get('CheckCode').upper() != self.request.POST.get('check_code').upper():
            raise ValidationError(message='验证码错误', code='invalid')


class RegisterForm(BaseForm, django_forms.Form):
    username = django_fields.CharField(error_messages={"required": "用戶名不能為空"})
    password = django_fields.CharField(error_messages={"required": "密碼不能為空"})
    confirm_pwd = django_fields.CharField(error_messages={"required": "請重覆輸入密碼"})
    email = django_fields.CharField(error_messages={"required": "電郵不能為空"})
    check_code = django_fields.CharField(
        error_messages={'required': '验证码不能为空.'}
    )

    # Create your views here.
    # 自定義方法 clean_字段名
    # 必須有返回值 self.cleaned_data['user']
    # 如果出錯:  raise ValidationError("用戶名已存在")
    def clean_username(self):
        v = self.cleaned_data['username']
        ret = models.UserInfo.objects.filter(username=v).count()
        if ret:
            # 整體錯了
            # 自己的詳細錯誤信息
            raise ValidationError("用戶名已存在")
        return v

    def clean_check_code(self):
        if self.request.session.get('CheckCode').upper() != self.request.POST.get('check_code').upper():
            raise ValidationError(message='验证码错误', code='invalid')

    def clean(self):
        value_dict = self.cleaned_data
        v1 = value_dict.get("password")
        v2 = value_dict.get("confirm_pwd")
        if v1 == v2:
            pass
        else:
            raise ValidationError('密码输入不一致')
        return self.cleaned_data


