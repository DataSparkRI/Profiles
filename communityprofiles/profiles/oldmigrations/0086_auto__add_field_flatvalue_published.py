# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'FlatValue.published'
        db.add_column(u'profiles_flatvalue', 'published', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'FlatValue.published'
        db.delete_column(u'profiles_flatvalue', 'published')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 12, 15, 0, 21, 606618)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 12, 15, 0, 21, 606228)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        },
        u'profiles.customvalue': {
            'Meta': {'object_name': 'CustomValue'},
            'data_type': ('django.db.models.fields.CharField', [], {'default': "'COUNT'", 'max_length': '30'}),
            'display_value': ('django.db.models.fields.CharField', [], {'max_length': "'255'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Indicator']"}),
            'supress': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'value_operator': ('django.db.models.fields.CharField', [], {'max_length': "'255'"})
        },
        u'profiles.datadomain': {
            'Meta': {'ordering': "['weight']", 'object_name': 'DataDomain'},
            'group': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['profiles.Group']", 'through': u"orm['profiles.DataDomainIndex']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicators': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['profiles.Indicator']", 'through': u"orm['profiles.IndicatorDomain']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'subdomain_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subdomains': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['profiles.DataDomain']", 'symmetrical': 'False', 'blank': 'True'}),
            'weight': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'profiles.datadomainindex': {
            'Meta': {'ordering': "['order']", 'object_name': 'DataDomainIndex'},
            'dataDomain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.DataDomain']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'profiles.datapoint': {
            'Meta': {'unique_together': "(('indicator', 'record', 'time'),)", 'object_name': 'DataPoint'},
            'change_from_time': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datapoint_as_change_from'", 'null': 'True', 'to': u"orm['profiles.Time']"}),
            'change_to_time': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datapoint_as_change_to'", 'null': 'True', 'to': u"orm['profiles.Time']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Indicator']"}),
            'record': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.GeoRecord']"}),
            'time': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Time']", 'null': 'True'})
        },
        u'profiles.datasource': {
            'Meta': {'object_name': 'DataSource'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implementation': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'profiles.denominator': {
            'Meta': {'object_name': 'Denominator'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Indicator']"}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'multiplier': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'sort': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'table_label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'profiles.denominatorpart': {
            'Meta': {'object_name': 'DenominatorPart'},
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.DataSource']"}),
            'denominator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Denominator']"}),
            'formula': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Indicator']"}),
            'levels': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['profiles.GeoLevel']", 'null': 'True', 'blank': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.IndicatorPart']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'profiles.flatvalue': {
            'Meta': {'object_name': 'FlatValue'},
            'display_title': ('django.db.models.fields.CharField', [], {'max_length': "'255'", 'db_index': 'True'}),
            'f_moe': ('django.db.models.fields.CharField', [], {'max_length': "'255'", 'null': 'True', 'blank': 'True'}),
            'f_number': ('django.db.models.fields.CharField', [], {'max_length': "'255'", 'null': 'True', 'blank': 'True'}),
            'f_numerator': ('django.db.models.fields.CharField', [], {'max_length': "'255'", 'null': 'True', 'blank': 'True'}),
            'f_numerator_moe': ('django.db.models.fields.CharField', [], {'max_length': "'255'", 'null': 'True', 'blank': 'True'}),
            'f_percent': ('django.db.models.fields.CharField', [], {'max_length': "'255'", 'null': 'True', 'blank': 'True'}),
            'geography': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.GeoRecord']"}),
            'geography_geo_key': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': "'255'", 'db_index': 'True'}),
            'geography_name': ('django.db.models.fields.CharField', [], {'max_length': "'255'"}),
            'geography_slug': ('django.db.models.fields.CharField', [], {'max_length': "'255'", 'db_index': 'True'}),
            'geometry_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Indicator']"}),
            'indicator_slug': ('django.db.models.fields.CharField', [], {'max_length': "'255'", 'db_index': 'True'}),
            'moe': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'number': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'numerator': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'numerator_moe': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'time_key': ('django.db.models.fields.CharField', [], {'max_length': "'255'"}),
            'value_type': ('django.db.models.fields.CharField', [], {'max_length': "'100'"})
        },
        u'profiles.geolevel': {
            'Meta': {'object_name': 'GeoLevel'},
            'data_sources': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['profiles.DataSource']", 'symmetrical': 'False', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.GeoLevel']", 'null': 'True', 'blank': 'True'}),
            'shapefile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maps.ShapeFile']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'summary_level': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'profiles.georecord': {
            'Meta': {'unique_together': "(('slug', 'level'), ('level', 'geo_id', 'custom_name', 'owner'))", 'object_name': 'GeoRecord'},
            'components': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'components_rel_+'", 'blank': 'True', 'to': u"orm['profiles.GeoRecord']"}),
            'custom_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'geo_id': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geo_id_segments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geo_searchable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.GeoLevel']"}),
            'mappings': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'mappings_rel_+'", 'blank': 'True', 'to': u"orm['profiles.GeoRecord']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.GeoRecord']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '100', 'blank': 'True'})
        },
        u'profiles.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicators': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['profiles.Indicator']", 'through': u"orm['profiles.GroupIndex']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'profiles.groupindex': {
            'Meta': {'ordering': "['order']", 'object_name': 'GroupIndex'},
            'groups': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicators': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': u"orm['profiles.Indicator']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'profiles.indicator': {
            'Meta': {'ordering': "['display_name', 'name']", 'object_name': 'Indicator'},
            'data_domains': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['profiles.DataDomain']", 'through': u"orm['profiles.IndicatorDomain']", 'symmetrical': 'False'}),
            'data_type': ('django.db.models.fields.CharField', [], {'default': "'COUNT'", 'max_length': '30'}),
            'display_change': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'display_distribution': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'display_percent': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator_tasks': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'ind_tasks'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['profiles.IndicatorTask']"}),
            'last_generated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['profiles.GeoLevel']", 'symmetrical': 'False'}),
            'limitations': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'long_definition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'purpose': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'routine_use': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'short_definition': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'default': "'U.S. Census Bureau'", 'max_length': '300', 'blank': 'True'}),
            'universe': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        u'profiles.indicatordomain': {
            'Meta': {'object_name': 'IndicatorDomain'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.DataDomain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Indicator']"})
        },
        u'profiles.indicatorpart': {
            'Meta': {'object_name': 'IndicatorPart'},
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.DataSource']"}),
            'formula': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Indicator']"}),
            'levels': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['profiles.GeoLevel']", 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'time': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Time']"})
        },
        u'profiles.indicatortask': {
            'Meta': {'object_name': 'IndicatorTask'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Indicator']", 'null': 'True', 'blank': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'profiles.legendoption': {
            'Meta': {'object_name': 'LegendOption'},
            'bin_options': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'bin_type': ('django.db.models.fields.CharField', [], {'default': "'jenks'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Indicator']"})
        },
        u'profiles.precalculatedvalue': {
            'Meta': {'object_name': 'PrecalculatedValue'},
            'data_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.DataSource']"}),
            'geo_record': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.GeoRecord']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'table': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'profiles.taskstatus': {
            'Meta': {'object_name': 'TaskStatus'},
            'error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            't_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'task': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'traceback': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'profiles.time': {
            'Meta': {'object_name': 'Time'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sort': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '1'})
        },
        u'profiles.value': {
            'Meta': {'object_name': 'Value'},
            'datapoint': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.DataPoint']"}),
            'denominator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.Denominator']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moe': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'number': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        }
    }

    complete_apps = ['profiles']
