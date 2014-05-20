# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'IndicatorDomain'
        db.create_table(u'profiles_indicatordomain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.DataDomain'])),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'profiles', ['IndicatorDomain'])

        # Adding model 'Group'
        db.create_table(u'profiles_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['Group'])

        # Adding model 'GroupIndex'
        db.create_table(u'profiles_groupindex', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=1, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('groups', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Group'])),
            ('indicators', self.gf('django.db.models.fields.related.ForeignKey')(related_name='groups', to=orm['profiles.Indicator'])),
        ))
        db.send_create_signal(u'profiles', ['GroupIndex'])

        # Adding model 'DataDomainIndex'
        db.create_table(u'profiles_datadomainindex', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=1, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('dataDomain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.DataDomain'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Group'])),
        ))
        db.send_create_signal(u'profiles', ['DataDomainIndex'])

        # Adding model 'DataDomain'
        db.create_table(u'profiles_datadomain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100, db_index=True)),
            ('weight', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('subdomain_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['DataDomain'])

        # Adding M2M table for field subdomains on 'DataDomain'
        db.create_table(u'profiles_datadomain_subdomains', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_datadomain', models.ForeignKey(orm[u'profiles.datadomain'], null=False)),
            ('to_datadomain', models.ForeignKey(orm[u'profiles.datadomain'], null=False))
        ))
        db.create_unique(u'profiles_datadomain_subdomains', ['from_datadomain_id', 'to_datadomain_id'])

        # Adding model 'GeoLevel'
        db.create_table(u'profiles_geolevel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=200, null=True, blank=True)),
            ('year', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=200, db_index=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.GeoLevel'], null=True, blank=True)),
            ('summary_level', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('shapefile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maps.ShapeFile'], null=True, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['GeoLevel'])

        # Adding M2M table for field data_sources on 'GeoLevel'
        db.create_table(u'profiles_geolevel_data_sources', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('geolevel', models.ForeignKey(orm[u'profiles.geolevel'], null=False)),
            ('datasource', models.ForeignKey(orm[u'profiles.datasource'], null=False))
        ))
        db.create_unique(u'profiles_geolevel_data_sources', ['geolevel_id', 'datasource_id'])

        # Adding model 'GeoRecord'
        db.create_table(u'profiles_georecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.GeoLevel'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=100, blank=True)),
            ('geo_id', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('geo_searchable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('geo_id_segments', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.GeoRecord'], null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('custom_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['GeoRecord'])

        # Adding unique constraint on 'GeoRecord', fields ['slug', 'level']
        db.create_unique(u'profiles_georecord', ['slug', 'level_id'])

        # Adding unique constraint on 'GeoRecord', fields ['level', 'geo_id', 'custom_name', 'owner']
        db.create_unique(u'profiles_georecord', ['level_id', 'geo_id', 'custom_name', 'owner_id'])

        # Adding M2M table for field components on 'GeoRecord'
        db.create_table(u'profiles_georecord_components', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_georecord', models.ForeignKey(orm[u'profiles.georecord'], null=False)),
            ('to_georecord', models.ForeignKey(orm[u'profiles.georecord'], null=False))
        ))
        db.create_unique(u'profiles_georecord_components', ['from_georecord_id', 'to_georecord_id'])

        # Adding M2M table for field mappings on 'GeoRecord'
        db.create_table(u'profiles_georecord_mappings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_georecord', models.ForeignKey(orm[u'profiles.georecord'], null=False)),
            ('to_georecord', models.ForeignKey(orm[u'profiles.georecord'], null=False))
        ))
        db.create_unique(u'profiles_georecord_mappings', ['from_georecord_id', 'to_georecord_id'])

        # Adding model 'DataSource'
        db.create_table(u'profiles_datasource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('implementation', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'profiles', ['DataSource'])

        # Adding model 'Time'
        db.create_table(u'profiles_time', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('sort', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=1)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['Time'])

        # Adding model 'Indicator'
        db.create_table(u'profiles_indicator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100, db_index=True)),
            ('data_type', self.gf('django.db.models.fields.CharField')(default='COUNT', max_length=30)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('short_definition', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('long_definition', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('purpose', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('universe', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('limitations', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('routine_use', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(default='U.S. Census Bureau', max_length=300, blank=True)),
            ('display_percent', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('display_change', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('display_distribution', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_generated_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_modified_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['Indicator'])

        # Adding M2M table for field indicator_tasks on 'Indicator'
        db.create_table(u'profiles_indicator_indicator_tasks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('indicator', models.ForeignKey(orm[u'profiles.indicator'], null=False)),
            ('indicatortask', models.ForeignKey(orm[u'profiles.indicatortask'], null=False))
        ))
        db.create_unique(u'profiles_indicator_indicator_tasks', ['indicator_id', 'indicatortask_id'])

        # Adding model 'IndicatorPart'
        db.create_table(u'profiles_indicatorpart', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.DataSource'])),
            ('formula', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('data', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Time'])),
        ))
        db.send_create_signal(u'profiles', ['IndicatorPart'])

        # Adding M2M table for field levels on 'IndicatorPart'
        db.create_table(u'profiles_indicatorpart_levels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('indicatorpart', models.ForeignKey(orm[u'profiles.indicatorpart'], null=False)),
            ('geolevel', models.ForeignKey(orm[u'profiles.geolevel'], null=False))
        ))
        db.create_unique(u'profiles_indicatorpart_levels', ['indicatorpart_id', 'geolevel_id'])

        # Adding model 'Denominator'
        db.create_table(u'profiles_denominator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('table_label', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('multiplier', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('sort', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=100, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['Denominator'])

        # Adding model 'DenominatorPart'
        db.create_table(u'profiles_denominatorpart', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.DataSource'])),
            ('formula', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('data', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('denominator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Denominator'])),
            ('part', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.IndicatorPart'])),
        ))
        db.send_create_signal(u'profiles', ['DenominatorPart'])

        # Adding M2M table for field levels on 'DenominatorPart'
        db.create_table(u'profiles_denominatorpart_levels', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('denominatorpart', models.ForeignKey(orm[u'profiles.denominatorpart'], null=False)),
            ('geolevel', models.ForeignKey(orm[u'profiles.geolevel'], null=False))
        ))
        db.create_unique(u'profiles_denominatorpart_levels', ['denominatorpart_id', 'geolevel_id'])

        # Adding model 'DataPoint'
        db.create_table(u'profiles_datapoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.GeoRecord'])),
            ('time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Time'], null=True)),
            ('change_from_time', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datapoint_as_change_from', null=True, to=orm['profiles.Time'])),
            ('change_to_time', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datapoint_as_change_to', null=True, to=orm['profiles.Time'])),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['DataPoint'])

        # Adding unique constraint on 'DataPoint', fields ['indicator', 'record', 'time']
        db.create_unique(u'profiles_datapoint', ['indicator_id', 'record_id', 'time_id'])

        # Adding model 'Value'
        db.create_table(u'profiles_value', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datapoint', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.DataPoint'])),
            ('denominator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Denominator'], null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('percent', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('moe', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['Value'])

        # Adding model 'CustomValue'
        db.create_table(u'profiles_customvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('value_operator', self.gf('django.db.models.fields.CharField')(max_length='255')),
            ('display_value', self.gf('django.db.models.fields.CharField')(max_length='255')),
            ('data_type', self.gf('django.db.models.fields.CharField')(default='COUNT', max_length=30)),
            ('supress', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'profiles', ['CustomValue'])

        # Adding model 'FlatValue'
        db.create_table(u'profiles_flatvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('display_title', self.gf('django.db.models.fields.CharField')(max_length='255', db_index=True)),
            ('indicator_slug', self.gf('django.db.models.fields.CharField')(max_length='255', db_index=True)),
            ('geography', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.GeoRecord'])),
            ('geography_name', self.gf('django.db.models.fields.CharField')(max_length='255')),
            ('geography_slug', self.gf('django.db.models.fields.CharField')(max_length='255', db_index=True)),
            ('geography_geo_key', self.gf('django.db.models.fields.CharField')(default=0, max_length='255', db_index=True)),
            ('value_type', self.gf('django.db.models.fields.CharField')(max_length='100')),
            ('time_key', self.gf('django.db.models.fields.CharField')(max_length='255')),
            ('geometry_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('percent', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('moe', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('numerator', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('numerator_moe', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('f_number', self.gf('django.db.models.fields.CharField')(max_length='255', null=True, blank=True)),
            ('f_percent', self.gf('django.db.models.fields.CharField')(max_length='255', null=True, blank=True)),
            ('f_moe', self.gf('django.db.models.fields.CharField')(max_length='255', null=True, blank=True)),
            ('f_numerator', self.gf('django.db.models.fields.CharField')(max_length='255', null=True, blank=True)),
            ('f_numerator_moe', self.gf('django.db.models.fields.CharField')(max_length='255', null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'profiles', ['FlatValue'])

        # Adding model 'PrecalculatedValue'
        db.create_table(u'profiles_precalculatedvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('table', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('geo_record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.GeoRecord'])),
            ('value', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('data_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.DataSource'])),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'profiles', ['PrecalculatedValue'])

        # Adding model 'LegendOption'
        db.create_table(u'profiles_legendoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'])),
            ('bin_type', self.gf('django.db.models.fields.CharField')(default='jenks', max_length=255)),
            ('bin_options', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal(u'profiles', ['LegendOption'])

        # Adding model 'TaskStatus'
        db.create_table(u'profiles_taskstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_seen', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('task', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('t_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('error', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('traceback', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['TaskStatus'])

        # Adding model 'IndicatorTask'
        db.create_table(u'profiles_indicatortask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Indicator'], null=True, blank=True)),
            ('task_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'profiles', ['IndicatorTask'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'DataPoint', fields ['indicator', 'record', 'time']
        db.delete_unique(u'profiles_datapoint', ['indicator_id', 'record_id', 'time_id'])

        # Removing unique constraint on 'GeoRecord', fields ['level', 'geo_id', 'custom_name', 'owner']
        db.delete_unique(u'profiles_georecord', ['level_id', 'geo_id', 'custom_name', 'owner_id'])

        # Removing unique constraint on 'GeoRecord', fields ['slug', 'level']
        db.delete_unique(u'profiles_georecord', ['slug', 'level_id'])

        # Deleting model 'IndicatorDomain'
        db.delete_table(u'profiles_indicatordomain')

        # Deleting model 'Group'
        db.delete_table(u'profiles_group')

        # Deleting model 'GroupIndex'
        db.delete_table(u'profiles_groupindex')

        # Deleting model 'DataDomainIndex'
        db.delete_table(u'profiles_datadomainindex')

        # Deleting model 'DataDomain'
        db.delete_table(u'profiles_datadomain')

        # Removing M2M table for field subdomains on 'DataDomain'
        db.delete_table('profiles_datadomain_subdomains')

        # Deleting model 'GeoLevel'
        db.delete_table(u'profiles_geolevel')

        # Removing M2M table for field data_sources on 'GeoLevel'
        db.delete_table('profiles_geolevel_data_sources')

        # Deleting model 'GeoRecord'
        db.delete_table(u'profiles_georecord')

        # Removing M2M table for field components on 'GeoRecord'
        db.delete_table('profiles_georecord_components')

        # Removing M2M table for field mappings on 'GeoRecord'
        db.delete_table('profiles_georecord_mappings')

        # Deleting model 'DataSource'
        db.delete_table(u'profiles_datasource')

        # Deleting model 'Time'
        db.delete_table(u'profiles_time')

        # Deleting model 'Indicator'
        db.delete_table(u'profiles_indicator')

        # Removing M2M table for field indicator_tasks on 'Indicator'
        db.delete_table('profiles_indicator_indicator_tasks')

        # Deleting model 'IndicatorPart'
        db.delete_table(u'profiles_indicatorpart')

        # Removing M2M table for field levels on 'IndicatorPart'
        db.delete_table('profiles_indicatorpart_levels')

        # Deleting model 'Denominator'
        db.delete_table(u'profiles_denominator')

        # Deleting model 'DenominatorPart'
        db.delete_table(u'profiles_denominatorpart')

        # Removing M2M table for field levels on 'DenominatorPart'
        db.delete_table('profiles_denominatorpart_levels')

        # Deleting model 'DataPoint'
        db.delete_table(u'profiles_datapoint')

        # Deleting model 'Value'
        db.delete_table(u'profiles_value')

        # Deleting model 'CustomValue'
        db.delete_table(u'profiles_customvalue')

        # Deleting model 'FlatValue'
        db.delete_table(u'profiles_flatvalue')

        # Deleting model 'PrecalculatedValue'
        db.delete_table(u'profiles_precalculatedvalue')

        # Deleting model 'LegendOption'
        db.delete_table(u'profiles_legendoption')

        # Deleting model 'TaskStatus'
        db.delete_table(u'profiles_taskstatus')

        # Deleting model 'IndicatorTask'
        db.delete_table(u'profiles_indicatortask')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 6, 13, 39, 33, 346653)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 6, 13, 39, 33, 345958)'}),
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
            'last_modified_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
