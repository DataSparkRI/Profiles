import os, sys
from profiles.tests.utils.census_to_db_importer import *
from profiles.models import *

def load_2000sf1_data():
    file_path = os.path.join(os.path.dirname(__file__),'..', 'sampledata/sampledata_2000sf1.csv')
    load_census_2000(file_path)

def load_2000sf3_data():
    file_path = os.path.join(os.path.dirname(__file__),'..', 'sampledata/sampledata_2000sf3.csv')
    load_census_2000(file_path)

def load_2010sf_data():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'sampledata/sampledata_2010_SF1.csv')
    load_census_2010SF(file_path)

def load_acs_data():
    file_path = os.path.join(os.path.dirname(__file__),'..', 'sampledata/')
    load_census_acs(file_path+"sampledata_ACS_06_10.csv")
    load_census_acs(file_path+"sampledata_ACS_06_10_poptot.csv")

def build_geos(self):
    """ Builds all the standard geos to test with. Mostly this exists to keep the test readable
        For testing purposes, we are gonna make up georecords ids aka LOGRECNO
        State: 0000001
        Muni-Providence: 0000011
        Tract 192: 0000089
    """
    self.state_lev = GeoLevel.objects.get(name='State')
    self.state_sf1_lev = GeoLevel.objects.get(name='Census 2000 SF1 State')
    self.state_sf3_lev = GeoLevel.objects.get(name='Census 2000 SF3 State')
    self.state_2010_lev = GeoLevel.objects.get(name='Census 2010 State')
    self.state_acs_lev = GeoLevel.objects.get(name='ACS 2010e5 State')

    self.muni_lev = GeoLevel.objects.get(name='Municipality')
    self.muni_sf1_lev = GeoLevel.objects.get(name='Census 2000 SF1 Municipality')
    self.muni_sf3_lev = GeoLevel.objects.get(name='Census 2000 SF3 Municipality')
    self.muni_2010_lev = GeoLevel.objects.get(name='Census 2010 Municipality')
    self.muni_acs_lev = GeoLevel.objects.get(name='ACS 2010e5 Municipality')

    self.tract_lev = GeoLevel.objects.get(name='Census Tract')
    self.tract_sf1_lev = GeoLevel.objects.get(name='Census 2000 SF1 Tract')
    self.tract_sf3_lev = GeoLevel.objects.get(name='Census 2000 SF3 Tract')
    self.tract_2010_lev = GeoLevel.objects.get(name='Census 2010 Tract')
    self.tract_acs_lev = GeoLevel.objects.get(name='ACS 2010e5 Tract')

    # create some geo_records... this is normally done via the census geo files
    self.state_rec = GeoRecord.objects.create(level=self.state_lev, name="Rhode Island", slug="state-rhode-island", geo_id='RI')
    self.state_sf1_rec = GeoRecord.objects.create(level=self.state_sf1_lev, name="Rhode Island", slug="state-rhode-island", geo_id='0000001')
    self.state_sf3_rec = GeoRecord.objects.create(level=self.state_sf3_lev, name="Rhode Island", slug="state-rhode-island", geo_id='0000001')
    self.state_2010_rec = GeoRecord.objects.create(level=self.state_2010_lev, name="Rhode Island", slug="state-rhode-island", geo_id='0000001')
    self.state_acs_rec = GeoRecord.objects.create(level=self.state_acs_lev, name="Rhode Island", slug="state-rhode-island", geo_id='0000001')

    # add mappings for state
    self.state_rec.mappings.add(self.state_sf1_rec, self.state_sf3_rec, self.state_2010_rec, self.state_acs_rec)

    # create a muni
    self.muni_rec = GeoRecord.objects.create(level=self.muni_lev,parent=self.state_rec, name="Providence", slug="providence", geo_id='providence')
    self.muni_sf1_rec = GeoRecord.objects.create(level=self.muni_sf1_lev, parent=self.state_sf1_rec, name="Providence", slug="providence", geo_id='0014943')
    self.muni_sf3_rec = GeoRecord.objects.create(level=self.muni_sf3_lev,parent=self.state_sf3_rec, name="Providence", slug="providence", geo_id='0001522')
    self.muni_2010_rec = GeoRecord.objects.create(level=self.muni_2010_lev, parent=self.state_2010_rec, name="Providence", slug="providence", geo_id='0017456')
    self.muni_acs_rec = GeoRecord.objects.create(level=self.muni_acs_lev, parent=self.state_acs_rec, name="Providence", slug="providence", geo_id='0000040')

    # add mappings for muni
    self.muni_rec.mappings.add(self.muni_sf1_rec, self.muni_sf3_rec, self.muni_2010_rec, self.muni_acs_rec)

    # create a tract
    self.tract_rec = GeoRecord.objects.create(level=self.tract_lev, parent=self.muni_rec, name="Census Tract 25", slug="census_tract_25", geo_id='census_tract_25')
    self.tract_sf1_rec = GeoRecord.objects.create(level=self.tract_sf1_lev, parent=self.muni_sf1_rec, name="Census Tract 25", slug="census_tract_25", geo_id='0002041')
    self.tract_sf3_rec = GeoRecord.objects.create(level=self.tract_sf3_lev, parent=self.muni_sf3_rec, name="Census Tract 25", slug="census_tract_25", geo_id='0002041')
    self.tract_2010_rec = GeoRecord.objects.create(level=self.tract_2010_lev,  parent=self.muni_2010_rec, name="Census Tract 25", slug="census_tract_25", geo_id='0022431')
    self.tract_acs_rec = GeoRecord.objects.create(level=self.tract_acs_lev,  parent=self.muni_acs_rec, name="Census Tract 25", slug="census_tract_25", geo_id='0000524')

    # add mappings for tract
    self.tract_rec.mappings.add(self.tract_sf1_rec, self.tract_sf3_rec, self.tract_2010_rec, self.tract_acs_rec)
