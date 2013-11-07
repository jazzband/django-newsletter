from django.conf.urls import patterns, url

from .views import (
    NewsletterListView, NewsletterDetailView,
    SubmissionArchiveIndexView, SubmissionArchiveDetailView,
    SubscribeRequestView, UnsubscribeRequestView, UpdateRequestView,
    ActionTemplateView, UpdateSubscriptionViev,
)

urlpatterns = patterns('newsletter.views',
    # Newsletter list and detail view
    url('^$', NewsletterListView.as_view(), name='newsletter_list'),
    url(
        '^(?P<newsletter_slug>[\w-]+)/$',
        NewsletterDetailView.as_view(), name='newsletter_detail'
    ),

    # Action request views
    url(
        '^(?P<newsletter_slug>[\w-]+)/subscribe/$',
        SubscribeRequestView.as_view(),
        name='newsletter_subscribe_request'
    ),
    url(
        '^(?P<newsletter_slug>[\w-]+)/subscribe/confirm/$',
        SubscribeRequestView.as_view(confirm=True),
        name='newsletter_subscribe_confirm'
    ),
    url(
        '^(?P<newsletter_slug>[\w-]+)/update/$',
        UpdateRequestView.as_view(),
        name='newsletter_update_request'
    ),
    url(
        '^(?P<newsletter_slug>[\w-]+)/unsubscribe/$',
        UnsubscribeRequestView.as_view(),
        name='newsletter_unsubscribe_request'
    ),
    url(
        '^(?P<newsletter_slug>[\w-]+)/unsubscribe/confirm/$',
        UnsubscribeRequestView.as_view(confirm=True),
        name='newsletter_unsubscribe_confirm'
    ),

    # Activation email sent view
    url(
        '^(?P<newsletter_slug>[\w-]+)/'
        '(?P<action>(subscribe|update|unsubscribe))/email-sent/$',
        ActionTemplateView.as_view(
            template_name='newsletter/subscription_%(action)s_email_sent.html'
        ),
        name='newsletter_activation_email_sent'),

    # Action confirmation views
    url(
        '^(?P<newsletter_slug>[\w-]+)/subscription/'
        '(?P<email>[-_a-zA-Z0-9@\.\+~]+)/'
        '(?P<action>(subscribe|update|unsubscribe))/'
        'activate/(?P<activation_code>[\w-]+)/$',
        UpdateSubscriptionViev.as_view(), name='newsletter_update_activate'
    ),
    url(
        '^(?P<newsletter_slug>[\w-]+)/subscription/'
        '(?P<email>[-_a-zA-Z0-9@\.\+~]+)/'
        '(?P<action>(subscribe|update|unsubscribe))/activate/$',
        UpdateSubscriptionViev.as_view(), name='newsletter_update'
    ),

    # Action activation completed view
    url(
        '^(?P<newsletter_slug>[\w-]+)/'
        '(?P<action>(subscribe|update|unsubscribe))/activation-completed/$',
        ActionTemplateView.as_view(
            template_name='newsletter/subscription_%(action)s_activated.html'
        ),
        name='newsletter_action_activated'),

    # Archive views
    url(
        '^(?P<newsletter_slug>[\w-]+)/archive/'
        '(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/'
        '(?P<slug>[\w-]+)/$',
        SubmissionArchiveDetailView.as_view(), name='newsletter_archive_detail'
    ),
    url(
        '^(?P<newsletter_slug>[\w-]+)/archive/$',
        SubmissionArchiveIndexView.as_view(), name='newsletter_archive'
    ),
)
