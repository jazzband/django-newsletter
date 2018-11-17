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

try:
    REQUIREMENTS = open('requirements.txt').read()
except:
    warnings.warn('Could not read requirements.txt')
    REQUIREMENTS = None

try:
    TEST_REQUIREMENTS = open('requirements_test.txt').read()
except:
    warnings.warn('Could not read requirements_test.txt')
    TEST_REQUIREMENTS = None


setup(
    name='django-newsletter',
    version="0.8b1",
    description=(
        'Django app for managing multiple mass-mailing lists with both '
        'plaintext as well as HTML templates (and pluggable WYSIWYG editors '
        'for messages), images and a smart queueing system all right from '
        'the admin interface.'
    ),
    long_description=README,
    install_requires=REQUIREMENTS,
    license='AGPL',
    author='Mathijs de Bruin',
    author_email='mathijs@mathijsfietst.nl',
    url='http://github.com/dokterbob/django-newsletter/',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities'
    ],
    test_suite='runtests.run_tests',
    tests_require=TEST_REQUIREMENTS
)
