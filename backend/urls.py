from django.urls import path, re_path
from django.conf.urls import include
from .views import user
from .views import trouble

urlpatterns = [
    re_path('^index.html$', user.index),
    re_path('^base-info.html$', user.base_info),
    re_path('^tag.html$', user.tag),
    re_path('^category.html$', user.category),
    re_path('^article-(?P<article_type_id>\d+)-(?P<category_id>\d+).html$', user.article, name='article'),
    re_path('^add-article.html$', user.add_article),
    re_path('^edit-article-(?P<nid>\d+).html$', user.edit_article),
    re_path('^del-article.html$', user.del_article),
    re_path('^add-category.html$', user.add_category),
    re_path('^edit-category.html$', user.edit_category),
    re_path('^del-category.html$', user.del_category),
    re_path('^add-tag.html$', user.add_tag),
    re_path('^edit-tag.html$', user.edit_tag),
    re_path('^del-tag.html$', user.del_tag),
    re_path('^edit-info.html$', user.edit_base_info),
    re_path('^upload-avatar.html$', user.upload_avatar),

    # 舉報系統
    re_path('report.html', user.report),
    re_path('^edit-report-(?P<id>\d+).html$', user.edit_report),

    # 一般用户： 提交报障单,查看，修改（未处理），评分（处理完成，未评分）
    re_path('^trouble-list.html$', trouble.trouble_list),
    re_path('^trouble-create.html$', trouble.trouble_create),
    re_path('^trouble-edit-(\d+).html$', trouble.trouble_edit),

    re_path('^trouble-kill-list.html$', trouble.trouble_kill_list),
    re_path('^trouble-kill-(\d+).html$', trouble.trouble_kill),
    re_path('^trouble-report.html$', trouble.trouble_report),
    re_path('^trouble-json-report.html$', trouble.trouble_json_report),
]
