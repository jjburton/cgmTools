"""
# ----------------------------------------------------------------------
# ctokens.py
#
# Token specifications for symbols in ANSI C and C++.  This file is
# meant to be used as a library in other tokenizers.
# ----------------------------------------------------------------------
"""

def t_COMMENT(t):
    """
    /\*(.|\n)*?\*/
    """

    pass


def t_CPPCOMMENT(t):
    """
    //.*\n
    """

    pass



t_AND = '&'

t_GE = '>='

t_RBRACE = r'\}'

t_FLOAT = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

t_OR = r'\|'

t_SEMI = ';'

t_LE = '<='

t_NE = '!='

t_TIMES = r'\*'

t_MINUSEQUAL = '-='

t_ELLIPSIS = r'\.\.\.'

t_NOT = '~'

t_MINUS = '-'

t_LBRACE = r'\{'

t_LAND = '&&'

t_MODEQUAL = '%='

t_LT = '<'

t_EQ = '=='

t_ARROW = '->'

t_INTEGER = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'

t_DECREMENT = '--'

t_MODULO = '%'

t_PLUS = r'\+'

t_OREQUAL = r'\|='

t_XOR = r'\^'

t_LSHIFTEQUAL = '<<='

t_COMMA = ','

t_TERNARY = r'\?'

t_LNOT = '!'

t_DIVEQUAL = '/='

t_RSHIFT = '>>'

t_TIMESEQUAL = r'\*='

t_LPAREN = r'\('

t_COLON = ':'

t_STRING = r'\"([^\\\n]|(\\.))*?\"'

t_LBRACKET = r'\['

t_RBRACKET = r'\]'

t_EQUALS = '='

t_PLUSEQUAL = r'\+='

t_CHARACTER = r"(L)?\'([^\\\n]|(\\.))*?\'"

t_INCREMENT = r'\+\+'

t_ANDEQUAL = '&='

t_RSHIFTEQUAL = '>>='

t_LSHIFT = '<<'

t_XOREQUAL = '^='

t_LOR = r'\|\|'

t_ID = '[A-Za-z_][A-Za-z0-9_]*'

t_DIVIDE = '/'

t_RPAREN = r'\)'

t_GT = '>'

tokens = []

t_PERIOD = r'\.'


