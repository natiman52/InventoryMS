from .models import Bill,SaleryPayment,InventoryMaterial
from django.utils import timezone
from datetime import timedelta
import calendar
import datetime
def clean_tab(items,cash):
    result = cash
    for i in items:
        if(i.price):
            if(result >= i.price):
                result -= i.price
                i.paid = True
                i.save()
    return result

def get_total_order_value(customer):
    result = 0
    for i in customer:
        result += i.quantity
    return result
def get_total_unpaid_value(customer):
    result = 0
    for i in customer:
        if(i.price):
            if(not i.paid):
                result += i.price
    return result
def get_total_paid_value(customer):
    result = 0
    for i in customer:
        if(i.price):
            if(i.paid):
                result += i.price
    return result

def get_all_expense():
    paid_bills = 0
    unpaid_bills = 0
    for i in Bill.objects.filter(date__year=timezone.now().year):
        if(i.status):
            paid_bills += i.amount
        else:
            unpaid_bills += i.amount
    return [unpaid_bills,paid_bills]

def get_total_salary_paid():
    pay =0
    for i in SaleryPayment.objects.filter(date__year=timezone.now().year):
        pay += i.total
    return pay

def get_material_cost():
    leftover=0
    paid=0
    for i in InventoryMaterial.objects.filter(date__year=timezone.now().year):
        paid += i.advance
        if(i.leftover):
            leftover += i.leftover
    return [paid,leftover]


def getDateRangeFromWeek(p_year,p_week):

    firstdayofweek = datetime.datetime.strptime(f'{p_year}-W{int(p_week )- 1}-1', "%Y-W%W-%w").date()
    lastdayofweek = firstdayofweek + datetime.timedelta(days=6.9)
    return firstdayofweek, lastdayofweek


def get_months_with_their_weeks():
    year = datetime.date.today().year
    list_of_weeks= []
    for i in range(1,13):
        ending_day    = calendar.monthrange(year, i)[1] #get the last day of month
        initial_week  = datetime.date(year, i, 1).isocalendar()[1]
        ending_week   = datetime.date(year, i, ending_day).isocalendar()[1]
        list_of_weeks.append({"num":i
                              ,"month":calendar.month_name[i],"initial_week":initial_week,"ending_week":ending_week})
    return list_of_weeks

def get_days(initial_week):
    year = datetime.date.today().year
    first_day =datetime.datetime.strptime(f'{year}-W{int(initial_week) - 1}-1', "%Y-W%W-%w").date()
    dates =[first_day] 
    for i in range(1,6):
        dates.append(first_day + timedelta(i))
    return dates
def get_weekday():
    today =timezone.now().date()
    my_dates = [today]
    t =0
    for i in range(0,4):
        if((today - timedelta(i+1+t)).weekday() != 6 ):
            my_dates.append(today - timedelta(i+1+t))
        else:
            my_dates.append(today -timedelta(i+2))
            t=1
    return my_dates

def get_yesterday():
    date = timezone.datetime.now() - timedelta(1)
    if(date.weekday() == 6):
        date = date - timedelta(1)
    return date
def comparetoday(date):
    yesterday =timezone.datetime.today() - timedelta(1)
    if(yesterday.strftime("%Y-%m-%d") == timezone.datetime.strptime(date,"%Y-%m-%d").strftime("%Y-%m-%d")):
        return ""
    else:
        return f"?date={date}"