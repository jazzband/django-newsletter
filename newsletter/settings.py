from django.conf import settings as django_settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured


class NewsletterSettings(object):
    """
    A settings object, that handles newsletter default settings.

    With instance being instance of NewsletterSettings,
    accessing instance.SETTING_NAME returns NEWSLETTER_SETTING_NAME,
    if it's defined in project, or instance.DEFAULT_SETTING_NAME if not.

    DEFAULT_SETTING_NAME can be a class variable or a property if needed.

    SETTING_NAME can be overridden if above behavior is not adequate.
    """

    def __getattr__(self, attr):
        return getattr(
            django_settings,
            'NEWSLETTER_%s' % attr,
            getattr(self, 'DEFAULT_%s' % attr)
        )

    DEFAULT_CONFIRM_EMAIL = True

    @property
    def DEFAULT_CONFIRM_EMAIL_SUBSCRIBE(self):
        return self.CONFIRM_EMAIL

    @property
    def DEFAULT_CONFIRM_EMAIL_UNSUBSCRIBE(self):
        return self.CONFIRM_EMAIL

    @property
    def DEFAULT_CONFIRM_EMAIL_UPDATE(self):
        return self.CONFIRM_EMAIL

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
