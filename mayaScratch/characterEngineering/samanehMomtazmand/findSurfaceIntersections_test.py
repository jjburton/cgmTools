from cgm.core import cgm_Meta as cgmMeta
import Red9.core.Red9_Meta as r9Meta
import maya.cmds as mc
import copy
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as om
from zooPyMaya import apiExtensions
from cgm.core import cgm_General as cgmGeneral
from cgm.lib import(locators,dictionary,cgmMath,lists,geo,distance,search)
import os
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def findSurfaceIntersections(surface, raySource):
    '''
    findSurfaceIntersections
    '''
    surfaceShape = mc.listRelatives(surface, s=1)
    centerPoint = mc.xform(surface, q=1, ws=1, t=1)    
    log.debug("raySource: %s"%raySource)
    maxDistance = 1000
    rayDir = (0.0,0.0,0.0)
    log.debug("maxDistance: %s"%maxDistance)
    
    try:
        _str_funcName = 'findSurfaceIntersections'
        log.debug(">>> %s >> "%_str_funcName + "="*75)           
        if len(mc.ls(surface))>1:
            raise StandardError,"findSurfaceIntersections>>> More than one surface named: %s"%surface
    except StandardError,error:
        log.error(">>> %s >> surface: %s | raysource: %s | rayDir %s | error:%s"%(_str_funcName,surface,raySource,rayDir,error))               

    #check the type
    objType = search.returnObjectType(surface)
    
    if objType == 'nurbsSurface':
        raySource = om.MPoint(raySource[0], raySource[1], raySource[2]) 
        raySourceVector = om.MVector(raySource[0], raySource[1], raySource[2])
        centerPointVector = om.MVector(centerPoint[0],centerPoint[1],centerPoint[2]) 
        rayDir = om.MPoint(centerPointVector - raySourceVector)
        rayDirection = om.MVector(rayDir[0], rayDir[1], rayDir[2])
        hitPoints = om.MPointArray()
            
        selectionList = om.MSelectionList()
        selectionList.add(surfaceShape)
        surfacePath = om.MDagPath()
        selectionList.getDagPath(0, surfacePath)
        surfaceFn = om.MFnNurbsSurface(surfacePath)

        #maxDist
        maxDist = maxDistance

        #other variables 
        u = om.MDoubleArray()
        v = om.MDoubleArray()
        spc = om.MSpace.kWorld
        toleranceSU = om.MScriptUtil()
        tolerance = toleranceSU.asDoublePtr()
        om.MScriptUtil.setDouble(tolerance, .1)

        #Get the closest intersection.
        gotHit = surfaceFn.intersect(raySource,rayDirection,u,v,hitPoints,toleranceSU.asDouble(),spc,False,None,False,None)

    elif objType == 'mesh':
        raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])
        raySourceVector = om.MFloatVector(raySource[0], raySource[1], raySource[2])
        centerPointVector = om.MFloatVector(centerPoint[0],centerPoint[1],centerPoint[2]) 
        rayDir = om.MFloatPoint(centerPointVector - raySourceVector)
        rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])
        hitPoints = om.MFloatPointArray()
             
        selectionList = om.MSelectionList()
        selectionList.add(surface)
        meshPath = om.MDagPath()
        selectionList.getDagPath(0, meshPath)
        meshFn = om.MFnMesh(meshPath)

        #maxDist
        maxDist = maxDistance

        #other variables
        spc = om.MSpace.kWorld

        #Get the closest intersection.
        gotHit = meshFn.allIntersections(raySource,rayDirection,None,None,False,spc,maxDist,False,None,False,hitPoints,None,None,None,None,None)
        
    else : raise StandardError,"wrong surface type!"

    #Return the intersection as a Python list.
    if gotHit :
        len = hitPoints.length()
        for i in range(0,len):
            point = hitPoints[i]                
            hitMPoint = om.MPoint(point)         
            pArray = [0.0,0.0]
            x1 = om.MScriptUtil()
            x1.createFromList( pArray, 2 )
            uvPoint = x1.asFloat2Ptr()
            uvSet = None
            closestPolygon=None
            uvReturn = meshFn.getUVAtPoint(hitMPoint,uvPoint,om.MSpace.kWorld)
            uValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 0) or False
            vValue = om.MScriptUtil.getFloat2ArrayItem(uvPoint, 0, 1) or False
            log.debug("Hit! [%s]"%(point))
            print(point, raySource)                
            mc.spaceLocator(p=(point[0],point[1],point[2]))
    else:
        return None
    
#test
surface = mc.cylinder()[0]
loc = mc.spaceLocator()
mc.move(8,6,3, loc)
mc.move(8,0,3, surface)
mc.delete(mc.aimConstraint(surface, loc))
raySource = mc.xform(loc, q=1, ws=1, t=1)
centerPoint = mc.xform(surface, q=1, ws=1, t=1)
findSurfaceIntersections(surface, raySource)
