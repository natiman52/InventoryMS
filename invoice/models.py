from django.db import models
from django_extensions.db.fields import AutoSlugField
from store.models import Item
from django.utils import timezone
from .calc import get_opertional_cost,total_opertional_cost,get_count_of_lamera
class Invoice(models.Model):

    slug = AutoSlugField(unique=True, populate_from='date')
    date = models.DateTimeField(default=timezone.now,verbose_name='Date (e.g., 2022/11/22)')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    sheet_metal_cost =models.IntegerField()
    dimensions =models.CharField(max_length=255,blank=True)
    quantity = models.IntegerField()
    scrap_type =models.CharField(max_length=255,choices=(('No','No'),("Used",'User'),("Clean","Clean")),blank=True)
    scrap_value =models.FloatField(default=0)
    unit_price = models.FloatField()
    total = models.FloatField(blank=True)
    gross_revenue = models.FloatField(blank=True)
    gross_cost =models.FloatField(blank=True)
    gross_profit=models.FloatField(blank=True)
    opertional_cost = models.FloatField(blank=True)
    net_profit = models.FloatField(blank=True)
    def save(self, *args, **kwargs):

        self.total = round(self.quantity * self.unit_price, 2)
        self.gross_revenue = round(self.total + (self.scrap_value * self.quantity), 2)
        self.gross_cost =round(self.sheet_metal_cost * self.quantity,2)
        self.gross_profit =round(self.gross_revenue - self.gross_cost,2)
        self.opertional_cost = (total_opertional_cost(get_opertional_cost(self.item.date))) / get_count_of_lamera(Item.objects.filter(date__date=self.item.date))[1]
        self.net_profit = self.gross_profit - self.opertional_cost
        return super().save(*args, **kwargs)

    def __str__(self):
        """
        Return the invoice's slug.
        """
        return self.slug
