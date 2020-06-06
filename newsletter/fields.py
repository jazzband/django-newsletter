"""Model fields for django-newsletter."""
from django.db.models import ImageField

# Conditional imports as Thumbnail apps are optional and may not be installed
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
# If no application set, uses the Django ImageField as the fallback
if newsletter_settings.THUMBNAIL == 'sorl-thumbnail':
    ParentClass = SorlImageField
elif newsletter_settings.THUMBNAIL == 'easy-thumbnails':
    ParentClass = ThumbnailerImageField
else:
    ParentClass = ImageField

DynamicImageField = type('DynamicImageField', (ParentClass,), {})