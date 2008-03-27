from django.contrib.admin.views.main import *
from django.utils.translation import ugettext as _
from MySQLdb import IntegrityError

def alter_fields(obj):
    try:
        obj.publish = False
    except AttributeError: 
        pass
    try:
        obj.slug = "%s_" %obj.slug
    except AttributeError: 
        pass
    try:
        obj.title = "%s_" %obj.title
    except AttributeError: 
        pass
    try:
        obj.name = "%s_" %obj.name
    except AttributeError: 
        pass
    return obj

def duplicate(obj):
    obj.id = None
    alter_fields(obj)
    saved = False
    while saved == False:
        try: 
            obj.save()
            saved = True
        except IntegrityError: 
            alter_fields(obj)
    return obj

def delete(request, app_label, model_name):
    model = models.get_model(app_label, model_name)
    opts = model._meta  
    if model is None:
        raise Http404("App %r, model %r, not found" % (app_label, model_name))
    if not request.user.has_perm(app_label + '.' + model._meta.get_change_permission()):
        raise PermissionDenied  
    try:
        cl = ChangeList(request, model)
    except IncorrectLookupParameters:
        if ERROR_FLAG in request.GET.keys():
            return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
        return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')


    if 'delete_selected' in request.POST and model_name in request.POST:
        deleted = []
        for obj in cl.get_query_set().filter(id__in=request.POST.getlist(model_name)):
            obj.delete()
            deleted.append('"%s"' % str(obj))
        request.user.message_set.create(message=_('The %(name)s %(obj)s were deleted successfully.') % {'name': opts.verbose_name_plural, 'obj': ", ".join(deleted)})

    if 'duplicate_selected' in request.POST and model_name in request.POST:
        duplicated = []
        for obj in cl.get_query_set().filter(id__in=request.POST.getlist(model_name)):
            duplicate(obj)
            duplicated.append('"%s"' % str(obj))
        request.user.message_set.create(message=_('The %(name)s %(obj)s were created successfully.') % {'name': opts.verbose_name_plural, 'obj': ", ".join(duplicated)})

#     if 'delete' in request.GET and model_name in request.GET:
#         obj = cl.get_query_set().filter(id__in=request.GET.getlist(model_name))[0]
#         #obj.delete()
#         request.user.message_set.create(message=_('The %(name)s %(obj)s were deleted successfully.') % {'name': opts.verbose_name_plural, 'obj':  obj })

    if 'duplicate_one' in request.POST and model_name in request.POST:
        #obj = cl.get_query_set().filter(id__in=request.GET.getlist(model_name))[0]
        for obj in cl.get_query_set().filter(id__in=request.POST.getlist(model_name)):
            duplicate(obj)
        request.user.message_set.create(message=_('The %(name)s %(obj)s were created successfully.') % {'name': opts.verbose_name_plural, 'obj': obj })
                    
    return HttpResponseRedirect('..')
change_list = staff_member_required(never_cache(change_list))