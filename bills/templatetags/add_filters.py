from django import template 

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