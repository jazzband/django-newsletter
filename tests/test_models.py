from django.test import TestCase

from newsletter.models import Newsletter


class CustomNewsletter(Newsletter):
    class Meta:
        app_label = 'name_of_my_app'


class ModelTestCase(TestCase):
    """ Test case for models. """

    def test_newsletter_label_name(self):
        """ Test that _meta returns correct app_label and model_name. """
        self.assertEqual(Newsletter._meta.app_label, 'newsletter')
        self.assertEqual(Newsletter._meta.model_name, 'newsletter')

        obj = Newsletter()
        self.assertEqual(obj._meta.app_label, 'newsletter')
        self.assertEqual(obj._meta.model_name, 'newsletter')

        custom_obj = CustomNewsletter()
        self.assertEqual(custom_obj._meta.app_label, 'name_of_my_app')
        self.assertEqual(custom_obj._meta.model_name, 'customnewsletter')
