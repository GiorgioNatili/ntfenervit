from django.contrib.auth.models import User, Group
from django.db.models import Q


def group(user):
    group_ = None
    user_groups = user.groups.all()
    if user_groups:
        group_ = user_groups[0]
    return group_

def is_user_in_groups(user, *groups):
    """
    :param user:
    :return: Boolean
    """
    group_ = group(user)
    if user.is_superuser or (group_ and group_.name in groups):
        return True
    return False

def get_its_users():
    ids = Group.objects.filter(Q(name='ITS') | Q(name='DISTRICT MANAGER ITS')).values_list('id')
    return User.objects.filter(groups__in=ids)


def is_backend_admin(user):
    '''
    Check if user can perform backend administrative functions.

    ToDo: This feature should be removed and replaced with actual permission list in the Utenti section

    :param user:  logged-in user
    :return:
    '''
    return user.is_superuser or is_user_in_groups(user, 'CONTROLLER', 'AMMINISTRATORE')

