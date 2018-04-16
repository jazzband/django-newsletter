========
Settings
========

The following optional features may be configured.

Disabling email confirmation
----------------------------
Disable email confirmation for subscribe, unsubscribe and update actions for subscriptions.

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

Delay and batch size
--------------------
The delay between each email, batches en batch size can be specified with e.g.::

    # Amount of seconds to wait between each email. Here 100ms is used.
    ``NEWSLETTER_EMAIL_DELAY = 0.1``

    # Amount of seconds to wait between each batch. Here one minute is used.
    ``NEWSLETTER_BATCH_DELAY = 60``

    # Number of emails in one batch
    ``NEWSLETTER_BATCH_SIZE = 100``

For both delays, sub-second delays can also be used. If the delays are not
set, it will default to not sleeping.
