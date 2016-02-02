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
All strings have been translated to German, French, English, Russion, Polish, Dutch, Italian, Arabic, Brazilian Portuguese, Icelandic and Czech with more languages on their way.

Contributions to translations are welcome through `Transifex <http://www.transifex.net/projects/p/django-newsletter/>`_. Strings will be included as
soon as near-full coverage is reached.

.. image:: https://www.transifex.com/projects/p/django-newsletter/resource/django/chart/image_png
    :target: http://www.transifex.net/projects/p/django-newsletter/

Compatibility
=============
Currently, django-newsletter is officially supported for Django 1.8 and 1.9 and Python 2.7, 3.4 and 3.5.

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
.. image:: https://badge.waffle.io/dokterbob/django-newsletter.png?label=ready&title=Ready
   :target: https://waffle.io/dokterbob/django-newsletter
   :alt: 'Stories in Ready'

.. image:: https://badge.waffle.io/dokterbob/django-newsletter.png?label=in%20progress&title=Progress
   :target: https://waffle.io/dokterbob/django-newsletter
   :alt: 'Stories in Progress'

.. image:: https://badge.waffle.io/dokterbob/django-newsletter.png?label=under%20review&title=Review
   :target: https://waffle.io/dokterbob/django-newsletter
   :alt: 'Stories Under Review'

Should you wish to contribute, great! Please have a look at the `waffle.io board <https://waffle.io/dokterbob/django-newsletter>`_. Issues in the 'Ready' column are ready for implementation, just drag the issue to 'In Progress' and then to 'Review'. Issues in the backlog require some further discussion concering the scope and methods of implementation, please feel free to mingle in discussions. Lastly, should you see an issue with the 'Review' status, feel free to help out other contributors with your feedback.

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
