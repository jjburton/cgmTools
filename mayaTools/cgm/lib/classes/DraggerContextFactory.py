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
import maya.OpenMaya as OpenMaya
from zooPyMaya import apiExtensions

from cgm.lib import (locators,
                     curves,
                     search,
                     attributes,
                     lists,
                     nodes,
                     rigging,
                     distance,
                     guiFactory)
reload(distance)
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
class clickMesh(ContextualPick):
    """
    Find positional data from clicking on a surface from a ContextualPick instance.
    And other things...:)
    
    Arguments
    mesh(list) -- currently poly surfaces only
    mode(string) -- options:('surface' is default)
                    'surface' -- surface hit per mesh piece
                    'intersections' -- all hits on the vector ray
                    'midPoint' -- mid point of intersections
    
    create(False/option) -- options:('locator' is default)
                            'locator' -- makes a locator 
                            'joint' -- creates joints per click
                            'jointChain' -- rebuilds all positions as a chain at tool exit
                            'curve' -- builds curve from positions at tool exit
                            'group' -- build groups at positions
                            'follicle' --creates a folicle
                            
    closestOnly(bool) -- only return the closest hit from all mesh hits (default - True)
    clampIntersections(False/int) -- clamp number of interactions
    dragStore(bool) -- whether to force store data during drag
    
    Stores
    self.posList(list) -- points on the surface selected in world space
    """  
    def __init__(self,
                 mode = 'surface',
                 mesh = None,
                 create = False,
                 closestOnly = True,
                 clampIntersections = False,
                 dragStore = False,
                 *a,**kw):
        # Set our attributes  
        self.createModes = ['locator','joint','jointChain','curve','follicle','group',False]
        self.modes = ['surface','intersections','midPoint']
        self.meshList = []
        self.meshPosDict = {} #creating this pretty much just for follicle mode so we can attache to a specific mesh
        self.createMode = create
        self.closestOnly = closestOnly
        self.createdList = []
        self.clampSetting = clampIntersections
        self.dragStoreMode = dragStore
        self.returnList = []
        self.posBuffer = False
        self.createModeBuffer = False
        
        self.setMode(mode)
               
        ContextualPick.__init__(self, drag = True, space = 'screen',projection = 'viewPlane', *a,**kw )
        
        if mesh is not None:
            assert type(mesh) is list,"Mesh call must be in list form when called"
            for m in mesh:
                self.addTargetMesh(m)        
        
    def addTargetMesh(self,mesh):
        """
        Add target mesh to the tool
        """
        if not mc.objExists(mesh):
            guiFactory.warning("'%s' doesn't exist. Ignoring..."%mesh)
            return False

        if mesh not in self.meshList:
            buffer = search.returnObjectType(mesh)
            if buffer == 'mesh':
                self.meshList.append(mesh)
                return True
            else:
                guiFactory.warning("'%s' is not a mesh. It is returning as '%s'"%(mesh,buffer))
                return False
        return False
            
    def removeTargetMesh(self,mesh):
        """
        Remove target mesh to the tool
        """
        if mesh in self.meshList:
            self.meshList.remove(mesh) 
            guiFactory.report("'%s' removed from '%s'"%(mesh,self.name))
        
    def setMode(self,mode):
        """
        Set tool mode
        """
        assert mode in ['surface','intersections','midPoint'],"'%s' not a defined mode"%mode
        self.mode = mode
        
    def setClamp(self,setting):
        """
        Set clamp setting
        """
        assert type(setting) is int or setting is False,"'%s' is not a valid setting"%setting 
        self.clampSetting = setting
        
    def setCreate(self,create):
        """
        Set tool mode
        """
        assert create in self.createModes,"'%s' is not a valid create mode"%create    
        self.createMode = create
        
    def setDragStoreMode(self,mode):
        """
        Set drag update mode
        """
        assert type(mode) is bool,"'%s' should be a bool"%mode                 
        self.dragStoreMode = mode
        
    def reset(self):
        """
        Reset data
        """
        self.createdList = []
        self.returnList = []
        
        guiFactory.warning("'%s' reset."%self.name)
        
    def setTool(self):
        ContextualPick.setTool(self)
        
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
        #Clean our lists...
        self.createdList = lists.returnListNoDuplicates(self.createdList)
        self.returnList = lists.returnListNoDuplicates(self.returnList)
        
        if self.createMode in ['curve','jointChain','group','follicle'] and self.returnList and len(self.returnList)>1:
            if self.createMode == 'group':
                bufferList = []
                for i,o in enumerate(self.createdList):
                    buffer = rigging.groupMeObject(o,False)
                    bufferList.append(buffer)                    
                    try:mc.delete(o)
                    except:pass
                self.createdList = bufferList
                
                    
            else:
                for o in self.createdList:
                    try:mc.delete(o)
                    except:pass
                if self.createMode == 'curve':
                    if len(self.returnList) > 1:
                        self.createdList = [mc.curve (d=2, p = self.returnList , ws=True)]
                    else:
                        guiFactory.warning("Need at least 2 points for a curve")                        
                elif self.createMode == 'jointChain':
                    self.createdList = []
                    mc.select(cl=True)
                    for pos in self.returnList:        
                        self.createdList.append( mc.joint (p = (pos[0], pos[1], pos[2])) )
                        
                elif self.createMode =='follicle':
                    for pos in self.returnList:
                        for m in self.meshPosDict.keys():
                            if pos in self.meshPosDict[m]:
                                info = distance.returnClosestPointOnMeshInfoFromPos(pos,m)
                                if info['parameterU'] and info['parameterV']:
                                    follicle = nodes.createFollicleOnMesh(m)
                                    attributes.doSetAttr(follicle[0],'parameterU',info['parameterU'])
                                    attributes.doSetAttr(follicle[0],'parameterV',info['parameterV'])
                                

        self.reset()
        
        
    def release(self):
        """
        Store current data to return buffers
        """
        if self.posBuffer:
            guiFactory.report("Position data : %s "%(self.posBuffer))
        if self.createModeBuffer:
            guiFactory.report("Created : %s "%(self.createModeBuffer))
            mc.select(cl=True)
                
        #Only store return values on release
        if self.posBuffer:
            for p in self.posBuffer:
                self.returnList.append(p)
        if self.createModeBuffer:
            self.createdList.extend(self.createModeBuffer)
    
    def drag(self):
        """
        update positions
        """
        ContextualPick.drag(self)
        self.updatePos()
        
        if self.dragStoreMode:
            if self.posBuffer:
                for p in self.posBuffer:
                    self.returnList.append(p)
        if self.createModeBuffer:
            self.createdList.extend(self.createModeBuffer) 
            
    def getDistanceToCheck(self,m):
        assert mc.objExists(m), "'%s' doesn't exist. Couldn't check distance!"%m
        baseDistance = distance.returnDistanceBetweenPoints(self.clickPos, distance.returnWorldSpacePosition(m))
        baseSize = distance.returnBoundingBoxSize(m)
        
        return distance.returnWorldSpaceFromMayaSpace( baseDistance + sum(baseSize) )
    
    def convertPosToLocalSpace(self,pos):
        assert type(pos) is list,"'%s' is not a list. Coordinate expected"%pos
        returnList = []
        for f in pos:
            returnList.append( distance.returnMayaSpaceFromWorldSpace(f))
        return returnList
        
    def updatePos(self):
        """
        Get updated position data via shooting rays
        """
        if not self.meshList:
            return guiFactory.warnqing("No mesh objects have been added to '%s'"%(self.name))
        
        buffer =  screenToWorld(int(self.x),int(self.y))#get world point and vector!
        #locators.doLocPos(buffer[0])
        
        self.clickPos = buffer[0] #Our world space click point
        self.clickVector = buffer[1] #Camera vector
        
        self.posBuffer = []#Clear our pos buffer
        
        for m in self.meshList:#Get positions per mesh piece
            #First get the distance to try to check
            checkDistance = self.getDistanceToCheck(m)
            print ("Checking %s"%checkDistance)
            if m not in self.meshPosDict.keys():
                self.meshPosDict[m] = []
                
            if mc.objExists(m):
                if self.mode == 'surface':
                    buffer = findMeshIntersection(m, self.clickPos , self.clickVector, checkDistance )                
                    
                    if buffer is not None:
                        self.posBuffer.append(self.convertPosToLocalSpace( buffer['hit'] ))  
                        self.startPoint = self.convertPosToLocalSpace( buffer['source'] )
                        self.meshPosDict[m].append(buffer['hit'])
                else:
                    buffer = findMeshIntersections(m, self.clickPos , self.clickVector , checkDistance)                                    
                    if buffer:
                        conversionBuffer = []
                        #Need to convert to local space
                        for hit in buffer['hits']:
                            conversionBuffer.append(self.convertPosToLocalSpace( hit ))
                            
                        self.posBuffer.extend(conversionBuffer)
                        self.startPoint = self.convertPosToLocalSpace( buffer['source'] )
                        self.meshPosDict[m].extend(buffer['hits'])
                        
        if not self.posBuffer:
            guiFactory.warning('No hits detected!')
            return
        
        if self.clampSetting and self.clampSetting < len(self.posBuffer):
            guiFactory.warning("Position buffer was clamped. Check settings if this was not desired.")
            self.posBuffer = distance.returnPositionDataDistanceSortedList(self.startPoint,self.posBuffer)
            self.posBuffer = self.posBuffer[:self.clampSetting]
            
        if self.mode == 'midPoint':                
            self.posBuffer = [distance.returnAveragePointPosition(self.posBuffer)]

        if self.posBuffer: #Check for closest and just for hits
            if self.closestOnly and self.mode != 'intersections':
                buffer = distance.returnClosestPoint(self.startPoint,self.posBuffer)
                self.posBuffer = [buffer]               
        else:pass
            #guiFactory.warning("No hits detected")
            
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
    maxDist = OpenMaya.MDistance.internalToUI(1000000)# This needs work    
    #maxDist = OpenMaya.MDistance.internalToUI(maxDistance) # This needs work
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
            return {'hit':[hitPoint.x, hitPoint.y, hitPoint.z],'source':[raySource.x,raySource.y,raySource.z]}
    else:
            return None    
        
def findMeshIntersections(mesh, raySource, rayDir,maxDistance = 1000):
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
    maxDist = OpenMaya.MDistance.internalToUI(1000000)# This needs work    
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
        returnDict = {}
        hitList = []
        for i in range( hitPoints.length() ):
            hitList.append( [hitPoints[i].x, hitPoints[i].y,hitPoints[i].z])
            
            returnDict = {'hits':hitList,'source':[raySource.x,raySource.y,raySource.z]}

        return returnDict
    else:
        return None   
    
