def group(user):
    group_ = None
    user_groups = user.groups.all()
    if user_groups:
        group_ = user_groups[0]
    return group_


def is_controller(user):
    group_ = group(user)
    if user.is_superuser or (group_ and group_.name in ('CONTROLLER', 'AMMINISTRATORE')):
        return True
    return False
