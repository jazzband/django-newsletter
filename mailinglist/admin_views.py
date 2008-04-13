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
    
    return HttpResponse(message.render_html())

@staff_member_required
def text_preview(request, myid):
    message = get_object_or_404(Message, id=myid)
    
    return HttpResponse(message.render_text(), mimetype='text/plain')
    
