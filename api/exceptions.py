

class ParseException(Exception):
    def  __init__(self, message="Unable to parse database field value"):
        self.message = message
        super.__init__(self.message)