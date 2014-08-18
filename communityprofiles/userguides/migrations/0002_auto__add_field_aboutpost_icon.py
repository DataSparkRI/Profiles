# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AboutPost.icon'
        db.add_column(u'userguides_aboutpost', 'icon',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AboutPost.icon'
        db.delete_column(u'userguides_aboutpost', 'icon')


    models = {
        u'userguides.aboutpost': {
            'Meta': {'object_name': 'AboutPost'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
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