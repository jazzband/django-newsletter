from django.conf.urls.defaults import *

urlpatterns = patterns('mailinglist.views',
    # Admin shit
    (r'^json/message/(.+)/subscribers/$', 'json_subscribers'),
)
