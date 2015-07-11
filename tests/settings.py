DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.sites',
    'django_extensions',
    'sorl.thumbnail',
    'imperavi',
    'tinymce',
    'newsletter'
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

try:
    # If available, South is required by setuptest
    import south
    INSTALLED_APPS.append('south')
except ImportError:
    # South not installed and hence is not required
    pass

ROOT_URLCONF = 'tests.urls'

SITE_ID = 1

TEMPLATE_DIRS = ('templates', )

# Enable time-zone support for Django 1.4 (ignored in older versions)
USE_TZ = True

# Required for django-webtest to work
STATIC_URL = '/static/'

# Random secret key
import random
key_chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
SECRET_KEY = ''.join([
    random.SystemRandom().choice(key_chars) for i in range(50)
])
