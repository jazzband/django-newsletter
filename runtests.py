#!/usr/bin/env python

import os
import sys

import django
from django.core.management.commands.test import Command as TestCommand


def setup_django():
    """ Setup Django for testing using the test_project directory """

    test_project_dir = os.path.join(os.path.dirname(__file__), 'test_project')
    sys.path.insert(0, test_project_dir)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'
    django.setup()


def run_tests():
    """ Run tests via setuptools, all tests with no special options """

    setup_django()

    # Bypass argument parsing and run the test command manually with no args
    TestCommand().handle()

    sys.exit(0)  # TestCommand exits itself on failure, we only exit on success


if __name__ == "__main__":
    setup_django()

    # Command expects to be called via 'manage.py test' so
    # add the extra argument so that it can parse correctly
    sys.argv.insert(1, 'test')

    # Run the test command with argv to get all the argument goodies
    TestCommand().run_from_argv(sys.argv)
