# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


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
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('post', 'sortorder')]),
        ),
    ]
