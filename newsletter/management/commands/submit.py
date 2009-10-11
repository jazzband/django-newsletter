import logging

from django.core.management.base import BaseCommand

from django.utils.translation import ugettext as _

from newsletter.models import Submission

class Command(BaseCommand):
    def handle(self, **options):
        print _('Submitting queued newsletter mailings')
        Submission.submit_queue()

