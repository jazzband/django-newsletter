from django.conf import settings as django_settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

from .utils import Singleton


class Settings(object):
    """
    A settings object that proxies settings and handles defaults, inspired
    by `django-appconf` and the way it works  in `django-rest-framework`.

    By default, a single instance of this class is created as `<app>_settings`,
    from which `<APP>_SETTING_NAME` can be accessed as `SETTING_NAME`, i.e.::

        from myapp.settings import myapp_settings

        if myapp_settings.SETTING_NAME:
            # DO FUNKY DANCE

    If a setting has not been explicitly defined in Django's settings, defaults
    can be specified as `DEFAULT_SETTING_NAME` class variable or property.
    """

    __metaclass__ = Singleton

    def __init__(self):
        """
        Assert app-specific prefix.
        """
        assert hasattr(self, 'settings_prefix'), 'No prefix specified.'

    def __getattr__(self, attr):
        """
        Return Django setting `PREFIX_SETTING` if explicitly specified,
        otherwise return `PREFIX_SETTING_DEFAULT` if specified.
        """

        if attr.isupper():
            # Require settings to have uppercase characters

            try:
                setting = getattr(
                    django_settings,
                    '%s_%s' % (self.settings_prefix, attr),
                )
            except AttributeError:
                if not attr.startswith('DEFAULT_'):
                    setting = getattr(self, 'DEFAULT_%s' % attr)
                else:
                    raise

            return setting

        else:
            # Default behaviour
            raise AttributeError(
                'No setting or default available for \'%s\'' % attr
            )


class NewsletterSettings(Settings):
    """ Django-newsletter specific settings. """
    settings_prefix = 'NEWSLETTER'

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
        NEWSLETTER_RICHTEXT_WIDGET = getattr(
            django_settings, "NEWSLETTER_RICHTEXT_WIDGET", ""
        )

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
