from django.conf.urls.defaults import *

from surlex.dj import surl

from .views import (
    NewsletterListView, NewsletterDetailView,
    SubmissionArchiveIndexView, SubmissionArchiveDetailView,
    SubscribeRequestView, UnsubscribeRequestView, UpdateRequestView,
    UpdateSubscriptionViev
)

urlpatterns = patterns('newsletter.views',
    # Newsletter list and detail view
    surl('^$', NewsletterListView.as_view(), name='newsletter_list'),
    surl(
        '^<newsletter_slug:s>/$',
        NewsletterDetailView.as_view(), name='newsletter_detail'
    ),

    # Action request views
    surl(
        '^<newsletter_slug:s>/subscribe/$',
        SubscribeRequestView.as_view(),
        name='newsletter_subscribe_request'
    ),
    surl(
        '^<newsletter_slug:s>/subscribe/confirm/$',
        SubscribeRequestView.as_view(confirm=True),
        name='newsletter_subscribe_confirm'
    ),
    surl(
        '^<newsletter_slug:s>/update/$',
        UpdateRequestView.as_view(),
        name='newsletter_update_request'
    ),
    surl(
        '^<newsletter_slug:s>/unsubscribe/$',
        UnsubscribeRequestView.as_view(),
        name='newsletter_unsubscribe_request'
    ),
    surl(
        '^<newsletter_slug:s>/unsubscribe/confirm/$',
        UnsubscribeRequestView.as_view(confirm=True),
        name='newsletter_unsubscribe_confirm'
    ),

    # Action confirmation views
    surl(
        '^<newsletter_slug:s>/subscription/<email=[-_a-zA-Z0-9@\.\+~]+>/'
        '<action=subscribe|update|unsubscribe>/activate/<activation_code:s>/$',
        UpdateSubscriptionViev.as_view(), name='newsletter_update_activate'
    ),
    surl(
        '^<newsletter_slug:s>/subscription/<email=[-_a-zA-Z0-9@\.\+~]+>/'
        '<action=subscribe|update|unsubscribe>/activate/$',
        UpdateSubscriptionViev.as_view(), name='newsletter_update'
    ),

    # Archive views
    surl(
        '^<newsletter_slug:s>/archive/<year:Y>/<month:m>/<day:d>/<slug:s>/$',
        SubmissionArchiveDetailView.as_view(), name='newsletter_archive_detail'
    ),
    surl(
        '^<newsletter_slug:s>/archive/$',
        SubmissionArchiveIndexView.as_view(), name='newsletter_archive'
    ),
)
