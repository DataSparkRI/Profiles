# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AboutTopic'
        db.create_table(u'userguides_abouttopic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')(blank=True)),
        ))
        db.send_create_signal(u'userguides', ['AboutTopic'])

        # Adding model 'AboutPost'
        db.create_table(u'userguides_aboutpost', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post_title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('topics', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userguides.AboutTopic'], blank=True)),
            ('display_order', self.gf('django.db.models.fields.IntegerField')(blank=True)),
        ))
        db.send_create_signal(u'userguides', ['AboutPost'])


    def backwards(self, orm):
        # Deleting model 'AboutTopic'
        db.delete_table(u'userguides_abouttopic')

        # Deleting model 'AboutPost'
        db.delete_table(u'userguides_aboutpost')


    models = {
        u'userguides.aboutpost': {
            'Meta': {'object_name': 'AboutPost'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post_title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'topics': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['userguides.AboutTopic']", 'blank': 'True'})
        },
        u'userguides.abouttopic': {
            'Meta': {'object_name': 'AboutTopic'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        }
    }

    complete_apps = ['userguides']