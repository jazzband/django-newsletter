from django.conf.urls.defaults import *

urlpatterns = patterns('',

    # Uncomment this for use with static files and media. Don't use this in a production environment!
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
               {'document_root': 'static/'}),
               

    (r'^$', 'django.views.generic.simple.redirect_to',{'url': '/mailinglist/'}),
    (r'^mailinglist/', include('newsletter.mailinglist.urls')),    
	
    # Admin
     (r'^admin/', include('django.contrib.admin.urls')),
     
 
)
