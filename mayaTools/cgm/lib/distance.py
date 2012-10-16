#=================================================================================================================================================
#=================================================================================================================================================
#	distance - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Series of tools for working with distances
#
# ARGUMENTS:
# 	rigging, nodes
#
# AUTHOR:
# 	Josh Burton (under the supervision of python guru David Bokser) - jjburton@gmail.com
#	http://www.cgmonks.com
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# CHANGELOG:
#
# FUNCTION SECTIONS:
#   1) Measure Tools - measuring distances between stuff
#   2) Positional Information - Querying positional info
#   3) Measure Rigs - Setups for continual information
#   4) Size Tools - Volume info
#   5) Proximity Tools - Finding closest x to y
#   6) returnBoundingBoxSize (meshGrp/mesh/obj)
#
#=================================================================================================================================================
import maya.cmds as mc
import maya.OpenMaya as om

import maya.mel as mel
import copy

from cgm.lib import (nodes,
                     rigging,
                     lists,
                     search,
                     geo,
                     cgmMath,
                     attributes)

from math import sqrt,pow

# Maya version check
mayaVersion = int( mel.eval( 'getApplicationVersionAsFloat' ) )

def returnMayaSpaceFromWorldSpace(value):
    """
    Thanks to parentToSurface.mel from autodesk for figuring out this was necessary
    
    
    """
    assert type(float(value)) is float,"'%s' is not a numeric value"%value
    unit = mc.currentUnit(q=True,linear=True)
	
    if unit == 'mm':
	return (value * 10)
    elif unit =='cm':
	return value
    elif unit =='m':
	return(value * .01)
    elif unit == 'in':
	return(value * 0.393701)
    elif unit == 'ft':
	return(value * 0.0328084)
    elif unit =='yd':
	return(value * 0.0109361)
    else:
	return value
    
def returnWorldSpaceFromMayaSpace(value):
    """
    Thanks to parentToSurface.mel from autodesk for figuring out this was necessary
        
    """
    assert type(float(value)) is float,"'%s' is not a numeric value"%value
    unit = mc.currentUnit(q=True,linear=True)
	
    if unit == 'mm':
	return (value * .1)
    elif unit =='cm':
	return value
    elif unit =='m':
	return(value * 100)
    elif unit == 'in':
	return(value * 2.54)
    elif unit == 'ft':
	return(value * 30.48)
    elif unit =='yd':
	return(value * 91.44)
    else:
	return value
				
#			
#

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Measure Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDistanceBetweenPoints (point1, point2):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Get's the distance bewteen two points

    ARGUMENTS:
    point1(list) - [x,x,x]
    point1(list) - [x,x,x]

    RETURNS:
    distance(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    distance = sqrt( pow(point1[0]-point2[0], 2) + pow(point1[1]-point2[1], 2) + pow(point1[2]-point2[2], 2) )
    return distance
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnDistanceBetweenObjects (obj1, obj2):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Gets the distance bewteen two objects

    ARGUMENTS:
    obj1(string)
    obj2(string)

    RETURNS:
    distance(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    point1 = returnWorldSpacePosition (obj1)
    point2 = returnWorldSpacePosition (obj2)
    distance = returnDistanceBetweenPoints (point1,point2)
    return distance
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDistanceBetweenObjectsList (objList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Measure the distance between an list of objects. From object1 to object2, then object2 to object3, etc.

    ARGUMENTS:
    objectList(list) - list of objects

    RETURNS:
    distanceList(list) - list of the distances between the objects
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ Pass an list of objects into it and return an list of distances between them. Input - objList(list).  Return - distanceList(list) """
    cnt = 0
    distancesList = []
    cnt = (len(objList) - 1)
    firstTermCnt = 0
    secondTermCnt = 1
    while cnt > 0:
        distance =returnDistanceBetweenObjects (objList[firstTermCnt], objList[secondTermCnt])
        distancesList.append (distance)
        firstTermCnt +=1
        secondTermCnt +=1
        cnt -= 1
        if (cnt == 0):
            break
    return distancesList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Averages
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnAveragePointPosition (posList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass a list of objects into it and get an average position back

    ARGUMENTS:
    objList(list) - list of objects to measure between

    RETURNS:
    averageDistance (float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    posX = []
    posY = []
    posZ = []
    for pos in posList:
        posBuffer = pos
        posX.append(posBuffer[0])
        posY.append(posBuffer[1])
        posZ.append(posBuffer[2])
    return [float(sum(posX)/len(posList)), float(sum(posY)/len(posList)), float(sum(posZ)/len(posList))]
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def returnAverageDistanceBetweenObjectsAndRoot (objList,root):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an list of objects into it, it measures distances and returns an average.

    ARGUMENTS:
    objList(list) - list of objects to measure between

    RETURNS:
    averageDistance (float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    distanceList = []
    for obj in objList:
        distanceList.append(returnDistanceBetweenObjects(obj,root))
    average = float(sum(distanceList)) / len(distanceList)
    return average
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def returnAverageDistanceBetweenObjects (objList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an list of objects into it, it measures distances and returns an average.

    ARGUMENTS:
    objList(list) - list of objects to measure between

    RETURNS:
    averageDistance (float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    distanceList = returnDistanceBetweenObjectsList (objList)
    average = float(sum(distanceList)) / len(distanceList)
    return average
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnAverageDistanceBetweenPositionList (posList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an list of objects into it, it measures distances and returns an average.

    ARGUMENTS:
    objList(list) - list of objects to measure between

    RETURNS:
    averageDistance (float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    pairList = lists.parseListToPairs(posList)
    distanceList = []
    for pair in pairList:
        distanceList.append(returnDistanceBetweenPoints(pair[0],pair[1]))
    average = float(sum(distanceList)) / len(distanceList)
    return average
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnBoundingBoxSizeToAverage (meshGrp):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object, mesh group or whatever into it,  it calculates it's
    bounding box info and returns list

    ARGUMENTS:
    meshGrp(string) - mesh or mesh group

    RETURNS:
    returnList(list) - [xLength,yLength,zLength]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    boundingBoxSizeList = returnBoundingBoxSize (meshGrp)
    return float(sum(boundingBoxSizeList)) / len(boundingBoxSizeList)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Positional Information
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnWorldSpacePosition (obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Gets an object's world space position

    ARGUMENTS:
    obj(string)

    RETURNS:
    position(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ Queries world space loaction. Input - obj(obj).  Return - pos(list) """
    if 'vtx[' in obj or 'ep[' in obj or 'cv[' in obj:
        posBuffer = mc.pointPosition(obj,w=True)
    else:
        posBuffer = mc.xform (obj,q=True, rp=True, ws=True)
    return posBuffer
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnWorldSpacePositionFromList (objList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates an nested list of postions from a list of locators

    ARGUMENTS:
    objList(list)

    RETURNS:
    positionList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objectionPositionList = []
    for obj in objList:
        tempPos = returnWorldSpacePosition(obj)
        objectionPositionList.append (tempPos)

    return objectionPositionList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Measure Rigs
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def createCurveLengthNode(curve):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a curve lenght measuring node

    ARGUMENTS:
    polyFace(string) - face of a poly

    RETURNS:
    length(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objType = search.returnObjectType(curve)
    shapes = []

    if objType == 'shape':
        shapes.append(curve)
    else:
        shapes = mc.listRelatives(curve,shapes=True)

    #first see if there's a length node
    isConnected = attributes.returnDrivenAttribute(shapes[0]+'.worldSpace[0]')
    if isConnected !=False:
        return (attributes.returnDrivenObject(shapes[0]+'.worldSpace'))
    else:
        infoNode = nodes.createNamedNode(curve,'curveInfo')
        attributes.doConnectAttr((shapes[0]+'.worldSpace'),(infoNode+'.inputCurve'))
        return infoNode


def createDistanceNodeBetweenObjects (obj1,obj2):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a distance node between objects

    ARGUMENTS:
    obj1(string)
    obj2(string)

    RETURNS:
    none
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ Creates a distance node between objects """
    pos1 = returnWorldSpacePosition (obj1)
    pos2 = returnWorldSpacePosition (obj2)
    tmp = mc.distanceDimension( sp=pos1, ep=pos2 )
    distBuffer = mc.listRelatives ( [tmp], p=True)
    distanceObj = mc.rename (distBuffer, (obj1+'_to_'+obj2+'_distMeas') )
    #return the stupid locators it makes so we can connect our own stuff
    distanceStartPoint = (distanceObj+'Shape.startPoint')
    distanceEndPoint = (distanceObj+'Shape.endPoint')
    locAttr1connection =  (mc.connectionInfo (distanceStartPoint,sourceFromDestination=True))
    locAttr2connection =  (mc.connectionInfo (distanceEndPoint,sourceFromDestination=True))
    locAttr1Stripped = '.'.join(locAttr1connection.split('.')[0:-1])
    locAttr2Stripped = '.'.join(locAttr2connection.split('.')[0:-1])
    loc1Buffer = (mc.listRelatives (locAttr1Stripped,parent=True))
    loc2Buffer = (mc.listRelatives (locAttr2Stripped,parent=True))
    distObj1 = mc.rename (loc1Buffer, (obj1+'_distLoc') )
    distObj2 = mc.rename (loc2Buffer, (obj2+'_distLoc') )

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def createDistanceNodeBetweenPosInfoNodes (node1,node2):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Creates a distance node between two position info nodes

    ARGUMENTS:
    node1(string)
    node2(string)

    RETURNS:
    returnList[0] - distance object
    returnList[1] - shape node
    returnList[2] - shape node distance attribute
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    returnList =[]
    distShapeBuffer = mc.createNode ('distanceDimShape')
    distBuffer = (mc.listRelatives (distShapeBuffer,parent=True))
    mc.connectAttr ((node1+'.position'),(distShapeBuffer+'.startPoint'))
    mc.connectAttr ((node2+'.position'),(distShapeBuffer+'.endPoint'))
    distanceObj = mc.rename (distBuffer, (node1+'_to_'+node2+'_distNode') )
    newDistShapeBuffer = (mc.listRelatives (distanceObj,shapes=True))
    returnList.append (distanceObj)
    returnList.append (newDistShapeBuffer[0])
    returnList.append (newDistShapeBuffer[0]+'.distance')
    return returnList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def createDistanceObjectsBetweenObjectList (objList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an list of objects into it, it creates distance dimension objects between them while naming and grouping them

    ARGUMENTS:
    objList - list of objects to measure between

    RETURNS:
    distanceObjList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    cnt = 0
    locatorPositionList = []
    cnt = (len(objList) - 1)
    firstTermCnt = 0
    secondTermCnt =1
    distanceObjList = []
    coreNameList = []
    if mc.objExists ('measure_grp'):
        pass
    else:
        tmp = mc.group (empty=True, name='measure_grp')
        mc.xform (tmp, os=True, piv= (0,0,0))
    for obj in objList:
        """return its positional data"""
        tempPos = mc.xform (obj,q=True, ws=True, rp=True)
        locatorPositionList.append (tempPos)

        tmp = obj.split('_')
        coreNameList.append (tmp[0])
    while cnt > 0:
        distanceObj = mc.distanceDimension( sp=locatorPositionList[firstTermCnt], ep=locatorPositionList[secondTermCnt] )
        tmp = mc.listRelatives ( [distanceObj], p=True)
        tmp = mc.rename (tmp, (coreNameList[firstTermCnt]+'_to_'+coreNameList[secondTermCnt]+'_distMeas') )
        distanceObjList.append (tmp)
        firstTermCnt +=1
        secondTermCnt +=1
        cnt -= 1
        mc.parent (tmp,'measure_grp')
        if (cnt == 0):
            break
    return distanceObjList
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Size Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnAbsoluteSizeCurve(curve):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an curve into it and it returns absolute distance scale

    ARGUMENTS:
    curve(string) - curve

    RETURNS:
    distances(list) - [xLength,yLength,zLength]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    def duplicateShape(shape):
        parentObj = mc.listRelatives(shape, p=True, fullPath=True)
        shapes = mc.listRelatives(parentObj, shapes=True, fullPath=True)
        matchObjName = mc.ls(shape, long=True)
        matchIndex = shapes.index(matchObjName[0])

        dupBuffer = mc.duplicate(parentObj)
        children = mc.listRelatives(dupBuffer[0], children = True, fullPath =True)
        if len(children) > 0:
            for c in children:
                if search.returnObjectType(c) != 'shape':
                    mc.delete(c)

        dupShapes = mc.listRelatives(dupBuffer[0], shapes=True, fullPath=True)
        for shape in dupShapes:
            if dupShapes.index(shape) != matchIndex:
                mc.delete(shape)
                return dupBuffer[0]


    boundingBoxSize = returnBoundingBoxSize(curve)
    if mayaVersion <=2010:
        return boundingBoxSize
    else:
        distanceToMove = max(boundingBoxSize)
        positions = []
        isShape = False
        if search.returnObjectType(curve) == 'shape':
            dupCurve = duplicateShape(curve)
            curve = dupCurve
            isShape = True

        loc = rigging.locMeObjectStandAlone(curve)
        locGroup = rigging.groupMeObject(loc,False)
        loc = rigging.doParentReturnName(loc,locGroup)
        directions = ['x','y','z']
        for direction in directions:
            positionsBuffer = []
            mc.setAttr((loc+'.t'+direction),distanceToMove)
            positionsBuffer.append(returnClosestUPosition(loc,curve))
            mc.setAttr((loc+'.t'+direction),-distanceToMove)
            positionsBuffer.append(returnClosestUPosition(loc,curve))
            mc.setAttr((loc+'.t'+direction),0)
            positions.append(positionsBuffer)

        distances = []
        for set in positions:
            distances.append(returnDistanceBetweenPoints(set[0],set[1]))

        if isShape == True:
            mc.delete(dupCurve)

        mc.delete(locGroup)
        return distances


def returnBoundingBoxSize (meshGrp):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object, mesh group or whatever into it,  it calculates it's bounding box info and returns list

    ARGUMENTS:
    meshGrp(string) - mesh or mesh group

    RETURNS:
    returnList(list) - [xLength,yLength,zLength]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    returnList = []
    boundingBoxSize = []
    box = mc.exactWorldBoundingBox (meshGrp)
    rawBuffer =  [(box[3] - box[0]), (box[4] - box[1]), (box[5] - box[2])]
    for number in rawBuffer:
        if mayaVersion >= 2010:
            returnList.append(float('{0:f}'.format(number)))
        else:
            returnList.append(float(number))
    return returnList

def returnCenterPivotPosition (meshGrp):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass an object, mesh group or whatever into it,  it calculates it's bounding box pivot

    ARGUMENTS:
    meshGrp(string) - mesh or mesh group

    RETURNS:
    returnList(list) - [xLength,yLength,zLength]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    returnList = []
    boundingBoxSize = []
    box = mc.exactWorldBoundingBox (meshGrp)
    rawBuffer =  [((box[0] + box[3])/2),((box[4] + box[1])/2), ((box[5] + box[2])/2)]
    for number in rawBuffer:
        if mayaVersion >= 2010:
            returnList.append(float('{0:f}'.format(number)))
        else:
            returnList.append(float(number))
    return returnList

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnObjectSize(obj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Semi intelligent object sizer. Currently works for verts, edges,
    faces, poly meshes, nurbs surfaces, nurbs curve

    ARGUMENTS:
    obj(string) - mesh or mesh group

    RETURNS:
    size(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    objType = search.returnObjectType(obj)
    print objType

    #>>> Poly
    if objType == 'mesh':
        size =  mc.polyEvaluate(obj,worldArea = True)

        print ('%s%f' %('mesh area is ',size))
        return size

    elif objType == 'polyVertex':
        meshArea = mc.polyEvaluate(obj,worldArea = True)
        splitBuffer = obj.split('.')
        vertices = mc.ls ([splitBuffer[0]+'.vtx[*]'],flatten=True)
        size = meshArea/len(vertices)

        print ('%s%f' %('Average mesh area per vert is  ',size))
        return size

    elif objType == 'polyEdge':
        size = returnEdgeLength(obj)

        print ('%s%f' %('The Edge length is ',size))
        return size

    elif objType == 'polyFace':
        size =  returnFaceArea(obj)

        print ('%s%f' %('face area is ',size))
        return size

    #>>> Nurbs
    elif objType == 'nurbsSurface':
        boundingBoxSize = returnBoundingBoxSize(obj)
        size = cgmMath.multiplyList(boundingBoxSize)

        print ('%s%f' %('Bounding box volume is ',size))
        return size

    elif objType == 'nurbsCurve':
        size =  returnCurveLength(obj)

        print ('%s%f' %('Curve length is ',size))
        return size
    else:
        print ("Don't know how to handle that one")
        return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnEdgeLength(polyEdge):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns an edge length

    ARGUMENTS:
    polyEdge(string) - edge of a poly

    RETURNS:
    length(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    edgeVerts = search.returnVertsFromEdge(polyEdge)
    lengthList =  returnDistanceBetweenObjectsList(edgeVerts)
    return sum(lengthList)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnFaceArea(polyFace):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns area of a face

    ARGUMENTS:
    polyFace(string) - face of a poly

    RETURNS:
    length(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    faceVerts = search.returnVertsFromFace(polyFace)
    posList = []
    for vtx in faceVerts:
        posList.append( mc.pointPosition(vtx,w=True) )

    polyBuffer = geo.createPolyFromPosList(posList)

    polyArea = mc.polyEvaluate(polyBuffer,worldArea = True)
    mc.delete(polyBuffer)

    return polyArea

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnCurveLength(curve):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the length of a curve, and a sum of the shapes lenghts of a compound curve

    ARGUMENTS:
    curve(string)

    RETURNS:
    length(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    shapes = mc.listRelatives(curve,shapes=True)

    shapeLengths = []

    for shape in shapes:
        print shape
        infoNode = createCurveLengthNode(shape)
        shapeLengths.append(mc.getAttr(infoNode+'.arcLength'))
        print shapeLengths
        mc.delete(infoNode)
    return sum(shapeLengths)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Proximity Tools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnDirectionSortedDict(targetObject,objectList):
    directions = ['x','y','z','-x','-y','-z']
    returnDict = {}
    for direction in directions:
        directionObjsBuffer = []
        for obj in objectList:
            if returnLinearDirection(targetObject,obj) == direction:
                directionObjsBuffer.append(obj)
        if len(directionObjsBuffer) != 0:
            returnDict[direction] = directionObjsBuffer
    return returnDict



def returnClosestObjectsFromAim(targetObject,objectList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns normalized list of values derived from up and down stream objects from
    a target object

    ARGUMENTS:
    targetObject(string) - object you want to check distance to
    objectList(list) - list of objects to pick from
    maxReturn(int) - maximum number of return values

    RETURNS:
    returnDict(dict) - {'up':[obj1,ob2], 'down':[obj3,obj4]}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """first get the clostest object"""
    returnDict = {}

    closestObj = returnClosestObject(targetObject, objectList)

    """ distance """
    distance = returnDistanceBetweenObjects(targetObject,closestObj)

    """ get our objects in direction dictionary format"""
    directionDict = returnDirectionSortedDict(targetObject,objectList)

    #>>> directional stuff
    """ first determine the aim and get it in usable format"""
    localAim = returnLocalAimDirection(targetObject,closestObj)
    directions = ['x','-x','y','-y','z','-z']
    oppositeDirections = ['-x','x','-y','y','-z','z']
    returnDirections = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]
    upIndex = returnDirections.index(localAim)
    upAim = directions[upIndex]
    downAim = oppositeDirections[upIndex]

    upObjects = directionDict.get(upAim)
    dnObjects = directionDict.get(downAim)

    """ sort by distance """
    if upObjects != None:
        upObjects = returnDistanceSortedList(targetObject,upObjects)
        returnDict['up'] = upObjects
    if dnObjects != None:
        dnObjects = returnDistanceSortedList(targetObject,dnObjects)
        returnDict['down'] = dnObjects


    return returnDict

    #>>> distances



def returnDistanceSortedList(targetObject, objectList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a list of objects in order of closeness to a target object

    ARGUMENTS:
    targetObject(string) - object you want to check distance to
    objectList(list) - list of objects to pick from

    RETURNS:
    sortedList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = copy.copy(objectList)
    sortedList = []
    while len(bufferList) > 0:
        currentClosest = returnClosestObject(targetObject, bufferList)
        sortedList.append(currentClosest)
        bufferList.remove(currentClosest)
    return sortedList

def returnPositionDataDistanceSortedList(startPosition, posList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a list of objects in order of closeness to a target object

    ARGUMENTS:
    targetObject(string) - object you want to check distance to
    objectList(list) - list of objects to pick from

    RETURNS:
    sortedList(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    bufferList = copy.copy(posList)
    sortedList = []
    while len(bufferList) > 0:
        currentClosest = returnClosestPoint(startPosition, bufferList)
        sortedList.append(currentClosest)
        bufferList.remove(currentClosest)
    return sortedList

def returnClosestVert(targetVert, vertList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Get the closest object from an list to a target object

    ARGUMENTS:
    targetObject(string) - object you want to check distance to
    objectList(list) - list of objects to pick from

    RETURNS:
    closestObject(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    distanceList = []
    for vert in vertList:
        distance = returnDistanceBetweenObjects (targetObject, obj)
        distanceList.append (distance)
    return objectList[(distanceList.index ((min(distanceList))))]

def returnClosestObject(targetObject, objectList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Get the closest object from an list to a target object

    ARGUMENTS:
    targetObject(string) - object you want to check distance to
    objectList(list) - list of objects to pick from

    RETURNS:
    closestObject(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    distanceList = []
    for obj in objectList:
        distance = returnDistanceBetweenObjects (targetObject, obj)
        distanceList.append (distance)
    return objectList[(distanceList.index ((min(distanceList))))]

def returnClosestPoint(startPoint, posList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Get closest point from a start point

    ARGUMENTS:
    startPoint(double3) - 
    posList(double3List) - list of positions to pick from

    RETURNS:
    closestPosition(double3)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    distanceList = []
    for pos in posList:
        distanceList.append (returnDistanceBetweenPoints(startPoint, pos))
    return posList[(distanceList.index ((min(distanceList))))]
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnClosestCV (targetObject, surface):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Get the closest cv on a surface to a target object

    ARGUMENTS:
    targetObject(string)
    surface(string) - nurbs surface

    RETURNS:
    cv(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    distanceList = []
    cvList = (mc.ls ([surface+'.cv[*][*]'],flatten=True))
    targetObjectPos = returnWorldSpacePosition (targetObject)
    for cv in cvList:
        cvPos = mc.pointPosition (cv,world=True)
        distance = returnDistanceBetweenPoints (cvPos, targetObjectPos)
        distanceList.append (distance)
    return cvList[(distanceList.index ((min(distanceList))))]
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnClosestCVFromList (targetObject, cvList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Get the closest cv on a surface to a target object

    ARGUMENTS:
    targetObject(string)
    surface(string) - nurbs surface

    RETURNS:
    cv(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    distanceList = []
    targetObjectPos = returnWorldSpacePosition (targetObject)
    for cv in cvList:
        cvPos = mc.pointPosition (cv,world=True)
        distance = returnDistanceBetweenPoints (cvPos, targetObjectPos)
        distanceList.append (distance)
    return cvList[(distanceList.index ((min(distanceList))))]
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnClosestObjToCV (cv, objectList):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Get the closest object to a cv

    ARGUMENTS:
    cv(list)
    objectList(list)

    RETURNS:
    closestObj(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    distanceList = []
    cvPos = mc.pointPosition (cv,world=True)
    wantedName = (cv + 'loc')
    actualName = mc.spaceLocator (n= wantedName)
    mc.move (cvPos[0],cvPos[1],cvPos[2], [actualName[0]])
    closestObj = returnClosestObject (actualName[0], objectList)
    mc.delete (actualName[0])
    return closestObj
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def returnClosestUV (targetObject,surface):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass target object and surface into it and return the closest UV coordinates

    ARGUMENTS:
    targetObject(string)
    surface(string)

    RETURNS:
    UV(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ pass target object and surface into it and return the closest UV coordinates"""
    UVs = []
    """ make the node """
    tmpNode = mc.createNode ('closestPointOnSurface')
    """ to account for target objects in heirarchies """
    tmpObj = rigging.locMeObjectStandAlone(targetObject)
    mc.connectAttr ((tmpObj+'.translate'),(tmpNode+'.inPosition'))
    mc.connectAttr ((surface+'.worldSpace'),(tmpNode+'.inputSurface'))
    UVs.append (mc.getAttr (tmpNode+'.u'))
    UVs.append (mc.getAttr (tmpNode+'.v'))
    mc.delete (tmpNode)
    mc.delete (tmpObj)
    return UVs
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def returnClosestUPosition (targetObject,curve):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass target object and curve into it and return the closest U position

    ARGUMENTS:
    targetObject(string)
    surface(string)

    RETURNS:
    position(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ pass target object and surface into it and return the closest UV coordinates"""
    position = []
    if search.returnObjectType(curve) == 'shape':
        shapes = []
        shapes.append(curve)
    else:
        shapes = mc.listRelatives (curve, shapes=True)
    """ to account for target objects in heirarchies """
    tmpObj = rigging.locMeObjectStandAlone(targetObject)
    positions = []
    for shape in shapes:
        tmpNode = mc.createNode ('nearestPointOnCurve')
        position = []
        distances = []
        mc.connectAttr ((tmpObj+'.translate'),(tmpNode+'.inPosition'))
        mc.connectAttr ((shape+'.worldSpace'),(tmpNode+'.inputCurve'))
        position.append (mc.getAttr (tmpNode+'.positionX'))
        position.append (mc.getAttr (tmpNode+'.positionY'))
        position.append (mc.getAttr (tmpNode+'.positionZ'))
        positions.append(position)
        mc.delete (tmpNode)

    distances = []
    """ measure distances """
    locPos = returnWorldSpacePosition (tmpObj)
    mc.delete (tmpObj)
    for position in positions:
        distances.append(returnDistanceBetweenPoints(locPos,position))

    """ find the closest to our object """
    closestPosition = min(distances)
    matchIndex = distances.index(closestPosition)

    return positions[matchIndex]


def returnClosestPointOnMeshInfoFromPos(pos, mesh):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns pertinent info of the closest point of a mesh to a position in space -
    position, normal, parameterU,parameterV,closestFaceIndex,closestVertexIndex

    ARGUMENTS:
    pos(string)
    mesh(string)

    RETURNS:
    closestPointInfo(dict)
    Keys:
    position
    normal
    parameterU
    parameterV
    closestFaceIndex
    closestVertexIndex
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """

    """ make the closest point node """
    closestPointNode = mc.createNode ('closestPointOnMesh')
    controlSurface = mc.listRelatives(mesh,shapes=True)

    """ to account for target objects in heirarchies """
    locBuffer = mc.spaceLocator()
    mc.move (pos[0],pos[1],pos[2], locBuffer[0])

    attributes.doConnectAttr((locBuffer[0]+'.translate'),(closestPointNode+'.inPosition'))
    attributes.doConnectAttr((controlSurface[0]+'.worldMesh'),(closestPointNode+'.inMesh'))
    attributes.doConnectAttr((locBuffer[0]+'.matrix'),(closestPointNode+'.inputMatrix'))
 
    pointInfo = {}
    pointInfo['position']=attributes.doGetAttr(closestPointNode,'position')
    pointInfo['normal']=attributes.doGetAttr(closestPointNode,'normal')
    pointInfo['parameterU']=mc.getAttr(closestPointNode+'.parameterU')
    pointInfo['parameterV']=mc.getAttr(closestPointNode+'.parameterV')
    pointInfo['closestFaceIndex']=mc.getAttr(closestPointNode+'.closestFaceIndex')
    pointInfo['closestVertexIndex']=mc.getAttr(closestPointNode+'.closestVertexIndex')

    mc.delete(closestPointNode)
    mc.delete(locBuffer[0])
    return pointInfo

def returnClosestPointOnMeshInfo(targetObj, mesh):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns pertinent info of the closest point of a mesh to a target object -
    position, normal, parameterU,parameterV,closestFaceIndex,closestVertexIndex

    ARGUMENTS:
    targetObj(string)
    mesh(string)

    RETURNS:
    closestPointInfo(dict)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """

    """ make the closest point node """
    closestPointNode = mc.createNode ('closestPointOnMesh')
    controlSurface = mc.listRelatives(mesh,shapes=True)

    """ to account for target objects in heirarchies """
    attributes.doConnectAttr((targetObj+'.translate'),(closestPointNode+'.inPosition'))
    attributes.doConnectAttr((controlSurface[0]+'.worldMesh'),(closestPointNode+'.inMesh'))
    attributes.doConnectAttr((controlSurface[0]+'.matrix'),(closestPointNode+'.inputMatrix'))

    pointInfo = {}
    pointInfo['position']=attributes.doGetAttr(closestPointNode,'position')
    pointInfo['normal']=attributes.doGetAttr(closestPointNode,'normal')
    pointInfo['parameterU']=mc.getAttr(closestPointNode+'.parameterU')
    pointInfo['parameterV']=mc.getAttr(closestPointNode+'.parameterV')
    pointInfo['closestFaceIndex']=mc.getAttr(closestPointNode+'.closestFaceIndex')
    pointInfo['closestVertexIndex']=mc.getAttr(closestPointNode+'.closestVertexIndex')

    mc.delete(closestPointNode)
    return pointInfo


def returnClosestUVToPos(mesh, pos):
    """   
    Return the closest point on a mesh to a point in space
    
    Arguments
    mesh(string) -- currently poly surface only
    pos(double3) -- point in world space
    
    returns(double2) -- uv coordinate on mesh
    """
    buffer = []
    for p in pos:
	buffer.append(returnWorldSpaceFromMayaSpace(p))
    pos = buffer
    
    #Create an empty selection list.
    selectionList = om.MSelectionList()

    #Put the mesh's name on the selection list.
    selectionList.add(mesh)

    #Create an empty MDagPath object.
    meshPath = om.MDagPath()

    #Get the first item on the selection list (which will be our mesh)
    #as an MDagPath.
    selectionList.getDagPath(0, meshPath)

    #Create an MFnMesh functionset to operate on the node pointed to by
    #the dag path.
    meshFn = om.MFnMesh(meshPath)
    
    #Thank you Mattias Bergbom, http://bergbom.blogspot.com/2009/01/float2-and-float3-in-maya-python-api.html
    floatPoint = om.MFloatPoint(pos[0], pos[1], pos[2])
    refPoint = om.MPoint(floatPoint) # Thank you Capper on Tech-artists.org          
    pArray = [0.0,0.0]
    x1 = om.MScriptUtil()
    x1.createFromList( pArray, 2 )
    uvPoint = x1.asFloat2Ptr()
    uvSet = None
    closestPolygon=None
    uvReturn = meshFn.getUVAtPoint(refPoint,uvPoint,om.MSpace.kWorld)
    
    uValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0) or False
    vValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1) or False
    
    if uValue and vValue:
        return [uValue,vValue]
    return False
    










