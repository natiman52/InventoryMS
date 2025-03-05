from django import forms
from .models import Item, Category, Delivery,ImageFile,DxfFile,Thickness
from django.forms import formset_factory
#Marketing Form
class ModuleSelectorModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%smm (%s)" %( obj.name, obj.added - obj.removed)

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
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control mb-3',}),
            "priority": forms.Select(attrs={'class': 'form-control mb-3'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'remark': forms.Textarea(
                attrs={
                    'class': 'form-control mb-3',
                    'rows': 5
                }
            ),
        }


# Designer Form
class ItemDxfForm(forms.ModelForm):
    dxf_file = forms.FileField(required=False,widget=forms.FileInput(attrs={'class':"form-control mb-2 mt-2"}))
    class Meta:
        model = Item
        fields = ('dxf_file',)
class ItemDxfAddForm(forms.Form):
    search = forms.CharField(required=False,widget=forms.HiddenInput(attrs={'class':"form-control mb-4 mt-2"}))
    dxf_file = forms.FileField(required=False,widget=forms.FileInput(attrs={'class':"form-control mb-4 mt-2"}))
    quantity = forms.IntegerField(required=True,widget=forms.TextInput(attrs={'class':"form-control mb-4 mt-2"}))


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
