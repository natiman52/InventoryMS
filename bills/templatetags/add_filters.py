from django import template 
from django.db.models import Q
register = template.library.Library()

@register.filter
def subtract(value,minus):
    return(value - minus)

@register.filter
def get_unit(value):
    total_unit = 0
    for i in value.all():
        total_unit += i.quantity
    return total_unit

@register.filter
def filter_list(value,test):
    print(test)
    return value.filter(dxf_file__contains=test)