from django.conf.urls.defaults import *

urlpatterns = patterns('mailinglist.views',

    # This one is to be removed later on
    (r'^$', 'newsletter_list'),
    
    (r'^(?P<newsletter_slug>[-\w]+)/$','newsletter'),
    (r'^(?P<newsletter_slug>[-\w]+)/subscribe/$', 'subscribe_request'),
    (r'^(?P<newsletter_slug>[-\w]+)/subscribe/(?P<subscription_id>[0-9]+)/$', 'subscribe_update'),
    (r'^(?P<newsletter_slug>[-\w]+)/unsubscribe/$', 'unsubscribe_request'),
    (r'^(?P<newsletter_slug>[-\w]+)/unsubscribe/(?P<subscription_id>[0-9]+)/$', 'unsubscribe_update'),
    (r'^(?P<newsletter_slug>[-\w]+)/archive/$','archive'),
)

