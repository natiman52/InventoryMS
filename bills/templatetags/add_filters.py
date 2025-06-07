from django import template 
from django.utils import timezone
from bills.algebra import getDateRangeFromWeek
from bills.models import thickness_type
from invoice.models import Invoice
register = template.library.Library()

@register.filter
def strf(value):
    return f"{value}"
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
def get_GET_week(value):
    month = value.GET.get("month")
    if("month" in value.get_full_path()):
        return f"month={month}"
    return ""

@register.filter
def get_GET_day(value):
    week = value.GET.get("week")
    month =value.GET.get("month")
    if("week" in value.get_full_path() and "month" in value.get_full_path()):
        return f"&week={week}&month={month}"
    elif("week" in value.get_full_path()):
        return f"&week={week}"
    elif("month" in value.get_full_path()):
        return f"&month={month}"
    return ""
@register.filter
def get_GET(value):
    week = value.GET.get("week")
    month =value.GET.get("month")
    date =value.GET.get('date')
    if("week" in value.get_full_path() and "month" in value.get_full_path() and "date" in value.get_full_path()):
        return f"&week={week}&month={month}&date={date}"
    if("month" in value.get_full_path() and "week" in value.get_full_path() ):
        return f"&month={month}&week={week}"
    if("month" in value.get_full_path() and "day" in value.get_full_path() ):
        return f"&month={month}&day={date}"
    if("week" in value.get_full_path() and "day" in value.get_full_path() ):
        return f"&week={week}&day={date}"
    elif("month" in value.get_full_path()):
        return f"&month={month}" 
    elif("week" in value.get_full_path()):
        return f"&week={week}"   
    elif("date" in value.get_full_path()):
        return f"&date={date}"
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
@register.filter
def overtime(value):
    non_overtime = value.employee.salary + value.bonus
    overtime_ammount =value.total - non_overtime
    return overtime_ammount 

@register.filter
def decide_pos(value):
    if(value < 0):
        return False
    else:
        return True
@register.filter
def myrange(value):
    lst = []
    for i in range(value,value+5):
        firstdayofweek, lastdayofweek=getDateRangeFromWeek(timezone.datetime.now().year,i)
        lst.append({'weekno':f"{i}",'dates':f'{firstdayofweek.strftime("%b %d")}-{lastdayofweek.strftime("%b %d")}'})
    return lst
@register.filter
def weekno(value):
    return value.weekno

@register.filter
def thickness_name(q):
    for choice in thickness_type:
        if choice[0] == q:
            return choice[1]
    return ''

@register.filter
def get_invoice(value):
    item = Invoice.objects.filter(item=value)
    if(item.exists()):
        return item.first()
    else:
        return value
    
@register.filter
def rounded(value):
    if(value):
        return round(value,2)
    else:
        return value