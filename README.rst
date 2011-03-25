=================
django-newsletter
=================
Newsletter application for the Django web framework.
----------------------------------------------------

What is it?
===========
Django app for managing multiple mass-mailing lists with both plaintext as
well as HTML templates (and TinyMCE editor for HTML messages), images and a
smart queueing system all right from the admin interface.

Status
======
We are currently using this package in several production environments, but it
should still be considered a work in progress.

Translations
============
Most of the strings have been translated to Dutch and a German translation should be available soon. Feel free to contribute any translations through `Transifex <http://www.transifex.net/projects/p/django-newsletter/>`_.

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
    the dependencies django-tinymce and django-extensions are there as well::

	INSTALLED_APPS = (
	    ...
	    'tinymce',
	    'django_extensions',
	    ...
	    'newsletter',
	    ...
	)

#)  Import subscription, unsubscription and archive URL's somewhere in your
    `urls.py`::

	urlpatterns = patterns('',
	    ...
	    (r'^newsletter/', include('newsletter.urls')),
	    ...
	)

#)  Make the ``media`` dir available as ``{{ MEDIA_URL }}newsletter/`` and do the
    same for the django-tinymce app.

    Preferably use something like ``django-staticmedia`` to manage the media files
    for your installed apps so you won't have to worry about this. You can
    simply ``pip install django-staticmedia`` and add the following to ``urls.py``
    to make everything accessible in the development server::

	import staticmedia
	urlpatterns += staticmedia.serve()

#)  Configure TinyMCE if you have not already done so. At the very least make
    sure you set ``TINYMCE_JS_URL`` in ``settings.py`` to point to wherever 
    ``tiny_mce.js`` is located. (Typically ``/media/tinymce/tiny_mce/tiny_mce.js``)

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
(un)subscription and mail sending. One feature currently untested is actually
sending mail to very large numbers of recipients (1000+), but feel free to try
around. Please to note that the unittests (or actually, Django) currently 
requires a `404.html` in your `templates` directory in order to be able to
test 404 responses.

TODO
====
* Add a separate submission queue view in the admin instead of the modded edit
  view, which is confusing to the user. 
* Finish front end for article ordering from admin.
* Write tests for: template syntax checking, ordering of articles in a
  message.
* Extend subscription models to allow for mail deliverability feedback.
* Refactor default contact email out of the templates.

License
=======
This application is released 
under the GNU Affero General Public License version 3.
