from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/(ref|cert|event)/(\d+)$','cabinet.views.view_user_file'),
    url(r'^(\d+)/(ref|cert|event)/add$','cabinet.views.view_user_file_add')
)
