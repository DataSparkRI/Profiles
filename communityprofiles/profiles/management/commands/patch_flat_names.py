from django.core.management.base import BaseCommand, CommandError
from profiles.models import FlatValue

class Command(BaseCommand):
    """ Patches denominator names in flat values. It appends the indicator name infront of it"""
    def handle(self, *args, **options):
        fvs = FlatValue.objects.filter(value_type="d")
        for f in fvs:
            f.display_title = "%s - %s" % (f.indicator.display_name, f.display_title)
            f.save()


