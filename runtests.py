#!/usr/bin/env python  # Run tests for application
# Source: https://stackoverflow.com/questions/3841725/how-to-launch-tests-for-django-reusable-app

import os
import sys
from argparse import ArgumentParser

import django

from django.test.runner import DiscoverRunner


# Any parameter should be optional as automated tests do not set parameters
def runtests(options=None):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()

    verbosity = options.verbosity if options else 1
    failfast = options.failfast if options else False
    test_runner = DiscoverRunner(verbosity=verbosity, failfast=failfast)

    labels = options.labels if options else []
    failures = test_runner.run_tests(labels or ['newsletter'])
    sys.exit(failures)


if __name__ == '__main__':
    parser = ArgumentParser(description="Run the django-newsletter test suite.")
    parser.add_argument('labels', nargs='*', metavar='label',
        help='Optional path(s) to test modules; e.g. "newsletter.tests.test_mailing".')
    parser.add_argument(
        '-v', '--verbosity', default=1, type=int, choices=[0, 1, 2, 3],
        help='Verbosity level; 0=minimal output, 1=normal output, 2=all output')
    parser.add_argument(
        '--failfast', action='store_true', dest='failfast', default=False,
        help='Tells Django to stop running the test suite after first failed test.')
    options = parser.parse_args()
    runtests(options)
