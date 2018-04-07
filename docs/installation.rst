============
Installation
============

#) Make sure all `requirements <http://github.com/dokterbob/django-newsletter/blob/master/requirements.txt>`_ are properly setup.

#)  Install the package from PyPI::

        pip install django-newsletter

    **Or** get the latest & greatest from Github and link it to your
    application tree::

        pip install -e git://github.com/dokterbob/django-newsletter.git#egg=django-newsletter

    (In either case it is recommended that you use
    `VirtualEnv <http://pypi.python.org/pypi/virtualenv>`_ in order to
    keep your Python environment somewhat clean.)

#)  Add newsletter to ``INSTALLED_APPS`` in settings.py and make sure that
    your favourite rich text widget (optional), some Django contrib dependencies
    and `sorl-thumbnail <http://sorl-thumbnail.readthedocs.org/en/latest/installation.html>`_
    are in there as well::

        INSTALLED_APPS = (
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.auth',
            'django.contrib.sites',
            ...
            # Imperavi (or tinymce) rich text editor is optional
            # 'imperavi',
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

#)  Configure delay and batch size (optional).

    The delay between each email, batches en batch size can be specified with e.g.::

        # Amount of seconds to wait between each email. Here 100ms is used.
        ``NEWSLETTER_EMAIL_DELAY = 0.1``

        # Amount of seconds to wait between each batch. Here one minute is used.
        ``NEWSLETTER_BATCH_DELAY = 60``

        # Number of emails in one batch
        ``NEWSLETTER_BATCH_SIZE = 100``

    For both delays, sub-second delays can also be used. If the delays are not
    set, it will default to not sleeping.

#)  Import subscription, unsubscription and archive URL's somewhere in your
    `urls.py`::

        urlpatterns = [
            ...
            url(r'^newsletter/', include('newsletter.urls')),
            ...
        ]

#)  Enable Django's `staticfiles <http://docs.djangoproject.com/en/dev/howto/static-files/>`_
    app so the admin icons, CSS and JavaScript will be available where
    we expect it.

#)  Create the required data structure::

        ./manage.py migrate

#)  Change the default contact email listed in
    ``templates/newsletter/subscription_subscribe.html`` and
    ``templates/newsletter/subscription_update.html``.

#)  (Optionally) Create message template overrides for specific newsletters in
    ``templates/newsletter/message/<newsletter_slug>/<message_type>[_subject].<html|txt>``
    where ``<message_type>`` can be one from `subscribe`, `unsubscribe`, `message`
    or `update`.

#)  You may now navigate to the Django admin where the Newsletter module
    should be available for you to play with.

    In order to test if submissions work, make sure you create a newsletter,
    a subscription, a message and finally a submission.

    After creating the submission, you must schedule it by clicking the
    'submit' button in the top right of the page where you edit it.

#)  Now you may perform a test submission with the `submit_newsletter`
    management command (`-v 2` is for extra verbosity)::

        ./manage.py submit_newsletter -v 2

#)  Add the `submit_newsletter` management command to `crontab <http://man7.org/linux/man-pages/man5/crontab.5.html>`_.

    For example (for sending every 15 minutes)::

        */15  *  *   *   *     <path_to_virtualenv>/bin/python <project_root>/manage.py submit_newsletter 1>/dev/null 2>&1

To send mail, ``django-newsletter`` uses Django-provided email utilities, so
ensure that `email settings
<https://docs.djangoproject.com/en/stable/ref/settings/#email-backend>`_ are
properly configured for your project.
