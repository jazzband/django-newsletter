from django.urls import path, register_converter

from .converters import NewsletterActionsConverter
from .views import (
    NewsletterListView, NewsletterDetailView,
    SubmissionArchiveIndexView, SubmissionArchiveDetailView,
    SubscribeRequestView, UnsubscribeRequestView, UpdateRequestView,
    ActionTemplateView, UpdateSubscriptionView,
)

register_converter(NewsletterActionsConverter, 'actions')

app_name = 'newsletter'
urlpatterns = [
    # Newsletter list and detail view
    path('', NewsletterListView.as_view(), name='list'),
    path(
        '<newsletter_slug>/',
        NewsletterDetailView.as_view(), name='detail'
    ),

    # Action request views
    path(
        '<newsletter_slug>/subscribe/',
        SubscribeRequestView.as_view(),
        name='subscribe_request'
    ),
    path(
        '<newsletter_slug>/subscribe/confirm/',
        SubscribeRequestView.as_view(confirm=True),
        name='subscribe_confirm'
    ),
    path(
        '<newsletter_slug>/update/',
        UpdateRequestView.as_view(),
        name='update_request'
    ),
    path(
        '<newsletter_slug>/unsubscribe/',
        UnsubscribeRequestView.as_view(),
        name='unsubscribe_request'
    ),
    path(
        '<newsletter_slug>/unsubscribe/confirm/',
        UnsubscribeRequestView.as_view(confirm=True),
        name='unsubscribe_confirm'
    ),

    # Activation email sent view
    path(
        '<newsletter_slug>/<actions:action>/email-sent/',
        ActionTemplateView.as_view(
            template_name='newsletter/subscription_%(action)s_email_sent.html'
        ),
        name='activation_email_sent'),

    # Action confirmation views
    path(
        '<newsletter_slug>/subscription/<email>/<actions:action>/activate/<activation_code>/',
        UpdateSubscriptionView.as_view(), name='update_activate'
    ),
    path(
        '<newsletter_slug>/subscription/<email>/<actions:action>/activate/',
        UpdateSubscriptionView.as_view(), name='update'
    ),

    # Action activation completed view
    path(
        '<newsletter_slug>/<actions:action>/activation-completed/',
        ActionTemplateView.as_view(
            template_name='newsletter/subscription_%(action)s_activated.html'
        ),
        name='action_activated'),

    # Archive views
    path(
        '<newsletter_slug>/archive/<year>/<month>/<day>/<slug>/',
        SubmissionArchiveDetailView.as_view(), name='archive_detail'
    ),
    path(
        '<newsletter_slug>/archive/',
        SubmissionArchiveIndexView.as_view(), name='archive'
    ),
]
