from __builtin__ import all as _all
from __builtin__ import min as _min
from __builtin__ import abs as _abs
from __builtin__ import max as _max
from pymel.util.arguments import isNumeric
from __builtin__ import any as _any
from __builtin__ import sum as _sum
from pymel.util.utilitytypes import metaReadOnlyAttr
from pymel.util.arguments import clsname
from pymel.util.utilitytypes import readonly

class Array(object):
    """
    A generic n-dimensional array class using nested lists for storage.
    
    Arrays can be built from numeric values, iterables, nested lists or other Array instances
    
    >>> Array()
    Array([])
    >>> Array(2)
    Array([2])
    >>> A = Array([[1, 2], [3, 4]])
    >>> print A.formated()
    [[1, 2],
     [3, 4]]
    >>> A = Array([1, 2], [3, 4])
    >>> print A.formated()
    [[1, 2],
     [3, 4]]
    >>> A = Array([[1, 2]])
    >>> print A.formated()
    [[1, 2]]
    >>> A = Array([1], [2], [3])
    >>> print A.formated()
    [[1],
     [2],
     [3]]
    >>> A = Array([[[1], [2], [3]]])
    >>> print A.formated()
    [[[1],
      [2],
      [3]]]
    
    You can query some Array characteristics with the properties shape, ndim (number of dimensions) and size,
    the total number of numeric components
    
    >>> A = Array(range(1, 10), shape=(3, 3))
    >>> print A.formated()
    [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]
    >>> A.shape
    (3, 3)
    >>> A.ndim
    2
    >>> A.size
    9
    
    Arrays are stored as nested lists and derive from the 'list' class.
    
    >>> A.data
    [Array([1, 2, 3]), Array([4, 5, 6]), Array([7, 8, 9])]
    >>> list(A)
    [Array([1, 2, 3]), Array([4, 5, 6]), Array([7, 8, 9])]
    
    Initialization from another Array does a shallow copy, not a deepcopy,
    unless the Array argument is resized / reshaped.
    
    >>> B = Array(A)
    >>> print B.formated()
    [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]
    >>> B == A
    True
    >>> B is A
    False
    >>> B[0] is A[0]
    True
    >>> C = Array([A])
    >>> print C.formated()
    [[[1, 2, 3],
      [4, 5, 6],
      [7, 8, 9]]]
    >>> C[0] is A
    True
    >>> C[0,0] is A[0]
    True
    
    You can pass optional shape information at creation with the keyword arguments
    shape, ndim and size. The provided data will be expanded to fit the desirable shape,
    either repeating it if it's a valid sub-array of the requested shape, or padding it with
    the Array default value (0 unless defined otherwise in an Array sub-class).
    
    Value will be repeated if it is a valid sub-array of the Array requested
    
    >>> A = Array(1, shape=(2, 2))
    >>> print A.formated()
    [[1, 1],
     [1, 1]]
    
    It will be padded otherwise, with the Array class default value
    
    >>> A = Array(1, 2, shape=(4,))
    >>> print A.formated()
    [1, 2, 0, 0]
    
    Or a combination of both, first pad it to a valid sub-array then repeat it
    
    >>> A = Array(1, 2, shape=(3, 3))
    >>> print A.formated()
    [[1, 2, 0],
     [1, 2, 0],
     [1, 2, 0]]
    
    Repeat can occur in any dimension
    
    >>> A = Array([1, 2, 3], shape=(3, 3))
    >>> print A.formated()
    [[1, 2, 3],
     [1, 2, 3],
     [1, 2, 3]]
    
    TODO :
    #>>> A = Array([[1], [2], [3]], shape=(3, 3))
    #>>> print A.formated()
    #[[1, 1, 1],
    # [2, 2, 2],
    # [3, 3, 3]]
    
    To avoid repetition, you can use a nested list of the desired number of dimensions
    
    >>> A = Array([1,2,3], shape=(3, 3))
    >>> print A.formated()
    [[1, 2, 3],
     [1, 2, 3],
     [1, 2, 3]]
    >>> A = Array([[1,2,3]], shape=(3, 3))
    >>> print A.formated()
    [[1, 2, 3],
     [0, 0, 0],
     [0, 0, 0]]
    
    If sub-array and requested array have same number of dimensions, padding with row / columns
    will be used (useful for the MatrixN sub-class or Array)
    
    >>> A = Array(range(1, 10), shape=(3, 3))
    >>> print A.formated()
    [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]
    >>> B = Array(A, shape=(4, 4))
    >>> print B.formated()
    [[1, 2, 3, 0],
     [4, 5, 6, 0],
     [7, 8, 9, 0],
     [0, 0, 0, 0]]
    
    Initialization will not allow to truncate data, if you provide more arguments than the
    requested array shape can fit, it will raise an exception.
    Use an explicit trim / resize or item indexing if you want to extract a sub-array
    
    >>> A = Array([1, 2, 3, 4, 5], shape=(2, 2))
    Traceback (most recent call last):
        ...
    TypeError: cannot initialize a Array of shape (2, 2) from [1, 2, 3, 4, 5] of shape (5,),
    as it would truncate data or reduce the number of dimensions
    """
    
    
    
    def __abs__(self):
        """
        a.__abs__() <==> abs(a)
        
        Element-wise absolute value of a.
        
        >>> A = Array([[complex(1, 2), complex(2, 3)], [complex(4, 5), complex(6, 7)]])
        >>> print abs(A).formated()
        [[2.2360679775, 3.60555127546],
         [6.40312423743, 9.21954445729]]
        >>> A = Array(-1, 2, -3)
        >>> print repr(abs(A))
        Array([1, 2, 3])
        """
    
        pass
    
    
    def __add__(self, other):
        """
        a.__add__(b) <==> a+b
        
        Returns the result of the element wise addition of a and b if b is convertible to Array,
        adds b to every component of a if b is a single numeric value
        
        Note : when the operands are 2 Arrays of different shapes, both are cast to the shape of largest size
        if possible. Created components are filled with class default value.
        
        Related : See the Array.__coerce__ method
        
        >>> A = Array(range(4), shape=(2, 2))
        >>> print (A).formated()
        [[0, 1],
         [2, 3]]
        >>> print (A+1).formated()
        [[1, 2],
         [3, 4]]
        >>> print (A+[1, 2]).formated()
        [[1, 3],
         [3, 5]]
        >>> A = Array(range(9), shape=(3, 3))
        >>> M = MatrixN(range(10, 50, 10), shape=(2, 2))
        >>> print (A+M).formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(A+M)
        MatrixN
        >>> A = Array(range(10, 50, 10), shape=(2, 2))
        >>> M = MatrixN(range(9), shape=(3, 3))
        >>> print (A+M).formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(A+M)
        MatrixN
        """
    
        pass
    
    
    def __coerce__(self, other):
        """
        coerce(a, b) -> (a1, b1)
        
        Return a tuple consisting of the two numeric arguments converted to
        a common type and shape, using the same rules as used by arithmetic operations.
        If coercion is not possible, return NotImplemented.
        
        b is cast to Array when possible
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> nA, nB = coerce(A, 1)
        >>> print nA.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> print nB.formated()
        [[1, 1, 1],
         [1, 1, 1],
         [1, 1, 1]]
        >>> nA, nB = coerce(A, [1, 2, 3])
        >>> print nA.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> print nB.formated()
        [[1, 2, 3],
         [1, 2, 3],
         [1, 2, 3]]
        
        Arguments can only be expanded, not truncated to avoid silent loss of data.
        
        >>> A = Array(range(4), shape=(2, 2))
        >>> nA, nB = coerce(A, [1, 2, 3, 4, 5])
        Traceback (most recent call last):
            ...
        TypeError: number coercion failed
        
        TODO : would be more explicit to get :
        TypeError: Array of shape (2, 2) and Array of shape (5,) cannot be converted to an common Array instance of same shape
        
        Arrays of dissimular shape are cast to same shape when possible, smallest size is cast to largest
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> B = Array(range(1, 5), shape=(2, 2))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> print B.formated()
        [[1, 2],
         [3, 4]]
        >>> nA, nB = coerce(A, B)
        >>> print nA.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> print nB.formated()
        [[1, 2, 0],
         [3, 4, 0],
         [0, 0, 0]]
        
        When coerce(x, y) is not doable, it defers to coerce(y, x)
        
        >>> nB, nA = coerce(B, A)
        >>> print nA.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> print nB.formated()
        [[1, 2, 0],
         [3, 4, 0],
         [0, 0, 0]]
        
        And does not raise an excepetion like :
            Traceback (most recent call last):
                ...
            TypeError: Array of shape (2, 2) and Array of shape (3, 3) cannot be converted to an common Array instance of same shape
        as it could be expected without this __coerce__ mechanism.
        
        When mixing Array derived types, result are cast to the first base class of either argument that accepts both shapes,
        ie 'deepest' derived class is tried first, MatrixN before Array, etc.
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> M = MatrixN(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> print M.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> nA, nM = coerce(A, M)
        >>> print repr(nA)
        MatrixN([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> print repr(nM)
        MatrixN([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> nM, nA = coerce(M, A)
        >>> print repr(nA)
        MatrixN([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> print repr(nM)
        MatrixN([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        
        This allows to implement a common behavior for element-wise arithmetics between Arrays of same
        or dissimilar shapes, Arrays and types derived from Arrays, Arrays and numerics or iterables of numerics.
        
        All operators on Arrays that take 2 operands and work element-wise follow the following rules :
        
        Operands are cast to Array when possible
        
        >>> A = Array(range(4), shape=(2, 2))
        >>> print (A).formated()
        [[0, 1],
         [2, 3]]
        >>> print (A+1).formated()
        [[1, 2],
         [3, 4]]
        >>> print (A+[1, 2]).formated()
        [[1, 3],
         [3, 5]]
        
        Operands can only be expanded, not truncated to avoid silent loss of data.
        
        >>> print (A+[1, 2, 3, 4, 5]).formated()
        Traceback (most recent call last):
            ...
        TypeError: unsupported operand type(s) for +: 'Array' and 'list'
        
        TODO : it would be more explicit to get more specific error messages, like :
            TypeError: Array of shape (2, 2) and Array of shape (5,) cannot be converted to an common Array instance of same shape
        
        Arrays of dissimilar shape are cast to same shape by Array.__coerce__ if possible.
        
        >>> A = Array(range(9), shape=(3, 3))
        >>> B = Array(range(10, 50, 10), shape=(2, 2))
        >>> print (A+B).formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(A+B)
        Array
        
        As Array.__coerce__ cannot truncate data, it will defer to the other operand's __coerce__ if it exists,
        then to its 'right operation' (here __radd__) method if it exists and is defined for an Array left operand.
        
        >>> A = Array(range(10, 50, 10), shape=(2, 2))
        >>> B = Array(range(9), shape=(3, 3))
        >>> print (A+B).formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(A+B)
        Array
        
        Result is cast to the first applicable Array herited type of either operand
        
        >>> A = Array(range(9), shape=(3, 3))
        >>> M = MatrixN(range(10, 50, 10), shape=(2, 2))
        >>> print (A+M).formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(A+M)
        MatrixN
        >>> print (M+A).formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(M+A)
        MatrixN
        
        >>> A = Array(range(10, 50, 10), shape=(2, 2))
        >>> M = MatrixN(range(9), shape=(3, 3))
        >>> print (A+M).formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(A+M)
        MatrixN
        >>> print (M+A).formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(M+A)
        MatrixN
        
        Here result is cast to Array as a MatrixN can't have 3 dimensions
        
        >>> A = Array(range(10, 190, 10), shape=(2, 3, 3))
        >>> M = MatrixN(range(9), shape=(3, 3))
        >>> print (A+M).formated()
        [[[10, 21, 32],
          [43, 54, 65],
          [76, 87, 98]],
        <BLANKLINE>
         [[100, 111, 122],
          [133, 144, 155],
          [166, 177, 188]]]
        >>> print clsname(A+M)
        Array
        >>> print (M+A).formated()
        [[[10, 21, 32],
          [43, 54, 65],
          [76, 87, 98]],
        <BLANKLINE>
         [[100, 111, 122],
          [133, 144, 155],
          [166, 177, 188]]]
        >>> print clsname(M+A)
        Array
        
        There are cases where no type coercion is possible, as it would truncate data or reduce number
        of dimensions in either way, use an explicit conversion (trim, size, etc.) in that case :
        
        >>> A = Array(range(8), shape=(2, 2, 2))
        >>> M = MatrixN(range(9), shape=(3, 3))
        >>> print (A+M).formated()
        Traceback (most recent call last):
            ...
        TypeError: unsupported operand type(s) for +: 'Array' and 'MatrixN'
        
        TODO : return some more explicit messages in these cases
        """
    
        pass
    
    
    def __contains__(self, value):
        """
        a.__contains__(b) <==> b in a
        
        Returns True if at least one of the sub-Arrays of a (down to individual components) is equal to b,
        False otherwise
        
        >>> A = Array(list(range(1, 6))+list(range(4, 0, -1)), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 4],
         [3, 2, 1]]
        >>> 5 in A
        True
        >>> [1, 2, 3] in A
        True
        >>> [1, 2] in A
        False
        >>> Array([[1, 2], [4, 5]]) in A
        False
        
        This behavior is unlike numpy arrays (where it would return True), but like builtin list
        
        >>> A in A
        False
        
        TODO :
        #>>> [1, 4, 3] in A
        #True
        #>>> [[1], [4], [3]] in A
        #True
        """
    
        pass
    
    
    def __delitem__(self, index):
        """
        a.__delitem__(index) <==> del a[index]
        
        Delete elements that match index from the Array.
        
        Note : as opposed to a.strip(index), do not collapse dimensions of the Array
        that end up with only one sub-array.
        
        >>> A = Array(xrange(1, 28), shape=(3, 3, 3))
        >>> print A.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[10, 11, 12],
          [13, 14, 15],
          [16, 17, 18]],
        <BLANKLINE>
         [[19, 20, 21],
          [22, 23, 24],
          [25, 26, 27]]]
        >>> A.shape
        (3, 3, 3)
        >>> S = A[0]
        >>> del A[1]
        >>> print A.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[19, 20, 21],
          [22, 23, 24],
          [25, 26, 27]]]
        >>> A.shape
        (2, 3, 3)
        >>> S == A[0]
        True
        >>> S is A[0]
        True
        >>> del A[-1]
        >>> print A.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]]
        >>> A.shape
        (1, 3, 3)
        >>> del A[None, None, 1:3]
        >>> print A.formated()
        [[[1],
          [4],
          [7]]]
        >>> A.shape
        (1, 3, 1)
        >>> del A[None, 1:3]
        >>> print A.formated()
        [[[1]]]
        >>> A.shape
        (1, 1, 1)
        >>> del A[-1]
        >>> print A.formated()
        []
        >>> A.shape
        (0,)
        """
    
        pass
    
    
    def __delslice__(self, start):
        """
        deprecated and __setitem__ should accept slices anyway
        """
    
        pass
    
    
    def __div__(self, other):
        """
        a.__div__(b) <==> a/b
        The division operator (/) is implemented by these methods. The __truediv__() method is used
        when __future__.division is in effect, otherwise __div__() is used.
        Returns the result of the element wise division of a by b if b is convertible to Array,
        divides every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __eq__(self, other):
        """
        a.__equ__(b) <==> a == b
        
        Equivalence operator, will only work for exact same type of a and b, check isEquivalent method to have it
        convert a and b to a common type (if possible).
        
        >>> Array(range(4), shape=(4)) == Array(range(4), shape=(1, 4))
        False
        >>> Array(range(4), shape=(2, 2)) == Array(range(4), shape=(2, 2))
        True
        >>> Array(range(4), shape=(2, 2)) == MatrixN(range(4), shape=(2, 2))
        False
        """
    
        pass
    
    
    def __floordiv__(self, other):
        """
        a.__floordiv__(b) <==> a//b
        Returns the result of the element wise floor division of a by b if b is convertible to Array,
        performs floor division of every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __getitem__(self, index):
        """
        a.__getitem__(index) <==> a[index]
        
        Get Array element from either a single (integer) or multiple (tuple) indices, supports slices.
        
        Note : __getitem__ returns reference that can be modified unless the sub-array had to be reconstructed.
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> print repr(A[0])
        Array([1, 2, 3])
        >>> print repr(A[-1])
        Array([7, 8, 9])
        >>> print repr(A[0, 0])
        1
        >>> print repr(A[-1, -1])
        9
        
        Multiple indices and slices are supported :
        
        >>> B = A[0:2, 0:2]
        >>> print B.formated()
        [[1, 2],
         [4, 5]]
        
        When sub-arrays are not broken / rebuilt by requested indexing, a reference is returned :
        
        >>> B = A[0:2]
        >>> print B.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        >>> B[0] == A[0]
        True
        >>> B[0] is A[0]
        True
        
        Missing indices are equivalent to slice(None), noted ':', but as with list, a[:] returns
        a copy of a, not a reference to a.
        
        >>> B = A[0:2, :]
        >>> print B.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        >>> B[0] == A[0]
        True
        >>> B[0] is A[0]
        False
        
        When sub-arrays are rebuilt, result is a copy.
        
        >>> B = A[:, 0:2]
        >>> print B.formated()
        [[1, 2],
         [4, 5],
         [7, 8]]
        >>> print repr(B[:,0])
        Array([1, 4, 7])
        >>> B[:,0] == A[:, 0]
        True
        >>> B[:,0] is A[:, 0]
        False
        
        Use __setindex__ to change the value of an indexed element in that case
        
        >>> A[:, 0:2] += 10
        >>> print A.formated()
        [[11, 12, 3],
         [14, 15, 6],
         [17, 18, 9]]
        """
    
        pass
    
    
    def __getnewargs__(self):
        pass
    
    
    def __getslice__(self, start, end):
        """
        Deprecated and __getitem__ should accept slices anyway
        """
    
        pass
    
    
    def __iadd__(self, other):
        """
        a.__iadd__(b) <==> a += b
        
        In place addition of a and b, see __add__, result must fit a's type
        
        >>> A = Array(range(9), shape=(3, 3))
        >>> M = MatrixN(range(10, 50, 10), shape=(2, 2))
        >>> A += M
        >>> print A.formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(A)
        Array
        >>> A = Array(range(9), shape=(3, 3))
        >>> M = MatrixN(range(10, 50, 10), shape=(2, 2))
        >>> M += A
        >>> print M.formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(M)
        MatrixN
        
        Result must be castable to the type of a
        
        >>> A = Array(range(12), shape=(2, 3, 2))
        >>> M = MatrixN(range(9), shape=(3, 3))
        >>> B = M + A
        >>> print B.formated()
        [[[0, 2],
          [4, 6],
          [8, 10]],
        <BLANKLINE>
         [[12, 14],
          [16, 9],
          [10, 11]]]
        >>> print clsname(B)
        Array
        >>> M += A
        Traceback (most recent call last):
            ...
        TypeError: cannot cast a Array of shape (2, 3, 2) to a MatrixN of shape (2, 6),
        as it would truncate data or reduce the number of dimensions
        """
    
        pass
    
    
    def __idiv__(self, other):
        """
        a.__idiv__(b) <==> a /= b
        The division operator (/) is implemented by these methods. The __truediv__() method is used
        when __future__.division is in effect, otherwise __div__() is used.
        In place division of a by b, see __div__, result must fit a's type
        """
    
        pass
    
    
    def __ifloordiv__(self, other):
        """
        a.__ifloordiv__(b) <==> a //= b
        In place true division of a by b, see __floordiv__, result must fit a's type
        """
    
        pass
    
    
    def __imod__(self, other):
        """
        a.__imod__(b) <==> a %= b
        In place modulo of a by b, see __mod__, result must fit a's type
        """
    
        pass
    
    
    def __imul__(self, other):
        """
        a.__imul__(b) <==> a *= b
        In place multiplication of a and b, see __mul__, result must fit a's type
        """
    
        pass
    
    
    def __init__(self, *args, **kwargs):
        """
        a.__init__(...)
        
        Initializes Array a from one or more iterable, nested lists or numeric values,
        See Array, MatrixN or VectorN help for more information.
        
        Note : __init__ from another Array acts as a shallow copy, not a deepcopy, unless
        the Array argument is resized or reshaped.
        """
    
        pass
    
    
    def __invert__(self):
        """
        a.__invert__() <==> ~a
        
        Element-wise invert of a, as with '~', operator 'invert'
        
        >>> A = Array(range(4), shape=(2, 2))
        >>> print (~A).formated()
        [[-1, -2],
         [-3, -4]]
        """
    
        pass
    
    
    def __ipow__(self, other, modulo=None):
        """
        a.__ipow__(b[, modulo]) <==> a**=b or a = (a**b) % modulo
        In place elevation to power of a by b, see __pow__, result must fit a's type
        """
    
        pass
    
    
    def __isub__(self, other):
        """
        a.__isub__(b) <==> a -= b
        In place substraction of a and b, see __sub__, result must fit a's type
        """
    
        pass
    
    
    def __iter__(self, *args, **kwargs):
        """
        a.__iter__(*args, **kwargs) <==> iter(a, *args, **kwargs)
        
        Default Array storage class iterator, operates on first axis only
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> [a for a in A]
        [Array([1, 2, 3]), Array([4, 5, 6]), Array([7, 8, 9])]
        """
    
        pass
    
    
    def __itruediv__(self, other):
        """
        a.__itruediv__(b) <==> a /= b
        In place true division of a by b, see __truediv__, result must fit a's type
        """
    
        pass
    
    
    def __len__(self):
        """
        a.__len__() <==> len(a)
        
        Length of the first dimension of the array, ie len of the array considered as the top level list,
        thus len(a) == a.shape[0].
        
        >>> Array(shape=(3, 2)).__len__()
        3
        """
    
        pass
    
    
    def __mod__(self, other):
        """
        a.__mod__(b) <==> a%b
        Returns the result of the element wise modulo of a by b if b is convertible to Array,
        performs modulo of every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __mul__(self, other):
        """
        a.__mul__(b) <==> a*b
        Returns the result of the element wise multiplication of a and b if b is convertible to Array,
        multiplies every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __ne__(self, other):
        """
        a.__ne__(b) <==> a != b
        
        a.__ne__(b) returns not a.__equ__(b).
        
        >>> Array(range(4), shape=(4)) != Array(range(4), shape=(1, 4))
        True
        >>> Array(range(4), shape=(2, 2)) != Array(range(4), shape=(2, 2))
        False
        >>> Array(range(4), shape=(2, 2)) != MatrixN(range(4), shape=(2, 2))
        True
        """
    
        pass
    
    
    def __neg__(self):
        """
        a.__neg__() <==> -a
        
        Element-wise negation of a
        
        >>> A = Array(range(4), shape=(2, 2))
        >>> print (-A).formated()
        [[0, -1],
         [-2, -3]]
        """
    
        pass
    
    
    def __neq__(self, other):
        """
        a.__ne__(b) <==> a != b
        
        a.__ne__(b) returns not a.__equ__(b).
        
        >>> Array(range(4), shape=(4)) != Array(range(4), shape=(1, 4))
        True
        >>> Array(range(4), shape=(2, 2)) != Array(range(4), shape=(2, 2))
        False
        >>> Array(range(4), shape=(2, 2)) != MatrixN(range(4), shape=(2, 2))
        True
        """
    
        pass
    
    
    def __pos__(self):
        """
        a.__pos__() <==> +a
        
        Element-wise positive of a
        
        >>> A = Array(range(4), shape=(2, 2))
        >>> print (+A).formated()
        [[0, 1],
         [2, 3]]
        """
    
        pass
    
    
    def __pow__(self, other, modulo=None):
        """
        a.__pow__(b[, modulo]) <==> a**b or (a**b) % modulo
        With two arguments, equivalent to a**b.  With three arguments, equivalent to (a**b) % modulo, but may be more efficient (e.g. for longs).
        Returns the result of the element wise elevation to power of a by b if b is convertible to Array,
        elevates every component of a to power b if b is a single numeric value
        """
    
        pass
    
    
    def __radd__(self, other):
        """
        a.__radd__(b) <==> b+a
        
        Returns the result of the element wise addition of a and b if b is convertible to Array,
        adds b to every component of a if b is a single numeric value
        
        Note : when the operands are 2 Arrays of different shapes, both are cast to the shape of largest size
        if possible. Created components are filled with class default value.
        
        Related : See the Array.__coerce__ method
        
        >>> A = Array(range(4), shape=(2, 2))
        >>> print (A).formated()
        [[0, 1],
         [2, 3]]
        >>> print (1+A).formated()
        [[1, 2],
         [3, 4]]
        >>> print ([1, 2]+A).formated()
        [[1, 3],
         [3, 5]]
        >>> A = Array(range(9), shape=(3, 3))
        >>> M = MatrixN(range(10, 50, 10), shape=(2, 2))
        >>> print (M+A).formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(M+A)
        MatrixN
        >>> A = Array(range(10, 50, 10), shape=(2, 2))
        >>> M = MatrixN(range(9), shape=(3, 3))
        >>> print (M+A).formated()
        [[10, 21, 2],
         [33, 44, 5],
         [6, 7, 8]]
        >>> print clsname(M+A)
        MatrixN
        """
    
        pass
    
    
    def __rdiv__(self, other):
        """
        a.__rdiv__(b) <==> b/a
        The division operator (/) is implemented by these methods. The __truediv__() method is used
        when __future__.division is in effect, otherwise __div__() is used.
        Returns the result of the element wise division of b by a if b is convertible to Array,
        replaces every component c of a by b/c if b is a single numeric value
        """
    
        pass
    
    
    def __reduce__(self):
        """
        __reduce__ is defined to allow pickling of Arrays
        """
    
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __rfloordiv__(self, other):
        """
        a.__rfloordiv__(b) <==> b//a
        Returns the result of the element wise floor division of b by a if b is convertible to Array,
        replaces every component c of a by b//c if b is a single numeric value
        """
    
        pass
    
    
    def __rmod__(self, other):
        """
        a.__rmod__(b) <==> b%a
        Returns the result of the element wise modulo of b by a if b is convertible to Array,
        replaces every component c of a by b%c if b is a single numeric value
        """
    
        pass
    
    
    def __rmul__(self, other):
        """
        a.__mul__(b) <==> b*a
        Returns the result of the element wise multiplication of a and b if b is convertible to Array,
        multiplies every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __round__(self, ndigits=0):
        """
        a.__round__([ndigits]) <==> round(a[, ndigits])
        
        Element-wise round to given precision in decimal digits (default 0 digits).
        This always returns an Array of floating point numbers.  Precision may be negative.
        
        >>> A = Array([1.0/x for x in range(1, 10)], shape=(3, 3))
        >>> print round(A, 2).formated()
        [[1.0, 0.5, 0.33],
         [0.25, 0.2, 0.17],
         [0.14, 0.13, 0.11]]
        """
    
        pass
    
    
    def __rpow__(self, other):
        """
        a.__rpow__(b[, modulo]) <==> b**a or (b**a) % modulo
        With two arguments, equivalent to b**a.  With three arguments, equivalent to (b**a) % modulo, but may be more efficient (e.g. for longs).
        Returns the result of the element wise elevation to power of b by a if b is convertible to Array,
        replaces every component c of a by b elevated to power c if b is a single numeric value
        """
    
        pass
    
    
    def __rsub__(self, other):
        """
        a.__rsub__(b) <==> b-a
        Returns the result of the element wise substraction of a from b if b is convertible to Array,
        replace every component c of a by b-c if b is a single numeric value
        """
    
        pass
    
    
    def __rtruediv__(self, other):
        """
        a.__rtruediv__(b) <==> b/a
        The division operator (/) is implemented by these methods. The __rtruediv__() method is used
        when __future__.division is in effect, otherwise __rdiv__() is used.
        Returns the result of the element wise true division of b by a if b is convertible to Array,
        replaces every component c of a by b/c if b is a single numeric value
        """
    
        pass
    
    
    def __setitem__(self, index, value):
        """
        a.__setitem__(index, value) <==> a[index] = value
        
        Set Array element from either a single (integer) or multiple (tuple) indices, supports slices.
        
        Note : if value is not reshaped / resized, it's a reference to value that is set at the indexed element,
        use an explicit deepcopy
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        
        If value doesn't have to be rebuilt, the indexed elements will hold a reference to value, otherwise a copy
        
        >>> S = Array([0, 0, 0])
        >>> A[0] = S
        >>> print A.formated()
        [[0, 0, 0],
         [4, 5, 6],
         [7, 8, 9]]
        >>> A[0] == S
        True
        >>> A[0] is S
        True
        >>> A[:, 2] = S
        >>> print A.formated()
        [[0, 0, 0],
         [4, 5, 0],
         [7, 8, 0]]
        >>> A[:, 2] == S
        True
        >>> A[:, 2] is S
        False
        
        Multiple indices and slices are supported :
        
        >>> A[0] = [2, 4, 6]
        >>> print A.formated()
        [[2, 4, 6],
         [4, 5, 0],
         [7, 8, 0]]
        >>> A[1, 1] = 10
        >>> print A.formated()
        [[2, 4, 6],
         [4, 10, 0],
         [7, 8, 0]]
        >>> A[:, -1] = [7, 8, 9]
        >>> print A.formated()
        [[2, 4, 7],
         [4, 10, 8],
         [7, 8, 9]]
        >>> A[:, 0:2] += 10
        >>> print A.formated()
        [[12, 14, 7],
         [14, 20, 8],
         [17, 18, 9]]
        
        Value is expanded / repeated as necessary to fit the indexed sub-array
        
        >>> A[0:2, 0:2] = 1
        >>> print A.formated()
        [[1, 1, 7],
         [1, 1, 8],
         [17, 18, 9]]
        >>> A[1:3, :] = [1, 2]
        >>> print A.formated()
        [[1, 1, 7],
         [1, 2, 0],
         [1, 2, 0]]
        >>> A[0:2, 1:3] = [1, 2]
        >>> print A.formated()
        [[1, 1, 2],
         [1, 1, 2],
         [1, 2, 0]]
        >>> A[0:2, 1:3] = [[1], [2]]
        >>> print A.formated()
        [[1, 1, 0],
         [1, 2, 0],
         [1, 2, 0]]
        
        It cannot be truncated however
        
        >>> A[0] = [1, 2, 3, 4]
        Traceback (most recent call last):
            ...
        ValueError: shape mismatch between value(s) and Array components or sub Arrays designated by the indexing
        """
    
        pass
    
    
    def __setslice__(self, start, end, value):
        """
        Deprecated and __setitem__ should accept slices anyway
        """
    
        pass
    
    
    def __str__(self):
        """
        # display
        """
    
        pass
    
    
    def __sub__(self, other):
        """
        a.__sub__(b) <==> a-b
        Returns the result of the element wise substraction of b from a if b is convertible to Array,
        substracts b from every component of a if b is a single numeric value
        """
    
        pass
    
    
    def __truediv__(self, other):
        """
        a.__truediv__(b) <==> a/b
        The division operator (/) is implemented by these methods. The __truediv__() method is used
        when __future__.division is in effect, otherwise __div__() is used.
        Returns the result of the element wise true division of a by b if b is convertible to Array,
        performs true division of every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __unicode__(self):
        pass
    
    
    def all(self, *args, **kwargs):
        """
        a.all([axis0[, axis1[, ...]]]) <=> all(a, axis=(axis0, axis1, ...))
        
        Returns True if all the components of iterable a evaluate to True.
        If axis are specified will return an Array of all(x) for x in a.axisiter(*axis).
        
        >>> A = Array([[True,True,True],[False,True,False]])
        >>> print A.formated()
        [[True, True, True],
         [False, True, False]]
        >>> A.all()
        False
        >>> A.all(0, 1)
        False
        >>> A.all(0)
        Array([False, True, False])
        >>> A.all(1)
        Array([True, False])
        """
    
        pass
    
    
    def any(self, *args, **kwargs):
        """
        a.any([axis0[, axis1[, ...]]]) <=> any(a, axis=(axis0, axis1, ...))
        
        Returns True if any of the components of iterable a evaluate to True.
        If axis are specified will return an Array of any(x) for x in a.axisiter(*axis).
        
        >>> A = Array([[False,True,True],[False,True,False]])
        >>> print A.formated()
        [[False, True, True],
         [False, True, False]]
        >>> A.any()
        True
        >>> A.any(0, 1)
        True
        >>> A.any(0)
        Array([False, True, True])
        >>> A.any(1)
        Array([True, True])
        """
    
        pass
    
    
    def append(self, other, axis=0):
        """
        a.append(b[, axis=0])
        
        Modifies a by appending b at its end, as iterated on axis.
        
        Note : does not work as list append and appends a copy (deepcopy) of b, not a reference to b. However a is appended in place.
        
        Examples:
        
        >>> A = Array([])
        >>> print repr(A)
        Array([])
        >>> A.append(1)
        >>> print A.formated()
        [1]
        >>> A.append(2)
        >>> print A.formated()
        [1, 2]
        >>> A = Array([A])
        >>> print A.formated()
        [[1, 2]]
        >>> A.append([4, 5], axis=0)
        >>> print A.formated()
        [[1, 2],
         [4, 5]]
        >>> A.append([3, 6], axis=1)
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        >>> A.append([7, 8, 9])
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> B = Array([A])
        >>> B.append(A)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]]
        >>> B[0] == B[1]
        True
        >>> B[0] is B[1]
        False
        >>> A == B[0]
        True
        >>> A is B[0]
        True
        >>> B.append([0, 0, 0], axis=1)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          [0, 0, 0]],
        <BLANKLINE>
         [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          [0, 0, 0]]]
        >>> B.append([0, 0, 0, 1], axis=2)
        >>> print B.formated()
        [[[1, 2, 3, 0],
          [4, 5, 6, 0],
          [7, 8, 9, 0],
          [0, 0, 0, 1]],
        <BLANKLINE>
         [[1, 2, 3, 0],
          [4, 5, 6, 0],
          [7, 8, 9, 0],
          [0, 0, 0, 1]]]
        """
    
        pass
    
    
    def appended(self, other, axis=0):
        """
        a.appended(b[, axis=0]) --> Array
        
        Returns the Array obtained by appending b at the end of a as iterated on axis.
        
        Note : returns a deepcopy of a.appends(b[, axis=0]).
        
        Examples:
        
        >>> A = Array([])
        >>> print repr(A)
        Array([])
        >>> A = A.appended(1)
        >>> print A.formated()
        [1]
        >>> A = A.appended(2)
        >>> print A.formated()
        [1, 2]
        >>> A = Array([A])
        >>> print A.formated()
        [[1, 2]]
        >>> A = A.appended([4, 5], axis=0)
        >>> print A.formated()
        [[1, 2],
         [4, 5]]
        >>> A = A.appended([3, 6], axis=1)
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        >>> A = A.appended([7, 8, 9])
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> B = Array([A]).appended(A)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]]
        >>> B[0] == B[1]
        True
        >>> B[0] is B[1]
        False
        >>> A == B[0]
        True
        >>> A is B[0]
        False
        >>> B = B.appended([0, 0, 0], axis=1)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          [0, 0, 0]],
        <BLANKLINE>
         [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          [0, 0, 0]]]
        >>> B = B.appended([0, 0, 0, 1], axis=2)
        >>> print B.formated()
        [[[1, 2, 3, 0],
          [4, 5, 6, 0],
          [7, 8, 9, 0],
          [0, 0, 0, 1]],
        <BLANKLINE>
         [[1, 2, 3, 0],
          [4, 5, 6, 0],
          [7, 8, 9, 0],
          [0, 0, 0, 1]]]
        """
    
        pass
    
    
    def assign(self, value):
        """
        a.assign(b) --> Array
        
        Assigns the value of b to a, equivalent to using the data property : a.data = b.
        Besides changing a's value, it also returns the new a to conform to Maya's api assign.
        
        Note: assign acts as a shallow copy
        
        >>> A = Array(range(1, 5), shape=(2, 2))
        >>> B = Array()
        >>> B.assign(A)
        Array([[1, 2], [3, 4]])
        >>> print B.formated()
        [[1, 2],
         [3, 4]]
        >>> B == A
        True
        >>> B is A
        False
        >>> B[0] is A[0]
        True
        """
    
        pass
    
    
    def axisiter(self, *args):
        """
        a.axisiter([axis1[, axis2[, ...]]]) --> ArrayIter
        
        Returns an iterator using a specific axis or list of ordered axis.
        It is equivalent to transposing the Array using these ordered axis and iterating
        on the new Array for the remaining sub array dimension
        
        Note : ArrayIter ierators support __len__, __getitem__ and __setitem__
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> [a for a in A]
        [Array([1, 2, 3]), Array([4, 5, 6]), Array([7, 8, 9])]
        >>> [a for a in A.axisiter(0)]
        [Array([1, 2, 3]), Array([4, 5, 6]), Array([7, 8, 9])]
        >>> [a for a in A.axisiter(1)]
        [Array([1, 4, 7]), Array([2, 5, 8]), Array([3, 6, 9])]
        >>> [a for a in A.axisiter(0,1)]
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> [a for a in A.axisiter(1,0)]
        [1, 4, 7, 2, 5, 8, 3, 6, 9]
        """
    
        pass
    
    
    def blend(self, other, weight=0.5):
        """
        a.blend(b[, weight=0.5]) <==> blend(a, b[, weights=0.5])
        
        Returns the result of blending from Array instance u to v according to
        either a scalar weight where blend will yield a*(1-weight) + b*weight Array,
        or a an iterable of independent weights.
        
        >>> A = Array(0, shape=(2, 2))
        >>> print A.formated()
        [[0, 0],
         [0, 0]]
        >>> B = Array(1, shape=(2, 2))
        >>> print B.formated()
        [[1, 1],
         [1, 1]]
        >>> print A.blend(B, weight=0.5).formated()
        [[0.5, 0.5],
         [0.5, 0.5]]
        >>> print blend(A, B).formated()
        [[0.5, 0.5],
         [0.5, 0.5]]
        >>> print blend(A, B, weight=[x/4.0 for x in range(4)]).formated()
        [[0.0, 0.25],
         [0.5, 0.75]]
        >>> print blend(A, B, weight=[[0.0, 0.25],[0.75, 1.0]]).formated()
        [[0.0, 0.25],
         [0.75, 1.0]]
        """
    
        pass
    
    
    def clamp(self, low=0, high=1):
        """
        a.clamp([low=0[, high=1]]) <==> clamp (a, low, high)
        
        Returns the result of clamping each component of a between low and high if low and high are scalars,
        or the corresponding components of low and high if low and high are sequences of scalars
        
        >>> A = Array(range(4), shape=(2, 2))
        >>> print A.formated()
        [[0, 1],
         [2, 3]]
        >>> print A.clamp(1, 2).formated()
        [[1, 1],
         [2, 2]]
        >>> print clamp(A, 1, 2).formated()
        [[1, 1],
         [2, 2]]
        >>> print clamp(A, 0.0, [x/4.0 for x in range(4)]).formated()
        [[0, 0.25],
         [0.5, 0.75]]
        """
    
        pass
    
    
    def conjugate(self):
        """
        a.conjugate() <==> conjugate(a)
        
        Returns the element-wise complex.conjugate() of the Array.
        
        >>> A = Array([[complex(1, 2), complex(2, 3)], [complex(4, 5), complex(6, 7)]])
        >>> print A.formated()
        [[(1+2j), (2+3j)],
         [(4+5j), (6+7j)]]
        >>> print A.conjugate().formated()
        [[(1-2j), (2-3j)],
         [(4-5j), (6-7j)]]
        >>> print conjugate(A).formated()
        [[(1-2j), (2-3j)],
         [(4-5j), (6-7j)]]
        >>> A = Array(range(1, 5), shape=(2, 2))
        >>> print conjugate(A).formated()
        [[1, 2],
         [3, 4]]
        """
    
        pass
    
    
    def copy(self):
        """
        a.copy() <==> copy.copy(a)
        
        Returns a shallow copy of a
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> B = A.copy()
        >>> print B.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> print B == A
        True
        >>> print B is A
        False
        >>> print B[0] == A[0]
        True
        >>> print B[0] is A[0]
        True
        """
    
        pass
    
    
    def count(self, value):
        """
        a.count(b) --> int
        
        Returns the number of occurrences of b in a.
        
        >>> A = Array(list(range(1, 6))+list(range(4, 0, -1)), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 4],
         [3, 2, 1]]
        >>> A.count(5)
        1
        >>> A.count(4)
        2
        >>> A.count([1, 2, 3])
        1
        >>> A.count([1, 2])
        0
        """
    
        pass
    
    
    def deepcopy(self):
        """
        a.deepcopy() <==> copy.deepcopy(a)
        
        Returns a deep copy of a
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> B = A.deepcopy()
        >>> print B.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> print B == A
        True
        >>> print B is A
        False
        >>> print B[0] == A[0]
        True
        >>> print B[0] is A[0]
        False
        """
    
        pass
    
    
    def deleted(self, *args):
        """
        a.deleted(index) --> Array
        
        Returns a copy (deepcopy) of a with the elements designated by index deleted,
        as in a.__delitem__(index).
        
        Note : as opposed to a.stripped(index), do not collapse dimensions of the Array
        that end up with only one sub-array.
        
        >>> A = Array(xrange(1, 28), shape=(3, 3, 3))
        >>> print A.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[10, 11, 12],
          [13, 14, 15],
          [16, 17, 18]],
        <BLANKLINE>
         [[19, 20, 21],
          [22, 23, 24],
          [25, 26, 27]]]
        >>> A.shape
        (3, 3, 3)
        >>> B = A.deleted(1)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[19, 20, 21],
          [22, 23, 24],
          [25, 26, 27]]]
        >>> B.shape
        (2, 3, 3)
        >>> B[0] == A[0]
        True
        >>> B[0] is A[0]
        False
        >>> B = B.deleted(-1)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]]
        >>> B.shape
        (1, 3, 3)
        >>> B = B.deleted(None, None, slice(1, 3))
        >>> print B.formated()
        [[[1],
          [4],
          [7]]]
        >>> B.shape
        (1, 3, 1)
        >>> B = B.deleted((None, slice(1, 3)))
        >>> print B.formated()
        [[[1]]]
        >>> B.shape
        (1, 1, 1)
        >>> B = B.deleted(-1)
        >>> print B.formated()
        []
        >>> B.shape
        (0,)
        """
    
        pass
    
    
    def dist(self, other, *args):
        """
        a.dist(b, axis0, axis1, ...) <==> dist(a, b[, axis=(axis0, axis1, ...)])
        
        Returns the distance between a and b, ie length(b-a, axis)
        
        >>> A = Array([[0.5, 0.5, -0.707],[0.707, -0.707, 0.0]])
        >>> print A.formated()
        [[0.5, 0.5, -0.707],
         [0.707, -0.707, 0.0]]
        >>> B = Array([[0.51, 0.49, -0.71],[0.71, -0.70, 0.0]])
        >>> print B.formated()
        [[0.51, 0.49, -0.71],
         [0.71, -0.7, 0.0]]
        >>> A.dist(B)
        0.016340134638368205
        >>> A.dist(B, 0, 1)
        0.016340134638368205
        >>> A.dist(B, 0)
        Array([0.0144568322948, 0.00761577310586])
        >>> A.dist(B, 1)
        Array([0.0104403065089, 0.0122065556157, 0.003])
        """
    
        pass
    
    
    def distanceTo(self, other):
        """
        a.distanceTo(b) <==> a.dist(b)
        
        Equivalent to the dist method, for compatibility with Maya's API. Does not take axis arguements
        """
    
        pass
    
    
    def extend(self, other):
        """
        a.vstack(b) <==> a.stack(b, axis=0)
        
        Modifies a by concatenating b at its end, as iterated on first axis.
        For a 2 dimensional Array/MatrixN, it stacks a and b vertically
        
        >>> A = Array([[1, 2], [3, 4]])
        >>> print A.formated()
        [[1, 2],
         [3, 4]]
        >>> A.vstack([[5, 6]])
        >>> print A.formated()
        [[1, 2],
         [3, 4],
         [5, 6]]
        """
    
        pass
    
    
    def extended(self, other):
        """
        a.vstacked(b) <==> a.stacked(b, axis=0)
        
        Returns the Array obtained by concatenating a and b on first axis.
        For a 2 dimensional Array/MatrixN, it stacks a and b vertically.
        
        >>> A = Array([[1, 2], [3, 4]])
        >>> print A.formated()
        [[1, 2],
         [3, 4]]
        >>> A = A.vstacked([[5, 6]])
        >>> print A.formated()
        [[1, 2],
         [3, 4],
         [5, 6]]
        """
    
        pass
    
    
    def fill(self, value=None):
        """
        a.fill([value])
        
        Fills the array in place with the given value, if no value is given a is filled with the default class values
        
        Note : value is copied (deepcopy) as many times as it is inserted in a, not referenced.
        
        Examples:
        
        >>> A = Array(shape=(3, 3))
        >>> print A.formated()
        [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]]
        >>> A.fill(10)
        >>> print A.formated()
        [[10, 10, 10],
         [10, 10, 10],
         [10, 10, 10]]
        >>> A.fill()
        >>> print A.formated()
        [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]]
        >>> A.fill([1, 2])
        >>> print A.formated()
        [[1, 2, 0],
         [1, 2, 0],
         [1, 2, 0]]
        >>> A.fill([1, 2, 3])
        >>> print A.formated()
        [[1, 2, 3],
         [1, 2, 3],
         [1, 2, 3]]
        >>> A[0] == A[-1]
        True
        >>> A[0] is A[-1]
        False
        """
    
        pass
    
    
    def filled(self, value=None):
        """
        a.filled([value]) --> Array
        
        Returns a copy (deepcopy) of a, filled with value for a's shape. If no value is given, a is filled with the class default.
        value will be expended with the class default values to the nearest matching sub array of a, then repeated.
        value can't be truncated and will raise an error if of a size superior to the size of the nearest matching sub array
        of the class, to avoid improper casts.
        
        Note : value is copied (deepcopy) as many times as it is inserted in a, not referenced.
        
        Examples:
        
        >>> Array(shape=(5,)).filled([0, 1, 2])
        Array([0, 1, 2, 0, 0])
        >>> Array(shape=(5,)).filled(2)
        Array([2, 2, 2, 2, 2])
        >>> print Array(shape=(2, 2)).filled(1).formated()
        [[1, 1],
         [1, 1]]
        >>> A = Array(shape=(3, 3)).filled([1, 2, 3])
        >>> print A.formated()
        [[1, 2, 3],
         [1, 2, 3],
         [1, 2, 3]]
        >>> A[0] == A[-1]
        True
        >>> A[0] is A[-1]
        False
        >>> A = Array(shape=(3, 3)).filled([1, 2])
        >>> print A.formated()
        [[1, 2, 0],
         [1, 2, 0],
         [1, 2, 0]]
        >>> Array(shape=(2, 2)).filled([1, 2, 3])
        Traceback (most recent call last):
            ...
        ValueError: value of shape (3,) cannot be fit in a Array of shape (2, 2), some data would be lost
        """
    
        pass
    
    
    def fit(self, other):
        """
        a.fit(b)
        
        Fits the Array b in a.
        For every component of a that exists in b (there is a component of same coordinates in b),
        replace it with the value of the corresponding component in b.
        Both Arrays a and b must have same number of dimensions.
        
        Note : copies (deepcopy) of b sub-arrays are fit in a, not references, but modification of a is done in-place.
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> B = Array(shape=(4, 3))
        >>> print B.formated()
        [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]]
        >>> S = B[-1]
        >>> B.fit(A)
        >>> print B.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9],
         [0, 0, 0]]
        >>> B[0] == A[0]
        True
        >>> B[0] is A[0]
        False
        >>> S == B[-1]
        True
        >>> S is B[-1]
        True
        >>> B = Array(shape=(4, 4))
        >>> B.fit(A)
        >>> print B.formated()
        [[1, 2, 3, 0],
         [4, 5, 6, 0],
         [7, 8, 9, 0],
         [0, 0, 0, 0]]
        >>> B = Array(shape=(2, 2))
        >>> B.fit(A)
        >>> print B.formated()
        [[1, 2],
         [4, 5]]
        """
    
        pass
    
    
    def fitted(self, other):
        """
        a.fitted(b) --> Array
        
        Returns the result of fitting the Array b in a.
        For every component of a that exists in b (there is a component of same coordinates in b),
        replace it with the value of the corresponding component in b.
        Both Arrays a and b must have same number of dimensions.
        
        Note : returns a copy (deepcopy) of a.fit(b)
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> B = Array(shape=(4, 3))
        >>> print B.formated()
        [[0, 0, 0],
         [0, 0, 0],
         [0, 0, 0],
         [0, 0, 0]]
        >>> C = B.fitted(A)
        >>> print C.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9],
         [0, 0, 0]]
        >>> C[0] == A[0]
        True
        >>> C[0] is A[0]
        False
        >>> C[-1] == B[-1]
        True
        >>> C[-1] is B[-1]
        False
        >>> B = Array(shape=(4, 4)).fitted(A)
        >>> print B.formated()
        [[1, 2, 3, 0],
         [4, 5, 6, 0],
         [7, 8, 9, 0],
         [0, 0, 0, 0]]
        >>> B = Array(shape=(2, 2)).fitted(A)
        >>> print B.formated()
        [[1, 2],
         [4, 5]]
        """
    
        pass
    
    
    def formated(self):
        """
        a.formated() --> str
        
        Returns a string representing a formated output of Array a
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        """
    
        pass
    
    
    def get(self):
        """
        a.get() --> Tuple
        
        Returns a's internally stored value as a nested tuple, a raw dump of the stored numeric components.
        
        >>> A = Array(range(1, 5), shape=(2, 2))
        >>> print A.get()
        ((1, 2), (3, 4))
        """
    
        pass
    
    
    def hstack(self, other):
        """
        a.hstack(b) <==> a.stack(b, axis=-1)
        
        Modifies a by concatenating b at its end, as iterated on last axis.
        For a 2 dimensional Array/MatrixN, it stacks a and b horizontally.
        
        >>> A = Array([[1, 2], [4, 5]])
        >>> print A.formated()
        [[1, 2],
         [4, 5]]
        >>> A.hstack([[3], [6]])
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        """
    
        pass
    
    
    def hstacked(self, other):
        """
        a.hstacked(b) <==> a.stacked(b, axis=-1)
        
        Returns the Array obtained by concatenating a and b on last axis.
        For a 2 dimensional Array/MatrixN, it stacks a and b horizontally.
        
        >>> A = Array([[1, 2], [4, 5]])
        >>> print A.formated()
        [[1, 2],
         [4, 5]]
        >>> A = A.hstacked([[3], [6]])
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        """
    
        pass
    
    
    def imag(self):
        """
        a.real() <==> real(a)
        
        Returns the element-wise complex imaginary part of the Array.
        
        >>> A = Array([[complex(1, 2), complex(2, 3)], [complex(4, 5), complex(6, 7)]])
        >>> print A.formated()
        [[(1+2j), (2+3j)],
         [(4+5j), (6+7j)]]
        >>> print A.imag().formated()
        [[2.0, 3.0],
         [5.0, 7.0]]
        >>> print imag(A).formated()
        [[2.0, 3.0],
         [5.0, 7.0]]
        >>> A = Array(range(1, 5), shape=(2, 2))
        >>> print imag(A).formated()
        [[0, 0],
         [0, 0]]
        """
    
        pass
    
    
    def index(self, value):
        """
        a.index(b) --> int or tuple
        
        Returns the index of the first occurrence of b in a.
        
        >>> A = Array(list(range(1, 6))+list(range(4, 0, -1)), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 4],
         [3, 2, 1]]
        >>> A.index(5)
        (1, 1)
        >>> A.index(4)
        (1, 0)
        >>> A.index([1, 2, 3])
        (0,)
        >>> A.index([1, 2])
        Traceback (most recent call last):
            ...
        ValueError: Array.index(x): x not in Array
        """
    
        pass
    
    
    def isEquivalent(self, other, tol=9.313225746154785e-10):
        """
        a.isEquivalent(b[, tol]) --> bool
        
        Returns True if both arguments have same shape and distance between both Array arguments is inferior or equal to tol.
        
        >>> A = Array([[0.5,0.5,-0.707],[0.707,-0.707,0]])
        >>> B = Array([[0.51,0.49,-0.71],[0.71,-0.70,0]])
        >>> C = Array([[0.501,0.499,-0.706],[0.706,-0.708,0.01]])
        >>> A.dist(B)
        0.016340134638368205
        >>> A.dist(C)
        0.010246950765959599
        >>> A.isEquivalent(C, 0.015)
        True
        >>> A.isEquivalent(B, 0.015)
        False
        >>> A.isEquivalent(B, 0.020)
        True
        """
    
        pass
    
    
    def length(self, *args):
        """
        a.length(axis0, axis1, ...) <==> length(a[, axis=(axis0, axis1, ...)])
        
        Returns length of a, sqrt(a*a) or the square root of the sum of x*x for x in a if a is an iterable of numeric values.
        If a is an Array and axis are specified will return a list of length(x) for x in a.axisiter(*axis).
        
        >>> A = Array([[0.5,0.5,-0.707],[0.707,-0.707,0.0]])
        >>> print A.formated()
        [[0.5, 0.5, -0.707],
         [0.707, -0.707, 0.0]]
        >>> round(A.length(), 7)
        1.4140534
        >>> round(A.length(0,1), 7)
        1.4140534
        >>> A.length(0)
        Array([0.99992449715, 0.999848988598])
        >>> A.length(1)
        Array([0.865938219505, 0.865938219505, 0.707])
        """
    
        pass
    
    
    def max(self, *args, **kwargs):
        """
        a.max([axis0[, axis1[, ...[, key=func]]]])  <==> max(a[, key=func[, axis=(axis0, axis1, ...)]])
        
        Returns the greatest component of a.
        If axis are specified will return an Array of element-wise max(x) for x in a.axisiter(*axis).
        
        >>> A = Array([[6,3,4],[1,5,0.5]])
        >>> print A.formated()
        [[6, 3, 4],
         [1, 5, 0.5]]
        >>> A.max()
        6
        >>> A.max(0,1)
        6
        >>> A.max(0)
        Array([6, 5, 4])
        >>> A.max(1)
        Array([6, 5])
        """
    
        pass
    
    
    def min(self, *args, **kwargs):
        """
        a.min([axis0[, axis1[, ...[, key=func]]]])  <==> min(a[, key=func[, axis=(axis0, axis1, ...)]])
        
        Returns the smallest component of a.
        If axis are specified will return an Array of element-wise min(x) for x in a.axisiter(*axis).
        
        >>> A = Array([[6,3,4],[1,5,0.5]])
        >>> print A.formated()
        [[6, 3, 4],
         [1, 5, 0.5]]
        >>> A.min()
        0.5
        >>> A.min(0, 1)
        0.5
        >>> A.min(0)
        Array([1, 3, 0.5])
        >>> A.min(1)
        Array([3, 0.5])
        """
    
        pass
    
    
    def normal(self, *args):
        """
        a.normal(axis0, axis1, ...) <==> normal(a[, axis=(axis0, axis1, ...)])
        
        Returns a normalized copy of self: self/self.length(axis0, axis1, ...).
        
        >>> A = Array([[0.5,0.5,-0.707],[0.707,-0.707,0.0]])
        >>> print A.formated()
        [[0.5, 0.5, -0.707],
         [0.707, -0.707, 0.0]]
        >>> print A.normal().formated()
        [[0.353593437318, 0.353593437318, -0.499981120367],
         [0.499981120367, -0.499981120367, 0.0]]
        >>> print A.normal(0,1).formated()
        [[0.353593437318, 0.353593437318, -0.499981120367],
         [0.499981120367, -0.499981120367, 0.0]]
        >>> print A.normal(0).formated()
        [[0.5, 0.5, -0.707],
         [0.707, -0.707, 0.0]]
        >>> print A.normal(1).formated()
        [[0.577408397894, 0.577408397894, -1.0],
         [0.816455474623, -0.816455474623, 0.0]]
        """
    
        pass
    
    
    def normalize(self, *args):
        """
        Performs an in place normalization of self
        """
    
        pass
    
    
    def prod(self, *args, **kwargs):
        """
        a.prod([axis0[, axis1[, ...[, start=0]]]]) <=> prod(a, start=start, axis=(axis0, axis1, ...))
        
        Returns the product of all the components of a, an iterable of values that support the mul operator, times start.
        If axis are specified will return an Array of prod(x) for x in a.axisiter(*axis).
        
        >>> A = Array([[1,2,3],[4,5,6]])
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        >>> A.prod()
        720
        >>> A.prod(0, 1)
        720
        >>> A.prod(0)
        Array([4, 10, 18])
        >>> A.prod(1)
        Array([6, 120])
        """
    
        pass
    
    
    def ravel(self):
        """
        a.ravel() <==> Array(a.flat)
        
        Returns that Array flattened as to a one-dimensional array.
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print repr(A.ravel())
        Array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        """
    
        pass
    
    
    def real(self):
        """
        a.real() <==> real(a)
        
        Returns the element-wise complex real part of the Array.
        
        >>> A = Array([[complex(1, 2), complex(2, 3)], [complex(4, 5), complex(6, 7)]])
        >>> print A.formated()
        [[(1+2j), (2+3j)],
         [(4+5j), (6+7j)]]
        >>> print A.real().formated()
        [[1.0, 2.0],
         [4.0, 6.0]]
        >>> print real(A).formated()
        [[1.0, 2.0],
         [4.0, 6.0]]
        >>> A = Array(range(1, 5), shape=(2, 2))
        >>> print real(A).formated()
        [[1, 2],
         [3, 4]]
        """
    
        pass
    
    
    def reshape(self, shape=None):
        """
        a.reshaped(shape) <==> a.shape = shape
        
        Performs in-place reshape of array a according to the shape argument without changing the Array's size
        (total number of components).
        
        Note : as opposed to trim, reshape will reshuffle components and thus not preserve sub-arrays identity.
        
        Examples :
        
        >>> A = Array(range(1, 17), shape=(4, 4))
        >>> print A.formated()
        [[1, 2, 3, 4],
         [5, 6, 7, 8],
         [9, 10, 11, 12],
         [13, 14, 15, 16]]
        >>> S = A[0]
        >>> A.reshape(shape=(2, 2, 4))
        >>> print A.formated()
        [[[1, 2, 3, 4],
          [5, 6, 7, 8]],
        <BLANKLINE>
         [[9, 10, 11, 12],
          [13, 14, 15, 16]]]
        >>> S == A[0, 0]
        True
        >>> S is A[0, 0]
        False
        """
    
        pass
    
    
    def reshaped(self, shape=None):
        """
        a.reshaped(shape) --> Array
        
        Returns a copy the Array as reshaped according to the shape argument, without changing the Array's size
        (total number of components)
        
        Examples :
        
        >>> A = Array(range(1, 17), shape=(4, 4))
        >>> print A.formated()
        [[1, 2, 3, 4],
         [5, 6, 7, 8],
         [9, 10, 11, 12],
         [13, 14, 15, 16]]
        >>> B = A.reshaped(shape=(2, 2, 4))
        >>> print B.formated()
        [[[1, 2, 3, 4],
          [5, 6, 7, 8]],
        <BLANKLINE>
         [[9, 10, 11, 12],
          [13, 14, 15, 16]]]
        >>> A[0] == B[0, 0]
        True
        >>> A[0] is B[0, 0]
        False
        """
    
        pass
    
    
    def resize(self, shape=None, value=None):
        """
        a.resize([shape[, value]])
        
        Performs in-place resize of array a according to the shape argument.
        An optional value argument can be passed and will be used to fill the newly created components
        if the resize results in a size increase, otherwise the Array class default values are used.
        
        Note : as opposed to trim, resize will reshuffle components and thus not preserve sub-arrays identity.
        
        Examples :
        
        >>> A = Array(range(1, 17), shape=(4, 4))
        >>> print A.formated()
        [[1, 2, 3, 4],
         [5, 6, 7, 8],
         [9, 10, 11, 12],
         [13, 14, 15, 16]]
        >>> S = A[0]
        >>> A.resize(shape=(2, 2, 4))
        >>> print A.formated()
        [[[1, 2, 3, 4],
          [5, 6, 7, 8]],
        <BLANKLINE>
         [[9, 10, 11, 12],
          [13, 14, 15, 16]]]
        >>> S == A[0, 0]
        True
        >>> S is A[0, 0]
        False
        >>> A.resize(shape=(2, 3, 3))
        >>> print A.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[10, 11, 12],
          [13, 14, 15],
          [16, 0, 0]]]
        >>> A.resize(shape=(4, 5), value=1)
        >>> print A.formated()
        [[1, 2, 3, 4, 5],
         [6, 7, 8, 9, 10],
         [11, 12, 13, 14, 15],
         [16, 0, 0, 1, 1]]
        """
    
        pass
    
    
    def resized(self, shape=None, value=None):
        """
        a.resized([shape [, value]]) --> Array
        
        Returns a copy of the Array resized according to the shape argument.
        An optional value argument can be passed and will be used to fill the extra components
        of the new Array if the resize results in a size increase, otherwise the Array class default values are used.
        
        Examples :
        
        >>> A = Array(range(1, 17), shape=(4, 4))
        >>> print A.formated()
        [[1, 2, 3, 4],
         [5, 6, 7, 8],
         [9, 10, 11, 12],
         [13, 14, 15, 16]]
        >>> B = A.resized(shape=(2, 2, 4))
        >>> print B.formated()
        [[[1, 2, 3, 4],
          [5, 6, 7, 8]],
        <BLANKLINE>
         [[9, 10, 11, 12],
          [13, 14, 15, 16]]]
        >>> A[0] == B[0, 0]
        True
        >>> A[0] is B[0, 0]
        False
        >>> B = B.resized(shape=(2, 3, 3))
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[10, 11, 12],
          [13, 14, 15],
          [16, 0, 0]]]
        >>> B = B.resized(shape=(4, 5), value=1)
        >>> print B.formated()
        [[1, 2, 3, 4, 5],
         [6, 7, 8, 9, 10],
         [11, 12, 13, 14, 15],
         [16, 0, 0, 1, 1]]
        """
    
        pass
    
    
    def sqlength(self, *args):
        """
        a.sqlength(axis0, axis1, ...) <==> sqlength(a[, axis=(axis0, axis1, ...)])
        
        Returns square length of a, ie a*a or the sum of x*x for x in a if a is an iterable of numeric values.
        If a is an Array and axis are specified will return a list of sqlength(x) for x in a.axisiter(*axis).
        
        >>> A = Array([[0.5,0.5,-0.707],[0.707,-0.707,0.0]])
        >>> print A.formated()
        [[0.5, 0.5, -0.707],
         [0.707, -0.707, 0.0]]
        >>> A.sqlength()
        1.999547
        >>> A.sqlength(0,1)
        1.999547
        >>> A.sqlength(0)
        Array([0.999849, 0.999698])
        >>> A.sqlength(1)
        Array([0.749849, 0.749849, 0.499849])
        """
    
        pass
    
    
    def stack(self, other, axis=0):
        """
        a.stack(b[, axis=0]) --> Array
        
        Modifies a by concatenating b at its end, as iterated on axis.
        
        Note : stacks a copy (deepcopy) of b, not a reference to b. However a is modified in place.
        
        Examples:
        
        >>> A = Array([])
        >>> print repr(A)
        Array([])
        >>> A.stack([1])
        >>> print A.formated()
        [1]
        >>> A.stack([2])
        >>> print A.formated()
        [1, 2]
        >>> A = Array([A])
        >>> print A.formated()
        [[1, 2]]
        >>> A.stack([[4, 5]], axis=0)
        >>> print A.formated()
        [[1, 2],
         [4, 5]]
        >>> A.stack([[3], [6]], axis=1)
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        >>> A.stack([[7, 8, 9]])
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> B = Array([A])
        >>> B.stack(B)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]]
        >>> B[0] == B[1]
        True
        >>> B[0] is B[1]
        False
        >>> A == B[0]
        True
        >>> A is B[0]
        True
        >>> B.stack([[[0, 0, 0]], [[0, 0, 0]]], axis=1)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          [0, 0, 0]],
        <BLANKLINE>
         [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          [0, 0, 0]]]
        >>> B.stack([[[0], [0], [0], [1]], [[0], [0], [0], [1]]], axis=2)
        >>> print B.formated()
        [[[1, 2, 3, 0],
          [4, 5, 6, 0],
          [7, 8, 9, 0],
          [0, 0, 0, 1]],
        <BLANKLINE>
         [[1, 2, 3, 0],
          [4, 5, 6, 0],
          [7, 8, 9, 0],
          [0, 0, 0, 1]]]
        """
    
        pass
    
    
    def stacked(self, other, axis=0):
        """
        a.stacked(b[, axis=0]) --> Array
        
        Returns the Array obtained by concatenating a and b on axis.
        
        Note : returns a deepcopy of a.stack(b[, axis=0]).
        
        Examples:
        
        >>> A = Array([])
        >>> print repr(A)
        Array([])
        >>> A = A.stacked([1])
        >>> print A.formated()
        [1]
        >>> A = A.stacked([2])
        >>> print A.formated()
        [1, 2]
        >>> A = Array([A])
        >>> print A.formated()
        [[1, 2]]
        >>> A = A.stacked([[4, 5]], axis=0)
        >>> print A.formated()
        [[1, 2],
         [4, 5]]
        >>> A = A.stacked([[3], [6]], axis=1)
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        >>> A = A.stacked([[7, 8, 9]])
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> B = Array([A])
        >>> B = B.stacked(B)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]]
        >>> B[0] == B[1]
        True
        >>> B[0] is B[1]
        False
        >>> A == B[0]
        True
        >>> A is B[0]
        False
        >>> B = B.stacked([[[0, 0, 0]], [[0, 0, 0]]], axis=1)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          [0, 0, 0]],
        <BLANKLINE>
         [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9],
          [0, 0, 0]]]
        >>> B = B.stacked([[[0], [0], [0], [1]], [[0], [0], [0], [1]]], axis=2)
        >>> print B.formated()
        [[[1, 2, 3, 0],
          [4, 5, 6, 0],
          [7, 8, 9, 0],
          [0, 0, 0, 1]],
        <BLANKLINE>
         [[1, 2, 3, 0],
          [4, 5, 6, 0],
          [7, 8, 9, 0],
          [0, 0, 0, 1]]]
        """
    
        pass
    
    
    def strip(self, *args):
        """
        a.strip(index)
        
        Strip the elements designated by index from a.
        
        Note : as opposed to a.__delete__(index), will collapse dimensions of the Array
        that end up with only one sub-array.
        
        >>> A = Array(xrange(1, 28), shape=(3, 3, 3))
        >>> print A.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[10, 11, 12],
          [13, 14, 15],
          [16, 17, 18]],
        <BLANKLINE>
         [[19, 20, 21],
          [22, 23, 24],
          [25, 26, 27]]]
        >>> A.shape
        (3, 3, 3)
        >>> S = A[0]
        >>> A.strip(1)
        >>> print A.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[19, 20, 21],
          [22, 23, 24],
          [25, 26, 27]]]
        >>> S == A[0]
        True
        >>> S is A[0]
        True
        >>> A.strip(-1)
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> S == A
        True
        >>> S is A
        False
        >>> S[0] == A[0]
        True
        >>> S[0] is A[0]
        True
        >>> A.strip(None, slice(1,3))
        >>> print A.formated()
        [[1],
         [4],
         [7]]
        >>> A.strip(-1)
        >>> print A.formated()
        [[1],
         [4]]
        >>> A.strip(-1)
        >>> print A.formated()
        [1]
        >>> A.strip(-1)
        >>> print A.formated()
        []
        """
    
        pass
    
    
    def stripped(self, *args):
        """
        a.stripped(index) --> Array
        
        Returns a copy (deepcopy) of a with the elements designated by index stripped,
        as in a.strip(index)
        
        Note : as opposed to a.deleted(index), will collapse dimensions of the Array
        that end up with only one sub-array.
        
        >>> A = Array(xrange(1, 28), shape=(3, 3, 3))
        >>> print A.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[10, 11, 12],
          [13, 14, 15],
          [16, 17, 18]],
        <BLANKLINE>
         [[19, 20, 21],
          [22, 23, 24],
          [25, 26, 27]]]
        >>> A.shape
        (3, 3, 3)
        >>> B = A.stripped(1)
        >>> print B.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[19, 20, 21],
          [22, 23, 24],
          [25, 26, 27]]]
        >>> B[0] == A[0]
        True
        >>> B[0] is A[0]
        False
        >>> B = B.stripped(-1)
        >>> print B.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> B == A[0]
        True
        >>> B is A[0]
        False
        >>> B[0] == A[0, 0]
        True
        >>> B[0] is A[0,0]
        False
        >>> B = B.stripped(None, slice(1,3))
        >>> print B.formated()
        [[1],
         [4],
         [7]]
        >>> B = B.stripped(-1)
        >>> print B.formated()
        [[1],
         [4]]
        >>> B = B.stripped(-1)
        >>> print B.formated()
        [1]
        >>> B = B.stripped(-1)
        >>> print B.formated()
        []
        """
    
        pass
    
    
    def subiter(self, dim=None):
        """
        a.subiter([dim=None]) --> ArrayIter
        
        Returns an iterator on all sub Arrays for a specific sub Array number of dimension.
        
        a.subiter(0) is equivalent to a.flat: lista sub-arrays of dimension 0, ie components
        a.subiter() is equivalent to self.subiter(self.ndim-1) and thus to self.__iter__()
        
        Note : ArrayIter iterators support __len__, __getitem__ and __setitem__
        
        >>> A = Array(range(1, 28), shape=(3, 3, 3))
        >>> print A.formated()
        [[[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]],
        <BLANKLINE>
         [[10, 11, 12],
          [13, 14, 15],
          [16, 17, 18]],
        <BLANKLINE>
         [[19, 20, 21],
          [22, 23, 24],
          [25, 26, 27]]]
        >>> [a for a in A.subiter(0)]
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
        >>> [a for a in A.subiter(1)]
        [Array([1, 2, 3]), Array([4, 5, 6]), Array([7, 8, 9]), Array([10, 11, 12]), Array([13, 14, 15]), Array([16, 17, 18]), Array([19, 20, 21]), Array([22, 23, 24]), Array([25, 26, 27])]
        >>> [a for a in A.subiter(2)]
        [Array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), Array([[10, 11, 12], [13, 14, 15], [16, 17, 18]]), Array([[19, 20, 21], [22, 23, 24], [25, 26, 27]])]
        >>> [a for a in A.subiter(3)]
        Traceback (most recent call last):
            ...
        ValueError: can only iterate for a sub-dimension inferior to Array's number of dimensions 3
        """
    
        pass
    
    
    def sum(self, *args, **kwargs):
        """
        a.sum([axis0[, axis1[, ...[, start=0]]]]) <=> sum(a, start=start, axis=(axis0, axis1, ...))
        
        Returns the sum of all the components of a, plus start.
        If axis are specified will return an Array of sum(x) for x in a.axisiter(*axis), else will
        sum on all axis of a.
        
        >>> A = Array([[1,2,3],[4,5,6]])
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        >>> A.sum()
        21
        >>> A.sum(0, 1)
        21
        >>> A.sum(0)
        Array([5, 7, 9])
        >>> A.sum(1)
        Array([6, 15])
        """
    
        pass
    
    
    def tolist(self):
        """
        a.tolist() --> list
        
        Returns that Array converted to a nested list
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print repr(A)
        Array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> print repr(list(A))
        [Array([1, 2, 3]), Array([4, 5, 6]), Array([7, 8, 9])]
        >>> print repr(A.tolist())
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        """
    
        pass
    
    
    def totuple(self):
        """
        a.totuple() --> tuple
        
        Returns that Array converted to a nested tuple
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print repr(A)
        Array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> print repr(tuple(A))
        (Array([1, 2, 3]), Array([4, 5, 6]), Array([7, 8, 9]))
        >>> print repr(A.totuple())
        ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        """
    
        pass
    
    
    def transpose(self, *args):
        """
        a.transpose([axis0[, axis1[, ...]]]) --> Array
        
        Returns a reordered / transposed along the specified axes.
        If no axes are given,or None is passed, switches the complete axes order.
        For a 2-d array, this is the usual matrix transpose.
        
        >>> A = Array(range(18), shape=(2,3,3))
        >>> print A.formated()
        [[[0, 1, 2],
          [3, 4, 5],
          [6, 7, 8]],
        <BLANKLINE>
         [[9, 10, 11],
          [12, 13, 14],
          [15, 16, 17]]]
        >>> print A.transpose().formated()
        [[[0, 9],
          [3, 12],
          [6, 15]],
        <BLANKLINE>
         [[1, 10],
          [4, 13],
          [7, 16]],
        <BLANKLINE>
         [[2, 11],
          [5, 14],
          [8, 17]]]
        >>> print A.transpose(0,2,1).formated()
        [[[0, 3, 6],
          [1, 4, 7],
          [2, 5, 8]],
        <BLANKLINE>
         [[9, 12, 15],
          [10, 13, 16],
          [11, 14, 17]]]
        
        >>> B=MatrixN(range(9), shape=(3, 3))
        >>> print B.formated()
        [[0, 1, 2],
         [3, 4, 5],
         [6, 7, 8]]
        >>> print B.transpose().formated()
        [[0, 3, 6],
         [1, 4, 7],
         [2, 5, 8]]
        """
    
        pass
    
    
    def trim(self, shape=None, value=None):
        """
        a.trim(shape)
        Performs in-place trimming of array a to given shape.
        An optional value argument can be passed and will be used to fill
        the newly created components if the resize results in a size increase.
        
        Note : a is modified in-place
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> S = A[0]
        >>> A.trim(shape=(4, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9],
         [0, 0, 0]]
        >>> S == A[0]
        True
        >>> S is A[0]
        True
        >>> A.trim(shape=(4, 4))
        >>> print A.formated()
        [[1, 2, 3, 0],
         [4, 5, 6, 0],
         [7, 8, 9, 0],
         [0, 0, 0, 0]]
        >>> A.trim(shape=(2, 2))
        >>> print A.formated()
        [[1, 2],
         [4, 5]]
        """
    
        pass
    
    
    def trimmed(self, shape=None, value=None):
        """
        a.trimmed([shape [, value]]) --> Array
        
        Returns the Array as "trimmed", re-sized according to the shape argument.
        The difference with a resize is that each dimension will be resized individually,
        thus the shape argument must have the same number of dimensions as the Array a.
        A value of -1 or None for a shape dimension size will leave it unchanged.
        An optional value argument can be passed and will be used to fill the newly created
        components if the trimmed results in a size increase, otherwise the class default values
        will be used to fill new components
        
        Note : returns a copy (deepcopy) of a.trim([shape [, value]])
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> B = A.trimmed(shape=(4, 3))
        >>> print B.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9],
         [0, 0, 0]]
        >>> B[0] == A[0]
        True
        >>> B[0] is A[0]
        False
        >>> B = A.trimmed(shape=(4, 4))
        >>> print B.formated()
        [[1, 2, 3, 0],
         [4, 5, 6, 0],
         [7, 8, 9, 0],
         [0, 0, 0, 0]]
        >>> B = A.trimmed(shape=(2, 2))
        >>> print B.formated()
        [[1, 2],
         [4, 5]]
        """
    
        pass
    
    
    def vstack(self, other):
        """
        a.vstack(b) <==> a.stack(b, axis=0)
        
        Modifies a by concatenating b at its end, as iterated on first axis.
        For a 2 dimensional Array/MatrixN, it stacks a and b vertically
        
        >>> A = Array([[1, 2], [3, 4]])
        >>> print A.formated()
        [[1, 2],
         [3, 4]]
        >>> A.vstack([[5, 6]])
        >>> print A.formated()
        [[1, 2],
         [3, 4],
         [5, 6]]
        """
    
        pass
    
    
    def vstacked(self, other):
        """
        a.vstacked(b) <==> a.stacked(b, axis=0)
        
        Returns the Array obtained by concatenating a and b on first axis.
        For a 2 dimensional Array/MatrixN, it stacks a and b vertically.
        
        >>> A = Array([[1, 2], [3, 4]])
        >>> print A.formated()
        [[1, 2],
         [3, 4]]
        >>> A = A.vstacked([[5, 6]])
        >>> print A.formated()
        [[1, 2],
         [3, 4],
         [5, 6]]
        """
    
        pass
    
    
    def __new__(cls, *args, **kwargs):
        """
        cls.__new__(...) --> cls
        
        Creates a new Array instance without calling __init__, the created instance will be of the
        class cls (an Array subclass) default shape (if any) and set to the class default value.
        See Array, MatrixN or VectorN help for more information.
        """
    
        pass
    
    
    T = None
    
    data = None
    
    flat = None
    
    ndim = None
    
    shape = None
    
    size = None
    
    __hash__ = None
    
    
    
    
    __readonly__ = {}
    
    
    apicls = None


class ArrayIter(object):
    """
    A general purpose iterator on Arrays.
    
    ArrayIter allows to iterate on one or more specified axis of an Array, in any order.
    
    For an Array of n dimensions, iterator on p axis will yield sub-arrays of n-p dimensions,
    numerical components if n-p is 0.
    
    >>> A = Array(range(1, 28), shape=(3, 3, 3))
    >>> print A.formated()
    [[[1, 2, 3],
      [4, 5, 6],
      [7, 8, 9]],
    <BLANKLINE>
     [[10, 11, 12],
      [13, 14, 15],
      [16, 17, 18]],
    <BLANKLINE>
     [[19, 20, 21],
      [22, 23, 24],
      [25, 26, 27]]]
    >>> [a for a in A]
    [Array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), Array([[10, 11, 12], [13, 14, 15], [16, 17, 18]]), Array([[19, 20, 21], [22, 23, 24], [25, 26, 27]])]
    >>> [a for a in ArrayIter(A, 0)]
    [Array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), Array([[10, 11, 12], [13, 14, 15], [16, 17, 18]]), Array([[19, 20, 21], [22, 23, 24], [25, 26, 27]])]
    >>> [a for a in ArrayIter(A, 1)]
    [Array([[1, 2, 3], [10, 11, 12], [19, 20, 21]]), Array([[4, 5, 6], [13, 14, 15], [22, 23, 24]]), Array([[7, 8, 9], [16, 17, 18], [25, 26, 27]])]
    >>> [a for a in ArrayIter(A, 2)]
    [Array([[1, 4, 7], [10, 13, 16], [19, 22, 25]]), Array([[2, 5, 8], [11, 14, 17], [20, 23, 26]]), Array([[3, 6, 9], [12, 15, 18], [21, 24, 27]])]
    >>> [a for a in ArrayIter(A, 0, 1)]
    [Array([1, 2, 3]), Array([4, 5, 6]), Array([7, 8, 9]), Array([10, 11, 12]), Array([13, 14, 15]), Array([16, 17, 18]), Array([19, 20, 21]), Array([22, 23, 24]), Array([25, 26, 27])]
    >>> [a for a in ArrayIter(A, 0, 2)]
    [Array([1, 4, 7]), Array([2, 5, 8]), Array([3, 6, 9]), Array([10, 13, 16]), Array([11, 14, 17]), Array([12, 15, 18]), Array([19, 22, 25]), Array([20, 23, 26]), Array([21, 24, 27])]
    >>> [a for a in ArrayIter(A, 0, 1, 2)]
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
    >>> [a for a in ArrayIter(A, 0, 2, 1)]
    [1, 4, 7, 2, 5, 8, 3, 6, 9, 10, 13, 16, 11, 14, 17, 12, 15, 18, 19, 22, 25, 20, 23, 26, 21, 24, 27]
    
    ArrayIter iterators support __len__, __getitem__,  __setitem__ and __delitem__ methods, it can be used
    to set whole sub-arrays in any order (for instance rows or columns in MatrixN)
    
    >>> A = Array(range(1, 10), shape=(3, 3))
    >>> print A.formated()
    [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]
    >>> [a for a in ArrayIter(A, 0, 1)]
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> len(ArrayIter(A, 0, 1))
    9
    >>> ArrayIter(A, 0, 1)[5:9] = [4, 3, 2, 1]
    >>> print A.formated()
    [[1, 2, 3],
     [4, 5, 4],
     [3, 2, 1]]
    >>> [a for a in ArrayIter(A, 1)]
    [Array([1, 4, 3]), Array([2, 5, 2]), Array([3, 4, 1])]
    >>> len(ArrayIter(A, 1))
    3
    >>> ArrayIter(A, 1)[1] = [7, 8, 9]
    >>> print A.formated()
    [[1, 7, 3],
     [4, 8, 4],
     [3, 9, 1]]
    >>> ArrayIter(A, 0)[1] = 0
    >>> print A.formated()
    [[1, 7, 3],
     [0, 0, 0],
     [3, 9, 1]]
    """
    
    
    
    def __delitem__(self, index):
        """
        it.__delitem__(index) <==> del it[index]
        
        Note : if it is an ArrayIter built on Array a, it's equivalent to del a[c] for c in it.toArrayCoords(index)
        
        Warning : Do not use __delitem__ during iteration
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> [a for a in ArrayIter(A, 0, 1)]
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> del ArrayIter(A, 0, 1)[1]
        >>> [a for a in ArrayIter(A, 0, 1)]
        [4, 6, 7, 9]
        >>> print A.formated()
        [[4, 6],
         [7, 9]]
        >>> [a for a in ArrayIter(A, 1)]
        [Array([4, 7]), Array([6, 9])]
        >>> del ArrayIter(A, 1)[-1]
        >>> print A.formated()
        [[4],
         [7]]
        """
    
        pass
    
    
    def __getitem__(self, index):
        """
        it.__getitem__(index) <==> it[index]
        
        Returns a single sub-Array or component corresponding to the iterator item designated by index, or an Array of values if index is a slice.
        
        Note : if it is an ArrayIter built on Array a, it's equivalent to a[c] for c in it.toArrayCoords(index)
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> [a for a in ArrayIter(A, 0, 1)]
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> ArrayIter(A, 0, 1)[4]
        5
        >>> ArrayIter(A, 0, 1)[0:6]
        Array([1, 2, 3, 4, 5, 6])
        >>> [a for a in ArrayIter(A, 1)]
        [Array([1, 4, 7]), Array([2, 5, 8]), Array([3, 6, 9])]
        >>> ArrayIter(A, 1)[1]
        Array([2, 5, 8])
        >>> ArrayIter(A, 1)[1, 0]
        2
        >>> print ArrayIter(A, 1)[0:2, 0:2].formated()
        [[1, 4],
         [2, 5]]
        >>> print A.transpose()[0:2, 0:2].formated()
        [[1, 4],
         [2, 5]]
        """
    
        pass
    
    
    def __init__(self, data, *args):
        """
        it.__init__(a[, axis1[, axis2[, ...]]])
        
        Inits this Array iterator on Array a, using the specified list of axis, see ArrayIter help.
        """
    
        pass
    
    
    def __iter__(self):
        pass
    
    
    def __len__(self):
        pass
    
    
    def __length_hint__(self):
        pass
    
    
    def __setitem__(self, index, value):
        """
        it.__setitem__(index, value) <==> it[index] = value
        
        Returns a single sub-Array or component corresponding to the iterator item item, or an Array of values if index is a slice.
        
        Note : if it is an ArrayIter built on Array a, it's equivalent to a[c]=value for c in it.toArrayCoords(index) or
        a[c] = value[i] for i, c in enumerate(it.toArrayCoords(index)) if an iterable of values of suitable shapes was provided.
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> [a for a in ArrayIter(A, 0, 1)]
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> ArrayIter(A, 0, 1)[4] = 10
        >>> [a for a in ArrayIter(A, 0, 1)]
        [1, 2, 3, 4, 10, 6, 7, 8, 9]
        >>> print A.formated()
        [[1, 2, 3],
         [4, 10, 6],
         [7, 8, 9]]
        >>> ArrayIter(A, 0, 1)[0:3] = 1
        >>> [a for a in ArrayIter(A, 0, 1)]
        [1, 1, 1, 4, 10, 6, 7, 8, 9]
        >>> print A.formated()
        [[1, 1, 1],
         [4, 10, 6],
         [7, 8, 9]]
        >>> ArrayIter(A, 0, 1)[5:9] = [4, 3, 2, 1]
        >>> [a for a in ArrayIter(A, 0, 1)]
        [1, 1, 1, 4, 10, 4, 3, 2, 1]
        >>> print A.formated()
        [[1, 1, 1],
         [4, 10, 4],
         [3, 2, 1]]
        >>> [a for a in ArrayIter(A, 1)]
        [Array([1, 4, 3]), Array([1, 10, 2]), Array([1, 4, 1])]
        >>> ArrayIter(A, 1)[1]
        Array([1, 10, 2])
        >>> ArrayIter(A, 1)[1, 1] = 5
        >>> print A.formated()
        [[1, 1, 1],
         [4, 5, 4],
         [3, 2, 1]]
        >>> ArrayIter(A, 1)[-1] = [7, 8, 9]
        >>> print A.formated()
        [[1, 1, 7],
         [4, 5, 8],
         [3, 2, 9]]
        >>> ArrayIter(A, 0)[1] = 0
        >>> print A.formated()
        [[1, 1, 7],
         [0, 0, 0],
         [3, 2, 9]]
        """
    
        pass
    
    
    def next(self):
        """
        it.next() -> the next value, or raise StopIteration
        """
    
        pass
    
    
    def toArrayCoords(self, index, default=None):
        """
        it.toArrayCoords(index, default=None) --> list or tuple
        
        Converts an iterator item index (item of number index in the iterator) for that Array iterator to a tuple of axis coordinates for that Array,
        returns a single coordinates tuple or a list of coordinate tuples if index was a slice.
        If index is a multi-index (a tuple), the first element if index is checked against the iterator and the remaining elements are considered
        indices on the iterated sub-array (s).
        
        >>> A = Array(range(1, 10), shape=(3, 3))
        >>> print A.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> [a for a in ArrayIter(A, 0, 1)]
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> it = ArrayIter(A, 0, 1)
        >>> it[4]
        5
        >>> it.toArrayCoords(4)
        (1, 1)
        >>> A[1, 1]
        5
        >>> it[1:4]
        Array([2, 3, 4])
        >>> it.toArrayCoords(slice(1, 4))
        [(0, 1), (0, 2), (1, 0)]
        
        >>> [a for a in ArrayIter(A, 1)]
        [Array([1, 4, 7]), Array([2, 5, 8]), Array([3, 6, 9])]
        >>> it = ArrayIter(A, 1)
        >>> it[0]
        Array([1, 4, 7])
        >>> it.toArrayCoords(0)
        (None, 0)
        >>> it.toArrayCoords(0, default=slice(None))
        (slice(None, None, None), 0)
        >>> A[:, 0]
        Array([1, 4, 7])
        >>> it.toArrayCoords((0, 1))
        (1, 0)
        >>> it[0, 1]
        4
        >>> A[1, 0]
        4
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class MatrixN(Array):
    """
    A generic size MatrixN class, basically a 2 dimensional Array.
    
    Most methods and behavior are herited from Array, with the limitation that a MatrixN must have
    exactly 2 dimensions.
    
    >>> M = MatrixN()
    >>> M
    MatrixN([[]])
    >>> M = MatrixN([])
    >>> M
    MatrixN([[]])
    >>> M = MatrixN([0, 1, 2])
    >>> print M.formated()
    [[0, 1, 2]]
    >>> M = MatrixN([[0, 1, 2]])
    >>> print M.formated()
    [[0, 1, 2]]
    >>> M = MatrixN([[0], [1], [2]])
    >>> print M.formated()
    [[0],
     [1],
     [2]]
    >>> M = MatrixN([[1, 2, 3], [4, 5, 6]])
    >>> print M.formated()
    [[1, 2, 3],
     [4, 5, 6]]
    >>> M = MatrixN(range(4), shape=(2, 2))
    >>> print M.formated()
    [[0, 1],
     [2, 3]]
    
    The MatrixN class has a constant ndim of 2
    
    >>> MatrixN.ndim
    2
    >>> M.ndim
    2
    >>> MatrixN.ndim = 3
    Traceback (most recent call last):
        ...
    AttributeError: attribute ndim is a read only class attribute and cannot be modified on class MatrixN
    >>> M.ndim = 3
    Traceback (most recent call last):
        ...
    AttributeError: 'MatrixN' object attribute 'ndim' is read-only
    
    It's protected against initialization or resizing to a shape that wouldn't be a MatrixN anymore
    
    >>> M = MatrixN([[[0, 1, 2], [3, 4, 5]], [[6, 7, 8], [9, 10, 11]]])
    Traceback (most recent call last):
        ...
    TypeError: cannot initialize a MatrixN of shape (2, 6) from [[[0, 1, 2], [3, 4, 5]], [[6, 7, 8], [9, 10, 11]]] of shape (2, 2, 3),
    as it would truncate data or reduce the number of dimensions
    
    >>> M.resize((2, 2, 3))
    Traceback (most recent call last):
        ...
    TypeError: new shape (2, 2, 3) is not compatible with class MatrixN
    
    Other Array types can be cast to MatrixN, but truncating data or reducing dimensions is not allowed
    to avoid silent loss of data in a conversion, use an explicit resize / trim / sub-array extraction
    
    >>> A = Array(range(9), shape=(3, 3))
    >>> M = MatrixN(A)
    >>> print M.formated()
    [[0, 1, 2],
     [3, 4, 5],
     [6, 7, 8]]
    >>> print clsname(M)
    MatrixN
    >>> A = Array([[[1, 2, 3], [4, 5, 6]], [[10, 20, 30], [40, 50, 60]]])
    >>> M = MatrixN(A)
    Traceback (most recent call last):
        ...
    TypeError: cannot cast a Array of shape (2, 2, 3) to a MatrixN of shape (2, 6),
    as it would truncate data or reduce the number of dimensions
    
    When initializing from a 1-d Array like a VectorN, dimension is upped to 2 by making it a row
    
    >>> V = VectorN(1, 2, 3)
    >>> M = MatrixN(V)
    >>> print M.formated()
    [[1, 2, 3]]
    
    Internally, rows are stored as Array though, not VectorN
    
    >>> M[0]
    Array([1, 2, 3])
    
    As for Array, __init__ is a shallow copy
    
    >>> A = Array(range(9), shape=(3, 3))
    >>> M = MatrixN(A)
    >>> M == A
    False
    >>> M is A
    False
    >>> M.isEquivalent(A)
    True
    >>> M[0] == A[0]
    True
    >>> M[0] is A[0]
    True
    """
    
    
    
    def __imul__(self, other):
        """
        a.__imul__(b) <==> a *= b
        
        In place multiplication of MatrixN a and b, see __mul__, result must fit a's type
        """
    
        pass
    
    
    def __mul__(self, other):
        """
        a.__mul__(b) <==> a*b
        
        If b is a MatrixN, __mul__ is mapped to matrix multiplication, if b is a VectorN, to MatrixN by VectorN multiplication,
        otherwise, returns the result of the element wise multiplication of a and b if b is convertible to Array,
        multiplies every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __rmul__(self, other):
        """
        a.__rmul__(b) <==> b*a
        
        If b is a MatrixN, __rmul__ is mapped to matrix multiplication, if b is a VectorN, to VectorN by MatrixN multiplication,
        otherwise, returns the result of the element wise multiplication of a and b if b is convertible to Array,
        multiplies every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def adjugate(self):
        """
        m.adjugate() --> MatrixN
        
        Returns the adjugate MatrixN of the square MatrixN m : the MatrixN of the cofactors of m.
        It's a square MatrixN of same size as m, where a component of index (i, j) is set to the value
        of m.cofactor(i, j).
        
        >>> M = MatrixN([ [100/(i+j) for i in xrange(1,5)] for j in xrange(4) ])
        >>> print M.formated()
        [[100, 50, 33, 25],
         [50, 33, 25, 20],
         [33, 25, 20, 16],
         [25, 20, 16, 14]]
        >>> print M[:1, :1].adjugate().formated()
        [[1]]
        >>> print M[:2, :2].adjugate().formated()
        [[33, -50],
         [-50, 100]]
        >>> print M[:3, :3].adjugate().formated()
        [[35, -175, 161],
         [-175, 911, -850],
         [161, -850, 800]]
        >>> print M[:4, :4].adjugate().formated()
        [[42, -210, 154, 49],
         [-210, 1054, -775, -245],
         [154, -775, 575, 175],
         [49, -245, 175, 63]]
        """
    
        pass
    
    
    def cofactor(self, i, j):
        """
        m.cofactor(i, j) --> float
        
        Returns the cofactor of matrix m for index (i, j),
        the determinant of the MatrixN obtained by deleting row i and column j from m (the minor),
        signed by (-1)**(i+j).
        
        >>> M = MatrixN(range(1, 10), shape=(3, 3))
        >>> print M.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> print M.minor(2, 2).formated()
        [[1, 2],
         [4, 5]]
        >>> M.minor(2, 2).det()
        -3
        >>> M.cofactor(2, 2)
        -3
        >>> print M.minor(0, 1).formated()
        [[4, 6],
         [7, 9]]
        >>> M.minor(0, 1).det()
        -6
        >>> M.cofactor(0, 1)
        6
        """
    
        pass
    
    
    def det(self):
        """
        m.det() <==> det(m)
        
        Returns the determinant of m, 0 if MatrixN is singular.
        
        >>> M = MatrixN([ [100/(i+j) for i in xrange(1,7)] for j in xrange(6) ])
        >>> print M.formated()
        [[100, 50, 33, 25, 20, 16],
         [50, 33, 25, 20, 16, 14],
         [33, 25, 20, 16, 14, 12],
         [25, 20, 16, 14, 12, 11],
         [20, 16, 14, 12, 11, 10],
         [16, 14, 12, 11, 10, 9]]
        >>> M[:1, :1].det()
        100
        >>> M[:2, :2].det()
        800
        >>> M[:3, :3].det()
        63
        >>> M[:4, :4].det()
        7
        >>> M[:5, :5].det()
        -1199
        >>> M[:6, :6].det()
        452.0
        
        >>> M = MatrixN(range(1, 10), shape=(3, 3))
        >>> print M.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> M.det()
        0
        """
    
        pass
    
    
    def diagonal(self, offset=0, wrap=False):
        """
        m.diagonal([offset=0[, wrap=False]]) -> Array
        
        Returns the diagonal of the MatrixN with the given offset,
        i.e., the collection of elements of the form a[i,i+offset].
        If keyword wrap=True will wrap out of bounds indices
        
        Examples :
        
        >>> M = MatrixN([[1, 2], [4, 6]])
        >>> print M.formated()
        [[1, 2],
         [4, 6]]
        >>> M.diagonal()
        Array([1, 6])
        >>> M.diagonal(1)
        Array([2])
        >>> M.diagonal(1, wrap=True)
        Array([2, 4])
        >>> M.diagonal(-1)
        Array([2, 4])
        >>> M.diagonal(-1, wrap=True)
        Array([2, 4])
        """
    
        pass
    
    
    def gauss(self):
        """
        m.gauss() --> MatrixN
        
        Returns the triangular matrix obtained by Gauss-Jordan elimination on m,
        will raise a ZeroDivisionError if m cannot be triangulated.
        
        >>> M = MatrixN([ [1.0/(i+j) for i in xrange(1,7)] for j in xrange(6) ])
        >>> print round(M, 2).formated()
        [[1.0, 0.5, 0.33, 0.25, 0.2, 0.17],
         [0.5, 0.33, 0.25, 0.2, 0.17, 0.14],
         [0.33, 0.25, 0.2, 0.17, 0.14, 0.13],
         [0.25, 0.2, 0.17, 0.14, 0.13, 0.11],
         [0.2, 0.17, 0.14, 0.13, 0.11, 0.1],
         [0.17, 0.14, 0.13, 0.11, 0.1, 0.09]]
        >>> print round(M[:1, :1].gauss(), 2).formated()
        [[1.0]]
        >>> print round(M[:2, :2].gauss(), 2).formated()
        [[1.0, 0.5],
         [0.0, 0.08]]
        >>> print round(M[:3, :3].gauss(), 2).formated() # doctest: +SKIP
        [[1.0, 0.5, 0.33],
         [0.0, 0.08, 0.09],
         [0.0, 0.0, -0.01]]
        >>> print round(M[:4, :4].gauss(), 2).formated() # doctest: +SKIP
        [[1.0, 0.5, 0.33, 0.25],
         [0.0, 0.08, 0.09, 0.08],
         [0.0, 0.0, -0.01, -0.01],
         [0.0, 0.0, 0.0, 0.0]]
        >>> print round(M[:5, :5].gauss(), 2).formated()  # doctest: +SKIP
        [[1.0, 0.5, 0.33, 0.25, 0.2],
         [0.0, 0.08, 0.09, 0.08, 0.08],
         [0.0, 0.0, -0.01, -0.01, -0.01],
         [0.0, 0.0, 0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0, -0.0, -0.0]]
        >>> print round(M[:6, :6].gauss(), 2).formated() # doctest: +SKIP
        [[1.0, 0.5, 0.33, 0.25, 0.2, 0.17],
         [0.0, 0.08, 0.09, 0.08, 0.08, 0.07],
         [0.0, 0.0, 0.01, 0.01, 0.01, 0.01],
         [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0, 0.0, -0.0, -0.0],
         [0.0, 0.0, 0.0, 0.0, 0.0, -0.0]]
        
        >>> M = MatrixN([[1, 2, 3], [2, 4, 6], [6, 7, 8]])
        >>> print M.formated()
        [[1, 2, 3],
         [2, 4, 6],
         [6, 7, 8]]
        >>> M.det()
        0
        >>> M.isSingular()
        True
        >>> print M.gauss().formated()
        Traceback (most recent call last):
            ...
        ZeroDivisionError: MatrixN is singular
        """
    
        pass
    
    
    def inv(self):
        """
        m.inverse() <==> inv(m)
        
        Returns the inverse MatrixN of m, if m is invertible, will raise a ValueError otherwise.
        
        >>> M = MatrixN([ [1.0/(i+j) for i in xrange(1,7)] for j in xrange(6) ])
        >>> print round(M, 2).formated()
        [[1.0, 0.5, 0.33, 0.25, 0.2, 0.17],
         [0.5, 0.33, 0.25, 0.2, 0.17, 0.14],
         [0.33, 0.25, 0.2, 0.17, 0.14, 0.13],
         [0.25, 0.2, 0.17, 0.14, 0.13, 0.11],
         [0.2, 0.17, 0.14, 0.13, 0.11, 0.1],
         [0.17, 0.14, 0.13, 0.11, 0.1, 0.09]]
        >>> print round(M[:1, :1].inverse(), 0).formated()
        [[1.0]]
        >>> print round(M[:2, :2].inverse(), 0).formated()
        [[4.0, -6.0],
         [-6.0, 12.0]]
        >>> print round(M[:3, :3].inverse(), 0).formated()
        [[9.0, -36.0, 30.0],
         [-36.0, 192.0, -180.0],
         [30.0, -180.0, 180.0]]
        >>> print round(M[:4, :4].inverse(), 0).formated()
        [[16.0, -120.0, 240.0, -140.0],
         [-120.0, 1200.0, -2700.0, 1680.0],
         [240.0, -2700.0, 6480.0, -4200.0],
         [-140.0, 1680.0, -4200.0, 2800.0]]
        >>> print round(M[:5, :5].inverse(), 0).formated()
        [[25.0, -300.0, 1050.0, -1400.0, 630.0],
         [-300.0, 4800.0, -18900.0, 26880.0, -12600.0],
         [1050.0, -18900.0, 79380.0, -117600.0, 56700.0],
         [-1400.0, 26880.0, -117600.0, 179200.0, -88200.0],
         [630.0, -12600.0, 56700.0, -88200.0, 44100.0]]
        >>> print round(M[:6, :6].inverse(), 0).formated()
        [[36.0, -630.0, 3360.0, -7560.0, 7560.0, -2772.0],
         [-630.0, 14700.0, -88200.0, 211680.0, -220500.0, 83160.0],
         [3360.0, -88200.0, 564480.0, -1411200.0, 1512000.0, -582120.0],
         [-7560.0, 211680.0, -1411200.0, 3628800.0, -3969000.0, 1552320.0],
         [7560.0, -220500.0, 1512000.0, -3969000.0, 4410000.0, -1746360.0],
         [-2772.0, 83160.0, -582120.0, 1552320.0, -1746360.0, 698544.0]]
        
        >>> M = MatrixN(range(1, 10), shape=(3, 3))
        >>> print M.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> M.det()
        0
        >>> M.isSingular()
        True
        >>> print M.inverse().formated()
        Traceback (most recent call last):
            ...
        ValueError: MatrixN is not invertible
        """
    
        pass
    
    
    def inverse(self):
        """
        m.inverse() <==> inv(m)
        
        Returns the inverse MatrixN of m, if m is invertible, will raise a ValueError otherwise.
        
        >>> M = MatrixN([ [1.0/(i+j) for i in xrange(1,7)] for j in xrange(6) ])
        >>> print round(M, 2).formated()
        [[1.0, 0.5, 0.33, 0.25, 0.2, 0.17],
         [0.5, 0.33, 0.25, 0.2, 0.17, 0.14],
         [0.33, 0.25, 0.2, 0.17, 0.14, 0.13],
         [0.25, 0.2, 0.17, 0.14, 0.13, 0.11],
         [0.2, 0.17, 0.14, 0.13, 0.11, 0.1],
         [0.17, 0.14, 0.13, 0.11, 0.1, 0.09]]
        >>> print round(M[:1, :1].inverse(), 0).formated()
        [[1.0]]
        >>> print round(M[:2, :2].inverse(), 0).formated()
        [[4.0, -6.0],
         [-6.0, 12.0]]
        >>> print round(M[:3, :3].inverse(), 0).formated()
        [[9.0, -36.0, 30.0],
         [-36.0, 192.0, -180.0],
         [30.0, -180.0, 180.0]]
        >>> print round(M[:4, :4].inverse(), 0).formated()
        [[16.0, -120.0, 240.0, -140.0],
         [-120.0, 1200.0, -2700.0, 1680.0],
         [240.0, -2700.0, 6480.0, -4200.0],
         [-140.0, 1680.0, -4200.0, 2800.0]]
        >>> print round(M[:5, :5].inverse(), 0).formated()
        [[25.0, -300.0, 1050.0, -1400.0, 630.0],
         [-300.0, 4800.0, -18900.0, 26880.0, -12600.0],
         [1050.0, -18900.0, 79380.0, -117600.0, 56700.0],
         [-1400.0, 26880.0, -117600.0, 179200.0, -88200.0],
         [630.0, -12600.0, 56700.0, -88200.0, 44100.0]]
        >>> print round(M[:6, :6].inverse(), 0).formated()
        [[36.0, -630.0, 3360.0, -7560.0, 7560.0, -2772.0],
         [-630.0, 14700.0, -88200.0, 211680.0, -220500.0, 83160.0],
         [3360.0, -88200.0, 564480.0, -1411200.0, 1512000.0, -582120.0],
         [-7560.0, 211680.0, -1411200.0, 3628800.0, -3969000.0, 1552320.0],
         [7560.0, -220500.0, 1512000.0, -3969000.0, 4410000.0, -1746360.0],
         [-2772.0, 83160.0, -582120.0, 1552320.0, -1746360.0, 698544.0]]
        
        >>> M = MatrixN(range(1, 10), shape=(3, 3))
        >>> print M.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> M.det()
        0
        >>> M.isSingular()
        True
        >>> print M.inverse().formated()
        Traceback (most recent call last):
            ...
        ValueError: MatrixN is not invertible
        """
    
        pass
    
    
    def isSingular(self, tol=9.313225746154785e-10):
        """
        m.isSingular([tol]) --> bool
        
        Returns True if m is singular, ie it's determinant is smaller than the given tolerance.
        
        >>> M = MatrixN(range(1, 5), shape=(2, 2))
        >>> print M.formated()
        [[1, 2],
         [3, 4]]
        >>> M.det()
        -2
        >>> M.isSingular()
        False
        
        >>> M = MatrixN(range(1, 10), shape=(3, 3))
        >>> print M.formated()
        [[1, 2, 3],
         [4, 5, 6],
         [7, 8, 9]]
        >>> M.det()
        0
        >>> M.isSingular()
        True
        """
    
        pass
    
    
    def is_square(self):
        """
        m.is_square() --> bool
        
        Returns True if m is a square MatrixN, it has the same number of rows and columns.
        
        >>> M = MatrixN(range(4), shape=(2, 2))
        >>> M.is_square()
        True
        >>> M = MatrixN(range(6), shape=(2, 3))
        >>> M.is_square()
        False
        """
    
        pass
    
    
    def linverse(self):
        """
        m.linverse() --> MatrixN
        
        Returns the left inverse matrix of m, the matrix n so that n * m = identity, if m is left-invertible,
        otherwise will raise a ValueError.
        If m is invertible then the left inverse of m is also it's right inverse, and it's inverse matrix.
        
        >>> M = MatrixN([[1, 2], [3, 4], [5, 6]])
        >>> print M.formated()
        [[1, 2],
         [3, 4],
         [5, 6]]
        >>> print round(M.linverse(), 2).formated()
        [[-1.33, -0.33, 0.67],
         [1.08, 0.33, -0.42]]
        """
    
        pass
    
    
    def minor(self, i, j):
        """
        m.minor(i, j) --> MatrixN
        
        Returns the MatrixN obtained by deleting row i and column j from m.
        
        >>> M = MatrixN(range(4), shape=(2, 2))
        >>> print M.formated()
        [[0, 1],
         [2, 3]]
        >>> M.minor(0, 0)
        MatrixN([[3]])
        >>> M.minor(0, 1)
        MatrixN([[2]])
        >>> M.minor(1, 0)
        MatrixN([[1]])
        >>> M.minor(1, 1)
        MatrixN([[0]])
        
        >>> M = MatrixN.identity(4)
        >>> M[:3, :3] = [float(i) for i in range(1, 10)]
        >>> print M.formated()
        [[1.0, 2.0, 3.0, 0.0],
         [4.0, 5.0, 6.0, 0.0],
         [7.0, 8.0, 9.0, 0.0],
         [0.0, 0.0, 0.0, 1.0]]
        >>> print M.minor(3, 3).formated()
        [[1.0, 2.0, 3.0],
         [4.0, 5.0, 6.0],
         [7.0, 8.0, 9.0]]
        """
    
        pass
    
    
    def reduced(self):
        """
        m.reduced() --> MatrixN
        
        Returns the reduced row echelon form of the matrix a by Gauss-Jordan elimination,
        followed by back substitution.
        
        >>> M = MatrixN([ [1.0/(i+j) for i in xrange(1,7)] for j in xrange(6) ])
        >>> print round(M, 2).formated()
        [[1.0, 0.5, 0.33, 0.25, 0.2, 0.17],
         [0.5, 0.33, 0.25, 0.2, 0.17, 0.14],
         [0.33, 0.25, 0.2, 0.17, 0.14, 0.13],
         [0.25, 0.2, 0.17, 0.14, 0.13, 0.11],
         [0.2, 0.17, 0.14, 0.13, 0.11, 0.1],
         [0.17, 0.14, 0.13, 0.11, 0.1, 0.09]]
        >>> print round(M[:1, :1].reduced(), 2).formated()
        [[1.0]]
        >>> print round(M[:2, :2].reduced(), 2).formated()
        [[1.0, 0.0],
         [0.0, 1.0]]
        >>> print round(M[:3, :3].reduced(), 2).formated() # doctest: +SKIP
        [[1.0, 0.0, 0.0],
         [0.0, 1.0, -0.0],
         [0.0, 0.0, 1.0]]
        >>> print round(M[:4, :4].reduced(), 2).formated() # doctest: +SKIP
        [[1.0, 0.0, 0.0, 0.0],
         [0.0, 1.0, -0.0, 0.0],
         [0.0, 0.0, 1.0, 0.0],
         [0.0, 0.0, 0.0, 1.0]]
        >>> print round(M[:5, :5].reduced(), 2).formated() # doctest: +SKIP
        [[1.0, 0.0, 0.0, 0.0, 0.0],
         [0.0, 1.0, -0.0, 0.0, -0.0],
         [0.0, 0.0, 1.0, 0.0, -0.0],
         [0.0, 0.0, 0.0, 1.0, -0.0],
         [0.0, 0.0, 0.0, -0.0, 1.0]]
        >>> print round(M[:6, :6].reduced(), 2).formated() # doctest: +SKIP
        [[1.0, 0.0, 0.0, 0.0, -0.0, 0.0],
         [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
         [0.0, 0.0, 1.0, 0.0, -0.0, 0.0],
         [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
         [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
         [0.0, 0.0, 0.0, 0.0, 0.0, 1.0]]
        
        >>> M = MatrixN([[1, 2, 3], [2, 4, 6], [6, 7, 8]])
        >>> print M.formated()
        [[1, 2, 3],
         [2, 4, 6],
         [6, 7, 8]]
        >>> M.det()
        0
        >>> M.isSingular()
        True
        >>> print M.reduced().formated()
        Traceback (most recent call last):
            ...
        ZeroDivisionError: MatrixN is singular
        """
    
        pass
    
    
    def rinverse(self):
        """
        m.rinverse() --> MatrixN
        
        Returns the right inverse matrix of m, the matrix n so that m * n = identity, if m is right-invertible,
        otherwise will raise a ValueError.
        If m is invertible then the right inverse of m is also it's left inverse, and it's inverse matrix.
        
        >>> M = MatrixN([[1, 2, 3], [4, 5, 6]])
        >>> print M.formated()
        [[1, 2, 3],
         [4, 5, 6]]
        >>> print round(M.rinverse(), 2).formated()
        [[-0.94, 0.44],
         [-0.11, 0.11],
         [0.72, -0.22]]
        """
    
        pass
    
    
    def trace(self, offset=0, wrap=False):
        """
        a.trace([offset=0[, wrap=False]]) -> float
        
        Returns the sum of the components on the diagonal, obtained by calling m.diagonal(offset, wrap).
        
        >>> M = MatrixN([[1, 2], [4, 6]])
        >>> print M.formated()
        [[1, 2],
         [4, 6]]
        >>> M.trace()
        7
        >>> M.trace(offset=1)
        2
        >>> M.trace(offset=1, wrap=True)
        6
        >>> M.trace(offset=-1)
        6
        >>> M.trace(offset=-1, wrap=True)
        6
        """
    
        pass
    
    
    def basis(cls, u, v, normalize=False):
        """
        MatrixN.basis(u, v[, normalize=False]) --> MatrixN
        
        Returns the basis MatrixN built using u, v and u^v as coordinate axis,
        The a, b, n vectors are recomputed to obtain an orthogonal coordinate system as follows:
            n = u ^ v
            v = n ^ u
        if the normalize keyword argument is set to True, the vectors are also normalized
        
        >>> M = MatrixN.basis(VectorN(0, 1, 0), VectorN(0, 0, 1))
        >>> print M.formated()
        [[0, 0, 1],
         [1, 0, 0],
         [0, 1, 0]]
        """
    
        pass
    
    
    def identity(cls, n):
        """
        MatrixN.identity(n) --> MatrixN
        
        Returns the identity MatrixN of size n :
        a square n x n MatrixN of 0.0, with all diagonal components set to 1.0.
        
        >>> I = MatrixN.identity(4)
        >>> print I.formated()
        [[1.0, 0.0, 0.0, 0.0],
         [0.0, 1.0, 0.0, 0.0],
         [0.0, 0.0, 1.0, 0.0],
         [0.0, 0.0, 0.0, 1.0]]
        """
    
        pass
    
    
    I = None
    
    col = None
    
    ncol = None
    
    nrow = None
    
    row = None
    
    shape = None
    
    size = None
    
    __readonly__ = {}
    
    
    ndim = 2


class VectorN(Array):
    """
    A generic size VectorN class derived from Array, basically a 1 dimensional Array.
    
    Most methods and behavior are herited from Array, with the limitation that a MatrixN must have
    exactly 2 dimensions.
    
    >>> V = VectorN()
    >>> V
    VectorN([])
    >>> V = VectorN([0, 1, 2])
    >>> V
    VectorN([0, 1, 2])
    >>> V = VectorN(0, 1, 2)
    >>> V
    VectorN([0, 1, 2])
    >>> M = MatrixN([[0], [1], [2]])
    >>> print M.formated()
    [[0],
     [1],
     [2]]
    >>> V = VectorN(M.col[0])
    >>> V
    VectorN([0, 1, 2])
    
    The VectorN class has a constant ndim of 1
    
    >>> VectorN.ndim
    1
    >>> V.ndim
    1
    >>> VectorN.ndim = 2
    Traceback (most recent call last):
        ...
    AttributeError: attribute ndim is a read only class attribute and cannot be modified on class VectorN
    >>> V.ndim = 2
    Traceback (most recent call last):
        ...
    AttributeError: 'VectorN' object attribute 'ndim' is read-only
    
    It's protected against initialization or resizing to a shape that wouldn't be a VectorN anymore
    
    >>> V = VectorN([[0, 1], [2, 3]])
    Traceback (most recent call last):
        ...
    TypeError: cannot initialize a VectorN of shape (4,) from [[0, 1], [2, 3]] of shape (2, 2),
    as it would truncate data or reduce the number of dimensions
    
    >>> V.resize((2, 2))
    Traceback (most recent call last):
        ...
    TypeError: new shape (2, 2) is not compatible with class VectorN
    
    Other Array types can be cast to VectorN, but truncating data or reducing dimensions is not allowed
    to avoid silent loss of data in a conversion, use an explicit resize / trim / sub-array extraction
    
    >>> A = Array(range(4), shape=(4,))
    >>> V = VectorN(A)
    >>> V
    VectorN([0, 1, 2, 3])
    
    >>> A = Array(range(4), shape=(2, 2))
    >>> V = VectorN(A)
    Traceback (most recent call last):
        ...
    TypeError: cannot cast a Array of shape (2, 2) to a VectorN of shape (4,),
    as it would truncate data or reduce the number of dimensions
    
    As for Array, __init__ is a shallow copy, note that as VectorN don't have sub-arrays,
    shallow and deep copy amounts to the same thing.
    
    >>> A = Array(range(4), shape=(4,))
    >>> V = VectorN(A)
    >>> V == A
    False
    >>> V is A
    False
    >>> V.isEquivalent(A)
    True
    >>> V[0] == A[0]
    True
    >>> V[0] is A[0]
    True
    """
    
    
    
    def __imul__(self, other):
        """
        a.__imul__(b) <==> a *= b
        
        In place multiplication of VectorN a and b, see __mul__, result must fit a's type
        """
    
        pass
    
    
    def __ixor__(self, other):
        """
        a.__xor__(b) <==> a^=b
        
        Inplace cross product or transformation by inverse transpose MatrixN of b is v is a MatrixN
        """
    
        pass
    
    
    def __mul__(self, other):
        """
        a.__mul__(b) <==> a*b
        
        If b is a VectorN, __mul__ is mapped to the dot product of the two vectors a and b,
        If b is a MatrixN, __mul__ is mapped to VectorN a by MatrixN b multiplication (post multiplication or transformation of a by b),
        otherwise, returns the result of the element wise multiplication of a and b if b is convertible to Array,
        multiplies every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __rmul__(self, other):
        """
        a.__rmul__(b) <==> b*a
        
        If b is a VectorN, __rmul__ is mapped to the dot product of the two vectors a and b,
        If b is a MatrixN, __rmul__ is mapped to MatrixN b by VectorN a multiplication,
        otherwise, returns the result of the element wise multiplication of b and a if b is convertible to Array,
        multiplies every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __xor__(self, other):
        """
        a.__xor__(b) <==> a^b
        
        Defines the cross product operator between two vectors,
        if b is a MatrixN, a^b is equivalent to transforming a by the inverse transpose MatrixN of b,
        often used to transform normals
        """
    
        pass
    
    
    def angle(self, other, third=None):
        """
        u.angle(v) <==> angle(u, v) --> float
        
        Returns the angle of rotation between u and v, 3 dimensional Vectors representing 3D vectors.
        
        Note : this angle is not signed, use axis to know the direction of the rotation
        
        Alternatively can use the form a.angle(b, c), where a, b, c are 4 dimensional Vectors representing 3D points,
        it is then equivalent to angle(b-a, c-a)
        """
    
        pass
    
    
    def axis(self, other, third=None, normalize=False):
        """
        u.axis(v[, normalize=False]) <==> axis(u, v[, normalize=False])
        
        Returns the axis of rotation from u to v as the vector n = u ^ v, u and v
        being 3 dimensional Vectors representing 3D vectors.
        If the normalize keyword argument is set to True, n is also normalized.
        
        
        Alternatively can use the form a.axis(b, c), where a, b, c are 4 dimensional Vectors representing 3D points,
        it is then equivalent to axis(b-a, c-a).
        """
    
        pass
    
    
    def cotan(self, other, third=None):
        """
        u.cotan(v) <==> cotan(u, v)
        
        Returns the cotangent of the u, v angle, u and v should be 3 dimensional Vectors representing 3D vectors.
        
        Alternatively can use the form a.cotan(b, c), where a, b, c are 4 dimensional Vectors representing 3D points,
        it is then equivalent to cotan(b-a, c-a)
        """
    
        pass
    
    
    def cross(self, other):
        """
        u.cross(v) <==> cross(u, v)
        
        cross product of u and v, u and v should be 3 dimensional vectors.
        """
    
        pass
    
    
    def dot(self, other):
        """
        u.dot(v) <==> dot(u, v)
        
        dot product of u and v, u and v should be Vectors of identical size.
        """
    
        pass
    
    
    def isParallel(self, other, tol=9.313225746154785e-10):
        """
        u.isParallel(v[, tol]) --> bool
        
        Returns True if both arguments considered as VectorN are parallel within the specified tolerance
        """
    
        pass
    
    
    def length(self):
        """
        u.length() --> float
        
        Returns the length of u, ie sqrt(u.dot(u))
        """
    
        pass
    
    
    def normal(self):
        """
        u.normal() --> VectorN
        
        Returns a normalized copy of self. Overriden to be consistant with Maya API and MEL unit command,
        does not raise an exception if self if of zero length, instead returns a copy of self
        """
    
        pass
    
    
    def outer(self, other):
        """
        u.outer(v) <==> outer(u, v)
        
        Outer product of vectors u and v
        """
    
        pass
    
    
    def projectionOnto(self, other):
        """
        Returns the projection of this vector onto other vector.
        """
    
        pass
    
    
    def sqlength(self):
        """
        u.sqlength() --> float
        
        Returns the square length of u, ie u.dot(u).
        """
    
        pass
    
    
    def transformAsNormal(self, other):
        """
        u.transformAsNormal(m) --> VectorN
        
        Equivalent to transforming u by the inverse transpose MatrixN of m, used to transform normals.
        """
    
        pass
    
    
    def unit(self):
        """
        u.normal() --> VectorN
        
        Returns a normalized copy of self. Overriden to be consistant with Maya API and MEL unit command,
        does not raise an exception if self if of zero length, instead returns a copy of self
        """
    
        pass
    
    
    shape = None
    
    size = None
    
    __readonly__ = {}
    
    
    ndim = 1



def smoothstep(*args, **kwargs):
    """
    Returns the value of a smooth step function.
    
        Returns 0 if x < min, 1 if x > max, and performs a smooth Hermite
        interpolation between 0 and 1 in the interval min to max.
    
        :rtype: float
        
    This function has been overriden from pymel.util.mathutils.smoothstep to work element-wise on iterables
    """

    pass


def tanh(*args, **kwargs):
    """
    tanh(x)
    
    Return the hyperbolic tangent of x.
    This function has been overriden from math.tanh to work element-wise on iterables
    """

    pass


def asin(*args, **kwargs):
    """
    asin(x)
    
    Return the arc sine (measured in radians) of x.
    This function has been overriden from math.asin to work element-wise on iterables
    """

    pass


def floor(*args, **kwargs):
    """
    floor(x)
    
    Return the floor of x as a float.
    This is the largest integral value <= x.
    This function has been overriden from math.floor to work element-wise on iterables
    """

    pass


def isnan(*args, **kwargs):
    """
    isnan(x) -> bool
    
    Check if float x is not a number (NaN).
    This function has been overriden from math.isnan to work element-wise on iterables
    """

    pass


def normal(a, axis=None):
    """
    normal(a[, axis=(axis0, axis1, ...)]) --> Array
    
    Returns a normalized copy of self: self/length(self, axis).
    
    >>> A = Array([[0.5,0.5,-0.707],[0.707,-0.707,0.0]])
    >>> print A.formated()
    [[0.5, 0.5, -0.707],
     [0.707, -0.707, 0.0]]
    >>> print normal(A).formated()
    [[0.353593437318, 0.353593437318, -0.499981120367],
     [0.499981120367, -0.499981120367, 0.0]]
    >>> print normal(A, axis=(0,1)).formated()
    [[0.353593437318, 0.353593437318, -0.499981120367],
     [0.499981120367, -0.499981120367, 0.0]]
    >>> print normal(A, axis=0).formated()
    [[0.5, 0.5, -0.707],
     [0.707, -0.707, 0.0]]
    >>> print normal(A, axis=1).formated()
    [[0.577408397894, 0.577408397894, -1.0],
     [0.816455474623, -0.816455474623, 0.0]]
    """

    pass


def dist(a, b, axis=None):
    """
    dist(a, b[, axis=(axis0, axis1, ...)]) --> float or Array
    
    Returns the distance between a and b, ie length(b-a, axis)
    
    >>> A = Array([[0.5, 0.5, -0.707],[0.707, -0.707, 0.0]])
    >>> print A.formated()
    [[0.5, 0.5, -0.707],
     [0.707, -0.707, 0.0]]
    >>> B = Array([[0.51, 0.49, -0.71],[0.71, -0.70, 0.0]])
    >>> print B.formated()
    [[0.51, 0.49, -0.71],
     [0.71, -0.7, 0.0]]
    >>> length(B-A)
    0.016340134638368205
    >>> dist(A, B)
    0.016340134638368205
    >>> dist(A, B, axis=(0, 1))
    0.016340134638368205
    >>> dist(A, B, axis=0)
    Array([0.0144568322948, 0.00761577310586])
    >>> dist(A, B, axis=1)
    Array([0.0104403065089, 0.0122065556157, 0.003])
    """

    pass


def exp(*args, **kwargs):
    """
    exp(x)
    
    Return e raised to the power of x.
    This function has been overriden from math.exp to work element-wise on iterables
    """

    pass


def outer(u, v):
    """
    outer(u, v) --> MatrixN
    
    Returns the outer product of vectors u and v.
    
    >>> u = VectorN(1.0, 2.0, 3.0)
    >>> v = VectorN(10.0, 20.0, 30.0)
    >>> outer(u, v)
    MatrixN([[10.0, 20.0, 30.0], [20.0, 40.0, 60.0], [30.0, 60.0, 90.0]])
    >>> outer(u, [10.0, 20.0, 30.0])
    MatrixN([[10.0, 20.0, 30.0], [20.0, 40.0, 60.0], [30.0, 60.0, 90.0]])
    
    Related : see VectorN.outer method.
    """

    pass


def cotan(a, b, c=None):
    """
    cotan(u, v) --> float :
    
    Returns the cotangent of the u, v angle, u and v should be 3 dimensional Vectors representing 3D vectors.
    
    >>> u = VectorN(1.0, 0.0, 0.0)
    >>> v = VectorN(0.707, 0.0, -0.707)
    >>> cotan(u, v)
    1.0
    >>> cotan(u, [0.707, 0.0, -0.707])
    1.0
    
    Alternatively can use the form cotan(a, b, c), where a, b, c are 4 dimensional Vectors representing 3D points,
    it is then equivalent to cotan(b-a, c-a).
    
    >>> o = VectorN(0.0, 1.0, 0.0, 1.0)
    >>> p = VectorN(1.0, 1.0, 0.0, 1.0)
    >>> q = VectorN(0.707, 1.0, -0.707, 1.0)
    >>> cotan(o, p, q)
    1.0
    
    Related : see VectorN.cotan method.
    """

    pass


def blend(*args, **kwargs):
    """
        blend(a, b[, weight=0.5]) :
        Blends values a and b according to normalized weight w,
        returns a for weight == 0.0 and b for weight = 1.0, a*(1.0-weight)+b*weight in between
    
        :rtype: float
        
    This function has been overriden from pymel.util.mathutils.blend to work element-wise on iterables
    """

    pass


def lgamma(*args, **kwargs):
    """
    lgamma(x)
    
    Natural logarithm of absolute value of Gamma function at x.
    This function has been overriden from math.lgamma to work element-wise on iterables
    """

    pass


def sqlength(a, axis=None):
    """
    sqlength(a[, axis=(axis0, axis1, ...)]) --> numeric or Array
    
    Returns square length of a, ie a*a or the sum of x*x for x in a if a is an iterable of numeric values.
    If a is an Array and axis are specified will return a list of sqlength(x) for x in a.axisiter(*axis).
    
    >>> A = Array([[0.5,0.5,-0.707],[0.707,-0.707,0.0]])
    >>> print A.formated()
    [[0.5, 0.5, -0.707],
     [0.707, -0.707, 0.0]]
    >>> sqlength(A)
    1.999547
    >>> sqlength(A, axis=(0,1))
    1.999547
    >>> sqlength(A, axis=0)
    Array([0.999849, 0.999698])
    >>> sqlength(A, axis=1)
    Array([0.749849, 0.749849, 0.499849])
    """

    pass


def gamma(*args, **kwargs):
    """
        Gamma color correction of c with a single scalar gamma value g
    
        :rtype: float
        
    This function has been overriden from pymel.util.mathutils.gamma to work element-wise on iterables
    """

    pass


def length(a, axis=None):
    """
    length(a[, axis=(axis0, axis1, ...)]) --> numeric or Array
    
    Returns length of a, sqrt(a*a) or the square root of the sum of x*x for x in a if a is an iterable of numeric values.
    If a is an Array and axis are specified will return a list of length(x) for x in a.axisiter(*axis).
    
    >>> A = Array([[0.5,0.5,-0.707],[0.707,-0.707,0.0]])
    >>> print A.formated()
    [[0.5, 0.5, -0.707],
     [0.707, -0.707, 0.0]]
    >>> round(length(A), 7)
    1.4140534
    >>> round(length(A, axis=(0,1)), 7)
    1.4140534
    >>> length(A, axis=0)
    Array([0.99992449715, 0.999848988598])
    >>> length(A, axis=1)
    Array([0.865938219505, 0.865938219505, 0.707])
    """

    pass


def ceil(*args, **kwargs):
    """
    ceil(x)
    
    Return the ceiling of x as a float.
    This is the smallest integral value >= x.
    This function has been overriden from math.ceil to work element-wise on iterables
    """

    pass


def prod(a, start=1, axis=None):
    """
    prod(a[, start=1[, axis=(axis0, axis1, ...)]]) --> numeric or Array
    
    Returns the product of all the components of a, an iterable of values that support the mul operator, times start.
    If axis are specified will return an Array of prod(x) for x in a.axisiter(*axis).
    
    >>> A = Array([[1,2,3],[4,5,6]])
    >>> print A.formated()
    [[1, 2, 3],
     [4, 5, 6]]
    >>> prod(A)
    720
    >>> prod(A, axis=(0, 1))
    720
    >>> prod(A, axis=0)
    Array([4, 10, 18])
    >>> prod(A, axis=1)
    Array([6, 120])
    """

    pass


def hypot(*args, **kwargs):
    """
    hypot(x, y)
    
    Return the Euclidean distance, sqrt(x*x + y*y).
    This function has been overriden from math.hypot to work element-wise on iterables
    """

    pass


def log1p(*args, **kwargs):
    """
    log1p(x)
    
    Return the natural logarithm of 1+x (base e).
    The result is computed in a way which is accurate for x near zero.
    This function has been overriden from math.log1p to work element-wise on iterables
    """

    pass


def angle(a, b, c=None):
    """
    angle(u, v) --> float
    
    Returns the angle of rotation between u and v.
    u and v should be 3 dimensional Vectors representing 3D vectors.
    
    Note: this angle is not signed, use axis to know the direction of the rotation.
    
    >>> u = VectorN(1.0, 0.0, 0.0)
    >>> v = VectorN(0.707, 0.0, -0.707)
    >>> print round(angle(u, v), 7)
    0.7853982
    >>> print round(angle(u, [0.707, 0.0, -0.707]), 7)
    0.7853982
    
    Alternatively can use the form angle(a, b, c), where a, b, c are 4 dimensional Vectors representing 3D points,
    it is then equivalent to angle(b-a, c-a)
    
    >>> o = VectorN(0.0, 1.0, 0.0, 1.0)
    >>> p = VectorN(1.0, 1.0, 0.0, 1.0)
    >>> q = VectorN(0.707, 1.0, -0.707, 1.0)
    >>> print round(angle(o, p, q), 7)
    0.7853982
    
    Related : see VectorN.angle method.
    """

    pass


def _toCompOrArray(value):
    pass


def modf(*args, **kwargs):
    """
    modf(x)
    
    Return the fractional and integer parts of x.  Both results carry the sign
    of x and are floats.
    This function has been overriden from math.modf to work element-wise on iterables
    """

    pass


def fmod(*args, **kwargs):
    """
    fmod(x, y)
    
    Return fmod(x, y), according to platform C.  x % y may differ.
    This function has been overriden from math.fmod to work element-wise on iterables
    """

    pass


def acos(*args, **kwargs):
    """
    acos(x)
    
    Return the arc cosine (measured in radians) of x.
    This function has been overriden from math.acos to work element-wise on iterables
    """

    pass


def pow(*args, **kwargs):
    """
    pow(x, y)
    
    Return x**y (x to the power of y).
    This function has been overriden from math.pow to work element-wise on iterables
    """

    pass


def cross(u, v):
    """
    cross(u, v) --> VectorN
    
    Returns the cross product of u and v, u and v should be 3 dimensional vectors.
    
    >>> u = VectorN(1.0, 0.0, 0.0)
    >>> v = VectorN(0.0, 1.0, 0.0)
    >>> cross(u, v)
    VectorN([0.0, 0.0, 1.0])
    >>> cross(u, [0.0, 1.0, 0.0])
    VectorN([0.0, 0.0, 1.0])
    
    Related : see VectorN.cross method.
    """

    pass


def linstep(*args, **kwargs):
    """
    Returns the value of a linear step function.
    
        Returns 0 if x < min, 1 if x > max, and performs a linear
        interpolation between 0 and 1 in the interval min to max.
    
        :rtype: float
        
    This function has been overriden from pymel.util.mathutils.linstep to work element-wise on iterables
    """

    pass


def degrees(*args, **kwargs):
    """
    degrees(x)
    
    Convert angle x from radians to degrees.
    This function has been overriden from math.degrees to work element-wise on iterables
    """

    pass


def log(*args, **kwargs):
    """
    log(x[, base])
    
    Return the logarithm of x to the given base.
    If the base not specified, returns the natural logarithm (base e) of x.
    This function has been overriden from math.log to work element-wise on iterables
    """

    pass


def sin(*args, **kwargs):
    """
    sin(x)
    
    Return the sine of x (measured in radians).
    This function has been overriden from math.sin to work element-wise on iterables
    """

    pass


def abs(*args, **kwargs):
    """
    abs(number) -> number
    
    Return the absolute value of the argument.
    This function has been overriden from __builtin__.abs to work element-wise on iterables
    """

    pass


def sinh(*args, **kwargs):
    """
    sinh(x)
    
    Return the hyperbolic sine of x.
    This function has been overriden from math.sinh to work element-wise on iterables
    """

    pass


def copysign(*args, **kwargs):
    """
    copysign(x, y)
    
    Return x with the sign of y.
    This function has been overriden from math.copysign to work element-wise on iterables
    """

    pass


def isinf(*args, **kwargs):
    """
    isinf(x) -> bool
    
    Check if float x is infinite (positive or negative).
    This function has been overriden from math.isinf to work element-wise on iterables
    """

    pass


def ldexp(*args, **kwargs):
    """
    ldexp(x, i)
    
    Return x * (2**i).
    This function has been overriden from math.ldexp to work element-wise on iterables
    """

    pass


def cosh(*args, **kwargs):
    """
    cosh(x)
    
    Return the hyperbolic cosine of x.
    This function has been overriden from math.cosh to work element-wise on iterables
    """

    pass


def sqrt(*args, **kwargs):
    """
    sqrt(x)
    
    Return the square root of x.
    This function has been overriden from math.sqrt to work element-wise on iterables
    """

    pass


def _patchfn(basefn):
    """
    Overload the given base function to have it accept iterables
    """

    pass


def inv(value):
    """
    inv(m) --> MatrixN
    
    Returns the inverse of m, if m is invertible, raises ZeroDivisionError otherwise.
    m must be convertible to MatrixN.
    
    Related : see MatrixN.inverse(self) method and MatrixN.I property
    """

    pass


def hermite(*args, **kwargs):
    """
        As the MEL command : This command returns x point along on x hermite curve from the five given control arguments.
        The first two arguments are the start and end points of the curve, respectively.
        The next two arguments are the tangents of the curve at the start point and end point of the curve, respectively.
        The fifth argument, parameter, specifies the point on the hermite curve that is returned by this function.
        This parameter is the unitized distance along the curve from the start point to the end point.
        A parameter value of 0.0 corresponds to the start point and x parameter value of 1.0 corresponds to the end point of the curve.
    
        :rtype: float
    
        
    This function has been overriden from pymel.util.mathutils.hermite to work element-wise on iterables
    """

    pass


def axis(a, b, c=None, normalize=False):
    """
    axis(u, v[, normalize=False]) --> VectorN
    
    Returns the axis of rotation from u to v as the vector n = u ^ v
    if the normalize keyword argument is set to True, n is also normalized.
    u and v should be 3 dimensional Vectors representing 3D vectors.
    
    >>> u = VectorN(1.0, 0.0, 0.0)
    >>> v = VectorN(0.707, 0.0, -0.707)
    >>> axis(u, v) == VectorN([0.0, 0.707, 0.0])
    True
    >>> axis(u, [0.707, 0.0, -0.707], normalize=True) == VectorN([-0.0, 1.0, 0.0])
    True
    
    Alternatively can use the form axis(a, b, c), where a, b, c are 4 dimensional Vectors representing 3D points,
    it is then equivalent to axis(b-a, c-a).
    
    >>> o = VectorN(0.0, 1.0, 0.0, 1.0)
    >>> p = VectorN(1.0, 1.0, 0.0, 1.0)
    >>> q = VectorN(0.707, 1.0, -0.707, 1.0)
    >>> axis(o, p, q, normalize=True) == VectorN([0.0, 1.0, 0.0])
    True
    
    Related : see VectorN.axis method.
    """

    pass


def frexp(*args, **kwargs):
    """
    frexp(x)
    
    Return the mantissa and exponent of x, as pair (m, e).
    m is a float and e is an int, such that x = m * 2.**e.
    If x is 0, m and e are both 0.  Else 0.5 <= abs(m) < 1.0.
    This function has been overriden from math.frexp to work element-wise on iterables
    """

    pass


def asinh(*args, **kwargs):
    """
    asinh(x)
    
    Return the inverse hyperbolic sine of x.
    This function has been overriden from math.asinh to work element-wise on iterables
    """

    pass


def clamp(*args, **kwargs):
    """
    Clamps the value x between min and max
    
        :rtype: float
        
    This function has been overriden from pymel.util.mathutils.clamp to work element-wise on iterables
    """

    pass


def radians(*args, **kwargs):
    """
    radians(x)
    
    Convert angle x from degrees to radians.
    This function has been overriden from math.radians to work element-wise on iterables
    """

    pass


def fabs(*args, **kwargs):
    """
    fabs(x)
    
    Return the absolute value of the float x.
    This function has been overriden from math.fabs to work element-wise on iterables
    """

    pass


def linmap(*args, **kwargs):
    """
    Returns the value of a linear remapping function.
    
        performs a linear interpolation between 0 and 1 in the interval min to max,
        but does not clamp the range
    
        :rtype: float
        
    This function has been overriden from pymel.util.mathutils.linmap to work element-wise on iterables
    """

    pass


def imag(*args, **kwargs):
    """
    the imaginary part of x 
    This function has been overriden from pymel.util.mathutils.imag to work element-wise on iterables
    """

    pass


def trunc(*args, **kwargs):
    """
    trunc(x:Real) -> Integral
    
    Truncates x to the nearest Integral toward 0. Uses the __trunc__ magic method.
    This function has been overriden from math.trunc to work element-wise on iterables
    """

    pass


def log10(*args, **kwargs):
    """
    log10(x)
    
    Return the base 10 logarithm of x.
    This function has been overriden from math.log10 to work element-wise on iterables
    """

    pass


def hermiteInterp(*args, **kwargs):
    """
    Hermite interpolation of x between points y0 and y1 of tangent slope s0 and s1
    
        :rtype: float
        
    This function has been overriden from pymel.util.mathutils.hermiteInterp to work element-wise on iterables
    """

    pass


def conjugate(*args, **kwargs):
    """
    the conjugate part of x 
    This function has been overriden from pymel.util.mathutils.conjugate to work element-wise on iterables
    """

    pass


def all(a, axis=None):
    """
    all(a, [,axis=(axis0, axis1, ...)]) --> bool or Array of booleans
    
    Returns True if all the components of iterable a evaluate to True.
    If axis are specified will return an Array of all(x) for x in a.axisiter(*axis).
    
    >>> A = Array([[True,True,True],[False,True,False]])
    >>> print A.formated()
    [[True, True, True],
     [False, True, False]]
    >>> all(A)
    False
    >>> all(A, axis=(0, 1))
    False
    >>> all(A, axis=0)
    Array([False, True, False])
    >>> all(A, axis=1)
    Array([True, False])
    """

    pass


def _toCompOrArrayInstance(value, cls=None):
    pass


def dot(u, v):
    """
    dot(u, v) --> float
    
    Returns the dot product of u and v, u and v should be Vectors of identical size.
    
    >>> u = VectorN(1.0, 0.0, 0.0)
    >>> v = VectorN(0.707, 0.0, -0.707)
    >>> print round(dot(u, v), 3)
    0.707
    >>> print round(dot(u, [0.707, 0.0, -0.707]), 3)
    0.707
    
    Related : see VectorN.dot method.
    """

    pass


def atan2(*args, **kwargs):
    """
    atan2(y, x)
    
    Return the arc tangent (measured in radians) of y/x.
    Unlike atan(y/x), the signs of both x and y are considered.
    This function has been overriden from math.atan2 to work element-wise on iterables
    """

    pass


def fsum(*args, **kwargs):
    """
    fsum(iterable)
    
    Return an accurate floating point sum of values in the iterable.
    Assumes IEEE-754 floating point arithmetic.
    This function has been overriden from math.fsum to work element-wise on iterables
    """

    pass


def erf(*args, **kwargs):
    """
    erf(x)
    
    Error function at x.
    This function has been overriden from math.erf to work element-wise on iterables
    """

    pass


def setRange(*args, **kwargs):
    """
    Resets x range from x linear interpolation of oldmin to oldmax to x linear interpolation from newmin to newmax
    
        :rtype: float
        
    This function has been overriden from pymel.util.mathutils.setRange to work element-wise on iterables
    """

    pass


def acosh(*args, **kwargs):
    """
    acosh(x)
    
    Return the inverse hyperbolic cosine of x.
    This function has been overriden from math.acosh to work element-wise on iterables
    """

    pass


def round(*args, **kwargs):
    """
        round(number[, ndigits]) -> float
        Round a number to a given precision in decimal digits (default 0 digits).
        This always returns a floating point number.  Precision may be negative.
        This builtin function was overloaded in mathutils to work on complex numbers,
        in that case rel and imaginary values are rounded separately
    
        
    This function has been overriden from pymel.util.mathutils.round to work element-wise on iterables
    """

    pass


def factorial(*args, **kwargs):
    """
    factorial(x) -> Integral
    
    Find x!. Raise a ValueError if x is negative or non-integral.
    This function has been overriden from math.factorial to work element-wise on iterables
    """

    pass


def smoothmap(*args, **kwargs):
    """
    Returns the value of a smooth remapping function.
    
        performs a smooth Hermite interpolation between 0 and 1 in the interval min to max,
        but does not clamp the range
    
        :rtype: float
        
    This function has been overriden from pymel.util.mathutils.smoothmap to work element-wise on iterables
    """

    pass


def patchMath():
    """
    Overload various math functions to work element-wise on iterables
    
    >>> A = Array([[0, pi/4.0], [pi/2.0, 3.0*pi/4.0], [pi, 5.0*pi/4.0], [3.0*pi/2.0, 7.0*pi/4.0]])
    >>> print round(A,2).formated()
    [[0.0, 0.79],
     [1.57, 2.36],
     [3.14, 3.93],
     [4.71, 5.5]]
    >>> print degrees(A).formated()
    [[0.0, 45.0],
     [90.0, 135.0],
     [180.0, 225.0],
     [270.0, 315.0]]
    >>> print round(sin(A), 2).formated()
    [[0.0, 0.71],
     [1.0, 0.71],
     [0.0, -0.71],
     [-1.0, -0.71]]
    """

    pass


def _shapeInfo(value):
    pass


def max(*args, **kwargs):
    """
    max(iterable[, key=func[, axis=(axis0, axis1, ...)]]) --> value
    max(a, b, c, ...[, key=func[, axis=(axis0, axis1, ...)]]) --> value
    
    With a single iterable argument, return its largest item.
    With two or more arguments, return the largest argument.
    If the iterable argument is an Array instance, returns the largest component of iterable.
    If axis are specified will return an Array of element-wise max(x) for x in a.axisiter(*axis).
    
    >>> A = Array([[6,3,4],[1,5,0.5]])
    >>> print A.formated()
    [[6, 3, 4],
     [1, 5, 0.5]]
    >>> max(A)
    6
    >>> max(A, axis=(0, 1))
    6
    >>> max(A, axis=0)
    Array([6, 5, 4])
    >>> max(A, axis=1)
    Array([6, 5])
    """

    pass


def erfc(*args, **kwargs):
    """
    erfc(x)
    
    Complementary error function at x.
    This function has been overriden from math.erfc to work element-wise on iterables
    """

    pass


def real(*args, **kwargs):
    """
    the real part of x 
    This function has been overriden from pymel.util.mathutils.real to work element-wise on iterables
    """

    pass


def det(value):
    """
    det(m) --> float
    
    Returns the determinant of m, 0 if m is a singular MatrixN, m must be convertible to MatrixN.
    
    Related : see MatrixN.det(self) method.
    """

    pass


def min(*args, **kwargs):
    """
    min(iterable[, key=func[, axis=(axis0, axis1, ...)]]) --> value
    min(a, b, c, ...[, key=func[, axis=(axis0, axis1, ...)]]) --> value
    
    With a single iterable argument, return its smallest item.
    With two or more arguments, return the smallest argument.
    If the iterable argument is an Array instance, returns the smallest component of iterable.
    If axis are specified will return an Array of element-wise min(x) for x in a.axisiter(*axis).
    
    >>> A = Array([[6,3,4],[1,5,0.5]])
    >>> print A.formated()
    [[6, 3, 4],
     [1, 5, 0.5]]
    >>> min(A)
    0.5
    >>> min(A, axis=(0,1))
    0.5
    >>> min(A, axis=0)
    Array([1, 3, 0.5])
    >>> min(A, axis=1)
    Array([3, 0.5])
    """

    pass


def atan(*args, **kwargs):
    """
    atan(x)
    
    Return the arc tangent (measured in radians) of x.
    This function has been overriden from math.atan to work element-wise on iterables
    """

    pass


def sum(a, start=0, axis=None):
    """
    sum(a[, start=0[, axis=(axis0, axis1, ...)]]) --> numeric or Array
    
    Returns the sum of all the components of a, an iterable of values that support the add operator, plus start.
    If a is an Array and axis are specified will return an Array of sum(x) for x in a.axisiter(*axis)
    
    >>> A = Array([[1,2,3],[4,5,6]])
    >>> print A.formated()
    [[1, 2, 3],
     [4, 5, 6]]
    >>> sum(A)
    21
    >>> sum(A, axis=(0, 1))
    21
    >>> sum(A, axis=0)
    Array([5, 7, 9])
    >>> sum(A, axis=1)
    Array([6, 15])
    """

    pass


def cos(*args, **kwargs):
    """
    cos(x)
    
    Return the cosine of x (measured in radians).
    This function has been overriden from math.cos to work element-wise on iterables
    """

    pass


def atanh(*args, **kwargs):
    """
    atanh(x)
    
    Return the inverse hyperbolic tangent of x.
    This function has been overriden from math.atanh to work element-wise on iterables
    """

    pass


def tan(*args, **kwargs):
    """
    tan(x)
    
    Return the tangent of x (measured in radians).
    This function has been overriden from math.tan to work element-wise on iterables
    """

    pass


def expm1(*args, **kwargs):
    """
    expm1(x)
    
    Return exp(x)-1.
    This function avoids the loss of precision involved in the direct evaluation of exp(x)-1 for small x.
    This function has been overriden from math.expm1 to work element-wise on iterables
    """

    pass


def any(a, axis=None):
    """
    any(a [,axis=(axis0, axis1, ...)]) --> bool or Array of booleans
    
    Returns True if any of the components of iterable a evaluate to True.
    If axis are specified will return an Array of any(x) for x in a.axisiter(*axis).
    
    >>> A = Array([[False,True,True],[False,True,False]])
    >>> print A.formated()
    [[False, True, True],
     [False, True, False]]
    >>> any(A)
    True
    >>> any(A, axis=(0, 1))
    True
    >>> any(A, axis=0)
    Array([False, True, True])
    >>> any(A, axis=1)
    Array([True, True])
    """

    pass



eps = 9.313225746154785e-10

pi = 3.141592653589793


