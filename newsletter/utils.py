""" Generic helper functions """
import logging
import random
from datetime import datetime
from django import VERSION
from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)

try:
    from hashlib import sha1
except ImportError:
    from django.utils.hashcompat import sha_constructor as sha1

# Possible actions that user can perform
ACTIONS = ('subscribe', 'unsubscribe', 'update')


def get_user_model():
    """ get_user_model compatibility wrapper. Returns active User model. """

    # Django 1.7 and above
    if VERSION[0] == 1 and VERSION[1] > 6:
        from django.conf import settings
        return settings.AUTH_USER_MODEL

    try:
        from django.contrib.auth import get_user_model
    except ImportError:
        # Django < v1.5
        from django.contrib.auth.models import User
    else:
        User = get_user_model()

    return User


def make_activation_code():
    """ Generate a unique activation code. """
    random_string = str(random.random())
    random_digest = sha1(random_string).hexdigest()[:5]
    time_string = str(datetime.now().microsecond)

    combined_string = random_digest + time_string

    return sha1(combined_string).hexdigest()


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
