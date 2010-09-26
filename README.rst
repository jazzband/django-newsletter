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

Requirements
============
Please refer to `requirements.txt <http://github.com/dokterbob/django-newsletter/blob/master/requirements.txt>`_ for an updated list of required packes.

Installation
============
#)  Get it from the Cheese Shop::
    
	pip install django-newsletter
    
    **Or** get the latest & greatest from Github and link it to your
    application tree::
    
	git clone git://github.com/dokterbob/django-newsletter.git
    
#)  Add newsletter and to `INSTALLED_APPS` in settings.py and make sure that
    django-tinymce is there as well::

	INSTALLED_APPS = (
	    ...
	    'tinymce',
	    ...
	    'newsletter',
	    ...
	)

#)  Make the ``media`` dir available as ``{{ MEDIA_URL }}newsletter/`` and do the
    same for the django-tinymce app.

    Preferably use something like ``django-staticmedia`` to manage the media files
    for your installed apps so you won't have to worry about this. You can
    simply ``pip install django-staticmedia`` and add the following to ``urls.py``
    to make everything accessible in the development server::

	import staticmedia
	urlpatterns = staticmedia.serve()
    
#)  Create required data structure and load default template fixture::
    
	cd $PROJECT_DIR
	./manage.py syncdb
	./manage.py loaddata default_templates
    
#)  Run the tests to see if it all works::
    
	./manage.py test
    
    If this fails, please contact me!
    If it doesn't: that's a good sign, chap! Go on to the next step.

Usage
=====
#) Start the development server: ``./manage.py runserver``
#) Navigate to ``/admin/`` and: behold!
#) Put a submission in the queue.
#) Submit your message with ``./manage.py runjob submit``
#) For a proper understanding, please take a look at the model graph.

.. image:: http://github.com/dokterbob/django-newsletter/raw/master/graph_models.png

Unit tests
==========
Fairly extensive tests are available for internal frameworks, web
(un)subscription and mail sending. One feature currently untested is actually
sending mail to very large numbers of recipients (1000+), but feel free to try
around.

TODO
====
* Add a separate submission queue view in the admin instead of the modded edit
  view, which is confusing to the user. 
* Finish front end for article ordering from admin.
* Write tests for: template syntax checking, ordering of articles in a
  message.

License
=======
This application is released 
under the GNU Affero General Public License version 3.
