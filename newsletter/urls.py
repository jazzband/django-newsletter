from django.urls import re_path, register_converter

from .converters import NewsletterActionsConverter
from .views import (
    NewsletterListView, NewsletterDetailView,
    SubmissionArchiveIndexView, SubmissionArchiveDetailView,
    SubscribeRequestView, UnsubscribeRequestView, UpdateRequestView,
    ActionTemplateView, UpdateSubscriptionView,
)

register_converter(NewsletterActionsConverter, 'actions')

urlpatterns = [
    # Newsletter list and detail view
    re_path('', NewsletterListView.as_view(), name='newsletter_list'),
    re_path(
        '<newsletter_slug>/',
        NewsletterDetailView.as_view(), name='newsletter_detail'
    ),

    # Action request views
    re_path(
        '<newsletter_slug>/subscribe/',
        SubscribeRequestView.as_view(),
        name='newsletter_subscribe_request'
    ),
    re_path(
        '<newsletter_slug>/subscribe/confirm/',
        SubscribeRequestView.as_view(confirm=True),
        name='newsletter_subscribe_confirm'
    ),
    re_path(
        '<newsletter_slug>/update/',
        UpdateRequestView.as_view(),
        name='newsletter_update_request'
    ),
    re_path(
        '<newsletter_slug>/unsubscribe/',
        UnsubscribeRequestView.as_view(),
        name='newsletter_unsubscribe_request'
    ),
    re_path(
        '<newsletter_slug>/unsubscribe/confirm/',
        UnsubscribeRequestView.as_view(confirm=True),
        name='newsletter_unsubscribe_confirm'
    ),

    # Activation email sent view
    re_path(
        '<newsletter_slug>/<actions:action>/email-sent/',
        ActionTemplateView.as_view(
            template_name='newsletter/subscription_%(action)s_email_sent.html'
        ),
        name='newsletter_activation_email_sent'),

    # Action confirmation views
    re_path(
        '<newsletter_slug>/subscription/<email>/<actions:action>/activate/<activation_code>/',
        UpdateSubscriptionView.as_view(), name='newsletter_update_activate'
    ),
    re_path(
        '<newsletter_slug>/subscription/<email>/<actions:action>/activate/',
        UpdateSubscriptionView.as_view(), name='newsletter_update'
    ),

    # Action activation completed view
    re_path(
        '<newsletter_slug>/<actions:action>/activation-completed/',
        ActionTemplateView.as_view(
            template_name='newsletter/subscription_%(action)s_activated.html'
        ),
        name='newsletter_action_activated'),

    # Archive views
    re_path(
        '<newsletter_slug>/archive/<year>/<month>/<day>/<slug>/',
        SubmissionArchiveDetailView.as_view(), name='newsletter_archive_detail'
    ),
    re_path(
        '<newsletter_slug>/archive/',
        SubmissionArchiveIndexView.as_view(), name='newsletter_archive'
    ),
]
