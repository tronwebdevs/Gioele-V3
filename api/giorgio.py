import random
import math
from uuid import uuid4

from django.utils import timezone

from .classes import Parser
from .exceptions import GameException
from .game import MAX_MSHIP_LIFES, Player, ENEMY_TYPES, POWERUP_TYPES
from .models import GameLog

parser = Parser()


class Giorgio:
    def __init__(self, user, visit_id, abilities, main_gun_id, side_gun_id, skin_id):
        self.user = user
        self.visit_id = visit_id
        self.player = Player(user.user.id, abilities, main_gun_id, side_gun_id, skin_id)
        self.game_id = uuid4()
        self.running = False
        self.enemies = dict()
        self.powerups = dict()
        self.mship_lifes = MAX_MSHIP_LIFES
        self._last_entity_id = 0
        self._generation = 0
        self._round = 0

    def start_game(self):
        self.start_time = timezone.now()
        # Mark game as running
        self.running = True

    def powerup_expired(self, powerup=None):
        # Remove powerup from player's active powerups list
        del self.player.active_powerups[powerup.id]
        # Increment player's expired powerups list
        self.player.expired_powerups.add(powerup.type)

    def _generate_from_perc(self, ch1, ch2):
        EnemyType = None
        rnd = random.random()
        # print('DEBUG: ', self._generation, self._round, ch1, ch2, ' rand: ', rnd)
        if rnd <= ch1:
            EnemyType = ENEMY_TYPES['ship']
        elif rnd <= ch2:
            EnemyType = ENEMY_TYPES['kamikaze']
        else:
            EnemyType = ENEMY_TYPES['interceptor']
        return EnemyType[1](self._last_entity_id)

    """
    'u guru digidàl v2'
    Generates enemies, bosses and powerups.
    Return generated entities.
    """
    def generate_entities(self):
        # Increment generations counter
        self._generation += 1
        new_enemies = []
        k = self._round
        g = self._generation
        # g + 3 - 10k > 0
        if g > 2 and (k == 0 or (g + 3 - (10 * k)) > 0):
            self._round += 1
        # Pb(k) = (100 - 10 - 10k)%
        ch1 = 100 - 10 * (k + 1)
        if k == 0: # k = 0
            for i in range(5):
                self._last_entity_id += 1
                new_enemies.append(ENEMY_TYPES['ship'][1](self._last_entity_id))
        elif k <= 5: # 1 <= k <= 5
            # Pk(k) = (15 + 5k)%
            ch2 = ch1 + 5 * (k + 3)
            # Pi(k) = (5(k - 1))%
            for i in range(5):
                self._last_entity_id += 1
                new_enemies.append(self._generate_from_perc(ch1 / 100, ch2 / 100))
        else: # K >= 6
            if k > 6: # k != 6
                # Pb(k) = 20%
                ch1 = 20
            # Pk(k) = 40%
            ch2 = ch1 + 40
            for i in range(5):
                self._last_entity_id += 1
                new_enemies.append(self._generate_from_perc(ch1 / 100, ch2 / 100))
        # Push new evemy to the stack
        for enemy in new_enemies:
            self.enemies[enemy.id] = enemy

        # TODO: implement algorithm's powerups generation
        new_powerups = []
        # Generate 1 powerup every 5 generations
        if self._generation % 5 == 0:
            self._last_entity_id += 1
            # Pick a random powerup from list
            PowerUpType = random.choice(list(POWERUP_TYPES.values()))[1]
            # Push created powerup to temp stack
            new_powerups.append(PowerUpType(self._last_entity_id))
        # Push new powerups to the stack
        for powerup in new_powerups:
            self.powerups[powerup.id] = powerup

        # Return generated entities
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
        # Return updated enemy
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
        # Compute attack
        self.player.attacked(enemy.damage)
        # Return updated player
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
        # Return updated mship's lifes
        return lifes

    """
    Activate powerup and add it to the player's list.
    """
    def player_gain_powerup(self, powerup):
        # Activate powerup
        powerup.activate(self.player)
        ptype = powerup.type

        if ptype != POWERUP_TYPES['shield'][0]:
            # Add powerup to player's active powerups list
            self.player.active_powerups[powerup.id] = powerup
        else:
            # Increment player's shield counter
            self.player.expired_powerups.add(ptype)
        # Return updated player
        return self.player

    """
    Perform the ability effects and add it to the player's list.
    """
    def player_use_ability(self, ability):
        # Perform ability
        ability.run(self)
        # Add player's ability counter
        self.player.used_abilities.add(ability.id)
        # Return updated player
        return self.player

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
