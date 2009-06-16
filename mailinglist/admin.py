from mailinglist.models import EmailTemplate, Newsletter, Subscription, Article, Message, Submission
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class Article_Inline(admin.TabularInline):
    model = Article
    extra = 2

class NewsletterOptions(admin.ModelAdmin):
    list_display = ('title', 'admin_subscriptions', 'admin_messages', 'admin_submissions')
    prepopulated_fields = {'slug': ('title',)}

class SubmissionOptions(admin.ModelAdmin):
    list_display = ('admin_newsletter', 'message', 'publish_date', 'publish', 'admin_status_text', 'admin_status')
    list_display_links = ['message',]
    date_hierarchy = 'publish_date'
    list_filter = ('newsletter', 'publish', 'sent')
    save_as = True
    filter_horizontal = ('subscriptions',)

class MessageOptions(admin.ModelAdmin):
    js = ('/static/admin/tiny_mce/tiny_mce.js','/static/admin/tiny_mce/textareas.js')
    save_as = True
    list_display = ('admin_newsletter', 'title', 'admin_preview', 'date_create', 'date_modify')
    list_display_links  = ('title',)
    list_filter = ('newsletter', )
    date_hierarchy = 'date_create'

class EmailTemplateOptions(admin.ModelAdmin):
    list_display = ('title','action')
    list_display_links = ('title',)
    list_filter = ('action',)
    save_as = True

class SubscriptionOptions(admin.ModelAdmin):
    list_display = ('name', 'email', 'admin_newsletter', 'subscribe_date', 'admin_unsubscribe_date', 'admin_status_text', 'admin_status')
    list_display_links = ('name', 'email')
    list_filter = ('newsletter','activated', 'unsubscribed','subscribe_date')
    search_fieldsets = ('name', 'email')
    date_hierarchy = 'subscribe_date'

admin.site.register(Newsletter, NewsletterOptions)
admin.site.register(Submission, SubmissionOptions)
admin.site.register(Message, MessageOptions)
admin.site.register(EmailTemplate, EmailTemplateOptions)
admin.site.register(Subscription, SubscriptionOptions)

