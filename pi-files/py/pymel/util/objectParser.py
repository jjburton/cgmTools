import exceptions

"""
.. dotgraph::

    main -> parse -> execute;
    main -> init;
    main -> cleanup;
    execute -> make_string;
    execute -> printf
    init -> make_string;
    main -> printf;
    execute -> compare;
"""

from pymel.util.arguments import *
from pymel.util.utilitytypes import *

from pymel.util.common import uncapitalize
from pymel.util.common import capitalize

class Parser(object):
    """
    Abstract Base class for all name parsers
    """
    
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def build(self, **kwargs):
        pass
    
    
    def p_error(self, p):
        pass
    
    
    def parse(self, data, **kwargs):
        pass
    
    
    def t_error(self, t):
        pass
    
    
    def __new__(cls, *args, **kwargs):
        pass
    
    
    def getRulesAndTokens(parsercls):
        """
        build the tokens and precedence tuples from inherited declarations.
        gather tokens and rules definition from Parser class members (own and inherited)
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    classes = {}


class ProxyUni(object):
    def __add__(self, *args, **kwargs):
        """
        x.__add__(y) <==> x+y
        """
    
        pass
    
    
    def __contains__(self, *args, **kwargs):
        """
        x.__contains__(y) <==> y in x
        """
    
        pass
    
    
    def __delattr__(self, *args, **kwargs):
        """
        x.__delattr__('name') <==> del x.name
        """
    
        pass
    
    
    def __eq__(self, *args, **kwargs):
        """
        x.__eq__(y) <==> x==y
        """
    
        pass
    
    
    def __format__(self, *args, **kwargs):
        """
        S.__format__(format_spec) -> unicode
        
        Return a formatted version of S as described by format_spec.
        """
    
        pass
    
    
    def __ge__(self, *args, **kwargs):
        """
        x.__ge__(y) <==> x>=y
        """
    
        pass
    
    
    def __getnewargs__(self, *args, **kwargs):
        """
        # print method
        #@functools.wraps(f)
        """
    
        pass
    
    
    def __getslice__(self, *args, **kwargs):
        """
        x.__getslice__(i, j) <==> x[i:j]
        
        Use of negative indices is not supported.
        """
    
        pass
    
    
    def __gt__(self, *args, **kwargs):
        """
        x.__gt__(y) <==> x>y
        """
    
        pass
    
    
    def __hash__(self, *args, **kwargs):
        """
        x.__hash__() <==> hash(x)
        """
    
        pass
    
    
    def __le__(self, *args, **kwargs):
        """
        x.__le__(y) <==> x<=y
        """
    
        pass
    
    
    def __len__(self, *args, **kwargs):
        """
        x.__len__() <==> len(x)
        """
    
        pass
    
    
    def __lt__(self, *args, **kwargs):
        """
        x.__lt__(y) <==> x<y
        """
    
        pass
    
    
    def __mod__(self, *args, **kwargs):
        """
        x.__mod__(y) <==> x%y
        """
    
        pass
    
    
    def __mul__(self, *args, **kwargs):
        """
        x.__mul__(n) <==> x*n
        """
    
        pass
    
    
    def __ne__(self, *args, **kwargs):
        """
        x.__ne__(y) <==> x!=y
        """
    
        pass
    
    
    def __repr__(self, *args, **kwargs):
        """
        x.__repr__() <==> repr(x)
        """
    
        pass
    
    
    def __rmod__(self, *args, **kwargs):
        """
        x.__rmod__(y) <==> y%x
        """
    
        pass
    
    
    def __rmul__(self, *args, **kwargs):
        """
        x.__rmul__(n) <==> n*x
        """
    
        pass
    
    
    def __str__(self, *args, **kwargs):
        """
        x.__str__() <==> str(x)
        """
    
        pass
    
    
    def capitalize(self, *args, **kwargs):
        """
        S.capitalize() -> unicode
        
        Return a capitalized version of S, i.e. make the first character
        have upper case and the rest lower case.
        """
    
        pass
    
    
    def center(self, *args, **kwargs):
        """
        S.center(width[, fillchar]) -> unicode
        
        Return S centered in a Unicode string of length width. Padding is
        done using the specified fill character (default is a space)
        """
    
        pass
    
    
    def count(self, *args, **kwargs):
        """
        S.count(sub[, start[, end]]) -> int
        
        Return the number of non-overlapping occurrences of substring sub in
        Unicode string S[start:end].  Optional arguments start and end are
        interpreted as in slice notation.
        """
    
        pass
    
    
    def decode(self, *args, **kwargs):
        """
        S.decode([encoding[,errors]]) -> string or unicode
        
        Decodes S using the codec registered for encoding. encoding defaults
        to the default encoding. errors may be given to set a different error
        handling scheme. Default is 'strict' meaning that encoding errors raise
        a UnicodeDecodeError. Other possible values are 'ignore' and 'replace'
        as well as any other name registered with codecs.register_error that is
        able to handle UnicodeDecodeErrors.
        """
    
        pass
    
    
    def encode(self, *args, **kwargs):
        """
        S.encode([encoding[,errors]]) -> string or unicode
        
        Encodes S using the codec registered for encoding. encoding defaults
        to the default encoding. errors may be given to set a different error
        handling scheme. Default is 'strict' meaning that encoding errors raise
        a UnicodeEncodeError. Other possible values are 'ignore', 'replace' and
        'xmlcharrefreplace' as well as any other name registered with
        codecs.register_error that can handle UnicodeEncodeErrors.
        """
    
        pass
    
    
    def endswith(self, *args, **kwargs):
        """
        S.endswith(suffix[, start[, end]]) -> bool
        
        Return True if S ends with the specified suffix, False otherwise.
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        suffix can also be a tuple of strings to try.
        """
    
        pass
    
    
    def expandtabs(self, *args, **kwargs):
        """
        S.expandtabs([tabsize]) -> unicode
        
        Return a copy of S where all tab characters are expanded using spaces.
        If tabsize is not given, a tab size of 8 characters is assumed.
        """
    
        pass
    
    
    def find(self, *args, **kwargs):
        """
        S.find(sub [,start [,end]]) -> int
        
        Return the lowest index in S where substring sub is found,
        such that sub is contained within S[start:end].  Optional
        arguments start and end are interpreted as in slice notation.
        
        Return -1 on failure.
        """
    
        pass
    
    
    def format(self, *args, **kwargs):
        """
        S.format(*args, **kwargs) -> unicode
        
        Return a formatted version of S, using substitutions from args and kwargs.
        The substitutions are identified by braces ('{' and '}').
        """
    
        pass
    
    
    def index(self, *args, **kwargs):
        """
        S.index(sub [,start [,end]]) -> int
        
        Like S.find() but raise ValueError when the substring is not found.
        """
    
        pass
    
    
    def isalnum(self, *args, **kwargs):
        """
        S.isalnum() -> bool
        
        Return True if all characters in S are alphanumeric
        and there is at least one character in S, False otherwise.
        """
    
        pass
    
    
    def isalpha(self, *args, **kwargs):
        """
        S.isalpha() -> bool
        
        Return True if all characters in S are alphabetic
        and there is at least one character in S, False otherwise.
        """
    
        pass
    
    
    def isdecimal(self, *args, **kwargs):
        """
        S.isdecimal() -> bool
        
        Return True if there are only decimal characters in S,
        False otherwise.
        """
    
        pass
    
    
    def isdigit(self, *args, **kwargs):
        """
        S.isdigit() -> bool
        
        Return True if all characters in S are digits
        and there is at least one character in S, False otherwise.
        """
    
        pass
    
    
    def islower(self, *args, **kwargs):
        """
        S.islower() -> bool
        
        Return True if all cased characters in S are lowercase and there is
        at least one cased character in S, False otherwise.
        """
    
        pass
    
    
    def isnumeric(self, *args, **kwargs):
        """
        S.isnumeric() -> bool
        
        Return True if there are only numeric characters in S,
        False otherwise.
        """
    
        pass
    
    
    def isspace(self, *args, **kwargs):
        """
        S.isspace() -> bool
        
        Return True if all characters in S are whitespace
        and there is at least one character in S, False otherwise.
        """
    
        pass
    
    
    def istitle(self, *args, **kwargs):
        """
        S.istitle() -> bool
        
        Return True if S is a titlecased string and there is at least one
        character in S, i.e. upper- and titlecase characters may only
        follow uncased characters and lowercase characters only cased ones.
        Return False otherwise.
        """
    
        pass
    
    
    def isupper(self, *args, **kwargs):
        """
        S.isupper() -> bool
        
        Return True if all cased characters in S are uppercase and there is
        at least one cased character in S, False otherwise.
        """
    
        pass
    
    
    def join(self, *args, **kwargs):
        """
        S.join(iterable) -> unicode
        
        Return a string which is the concatenation of the strings in the
        iterable.  The separator between elements is S.
        """
    
        pass
    
    
    def ljust(self, *args, **kwargs):
        """
        S.ljust(width[, fillchar]) -> int
        
        Return S left-justified in a Unicode string of length width. Padding is
        done using the specified fill character (default is a space).
        """
    
        pass
    
    
    def lower(self, *args, **kwargs):
        """
        S.lower() -> unicode
        
        Return a copy of the string S converted to lowercase.
        """
    
        pass
    
    
    def lstrip(self, *args, **kwargs):
        """
        S.lstrip([chars]) -> unicode
        
        Return a copy of the string S with leading whitespace removed.
        If chars is given and not None, remove characters in chars instead.
        If chars is a str, it will be converted to unicode before stripping
        """
    
        pass
    
    
    def partition(self, *args, **kwargs):
        """
        S.partition(sep) -> (head, sep, tail)
        
        Search for the separator sep in S, and return the part before it,
        the separator itself, and the part after it.  If the separator is not
        found, return S and two empty strings.
        """
    
        pass
    
    
    def replace(self, *args, **kwargs):
        """
        S.replace(old, new[, count]) -> unicode
        
        Return a copy of S with all occurrences of substring
        old replaced by new.  If the optional argument count is
        given, only the first count occurrences are replaced.
        """
    
        pass
    
    
    def rfind(self, *args, **kwargs):
        """
        S.rfind(sub [,start [,end]]) -> int
        
        Return the highest index in S where substring sub is found,
        such that sub is contained within S[start:end].  Optional
        arguments start and end are interpreted as in slice notation.
        
        Return -1 on failure.
        """
    
        pass
    
    
    def rindex(self, *args, **kwargs):
        """
        S.rindex(sub [,start [,end]]) -> int
        
        Like S.rfind() but raise ValueError when the substring is not found.
        """
    
        pass
    
    
    def rjust(self, *args, **kwargs):
        """
        S.rjust(width[, fillchar]) -> unicode
        
        Return S right-justified in a Unicode string of length width. Padding is
        done using the specified fill character (default is a space).
        """
    
        pass
    
    
    def rpartition(self, *args, **kwargs):
        """
        S.rpartition(sep) -> (head, sep, tail)
        
        Search for the separator sep in S, starting at the end of S, and return
        the part before it, the separator itself, and the part after it.  If the
        separator is not found, return two empty strings and S.
        """
    
        pass
    
    
    def rsplit(self, *args, **kwargs):
        """
        S.rsplit([sep [,maxsplit]]) -> list of strings
        
        Return a list of the words in S, using sep as the
        delimiter string, starting at the end of the string and
        working to the front.  If maxsplit is given, at most maxsplit
        splits are done. If sep is not specified, any whitespace string
        is a separator.
        """
    
        pass
    
    
    def rstrip(self, *args, **kwargs):
        """
        S.rstrip([chars]) -> unicode
        
        Return a copy of the string S with trailing whitespace removed.
        If chars is given and not None, remove characters in chars instead.
        If chars is a str, it will be converted to unicode before stripping
        """
    
        pass
    
    
    def split(self, *args, **kwargs):
        """
        S.split([sep [,maxsplit]]) -> list of strings
        
        Return a list of the words in S, using sep as the
        delimiter string.  If maxsplit is given, at most maxsplit
        splits are done. If sep is not specified or is None, any
        whitespace string is a separator and empty strings are
        removed from the result.
        """
    
        pass
    
    
    def splitlines(self, *args, **kwargs):
        """
        S.splitlines(keepends=False) -> list of strings
        
        Return a list of the lines in S, breaking at line boundaries.
        Line breaks are not included in the resulting list unless keepends
        is given and true.
        """
    
        pass
    
    
    def startswith(self, *args, **kwargs):
        """
        S.startswith(prefix[, start[, end]]) -> bool
        
        Return True if S starts with the specified prefix, False otherwise.
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        prefix can also be a tuple of strings to try.
        """
    
        pass
    
    
    def strip(self, *args, **kwargs):
        """
        S.strip([chars]) -> unicode
        
        Return a copy of the string S with leading and trailing
        whitespace removed.
        If chars is given and not None, remove characters in chars instead.
        If chars is a str, it will be converted to unicode before stripping
        """
    
        pass
    
    
    def swapcase(self, *args, **kwargs):
        """
        S.swapcase() -> unicode
        
        Return a copy of S with uppercase characters converted to lowercase
        and vice versa.
        """
    
        pass
    
    
    def title(self, *args, **kwargs):
        """
        S.title() -> unicode
        
        Return a titlecased version of S, i.e. words start with title case
        characters, all remaining cased characters have lower case.
        """
    
        pass
    
    
    def translate(self, *args, **kwargs):
        """
        S.translate(table) -> unicode
        
        Return a copy of the string S, where all characters have been mapped
        through the given translation table, which must be a mapping of
        Unicode ordinals to Unicode ordinals, Unicode strings or None.
        Unmapped characters are left untouched. Characters mapped to None
        are deleted.
        """
    
        pass
    
    
    def upper(self, *args, **kwargs):
        """
        S.upper() -> unicode
        
        Return a copy of S converted to uppercase.
        """
    
        pass
    
    
    def zfill(self, *args, **kwargs):
        """
        S.zfill(width) -> unicode
        
        Pad a numeric string S with zeros on the left, to fill a field
        of the specified width. The string S is never truncated.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class ParsingWarning(exceptions.UserWarning):
    __weakref__ = None


class autoparsed(type):
    """
    metaclass for dramatically reducing setup syntax for simple hierarchies
    """
    
    
    
    def __new__(mcl, classname, bases, classdict):
        pass


class NameParseError(exceptions.Exception):
    __weakref__ = None


class EmptyTokenParser(Parser):
    """
    # special purpose empty parser
    """
    
    
    
    def build(self, **kwargs):
        pass
    
    
    def parse(self, data, **kwargs):
        pass


class TokenParser(Parser):
    """
    Abstract base class for Token parser
    """
    
    
    
    def build(self, **kwargs):
        pass
    
    
    def parse(self, data, **kwargs):
        pass


class Parsed(ProxyUni):
    """
    # For parsed objects, Token or upper level constructs
    """
    
    
    
    def __add__(self, other):
        """
        p1.__add__(p2) <==> p1+p2
        if p1 and p2 are of the same Parsed type, it's equivalent to reparsing str(p1) + str(p2)
        if p2 is an accepted sub part of p1, it adds it to the sub-parts
        """
    
        pass
    
    
    def __repr__(self):
        pass
    
    
    def compileName(self):
        pass
    
    
    def copy(self):
        """
        return an new independent copy of the parsed object
        """
    
        pass
    
    
    def findType(self, type):
        pass
    
    
    def isValid(self):
        """
        Validity
        """
    
        pass
    
    
    def parse(self, data, **kwargs):
        pass
    
    
    def setSubItem(self, index, value):
        """
        Change the value of one of the Parsed sub parts.  The new value will first be parsed as the same
        type as it is replacing.
        """
    
        pass
    
    
    def accepts(cls, other):
        """
        Checks if this Parsed class can accept another object as a subpart without reparsing
        """
    
        pass
    
    
    def classparse(cls, data, **kwargs):
        pass
    
    
    def classparser(cls):
        """
        parser object for that class
        """
    
        pass
    
    
    def classparserbuild(cls, **kwargs):
        """
        Inits class Parser, all instances of a Parsed class share the same yacc parser object
        """
    
        pass
    
    
    def getParserClass(cls, parsername):
        pass
    
    
    def __new__(cls, *args, **kwargs):
        """
        Creation of a Parsed object from a LexToken, other Parsed of compatible type or string,
        if a string is passed it will be parsed and checked for compatibility with this Parsed type
        """
    
        pass
    
    
    parser = None
    
    pos = None
    
    sub = None
    
    tokens = None
    
    classes = {}


class EmptyParser(Parser):
    """
    Parser for the empty production
    """
    
    
    
    def p_empty(self, p):
        """
        Empty :
        """
    
        pass
    
    
    start = 'Empty'


class Token(Parsed):
    """
    A class for token types, allows direct initialization from a string and type without checking
    to avoid unnecessary double parse of the string
    """
    
    
    
    pass



def isParsedClass(x):
    pass


def _printClassTree(cls):
    pass


def isParserClass(x):
    pass


def currentfn():
    pass


def verbose():
    """
    # increase from 0 to 1 or 2 for more debug feedback
    """

    pass


def _getTokenPatterns(parsercls):
    pass


def process(module=None):
    """
    cache out a dictionary of all Parsed and Parser classes, and create token classes
    """

    pass



