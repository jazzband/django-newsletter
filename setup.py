# This file is part of django-newsletter.
# 
# django-newsletter: Django app for managing multiple mass-mailing lists with 
# both plaintext as well as HTML templates (and TinyMCE editor for HTML messages), 
# images and a smart queueing system all right from the admin interface.
# Copyright (C) 2008-2009 Mathijs de Bruin
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

from distutils.core import setup

try:
    README = open('README.rst').read()
except:
    README = None

setup(
    name = 'django-newsletter',
    version = "0.1",
    description = 'Django app for managing multiple mass-mailing lists with both plaintext as well as HTML templates (and TinyMCE editor for HTML messages), images and a smart queueing system all right from the admin interface.',
    long_description = README,
    author = 'Mathijs de Bruin',
    author_email = 'drbob@dokterbob.net',
    url = 'http://github.com/dokterbob/django-newsletter',
    packages = ['newsletter', 'newsletter.templatetags',],
    include_package_data = True,
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
