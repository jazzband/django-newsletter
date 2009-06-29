import logging

from datetime import datetime

from django.shortcuts import get_object_or_404, get_list_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.date_based import archive_index

from django.contrib.sites.models import Site

from mailinglist.models import *
from mailinglist.forms import *

def newsletter_list(request):
    newsletters = Newsletter.on_site.filter(visible=True)

    if not newsletters:
        raise Http404

    return object_list(request, newsletters)

def newsletter(request, newsletter_slug):
    newsletters = Newsletter.on_site.filter(visible=True)
    
    if not newsletters:
        raise Http404
        
    return object_detail(request, newsletters, slug=newsletter_slug)

def subscribe_request(request, newsletter_slug):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    
    error = None
    if request.POST:
        form = SubscribeForm(request.POST, newsletter=my_newsletter, ip=request.META.get('REMOTE_ADDR'))
        if form.is_valid():
            try:
                instance = form.save()
                instance.send_activation_email(action='subscribe')

            except Exception, e:
                logging.warn('Error %s while subscribing.' % e)
                error = True
    else:
        form = SubscribeForm(newsletter=my_newsletter)
    
    env = { 'newsletter' : my_newsletter,
            'form' : form,
            'error' : error }

    return render_to_response("mailinglist/subscription_subscribe.html", env)
    
def unsubscribe_request(request, newsletter_slug):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    
    if request.POST:
        form = UnsubscribeForm(request.POST, newsletter=my_newsletter)
        if form.is_valid():
            instance = form.save()
    else:
        form = UnsubscribeForm(newsletter=my_newsletter)

    env = { 'newsletter' : my_newsletter,
            'form' : form }

    return render_to_response("mailinglist/subscription_unsubscribe.html", env)

def activate_subscription(request, newsletter_slug, email, action, activation_code=None):
    if not action in ['subscribe', 'update', 'unsubscribe']:
        raise Http404

    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)

    my_subscription = get_object_or_404(Subscription, newsletter=my_newsletter, email__exact=email)
    
    if activation_code:
        my_initial = {'user_activation_code' : activation_code}
    else:
        my_initial = None
    
    if request.POST:
        form = ActivateForm(request.POST, newsletter=my_newsletter, instance=my_subscription, initial=my_initial)
        if form.is_valid():
            subscription = form.save(commit=False)
            if action == 'subscribe' or action == 'update':
                subscription.activated=True
            else:
                subscription.unsubscribed=True
                subscription.unsubscribe_date = datetime.now()
            
            subscription.save()
    else:
        form = ActivateForm(newsletter=my_newsletter, instance=my_subscription, initial=my_initial)

    env = { 'newsletter' : my_newsletter,
            'form' : form,
            'action' : action}
    
    return render_to_response("mailinglist/subscription_activate.html", env)

""" These should be removed. It is old crappy code. Surely. 1"""
def subscribe_activate(request, newsletter_slug, subscription_id=None):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    
    my_subscription = get_subscription(subscription_id)
    
    logging.debug('subscribe update %s' % my_subscription)
    
    if request.GET.has_key('activation_code'):
        my_initial = {'user_activation_code' : request.GET['activation_code']}
    else:
        my_initial = None
    
    if request.POST:
        form = ActivateForm(request.POST, newsletter=my_newsletter, instance=my_subscription, initial=my_initial)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.activated = True
            instance.unsubscribed = False
            instance.save()
    else:
        form = ActivateForm(newsletter=my_newsletter, instance=my_subscription, initial=my_initial)

    env = { 'newsletter' : my_newsletter,
            'form' : form }
    
    return render_to_response("mailinglist/newsletter_subscribe_activate.html", env)

def unsubscribe_activate(request, newsletter_slug, subscription_id=None):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    
    my_subscription = get_subscription(subscription_id)
    
    logging.debug('subscribe update %s' % my_subscription)
    
    if request.GET.has_key('activation_code'):
        my_initial = {'user_activation_code' : request.GET['activation_code']}
    else:
        my_initial = None
    
    if request.POST:
        form = UnsubscribeActivateForm(request.POST, newsletter=my_newsletter, instance=my_subscription, initial=my_initial)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.unsubscribed = True
            instance.save()
    else:
        form = UnsubscribeActivateForm(newsletter=my_newsletter, instance=my_subscription, initial=my_initial)

    env = { 'newsletter' : my_newsletter,
            'form' : form }
    
    return render_to_response("mailinglist/newsletter_unsubscribe_activate.html", env)

def update_request(request, newsletter_slug, subscription_id=None):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    
    my_subscription = get_subscription(subscription_id)
    logging.debug('unsubscribe request %s' % my_subscription)

    if request.POST:
        form = UpdateForm(request.POST, newsletter=my_newsletter, instance=my_subscription)
        if form.is_valid():
            instance = form.save()
            instance.send_subscription_request()
    else:
        form = UpdateForm(newsletter=my_newsletter, instance=my_subscription)

    env = { 'newsletter' : my_newsletter,
            'form' : form }

    return render_to_response("mailinglist/newsletter_update.html", env)


def archive(request, newsletter_slug):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    
    publications = Mailing.objects.filter(newsletter = my_newsletter)
    
    return archive_index(request, publications, 'publish_date', extra_context = {'newsletter': my_newsletter})
