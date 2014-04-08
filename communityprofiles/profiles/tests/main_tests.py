import os, re
from decimal import Decimal
from django.test import TestCase
from django.test.client import Client
from django.template import Context
from django.template import Template
from django.utils.html import strip_spaces_between_tags as shorten
from data_adapters import *
from profiles.models import *
from profiles.utils import *
from profiles.templatetags import profiles_tags
from census.models import Row
from tastypie.test import ResourceTestCase
import json

class Indicators(TestCase):
    fixtures = ['times.json','datasources.json', 'geolevels.json', 'datadomains.json','indicators.json','indicator_parts.json',
            'denoms.json', 'denom_parts.json', 'indicator_domains.json', 'geo-ri.json','ri-census-rows.json']

    def setUp(self):
        self.ind_poptot = Indicator.objects.get(slug="poptot")
        self.ind_income7 = Indicator.objects.get(slug="income7")
        self.ind_income6 = Indicator.objects.get(slug="income6")
        self.state_rec = GeoRecord.objects.filter(name='Rhode Island')[0]

    def test_get_levels(self):
        print self.ind_income7.levels
        #TODO: finish this test

    def test_get_times(self):
        times = self.ind_poptot.get_times()
        self.assertTrue(len(times)==2)
        # TODO: We could be more specific...

    def test_get_notes(self):
        self.assertTrue('text' in self.ind_poptot.get_notes()[0])

    def test_default_domain(self):
        self.assertEqual(self.ind_poptot.default_domain().name,'Overview')

    def test_collect_data(self):
        """ Test all 3 indicators just to get better sampling"""
        data = self.ind_poptot.collect_data(self.state_rec)
        self.assertEqual(data[0]['value'],'1052567')

        # income7 has denoms
        data = self.ind_income7.collect_data(self.state_rec)
        self.assertEqual(len(data[0]['denoms']),4)

    def test_generate_data(self):
        """Every Indicator generates a Datapoint for every combo of  Time & Geography"""
        self.ind_income7.generate_data()
        # for income7 we should get 2
        self.assertEqual(DataPoint.objects.filter(indicator=self.ind_income7).count(), 2)

    def test_generate_distribution(self):
        """ Distribution is saved as the percentage of the Value obj """
        self.ind_income7.generate_data()
        self.ind_income7.generate_distribution()
        # we can now use another helper to test the result of that/test the helper
        times = self.ind_income7.get_times()
        value = self.ind_income7.get_indicator_value(self.state_rec, times[0])
        self.assertEqual(value.percent, 100)

    def test_generate_change(self):
        """ Datapoint objects with Time=None are change values"""
        self.ind_income7.generate_data()
        self.ind_income7.generate_change()
        times = self.ind_income7.get_times()
        value1 = self.ind_income7.get_indicator_value(self.state_rec, times[0]).number
        value2 = self.ind_income7.get_indicator_value(self.state_rec, times[1]).number
        change = self.ind_income7.get_change(self.state_rec)
        self.assertEqual(change.number, value2-value1)
        self.assertEqual(float(change.percent), float(-8.54))

        # we need to also test the denominator changes
        denoms = self.ind_income7.denominator_set.all() # [<Denominator: % of Families with Children>, <Denominator: % Families Below Poverty>]
        #grab single val
        d_val1 = denoms[0].get_value(self.state_rec, times[0])
        d_val2 = denoms[0].get_value(self.state_rec, times[1])
        self.assertEqual(d_val2.number - d_val1.number, denoms[0].get_change(self.state_rec).number) # -1827
        # denoms change percent are calculated based percentages in values.
        self.assertEqual(float(denoms[0].get_change(self.state_rec).percent), float(d_val2.percent-d_val1.percent))

    def test_generate_flat_vals(self):
        from profiles.tasks import generate_flat_values
        self.ind_income7.generate_data()
        self.ind_income7.generate_distribution()
        self.ind_income7.generate_change()
        generate_flat_values(self.ind_income7)
        self.assertEqual(8, FlatValue.objects.all().count()) # 3 for indicator + change 3 for each denom + change


class IndicatorLongTest(TestCase):
    """ A longer test that runs through many levels of geography"""
    fixtures = ['times.json','datasources.json', 'geolevels.json', 'datadomains.json','indicators.json','indicator_parts.json',
            'denoms.json', 'denom_parts.json', 'indicator_domains.json', 'geo-ri.json','geo-prov.json','geo-tract.json','ri-census-rows.json', 'prov-census-rows.json', 'tract29-census-rws.json']

    def setUp(self):
        self.ind_poptot = Indicator.objects.get(slug="poptot")
        self.ind_income7 = Indicator.objects.get(slug="income7")
        self.ind_income6 = Indicator.objects.get(slug="income6")
        self.muni_lev = GeoLevel.objects.get(slug="municipality")
        self.tract_lev = GeoLevel.objects.get(slug="census-tract")
        self.state_rec = GeoRecord.objects.filter(name='Rhode Island')[0]
        self.muni_rec = GeoRecord.objects.get(slug="providence", level=self.muni_lev)
        self.tract_rec = GeoRecord.objects.get(slug="census-tract-29", level=self.tract_lev)

    def test_collect_data(self):
        """ Test all 3 levels of geo to get better sampling. Just dont crash for now."""
        self.ind_poptot.collect_data(self.state_rec)
        self.ind_poptot.collect_data(self.muni_rec)
        self.ind_poptot.collect_data(self.tract_rec)
        self.ind_income7.collect_data(self.state_rec)
        self.ind_income7.collect_data(self.muni_rec)
        self.ind_income7.collect_data(self.tract_rec)

    def test_generate_data(self):
        """ Just dont crash for now """
        self.ind_income7.generate_data()
        self.assertEqual(DataPoint.objects.filter(indicator=self.ind_income7).count(),6)


class SimpleAPI(TestCase):
    fixtures = ['intitial_data.json','geolevels.json','indicators.json','times.json']

    def setUp(self):
        build_geos(self)

    def test_geography_api_errors(self):
        c = Client()
        response = c.get('/profiles/api/geo/')
        # test no l or name
        self.assertEqual(response.status_code, 404)

        #test both l or name in request
        response = c.get('/profiles/api/geo/', {'l':'state','name':'asdf'})
        self.assertEqual(response.status_code, 404)

        # test invalid level
        response = c.get('/profiles/api/geo/', {'l':'bad'})
        self.assertEqual(response.status_code, 404)

        #test invalid geo
        response = c.get('/profiles/api/geo/', {'name':'Oz'})
        self.assertEqual(response.status_code, 404)

    def test_geography_api_valid(self):
        c = Client()
        # test level gettin'
        response = c.get('/profiles/api/geo/', {'l':'state'})
        self.assertEqual(response.content,'{"Rhode Island": {"parent_geos": {}, "geo_id": "RI", "id": 16, "name": "Rhode Island", "level": "State"}}')
        # test name getting
        response = c.get('/profiles/api/geo/', {'name':'Providence'})
        self.assertEqual(response.content, '{"Providence": {"parent_geos": {"State": "Rhode Island"}, "geo_id": "providence", "id": 21, "name": "Providence", "level": "Municipality"}}')

        #test depth
        response = c.get('/profiles/api/geo/', {'name':'Providence', 'depth':'1'})
        self.assertEqual(response.content,'{"Providence": {"name": "Providence", "level": "Municipality", "geo_id": "providence", "parent_geos": {"State": "Rhode Island"}, "id": 21, "children": [{"parent_geos": {"State": "Rhode Island", "Municipality": "Providence"}, "geo_id": "census_tract_25", "id": 26, "name": "Census Tract 25", "level": "Census Tract"}]}}')


class DataAgg(TestCase):
    """ Testing Census Value aggregators for commonly used operations"""

    def test_value_agg(self):
        from census.data import Value
        v1 = Value(10, 2)
        v2 = Value(15, 5)
        v3 = Value(20, 4)
        v4 = Value(5, 2)

        v = v1 + v2 + v3 + v4
        self.assertEqual(v.value, 50)
        self.assertEqual(v.moe, 7)

        v1 = Value(52354, 3303)
        v2 = Value(19464, 2011)
        v3 = Value(17190, 1854)

        v = v1 + v2 + v3

        self.assertEqual(v.value, 89008)
        self.assertEqual(float(v.moe),4288.50160312)

    def test_value_derived_porportions(self):
        from census.data import Value
        v1 = Value(4634, 989)
        v2 = Value(31713, 601)
        v = v1 / v2
        self.assertEqual(float(v.value), float(0.146123041024))
        self.assertEqual(float(v.moe), float(0.03118594897991360010090499164))


class DataAdapters(TestCase):
    fixtures = ['datasources.json', 'geolevels.json', 'indicators.json', 'geo-ri.json','geo-prov.json']

    def test_api_adapter(self):
        from census.data import Value
        state_rec = GeoRecord.objects.filter(name='Rhode Island')[0]
        state_rec.geo_id_segments = json.dumps({'040':"44"})
        state_rec.save()
        d_adapter = DataSource.objects.get(implementation='data_adapters.CensusAPI_SF1_2000')
        state_rec.level.data_sources.all().delete()
        state_rec.level.data_sources.add(d_adapter)
        state_rec.level.summary_level = "040"
        state_rec.level.save()

        muni_rec = GeoRecord.objects.filter(name='Providence')[0]
        muni_rec.geo_id_segments = '{"060": "59000", "050": "007", "040": "44"}'
        muni_rec.parent = state_rec
        muni_rec.save()

        muni_rec.level.data_sources.all().delete()
        muni_rec.level.data_sources.add(d_adapter)
        muni_rec.level.summary_level = "060"
        muni_rec.level.save()

        # ----------------------_BASIC API ---------------- #

        c = CensusAPI_SF1_2000()
        single_result = c.data(u'P001001', state_rec)
        self.assertTrue(single_result.value != None)

        c = CensusAPI_SF3_2000()
        single_result = c.data(u'P001001', state_rec)
        self.assertTrue(single_result.value != None)

        c = CensusAPI_SF1_2010()
        single_result = c.data(u'P0010001', state_rec)
        self.assertTrue(single_result.value != None)

        c = CensusAPI_ACS5_2010()
        single_result = c.data(u'B00001_001', state_rec)
        self.assertTrue(single_result.value != None)
        self.assertTrue(single_result.moe != None)

        c = CensusAPI_ACS5_2011()
        single_result = c.data(u'B00001_001', state_rec)
        self.assertTrue(single_result.value != None)
        self.assertTrue(single_result.moe != None)

        s2 = single_result + single_result
        c = CensusAPI_ACS5_2011()
        combined = c.data('B00001_001 + B00001_001', state_rec)
        self.assertEqual(combined.value, s2.value)
        self.assertEqual(combined.moe, s2.moe)

        s3 = single_result + single_result + single_result
        c = CensusAPI_ACS5_2011()
        combined = c.data('B00001_001 + B00001_001 + B00001_001', state_rec)
        self.assertEqual(combined.value, s3.value)
        self.assertEqual(combined.moe, s3.moe)


        c = CensusAPI_SF1_2010()
        combined = c.data('P0120006+P0120007', state_rec)
        self.assertEqual(combined.value,  40157.0)

        # ----------- nested geos api calls ----------------#
        c = CensusAPI_SF1_2010()
        muni_result = c.data('P0010001', muni_rec)
        self.assertTrue(muni_result.value != None)

        c = CensusAPI_SF1_2000()
        muni_result = c.data('P001001', muni_rec)
        self.assertTrue(muni_result.value == None)


    def test_file_adapter(self):
        #TODO: this test is incomplete
        file_path = os.path.join(os.path.dirname(__file__), 'sampledata/sample_file_adapter_file.csv')
        sample_file = open(file_path, 'rb')
        file_adapter = FileAdapter(data_file=sample_file)
        pass
        #result =  file_adapter.data('value', self.tract_rec)
        #self.assertEqual(result.value, 25)


class APIGeoTest(ResourceTestCase):
    """ Test API Getting values """
    fixtures = ['times.json','datasources.json', 'geolevels.json', 'datadomains.json','indicators.json','indicator_parts.json',
            'denoms.json', 'denom_parts.json', 'indicator_domains.json', 'geo-ri.json','geo-prov.json','geo-tract.json','ri-census-rows.json', 'prov-census-rows.json', 'tract29-census-rws.json']

    def setUp(self):
        self.ind_poptot = Indicator.objects.get(slug="poptot")
        self.ind_income7 = Indicator.objects.get(slug="income7")
        self.ind_income6 = Indicator.objects.get(slug="income6")
        self.muni_lev = GeoLevel.objects.get(slug="municipality")
        self.tract_lev = GeoLevel.objects.get(slug="census-tract")
        self.state_rec = GeoRecord.objects.filter(name='Rhode Island')[0]
        self.muni_rec = GeoRecord.objects.get(slug="providence", level=self.muni_lev)
        self.tract_rec = GeoRecord.objects.get(slug="census-tract-29", level=self.tract_lev)
        self.ind_income7.generate_data()
        self.ind_income7.generate_distribution()
        self.ind_income7.generate_change()

    def test_basic_get(self):
        print self.ind_income7.get_values_as_dict(self.tract_rec)



class Utils(TestCase):

    def test_alt_parser(self):
        from census.parse import AltFormulaParser
        p = AltFormulaParser()
        r = p.parse_string("B0001_001 + B0001_002 + B0001_004")
        #print type(p.expr_stack)


    def test_get_levels(self):
        #TODO: This isnt really a great test :\
        l = get_default_levels()
        self.assertTrue(type(l) is tuple)

    def test_parse_comparison(self):
        comp = parse_value_comparison("10")
        self.assertEqual(comp, ['10'])

        comp = parse_value_comparison(">10")
        self.assertEqual(comp, ['>', '10'])

        comp = parse_value_comparison(">=10")
        self.assertEqual(comp, ['>=', '10'])

        comp = parse_value_comparison("<10")
        self.assertEqual(comp, ['<', '10'])

        comp = parse_value_comparison("<=10")
        self.assertEqual(comp, ['<=', '10'])

    def test_op_comparison(self):
        # Test equals
        func = build_value_comparison("10") # 10 == 10 ?
        self.assertTrue(func(10))

        func = build_value_comparison(">10") # 11 > 10 ?
        self.assertTrue(func(11))

        func = build_value_comparison(">=10") # 10 >= 10 ?
        self.assertTrue(func(10))

        func = build_value_comparison("<10") # 9 <= 10 ?
        self.assertTrue(func(9))

        func = build_value_comparison("<=10") # 10 <= 10 ?
        self.assertTrue(func(10))



