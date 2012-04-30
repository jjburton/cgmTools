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
    
