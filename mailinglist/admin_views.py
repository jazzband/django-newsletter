from django.shortcuts import get_object_or_404, render_to_response

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.core import serializers
from django.contrib.admin.views.decorators import staff_member_required

from django.template import RequestContext

from django.utils.translation import ugettext as _

from mailinglist.models import *

# @staff_member_required
# def json_subscribers(request, myid):
#     message = get_object_or_404(Message, id=myid)
# 
#     json = serializers.serialize("json", message.newsletter.get_subscriptions(), fields=())
#     return HttpResponse(json, mimetype='application/json')
# 
# @staff_member_required
# def submit(request, myid):
#     submission = get_object_or_404(Submission, id=myid)
#     
#     if submission.sent or submission.prepared:
#         request.user.message_set.create(message=_('Submission already sent.'))
#         
#         return HttpResponseRedirect('../')
#         
#     submission.prepared=True
#     submission.save()
#     
#     request.user.message_set.create(message=_('Your submission is being sent.'))
#     
#     return HttpResponseRedirect('../../')

from admin_forms import *

@staff_member_required
def import_subscribers(request):
    if request.POST:
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            request.session['addresses'] = form.get_addresses()
            return HttpResponseRedirect('confirm/')
    else:
        form = ImportForm()

    return render_to_response(
        "admin/mailinglist/subscription/importform.html",
        { 'form' : form },
        RequestContext(request, {}),
    )

@staff_member_required
def confirm_import_subscribers(request):
    # If no addresses are in the session, start all over.
    if not request.session.has_key('addresses'):
        return HttpResponseRedirect('../')
        
    addresses = request.session['addresses']
    print 'confirming addresses', addresses 
    if request.POST:
        form = ConfirmForm(request.POST)
        if form.is_valid():
            try:
                for address in addresses.values():
                    address.save()
            finally:
                del request.session['addresses']
            request.user.message_set.create(message=_('%s subscriptions have been succesfully added.') % len(addresses)) 
            
            return HttpResponseRedirect('../../')
    else:
        form = ConfirmForm()
         
    return render_to_response(
        "admin/mailinglist/subscription/confirmimportform.html",
        { 'form' : form ,
          'subscribers': addresses },
        RequestContext(request, {}),
    )