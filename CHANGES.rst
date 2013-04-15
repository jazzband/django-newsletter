Changes
=======

0.4.1 (15-04-2013)
------------------

- Started keeping a decent history file. (Finally...)
- Support Django 1.5; make use of class based generic views
- Drop Django 1.3 and Python 2.5 support.
- 100% test coverage for views
- Farsi translations (contributed by rohamn)
- French translations (contributed by smalter)
- Admin actions for subscribing/unsubscribing (contributed by jnns)
- Introduced django-webtest for some tests
- Exempt previews from XFrame protection (fixes #54)

0.4 (20-11-2012)
----------------

- Major code cleanup; PEP8, imports, restructuring, removal of legacy code
- Improved testing throgh Travis and better test coverage
- South migrations
- Added German translation (contributed by jnns)
- WYSIWYG editor is now optional and pluggable, Imperavi and TinyMCE supported
- Timezone-aware date-times when Django 1.4 is used
- Ue of Django 1.3's messages framework
- Many small bugfixes (see GitHub issues)
- Drop support for Django 1.2
- Automatic detection of charset, encoding and dialect for CSV import
- Much cleaner log messages with proper message substitution
- Use Django's staticfiles contrib for static assets in admin interface
- Use surlex for more readable URL templates
- Use sorl-thumbnail for article images and default templates
