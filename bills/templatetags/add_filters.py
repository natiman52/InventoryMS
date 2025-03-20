from django import template 
from django.utils import timezone
register = template.library.Library()

@register.filter
def subtract(value,minus):
    return(value - minus)

@register.filter
def get_sort(value):
    sort = value.GET.get("sort")
    q = value.GET.get("q")
    if("sort" in value.get_full_path() and "q" in value.get_full_path()):
        return f"&sort={sort}&q={q}"
    elif("sort" in value.get_full_path()):
        return f"&sort={sort}" 
    elif("q" in value.get_full_path()):
        return f"&q={q}"
    else:
        return ""
@register.filter
def get_page(value):
    page = value.GET.get("page")
    q = value.GET.get("q")
    if("page" in value.get_full_path() and "q" in value.get_full_path()):
        return f"&page={1}&q={q}"
    elif("page" in value.get_full_path()):
        return f"&page={1}" 
    elif("q" in value.get_full_path()):
        return f"&q={q}"
    else:
        return ""
@register.filter
def get_unit(value):
    total_unit = 0
    for i in value.all():
        total_unit += i.quantity
    return total_unit
@register.filter
def date_week(value):
    return int(timezone.datetime.today().isoweekday())
@register.filter
def date_week2(value):
    return str(timezone.datetime.today().isoweekday())

@register.filter
def filter_list(value,test):
    return value.filter(dxf_file__contains=test)