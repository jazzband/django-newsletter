###################
Release engineering
###################

Preliminary documentation of the actions required to publish a new release.

Steps
=====

#. Pick release date.
#. Create milestone on GitHub, organise open tickets.
#. Push source translations to Transifex::
    $ django-admin makemessages -l en
    $ tx push -s
#. Send out announcement to translators on Transifex.
#. Bump version in :code:`setup.py`.
#. Update supported Django/Python releases to match Django's.
#. Pull in latest translations: `tx pull`
#. Update CHANGELOG based on :code:`git diff HEAD..<last_release_tag>`.
#. Create signed tag: :code:`git tag -s vx.y`.
#. Create release on GitHub with CHANGELOG as release notes.
#. Create build: :code:`python setup.py sdist bdist_wheel`
#. Upload build: :code:`cd dist; twine upload -s *`
