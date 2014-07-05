# -*- coding: utf-8 -*-
# Django settings for YellowPage project.

import os
import sys
import json

# Read the config file if exists
__config_file = os.path.splitext(os.path.basename(__file__))[0] + ".json"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), __config_file)
__config = None

if os.path.isfile(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as fh:
            __config = json.load(fh)
    except Exception as e:
        sys.stderr.write("Configuration Error: Failed to read '%s' with error '%s'" (CONFIG_FILE, e))

def getConfig(key, default=None):
    if __config and key in __config:
        # print "!!! returning from config: %s" % str(__config[key])
        return __config[key]
    else:
        # print "!!! returning from default: %s" % str(default)
        return default

# Start the normal settings.py section
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__)+'/..')

DEBUG = getConfig("DEBUG", True)
TEMPLATE_DEBUG = getConfig("TEMPLATE_DEBUG", DEBUG)

ADMINS = getConfig("ADMINS", ())

ROOT_URL = getConfig("ROOT_URL","http://localhost:8000")

MANAGERS = getConfig("ADMINS", ADMINS)

__databases = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yellowpagedb',
        'USER': 'enervit',
        'PASSWORD': 'enervitdev',
        'HOST': '',
        'PORT': ''
    }
}
DATABASES = getConfig("DATABASES", __databases)

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = getConfig("ALLOWED_HOSTS", ['localhost', '127.0.0.1'])

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = getConfig("TIME_ZONE", 'Europe/Rome')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = getConfig("LANGUAGE_CODE", 'it-IT')

SITE_ID = getConfig("SITE_ID", 1)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = getConfig("USE_I18N", True)

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = getConfig("USE_L10N", True)

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = getConfig("USE_TZ", True)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, getConfig("MEDIA_SUBDIR", 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = getConfig("MEDIA_URL", '/media/')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, getConfig("STATIC_SUBDIR", 'static'))

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = getConfig("STATIC_URL", '/static/')

# Additional locations of static files
__staticfiles_dirs = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'staticfiles'),
)
STATICFILES_DIRS = getConfig("STATICFILES_DIRS", __staticfiles_dirs)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = getConfig("SECRET_KEY", 'g%eh7ov*xub8=-*q*165h%(9bo%#$x7%e_*gqftsp(pim7jav@')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'yellowPage.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'yellowPage.wsgi.application'


TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), '..', getConfig("STATIC_SUBDIR", 'templates')).replace('\\','/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    #'tinymce',
    'haystack',
    'redactor',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'south',
    'contacts',
    'survey',
    'campaigns',
    'registration',
    'cabinet',

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)
REDACTOR_OPTIONS = getConfig("REDACTOR_OPTIONS", {'lang': 'it'})
REDACTOR_UPLOAD = getConfig("REDACTOR_UPLOAD", 'uploads/')

# Django registration settings
ACCOUNT_ACTIVATION_DAYS = getConfig("ACCOUNT_ACTIVATION_DAYS", 7)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGIN_REDIRECT_URL = getConfig("LOGIN_REDIRECT_URL", '/frontend/main')

EMAIL_BACKEND = getConfig("EMAIL_BACKEND", None)
EMAIL_HOST = getConfig("EMAIL_HOST", "localhost")
EMAIL_HOST_USER = getConfig("EMAIL_HOST_USER", 'testuser')
EMAIL_HOST_PASSWORD = getConfig("EMAIL_HOST_PASSWORD", 'testpassword')
EMAIL_FROM = getConfig("EMAIL_FROM", 'ENERVIT-DEV <no-reply@example.com>')
EMAIL_PORT = getConfig("EMAIL_PORT", 8025)
EMAIL_USE_TLS = getConfig("EMAIL_USE_TLS", False)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), getConfig("HAYSTACK_INDEX_SUBDIR", 'whoosh_index')),
    },
}
