import math

from django import template

register = template.Library()

def model_to_jsarray(val):
    return str(list(map(lambda s: s.value, val)))

def levelbar(val):
    val -= math.floor(val)
    return round(val * 100)

def levelbarwitdth(val):
    return str(levelbar(val)) + '%'

def rounddown(val):
    return math.floor(val)

def contained(val, dataset):
    return len(dataset.filter(pk=val)) > 0

def formatgbucks(val, zero_label=None):
    if val == 0:
        text = '0 @' if zero_label is None else zero_label
    elif val < 1000:
        text = '%d @' % val
    elif val < 1000000:
        text = '%gk @' % round(val / 1000.0, 1)
    else:
        text = '%gM @' % round(val / 1000000.0, 1)
    return text

register.filter('model_to_jsarray', model_to_jsarray)
register.filter('levelbarwitdth', levelbarwitdth)
register.filter('levelbar', levelbar)
register.filter('rounddown', rounddown)
register.filter('contained', contained)
register.filter('formatgbucks', formatgbucks)