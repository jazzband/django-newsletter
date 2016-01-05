import os

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from newsletter import admin  # Triggers model admin registration
from newsletter.models import Newsletter
from newsletter.admin_utils import make_subscription

test_files_dir = os.path.join(os.path.dirname(__file__), 'files')


class AdminTestCase(TestCase):
    def setUp(self):
        super(AdminTestCase, self).setUp()
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

        response = self.admin_import_subscribers(
            'addresses_duplicates.csv', ignore_errors='true'
        )

        self.assertContains(
            response,
            "2 subscriptions have been successfully added."
        )
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

    def test_admin_import_subscribers_existing(self):
        """ Test importing already existing subscriptions. """

        subscription = make_subscription(self.newsletter, 'john@example.org')
        subscription.save()

        response = self.admin_import_subscribers(
            'addresses.csv', ignore_errors='true'
        )

        self.assertContains(
            response,
            "1 subscriptions have been successfully added."
        )
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

        response = self.admin_import_file('addresses.csv')

        self.assertContains(
            response,
            "Some entries are already subscribed to."
        )
        self.assertEqual(self.newsletter.subscription_set.count(), 2)
