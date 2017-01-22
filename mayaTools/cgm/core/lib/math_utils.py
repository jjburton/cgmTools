"""
------------------------------------------
math_utils: cgm.core.lib.math_utils
Authors: Josh Burton & David Bokser
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
# From Python =============================================================

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
from maya import mel
#import cgm.core.lib.euclid as euclid
import euclid as euclid

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core.cgmPy import validateArgs as VALID

'''
Lerp and Slerp functions translated from taken from https://keithmaggio.wordpress.com/2011/02/15/math-magician-lerp-slerp-and-nlerp/
'''

class Vector3(euclid.Vector3):
    @staticmethod
    def    forward():
        return euclid.Vector3(0,0,1)

    @staticmethod
    def    back():
        return euclid.Vector3(0,0,-1)

    @staticmethod
    def    left():
        return euclid.Vector3(-1,0,0)

    @staticmethod
    def    right():
        return euclid.Vector3(1,0,0)

    @staticmethod
    def    up():
        return euclid.Vector3(0,1,0)

    @staticmethod
    def    down():
        return euclid.Vector3(0,-1,0)


    @staticmethod
    def    zero():
        return euclid.Vector3(0,0,0)

    @staticmethod
    def    one():
        return euclid.Vector3(1,1,1)

    #def __init__(self, x=0, y=0, z=0):
    #    super(euclid.Vector3, self).__init__(x, y, z)

    @staticmethod
    def Lerp(start, end, percent):
        '''Linearly interpolate between 2 Vector3 variables by a given percentage'''
        return (start + percent*(end - start))

    @staticmethod
    def Slerp(start, end, percent):
        '''Slerp between 2 Vector3 variables by a given percentage'''
        # Dot product - the cosine of the angle between 2 vectors.
        dot = start.dot(end)     
        # Clamp it to be in the range of Acos()
        # This may be unnecessary, but floating point
        # precision can be a fickle mistress.
        dot = Clamp(dot, -1.0, 1.0)
        # Acos(dot) returns the angle between start and end,
        # And multiplying that by percent returns the angle between
        # start and the final result.
        theta = math.acos(dot)*percent
        RelativeVec = end - start*dot
        RelativeVec.normalize()     # Orthonormal basis
        # The final result.
        return ((start*math.cos(theta)) + (RelativeVec*math.sin(theta)))

    @staticmethod
    def Nlerp(start, end, percent):
        '''Normalized linear interpolation between 2 Vector3 variables by a given percentage'''
        return Vector3.Lerp(start,end,percent).normalized()

    @staticmethod
    def Create(v):
        '''Returns a Vector object from a 3 value array'''
        return euclid.Vector3(v[0], v[1], v[2])

    @staticmethod
    def AsArray(v):
        '''Returns an array from a Vector object'''
        return [v.x, v.y, v.z]


#>>> Utilities
#===================================================================

def get_average_pos(posList = []):
    """
    Returns the average of a list of given positions
    
    :parameters:
        posList(list): List of positions
    :returns
        average(list)
    """   
    _str_func = 'get_average_pos'
    
    posX = []
    posY = []
    posZ = []
    for pos in posList:
        posBuffer = pos
        posX.append(posBuffer[0])
        posY.append(posBuffer[1])
        posZ.append(posBuffer[2])
    return [float(sum(posX)/len(posList)), float(sum(posY)/len(posList)), float(sum(posZ)/len(posList))]    

def get_vector_of_two_points(point1,point2):
    """
    Get a vector between two points
    
    :parameters:
        point1(list): [x,x,x]
        point2(list): [x,x,x]

    :returns
        point(x,y,z)
    """         
    _str_func = 'get_vector_of_points'
    
    _point1 = Vector3(point1[0],point1[1],point1[2])
    _point2 = Vector3(point2[0],point2[1],point2[2])
    
    _new = (_point2 - _point1).normalized()
    
    return _new.x,_new.y,_new.z    
    
def get_space_value(arg, mode = 'mayaSpace'):
    """
    Space conversion of values. api which is in cm to maya space and vice versa
    
    :parameters:
        arg(float/list)
        mode(str)
            mayaSpace -- api(cm) to maya
            apiSpace -- maya to api(cm)

    :returns
        converted value(s)
        
    :Acknowledgement
    Thanks to parentToSurface.mel from autodesk for figuring out this was necessary

    """         
    _str_func = 'get_space_value'
    
    _values = VALID.listArg(arg) 
    _res = []
    unit = mc.currentUnit(q=True,linear=True)
    
    if mode == 'mayaSpace':
        for v in _values:
            if unit == 'mm':
                _res.append(v * 10)
            elif unit =='cm':
                _res.append(v)
            elif unit =='m':
                _res.append(v * .01)
            elif unit == 'in':
                _res.append(v * 0.393701)
            elif unit == 'ft':
                _res.append(v * 0.0328084)
            elif unit =='yd':
                _res.append(v * 0.0109361)
            else:
                raise ValueError,"|{0}| >> nonhandled unit: {1}".format(_str_func,unit)
    elif mode == 'apiSpace':
        for v in _values:
            if unit == 'mm':
                _res.append(v * .1)
            elif unit =='cm':
                _res.append(v)
            elif unit =='m':
                _res.append(v * 100)
            elif unit == 'in':
                _res.append(v * 2.54)
            elif unit == 'ft':
                _res.append(v * 30.48)
            elif unit =='yd':
                _res.append(v * 91.44)
            else:
                raise ValueError,"|{0}| >> nonhandled unit: {1}".format(_str_func,unit)    
    else:
        raise ValueError,"|{0}| >> unknown mode: {1}".format(_str_func,mode)

    if len(_res) == 1:
        return _res[0]
    return _res

def ut_isFloatEquivalent():
    assert is_float_equivalent(-4.11241646134e-07,0.0),"sc>0.0 fail"
    assert is_float_equivalent(-4.11241646134e-07,0.00001),"sc>0.00001 fail"
    assert is_float_equivalent(-4.11241646134e-07,-0.0),"sc>0.00001 fail"
    assert is_float_equivalent(0.0,-0.0),"0.0>-0.0 fail"
    assert is_float_equivalent(0.0,0),"0.0>0 fail"
    
def is_float_equivalent(f1,f2,places=4):
    """
    Compare two floats, returns if equivalent
    
    :parameters:
        f1(float)
        f2(float)
        places(int) - how many places to check to

    :returns
        status(bool)
    """         
    _str_func = 'is_float_equivalent'
    
    #zeroCheck
    l_zeros = [-0.0,0.0]

    if round(f1,places) in l_zeros and round(f2,places) in l_zeros:
        log.debug("|{0}| >> zero match: {1}|{2}".format(_str_func,f1,f2))
        return True

    f1_rounded = round(f1,places)
    f2_rounded = round(f2,places)

    if f1_rounded == f2_rounded:
        return True
    return False     
    
def is_vector_equivalent(v1,v2,places=7):
    """
    Compare two floats, returns if equivalent
    
    :parameters:
        f1(float)
        f2(float)
        places(int) - how many places to check to

    :returns
        status(bool)
    """ 
    if type(v1) not in [list,tuple]:return False
    if type(v2) not in [list,tuple]:return False
    
    if len(v1)!= len(v2):return False 

    for i,n in enumerate(v1):
        if not is_float_equivalent(n,v2[i],places):
            return False
    return True
    
#Bosker's stuff ===========================================================================================================================
def Clamp(val, minimum, maximum):
    '''Clamps the value between 2 minimum and maximum values'''
    return max(min(val,maximum),minimum)

def Lerp(start, end, percent):
    '''Linearly interpolate between 2 floating point variables by a given percentage'''
    return (start + percent*(end - start));

def isclose(a, b, rel_tol=1e-04, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def get_world_matrix(obj):
    matrix_a = mc.xform( obj, q=True, m=True, ws=True )
    current_matrix = euclid.Matrix4()
    current_matrix.a = matrix_a[0]
    current_matrix.b = matrix_a[1]
    current_matrix.c = matrix_a[2]
    current_matrix.d = matrix_a[3]
    current_matrix.e = matrix_a[4]
    current_matrix.f = matrix_a[5]
    current_matrix.g = matrix_a[6]
    current_matrix.h = matrix_a[7]
    current_matrix.i = matrix_a[8]
    current_matrix.j = matrix_a[9]
    current_matrix.k = matrix_a[10]
    current_matrix.l = matrix_a[11]
    current_matrix.m = matrix_a[12]
    current_matrix.n = matrix_a[13]
    current_matrix.o = matrix_a[14]
    current_matrix.p = matrix_a[15]

    return current_matrix

def transform_direction(obj, v):
    '''
    Get local position of vector transformed from world space of Transform
    
    Inputs: string, Vector3
    Returns: Vector3
    '''
    
    current_matrix = get_world_matrix(obj)
    current_matrix.m = 0
    current_matrix.n = 0
    current_matrix.o = 0

    s = Vector3.Create( mc.getAttr('%s.scale' % obj)[0] )

    transform_matrix = euclid.Matrix4()
    transform_matrix.m = v.x
    transform_matrix.n = v.y
    transform_matrix.o = v.z

    scale_matrix = euclid.Matrix4()
    scale_matrix.a = s.x
    scale_matrix.f = s.y
    scale_matrix.k = s.z
    scale_matrix.p = 1

    result_matrix = transform_matrix * current_matrix * scale_matrix

    result_vector = Vector3(result_matrix.m, result_matrix.n, result_matrix.o) - Vector3(current_matrix.m, current_matrix.n, current_matrix.o)

    return result_vector

def convert_aim_vectors_to_different_axis(aim, up, aimAxis="z+", upAxis="y+"):
    # get the full axis vectors
    aim = aim.normalized()
    up = up.normalized()
    right = up.cross(aim).normalized()
    up = aim.cross(right).normalized()

    wantedAim = None
    wantedUp = None

    # wanted aim
    if aimAxis == "z+":
        wantedAim = aim
    elif aimAxis == "z-":
        wantedAim = -aim
    elif aimAxis == "x+":
        if upAxis == "y+":
            wantedAim = -right
        elif upAxis == "y-":
            wantedAim = right
        elif upAxis == "z+":
            wantedAim = up
        elif upAxis == "z-":
            wantedAim = -up
    elif aimAxis == "x-":
        if upAxis == "y+":
            wantedAim = right
        elif upAxis == "y-":
            wantedAim = -right
        elif upAxis == "z+":
            wantedAim = up
        elif upAxis == "z-":
            wantedAim = -up
    elif aimAxis == "y+":
        if upAxis == "x+":
            wantedAim = right
        elif upAxis == "x-":
            wantedAim = -right
        elif upAxis == "z+":
            wantedAim = up
        elif upAxis == "z-":
            wantedAim = -up
    elif aimAxis == "y-":
        if upAxis == "x+":
            wantedAim = -right
        elif upAxis == "x-":
            wantedAim = right
        elif upAxis == "z+":
            wantedAim = up
        elif upAxis == "z-":
            wantedAim = -up

    # wanted up
    if upAxis == "y+":
        wantedUp = up
    elif upAxis == "y-":
        wantedUp = -up
    elif upAxis == "z+":
        if aimAxis == "x+":
            wantedUp = right
        elif aimAxis == "x-":
            wantedUp = -right
        elif aimAxis == "y+":
            wantedUp = aim
        elif aimAxis == "y-":
            wantedUp = -aim
    elif upAxis == "z-":
        if aimAxis == "x+":
            wantedUp = -right
        elif aimAxis == "x-":
            wantedUp = right
        elif aimAxis == "y+":
            wantedUp = aim
        elif aimAxis == "y-":
            wantedUp = -aim
    elif upAxis == "x+":
        if aimAxis == "y+":
            wantedUp = aim
        elif aimAxis == "y-":
            wantedUp = -aim
        elif aimAxis == "z+":
            wantedUp = -right
        elif aimAxis == "z-":
            wantedUp = right
    elif upAxis == "x-":
        if aimAxis == "y+":
            wantedUp = aim
        elif aimAxis == "y-":
            wantedUp = -aim
        elif aimAxis == "z+":
            wantedUp = right
        elif aimAxis == "z-":
            wantedUp = -right

    return wantedAim, wantedUp

