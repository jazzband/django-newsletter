from django.conf.urls.defaults import *

urlpatterns = patterns('mailinglist.views',

    # This one is to be removed later on
    (r'^$', 'newsletter_list'),
    
    (r'^(?P<newsletter_slug>[-\w]+)/$','newsletter'),
    (r'^(?P<newsletter_slug>[-\w]+)/subscribe/$', 'subscribe'),
    (r'^(?P<newsletter_slug>[-\w]+)/subscribe/activate/(?P<subscription_id>[0-9]+)/$', 'activate'),
    (r'^(?P<newsletter_slug>[-\w]+)/subscribe/activate/(?P<subscription_id>[0-9]+)/(?P<activation_code>[-\w]+)/$', 'activate'),
    (r'^(?P<newsletter_slug>[-\w]+)/unsubscribe/(?P<subscription_id>[0-9]+)/$', 'unsubscribe'),
    (r'^(?P<newsletter_slug>[-\w]+)/unsubscribe/activate/(?P<subscription_id>[0-9]+)/$', 'unsubscribe_activate'),
    (r'^(?P<newsletter_slug>[-\w]+)/unsubscribe/activate/(?P<subscription_id>[0-9]+)/(?P<activation_code>[-\w]+)/$', 'unsubscribe_activate'),    
    (r'^(?P<newsletter_slug>[-\w]+)/archive/$','archive'),
)

