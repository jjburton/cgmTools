from pymel.mayautils import getMayaAppDir

class ValueLex:
    """
    second level lexer to parse right-values depending on os name
    """
    
    
    
    def __init__(self, symbols, osname='posix'):
        pass
    
    
    def build(self, **kwargs):
        pass
    
    
    def t_PATHSEP(self, t):
        """
        \/|\\
        """
    
        pass
    
    
    def t_RVAR1(self, t):
        """
        \$[^\\^/^:^*^"^<^>^|^=^ ^\t^\n^#^$]+
        """
    
        pass
    
    
    def t_RVAR2(self, t):
        """
        \%[^\\^/^:^*^"^<^>^|^=^ ^\t^\n^#]+\%
        """
    
        pass
    
    
    def t_SEP(self, t):
        """
        :;
        """
    
        pass
    
    
    def t_VALUE(self, t):
        """
        [^=^\n^#^$]+
        """
    
        pass
    
    
    def t_error(self, t):
        pass
    
    
    def test(self, data):
        """
        # Test it
        """
    
        pass
    
    
    Warn = None
    
    
    t_ignore = '^[ \t]+'
    
    
    tokens = ()


class EnvLex:
    """
    ply.lex lexer class to parse Maya.env file
    """
    
    
    
    def __init__(self):
        pass
    
    
    def build(self, **kwargs):
        pass
    
    
    def t_ANY_error(self, t):
        pass
    
    
    def t_ANY_newline(self, t):
        """
        [ \t]*\n+
        """
    
        pass
    
    
    def t_INITIAL_error(self, t):
        pass
    
    
    def t_VAR(self, t):
        """
        [^\\^\/^\:^\*^\"^\<^\>^\|^=^ ^\t^\n^#]+
        """
    
        pass
    
    
    def t_end_ASSIGN(self, t):
        """
        [ \t]*=[ \t]*
        """
    
        pass
    
    
    def t_end_VALUE(self, t):
        """
        [^=^\n^#]+
        """
    
        pass
    
    
    def t_left_ASSIGN(self, t):
        """
        [ \t]*=[ \t]*
        """
    
        pass
    
    
    def t_left_error(self, t):
        pass
    
    
    def t_right_ASSIGN(self, t):
        """
        [ \t]*=[ \t]*
        """
    
        pass
    
    
    def t_right_VALUE(self, t):
        """
        [^=^\n^#]+
        """
    
        pass
    
    
    def t_right_error(self, t):
        pass
    
    
    def test(self, data):
        """
        # Test it
        """
    
        pass
    
    
    t_ANY_ignore_COMMENT = r'\#[^\n]*'
    
    
    t_INITIAL_ignore = '^[ \t]+'
    
    
    t_cancel_ignore = '[^\n]+'
    
    
    t_end_ignore = '[ \t]+$'
    
    
    t_left_ignore = '[ \t]+'
    
    
    t_right_ignore = '[ \t]+'
    
    
    tokens = ()



def parseMayaenv(envLocation=None, version=None):
    """
    parse the Maya.env file and set the environement variablas and python path accordingly.
    You can specify a location for the Maya.env file or the Maya version
    """

    pass


def parse(text, environ={'PROXY_FOR': 'os.environ'}, osname='posix'):
    """
    # Do the 2 level parse of a Maya.env format text and return a symbol table of the declared env vars
    """

    pass



_logger = None


