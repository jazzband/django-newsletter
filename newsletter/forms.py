from django import forms
from django.db import transaction
from django.forms.utils import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Newsletter, Subscription
from .validators import validate_email_no_user


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

        super().__init__(*args, **kwargs)

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
        label=_("e-mail"), validators=[validate_email_no_user]
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
        label=_("e-mail"), validators=[validate_email_no_user]
    )

    class Meta(NewsletterForm.Meta):
        fields = ('email_field',)

    def clean(self):
        if not self.instance.subscribed:
            raise ValidationError(
                _("This subscription has not yet been activated.")
            )

        return super().clean()

    def clean_email_field(self):
        data = self.cleaned_data['email_field']
        newsletter = self.instance.newsletter

        # Set our instance on the basis of the email field, or raise
        # a ValidationError
        try:
            self.instance = Subscription.objects.get(
                newsletter=self.instance.newsletter,
                email_field__exact=data
            )

        except Subscription.DoesNotExist:
            instance = newsletter.create_subscription_from_generator(data, commit=False)
            if instance:
                self.instance = instance
            else:
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

        return super().clean()


class UpdateForm(NewsletterForm):
    """
    This form allows one to actually update to or unsubscribe from the
    newsletter. To do this, a correct activation code is required.
    """

    email_field = forms.EmailField(
        label=_("e-mail"), validators=[validate_email_no_user], disabled=True
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
        fields = ('newsletter', 'subscribed')
        widgets = {'newsletter': forms.HiddenInput}

    def __init__(self, *args, newsletter=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['newsletter'].queryset = Newsletter.objects.filter(
            pk=newsletter.pk
        ) if newsletter else Newsletter.objects.none()


class BaseUserUpdateFormSet(forms.BaseFormSet):
    def __init__(self, *args, newsletters, user, **kwargs):
        self.newsletters = list(newsletters)
        self.user = user
        self.subscriptions = {
            subscription.newsletter_id: subscription
            for subscription in Subscription.objects.filter(
                newsletter__in=self.newsletters, user=user
            )
        }
        kwargs['initial'] = [
            {
                'newsletter': newsletter.pk,
                'subscribed': (
                    self.subscriptions[newsletter.pk].subscribed
                    if newsletter.pk in self.subscriptions else False
                ),
            }
            for newsletter in self.newsletters
        ]
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        if index is not None and index < len(self.newsletters):
            newsletter = self.newsletters[index]
            kwargs['newsletter'] = newsletter
            kwargs['instance'] = self.subscriptions.get(newsletter.pk) or Subscription(
                newsletter=newsletter, user=self.user
            )
        return kwargs

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        if (self.total_form_count() != len(self.newsletters) or
                self.initial_form_count() != len(self.newsletters)):
            raise ValidationError(
                _("The newsletter list has changed. Please reload the page.")
            )

    @transaction.atomic
    def save(self):
        for form in self.forms:
            if form.has_changed():
                form.save()


UserUpdateFormSet = forms.formset_factory(
    UserUpdateForm, formset=BaseUserUpdateFormSet, extra=0
)
