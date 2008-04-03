from django.shortcuts import get_object_or_404, get_list_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
# from django.core.mail import send_mail, EmailMultiAlternatives
# from random import sample
# from newsletter.middleware import threadlocals
# from django.template import Context, loader
# from django.contrib.auth.decorators import login_required
# import datetime
# from BeautifulSoup import BeautifulStoneSoup

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
    
def subscribe(request, newsletter_slug, subscription_id=None):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    
    if subscription_id:
        my_subscription = get_object_or_404(Subscription, newsletter=my_newsletter, email__exact=email)
    else:
        my_subscription = None
    
    if request.POST:
        form = SubscribeForm(request.POST, newsletter=my_newsletter, instance=my_subscription)
        if form.is_valid():
            form.save()
    else:
        form = SubscribeForm(newsletter=my_newsletter, instance=my_subscription)
    
    env = { 'newsletter' : my_newsletter,
            'form' : form }

    return render_to_response("mailinglist/newsletter_subscribe.html", env)
    
def subscribe_activate(request, newsletter_slug, subscription_id, activation_code=None):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    my_subscription = get_object_or_404(Subscription, newsletter=my_newsletter, id=subscription_id)
    
    if activation_code:
        my_initial = {'user_activation_code':activation_code}
    else:
        my_initial = None
    
    if request.POST:
        form = SubscribeActivateForm(request.POST, instance=my_subscription, initial=my_initial)
        if form.is_valid():
            form.save()
    else:
        form = SubscribeActivateForm(instance=my_subscription, initial=my_initial)

    env = { 'newsletter' : my_newsletter,
            'form' : form }
    
    return render_to_response("mailinglist/newsletter_subscribe_activate.html", env)

def unsubscribe(request, newsletter_slug, subscription_id=None):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    
    if subscription_id:
        my_subscription = get_object_or_404(Subscription, newsletter=my_newsletter, email__exact=email)
    else:
        my_subscription = None

    if request.POST:
        form = UnsubscribeForm(request.POST, instance=my_subscription)
        if form.is_valid():
            form.save()
    else:
        form = UnsubscribeForm(instance=my_subscription)

    env = { 'newsletter' : my_newsletter,
            'form' : form }

    return render_to_response("mailinglist/newsletter_unsubscribe.html", env)


def unsubscribe_activate(request, newsletter_slug, subscription_id=None):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)

    if subscription_id:
        my_subscription = get_object_or_404(Subscription, newsletter=my_newsletter, email__exact=email)
    else:
        my_subscription = None

    if request.POST:
        form = UnsubscribeActivateForm(request.POST, instance=my_subscription)
        if form.is_valid():
            form.save()
    else:
        form = UnsubscribeActivateForm(instance=my_subscription)

    env = { 'newsletter' : my_newsletter,
            'form' : form }

    return render_to_response("mailinglist/newsletter_unsubscribe_activate.html", env)


def archive(request, newsletter_slug):
    my_newsletter = get_object_or_404(Newsletter.on_site, slug=newsletter_slug)
    
    publications = Mailing.objects.filter(newsletter = my_newsletter)
    
    return archive_index(request, publications, 'publish_date', extra_context = {'newsletter': my_newsletter})




# def home(request):
#     return render_to_response('mailinglist/home.html', locals())
#
# 
# def send_subscription_confirmation(email, verification):
#     generalsettings = GeneralSettings.objects.all()[0] ## .title .sender .edition .email .domain
#     if verification == None:
#         verification = ''.join(sample("abcdefghijklmnopqrstuvw0123456789", 8))
#     obj = Subscriber.objects.get_or_create(email=email, active=False, defaults={'verification_code': verification})
#     send_mail(
#         'Aanmelden - %s' %generalsettings.title ,
#         'U heeft zich aangemeld bij %s nieuwsbrief.\n\nOm deze aanmelding te bevestigen gaat u naar:\n\n%s/aanmelden/bevestigen/?mail=%s&code=%s'  % (generalsettings.title, generalsettings.domain, email, verification),
#         generalsettings.email, # From
#         [ '%s' %email ], # To
#         fail_silently=False
#         )
# 
# 
# def send_unsubscription_confirmation(email, verification):
#     generalsettings = GeneralSettings.objects.all()[0] ## .title .sender .edition .email .domain
#     send_mail(
#         'Afmelden - %s' %generalsettings.title ,
#         'U heeft zich afgemeld bij %s nieuwsbrief.\n\nOm deze afmelding te bevestigen gaat u naar:\n\n%s/afmelden/bevestigen/?mail=%s&code=%s'  % (generalsettings.title, generalsettings.domain, email, verification),
#         generalsettings.email, # From
#         [ '%s' %email ], # To
#         fail_silently=False
#         )
# 
# 
# def request_subscription(request):
#     if request.method == 'POST':
#         form = SubsriberForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['subscriber_email']
#             try:
#                 obj = Subscriber.objects.get(email=email)
#                 if obj.active == True:
#                     return render_to_response('mailinglist/subscribe.html', {'message': 'Abonnee bestaat al.'})
#                 else:
#                     send_subscription_confirmation(email, obj.verification_code)
#                     return render_to_response('mailinglist/subscribe.html', {'message': 'Abonnee is nog niet geverifieerd. Een nieuwe verificatie-mail is verzonden.'})
#             except Subscriber.DoesNotExist:
#                     send_subscription_confirmation(email, None)
#                     return render_to_response('mailinglist/subscribe.html', {'message': 'Een verificatie-mail is verzonden.'})
#     else:
#         form = SubsriberForm()
#     return render_to_response('mailinglist/subscribe.html', {'form': form})
# 
# 
# def request_unsubscription(request):
#     if request.method == 'POST':
#         form = SubsriberForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['subscriber_email']
#             try:
#                 obj = Subscriber.objects.get(email=email)
#                 send_unsubscription_confirmation(obj.email, obj.verification_code)
#                 return render_to_response('mailinglist/unsubscribe.html', {'message': 'Een verificatie-mail is verzonden.'})
#             except Subscriber.DoesNotExist:
#                 return render_to_response('mailinglist/unsubscribe.html', {'message': 'Abonnee bestaat niet'})
#     else:
#         try:
#             mail = request.GET['mail']
#         except:
#             mail = ""
#         form = SubsriberForm()
#     return render_to_response('mailinglist/unsubscribe.html', locals())
# 
# 
# def subscribe(request):
#     if request.method == 'GET':
#         form = ConfirmForm(request.GET)
#         if form.is_valid():
#             obj = get_object_or_404(Subscriber, email=form.cleaned_data['mail'], verification_code=form.cleaned_data['code'])
#             obj.active = True
#             obj.save()
#             return render_to_response('mailinglist/confirm.html', {'message': "U bent ingeschreven!"})
#     return render_to_response('mailinglist/confirm.html', {'message': "Helaas, verkeerde URL"})
# 
# 
# def unsubscribe(request):
#     if request.method == 'GET':
#         form = ConfirmForm(request.GET)
#         if form.is_valid():
#             mail = form.cleaned_data['mail']
#             verification = form.cleaned_data['code']
#             obj = get_object_or_404(Subscriber, email=mail, verification_code=verification)
#             obj.delete()            
#             return render_to_response('mailinglist/confirm.html', {'message': "U bent nu uitgeschreven!"})
#     return render_to_response('mailinglist/confirm.html', {'message': "Helaas, verkeerde URL"})
# 
# 
# def create_newsletter(id):
#     general = GeneralSettings.objects.all()[0]
#     date = datetime.datetime.now()    
#     newsletter = get_object_or_404(NewsLetter, id=id)
#     c = Context(locals())
#     html = loader.get_template('mailinglist/nieuwsbrief_html.html').render(c)
#     txt = loader.get_template('mailinglist/nieuwsbrief_txt.html').render(c)
#     txt = BeautifulStoneSoup(txt, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]
#     return html, txt
# 
# 
# @login_required(redirect_field_name='/')    
# def preview_newsletter(request, format, id):
#     general = GeneralSettings.objects.all()[0]
#     html, txt = create_newsletter(id)
#     if format == "txt":
#         return HttpResponse("<pre>" + txt + "</pre>")  
#     elif format == "html":
#         return HttpResponse(html)
#     else:
#         return HttpResponseRedirect('/')
# 
# 
# @login_required(redirect_field_name='/')
# def select_newsletter(request):
#     user = threadlocals.get_current_user()
#     if request.method == 'POST':
#         form = NewsLetter_Preview_Form(request.POST)
#         if form.is_valid():
#             newsletter = get_object_or_404(NewsLetter, work_title=unicode(form.cleaned_data['newsletter']))
#             sendform = NewsLetter_Send_Form()
#             return render_to_response('admin/send_newsletter.html', locals())
#     else:
#         form = NewsLetter_Preview_Form()
#     return render_to_response('admin/send_newsletter.html', locals())
# 
# 
# def save_newsletter_in_archive(html, txt):
#     general = GeneralSettings.objects.all()[0]
#     title = "%s - %s" %(general.title, general.edition)
#     NewsLetter_Archive(title=title, publish=True, print_run=len(Subscriber.objects.filter(active=True)), edition=general.edition,  send_date=datetime.datetime.now(), html=html, txt=txt).save()
#     general.edition = general.edition + 1
#     general.save()
# 
# 
# def create_user_html(html, email, domain):
#     return html.replace('<div id="unsubsribe"></div>', '<div id="unsubsribe"><h4>Unsubscribe? <a href="%s/afmelden/?mail=%s">Klick here.</a></div>' % (domain, email))
#     
# def create_user_txt(txt, email, domain):
#     return txt + '\n\nUnsubscribe? Go to:\n%s/afmelden/?mail=%s' % (domain, email)
# 
# @login_required(redirect_field_name='/')
# def send_newsletter(request):
#     generalsettings = GeneralSettings.objects.all()[0] ## .title .sender .edition .email .domain
#     if request.method == 'POST':
#         sendform = NewsLetter_Send_Form(request.POST)
#         if sendform.is_valid():
#             html, txt = create_newsletter(sendform.cleaned_data['newsletter_id'])
#             for i in Subscriber.objects.filter(active=True):
#                 subject, from_email, to = '%s - %s' %(generalsettings.title ,generalsettings.edition), generalsettings.email, i.email
#                 user_html = create_user_html(html, i.email, generalsettings.domain)
#                 user_txt = create_user_txt(txt, i.email, generalsettings.domain)
#                 msg = EmailMultiAlternatives(subject, user_txt, from_email, [to])
#                 msg.attach_alternative(user_html, "text/html")
#                 msg.send()
#                 print i
#             # Save newsletter to archive and delete work concept newsletter
#             save_newsletter_in_archive(html, txt)
#             # NewsLetter.objects.get(id=sendform.cleaned_data['newsletter_id']).delete()
#             return HttpResponseRedirect('/admin/mailinglist/send_newsletter/succes/')
#         else:
#             return HttpResponse('Error, Nieuwsbrief is niet verzonden')
#     else:
#         return HttpResponse('Error, Nieuwsbrief is niet verzonden')
# 
# 
# @login_required(redirect_field_name='/')
# def send_newsletter_succes(request):
#     user = threadlocals.get_current_user()
#     return render_to_response('admin/send_newsletter_succes.html', locals())
#     
#     
# def archive(request):
#     newsletters = NewsLetter_Archive.objects.filter(publish=True).order_by('send_date')
#     return render_to_response('mailinglist/archive.html', locals())
# 
# 
# def archive_detail(request, year, month, day, slug):
#     newsletter = get_object_or_404(NewsLetter_Archive, send_date=datetime.date(int(year),int(month),int(day)), slug=slug, publish=True)
#     return HttpResponse(newsletter.html)
#     
    