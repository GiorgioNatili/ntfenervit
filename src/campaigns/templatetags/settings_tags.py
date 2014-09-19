__author__ = 'dominik'
from django import template
from django.conf import settings
register = template.Library()

ALLOWABLE_VALUES = ['GOOGLE_MAP_API_KEY']


@register.simple_tag
def settings_value(var_name):

    is_allowable = var_name in ALLOWABLE_VALUES
    if is_allowable:
        return getattr(settings, var_name, '')
    return ''

