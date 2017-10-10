"""
A wrap of Maya's Vector, Point, Color, Matrix, TransformationMatrix, Quaternion, EulerRotation types
"""

from pymel.util.arrays import *

from maya.OpenMaya import MBoundingBox as _MBoundingBox
from maya.OpenMaya import MFloatMatrix as _MFloatMatrix
from maya.OpenMaya import MQuaternion as _MQuaternion
from maya.OpenMaya import MSpace as _MSpace
from maya.OpenMaya import MVector as _MVector
from maya.OpenMaya import MPoint as _MPoint
from maya.OpenMaya import MFloatVector as _MFloatVector
from maya.OpenMaya import MTransformationMatrix as _MTransformationMatrix
from pymel.util.arrays import _toCompOrArrayInstance
from maya.OpenMaya import MEulerRotation as _MEulerRotation
from maya.OpenMaya import MFloatPoint as _MFloatPoint
from maya.OpenMaya import MColor as _MColor
from maya.OpenMaya import MMatrix as _MMatrix

class Matrix(MatrixN, _MMatrix):
    """
    A 4x4 transformation matrix based on api Matrix
    
    >>> from pymel.all import *
    >>> import pymel.core.datatypes as dt
    >>>
    >>> i = dt.Matrix()
    >>> print i.formated()
    [[1.0, 0.0, 0.0, 0.0],
     [0.0, 1.0, 0.0, 0.0],
     [0.0, 0.0, 1.0, 0.0],
     [0.0, 0.0, 0.0, 1.0]]
    
    >>> v = dt.Matrix(1, 2, 3)
    >>> print v.formated()
    [[1.0, 2.0, 3.0, 0.0],
     [1.0, 2.0, 3.0, 0.0],
     [1.0, 2.0, 3.0, 0.0],
     [1.0, 2.0, 3.0, 0.0]]
    """
    
    
    
    def __add__(self, other):
        """
        m.__add__(v) <==> m+v
        Returns the result of the addition of m and v if v is convertible to a MatrixN (element-wise addition),
        adds v to every component of m if v is a scalar
        """
    
        pass
    
    
    def __delitem__(self, index):
        """
        Cannot delete from a class with a fixed shape
        """
    
        pass
    
    
    def __delslice__(self, start, end):
        pass
    
    
    def __eq__(self, other):
        """
        m.__eq__(v) <==> m == v
        Equivalence test
        """
    
        pass
    
    
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    def __getitem__(self, index):
        """
        m.__getitem__(index) <==> m[index]
        Get component index value from self.
        index can be a single numeric value or slice, thus one or more rows will be returned,
        or a row,column tuple of numeric values / slices
        """
    
        pass
    
    
    def __getslice__(self, start, end):
        """
        # deprecated and __getitem__ should accept slices anyway
        """
    
        pass
    
    
    def __iadd__(self, other):
        """
        m.__iadd__(v) <==> m += v
        In place addition of m and v, see __add__
        """
    
        pass
    
    
    def __imul__(self, other):
        """
        m.__imul__(n) <==> m *= n
        Valid for Matrix * Matrix multiplication, in place multiplication of MatrixN m by MatrixN n
        """
    
        pass
    
    
    def __init__(self, *args, **kwargs):
        """
        __init__ method, valid for Vector, Point and Color classes
        """
    
        pass
    
    
    def __isub__(self, other):
        """
        m.__isub__(v) <==> m -= v
        In place substraction of m and v, see __sub__
        """
    
        pass
    
    
    def __iter__(self, *args, **kwargs):
        """
        Iterate on the Matrix rows
        """
    
        pass
    
    
    def __len__(self):
        """
        Number of components in the Matrix instance
        """
    
        pass
    
    
    def __melobject__(self):
        """
        Special method for returning a mel-friendly representation. In this case, a flat list of 16 values
        """
    
        pass
    
    
    def __mul__(self, other):
        """
        m.__mul__(x) <==> m*x
        If x is a MatrixN, __mul__ is mapped to matrix multiplication m*x, if x is a VectorN, to MatrixN by VectorN multiplication.
        Otherwise, returns the result of the element wise multiplication of m and x if x is convertible to Array,
        multiplies every component of b by x if x is a single numeric value
        """
    
        pass
    
    
    def __ne__(self, other):
        """
        m.__ne__(v) <==> m != v
        Equivalence test
        """
    
        pass
    
    
    def __neg__(self):
        """
        m.__neg__() <==> -m
        The unary minus operator. Negates the value of each of the components of m
        """
    
        pass
    
    
    def __radd__(self, other):
        """
        m.__radd__(v) <==> v+m
        Returns the result of the addition of m and v if v is convertible to a MatrixN (element-wise addition),
        adds v to every component of m if v is a scalar
        """
    
        pass
    
    
    def __rmul__(self, other):
        """
        m.__rmul__(x) <==> x*m
        If x is a MatrixN, __rmul__ is mapped to matrix multiplication x*m, if x is a VectorN (or Vector or Point or Color),
        to transformation, ie VectorN by MatrixN multiplication.
        Otherwise, returns the result of the element wise multiplication of m and x if x is convertible to Array,
        multiplies every component of m by x if x is a single numeric value
        """
    
        pass
    
    
    def __rsub__(self, other):
        """
        m.__rsub__(v) <==> v-m
        Returns the result of the substraction of m from v if v is convertible to a MatrixN (element-wise substration),
        replace every component c of m by v-c if v is a scalar
        """
    
        pass
    
    
    def __setitem__(self, index, value):
        """
        m.__setitem__(index, value) <==> m[index] = value
        Set value of component index on self
        index can be a single numeric value or slice, thus one or more rows will be returned,
        or a row,column tuple of numeric values / slices
        """
    
        pass
    
    
    def __setslice__(self, start, end, value):
        """
        # deprecated and __setitem__ should accept slices anyway
        """
    
        pass
    
    
    def __sub__(self, other):
        """
        m.__sub__(v) <==> m-v
        Returns the result of the substraction of v from m if v is convertible to a MatrixN (element-wise substration),
        substract v to every component of m if v is a scalar
        """
    
        pass
    
    
    def adjoint(self):
        """
        Returns the adjoint (adjugate) Matrix
        """
    
        pass
    
    
    def asMatrix(self, percent=None):
        """
        The matrix representation for this Matrix/TransformationMatrix/Quaternion/EulerRotation instance
        """
    
        pass
    
    
    def assign(self, value):
        """
        # overloads for assign and get though standard way should be to use the data property
        # to access stored values
        """
    
        pass
    
    
    def blend(self, other, weight=0.5):
        """
        Returns a 0.0-1.0 scalar weight blend between self and other Matrix,
        blend mixes Matrix as transformation matrices
        """
    
        pass
    
    
    def det(self):
        """
        Returns the determinant of this Matrix instance
        """
    
        pass
    
    
    def det3x3(self):
        """
        Returns the determinant of the upper left 3x3 submatrix of this Matrix instance,
        it's the same as doing det(m[0:3, 0:3])
        """
    
        pass
    
    
    def det4x4(self):
        """
        Returns the 4x4 determinant of this Matrix instance
        """
    
        pass
    
    
    def get(self):
        """
        Wrap the Matrix api get method
        """
    
        pass
    
    
    def homogenize(self):
        """
        Returns a homogenized version of the Matrix
        """
    
        pass
    
    
    def inverse(self):
        """
        Returns the inverse Matrix
        """
    
        pass
    
    
    def isEquivalent(self, other, tol=1e-10):
        """
        Returns true if both arguments considered as Matrix are equal within the specified tolerance
        """
    
        pass
    
    
    def isSingular(self):
        """
        Returns True if the given Matrix is singular
        """
    
        pass
    
    
    def setToIdentity(self):
        """
        m.setToIdentity() <==> m = a * b
        Sets MatrixN to the identity matrix
        """
    
        pass
    
    
    def setToProduct(self, left, right):
        """
        m.setToProduct(a, b) <==> m = a * b
        Sets MatrixN to the result of the product of MatrixN a and MatrixN b
        """
    
        pass
    
    
    def transpose(self):
        """
        Returns the transposed Matrix
        """
    
        pass
    
    
    def weighted(self, weight):
        """
        Returns a 0.0-1.0 scalar weighted blend between identity and self
        """
    
        pass
    
    
    def __new__(cls, *args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    a00 = None
    
    a01 = None
    
    a02 = None
    
    a03 = None
    
    a10 = None
    
    a11 = None
    
    a12 = None
    
    a13 = None
    
    a20 = None
    
    a21 = None
    
    a22 = None
    
    a23 = None
    
    a30 = None
    
    a31 = None
    
    a32 = None
    
    a33 = None
    
    data = None
    
    identity = None
    
    matrix = None
    
    rotate = None
    
    scale = None
    
    translate = None
    
    
    
    __readonly__ = {}
    
    
    apicls = None
    
    
    cnames = ()
    
    
    ndim = 2
    
    
    shape = ()
    
    
    size = 16


class BoundingBox(_MBoundingBox):
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    def __getitem__(self, item):
        pass
    
    
    def __init__(self, *args):
        pass
    
    
    def __melobject__(self):
        """
        A flat list of 6 values [minx, miny, minz, maxx, maxy, maxz]
        """
    
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __str__(self):
        pass
    
    
    def center(self):
        """
        Returns the center of the bounding box.
        
        :rtype: `Point`
        
        Derived from api method `maya.OpenMaya.MBoundingBox.center`
        """
    
        pass
    
    
    def clear(self):
        """
        Empties the current bounding box. 
        
        Derived from api method `maya.OpenMaya.MBoundingBox.clear`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def contains(self, point):
        """
        Returns true if the bounding box contains the given point.
        
        :Parameters:
            point : `Point`
                point to check for inclusion in this bounding box
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MBoundingBox.contains`
        """
    
        pass
    
    
    def depth(self):
        """
        Returns the depth of the bounding box.
        
        :rtype: `float`
        
        Derived from api method `maya.OpenMaya.MBoundingBox.depth`
        """
    
        pass
    
    
    def expand(self, point):
        """
        Expand the bounding box to include the given point.
        
        :Parameters:
            point : `Point`
                new point to include in the bounding box. 
        
        Derived from api method `maya.OpenMaya.MBoundingBox.expand`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def height(self):
        """
        Returns the height of the bounding box.
        
        :rtype: `float`
        
        Derived from api method `maya.OpenMaya.MBoundingBox.height`
        """
    
        pass
    
    
    def intersects(self, box, tol=0.0):
        """
        Returns true if the bounding box intersects another given bounding box
        
        :Parameters:
            box : `BoundingBox`
                bounding box to check for intersection 
            tol : `float`
                tolerance of the intersection check
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MBoundingBox.intersects`
        """
    
        pass
    
    
    def max(self):
        """
        Returns the maximum point for the bounding box. That is the point whose x, y, and z components represent the bounding box's maximum value in each dimension.
        
        :rtype: `Point`
        
        Derived from api method `maya.OpenMaya.MBoundingBox.max`
        """
    
        pass
    
    
    def min(self):
        """
        Returns the minimum point for the bounding box. That is the point whose x, y, and z components represent the bounding box's minimum value in each dimension.
        
        :rtype: `Point`
        
        Derived from api method `maya.OpenMaya.MBoundingBox.min`
        """
    
        pass
    
    
    def repr(self):
        pass
    
    
    def transformUsing(self, matrix):
        """
        Apply the given transformation to this bounding box.
        
        :Parameters:
            matrix : `Matrix`
                transformation matrix 
        
        Derived from api method `maya.OpenMaya.MBoundingBox.transformUsing`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def width(self):
        """
        Returns the width of the bounding box.
        
        :rtype: `float`
        
        Derived from api method `maya.OpenMaya.MBoundingBox.width`
        """
    
        pass
    
    
    d = None
    
    h = None
    
    w = None
    
    
    
    __readonly__ = {}
    
    
    apicls = None


class EulerRotation(Array, _MEulerRotation):
    """
    unit handling:
    >>> from pymel.all import *
    >>> import pymel.core.datatypes as dt
    >>>
    >>> currentUnit(angle='degree')
    u'degree'
    >>> e = dt.EulerRotation([math.pi,0,0], unit='radians')
    >>> e
    dt.EulerRotation([3.14159265359, 0.0, 0.0], unit='radians')
    >>> e2 = dt.EulerRotation([180,0,0], unit='degrees')
    >>> e2
    dt.EulerRotation([180.0, 0.0, 0.0])
    >>> e.isEquivalent( e2 )
    True
    >>> e == e2
    True
    
    units are only displayed when they do not match the current ui unit
    >>> dt.Angle.getUIUnit() # check current angular unit
    'degrees'
    >>> e
    dt.EulerRotation([3.14159265359, 0.0, 0.0], unit='radians')
    >>> dt.Angle.setUIUnit('radians')  # change to radians
    >>> e
    dt.EulerRotation([3.14159265359, 0.0, 0.0])
    """
    
    
    
    def __add__(self, other):
        """
        u.__add__(v) <==> u+v
        Returns the result of the addition of u and v if v is convertible to a VectorN (element-wise addition),
        adds v to every component of u if v is a scalar
        """
    
        pass
    
    
    def __contains__(self, value):
        """
        True if at least one of the vector components is equal to the argument
        """
    
        pass
    
    
    def __div__(self, other):
        """
        u.__div__(v) <==> u/v
        Returns the result of the division of u by v if v is convertible to a VectorN (element-wise division),
        divide every component of u by v if v is a scalar
        """
    
        pass
    
    
    def __eq__(self, other):
        """
        u.__eq__(v) <==> u == v
        Equivalence test
        """
    
        pass
    
    
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    def __getitem__(self, i):
        pass
    
    
    def __iadd__(self, other):
        """
        u.__iadd__(v) <==> u += v
        In place addition of u and v, see __add__
        """
    
        pass
    
    
    def __idiv__(self, other):
        """
        u.__idiv__(v) <==> u /= v
        In place division of u by v, see __div__
        """
    
        pass
    
    
    def __imul__(self, other):
        """
        u.__imul__(v) <==> u *= v
        Valid for EulerRotation * Matrix multiplication, in place transformation of u by Matrix v
        or EulerRotation by scalar multiplication only
        """
    
        pass
    
    
    def __init__(self, *args, **kwargs):
        """
        __init__ method for EulerRotation
        """
    
        pass
    
    
    def __isub__(self, other):
        """
        u.__isub__(v) <==> u -= v
        In place substraction of u and v, see __sub__
        """
    
        pass
    
    
    def __iter__(self):
        pass
    
    
    def __len__(self):
        pass
    
    
    def __mul__(self, other):
        """
        u.__mul__(v) <==> u*v
        The multiply '*' operator is mapped to the dot product when both objects are Vectors,
        to the transformation of u by matrix v when v is a MatrixN,
        to element wise multiplication when v is a sequence,
        and multiplies each component of u by v when v is a numeric type.
        """
    
        pass
    
    
    def __ne__(self, other):
        """
        u.__ne__(v) <==> u != v
        Equivalence test
        """
    
        pass
    
    
    def __neg__(self):
        """
        u.__neg__() <==> -u
        The unary minus operator. Negates the value of each of the components of u
        """
    
        pass
    
    
    def __radd__(self, other):
        """
        u.__radd__(v) <==> v+u
        Returns the result of the addition of u and v if v is convertible to a VectorN (element-wise addition),
        adds v to every component of u if v is a scalar
        """
    
        pass
    
    
    def __rdiv__(self, other):
        """
        u.__rdiv__(v) <==> v/u
        Returns the result of of the division of v by u if v is convertible to a VectorN (element-wise division),
        invert every component of u and multiply it by v if v is a scalar
        """
    
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __rmul__(self, other):
        """
        u.__rmul__(v) <==> v*u
        The multiply '*' operator is mapped to the dot product when both objects are Vectors,
        to the left side multiplication (pre-multiplication) of u by matrix v when v is a MatrixN,
        to element wise multiplication when v is a sequence,
        and multiplies each component of u by v when v is a numeric type.
        """
    
        pass
    
    
    def __rsub__(self, other):
        """
        u.__rsub__(v) <==> v-u
        Returns the result of the substraction of u from v if v is convertible to a VectorN (element-wise substration),
        replace every component c of u by v-c if v is a scalar
        """
    
        pass
    
    
    def __setitem__(self, key, val):
        pass
    
    
    def __sub__(self, other):
        """
        u.__sub__(v) <==> u-v
        Returns the result of the substraction of v from u if v is convertible to a VectorN (element-wise substration),
        substract v to every component of u if v is a scalar
        """
    
        pass
    
    
    def alternateSolution(self):
        """
        Returns an alternate solution to this rotation. The resulting rotation will be bound between +/- PI, and the rotation order will remain unchanged.
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.alternateSolution`
        """
    
        pass
    
    
    def asMatrix(self):
        """
        Converts an euler rotation to a rotation matrix.
        
        :rtype: `Matrix`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.asMatrix`
        """
    
        pass
    
    
    def asQuaternion(self):
        """
        Converts an euler rotation to a quaternion.
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.asQuaternion`
        """
    
        pass
    
    
    def asVector(self):
        """
        Converts an euler rotation to a vector. The rotation order component is dropped.
        
        :rtype: `Vector`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.asVector`
        """
    
        pass
    
    
    def assign(self, *args, **kwargs):
        """
        Wrap the Quaternion api assign method
        """
    
        pass
    
    
    def bound(self):
        """
        Returns the result of bounding this rotation to be within +/- PI. Bounding a rotation to be within +/- PI is defined to be the result of offsetting the rotation by +/- 2nPI (term by term) such that the offset is within +/- PI.
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.bound`
        """
    
        pass
    
    
    def boundIt(self, src):
        """
        Sets this euler rotation to be the input rotation that has been bound to be within +/- PI. Bounding a rotation to be within +/- PI is defined to be the result of offsetting the rotation by +/- 2nPI (term by term) such that the offset is within +/- PI.
        
        :Parameters:
            src : `EulerRotation`
                the input rotation that will be bound
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.boundIt`
        """
    
        pass
    
    
    def closestCut(self, dst):
        """
        Returns the closest cut of this rotation to "dst". The closest cut of rotation A to rotation B is defined to be the rotation that is +/- 2nPI to rotation A (term by term) and within +/- PI to rotation B.
        
        :Parameters:
            dst : `EulerRotation`
                the range of the closest cut
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.closestCut`
        """
    
        pass
    
    
    def closestSolution(self, dst):
        """
        Returns the euler rotation that is the closest solution to the "dst" euler rotation.
        
        :Parameters:
            dst : `EulerRotation`
                the euler rotation to which the solution should be closest
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.closestSolution`
        """
    
        pass
    
    
    def get(self):
        """
        Wrap the MEulerRotation api get method
        """
    
        pass
    
    
    def incrementalRotateBy(self, axis, angle):
        """
        Perform an incremental rotation by the specified axis and angle. The rotation is broken down and performed in smaller steps so that the angles update properly.
        
        :Parameters:
            axis : `Vector`
                the axis to rotate around 
            angle : `float`
                the angle by which to rotate around the axis
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.incrementalRotateBy`
        """
    
        pass
    
    
    def inverse(self):
        """
        Returns the inverse of this euler rotation. The rotation order will be reversed.
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.inverse`
        """
    
        pass
    
    
    def invertIt(self):
        """
        Performs an in place inversion of this euler rotation. The rotation order will be reversed.
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.invertIt`
        """
    
        pass
    
    
    def isZero(self, tolerance=1e-10):
        """
        This method returns true if this euler rotation is zero, within some given tolerance.
        
        :Parameters:
            tolerance : `float`
                the amount of variation allowed for equivalency to zero
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.isZero`
        """
    
        pass
    
    
    def reorder(self, ord):
        """
        Returns the reordering of this euler rotation, such that the euler rotation will have the specified rotation order.
        
        :Parameters:
            ord : `EulerRotation.RotationOrder`
                the new rotation order of the euler rotation
        
                values: 'XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX'
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.reorder`
        """
    
        pass
    
    
    def reorderIt(self, ord):
        """
        Performs an in place reordering of this euler rotation, such that the euler rotation will have the specified rotation order.
        
        :Parameters:
            ord : `EulerRotation.RotationOrder`
                the new rotation order of the euler rotation
        
                values: 'XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX'
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.reorderIt`
        """
    
        pass
    
    
    def setDisplayUnit(self, unit):
        pass
    
    
    def setToAlternateSolution(self, src):
        """
        Sets this euler rotation to an alternate solution of the input rotation. The resulting rotation will be bound between +/- PI, and the rotation order will remain unchanged.
        
        :Parameters:
            src : `EulerRotation`
                the rotation to compute an alternate solution to
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.setToAlternateSolution`
        """
    
        pass
    
    
    def setToClosestCut(self, src, dst):
        """
        Sets this rotation to be the closest cut of "src" to "dst". The closest cut of rotation A to rotation B is defined to be the rotation that is +/- 2nPI to rotation A (term by term) and within +/- PI to rotation B.
        
        :Parameters:
            src : `EulerRotation`
                the euler rotation whose terms will be offset by +/- 2nPI 
            dst : `EulerRotation`
                the range of the closest cut
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.setToClosestCut`
        """
    
        pass
    
    
    def setToClosestSolution(self, src, dst):
        """
        Sets this euler rotation to the euler rotation that is the closest solution of the "src" euler rotation to the "dst" euler rotation.
        
        :Parameters:
            src : `EulerRotation`
                the euler rotation whose closest solution will be calculated 
            dst : `EulerRotation`
                the euler rotation to which the solution should be closest
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.setToClosestSolution`
        """
    
        pass
    
    
    def setValue(self, v, ord='XYZ'):
        """
        Sets the euler rotation to the values contained in the vector and with the specified rotation order.
        
        :Parameters:
            v : `Vector`
                vector from which to set the x, y, and z rotation components 
            ord : `EulerRotation.RotationOrder`
                the rotation order; the default rotation order is XYZ
        
                values: 'XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX'
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.setValue`
        """
    
        pass
    
    
    def decompose(self, matrix, ord):
        """
        Decompose a rotation matrix into the desired euler angles with the specified order.
        
        :Parameters:
            matrix : `Matrix`
                the matrix that will be decomposed into an euler rotation with the specified order 
            ord : `EulerRotation.RotationOrder`
                the order which the euler rotation will have
        
                values: 'XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX'
        
        
        :rtype: `EulerRotation`
        
        Derived from api method `maya.OpenMaya.MEulerRotation.decompose`
        """
    
        pass
    
    
    def __new__(cls, *args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    identity = None
    
    order = None
    
    x = None
    
    y = None
    
    z = None
    
    RotationOrder = {}
    
    
    
    
    __readonly__ = {}
    
    
    apicls = None
    
    
    cnames = ()
    
    
    ndim = 1
    
    
    shape = ()
    
    
    size = 3


class Vector(VectorN, _MVector):
    """
    A 3 dimensional vector class that wraps Maya's api Vector class
    
        >>> from pymel.all import *
        >>> import pymel.core.datatypes as dt
        >>>
        >>> v = dt.Vector(1, 2, 3)
        >>> w = dt.Vector(x=1, z=2)
        >>> z = dt.Vector( dt.Vector.xAxis, z=1)
    
        >>> v = dt.Vector(1, 2, 3, unit='meters')
        >>> print v
        [1.0, 2.0, 3.0]
    """
    
    
    
    def __add__(self, other):
        """
        u.__add__(v) <==> u+v
        Returns the result of the addition of u and v if v is convertible to a VectorN (element-wise addition),
        adds v to every component of u if v is a scalar
        """
    
        pass
    
    
    def __contains__(self, value):
        """
        True if at least one of the vector components is equal to the argument
        """
    
        pass
    
    
    def __div__(self, other):
        """
        u.__div__(v) <==> u/v
        Returns the result of the division of u by v if v is convertible to a VectorN (element-wise division),
        divide every component of u by v if v is a scalar
        """
    
        pass
    
    
    def __eq__(self, other):
        """
        u.__eq__(v) <==> u == v
        Equivalence test
        """
    
        pass
    
    
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    def __getitem__(self, i):
        """
        Get component i value from self
        """
    
        pass
    
    
    def __iadd__(self, other):
        """
        u.__iadd__(v) <==> u += v
        In place addition of u and v, see __add__
        """
    
        pass
    
    
    def __idiv__(self, other):
        """
        u.__idiv__(v) <==> u /= v
        In place division of u by v, see __div__
        """
    
        pass
    
    
    def __imul__(self, other):
        """
        u.__imul__(v) <==> u *= v
        Valid for Vector * Matrix multiplication, in place transformation of u by Matrix v
        or Vector by scalar multiplication only
        """
    
        pass
    
    
    def __init__(self, *args, **kwargs):
        """
        __init__ method, valid for Vector, Point and Color classes
        """
    
        pass
    
    
    def __isub__(self, other):
        """
        u.__isub__(v) <==> u -= v
        In place substraction of u and v, see __sub__
        """
    
        pass
    
    
    def __iter__(self, *args, **kwargs):
        """
        Iterate on the api components
        """
    
        pass
    
    
    def __ixor__(self, other):
        """
        u.__xor__(v) <==> u^=v
        Inplace cross product or transformation by inverse transpose of v is v is a MatrixN
        """
    
        pass
    
    
    def __len__(self):
        """
        Number of components in the Vector instance, 3 for Vector, 4 for Point and Color
        """
    
        pass
    
    
    def __mul__(self, other):
        """
        u.__mul__(v) <==> u*v
        The multiply '*' operator is mapped to the dot product when both objects are Vectors,
        to the transformation of u by matrix v when v is a MatrixN,
        to element wise multiplication when v is a sequence,
        and multiplies each component of u by v when v is a numeric type.
        """
    
        pass
    
    
    def __ne__(self, other):
        """
        u.__ne__(v) <==> u != v
        Equivalence test
        """
    
        pass
    
    
    def __neg__(self):
        """
        u.__neg__() <==> -u
        The unary minus operator. Negates the value of each of the components of u
        """
    
        pass
    
    
    def __radd__(self, other):
        """
        u.__radd__(v) <==> v+u
        Returns the result of the addition of u and v if v is convertible to a VectorN (element-wise addition),
        adds v to every component of u if v is a scalar
        """
    
        pass
    
    
    def __rdiv__(self, other):
        """
        u.__rdiv__(v) <==> v/u
        Returns the result of of the division of v by u if v is convertible to a VectorN (element-wise division),
        invert every component of u and multiply it by v if v is a scalar
        """
    
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __rmul__(self, other):
        """
        u.__rmul__(v) <==> v*u
        The multiply '*' operator is mapped to the dot product when both objects are Vectors,
        to the left side multiplication (pre-multiplication) of u by matrix v when v is a MatrixN,
        to element wise multiplication when v is a sequence,
        and multiplies each component of u by v when v is a numeric type.
        """
    
        pass
    
    
    def __rsub__(self, other):
        """
        u.__rsub__(v) <==> v-u
        Returns the result of the substraction of u from v if v is convertible to a VectorN (element-wise substration),
        replace every component c of u by v-c if v is a scalar
        """
    
        pass
    
    
    def __setitem__(self, i, a):
        """
        Set component i value on self
        """
    
        pass
    
    
    def __sub__(self, other):
        """
        u.__sub__(v) <==> u-v
        Returns the result of the substraction of v from u if v is convertible to a VectorN (element-wise substration),
        substract v to every component of u if v is a scalar
        """
    
        pass
    
    
    def __xor__(self, other):
        """
        u.__xor__(v) <==> u^v
        Defines the cross product operator between two 3D vectors,
        if v is a MatrixN, u^v is equivalent to u.transformAsNormal(v)
        """
    
        pass
    
    
    def angle(self, other):
        """
        u.angle(v) <==> angle(u, v) --> float
        Returns the angle (in radians) between the two vectors u and v
        Note that this angle is not signed, use axis to know the direction of the rotation
        """
    
        pass
    
    
    def assign(self, value):
        """
        Wrap the Vector api assign method
        """
    
        pass
    
    
    def axis(self, other, normalize=False):
        """
        u.axis(v) <==> angle(u, v) --> Vector
        Returns the axis of rotation from u to v as the vector n = u ^ v
        if the normalize keyword argument is set to True, n is also normalized
        """
    
        pass
    
    
    def cotan(self, other):
        """
        u.cotan(v) <==> cotan(u, v) --> float :
        cotangent of the a, b angle, a and b should be MVectors
        """
    
        pass
    
    
    def cross(self, other):
        """
        cross product, only defined for two 3D vectors
        """
    
        pass
    
    
    def distanceTo(self, other):
        pass
    
    
    def dot(self, other):
        """
        dot product of two vectors
        """
    
        pass
    
    
    def get(self):
        """
        Wrap the Vector api get method
        """
    
        pass
    
    
    def isEquivalent(self, other, tol=None):
        """
        Returns true if both arguments considered as Vector are equal within the specified tolerance
        """
    
        pass
    
    
    def isParallel(self, other, tol=None):
        """
        Returns true if both arguments considered as Vector are parallel within the specified tolerance
        """
    
        pass
    
    
    def length(self):
        """
        Return the length of the vector
        """
    
        pass
    
    
    def normal(self):
        """
        Return a normalized copy of self
        """
    
        pass
    
    
    def normalize(self):
        """
        Performs an in place normalization of self
        """
    
        pass
    
    
    def rotateBy(self, *args):
        """
        u.rotateBy(*args) --> Vector
        Returns the result of rotating u by the specified arguments.
        There are several ways the rotation can be specified:
        args is a tuple of one Matrix, TransformationMatrix, Quaternion, EulerRotation
        arg is tuple of 4 arguments, 3 rotation value and an optionnal rotation order
        args is a tuple of one Vector, the axis and one float, the angle to rotate around that axis in radians
        """
    
        pass
    
    
    def rotateTo(self, other):
        """
        u.rotateTo(v) --> Quaternion
        Returns the Quaternion that represents the rotation of the Vector u into the Vector v
        around their mutually perpendicular axis. It amounts to rotate u by angle(u, v) around axis(u, v)
        """
    
        pass
    
    
    def sqlength(self):
        """
        Return the square length of the vector
        """
    
        pass
    
    
    def transformAsNormal(self, other):
        """
        Returns the vector transformed by the matrix as a normal
        Normal vectors are not transformed in the same way as position vectors or points.
        If this vector is treated as a normal vector then it needs to be transformed by
        post multiplying it by the inverse transpose of the transformation matrix.
        This method will apply the proper transformation to the vector as if it were a normal.
        """
    
        pass
    
    
    def __new__(cls, *args, **kwargs):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    data = None
    
    one = None
    
    x = None
    
    xAxis = None
    
    xNegAxis = None
    
    y = None
    
    yAxis = None
    
    yNegAxis = None
    
    z = None
    
    zAxis = None
    
    zNegAxis = None
    
    zero = None
    
    Axis = {}
    
    
    
    
    __readonly__ = {}
    
    
    apicls = None
    
    
    cnames = ()
    
    
    ndim = 1
    
    
    shape = ()
    
    
    size = 3
    
    
    unit = None


class Unit(float):
    def __repr__(self):
        pass
    
    
    def asInternalUnit(self):
        pass
    
    
    def asUIUnit(self):
        pass
    
    
    def asUnit(self, unit):
        pass
    
    
    def assign(self, *args):
        pass
    
    
    def getUnit(self):
        """
        Returns the units currently in effect for this instance
        """
    
        pass
    
    
    def getInternalUnit(cls):
        """
        Returns the inernal units currently in use for that type
        """
    
        pass
    
    
    def getUIUnit(cls):
        """
        Returns the global UI units currently in use for that type
        """
    
        pass
    
    
    def kUnit(cls, unit=None):
        """
        Converts a string unit name to the internal int unit enum representation
        """
    
        pass
    
    
    def sUnit(cls, unit=None):
        """
        Converts an internal int unit enum representation tp the string unit name
        """
    
        pass
    
    
    def setUIUnit(cls, unit=None):
        """
        Sets the global UI units currently to use for that type
        """
    
        pass
    
    
    def uiToInternal(cls, value):
        pass
    
    
    def __new__(cls, value, unit=None):
        pass
    
    
    data = None
    
    unit = None
    
    value = None


import pymel.internal.factories as _factories

class MetaMayaArrayTypeWrapper(_factories.MetaMayaTypeWrapper):
    """
    A metaclass to wrap Maya array type classes such as Vector, Matrix
    """
    
    
    
    def __new__(mcl, classname, bases, classdict):
        """
        Create a new wrapping class for a Maya api type, such as Vector or Matrix
        """
    
        pass


class Space(_MSpace):
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    Space = {}
    
    
    
    
    __readonly__ = {}
    
    
    apicls = None


class Quaternion(Matrix, _MQuaternion):
    def __contains__(self, value):
        """
        True if at least one of the vector components is equal to the argument
        """
    
        pass
    
    
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    def __getitem__(self, i):
        pass
    
    
    def __init__(self, *args, **kwargs):
        """
        __init__ method for Quaternion
        """
    
        pass
    
    
    def __iter__(self):
        pass
    
    
    def __len__(self):
        pass
    
    
    def __setitem__(self, i, a):
        """
        Set component i value on self
        """
    
        pass
    
    
    def assign(self, value):
        """
        Wrap the Quaternion api assign method
        """
    
        pass
    
    
    def conjugateIt(self):
        """
        Performs an in place conjugation of this quaternion. The result is a quaternion whose x, y, and z values have been negated.
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MQuaternion.conjugateIt`
        """
    
        pass
    
    
    def exp(self):
        """
        Exponentiates a quaternion that has a scalar part of zero. The precondition for using this method is that w is zero.
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MQuaternion.exp`
        """
    
        pass
    
    
    def get(self):
        """
        Wrap the Quaternion api get method
        """
    
        pass
    
    
    def invertIt(self):
        """
        Performs an in place inversion of this quaternion.
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MQuaternion.invertIt`
        """
    
        pass
    
    
    def log(self):
        """
        Returns the natural log of a quaternion. The precondition for using this method is that the quaternion must be normalized.
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MQuaternion.log`
        """
    
        pass
    
    
    def negateIt(self):
        """
        Performs an in place negation of the quaternion. The result is a quaternion whose x, y, z, and w values have been negated.
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MQuaternion.negateIt`
        """
    
        pass
    
    
    def normalizeIt(self):
        """
        Performs an in place normalization of this quaternion. The result is a quaternion of unit length.
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MQuaternion.normalizeIt`
        """
    
        pass
    
    
    def scaleIt(self, scale):
        """
        Performs an in place scaling of the quaternion. The result is a quaternion whose x, y, z, and w values have been scaled by the specified amount.
        
        :Parameters:
            scale : `float`
                the amount by which the quaternion should be scaled
        
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MQuaternion.scaleIt`
        """
    
        pass
    
    
    def setToXAxis(self, theta):
        """
        Sets this quaternion to be the rotation about the X axis of theta (in angular units). If the length of the axis is too small the quaternion returned will be the identity quaternion.
        
        :Parameters:
            theta : `float`
                the angle of rotation about the X axis in radians
        
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MQuaternion.setToXAxis`
        """
    
        pass
    
    
    def setToYAxis(self, theta):
        """
        Sets this quaternion to be the rotation about the Y axis of theta (in angular units). If the length of the axis is too small the quaternion returned will be the identity quaternion.
        
        :Parameters:
            theta : `float`
                the angle of rotation about the Y axis in radians
        
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MQuaternion.setToYAxis`
        """
    
        pass
    
    
    def setToZAxis(self, theta):
        """
        Sets this quaternion to be the rotation about the Z axis of theta (in angular units). If the length of the axis is too small the quaternion returned will be the identity quaternion.
        
        :Parameters:
            theta : `float`
                the angle of rotation about the Z axis in radians
        
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MQuaternion.setToZAxis`
        """
    
        pass
    
    
    def __new__(cls, *args, **kwargs):
        pass
    
    
    identity = None
    
    rotate = None
    
    scale = None
    
    translate = None
    
    w = None
    
    x = None
    
    y = None
    
    z = None
    
    __readonly__ = {}
    
    
    apicls = None
    
    
    cnames = ()
    
    
    ndim = 1
    
    
    shape = ()
    
    
    size = 4


class Angle(Unit):
    def asAngMinutes(self):
        pass
    
    
    def asAngSeconds(self):
        pass
    
    
    def asDegrees(self):
        pass
    
    
    def asRadians(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    Unit = {}
    
    
    apicls = None


class Color(Vector, _MColor):
    """
    A 4 dimensional vector class that wraps Maya's api Color class,
    It stores the r, g, b, a components of the color, as normalized (Python) floats
    """
    
    
    
    def __add__(self, other):
        """
        c.__add__(d) <==> c+d
        Returns the result of the addition of MColors c and d if d is convertible to a Color,
        adds d to every component of c if d is a scalar
        """
    
        pass
    
    
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    def __iadd__(self, other):
        """
        c.__iadd__(d) <==> c += d
        In place addition of c and d, see __add__
        """
    
        pass
    
    
    def __imul__(self, other):
        """
        a.__imul__(b) <==> a *= b
        In place multiplication of VectorN a and b, see __mul__, result must fit a's type
        """
    
        pass
    
    
    def __init__(self, *args, **kwargs):
        """
        Init a Color instance
        Can pass one argument being another Color instance , or the color components
        """
    
        pass
    
    
    def __isub__(self, other):
        """
        c.__isub__(d) <==> c -= d
        In place substraction of d from c, see __sub__
        """
    
        pass
    
    
    def __melobject__(self):
        """
        Special method for returning a mel-friendly representation. In this case, a 3-component color (RGB)
        """
    
        pass
    
    
    def __mul__(self, other):
        """
        a.__mul__(b) <==> a*b
        If b is a 1D sequence (Array, VectorN, Color), __mul__ is mapped to element-wise multiplication,
        If b is a MatrixN, __mul__ is similar to Point a by MatrixN b multiplication (post multiplication or transformation of a by b),
        multiplies every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __radd__(self, other):
        """
        c.__radd__(d) <==> d+c
        Returns the result of the addition of MColors c and d if d is convertible to a Color,
        adds d to every component of c if d is a scalar
        """
    
        pass
    
    
    def __rmul__(self, other):
        """
        a.__rmul__(b) <==> b*a
        If b is a 1D sequence (Array, VectorN, Color), __mul__ is mapped to element-wise multiplication,
        If b is a MatrixN, __mul__ is similar to MatrixN b by Point a matrix multiplication,
        multiplies every component of a by b if b is a single numeric value
        """
    
        pass
    
    
    def __rsub__(self, other):
        """
        c.__rsub__(d) <==> d-c
        Returns the result of the substraction of Color c from d if d is convertible to a Color,
        replace every component c[i] of c by d-c[i] if d is a scalar
        """
    
        pass
    
    
    def __sub__(self, other):
        """
        c.__add__(d) <==> c+d
        Returns the result of the substraction of Color d from c if d is convertible to a Color,
        substract d from every component of c if d is a scalar
        """
    
        pass
    
    
    def gamma(self, g):
        """
        c.gamma(g) applies gamma correction g to Color c, g can be a scalar and then will be applied to r, g, b
        or an iterable of up to 3 (r, g, b) independant gamma correction values
        """
    
        pass
    
    
    def hsvblend(self, other, weight=0.5):
        """
        c1.hsvblend(c2) --> Color
        Returns the result of blending c1 with c2 in hsv space, using the given weight
        """
    
        pass
    
    
    def over(self, other):
        """
        c1.over(c2): Composites c1 over other c2 using c1's alpha, the resulting color has the alpha of c2
        """
    
        pass
    
    
    def premult(self):
        """
        Premultiply Color r, g and b by it's alpha and resets alpha to 1.0
        """
    
        pass
    
    
    def set(self, colorModel, c1, c2, c3, alpha=1.0):
        """
        Color component assigment. 
        
        
        :Parameters:
            colorModel : `Color.MColorType`
                The color model. 
        
                values: 'RGB', 'HSV', 'CMY', 'CMYK'
            c1 : `float`
                First component of color. 
            c2 : `float`
                Second component of color. 
            c3 : `float`
                Third component of color. 
            alpha : `float`
                Alpha component of color.
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MColor.set`
        """
    
        pass
    
    
    def hsvtorgb(c):
        pass
    
    
    def rgbtohsv(c):
        """
        # static methods
        """
    
        pass
    
    
    a = None
    
    b = None
    
    black = None
    
    blue = None
    
    clear = None
    
    g = None
    
    green = None
    
    h = None
    
    hsv = None
    
    hsva = None
    
    kOpaqueBlack = None
    
    one = None
    
    opaque = None
    
    r = None
    
    red = None
    
    rgb = None
    
    rgba = None
    
    s = None
    
    v = None
    
    white = None
    
    xAxis = None
    
    xNegAxis = None
    
    yAxis = None
    
    yNegAxis = None
    
    zAxis = None
    
    zNegAxis = None
    
    zero = None
    
    MColorType = {}
    
    
    __readonly__ = {}
    
    
    apicls = None
    
    
    cnames = ()
    
    
    modes = ()
    
    
    ndim = 1
    
    
    shape = ()
    
    
    size = 4


class TransformationMatrix(Matrix, _MTransformationMatrix):
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    def addRotation(self, rot, order, space):
        """
        Add to the rotation component by rotating relative to the existing transformation. The only valid transformation spaces for this method are  MSpace::kTransform  and  MSpace::kPreTransform . All other spaces are treated as being equivalent to  MSpace::kTransform .
        
        :Parameters:
            rot : (`float`, `float`, `float`)
                relative value to rotate by 
            order : `TransformationMatrix.RotationOrder`
                order in which to apply the rotation components 
        
                values: 'XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX'
            space : `Space.Space`
                transform space in which to perform the rotation
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.addRotation`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def addRotationQuaternion(self, x, y, z, w, space):
        """
        Add to the rotation component by rotating relative to the existing transformation. Rotation is a quaternion. The only valid transformation spaces for this method are  MSpace::kTransform  and  MSpace::kPreTransform . All other spaces are treated as being equivalent to  MSpace::kTransform .
        
        :Parameters:
            x : `float`
                x component of quaternion 
            y : `float`
                y component of quaternion 
            z : `float`
                z component of quaternion 
            w : `float`
                w component of quaternion 
            space : `Space.Space`
                transformation space in which to perform the operation
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.addRotationQuaternion`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def addScale(self, scale, space):
        """
        Add to the scale component by scaling relative to the existing transformation.
        
        :Parameters:
            scale : (`float`, `float`, `float`)
                relative value to scale by 
            space : `Space.Space`
                transform space in which to perform the scale
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.addScale`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def addShear(self, shear, space):
        """
        Add to the shear component by shearing relative to the existing transformation.
        
        :Parameters:
            shear : (`float`, `float`, `float`)
                relative value to shear by 
            space : `Space.Space`
                transform space in which to perform the shear
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.addShear`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def addTranslation(self, vector, space):
        """
        Add to the translation component by translating relative to the existing transformation.
        
        :Parameters:
            vector : `Vector`
                relative value to translate by 
            space : `Space.Space`
                transform space in which to perform the scale
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.addTranslation`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def asMatrixInverse(self):
        """
        Returns the inverse of the four by four matrix that describes this transformation.
        
        :rtype: `Matrix`
        
        Derived from api method `maya.OpenMaya.MTransformationMatrix.asMatrixInverse`
        """
    
        pass
    
    
    def asRotateMatrix(self):
        """
        Returns rotate space matrix. The rotate space matrix takes points from object space to the space immediately following the scale/shear/rotation transformations.
        
        :rtype: `Matrix`
        
        Derived from api method `maya.OpenMaya.MTransformationMatrix.asRotateMatrix`
        """
    
        pass
    
    
    def asScaleMatrix(self):
        """
        Returns scale space matrix. The scale space matrix takes points from object space to the space immediately following scale and shear transformations.
        
        :rtype: `Matrix`
        
        Derived from api method `maya.OpenMaya.MTransformationMatrix.asScaleMatrix`
        """
    
        pass
    
    
    def eulerRotation(self):
        pass
    
    
    def getRotatePivot(self, space):
        """
        Returns the pivot around which the rotation is applied.
        
        :Parameters:
            space : `Space.Space`
                space in which to get the pivot 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Point`
        
        Derived from api method `maya.OpenMaya.MSpace.rotatePivot`
        """
    
        pass
    
    
    def getRotatePivotTranslation(self, space):
        """
        Returns the rotation pivot translation. This is the translation that is used to compensate for the movement of the rotation pivot.
        
        :Parameters:
            space : `Space.Space`
                space in which to get the pivot translation 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Vector`
        
        Derived from api method `maya.OpenMaya.MSpace.rotatePivotTranslation`
        """
    
        pass
    
    
    def getRotation(self):
        """
        # The apicls getRotation needs a "RotationOrder &" object, which is
        # impossible to make in python...
        # So instead, wrap eulerRotation
        """
    
        pass
    
    
    def getRotationOrientation(self):
        """
        Returns the rotation orientation for the transformation matrix. The rotation orientation is the rotation that orients the local rotation space. The rotation is returned in  MSpace::kTransform  space.
        
        :rtype: `Quaternion`
        
        Derived from api method `maya.OpenMaya.MTransformationMatrix.rotationOrientation`
        """
    
        pass
    
    
    def getRotationQuaternion(self):
        """
        Get the rotation component of the transformation matrix as a quaternion. The rotation is retrieved in  MSpace::kTransform  space.
        
        :rtype: (`float`, `float`, `float`, `float`)
        
        Derived from api method `maya.OpenMaya.MTransformationMatrix.getRotationQuaternion`
        """
    
        pass
    
    
    def getScale(self, space):
        """
        Get the scale component of the transformation matrix.
        
        :Parameters:
            space : `Space.Space`
                transform space in which to get the scale
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: (`float`, `float`, `float`)
        
        Derived from api method `maya.OpenMaya.MSpace.getScale`
        """
    
        pass
    
    
    def getScalePivot(self, space):
        """
        Returns the pivot around which the scale is applied.
        
        :Parameters:
            space : `Space.Space`
                space in which to get the pivot 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Point`
        
        Derived from api method `maya.OpenMaya.MSpace.scalePivot`
        """
    
        pass
    
    
    def getScalePivotTranslation(self, space):
        """
        Returns the scale pivot translation. This is the translation that is used to compensate for the movement of the scale pivot.
        
        :Parameters:
            space : `Space.Space`
                space in which to get the pivot 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Vector`
        
        Derived from api method `maya.OpenMaya.MSpace.scalePivotTranslation`
        """
    
        pass
    
    
    def getShear(self, space):
        """
        Get the shear component of the transformation matrix.
        
        :Parameters:
            space : `Space.Space`
                Transform space in which to get the shear.
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: (`float`, `float`, `float`)
        
        Derived from api method `maya.OpenMaya.MSpace.getShear`
        """
    
        pass
    
    
    def getTranslation(self, space):
        """
        Returns the translation component of the translation as a vector in linear units.
        
        :Parameters:
            space : `Space.Space`
                space in which to perform the translation 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Vector`
        
        Derived from api method `maya.OpenMaya.MSpace.getTranslation`
        """
    
        pass
    
    
    def reorderRotation(self, order):
        """
        Reorders the x, y, and z components of the rotation of this transform. The overall rotation will remain the same. This operation is not unique, so spin information will be lost.
        
        :Parameters:
            order : `TransformationMatrix.RotationOrder`
                new order of the rotations
        
                values: 'XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX'
        
        Derived from api method `maya.OpenMaya.MTransformationMatrix.reorderRotation`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def rotateBy(self, q, space):
        """
        Adds to the rotation component of the rotation matrix by rotating relative to the existing transformation using a quaternion. The only valid transformation spaces for this method are  MSpace::kTransform  and  MSpace::kPreTransform /MSpacekObject. All other spaces are treated as being equivalent to  MSpace::kTransform .
        
        :Parameters:
            q : `Quaternion`
                the quaternion that indicates how much the transformation matrix will be rotated by 
            space : `Space.Space`
                the space in which the rotation is performed 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `TransformationMatrix`
        
        Derived from api method `maya.OpenMaya.MSpace.rotateBy`
        """
    
        pass
    
    
    def rotateTo(self, value):
        """
        Set to the given rotation (and result self)
        
        Value may be either a Quaternion, EulerRotation object, or a list of
        floats; if it is floats, if it has length 4 it is interpreted as
        a Quaternion; if 3, as a EulerRotation.
        """
    
        pass
    
    
    def rotationOrder(self):
        """
        Returns the rotation order for the transform matrix. That is the order in which the Euler angles are applied to create the end rotation.
        
        :rtype: `TransformationMatrix.RotationOrder`
        
        Derived from api method `maya.OpenMaya.MTransformationMatrix.rotationOrder`
        """
    
        pass
    
    
    def setRotatePivot(self, point, space, balance):
        """
        Set the pivot around which the rotation is applied.
        
        :Parameters:
            point : `Point`
                new rotation pivot 
            space : `Space.Space`
                transform space in which to set the pivot 
        
                values: 'transform', 'preTransform', 'object', 'world'
            balance : `bool`
                whether to balance the matrix
        
        Derived from api method `maya.OpenMaya.MSpace.setRotatePivot`
        """
    
        pass
    
    
    def setRotatePivotTranslation(self, vector, space):
        """
        Set the pivot translation. This component is used to preserve existing transformations when moving pivot. This method will only be useful to advanced users.
        
        :Parameters:
            vector : `Vector`
                new rotation pivot translation 
            space : `Space.Space`
                transform space in which to set the rotation translation
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.setRotatePivotTranslation`
        """
    
        pass
    
    
    def setRotation(self, *args):
        pass
    
    
    def setRotationOrientation(self, q):
        """
        Sets the rotation orientation for the transformation matrix. The rotation orientation is the rotation that orients the local rotation space. The rotation is set in  MSpace::kTransform  space.
        
        :Parameters:
            q : `Quaternion`
                Rotation quaternion.
        
        
        :rtype: `TransformationMatrix`
        
        Derived from api method `maya.OpenMaya.MTransformationMatrix.setRotationOrientation`
        """
    
        pass
    
    
    def setRotationQuaternion(self, x, y, z, w):
        """
        Set the rotation component of the transformation matrix using a quaternion. The rotation is set in  MSpace::kTransform  space.
        
        :Parameters:
            x : `float`
                x component of new quaternion 
            y : `float`
                y component of new quaternion 
            z : `float`
                z component of new quaternion 
            w : `float`
                w component of new quaternion
        
        Derived from api method `maya.OpenMaya.MTransformationMatrix.setRotationQuaternion`
        """
    
        pass
    
    
    def setScale(self, scale, space):
        """
        Set the scale component of the transformation matrix.
        
        :Parameters:
            scale : (`float`, `float`, `float`)
                new scale component 
            space : `Space.Space`
                transform space in which to perform the scale
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.setScale`
        """
    
        pass
    
    
    def setScalePivot(self, point, space, balance):
        """
        Set the pivot around which the scale is applied.
        
        :Parameters:
            point : `Point`
                new scale pivot 
            space : `Space.Space`
                transform space in which to set the scale pivot 
        
                values: 'transform', 'preTransform', 'object', 'world'
            balance : `bool`
                whether to balance the matrix
        
        Derived from api method `maya.OpenMaya.MSpace.setScalePivot`
        """
    
        pass
    
    
    def setScalePivotTranslation(self, vector, space):
        """
        Set the pivot translation. This component is used to preserve existing scale transformations when moving pivot. This method will only be useful to advanced users.
        
        :Parameters:
            vector : `Vector`
                new scale pivot translation 
            space : `Space.Space`
                transform space in which to set the scale translation
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.setScalePivotTranslation`
        """
    
        pass
    
    
    def setShear(self, shear, space):
        """
        Set the shear component of the transformation matrix. The shear values represent (xy, xz, yx).
        
        :Parameters:
            shear : (`float`, `float`, `float`)
                new shear component 
            space : `Space.Space`
                transform space in which to perform the shear
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.setShear`
        """
    
        pass
    
    
    def setToRotationAxis(self, axis, rotation):
        """
        Sets the rotation given an axis and a rotation about it.
        
        :Parameters:
            axis : `Vector`
                axis to rotate about 
            rotation : `float`
                rotation in radians
        
        Derived from api method `maya.OpenMaya.MTransformationMatrix.setToRotationAxis`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def setTranslation(self, vector, space):
        """
        Set the translation component of the transformation matrix in linear units.
        
        :Parameters:
            vector : `Vector`
                new translation component in centimeters. 
            space : `Space.Space`
                transform space in which to perform the translation
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.setTranslation`
        """
    
        pass
    
    
    a00 = None
    
    a01 = None
    
    a02 = None
    
    a03 = None
    
    a10 = None
    
    a11 = None
    
    a12 = None
    
    a13 = None
    
    a20 = None
    
    a21 = None
    
    a22 = None
    
    a23 = None
    
    a30 = None
    
    a31 = None
    
    a32 = None
    
    a33 = None
    
    euler = None
    
    identity = None
    
    rotate = None
    
    scale = None
    
    translate = None
    
    RotationOrder = {}
    
    
    __readonly__ = {}
    
    
    apicls = None
    
    
    cnames = ()
    
    
    ndim = 2
    
    
    shape = ()
    
    
    size = 16


class FloatVector(Vector, _MFloatVector):
    """
    A 3 dimensional vector class that wraps Maya's api FloatVector class,
    It behaves identically to Vector, but it also derives from api's FloatVector
    to keep api methods happy
    """
    
    
    
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    one = None
    
    x = None
    
    xAxis = None
    
    xNegAxis = None
    
    y = None
    
    yAxis = None
    
    yNegAxis = None
    
    z = None
    
    zAxis = None
    
    zNegAxis = None
    
    zero = None
    
    __readonly__ = {}
    
    
    apicls = None
    
    
    cnames = ()
    
    
    ndim = 1
    
    
    shape = ()
    
    
    size = 3


class FloatMatrix(Matrix, _MFloatMatrix):
    """
    A 4x4 matrix class that wraps Maya's api FloatMatrix class,
    It behaves identically to Matrix, but it also derives from api's FloatMatrix
    to keep api methods happy
    """
    
    
    
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    a00 = None
    
    a01 = None
    
    a02 = None
    
    a03 = None
    
    a10 = None
    
    a11 = None
    
    a12 = None
    
    a13 = None
    
    a20 = None
    
    a21 = None
    
    a22 = None
    
    a23 = None
    
    a30 = None
    
    a31 = None
    
    a32 = None
    
    a33 = None
    
    identity = None
    
    __readonly__ = {}
    
    
    apicls = None
    
    
    cnames = ()
    
    
    ndim = 2
    
    
    shape = ()
    
    
    size = 16


class Distance(Unit):
    """
    >>> from pymel.core import *
    >>> import pymel.core.datatypes as dt
    >>>
    >>> dt.Distance.getInternalUnit()
    'centimeters'
    >>> dt.Distance.setUIUnit('meters')
    >>> dt.Distance.getUIUnit()
    'meters'
    
    >>> d = dt.Distance(12)
    >>> d.unit
    'meters'
    >>> print d
    12.0
    >>> print repr(d)
    dt.Distance(12.0, unit='meters')
    >>> print d.asUIUnit()
    12.0
    >>> print d.asInternalUnit()
    1200.0
    
    >>> dt.Distance.setUIUnit('centimeters')
    >>> dt.Distance.getUIUnit()
    'centimeters'
    >>> e = dt.Distance(12)
    >>> e.unit
    'centimeters'
    >>> print e
    12.0
    >>> str(e)
    '12.0'
    >>> print repr(e)
    dt.Distance(12.0, unit='centimeters')
    >>> print e.asUIUnit()
    12.0
    >>> print e.asInternalUnit()
    12.0
    
    >>> f = dt.Distance(12, 'feet')
    >>> print f
    12.0
    >>> print repr(f)
    dt.Distance(12.0, unit='feet')
    >>> f.unit
    'feet'
    >>> print f.asUIUnit()
    365.76
    >>> dt.Distance.setUIUnit('meters')
    >>> dt.Distance.getUIUnit()
    'meters'
    >>> print f.asUIUnit()
    3.6576
    >>> dt.Distance.getInternalUnit()
    'centimeters'
    >>> print f.asInternalUnit()
    365.76
    
    >>> print f.asFeet()
    12.0
    >>> print f.asMeters()
    3.6576
    >>> print f.asCentimeters()
    365.76
    
    >>> dt.Distance.setUIUnit()
    >>> dt.Distance.getUIUnit()
    'centimeters'
    """
    
    
    
    def asCentimeters(self):
        pass
    
    
    def asFeet(self):
        pass
    
    
    def asInches(self):
        pass
    
    
    def asKilometers(self):
        pass
    
    
    def asMeters(self):
        pass
    
    
    def asMiles(self):
        pass
    
    
    def asMillimeter(self):
        pass
    
    
    def asYards(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    Unit = {}
    
    
    apicls = None


class Point(Vector, _MPoint):
    """
    A 4 dimensional vector class that wraps Maya's api Point class,
    """
    
    
    
    def __add__(self, other):
        """
        u.__add__(v) <==> u+v
        Returns the result of the addition of u and v if v is convertible to a VectorN (element-wise addition),
        adds v to every component of u if v is a scalar
        """
    
        pass
    
    
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    def __iadd__(self, other):
        """
        u.__iadd__(v) <==> u += v
        In place addition of u and v, see __add__
        """
    
        pass
    
    
    def __iter__(self, *args, **kwargs):
        """
        Iterate on the api components
        """
    
        pass
    
    
    def __len__(self):
        """
        # we only show the x, y, z components on an iter
        """
    
        pass
    
    
    def __melobject__(self):
        """
        Special method for returning a mel-friendly representation. In this case, a cartesian 3D point
        """
    
        pass
    
    
    def __radd__(self, other):
        """
        u.__radd__(v) <==> v+u
        Returns the result of the addition of u and v if v is convertible to a VectorN (element-wise addition),
        adds v to every component of u if v is a scalar
        """
    
        pass
    
    
    def angle(self, start, end):
        """
        a.angle(b, c) --> float
        Returns the angle (in radians) of rotation from point b to c around a.
        Note that this angle is not signed, use axis to know the direction of the rotation
        """
    
        pass
    
    
    def axis(self, start, end, normalize=False):
        """
        a.axis(b, c) --> Vector
        Returns the axis of rotation from point b to c around a as the vector n = (b-a)^(c-a)
        if the normalize keyword argument is set to True, n is also normalized
        """
    
        pass
    
    
    def bWeights(self, *args):
        """
        p.bWeights(p0, p1, (...), pn) --> tuple
        Returns a tuple of (n0, n1, ...) normalized barycentric weights so that n0*p0 + n1*p1 + ... = p.
        This method works for n points defining a concave or convex n sided face,
        always returns positive normalized weights, and is continuous on the face limits (on the edges),
        but the n points must be coplanar, and p must be inside the face delimited by (p0, ..., pn)
        """
    
        pass
    
    
    def cartesian(self):
        """
        p.cartesian() --> Point
        Returns the cartesianized version of p, without changing p.
        """
    
        pass
    
    
    def cartesianize(self):
        """
        p.cartesianize() --> Point
        If the point instance p is of the form P(W*x, W*y, W*z, W), for some scale factor W != 0,
        then it is reset to be P(x, y, z, 1).
        This will only work correctly if the point is in homogenous form or cartesian form.
        If the point is in rational form, the results are not defined.
        """
    
        pass
    
    
    def center(self, *args):
        """
        p.center(q, r, s (...)) --> Point
        Returns the Point that is the center of p, q, r, s (...)
        """
    
        pass
    
    
    def cotan(self, start, end):
        """
        a.cotan(b, c) --> float :
        cotangent of the (b-a), (c-a) angle, a, b, and c should be MPoints representing points a, b, c
        """
    
        pass
    
    
    def homogen(self):
        """
        p.homogen() --> Point
        Returns the homogenized version of p, without changing p.
        """
    
        pass
    
    
    def homogenize(self):
        """
        p.homogenize() --> Point
        If the point instance p is of the form P(x, y, z, W) (ie. is in rational or (for W==1) cartesian form),
        for some scale factor W != 0, then it is reset to be P(W*x, W*y, W*z, W).
        """
    
        pass
    
    
    def isEquivalent(self, other, tol=None):
        """
        Returns true if both arguments considered as Point are equal within the specified tolerance
        """
    
        pass
    
    
    def planar(self, *args, **kwargs):
        """
        p.planar(q, r, s (...), tol=tolerance) --> bool
        Returns True if all provided points are planar within given tolerance
        """
    
        pass
    
    
    def rational(self):
        """
        p.rational() --> Point
        Returns the rationalized version of p, without changing p.
        """
    
        pass
    
    
    def rationalize(self):
        """
        p.rationalize() --> Point
        If the point instance p is of the form P(W*x, W*y, W*z, W) (ie. is in homogenous or (for W==1) cartesian form),
        for some scale factor W != 0, then it is reset to be P(x, y, z, W).
        This will only work correctly if the point is in homogenous or cartesian form.
        If the point is already in rational form, the results are not defined.
        """
    
        pass
    
    
    one = None
    
    origin = None
    
    w = None
    
    x = None
    
    xAxis = None
    
    xNegAxis = None
    
    y = None
    
    yAxis = None
    
    yNegAxis = None
    
    z = None
    
    zAxis = None
    
    zNegAxis = None
    
    zero = None
    
    __readonly__ = {}
    
    
    apicls = None
    
    
    cnames = ()
    
    
    ndim = 1
    
    
    shape = ()
    
    
    size = 4


class Time(Unit):
    __dict__ = None
    
    __weakref__ = None
    
    Unit = {}
    
    
    apicls = None


class FloatPoint(Point, _MFloatPoint):
    """
    A 4 dimensional vector class that wraps Maya's api FloatPoint class,
    It behaves identically to Point, but it also derives from api's FloatPoint
    to keep api methods happy
    """
    
    
    
    def __getattribute__(self, name):
        """
        # if removeAttrs:
        #    #_logger.debug( "%s: removing attributes %s" % (classname, removeAttrs) )
        """
    
        pass
    
    
    def setCast(self, srcpt):
        """
        Copy the values of x, y, z, and w from srcpt to the instance.
        
        :Parameters:
            srcpt : `Point`
                the point to copy the x, y, z and w values from.
        
        Derived from api method `maya.OpenMaya.MFloatPoint.setCast`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    one = None
    
    origin = None
    
    w = None
    
    x = None
    
    xAxis = None
    
    xNegAxis = None
    
    y = None
    
    yAxis = None
    
    yNegAxis = None
    
    z = None
    
    zAxis = None
    
    zNegAxis = None
    
    zero = None
    
    __readonly__ = {}
    
    
    apicls = None
    
    
    cnames = ()
    
    
    ndim = 1
    
    
    shape = ()
    
    
    size = 4



def _patchMFloatMatrix():
    pass


def _patchMColor():
    pass


def getPlugValue(plug):
    """
    given an MPlug, get its value as a pymel-style object
    """

    pass


def _testMVector():
    pass


def _patchMEulerRotation():
    pass


def _testMPoint():
    pass


def _testMColor():
    pass


def _patchMMatrix():
    pass


def _patchMFloatVector():
    pass


def equivalentSpace(space1, space2, rotationOnly=False):
    """
    Compare the two given space values to see if they are equal
    
    Parameters
    ----------
    space1 : int or str
        the first space to compare (may be either the integer enum value, or the
        api enum name - ie, "kPostTransform" - or the pymel enum name - ie,
        "postTransform" )
    space2 : int or str
        the seoncd space to compare (may be either the integer enum value, or
        the api enum name - ie, "kPostTransform" - or the pymel enum name - ie,
        "postTransform")
    rotationOnly : bool
        If true, then compare the spaces, assuming we are only considering
        rotation - in rotation, transform is the same as preTransform/object
        (the reason being that in maya, preTransform means rotation +
        translation are both defined in the preTransform/object coordinate
        system, while transform means rotation is defined in preTransform/object
        coordinates, while translate is given in the postTransform space...
        which matches the way maya applies transforms)
    """

    pass


def planar(p, *args, **kwargs):
    """
    planar(p[, q, r, s (...), tol=tolerance]) --> bool
    Returns True if all provided MPoints are planar within given tolerance
    """

    pass


def _patchMPoint():
    pass


def _patchMVector():
    """
    # patch some Maya api classes that miss __iter__ to make them iterable / convertible to list
    """

    pass


def center(p, *args):
    """
    center(p[, q, r, s (...)]) --> Point
    Returns the Point that is the center of p, q, r, s (...)
    """

    pass


def bWeights(p, *args):
    """
    bWeights(p[, p0, p1, (...), pn]) --> tuple
    Returns a tuple of (n0, n1, ...) normalized barycentric weights so that n0*p0 + n1*p1 + ... = p
    """

    pass


def _testMMatrix():
    pass


def _testMTransformationMatrix():
    pass


def _patchMFloatPoint():
    pass


def _patchMTransformationMatrix():
    pass


def _patchMQuaternion():
    pass



Spaces = {}

AS_UNITS = 'asUnits'


