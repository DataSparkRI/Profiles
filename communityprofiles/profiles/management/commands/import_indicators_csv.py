from django.core.management.base import BaseCommand, CommandError
from profiles.models import Indicator, Time, GeoLevel
import csv
from django.utils.text import slugify

class Command(BaseCommand):
    args = '<path_to_file>'
    help = """Import Indicators from a csv file
    Headers are name,display_name,short_description,long_description,notes,times
    times should be formatted like so "2000 & 2006-2010". IOW they should be splitible by " & "
    """

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError('path_to_file is required. See --help')
        Indicator.objects.all().delete()
        with open(args[0], 'rb') as f:
            reader = csv.DictReader(f, quotechar='"')
            for r in reader:
                #print r
                times = r['times'].split(" & ")
                # create times if need be
                time_objs = []
                for t in times:
                    name = t.strip()
                    if name != "":
                        obj, created = Time.objects.get_or_create(name=name, sort=0)
                        if created:
                            self.stdout.write("Created time %s" % obj.name)
                # create the indicator
                obj, created = Indicator.objects.get_or_create(name=r['name'],
                                                              display_name=r['display_name'],
                                                              short_definition=r['short_description'],
                                                              long_definition=r['long_description'],
                                                              notes=r['notes'],
                                                              display_change=False,
                                                              display_distribution=False,
                                                              slug=slugify(unicode(r['name']+r['display_name'])),
                                                              )
                if created:
                    self.stdout.write("Created indicator %s" % obj.name)








