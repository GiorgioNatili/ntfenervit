from campaigns.models import Event
from django.contrib.auth.models import Group, User
import sys
sys.path.append('../../src')
__author__ = 'dominik'

a = Event.objects.exclude(districtmanager__isnull=True)
#TODO create its staff users for every AreaITS
#TODO associate its staff users to the event's field its_districtmanager
#  The association above will be based on the districtmanager value
#  which is an AreaIts
