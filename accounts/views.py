# Django core imports
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Authentication and permissions
from django.contrib.auth.decorators import login_required
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
from bills.models import InventoryMaterial
from .models import Customer, Supplier,MyUser
from .forms import (
    CreateUserForm, CustomerForm,
    SupplierForm,ItemPriceForm
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
    """
    View for listing all customers.

    Requires the user to be logged in. Displays a list of all Customer objects.
    """
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

class AccountDetailView(LoginRequiredMixin,DetailView,UserPassesTestMixin,UpdateView):
    model = Item
    context_object_name = 'item'
    template_name = 'store/account/accountdetail.html'
    form_class = ItemPriceForm
    pk_url_kwarg = 'id'
    success_url ="/"
    def test_func(self):
        if self.request.user.role == "AT" or self.request.user.role == "AD":
            return True
        else:
            return False
    def get_context_data(self, **kwargs):
        context = super(AccountDetailView,self).get_context_data(**kwargs)
        if(context['item'].diminsions):
            context['diminsion'] = json.loads(context['item'].diminsions)
        return context
    def post(self, request,id, *args, **kwargs):
        channel = get_channel_layer()
        item =self.get_object()
        UserPrint.objects.create(user=request.user,item=item)
        item.verif_price = "P"
        item.save()
        async_to_sync(channel.group_send)('MR',{'type':"send.notification"})
        return super().post(self,request,id,*args,**kwargs)
class AccountOrderList(ListView):
    context_object_name = "items"
    template_name = 'store/account/accountorderlist.html'
    def get_queryset(self):
        obje = []
        current = ''
        prints =UserPrint.objects.filter(user=self.request.user)
        for i in prints:
            try:
                if(i.item.verif_price == "P" and (obje.index(i.item))):
                    current = i.item
            except:
                    if(i.item.verif_price == "P"):
                        obje.append(i.item)
                        current = i.item
        print(obje)
        return obje
class AccountOrderListFinished(ListView):
    context_object_name = "items"
    template_name = 'store/account/accountorderlist.html'
    def get_queryset(self):
        obje = []
        current = ''
        prints =UserPrint.objects.filter(user=self.request.user)
        for i in prints:
            try:
                if(i.item.verif_price == "A" and (obje.index(i.item))):
                    current = i.item
            except:
                    if(i.item.verif_price == "A"):
                        obje.append(i.item)
                        current = i.item
        print(obje)
        return obje
class AccountCustomerOrderList(LoginRequiredMixin,DetailView):
    model = Customer
    context_object_name = 'items'
    template_name = "store/account/accountcustomerorderlist.html"
    pk_url_kwarg = "id"
    def get_object(self):
        obj = super(AccountCustomerOrderList,self).get_object()
        obje = Item.objects.filter(client=obj)
        return obje

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
