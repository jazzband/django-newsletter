from django.conf.urls import patterns, include


urlpatterns = patterns('',
    (r'^newsletter/', include('newsletter.urls')),
)
