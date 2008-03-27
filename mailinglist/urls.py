from django.conf.urls.defaults import *
from models import NewsLetter_Archive

urlpatterns = patterns('mailinglist.views',

    (r'^$', 'home'),
    
    (r'^aanmelden/$', 'request_subscription'),
    (r'^aanmelden/bevestigen/$', 'subscribe'),

    (r'^afmelden/$', 'request_unsubscription'),
	(r'^afmelden/bevestigen/$', 'unsubscribe'),

    # Special Admin Action for Newsletter
    (r'^admin/mailinglist/send_newsletter/$', 'select_newsletter'),	
	(r'^admin/mailinglist/send_newsletter/preview/(?P<format>\w+)/(?P<id>\d+)/$', 'preview_newsletter'),
	(r'^admin/mailinglist/send_newsletter/send/$', 'send_newsletter'),
	(r'^admin/mailinglist/send_newsletter/succes/$', 'send_newsletter_succes'),
	
    # Archive
	(r'^archief/$', 'archive'),
    (r'^archief/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[A-Za-z0-9-]+)$', 'archive_detail'),   
    
)
