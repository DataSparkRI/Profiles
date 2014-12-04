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
import re
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

class QUICKAPI(object):
    """ A data adapter that gets data via the census api. SEE http://www.census.gov/developers/data/"""
    def __init__(self,year, api_levs):
        # api_levs are remapped levels that the census api accepts EX: http://api.census.gov/data/2000/sf1/geo.html
        self.api_levs = api_levs
        self.year = year
        self.parser = AltFormulaParser()
        self.JSON = None

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

            parts_dict = OrderedDict()
            pcount = 0

            def get_value(formula, geo_record):
                try:
                   result = re.match(r"{(?P<part1>(.*))}(?P<op>[-|\+|\*|\\])(?P<part2>(.*))", formula).groupdict()
                   v2 = Value(self.get_api_data(result['part2'], geo_record))
                   return self.op_map[result['op']](get_value('{'+result['part1']+'}', geo_record), v2)

                except AttributeError:
                   val = Value(self.get_api_data(formula, geo_record))
                   return val
            
            formula = formula.replace('\n','')
            parts_dict[pcount] = get_value(formula, geo_record)
            
            #################################################################################
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
        url_str = url_str.replace(" ","%20")
        logger.debug("Fetching url %s via QuickAPI" % url_str)

        try:
            req = urllib2.Request(url_str)
            opener = urllib2.build_opener()
            f = opener.open(req)

            return f.read()
        except Exception as e:
            return "error: %s" % e
            
    def get_state_alpha(self, census_id):
        r = requests.get('https://www.census.gov/geo/reference/docs/state.txt')
        l = r.content.split("\n")
        for i in l:
            row = i.split("|")
            if row[0] == census_id:
               return row[1]
        return None

    def get_api_data(self, formula, geo_record):

        def get_total_value(json_data):
            value = None
            for i in json_data:
               try:
                   value = float(value) + float(i['Value'].replace(",",""))
               except TypeError:
                   value = float(i['Value'].replace(",",""))
            return value


        import json
        """ Needs to end up looking like this http://api.census.gov/data/2010/sf1?get=P0010001&for=county+subdivision:003&in=state:02+county:290"""
        url = "http://quickstats.nass.usda.gov/api/api_GET/?key=A92FB496-9FD3-3853-B73F-65B0752EE775"

        dic = json.loads(formula)
        record_sum_lev = geo_record.level.summary_level
        sum_lev = self.api_levs[record_sum_lev]

        if geo_record.census_id == geo_record.geo_id:
           state_id = geo_record.census_id
           county_code = None
        else:
           state_id = geo_record.geo_id[:2]
           county_code = geo_record.census_id
        

        if county_code == None:
           try:
              del dic['county_code']
           except KeyError: #json don't have county_code
              pass
        else:
           dic['county_code'] = county_code
           dic['year'] = self.year
           dic['agg_level_desc'] = sum_lev.upper()
           dic['state_fips_code'] = state_id

        r = self.get(url,dic)
        
        try:
           value = get_total_value(json.loads(r)["data"])
        except ValueError: #"bad request - invalid query"
           return None
        return value

    
class BLSAPI(object):
    """ A data adapter that gets data via the census api. SEE http://www.census.gov/developers/data/"""
    def __init__(self,year, api_levs):
        # api_levs are remapped levels that the census api accepts EX: http://api.census.gov/data/2000/sf1/geo.html
        self.api_levs = api_levs
        self.year = year
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
            try:
               return self.parser.opn[op]( op1, op2 )
            except:
               try:
                  if op=='/':
                     return op1 / op2
                  if op=='*':
                     return op1 * op2
               except:
                  return None
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
            ###################################################################################
            
            for part in self.parser.expr_stack:

                if part not in self.op_map:
                    parts_dict[pcount] = Value(self.get_api_data(part, geo_record))
                else:
                    # this is on op
                    parts_dict[pcount] = part
                pcount += 1
            
            #################################################################################
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
        
        def get_total_value(json_data):
           value = None
           for i in json_data['Results']['series'][0]['data']:
               try:
                  value = float(value) + float(i['value'])
               except TypeError:
                  value = float(i['value'])
           return value
        
        import requests
        import json
        import prettytable
 
        headers = {'Content-type': 'application/json'}
        data = json.dumps(params)
        p = requests.post(url, data=data, headers=headers)
        json_data = json.loads(p.text)
        logger.debug("Fetching url %s via BLSAPI" % url)

        try:
            p = requests.post(url, data=data, headers=headers)
            json_data = json.loads(p.text)
            return get_total_value(json_data)
            
        except Exception as e:
            return False

    def get_api_data(self, table, geo_record):
        try:
           return float(table)
        except:
           pass        

        url = 'http://api.bls.gov/publicAPI/v2/timeseries/data/'
        if geo_record.census_id == geo_record.geo_id:
           geo_id = geo_record.geo_id+'000'
        else:
           geo_id = geo_record.geo_id 
        
        prefix = table[0:2]
        # State Code, Area Code
        
        prefix_index = ["EN","EW"]
        for key in getattr(settings, 'BLS_KEYS', None):
           if prefix in prefix_index:
              seriesid = table[0:3] + geo_id + table[8:]
              value = self.get(url, {"seriesid": [seriesid],"startyear":self.year, "endyear":self.year, 
                               "registrationKey":key})
           else:
              value = self.get(url, {"seriesid": [table],"startyear":self.year, "endyear":self.year, 
                               "registrationKey":key})
           print key
           if value != False:
              print "Value: ", value
              if value == '-':
                 return None
              try:
                 return float(value)
              except:
                 return None
        return None

class QUICKAPI_2010(QUICKAPI):
    def __init__(self):
    
       super(QUICKAPI_2010, self).__init__('2010',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class QUICKAPI_2011(QUICKAPI):
    def __init__(self):
    
       super(QUICKAPI_2011, self).__init__('2011',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class QUICKAPI_2012(QUICKAPI):
    def __init__(self):
    
       super(QUICKAPI_2012, self).__init__('2012',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class QUICKAPI_2013(QUICKAPI):
    def __init__(self):
    
       super(QUICKAPI_2013, self).__init__('2013',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class BLSAPI_2010(BLSAPI):
    def __init__(self):
    
       super(BLSAPI_2010, self).__init__('2010',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class BLSAPI_2011(BLSAPI):
    def __init__(self):
    
       super(BLSAPI_2011, self).__init__('2011',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })
                
class BLSAPI_2012(BLSAPI):
    def __init__(self):
    
       super(BLSAPI_2012, self).__init__('2012',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

class BLSAPI_2013(BLSAPI):
    def __init__(self):
    
       super(BLSAPI_2013, self).__init__('2013',
                api_levs={
                    '040':'state',
                    '050':'county',
                    '060': 'county+subdivision',
                    '101':'block',
                    '140':'tract',
                    '150':'block+group',
                    '160': 'place',
                })

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

class CensusAPI_ACS5_2012_Profile(CensusAPI):
    # API levs supported by api
    def __init__(self):

        super(CensusAPI_ACS5_2012_Profile, self).__init__('2012', 'acs5/profile',
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
                for key, value in row.iteritems():
                    if key.lower() =='moe': # Try to mach 'moe'
                       return Value(self.parse_value(row[formula]), moe=self.parse_value(row[key]))
                #return Value(self.parse_value(row[formula]), moe=self.parse_value(row['moe']))

        return None
