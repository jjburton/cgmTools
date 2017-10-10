"""
# ----------------------------------------------------------------------
# clex.py
#
# A lexer for ANSI C.
# ----------------------------------------------------------------------
"""

def t_VAR(t):
    """
    \$[A-Za-z_][\w_]*
    """

    pass


def t_COMPONENT(t):
    """
    \.[xyz]
    """

    pass


def t_CAPTURE(t):
    """
    `
    """

    pass


def t_RPAREN(t):
    """
    \)
    """

    pass


def t_LPAREN(t):
    """
    \(
    """

    pass


def t_ELLIPSIS(t):
    """
    \.\.
    """

    pass


def t_LBRACKET(t):
    """
    \[
    """

    pass


def t_ID(t):
    """
    ([|]?([:]?([.]?[A-Za-z_][\w]*)+)+)+?
    """

    pass


def t_RBRACKET(t):
    """
    \]
    """

    pass


def t_COMMENT(t):
    """
    //.*
    """

    pass


def t_COMMENT_BLOCK(t):
    """
    /\*(.|\n)*?\*/|/\*(.|\n)*?$
    """

    pass


def t_SEMI(t):
    """
    ;
    """

    pass


def t_NEWLINE(t):
    """
    \n+|\r+
    """

    pass



id_state = None

t_LVEC = '<<'

suspend_depth = 0

t_MINUSMINUS = '--'

t_NOT = '!'

t_EQ = '=='

tokens = ()

t_MINUSEQUAL = '-='

t_MINUS = '-'

t_FCONST = r'(((\d+\.)(\d+)?|(\d+)?(\.\d+))(e(\+|-)?(\d+))?|(\d+)e(\+|-)?(\d+))([lL]|[fF])?'

t_LT = '<'

t_PLUSPLUS = r'\+\+'

t_CROSS = r'\^'

t_LE = '<='

t_CONDOP = r'\?'

t_MOD = '%'

t_MODEQUAL = '%='

t_LOR = r'\|\|'

t_ICONST = r'(0x[a-fA-F0-9]*)|\d+'

reserved = ()

t_GE = '>='

t_ignore = ' \t\x0c'

t_COLON = ':'

t_CROSSEQUAL = '^='

r = 'YES'

t_GT = '>'

t_NE = '!='

t_TIMES = r'\*'

t_SCONST = r'"([^\\\n]|(\\.)|\\\n)*?"'

t_EQUALS = '='

t_TIMESEQUAL = r'\*='

t_COMMA = ','

t_DIVEQUAL = '/='

t_LAND = '&&'

t_PLUS = r'\+'

t_PLUSEQUAL = r'\+='

t_RBRACE = r'\}'

t_DIVIDE = '/'

reserved_map = {}

t_LBRACE = r'\{'

t_RVEC = '>>'


