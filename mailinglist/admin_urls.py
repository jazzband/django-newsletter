from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('mailinglist','django.conf'),}),
)

urlpatterns += patterns('mailinglist.admin_views',
    # (r'^json/message/(.+)/subscribers/$', 'json_subscribers'),
    # (r'^submission/(.+)/submit/$', 'submit'),
    (r'^subscription/import/$', 'import_subscribers'),
    (r'^subscription/import/confirm/$', 'confirm_import_subscribers'),
)

