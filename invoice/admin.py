from django.contrib import admin
from .models import Invoice

def update_all(model,request,queryset):
    for i in queryset:
        i.save()
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Invoice model.
    """
    actions =[update_all]
    list_display = ("slug",'item',)
