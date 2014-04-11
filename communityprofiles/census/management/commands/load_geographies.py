from django.core.management.base import BaseCommand, CommandError
from census.tools.geography import parse_file, get_sum_lev_name, SUPPORTED_DATASETS
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from profiles.models import GeoRecord, GeoLevel
from django.utils.text import slugify as djslugify
import json

class Command(BaseCommand):
    #TODO: Possibly drop all these tables before importing
    args = '<path_to_census_geo_file> <dataset_type>'

    help = """Create GeoRecords from census geo files. This process deals with a single census data source.
    This process should be indempodent
    Census geo files can be downloaded from census.gov, check dataset documentation for more info
    Supported dataset_types are %s
    """ % ','.join(SUPPORTED_DATASETS)

    def slugify(self, str, uuid=False):
        """ Wrapper for slugify that replaces . with - since Django slugify ignores it"""
        from uuid import uuid4
        str = str.replace(".", "-")
        if uuid:
            str += unicode(uuid4())[:6]
        return djslugify(str)

    def handle(self, *args, **options):
        if len(args) < 2:
            self.stderr.write("Missing arguments. Try --help.")

        census_geo_file_path = args[0]
        dataset_type = args[1]

        # Generate GeoLevels from defined settings
        sum_levs = getattr(settings, 'SUMMARY_LEVELS', None)

        if sum_levs is None:
            raise ImproperlyConfigured('SUMMARY_LEVELS is required. Please check settings.py')
        elif len(sum_levs) == 0:
            raise ImproperlyConfigured('SUMMARY_LEVELS is required. Please check settings.py')

        self.stdout.write("---- Generating Base GeoLevels ------")
        for sum_lev in sum_levs:
            geo_lev = get_sum_lev_name(sum_lev)
            try:
                obj = GeoLevel.objects.get(name=geo_lev, slug=self.slugify(u'' + geo_lev.lower()), summary_level=sum_lev, year='')
                self.stdout.write("%s exists. Skipping..." % geo_lev)
            except GeoLevel.DoesNotExist:
                created = GeoLevel.objects.create(name=geo_lev, slug=self.slugify(u'' + geo_lev.lower()), summary_level=sum_lev, year='')
                self.stdout.write("Created %s" % geo_lev)

        self.stdout.write("---- Generating %s GeoLevels ------" % dataset_type )
        for sum_lev in sum_levs:
            geo_lev = get_sum_lev_name(sum_lev)
            geo_lev_name = geo_lev
            obj, created = GeoLevel.objects.get_or_create(name=geo_lev_name, year=dataset_type, slug=self.slugify(dataset_type + u'_'+ geo_lev_name.lower()), summary_level=sum_lev) # TODO: What about parenting?
            if not created:
                self.stdout.write("%s exists..." % (geo_lev_name))
            elif created:
                self.stdout.write("Created %s " % geo_lev_name)

        # Now we create all the GeoRecords but first we must read the census
        # geo_file
        geos = parse_file(args[0], args[1], getattr(settings, 'SUMMARY_LEVELS', None))
        geos_keys = []
        for key in geos.iterkeys():
            if key not in ['names', 'name_index']:
                geos_keys.append(key)
        geos_keys.sort()
        for key in geos_keys:
            if key not in ['names', 'name_index']: # skip these 2 the rest are sumlevs
                # Grab a geography level for each summary level returned from
                # the census file
                self.stdout.write("----Creatings Geos for Sum Lev %s----" % key)

                geo_lev_name = get_sum_lev_name(key)
                base_geo_level = GeoLevel.objects.get(name=geo_lev_name, year='')
                dataset_geo_level = GeoLevel.objects.get(year=dataset_type, name=geo_lev_name)

                # Now create a Geo Record for each Geography we have found in
                # this sumlev
                # There should be a Geo Record in the Base Geographies for
                # everyone that exists in each data set.

                for geo in geos[key].itervalues():
                    if geo['parent'] != None:
                        try:
                            pass
                            """
                            base_parent_level = GeoLevel.objects.get(summary_level = geo['parent']['sumlev'],
                                                                     name=get_sum_lev_name(geo['parent']['sumlev']),
                                                                     year__isnull=True)

                            base_parent = GeoRecord.objects.get(level=base_parent_level, geo_id=geo['parent']['geoid'])

                            dataset_parent_level = GeoLevel.objects.get(summary_level = geo['parent']['sumlev'],
                                                                       name=get_sum_lev_name(geo['parent']['sumlev']),
                                                                       year=dataset_type)

                            dataset_parent = GeoRecord.objects.get(level=dataset_parent_level, geo_id=geo['parent']['geoid'])
                            """
                        except Exception as e:
                            """
                            if key != "040":
                                self.stderr.write("Parent Geo for %s not found - %s" % (geo['name'], e))
                            base_parent = None
                            dataset_parent = None
                            """
                            pass
                    else:
                        if key != "040":
                            self.stderr.write("Parent Geo Not found through Geography File for: %s" % geo)
                        base_parent = None
                        dataset_parent = None

                    base_geo_record, created = GeoRecord.objects.get_or_create(level = base_geo_level,
                                                                               name = geo['name'],
                                                                               slug = self.slugify(u''+geo['geoid']),
                                                                               geo_id = geo['geoid'],
                                                                               geo_id_segments = json.dumps(geo['geoid_dict']),
                                                                               geo_searchable = True,)
                                                                               #parent = base_parent)

                    if not created:
                        self.stdout.write("%s @ Geo Lev %s exists. GEOID = %s " % (geo['name'], base_geo_level.name, base_geo_record.geo_id) )
                    elif created:
                        self.stdout.write("Created %s @ Geo Lev %s with GeoId %s " %  (geo['name'], base_geo_level.name, geo['geoid']) )

                    dataset_geo_record, created = GeoRecord.objects.get_or_create(level = dataset_geo_level,
                                                                               name = geo['name'],
                                                                               slug = self.slugify(u''+geo['geoid'] + dataset_type),
                                                                               geo_id = geo['geoid'],
                                                                               geo_id_segments = json.dumps(geo['geoid_dict']),
                                                                               geo_searchable = False,)
                                                                               #parent = dataset_parent,
                                                                            

                    if not created:
                        self.stdout.write("%s @ Geo Lev %s exists. Skipping..." % (geo['name'], dataset_geo_level.name) )
                    elif created:
                        self.stdout.write("Created %s @ Geo Lev %s " % (geo['name'], dataset_geo_level.name) )






