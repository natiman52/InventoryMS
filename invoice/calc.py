from django.db.models import Sum
from bills.models import Bill,bill_type

def get_count_of_clients(item):
    unique_count = []
    for i in item:
        if(not i.client in unique_count):
            unique_count.append(i.client)  
    return unique_count

def get_count_of_clients_debt(item):
    unique_count = []
    for i in item:
        if(len(unique_count) > 0):
            count = 0
            test =False
            for d in unique_count:
                if not d['name'] == i.client.name:
                    count += 1
                if count == len(unique_count):
                    test =True
            if(test):
                unique_count.append({'name':i.client.name,'debt':get_count_of_each_client_debt(item,i.client)})
        else:
            unique_count.append({'name':i.client.name,'debt':get_count_of_each_client_debt(item,i.client)})
    return unique_count
def get_count_of_each_client_debt(items,client):
    data = 0
    cancel = False
    for i in items:
        if(cancel):
            return None
        if(i.client == client):
            if(not i.invoice_set.exists()):
                cancel = True
            elif(i.invoice_set.all()[0].quantity != 0 ):
                data += i.invoice_set.all()[0].quantity * i.invoice_set.all()[0].unit_price
            else:
                data += 1 * i.invoice_set.all()[0].unit_price
    return data     

def get_single_client_debt(invoices,client):
    data = 0
    for i in invoices:
        if(i.item.client == client):
            if(i.quantity != 0 ):
                data += i.quantity * i.unit_price
            else:
                data += 1 * i.unit_price
    return data




def get_opertional_cost(date,l=1):
    if(l == 0):
        l = 1
    data = []
    AMMOUNT = 0
    item = Bill.objects.filter(date__date=date,bill_type__in=[x[0] for x in bill_type])
    if(item.exists()):
        pass
    else:
        return False
    for i in item:
        data.append({'name':i.bill_type,"amm":i.amount})
        AMMOUNT += i.amount
    data.append({'name':'total cost/day',"amm":round(AMMOUNT,2)})
    data.append({'name':'operational cost/lamera',"amm":round(AMMOUNT/l,2)})
    return data



def total_opertional_cost(costs):
    data = 0
    for i in costs:
        if(i.get('name') != "total cost/day" and i.get('name') != "operational cost/lamera"):
            data += i.get('amm')
    return data

def get_each_clients_debt(item):
    unique_count = []
    for i in item:
        if(len(unique_count) > 0):
            count = 0
            test =False
            for d in unique_count:
                if not d['name'] == i.item.client.name:
                    count += 1
                if count == len(unique_count):
                    test =True
            if(test):
                unique_count.append({'name':i.item.client.name,'debt':get_single_client_debt(item,i.item.client)})
        else:
            unique_count.append({'name':i.item.client.name,'debt':get_single_client_debt(item,i.item.client)})
    return unique_count


def get_count_of_lamera(item):
    unique_count = []
    total = 0
    for i in item:
        if(len(unique_count) > 0):
            count = 0
            test =False
            for d in unique_count:
                if not d['name'] == i.thickness.name:
                    count += 1
                if count == len(unique_count):
                    test =True
            if(test):
                unique_count.append({'name':i.thickness.name,'quantity':item.filter(thickness=i.thickness).aggregate(amm=Sum('quantity'))})
        else:
            unique_count.append({'name':i.thickness.name,'quantity':item.filter(thickness=i.thickness).aggregate(amm=Sum('quantity'))})
    for i in unique_count:
        total += i.get('quantity').get('amm')
    return unique_count,total


