from django.shortcuts import get_object_or_404, render_to_response

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.core import serializers
from django.contrib.admin.views.decorators import staff_member_required

from django.template import RequestContext

from django.utils.translation import ugettext as _

from mailinglist.models import *

@staff_member_required
def json_subscribers(request, myid):
    message = get_object_or_404(Message, id=myid)

    json = serializers.serialize("json", message.newsletter.get_subscriptions(), fields=())
    return HttpResponse(json, mimetype='application/json')

@staff_member_required
def message_preview(request, myid):
    message = get_object_or_404(Message, id=myid)

    return render_to_response(
        "admin/mailinglist/message/preview.html",
        { 'message' : message },
        RequestContext(request, {}),
    )

@staff_member_required
def message_submit(request, myid):
    message = get_object_or_404(Message, id=myid)
    
    submission = Submission.from_message(message)
    
    return HttpResponseRedirect('../../../submission/%s/' % submission.id)

@staff_member_required
def html_preview(request, myid):
    message = get_object_or_404(Message, id=myid)

    (subject_template, text_template, html_template) = EmailTemplate.get_templates('message', message.newsletter)

    if not html_template:
        # If no HTML available, return an empty bogus HTML page.
        #return HttpResponse('<html><head><title></title></head><body></body></html>')
        raise Http404
        
    c = Context({'message' : message, 
                 'site' : Site.objects.get_current(),
                 'newsletter' : message.newsletter,
                 'date' : datetime.now()})
                 
    return HttpResponse(html_template.render(c))

@staff_member_required
def text_preview(request, myid):
    message = get_object_or_404(Message, id=myid)

    (subject_template, text_template, html_template) = EmailTemplate.get_templates('message', message.newsletter)

    c = Context({'message' : message, 
                 'site' : Site.objects.get_current(),
                 'newsletter' : message.newsletter,
                 'date' : datetime.now()})
                 
    return HttpResponse(text_template.render(c), mimetype='text/plain')

@staff_member_required
def submit(request, myid):
    submission = get_object_or_404(Submission, id=myid)
    
    if submission.sent or submission.prepared:
        request.user.message_set.create(message=_('Submission already sent.'))
        
        return HttpResponseRedirect('../')
        
    submission.prepared=True
    submission.save()
    
    request.user.message_set.create(message=_('Your submission is being sent.'))
    
    return HttpResponseRedirect('../../')

@staff_member_required
def import_subscribers(request):
    pass


