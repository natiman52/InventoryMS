"""
Module: admin.py

Django admin configurations for managing categories, items, and deliveries.

This module defines the following admin classes:
- CategoryAdmin: Configuration for the Category model in the admin interface.
- ItemAdmin: Configuration for the Item model in the admin interface.
- DeliveryAdmin: Configuration for the Delivery model in the admin interface.
"""

from django.contrib import admin
from .models import Category, Item, Delivery,ImageFile,DxfFile,UserPrint

@admin.decorators.register(ImageFile)
class ImageFileAdmin(admin.ModelAdmin):
    list_display =('name','image','date')
@admin.decorators.register(DxfFile)
class DxfFileAdmin(admin.ModelAdmin):
    list_display = ('type','date')
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Category model.
    """
    list_display = ('name', 'slug')
    search_fields = ('name',)
    ordering = ('name',)


class ItemAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Item model.
    """
    list_display = (
        'id', 'quantity', 'thickness',"date",'priority'
    )
    search_fields = ('id',)
    list_filter = ("id",)
    ordering = ('priority','date',)
@admin.decorators.register(UserPrint)
class UserPrintAdmin(admin.ModelAdmin):
    list_display = ('user','item')


class DeliveryAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Delivery model.
    """
    list_display = (
        'item', 'customer','date', 'is_delivered'
    )
    search_fields = ('item__name', 'customer__name')
    list_filter = ('is_delivered', 'date')
    ordering = ('-date',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Delivery, DeliveryAdmin)
