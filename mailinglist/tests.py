import logging

from django.core import mail

from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test.client import Client

from models import *
from forms import *

class WebTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.get_current()
        
        super(WebTestCase, self).setUp()

    def assertInContext(self, response, variable, instance_of=None, value=None):
        try:
            instance = response.context[variable]
            self.assert_(instance)
        except KeyError:
            self.fail('Asserted variable %s not in response context.')
        
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
            self.assert_((value in my_email.subject) or (value in my_email.body), 'Email does not contain "%s".' % value)
    
    def assertEmailBodyContains(self, value, email=None):
        for my_email in self.get_email_list(email):
            self.assert_(value in my_email.body, 'Email body does not contain "%s".' % value)
            
    def assertEmailSubjectContains(self, value, email=None):
        for my_email in self.get_email_list(email):
            self.assert_(value in my_email.subject, 'Email subject does not contain "%s".' % value)
    
class WebSubscribeTestCase(WebTestCase, MailTestCase):
    def setUp(self):
        self.n = Newsletter(title='Test newsletter',
                            slug='test-newsletter',
                            sender='Test Sender',
                            email='test@testsender.com')
        self.n.save()
        self.n.site = get_default_sites()
        
        self.subscribe_url = reverse('mailinglist_newsletter_subscribe_request', 
                                     kwargs={'newsletter_slug' : self.n.slug })
                                     
        self.unsubscribe_url = reverse('mailinglist_newsletter_unsubscribe_request', 
                                       kwargs={'newsletter_slug' : self.n.slug })
                                       
        self.update_url = reverse('mailinglist_newsletter_update_request', 
                                  kwargs={'newsletter_slug' : self.n.slug })
        
        super(WebSubscribeTestCase, self).setUp()

    
    def test_urls(self):
        self.assert_(len(self.subscribe_url))
        self.assert_(len(self.unsubscribe_url))
        self.assert_(len(self.update_url))
    
    def test_subscribe_request_view(self):
        """ Test the subscription form. """
        r = self.client.get(self.subscribe_url)
        
        self.assertContains(r, self.n.title, status_code=200)
        self.assertContains(r, 'input id="id_name" type="text" name="name"')
        self.assertContains(r, 'input id="id_email" type="text" name="email"')
        
        self.assertEqual(r.context['newsletter'], self.n)
    
    def test_subscribe_request_post(self):
        """ Post the subscription form. """
        r = self.client.post(self.subscribe_url, {'name':'Test Name', 'email':'test@email.com'})
        
        self.assertContains(r, self.n.title, status_code=200)
        self.assertNotContains(r, 'input id="id_name" type="text" name="name"')
        self.assertNotContains(r, 'input id="id_email" type="text" name="email"')
        
        self.assertInContext(r, 'newsletter', Newsletter, self.n)
        self.assertInContext(r, 'site', Site, self.site)        
        self.assertInContext(r, 'form', SubscribeRequestForm)
        
        subscription = getattr(r.context['form'], 'instance', None)
        self.assert_(subscription)
        self.assertFalse(subscription.activated)
        self.assertFalse(subscription.unsubscribed)
        
        """ Check the subscription email. """
        self.assertEquals(len(mail.outbox), 1)
                
        activate_url = subscription.subscribe_activate_url()
        full_activate_url = 'http://%s%s' % (self.site.domain, activate_url)
        
        self.assertEmailContains(full_activate_url)
    
    def test_subscribe_request_activate(self):
        """ Test subscription activation. """
        subscription = Subscription(newsletter=self.n, name='Test Name', email='test@email.com')
        subscription.save()
        
        self.assertFalse(subscription.activated)
        
        activate_url = subscription.subscribe_activate_url()
        self.assert_(activate_url)

        r = self.client.post(activate_url, {'name':'Test Name', 'email':'test@email.com', 'user_activation_code':subscription.activation_code})
        
        self.assertInContext(r, 'form', UpdateForm)
        
        subscription = getattr(r.context['form'], 'instance', None)
        self.assert_(subscription)
        self.assert_(subscription.activated)
        self.assertFalse(subscription.unsubscribed)

