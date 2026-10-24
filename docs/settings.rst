.. _settings:

========
Settings
========

Required Settings
^^^^^^^^^^^^^^^^^

The following settings are required.

Configure thumbnailing applications
-----------------------------------
Article images in newsletter messages are thumbnailed by a thumbnailing
application. Choose how images are handled with ``NEWSLETTER_THUMBNAIL``::

    # Using sorl-thumbnail
    NEWSLETTER_THUMBNAIL = 'sorl-thumbnail'

    # Using easy-thumbnails
    NEWSLETTER_THUMBNAIL = 'easy-thumbnails'

    # Without a thumbnailing application
    NEWSLETTER_THUMBNAIL = 'no-thumbnail'

`sorl-thumbnail <https://pypi.org/project/sorl-thumbnail/>`_ and
`easy-thumbnails <https://pypi.org/project/easy-thumbnails/>`_ need to be
installed and added to ``INSTALLED_APPS`` following their own instructions.
django-newsletter then uses them for the article image model field, the admin
widget and the thumbnails in message templates.

With ``'no-thumbnail'``, article images use Django's ``ImageField`` and no
thumbnails are generated. Messages link to the original image and scale it
with the ``width`` and ``height`` attributes of the ``<img>`` tag.

If ``NEWSLETTER_THUMBNAIL`` is not set, django-newsletter shows a warning at
startup and uses sorl-thumbnail, which then needs to be installed.

Optional Settings
^^^^^^^^^^^^^^^^^

The following optional features may be configured.

Disabling email confirmation
----------------------------
Disable email confirmation for subscribe, unsubscribe and update actions for subscriptions.

By default subscribe, unsubscribe and update requests made by a user who is
not logged in need to be confirmed by clicking on an activation link in an
email. If you want all requested actions to be performed without email
confirmation, add following line to ``settings.py``::

    NEWSLETTER_CONFIRM_EMAIL = False

For more granular control the ``NEWSLETTER_CONFIRM_EMAIL`` setting can be
overridden for each of subscribe, unsubscribe and update actions, by adding
``NEWSLETTER_CONFIRM_EMAIL_SUBSCRIBE`` and/or
``NEWSLETTER_CONFIRM_EMAIL_UNSUBSCRIBE`` and/or
``NEWSLETTER_CONFIRM_EMAIL_UPDATE`` set to ``True`` or ``False``.

Disabling the no-user validation
--------------------------------
Disable checking for existing users for the provided email address.

By default, the subscribe/update/unsubscribe forms will reject email addresses
that belong to a registered user, asking the visitor to login instead. If you
want to bypass this check, add to ``settings.py``::

    NEWSLETTER_VALIDATE_NO_USER = False

Defaults to ``True``.

Configure rich text widget
--------------------------
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

Thumbnail quality
-----------------
The JPEG quality of generated thumbnails can be set from 1 to 100 with::

    NEWSLETTER_THUMBNAIL_QUALITY = 95

Defaults to ``95``. It has no effect with ``NEWSLETTER_THUMBNAIL = 'no-thumbnail'``,
as no thumbnails are generated.

HTTPS links
-----------
Links in emails and in the online archive use ``https`` by default. This
covers activation, unsubscribe and "read online" links, image URLs and the
``List-Unsubscribe`` header. To generate ``http`` links instead, add to
``settings.py``::

    NEWSLETTER_USE_HTTPS = False

If not set, django-newsletter shows a warning at startup and uses ``True``.

Delay and batch size
--------------------
The delay between each email, the delay between batches and the batch size
can be specified with e.g.::

    # Amount of seconds to wait between each email. Here 100ms is used.
    NEWSLETTER_EMAIL_DELAY = 0.1

    # Amount of seconds to wait between each batch. Here one minute is used.
    NEWSLETTER_BATCH_DELAY = 60

    # Number of emails in one batch
    NEWSLETTER_BATCH_SIZE = 100

For both delays, sub-second delays can also be used. If the delays are not
set, it will default to not sleeping.


Separate mailer for newsletters
-------------------------------
Newsletters can go through a different mailer than the other emails. This
needs Django 6.1 or later.

Set ``NEWSLETTER_MAILER`` to an alias from Django's `MAILERS
<https://docs.djangoproject.com/en/stable/ref/settings/#mailers>`_ setting.
Submissions go through that mailer. Subscribe, unsubscribe and update
confirmations still use the ``default`` mailer. For example, to send
newsletters through Mailtrap's bulk stream::

    MAILERS = {
        'default': {...},
        'newsletters': {
            'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'OPTIONS': {
                'host': 'bulk.smtp.mailtrap.io',
                'port': 587,
                'username': 'api',
                'password': os.environ['MAILTRAP_API_TOKEN'],
                'use_tls': True,
            },
        },
    }

    NEWSLETTER_MAILER = 'newsletters'

With `django-anymail <https://anymail.dev/>`_, use the
``anymail.backends.mailtrap.EmailBackend`` backend with the ``api_token``
option and ``'api_url': 'https://bulk.api.mailtrap.io/api/'`` instead.

If not set, all emails use the ``default`` mailer.
