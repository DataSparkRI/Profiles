from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from profiles.models import GeoRecord, GeoLevel

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--dryrun', '-d', dest='dryrun', help='Dry run? True or False',default='true'),
    )

    def handle(self, *args, **options):
        levels = GeoLevel.objects.filter(slug__in=['state','municipality','census-tract'])
        recs = GeoRecord.objects.filter(level__in=levels)

        if options.get('dryrun') == 'true':
            for rec in recs:
                count = rec.mappings.count()
                if count < 2:
                    print rec.name, 'Mappings: ', count
        elif options.get('dryrun') == 'false':
            print 'Non Dry run'
            for rec in recs:
                count = rec.mappings.count()
                if count < 2:
                    # do some simple mapping. This doesnt take care to map
                    # census tracks to blocks.
                    mappings = GeoRecord.objects.filter(name=rec.name).exclude(level__in=levels)
                    for m in mappings:
                        rec.mappings.add(m)





