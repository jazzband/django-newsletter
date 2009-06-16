from datetime import datetime

from django.conf import settings
from django.conf.urls.defaults import patterns, url

from django.contrib import admin
from django.contrib.admin.util import unquote, force_unicode
from django.contrib.sites.models import Site

from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from django.db.models import permalink

from django.forms.util import ValidationError

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.template import RequestContext, Context

from django.shortcuts import render_to_response

from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.functional import update_wrapper

from mailinglist.models import EmailTemplate, Newsletter, Subscription, Article, Message, Submission

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'admin_subscriptions', 'admin_messages', 'admin_submissions')
    prepopulated_fields = {'slug': ('title',)}
    
    def admin_messages(self, obj):
        return '<a href="../message/?newsletter__id__exact=%s">%s</a>' % (obj.id, ugettext('Messages'))
    admin_messages.allow_tags = True
    admin_messages.short_description = ''

    def admin_subscriptions(self, obj):
        return '<a href="../subscription/?newsletter__id__exact=%s">%s</a>' % (obj.id, ugettext('Subscriptions'))
    admin_subscriptions.allow_tags = True
    admin_subscriptions.short_description = ''

    def admin_submissions(self, obj):
        return '<a href="../submission/?newsletter__id__exact=%s">%s</a>' % (obj.id, ugettext('Submissions'))
    admin_submissions.allow_tags = True
    admin_submissions.short_description = ''

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('admin_newsletter', 'message', 'publish_date', 'publish', 'admin_status_text', 'admin_status')
    list_display_links = ['message',]
    date_hierarchy = 'publish_date'
    list_filter = ('newsletter', 'publish', 'sent')
    save_as = True
    filter_horizontal = ('subscriptions',)
    
    def admin_newsletter(self, obj):
        return '<a href="../newsletter/%s/">%s</a>' % (obj.newsletter.id, obj.newsletter)
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True
    
    def admin_status(self, obj):
        if obj.prepared:
            if obj.sent:
                return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-yes.gif', obj.admin_status_text())
            else:
                if obj.publish_date > datetime.now():
                    return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.MEDIA_URL+'newsletter/admin/img/waiting.gif', obj.admin_status_text())
                else:
                    return u'<img src="%s" width="12" height="12" alt="%s"/>' % (settings.MEDIA_URL+'newsletter/admin/img/submitting.gif', obj.admin_status_text())
        else:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-no.gif', obj.admin_status_text())
        
    admin_status.short_description = ''
    admin_status.allow_tags = True
    
    def admin_status_text(self, obj):
        if obj.prepared:
            if obj.sent:
                return ugettext("Sent.")
            else:
                if obj.publish_date > datetime.now():
                    return ugettext("Delayed submission.")
                else:
                    return ugettext("Submitting.")
        else:
            return ugettext("Not sent.")
    admin_status_text.short_description = ugettext('Status')

class ArticleInline(admin.TabularInline):
    model = Article
    extra = 2

class MessageAdmin(admin.ModelAdmin):
    js = ('/static/admin/tiny_mce/tiny_mce.js','/static/admin/tiny_mce/textareas.js')
    save_as = True
    list_display = ('admin_newsletter', 'title', 'admin_preview', 'date_create', 'date_modify')
    list_display_links  = ('title',)
    list_filter = ('newsletter', )
    date_hierarchy = 'date_create'
    
    inlines = [ArticleInline,]
    
    @permalink
    def preview_url(self, obj):
        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name
        
        return ('%sadmin_%s_%s_preview' % info, (obj.id, ), {})
    
    @permalink
    def preview_text_url(self, obj):
        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name
        
        return ('%sadmin_%s_%s_preview_text' % info, (obj.id, ), {})
        
    @permalink
    def preview_html_url(self, obj):
        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name
        
        return ('%sadmin_%s_%s_preview_html' % info, (obj.id, ), {})
    
    def admin_preview(self, obj):
        return '<a href="%s">%s</a>' % (self.preview_url(obj), ugettext('Preview'))
    admin_preview.short_description = ''
    admin_preview.allow_tags = True
    
    def admin_newsletter(self, obj):
        return '<a href="../newsletter/%s/">%s</a>' % (obj.newsletter.id, obj.newsletter)
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True
    
    def _getobj(self, request, object_id):
        opts = self.model._meta
        app_label = opts.app_label
    
        try:
            obj = self.queryset(request).get(pk=unquote(object_id))
        except self.model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None
    
        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        return obj
    
    def preview(self, request, object_id):
        return render_to_response(
            "admin/mailinglist/message/preview.html",
            { 'message' : self._getobj(request, object_id) },
            RequestContext(request, {}),
        )
        
    def preview_html(self, request, object_id):
        message = self._getobj(request, object_id)
        (subject_template, text_template, html_template) = EmailTemplate.get_templates('message', message.newsletter)

        if not html_template:
            raise Http404(_('No HTML template associated with the newsletter this message belongs to.'))
        
        c = Context({'message' : message, 
                     'site' : Site.objects.get_current(),
                     'newsletter' : message.newsletter,
                     'date' : datetime.now()})
        
        return HttpResponse(html_template.render(c))

    def preview_text(self, request, object_id):
        message = self._getobj(request, object_id)
        (subject_template, text_template, html_template) = EmailTemplate.get_templates('message', message.newsletter)

        c = Context({'message' : message, 
                     'site' : Site.objects.get_current(),
                     'newsletter' : message.newsletter,
                     'date' : datetime.now()})
         
        return HttpResponse(text_template.render(c), mimetype='text/plain')

    def submit(self, request, object_id):
        submission = Submission.from_message(self._getobj(request, object_id))
        
        return HttpResponseRedirect('../../../submission/%s/' % submission.id)
    
    def get_urls(self):
        urls = super(MessageAdmin, self).get_urls()
    
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
    
        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name
        
        my_urls = patterns('',
            url(r'^(.+)/preview/$', 
                wrap(self.preview), 
                name='%sadmin_%s_%s_preview' % info),
            url(r'^(.+)/preview/html/$', 
                wrap(self.preview_html), 
                name='%sadmin_%s_%s_preview_html' % info),
            url(r'^(.+)/preview/text/$', 
                wrap(self.preview_text), 
                name='%sadmin_%s_%s_preview_text' % info),
            url(r'^(.+)/submit/$', 
                wrap(self.submit), 
                name='%sadmin_%s_%s_submit' % info),

            )

        return my_urls + urls


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('title','action')
    list_display_links = ('title',)
    list_filter = ('action',)
    save_as = True
    
    def TemplateValidator(self, field):
        try:
            Template(self.cleaned_data[field])
        except Exception, e:
            raise ValidationError(_('There was an error parsing your template: %s') % e)
    
    def clean_subject(self):
        return TemplateValidator('subject')
    
    def clean_text(self):
        return TemplateValidator('text')
    
    def clean_html(self):
        return TemplateValidator('html')

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'admin_newsletter', 'subscribe_date', 'admin_unsubscribe_date', 'admin_status_text', 'admin_status')
    list_display_links = ('name', 'email')
    list_filter = ('newsletter','activated', 'unsubscribed','subscribe_date')
    search_fieldsets = ('name', 'email')
    date_hierarchy = 'subscribe_date'
    
    def admin_newsletter(self, obj):
        return '<a href="../newsletter/%s/">%s</a>' % (obj.newsletter.id, obj.newsletter)
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True       

    def admin_status(self, obj):
        if obj.unsubscribed:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-no.gif', obj.admin_status_text())
        
        if obj.activated:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-yes.gif', obj.admin_status_text())
        else:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.MEDIA_URL+'newsletter/admin/img/waiting.gif', obj.admin_status_text())
        
    admin_status.short_description = ''
    admin_status.allow_tags = True

    def admin_status_text(self, obj):
        if obj.unsubscribed:
            return ugettext("Unsubscribed")
        
        if obj.activated:
            return ugettext("Activated")
        else:
            return ugettext("Unactivated")
    admin_status_text.short_description = ugettext('Status')   
    
    def admin_unsubscribe_date(self, obj):
        if obj.unsubscribe_date:
            return obj.unsubscribe_date
        else:
            return ''
    admin_unsubscribe_date.short_description = _("unsubscribe date")

admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(Subscription, SubscriptionAdmin)

