from django.conf.urls import patterns, include, url

urlpatterns = patterns('cabinet.views',
    url(r'^(\w+)/(ref|cert|event)/(\d+)$','view_contact_file'),
    url(r'^(\w+)/(ref|cert|event)/add$','view_contact_file_add')
)
