# Django core imports
from typing import Any, Dict
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count,Q
from django.db.models.functions import ExtractWeekDay
from django.core.serializers.json import DjangoJSONEncoder

# Class-based views
from django.views.generic import (
    UpdateView,
    DeleteView,
    DetailView,
    ListView,CreateView
)
from django.shortcuts import render,redirect
# Authentication and permissions
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Third-party packages
from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin
from datetime import timedelta
import json
# Local app imports
from .models import Bill,InventoryMaterial,InventoryPayment,Thickness,ClientPayment,SaleryPayment
from .tables import BillTable
from .forms import InventoryBillForm,SingleBillForm,InventoryUpdateBillForm,CreateClientPayment,BillFrom
from accounts.models import MyUser,Employee,Customer
from store.models import Item
from .algebra import get_weekday

class MaterialListView(LoginRequiredMixin, ExportMixin, SingleTableView):
    """View for listing bills."""
    model = InventoryMaterial
    table_class = BillTable
    template_name = 'bills/material_list.html'
    context_object_name = 'bills'
    paginate_by = 10
    SingleTableView.table_pagination = False
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
         context = super().get_context_data(**kwargs)
         context['types'] = Thickness.objects.all()
         return context

class MaterialDetailView(LoginRequiredMixin,DetailView):
    model = InventoryMaterial
    template_name = 'bills/materialdetail.html'
    context_object_name = 'bill'  
    pk_url_kwarg = 'id' 
    def get_context_data(self, **kwargs):
         form = InventoryUpdateBillForm()
         context = super().get_context_data(**kwargs)
         context['payments'] = InventoryPayment.objects.filter(inventory=self.get_object())
         context['form'] = form
         return context
    def post(self,request,*args,**kwargs):
        obj = InventoryMaterial.objects.get(id=self.kwargs['id'])
        if(int(request.POST.get('payment'))):
            if(obj.leftover < int(request.POST.get('payment'))):
                obj.leftover = 0
                obj.advance = obj.total_cost
            else:
                obj.leftover = obj.leftover - int(request.POST.get('payment'))
                obj.advance += int(request.POST.get('payment'))
            obj.save()
            InventoryPayment.objects.create(inventory=self.get_object(),user=request.user,amount=int(request.POST.get('payment')))
            return redirect(reverse('bill_list'))
        else:
            return redirect(reverse('bill-detail',kwargs={id:self.kwargs["id"]}))

def test_func(user):
     if(user.role == "AT" or user.role == "AD" or user.role == "GM"):
          return True
     return False
@login_required
@user_passes_test(test_func)
def material_create_view(request):
    """View for creating a new bill."""
    form_main = InventoryBillForm()
    sub_form = SingleBillForm(prefix='sub_form')
    sub_form2 =SingleBillForm(use_required_attribute=False,prefix='sub_form2')
    sub_form3 =SingleBillForm(use_required_attribute=False,prefix='sub_form3')
    sub_form4 =SingleBillForm(use_required_attribute=False,prefix='sub_form4')
    sub_form5 =SingleBillForm(use_required_attribute=False,prefix='sub_form5')
    if request.method == "POST":
        singleMaterial = []
        total_price = 0
        form_main = InventoryBillForm(request.POST)
        sub_form = SingleBillForm(request.POST,prefix='sub_form')
        sub_form2 =SingleBillForm(request.POST,prefix='sub_form2')
        #sub form begins
        if(sub_form2.is_valid()):
                thickness = sub_form2.cleaned_data.get('thickness')
                thickness.added += int(sub_form2.cleaned_data.get('quantity'))
                thickness.save()
                total_price += sub_form2.cleaned_data.get("price") * sub_form2.cleaned_data.get('quantity')
                singleMaterial.append(sub_form2.save(commit=True).id)
        sub_form3 =SingleBillForm(request.POST,prefix='sub_form3')
        if(sub_form3.is_valid()):
                thickness = sub_form3.cleaned_data.get('thickness')
                thickness.added += int(sub_form3.cleaned_data.get('quantity'))
                thickness.save()
                total_price += sub_form3.cleaned_data.get("price") * sub_form3.cleaned_data.get('quantity')
                singleMaterial.append(sub_form3.save(commit=True).id)
        sub_form4 =SingleBillForm(request.POST,prefix='sub_form4')
        if(sub_form4.is_valid()):
                thickness = sub_form4.cleaned_data.get('thickness')
                thickness.added += int(sub_form4.cleaned_data.get('quantity'))
                thickness.save()
                total_price += sub_form4.cleaned_data.get("price") * sub_form4.cleaned_data.get('quantity')
                singleMaterial.append(sub_form4.save(commit=True).id)
        sub_form5 =SingleBillForm(request.POST,prefix='sub_form5')
        if(sub_form5.is_valid()):
                thickness = sub_form5.cleaned_data.get('thickness')
                thickness.added += int(sub_form5.cleaned_data.get('quantity'))
                thickness.save()
                total_price += sub_form5.cleaned_data.get("price") * sub_form5.cleaned_data.get('quantity')
                singleMaterial.append(sub_form5.save(commit=True).id)
        
        # subform ends
            
        if(form_main.is_valid() and sub_form.is_valid()):
            thickness = sub_form.cleaned_data.get('thickness')
            thickness.added += float(sub_form.cleaned_data.get('quantity'))
            thickness.save()
            total_price += sub_form.cleaned_data.get("price") * sub_form.cleaned_data.get('quantity')
            total_price += form_main.cleaned_data.get('minsceus_cost')
            singleMaterial.append(sub_form.save(commit=True).id)
            form_main.instance.user = request.user
            form_main.instance.total_cost =total_price
            if(form_main.cleaned_data.get("payment_method") != "cash"):
                form_main.instance.leftover = total_price - int(form_main.cleaned_data.get("advance"))
            else:
                 form_main.instance.advance = total_price
            obj = form_main.save(commit=True)
            obj.irons.add(*singleMaterial)
            return redirect(reverse('bill_list'))
        return render(request,"bills/materialcreate.html",{"form_main":form_main,'sub_form':sub_form,'sub_form2':sub_form2,'sub_form3':sub_form3,'sub_form4':sub_form4,'sub_form5':sub_form5})

 
    return render(request,"bills/materialcreate.html",{"form_main":form_main,'sub_form':sub_form,'sub_form2':sub_form2,'sub_form3':sub_form3,'sub_form4':sub_form4,'sub_form5':sub_form5})

class BillListView(LoginRequiredMixin,UserPassesTestMixin,ListView):
    model = Bill
    template_name="bills/expanse.html"
    context_object_name = "bills"
    def test_func(self):
        """Check if the user has the required permissions."""
        return self.request.user in MyUser.objects.all()
class BillCreateView(LoginRequiredMixin,CreateView):
     model =Bill
     template_name = "bills/billcreate.html"
     form_class = BillFrom
     def get_success_url(self):
          return reverse("expanse_list")
class BillUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing bill."""
    model = Bill
    template_name = 'bills/billupdate.html'
    fields = [
        'date',
        'description',
        'amount',
        'status'
    ]

    def test_func(self):
        """Check if the user has the required permissions."""
        return self.request.user in MyUser.objects.all()

    def get_success_url(self):
        """Redirect to the list of bills after a successful update."""
        return reverse('bill_list')


class BillDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a bill."""
    model = Bill
    template_name = 'bills/billdelete.html'

    def test_func(self):
        """Check if the user is a superuser."""
        return self.request.user.is_superuser

    def get_success_url(self):
        """Redirect to the list of bills after successful deletion."""
        return reverse('bill_list')


class ClientPaymentListCreate(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    template_name = 'bills/clientpaymentlistcreate.html'
    paginate_by = 20
    form_class = CreateClientPayment
    def get_success_url(self):
         return reverse("account-customer-order",kwargs={"id":self.kwargs.get('id')})
    def test_func(self):
        return True
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = Customer.objects.get(id=self.kwargs.get('id'))
        queryset = ClientPayment.objects.filter(customer=customer)
        context['payments'] = queryset
        return context
    def get(self, request,*args,**kwargs ):
            if(kwargs.get('id')):
                return super().get(request, *args, **kwargs)
            else:
                return Http404
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.customer = Customer.objects.get(id=self.kwargs.get('id'))
        return super().form_valid(form)

class EmployeePayroll(LoginRequiredMixin,DetailView):
    model = Employee
    template_name= "bills/payroll.html"
    pk_url_kwarg = "id"
    context_object_name = "employee"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj =self.get_object()
        context['payments'] = SaleryPayment.objects.filter(employee=obj)
        context['last_payment'] = SaleryPayment.objects.filter(employee=obj).last()
        overtime = 0
        if(obj.account):
            for i in obj.account.overtime.filter(paid=False):
                for t in i.ammount.all():
                    overtime += t.quantity    
        context['overtime'] = overtime 
        context['total'] =(overtime * 50) + obj.salary
        return context
    def post(self,request,**kwargs):
        bonus = request.POST.get('bonus')
        obj =self.get_object()
        overtime = 0
        if(obj.account):
            for i in obj.account.overtime.filter(paid=False):
                for t in i.ammount.all():
                    overtime += t.quantity  
        if(bonus):
            total = (overtime * 50) + obj.salary + int(bonus)
            payment = SaleryPayment(employee=self.get_object(),bonus=int(bonus),total=total)
            payment.save()
        else:
            obj =self.get_object()
            total = (self.get_context_data()['overtime'] * 50) + obj.salary
            payment = SaleryPayment(employee=self.get_object(),bonus=0,total=total)
            payment.save()            
        return redirect(reverse('payroll',kwargs={'id':obj.id}))
        
def daily_activity(request):
     today =timezone.now()
     item = Item.objects.filter(finish__date=today).count()
     yesterday_items = Item.objects.filter(finish__date=today - timedelta(1)).count()
     print(item ,yesterday_items)
     try:
        percentage_diff = ((item - yesterday_items)/((item + yesterday_items) /2)) * 100
     except:
        percentage_diff = 0
     itemsWeek =Item.objects.filter(completed=True,date__date__gte=get_weekday()[-1],date__date__lte=get_weekday()[0]).annotate(weekday=ExtractWeekDay('date__date')).values('weekday').annotate(count=Count('id')).values('weekday', 'count') 
     return render(request,'bills/daily_activity.html',{'today':item,'yesterday':yesterday_items,'diff':percentage_diff,'itemsweek':json.dumps(list(itemsWeek),cls=DjangoJSONEncoder)})