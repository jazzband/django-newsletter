from datetime import datetime, timedelta

from django.core import mail

from newsletter.models import *
from newsletter.forms import *

from utils import *


class MailingTestCase(MailTestCase):

    fixtures = ['default_templates']

    def setUp(self):
        self.n = Newsletter(title='Test newsletter',
                            slug='test-newsletter',
                            sender='Test Sender',
                            email='test@testsender.com')
        self.n.save()
        self.n.site = get_default_sites()

        self.m = Message(title='Test message',
                         newsletter=self.n)
        self.m.save()

        self.s = Subscription(
            name='Test Name', email='test@test.com',
            newsletter=self.n, subscribed=True
        )
        self.s.save()


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
        self.assertEqual(self.s.get_recipient(), 'Test Name <test@test.com>')

    def test_submission_from_message(self):
        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [self.s])

        self.assertFalse(sub.prepared)
        self.assertFalse(sub.sent)
        self.assertFalse(sub.sending)

    def test_submission_unsubscribed(self):
        self.s.subscribed = False
        self.s.save()

        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [])

    def test_submission_unsubscribed(self):
        self.s.unsubscribed = True
        self.s.save()

        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [])

    def test_submission_unsubscribed_unsubscribed(self):
        self.s.subscribed = False
        self.s.unsubscribed = True
        self.s.save()

        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [])

    def test_twosubmissions(self):
        s2 = Subscription(
            name='Test Name 2', email='test2@test.com',
            newsletter=self.n, subscribed=True
        )
        s2.save()

        sub = Submission.from_message(self.m)

        subscriptions = sub.subscriptions.all()
        self.assert_(self.s in list(subscriptions))
        self.assert_(s2 in list(subscriptions))

    def test_twosubmissions(self):
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
        self.sub.publish_date = datetime.now() - timedelta(seconds=1)
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
