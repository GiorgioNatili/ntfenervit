# Django settings for YellowPage project.

import os.path

# -*- coding: utf-8 -*-
from django.contrib import messages

PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__)+'/..')


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

ROOT_URL = "http://testenervit.mochunk.com/" 


MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'yellowpagedev',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'enervitdev',
        'PASSWORD': 'devel02',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'it-IT'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'staticfiles'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'g%eh7ov*xub8=-*q*165h%(9bo%#$x7%e_*gqftsp(pim7jav@'

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

import os
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\','/'),)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
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
    'coupon',

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)
REDACTOR_OPTIONS = {'lang': 'it'}
REDACTOR_UPLOAD = 'uploads/'

# Django registration settings
ACCOUNT_ACTIVATION_DAYS = 7


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

LOGIN_REDIRECT_URL = '/frontend/main'

#EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'

EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com" #'mailtrap.io'#'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_USER = 'AKIAJZMTMFKG57XDSWUA' #'AKIAJIU544ECRF35H5AA'
EMAIL_HOST_PASSWORD = 'AgWau87uAAnlK48A52o1QHJX11lo2+a5jtPEutI7KNtY' #'ArzHgFmhQySgou18TKyyXwte4Kq/uqd2uwhnODXvmuB8'
EMAIL_FROM = 'ENERVIT <no-reply@enervit.it>' #'Christian Ferranti <cferranti@mochunk.com>'
DEFAULT_FROM_EMAIL = EMAIL_FROM
EMAIL_PORT = 465
EMAIL_USE_TLS = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}

#SURVEY app
#this setting serve to find the threshold date
# for a survey to be considered as abandoned
#It's the maximum number of days passed since
# last access to the survey to be considered
# as Active (in corso)
SURVEY_ACTIVE_DAYS = 15

GOOGLE_MAP_API_KEY = 'AIzaSyDvwBg4JHzHXh4DISNEtFJwhYaMX0jv2ic'
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

