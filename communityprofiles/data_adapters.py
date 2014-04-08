"""
Data Adapters act as a bridge between the profiles app and various data sources.
They are responsible for the following:

    - interpreting and running formulas from Indicator objects
    - mapping the requested geo objects to a geo record that they understand
"""

import csv
from decimal import Decimal
import logging

from census.datasources import Census2000, ACS2010e5 as _ACS2010e5, Census2010 as _Census2010
from census.data import Value
from census.parse import FormulaParser, AltFormulaParser
from profiles.models import GeoLevel, GeoRecord, IndicatorPart, DenominatorPart, PrecalculatedValue, DataSource
from django.conf import settings
import requests
from pyparsing import ParseResults
import json
import urllib2
from collections import OrderedDict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#------------------------------------ OLD WAY------------------------------------
def _to_local_2000_acs_geo_dict(p_geo_record, fileid):
    geo_template = {
        'FILEID': 'ACSSF',
        'STUSAB': 'RI',
        'CHARITER': '000',
        'CIFSN': '01',
    }
    results = []

    if p_geo_record.level.name == 'State':
        geo_record = p_geo_record
        target = GeoLevel.objects.get(name='ACS 2010e5 State')
        mapped = geo_record.mapped_to(target)
        for g in mapped:
            r = geo_template.copy()
            r['LOGRECNO'] = g.geo_id
            r['SUMLEV'] = '040'
            results.append(r)

    if p_geo_record.level.name == 'Census Tract':
        geo_record = p_geo_record
        target = GeoLevel.objects.get(name='ACS 2010e5 Tract')
        mapped = geo_record.mapped_to(target)
        for g in mapped:
            r = geo_template.copy()
            r['LOGRECNO'] = g.geo_id
            r['SUMLEV'] = '140'
            results.append(r)

    if p_geo_record.level.name == 'Municipality':
        geo_record = p_geo_record
        target = GeoLevel.objects.get(name='ACS 2010e5 Municipality')
        mapped = geo_record.mapped_to(target)
        for g in mapped:
            r = geo_template.copy()
            r['LOGRECNO'] = g.geo_id
            r['SUMLEV'] = '060'
            results.append(r)
    return results


def _to_local_2000_sf1_geo_dict(geo_record, fileid):
    geo_template = {
        'FILEID': 'uSF1',
        'STUSAB': 'RI',
        'CHARITER': '000',
        'CIFSN': '01',
    }
    results = []

    if geo_record.level.name == 'State':
        target = GeoLevel.objects.get(name='Census 2000 SF1 State')
        mapped = geo_record.mapped_to(target)
        for g in mapped:
            r = geo_template.copy()
            r['LOGRECNO'] = g.geo_id
            r['SUMLEV'] = '040'
            results.append(r)
    if geo_record.level.name == 'Census Tract':
        target = GeoLevel.objects.get(name='Census 2000 SF1 Tract')
        mapped = geo_record.mapped_to(target)
        if len(mapped)==0:
            #using block groups
            target = GeoLevel.objects.get(name='Census 2000 SF1 Block')
            mapped = geo_record.mapped_to(target)
        for g in mapped:
            r = geo_template.copy()
            r['LOGRECNO'] = g.geo_id
            r['SUMLEV'] = '101'
            results.append(r)
    if geo_record.level.name == '':
        target = GeoLevel.objects.get(name='Census 2000 SF1 Municipality')
        mapped = geo_record.mapped_to(target)
        for g in mapped:
            r = geo_template.copy()
            r['LOGRECNO'] = g.geo_id
            r['SUMLEV'] = '060'
            results.append(r)
    return results


def _to_local_2000_sf3_geo_dict(geo_record, fileid):
    geo_template = {
        'FILEID': 'uSF3',
        'STUSAB': 'RI',
        'CHARITER': '000',
        'CIFSN': '01',
    }
    results = []
    if geo_record.level.name == 'State':
        target = GeoLevel.objects.get(name='Census 2000 SF3 State')
        mapped = geo_record.mapped_to(target)
        for g in mapped:
            r = geo_template.copy()
            r['LOGRECNO'] = g.geo_id
            r['SUMLEV'] = '040'
            results.append(r)
    if geo_record.level.name == 'Census Tract':
        target = GeoLevel.objects.get(name='Census 2000 SF3 Tract')
        mapped = geo_record.mapped_to(target)

        if len(mapped)==0:
            #using block groups
            target = GeoLevel.objects.get(name='Census 2000 SF3 Block Group')
            mapped = geo_record.mapped_to(target)

        for g in mapped:
            r = geo_template.copy()
            r['LOGRECNO'] = g.geo_id
            r['SUMLEV'] = '090'
            results.append(r)
    if geo_record.level.name == 'Municipality':
        target = GeoLevel.objects.get(name='Census 2000 SF3 Municipality')
        mapped = geo_record.mapped_to(target)
        for g in mapped:
            r = geo_template.copy()
            r['LOGRECNO'] = g.geo_id
            r['SUMLEV'] = '060'
            results.append(r)
    return results


def _to_local_2010sf1_geo_dict(geo_record):
    results = []
    if geo_record.level.name == 'State':
        target = GeoLevel.objects.get(name='Census 2010 State')
        mapped = geo_record.mapped_to(target)
        for g in mapped:
            results.append({
                'FILEID': 'SF1ST',
                'STUSAB': 'RI',
                'SUMLEV': '040',
                'CHARITER': '000',
                'CIFSN': '01',
                'LOGRECNO': g.geo_id,
            })

    if geo_record.level.name == 'Census Tract':
        target = GeoLevel.objects.get(name='Census 2010 Tract')
        mapped = geo_record.mapped_to(target)
        for g in mapped:
            results.append({
                'FILEID': 'SF1ST',
                'STUSAB': 'RI',
                'SUMLEV': '140',
                'CHARITER': '000',
                'CIFSN': '01',
                'LOGRECNO': g.geo_id,
            })

    if geo_record.level.name == 'Municipality':
        target = GeoLevel.objects.get(name='Census 2010 Municipality')
        mapped = geo_record.mapped_to(target)
        for g in mapped:
            results.append({
                'FILEID': 'SF1ST',
                'STUSAB': 'RI',
                'SUMLEV': '060',
                'CHARITER': '000',
                'CIFSN': '01',
                'LOGRECNO': g.geo_id,
            })
    return results

#------------------------------------END OLD WAY------------------------------------

def check_for_cached_value(data_adapter, formula, geo_record):
    pass



def check_for_precalculated_value(data_adapter, formula, geo_record):
	"""Check to see if there is a precalculated value """
	try:
		precal_val = PrecalculatedValue.objects.get(
			data_source = DataSource.objects.get(implementation="data_adapters.%s" % data_adapter.__class__.__name__),
			table = formula,
			geo_record = geo_record
		)

		return Value(precal_val.value)
	except PrecalculatedValue.DoesNotExist:
		return None

class BaseCensusDataAdapter(object):
    def __init__(self):
        super(BaseCensusDataAdapter, self).__init__()

    def data(self, formula, geo_record, **kwargs):
        if not hasattr(self, 'source'):
            raise NotImplementedError('BaseCensusDataAdapter cannot be called if a source attribute is not set')

        precalc = check_for_precalculated_value(self,formula, geo_record)
        if precalc:
            return precalc
        else:
            local_geos = self.map_to_local_geos(geo_record)
            return self.source.data(formula, local_geos,**kwargs)  # map(lambda g: self.source.data(formula, g), local_geos)


class Census2000SF1(BaseCensusDataAdapter):
    def __init__(self):
        self.source = Census2000('SF1')
        super(Census2000SF1, self).__init__()

    def map_to_local_geos(self, geo_record):
        return _to_local_2000_sf1_geo_dict(geo_record, 'uSF1')


class Census2000SF3(BaseCensusDataAdapter):
    def __init__(self):
        self.source = Census2000('SF3')
        super(Census2000SF3, self).__init__()

    def map_to_local_geos(self, geo_record):
        return _to_local_2000_sf3_geo_dict(geo_record, 'uSF3')


class Census2010SF1(BaseCensusDataAdapter):
    def __init__(self):
        self.source = _Census2010('sf1')
        super(Census2010SF1, self).__init__()

    def map_to_local_geos(self, geo_record):
        return _to_local_2010sf1_geo_dict(geo_record)


class ACS2010e5(BaseCensusDataAdapter):
    def __init__(self):
        self.source = _ACS2010e5()
        super(ACS2010e5, self).__init__()

    def map_to_local_geos(self, geo_record):

        return _to_local_2000_acs_geo_dict(geo_record, 'ACSSF')


class CensusAPI(object):
    """ A data adapter that gets data via the census api. SEE http://www.census.gov/developers/data/"""
    def __init__(self,year, dataset, api_levs):
        # api_levs are remapped levels that the census api accepts EX: http://api.census.gov/data/2000/sf1/geo.html
        self.api_levs = api_levs
        self.year = year
        self.dataset = dataset
        self.parser = AltFormulaParser()


        self.op_map = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
        }

    def evaluate(self, stack):
        op = stack.pop()
        if type(op) == str and op in "+-*/^":
            op2 = self.evaluate( stack )
            op1 = self.evaluate(stack)
            return self.parser.opn[op]( op1, op2 )
        else:
            return op

    def check_for_existing_value(self, formula, geo_record):
        return None #TODO: Bypassing this for now
        """ Check to see if this formula exists any where else and return the value for given geo_record"""
        logger.debug("----Checking for existing formula " + formula + "------")

        # first try indicator_parts
        ds = DataSource.objects.get(implementation="data_adapters.%s" % self.__class__.__name__)
        matching_ind_parts = IndicatorPart.objects.filter(data_source=ds, formula = formula)

        if matching_ind_parts:
            # try to get the value from here.
            logger.debug("Found indicator parts")
            for ind_part in matching_ind_parts:
                value = ind_part.indicator.get_indicator_value(geo_record, ind_part.time)
                if value is not None:
                    return Value(value=value.number, moe=value.moe)

            return None
        else:
            matching_denom_parts = DenominatorPart.objects.filter(data_source=ds, formula=formula)
            if matching_denom_parts:
                logger.debug("Found denom part")
                # get this value from the denominator
                for denom_part in matching_denom_parts:
                    value = denom_part.denominator.get_value(geo_record, denom_part.part.time)
                    if value is not None:
                        return Value(value=value.number, moe=value.moe)
                return None

        return None

    def data(self, formula, geo_record, **kwargs):
        # return a precalculated value if found
        if formula.strip() == "":
            return None

        precalc = check_for_precalculated_value(self, formula, geo_record)

        if precalc:
            return precalc
        else:
            # Get Data
            # From here we have to make requests to the census api based on
            # what Year we want
            cached_value = self.check_for_existing_value(formula, geo_record)
            if cached_value is not None:
                logger.debug("Using cached value")
                return cached_value

            self.parser.parse_string(formula)
            parts_dict = OrderedDict()
            pcount = 0
            # build a dict of values
            for part in self.parser.expr_stack:
                if part not in self.op_map:
                    # This is a table num
                    if 'acs' not in self.dataset:
                        parts_dict[pcount] = Value(self.get_api_data(part, geo_record))
                    else:
                        # this is an ACS value
                        estimate = self.get_api_data(part+"E", geo_record)
                        moe = self.get_api_data(part+"M", geo_record)
                        parts_dict[pcount] = Value(estimate, moe)
                else:
                    # this is on op
                    parts_dict[pcount] = part
                pcount += 1

            # now we need to actually need to run the formula
            val = self.evaluate(parts_dict.values())
            return val


    def make_geo_string(self, geo_id, sum_lev=None):
        """ Take the geo_record.geoid and turn it into something the census api can use. the 'in' bit """
        geoids = json.loads(geo_id)
        sumlevs = geoids.keys()
        sumlevs.sort() # the order of the sumlevs should be lowest to highest. Ex: 040, 050, 060
        geos = []
        for s in sumlevs:
            if s!=None:
                if s!=sum_lev:
                    geos.append("{sum_lev_name}:{geo_id}".format(sum_lev_name=self.api_levs[s], geo_id=geoids[s])) # we want state:id,county:201 etc...
            else:
                geos.append("{sum_lev_name}:{geo_id}".format(sum_lev_name=self.api_levs[s], geo_id=geoids[s])) # we want state:id,county:201 etc...

        return '+'.join(geos)

    def get(self, url, params={}):
        url_str = url
        for k, v in params.iteritems():
            url_str += "&" + k + "=" + v

        logger.debug("Fetching url %s via CensusAPI" % url_str)

        try:
            req = urllib2.Request(url_str)
            opener = urllib2.build_opener()
            f = opener.open(req)
            return f.read()
        except Exception as e:
            return "error: %s" % e

    def get_api_data(self, table, geo_record):
        """ Needs to end up looking like this http://api.census.gov/data/2010/sf1?get=P0010001&for=county+subdivision:003&in=state:02+county:290"""
        url = "http://api.census.gov/data/{year}/{dataset}?".format(year=self.year, dataset=self.dataset)
        key = getattr(settings, 'CENSUS_API_KEY', None)
        record_sum_lev = geo_record.level.summary_level
        sum_lev = self.api_levs[record_sum_lev]

        #print table, geo_record

        if record_sum_lev!="040":
            r = self.get(url, {'key':key, 'get':table, 'for':sum_lev+":"+geo_record.census_id, 'in':self.make_geo_string(geo_record.geo_id_segments, record_sum_lev)})
        else:
            # state data urls are diffent
            r = self.get(url,{'key':key, 'get':table, 'for':self.make_geo_string(geo_record.geo_id_segments)})
        if "error" in r:
            logger.error("Couldt find %s %s" % (table, geo_record))
            return None
        else:
            try:
                # this is what this response looks like [[u'P001001', u'state'], [u'1048319', u'44']]
                result = json.loads(r)[1][0]
                return float(result)
            except Exception as e:
                logger.debug(e)
                #TODO: Log
                return None


class CensusAPI_SF1_2000(CensusAPI):
    # API levs supported by api
    def __init__(self):

        super(CensusAPI_SF1_2000, self).__init__('2000', 'sf1',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class CensusAPI_SF3_2000(CensusAPI):
    # API levs supported by api
    def __init__(self):

        super(CensusAPI_SF3_2000, self).__init__('2000', 'sf3',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })


class CensusAPI_SF1_2010(CensusAPI):
    # API levs supported by api
    def __init__(self):

        super(CensusAPI_SF1_2010, self).__init__('2010', 'sf1',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class CensusAPI_ACS5_2010(CensusAPI):
    # API levs supported by api
    def __init__(self):

        super(CensusAPI_ACS5_2010, self).__init__('2010', 'acs5',
                api_levs={
                    '010':'us',
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class CensusAPI_ACS5_2011(CensusAPI):
    # API levs supported by api
    def __init__(self):

        super(CensusAPI_ACS5_2011, self).__init__('2011', 'acs5',
                api_levs={
                    '010':'us',
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class CensusAPI_ACS5_2012(CensusAPI):
    # API levs supported by api
    def __init__(self):

        super(CensusAPI_ACS5_2012, self).__init__('2012', 'acs5',
                api_levs={
                    '010':'us',
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class FileAdapter(BaseCensusDataAdapter):
    def __init__(self, data_file=None):
        if data_file is None:
            raise Exception('data_file cannot be None for FileAdapter')
        self.data_file = data_file
        super(FileAdapter, self).__init__()

    def parse_value(self, value):
        # we need to clean out all spaces Just in case
        value = value.replace(' ','')
        if value == '' or value is None:
            return None

        return Decimal(value)

    def data(self, formula, geo_record):
        reader = csv.DictReader(self.data_file, delimiter=",")
        for row in reader:
            if row['level'].lower() == geo_record.level.name.lower() and row['geo_id'] == geo_record.geo_id:
                return Value(self.parse_value(row['value']), moe=self.parse_value(row['moe']))

        return None
