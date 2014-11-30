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

ROOT_URLCONF = 'test_urls'

SITE_ID = 1

TEMPLATE_DIRS = ('test_templates', )

# Enable time-zone support for Django 1.4 (ignored in older versions)
USE_TZ = True

# Required for django-webtest to work
STATIC_URL = '/static/'
