import json

from channels.generic.websocket import WebsocketConsumer


class GameConsumer(WebsocketConsumer):
    def connect(self):
        print(self.scope["user"].user.username + ' connected')
        self.accept()

    def disconnect(self, close_code):
        print(self.scope["user"].user.username + ' disconnected')

    def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        self.send(text_data=json.dumps({
            'result': 'ok'
        }))
