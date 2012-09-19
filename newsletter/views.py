import logging

logger = logging.getLogger(__name__)

from django.conf import settings

from django.template import RequestContext

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, Http404

from django.views.generic import list_detail, date_based

from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required

from django.utils.translation import ugettext, ugettext_lazy as _

from newsletter.models import *
from newsletter.forms import *

from django.forms.models import modelformset_factory


def newsletter_list(request):
    newsletters = Newsletter.on_site.filter(visible=True)

    if not newsletters:
        raise Http404

    if request.user.is_authenticated():
        SubscriptionFormSet = modelformset_factory(
            Subscription, form=UserUpdateForm, extra=0)

        for n in newsletters:
            Subscription.objects.get_or_create(
                newsletter=n, user=request.user)

        qs = Subscription.objects.filter(
            newsletter__in=newsletters, user=request.user)

        if request.method == 'POST':
            formset = SubscriptionFormSet(request.POST, queryset=qs)
            if formset.is_valid():
                formset.save()
                messages.info(request,
                    ugettext("Your changes have been saved."))
            else:
                assert False, 'An invalid user update request was recieved.'
        else:
            formset = SubscriptionFormSet(queryset=qs)

    else:
        formset = None

    return list_detail.object_list(
        request, newsletters, extra_context={'formset': formset})

def newsletter_detail(request, newsletter_slug):
    newsletters = Newsletter.on_site.filter(visible=True)

    if not newsletters:
        raise Http404

    return list_detail.object_detail(
        request, newsletters, slug=newsletter_slug)

@login_required
def subscribe_user(request, newsletter_slug, confirm=False):
    my_newsletter = get_object_or_404(
        Newsletter.on_site, slug=newsletter_slug)

    already_subscribed = False
    instance = Subscription.objects.get_or_create(
        newsletter=my_newsletter, user=request.user)[0]

    if instance.subscribed:
        already_subscribed = True
    elif confirm:
        instance.subscribed = True
        instance.save()

        messages.success(
            request, _('You have been subscribed to %s.') % my_newsletter)
        logger.debug(_('User %(rs)s subscribed to %(my_newsletter)s.'),
            {"rs":request.user, "my_newsletter": my_newsletter})

    if already_subscribed:
        messages.info(
            request, _('You are already subscribed to %s.') % my_newsletter)

    env = { 'newsletter'            : my_newsletter,
            'action'                : 'subscribe',}

    return render_to_response(
        "newsletter/subscription_subscribe_user.html",
        env, context_instance=RequestContext(request))


@login_required
def unsubscribe_user(request, newsletter_slug, confirm=False):
    my_newsletter = get_object_or_404(
        Newsletter.on_site, slug=newsletter_slug)

    not_subscribed = False

    try:
        instance = Subscription.objects.get(
            newsletter=my_newsletter, user=request.user)
        if not instance.subscribed:
            not_subscribed = True
        elif confirm:
            instance.subscribed=False
            instance.save()

            messages.success(request,
                _('You have been unsubscribed from %s.') % my_newsletter)
            logger.debug(
                _('User %(rs)s unsubscribed from %(my_newsletter)s.'),
                {"rs":request.user, "my_newsletter":my_newsletter })

    except Subscription.DoesNotExist:
        not_subscribed = True

    if not_subscribed:
        messages.info(request,
            _('You are not subscribed to %s.') % my_newsletter)

    env = { 'newsletter'     : my_newsletter,
            'action'         : 'unsubscribe' }

    return render_to_response(
        "newsletter/subscription_unsubscribe_user.html",
        env, context_instance=RequestContext(request))

def subscribe_request(request, newsletter_slug, confirm=False):
    if request.user.is_authenticated() or confirm:
        return subscribe_user(request, newsletter_slug, confirm)

    my_newsletter = get_object_or_404(
        Newsletter.on_site, slug=newsletter_slug)

    error = None
    if request.POST:
        form = SubscribeRequestForm(
            request.POST, newsletter=my_newsletter,
            ip=request.META.get('REMOTE_ADDR'))

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

    env = {'newsletter': my_newsletter,
           'form': form,
           'error': error,
           'action':'subscribe'}

    return render_to_response(
        "newsletter/subscription_subscribe.html",
        env, context_instance=RequestContext(request))

def unsubscribe_request(request, newsletter_slug, confirm=False):
    if request.user.is_authenticated() or confirm:
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

    env = { 'newsletter' : my_newsletter,
            'form' : form,
            'error' : error,
            'action' :'unsubscribe' }

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

    env = {'newsletter': my_newsletter,
           'form': form,
           'error': error,
           'action':'update' }

    return render_to_response(
        "newsletter/subscription_update.html",
        env, context_instance=RequestContext(request))


def update_subscription(request, newsletter_slug, email, action, activation_code=None):
    if not action in ['subscribe', 'update', 'unsubscribe']:
        raise Http404

    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    my_subscription = get_object_or_404(Subscription, newsletter=my_newsletter, email_field__exact=email)

    if activation_code:
        my_initial = {'user_activation_code' : activation_code}
    else:
        my_initial = None

    if request.POST:
        form = UpdateForm(request.POST, newsletter=my_newsletter, instance=my_subscription, initial=my_initial)
        if form.is_valid():
            # Get our instance, but do not save yet
            subscription = form.save(commit=False)

            # If a new subscription or update, make sure it is subscribed
            # Else, unsubscribe
            if action == 'subscribe' or action == 'update':
                subscription.subscribed=True
            else:
                subscription.unsubscribed=True

            logger.debug(_(u'Updated subscription %(subscription)s through the web.'), {'subscription':subscription})
            subscription.save()
    else:
        form = UpdateForm(newsletter=my_newsletter, instance=my_subscription, initial=my_initial)

        # If we are activating and activation code is valid and not already subscribed, activate straight away
        # if action == 'subscribe' and form.is_valid() and not my_subscription.subscribed:
        #     subscription = form.save(commit=False)
        #     subscription.subscribed = True
        #     subscription.save()
        #
        #     logger.debug(_(u'Activated subscription %(subscription)s through the web.') % {'subscription':subscription})
        # from ipdb import set_trace; set_trace()

    env = { 'newsletter' : my_newsletter,
            'form' : form,
            'action' : action }

    return render_to_response("newsletter/subscription_activate.html", env, context_instance=RequestContext(request))

def archive(request, newsletter_slug):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug, visible=True)

    submissions = Submission.objects.filter(newsletter=my_newsletter, publish=True)

    return date_based.archive_index(request,
                                    queryset=submissions,
                                    date_field='publish_date',
                                    extra_context = {'newsletter': my_newsletter})

def archive_detail(request, newsletter_slug, year, month, day, slug):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug, visible=True)

    submission = get_object_or_404(Submission, newsletter=my_newsletter,
                                               publish=True,
                                               publish_date__year=year,
                                               publish_date__month=month,
                                               publish_date__day=day,
                                               message__slug=slug)

    message = submission.message
    (subject_template, text_template, html_template) = EmailTemplate.get_templates('message', message.newsletter)

    if not html_template:
        raise Http404(ugettext('No HTML template associated with the newsletter this message belongs to.'))

    c = Context({'message' : message,
                 'site' : Site.objects.get_current(),
                 'newsletter' : message.newsletter,
                 'date' : submission.publish_date,
                 'STATIC_URL': settings.STATIC_URL,
                 'MEDIA_URL': settings.MEDIA_URL})

    return HttpResponse(html_template.render(c))

