from django.test import TestCase
from django.forms.utils import ValidationError
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

from newsletter.validators import validate_email_nouser


class ValidatorTestCase(TestCase):
    """ Test case for validators. """

    def test_validate_email_nouser_noerror(self):
        """ Test validate_email_nouser where no error is raised. """
        validate_email_nouser('test@nowhere.com')

    def test_validate_email_nouser_error(self):
        """ Test validate_email_nouser where error is raised. """
        User = get_user_model()
        password = get_random_string(length=16)
        user = User.objects.create_user(
            'john', 'lennon@thebeatles.com', password)
        user.save()

        with self.assertRaises(ValidationError):
            validate_email_nouser(user.email)
