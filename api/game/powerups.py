from api.game.entity import Entity


class PowerUp(Entity):
    def __init__(self, id, type, rnd):
        super().__init__(id, type, rnd)

    def activate(self, player):
        pass

    def deactivate(self, player):
        pass


class ShieldPowerUp(PowerUp):
    TYPE = 0

    def __init__(self, id, rnd):
        super().__init__(id, self.TYPE, rnd)
    
    def activate(self, player):
        player.reload_shield()

    def deactivate(self, player):
        player.reset_speed()


class FuelPowerUp(PowerUp):
    TYPE = 1

    def __init__(self, id, rnd):
        super().__init__(id, self.TYPE, rnd)
    
    def activate(self, player):
        player.speed_up()

    def deactivate(self, player):
        player.reset_speed()


class DamagePowerUp(PowerUp):
    TYPE = 2

    def __init__(self, id, rnd):
        super().__init__(id, self.TYPE, rnd)
    
    def activate(self, player):
        player.damage_up()

    def deactivate(self, player):
        player.reset_damage()


POWERUP_TYPES = {
    'shield': (ShieldPowerUp.TYPE, ShieldPowerUp),
    'fuel': (FuelPowerUp.TYPE, FuelPowerUp),
    'damage': (DamagePowerUp.TYPE, DamagePowerUp),
}
