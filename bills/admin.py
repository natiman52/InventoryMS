from django.contrib import admin
from .models import Bill,InventoryMaterial,SingleMaterial,InventoryPayment,Thickness,ClientPayment,FreeAssets


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    """Admin interface for managing Bill instances."""
    list_display = (
        'slug',
        'date',
        'description',
        'amount',
        'status'
    )
@admin.register(ClientPayment)
class CPadmin(admin.ModelAdmin):
    list_display = ('customer',)
@admin.register(FreeAssets)
class FAadmin(admin.ModelAdmin):
    list_display = ('customer',"ammount")
@admin.register(InventoryMaterial)
class IBAdmin(admin.ModelAdmin):
    list_display = ('supplier',"user")
@admin.register(InventoryPayment)
class IPAdmin(admin.ModelAdmin):
    list_display = ('inventory',"amount")
@admin.register(SingleMaterial)
class SIAdmin(admin.ModelAdmin):
    list_display = ('thickness',"price")

@admin.register(Thickness)
class TKAdmin(admin.ModelAdmin):
    list_display = ('name',"added","removed")