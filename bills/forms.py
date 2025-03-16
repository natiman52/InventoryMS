from typing import Any
from django import forms
from  .models import SingleMaterial,InventoryMaterial,Thickness


class InventoryUpdateBillForm(forms.Form):
    payment = forms.IntegerField(widget=forms.NumberInput(attrs={"class":"form-control mt-2"}))    
  
class InventoryBillForm(forms.ModelForm):
    class Meta:
        model = InventoryMaterial
        fields = ['supplier',"minsceus_cost","payment_method",'advance']
        widgets = {
            'supplier':forms.Select(attrs={"class":"form-control"}),
            "payment_method":forms.Select(attrs={"class":"form-control mt-2"}),
            "minsceus_cost":forms.NumberInput(attrs={"class":"form-control mt-2"}),
            'advance':forms.NumberInput(attrs={"class":"form-control"}),
        }

class ModuleSelectorModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%smm" % obj.name

class SingleBillForm(forms.ModelForm):
    thickness = forms.ModelChoiceField(Thickness.objects.all())
    quantity= forms.IntegerField(widget=forms.NumberInput(attrs={"class":"form-control mt-2"}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={"class":"form-control mt-2"}))
    class Meta:
        model = SingleMaterial
        fields = ['thickness','quantity',"price"]

        def clean_thickness(self) :
            if (self.thickness == "----"):
                self.is_bound = False
            return self.thickness