from django.conf.urls.defaults import *

urlpatterns = patterns('',

    # Uncomment this for use with static files and media. Don't use this in a production environment!
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
               {'document_root': 'static/'}),
               
    # Newsletter, before admin!
     (r'^', include('newsletter.mailinglist.urls')),    
	
    # Admin
     (r'^admin/', include('django.contrib.admin.urls')),
     
 
)
