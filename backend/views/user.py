#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import json
import uuid
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.db import transaction
from django.urls import reverse

from ..forms.article import ArticleForm
from ..auth.auth import check_login
from repository import models
from utils.pagination import Pagination
from utils.xss import XSSFilter


@check_login
def index(request):
    return render(request, 'backend_index.html', {'menu_string': request.session['menu_string']})


@check_login
def base_info(request):
    """
    博主个人信息
    :param request:
    :return:
    """
    user_info_nid = request.session['user_info']['nid']
    user_info = models.UserInfo.objects.filter(nid=user_info_nid).values('nid', 'nickname',
                                                                         'username', 'email',
                                                                         'avatar', 'blog__theme',
                                                                         'blog__nid',
                                                                         'blog__site', 'blog__title').first()

    return render(request, 'backend_base_info.html',
                  {"user_info": user_info, 'menu_string': request.session['menu_string']})


@check_login
def edit_base_info(request):
    ret = {"error": False, "data": None}
    nid = request.POST.get('nid')
    blog_nid = request.POST.get('blog_nid')
    title = request.POST.get('title')
    theme = request.POST.get('theme')
    nickname = request.POST.get('nickname')

    models.UserInfo.objects.filter(nid=nid).update(nickname=nickname)
    models.Blog.objects.filter(nid=blog_nid).update(title=title, theme=theme)
    return HttpResponse(json.dumps(ret))


@check_login
def upload_avatar(request):
    ret = {'status': False, 'data': None, 'message': None}
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar_img')
        print(file_obj)
        if not file_obj:
            pass
        else:
            file_path = os.path.join('static', 'imgs', 'avatar', file_obj.name)
            f = open(file_path, 'wb')
            for chunk in file_obj.chunks():
                f.write(chunk)
            f.close()
            ret['status'] = True
            ret['data'] = file_path
    user_info_nid = request.session['user_info']['nid']
    models.UserInfo.objects.filter(nid=user_info_nid).update(avatar=file_path)

    return HttpResponse(json.dumps(ret))


@check_login
def category(request):
    """
    博主个人分类管理
    :param request:
    :return:
    """
    blog_id = request.session['user_info']['blog__nid']

    data_count = models.Category.objects.count()
    page = Pagination(request.GET.get('p', 1), data_count)
    result = models.Category.objects.filter(blog_id=blog_id).order_by('-nid').select_related(
        'blog')[page.start:page.end]
    page_str = page.page_str("/category.html")
    article_list = models.Article.objects.filter(blog_id=blog_id)

    return render(request,
                  'backend_category.html',
                  {'result': result,
                   'page_str': page_str,
                   'article_list': article_list,
                   'data_count': data_count,
                   'menu_string': request.session['menu_string'],
                   }

                  )


@check_login
def article(request, *args, **kwargs):
    """
    博主个人文章管理
    :param request:
    :return:
    """
    blog_id = request.session['user_info']['blog__nid']
    condition = {}
    for k, v in kwargs.items():
        if v == '0':
            pass
        else:
            # article_type_id,category_id
            condition[k] = v
    condition['blog_id'] = blog_id
    data_count = models.Article.objects.filter(**condition).count()
    page = Pagination(request.GET.get('p', 1), data_count)
    result = models.Article.objects.filter(**condition).order_by('-nid').only('nid', 'title', 'blog').select_related(
        'blog')[page.start:page.end]
    page_str = page.page_str(reverse('article', kwargs=kwargs))
    category_list = models.Category.objects.filter(blog_id=blog_id).values('nid', 'title')
    type_list = map(lambda item: {'nid': item[0], 'title': item[1]}, models.Article.type_choices)
    kwargs['p'] = page.current_page
    return render(request,
                  'backend_article.html',
                  {'result': result,
                   'page_str': page_str,
                   'category_list': category_list,
                   'type_list': type_list,
                   'arg_dict': kwargs,
                   'data_count': data_count,
                   'menu_string': request.session['menu_string'],
                   }
                  )


@check_login
def add_article(request):
    """
    添加文章
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = ArticleForm(request=request)
        return render(request, 'backend_add_article.html',
                      {'form': form, 'menu_string': request.session['menu_string']})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                tags = form.cleaned_data.pop('tags')
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process(content)
                form.cleaned_data['blog_id'] = request.session['user_info']['blog__nid']
                obj = models.Article.objects.create(**form.cleaned_data)
                models.ArticleDetail.objects.create(content=content, article=obj)
                tag_list = []
                for tag_id in tags:
                    tag_id = int(tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)

            return redirect('/backend/article-0-0.html')
        else:
            return render(request, 'backend_add_article.html',
                          {'form': form, 'menu_string': request.session['menu_string']})
    else:
        return redirect('/')


@check_login
def edit_article(request, nid):
    """
    编辑文章
    :param request:
    :return:
    """
    blog_id = request.session['user_info']['blog__nid']
    if request.method == 'GET':
        obj = models.Article.objects.filter(nid=nid).first()
        if not obj:
            return render(request, 'backend_no_article.html')
        tags = obj.tags.values_list('nid')  # <QuerySet [(1,)]>

        if tags:
            tags = list(zip(*tags))[0]  # (1,)
        init_dict = {
            'nid': obj.nid,
            'title': obj.title,
            'summary': obj.summary,
            'category_id': obj.category_id,
            'article_type_id': obj.article_type_id,
            'content': obj.articledetail.content,
            'tags': tags
        }
        form = ArticleForm(request=request, data=init_dict)
        return render(request, 'backend_edit_article.html',
                      {'form': form, 'nid': nid, 'menu_string': request.session['menu_string']})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():
            obj = models.Article.objects.filter(nid=nid, blog_id=blog_id).first()
            if not obj:
                return render(request, 'backend_no_article.html')
            with transaction.atomic():
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process(content)
                tags = form.cleaned_data.pop('tags')
                models.Article.objects.filter(nid=obj.nid).update(**form.cleaned_data)
                models.ArticleDetail.objects.filter(article=obj).update(content=content)
                models.Article2Tag.objects.filter(article=obj).delete()
                tag_list = []
                for tag_id in tags:
                    tag_id = int(tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))

                models.Article2Tag.objects.bulk_create(tag_list)
            return redirect('/backend/article-0-0.html')
        else:
            return render(request, 'backend_edit_article.html',
                          {'form': form, 'nid': nid, 'menu_string': request.session['menu_string']})


@check_login
def del_article(request):
    ret = {"error": False, "data": None}
    nid = request.POST.get('nid')
    models.Article.objects.filter(nid=nid).delete()

    return HttpResponse(json.dumps(ret))


@check_login
def add_category(request):
    blog_id = request.session['user_info']['blog__nid']
    ret = {"error": False, "data": None}
    title = request.POST.get('title')
    category = models.Category.objects.create(title=title, blog_id=blog_id)
    val = models.Category.objects.filter(nid=category.nid).values("nid", "title")
    ret['data'] = list(val)
    return HttpResponse(json.dumps(ret))


@check_login
def edit_category(request):
    ret = {"error": False, "data": None}
    nid = request.POST.get('nid')
    title = request.POST.get('title')
    models.Category.objects.filter(nid=nid).update(title=title)

    return HttpResponse(json.dumps(ret))


@check_login
def del_category(request):
    ret = {"error": False, "data": None}
    nid = request.POST.get('nid')
    models.Category.objects.filter(nid=nid).delete()

    return HttpResponse(json.dumps(ret))


@check_login
def tag(request):
    blog_id = request.session['user_info']['blog__nid']

    data_count = models.Category.objects.count()
    page = Pagination(request.GET.get('p', 1), data_count)
    result = models.Tag.objects.filter(blog_id=blog_id).order_by('-nid').select_related(
        'blog')[page.start:page.end]
    page_str = page.page_str("/tag.html")
    article_list = models.Article.objects.filter(blog_id=blog_id)

    return render(request,
                  'backend_tag.html',
                  {'result': result,
                   'page_str': page_str,
                   'article_list': article_list,
                   'data_count': data_count,
                   'menu_string': request.session['menu_string']
                   }
                  )


@check_login
def add_tag(request):
    blog_id = request.session['user_info']['blog__nid']
    ret = {"error": False, "data": None}
    title = request.POST.get('title')
    tag = models.Tag.objects.create(title=title, blog_id=blog_id)
    val = models.Tag.objects.filter(nid=tag.nid).values("nid", "title")
    ret['data'] = list(val)
    return HttpResponse(json.dumps(ret))


@check_login
def edit_tag(request):
    ret = {"error": False, "data": None}
    nid = request.POST.get('nid')
    title = request.POST.get('title')
    models.Tag.objects.filter(nid=nid).update(title=title)

    return HttpResponse(json.dumps(ret))


@check_login
def del_tag(request):
    ret = {"error": False, "data": None}
    nid = request.POST.get('nid')
    models.Tag.objects.filter(nid=nid).delete()

    return HttpResponse(json.dumps(ret))

@check_login
def report(request):
    if request.method == 'GET':

        data_count = models.Report.objects.count()
        page = Pagination(request.GET.get('p', 1), data_count)
        result = models.Report.objects.order_by('-id').select_related(
            'article_id', )[page.start:page.end]
        page_str = page.page_str("/report.html")

        return render(request,
                      'backend_report.html',
                      {'result': result,
                       'page_str': page_str,

                       'data_count': data_count,
                       'menu_string': request.session['menu_string'],
                       }

                      )



@check_login
def edit_report(request, id):
    if request.method == 'GET':
        obj = models.Report.objects.filter(id=id).first()
        if not obj:
            return render(request, 'backend_no_article.html')

        data = {
            'id': obj.id,
            'title': obj.title,
            'status_choices_list': obj.status_choices,
            'report_status': obj.report_status,
            'type_choices_list': obj.type_choices,
            'report_type': obj.report_type,
            'reporter': obj.reporter,
            'article_id': obj.article_id,
            'detail': obj.detail
        }

        return render(request, 'backend_edit_report.html',
                      {'data': data, 'menu_string': request.session['menu_string']})
    elif request.method == 'POST':
        id = request.POST.get('id')
        data = {}
        data['title']=request.POST.get('title')
        data['report_status'] = request.POST.get('report_status')
        data['report_type'] = request.POST.get('report_type')
        data['article_id_id'] = request.POST.get('article_id')
        data['reporter_id'] = request.POST.get('reporter_id')
        data['title'] = request.POST.get('title')
        data['detail'] = request.POST.get('detail')
        models.Report.objects.filter(id=id).update(**data)
        return redirect('/backend/report.html')
