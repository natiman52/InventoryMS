from django.contrib import admin
from .models import MyUser, Supplier,Customer
from django.contrib.auth import admin as base
from .forms import *
@admin.register(MyUser)
class MyuserAdmin(base.UserAdmin):
    form =UserUpdateForm
    add_form = CreateUserForm
    list_display= ('username','role')
    fieldsets = (('personal',{"fields":('username',"password")}),(None,{"fields":('role',)}))
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display=('name',)
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    fields = ("user",'name', 'phone_number', 'address')
    list_display = ('name', 'phone_number', 'address')
    search_fields = ('name', 'phone_number', 'address')
