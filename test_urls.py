from django.conf.urls import *


urlpatterns = patterns('',
    (r'^newsletter/', include('newsletter.urls')),
)