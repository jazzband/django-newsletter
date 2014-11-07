# -*- coding: utf-8 -*-
import os

from django.conf import settings
from south.v2 import DataMigration

import newsletter


from ..utils import get_user_model
User = get_user_model()

user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.model_name)
user_ptr_name = '%s_ptr' % User._meta.object_name.lower()

class Migration(DataMigration):
    def get_template_path(self):
        """ Return the template path. """
        if not settings.TEMPLATE_DIRS:
            raise Exception(
                'TEMPLATE_DIRS not set, could not migrate templates from '
                'databse to file!'
            )

        return os.path.join(
            settings.TEMPLATE_DIRS[0], 'newsletter', 'message'
        )

    def write_template(self, path, template):
        print 'Writing email template from DB to %s' % path

        f = open(path, 'w')
        f.write(template.encode('utf-8'))
        f.close()

    def forwards(self, orm):
        """ Grab templates from database and write to template files. """

        for newsletter in orm.Newsletter.objects.all():
            template_path = os.path.join(
                self.get_template_path(), newsletter.slug
            )

            # Optionally, create template dir
            try:
                os.makedirs(template_path)
            except OSError:
                pass

            # Subscribe template HTML, text, subject
            self.write_template(
                os.path.join(template_path, 'subscribe.html'),
                newsletter.subscribe_template.html
            )

            self.write_template(
                os.path.join(template_path, 'subscribe.txt'),
                newsletter.subscribe_template.text
            )

            self.write_template(
                os.path.join(template_path, 'subscribe_subject.txt'),
                newsletter.subscribe_template.subject
            )

            # Unsubscribe template HTML, text, subject
            self.write_template(
                os.path.join(template_path, 'unsubscribe.html'),
                newsletter.unsubscribe_template.html
            )

            self.write_template(
                os.path.join(template_path, 'unsubscribe.txt'),
                newsletter.unsubscribe_template.text
            )

            self.write_template(
                os.path.join(template_path, 'unsubscribe_subject.txt'),
                newsletter.unsubscribe_template.subject
            )

            # Update template HTML, text, subject
            self.write_template(
                os.path.join(template_path, 'update.html'),
                newsletter.update_template.html
            )

            self.write_template(
                os.path.join(template_path, 'update.txt'),
                newsletter.update_template.text
            )

            self.write_template(
                os.path.join(template_path, 'update_subject.txt'),
                newsletter.update_template.subject
            )

            # Message template HTML, text, subject
            self.write_template(
                os.path.join(template_path, 'message.html'),
                newsletter.message_template.html
            )

            self.write_template(
                os.path.join(template_path, 'message.txt'),
                newsletter.message_template.text
            )

            self.write_template(
                os.path.join(template_path, 'message_subject.txt'),
                newsletter.message_template.subject
            )

    def backwards(self, orm):
        """
        Way too lazy to write backwards migration for this one. It would have
        to load templates from the files and put them in the database.

        Also, a full backwards mapping is impossible as in the old setup a
        single template can be used for multiple newsletters.
        """
        raise RuntimeError("Cannot reverse this migration.")

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
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'articles'", 'to': "orm['newsletter.Message']"}),
            'sortorder': ('django.db.models.fields.PositiveIntegerField', [], {'default': '20', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
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
            'message_template': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'message_template'", 'to': "orm['newsletter.EmailTemplate']"}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'site': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'subscribe_template': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'subcribe_template'", 'to': "orm['newsletter.EmailTemplate']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unsubscribe_template': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'unsubcribe_template'", 'to': "orm['newsletter.EmailTemplate']"}),
            'update_template': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'update_template'", 'to': "orm['newsletter.EmailTemplate']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'})
        },
        'newsletter.submission': {
            'Meta': {'object_name': 'Submission'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['newsletter.Message']"}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['newsletter.Newsletter']"}),
            'prepared': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'publish': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 5, 16, 0, 0)', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'sending': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'subscriptions': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'to': "orm['newsletter.Subscription']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'newsletter.subscription': {
            'Meta': {'unique_together': "(('user', 'email_field', 'newsletter'),)", 'object_name': 'Subscription'},
            'activation_code': ('django.db.models.fields.CharField', [], {'default': "'474708311b8ecc15d4e780f03193d222683d17f1'", 'max_length': '40'}),
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
    symmetrical = True
