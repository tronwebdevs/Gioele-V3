from uuid import uuid4

from django.utils import timezone

from .models import Gun, GUser, GameLog, VisitLog
from .classes import Parser

parser = Parser()


class PowerUp:
    TYPES = [
        'pu_type_0', 'pu_type_1', 'pu_type_2', 'pu_type_3'
    ]

    def __init__(self, _type):
        self.type = _type


class Enemy:
    TYPES = [
        'enemy_type_0', 'enemy_type_1', 'enemy_type_2', 'enemy_type_3'
    ]

    def __init__(self, xp, _type):
        self.xp = xp
        self.type = _type


class Manager:
    def __init__(self, data):
        self.data = data

    def get(self, id):
        return self.data[id]

    def add(self, id):
        self.data[id] += 1

    def remove(self, id):
        self.data[id] -= 1

    def __str__(self):
        return parser.dict_to_string(self.data)


class PowerUpManager(Manager):
    def __init__(self):
        super().__init__({PowerUp.TYPES[i]: 0 for i in range(0, len(PowerUp.TYPES))})


class EnemyManager(Manager):
    def __init__(self):
        super().__init__({Enemy.TYPES[i]: 0 for i in range(0, len(Enemy.TYPES))})


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
    killed = EnemyManager()

    def __init__(self, user_id, main_gun_id, side_gun_id):
        self.player = Player(user_id)
        self.main_gun = Gun.objects.get(pk=main_gun_id)
        self.side_gun = Gun.objects.get(pk=side_gun_id)

    def enemy_hit(self, gun_type, enemy_id):
        
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
            time_end=timezone.now(),
            shooted_main=self.shooted_main,
            shooted_side=self.shooted_side,
            exp_gained=self.exp,
            gbucks_earned=self.gbucks
        )
        game_log.user = GUser.objects.get(pk=self.player.user_id)
        game_log.skin = game_log.user.skin
        game_log.visit = VisitLog.objects.get(pk=visit_id)
        # for enemy in self.killed:
        #     game_log.killed = 
        # game_log.killed = game_log.killed[:-1]
        game_log.killed = ''
        game_log.powerups = str(self.player.expired_powerups)
        game_log.save()
