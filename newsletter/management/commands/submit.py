# -*- coding: utf-8 -*-
"""
actual sending of the submissions
"""
import logging

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from newsletter.models import Submission


class Command(BaseCommand):
    help = "Submit pending messages."
    args = ""

    def handle(self, *args, **options):
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.debug('Handle called')
        self.logger.info(_('Submitting queued newsletter mailings'))
        Submission.submit_queue()