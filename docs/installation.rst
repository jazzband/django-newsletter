============
Installation
============

#) Make sure all `requirements <http://github.com/dokterbob/django-newsletter/blob/master/requirements.txt>`_ are properly setup.

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
#)  Configure delay between each Email (optional).

    As default the configuration delay between each Email is 0 but you can easily
    change it to what ever you feel is good for your company::

        DELAY_BETWEEN_EACH_EMAIL = 0

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

#)  Add jobs for sending out mail queues to `crontab <http://linuxmanpages.com/man5/crontab.5.php>`_::

        @hourly /path/to/my/project/manage.py runjobs hourly
        @daily /path/to/my/project/manage.py runjobs daily
        @weekly /path/to/my/project/manage.py runjobs weekly
        @monthly /path/to/my/project/manage.py runjobs monthly

To send mail, ``django-newsletter`` uses Django-provided email utilities, so
ensure that `EMAIL_* settings
<https://docs.djangoproject.com/en/stable/ref/settings/#email-backend`_ are
properly configured for your project.
