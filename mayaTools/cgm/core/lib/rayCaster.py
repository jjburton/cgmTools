#=================================================================================================================================================
#=================================================================================================================================================
#	DraggerContextFactory - a part of cgmTools
#=================================================================================================================================================
#=================================================================================================================================================
#
# DESCRIPTION:
#	Classes and functions for DraggerContext
#
#
# AUTHOR:
# 	Josh Burton
#	http://www.cgmonks.com
# 	Copyright 2012 CG Monks - All Rights Reserved.
#
# ACKNOWLEDGEMENTS:
#   Morgan Loomis
# 	http://forums.cgsociety.org/archive/index.php/t-983068.html
# 	http://forums.cgsociety.org/archive/index.php/t-1002257.html
# 	https://groups.google.com/forum/?fromgroups#!topic/python_inside_maya/n6aJq27fg0o%5B1-25%5D
#======================================================================================================================
import maya.cmds as mc
import copy
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as om
from zooPyMaya import apiExtensions

from cgm.lib import (locators,
                     dictionary,
                     cgmMath,
                     lists,
                     geo,
                     distance)
import os

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def findMeshIntersection(mesh, raySource, rayDir, maxDistance = 1000):
    """
    Thanks to Deane @ https://groups.google.com/forum/?fromgroups#!topic/python_inside_maya/n6aJq27fg0o%5B1-25%5D

    Return the closest point on a surface from a raySource and rayDir

    Arguments
    mesh(string) -- currently poly surface only
    raySource(double3) -- point in world space
    rayDir(double3) -- world space vector

    returns hitpoint(double3)
    """    
    try:
        _str_funcName = 'findMeshIntersection'
        log.info(">>> %s >> "%_str_funcName + "="*75)           
        if len(mc.ls(mesh))>1:
            raise StandardError,"findMeshIntersection>>> More than one mesh named: %s"%mesh    
    
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
    
        #Convert the 'raySource' parameter into an MFloatPoint.
        raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])
    
        #Convert the 'rayDir' parameter into an MVector.`
        rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])
    
        #Create an empty MFloatPoint to receive the hit point from the call.
        hitPoint = om.MFloatPoint()
    
        log.debug("maxDistance: %s"%maxDistance)
    
        #Set up a variable for each remaining parameter in the
        #MFnMesh::closestIntersection call. We could have supplied these as
        #literal values in the call, but this makes the example more readable.
        sortIds = False
        maxDist = maxDistance#om.MDistance.internalToUI(1000000)# This needs work    
        #maxDist = om.MDistance.internalToUI(maxDistance) # This needs work
        bothDirections = False
        noFaceIds = None
        noTriangleIds = None
        noAccelerator = None
        noHitParam = None
        noHitFace = None
        noHitTriangle = None
        noHitBary1 = None
        noHitBary2 = None
    
        #Get the closest intersection.
        gotHit = meshFn.closestIntersection(
            raySource, rayDirection,
            noFaceIds, noTriangleIds,
            sortIds, om.MSpace.kWorld, maxDist, bothDirections,
            noAccelerator,
            hitPoint,
            noHitParam, noHitFace, noHitTriangle, noHitBary1, noHitBary2)
    
        #Return the intersection as a Pthon list.
        if gotHit:
            #Thank you Mattias Bergbom, http://bergbom.blogspot.com/2009/01/float2-and-float3-in-maya-python-api.html
            hitMPoint = om.MPoint(hitPoint) # Thank you Capper on Tech-artists.org          
            pArray = [0.0,0.0]
            x1 = om.MScriptUtil()
            x1.createFromList( pArray, 2 )
            uvPoint = x1.asFloat2Ptr()
            uvSet = None
            closestPolygon=None
            uvReturn = meshFn.getUVAtPoint(hitMPoint,uvPoint,om.MSpace.kWorld)
    
            uValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0) or False
            vValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1) or False
            log.debug("Hit! [%s,%s,%s]"%(hitPoint.x, hitPoint.y, hitPoint.z))
            if uValue and vValue:
                return {'hit':[hitPoint.x, hitPoint.y, hitPoint.z],'source':[raySource.x,raySource.y,raySource.z],'uv':[uValue,vValue]}                
            else:
                return {'hit':[hitPoint.x, hitPoint.y, hitPoint.z],'source':[raySource.x,raySource.y,raySource.z],'uv':False}
        else:
            return None    
    except StandardError,error:
        log.error(">>> %s >> mesh: %s | raysource: %s | rayDir %s | error: %s"%(_str_funcName,mesh,raySource,rayDir,error))
        return None
    
def findMeshIntersections(mesh, raySource, rayDir, maxDistance = 1000):
    """
    Thanks to Deane @ https://groups.google.com/forum/?fromgroups#!topic/python_inside_maya/n6aJq27fg0o%5B1-25%5D

    Return the pierced points on a surface from a raySource and rayDir

    Arguments
    mesh(string) -- currently poly surface only
    raySource(double3) -- point in world space
    rayDir(double3) -- world space vector

    returns hitpoints(list) -- [pos1,pos2...]
    """    
    try:
        _str_funcName = 'findMeshIntersections'
        log.info(">>> %s >> "%_str_funcName + "="*75)       
        if len(mc.ls(mesh))>1:
            raise StandardError,"findMeshIntersections>>> More than one mesh named: %s"%mesh       
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
    
        #Convert the 'raySource' parameter into an MFloatPoint.
        raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])
    
        #Convert the 'rayDir' parameter into an MVector.`
        rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])
    
        #Create an empty MFloatPoint to receive the hit point from the call.
        hitPoints = om.MFloatPointArray()
    
        #Set up a variable for each remaining parameter in the
        #MFnMesh::allIntersections call. We could have supplied these as
        #literal values in the call, but this makes the example more readable.
        sortIds = False
        maxDist = maxDistance#om.MDistance.internalToUI(1000000)# This needs work    
        bothDirections = False
        noFaceIds = None
        noTriangleIds = None
        noHitParam = None
        noSortHits = False
        noHitFace = None
        noHitTriangle = None
        noHitBary1 = None
        noHitBary2 = None
        tolerance = 0
        noAccelerator = None
    
        #Get the closest intersection.
        gotHit = meshFn.allIntersections(
            raySource,
            rayDirection,
            noFaceIds,
            noTriangleIds,
            sortIds,
            om.MSpace.kWorld,
            maxDist,
            bothDirections,
            noAccelerator,
            noSortHits,
            hitPoints, noHitParam, noHitFace, noHitTriangle, noHitBary1, noHitBary2,tolerance)
    
        #Return the intersection as a Pthon list.
        if gotHit:        
            returnDict = {}
            hitList = []
            uvList = []
            for i in range( hitPoints.length() ):
                hitList.append( [hitPoints[i].x, hitPoints[i].y,hitPoints[i].z])
    
                #Thank you Mattias Bergbom, http://bergbom.blogspot.com/2009/01/float2-and-float3-in-maya-python-api.html
                hitMPoint = om.MPoint(hitPoints[i]) # Thank you Capper on Tech-artists.org          
                pArray = [0.0,0.0]
                x1 = om.MScriptUtil()
                x1.createFromList( pArray, 2 )
                uvPoint = x1.asFloat2Ptr()
                uvSet = None
                closestPolygon=None
                uvReturn = meshFn.getUVAtPoint(hitMPoint,uvPoint,om.MSpace.kWorld)
    
                uValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0) or False
                vValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1) or False
                uvList.append([uValue,vValue])
    
            returnDict = {'hits':hitList,'source':[raySource.x,raySource.y,raySource.z],'uvs':uvList}
    
            return returnDict
        else:
            return None   
    except StandardError,error:
        log.error(">>> %s >> mesh: %s | raysource: %s | rayDir %s | error: %s"%(_str_funcName,mesh,raySource,rayDir,error))
        return None
    
def findMeshIntersectionFromObjectAxis(mesh, obj, axis = 'z+', vector = False, maxDistance = 1000, singleReturn = True):
    """
    Find mesh intersections for an object's axis
    """
    try:
        _str_funcName = 'findMeshIntersectionFromObjectAxis'
        log.info(">>> %s >> "%_str_funcName + "="*75)     
        if len(mc.ls(mesh))>1:
            raise StandardError,"findMeshIntersectionFromObjectAxis>>> More than one mesh named: %s"%mesh    
        if not vector or type(vector) not in [list,tuple]:
            d_matrixVectorIndices = {'x':[0,1,2],
                                     'y': [4,5,6],
                                     'z' : [8,9,10]}
            matrix = mc.xform(obj, q=True,  matrix=True, worldSpace=True)
    
            #>>> Figure out our vector
            if axis not in dictionary.stringToVectorDict.keys():
                log.error("findMeshIntersectionFromObjectAxis axis arg not valid: '%s'"%axis)
                return False
            if list(axis)[0] not in d_matrixVectorIndices.keys():
                log.error("findMeshIntersectionFromObjectAxis axis arg not in d_matrixVectorIndices: '%s'"%axis)
                return False  
            vector = [matrix[i] for i in d_matrixVectorIndices.get(list(axis)[0])]
            if list(axis)[1] == '-':
                for i,v in enumerate(vector):
                    vector[i]=-v
        if singleReturn:
            return findMeshIntersection(mesh, distance.returnWorldSpacePosition(obj), rayDir=vector, maxDistance = maxDistance)
        else:
            return findMeshIntersections(mesh, distance.returnWorldSpacePosition(obj), rayDir=vector, maxDistance = maxDistance)
    except StandardError,error:
        log.error(">>> %s >> mesh: %s | obj: %s | axis %s | vector: %s | error: %s"%(_str_funcName,mesh,obj,axis,vector,error))
        return None
    
def findMeshMidPointFromObject(mesh,obj,axisToCheck = ['x','z'],
                               vector = False, maxDistance = 1000, maxIterations = 10,**kws):
    try:#findMeshMidPointFromObject
        _str_funcName = 'findMeshMidPointFromObject'
        log.info(">>> %s >> "%_str_funcName + "="*75)             
        if len(mc.ls(mesh))>1:
            raise StandardError,"findMeshMidPointFromObject>>> More than one mesh named: %s"%mesh      
        if type(axisToCheck) not in [list,tuple]:axisToCheck=[axisToCheck]
        axis = ['x','y','z']
        for a in axisToCheck:
            if a not in axis:
                raise StandardError,"findMeshMidPointFromObject>>> Not a valid axis : %s not in ['x','y','z']"%axisToCheck
        l_lastPos = []
        loc = locators.locMeObjectStandAlone(obj)
        for i in range(maxIterations):
            l_positions = []
            for a in axisToCheck:
                log.debug("firing: %s"%a)
                d_posReturn = findMeshIntersectionFromObjectAxis(mesh, loc, axis = '%s+'%a,vector=vector,maxDistance = maxDistance)
                d_negReturn = findMeshIntersectionFromObjectAxis(mesh, loc, axis = '%s-'%a,vector=vector,maxDistance = maxDistance)

                if 'hit' in d_posReturn.keys() and d_negReturn.keys():
                    l_pos = [d_posReturn.get('hit'),d_negReturn.get('hit')]
                    pos = distance.returnAveragePointPosition(l_pos)          
                    l_positions.append(pos)
            if len(l_positions) == 1:
                l_pos =  l_positions[0]
            else:
                l_pos =  distance.returnAveragePointPosition(l_positions)
            if l_lastPos:dif = cgmMath.mag( cgmMath.list_subtract(l_pos,l_lastPos) )
            else:dif = 'No last'
            log.debug("findMeshMidPointFromObject>>> Step : %s | dif: %s | last: %s | pos: %s "%(i,dif,l_lastPos,l_pos)) 					
            if l_lastPos and cgmMath.isVectorEquivalent(l_lastPos,l_pos,2):
                log.debug("findMeshMidPointFromObject>>> Match found step: %s"%(i))
                mc.delete(loc)
                return l_pos
            mc.move(l_pos[0],l_pos[1],l_pos[2],loc,ws=True)
            l_lastPos = l_pos#If we get to here, add the current
        mc.delete(loc)    
        return l_pos
    except StandardError,error:
        for kw in [mesh,obj,axisToCheck,vector,maxDistance,maxIterations]:
            log.debug("%s"%kw)        
        raise StandardError, "%s >> error: %s"%(_str_funcName,error)

def findFurthestPointInRangeFromObject(mesh,obj,axis = 'z+', pierceDepth = 4,
                                       vector = False, maxDistance = 1000):
    """ Find the furthest point in range on an axis. Useful for getting to the outershell of a mesh """
    try:
        _str_funcName = 'findFurthestPointInRangeFromObject'
        log.info(">>> %s >> "%_str_funcName + "="*75)             
        if len(mc.ls(mesh))>1:
            raise StandardError,"findFurthestPointInRangeFromObject>>> More than one mesh named: %s"%mesh      
        #>>>First cast to get our initial range
        d_firstcast = findMeshIntersectionFromObjectAxis(mesh, obj, axis = axis, vector=vector, maxDistance = maxDistance)
        if not d_firstcast.get('hit'):
            raise StandardError,"findFurthestPointInRangeFromObject>>> first cast failed to hit"
    
        baseDistance = distance.returnDistanceBetweenPoints(distance.returnWorldSpacePosition(obj),d_firstcast['hit'])
        log.debug("findFurthestPointInRangeFromObject>>>baseDistance: %s"%baseDistance)
        castDistance = baseDistance + pierceDepth
        log.debug("findFurthestPointInRangeFromObject>>>castDistance: %s"%castDistance)
    
        l_positions = []
    
        d_castReturn = findMeshIntersectionFromObjectAxis(mesh, obj, axis=axis, maxDistance = castDistance, singleReturn=False) or {}
        log.debug("2nd castReturn: %s"%d_castReturn)
        if d_castReturn.get('hits'):
            closestPoint = distance.returnFurthestPoint(distance.returnWorldSpacePosition(obj),d_castReturn.get('hits')) or False
            d_castReturn['hit'] = closestPoint
        return d_castReturn
    except StandardError,error:
        for kw in [mesh,obj,axis,pierceDepth,vector,maxDistance]:
            log.debug("%s"%kw)
        raise StandardError, "%s >> error: %s"%(_str_funcName,error)



