from django import forms
from django.forms.utils import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Subscription
from .validators import validate_email_nouser


class NewsletterForm(forms.ModelForm):
    """ This is the base class for all forms managing subscriptions. """

    class Meta:
        model = Subscription
        fields = ('name_field', 'email_field')

    def __init__(self, *args, **kwargs):

        assert 'newsletter' in kwargs, 'No newsletter specified'

        newsletter = kwargs.pop('newsletter')

        if 'ip' in kwargs:
            ip = kwargs['ip']
            del kwargs['ip']
        else:
            ip = None

        super(NewsletterForm, self).__init__(*args, **kwargs)

        self.instance.newsletter = newsletter

        if ip:
            self.instance.ip = ip


class SubscribeRequestForm(NewsletterForm):
    """
    Request subscription to the newsletter. Will result in an activation email
    being sent with a link where one can edit, confirm and activate one's
    subscription.
    """

    email_field = forms.EmailField(
        label=_("e-mail"), validators=[validate_email_nouser]
    )

    def clean_email_field(self):
        data = self.cleaned_data['email_field']

        # Check whether we have already been subscribed to
        try:
            subscription = Subscription.objects.get(
                email_field__exact=data,
                newsletter=self.instance.newsletter
            )

            if subscription.subscribed and not subscription.unsubscribed:
                raise ValidationError(
                    _("Your e-mail address has already been subscribed to.")
                )
            else:
                self.instance = subscription

            self.instance = subscription

        except Subscription.DoesNotExist:
            pass

        return data


class UpdateRequestForm(NewsletterForm):
    """
    Request updating or activating subscription. Will result in an activation
    email being sent.
    """

    email_field = forms.EmailField(
        label=_("e-mail"), validators=[validate_email_nouser]
    )

    class Meta(NewsletterForm.Meta):
        fields = ('email_field',)

    def clean(self):
        if not self.instance.subscribed:
            raise ValidationError(
                _("This subscription has not yet been activated.")
            )

        return super(UpdateRequestForm, self).clean()

    def clean_email_field(self):
        data = self.cleaned_data['email_field']

        # Set our instance on the basis of the email field, or raise
        # a validationerror
        try:
            self.instance = Subscription.objects.get(
                newsletter=self.instance.newsletter,
                email_field__exact=data
            )

        except Subscription.DoesNotExist:
                raise ValidationError(
                    _("This e-mail address has not been subscribed to.")
                )

        return data


class UnsubscribeRequestForm(UpdateRequestForm):
    """
    Similar to previous form but checks if we have not
    already been unsubscribed.
    """

    def clean(self):
        if self.instance.unsubscribed:
            raise ValidationError(
                _("This subscription has already been unsubscribed from.")
            )

        return super(UnsubscribeRequestForm, self).clean()


class UpdateForm(NewsletterForm):
    """
    This form allows one to actually update to or unsubscribe from the
    newsletter. To do this, a correct activation code is required.
    """

    email_field = forms.EmailField(
        label=_("e-mail"), validators=[validate_email_nouser], disabled=True
    )

    def clean_user_activation_code(self):
        data = self.cleaned_data['user_activation_code']

        if data != self.instance.activation_code:
            raise ValidationError(
                _('The validation code supplied by you does not match.')
            )

        return data

    user_activation_code = forms.CharField(
        label=_("Activation code"), max_length=40
    )


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating subscription information/unsubscribing as a logged-in
    user.
    """

    class Meta:
        model = Subscription
        fields = ('subscribed',)
        # Newsletter here should become a read only field,
        # once this is supported by Django.

        # For now, use a hidden field.
        hidden_fields = ('newsletter',)
