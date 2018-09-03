from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def like(article, username):
    updown_list = article.updown_set.all()
    for item in updown_list:
        if item.user.username == username and item.up == True:
            return True
    return False


@register.filter
def dislike(article, username):
    updown_list = article.updown_set.all()
    for item in updown_list:
        if item.user.username == username and item.down == True:
            return True
    return False

@register.filter
def check_follow(follow_list, nid):

    for item in follow_list:
        if item.nid == nid:
            return True
    return False