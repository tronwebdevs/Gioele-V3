import math

from django import template

register = template.Library()

def model_to_jsarray(val):
    return str(list(map(lambda s: s.value, val)))

def levelbarwitdth(val):
    rounded = math.ceil(val)
    if rounded == val:
        rounded = val + 1
    return str(round(val * 100 / rounded)) + '%'

def levelbar(val):
    rounded = math.ceil(val)
    if rounded == val:
        rounded = val + 1
    return round(val * 100 / rounded)

def rounddown(val):
    return math.floor(val)

def contained(val, dataset):
    return len(dataset.filter(pk=val)) > 0

register.filter('model_to_jsarray', model_to_jsarray)
register.filter('levelbarwitdth', levelbarwitdth)
register.filter('levelbar', levelbar)
register.filter('rounddown', rounddown)
register.filter('contained', contained)