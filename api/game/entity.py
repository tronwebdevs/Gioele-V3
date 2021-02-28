import random

from django.utils import timezone

from api.game.constants import CLIENT_CANVAS_WIDTH, CLIENT_MAX_CANVAS_DEPTH

class Position:
    CLOSE_DISTANCE_TOLLERATION = 5

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def generate(self):
        # FIXME: bad entity's position generation
        # see: https://stackoverflow.com/a/2145551
        shuffled_x = list(range(15, CLIENT_CANVAS_WIDTH - 15))
        shuffled_y = list(range(0, CLIENT_MAX_CANVAS_DEPTH))
        random.shuffle(shuffled_x)
        random.shuffle(shuffled_y)
        self.x = random.choice(shuffled_x)
        self.y = random.choice(shuffled_y) * -1

    def check(self, pos1):
        return abs(self.x - pos1.x) < self.CLOSE_DISTANCE_TOLLERATION \
             or abs(self.y - pos1.y) < self.CLOSE_DISTANCE_TOLLERATION


class Entity:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.pos = Position()
        self.pos.generate()
        self.born_at = timezone.now()
