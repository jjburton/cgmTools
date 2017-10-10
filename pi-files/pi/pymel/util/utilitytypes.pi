import exceptions

"""
Defines common types and type related utilities:  Singleton, etc.
These types can be shared by other utils modules and imported into util main namespace for use by other pymel modules
"""

from collections import defaultdict

class defaultlist(list):
    def __getitem__(self, index):
        pass
    
    
    def __init__(self, default_factory, *args, **kwargs):
        pass
    
    
    def __setitem__(self, index, item):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class universalmethod(object):
    def __get__(self, instance, cls=None):
        pass
    
    
    def __init__(self, f):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class Singleton(type):
    """
    Metaclass for Singleton classes.
    
    >>> class DictSingleton(dict) :
    ...    __metaclass__ = Singleton
    ...
    >>> DictSingleton({'A':1})
    {'A': 1}
    >>> a = DictSingleton()
    >>> a
    {'A': 1}
    >>> b = DictSingleton({'B':2})
    >>> a, b, DictSingleton()
    ({'B': 2}, {'B': 2}, {'B': 2})
    >>> a is b and a is DictSingleton()
    True
    
    >>> class StringSingleton(str) :
    ...    __metaclass__ = Singleton
    ...
    >>> StringSingleton("first")
    'first'
    >>> a = StringSingleton()
    >>> a
    'first'
    >>> b = StringSingleton("changed")
    >>> a, b, StringSingleton()
    ('first', 'first', 'first')
    >>> a is b and a is StringSingleton()
    True
    
    >>> class DictSingleton2(DictSingleton):
    ...     pass
    ...
    >>> DictSingleton2({'A':1})
    {'A': 1}
    >>> a = DictSingleton2()
    >>> a
    {'A': 1}
    >>> b = DictSingleton2({'B':2})
    >>> a, b, DictSingleton2()
    ({'B': 2}, {'B': 2}, {'B': 2})
    >>> a is b and a is DictSingleton2()
    True
    """
    
    
    
    def __new__(mcl, classname, bases, classdict):
        pass


class ModuleInterceptor(object):
    """
    This class is used to intercept an unset attribute of a module to perfrom a callback. The
    callback will only be performed if the attribute does not exist on the module. Any error raised
    in the callback will cause the original AttributeError to be raised.
    
        def cb( module, attr):
             if attr == 'this':
                 print "intercepted"
             else:
                 raise ValueError
        import sys
        sys.modules[__name__] = ModuleInterceptor(__name__, cb)
        intercepted
    
    The class does not work when imported into the main namespace.
    """
    
    
    
    def __getattr__(self, attr):
        pass
    
    
    def __init__(self, moduleName, callback):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class ProxyUnicode(object):
    def __add__(self, *args, **kwargs):
        """
        x.__add__(y) <==> x+y
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
    
    
    def __getitem__(self, *args, **kwargs):
        """
        x.__getitem__(y) <==> x[y]
        """
    
        pass
    
    
    def __getnewargs__(self, *args, **kwargs):
        """
        # print method
        #@functools.wraps(f)
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
    
    
    def __lt__(self, *args, **kwargs):
        """
        x.__lt__(y) <==> x<y
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
    
    
    def __str__(self, *args, **kwargs):
        """
        x.__str__() <==> str(x)
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
    
    
    def endswith(self, *args, **kwargs):
        """
        S.endswith(suffix[, start[, end]]) -> bool
        
        Return True if S ends with the specified suffix, False otherwise.
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        suffix can also be a tuple of strings to try.
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
    
    
    def isdecimal(self, *args, **kwargs):
        """
        S.isdecimal() -> bool
        
        Return True if there are only decimal characters in S,
        False otherwise.
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
    
    
    def upper(self, *args, **kwargs):
        """
        S.upper() -> unicode
        
        Return a copy of S converted to uppercase.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class TwoWayDict(dict):
    """
    A dictionary that can also map in reverse: value to key.
    
    >>> twd = TwoWayDict( {3:'foobar'} )
    >>> twd[3]
    'foobar'
    >>> twd.get_key('foobar')
    3
    
    Entries in both sets (keys and values) must be unique within that set, but
    not necessarily across the two sets - ie, you may have 12 as both a key and
    a value, but you may not have two keys which both map to 12 (or, as with a
    regular dict, two key entries for 12).
    
    If a key is updated to a new value, get_key for the old value will raise
    a KeyError:
    
    >>> twd = TwoWayDict( {3:'old'} )
    >>> twd[3] = 'new'
    >>> twd[3]
    'new'
    >>> twd.get_key('new')
    3
    >>> twd.get_key('old')
    Traceback (most recent call last):
        ...
    KeyError: 'old'
    
    Similarly, if a key is updated to an already-existing value, then the old key
    will be removed from the dictionary!
    
    >>> twd = TwoWayDict( {'oldKey':'aValue'} )
    >>> twd['newKey'] = 'aValue'
    >>> twd['newKey']
    'aValue'
    >>> twd.get_key('aValue')
    'newKey'
    >>> twd['oldKey']
    Traceback (most recent call last):
        ...
    KeyError: 'oldKey'
    
    If a group of values is fed to the TwoWayDict (either on initialization, or
    through 'update', etc) that is not consistent with these conditions, then the
    resulting dictionary is indeterminate; however, it is guaranteed to be a valid/
    uncorrupted TwoWayDict.
    (This is similar to how dict will allow, for instance, {1:'foo', 1:'bar'}).
    
    >>> twd = TwoWayDict( {1:'foo', 1:'bar'} )
    >>> # Is twd[1] 'foo' or 'bar'?? Nobody knows!
    >>> # ...however, one of these is guaranteed to raise an error...
    >>> twd.get_key('foo') + twd.get_key('bar')   #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    KeyError: (either 'bar' or 'foo')
    >>> twd = TwoWayDict( {1:'foo', 2:'foo'} )
    >>> # Is twd.get_key('foo') 1 or 2? Nobody knows!
    >>> # ...however, one of these is guaranteed to raise an error...
    >>> twd[1] + twd[2]   #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    KeyError: (either 1 or 2)
    
    Obviously, such shenannigans should be avoided - at some point in the future, this may
    cause an error to be raised...
    """
    
    
    
    def __delitem__(self, k):
        pass
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def __setitem__(self, k, v):
        pass
    
    
    def clear(self):
        pass
    
    
    def copy(self):
        pass
    
    
    def get_key(self, v):
        pass
    
    
    def has_value(self, v):
        pass
    
    
    def pop(self, k):
        pass
    
    
    def popitem(self, **kws):
        pass
    
    
    def setdefault(self, **kws):
        pass
    
    
    def update(self, *args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class LazyDocString(str):
    """
    Set the __doc__ of an object to an object of this class in order to have
    a docstring that is dynamically generated when used.
    
    Due to restrictions of inheriting from StringType (which is necessary,
    as the 'help' function does a check to see if __doc__ is a string),
    the creator can only take a single object.
    
    Since the object initialization requires multiple parameters, the
    LazyDocString should be fed an sliceable-iterable on creation,
    of the following form:
    
        LazyDocString( [documentedObj, docGetter, arg1, arg2, ...] )
    
    documentedObj should be the object on which we are placing the docstring
    
    docGetter should be a function which is used to retrieve the 'real'
    docstring - it's args will be documentedObj and any extra args
    passed to the object on creation.
    
    Example Usage:
    
    >>> def getDocStringFromDict(obj):
    ...     returnVal = docStringDict[obj]
    ...     return returnVal
    >>>
    >>> # In order to alter the doc of a class, we need to use a metaclass
    >>> class TestMetaClass(type): pass
    >>>
    >>> class TestClass(object):
    ...     __metaclass__ = TestMetaClass
    ...
    ...     def aMethod(self):
    ...         pass
    ...
    ...     aMethod.__doc__ = LazyDocString( (aMethod, getDocStringFromDict, (aMethod,)) )
    >>>
    >>> TestClass.__doc__ = LazyDocString( (TestClass, getDocStringFromDict, (TestClass,)) )
    >>>
    >>>
    >>> docStringDict = {TestClass:'New Docs for PynodeClass!',
    ...                  TestClass.aMethod.im_func:'Method docs!'}
    >>>
    >>> TestClass.__doc__
    'New Docs for PynodeClass!'
    >>> TestClass.aMethod.__doc__
    'Method docs!'
    
    
    Note that new-style classes (ie, instances of 'type') and instancemethods
    can't have their __doc__ altered.
    
    In the case of classes, you can get around this by using a metaclass for
    the class whose docstring you wish to alter.
    
    In the case of instancemethods, just set the __doc__ on the function
    underlying the method (ie, myMethod.im_func). Note that if the __doc__
    for the method is set within the class definition itself, you will
    already automatically be modifying the underlying function.
    """
    
    
    
    def __init__(self, argList):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    def capitalize(self, *args, **kwargs):
        pass
    
    
    def center(self, *args, **kwargs):
        pass
    
    
    def count(self, *args, **kwargs):
        pass
    
    
    def decode(self, *args, **kwargs):
        pass
    
    
    def encode(self, *args, **kwargs):
        pass
    
    
    def endswith(self, *args, **kwargs):
        pass
    
    
    def expandtabs(self, *args, **kwargs):
        pass
    
    
    def find(self, *args, **kwargs):
        pass
    
    
    def format(self, *args, **kwargs):
        pass
    
    
    def index(self, *args, **kwargs):
        pass
    
    
    def isalnum(self, *args, **kwargs):
        pass
    
    
    def isalpha(self, *args, **kwargs):
        pass
    
    
    def isdigit(self, *args, **kwargs):
        pass
    
    
    def islower(self, *args, **kwargs):
        pass
    
    
    def isspace(self, *args, **kwargs):
        pass
    
    
    def istitle(self, *args, **kwargs):
        pass
    
    
    def isupper(self, *args, **kwargs):
        pass
    
    
    def join(self, *args, **kwargs):
        pass
    
    
    def ljust(self, *args, **kwargs):
        pass
    
    
    def lower(self, *args, **kwargs):
        pass
    
    
    def lstrip(self, *args, **kwargs):
        pass
    
    
    def partition(self, *args, **kwargs):
        pass
    
    
    def replace(self, *args, **kwargs):
        pass
    
    
    def rfind(self, *args, **kwargs):
        pass
    
    
    def rindex(self, *args, **kwargs):
        pass
    
    
    def rjust(self, *args, **kwargs):
        pass
    
    
    def rpartition(self, *args, **kwargs):
        pass
    
    
    def rsplit(self, *args, **kwargs):
        pass
    
    
    def rstrip(self, *args, **kwargs):
        pass
    
    
    def split(self, *args, **kwargs):
        pass
    
    
    def splitlines(self, *args, **kwargs):
        pass
    
    
    def startswith(self, *args, **kwargs):
        pass
    
    
    def strip(self, *args, **kwargs):
        pass
    
    
    def swapcase(self, *args, **kwargs):
        pass
    
    
    def title(self, *args, **kwargs):
        pass
    
    
    def translate(self, *args, **kwargs):
        pass
    
    
    def upper(self, *args, **kwargs):
        pass
    
    
    def zfill(self, *args, **kwargs):
        pass
    
    
    __dict__ = None


class propertycache(object):
    """
    Class for creating properties where the value is initially calculated then stored.
    
    Intended for use as a descriptor, ie:
    
    class MyClass(object):
        @propertycache
        def aValue(self):
            return calcValue()
    c = MyClass()
    c.aValue
    """
    
    
    
    def __get__(self, ownerInstance, ownerCls=None):
        pass
    
    
    def __init__(self, func):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class LazyDocStringError(exceptions.Exception):
    __weakref__ = None


class metaReadOnlyAttr(type):
    """
    A metaclass to allow to define read-only class attributes, accessible either on the class or it's instances
    and protected against re-write or re-definition.
    Read only attributes are stored in the class '__readonly__' dictionary.
    Any attribute can be marked as read only by including its name in a tuple named '__readonly__' in the class
    definition. Alternatively methods can be marked as read only with the @readonly decorator and will then get
    added to the dictionary at class creation
    """
    
    
    
    def __setattr__(cls, name, value):
        """
        overload __setattr__ to forbid modification of read only class info
        """
    
        pass
    
    
    def __new__(mcl, classname, bases, classdict):
        """
        Create a new metaReadOnlyAttr class
        """
    
        pass


class metaStatic(Singleton):
    """
    A static (immutable) Singleton metaclass to quickly build classes
    holding predefined immutable dicts
    
    >>> class FrozenDictSingleton(dict) :
    ...    __metaclass__ = metaStatic
    ...
    >>> FrozenDictSingleton({'A':1})
    {'A': 1}
    >>> a = FrozenDictSingleton()
    >>> a
    {'A': 1}
    >>> b = FrozenDictSingleton()
    >>> a, b
    ({'A': 1}, {'A': 1})
    >>> a is b
    True
    
    >>> b = FrozenDictSingleton({'B':2})
    Traceback (most recent call last):
        ...
    TypeError: 'FrozenDictSingleton' object does not support redefinition
    
    >>> a['A']
    1
    >>> a['A'] = 2   #doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: '<class '...FrozenDictSingleton'>' object does not support item assignation
    
    >>> a.clear()
    Traceback (most recent call last):
        ...
    AttributeError: 'FrozenDictSingleton' object has no attribute 'clear'
    
    >>> a, b, FrozenDictSingleton()
    ({'A': 1}, {'A': 1}, {'A': 1})
    >>> a is b and a is FrozenDictSingleton()
    True
    
    >>> class StaticTest(FrozenDictSingleton):
    ...     pass
    ...
    >>> StaticTest({'A': 1})
    {'A': 1}
    >>> a = StaticTest()
    >>> a
    {'A': 1}
    >>> b = StaticTest()
    >>> a, b
    ({'A': 1}, {'A': 1})
    
    >>> class StaticTest2( StaticTest ):
    ...     pass
    ...
    >>> StaticTest2({'B': 2})
    {'B': 2}
    >>> a = StaticTest2()
    >>> a
    {'B': 2}
    >>> b = StaticTest2()
    >>> a, b
    ({'B': 2}, {'B': 2})
    """
    
    
    
    def __new__(mcl, classname, bases, classdict):
        pass


class EquivalencePairs(TwoWayDict):
    """
    A mapping object similar to a TwoWayDict, with the addition that indexing
    and '__contains__' can now be used with keys OR values:
    
    >>> eq = EquivalencePairs( {3:'foobar'} )
    >>> eq[3]
    'foobar'
    >>> eq['foobar']
    3
    >>> 3 in eq
    True
    >>> 'foobar' in eq
    True
    
    This is intended to be used where there is a clear distinction between
    keys and values, so there is little likelihood of the sets of keys
    and values intersecting.
    
    The dictionary has the same restrictions as a TwoWayDict, with the added restriction
    that an object must NOT appear in both the keys and values, unless it maps to itself.
    If a new item is set that would break this restriction, the old keys/values will be
    removed from the mapping to ensure these restrictions are met.
    
    >>> eq = EquivalencePairs( {1:'a', 2:'b', 3:'die'} )
    >>> eq['a']
    1
    >>> eq['b']
    2
    >>> eq[1]
    'a'
    >>> eq[2]
    'b'
    >>> del eq['die']
    >>> eq[3]
    Traceback (most recent call last):
        ...
    KeyError: 3
    >>> eq[2] = 1
    >>> eq[1]
    2
    >>> eq[2]
    1
    >>> eq['a']
    Traceback (most recent call last):
        ...
    KeyError: 'a'
    >>> eq['b']
    Traceback (most recent call last):
        ...
    KeyError: 'b'
    
    # Even though 2 is set as a VALUE, since it already
    # exists as a KEY, the 2:'b' mapping is removed,
    # so eq['b'] will be invalid...
    >>> eq = EquivalencePairs( {1:'a', 2:'b'} )
    >>> eq['new'] = 2
    >>> eq['new']
    2
    >>> eq[2]
    'new'
    >>> eq['b']
    Traceback (most recent call last):
        ...
    KeyError: 'b'
    
    # Similarly, if you set as a KEy something that
    # already exists as a value...
    >>> eq = EquivalencePairs( {1:'a', 2:'b'} )
    >>> eq['b'] = 3
    >>> eq['b']
    3
    >>> eq[3]
    'b'
    >>> eq[2]
    Traceback (most recent call last):
        ...
    KeyError: 2
    
    If a group of values is fed to the EquivalencePairs (either on initialization, or
    through 'update', etc) that is not consistent with it's restrictions, then the
    resulting dictionary is indeterminate; however, it is guaranteed to be a valid/
    uncorrupted TwoWayDict.
    
    (This is somewhat similar to the behavior of the dict object itself, which will allow
    a definition such as {1:2, 1:4} )
    
    Obviously, such shenannigans should be avoided - at some point in the future, this may
    even cause an error to be raised...
    
    Finally, note that a distinction between keys and values IS maintained, for compatibility
    with keys(), iter_values(), etc.
    """
    
    
    
    def __contains__(self, key):
        pass
    
    
    def __delitem__(self, key):
        pass
    
    
    def __getitem__(self, key):
        pass
    
    
    def __setitem__(self, k, v):
        pass
    
    
    def get(self, key, d=None):
        pass



def alias(origAttrName):
    """
    Returns a property which is simply an alias for another property.
    
    Acts simply to provide another name to reference the same
    underlying attribute; useful when subclassing, where a subclass
    might have a more descriptive name for an attribute that has the
    same function.
    
    The only purpose of this function is to produce more readable code.
    
    Example:
    
    >>> class GenericExporter(object):
    ...     def __init__(self, outFile):
    ...         self.outFile = outFile
    ...
    >>> class CowExporter(GenericExporter):
    ...     cowFile = alias('outFile')
    ...
    >>> CowExporter('bessie.cow').cowFile
    'bessie.cow'
    """

    pass


def proxyClass(cls, classname, dataAttrName=None, dataFuncName=None, remove=(), makeDefaultInit=False, sourceIsImmutable=True, module=None):
    """
    This function will generate a proxy class which keeps the internal data separate from the wrapped class. This
    is useful for emulating immutable types such as str and tuple, while using mutable data.  Be aware that changing data
    will break hashing.  not sure the best solution to this, but a good approach would be to subclass your proxy and implement
    a valid __hash__ method.
    
    :Parameters:
    cls : `type`
        The class to wrap
    classname : `string`
        The name to give the resulting proxy class
    dataAttrName : `string`
        The name of an attribute on which an instance of the wrapped class will
        be stored.
        Either dataAttrname or dataFuncName must be given, but not both.
    dataFuncName : `string`
        The name of an attribute on which reside a function, which takes no
        arguments, and when called, will return an instance of the wrapped
        class.
        Either dataAttrname or dataFuncName must be given, but not both.
    remove : `string` iterable
        An iterable of name of attributes which should NOT be wrapped.
        Note that certain attributes will never be wrapped - the list of
        such items is found in the NOT_PROXY_WRAPPED constant.
    makeDefaultInit : `bool`
        If True and dataAttrName is True, then a 'default' __init__ function
        will be created, which creates an instance of the wrapped class, and
        assigns it to the dataAttr. Defaults to False
        If dataAttrName is False, does nothing
    sourceIsImmutable : `bool`
        This parameter is included only for backwards compatibility - it is
        ignored.
    
    :rtype: `type`
    """

    pass


def addLazyDocString(object, creator, *creatorArgs, **creatorKwargs):
    """
    helper for LazyDocString.  Equivalent to :
    
    object.__doc__ = LazyDocString( (object, creator, creatorArgs, creatorKwargs) )
    """

    pass


def _method(*args, **kwargs):
    """
    S.zfill(width) -> string
    
    Pad a numeric string S with zeros on the left, to fill a field
    of the specified width.  The string S is never truncated.
    """

    pass


def LazyLoadModule(name, contents):
    """
    :param name: name of the module
    :param contents: dictionary of initial module globals
    
    This function returns a special module type with one method `_addattr`.  The signature
    of this method is:
    
        _addattr(name, creator, *creatorArgs, **creatorKwargs)
    
    Attributes added with this method will not be created until the first time that
    they are accessed, at which point a callback function will be called to generate
    the attribute's value.
    
    :param name: name of the attribute to lazily add
    :param creator: a function that create the
    
    Example::
    
        import sys
        mod = LazyLoadModule(__name__, globals())
        mod._addattr( 'foo', str, 'bar' )
        sys.modules[__name__] = mod
    
    One caveat of this technique is that if a user imports everything from your
    lazy module ( .e.g from module import * ), it will cause all lazy attributes
    to be evaluated.
    
    Also, if any module-level expression needs to reference something that only
    exists in the LazyLoadModule, it will need to be stuck in after the creation of the
    LazyLoadModule.  Then, typically, after defining all functions/classes/etc
    which rely on the LazyLoadModule attributes, you will wish to update the
    LazyLoadModule with the newly-created functions - typically, this is done
    with the _updateLazyModule method.
    
    Finally, any functions which reference any LazyLoadModule-only attributes,
    whether they are defined after OR before the creation of the LazyLoadModule,
    will have to prefix it with a reference to the LazyLoadModule.
    
    Example::
    
        import sys
    
        def myFunc():
            # need to preface foo with 'lazyModule',
            # even though this function is defined before
            # the creation of the lazy module!
            print 'foo is:', lazyModule.foo
    
        mod = lazyLoadModule(__name__, globals())
        mod._addattr( 'foo', str, 'bar' )
        sys.modules[__name__] = mod
    
        # create a reference to the LazyLoadModule in this module's
        # global space
        lazyModule = sys.modules[__name__]
    
        # define something which relies on something in the lazy module
        fooExpanded = lazyModule.foo + '... now with MORE!'
    
        # update the lazyModule with our new additions (ie, fooExpanded)
        lazyModule._updateLazyModule(globals())
    """

    pass


def makeMethod(name):
    pass


def readonly(f):
    """
    Marks a class member as protected, allowing metaProtected to prevent re-assignation on the classes it generates
    """

    pass



_name = 'zfill'

NOT_PROXY_WRAPPED = []


