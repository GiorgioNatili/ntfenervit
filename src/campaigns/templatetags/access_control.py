#TODO to move it in another place since these tags are used in many places
from campaigns.models import is_its as is_its_util

__author__ = 'dominik'

from django import template
from backend.utils import group, is_user_in_groups, is_backend_admin
register = template.Library()


def is_its(user_):
    return is_its_util(user_)


def is_group(user_, group_name_):
    return is_user_in_groups(user_, group_name_)


def group_name(user_):
    return group(user_).name

register.filter('is_its', is_its)
register.filter('is_group', is_group)
register.filter('group', group_name)
register.filter('is_backend_admin', is_backend_admin)