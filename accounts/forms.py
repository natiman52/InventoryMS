from django import forms
from store.models import Item
from .models import MyUser, Customer, Supplier


class CreateUserForm(forms.ModelForm):
    """Form for creating a new user with an email field."""
    username = forms.CharField(max_length=256)
    password1 = forms.CharField(label='password',widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm Password',widget=forms.PasswordInput)

    class Meta:
        """Meta options for the CreateUserForm."""
        model = MyUser
        fields = ['username','password1','password2',"role"]
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if(password1 == password2 and password1 and password2):
            self.save(self)
            user =super(CreateUserForm,self).save(commit=False)
            user.set_password(self.cleaned_data.get('password1'))
            user.save()
            return user
        else:
            raise forms.ValidationError()
class UserUpdateForm(forms.ModelForm):
    """Form for updating existing user information."""
    class Meta:
        """Meta options for the UserUpdateForm."""
        model = MyUser
        fields = [
            'username',
            'role'
        ]
class CustomerForm(forms.ModelForm):
    """Form for creating/updating customer information."""
    class Meta:
        model = Customer
        fields = [
            "name",
            'address',
            'email',
            'phone',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter name'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address',
                'rows': 3
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),

        }

class ItemPriceForm(forms.ModelForm):
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class':"form-control"}))
    class Meta:
        model = Item
        fields = ('price',)

class SupplierForm(forms.ModelForm):
    """Form for creating/updating vendor information."""
    class Meta:
        model = Supplier
        fields = ['name', 'phone_number', 'address']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Vendor Name'}
            ),
            'phone_number': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Phone Number'}
            ),
            'address': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Address'}
            ),
        }
