from django.conf.urls.defaults import *


urlpatterns = patterns('newsletter.views',
    # TODO: Use surlex here to simplify regexes
    url(r'^$', 'newsletter_list', name='newsletter_list'),

    url(r'^(?P<newsletter_slug>[-\w]+)/$','newsletter_detail', name='newsletter_detail'),

    url(r'^(?P<newsletter_slug>[-\w]+)/subscribe/$', 'subscribe_request', name='newsletter_subscribe_request'),
    url(r'^(?P<newsletter_slug>[-\w]+)/subscribe/confirm/$', 'subscribe_request', kwargs={'confirm':True}, name='newsletter_subscribe_confirm'),
    url(r'^(?P<newsletter_slug>[-\w]+)/update/$', 'update_request', name='newsletter_update_request'),
    url(r'^(?P<newsletter_slug>[-\w]+)/unsubscribe/$', 'unsubscribe_request', name='newsletter_unsubscribe_request'),
    url(r'^(?P<newsletter_slug>[-\w]+)/unsubscribe/confirm/$', 'unsubscribe_request', kwargs={'confirm':True}, name='newsletter_unsubscribe_confirm'),

    url(r'^(?P<newsletter_slug>[-\w]+)/subscription/(?P<email>[-_a-zA-Z0-9@\.\+~]+)/(?P<action>[a-z]+)/activate/(?P<activation_code>[a-zA-Z0-9]+)/$', 'update_subscription', name='newsletter_update_activate'),
    url(r'^(?P<newsletter_slug>[-\w]+)/subscription/(?P<email>[-_a-zA-Z0-9@\.\+~]+)/(?P<action>[a-z]+)/activate/$', 'update_subscription', name='newsletter_update'),

    url(r'^(?P<newsletter_slug>[-\w]+)/archive/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$', 'archive_detail', name='newsletter_archive_detail'),
    url(r'^(?P<newsletter_slug>[-\w]+)/archive/$', 'archive', name='newsletter_archive'),
)