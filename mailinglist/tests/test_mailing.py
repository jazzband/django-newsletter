from mailinglist.models import *
from mailinglist.forms import *

from utils import *

class MailingTestCase(MailTestCase):
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
        
        self.s = Subscription(name='Test Name', email='test@test.com', newsletter=self.n, activated=True)
        self.s.save()
        

class CreateSubmissionTestCase(MailingTestCase):
    def test_subscription(self):
        self.assertEqual(self.s.get_recipient(), 'Test Name <test@test.com>')
        
    def test_submission_from_message(self):        
        sub = Submission.from_message(self.m)
        
        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [self.s,])
        
        self.assertFalse(sub.prepared)
        self.assertFalse(sub.sent)
        self.assertFalse(sub.sending)
    
    def test_submission_unactivated(self):
        self.s.activated=False
        self.s.save()
        
        sub = Submission.from_message(self.m)
        
        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [])
    
    def test_submission_unsubscribed(self):
        self.s.unsubscribed=True
        self.s.save()
        
        sub = Submission.from_message(self.m)
        
        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [])
    
    def test_submission_unsubscribed_unactivated(self):
        self.s.activated=False
        self.s.unsubscribed=True
        self.s.save()
        
        sub = Submission.from_message(self.m)
        
        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [])
    
    def test_twosubmissions(self):
        s2 = Subscription(name='Test Name 2', email='test2@test.com', newsletter=self.n, activated=True)
        s2.save()
        
        sub = Submission.from_message(self.m)
        
        subscriptions = sub.subscriptions.all()
        self.assert_(self.s in list(subscriptions))
        self.assert_(s2 in list(subscriptions))
    
    def test_twosubmissions(self):
        s2 = Subscription(name='Test Name 2', email='test2@test.com', newsletter=self.n, activated=False)
        s2.save()
        
        sub = Submission.from_message(self.m)
        
        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [self.s] )

class SubmitSubmissionTestCase(MailingTestCase):
    def setUp(self):
        super(SubmitSubmissionTestCase, self).setUp()
        
        self.sub = Submission.from_message(self.m)
        self.sub.save()
    
    def test_submission(self):
        self.assertFalse(self.sub.prepared)
        self.assertFalse(self.sub.sent)
        self.assertFalse(self.sub.sending)
    
    def test_submitsubmission(self):
        self.sub.prepared=True
        self.sub.save()
        
        self.sub.submit()
        
        self.assert_(self.sub.sent)
        self.assertFalse(self.sub.sending)
        
        
        