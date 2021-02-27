from api.game.entity import Entity


class Enemy(Entity):
    RARITIES = {
        'base': 0,
        'rare': 1,
        'epic': 2,
        'mytic': 3,
        'leggendary': 4,
    }

    def __init__(self, id, type, hp, exp_reward, gbucks_reward, \
                 damage, rarity=RARITIES['base'], is_boss=False):
        super().__init__(id, type)
        self.hp = hp
        self.damage = damage
        self.rarity = rarity
        self.is_boss = is_boss
        self.exp_reward = exp_reward
        self.gbucks_reward = gbucks_reward

    def get_displayable(self):
        return {
            'id': self.id,
            'type': self.type,
            'hp': self.hp,
            'damage': self.damage,
            'rarity': self.rarity,
            'pos': vars(self.pos),
        }

    def __str__(self):
        return f'{self.id}({self.type}): {self.hp} [{self.rarity}]'


class BaseShipEnemy(Enemy):
    TYPE = 0
    BASE_HP = 100

    def __init__(self, id, hp=BASE_HP, rarity=Enemy.RARITIES['base']):
        super().__init__(
            id=id,
            type=self.TYPE,
            hp=hp,
            exp_reward=1,
            gbucks_reward=1,
            damage=10,
            rarity=rarity,
            is_boss=False
        )


class KamikazeShipEnemy(Enemy):
    TYPE = 1
    BASE_HP = 150

    def __init__(self, id, hp=BASE_HP, rarity=Enemy.RARITIES['base']):
        super().__init__(
            id=id,
            type=self.TYPE,
            hp=hp,
            exp_reward=2,
            gbucks_reward=2,
            damage=5,
            rarity=rarity,
            is_boss=False
        )


class InterceptorShipEnemy(Enemy):
    TYPE = 2
    BASE_HP = 200

    def __init__(self, id, hp=BASE_HP, rarity=Enemy.RARITIES['base']):
        super().__init__(
            id=id,
            type=self.TYPE,
            hp=hp,
            exp_reward=10,
            gbucks_reward=10,
            damage=40,
            rarity=rarity,
            is_boss=False
        )


class BossEnemy(Enemy):
    def __init__(self, id, type, hp, exp_reward, gbucks_reward, \
                 damage, rarity=Enemy.RARITIES['base']):
        super().__init__(
            id=id,
            type=type,
            hp=hp,
            exp_reward=exp_reward,
            gbucks_reward=gbucks_reward,
            damage=damage,
            rarity=rarity,
            is_boss=True
        )

    def attack(self, giorgio):
        pass


class ShitAssBossEnemy(BossEnemy):
    TYPE = 10
    BASE_HP = 5000

    def __init__(self, id, hp=BASE_HP, rarity=Enemy.RARITIES['base']):
        super().__init__(
            id=id,
            type=self.TYPE,
            hp=hp,
            exp_reward=1000,
            gbucks_reward=1000,
            damage=10,
            rarity=rarity
        )

    def attack(self, giorgio):
        # giorgio.generate_enemies(100, 0)
        print('ShitAss is attacking you.')


ENEMY_TYPES  = {
    'ship': (BaseShipEnemy.TYPE, BaseShipEnemy),
    'kamikaze': (KamikazeShipEnemy.TYPE, KamikazeShipEnemy),
    'interceptor': (InterceptorShipEnemy.TYPE, InterceptorShipEnemy),
}

BOSS_TYPES = {
    'shitass': (ShitAssBossEnemy.TYPE, ShitAssBossEnemy),
}
