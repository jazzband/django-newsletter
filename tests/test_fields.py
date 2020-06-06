"""Tests for the fields module."""
import sys

# Conditional imports for Python 2.7
try:
    from importlib import reload
except ImportError:
    pass

try:
    from unittest.mock import patch, MagicMock, PropertyMock
except ImportError:
    from mock import patch, MagicMock, PropertyMock

from django.core.exceptions import ImproperlyConfigured
from django.db.models import ImageField
from django.test import TestCase

from newsletter import fields

class FieldsTestCase(TestCase):
    class MockSorlThumbnailImageField(object):
        def __init__(self):
            self.parent_class = 'sorl-thumbnail'

    class MockEasyThumbnailsImageField(object):
        def __init__(self):
            self.parent_class = 'easy-thumbnails'

    def setUp(self):
        # Mocks imports for testing
        sys.modules['sorl'] = MagicMock()
        sys.modules['sorl.thumbnail'] = MagicMock()
        sys.modules['sorl.thumbnail.fields'] = MagicMock()
        sys.modules['sorl.thumbnail.fields.ImageField'] = (
            self.MockSorlThumbnailImageField
        )
        sys.modules['easy_thumbnails'] = MagicMock()
        sys.modules['easy_thumbnails.fields'] = MagicMock()
        sys.modules['easy_thumbnails.fields.ThumbnailerImageField'] = (
            self.MockEasyThumbnailsImageField
        )
        # Have to set attributes to get around metaclass conflicts when
        # setting up the Dynamic ImageField
        # https://stackoverflow.com/a/52460876/4521808
        setattr(
            sys.modules['sorl.thumbnail.fields'],
            'ImageField',
            self.MockSorlThumbnailImageField
        )
        setattr(
            sys.modules['easy_thumbnails.fields'],
            'ThumbnailerImageField',
            self.MockEasyThumbnailsImageField
        )

    def tearDown(self):
        # Remove mocked imports to ensure no future test conflicts
        del sys.modules['sorl']
        del sys.modules['sorl.thumbnail']
        del sys.modules['sorl.thumbnail.fields']
        del sys.modules['sorl.thumbnail.fields.ImageField']
        del sys.modules['easy_thumbnails']
        del sys.modules['easy_thumbnails.fields']
        del sys.modules['easy_thumbnails.fields.ThumbnailerImageField']

    @patch(
        'newsletter.settings.NewsletterSettings.THUMBNAIL',
        new_callable=PropertyMock,
    )
    def test_sorl_thumbnail_image_field(self, THUMBNAIL):
        """Tests that sorl-thumbnail image field loads as expected."""
        THUMBNAIL.return_value = 'sorl-thumbnail'

        # Reload fields to redeclare the DynamicImageField=
        reload(fields)

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

        # Reload fields to redeclare the DynamicImageField
        reload(fields)

        # Confirm inheritance from easy-thumbnails ThumbnailerImageField
        image_field = fields.DynamicImageField()
        self.assertEqual(image_field.parent_class, 'easy-thumbnails')
