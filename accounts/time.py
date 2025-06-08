from django.utils import timezone
def timechecker():
    hour = timezone.now()
    if(hour.hour < 6 or hour.hour > 0):
        return timezone.now() - timezone.timedelta(1)
    else:
        return timezone.now()
    
def datechecker():
    hour = timezone.now()
    if(hour.hour < 6 or hour.hour > 0):
        return timezone.datetime.today() - timezone.timedelta(1)
    else:
        return timezone.datetime.today()