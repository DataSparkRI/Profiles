from pyparsing import Word, oneOf, operatorPrecedence,\
        opAssoc, printables, nums, alphanums, Optional,\
        OneOrMore, alphas, Combine, Literal, CaselessLiteral,\
        Group, ZeroOrMore, Forward

from decimal import Decimal
from census.data import Table, Value

import math
import operator

class IdentityDatasource(object):
    """ A data source that always returns the table argument """
    def get_value(self, table, geo_dicts):
        return [table, ]


class FormulaParser(object):
    op_map = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
    }

    def __init__(self, datasource):
        self.datasource = datasource

    def _number_parse_action(self, result):
        number = Value(result[0])
        return Table(IdentityDatasource(), number)

    def _table_parse_action(self, result):
        return Table(self.datasource, result[0])

    def grammar(self, tabilify=True):
        number = Combine(Word(nums) + Optional("." + OneOrMore(Word(nums))))
        table = Combine(Word(alphas) + OneOrMore(Word("_"+alphanums)))
        if tabilify:
            number.setParseAction(self._number_parse_action)
            table.setParseAction(self._table_parse_action)

        signop = oneOf('+ -')
        multop = oneOf('* /')
        plusop = oneOf('+ -')

        operand = number | table

        return operatorPrecedence(operand, [
            (signop, 1, opAssoc.RIGHT),
            (multop, 2, opAssoc.LEFT),
            (plusop, 2, opAssoc.LEFT)
        ])

    def tokens(self, formula, tabilify=True):
        """ @param tabilify = Return this in the old table format?"""
        try:
           return self.grammar(tabilify).parseString(formula)
        except:
           return None

    def _df_parse(self, parse_result,**kwargs):

        if type(parse_result) in (Table, Decimal, str):
            return parse_result

        output = None
        pending_op = None
        for expr in parse_result:
            expr = self._df_parse(expr)
            if type(expr) is str:
                pending_op = expr

            if type(expr) is Table:
                if output is None:
                    output = expr
                else:
                    output = self.op_map[pending_op](output, expr)
        return output

    def parse(self, formula, **kwargs):
        formula = str(formula)  # unicode isn't (currently) supported for formula
        return self._df_parse(self.tokens(str(formula))[0],**kwargs)


class AltFormulaParser:
    """ An alternate simplified formula parser. Used in Census API DataAdapter"""
    # map operator symbols to corresponding arithmetic operations
    epsilon = 1e-12

    opn = { "+" : operator.add,
            "-" : operator.sub,
            "*" : operator.mul,
            "/" : operator.truediv,
            "^" : operator.pow }
    fn  = { "sin" : math.sin,
            "cos" : math.cos,
            "tan" : math.tan,
            "abs" : abs,
            "trunc" : lambda a: int(a),
            "round" : round,
            "sgn" : lambda a: abs(a)>epsilon and cmp(a,0) or 0}

    def __init__(self):
        self.expr_stack = []
        self.bnf = None
        epsilon = 1e-12

        self.opn = { "+" : operator.add,
                "-" : operator.sub,
                "*" : operator.mul,
                "/" : operator.truediv,
                "^" : operator.pow }
        self.fn  = { "sin" : math.sin,
                "cos" : math.cos,
                "tan" : math.tan,
                "abs" : abs,
                "trunc" : lambda a: int(a),
                "round" : round,
                "sgn" : lambda a: abs(a)>epsilon and cmp(a,0) or 0}

    def push_first(self, strg, loc, toks ):
        self.expr_stack.append( toks[0] )

    def push_uminus(self, strg, loc, toks ):
        if toks and toks[0]=='-':
            self.expr_stack.append( 'unary -' )

    def BNF(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        if not self.bnf:
            point = Literal( "." )
            uscore = Literal("_")

            #e     = CaselessLiteral( "E" )
            fnumber = Combine( Word( "+-"+alphanums, alphanums ) +
                            Optional(point + Optional(Word(alphanums))) +
                            Optional(Word( "+-" + alphanums,alphanums)) +
                            #Optional(e + Word( "+-" + alphanums,alphanums)) +
                            Optional(uscore + Optional(Word(alphanums)))
                            )
            ident = Word(alphas, alphas+nums+"_$")

            plus  = Literal( "+" )
            minus = Literal( "-" )
            mult  = Literal( "*" )
            div   = Literal( "/" )
            lpar  = Literal( "(" ).suppress()
            rpar  = Literal( ")" ).suppress()
            addop  = plus | minus
            multop = mult | div
            expop = Literal( "^" )
            pi    = CaselessLiteral( "PI" )
            expr = Forward()
            atom = (Optional("-") + ( pi | fnumber | ident + lpar + expr + rpar ).setParseAction( self.push_first ) | ( lpar + expr.suppress() + rpar )).setParseAction(self.push_uminus) # unlock E
            #atom = (Optional("-") + ( pi | e | fnumber | ident + lpar + expr + rpar ).setParseAction( self.push_first ) | ( lpar + expr.suppress() + rpar )).setParseAction(self.push_uminus)

            # by defining exponentiation as "atom [ ^ factor ]..." instead of "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-righ
            # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
            factor = Forward()
            factor << atom + ZeroOrMore( ( expop + factor ).setParseAction( self.push_first ) )

            term = factor + ZeroOrMore( ( multop + factor ).setParseAction( self.push_first ) )
            expr << term + ZeroOrMore( ( addop + term ).setParseAction( self.push_first ) )
            bnf = expr
        return bnf

    def parse_string(self, s):
        """ Parse a string into its parts, this returns a PyParsing Result"""
        return self.BNF().parseString(s)

    def evaluate_stack(self):
        s = self.expr_stack[:]
        op = s.pop()
        if op == 'unary -':
            return -self.evaluate_stack()
        if op in "+-*/^":
            op2 = self.evaluate_stack()
            op1 = self.evaluate_stack()
            return opn[op](op1,op2)
        elif op == "PI":
            return math.pi # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op in fn:
            return fn[op](self.evaluate_stack())
        elif op[0].isalpha():
            return 0
        else:
            return float( op )



