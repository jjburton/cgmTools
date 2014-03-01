from cgm.core import cgm_Meta as cgmMeta
import Red9.core.Red9_Meta as r9Meta
import maya.cmds as mc
import copy
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as om
from zooPyMaya import apiExtensions
from cgm.core import cgm_General as cgmGeneral
from cgm.lib import (locators,dictionary,cgmMath,lists,geo,distance)
import os
import math
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

#----------------------------------

#rayCasterMeshTest
sphere = mc.polySphere(sx=5,sy=5)
loc = mc.spaceLocator()
mc.move(8,6,3, loc)
mc.delete(mc.aimConstraint(sphere, loc))
mc.select(sphere, loc)
selections = [r9Meta.MetaClass(obj) for obj in mc.ls(sl=True)]
mesh = selections[0]
raySource = mc.xform(loc, q=1, ws=1, t=1)
log.debug("raySource: %s"%raySource)
rayDir = (1.0, 0.0, 0.0)
maxDistance = 1000

selectionList = om.MSelectionList()
selectionList.add('pSphere1')
meshPath = om.MDagPath()
selectionList.getDagPath(0, meshPath)
meshFn = om.MFnMesh(meshPath)
raySource = om.MFloatPoint(raySource[0], raySource[1], raySource[2])
rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])
hitPoint = om.MFloatPoint()

log.debug("maxDistance: %s"%maxDistance)

#maxDist
#vtxs number
verts = om.MFloatPointArray()
mPoints = meshFn.getPoints(verts, om.MSpace.kWorld)
vertsN = verts.length()
print(vertsN)

#vertices
vertices = []
om.MGlobal_getActiveSelectionList(selectionList)
for i in range(0,selectionList.length()):
    obj= om.MObject()
    selectionList.getDagPath(0,meshPath,obj)
    vts=om.MPointArray()
    meshFn.getPoints(vts)
    for j in range(0,vts.length()):
        print ("The object "+meshPath.partialPathName()+ "'s vertex #"+ str(j+1)+" is :")
        print ("X= " + str(vts[j].x) + "     Y= " + str(vts[j].y) + "     Z= " + str(vts[j].z))
        vtx = [str(vts[j].x), str(vts[j].y), str(vts[j].z)]
        vertices.append(vtx)

#test
for x in range(0,vertsN):
    testLoc = mc.spaceLocator(p = (vertices[x]))

maxDist = 1.0
for p in range(0,vertsN):
    distance = math.sqrt((raySource[0] - float(vertices[p][0]))**2 + (raySource[1] - float(vertices[p][1]))**2)
    maxDist = max(maxDist, distance)
maxDist = om.MDistance.internalToUI(maxDist)

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
rayDir = (1.0, 0.0, 0.0)
rayDirection = om.MFloatVector(rayDir[0], rayDir[1], rayDir[2])

#Get the closest intersection.
gotHit = meshFn.closestIntersection(raySource,rayDirection,noFaceIds,noTriangleIds,sortIds,
                                                            om.MSpace.kWorld,maxDist, bothDirections,noAccelerator,
                                                            hitPoint,noHitParam, noHitFace, noHitTriangle, noHitBary1, noHitBary2)
#I got 'gotHit' False!!!!


#Return the intersection as a Python list.
#if gotHit :
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
print( {'hit':[hitPoint.x, hitPoint.y, hitPoint.z],'source':[raySource.x,raySource.y,raySource.z],'uv':[uValue,vValue]})                

#test
#sel = mc.select(mc.polyListComponentConversion(tuv = True), r = True) 
#print(mc.polyEditUV(sel, q=1))
 




















