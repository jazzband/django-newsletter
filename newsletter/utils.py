""" Generic helper functions """

import logging
logger = logging.getLogger(__name__)

import random

from datetime import datetime
from hashlib import sha1

from django.contrib.sites.models import Site
from django.utils.encoding import force_bytes

# Possible actions that user can perform
ACTIONS = ('subscribe', 'unsubscribe', 'update')


def make_activation_code():
    """ Generate a unique activation code. """
    random_string = str(random.random())
    random_digest = sha1(force_bytes(random_string)).hexdigest()[:5]
    time_string = str(datetime.now().microsecond)

    combined_string = random_digest + time_string

    return sha1(force_bytes(combined_string)).hexdigest()


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
