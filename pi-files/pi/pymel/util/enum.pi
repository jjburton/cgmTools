import exceptions

"""
This package provides a module for robust enumerations in Python.

An enumeration object is created with a sequence of string arguments
to the Enum() constructor:

    >>> from enum import Enum
    >>> Colours = Enum('Colours', ['red', 'blue', 'green'])
    >>> Weekdays = Enum('Weekdays', ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])

The return value is an immutable sequence object with a value for each
of the string arguments. Each value is also available as an attribute
named from the corresponding string argument:

    >>> pizza_night = Weekdays[4]
    >>> shirt_colour = Colours.green

The values are constants that can be compared with values from
the same enumeration, as well as with integers or strings; comparison with other
values will invoke Python's fallback comparisons:

    >>> pizza_night == Weekdays.fri
    True
    >>> shirt_colour > Colours.red
    True
    >>> shirt_colour == "green"
    True

Each value from an enumeration exports its sequence index
as an integer, and can be coerced to a simple string matching the
original arguments used to create the enumeration:

    >>> str(pizza_night)
    'fri'
    >>> shirt_colour.index
    2
"""

class Enum(object):
    """
    Enumerated type
    """
    
    
    
    def __contains__(self, value):
        pass
    
    
    def __delattr__(self, name):
        pass
    
    
    def __delitem__(self, index):
        pass
    
    
    def __eq__(self, other):
        pass
    
    
    def __getitem__(self, index):
        pass
    
    
    def __init__(self, name, keys, **kwargs):
        """
        Create an enumeration instance
        
        :Parameters:
        name : `str`
            The name of this enumeration
        keys : `dict` from `str` to `int`, or iterable of keys
            The keys for the enumeration; if this is a dict, it should map
            from key to it's value (ie, from string to int)
            Otherwise, it should be an iterable of keys, where their index
            within the iterable is their value -ie, passing either of these
            would give the same result:
                {'Red':0,'Green':1,'Blue':2}
                ('Red', 'Green', 'Blue')
        multiKeys : `bool`
            Defaults to False
            If True, allows multiple keys per value - ie,
                Enum('Names', {'Bob':0,'Charles':1,'Chuck':1}, multiKeys=True)
            When looking up a key from a value, a single key is always returned
            - see defaultKeys for a discussion of which key this is.
            When multiKeys is enabled, the length of keys and values may not be
            equal.
            If False (default), then the end result enum will always have a
            one-to-one key / value mapping; if multiple keys are supplied for a
            a single value, then which key is used is indeterminate (an error
            will not be raised).
        defaultKeys : `dict` from `int` to `string`
            If given, should be a map from values to the 'default' key to
            return for that value when using methods like getKey(index)
            This will only be used if the value actually has multiple keys
            mapping to it, and in this case, the specified default key must be
            present within keys (if not, a EnumBadDefaultKeyError is raised).
            If there are multiple keys for a given value, and no defaultKey is
            provided, which one is used is undefined.
        docs : `dict` from `str` to `int, or None
            if given, should provide a map from keys to an associated docstring
            for that key; the dict need not provide an entry for every key
        """
    
        pass
    
    
    def __iter__(self):
        pass
    
    
    def __len__(self):
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __setattr__(self, name, value):
        pass
    
    
    def __setitem__(self, index, value):
        pass
    
    
    def __str__(self):
        pass
    
    
    def getIndex(self, key):
        """
        Get an index value from a key
        This method always returns an index. If a valid index is passed instead
        of a key, the index will be returned unchanged.  This is useful when you
        need an index, but are not certain whether you are starting with a key
        or an index.
        
            >>> units = Enum('units', ['invalid', 'inches', 'feet', 'yards', 'miles', 'millimeters', 'centimeters', 'kilometers', 'meters'])
            >>> units.getIndex('inches')
            1
            >>> units.getIndex(3)
            3
            >>> units.getIndex('hectares')
            Traceback (most recent call last):
              ...
            ValueError: invalid enumerator key: 'hectares'
            >>> units.getIndex(10)
            Traceback (most recent call last):
              ...
            ValueError: invalid enumerator index: 10
        """
    
        pass
    
    
    def getKey(self, index):
        """
        Get a key value from an index
        This method always returns a key. If a valid key is passed instead of an
        index, the key will be returned unchanged.  This is useful when you need
        a key, but are not certain whether you are starting with a key or an
        index.
        
            >>> units = Enum('units', ['invalid', 'inches', 'feet', 'yards', 'miles', 'millimeters', 'centimeters', 'kilometers', 'meters'])
            >>> units.getKey(2)
            'feet'
            >>> units.getKey('inches')
            'inches'
            >>> units.getKey(10)
            Traceback (most recent call last):
              ...
            ValueError: invalid enumerator index: 10
            >>> units.getKey('hectares')
            Traceback (most recent call last):
              ...
            ValueError: invalid enumerator key: 'hectares'
        """
    
        pass
    
    
    def keys(self):
        """
        return a list of keys as strings
        """
    
        pass
    
    
    def values(self):
        """
        return a list of `EnumValue`s
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    name = None


class EnumException(exceptions.Exception):
    """
    Base class for all exceptions in this module
    """
    
    
    
    def __init__(self):
        pass
    
    
    __weakref__ = None


class EnumValue(object):
    """
    A specific value of an enumerated type
    """
    
    
    
    def __cmp__(self, other):
        pass
    
    
    def __hash__(self):
        pass
    
    
    def __init__(self, enumtype, index, key, doc=None):
        """
        Set up a new instance
        """
    
        pass
    
    
    def __int__(self):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    enumtype = None
    
    index = None
    
    key = None


from . import utilitytypes

class EnumDict(utilitytypes.EquivalencePairs):
    """
    This class provides a dictionary type for storing enumerations.  Keys are string labels, while
    values are enumerated integers.
    
    To instantiate, pass a sequence of string arguments to the EnumDict() constructor:
    
        >>> from enum import EnumDict
        >>> Colours = EnumDict(['red', 'blue', 'green'])
        >>> Weekdays = EnumDict(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])
        >>> sorted(Weekdays.items())
        [('fri', 4), ('mon', 0), ('sat', 5), ('sun', 6), ('thu', 3), ('tue', 1), ('wed', 2)]
    
    Alternately, a dictionary of label-value pairs can be provided:
    
        >>> Numbers = EnumDict({'one': 1, 'two': 2, 'hundred' : 100, 'thousand' : 1000 } )
    
    To convert from one representation to another, just use normal dictionary retrieval, it
    works in either direction:
    
        >>> Weekdays[4]
        'fri'
        >>> Weekdays['fri']
        4
    
    If you need a particular representation, but don't know what you're starting from ( for
    example, a value that was passed as an argument ) you can use `EnumDict.key` or
    `EnumDict.value`:
    
        >>> Weekdays.value(3)
        3
        >>> Weekdays.value('thu')
        3
        >>> Weekdays.key(2)
        'wed'
        >>> Weekdays.key('wed')
        'wed'
    """
    
    
    
    def __init__(self, keys, **kwargs):
        """
        Create an enumeration instance
        """
    
        pass
    
    
    def __repr__(self):
        pass
    
    
    def key(self, index):
        """
        get a key value from an index. this method always returns a key. if a valid key is passed instead of an index, the key will
        be returned unchanged.  this is useful when you need a key, but are not certain whether you are starting with a key or an index.
        
            >>> units = EnumDict(['invalid', 'inches', 'feet', 'yards', 'miles', 'millimeters', 'centimeters', 'kilometers', 'meters'])
            >>> units.key(2)
            'feet'
            >>> units.key('inches')
            'inches'
            >>> units.key(10)  #doctest: +ELLIPSIS
            Traceback (most recent call last):
              ...
            ValueError: invalid enumerator value: 10
            >>> units.key('hectares')
            Traceback (most recent call last):
              ...
            ValueError: invalid enumerator key: 'hectares'
        """
    
        pass
    
    
    def keys(self):
        """
        return a list of keys as strings ordered by their enumerator value
        """
    
        pass
    
    
    def value(self, key):
        """
        get an index value from a key. this method always returns an index. if a valid index is passed instead of a key, the index will
        be returned unchanged.  this is useful when you need an index, but are not certain whether you are starting with a key or an index.
        
            >>> units = EnumDict(['invalid', 'inches', 'feet', 'yards', 'miles', 'millimeters', 'centimeters', 'kilometers', 'meters'])
            >>> units.value('inches')
            1
            >>> units.value(3)
            3
            >>> units.value('hectares')
            Traceback (most recent call last):
              ...
            ValueError: invalid enumerator key: 'hectares'
            >>> units.value(10) #doctest: +ELLIPSIS
            Traceback (most recent call last):
              ...
            ValueError: invalid enumerator value: 10
        """
    
        pass
    
    
    def values(self):
        """
        return a list of ordered integer values
        """
    
        pass


class EnumBadDefaultKeyError(exceptions.ValueError, EnumException):
    """
    Raised when a supplied default key for a value was not present
    """
    
    
    
    def __init__(self, val, key):
        pass
    
    
    def __str__(self):
        pass
    
    
    __weakref__ = None


class EnumImmutableError(exceptions.TypeError, EnumException):
    """
    Raised when attempting to modify an Enum
    """
    
    
    
    def __init__(self, *args):
        pass
    
    
    def __str__(self):
        pass
    
    
    __weakref__ = None


class EnumBadKeyError(exceptions.TypeError, EnumException):
    """
    Raised when creating an Enum with non-string keys
    """
    
    
    
    def __init__(self, key):
        pass
    
    
    def __str__(self):
        pass
    
    
    __weakref__ = None


class EnumEmptyError(exceptions.AssertionError, EnumException):
    """
    Raised when attempting to create an empty enumeration
    """
    
    
    
    def __str__(self):
        pass
    
    
    __weakref__ = None



__date__ = '2007-01-24'

__version__ = '0.4.3'


