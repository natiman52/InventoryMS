# Django core imports
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Authentication and permissions
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import json
# Class-based views
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView
)

# Third-party packages

# Local app imports
from store.models import Item,UserPrint
from bills.models import InventoryMaterial,FreeAssets
from bills.algebra import get_total_paid_value,get_total_unpaid_value
from .models import Customer, Supplier,OverTime,MyUser,Employee

from .forms import (
    CreateUserForm, CustomerForm,
    SupplierForm,ItemPriceForm,changePasswordForm,CreateEmployeeForm
)
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def register(request):
    """
    Handle user registration.
    If the request is POST, process the form data to create a new user.
    Redirect to the login page on successful registration.
    For GET requests, render the registration form.
    """
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user-login')
    else:
        form = CreateUserForm()

    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    """
    Render the user profile page.
    Requires user to be logged in.
    """
    return render(request, 'accounts/profile.html')







class CustomerListView(LoginRequiredMixin, ListView):

    model = Customer
    template_name = 'accounts/accountcustomerlist.html'
    context_object_name = 'items'
    def get_queryset(self):
        model = Customer.objects.all()
        queryset = []
        for i in model:
            queryset.append({
                "client":i,
                'item_no':Item.objects.filter(client=i).count()
            })
        return queryset


class SupplierSellsListView(LoginRequiredMixin, ListView):
    """
    View for listing all customers.

    Requires the user to be logged in. Displays a list of all Customer objects.
    """
    model = Supplier
    template_name = 'accounts/vendorsells.html'
    paginate_by = 10
    context_object_name = 'items'
    def get_queryset(self):
        model = InventoryMaterial.objects.filter(supplier__id=int(self.kwargs['id']))
        return model


class CustomerCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new customer.

    Requires the user to be logged in.
    Provides a form for creating a new Customer object.
    On successful form submission, redirects to the customer list.
    """
    model = Customer
    template_name = 'accounts/customer_form.html'
    form_class = CustomerForm
    success_url = reverse_lazy('customer_list')


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing customer.

    Requires the user to be logged in.
    Provides a form for editing an existing Customer object.
    On successful form submission, redirects to the customer list.
    """
    model = Customer
    template_name = 'accounts/customer_form.html'
    form_class = CustomerForm
    success_url = reverse_lazy('customer_list')


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting a customer.

    Requires the user to be logged in.
    Displays a confirmation page for deleting an existing Customer object.
    On confirmation, deletes the object and redirects to the customer list.
    """
    model = Customer
    template_name = 'accounts/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')

##Account Views
    
class AccountDetailView(LoginRequiredMixin,DetailView,UserPassesTestMixin,UpdateView):
    model = Item
    context_object_name = 'item'
    template_name = 'accounts/accountdetail.html'
    form_class = ItemPriceForm
    pk_url_kwarg = 'id'
    success_url ="/"
    def test_func(self):
        if self.request.user.role == "AT" or self.request.user.role == "AD" or self.request.user.role == "GM":
            return True
        else:
            return False
    def get_context_data(self, **kwargs):
        context = super(AccountDetailView,self).get_context_data(**kwargs)
        if(context['item'].diminsions):
            context['diminsion'] = json.loads(context['item'].diminsions)
        return context
    def post(self, request, *args, **kwargs):
        form = ItemPriceForm(request.POST,request.FILES)
        channel = get_channel_layer()
        item =self.get_object()
        UserPrint.objects.create(user=request.user,item=item)
        if(form.is_valid()):
            item.verif_price = "P"
            item.price =form.cleaned_data.get('price') * item.quantity if item.quantity > 0 else form.cleaned_data.get('price')
            item.save()
            async_to_sync(channel.group_send)('MR',{'type':"send.notification"})
            return redirect(reverse('dashboard'))
        else:
            return super(AccountDetailView,self).post(request,*args,**kwargs)
class AccountOrderList(ListView):
    context_object_name = "items"
    template_name = 'accounts/accountorderlist.html'
    def get_queryset(self):
        obje = Item.objects.filter(verif_price="P")
        return obje
class AccountOrderListFinished(ListView):
    context_object_name = "items"
    template_name = 'accounts/accountorderlist.html'
    def get_queryset(self):
        obje =Item.objects.filter(completed=True)
        return obje
class AccountCustomerOrderList(LoginRequiredMixin,DetailView):
    model = Customer
    context_object_name = 'obj'
    template_name = "accounts/accountcustomerorderlist.html"
    pk_url_kwarg = "id"
    def get_object(self):
        obj = super(AccountCustomerOrderList,self).get_object()
        obje = Item.objects.filter(client=obj)
        total_unpaid = get_total_unpaid_value(obje)
        total_paid = get_total_paid_value(obje)
        total_value = total_paid + total_unpaid
        free_assets = FreeAssets.objects.get(customer=obj)
        return {"client":obj,"order_value":total_value,"unpaid":total_unpaid,"assets":free_assets,"paid":total_paid,"items":obje}

def changepasswordtest(user):
    if(user.is_superuser):
        return True
    else:
        return False
@login_required
@user_passes_test(changepasswordtest)
def changepassword(request):
    form =changePasswordForm()
    if(request.method == "POST"):
        form =changePasswordForm(request.POST)
        if(form.is_valid()):
            user = form.cleaned_data.get('user')
            password = form.cleaned_data.get("password1")
            user.set_password(password)
            user.save()
            return redirect(reverse('user-changepassword'))
        return render(request,'accounts/changepassword.html',{'form':form})
    return render(request,'accounts/changepassword.html',{'form':form})
## End of Account views
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@csrf_exempt
@require_POST
@login_required
def get_customers(request):
    if is_ajax(request) and request.method == 'POST':
        term = request.POST.get('term', '')
        customers = Customer.objects.filter(
            name__icontains=term
        ).values('id', 'name')
        customer_list = list(customers)
        return JsonResponse(customer_list, safe=False)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'accounts/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 10


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'accounts/vendor_form.html'
    success_url = reverse_lazy('vendor-list')


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'accounts/vendor_form.html'
    success_url = reverse_lazy('vendor-list')


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'accounts/vendor_confirm_delete.html'
    success_url = reverse_lazy('vendor-list')

class AllOverTimeDisplay(LoginRequiredMixin,ListView):
    template_name = "accounts/allovertime.html"
    context_object_name = "operators"
    paginate_by = 15
    def get_queryset(self):
        obje =MyUser.objects.filter(role="OP")
        if(self.request.GET.get('date')):
            obje =obje.filter(overtime__date =self.request.GET.get('date'))
        elif(self.request.GET.get('q')):
            obje =obje.filter(username__contains=self.request.GET.get('q'))
        return obje
      
class OverTimeDisplayView(LoginRequiredMixin,ListView):
    template_name = "accounts/overtime.html"
    context_object_name = "overtimes"
    paginate_by = 15
    def get_queryset(self):
        obje =self.request.user.overtime.all()
        if(self.request.GET.get('date')):
            obje =self.request.user.overtime.filter(date=self.request.GET.get('date'))
        return obje
class OverTimeDetailView(LoginRequiredMixin,DetailView):
    model=OverTime
    template_name="accounts/overtimedetail.html"
    context_object_name = 'overtime'
    pk_url_kwarg = 'id'
class EmployeePayRollList(LoginRequiredMixin,UserPassesTestMixin,ListView):
    model= Employee
    template_name = "accounts/stafflist.html"
    context_object_name ="employee"
    def test_func(self):
        """Check if the user has the required permissions."""
        return self.request.user in MyUser.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for item in context['employee']:
            overtime = 0
            if(item.account):
                for i in item.account.overtime.filter(paid=False):
                    for t in i.ammount.all():
                        overtime += t.quantity    
            item.overtime = overtime * 50
            item.total = item.overtime + item.salary
        return context

class CreateEmployee(LoginRequiredMixin,CreateView):
    model=Employee
    form_class = CreateEmployeeForm
    template_name = "accounts/staffcreate.html"
    def get_success_url(self):
        return reverse('payroll')
    