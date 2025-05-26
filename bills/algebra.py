from .models import Bill,SaleryPayment,InventoryMaterial
from django.utils import timezone
from datetime import timedelta
def clean_tab(items,cash):
    result = cash
    for i in items:
        if(i.price):
            if(result >= i.price):
                result -= i.price
                i.paid = True
                i.save()
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