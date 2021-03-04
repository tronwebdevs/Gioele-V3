from api.models import Gun, Skin
from api.utils import parser
from api.exceptions import GameException
from api.game.enemies import ENEMY_TYPES
from api.game.powerups import POWERUP_TYPES
from api.game.abilities import ABILITY_TYPES

PLAYER_MAX_HP = 100
PLAYER_SHIELD_INCREMENT = 10
PLAYER_SPEED_INCREMENT = 0.5
PLAYER_DAMAGE_INCREMENT = 0.5
PLAYER_HP_INCREMENT = PLAYER_MAX_HP // 5
PLAYER_BASE_MODIFIER = 1
PLAYER_MAX_SHIELD = 100

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
        self.hp = PLAYER_MAX_HP
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
        if self.shield < PLAYER_MAX_SHIELD:
            temp = self.shield + PLAYER_SHIELD_INCREMENT
            if temp > PLAYER_MAX_SHIELD:
                self.shield = PLAYER_MAX_SHIELD
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
        if temp < PLAYER_MAX_HP:
            self.hp = temp
        else:
            self.hp = PLAYER_MAX_HP

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
            'damage_modifier': self.damage_modifier,
            'main_gun': self.main_gun.readable_dict(),
            'side_gun': self.side_gun.readable_dict(),
        }
