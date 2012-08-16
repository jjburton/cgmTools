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
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMaya as OpenMaya
from zooPyMaya import apiExtensions

from cgm.lib import (locators,
                     curves,
                     rigging,
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
        self.undoMode = kw.pop('undoMode','step')
        self.projection = kw.pop('projection','plane')
        self.plane = kw.pop('plane',[1,0,0])
        self.space = kw.pop('space','world')
        self.cursor = kw.pop('cursor','crossHair')
        self.dragOption = kw.pop('drag',False)
        
        self.name = name
        self.returnList = []
        
        self.build(*a,**kw )
        self.setTool()
        
    def build(self,*a,**kw ):
        if mc.draggerContext(self.name,query=True,exists=True): # if it exists, delete it
            mc.setToolTo('selectSuperContext')        
            mc.selectMode(object=True)             
            mc.deleteUI(self.name)  
            
        imageFilePath = ('cgmDefault.png')
            
        mc.draggerContext( self.name,  image1 = imageFilePath,
                           undoMode = self.undoMode, projection = self.projection, space = self.space,
                           initialize = self.initialPress,
                           pressCommand = self.press,
                           releaseCommand = self.release,
                           finalize = self.finalize,
                           *a,**kw )
        
        if self.projection == 'plane': mc.draggerContext(self.name,e=True, plane = self.plane)# if our projection is 'plane', set the plane
        if self.dragOption:mc.draggerContext(self.name,e=True, dragCommand = self.drag)# If drag mode, turn it on
        
        
    def finalize(self):pass
              
        
    def press(self):
        if not mc.draggerContext(self.name,query=True,exists=True): # if it exists, delete it       
            self.build
            self.setTool()            
        
        self.anchorPoint = mc.draggerContext(self.name, query=True, anchorPoint=True)
        self.modifier = mc.draggerContext(self.name, query=True, modifier=True)
        self.button = mc.draggerContext(self.name, query=True, button=True)
        
        self.x = self.anchorPoint[0]
        self.y = self.anchorPoint[1]
        self.z = self.anchorPoint[2]
        
        #guiFactory.report("Position is %s in '%s' space"%(self.anchorPoint,self.space))
        
    def release(self):pass
    
    def drag(self):
        self.dragPoint = mc.draggerContext(self.name, query=True, dragPoint=True)
        self.button = mc.draggerContext( self.name, query=True, button=True)
        self.modifier = mc.draggerContext( self.name, query=True, modifier=True)
        
        self.x = self.dragPoint[0]
        self.y = self.dragPoint[1]
        self.z = self.dragPoint[2]

    def initialPress(self):pass
    
    def dropTool(self):
        mc.setToolTo('selectSuperContext')        
        mc.selectMode(object=True) 
            
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
    mode(string) -- ['surface','intersections','midPoint']
    
    create(False/option) -- options - 'locator','joint','curve','group' ('locator' is default
    closestOnly(bool) -- only get the closest point (default - True)
    clampIntersections(False/int) -- clamp number of interactions
    
    Stores
    self.posList(list) -- points on the surface selected in world space
    """  
    def __init__(self,mesh = None, mode = 'surface', create = False, closestOnly = True,clampIntersections = False,*a,**kw
                 ):
        assert mesh is not None, "Mesh must be specified"
        assert type(mesh) is list, "Mesh specified must be list"
        
        self.meshList = []
        self.createMode = create
        self.closestOnly = closestOnly
        self.createdList = []
        self.setMode(mode)
        self.clampSetting = clampIntersections
        self.returnList = []
        
        if mesh is None:
            guiFactory.warning("No mesh specified")
            return
        else:
            for m in mesh:
                if mc.objExists(m):
                    self.meshList.append(m)
                else:
                    guiFactory.warning("'%s' doesn't exist. Ignoring..."%m)
        
        ContextualPick.__init__(self, drag = True, space = 'screen',projection = 'viewPlane', *a,**kw )
        
    def setMode(self,mode):
        """
        Set tool mode
        """
        assert mode in ['surface','intersections','midPoint'],"'%s' not a defined mode"%mode
        self.mode = mode
        
    def setCreate(self,create):
        """
        Set tool mode
        """
        self.createMode = create
        
    def reset(self):
        """
        Reset data
        """
        self.createdList = []
        self.returnList = []
        
        guiFactory.warning("'%s' reset."%self.name)
        
    def press(self):
        """
        Press action. Clears buffers.
        """
        ContextualPick.press(self)
        self.createModeBuffer = []
        self.updatePos()
        
    def finalize(self):
        """
        Press action. Clears buffers.
        """
        
        if self.createMode in ['curve','joint','group'] and self.returnList and len(self.returnList)>1:
            if self.createMode == 'group':
                for i,o in enumerate(self.createdList):
                    buffer = rigging.groupMeObject(o,False)
                    try:mc.delete(o)
                    except:pass
                    self.createdList[i] = buffer                
            else:
                for o in self.createdList:
                    try:mc.delete(o)
                    except:pass
                if self.createMode == 'curve':
                    self.createdList = [curves.curveFromPosList(self.returnList)]
                elif self.createMode == 'joint':
                    self.createdList = []
                    mc.select(cl=True)
                    for pos in self.returnList:        
                        self.createdList.append( mc.joint (p = (pos[0], pos[1], pos[2])) )            

        
    def release(self):
        """
        Store current data to return buffers
        """       
        guiFactory.report("Position data : %s "%(self.posBuffer))
        if self.createModeBuffer:
            guiFactory.report("Created : %s "%(self.createModeBuffer))
            mc.select(cl=True)
                
        #Only store return values on release
        for p in self.posBuffer:
            self.returnList.append(p)
        self.createdList.extend(self.createModeBuffer)
    
    def drag(self):
        """
        update positions
        """
        ContextualPick.drag(self)
        self.updatePos()
    
    def updatePos(self):
        """
        Get updated position data via shooting rays
        """       
        buffer =  screenToWorld(int(self.x),int(self.y))#get world point and vector!
        self.clickPos = buffer[0] #Our world space click point
        self.clickVector = buffer[1] #Camera vector
        
        self.posBuffer = []#Clear our pos buffer
        
        for m in self.meshList:#Get positions per mesh piece
            if mc.objExists(m):
                if self.mode == 'surface':
                    pos = findMeshIntersection(m, self.clickPos , self.clickVector )
                    if pos is not None:
                        self.posBuffer.append(pos)                
                else:
                    pos = findMeshIntersections(m, self.clickPos ,  self.clickVector )              
                    if pos:
                        self.posBuffer.extend(pos)
                        
                if self.mode == 'midPoint' and self.posBuffer:
                    if self.clampSetting and self.clampSetting < len(self.posBuffer):
                        self.posBuffer = self.posBuffer[:self.clampSetting]
                        
                    self.posBuffer = [distance.returnAveragePointPosition(self.posBuffer)]

                
        if self.posBuffer: #Check for closest and just for hits
            if self.closestOnly and self.mode != 'intersections':
                buffer = distance.returnClosestPoint(self.anchorPoint,self.posBuffer)
                self.posBuffer = [buffer]               
        else:
            guiFactory.warning("No hits detected")
            
        if self.createMode and self.posBuffer: # Make our stuff
            #Delete the old stuff
            if self.createModeBuffer:
                for o in self.createModeBuffer:
                    try:mc.delete(o)
                    except:pass
                self.createModeBuffer = []
            
            for pos in self.posBuffer:
                if len(pos) == 3:
                    if self.createMode == 'joint':
                        nameBuffer = mc.joint()
                    else:
                        nameBuffer = mc.spaceLocator()[0]
                        
                    mc.move (pos[0],pos[1],pos[2], nameBuffer)              
                    self.createModeBuffer.append(nameBuffer)
                else:
                    guiFactory.warning("'%s' isn't a valid position"%pos)
                
        mc.refresh()#Update maya to make it interactive!

    
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
    Thanks to Deane @ https://groups.google.com/forum/?fromgroups#!topic/python_inside_maya/n6aJq27fg0o%5B1-25%5D
    
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
    
