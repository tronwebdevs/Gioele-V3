import json
import threading
import time
import uuid
import asyncio
from random import random

import aioredis
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser

from gioele_v3.settings import CHANNEL_LAYERS
from .exceptions import GameDataException, GameException, GameEndException
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

RESPONSE_ERROR = -1
RESPONSE_GAME_RELATED = 0
RESPONSE_PLAYER_OBJECT = 1
RESPONSE_MSHIP_LIFES = 2
RESPONSE_GENERATED_ENTITIES = 3
RESPONSE_ENEMY_OBJECT = 4
RESPONSE_GAME_ENDED = 5

WS_CLOSE_DEFAULT = 1001
WS_CLOSE_ERROR = 1008
WS_CLOSE_GAME_ENDED = 4001

redis_settings = CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]

def generation_worker(giorgio, channel_name):
    if giorgio.running:
        channel_layer = get_channel_layer()
        DEBUG('WebSocket', 'Sending request to generate entities')
        async_to_sync(channel_layer.group_send)(channel_name, {
            'type': 'run_generation'
        })
        # d = (base_delay + 400 * (k - 1)) milliseconds
        delay = DELAY_BETWEEN_ENEMIES_GENERATIONS + (4 * (giorgio.round - 1)) / 10

        if giorgio.gen_status == Giorgio.GENERATION_STATES['waiting']:
            DEBUG('WebSocket', 'Generation postponed')
            # Set delay to 4s
            delay = 4
    
        threading.Timer(
            delay,
            generation_worker,
            (giorgio,channel_name,)
        ).start()

def powerup_expire_worker(channel_name, powerup_id):
    channel_layer = get_channel_layer()
    DEBUG('WebSocket', ('Sending request to expire powerup #%i' % powerup_id))
    async_to_sync(channel_layer.group_send)(channel_name, {
        'type': 'expire_powerup',
        'powerup_id': powerup_id
    })


async def user_is_playing(channel_name):
    redis = await aioredis.create_redis_pool('redis://%s:%i' % (redis_settings[0], redis_settings[1]))
    result = await redis.exists('asgi:group:%s' % channel_name)
    redis.close()
    return result


# async def register_match(game_id, channel_id):
#     redis = await aioredis.create_redis_pool('redis://%s:%i' % (redis_settings[0], redis_settings[1]))
#     await redis.set('giorgio:games:%s' % game_id, channel_id)
#     redis.close()


# async def clear_match(game_id):
#     redis = await aioredis.create_redis_pool('redis://%s:%i' % (redis_settings[0], redis_settings[1]))
#     await redis.delete('giorgio:games:%s' % game_id)
#     redis.close()


class GameConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        if type(user) is AnonymousUser:

            DEBUG('WebSocket', 'Unauthenticated user', ltype='WARNING')

            self.close(WS_CLOSE_ERROR)
            return

        self.delayed_channel_name = 'giorgio_%i' % user.id
        self.scope['giorgio'] = None
        # Check if channel is already active thus the player is already playing
        if asyncio.run(user_is_playing(self.delayed_channel_name)):
            
            DEBUG('WebSocket', '"%s" is already playing' % user.username)

            self.close(WS_CLOSE_ERROR)
            return
        # Create giorgio
        self.scope['giorgio'] = Giorgio(
            user=user,
            visit_id=self.scope['visit_id'],
            abilities=user.inventory.abilities,
            main_gun=user.main_gun,
            side_gun=user.side_gun,
            skin=user.skin
        )

        DEBUG('WebSocket', ('"%s" connected, giorgio started' % user.username))

        # Generate channel name and add to Redis
        async_to_sync(self.channel_layer.group_add)(
            self.delayed_channel_name,
            self.channel_name
        )

        # asyncio.run(register_match(self.scope['giorgio'].game_id, self.delayed_channel_name))

        DEBUG('WebSocket', 'Channel for delayed comunications created (%s)' % self.delayed_channel_name)

        self.accept()

    def disconnect(self, close_code):
        user = self.scope['user']
        giorgio = self.scope.get('giorgio')
        if type(user) is not AnonymousUser:
            # Remove channel from Redis
            async_to_sync(self.channel_layer.group_discard)(
                self.delayed_channel_name,
                self.channel_name
            )

            # asyncio.run(clear_match(giorgio.game_id))

            if giorgio is not None and giorgio.running and close_code == WS_CLOSE_DEFAULT:
                # Game ended unexpectedly
                giorgio.end_game('connection closed', save=False)

            DEBUG('WebSocket', ('"%s" disconnected' % user.username))

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
            'r': RESPONSE_ERROR,
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
                self.send_dict({
                    'r': RESPONSE_PLAYER_OBJECT,
                    'player': self.scope['giorgio'].player.to_safe_dict(),
                })
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
                giorgio.end_game('received game stop command')
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
                    'enemy': entity.to_safe_dict()
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
                'player': player.to_safe_dict()
            }
        DEBUG('WebSocket', ('Sending response (action: %i)' % action))
        self.send_dict(response)

    def receive(self, text_data):
        try:
            data, action, entity_id = self.validate_data(text_data)
            self.execute(action, data, self.scope['giorgio'], self.scope['user'], entity_id)
        except GameEndException as e:
            self.send_dict({
                'r': RESPONSE_GAME_ENDED,
                'm': e.message,
            })
            self.close(WS_CLOSE_GAME_ENDED)
        except Exception as e:
            self.send_error(e)

    def run_generation(self, event):
        giorgio = self.scope['giorgio']
        if giorgio.running:
            # Run algorithm witch generates entities and get result
            gen_enemies, gen_powerups, current_round = giorgio.generate_entities()
            if len(gen_enemies) > 0:
                gen_enemies = list(map(lambda e: e.to_safe_dict(), gen_enemies))
                gen_powerups = list(map(lambda p: p.to_safe_dict(), gen_powerups))
                DEBUG('WebSocket', 'Sending generated entities')
                # Send to client generated entity lists
                self.send_dict({
                    'r': RESPONSE_GENERATED_ENTITIES,
                    'round': current_round,
                    'enemies': gen_enemies,
                    'powerups': gen_powerups
                })
        else:
            DEBUG('WebSocket', 'Generation prevented as the game is stopped')

    def expire_powerup(self, event):
        giorgio = self.scope['giorgio']
        if giorgio.running:
            powerup_id = event['powerup_id']
            player = giorgio.player
            powerup = player.active_powerups.get(powerup_id)
            if powerup is not None:
                del player.active_powerups[powerup.id]
                player.expired_powerups.add(powerup.type)
            DEBUG('WebSocket', 'Sending expired powerups')
            self.send_dict({
                'r': RESPONSE_PLAYER_OBJECT,
                'player': player.to_safe_dict()
            })
        else:
            DEBUG('WebSocket', 'Expiration prevented as the game is stopped')
