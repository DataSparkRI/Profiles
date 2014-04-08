from django.core.management.base import BaseCommand, CommandError
from profiles.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        """ Add all the levels in each indicator to all the parts of
            an indicator"""
        levels = GeoLevel.objects.filter(name__in=['County', 'Census Tract', 'County Subdivision'], year='') | GeoLevel.objects.filter(name__in=['County', 'Census Tract', 'County Subdivision'], year=None)
        for indicator in Indicator.objects.all():
            for ip in indicator.indicatorpart_set.all():
                for l in levels:
                    ip.levels.add(l)
            for dp in indicator.denominatorpart_set.all():
                for l in levels:
                    dp.levels.add(l)
        print "DONE!"

