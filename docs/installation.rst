============
Installation
============

#)  Install the package from PyPI::

        pip install django-newsletter

    **Or** get the latest & greatest from Github and link it to your
    application tree::

        pip install -e git://github.com/dokterbob/django-newsletter.git#egg=django-newsletter

    (In either case it is recommended that you use
    `VirtualEnv <http://pypi.python.org/pypi/virtualenv>`_ in order to
    keep your Python environment somewhat clean.)

#)  Add ``newsletter`` and the Django ``contrib`` dependencies noted below to
    ``INSTALLED_APPS`` in your settings file. You will need one of the
    supported thumbnail applications (
    `sorl-thumbnail <http://sorl-thumbnail.readthedocs.org/en/latest/installation.html>`_
    or `easy-thumbnails <https://easy-thumbnails.readthedocs.io/en/latest/>`_).
    You may also add an *optional* rich text widget (
    `Django Imperavi <https://github.com/vasyabigi/django-imperavi>`_
    or `Django TinyMCE <https://django-tinymce.readthedocs.io/en/latest/>`_)
    and ::

        INSTALLED_APPS = (
            # Required Contrib Apps
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.auth',
            'django.contrib.sites',
            ...
            # Thumbnail Applications
            'sorl.thumbnail',
            'easy_thumbnails',
            ...
            # Optional Rich Text Editors
            'imperavi',
            'tinymce',
            ...
            'newsletter',
            ...
        )

#)  Specify your thumbnail application in your settings file::

        # Using sorl-thumbnail
        NEWSLETTER_THUMBNAIL = 'sorl-thumbnail'

        # Using easy-thumbnails
        NEWSLETTER_THUMBNAIL = 'easy-thumbnails'

#)  Configure any of the optional :doc:`settings`.

#)  Import subscription, unsubscription and archive URL's somewhere in your
    ``urls.py``::

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
