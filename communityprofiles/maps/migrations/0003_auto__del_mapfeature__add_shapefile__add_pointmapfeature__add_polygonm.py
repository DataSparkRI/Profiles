# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'MapFeature'
        db.delete_table('maps_mapfeature')

        # Adding model 'ShapeFile'
        db.create_table('maps_shapefile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maps.MapLayer'])),
            ('geom_type', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('shape_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('maps', ['ShapeFile'])

        # Adding model 'PointMapFeature'
        db.create_table('maps_pointmapfeature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maps.ShapeFile'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('muni', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal('maps', ['PointMapFeature'])

        # Adding model 'PolygonMapFeature'
        db.create_table('maps_polygonmapfeature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maps.ShapeFile'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('muni', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('maps', ['PolygonMapFeature'])

        # Adding model 'LineStringMapFeature'
        db.create_table('maps_linestringmapfeature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maps.ShapeFile'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('muni', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')()),
        ))
        db.send_create_signal('maps', ['LineStringMapFeature'])

        # Deleting field 'MapLayer.shape_file'
        db.delete_column('maps_maplayer', 'shape_file')

        # Deleting field 'MapLayer.color'
        db.delete_column('maps_maplayer', 'color')


    def backwards(self, orm):
        # Adding model 'MapFeature'
        db.create_table('maps_mapfeature', (
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maps.MapLayer'])),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('muni', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('maps', ['MapFeature'])

        # Deleting model 'ShapeFile'
        db.delete_table('maps_shapefile')

        # Deleting model 'PointMapFeature'
        db.delete_table('maps_pointmapfeature')

        # Deleting model 'PolygonMapFeature'
        db.delete_table('maps_polygonmapfeature')

        # Deleting model 'LineStringMapFeature'
        db.delete_table('maps_linestringmapfeature')

        # Adding field 'MapLayer.shape_file'
        db.add_column('maps_maplayer', 'shape_file',
                      self.gf('django.db.models.fields.files.FileField')(default=None, max_length=100),
                      keep_default=False)

        # Adding field 'MapLayer.color'
        db.add_column('maps_maplayer', 'color',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


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
            'shape_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['maps']