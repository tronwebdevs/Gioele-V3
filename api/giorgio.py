import random
from uuid import uuid4

from django.utils import timezone

from .classes import Parser
from .exceptions import GameException
from .game import MAX_MSHIP_LIFES, Player, ENEMY_TYPES, POWERUP_TYPES
from .models import GameLog

parser = Parser()


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
        EnemyType = random.choice(list(ENEMY_TYPES.values()))[1]
        new_enemies = []
        # FIXME: temporary entities limit
        if len(enemies_list) < 30:
            new_enemies.append(EnemyType(last_id + 1))
        for enemy in new_enemies:
            self.enemies[enemy.id] = enemy

        new_powerups = []
        if len(list(self.powerups)) == 0:
            new_powerups.append(POWERUP_TYPES['fuel'][1](0))

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
        powerup.activate(self.player)
        ptype = powerup.type

        if ptype != POWERUP_TYPES['shield'][0]:
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
