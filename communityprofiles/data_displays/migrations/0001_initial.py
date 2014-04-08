# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DataVisualizationResource'
        db.create_table('data_displays_datavisualizationresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('source_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
        ))
        db.send_create_signal('data_displays', ['DataVisualizationResource'])

        # Adding model 'DataVisualization'
        db.create_table('data_displays_datavisualization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('data_displays', ['DataVisualization'])

        # Adding model 'DataVisualizationPart'
        db.create_table('data_displays_datavisualizationpart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('visualization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_displays.DataVisualization'], blank=True)),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_displays.DataVisualizationResource'], blank=True)),
            ('load_order', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('data_displays', ['DataVisualizationPart'])

        # Adding model 'DataDisplayTemplate'
        db.create_table('data_displays_datadisplaytemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('subtitle', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('subsubtitle', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('data_displays', ['DataDisplayTemplate'])

        # Adding M2M table for field visualizations on 'DataDisplayTemplate'
        db.create_table('data_displays_datadisplaytemplate_visualizations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datadisplaytemplate', models.ForeignKey(orm['data_displays.datadisplaytemplate'], null=False)),
            ('datavisualization', models.ForeignKey(orm['data_displays.datavisualization'], null=False))
        ))
        db.create_unique('data_displays_datadisplaytemplate_visualizations', ['datadisplaytemplate_id', 'datavisualization_id'])

        # Adding M2M table for field levels on 'DataDisplayTemplate'
        db.create_table('data_displays_datadisplaytemplate_levels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datadisplaytemplate', models.ForeignKey(orm['data_displays.datadisplaytemplate'], null=False)),
            ('geolevel', models.ForeignKey(orm['profiles.geolevel'], null=False))
        ))
        db.create_unique('data_displays_datadisplaytemplate_levels', ['datadisplaytemplate_id', 'geolevel_id'])

        # Adding M2M table for field records on 'DataDisplayTemplate'
        db.create_table('data_displays_datadisplaytemplate_records', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datadisplaytemplate', models.ForeignKey(orm['data_displays.datadisplaytemplate'], null=False)),
            ('georecord', models.ForeignKey(orm['profiles.georecord'], null=False))
        ))
        db.create_unique('data_displays_datadisplaytemplate_records', ['datadisplaytemplate_id', 'georecord_id'])

        # Adding M2M table for field domains on 'DataDisplayTemplate'
        db.create_table('data_displays_datadisplaytemplate_domains', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datadisplaytemplate', models.ForeignKey(orm['data_displays.datadisplaytemplate'], null=False)),
            ('datadomain', models.ForeignKey(orm['profiles.datadomain'], null=False))
        ))
        db.create_unique('data_displays_datadisplaytemplate_domains', ['datadisplaytemplate_id', 'datadomain_id'])

        # Adding M2M table for field indicators on 'DataDisplayTemplate'
        db.create_table('data_displays_datadisplaytemplate_indicators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datadisplaytemplate', models.ForeignKey(orm['data_displays.datadisplaytemplate'], null=False)),
            ('indicator', models.ForeignKey(orm['profiles.indicator'], null=False))
        ))
        db.create_unique('data_displays_datadisplaytemplate_indicators', ['datadisplaytemplate_id', 'indicator_id'])

        # Adding model 'DataDisplay'
        db.create_table('data_displays_datadisplay', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('subtitle', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('subsubtitle', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.GeoRecord'], null=True, blank=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'], null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Time'], null=True, blank=True)),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, blank=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['data_displays.DataDisplayTemplate'])),
            ('html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=100, blank=True)),
        ))
        db.send_create_signal('data_displays', ['DataDisplay'])


    def backwards(self, orm):
        
        # Deleting model 'DataVisualizationResource'
        db.delete_table('data_displays_datavisualizationresource')

        # Deleting model 'DataVisualization'
        db.delete_table('data_displays_datavisualization')

        # Deleting model 'DataVisualizationPart'
        db.delete_table('data_displays_datavisualizationpart')

        # Deleting model 'DataDisplayTemplate'
        db.delete_table('data_displays_datadisplaytemplate')

        # Removing M2M table for field visualizations on 'DataDisplayTemplate'
        db.delete_table('data_displays_datadisplaytemplate_visualizations')

        # Removing M2M table for field levels on 'DataDisplayTemplate'
        db.delete_table('data_displays_datadisplaytemplate_levels')

        # Removing M2M table for field records on 'DataDisplayTemplate'
        db.delete_table('data_displays_datadisplaytemplate_records')

        # Removing M2M table for field domains on 'DataDisplayTemplate'
        db.delete_table('data_displays_datadisplaytemplate_domains')

        # Removing M2M table for field indicators on 'DataDisplayTemplate'
        db.delete_table('data_displays_datadisplaytemplate_indicators')

        # Deleting model 'DataDisplay'
        db.delete_table('data_displays_datadisplay')


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
        'data_displays.datadisplay': {
            'Meta': {'object_name': 'DataDisplay'},
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Indicator']", 'null': 'True', 'blank': 'True'}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.GeoRecord']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '100', 'blank': 'True'}),
            'subsubtitle': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['data_displays.DataDisplayTemplate']"}),
            'time': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Time']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'data_displays.datadisplaytemplate': {
            'Meta': {'object_name': 'DataDisplayTemplate'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'domains': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.DataDomain']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.Indicator']", 'symmetrical': 'False', 'blank': 'True'}),
            'levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.GeoLevel']", 'symmetrical': 'False', 'blank': 'True'}),
            'records': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.GeoRecord']", 'symmetrical': 'False', 'blank': 'True'}),
            'subsubtitle': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'visualizations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['data_displays.DataVisualization']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'data_displays.datavisualization': {
            'Meta': {'object_name': 'DataVisualization'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'data_displays.datavisualizationpart': {
            'Meta': {'object_name': 'DataVisualizationPart'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load_order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['data_displays.DataVisualizationResource']", 'blank': 'True'}),
            'visualization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['data_displays.DataVisualization']", 'blank': 'True'})
        },
        'data_displays.datavisualizationresource': {
            'Meta': {'object_name': 'DataVisualizationResource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        'profiles.datadomain': {
            'Meta': {'object_name': 'DataDomain'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.Indicator']", 'through': "orm['profiles.IndicatorDomain']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20', 'db_index': 'True'}),
            'weight': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        'profiles.datasource': {
            'Meta': {'object_name': 'DataSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implementation': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
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
        'profiles.time': {
            'Meta': {'object_name': 'Time'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sort': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '1'})
        }
    }

    complete_apps = ['data_displays']
