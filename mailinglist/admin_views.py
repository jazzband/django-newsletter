from django.shortcuts import get_object_or_404, render_to_response

from django.http import HttpResponse

from django.core import serializers
from django.contrib.admin.views.decorators import staff_member_required

from django.template import RequestContext

from mailinglist.models import *

@staff_member_required
def json_subscribers(request, myid):
    message = get_object_or_404(Message, id=myid)

    json = serializers.serialize("json", message.newsletter.get_subscribers(), fields=())
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
def html_preview(request, myid):
    message = get_object_or_404(Message, id=myid)

    (subject_template, text_template, html_template) = EmailTemplate.get_templates('message', message.newsletter)

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
    
