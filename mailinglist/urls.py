from django.conf.urls.defaults import *

urlpatterns = patterns('mailinglist.views',
    # Admin shit
    #(r'^/admin/mailinglist/newsletter/(.+)/json/subscribers/$', 'json_subscribers'),

    # This one is to be removed later on
    (r'^$', 'newsletter_list'),
    
    (r'^(?P<newsletter_slug>[-\w]+)/$','newsletter'),
    
    (r'^(?P<newsletter_slug>[-\w]+)/subscribe/$', 'subscribe_request'),
    (r'^(?P<newsletter_slug>[-\w]+)/unsubscribe/$', 'unsubscribe_request'),
        
    #(r'^(?P<newsletter_slug>[-\w]+)/subscription/(?P<email>[.*]+)/$', 'update_subscription'),
    (r'^(?P<newsletter_slug>[-\w]+)/subscription/(?P<email>[-_a-zA-Z@\.]+)/(?P<action>[a-z]+)/activate/(?P<activation_code>[a-zA-Z0-9]+)/$', 'activate_subscription'),
    (r'^(?P<newsletter_slug>[-\w]+)/subscription/(?P<email>[-_a-zA-Z@\.]+)/(?P<action>[a-z]+)/activate/$', 'activate_subscription'),


    (r'^(?P<newsletter_slug>[-\w]+)/archive/$','archive'),
)

