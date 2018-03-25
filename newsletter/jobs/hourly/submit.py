import warnings

from django_extensions.management.jobs import HourlyJob
from django.core.management import call_command


class Job(HourlyJob):
    help = "Submit pending messages."

    def execute(self):
        warnings.warn(
            "The django-extensions cron job is deprecated in favor of the"
            "submit_newsletter management command.", DeprecationWarning)

        call_command('submit_newsletter')
