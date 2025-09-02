import os
import sys
import django
from importlib import reload
from unittest.mock import patch, MagicMock, PropertyMock

from django.contrib import admin as django_admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from newsletter import admin  # Triggers model admin registration
from newsletter.admin_utils import make_subscription
from newsletter.models import Message, Newsletter, Submission, Subscription, Attachment, attachment_upload_to

test_files_dir = os.path.join(os.path.dirname(__file__), 'files')


class AdminTestMixin:
    def setUp(self):
        super().setUp()

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
        self.message_with_attachment = Message.objects.create(
            newsletter=self.newsletter, title='Test message with attachment', slug='test-message-with-attachment'
        )
        self.attachment = Attachment.objects.create(file=os.path.join('tests', 'files', 'sample.txt'),
                                                    message=self.message_with_attachment)


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
        self.assertContains(response, "<li>Jill Martin &lt;jill@example.org&gt;</li>")

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
            '<a href="/admin/newsletter/message/?newsletter__id=%s">Messages</a>' % self.newsletter.pk
        )
        self.assertContains(
            response,
            '<a href="/admin/newsletter/subscription/?newsletter__id=%s">Subscriptions</a>' % self.newsletter.pk
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

        with self.assertLogs('newsletter.addressimport.parsers', 'WARNING') as messages:
            response = self.admin_import_subscribers(
                'addresses_duplicates.csv', ignore_errors='true'
            )

        self.assertContains(
            response,
            "2 subscriptions have been successfully added."
        )
        self.assertEqual(len(messages.output), 2)
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

    def test_admin_import_subscribers_existing(self):
        """ Test importing already existing subscriptions. """

        subscription = make_subscription(self.newsletter, 'john@example.org')
        subscription.save()

        with self.assertLogs('newsletter.addressimport.parsers', 'WARNING') as messages:
            response = self.admin_import_subscribers(
                'addresses.csv', ignore_errors='true'
            )

        self.assertContains(
            response,
            "1 subscription has been successfully added."
        )
        self.assertEqual(len(messages.output), 1)
        self.assertEqual(self.newsletter.subscription_set.count(), 2)

        with self.assertLogs('newsletter.addressimport.parsers', 'WARNING') as messages:
            response = self.admin_import_file('addresses.csv')

        self.assertContains(
            response,
            "Some entries are already subscribed to."
        )
        self.assertEqual(len(messages.output), 1)
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
            '<a href="/admin/newsletter/message/%d/preview/">Preview</a>' % self.message.pk,
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

        response_content = self.client.get(preview_text_url).content.decode('utf-8')
        self.assertIn('Test Newsletter: Test message', response_content)
        self.assertIn(self.newsletter.unsubscribe_url(), response_content)

        response = self.client.get(preview_html_url)
        self.assertContains(response, '<h1>Test Newsletter</h1>')
        self.assertContains(response, '<h2>Test message</h2>')
        self.assertContains(response, self.newsletter.unsubscribe_url())

        # HTML preview returns 404 if send_html is False
        self.newsletter.send_html = False
        self.newsletter.save()
        response = self.client.get(preview_html_url)
        self.assertEqual(response.status_code, 404)

    def test_message_with_attachment_admin(self):
        """
        Testing message with attachment admin change list display.
        """
        self.assertEqual(Message.objects.count(), 2)

        message_with_a = Message.objects.last()
        self.assertEqual(message_with_a.attachments.count(), 1)

        upload_to = attachment_upload_to(self.attachment, 'sample.txt')
        self.assertEqual(os.path.split(upload_to)[1], 'sample.txt')

        change_url = reverse('admin:newsletter_message_change', args=(self.message_with_attachment.pk,))
        response = self.client.get(change_url)

        if django.VERSION[0] >= 5:
            self.assertContains(response, '<h2 id="attachments-heading" class="inline-heading">Attachments</h2>', html=True)
        else:
            self.assertContains(response, '<h2>Attachments</h2>', html=True)
        self.assertContains(response, '<a href="/tests/files/sample.txt">tests/files/sample.txt</a>', html=True)


class MessageAdminTests(AdminTestMixin, TestCase):
    """ Tests for Message admin. """

    def test_add_existing_message_regression(self):
        """ Regression test for #322. """

        # ToDo(frennkie) is there a more elegant way to handle the inlines?!
        response = self.client.post(reverse('admin:newsletter_message_add'), data={
            'title': self.message.title,
            'slug': self.message.slug,
            'newsletter': self.message.newsletter.id,
            'articles-TOTAL_FORMS': 3,
            'articles-INITIAL_FORMS': 1,
            'articles-MIN_NUM_FORMS': 0,
            'articles-MAX_NUM_FORMS': 1000,
            'attachments-TOTAL_FORMS': 3,
            'attachments-INITIAL_FORMS': 1,
            'attachments-MIN_NUM_FORMS': 0,
            'attachments-MAX_NUM_FORMS': 1000,
            '_saveasnew': 'Save as new'
        }, follow=True)

        self.assertContains(response, "Message with this Slug and Newsletter already exists.")


class SubmissionAdminTests(AdminTestMixin, TestCase):
    """ Tests for Submission admin. """

    def setUp(self):
        super().setUp()

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
            'publish_date_1': '07:24',
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

    def test_add_existing_submission_regression(self):
        """ Regression test for #322. """

        # create a third message
        message = Message.objects.create(
            newsletter=self.newsletter, title='3nd message', slug='test-message-3'
        )

        # create submission for third message and add it
        response = self.client.post(self.add_url, data={
            'message': message.pk,
            'publish_date_0': '2020-10-30',
            'publish_date_1': '07:24',
            'publish': 'on',
        }, follow=True)

        self.assertContains(response, "added")

        # try to add a submission for third message again
        # -> this will cause a validation error and print a warning
        response = self.client.post(
            reverse('admin:newsletter_submission_change', kwargs={'object_id': 3}), data={
                'message': message.pk,
                'publish_date_0': '2020-10-30',
                'publish_date_1': '07:24',
                'publish': 'on',
                '_saveasnew': 'Save as new'
            }, follow=True)

        self.assertContains(response, "This message has already been published in some other submission. "
                                      "Messages can only be published once.")


class ArticleInlineTests(TestCase):
    class MockSorlAdminImageMixin:
        def __init__(self):
            self.parent_class = 'sorl-thumbnail'

    def clear_imports(self):
        """Removes imported modules to ensure proper test environment.

            Need to set import to None because otherwise Python will
            automatically re-import them when called during testing.
        """
        sys.modules['sorl'] = None
        sys.modules['sorl.thumbnail'] = None
        sys.modules['sorl.thumbnail.admin'] = None
        sys.modules['sorl.thumbnail.admin.AdminImageMixin'] = None
        sys.modules['easy_thumbnails'] = None
        sys.modules['easy_thumbnails.widgets'] = None
        sys.modules['easy_thumbnails.widgets.ImageClearableFileInput'] = None

    def mock_sorl_import(self):
        """Mocks import of sorl-thumbnail AdminImageMixin."""
        sys.modules['sorl'] = MagicMock()
        sys.modules['sorl.thumbnail'] = MagicMock()
        sys.modules['sorl.thumbnail.admin'] = MagicMock()
        sys.modules['sorl.thumbnail.admin.AdminImageMixin'] = (
            self.MockSorlAdminImageMixin
        )

        # Have to set attributes to get around metaclass conflicts when
        # setting up ArticleInlineClassTuple
        # https://stackoverflow.com/a/52460876/4521808
        setattr(
            sys.modules['sorl.thumbnail.admin'],
            'AdminImageMixin',
            self.MockSorlAdminImageMixin
        )

    def mock_easy_thumbnails_import(self):
        """Mocks import of easy-thumbnails ImageClearableFileInput."""
        sys.modules['easy_thumbnails'] = MagicMock()
        sys.modules['easy_thumbnails.widgets'] = MagicMock()
        sys.modules['easy_thumbnails.widgets.ImageClearableFileInput'] = MagicMock()

    def setUp(self):
        # Unregister models first to avoid an AlreadyRegistered error when
        # reloading the admin for tests
        django_admin.site.unregister(Newsletter)
        django_admin.site.unregister(Submission)
        django_admin.site.unregister(Message)
        django_admin.site.unregister(Subscription)

    def tearDown(self):
        self.clear_imports()

    @patch(
        'newsletter.settings.NewsletterSettings.THUMBNAIL',
        new_callable=PropertyMock,
    )
    def test_sorl_thumbails_admin_added(self, THUMBNAIL):
        """Tests that sorl-thumbnail admin mixin loads as expected."""
        THUMBNAIL.return_value = 'sorl-thumbnail'

        # Reset imported sys modules
        self.clear_imports()
        self.mock_sorl_import()

        # Reload fields to re-declare ArticleInlineClassTuple
        reload(admin)

        # Confirm sorl-thumbnail admin details added (tests for the
        # patched class as sorl-thumbnail is not installed)
        self.assertEqual(
            admin.ArticleInlineClassTuple[0], self.MockSorlAdminImageMixin
        )

        # Get key names from formfield_overrides for easier testing
        key_names = [
            key.__name__ for key in admin.ArticleInline.formfield_overrides
        ]

        # Confirm easy-thumbnails details not added
        self.assertNotIn('DynamicImageField', key_names)

    @patch(
        'newsletter.settings.NewsletterSettings.THUMBNAIL',
        new_callable=PropertyMock,
    )
    def test_easy_thumbails_admin_added(self, THUMBNAIL):
        """Tests that easy-thumbnials Admin widget loads as expected."""
        THUMBNAIL.return_value = 'easy-thumbnails'

        # Reset imported sys modules
        self.clear_imports()
        self.mock_easy_thumbnails_import()

        # Reload fields to re-declare ArticleInline
        reload(admin)

        # Get key names from formfield_overrides for easier testing
        key_names = [
            key.__name__ for key in admin.ArticleInline.formfield_overrides
        ]

        # Confirm easy-thumbnails details are added=
        self.assertIn('DynamicImageField', key_names)

        # Confirm sorl-thumbnail admin details not added
        self.assertEqual(
            admin.ArticleInlineClassTuple[0].__name__, 'StackedInline'
        )
