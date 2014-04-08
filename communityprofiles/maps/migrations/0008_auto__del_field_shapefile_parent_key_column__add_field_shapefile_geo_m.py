# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'ShapeFile.parent_key_column'
        db.delete_column(u'maps_shapefile', 'parent_key_column')

        # Adding field 'ShapeFile.geo_meta_key_column'
        db.add_column(u'maps_shapefile', 'geo_meta_key_column', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'PolygonMapFeature.geo_meta'
        db.add_column(u'maps_polygonmapfeature', 'geo_meta', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Adding field 'LineStringMapFeature.geo_meta'
        db.add_column(u'maps_linestringmapfeature', 'geo_meta', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Adding field 'PointMapFeature.geo_meta'
        db.add_column(u'maps_pointmapfeature', 'geo_meta', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'ShapeFile.parent_key_column'
        db.add_column(u'maps_shapefile', 'parent_key_column', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Deleting field 'ShapeFile.geo_meta_key_column'
        db.delete_column(u'maps_shapefile', 'geo_meta_key_column')

        # Deleting field 'PolygonMapFeature.geo_meta'
        db.delete_column(u'maps_polygonmapfeature', 'geo_meta')

        # Deleting field 'LineStringMapFeature.geo_meta'
        db.delete_column(u'maps_linestringmapfeature', 'geo_meta')

        # Deleting field 'PointMapFeature.geo_meta'
        db.delete_column(u'maps_pointmapfeature', 'geo_meta')


    models = {
        u'maps.linestringmapfeature': {
            'Meta': {'object_name': 'LineStringMapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geo_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
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
            'geo_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geo_meta': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maps.ShapeFile']"})
        },
        u'maps.polygonmapfeature': {
            'Meta': {'object_name': 'PolygonMapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geo_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geo_meta': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maps.ShapeFile']"})
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
