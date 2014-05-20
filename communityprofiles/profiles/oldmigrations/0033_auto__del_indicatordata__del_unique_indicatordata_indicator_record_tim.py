# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'IndicatorData', fields ['indicator', 'record', 'time']
        db.delete_unique('profiles_indicatordata', ['indicator_id', 'record_id', 'time_id'])

        # Deleting model 'IndicatorData'
        db.delete_table('profiles_indicatordata')

        # Adding model 'DataPoint'
        db.create_table('profiles_datapoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.GeoRecord'])),
            ('time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Time'], null=True)),
            ('change_from_time', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datapoint_as_change_from', null=True, to=orm['profiles.Time'])),
            ('change_to_time', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datapoint_as_change_to', null=True, to=orm['profiles.Time'])),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('profiles', ['DataPoint'])

        # Adding unique constraint on 'DataPoint', fields ['indicator', 'record', 'time']
        db.create_unique('profiles_datapoint', ['indicator_id', 'record_id', 'time_id'])

        # Adding model 'DenominatorPart'
        db.create_table('profiles_denominatorpart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.DataSource'])),
            ('formula', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('data', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('denominator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Denominator'])),
            ('part', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.IndicatorPart'])),
        ))
        db.send_create_signal('profiles', ['DenominatorPart'])

        # Adding model 'Denominator'
        db.create_table('profiles_denominator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('sort', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal('profiles', ['Denominator'])

        # Adding model 'Value'
        db.create_table('profiles_value', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datapoint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.DataPoint'])),
            ('denominator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Denominator'], null=True)),
            ('number', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('percent', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('moe', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('profiles', ['Value'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'DataPoint', fields ['indicator', 'record', 'time']
        db.delete_unique('profiles_datapoint', ['indicator_id', 'record_id', 'time_id'])

        # Adding model 'IndicatorData'
        db.create_table('profiles_indicatordata', (
            ('change_to_time', self.gf('django.db.models.fields.related.ForeignKey')(related_name='data_as_change_to', null=True, to=orm['profiles.Time'])),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('change_from_time', self.gf('django.db.models.fields.related.ForeignKey')(related_name='data_as_change_from', null=True, to=orm['profiles.Time'])),
            ('moe', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('percent', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.GeoRecord'])),
            ('time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Time'], null=True)),
        ))
        db.send_create_signal('profiles', ['IndicatorData'])

        # Adding unique constraint on 'IndicatorData', fields ['indicator', 'record', 'time']
        db.create_unique('profiles_indicatordata', ['indicator_id', 'record_id', 'time_id'])

        # Deleting model 'DataPoint'
        db.delete_table('profiles_datapoint')

        # Deleting model 'DenominatorPart'
        db.delete_table('profiles_denominatorpart')

        # Deleting model 'Denominator'
        db.delete_table('profiles_denominator')

        # Deleting model 'Value'
        db.delete_table('profiles_value')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'profiles.datadisplay': {
            'Meta': {'object_name': 'DataDisplay'},
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Indicator']", 'null': 'True', 'blank': 'True'}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.GeoRecord']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'subsubtitle': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.DataDisplayTemplate']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'profiles.datadisplaytemplate': {
            'Meta': {'object_name': 'DataDisplayTemplate'},
            'display_type': ('django.db.models.fields.CharField', [], {'default': "'STANDARD'", 'max_length': '11'}),
            'domains': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.DataDomain']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.Indicator']", 'symmetrical': 'False', 'blank': 'True'}),
            'levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.GeoLevel']", 'symmetrical': 'False', 'blank': 'True'}),
            'records': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.GeoRecord']", 'symmetrical': 'False', 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'subsubtitle': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'profiles.datadomain': {
            'Meta': {'object_name': 'DataDomain'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.Indicator']", 'through': "orm['profiles.IndicatorDomain']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20', 'db_index': 'True'}),
            'weight': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        'profiles.datapoint': {
            'Meta': {'unique_together': "(('indicator', 'record', 'time'),)", 'object_name': 'DataPoint'},
            'change_from_time': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datapoint_as_change_from'", 'null': 'True', 'to': "orm['profiles.Time']"}),
            'change_to_time': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datapoint_as_change_to'", 'null': 'True', 'to': "orm['profiles.Time']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Indicator']"}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.GeoRecord']"}),
            'time': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Time']", 'null': 'True'})
        },
        'profiles.datasource': {
            'Meta': {'object_name': 'DataSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implementation': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'profiles.denominator': {
            'Meta': {'object_name': 'Denominator'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Indicator']"}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'sort': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        'profiles.denominatorpart': {
            'Meta': {'object_name': 'DenominatorPart'},
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.DataSource']"}),
            'denominator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Denominator']"}),
            'formula': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Indicator']"}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.IndicatorPart']"})
        },
        'profiles.geolevel': {
            'Meta': {'object_name': 'GeoLevel'},
            'data_sources': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.DataSource']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.GeoLevel']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        'profiles.georecord': {
            'Meta': {'unique_together': "(('slug', 'level'), ('level', 'geo_id', 'custom_name', 'owner'))", 'object_name': 'GeoRecord'},
            'components': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'components_rel_+'", 'blank': 'True', 'to': "orm['profiles.GeoRecord']"}),
            'custom_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'geo_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.GeoLevel']"}),
            'mappings': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mappings_rel_+'", 'blank': 'True', 'to': "orm['profiles.GeoRecord']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.GeoRecord']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '100', 'blank': 'True'})
        },
        'profiles.indicator': {
            'Meta': {'object_name': 'Indicator'},
            'data_domains': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.DataDomain']", 'through': "orm['profiles.IndicatorDomain']", 'symmetrical': 'False'}),
            'data_type': ('django.db.models.fields.CharField', [], {'default': "'COUNT'", 'max_length': '10'}),
            'display_change': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'display_percent': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.GeoLevel']", 'symmetrical': 'False'}),
            'limitations': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'long_definition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'purpose': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'routine_use': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'short_definition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'universe': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        'profiles.indicatordomain': {
            'Meta': {'object_name': 'IndicatorDomain'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.DataDomain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Indicator']"})
        },
        'profiles.indicatorpart': {
            'Meta': {'object_name': 'IndicatorPart'},
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.DataSource']"}),
            'formula': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Indicator']"}),
            'time': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Time']"})
        },
        'profiles.time': {
            'Meta': {'object_name': 'Time'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sort': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '1'})
        },
        'profiles.value': {
            'Meta': {'object_name': 'Value'},
            'datapoint': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.DataPoint']"}),
            'denominator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Denominator']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moe': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'number': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        }
    }

    complete_apps = ['profiles']
