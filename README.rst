#################
django-newsletter
#################

.. image:: https://img.shields.io/pypi/v/django-newsletter.svg
    :target: https://pypi.python.org/pypi/django-newsletter

.. image:: https://img.shields.io/travis/dokterbob/django-newsletter/master.svg
    :target: http://travis-ci.org/dokterbob/django-newsletter

.. image:: https://coveralls.io/repos/dokterbob/django-newsletter/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/dokterbob/django-newsletter?branch=master

.. image:: https://landscape.io/github/dokterbob/django-newsletter/master/landscape.svg?style=flat
   :target: https://landscape.io/github/dokterbob/django-newsletter/master
   :alt: Code Health

Newsletter application for the Django web framework.

What is it?
===========
Django app for managing multiple mass-mailing lists with both plaintext as
well as HTML templates with rich text widget  integration, images and a smart
queueing system all right from the admin interface.

Status
======
We are currently using this package in several large to medium scale production
environments, but it should be considered a permanent work in progress.

Documentation
=============
Extended documentation is available on
`Read the Docs <http://django-newsletter.readthedocs.org/>`_.

Translations
============
All strings have been translated to German, French, English, Russian, Polish, Dutch, Italian, Arabic, Brazilian Portuguese, Icelandic and Czech with more languages on their way.

Contributions to translations are welcome through `Transifex <http://www.transifex.net/projects/p/django-newsletter/>`_. Strings will be included as
soon as near-full coverage is reached.

.. image:: https://www.transifex.com/projects/p/django-newsletter/resource/django/chart/image_png
    :target: http://www.transifex.net/projects/p/django-newsletter/

Compatibility
=============
Currently, django-newsletter is officially supported for Django 1.11.x, 2.2.x and 3.0.x support pending. We support Python
2.7 through 3.8.

Requirements
============
Please refer to `requirements.txt <http://github.com/dokterbob/django-newsletter/blob/master/requirements.txt>`_
for an updated list of required packages.

Tests
==========
Fairly extensive tests are available for internal frameworks, web
(un)subscription and mail sending. Sending a newsletter to large groups of recipients
(+15k) has been confirmed to work in multiple production environments. Tests
for pull req's and the master branch are automatically run through
`Travis CI <http://travis-ci.org/dokterbob/django-newsletter>`_.

Contributing
=============
Want to contribute, great!

Please refer to the `issues <https://github.com/dokterbob/django-newsletter/issues>` on
GitHub and read `CONTRIBUTING.rst <https://github.com/dokterbob/django-newsletter/blob/master/CONTRIBUTING.rst>`.

Feedback
========
If you find any bugs or have feature request for django-newsletter, don't hesitate to
open up an issue on `GitHub <https://github.com/dokterbob/django-newsletter/issues>`_
(but please make sure your issue hasn't been noticed before, finding duplicates is a
waste of time). When modifying or adding features to django-newsletter in a fork, be
sure to let me know what you're building and how you're building it. That way we can
coordinate whether, when and how it will end up in the main fork and (eventually) an
official release.

In general: thanks for the support, feedback, patches and code that's been flowing in
over the years! Django has a truly great community. <3

License
=======
This application is released
under the GNU Affero General Public License version 3.
