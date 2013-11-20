import logging

logger = logging.getLogger(__name__)

from django.core import mail

from django.test import TestCase

from django.contrib.sites.models import Site

from django.template import loader, TemplateDoesNotExist

from django_webtest import WebTest

from ..utils import get_user_model
User = get_user_model()


class WebTestCase(WebTest):
    def setUp(self):
        self.site = Site.objects.get_current()

        super(WebTestCase, self).setUp()

    def assertInContext(self, response, variable,
                        instance_of=None, value=None):
        try:
            instance = response.context[variable]
            self.assert_(instance)
        except KeyError:
            self.fail(
                'Asserted variable %s not in response context.' % variable
            )

        if instance_of:
            self.assert_(isinstance(instance, instance_of))

        if value:
            self.assertEqual(instance, value)


class MailTestCase(TestCase):
    def get_email_list(self, email):
        if email:
            return (email,)
        else:
            return mail.outbox

    def assertEmailContains(self, value, email=None):
        for my_email in self.get_email_list(email):
            self.assert_(
                (value in my_email.subject) or
                (value in my_email.body),
                'Email does not contain "%s".' % value
            )

    def assertEmailBodyContains(self, value, email=None):
        for my_email in self.get_email_list(email):
            self.assert_(
                value in my_email.body,
                'Email body does not contain "%s".' % value
            )

    def assertEmailSubjectContains(self, value, email=None):
        for my_email in self.get_email_list(email):
            self.assert_(
                value in my_email.subject,
                'Email subject does not contain "%s".' % value
            )

    def assertEmailHasNoAlternatives(self, email=None):
        for my_email in self.get_email_list(email):
            self.assert_(
                not getattr(my_email, 'alternatives', None),
                'Email has alternative content types.'
            )

    def assertEmailAlternativesContainMimetype(self, mimetype, email=None):
        for my_email in self.get_email_list(email):
            self.assert_(
                mimetype in (mime for content, mime in my_email.alternatives),
                'Email does not contain "%s" alternative.' % mimetype
            )

    def assertEmailAlternativeBodyContains(self, value, email=None):
        for my_email in self.get_email_list(email):
            self.assert_(
                all(
                    value in content for content, mime in my_email.alternatives
                ),
                'Email does not contain "%s" in alternative body.' % value
            )


class UserTestCase(TestCase):
    def setUp(self):
        super(UserTestCase, self).setUp()

        self.password = 'johnpassword'
        self.user = User.objects.create_user(
            'john', 'lennon@thebeatles.com', self.password)

        # Make sure the user has been created
        self.assertIn(self.user, User.objects.all())

        # Login the newly created user
        result = self.client.login(
            username=self.user.username, password=self.password
        )

        # Make sure the login went well
        self.assertTrue(result)

    def tearDown(self):
        self.client.logout()
        self.user.delete()


class ComparingTestCase(TestCase):
    def assertLessThan(self, value1, value2):
        self.assert_(value1 < value2)

    def assertMoreThan(self, value1, value2):
        self.assert_(value1 > value2)

    def assertBetween(self, value, min, max):
        self.assert_(value >= min)
        self.assert_(value <= max)

    def assertWithin(self, value, min, max):
        self.assert_(value > min)
        self.assert_(value < max)


def template_exists(template_name):
    try:
        loader.get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False
