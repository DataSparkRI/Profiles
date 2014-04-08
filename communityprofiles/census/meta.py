import csv
import os

class BaseMeta(object):
    def _meta_reader(self):
        return csv.DictReader(open(self._meta_file(), 'r'), dialect='excel-tab')

    def _state_name(self, abbr):
        from django.contrib.localflavor.us.us_states import STATES_NORMALIZED, US_STATES
        return filter(lambda s: s[0] == abbr.upper(), US_STATES)[0][1]

    def _file_name_for_matrix(self, matrix_number):
        return self._meta_for_matrix(matrix_number)['File Name']

    def _meta_for_file(self, file_name):
        return [row for row in self._meta_reader()
            if row['File Name'] == file_name]
   
    def _meta_for_matrix(self, matrix_number):
        matrix, cell = self._parse_table(matrix_number)
        this_file_meta = [row for row in self._meta_reader()
            if row['Matrix Number'] == matrix]
        if len(this_file_meta) != 1:
            raise ValueError('Table %s could not be resolved' % (matrix_number, ))

        return this_file_meta[0]

    def _parse_table(self, matrix_number):
        """ Splits a combined table+cell into parts.

        Expects input in the form XXXXYYY or XXXXXYYY. The cell (YYY) must 
        be three digits.

        Table transformation ignores insignificant zeros. For example:

        P001 --> 'P1'
        P010 --> 'P10'
        PCT017C --> 'PCT17C
        """
        # seperate XXXXYYY into XXXX and YYY, taking into account a variable
        # number table digits (XXXX). Cell size is fixed, for the data source
        table_size = len(matrix_number) - self.cell_digits
        table = matrix_number[0:table_size]
        col_number = int(matrix_number[table_size:])
        
        digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',]
        in_first_transition = False
        table_id = ''
        last = None

        for c in table:
            # catch the first transition from chars -> '0' and start ignoring
            if c == '0' and not last in digits and not in_first_transition:
                in_first_transition = True
            if c != '0' and in_first_transition:
                in_first_transition = False

            if in_first_transition and c == '0':
                last = c
                continue
            
            table_id += c
            last = c
        
        for meta_row in self._meta_reader():
            if table_id == meta_row['Matrix Number']:
                if col_number > 0 and col_number <= int(meta_row['Cell Count']):
                    return (table_id, "%03d" % col_number)
        raise ValueError("The matrix or cell number %s could not be found" % matrix_number)

    def csv_column_for_matrix(self, matrix_number):
        matrix, cell = self._parse_table(matrix_number)
        matrices_meta = self._meta_for_file(self._file_name_for_matrix(matrix_number))

        offset = self.data_cell_offset
        
        for meta in matrices_meta:
            if meta['Matrix Number'] != matrix:
                offset += int(meta['Cell Count'])
            else:
                break
        return offset + int(cell)


class ACSMeta(BaseMeta):
    data_cell_offset = 5
    cell_digits = 3

    def __init__(self, data_table_matrix_file, year_prfx):

        """ data_table_matrix_file : something that looks like https://github.com/ProvidencePlan/Community-Profiles/blob/amedrano/communityprofiles/census/ACS_2006_2010.txt
            year_prfx = '2009'
        """
        self.data_table_matrix_file = data_table_matrix_file
        self.year_prefix = year_prfx
        super(ACSMeta, self).__init__()

    def _meta_file(self):
        return os.path.join(os.path.dirname(__file__),self.data_table_matrix_file)


    def _parse_table(self, matrix):
        """ Expects input in the form XXXXX_YYY

            The table number should be 6-9 digits, and match the "Matrix Number"
            field in ACS_2005-2009.txt
        """
        matrix, cell =  self._parse_table_from_matrix(matrix)

        cell = int(cell)

        for meta_row in self._meta_reader():
            if matrix == meta_row['Matrix Number']:
                if cell > 0 and cell <= int(meta_row['Cell Count']):
                    return (matrix, "%03d" % cell)

        raise ValueError("The matrix or cell number %s could not be found" % matrix)


    def _parse_table_from_matrix(self, matrix_number):
        """ Splits a combined table+cell into parts.

        Expects input in the form XXXXYYY or XXXXXYYY. The cell (YYY) must 
        be three digits.

        THIS IS A PATCH! -AM
        """
        # seperate XXXXYYY into XXXX and YYY, taking into account a variable
        # number table digits (XXXX). Cell size is fixed, for the data source
        table_size = len(matrix_number) - self.cell_digits
        table = matrix_number[0:table_size]
        col_number = int(matrix_number[table_size:])
        
        return (table, col_number)
        

    def _meta_for_matrix(self, matrix_number):
        PR_only_files = [
            '0108',
            '0109',
            '0110',
            '0111',
            '0112',
            '0113',
            '0114',
            '0115',
            '0116',
            '0117',
            ]
        matrix, cell = self._parse_table(matrix_number)

        this_file_meta = [row for row in self._meta_reader()
                          if row['Matrix Number'] == matrix and row['File Name'] not in PR_only_files]
        if len(this_file_meta) != 1:
            raise ValueError('Table %s could not be resolved' % matrix_number)

        return this_file_meta[0]

    def _geo_dir_part(self, sumlevel):
        "The data file directory depends on the summary level"
        if sumlevel in ('140', '150', ):
            return 'Tracts_Block_Groups_Only'
        else:
            return 'All_Geographies_Not_Tracts_Block_Groups'

    def _full_file_for_matrix(self, matrix_number, state_abbr):
        return '%s5%s%s000.txt' % (
            self.year_prefix,
            state_abbr.lower(),
            self._file_name_for_matrix(matrix_number),
            )


    def file_names_for_matrix(self, matrix_number, state_abbr, sumlevel):
        base_file_name = self._full_file_for_matrix(matrix_number, state_abbr)
        return ('e' + base_file_name, 'm' + base_file_name, )

    def zip_path_for_matrix(self, matrix_number, state_abbr, sumlevel):
        import os
        state_name = self._state_name(state_abbr)

        zip_path = os.path.join(
            state_name.replace(' ', ''),
            self._geo_dir_part(sumlevel),
            "%s5%s%s000.zip" % (self.year_prefix,state_abbr.lower(), self._file_name_for_matrix(matrix_number), )
        )
        return zip_path


class ACS2010Meta(ACSMeta):
    def __init__(self):
        super(ACS2010Meta, self).__init__("ACS_2006_2010.txt","2010")

     
class CensusMeta(BaseMeta):
    data_cell_offset = 4
    cell_digits = 3
    
    def __init__(self, summary_file):
        if summary_file not in ['SF1', 'SF3']:
            raise ValueError('%s is not a supported summary file.' % summary_file)
        self.summary_file = summary_file

    def _meta_file(self):
        return os.path.join(os.path.dirname(__file__),'%s.txt' % self.summary_file) 
    

    def file_path_for_matrix(self, matrix_number, state_abbr, sumlevel):
        import os
        state_name = self._state_name(state_abbr)
        return os.path.join(
            "Summary_File_%s" % self.summary_file[2],
            state_name.replace(' ', '_'),
            self._full_file_for_matrix(matrix_number, state_abbr)
        )

class Census2010Meta(BaseMeta):
    data_cell_offset = 4
    cell_digits = 4

    def __init__(self, file_type):
        self.file_type = file_type
        if not self.file_type in ['pl', 'sf1']:
            raise ValueError('%s is not a recognized 2010 file type' % file_type)

    def _meta_file(self):
        return os.path.join(os.path.dirname(__file__),'2010_%s.txt' % self.file_type.upper()) 
    
    def zip_file_path_for_matrix(self, matrix_number, state_abbr):
        """ PL data is always in a single zip file """
        import os
        state_name = self._state_name(state_abbr)
        return os.path.join(
            state_name.replace(' ', '_'),
            "%s2010.%s.zip" % (state_abbr.lower(), self.file_type)
        )
    
    def file_name_for_matrix(self, matrix_number, state_abbr):
        return "%s000%s2010.%s" % (
            state_abbr.lower(),
            self._meta_for_matrix(matrix_number)['File Name'],
            self.file_type
        )
