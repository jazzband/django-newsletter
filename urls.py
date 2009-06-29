from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

from django.conf import settings
if settings.DEBUG:
    from os import path
    urlpatterns = patterns('django.views', (r'^static/(?P<path>.*)$', 'static.serve', {'document_root': path.join(settings.PROJECT_ROOT, 'static') }))
else:
    urlpatterns = patterns('')

urlpatterns = patterns('',

    # Uncomment this for use with static files and media. Don't use this in a production environment!
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
               {'document_root': 'static/'}),
               

    (r'^$', 'django.views.generic.simple.redirect_to',{'url': '/mailinglist/'}),
    (r'^mailinglist/', include('mailinglist.urls')),    

    # Django Admin
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

)
