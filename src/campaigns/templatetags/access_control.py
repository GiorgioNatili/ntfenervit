#TODO to move it in another app (to create a general app)
#  since these tags are used in many places
from campaigns.models import is_its as is_its_util

__author__ = 'dominik'

from django import template
from backend.utils import group, is_user_in_groups, is_backend_admin
register = template.Library()


@register.filter
def is_its(user_):
    return is_its_util(user_)

@register.filter
def is_group(user_, group_name_):
    return is_user_in_groups(user_, group_name_)

@register.filter(name='group')
def group_name(user_):
    return group(user_).name

register.filter('group', group_name)
register.filter('is_backend_admin', is_backend_admin)