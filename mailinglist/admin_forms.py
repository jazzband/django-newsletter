from django.utils.translation import ugettext_lazy as _

from django import newforms as forms
#from django.newforms import widgets

from django.newforms.util import ValidationError

from models import Subscription

class ImportForm(forms.Form):
    class Meta:
        pass

    def clean_address_file(self):
        # This is _not_ neat code
        myfield = self.base_fields['ignore_errors']
        myvalue = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('ignore_errors'))
        ignore_errors = myfield.clean(myvalue)
        
        myfield = self.base_fields['address_file']
        myvalue = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('address_file'))
        myfile = myfield.clean(myvalue)
        
        content_type = myvalue.content_type
        allowed_types = ['text/plain', 'application/octet-stream', ]
        if content_type not in allowed_types:
            raise ValidationError(_("File type '%s' was not recognized.") % content_type)

        self.addresses = []
        
        ext = myvalue.file_name.rsplit('.', 1)[-1].lower()
        if ext == 'vcf':
            pass
            
        elif ext == 'ldif':
            from addressimport import ldif
            class AddressParser(ldif.LDIFParser):
                addresses = []

                def handle(self, dn, entry):
                    if entry.has_key('mail'):
                        mail = entry['mail'][0]
                        print 'parsing', mail
                        subscriber = Subscription(email=mail, activated=True)

                        #if entry.has_key('cn'):
                        #    subscriber.name = entry['cn'][0]
                        
                        #print 'result', subscriber
                        #self.addresses.append(subscriber)
                    elif not ignore_errors:
                        raise ValidationError(_("Some entries have no e-mail address."))
            try:
                myparser = AddressParser(myvalue.file).parse()
                self.addresses = myparser.addresses
            except ValueError, e:
                if ignore_errors:
                    raise ValidationError(e)
                #raise ValidationError(_("Error parsing address file."))

        elif ext == 'vcf':
            pass
            
        else:
            raise ValidationError(_("File extention '%s' was not recognized.") % ext)

        return myfile

    def get_addresses(self):
        print 'adressen', self.addresses
        return self.addresses
        
    address_file = forms.FileField(label=_("Address file"),)
    ignore_errors = forms.BooleanField(label=_("Ignore parse errors"), initial=False, required=False)
    
class ConfirmForm(forms.Form):
    def clean_confirm(self):
        value = super(ConfirmForm, self).clean_confirm()
        
        if not value:
            raise ValidationError(_("You should confirm in order to continue."))
            
        return value
        
    confirm = forms.BooleanField(label=_("Confirm import"),)