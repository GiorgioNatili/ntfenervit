from campaigns.models import is_its as is_its_util

__author__ = 'dominik'

from django import template
from backend.utils import group as group_
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