from datetime import datetime, timedelta
import time

from django.core import mail

from django.core.urlresolvers import reverse

from newsletter.models import *
from newsletter.forms import *

from utils import *

WAIT_TIME=1


class NoNewsLetterListTestCase(WebTestCase):
    """ Test case for when no newsletter exists """
    
    def setUp(self):
        Newsletter.objects.all().delete()
        
        self.list_url = reverse('newsletter_list')
    
    def test_list(self):
        """ Test whether all newsletters are in the list and whether the links
            to them are correct. """
            
        r = self.client.get(self.list_url)
        
        self.assertEqual(r.status_code, 404)


class NewsletterListTestCase(WebTestCase):
    """ Base class for newsletter test cases. """
    
    fixtures = ['default_templates', 'test_newsletters']

    def setUp(self):
        self.newsletters = Newsletter.objects.all()

        self.list_url = reverse('newsletter_list')


class AnonymousNewsletterListTestCase(NewsletterListTestCase):
    """ Test case for anonymous views of newsletter. """

    def test_list(self):
        """ Test whether all newsletters are in the list and whether the links
        to them are correct. """
        r = self.client.get(self.list_url)

        for n in self.newsletters.filter(visible=True):
            self.assertContains(r, n.title)

            detail_url = reverse('newsletter_detail',
                                 kwargs={'newsletter_slug': n.slug})
            self.assertContains(r, '<a href="%s">' % detail_url)
        
        for n in self.newsletters.filter(visible=False):
            self.assertNotContains(r, n.title)

    def test_detail(self):
        for n in self.newsletters:
            detail_url = reverse('newsletter_detail',
                                 kwargs={'newsletter_slug': n.slug})

            subscribe_url = reverse('newsletter_subscribe_request',
                                 kwargs={'newsletter_slug': n.slug})


            unsubscribe_url = reverse('newsletter_unsubscribe_request',
                                 kwargs={'newsletter_slug': n.slug})


            update_url = reverse('newsletter_update_request',
                                 kwargs={'newsletter_slug': n.slug})

            archive_url = reverse('newsletter_archive',
                                 kwargs={'newsletter_slug': n.slug})

            
            r = self.client.get(detail_url)
            
            if not n.visible:
                self.assertEqual(r.status_code, 404)
                continue
            
            self.assertContains(r, '<a href="%s">' % subscribe_url )
            self.assertContains(r, '<a href="%s">' % update_url )
            self.assertContains(r, '<a href="%s">' % unsubscribe_url )
            self.assertContains(r, '<a href="%s">' % archive_url )
            
            r = self.client.get(subscribe_url)
            self.assertContains(r, n.title, status_code=200)

            r = self.client.get(unsubscribe_url)
            self.assertContains(r, n.title, status_code=200)

            r = self.client.get(update_url)
            self.assertContains(r, n.title, status_code=200)

            r = self.client.get(archive_url)
            self.assertContains(r, n.title, status_code=200)


class UserNewsletterListTestCase(UserTestCase,
                                 NewsletterListTestCase):

    def get_user_subscription(self, newsletter):
        subscriptions = Subscription.objects.filter(newsletter=newsletter,
                                                    user=self.user)
        self.assertEqual(subscriptions.count(), 1)

        subscription = subscriptions[0]
        self.assert_(subscription.create_date)

        return subscriptions[0]

    def test_form(self):
        """ Test whether form elements are present. """
        r = self.client.get(self.list_url)

        formset = r.context['formset']
        total_forms = len(formset.forms)
        self.assertEqual(total_forms, len(self.newsletters.filter(visible=True)))
        self.assertContains(r, \
            '<input type="hidden" name="form-TOTAL_FORMS" value="%d" id="id_form-TOTAL_FORMS" />' % total_forms)
        self.assertContains(r, \
            '<input type="hidden" name="form-INITIAL_FORMS" value="%d" id="id_form-INITIAL_FORMS" />' % total_forms)

        for form in formset.forms:
            self.assert_(form.instance.newsletter in self.newsletters, \
                "%s not in %s" % (form.instance.newsletter, self.newsletters))
            self.assertContains(r, form['id'])
            self.assertContains(r, form['subscribed'])

    # def test_update(self):
    #     r = self.client.get(self.list_url)
    # 
    #     formset = r.context['formset']
    # 
    #     total_forms = self.newsletters.count()
    #     params = {'form-TOTAL_FORMS' : total_forms,
    #               'form-INITIAL_FORMS' : total_forms}
    #     
    #     for n in self.newsletters:
    #         for x in xrange(0, total_forms):
    #             field = 'form-%d-id' % x
    #             params.update({field: self.newsletters[x-1]})
    #             if n == self.newsletters[x-1]:
    #                 params.update('form-%d-subscribed' % x: 'checked'})
    #         r = self.client.post(self.list_url, params)

class WebSubscribeTestCase(WebTestCase, MailTestCase):
    
    fixtures = ['default_templates']

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

        self.update_url = \
            reverse('newsletter_update_request',
                    kwargs={'newsletter_slug': self.n.slug})

        self.unsubscribe_url = \
            reverse('newsletter_unsubscribe_request',
                    kwargs={'newsletter_slug': self.n.slug})

        self.unsubscribe_confirm_url = \
            reverse('newsletter_unsubscribe_confirm',
                    kwargs={'newsletter_slug': self.n.slug})

        super(WebSubscribeTestCase, self).setUp()

    def test_urls(self):
        self.assert_(len(self.subscribe_url))
        self.assert_(len(self.update_url))
        self.assert_(len(self.unsubscribe_url))
        self.assert_(len(self.subscribe_confirm_url))
        self.assert_(len(self.unsubscribe_confirm_url))


class WebUserSubscribeTestCase(WebSubscribeTestCase,
                               UserTestCase,
                               ComparingTestCase):
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
        r = self.client.get(self.subscribe_url)

        self.assertContains(r, self.n.title, status_code=200)

        self.assertEqual(r.context['newsletter'], self.n)
        self.assertEqual(r.context['user'], self.user)

        self.assertContains(r, 'action="%s"' % self.subscribe_confirm_url)
        self.assertContains(r, 'id="id_submit"')

        subscription = self.get_user_subscription()
        self.assertFalse(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

    def test_subscribe_post(self):
        """ Test subscription confirmation. """
        r = self.client.post(self.subscribe_confirm_url)

        self.assertContains(r, self.n.title, status_code=200)

        self.assertEqual(r.context['newsletter'], self.n)
        self.assertEqual(r.context['user'], self.user)

        subscription = self.get_user_subscription()
        self.assert_(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)
    
    def test_subscribe_twice(self):
        # After subscribing we should not be able to subscribe again
        subscription = Subscription(user=self.user, newsletter=self.n)
        subscription.subscribed = True
        subscription.unsubscribed = False
        subscription.save()
        
        r = self.client.get(self.subscribe_url)

        self.assertContains(r, self.n.title, status_code=200)

        self.assertEqual(r.context['newsletter'], self.n)
        self.assertEqual(r.context['user'], self.user)

        self.assertNotContains(r, 'action="%s"' % self.subscribe_confirm_url)
        self.assertNotContains(r, 'id="id_submit"')

    def test_unsubscribe_view(self):
        """ Test the unsubscription form. """
        subscription = Subscription(user=self.user, newsletter=self.n)
        subscription.subscribed = True
        subscription.unsubscribed = False
        subscription.save()

        self.assertLessThan(subscription.subscribe_date, datetime.now() \
            + timedelta(seconds=1))

        r = self.client.get(self.unsubscribe_url)

        self.assertContains(r, self.n.title, status_code=200)

        self.assertEqual(r.context['newsletter'], self.n)
        self.assertEqual(r.context['user'], self.user)

        self.assertContains(r, 'action="%s"' % self.unsubscribe_confirm_url)
        self.assertContains(r, 'id="id_submit"')

        subscription = self.get_user_subscription()
        self.assert_(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

    def test_unsubscribe_post(self):
        """ Test unsubscription confirmation. """
        subscription = Subscription(user=self.user, newsletter=self.n)
        subscription.subscribed = True
        subscription.unsubscribed = False
        subscription.save()

        r = self.client.post(self.unsubscribe_confirm_url)

        self.assertContains(r, self.n.title, status_code=200)

        self.assertEqual(r.context['newsletter'], self.n)
        self.assertEqual(r.context['user'], self.user)

        subscription = self.get_user_subscription()
        self.assertFalse(subscription.subscribed)
        self.assert_(subscription.unsubscribed)
        self.assertLessThan(subscription.unsubscribe_date, datetime.now() \
                                + timedelta(seconds=1))

    def test_unsubscribe_twice(self):
        subscription = Subscription(user=self.user, newsletter=self.n)
        subscription.subscribed = False
        subscription.unsubscribed = True
        subscription.save()
        
        r = self.client.get(self.unsubscribe_url)

        self.assertContains(r, self.n.title, status_code=200)

        self.assertEqual(r.context['newsletter'], self.n)
        self.assertEqual(r.context['user'], self.user)

        self.assertNotContains(r, 'action="%s"' % self.unsubscribe_confirm_url)
        self.assertNotContains(r, 'id="id_submit"')

class AnonymousSubscribeTestCase(WebSubscribeTestCase, 
                                 ComparingTestCase):

    def test_subscribe_request_view(self):
        """ Test the subscription form. """
        r = self.client.get(self.subscribe_url)

        self.assertContains(r, self.n.title, status_code=200)
        self.assertContains(r, 'input id="id_name_field" type="text" name="name_field"')
        self.assertContains(r, 'input id="id_email_field" type="text" name="email_field"')

        self.assertEqual(r.context['newsletter'], self.n)

    def test_subscribe_request_post(self):
        """ Post the subscription form. """
        r = self.client.post(self.subscribe_url, {'name_field': 'Test Name',
                                                  'email_field': 'test@email.com'})

        self.assertContains(r, self.n.title, status_code=200)
        self.assertNotContains(r, 'input id="id_name_field" type="text" name="name"')
        self.assertNotContains(r, 'input id="id_email_field" type="text" name="email"')

        self.assertInContext(r, 'newsletter', Newsletter, self.n)
        self.assertInContext(r, 'form', SubscribeRequestForm)

        subscription = getattr(r.context['form'], 'instance', None)
        self.assert_(subscription)
        self.assertFalse(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

        """ Check the subscription email. """
        self.assertEquals(len(mail.outbox), 1)

        activate_url = subscription.subscribe_activate_url()
        full_activate_url = 'http://%s%s' % (self.site.domain, activate_url)

        self.assertEmailContains(full_activate_url)

    def test_subscribe_twice(self):
        """ Subscribing twice should not be possible """
        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=True)
        subscription.save()

        r = self.client.post(self.subscribe_url, {'name_field': 'Test Name',
                                                  'email_field': 'test@email.com'})
        
        self.assertContains(r, "already been subscribed to",
                            status_code=200)
        
    def test_user_update(self):
        """ We should not be able to update anonymous for an email address belonging
            to an existing user. """

        from django.contrib.auth.models import User
        password = User.objects.make_random_password()
        user = User.objects.create_user('john', 'lennon@thebeatles.com', password)
        user.save()

        # Attempt to subscribe with user email address
        for url in (self.subscribe_url, self.update_url, self.unsubscribe_url):
            r = self.client.post(url, {'name_field': 'Test Name',
                                                      'email_field': user.email})

            self.assertContains(r, "Please log in as that user and try again.",
                                status_code=200)

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

        r = self.client.get(activate_url)
        self.assertInContext(r, 'form', UpdateForm)
        self.assertContains(r, subscription.activation_code)

        r = self.client.post(activate_url, {'name_field': 'Test Name',
                                            'email_field': 'test@email.com',
                                            'user_activation_code': subscription.activation_code})
        self.assertInContext(r, 'form', UpdateForm)

        subscription = getattr(r.context['form'], 'instance', None)
        self.assert_(subscription)
        self.assert_(subscription.subscribed)
        self.assertFalse(subscription.unsubscribed)

        dt = (subscription.subscribe_date - subscription.create_date).seconds
        self.assertBetween(dt, WAIT_TIME, WAIT_TIME+1)
        
    def test_unsubscribe_request_post(self):
        """ Post the unsubscribe request form. """
        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com',
                                    subscribed=True)
        subscription.save()

        r = self.client.post(self.unsubscribe_url, {'email_field': 'test@email.com'})

        self.assertContains(r, self.n.title, status_code=200)
        self.assertNotContains(r, 'input id="id_email_field" type="text" name="email"')

        self.assertInContext(r, 'newsletter', Newsletter, self.n)
        self.assertInContext(r, 'form', UpdateRequestForm)

        self.assertEqual(subscription, r.context['form'].instance)

        """ Check the subscription email. """
        self.assertEquals(len(mail.outbox), 1)

        activate_url = subscription.unsubscribe_activate_url()
        full_activate_url = 'http://%s%s' % (self.site.domain, activate_url)

        self.assertEmailContains(full_activate_url)

    def test_unsubscribe_request_view(self):
        """ Test the unsubscribe request form. """
        r = self.client.get(self.unsubscribe_url)

        self.assertContains(r, self.n.title, status_code=200)
        self.assertContains(r, 'input id="id_email_field" type="text" name="email_field"')

        self.assertEqual(r.context['newsletter'], self.n)

    def test_unsubscribe_request_activate(self):
        """ Update a request. """
        subscription = Subscription(newsletter=self.n,
                                    name='Test Name',
                                    email='test@email.com')
        subscription.save()

        activate_url = subscription.unsubscribe_activate_url()

        r = self.client.get(activate_url)
        self.assertInContext(r, 'form', UpdateForm)
        self.assertContains(r, subscription.activation_code)

        testname2 = 'Test Name2'
        testemail2 = 'test2@email.com'
        r = self.client.post(activate_url, \
                {'name_field': testname2,
                 'email_field': testemail2,
                 'user_activation_code': subscription.activation_code})
        self.assertInContext(r, 'form', UpdateForm)

        subscription = getattr(r.context['form'], 'instance', None)
        self.assert_(subscription)
        self.assert_(subscription.unsubscribed)
        self.assertEqual(subscription.name, testname2)
        self.assertEqual(subscription.email, testemail2)

        dt = (datetime.now() - subscription.unsubscribe_date).seconds
        self.assertLessThan(dt, 2)
