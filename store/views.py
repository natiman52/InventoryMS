# Standard library imports
import operator
from functools import reduce
import json
# Django core imports
from asgiref.sync import async_to_sync
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render,redirect
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.core.serializers.json import DjangoJSONEncoder

# Authentication and permissions
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from channels.layers import get_channel_layer
# Class-based views
from django.views.generic import (
    DetailView, CreateView, UpdateView, DeleteView, ListView
)
# Third-party packages
from django_tables2 import SingleTableView
import django_tables2 as tables
from django_tables2.export.views import ExportMixin
import json
# Local app imports
from accounts.models import MyUser, Supplier,Employee
from .models import Category, Item, Delivery,ImageFile,DxfFile,Portfolio,Quote
from .forms import ItemForm, CategoryForm, DeliveryForm,imageFileForm,DXFFileForm
from .tables import ItemTable
from django.utils import timezone
from store.signals import ChangeId
from .filters import get_date_specfic
from bills.algebra import get_total_paid_value,get_total_unpaid_value,get_days,get_all_expense,get_total_salary_paid,get_material_cost,get_months_with_their_weeks

def HomePage(request):
    porto = Portfolio.objects.all().order_by('-date')
    return render(request,'index.html',{'porto':porto})

class Dashboard(LoginRequiredMixin,ListView):
    template_name = "store/dashboard.html"
    context_object_name = "items"
    paginate_by = 8
    export_name = "given_order_list"
    def get_queryset(self):
        date =timezone.now()
        if(self.request.GET.get("sort") == 'yesterday'):
            date =timezone.datetime(date.year,date.month,date.day ) -timezone.timedelta(days=1)
        date_time2 =date.replace(hour=0,minute=0,second=0) + timezone.timedelta(hours=23,minutes=59,seconds=0)
        my_range = [date.replace(hour=0,minute=0,second=0),date_time2]
        if(self.request.user.role == "AD" or self.request.user.role == "SH"):
            items = Item.objects.all()
            return items
        elif(self.request.user.role == "MR"):
            items = Item.objects.filter(Q(verif_price='P',date__date=date) | Q(verif_design="P",date__range=my_range))
            if(self.request.GET.get("sort") == "all"):
                items = Item.objects.filter(Q(verif_price='P') | Q(verif_design="P"))
            if(self.request.GET.get('q')):
                items=items.filter(Q(id__contains=self.request.GET.get('q')) | Q(client__name__contains=self.request.GET.get('q')))
            return items
        elif(self.request.user.role == "DR"):
            items = Item.objects.filter( Q(verif_design="W",date__date=date) | Q(verif_design="D",date__range=my_range))
            if(self.request.GET.get("sort") == "all"):
                items = Item.objects.filter(Q(verif_design="W") | Q(verif_design="D"))
            if(self.request.GET.get('q')):
                items=items.filter(Q(id__contains=self.request.GET.get('q')) | Q(client__name__contains=self.request.GET.get('q')))
            return items
        elif(self.request.user.role == "AT" or self.request.user.role == "GM"):
            profiles = MyUser.objects.all()
            items = Item.objects.filter(Q(verif_price="W",date__date=date,verif_design="A") | Q(verif_design="A",verif_price="D",date__range=my_range))
            if(self.request.GET.get("sort") == "all"):
                items = Item.objects.filter(Q(verif_price="W",verif_design="A") | Q(verif_design="A",verif_price="D"))
            if(self.request.GET.get('q')):
                items=items.filter(Q(id__contains=self.request.GET.get('q')) | Q(client__name__contains=self.request.GET.get('q')))
            return items
        elif(self.request.user.role == "OP"):
            my_range=get_date_specfic(timezone.now().isoweekday())
            if(self.request.GET.get("sort") and self.request.GET.get("sort").isdigit()):
                my_range=get_date_specfic(int(self.request.GET.get('sort')))
            items = Item.objects.filter(verif_price="A",date__date=date,verif_design="A",completed=False)
            if(self.request.GET.get("sort") == "all"):
                items = Item.objects.filter(verif_price='A',verif_design="A",completed=False)
            if(self.request.GET.get('q')):
                items=items.filter(Q(id__contains=self.request.GET.get('q')) | Q(client__name__contains=self.request.GET.get('q')))     
            return items 
    def get_context_data(self, **kwargs):
        if(self.request.user.role != "SH" and self.request.user.role != "AD"):
            return super().get_context_data(**kwargs)
        else:
            profiles = Employee.objects.all()
            items = Item.objects.filter(date__year=timezone.now().year)
            paid_order =get_total_paid_value(items) 
            unpaid_order =get_total_unpaid_value(items) 
            total_order = paid_order + unpaid_order
            unpaid_expense,paid_expense= get_all_expense()
            orders_count = items.count()
            debt_material,free_material =get_material_cost()
            profit = total_order - (unpaid_expense + paid_expense) - get_total_salary_paid() - (debt_material + free_material)
            each_month_data=items.filter(completed=True).annotate(month=TruncMonth('finish')).values('month').annotate(sum=Sum('price')).order_by('-month')
            profit_type = True
            if(profit < 0):
                profit_type = False
            context = {
            "profiles_count": profiles.count(),
            "items_count": orders_count,
            "each_month_data":json.dumps(list(each_month_data),cls=DjangoJSONEncoder),
            "total_order_value": total_order,
            "total_expense":int(paid_expense+unpaid_expense),
            "total_payroll":get_total_salary_paid(),
            "total_material":debt_material+free_material,
            "profit":int(profit),
            'profit_type':profit_type,
            "vendors": Supplier.objects.all(),
            "delivery": Delivery.objects.all(),
        }
            return context

class AllList(ListView):
    model =Item
    template_name = "store/all_list.html"
    context_object_name = "items"
    paginate_by = 25
    def get_queryset(self,**kwargs):
        if(self.request.GET.get('month')):
            week =get_months_with_their_weeks()[int(self.request.GET.get('month')) - 1].get('initial_week')
        else:
            week = get_months_with_their_weeks()[0].get('initial_week')
        if(self.request.GET.get('week')):
            day =get_days(int(self.request.GET.get('week')))[0]
        else:
            day =get_days(week)[0]
        items = Item.objects.filter(completed=True)
        if(self.request.GET.get('date')):
            items =items.filter(finish__date=self.request.GET.get('date'))
        else:
            items = items.filter(finish__date=day)
        return items
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        weeks =get_months_with_their_weeks()
        context['weeks'] = weeks
        week = weeks[0].get('initial_week')
        if(self.request.GET.get('month')):
            week =weeks[int(self.request.GET.get('month')) - 1].get('initial_week')
            context['week'] = weeks[int(self.request.GET.get('month')) - 1].get('initial_week')
        else:
            context['week'] = weeks[0].get('initial_week')
        if(self.request.GET.get('week')):
            context['days'] =get_days(int(self.request.GET.get('week')))
        else:
            context['days'] =get_days(week)
        return context


class GivenOrderListView(LoginRequiredMixin, ExportMixin, tables.SingleTableView):
    """
    View class to display a list of products.

    Attributes:
    - model: The model associated with the view.
    - table_class: The table class used for rendering.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    - paginate_by: Number of items per page for pagination.
    """

    queryset = Item.objects.filter(Q(verif_price="W") | Q(verif_design="W"))
    table_class = ItemTable
    template_name = "store/GivenProductList.html"
    context_object_name = "items"
    paginate_by = 30
    export_name = "given_order_list"
    SingleTableView.table_pagination = False


class ProductListView(LoginRequiredMixin,ExportMixin, tables.SingleTableView):
    """
    View class to display a list of products.

    Attributes:
    - model: The model associated with the view.
    - table_class: The table class used for rendering.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    - paginate_by: Number of items per page for pagination.
    """
    table_class = ItemTable
    template_name = "store/productslist.html"
    context_object_name = "items"
    paginate_by = 30
    queryset = Item.objects.all()
    SingleTableView.table_pagination = False


class ItemSearchListView(ProductListView):
    """
    View class to search and display a filtered list of items.

    Attributes:
    - paginate_by: Number of items per page for pagination.
    """

    paginate_by = 40

    def get_queryset(self):
        result = super(ItemSearchListView, self).get_queryset()

        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.and_, (Q(client__name__icontains=q) for q in query_list)
                )
            )
        return result

class ProductDetailView(LoginRequiredMixin,UserPassesTestMixin,DetailView):
    
    model = Item
    template_name = "store/productdetail.html"
    context_object_name = 'item'
    def test_func(self):

        if self.request.user.role == "MR" or self.request.user.role == "GM":
            return True
        else:
            return False
    def get_object(self, queryset=None):
        id =self.kwargs['id']
        object = Item.objects.get(id=id)
        return object
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if(context['item'].diminsions):
            context['diminsion'] = json.loads(context['item'].diminsions)
        return context
    def post(self,request,id):
        channel = get_channel_layer()
        design = request.POST.get('design')
        price = request.POST.get('price')
        obj = Item.objects.get(id=id)
        if(design and obj.dxf_file):
            obj.verif_design =design
            if(design == "D"):
                obj.dxf_file.delete()
                async_to_sync(channel.group_send)("DR",{"type":"send.notification"})
            if(design == "A"):
                async_to_sync(channel.group_send)("AT",{"type":"send.notification"})
        if(price and obj.price):
            obj.verif_price = price
            if(price == "D"):
                async_to_sync(channel.group_send)("AT",{"type":"send.notification"})
        obj.save()
        if(obj.verif_price == "A" and obj.verif_design == "A"):
            async_to_sync(channel.group_send)("OP",{"type":"send.notification"})
        return redirect(f'/new-order/{obj.id}')



def Item_create_view(request,type):
    form = ItemForm()
    if(request.method == "POST"):
        form = ItemForm(request.POST,request.FILES)
        dimensions = request.POST.get("dimensions")
        width = request.POST.get("width")
        length =request.POST.get("length")
        if(form.is_valid()):
            obj = form.save(commit=False)
            obj.user =request.user
            obj.type =type
            if(request.FILES.get('image1')):
                obj.image1 =request.FILES.get('image1')
            else:
                return render(request,"store/productcreate.html",{"form":form,'type':type,"error":True})
            if(request.FILES.get('image2')):
                obj.image2 =request.FILES.get('image2')
            if(request.FILES.get('image3')):
                obj.image3 =request.FILES.get('image3')  
            if(dimensions):
                obj.dimensions_type =dimensions
            if(dimensions == 'rectangular' and width and length):
               obj.diminsions = json.dumps({"type":"rectangular","width":width,"length":length})
            elif(dimensions == "square" and width):
                obj.diminsions=json.dumps({'type':"square","width":request.POST.get("width")})
            elif(dimensions == 'other' and request.FILES.get("dimensions-image") ):
                obj.dimensions_image = request.FILES.get("dimensions-image")
                obj.dimensions_info =request.POST.get("dimensions_info")
                obj.quantity = 0
            elif(dimensions == 'other' and request.POST.get('dimensions_info')):
                obj.quantity = 0
                obj.dimensions_info =request.POST.get("dimensions_info")
            else:   
                return render(request,"store/productcreate.html",{"form":form,'type':type,"error":True})
            ChangeId(obj)
            obj.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('DR',{"type":"send.notification",'message':"message"})
            return redirect(reverse("dashboard"))
        return render(request,"store/productcreate.html",{"form":form,'type':type,"error":True})   
    return render(request,"store/productcreate.html",{"form":form,'type':type})


# finsihed top level

class PhotoCreateView(LoginRequiredMixin,CreateView):
    model =ImageFile
    template_name = 'store/newphoto.html'
    form_class = imageFileForm
    success_url = "/"
    def get_context_data(self, **kwargs) :
        context =super().get_context_data(**kwargs)
        context['type']=self.kwargs.get('type')
        return context
class DXFCreateView(LoginRequiredMixin,CreateView):
    model =DxfFile
    template_name = 'store/newdxf.html'
    form_class = DXFFileForm
    def get_success_url(self):
        return reverse('order-dxf',kwargs={'type':self.kwargs['type']})
    def get_context_data(self, **kwargs) :
        context =super().get_context_data(**kwargs)
        context['type']=self.kwargs.get('type')
        return context
class DXFUpdateView(LoginRequiredMixin,UpdateView):
    model =DxfFile
    template_name = 'store/newdxf.html'
    form_class = DXFFileForm
    pk_url_kwarg = "id"
    def get_success_url(self):
        return reverse('order-dxf',kwargs={"type":self.get_object().type})
    def get_context_data(self, **kwargs) :
        context =super().get_context_data(**kwargs)
        context['type']=self.get_object().type
        return context    
    def post(self, request, *args, **kwargs):
        if(self.get_form().is_valid()):
            self.get_object().dxf_file.delete()
        return super().post(request, *args, **kwargs)


@login_required    
def listofOrders(request,type):
    return render(request,'store/list-of-info.html',{"type":type})

def listofPhoto(request,type):
    images = ImageFile.objects.filter(type=type)
    if(request.GET.get('q')):
       images = images.filter(Q(name__contains=request.GET.get('q')))
    return render(request,"store/photo_list.html",{"photos":images,"type":type})
def listofDxf(request,type):
    object = DxfFile.objects.filter(type=type)
    items = Item.objects.filter( ~Q(dxf_file='') & Q(type=type))
    if(request.GET.get('q')):
        items=items.filter(Q(dxf_file__contains=request.GET.get('q')))
        object=object.filter(Q(dxf_file__contains=request.GET.get('q')))       
    context = {"Dxf_flies":list(object) ,"items":list(items),"type":type}
    return render(request,"store/list_of_dxf.html",context)


## End of Known Functions
class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View class to delete a product.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful deletion.
    """

    model = Item
    template_name = "store/productdelete.html"
    success_url = "/products"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return False


class DeliveryListView(
    LoginRequiredMixin, ExportMixin, tables.SingleTableView
):
    """
    View class to display a list of deliveries.

    Attributes:
    - model: The model associated with the view.
    - pagination: Number of items per page for pagination.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    """

    model = Delivery
    pagination = 10
    template_name = "store/deliveries.html"
    context_object_name = "deliveries"


class DeliverySearchListView(DeliveryListView):
    """
    View class to search and display a filtered list of deliveries.

    Attributes:
    - paginate_by: Number of items per page for pagination.
    """

    paginate_by = 10

    def get_queryset(self):
        result = super(DeliverySearchListView, self).get_queryset()

        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.
                    and_, (Q(customer_name__icontains=q) for q in query_list)
                )
            )
        return result


class DeliveryDetailView(LoginRequiredMixin, DetailView):
    """
    View class to display detailed information about a delivery.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    """

    model = Delivery
    template_name = "store/deliverydetail.html"


class DeliveryCreateView(LoginRequiredMixin, CreateView):
    """
    View class to create a new delivery.

    Attributes:
    - model: The model associated with the view.
    - fields: The fields to be included in the form.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Delivery
    form_class = DeliveryForm
    template_name = "store/delivery_form.html"
    success_url = "/deliveries"


class DeliveryUpdateView(LoginRequiredMixin, UpdateView):
    """
    View class to update delivery information.

    Attributes:
    - model: The model associated with the view.
    - fields: The fields to be updated.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Delivery
    form_class = DeliveryForm
    template_name = "store/delivery_form.html"
    success_url = "/deliveries"


class DeliveryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View class to delete a delivery.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful deletion.
    """

    model = Delivery
    template_name = "store/productdelete.html"
    success_url = "/deliveries"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return False


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'store/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    login_url = 'login'


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'store/category_detail.html'
    context_object_name = 'category'
    login_url = 'login'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'store/category_form.html'
    form_class = CategoryForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'store/category_form.html'
    form_class = CategoryForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'store/category_confirm_delete.html'
    context_object_name = 'category'
    success_url = reverse_lazy('category-list')
    login_url = 'login'


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'



@login_required
def get_items_ajax_view(request):
    if is_ajax(request):
        try:
            type=request.GET.get('type')
            files =json.dumps([item.toJSON() for item in Item.objects.filter(Q(verif_design="A") & Q(type=type)) ])
            files2 =json.dumps([file.toJSON() for file in DxfFile.objects.filter(type=type)])
            return JsonResponse({'files':files,'files2':files2}, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Not an AJAX request'}, status=400)
