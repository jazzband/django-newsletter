# Python 2.5 compatibility
# Get the with statement from the future
from __future__ import with_statement

from datetime import datetime, timedelta

import time

# Conditioally import pytz
try:
    import pytz
except ImportError:
    pytz = None

from django import VERSION as DJANGO_VERSION

from django.core import mail
from django.core.urlresolvers import reverse

from django.utils import unittest, timezone

from django.test.utils import override_settings

from ..models import (
    Newsletter, Subscription, Submission, Message, get_default_sites
)

from ..forms import UpdateForm

from ..utils import get_user_model
User = get_user_model()

from .utils import MailTestCase, UserTestCase, WebTestCase, ComparingTestCase


# Amount of seconds to wait to test time comparisons in submissions.
WAIT_TIME = 1


class NewsletterListTestCase(WebTestCase):
    """ Base class for newsletter test cases. """

    fixtures = ['test_newsletters']

    def setUp(self):
        self.newsletters = Newsletter.objects.all()

        self.list_url = reverse('newsletter_list')


class AnonymousNewsletterListTestCase(NewsletterListTestCase):
    """ Test case for anonymous views of newsletter. """

    def test_emptylist(self):
        """ No newsletters should yield an emtpy list. """

        # Delete existing newsletters
        Newsletter.objects.all().delete()

        # Assert a 404 is returned
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 404)

    def test_list(self):
        """
        Test whether all newsletters are in the list and whether the links
        to them are correct.
        """
        response = self.client.get(self.list_url)

        for n in self.newsletters.filter(visible=True):
            self.assertContains(response, n.title)

            detail_url = reverse('newsletter_detail',
                                 kwargs={'newsletter_slug': n.slug})
            self.assertContains(response, '<a href="%s">' % detail_url)

        for n in self.newsletters.filter(visible=False):
            self.assertNotContains(response, n.title)

    def test_detail(self):
        for n in self.newsletters:

            detail_url = reverse(
                'newsletter_detail',
                kwargs={'newsletter_slug': n.slug}
            )

            subscribe_url = reverse(
                'newsletter_subscribe_request',
                kwargs={'newsletter_slug': n.slug}
            )

            unsubscribe_url = reverse(
                'newsletter_unsubscribe_request',
                kwargs={'newsletter_slug': n.slug}
            )

            update_url = reverse(
                'newsletter_update_request',
                kwargs={'newsletter_slug': n.slug}
            )

            archive_url = reverse(
                'newsletter_archive',
                kwargs={'newsletter_slug': n.slug}
            )

            # Check returned URL's exist and equal result of lookup methods
            self.assertTrue(subscribe_url)
            self.assertEquals(subscribe_url, n.subscribe_url())

            self.assertTrue(unsubscribe_url)
            self.assertEquals(unsubscribe_url, n.unsubscribe_url())

            self.assertTrue(update_url)
            self.assertEquals(update_url, n.update_url())

            self.assertTrue(archive_url)
            self.assertEquals(archive_url, n.archive_url())

            # Request detail URL and assert it links to all other URL's
            response = self.client.get(detail_url)

            if not n.visible:
                self.assertEqual(response.status_code, 404)
                continue

            self.assertContains(response, subscribe_url)
            self.assertContains(response, update_url)
            self.assertContains(response, unsubscribe_url)
            self.assertContains(response, archive_url)

            # Request each particular newsletter URL and assert
            # it returns a 200
            response = self.client.get(subscribe_url)
            self.assertContains(response, n.title, status_code=200)

            response = self.client.get(unsubscribe_url)
            self.assertContains(response, n.title, status_code=200)

            response = self.client.get(update_url)
            self.assertContains(response, n.title, status_code=200)

            response = self.client.get(archive_url)
            self.assertContains(response, n.title, status_code=200)

    def test_detail_invisible_not_found(self):
        """
        Test whether an invisible newsletter causes a 404 in detail view.
        """

        # Get an invisible newsletter
        n = Newsletter.objects.filter(visible=False)[0]

        detail_url = reverse(
            'newsletter_detail',
            kwargs={'newsletter_slug': n.slug}
        )

        response = self.client.get(detail_url)

        self.assertEquals(response.status_code, 404)


class UserNewsletterListTestCase(UserTestCase,
                                 NewsletterListTestCase):

    def get_user_subscription(self, newsletter):
        subscriptions = Subscription.objects.filter(newsletter=newsletter,
                                                    user=self.user)
        self.assertEqual(subscriptions.count(), 1)

        subscription = subscriptions[0]
        self.assert_(subscription.create_date)

        return subscriptions[0]

    def test_listform(self):
        """ Test whether form elements are present in list. """

        response = self.client.get(self.list_url)

        formset = response.context['formset']
        total_forms = len(formset.forms)

        self.assertEqual(
            total_forms, len(self.newsletters.filter(visible=True))
        )

        if DJANGO_VERSION[:2] == (1, 4):
            # Django 1.4
            self.assertContains(
                response,
                '<input type="hidden" name="form-TOTAL_FORMS" value="%d" '
                'id="id_form-TOTAL_FORMS" />' % total_forms
            )

            self.assertContains(
                response,
                '<input type="hidden" name="form-INITIAL_FORMS" value="%d" '
                'id="id_form-INITIAL_FORMS" />' % total_forms
            )

        else:
            # Django 1.5
            self.assertContains(
                response,
                '<input id="id_form-TOTAL_FORMS" name="form-TOTAL_FORMS" '
                'type="hidden" value="%d" />' % total_forms
            )

            self.assertContains(
                response,
                '<input id="id_form-INITIAL_FORMS" name="form-INITIAL_FORMS" '
                'type="hidden" value="%d" />' % total_forms
            )

        for form in formset.forms:
            self.assert_(
                form.instance.newsletter in self.newsletters,
                "%s not in %s" % (form.instance.newsletter, self.newsletters)
            )
            self.assertContains(response, form['id'])
            self.assertContains(response, form['subscribed'])

    def test_update(self):
        """ Attempt to subscribe a user to newsletters. """

        # Make sure no subscriptions exist on beforehand
        Subscription.objects.all().delete()

        # Construct management form data
        total_forms = self.newsletters.filter(visible=True).count()

        params = {
            'form-TOTAL_FORMS': total_forms,
            'form-INITIAL_FORMS': total_forms
        }

        # Add subscribe to all newsletters
        count = 0
        for n in self.newsletters.filter(visible=True):
            params.update({
                'form-%d-id' % count: n.id,
                'form-%d-subscribed' % count: '1'
            })

            count += 1

        # Post the form
        response = self.client.post(self.list_url, params)

        # Make sure the result is a success
        self.assertEquals(response.status_code, 200)

        subscriptions = Subscription.objects.filter(
            user=self.user
        )

        # Assert all newsletters have related subscriptions now
        self.assertTrue(subscriptions.count())
        self.assertEquals(
            subscriptions.count(),
            self.newsletters.filter(visible=True).count()
        )

    def test_invalid_update(self):
        """ Test an invalid update, which should fail. """
        # Make sure no subscriptions exist on beforehand
        Subscription.objects.all().delete()

        # TODO: Use a Mock to assert a warning has been logged
        # Ref: http://www.michaelpollmeier.com/python-mock-how-to-assert-a-substring-of-logger-output/

        # A post without any form elements should fail, horribly
        self.client.post(self.list_url)

        # A post with correct management data with weird values
        # should cause the formset not to validate.

        # Construct management form data
        total_forms = self.newsletters.filter(visible=True).count()

        params = {
            'form-TOTAL_FORMS': total_forms,
            'form-INITIAL_FORMS': total_forms
        }

        # Add subscribe to all newsletters
        count = 0
        for n in self.newsletters.filter(visible=True):
            params.update({
                # Use a wrong value here
                'form-%d-id' % count: 1000,
                'form-%d-subscribed' % count: '1'
            })

            count += 1

        # Post the form
        self.client.post(self.list_url, params)

        # Assert no subscriptions have been created
        self.assertFalse(
            Subscription.objects.filter(subscribed=True).exists())


class SubscribeTestCase(WebTestCase, MailTestCase):

    def setUp(self):
        self.n = Newsletter(title='Test newsletter',
                            slug='test-newsletter',
                            sender='Test Sender',
                            email='test@testsender.com')
        self.n.save()
        self.n.site = get_default_sites()

        self.subscribe_url = \
            reverse('newsletter_subscribe_request',
                    kwargs={'newsletter_slug': self.n.slug})
        self.subscribe_confirm_url = \
            reverse('newsletter_subscribe_confirm',
                    kwargs={'newsletter_slug': self.n.slug})
        self.subscribe_email_sent_url = \
            reverse('newsletter_activation_email_sent',
                    kwargs={'newsletter_slug': self.n.slug,
                            'action': 'subscribe'})
        self.subscribe_activated_url = \
            reverse('newsletter_action_activated',
                    kwargs={'newsletter_slug': self.n.slug,
                            'action': 'subscribe'})

        self.update_url = \
            reverse('newsletter_update_request',
                    kwargs={'newsletter_slug': self.n.slug})
        self.update_email_sent_url = \
            reverse('newsletter_activation_email_sent',
                    kwargs={'newsletter_slug': self.n.slug,
                            'action': 'update'})
        self.update_activated_url = \
            reverse('newsletter_action_activated',
                    kwargs={'newsletter_slug': self.n.slug,
                            'action': 'update'})

        self.unsubscribe_url = \
            reverse('newsletter_unsubscribe_request',
                    kwargs={'newsletter_slug': self.n.slug})
        self.unsubscribe_confirm_url = \
            reverse('newsletter_unsubscribe_confirm',
                    kwargs={'newsletter_slug': self.n.slug})
        self.unsubscribe_email_sent_url = \
            reverse('newsletter_activation_email_sent',
                    kwargs={'newsletter_slug': self.n.slug,
                            'action': 'unsubscribe'})
        self.unsubscribe_activated_url = \
            reverse('newsletter_action_activated',
                    kwargs={'newsletter_slug': self.n.slug,
                            'action': 'unsubscribe'})

        super(SubscribeTestCase, self).setUp()

    def test_urls(self):
        # TODO: is performing this test in each subclass
        #     of WebSubscribeTestCase really needed?
        self.assert_(self.subscribe_url)
        self.assert_(self.update_url)
        self.assert_(self.unsubscribe_url)
        self.assert_(self.subscribe_confirm_url)
        self.assert_(self.unsubscribe_confirm_url)
        self.assert_(self.subscribe_email_sent_url)
        self.assert_(self.update_email_sent_url)
        self.assert_(self.unsubscribe_email_sent_url)
        self.assert_(self.subscribe_activated_url)
        self.assert_(self.update_activated_url)
        self.assert_(self.unsubscribe_activated_url)


class UserSubscribeTestCase(
    SubscribeTestCase,
    UserTestCase,
    ComparingTestCase
):
    """ Test case for user subscription and unsubscription."""

    def get_user_subscription(self):
        subscriptions = Subscription.objects.filter(newsletter=self.n,
                                                    user=self.user)
        self.assertEqual(subscriptions.count(), 1)

        subscription = subscriptions[0]
        self.assert_(subscription.create_date)

        return subscriptions[0]

    def test_subscribe_view(self):
        """ Test the subscription form. """
        response = self.client.get(self.subscribe_url)

        self.assertContains(response, self.n.title, status_code=200)

        self.assertEqual(response.context['newsletter'], self.n)
        self.assertEqual(response.context['user'], self.user)

        self.assertContains(
            response,
            'action="%s"' % self.subscribe_confirm_url
        )
        self.assertContains(response, 'id="id_submit"')

        subscription = self.get_user_subscription()
        self.assertFalse(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

    def test_subscribe_post(self):
        """ Test subscription confirmation. """
        response = self.client.post(self.subscribe_confirm_url)

        self.assertContains(response, self.n.title, status_code=200)

        self.assertEqual(response.context['newsletter'], self.n)
        self.assertEqual(response.context['user'], self.user)

        subscription = self.get_user_subscription()
        self.assert_(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

    def test_subscribe_twice(self):
        # After subscribing we should not be able to subscribe again
        subscription = Subscription(user=self.user, newsletter=self.n)
        subscription.subscribed = True
        subscription.unsubscribed = False
        subscription.save()

        response = self.client.get(self.subscribe_url)

        self.assertContains(response, self.n.title, status_code=200)

        self.assertEqual(response.context['newsletter'], self.n)
        self.assertEqual(response.context['user'], self.user)

        self.assertNotContains(
            response, 'action="%s"' % self.subscribe_confirm_url)
        self.assertNotContains(response, 'id="id_submit"')

    def test_unsubscribe_view(self):
        """ Test the unsubscription form. """
        subscription = Subscription(user=self.user, newsletter=self.n)
        subscription.subscribed = True
        subscription.unsubscribed = False
        subscription.save()

        self.assertLessThan(
            subscription.subscribe_date, timezone.now() + timedelta(seconds=1)
        )

        response = self.client.get(self.unsubscribe_url)

        self.assertContains(response, self.n.title, status_code=200)

        self.assertEqual(response.context['newsletter'], self.n)
        self.assertEqual(response.context['user'], self.user)

        self.assertContains(
            response, 'action="%s"' % self.unsubscribe_confirm_url)
        self.assertContains(response, 'id="id_submit"')

        subscription = self.get_user_subscription()
        self.assert_(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

    def test_unsubscribe_not_subscribed_view(self):
        """
        Test attempting to unsubscriped a user without a subscription.
        """

        response = self.client.get(self.unsubscribe_url)

        self.assertIn(
            'You are not subscribed to',
            unicode(list(response.context['messages'])[0])
        )

    def test_unsubscribe_post(self):
        """ Test unsubscription confirmation. """
        subscription = Subscription(user=self.user, newsletter=self.n)
        subscription.subscribed = True
        subscription.unsubscribed = False
        subscription.save()

        response = self.client.post(self.unsubscribe_confirm_url)

        self.assertContains(response, self.n.title, status_code=200)

        self.assertEqual(response.context['newsletter'], self.n)
        self.assertEqual(response.context['user'], self.user)

        subscription = self.get_user_subscription()
        self.assertFalse(subscription.subscribed)
        self.assert_(subscription.unsubscribed)
        self.assertLessThan(
            subscription.unsubscribe_date,
            timezone.now() + timedelta(seconds=1)
        )

    def test_unsubscribe_twice(self):
        subscription = Subscription(user=self.user, newsletter=self.n)
        subscription.subscribed = False
        subscription.unsubscribed = True
        subscription.save()

        response = self.client.get(self.unsubscribe_url)

        self.assertContains(response, self.n.title, status_code=200)

        self.assertEqual(response.context['newsletter'], self.n)
        self.assertEqual(response.context['user'], self.user)

        self.assertNotContains(
            response,
            'action="%s"' % self.unsubscribe_confirm_url
        )
        self.assertNotContains(response, 'id="id_submit"')


class AnonymousSubscribeTestCase(
    SubscribeTestCase,
    ComparingTestCase
):

    def get_only_subscription(self, **kwargs):
        """
        Assert there's exactly one subscription that match kwargs lookup.
        Return this subscription.
        """

        subscription_qs = self.n.subscription_set.filter(**kwargs)

        self.assertEquals(subscription_qs.count(), 1)

        return subscription_qs[0]

    def test_subscribe_request_view(self):
        """ Test the subscription form. """

        response = self.app.get(self.subscribe_url)

        self.assertContains(response, self.n.title, status_code=200)

        self.assertIn('name_field', response.form.fields)
        self.assertIn('email_field', response.form.fields)

        self.assertEqual(response.context['newsletter'], self.n)

    @override_settings(NEWSLETTER_CONFIRM_EMAIL_SUBSCRIBE=True)
    def test_subscribe_request_post(self):
        """ Post the subscription form. """

        response = self.client.post(
            self.subscribe_url, {
                'name_field': 'Test Name',
                'email_field': 'test@email.com'
            }
        )

        # Assure we are redirected to "subscribe activation email sent" page.
        self.assertRedirects(response, self.subscribe_email_sent_url)

        subscription = self.get_only_subscription(
            email_field__exact='test@email.com'
        )

        self.assertFalse(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

        """ Check the subscription email. """
        self.assertEquals(len(mail.outbox), 1)

        activate_url = subscription.subscribe_activate_url()
        full_activate_url = 'http://%s%s' % (self.site.domain, activate_url)

        self.assertEmailContains(full_activate_url)

    @override_settings(NEWSLETTER_CONFIRM_EMAIL_SUBSCRIBE=False)
    def test_subscribe_request_post_no_email(self):
        """
        Post the subscription form
        with confirmation email switched off in settings.
        """

        response = self.client.post(
            self.subscribe_url, {
                'name_field': 'Test Name',
                'email_field': 'test@email.com'
            }
        )

        # Assure we are redirected to "subscribe activated" page.
        self.assertRedirects(response, self.subscribe_activated_url)

        subscription = self.get_only_subscription(
            email_field__exact='test@email.com'
        )

        # email confirmation is switched off,
        # so after subscribe request user should be subscribed
        self.assertTrue(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

        """ Check the subscription email. """
        # no email should be send
        self.assertEquals(len(mail.outbox), 0)

    # Only run this test when settings overrides are available
    @override_settings(NEWSLETTER_CONFIRM_EMAIL_SUBSCRIBE=True)
    def test_subscribe_request_post_error(self):
        """
        Test whether a failing subscribe request email generated an error in
        the context.

        We do this by overriding the default mail backend to a settings which
        we know pretty sure is bound to fail.
        """

        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
        ):
            with override_settings(EMAIL_PORT=12345678):
                response = self.client.post(
                    self.subscribe_url, {
                        'name_field': 'Test Name',
                        'email_field': 'test@ifjoidjsufhdsidhsuufihs.dfs'
                    }
                )

        self.assertTrue(response.context['error'])

    def test_retry_subscribe(self):
        """
        When requesting a subscription for an e-mail address for which
        an unconfirmed subscription is already available, make sure
        only one subscription object gets created.

        This is a regression of #14 on GitHub.
        """

        self.assertEquals(Subscription.objects.all().count(), 0)

        # Request subscription
        self.client.post(
            self.subscribe_url, {
                'name_field': 'Test Name',
                'email_field': 'test@email.com'
            }
        )

        self.assertEquals(Subscription.objects.all().count(), 1)

        # Request subscription
        self.client.post(
            self.subscribe_url, {
                'name_field': 'Test Name',
                'email_field': 'test@email.com'
            }
        )

        self.assertEquals(Subscription.objects.all().count(), 1)

    def test_subscribe_twice(self):
        """ Subscribing twice should not be possible. """

        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=True)
        subscription.save()

        response = self.client.post(
            self.subscribe_url, {
                'name_field': 'Test Name',
                'email_field': 'test@email.com'
            }
        )

        self.assertContains(response, "already been subscribed to",
                            status_code=200)

    def test_subscribe_unsubscribed(self):
        """
        After having been unsubscribed, a user should be able to subscribe
        again.

        This relates to #5 on GitHub.
        """

        # Create a subscription
        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=True)
        subscription.save()

        # Unsubscribe
        response = self.client.post(
            subscription.unsubscribe_activate_url(),
            {
                'name_field': subscription.name,
                'email_field': subscription.email,
                'user_activation_code': subscription.activation_code
            }
        )

        # Assure we are redirected to "unsubscribe activated" page.
        self.assertRedirects(response, self.unsubscribe_activated_url)

        subscription = self.get_only_subscription(
            email_field__exact='test@email.com'
        )

        self.assertFalse(subscription.subscribed)
        self.assert_(subscription.unsubscribed)

        # Resubscribe request
        response = self.client.post(
            self.subscribe_url,
            {
                'name_field': subscription.name,
                'email_field': subscription.email,
            }
        )

        # Assure we are redirected to "email sent page"
        self.assertRedirects(response, self.subscribe_email_sent_url)

        # self.assertFalse(subscription.subscribed)
        self.assert_(subscription.unsubscribed)

        # Activate subscription
        response = self.client.post(
            subscription.subscribe_activate_url(),
            {
                'name_field': subscription.name,
                'email_field': subscription.email,
                'user_activation_code': subscription.activation_code
            }
        )

        # Assure we are redirected to "subscribe activated" page.
        self.assertRedirects(response, self.subscribe_activated_url)

        subscription = self.get_only_subscription(
            email_field__exact='test@email.com'
        )

        self.assert_(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

    def test_user_update(self):
        """
        We should not be able to update anonymous for an email address
        belonging to an existing user.
        """

        password = User.objects.make_random_password()
        user = User.objects.create_user(
            'john', 'lennon@thebeatles.com', password)
        user.save()

        # Attempt to subscribe with user email address
        for url in (self.subscribe_url, self.update_url, self.unsubscribe_url):
            response = self.client.post(
                url, {
                    'name_field': 'Test Name',
                    'email_field': user.email
                }
            )

            self.assertContains(
                response,
                "Please log in as that user and try again.",
                status_code=200
            )

    def test_subscribe_request_activate(self):
        """ Test subscription activation. """

        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com')
        subscription.save()

        time.sleep(WAIT_TIME)

        self.assertFalse(subscription.subscribed)

        activate_url = subscription.subscribe_activate_url()
        self.assert_(activate_url)

        response = self.client.get(activate_url)
        self.assertInContext(response, 'form', UpdateForm)
        self.assertContains(response, subscription.activation_code)

        response = self.client.post(
            activate_url, {
                'name_field': 'Test Name',
                'email_field': 'test@email.com',
                'user_activation_code': subscription.activation_code
            }
        )

        # Assure we are redirected to "subscribe activated" page.
        self.assertRedirects(response, self.subscribe_activated_url)

        subscription = self.get_only_subscription(
            email_field__exact='test@email.com'
        )

        self.assert_(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

        dt = (subscription.subscribe_date - subscription.create_date).seconds
        self.assertBetween(dt, WAIT_TIME, WAIT_TIME + 1)

    @override_settings(NEWSLETTER_CONFIRM_EMAIL_UNSUBSCRIBE=True)
    def test_unsubscribe_request_post(self):
        """ Post the unsubscribe request form. """

        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=True)
        subscription.save()

        response = self.client.post(
            self.unsubscribe_url, {'email_field': 'test@email.com'}
        )

        # Assure we are redirected to "unsubscribe activation email sent" page.
        self.assertRedirects(response, self.unsubscribe_email_sent_url)

        """ Check the subscription email. """
        self.assertEquals(len(mail.outbox), 1)

        activate_url = subscription.unsubscribe_activate_url()
        full_activate_url = 'http://%s%s' % (self.site.domain, activate_url)

        self.assertEmailContains(full_activate_url)

    @override_settings(NEWSLETTER_CONFIRM_EMAIL_UNSUBSCRIBE=False)
    def test_unsubscribe_request_post_no_email(self):
        """
        Post the unsubscribe request form
        with confirmation email switched off in settings.
        """

        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=True)
        subscription.save()

        response = self.client.post(
            self.unsubscribe_url, {'email_field': 'test@email.com'}
        )

        # Assure we are redirected to "unsubscribe activated" page.
        self.assertRedirects(response, self.unsubscribe_activated_url)

        changed_subscription = self.get_only_subscription(
            email_field__exact='test@email.com'
        )

        # email confirmation is switched off,
        # so after unsubscribe request user should be unsubscribed
        self.assertFalse(changed_subscription.subscribed)
        self.assertTrue(changed_subscription.unsubscribed)

        """ Check the subscription email. """
        # no email should be send
        self.assertEquals(len(mail.outbox), 0)

    @override_settings(NEWSLETTER_CONFIRM_EMAIL_UNSUBSCRIBE=True)
    def test_unsubscribe_request_post_error(self):
        """
        Test whether a failing unsubscribe request email generated an error in
        the context.

        We do this by overriding the default mail backend to a settings which
        we know pretty sure is bound to fail.
        """
        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=True)
        subscription.save()

        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
        ):
            with override_settings(EMAIL_PORT=12345678):
                response = self.client.post(
                    self.unsubscribe_url, {'email_field': 'test@email.com'}
                )

        self.assertTrue(response.context['error'])

    def test_unsubscribe_request_view(self):
        """ Test the unsubscribe request form. """
        response = self.app.get(self.unsubscribe_url)

        self.assertContains(response, self.n.title, status_code=200)

        self.assertIn('email_field', response.form.fields)

        self.assertEqual(response.context['newsletter'], self.n)

    def test_unsubscribe_request_activate(self):
        """ Update a request. """

        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com')
        subscription.save()

        activate_url = subscription.unsubscribe_activate_url()

        response = self.client.get(activate_url)
        self.assertInContext(response, 'form', UpdateForm)
        self.assertContains(response, subscription.activation_code)

        testname2 = 'Test Name2'
        testemail2 = 'test2@email.com'
        response = self.client.post(activate_url, {
            'name_field': testname2,
            'email_field': testemail2,
            'user_activation_code': subscription.activation_code
        })

        # Assure we are redirected to "unsubscribe activated" page.
        self.assertRedirects(response, self.unsubscribe_activated_url)

        subscription = self.get_only_subscription(
            email_field__exact=testemail2
        )

        self.assert_(subscription.unsubscribed)
        self.assertEqual(subscription.name, testname2)
        self.assertEqual(subscription.email, testemail2)

        dt = (timezone.now() - subscription.unsubscribe_date).seconds
        self.assertLessThan(dt, 2)

    def test_update_request_view(self):
        """ Test the update request form. """

        response = self.app.get(self.update_url)

        self.assertContains(response, self.n.title, status_code=200)
        self.assertIn('email_field', response.form.fields)

        self.assertEqual(response.context['newsletter'], self.n)

    @override_settings(NEWSLETTER_CONFIRM_EMAIL_UPDATE=True)
    def test_update_request_post(self):
        """ Test the update request post view. """

        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=True)
        subscription.save()

        response = self.client.post(
            self.update_url, {'email_field': 'test@email.com'}
        )

        # Assure we are redirected to "update activation email sent" page.
        self.assertRedirects(response, self.update_email_sent_url)

        """ Check the subscription email. """
        self.assertEquals(len(mail.outbox), 1)

        activate_url = subscription.update_activate_url()
        full_activate_url = 'http://%s%s' % (self.site.domain, activate_url)

        self.assertEmailContains(full_activate_url)

    @override_settings(NEWSLETTER_CONFIRM_EMAIL_UPDATE=False)
    def test_update_request_post_no_email(self):
        """
        Test the update request post view
        with confirmation email switched off in settings.
        """

        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=True)
        subscription.save()

        response = self.client.post(
            self.update_url, {'email_field': 'test@email.com'}
        )

        self.assertRedirects(response, subscription.update_activate_url())

        """ Check the subscription email. """
        # no email should be send
        self.assertEquals(len(mail.outbox), 0)

    @override_settings(NEWSLETTER_CONFIRM_EMAIL_UPDATE=True)
    def test_update_request_post_error(self):
        """
        Test whether a failing update request email generated an error in
        the context.

        We do this by overriding the default mail backend to a settings which
        we know pretty sure is bound to fail.
        """
        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=True)
        subscription.save()

        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
        ):
            with override_settings(EMAIL_PORT=12345678):
                response = self.client.post(
                    self.update_url, {'email_field': 'test@email.com'}
                )

        self.assertTrue(response.context['error'])

    def test_unsubscribe_update_unactivated(self):
        """ Test updating unsubscribed subscriptions view. """

        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=False)
        subscription.save()

        for url in (self.update_url, self.unsubscribe_url):
            response = self.client.post(
                url, {'email_field': 'test@email.com'}
            )

            self.assertContains(
                response, "This subscription has not yet been activated."
            )

    def test_unsubscribe_update_unsubscribed(self):
        """ Test updating nonexisting subscriptions view. """

        # The second call of this will fail due to a weird bug
        # where Django picks the wrong translation. Nevermind.
        for url in (self.update_url, self.unsubscribe_url):
            response = self.client.post(
                url, {'email_field': 'newemail@fdgf.com'})

            self.assertContains(
                response, "This e-mail address has not been subscribed to."
            )

    def test_update_request_activate(self):
        """ Update a request. """

        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com')
        subscription.save()

        activate_url = subscription.update_activate_url()

        response = self.client.get(activate_url)
        self.assertInContext(response, 'form', UpdateForm)
        self.assertContains(response, subscription.activation_code)

        testname2 = 'Test Name2'
        testemail2 = 'test2@email.com'
        response = self.client.post(activate_url, {
            'name_field': testname2,
            'email_field': testemail2,
            'user_activation_code': subscription.activation_code
        })

        # Assure we are redirected to "update activated" page.
        self.assertRedirects(response, self.update_activated_url)

        subscription = self.get_only_subscription(
            email_field__exact=testemail2
        )

        self.assert_(subscription)
        self.assert_(subscription.subscribed)
        self.assertEqual(subscription.name, testname2)
        self.assertEqual(subscription.email, testemail2)

    def test_update_request_activate_form(self):
        """
        Test requesting a form for activating an update without activation
        code in the URL.
        """

        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com')
        subscription.save()

        activate_url = reverse('newsletter_update', kwargs={
            'newsletter_slug': self.n.slug,
            'action': 'update',
            'email': subscription.email
        })

        response = self.client.get(activate_url)

        # Make sure the form is there
        self.assertInContext(response, 'form', UpdateForm)


class InvisibleAnonymousSubscribeTestCase(AnonymousSubscribeTestCase):
    """
    Tests for subscribing, unsubscribing and updating of subscription to
    a newsletter that is not publicly exposed on the site
    (has visible=False).

    Runs all anonymous and user test cases with invisible newsletter.
    """

    def setUp(self):
        super_obj = super(InvisibleAnonymousSubscribeTestCase, self)
        super_obj.setUp()

        # Make newsletter invisible
        self.n.visible = False
        self.n.save()


class InvisibleUserSubscribeTestCase(UserSubscribeTestCase):
    """
    Tests for subscribing, unsubscribing and updating of subscription to
    a newsletter that is not publicly exposed on the site
    (has visible=False).

    Runs all anonymous and user test cases with invisible newsletter.
    """

    def setUp(self):
        super_obj = super(InvisibleUserSubscribeTestCase, self)
        super_obj.setUp()

        # Make newsletter invisible
        self.n.visible = False
        self.n.save()


class ArchiveTestcase(NewsletterListTestCase):
    def setUp(self):
        """ Make sure we have a few submissions to test with. """

        # Pick some newsletter
        try:
            self.newsletter = Newsletter.objects.all()[0]
        except IndexError:
            self.newsletter = None

        # Make sure there's a HTML template for this newsletter,
        # otherwise the archive will not function.

        (subject_template, text_template, html_template) = \
            self.newsletter.get_templates('message')

        self.assertTrue(html_template)

        # Create a message first
        message = Message(
            title='Test message',
            slug='test-message',
        )

        message.save()

        # Create a submission
        self.submission = Submission.from_message(message)

    def test_archive_invisible(self):
        """ Test whether an invisible newsletter is indeed not shown. """

        self.newsletter.visible = False
        self.newsletter.save()

        archive_url = self.submission.newsletter.archive_url()

        response = self.client.get(archive_url)
        self.assertEqual(response.status_code, 404)

        detail_url = self.submission.get_absolute_url()

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)

    def test_archive_list(self):
        """ Test the Submission list view. """

        archive_url = self.submission.newsletter.archive_url()

        # When published, this should return properly
        response = self.client.get(archive_url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.submission.message.title)
        self.assertContains(response, self.submission.get_absolute_url())

    def test_archive_detail(self):
        """ Test Submission detail view. """

        detail_url = self.submission.get_absolute_url()

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.submission.message.title)

    def test_archive_unpublished_detail(self):
        """ Assert that an unpublished submission is truly inaccessible. """

        self.submission.publish = False
        self.submission.save()

        archive_url = self.submission.newsletter.archive_url()

        response = self.client.get(archive_url)
        self.assertNotContains(response, self.submission.message.title)
        self.assertNotContains(response, self.submission.get_absolute_url())

        detail_url = self.submission.get_absolute_url()

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)

    @unittest.skipUnless(pytz, 'pytz could not be imported.')
    @override_settings(
        TIME_ZONE='Europe/Paris',
        USE_TZ=True
    )
    def test_archive_timezone_regression(self):
        """
        Regression test for #74: Wrong submission archive urls when
        timezones are enabled.

        Ref:
            * https://docs.djangoproject.com/en/1.5/topics/i18n/timezones/#troubleshooting
            * https://github.com/dokterbob/django-newsletter/issues/74
        """
        problematic_date = datetime(2012, 3, 3, 1, 30)

        paris_date = timezone.make_aware(
            problematic_date, timezone.get_default_timezone()
        )

        # Setup submission in paris timezone
        self.submission.publish_date = paris_date
        self.submission.save()

        # Test viewing the submission in another timezone
        timezone.activate('America/New_York')

        # Test viewing the submission
        self.test_archive_detail()


class ActionTemplateViewMixin(object):
    """ Mixin for testing requests to urls for all three actions. """

    def get_action_url(self, action):
        """
        This method should be overridden in subclasses.
        Return url for given action.
        """

        raise NotImplementedError(
            '%(class_name)s inherits from of ActionTemplateViewMixin '
            'and should define get_url method.' % {
                'class_name': self.__class__.__name__
            }
        )

    def action_url_test(self, action):
        """ Assertions common for all actions. """
        response = self.client.get(self.get_action_url(action))

        self.assertEquals(response.status_code, 200)
        self.assertInContext(response, 'newsletter', Newsletter, self.n)
        self.assertInContext(response, 'action', value=action)

    def test_subscribe_url(self):
        self.action_url_test('subscribe')

    def test_unsubscribe_url(self):
        self.action_url_test('unsubscribe')

    def test_update_url(self):
        self.action_url_test('update')


class ActivationEmailSentUrlTestCase(
        ActionTemplateViewMixin, SubscribeTestCase
):
    """
    TestCase for testing requests to urls with activation email sent info.
    """

    def get_action_url(self, action):
        """ Return url with email sent info for given action. """

        return getattr(self, '%s_email_sent_url' % action)


class ActionActivatedUrlTestCase(
        ActionTemplateViewMixin, SubscribeTestCase
):
    """
    TestCase for testing requests to urls with action activated info.
    """

    def get_action_url(self, action):
        """ Return url with action activated info for given action. """

        return getattr(self, '%s_activated_url' % action)
