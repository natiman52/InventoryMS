from django.db import models
from autoslug import AutoSlugField
from accounts.models import Supplier
from accounts.models import MyUser
thickness_type = ((0.5,"0.5mm"),(0.7,"0.7mm"),(0.8,"0.8mm"),
                  (0.9,"0.9mm"),(0.9,"0.9mm"),(1.0,"1.0mm"),
                  (1.1,"1.1mm"),(1.4,"1.4mm"),(1.8,"1.8mm"),
                  (2.5,"2.5mm"),(3.0,"3.0mm"))
class SingleMaterial(models.Model):
    thickness = models.FloatField(choices=thickness_type)
    quantity = models.IntegerField()
    price =models.IntegerField()


class InventoryMaterial(models.Model):
    id =models.CharField(max_length=250,unique=True,primary_key=True)
    user = models.ForeignKey(MyUser,null=True,on_delete=models.SET_NULL)
    supplier = models.ForeignKey(Supplier,on_delete=models.SET_NULL,null=True)
    irons = models.ManyToManyField(SingleMaterial)
    total_cost =models.IntegerField()
    minsceus_cost = models.IntegerField()
    payment_method = models.CharField(max_length=256,choices=(("credit",'credit'),('cash','cash')))
    advance = models.IntegerField(null=True,blank=True)
    leftover =models.IntegerField(null=True,blank=True)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        get_latest_by = 'date'
        ordering = ["-date"]
class InventoryPayment(models.Model):
    user = models.ForeignKey(MyUser,on_delete=models.SET_NULL,null=True)
    inventory = models.ForeignKey(InventoryMaterial,on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField(auto_now=True)
class Bill(models.Model):
    """Model representing a bill with various details and payment status."""

    slug = AutoSlugField(unique=True, populate_from='date')
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date (e.g., 2022/11/22)'
    )
    institution_name = models.CharField(
        max_length=30,
        blank=False,
        null=False
    )
    phone_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Phone number of the institution'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text='Email address of the institution'
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Address of the institution'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Description of the bill'
    )
    payment_details = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text='Details of the payment'
    )
    amount = models.FloatField(
        verbose_name='Total Amount Owing (Ksh)',
        help_text='Total amount due for payment'
    )
    status = models.BooleanField(
        default=False,
        verbose_name='Paid',
        help_text='Payment status of the bill'
    )

    def __str__(self):
        return self.institution_name


