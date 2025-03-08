from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import ImageFile,Item
import os
from django.utils import timezone
@receiver(pre_save,sender=ImageFile)
def saveImageName(sender,instance,**kwargs):
    name =os.path.basename(instance.image.name).split('.')[0]
    instance.name = name


def ChangeId(instance):
        # first 2 months 2 days
        date_month = timezone.now().date().strftime('%b')
        month = str(date_month[0] + date_month[1])
        day = ''
        if timezone.now().date().day < 10:
            day = f'0{timezone.now().date().day}'
        else:
            day = timezone.now().date().day
        try:
            item=Item.objects.filter(id__contains=f"{str(month).upper()}{str(day)}").latest()
            if(f"{item.id[-9]}{item.id[-8]}{item.id[-7]}{item.id[-6]}" != (str(month).upper() + str(day))): 
                last_no = "001"
            else:
                last_no =int(item.id[-3] + item.id[-2] + item.id[-1])
                if((last_no + 1) < 10 ):
                    last_no = f'00{last_no + 1}'
                elif((last_no + 1) < 100):
                    last_no = f'0{last_no + 1}'
        except:
                last_no = "001"
        client = f"{instance.client.name[0] + instance.client.name[1]}".upper()
        instance.date_created = timezone.now()
        instance.id = str(month).upper() + str(day) + f'{client}{last_no}'
