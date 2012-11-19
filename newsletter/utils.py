import logging
logger = logging.getLogger(__name__)

# Conditional import of 'now'
# Django 1.4 should use timezone.now, Django 1.3 datetime.now
try:
    from django.utils.timezone import now
except ImportError:
    logger.warn('Timezone support not enabled.')
    from datetime import datetime
    now = datetime.now
