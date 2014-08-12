from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import cabinet

#from frontend.views import MyRegistrationView
admin.autodiscover()

handler404 = 'campaigns.views.view_404'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'YellowPage.views.home', name='home'),
    # url(r'^YellowPage/', include('YellowPage.foo.urls')),

    url(r'^$','frontend.views.view_home'),
    url(r'^testuser/','frontend.views.test_user'),
    url(r'^frontend/main/','frontend.views.view_main'),
    url(r'^frontend/contactme/','frontend.views.view_contact'),
    url(r'^frontend/signup/','frontend.views.view_signup'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^survey/', include('survey.urls')),
    url(r"^ajax/photos/upload/$", "campaigns.views.upload_photos"),
    url(r"^ajax/photos/recent/$", "campaigns.views.recent_photos",),
    url(r'^redactor/', include('redactor.urls')),
    url(r'^newsletter/unsubscribe','campaigns.views.view_unsubscribe'),
    url(r'^admin/contacts/company/$', 'contacts.views.view_company'),
    url(r'^admin/contacts/company/add/$', 'contacts.views.view_add_company'),
    url(r'^admin/contacts/company/(\d+)/$', 'contacts.views.view_company_details'),

    url(r'^admin/contacts/division/$', 'contacts.views.view_division'),
    url(r'^admin/contacts/division/add/$', 'contacts.views.view_add_division'),
    url(r'^admin/contacts/division/(\d+)/$', 'contacts.views.view_division_details'),

    url(r'^admin/contacts/subdivision/$', 'contacts.views.view_subdivision'),
    url(r'^admin/contacts/subdivision/add/$', 'contacts.views.view_add_subdivision'),
    url(r'^admin/contacts/subdivision/(\d+)/$', 'contacts.views.view_subdivision_details'),
    url(r'^admin/contacts/rest/subdivision', 'contacts.views.view_subdivision_rest'),

    url(r'^admin/contacts/sector/$', 'contacts.views.view_sector'),
    url(r'^admin/contacts/sector/add/$', 'contacts.views.view_add_sector'),
    url(r'^admin/contacts/sector/(\d+)/$', 'contacts.views.view_sector_details'),

    url(r'^admin/contacts/work/$', 'contacts.views.view_work'),
    url(r'^admin/contacts/work/add/$', 'contacts.views.view_add_work'),
    url(r'^admin/contacts/work/(\d+)/$', 'contacts.views.view_work_details'),
    url(r'^admin/contacts/rest/work', 'contacts.views.view_work_rest'),

    url(r'^admin/contacts/contact/$', 'contacts.views.view_contact'),
    url(r'^admin/contacts/contact/add/$', 'contacts.views.view_add_contact'),
    url(r'^admin/contacts/contact/import/$', 'contacts.views.view_contact_import'),
    url(r'^admin/contacts/contact/(\w+)/$', 'contacts.views.view_contact_details'),

    url(r'^admin/contacts/ranking/(\d+)/$', 'contacts.views.view_ranking_details'),

    url(r'^admin/campaigns/campaign/$', 'campaigns.views.view_campaign'),
    url(r'^admin/campaigns/campaign/add/$', 'campaigns.views.view_add_campaign'),
    url(r'^admin/campaigns/campaign/(\w+)/$', 'campaigns.views.view_campaign_details'),

    url(r'^admin/campaigns/areaits/$', 'campaigns.views.view_areeits'),
    url(r'^admin/campaigns/areaits/add/$', 'campaigns.views.view_add_areeits'),
    url(r'^admin/campaigns/areaits/(\d+)$', 'campaigns.views.view_areeits_details'),

    url(r'^admin/campaigns/areamanager/$', 'campaigns.views.view_areemanager'),
    url(r'^admin/campaigns/areamanager/add/$', 'campaigns.views.view_add_areemanager'),
    url(r'^admin/campaigns/areamanager/(\d+)$', 'campaigns.views.view_areemanager_details'),

    url(r'^admin/campaigns/theme/$', 'campaigns.views.view_theme'),
    url(r'^admin/campaigns/theme/add/$', 'campaigns.views.view_add_theme'),
    url(r'^admin/campaigns/theme/(\d+)$', 'campaigns.views.view_theme_details'),

    url(r'^admin/campaigns/goal/$', 'campaigns.views.view_goal'),
    url(r'^admin/campaigns/goal/add/$', 'campaigns.views.view_add_goal'),
    url(r'^admin/campaigns/goal/(\d+)$', 'campaigns.views.view_goal_details'),

    url(r'^admin/campaigns/channel/$', 'campaigns.views.view_channel'),
    url(r'^admin/campaigns/channel/add/$', 'campaigns.views.view_add_channel'),
    url(r'^admin/campaigns/channel/(\d+)$', 'campaigns.views.view_channel_details'),

    url(r'^admin/campaigns/pointofsaletype/$', 'campaigns.views.view_pointofsaletype'),
    url(r'^admin/campaigns/pointofsaletype/add/$', 'campaigns.views.view_add_pointofsaletype'),
    url(r'^admin/campaigns/pointofsaletype/(\d+)$', 'campaigns.views.view_pointofsaletype_details'),

    url(r'^admin/campaigns/pointofsaletype/$', 'campaigns.views.view_pointofsaletype'),
    url(r'^admin/campaigns/pointofsaletype/add/$', 'campaigns.views.view_add_pointofsaletype'),
    url(r'^admin/campaigns/pointofsaletype/(\d+)$', 'campaigns.views.view_pointofsaletype_details'),

    url(r'^admin/campaigns/eventtype/$', 'campaigns.views.view_eventtype'),
    url(r'^admin/campaigns/eventtype/add/$', 'campaigns.views.view_add_eventtype'),
    url(r'^admin/campaigns/eventtype/(\d+)$', 'campaigns.views.view_eventtype_details'),

    url(r'^admin/campaigns/productgroup/$', 'campaigns.views.view_productgroup'),
    url(r'^admin/campaigns/productgroup/add/$', 'campaigns.views.view_add_productgroup'),
    url(r'^admin/campaigns/productgroup/(\d+)$', 'campaigns.views.view_productgroup_details'),


    url(r'^admin/coupons/', include('coupon.urls')),


    url(r'^admin/campaigns/newsletter/$', 'campaigns.views.view_newsletter'),
    url(r'^admin/campaigns/newsletter/add/$', 'campaigns.views.view_add_newsletter'),
    url(r'^admin/campaigns/newsletter/(\d+)/$', 'campaigns.views.view_newsletter_details'),
    url(r'^admin/campaigns/newsletter/test/(\d+)', 'campaigns.views.test_newsletter'),
    url(r'^admin/campaigns/newsletter/tasks', 'campaigns.views.tasks_newsletter'),
    url(r'^admin/campaigns/newsletter/schedule/add/$', 'campaigns.views.add_schedule_newsletter'),
    url(r'^admin/campaigns/newsletter/schedule/(\d+)/$', 'campaigns.views.schedule_newsletter_details'),
    url(r'^admin/campaigns/newsletter/schedule/(\d+)/delete', 'campaigns.views.schedule_newsletter_delete'),
    url(r'^admin/campaigns/newsletter/single','campaigns.views.send_single_newsletter'),
    url(r'^admin/campaigns/newsletter/sendsingleemail','campaigns.views.send_single_email'),

    url(r'^admin/campaigns/event/$','campaigns.views.view_events'),
    url(r'^admin/campaigns/event/add/$', 'campaigns.views.view_add_event'),
    url(r'^admin/campaigns/event/import/$', 'campaigns.views.view_event_import'),
    url(r'^admin/campaigns/event/(\d+)/$', 'campaigns.views.view_event_details'),
    url(r'^admin/campaigns/rest/eventslist', 'campaigns.views.view_eventlist_rest'),
    url(r'^admin/campaigns/event/calendar', 'campaigns.views.view_calendar'),
    url(r'^admin/campaigns/event/signups', 'campaigns.views.view_signups'),
    url(r'^admin/campaigns/event/eventsignups/(\d+)/$', 'campaigns.views.view_signup_by_event'),
    url(r'^admin/campaigns/event/signup/(\d+)/$','campaigns.views.view_signup_details'),
    url(r'^admin/campaingis/eventi/signupexport/(\d+)/$','campaigns.views.view_export_signup_by_event'),

    url(r'^admin/campaigns/newslettertemplate/$','campaigns.views.view_newslettertemplate'),
    url(r'^admin/campaigns/newslettertemplate/add/$', 'campaigns.views.view_add_newslettertemplate'),
    url(r'^admin/campaigns/newslettertemplate/(\w+)/$', 'campaigns.views.view_newslettertemplate_details'),
    url(r'^admin/campaigns/rest/newslettertemplate', 'campaigns.views.view_newslettertemplate_rest'),

    url(r'^admin/campaigns/mailinglist','campaigns.views.view_newslettertarget'),
    #url(r'^admin/campaigns/newslettertarget/add/$', 'campaigns.views.view_add_newslettertarget'),
    url(r'^admin/campaigns/newslettertarget/(\d+)/$', 'campaigns.views.view_newslettertarget_add'),
    url(r'^admin/campaigns/rest/newslettertargetadd','campaigns.views.view_newslettertarget_add_rest'),
    url(r'^admin/campaigns/rest/newslettertargetaremove','campaigns.views.view_newslettertarget_remove_rest'),
    url(r'^admin/campaigns/rest/newslettertargetlist', 'campaigns.views.view_newslettertarget_list_rest'),

    url(r'^admin/survey/survey/$', 'survey.views.surveys_list'),
    url(r'^admin/survey/survey/add/$', 'survey.views.survey_add'),
    url(r'^admin/survey/survey/(\d+)/$', 'survey.views.survey_details'),
    url(r'^admin/survey/questionadd/(\d+)/$', 'survey.views.question_add'),
    url(r'^admin/survey/questiondetails/(\d+)/$', 'survey.views.question_details'),
    url(r'^admin/survey/question/delete/(\d+)/$', 'survey.views.question_delete'),
    url(r'^admin/survey/report/$', 'survey.views.report_list'),
    url(r'^admin/survey/report/(\d+)$', 'survey.views.report_detail'),
    url(r'^admin/survey/report/details/(\d+)$', 'survey.views.single_report_detail'),

    url(r'^admin/backend/utenti/$','backend.views.user_list'),
    url(r'^admin/backend/utenti/add/','backend.views.user_add'),
    url(r'^admin/backend/utenti/details/(\d+)/$','backend.views.user_details'),

    url(r'^admin/backend/gruppi/$','backend.views.group_list'),
    url(r'^admin/backend/gruppi/add/','backend.views.group_add'),
    url(r'^admin/backend/gruppi/details/(\d+)/$','backend.views.group_details'),

    url(r'^admin/search/contact/$','contacts.views.search_contact'),
    url(r'^admin/search/contactexport/$','contacts.views.search_contact_export'),
    url(r'^admin/search/campaign/$','campaigns.views.search_campaign'),
    url(r'^admin/search/campaignexport/$','campaigns.views.search_campaign_export'),
    url(r'^admin/search/newsletter/$','campaigns.views.search_newsletter'),
    url(r'^admin/search/newsletterexport/$','campaigns.views.search_newsletter_export'),
    url(r'^admin/search/event/$','campaigns.views.search_event'),
    url(r'^admin/search/eventexport/$','campaigns.views.search_event_export'),
    url(r'^admin/search/certificate/$','cabinet.views.search_certificate'),

    url(r'^admin/campaigns/registro','campaigns.views.view_registro'),
    url(r'^admin/campaigns/eventpresence/export/(\d+)/$', 'campaigns.views.view_export_presence'),
    url(r'^admin/campaigns/eventpresence/(\d+)/$', 'campaigns.views.view_presence'),
    url(r'^admin/campaigns/rest/eventpresence', 'campaigns.views.view_presence_rest'),
    url(r'^admin/campaigns/eventsignup/add', 'campaigns.views.view_add_eventsignup'),

    url(r'^admin/rest/counter','campaigns.views.view_rest_counter'),

    url(r'^admin/cabinet/', include('cabinet.urls')),
    url(r'^admin/its/agenda', 'campaigns.views_its.its.view_agenda'),
    url(r'^admin/its/rest/eventslist', 'campaigns.views_its.its.view_eventlist_rest'),
    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls))

)
urlpatterns += patterns('',
                        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
                        )
urlpatterns += patterns('',
                        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
                        )
