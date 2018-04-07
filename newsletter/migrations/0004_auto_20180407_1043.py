# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import newsletter.models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0003_auto_20160226_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='newsletter',
            field=models.ForeignKey(default=newsletter.models.get_default_newsletter,
                                    verbose_name='newsletter',
                                    to='newsletter.Newsletter',
                                    on_delete=models.CASCADE),
        ),
    ]
