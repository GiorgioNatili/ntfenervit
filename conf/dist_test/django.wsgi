import os
import sys

sys.path.append('/var/www/test/')
sys.path.append('/var/www/test/yellowPage')
sys.path.append('/var/www/test/survey')
sys.path.append('/var/www/test/contacts')
sys.path.append('/var/www/test/campaigns')

os.environ['PYTHON_EGG_CACHE'] = '/var/www/test/.python-egg'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_test'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

