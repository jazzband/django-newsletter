import logging

from django.core import mail

from django.contrib.sites.models import Site

from django.test import TestCase
from django.test.client import Client

class WebTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.get_current()
        
        super(WebTestCase, self).setUp()

    def assertInContext(self, response, variable, instance_of=None, value=None):
        try:
            instance = response.context[variable]
            self.assert_(instance)
        except KeyError:
            self.fail('Asserted variable %s not in response context.' % variable)
        
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
    