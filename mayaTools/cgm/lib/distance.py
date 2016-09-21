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
import math
import maya.cmds as mc
import maya.OpenMaya as om

import maya.mel as mel
import copy

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core import cgm_General as cgmGeneral
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
def returnBoundingBoxSizeToAverage (meshGrp,objOnly = False):
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
    boundingBoxSizeList = returnBoundingBoxSize (meshGrp,objOnly)
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
    if 'vtx[' in obj or 'ep[' in obj or 'cv[' in obj or 'u[' in obj:
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
    #distObj1 = mc.rename (loc1Buffer, (obj1+'_distLoc') )
    #distObj2 = mc.rename (loc2Buffer, (obj2+'_distLoc') )

    return distanceObj

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


def returnBoundingBoxSize (meshGrp,objOnly = False):
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
    if type(meshGrp) is list:
        for o in meshGrp: assert mc.objExists(o),"returnBoundingBoxSize: meshGrp object doesn't exist: '%s'"%o
    else:
        assert mc.objExists(meshGrp),"returnBoundingBoxSize: meshGrp doesn't exist: '%s'"%meshGrp
    returnList = []
    boundingBoxSize = []

    if objOnly:
        buffer= mc.duplicate(meshGrp,returnRootsOnly=True)
        l_relatives = mc.listRelatives(buffer[0],allDescendents = True,fullPath = True,type = 'transform')
        if l_relatives:mc.delete(l_relatives)  
        box = mc.exactWorldBoundingBox (buffer[0]) 
        if buffer:mc.delete(buffer)

    #box = mc.exactWorldBoundingBox (meshGrp)
    else:
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
def returnObjectSize(obj,debugReport = False):
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

    #>>> Poly
    if objType == 'mesh':
        size =  mc.polyEvaluate(obj,worldArea = True)

        if debugReport: print ('%s%f' %('mesh area is ',size))
        return size

    elif objType == 'polyVertex':
        meshArea = mc.polyEvaluate(obj,worldArea = True)
        splitBuffer = obj.split('.')
        vertices = mc.ls ([splitBuffer[0]+'.vtx[*]'],flatten=True)
        size = meshArea/len(vertices)

        if debugReport: print ('%s%f' %('Average mesh area per vert is  ',size))
        return size

    elif objType == 'polyEdge':
        size = returnEdgeLength(obj)

        if debugReport: print ('%s%f' %('The Edge length is ',size))
        return size

    elif objType == 'polyFace':
        size =  returnFaceArea(obj)

        if debugReport: print ('%s%f' %('face area is ',size))
        return size

    #>>> Nurbs
    elif objType == 'nurbsSurface':
        boundingBoxSize = returnBoundingBoxSize(obj)
        size = cgmMath.multiplyList(boundingBoxSize)

        if debugReport: print ('%s%f' %('Bounding box volume is ',size))
        return size

    elif objType == 'nurbsCurve':
        size =  returnCurveLength(obj)

        if debugReport: print ('%s%f' %('Curve length is ',size))
        return size
    else:
        if debugReport: print ("Don't know how to handle that one")
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
    """_split = polyface.split('.')
    mesh =_split[0]
    _split = _split.split('f[')[-1]
    _split = _split.split(']')[0]
    poly = _split
    face = polyface.split
    log.info(poly)
    log.info(face)"""
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
    shapes = mc.listRelatives(curve,shapes=True,path = 1)

    shapeLengths = []

    for shape in shapes:
        infoNode = createCurveLengthNode(shape)
        shapeLengths.append(mc.getAttr(infoNode+'.arcLength'))
        mc.delete(infoNode)
    return sum(shapeLengths)

def returnCurveDiameter(curve):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Assuming a given curve is a circle, return it's diameter. This is mainly to account for hidden objects with which
    bounding box size fails to handle properly.

    cir = pi * d

    ARGUMENTS:
    curve(string)

    RETURNS:
    diamter(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    return returnCurveLength(curve) / math.pi


def returnMidU(curve):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the mid u point of a curve

    ARGUMENTS:
    curve(string)

    RETURNS:
    uPosition(float)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    uReturn = mc.ls('%s.u[*]'%curve,flatten = True) or []
    if not uReturn:
        raise StandardError, "returnMidU>>> No u return "
    if len(uReturn)>1:
        raise StandardError, "returnMidU>>> Can only currently do single curves: %s"%uReturn
    if ':' not in uReturn[0]:
        raise StandardError, "returnMidU>>> No ':' in return: %s"%uReturn
    bracketEnd_split = uReturn[0].split(']')[0]
    bracketStart_split = bracketEnd_split.split('[')[1]
    log.debug("bracket: %s"%bracketStart_split)
    colonSplit = bracketStart_split.split(':')
    l_floats = [float(i) for i in colonSplit]
    log.debug("l_floats: %s"%l_floats)
    midU = (l_floats[1]-l_floats[0]) /2
    return "%s.u[%s]"%(curve,midU)



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

def returnLinearDirection(rootObj,aimObj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a linear direction

    ARGUMENTS:
    rootObj(string)
    aimObj(string)

    RETURNS:
    direction(string) - 'x,y,z,-x,-y,-z'
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    #make locators in case we're using something like joints
    axis = {0:'x',1:'y',2:'z'}
    rootPos = mc.xform (rootObj,q=True, ws=True, rp=True)
    aimPos = mc.xform (aimObj,q=True, ws=True, rp=True)

    rawDifferenceList = [(aimPos[0]-rootPos[0]),(aimPos[1]-rootPos[1]),(aimPos[2]-rootPos[2])]
    absDifferenceList = [abs(rawDifferenceList[0]),abs(rawDifferenceList[1]),abs(rawDifferenceList[2])]

    biggestNumberIndex = absDifferenceList.index(max(absDifferenceList))
    direction = axis.get(biggestNumberIndex)
    if rawDifferenceList[biggestNumberIndex] < 0:
        return ('%s%s' %('-',direction))
    else:
        return (direction)

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

def returnLocalAimDirection(rootObj,aimObj):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns a local aim direction

    ARGUMENTS:
    rootObj(string)
    aimObj(string)

    RETURNS:
    direction(list) - [0,0,0]
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    directionalLocArray = []
    locGroups = []
    directions = ['+x','-x','+y','-y','+z','-z']
    returnDirections = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]
    distanceBuffer = returnDistanceBetweenObjects(rootObj,aimObj)
    rotationOrderDictionary = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}

    #distanceValues = distanceBuffer /2
    cnt = 0
    for direction in directions:
        locBuffer = mc.spaceLocator()[0]
        objTrans = mc.xform (rootObj, q=True, ws=True, sp=True)
        objRot = mc.xform (rootObj, q=True, ws=True, ro=True)
        objRoo = mc.xform (rootObj, q=True, roo=True )

        mc.move (objTrans[0],objTrans[1],objTrans[2], locBuffer)
        mc.setAttr ((locBuffer+'.rotateOrder'), rotationOrderDictionary[objRoo])
        mc.rotate (objRot[0], objRot[1], objRot[2], locBuffer, ws=True)	

        locGroups.append(rigging.groupMeObject(locBuffer))
        directionBuffer = list(direction)
        if directionBuffer[0] == '-':
            mc.setAttr((locBuffer+'.t'+directionBuffer[1]), -1)
        else:
            mc.setAttr((locBuffer+'.t'+directionBuffer[1]), 1)
        directionalLocArray.append(locBuffer)
        cnt+=1
    closestLoc = returnClosestObject(aimObj, directionalLocArray)
    matchIndex = directionalLocArray.index(closestLoc)

    for grp in locGroups:
        mc.delete(grp)

    return returnDirections[matchIndex]

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
    targetVert(string) - object you want to check distance to
    vertList(list) - list of objects to pick from

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

def returnClosestObjectFromPos(startPoint, objectList):
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
        pos = returnWorldSpacePosition(obj)
        distanceList.append (returnDistanceBetweenPoints(startPoint, pos))
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

def returnFurthestPoint(startPoint, posList):
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
    return posList[(distanceList.index ((max(distanceList))))]
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
#@cgmGeneral.Timer
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

#@cgmGeneral.TimerDebug
def returnNearestPointOnCurveInfo(targetObject,curve,deleteNode = True,cullOriginalShapes = True):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Pass target object and curve into it and return the closest U position

    ARGUMENTS:
    targetObject(string)
    surface(string)
    deleteNode(bool)

    RETURNS:
    {'position':(list),'parameter':(float},'shape':(string),'object':(string)}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    _str_funcName = 'returnNearestPointOnCurveInfo'
    log.debug(">>> %s >> "%_str_funcName + "="*75) 
    try:
        position = []
        if search.returnObjectType(curve) == 'shape':
            shapes = []
            shapes.append(curve)
        else:
            shapes = mc.listRelatives (curve, shapes=True)
        if cullOriginalShapes:
            for shape in shapes:
                if len(shape)>5 and shape[-4:] == 'Orig':
                    shapes.remove(shape)
        #to account for target objects in heirarchies """
        tmpObj = rigging.locMeObjectStandAlone(targetObject)
        l_positions = []
        l_uValues = []
        l_shapes = []
        l_objects = []
        l_nodes = []
        for shape in shapes:
            tmpNode = mc.createNode ('nearestPointOnCurve',n='%s_npoc'%shape)
            position = []
            distances = []
            mc.connectAttr ((tmpObj+'.translate'),(tmpNode+'.inPosition'))
            mc.connectAttr ((shape+'.worldSpace'),(tmpNode+'.inputCurve'))
            position.append (mc.getAttr (tmpNode+'.positionX'))
            position.append (mc.getAttr (tmpNode+'.positionY'))
            position.append (mc.getAttr (tmpNode+'.positionZ'))
            l_positions.append(position)
            l_shapes.append(shape)
            l_uValues.append(mc.getAttr (tmpNode+'.parameter'))
            l_objects.append("%s.u[%f]"%(shape,mc.getAttr (tmpNode+'.parameter')))
            l_nodes.append(tmpNode)

        distances = []
        """ measure distances """
        locPos = returnWorldSpacePosition (tmpObj)
        mc.delete (tmpObj)
        for position in l_positions:
            distances.append(returnDistanceBetweenPoints(locPos,position))

        """ find the closest to our object """
        closestPosition = min(distances)
        matchIndex = distances.index(closestPosition)
        d_return = {'position':l_positions[matchIndex],'parameter':l_uValues[matchIndex],'shape':l_shapes[matchIndex],'object':l_objects[matchIndex]}
        if not deleteNode:
            d_return['node'] = l_nodes[matchIndex]
            l_nodes.remove(l_nodes[matchIndex])	
        if l_nodes:mc.delete(l_nodes)

        return d_return
    except StandardError,error:
        raise StandardError,"%s >>> error : %s"%(_str_funcName,error)	    

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

    pointInfo = returnClosestPointOnMeshInfo(locBuffer[0],mesh)

    mc.delete(locBuffer[0],closestPointNode)
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

def returnClosestPointOnSurfaceInfo(targetObj, surface):
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
    # make the closest point node #
    closestPointNode = mc.createNode ('closestPointOnSurface')
    pointOnSurfaceNode = mc.createNode ('pointOnSurfaceInfo')
    controlSurface = mc.listRelatives(surface,shapes=True)

    #>>>Surface Info
    #Thanks - http://www.kylenikolich.com/scripting/lod/parentToSurface.mel
    f_minU = attributes.doGetAttr(controlSurface[0],'mnu')
    f_maxU = attributes.doGetAttr(controlSurface[0],'mxu')
    f_sizeU = f_maxU - f_minU
    f_minV = attributes.doGetAttr(controlSurface[0],'mnv')
    f_maxV = attributes.doGetAttr(controlSurface[0],'mxv')
    f_sizeV = f_maxV - f_minV    

    # to account for target objects in heirarchies #
    pos = returnWorldSpacePosition(targetObj)
    attributes.doSetAttr(closestPointNode,'inPositionX',pos[0])
    attributes.doSetAttr(closestPointNode,'inPositionY',pos[1])
    attributes.doSetAttr(closestPointNode,'inPositionZ',pos[2])

    attributes.doConnectAttr((controlSurface[0]+'.worldSpace'),(closestPointNode+'.inputSurface'))
    # Connect the info node to the surface #
    attributes.doConnectAttr  ((controlSurface[0]+'.local'),(pointOnSurfaceNode+'.inputSurface'))
    # Contect the pos group to the info node#
    attributes.doConnectAttr ((closestPointNode+'.parameterU'),(pointOnSurfaceNode+'.parameterU'))
    attributes.doConnectAttr  ((closestPointNode+'.parameterV'),(pointOnSurfaceNode+'.parameterV'))

    pointInfo = {}
    pointInfo['position']=attributes.doGetAttr(pointOnSurfaceNode,'position')
    pointInfo['normal']=attributes.doGetAttr(pointOnSurfaceNode,'normal')
    pointInfo['parameterU']=mc.getAttr(pointOnSurfaceNode+'.parameterU')
    pointInfo['parameterV']=mc.getAttr(pointOnSurfaceNode+'.parameterV')
    pointInfo['normalizedU'] = (pointInfo['parameterU'] + f_minU)/f_sizeU
    pointInfo['normalizedV'] =  (pointInfo['parameterV'] + f_minV)/f_sizeV  
    pointInfo['tangentU']=mc.getAttr(pointOnSurfaceNode+'.tangentU')
    pointInfo['tangentV']=mc.getAttr(pointOnSurfaceNode+'.tangentV')

    mc.delete(closestPointNode)
    mc.delete(pointOnSurfaceNode)
    log.debug(pointInfo)
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
    _type = search.returnObjectType(mesh)
    if _type == 'nurbsSurface':
        surfFn = om.MFnNurbsSurface(meshPath)	
    else:
        meshFn = om.MFnMesh(meshPath)

    #Thank you Mattias Bergbom, http://bergbom.blogspot.com/2009/01/float2-and-float3-in-maya-python-api.html

    if _type == 'nurbsSurface':
        uu = om.MScriptUtil()
        pu = uu.createFromDouble(0.0)
        pu = uu.asDoublePtr()
        uv = om.MScriptUtil()
        pv = uv.createFromDouble(0.0)
        pv = uv.asDoublePtr()    
        
        p = om.MPoint(pos[0], pos[1], pos[2])
        cpos = surfFn.closestPoint(p, pu, pv,  False, .0002, om.MSpace.kWorld)
        return returnNormalizedUV(mesh, uu.getDouble(pu), uv.getDouble(pv))['uv']
        """
        p = om.MPoint(pos[0], pos[1], pos[2])
        cpos = surfFn.closestPoint(p)
        # get U and V parameters from the point on surface
        surfFn.getParamAtPoint(cpos, pu, pv, False, om.MSpace.kWorld)
        uValue = uu.getDouble(pu)
        vValue = uv.getDouble(pv)
        #uValue = om.MScriptUtil.getFloat2ArrayItem(pu, 0, 0) or False
        #vValue = om.MScriptUtil.getFloat2ArrayItem(pv, 0, 1) or False        
        # get normal at U and V parameters
        n = surfFn.normal(uValue, vValue) """            
    else:
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
            return [uValue, vValue]
    return False

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#>>> 
#=====================================================================
def returnNormalizedUV(mesh, uValue, vValue):
    """
    uv Values from many functions need to be normalized to be correct when using those values for other functions

    The calculcaion for doing so is 
    size = maxV - minV
    sum = rawV + minV
    normalValue = sum / size

    :parameters:
    mesh(string) | Surface to normalize to
    uValue(float) | uValue to normalize 
    vValue(float) | vValue to normalize 

    :returns:
    Dict ------------------------------------------------------------------
    'uv'(double2) |  point from which we cast
    'uValue'(float) | normalized uValue
    'vValue'(float) | normalized vValue

    :raises:
    Exception | if reached

    """      
    try:
        _str_funcName = 'returnNormalizedUV'

        try:#Validation ----------------------------------------------------------------
            mesh = cgmValid.objString(mesh,'nurbsSurface', calledFrom = _str_funcName)
            if len(mc.ls(mesh))>1:
                raise StandardError,"{0}>>> More than one mesh named: {1}".format(_str_funcName,mesh)
            _str_objType = search.returnObjectType(mesh)

            l_shapes = mc.listRelatives(mesh, shapes=True)
            if len(l_shapes)>1:
                log.debug( "More than one shape found. Using 0. targetSurface : %s | shapes: %s"%(mesh,l_shapes) )
            #mi_shape = cgmMeta.validateObjArg(l_shapes[0],cgmMeta.cgmNode,noneValid=False)

            uMin = attributes.doGetAttr(l_shapes[0],'mnu')
            uMax = attributes.doGetAttr(l_shapes[0],'mxu')
            vMin = attributes.doGetAttr(l_shapes[0],'mnv')
            vMax = attributes.doGetAttr(l_shapes[0],'mxv')         
            """uMin = mi_shape.mnu
            uMax = mi_shape.mxu
            vMin = mi_shape.mnv
            vMax = mi_shape.mxv"""

        except Exception,error:raise Exception,"Validation failure | {0}".format(error) 		

        try:#Calculation ----------------------------------------------------------------
            uSize = uMax - uMin
            vSize = vMax - vMin

            uSum = uMin + uValue
            vSum = vMin + vValue

            uNormal = uSum / uSize
            vNormal = vSum / vSize
        except Exception,error:raise Exception,"Calculation |{0}".format(error) 		

        try:
            d_return = {'uv':[uNormal,vNormal],'uValue':uNormal,'vValue':vNormal}
            return d_return 
        except Exception,error:raise Exception,"Return prep |{0}".format(error) 		

    except Exception,error:
        log.error(">>> {0} >> Failure! mesh: '{1}' | uValue: {2} | vValue {3}".format(_str_funcName,mesh,uValue,vValue))
        log.error(">>> {0} >> error: {1}".format(_str_funcName,error))        
        return None