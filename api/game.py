from uuid import uuid4

from django.utils import timezone

from .models import Gun, GUser, GameLog, VisitLog
from .classes import Parser


class PowerUp:
    def __init__(self, _type):
        self.type = _type


class Enemy:
    def __init__(self, xp, _type):
        self.xp = xp
        self.type = _type


class PowerUpManager:
    data = {
        'type_0': 0,
        'type_1': 0,
        'type_2': 0,
        'type_3': 0,
        'type_4': 0,
    }

    def add(self, id):
        self.data[id] += 1

    def remove(self, id):
        self.data[id] -= 1

    def __str__(self):
        result = ''
        for key in self.data:
            result += key + Parser.DICT_SEPARATOR + self.data[key] + Parser.ITEM_SEPARATOR
        return result[:-1]


class Player:
    expired_powerups = PowerUpManager()
    active_powerups = PowerUpManager()
    shield_active = False

    def __init__(self, user_id):
        self.user_id = user_id


class Game:
    id = uuid4()
    exp = 0
    gbucks = 0
    shooted_main = 0
    shooted_side = 0
    start_time = timezone.now()
    killed = list()

    def __init__(self, user_id, main_gun_id, side_gun_id):
        self.player = Player(user_id)
        self.main_gun = Gun.objects.get(pk=main_gun_id)
        self.side_gun = Gun.objects.get(pk=side_gun_id)

    def enemy_hit(self, gun_id, enemy_id):
        if gun_id == self.main_gun.id:
            self.shooted_main += 1
        else:
            self.shooted_side += 1
        
        # TODO: enemy hit system (if enemy is killed or if it just lost xp)

        # Return the enemy that has been killed or none if enemy is still alive
        return None

    def acquired_powerup(self, powerup):
        self.player.active_powerups.add(powerup)

        # TODO: ingame logic like incrementing speed, applying shield, etc.

    def save(self, visit_id):
        game_log = GameLog(
            id=self.id,
            time_start=self.start_time,
            shooted_main=self.shooted_main,
            shooted_side=self.shooted_side,
            exp_gained=self.exp,
            gbucks_earned=self.gbucks
        )
        game_log.user = GUser.objects.get(pk=self.player.user_id)
        game_log.skin = game_log.user.skin
        game_log.visit = VisitLog.objects(pk=visit_id)
        # for enemy in self.killed:
        #     game_log.killed = 
        # game_log.killed = game_log.killed[:-1]
        game_log.killed = ''
        game_log.powerups = str(self.player.expired_powerups)
        game_log.save()
