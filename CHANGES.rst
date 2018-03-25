Changes
=======

0.7b2 (25-03-2018)
------------------

- Drop support for deprecated Django 1.10.
- Introduce `submit_newsletter` management command, deprecating cron job and
  dropping `django-extensions` dependency.

- Fix for encoding of non-ASCII recipient names for Django < 1.9 (#244).
- Allow programmatic access Article and Submission save() methods (#246).

0.7b1 (16-11-2017)
------------------

- Support for Django 1.10, 1.11 and tentative support for 2.0.
- Drop support for Django 1.9.
- Added support for Python 3.6.

- Isolated the send_message process in anticipation of dropping of
  django-extensions dependency (#39).
- Custom ArticleFormSet for improved Article sortorder, hidden
  by default. (#194)
- Move tests to separate directory, exclude from binaries and use
  Django's native test runner. (#206)
- Cleanup of form validation. (#209)
- Settings for delays between emails, batches and the size of batches. (#223)
- Add missing translatable strings in templates. (#220)
- Added translations for es, el_GR.
- Updated translations for fa, fr, nl.

Security fixes
^^^^^^^^^^^^^^

- Don’t leak username in unsubscribe form.
- Use Django’s crypto code to generate random code.

Small fixes
^^^^^^^^^^^

- Add MySQL contrib to export list of subscribers.
- Add note about EMAIL_* settings in installation docs.
- Added test for `Message.__str__`.
- Warnings when files cannot be read in setup.py.
- Move test requirements to their approriate place. Closes (#190)
- Note on upgrading from <0.5.
- Added documentation on premailers. Closes (#178)
- Display email on import confirmation page.
- Fix broken links in requirements. (#205)
- Move Pillow to requirements, fixes (#202).
- Add a second subscription for mailing tests.
- Require Django 1.8.18 (latest point release).
- HTML5 doctype for default templates.

0.6 (2-2-2016)
--------------

- Added support for Django 1.8 and 1.9, and dropped support for older versions.
- Added support for native Django migrations, replacing South migrations.
- Added Python 3.4/3.5 support and dropped Python 2.6 support.
- Replaced IPAddressField by GenericIPAddressField (#131).
- Fixed addresses serialization with JSON-based sessions (#104).
- Add List-Unsubscribe header to sent messages (#169).
- Added Polish and Brazilian Portuguese translations.
- Significantly improved test coverage.

Small fixes
^^^^^^^^^^^

- Submission admin always takes last message (#170).
- Check that user has "add_subscription" permission when importing subscriptions (#128).
- Fix for Submission.publish_date default value (#125).
- Change subscription status in admin to radio field (#122).
- Make the Submissions list display the Publish date and time with respect to the server's timezone (#112).
- Several smaller issues: #107, #121, #123

0.5.2 (1-5-2014)
----------------

- Additional locale support: Arabic, Czech, French and Islandic
- Run tests on Django 1.7 beta and Python 3.3 (but allow failure)

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
