from django.urls import re_path,path
from .consumer import HomeConsumer
websocket_urlpatterns = [
    re_path(r"ws/notification-count",HomeConsumer.as_asgi())
]