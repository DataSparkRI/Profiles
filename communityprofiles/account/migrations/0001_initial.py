# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UserProfile'
        db.create_table('account_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_general_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_community_advocate', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_journalist', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_researcher', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_grant_writer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_city_state_agency_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_consultant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_legislator', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_policy_analyst', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_other', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('organization', self.gf('django.db.models.fields.CharField')(default='', max_length=300, blank=True)),
            ('org_is_non_profit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('org_is_state_city_agency', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('org_is_university', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('org_is_other', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('wants_notifications', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('account', ['UserProfile'])


    def backwards(self, orm):
        
        # Deleting model 'UserProfile'
        db.delete_table('account_userprofile')


    models = {
        'account.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_city_state_agency_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_community_advocate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_consultant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_general_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_grant_writer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_journalist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_legislator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_policy_analyst': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_researcher': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'org_is_non_profit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'org_is_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'org_is_state_city_agency': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'org_is_university': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organization': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'wants_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
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
        'auth.user': {
            'Meta': {'object_name': 'User'},
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
        }
    }

    complete_apps = ['account']
