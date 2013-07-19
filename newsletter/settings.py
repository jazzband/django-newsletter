from django.conf import settings as django_settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured


class NewsletterSettings(object):
    """
    A settings object, that handles newsletter default settings.
    """

    @property
    def RICHTEXT_WIDGET(self):
        # Import and set the richtext field
        NEWSLETTER_RICHTEXT_WIDGET = \
            getattr(django_settings, "NEWSLETTER_RICHTEXT_WIDGET", "")

        if NEWSLETTER_RICHTEXT_WIDGET:
            try:
                module, attr = NEWSLETTER_RICHTEXT_WIDGET.rsplit(".", 1)
                mod = import_module(module)
                return getattr(mod, attr)
            except Exception as e:
                # Catch ImportError and other exceptions too
                # (e.g. user sets setting to an integer)
                raise ImproperlyConfigured(
                    "Error while importing setting "
                    "NEWSLETTER_RICHTEXT_WIDGET %r: %s" % (
                        NEWSLETTER_RICHTEXT_WIDGET, e
                    )
                )

        return None

newsletter_settings = NewsletterSettings()
