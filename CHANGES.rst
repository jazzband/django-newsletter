=============
Changes
=============

0.4
===
* Major code cleanup; PEP8, imports, restructuring, removal of legacy code
* Improved testing throgh Travis and better test coverage
* South migrations
* Added German translation
* WYSIWYG editor is now optional and pluggable, Imperavi and TinyMCE supported
* Timezone-aware date-times when Django 1.4 is used
* Ue of Django 1.3's messages framework
* Many small bugfixes (see GitHub issues)
* Drop support for Django 1.2
* Automatic detection of charset, encoding and dialect for CSV import
* Much cleaner log messages with proper message substitution
* Use Django's staticfiles contrib for static assets in admin interface
* Use surlex for more readable URL templates
* Use sorl-thumbnail for article images and default templates
