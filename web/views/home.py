#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.shortcuts import redirect, HttpResponse
from repository import models
from utils.pagination import Pagination
from django.urls import reverse
from django.db.models import F
import json
import datetime


def index(request, *args, **kwargs):
    """
    博客首页，展示全部博文
    :param request:
    :return:
    """
    # return render(request,'index.html')
    # 获取文章类型
    article_type_list = models.Article.type_choices
    # {},[]
    if kwargs:
        article_type_id = int(kwargs['article_type_id'])
        # 按照別名反向生成URL
        # 有參數時 all/(?P<article_type_id>\d+).html {%url 'index' article_type_id=1%} all/1.html
        # 無參數時 all/(\d+).html{%url 'index' 1%} all/1.html
        # 在 views中使用  有分組時 kwargs={article_type_id:1,}
        # 在 views中使用  無分組時 args=(1,)
        base_url = reverse('index', kwargs=kwargs)  # all/1.html
    else:
        article_type_id = None
        base_url = '/'  # /

    data_count = models.Article.objects.filter(**kwargs).count()

    page_obj = Pagination(request.GET.get('p'), data_count)
    article_list = models.Article.objects.filter(**kwargs).order_by('-nid')[page_obj.start:page_obj.end]
    page_str = page_obj.page_str(base_url)
    article_like_list = models.Article.objects.order_by('-up_count')[0:10]
    article_comment_list = models.Article.objects.order_by('-comment_count')[0:10]
    return render(
        request,
        'index.html',
        {
            'article_list': article_list,
            'article_type_id': article_type_id,  # 文章分類id
            'article_type_list': article_type_list,  # 文章分類的文本
            'page_str': page_str,
            'article_like_list': article_like_list,
            'article_comment_list': article_comment_list,
        }
    )


def home(request, site):
    """
    博主个人首页
    :param request:
    :param site: 博主的网站后缀如：http://xxx.com/wupeiqi.html
    :return:
    """
    blog = models.Blog.objects.filter(site=site).select_related('user').first()

    if not blog:
        return redirect('/')
    tag_list = models.Tag.objects.filter(blog=blog)
    # tag_list = models.Tag.objects.filter(blog_id=blog.nid)
    category_list = models.Category.objects.filter(blog=blog)

    date_list = models.Article.objects.raw(
        'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article where blog_id=%d group by strftime("%%Y-%%m",create_time)' % (
            blog.nid))

    data_count = models.Article.objects.filter(blog=blog).count()
    page_obj = Pagination(request.GET.get('p'), data_count)
    article_list = models.Article.objects.filter(blog=blog).order_by('-nid')[
                   page_obj.start:page_obj.end]
    base_url = "/" + site + ".html"
    page_str = page_obj.page_str(base_url)

    return render(
        request,
        'home.html',
        {
            'blog': blog,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'article_list': article_list,
            'page_str': page_str,
        }
    )


def filter(request, site, condition, val):
    """
    分类显示
    :param request:
    :param site:
    :param condition:
    :param val:
    :return:
    """
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    if not blog:
        return redirect('/')
    tag_list = models.Tag.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog)

    date_list = models.Article.objects.raw(
        'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article where blog_id=%d group by strftime("%%Y-%%m",create_time)' % (
            blog.nid))
    template_name = "home_summary_list.html"

    if condition == 'tag':
        template_name = "home_title_list.html"
        # 使用了Article的多對多字段tags進行查詢
        data_count = models.Article.objects.filter(tags=val, blog=blog).count()
        page_obj = Pagination(request.GET.get('p'), data_count)
        article_list = models.Article.objects.filter(tags=val, blog=blog).order_by('-nid')[
                       page_obj.start:page_obj.end]
        base_url = "/" + site + "/" + condition + "/" + val + ".html"
        page_str = page_obj.page_str(base_url)
    elif condition == 'category':
        data_count = models.Article.objects.filter(category_id=val, blog=blog).count()
        page_obj = Pagination(request.GET.get('p'), data_count)
        article_list = models.Article.objects.filter(category_id=val, blog=blog).order_by('-nid')[
                       page_obj.start:page_obj.end]
        base_url = "/" + site + "/" + condition + "/" + val + ".html"
        page_str = page_obj.page_str(base_url)
    elif condition == 'date':
        # article_list = models.Article.objects.filter(blog=blog).extra(
        # where=['date_format(create_time,"%%Y-%%m")=%s'], params=[val, ]).all()

        data_count = models.Article.objects.filter(blog=blog).extra(
            where=['strftime("%%Y-%%m",create_time)=%s'], params=[val, ]).count()
        page_obj = Pagination(request.GET.get('p'), data_count)
        article_list = models.Article.objects.filter(blog=blog).extra(
            where=['strftime("%%Y-%%m",create_time)=%s'], params=[val, ]).order_by('-nid')[
                       page_obj.start:page_obj.end]
        base_url = "/" + site + "/" + condition + "/" + val + ".html"
        page_str = page_obj.page_str(base_url)
        # select * from tb where blog_id=1 and strftime("%Y-%m",create_time)=2017-01
    else:
        article_list = []

    return render(
        request,
        template_name,
        {
            'blog': blog,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'article_list': article_list,
            'page_str': page_str,
        }
    )


def detail(request, site, nid):
    """
    博文详细页
    :param request:
    :param site:
    :param nid:
    :return:
    """
    blog = models.Blog.objects.filter(site=site).select_related('user').first()
    tag_list = models.Tag.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog)
    # 只取創建時間中的年月:strftime("%Y-%m",create_time)
    # 並以此進行分組 group by strftime("%Y-%m",create_time)
    date_list = models.Article.objects.raw(
        'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article where blog_id=%d group by strftime("%%Y-%%m",create_time)' % (
            blog.nid))

    article = models.Article.objects.filter(blog=blog, nid=nid).select_related('category', 'articledetail').first()
    article.read_count = article.read_count + 1
    article.save()

    data_count = models.Comment.objects.filter(article=article).count()
    # page_obj = Pagination(request.GET.get('p'), data_count)
    comment_list = models.Comment.objects.filter(article=article, reply=None).order_by('-nid')[
                   0:10]
    # base_url = "/" + site + "/" + nid + ".html"
    # page_str = page_obj.page_str(base_url)

    return render(
        request,
        'home_detail.html',
        {
            'blog': blog,
            'article': article,
            'comment_list': comment_list,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            # 'page_str': page_str,
            'data_count': data_count,
        }

    )


def like(request, site, nid):
    """
    博文详细页
    :param request:
    :param site:
    :param nid:
    :return:
    """
    ret = {"error": False, "data": None}
    user_info = request.session.get('user_info', default=None)
    if not user_info:
        ret["error"] = True
        ret["data"] = "請先登入"
        return HttpResponse(json.dumps(ret))

    blog = models.Blog.objects.filter(site=site).first()
    article = models.Article.objects.filter(blog=blog, nid=nid).first()
    user = models.UserInfo.objects.filter(nid=user_info['nid']).first()
    UpDown = models.UpDown.objects.filter(article=article, user=user).first()
    if not UpDown:
        models.UpDown.objects.create(article=article, user=user, up=True, down=False)
        article.up_count = article.up_count + 1
        ret["status"] = True
        article.save()
    elif UpDown.up == True:
        UpDown.delete()
        article.up_count = article.up_count - 1
        ret["status"] = False
        article.save()
        # article.update(up_count=F('up_count') - 1)
    else:
        # UpDown.update(up=True, down=False)
        UpDown.up = True
        if UpDown.down == True:
            UpDown.down = False
            article.down_count = article.down_count - 1
        UpDown.save()
        ret["status"] = True
        article.up_count = article.up_count + 1
        article.save()
        # article.update(up_count=F('up_count') + 1, down_count=F('down_count') - 1)
    ret["data"] = "評價成功"
    ret["up_count"] = article.up_count
    ret["down_count"] = article.down_count
    return HttpResponse(json.dumps(ret))


def dislike(request, site, nid):
    """
    博文详细页
    :param request:
    :param site:
    :param nid:
    :return:
    """
    ret = {"error": False, "data": None}
    user_info = request.session.get('user_info', default=None)
    if not user_info:
        ret["error"] = True
        ret["data"] = "請先登入"
        return HttpResponse(json.dumps(ret))

    blog = models.Blog.objects.filter(site=site).first()
    article = models.Article.objects.filter(blog=blog, nid=nid).first()
    user = models.UserInfo.objects.filter(nid=user_info['nid']).first()
    UpDown = models.UpDown.objects.filter(article=article, user=user).first()
    if not UpDown:
        models.UpDown.objects.create(article=article, user=user, up=False, down=True)
        article.down_count = article.down_count + 1
        ret["status"] = True
        article.save()
    elif UpDown.down == True:
        UpDown.delete()
        article.down_count = article.down_count - 1
        ret["status"] = False
        article.save()
        # article.update(up_count=F('up_count') - 1)
    else:
        # UpDown.update(up=True, down=False)
        UpDown.down = True
        if UpDown.up == True:
            UpDown.up = False
            article.up_count = article.up_count - 1
        UpDown.save()
        ret["status"] = True
        article.down_count = article.down_count + 1
        article.save()
        # article.update(up_count=F('up_count') + 1, down_count=F('down_count') - 1)
    ret["data"] = "評價成功"
    ret["up_count"] = article.up_count
    ret["down_count"] = article.down_count
    return HttpResponse(json.dumps(ret))


def reply(request):
    ret = {"error": False, "data": None}
    article_id = request.POST.get('article')
    user_id = request.POST.get('user')
    comment_id = request.POST.get('comment')
    content = request.POST.get('content')
    article = models.Article.objects.filter(nid=article_id).first()
    article.comment_count = article.comment_count + 1
    article.save()
    user = models.UserInfo.objects.filter(nid=user_id).first()
    if comment_id == "":
        comment = models.Comment.objects.create(article=article, user=user, content=content)
    else:
        comment0 = models.Comment.objects.filter(nid=comment_id).first()
        comment = models.Comment.objects.create(article=article, user=user, content=content, reply=comment0)
    ret['data'] = "評論成功"

    ret['info'] = {"username": comment.user.nickname,
                   "content": comment.content, "comment_id": comment.nid}
    ret['info']['comment_reply'] = False
    if comment.reply:
        ret['info']['comment_reply'] = comment.reply.nid
    return HttpResponse(json.dumps(ret))


def get_reply(request):
    ret = {"error": False, "data": None}
    comment_id = request.POST.get('comment')
    comment_list = models.Comment.objects.filter(reply_id=comment_id).order_by('-nid').values('user__nickname', 'nid',
                                                                                              'create_time', 'content')
    ret["data"] = list(comment_list)
    print(comment_list)
    return HttpResponse(json.dumps(ret, cls=DateEncoder))


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%b %d, %Y, %I:%M %p')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def get_more_comment(request):
    ret = {"error": False, "data": None}
    num = request.POST.get('num')
    num = int(num)
    article_id = request.POST.get('article_id')
    comment_list = models.Comment.objects.filter(article_id=article_id, reply=None).order_by('-nid')[
                   num * 10 + 1:num * 10 + 10]
    ret['data'] = []
    for i in comment_list:
        ret['data'].append(
            {'user__nickname': i.user.nickname, 'nid': i.nid, 'create_time': i.create_time, 'content': i.content,
             'count': i.back.count()})

    ret['info'] = "成功"
    print(comment_list)
    return HttpResponse(json.dumps(ret, cls=DateEncoder))


def follow(request):
    ret = {"error": False, "data": None}
    blog_user_id = request.POST.get('blog_user_id')
    user_id = request.POST.get('user_id')

    models.UserFans.objects.create(follower_id=user_id, user_id=blog_user_id)
    return HttpResponse(json.dumps(ret))


def unfollow(request):
    ret = {"error": False, "data": None}
    blog_user_id = request.POST.get('blog_user_id')
    user_id = request.POST.get('user_id')

    models.UserFans.objects.filter(follower_id=user_id, user_id=blog_user_id).delete()
    return HttpResponse(json.dumps(ret))


def get_follower(request, site):
    blog = models.Blog.objects.filter(site=site).select_related('user').first()

    if not blog:
        return redirect('/')
    tag_list = models.Tag.objects.filter(blog=blog)
    # tag_list = models.Tag.objects.filter(blog_id=blog.nid)
    category_list = models.Category.objects.filter(blog=blog)

    date_list = models.Article.objects.raw(
        'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article where blog_id=%d group by strftime("%%Y-%%m",create_time)' % (
            blog.nid))

    # blog_user_id = request.GET.get('nid')

    # user = models.UserInfo.objects.filter(nid=blog.user.nid).first()
    data_count = blog.user.fans.count()
    page_obj = Pagination(request.GET.get('p'), data_count)
    follower_list = models.UserInfo.objects.filter(nid=blog.user.nid).first().fans.order_by('-nid')[
                    page_obj.start:page_obj.end]
    base_url = "/follower_list/" + site + ".html"
    page_str = page_obj.page_str(base_url)
    return render(
        request,
        'follower_list.html',
        {'blog': blog,
         'tag_list': tag_list,
         'category_list': category_list,
         'date_list': date_list,
         'follower_list': follower_list,
         'page_str': page_str
         }

    )


def get_blogger(request, site):
    blog = models.Blog.objects.filter(site=site).select_related('user').first()

    if not blog:
        return redirect('/')
    tag_list = models.Tag.objects.filter(blog=blog)
    # tag_list = models.Tag.objects.filter(blog_id=blog.nid)
    category_list = models.Category.objects.filter(blog=blog)

    date_list = models.Article.objects.raw(
        'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article where blog_id=%d group by strftime("%%Y-%%m",create_time)' % (
            blog.nid))

    # blog_user_id = request.GET.get('nid')

    # user = models.UserInfo.objects.filter(nid=blog.user.nid).first()
    data_count = blog.user.f.count()
    page_obj = Pagination(request.GET.get('p'), data_count)
    follower_list = models.UserInfo.objects.filter(nid=blog.user.nid).first().f.order_by('-nid')[
                    page_obj.start:page_obj.end]
    base_url = "/blogger_list/" + site + ".html"
    page_str = page_obj.page_str(base_url)
    return render(
        request,
        'follower_list.html',
        {'blog': blog,
         'tag_list': tag_list,
         'category_list': category_list,
         'date_list': date_list,
         'follower_list': follower_list,
         'page_str': page_str
         }

    )


def report(request):
    if request.method == 'GET':
        data = {}
        username = request.GET.get('username')
        data['nickname'] = request.session['user_info']['nickname']
        data['user_id'] = request.session['user_info']['nid']
        data['title'] = request.GET.get('title')
        data['article_id'] = request.GET.get('article_id')
        report_type_list = models.Report.type_choices
        data['report_type_list'] = report_type_list

        blog = models.Blog.objects.filter(site=username).select_related('user').first()
        if not blog:
            return redirect('/')
        tag_list = models.Tag.objects.filter(blog=blog)
        # tag_list = models.Tag.objects.filter(blog_id=blog.nid)
        category_list = models.Category.objects.filter(blog=blog)

        date_list = models.Article.objects.raw(
            'select nid, count(nid) as num,strftime("%%Y-%%m",create_time) as ctime from repository_article where blog_id=%d group by strftime("%%Y-%%m",create_time)' % (
                blog.nid))

        return render(request, 'report.html', {'data': data, 'blog': blog,
                                               'tag_list': tag_list,
                                               'category_list': category_list,
                                               'date_list': date_list, })

    elif request.method == "POST":
        data = {}
        data['title'] = request.POST.get('title')
        data['article_id_id'] = request.POST.get('article_id')
        data['reporter_id'] = request.POST.get('user_id')
        data['report_type'] = request.POST.get('report_type')
        data['detail'] = request.POST.get('detail')
        models.Report.objects.create(**data)
        return render(request, 'index.html',)
