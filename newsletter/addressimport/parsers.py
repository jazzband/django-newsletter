import logging
logger = logging.getLogger(__name__)

import io

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import ugettext as _

from newsletter.models import Subscription


class AddressList(object):
    """ List with unique addresses. """

    def __init__(self, newsletter, ignore_errors=False):
        self.newsletter = newsletter
        self.ignore_errors = ignore_errors
        self.addresses = {}

    def add(self, email, name=None, location='unknown location'):
        """ Add name to list. """

        logger.debug("Going to add %s <%s>", name, email)

        name = check_name(name, self.ignore_errors)
        email = check_email(email, self.ignore_errors)

        try:
            validate_email(email)
        except ValidationError:
            logger.warning(
                "Entry '%s' does not contain a valid e-mail address at %s."
                % (email, location)
            )

            if not self.ignore_errors:
                raise forms.ValidationError(_(
                    "Entry '%s' does not contain a valid "
                    "e-mail address.") % name
                )

            # Skip this entry
            return

        if email in self.addresses:
            logger.warning(
                "Entry '%s' contains a duplicate entry at %s."
                % (email, location)
            )

            if not self.ignore_errors:
                raise forms.ValidationError(_(
                    "The address file contains duplicate entries "
                    "for '%s'.") % email)

            # Skip this entry
            return

        if subscription_exists(self.newsletter, email, name):
            logger.warning(
                "Entry '%s' is already subscribed to at %s."
                % (email, location)
            )

            if not self.ignore_errors:
                raise forms.ValidationError(
                    _("Some entries are already subscribed to."))

            # Skip this entry
            return

        self.addresses[email] = name


def subscription_exists(newsletter, email, name=None):
    """
    Return wheter or not a subscription exists.
    """
    qs = Subscription.objects.filter(
        newsletter__id=newsletter.id,
        subscribed=True,
        email_field__exact=email)

    return qs.exists()


def check_email(email, ignore_errors=False):
    """
    Check (length of) email address.

    TODO: Update this to perform full validation on email.
    """

    logger.debug("Checking e-mail address %s", email)

    email_length = Subscription._meta.get_field('email_field').max_length

    # Get rid of leading/trailing spaces
    email = email.strip()

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
    """
    Check (length of) name.

    TODO: Update this to perform full validation on name.
    """
    logger.debug("Checking name: %s", name)

    name_length = Subscription._meta.get_field('name_field').max_length

    # Get rid of leading/trailing spaces
    name = name.strip()

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


def get_encoding(myfile):
    """ Returns encoding of file, rewinding the file after detection. """

    # Detect encoding
    from chardet.universaldetector import UniversalDetector

    detector = UniversalDetector()

    for line in myfile.readlines():
        detector.feed(line)
        if detector.done:
            break

    detector.close()
    encoding = detector.result['encoding']

    # Reset the file index
    myfile.seek(0)

    return encoding


def parse_csv(myfile, newsletter, ignore_errors=False):
    """
    Parse addresses from CSV file-object into newsletter.

    Returns a dictionary mapping email addresses into Subscription objects.
    """

    import unicodecsv

    encoding = get_encoding(myfile)

    # Attempt to detect the dialect
    # Ref: https://bugs.python.org/issue5332
    encodedfile = io.TextIOWrapper(myfile, encoding=encoding, newline='')
    dialect = unicodecsv.Sniffer().sniff(encodedfile.read(1024))

    # Reset the file index
    myfile.seek(0)

    logger.info('Detected encoding %s and dialect %s for CSV file',
                encoding, dialect)

    myreader = unicodecsv.reader(myfile, dialect=dialect, encoding=encoding)

    firstrow = next(myreader)

    # Find name column
    colnum = 0
    namecol = None
    for column in firstrow:
        if "name" in column.lower() or _("name") in column.lower():
            namecol = colnum

            if "display" in column.lower() or \
                    _("display") in column.lower():
                break

        colnum += 1

    if namecol is None:
        raise forms.ValidationError(_(
            "Name column not found. The name of this column should be "
            "either 'name' or '%s'.") % _("name")
        )

    logger.debug("Name column found: '%s'", firstrow[namecol])

    # Find email column
    colnum = 0
    mailcol = None
    for column in firstrow:
        if 'email' in column.lower() or \
                'e-mail' in column.lower() or \
                _("e-mail") in column.lower():

            mailcol = colnum

            break

        colnum += 1

    if mailcol is None:
        raise forms.ValidationError(_(
            "E-mail column not found. The name of this column should be "
            "either 'email', 'e-mail' or '%(email)s'.") %
            {'email': _("e-mail")}
        )

    logger.debug("E-mail column found: '%s'", firstrow[mailcol])

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

    address_list = AddressList(newsletter, ignore_errors)

    for row in myreader:
        if not max(namecol, mailcol) < len(row):
            logger.warning(
                "Column count does not match for row number %d",
                myreader.line_num, extra=dict(data={'row': row})
            )

            if ignore_errors:
                # Skip this record
                continue
            else:
                raise forms.ValidationError(_(
                    "Row with content '%(row)s' does not contain a name and "
                    "email field.") % {'row': row}
                )

        address_list.add(
            row[mailcol], row[namecol], location="line %d" % myreader.line_num
        )

    return address_list.addresses


def parse_vcard(myfile, newsletter, ignore_errors=False):
    """
    Parse addresses from vCard file-object into newsletter.

    Returns a dictionary mapping email addresses into Subscription objects.
    """
    import card_me

    encoding = get_encoding(myfile)
    encodedfile = io.TextIOWrapper(myfile, encoding=encoding)

    try:
        myvcards = card_me.readComponents(encodedfile)
    except card_me.VObjectError as e:
        raise forms.ValidationError(
            _(u"Error reading vCard file: %s" % e)
        )

    address_list = AddressList(newsletter, ignore_errors)

    for myvcard in myvcards:
        if hasattr(myvcard, 'fn'):
            name = myvcard.fn.value
        else:


            name = None

        # Do we have an email address?
        # If not: either continue to the next vcard or raise validation error.
        if hasattr(myvcard, 'email'):
            email = myvcard.email.value
        elif not ignore_errors:
            raise forms.ValidationError(
                _("Entry '%s' contains no email address.") % name)
        else:
            continue

        address_list.add(email, name)

    return address_list.addresses


def parse_ldif(myfile, newsletter, ignore_errors=False):
    """
    Parse addresses from LDIF file-object into newsletter.

    Returns a dictionary mapping email addresses into Subscription objects.
    """

    from ldif3 import LDIFParser

    address_list = AddressList(newsletter, ignore_errors)

    try:
        parser = LDIFParser(myfile)

        for dn, entry in parser.parse():
            if 'mail' in entry:
                email = entry['mail'][0]

                if 'cn' in entry:
                    name = entry['cn'][0]
                else:
                    name = None

                address_list.add(email, name)

            elif not ignore_errors:
                raise forms.ValidationError(
                    _("Some entries have no e-mail address."))

    except ValueError as e:
        if not ignore_errors:
            raise forms.ValidationError(e)

    return address_list.addresses
