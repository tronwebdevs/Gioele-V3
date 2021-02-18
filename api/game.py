from random import random

from .classes import Parser
from .exceptions import GameCheatDetectedException, GameException
from .models import Gun, GUser, Skin

DELAY_BETWEEN_ENEMIES_GENERATIONS = 5 # in seconds
MAX_PLAYER_HP = 100
MAX_MSHIP_LIFES = 3
PLAYER_SHIELD_INCREMENT = 10
PLAYER_SPEED_INCREMENT = 0.5
PLAYER_DAMAGE_INCREMENT = 0.5
PLAYER_HP_INCREMENT = MAX_PLAYER_HP // 5
PLAYER_BASE_MODIFIER = 1
MAX_PLAYER_SHIELD = 100
POWERUPS_LAST_TIME = 10 # in seconds
CLIENT_CANVAS_WIDTH = 800 # in pixels

parser = Parser()


class Entity:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.x = round(random() * (CLIENT_CANVAS_WIDTH - 50))


class PowerUp(Entity):
    def __init__(self, id, type):
        super().__init__(id, type)

    def activate(self, player):
        pass

    def deactivate(self, player):
        pass


class Ability(Entity):
    def __init__(self, id, type):
        super().__init__(id, type)

    def run(self, giorgio):
        pass


class Enemy(Entity):
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
        return f'{self.id}({self.type}): {self.hp} [{self.rarity}]'


class BaseShipEnemy(Enemy):
    TYPE = 0

    def __init__(self, id, rarity=Enemy.RARITIES['base']):
        super().__init__(
            id=id,
            type=self.TYPE,
            hp=20,
            damage=10,
            rarity=rarity,
            is_boss=False
        )


class ShieldPowerUp(PowerUp):
    TYPE = 0

    def __init__(self, id):
        super().__init__(id, self.TYPE)
    
    def activate(self, player):
        player.reload_shield()

    def deactivate(self, player):
        player.reset_speed()


class FuelPowerUp(PowerUp):
    TYPE = 1

    def __init__(self, id):
        super().__init__(id, self.TYPE)
    
    def activate(self, player):
        player.speed_up()

    def deactivate(self, player):
        player.reset_speed()


class DamagePowerUp(PowerUp):
    TYPE = 2

    def __init__(self, id):
        super().__init__(id, self.TYPE)
    
    def activate(self, player):
        player.damage_up()

    def deactivate(self, player):
        player.reset_damage()


class WaveAbility(Ability):
    TYPE = 0

    def __init__(self, id):
        super().__init__(id, self.TYPE)
    
    def run(self, giorgio):
        for enemy in giorgio.enemies:
            enemy.hp = 0


class HpRegenAbility(Ability):
    TYPE = 1

    def __init__(self, id):
        super().__init__(id, self.TYPE)
    
    def run(self, giorgio):
        giorgio.player.regen_hp()

ENEMY_TYPES  = {
    'ship': (BaseShipEnemy.TYPE, BaseShipEnemy),
    # 'kamikaze': (1, None),
    # 'interceptor': (2, None),
}

POWERUP_TYPES = {
    'shield': (ShieldPowerUp.TYPE, ShieldPowerUp),
    'fuel': (FuelPowerUp.TYPE, FuelPowerUp),
    'damage': (DamagePowerUp.TYPE, DamagePowerUp),
}

ABILITY_TYPES = {
    'wave': (WaveAbility.TYPE, WaveAbility),
    'hp_regen': (HpRegenAbility.TYPE, HpRegenAbility),
}


class Manager:
    def __init__(self, types):
        items = list(types.values())
        self.data = { items[i][0]: 0 for i in range(len(items)) }

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
        super().__init__(POWERUP_TYPES)


class EnemyManager(Manager):
    def __init__(self):
        super().__init__(ENEMY_TYPES)


class AbilityManager(Manager):
    def __init__(self):
        super().__init__(ABILITY_TYPES)


class Player:
    def __init__(self, user_id, abilities, main_gun_id, side_gun_id, skin_id):
        self.expired_powerups = PowerUpManager()
        self.active_powerups = dict()
        self.used_abilities = AbilityManager()
        self.killed = EnemyManager()
        self.shield = 0
        self.hp = MAX_PLAYER_HP
        self.exp = 0
        self.gbucks = 0
        self.main_hit = 0
        self.side_hit = 0
        self.damage_modifier = PLAYER_BASE_MODIFIER
        self.speed_modifier = PLAYER_BASE_MODIFIER
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

    def attacked(self, damage):
        if damage > self.shield:
            damage -= self.shield
            self.shield = 0
        else:
            self.shield -= damage
            damage = 0
        temp = self.hp - damage
        if temp < 0:
            raise GameException('Player killed')
        self.hp = temp

    def reload_shield(self):
        if self.shield < MAX_PLAYER_SHIELD:
            temp = self.shield + PLAYER_SHIELD_INCREMENT
            if temp > MAX_PLAYER_SHIELD:
                self.shield = MAX_PLAYER_SHIELD
            else:
                self.shield = temp
    
    def reset_speed(self):
        self.speed_modifier = 1

    def speed_up(self):
        self.reset_speed()
        self.speed_modifier += PLAYER_SPEED_INCREMENT

    def reset_damage(self):
        self.damage_modifier = 1
        
    def damage_up(self):
        self.reset_damage()
        self.damage_modifier += PLAYER_SPEED_INCREMENT

    def regen_hp(self):
        temp = self.hp + PLAYER_HP_INCREMENT
        if temp < MAX_PLAYER_HP:
            self.hp = temp
        else:
            self.hp = MAX_PLAYER_HP

    """
    Get hp damage from a specified gun type.
    Remember to check first if side_gun is not null.
    """
    def get_damage(self, gun_type):
        gun_damage = self.main_gun.damage if gun_type == 0 else self.side_gun.damage
        return gun_damage * self.damage_modifier

    def get_displayable(self):
        return {
            'shield': self.shield,
            'hp': self.hp,
            'powerups': list(map(vars, self.active_powerups.values())),
            'speed': self.speed_modifier,
            'damage_modifier': self.damage_modifier
        }
