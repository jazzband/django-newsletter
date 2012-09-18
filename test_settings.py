DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django_extensions',
    'newsletter',
)

ROOT_URLCONF = 'test_urls'

SITE_ID = 1

TEMPLATE_DIRS = ('test_templates', )
