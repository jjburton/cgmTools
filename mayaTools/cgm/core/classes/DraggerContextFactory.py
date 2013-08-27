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
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.rigger.lib import joint_Utils as jntUtils
from cgm.core.lib import rayCaster as RayCast
from cgm.lib import (locators,
                     geo,
                     curves,
                     search,
                     attributes,
                     lists,
                     nodes,
                     rigging,
                     distance,
                     guiFactory)
reload(distance)
reload(curves)
import os

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

class ContextualPick(object):
    def __init__(self,name = 'cgmDraggerContext', *a,**kws):
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
        self.undoMode = kws.pop('undoMode','step')
        self.projection = kws.pop('projection','plane')
        self.plane = kws.pop('plane',[1,0,0])
        self.space = kws.pop('space','world')
        self.cursor = kws.pop('cursor','crossHair')
        self.dragOption = kws.pop('drag',False)
        
        self.name = name
        self.l_return = []
        
        self.build(*a,**kws )
        self.setTool()
        
    def build(self,*a,**kws ):
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
                           *a,**kws )
        
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
        
        #log.info("Position is %s in '%s' space"%(self.anchorPoint,self.space))
        
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
    
    @Parameters
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
    toCreate(list) -- list of items names to make, sets's max as well
    posOffset(vector) -- how much ot offset 
    offsetMode(bool) -- 'vector','normal' (default -- 'vector')
    orientSnap(bool) -- orient the created object to surface
    
    Stores
    self.l_pos(list) -- points on the surface selected in world space
    
    TODO:
    Add depth option
    """  
    def __init__(self,
                 mode = 'surface',
                 mesh = None,
                 create = False,
                 closestOnly = True,
                 clampIntersections = False,
                 dragStore = False,
                 maxStore = False,
                 posOffset = None,
                 clampValues = [None,None,None],
                 offsetMode = 'normal',
                 orientSnap = True,
                 tagAndName = {},
                 toCreate = [],
                 *a,**kws):
	
	_str_funcName = 'clickMesh.__init__'
	log.info(">>> %s >> "%_str_funcName + "="*75)     	
	#>>> Store our info ====================================================================
        self._createModes = ['locator','joint','jointChain','curve','follicle','group',False]
        self._l_modes = ['surface','intersections','midPoint']
        self.l_mesh = []
        self.d_meshPos = {} #creating this pretty much just for follicle mode so we can attache to a specific mesh
        self.d_meshUV = {}
        self.f_meshArea = 1
        
        self._createMode = create
        self._getUV = False
        
        if self._createMode == 'follicle':#Only get uv intersection for follicles
            self._getUV = True
            
        self.b_closestOnly = closestOnly
        self.l_created = []
        self.b_clampSetting = clampIntersections
        self.b_dragStoreMode = dragStore
        self.l_return = []
	self.d_tagAndName = tagAndName
        self._posBuffer = False
        self.v_posOffset = posOffset or False    
	self.str_offsetMode = offsetMode
	self.b_orientSnap = orientSnap
        self._createModeBuffer = False
        self.int_maxStore = maxStore
        self.l_toCreate = toCreate
	self.v_clampValues = clampValues
        if toCreate:
            self.int_maxStore = len(toCreate)
        
        self.setMode(mode)
               
        ContextualPick.__init__(self, drag = True, space = 'screen',projection = 'viewPlane', *a,**kws )
        
        if mesh is not None:
            assert type(mesh) is list,"Mesh call must be in list form when called"
            for m in mesh:
                self.addTargetMesh(m)    
            self.updateMeshArea()
            
    def updateMeshArea(self):
        """
        Updates the mesh area of the added meshes (for sizing purposes)
        """
        self.f_meshArea = 1
        buffer = []
        for m in self.l_mesh:
            buffer.append(distance.returnObjectSize(m))
        
        if buffer:
            self.f_meshArea = sum(buffer)/len(buffer)
            
    def addTargetMesh(self,mesh):
        """
        Add target mesh to the tool
        """
        if not mc.objExists(mesh):
            log.warning("'%s' doesn't exist. Ignoring..."%mesh)
            return False

        if mesh not in self.l_mesh:
            buffer = search.returnObjectType(mesh)
            if buffer == 'mesh':
                self.l_mesh.append(mesh)
                self.updateMeshArea()
                return True
            else:
                log.warning("'%s' is not a mesh. It is returning as '%s'"%(mesh,buffer))
                return False
        return False
            
    def removeTargetMesh(self,mesh):
        """
        Remove target mesh to the tool
        """
        if mesh in self.l_mesh:
            self.l_mesh.remove(mesh) 
            log.info("'%s' removed from '%s'"%(mesh,self.name))
        
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
        self.b_clampSetting = setting
        
    def setCreate(self,create):
        """
        Set tool mode
        """
        assert create in self._createModes,"'%s' is not a valid create mode"%create    
        self._createMode = create
        if self._createMode == 'follicle':#Only get uv intersection for follicles
            self._getUV = True            
        
    def setDragStoreMode(self,mode):
        """
        Set drag update mode
        """
        assert bool(mode) in [True,False],"'%s' should be a bool"%mode                 
        self.b_dragStoreMode = mode
        log.warning("Drag store is %s!"%mode)
        
    def reset(self):
        """
        Reset data
        """
        self.l_created = []
        self.l_return = []
        
        log.warning("'%s' reset."%self.name)
        
    def setTool(self):
        ContextualPick.setTool(self)
        
    def dropTool(self):
        mc.setToolTo('selectSuperContext')        
        mc.selectMode(object=True)
        
    def press(self):
        """
        Press action. Clears buffers.
        """
        ContextualPick.press(self)
        self._createModeBuffer = []
        self.updatePos()
        
    def finalize(self):
        """
        Press action. Clears buffers.
        """
        #Clean our lists...
        self.l_created = lists.returnListNoDuplicates(self.l_created)
        self.l_return = lists.returnListNoDuplicates(self.l_return)
        
        if self._createMode in ['curve','jointChain','group','follicle'] and self.l_return:
            if self._createMode == 'group':
                bufferList = []
                for i,o in enumerate(self.l_created):
                    buffer = rigging.groupMeObject(o,False)
                    bufferList.append(buffer)                    
                    try:mc.delete(o)
                    except:pass
                self.l_created = bufferList
                
            elif self._createMode =='follicle':
                if self.mode == 'midPoint':
                    log.warning("Mid point mode doesn't work with follicles")
                    return
                bufferList = []
                for o in self.l_created:
                    mesh = attributes.doGetAttr(o,'cgmHitTarget')
                    if mc.objExists(mesh):
                        uv = distance.returnClosestUVToPos(mesh,distance.returnWorldSpacePosition(o))
                        follicle = nodes.createFollicleOnMesh(mesh)
                        attributes.doSetAttr(follicle[0],'parameterU',uv[0])
                        attributes.doSetAttr(follicle[0],'parameterV',uv[1])
                        try:mc.delete(o)
                        except:pass                        
            else:
                for o in self.l_created:
                    try:mc.delete(o)
                    except:pass
                if self._createMode == 'curve' and len(self.l_return)>1:
                    if len(self.l_return) > 1:
                        self.l_created = [curves.curveFromPosList(self.l_return)]
                    else:
                        log.warning("Need at least 2 points for a curve")                        
                elif self._createMode == 'jointChain':
                    self.l_created = []
                    mc.select(cl=True)
                    for pos in self.l_return:                             
                        self.l_created.append( mc.joint (p = (pos[0], pos[1], pos[2]),radius = 1) ) 
        log.debug( self.l_created)
	if self.d_tagAndName:
	    for o in self.l_created:
		try:
		    i_o = cgmMeta.cgmNode(o)
		    for tag in self.d_tagAndName.keys():
			i_o.doStore(tag,self.d_tagAndName[tag])
		    i_o.doName()
		except StandardError,error:
		    log.error(">>> clickMesh >> Failed to tag and name: %s | error: %s"%(i_o.p_nameShort,error))            	            		
        
        self.reset()        
        
    def release(self):
        """
        Store current data to return buffers
        """                
        #Only store return values on release
        if self._posBuffer:
            for p in self._posBuffer:
                self.l_return.append(p)            
        if self._createModeBuffer:
            self.l_created.extend(self._createModeBuffer)
            
        if self._posBuffer:
            log.debug("Position data : %s "%(self.l_return))
        if self._createModeBuffer:
            log.debug("Created : %s "%(self._createModeBuffer))
            mc.select(cl=True)
	    if 'joint' in self._createMode:
		jntUtils.metaFreezeJointOrientation(self._createModeBuffer)	
		
        if self.int_maxStore and len(self.l_return) == self.int_maxStore:
            log.debug("Max hit, finalizing")
            self.dropTool()
    
    def drag(self):
        """
        update positions
        """
        ContextualPick.drag(self)
        self.updatePos()
        
        if self._createModeBuffer:
            self.l_created.extend(self._createModeBuffer)          
            
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
	_str_funcName = 'clickMesh.updatePos'
	log.debug(">>> %s >> "%_str_funcName + "="*75)     	
        if not self.l_mesh:
            return log.warning("No mesh objects have been added to '%s'"%(self.name))
        
        buffer =  screenToWorld(int(self.x),int(self.y))#get world point and vector!
                
        self.clickPos = buffer[0] #Our world space click point
        self.clickVector = buffer[1] #Camera vector
        self._posBuffer = []#Clear our pos buffer
        
        for m in self.l_mesh:#Get positions per mesh piece
            #First get the distance to try to check
            checkDistance = self.getDistanceToCheck(m)
            #print ("Checking distance of %s"%checkDistance)
            if m not in self.d_meshPos.keys():
                self.d_meshPos[m] = []
                self.d_meshUV[m] = []
                
            if mc.objExists(m):
                if self.mode == 'surface':
		    try:buffer = RayCast.findMeshIntersection(m, self.clickPos , self.clickVector, checkDistance)   
		    except StandardError,error:
			buffer = None
			log.error("%s >>> cast fail. More than likely, the offending face lacks uv's. Error: %s"%(_str_funcName,error))
                    if buffer is not None:
                        hit = self.convertPosToLocalSpace( buffer['hit'] )
                        self._posBuffer.append(hit)  
                        self.startPoint = self.convertPosToLocalSpace( buffer['source'] )
                        self.d_meshPos[m].append(hit)
                        self.d_meshUV[m].append(buffer['uv'])
			
                else:
                    buffer = RayCast.findMeshIntersections(m, self.clickPos , self.clickVector , checkDistance)                                    
                    if buffer:
                        conversionBuffer = []
                        #Need to convert to local space
                        for hit in buffer['hits']:
                            conversionBuffer.append(self.convertPosToLocalSpace( hit ))
                             
                        self._posBuffer.extend(conversionBuffer)
                        self.startPoint = self.convertPosToLocalSpace( buffer['source'] )
                        
                        self.d_meshPos[m].extend(conversionBuffer)
                        self.d_meshUV[m].extend(buffer['uvs'])
			
        if not self._posBuffer:
            log.warning('No hits detected!')
            return
        
        if self.b_clampSetting and self.b_clampSetting < len(self._posBuffer):
            log.warning("Position buffer was clamped. Check settings if this was not desired.")
            self._posBuffer = distance.returnPositionDataDistanceSortedList(self.startPoint,self._posBuffer)
            self._posBuffer = self._posBuffer[:self.b_clampSetting]
            
        if self.mode == 'midPoint':                
            self._posBuffer = [distance.returnAveragePointPosition(self._posBuffer)]

        if self._posBuffer: #Check for closest and just for hits
            if self.b_closestOnly and self.mode != 'intersections':
                buffer = distance.returnClosestPoint(self.startPoint,self._posBuffer)
                self._posBuffer = [buffer]                 
        else:pass
            #log.warning("No hits detected")
            
        #>>> Make our stuff ======================================================
        if self._createMode and self._posBuffer: # Make our stuff
            #Delete the old stuff
            if self._createModeBuffer and not self.b_dragStoreMode:
                for o in self._createModeBuffer:
                    try:mc.delete(o)
                    except:pass
                self._createModeBuffer = []
            
            for i,pos in enumerate(self._posBuffer):
		for i2,v in enumerate(self.v_clampValues):
		    if v is not None:
			pos[i2] = v
		#Let's make our stuff
                if len(pos) == 3:
                    baseScale = distance.returnMayaSpaceFromWorldSpace(10)
                    if self._createMode == 'joint':
                        nameBuffer = mc.joint(radius = 1)
                        #attributes.doSetAttr(nameBuffer,'radius',1)
                        mc.select(cl=True)
                    else:
                        nameBuffer = mc.spaceLocator()[0]
			
		    mc.move (pos[0],pos[1],pos[2], nameBuffer)
		    
		    for m in self.d_meshPos.keys():#check each mesh dictionary to see where it came from
			if pos in self.d_meshPos[m]:#if the mesh has a match
			    attributes.storeInfo(nameBuffer,'cgmHitTarget',m)
			    
			    #attributes.doSetAttr(nameBuffer,'localScaleX',(self.f_meshArea*.025))
			    #attributes.doSetAttr(nameBuffer,'localScaleY',(self.f_meshArea*.025))
			    #attributes.doSetAttr(nameBuffer,'localScaleZ',(self.f_meshArea*.025))
			    
			    if self.v_posOffset is not None and self.v_posOffset and nameBuffer and self.str_offsetMode and self._createMode not in ['follicle']:
				mi_obj = cgmMeta.cgmObject(nameBuffer)
				mc.move (pos[0],pos[1],pos[2], mi_obj.mNode,ws=True)	
				if self.str_offsetMode =='vector':
				    mi_hitLoc = cgmMeta.cgmObject(mc.spaceLocator(n='hitLoc')[0])
				    mc.move (self.startPoint[0],self.startPoint[1],self.startPoint[2], mi_hitLoc.mNode,ws=True)				
				    constBuffer = mc.aimConstraint(mi_hitLoc.mNode,mi_obj.mNode,
				                                   aimVector=[0,0,1],
				                                   upVector=[0,1,0],
				                                   worldUpType = 'scene')
				    mi_hitLoc.delete()
				else:
				    constBuffer = mc.normalConstraint(m,mi_obj.mNode,
				                                      aimVector=[0,0,1],
				                                      upVector=[0,1,0],
				                                      worldUpType = 'scene')
				try:mc.delete(constBuffer)
				except:pass
				try:mc.move(self.v_posOffset[0],self.v_posOffset[1],self.v_posOffset[2], [mi_obj.mNode], r=True, rpr = True, os = True, wd = True)
				except StandardError,error:log.error("%s >>> Failed to move! | self.v_posOffset: %s | mi_obj: %s | error: %s"%(_str_funcName,self.v_posOffset,mi_obj,error))				
				self._posBuffer[i] = mi_obj.getPosition()  
				if not self.b_orientSnap:
				    mi_obj.rotate = [0,0,0]
				#mi_tmpLoc.delete()			    
			    
			    break                              
                                            
                    if self.l_toCreate:#Name it
                        nameBuffer = mc.rename(nameBuffer,self.l_toCreate[len(self.l_return)])
                    
                    self._createModeBuffer.append(nameBuffer)
                else:
		    
                    log.warning("'%s' isn't a valid position"%pos)      
		    
        if self.b_dragStoreMode:
            if self._posBuffer:
                for p in self._posBuffer:
                    self.l_return.append(p)  
               
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
    posMPoint = om.MPoint() #Storage items
    vecMVector = om.MVector()

    success = activeView.viewToWorld(startX, startY, posMPoint, vecMVector ) # The function
            
    return [posMPoint.x,posMPoint.y,posMPoint.z],[vecMVector.x,vecMVector.y,vecMVector.z]
