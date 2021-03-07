def valid_string(val):
    return val is not None and val.strip() != ''

def valid_number(val):
    val_type = type(val)
    return val_type is int or val_type is float

def raise_if_not_valid(val, validator, field=None):
    if not validator(val):
        message = 'Invalid value'
        if field is not None:
            message = field + ': ' + message
        raise Exception(message)
    return val

def get_percentage(current, last):
    if last != 0:
        return str((current - last) * 100 / last) + '%'
    else:
        return '+0%'
