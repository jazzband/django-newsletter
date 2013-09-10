import itertools

from datetime import timedelta

from django.core import mail

from django.utils import unittest
from django.utils.timezone import now

from ..models import (
    Newsletter, Subscription, Submission, Message, Article, get_default_sites
)
from ..utils import ACTIONS

from .utils import MailTestCase, UserTestCase, template_exists


class MailingTestCase(MailTestCase):

    def get_newsletter_kwargs(self):
        """ Returns the keyword arguments for instanciating the newsletter. """

        return {
            'title': 'Test newsletter',
            'slug': 'test-newsletter',
            'sender': 'Test Sender',
            'email': 'test@testsender.com'
        }

    def setUp(self):
        self.n = Newsletter(**self.get_newsletter_kwargs())
        self.n.save()
        self.n.site = get_default_sites()

        self.m = Message(title='Test message',
                         newsletter=self.n,
                         slug='test-message')
        self.m.save()

        self.s = Subscription(
            name='Test Name', email='test@test.com',
            newsletter=self.n, subscribed=True
        )
        self.s.save()

    def send_email(self, action):
        assert action in ACTIONS + ('message', ), 'Unknown action: %s' % action

        if action == 'message':
            # Create submission
            sub = Submission.from_message(self.m)
            sub.prepared = True
            sub.publish_date = now() - timedelta(seconds=1)
            sub.save()

            # Send message email
            Submission.submit_queue()
        else:
            self.s.send_activation_email(action)


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
        for current in xrange(total):
            a = self.make_article()
            if last:
                self.assert_(a.sortorder > last)
            last = a.sortorder


class CreateSubmissionTestCase(MailingTestCase):
    def test_subscription(self):
        """ Test whether the recipient corresponds for Subscription. """

        self.assertEqual(self.s.get_recipient(), 'Test Name <test@test.com>')

    def test_submission_from_message(self):
        """ Test creating a submission from a message. """

        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [self.s])

        self.assertFalse(sub.prepared)
        self.assertFalse(sub.sent)
        self.assertFalse(sub.sending)

    def test_submission_subscribed(self):
        """ Test a simpel submission with single subscriber. """

        self.s.subscribed = False
        self.s.save()

        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [])

    def test_submission_unsubscribed(self):
        """ Test submission with unsubscribed activated subscriber. """

        self.s.unsubscribed = True
        self.s.save()

        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [])

    def test_submission_unsubscribed_unactivated(self):
        """ Test submissions with unsubscribed unactivated subscriber. """

        self.s.subscribed = False
        self.s.unsubscribed = True
        self.s.save()

        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [])

    def test_twosubmissions(self):
        """ Test submission with two activated subscribers. """

        s2 = Subscription(
            name='Test Name 2', email='test2@test.com',
            newsletter=self.n, subscribed=True
        )
        s2.save()

        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assert_(self.s in list(subscriptions))
        self.assert_(s2 in list(subscriptions))

    def test_twosubmissions_unsubscried(self):
        """ Test submission with two subscribers, one unactivated. """

        s2 = Subscription(
            name='Test Name 2', email='test2@test.com',
            newsletter=self.n, subscribed=False
        )
        s2.save()

        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [self.s])


class SubmitSubmissionTestCase(MailingTestCase):
    def setUp(self):
        super(SubmitSubmissionTestCase, self).setUp()

        self.sub = Submission.from_message(self.m)
        self.sub.save()

    def test_submission(self):
        """ Assure initial Submission is in expected state. """

        self.assertFalse(self.sub.prepared)
        self.assertFalse(self.sub.sent)
        self.assertFalse(self.sub.sending)

    def test_nosubmit(self):
        """ Assure nothing happends if not prepared. """

        # Assure nothing happends
        Submission.submit_queue()

        self.assertFalse(self.sub.prepared)
        self.assertFalse(self.sub.sent)
        self.assertFalse(self.sub.sending)

    def test_submitsubmission(self):
        """ Test queue-based submission. """

        self.sub.prepared = True
        self.sub.publish_date = now() - timedelta(seconds=1)
        self.sub.save()

        Submission.submit_queue()

        # Get the object fresh from DB, as to assure no caching takes place
        submission = Submission.objects.get(pk=self.sub.pk)

        self.assert_(submission.sent)
        self.assertFalse(submission.sending)

        # Make sure mail is being sent out
        self.assertEquals(len(mail.outbox), 1)

        # Make sure a submission contains the title and unsubscribe URL
        self.assertEmailContains(submission.message.title)
        self.assertEmailContains(submission.newsletter.unsubscribe_url())


class SubscriptionTestCase(UserTestCase, MailingTestCase):
    def setUp(self):
        super(SubscriptionTestCase, self).setUp()

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
            for x in xrange(2):
                s.subscribed = True
                s.save()

                self.assert_(s.subscribed)
                self.assert_(s.subscribe_date)
                self.assertFalse(s.unsubscribed)
                old_subscribe_date = s.subscribe_date

                s.unsubscribed = True
                s.save()

                self.assertFalse(s.subscribed)
                self.assert_(s.unsubscribed)
                self.assert_(s.unsubscribe_date)

                s.unsubscribed = False
                s.save()

                self.assertFalse(s.unsubscribed)
                self.assert_(s.subscribed)
                self.assertNotEqual(s.subscribe_date, old_subscribe_date)


class AllEmailsTestsMixin(object):
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

        kwargs = super(HtmlEmailsTestCase, self).get_newsletter_kwargs()
        kwargs.update(send_html=True)

        return kwargs

    def assertSentEmailIsProper(self, action):
        """
        Assert that there's exactly one email in outbox
        and that it contains alternative with mimetype text/html.
        """

        # Make sure one mail is being sent out
        self.assertEquals(len(mail.outbox), 1)

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

        kwargs = super(TextOnlyEmailsTestCase, self).get_newsletter_kwargs()
        kwargs.update(send_html=False)

        return kwargs

    def assertSentEmailIsProper(self, action):
        """
        Assert that there's exactly one email in outbox
        and that it has no alternative content types.
        """

        # Make sure one mail is being sent out
        self.assertEquals(len(mail.outbox), 1)

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
        Update keyword arguments for instanciating the newsletter
        so that slug corresponds to one for which template overrides exists
        and make sure e-mails will be sent with text and HTML versions.
        """

        kwargs = super(TemplateOverridesTestCase, self).get_newsletter_kwargs()
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
        self.assertEquals(len(mail.outbox), 1)

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
