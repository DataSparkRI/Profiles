# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MapFeature'
        db.create_table('maps_mapfeature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maps.MapLayer'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('muni', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('maps', ['MapFeature'])

        # Adding model 'MapLayer'
        db.create_table('maps_maplayer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('shape_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('available_on_maps', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('maps', ['MapLayer'])


    def backwards(self, orm):
        
        # Deleting model 'MapFeature'
        db.delete_table('maps_mapfeature')

        # Deleting model 'MapLayer'
        db.delete_table('maps_maplayer')


    models = {
        'maps.mapfeature': {
            'Meta': {'object_name': 'MapFeature'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'muni': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maps.MapLayer']"})
        },
        'maps.maplayer': {
            'Meta': {'object_name': 'MapLayer'},
            'available_on_maps': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'shape_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['maps']
