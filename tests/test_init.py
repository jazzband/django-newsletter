from django.test import TestCase
from importlib.metadata import version, PackageNotFoundError
from . import __version__

class TestNewsletterInit(TestCase):

    def test_version(self):
        try:
            expected_version = version("django-newsletter")
        except PackageNotFoundError:
            expected_version = None
        self.assertEqual(__version__, expected_version)
