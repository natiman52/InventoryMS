from django import forms
from .models import Item, Category, Delivery,ImageFile,DxfFile,Thickness,Quote
from django.forms import BaseFormSet


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = '__all__'
class MyFormSet(BaseFormSet):
    def my_custom_clean(self,item):
        for form in self.forms:
            if(form.cleaned_data.get('quantity') and form.cleaned_data.get('thickness')):
                available =form.cleaned_data.get('thickness').added - form.cleaned_data.get('thickness').removed
                if(int(form.cleaned_data.get('quantity')) > available):
                    form.add_error('quantity',"there is not enough lamera")
                    return False
        return True
#Marketing Form
class ModuleSelectorModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s (%s)" %( obj.get_name_display(), obj.added - obj.removed)

class ItemForm(forms.ModelForm):
    thickness =ModuleSelectorModelChoiceField(Thickness.objects.all(),widget=forms.Select(attrs={'class':"form-control mb-3"}))  
    """
    A form for creating or updating an Item in the inventory.
    """
    class Meta:
        model = Item
        fields = [
            'client',
            'thickness',
            'priority',
            'quantity',
            'remark',
        ]
    def clean(self):
        thickness =self.cleaned_data.get('thickness')
        if((thickness.added - thickness.removed) < int(self.cleaned_data.get('quantity'))):
            raise forms.ValidationError({"quantity":'there is no availble material'})
        else:
            return self.cleaned_data
# Designer Form
class ItemDxfForm(forms.ModelForm):
    dxf_file = forms.FileField(required=False,widget=forms.FileInput(attrs={'class':"form-control mb-2 mt-2"}))
    thickness =ModuleSelectorModelChoiceField(required=False,queryset=Thickness.objects.all(),widget=forms.Select(attrs={'class':"form-control mb-3"}))  
    class Meta:
        model = Item
        fields = ('dxf_file',)
class ItemDxfAddForm(forms.Form):
    search = forms.CharField(required=False,widget=forms.HiddenInput(attrs={'class':"form-control mb-2 mt-2"}))
    dxf_file = forms.FileField(required=False,widget=forms.FileInput(attrs={'class':"form-control mb-3 mt-2"}))
    thickness =ModuleSelectorModelChoiceField(required=True,queryset=Thickness.objects.all(),widget=forms.Select(attrs={'class':"form-control mb-3"}))  
    quantity = forms.IntegerField(required=True,widget=forms.TextInput(attrs={'class':"form-control mb-2 mt-1"}))
    def clean_quantity(self):
        if(self.cleaned_data.get("quantity")):
            return self.cleaned_data.get("quantity")
        else:
            raise forms.ValidationError('please fill the quantity')
    def get_item_or_dxffile(self):
        dx = self.cleaned_data.get("search")
        if(dx[:2] == "It"):
            return Item.objects.get(id=dx[3:],verif_design="A")
        else:
            return DxfFile.objects.get(id=int(dx[3:]))

# Accountant Form

#Operator View Form


#Addition Form
class CategoryForm(forms.ModelForm):
    """
    A form for creating or updating category.
    """
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
                'aria-label': 'Category Name'
            }),
        }
        labels = {
            'name': 'Category Name',
        }
class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = [
            'item',
            'customer',
            'is_delivered'
        ]
        widgets = {
            'item': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select item',
            }),
            'customer': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select customer',
            }),
            'is_delivered': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'label': 'Mark as delivered',
            }),
        }
class imageFileForm(forms.ModelForm):
    type = forms.CharField(widget=forms.TextInput(attrs={'type':'hidden',"id":"type"}))
    class Meta:
        model = ImageFile
        fields = ["image",'type']
        widgets={
            "image":forms.FileInput(attrs={"class":"form-control  mt-1"})
        }
class DXFFileForm(forms.ModelForm):
    type = forms.CharField(widget=forms.TextInput(attrs={'type':'hidden',"id":"type"}))
    class Meta:
        model = DxfFile
        fields = ["dxf_file",'type']
        widgets={
            "dxf":forms.FileInput(attrs={"class":"form-control  mt-1"})
        }
