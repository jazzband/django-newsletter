import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import patch_logger

from newsletter import admin  # Triggers model admin registration
from newsletter.admin_utils import make_subscription
from newsletter.models import Message, Newsletter, Submission, Subscription

test_files_dir = os.path.join(os.path.dirname(__file__), 'files')


class AdminTestMixin(object):
    def setUp(self):
        super(AdminTestMixin, self).setUp()

        User = get_user_model()
        self.password = 'johnpassword'
        self.admin_user = User.objects.create_superuser(
            'john', 'lennon@thebeatles.com', self.password
        )
        self.client.login(username=self.admin_user.username, password=self.password)
        self.newsletter = Newsletter.objects.create(
            sender='Test Sender', title='Test Newsletter',
            slug='test-newsletter', visible=True, email='test@test.com',
        )
        self.message = Message.objects.create(
            newsletter=self.newsletter, title='Test message', slug='test-message'
        )


class AdminTestCase(AdminTestMixin, TestCase):
    def admin_import_file(self, source_file, ignore_errors=''):
        """ Upload an address file for import to admin. """

        import_url = reverse('admin:newsletter_subscription_import')

        with open(os.path.join(test_files_dir, source_file), 'rb') as fh:
            return self.client.post(import_url, {
                'newsletter': self.newsletter.pk,
                'address_file': fh,
                'ignore_errors': ignore_errors,
            }, follow=True)

    def admin_import_subscribers(self, source_file, ignore_errors=''):
        """
        Import process of a CSV/LDIF/VCARD file containing subscription
        addresses from the admin site.
        """

        response = self.admin_import_file(source_file, ignore_errors)

        self.assertContains(response, "<h1>Confirm import</h1>")

        import_confirm_url = reverse(
            'admin:newsletter_subscription_import_confirm'
        )

        return self.client.post(
            import_confirm_url, {'confirm': True}, follow=True
        )

    def test_newsletter_admin(self):
        """
        Testing newsletter admin change list display.
        """
        changelist_url = reverse('admin:newsletter_newsletter_changelist')
        response = self.client.get(changelist_url)
        self.assertContains(
            response,
            '<a href="../message/?newsletter__id__exact=%s">Messages</a>' % self.newsletter.pk
        )
        self.assertContains(
            response,
            '<a href="../subscription/?newsletter__id__exact=%s">Subscriptions</a>' % self.newsletter.pk
        )

    def test_subscription_admin(self):
        """
        Testing subscription admin change list display and actions.
        """
        Subscription.objects.bulk_create([
            Subscription(
                newsletter=self.newsletter, name_field='Sara',
                email_field='sara@example.org', subscribed=True,
            ),
            Subscription(
                newsletter=self.newsletter, name_field='Bob',
                email_field='bob@example.org', unsubscribed=True,
            ),
            Subscription(
                newsletter=self.newsletter, name_field='Khaled',
                email_field='khaled@example.org', subscribed=False,
                unsubscribed=False,
            ),
        ])
        changelist_url = reverse('admin:newsletter_subscription_changelist')
        response = self.client.get(changelist_url)
        self.assertContains(
            response,
            '<img src="/static/newsletter/admin/img/icon-no.gif" width="10" height="10" alt="Unsubscribed"/>',
            html=True
        )
        self.assertContains(
            response,
            '<img src="/static/newsletter/admin/img/icon-yes.gif" width="10" height="10" alt="Subscribed"/>',
            html=True
        )
        self.assertContains(
            response,
            '<img src="/static/newsletter/admin/img/waiting.gif" width="10" height="10" alt="Unactivated"/>',
            html=True
        )

        # Test actions
        response = self.client.post(changelist_url, data={
            'index': 0,
            'action': ['make_subscribed'],
            '_selected_action': [str(Subscription.objects.get(name_field='Khaled').pk)],
        })
        self.assertTrue(Subscription.objects.get(name_field='Khaled').subscribed)

        response = self.client.post(changelist_url, data={
            'index': 0,
            'action': ['make_unsubscribed'],
            '_selected_action': [str(Subscription.objects.get(name_field='Sara').pk)],
        })
        self.assertFalse(Subscription.objects.get(name_field='Sara').subscribed)

    def test_admin_import_get_form(self):
        """ Test Import form. """

        import_url = reverse('admin:newsletter_subscription_import')
        response = self.client.get(import_url)
        self.assertContains(response, "<h1>Import addresses</h1>")

    def test_admin_import_subscribers_csv(self):
        response = self.admin_import_subscribers('addresses.csv')

        self.assertContains(
            response,
            "2 subscriptions have been successfully added."
        )
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

    def test_admin_import_subscribers_ldif(self):
        response = self.admin_import_subscribers('addresses.ldif')

        self.assertContains(
            response,
            "2 subscriptions have been successfully added."
        )
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

    def test_admin_import_subscribers_vcf(self):
        response = self.admin_import_subscribers('addresses.vcf')

        self.assertContains(
            response,
            "2 subscriptions have been successfully added."
        )
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

    def test_admin_import_subscribers_duplicates(self):
        """ Test importing a file with duplicate addresses. """

        with patch_logger('newsletter.addressimport.parsers', 'warning') as messages:
            response = self.admin_import_subscribers(
                'addresses_duplicates.csv', ignore_errors='true'
            )

        self.assertContains(
            response,
            "2 subscriptions have been successfully added."
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

    def test_admin_import_subscribers_existing(self):
        """ Test importing already existing subscriptions. """

        subscription = make_subscription(self.newsletter, 'john@example.org')
        subscription.save()

        with patch_logger('newsletter.addressimport.parsers', 'warning') as messages:
            response = self.admin_import_subscribers(
                'addresses.csv', ignore_errors='true'
            )

        self.assertContains(
            response,
            "1 subscription has been successfully added."
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

        with patch_logger('newsletter.addressimport.parsers', 'warning') as messages:
            response = self.admin_import_file('addresses.csv')

        self.assertContains(
            response,
            "Some entries are already subscribed to."
        )
        self.assertEqual(len(messages), 1)
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

    def test_admin_import_subscribers_permission(self):
        """
        To be able to import subscriptions, user must have the
        'add_subscription' permission.
        """
        self.admin_user.is_superuser = False
        self.admin_user.save()
        import_url = reverse('admin:newsletter_subscription_import')
        response = self.client.get(import_url)
        self.assertEqual(response.status_code, 403)

        self.admin_user.user_permissions.add(
            Permission.objects.get(codename='add_subscription')
        )
        response = self.client.get(import_url)
        self.assertEqual(response.status_code, 200)

    def test_admin_import_subscribers_no_addresses(self):
        """
        Cannot confirm subscribers import if 'addresses' misses in session.
        """
        import_url = reverse('admin:newsletter_subscription_import')
        import_confirm_url = reverse(
            'admin:newsletter_subscription_import_confirm'
        )
        response = self.client.post(
            import_confirm_url, {'confirm': True}
        )
        self.assertRedirects(response, import_url)

    def test_message_admin(self):
        """
        Testing message admin change list display and message previews.
        """
        changelist_url = reverse('admin:newsletter_message_changelist')
        response = self.client.get(changelist_url)
        self.assertContains(
            response,
            '<a href="%d/preview/">Preview</a>' % self.message.pk,
            html=True
        )

        # Previews
        preview_url = reverse('admin:newsletter_message_preview', args=[self.message.pk])
        preview_text_url = reverse('admin:newsletter_message_preview_text', args=[self.message.pk])
        preview_html_url = reverse('admin:newsletter_message_preview_html', args=[self.message.pk])
        response = self.client.get(preview_url)
        self.assertContains(
            response,
            '<iframe src ="%s" width="960px" height="720px"></iframe>' % preview_html_url,
            html=True
        )
        self.assertContains(
            response,
            '<iframe src ="%s" width="960px" height="720px"></iframe>' % preview_text_url,
            html=True
        )

        response = self.client.get(preview_text_url)
        self.assertEqual(
            response.content,
            b'''++++++++++++++++++++

Test Newsletter: Test message

++++++++++++++++++++



++++++++++++++++++++

Unsubscribe: http://example.com/newsletter/test-newsletter/unsubscribe/
''')

        response = self.client.get(preview_html_url)
        self.assertContains(response, '<h1>Test Newsletter</h1>')
        self.assertContains(response, '<h2>Test message</h2>')
        self.assertContains(response, self.newsletter.unsubscribe_url())

        # HTML preview returns 404 if send_html is False
        self.newsletter.send_html = False
        self.newsletter.save()
        response = self.client.get(preview_html_url)
        self.assertEqual(response.status_code, 404)


class SubmissionAdminTests(AdminTestMixin, TestCase):
    """ Tests for Submission admin. """

    def setUp(self):
        super(SubmissionAdminTests, self).setUp()

        self.add_url = reverse('admin:newsletter_submission_add')
        self.changelist_url = reverse('admin:newsletter_submission_changelist')

    def test_changelist(self):
        """ Testing submission admin change list display. """

        # Assure there's a submission
        Submission.from_message(self.message)

        response = self.client.get(self.changelist_url)
        self.assertContains(
            response,
            '<td class="field-admin_status_text">Not sent.</td>'
        )

    def test_duplicate_fail(self):
        """ Test that a message cannot be published twice. """

        # Assure there's a submission
        Submission.from_message(self.message)

        response = self.client.post(self.add_url, data={
            'message': self.message.pk,
            'publish_date_0': '2016-01-09',
            'publish_date_1 ': '07:24',
            'publish': 'on',
        })
        self.assertContains(
            response,
            "This message has already been published in some other submission."
        )

    def test_add(self):
        """ Test adding a Submission. """

        response = self.client.post(self.add_url, data={
            'message': self.message.pk,
            'publish_date_0': '2016-01-09',
            'publish_date_1': '07:24',
            'publish': 'on',
        }, follow=True)

        self.assertContains(response, "added")

        self.assertEqual(Submission.objects.count(), 1)
        submission = Submission.objects.all()[0]

        self.assertEqual(submission.message, self.message)

    def test_add_wrongmessage_regression(self):
        """ Regression test for #170. """

        # Create a second message
        Message.objects.create(
            newsletter=self.newsletter, title='2nd message', slug='test-message-2'
        )

        response = self.client.post(self.add_url, data={
            'message': self.message.pk,
            'publish_date_0': '2016-01-09',
            'publish_date_1': '07:24',
            'publish': 'on',
        }, follow=True)

        self.assertContains(response, "added")

        self.assertEqual(Submission.objects.count(), 1)
        submission = Submission.objects.all()[0]

        self.assertEqual(submission.message, self.message)
