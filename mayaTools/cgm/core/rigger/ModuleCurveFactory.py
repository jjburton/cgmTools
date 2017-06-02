"""
Module for building controls for cgmModules

"""
# From Python =============================================================
import copy
import re

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.core.classes import SnapFactory as Snap
from cgm.core.lib import rayCaster as RayCast

from cgm.lib import (cgmMath,
                     locators,
                     modules,
                     distance,
                     dictionary,
                     rigging,
                     search,
                     curves,
                     lists,
                     )

from cgm.core.lib import nameTools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    @r9General.Timer
    def __init__(self,moduleInstance,controlTypes = [],targetObjects = [],storageInstance = False,midSplits = None,**kws): 
        """
	Class factor generating module controls
	
        @kws
	moduleInstance -- must be a module instance
        """
	self.d_controlBuildFunctions = {'cog':self.build_cog,
	                                'hips':self.build_hips,
	                                'segmentFK':self.build_segmentFKHandles,
	                                'segmentIK':self.build_segmentIKHandles,
	                                'segmentFK_Loli':self.build_segmentFKLoliHandles,
	                                'torsoIK':self.build_torsoIKHandles,
	                                'loliHandles':self.build_loliHandles,
	                                'midIK':self.build_midIKHandle,
	                                'footPivots':self.build_footPivots,
	                                'foot':self.build_footShape,
	                                'settings':self.build_settings}
        # Get our base info
        #==============	        
        #>>> module null data
        if not issubclass(type(moduleInstance),cgmPM.cgmModule):
            log.error("Not a cgmModule: '%s'"%moduleInstance)
            return 
	if not mc.objExists(moduleInstance.mNode):
	    raise StandardError,"RigFactory.go.init Module instance no longer exists: '%s'"%moduleInstance
	
	if type(controlTypes) is not list:controlTypes = [controlTypes]
        assert moduleInstance.isTemplated(),"Module is not templated: '%s'"%moduleInstance.getShortName()        
        #assert moduleInstance.isSkeletonized(),"Module is not skeletonized: '%s'"%moduleInstance.getShortName()
        
        log.debug(">>> ModuleControlFactory.go.__init__")
        self._mi_module = moduleInstance# Link for shortness	
        """
        if moduleInstance.hasControls():
            if forceNew:
                deleteControls(moduleInstance)
            else:
                log.warning("'%s' has already been skeletonized"%moduleInstance.getShortName())
                return        
        """
        #>>> Gather info
        #=========================================================
	self._midSplits = midSplits
        self.l_moduleColors = self._mi_module.getModuleColors()
        self.l_coreNames = self._mi_module.coreNames.value
        self.mi_templateNull = self._mi_module.templateNull#speed link
	self.mi_rigNull = self._mi_module.rigNull#speed link
        self._targetMesh = self._mi_module.modulePuppet.getGeo()[0] or 'Morphy_Body_GEO1'#>>>>>>>>>>>>>>>>>this needs better logic   
	self.ml_targetObjects = cgmMeta.validateObjListArg(targetObjects, cgmMeta.cgmObject,noneValid=True)
        #>>> part name 
        self._partName = self._mi_module.getPartNameBase()
        self._partType = self._mi_module.moduleType or False
	
        self._direction = None
        if self._mi_module.hasAttr('cgmDirection'):
            self._direction = self._mi_module.cgmDirection or None
               
        #>>> Instances and joint stuff
        self._jointOrientation = str(modules.returnSettingsData('jointOrientation')) or 'zyx'#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<   
	self.l_controlSnapObjects = []
	for mi_obj in self.mi_templateNull.controlObjects:
	    self.l_controlSnapObjects.append(mi_obj.helper.mNode)  
	self._skinOffset = self._mi_module.modulePuppet.getAttr('skinDepth') or 1 #Need to get from puppet!<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	self.l_segmentControls = []
	self.l_segmentHandles = []
	self.l_indexPairs = lists.parseListToPairs(list(range(len(self.l_controlSnapObjects))))
	self.l_segments = lists.parseListToPairs(self.l_controlSnapObjects)		
	self.d_returnControls = {}	
	self.md_ReturnControls = {}	
	self.d_returnPivots = {}		
	self.md_returnPivots = {}   
	self.md_fkControls = {}
	self.md_segmentHandles = {}
	
        #>>> We need to figure out which control to make
	#===================================================================================
	self.l_controlsToMakeArg = []	
	
	if controlTypes:#If we get an override
	    for c in controlTypes:
		if self.validateControlArg(c):
		    self.l_controlsToMakeArg.append(c)
	else:
	    if not self._mi_module.getMessage('moduleParent'):
		self.l_controlsToMakeArg.append('cog')
	    #if self.mi_rigNull.ik:
		#self.l_controlsToMakeArg.extend(['vectorHandles'])
		#if self._partType == 'torso':#Maybe move to a dict?
		    #self.l_controlsToMakeArg.append('spineIKHandle')            
	    if self.mi_rigNull.fk:
		self.l_controlsToMakeArg.extend(['segmentFK','segmentIK'])
		if self._partType == 'torso':#Maybe move to a dict?
		    self.l_controlsToMakeArg.extend(['hips','torsoIK'])
		    if 'segmentIK' in self.l_controlsToMakeArg:self.l_controlsToMakeArg.remove('segmentIK')
		    #We don't need segmentIK because we have special torsoIK handles
		    
	log.debug("l_controlsToMakeArg: %s"%self.l_controlsToMakeArg)
	    
	#self.d_controlShapes = mControlFactory.limbControlMaker(self.m,self.l_controlsToMakeArg)
	
	for key in self.l_controlsToMakeArg:
	    self.d_controlBuildFunctions[key]()#Run it
	    #if key not in self.d_returnControls:
		#log.warning("Necessary control shape(s) was not built: '%s'"%key)
		#raise StandardError,"Did not get all necessary controls built"
	if storageInstance:
	    try:
		storageInstance._d_controlShapes = self.d_returnControls
		storageInstance._md_controlShapes = self.md_ReturnControls
		storageInstance._md_fkControls = self.md_fkControls
		storageInstance._md_controlPivots = self.md_returnPivots
		
		
	    except StandardError,error:
		log.error("storage fail! | %s"%storageInstance) 
		raise StandardError,"Did not get all necessary controls built"

    def validateControlArg(self,arg):
	"""returns function"""
	if arg in self.d_controlBuildFunctions.keys():
	    return True
	log.warning("validateControlArg couldn't find: %s"%arg)
	return False
    
    @r9General.Timer    
    def build_cog(self):
	try:
	    multiplier = 1.1
	    tmplRoot = self.mi_templateNull.root.mNode
	    mi_loc = cgmMeta.cgmNode(tmplRoot).doLoc()#make loc for sizing
	    mi_loc.doGroup()#group to zero
	    sizeReturn = returnBaseControlSize(mi_loc,self._targetMesh,axis=['x','y'])#Get size
	    l_size = [sizeReturn['x']+(self._skinOffset*2),sizeReturn['y']+(self._skinOffset*2)]
	    mc.delete(mi_loc.parent)#delete loc
	    
	    size = max(l_size)/2.5
	    ml_curvesToCombine = []
	    mi_crvBase = cgmMeta.asMeta( curves.createControlCurve('arrowSingleFat3d',direction = 'y-',size = size,absoluteSize=False),'cgmObject', setClass=True)
	    mi_crvBase.scaleY = 2
	    mi_crvBase.scaleZ = .75
	    Snap.go(mi_crvBase, tmplRoot) #Snap it
	    i_grp = cgmMeta.cgmObject( mi_crvBase.doGroup() )
	    
	    for i,rot in enumerate([0,90,90,90]):
		#rot, shoot, move, dup
		log.debug("curve: %s | rot int: %s | grp: %s"%(mi_crvBase.mNode,i, i_grp.mNode))
		i_grp.rotateY = i_grp.rotateY + rot
		#Shoot
		d_return = RayCast.findMeshIntersectionFromObjectAxis(self._targetMesh,mi_crvBase.mNode)
		if not d_return.get('hit'):
		    raise StandardError,"build_cog>>failed to get hit. Master template object probably isn't in mesh"
		log.debug("hitDict: %s"%d_return)
		dist = distance.returnDistanceBetweenPoints(mi_crvBase.getPosition(),d_return['hit'])+(self._skinOffset*10)
		log.debug("dist: %s"%dist)
		log.debug("crv: %s"%mi_crvBase.mNode)
		mi_crvBase.__setattr__("tz",dist)
		mi_tmp = mi_crvBase.doDuplicate(parentOnly=False)
		log.debug(mi_tmp)
		mi_tmp.parent = False
		ml_curvesToCombine.append(mi_tmp)
		mi_crvBase.__setattr__("tz",0)
	    
	    i_grp.delete()
	    mi_crv = cgmMeta.cgmObject( curves.combineCurves([i_obj.mNode for i_obj in ml_curvesToCombine]) )
	    log.debug("mi_crv: %s"%mi_crv.mNode)
	    #>>Copy tags and name
	    mi_crv.addAttr('cgmName',attrType='string',value = 'cog',lock=True)        
	    mi_crv.addAttr('cgmType',attrType='string',value = 'controlCurve',lock=True)
	    mi_crv.doName()        
    
	    mc.xform(mi_crv.mNode, cp=True)
	    mc.makeIdentity(mi_crv.mNode, apply=True,s=1,n=0)	
    
	    #>>> Color
	    curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])    
	    self.d_returnControls['cog'] = mi_crv.mNode
	    self.md_ReturnControls['cog'] = mi_crv
	    
	    
	except StandardError,error:
		log.error("build_cog fail! | %s"%error) 
		return False
    
    @r9General.Timer    
    def build_cog2(self):
	try:
	    multiplier = 1.1
	    tmplRoot = self.mi_templateNull.root.mNode
	    mi_loc = cgmMeta.cgmNode(tmplRoot).doLoc()#make loc for sizing
	    mi_loc.doGroup()#group to zero
	    sizeReturn = returnBaseControlSize(mi_loc,self._targetMesh,axis=['x','y'])#Get size
	    l_size = [sizeReturn['x']+(self._skinOffset*2),sizeReturn['y']+(self._skinOffset*2)]
	    mc.delete(mi_loc.parent)#delete loc
	    
	    mi_crv = cgmMeta.cgmObject( curves.createControlCurve('circleArrow',direction = 'y+',size = max(l_size),absoluteSize=False))
	    Snap.go(mi_crv, tmplRoot) #Snap it
	    
	    #>>Copy tags and name
	    mi_crv.addAttr('cgmName',attrType='string',value = 'cog',lock=True)        
	    mi_crv.addAttr('cgmType',attrType='string',value = 'controlCurve',lock=True)
	    mi_crv.doName()        
    
	    #>>> Color
	    curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])    
	    self.d_returnControls['cog'] = mi_crv.mNode
	    self.md_ReturnControls['cog'] = mi_crv
	except StandardError,error:
		log.error("build_cog fail! | %s"%error) 
		return False
	
    def build_hips(self):
	distanceMult = .5	    
	orientHelper = self.l_controlSnapObjects[1]
	log.debug(orientHelper)
	mi_loc = cgmMeta.cgmNode(orientHelper).doLoc()#make loc for sizing
	mi_loc.doGroup()#group to zero
	
	d_return = RayCast.findMeshIntersectionFromObjectAxis(self._targetMesh,mi_loc.mNode,'z-')
	if not d_return.get('hit'):
	    raise StandardError,"build_cog>>failed to get hit. Master template object probably isn't in mesh"
	dist = distance.returnDistanceBetweenPoints(mi_loc.getPosition(),d_return['hit'])
	mi_loc.tz = -dist *.2	
	
	returnBuffer = createWrapControlShape(mi_loc.mNode,self._targetMesh,
                                              curveDegree=3,
                                              insetMult = .2,
                                              closedCurve=True,
	                                      points = 8,
                                              posOffset = [0,0,self._skinOffset*3],
                                              extendMode='')
	mi_crvRound = returnBuffer['instance']
	
	str_traceCrv = createMeshSliceCurve(self._targetMesh,mi_loc.mNode,
	                                    latheAxis='x',aimAxis='y+',
	                                    curveDegree=3,
	                                    closedCurve=False,
	                                    l_specifiedRotates=[0,-30,-60,-90,-120,-150,-180],
	                                    posOffset = [0,0,self._skinOffset*3],
	                                    )
	
	mi_crv = cgmMeta.cgmObject ( curves.combineCurves([mi_crvRound.mNode,str_traceCrv]) )
	
	mc.delete(mi_loc.getAllParents()[-1])
	
	#>>Copy tags and name
	mi_crv.addAttr('cgmName',attrType='string',value = 'hips',lock=True)        
	mi_crv.addAttr('cgmType',attrType='string',value = 'controlCurve',lock=True)
	mi_crv.doName()        
	
	#>>> Color
	curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])    
	self.d_returnControls['hips'] = mi_crv.mNode
	self.md_ReturnControls['hips'] = mi_crv
	
	
	
    
    	    
    @r9General.Timer    
    def build_segmentFKHandles(self):
	try:
	    l_segmentControls = []
	    l_iSegmentControls = []
	    if self._partType == 'torso':
		l_segmentsToDo = self.l_segments[1:-1]
	    else:
		l_segmentsToDo = self.l_segments
	    log.info("segments: %s"%l_segmentsToDo)
	    for i,seg in enumerate(l_segmentsToDo):	
		returnBuffer = createWrapControlShape(seg,self._targetMesh,
		                                      points = 10,
		                                      curveDegree=1,
		                                      insetMult = .2,
		                                      posOffset = [0,0,self._skinOffset*3],
		                                      joinMode=True,
		                                      joinHits = [0,2,4,6,8],
		                                      extendMode='segment')
		mi_crv = returnBuffer['instance']	    
		#>>> Color
		curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
		mi_crv.addAttr('cgmType',attrType='string',value = 'segFKCurve',lock=True)	
		mi_crv.doName()
		
		#Store for return
		l_segmentControls.append( mi_crv.mNode )
		l_iSegmentControls.append( mi_crv )
		if i ==1:raise StandardError
		
	    self.d_returnControls['segmentFK'] = l_segmentControls 
	    self.md_ReturnControls['segmentFK'] = l_iSegmentControls
	    
	except StandardError,error:
		log.error("build_segmentFKHandles fail! | %s"%error) 
		return False
	    
    @r9General.Timer    
    def build_segmentFKLoliHandles(self):
	try:
	    l_segmentControls = []
	    ml_segmentControls = []
	    if self._partType == 'torso':
		l_segmentsToDo = self.l_segments[1:-1]
	    else:
		l_segmentsToDo = self.l_segments
	    #figure out our settings
	    #================================================================
	    #defaults first
	    d_kws = {}
	    self.posOffset = []
	    self.l_specifiedRotates = None
	    self.joinMode = False
	    self.closedCurve = False
	    self.rotateBank = None
	    self.latheAxis = 'z'
	    self.aimAxis = 'y+'
	    self.rotateBank = None	
	    self.rootOffset = None
	    self.rootRotate = None
	    if 'neck' in self._partType:
		posOffset = [0,0,self._skinOffset*5]
		l_specifiedRotates = [-30,-10,0,10,30]
		latheAxis = 'z'
		aimAxis = 'y+'
	    elif 'leg' in self._partType:
		d_kws = {'default':{'closedCurve':False,
		                    'latheAxis':'z',
		                    'l_specifiedRotates':[-60,-40,-20,0,20,40,60],
		                    'rootOffset':[],
		                    'rootRotate':None},
		         0:{},
		         -2:{}}	
		d_kws[0]['l_specifiedRotates'] = [-110,-90,-60,-30,0,30,60,90,110]
		d_kws[0]['rootOffset'] = [0,0,self._skinOffset*8]	
		
		self.posOffset = [0,0,self._skinOffset*3]
		if self._direction == 'left':
		    self.aimAxis = 'x+'
		else:self.aimAxis = 'x-'
		
		
	    log.info("Snap Objects: %s"%self.l_controlSnapObjects)
	    for i,obj in enumerate(self.l_controlSnapObjects):			
		#make ball
		if d_kws:
		    if d_kws.get(i):
			for k in d_kws[i].keys():
			    self.__dict__[k] = d_kws[i].get(k)
		    elif i == len(self.l_controlSnapObjects)-1 and d_kws.get(-1):
			log.info('last mode')
			for k in d_kws[-1].keys():
			    self.__dict__[k] = d_kws[-1].get(k)
		    else:
			for k in d_kws['default'].keys():
			    self.__dict__[k] = d_kws['default'].get(k)
			    
		#Few more special cases
		if cgmMeta.cgmObject(obj).getAttr('cgmName') in ['ankle']:
		    log.info('Special rotate mode')
		    self.rootRotate = [0,0,0]
		    self.latheAxis = 'y'
		returnBuffer = createWrapControlShape(obj,self._targetMesh,
	                                              curveDegree=3,
	                                              insetMult = .2,
		                                      closedCurve= self.closedCurve,
		                                      aimAxis = self.aimAxis,
		                                      latheAxis = self.latheAxis,
		                                      l_specifiedRotates = self.l_specifiedRotates,
	                                              posOffset = self.posOffset,
		                                      rootOffset = self.rootOffset,
		                                      rootRotate = self.rootRotate,
	                                              extendMode='loliwrap')
		mi_newCurve = returnBuffer['instance']
		mi_newCurve.doCopyPivot(obj)
		#>>> Color
		curves.setCurveColorByName(mi_newCurve.mNode,self.l_moduleColors[0])                    
		mi_newCurve.addAttr('cgmType',attrType='string',value = 'loliHandle',lock=True)	
		mi_newCurve.doName()
		
		#Store for return
		l_segmentControls.append( mi_newCurve.mNode )
		ml_segmentControls.append( mi_newCurve )		
		
	    self.d_returnControls['segmentFK_Loli'] = l_segmentControls 
	    self.md_ReturnControls['segmentFK_Loli'] = ml_segmentControls
	    
	except StandardError,error:
		log.error("build_segmentIKHandles fail! | %s"%error) 
		return False
	    
    @r9General.Timer	
    def build_midIKHandle(self):
	try:
	    l_segmentControls = []
	    ml_segmentControls = []

	    mi_mid = False
	    if 'arm' in self._partType:
		for obj in self.l_controlSnapObjects:
		    if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'elbow':
			mi_mid = cgmMeta.cgmObject(obj)
			break
	    if 'leg' in self._partType:
		for obj in self.l_controlSnapObjects:
		    if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'knee':
			mi_mid = cgmMeta.cgmObject(obj)
			break   
	    if not mi_mid:
		raise StandardError, "build_midIKHandle>>> currently needs an arm or leg"
		
	    #figure out our settings
	    #================================================================
	    #defaults first


	    returnBuffer = createWrapControlShape(mi_mid.mNode,self._targetMesh,
	                                          points = 10,
	                                          curveDegree=3,
	                                          insetMult = .5,
	                                          posOffset = [0,0,self._skinOffset*3],
	                                          joinMode=True,
	                                          joinHits = [0,5],
	                                          extendMode='cylinder')
	    
	    mi_newCurve = returnBuffer['instance']
	    mi_newCurve.doCopyPivot(obj)
	    #>>> Color
	    curves.setCurveColorByName(mi_newCurve.mNode,self.l_moduleColors[0])                    
	    mi_newCurve.addAttr('cgmType',attrType='string',value = 'loliHandle',lock=True)	
	    mi_newCurve.doName()
	    
	    #Store for return
	    l_segmentControls.append( mi_newCurve.mNode )
	    ml_segmentControls.append( mi_newCurve )		
		
	    self.d_returnControls['midIK'] = mi_newCurve.mNode 
	    self.md_ReturnControls['midIK'] = mi_newCurve
	    
	except StandardError,error:
		log.error("build_midIKHandle fail! | %s"%error) 
		return False
	    
    @r9General.Timer	
    def build_loliHandles(self):
	#Target objects expected
	if not self.ml_targetObjects:raise StandardError,"build_loliHandles requires target objects"
	
	try:
	    l_controls = []
	    ml_controls = []

	    for i,i_target in enumerate(self.ml_targetObjects):	
		d_size = returnBaseControlSize(i_target,self._targetMesh,axis=[self._jointOrientation[1],self._jointOrientation[2]])#Get size			
		l_size = [d_size[self._jointOrientation[1]],d_size[self._jointOrientation[2]]]
		size = sum(l_size)/1.5
		
		log.debug("loli size return: %s"%d_size)
		log.debug("loli size: %s"%size)
		i_ball = cgmMeta.cgmObject(curves.createControlCurve('sphere',size = size/4))
		Snap.go(i_ball,i_target.mNode,True, True)#Snap to main object
		
		#make ball
		returnBuffer = createWrapControlShape(i_target.mNode,self._targetMesh,
	                                              curveDegree=3,
	                                              insetMult = .2,
		                                      closedCurve=False,
		                                      l_specifiedRotates = [-30,-10,0,10,30],
	                                              posOffset = [0,0,self._skinOffset*1.2],
	                                              extendMode='')
		mi_crv = returnBuffer['instance']
		l_eps = mi_crv.getComponents('ep')
		midIndex = int(len(l_eps)/2)
		log.debug("eps: %s"%l_eps)
		log.debug("mid: %s"%midIndex)
		
		#Move the ball
		pos = distance.returnWorldSpacePosition(l_eps[midIndex])
		mc.xform( i_ball.mNode, translation = pos, ws = True)#Snap to the mid ep
		mc.move(0,self._skinOffset*3,0,i_ball.mNode,relative = True,os=True)
		
		#Make the curve between the two 
		traceCurve = mc.curve(degree = 1, ep = [pos,i_ball.getPosition()])
		
		#Combine
		mi_newCurve = cgmMeta.cgmObject( curves.combineCurves([mi_crv.mNode,i_ball.mNode,traceCurve]) )
		
		#>>> Color
		curves.setCurveColorByName(mi_newCurve.mNode,self.l_moduleColors[0])                    
		mi_crv.addAttr('cgmType',attrType='string',value = 'loliHandle',lock=True)	
		mi_crv.doName()
		
		#Store for return
		l_controls.append( mi_newCurve.mNode )
		ml_controls.append( mi_newCurve )
		
	    self.d_returnControls['loliHandles'] = l_controls 
	    self.md_ReturnControls['loliHandles'] = ml_controls
		
	except StandardError,error:
		log.error("build_loliHandles! | %s"%error) 
		return False
	     
    @r9General.Timer	
    def build_torsoIKHandles(self):
	try:
	    l_segmentControls = []
	    l_iSegmentControls = []
	    
	    l_segmentsToDo = self.l_segments[1:]

	    for i,seg in enumerate(l_segmentsToDo):
		returnBuffer = createWrapControlShape(seg,self._targetMesh,
		                                      points = 8,
		                                      curveDegree=3,
		                                      insetMult = .05,
		                                      posOffset = [0,0,self._skinOffset*3],
		                                      joinMode=True,
		                                      extendMode='disc')
		mi_crv = returnBuffer['instance']	    
		#>>> Color
		curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[1])                    
		mi_crv.addAttr('cgmType',attrType='string',value = 'segIKCurve',lock=True)	
		mi_crv.doName()
		
		#Store for return
		l_segmentControls.append( mi_crv.mNode )
		l_iSegmentControls.append( mi_crv )
		
	    self.d_returnControls['segmentIK'] = l_segmentControls 
	    self.md_ReturnControls['segmentIK'] = l_iSegmentControls
	    
	    if len(self.l_segments)>2:
		objects = self.l_controlSnapObjects[-2:]
	    else:
		objects = self.l_segments[-1]
	    returnBuffer = createWrapControlShape(self.l_segments[-1],self._targetMesh,
	                                          points = 10,
	                                          curveDegree=3,
	                                          insetMult = .05,
	                                          posOffset = [0,0,self._skinOffset*3],
	                                          joinHits = [0,2,4,6,8],	                                          
	                                          joinMode=True,
	                                          extendMode='segment')
	    mi_crv = returnBuffer['instance']	    
	    #>>> Color
	    curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
	    mi_crv.doCopyNameTagsFromObject(self.l_controlSnapObjects[-1],ignore = ['cgmType'])
	    mi_crv.addAttr('cgmType',attrType='string',value = 'ikCurve',lock=True)	    
	    mi_crv.doName()
		
	    self.d_returnControls['segmentIKEnd'] = mi_crv.mNode 		
	    self.md_ReturnControls['segmentIKEnd'] = mi_crv
		
	except StandardError,error:
		log.error("build_torsoIKHandles! | %s"%error) 
		return False
	    
    def build_settings(self):
	l_segmentControls = []
	ml_SegmentControls = []
	mi_footModule = False
	
	#Find our settings
	#============================================================================	
	self.latheAxis = self._jointOrientation[0]
	self.aimAxis = self._jointOrientation[1] + '-'
	self.outAxis = self._jointOrientation[2]
	self.posOffset = [0,0,self._skinOffset*6]
	self.gearVector = [0,0,-1]
	if self._partType == 'leg':
	    index = -2
	    self.settingsVector = [0,0,-1]	    
	else:
	    index = -1
	
	i_target = cgmMeta.cgmObject( self.l_controlSnapObjects[index] )
	mi_rootLoc = i_target.doLoc()
	
	d_size = returnBaseControlSize(mi_rootLoc,self._targetMesh,axis=[self.outAxis])#Get size
	baseSize = d_size.get(d_size.keys()[0])*.75
	log.info("build_settings>>> baseSize: %s"%baseSize)
		
	i_gear = cgmMeta.cgmObject(curves.createControlCurve('gear',size = baseSize,direction=self.outAxis+'+'))	
	
	#Move stuff
	Snap.go(i_gear.mNode,mi_rootLoc.mNode,True, False)#Snap to main object
	
	#Move the ball
	d_return = RayCast.findMeshIntersectionFromObjectAxis(self._targetMesh,mi_rootLoc.mNode,vector = self.settingsVector,singleReturn=True)
	if not d_return.get('hit'):
	    raise StandardError,"go.build_settings>>failed to get hit to measure distance"
	
	mc.move(d_return['hit'][0],d_return['hit'][1],d_return['hit'][2],i_gear.mNode,absolute = True,ws=True)
	Snap.go(i_gear.mNode,mi_rootLoc.mNode,move = False, orient = False, aim=True, aimVector=[0,0,-1])
	
	mc.move(self.posOffset[0]*1.5,self.posOffset[1]*1.5,self.posOffset[2]*1.5, [i_gear.mNode], r = True, rpr = True, os = True, wd = True)
    
	mi_rootLoc.delete()
	#Combine and finale
	#============================================================================
	
	i_gear.doCopyPivot(i_target.mNode)
	#>>> Color
	curves.setCurveColorByName(i_gear.mNode,self.l_moduleColors[0])                    
	#i_gear.doCopyNameTagsFromObject(i_target.mNode,ignore = ['cgmType'])
	i_gear.addAttr(self._partName,attrType='string',value = 'settings',lock=True)	    
	i_gear.addAttr('cgmType',attrType='string',value = 'settings',lock=True)	    
	i_gear.doName()
	    
	self.d_returnControls['settings'] = i_gear.mNode 		
	self.md_ReturnControls['settings'] = i_gear		
	
    def build_footPivots(self):
	"""
	build foot pivot locs 
	"""
	mi_footModule = False
	mi_ball = False
	mi_ankle = False
	
	#Find our foot
	#============================================================================	
	if self._partType == 'foot':
	    raise NotImplementedError,"haven't implemented foot"
	elif self._partType == 'legSimple':
	    #find the foot. 1) Build search dict
	    d_search = {'moduleType':'foot'}
	    for key in ['cgmDirection','cgmPosition']:
		buffer = self._mi_module.getAttr(key)
		if buffer:
		    d_search[key] = buffer
	    #Find it
	    mi_footModule = self._mi_module.modulePuppet.getModuleFromDict(d_search)
	    ml_children = self._mi_module.moduleChildren
	    if mi_footModule in ml_children:log.debug("found match modules: %s"%mi_footModule)
	    
	    ml_controlSnapObjects = []
	    for mi_obj in mi_footModule.templateNull.controlObjects:
		ml_controlSnapObjects.append(mi_obj.helper)  
	    log.debug("helperObjects: %s"%[i_obj.getShortName() for i_obj in ml_controlSnapObjects])
	    if ml_controlSnapObjects[1].cgmName != 'ball':
		raise StandardError,"go.build_footShape>>> Expected second snap object to be 'ball'. Found: %s"%ml_controlSnapObjects[1].mNode
	    mi_ball = ml_controlSnapObjects[1]
	    mi_ankle = ml_controlSnapObjects[0]
	    
	elif self._partType == 'leg':
	    for obj in self.l_controlSnapObjects:
		if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'ankle':
		    mi_ankle = cgmMeta.cgmObject(obj)
		    break
	    for obj in self.l_controlSnapObjects:
		if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'ball':
		    mi_ball = cgmMeta.cgmObject(obj)
		    break
		
	if not mi_ball and not mi_ankle:
	    raise StandardError,"go.build_footShape>>> Haven't found a foot module to build from"
	
	#Get our helper objects
	#============================================================================
	mi_heelLoc = mi_ankle.doLoc()
	mi_ballLoc = mi_ball.doLoc()
	mi_heelLoc.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_heelLoc.__setattr__('t%s'%self._jointOrientation[1],mi_ballLoc.getAttr('t%s'%self._jointOrientation[1]))
	
	#Get our distance for our front cast
	
	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,self._jointOrientation[0]+'+',pierceDepth=self._skinOffset*15) or {}
	if not d_return.get('hit'):
	    raise StandardError,"go.build_footShape>>failed to get hit to measure first distance"
	dist = distance.returnDistanceBetweenPoints(mi_ballLoc.getPosition(),d_return['hit']) *1.5
	log.debug("go.build_footShape>>front distance: %s"%dist)
	
	#Pivots
	#===================================================================================
	#Ball pivot
	mi_ballPivot = mi_ballLoc.doLoc()
	mi_ballPivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_ballPivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_ballPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_ballPivot.doName()
	self.d_returnPivots['ball'] = mi_ballPivot.mNode 		
	self.md_returnPivots['ball'] = mi_ballPivot	
	
	#Toe pivot
	mi_toePivot =  mi_ballLoc.doLoc()
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_toePivot.mNode)
	mi_toePivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_toePivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_toePivot.addAttr('cgmName','toe',lock=True)	
	mi_toePivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_toePivot.doName()	
	#mc.rotate (objRot[0], objRot[1], objRot[2], str_pivotToe, ws=True)	
	self.d_returnPivots['toe'] = mi_toePivot.mNode 		
	self.md_returnPivots['toe'] = mi_toePivot	
	
	#Inner bank pivots
	if self._direction == 'left':
	    innerAim = self._jointOrientation[2]+'-'
	    outerAim = self._jointOrientation[2]+'+'
	    
	else:
	    innerAim = self._jointOrientation[2]+'+'
	    outerAim = self._jointOrientation[2]+'-'
	    
	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,innerAim,pierceDepth=self._skinOffset*5) or {}
	if not d_return.get('hit'):
	    raise StandardError,"go.build_footShape>>failed to get inner bank hit"	
	mi_innerPivot =  mi_ballLoc.doLoc()
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_innerPivot.mNode)
	mi_innerPivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_innerPivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_innerPivot.addAttr('cgmName','ball',lock=True)	
	mi_innerPivot.addAttr('cgmDirectionModifier','inner',lock=True)		    
	mi_innerPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_innerPivot.doName()		
	self.d_returnPivots['inner'] = mi_innerPivot.mNode 		
	self.md_returnPivots['inner'] = mi_innerPivot	
	
	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,outerAim,pierceDepth=self._skinOffset*5) or {}
	if not d_return.get('hit'):
	    raise StandardError,"go.build_footShape>>failed to get inner bank hit"	
	mi_outerPivot =  mi_ballLoc.doLoc()
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_outerPivot.mNode)
	mi_outerPivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_outerPivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_outerPivot.addAttr('cgmName','ball',lock=True)	
	mi_outerPivot.addAttr('cgmDirectionModifier','outer',lock=True)		    	    
	mi_outerPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_outerPivot.doName()	
	self.d_returnPivots['outer'] = mi_outerPivot.mNode 		
	self.md_returnPivots['outer'] = mi_outerPivot	
	
	#Heel pivot
	mi_heelPivot =  mi_heelLoc.doLoc()
	mi_heelPivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_heelPivot.__setattr__('t%s'%self._jointOrientation[1],.25)
	
	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_heelPivot.mNode,self._jointOrientation[0]+'-',pierceDepth=self._skinOffset*5) or {}
	if not d_return.get('hit'):
	    raise StandardError,"go.build_footShape>>failed to get inner bank hit"	
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_heelPivot.mNode)
	mi_heelPivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_heelPivot.addAttr('cgmName','heel',lock=True)	
	mi_heelPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_heelPivot.doName()		
	self.d_returnPivots['heel'] = mi_heelPivot.mNode 		
	self.md_returnPivots['heel'] = mi_heelPivot		
	
	mi_ballLoc.delete()
	mi_heelLoc.delete()
	
	#Store em all
	self.mi_templateNull.connectChildNode(mi_toePivot,'pivot_toe','module')
	self.mi_templateNull.connectChildNode(mi_heelPivot,'pivot_heel','module')
	self.mi_templateNull.connectChildNode(mi_ballPivot,'pivot_ball','module')
	self.mi_templateNull.connectChildNode(mi_innerPivot,'pivot_inner','module')
	self.mi_templateNull.connectChildNode(mi_outerPivot,'pivot_outer','module')
	
	#Parent
	for p in mi_toePivot,mi_heelPivot,mi_ballPivot,mi_innerPivot,mi_outerPivot:
	    p.parent = self.mi_templateNull.mNode	
		
    def build_footShape(self):
	"""
	build foot shape and pivot locs at the same time
	"""
	l_segmentControls = []
	ml_SegmentControls = []
	mi_footModule = False
	mi_ball = False
	mi_ankle = False
	
	#Find our foot
	#============================================================================	
	if self._partType == 'foot':
	    raise NotImplementedError,"haven't implemented foot"
	elif self._partType == 'legSimple':
	    #find the foot. 1) Build search dict
	    d_search = {'moduleType':'foot'}
	    for key in ['cgmDirection','cgmPosition']:
		buffer = self._mi_module.getAttr(key)
		if buffer:
		    d_search[key] = buffer
	    #Find it
	    mi_footModule = self._mi_module.modulePuppet.getModuleFromDict(d_search)
	    ml_children = self._mi_module.moduleChildren
	    if mi_footModule in ml_children:log.info("found match modules: %s"%mi_footModule)
	    
	    ml_controlSnapObjects = []
	    for mi_obj in mi_footModule.templateNull.controlObjects:
		ml_controlSnapObjects.append(mi_obj.helper)  
	    log.info("helperObjects: %s"%[i_obj.getShortName() for i_obj in ml_controlSnapObjects])
	    if ml_controlSnapObjects[1].cgmName != 'ball':
		raise StandardError,"go.build_footShape>>> Expected second snap object to be 'ball'. Found: %s"%ml_controlSnapObjects[1].mNode
	    mi_ball = ml_controlSnapObjects[1]
	    mi_ankle = ml_controlSnapObjects[0]
	    
	elif self._partType == 'leg':
	    for obj in self.l_controlSnapObjects:
		if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'ankle':
		    mi_ankle = cgmMeta.cgmObject(obj)
		    break
	    for obj in self.l_controlSnapObjects:
		if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'ball':
		    mi_ball = cgmMeta.cgmObject(obj)
		    break
		
	if not mi_ball and not mi_ankle:
	    raise StandardError,"go.build_footShape>>> Haven't found a foot module to build from"
	
	#Get our helper objects
	#============================================================================
	mi_heelLoc = mi_ankle.doLoc()
	mi_ballLoc = mi_ball.doLoc()
	mi_heelLoc.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_heelLoc.__setattr__('t%s'%self._jointOrientation[1],mi_ballLoc.getAttr('t%s'%self._jointOrientation[1]))
	
	#Get our distance for our front cast
	
	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,self._jointOrientation[0]+'+',pierceDepth=self._skinOffset*15) or {}
	if not d_return.get('hit'):
	    raise StandardError,"go.build_footShape>>failed to get hit to measure first distance"
	dist = distance.returnDistanceBetweenPoints(mi_ballLoc.getPosition(),d_return['hit']) *1.5
	log.info("go.build_footShape>>front distance: %s"%dist)
	
	#Pivots
	#===================================================================================
	#Ball pivot
	mi_ballPivot = mi_ballLoc.doLoc()
	mi_ballPivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_ballPivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_ballPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_ballPivot.doName()
	self.d_returnPivots['ball'] = mi_ballPivot.mNode 		
	self.md_returnPivots['ball'] = mi_ballPivot	
	
	#Toe pivot
	mi_toePivot =  mi_ballLoc.doLoc()
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_toePivot.mNode)
	mi_toePivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_toePivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_toePivot.addAttr('cgmName','toe',lock=True)	
	mi_toePivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_toePivot.doName()	
	#mc.rotate (objRot[0], objRot[1], objRot[2], str_pivotToe, ws=True)	
	self.d_returnPivots['toe'] = mi_toePivot.mNode 		
	self.md_returnPivots['toe'] = mi_toePivot	
	
	#Inner bank pivots
	if self._direction == 'left':
	    innerAim = self._jointOrientation[2]+'-'
	    outerAim = self._jointOrientation[2]+'+'
	    
	else:
	    innerAim = self._jointOrientation[2]+'+'
	    outerAim = self._jointOrientation[2]+'-'
	    
	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,innerAim,pierceDepth=self._skinOffset*5) or {}
	if not d_return.get('hit'):
	    raise StandardError,"go.build_footShape>>failed to get inner bank hit"	
	mi_innerPivot =  mi_ballLoc.doLoc()
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_innerPivot.mNode)
	mi_innerPivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_innerPivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_innerPivot.addAttr('cgmName','inner',lock=True)	
	mi_innerPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_innerPivot.doName()		
	self.d_returnPivots['inner'] = mi_innerPivot.mNode 		
	self.md_returnPivots['inner'] = mi_innerPivot	
	
	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_ballLoc.mNode,outerAim,pierceDepth=self._skinOffset*5) or {}
	if not d_return.get('hit'):
	    raise StandardError,"go.build_footShape>>failed to get inner bank hit"	
	mi_outerPivot =  mi_ballLoc.doLoc()
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_outerPivot.mNode)
	mi_outerPivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_outerPivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_outerPivot.addAttr('cgmName','outer',lock=True)	
	mi_outerPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_outerPivot.doName()	
	self.d_returnPivots['outer'] = mi_outerPivot.mNode 		
	self.md_returnPivots['outer'] = mi_outerPivot	
	
	#Heel pivot
	mi_heelPivot =  mi_heelLoc.doLoc()
	mi_heelPivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_heelPivot.__setattr__('t%s'%self._jointOrientation[1],.25)
	
	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_heelPivot.mNode,self._jointOrientation[0]+'-',pierceDepth=self._skinOffset*5) or {}
	if not d_return.get('hit'):
	    raise StandardError,"go.build_footShape>>failed to get inner bank hit"	
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_heelPivot.mNode)
	mi_heelPivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_heelPivot.addAttr('cgmName','heel',lock=True)	
	mi_heelPivot.addAttr('cgmTypeModifier','pivot',lock=True)
	mi_heelPivot.doName()		
	self.d_returnPivots['heel'] = mi_heelPivot.mNode 		
	self.md_returnPivots['heel'] = mi_heelPivot		
    
	#Cast our stuff
	#============================================================================
	self.posOffset = [0,0,self._skinOffset*3]
	self.latheAxis = self._jointOrientation[1]
	self.aimAxis = self._jointOrientation[0] + '+'
	
	if self._direction == 'left':
	    l_specifiedRotates = [-40,-20,0,20,60,80]
	    
	else:
	    l_specifiedRotates = [40,20,0,-20,-60,-80]
	    
	d_return = createMeshSliceCurve(self._targetMesh,mi_ballLoc.mNode,offsetMode='vector',maxDistance = dist,l_specifiedRotates = l_specifiedRotates,
	                                closedCurve = False,curveDegree=1,posOffset = self.posOffset,returnDict = True,
	                                latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=False)
	str_frontCurve = d_return['curve']
	
	
	#Heel cast

	self.aimAxis = self._jointOrientation[0] + '-'	
	if self._direction == 'left':
	    l_specifiedRotates = [-90,-60,-20,-10,0,10,20,40,60,80]#foot back, closed false, closest in range false
	    
	else:
	    l_specifiedRotates = [90,60,20,10,0,-10,-20,-40,-60,-80]
	d_return = createMeshSliceCurve(self._targetMesh,mi_heelLoc.mNode,offsetMode='vector',maxDistance = 1000,l_specifiedRotates = l_specifiedRotates,
	                                closedCurve = False,curveDegree=1,posOffset = self.posOffset,returnDict = True,
	                                latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=True)
	str_backCurve = d_return['curve']
	
	#side cast
	self.aimAxis = self._jointOrientation[0] + '+'
	if self._direction == 'left':
	    l_specifiedRotates = [-100,-80,-50]#foot front closest, closed false, closest in range true
	    
	else:
	    l_specifiedRotates =  [-50,-80,-100]	
	d_return = createMeshSliceCurve(self._targetMesh,mi_ballLoc.mNode,offsetMode='vector',maxDistance = 1000,l_specifiedRotates = l_specifiedRotates,
	                                closedCurve = False,curveDegree=1,posOffset = self.posOffset,returnDict = True,
	                                latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=True)
	str_sideCurve = d_return['curve']
	
	#Let's collect the points of the curves
	l_pos = []
	l_basePos = []
	ballY = distance.returnWorldSpacePosition(mi_ballLoc.mNode)[1]/2
	log.info("ballY: %s"%ballY)
	for crv in [str_frontCurve,str_backCurve,str_sideCurve]:
	    for ep in cgmMeta.cgmNode(crv).getComponents('ep'):
		buffer = distance.returnWorldSpacePosition(ep)
		l_pos.append( [buffer[0],ballY,buffer[2]] )
		l_basePos.append( [buffer[0],0,buffer[2]] )
	    mc.delete(crv)

	l_pos.append(l_pos[0])#append to close loop
	l_basePos.append(l_basePos[0])#append to close loop
	mi_ballLoc.delete()
	mi_heelLoc.delete()	
		
	topCrv = mc.curve(degree = 3, ep = l_pos)
	baseCrv = mc.curve(degree = 3, ep = l_basePos)
	
	#Combine and finale
	#============================================================================
	newCrv = curves.combineCurves([topCrv,baseCrv])
	mi_crv = cgmMeta.cgmObject(newCrv)
	
	mi_crv.doCopyPivot(mi_ankle.mNode)
	#>>> Color
	curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
	mi_crv.doCopyNameTagsFromObject(mi_ankle.mNode,ignore = ['cgmType'])
	mi_crv.addAttr('cgmType',attrType='string',value = 'foot',lock=True)	    
	mi_crv.doName()
	    
	self.d_returnControls['foot'] = mi_crv.mNode 		
	self.md_ReturnControls['foot'] = mi_crv	
	
	
    def build_segmentIKHandles(self):
	l_segmentControls = []
	ml_SegmentControls = []
	
	#Defaults
	self.posOffset = [0,0,self._skinOffset*1.2]
	self.l_specifiedRotates = None	
	self.joinMode = True
	self.closedCurve = True
	self.rotateBank = None	    
	self.maxDistance = 1000
	self.aimAxis = 'y+'
	self.latheAxis = 'z'
	self.insetMult = .1
	self.points = 8
	self.rootRotate = None
	self.rootOffset = None
	d_kws = {}
	l_objectsToDo = []
	
	#Figure out some flag stuff
	if 'neck' in self._partType:
	    self.maxDistance = 1000
	    self.insetMult = .05
	    self.posOffset = [0,0,self._skinOffset*2]
	    d_kws = {'default':{'l_specifiedRotates':None,
	                        'joinMode': True,
	                        'rotateBank':None,
	                        'closedCurve':True,
	                        'aimAxis':'y+'},
	             0:{'rotateBank':10},
	             -1:{'closedCurve':False,'l_specifiedRotates':[-90,-60,-30,0,30,60,90],'rotateBank':-10}}
	    
	elif self._partType == 'leg':
	    l_objectsToDo = self.l_controlSnapObjects[:-1]
	    self.posOffset = [0,0,self._skinOffset*2]
	    self.points = 12
	    d_kws = {'default':{'closedCurve':True,
	                        'l_specifiedRotates':[],
	                        'insetMult':.15,
	                        'rootRotate':None,
	                        'rootOffset':[],
	                        'rotateBank':[]},
	             0:{'closedCurve':False,
	                'rootOffset':[0,0,self._skinOffset*4]},
	             -1:{'rootOffset':[0,self._skinOffset*4,0]}}
	    
	    if self._direction == 'left':
		self.aimAxis = 'x+'
		d_kws['default']['aimAxis']= 'x+'			
		d_kws[0]['l_specifiedRotates']=[-90,-60,-30,0,30,60,90]
		d_kws[0]['rotateBank'] = -10
	    else:
		self.aimAxis = 'x-'		
		d_kws['default']['aimAxis']= 'x-'	
		d_kws[0]['l_specifiedRotates']=[-90,-60,-30,0,30,60,90]
		d_kws[0]['rotateBank'] = 10

	if not l_objectsToDo:l_objectsToDo = self.l_controlSnapObjects
	for i,obj in enumerate(l_objectsToDo):
	    log.info(obj)
	    if d_kws:
		for k in d_kws['default'].keys():
		    self.__dict__[k] = d_kws['default'].get(k)		

		if d_kws.get(i):
		    for k in d_kws[i].keys():
			self.__dict__[k] = d_kws[i].get(k)
		elif i == len(l_objectsToDo)-1 and d_kws.get(-1):
		    log.info('last mode')
		    for k in d_kws[-1].keys():
			self.__dict__[k] = d_kws[-1].get(k)

		    
	    log.info(">>>>>>>>>>>aim: %s"%self.aimAxis)
	    log.info(">>>>>>>>>> lathe: %s"%self.latheAxis)
	    log.info(">>>>>>>>>> l_specifiedRotates: %s"%self.l_specifiedRotates)
	    log.info(">>>>>>>>>> distance: %s"%self.maxDistance)
	    #Few more special cases
	    if cgmMeta.cgmObject(obj).getAttr('cgmName') in ['ankle']:
		log.info('Special rotate mode')
		self.rootRotate = [0,0,0]
		self.latheAxis = 'y'	 
		
	    returnBuffer = createWrapControlShape(obj,self._targetMesh,
	                                          points = 8,
	                                          curveDegree=3,
	                                          insetMult = self.insetMult,
	                                          latheAxis = self.latheAxis,
	                                          aimAxis = self.aimAxis,	                                          
	                                          maxDistance = self.maxDistance,
	                                          rotateBank = self.rotateBank,
	                                          posOffset = self.posOffset,
	                                          rootRotate = self.rootRotate,
	                                          rootOffset = self.rootOffset,
	                                          closedCurve = self.closedCurve,
	                                          l_specifiedRotates = self.l_specifiedRotates,
	                                          joinMode=self.joinMode,
	                                          extendMode='disc')
	    mi_crv = returnBuffer['instance']	    
	    #>>> Color
	    curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[1])                    
	    mi_crv.addAttr('cgmType',attrType='string',value = 'segIKCurve',lock=True)	
	    mi_crv.doName()
	    
	    #Store for return
	    l_segmentControls.append( mi_crv.mNode )
	    ml_SegmentControls.append( mi_crv )
	    
	self.d_returnControls['segmentIK'] = l_segmentControls 
	self.md_ReturnControls['segmentIK'] = ml_SegmentControls
	    
	#except StandardError,error:
	#	log.error("build_segmentIKHandles! | %s"%error) 
	#	return False
	     
def returnBaseControlSize(mi_obj,mesh,axis=True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Figure out the base size for a control from a point in space within a mesh

    ARGUMENTS:
    mi_obj(cgmObject instance)
    mesh(obj) = ['option1','option2']
    axis(list) -- what axis to check
    
    RETURNS:
    axisDistances(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    #if type(l_mesh) not in [list,tuple]:l_mesh = [l_mesh]
    if mc.objExists(mi_obj):
	try:
	    mi_obj = cgmMeta.cgmObject(mi_obj)
	except StandardError,error:
		log.error("returnBaseControlSize Failed to initialize mi_obj! | %s"%error) 
		raise StandardError    
    elif not issubclass(type(mi_obj),cgmMeta.cgmObject):
	try:
	    mi_obj = cgmMeta.cgmObject(mi_obj.mNode)
	except StandardError,error:
		log.error("returnBaseControlSize Failed to initialize existing instance as mi_obj! | %s"%error) 
		raise StandardError  
	    
   	   
    #>>>Figure out the axis to do
    d_axisToDo = {}
    if axis == True:
        axis = ['x','y','z']
    if type(axis) in [list,tuple]:
        for a in axis:
            if a in dictionary.stringToVectorDict.keys():
                if list(a)[0] in d_axisToDo.keys():
                    d_axisToDo[list(a)[0]].append( a )
                else:
                    d_axisToDo[list(a)[0]] = [ a ]
                     
            elif type(a) is str and a.lower() in ['x','y','z']:
                buffer = []
                buffer.append('%s+'%a.lower())
                buffer.append('%s-'%a.lower())  
                d_axisToDo[a.lower()] = buffer
            else:
                log.warning("Don't know what with: '%s'"%a)
    
    log.debug(d_axisToDo)
    if not d_axisToDo:return False
    #>>>
    d_returnDistances = {}
    for axis in d_axisToDo:
        log.debug("Checking: %s"%axis)
        directions = d_axisToDo[axis]
        if len(directions) == 1:#gonna multiply our distance 
            info = RayCast.findMeshIntersectionFromObjectAxis(mesh,mi_obj.mNode,directions[0])
            d_returnDistances[axis] = (distance.returnDistanceBetweenPoints(info['hit'],mi_obj.getPosition()) *2)
        else:
            info1 = RayCast.findMeshIntersectionFromObjectAxis(mesh,mi_obj.mNode,directions[0])
            info2 = RayCast.findMeshIntersectionFromObjectAxis(mesh,mi_obj.mNode,directions[1])
            if info1 and info2:
                d_returnDistances[axis] = distance.returnDistanceBetweenPoints(info1['hit'],info2['hit'])                    
    log.debug(d_returnDistances) 
    return d_returnDistances

  
#@r9General.Timer    
def createWrapControlShape(targetObjects,
                           targetGeo = None,
                           latheAxis = 'z',aimAxis = 'y+',
                           points = 8,
                           curveDegree = 1,
                           insetMult = None,#Inset multiplier
                           posOffset = [],
                           rootOffset = [],#offset root before cast
                           rootRotate = None,
                           joinMode = False,
                           extendMode = None,
                           closedCurve = True,
                           l_specifiedRotates = None,
                           maxDistance = 1000,
                           closestInRange = True,
                           rotateBank = None,
                           joinHits = None,#keys to processed hits to see what to join
                           ):#'segment,radial,disc' 
    """
    Function for creating control curves from other objects. Currently assumes z aim, y up
    1) Cather info
    2) Get initial curves
    3) Store info
    4) return
    
    TODO:
    Change offsets to use lathe axis rather than 
    """
    if type(targetObjects) not in [list,tuple]:targetObjects = [targetObjects]
    if not targetGeo:
	raise NotImplementedError, "Must have geo for now"
    assert type(points) is int,"Points must be int: %s"%points
    assert type(curveDegree) is int,"Points must be int: %s"%points
    assert curveDegree > 0,"Curve degree must be greater than 1: %s"%curveDegree
    if posOffset is not None and len(posOffset) and len(posOffset)!=3:raise StandardError, "posOffset must be len(3): %s | len: %s"%(posOffset,len(posOffset))
    if rootOffset is not None and len(rootOffset) and len(rootOffset)!=3:raise StandardError, "rootOffset must be len(3): %s | len: %s"%(rootOffset,len(rootOffset))
    if rootRotate is not None and len(rootRotate) and len(rootRotate)!=3:raise StandardError, "rootRotate must be len(3): %s | len: %s"%(rootRotate,len(rootRotate))
    
    if insetMult is None:insetMult = 1
    for axis in ['x','y','z']:
	if axis in latheAxis.lower():latheAxis = axis
    
    log.info("targetObjects: %s"%targetObjects)
    
    if len(aimAxis) == 2:single_aimAxis = aimAxis[0]
    else:single_aimAxis = aimAxis
    
    #>>> Info
    l_groupsBuffer = []
    il_curvesToCombine = []
    l_sliceReturns = []
    #Need to do more to get a better size
    
    #>>> Build curves
    #=================================================================
    #> Root curve #
    log.info("RootRotate: %s"%rootRotate)
    mi_rootLoc = cgmMeta.cgmNode(targetObjects[0]).doLoc()
    if rootOffset:
	mc.move(rootOffset[0],rootOffset[1],rootOffset[2], [mi_rootLoc.mNode], r=True, rpr = True, os = True, wd = True)
    if rootRotate is not None and len(rootRotate):
	mc.rotate(rootRotate[0],rootRotate[1],rootRotate[2], [mi_rootLoc.mNode], os = True)

	    
    #>>> Root
    mi_rootLoc.doGroup()#Group to zero    
    if extendMode == 'segment':
	try:
	    if len(targetObjects) < 2:
		log.warning("Segment build mode only works with two objects or more")    
	    else:
		if insetMult is not None:
		    rootDistanceToMove = distance.returnDistanceBetweenObjects(targetObjects[0],targetObjects[1])
		    log.info("rootDistanceToMove: %s"%rootDistanceToMove)
		    mi_rootLoc.__setattr__('t%s'%latheAxis,rootDistanceToMove*insetMult)
		    #mi_rootLoc.tz = (rootDistanceToMove*insetMult)#Offset it
		
		for i,obj in enumerate(targetObjects[1:]):
		    log.info(i)
		    log.info(len(targetObjects[1:]))
		    #> End Curve
		    mi_endLoc = cgmMeta.cgmNode(obj).doLoc()
		    aimVector = dictionary.returnStringToVectors(latheAxis+'+')
		    Snap.go(mi_endLoc.mNode,mi_rootLoc.mNode,move=False,aim=True,aimVector=aimVector)
		    mi_endLoc.doGroup()
		    if i == len(targetObjects[1:])-1:
			if insetMult is not None:
			    distanceToMove = distance.returnDistanceBetweenObjects(targetObjects[-1],targetObjects[0])
			    log.info("distanceToMove: %s"%distanceToMove)
			    #mi_endLoc.tz = -(distanceToMove*insetMult)#Offset it  
			    mi_endLoc.__setattr__('t%s'%latheAxis,(distanceToMove*insetMult))
		    d_endCastInfo = createMeshSliceCurve(targetGeo,mi_endLoc,curveDegree=curveDegree,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = posOffset,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank, l_specifiedRotates = l_specifiedRotates)  	
		    l_sliceReturns.append(d_endCastInfo)
		    mi_end = cgmMeta.cgmObject(d_endCastInfo['curve'])
		    il_curvesToCombine.append(mi_end)
		    mc.delete(mi_endLoc.parent)#delete the loc
	except StandardError,error:
	    raise StandardError,"createWrapControlShape>>> segment wrap fail! | %s"%error
	
    elif extendMode == 'radial':
	    d_handleInner = createMeshSliceCurve(targetGeo,mi_rootLoc,curveDegree=curveDegree,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = 0,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank, l_specifiedRotates = l_specifiedRotates)  
	    mi_buffer = cgmMeta.cgmObject(d_handleInner['curve'])#instance curve	
	    l_sliceReturns.append(d_handleInner)
	    il_curvesToCombine.append(mi_buffer)    
	       
    elif extendMode == 'disc':
	log.info("disc mode")
	d_size = returnBaseControlSize(mi_rootLoc,targetGeo,axis=[aimAxis])#Get size
	#discOffset = d_size[ d_size.keys()[0]]*insetMult
	l_absSize = [abs(i) for i in posOffset]
	size = max(l_absSize) 
	if not size:
	    d_size = returnBaseControlSize(mi_rootLoc,targetGeo,axis=[aimAxis])#Get size
	    log.info("d_size: %s"%d_size)
	    size = d_size[ d_size.keys()[0]]*insetMult	
	    
	discOffset = size
	log.info("d_size: %s"%d_size)
	log.info("discOffset is: %s"%discOffset)
	
	mi_rootLoc.__setattr__('t%s'%latheAxis,discOffset)
	d_handleInnerUp = createMeshSliceCurve(targetGeo,mi_rootLoc,curveDegree=curveDegree,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = 0,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank, l_specifiedRotates = l_specifiedRotates) 
	mi_buffer = cgmMeta.cgmObject(d_handleInnerUp['curve'])#instance curve	
	l_sliceReturns.append(d_handleInnerUp)
	il_curvesToCombine.append(mi_buffer) 
	
	mi_rootLoc.__setattr__('t%s'%latheAxis,-discOffset)
	d_handleInnerDown = createMeshSliceCurve(targetGeo,mi_rootLoc,curveDegree=curveDegree,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = 0,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank,  l_specifiedRotates = l_specifiedRotates) 
	mi_buffer = cgmMeta.cgmObject(d_handleInnerDown['curve'])#instance curve	
	l_sliceReturns.append(d_handleInnerDown)
	il_curvesToCombine.append(mi_buffer) 
	
	mi_rootLoc.tz = 0
	
    elif extendMode == 'cylinder':
	log.info("cylinder mode")
	d_size = returnBaseControlSize(mi_rootLoc,targetGeo,axis=[aimAxis])#Get size
	discOffset = d_size[ d_size.keys()[0]]*insetMult
	log.info("d_size: %s"%d_size)
	log.info("discOffset is: %s"%discOffset)
	
	mi_rootLoc.__setattr__('t%s'%latheAxis,discOffset)
	d_handleInnerUp = createMeshSliceCurve(targetGeo,mi_rootLoc,curveDegree=curveDegree,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = posOffset,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank, l_specifiedRotates = l_specifiedRotates)  
	mi_buffer = cgmMeta.cgmObject(d_handleInnerUp['curve'])#instance curve	
	l_sliceReturns.append(d_handleInnerUp)
	il_curvesToCombine.append(mi_buffer) 
		
	mi_rootLoc.__setattr__('t%s'%latheAxis,0)
	
    elif extendMode == 'loliwrap':
	log.info("lolipop mode")
	l_absSize = [abs(i) for i in posOffset]
	size = max(l_absSize)*1.25
	if not size:
	    d_size = returnBaseControlSize(mi_rootLoc,targetGeo,axis=[aimAxis])#Get size
	    log.info("d_size: %s"%d_size)
	    l_size = d_size[single_aimAxis]
	    size = l_size#/1.5
	log.info("loli size: %s"%size)
	i_ball = cgmMeta.cgmObject(curves.createControlCurve('sphere',size = size))
	
    #Now cast our root since we needed to move it with segment mode before casting
    if extendMode == 'cylinder':
	mi_rootLoc.__setattr__('t%s'%latheAxis,-discOffset)
	
    d_rootCastInfo = createMeshSliceCurve(targetGeo,mi_rootLoc,curveDegree=curveDegree,latheAxis=latheAxis,aimAxis=aimAxis,posOffset = posOffset,points = points,returnDict=True,closedCurve = closedCurve, maxDistance = maxDistance, closestInRange=closestInRange, rotateBank=rotateBank, l_specifiedRotates = l_specifiedRotates)  
    if extendMode == 'disc':
	l_sliceReturns.insert(1,d_rootCastInfo)	
    else:
	l_sliceReturns.insert(0,d_rootCastInfo)
    
    if extendMode == 'loliwrap':
	Snap.go(i_ball.mNode,mi_rootLoc.mNode,True, True)#Snap to main object
	
	mi_crv = cgmMeta.cgmObject( d_rootCastInfo['curve'] )
	l_eps = mi_crv.getComponents('ep')
	midIndex = int(len(l_eps)/2)
	log.info("eps: %s"%l_eps)
	log.info("mid: %s"%midIndex)
	
	#Move the ball
	pos = distance.returnWorldSpacePosition(l_eps[midIndex])
	mc.xform( i_ball.mNode, translation = pos, ws = True)#Snap to the mid ep
	mc.move(pos[0],pos[1],pos[2],i_ball.mNode,absolute = True,ws=True)
	Snap.go(i_ball.mNode,mi_rootLoc.mNode,move = False, orient = False, aim=True, aimVector=[0,0,-1])
	
	if posOffset:
	    mc.move(posOffset[0]*2,posOffset[1]*2,posOffset[2]*2, [i_ball.mNode], r = True, rpr = True, os = True, wd = True)
	
	#Make the curve between the two 
	mi_traceCrv = cgmMeta.cgmObject( mc.curve(degree = 1, ep = [pos,i_ball.getPosition()]) )
	
	#Combine
	il_curvesToCombine.extend([i_ball,mi_traceCrv])
	    
    mi_root = cgmMeta.cgmObject(d_rootCastInfo['curve'])#instance curve
    il_curvesToCombine.append(mi_root)    
    
    mc.delete(mi_rootLoc.parent)#delete the loc
    
    l_curvesToCombine = [mi_obj.mNode for mi_obj in il_curvesToCombine]#Build our combine list before adding connectors         
    log.info(d_rootCastInfo['processedHits'])
    if joinMode and extendMode is not 'loliwrap' and len(l_sliceReturns)>1:
	if joinHits:
	    keys = d_rootCastInfo['processedHits'].keys()
	    keys.sort()
	    #goodDegrees = []
	    #for i,key in enumerate(keys):
		#if i in joinHits:
		#goodDegrees.append(key)
	    goodDegrees = [key for i,key in enumerate(keys) if i in joinHits]
	    log.info("joinHits: %s"%joinHits)
	    log.info("goodDegrees: %s"%goodDegrees)	    
	else:
	    goodDegrees = [key for key in d_rootCastInfo['processedHits'].keys()]
	#> Side Curves
	for degree in goodDegrees:
	    l_pos = []	    
	    for d in l_sliceReturns:
		l_pos.append( d['processedHits'].get(degree) or False )
	    while False in l_pos:
		l_pos.remove(False)
	    log.info("l_pos: %s"%l_pos)
	    if len(l_pos)>=2:
		try:
		    l_curvesToCombine.append( mc.curve(d=curveDegree,ep=l_pos,os =True) )#Make the curve
		except:
		    log.info("createWrapControlShape>>>> skipping curve fail: %s"%(degree))
		    
    #>>>Combine the curves
    newCurve = curves.combineCurves(l_curvesToCombine) 
    mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(targetObjects[0],False) )
    curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
    mc.delete(newCurve)
    
    #>>Copy tags and name
    mi_crv.doCopyNameTagsFromObject(targetObjects[0],ignore = ['cgmType'])
    mi_crv.addAttr('cgmType',attrType='string',value = 'controlCurve')
    mi_crv.doName()                
        
    #Store for return
    return {'curve':mi_crv.mNode,'instance':mi_crv}  
 
#@r9General.Timer
def createMeshSliceCurve(mesh, mi_obj,latheAxis = 'z',aimAxis = 'y+',
                         points = 12, curveDegree = 3, minRotate = None, maxRotate = None, rotateRange = None,
                         posOffset = 0, markHits = False,rotateBank = None, closedCurve = True, maxDistance = 1000,
                         initialRotate = 0, offsetMode = 'vector', l_specifiedRotates = None, closestInRange = True,
                         returnDict = False):
    """
    This function lathes an axis of an object, shoot rays out the aim axis at the provided mesh and returning hits. 
    it then uses this information to build a curve shape.
    
    @Paremeters
    mi_obj(string instance) -- object to use as base
    latheAxis(str) -- axis of the objec to lathe TODO: add validation
    aimAxis(str) -- axis to shoot out of
    points(int) -- how many points you want in the curve
    posOffset(vector) -- transformational offset for the hit from a normalized locator at the hit. Oriented to the surface
    markHits(bool) -- whether to keep the hit markers
    returnDict(bool) -- whether you want all the infomation from the process.
    rotateBank (float) -- let's you add a bank to the rotation object
    minRotate(float) -- let's you specify a valid range to shoot
    maxRotate(float) -- let's you specify a valid range to shoot
    l_specifiedRotates(list of values) -- specify where to shoot relative to an object. Ignores some other settings
    maxDistance(float) -- max distance to cast rays
    closestInRange(bool) -- True by default. If True, takes first hit. Else take the furthest away hit in range.
    """
    if issubclass(type(mi_obj),cgmMeta.cgmObject):
        mi_obj = mi_obj
    else:
        try:
	    mi_obj = cgmMeta.cgmObject(mi_obj)
	except StandardError,error:
		log.error(error) 
		return False

    log.debug("Casting: '%s"%mi_obj.mNode)
    if type(mesh) in [list,tuple]:
	log.error("Can only pass one mesh. passing first: '%s'"%mesh[0])
	mesh = mesh[0]
    assert mc.objExists(mesh),"Mesh doesn't exist: '%s'"%mesh
    
    #>>>> Info
    #================================================================
    mi_loc = mi_obj.doLoc()
    mi_loc.doGroup()
    l_pos = []
    d_returnDict = {}
    d_hitReturnFromValue = {}
    d_processedHitFromValue = {}

    for axis in ['x','y','z']:
	if axis in latheAxis:latheAxis = axis
	
    log.debug("latheAxis: %s"%latheAxis)
    if rotateBank is not None:#we need a bank  axis
	l_axisCull = ['x','y','z']
	l_axisCull.remove(latheAxis)
	log.debug(latheAxis)
	if len(aimAxis) == 2: aimCull = aimAxis[0].lower()
	else: aimCull = aimAxis.lower()
	l_axisCull.remove(aimCull)
	log.debug(aimCull)	
	log.debug("Bank rotate: %s"%l_axisCull)
	bankAxis = l_axisCull[0]
	
    #Rotate obj 
    mi_rotObj = mi_loc
    if rotateBank is not None and type(rotateBank) is not list:
	rotateGroup = mi_loc.doGroup(True)
	mi_rotObj = cgmMeta.cgmObject(rotateGroup)
	mi_loc.__setattr__('rotate%s'%bankAxis.capitalize(),rotateBank)
	    
    #Figure out the rotateBaseValue
    if minRotate is not None:
	rotateFloor = minRotate
    else:
	rotateFloor = 0
    if maxRotate is not None:
	rotateCeiling = maxRotate
    else:
	rotateCeiling = 360
	
    #>>>> Get our rotate info
    #================================================================
    l_rotateSettings = []
    
    if l_specifiedRotates and type(l_specifiedRotates) in [list,tuple]:
	#See if it's good
	for f in l_specifiedRotates:
	    if type(f) in [int,float]:
		l_rotateSettings.append(f) 
	
    if not l_rotateSettings or len(l_rotateSettings) < 2:
	#If we don't have data, we're gonna build it
	if minRotate is not None or maxRotate is not None:
	    #add a point if we don't have a full loop
	    points = points+1	
	rotateBaseValue = len(range(rotateFloor,rotateCeiling+1))/points
	log.debug("rotateBaseValue: %s"%rotateBaseValue)
	    
	#Build our rotate values
	for i in range(points):
	    l_rotateSettings.append( (rotateBaseValue*(i)) + initialRotate +rotateFloor)
    
    if not l_rotateSettings:raise StandardError, "Should have had some l_rotateSettings by now"
    #>>>> Pew, pew !
    #================================================================
    for i,rotateValue in enumerate(l_rotateSettings):
	d_castReturn = {}
	hit = False
	
	#shoot our ray, store the hit
	log.debug("Casting: %i>>%f"%(i,rotateValue))
	mc.setAttr("%s.rotate%s"%(mi_rotObj.mNode,latheAxis.capitalize()),rotateValue)
	log.debug(mc.getAttr("%s.rotate%s"%(mi_rotObj.mNode,latheAxis.capitalize())) )
	#mi_rotObj.__setattr__('rotate%s'%latheAxis.capitalize(),rotateValue)	
	try:
	    log.debug("mesh: %s"%mesh)
	    log.debug("mi_loc.mNode: %s"%mi_loc.mNode)
	    log.debug("aimAxis: %s"%aimAxis)
	    log.debug("latheAxis: %s"%latheAxis)
	    log.debug("maxDistance: %s"%maxDistance)
	    
	    if closestInRange:
		d_castReturn = RayCast.findMeshIntersectionFromObjectAxis(mesh, mi_loc.mNode, axis=aimAxis, maxDistance = maxDistance) or {}
		log.debug("closest in range castReturn: %s"%d_castReturn)		
		d_hitReturnFromValue[rotateValue] = d_castReturn	
		log.debug("From %s: %s" %(rotateValue,d_castReturn))
		    
	    else:
		d_castReturn = RayCast.findMeshIntersectionFromObjectAxis(mesh, mi_loc.mNode, axis=aimAxis, maxDistance = maxDistance, singleReturn=False) or {}
		log.debug("castReturn: %s"%d_castReturn)
		if d_castReturn.get('hits'):
		    closestPoint = distance.returnFurthestPoint(mi_loc.getPosition(),d_castReturn.get('hits')) or False
		    d_castReturn['hit'] = closestPoint
		    log.debug("From %s: %s" %(rotateValue,d_castReturn))
		
	    hit = d_castReturn.get('hit') or False

	except StandardError,error:
		raise StandardError,"createMeshSliceCurve>>> error: %s"%error 
	if hit:
	    if markHits or posOffset:
		mi_tmpLoc = cgmMeta.cgmObject(mc.spaceLocator()[0])
		mc.move (hit[0],hit[1],hit[2], mi_tmpLoc.mNode)	
		if posOffset:
		    if offsetMode =='vector':
			constBuffer = mc.aimConstraint(mi_obj.mNode,mi_tmpLoc.mNode,
		                                          aimVector=[0,0,-1],
		                                          upVector=[0,1,0],
		                                          worldUpType = 'scene')
		    else:
			constBuffer = mc.normalConstraint(mesh,mi_tmpLoc.mNode,
		                                          aimVector=[0,0,1],
		                                          upVector=[0,1,0],
		                                          worldUpType = 'scene')
		    mc.delete(constBuffer)
		    mc.move(posOffset[0],posOffset[1],posOffset[2], [mi_tmpLoc.mNode], r=True, rpr = True, os = True, wd = True)
		    hit = mi_tmpLoc.getPosition()
		if not markHits:
		    mi_tmpLoc.delete()
		
	    l_pos.append(hit)
	    d_processedHitFromValue[rotateValue] = hit
	
    mc.delete(mi_loc.getAllParents()[-1])#delete top group
    log.debug("pos list: %s"%l_pos)    
    if not l_pos:
	log.warning("Cast return: %s"%d_castReturn)
	raise StandardError,"createMeshSliceCurve>> Not hits found. Nothing to do"
    if len(l_pos)>=3:
	if closedCurve:
	    buffer = l_pos[0]
	    l_finalPos = l_pos.append(buffer)
	curveBuffer =  mc.curve (d=curveDegree, ep = l_pos, os=True)
	if returnDict:
	    return {'curve':curveBuffer,
	            'processedHits':d_processedHitFromValue,
	            'hitReturns':d_hitReturnFromValue}
	else:
	    return curveBuffer
    
    return False    

'''	
@r9General.Timer
def limbControlMaker(moduleInstance,controlTypes = ['cog']):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    * Save the new positional information from the template objects
    * Collect all names of objects for a delete list
    * If anything in the module doesn't belong there, un parent it, report it
        * like a template object parented to another obect

    ARGUMENTS:
    moduleNull(string)
    controlTypes(list) = ['option1','option2']
    
    RETURNS:
    limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """ 
    if type(controlTypes) is not list:controlTypes = [controlTypes]
    if not issubclass(type(moduleInstance),cgmPM.cgmModule):
        log.error("Not a cgmModule: '%s'"%moduleInstance)
        return 
    
    assert moduleInstance.mClass in ['cgmModule','cgmLimb'],"Not a module"
    assert moduleInstance.isTemplated(),"Module is not templated: '%s'"%moduleInstance.getShortName()        
    assert moduleInstance.isSkeletonized(),"Module is not skeletonized: '%s'"%moduleInstance.getShortName()
    
    log.debug(">>> ModuleControlFactory.go.__init__")
    mi_m = moduleInstance# Link for shortness    
    """
    if moduleInstance.hasControls():
        if forceNew:
            deleteControls(moduleInstance)
        else:
            log.warning("'%s' has already been skeletonized"%moduleInstance.getShortName())
            return        
    """
    #>>> Gather info
    #=========================================================
    l_moduleColors = mi_m.getModuleColors()
    l_coreNames = mi_m.coreNames.value
            
    #>>> part name 
    partName = mi_m.getPartNameBase()
    partType = mi_m.moduleType or False
    
    direction = None
    if mi_m.hasAttr('cgmDirection'):
        direction = mi_m.cgmDirection or None
        
    
    #Gether information 
    mi_templateNull = mi_m.templateNull
    bodyGeo = mi_m.modulePuppet.getGeo() or ['Morphy_Body_GEO1'] #>>>>>>>>>>>>>>>>>this needs better logic
    l_controlSnapObjects = []
    for mi_obj in mi_templateNull.controlObjects:
        l_controlSnapObjects.append(mi_obj.helper.mNode)  
    skinDepth = 2.5
    d_returnControls = {}
    if 'fkSegmentControls' in controlTypes:
	    l_segmentControls = []
	    l_segmentHandles = []
	    l_indexPairs = lists.parseListToPairs(list(range(len(l_controlSnapObjects))))
	    l_segments = lists.parseListToPairs(l_controlSnapObjects)
	    for i,seg in enumerate(l_segments):
		#> Figure out a base scale and set it
		if not bodyGeo:
		    raise StandardError,"NO BODY GEO"
		
		log.debug("segment: %s"%seg)
		log.debug("indices: %s"%l_indexPairs[i])
		distanceMult = .2
		
		#>>> Get a base distance
		distanceToMove = distance.returnDistanceBetweenObjects(seg[0],seg[1])
		log.debug("distanceToMove: %s"%distanceToMove)
		l_groupsBuffer = []
		#Need to do more to get a better size
		
		#>>> Build curves
		#=================================================================
		points = 8
		curveDegree = 1
		posOffset = [0,0,skinDepth*1.25]
		#> Root curve #
		mi_rootLoc = cgmMeta.cgmNode(seg[0]).doLoc()
			    
		#>>> Root
		mi_rootLoc.doGroup()
		mi_rootLoc.tz = (distanceToMove*distanceMult)#Offset it
		
		d_rootCastInfo = createMeshSliceCurve(bodyGeo[0],mi_rootLoc,curveDegree=curveDegree,posOffset = posOffset,points = points,returnDict=True) 
		mi_root = cgmMeta.cgmObject(d_rootCastInfo['curve'])
		    
		#> End Curve
		mi_endLoc = cgmMeta.cgmNode(seg[1]).doLoc()
		mi_endLoc.doGroup()
		mi_endLoc.tz = -(distanceToMove*distanceMult)#Offset it  
		d_endCastInfo = createMeshSliceCurve(bodyGeo[0],mi_endLoc,curveDegree=curveDegree,posOffset = posOffset,points = points,returnDict=True) 
		mi_end = cgmMeta.cgmObject(d_endCastInfo['curve'])          
		
		#> Side Curves
		l_rootPos = []
		l_endPos = []
		l_curvesToCombine = []
		for degree in d_rootCastInfo['processedHits'].keys():
		    rootPoint = d_rootCastInfo['processedHits'].get(degree) or False
		    endPoint = d_endCastInfo['processedHits'].get(degree) or False
		    if rootPoint and endPoint:
			l_curvesToCombine.append( mc.curve(d=1,ep=[rootPoint,endPoint],os =True) )#Make the curve
		    else:
			log.warning("Failed to find side data on: %s"%(seg))
    
		#>>>Store groups
		l_groupsBuffer.append( mi_endLoc.parent )
		l_groupsBuffer.append( mi_rootLoc.parent )
    
		#>>>Combine the curves
		l_curvesToCombine.extend([mi_root.mNode,mi_end.mNode])            
		newCurve = curves.combineCurves(l_curvesToCombine) 
		mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(seg[0],False) )
		curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
		mc.delete(newCurve)
		
		#>>Copy tags and name
		mi_crv.doCopyNameTagsFromObject(seg[0],ignore = ['cgmType'])
		mi_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
		mi_crv.addAttr('cgmTypeModifier',attrType='string',value = 'fk')				
		mi_crv.doName()
		
		#>>> Color
		curves.setCurveColorByName(mi_crv.mNode,l_moduleColors[0])                    
		
		#>>>Clean up groups
		for g in l_groupsBuffer:
		    if mc.objExists(g):
			mc.delete(g)
		
		#Store for return
		l_segmentControls.append( mi_crv.mNode )
	    d_returnControls['fkSegmentControls'] = l_segmentControls 
	    
    if 'ikSegmentControls' in controlTypes:
	    l_segmentControls = []
	    l_segmentHandles = []
	    distanceMult = .025	  
	    points = 8
	    curveDegree = 3
	    posOffset = [0,0,skinDepth]	    
	    l_indexPairs = lists.parseListToPairs(list(range(len(l_controlSnapObjects))))
	    l_segments = lists.parseListToPairs(l_controlSnapObjects)
	    for i,seg in enumerate(l_segments):
		#> Figure out a base scale and set it
		if not bodyGeo:
		    raise StandardError,"NO BODY GEO"
		
		log.debug("segment: %s"%seg)
		log.debug("indices: %s"%l_indexPairs[i])
		
		#>>> Get a base distance
		distanceToMove = distance.returnDistanceBetweenObjects(seg[0],seg[1])
		log.debug("distanceToMove: %s"%distanceToMove)
		l_groupsBuffer = []
		#Need to do more to get a better size
		
		#>>> Build curves
		#=================================================================
		#> Root curve #
		mi_rootLoc = cgmMeta.cgmNode(seg[0]).doLoc()
			    
		#>>> Root
		mi_rootLoc.doGroup()
		mi_rootLoc.tz = (distanceToMove*distanceMult)#Offset it
		
		d_rootCastInfo = createMeshSliceCurve(bodyGeo[0],mi_rootLoc,curveDegree=curveDegree,posOffset = posOffset,points = points,returnDict=True) 
		mi_root = cgmMeta.cgmObject(d_rootCastInfo['curve'])
		    
		#> End Curve
		mi_rootLoc.tz = -(distanceToMove*distanceMult)#Offset it  
		d_endCastInfo = createMeshSliceCurve(bodyGeo[0],mi_rootLoc,curveDegree=curveDegree,posOffset = posOffset,points = points,returnDict=True) 
		mi_end = cgmMeta.cgmObject(d_endCastInfo['curve'])          
		
		#> Side Curves
		l_rootPos = []
		l_endPos = []
		l_curvesToCombine = []
		for degree in d_rootCastInfo['processedHits'].keys():
		    rootPoint = d_rootCastInfo['processedHits'].get(degree) or False
		    endPoint = d_endCastInfo['processedHits'].get(degree) or False
		    if rootPoint and endPoint:
			l_curvesToCombine.append( mc.curve(d=1,ep=[rootPoint,endPoint],os =True) )#Make the curve
		    else:
			log.warning("Failed to find side data on: %s"%(seg))
    
		#>>>Store groups
		l_groupsBuffer.append( mi_rootLoc.parent )
    
		#>>>Combine the curves
		l_curvesToCombine.extend([mi_root.mNode,mi_end.mNode])            
		newCurve = curves.combineCurves(l_curvesToCombine) 
		mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(seg[0],False) )
		curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
		mc.delete(newCurve)
		
		#>>Copy tags and name
		mi_crv.doCopyNameTagsFromObject(seg[0],ignore = ['cgmType'])
		mi_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
		mi_crv.addAttr('cgmTypeModifier',attrType='string',value = 'ik')		
		mi_crv.doName()
		
		#>>> Color
		curves.setCurveColorByName(mi_crv.mNode,l_moduleColors[0])                    
		
		#>>>Clean up groups
		for g in l_groupsBuffer:
		    if mc.objExists(g):
			mc.delete(g)
		
		#Store for return
		l_segmentControls.append( mi_crv.mNode )
	    d_returnControls['ikSegmentControls'] = l_segmentControls 
	    
    if 'segmentControlsNEW' in controlTypes:
        l_segmentControls = []
	l_segmentHandles = []
        l_indexPairs = lists.parseListToPairs(list(range(len(l_controlSnapObjects))))
        l_segments = lists.parseListToPairs(l_controlSnapObjects)
        for i,seg in enumerate(l_segments):
            #> Figure out a base scale and set it
            if not bodyGeo:
                raise StandardError,"NO BODY GEO"
	    
            log.debug("segment: %s"%seg)
            log.debug("indices: %s"%l_indexPairs[i])
	    distanceMult = .2
	    
            #>>> Get a base distance
            distanceToMove = distance.returnDistanceBetweenObjects(seg[0],seg[1])
            log.debug("distanceToMove: %s"%distanceToMove)
            l_groupsBuffer = []
            #Need to do more to get a better size
            
            #>>> Build curves
            #=================================================================
	    points = 8
            #> Root curve #
            mi_rootLoc = cgmMeta.cgmNode(seg[0]).doLoc()
	    
	    #>>> Handle
	    d_handleInnerInfo = createMeshSliceCurve(bodyGeo[0],mi_rootLoc,posOffset = [0,0,skinDepth],points = points,returnDict=True) 
	    d_handleOuterInfo = createMeshSliceCurve(bodyGeo[0],mi_rootLoc,posOffset = [0,0,skinDepth*2],points = points,returnDict=True) 
            l_handleCurvesToCombine = [d_handleInnerInfo['curve'],d_handleOuterInfo['curve']]    
	    
            mi_handle = cgmMeta.cgmObject( rigging.groupMeObject(seg[0],False) )
	    
	    for degree in [0,90,180,270]:
		rootPoint = d_handleInnerInfo['processedHits'].get(degree) or False
		endPoint = d_handleOuterInfo['processedHits'].get(degree) or False
		if rootPoint and endPoint:
		    l_handleCurvesToCombine.append( mc.curve(d=1,ep=[rootPoint,endPoint],os =True) )#Make the curve
		else:
		    log.warning("Failed to find side data on: %s"%(seg))
	    
	    newCurve = curves.combineCurves(l_handleCurvesToCombine)   
            curves.parentShapeInPlace(mi_handle.mNode,newCurve)#Parent shape
	    mc.delete(newCurve)
            
	    
            #>>Copy tags and name
            mi_handle.doCopyNameTagsFromObject(seg[0],ignore = ['cgmType'])
            mi_handle.addAttr('cgmType',attrType='string',value = 'controlAnim')
            mi_handle.addAttr('cgmTypeModifier',attrType='string',value = 'handle')	    
            mi_handle.doName()
            
            #>>> Color
            curves.setCurveColorByName(mi_handle.mNode,l_moduleColors[1]) 	    
	    
	    #>>> Main Curve =====================================================
	    #>>> Root
            mi_rootLoc.doGroup()
            mi_rootLoc.tz = (distanceToMove*distanceMult)#Offset it
            
	    d_rootCastInfo = createMeshSliceCurve(bodyGeo[0],mi_rootLoc,posOffset = [0,0,skinDepth],points = points,returnDict=True) 
            mi_root = cgmMeta.cgmObject(d_rootCastInfo['curve'])
	        
            #> End Curve
            mi_endLoc = cgmMeta.cgmNode(seg[1]).doLoc()
            mi_endLoc.doGroup()
            mi_endLoc.tz = -(distanceToMove*distanceMult)#Offset it  
	    d_endCastInfo = createMeshSliceCurve(bodyGeo[0],mi_endLoc,posOffset = [0,0,skinDepth],points = points,returnDict=True) 
            mi_end = cgmMeta.cgmObject(d_endCastInfo['curve'])          
            
            #> Side Curves
            l_rootPos = []
            l_endPos = []
            l_curvesToCombine = []
	    for degree in [0,90,180,270]:
		rootPoint = d_rootCastInfo['processedHits'].get(degree) or False
		endPoint = d_endCastInfo['processedHits'].get(degree) or False
		if rootPoint and endPoint:
		    l_curvesToCombine.append( mc.curve(d=1,ep=[rootPoint,endPoint],os =True) )#Make the curve
		else:
		    log.warning("Failed to find side data on: %s"%(seg))

            #>>>Store groups
            l_groupsBuffer.append( mi_endLoc.parent )
            l_groupsBuffer.append( mi_rootLoc.parent )

            #>>>Combine the curves
            l_curvesToCombine.extend([mi_root.mNode,mi_end.mNode])            
            newCurve = curves.combineCurves(l_curvesToCombine) 
            mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(seg[0],False) )
            curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
            mc.delete(newCurve)
            
            #>>Copy tags and name
            mi_crv.doCopyNameTagsFromObject(seg[0],ignore = ['cgmType'])
            mi_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
            mi_crv.doName()
            
            #>>> Color
            curves.setCurveColorByName(mi_crv.mNode,l_moduleColors[0])                    
            
            #>>>Clean up groups
            for g in l_groupsBuffer:
                if mc.objExists(g):
                    mc.delete(g)
            
            #Store for return
            l_segmentControls.append( mi_crv.mNode )
	    l_segmentHandles.append( mi_handle.mNode )
        d_returnControls['segmentControls'] = l_segmentControls 
        d_returnControls['segmentHandles'] = l_segmentHandles 
            
    if 'segmentControls2' in controlTypes:
            l_segmentControls = []
            l_indexPairs = lists.parseListToPairs(list(range(len(l_controlSnapObjects))))
            l_segments = lists.parseListToPairs(l_controlSnapObjects)
            for i,seg in enumerate(l_segments):
                log.debug("segment: %s"%seg)
                log.debug("indices: %s"%l_indexPairs[i])
                mi_loc = cgmMeta.cgmObject(mc.spaceLocator()[0])#Make a loc            
                #>>> Get a base distance
                distanceToMove = distance.returnDistanceBetweenObjects(seg[0],seg[1])
                log.debug("distanceToMove: %s"%distanceToMove)
                l_groupsBuffer = []
                #Need to do more to get a better size
                
                #>>> Build curves
                #=================================================================
                #> Root curve #
                mi_root = cgmMeta.cgmObject(curves.createControlCurve('circle',1))
                Snap.go(mi_root.mNode,seg[0],move = True, orient = True)#Snap it
                mi_root.doGroup()
                mi_root.tz = (distanceToMove*.1)#Offset it
                
                #> End Curve
                mi_end = cgmMeta.cgmObject(curves.createControlCurve('circle',1))
                Snap.go(mi_end.mNode,seg[1],move = True, orient = True)#Snap it
                mi_end.doGroup()
                mi_end.tz = -(distanceToMove*.1)#Offset it  
                
                #> Figure out a base scale and set it
                if bodyGeo:
                    multiplier = 1.25
                    log.debug("Shrinkwrap mode")
                    Snap.go(mi_loc.mNode,mi_root.parent,move = True, orient = True)#Snap
                    mi_loc.parent = mi_root.parent#parent

                    d_info = returnBaseControlSize(mi_loc,bodyGeo[0],axis = ['x','y'])
                    xScale = d_info['x']
                    yScale = d_info['y']
                    log.debug("x: %s"%xScale)
                    log.debug("y: %s"%yScale)                
                    #> Now our first pass of scaling
                    mi_root.sx = xScale*1.25
                    mi_root.sy = yScale*1.25
                    mi_root.sz = 1
                    
                    mi_end.sx = xScale*1.25
                    mi_end.sy = yScale*1.25
                    mi_end.sz = 1    
                    #> Now we're gonna strink wrap it
                    for mi_crv in [mi_root,mi_end]:
                        Snap.go(mi_crv ,targets = bodyGeo[0],orient = False,snapToSurface=True,snapComponents=True,posOffset=[0,0,skinDepth])                    
                        log.debug(mi_crv.getShortName())
    
                #> Side Curves
                l_rootPos = []
                l_endPos = []
                l_curvesToCombine = []
                for cv in [0,3,5,7]:
                    l_posBuffer = []
                    #>>> Need to get u positions for more accuracy
                    l_posBuffer.append(cgmMeta.cgmNode('%s.ep[%i]'%(mi_root.mNode,cv-1)).getPosition())
                    l_posBuffer.append(cgmMeta.cgmNode('%s.ep[%i]'%(mi_end.mNode,cv-1)).getPosition())
                    l_curvesToCombine.append( mc.curve(d=1,p=l_posBuffer,os =True) )#Make the curve
                
                #>>>Store groups
                l_groupsBuffer.append( mi_end.parent )
                l_groupsBuffer.append( mi_root.parent )
    
                #>>>Combine the curves
                l_curvesToCombine.extend([mi_root.mNode,mi_end.mNode])            
                newCurve = curves.combineCurves(l_curvesToCombine) 
                mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(seg[0],False) )
                curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
                mc.delete(newCurve)
                
                #>>Copy tags and name
                mi_crv.doCopyNameTagsFromObject(seg[0],ignore = ['cgmType'])
                mi_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
                mi_crv.doName()
                
                #>>> Color
                curves.setCurveColorByName(mi_crv.mNode,l_moduleColors[0])                    
                
                #>>>Clean up groups
                for g in l_groupsBuffer:
                    if mc.objExists(g):
                        mc.delete(g)
                
                #Store for return
                l_segmentControls.append( mi_crv.mNode )
    
            d_returnControls['segmentControls'] = l_segmentControls 
	    
    if 'cog' in controlTypes:
        if 'segmentControls' not in d_returnControls.keys():
            log.warn("Don't have cog creation without segment controls at present")
            return False
        
        mi_crv = cgmMeta.cgmObject( curves.createControlCurve('circleArrow',direction = 'y+',absoluteSize=False))
        Snap.go(mi_crv, d_returnControls['segmentControls'][0]) #Snap it
        size = distance.returnBoundingBoxSize(d_returnControls['segmentControls'][0],True)#Get size
        log.debug(size)
        mc.scale(size[0]*1.1,size[1],size[2]*1.1,mi_crv.mNode,relative = True)
        
        #>>Copy tags and name
        mi_crv.addAttr('cgmName',attrType='string',value = 'cog')        
        mi_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
        mi_crv.doName()        

        #>>> Color
        curves.setCurveColorByName(mi_crv.mNode,l_moduleColors[0])    
        
        d_returnControls['cog'] = mi_crv.mNode
	
    if 'cog2' in controlTypes:
        if 'segmentControls' not in d_returnControls.keys():
            log.warn("Don't have cog creation without segment controls at present")
            return False
        
        mi_crv = cgmMeta.cgmObject( curves.createControlCurve('cube',1))
        Snap.go(mi_crv, d_returnControls['segmentControls'][0]) #Snap it
        size = distance.returnBoundingBoxSize(d_returnControls['segmentControls'][0],True)#Get size
        log.debug(size)
        mc.scale(size[0]*1.1,size[1],size[2]*1.1,mi_crv.mNode,relative = True)
        
        #>>Copy tags and name
        mi_crv.addAttr('cgmName',attrType='string',value = 'cog')        
        mi_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
        mi_crv.doName()        

        #>>> Color
        curves.setCurveColorByName(mi_crv.mNode,l_moduleColors[0])    
        
        d_returnControls['cog'] = mi_crv.mNode
        
    if 'hips' in controlTypes:
        if 'segmentControls' not in d_returnControls.keys():
            log.warn("Don't have hip creation without segment controls at present")
            return False
	
	distanceMult = .3
        
        #>>>Create the curve
        mi_crv = cgmMeta.cgmObject( curves.createControlCurve('semiSphere',1,'z-'))
        Snap.go(mi_crv, d_returnControls['segmentControls'][0],orient = True) #Snap it
        mi_crv.doGroup()
        if len(l_controlSnapObjects)>2:
            distanceToMove = distance.returnDistanceBetweenObjects(l_controlSnapObjects[0],l_controlSnapObjects[1])
            mi_crv.tz = -(distanceToMove*distanceMult)#Offset it
        
        #>Clean up group
        g = mi_crv.parent
        mi_crv.parent = False
        mc.delete(g)
        
        #>Size it
        size = distance.returnBoundingBoxSize(d_returnControls['segmentControls'][0],True)#Get size
        mi_obj = cgmMeta.cgmObject(d_returnControls['segmentControls'][0])
        d_size = returnBaseControlSize(mi_crv,bodyGeo[0],['z-'])      
        log.debug(size)
        mc.scale(size[0],size[2],(size[1]),mi_crv.mNode,os = True, relative = True)
        mi_crv.sz = d_size['z'] * 1.25
        mc.makeIdentity(mi_crv.mNode,apply=True, scale=True)
        
        #>>Copy tags and name
        mi_crv.addAttr('cgmName',attrType='string',value = 'hips')        
        mi_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
        mi_crv.doName()  
        
        #>>> Color
        curves.setCurveColorByName(mi_crv.mNode,l_moduleColors[0])        

        d_returnControls['hips'] = mi_crv.mNode
        
    """
        
        mc.makeIdentity(cogControl,apply=True, scale=True)
        """
    
    return d_returnControls
'''

"""
def limbControlMakerBAK(moduleNull,controlTypes = ['cog']):
    # 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    * Save the new positional information from the template objects
    * Collect all names of objects for a delete list
    * If anything in the module doesn't belong there, un parent it, report it
        * like a template object parented to another obect

    ARGUMENTS:
    moduleNull(string)
    controlTypes(list) = ['option1','option2']
    
    RETURNS:
    limbJoints(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #   
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Gather data
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # control helper objects - distance sorted#
    templateRoot =  modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateRoot')
    controlTemplateObjects =  modules.returnInfoNullObjects(moduleNull,'templateControlObjects',types='all')
    controlTemplateObjects = distance.returnDistanceSortedList(templateRoot,controlTemplateObjects)

    #size list of template control objects #
    controlTemplateObjectsSizes = []
    for obj in controlTemplateObjects:
        controlTemplateObjectsSizes.append(distance.returnAbsoluteSizeCurve(obj))
    
    # pos objects - distance sorted #
    posTemplateObjects =  modules.returnInfoNullObjects(moduleNull,'templatePosObjects',types='templateObject')
    posTemplateObjects = distance.returnDistanceSortedList(templateRoot,posTemplateObjects)

    
    # orientation objects - distance sorted #
    orientationTemplateObjects = []
    for obj in posTemplateObjects:
        orientationTemplateObjects.append(attributes.returnMessageObject(obj,'orientHelper'))
    
    orientationTemplateObjects = distance.returnDistanceSortedList(templateRoot,orientationTemplateObjects)
    

    returnControls = {}
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    #>>> Control Maker
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if 'spineIKHandle' in controlTypes:
        # initial create#
        ikHandleCurve = curves.createControlCurve('circleArrow2',1)
        mc.setAttr((ikHandleCurve+'.rz'),90)
        mc.setAttr((ikHandleCurve+'.ry'),90)
        mc.makeIdentity(ikHandleCurve, apply = True, r=True)
        startSizeBuffer = controlTemplateObjectsSizes[-1]
        scaleFactor = startSizeBuffer[0] * 1.25
        mc.setAttr((ikHandleCurve+'.sx'),1)
        mc.setAttr((ikHandleCurve+'.sy'),scaleFactor)
        mc.setAttr((ikHandleCurve+'.sz'),scaleFactor)
        position.moveParentSnap(ikHandleCurve,controlTemplateObjects[-1])
        position.movePointSnap(ikHandleCurve,orientationTemplateObjects[-1])
        
        # make our transform #
        transform = rigging.groupMeObject(controlTemplateObjects[-1],False)
        
        # connects shape #
        curves.parentShapeInPlace(transform,ikHandleCurve)
        mc.delete(ikHandleCurve)
        
        # copy over the pivot we want #
        rigging.copyPivot(transform,orientationTemplateObjects[-1])
        
        # Store data and name#
        attributes.copyUserAttrs(controlTemplateObjects[-1],transform,attrsToCopy=['cgmName'])
        attributes.storeInfo(transform,'cgmType','controlAnim')
        attributes.storeInfo(transform,'cgmTypeModifier','ik')
        transform = NameFactory.doNameObject(transform)
        returnControls['spineIKHandle'] = transform
    
    if 'ikHandle' in controlTypes:
        # initial create#
        ikHandleCurve = curves.createControlCurve('cube',1)
        endSizeBuffer = controlTemplateObjectsSizes[-1]
        mc.setAttr((ikHandleCurve+'.sx'),endSizeBuffer[0])
        mc.setAttr((ikHandleCurve+'.sy'),endSizeBuffer[1])
        mc.setAttr((ikHandleCurve+'.sz'),endSizeBuffer[1])
        position.moveParentSnap(ikHandleCurve,controlTemplateObjects[-1])
        position.movePointSnap(ikHandleCurve,orientationTemplateObjects[-1])
        
        # make our transform #
        transform = rigging.groupMeObject(controlTemplateObjects[-1],False)
        
        # connects shape #
        curves.parentShapeInPlace(transform,ikHandleCurve)
        mc.delete(ikHandleCurve)
        
        # copy over the pivot we want #
        rigging.copyPivot(transform,orientationTemplateObjects[-1])
        
        # Store data and name#
        attributes.copyUserAttrs(controlTemplateObjects[-1],transform,attrsToCopy=['cgmName'])
        attributes.storeInfo(transform,'cgmType','controlAnim')
        attributes.storeInfo(transform,'cgmTypeModifier','ik')
        transform = NameFactory.doNameObject(transform)
        returnControls['ikHandle'] = transform
        
    if 'twistFix' in controlTypes:
        # initial create#
        twistCurve = curves.createControlCurve('circleArrow1',1,'y+')
        startSizeBuffer = controlTemplateObjectsSizes[0]
        scaleFactor = startSizeBuffer[0] * 1.25
        mc.setAttr((twistCurve+'.sx'),1)
        mc.setAttr((twistCurve+'.sy'),scaleFactor)
        mc.setAttr((twistCurve+'.sz'),scaleFactor)
        position.moveParentSnap(twistCurve,orientationTemplateObjects[0])

        # make our transform #
        transform = rigging.groupMeObject(controlTemplateObjects[0],False)
        
        # connects shape #
        curves.parentShapeInPlace(transform,twistCurve)
        mc.delete(twistCurve)
        
        # copy over the pivot we want #
        rigging.copyPivot(transform,orientationTemplateObjects[0])
        
        # Store data and name#
        attributes.copyUserAttrs(controlTemplateObjects[0],transform,attrsToCopy=['cgmName'])
        attributes.storeInfo(transform,'cgmType','controlAnim')
        attributes.storeInfo(transform,'cgmTypeModifier','twist')
        transform = NameFactory.doNameObject(transform)
        returnControls['twistFix'] = transform
     
    if 'vectorHandleSpheres' in controlTypes:
        vectorHandles = []
        for obj in controlTemplateObjects[1:-1]:
            vectorHandleBuffer = []
            currentIndex = controlTemplateObjects.index(obj)
            vectorHandleCurve = curves.createControlCurve('sphere',1)
            sizeBuffer = controlTemplateObjectsSizes[currentIndex]
            scaleFactor = sizeBuffer[0]*.75
            mc.setAttr((vectorHandleCurve+'.sx'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sy'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sz'),scaleFactor)
            position.moveParentSnap(vectorHandleCurve,orientationTemplateObjects[currentIndex])
            
            # make our transform #
            transform = rigging.groupMeObject(obj,False)
            
            # connects shape #
            curves.parentShapeInPlace(transform,vectorHandleCurve)
            mc.delete(vectorHandleCurve)
            
            # copy over the pivot we want #
            rigging.copyPivot(transform,orientationTemplateObjects[currentIndex])
            
            # Store data and name#
            attributes.copyUserAttrs(obj,transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','ik')
            vectorHandleBuffer = NameFactory.doNameObject(transform)
            vectorHandles.append(vectorHandleBuffer)
            
            
        returnControls['vectorHandleSpheres'] = vectorHandles
        
    if 'vectorHandles' in controlTypes:
        vectorHandles = []
        for obj in controlTemplateObjects[1:-1]:
            vectorHandleBuffer = []
            currentIndex = controlTemplateObjects.index(obj)
            vectorHandleCurve = curves.createControlCurve('circleArrow',1)
            mc.setAttr((vectorHandleCurve+'.rx'),90)
            mc.makeIdentity(vectorHandleCurve, apply = True, r=True)
            sizeBuffer = controlTemplateObjectsSizes[currentIndex]
            scaleFactor = sizeBuffer[0]*1.5
            mc.setAttr((vectorHandleCurve+'.sx'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sy'),scaleFactor)
            mc.setAttr((vectorHandleCurve+'.sz'),scaleFactor)
            position.moveParentSnap(vectorHandleCurve,controlTemplateObjects[currentIndex])
            position.movePointSnap(vectorHandleCurve,orientationTemplateObjects[currentIndex])
            
            # make our transform #
            transform = rigging.groupMeObject(obj,False)
            
            # connects shape #
            curves.parentShapeInPlace(transform,vectorHandleCurve)
            mc.delete(vectorHandleCurve)
            
            # copy over the pivot we want #
            rigging.copyPivot(transform,orientationTemplateObjects[currentIndex])
            
            # Store data and name#
            attributes.copyUserAttrs(obj,transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','ik')
            vectorHandleBuffer = NameFactory.doNameObject(transform)
            vectorHandles.append(vectorHandleBuffer)
            
            
        returnControls['vectorHandles'] = vectorHandles
        
    if 'hips' in controlTypes:
        hipsCurve = curves.createControlCurve('semiSphere',1)
        mc.setAttr((hipsCurve+'.rx'),90)
        mc.makeIdentity(hipsCurve,apply=True,translate =True, rotate = True, scale=True)
        rootSizeBuffer = controlTemplateObjectsSizes[0]
        mc.setAttr((hipsCurve+'.sx'),rootSizeBuffer[0])
        mc.setAttr((hipsCurve+'.sy'),rootSizeBuffer[1])
        mc.setAttr((hipsCurve+'.sz'),rootSizeBuffer[0])
        position.moveParentSnap(hipsCurve,controlTemplateObjects[0])
        
        # make our transform #
        transform = rigging.groupMeObject(controlTemplateObjects[0],False)
        
        # connects shape #
        curves.parentShapeInPlace(transform,hipsCurve)
        mc.delete(hipsCurve)
        
        # Store data and name#
        attributes.storeInfo(transform,'cgmName','hips')
        attributes.storeInfo(transform,'cgmType','controlAnim')
        hips = NameFactory.doNameObject(transform)
        returnControls['hips'] = hips
            
    if 'cog' in controlTypes:
        cogControl = curves.createControlCurve('cube',1)
        rootSizeBuffer = controlTemplateObjectsSizes[0]
        mc.setAttr((cogControl+'.sx'),rootSizeBuffer[0]*1.05)
        mc.setAttr((cogControl+'.sy'),rootSizeBuffer[1]*1.05)
        mc.setAttr((cogControl+'.sz'),rootSizeBuffer[0]*.25)
        position.moveParentSnap(cogControl,controlTemplateObjects[0])
        
        mc.makeIdentity(cogControl,apply=True, scale=True)
        
        # Store data and name#
        attributes.storeInfo(cogControl,'cgmName','cog')
        attributes.storeInfo(cogControl,'cgmType','controlAnim')
        cogControl = NameFactory.doNameObject(cogControl)
        returnControls['cog'] = cogControl
    

    if 'limbControls' in controlTypes:
        limbControls = []
        controlSegments = lists.parseListToPairs(controlTemplateObjects)
        orientationSegments = lists.parseListToPairs(orientationTemplateObjects)
        cnt = 0
        for segment in controlSegments:
            # get our orientation segment buffer #
            orientationSegment = orientationSegments[cnt]
            #move distance #
            distanceToMove = distance.returnDistanceBetweenObjects(orientationSegment[0],orientationSegment[1])

            # root curve #
            rootCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[0])
            mc.setAttr((rootCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((rootCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((rootCurve+'.sz'),1)
            position.moveParentSnap(rootCurve,segment[0])
            #mc.move(0, 0, (distanceToMove * .15), rootCurve, r=True,os=True,wd=True)
            
            # end curve #
            endCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[1])
            mc.setAttr((endCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((endCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((endCurve+'.sz'),1)
            position.moveParentSnap(endCurve,segment[1])
            position.movePointSnap(endCurve,orientationSegment[1])
            mc.move(0, 0, -(distanceToMove * .15), endCurve, r=True,os=True,wd=True)
            
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>>> Side curves
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # locators on curve#
            side1Locs = []
            side2Locs = []
            frontLocs = []
            backLocs = []
            side1Locs.append(locators.locMeCvFromCvIndex(rootCurve,3))
            side1Locs.append(locators.locMeCvFromCvIndex(endCurve,3))
            side2Locs.append(locators.locMeCvFromCvIndex(rootCurve,7))
            side2Locs.append(locators.locMeCvFromCvIndex(endCurve,7))
            frontLocs.append(locators.locMeCvFromCvIndex(rootCurve,5))
            frontLocs.append(locators.locMeCvFromCvIndex(endCurve,5))
            backLocs.append(locators.locMeCvFromCvIndex(rootCurve,0))
            backLocs.append(locators.locMeCvFromCvIndex(endCurve,0))
            
            # get u positions for new curves#
            side1PosSet = []
            side2PosSet = []
            frontPosSet = []
            backPosSet = []
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[0],rootCurve))
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[1],endCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[0],rootCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[1],endCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[0],rootCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[1],endCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[0],rootCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[1],endCurve))

            # make side curves#
            sideCrv1 = mc.curve (d=1, p = side1PosSet , os=True)
            sideCrv2 = mc.curve (d=1, p = side2PosSet , os=True)
            frontCrv = mc.curve (d=1, p = frontPosSet , os=True)
            backCrv = mc.curve (d=1, p = backPosSet , os=True)
            
            # combine curves #
            mc.makeIdentity(rootCurve,apply=True,translate =True, rotate = True, scale=True)
            mc.makeIdentity(endCurve,apply=True,translate =True, rotate = True, scale=True)
            segmentCurveBuffer = curves.combineCurves([sideCrv1,sideCrv2,frontCrv,backCrv,rootCurve,endCurve])
            
            # delete locs #
            for loc in side1Locs,side2Locs,frontLocs,backLocs:
                mc.delete(loc)
                
            # make our transform #
            transform = rigging.groupMeObject(segment[0],False)
            
            # connects shape #
            curves.parentShapeInPlace(transform,segmentCurveBuffer)
            mc.delete(segmentCurveBuffer)
            
            # copy over the pivot we want #
            rigging.copyPivot(transform,orientationSegment[0])

                
            # Store data and name#
            attributes.copyUserAttrs(segment[0],transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','fk')
            limbControlBuffer = NameFactory.doNameObject(transform)
            limbControls.append(limbControlBuffer)
            
            cnt+=1
        returnControls['limbControls'] = limbControls
        
    if 'headControls' in controlTypes:
        headControls = []
        controlSegments = lists.parseListToPairs(controlTemplateObjects)
        orientationSegments = lists.parseListToPairs(orientationTemplateObjects)
        # figure out our second to last segment to do something a bit different #
        secondToLastCheck = (len(controlSegments)-2)
        print secondToLastCheck  
        cnt = 0
        for segment in controlSegments:
            # get our orientation segment buffer #
            orientationSegment = orientationSegments[cnt]            
            #move distance #
            distanceToMove = distance.returnDistanceBetweenObjects(segment[0],segment[1])

            # root curve #
            rootCurve = curves.createControlCurve('circle',1)
            rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[0])
            mc.setAttr((rootCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((rootCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((rootCurve+'.sz'),1)
            position.moveParentSnap(rootCurve,segment[0])
            mc.move(0, 0, (distanceToMove * .05), rootCurve, r=True,os=True,wd=True)
            
            # end curve #
            endCurve = curves.createControlCurve('circle',1)
            if cnt != secondToLastCheck:
                rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[1])
            else:
                rootSizeBuffer = distance.returnAbsoluteSizeCurve(segment[0])
            mc.setAttr((endCurve+'.sx'),rootSizeBuffer[0])
            mc.setAttr((endCurve+'.sy'),rootSizeBuffer[1])
            mc.setAttr((endCurve+'.sz'),1)
            position.moveParentSnap(endCurve,segment[1])
            mc.move(0, 0, -(distanceToMove * .05), endCurve, r=True,os=True,wd=True)
            
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            #>>> Side curves
            #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # locators on curve#
            side1Locs = []
            side2Locs = []
            frontLocs = []
            backLocs = []
            side1Locs.append(locators.locMeCvFromCvIndex(rootCurve,3))
            side1Locs.append(locators.locMeCvFromCvIndex(endCurve,3))
            side2Locs.append(locators.locMeCvFromCvIndex(rootCurve,7))
            side2Locs.append(locators.locMeCvFromCvIndex(endCurve,7))
            frontLocs.append(locators.locMeCvFromCvIndex(rootCurve,5))
            frontLocs.append(locators.locMeCvFromCvIndex(endCurve,5))
            backLocs.append(locators.locMeCvFromCvIndex(rootCurve,0))
            backLocs.append(locators.locMeCvFromCvIndex(endCurve,0))
            
            # get u positions for new curves#
            side1PosSet = []
            side2PosSet = []
            frontPosSet = []
            backPosSet = []
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[0],rootCurve))
            side1PosSet.append(distance.returnClosestUPosition(side1Locs[1],endCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[0],rootCurve))
            side2PosSet.append(distance.returnClosestUPosition(side2Locs[1],endCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[0],rootCurve))
            frontPosSet.append(distance.returnClosestUPosition(frontLocs[1],endCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[0],rootCurve))
            backPosSet.append(distance.returnClosestUPosition(backLocs[1],endCurve))

            # make side curves#
            sideCrv1 = mc.curve (d=1, p = side1PosSet , os=True)
            sideCrv2 = mc.curve (d=1, p = side2PosSet , os=True)
            frontCrv = mc.curve (d=1, p = frontPosSet , os=True)
            backCrv = mc.curve (d=1, p = backPosSet , os=True)
            
            # combine curves #
            mc.makeIdentity(rootCurve,apply=True,translate =True, rotate = True, scale=True)
            mc.makeIdentity(endCurve,apply=True,translate =True, rotate = True, scale=True)
            segmentCurveBuffer = curves.combineCurves([sideCrv1,sideCrv2,frontCrv,backCrv,rootCurve,endCurve])
            
            # delete locs #
            for loc in side1Locs,side2Locs,frontLocs,backLocs:
                mc.delete(loc)
                
            # make our transform #
            transform = rigging.groupMeObject(segment[0],False)
            
            # connects shape #
            curves.parentShapeInPlace(transform,segmentCurveBuffer)
            mc.delete(segmentCurveBuffer)
            
            # copy over the pivot we want #
            rigging.copyPivot(transform,orientationSegment[0])
              
            # Store data and name#
            attributes.copyUserAttrs(segment[0],transform,attrsToCopy=['cgmName'])
            attributes.storeInfo(transform,'cgmType','controlAnim')
            attributes.storeInfo(transform,'cgmTypeModifier','fk')
            segmentCurveBuffer = NameFactory.doNameObject(transform)
            headControls.append(segmentCurveBuffer)
            
            cnt+=1
        returnControls['headControls'] = headControls

    
    return returnControls"""


    
    
