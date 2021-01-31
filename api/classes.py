class UserItem(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return f'{self.id}-{self.name}'


class UserGun(UserItem):
    def __init__(self, id, name=None, level=1):
        self.level = level
        super().__init__(id, name)

    def __str__(self):
        return super().__str__() + ':' + self.level


class UserSkin(UserItem):
    pass