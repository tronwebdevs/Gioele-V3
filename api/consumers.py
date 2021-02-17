import json
import time
import uuid
import threading
from random import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser

from .exceptions import GameException
from .game import Giorgio, PowerUp, POWERUPS_LAST_TIME

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

DELAY_BETWEEN_ENEMIES_GENERATIONS = 5

def run_generator(giorgio, channel_name):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_name, {
        'type': 'run_generation'
    })
    # DEBUG
    print('[%s/%s][INFO][Giorgio] Sent request to generate entities' % (threading.get_ident(), 'run_generator'))
    # /DEBUG
    if giorgio.running:
        threading.Timer(DELAY_BETWEEN_ENEMIES_GENERATIONS, run_generator, (giorgio,channel_name,)).start()

def run_powerup_expirer(channel_name, powerup_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_name, {
        'type': 'expire_powerup',
        'powerup_id': powerup_id
    })
    # DEBUG
    print('[%s/%s][INFO][Giorgio] Sent request to expire powerup %i' % (threading.get_ident(), 'run_generator', powerup_id))
    # /DEBUG


class GameConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        if type(user) is AnonymousUser:
            # DEBUG
            print('[%s/%s][WARNING][WebSocket] Unauthenticated user' % (threading.get_ident(), 'connect'))
            # /DEBUG
            self.close()
            return
        # DEBUG
        print('[%s/%s][INFO][WebSocket] %s connected, starting giorgio' % (threading.get_ident(), 'connect', user.user.username))
        # /DEBUG
        self.scope['giorgio'] = Giorgio(
            user=user,
            visit_id=uuid.UUID('19488172-d2fe-4025-a273-08803c4664ad'),
            abilities=user.inventory.abilities,
            main_gun_id=user.main_gun,
            side_gun_id=user.side_gun,
            skin_id=user.skin
        )
        self.gen_channel_name = 'gen_%i_%i' % (user.user.id, round(random() * 1000))
        self.pu_channel_name = 'pu_%i_%i' % (user.user.id, round(random() * 1000))
        async_to_sync(self.channel_layer.group_add)(
            self.gen_channel_name,
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_add)(
            self.pu_channel_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        user = self.scope['user']
        giorgio = self.scope.get('giorgio')
        if type(user) is not AnonymousUser:
            if giorgio is not None and giorgio.running == True:
                giorgio.running = False
                # giorgio.end_game()
            # DEBUG
            print('[%s/%s][INFO][WebSocket] %s disconnected' % (threading.get_ident(), 'disconnect', user.user.username))
            # /DEBUG

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
                run_generator(self.scope['giorgio'], self.gen_channel_name)
                response = { 'r': 0, 'm': 'ok' }
                # DEBUG
                print('[%s/%s][INFO][Giorgio] Game started' % (threading.get_ident(), 'executor'))
                # /DEBUG
            except Exception as e:
                raise GameException(str(e))
        elif giorgio is not None and giorgio.running == True:
            if action > 2:
                # Check if given entity's id is valid and get entity object from stack
                entity = self.get_entity(action, entity_id)
            # Switch between actions
            if action == ACTION_GAME_PAUSE:
                giorgio.pause_game()
                response = { 'r': 0, 'm': 'ok' }
            elif action == ACTION_GAME_STOP:
                giorgio.end_game()
                response = { 'r': 0, 'm': 'ok' }
            elif action == ACTION_ENEMY_HIT_PLAYER_DIR:
                player = giorgio.enemy_hit_player(entity, True)
            elif action == ACTION_ENEMY_HIT_PLAYER_IND:
                player = giorgio.enemy_hit_player(entity, False)
            elif action == ACTION_ENEMY_HIT_MSHIP:
                mship_lifes = giorgio.enemy_hit_mship(entity)
                response = { 'r': 2, 'lifes': mship_lifes }
            elif action == ACTION_PLAYER_HIT_ENEMY:
                # Check if given gun's type is valid
                gun_type = data.get('t')
                if type(gun_type) is not int or gun_type < 0 or gun_type > 1 or (gun_type == 1 and giorgio.player.side_gun is None):
                    raise GameException('Invalid data (t)')
                entity = giorgio.player_hit_enemy(gun_type, entity)
                response = vars(entity)
            elif action == ACTION_PLAYER_GAIN_POWERUP:
                player = giorgio.player_gain_powerup(entity)
                if entity.type != PowerUp.TYPES['shield']:
                    threading.Timer(POWERUPS_LAST_TIME, run_powerup_expirer, args=(self.pu_channel_name, entity.id)).start()
            elif action == ACTION_PLAYER_USE_ABILITY:
                player = giorgio.player_use_ability(entity)
            else:
                raise GameException('Invalid action', ERROR_INVALID_ACTION)
        else:
            raise GameException("Game hasn't started", ERROR_GAME_NOT_STARTED)
        if response is None:
            response = {
                'r': 1,
                'player': player.get_displayable()
            }
        # DEBUG
        print('[%s/%s][INFO][WebSocket] Sending response (action:%i)' % (threading.get_ident(), 'executor', action))
        # /DEBUG
        self.send_dict(response)

    def receive(self, text_data):
        try:
            data, action, entity_id = self.validate_data(text_data)
            self.execute(action, data, self.scope['giorgio'], self.scope['user'], entity_id)
        except Exception as e:
            self.send_error(e)
            return

    def run_generation(self, event):
        giorgio = self.scope['giorgio']
        if giorgio.running:
            # DEBUG
            print('[%s/%s][INFO][Giorgio] Generating entities' % (threading.get_ident(), 'run_generation'))
            # /DEBUG
            # Run algorithm witch generates entities
            giorgio.generate_entities()

            # Transform dicts into json-friendly lists
            enemies = list(map(vars, giorgio.enemies.values()))
            powerups = list(map(vars, giorgio.powerups.values()))
            # Send to client updated entity lists
            # DEBUG
            print('[%s/%s][INFO][WebSocket] Sending updated entities' % (threading.get_ident(), 'run_generation'))
            # /DEBUG
            self.send_dict({
                'r': 3,
                'enemies': enemies,
                'powerups': powerups
            })

    def expire_powerup(self, event):
        giorgio = self.scope['giorgio']
        if giorgio.running:
            powerup_id = event['powerup_id']
            # DEBUG
            print('[%s/%s][INFO][Giorgio] Expiring powerup #%i' % (threading.get_ident(), 'run_generation', powerup_id))
            # /DEBUG
            player = giorgio.player
            powerup = player.active_powerups.get(powerup_id)
            if powerup is not None:
                del player.active_powerups[powerup.id]
                player.expired_powerups.add(powerup.type)
            # DEBUG
            print('[%s/%s][INFO][WebSocket] Sending updated powerups' % (threading.get_ident(), 'expire_powerup'))
            # /DEBUG
            self.send_dict({
                'r': 1,
                'player': player.get_displayable()
            })
