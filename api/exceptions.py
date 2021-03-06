

class ParseException(Exception):
    def  __init__(self, message="Unable to parse database field value"):
        self.message = message
        super().__init__(self.message)


class NotEnoughtCoins(Exception):
    def  __init__(self, message="This user doesn't have enought coins"):
        self.message = message
        super().__init__(self.message)


class AlreadyExist(Exception):
    def  __init__(self, message="Value already exists"):
        self.message = message
        super().__init__(self.message)


class GameException(Exception):
    GENERIC = 0
    INVALID_ACTION = 1
    GAME_END = 2
    GAME_NOT_STARTED = 3
    GAME_ALREADY_STARTED = 4
    ENTITY_NOT_FOUND = 5
    INVALID_DATA = 6
    CHEAT_DETECTED = 7
    PLAYER_DEAD = 8

    def __init__(self, message, code=GENERIC):
        self.message = message
        self.code = code
        super().__init__(self.message)


class GameEndException(GameException):
    def __init__(self, reason):
        super().__init__(reason, code=GameException.GAME_END)


class GameDataException(GameException):
    def __init__(self, param):
        self.param = param
        super().__init__('Invalid data (%s)' % param, GameException.INVALID_DATA)


class GameCheatDetectedException(GameException):
    def __init__(self, message):
        super().__init__('[Giovanni] ' + message, GameException.CHEAT_DETECTED)


class PlayerDead(GameException):
    def __init__(self, message):
        super().__init__(message, GameException.PLAYER_DEAD)
