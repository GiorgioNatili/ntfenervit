from django.conf.urls import patterns, url

__author__ = 'dominik'

urlpatterns = patterns(
    "",
    url(r'^eventcoupon/$', 'coupon.views.view_eventcoupon'),
    # url(r'^eventcoupon/export/(\d+)$', 'campaigns.views.view_eventcoupon_export'),
    # url(r'^restcoupon/generate', 'campaigns.views.view_eventcoupon_restgenerate'),
    url(r'^eventcoupon/generate/(\d+)$', 'coupon.views.view_eventcoupon_generate'),
    url(r'^couponbyevent/(\d+)$','coupon.views.view_couponbyevent', name='view_couponbyevent'),
    url(r'^delete/(\d+)/(\d+)$','coupon.views.delete_couponset', name='delete_couponset'),
    url(r'^delete_single/(\d+)$','coupon.views.delete_coupon', name='delete_single_coupon'),
    url(r'^couponset/(\d+)/(\d+)$','coupon.views.view_couponset', name='view_couponset'),
    url(r'^couponset/export/(\d+)$','coupon.views.export_couponset', name='export_couponset'),
    url(r'^couponset/export_all/(\d+)$','coupon.views.export_event_couponsets', name='export_event_allcoupons'),
    )