#!/usr/bin/env python
# This file is part of django-newsletter.
#
# django-newsletter: Django app for managing multiple mass-mailing lists with
# both plaintext as well as HTML templates (and TinyMCE editor for HTML messages),
# images and a smart queueing system all right from the admin interface.
# Copyright (C) 2008-2013 Mathijs de Bruin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import warnings

from setuptools import setup, find_packages

try:
    README = open('README.rst').read() + '\n\n'
    README += open('CHANGES.rst').read()
except:
    warnings.warn('Could not read README.rst and/or CHANGES.rst')
    README = None


setup(
    name='django-newsletter',
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    description=(
        'Django app for managing multiple mass-mailing lists with both '
        'plaintext as well as HTML templates (and pluggable WYSIWYG editors '
        'for messages), images and a smart queueing system all right from '
        'the admin interface.'
    ),
    long_description=README,
    install_requires=[
        "Django>=2.2.16",
        "python-card-me<1.0",
        "ldif3<3.2",
        "chardet",
        "unicodecsv<0.15",
        "Pillow",
    ],
    author='Mathijs de Bruin',
    author_email='mathijs@mathijsfietst.nl',
    url='http://github.com/jazzband/django-newsletter/',
    packages=find_packages(exclude=("tests", "test_project")),
    include_package_data=True,
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities'
    ],
)
