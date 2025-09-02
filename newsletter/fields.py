"""Model fields for django-newsletter."""
from django.core.exceptions import ImproperlyConfigured
from .settings import newsletter_settings

# Uses the model field provided by the thumbnailing application
if newsletter_settings.THUMBNAIL == 'sorl-thumbnail':
    from sorl.thumbnail.fields import ImageField as SorlImageField
    ParentClass = SorlImageField
elif newsletter_settings.THUMBNAIL == 'easy-thumbnails':
    from easy_thumbnails.fields import ThumbnailerImageField
    ParentClass = ThumbnailerImageField
else:
    raise ImproperlyConfigured('Invalid NEWSLETTER_THUMBNAIL value.')

DynamicImageField = type('DynamicImageField', (ParentClass,), {})
