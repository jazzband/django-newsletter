Changes
=======

0.5.1 (21-11-2013)
------------------

- Added Italian translation, thanks to azanibellato.
- Support for pluggable/custom user models (#101).
- Proper Sphinx documentation with autodoc on Read the Docs (#90).
- Compatibility with Django 1.6 thanks to @jnss (#97).
- Include default message templates in package (#95).
- Fix database to template file migration for non-ASCII characters (#94).
- Fix small issues with vCard imports (mainly mimetype-related).

0.5 (03-10-2013)
----------------

- Added proxy for app-specific settings.
- Optional skipping of email confirmation in views (`CONFIRM_EMAIL_<ACTION>`).
- Russian translation (contributed by ak3n).
- Added explicit HTML toogle to Newsletter model.
- Fix JavaScript submit link on "Add submission", ported to use jQuery.
- Replacement of remaining function based views with class based equivalents.
- Move message templates from database to files.

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
