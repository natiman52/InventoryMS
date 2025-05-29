# Django core imports
from typing import Any
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils import timezone
# Authentication and permissions
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Class-based views
from django.views.generic import (
    DetailView, CreateView, UpdateView, DeleteView,ListView
)

# Third-party packages
from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin
# Local app imports
from .models import Invoice
from .tables import InvoiceTable
from store.models import Item
from bills.algebra import get_months_with_their_weeks,get_days,get_yesterday,comparetoday
from .calc import get_count_of_clients,get_count_of_lamera,get_opertional_cost,get_each_clients_debt,getstatus
from bills.models import Bill
class InvoiceListView(LoginRequiredMixin, ExportMixin, SingleTableView):
    """
    View for listing invoices with table export functionality.
    """
    model = Invoice
    table_class = InvoiceTable
    template_name = 'invoice/invoicelist.html'
    context_object_name = 'invoices'
    paginate_by = 10
    table_pagination = False  # Disable table pagination
    def get_queryset(self,**kwargs):
        if(self.request.GET.get('month')):
            week =get_months_with_their_weeks()[int(self.request.GET.get('month')) - 1].get('initial_week')
        else:
            week = get_months_with_their_weeks()[0].get('initial_week')
        if(self.request.GET.get('week')):
            day =get_days(int(self.request.GET.get('week')))[0]
        else:
            day =get_days(week)[0]
        invoice = Invoice.objects.all()
        if(self.request.GET.get('date')):
            invoice =invoice.filter(item__date__date=self.request.GET.get('date'))
        else:
            invoice = invoice.filter(item__date__date=day)
        return invoice
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        weeks =get_months_with_their_weeks()
        context['weeks'] = weeks
        week = weeks[0].get('initial_week')
        context['clients'] =get_each_clients_debt(self.get_queryset(**kwargs))
        if(self.request.GET.get('month')):
            week =weeks[int(self.request.GET.get('month')) - 1].get('initial_week')
            context['week'] = weeks[int(self.request.GET.get('month')) - 1].get('initial_week')
        else:
            context['week'] = weeks[0].get('initial_week')
        if(self.request.GET.get('week')):
            context['days'] =get_days(int(self.request.GET.get('week')))
        else:
            context['days'] =get_days(week)
        if(self.request.GET.get('date')):
            context['clients_count'] = len(get_count_of_clients(Item.objects.filter(date__date=self.request.GET.get('date'))))
            context['metals']= get_count_of_lamera(Item.objects.filter(date__date=self.request.GET.get('date')))[0]
            context['total_metals']= get_count_of_lamera(Item.objects.filter(date__date=self.request.GET.get('date')))[1]
            context['current_date'] = timezone.datetime.strptime(self.request.GET.get('date'),"%Y-%m-%d")
            context['operational_cost'] = get_opertional_cost(self.request.GET.get('date'))
        else:
            context['clients_count'] = len(get_count_of_clients(Item.objects.filter(date__date=get_days(week)[0])))
            context['metals']= get_count_of_lamera(Item.objects.filter(date__date=get_days(week)[0]))[0]
            context['total_metals']= get_count_of_lamera(Item.objects.filter(date__date=get_days(week)[0]))[1]
            context['current_date'] =get_days(week)[0]
            context['operational_cost'] = get_opertional_cost(get_days(week)[0])
        return context


class InvoiceDetailView(DetailView):
    """
    View for displaying invoice details.
    """
    model = Invoice
    template_name = 'invoice/invoicedetail.html'

    def get_success_url(self):
        """
        Return the URL to redirect to after a successful action.
        """
        return reverse('invoice-detail', kwargs={'slug': self.object.pk})


class InvoicePrepView(ListView):
    template_name = 'invoice/invoiceprep.html'
    context_object_name = 'items'

    
    def get_queryset(self):
        if(self.request.GET.get('date')):
            res =getstatus(Item.objects.filter(date__date=self.request.GET.get('date')))
        else:
            res =Item.objects.filter(date__date=get_yesterday())
        return res
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        date = get_yesterday()
        context['clients'] =get_count_of_clients(self.get_queryset(**kwargs))
        if(self.request.GET.get('date')):
            context['clients_count'] = len(get_count_of_clients(Item.objects.filter(date__date=self.request.GET.get('date'))))
            context['metals']= get_count_of_lamera(Item.objects.filter(date__date=self.request.GET.get('date')))[0]
            context['total_metals']= get_count_of_lamera(Item.objects.filter(date__date=self.request.GET.get('date')))[1]
            context['current_date'] =timezone.datetime.strptime(self.request.GET.get('date'),"%Y-%m-%d")
            context['operational_cost'] = get_opertional_cost(self.request.GET.get('date'))       
        else:
            context['clients_count'] = len(get_count_of_clients(Item.objects.filter(date__date=date)))
            context['metals']= get_count_of_lamera(Item.objects.filter(date__date=date))[0]
            context['total_metals']= get_count_of_lamera(Item.objects.filter(date__date=date))[1]
            context['current_date'] =date
            context['operational_cost'] = get_opertional_cost(date)
        return context

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new invoice.
    """
    model = Invoice
    template_name = 'invoice/invoicecreate.html'
    fields = [
        'sheet_metal_cost', 'dimensions', 'quantity',
        'scrap_type', 'scrap_value', 'unit_price'
    ]
    context_object_name = 'data'
    pk_url_kwarg = "id"
    def get_context_data(self, **kwargs: Any):
        context =super().get_context_data(**kwargs)
        context['item'] =Item.objects.get(id=self.kwargs.get('id'))
        return context
    def form_valid(self, form):
        item = Item.objects.get(id=self.kwargs.get('id'))
        self.object = form.save(commit=False)
        self.object.item = item
        self.object.save()
        return super().form_valid(form)
    def get_success_url(self):
        """
        Return the URL to redirect to after a successful creation.
        """
        date =comparetoday(Item.objects.get(id=self.kwargs.get("id")).date)
        return reverse('invoiceprep') + date


class InvoiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View for updating an existing invoice.
    """
    model = Invoice
    template_name = 'invoice/invoiceupdate.html'
    fields = [
        'customer_name', 'contact_number', 'item',
        'price_per_item', 'quantity', 'shipping'
    ]

    def get_success_url(self):
        """
        Return the URL to redirect to after a successful update.
        """
        return reverse('invoicelist')

    def test_func(self):
        """
        Determine if the user has permission to update the invoice.
        """
        return self.request.user.is_superuser


class InvoiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View for deleting an invoice.
    """
    model = Invoice
    template_name = 'invoice/invoicedelete.html'
    success_url = '/products'  # Can be overridden in get_success_url()

    def get_success_url(self):
        """
        Return the URL to redirect to after a successful deletion.
        """
        return reverse('invoicelist')

    def test_func(self):
        """
        Determine if the user has permission to delete the invoice.
        """
        return self.request.user.is_superuser


def create_operation_cost(request):

    if(request.method == "POST"):
        if(request.POST.get('date') and request.POST.get('rent') and request.POST.get("log") and request.POST.get('pay') and request.POST.get("elec") and request.POST.get('over')):
            Bill.objects.create(date=request.POST.get('date'),bill_type="Rent",amount=int(request.POST.get('rent')))
            Bill.objects.create(date=request.POST.get('date'),bill_type="Logistics",amount=int(request.POST.get('log')))
            Bill.objects.create(date=request.POST.get('date'),bill_type="PayRoll",amount=int(request.POST.get('pay')))
            Bill.objects.create(date=request.POST.get('date'),bill_type="Electric",amount=int(request.POST.get('elec')))
            Bill.objects.create(date=request.POST.get('date'),bill_type="Overtime",amount=int(request.POST.get('over')))
            return redirect(reverse("invoiceprep") + comparetoday(request.POST.get('date')))
        else:
            return HttpResponseBadRequest()