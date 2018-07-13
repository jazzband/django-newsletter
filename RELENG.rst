###################
Release engineering
###################

Preliminary documentation of the actions required to publish a new release.

Steps
=====
1. Pick release date.
2. Create milestone on GitHub, organise open tickets.
3. Send out announcement to translators on Transifex.
4. Bump version in `setup.py`.
5. Update supported Django/Python releases to match Django's.
6. Pull in latest translations.
7. Update CHANGELOG based on `git diff HEAD..<last_release_tag>`.
7. Create signed tag: `git tag -s vx.y`.
8. Create release on GitHub with CHANGELOG as release notes.
9. Create build: `python setup.py sdist bdist_wheel`
10. Upload build: `cd dist; twine upload -s *`
