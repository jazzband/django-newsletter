=================
django-newsletter
=================

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
Please refere to ``requirements.txt`` for an updated list of required packes.

Installation
============
#) Install the package using ``pip install -e git://github.com/dokterbob/django-newsletter.git#egg=django_newsletter``
#) ``ln -s <my_project>/<media_dir> <newsletter_install_dir>/media``
#) Add newsletter to ``INSTALLED_APPS`` in ``settings.py``
#) Run unit tests just to be sure it is working: ``./manage.py test``.
#) If it is not, let me know. Create an issue on GitHub or send me a message.

Usage
=====
#) Start the development server: ``./manage.py runserver``
#) Navigate to ``/admin/`` and: behold!
#) Put a submission in the queue.
#) Submit your message with ``./manage.py runjob submit``
#) For a proper understanding, please take a look at the model graph in
.. image:: model_graph.png


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
