""" Parse a custom formated geography file
    Headers should look like so
    sumlev,name,custom_name,geo_id,geo_id_segements,year
"""
from django.core.management.base import BaseCommand, CommandError
from census.tools.geography import parse_file, get_sum_lev_name, SUPPORTED_DATASETS, geo_id_to_segments
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from profiles.models import GeoRecord, GeoLevel
from django.utils.text import slugify
import json
import csv

class Command(BaseCommand):
    args = '<path_to_geo_file>'

    help = """Create GeoRecords from custom formated geo files.
    This process should be indempodent"""

    def handle(self, *args, **options):
        if len(args) < 1:
            self.stderr.write("Missing arguments. Try --help.")

        geo_file_path = args[0]

        # Generate GeoLevels from defined settings
        sum_levs = getattr(settings, 'SUMMARY_LEVELS', None)

        if sum_levs is None:
            raise ImproperlyConfigured('SUMMARY_LEVELS is required. Please check settings.py')
        elif len(sum_levs) == 0:
            raise ImproperlyConfigured('SUMMARY_LEVELS is required. Please check settings.py')

        self.stdout.write("---- Generating Base GeoLevels ------")
        for sum_lev in sum_levs:
            geo_lev = get_sum_lev_name(sum_lev)
            obj, created = GeoLevel.objects.get_or_create(name=geo_lev, slug=slugify(u'' + geo_lev.lower()), summary_level=sum_lev, year='') # TODO: What about parenting?
            if not created:
                self.stdout.write("%s exists. Skipping..." % geo_lev)
            elif created:
                self.stdout.write("Created %s" % geo_lev)

        self.stdout.write("---- Generating %s GeoLevels ------" % ",".join(SUPPORTED_DATASETS))
        for sum_lev in sum_levs:
            for dataset_type in SUPPORTED_DATASETS:
                geo_lev = get_sum_lev_name(sum_lev)
                geo_lev_name = geo_lev
                obj, created = GeoLevel.objects.get_or_create(name=geo_lev_name, year=dataset_type, slug=slugify(dataset_type + u'_'+ geo_lev_name.lower()), summary_level=sum_lev) # TODO: What about parenting?
                if not created:
                    self.stdout.write("%s exists..." % (geo_lev_name))
                elif created:
                    self.stdout.write("Created %s " % geo_lev_name)

        # Now read that file
        with open(geo_file_path, 'rb') as f:
            reader = csv.DictReader(f)
            for item in reader:
                years = [i.strip() for i in item['year'].split(",")]
                years.append('')
                geo_id_segments = geo_id_to_segments(item['geo_id'], item['sumlev'])

                for year in years:
                    level = GeoLevel.objects.get(summary_level=item['sumlev'].strip(), year=year)
                    #print level
                    geo_record, created = GeoRecord.objects.get_or_create(level = level,
                                                                                name = item['name'],
                                                                                custom_name = item['custom_name'],
                                                                                slug = slugify(u''+item['name']),
                                                                                geo_id = item['geo_id'],
                                                                                geo_id_segments = json.dumps(geo_id_segments),
                                                                                geo_searchable = True,
                                                                                parent = None)
                    if created:
                        self.stdout.write("Created %s for level %s" % (item['name'], level.name))


        self.stdout.write("Done!")

