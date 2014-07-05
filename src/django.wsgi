import os
import sys

sys.path.append('/var/www/yellowpage/')
sys.path.append('/var/www/yellowpage/yellowPage')
sys.path.append('/var/www/yellowpage/survey')
sys.path.append('/var/www/yellowpage/contacts')
sys.path.append('/var/www/yellowpage/campaigns')

os.environ['PYTHON_EGG_CACHE'] = '/var/www/yellowpage/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

