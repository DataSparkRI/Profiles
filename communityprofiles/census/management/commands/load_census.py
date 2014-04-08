import os
from zipfile import ZipFile

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.contrib.localflavor.us.us_states import STATES_NORMALIZED, US_STATES

from census.models import Row
from census.remote_file import RemoteFileObject

def state_abbr_to_name(state_abbr):
    return filter(lambda s: s[0] == state_abbr.upper(), US_STATES)[0][1]

def remote_fallback_reader(local_base_path, remote_base_url, file_path):
    """ Attempt to read the file locally, but grab from `remote_base_url` if it
    doesn't exist.
    """
    local_path = os.path.join(local_base_path, file_path)
    if os.path.isfile(local_path):
        print 'found file locally'
        return open(local_path, 'r')
    print 'need to fetch file'
    return RemoteFileObject('/'.join([remote_base_url, file_path]))


class Command(BaseCommand):
    args = '[filetype state_abbr]'
    help = 'Loads the records the given file type (cd .., PLST, uSF1, uSF3) and state abbreviation into the database'

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('Please enter a file type and state abbreviation')
        
        filetype = args[0]
        if filetype not in ['ACSSF', 'PLST', 'uSF1', 'uSF3', 'SF1ST']:
            raise CommandError("'%s' is not a valid file type (ACSSF, PLST, uSF1, uSF3, SF1ST)" % filetype)
        state_abbr = args[1].lower()
        try:
            state_name = filter(lambda s: s[0] == state_abbr.upper(), US_STATES)[0][1]
        except IndexError:
            raise CommandError("'%s' is not a valid state abbreviation" % state_abbr)

        cursor = connection.cursor()

        # test, load all the files for the given state abbreviation
        stusab = state_abbr.upper()
        if filetype == 'ACSSF':
            stusab = state_abbr.lower()
        cursor.execute("DELETE FROM %s WHERE stusab = '%s' and fileid = '%s'" % (
            Row._meta.db_table, stusab, filetype))
        

        def census2000(summary_file_num, filenum):
            base_url = 'http://www2.census.gov/census_2000/datasets/'
            path = os.path.join( 
                'Summary_File_%s' % summary_file_num, state_name.replace(' ', '_'), 
                '%s000%02d_uf%s.zip' % (state_abbr, filenum, summary_file_num)
            )
            reader = remote_fallback_reader(
                '../data/census_2000/datasets',
                base_url,
                path
            )
            
            z = ZipFile(reader)
            n = z.namelist()
            z.extract(n[0], '/tmp/')
            
            filename = '/tmp/%s000%02d.uf%s' % (state_abbr, filenum, summary_file_num)

            # count the number of columns, to determine how many columns to fill
            firstline = open(filename).readline()
            cols = ['fileid', 'stusab', 'chariter', 'cifsn', 'logrecno']
            cols.extend(map(
                lambda c: 'col%s' % str(c+1),
                range(firstline.count(',')+1-5) # subtract 5 to account for the 5 geo header columns
            ))
            cursor.copy_from(open(filename), 'census_row', sep=',',
                columns=cols)
            os.unlink(filename)

        def acs(file_num, geo_type_dir):
            base_url = 'http://www2.census.gov/acs2010_5yr/summaryfile/2006-2010_ACSSF_By_State_By_Sequence_Table_Subset/'
            path = os.path.join(
                state_name.replace(' ', ''), geo_type_dir,
                '20105%s%04d000.zip' % (state_abbr, file_num)
            )
            reader = remote_fallback_reader(
                '../data/acs2006_2010_5yr/summaryfile/2006-2010_ACSSF_By_State_By_Sequence_Table_Subset',
                base_url,
                path
            )

            z = ZipFile(reader)
            n = z.namelist()
            z.extractall('/tmp/')
            files = ['e20105%s%04d000.txt' % (state_abbr, file_num),
                'm20105%s%04d000.txt' % (state_abbr, file_num),]
            for f in files:
                z.extract(f, '/tmp/')

                # count the number of columns, to determine how many columns to fill
                firstline = open('/tmp/' + f).readline()
                if not firstline:
                    # some files are empty, so just continue to the next
                    os.unlink('/tmp/' + f)
                    continue
                cols = ['fileid', 'filetype', 'stusab', 'chariter', 'cifsn', 'logrecno']
                cols.extend(map(
                    lambda c: 'col%s' % str(c+1),
                    range(firstline.count(',')+1-6) # subtract 6 to account for the 6 geo header columns
                ))
                cursor.copy_from(open('/tmp/%s' % f), 'census_row', sep=',',
                    columns=cols)
                os.unlink('/tmp/' + f)

        def census2010PL():
            base_url = 'http://www2.census.gov/census_2010/01-Redistricting_File--PL_94-171/'
            path = os.path.join(
                state_name.replace(' ', '_'),
                '%s2010.pl.zip' % state_abbr
            )
            reader = remote_fallback_reader(
                '../data/census_2010/01-Redistricting_File--PL_94-171',
                base_url,
                path
            )

            z = ZipFile(reader)
            for f in ['%s000012010.pl' % state_abbr, '%s000022010.pl' % state_abbr]:
                z.extract(f, '/tmp/')
                firstline = open('/tmp/' + f).readline()
                cols = ['fileid', 'stusab', 'chariter', 'cifsn', 'logrecno']
                cols.extend(map(lambda c: 'col%s' % str(c+1), range(firstline.count(',')+1-5)))
                cursor.copy_from(open('/tmp/%s' % f), 'census_row', sep=',',
                    columns=cols)
                os.unlink('/tmp/' + f)
            return

        def census2010SF(SF_num):
            base_url = 'http://www2.census.gov/census_2010/'
            path = os.path.join( 
                '04-Summary_File_%s' % SF_num, state_name.replace(' ', '_'), 
                '%s2010.sf1.zip' % state_abbr
            )
            reader = remote_fallback_reader(
			    '../data/census_2010', 
				base_url, 
				path
			)
			
            z = ZipFile(reader)
            for file_num in range(47):
                file_name = '%s000%02d2010.sf%s' % (state_abbr, file_num+1, SF_num)
                z.extract(file_name, '/tmp/')
                
                firstline = open('/tmp/' + file_name).readline()
                cols = ['fileid', 'stusab', 'chariter', 'cifsn', 'logrecno']
                cols.extend(map(lambda c: 'col%s' % str(c+1), range(firstline.count(',')+1-5)))
                cursor.copy_from(open('/tmp/%s' % file_name), 'census_row', sep=',', columns=cols)
                os.unlink('/tmp/' + file_name)
					
        # Census 2000 SF1
        if filetype == 'uSF1':
            for file_num in range(39):
                census2000(1, file_num+1)

        # Census 2000 SF3
        if filetype == 'uSF3':
            for file_num in range(76):
                census2000(3, file_num+1)
        
        # 2010 ACS 5 year estimate
        if filetype == 'ACSSF':
            for file_num in range(118):
                print "Reading File: " + str(file_num)
                acs(file_num+1, 'Tracts_Block_Groups_Only')
                acs(file_num+1, 'All_Geographies_Not_Tracts_Block_Groups')

        # Census 2010 PL
        if filetype == 'PLST':
            census2010PL()
			
		# Census 2010 SF1
        if filetype == 'SF1ST':
            census2010SF(1)
