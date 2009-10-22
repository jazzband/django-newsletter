from django.utils.translation import ugettext_lazy as _

from django import forms
from django.forms import widgets
from django.forms.util import ValidationError, ErrorList

from models import Subscription

def getSubscriptionFromEmail(mynewsletter, myemail):
        try:
            instance = Subscription.objects.get(newsletter__id=mynewsletter.id, email_field__exact=myemail)
        except Subscription.DoesNotExist:
            raise ValidationError(_("The e-mail address you specified has not been subscribed to."))
        
        return instance

class NewsletterForm(forms.ModelForm):
    """ This is the base class for all forms managing subscriptions. """
    
    class Meta:
        model = Subscription
        fields = ('name_field', 'email_field')

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('newsletter'):
            newsletter = kwargs['newsletter']
            del kwargs['newsletter']            
        else:
            newsletter = None
        
        if kwargs.has_key('ip'):
            ip = kwargs['ip']
            del kwargs['ip']
        else:
            ip = None
        
        super(NewsletterForm, self).__init__(*args, **kwargs)
         
        if newsletter:
            self.instance.newsletter = newsletter
        
        if ip:
            self.instance.ip = ip
            
class SubscribeRequestForm(NewsletterForm):        
    """ Request subscription to the newsletter. Will result in an activation email
        being sent with a link where one can edit, confirm and activate one's subscription. 
    """
        
    def clean_email_field(self):
        myfield = self.base_fields['email_field']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('email_field'))

        # Set our instance on the basis of the email field, or raise a validationerror
        try:
            subscription = Subscription.objects.get(email_field__exact=value, newsletter=self.instance.newsletter)
            if subscription.activated == True and subscription.unsubscribed == False:
                raise ValidationError(_("Your e-mail address has already been subscribed to."))
            
            self.instance = subscription
                
        except Subscription.DoesNotExist:
            pass
        
        return value

class UpdateRequestForm(NewsletterForm):
    """ Request updating or activating subscription. Will result in an activation
        email being sent.
    """
    
    class Meta(NewsletterForm.Meta):
        fields = ('email_field',)
    
    def clean_email_field(self):
        myfield = self.base_fields['email_field']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('email_field'))
        
        # Set our instance on the basis of the email field, or raise a validationerror
        try:
            self.instance = Subscription.objects.get(newsletter=self.instance.newsletter, email_field__exact=value)
                
        except Subscription.DoesNotExist:
                raise ValidationError(_("This e-mail address has not been subscribed to."))
                
        return value
    
    def clean(self):
        if not self.instance.activated:
            raise ValidationError(_("This subscription has not yet been activated."))


class UnsubscribeRequestForm(UpdateRequestForm):
    """ Similar to previous form but checks if we have not already been unsubscribed. """
    
    def clean(self):
        super(UnsubscribeRequestForm, self).clean()
        
        if self.instance.unsubscribed:
            raise ValidationError(_("This subscription has already been unsubscribed from."))

class UpdateForm(NewsletterForm):
    """ This form allows one to actually update to or unsubscribe from the newsletter. To do this, a 
        correct activation code is required. 
    """
    def clean_user_activation_code(self):
        myfield = self.base_fields['user_activation_code']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('user_activation_code'))
        user_activation_code = myfield.clean(value)
        
        if user_activation_code != self.instance.activation_code:
            raise ValidationError(_('The validation code supplied by you does not match.'))
          
    user_activation_code = forms.CharField(label=_("Activation code"), max_length=40)
