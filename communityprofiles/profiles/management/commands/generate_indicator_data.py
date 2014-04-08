from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from django.db import transaction

from profiles.tasks import generate_indicator_data

from profiles.models import *

class Command(BaseCommand):
    args = '<cmd, optional> '
    help = 'Generates indicator data for all indicators or a single indicator. ***Generating data for ALL indicators can take a while! '

    def handle(self, *args, **options):

        if len(args) == 0:
            raise CommandError("Enter a command: <all> or <single>")

        if args[0] == 'all':
            self.generate_all_indicator_data()
        elif args[0] == 'single':
            if len(args)!=2:
                raise CommandError('Please enter an Indicator Slug')
            self.generate_single_indicator_data_from_name(args[1])


    def generate_single_indicator_data_from_name(self, indicator_slug):

        indicator = Indicator.objects.get(slug=indicator_slug)
        print(indicator.name)

        generate_indicator_data(indicator)



    def generate_all_indicator_data(self):

        for indicator in Indicator.objects.filter(published=True):
            print "Generating data for %s" % indicator.display_name
            generate_indicator_data(indicator)



