# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StayInTouchUser'
        db.create_table(u'userguides_stayintouchuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=254)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'userguides', ['StayInTouchUser'])


    def backwards(self, orm):
        # Deleting model 'StayInTouchUser'
        db.delete_table(u'userguides_stayintouchuser')


    models = {
        u'userguides.aboutpost': {
            'Meta': {'object_name': 'AboutPost'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post_title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'topics': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['userguides.AboutTopic']", 'blank': 'True'})
        },
        u'userguides.abouttopic': {
            'Meta': {'object_name': 'AboutTopic'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'userguides.faq': {
            'Meta': {'object_name': 'faq'},
            'answer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'userguides.stayintouchuser': {
            'Meta': {'object_name': 'StayInTouchUser'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['userguides']