# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Setting'
        db.create_table(u'maps_setting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('DEFAULT_GEO_RECORD_ID', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'maps', ['Setting'])


    def backwards(self, orm):
        # Deleting model 'Setting'
        db.delete_table(u'maps_setting')


    models = {
        u'maps.geofile': {
            'Meta': {'object_name': 'GeoFile'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'maps.linestringmapfeature': {
            'Meta': {'object_name': 'LineStringMapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geo_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'geo_level': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'geo_meta': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maps.ShapeFile']"})
        },
        u'maps.maplayer': {
            'Meta': {'object_name': 'MapLayer'},
            'available_on_maps': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'shapefiles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['maps.ShapeFile']", 'symmetrical': 'False'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'maps.pointmapfeature': {
            'Meta': {'object_name': 'PointMapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geo_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'geo_level': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'geo_meta': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maps.ShapeFile']"})
        },
        u'maps.polygonmapfeature': {
            'Meta': {'object_name': 'PolygonMapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geo_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'geo_level': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'geo_meta': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maps.ShapeFile']"})
        },
        u'maps.setting': {
            'DEFAULT_GEO_RECORD_ID': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'Meta': {'object_name': 'Setting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'maps.shapefile': {
            'Meta': {'object_name': 'ShapeFile'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geo_key_column': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'geo_meta_key_column': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'geom_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_column': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'shape_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zoom_threshold': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        }
    }

    complete_apps = ['maps']