from django.contrib import admin
from .models import Invoice
from bills.models import Bill,bill_type
def update_all(model,request,queryset):
    for i in queryset:
        item = Bill.objects.filter(date__date=i.item.date,bill_type__in=[x[0] for x in bill_type])
        if(item.exists()):
            i.save()
        else:
            return False
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Invoice model.
    """
    actions =[update_all]
    list_display = ("slug",'item',)
