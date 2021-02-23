from django import template

register = template.Library()

def model_to_jsarray(val):
    return str(list(map(lambda s: s.value, val)))

register.filter('model_to_jsarray', model_to_jsarray)