"""
Module: models.py

Contains Django models for handling categories, items, and deliveries.

This module defines the following classes:
- Category: Represents a category for items.
- Item: Represents an item in the inventory.
- Delivery: Represents a delivery of an item to a customer.

Each class provides specific fields and methods for handling related data.
"""

from django.db import models
from django.urls import reverse
from django.forms import model_to_dict
from django_extensions.db.fields import AutoSlugField
from accounts.models import Customer,MyUser
from bills.models import Thickness
import os
from django.db.models import Value
thickness_type = ((0.5,"0.5mm"),(0.7,"0.7mm"),(0.8,"0.8mm"),
                 (0.9,"0.9mm"),(1.0,"1.0mm"),(1.1,"1.1mm"),
                 (1.4,"1.4mm"),(1.8,"1.8mm"),
                  (2.5,"2.5mm"),(3.0,"3.0mm"))
class DxfFile(models.Model):
    date=models.DateField(auto_now_add=True)
    dxf_file = models.FileField(upload_to="manual/dxf")
    type = models.CharField(max_length=256,choices=(('DR',"Door (bere)"),("BL",'Balkeni (berenda)'),("ST","stairs"),("OT","Other")))
    def __str__(self):
        return f"{self.type} {self.id}"
    def filename(self):
        return os.path.basename(self.dxf_file.name).split('.')[0]
class ImageFile(models.Model):
    name = models.CharField(max_length=100,blank=True)
    date=models.DateField(auto_now=True)
    image = models.FileField(upload_to="manual/image")
    type = models.CharField(max_length=256,choices=(('DR',"Door (bere)"),("BL",'Balkeni (berenda)'),("ST","stairs"),("OT","Other")))

    def filename(self):
        return os.path.basename(self.image.name).split('.')[0]
class Category(models.Model):
    """
    Represents a category for items.
    """
    name = models.CharField(max_length=50)
    slug = AutoSlugField(unique=True, populate_from='name')

    def __str__(self):
        """
        String representation of the category.
        """
        return f"Category: {self.name}"

    class Meta:
        verbose_name_plural = 'Categories'
def uploadTo(instance,model):
    return f"item/images/{instance.client.name}" + model
def uploadDXFTo(instance,model):
    return f"item/DXF/{instance.client.name}/" + model


class DXFOrder(models.Model):
    quantity = models.IntegerField(default=1)
    dxf_file = models.FileField(upload_to="manual/dxf")
    date = models.DateTimeField(auto_now_add=True)

class Item(models.Model):
    """
    Represents an item in the inventory.
    """
    id = models.CharField(max_length=250,unique=True,primary_key=True)
    user = models.ForeignKey(MyUser,on_delete=models.SET_NULL,null=True)
    image1 =models.ImageField('image 1',upload_to=uploadTo) 
    image2 =models.ImageField('image 2',upload_to=uploadTo,blank=True) 
    image3=models.ImageField("image 3",upload_to=uploadTo,blank=True)
    thickness=models.ForeignKey(Thickness,on_delete=models.SET_NULL,null=True)
    dimensions_type = models.CharField(max_length=256,choices=(('square','square'),('rectangular',"rectangular"),('other','other')))
    diminsions= models.CharField(max_length=256,blank=True,null=True)
    dimensions_info = models.TextField(blank=True,null=True)
    dimensions_image=models.ImageField(blank=True,null=True)
    client = models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True)
    priority = models.CharField(choices=(("H","High"),("S","Sequence")),max_length=256)
    remark = models.TextField(max_length=256)
    quantity = models.IntegerField(default=1)
    verif_price = models.CharField(max_length=256,choices=(("P","pending"),('A',"Accepted"),("D","Declined"),("W","Waiting")),default="W")
    verif_design = models.CharField(max_length=256,choices=(("P","pending"),('A',"Accepted"),("D","Declined"),('W',"Waiting")),default="W")
    price=models.IntegerField(blank=True,null=True) 
    dxf_file = models.FileField('dxf',upload_to=uploadDXFTo,blank=True,null=True)
    date = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    start = models.DateTimeField(blank=True,null=True)
    finish = models.DateTimeField(blank=True,null=True)
    type = models.CharField(max_length=256,choices=(('DR',"Door (bere)"),("BL",'Balkeni (berenda)'),("ST","stairs"),("OT","Other")))
    subclassed = models.BooleanField(default=False)
    def __str__(self):
        """
        String representation of the item.
        """
        return (
            f"{self.client}  "
            f"{self.id}"
        )
    def checkname(self,value):
        return bool(self.dxf_file.name) and self.dxf_file.storage.exists(value)
    def filename(self):
        return os.path.basename(self.dxf_file.name).split('.')[0]

    def get_absolute_url(self):
        """
        Returns the absolute URL for an item detail view.
        """
        return reverse('item-detail', kwargs={'slug': self.id})

    class Meta:
        ordering = ["priority",'date']
        verbose_name_plural = 'Items'
        get_latest_by = 'date'


class UserPrint(models.Model):
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=256)

class Delivery(models.Model):
    """
    Represents a delivery of an item to a customer.
    """
    user = models.ForeignKey(MyUser,null=True,on_delete=models.SET_NULL)
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(Customer,blank=True, null=True,on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False, verbose_name='Is Delivered')

    def __str__(self):
        """
        String representation of the delivery.
        """
        return (
            f"Delivery of {self.item} to {self.customer.name} "
            f"on {self.date}"
        )
