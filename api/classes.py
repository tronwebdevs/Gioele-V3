import hashlib
import inspect

from .exceptions import ParseException


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


class Displayable:
    def to_safe_dict(self, remove_fields=()):
        if not hasattr(self, '_meta'):
            return None

        data = self.to_dict(safe=True)
        for field in remove_fields:
            data.pop(field, None)
        return data

    def to_dict(self, safe=False):
        if not hasattr(self, '_meta'):
            return None
        
        data = {}
        for field in self._meta.get_fields():
            fname = field.name
            if fname.startswith('_'):
                continue

            if safe and (fname == 'created_at' or fname == 'updated_at'):
                continue

            if field.get_internal_type() == 'DateTimeField':
                data[fname] = str(getattr(self, fname))
            else:
                if hasattr(self, fname):
                    attr = getattr(self, fname)
                    if issubclass(attr.__class__, Displayable):
                        if safe:
                            attr = attr.to_safe_dict()
                        else:
                            attr = attr.to_dict()
                    data[fname] = attr
        return data



"""
Parser definition:
dict: `item_1_id:level_item_1|item_2_id:level_item_2|...|item_N_id:level_item_N`
list: `item_1_id|item_2_id|...|item_N_id`
"""
class Parser:
    ITEM_SEPARATOR = '|'
    DICT_SEPARATOR = ':'

    def string_to_dicts(self, val, key_name='id', value_name='level'):
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

    def dicts_to_string(self, val):
        temp = list()
        for item in val:
            key1, key2 = item
            temp.append(str(item[key1]) + self.DICT_SEPARATOR + str(item[key2]))
        return self.ITEM_SEPARATOR.join(temp)

    def dict_to_string(self, val):
        temp = list()
        for key in val:
            temp.append(str(key) + self.DICT_SEPARATOR + str(val[key]))
        return self.ITEM_SEPARATOR.join(temp)

    def string_to_list(self, val):
        if val == '' or val is None:
            return list()
        return val.split(self.ITEM_SEPARATOR)

    def list_to_string(self, val):
        if len(val) == 0 or val is None:
            return None
        return self.ITEM_SEPARATOR.join(val)
