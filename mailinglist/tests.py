import unittest, logging

from django.test.client import Client
from django.core.urlresolvers import reverse

from models import *

class WebSubscribeTestCase(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.c = Client()
        self.n = Newsletter(title='Test newsletter',
                            slug='test-newsletter',
                            sender='Test Sender',
                            email='test@testsender.com')
        self.n.save()
        self.n.site = get_default_sites()
    
    def test_subscribe_request(self):
        subscribe_url = reverse('mailinglist_newsletter_subscribe_request', 
                                kwargs={'newsletter_slug' : self.n.slug })
                                
        r = self.c.get(subscribe_url)

        