from mailinglist.models import EmailTemplate, Newsletter, Subscription, Article, Message, Submission
from django.contrib import admin

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.db.models import permalink

from django.forms.util import ValidationError

from django.conf import settings

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
    def text_preview_url(self, obj):
        return ('mailinglist.admin_views.text_preview', (obj.id, ), {})
        
    @permalink
    def html_preview_url(self, obj):
        return ('mailinglist.admin_views.html_preview', (obj.id, ), {})
    
    def admin_preview(self, obj):
        return '<a href="%s/preview/">%s</a>' % (obj.id, ugettext('Preview'))
    admin_preview.short_description = ''
    admin_preview.allow_tags = True
    
    def admin_newsletter(self, obj):
        return '<a href="../newsletter/%s/">%s</a>' % (obj.newsletter.id, obj.newsletter)
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True


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

