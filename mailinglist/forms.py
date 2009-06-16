from django.utils.translation import ugettext_lazy as _

from django import forms
from django.newforms import widgets
from django.newforms.util import ValidationError, ErrorList

from models import Subscription

def getSubscriptionFromEmail(mynewsletter, myemail):
        try:
            instance = Subscription.objects.get(newsletter__id=mynewsletter.id, email__exact=myemail)
        except Subscription.DoesNotExist:
            raise ValidationError(_("The e-mail address you specified has not been subscribed to."))
        
        return instance

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ('name', 'email')
        
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

class SubscribeForm(NewsletterForm):        
    def clean_email(self):
        myfield = self.base_fields['email']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('email'))

        # Set our instance on the basis of the email field, or raise a validationerror
        try:
            subscription = Subscription.objects.get(email__exact=value, newsletter=self.instance.newsletter)
            if subscription.activated == True and subscription.unsubscribed == False:
                raise ValidationError(_("Your e-mail address has already been subscribed to."))
            else:
                self.instance = subscription
                
        except Subscription.DoesNotExist:
            pass

        return value
    
    def save(self, commit=True):
        instance = super(SubscribeForm, self).save(commit)
        instance.send_activation_email(action='subscribe')
        return instance

class ActivateForm(NewsletterForm):        
    class Meta:
        fields = (None,)
        
    def clean_user_activation_code(self):
        myfield = self.base_fields['user_activation_code']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('user_activation_code'))
        user_activation_code = myfield.clean(value)
        
        if user_activation_code != self.instance.activation_code:
            raise ValidationError(_('The validation code supplied by you does not match.'))

    def save(self, commit=True):
        return super(ActivateForm, self).save(commit)
          
    user_activation_code = forms.CharField(label=_("Activation code"), max_length=40)
    
class UpdateForm(NewsletterForm):
    class Meta(NewsletterForm.Meta):
        fields = ('name','email',)

    def clean(self):
        # BUG ALERT:
        # A ValidationError in clean does most probably NOT get caught by Django.
        if not self.instance.activated:
            ValidationError(_("The subscription has not yet been activated."))
            
        if self.instance.unsubscribed:
            ValidationError(_("The subscription has been unsubscribed. To update your information, please subscribe again."))

        return super(UpdateForm, self).clean()
        
class UnsubscribeForm(UpdateForm):
    class Meta(NewsletterForm.Meta):
        fields = ('email',)
        
    def clean_email(self):
        myfield = self.base_fields['email']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('email'))

        # Set our instance on the basis of the email field, or raise a validationerror
        try:
            self.instance = Subscription.objects.get(newsletter=self.instance.newsletter, email__exact=value)
            if self.instance.activated == False:
                raise ValidationError(_("The subscription has not yet been activated."))
                
        except Subscription.DoesNotExist:
                raise ValidationError(_("This e-mail address has not been subscribed to."))

        return value  
        
    def save(self, commit=True):
        self.instance.send_activation_email(action='unsubscribe')
        return self.instance

