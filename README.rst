=================
django-newsletter
=================

.. image:: https://secure.travis-ci.org/dokterbob/django-newsletter.png?branch=master
    :target: http://travis-ci.org/dokterbob/django-newsletter

Newsletter application for the Django web framework.
----------------------------------------------------

What is it?
===========
Django app for managing multiple mass-mailing lists with both plaintext as
well as HTML templates with rich text widget integration, images and a
smart queueing system all right from the admin interface.

Status
======
We are currently using this package in several large to medium scale
production environments, but it should be considered a permanent work in
progress.

Translations
============
Most if not all strings are available in Dutch, German and English.
Contributions to translations are welcome through `Transifex <http://www.transifex.net/projects/p/django-newsletter/>`_.

.. image:: https://www.transifex.com/projects/p/django-newsletter/resource/django/chart/image_png
    :target: http://www.transifex.net/projects/p/django-newsletter/

Requirements
============
Please refer to `requirements.txt <http://github.com/dokterbob/django-newsletter/blob/master/requirements.txt>`_ for an updated list of required packes.

Installation
============
#)  Get it from the Cheese Shop::

	pip install django-newsletter

    **Or** get the latest & greatest from Github and link it to your
    application tree::

	pip install -e git://github.com/dokterbob/django-newsletter.git#egg=django-newsletter

    (In either case it is recommended that you use
    `VirtualEnv <http://pypi.python.org/pypi/virtualenv>`_ in order to
    keep your Python environment somewhat clean.)

#)  Add newsletter and to ``INSTALLED_APPS`` in settings.py and make sure that
    your favourite rich text widget, some Django contrib dependencies and
    django-extensions (for the submission jobs) are there as well::

	INSTALLED_APPS = (
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.auth',
	    'django.contrib.sites',
	    ...
	    'imperavi',
	    'django_extensions',
	    ...
	    'newsletter',
	    ...
	)

#)  Install and configure your preferred rich text widget (optional).
    If not set, django-newsletter will fall back to Django's default TextField
    widget. (Make sure to follow your editor's installation instructions
    closely.)

	# Using django-imperavi
	NEWSLETTER_RICHTEXT_WIDGET = "imperavi.widget.ImperaviWidget"

        # Using django-tinymce
	NEWSLETTER_RICHTEXT_WIDGET = "tinymce.widgets.TinyMCE"

#)  Import subscription, unsubscription and archive URL's somewhere in your
    `urls.py`::

	urlpatterns = patterns('',
	    ...
	    (r'^newsletter/', include('newsletter.urls')),
	    ...
	)

#)  Enable Django's `staticfiles <http://docs.djangoproject.com/en/dev/howto/static-files/>`_
    app so the admin icons, CSS and JavaScript will be available where
    we expect it.

#)  Create required data structure and load default template fixture::

	./manage.py syncdb
	./manage.py loaddata default_templates

#)  Change the default contact email listed in
    ``templates/newsletter/subscription_subscribe.html`` and
    ``templates/newsletter/subscription_update.html``.

#)  Run the tests to see if it all works::

	./manage.py test

    If this fails, please contact me!
    If it doesn't: that's a good sign, chap. You'll probably have yourself a
    working configuration!

#)  Add jobs for sending out mail queues to `crontab <http://linuxmanpages.com/man5/crontab.5.php>`_::

	@hourly /path/to/my/project/manage.py runjobs hourly
	@daily /path/to/my/project/manage.py runjobs daily
	@weekly /path/to/my/project/manage.py runjobs weekly
	@monthly /path/to/my/project/manage.py runjobs monthly

South migrations / upgrading
============================
Since 5f79f40, the app makes use of `South <http://south.aeracode.org/>`_ for
schema migrations. As of this version, using South with django-newsletter
is the official recommendation and `installing it <http://south.readthedocs.org/en/latest/installation.html>`_ is easy.

When upgrading from a pre-South version of newsletter to a current
release (in a project for which South has been enabled), you might have to
fake the initial migration as the DB tables already exist. This can be done
by running the following command::

	./manage.py migrate newsletter 0001 --fake

Usage
=====
#) Start the development server: ``./manage.py runserver``
#) Navigate to ``/admin/`` and: behold!
#) Put a submission in the queue.
#) Submit your message with ``./manage.py runjob submit``
#) For a proper understanding, please take a look at the `model graph <https://github.com/dokterbob/django-newsletter/raw/master/graph_models.png>`_.

.. image:: https://github.com/dokterbob/django-newsletter/raw/master/graph_models.png

Unit tests
==========
Fairly extensive tests are available for internal frameworks, web
(un)subscription and mail sending. Sending a newsletter to large groups of recipients
(+10k) has been confirmed to work in multiple production environments. Tests
for pull req's and the master branch are automatically run through
`Travis CI <http://travis-ci.org/dokterbob/django-newsletter>`_.

License
=======
This application is released
under the GNU Affero General Public License version 3.
