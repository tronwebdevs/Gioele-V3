import json
import uuid

from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser

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


class GameConsumer(WebsocketConsumer):

    def connect(self):
        if type(self.scope['user']) is AnonymousUser:
            print('Unauthenticated user')
            self.disconnect(1008)
            return
        print(self.scope['user'].user.username + ' connected')
        self.scope['game'] = None
        self.accept()

    def disconnect(self, close_code):
        if type(self.scope['user']) is not AnonymousUser:
            if self.scope['game'] is not None:
                self.scope['game'].save(uuid.UUID('5c9539b514a9442ab5e14ae6ec50ccdb'))
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

    def send_error(self, message, code=-1):
        self.send_dict({
            'code': code,
            'message': message
        })

    def get_entity(self, action, eid):
        exception = Exception('Entity not found')
        game = self.scope['game']
        if action < 7:
            # Entity is an enemy
            entity = game.enemies.get(eid)
        elif action == 7:
            # Entity is a powerup
            entity = game.player.active_powerups.get(eid)
        elif action == 8:
            # Entity is an ability
            entity = None #game.player.abilites.get(eid)
        else:
            raise exception
        
        if entity is None:
            raise exception
        return entity

    def receive(self, text_data):
        try:
            data, action, obj_id = self.validate_data(text_data)
        except Exception as e:
            self.send_error(str(e))
            return
        game = self.scope['game']
        user = self.scope['user']
        
        if action == ACTION_GAME_START:
            if game is None:
                self.send_error('Game already started', ERROR_GAME_ALREADY_STARTED)
                return
            try:
                self.scope['game'] = Giorgio(
                    user.user.id,
                    user.inventory.abilites,
                    user.main_gun,
                    user.side_gun,
                    user.skin
                )
                print('Game started')
            except Exception as e:
                self.send_error(str(e))
        elif game is not None:
            player = game.player
            
            if action > 2:
                # Check if given enemy's id is valid and get enemy object from stack
                try:
                    enemy = game.get_enemy(obj_id)
                except Exception as e:
                    self.send_error(str(e), ERROR_ENTITY_NOT_FOUND)
                    return
            # Switch between actions
            if action == ACTION_GAME_PAUSE:
                # TODO: game paused, stop all scheds
                pass
            elif action == ACTION_GAME_STOP:
                # TODO: game stopped, store on db
                self.send_error('Game ended', 0)
            elif action == ACTION_ENEMY_HIT_PLAYER_DIR:
                # TODO: remove the enemy from the stack, check if player died (trigger end game) or just remove xp (or shield) from player
                pass
            elif action == ACTION_ENEMY_HIT_PLAYER_IND:
                # TODO: check for player death or remove xp (or sheild)
                pass
            elif action == ACTION_ENEMY_HIT_MSHIP:
                # Remove enemy from stack
                del game.enemies[obj_id]
                temp = game.mship_lifes - 1
                if temp < 0:
                    # Mother ship is dead, game ends
                    # TODO: game end
                    self.send_error('Game ended', 0)
                else:
                    # Mother ship lost a life
                    game.mship_lifes = temp
                    self.send_dict({ 'lifes': game.mship_lifes })
            elif action == ACTION_PLAYER_HIT_ENEMY:
                # Check if given gun's type is valid
                gun_type = data.get('t')
                if type(gun_type) is not int or gun_type < 0 or gun_type > 1 or (gun_type == 1 and player.side_gun is None):
                    self.send_error('Invalid data (t)')
                    return
                # Increment hit bullets' counter
                player.bullet_hit()
                # Calculate enemy's remained hp
                temp = enemy.hp - player.get_damage(gun_type)
                if temp < 0:
                    # enemy is dead
                    game.killed.add(enemy.type)
                    # Remove enemy from stack
                    del game.enemies[obj_id]
                    enemy.hp = 0
                else:
                    # enemy has lost hp
                    game.enemies[obj_id].hp = temp
                # Return updated enemy
                self.send_dict(enemy)
            elif action == ACTION_PLAYER_GAIN_POWERUP:
                # TODO: Add powerup to player's list and start timer (which at end remove) the powerup from every stack)
                pass
            elif action == ACTION_PLAYER_USE_ABILITY:
                # TODO: Perform the ability effects
                pass
            else:
                self.send_error('Invalid action')
        else:
            self.send_error('Game hasn\'t started', ERROR_GAME_NOT_STARTED)
