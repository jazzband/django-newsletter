#!/usr/bin/env python
# This file is part of django-newsletter.
#
# django-newsletter: Django app for managing multiple mass-mailing lists with
# both plaintext as well as HTML templates (and TinyMCE editor for HTML messages),
# images and a smart queueing system all right from the admin interface.
# Copyright (C) 2008-2012 Mathijs de Bruin
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

import distribute_setup
distribute_setup.use_setuptools('0.6.10')

from setuptools import setup, find_packages
from pip.req import parse_requirements

try:
    README = open('README.rst').read() + '\n\n'
    README += open('CHANGES.rst').read()
except:
    README = None

try:
    # Idea to use pip to parse requirements from Romain Hardouin:
    # http://stackoverflow.com/a/16624700/219519
    REQUIREMENTS = [str(ir.req) for ir in parse_requirements('requirements.txt')]
except:
    REQUIREMENTS = None

print REQUIREMENTS

setup(
    name='django-newsletter',
    version="0.4.1",
    description='Django app for managing multiple mass-mailing lists with both plaintext as well as HTML templates (and TinyMCE editor for HTML messages), images and a smart queueing system all right from the admin interface.',
    long_description=README,
    install_requires=REQUIREMENTS,
    author='Mathijs de Bruin',
    author_email='mathijs@mathijsfietst.nl',
    url='http://github.com/dokterbob/django-newsletter/',
    packages=find_packages(),
    include_package_data=True,
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU Affero General Public License v3',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
    test_suite='setuptest.setuptest.SetupTestSuite',
    tests_require=(
        'django-setuptest',
        'argparse',  # apparently needed by django-setuptest on python 2.6
    ),
)
