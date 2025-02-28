from django.contrib import admin
from .models import Bill,InventoryMaterial,SingleMaterial,InventoryPayment


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    """Admin interface for managing Bill instances."""

    fields = (
        'date',
        'institution_name',
        'phone_number',
        'email',
        'address',
        'description',
        'payment_details',
        'amount',
        'status'
    )

    list_display = (
        'slug',
        'date',
        'institution_name',
        'phone_number',
        'email',
        'address',
        'description',
        'payment_details',
        'amount',
        'status'
    )


@admin.register(InventoryMaterial)
class IBAdmin(admin.ModelAdmin):
    list_display = ('supplier',"user")
@admin.register(InventoryPayment)
class IPAdmin(admin.ModelAdmin):
    list_display = ('inventory',"amount")
@admin.register(SingleMaterial)
class SIAdmin(admin.ModelAdmin):
    list_display = ('thickness',"quantity")