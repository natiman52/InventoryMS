import django_tables2 as tables
from .models import Invoice
from store.models import Item
class InvoiceTable(tables.Table):
    """
    Table representation for the Invoice model.
    """

    class Meta:
        model = Item
        template_name = "django_tables2/semantic.html"
        fields = (
            'date', 'customer_name', 'contact_number',
            'price', 'quantity'
        )
        order_by = 'date'
