import os

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from newsletter import admin  # Triggers model admin registration
from newsletter.models import Newsletter

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

    def admin_import_subscribers(self, source_file, ignore_errors=''):
        """
        Import process of a CSV/LDIF/VCARD file containing subscription
        addresses from the admin site.
        """
        import_url = reverse('admin:newsletter_subscription_import')

        with open(source_file, 'rb') as fh:
            response = self.client.post(import_url, {
                'newsletter': self.newsletter.pk,
                'address_file': fh,
                'ignore_errors': ignore_errors,
            }, follow=True)

        self.assertContains(response, "<h1>Confirm import</h1>")

        import_confirm_url = reverse(
            'admin:newsletter_subscription_import_confirm'
        )
        response = self.client.post(
            import_confirm_url, {'confirm': True}, follow=True
        )
        self.assertContains(
            response,
            "2 subscriptions have been successfully added."
        )
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

    def test_admin_import_form(self):
        """ Test Import form. """

        import_url = reverse('admin:newsletter_subscription_import')
        response = self.client.get(import_url)
        self.assertContains(response, "<h1>Import addresses</h1>")

    def test_admin_import_subscribers_csv(self):
        source_file = os.path.join(test_files_dir, 'addresses.csv')
        self.admin_import_subscribers(source_file)

    def test_admin_import_subscribers_ldif(self):
        source_file = os.path.join(test_files_dir, 'addresses.ldif')
        self.admin_import_subscribers(source_file)

    def test_admin_import_subscribers_vcf(self):
        source_file = os.path.join(test_files_dir, 'addresses.vcf')
        self.admin_import_subscribers(source_file)

    def test_admin_import_subscribers_duplicates(self):
        """ Test importing a file with duplicate addresses. """
        source_file = os.path.join(test_files_dir, 'addresses_duplicates.csv')

        self.admin_import_subscribers(source_file, ignore_errors='true')
