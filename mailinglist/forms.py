from django.utils.translation import ugettext_lazy as _

from django import newforms as forms
from django.newforms import widgets
from django.newforms.util import ValidationError, ErrorList

from models import *

def getSubscriptionFromEmail(mynewsletter, myemail):
        try:
            instance = Subscription.objects.get(newsletter__id=mynewsletter.id, email__exact=myemail)
        except Subscription.DoesNotExist:
            raise ValidationError(_("The email address you specified has not been subscribed to."))
        
        return instance

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ('name', 'email')
        
    def __init__(self, *args, **kwargs):
        assert kwargs.has_key('newsletter'), 'No newsletter specified.'
        newsletter = kwargs['newsletter']
        del kwargs['newsletter']

        super(NewsletterForm, self).__init__(*args, **kwargs)
        self.instance.newsletter = newsletter

class SubscribeForm(NewsletterForm):
    def clean_email(self):
        myfield = self.base_fields['email']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('email'))

        # Set our instance on the basis of the email field, or raise a validationerror
        try:
            Subscription.objects.get(newsletter__id=mynewsletter.id, email__exact=value, activated=True)
        except Subscription.DoesNotExist:
            raise ValidationError(_("Your email address has already been subscribed to."))

        return value    

    def save(self, commit=True):
        super(SubscribeForm, self).save(commit)
        
        # Send an activation email

class SubscribeActivateForm(NewsletterForm):                
    def clean_user_activation_code(self):
        myfield = self.base_fields['user_activation_code']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('user_activation_code'))
        user_activation_code = myfield.clean(value)
        
        if user_activation_code != instance.activation_code:
            raise ValidationError(_('The validation code supplied by you does not match.'))

    def clean_email(self):
        myfield = self.base_fields['email']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('email'))

        # Set our instance on the basis of the email field, or raise a validationerror
        self.instance = getSubscriptionFromEmail(self.instance.newsletter, value)

        return value        
        
    def save(self, commit=True):
        self.instance.activated = True
        instance = super(SubscribeActivateForm, self).save(commit)
        
    user_activation_code = forms.CharField(label=_("activation code"), max_length=40)
        
class UnsubscribeForm(NewsletterForm):
    class Meta(NewsletterForm.Meta):
        fields = ('email',)
        
    def clean_email(self):
        myfield = self.base_fields['email']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('email'))

        # Set our instance on the basis of the email field, or raise a validationerror
        self.instance = getSubscriptionFromEmail(self.instance.newsletter, value)

        return value        
        
    def save(self, commit=True):
        # No need to actually save, just send the user a confirmation email for unsubscription
        pass
        
class UnsubscribeActivateForm(SubscribeActivateForm):
    def save(self, commit=True):
        self.instance.ubsubscribed = True
        
        super(UnsubscribeActivateForm, self).save(commit)
        