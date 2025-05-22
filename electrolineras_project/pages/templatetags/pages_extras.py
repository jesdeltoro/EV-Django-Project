from django import template
from pages.models import Page
from django.core.paginator import Paginator

register = template.Library()

@register.simple_tag
def get_page_list():
    pages = Page.objects.all().order_by('-created')
    return pages

@register.simple_tag
def get_page_count():
    return Page.objects.count()