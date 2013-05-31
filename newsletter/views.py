import logging

logger = logging.getLogger(__name__)

from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.conf import settings

from django.template.response import SimpleTemplateResponse

from django.shortcuts import get_object_or_404
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


class NewsletterMixin(object):
    """ Mixin providing the ability to retrieve a newsletter. """
    newsletter_queryset = None

    def get_newsletter_queryset(self):
        """ Get the queryset to look an newsletter up against. """
        if self.newsletter_queryset is None:
            raise ImproperlyConfigured(
                "%(cls)s is missing a newsletter_queryset. "
                "Define %(cls)s.newsletter_queryset, "
                "or override %(cls)s.get_newsletter_queryset()." % {
                    'cls': self.__class__.__name__
                })
        return self.newsletter_queryset._clone()

    def get_newsletter(self,
            newsletter_slug=None, newsletter_queryset=None, **kwargs):
        """
        Return the newsletter for the current request.

        By default this requires `self.newsletter_queryset`
        and a `newsletter_slug` argument in the URLconf.
        """

        if newsletter_slug is None:
            assert 'newsletter_slug' in self.kwargs
            newsletter_slug = self.kwargs['newsletter_slug']

        if newsletter_queryset is None:
            newsletter_queryset = self.get_newsletter_queryset()

        newsletter = get_object_or_404(
            newsletter_queryset, slug=newsletter_slug,
        )

        return newsletter

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


class ActionUserView(NewsletterMixin, TemplateView):
    """ Base class for subscribe and unsubscribe user views. """
    newsletter_queryset = Newsletter.on_site.all()
    action = None

    def get_context_data(self, **kwargs):
        """ Add action to context. """
        context = super(ActionUserView, self).get_context_data(**kwargs)

        context['action'] = self.action

        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.newsletter = self.get_newsletter(**kwargs)

        # confirm is optional kwarg defaulting to False
        self.confirm = kwargs.get('confirm', False)

        return super(ActionUserView, self).dispatch(*args, **kwargs)


class SubscribeUserView(ActionUserView):
    action = 'subscribe'
    template_name = "newsletter/subscription_subscribe_user.html"

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
                _('User %(rs)s subscribed to %(my_newsletter)s.'), {
                    "rs": request.user,
                    "my_newsletter": self.newsletter
            })

        if already_subscribed:
            messages.info(
                request,
                _('You are already subscribed to %s.') % self.newsletter
            )

        return super(SubscribeUserView, self).get(request, *args, **kwargs)


class UnsubscribeUserView(ActionUserView):
    action = 'unsubscribe'
    template_name = "newsletter/subscription_unsubscribe_user.html"

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
                    _('You have been unsubscribed from %s.') % \
                        self.newsletter
                )

                logger.debug(
                    _('User %(rs)s unsubscribed from %(my_newsletter)s.'), {
                        "rs": request.user,
                        "my_newsletter": self.newsletter
                })

        except Subscription.DoesNotExist:
            not_subscribed = True

        if not_subscribed:
            messages.info(request,
                _('You are not subscribed to %s.') % self.newsletter)

        return super(UnsubscribeUserView, self).get(request, *args, **kwargs)


class ActionRequestView(NewsletterMixin, FormView):
    """ Base class for subscribe, unsubscribe and update request views. """
    newsletter_queryset = Newsletter.on_site.all()
    action = None

    def get_context_data(self, **kwargs):
        """ Add error and action to context. """
        context = super(ActionRequestView, self).get_context_data(**kwargs)

        context.update({
            'error': self.error,
            'action': self.action
        })

        return context

    def get_subscription(self, form):
        """ Return subscription for the current request. """
        return form.instance

    def form_valid(self, form):
        subscription = self.get_subscription(form)

        try:
            subscription.send_activation_email(action=self.action)

        except Exception, e:
            logger.exception('Error %s while submitting email to %s.',
                e, subscription.email)
            self.error = True

        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, *args, **kwargs):
        self.newsletter = self.get_newsletter(**kwargs)
        self.error = None

        return super(ActionRequestView, self).dispatch(*args, **kwargs)


class SubscribeRequestView(ActionRequestView):
    action = 'subscribe'
    form_class = SubscribeRequestForm
    template_name = "newsletter/subscription_subscribe.html"
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
    template_name = "newsletter/subscription_unsubscribe.html"
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
    template_name = "newsletter/subscription_update.html"


class UpdateSubscriptionViev(NewsletterMixin, FormView):
    newsletter_queryset = Newsletter.on_site.all()
    form_class = UpdateForm
    template_name = "newsletter/subscription_activate.html"

    def get_initial(self):
        """ Returns the initial data to use for forms on this view. """
        if self.activation_code:
            return {'user_activation_code': self.activation_code}
        else:
            # TODO: Test coverage of this branch
            return None

    def get_form_kwargs(self):
        """ Add instance to form kwargs. """
        kwargs = super(UpdateSubscriptionViev, self).get_form_kwargs()

        kwargs['instance'] = self.subscription

        return kwargs

    def get_context_data(self, **kwargs):
        """ Add action to context. """
        context = \
            super(UpdateSubscriptionViev, self).get_context_data(**kwargs)

        context['action'] = self.action

        return context

    def form_valid(self, form):
        # Get our instance, but do not save yet
        subscription = form.save(commit=False)

        # If a new subscription or update, make sure it is subscribed
        # Else, unsubscribe
        if self.action == 'subscribe' or self.action == 'update':
            subscription.subscribed = True
        else:
            subscription.unsubscribed = True

        logger.debug(
            _(u'Updated subscription %(subscription)s through the web.'),
            {'subscription': subscription}
        )
        subscription.save()

        return self.render_to_response(self.get_context_data(form=form))

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        # TODO: Figure out what the hell this code is doing here.

        # If we are activating and activation code is valid and not already
        # subscribed, activate straight away

        # if action == 'subscribe' and form.is_valid() and not my_subscription.subscribed:
        #     subscription = form.save(commit=False)
        #     subscription.subscribed = True
        #     subscription.save()
        #
        #     logger.debug(_(u'Activated subscription %(subscription)s through the web.') % {'subscription':subscription})

        return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, *args, **kwargs):
        assert 'action' in kwargs
        assert 'email' in kwargs

        self.action = kwargs['action']
        assert self.action in ['subscribe', 'update', 'unsubscribe']

        self.newsletter = self.get_newsletter(**kwargs)
        self.subscription = get_object_or_404(
            Subscription, newsletter=self.newsletter,
            email_field__exact=kwargs['email']
        )
        # activation_code is optional kwarg which defaults to None
        self.activation_code = kwargs.get('activation_code')

        return super(UpdateSubscriptionViev, self).dispatch(*args, **kwargs)


class SubmissionViewBase(NewsletterMixin):
    """ Base class for submission archive views. """
    date_field = 'publish_date'
    allow_empty = True
    queryset = Submission.objects.filter(publish=True)
    newsletter_queryset = NewsletterViewBase.queryset
    slug_field = 'message__slug'

    # Specify date element notation
    year_format = '%Y'
    month_format = '%m'
    day_format = '%d'

    def get(self, request, *args, **kwargs):
        # Make sure newsletter is available for further processing
        self.newsletter = self.get_newsletter()

        return super(SubmissionViewBase, self).get(request, *args, **kwargs)

    def get_queryset(self):
        """ Filter out submissions for current newsletter. """
        qs = super(SubmissionViewBase, self).get_queryset()

        qs = qs.filter(newsletter=self.newsletter)

        return qs


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
