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
#. Update the English source strings and push them to Transifex::

    $ cd newsletter
    $ django-admin makemessages -l en
    $ django-admin makemessages -d djangojs -l en
    $ tx push -s

#. Send out an announcement to translators on Transifex.
#. If supported Django or Python versions change, update ``tox.ini`` (envlist,
   deps and ``[gh-actions:env]``), the matrix in ``.github/workflows/test.yml``,
   the classifiers in ``pyproject.toml`` and the Compatibility section of
   ``README.rst``.
#. Pull in the latest translations and compile them::

    $ tx pull -f
    $ cd newsletter
    $ django-admin compilemessages

#. In ``CHANGES.rst``, rename the ``Unreleased`` heading to the version and
   date, e.g. ``1.3 (2026-11-01)``. Check it against
   ``git log <last_release_tag>..HEAD``.
#. Commit the changes and check that the package builds::

    $ uv build
    $ uvx --from twine twine check dist/*

#. Tag the release commit and push the tag::

    $ git tag vX.Y
    $ git push origin vX.Y

   Pushing the tag runs ``.github/workflows/release.yml``, which builds the
   package and uploads it to Jazzband.
#. Release the upload to PyPI from the project page on
   `Jazzband <https://jazzband.co/projects/django-newsletter>`_ (project leads
   only).
#. Create a release on GitHub with the ``CHANGES.rst`` entry as release notes.
