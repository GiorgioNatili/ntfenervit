__author__ = 'dominik'

from django import template
from backend.utils import is_its as is_its_util, group as group_, is_backend_admin
register = template.Library()


def is_its(user):
    return is_its_util(user)


def is_group(user, group_name):
    g = group(user)
    return g == group_name


def group(user):
    return group_(user).name

register.filter('is_its', is_its)
register.filter('is_group', is_group)
register.filter('group', group)
register.filter('is_backend_admin', is_backend_admin)
