from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def count(row, article_list):
    i = 0
    for item in article_list:
        if item.category == row:
            i += 1

    return i


@register.simple_tag
def tag_count(row, article_list):
    i = 0
    for item in article_list:
        for j in item.tags.all():

            if j.nid == row.nid:

                i += 1

    return i
