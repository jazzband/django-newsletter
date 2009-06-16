from mailinglist.models import EmailTemplate, Newsletter, Subscription, Article, Message, Submission
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from django.forms.util import ValidationError

class Article_Inline(admin.TabularInline):
    model = Article
    extra = 2

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'admin_subscriptions', 'admin_messages', 'admin_submissions')
    prepopulated_fields = {'slug': ('title',)}
    
    def admin_messages(self):
        return '<a href="../message/?newsletter__id__exact=%s">%s</a>' % (self.id, ugettext('Messages'))
    admin_messages.allow_tags = True
    admin_messages.short_description = ''

    def admin_subscriptions(self):
        return '<a href="../subscription/?newsletter__id__exact=%s">%s</a>' % (self.id, ugettext('Subscriptions'))
    admin_subscriptions.allow_tags = True
    admin_subscriptions.short_description = ''

    def admin_submissions(self):
        return '<a href="../submission/?newsletter__id__exact=%s">%s</a>' % (self.id, ugettext('Submissions'))
    admin_submissions.allow_tags = True
    admin_submissions.short_description = ''

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('admin_newsletter', 'message', 'publish_date', 'publish', 'admin_status_text', 'admin_status')
    list_display_links = ['message',]
    date_hierarchy = 'publish_date'
    list_filter = ('newsletter', 'publish', 'sent')
    save_as = True
    filter_horizontal = ('subscriptions',)
    
    def admin_newsletter(self):
        return '<a href="../newsletter/%s/">%s</a>' % (self.newsletter.id, self.newsletter)
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True
    
    def admin_status(self):
        if self.prepared:
            if self.sent:
                return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-yes.gif', self.admin_status_text())
            else:
                if self.publish_date > datetime.now():
                    return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.MEDIA_URL+'newsletter/admin/img/waiting.gif', self.admin_status_text())
                else:
                    return u'<img src="%s" width="12" height="12" alt="%s"/>' % (settings.MEDIA_URL+'newsletter/admin/img/submitting.gif', self.admin_status_text())
        else:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-no.gif', self.admin_status_text())
        
    admin_status.short_description = ''
    admin_status.allow_tags = True
    
    def admin_status_text(self):
        if self.prepared:
            if self.sent:
                return ugettext("Sent.")
            else:
                if self.publish_date > datetime.now():
                    return ugettext("Delayed submission.")
                else:
                    return ugettext("Submitting.")
        else:
            return ugettext("Not sent.")
    admin_status_text.short_description = ugettext('Status')

class MessageAdmin(admin.ModelAdmin):
    js = ('/static/admin/tiny_mce/tiny_mce.js','/static/admin/tiny_mce/textareas.js')
    save_as = True
    list_display = ('admin_newsletter', 'title', 'admin_preview', 'date_create', 'date_modify')
    list_display_links  = ('title',)
    list_filter = ('newsletter', )
    date_hierarchy = 'date_create'
    
    @permalink
    def text_preview_url(self):
        return ('mailinglist.admin_views.text_preview', (self.id, ), {})
        
    @permalink
    def html_preview_url(self):
        return ('mailinglist.admin_views.html_preview', (self.id, ), {})
    
    def admin_preview(self):
        return '<a href="%s/preview/">%s</a>' % (self.id, ugettext('Preview'))
    admin_preview.short_description = ''
    admin_preview.allow_tags = True
    
    def admin_newsletter(self):
        return '<a href="../newsletter/%s/">%s</a>' % (self.newsletter.id, self.newsletter)
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
    
    def admin_newsletter(self):
        return '<a href="../newsletter/%s/">%s</a>' % (self.newsletter.id, self.newsletter)
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True       

    def admin_status(self):
        if self.unsubscribed:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-no.gif', self.admin_status_text())
        
        if self.activated:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.ADMIN_MEDIA_PREFIX+'img/admin/icon-yes.gif', self.admin_status_text())
        else:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (settings.MEDIA_URL+'newsletter/admin/img/waiting.gif', self.admin_status_text())
        
    admin_status.short_description = ''
    admin_status.allow_tags = True

    def admin_status_text(self):
        if self.unsubscribed:
            return ugettext("Unsubscribed")
        
        if self.activated:
            return ugettext("Activated")
        else:
            return ugettext("Unactivated")
    admin_status_text.short_description = ugettext('Status')   
    
    def admin_unsubscribe_date(self):
        if self.unsubscribe_date:
            return self.unsubscribe_date
        else:
            return ''
    admin_unsubscribe_date.short_description = unsubscribe_date.verbose_name

admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(Subscription, SubscriptionAdmin)

