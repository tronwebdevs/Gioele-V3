import sched
from uuid import uuid4

from django.utils import timezone

from .models import Gun, Skin, GUser, GameLog, VisitLog
from .classes import Parser

MAX_PLAYER_HP = 100
MAX_MSHIP_LIFES = 3

parser = Parser()


class Entity:
    def __init__(self, id, type):
        self.id = id
        self.type = type


class PowerUp(Entity):
    TYPES = ['pu_type_0', 'pu_type_1', 'pu_type_2', 'pu_type_3']

    def __init__(self, id, type):
        super().__init__(id, type)


class Ability(Entity):
    TYPES = ['a_type_0', 'a_type_1', 'a_type_2', 'a_type_3']

    def __init__(self, id, type):
        super().__init__(id, type)


class Enemy(Entity):
    TYPES = ['enemy_type_0', 'enemy_type_1', 'enemy_type_2', 'enemy_type_3']
    RARITIES = {
        'base': 0,
        'rare': 1,
        'epic': 2,
        'mytic': 3,
        'leggendary': 4,
    }

    def __init__(self, id, type, hp, damage, rarity=RARITIES['base'], is_boss=False):
        super().__init__(id, type)
        self.hp = hp
        self.damage = damage
        self.rarity = rarity
        self.is_boss = is_boss

    def __str__(self):
        return f'{self.id}({self.type}): {self.xp} [{self.rarity}]'


class Manager:
    def __init__(self, types):
        self.data = { types[i]: 0 for i in range(len(types)) }

    def get(self, _id):
        return self.data.get(_id)

    def add(self, _id):
        self.data[_id] += 1

    def remove(self, _id):
        self.data[_id] -= 1

    def __str__(self):
        return parser.dict_to_string(self.data)


class PowerUpManager(Manager):
    def __init__(self):
        super().__init__(PowerUp.TYPES)


class EnemyManager(Manager):
    def __init__(self):
        super().__init__(Enemy.TYPES)

class AbilityManager(Manager):
    def __init__(self):
        super().__init__(Ability.TYPES)


class Player:
    expired_powerups = PowerUpManager()
    active_powerups = PowerUpManager()
    used_abilities = AbilityManager()
    shield_active = False
    hp = MAX_PLAYER_HP
    exp = 0
    gbucks = 0
    main_hit = 0
    side_hit = 0

    def __init__(self, user_id, abilities, main_gun_id, side_gun_id, skin_id):
        self.user_id = user_id
        self.abilities = []
        self.main_gun = Gun.objects.get(pk=main_gun_id)
        if side_gun_id is not None:
            self.side_gun = Gun.objects.get(pk=side_gun_id)
        else:
            self.side_gun = None
        self.skin = Skin.objects.get(pk=skin_id)

    def bullet_hit(self, gun_type):
        if gun_type == 0:
            self.main_hit += 1
        else:
            self.side_hit += 1

    """
    Get hp damage from a specified gun type.
    Remember to check first if side_gun is not null.
    """
    def get_damage(self, gun_type):
        return self.main_gun.damage if gun_type == 0 else self.side_gun.damage


class Giorgio:
    game_id = uuid4()
    start_time = timezone.now()
    enemies = dict()
    killed = EnemyManager()
    mship_lifes = MAX_MSHIP_LIFES

    def __init__(self, user_id, abilities, main_gun_id, side_gun_id, skin_id):
        self.player = Player(user_id, abilities, main_gun_id, side_gun_id, skin_id)

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
