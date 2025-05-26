from django.db import models
from autoslug import AutoSlugField
from accounts.models import Supplier,MyUser,Employee,Customer
from django.utils import timezone
thickness_type = ((0.5,"0.5mm"),(0.6,"0.6mm"),(0.7,"0.7mm"),(0.8,"0.8mm"),
                 (0.9,"0.9mm"),(1.4,"1.4mm"),(1.8,"1.8mm"),(2.5,"2.5mm"),
                 (1.0,"1.0mm"),(1.1,"1.1mm"),(1.2,"1.2mm"),(3.0,"3.0mm"),
                 (0.91,"0.9mm(oversize)"),(1.11,"1.1mm(oversize)"),(1.21,"1.2mm(oversize)"),
                 (1.01,"1.0mm(oversize)"),(1.81,"1.8mm(oversize)"),(2.51,"2.5mm(oversize)"),
                 (1.41,"1.4mm(oversize)"))

class Thickness(models.Model):
    name = models.FloatField(max_length=250,unique=True,choices=thickness_type)
    added =models.IntegerField()
    removed =models.IntegerField()
    def __str__(self) -> str:
        return f"{self.get_name_display()}"
    class Meta:
        ordering = ['name']

class SingleMaterial(models.Model):
    thickness = models.ForeignKey(Thickness,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price =models.IntegerField()
    def __str__(self):
        return f"{self.id}-{self.thickness}"

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
    date = models.DateTimeField(default=timezone.datetime.now)
    class Meta:
        get_latest_by = 'date'
        ordering = ["-date"]
class InventoryPayment(models.Model):
    user = models.ForeignKey(MyUser,on_delete=models.SET_NULL,null=True)
    inventory = models.ForeignKey(InventoryMaterial,on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField(default=timezone.datetime.today)
class SaleryPayment(models.Model):
    date =models.DateField(auto_now_add=True)
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    bonus =models.IntegerField()
    total = models.IntegerField()
    class Meta:
        ordering = ['date']
class ClientPayment(models.Model):
    user =models.ForeignKey(MyUser,on_delete=models.SET_NULL,null=True,blank=True)
    date = models.DateField(auto_now_add=True)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    ammount = models.IntegerField()
    payment_method = models.CharField(max_length=150,choices=[('cash',"cash"),("transfer","transfer")])
    proof = models.ImageField(upload_to="proof/",blank=True,null=True)
class FreeAssets(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    ammount = models.IntegerField(default=0)
class Bill(models.Model):
    """Model representing a bill with various details and payment status."""

    slug = AutoSlugField(unique=True, populate_from='date')
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date (e.g., 2022/11/22)'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='What is the expense for'
    )
    amount = models.FloatField(
        verbose_name='Total Amount (Birr)',
        help_text='Total amount due for payment'
    )
    status = models.BooleanField(
        default=False,
        verbose_name='Paid',
        help_text='Payment status of the bill'
    )

    def __str__(self):
        return self.date


