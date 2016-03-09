# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.manager
import django.contrib.sites.managers


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsletter',
            name='email',
            field=models.EmailField(help_text='Sender e-mail', max_length=254, verbose_name='e-mail'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='email_field',
            field=models.EmailField(db_column='email', max_length=254, blank=True, null=True, verbose_name='e-mail', db_index=True),
        ),
    ]

    # if using Django version 1.8 and later also apply AlterModelManagers and AlterField to GenericIPAddressField
    if django.VERSION >= (1,8):
        operations += [
            migrations.AlterModelManagers(
                name='newsletter',
                managers=[
                    ('objects', django.db.models.manager.Manager()),
                    ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
                ],
            ),
            migrations.AlterField(
                model_name='subscription',
                name='ip',
                field=models.GenericIPAddressField(null=True, verbose_name='IP address', blank=True),
            )
        ]