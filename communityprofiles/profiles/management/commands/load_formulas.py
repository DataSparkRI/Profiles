from django.core.management.base import BaseCommand, CommandError
from profiles.models import *
import json

class Command(BaseCommand):

    def handle(self, *args, **options):
        with open(args[0]) as f:
            fls = json.loads(f.read())
            for fl in fls:
                # {"formula": "H041002", "time_name": "2000", "datasource": "Census 2000 SF3", "indicator_name": "HOUSING20"}
                try:
                    ind = Indicator.objects.get(name=fl['indicator_name'].strip())
                    time = Time.objects.filter(name=fl['time_name'])[0]

                    if fl['datasource'] == 'Census 2000 SF1':
                        ds = DataSource.objects.get(name='CensusAPI_SF1_2000')
                    elif fl['datasource'] == 'Census 2000 SF3':
                        ds = DataSource.objects.get(name='CensusAPI_SF3_2000')
                    elif fl['datasource'] == 'Census 2010 SF1':
                        ds = DataSource.objects.get(name='CensusAPI_SF1_2010')
                    elif fl['datasource'] == 'ACS 2010 Five Year Estimate':
                        ds = DataSource.objects.get(name='CensusAPI_ACS5_2010')
                    else:
                        ds = None
                    if ds != None:
                        obj, created = IndicatorPart.objects.get_or_create(data_source = ds, indicator=ind, time=time, formula=fl['formula'])
                        if created:
                            self.stdout.write('Created time %s  for %s' %(fl['time_name'], fl['indicator_name']))
                    else:
                        pass
                except Exception as e:
                    print(e)
                    #self.stdout.write('Didnt find: ' +  fl['indicator_name'])


