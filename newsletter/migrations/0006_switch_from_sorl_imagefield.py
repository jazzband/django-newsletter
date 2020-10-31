"""Migrations to switch from sorl ImageField to a new dynamic field."""
from django.db import migrations

from newsletter.fields import DynamicImageField


class Migration(migrations.Migration):
    dependencies = [
        ('newsletter', '0006_attachment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image',
            field=DynamicImageField(
                blank=True,
                null=True,
                upload_to='newsletter/images/%Y/%m/%d',
                verbose_name='image'
            ),
        ),
    ]
