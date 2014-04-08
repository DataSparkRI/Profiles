# Tools for importing Geographies created specifically for pittsburg
import csv
from geography import parse_file


def get_census_geos(census_geos_file, census_src):
    """ Get Logrecnos for each geo in geos list
        @param geos_list_file is path to a file (see below)
        @param census_geos_file is a path to a census_geos_file
        @param censu_src is one of: 2000 2010 or acs2010

        The Geos file we recieve from Pittsburg look like this
        STATEFP,COUNTYFP,COUNTYNS,GEOID,NAME,NAMELSAD,LSAD,CLASSFP,MTFCC,CSAFP,CBSAFP,METDIVFP,FUNCSTAT,ALAND,AWATER,INTPTLAT,INTPTLON
        ---
        AND
        ---
        CountyTract2010.csv
        OBJECTID,STATEFP10,COUNTYFP10,TRACTCE10,GEOID10,NAME10,NAMELSAD10,MTFCC10,FUNCSTAT10,ALAND10,AWATER10,INTPTLAT10,INTPTLON10,Shape_Leng,Shape_Area
    """
    # 1) First we need to parse the census_geos_file
