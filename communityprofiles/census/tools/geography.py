import csv
import sys
import re
import os
from collections import OrderedDict

"""
http://www.census.gov/prod/cen2000/doc/sf1.pdf Figure 2.5 2000
http://www.census.gov/prod/cen2010/doc/sf1.pdf Figure 2.5 2010
http://www2.census.gov/acs2010_5yr/summaryfile/ACS_2006-2010_SF_Tech_Doc.pdf acs
    sample for the acs, the txt file not the csv
    http://www2.census.gov/acs2010_5yr/summaryfile/2006-2010_ACSSF_By_State_By_Sequence_Table_Subset/RhodeIsland/All_Geographies_Not_Tracts_Block_Groups/g20105ri.txt
"""


"""
Summary Level Definitions
Defined as:
SUMLEV: (Geographies, Hierarchy)
"""

SUM_LEV = {
        '010':('United States', 'United States',),
        '020':('Region',),
        '030':('Division',),
        '040':('State','State'),
        '050':('County','State-County'),
        '060':('County Subdivision', 'State-County-County-Subdivision',),
        '067':('Subminor Civil Division','State-County-County Subdivision-Subminor Civil Division',),
        '070':('Place/Remainder', 'State-County-County Subdivision-Place/Remainder'),
        '080':('Census Tract','State-County-County Subdivision-Place/Remainder-Census Tract'),
        '140':('Census Tract','State-County-Census Tract'),
        '150':('Block Group', 'State-County-Census Tract-Block Group'),
        '155':('State-Place-County',),
        '160':('State-Place',),
        '170':('State-Consolidated City',),
        '172':('State-Consolidated City-Place Within Consolidated City',),
        '230':('State-Alaska Native Regional Corporation',),
        '250':('American Indian Area/Alaska Native Area/Hawaiian Home Land',),
        '251':('American Indian Area-Tribal Subdivision/Remainder',),
        '252':('American Indian Area/Alaska Native Area (Reservation or Statistical Entity Only) US', ' All Geos Xcpt T&BG', '',),
        '254':('American Indian Area (Off-Reservation Trust Land Only)/Hawaiian Home Land',),
        '256':('American Indian Area-Tribal Census Tract',),
        '258':('American Indian Area-Tribal Census Tract-Tribal Block Group',),
        '260':('American Indian Area/Alaska Native Area/Hawaiian Home Land-State',),
        '269':('American Indian Area/Alaska Native Area/Hawaiian Home Land-State- Place/Remainder',),
        '270':('American Indian Area/Alaska Native Area/Hawaiian Home Land-State-County',),
        '280':('State-American Indian Area/Alaska Native Area/Hawaiian Home Land',),
        '283':('State-American Indian Area/Alaska Native Area (Reservation or Statistical Entity Only)',),
        '286':('State-American Indian Area (Off-Reservation Trust Land Only)/Hawaiian Home Land State', ' All Geos Xcpt T&BG', '',),
        '290':('American Indian Area-Tribal Subdivision/Remainder-State',),
        '291':('American Indian Area (Reservation Only)-Tribal Census Tract',),
        '292':('American Indian Area (Off-Reservation Trust Land Only)-Tribal Census Tract',),
        '293':('American Indian Area (Reservation Only)-Tribal Census Tract-Tribal Block Group',),
        '294':('American Indian Area (Off-Reservation Trust Land Only)-Tribal Census Tract-Tribal Block Group',),
        '310':('Metropolitan Statistical Area/Micropolitan Statistical Area',),
        '311':('Metropolitan Statistical Area/Micropolitan Statistical Area-State',),
        '312':('Metropolitan Statistical Area/Micropolitan Statistical Area-State-Principal City',),
        '313':('Metropolitan Statistical Area/Micropolitan Statistical Area-State-County',),
        '314':('Metropolitan Statistical Area-Metropolitan Division',),
        '315':('Metropolitan Statistical Area-Metropolitan Division-State',),
        '316':('Metropolitan Statistical Area-Metropolitan Division-State-County',),
        '320':('State-Metropolitan Statistical Area/Micropolitan Statistical Area',),
        '321':('State-Metropolitan Statistical Area/Micropolitan Statistical Area-Principal City',),
        '322':('State-Metropolitan Statistical Area/Micropolitan Statistical Area-County',),
        '323':('State-Metropolitan Statistical Area-Metropolitan Division',),
        '324':('State-Metropolitan Statistical Area-Metropolitan Division-County',),
        '330':('Combined Statistical Area',),
        '331':('Combined Statistical Area-State',),
        '332':('Combined Statistical Area-Metropolitan Statistical Area/Micropolitan Statistical Area',),
        '333':('Combined Statistical Area-Metropolitan Statistical Area/Micropolitan Statistical Area-State',),
        '335':('Combined New England City and Town Area',),
        '336':('Combined New England City and Town Area-State',),
        '337':('Combined New England City and Town Area-New England City and Town Area',),
        '338':('Combined New England City and Town Area-New England City and Town Area-State',),
        '340':('State-Combined Statistical Area',),
        '341':('State-Combined Statistical Area-Metropolitan Statistical Area/Micropolitan Statistical Area',),
        '345':('State-Combined New England City and Town Area',),
        '346':('State-Combined New England City and Town Area-New England City and Town Area',),
        '350':('New England City and Town Area',),
        '351':('New England City and Town Area-State',),
        '352':('New England City and Town Area-State-Principal City',),
        '353':('New England City and Town Area-State-County',),
        '354':('New England City and Town Area-State-County-County Subdivision',),
        '355':('New England City and Town Area (NECTA)-NECTA Division',),
        '356':('New England City and Town Area (NECTA)-NECTA Division-State',),
        '357':('New England City and Town Area (NECTA)-NECTA Division-State-County',),
        '358':('New England City and Town Area (NECTA)-NECTA Division-State-County-County Subdivision',),
        '360':('State-New England City and Town Area',),
        '361':('State-New England City and Town Area-Principal City',),
        '362':('State-New England City and Town Area-County',),
        '363':('State-New England City and Town Area-County-County Subdivision',),
        '364':('State-New England City and Town Area (NECTA)-NECTA Division',),
        '365':('State-New England City and Town Area (NECTA)-NECTA Division-County',),
        '366':('State-New England City and Town Area (NECTA)-NECTA Division-County-County Subdivision',),
        '400':('Urban Area',),
        '500':('State-Congressional District',),
        '510':('State-Congressional District-County',),
        '550':('State-Congressional District-American Indian Area/Hawaiian Home Land',),
        '610':('State-State Legislative District (Upper Chamber)',),
        '612':('State-State Legislative District (Upper Chamber)-County',),
        '620':('State-State Legislative District (Lower Chamber)',),
        '622':('State-State Legislative District (Lower Chamber)-County',),
        '795':('State-Public Use Microdata Sample Area (PUMA)',),
        '950':('State-School District (Elementary)/Remainder',),
        '960':('State-School District (Secondary)/Remainder',),
        '970':('State-School District (Unified)/Remainder',),
}

VALID_SUM_LEVS = SUM_LEV.keys()

SUPPORTED_DATASETS = ('2000', '2010', 'acs2010')


def geo_id_to_segments(geoid, sum_lev):
    """ Parse a geoid into an object of segments"""
    segments = {}
    if sum_lev == "040":
        segments = {'040':geoid}
    elif sum_lev =="050":
        # Ex: 42007
        segments = {'040':geoid[:2], '050': geoid[2:]}
    elif sum_lev == "060":
        # Ex: 4200323616
        segments = {'040':geoid[:2], '050': geoid[2:5], '060':geoid[5:]}
    elif sum_lev == "140":
        #Ex: 42003010300
        segments = {'040':geoid[:2], '050': geoid[2:5], '140':geoid[5:11]}
    elif sum_lev == "150":
        #ex: 420035003001
        segments = {'040':geoid[:2], '050': geoid[2:5], '140':geoid[5:11], '150':geoid[11:]}
    else:
        segments[sum_lev] = geoid
    return segments


def get_sum_lev_names(sum_levs):
    """ Return a tuple of sum_lev names from an iterable of sum_lev nums"""
    names_set = set()
    for sl in sum_levs:
        try:
            names_set.add(SUM_LEV[sl][0])
        except Exception as e:
            print(e)
    return tuple(names_set)

def get_sum_lev_name(sum_lev):
    return SUM_LEV[sum_lev][0]

def get_sum_lev(line, source):
    """ Get the sum lev for the geography """
    if source == '2000':
        return line[8:11]
    elif source == '2010':
        return line[8:11]
    elif source == 'acs2010':
        return line[8:11]
    else:
        regex = re.compile("\d{3}")
        matches = regex.findall(line)
        for m in matches:
            if m in VALID_SUM_LEVS:
                return m
        return None

def get_logrecno(line, source):
    if source == '2000':
        return line[18:25]
    elif source =='2010':
        return line[18:25]
    elif source =='acs2010':
        return line[13:20].zfill(7)
    else:
        # guess
        regex = re.compile("0{2}\d{5}")
        matches = matches = regex.findall(line)
        if len(matches) > 1:
            matches.sort()
        if matches:
            return matches[0]
        else:
            return None

def get_geoid(line, source, sum_lev):
    """ Return the geo id from files as Ordered Dict"""
    geo_id = OrderedDict()
    if sum_lev == "040":
        levs = ['040']
    elif sum_lev =="050":
        levs = ['050', '040']
    elif sum_lev == "060":
        levs = ['060', '050', '040']
    elif sum_lev == "140":
        levs = ['140', '050', '040']
    elif sum_lev == "150":
        levs = ['150', '140', '050', '040']
    else:
        return None
    levs.sort()
    # Do a backwards iteration of summary levels
    if source == '2000':
        for lev in levs:
            geo_id[lev] = get_geo_id_uf1(line, lev)
    elif source =='2010':
        for lev in levs:
            geo_id[lev] = get_geo_id_sf1(line, lev)
    elif source =='acs2010':
        for lev in levs:
            geo_id[lev] = get_geo_id_acs2010(line, lev)
    return geo_id

def get_geo_id_uf1(line, sum_lev):
    """ Return the geo id for uf1 files"""
    if sum_lev == "040":
        return line[27:29]
    elif sum_lev =="050":
        return line[31:34]
    elif sum_lev == "060":
        return line[36:41]
    elif sum_lev == "140":
                # There should be a Geo Record in the Base Geographies for
                # everyone that exists in each data set.
        return line[55:61]
    elif sum_lev == "150":
        return line[61:62]
    else:
        return None

def get_geo_id_sf1(line, sum_lev):
    """ Return the geo id for uf1 files"""
    if sum_lev == "040":
        return line[27:29]
    elif sum_lev =="050":
        return line[29:32]
    elif sum_lev == "060":
        return line[36:41]
    #elif sum_lev == "080":
    #    return name_field
                # There should be a Geo Record in the Base Geographies for
                # everyone that exists in each data set.
    elif sum_lev == "140":
        return line[54:60]
    elif sum_lev == "150":
        return line[60:61]
    else:
        return None

def get_geo_id_acs2010(line, sum_lev):
    """ Return the geo id for uf1 files"""
    if sum_lev == "040":
        return line[25:27]
    elif sum_lev =="050":
        return line[27:30]
    elif sum_lev == "060":
        return line[30:35]
    #elif sum_lev == "080":
    #    return name_field
    elif sum_lev == "140":
        return line[40:46]
    elif sum_lev == "150":
        return line[46:47]
    else:
        return None

def get_name(line, source, sum_lev):
    """ Get the name from line based on its sum_lev"""
    if source == '2000':
        return get_name_uf1(line, sum_lev)
    elif source =='2010':
        return get_name_sf1(line, sum_lev)
    elif source =='acs2010':
        return get_name_acs2010(line, sum_lev)

    return None

def get_name_uf1(line, sum_lev):
    """ Get the Census Name of this geo based on its sum lev"""
    name_field = line[200:290].strip()

    if sum_lev == "040":
        return name_field
    elif sum_lev =="050":
        return name_field
    elif sum_lev == "060":
        return name_field
    elif sum_lev == "080":
        return name_field
    elif sum_lev == "140":
        return name_field
    elif sum_lev == "150":
        return name_field
    else:
        return None

def get_name_sf1(line, sum_lev):
    """ Get the Census Name of this geo based on its sum lev"""
    name_field = line[226:316].strip()

    if sum_lev == "040":
        return name_field
    elif sum_lev =="050":
        return name_field
    elif sum_lev == "060":
        return name_field
    elif sum_lev == "080":
        return name_field
    elif sum_lev == "140":
        return name_field
    elif sum_lev == "150":
        return name_field
    else:
        return None

def get_name_acs2010(line, sum_lev):
    """ Get the Census Name of this geo based on its sum lev"""
    name_field = line[218:418].strip()

    if sum_lev == "040":
        return name_field
    elif sum_lev =="050":
        return name_field
    elif sum_lev == "060":
        return name_field
    elif sum_lev == "080":
        return name_field
    elif sum_lev == "140":
        return name_field
    elif sum_lev == "150":
        return name_field
    else:
        return None

def get_parent(line, source, sum_lev):
    """ Return the Geoid and sum_lev of the parent"""
    if sum_lev == "040":
        return None
    elif sum_lev =="050":
        parent_id = get_geoid(line, source, "040")
        return {'sumlev':"040", 'geoid':''.join(parent_id.values())}
    elif sum_lev == "060":
        parent_id = get_geoid(line, source, "050")
        return {'sumlev':"050", 'geoid':''.join(parent_id.values())}
    elif sum_lev == "140":
        parent_id = get_geoid(line, source, "060")
        return {'sumlev':"060", 'geoid':''.join(parent_id.values())}
    elif sum_lev == "150":
        parent_id = get_geoid(line, source, "140")
        return {'sumlev':"140", 'geoid':''.join(parent_id.values())}
    else:
        return None

def parse_file(file_path, source='2000', sum_levs=None):
    """
        Parse a single census geo file
        @param source is what type of data set it came from
    """
    if source not in SUPPORTED_DATASETS:
        raise ValueError('%s not a valid source. Valid sources are %s' % (source, ', '.join(SUPPORTED_DATASETS)))
    if sum_levs == None:
        sum_levs=('040', '050', '060', '140', '150')

    GEOS = {
        'name_index':{},
        'names':[],
    }

    # build out the resut of the GEOS sum_lev keys based on the sum levs
    for sl in sum_levs:
        GEOS[sl] = {}

    with open(file_path, 'r+') as f:
        for line in f:
            sum_lev = get_sum_lev(line, source)
            if sum_lev in sum_levs:
                logrecno = get_logrecno(line, source)
                name = get_name(line, source, sum_lev)
                geo_id_dict = get_geoid(line, source, sum_lev)
                geo_id_str = ''.join(geo_id_dict.values())
                parent = get_parent(line, source, sum_lev)
                if sum_lev and logrecno and name:
                    try:

                        GEOS[sum_lev][logrecno] = {'logrecno':logrecno, 'name':name,
                                'sum_lev':sum_lev, 'geoid': geo_id_str,
                                'geoid_dict':geo_id_dict ,'parent':parent}
                        if name:
                            GEOS['name_index'][name] = logrecno
                            GEOS['names'].append(name)
                    except KeyError:
                        # this may not be a sum lev we want
                        pass
    return GEOS

#---------------------------NOSE TESTS ---------------------------------------------------------------_#

def test_parse_file():
    from nose import tools
    import json
    file_path = os.path.join(os.path.dirname(__file__), 'sample_data/g20105pa.sample.txt')
    SUMMARY_LEVELS = ('040','050','060','140','150',)
    geos = parse_file(file_path, 'acs2010', SUMMARY_LEVELS)

    tools.assert_raises(ValueError, parse_file, '/', '8474j')
    assert get_sum_lev_names(SUMMARY_LEVELS) == ('County', 'State', 'Census Tract', 'Block Group', 'County Subdivision')

    assert geo_id_to_segments("42", "040") == {'040':'42'}
    assert geo_id_to_segments("42007", "050") == {'050': '007', '040': '42'}
    assert geo_id_to_segments("42007323616", "060") == {'060': '323616', '050': '007', '040': '42'}
    assert geo_id_to_segments("42003010300", "140") == {'050': '003', '140': '010300', '040': '42'}
    assert geo_id_to_segments("420035003001", "150") == {'150': '1', '050': '003', '140': '500300', '040': '42'}

