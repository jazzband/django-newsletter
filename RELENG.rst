###################
Release engineering
###################

Steps to publish a new release. Versions come from git tags through
setuptools-scm, so there is no version number to bump in the code.

The translation commands need GNU gettext and the Transifex client (``tx``).

Steps
=====

#. Pick a release date. Create a milestone on GitHub and organise the open
   issues.
#. If supported Django or Python versions change, update ``tox.ini`` (envlist,
   deps and ``[gh-actions:env]``), the matrix in ``.github/workflows/test.yml``,
   the classifiers in ``pyproject.toml`` and the Compatibility section of
   ``README.rst``.
#. In ``CHANGES.rst``, rename the ``Unreleased`` heading to the version and
   date, e.g. ``1.3 (2026-11-01)``. Check it against
   ``git log <last_release_tag>..HEAD``.
#. Update the English source strings and push them to Transifex::

    $ cd newsletter
    $ django-admin makemessages -l en
    $ django-admin makemessages -d djangojs -l en
    $ tx push -s

#. Send out an announcement to translators on Transifex.
#. Pull in the latest translations and compile them::

    $ tx pull -f
    $ cd newsletter
    $ django-admin compilemessages

#. Commit the changes and check that the package builds::

    $ uv build
    $ uvx --from twine twine check dist/*

#. Tag the release commit and push the tag::

    $ git tag vX.Y
    $ git push origin vX.Y

   Pushing the tag runs ``.github/workflows/release.yml``, which builds the
   package, uploads it to Jazzband and creates a draft GitHub release. The test
   workflow runs on the tag as well. Check on GitHub Actions that both
   succeeded before going on.
#. Release the uploads to PyPI (project leads only). Jazzband emails the leads
   once for each uploaded file, so expect two emails, one for the wheel and one
   for the source distribution. Open the project page on
   `Jazzband <https://jazzband.co/projects/django-newsletter>`_ (or follow the
   links in the emails), check the uploads against the commits in the
   repository, and release both.
#. Review the draft release that ``release.yml`` created on GitHub. Its notes
   are the entry for this version in ``CHANGES.rst``. Publish it once the
   package is on PyPI.
