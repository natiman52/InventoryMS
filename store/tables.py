import django_tables2 as tables
from .models import Item, Delivery


class ItemTable(tables.Table):
    """
    Table representation for Item model.
    """
    class Meta:
        model = Item
        template_name = "django_tables2/semantic.html"
        fields = (
            'id', 'client', 'quantity',"thickness",
            'price', 'date'
        )
        order_by_field = 'sort'

class ItemTableDesign(tables.Table):
    """
    Table representation for Item model.
    """
    class Meta:
        model = Item
        template_name = "django_tables2/semantic.html"
        fields = (
            'id', 'client', 'quantity',"thickness",
            'price', 'date','verif_design'
        )
        order_by_field = 'sort'
class ItemTableOperator(tables.Table):
    """
    Table representation for Item model.
    """
    class Meta:
        model = Item
        template_name = "django_tables2/semantic.html"
        fields = (
            'id', 'client', 'quantity',"completed",
            'price', 'date','start','finish'
        )
        order_by_field = 'sort'
class DeliveryTable(tables.Table):
    """
    Table representation for Delivery model.
    """
    class Meta:
        model = Delivery
        fields = (
            'id', 'item', 'customer_name', 'phone_number',
            'location', 'date', 'is_delivered'
        )
