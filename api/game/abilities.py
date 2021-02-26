from api.game.entity import Entity


class Ability(Entity):
    def __init__(self, id, type):
        super().__init__(id, type)

    def run(self, giorgio):
        pass


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


ABILITY_TYPES = {
    'wave': (WaveAbility.TYPE, WaveAbility),
    'hp_regen': (HpRegenAbility.TYPE, HpRegenAbility),
}
