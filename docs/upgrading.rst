=========
Upgrading
=========

0.7: Management command instead of django-extensions cron job
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this version, we have deprecated support for the django-extensions cron
job. Hence, it will become necessary to update the crontab; whereas before
messages where submitted with the `runjobs hourly` cron job, this has now
become `submit_newsletter`.

0.6: Upgrading from South to Django Migrations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Based on https://docs.djangoproject.com/en/1.9/topics/migrations/#upgrading-from-south, the procedure should be:

1. Remove ``'south'`` from ``INSTALLED_APPS``.
2. Run ``python manage.py migrate --fake-initial``.

If you are upgrading from below 0.5, you need to upgrade to 0.5 first to
perform required South migrations before moving to 0.6.

0.5: Message templates in files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
As of 0.5 message templates are living in the filesystem like normal files
instead of resorting in the EmailTemplate in the database. In most cases,
South should take care of writing your existing templates to disk and deleting
the database models.

0.4: South migrations
^^^^^^^^^^^^^^^^^^^^^
Since 5f79f40, the app makes use of `South <http://south.aeracode.org/>`_ for
schema migrations. As of this version, using South with django-newsletter
is the official recommendation and `installing it <http://south.readthedocs.org/en/latest/installation.html>`_ is easy.

When upgrading from a pre-South version of newsletter to a current
release (in a project for which South has been enabled), you might have to
fake the initial migration as the DB tables already exist. This can be done
by running the following command::

    ./manage.py migrate newsletter 0001 --fake
