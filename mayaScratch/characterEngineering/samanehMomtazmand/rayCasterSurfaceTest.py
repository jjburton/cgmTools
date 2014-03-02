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

#rayCasterSurfaceTest
sphere = mc.sphere()
loc = mc.spaceLocator()
mc.move(8,6,3, loc)
mc.select(sphere, loc)
selections = [r9Meta.MetaClass(obj) for obj in mc.ls(sl=True)]

surface = selections[0]
raySource = mc.xform(loc, q=1, ws=1, t=1)
centerPoint = mc.xform(sphere, q=1, ws=1, t=1)
log.debug("raySource: %s"%raySource)
rayDir = (-1.0, 0.0, 0.0)
maxDistance = 1000

selectionList = om.MSelectionList()
selectionList.add('nurbsSphere1')
surfacePath = om.MDagPath()
selectionList.getDagPath(0, surfacePath)
surfaceFn = om.MFnNurbsSurface(surfacePath)

raySource = om.MPoint(raySource[0], raySource[1], raySource[2])
raySourceVector = om.MVector(raySource[0], raySource[1], raySource[2])
centerPointVector = om.MVector(centerPoint[0], centerPoint[1], centerPoint[2])
rayDir = om.MPoint(centerPointVector - raySourceVector)
rayDirection = om.MVector(rayDir[0], rayDir[1], rayDir[2])
hitPoint = om.MPoint()

log.debug("maxDistance: %s"%maxDistance)

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
hitMPoint = om.MPoint(hitPoint)         
log.debug("Hit! [%s,%s,%s]"%(hitPoint.x, hitPoint.y, hitPoint.z))
print( {'hit':[hitPoint.x, hitPoint.y, hitPoint.z],'source':[raySource.x,raySource.y,raySource.z]})                

mc.spaceLocator(p=(hitPoint.x, hitPoint.y, hitPoint.z))




















