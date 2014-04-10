import re
import logging
from datetime import datetime
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from sorl.thumbnail import ImageField
from profiles.utils import unique_slugify, format_number, build_value_comparison, get_default_levels
from census import data as census_data
from maps.models import ShapeFile, PolygonMapFeature
from django.contrib.gis.db.models import Union
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core import serializers
import json
from adminsortable.fields import SortableForeignKey
from adminsortable.models import Sortable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class IndicatorDomain(models.Model):
    indicator = models.ForeignKey('Indicator')
    domain = models.ForeignKey('DataDomain')
    default = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s - %s" % (self.indicator, self.domain)

class Group(models.Model):

    name = models.CharField(max_length=100, unique=True, db_index=True, help_text="Display Name for this Group")
    order = models.PositiveIntegerField(null=True, blank=True)
    indicators = models.ManyToManyField('Indicator', through='GroupIndex')

    def sorted_indicators(self, level=None):
        if level is None:
            indicators = [g.indicators for g in GroupIndex.objects.filter(groups=self).only('indicators')]
        else:
            all_inds = [g.indicators for g in GroupIndex.objects.filter(groups=self).only('indicators')]
            # we need to reduce these indicators by the levels they contain
            indicators = []
            for ind in all_inds:
                if level in ind.levels:
                    indicators.append(ind)

        return indicators

    class Meta:
        pass

    def __unicode__(self):
        return self.name

class GroupIndex(Sortable):
    name = models.CharField(max_length=100, blank=True)
    groups = models.ForeignKey('Group')
    indicators = models.ForeignKey('Indicator', related_name='groups')

    class Meta(Sortable.Meta):
        pass

    def __unicode__(self):
        return self.name

class DataDomainIndex(Sortable):

    class Meta(Sortable.Meta):
        pass

    name = models.CharField(max_length=100)
    dataDomain = models.ForeignKey('DataDomain')
    group = models.ForeignKey('Group')
    #order = models.PositiveIntegerField(null=True, blank=True)
    class Meta(Sortable.Meta):
        pass

    def __unicode__(self):
        return self.group.name

class DataDomain(models.Model):

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    weight = models.PositiveIntegerField(default=1)
    indicators = models.ManyToManyField('Indicator', through='IndicatorDomain')
    group = models.ManyToManyField('Group', through='DataDomainIndex')
    subdomains = models.ManyToManyField('self', symmetrical=False, blank=True) # a datadomain that is "nested" under this one
    subdomain_only = models.BooleanField(default=False) # if False will appear in Nav
    order = models.PositiveIntegerField(null=True, blank=True)

    @property
    def sorted_groups(self):
        groups = [g.group for g in DataDomainIndex.objects.filter(dataDomain=self).only('group')]
        return groups

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['weight']


class GeoLevel(models.Model):
    """ Represents a level of geography
        Ex: State, Muni, Tract, block
        GeoLevels can have Parent GeoLevels. Ex: Tract->Muni->State"""
    name = models.CharField(max_length=200, db_index=True)
    display_name = models.CharField(max_length = 200, db_index=True, blank=True, null=True)
    year = models.CharField(max_length=200, blank=True, null=True) # year this level represents Ex: 2000, 2010, acs
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    data_sources = models.ManyToManyField('DataSource', blank=True) # This isnt used anymore
    summary_level = models.CharField(max_length=200, blank=True, null=True)
    shapefile = models.ForeignKey(ShapeFile, blank=True, null=True, on_delete=models.SET_NULL, help_text="The shapefile that contains the geometries for this level of Geography. Profiles expects this to be a Polygon type shapefile")

    @property
    def lev_name(self):
        if self.display_name:
            return self.display_name
        return self.name

    @property
    def sort_key(self):
        """ A property that returns the proper nesting level for a a geolevel """
        if self.summary_level == "040":
            return 1
        elif self.summary_level == "050":
            return 2
        elif self.summary_level == "060":
            return 3
        elif self.summary_level == "140":
            return 4
        elif self.summary_level == "150":
            return 5
        else:
            return 10

    def get_geojson(self):
        pass

    def save(self, *args, **kwargs):
        super(GeoLevel, self).save(*args, **kwargs)
        # we are gonna assign all the shapefiles associated with this Geolevel
        # a level
        for p in PolygonMapFeature.objects.filter(source=self.shapefile):
            logger.debug("Assigning PolyGeolevel: %s : %s" % (p.label, self.id))
            p.geo_level = self.id
            p.save()


    def __unicode__(self):
        if self.year:
            return self.name + ': ' + self.year
        else:
            return self.name


class GeoRecord(models.Model):
    """ A single geographic entity in a GeoLevel.

    """
    level = models.ForeignKey(GeoLevel)
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, blank=True, db_index=True)

    # GIS properties
    #shapefile = models.ForeignKey(ShapeFile, blank=True, null=True, on_delete=models.SET_NULL, help_text="The shapefile that contains the geometries for this GeoRecord. Profiles expects this to be a Polygon type shapefile")
    geo_id = models.TextField(null=True, blank=True)  # some ID string. any data source supporting th Feature's layer should understand it
    geo_searchable = models.BooleanField(default=False, help_text="Should this GeoRecord be included in GIS search?")
    geo_id_segments = models.TextField(null=True, blank=True) # If this field exists, its a census geo_id segmented

    parent = models.ForeignKey('self', null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    # A user defines a custom geography as an agglomeration of component GeoRecords
    custom_name = models.CharField(max_length=100, null=True, blank=True)
    owner = models.ForeignKey(User, null=True, blank=True)

    components = models.ManyToManyField('self', blank=True) # dont know what this is
    mappings = models.ManyToManyField('self', blank=True)

    objects = models.GeoManager()

    @property
    def shapefile(self):
        return self.level.shapefile

    def get_geom(self, union=False):
        """ Return the geometry associated with this Geo Record via the shapefile associated with it """
        if self.shapefile:
            if union:
                geoms = self.shapefile.polygonmapfeature_set.filter(geo_key=self.name).aggregate(Union('geom'))['geom__union']
            else:
                geoms = self.shapefile.polygonmapfeature_set.filter(geo_key=self.name)
            return geoms
        else:
            return []

    def get_geom_id(self):
        """ Return the id of a matching polygon"""
        if self.shapefile:
            geoms = self.shapefile.polygonmapfeature_set.filter(geo_key=self.geo_id).only('id')
            if geoms:
                return geoms[0].id
            else:
                return None


    def mapped_to(self, level):
        return self.mappings.filter(level=level)

    def child_ids(self):
        return GeoRecord.objects.filter(parent=self).values_list('id', flat=True)

    def child_records(self):
        return GeoRecord.objects.filter(parent=self).defer('mappings').order_by("name")

    def sibling_records(self, include_self=False):
        siblings = GeoRecord.objects.filter(level=self.level, parent=self.parent).defer('mappings')
        if not include_self:
            siblings.exclude(id=self.id)
        return siblings

    def get_absolute_url(self):
        return reverse('geo_record', kwargs={'geo_level_slug': self.level.slug,
            'geo_record_slug': self.slug}
        )

    def get_as_dict(self):
        """ returns the GeoRecord's structure as a dict
            Ex: {'state':'RI', 'municipality': 'Providence', 'tract':'Census Tract 11'}
        """
        structure = {}
        # iterate parents
        rec = self
        while rec.parent:
            structure[rec.parent.level.name] = rec.parent.name
            rec = rec.parent

        return {'id': self.id, 'slug':self.slug, 'level':self.level.name, 'name': self.name, 'geo_id':self.geo_id, 'parent_geos':structure}

    def get_parents_geo_ids(self):
        from collections import OrderedDict
        """ Return summary level and geoid of parent geos in a dict. They are ordered by the dict key"""
        rec = self
        parent_lev_count = 0 # to keep this dict ordered
        if rec.parent:
            parents = OrderedDict()
            while rec.parent:
                parent_lev_count += 1
                parents[parent_lev_count] = {'sum_lev':rec.parent.level.summary_level,
                                            'geo_id': rec.parent.geo_id,
                                            }
                rec = rec.parent
        else:
            parents = None

        return parents

    def get_state(self):
        rec = self
        while rec.parent:
            if rec.parent.level.slug == 'state':
                return rec.parent
            rec = rec.parent

    @property
    def census_id(self):
        """ Return the census designated id for this geo_record"""
        geoids = json.loads(self.geo_id_segments)
        sum_lev = self.level.summary_level
        return geoids[sum_lev]

    @property
    def sortable_name(self):
        """ Return a name to sort on. This is helpfull for names that need to sort as alphanum vs just alpha"""
        regex = re.compile("\d+")
        try:
            return regex.findall(self.name)[0]
        except IndexError:
            return self.name

    def save(self, *args, **kwargs):
        
        unique_slugify(self, self.name, queryset=GeoRecord.objects.filter(level=self.level))
        
        super(GeoRecord ,self).save(*args,**kwargs)
        default_levels = get_default_levels()

        try:
            if self.level.name in default_levels and self.level.year == None: # When Year is none, This is base geography
                # Lets "Reparent all the layers related to this main level so the user doesnt have to
                # 1) find matching GeoRecords who's level is different than this one
                matches = GeoRecord.objects.filter(name=self.name).exclude(level__name__in=default_levels, level__year=None).only('name', 'level')
                # now reparent this geo record to the apporiate matching NEW georecord
                targ_geo_name = self.parent.name
                targ_geo_lev_name = self.parent.level.name
                for match in matches:
                    try:
                        logger.debug("Reparenting: %s : %s" % (match.name, match.level.__unicode__()))
                        new_parent = GeoRecord.objects.get(name=targ_geo_name,level__name=targ_geo_lev_name, level__year = match.level.year)
                        match.parent = new_parent
                        match.save()
                    except Exception as e:
                        logger.error(e)

        except Exception:
            # this takes care of failures when importing Geographys
            pass

    class Meta:

        unique_together = (
            ('slug', 'level',),
            ('level', 'geo_id', 'custom_name', 'owner',),
        )

    def __unicode__(self):
        if self.custom_name:
            return u"%s - %s" % (self.level.name, self.custom_name)
        return u"ID: %s %s - %s -- %s" % (self.id, self.level.__unicode__(), self.name, self.geo_id)


class DataSource(models.Model):
    """ Represents the implementation of a data_adapters see communityprofiles/data_adapters.py"""
    name = models.CharField(max_length=100, unique=True)
    implementation = models.CharField(max_length=100, unique=True)

    def get_implementation(self):
        from django.utils.importlib import import_module
        module_name, class_name = self.implementation.rsplit('.', 1)
        return getattr(import_module(module_name), class_name)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.implementation)


class Time(models.Model):
    """ A time period """
    name = models.CharField(max_length=20)
    sort = models.DecimalField(max_digits=5, decimal_places=1)  # a numeric value# used for sorting
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name

DATA_TYPE_CHOICES = (
    ('COUNT', 'Count'),
    ('DECIMAL_1', 'Decimal 1'),
    ('DECIMAL_2', 'Decimal 2'),
    ('DOLLARS', 'Dollars'),
    ('AVERAGE_OR_MEDIAN_DOLLARS','$ Average or Median'),
    ('AVERAGE_OR_MEDIAN', 'Average or Median'),
    ('CUSTOM', 'Custom'),
)


class Indicator(models.Model):
    #levels = models.ManyToManyField(GeoLevel)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    data_domains = models.ManyToManyField(DataDomain, through='IndicatorDomain')
    data_type = models.CharField(max_length=30, choices=DATA_TYPE_CHOICES, default='COUNT')

    # metadata
    display_name = models.CharField(max_length=100)
    short_definition = models.TextField(blank=True)
    long_definition = models.TextField(blank=True)
    purpose = models.TextField(blank=True)  # aka rationale/implications
    universe = models.CharField(max_length=300, blank=True)
    limitations = models.TextField(blank=True)
    routine_use = models.TextField(blank=True)
    notes = models.TextField(blank=True)  # internal use misc notes
    source = models.CharField(max_length=300, blank=True, default='U.S. Census Bureau')
    display_percent = models.BooleanField(default=True)
    display_change = models.BooleanField(default=True)  # Generates a change value between the highest and lowest time part
    display_distribution = models.BooleanField(default=True)
    published = models.BooleanField(default=True)
    data_as_of = models.DateTimeField(verbose_name="Data As Of", blank=True, null=True, help_text='')
    last_generated_at = models.DateTimeField(verbose_name="Data Last Generated at", blank=True, null=True, help_text='This field is auto populated when the Indicator Data gets generated.') # save a date time when this indicator gets generated
    last_modified_at = models.DateTimeField(verbose_name="Indicator Meta Data Last Modified", blank=True, null=True, help_text="Last modified time. Updated everytime Indicator Meta data is saved")
    indicator_tasks = models.ManyToManyField('IndicatorTask', null=True, blank=True, related_name="ind_tasks")

    class Meta:
        ordering = ["display_name", "name"]

    def save(self, *args, **kwargs):
        self.last_modified_at = datetime.today()
        super(Indicator ,self).save(*args,**kwargs)

    @property
    def levels(self):
        parts = IndicatorPart.objects.filter(indicator=self).only('levels')
        levels_keys = set()
        for p in parts:
            for l in p.levels.all().only('pk'):
                levels_keys.add(l.pk)
        return GeoLevel.objects.filter(pk__in=levels_keys)

    def get_absolute_url(self):
        return "/profiles/preview/?i=%s" % str(self.id)

    def get_parts(self):
        """ Returns all Indicator Parts for this indicator"""
        return IndicatorPart.objects.filter(indicator=self).order_by('time__name')

    def get_times(self, name_only=False):
        """ Returns all time objects related to this Indicator"""
        times_uq = []
        times = []
        for part in self.get_parts():
            if part.time.name not in times_uq:
                times_uq.append(part.time.name)
                if name_only:
                    times.append(part.time.name)
                else:
                    times.append(part.time)
                    times.sort(key=lambda tm: tm.name)
        return times

    def get_slug_time_props(self):

        def html_escape(string):
            from cgi import escape
            return escape(string.replace("'", "&#39;").replace('"', "&quot;"))
            #return string

        t = {'slug':self.slug, 'times':self.get_times(name_only=True),
             'name':html_escape(self.display_name),
             'id':self.id,
             'denoms':[{'slug':d.slug, 'name':d.label} for d in self.denominator_set.all().only('slug','label')],

             }
        return json.dumps(t)

    def get_source_names(self):
        """ Return all sources and times used in this indicator"""
        sources = []
        for ip in self.indicatorpart_set.all():
            sources.append("{time}:{ds}".format(time=ip.time.name, ds=ip.data_source.name))
        for dp in self.denominatorpart_set.all():
            sources.append("{time}:{ds}".format(time=dp.time.name, ds=dp.data_source.name))
        return sources

    def get_tables(self, denom=False):
        """ Get the Formulas, we need to clean off the column nums
            TODO:This needs to get reworked when we rework indicators.
        """
        parts_list = []
        if denom is False:
            parts = self.indicatorpart_set.all().order_by('time__name')
        else:
            parts = self.denominatorpart_set.all().order_by('part__time__name')

        for i_p in parts:
            p = {}
            try:
                p['time'] = i_p.time.name
            except AttributeError:
                #denoms dont have times
                p['time'] = i_p.part.time.name
            tables = i_p.get_tables()
            if tables:
                p['tables'] = tables
                p['tables_str'] = ', '.join(p['tables'])
                parts_list.append(p)
        return parts_list

    def get_numerator_tables(self):
        return self.get_tables()

    def get_denominator_tables(self):
        return self.get_tables(True)

    def get_notes(self):
        """ Returns a list made up of long def, purpose, universe, limitation, notes
        or None if there is nothing in any of those fields
        """
        num_tbls = self.get_numerator_tables()
        denom_tbls = self.get_denominator_tables()
        notes = []
        if self.long_definition:
            notes.append({'label':'Definition', 'text':self.long_definition})
        if self.purpose:
            notes.append({'label':'Purpose', 'text':self.purpose })
        if self.universe:
            notes.append({'label':'Universe','text':self.universe })
        if self.limitations:
            notes.append({'label':'Limitations', 'text':self.limitations })
        if self.routine_use:
            notes.append({'label':'Routine', 'text':self.routine_use })
        if self.notes:
            notes.append({'label':'Notes', 'text':u''+self.notes})
        if self.source:
            notes.append({'label':'Source', 'text':self.source})
        if self.data_as_of:
            notes.append({'label':'Data As Of', 'text':self.data_as_of.strftime("%B, %d %Y")})

        #construct the tables string
        if num_tbls:
            txt = ""
            for t in num_tbls:
                txt += "%s: %s<br/>\n" % (t['time'], t['tables_str'])
            notes.append({'label':'Numerator Tables', 'text':txt})

        if denom_tbls:
            txt = ""
            for t in denom_tbls:
                txt += "%s: %s<br/>\n" % (t['time'], t['tables_str'])
            notes.append({'label':'Denominator Tables', 'text':txt})


        if notes:
            return notes
        else:
            return None

    def default_domain(self):
        """ Return the first domain marked as "default".
            If none are default, return some domain, but behavior is undefined in that case.
        """
        default = None
        for domain in IndicatorDomain.objects.filter(indicator=self).order_by('-default'):
            if domain.default:
                default = domain.domain
                break
            default = domain.domain
            break
        return default

    def collect_data(self, record):
        """
        Convinience Method
        Gets RAW Data from Census Rows for a single record, Does not create DataPoints
        Returns a list of IndicatorParts and Denoms associated with it that Part.
        """
        values = []
        denoms=[]
        for part in self.indicatorpart_set.all():
            part_value = part.value_for_geo(record)

            for denominator_part in DenominatorPart.objects.filter(part=part):
                denominator_value = denominator_part.value_for_geo(record) # gets value from census files
                if part_value is not None and not part_value.value is None and part_value.value != 0 and not denominator_value.value is None and not denominator_value.value == 0:
                    divided_result = part_value / denominator_value
                    if denominator_part.denominator.multiplier is not None:
                        divided_result *= census_data.Value(denominator_part.denominator.multiplier)
                        number = float(denominator_value.value) if denominator_value.value != None else None
                        moe = float(divided_result.moe) if divided_result.moe != None else None
                        denoms.append({"geo_rec" : {'name':record.name,'slug':record.slug},'name':denominator_part.denominator.label, 'time':part.time.name, 'value':str(divided_result) })

            values.append({"geo_rec" : {'name':record.name,'slug':record.slug}, "time":part.time.name, "value": str(part_value), 'denoms':denoms})

        return values

    def generate_data(self):
        """ Collects data from the stored census files and creates Datapoints for all levels"""
        # always flush out data
        DataPoint.objects.filter(indicator=self).delete()
        # -- INDICATORS
        for part in self.indicatorpart_set.all():

            for level in part.levels.all():
                try:
                    denominator_part = self.denominatorpart_set.filter(part=part)[0] # always return just one
                except IndexError:
                    denominator_part = None

                for record in level.georecord_set.filter(owner=None):
                    part_value = part.value_for_geo(record)
                    datapoint = DataPoint.objects.create(
                        indicator=self,
                        time=part.time,
                        record=record
                    )

                    if part_value is None:
                        continue

                    Value.objects.create(
                        datapoint=datapoint,
                        number=part_value.value,
                        moe=part_value.moe
                    )

                    # lets grab denoms here. Its kinda crappy to have to do a
                    # dumb query like what follows but since this process is
                    # admin initiated and goes into the task queue, I'm not
                    # gonna bother much with it.
                    if denominator_part != None:
                        denominator_value = denominator_part.value_for_geo(record)
                        if part_value is not None and not part_value.value is None and part_value.value != 0 \
                        and not denominator_value is None and denominator_value.value is not None and not denominator_value.value == 0:

                            divided_result = part_value / denominator_value

                            if denominator_part.denominator.multiplier is not None:
                                divided_result *= census_data.Value(denominator_part.denominator.multiplier)
                            Value.objects.create(
                                datapoint=datapoint,
                                denominator=denominator_part.denominator,
                                number=denominator_value.value, #this is the divisor
                                percent=divided_result.value,
                                moe=divided_result.moe
                            )

        self.last_generated_at = datetime.now()
        self.save()

    def generate_distribution(self):
        if not self.display_percent:
            return
        for datapoint in self.datapoint_set.all():
            datapoint.calculate_distribution()

    def generate_change(self):
        if not self.display_change:
            return
        DEFAULT_LEVELS = get_default_levels()
        # Datapoint objects with time = None are change values
        DataPoint.objects.filter(indicator=self, time=None).delete()

        levels = GeoLevel.objects.filter(name__in=DEFAULT_LEVELS)
        change_records = []

        for level in levels:
            change_records += list(GeoRecord.objects.filter(datapoint__indicator=self).filter(level=level).distinct())

        for record in change_records:
            first_datapoint = self.datapoint_set.filter(record=record).order_by('time__sort')[0]
            last_datapoint = self.datapoint_set.filter(record=record).order_by('-time__sort')[0]
            if not first_datapoint and not last_datapoint:
                continue
            if first_datapoint == last_datapoint:
                continue

            try:
                change_datapoint = DataPoint.objects.create(
                    indicator=self,
                    time=None,
                    change_from_time=first_datapoint.time,
                    change_to_time=last_datapoint.time,
                    record=record
                )

                Value.objects.create_for_change(
                    change_datapoint,
                    first_datapoint._count_value(),
                    last_datapoint._count_value(),
                    calculate_moe=False,
                    calculate_percent=self.display_percent
                )
            except Value.DoesNotExist:
                pass

            for denominator in self.denominator_set.all():
                try:
                    Value.objects.create_for_change(
                        change_datapoint,
                        first_datapoint.value_set.get(denominator=denominator),
                        last_datapoint.value_set.get(denominator=denominator),
                        denominator=denominator,
                        calculate_moe=False,
                        calculate_percent=self.display_percent
                    )
                except Value.DoesNotExist:
                    pass

    def get_indicator_href(self, geo_record, data_domain=None):
        # Get the href for the indicator, in the context of a geo_record
        if not data_domain:
            data_domain = self.default_domain()

        return reverse('indicator', kwargs={'geo_level_slug':geo_record.level.slug, 'geo_record_slug': geo_record.slug, 'data_domain_slug': data_domain.slug, 'indicator_slug': self.slug})

    def get_change(self, geo_record):
        if self.display_change:
            try:
                return Value.objects.get(datapoint__record=geo_record, datapoint__indicator=self, denominator=None, datapoint__time=None)
            except Value.DoesNotExist:
                return None
        else:
            return None

    def get_indicator_value(self, geo_record, time):
        """Returns a Value object for a specific GeoRecord and Time Period"""

        if geo_record is None or time is None:
            raise ValueError("GeoRecord and Time is required.")
        try:
            return Value.objects.get(datapoint__record=geo_record, datapoint__indicator=self, denominator=None, datapoint__time=time)
        except Value.DoesNotExist:
            return None

    def get_denominator_value(self, denominator, geo_record, time):
        """ Returns a Value object for a specific Denominator via GeoRecord and time
            This is mostly here so we dont have to rewrite a bunch of other code :D The actual getting is in the Denominator model
        """
        if denominator is None or geo_record is None or time is None:
            raise ValueError("Denominator, GeoRecord and Time is required.")

        return denominator.get_value(geo_record, time)

    def get_values_as_dict(self, geo_record, times=None):
        """ Returns Indicator Values in a structured Format"""
        if times:
            times = times
        else:
            times = self.get_times()
        denoms = self.denominator_set.all()
        data = {
            'indicator':{},
            'denominators':{}
        }
        #------------------------------BEGIN INDICATOR ------------------------------
        contains_suppressed_value = False

        for t in times:
            val = self.get_indicator_value(geo_record, t)
            if val:
                data['indicator'][t.name] = val.to_dict()
                #Check to see if these values contain suppressed values
                if data['indicator'][t.name]['number'] == -1:
                    contains_suppressed_value = True
            else:
                data['indicator'][t.name] = {} # No value

        # only collect change if there are no suppressed values
        if contains_suppressed_value == False:
            change = self.get_change(geo_record)
            if change:
                data['indicator']['change'] = change.to_dict()
        else:
            change = None

        #------------------------------BEGIN DENOMS-----------------------------------#
        if contains_suppressed_value == False:
            if denoms:
                data['denominators'] = {}
                for d in denoms:
                    data['denominators'][d.slug] = {}
                    dchange = d.get_change(geo_record)
                    if dchange:
                        data['denominators'][d.slug]['change'] = dchange.to_dict()
                    for t in times:
                        data['denominators'][d.slug][t.name] = {}
                        dval = d.get_value(geo_record, t)
                        indval = d.indicator.get_indicator_value(geo_record, t)
                        if dval:

                            data['denominators'][d.slug][t.name] = dval.to_dict()
                            data['denominators'][d.slug][t.name]['label'] = d.label # this is an extra field for denominators
                            if indval:
                                ivd = indval.to_dict()
                                data['denominators'][d.slug][t.name]['numerator'] = ivd['number'] # this is an extra field for denominators
                                data['denominators'][d.slug][t.name]['f_numerator'] = ivd['f_number'] # this is an extra field for denominators
        return data

    def get_indicator_info(self, geo_record, time_ids=[], data_domain=None):
        """
            Returns a dictionary loaded with all Indicator values as well as Denominator values
            time_ids = a list of time objects ids
        """
        times = []
        if len(time_ids):
            for tid in time_ids:
                try:
                    time = Time.objects.get(pk=tid)
                    if time not in times:
                        times.append(time)
                except Time.DoesNotExist:
                    pass
        else:
            # just return your own times
            times = self.get_times()

        # we may have passed it bogus time ids, so lets make sure we always
        # have something
        if not len(times):
            times = self.get_times()
        # check to see if we ant to display change
        display_change = False
        display_change |= self.display_change and len(times) > 1
        geo_as_dict = geo_record.get_as_dict()
        geo_dict = geo_as_dict['parent_geos']
        geo_dict[geo_as_dict['level']] = geo_as_dict['name']

        info = {
                'indicator':self,
                'geo_record':geo_dict,
                'href' : self.get_indicator_href(geo_record, data_domain),
                'denominators': [],
                'values':{}, # stored as {'time-pk':Value}
                'indicator_times':times,
                'change':None,
                'distribution':{}
        }
        # Append a value, or None for each time.
        for time in times:
            info['values'][time.id] = self.get_indicator_value(geo_record, time)
            # get distribution
            try:
                info['distribution'][time.id] = info['values'][time.id].datapoint._count_value()
            except AttributeError:
                # distribution isnt generated
                info['distribution'][time.id] = None

        info['denominators'] = self.get_denominator_info(geo_record, time_ids)

        if display_change:
            info['change'] = self.get_change(geo_record)

        return info

    def get_denominator_info(self, geo_record, time_ids=[]):
        """ Returns a list of dictionaries which contain Denominators and their values """
        times = []
        denom_info = []
        if len(time_ids):
            for tid in time_ids:
                try:
                    time = Time.objects.get(pk=tid)
                    if time not in times:
                        times.append(time)
                except Time.DoesNotExist:
                    pass
        else:
            # just return your own times
            times = self.get_times()

        # we may have passed it bogus time ids, so lets make sure we always
        # have something
        if not len(times):
            times = self.get_times()

        # check to see if we ant to display change
        display_change = False
        display_change |= self.display_change and len(times) > 1

        for denominator in self.denominator_set.order_by('sort'):
            #den_info = (denominator, [])
            den_info = {
                'denominator':denominator,
                'values': {},
                'change': None,
            }

            for time in times:
                den_info['values'][time.id] = self.get_denominator_value(denominator, geo_record, time)

            if display_change:
                try:
                    den_info['change'] = Value.objects.get(datapoint__record=geo_record, datapoint__indicator=self, denominator=denominator, datapoint__time=None)

                except Value.DoesNotExist:
                    den_info['change'] = None

            denom_info.append(den_info)

        return denom_info

    def get_display_options(self):
        """ Return a dict of display options """
        display_options = {}
        l = self.legendoption_set.all()
        if l:
            legend_options = {'bin_type':l[0].bin_type, 'bin_options':l[0].bin_options}
            display_options['legend'] = legend_options
        else:
            display_options['legend'] = None

        display_options['value_format'] = self.value_formatter

        return display_options

    @property
    def value_formatter(self):
        """ Return a dict that represents how this value should be formated"""
        if self.data_type == "DOLLARS" or self.data_type == "AVERAGE_OR_MEDIAN_DOLLARS":
            return {'type':'dollars'}

        elif self.data_type == 'CUSTOM':
            cvs = CustomValue.objects.filter(indicator=self)
            f = {'type':'custom'}
            rules = []
            for cv in cvs:
                rules.append({
                    'value_operator':cv.value_operator,
                    'display_value': cv.display_value,
                    'data_type': cv.data_type
                })
            f['rules'] = rules
            return f
        else:
            return {'type':'count'}

    @property
    def domain_group_path(self):
        """ return a path uri to where this indicator lives"""
        paths = []
        groups = self.group_set.all().only('name')
        for g in groups:
            for gd in g.datadomain_set.all().only('slug'):
                for dd in gd.datadomain_set.all():
                    paths.append({'domain':{'slug':dd.slug, 'name':dd.name}, 'subdomain':gd.slug, 'group':g.name})
        return paths

    def __unicode__(self):
        return '%s -- %s' % (self.name, self.display_name)


class DataGenerator(models.Model):
    """ Abstract model class for any model that generates data.

    This consolidates the fields and logic necessary to talk to data sources,
    for a given GeoRecord.
    """
    data_source = models.ForeignKey(DataSource)
    formula = models.TextField(blank=True)
    data = models.FileField(upload_to='data_files', null=True, blank=True)
    levels = models.ManyToManyField(GeoLevel, null=True, blank=True, help_text="Levels for which this Part applies.")
    published = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def value_for_geo(self, geo_record):
        data_source_kwargs = {}
        if self.data:
            data_source_kwargs['data_file'] = self.data
        data_source = self.data_source.get_implementation()(**data_source_kwargs)
        result = data_source.data(self.formula, geo_record)
        if result is None:
            logger.debug("None value for %s, %s (%s)" % (self.indicator.name, geo_record, self.formula))
        return result

    def get_tables(self):
        """ Return a list of tables that are used in this Data Generator"""
        from census import parse
        from census import data
        tables = []
        if self.data_source.name != "File":
            prs = parse.FormulaParser(self.data_source)
            tokens = prs.tokens(str(self.formula))
            for tl in tokens:
                if type(tl) == data.Table:
                    # single item its just a census.Table
                    tables.append(tl.table[:-3])
                else:
                    for t in tl:
                        if type(t) != str:
                            #p['tables'].append()
                            tbl = t.table[:-3]
                            if tbl not in tables:
                                tables.append(tbl)
        return tables


class IndicatorPart(DataGenerator):
    """ A part of an Indicator definition, specific to a Time.

    Since Indicators can span times, and each time may be a different data source,
    we define individual parts that generate data for the Indicator.
    """
    indicator = models.ForeignKey(Indicator)
    time = models.ForeignKey(Time)

    def __unicode__(self):
        return u"%s %s" % (self.time.name, self.data_source.name)


class Denominator(models.Model):
    """ A denominator to generate rates, proportions, etc, for Indicators.

    They will be listed alongside the main count value for an Indicator.
    The first denominator, as sorted by the "sort" field, will be considered
    the "default". If > 1 has the lowest sort value, behavior is undefined and
    one will be chosen at random.
    """
    label = models.CharField(max_length=50, blank=False)
    table_label = models.CharField(max_length=100, blank=True, null=True, help_text="A Short label that will be displayed in a table")
    multiplier = models.PositiveIntegerField(null=True, blank=True)
    indicator = models.ForeignKey(Indicator)
    sort = models.PositiveIntegerField(default = 1)
    slug = models.SlugField(max_length=100, unique=True, db_index=True, null=True, blank=True)

    @property
    def display_name(self):
        return self.label

    def get_display_options(self):
        opts = self.indicator.get_display_options()
        opts['value_format']['type'] = 'percent'
        return opts

    def get_times(self, name_only=True):
        return self.indicator.get_times(name_only)

    def get_change(self, geo_record):
        try:
            return Value.objects.get(datapoint__record=geo_record, datapoint__indicator=self.indicator, denominator=self, datapoint__time=None)
        except Value.DoesNotExist:
            return None

    def get_value(self, geo_record, time):
        """ Returns a Value object for a specific Denominator via GeoRecord and time"""
        if geo_record is None or time is None:
            raise ValueError("GeoRecord and Time is required.")
        try:
            return Value.objects.get(datapoint__record=geo_record, datapoint__indicator=self.indicator, denominator=self, datapoint__time=time)
        except Value.DoesNotExist:
            return None

    def __unicode__(self):
        return self.label


class DenominatorPart(DataGenerator):
    """ Similar to IndicatorPart, this specifies a formula and data source
    for a Denominator, for a specific IndicatorPart.
    """
    indicator = models.ForeignKey(Indicator)  # Hack, to allow for inline editing on the admin screen
    denominator = models.ForeignKey(Denominator)
    part = models.ForeignKey(IndicatorPart)

    def __unicode__(self):
        return u"%s (%s)" % (self.data_source.name, self.denominator)


class DataPoint(models.Model):
    """ A collection of values for an Indicator.

    DataPoint collects all values for a particular Time (including change), GeoRecord, and
    Indicator. This gives us a single entry point to values for different denominators.
    """
    indicator = models.ForeignKey(Indicator)
    record = models.ForeignKey(GeoRecord)
    time = models.ForeignKey(Time, null=True)
    change_from_time = models.ForeignKey(Time, null=True, related_name='datapoint_as_change_from')
    change_to_time = models.ForeignKey(Time, null=True, related_name='datapoint_as_change_to')
    image = ImageField(upload_to='indicator_images', blank=True, null=True)

    def _count_value(self):
        return self.value_set.get(denominator=None)

    def calculate_distribution(self):
        from django.db.models import Sum

        # grab the Value for the "count" portion of this DataPoint
        try:
            count_value = self._count_value()
        except Value.DoesNotExist:
            # TODO: log error
            return

        parent_total = Value.objects.filter(
            datapoint__indicator=self.indicator,
            datapoint__record__parent=self.record.parent,
            datapoint__time=self.time,
            denominator__isnull=True
        ).aggregate(Sum('number'))['number__sum']

        if parent_total > 0 and count_value.number:
            count_value.percent = (count_value.number / parent_total) * 100
        else:
            count_value.percent = None
        count_value.save()

    def is_change(self):
        return self.time is None and not self.change_from_time is None and not self.change_to_time is None

    def __unicode__(self):
        return "%s" % (self.time,)
    class Meta:
        unique_together = (
            ('indicator', 'record', 'time', ),
        )


class ValueManager(models.Manager):
    def create_for_change(self, datapoint, first_value, last_value, denominator=None,
                        calculate_moe=False, calculate_percent=False):

        change_percent = None

        if calculate_percent and not first_value.number == 0 and first_value.number is not None and last_value.number is not None:
            if denominator is None:
                change_percent = ((last_value.number - first_value.number) / first_value.number) * 100
            else: #TODO need to remember why we changed this!
                change_percent = (last_value.percent - first_value.percent)

        change_value = last_value - first_value

        moe = None

        if calculate_moe:
            moe = change_value.moe

        val = Value.objects.create(
            datapoint=datapoint,
            denominator=denominator,
            number=change_value.value,
            percent=change_percent,
            moe=moe
        )
        return val


class Value(models.Model):
    """ A specific value for an Indicator.

    Each data point will have multiple Value objects associated with it. Each
    denominator value, each percent, etc, will all have a Value.

    When denominator is None, percent represents the distribution % of the containing geography
    When denominator is not None, number represents the divisor

    """
    datapoint = models.ForeignKey(DataPoint)
    denominator = models.ForeignKey(Denominator, null=True, blank=True)
    number = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    moe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    objects = ValueManager()

    def as_value_instance(self):
        return census_data.Value(self.number, moe=self.moe)

    def __add__(self, other):
        return self.as_value_instance() + other.as_value_instance()

    def __sub__(self, other):
        return self.as_value_instance() - other.as_value_instance()

    @property
    def is_denom(self):
        if self.denominator:
            return True
        return False

    @property
    def is_change(self):
        """ When the datapoint time is None, this is a change value """
        if self.datapoint.time == None:
            return True
        return False

    @property
    def originating_value(self):
        if not self.is_denom:
            # look up the originating indicator value
            ind = self.datapoint.indicator
            time = self.datapoint.time
            rec = self.datapoint.record
            return ind.get_indicator_value(rec, time)

        else:
            return self

    @property
    def number_value(self):
        """ A proxy for getting self.number. this is how where we check for supressed values and such"""
        cv_outcome, cv = self.test_value()

        if cv_outcome and cv.supress and self.number != 0:
            return Decimal(-1)
        else:
            return self.number

    def test_value(self):
        custom_vals = CustomValue.objects.filter(indicator=self.datapoint.indicator)
        cus_val = None
        outcome = False
        for cv in custom_vals:
            test_outcome = cv.test_value(self.number)
            if test_outcome is True:
                #number meets a criteria stop loop
                return True, cv
            else:
                cus_val = cv
                outcome = False

        return outcome, cus_val

    def to_dict(self):
        """ Almost Every if not all displayed value in profiles comes from accessing values by this method.
        """
        if self.datapoint.indicator.data_type != "CUSTOM" or self.is_change is True:
            return {'number':self.number,
                    'percent':self.percent or 0,
                    'moe': self.moe if self.moe > 0 else None,
                    'f_number':format_number(self.number, self.datapoint.indicator.data_type),
                    'f_percent': format_number(self.percent or 0, 'PERCENT') + "%",
                    'f_moe':format_number(self.moe, self.datapoint.indicator.data_type) if self.moe > 0 else None
            }
        else:
            cv_outcome, cv = self.test_value()

            if cv_outcome != False:
                #this value has met the criteria of a custom value
                if cv.supress == False:
                    display_val = cv.display_value
                elif cv.supress == True:
                    #this is a supressed value where 0 is important
                    if self.number != 0:
                        display_val = cv.display_value
                    else:
                        display_val = "0"

            else:
                display_val = format_number(self.number, cv.data_type)


            return {'number':self.number_value,
                    'percent':self.percent or 0,
                    'moe': self.moe if self.moe > 0 else None,
                    'f_number': display_val,
                    'f_percent': format_number(self.percent or 0, 'PERCENT') + "%",
                    'f_moe':format_number(self.moe, self.datapoint.indicator.data_type) if self.moe > 0 else None
            }



class CustomValue(models.Model):
    """ A value object can represent a number of strings
        Ex: 0 True
            1 False
            2 Maybe
        This mapping only affects the way values are displayed for a specific Indicator
    """
    CV_DATA_TYPE_CHOICES = (
        ('COUNT', 'Count'),
        ('DECIMAL_1', 'Decimal 1'),
        ('DECIMAL_2', 'Decimal 2'),
        ('DOLLARS', 'Dollars'),
        ('AVERAGE_OR_MEDIAN_DOLLARS','$ Average or Median'),
        ('AVERAGE_OR_MEDIAN', 'Average or Median'),
    )

    indicator = models.ForeignKey('Indicator')
    value_operator = models.CharField(max_length="255", blank=False, null=False, help_text="The value or An optional comparison operator. Example: '< 5' would map a value less than 5 to the display value. '10' would map a value equal to 10 to a the display value")
    display_value = models.CharField(max_length="255", blank=False, null=False)
    data_type = models.CharField(max_length=30, choices=CV_DATA_TYPE_CHOICES, default='COUNT')
    supress = models.BooleanField(default=False)

    def test_value(self, value):
        """Does this value meet the criteria of the value operator?"""
        comp = build_value_comparison(self.value_operator)
        return comp(value)

    def __unicode__(self):
        return "%s: %s" % (self.indicator.display_name, self.value_operator)



class FlatValue(models.Model):
    """ Denormalized Representation of an indicator or denominator value obj post formating and suppression for a given time and geography """
    VALUE_TYPES = (
        ('i','Indicator'),
        ('d', 'Denominator'),
        ('c','Change'),
    )
    indicator = models.ForeignKey('Indicator') # should always relate to an indicator
    display_title = models.CharField(max_length="255", blank=False, null=False, db_index=True)
    indicator_slug= models.CharField(max_length="255", blank=False, null=False, db_index=True)
    geography = models.ForeignKey('GeoRecord')
    geography_name = models.CharField(max_length="255",null=False, blank=False)
    geography_slug = models.CharField(max_length="255", blank=False, null=False, db_index=True)
    geography_geo_key = models.CharField(max_length="255", blank=False, null=False, db_index=True, default=0)
    value_type = models.CharField(max_length="100", blank=False, null=False, choices=VALUE_TYPES)
    time_key = models.CharField(max_length="255", blank=False, null=False) # time as string
    geometry_id = models.IntegerField(null=True, blank=True) # a polygon shapefile id we can pull for this
    #################### VALUES ##########################
    number = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    moe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    numerator = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Only denominators contain numerators
    numerator_moe = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Cause it happens!
    #################### Formated Values ##########################
    f_number = models.CharField(max_length="255", blank=True, null=True)
    f_percent = models.CharField(max_length="255", blank=True, null=True)
    f_moe = models.CharField(max_length="255", blank=True, null=True)
    f_numerator = models.CharField(max_length="255", blank=True, null=True)
    f_numerator_moe = models.CharField(max_length="255", blank=True, null=True)

    published = models.BooleanField(default=True)


    def to_dict(self):
        return {
            'name': self.display_title,
            'geography': self.geography.name,
            'time': self.time_key,
            'number':self.number,
            'percent':self.percent,
            'moe':self.moe,
            'numerator':self.numerator,
            'type': self.value_type,
            'f_number':self.f_number or "No Data",
            'f_percent':self.f_percent,
            'f_moe':self.f_moe,
        }

    def __unicode__(self):
        return "%s: %s: %s %s" % (self.display_title, self.geography.name, self.time_key, self.f_number)


class PrecalculatedValue(models.Model):
	""" These values are essentially overrides to what appear in the census row tables. Sometimes, we want to display specific human calculated values insteadof going with what Profiles does on its own. This is especially true for Aggregated Median values, etc. This table gets accessed before the census Rows."""
	table = models.TextField(blank=True)
	geo_record = models.ForeignKey(GeoRecord)
	value = models.TextField(blank=True)
	data_source = models.ForeignKey(DataSource)
	notes = models.TextField(blank=True)

	def __unicode__(self):
		return "DS: %s, Tbl: %s, GR: %s" % (self.data_source.name, self.table, self.geo_record.name)


#----------INDICATOR DISPLAY OPTIONS ----- #
class LegendOption(models.Model):
    BIN_OPTIONS = (
        ('eq', 'Equally Spaced'),
        ('cb', 'Custom Breaks'),
        ('ei', 'Equal Interval'),
        ('jenks', 'Jenks'),
        ('all', 'All Categories'),
    )
    indicator = models.ForeignKey('Indicator')
    bin_type = models.CharField(max_length=255, choices=BIN_OPTIONS, null=False, blank=False, help_text="The type of color bin to use.", default='jenks')
    bin_options = models.TextField(null=False, blank=False, default="", help_text="If you have selected All Categories for bin type, put 'all' in here")

    def clean(self):
        indset = self.indicator.legendoption_set.all() # get the current legend options that are related to the indicator we are trying to save.
        if indset.count() > 0 and indset[0].id != self.id:
            raise ValidationError('Indicators can only have one Instance of Legend option')

    def __unicode__(self):
        return self.bin_type


class TaskStatus(models.Model):
    """ A task tombstone emitted by Huey"""
    first_seen = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=True)
    last_updated = models.DateTimeField(auto_now=True, null=True, blank=True, editable=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    task = models.CharField(max_length=255, null=True, blank=True)
    t_id = models.CharField(max_length=255, null=True, blank=True) # this is a UUID cast as a string
    error = models.BooleanField(default=False, blank=True)
    traceback = models.TextField(null=True, blank=True)

    def __unicode__(self):
        try:
            label = IndicatorTask.objects.get(task_id= self.t_id).indicator.name
        except IndicatorTask.DoesNotExist:
            label = self.task

        return "%s: %s -- %s: First seen: %s, Last Updated: %s" % (label,
                                                                   self.t_id,
                                                                   self.status,
                                                                   self.first_seen,
                                                                   self.last_updated)
class IndicatorTask(models.Model):
    indicator = models.ForeignKey(Indicator, null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True) # this is a UUID cast as a string
    def __unicode__(self):
        try:
            t = TaskStatus.objects.get(t_id=self.task_id)
            return "%s for %s started at %s, Last updated: %s, Status: %s" %(t.task, self.indicator.display_name, t.first_seen, t.last_updated, t.status)
        except TaskStatus.DoesNotExist:
            return "Task for %s pending or does not exist" % self.indicator.display_name


@receiver(pre_delete, sender=TaskStatus)
def task_cleanup(sender, instance, **kwargs):
    """ Delete indicator Task Meta data when we delete a TaskStatus"""
    try:
        IndicatorTask.objects.get(task_id=instance.t_id).delete()
    except IndicatorTask.DoesNotExist:
        pass


@receiver(pre_save, sender=Denominator)
def slug_handler(sender, instance, **kwargs):
    unique_slugify(instance, instance.label, queryset=Denominator.objects.all())
