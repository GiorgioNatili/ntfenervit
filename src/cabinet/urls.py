from django.conf.urls import patterns, include, url

urlpatterns = patterns('cabinet.views',
    url(r'^(\d+)/(ref|cert|event)/(\d+)$','view_user_file'),
    url(r'^(\d+)/(ref|cert|event)/add$','view_user_file_add')
)
