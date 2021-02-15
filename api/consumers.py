import json
import uuid
import sched
from multiprocessing import Process

from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from .exceptions import GameException
from .game import Giorgio

ACTION_GAME_START = 0
ACTION_GAME_PAUSE = 1
ACTION_GAME_STOP = 2
ACTION_ENEMY_HIT_PLAYER_DIR = 3
ACTION_ENEMY_HIT_PLAYER_IND = 4
ACTION_ENEMY_HIT_MSHIP = 5
ACTION_PLAYER_HIT_ENEMY = 6
ACTION_PLAYER_GAIN_POWERUP = 7
ACTION_PLAYER_USE_ABILITY = 8

ERROR_INVALID_ACTION = 1
ERROR_GAME_NOT_STARTED = 2
ERROR_GAME_ALREADY_STARTED = 3
ERROR_ENTITY_NOT_FOUND = 4

DELAY_BETWEEN_ENEMIES_GENERATIONS = 2

def run_giogio_generator(scheduler, giorgio, socket):
    # print(vars(giorgio))
    giorgio.generate_entities(socket)
    if giorgio.running == True:
        scheduler.enter(
            DELAY_BETWEEN_ENEMIES_GENERATIONS, 1,
            run_giogio_generator,
            argument=(scheduler, giorgio, socket,)
        )


class GameConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        if type(user) is AnonymousUser:
            print('Unauthenticated user')
            self.disconnect(1008)
            return
        print(user.user.username + ' connected, starting giorgio')
        self.scope['giorgio'] = Giorgio(
            user=user,
            visit_id=uuid.UUID('19488172-d2fe-4025-a273-08803c4664ad'),
            abilities=user.inventory.abilities,
            main_gun_id=user.main_gun,
            side_gun_id=user.side_gun,
            skin_id=user.skin
        )
        self.accept()

    def disconnect(self, close_code):
        if type(self.scope['user']) is not AnonymousUser:
            if self.scope['giorgio'] is not None:
                self.scope['giorgio'].end_game()
            print(self.scope['user'].user.username + ' disconnected')

    def validate_data(self, text_data):
        data = json.loads(text_data)
        action = data.get('a')
        if type(action) is not int or action < 0 or action > 8:
            raise Exception('Invalid data (a)')
        _id = None
        if action > 2:
            _id = data.get('i')
            if type(_id) is not int:
                raise Exception('Invalid data (i)')
        return data, action, _id

    def send_dict(self, val):
        self.send(text_data=json.dumps(val))

    def send_error(self, exception):
        code = -1
        if 'code' in vars(exception):
            code = exception.code
        self.send_dict({
            'code': code,
            'message': str(exception)
        })

    def get_entity(self, action, eid):
        exception = GameException('Entity not found', ERROR_ENTITY_NOT_FOUND)
        giorgio = self.scope['giorgio']
        if action < 7:
            # Entity is an enemy
            entity = giorgio.enemies.get(eid)
        elif action == 7:
            # Entity is a powerup
            entity = giorgio.powerups.get(eid)
        elif action == 8:
            # Entity is an ability
            entity = None #giorgio.player.abilites.get(eid)
        else:
            raise exception
        
        if entity is None:
            raise exception
        return entity

    def execute(self, action, data, giorgio, user, entity_id):
        response = None
        if action == ACTION_GAME_START:
            if giorgio.running == True:
                raise GameException('Game already started', ERROR_GAME_ALREADY_STARTED)
            try:
                self.scope['giorgio'].start_game()
                self.scope['generator'] = sched.scheduler()
                self.scope['generator'].enter(
                    DELAY_BETWEEN_ENEMIES_GENERATIONS,
                    1,
                    run_giogio_generator,
                    argument=(self.scope['generator'], self.scope['giorgio'], self)
                )
                Process(target=self.scope['generator'].run)
                response = { 'm': 'ok' }
                print('Game started')
            except Exception as e:
                raise GameException(str(e))
        elif giorgio is not None and giorgio.running == True:
            if action > 2:
                # Check if given entity's id is valid and get entity object from stack
                entity = self.get_entity(action, entity_id)
            # Switch between actions
            if action == ACTION_GAME_PAUSE:
                giorgio.pause_game()
                response = { 'm': 'ok' }
            elif action == ACTION_GAME_STOP:
                giorgio.end_game()
                response = { 'm': 'ok' }
            elif action == ACTION_ENEMY_HIT_PLAYER_DIR:
                player = giorgio.enemy_hit_player(entity, True)
            elif action == ACTION_ENEMY_HIT_PLAYER_IND:
                player = giorgio.enemy_hit_player(entity, False)
            elif action == ACTION_ENEMY_HIT_MSHIP:
                mship_lifes = giorgio.enemy_hit_mship(entity)
                response = { 'lifes': mship_lifes }
            elif action == ACTION_PLAYER_HIT_ENEMY:
                # Check if given gun's type is valid
                gun_type = data.get('t')
                if type(gun_type) is not int or gun_type < 0 or gun_type > 1 or (gun_type == 1 and giorgio.player.side_gun is None):
                    raise GameException('Invalid data (t)')
                entity = giorgio.player_hit_enemy(gun_type, entity)
                response = vars(entity)
            elif action == ACTION_PLAYER_GAIN_POWERUP:
                player = giorgio.player_gain_powerup(entity)
            elif action == ACTION_PLAYER_USE_ABILITY:
                player = giorgio.player_use_ability(entity)
            else:
                raise GameException('Invalid action', ERROR_INVALID_ACTION)
        else:
            raise GameException("Game hasn't started", ERROR_GAME_NOT_STARTED)
        if response is None:
            response = player.get_displayable()
        self.send_dict(response)

    def receive(self, text_data):
        try:
            data, action, entity_id = self.validate_data(text_data)
            self.execute(action, data, self.scope['giorgio'], self.scope['user'], entity_id)
        except Exception as e:
            self.send_error(e)
            return
