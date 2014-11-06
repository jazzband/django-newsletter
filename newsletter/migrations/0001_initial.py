# -*- coding: utf-8 -*-
import datetime
import south
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

if south.__version__ == '0.8.3':
    raise Exception(
        'Due to a bug in South 0.8.3, migrations cannot be run. Please '
        'upgrade to South 0.8.4 or later using `pip install -U South` and '
        'run the migrations again.'
    )


from ..utils import get_user_model
User = get_user_model()

user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.model_name)
user_ptr_name = '%s_ptr' % User._meta.object_name.lower()

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailTemplate'
        db.create_table('newsletter_emailtemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Default', max_length=200)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=16, db_index=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('newsletter', ['EmailTemplate'])

        # Adding unique constraint on 'EmailTemplate', fields ['title', 'action']
        db.create_unique('newsletter_emailtemplate', ['title', 'action'])

        # Adding model 'Newsletter'
        db.create_table('newsletter_newsletter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('sender', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('subscribe_template', self.gf('django.db.models.fields.related.ForeignKey')(default=2, related_name='subcribe_template', to=orm['newsletter.EmailTemplate'])),
            ('unsubscribe_template', self.gf('django.db.models.fields.related.ForeignKey')(default=3, related_name='unsubcribe_template', to=orm['newsletter.EmailTemplate'])),
            ('update_template', self.gf('django.db.models.fields.related.ForeignKey')(default=4, related_name='update_template', to=orm['newsletter.EmailTemplate'])),
            ('message_template', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='message_template', to=orm['newsletter.EmailTemplate'])),
        ))
        db.send_create_signal('newsletter', ['Newsletter'])

        # Adding M2M table for field site on 'Newsletter'
        db.create_table('newsletter_newsletter_site', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newsletter', models.ForeignKey(orm['newsletter.newsletter'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('newsletter_newsletter_site', ['newsletter_id', 'site_id'])

        # Adding model 'Subscription'
        db.create_table('newsletter_subscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[user_orm_label], null=True, blank=True)),
            ('name_field', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, db_column='name', blank=True)),
            ('email_field', self.gf('django.db.models.fields.EmailField')(db_index=True, max_length=75, null=True, db_column='email', blank=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('newsletter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['newsletter.Newsletter'])),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('activation_code', self.gf('django.db.models.fields.CharField')(default='7f954ab42db0e45e6ee3e230e41b38b1e16614a8', max_length=40)),
            ('subscribed', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('subscribe_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('unsubscribed', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('unsubscribe_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('newsletter', ['Subscription'])

        # Adding unique constraint on 'Subscription', fields ['user', 'email_field', 'newsletter']
        db.create_unique('newsletter_subscription', ['user_id', 'email', 'newsletter_id'])

        # Adding model 'Article'
        db.create_table('newsletter_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sortorder', self.gf('django.db.models.fields.PositiveIntegerField')(default=30, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('thumb', self.gf('django.db.models.fields.CharField')(max_length=600, null=True, blank=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(related_name='articles', to=orm['newsletter.Message'])),
        ))
        db.send_create_signal('newsletter', ['Article'])

        # Adding model 'Message'
        db.create_table('newsletter_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('newsletter', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['newsletter.Newsletter'])),
            ('date_create', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modify', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('newsletter', ['Message'])

        # Adding unique constraint on 'Message', fields ['slug', 'newsletter']
        db.create_unique('newsletter_message', ['slug', 'newsletter_id'])

        # Adding model 'Submission'
        db.create_table('newsletter_submission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('newsletter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['newsletter.Newsletter'])),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(default=2, to=orm['newsletter.Message'])),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 11, 19, 0, 0), null=True, db_index=True, blank=True)),
            ('publish', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('prepared', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('sending', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('newsletter', ['Submission'])

        # Adding M2M table for field subscriptions on 'Submission'
        db.create_table('newsletter_submission_subscriptions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['newsletter.submission'], null=False)),
            ('subscription', models.ForeignKey(orm['newsletter.subscription'], null=False))
        ))
        db.create_unique('newsletter_submission_subscriptions', ['submission_id', 'subscription_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Message', fields ['slug', 'newsletter']
        db.delete_unique('newsletter_message', ['slug', 'newsletter_id'])

        # Removing unique constraint on 'Subscription', fields ['user', 'email_field', 'newsletter']
        db.delete_unique('newsletter_subscription', ['user_id', 'email', 'newsletter_id'])

        # Removing unique constraint on 'EmailTemplate', fields ['title', 'action']
        db.delete_unique('newsletter_emailtemplate', ['title', 'action'])

        # Deleting model 'EmailTemplate'
        db.delete_table('newsletter_emailtemplate')

        # Deleting model 'Newsletter'
        db.delete_table('newsletter_newsletter')

        # Removing M2M table for field site on 'Newsletter'
        db.delete_table('newsletter_newsletter_site')

        # Deleting model 'Subscription'
        db.delete_table('newsletter_subscription')

        # Deleting model 'Article'
        db.delete_table('newsletter_article')

        # Deleting model 'Message'
        db.delete_table('newsletter_message')

        # Deleting model 'Submission'
        db.delete_table('newsletter_submission')

        # Removing M2M table for field subscriptions on 'Submission'
        db.delete_table('newsletter_submission_subscriptions')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        user_model_label: {
            'Meta': {'object_name': User.__name__, 'db_table': "'%s'" % User._meta.db_table},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'newsletter.article': {
            'Meta': {'ordering': "('sortorder',)", 'object_name': 'Article'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'articles'", 'to': "orm['newsletter.Message']"}),
            'sortorder': ('django.db.models.fields.PositiveIntegerField', [], {'default': '30', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'thumb': ('django.db.models.fields.CharField', [], {'max_length': '600', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'newsletter.emailtemplate': {
            'Meta': {'ordering': "('title',)", 'unique_together': "(('title', 'action'),)", 'object_name': 'EmailTemplate'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Default'", 'max_length': '200'})
        },
        'newsletter.message': {
            'Meta': {'unique_together': "(('slug', 'newsletter'),)", 'object_name': 'Message'},
            'date_create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modify': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['newsletter.Newsletter']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'newsletter.newsletter': {
            'Meta': {'object_name': 'Newsletter'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_template': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'message_template'", 'to': "orm['newsletter.EmailTemplate']"}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'site': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'subscribe_template': ('django.db.models.fields.related.ForeignKey', [], {'default': '2', 'related_name': "'subcribe_template'", 'to': "orm['newsletter.EmailTemplate']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unsubscribe_template': ('django.db.models.fields.related.ForeignKey', [], {'default': '3', 'related_name': "'unsubcribe_template'", 'to': "orm['newsletter.EmailTemplate']"}),
            'update_template': ('django.db.models.fields.related.ForeignKey', [], {'default': '4', 'related_name': "'update_template'", 'to': "orm['newsletter.EmailTemplate']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'})
        },
        'newsletter.submission': {
            'Meta': {'object_name': 'Submission'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'default': '2', 'to': "orm['newsletter.Message']"}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['newsletter.Newsletter']"}),
            'prepared': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'publish': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 19, 0, 0)', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'sending': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'subscriptions': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'to': "orm['newsletter.Subscription']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'newsletter.subscription': {
            'Meta': {'unique_together': "(('user', 'email_field', 'newsletter'),)", 'object_name': 'Subscription'},
            'activation_code': ('django.db.models.fields.CharField', [], {'default': "'08b41d231f04490b0bfb77553fb8a7c6ea9a6376'", 'max_length': '40'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email_field': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '75', 'null': 'True', 'db_column': "'email'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'name_field': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'db_column': "'name'", 'blank': 'True'}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['newsletter.Newsletter']"}),
            'subscribe_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subscribed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'unsubscribe_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'unsubscribed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['%s']" % user_orm_label, 'null': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['newsletter']
