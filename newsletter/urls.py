from django.conf.urls.defaults import *

urlpatterns = patterns('newsletter.views',
    url(r'^$', 'newsletter_list', name='newsletter_newsletter_list'),
    
    url(r'^(?P<newsletter_slug>[-\w]+)/$','newsletter_detail', name='newsletter_newsletter_detail'),

    url(r'^(?P<newsletter_slug>[-\w]+)/user/subscribe/$', 'subscribe_user', name='newsletter_newsletter_subscribe_user'),
    url(r'^(?P<newsletter_slug>[-\w]+)/user/unsubscribe/$', 'unsubscribe_user', name='newsletter_newsletter_unsubscribe_user'),
    
    url(r'^(?P<newsletter_slug>[-\w]+)/subscribe/$', 'subscribe_request', name='newsletter_newsletter_subscribe_request'),
    url(r'^(?P<newsletter_slug>[-\w]+)/update/$', 'update_request', name='newsletter_newsletter_update_request'),
    url(r'^(?P<newsletter_slug>[-\w]+)/unsubscribe/$', 'unsubscribe_request', name='newsletter_newsletter_unsubscribe_request'),
        
    url(r'^(?P<newsletter_slug>[-\w]+)/subscription/(?P<email>[-_a-zA-Z@\.]+)/(?P<action>[a-z]+)/activate/(?P<activation_code>[a-zA-Z0-9]+)/$', 'update_subscription', name='newsletter_newsletter_update_activate'),
    url(r'^(?P<newsletter_slug>[-\w]+)/subscription/(?P<email>[-_a-zA-Z@\.]+)/(?P<action>[a-z]+)/activate/$', 'update_subscription', name='newsletter_newsletter_update'),
    
    url(r'^(?P<newsletter_slug>[-\w]+)/archive/$','archive', name='newsletter_newsletter_archive'),
)

