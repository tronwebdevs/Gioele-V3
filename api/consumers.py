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
from .game.constants import POWERUPS_LAST_TIME, DELAY_BETWEEN_ENEMIES_GENERATIONS
from .game.powerups import POWERUP_TYPES
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

RESPONSE_GAME_RELATED = 0
RESPONSE_PLAYER_OBJECT = 1
RESPONSE_MSHIP_LIFES = 2
RESPONSE_GENERATED_ENTITIES = 3
RESPONSE_ENEMY_OBJECT = 4

def generation_worker(giorgio, channel_name):
    channel_layer = get_channel_layer()
    DEBUG('Giorgio', 'Sending request to generate entities')
    async_to_sync(channel_layer.group_send)(channel_name, {
        'type': 'run_generation'
    })
    # d = (5000 + 400 * (k - 1)) milliseconds
    delay = DELAY_BETWEEN_ENEMIES_GENERATIONS + (4 * (giorgio.round - 1)) / 10
    if giorgio.running:
        threading.Timer(
            delay,
            generation_worker,
            (giorgio,channel_name,)
        ).start()

def powerup_expire_worker(channel_name, powerup_id):
    channel_layer = get_channel_layer()
    DEBUG('Giorgio', ('Sending request to expire powerup #%i' % powerup_id))
    async_to_sync(channel_layer.group_send)(channel_name, {
        'type': 'expire_powerup',
        'powerup_id': powerup_id
    })


class GameConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        if type(user) is AnonymousUser:
            DEBUG('WebSocket', 'Unauthenticated user', ltype='WARGING')
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
        DEBUG('WebSocket', ('"%s" connected, giorgio started' % user.user.username))
        self.delayed_channel_name = 'giorgio_%i_%i' % (user.user.id, round(random() * 1000))
        async_to_sync(self.channel_layer.group_add)(
            self.delayed_channel_name,
            self.channel_name
        )
        DEBUG('WebSocket', 'Channel for delayed comunications created (%s)' % self.delayed_channel_name)
        self.accept()

    def disconnect(self, close_code):
        user = self.scope['user']
        giorgio = self.scope.get('giorgio')
        if type(user) is not AnonymousUser:
            if giorgio is not None and giorgio.running == True:
                giorgio.running = False
                # giorgio.end_game()
            DEBUG('WebSocket', ('%s disconnected' % user.user.username))

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
            'c': code,
            'm': str(exception)
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
        
        if dataset is None or dataset.get(eid) is None:
            raise GameException('Entity not found', GameException.ENTITY_NOT_FOUND)
        return dataset[eid]

    def execute(self, action, data, giorgio, user, entity_id):
        response = None
        if action == ACTION_GAME_START:
            if giorgio.running == True:
                raise GameException('Game already started', GameException.GAME_ALREADY_STARTED)
            try:
                self.scope['giorgio'].start_game()
                generation_worker(self.scope['giorgio'], self.delayed_channel_name)
                response = {
                    'r': RESPONSE_GAME_RELATED,
                    'm': 'ok'
                }
                DEBUG('Giorgio', 'Game started (%s)' % self.scope['giorgio'].game_id)
            except Exception as e:
                raise GameException(str(e))
        elif giorgio is not None and giorgio.running == True:
            if action > 2:
                # Check if given entity's id is valid and get entity object from stack
                entity = self.get_entity(action, entity_id)
            # Switch between actions
            if action == ACTION_GAME_PAUSE:
                giorgio.pause_game()
                response = {
                    'r': RESPONSE_GAME_RELATED,
                    'm': 'ok'
                }
            elif action == ACTION_GAME_STOP:
                giorgio.end_game()
                response = {
                    'r': RESPONSE_GAME_RELATED,
                    'm': 'ok'
                }
            elif action == ACTION_ENEMY_HIT_PLAYER_DIR:
                player = giorgio.enemy_hit_player(entity, True)
            elif action == ACTION_ENEMY_HIT_PLAYER_IND:
                player = giorgio.enemy_hit_player(entity, False)
            elif action == ACTION_ENEMY_HIT_MSHIP:
                mship_lifes = giorgio.enemy_hit_mship(entity)
                response = {
                    'r': RESPONSE_MSHIP_LIFES,
                    'lifes': mship_lifes
                }
            elif action == ACTION_PLAYER_HIT_ENEMY:
                # Check if given gun's type is valid
                gun_type = data.get('g')
                if type(gun_type) is not int \
                    or gun_type < 0 or gun_type > 1 \
                    or (gun_type == 1 and giorgio.player.side_gun is None):
                    raise GameDataException('g')
                entity = giorgio.player_hit_enemy(gun_type, entity)
                response = {
                    'r': RESPONSE_ENEMY_OBJECT,
                    'enemy': entity.get_displayable()
                }
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
                'r': RESPONSE_PLAYER_OBJECT,
                'player': player.get_displayable()
            }
        DEBUG('WebSocket', ('Sending response (action: %i)' % action))
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
            DEBUG('Giorgio', 'Generating entities')
            # Run algorithm witch generates entities and get result
            gen_enemies, gen_powerups = giorgio.generate_entities()
            gen_enemies = list(map(lambda e: e.get_displayable(), gen_enemies))
            gen_powerups = list(map(lambda p: p.get_displayable(), gen_powerups))
            DEBUG('WebSocket', 'Sending generated entities')
            # Send to client generated entity lists
            self.send_dict({
                'r': RESPONSE_GENERATED_ENTITIES,
                'enemies': gen_enemies,
                'powerups': gen_powerups
            })
        else:
            DEBUG('WebSocket', 'Generation prevented as the game is stopped')

    def expire_powerup(self, event):
        giorgio = self.scope['giorgio']
        if giorgio.running:
            powerup_id = event['powerup_id']
            DEBUG('Giorgio', ('Expiring powerup #%i' % powerup_id))
            player = giorgio.player
            powerup = player.active_powerups.get(powerup_id)
            if powerup is not None:
                del player.active_powerups[powerup.id]
                player.expired_powerups.add(powerup.type)
            DEBUG('WebSocket', 'Sending expired powerups')
            self.send_dict({
                'r': RESPONSE_PLAYER_OBJECT,
                'player': player.get_displayable()
            })
        else:
            DEBUG('WebSocket', 'Expiration prevented as the game is stopped')
