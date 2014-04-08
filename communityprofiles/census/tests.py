from decimal import Decimal

from django.test import TestCase

from census.meta import ACSMeta, CensusMeta, Census2010Meta
from census.datasources import Census2000, Census2010
from census.data import Value
from census.management.commands import load_census


class MockDatasource(object):
    def get_value(self, table, geo_dicts):
        return [0, ]


class ParsingTest(TestCase):
    def test_trivial_formula(self):
        from census.parse import FormulaParser
        parser = FormulaParser(MockDatasource())

        self.failUnlessEqual(
            'P0010001',
            parser.parse('P0010001').table
        )

        table = parser.parse('P0010001 + P0010002')
        self.failUnlessEqual(table.left.table, 'P0010001')
        self.failUnlessEqual(table.operation, '+')
        self.failUnlessEqual(table.right.table, 'P0010002')

    def test_operator_precedence(self):
        from census.parse import FormulaParser
        parser = FormulaParser(MockDatasource())

        self.failUnlessEqual(
            Value(7),
            parser.parse('1 + 2 * 3')(None)
        )
        self.failUnlessEqual(
            Value(9),
            parser.parse('(1 + 2) * 3')(None)
        )

    def test_operations(self):
        from census.parse import FormulaParser
        parser = FormulaParser(MockDatasource())

        self.failUnlessEqual(
            Value(4),
            parser.parse('2 + 2')(None)
        )
        self.failUnlessEqual(
            Value(0),
            parser.parse('2 - 2')(None)
        )
        self.failUnlessEqual(
            Value(6),
            parser.parse('2 * 3')(None)
        )
        self.failUnlessEqual(
            Value(2),
            parser.parse('4 / 2')(None)
        )

    def test_unicode(self):
        from census.parse import FormulaParser
        parser = FormulaParser(MockDatasource())
        table = parser.parse(u'P049013 + P049040\r\n')

        self.failUnlessEqual(
            'P049013',
            table.left.table
        )
        self.failUnlessEqual(
            'P049040',
            table.right.table
        )


class DataTest(TestCase):
    def test_moe_times_value(self):
        # test that if a number with an moe is multiplied by a normal non-estimate
        # number, the moe is simply multiplied but that number

        a = Value(10, moe=5)
        b = Value(2)
        self.failUnlessEqual(
            Value(20, moe=10),
            a * b
        )
        self.failUnlessEqual(
            Value(20, moe=10),
            b * a
        )

    def test_meta_files(self):
        acs_meta = ACSMeta()
        self.failUnlessEqual(acs_meta.csv_column_for_matrix('B07401_001'), 6)

        census_meta = CensusMeta('SF1')
        self.failUnlessEqual(census_meta.csv_column_for_matrix('P001001'), 5)

        census_meta = CensusMeta('SF3')
        self.failUnlessEqual(census_meta.csv_column_for_matrix('P021001'), 171)

        census_2010_sf1_meta = Census2010Meta('sf1')
        self.failUnlessEqual(census_2010_sf1_meta.csv_column_for_matrix('P0040002'), 14)

    def test_census2000_data(self):
        """ Test that the data files are read properly

        NOTE: It is advisable to download a locally cached copy of RI's files
        (the state these tests are written for) before running, so there are no
        network side-effects.
        """
        return
        # RI total population (2000)
        cmd = load_census.Command()
        cmd.handle('uSF1', 'ri')

        geo = {
            'FILEID': 'uSF1',
            'SUMLEV': '040',
            'STUSAB': 'RI',
            'CHARITER': '000',
            'CIFSN': '01',
            'LOGRECNO': '0000001'
        }

        c2k = Census2000('SF1')
        self.failUnlessEqual(c2k.data('P0001001', geo), Value(1048319))

    def test_census2010(self):
        """ Test that the data files are read properly, and that operations and
        formula are handled correctly.

        NOTE: It is advisable to download a locally cached copy of RI's files
        (the state these tests are written for) before running, so there are no
        network side-effects.
        """
        # RI total population (2010)
        cmd = load_census.Command()
        cmd.handle('SF1ST', 'ri')

        geo = {
            'FILEID': 'SF1ST',
            'SUMLEV': '040',
            'STUSAB': 'RI',
            'CHARITER': '000',
            'CIFSN': '01',
            'LOGRECNO': '0000001'
        }
        c2010sf1 = Census2010('sf1')
        self.failUnlessEqual(c2010sf1.data('P00010001', geo), Value(1052567))
        self.failUnlessEqual(c2010sf1.data('P00060001', geo), Value(1091043))
        self.failUnlessEqual(c2010sf1.data('P00010001-P00060001', geo), Value(1052567 - 1091043))
        self.failUnlessEqual(str(c2010sf1.data('P00010001/P00060001', geo).value), str(Decimal(1052567) / Decimal(1091043)))

    def test_ratio_moe(self):
        """ Test that MOE is calculated properly for ratios/proportions """
        v1 = Value(4634, moe=989)
        v2 = Value(6440, moe=1328)
        result = v1 / v2

        # http://www.census.gov/acs/www/Downloads/handbooks/ACSResearch.pdf
        # page A-16
        self.failUnlessEqual(round(result.value, 2), 0.72)
        self.failUnlessEqual(round(result.moe, 4), 0.2135)
