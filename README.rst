#################
django-newsletter
#################

.. image:: https://img.shields.io/pypi/v/django-newsletter.svg
    :target: https://pypi.python.org/pypi/django-newsletter

.. image:: https://img.shields.io/pypi/pyversions/django-newsletter.svg
    :target: https://pypi.org/project/django-newsletter/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/djversions/django-newsletter.svg
    :target: https://pypi.org/project/django-newsletter/
    :alt: Supported Django versions

.. image:: https://github.com/jazzband/django-newsletter/workflows/Test/badge.svg
   :target: https://github.com/jazzband/django-newsletter/actions
   :alt: GitHub Actions

.. image:: https://codecov.io/gh/jazzband/django-newsletter/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/jazzband/django-newsletter

.. image:: https://jazzband.co/static/img/badge.svg
    :target: https://jazzband.co/
    :alt: Jazzband

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
Strings have been fully translated to a lot of languages with many more on their way.

.. image:: https://www.transifex.com/projects/p/django-newsletter/resource/django/chart/image_png
    :target: http://www.transifex.com/projects/p/django-newsletter/

Contributions to translations are welcome through `Transifex <http://www.transifex.net/projects/p/django-newsletter/>`_. Strings will be included as
soon as near-full coverage is reached.

Compatibility
=============
Currently, django-newsletter officially supports Django 2.2.x LTS, 3.1.x and 3.2.x and Python 3.7 through 3.10.

Requirements
============
Please refer to `requirements.txt <http://github.com/jazzband/django-newsletter/blob/master/requirements.txt>`_
for an updated list of required packages.

Tests
==========
Fairly extensive tests are available for internal frameworks, web
(un)subscription and mail sending. Sending a newsletter to large groups of recipients
(+15k) has been confirmed to work in multiple production environments. Tests
for pull req's and the master branch are automatically run through
`GitHub Actions <https://github.com/jazzband/django-newsletter/actions>`_.

Contributing
=============
Want to contribute, great!

Please refer to the `issues <https://github.com/jazzband/django-newsletter/issues>`_ on
GitHub and read `CONTRIBUTING.rst <https://github.com/jazzband/django-newsletter/blob/master/CONTRIBUTING.rst>`_ .

Feedback
========
If you find any bugs or have feature request for django-newsletter, don't hesitate to
open up an issue on `GitHub <https://github.com/jazzband/django-newsletter/issues>`_
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
