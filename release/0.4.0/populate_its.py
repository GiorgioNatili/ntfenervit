from campaigns.models import Event
from django.contrib.auth.models import Group, User

__author__ = 'dominik'


a = Event.objects.exclude(districtmanager__isnull=True)
