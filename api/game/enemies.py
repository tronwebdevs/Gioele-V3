import random

from api.game.entity import Entity


class Enemy(Entity):
    RARITIES = {
        'base': (0, 1),
        'rare': (1, 2),
        'epic': (2, 5),
        'mytic': (3, 10),
        'leggendary': (4, 25),
    }

    def _pick_rarity(self):
        self.rarity_rnd = random.random()
        if self.rarity_rnd <= 0.05: # 5%
            return self.RARITIES['rare']
        elif self.rarity_rnd <= 0.06: # 1%
            return self.RARITIES['epic']
        elif self.rarity_rnd <= 0.062: # 0.2%
            return self.RARITIES['mytic']
        elif self.rarity_rnd <= 0.0625: # 0.05%
            return self.RARITIES['leggendary']
        else: # 93.75%
            return self.RARITIES['base']

    def __init__(self, id, type, hp, exp_reward, gbucks_reward, \
                 damage, rnd, rarity=None, is_boss=False):
        super().__init__(id, type, rnd)
        self.rarity_rnd = 0.0
        if rarity is None:
            rarity = self._pick_rarity()
        self.rarity = rarity
        moltiplier = rarity[1]
        self.hp = hp * moltiplier
        self.damage = damage * moltiplier
        self.exp_reward = exp_reward * moltiplier
        self.gbucks_reward = gbucks_reward * moltiplier
        self.is_boss = is_boss

    def get_displayable(self, internal=False):
        obj = {
            **super().get_displayable(internal),
            'hp': self.hp,
            'damage': self.damage,
            'rarity': self.rarity[0],
            'is_boss': self.is_boss,
        }
        if internal:
            obj['rarity_rnd'] = self.rarity_rnd
        return obj

    def __str__(self):
        return f'{self.id}({self.type}): {self.hp} [{self.rarity}]'


class BaseShipEnemy(Enemy):
    TYPE = 0
    BASE_HP = 100

    def __init__(self, id, rnd, hp=BASE_HP, rarity=None):
        super().__init__(
            id=id,
            type=self.TYPE,
            hp=hp,
            exp_reward=1,
            gbucks_reward=1,
            damage=10,
            rarity=rarity,
            is_boss=False,
            rnd=rnd
        )


class KamikazeShipEnemy(Enemy):
    TYPE = 1
    BASE_HP = 150

    def __init__(self, id, rnd, hp=BASE_HP, rarity=None):
        super().__init__(
            id=id,
            type=self.TYPE,
            hp=hp,
            exp_reward=2,
            gbucks_reward=2,
            damage=5,
            rarity=rarity,
            is_boss=False,
            rnd=rnd
        )


class InterceptorShipEnemy(Enemy):
    TYPE = 2
    BASE_HP = 200

    def __init__(self, id, rnd, hp=BASE_HP, rarity=None):
        super().__init__(
            id=id,
            type=self.TYPE,
            hp=hp,
            exp_reward=10,
            gbucks_reward=10,
            damage=40,
            rarity=rarity,
            is_boss=False,
            rnd=rnd
        )


class BossEnemy(Enemy):
    def __init__(self, id, type, hp, exp_reward, gbucks_reward, damage, rnd, rarity=None):
        super().__init__(
            id=id,
            type=type,
            hp=hp,
            exp_reward=exp_reward,
            gbucks_reward=gbucks_reward,
            damage=damage,
            rarity=rarity,
            is_boss=True,
            rnd=rnd
        )

    def attack(self, giorgio):
        pass


class ShitAssBossEnemy(BossEnemy):
    TYPE = 10
    BASE_HP = 5000

    def __init__(self, id, rnd, hp=BASE_HP, rarity=None):
        super().__init__(
            id=id,
            type=self.TYPE,
            hp=hp,
            exp_reward=1000,
            gbucks_reward=1000,
            damage=10,
            rarity=rarity,
            rnd=rnd
        )

    def attack(self, giorgio):
        # giorgio.generate_enemies(100, 0)
        print('ShitAss is attacking you.')


class JarvisBossEnemy(BossEnemy):
    TYPE = 11
    BASE_HP = 10000

    def __init__(self, id, rnd, hp=BASE_HP, rarity=None):
        super().__init__(
            id=id,
            type=self.TYPE,
            hp=hp,
            exp_reward=8000,
            gbucks_reward=12000,
            damage=90,
            rarity=rarity,
            rnd=rnd
        )

    def attack(self, giorgio):
        # giorgio.generate_enemies(100, 0)
        print('Jarvis is attacking you.')


ENEMY_TYPES  = {
    'ship': (BaseShipEnemy.TYPE, BaseShipEnemy),
    'kamikaze': (KamikazeShipEnemy.TYPE, KamikazeShipEnemy),
    'interceptor': (InterceptorShipEnemy.TYPE, InterceptorShipEnemy),
}

BOSS_TYPES = {
    'shitass': (ShitAssBossEnemy.TYPE, ShitAssBossEnemy),
    'jarvis': (JarvisBossEnemy.TYPE, JarvisBossEnemy),
}
