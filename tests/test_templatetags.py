"""Tests for the templatetags module."""
from io import BytesIO
from shutil import rmtree

# Conditionally import for Python 2.7 support
try:
    from tempfile import TemporaryDirectory as TempDir
except ImportError:
    import tempfile
    TempDir = None

from PIL import Image

from django.core.files.base import File
from django.template import Context, Template
from django.test import override_settings

from newsletter.models import (
    Newsletter, Message, Article, get_default_sites
)
from newsletter.templatetags.newsletter_thumbnails import ThumbnailNode
from .utils import MailTestCase


class TemporaryDirectory:
    """Mimicks TemporaryDirectory to give Python 2 and 3 support."""
    def __init__(self):
        if TempDir:
            temp_dir = TempDir()
            self.name = temp_dir.name
        else:
            self.name = tempfile.mkdtemp()

    def __exit__(self, exc, value, traceback):
        rmtree(self.name)

# Create temporary directory for created media files
TEMP_DIR = TemporaryDirectory()
TEMP_DIR_PATH = TEMP_DIR.name


@override_settings(MEDIA_ROOT=TEMP_DIR_PATH)
class TemplateTestCase(MailTestCase):
    class MockSourceVariable:
        """Mocks the source_variable attribute for testing."""
        def __init__(self, source_image):
            self.source_image = source_image

        def resolve(self, context):
            return self.source_image

    def get_newsletter_kwargs(self):
        """ Returns the keyword arguments for instanciating the newsletter."""
        return {
            'title': 'Test newsletter',
            'slug': 'test-newsletter',
            'sender': 'Test Sender',
            'email': 'test@testsender.com'
        }

    def create_test_image(self, image_name='test-image.png', image_format='PNG'):
        # Create Bytes object to hold image in memory
        image_file = BytesIO()

        # Create a 600 x 600 px image and save to bytes object
        image = Image.new('RGB', size=(600, 600), color=(256, 0, 0))
        image.save(image_file, image_format)

        # Return file pointer to start to allow proper reading
        image_file.seek(0)

        # Return image as a Django File object
        return File(image_file, name=image_name)

    def setUp(self):
        # Create newsletter for testing
        self.newsletter = Newsletter.objects.create(
            **self.get_newsletter_kwargs()
        )
        self.newsletter.site.set(get_default_sites())

        # Add a message to the newsletter
        self.message = Message.objects.create(
            title='Test message',
            newsletter=self.newsletter,
            slug='test-message',
        )

        # Add an article to message
        self.article = Article.objects.create(
            title='Test title',
            text='This is the article text.',
            post=self.message,
            image=self.create_test_image(),
        )

        # Create a thumbnail node for tests
        self.node = ThumbnailNode(
            self.MockSourceVariable(self.article.image), 'thumbnail'
        )

    def test_node_create_path(self):
        """Confirms that thumbnail path works as expected."""
        path = self.node._create_thumbnail_file_path(self.article.image.name)

        # TODO: Update to assertRegex when Python 2.7 support dropped
        self.assertRegexpMatches(
            path,
            r'newsletter(\/|\\)images(\/|\\).*test-image.*_thumbnail\.png',
        )

    def test_node_pillow_format(self):
        """Confirms that node can parse image formats for Pillow properly."""
        # Test for JPEG images
        jpg_test = self.node._get_pillow_format('thumbnail.jpg')
        self.assertEqual(jpg_test, 'JPEG')

        # Test for PNG images
        png_test = self.node._get_pillow_format('thumbnail.png')
        self.assertEqual(png_test, 'PNG')

    def test_node_create_thumbnail_jpg(self):
        """Confirms that node can thumbnail JPEG images."""
        # Create image and assign to article
        original_image = self.create_test_image('test-image.jpg', image_format='JPEG')
        self.article.image = original_image
        self.article.save()

        # Test that thumbnail works for image
        thumbnail_url = self.node._get_or_create_thumbnail(self.article.image)

        # TODO: Update to assertRegex when Python 2.7 support dropped
        self.assertRegexpMatches(
            thumbnail_url,
            r'newsletter(\/|\\)images(\/|\\).*test-image.*_thumbnail\.jpg',
        )

    def test_node_create_thumbnail_png(self):
        """Confirms that node can thumbnail PNG images."""
        # Create image and assign to article
        original_image = self.create_test_image('test-image.png', image_format='PNG')
        self.article.image = original_image
        self.article.save()

        # Test that thumbnail works for image
        thumbnail_url = self.node._get_or_create_thumbnail(self.article.image)

        # TODO: Update to assertRegex when Python 2.7 support dropped
        self.assertRegexpMatches(
            thumbnail_url,
            r'newsletter(\/|\\)images(\/|\\).*test-image.*_thumbnail\.png',
        )

    def test_node_create_thumbnail_gif(self):
        """Confirms that node can thumbnail GIF images."""
        # Create image and assign to article
        original_image = self.create_test_image('test-image.gif', image_format='GIF')
        self.article.image = original_image
        self.article.save()

        # Test that thumbnail works for image
        thumbnail_url = self.node._get_or_create_thumbnail(self.article.image)

        # TODO: Update to assertRegex when Python 2.7 support dropped
        self.assertRegexpMatches(
            thumbnail_url,
            r'newsletter(\/|\\)images(\/|\\).*test-image.*_thumbnail\.gif',
        )

    def test_node_create_thumbnail_bmp(self):
        """Confirms that node can thumbnail BMP images."""
        # Create image and assign to article
        original_image = self.create_test_image('test-image.bmp', image_format='BMP')
        self.article.image = original_image
        self.article.save()

        # Test that thumbnail works for image
        thumbnail_url = self.node._get_or_create_thumbnail(self.article.image)

        # TODO: Update to assertRegex when Python 2.7 support dropped
        self.assertRegexpMatches(
            thumbnail_url,
            r'newsletter(\/|\\)images(\/|\\).*test-image.*_thumbnail\.bmp',
        )

    def test_node_create_thumbnail_tiff(self):
        """Confirms that node can thumbnail TIFF images."""
        # Create image and assign to article
        original_image = self.create_test_image('test-image.tiff', image_format='TIFF')
        self.article.image = original_image
        self.article.save()

        # Test that thumbnail works for image
        thumbnail_url = self.node._get_or_create_thumbnail(self.article.image)

        # TODO: Update to assertRegex when Python 2.7 support dropped
        self.assertRegexpMatches(
            thumbnail_url,
            r'newsletter(\/|\\)images(\/|\\).*test-image.*_thumbnail\.tiff',
        )

    def test_node_render_returns_empty_string(self):
        """Confirms node render method returns empty string."""
        render_return = self.node.render({})

        self.assertEqual(render_return, '')
        self.assertIsInstance(render_return, str)

    def test_tag_outputs_thubmnail_url(self):
        """Confirms an expected image URL is provided."""
        template = Template(
            '{% load newsletter_thumbnails %}'
            '{% for article in message.articles.all %}'
            '{% newsletter_thumbnail article.image as thumbnail %}'
            '{{ thumbnail }}'
            '{% endfor %}'
        ).render(
            Context({'message': self.message})
        )

        # TODO: Update to assertRegex when Python 2.7 support dropped
        self.assertRegexpMatches(
            template,
            r'newsletter(\/|\\)images(\/|\\).*test-image.*_thumbnail\.png',
        )