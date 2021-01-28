from contextlib import contextmanager
import logging
logger = logging.getLogger(__name__)

import smtplib

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend

from django.test import TestCase


from django.template import loader, TemplateDoesNotExist

from django_webtest import WebTest


class AssertLogsMixin:
    """Mixin to enable assertLogs method in Python 2.7.

        patch_logger has similar functionality for Python 2.7, but is
        removed in Django 3.0. This mixin reworks patch_logger so that
        the assertLogs method can be used for any supported Django
        version.
    """
    # TODO: Remove use of mixin when Django 1.11 support dropped
    def assertLogs(self, logger=None, level=None):
        # Use assertLogs context manager if present
        try:
            from unittest.case import _AssertLogsContext

            return _AssertLogsContext(self, logger, level)
        except ImportError:
            # Fallback if Django version does not support assertLogs
            import logging
            from django.test.utils import patch_logger

            class PatchLoggerResponse:
                """Object to mimic AssertLogsContext response."""
                def __init__(self, messages):
                    self.output = messages

            @contextmanager
            def patch_logger(logger_name, log_level, log_kwargs=False):
                """Replicating patch_logger functionality from Django 1.11.

                    Cannot use original Django patch_logger because of how
                    it returns its response. Have copied and modified it
                    to return an object that mimics the assertLogs response.
                """
                logger_response = PatchLoggerResponse([])

                def replacement(msg, *args, **kwargs):
                    call = msg % args
                    logger_response.output.append((call, kwargs) if log_kwargs else call)

                logger = logging.getLogger(logger_name)
                orig = getattr(logger, log_level)
                setattr(logger, log_level, replacement)

                try:
                    yield logger_response
                finally:
                    setattr(logger, log_level, orig)

                    if len(logger_response.output) == 0:
                        raise self.failureException(
                            "no logs of level {} or higher triggered on {}".format(
                                log_level, logger_name
                            )
                        )

            return patch_logger(logger, level.lower())

class WebTestCase(WebTest):
    def setUp(self):
        self.site = Site.objects.get_current()

        super().setUp()

    def assertInContext(self, response, variable,
                        instance_of=None, value=None):
        try:
            instance = response.context[variable]
            self.assertTrue(instance)
        except KeyError:
            self.fail(
                'Asserted variable %s not in response context.' % variable
            )

        if instance_of:
            self.assertTrue(isinstance(instance, instance_of))

        if value:
            self.assertEqual(instance, value)


class MailTestCase(AssertLogsMixin, TestCase):
    def get_email_list(self, email):
        if email:
            return (email,)
        else:
            return mail.outbox

    def assertEmailContains(self, value, email=None):
        for my_email in self.get_email_list(email):
            self.assertTrue(
                (value in my_email.subject) or
                (value in my_email.body),
                'Email does not contain "%s".' % value
            )

    def assertEmailBodyContains(self, value, email=None):
        for my_email in self.get_email_list(email):
            self.assertTrue(
                value in my_email.body,
                'Email body does not contain "%s".' % value
            )

    def assertEmailSubjectContains(self, value, email=None):
        for my_email in self.get_email_list(email):
            self.assertTrue(
                value in my_email.subject,
                'Email subject does not contain "%s".' % value
            )

    def assertEmailHasNoAlternatives(self, email=None):
        for my_email in self.get_email_list(email):
            self.assertTrue(
                not getattr(my_email, 'alternatives', None),
                'Email has alternative content types.'
            )

    def assertEmailAlternativesContainMimetype(self, mimetype, email=None):
        for my_email in self.get_email_list(email):
            self.assertTrue(
                mimetype in (mime for content, mime in my_email.alternatives),
                'Email does not contain "%s" alternative.' % mimetype
            )

    def assertEmailAlternativeBodyContains(self, value, email=None):
        for my_email in self.get_email_list(email):
            self.assertTrue(
                all(
                    value in content for content, mime in my_email.alternatives
                ),
                'Email does not contain "%s" in alternative body.' % value
            )

    def assertEmailHasHeader(self, header, content=None, email=None):
        for my_email in self.get_email_list(email):
            self.assertTrue(
                header in my_email.extra_headers,
                'Email does not have the "%s" header.' % header
            )
            if content is not None:
                self.assertEqual(my_email.extra_headers[header], content)


class UserTestCase(AssertLogsMixin, TestCase):
    def setUp(self):
        super().setUp()

        User = get_user_model()
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


class ComparingTestCase(AssertLogsMixin, TestCase):
    def assertLessThan(self, value1, value2):
        self.assertTrue(value1 < value2)

    def assertMoreThan(self, value1, value2):
        self.assertTrue(value1 > value2)

    def assertBetween(self, value, min, max):
        self.assertTrue(value >= min)
        self.assertTrue(value <= max)

    def assertWithin(self, value, min, max):
        self.assertTrue(value > min)
        self.assertTrue(value < max)


def template_exists(template_name):
    try:
        loader.get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False


class FailingEmailBackend(BaseEmailBackend):
    """ Email backend that just fails, for testing purposes. """

    def send_messages(self, email_messages):
        raise smtplib.SMTPException('Connection refused')
