=========
Upgrading
=========

Unreleased: Subscription generators need ``find_subscription``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We added a new method to ``SubscriptionGenerator`` called ``find_subscription`` to search if an email address is
in the dynamically generated subscriptions. We added this method to avoid generating the whole subscription list
to check if an email address is subscribed. Implementations of ``SubscriptionGenerator`` must implement this method,
or it will fail when instantiating the Newsletter.

Unreleased: subscription forms and confirmation requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We have changed logged-in subscribe and unsubscribe confirmation URLs to require POST to change subscription state.
GET requests display the confirmation page without changing the subscription.
Integrations calling these must submit POST requests with Django's usual CSRF protection.
The bundled confirmation templates already use POST.

We have changed the newsletter list forms to identify newsletters directly, so displaying the list
no longer requires creating subscription rows. Since a subscription row may not exist when a form is displayed,
overridden ``newsletter/newsletter_list.html`` templates must use the hidden ``{{ form.newsletter }}`` field
instead of ``{{ form.id }}`` for each form.
Keep ``{{ form.subscribed }}`` in each form and include ``{{ formset.management_form }}`` once for the whole formset.
Forms still provide ``form.instance.newsletter`` for rendering the newsletter's title and links.

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
