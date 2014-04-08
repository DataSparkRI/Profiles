import math
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO: do the moe by adding all component MOEs instead of doing them at addition/subtraction
class Value(object):
    """ Represents a value from any Census data source.

    MOE, if applicable, is tracked automatically.
    """
    def __init__(self, value, moe=None):
        self._value = None
        self._moe = None
        if value is not None:
            self._value = Decimal(str(value))
        if moe is not None:
            self._moe = Decimal(str(moe))

    def _calc_moe(self, other, operation, result_value=None):
        if self._value is None:
            return None
        moe = None
        moe_funcs = {
            '+': lambda a, b: math.sqrt(a._moe ** 2 + b._moe ** 2),
            '-': lambda a, b: math.sqrt(a._moe ** 2 + b._moe ** 2),
            '*': lambda a, b: math.sqrt(a._value ** 2 * b._moe ** 2 + b._value ** 2 * a._moe ** 2),
            '/': lambda a, b, div_result: Decimal(str(math.sqrt(a._moe ** 2 + (div_result ** 2 * b._moe ** 2)))) / b._value
        }
        if self._moe is None and other._moe is not None:  # this number has no moe, and the other does
            moe = other._moe * self._value
        elif self._moe is not None and other._moe is None:  # other number has no moe, and this one does
            moe = self._moe * other._value
        elif self._moe is not None and other._moe is not None:
            args = [self, other]
            if operation == '/':
                args.append(result_value)
            moe = moe_funcs[operation](*args)
        return moe

    def __add__(self, other):
        if self._value is None and other._value is None:
            return Value(None)

        return Value((self._value or 0) + (other._value or 0), moe=self._calc_moe(other, '+'))

    def __sub__(self, other):
        if self._value is None and other._value is None:
            return Value(None)

        return Value(
            (self._value or 0) - (other._value or 0),
            moe=self._calc_moe(other, '-')
        )

    def __div__(self, other):
        # self is numerator
        # http://www.census.gov/acs/www/Downloads/handbooks/ACSResearch.pdf page A-15

        if self._value is None and other._value is None:
            return Value(None)

        div_result = float(self._value) / float(other._value)
        #print self._value,"/",other._value, div_result, "<------div_result"
        return Value(div_result, moe=self._calc_moe(other, '/', result_value=int(div_result)))

    def __mul__(self, other):
        # http://www.census.gov/acs/www/Downloads/handbooks/ACSResearch.pdf page A-16
        if self._value is None and other._value is None:
            return Value(None)

        mul_result = self._value * other._value

        return Value(mul_result, moe=self._calc_moe(other, '*'))

    def __repr__(self):
        if not self.moe:
            return str(self.value)
        else:
            return "%s (+/- %s)" % (self.value, self.moe)

    def __cmp__(self, other):
        if self.value < other.value:
            return -1
        if self.value > other.value:
            return 1
        if self.moe != other.moe:
            return 1
        return 0

    def __str__(self):
        if not self.moe:
            return str(self.value)
        else:
            return "%s (+/- %s)" % (self.value, self.moe)

    # TODO: is this the correct place to handle rounding?
    @property
    def moe(self):
        if self._moe is None:
            return None

        return self._moe

    @property
    def value(self):
        if self._value is None:
            return None

        return self._value


class Table(object):
    """ A 'logical' table representing a value from a Census datasource.

    This may represent a Census table directly, or some combination of tables.
    """
    def __init__(self, datasource, table=None, left=None, right=None, operation=None):
        self.datasource = datasource
        self.table = table
        self.left = left
        self.right = right
        self.operation = operation

    def __add__(self, other):
        if not type(other.datasource) == type(self.datasource):
            return ValueError
        return Table(datasource=self.datasource, left=self, right=other, operation='+')

    def __sub__(self, other):
        if not type(other.datasource) == type(self.datasource):
            return ValueError
        return Table(datasource=self.datasource, left=self, right=other, operation='-')

    def __div__(self, other):
        if not type(other.datasource) == type(self.datasource):
            return ValueError
        return Table(datasource=self.datasource, left=self, right=other, operation='/')

    def __mul__(self, other):
        if not type(other.datasource) == type(self.datasource):
            return ValueError
        return Table(datasource=self.datasource, left=self, right=other, operation='*')

    def __call__(self, geo, use_cache=False, **kwargs):
        """ Return a value or values for the given geo or geos

        `geo` should be a dict containing
                STUSAB
                SUMLEV
                LOGRECNO
        """
        #print "Table.__call__: %s, %s, %s, %s, %s, %s" % (self.datasource, self.table, self.left, self.right, self.operation, geo)

        if self.operation:
            left_result = self.left(geo)
            right_result = self.right(geo)
            result = self._apply_operator(left_result, right_result, self.operation)
        else:
            # this is an only child or a leaf child
            # reduce the results, as get_value should return a list (necessary
            # when geo is a list of component geos)
            result = self.datasource.get_value(self.table, geo, **kwargs)
            if len(result) == 0:
                return None
            result = reduce(lambda l, r: l + r, result)

        return result

    def _apply_operator(self, left_val, right_val, operator):
        if left_val is None or right_val is None:
            # TODO: is this the best way? it may be difficult to debug, if only half is none
            return None
        if operator == '+':
            return left_val + right_val
        if operator == '-':
            return left_val - right_val
        if operator == '/':
            return left_val / right_val
        if operator == '*':
            return left_val * right_val
        return None


    @property
    def name(self):
        if self.table:
            return unicode(self.table)
        else:
            return u"%s %s %s" % (self.left.name, self.operation, self.right.name)


