
from django.forms import formset_factory
from .models import  Item ,UserPrint
from django.utils import timezone
from django.db.models.base import Model as Model
from django.shortcuts import render,redirect
from django.urls import reverse, reverse_lazy
from django.db.models import Q
import json
from django.core.exceptions import PermissionDenied
# Authentication and permissions
from asgiref.sync import async_to_sync
import string
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django_tables2 import SingleTableView
import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from .tables import ItemTableDesign
from channels.layers import get_channel_layer
# Class-based views
from django.views.generic import (DetailView, UpdateView, ListView)
from .forms import ItemDxfForm,ItemDxfAddForm
from django.contrib.auth.mixins import UserPassesTestMixin
from .filters import get_item_or_dxffile
class DesignDetailView(LoginRequiredMixin,DetailView,UserPassesTestMixin,UpdateView):
    model = Item
    context_object_name = 'item'
    template_name = 'store/designdetail.html'
    form_class = ItemDxfForm
    pk_url_kwarg = 'id'
    def get_success_url(self) -> str:
        return reverse_lazy('designer-order',kwargs={"id":self.kwargs['id']})
    def test_func(self):
        if self.request.user.role == "DR" or self.request.user.role == "AD":
            return True
        else:
            return False
    def get_context_data(self, **kwargs):
        context = super(DesignDetailView,self).get_context_data(**kwargs)
        formset =formset_factory(form=ItemDxfAddForm,extra=0)
        context['formset'] = formset()
        if(context['item'].diminsions):
            context['diminsion'] = json.loads(context['item'].diminsions)
        return context
    def post(self, request,id, *args, **kwargs):
        channel = get_channel_layer()
        async_to_sync(channel.group_send)('MR',{'type':"send.notification"})
        item =self.get_object()
        model_formset =formset_factory(form=ItemDxfAddForm,extra=0)
        formset= model_formset(request.POST,request.FILES)
        print(formset.errors)
        if(request.POST.get('choosen') != "" or request.FILES.get("dxf_file")):
            UserPrint.objects.create(user=request.user,item=self.get_object(),comment="designer_change_add")
            item.verif_design = "P"
            if(request.POST.get('choosen') != ""):
                item.dxf_file = get_item_or_dxffile(request.POST.get('choosen')).dxf_file
            if(request.POST.get('quantity')):
                item.quantity = int(request.POST.get('quantity'))
            item.save()
            for index,f in enumerate(formset):
                if(f.is_valid()):
                    item2 =self.get_object()
                    print(item2.pk + string.ascii_uppercase[index])
                    item2.pk = item2.pk + string.ascii_uppercase[index]
                    item2.dxf_file = f.cleaned_data.get("dxf_file")
                    if(f.cleaned_data.get('search')):
                        item2.dxf_file = get_item_or_dxffile(f.cleaned_data.get('search')).dxf_file
                    item2.quantity = f.cleaned_data.get('quantity')
                    item2.subclassed = True
                    item2.save()
        return super(DesignDetailView,self).post(request,*args,**kwargs)

class DesignerOrderList(LoginRequiredMixin, ExportMixin , tables.SingleTableView):
    model = Item
    context_object_name = "items"
    table_class = ItemTableDesign
    template_name = 'store/designerorderlist.html'
    paginate_by = 10
    SingleTableView.table_pagination = False
    def get_queryset(self):
        objects = Item.objects.filter(verif_design="P")
        return objects

class DesignerOrderListFinished(ListView):
    context_object_name = "items"
    template_name = 'store/designerorderlist.html'
    def get_queryset(self):
        objects = Item.objects.filter(verif_design="A")
        return objects
    

# Operator Views
class OperatorFinishedList(LoginRequiredMixin, ExportMixin , tables.SingleTableView):
    context_object_name = "items"
    table_class = ItemTableDesign
    paginate_by =10
    template_name = 'store/operator/operatororderlist.html'
    SingleTableView.table_pagination = False
    def get(self,request,*args,**kwargs):
        if(request.GET.get('q')):
            self.queryset = self.model.objects.filter(Q(id__contains=request.GET.get('q')) | Q(client__name__contains=request.GET.get('q')))
        return super(OperatorFinishedList,self).get(request,*args,**kwargs)
    def get_queryset(self):
        obje = []
        prints =UserPrint.objects.filter(user=self.request.user)
        for i in prints:
            try:
                if(i.item.completed == True and (obje.index(i.item))):
                    pass
            except:
                    if(i.item.completed == True):
                        obje.append(i.item)
        return obje
def test_func(event):
    if(event.role == "OP" or event.role == "AD"):
        return True
    else:
        return False
@login_required()
@user_passes_test(test_func)
def operator_detail_view(request,id):
    context = {}
    obj = Item.objects.get(id=id)
    if(obj.verif_design !='A' and obj.verif_price !='A'):
        return PermissionDenied()
    if(obj.diminsions):
            context['diminsion'] = json.loads(obj.diminsions)
    context['item'] = obj
    if request.method == "POST":
        if(request.POST.get('start')):
            obj.start = timezone.now()
            UserPrint.objects.create(user=request.user,item=obj,comment="operator_started_task")
            obj.save()
        if(request.POST.get('finish')):
            obj.completed = True
            obj.finish = timezone.now()
            UserPrint.objects.create(user=request.user,item=obj,comment="operator_finished_task")
            obj.save()  
            return redirect(reverse("operator-finished"))
    return render(request,"store/operator/operatordetail.html",context)

