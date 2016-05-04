import logging

from django import forms

from django.contrib.admin import widgets, options

from django.utils.translation import ugettext as _

from .models import Subscription, Newsletter, Submission
from .addressimport.parsers import parse_csv, parse_vcard, parse_ldif


logger = logging.getLogger(__name__)


class ImportForm(forms.Form):

    def clean(self):
        # If there are validation errors earlier on, don't bother.
        if not ('address_file' in self.cleaned_data and
                'ignore_errors' in self.cleaned_data and
                'newsletter' in self.cleaned_data):
            return self.cleaned_data
            # TESTME: Should an error be raised here or not?
            # raise forms.ValidationError(_("No file has been specified."))

        ignore_errors = self.cleaned_data['ignore_errors']
        newsletter = self.cleaned_data['newsletter']

        myfield = self.base_fields['address_file']
        myvalue = myfield.widget.value_from_datadict(
            self.data, self.files, self.add_prefix('address_file'))

        content_type = myvalue.content_type
        allowed_types = ('text/plain', 'application/octet-stream',
                         'text/vcard', 'text/directory', 'text/x-vcard',
                         'application/vnd.ms-excel',
                         'text/comma-separated-values', 'text/csv',
                         'application/csv', 'application/excel',
                         'application/vnd.msexcel', 'text/anytext')
        if content_type not in allowed_types:
            raise forms.ValidationError(_(
                "File type '%s' was not recognized.") % content_type)

        ext = myvalue.name.rsplit('.', 1)[-1].lower()
        if ext == 'vcf':
            self.addresses = parse_vcard(
                myvalue.file, newsletter, ignore_errors)

        elif ext == 'ldif':
            self.addresses = parse_ldif(
                myvalue.file, newsletter, ignore_errors)

        elif ext == 'csv':
            self.addresses = parse_csv(
                myvalue.file, newsletter, ignore_errors)

        else:
            raise forms.ValidationError(
                _("File extension '%s' was not recognized.") % ext)

        if len(self.addresses) == 0:
            raise forms.ValidationError(
                _("No entries could found in this file."))

        return self.cleaned_data

    def get_addresses(self):
        return getattr(self, 'addresses', {})

    newsletter = forms.ModelChoiceField(
        label=_("Newsletter"),
        queryset=Newsletter.objects.all(),
        initial=Newsletter.get_default)
    address_file = forms.FileField(label=_("Address file"))
    ignore_errors = forms.BooleanField(
        label=_("Ignore non-fatal errors"),
        initial=False, required=False)


class ConfirmForm(forms.Form):

    def clean(self):
        value = self.cleaned_data['confirm']

        if not value:
            raise forms.ValidationError(
                _("You should confirm in order to continue."))

    confirm = forms.BooleanField(
        label=_("Confirm import"),
        initial=True, widget=forms.HiddenInput)


class SubscriptionAdminForm(forms.ModelForm):

    class Meta:
        model = Subscription
        fields = '__all__'
        widgets = {
            'subscribed': widgets.AdminRadioSelect(
                choices=[
                    (True, _('Subscribed')),
                    (False, _('Unsubscribed'))
                ],
                attrs={
                    'class': options.get_ul_class(options.HORIZONTAL)
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super(SubscriptionAdminForm, self).__init__(*args, **kwargs)

        self.fields['subscribed'].label = _('Status')

    def clean_email_field(self):
        data = self.cleaned_data['email_field']
        if self.cleaned_data['user'] and data:
            raise forms.ValidationError(_(
                'If a user has been selected this field '
                'should remain empty.'))
        return data

    def clean_name_field(self):
        data = self.cleaned_data['name_field']
        if self.cleaned_data['user'] and data:
            raise forms.ValidationError(_(
                'If a user has been selected '
                'this field should remain empty.'))
        return data

    def clean(self):
        cleaned_data = super(SubscriptionAdminForm, self).clean()
        if not (cleaned_data.get('user', None) or
                cleaned_data.get('email_field', None)):

            raise forms.ValidationError(_(
                'Either a user must be selected or an email address must '
                'be specified.')
            )
        return cleaned_data


class SubmissionAdminForm(forms.ModelForm):

    class Meta:
        model = Submission
        fields = '__all__'

    def clean_publish(self):
        """
        Make sure only one submission can be published for each message.
        """
        publish = self.cleaned_data['publish']

        if publish and not self.errors:
            message = self.cleaned_data['message']
            qs = Submission.objects.filter(publish=True, message=message)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(_(
                    'This message has already been published in some '
                    'other submission. Messages can only be published once.')
                )

        return publish


class ArticleFormSet(forms.BaseInlineFormSet):
    """ Formset for articles yielding default sortoder. """

    def __init__(self, *args, **kwargs):
        super(ArticleFormSet, self).__init__(*args, **kwargs)

        assert self.instance
        next_sortorder = self.instance.get_next_article_sortorder()
        for index, form in enumerate(self.extra_forms):
            form.initial['sortorder'] = next_sortorder + index * 10
