# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ShapeFile.label_column'
        db.add_column('maps_shapefile', 'label_column', self.gf('django.db.models.fields.CharField')(default='', max_length=255), keep_default=False)

        # Adding field 'ShapeFile.geo_key_column'
        db.add_column('maps_shapefile', 'geo_key_column', self.gf('django.db.models.fields.CharField')(default='', max_length=255), keep_default=False)

        # Deleting field 'PolygonMapFeature.muni'
        db.delete_column('maps_polygonmapfeature', 'muni')

        # Adding field 'PolygonMapFeature.geo_key'
        db.add_column('maps_polygonmapfeature', 'geo_key', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Deleting field 'LineStringMapFeature.muni'
        db.delete_column('maps_linestringmapfeature', 'muni')

        # Adding field 'LineStringMapFeature.geo_key'
        db.add_column('maps_linestringmapfeature', 'geo_key', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Deleting field 'PointMapFeature.muni'
        db.delete_column('maps_pointmapfeature', 'muni')

        # Adding field 'PointMapFeature.geo_key'
        db.add_column('maps_pointmapfeature', 'geo_key', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ShapeFile.label_column'
        db.delete_column('maps_shapefile', 'label_column')

        # Deleting field 'ShapeFile.geo_key_column'
        db.delete_column('maps_shapefile', 'geo_key_column')

        # Adding field 'PolygonMapFeature.muni'
        db.add_column('maps_polygonmapfeature', 'muni', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Deleting field 'PolygonMapFeature.geo_key'
        db.delete_column('maps_polygonmapfeature', 'geo_key')

        # Adding field 'LineStringMapFeature.muni'
        db.add_column('maps_linestringmapfeature', 'muni', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Deleting field 'LineStringMapFeature.geo_key'
        db.delete_column('maps_linestringmapfeature', 'geo_key')

        # Adding field 'PointMapFeature.muni'
        db.add_column('maps_pointmapfeature', 'muni', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Deleting field 'PointMapFeature.geo_key'
        db.delete_column('maps_pointmapfeature', 'geo_key')


    models = {
        'maps.linestringmapfeature': {
            'Meta': {'object_name': 'LineStringMapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geo_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
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
            'geo_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maps.ShapeFile']"})
        },
        'maps.polygonmapfeature': {
            'Meta': {'object_name': 'PolygonMapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geo_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maps.ShapeFile']"})
        },
        'maps.shapefile': {
            'Meta': {'object_name': 'ShapeFile'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geo_key_column': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'geom_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_column': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maps.MapLayer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'shape_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zoom_threshold': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        }
    }

    complete_apps = ['maps']
