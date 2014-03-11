from cgm.core import cgm_Meta as cgmMeta
import Red9.core.Red9_Meta as r9Meta
import maya.cmds as mc
import maya.OpenMaya as om
from zooPyMaya import apiExtensions

#test
surface = mc.polyCylinder()[0]
loc = mc.spaceLocator()
mc.move(8,6,3, loc)
mc.move(8,0,3, surface)
mc.delete(mc.aimConstraint(surface, loc))

raySource = mc.xform(loc, q=1, ws=1, t=1)
surfaceShape = mc.listRelatives(surface, s=1)
centerPoint = mc.xform(surface, q=1, ws=1, t=1)
surfaceShape = mc.listRelatives(surface, s=1)
centerPoint = mc.xform(surface, q=1, ws=1, t=1)    
maxDistance = 1000
rayDir = (0.0,0.0,0.0)

raySource = om.MPoint(raySource[0], raySource[1], raySource[2])
raySourceVector = om.MVector(raySource[0], raySource[1], raySource[2])
centerPointVector = om.MVector(centerPoint[0],centerPoint[1],centerPoint[2]) 
rayDir = om.MPoint(centerPointVector - raySourceVector)
rayDirection = om.MVector(rayDir[0], rayDir[1], rayDir[2])
hitPoints = om.MPointArray()
             
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
        
#Return the intersection as a Python list.
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
    print(point, raySource)                
    mc.spaceLocator(p=(point[0],point[1],point[2]))
    
# TypeError: in method 'MFnMesh_allIntersections', argument 2 of type 'MFloatPoint const &' # 
