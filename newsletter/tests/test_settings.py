from django.utils import unittest

from django.conf import settings

from django.test import TestCase
from django.test.utils import override_settings

from django.core.exceptions import ImproperlyConfigured

from newsletter.settings import newsletter_settings


class SettingsTestCase(TestCase):
    @override_settings(NEWSLETTER_RICHTEXT_WIDGET='banana.nowaythisexists')
    def test_editor_nonexistent(self):
        """
        Setting nonexistant newsletter widget yields ImproperlyConfigured.
        """

        self.assertRaises(
            ImproperlyConfigured, lambda: newsletter_settings.RICHTEXT_WIDGET
        )

    @unittest.skipUnless(
        # Only run tests when TinyMCE is available
        'tinymce' in settings.INSTALLED_APPS,
        'django-tinymce not available for testing.'
    )
    @override_settings(
        # Filter imperavi from editors so just tinymce is left
        INSTALLED_APPS=filter(
            lambda app: app != 'imperavi', settings.INSTALLED_APPS
        ),
        NEWSLETTER_RICHTEXT_WIDGET='tinymce.widgets.TinyMCE'
    )
    def test_editor_tinymce(self):
        """
        Test explicit setting TinyMCE as editor.
        """

        from tinymce.widgets import TinyMCE
        self.assertEquals(newsletter_settings.RICHTEXT_WIDGET, TinyMCE)

    @unittest.skipUnless(
        # Only run tests when TinyMCE is available
        'imperavi' in settings.INSTALLED_APPS,
        'django-imperavi not available for testing.'
    )
    @override_settings(
        # Filter tinymce from editors so just imparavi is left
        INSTALLED_APPS=filter(
            lambda app: app != 'tinymce', settings.INSTALLED_APPS
        ),
        NEWSLETTER_RICHTEXT_WIDGET='imperavi.widget.ImperaviWidget'
    )
    def test_editor_imperavi(self):
        """
        Test explicit setting Imperavi as editor.
        """

        from imperavi.admin import ImperaviWidget
        self.assertEquals(newsletter_settings.RICHTEXT_WIDGET, ImperaviWidget)

    @unittest.skipIf(
        hasattr(settings, 'NEWSLETTER_CONFIRM_EMAIL_SUBSCRIBE') or
        hasattr(settings, 'NEWSLETTER_CONFIRM_EMAIL_UNSUBSCRIBE') or
        hasattr(settings, 'NEWSLETTER_CONFIRM_EMAIL_UPDATE'),
        'Confirmation e-mail defaults overridden by Django settings.'
    )
    def test_confirm_default(self):
        """
        Test whether e-mail confirmation defaults come through.
        """
        self.assertTrue(newsletter_settings.CONFIRM_EMAIL_SUBSCRIBE)
        self.assertTrue(newsletter_settings.CONFIRM_EMAIL_UNSUBSCRIBE)
        self.assertTrue(newsletter_settings.CONFIRM_EMAIL_UPDATE)

    @override_settings(
        NEWSLETTER_CONFIRM_EMAIL_SUBSCRIBE=False
    )
    def test_confirm_subscribe_override(self):
        """
        Test whether e-mail confirmation overrides come through.
        """
        self.assertFalse(newsletter_settings.CONFIRM_EMAIL_SUBSCRIBE)

    @override_settings(
        NEWSLETTER_CONFIRM_EMAIL_UNSUBSCRIBE=False
    )
    def test_confirm_unsubscribe_override(self):
        """
        Test whether e-mail confirmation overrides come through.
        """
        self.assertFalse(newsletter_settings.CONFIRM_EMAIL_UNSUBSCRIBE)

    @override_settings(
        NEWSLETTER_CONFIRM_EMAIL_UPDATE=False
    )
    def test_confirm_update_override(self):
        """
        Test whether e-mail confirmation overrides come through.
        """
        self.assertFalse(newsletter_settings.CONFIRM_EMAIL_UPDATE)
