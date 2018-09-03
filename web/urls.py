"""EdmureBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from .views import home
from .views import account

urlpatterns = [


    re_path('^all/(?P<article_type_id>\d+).html$', home.index, name='index'),
    path('login.html', account.login),
    path('logout.html', account.logout),
    path('register.html', account.register),
    path('check_code.html', account.check_code),
    re_path('^(?P<site>\w+).html$', home.home),
    re_path('^(?P<site>\w+)/(?P<condition>((tag)|(date)|(category)))/(?P<val>\w+-*\w*).html$', home.filter),
    re_path('^(?P<site>\w+)/(?P<nid>\d+).html$', home.detail),
    re_path('^like/(?P<site>\w+)/(?P<nid>\d+).html$', home.like),
    re_path('^dislike/(?P<site>\w+)/(?P<nid>\d+).html$', home.dislike),
    re_path('unfollow.html$', home.unfollow),
    re_path('follow.html$', home.follow),
    re_path('^get_follower/(?P<site>\w+).html$', home.get_follower),
    re_path('^get_blogger/(?P<site>\w+).html$', home.get_blogger),

    re_path('get_more_comment.html$', home.get_more_comment),
    re_path('get_reply.html$', home.get_reply),
    re_path('reply.html$', home.reply),

    # 舉報系統
    re_path('report.html', home.report),

    path('', home.index),
]
