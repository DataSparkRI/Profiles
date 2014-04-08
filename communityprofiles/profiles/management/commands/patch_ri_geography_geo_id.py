from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from profiles.models import GeoRecord, GeoLevel, FlatValue
from django.template.defaultfilters import slugify
from census.tools import geography


class Command(BaseCommand):
    def handle(self, *args, **options):
        #self.stdout.write('Done Patching %s Denom Slugs' % dcount)




