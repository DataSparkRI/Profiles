# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PointOverlayIcon'
        db.create_table(u'maps_pointoverlayicon', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'maps', ['PointOverlayIcon'])

        # Deleting field 'PointOverlay.updated_at'
        db.delete_column(u'maps_pointoverlay', 'updated_at')

        # Deleting field 'PointOverlay.created_at'
        db.delete_column(u'maps_pointoverlay', 'created_at')

        # Adding field 'PointOverlay.icon'
        db.add_column(u'maps_pointoverlay', 'icon',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['maps.PointOverlayIcon']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'PointOverlayIcon'
        db.delete_table(u'maps_pointoverlayicon')

        # Adding field 'PointOverlay.updated_at'
        db.add_column(u'maps_pointoverlay', 'updated_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2014, 7, 11, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'PointOverlay.created_at'
        db.add_column(u'maps_pointoverlay', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 7, 11, 0, 0), blank=True),
                      keep_default=False)

        # Deleting field 'PointOverlay.icon'
        db.delete_column(u'maps_pointoverlay', 'icon_id')


    models = {
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
        u'maps.pointoverlay': {
            'Meta': {'object_name': 'PointOverlay'},
            'available_on_maps': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'icon': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maps.PointOverlayIcon']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maps.ShapeFile']"})
        },
        u'maps.pointoverlayicon': {
            'Meta': {'object_name': 'PointOverlayIcon'},
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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