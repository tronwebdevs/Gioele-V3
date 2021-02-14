import sched
from uuid import uuid4

from django.utils import timezone

from .models import Gun, Skin, GUser, GameLog, VisitLog
from .classes import Parser
from .exceptions import GameException

MAX_PLAYER_HP = 100
MAX_MSHIP_LIFES = 3
PLAYER_SHIELD_INCREMENT = 10
MAX_PLAYER_SHIELD = 100

parser = Parser()


class Entity:
    def __init__(self, id, type):
        self.id = id
        self.type = type


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
    shield = 0
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

    """
    Get hp damage from a specified gun type.
    Remember to check first if side_gun is not null.
    """
    def get_damage(self, gun_type):
        return self.main_gun.damage if gun_type == 0 else self.side_gun.damage

    def get_displayable(self):
        return {
            'shield': self.shield,
            'hp': self.hp,
            'powerups': self.active_powerups
        }


class Giorgio:
    game_id = uuid4()
    start_time = timezone.now()
    enemies = dict()
    powerups = dict()
    killed = EnemyManager()
    mship_lifes = MAX_MSHIP_LIFES

    def __init__(self, user, visit_id, abilities, main_gun_id, side_gun_id, skin_id):
        self.user = user
        self.visit_id = visit_id
        self.player = Player(user.user.id, abilities, main_gun_id, side_gun_id, skin_id)

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
            self.killed.add(enemy.type)
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
    Add powerup to player's list and start sched (which at end remove the powerup from
    every stack).
    """
    def player_gain_powerup(self, powerup):
        ptype = powerup.type
        if ptype == PowerUp.TYPES['shield']:
            self.player.reload_shield()
        elif ptype == PowerUp.TYPES['fuel']:
            raise GameException('Not implemented yet')
        elif ptype == PowerUp.TYPES['ammo']:
            raise GameException('Not implemented yet')
        else:
            raise GameException('Unknown powerup')
        self.player.active_powerups.add(ptype)
        

    """
    Perform the ability effects.
    """
    def player_use_ability(self, ability):
        # TODO: implement the method
        raise GameException('Not implemented yet')

    def pause_game(self):
        # TODO: implement the method
        # game paused, stop all scheds
        raise GameException('Not implemented yet')

    def end_game(self):
        # TODO: implement the method
        raise GameException('Not implemented yet')

    def save(self):
        game_log = GameLog(
            id=self.game_id,
            user=self.user,
            time_start=self.start_time,
            time_end=timezone.now(),
            shooted_main=self.player.main_hit,
            shooted_side=self.player.side_hit,
            exp_gained=self.player.exp,
            gbucks_earned=self.player.gbucks
        )
        game_log.skin = game_log.user.skin
        game_log.visit = VisitLog.objects.get(pk=self.visit_id)
        # for enemy in self.killed:
        #     game_log.killed = 
        # game_log.killed = game_log.killed[:-1]
        game_log.killed = ''
        game_log.powerups = str(self.player.expired_powerups)
        game_log.save()
