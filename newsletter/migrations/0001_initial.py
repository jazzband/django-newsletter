# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields
import newsletter.utils
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sortorder', models.PositiveIntegerField(help_text='Sort order determines the order in which articles are concatenated in a post.', verbose_name='sort order', db_index=True)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('text', models.TextField(verbose_name='text')),
                ('url', models.URLField(null=True, verbose_name='link', blank=True)),
                ('image', sorl.thumbnail.fields.ImageField(upload_to=b'newsletter/images/%Y/%m/%d', null=True, verbose_name='image', blank=True)),
            ],
            options={
                'ordering': ('sortorder',),
                'verbose_name': 'article',
                'verbose_name_plural': 'articles',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('date_modify', models.DateTimeField(auto_now=True, verbose_name='modified')),
            ],
            options={
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='newsletter title')),
                ('slug', models.SlugField(unique=True)),
                ('email', models.EmailField(help_text='Sender e-mail', max_length=75, verbose_name='e-mail')),
                ('sender', models.CharField(help_text='Sender name', max_length=200, verbose_name='sender')),
                ('visible', models.BooleanField(default=True, db_index=True, verbose_name='visible')),
                ('send_html', models.BooleanField(default=True, help_text='Whether or not to send HTML versions of e-mails.', verbose_name='send html')),
                ('site', models.ManyToManyField(default=newsletter.utils.get_default_sites, to='sites.Site')),
            ],
            options={
                'verbose_name': 'newsletter',
                'verbose_name_plural': 'newsletters',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('publish_date', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='publication date', db_index=True, blank=True)),
                ('publish', models.BooleanField(default=True, help_text='Publish in archive.', db_index=True, verbose_name='publish')),
                ('prepared', models.BooleanField(default=False, verbose_name='prepared', db_index=True, editable=False)),
                ('sent', models.BooleanField(default=False, verbose_name='sent', db_index=True, editable=False)),
                ('sending', models.BooleanField(default=False, verbose_name='sending', db_index=True, editable=False)),
                ('message', models.ForeignKey(verbose_name='message', to='newsletter.Message')),
                ('newsletter', models.ForeignKey(editable=False, to='newsletter.Newsletter', verbose_name='newsletter')),
            ],
            options={
                'verbose_name': 'submission',
                'verbose_name_plural': 'submissions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_field', models.CharField(db_column=b'name', max_length=30, blank=True, help_text='optional', null=True, verbose_name='name')),
                ('email_field', models.EmailField(db_column=b'email', max_length=75, blank=True, null=True, verbose_name='e-mail', db_index=True)),
                ('ip', models.IPAddressField(null=True, verbose_name='IP address', blank=True)),
                ('create_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('activation_code', models.CharField(default=newsletter.utils.make_activation_code, max_length=40, verbose_name='activation code')),
                ('subscribed', models.BooleanField(default=False, db_index=True, verbose_name='subscribed')),
                ('subscribe_date', models.DateTimeField(null=True, verbose_name='subscribe date', blank=True)),
                ('unsubscribed', models.BooleanField(default=False, db_index=True, verbose_name='unsubscribed')),
                ('unsubscribe_date', models.DateTimeField(null=True, verbose_name='unsubscribe date', blank=True)),
                ('newsletter', models.ForeignKey(verbose_name='newsletter', to='newsletter.Newsletter')),
                ('user', models.ForeignKey(verbose_name='user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'subscription',
                'verbose_name_plural': 'subscriptions',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together=set([('user', 'email_field', 'newsletter')]),
        ),
        migrations.AddField(
            model_name='submission',
            name='subscriptions',
            field=models.ManyToManyField(help_text='If you select none, the system will automatically find the subscribers for you.', to='newsletter.Subscription', db_index=True, verbose_name='recipients', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='newsletter',
            field=models.ForeignKey(verbose_name='newsletter', to='newsletter.Newsletter'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='message',
            unique_together=set([('slug', 'newsletter')]),
        ),
        migrations.AddField(
            model_name='article',
            name='post',
            field=models.ForeignKey(related_name='articles', verbose_name='message', to='newsletter.Message'),
            preserve_default=True,
        ),
    ]
