import logging

logger = logging.getLogger(__name__)

import datetime
import socket

from smtplib import SMTPException

from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.conf import settings

from django.template.response import SimpleTemplateResponse

from django.shortcuts import get_object_or_404, redirect
from django.http import Http404

from django.views.generic import (
    ListView, DetailView,
    ArchiveIndexView, DateDetailView,
    TemplateView, FormView
)

from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils import timezone

from django.forms.models import modelformset_factory

from .models import Newsletter, Subscription, Submission
from .forms import (
    SubscribeRequestForm, UserUpdateForm, UpdateRequestForm,
    UnsubscribeRequestForm, UpdateForm
)
from .settings import newsletter_settings
from .utils import ACTIONS


class NewsletterViewBase(object):
    """ Base class for newsletter views. """
    queryset = Newsletter.on_site.filter(visible=True)
    allow_empty = False
    slug_url_kwarg = 'newsletter_slug'


class NewsletterDetailView(NewsletterViewBase, DetailView):
    pass


class NewsletterListView(NewsletterViewBase, ListView):
    """
    List available newsletters and generate a formset for (un)subscription
    for authenticated users.
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
        """
        Return a formset with newsletters for logged in users, or None.
        """

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

                messages.info(
                    request,
                    ugettext("Your changes have been saved.")
                )

            except ValidationError:
                # Invalid form posted. As there is no way for a user to
                # enter data - invalid forms should be ignored from the UI.

                # However, we log them for debugging purposes.
                logger.warning(
                    'Invalid form post received',
                    exc_info=True, extra={'request': request}
                )

                # Present a pristine form
                formset = SubscriptionFormSet(queryset=qs)

        else:
            formset = SubscriptionFormSet(queryset=qs)

        return formset


class ProcessUrlDataMixin(object):
    """
    Mixin providing the ability to process args and kwargs from url
    before dispatching request.
    """

    def process_url_data(self, *args, **kwargs):
        """ Subclasses should put url data processing in this method. """
        pass

    def dispatch(self, *args, **kwargs):
        self.process_url_data(*args, **kwargs)

        return super(ProcessUrlDataMixin, self).dispatch(*args, **kwargs)


class NewsletterMixin(ProcessUrlDataMixin):
    """
    Mixin retrieving newsletter based on newsletter_slug from url
    and adding it to context and form kwargs.
    """

    def process_url_data(self, *args, **kwargs):
        """
        Get newsletter based on `newsletter_slug` from url
        and add it to instance attributes.
        """

        assert 'newsletter_slug' in kwargs

        super(NewsletterMixin, self).process_url_data(*args, **kwargs)

        newsletter_queryset = kwargs.get(
            'newsletter_queryset',
            Newsletter.on_site.all()
        )
        newsletter_slug = kwargs['newsletter_slug']

        self.newsletter = get_object_or_404(
            newsletter_queryset, slug=newsletter_slug,
        )

    def get_form_kwargs(self):
        """ Add newsletter to form kwargs. """
        kwargs = super(NewsletterMixin, self).get_form_kwargs()

        kwargs['newsletter'] = self.newsletter

        return kwargs

    def get_context_data(self, **kwargs):
        """ Add newsletter to context. """
        context = super(NewsletterMixin, self).get_context_data(**kwargs)

        context['newsletter'] = self.newsletter

        return context


class ActionMixin(ProcessUrlDataMixin):
    """ Mixin retrieving action from url and adding it to context. """

    action = None

    def process_url_data(self, *args, **kwargs):
        """ Add action from url to instance attributes if not already set. """
        super(ActionMixin, self).process_url_data(*args, **kwargs)

        if self.action is None:
            assert 'action' in kwargs
            self.action = kwargs['action']

        assert self.action in ACTIONS, 'Unknown action: %s' % self.action

    def get_context_data(self, **kwargs):
        """ Add action to context. """
        context = super(ActionMixin, self).get_context_data(**kwargs)

        context['action'] = self.action

        return context

    def get_template_names(self):
        """ Return list of template names for proper action. """

        if self.template_name is None:
            raise ImproperlyConfigured(
                '%(class_name)s should define template_name, '
                'or implement get_template_names()' % {
                    'class_name': self.__class__.__name__
                }
            )

        else:
            try:
                return [self.template_name % {'action': self.action}]
            except KeyError, e:
                raise ImproperlyConfigured(
                    '%(class_name)s inherits from ActionMixin and can contain '
                    '%%(action)s in template_name to be replaced '
                    'by action name %(wrong_key)s given instead.' % {
                        'class_name': self.__class__.__name__,
                        'wrong_key': e,
                    }
                )


class ActionTemplateView(NewsletterMixin, ActionMixin, TemplateView):
    """
    View that renders a template for proper action,
    with newsletter and action in context.
    """
    pass


class ActionFormView(NewsletterMixin, ActionMixin, FormView):
    """ FormView with newsletter and action support. """

    def get_url_from_viewname(self, viewname):
        """
        Return url for given `viename`
        and associated with this view newsletter and action.
        """

        return reverse(
            viewname,
            kwargs={
                'newsletter_slug': self.newsletter.slug,
                'action': self.action
            }
        )


class ActionUserView(ActionTemplateView):
    """ Base class for subscribe and unsubscribe user views. """
    template_name = "newsletter/subscription_%(action)s_user.html"

    def process_url_data(self, *args, **kwargs):
        """ Add confirm to instance attributes. """
        super(ActionUserView, self).process_url_data(*args, **kwargs)

        # confirm is optional kwarg defaulting to False
        self.confirm = kwargs.get('confirm', False)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ActionUserView, self).dispatch(*args, **kwargs)


class SubscribeUserView(ActionUserView):
    action = 'subscribe'

    def get(self, request, *args, **kwargs):
        already_subscribed = False
        instance = Subscription.objects.get_or_create(
            newsletter=self.newsletter, user=request.user
        )[0]

        if instance.subscribed:
            already_subscribed = True
        elif self.confirm:
            instance.subscribed = True
            instance.save()

            messages.success(
                request,
                _('You have been subscribed to %s.') % self.newsletter
            )

            logger.debug(
                _('User %(rs)s subscribed to %(my_newsletter)s.'),
                {
                    "rs": request.user,
                    "my_newsletter": self.newsletter
                }
            )

        if already_subscribed:
            messages.info(
                request,
                _('You are already subscribed to %s.') % self.newsletter
            )

        return super(SubscribeUserView, self).get(request, *args, **kwargs)


class UnsubscribeUserView(ActionUserView):
    action = 'unsubscribe'

    def get(self, request, *args, **kwargs):
        not_subscribed = False

        try:
            instance = Subscription.objects.get(
                newsletter=self.newsletter, user=request.user
            )

            if not instance.subscribed:
                not_subscribed = True
            elif self.confirm:
                instance.subscribed = False
                instance.save()

                messages.success(
                    request,
                    _('You have been unsubscribed from %s.') % self.newsletter
                )

                logger.debug(
                    _('User %(rs)s unsubscribed from %(my_newsletter)s.'),
                    {
                        "rs": request.user,
                        "my_newsletter": self.newsletter
                    }
                )

        except Subscription.DoesNotExist:
            not_subscribed = True

        if not_subscribed:
            messages.info(
                request,
                _('You are not subscribed to %s.') % self.newsletter
            )

        return super(UnsubscribeUserView, self).get(request, *args, **kwargs)


class ActionRequestView(ActionFormView):
    """ Base class for subscribe, unsubscribe and update request views. """
    template_name = "newsletter/subscription_%(action)s.html"

    def process_url_data(self, *args, **kwargs):
        """ Add error to instance attributes. """
        super(ActionRequestView, self).process_url_data(*args, **kwargs)

        self.error = None

    def get_context_data(self, **kwargs):
        """ Add error to context. """
        context = super(ActionRequestView, self).get_context_data(**kwargs)

        context.update({
            'error': self.error,
        })

        return context

    def get_subscription(self, form):
        """ Return subscription for the current request. """
        return form.instance

    def no_email_confirm(self, form):
        """
        Subscribe/unsubscribe user and redirect to action activated page.
        """
        self.subscription.update(self.action)

        return redirect(
            self.get_url_from_viewname('newsletter_action_activated')
        )

    def get_success_url(self):
        return self.get_url_from_viewname('newsletter_activation_email_sent')

    def form_valid(self, form):
        self.subscription = self.get_subscription(form)

        if not getattr(
                newsletter_settings,
                'CONFIRM_EMAIL_%s' % self.action.upper()
        ):
            # Confirmation email for this action was switched off in settings.
            return self.no_email_confirm(form)

        try:
            self.subscription.send_activation_email(action=self.action)

        except (SMTPException, socket.error), e:
            logger.exception(
                'Error %s while submitting email to %s.',
                e, self.subscription.email
            )
            self.error = True

            # Although form was valid there was error while sending email,
            # so stay at the same url.
            return super(ActionRequestView, self).form_invalid(form)

        return super(ActionRequestView, self).form_valid(form)


class SubscribeRequestView(ActionRequestView):
    action = 'subscribe'
    form_class = SubscribeRequestForm
    confirm = False

    def get_form_kwargs(self):
        """ Add ip to form kwargs for submitted forms. """
        kwargs = super(SubscribeRequestView, self).get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            kwargs['ip'] = self.request.META.get('REMOTE_ADDR')

        return kwargs

    def get_subscription(self, form):
        return form.save()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            kwargs['confirm'] = self.confirm
            return SubscribeUserView.as_view()(request, *args, **kwargs)

        return super(SubscribeRequestView, self).dispatch(
            request, *args, **kwargs
        )


class UnsubscribeRequestView(ActionRequestView):
    action = 'unsubscribe'
    form_class = UnsubscribeRequestForm
    confirm = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            kwargs['confirm'] = self.confirm
            return UnsubscribeUserView.as_view()(request, *args, **kwargs)

        return super(UnsubscribeRequestView, self).dispatch(
            request, *args, **kwargs
        )


class UpdateRequestView(ActionRequestView):
    action = 'update'
    form_class = UpdateRequestForm

    def no_email_confirm(self, form):
        """ Redirect to update subscription view. """
        return redirect(self.subscription.update_activate_url())


class UpdateSubscriptionView(ActionFormView):
    form_class = UpdateForm
    template_name = "newsletter/subscription_activate.html"

    def process_url_data(self, *args, **kwargs):
        """
        Add email, subscription and activation_code
        to instance attributes.
        """
        assert 'email' in kwargs

        super(UpdateSubscriptionView, self).process_url_data(*args, **kwargs)

        self.subscription = get_object_or_404(
            Subscription, newsletter=self.newsletter,
            email_field__exact=kwargs['email']
        )
        # activation_code is optional kwarg which defaults to None
        self.activation_code = kwargs.get('activation_code')

    def get_initial(self):
        """ Returns the initial data to use for forms on this view. """
        if self.activation_code:
            return {'user_activation_code': self.activation_code}
        else:
            # TODO: Test coverage of this branch
            return None

    def get_form_kwargs(self):
        """ Add instance to form kwargs. """
        kwargs = super(UpdateSubscriptionView, self).get_form_kwargs()

        kwargs['instance'] = self.subscription

        return kwargs

    def get_success_url(self):
        return self.get_url_from_viewname('newsletter_action_activated')

    def form_valid(self, form):
        """ Get our instance, but do not save yet. """
        subscription = form.save(commit=False)

        subscription.update(self.action)

        return super(UpdateSubscriptionView, self).form_valid(form)


class SubmissionViewBase(NewsletterMixin):
    """ Base class for submission archive views. """
    date_field = 'publish_date'
    allow_empty = True
    queryset = Submission.objects.filter(publish=True)
    slug_field = 'message__slug'

    # Specify date element notation
    year_format = '%Y'
    month_format = '%m'
    day_format = '%d'

    def process_url_data(self, *args, **kwargs):
        """ Use only visible newsletters. """

        kwargs['newsletter_queryset'] = NewsletterListView().get_queryset()
        return super(
            SubmissionViewBase, self).process_url_data(*args, **kwargs)

    def get_queryset(self):
        """ Filter out submissions for current newsletter. """
        qs = super(SubmissionViewBase, self).get_queryset()

        qs = qs.filter(newsletter=self.newsletter)

        return qs

    def _make_date_lookup_arg(self, value):
        """
        Convert a date into a datetime when the date field is a DateTimeField.

        When time zone support is enabled, `date` is assumed to be in the
        default time zone, so that displayed items are consistent with the URL.

        Related discussion:
        https://github.com/dokterbob/django-newsletter/issues/74
        """
        value = datetime.datetime.combine(value, datetime.time.min)
        if settings.USE_TZ:
            value = timezone.make_aware(value, timezone.get_default_timezone())
        return value


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
            raise Http404(ugettext(
                'No HTML template associated with the newsletter this '
                'message belongs to.'
            ))

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
