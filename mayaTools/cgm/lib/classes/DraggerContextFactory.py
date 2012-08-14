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
# 	Copyright 2011 CG Monks - All Rights Reserved.
#
# ACKNOWLEDGEMENTS:
#   Morgan Loomis
# 	http://forums.cgsociety.org/archive/index.php/t-983068.html
# 	http://forums.cgsociety.org/archive/index.php/t-1002257.html
# 	https://groups.google.com/forum/?fromgroups#!topic/python_inside_maya/n6aJq27fg0o%5B1-25%5D
#======================================================================================================================
import maya.cmds as mc
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
from zooPyMaya import apiExtensions

from cgm.lib import (locators,
                     distance,
                     guiFactory)
import os


class ContextualPick(object):
    def __init__(self,name = 'cgmDraggerContext', *a,**kw):
        """ 
        Initializes a draggerContext object for use with other tools
        
        Arguments:
        undoMode --
        projection --
        plane --
        space --
        cursor
        drag -- Whether to enable drag mode
        """
        undoMode = kw.pop('undoMode','step')
        projection = kw.pop('projection','plane')
        plane = kw.pop('plane',[1,0,0])
        self.space = kw.pop('space','world')
        cursor = kw.pop('cursor','crossHair')
        drag = kw.pop('drag',False)
        
        if mc.draggerContext(name,query=True,exists=True): # if it exists, delete it
            mc.deleteUI(name)    
        
        self.name = name
        
        imageFilePath = ('cgmDefault.png')
        mc.draggerContext( self.name,  image1 = imageFilePath,
                           undoMode = undoMode, projection = projection, space = self.space,
                           initialize = self.initialPress,
                           pressCommand = self.press,
                           *a,**kw )
        
        if projection == 'plane': mc.draggerContext(self.name,e=True, plane = plane)# if our projection is 'plane', set the plane
        if drag:mc.draggerContext(self.name,e=True, dragCommand = self.drag)# If drag mode, turn it on

        self.setTool()
        
    def finalize(self):
        mc.setToolTo('selectSuperContext')
        mc.selectMode(object=True)
        
    def press(self):
        self.anchorPoint = mc.draggerContext(self.name, query=True, anchorPoint=True)
        self.modifier = mc.draggerContext(self.name, query=True, modifier=True)
        self.button = mc.draggerContext(self.name, query=True, button=True)
        self.returnList.append(self.anchorPoint)
        
        guiFactory.report("Position is %s in '%s' space"%(self.anchorPoint,self.space))
        
    def drag(self):
        self.dragPoint = mc.draggerContext(self.name, query=True, dragPoint=True)
        self.button = mc.draggerContext( self.name, query=True, button=True)
        self.modifier = mc.draggerContext( self.name, query=True, modifier=True)
        
        self.returnList.append(self.dragPoint)

    def initialPress(self):
        self.returnList = []
        mc.warning("Select the first point")
         
    def dropTool(self):
        mc.setToolTo('selectSuperContext')        
        mc.selectMode(object=True) 
        return self.returnList
        
    def setTool(self):
        mc.setToolTo(self.name)
              
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Subclasses
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class clickSurface(ContextualPick):
    """
    Find the points on a surface from a ContextualPick instance
    
    Arguments
    mesh(list) -- currently poly surfaces only
    create() -- options - 'locator','joint'
    closestOnly(bool) -- only get the closest point
    
    Stores
    self.posList(list) -- points on the surface selected in world space
    """  
    def __init__(self,mesh = None, create = False, closestOnly = False,*a,**kw
                 ):
        self.mesh = mesh
        self.create = create
        self.closestOnly = closestOnly
        
        ContextualPick.__init__(self, drag = False, space = 'screen',projection = 'viewPlane', *a,**kw )

    def press(self):
        ContextualPick.press(self)
        self.returnList.append(self.anchorPoint)

        buffer =  screenToWorld(int(self.anchorPoint[0]),int(self.anchorPoint[1]))#get world point and vector!
        
        if self.mesh is not None:
            self.posList = []
            for m in self.mesh:
                if mc.objExists(m):
                    pos = findMeshIntersection(m, buffer[0], buffer[1])
                    if pos is not None:
                        self.posList.append(pos)
         
            if self.posList:
                if self.closestOnly:
                    buffer = distance.returnClosestPoint(self.anchorPoint,self.posList)
                    print buffer
                    self.posList = [buffer]
                    
                if self.create:
                    for pos in self.posList:
                        if self.create == 'locator':
                            nameBuffer = mc.spaceLocator()[0]
                        elif self.create == 'joint':
                            nameBuffer = mc.joint()
                        else:
                            raise NotImplementedError("'%s' hasn't been implemented as a create type yet"%self.create)
                            
                        mc.move (pos[0],pos[1],pos[2], nameBuffer)  
                        
            else:
                guiFactory.warning("No hits detected")
        else:
            guiFactory.warning("No mesh specified")
            return
        
    def release(self):pass
    
    def drag(self):pass   

class clickIntersections(ContextualPick):
    """
    Find the interectiions on surfaces
    
    Arguments
    mesh(list) -- currently poly surfaces only
    create() -- options - 'locator','joint'
    
    returns hitpoints(list) -- [pos1,pos2...]
    """  
    def __init__(self,mesh = None, create = False,*a,**kw
                 ):
        self.mesh = mesh
        self.create = create
        self.intersections = False
        
        ContextualPick.__init__(self, drag = False, space = 'screen',projection = 'viewPlane', *a,**kw )

    def press(self):
        ContextualPick.press(self)
        self.returnList.append(self.anchorPoint)

        buffer =  screenToWorld(int(self.anchorPoint[0]),int(self.anchorPoint[1]))#get world point and vector!
        
        if self.mesh is not None:
            posList = []
            for m in self.mesh:
                if mc.objExists(m):
                    pos = findMeshIntersections(m, buffer[0], buffer[1])
                    if pos:
                        posList.extend(pos)
            if posList:
                self.intersections = posList
                guiFactory.report("Intersections are %s"%posList)
                
                if self.create:
                    for pos in posList:
                        if self.create == 'locator':
                            nameBuffer = mc.spaceLocator()[0]
                        elif self.create == 'joint':
                            nameBuffer = mc.joint()
                            mc.select(cl=True)
                        else:
                            raise NotImplementedError("'%s' hasn't been implemented as a create type yet"%self.create)
                            
                        mc.move (pos[0],pos[1],pos[2], nameBuffer)  
                        
   
            else:
                guiFactory.warning("No hits detected")
        else:
            guiFactory.warning("No mesh specified")
            return
        
    def release(self):pass
    
    def drag(self):pass
    
class clickMidPoint(ContextualPick):
    """
    Find the mid point of interected points on surfaces
    
    Arguments
    mesh(list) -- currently poly surfaces only
    create() -- options - 'locator','joint'    
    
    returns hitpoints(list) -- [pos1,pos2...]
    """  
    def __init__(self,mesh = None, create = False, *a,**kw
                 ):
        self.mesh = mesh
        self.create = create
        self.posList = []
        ContextualPick.__init__(self, drag = False, space = 'screen',projection = 'viewPlane', *a,**kw )

    def press(self):
        ContextualPick.press(self)
        self.returnList.append(self.anchorPoint)
        
        buffer =  screenToWorld(int(self.anchorPoint[0]),int(self.anchorPoint[1]))#get world point and vector!
        
        if self.mesh is not None:
            posList = []
            for m in self.mesh:
                if mc.objExists(m):
                    pos = findMeshIntersections(m, buffer[0], buffer[1])
                    if pos:
                        posList.extend(pos)
            if posList:
                pos = distance.returnAveragePointPosition(posList)
                self.posList.append(pos)
                    
                if self.create:
                    if self.create == 'locator':
                        nameBuffer = mc.spaceLocator()[0]
                    elif self.create == 'joint':
                        nameBuffer = mc.joint()
                    else:
                        raise NotImplementedError("'%s' hasn't been implemented as a create type yet"%self.create)
                        
                    mc.move (pos[0],pos[1],pos[2], nameBuffer)  
                    
                guiFactory.report("Mid point is %s"%pos)
                    
                self.x = pos[0]
                self.y = pos[1]
                self.z = pos[2]
            else:
                guiFactory.warning("No hits detected")
        else:
            guiFactory.warning("No mesh specified")
            return
        
    def release(self):pass
    
    def drag(self):pass
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Functions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def screenToWorld(startX,startY):
    """
    Function to convert a screen space draggerContext click to world space. 
    
    Arguments
    startX(int)
    startY(int)
    
    returns posDouble, vectorDouble
    """
    maya3DViewHandle = OpenMayaUI.M3dView() #3dView handle to be able to query
    activeView = maya3DViewHandle.active3dView() # Get the active view
    posMPoint = OpenMaya.MPoint() #Storage items
    vecMVector = OpenMaya.MVector()

    success = activeView.viewToWorld(startX, startY, posMPoint, vecMVector ) # The function
    
    return [posMPoint.x,posMPoint.y,posMPoint.z],[vecMVector.x,vecMVector.y,vecMVector.z]


def findMeshIntersection(mesh, raySource, rayDir):
    """
    Thanks to Deane @ https://groups.google.com/forum/?fromgroups#!topic/python_inside_maya/n6aJq27fg0o%5B1-25%5D
    
    Return the closest point on a surface from a raySource and rayDir
    
    Arguments
    mesh(string) -- currently poly surface only
    raySource(double3) -- point in world space
    rayDir(double3) -- world space vector
    
    returns hitpoint(double3)
    """    
    #Create an empty selection list.
    selectionList = OpenMaya.MSelectionList()

    #Put the mesh's name on the selection list.
    selectionList.add(mesh)

    #Create an empty MDagPath object.
    meshPath = OpenMaya.MDagPath()

    #Get the first item on the selection list (which will be our mesh)
    #as an MDagPath.
    selectionList.getDagPath(0, meshPath)

    #Create an MFnMesh functionset to operate on the node pointed to by
    #the dag path.
    meshFn = OpenMaya.MFnMesh(meshPath)

    #Convert the 'raySource' parameter into an MFloatPoint.
    raySource = OpenMaya.MFloatPoint(raySource[0], raySource[1], raySource[2])

    #Convert the 'rayDir' parameter into an MVector.`
    rayDirection = OpenMaya.MFloatVector(rayDir[0], rayDir[1], rayDir[2])

    #Create an empty MFloatPoint to receive the hit point from the call.
    hitPoint = OpenMaya.MFloatPoint()

    #Set up a variable for each remaining parameter in the
    #MFnMesh::closestIntersection call. We could have supplied these as
    #literal values in the call, but this makes the example more readable.
    sortIds = False
    maxDist = OpenMaya.MDistance.internalToUI(1000) # This needs work
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
        sortIds, OpenMaya.MSpace.kWorld, maxDist, bothDirections,
        noAccelerator,
        hitPoint,
        noHitParam, noHitFace, noHitTriangle, noHitBary1, noHitBary2)

    #Return the intersection as a Pthon list.
    if gotHit:
            return [hitPoint.x, hitPoint.y, hitPoint.z]
    else:
            return None    
        
def findMeshIntersections(mesh, raySource, rayDir):
    """
    Return the pierced points on a surface from a raySource and rayDir
    
    Arguments
    mesh(string) -- currently poly surface only
    raySource(double3) -- point in world space
    rayDir(double3) -- world space vector
    
    returns hitpoints(list) -- [pos1,pos2...]
    """    
    #Create an empty selection list.
    selectionList = OpenMaya.MSelectionList()

    #Put the mesh's name on the selection list.
    selectionList.add(mesh)

    #Create an empty MDagPath object.
    meshPath = OpenMaya.MDagPath()

    #Get the first item on the selection list (which will be our mesh)
    #as an MDagPath.
    selectionList.getDagPath(0, meshPath)

    #Create an MFnMesh functionset to operate on the node pointed to by
    #the dag path.
    meshFn = OpenMaya.MFnMesh(meshPath)

    #Convert the 'raySource' parameter into an MFloatPoint.
    raySource = OpenMaya.MFloatPoint(raySource[0], raySource[1], raySource[2])

    #Convert the 'rayDir' parameter into an MVector.`
    rayDirection = OpenMaya.MFloatVector(rayDir[0], rayDir[1], rayDir[2])

    #Create an empty MFloatPoint to receive the hit point from the call.
    hitPoints = OpenMaya.MFloatPointArray()

    #Set up a variable for each remaining parameter in the
    #MFnMesh::allIntersections call. We could have supplied these as
    #literal values in the call, but this makes the example more readable.
    sortIds = False
    maxDist = OpenMaya.MDistance.internalToUI(1000) # This needs work
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
        OpenMaya.MSpace.kWorld,
        maxDist,
        bothDirections,
        noAccelerator,
        noSortHits,
        hitPoints, noHitParam, noHitFace, noHitTriangle, noHitBary1, noHitBary2,tolerance)

    #Return the intersection as a Pthon list.
    if gotHit:
        returnList = []
        for i in range( hitPoints.length() ):
            returnList.append( [hitPoints[i].x, hitPoints[i].y,hitPoints[i].z])
        return returnList
    else:
        return None   
    
