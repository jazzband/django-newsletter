"""Model fields for django-newsletter."""
from django.db.models import ImageField
from django.core.exceptions import ImproperlyConfigured

# Conditional imports as only one Thumbnail app is required
try:
    from sorl.thumbnail.fields import ImageField as SorlImageField
except ImportError:
    pass

try:
    from easy_thumbnails.fields import ThumbnailerImageField
except (ImportError, RuntimeError):
    pass

from .settings import newsletter_settings

# Uses the model field provided by the thumbnailing application
if newsletter_settings.THUMBNAIL == 'sorl-thumbnail':
    ParentClass = SorlImageField
elif newsletter_settings.THUMBNAIL == 'easy-thumbnails':
    ParentClass = ThumbnailerImageField
else:
    raise ImproperlyConfigured('Invalid NEWSLETTER_THUMBNAIL value.')

DynamicImageField = type('DynamicImageField', (ParentClass,), {})
