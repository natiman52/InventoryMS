# Django core imports
from typing import Any, Dict
from django.urls import reverse

# Class-based views
from django.views.generic import (
    UpdateView,
    DeleteView,
    DetailView
)
from django.shortcuts import render,redirect
# Authentication and permissions
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Third-party packages
from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin

# Local app imports
from .models import Bill,InventoryMaterial,InventoryPayment
from .tables import BillTable
from .forms import InventoryBillForm,SingleBillForm,InventoryUpdateBillForm
from accounts.models import MyUser



class MaterialListView(LoginRequiredMixin, ExportMixin, SingleTableView):
    """View for listing bills."""
    model = InventoryMaterial
    table_class = BillTable
    template_name = 'bills/material_list.html'
    context_object_name = 'bills'
    paginate_by = 10
    SingleTableView.table_pagination = False


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
     if(user.role == "AT" or user.role == "AD"):
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
                total_price += sub_form2.cleaned_data.get("price") * sub_form2.cleaned_data.get('quantity')
                singleMaterial.append(sub_form2.save(commit=True).id)
        sub_form3 =SingleBillForm(request.POST,prefix='sub_form3')
        if(sub_form3.is_valid()):
                total_price += sub_form3.cleaned_data.get("price") * sub_form3.cleaned_data.get('quantity')
                singleMaterial.append(sub_form3.save(commit=True).id)
        sub_form4 =SingleBillForm(request.POST,prefix='sub_form4')
        if(sub_form4.is_valid()):
                total_price += sub_form4.cleaned_data.get("price") * sub_form4.cleaned_data.get('quantity')
                singleMaterial.append(sub_form4.save(commit=True).id)
        sub_form5 =SingleBillForm(request.POST,prefix='sub_form5')
        if(sub_form5.is_valid()):
                total_price += sub_form5.cleaned_data.get("price") * sub_form5.cleaned_data.get('quantity')
                singleMaterial.append(sub_form5.save(commit=True).id)
        
        # subform ends
        if(form_main.is_valid() and sub_form.is_valid()):
            total_price += sub_form.cleaned_data.get("price") * sub_form.cleaned_data.get('quantity')
            total_price += form_main.cleaned_data.get('minsceus_cost')
            singleMaterial.append(sub_form.save(commit=True).id)
            form_main.instance.user = request.user
            form_main.instance.total_cost =total_price
            form_main.instance.leftover = total_price - int(form_main.cleaned_data.get("advance"))
            obj = form_main.save(commit=True)
            obj.irons.add(*singleMaterial)
            return redirect(reverse('bill_list'))
        return render(request,"bills/materialcreate.html",{"form_main":form_main,'sub_form':sub_form,'sub_form2':sub_form2,'sub_form3':sub_form3,'sub_form4':sub_form4,'sub_form5':sub_form5})

 
    return render(request,"bills/materialcreate.html",{"form_main":form_main,'sub_form':sub_form,'sub_form2':sub_form2,'sub_form3':sub_form3,'sub_form4':sub_form4,'sub_form5':sub_form5})


class BillUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating an existing bill."""
    model = Bill
    template_name = 'bills/billupdate.html'
    fields = [
        'institution_name',
        'phone_number',
        'email',
        'address',
        'description',
        'payment_details',
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
