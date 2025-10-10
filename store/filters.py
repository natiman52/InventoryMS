from .models import Item,DxfFile
from django.utils import timezone
def get_item_or_dxffile(item):
    dx = item[:2]
    if(dx == "It"):
        return Item.objects.get(id=item[3:],verif_design="A")
    else:
        return DxfFile.objects.get(id=int(item[3:]))
#3 5-3 and 5-(5-3) or  2-3 and 2-(-1) 
def get_date_specfic(dayWeek):
        now = timezone.now()
        now = now - timezone.timedelta(days=(now.isoweekday() - dayWeek))
        date_time2 =now.replace(hour=0,minute=0,second=0) + timezone.timedelta(hours=23,minutes=59)
        return [now.replace(hour=0,minute=0,second=0),date_time2]