from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import InventoryMaterial
from django.utils import timezone


@receiver(pre_save,sender=InventoryMaterial)
def ChangeId(sender,instance,**kwargs):
        # first 2 months 2 days
        if(not InventoryMaterial.objects.filter(id=instance.id).exists()):
            date_month = timezone.now().date().strftime('%b')
            month = str(date_month[0] + date_month[1])
            day = ''
            if timezone.now().date().day < 10:
                day = f'0{timezone.now().date().day}'
            else:
                day = timezone.now().date().day
            try:
                bill =InventoryMaterial.objects.latest()
                if(f"{bill.id[-8]}{bill.id[-7]}{bill.id[-6]}{bill.id[-5]}" != (str(month).upper() + str(day))): 
                    last_no = "01"
                else:
                    last_no =int(InventoryMaterial.objects.latest().id[-2] + InventoryMaterial.objects.latest().id[-1])
                    if((last_no + 1) < 10 ):
                        last_no = f'0{last_no + 1}'
            except:
                 last_no = "01"
            client = f"{instance.supplier.name[0] + instance.supplier.name[1]}".upper()
            instance.id = "MR" + str(month).upper() + str(day) + f'{client}{last_no}'
