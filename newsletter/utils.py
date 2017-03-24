""" Generic helper functions """

import logging


from django.contrib.sites.models import Site
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)


# Possible actions that user can perform
ACTIONS = ('subscribe', 'unsubscribe', 'update')


def make_activation_code():
    """ Generate a unique activation code. """

    # Use Django's crypto get_random_string() instead of rolling our own.
    return get_random_string(length=40)


def get_default_sites():
    """ Get a list of id's for all sites; the default for newsletters. """
    return [site.id for site in Site.objects.all()]


class Singleton(type):
    """
    Singleton metaclass.
    Source:
    http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )

        return cls._instances[cls]
