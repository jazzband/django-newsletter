import itertools
import os

from unittest import mock
import unittest

from datetime import timedelta

from django.contrib.sites.models import Site
from django.core import mail
from django.core.exceptions import ValidationError

from django.utils.timezone import now

from newsletter.models import (
    Newsletter, Subscription, Submission, Message, Article, get_default_sites, Attachment
)
from newsletter.utils import ACTIONS

from .utils import MailTestCase, UserTestCase, template_exists

NUM_SUBSCRIBED = 2


class MailingTestCase(MailTestCase):

    def get_newsletter_kwargs(self):
        """ Returns the keyword arguments for instanciating the newsletter. """

        return {
            'title': 'Test newsletter',
            'slug': 'test-newsletter',
            'sender': 'Test Sender',
            'email': 'test@testsender.com'
        }
    
    def get_newsletter_sites(self):
        return get_default_sites()
    
    def get_site(self) -> Site:
        return Site.objects.get_current()

    def setUp(self):
        self.n = Newsletter(**self.get_newsletter_kwargs())
        self.n.save()
        self.n.site.set(self.get_newsletter_sites())

        self.m = Message(title='Test message',
                         newsletter=self.n,
                         slug='test-message')
        self.m.save()

        self.a = Attachment.objects.create(
            file=os.path.join('tests', 'files', 'sample.pdf'),
            message=self.m
        )

        self.s = Subscription.objects.create(
            name='Test Name', email='test@test.com',
            newsletter=self.n, subscribed=True
        )
        self.s2 = Subscription.objects.create(
            name='René Luçon', email='rene@test.com',
            newsletter=self.n, subscribed=True
        )

    def send_email(self, action):
        assert action in ACTIONS + ('message', ), 'Unknown action: %s' % action

        if action == 'message':
            # Create submission
            sub = Submission.from_message(self.m, Site.objects.get_current())
            sub.prepared = True
            sub.publish_date = now() - timedelta(seconds=1)
            sub.save()

            # Send message email
            Submission.submit_queue()
        else:
            for subscriber in self.n.get_subscriptions():
                subscriber.send_activation_email(Site.objects.get_current(), action)


class ArticleTestCase(MailingTestCase):
    def make_article(self):
        a = Article()
        a.title = 'Test title'
        a.text = 'This should be a very long text with <html> in it as well.'
        a.post = self.m
        a.save()

        return a

    def update(self, article):
        return Article.objects.get(pk=article.pk)

    def test_article(self):
        self.make_article()

    def test_sortorder_defaults(self):
        total = 3

        last = 0
        for current in range(total):
            a = self.make_article()
            if last:
                self.assertTrue(a.sortorder > last)
            last = a.sortorder


class MessageTestCase(MailingTestCase):
    def test_message_str(self):
        m1 = Message(title='Test message', slug='test-message')
        self.assertEqual(str(m1), "Test message in Test newsletter")

        m2 = Message.objects.create(
            title='Test message str',
            newsletter=self.n,
            slug='test-message-str'
        )

        self.assertEqual(
            str(m2), "Test message str in Test newsletter"
        )


class CreateSubmissionTestCase(MailingTestCase):
    def test_subscription(self):
        """ Test whether the recipient corresponds for Subscription. """

        self.assertEqual(self.s.get_recipient(), 'Test Name <test@test.com>')

    def test_submission_from_message(self):
        """ Test creating a submission from a message. """

        sub = Submission.from_message(self.m, self.get_site())

        subscriptions = sub.subscriptions.all()
        self.assertEqual(set(subscriptions), {self.s, self.s2})

        self.assertFalse(sub.prepared)
        self.assertFalse(sub.sent)
        self.assertFalse(sub.sending)

    def test_submission_subscribed(self):
        """ Test a simple submission with single subscriber. """

        self.s.subscribed = False
        self.s.save()

        sub = Submission.from_message(self.m, self.get_site())

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [self.s2])

    def test_submission_unsubscribed(self):
        """ Test submission with unsubscribed activated subscriber. """

        self.s.unsubscribed = True
        self.s.save()

        sub = Submission.from_message(self.m, self.get_site())

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [self.s2])

    def test_submission_unsubscribed_unactivated(self):
        """ Test submissions with unsubscribed unactivated subscriber. """

        self.s.subscribed = False
        self.s.unsubscribed = True
        self.s.save()

        sub = Submission.from_message(self.m, self.get_site())

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [self.s2])


class CreateSubmissionMultiSitesTestCase(CreateSubmissionTestCase):
    sites = "somerandom.com anotherrandom.net somethingelse.org anotheronegood.dev 1somethingelse.org " \
            "2anotheronegood.dev 32anotheronegood3.dev".split()

    def add_site(self, domain: str) -> Site:
        site = Site()
        site.domain = domain
        site.name = "Test " + domain
        site.save()
        return site

    def setUp(self):
        for domain in self.sites:
            self.add_site(domain)

        super().setUp()

    def get_newsletter_sites(self):
        domains = self.sites[1:-2]
        return Site.objects.filter(domain__in=domains)

    def get_site(self) -> Site:
        return Site.objects.get(domain=self.sites[2])

    def test_setup(self):
        count_sites = Site.objects.all().count()
        # example.com is created by default
        self.assertEqual(len(self.sites) + 1, count_sites)
        self.assertGreater(len(self.get_newsletter_sites()), 2)
        self.assertEqual(len(self.get_newsletter_sites()), len(self.n.site.all()))

    def test_submission_site_validation(self):
        """ Test creating a submission from a message with site provided. """

        callback = lambda: Submission.from_message(self.m, Site.objects.get(domain=self.sites[0]))
        self.assertRaises(ValidationError, callback)


class SubmitSubmissionTestCase(MailingTestCase):
    def setUp(self):
        super().setUp()

        self.sub = Submission.from_message(self.m, self.get_site())
        self.sub.save()

    def test_submission(self):
        """ Assure initial Submission is in expected state. """

        self.assertFalse(self.sub.prepared)
        self.assertFalse(self.sub.sent)
        self.assertFalse(self.sub.sending)

    def test_nosubmit(self):
        """ Assure nothing happens if not prepared. """

        # Assure nothing happens
        Submission.submit_queue()

        self.assertFalse(self.sub.prepared)
        self.assertFalse(self.sub.sent)
        self.assertFalse(self.sub.sending)

    def test_submitsubmission(self):
        """ Test queue-based submission. """

        # Adding a subscription after the submission has been created, it
        # should not be used when submitting self.sub
        Subscription.objects.create(
            name='Other Name', email='other@test.com',
            newsletter=self.n, subscribed=True
        )

        self.sub.prepared = True
        self.sub.publish_date = now() - timedelta(seconds=1)
        self.sub.save()

        Submission.submit_queue()

        # Get the object fresh from DB, as to assure no caching takes place
        submission = Submission.objects.get(pk=self.sub.pk)

        self.assertTrue(submission.sent)
        self.assertFalse(submission.sending)

        # Make sure mail is being sent out
        self.assertEqual(len(mail.outbox), NUM_SUBSCRIBED)

        # Make sure a submission contains the title and unsubscribe URL
        self.assertEmailContains(submission.message.title)
        self.assertEmailContains(submission.newsletter.unsubscribe_url())
        self.assertEmailHasHeader(
            'List-Unsubscribe',
            'http://example.com/newsletter/test-newsletter/unsubscribe/'
        )

    def test_delayedsumbmission(self):
        """ Test delays between emails """

        self.sub.prepared = True
        self.sub.publish_date = now() - timedelta(seconds=1)
        self.sub.save()

        with self.settings(NEWSLETTER_EMAIL_DELAY=0.01):
            with mock.patch('time.sleep', return_value=None) as sleep_mock:
                Submission.submit_queue()

        sleep_mock.assert_called_with(0.01)

    def test_delayedbatchsumbmission(self):
        """ Test delays between emails """

        self.sub.prepared = True
        self.sub.publish_date = now() - timedelta(seconds=1)
        self.sub.save()

        with self.settings(
            NEWSLETTER_BATCH_SIZE=1,
            NEWSLETTER_BATCH_DELAY=0.02
        ):
            with mock.patch('time.sleep', return_value=None) as sleep_mock:
                Submission.submit_queue()

        sleep_mock.assert_called_with(0.02)

    def test_management_command(self):
        """ Test submission through management command. """

        from django.core.management import call_command

        with mock.patch.object(
            Submission, 'submit_queue', return_value=None
        ) as mock_submit:
            call_command('submit_newsletter')
            mock_submit.assert_called_once()


class SubscriptionTestCase(UserTestCase, MailingTestCase):
    def setUp(self):
        super().setUp()

        self.us = Subscription(user=self.user, newsletter=self.n)
        self.us.save()

        self.ns = Subscription(
            name='Test susbcriber', newsletter=self.n,
            email='test@test.com'
        )
        self.ns.save()

        self.ss = [self.us, self.ns]

    def test_usersubscription(self):
        self.assertEqual(self.us.name, self.user.get_full_name())
        self.assertEqual(self.us.email, self.user.email)

    def test_subscribe_unsubscribe(self):
        for s in self.ss:
            self.assertFalse(s.subscribed)
            self.assertFalse(s.unsubscribed)
            self.assertFalse(s.subscribe_date)
            self.assertFalse(s.unsubscribe_date)

            # Repeat this to ensure consequencentness
            for x in range(2):
                s.subscribed = True
                s.save()

                self.assertTrue(s.subscribed)
                self.assertTrue(s.subscribe_date)
                self.assertFalse(s.unsubscribed)
                old_subscribe_date = s.subscribe_date

                s.unsubscribed = True
                s.save()

                self.assertFalse(s.subscribed)
                self.assertTrue(s.unsubscribed)
                self.assertTrue(s.unsubscribe_date)

                s.unsubscribed = False
                s.save()

                self.assertFalse(s.unsubscribed)
                self.assertTrue(s.subscribed)
                self.assertNotEqual(s.subscribe_date, old_subscribe_date)


class AllEmailsTestsMixin:
    """ Mixin for testing properties of sent e-mails for all message types. """

    def assertSentEmailIsProper(self, action):
        """
        This method should be overridden in subclasses.
        Assertions identical for all message types should be in this method.
        """

        raise NotImplementedError(
            '%(class_name)s inherits from of AllEmailsTestsMixin '
            'and should define assertSentEmailIsProper method.' % {
                'class_name': self.__class__.__name__
            }
        )

    def test_subscription_email(self):
        """ Assure subscription email is proper. """

        self.send_email('subscribe')

        self.assertSentEmailIsProper('subscribe')

    def test_unsubscription_email(self):
        """ Assure unsubscription email is proper. """

        self.send_email('unsubscribe')

        self.assertSentEmailIsProper('unsubscribe')

    def test_update_email(self):
        """ Assure update email is proper. """

        self.send_email('update')

        self.assertSentEmailIsProper('update')

    def test_message_email(self):
        """ Assure message email is proper. """

        self.send_email('message')

        self.assertSentEmailIsProper('message')


class HtmlEmailsTestCase(MailingTestCase, AllEmailsTestsMixin):
    """
    TestCase for testing whether e-mails sent for newsletter
    with send_html=True have HTML alternatives.
    """

    def get_newsletter_kwargs(self):
        """
        Update keyword arguments for instanciating the newsletter
        with send_html = True.
        """

        kwargs = super().get_newsletter_kwargs()
        kwargs.update(send_html=True)

        return kwargs

    def assertSentEmailIsProper(self, action):
        """
        Assert that there's exactly one email in outbox
        and that it contains alternative with mimetype text/html.
        """

        # Make sure one mail is being sent out
        self.assertEqual(len(mail.outbox), NUM_SUBSCRIBED)

        # Make sure mail contains HTML alternative
        self.assertEmailAlternativesContainMimetype('text/html')


class TextOnlyEmailsTestCase(MailingTestCase, AllEmailsTestsMixin):
    """
    TestCase for testing whether e-mails sent for newsletter
    with send_html=False are text only.
    """

    def get_newsletter_kwargs(self):
        """
        Update keyword arguments for instanciating the newsletter
        with send_html = False.
        """

        kwargs = super().get_newsletter_kwargs()
        kwargs.update(send_html=False)

        return kwargs

    def assertSentEmailIsProper(self, action):
        """
        Assert that there's exactly one email in outbox
        and that it has no alternative content types.
        """

        # Make sure one mail is being sent out
        self.assertEqual(len(mail.outbox), NUM_SUBSCRIBED)

        # Make sure mail is text only
        self.assertEmailHasNoAlternatives()


template_overrides = (
    'newsletter/message/test-newsletter-with-overrides/' + action + suff
    for action, suff in itertools.product(
        ('subscribe', 'update', 'unsubscribe', 'message'),
        ('_subject.txt', '.txt', '.html')
    )
)


# When tests are run outside test project
# test templates overrides will not exist,
# so skip their testing.
@unittest.skipUnless(
    all(
        template_exists(template_name) for template_name in template_overrides
    ),
    'Test templates overrides not found.'
)
class TemplateOverridesTestCase(MailingTestCase, AllEmailsTestsMixin):
    """
    TestCase for testing template overrides for specific newsletters.
    """

    def get_newsletter_kwargs(self):
        """
        Update keyword arguments for instantiating the newsletter
        so that slug corresponds to one for which template overrides exists
        and make sure e-mails will be sent with text and HTML versions.
        """

        kwargs = super().get_newsletter_kwargs()
        kwargs.update(slug='test-newsletter-with-overrides',
                      send_html=True)

        return kwargs

    def assertSentEmailIsProper(self, action):
        """
        Assert that there's exactly one email in outbox
        and that it contains proper strings from template overrides
        in subject and body.
        """

        # Make sure one mail is being sent out
        self.assertEqual(len(mail.outbox), NUM_SUBSCRIBED)

        # Make sure mail subject contains string
        # from template override for given action
        self.assertEmailSubjectContains(
            'override for %s_subject.txt' % action
        )

        # Make sure body of mail text version contains string
        # from text template override for given action
        self.assertEmailBodyContains('override for %s.txt' % action)

        # Make sure body of mail HTML version contains string
        # from HTML template override for given action
        self.assertEmailAlternativeBodyContains(
            'override for %s.html' % action
        )
