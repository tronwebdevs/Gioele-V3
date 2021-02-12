import json
import uuid

from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from .game import Game


class GameConsumer(WebsocketConsumer):

    def connect(self):
        if type(self.scope["user"]) is AnonymousUser:
            print('Unauthenticated user')
            self.disconnect(1008)
            return
        print(self.scope["user"].user.username + ' connected')
        self.scope["game"] = None
        self.accept()

    def disconnect(self, close_code):
        if type(self.scope["user"]) is not AnonymousUser:
            if self.scope["game"] is not None:
                self.scope["game"].save(uuid.UUID("5c9539b514a9442ab5e14ae6ec50ccdb"))
            print(self.scope["user"].user.username + ' disconnected')

    def validate_data(self, text_data):
        data = json.loads(text_data)
        if 'a' not in data:
            raise Exception('Invalid data (no a)')
        if type(data['a']) is not int or data['a'] < 0 or data['a'] > 10:
            raise Exception('Invalid data (a)')
        return data, data['a']

    def send_error(self, message, code=-1):
        self.send(text_data=json.dumps({
            'code': code,
            'message': message
        }))

    def receive(self, text_data):
        try:
            data, action = self.validate_data(text_data)
        except Exception as e:
            self.send_error(str(e))
            return
        game = self.scope["game"]
        """
        'a': action type, possible values:
            - 0: game start
            - 1: game stop
            - 5: bullet shooted
            - 10: enemy hit
        """
        
        if action == 0 and game is None:
            try:
                self.scope["game"] = Game(
                    self.scope["user"].user.id,
                    'yAiL',
                    'oBkq'
                )
                print('Game started')
            except Exception as e:
                self.send_error(str(e))
        elif game is not None:
            if action == 1:
                # TODO: game stopped, store on db
                pass
            elif action == 5:
                if data['t'] == 0:
                    game.shooted_main += 1
                    print(f'Shooted main: {game.shooted_main}')
                elif data['t'] == 1:
                    game.shooted_side += 1
                    print(f'Shooted side: {game.shooted_side}')
            elif action == 10:
                # TODO: check if enemy has been killed and act accordingly
                pass
            else:
                self.send_error('Invalid action')
        else:
            self.send_error('Game hasn\'t started')
