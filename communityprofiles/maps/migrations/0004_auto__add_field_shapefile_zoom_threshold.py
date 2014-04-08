# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ShapeFile.zoom_threshold'
        db.add_column('maps_shapefile', 'zoom_threshold', self.gf('django.db.models.fields.IntegerField')(default=5), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ShapeFile.zoom_threshold'
        db.delete_column('maps_shapefile', 'zoom_threshold')


    models = {
        'maps.linestringmapfeature': {
            'Meta': {'object_name': 'LineStringMapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'muni': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maps.ShapeFile']"})
        },
        'maps.maplayer': {
            'Meta': {'object_name': 'MapLayer'},
            'available_on_maps': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'maps.pointmapfeature': {
            'Meta': {'object_name': 'PointMapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'muni': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maps.ShapeFile']"})
        },
        'maps.polygonmapfeature': {
            'Meta': {'object_name': 'PolygonMapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'muni': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maps.ShapeFile']"})
        },
        'maps.shapefile': {
            'Meta': {'object_name': 'ShapeFile'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geom_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maps.MapLayer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'shape_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zoom_threshold': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        }
    }

    complete_apps = ['maps']
