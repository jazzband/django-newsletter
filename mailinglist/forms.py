from django.utils.translation import ugettext_lazy as _

from django import newforms as forms
from django.newforms import widgets
from django.newforms.util import ValidationError, ErrorList

from models import *


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ('name', 'email')
        
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 instance=None, newsletter=None):
        assert newsletter, 'No newsletter given'
        super(SubscribeForm, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, instance)
        self.instance.newsletter = newsletter
    
    def save(self, commit=True):
        super(SubscribeForm, self).save(commit)
        
        # Send an activation email

class ActivateForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ('name', 'email')
                
    def clean_user_activation_code(self):
        myfield = self.base_fields['user_activation_code']
        value = myfield.widget.value_from_datadict(self.data, self.files, self.add_prefix('user_activation_code'))
        user_activation_code = myfield.clean(value)
        
        if user_activation_code != instance.activation_code:
            raise ValidationError(_('The validation code supplied by you does not match.'))
        
    def save(self, commit=True):
        self.instance.activated = True
        instance = super(ActivateForm, self).save(commit)
        
    user_activation_code = forms.CharField(label=_("activation code"), max_length=40)

        
class UnsubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ('email',)
        
class UnsubscribeActivateForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ('email', 'activation_code')

