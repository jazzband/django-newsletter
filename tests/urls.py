from django.conf.urls import include, url


urlpatterns = [
    url(r'^newsletter/', include('newsletter.urls')),
]
