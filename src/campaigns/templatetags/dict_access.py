__author__ = 'dominik'

from django import template
register = template.Library()

def get_item(dictionary, key):
    return dictionary.get(str(key))

register.filter('get_item', get_item)