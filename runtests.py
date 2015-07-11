#!/usr/bin/env python# Run tests for application
# Source: https://stackoverflow.com/questions/3841725/how-to-launch-tests-for-django-reusable-app

import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

try:
    # Django <= 1.8
    from django.test.simple import DjangoTestSuiteRunner
    test_runner = DjangoTestSuiteRunner(verbosity=1)
except ImportError:
    # Django >= 1.8
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests(['newsletter'])
if failures:
    sys.exit(failures)
