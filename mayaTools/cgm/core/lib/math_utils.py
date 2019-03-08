"""
------------------------------------------
math_utils: cgm.core.lib.math_utils
Authors: Josh Burton & David Bokser
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
# From Python =============================================================
import pprint
import copy
import math

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
from maya import mel
#import cgm.core.lib.euclid as euclid
import euclid as EUCLID

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
import cgm.core.cgm_General as cgmGEN

#DO NOT IMPORT: DIST
'''
Lerp and Slerp functions translated from taken from https://keithmaggio.wordpress.com/2011/02/15/math-magician-lerp-slerp-and-nlerp/
'''

class Vector3(EUCLID.Vector3):
    @staticmethod
    def    forward():
        return EUCLID.Vector3(0,0,1)

    @staticmethod
    def    back():
        return EUCLID.Vector3(0,0,-1)

    @staticmethod
    def    left():
        return EUCLID.Vector3(-1,0,0)

    @staticmethod
    def    right():
        return EUCLID.Vector3(1,0,0)

    @staticmethod
    def    up():
        return EUCLID.Vector3(0,1,0)

    @staticmethod
    def    down():
        return EUCLID.Vector3(0,-1,0)


    @staticmethod
    def    zero():
        return EUCLID.Vector3(0,0,0)

    @staticmethod
    def    one():
        return EUCLID.Vector3(1,1,1)

    #def __init__(self, x=0, y=0, z=0):
    #    super(EUCLID.Vector3, self).__init__(x, y, z)

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
        return EUCLID.Vector3(v[0], v[1], v[2])

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

def get_normalized_parameter(minV,maxV,value,asEuclid=False):
    """
    """         
    _str_func = 'get_normalized_parameter'
    

    _range = (float(maxV) - float(minV)) 
    _diff = value - minV
    return _diff / _range
    
    if asEuclid:
        return Vector3(_new.x,_new.y,_new.z)
    return _new.x,_new.y,_new.z    


def get_vector_of_two_points(point1,point2,asEuclid=False):
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
    if asEuclid:
        return Vector3(_new.x,_new.y,_new.z)
    return _new.x,_new.y,_new.z    


def get_obj_vector(obj = None, axis = 'z+',asEuclid = False):
    """
    Get the vector along an object axis
    
    :parameters:
        obj(string)
        axis(str)
        asEuclid(bool) - data return format

    :returns
        vector(s)
        
    :Acknowledgement
    Thanks to parentToSurface.mel from autodesk for figuring out this was necessary

    """         
    _str_func = 'get_obj_vector'
    obj = VALID.mNodeString(obj)
    #if not mc.objExists(obj):
        #raise ValueError,"Must have an obj to get a vector when no vector is provided"

    d_matrixVectorIndices = {'x':[0,1,2],
                             'y': [4,5,6],
                             'z' : [8,9,10]}

    matrix = mc.xform(obj, q=True,  matrix=True, worldSpace=True)
    
    #>>> Figure out our vector
    if axis not in SHARED._d_axis_string_to_vector.keys():
        log.error("|{0}| >> axis arg not valid: '{1}'".format(_str_func,axis))
        return False
    if list(axis)[0] not in d_matrixVectorIndices.keys():
        log.error("|{0}| >> axis arg not in d_matrixVectorIndices: '{1}'".format(_str_func,axis))            
        return False  
    vector = [matrix[i] for i in d_matrixVectorIndices.get(list(axis)[0])]
    if list(axis)[1] == '-':
        for i,v in enumerate(vector):
            vector[i]=-v
            
    mVector = Vector3(vector[0],vector[1],vector[2])
    mVector.normalize()
    if asEuclid:
        return mVector
    return mVector.x,mVector.y,mVector.z
    
    
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
    
    
def is_even(f1):
    if f1%2 == 0:
        return True
    return False

def get_midIndex(v):
    if is_even(v):
        return int(v/2)
    return v/2 +1

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
    l_zeros = [-0.0,0.0,-2e-20]

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

def multiply(valueList):
    _res = None
    if valueList:
        for i,v in enumerate(valueList[:-1]):
            _res = v * valueList[i+1]
    return _res
    #from math import log, exp
    #return exp(sum(map(log, valueList))) # -- doesn't work for negative values



#Bosker's stuff ===========================================================================================================================
def Clamp(val, minimum=None, maximum=None):
    '''Clamps the value between 2 minimum and maximum values'''
    if minimum is None and maximum is None:
        return val
    if maximum is  None and minimum is not None:
        return  max(val,minimum)
    if minimum is None and maximum is not None:
        return min(val,maximum)
    return max(min(val,maximum),minimum)

def Lerp(start, end, percent):
    '''Linearly interpolate between 2 floating point variables by a given percentage'''
    return (start + percent*(end - start));

def isclose(a, b, rel_tol=1e-04, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def get_world_matrix(obj):
    matrix_a = mc.xform( obj, q=True, m=True, ws=True )
    current_matrix = EUCLID.Matrix4()
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

    transform_matrix = EUCLID.Matrix4()
    transform_matrix.m = v.x
    transform_matrix.n = v.y
    transform_matrix.o = v.z

    scale_matrix = EUCLID.Matrix4()
    scale_matrix.a = s.x
    scale_matrix.f = s.y
    scale_matrix.k = s.z
    scale_matrix.p = 1

    result_matrix = transform_matrix * current_matrix * scale_matrix

    result_vector = Vector3(result_matrix.m, result_matrix.n, result_matrix.o) - Vector3(current_matrix.m, current_matrix.n, current_matrix.o)

    return result_vector

def convert_aim_vectors_to_different_axis(aim, up, aimAxis="z+", upAxis="y+"):
    try:
        aim = Vector3.Create( aim )
        up = Vector3.Create( up )

        reload(VALID)
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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)

def normalizeList(L, normalizeTo=1):
    '''normalize values of a list to make its max = normalizeTo'''
    vMax = max(L)
    return [ x/(vMax*1.0)*normalizeTo for x in L]

def find_valueInList(v,l,mode='near'):
    _d = {}
    _l = []
    _l_use = []
    
    if mode == 'previous':
        for v1 in l:
            if v1 < v:
                _l_use.append(v1)
    elif mode == 'next':
        for v1 in l:
            if v1 > v:
                _l_use.append(v1)
    else:_l_use = copy.copy(l)
        
    for v1 in _l_use:
        _diff = abs(v1 - v)
        _l.append(_diff)
        _d[_diff] = v1
    
    pprint.pprint(vars())
    if mode in ['near','previous','next']:return _d[min(_l)]
    elif mode == 'far':return _d[max(_l)]


def get_blendList(count, maxValue=1.0, minValue = 0.0, mode = 'midPeak'):
    '''
    Get a factored list 
    
    :parameters:
        count(int) - number of values sought
        maxValue(float)
        minValue(float)
        mode(string)
            min
            max
            midPeak - ease to peak and back
            midBlendDown - max to mid then blend down
            midBlendUp  - blend from min to max then max
            
    :returns:
        list of values
        
        examples - all with example with count 5, min 0, max 1
            midPeak - [0.0, 0.5, 1.0, 0.5, 0.0]
            midBlendDown - [1.0, 1.0, 1.0, 0.5, 0.0]
            blendUpMid - [0.0, 0.5, 1.0, 1.0, 1.0]
            
    :raises:
        Exception | if reached
    
    '''
    _str_func = 'get_factorList'
    _res = []
    
    if mode in ['midPeak','blendUpMid','midBlendDown']:
        idx_mid = get_midIndex(count)
        
        if maxValue == minValue:
            return [maxValue for i in range(count)]
            
        
        blendFactor = (float(maxValue) - float(minValue))/(idx_mid-1)
        
        if is_even(count):
            for i in range(idx_mid):
                _res.append( i * blendFactor)
            _rev = copy.copy(_res)
            if mode == 'blendUpMid':
                _res = _res + [maxValue for i in range(idx_mid)]
            elif mode == 'midBlendDown':
                _res.reverse()
                _res = [maxValue for i in range(idx_mid)] + _res
            else:
                _rev.reverse()
                _res.extend(_rev)
        else:
            for i in range(idx_mid):
                _res.append( i * blendFactor)
                
            if mode == 'blendUpMid':
                _res = _res + [maxValue for i in range(idx_mid-1)]
            elif mode == 'midBlendDown':
                _res.reverse()
                _res = [maxValue for i in range(idx_mid-1)] + _res
            else:
                _rev = copy.copy(_res)
                _rev.reverse()
                _res.extend(_rev[1:])
            
    elif mode == 'max':
        return [maxValue for i in range(count)]
    elif mode == 'min':
        return [minValue for i in range(count)]
        
        
    else:
        raise ValueError,("|{0}| >> Unknown mode: {1}".format(_str_func,mode))

    #pprint.pprint(vars())
    return _res


def normalizeListToSum(L, normalizeTo=1.0):
    """normalize values of a list to make sum = normalizeTo
    
    For example [.2, .5] becomes [0.33333333333333331, 0.66666666666666663] for a sum of 1.0
    
    Thanks to:
    http://stackoverflow.com/questions/26785354/normalizing-a-list-of-numbers-in-python
    """
    
    #return [float(i)/normalizeTo for i in [float(i)/sum(L) for i in L]]
    norm = normalizeList(L)
    normSum = [float(i)/sum(L) for i in L]
    return [i * normalizeTo for i in normSum]

def get_splitValueList(minU = 0,
                       maxU = 1,
                       points = 3,
                       cullStartEnd = False,
                       startSplitFactor = None,
                       insetSplitFactor = None):
    """
    Function for parsing up a line of values (like a curve.u list or a surface.uv list  
    
    :parameters:
        minU(float) - Minimum value to use to start splitting
        maxU(float) - Maximum value to use to start splitting
        points(int) - Number of points to generate values for
        cullStartEnd() - If you want the start and end culled from the list
        startSplitFactor() - inset factor for subsequent splits after then ends
        insetSplitFactor() - Multiplier for pushing splits one way or another on a curve

    :returns
        values(list)
    """         
    _str_func = 'get_splitValueList'
    
    if insetSplitFactor is not None or startSplitFactor is not None:
        if not is_float_equivalent(minU,0):
            raise StandardError,"Min U must be 0 when insetSplitFactor or startSplitFactor are used"
    
    #>>> Divide stuff
    #==========================	
    l_spanUPositions = []    
    l_uValues = [minU]
    
    minU = float(minU)
    maxU = float(maxU)
    
    log.debug("%s >> maxU : %s"%(_str_func,maxU)) 

    if startSplitFactor is not None:
        if points < 5:
            raise StandardError,"Need at least 5 points for startSplitFactor. Points : %s"%(points)
        log.debug("%s >> startSplitFactor : %s"%(_str_func,startSplitFactor))  
        #Figure out our u's
        f_base = startSplitFactor * maxU 
        l_uValues.append( f_base )
        f_len = maxU - (f_base *2)	
        int_toMake = points-4
        f_factor = f_len/(int_toMake+1)
        log.debug("%s >> f_len : %s"%(_str_func,f_len)) 	
        log.debug("%s >> int_toMake : %s"%(_str_func,int_toMake)) 						
        log.debug("%s >> f_base : %s"%(_str_func,f_base)) 			
        log.debug("%s >> f_factor : %s"%(_str_func,f_factor))               
        for i in range(1,points-3):
            l_uValues.append(((i*f_factor + f_base)))
        l_uValues.append(maxU - f_base)
        l_uValues.append(maxU)
        log.debug("%s >> l_uValues : %s"%(_str_func,l_uValues))  	

    elif insetSplitFactor is not None:
        log.debug("%s >> insetSplitFactor : %s"%(_str_func,insetSplitFactor))  
        #Figure out our u's

        f_base = insetSplitFactor * maxU 
        f_len = maxU - (f_base *2)	
        f_factor = f_len/(points-1)

        #f_base = (maxU - minU) * insetSplitFactor
        #f_len = (maxU - f_base) - (minU + f_base)
        #f_factor = f_len/(points-1)
        log.debug("%s >> f_base : %s"%(_str_func,f_base)) 					    
        log.debug("%s >> f_len : %s"%(_str_func,f_len)) 			
        log.debug("%s >> f_factor : %s"%(_str_func,f_factor))               
        for i in range(1,points-1):
            l_uValues.append(((i*f_factor)+f_base))
        l_uValues.append(maxU)
        log.debug("%s >> l_uValues : %s"%(_str_func,l_uValues))

    else:
        #Figure out our u's
        log.debug("|{0}| >> Regular mode. Points: {1}".format(_str_func,points))
        
        if points == 1:
            l_uValues = [((maxU - minU)/2)+minU]
        elif points == 2:
            l_uValues = [minU,maxU]
        elif points == 3:            
            l_uValues.append(((maxU - minU)/2)+minU)
            l_uValues.append(maxU)
        else:
            f_factor = (maxU-minU)/(points-1)
            log.debug("%s >> maxU : %s"%(_str_func,maxU)) 
            log.debug("%s >> f_factor : %s"%(_str_func,f_factor))               
            for i in range(1,points-1):
                l_uValues.append((i*f_factor)+minU)
            l_uValues.append(maxU)
        log.debug("%s >> l_uValues : %s"%(_str_func,l_uValues))  

    if cullStartEnd and len(l_uValues)>3:
        l_uValues = l_uValues[1:-1]

    return l_uValues
    

def list_subtract(l1,l2):
    """ 
    """
    if len(l1)!=len(l2):
        raise ValueError,"list_subtract>>> lists must be same length! l1: %s | l2: %s"%(l1,l2)
    l_return = []
    for i,x in enumerate(l1):
        l_return.append( x-l2[i])
    return l_return

def list_add(l1,l2):
    """ 
    """
    if len(l1)!=len(l2):
        raise ValueError,"list_add>>> lists must be same length! l1: %s | l2: %s"%(l1,l2)
    l_return = []
    for i,x in enumerate(l1):
        l_return.append( x+l2[i])
    return l_return

def list_mult(l1,l2):
    """ 
    """
    if len(l1)!=len(l2):
        raise ValueError,"list_mult>>> lists must be same length! l1: %s | l2: %s"%(l1,l2)
    l_return = []
    for i,x in enumerate(l1):
        l_return.append( x*l2[i])
    return l_return

def list_div(l1,l2):
    """ 
    """
    if len(l1)!=len(l2):
        raise ValueError,"list_div>>> lists must be same length! l1: %s | l2: %s"%(l1,l2)
    l_return = []
    for i,x in enumerate(l1):
        l_return.append( x/l2[i])
    return l_return

def average(*args):
    """ 
    """
    if VALID.isListArg(args[0]):
        l=args[0]
    else:
        l = [a for a in args]
    return sum(l)/len(l)

def get_greatest(*args):
    """ 
    """
    if VALID.isListArg(args[0]):
        l=args[0]
    else:
        l = [a for a in args]
        
    return max(l)

def median(*args):
    """ 
    https://stackoverflow.com/questions/24101524/finding-median-of-list-in-python
    """
    if VALID.isListArg(args[0]):
        l=args[0]
    else:
        l = [a for a in args]
    
    n = len(l)
    if n < 1:
            return None
    if n % 2 == 1:
            return sorted(l)[n//2]
    else:
            return sum(sorted(l)[n//2-1:n//2+1])/2.0    

def angleBetween(p1, p2, p3):
    p1 = VALID.euclidVector3Arg(p1)
    p2 = VALID.euclidVector3Arg(p2)
    p3 = VALID.euclidVector3Arg(p3)
    
    v1 = (p2 - p1).normalized()
    v2 = (p3 - p2).normalized()
    
    return math.degrees(v1.angle(v2))



