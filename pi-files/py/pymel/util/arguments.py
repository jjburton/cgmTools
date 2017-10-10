"""
Defines arguments manipulation utilities, like checking if an argument is iterable, flattening a nested arguments list, etc.
These utility functions can be used by other util modules and are imported in util's main namespace for use by other pymel modules
"""

from collections import deque as _deque
from pymel.util.utilitytypes import ProxyUnicode

class RemovedKey(object):
    def __eq__(self, other):
        pass
    
    
    def __init__(self, oldVal):
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def __repr__(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class AddedKey(object):
    def __eq__(self, other):
        pass
    
    
    def __init__(self, newVal):
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def __repr__(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class ChangedKey(object):
    def __eq__(self, other):
        pass
    
    
    def __init__(self, oldVal, newVal):
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def __repr__(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def isIterable(obj):
    """
    Returns True if an object is iterable and not a string or ProxyUnicode type, otherwise returns False.
    
    :rtype: bool
    """

    pass


def iterateArgs(*args, **kwargs):
    """
    Iterates through all arguments list: recursively replaces any iterable argument in *args by a tuple of its
    elements that will be inserted at its place in the returned arguments.
    
    By default will return elements depth first, from root to leaves.  Set postorder or breadth to control order.
    
    :Keywords:
        depth : int
            will specify the nested depth limit after which iterables are returned as they are
    
        type
            for type='list' will only expand lists, by default type='all' expands any iterable sequence
    
        postorder : bool
             will return elements depth first, from leaves to roots
    
        breadth : bool
            will return elements breadth first, roots, then first depth level, etc.
    
    For a nested list represent trees::
    
        a____b____c
        |    |____d
        e____f
        |____g
    
    preorder(default) :
    
        >>> tuple(k for k in iterateArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'], limit=1 ))
        ('a', 'b', ['c', 'd'], 'e', 'f', 'g')
        >>> tuple(k for k in iterateArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'] ))
        ('a', 'b', 'c', 'd', 'e', 'f', 'g')
    
    postorder :
    
        >>> tuple(k for k in iterateArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'], postorder=True, limit=1 ))
        ('b', ['c', 'd'], 'a', 'f', 'g', 'e')
        >>> tuple(k for k in iterateArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'], postorder=True))
        ('c', 'd', 'b', 'a', 'f', 'g', 'e')
    
    breadth :
    
        >>> tuple(k for k in iterateArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'], limit=1, breadth=True))
        ('a', 'e', 'b', ['c', 'd'], 'f', 'g')
        >>> tuple(k for k in iterateArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'], breadth=True))
        ('a', 'e', 'b', 'f', 'g', 'c', 'd')
    
    Note that with default depth (-1 for unlimited) and order (preorder), if passed a pymel Tree
    result will be the equivalent of using a preorder iterator : iter(theTree)
    """

    pass


def setCascadingDictItem(dict, keys, value):
    pass


def mergeCascadingDicts(from_dict, to_dict, allowDictToListMerging=False, allowNewListMembers=False):
    """
    recursively update to_dict with values from from_dict.
    
    if any entries in 'from_dict' are instances of the class RemovedKey,
    then the key containing that value will be removed from to_dict
    
    if allowDictToListMerging is True, then if to_dict contains a list,
    from_dict can contain a dictionary with int keys which can be used to
    sparsely update the list.
    
    if allowNewListMembers is True, and allowDictToListMerging is also True,
    then if merging an index into a list that currently isn't long enough to
    contain that index, then the list will be extended to be long enough (with
    None inserted in any intermediate indices)
    
    Note: if using RemovedKey objects and allowDictToList merging, then only
    indices greater than all of any indices updated / added should be removed,
    because the order in which items are updated / removed is indeterminate.
    """

    pass


def listForNone(res):
    """
    returns an empty list when the result is None
    """

    pass


def breadth(iterable, testFn='<function isIterable>', limit=1000):
    """
    iterator doing a breadth first expansion of args
    """

    pass


def postorder(iterable, testFn='<function isIterable>', limit=1000):
    """
    iterator doing a postorder expansion of args
    """

    pass


def isNumeric(obj):
    """
    Returns True if an object is a number type, otherwise returns False.
    
    :rtype: bool
    """

    pass


def preorder(iterable, testFn='<function isIterable>', limit=1000):
    """
    iterator doing a preorder expansion of args
    """

    pass


def isScalar(obj):
    """
    Returns True if an object is a number or complex type, otherwise returns False.
    
    :rtype: bool
    """

    pass


def breadthIterArgs(limit=1000, testFn='<function isIterable>', *args):
    """
    iterator doing a breadth first expansion of args
    """

    pass


def getCascadingDictItem(dict, keys, default={}):
    pass


def postorderIterArgs(limit=1000, testFn='<function isIterable>', *args):
    """
    iterator doing a postorder expansion of args
    """

    pass


def preorderIterArgs(limit=1000, testFn='<function isIterable>', *args):
    """
    iterator doing a preorder expansion of args
    """

    pass


def sequenceToSlices(intList, sort=True):
    """
    convert a sequence of integers into a tuple of slice objects
    """

    pass


def breadthArgs(limit=1000, testFn='<function isIterable>', *args):
    """
    returns a list of a breadth first expansion of args
    """

    pass


def compareCascadingDicts(dict1, dict2, encoding=None, useAddedKeys=False, useChangedKeys=False):
    """
    compares two cascading dicts
    
    Parameters
    ----------
    dict1 : dict, list, or tuple
        the first object to compare
    dict2 : dict, list, or tuple
        the second object to compare
    encoding : `str` or None or False
        controls how comparisons are made when one value is a str, and one is a
        unicode; if None, then comparisons are simply made with == (so ascii
        characters will compare equally); if the value False, then unicode and
        str are ALWAYS considered different - ie, u'foo' and 'foo' would not be
        considered equal; otherwise, it should be the name of a unicode
        encoding, which will be applied to the unicode string before comparing
    useAddedKeys : bool
        if True, then similarly to how 'RemovedKey' objects are used in the
        returned diferences object (see the Returns section), 'AddedKey' objects
        are used for keys which exist in dict2 but not in dict1; this allows
        a user to distinguish, purely by inspecting the differences dict, which
        keys are brand new, versus merely changed; mergeCascadingDicts will
        treat AddedKey objects exactly the same as though they were their
        contents - ie, useAddedKeys should make no difference to the behavior
        of mergeCascadingDicts
    useChangedKeys : bool
        if True, then similarly to how 'RemovedKey' objects are used in the
        returned diferences object (see the Returns section), 'ChangedKey'
        objects are used for keys which exist in both dict1 and dict2, but with
        different values
    
    Returns
    -------
    both : `set`
        keys that were present in both (non-recursively)
        (both, only1, and only2 should be discrete partitions of all the keys
        present in both dict1 and dict2)
    only1 : `set`
        keys that were present in only1 (non-recursively)
    only2 : `set`
        keys that were present in only2 (non-recursively)
    differences : `dict`
        recursive sparse dict containing information that was 'different' in
        dict2 - either not present in dict1, or having a different value in
        dict2, or removed in dict2 (in which case an instance of 'RemovedKey'
        will be set as the value in differences)
        Values that are different, and both dictionaries, will themselves have
        sparse entries, showing only what is different
        The return value should be such that if you do if you merge the
        differences with d1, you will get d2.
    """

    pass


def postorderArgs(limit=1000, testFn='<function isIterable>', *args):
    """
    returns a list of  a postorder expansion of args
    """

    pass


def reorder(x, indexList=[], indexDict={}):
    """
    Reorder a list based upon a list of positional indices and/or a dictionary of fromIndex:toIndex.
    
        >>> l = ['zero', 'one', 'two', 'three', 'four', 'five', 'six']
        >>> reorder( l, [1, 4] ) # based on positional indices: 0-->1, 1-->4
        ['one', 'four', 'zero', 'two', 'three', 'five', 'six']
        >>> reorder( l, [1, None, 4] ) # None can be used as a place-holder
        ['one', 'zero', 'four', 'two', 'three', 'five', 'six']
        >>> reorder( l, [1, 4], {5:6} )  # remapping via dictionary: move the value at index 5 to index 6
        ['one', 'four', 'zero', 'two', 'three', 'six', 'five']
    """

    pass


def clsname(x):
    pass


def preorderArgs(limit=1000, testFn='<function isIterable>', *args):
    """
    returns a list of a preorder expansion of args
    """

    pass


def isSequence(obj):
    """
    same as `operator.isSequenceType`
    
    :rtype: bool
    """

    pass


def expandArgs(*args, **kwargs):
    """
    'Flattens' the arguments list: recursively replaces any iterable argument in *args by a tuple of its
    elements that will be inserted at its place in the returned arguments.
    
    By default will return elements depth first, from root to leaves.  Set postorder or breadth to control order.
    
    :Keywords:
        depth : int
            will specify the nested depth limit after which iterables are returned as they are
    
        type
            for type='list' will only expand lists, by default type='all' expands any iterable sequence
    
        postorder : bool
             will return elements depth first, from leaves to roots
    
        breadth : bool
            will return elements breadth first, roots, then first depth level, etc.
    
    For a nested list represent trees::
    
        a____b____c
        |    |____d
        e____f
        |____g
    
    preorder(default) :
    
        >>> expandArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'], limit=1 )
        ('a', 'b', ['c', 'd'], 'e', 'f', 'g')
        >>> expandArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'] )
        ('a', 'b', 'c', 'd', 'e', 'f', 'g')
    
    postorder :
    
        >>> expandArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'], postorder=True, limit=1)
        ('b', ['c', 'd'], 'a', 'f', 'g', 'e')
        >>> expandArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'], postorder=True)
        ('c', 'd', 'b', 'a', 'f', 'g', 'e')
    
    breadth :
    
        >>> expandArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'], limit=1, breadth=True)
        ('a', 'e', 'b', ['c', 'd'], 'f', 'g')
        >>> expandArgs( 'a', ['b', ['c', 'd']], 'e', ['f', 'g'], breadth=True)
        ('a', 'e', 'b', 'f', 'g', 'c', 'd')
    
    
    Note that with default depth (unlimited) and order (preorder), if passed a pymel Tree
    result will be the equivalent of doing a preorder traversal : [k for k in iter(theTree)]
    """

    pass


def convertListArgs(args):
    pass


def pairIter(sequence):
    """
    Returns an iterator over every 2 items of sequence.
    
    ie, [x for x in pairIter([1,2,3,4])] == [(1,2), (3,4)]
    
    If sequence has an odd number of items, the last item will not be returned in a pair.
    """

    pass


def izip_longest(*args, **kwds):
    pass


def isMapping(obj):
    """
    Returns True if an object is a mapping (dictionary) type, otherwise returns False.
    
    same as `operator.isMappingType`
    
    :rtype: bool
    """

    pass



