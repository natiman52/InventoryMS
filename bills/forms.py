from django import forms
from  .models import SingleMaterial,InventoryMaterial


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
class SingleBillForm(forms.ModelForm):
    quantity = forms.IntegerField()
    price = forms.IntegerField()
    class Meta:
        model = SingleMaterial
        fields = ['thickness','quantity',"price"]
        widgets = {
            'thickness':forms.Select(attrs={"class":"form-control"}),
            "quantity":forms.Select(attrs={"class":"form-control mt-2"}),
            "price":forms.NumberInput(attrs={"class":"form-control mt-2"}),
        }
