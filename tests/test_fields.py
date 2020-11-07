"""Tests for the fields module."""
import sys
from importlib import reload
from unittest.mock import patch, MagicMock, PropertyMock

from django.core.exceptions import ImproperlyConfigured
from django.db.models import ImageField
from django.test import TestCase

from newsletter import fields

class FieldsTestCase(TestCase):
    class MockSorlThumbnailImageField:
        def __init__(self):
            self.parent_class = 'sorl-thumbnail'

    class MockEasyThumbnailsImageField:
        def __init__(self):
            self.parent_class = 'easy-thumbnails'

    def clear_imports(self):
        """Removes imported modules to ensure proper test environment.

            Need to set import to None because otherwise Python will
            automatically re-import them when called during testing.
        """
        sys.modules['sorl'] = None
        sys.modules['sorl.thumbnail'] = None
        sys.modules['sorl.thumbnail.fields'] = None
        sys.modules['sorl.thumbnail.fields.ImageField'] = None
        sys.modules['easy_thumbnails'] = None
        sys.modules['easy_thumbnails.fields'] = None
        sys.modules['easy_thumbnails.fields.ThumbnailerImageField'] = None

    def mock_sorl_import(self):
        """Mocks import of sorl-thumbnail AdminImageMixin."""
        sys.modules['sorl'] = MagicMock()
        sys.modules['sorl.thumbnail'] = MagicMock()
        sys.modules['sorl.thumbnail.fields'] = MagicMock()
        sys.modules['sorl.thumbnail.fields.ImageField'] = (
            self.MockSorlThumbnailImageField
        )

        # Have to set attributes to get around metaclass conflicts when
        # setting up DynamicImageField
        # https://stackoverflow.com/a/52460876/4521808
        setattr(
            sys.modules['sorl.thumbnail.fields'],
            'ImageField',
            self.MockSorlThumbnailImageField
        )

    def mock_easy_thumbnails_import(self):
        """Mocks import of easy-thumbnails ImageClearableFileInput."""
        sys.modules['easy_thumbnails'] = MagicMock()
        sys.modules['easy_thumbnails.fields'] = MagicMock()
        sys.modules['easy_thumbnails.fields.ThumbnailerImageField'] = (
            self.MockEasyThumbnailsImageField
        )

        # Have to set attributes to get around metaclass conflicts when
        # setting up the DynamicImageField
        # https://stackoverflow.com/a/52460876/4521808
        setattr(
            sys.modules['easy_thumbnails.fields'],
            'ThumbnailerImageField',
            self.MockEasyThumbnailsImageField
        )

    def tearDown(self):
        self.clear_imports()

    @patch(
        'newsletter.settings.NewsletterSettings.THUMBNAIL',
        new_callable=PropertyMock,
    )
    def test_sorl_thumbnail_image_field(self, THUMBNAIL):
        """Tests that sorl-thumbnail image field loads as expected."""
        THUMBNAIL.return_value = 'sorl-thumbnail'

        # Reload fields to re-declare the DynamicImageField
        self.clear_imports()
        self.mock_sorl_import()

        # Confirm inheritance from sorl-thubmnail ImageField
        image_field = fields.DynamicImageField()
        self.assertTrue(image_field.parent_class, 'sorl-thubmnail')

    @patch(
        'newsletter.settings.NewsletterSettings.THUMBNAIL',
        new_callable=PropertyMock,
    )
    def test_easy_thumbnails_image_field(self, THUMBNAIL):
        """Tests that easy-thumbnails image field loads as expected."""
        THUMBNAIL.return_value = 'easy-thumbnails'

        # Reload fields to re-declare the DynamicImageField
        self.clear_imports()
        self.mock_easy_thumbnails_import()
        reload(fields)

        # Confirm inheritance from easy-thumbnails ThumbnailerImageField
        image_field = fields.DynamicImageField()
        self.assertEqual(image_field.parent_class, 'easy-thumbnails')

    @patch(
        'newsletter.settings.NewsletterSettings.THUMBNAIL',
        new_callable=PropertyMock,
    )
    def test_error_on_no_thumbnail(self, THUMBNAIL):
        """Tests that error occurs if no thumbnailer specified."""
        THUMBNAIL.return_value = None

        # Reload fields to re-declare the DynamicImageField
        try:
            self.clear_imports()
            reload(fields)
        except ImproperlyConfigured as error:
            self.assertEqual(str(error), 'Invalid NEWSLETTER_THUMBNAIL value.')
        else:
            self.assertTrue(False)
