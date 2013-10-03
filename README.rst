=================
django-newsletter
=================

.. image:: https://badge.fury.io/py/django-newsletter.png
    :target: http://badge.fury.io/py/django-newsletter

.. image:: https://secure.travis-ci.org/dokterbob/django-newsletter.png?branch=master
    :target: http://travis-ci.org/dokterbob/django-newsletter

.. image:: https://pypip.in/d/django-newsletter/badge.png
        :target: https://crate.io/packages/django-newsletter?version=latest

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
Most if not all strings are available in Dutch, German, French, Farsi,
Russian and English. Contributions to translations are welcome through
`Transifex <http://www.transifex.net/projects/p/django-newsletter/>`_.

.. image:: https://www.transifex.com/projects/p/django-newsletter/resource/django/chart/image_png
    :target: http://www.transifex.net/projects/p/django-newsletter/

Compatibility
=============
Currently, django-newsletter is being tested to run on Python 2.6, 2.7 and the
latest Django 1.4 and 1.5 releases. Apart from tests it *should* be compatible
with Python 2.5 as well.

Requirements
============
Please refer to `requirements.txt <http://github.com/dokterbob/django-newsletter/blob/master/requirements.txt>`_ for an updated list of required packages.

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
    your favourite rich text widget (optional), some Django contrib dependencies,
    `sorl-thumbnail <http://sorl-thumbnail.readthedocs.org/en/latest/installation.html>`_
    and `django-extensions <https://github.com/django-extensions/django-extensions>`_
    (the latter is used for the submission jobs) are there as well::

	INSTALLED_APPS = (
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.auth',
	    'django.contrib.sites',
	    ...
	    # Imperavi (or tinymce) rich text editor is optional
	    # 'imperavi',
	    'django_extensions',
	    'sorl.thumbnail',
	    ...
	    'newsletter',
	    ...
	)

#)  Disable email confirmation for subscribe, unsubscribe and update actions
    for subscriptions.

    By default subscribe, unsubscribe and update requests made by a user who is
    not logged in need to be confirmed by clicking on an activation link in an
    email. If you want all requested actions to be performed without email
    confirmation, add following line to settings.py::

	NEWSLETTER_CONFIRM_EMAIL = False

    For more granular control the ``NEWSLETTER_CONFIRM_EMAIL`` setting can be
    overridden for each of subscribe, unsubscribe and update actions, by adding
    ``NEWSLETTER_CONFIRM_EMAIL_SUBSCRIBE`` and/or
    ``NEWSLETTER_CONFIRM_EMAIL_UNSUBSCRIBE`` and/or
    ``NEWSLETTER_CONFIRM_EMAIL_UPDATE`` set to ``True`` or ``False``.

#)  Install and configure your preferred rich text widget (optional).

    Known to work are `django-imperavi <http://pypi.python.org/pypi/django-imperavi>`_
    as well as for `django-tinymce <http://pypi.python.org/pypi/django-tinymce>`_.
    Be sure to follow installation instructions for respective widgets. After
    installation, the widgets can be selected as follows::

	# Using django-imperavi
	NEWSLETTER_RICHTEXT_WIDGET = "imperavi.widget.ImperaviWidget"

	# Using django-tinymce
	NEWSLETTER_RICHTEXT_WIDGET = "tinymce.widgets.TinyMCE"

    If not set, django-newsletter will fall back to Django's default TextField
    widget.

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

#)  Create required data structure::

	./manage.py syncdb

#)  Change the default contact email listed in
    ``templates/newsletter/subscription_subscribe.html`` and
    ``templates/newsletter/subscription_update.html``.

#)  (Optionally) Create message template overrides for specific newsletters in
    ``templates/newsletter/message/<newsletter_slug>/<message_type>[_subject].<html|txt>``
    where ``<message_type>`` can be one from `subscribe`, `unsubscribe`, `message`
    or `update`.

#)  (Optionally) Run the tests to see if it all works::

	./manage.py test

    If it does: that's a good sign. You'll probably have yourself a
    working configuration!

#)  Add jobs for sending out mail queues to `crontab <http://linuxmanpages.com/man5/crontab.5.php>`_::

	@hourly /path/to/my/project/manage.py runjobs hourly
	@daily /path/to/my/project/manage.py runjobs daily
	@weekly /path/to/my/project/manage.py runjobs weekly
	@monthly /path/to/my/project/manage.py runjobs monthly

Usage
=====
#) Start the development server: ``./manage.py runserver``
#) Navigate to ``/admin/`` and: behold!
#) Put a submission in the queue.
#) Submit your message with ``./manage.py runjob submit``
#) For a proper understanding, please take a look at the `model graph <https://github.com/dokterbob/django-newsletter/raw/master/graph_models.png>`_.

.. image:: https://github.com/dokterbob/django-newsletter/raw/master/graph_models.png

Templates
=========
To get started, we recommend copying the existing 'stub'-templates from
the module directory to your project's `templates` dir::

    cp -rv `python -c 'import newsletter; from os import path; print path.dirname(newsletter.__file__)'`/templates/newsletter <project_dir>/templates/

Web view templates
^^^^^^^^^^^^^^^^^^
`newsletter_list.html`
    Newsletter list view, showing all newsletters marked as public and allowing
    authenticated Django users to (un)subscribe directly.
`newsletter_detail.html`
    Newsletter detail view, linking to subscribe, update,
    unsubscribe and archive views for a particular newsletter.
`submission_archive.html`
    Archive; list of public submissions for a particular newsletter.
`subscription_subscribe.html`
    Subscribe form for unauthenticated users.
`subscription_subscribe_email_sent.html`
    Confirmation of subscription request.
`subscription_activate.html`
    Activation form for (un)subscriptions or updates of unauthenticated users.
`subscription_subscribe_activated.html`
    Confirmation of activation of subscription.
`subscription_unsubscribe_activated.html`
    Confirmation of activation of unsubscription.
`subscription_update_activated.html`
    Confirmation of activation of update.
`subscription_subscribe_user.html`
    Subcribe form for authenticated users.
`subscription_unsubscribe.html`
    Unsubscribe form for unauthenticated users.
`subscription_unsubscribe_email_sent.html`
    Confirmation of unsubscription request.
`subscription_unsubscribe_user.html`
    Unsubscribe form for authenticated users.
`subscription_update.html`
    Update form for unauthenticated users.
`subscription_update_email_sent.html`
    Confirmation of update request.

Email templates
^^^^^^^^^^^^^^^^^
Email templates can be specified per newsletter in `message/<newsletter_slug>`.
If no newsletter-specific templates are found, the defaults in the `message`
folder are used.

When a newsletter is configured to send HTML-messages, the HTML and txt are
both used to create a multipart message. When the use of HTML is not configured
only the text templates are used.

The following templates can be defined:

`message.(html|txt)`
    Template for rendering a messages with the following context available:
        * `subscription`: Subscription containing name and email of recipient.
        * `site`: Current `site` object.
        * `submission`: Current submission.
        * `message`: Current message.
        * `newsletter`: Current newsletter.
        * `date`: Publication date of submission.
        * `STATIC_URL`: Django's `STATIC_URL` setting.
        * `MEDIA_URL`: Django's `MEDIA_URL` setting.
`message_subject.txt`
    Template for the subject of an email newsletter. Context is the same as
    with messages.
`subscribe.(html|txt)`
    Template with confirmation link for subscription.
`subscribe_subject.txt`
    Subject template with confirmation link for subscription.
`unsubscribe.(html|txt)`
    Template with confirmation link for unsubscription.
`unsubscribe_subject.txt`
    Subject template with confirmation link for unsubscription.
`update.(html|txt)`
    Template with confirmation link for updating subscriptions.unsubscription.
`update_subject.txt`
    Subject template with confirmation link for updating subscriptions.unsubscription.

Unit tests
==========
Fairly extensive tests are available for internal frameworks, web
(un)subscription and mail sending. Sending a newsletter to large groups of recipients
(+10k) has been confirmed to work in multiple production environments. Tests
for pull req's and the master branch are automatically run through
`Travis CI <http://travis-ci.org/dokterbob/django-newsletter>`_.

Upgrading
=========

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

Feedback
========
If you find any bugs or have feature request for django-newsletter, don't hesitate to
open up an issue on `GitHub <https://github.com/dokterbob/django-newsletter/issues>`_
(but please make sure your issue hasn't been noticed before, finding duplicates is a
waste of time). When modifying or adding features to django-newsletter in a fork, be
sure to let me know what you're building and how you're building it. That way we can
coordinate whether, when and how it will end up in the main fork and (eventually) an
official release.

In general: thanks for the support, feedback, patches and code that's been flowing in
over the years! Django has a truly great community. <3

Donations
=========
Donations are welcome in Bitcoin or Paypal through
`Properster <https://propster.me/tipjar/0D3UYAI13>`_. For Bitcoin, the link/QRCode below should suffice. If you donate, be sure to fill
in the note. I love to hear what people are using it for!

.. image:: http://qr.ma.eatgold.com/temp/bitcoin12omMNyLirypArtqwDtoKM2av1wsLMbVWs.png
    :target: https://propster.me/tipjar/0D3UYAI13

License
=======
This application is released
under the GNU Affero General Public License version 3.
