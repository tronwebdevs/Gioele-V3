import hashlib

from .exceptions import ParseException


class UserItem(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def get_displayable_id(self):
        return hashlib.md5(self.id.encode()).hexdigest()

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


"""
Parser definition: all items owned by the player are sotred in the database in
the format `item_1_id:level_item_1|item_2_id:level_item_2|...|item_N_id:level_item_N`.
The string must be less than 256 characters long.
"""
class Parser:
    ITEM_SEPARATOR = '|'
    DICT_SEPARATOR = ':'

    def to_dict_list(self, val, key_name='id', value_name='level'):
        result = []
        if val is None:
            return result
        for item in val.split(self.ITEM_SEPARATOR):
            t = item.split(self.DICT_SEPARATOR)
            if len(t) != 2:
                raise ParseException('Input value: "' + val + '"')
            item_id, level = t
            try:
                item_level = int(level)
            except ValueError:
                raise ParseException()
            result.append({
                key_name: item_id,
                value_name: item_level
            })
        return result

    def from_dict_list(self, val):
        temp = list()
        for item in val:
            key1, key2 = item
            temp.append(str(item[key1]) + self.DICT_SEPARATOR + str(item[key2]))
        return self.ITEM_SEPARATOR.join(temp)

    def to_str_list(self, val):
        if val is None:
            return list()
        return val.split(self.ITEM_SEPARATOR)

    def from_str_list(self, val):
        if val == '' or val is None:
            return None
        return self.ITEM_SEPARATOR.join(val)
