import logging

logger = logging.getLogger(__name__)

from django.core.exceptions import ValidationError
from django.conf import settings

from django.template import RequestContext
from django.template.response import SimpleTemplateResponse

from django.shortcuts import get_object_or_404, render_to_response
from django.http import Http404

from django.views.generic import (
    ListView, DetailView,
    ArchiveIndexView, DateDetailView
)

from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required

from django.utils.translation import ugettext, ugettext_lazy as _

from django.forms.models import modelformset_factory

from .models import Newsletter, Subscription, Submission
from .forms import (
    SubscribeRequestForm, UserUpdateForm, UpdateRequestForm,
    UnsubscribeRequestForm, UpdateForm
)


class NewsletterViewBase(object):
    """ Base class for newsletter views. """
    queryset = Newsletter.on_site.filter(visible=True)
    allow_empty = False

    def get_object(self, queryset=None):
        # This is a workaround for Django 1.3 and should be replaced by
        # the `slug_url_kwarg = 'newsletter_slug'` view attribute as soon
        # as 1.3 support is dropped.
        self.kwargs['slug'] = self.kwargs['newsletter_slug']

        return super(NewsletterViewBase, self).get_object(queryset)


class NewsletterDetailView(NewsletterViewBase, DetailView):
    pass


class NewsletterListView(NewsletterViewBase, ListView):
    """
    List available newsletters and generate a formset for (un)subscription for
    authenticated users.
    """

    def post(self, request, **kwargs):
        """ Allow post requests. """

        # All logic (for now) occurs in the form logic
        return super(NewsletterListView, self).get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NewsletterListView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            # Add a formset for logged in users.
            context['formset'] = self.get_formset()

        return context

    def get_formset(self):
        """ Return a formset with newsletters for logged in users, or None. """

        # Short-hand variable names
        newsletters = self.get_queryset()
        request = self.request
        user = request.user

        SubscriptionFormSet = modelformset_factory(
            Subscription, form=UserUpdateForm, extra=0
        )

        # Before rendering the formset, subscription objects should
        # already exist.
        for n in newsletters:
            Subscription.objects.get_or_create(
                newsletter=n, user=user
            )

        # Get all subscriptions for use in the formset
        qs = Subscription.objects.filter(
            newsletter__in=newsletters, user=user
        )

        if request.method == 'POST':
            try:
                formset = SubscriptionFormSet(request.POST, queryset=qs)

                if not formset.is_valid():
                    raise ValidationError('Update form invalid.')

                # Everything's allright, let's save
                formset.save()

                messages.info(request,
                    ugettext("Your changes have been saved."))

            except ValidationError:
                # Invalid form posted. As there is no way for a user to
                # enter data - invalid forms should be ignored from the UI.

                # However, we log them for debugging purposes.
                logger.warning('Invalid form post received',
                    exc_info=True, extra={'request': request})

                # Present a pristine form
                formset = SubscriptionFormSet(queryset=qs)

        else:
            formset = SubscriptionFormSet(queryset=qs)

        return formset


@login_required
def subscribe_user(request, newsletter_slug, confirm=False):
    my_newsletter = get_object_or_404(
        Newsletter.on_site, slug=newsletter_slug
    )

    already_subscribed = False
    instance = Subscription.objects.get_or_create(
        newsletter=my_newsletter, user=request.user
    )[0]

    if instance.subscribed:
        already_subscribed = True
    elif confirm:
        instance.subscribed = True
        instance.save()

        messages.success(
            request, _('You have been subscribed to %s.') % my_newsletter)

        logger.debug(
            _('User %(rs)s subscribed to %(my_newsletter)s.'), {
                "rs": request.user,
                "my_newsletter": my_newsletter
        })

    if already_subscribed:
        messages.info(
            request, _('You are already subscribed to %s.') % my_newsletter)

    env = {
        'newsletter': my_newsletter,
        'action': 'subscribe'
    }

    return render_to_response(
        "newsletter/subscription_subscribe_user.html",
        env, context_instance=RequestContext(request))


@login_required
def unsubscribe_user(request, newsletter_slug, confirm=False):
    my_newsletter = get_object_or_404(
        Newsletter.on_site, slug=newsletter_slug
    )

    not_subscribed = False

    try:
        instance = Subscription.objects.get(
            newsletter=my_newsletter, user=request.user
        )

        if not instance.subscribed:
            not_subscribed = True
        elif confirm:
            instance.subscribed = False
            instance.save()

            messages.success(
                request,
                _('You have been unsubscribed from %s.') % my_newsletter
            )

            logger.debug(
                _('User %(rs)s unsubscribed from %(my_newsletter)s.'), {
                    "rs": request.user,
                    "my_newsletter": my_newsletter
            })

    except Subscription.DoesNotExist:
        not_subscribed = True

    if not_subscribed:
        messages.info(request,
            _('You are not subscribed to %s.') % my_newsletter)

    env = {
        'newsletter': my_newsletter,
        'action': 'unsubscribe'
    }

    return render_to_response(
        "newsletter/subscription_unsubscribe_user.html",
        env, context_instance=RequestContext(request))


def subscribe_request(request, newsletter_slug, confirm=False):
    if request.user.is_authenticated():
        return subscribe_user(request, newsletter_slug, confirm)

    my_newsletter = get_object_or_404(
        Newsletter.on_site, slug=newsletter_slug)

    error = None
    if request.POST:
        form = SubscribeRequestForm(
            request.POST,
            newsletter=my_newsletter,
            ip=request.META.get('REMOTE_ADDR')
        )

        if form.is_valid():
            instance = form.save()

            try:
                instance.send_activation_email(action='subscribe')

            except Exception, e:
                logger.exception('Error %s while submitting email to %s.',
                    e, instance.email)
                error = True

    else:
        form = SubscribeRequestForm(newsletter=my_newsletter)

    env = {
        'newsletter': my_newsletter,
        'form': form,
        'error': error,
        'action': 'subscribe'
    }

    return render_to_response(
        "newsletter/subscription_subscribe.html",
        env, context_instance=RequestContext(request))


def unsubscribe_request(request, newsletter_slug, confirm=False):
    if request.user.is_authenticated():
        return unsubscribe_user(request, newsletter_slug, confirm)

    my_newsletter = get_object_or_404(
        Newsletter.on_site, slug=newsletter_slug)

    error = None
    if request.POST:
        form = UnsubscribeRequestForm(request.POST, newsletter=my_newsletter)

        if form.is_valid():
            instance = form.instance

            try:
                instance.send_activation_email(action='unsubscribe')

            except Exception, e:
                logger.exception(
                    'Error %s while submitting email to %s.',
                    e, instance.email)
                error = True
    else:
        form = UnsubscribeRequestForm(newsletter=my_newsletter)

    env = {
        'newsletter': my_newsletter,
        'form': form,
        'error': error,
        'action': 'unsubscribe'
    }

    return render_to_response(
        "newsletter/subscription_unsubscribe.html",
        env, context_instance=RequestContext(request))


def update_request(request, newsletter_slug):
    my_newsletter = get_object_or_404(
        Newsletter.on_site, slug=newsletter_slug)

    error = None
    if request.POST:
        form = UpdateRequestForm(request.POST, newsletter=my_newsletter)
        if form.is_valid():
            instance = form.instance
            try:
                instance.send_activation_email(action='update')

            except Exception, e:
                logger.exception(
                    'Error %s while submitting email to %s.',
                    e, instance.email)
                error = True
    else:
        form = UpdateRequestForm(newsletter=my_newsletter)

    env = {
        'newsletter': my_newsletter,
        'form': form,
        'error': error,
        'action': 'update'
    }

    return render_to_response(
        "newsletter/subscription_update.html",
        env, context_instance=RequestContext(request))


def update_subscription(request, newsletter_slug,
        email, action, activation_code=None):

    assert action in ['subscribe', 'update', 'unsubscribe']

    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    my_subscription = get_object_or_404(
        Subscription, newsletter=my_newsletter, email_field__exact=email
    )

    if activation_code:
        my_initial = {'user_activation_code': activation_code}
    else:
        # TODO: Test coverage of this branch
        my_initial = None

    if request.POST:
        form = UpdateForm(
            request.POST, newsletter=my_newsletter, instance=my_subscription,
            initial=my_initial
        )
        if form.is_valid():
            # Get our instance, but do not save yet
            subscription = form.save(commit=False)

            # If a new subscription or update, make sure it is subscribed
            # Else, unsubscribe
            if action == 'subscribe' or action == 'update':
                subscription.subscribed = True
            else:
                subscription.unsubscribed = True

            logger.debug(
                _(u'Updated subscription %(subscription)s through the web.'),
                {'subscription': subscription}
            )
            subscription.save()
    else:
        form = UpdateForm(
            newsletter=my_newsletter, instance=my_subscription,
            initial=my_initial
        )

        # TODO: Figure out what the hell this code is doing here.

        # If we are activating and activation code is valid and not already
        # subscribed, activate straight away

        # if action == 'subscribe' and form.is_valid() and not my_subscription.subscribed:
        #     subscription = form.save(commit=False)
        #     subscription.subscribed = True
        #     subscription.save()
        #
        #     logger.debug(_(u'Activated subscription %(subscription)s through the web.') % {'subscription':subscription})

    env = {
        'newsletter': my_newsletter,
        'form': form,
        'action': action
    }

    return render_to_response(
        "newsletter/subscription_activate.html", env,
        context_instance=RequestContext(request)
    )


class SubmissionViewBase(object):
    """ Base class for submission archive views. """
    date_field = 'publish_date'
    allow_empty = True
    queryset = Submission.objects.filter(publish=True)
    slug_field = 'message__slug'

    # Specify date element notation
    year_format = '%Y'
    month_format = '%m'
    day_format = '%d'

    def get(self, request, *args, **kwargs):
        # Make sure newsletter is available for further processing
        self.newsletter = self.get_newsletter(request, **kwargs)

        return super(SubmissionViewBase, self).get(request, *args, **kwargs)

    def get_newsletter(self, request, **kwargs):
        """ Return the newsletter for the current request. """
        assert 'newsletter_slug' in kwargs

        newsletter_slug = self.kwargs['newsletter_slug']

        # Directly use the queryset from the Newsletter view
        newsletter = get_object_or_404(
            NewsletterViewBase.queryset, slug=newsletter_slug,
        )

        return newsletter

    def get_queryset(self):
        """ Filter out submissions for current newsletter. """
        qs = super(SubmissionViewBase, self).get_queryset()

        qs = qs.filter(newsletter=self.newsletter)

        return qs

    def get_context_data(self, **kwargs):
        """ Add newsletter to context. """
        context = super(SubmissionViewBase, self).get_context_data(**kwargs)

        context['newsletter'] = self.newsletter

        return context


class SubmissionArchiveIndexView(SubmissionViewBase, ArchiveIndexView):
    pass


class SubmissionArchiveDetailView(SubmissionViewBase, DateDetailView):
    def get_context_data(self, **kwargs):
        """
        Make sure the actual message is available.
        """
        context = \
            super(SubmissionArchiveDetailView, self).get_context_data(**kwargs)

        message = self.object.message

        context.update({
            'message': message,
            'site': Site.objects.get_current(),
            'date': self.object.publish_date,
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL
        })

        return context

    def get_template(self):
        """ Get the message template for the current newsletter. """

        (subject_template, text_template, html_template) = \
            self.object.newsletter.get_templates('message')

        # No HTML -> no party!
        if not html_template:
            raise Http404(ugettext('No HTML template associated with the '
                                   'newsletter this message belongs to.'))

        return html_template

    def render_to_response(self, context, **response_kwargs):
        """
        Return a simplified response; the template should be rendered without
        any context. Use a SimpleTemplateResponse as a RequestContext should
        not be used.
        """
        return SimpleTemplateResponse(
            template=self.get_template(),
            context=context,
            **response_kwargs
        )
