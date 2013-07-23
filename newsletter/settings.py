from django.conf import settings as django_settings
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured


class Settings(object):
    """
    A settings object that proxies newsletter settings and handles defaults,
    inspired by `django-appconf` and the way it works in `django-rest-framework`.

    By default, a single instance of this class is created as `<app>_settings`,
    from which `<APP>_SETTING_NAME` can be accessed as `SETTING_NAME`, i.e.::

        from newsletter.settings import newsletter_settings

        if newsletter_settings.SETTING_NAME:
            # DO FUNKY DANCE

    If a setting has not been explicitly defined in Django's settings, defaults
    can be specified as `_DEFAULT_SETTING_NAME` class variable or property.
    """

    def __init__(self, prefix=None):
        """
        Set app specific prefix, either from __init__ argument or class variable.
        """
        if prefix:
            self.settings_prefix = prefix
        else:
            assert hasattr(self, 'settings_prefix'), 'No settings prefix specified.'

    def __getattr__(self, attr):
        """
        Return Django setting `PREFIX_SETTING` if explicitly specified, otherwise
        return `PREFIX_SETTING_DEFAULT` if specified.
        """

        assert attr.isupper(), 'Requested setting contains lower case characters.'

        if attr.startswith('_DEFAULT_'):
            raise AttributeError(
                '%r object has no attribute %r' % (type(self).__name__, attr)
            )

        # Explicit `try: ... except AttributeError: ...`,
        # instead of third argument of getattr is used intentionally
        # to prevent premature execution of getattr(self, '_DEFAULT_%s' % attr).
        try:
            return getattr(
                django_settings, '%s_%s' % (self.settings_prefix, attr)
            )
        except AttributeError:
            # `django.conf.settings.<APP>_SETTING_NAME` not found
            # return default value.
            return getattr(self, '_DEFAULT_%s' % attr)


class NewsletterSettings(Settings):
    """ Django-newsletter specific settings. """
    settings_prefix = 'NEWSLETTER'

    _DEFAULT_CONFIRM_EMAIL = True

    @property
    def _DEFAULT_CONFIRM_EMAIL_SUBSCRIBE(self):
        return self.CONFIRM_EMAIL

    @property
    def _DEFAULT_CONFIRM_EMAIL_UNSUBSCRIBE(self):
        return self.CONFIRM_EMAIL

    @property
    def _DEFAULT_CONFIRM_EMAIL_UPDATE(self):
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
