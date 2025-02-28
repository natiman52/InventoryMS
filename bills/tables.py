import django_tables2 as tables
from .models import Bill,InventoryMaterial


class BillTable(tables.Table):
    """Table view for displaying bills."""

    class Meta:
        """Meta options for the BillTable."""
        model = InventoryMaterial
        template_name = "django_tables2/semantic.html"
        fields = (
            'id',
            'supplier__name',
            'payment_method',
            'total_cost',
            'minsceus_cost',
        )
        order_by_field = 'sort'
