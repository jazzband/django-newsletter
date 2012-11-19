DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.sites',
    'django_extensions',
    'sorl.thumbnail',
    'newsletter',
)

ROOT_URLCONF = 'test_urls'

SITE_ID = 1

TEMPLATE_DIRS = ('test_templates', )

# Enable time-zone support for Django 1.4 (ignored in older versions)
USE_TZ = True
