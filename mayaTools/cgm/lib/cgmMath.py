#=================================================================================================================================================
#=================================================================================================================================================
#	cgmMath - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
# 
# DESCRIPTION:
#	Series of tools for working with cgmMath
# 
# ARGUMENTS:
# 	rigging
# 
# AUTHOR:
# 	Josh Burton (under the supervision of python guru David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
# 
# CHANGELOG:
#	0.1 - 02/09/2011 - added documenation
#
# FUNCTION KEY:
#   1) returnDistanceBetweenPoints (point1, point2)
#   
#=================================================================================================================================================
#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
import math
#=========================================================================

def multiplyLists(lists,allowZeros = True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Muliplies a list of lists
    
    ARGUMENTS:
    lists(list) - [[2,3,4],[2,3,4],[2,3,4,3]]
    
    RETURNS:
    number(list) - [8, 27, 64, 3]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    indicesDict = {}
    lenBuffer = []
    for list in lists:
        lenBuffer.append(len(list))
    terms = max(lenBuffer)
    
    """ collect our values """
    for i in range(terms):
        valueBuffer = []
        for list in lists:
            if (len(list)) > i:
                if list[i] != 0:
                    valueBuffer.append(list[i])
                elif allowZeros == True:
                    valueBuffer.append(list[i])
                else:
                    valueBuffer.append(1)
        indicesDict[i] = valueBuffer
    
    returnList = []
    """ multiply """
    for key in indicesDict:
        buffer = indicesDict.get(key)
        returnList.append(multiplyList(buffer))
    
    return returnList
      
def multiplyList(listToMultiply):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Muliplies all non zero values in a list
    
    ARGUMENTS:
    listToMultiply(listToMultiply) - [124,2,0,4]
    
    RETURNS:
    number(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    return reduce(lambda x,y: x*y, listToMultiply)

def list_subtract(l1,l2):
    """ 
    """
    if len(l1)!=len(l2):
        raise StandardError,"list_subtract>>> lists must be same length! l1: %s | l2: %s"%(l1,l2)
    l_return = []
    for i,x in enumerate(l1):
        l_return.append( x-l2[i])
    return l_return

def list_add(l1,l2):
    """ 
    """
    if len(l1)!=len(l2):
        raise StandardError,"list_subtract>>> lists must be same length! l1: %s | l2: %s"%(l1,l2)
    l_return = []
    for i,x in enumerate(l1):
        l_return.append( x+l2[i])
    return l_return
# ====================================================================================================================
# FUNCTION - 1
# From - http://code.activestate.com/recipes/278258-list-tools/
#
# SIGNATURE:
#	normList(L, normalizeTo=1)
#
# DESCRIPTION:
#   normalize values of a list to make its max = normalizeTo
# 
# ARGUMENTS:
#   L - list to normalize
# 	normalizeTo - the value to normalize to
#
# RETURNS:
#	normalized list
#
# ====================================================================================================================
def normList(L, normalizeTo=1):
    '''normalize values of a list to make its max = normalizeTo'''

    vMax = max(L)
    return [ x/(vMax*1.0)*normalizeTo for x in L]
    
# ====================================================================================================================
# FUNCTION - 2
#
# SIGNATURE:
#	divideLength(length, points)
#
# DESCRIPTION:
#   Divide a length into the positions of the number of points input
# 
# ARGUMENTS:
# 	length - 
#   points - the number of points on the length you want
#
# RETURNS:
#	point list
#
# ====================================================================================================================
def divideLength(length, points):
    """
    Pass at length and number of points on that length you want and it will return a list of the postions along that length:
    divideLength(10,5) = [0,2.5,5,7.5,10]
    """
    pointsList = []
    pointsList.append(0)
    
    #return mid points    
    segmentLength = length/float(points-1)
    cnt = 1
    for p in range (points-2):
        pnt = cnt * segmentLength
        cnt+=1
        pointsList.append(pnt)
    
    pointsList.append(length)
    return pointsList

def mag(v):
    assert type(v) in [list,tuple],"mag>>> arg must be vector"
    try:
        return math.sqrt(sum(i**2 for i in v))
    except:
        raise StandardError,"mag>>> Failure: %s"%v
    
def test_isFloatEquivalent():
    assert isFloatEquivalent(-4.11241646134e-07,0.0),"sc>0.0 fail"
    assert isFloatEquivalent(-4.11241646134e-07,0.00001),"sc>0.00001 fail"
    assert isFloatEquivalent(-4.11241646134e-07,-0.0),"sc>0.00001 fail"
    assert isFloatEquivalent(0.0,-0.0),"0.0>-0.0 fail"
    assert isFloatEquivalent(0.0,0),"0.0>0 fail"

def isFloatEquivalent(f1,f2,places=4):
    """
    Compare two floats, returns if equivalent
    """ 
    #zeroCheck
    l_zeros = [-0.0,0.0]
    zeroState = False
    
    if round(f1,places) in l_zeros and round(f2,places) in l_zeros:
        log.debug("zero match: %s|%s"%(f1,f2))
        return True
    
    #reg check
    f1_rounded = round(f1,places)
    f2_rounded = round(f2,places)
    #log.info(f1_rounded)
    #log.info(f2_rounded) 
    if f1_rounded == f2_rounded:
        return True
    return False 
    
def isVectorEquivalent(v1,v2,places=7):
    """
    Compare two vectors, returns if equivalent
    """ 
    if type(v1) not in [list,tuple]:return False
    if type(v2) not in [list,tuple]:return False
    if len(v1)!= len(v2):return False 
    
    for i,n in enumerate(v1):
        if not isFloatEquivalent(n,v2[i],places):
            return False
    return True

    
