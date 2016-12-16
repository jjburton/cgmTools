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
    
    
#Bosker's stuff ===========================================================================================================================
def Clamp(val, minimum, maximum):
    '''Clamps the value between 2 minimum and maximum values'''
    return max(min(val,maximum),minimum)

def Lerp(start, end, percent):
    '''Linearly interpolate between 2 floating point variables by a given percentage'''
    return (start + percent*(end - start));

def isclose(a, b, rel_tol=1e-04, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

'''
Lerp and Slerp functions translated from taken from https://keithmaggio.wordpress.com/2011/02/15/math-magician-lerp-slerp-and-nlerp/
'''

class Vector3(euclid.Vector3):

    forward = euclid.Vector3(0,0,1)
    back    = euclid.Vector3(0,0,-1)
    left    = euclid.Vector3(-1,0,0)
    right   = euclid.Vector3(1,0,0)
    up      = euclid.Vector3(0,1,0)
    down    = euclid.Vector3(0,-1,0)

    zero    = euclid.Vector3(0,0,0)
    one     = euclid.Vector3(1,1,1)

    #def __init__(self, x=0, y=0, z=0):
    #	super(euclid.Vector3, self).__init__(x, y, z)

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