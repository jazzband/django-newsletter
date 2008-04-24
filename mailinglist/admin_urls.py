from django.conf.urls.defaults import *

urlpatterns = patterns('mailinglist.admin_views',
    # Admin shit
    (r'^json/message/(.+)/subscribers/$', 'json_subscribers'),
    (r'^message/(.+)/preview/$', 'message_preview'),
    (r'^message/(.+)/preview/html/$', 'html_preview'),
    (r'^message/(.+)/preview/text/$', 'text_preview'),
    (r'^submission/(.+)/submit/$', 'submit'),
)
