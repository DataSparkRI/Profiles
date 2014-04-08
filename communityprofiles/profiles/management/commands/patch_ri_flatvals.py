from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from profiles.models import GeoRecord, GeoLevel, FlatValue
from django.template.defaultfilters import slugify


class Command(BaseCommand):
    def handle(self, *args, **options):
        flat_vals = FlatValue.objects.filter(indicator_slug=None)
        fvcount = flat_vals.count()
        count = 0
        self.stdout.write('Patching %s FlatValues' % fvcount)

        for fv in flat_vals:
            fv.indicator_slug = fv.indicator.slug
            fv.geography_name = fv.geography.name
            fv.geography_slug = fv.geography.slug
            fv.save()
            count+=1
            self.stdout.write('Patched %s of %s' % (count, fvcount))

        # now we have to patch the denoms slugs
        denoms = FlatValue.objects.filter(value_type="d")
        dcount = denoms.count()
        count = 0
        self.stdout.write('Patching %s Denom Slugs' % dcount)
        for d in denoms:

            d.indicator_slug = d.indicator_slug + slugify(d.display_title)
            d.save()
            count +=1
            self.stdout.write('Patched %s of %s' % (count, dcount))

        self.stdout.write('Done Patching %s Denom Slugs' % dcount)




