from newsletter.models import *
from newsletter.forms import *

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
        
        self.s = Subscription(name='Test Name', email='test@test.com', newsletter=self.n, subscribed=True)
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
        
    
    def test_moving(self):
        a1 = self.make_article()
        a1o = a1.sortorder
        
        a2 = self.make_article()
        a2o = a2.sortorder

        a3 = self.make_article()
        a3o = a3.sortorder
        
        a1.move_down()
        self.assertEqual(self.update(a1).sortorder, a2o)
        self.assertEqual(self.update(a2).sortorder, a1o)
        self.assertEqual(self.update(a3).sortorder, a3o)
        
        a1.move_up()
        self.assertEqual(self.update(a1).sortorder, a1o)
        self.assertEqual(self.update(a2).sortorder, a2o)
        self.assertEqual(self.update(a3).sortorder, a3o)
        
        a1.move_up()
        self.assertEqual(self.update(a1).sortorder, a1o)
        self.assertEqual(self.update(a2).sortorder, a2o)
        self.assertEqual(self.update(a3).sortorder, a3o)
        
        a3.move_down()
        self.assertEqual(self.update(a1).sortorder, a1o)
        self.assertEqual(self.update(a2).sortorder, a2o)
        self.assertEqual(self.update(a3).sortorder, a3o)


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
    
    def test_submission_unsubscribed(self):
        self.s.subscribed=False
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
    
    def test_submission_unsubscribed_unsubscribed(self):
        self.s.subscribed=False
        self.s.unsubscribed=True
        self.s.save()
        
        sub = Submission.from_message(self.m)
        
        subscriptions = sub.subscriptions.all()
        self.assertEqual(list(subscriptions), [])
    
    def test_twosubmissions(self):
        s2 = Subscription(name='Test Name 2', email='test2@test.com', newsletter=self.n, subscribed=True)
        s2.save()
        
        sub = Submission.from_message(self.m)
        
        subscriptions = sub.subscriptions.all()
        self.assert_(self.s in list(subscriptions))
        self.assert_(s2 in list(subscriptions))
    
    def test_twosubmissions(self):
        s2 = Subscription(name='Test Name 2', email='test2@test.com', newsletter=self.n, subscribed=False)
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

class SubscriptionTestCase(UserTestCase, MailingTestCase):
    def setUp(self):
        super(SubscriptionTestCase, self).setUp()

        self.us = Subscription(user=self.user, newsletter=self.n)
        self.us.save()

        self.ns = Subscription(name='Test susbcriber', newsletter=self.n, email='test@test.com')
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
            
