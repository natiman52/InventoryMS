from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
class HomeConsumer(WebsocketConsumer):
    def connect(self):
        group_name = 'default'
        try:
            group_name = self.scope['user'].role
        except:
            pass
        async_to_sync(self.channel_layer.group_add)(group_name,self.channel_name)
        self.accept()
    def disconnect(self,close_code):
        group_name = 'default'
        try:
            group_name =self.scope['user'].role
        except:
            pass
        async_to_sync(self.channel_layer.group_discard)(group_name,self.channel_name)
        self.close()
    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)('test',{"type":"test.message","message":"message"})
    def send_notification(self,event):
        self.send(text_data=json.dumps({"message": "message"}))