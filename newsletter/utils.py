import logging
logger = logging.getLogger(__name__)

import random

from django.utils.hashcompat import sha_constructor
from django.contrib.sites.models import Site

from datetime import datetime

# Conditional import of 'now'
# Django 1.4 should use timezone.now, Django 1.3 datetime.now
try:
    from django.utils.timezone import now
except ImportError:
    logger.warn('Timezone support not enabled.')
    now = datetime.now


# Generic helper functions
def make_activation_code():
    """ Generate a unique activation code. """
    random_string = str(random.random())
    random_digest = sha_constructor(random_string).hexdigest()[:5]
    time_string = str(datetime.now().microsecond)

    combined_string = random_digest + time_string

    return sha_constructor(combined_string).hexdigest()


def get_default_sites():
    """ Get a list of id's for all sites; the default for newsletters. """
    return [site.id for site in Site.objects.all()]
