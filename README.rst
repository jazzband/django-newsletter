=================
django-newsletter
=================

What is it?
===========
Django app for managing multiple mass-mailing lists with both plaintext as well as HTML templates (and TinyMCE editor for HTML messages), images and a smart queueing system all right from the admin interface.

Status
======
We are currently nearing the end of a migration from an early production version to a Django 1.1-compatible release and are steadily approaching a production-ready stage.

Requirements
============
* Django 1.1
* django-extensions (included in demo app)

Installation
============
#) git clone git://github.com/dokterbob/django-newsletter.git``
#) ``ln -s django-newsletter/newsletter``
#) ``ln -s django-newsletter/media static/newsletter``
#) Add newsletter to ``INSTALLED_APPS`` in ``settings.py``
#) Run unit tests just to be sure it is working: ``./manage.py test``.
#) If it is not, let me know. Create an issue on GitHub or send me a message.
#) Play around with the demo app! User and pass equal ``test``.

Usage
=====
#) Start the development server: ``./manage.py runserver``
#) Navigate to ``/admin/`` and: behold!
#) Put a submission in the queue.
#) Make sure django_extensions is installed and: ``./manage.py runjob submit``
#) For a proper understanding, please take a look at the model graph in .. image:: model_graph.png

Unit tests
==========
Yes, we can! 
Fairly extensive tests are available for internal frameworks, web (un)subscription and mail sending. One feature currently untested is actually sending mail to very large numbers of recipients (500+), but feel free to try around.

TODO
====
* Add a separate submission queue view in the admin instead of the modded edit view, which is confusing to the user.
* Finish front end for article ordering from admin.
* Write tests for: template syntax checking, ordering of articles in a message.

License
=======
This application is released 
under the GNU Affero General Public License version 3.
