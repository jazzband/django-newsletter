import logging

logger = logging.getLogger(__name__)

from datetime import datetime

from django.conf import settings
from django.conf.urls.defaults import patterns, url

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.util import force_unicode
from django.contrib.sites.models import Site

from django.core import serializers
from django.core.exceptions import ImproperlyConfigured

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.template import RequestContext, Context

from django.shortcuts import render_to_response

from django.utils.importlib import import_module
from django.utils.translation import ugettext, ugettext_lazy as _

from django.utils.formats import date_format

from .models import (
    EmailTemplate, Newsletter, Subscription, Article, Message, Submission
)

from .admin_forms import *
from .admin_utils import *

""" TODO: Factor settings out into seperate settings module. """

# Import and set the richtext field
NEWSLETTER_RICHTEXT_WIDGET = \
    getattr(settings, "NEWSLETTER_RICHTEXT_WIDGET", "")
RICHTEXT_WIDGET = None
if NEWSLETTER_RICHTEXT_WIDGET:
    module, attr = NEWSLETTER_RICHTEXT_WIDGET.rsplit(".", 1)
    try:
        mod = import_module(module)
        RICHTEXT_WIDGET = getattr(mod, attr)
    except Exception as e:
        # Catch ImportError and other exceptions too
        # (e.g. user sets setting to an integer)
        raise ImproperlyConfigured(
            "Error while importing setting "
            "NEWSLETTER_RICHTEXT_WIDGET %r: %s" % (
                NEWSLETTER_RICHTEXT_WIDGET, e
            )
        )


YES_ICON_URL = '%sadmin/img/icon-yes.gif' % settings.STATIC_URL
WAIT_ICON_URL = '%snewsletter/admin/img/waiting.gif' % settings.STATIC_URL
SUBMIT_ICON_URL = \
    '%snewsletter/admin/img/submitting.gif' % settings.STATIC_URL
NO_ICON_URL = '%sadmin/img/icon-no.gif' % settings.STATIC_URL


class NewsletterAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'admin_subscriptions', 'admin_messages', 'admin_submissions'
    )
    prepopulated_fields = {'slug': ('title',)}

    """ List extensions """
    def admin_messages(self, obj):
        return '<a href="../message/?newsletter__id__exact=%s">%s</a>' % (
            obj.id, ugettext('Messages')
        )
    admin_messages.allow_tags = True
    admin_messages.short_description = ''

    def admin_subscriptions(self, obj):
        return \
            '<a href="../subscription/?newsletter__id__exact=%s">%s</a>' % \
            (obj.id, ugettext('Subscriptions'))
    admin_subscriptions.allow_tags = True
    admin_subscriptions.short_description = ''

    def admin_submissions(self, obj):
        return '<a href="../submission/?newsletter__id__exact=%s">%s</a>' % (
            obj.id, ugettext('Submissions')
        )
    admin_submissions.allow_tags = True
    admin_submissions.short_description = ''


class SubmissionAdmin(admin.ModelAdmin, ExtendibleModelAdminMixin):
    form = SubmissionAdminForm
    list_display = (
        'admin_message', 'admin_newsletter', 'admin_publish_date', 'publish',
        'admin_status_text', 'admin_status'
    )
    date_hierarchy = 'publish_date'
    list_filter = ('newsletter', 'publish', 'sent')
    save_as = True
    filter_horizontal = ('subscriptions',)

    """ List extensions """
    def admin_message(self, obj):
        return '<a href="%d/">%s</a>' % (obj.id, obj.message.title)
    admin_message.short_description = ugettext('submission')
    admin_message.allow_tags = True

    def admin_newsletter(self, obj):
        return '<a href="../newsletter/%s/">%s</a>' % (
            obj.newsletter.id, obj.newsletter
        )
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True

    def admin_publish_date(self, obj):
        if obj.publish_date:
            return date_format(obj.publish_date)
        else:
            return ''
    admin_publish_date.short_description = _("publish date")

    def admin_status(self, obj):
        if obj.prepared:
            if obj.sent:
                return u'<img src="%s" width="10" height="10" alt="%s"/>' % (
                    YES_ICON_URL, self.admin_status_text(obj))
            else:
                if obj.publish_date > datetime.now():
                    return \
                        u'<img src="%s" width="10" height="10" alt="%s"/>' % (
                            WAIT_ICON_URL, self.admin_status_text(obj))
                else:
                    return \
                        u'<img src="%s" width="12" height="12" alt="%s"/>' % (
                            SUBMIT_ICON_URL, self.admin_status_text(obj))
        else:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (
                NO_ICON_URL, self.admin_status_text(obj))

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

    """ Views """
    def submit(self, request, object_id):
        submission = self._getobj(request, object_id)

        if submission.sent or submission.prepared:
            messages.info(request, ugettext("Submission already sent."))
            return HttpResponseRedirect('../')

        submission.prepared = True
        submission.save()

        messages.info(request, ugettext("Your submission is being sent."))

        return HttpResponseRedirect('../../')

    """ URLs """
    def get_urls(self):
        urls = super(SubmissionAdmin, self).get_urls()

        my_urls = patterns('',
            url(r'^(.+)/submit/$',
                self._wrap(self.submit),
                name=self._view_name('submit'))
        )

        return my_urls + urls


class OrderingWidget(forms.Widget):
    def __init__(self):
        super(OrderingWidget, self).__init__()

    def render(self, name, value, attrs=None):
        return unicode('Bananas')
        if self.display_value is not None:
            return unicode(self.display_value)
        return unicode(self.original_value)

    # def value_from_datadict(self, data, files, name):
    #     return self.original_value


StackedInline = admin.StackedInline
if RICHTEXT_WIDGET and RICHTEXT_WIDGET.__name__ == "ImperaviWidget":
    # Imperavi works a little differently
    # It's not just a field, it's also a media class and a method.
    # To avoid complications, we reuse ImperaviStackedInlineAdmin
    try:
        from imperavi.admin import ImperaviStackedInlineAdmin
        StackedInline = ImperaviStackedInlineAdmin
    except ImportError:
        pass


class ArticleInline(StackedInline):
    model = Article
    extra = 2
    fieldsets = (
        (None, {
            'fields': ('title', 'sortorder', 'text')
        }),
        (_('Optional'), {
            'fields': ('url', 'image'),
            'classes': ('collapse',)
        }),
    )

    if RICHTEXT_WIDGET:
        formfield_overrides = {
            models.TextField: {'widget': RICHTEXT_WIDGET},
        }


class MessageAdmin(admin.ModelAdmin, ExtendibleModelAdminMixin):
    save_as = True
    list_display = (
        'admin_title', 'admin_newsletter', 'admin_preview', 'date_create',
        'date_modify'
    )
    list_filter = ('newsletter', )
    date_hierarchy = 'date_create'
    prepopulated_fields = {'slug': ('title',)}

    inlines = [ArticleInline, ]

    """ List extensions """
    def admin_title(self, obj):
        return '<a href="%d/">%s</a>' % (obj.id, obj.title)
    admin_title.short_description = ugettext('message')
    admin_title.allow_tags = True

    def admin_preview(self, obj):
        return '<a href="%d/preview/">%s</a>' % (obj.id, ugettext('Preview'))
    admin_preview.short_description = ''
    admin_preview.allow_tags = True

    def admin_newsletter(self, obj):
        return '<a href="../newsletter/%s/">%s</a>' % (
            obj.newsletter.id, obj.newsletter
        )
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True

    """ Views """
    def preview(self, request, object_id):
        return render_to_response(
            "admin/newsletter/message/preview.html",
            {'message': self._getobj(request, object_id)},
            RequestContext(request, {}),
        )

    def preview_html(self, request, object_id):
        message = self._getobj(request, object_id)

        (subject_template, text_template, html_template) = \
            EmailTemplate.get_templates('message', message.newsletter)

        if not html_template:
            raise Http404(_(
                'No HTML template associated with the newsletter this '
                'message belongs to.'
            ))

        c = Context({'message': message,
                     'site': Site.objects.get_current(),
                     'newsletter': message.newsletter,
                     'date': datetime.now(),
                     'STATIC_URL': settings.STATIC_URL,
                     'MEDIA_URL': settings.MEDIA_URL})

        return HttpResponse(html_template.render(c))

    def preview_text(self, request, object_id):
        message = self._getobj(request, object_id)

        (subject_template, text_template, html_template) = \
            EmailTemplate.get_templates('message', message.newsletter)

        c = Context({
            'message': message,
            'site': Site.objects.get_current(),
            'newsletter': message.newsletter,
            'date': datetime.now(),
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL
            }, autoescape=False
        )

        return HttpResponse(text_template.render(c), mimetype='text/plain')

    def submit(self, request, object_id):
        submission = Submission.from_message(self._getobj(request, object_id))

        return HttpResponseRedirect('../../../submission/%s/' % submission.id)

    def subscribers_json(self, request, object_id):
        message = self._getobj(request, object_id)

        json = serializers.serialize(
            "json", message.newsletter.get_subscriptions(), fields=()
        )
        return HttpResponse(json, mimetype='application/json')

    """ URLs """
    def get_urls(self):
        urls = super(MessageAdmin, self).get_urls()

        my_urls = patterns('',
            url(r'^(.+)/preview/$',
                self._wrap(self.preview),
                name=self._view_name('preview')),
            url(r'^(.+)/preview/html/$',
                self._wrap(self.preview_html),
                name=self._view_name('preview_html')),
            url(r'^(.+)/preview/text/$',
                self._wrap(self.preview_text),
                name=self._view_name('preview_text')),
            url(r'^(.+)/submit/$',
                self._wrap(self.submit),
                name=self._view_name('submit')),
            url(r'^(.+)/subscribers/json/$',
                self._wrap(self.subscribers_json),
                name=self._view_name('subscribers_json')),
        )

        return my_urls + urls


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'action')
    list_display_links = ('title',)
    list_filter = ('action',)
    save_as = True

    form = EmailTemplateAdminForm


class SubscriptionAdmin(admin.ModelAdmin, ExtendibleModelAdminMixin):
    form = SubscriptionAdminForm
    list_display = (
        'name', 'email', 'admin_newsletter', 'admin_subscribe_date',
        'admin_unsubscribe_date', 'admin_status_text', 'admin_status'
    )
    list_display_links = ('name', 'email')
    list_filter = (
        'newsletter', 'subscribed', 'unsubscribed', 'subscribe_date'
    )
    search_fields = (
        'name_field', 'email_field', 'user__first_name', 'user__last_name',
        'user__email'
    )
    date_hierarchy = 'subscribe_date'

    """ List extensions """
    def admin_newsletter(self, obj):
        return '<a href="../newsletter/%s/">%s</a>' % (
            obj.newsletter.id, obj.newsletter
        )
    admin_newsletter.short_description = ugettext('newsletter')
    admin_newsletter.allow_tags = True

    def admin_status(self, obj):
        if obj.unsubscribed:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (
                NO_ICON_URL, self.admin_status_text(obj))

        if obj.subscribed:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (
                YES_ICON_URL, self.admin_status_text(obj))
        else:
            return u'<img src="%s" width="10" height="10" alt="%s"/>' % (
                WAIT_ICON_URL, self.admin_status_text(obj))

    admin_status.short_description = ''
    admin_status.allow_tags = True

    def admin_status_text(self, obj):
        if obj.subscribed:
            return ugettext("Subscribed")
        elif obj.unsubscribed:
            return ugettext("Unsubscribed")
        else:
            return ugettext("Unactivated")
    admin_status_text.short_description = ugettext('Status')

    def admin_subscribe_date(self, obj):
        if obj.subscribe_date:
            return date_format(obj.subscribe_date)
        else:
            return ''
    admin_subscribe_date.short_description = _("subscribe date")

    def admin_unsubscribe_date(self, obj):
        if obj.unsubscribe_date:
            return date_format(obj.unsubscribe_date)
        else:
            return ''
    admin_unsubscribe_date.short_description = _("unsubscribe date")

    """ Views """
    def subscribers_import(self, request):
        if request.POST:
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                request.session['addresses'] = form.get_addresses()
                return HttpResponseRedirect('confirm/')
        else:
            form = ImportForm()

        return render_to_response(
            "admin/newsletter/subscription/importform.html",
            {'form': form},
            RequestContext(request, {}),
        )

    def subscribers_import_confirm(self, request):
        # If no addresses are in the session, start all over.
        if not 'addresses' in request.session:
            return HttpResponseRedirect('../')

        addresses = request.session['addresses']
        logger.debug('Confirming addresses: %s', addresses)
        if request.POST:
            form = ConfirmForm(request.POST)
            if form.is_valid():
                try:
                    for address in addresses.values():
                        address.save()
                finally:
                    del request.session['addresses']

                messages.success(
                    request,
                    _('%s subscriptions have been successfully added.') %
                    len(addresses)
                )

                return HttpResponseRedirect('../../')
        else:
            form = ConfirmForm()

        return render_to_response(
            "admin/newsletter/subscription/confirmimportform.html",
            {'form': form, 'subscribers': addresses},
            RequestContext(request, {}),
        )

    """ URLs """
    def get_urls(self):
        urls = super(SubscriptionAdmin, self).get_urls()

        my_urls = patterns('',
            url(r'^import/$',
                self._wrap(self.subscribers_import),
                name=self._view_name('import')),
            url(r'^import/confirm/$',
                self._wrap(self.subscribers_import_confirm),
                name=self._view_name('import_confirm'))
        )

        return my_urls + urls


admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
