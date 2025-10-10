import django_tables2 as tables
from django.shortcuts import render

from .models import MyUser


class ProfileTable(tables.Table):
    """Table representation for Profile model."""

    class Meta:
        """Meta options for the ProfileTable."""
        model = MyUser
        template_name = "django_tables2/semantic.html"
        fields = (
            'date',
            'customer_name',
            'contact_number',
            'item',
            'price_per_item',
            'quantity',
            'total'
        )
        order_by_field = 'sort'
