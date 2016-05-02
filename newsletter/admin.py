import logging

import six

from django.db import models

from django.conf import settings
from django.conf.urls import url

from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.sites.models import Site

from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render

from django.template import Context
from django.template.response import SimpleTemplateResponse

from django.utils.formats import date_format
from django.utils.html import format_html
from django.utils.timezone import now
from django.utils.translation import ugettext as _, ungettext

from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.i18n import javascript_catalog

from sorl.thumbnail.admin import AdminImageMixin

from .models import (
    Newsletter, Subscription, Article, Message, Submission
)

from .admin_forms import (
    SubmissionAdminForm, SubscriptionAdminForm, ImportForm, ConfirmForm,
    ArticleFormSet
)
from .admin_utils import ExtendibleModelAdminMixin, make_subscription

from .settings import newsletter_settings


logger = logging.getLogger(__name__)


# Contsruct URL's for icons
def icon_url(icon, alt_text, _urls={}):
    if not _urls:
        _urls['yes'] = static('newsletter/admin/img/icon-yes.gif')
        _urls['wait'] = static('newsletter/admin/img/waiting.gif')
        _urls['submit'] = static('newsletter/admin/img/submitting.gif')
        _urls['no'] = static('newsletter/admin/img/icon-no.gif')

    return format_html(
        '<img src="{}" width="10" height="10" alt="{}"/>',
        _urls[icon], alt_text
    )


class NewsletterAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'admin_subscriptions', 'admin_messages', 'admin_submissions'
    )
    prepopulated_fields = {'slug': ('title',)}

    """ List extensions """
    def _admin_url(self, obj, model, text):
        url = reverse('admin:%s_%s_changelist' %
                      (model._meta.app_label, model._meta.model_name),
                      current_app=self.admin_site.name)

        return format_html(
            '<a href="{}?newsletter__id={}">{}</a>', url, obj.id, text
        )

    def admin_messages(self, obj):
        return self._admin_url(obj, Message, _("Messages"))
    admin_messages.short_description = ''

    def admin_subscriptions(self, obj):
        return self._admin_url(obj, Subscription, _("Subscriptions"))
    admin_subscriptions.short_description = ''

    def admin_submissions(self, obj):
        return self._admin_url(obj, Submission, _("Submissions"))
    admin_submissions.short_description = ''


class NewsletterAdminLinkMixin(object):
    def admin_newsletter(self, obj):
        opts = Newsletter._meta
        newsletter = obj.newsletter
        url = reverse('admin:%s_%s_change' % (opts.app_label, opts.model_name),
                      args=(newsletter.id,), current_app=self.admin_site.name)

        return format_html('<a href="{}">{}</a>', url, newsletter)
    admin_newsletter.short_description = _('newsletter')


class SubmissionAdmin(admin.ModelAdmin, ExtendibleModelAdminMixin,
                      NewsletterAdminLinkMixin):
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
    def _admin_url(self, model, obj_id, text):
        url = reverse('admin:%s_%s_change' %
                      (model._meta.app_label, model._meta.model_name),
                      args=(obj_id,), current_app=self.admin_site.name)

        return format_html('<a href="{}">{}</a>', url, text)

    def admin_message(self, obj):
        return self._admin_url(Submission, obj.id, obj.message.title)
    admin_message.short_description = _('submission')

    def admin_publish_date(self, obj):
        if obj.publish_date:
            return date_format(obj.publish_date, 'DATETIME_FORMAT')
        else:
            return ''
    admin_publish_date.short_description = _("publish date")

    def admin_status(self, obj):
        if obj.prepared:
            if obj.sent:
                icon = 'yes'
            elif obj.publish_date > now():
                icon = 'wait'
            else:
                icon = 'submit'
        else:
            icon = 'no'

        return icon_url(icon, self.admin_status_text(obj))
    admin_status.short_description = ''

    def admin_status_text(self, obj):
        if obj.prepared:
            if obj.sent:
                return _("Sent.")
            elif obj.publish_date > now():
                return _("Delayed submission.")
            else:
                return _("Submitting.")
        else:
            return _("Not sent.")
    admin_status_text.short_description = _('Status')

    """ Views """
    def submit(self, request, object_id):
        submission = self._getobj(request, object_id)

        if submission.sent or submission.prepared:
            messages.info(request, _("Submission already sent."))
            change_url = reverse(
                'admin:newsletter_submission_change', args=[object_id]
            )
            return HttpResponseRedirect(change_url)

        submission.prepared = True
        submission.save()

        messages.info(request, _("Your submission is being sent."))

        changelist_url = reverse('admin:newsletter_submission_changelist')
        return HttpResponseRedirect(changelist_url)

    """ URLs """
    def get_urls(self):
        urls = super(SubmissionAdmin, self).get_urls()

        my_urls = [
            url(
                r'^(.+)/submit/$',
                self._wrap(self.submit),
                name=self._view_name('submit')
            )
        ]

        return my_urls + urls


StackedInline = admin.StackedInline
if (
        newsletter_settings.RICHTEXT_WIDGET
        and newsletter_settings.RICHTEXT_WIDGET.__name__ == "ImperaviWidget"
):
    # Imperavi works a little differently
    # It's not just a field, it's also a media class and a method.
    # To avoid complications, we reuse ImperaviStackedInlineAdmin
    try:
        from imperavi.admin import ImperaviStackedInlineAdmin
        StackedInline = ImperaviStackedInlineAdmin
    except ImportError:
        # Log a warning when import fails as to aid debugging.
        logger.warning(
            'Error importing ImperaviStackedInlineAdmin. '
            'Imperavi WYSIWYG text editor might not work.'
        )


class ArticleInline(AdminImageMixin, StackedInline):
    model = Article
    extra = 2
    formset = ArticleFormSet
    fieldsets = (
        (None, {
            'fields': ('title', 'text')
        }),
        (_('Optional'), {
            'fields': ('sortorder', 'url', 'image'),
            'classes': ('collapse',)
        }),
    )

    if newsletter_settings.RICHTEXT_WIDGET:
        formfield_overrides = {
            models.TextField: {'widget': newsletter_settings.RICHTEXT_WIDGET},
        }


class MessageAdmin(admin.ModelAdmin, ExtendibleModelAdminMixin,
                   NewsletterAdminLinkMixin):
    save_as = True
    list_display = (
        'title', 'admin_newsletter', 'admin_preview', 'date_create',
        'date_modify'
    )
    list_display_links = ('title',)
    list_filter = ('newsletter', )
    date_hierarchy = 'date_create'
    prepopulated_fields = {'slug': ('title',)}

    inlines = [ArticleInline, ]

    """ List extensions """
    def admin_preview(self, obj):
        url = reverse('admin:' + self._view_name('preview'), args=(obj.id,),
                      current_app=self.admin_site.name)

        return format_html('<a href="{}">{}</a>', url, _("Preview"))
    admin_preview.short_description = ''

    """ Views """
    def preview(self, request, object_id):
        return render(
            request,
            "admin/newsletter/message/preview.html",
            {'message': self._getobj(request, object_id)},
        )

    @xframe_options_sameorigin
    def preview_html(self, request, object_id):
        message = self._getobj(request, object_id)

        if not message.html_template:
            raise Http404(_(
                'No HTML template associated with the newsletter this '
                'message belongs to.'
            ))

        c = {'message': message,
             'site': Site.objects.get_current(),
             'newsletter': message.newsletter,
             'date': now(),
             'STATIC_URL': settings.STATIC_URL,
             'MEDIA_URL': settings.MEDIA_URL}

        return SimpleTemplateResponse(message.html_template, context=c)

    @xframe_options_sameorigin
    def preview_text(self, request, object_id):
        message = self._getobj(request, object_id)

        c = Context({
            'message': message,
            'site': Site.objects.get_current(),
            'newsletter': message.newsletter,
            'date': now(),
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL
        }, autoescape=False)

        return SimpleTemplateResponse(
            message.text_template, context=c, content_type='text/plain'
        )

    def submit(self, request, object_id):
        submission = Submission.from_message(self._getobj(request, object_id))

        change_url = reverse(
            'admin:newsletter_submission_change', args=[submission.id])

        return HttpResponseRedirect(change_url)

    def subscribers_json(self, request, object_id):
        message = self._getobj(request, object_id)

        json = serializers.serialize(
            "json", message.newsletter.get_subscriptions(), fields=()
        )
        return HttpResponse(json, content_type='application/json')

    """ URLs """
    def get_urls(self):
        urls = super(MessageAdmin, self).get_urls()

        my_urls = [
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
        ]

        return my_urls + urls


class SubscriptionAdmin(admin.ModelAdmin, ExtendibleModelAdminMixin,
                        NewsletterAdminLinkMixin):
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
    readonly_fields = (
        'ip', 'subscribe_date', 'unsubscribe_date', 'activation_code'
    )
    date_hierarchy = 'subscribe_date'
    actions = ['make_subscribed', 'make_unsubscribed']
    exclude = ['unsubscribed']

    """ List extensions """
    def admin_status(self, obj):
        if obj.unsubscribed:
            icon = 'no'
        elif obj.subscribed:
            icon = 'yes'
        else:
            icon = 'wait'

        return icon_url(icon, self.admin_status_text(obj))
    admin_status.short_description = ''

    def admin_status_text(self, obj):
        if obj.subscribed:
            return _("Subscribed")
        elif obj.unsubscribed:
            return _("Unsubscribed")
        else:
            return _("Unactivated")
    admin_status_text.short_description = _('Status')

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

    """ Actions """
    def make_subscribed(self, request, queryset):
        rows_updated = queryset.update(subscribed=True)
        self.message_user(
            request,
            ungettext(
                "%d user has been successfully subscribed.",
                "%d users have been successfully subscribed.",
                rows_updated
            ) % rows_updated
        )
    make_subscribed.short_description = _("Subscribe selected users")

    def make_unsubscribed(self, request, queryset):
        rows_updated = queryset.update(subscribed=False)
        self.message_user(
            request,
            ungettext(
                "%d user has been successfully unsubscribed.",
                "%d users have been successfully unsubscribed.",
                rows_updated
            ) % rows_updated
        )
    make_unsubscribed.short_description = _("Unsubscribe selected users")

    """ Views """
    def subscribers_import(self, request):
        if not request.user.has_perm('newsletter.add_subscription'):
            raise PermissionDenied()
        if request.POST:
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                request.session['addresses'] = form.get_addresses()
                request.session['newsletter_pk'] = \
                    form.cleaned_data['newsletter'].pk

                confirm_url = reverse(
                    'admin:newsletter_subscription_import_confirm'
                )
                return HttpResponseRedirect(confirm_url)
        else:
            form = ImportForm()

        return render(
            request,
            "admin/newsletter/subscription/importform.html",
            {'form': form},
        )

    def subscribers_import_confirm(self, request):
        # If no addresses are in the session, start all over.

        if 'addresses' not in request.session:
            import_url = reverse('admin:newsletter_subscription_import')
            return HttpResponseRedirect(import_url)

        addresses = request.session['addresses']
        newsletter = Newsletter.objects.get(
            pk=request.session['newsletter_pk']
        )

        logger.debug('Confirming addresses: %s', addresses)

        if request.POST:
            form = ConfirmForm(request.POST)
            if form.is_valid():
                try:
                    for email, name in six.iteritems(addresses):
                        address_inst = make_subscription(
                            newsletter, email, name
                        )
                        address_inst.save()
                finally:
                    del request.session['addresses']
                    del request.session['newsletter_pk']

                messages.success(
                    request,
                    ungettext(
                        "%d subscription has been successfully added.",
                        "%d subscriptions have been successfully added.",
                        len(addresses)
                    ) % len(addresses)
                )

                changelist_url = reverse(
                    'admin:newsletter_subscription_changelist'
                )
                return HttpResponseRedirect(changelist_url)
        else:
            form = ConfirmForm()

        return render(
            request,
            "admin/newsletter/subscription/confirmimportform.html",
            {'form': form, 'subscribers': addresses},
        )

    """ URLs """
    def get_urls(self):
        urls = super(SubscriptionAdmin, self).get_urls()

        my_urls = [
            url(r'^import/$',
                self._wrap(self.subscribers_import),
                name=self._view_name('import')),
            url(r'^import/confirm/$',
                self._wrap(self.subscribers_import_confirm),
                name=self._view_name('import_confirm')),

            # Translated JS strings - these should be app-wide but are
            # only used in this part of the admin. For now, leave them here.
            url(r'^jsi18n/$',
                javascript_catalog,
                {'packages': ('newsletter',)},
                name='newsletter_js18n')
        ]

        return my_urls + urls


admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
