# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
logger = logging.getLogger(__name__)

from django.db import migrations, models


def renumerate_article_sortorder(apps, schema_editor):
    """ Renumerate articles for consistent and guaranteed unique sortorder. """

    Message = apps.get_model('newsletter', 'Message')

    for message in Message.objects.all():
        for index, article in enumerate(message.articles.all()):
            # We're using the fact that articles are ordered by default

            article.sortorder = (index + 1) * 10
            article.save()


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0002_auto_20150416_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='sortorder',
            field=models.PositiveIntegerField(help_text='Sort order determines the order in which articles are concatenated in a post.', verbose_name='sort order', blank=True),
        ),
        migrations.RunPython(renumerate_article_sortorder),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('post', 'sortorder')]),
        ),
    ]
