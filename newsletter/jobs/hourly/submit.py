import logging

from django.utils.translation import ugettext as _
from django_extensions.management.jobs import HourlyJob
from newsletter.models import Submission

logger = logging.getLogger(__name__)




class Job(HourlyJob):
    help = "Submit pending messages."

    def execute(self):
        logger.info(_('Submitting queued newsletter mailings'))
        Submission.submit_queue()
