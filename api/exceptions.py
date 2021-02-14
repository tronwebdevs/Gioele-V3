

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
    def __init__(self, message, code=-1):
        self.message = message
        self.code = code
        super().__init__(self.message)
