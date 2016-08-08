from django.contrib.auth import get_user_model
from django.forms.utils import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_email_nouser(email):
    """
    Check if the email address does not belong to an existing user.
    """
    # Check whether we should be subscribed to as a user
    User = get_user_model()

    if User.objects.filter(email__exact=email).exists():
        raise ValidationError(_(
            "The e-mail address '%(email)s' belongs to a user with an "
            "account on this site. Please log in as that user "
            "and try again."
        ) % {'email': email})
