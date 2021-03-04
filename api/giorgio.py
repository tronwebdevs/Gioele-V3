import random
import math
from uuid import uuid4

from django.utils import timezone

from .exceptions import GameException
from .utils import parser, redis_broadcast, log as DEBUG
from .game.constants import MAX_MSHIP_LIFES, ENEMIES_PER_GENERATION
from .game.player import Player
from .game.enemies import ENEMY_TYPES, BOSS_TYPES
from .game.powerups import POWERUP_TYPES
from .models import GameLog


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
        self.round = 1

    def start_game(self):

        DEBUG('Giorgio', 'Game started (%s)' % self.game_id, broadcast=True)

        self.start_time = timezone.now()
        redis_broadcast('general', {
            't': 4,
            'player': self.player.get_displayable(),
        })
        # Mark game as running
        self.running = True

    def powerup_expired(self, powerup=None):

        DEBUG('Giorgio', ('Expiring powerup #%i' % powerup.id), broadcast=True)

        # Remove powerup from player's active powerups list
        del self.player.active_powerups[powerup.id]
        # Increment player's expired powerups list
        self.player.expired_powerups.add(powerup.type)

    def generate_enemies(self, p1, p2):
        EnemyType = None
        generated = []
        for i in range(ENEMIES_PER_GENERATION):
            # Generate pseudo-random to choose enemy's type (based on given percentages)
            rnd = random.random()

            DEBUG('Giorgio', 'DEBUG ENEMIES GEN: g=%i, k=%i, p1=%f, p2=%f, rand:%f' % (self._generation, self.round, p1 / 100, (p1 + p2) / 100, rnd))

            # Choose enemy's type based on given percentages
            if rnd <= p1 / 100:
                EnemyType = ENEMY_TYPES['ship']
            elif rnd <= (p1 + p2) / 100:
                EnemyType = ENEMY_TYPES['kamikaze']
            else:
                EnemyType = ENEMY_TYPES['interceptor']

            # Increment entity counter, which is also current enemy's id
            self._last_entity_id += 1
            EnemyTypeClass = EnemyType[1]

            # Calculate enemy's health points based on: h = base * (1 + (k - 1) / 10)
            hp = round(EnemyTypeClass.BASE_HP * (1 + (self.round - 1) / 10))

            generated.append(EnemyTypeClass(id=self._last_entity_id, hp=hp, rnd=rnd))
        
        return generated

    def generate_powerups(self, p0, p1, p2=0):
        PowerUpType = None
        # Generate pseudo-random to choose powerup's type (based on given percentages)
        rnd = random.random()
        
        DEBUG('Giorgio', 'DEBUG POWERUPS GEN: g=%i, k=%i, p0=%f, p1=%f, p2=%f, rand:%f' % (self._generation, self.round, p0 / 100, (p0 + p1) / 100, (p0 + p1 + p2) / 100, rnd))

        # Choose powerup's type based on given percentages
        if rnd <= p0 / 100:
            return None
        elif rnd <= (p0 + p1) / 100:
            PowerUpType = POWERUP_TYPES['fuel']
        elif rnd <= (p0 + p1 + p2) / 100:
            PowerUpType = POWERUP_TYPES['shield']
        else:
            PowerUpType = POWERUP_TYPES['damage']

        # Increment entity counter, which is also current powerup's id
        self._last_entity_id += 1

        return PowerUpType[1](self._last_entity_id, rnd)

    """
    'u guru digidàl v2'
    Generates enemies, bosses and powerups.
    Returns generated entities.
    """
    def generate_entities(self):
        gen_powerups = gen_enemies = []

        # Return if enemies from previous round are still alive
        if self._generation == 0 and len(self.enemies) > 0:
            return gen_powerups, gen_enemies, self.round

        # Increment generations counter
        self._generation += 1

        k = self.round
        g = self._generation
        
        DEBUG('Giorgio', 'Generating entities for round %i' % k, broadcast=True)


        if k >= 20 and k % 10 == 0:
            # From round 20, every 10 rounds, spawn a random boss
            self._last_entity_id += 1
            EnemyBossClass = random.choice(list(BOSS_TYPES.values()))[1]
            gen_enemies.append(EnemyBossClass(id=self._last_entity_id, rnd=1.0))
        else:
            # Pb(k) = (100 - 10 - 10k)%
            p1 = 100 - 10 * (k + 1)
            # Generate enemies based on probability table (giorgio.txt)
            if k == 1: # k = 1
                gen_enemies = self.generate_enemies(100, 0)
            elif k <= 6: # 2 <= k <= 6
                # Pk(k) = (15 + 5k)%
                p2 = 5 * (k + 3)
                # Pi(k) = (5(k - 1))%
                gen_enemies = self.generate_enemies(p1, p2)
            else: # K >= 7
                if k > 7: # k != 7
                    # Pb(k) = 20%
                    p1 = 20
                # Pk(k) = 40%
                gen_enemies = self.generate_enemies(p1, 40)

        # Generate powerup based on probability table (giorgio.txt)
        powerup = None
        if k == 2:
            powerup = self.generate_powerups(50, 50)
        elif k == 3:
            powerup = self.generate_powerups(100/3, 100/3, 100/3)
        elif k >= 4:
            powerup = self.generate_powerups(25, 25, 25)
        
        if powerup is not None:
            gen_powerups.append(powerup)
        
        # Push new evemies to the stack
        for enemy in gen_enemies:
            self.enemies[enemy.id] = enemy
        # Push new powerups to the stack
        for powerup in gen_powerups:
            self.powerups[powerup.id] = powerup

        if g >= k:
            # Current generation was the last of the round,
            # reset generation counter and increment round counter
            self._generation = 0
            self.round += 1

        redis_broadcast('general', {
            't': 1,
            'round': k,
            'enemies': list(map(lambda e: e.get_displayable(internal=True), gen_enemies)),
            'powerups': list(map(lambda pu: pu.get_displayable(internal=True), gen_powerups)),
        })

        # Return generated entities
        return gen_enemies, gen_powerups, k

    """
    Check if enemy has been killed (and remove it from stack) or just
    remove xp from enemy and update counter of hit bullets.
    Returns updated enemy (hp).
    """
    def player_hit_enemy(self, gun_type, enemy):

        # TODO: handle multiple enemy hit at once

        # Increment hit bullets' counter
        self.player.bullet_hit(gun_type)
        # Calculate enemy's remained hp
        temp = enemy.hp - self.player.get_damage(gun_type)
        if temp <= 0:
            # enemy is dead
            self.player.killed.add(enemy.type)
            # Give rewards to player
            self.player.exp += enemy.exp_reward
            self.player.gbucks += enemy.gbucks_reward
            # Remove enemy from stack
            del self.enemies[enemy.id]
            enemy.hp = 0

            DEBUG('Giorgio', 'Player killed enemy #%i' % enemy.id, broadcast=True)

        else:
            # enemy has lost hp
            self.enemies[enemy.id].hp = temp

            DEBUG('Giorgio', 'Player hit enemy #%i, hp remaining: %i' % (enemy.id, enemy.hp), broadcast=True)

        redis_broadcast('general', {
            't': 2,
            'enemy': enemy.get_displayable(True),
        })

        # Return updated enemy
        return enemy

    """
    If directly, remove the enemy from the stack, check if player died (trigger end game)
    or just remove xp (or shield) from player. If with bullet, just check for player
    death or remove xp (or sheild).
    Returns updated player's object.
    """
    def enemy_hit_player(self, enemy, directly):

        DEBUG('Giorgio', 'Enemy #%i hit player (directly:%s)' % (enemy.id, directly), broadcast=True)

        if directly:
            # If enemy has collide with player (kamikaze) remove enemy from the stack
            del self.enemies[enemy.id]
        # Compute attack
        self.player.attacked(enemy.damage)

        enemy.hp = 0
        redis_broadcast('general', {
            't': 4,
            'player': self.player.get_displayable(),
            'enemy': enemy.get_displayable(),
        })

        # Return updated player
        return self.player

    """
    Subtract 1 from mother lifes (and check if she has died) and remove enemy from stack.
    Returns remained mship's lifes.
    """
    def enemy_hit_mship(self, enemy):
        enemy.hp = 0

        DEBUG('Giorgio', 'Enemy #%i hit mother ship' % enemy.id, broadcast=True)

        # Remove enemy from stack
        del self.enemies[enemy.id]
        lifes = self.mship_lifes - 1
        if lifes <= 0:
            # Mother ship is dead, game ends

            DEBUG('Giorgio', 'Mother ship dead, game end', broadcast=True)

            redis_broadcast('general', {
                't': 3,
                'lifes': 0,
                'enemy': enemy.get_displayable(True),
            })

            self.end_game()
            raise GameException('Game ended', 0)
        else:
            # Mother ship lost a life
            self.mship_lifes = lifes
        # Return updated mship's lifes

        redis_broadcast('general', {
            't': 3,
            'lifes': self.mship_lifes,
            'enemy': enemy.get_displayable(True),
        })

        return lifes

    """
    Activate powerup and add it to the player's list.
    Returns updated player's object.
    """
    def player_gain_powerup(self, powerup):

        DEBUG('Giorgio', 'Player gain powerup %i (#%i)' % (powerup.type, powerup.id), broadcast=True)

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
    Returns updated player's object.
    """
    def player_use_ability(self, ability):

        DEBUG('Giorgio', 'Player used ability %i' % ability.type, broadcast=True)

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
        redis_broadcast('general', {
            't': 5,
        })
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
