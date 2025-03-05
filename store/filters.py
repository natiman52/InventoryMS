import django_filters
from .models import Item,DxfFile


def get_item_or_dxffile(item):
    dx = item[:2]
    if(dx == "It"):
        return Item.objects.get(id=item[3:])
    else:
        return DxfFile.objects.get(id=int(item[3:]))

