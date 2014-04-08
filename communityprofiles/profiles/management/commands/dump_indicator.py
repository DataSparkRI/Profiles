from django.core.management.base import BaseCommand, CommandError
from profiles.models import * 

class Command(BaseCommand):

    def handle(self, *args, **options):

        indicators = Indicator.objects.all()[:5]

        for indicator in indicators:
            print "-----------------------------------------------"
            print indicator.name , indicator.display_name
            print "Short Definition:"
            print indicator.short_definition
            print "Long Definition:"
            print indicator.long_definition
            print "Universe:"
            print indicator.universe

            print "-------INDICATOR PARTS-------"
            indicator_parts = IndicatorPart.objects.filter(indicator = indicator)

            for i_p in indicator_parts:
                print ""
                print "Data Source:"
                print i_p.data_source
                print "Formula:"
                print i_p.formula

            print "------DENOMINATORS-------"

            denominators = Denominator.objects.filter(indicator = indicator)

            for denom in denominators:
                print denom.label
                print "Multiplier:", denom.multiplier

                print "-------DENOM PARTS-------"

                denom_parts = DenominatorPart.objects.filter(denominator=denom)
                
                for denom_part in denom_parts:
                    print ""
                    print "Data Source:"
                    print denom_part.data_source
                    print "Formula:"
                    print denom_part.formula






        