from django.conf.urls.defaults import *

from surlex.dj import surl


urlpatterns = patterns('newsletter.views',
    surl(r'^$', 'newsletter_list', name='newsletter_list'),

    surl(r'^<newsletter_slug:s>/$','newsletter_detail', name='newsletter_detail'),

    surl(r'^<newsletter_slug:s>/subscribe/$', 'subscribe_request', name='newsletter_subscribe_request'),
    surl(r'^<newsletter_slug:s>/subscribe/confirm/$', 'subscribe_request', kwargs={'confirm':True}, name='newsletter_subscribe_confirm'),
    surl(r'^<newsletter_slug:s>/update/$', 'update_request', name='newsletter_update_request'),
    surl(r'^<newsletter_slug:s>/unsubscribe/$', 'unsubscribe_request', name='newsletter_unsubscribe_request'),
    surl(r'^<newsletter_slug:s>/unsubscribe/confirm/$', 'unsubscribe_request', kwargs={'confirm':True}, name='newsletter_unsubscribe_confirm'),

    surl(r'^<newsletter_slug:s>/subscription/<email=[-_a-zA-Z0-9@\.\+~]+>/<action:s>/activate/<activation_code:s>/$', 'update_subscription', name='newsletter_update_activate'),
    surl(r'^<newsletter_slug:s>/subscription/<email=[-_a-zA-Z0-9@\.\+~]+>/<action:s>/activate/$', 'update_subscription', name='newsletter_update'),

    surl(r'^<newsletter_slug:s>/archive/<year:Y>/<month:m>/<day:d>/<slug:s>/$', 'archive_detail', name='newsletter_archive_detail'),
    surl(r'^<newsletter_slug:s>/archive/$', 'archive', name='newsletter_archive'),
)