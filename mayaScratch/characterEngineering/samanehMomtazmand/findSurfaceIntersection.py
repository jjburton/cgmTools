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

def findSurfaceIntersection(surface, raySource):
    '''
    findSurfaceIntersection
    '''
    surfaceShape = mc.listRelatives(surface, s=1)
    centerPoint = mc.xform(surface, q=1, ws=1, t=1)    
	raySource = om.MPoint(raySource[0], raySource[1], raySource[2])
	raySourceVector = om.MVector(raySource[0], raySource[1], raySource[2])
	centerPointVector = om.MVector(centerPoint[0],centerPoint[1],centerPoint[2]) 
	rayDir = om.MPoint(centerPointVector - raySourceVector)
	rayDirection = om.MVector(rayDir[0], rayDir[1], rayDir[2])
	hitPoint = om.MPoint()
	maxDistance = 1000
	
    log.debug("raySource: %s"%raySource)    
    log.debug("maxDistance: %s"%maxDistance)
    
    try:
        _str_funcName = 'findSurfaceIntersection'
        log.debug(">>> %s >> "%_str_funcName + "="*75)           
        if len(mc.ls(surface))>1:
            raise StandardError,"findSurfaceIntersection>>> More than one surface named: %s"%surface
    except StandardError,error:
        log.error(">>> %s >> surface: %s | raysource: %s | rayDir %s | error: %s"%(_str_funcName,surface,raySource,rayDir,error))   
                 
	#checking the type             
    objType = search.returnObjectType(surface)
    
    if objType == 'nurbsSurface':     
        selectionList = om.MSelectionList()
        selectionList.add(surfaceShape)
        surfacePath = om.MDagPath()
        selectionList.getDagPath(0, surfacePath)
        surfaceFn = om.MFnNurbsSurface(surfacePath)

        #maxDist
        maxDist = maxDistance

        #other variables 
        uSU = om.MScriptUtil()
        vSU = om.MScriptUtil()
        uPtr = uSU.asDoublePtr()
        vPtr = uSU.asDoublePtr()
        spc = om.MSpace.kWorld
        toleranceSU = om.MScriptUtil()
        tolerance = toleranceSU.asDoublePtr()
        om.MScriptUtil.setDouble(tolerance, .1)

        #Get the closest intersection.
        gotHit = surfaceFn.intersect(raySource, rayDirection, uPtr, vPtr,
        hitPoint, toleranceSU.asDouble(), spc, False, None, False, None)

    	#Return the intersection as a Python list.
        if gotHit:
            hitMPoint = om.MPoint(hitPoint)         
            log.debug("Hit! [%s,%s,%s]"%(hitPoint.x, hitPoint.y, hitPoint.z))
            print({'hit'[hitPoint.x,hitPoint.y,hitPoint.z],'source'[raySource.x,raySource.y,raySource.z]})                

            mc.spaceLocator(p=(hitPoint.x, hitPoint.y, hitPoint.z))
        else:
            return None
    
    elif objType == 'mesh':     
        selectionList = om.MSelectionList()
        selectionList.add(surface)
        meshPath = om.MDagPath()
        selectionList.getDagPath(0, meshPath)
        meshFn = om.MFnMesh(meshPath)

        #maxDist
        maxDist = maxDistance
        
        #other variables 
        sortIds = False
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
        gotHit=meshFn.closestIntersection(raySource,rayDirection,noFaceIds,noTriangleIds,sortIds,om.MSpace.kWorld,maxDist,bothDirections,noAccelerator,hitPoint,noHitParam,noHitFace,noHitTriangle,noHitBary1,noHitBary2)

    	#Return the intersection as a Python list.
        if gotHit :
            hitMPoint = om.MPoint(hitPoint.x, hitPoint.y, hitPoint.z)         
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
            print({'hit'[hitPoint.x,hitPoint.y,hitPoint.z],'source'[raySource.x,raySource.y,raySource.z],'uv'[uValue,vValue]})                
    
            mc.spaceLocator(p=(hitPoint.x, hitPoint.y, hitPoint.z))
        else:
            return None
    else : raise StandardError,"wrong surface type!"