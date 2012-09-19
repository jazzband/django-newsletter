from django.conf.urls.defaults import patterns, include


urlpatterns = patterns('',
    (r'^newsletter/', include('newsletter.urls')),
)
