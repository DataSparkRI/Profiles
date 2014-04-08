from django.utils import unittest
from profiles.models import *
from django.conf import settings

from profiles.views import get_indicator_csv_header, get_indicator_data_as_csv_row, get_denom_data_as_csv_row


class ProfilesTestCase(unittest.TestCase):

    def setUp(self):
        """
        About these tests:
        This test run with the DataTestRunner which bypasses making a new database. BE CAREFULL!
        't_i' = test_indicator
        't_i_wd' = test_indicator_with_denominator
        We use poptop as our primary test indicator since it is pretty simple.
        It should display change and percentage.

        """
        self.muni_geo_name = settings.DATA_TEST_SETTINGS['MUNICIPALITY']
        self.tract_geo_name = "Census Tract 36.02"#settings.DATA_TEST_SETTINGS['TRACT']
        self.muni_lev = GeoLevel.objects.get(slug='municipality')
        self.tract_lev = GeoLevel.objects.get(slug='census-tract')
        self.muni_record = GeoRecord.objects.filter(level=self.muni_lev, name=self.muni_geo_name)[0]
        self.tract_record = GeoRecord.objects.filter(level=self.tract_lev, name=self.tract_geo_name)[0]
        self.t_i = Indicator.objects.get(slug='poptot')
        self.t_i_wd = Indicator.objects.get(slug='income7') # this one has 2. Also has change and display percentage enabled


    def test_get_indicator_info(self):
        print "Testing with record: %s" % self.muni_record.name
        info = self.t_i.get_indicator_info(self.muni_record)
        self.assertNotEqual(info, None)

    def test_get_indicator_info_with_times(self):
        print "Testing with record-timefilter, first just 2000%s" % self.muni_record.name

        info = self.t_i.get_indicator_info(self.muni_record, [1])
        self.assertNotEqual(info, None)
        self.assertEqual(info['indicator_times'][0].name, "2000")

        # now test with 2 times
        info = self.t_i.get_indicator_info(self.muni_record, [1,6])
        self.assertEqual(info['indicator_times'][0].name, "2000")
        self.assertEqual(info['indicator_times'][1].name, "2006 - 2010")

    def test_get_indicator_with_change_percent(self):
        print "Testing indicator with change and percent"
        ind = Indicator.objects.get(slug='income7')
        info = ind.get_indicator_info(self.muni_record)
        #TODO: there needs to be an acceptance here


    def test_get_distribution(self):
        """ a purely cosmetic test for now """
        ind = Indicator.objects.get(slug='income7')
        info = ind.get_indicator_info(self.muni_record)
        #for key in info['distribution']:
            #print info['distribution'][key].percent

    def test_get_indicator_with_denoms_muni(self):
        print "Testing Indicator with Denoms with record: %s" % self.muni_record.name

        info = self.t_i_wd.get_indicator_info(self.muni_record)
        indicator = info['indicator']
        levels = [indicator.levels.all()]
        self.assertNotEqual(info, None)
        #self.assertEqual(len(info['denominators']), 2) # denoms return correctly

        for d in info['denominators']:
            # test that change exists
            if indicator.display_change:
                if self.muni_lev in levels:
                    self.assertNotEqual(d['change'], None)


    def test_get_indicator_with_denoms_tract(self):
        print "Testing Indicator with Denoms with record: %s" % self.tract_record.name

        info = self.t_i_wd.get_indicator_info(self.tract_record)
        indicator = info['indicator']
        levels = [indicator.levels.all()]
        self.assertNotEqual(info, None)
        #self.assertEqual(len(info['denominators']), 2) # denoms return correctly

        for d in info['denominators']:
            # test that change exists
            if indicator.display_change:
                # we need to test that the change filter actually works
                if self.tract_lev in levels:
                    self.assertNotEqual(d['change'], None)

    def test_csv_row_header(self):
        """ Tests that rows headers are created correctly from single indicator_data
            again cosmetic test.
            TODO:Setup mock system!
        """

        info = self.t_i_wd.get_indicator_info(self.muni_record)
        ind = info['indicator']
        # build expected header
        expected_header = ('record', 'indicator')
        expected_header += tuple([time.name for time in ind.get_times()])
        expected_header += ('change',)

        header = get_indicator_csv_header(info)
        #print "CSV Header"
        #print header
        #self.assertEqual(header, expected_header)


    def test_csv_row_indicator(self):
        """ Tests that indicator csv rows created correctly from single indicator_data. This test is incomplete... JUST DONT CRASH"""
        #self.muni_record = GeoRecord.objects.get(pk=11)
        self.muni_record = GeoRecord.objects.get(geo_id="WK")
        print "test_csv_row_indicator with %s" %  self.muni_record.name
        for rec in self.muni_record.child_records():
            info = self.t_i_wd.get_indicator_info(rec)
            ind = info['indicator']
            row = get_indicator_data_as_csv_row(info)
            #print row

        self.assertTrue(True)

    def test_csv_row_denom(self):
        """ Tests that indicator csv rows created correctly from a denom. This test is incomplete... JUST DONT CRASH!"""
        print "Test denom row"
        self.muni_record = GeoRecord.objects.get(geo_id="WK")
        for rec in self.muni_record.child_records():
            info = self.t_i_wd.get_indicator_info(rec)
            ind = info['indicator']
            row = get_denom_data_as_csv_row(info['denominators'][0], info['geo_record'])
            #print row

        self.assertTrue(True)
