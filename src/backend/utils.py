from django.contrib.auth.models import User, Group
from django.db.models import Q

__author__ = 'dominik'


def get_its_users():
    ids = Group.objects.filter(Q(name='ITS') | Q(name='DISTRICT MANAGER ITS')).values_list('id')
    return User.objects.filter(groups__in=ids)

def group(user):
    group_ = None
    user_groups = user.groups.all()
    if user_groups:
        group_ = user_groups[0]
    return group_


def is_its(user):
    group_ = group(user)
    if group and group_.name in ('ITS', 'DISTRICT MANAGER ITS'):
        return True
    return False