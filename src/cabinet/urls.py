from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(\d+)/(ref|cert)/add$','cabinet.views.view_user_file_add'),
    url(r'^(\d+)/(ref|cert)/(\d+)$','cabinet.views.view_user_file')
)