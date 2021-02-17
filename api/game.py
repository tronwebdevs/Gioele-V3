import random
from uuid import uuid4

from django.utils import timezone

from .classes import Parser
from .exceptions import GameException
from .models import GameLog, Gun, GUser, Skin, VisitLog

MAX_PLAYER_HP = 100
MAX_MSHIP_LIFES = 3
PLAYER_SHIELD_INCREMENT = 10
PLAYER_SPEED_INCREMENT = 0.5
PLAYER_DAMAGE_INCREMENT = 0.5
MAX_PLAYER_SHIELD = 100
POWERUPS_LAST_TIME = 10 # in seconds
CLIENT_CANVAS_WIDTH = 800

parser = Parser()


class Entity:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.x = round(random.random() * (CLIENT_CANVAS_WIDTH - 50))


class PowerUp(Entity):
    TYPES = {
        'shield': 0, 
        'fuel': 1,
        'ammo': 2,
    }

    def __init__(self, id, type):
        super().__init__(id, type)


class Ability(Entity):
    TYPES = {
        'wave': 0,
        'hp_regen': 1,
    }

    def __init__(self, id, type):
        super().__init__(id, type)


class Enemy(Entity):
    TYPES = {
        'ship': 0,
        'kamikaze': 1,
        'interceptor': 2,
    }
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


class Manager:
    def __init__(self, types):
        items = list(types.values())
        self.data = { items[i]: 0 for i in range(len(items)) }

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
    active_powerups = dict()
    used_abilities = AbilityManager()
    killed = EnemyManager()
    shield = 0
    hp = MAX_PLAYER_HP
    exp = 0
    gbucks = 0
    main_hit = 0
    side_hit = 0
    damage_modifier = 1
    speed_modifier = 1

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


class Giorgio:
    game_id = uuid4()
    running = False
    enemies = dict()
    powerups = dict()
    mship_lifes = MAX_MSHIP_LIFES
    _generation = 0

    def __init__(self, user, visit_id, abilities, main_gun_id, side_gun_id, skin_id):
        self.user = user
        self.visit_id = visit_id
        self.player = Player(user.user.id, abilities, main_gun_id, side_gun_id, skin_id)

    def start_game(self):
        self.start_time = timezone.now()
        # Mark game as running
        self.running = True

    def powerup_expired(self, powerup=None):
        del self.player.active_powerups[powerup.id]
        self.player.expired_powerups.add(powerup.type)

    """
    'u guru digidàl v2'
    Generates enemies, bosses and powerups.
    Return generated entities.
    """
    def generate_entities(self):
        self._generation += 1
        last_id = -1
        enemies_list = list(self.enemies)
        if len(enemies_list) > 0:
            last_id = list(self.enemies)[-1]
        enemy_id = last_id + 1
        enemy_type = random.choice(list(Enemy.TYPES.values()))
        new_enemies = []
        # FIXME: temporary entities limit
        if len(enemies_list) < 30:
            new_enemies.append(Enemy(enemy_id, enemy_type, 10, 10))
        for enemy in new_enemies:
            self.enemies[enemy.id] = enemy

        new_powerups = []
        if len(list(self.powerups)) == 0:
            new_powerups.append(PowerUp(0, PowerUp.TYPES['fuel']))

        for powerup in new_powerups:
            self.powerups[powerup.id] = powerup

        return new_enemies, new_powerups

    """
    Check if enemy has been killed (and remove it from stack) or just
    remove xp from enemy and update counter of hit bullets.
    Return updated enemy (hp).
    """
    def player_hit_enemy(self, gun_type, enemy):

        # TODO: handle multiple enemy hit at once

        # Increment hit bullets' counter
        self.player.bullet_hit(gun_type)
        # Calculate enemy's remained hp
        temp = enemy.hp - self.player.get_damage(gun_type)
        if temp < 0:
            # enemy is dead
            self.player.killed.add(enemy.type)
            # Remove enemy from stack
            del self.enemies[enemy.id]
            enemy.hp = 0
        else:
            # enemy has lost hp
            self.enemies[enemy.id].hp = temp
        return enemy

    """
    If directly, remove the enemy from the stack, check if player died (trigger end game)
    or just remove xp (or shield) from player. If with bullet, just check for player
    death or remove xp (or sheild).
    """
    def enemy_hit_player(self, enemy, directly):
        if directly:
            # If enemy has collide with player (kamikaze) remove enemy from the stack
            del self.enemies[enemy.id]
        self.player.attacked(enemy.damage)
        return self.player

    """
    Subtract 1 from mother lifes (and check if she has died) and remove enemy from stack.
    Return remained mship's lifes.
    """
    def enemy_hit_mship(self, enemy):
        # Remove enemy from stack
        del self.enemies[enemy.id]
        lifes = self.mship_lifes - 1
        if lifes < 0:
            # Mother ship is dead, game ends
            self.end_game()
            raise GameException('Game ended', 0)
        else:
            # Mother ship lost a life
            self.mship_lifes = lifes
        return lifes

    """
    Add powerup to player's list.
    """
    def player_gain_powerup(self, powerup):
        ptype = powerup.type
        if ptype == PowerUp.TYPES['shield']:
            self.player.reload_shield()
        elif ptype == PowerUp.TYPES['fuel']:
            self.player.speed_up()
        elif ptype == PowerUp.TYPES['ammo']:
            self.player.damage_up()
        else:
            raise GameException('Unknown powerup')

        if ptype != PowerUp.TYPES['shield']:
            # Add powerup to player's active powerups list
            self.player.active_powerups[powerup.id] = powerup
        else:
            # Add increment shield counter
            self.player.expired_powerups.add(ptype)
        return self.player

    """
    Perform the ability effects.
    """
    def player_use_ability(self, ability):
        # TODO: implement the method
        raise GameException('Not implemented yet')
        # return self.player

    def pause_game(self):
        self.running = False
        # TODO: implement the method
        raise GameException('Not implemented yet')

    def end_game(self):
        self.running = False
        # TODO: implement the method
        raise GameException('Not implemented yet')

    def save(self, shooted_main, shooted_side):
        game_log = GameLog(
            id=self.game_id,
            user=self.user,
            time_start=self.start_time,
            time_end=timezone.now(),
            exp_gained=self.player.exp,
            gbucks_earned=self.player.gbucks,
            shooted_main=shooted_main,
            shooted_main_hit=self.player.main_hit,
            shooted_side=shooted_side,
            shooted_side_hit=self.player.side_hit,
            main_gun=self.player.main_gun.id,
            side_gun=self.player.side_gun.id
        )
        game_log.visit = VisitLog.objects.get(pk=self.visit_id)
        game_log.killed = parser.dict_to_string(self.player.killed)
        game_log.powerups = parser.dict_to_string(self.player.expired_powerups)
        game_log.abilities = parser.dict_to_string(self.player.used_abilities)
        game_log.skin = game_log.user.skin
        game_log.save()
