import logging

logger = logging.getLogger(__name__)

from django import forms

from django.contrib.admin import widgets, options

from django.core.exceptions import ValidationError

from django.core.validators import validate_email

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.conf import settings

from .models import Subscription, Newsletter, Submission


def make_subscription(newsletter, email, name=None):
    qs = Subscription.objects.filter(
        newsletter__id=newsletter.id,
        subscribed=True,
        email_field__exact=email)

    if qs.count():
        return None

    addr = Subscription(subscribed=True)
    addr.newsletter = newsletter

    addr.email_field = email

    if name:
        addr.name_field = name

    return addr


def check_email(email, ignore_errors=False):
    if settings.DEBUG:
        logger.debug("Checking e-mail address %s", email)

    email_length = \
        Subscription._meta.get_field_by_name('email_field')[0].max_length

    if len(email) <= email_length or ignore_errors:
        return email[:email_length]
    else:
        raise forms.ValidationError(
            _(
                "E-mail address %(email)s too long, maximum length is "
                "%(email_length)s characters."
            ) % {
                "email": email,
                "email_length": email_length
            }
        )


def check_name(name, ignore_errors=False):
    if settings.DEBUG:
        logger.debug("Checking name: %s", name)

    name_length = \
        Subscription._meta.get_field_by_name('name_field')[0].max_length
    if len(name) <= name_length or ignore_errors:
        return name[:name_length]
    else:
        raise forms.ValidationError(
            _(
                "Name %(name)s too long, maximum length is "
                "%(name_length)s characters."
            ) % {
                "name": name,
                "name_length": name_length
            }
        )


def parse_csv(myfile, newsletter, ignore_errors=False):
    from newsletter.addressimport.csv_util import UnicodeReader
    import codecs
    import csv

    # Detect encoding
    from chardet.universaldetector import UniversalDetector

    detector = UniversalDetector()

    for line in myfile.readlines():
        detector.feed(line)
        if detector.done:
            break

    detector.close()
    charset = detector.result['encoding']

    # Reset the file index
    myfile.seek(0)

    # Attempt to detect the dialect
    encodedfile = codecs.EncodedFile(myfile, charset)
    dialect = csv.Sniffer().sniff(encodedfile.read(1024))

    # Reset the file index
    myfile.seek(0)

    logger.info('Detected encoding %s and dialect %s for CSV file',
                charset, dialect)

    myreader = UnicodeReader(myfile, dialect=dialect, encoding=charset)

    firstrow = myreader.next()

    # Find name column
    colnum = 0
    namecol = None
    for column in firstrow:
        if "name" in column.lower() or ugettext("name") in column.lower():
            namecol = colnum

            if "display" in column.lower() or \
                    ugettext("display") in column.lower():
                break

        colnum += 1

    if namecol is None:
        raise forms.ValidationError(_(
            "Name column not found. The name of this column should be "
            "either 'name' or '%s'.") % ugettext("name")
        )

    logger.debug("Name column found: '%s'", firstrow[namecol])

    # Find email column
    colnum = 0
    mailcol = None
    for column in firstrow:
        if 'email' in column.lower() or \
                'e-mail' in column.lower() or \
                ugettext("e-mail") in column.lower():

            mailcol = colnum

            break

        colnum += 1

    if mailcol is None:
        raise forms.ValidationError(_(
            "E-mail column not found. The name of this column should be "
            "either 'email', 'e-mail' or '%(email)s'.") %
            {'email': ugettext("e-mail")}
        )

    logger.debug("E-mail column found: '%s'", firstrow[mailcol])

    #assert namecol != mailcol, \
    #    'Name and e-mail column should not be the same.'
    if namecol == mailcol:
        raise forms.ValidationError(
            _(
                "Could not properly determine the proper columns in the "
                "CSV-file. There should be a field called 'name' or "
                "'%(name)s' and one called 'e-mail' or '%(e-mail)s'."
            ) % {
                "name": _("name"),
                "e-mail": _("e-mail")
            }
        )

    logger.debug('Extracting data.')

    addresses = {}
    for row in myreader:
        if not max(namecol, mailcol) < len(row):
            logger.warn("Column count does not match for row number %d",
                        myreader.line_num, extra=dict(data={'row': row}))

            if ignore_errors:
                # Skip this record
                continue
            else:
                raise forms.ValidationError(_(
                    "Row with content '%(row)s' does not contain a name and "
                    "email field.") % {'row': row}
                )

        name = check_name(row[namecol], ignore_errors)
        email = check_email(row[mailcol], ignore_errors)

        logger.debug("Going to add %s <%s>", name, email)

        try:
            validate_email(email)
            addr = make_subscription(newsletter, email, name)
        except ValidationError:
            if ignore_errors:
                logger.warn(
                    "Entry '%s' at line %d does not contain a valid "
                    "e-mail address.",
                    name, myreader.line_num, extra=dict(data={'row': row}))
            else:
                raise forms.ValidationError(_(
                    "Entry '%s' does not contain a valid "
                    "e-mail address.") % name
                )

        if addr:
            if email in addresses:
                logger.warn(
                    "Entry '%s' at line %d contains a "
                    "duplicate entry for '%s'",
                    name, myreader.line_num, email,
                    extra=dict(data={'row': row}))

                if not ignore_errors:
                    raise forms.ValidationError(_(
                        "The address file contains duplicate entries "
                        "for '%s'.") % email)

            addresses.update({email: addr})
        else:
            logger.warn(
                "Entry '%s' at line %d is already subscribed to "
                "with email '%s'",
                name, myreader.line_num, email, extra=dict(data={'row': row}))

            if not ignore_errors:
                raise forms.ValidationError(
                    _("Some entries are already subscribed to."))

    return addresses


def parse_vcard(myfile, newsletter, ignore_errors=False):
    import vobject

    try:
        myvcards = vobject.readComponents(myfile)
    except vobject.VObjectError, e:
        raise forms.ValidationError(
            _(u"Error reading vCard file: %s" % e)
        )

    addresses = {}

    for myvcard in myvcards:
        if hasattr(myvcard, 'fn'):
            name = check_name(myvcard.fn.value, ignore_errors)
        else:
            name = None

        # Do we have an email address?
        # If not: either continue to the next vcard or
        # raise a validation error.
        if hasattr(myvcard, 'email'):
            email = check_email(myvcard.email.value, ignore_errors)
        elif not ignore_errors:
            raise forms.ValidationError(
                _("Entry '%s' contains no email address.") % name)
        else:
            continue

        try:
            validate_email(email)
            addr = make_subscription(newsletter, email, name)
        except ValidationError:
            if not ignore_errors:
                raise forms.ValidationError(
                    _("Entry '%s' does not contain a valid e-mail address.")
                    % name
                )

        if addr:
            if email in addresses and not ignore_errors:
                raise forms.ValidationError(
                    _("The address file contains duplicate entries for '%s'.")
                    % email
                )

            addresses.update({email: addr})
        elif not ignore_errors:
            raise forms.ValidationError(
                _("Some entries are already subscribed to."))

    return addresses


def parse_ldif(myfile, newsletter, ignore_errors=False):
    from addressimport import ldif

    class AddressParser(ldif.LDIFParser):
        addresses = {}

        def handle(self, dn, entry):
            if 'mail' in entry:
                email = check_email(entry['mail'][0], ignore_errors)
                if 'cn' in entry:
                    name = check_name(entry['cn'][0], ignore_errors)
                else:
                    name = None

                try:
                    validate_email(email)
                    addr = make_subscription(newsletter, email, name)
                except ValidationError:
                    if not ignore_errors:
                        raise forms.ValidationError(_(
                            "Entry '%s' does not contain a valid "
                            "e-mail address.") % name
                        )

                if addr:
                    if email in self.addresses and not ignore_errors:
                        raise forms.ValidationError(_(
                            "The address file contains duplicate entries "
                            "for '%s'.") % email
                        )

                    self.addresses.update({email: addr})
                elif not ignore_errors:
                    raise forms.ValidationError(
                        _("Some entries are already subscribed to."))

            elif not ignore_errors:
                raise forms.ValidationError(
                    _("Some entries have no e-mail address."))
    try:
        myparser = AddressParser(myfile)
        myparser.parse()
    except ValueError, e:
        if not ignore_errors:
            raise forms.ValidationError(e)

    return myparser.addresses


class ImportForm(forms.Form):

    def clean(self):
        # If there are validation errors earlier on, don't bother.
        if not ('address_file' in self.cleaned_data and
                'ignore_errors' in self.cleaned_data and
                'newsletter' in self.cleaned_data):
            return self.cleaned_data
            # TESTME: Should an error be raised here or not?
            #raise forms.ValidationError(_("No file has been specified."))

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

        self.addresses = []

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
                _("File extention '%s' was not recognized.") % ext)

        if len(self.addresses) == 0:
            raise forms.ValidationError(
                _("No entries could found in this file."))

        return self.cleaned_data

    def get_addresses(self):
        if hasattr(self, 'addresses'):
            logger.debug('Getting addresses: %s', self.addresses)
            return self.addresses
        else:
            return {}

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
                    (True, ugettext('Subscribed')),
                    (False, ugettext('Unsubscribed'))
                ],
                attrs={
                    'class': options.get_ul_class(options.HORIZONTAL)
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super(SubscriptionAdminForm, self).__init__(*args, **kwargs)

        self.fields['subscribed'].label = ugettext('Status')

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

        if publish:
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
