"""
########################################################################
WARNING: this module may be removed in the future, or radically altered.
We do NOT recommend using it in external code...
########################################################################

>>> # Create a tree from nested sequences:
>>> myTree = Tree('a', ('ab', 'aa', 3, {}))
>>> print myTree
('a', ('ab', 'aa', '3', '{}'))
>>> print myTree.formatted()
+: a
|--: ab
|--: aa
|--: 3
\--: {}
>>> myTree.sort()
>>> print myTree.formatted()
+: a
|--: 3
|--: {}
|--: aa
\--: ab
>>>
>>> # Forests
>>> # -------
>>> # We can make a forest by passing in multiple args to the constructor
>>> myForest = Tree(1, 2, 3)
>>> for top in myForest.tops():
...     print top.value
...
1
2
3
>>> print myForest.formatted()
-: 1
<BLANKLINE>
-: 2
<BLANKLINE>
-: 3
"""

from collections import *

from copy import deepcopy
from copy import Error
from copy import copy

class IndexedFrozenTree(object):
    """
    Additionnal methods for pure python indexed trees implementation, elements must have unique values
                or Tree class must define a key method that provides a unique key for each element 
    The methods for an immutable Tree class.
    """
    
    
    
    def __cmp__(self, other):
        pass
    
    
    def __contains__(self, element):
        """
        Returns True if element is in the tree, False otherwise.
        """
    
        pass
    
    
    def __eq__(self, other):
        """
        Checks for equality of two trees.
        """
    
        pass
    
    
    def __getitem__(self, value):
        """
        Get a subtree from the Tree, given an element or value.
        Note that to be consistent with __getitem__ usual behavior, it will raise an exception
        it it doesn't find exactly one match (0 or more), method get will be more user friendly
        on non indexed trees.
        It's also possible to seek a path : a list of elements or values, it will limit the results
        to the subtrees that match the last item of the path, and whose parents match the path.
        A path can be relative, or absolute if starting with None as first item
        """
    
        pass
    
    
    def __init__(self, *args, **kwargs):
        """
        Initializer - non-sequences are values, sequeneces are children of previous value.
        
        The args represent tree nodes, where a node is specified by either another tree
        object, or a non sequence representing the value of that node, optionally followed
        by a sequence representing the children of that node.
        
        Values cannot be None, and when specifying the elements in a child sequence, they
        must fit the same rules for valid tree nodes given above.
        
        Invalid arguments (ie, two sequences following each other) will raise a ValueError.
        
        If there is only one node (ie, only one non-sequence arg, optionally followed by
        a list of children), then a tree is returned, with the single node as it's
        single root.
        
        If there are multiple nodes, then a forest is returned, with each node
        representing a root.
        
        For speed and ease of use, if there is only a single argument, and it is a sequence,
        it is the same as though we had unpacked the sequence:
        
        >>> list = (1,('a','b'))
        >>> Tree(list) == Tree(*list)
        True
        
        Now, some examples:
        
        >>> myTree = Tree()  # makes an empty tree
        >>> print myTree
        ()
        >>> myTree = Tree(1)
        >>> print repr(myTree) # different ways of stringifying...
        Tree(1)
        >>> myTree = Tree(1,('a','b'))  # make a tree with children
        >>> print myTree.formatted()
        +: 1
        |--: a
        \--: b
        >>> myTree = Tree(1,(2,'foo', ('bar',))) # tree with a subtree
        >>> myTree.view()
        +: 1
        |--: 2
        \-+: foo
          \--: bar
        >>> myForrest = Tree(1,2)   # make a forest
        >>> myForrest.view()        # view() is just shortcut for:
        ...                      # print treeInst.formatted()
        -: 1
        <BLANKLINE>
        -: 2
        >>> otherForrest = Tree('root1', myForrest, 'root4', ('kid1', 'kid2'))
        >>> otherForrest.view()
        -: root1
        <BLANKLINE>
        -: 1
        <BLANKLINE>
        -: 2
        <BLANKLINE>
        +: root4
        |--: kid1
        \--: kid2
        
        ...Note that a tree object, even if a forrest, will never be taken
        to represent the children of the previous arg - ie, the previous
        example did NOT result in:
        +: root1
        |--: 1
        \--: 2
        <BLANKLINE>
        +: root4
        |--: kid1
        \--: kid2
        
        This means that giving multiple forrest objects will effectively merge
        them into a larger forest:
        
        >>> forrest1 = Tree(1, 2)
        >>> forrest1.view()
        -: 1
        <BLANKLINE>
        -: 2
        >>> forrest2 = Tree('foo', 'bar')
        >>> forrest2.view()
        -: foo
        <BLANKLINE>
        -: bar
        >>> forrest3 = Tree(forrest1, forrest2)
        >>> forrest3.view()
        -: 1
        <BLANKLINE>
        -: 2
        <BLANKLINE>
        -: foo
        <BLANKLINE>
        -: bar
        
        Trying to give 2 sequences in a row results in a ValueError:
        
        >>> Tree('root1', (1,2), (3,4))
        Traceback (most recent call last):
          ...
        ValueError: Child sequence must immediately follow a non-sequence value when initializing a tree
        
        Similarly, trying to use 'None' as a tree value gives an error:
        >>> Tree(None, (1,2))
        Traceback (most recent call last):
          ...
        ValueError: None cannot be a tree element
        """
    
        pass
    
    
    def __iter__(self):
        """
        Iterates first level of tree returning nested tuples for childs
        """
    
        pass
    
    
    def __len__(self):
        """
        Returns the number of elements (nodes) in the tree.
        """
    
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def __nonzero__(self):
        pass
    
    
    def __reduce__(self):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        """
        # TODO: make it match new __init__
        # - use [] for child lists, () for value/children pairs
        """
    
        pass
    
    
    def __unicode__(self):
        pass
    
    
    def breadth(self):
        """
        Breadth first traversal of a tree.
        """
    
        pass
    
    
    def child(self, index=0):
        """
        Returns nth child (by default first), is it exists
        """
    
        pass
    
    
    def childs(self):
        """
        Returns an iterator on all childs of self, or an empty iterator if self has no childs
        """
    
        pass
    
    
    def copy(self, cls=None):
        """
        Shallow copy of a tree.
        An extra class argument can be given to copy with a different
        (tree) class. No checks are made on the class.
        """
    
        pass
    
    
    def debug(self, depth=0):
        """
        Returns an detailed representation of the tree fro debug purposes
        """
    
        pass
    
    
    def depth(self):
        """
        Depth of self, the distance to self's root
        """
    
        pass
    
    
    def dist(self, element, **kwargs):
        """
        Returns distance from self to element, 0 means self==element, None if no path exists
        up keyword set to True means it will search ascendants(parent and parents of parent) self for element, default is False
        down keyword set to True means it will search descendants(childs and childs of childs) of self for element, default is False
        If neither up nor down is specified, will search both directions
        signed keyword set to true means returns negative distance when element is upwards self, positive when it's downwards
        """
    
        pass
    
    
    def elementKey(self, element):
        pass
    
    
    def formatted(self, returnList=False):
        """
        Returns an indented string representation of the tree
        """
    
        pass
    
    
    def get(self, value, default=()):
        """
        Identical to the __getitem__ method but will return a default value instead of raising KeyError
        if nor result is found
        """
    
        pass
    
    
    def hasChilds(self):
        pass
    
    
    def height(self):
        """
        Get maximum downward depth (distance from element to furthest leaf downwards of it) of the tree
        """
    
        pass
    
    
    def isElement(self):
        pass
    
    
    def issubtree(self, other):
        pass
    
    
    def leaves(self):
        """
        Get an iterator on all leaves under self
        """
    
        pass
    
    
    def level(self, dist=0):
        """
        Get an iterator on all elements at the specified distance of self, negative distance means up, positive means down
        """
    
        pass
    
    
    def parents(self):
        """
        Returns an iterator on path from element to top root, starting with first parent, empty iterator means self is root
        """
    
        pass
    
    
    def path(self, element=None, **kwargs):
        """
        Returns an iterator of the path to specified element if found, including starting element,
        empty iterator means no path found.
        For trees where duplicate values are allowed, shortest path to an element of this value is returned.
        element can be an ancestor or a descendant of self, if no element is specified, will return path from self's root to self
        up keyword set to True means it will search ascendants(parent and parents of parent) self for element, default is False
        down keyword set to True means it will search descendants(childs and childs of childs) of self for element, default is False
        If neither up nor down is specified, will search both directions
        order keyword defines in what order the path will be returned and can be set to 'top', 'bottom' or 'self', order by default is 'top'
        'top' means path will be returned from ancestor to descendant
        'bottom' means path will be returned from descendant to ancestor
        'self' means path will be returned from self to element
        """
    
        pass
    
    
    def postorder(self):
        """
        Postorder traversal of a tree.
        """
    
        pass
    
    
    def preorder(self):
        """
        The standard preorder traversal iterator.
        """
    
        pass
    
    
    def root(self):
        """
        Root node of self, if self is a subtree, will travel up to top most node of containing tree
        """
    
        pass
    
    
    def siblings(self):
        """
        Returns an iterator on self siblings, not including self and starting with self next sibling,
        if self has no siblings (self has no parent or is unique child) then returns an empty iterator
        """
    
        pass
    
    
    def size(self):
        """
        Returns the number of elements (nodes) in the tree.
        """
    
        pass
    
    
    def top(self, index=0):
        """
        The nth top node of self (by default first)
        """
    
        pass
    
    
    def tops(self):
        """
        Iterator on the top nodes of self, the subtrees that have no parent in self,
        will yield only self if self isn't a forest
        """
    
        pass
    
    
    def view(self):
        """
        Shortcut for print(self.formatted())
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    key = None
    
    next = None
    
    parent = None
    
    value = None


class FrozenTree(object):
    """
    Core methods for pure python trees implementation
    The methods for an immutable Tree class.
    """
    
    
    
    def __cmp__(self, other):
        pass
    
    
    def __contains__(self, element):
        """
        Returns True if element is in the tree, False otherwise.
        """
    
        pass
    
    
    def __eq__(self, other):
        """
        Checks for equality of two trees.
        """
    
        pass
    
    
    def __getitem__(self, value):
        """
        Get a subtree from the Tree, given an element or value.
        Note that to be consistent with __getitem__ usual behavior, it will raise an exception
        it it doesn't find exactly one match (0 or more), method get will be more user friendly
        on non indexed trees.
        It's also possible to seek a path : a list of elements or values, it will limit the results
        to the subtrees that match the last item of the path, and whose parents match the path.
        A path can be relative, or absolute if starting with None as first item
        """
    
        pass
    
    
    def __init__(self, *args, **kwargs):
        """
        Initializer - non-sequences are values, sequeneces are children of previous value.
        
        The args represent tree nodes, where a node is specified by either another tree
        object, or a non sequence representing the value of that node, optionally followed
        by a sequence representing the children of that node.
        
        Values cannot be None, and when specifying the elements in a child sequence, they
        must fit the same rules for valid tree nodes given above.
        
        Invalid arguments (ie, two sequences following each other) will raise a ValueError.
        
        If there is only one node (ie, only one non-sequence arg, optionally followed by
        a list of children), then a tree is returned, with the single node as it's
        single root.
        
        If there are multiple nodes, then a forest is returned, with each node
        representing a root.
        
        For speed and ease of use, if there is only a single argument, and it is a sequence,
        it is the same as though we had unpacked the sequence:
        
        >>> list = (1,('a','b'))
        >>> Tree(list) == Tree(*list)
        True
        
        Now, some examples:
        
        >>> myTree = Tree()  # makes an empty tree
        >>> print myTree
        ()
        >>> myTree = Tree(1)
        >>> print repr(myTree) # different ways of stringifying...
        Tree(1)
        >>> myTree = Tree(1,('a','b'))  # make a tree with children
        >>> print myTree.formatted()
        +: 1
        |--: a
        \--: b
        >>> myTree = Tree(1,(2,'foo', ('bar',))) # tree with a subtree
        >>> myTree.view()
        +: 1
        |--: 2
        \-+: foo
          \--: bar
        >>> myForrest = Tree(1,2)   # make a forest
        >>> myForrest.view()        # view() is just shortcut for:
        ...                      # print treeInst.formatted()
        -: 1
        <BLANKLINE>
        -: 2
        >>> otherForrest = Tree('root1', myForrest, 'root4', ('kid1', 'kid2'))
        >>> otherForrest.view()
        -: root1
        <BLANKLINE>
        -: 1
        <BLANKLINE>
        -: 2
        <BLANKLINE>
        +: root4
        |--: kid1
        \--: kid2
        
        ...Note that a tree object, even if a forrest, will never be taken
        to represent the children of the previous arg - ie, the previous
        example did NOT result in:
        +: root1
        |--: 1
        \--: 2
        <BLANKLINE>
        +: root4
        |--: kid1
        \--: kid2
        
        This means that giving multiple forrest objects will effectively merge
        them into a larger forest:
        
        >>> forrest1 = Tree(1, 2)
        >>> forrest1.view()
        -: 1
        <BLANKLINE>
        -: 2
        >>> forrest2 = Tree('foo', 'bar')
        >>> forrest2.view()
        -: foo
        <BLANKLINE>
        -: bar
        >>> forrest3 = Tree(forrest1, forrest2)
        >>> forrest3.view()
        -: 1
        <BLANKLINE>
        -: 2
        <BLANKLINE>
        -: foo
        <BLANKLINE>
        -: bar
        
        Trying to give 2 sequences in a row results in a ValueError:
        
        >>> Tree('root1', (1,2), (3,4))
        Traceback (most recent call last):
          ...
        ValueError: Child sequence must immediately follow a non-sequence value when initializing a tree
        
        Similarly, trying to use 'None' as a tree value gives an error:
        >>> Tree(None, (1,2))
        Traceback (most recent call last):
          ...
        ValueError: None cannot be a tree element
        """
    
        pass
    
    
    def __iter__(self):
        """
        Iterates first level of tree returning nested tuples for childs
        """
    
        pass
    
    
    def __len__(self):
        """
        Returns the number of elements (nodes) in the tree.
        """
    
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def __nonzero__(self):
        pass
    
    
    def __reduce__(self):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        """
        # TODO: make it match new __init__
        # - use [] for child lists, () for value/children pairs
        """
    
        pass
    
    
    def __unicode__(self):
        pass
    
    
    def breadth(self):
        """
        Breadth first traversal of a tree.
        """
    
        pass
    
    
    def child(self, index=0):
        """
        Returns nth child (by default first), is it exists
        """
    
        pass
    
    
    def childs(self):
        """
        Returns an iterator on all childs of self, or an empty iterator if self has no childs
        """
    
        pass
    
    
    def copy(self, cls=None):
        """
        Shallow copy of a tree.
        An extra class argument can be given to copy with a different
        (tree) class. No checks are made on the class.
        """
    
        pass
    
    
    def debug(self, depth=0):
        """
        Returns an detailed representation of the tree fro debug purposes
        """
    
        pass
    
    
    def depth(self):
        """
        Depth of self, the distance to self's root
        """
    
        pass
    
    
    def dist(self, element, **kwargs):
        """
        Returns distance from self to element, 0 means self==element, None if no path exists
        up keyword set to True means it will search ascendants(parent and parents of parent) self for element, default is False
        down keyword set to True means it will search descendants(childs and childs of childs) of self for element, default is False
        If neither up nor down is specified, will search both directions
        signed keyword set to true means returns negative distance when element is upwards self, positive when it's downwards
        """
    
        pass
    
    
    def formatted(self, returnList=False):
        """
        Returns an indented string representation of the tree
        """
    
        pass
    
    
    def get(self, value, default=()):
        """
        Identical to the __getitem__ method but will return a default value instead of raising KeyError
        if nor result is found
        """
    
        pass
    
    
    def hasChilds(self):
        pass
    
    
    def height(self):
        """
        Get maximum downward depth (distance from element to furthest leaf downwards of it) of the tree
        """
    
        pass
    
    
    def isElement(self):
        pass
    
    
    def issubtree(self, other):
        pass
    
    
    def leaves(self):
        """
        Get an iterator on all leaves under self
        """
    
        pass
    
    
    def level(self, dist=0):
        """
        Get an iterator on all elements at the specified distance of self, negative distance means up, positive means down
        """
    
        pass
    
    
    def parents(self):
        """
        Returns an iterator on path from element to top root, starting with first parent, empty iterator means self is root
        """
    
        pass
    
    
    def path(self, element=None, **kwargs):
        """
        Returns an iterator of the path to specified element if found, including starting element,
        empty iterator means no path found.
        For trees where duplicate values are allowed, shortest path to an element of this value is returned.
        element can be an ancestor or a descendant of self, if no element is specified, will return path from self's root to self
        up keyword set to True means it will search ascendants(parent and parents of parent) self for element, default is False
        down keyword set to True means it will search descendants(childs and childs of childs) of self for element, default is False
        If neither up nor down is specified, will search both directions
        order keyword defines in what order the path will be returned and can be set to 'top', 'bottom' or 'self', order by default is 'top'
        'top' means path will be returned from ancestor to descendant
        'bottom' means path will be returned from descendant to ancestor
        'self' means path will be returned from self to element
        """
    
        pass
    
    
    def postorder(self):
        """
        Postorder traversal of a tree.
        """
    
        pass
    
    
    def preorder(self):
        """
        The standard preorder traversal iterator.
        """
    
        pass
    
    
    def root(self):
        """
        Root node of self, if self is a subtree, will travel up to top most node of containing tree
        """
    
        pass
    
    
    def siblings(self):
        """
        Returns an iterator on self siblings, not including self and starting with self next sibling,
        if self has no siblings (self has no parent or is unique child) then returns an empty iterator
        """
    
        pass
    
    
    def size(self):
        """
        Returns the number of elements (nodes) in the tree.
        """
    
        pass
    
    
    def top(self, index=0):
        """
        The nth top node of self (by default first)
        """
    
        pass
    
    
    def tops(self):
        """
        Iterator on the top nodes of self, the subtrees that have no parent in self,
        will yield only self if self isn't a forest
        """
    
        pass
    
    
    def view(self):
        """
        Shortcut for print(self.formatted())
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    next = None
    
    parent = None
    
    value = None


class IndexedTree(object):
    """
    Additionnal methods for pure python indexed trees implementation, elements must have unique values
                or Tree class must define a key method that provides a unique key for each element 
    Additionnal methods for a Mutable Tree class.
    """
    
    
    
    def __cmp__(self, other):
        pass
    
    
    def __contains__(self, element):
        """
        Returns True if element is in the tree, False otherwise.
        """
    
        pass
    
    
    def __delitem__(self, element):
        pass
    
    
    def __eq__(self, other):
        """
        Checks for equality of two trees.
        """
    
        pass
    
    
    def __getitem__(self, value):
        """
        Get a subtree from the Tree, given an element or value.
        Note that to be consistent with __getitem__ usual behavior, it will raise an exception
        it it doesn't find exactly one match (0 or more), method get will be more user friendly
        on non indexed trees.
        It's also possible to seek a path : a list of elements or values, it will limit the results
        to the subtrees that match the last item of the path, and whose parents match the path.
        A path can be relative, or absolute if starting with None as first item
        """
    
        pass
    
    
    def __init__(self, *args, **kwargs):
        """
        Initializer - non-sequences are values, sequeneces are children of previous value.
        
        The args represent tree nodes, where a node is specified by either another tree
        object, or a non sequence representing the value of that node, optionally followed
        by a sequence representing the children of that node.
        
        Values cannot be None, and when specifying the elements in a child sequence, they
        must fit the same rules for valid tree nodes given above.
        
        Invalid arguments (ie, two sequences following each other) will raise a ValueError.
        
        If there is only one node (ie, only one non-sequence arg, optionally followed by
        a list of children), then a tree is returned, with the single node as it's
        single root.
        
        If there are multiple nodes, then a forest is returned, with each node
        representing a root.
        
        For speed and ease of use, if there is only a single argument, and it is a sequence,
        it is the same as though we had unpacked the sequence:
        
        >>> list = (1,('a','b'))
        >>> Tree(list) == Tree(*list)
        True
        
        Now, some examples:
        
        >>> myTree = Tree()  # makes an empty tree
        >>> print myTree
        ()
        >>> myTree = Tree(1)
        >>> print repr(myTree) # different ways of stringifying...
        Tree(1)
        >>> myTree = Tree(1,('a','b'))  # make a tree with children
        >>> print myTree.formatted()
        +: 1
        |--: a
        \--: b
        >>> myTree = Tree(1,(2,'foo', ('bar',))) # tree with a subtree
        >>> myTree.view()
        +: 1
        |--: 2
        \-+: foo
          \--: bar
        >>> myForrest = Tree(1,2)   # make a forest
        >>> myForrest.view()        # view() is just shortcut for:
        ...                      # print treeInst.formatted()
        -: 1
        <BLANKLINE>
        -: 2
        >>> otherForrest = Tree('root1', myForrest, 'root4', ('kid1', 'kid2'))
        >>> otherForrest.view()
        -: root1
        <BLANKLINE>
        -: 1
        <BLANKLINE>
        -: 2
        <BLANKLINE>
        +: root4
        |--: kid1
        \--: kid2
        
        ...Note that a tree object, even if a forrest, will never be taken
        to represent the children of the previous arg - ie, the previous
        example did NOT result in:
        +: root1
        |--: 1
        \--: 2
        <BLANKLINE>
        +: root4
        |--: kid1
        \--: kid2
        
        This means that giving multiple forrest objects will effectively merge
        them into a larger forest:
        
        >>> forrest1 = Tree(1, 2)
        >>> forrest1.view()
        -: 1
        <BLANKLINE>
        -: 2
        >>> forrest2 = Tree('foo', 'bar')
        >>> forrest2.view()
        -: foo
        <BLANKLINE>
        -: bar
        >>> forrest3 = Tree(forrest1, forrest2)
        >>> forrest3.view()
        -: 1
        <BLANKLINE>
        -: 2
        <BLANKLINE>
        -: foo
        <BLANKLINE>
        -: bar
        
        Trying to give 2 sequences in a row results in a ValueError:
        
        >>> Tree('root1', (1,2), (3,4))
        Traceback (most recent call last):
          ...
        ValueError: Child sequence must immediately follow a non-sequence value when initializing a tree
        
        Similarly, trying to use 'None' as a tree value gives an error:
        >>> Tree(None, (1,2))
        Traceback (most recent call last):
          ...
        ValueError: None cannot be a tree element
        """
    
        pass
    
    
    def __iter__(self):
        """
        Iterates first level of tree returning nested tuples for childs
        """
    
        pass
    
    
    def __len__(self):
        """
        Returns the number of elements (nodes) in the tree.
        """
    
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def __nonzero__(self):
        pass
    
    
    def __reduce__(self):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __setitem__(self, element, value):
        """
        # Edit methods that are defined for mutable trees
        """
    
        pass
    
    
    def __str__(self):
        """
        # TODO: make it match new __init__
        # - use [] for child lists, () for value/children pairs
        """
    
        pass
    
    
    def __unicode__(self):
        pass
    
    
    def add(self, element, parent=None, next=None):
        """
        Add an element to self. parent and next element can be specified.
        Element will be added as a child of parent, parent can be any element or subtree of self:
        if parent is specified as a value there must exactly one match in self or an exception will be raised
        if parent is None, element will be added as a sibling of self's top node(s)
        if next is not none, element will be added before next in the childs of parent, else as a last childs
        """
    
        pass
    
    
    def breadth(self):
        """
        Breadth first traversal of a tree.
        """
    
        pass
    
    
    def child(self, index=0):
        """
        Returns nth child (by default first), is it exists
        """
    
        pass
    
    
    def childs(self):
        """
        Returns an iterator on all childs of self, or an empty iterator if self has no childs
        """
    
        pass
    
    
    def copy(self, cls=None):
        """
        Shallow copy of a tree.
        An extra class argument can be given to copy with a different
        (tree) class. No checks are made on the class.
        """
    
        pass
    
    
    def debug(self, depth=0):
        """
        Returns an detailed representation of the tree fro debug purposes
        """
    
        pass
    
    
    def depth(self):
        """
        Depth of self, the distance to self's root
        """
    
        pass
    
    
    def dist(self, element, **kwargs):
        """
        Returns distance from self to element, 0 means self==element, None if no path exists
        up keyword set to True means it will search ascendants(parent and parents of parent) self for element, default is False
        down keyword set to True means it will search descendants(childs and childs of childs) of self for element, default is False
        If neither up nor down is specified, will search both directions
        signed keyword set to true means returns negative distance when element is upwards self, positive when it's downwards
        """
    
        pass
    
    
    def elementKey(self, element):
        pass
    
    
    def formatted(self, returnList=False):
        """
        Returns an indented string representation of the tree
        """
    
        pass
    
    
    def get(self, value, default=()):
        """
        Identical to the __getitem__ method but will return a default value instead of raising KeyError
        if nor result is found
        """
    
        pass
    
    
    def graft(self, element, parent=None, next=None):
        """
        Attach element to self.
        If parent is secified, will be grafted as last child of parent (or before child 'next'),
        if parent is not in self, will raise an exception,
        if parent is None will be grafted at top level of self, besides any existing root(s).
        If next is specified, self will be grafted before next in the list of parent's childs,
        if next is not in parent's childs, will raise an exception,
        if next is None, self will be grafted as last child under parent.
        """
    
        pass
    
    
    def hasChilds(self):
        pass
    
    
    def height(self):
        """
        Get maximum downward depth (distance from element to furthest leaf downwards of it) of the tree
        """
    
        pass
    
    
    def isElement(self):
        pass
    
    
    def issubtree(self, other):
        pass
    
    
    def leaves(self):
        """
        Get an iterator on all leaves under self
        """
    
        pass
    
    
    def level(self, dist=0):
        """
        Get an iterator on all elements at the specified distance of self, negative distance means up, positive means down
        """
    
        pass
    
    
    def parents(self):
        """
        Returns an iterator on path from element to top root, starting with first parent, empty iterator means self is root
        """
    
        pass
    
    
    def path(self, element=None, **kwargs):
        """
        Returns an iterator of the path to specified element if found, including starting element,
        empty iterator means no path found.
        For trees where duplicate values are allowed, shortest path to an element of this value is returned.
        element can be an ancestor or a descendant of self, if no element is specified, will return path from self's root to self
        up keyword set to True means it will search ascendants(parent and parents of parent) self for element, default is False
        down keyword set to True means it will search descendants(childs and childs of childs) of self for element, default is False
        If neither up nor down is specified, will search both directions
        order keyword defines in what order the path will be returned and can be set to 'top', 'bottom' or 'self', order by default is 'top'
        'top' means path will be returned from ancestor to descendant
        'bottom' means path will be returned from descendant to ancestor
        'self' means path will be returned from self to element
        """
    
        pass
    
    
    def pop(self, element):
        """
        Delete top node of self and reparent all it's subtrees under it's current parent.
        If self was a root all it's subtrees become separate trees of a forest under the 'None' root.
        self will now have the new parent as top node
        """
    
        pass
    
    
    def postorder(self):
        """
        Postorder traversal of a tree.
        """
    
        pass
    
    
    def preorder(self):
        """
        The standard preorder traversal iterator.
        """
    
        pass
    
    
    def prune(self, element):
        """
        Ungrafts element from self, with everything under it
        """
    
        pass
    
    
    def remove(self, element):
        """
        Remove element from self, along with everything under it, will raise an exception if element is not in self
        """
    
        pass
    
    
    def reroot(self, element):
        """
        Reroot self so that element is self new top node
        """
    
        pass
    
    
    def root(self):
        """
        Root node of self, if self is a subtree, will travel up to top most node of containing tree
        """
    
        pass
    
    
    def siblings(self):
        """
        Returns an iterator on self siblings, not including self and starting with self next sibling,
        if self has no siblings (self has no parent or is unique child) then returns an empty iterator
        """
    
        pass
    
    
    def size(self):
        """
        Returns the number of elements (nodes) in the tree.
        """
    
        pass
    
    
    def sort(self, *args):
        pass
    
    
    def top(self, index=0):
        """
        The nth top node of self (by default first)
        """
    
        pass
    
    
    def tops(self):
        """
        Iterator on the top nodes of self, the subtrees that have no parent in self,
        will yield only self if self isn't a forest
        """
    
        pass
    
    
    def view(self):
        """
        Shortcut for print(self.formatted())
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    key = None
    
    next = None
    
    parent = None
    
    value = None


class Tree(object):
    """
    Core methods for pure python trees implementation
    Additionnal methods for a Mutable Tree class.
    """
    
    
    
    def __cmp__(self, other):
        pass
    
    
    def __contains__(self, element):
        """
        Returns True if element is in the tree, False otherwise.
        """
    
        pass
    
    
    def __delitem__(self, element):
        pass
    
    
    def __eq__(self, other):
        """
        Checks for equality of two trees.
        """
    
        pass
    
    
    def __getitem__(self, value):
        """
        Get a subtree from the Tree, given an element or value.
        Note that to be consistent with __getitem__ usual behavior, it will raise an exception
        it it doesn't find exactly one match (0 or more), method get will be more user friendly
        on non indexed trees.
        It's also possible to seek a path : a list of elements or values, it will limit the results
        to the subtrees that match the last item of the path, and whose parents match the path.
        A path can be relative, or absolute if starting with None as first item
        """
    
        pass
    
    
    def __init__(self, *args, **kwargs):
        """
        Initializer - non-sequences are values, sequeneces are children of previous value.
        
        The args represent tree nodes, where a node is specified by either another tree
        object, or a non sequence representing the value of that node, optionally followed
        by a sequence representing the children of that node.
        
        Values cannot be None, and when specifying the elements in a child sequence, they
        must fit the same rules for valid tree nodes given above.
        
        Invalid arguments (ie, two sequences following each other) will raise a ValueError.
        
        If there is only one node (ie, only one non-sequence arg, optionally followed by
        a list of children), then a tree is returned, with the single node as it's
        single root.
        
        If there are multiple nodes, then a forest is returned, with each node
        representing a root.
        
        For speed and ease of use, if there is only a single argument, and it is a sequence,
        it is the same as though we had unpacked the sequence:
        
        >>> list = (1,('a','b'))
        >>> Tree(list) == Tree(*list)
        True
        
        Now, some examples:
        
        >>> myTree = Tree()  # makes an empty tree
        >>> print myTree
        ()
        >>> myTree = Tree(1)
        >>> print repr(myTree) # different ways of stringifying...
        Tree(1)
        >>> myTree = Tree(1,('a','b'))  # make a tree with children
        >>> print myTree.formatted()
        +: 1
        |--: a
        \--: b
        >>> myTree = Tree(1,(2,'foo', ('bar',))) # tree with a subtree
        >>> myTree.view()
        +: 1
        |--: 2
        \-+: foo
          \--: bar
        >>> myForrest = Tree(1,2)   # make a forest
        >>> myForrest.view()        # view() is just shortcut for:
        ...                      # print treeInst.formatted()
        -: 1
        <BLANKLINE>
        -: 2
        >>> otherForrest = Tree('root1', myForrest, 'root4', ('kid1', 'kid2'))
        >>> otherForrest.view()
        -: root1
        <BLANKLINE>
        -: 1
        <BLANKLINE>
        -: 2
        <BLANKLINE>
        +: root4
        |--: kid1
        \--: kid2
        
        ...Note that a tree object, even if a forrest, will never be taken
        to represent the children of the previous arg - ie, the previous
        example did NOT result in:
        +: root1
        |--: 1
        \--: 2
        <BLANKLINE>
        +: root4
        |--: kid1
        \--: kid2
        
        This means that giving multiple forrest objects will effectively merge
        them into a larger forest:
        
        >>> forrest1 = Tree(1, 2)
        >>> forrest1.view()
        -: 1
        <BLANKLINE>
        -: 2
        >>> forrest2 = Tree('foo', 'bar')
        >>> forrest2.view()
        -: foo
        <BLANKLINE>
        -: bar
        >>> forrest3 = Tree(forrest1, forrest2)
        >>> forrest3.view()
        -: 1
        <BLANKLINE>
        -: 2
        <BLANKLINE>
        -: foo
        <BLANKLINE>
        -: bar
        
        Trying to give 2 sequences in a row results in a ValueError:
        
        >>> Tree('root1', (1,2), (3,4))
        Traceback (most recent call last):
          ...
        ValueError: Child sequence must immediately follow a non-sequence value when initializing a tree
        
        Similarly, trying to use 'None' as a tree value gives an error:
        >>> Tree(None, (1,2))
        Traceback (most recent call last):
          ...
        ValueError: None cannot be a tree element
        """
    
        pass
    
    
    def __iter__(self):
        """
        Iterates first level of tree returning nested tuples for childs
        """
    
        pass
    
    
    def __len__(self):
        """
        Returns the number of elements (nodes) in the tree.
        """
    
        pass
    
    
    def __ne__(self, other):
        pass
    
    
    def __nonzero__(self):
        pass
    
    
    def __reduce__(self):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __setitem__(self, element, value):
        """
        # Edit methods that are defined for mutable trees
        """
    
        pass
    
    
    def __str__(self):
        """
        # TODO: make it match new __init__
        # - use [] for child lists, () for value/children pairs
        """
    
        pass
    
    
    def __unicode__(self):
        pass
    
    
    def add(self, element, parent=None, next=None):
        """
        Add an element to self. parent and next element can be specified.
        Element will be added as a child of parent, parent can be any element or subtree of self:
        if parent is specified as a value there must exactly one match in self or an exception will be raised
        if parent is None, element will be added as a sibling of self's top node(s)
        if next is not none, element will be added before next in the childs of parent, else as a last childs
        """
    
        pass
    
    
    def breadth(self):
        """
        Breadth first traversal of a tree.
        """
    
        pass
    
    
    def child(self, index=0):
        """
        Returns nth child (by default first), is it exists
        """
    
        pass
    
    
    def childs(self):
        """
        Returns an iterator on all childs of self, or an empty iterator if self has no childs
        """
    
        pass
    
    
    def copy(self, cls=None):
        """
        Shallow copy of a tree.
        An extra class argument can be given to copy with a different
        (tree) class. No checks are made on the class.
        """
    
        pass
    
    
    def debug(self, depth=0):
        """
        Returns an detailed representation of the tree fro debug purposes
        """
    
        pass
    
    
    def depth(self):
        """
        Depth of self, the distance to self's root
        """
    
        pass
    
    
    def dist(self, element, **kwargs):
        """
        Returns distance from self to element, 0 means self==element, None if no path exists
        up keyword set to True means it will search ascendants(parent and parents of parent) self for element, default is False
        down keyword set to True means it will search descendants(childs and childs of childs) of self for element, default is False
        If neither up nor down is specified, will search both directions
        signed keyword set to true means returns negative distance when element is upwards self, positive when it's downwards
        """
    
        pass
    
    
    def formatted(self, returnList=False):
        """
        Returns an indented string representation of the tree
        """
    
        pass
    
    
    def get(self, value, default=()):
        """
        Identical to the __getitem__ method but will return a default value instead of raising KeyError
        if nor result is found
        """
    
        pass
    
    
    def graft(self, element, parent=None, next=None):
        """
        Attach element to self.
        If parent is secified, will be grafted as last child of parent (or before child 'next'),
        if parent is not in self, will raise an exception,
        if parent is None will be grafted at top level of self, besides any existing root(s).
        If next is specified, self will be grafted before next in the list of parent's childs,
        if next is not in parent's childs, will raise an exception,
        if next is None, self will be grafted as last child under parent.
        """
    
        pass
    
    
    def hasChilds(self):
        pass
    
    
    def height(self):
        """
        Get maximum downward depth (distance from element to furthest leaf downwards of it) of the tree
        """
    
        pass
    
    
    def isElement(self):
        pass
    
    
    def issubtree(self, other):
        pass
    
    
    def leaves(self):
        """
        Get an iterator on all leaves under self
        """
    
        pass
    
    
    def level(self, dist=0):
        """
        Get an iterator on all elements at the specified distance of self, negative distance means up, positive means down
        """
    
        pass
    
    
    def parents(self):
        """
        Returns an iterator on path from element to top root, starting with first parent, empty iterator means self is root
        """
    
        pass
    
    
    def path(self, element=None, **kwargs):
        """
        Returns an iterator of the path to specified element if found, including starting element,
        empty iterator means no path found.
        For trees where duplicate values are allowed, shortest path to an element of this value is returned.
        element can be an ancestor or a descendant of self, if no element is specified, will return path from self's root to self
        up keyword set to True means it will search ascendants(parent and parents of parent) self for element, default is False
        down keyword set to True means it will search descendants(childs and childs of childs) of self for element, default is False
        If neither up nor down is specified, will search both directions
        order keyword defines in what order the path will be returned and can be set to 'top', 'bottom' or 'self', order by default is 'top'
        'top' means path will be returned from ancestor to descendant
        'bottom' means path will be returned from descendant to ancestor
        'self' means path will be returned from self to element
        """
    
        pass
    
    
    def pop(self, element):
        """
        Delete top node of self and reparent all it's subtrees under it's current parent.
        If self was a root all it's subtrees become separate trees of a forest under the 'None' root.
        self will now have the new parent as top node
        """
    
        pass
    
    
    def postorder(self):
        """
        Postorder traversal of a tree.
        """
    
        pass
    
    
    def preorder(self):
        """
        The standard preorder traversal iterator.
        """
    
        pass
    
    
    def prune(self, element):
        """
        Ungrafts element from self, with everything under it
        """
    
        pass
    
    
    def remove(self, element):
        """
        Remove element from self, along with everything under it, will raise an exception if element is not in self
        """
    
        pass
    
    
    def reroot(self, element):
        """
        Reroot self so that element is self new top node
        """
    
        pass
    
    
    def root(self):
        """
        Root node of self, if self is a subtree, will travel up to top most node of containing tree
        """
    
        pass
    
    
    def siblings(self):
        """
        Returns an iterator on self siblings, not including self and starting with self next sibling,
        if self has no siblings (self has no parent or is unique child) then returns an empty iterator
        """
    
        pass
    
    
    def size(self):
        """
        Returns the number of elements (nodes) in the tree.
        """
    
        pass
    
    
    def sort(self, *args):
        pass
    
    
    def top(self, index=0):
        """
        The nth top node of self (by default first)
        """
    
        pass
    
    
    def tops(self):
        """
        Iterator on the top nodes of self, the subtrees that have no parent in self,
        will yield only self if self isn't a forest
        """
    
        pass
    
    
    def view(self):
        """
        Shortcut for print(self.formatted())
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    next = None
    
    parent = None
    
    value = None


class MetaTree(type):
    """
    This metaclass defines the type of all 'tree' classes
    """
    
    
    
    def __repr__(cls):
        pass
    
    
    def __str__(cls):
        pass
    
    
    def __unicode__(cls):
        pass
    
    
    def __new__(mcl, classname, bases, classdict):
        """
        # class creation using the method of the above class to populate a new class depending on
        # class creation options (mutable, indexed, etc)
        """
    
        pass
    
    
    TreeType = None
    
    ImTree = None
    
    
    IndexedPyTree = None
    
    
    MuTree = None
    
    
    NxTree = None
    
    
    PyTree = None



def isImmutableTree(x):
    pass


def isTree(x):
    pass


def mutabletree(f):
    """
    # decorator to identify mutable methods (that are only valid for mutable trees)
    """

    pass


def isMutableTree(x):
    pass


def treeFromDict(arg):
    """
    This function will build a tree from the provided dictionnary of child:parent relations :
        where each key represent an element and each key value represent the parent of that element, allows to build Trees form
        cmp(a,b): returns True if a is a direct child of b, False else.
        All elements must be present in the dictionnary keys, with root elements having None as value/parent
    """

    pass


def treeFromIsChild(isChildFn, *elements):
    """
    This function will build a tree from the provided sequence and a comparison function in the form:
        isChildFn(c,p): returns True if c is a child of p (direct or indirect), False otherwise
    
    The comparison function must satisfy the following conditions for all a, b, and c in the tree:
        isChildFn(a,a) == False
            (an object is not a child of itself)
        if isChildFn(a,b) AND isChildFn(b,c), then isChildFn(a,c)
            (indirect children are inherited)
        if isChildFn(a,b) AND isChildFn(a,c), then isChildFn(b,c) OR isChildFn(c,b) OR b==c
            (if a child has two distinct parents, then one must be the parent of the other)
    
    If any member of elements is itself a Tree, then it will be treated as a subtree (or subtrees, in the
    case of a forest) to be merged into the returned tree structure; for every root in such a subtree,
    the structure below the root will be unaltered, though the entire subtree itself may be parented to
    some other member of elements.
    
    >>> lst = ['aab', 'aba', 'aa', 'ba', 'bbb', 'a', 'b', 'bb', 'ab', 'bab', 'bba']
    >>> def isChild(s1, s2) :
    ...     return s1.startswith(s2)
    >>> a = treeFromIsChild (isChild, *lst)
    >>> a.sort()
    >>> print a.formatted()
    +: a
    |-+: aa
    | \--: aab
    \-+: ab
      \--: aba
    <BLANKLINE>
    +: b
    |-+: ba
    | \--: bab
    \-+: bb
      |--: bba
      \--: bbb
    """

    pass


def isSequence(x):
    pass


def treeFromChildLink(isExactChildFn, *args):
    """
    This function will build a tree from the provided sequence and a comparison function in the form:
        cmp(a,b): returns True if a is a direct child of b, False else
    
        >>> lst = ['aab', 'aba', 'aa', 'bbb', 'ba', 'b', 'a', 'bb', 'ab', 'bab', 'bba']
        >>> def isDirectChild(s1, s2) :
        ...     return s1.startswith(s2) and len(s1)==len(s2)+1
        >>> a = treeFromChildLink (isDirectChild, *lst)
        >>> a.sort()
        >>> print a.formatted()
        +: a
        |-+: aa
        | \--: aab
        \-+: ab
          \--: aba
        <BLANKLINE>
        +: b
        |-+: ba
        | \--: bab
        \-+: bb
          |--: bba
          \--: bbb
        >>>
        >>> # A child cannot have more than one parent, if the isChild is ambiguous an exception will be raised
        >>>
        >>> def isChild(s1, s2) :
        ...     return s1.startswith(s2)
        >>> failedTree = treeFromChildLink (isChild, *lst)
        Traceback (most recent call last):
            ...
        ValueError: A child in Tree cannot have multiple parents, check the provided isChild(c, p) function: 'isChild'
    """

    pass



networkxLoad = False

generators = None


