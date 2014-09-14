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

def is_user_in_groups(user, *groups):
    group_ = group(user)
    if user.is_superuser or (group_ and group_.name in groups):
        return True
    return False

def is_its(user):
    """
    :param user:
    :return: Boolean
    """
    group_ = group(user)
    if group_ and group_.name in ('ITS', 'DISTRICT MANAGER ITS'):
        return True
    return False

def can_handle_events(user, e=None, new=False, from_its=False):
    res = is_backend_admin(user) \
        or (e is not None and e.owner is not None and e.owner == user and from_its) \
        or (is_its(user) and new and from_its)
    return res

def is_backend_admin(user):
    '''
    Check if user can perform backend administrative functions.

    ToDo: This feature should be removed and replaced with actual permission list in the Utenti section

    :param user:  logged-in user
    :return:
    '''
    return user.is_superuser or is_user_in_groups(user, 'CONTROLLER', 'AMMINISTRATORE')


