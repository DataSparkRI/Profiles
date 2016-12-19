from django.core.management.base import BaseCommand, CommandError
from profiles.models import *
import json

class Command(BaseCommand):

    def handle(self, *args, **options):
        copy_data_source_name = 'CensusAPI_ACS5_2012' # already created
        new_time_name = '2006 - 2010'
        new_time_sort = '0'
        new_data_source_name = 'CensusAPI_ACS5_2010' # already created or auto created
        new_data_source_implementation = 'data_adapters.CensusAPI_ACS5_2010'
        
        '''
        copy_data_source_name = 'CensusAPI_ACS5_2012_Profile' # already created
        new_time_name = '2011-2015'
        new_time_sort = '2015'
        new_data_source_name = 'CensusAPI_ACS5_2015_Profile' # already created or auto created
        new_data_source_implementation = 'data_adapters.CensusAPI_ACS5_2015_Profile'
        '''
        
        time, created = Time.objects.get_or_create(name = new_time_name, sort = new_time_sort)
        datasource_copy_from = DataSource.objects.get(name = copy_data_source_name)
        datasource_copy_to, created = DataSource.objects.get_or_create(name = new_data_source_name, implementation = new_data_source_implementation)
        
        indicator_parts = IndicatorPart.objects.filter(data_source = datasource_copy_from)
        for indicator_part in indicator_parts:
           
           new_indicator_part, created = IndicatorPart.objects.get_or_create(indicator = indicator_part.indicator, 
                                              time = time,
                                              data_source = datasource_copy_to)
           if created:
               new_indicator_part.formula = indicator_part.formula
               new_indicator_part.data = indicator_part.data
               new_indicator_part.published = True #indicator_part.published
               new_indicator_part.levels = indicator_part.levels.all()
               new_indicator_part.save()
               
               indicator = indicator_part.indicator        

               denominator_parts = DenominatorPart.objects.filter(indicator = indicator, data_source = datasource_copy_from, part = indicator_part)
               for denominator_part in denominator_parts:
                   new_denominator_part, created = DenominatorPart.objects.get_or_create(indicator = denominator_part.indicator, 
                                   denominator = denominator_part.denominator,
                                   part = new_indicator_part,
                                   data_source = datasource_copy_to,
                                   formula = denominator_part.formula,
                                   data = denominator_part.data,
                                   published = denominator_part.published)
                   new_denominator_part.levels = denominator_part.levels.all()
                   new_denominator_part.save()

