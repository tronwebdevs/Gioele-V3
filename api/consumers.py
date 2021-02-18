import json
import threading
import time
import uuid
from random import random

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser

from .exceptions import GameDataException, GameException
from .game import POWERUPS_LAST_TIME, DELAY_BETWEEN_ENEMIES_GENERATIONS, POWERUP_TYPES
from .giorgio import Giorgio
from .utils import log as DEBUG

ACTION_GAME_START = 0
ACTION_GAME_PAUSE = 1
ACTION_GAME_STOP = 2
ACTION_ENEMY_HIT_PLAYER_DIR = 3
ACTION_ENEMY_HIT_PLAYER_IND = 4
ACTION_ENEMY_HIT_MSHIP = 5
ACTION_PLAYER_HIT_ENEMY = 6
ACTION_PLAYER_GAIN_POWERUP = 7
ACTION_PLAYER_USE_ABILITY = 8

def generation_worker(giorgio, channel_name):
    channel_layer = get_channel_layer()
    DEBUG('run_generator', 'Giorgio', 'Sending request to generate entities')
    async_to_sync(channel_layer.group_send)(channel_name, {
        'type': 'run_generation'
    })
    if giorgio.running:
        threading.Timer(
            DELAY_BETWEEN_ENEMIES_GENERATIONS,
            generation_worker,
            (giorgio,channel_name,)
        ).start()

def powerup_expire_worker(channel_name, powerup_id):
    channel_layer = get_channel_layer()
    DEBUG('run_generator', 'Giorgio', ('Sending request to expire powerup #%i' % powerup_id))
    async_to_sync(channel_layer.group_send)(channel_name, {
        'type': 'expire_powerup',
        'powerup_id': powerup_id
    })


class GameConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        if type(user) is AnonymousUser:
            DEBUG('connect', 'WebSocket', 'Unauthenticated user', ltype='WARGING')
            self.close()
            return
        self.scope['giorgio'] = Giorgio(
            user=user,
            visit_id=uuid.UUID('19488172-d2fe-4025-a273-08803c4664ad'),
            abilities=user.inventory.abilities,
            main_gun_id=user.main_gun,
            side_gun_id=user.side_gun,
            skin_id=user.skin
        )
        DEBUG('connect', 'WebSocket', ('%s connected, giorgio started (%s)' % (user.user.username, self.scope["giorgio"].game_id)))
        self.delayed_channel_name = 'giorgio_%i_%i' % (user.user.id, round(random() * 1000))
        async_to_sync(self.channel_layer.group_add)(
            self.delayed_channel_name,
            self.channel_name
        )
        DEBUG('connect', 'WebSocket', 'Channel for delayed comunications created')
        self.accept()

    def disconnect(self, close_code):
        user = self.scope['user']
        giorgio = self.scope.get('giorgio')
        if type(user) is not AnonymousUser:
            if giorgio is not None and giorgio.running == True:
                giorgio.running = False
                # giorgio.end_game()
            DEBUG('disconnect', 'WebSocket', ('%s disconnected' % user.user.username))

    def validate_data(self, text_data):
        data = json.loads(text_data)
        action = data.get('a')
        if type(action) is not int or action < 0 or action > 8:
            raise GameDataException('a')
        _id = None
        if action > 2:
            _id = data.get('i')
            if type(_id) is not int:
                raise GameDataException('i')
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
        giorgio = self.scope['giorgio']
        dataset = None
        if action < 7:
            # Entity is an enemy
            dataset = giorgio.enemies
        elif action == 7:
            # Entity is a powerup
            dataset = giorgio.powerups
        elif action == 8:
            # Entity is an ability
            dataset = giorgio.player.abilites
        
        if dataset is None:
            raise GameException('Entity not found', GameException.ENTITY_NOT_FOUND)
        return dataset.get(eid)

    def execute(self, action, data, giorgio, user, entity_id):
        response = None
        if action == ACTION_GAME_START:
            if giorgio.running == True:
                raise GameException('Game already started', GameException.GAME_ALREADY_STARTED)
            try:
                self.scope['giorgio'].start_game()
                generation_worker(self.scope['giorgio'], self.delayed_channel_name)
                response = { 'r': 0, 'm': 'ok' }
                DEBUG('execute', 'Giorgio', 'Game started')
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
                if type(gun_type) is not int \
                    or gun_type < 0 or gun_type > 1 \
                    or (gun_type == 1 and giorgio.player.side_gun is None):
                    raise GameDataException('t')
                entity = giorgio.player_hit_enemy(gun_type, entity)
                response = vars(entity)
            elif action == ACTION_PLAYER_GAIN_POWERUP:
                player = giorgio.player_gain_powerup(entity)
                if entity.type != POWERUP_TYPES['shield'][0]:
                    threading.Timer(
                        POWERUPS_LAST_TIME,
                        powerup_expire_worker,
                        (self.delayed_channel_name, entity.id,)
                    ).start()
            elif action == ACTION_PLAYER_USE_ABILITY:
                player = giorgio.player_use_ability(entity)
            else:
                raise GameException('Invalid action', GameException.INVALID_ACTION)
        else:
            raise GameException("Game hasn't started", GameException.GAME_NOT_STARTED)
        if response is None:
            response = {
                'r': 1,
                'player': player.get_displayable()
            }
        DEBUG('execute', 'WebSocket', ('Sending response (action: %i)' % action))
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
            DEBUG('run_generation', 'Giorgio', 'Generating entities')
            # Run algorithm witch generates entities and get result
            new_enemies, new_powerups = giorgio.generate_entities()
            new_enemies = list(map(vars, new_enemies))
            new_powerups = list(map(vars, new_powerups))
            DEBUG('run_generation', 'WebSocket', 'Sending generated entities')
            # Send to client generated entity lists
            self.send_dict({
                'r': 3,
                'enemies': new_enemies,
                'powerups': new_powerups
            })
        else:
            DEBUG('run_generation', 'WebSocket', 'Generation prevented as the game is stopped')

    def expire_powerup(self, event):
        giorgio = self.scope['giorgio']
        if giorgio.running:
            powerup_id = event['powerup_id']
            DEBUG('expire_powerup', 'Giorgio', ('Expiring powerup #%i' % powerup_id))
            player = giorgio.player
            powerup = player.active_powerups.get(powerup_id)
            if powerup is not None:
                del player.active_powerups[powerup.id]
                player.expired_powerups.add(powerup.type)
            DEBUG('expire_powerup', 'WebSocket', 'Sending expired powerups')
            self.send_dict({
                'r': 1,
                'player': player.get_displayable()
            })
        else:
            DEBUG('run_generation', 'WebSocket', 'Expiration prevented as the game is stopped')
