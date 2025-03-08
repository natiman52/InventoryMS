
from django.forms import formset_factory
from .models import  Item ,UserPrint
from django.utils import timezone
from django.db.models.base import Model as Model
from django.shortcuts import render,redirect
from django.urls import reverse
from django.db.models import Q
import json
from django.core.exceptions import PermissionDenied
# Authentication and permissions
from asgiref.sync import async_to_sync
import string
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import SingleTableView
import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from .tables import ItemTableDesign
from channels.layers import get_channel_layer
# Class-based views
from django.views.generic import  ListView
from .forms import ItemDxfForm,ItemDxfAddForm,MyFormSet
from .filters import get_item_or_dxffile
def test_func_design_view(user):
        if user.role == "DR" or user.role == "AD":
            return True
        else:
            return False
@login_required
@user_passes_test(test_func_design_view)
def design_detail_view(request,id):
    context = {}
    form = ItemDxfForm()
    model_formset =formset_factory(form=ItemDxfAddForm,formset=MyFormSet,extra=0)
    item = Item.objects.get(id=id)
    context['form'] = form
    context['item'] = item
    context['formset'] = model_formset
    if(item.diminsions):
        context['diminsion'] = json.loads(item.diminsions)
    if(request.method == "POST"):
        channel = get_channel_layer()
        async_to_sync(channel.group_send)('MR',{'type':"send.notification"})
        item =Item.objects.get(id=id)
        formset= model_formset(request.POST,request.FILES)
        if(request.POST.get('choosen') != "" or request.FILES.get('dxf_file')):
            UserPrint.objects.create(user=request.user,item=item,comment="designer_change_add")
            item.verif_design = "P"
            if(request.POST.get('choosen') != ""):
                item.dxf_file = get_item_or_dxffile(request.POST.get('choosen')).dxf_file
            else:
                item.dxf_file =request.FILES.get("dxf_file")
            if(not request.POST.get('hidden')):
                item.save()
                return redirect(reverse('designer-order',kwargs={"id":item.id}))
            elif(request.POST.get('hidden') and request.POST.get('quantity')):
                if(int(request.POST.get('quantity')) < (item.thickness.added - item.thickness.removed)):
                    item.quantity = int(request.POST.get('quantity'))
                    if(formset.is_valid()):
                        if(formset.my_custom_clean(item)):
                            item.subclassed = True
                            item.save()
                            for index,f in enumerate(formset):
                                item2 =Item.objects.get(id=id)
                                print(item2.pk + string.ascii_uppercase[index])
                                item2.pk = item2.pk + string.ascii_uppercase[index]
                                if(f.cleaned_data.get('search')):
                                    item2.dxf_file = get_item_or_dxffile(f.cleaned_data.get('search')).dxf_file
                                else:
                                    item2.dxf_file = f.cleaned_data.get("dxf_file")
                                item2.quantity = f.cleaned_data.get('quantity')
                                item2.subclassed = True
                                item2.save()
                            return redirect(reverse('designer-order',kwargs={"id":item.id}))
                        else:
                            context['formset'] = formset
                            context['errors'] = {'main':'please correct your errors'}
                            return render(request,"store/designdetail.html",context)                            
                    else:
                        context['formset'] = formset
                        context['errors'] = {'main':'please at least fill the first form'}
                        return render(request,"store/designdetail.html",context)
                else:
                    context['formset'] = formset
                    context['errors'] = {'main_quantity':'not enough in inventory','main':'please at least fill the first form'}
                    return render(request,"store/designdetail.html",context)                    
            elif(not request.POST.get('quantity')):
                context['formset'] = formset
                context['errors'] = {'main_quantity':'please fill the quantity'}
                return render(request,"store/designdetail.html",context)
        else:
            context['formset'] = formset
            context['errors'] = {'main':'please at least fill the first form'}
            return render(request,"store/designdetail.html",context)
    return render(request,"store/designdetail.html",context)


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
            self.queryset = self.model.objects.filter(Q(completed=True,id__contains=request.GET.get('q')) | Q(completed=True,client__name__contains=request.GET.get('q')))
        return super(OperatorFinishedList,self).get(request,*args,**kwargs)
    def get_queryset(self):
        obje = Item.objects.filter(verif_price="A",verif_design="A",completed=True)
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
            obj.thickness.removed += obj.quantity
            obj.save()
        if(request.POST.get('finish')):
            obj.completed = True
            obj.finish = timezone.now()
            UserPrint.objects.create(user=request.user,item=obj,comment="operator_finished_task")
            obj.save()  
            return redirect(reverse("operator-finished"))
    return render(request,"store/operator/operatordetail.html",context)

