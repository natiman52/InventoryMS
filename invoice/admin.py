from django.contrib import admin
from .models import Invoice



@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Invoice model.
    """

    list_display = ("slug",'item',)
