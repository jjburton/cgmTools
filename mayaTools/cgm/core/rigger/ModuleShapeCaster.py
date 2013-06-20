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
from cgm.core.classes import SnapFactory as Snap
from cgm.core.lib import rayCaster as RayCast
from cgm.core.lib import shapeCaster as ShapeCast
reload(ShapeCast)
reload(RayCast)
reload(Snap)
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

from cgm.lib.classes import NameFactory
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
	                                'cap':self.build_moduleCap,
	                                'hand':self.build_handShape,
	                                'clavicle':self.build_clavicle,
	                                'settings':self.build_settings}
        # Get our base info
        #==============	        
        #>>> module null data
        if not moduleInstance.isModule():
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
        self._targetMesh = self._mi_module.modulePuppet.getUnifiedGeo() or self._mi_module.modulePuppet.getGeo()[0] or 'Morphy_Body_GEO1'#>>>>>>>>>>>>>>>>>this needs better logic   
	self.ml_targetObjects = cgmMeta.validateObjListArg(targetObjects, cgmMeta.cgmObject,noneValid=True)
        #>>> part name 
        self._partName = self._mi_module.getPartNameBase()
        self._partType = self._mi_module.moduleType or False
	
        self._direction = None
        if self._mi_module.hasAttr('cgmDirection'):
            self._direction = self._mi_module.cgmDirection or None
               
        #>>> Instances and joint stuff
        self._jointOrientation = str(modules.returnSettingsData('jointOrientation')) or 'zyx'#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<   
	self._skinOffset = self._mi_module.modulePuppet.getAttr('skinDepth') or 1 #Need to get from puppet!<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<		
	self._verifyCastObjects()#verify cast objects
	self.d_returnControls = {}	
	self.md_ReturnControls = {}	
	self.d_returnPivots = {}		
	self.md_returnPivots = {}   
	self.md_fkControls = {}
	self.md_segmentHandles = {}
	self._baseModuleDistance = self._returnBaseThickness()
	log.info("_baseModuleDistance: %s"%self._baseModuleDistance)
        #>>> We need to figure out which control to make
	#===================================================================================
	self.l_controlsToMakeArg = []	
	
	if controlTypes:#If we get an override
	    for c in controlTypes:
		if self._validateControlArg(c):
		    self.l_controlsToMakeArg.append(c)
	log.debug("l_controlsToMakeArg: %s"%self.l_controlsToMakeArg)
	    
	#self.d_controlShapes = mControlFactory.limbControlMaker(self.m,self.l_controlsToMakeArg)
	if not self.l_controlsToMakeArg:
	    log.info("No arguments for shapes to cast.Initializing only.")
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
	    
	if self.ml_specialLocs:
	    mc.delete([i_obj.mNode for i_obj in self.ml_specialLocs])

    def _validateControlArg(self,arg):
	"""returns function"""
	if arg in self.d_controlBuildFunctions.keys():
	    return True
	log.warning("_validateControlArg couldn't find: %s"%arg)
	return False
    
    def _pushKWsDict(self,d_kws = None,i=None):
	"""
	Pushes specific kws dict during 
	"""
	if type(d_kws) is not dict:
	    raise StandardError, "_pushKWsDict>> 'd_kws' arg not a dict: %s"%d_kws
	try:
	    log.info("_pushKWsDict >> " + "="*50)
	    if d_kws:
		#push d_kws
		if d_kws.get(i):
		    for k in d_kws[i].keys():
			log.info("%s: %s"%(k,d_kws[i].get(k)))
			self.__dict__[k] = d_kws[i].get(k)
		elif i == len(self.l_controlSnapObjects)-1 and d_kws.get(-1):
		    log.info('last mode')
		    for k in d_kws[-1].keys():
			log.info("%s: %s"%(k,d_kws[-1].get(k)))			
			self.__dict__[k] = d_kws[-1].get(k)
		else:
		    for k in d_kws['default'].keys():
			log.info("%s: %s"%(k,d_kws['default'].get(k)))			
			self.__dict__[k] = d_kws['default'].get(k)
	    log.info("_pushKWsDict << " + "="*50)
	    
	except StandardError,error:
	    raise StandardError,"_pushKWsDict>> failed to push arg: %s | %s"%(d_kws,error)
	return True

    def _verifyCastObjects(self):
	"""
	Some module types need more cast positions than exist (like a finger).
	This makes sure we have the ones we need and pushes them to the segment stuff
	"""
	self.l_controlSnapObjects = []
	for mi_obj in self.mi_templateNull.controlObjects:
	    self.l_controlSnapObjects.append(mi_obj.helper.mNode)  
	self.l_segmentControls = []
	self.l_segmentHandles = []
	self.ml_specialLocs = []
	
	#Create end locs
	#if self._mi_module.moduleType.lower() in ['finger','thumb']:
	if self._mi_module.moduleType.lower() in ['asdf']:	
	    mi_lastLoc = cgmMeta.cgmObject(self.l_controlSnapObjects[-1]).doLoc()	
	    mi_lastLoc.doGroup()
	    #Distance stuff    
	    d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,
	                                                          mi_lastLoc.mNode,
	                                                          self._jointOrientation[0]+'+',
	                                                          pierceDepth=self._skinOffset*15) or {}
	    if not d_return.get('hit'):
		raise StandardError,"go._verifyCastObjects>>failed to get hit to measure first distance"
	    dist_cast = distance.returnDistanceBetweenPoints(mi_lastLoc.getPosition(),d_return['hit']) * 1.25
	    mi_lastLoc.__setattr__("t"+self._jointOrientation[0],dist_cast*.6)#Move
	    pBuffer = mi_lastLoc.parent
	    mi_lastLoc.parent = False
	    mc.delete(pBuffer)
	    self.ml_specialLocs.append(mi_lastLoc)
	    self.l_controlSnapObjects.append(mi_lastLoc.mNode)
	    
	self.l_indexPairs = lists.parseListToPairs(list(range(len(self.l_controlSnapObjects))))
	self.l_segments = lists.parseListToPairs(self.l_controlSnapObjects)	    
	return True

    def _returnBaseThickness(self):
	#We're going to cast from the middle of our limb segment to reduce the chance of firing to nowhere
	#Start by casting along template up and out
	midIndex = int(len(self.l_controlSnapObjects)/2)
	d_return = ShapeCast.returnBaseControlSize(self.l_controlSnapObjects[midIndex],self._targetMesh,axis=[self._jointOrientation[1],self._jointOrientation[2]])
	l_lengths = [d_return[k] for k in d_return.keys()]
	average = (sum(l_lengths))/len(l_lengths)
	
	return average *1.25
	
    @r9General.Timer    
    def build_cog(self):
	try:
	    multiplier = 1.1
	    tmplRoot = self.mi_templateNull.root.mNode
	    mi_loc = cgmMeta.cgmNode(tmplRoot).doLoc()#make loc for sizing
	    mi_loc.doGroup()#group to zero
	    sizeReturn = ShapeCast.returnBaseControlSize(mi_loc,self._targetMesh,axis=['x','y'])#Get size
	    fl_size = sizeReturn.get('average')
	    mc.delete(mi_loc.parent)#delete loc	    
	    size = fl_size/2.5
	    ml_curvesToCombine = []
	    mi_crvBase = cgmMeta.cgmObject( curves.createControlCurve('arrowSingleFat3d',direction = 'y-',size = size,absoluteSize=False),setClass=True)
	    mi_crvBase.scaleY = 2
	    mi_crvBase.scaleZ = .75
	    Snap.go(mi_crvBase, tmplRoot) #Snap it
	    i_grp = cgmMeta.cgmObject( mi_crvBase.doGroup() )
	    
	    for i,rot in enumerate([0,90,90,90]):
		log.info(rot)
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
	    self.mi_rigNull.connectChildNode(mi_crv,'shape_cog','owner')
	    
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
	
	returnBuffer = ShapeCast.createWrapControlShape(mi_loc.mNode,self._targetMesh,
                                              curveDegree=3,
                                              insetMult = .2,
                                              closedCurve=True,
	                                      points = 8,
                                              posOffset = [0,0,self._skinOffset*3],
                                              extendMode='')
	mi_crvRound = returnBuffer['instance']
	
	str_traceCrv = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_loc.mNode,
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
	self.mi_rigNull.connectChildNode(mi_crv,'shape_hips','owner')
	
    	    
    @r9General.Timer    
    def build_segmentFKHandles(self):
	try:
	    l_segmentControls = []
	    ml_segmentControls = []
	    if self._partType == 'torso':
		l_segmentsToDo = self.l_segments[1:-1]
	    else:
		l_segmentsToDo = self.l_segments
	    log.info("segments: %s"%l_segmentsToDo)
	    self.l_specifiedRotates = None
	    d_kws = False
	    self.posOffset = [0,0,self._skinOffset*3]
	    self.maxDistance = self._baseModuleDistance
	    self.joinHits = [0,2,4,6,8]	  
	    self.points = 10
	    
	    if self._mi_module.moduleType.lower() in ['finger','thumb']:
		self.posOffset = [0,0,self._skinOffset/2]
		self.maxDistance = self._baseModuleDistance * .75
		self.joinHits = [0,5]	    
		    
	    for i,seg in enumerate(l_segmentsToDo):	
		if d_kws:		
		    self._pushKWsDict(d_kws,i)
		returnBuffer = ShapeCast.createWrapControlShape(seg,self._targetMesh,
		                                      points = self.points,
		                                      curveDegree=1,
		                                      insetMult = .2,
		                                      posOffset = self.posOffset,
		                                      joinMode=True,
		                                      maxDistance=self.maxDistance,		                                      
		                                      joinHits = self.joinHits,
		                                      extendMode='segment')
		mi_crv = returnBuffer['instance']	    
		#>>> Color
		curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
		mi_crv.addAttr('cgmType',attrType='string',value = 'segFKCurve',lock=True)	
		mi_crv.doName()
		
		#Store for return
		l_segmentControls.append( mi_crv.mNode )
		ml_segmentControls.append( mi_crv )
		
	    self.d_returnControls['segmentFK'] = l_segmentControls 
	    self.md_ReturnControls['segmentFK'] = ml_segmentControls
	    self.mi_rigNull.connectChildrenNodes(ml_segmentControls,'shape_segmentFK','owner')
	    
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
	    self.rootOffset = []
	    self.rootRotate = None
	    if 'neck' in self._partType:
		self.posOffset = [0,0,self._skinOffset*5]
		self.l_specifiedRotates = [-30,-10,0,10,30]
		self.latheAxis = 'z'
		self.aimAxis = 'y+'
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
	    elif 'arm' in self._partType:
		d_kws = {'default':{'closedCurve':True,
	                            'latheAxis':'z',
	                            'l_specifiedRotates':[],
	                            'rootOffset':[],
	                            'rootRotate':None},
	                 0:{}}	
		#d_kws[0]['l_specifiedRotates'] = [-90,-60,-30,0,30,60,90]
		#d_kws[0]['closedCurve'] = False
		
		self.posOffset = [0,0,self._skinOffset*2]
		if self._direction == 'left':
		    self.aimAxis = 'x+'
		else:self.aimAxis = 'x-'
		
	    elif self._partType in ['index','middle','ring','pinky','thumb','finger']:
		d_kws = {'default':{'closedCurve':True,
	                            'latheAxis':'z',
	                            'l_specifiedRotates':[],
		                    'maxDistance':self._baseModuleDistance,
	                            'rootOffset':[],
	                            'rootRotate':None},
	                 0:{}}	
		d_kws[0]['l_specifiedRotates'] = [-60,-30,0,30,60]
		d_kws[0]['maxDistance'] = self._baseModuleDistance * 10	
		d_kws[0]['closedCurve'] = False
		self.posOffset = [0,0,self._skinOffset/2]
		
	    log.info("Snap Objects: %s"%self.l_controlSnapObjects)
	    for i,obj in enumerate(self.l_controlSnapObjects):			
		#make ball
		self._pushKWsDict(d_kws,i)
			    
		#Few more special cases
		if cgmMeta.cgmObject(obj).getAttr('cgmName') in ['ankle']:
		    log.info('Special rotate mode')
		    self.rootRotate = [0,0,0]
		    self.latheAxis = 'y'
		returnBuffer = ShapeCast.createWrapControlShape(obj,self._targetMesh,
	                                              curveDegree=3,
	                                              insetMult = .2,
		                                      closedCurve= self.closedCurve,
		                                      aimAxis = self.aimAxis,
		                                      latheAxis = self.latheAxis,
		                                      l_specifiedRotates = self.l_specifiedRotates,
	                                              posOffset = self.posOffset,
		                                      rootOffset = self.rootOffset,
		                                      rootRotate = self.rootRotate,
		                                      maxDistance=self._baseModuleDistance,
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
	    self.mi_rigNull.connectChildrenNodes(ml_segmentControls,'shape_segmentFKLoli','owner')
	    
	except StandardError,error:
		log.error("build_segmentFKLoliHandles fail! | %s"%error) 
		return False
	    
	    
    @r9General.Timer    
    def build_moduleCap(self):
	try:
	    l_segmentControls = []
	    ml_segmentControls = []

	    #figure out our settings
	    #================================================================
	    #defaults first
	    d_kws = {}
	    self.posOffset = []
	    self.l_specifiedRotates = None
	    self.joinMode = False
	    self.closedCurve = True
	    self.latheAxis = self._jointOrientation[0]
	    self.aimAxis = self._jointOrientation[1] + '+'
	    self.rotateBank = None	
	    self.rootOffset = []
	    self.rootRotate = None	
	    _snapObject = self.l_controlSnapObjects[-1]
	    self.maxDistance = self._baseModuleDistance
	    if self._partType in ['index','middle','ring','pinky','thumb','finger']:
		d_kws = {'default':{'rootOffset':[],
		                    'maxDistance': self._baseModuleDistance * 1.5,
		                    'posOffset':[0,0,self._skinOffset/2],
	                            'rootRotate':None},
	                 0:{}}	
		_snapObject = self.l_controlSnapObjects[-2]
		
	    #>>>Cast
	    self._pushKWsDict(d_kws)
	    log.info("snapObject: %s"%_snapObject)
	    returnBuffer = ShapeCast.createWrapControlShape(_snapObject,self._targetMesh,
	                                                    curveDegree=3,
	                                                    insetMult = .2,
	                                                    closedCurve= self.closedCurve,
	                                                    aimAxis = self.aimAxis,
	                                                    latheAxis = self.latheAxis,
	                                                    l_specifiedRotates = self.l_specifiedRotates,
	                                                    posOffset = self.posOffset,
	                                                    rootOffset = self.rootOffset,
	                                                    rootRotate = self.rootRotate,
	                                                    maxDistance=self.maxDistance,
	                                                    extendMode='endCap')
	    mi_newCurve = returnBuffer['instance']
	    mi_newCurve.doCopyPivot(_snapObject)
	    
	    #>>> Color
	    curves.setCurveColorByName(mi_newCurve.mNode,self.l_moduleColors[0])                    
	    mi_newCurve.addAttr('cgmType',attrType='string',value = 'moduleCap',lock=True)	
	    mi_newCurve.doName()
	    
	    #Store for return
	    l_segmentControls.append( mi_newCurve.mNode )
	    ml_segmentControls.append( mi_newCurve )		
		
	    self.d_returnControls['moduleCap'] = l_segmentControls 
	    self.md_ReturnControls['moduleCap'] = ml_segmentControls
	    self.mi_rigNull.connectChildrenNodes(ml_segmentControls,'shape_moduleCap','owner')
	    
	except StandardError,error:
		log.error("build_moduleCap fail! | %s"%error) 
		return False
    @r9General.Timer    
    def build_clavicle(self):
	"""
	build foot shape and pivot locs at the same time
	"""
	l_segmentControls = []
	ml_SegmentControls = []
	mi_startObj = False
	mi_endObj = False
	
	#Our controls
	#============================================================================	
	#find the foot. 1) Build search dict	
	ml_controlSnapObjects = []
	for mi_obj in self._mi_module.templateNull.controlObjects:
	    ml_controlSnapObjects.append(mi_obj.helper)  
	log.info("helperObjects: %s"%[i_obj.getShortName() for i_obj in ml_controlSnapObjects])
	if len(ml_controlSnapObjects) > 2:
	    raise StandardError,"go.build_clavicle>>> Must have only 2 control objects. Found: %s"%(len(ml_controlSnapObjects))

	mi_startObj = ml_controlSnapObjects[0]
	mi_endObj = ml_controlSnapObjects[1]
	
	#Get our helper objects
	#============================================================================
	mi_startLoc = mi_startObj.doLoc()
	mi_endLoc = mi_endObj.doLoc()

	#Get our distance for our casts
	if self._direction == 'left':
	    self.aimAxis = self._jointOrientation[2] + '-'
	    axis_distanceDirectionCast = self._jointOrientation[2] + '+'
	    l_specifiedRotates = [-15,-30,-90,-120,-180]
	    rootRotate = -30
	else:
	    self.aimAxis = self._jointOrientation[2] + '+'
	    axis_distanceDirectionCast = self._jointOrientation[2] + '-'	    
	    l_specifiedRotates = [15,30,90,120,180]
	    rootRotate = 30	    

	dist_inset = distance.returnDistanceBetweenPoints(mi_endLoc.getPosition(),mi_startLoc.getPosition()) *.3
	
	#Move our cast locs
	mi_startLoc.doGroup()#zero
	mi_endLoc.doGroup()#zero
	mi_startLoc.__setattr__('t%s'%self._jointOrientation[0],dist_inset)
	mi_endLoc.__setattr__('t%s'%self._jointOrientation[0],-dist_inset/2)	
	mi_startLoc.__setattr__('r%s'%self._jointOrientation[1],rootRotate)
	mi_endLoc.__setattr__('r%s'%self._jointOrientation[1],rootRotate)
	
	mi_castLoc = mi_startLoc.doDuplicate()

	Snap.go(mi_castLoc,self._targetMesh,True,False,midSurfacePos=True, axisToCheck = [self._jointOrientation[2]])
	
	#Distance stuff    
	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh, mi_endLoc.mNode, axis_distanceDirectionCast, pierceDepth=self._skinOffset*2) or {}
	if not d_return.get('hit'):
	    raise StandardError,"go.build_clavicle>>failed to get hit to measure first distance"
	dist_cast = distance.returnDistanceBetweenPoints(mi_endLoc.getPosition(),d_return['hit']) * 1.25
	
	log.info("go.build_clavicle>>cast distance: %s"%dist_cast)
	log.info("go.build_clavicle>>inset distance: %s"%dist_inset)
	
	#Cast our stuff
	#============================================================================
	self.posOffset = [0,0,self._skinOffset*3]
	self.latheAxis = self._jointOrientation[0]
	log.info("aim: %s"%self.aimAxis)
	log.info("lathe: %s"%self.latheAxis)
	
	d_startReturn = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_startLoc.mNode,offsetMode='vector',maxDistance = dist_cast,l_specifiedRotates = l_specifiedRotates,
	                                closedCurve = False,curveDegree=3,midMeshCast=True,axisToCheck=['x'],posOffset = self.posOffset,returnDict = True,
	                                latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=False)
	
	d_endReturn = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_endLoc.mNode,offsetMode='vector',maxDistance = dist_cast,l_specifiedRotates = l_specifiedRotates,
	                                closedCurve = False,curveDegree=3,midMeshCast=True,axisToCheck=['x'],posOffset = self.posOffset,returnDict = True,
	                                latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=False)
	
	
	#Let's collect the points to join
    
	l_curvesToCombine = [d_startReturn['curve'],d_endReturn['curve']]	
	
	joinReturn = ShapeCast.joinCurves(l_curvesToCombine)
	
	l_curvesToCombine.extend(joinReturn)
	
	mc.delete([mi_startLoc.parent,mi_endLoc.parent])
	
	#Combine and finale
	#============================================================================
	newCurve = curves.combineCurves(l_curvesToCombine) 
	mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(mi_startObj.mNode,False) )
	curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
	mc.delete(newCurve)
	
	#>>> Color
	curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
	mi_crv.doCopyNameTagsFromObject(mi_startObj.mNode,ignore = ['cgmType'])
	mi_crv.addAttr('cgmType',attrType='string',value = 'clavicle',lock=True)	    
	mi_crv.doName()
	    
	self.d_returnControls['clavicle'] = mi_crv.mNode 		
	self.md_ReturnControls['clavicle'] = mi_crv	
	self.mi_rigNull.connectChildNode(mi_crv,'shape_clavicle','owner')
	
	    
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


	    returnBuffer = ShapeCast.createWrapControlShape(mi_mid.mNode,self._targetMesh,
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
	    mi_newCurve.addAttr('cgmType',attrType='string',value = 'midIK',lock=True)	
	    mi_newCurve.doName()
	    
	    #Store for return
	    l_segmentControls.append( mi_newCurve.mNode )
	    ml_segmentControls.append( mi_newCurve )		
		
	    self.d_returnControls['midIK'] = mi_newCurve.mNode 
	    self.md_ReturnControls['midIK'] = mi_newCurve
	    self.mi_rigNull.connectChildNode(mi_newCurve,'shape_midIK','owner')
	    
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
		d_size = ShapeCast.returnBaseControlSize(i_target,self._targetMesh,axis=[self._jointOrientation[1],self._jointOrientation[2]])#Get size			
		l_size = d_size.get('average')
		size = sum(l_size)/1.5
		
		log.debug("loli size return: %s"%d_size)
		log.debug("loli size: %s"%size)
		i_ball = cgmMeta.cgmObject(curves.createControlCurve('sphere',size = size/4))
		Snap.go(i_ball,i_target.mNode,True, True)#Snap to main object
		
		#make ball
		returnBuffer = ShapeCast.createWrapControlShape(i_target.mNode,self._targetMesh,
	                                              curveDegree=3,
	                                              insetMult = .2,
		                                      closedCurve=False,
		                                      maxDistance=self._baseModuleDistance,		                                      
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
	    ml_segmentControls = []
	    
	    l_segmentsToDo = self.l_segments[1:]

	    for i,seg in enumerate(l_segmentsToDo):
		returnBuffer = ShapeCast.createWrapControlShape(seg,self._targetMesh,
		                                      points = 8,
		                                      curveDegree=3,
		                                      insetMult = .05,
		                                      posOffset = [0,0,self._skinOffset*3],
		                                      joinMode=True,
		                                      maxDistance=self._baseModuleDistance,		                                      
		                                      extendMode='disc')
		mi_crv = returnBuffer['instance']	    
		#>>> Color
		curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[1])                    
		mi_crv.addAttr('cgmType',attrType='string',value = 'segIKCurve',lock=True)	
		mi_crv.doName()
		
		#Store for return
		l_segmentControls.append( mi_crv.mNode )
		ml_segmentControls.append( mi_crv )
		
	    self.d_returnControls['segmentIK'] = l_segmentControls 
	    self.md_ReturnControls['segmentIK'] = ml_segmentControls
	    self.mi_rigNull.connectChildrenNodes(ml_segmentControls,'shape_segmentIK','owner')
	    
	    if len(self.l_segments)>2:
		objects = self.l_controlSnapObjects[-2:]
	    else:
		objects = self.l_segments[-1]
	    #"""l_specifiedRotates = [0,30,60,160,180,200,220,300,330]"""
	    returnBuffer = ShapeCast.createWrapControlShape(self.l_segments[-1],self._targetMesh,
	                                          points = 12 ,
	                                          curveDegree=3,
	                                          insetMult = .05,
	                                          posOffset = [0,0,self._skinOffset*3],
	                                          joinHits = [0,6],	                                          
	                                          joinMode=True,
	                                          maxDistance=self._baseModuleDistance*.6,
	                                          extendMode='segment')
	    mi_crv = returnBuffer['instance']
	    
	    #>>> Color
	    curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
	    mi_crv.doCopyNameTagsFromObject(self.l_controlSnapObjects[-1],ignore = ['cgmType'])
	    mi_crv.addAttr('cgmType',attrType='string',value = 'ikCurve',lock=True)	    
	    mi_crv.doName()
		
	    self.d_returnControls['segmentIKEnd'] = mi_crv.mNode 		
	    self.md_ReturnControls['segmentIKEnd'] = mi_crv
	    self.mi_rigNull.connectChildNode(mi_crv,'shape_handleIK','owner')
		
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
	self.settingsVector = [0,1,0]	    	
	self.gearVector = [0,0,-1]
	_moveMultiplier = 1.5
	_direction = self.outAxis+'+'
	index = -1
	index_size = index
	if self._partType == 'leg':
	    index = -2
	    index_size = -2
	    self.settingsVector = [0,0,-1]
	elif self._partType == 'arm':
	    index_size = 1
	    index = 0    
	    _direction = self.aimAxis	    
	    #self.settingsVector = [0,1,0]	    	
	    self.settingsVector = [0,1,0]
	    _moveMultiplier = 1.5
	
	i_target = cgmMeta.cgmObject( self.l_controlSnapObjects[index] )
	i_sizeTarget = cgmMeta.cgmObject( self.l_controlSnapObjects[index_size] )

	mi_rootLoc = i_target.doLoc()
	mi_sizeLoc = i_sizeTarget.doLoc()

	    
	d_size = ShapeCast.returnBaseControlSize(mi_sizeLoc,self._targetMesh,axis=[self.outAxis])#Get size
	baseSize = d_size.get(d_size.keys()[0])
	log.info("build_settings>>> baseSize: %s"%baseSize)
		
	i_gear = cgmMeta.cgmObject(curves.createControlCurve('gear',size = baseSize,direction=_direction))	
	
	#Move stuff
	Snap.go(i_gear.mNode,mi_rootLoc.mNode,True, False)#Snap to main object
	
	#Move the ball
	d_return = RayCast.findMeshIntersectionFromObjectAxis(self._targetMesh,mi_rootLoc.mNode,vector = self.settingsVector,singleReturn=True)
	if not d_return.get('hit'):
	    raise StandardError,"go.build_settings>>failed to get hit to measure distance"
	
	mc.move(d_return['hit'][0],d_return['hit'][1],d_return['hit'][2],i_gear.mNode,absolute = True,ws=True)
	Snap.go(i_gear.mNode,mi_rootLoc.mNode,move = False, orient = False, aim=True, aimVector=[0,0,-1])
	
	mc.move(self.posOffset[0]*_moveMultiplier,self.posOffset[1]*_moveMultiplier,self.posOffset[2]*_moveMultiplier, [i_gear.mNode], r = True, rpr = True, os = True, wd = True)
    
	mi_rootLoc.delete()
	mi_sizeLoc.delete()
	
	#Combine and finale
	#============================================================================
	i_gear.doCopyPivot(i_target.mNode)
	#>>> Color
	curves.setCurveColorByName(i_gear.mNode,self.l_moduleColors[0])                    
	#i_gear.doCopyNameTagsFromObject(i_target.mNode,ignore = ['cgmType'])
	i_gear.addAttr('cgmName',self._partName,attrType='string',lock=True)	    
	i_gear.addAttr('cgmType',attrType='string',value = 'settings',lock=True)	    
	i_gear.doName()
	    
	self.d_returnControls['settings'] = i_gear.mNode 		
	self.md_ReturnControls['settings'] = i_gear		
	self.mi_rigNull.connectChildNode(i_gear,'shape_settings','owner')
	
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
	mi_ballPivot.addAttr('cgmTypeModifier','templatePivot',lock=True)
	mi_ballPivot.doName()
	self.d_returnPivots['ball'] = mi_ballPivot.mNode 		
	self.md_returnPivots['ball'] = mi_ballPivot	
	
	#Toe pivot
	mi_toePivot =  mi_ballLoc.doLoc()
	mc.move (d_return['hit'][0],d_return['hit'][1],d_return['hit'][2], mi_toePivot.mNode)
	mi_toePivot.__setattr__('r%s'%self._jointOrientation[2],0)
	mi_toePivot.__setattr__('t%s'%self._jointOrientation[1],0)
	mi_toePivot.addAttr('cgmName','toe',lock=True)	
	mi_toePivot.addAttr('cgmTypeModifier','templatePivot',lock=True)
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
	mi_innerPivot.addAttr('cgmTypeModifier','templatePivot',lock=True)
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
	mi_outerPivot.addAttr('cgmTypeModifier','templatePivot',lock=True)
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
	mi_heelPivot.addAttr('cgmTypeModifier','templatePivot',lock=True)
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
	dist = distance.returnDistanceBetweenPoints(mi_ballLoc.getPosition(),d_return['hit']) *1.25
	log.info("go.build_footShape>>front distance: %s"%dist)
	
	#Pivots
	#===================================================================================
	"""
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
	"""
	#Cast our stuff
	#============================================================================
	self.posOffset = [0,0,self._skinOffset*3]
	self.latheAxis = self._jointOrientation[1]
	self.aimAxis = self._jointOrientation[0] + '+'
	
	if self._direction == 'left':
	    l_specifiedRotates = [-40,-20,0,20,60,80]
	    
	else:
	    l_specifiedRotates = [40,20,0,-20,-60,-80]
	    
	d_return = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_ballLoc.mNode,offsetMode='vector',maxDistance = dist,l_specifiedRotates = l_specifiedRotates,
	                                closedCurve = False,curveDegree=1,posOffset = self.posOffset,returnDict = True,
	                                latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=False)
	str_frontCurve = d_return['curve']
	
	#Heel cast

	self.aimAxis = self._jointOrientation[0] + '-'	
	if self._direction == 'left':
	    l_specifiedRotates = [-90,-60,-20,-10,0,10,20,40,60,80]#foot back, closed false, closest in range false
	    
	else:
	    l_specifiedRotates = [90,60,20,10,0,-10,-20,-40,-60,-80]
	d_return = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_heelLoc.mNode,offsetMode='vector',maxDistance = 1000,l_specifiedRotates = l_specifiedRotates,
	                                closedCurve = False,curveDegree=1,posOffset = self.posOffset,returnDict = True,
	                                latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=True)
	str_backCurve = d_return['curve']
	
	#side cast
	self.aimAxis = self._jointOrientation[0] + '+'
	if self._direction == 'left':
	    l_specifiedRotates = [-100,-80,-50]#foot front closest, closed false, closest in range true
	    
	else:
	    l_specifiedRotates =  [100,80,50]
	    
	d_return = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_ballLoc.mNode,offsetMode='vector',maxDistance = 1000,l_specifiedRotates = l_specifiedRotates,
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
	self.mi_rigNull.connectChildNode(mi_crv,'shape_foot','owner')
	
    def build_handShape(self):
	"""
	build hand shape and pivot locs at the same time
	"""
	log.info("in build_handShape")
	l_segmentControls = []
	ml_SegmentControls = []
	mi_handModule = False
	mi_palm = False
	mi_wrist = False
	
	#Find our hand
	#============================================================================	
	if self._partType == 'hand':
	    raise NotImplementedError,"haven't implemented hand"
	elif self._partType == 'armSimple':
	    raise NotImplementedError,"haven't implemented hand"
	
	    """
	    #find the hand. 1) Build search dict
	    d_search = {'moduleType':'hand'}
	    for key in ['cgmDirection','cgmPosition']:
		buffer = self._mi_module.getAttr(key)
		if buffer:
		    d_search[key] = buffer
	    #Find it
	    mi_handModule = self._mi_module.modulePuppet.getModuleFromDict(d_search)
	    ml_children = self._mi_module.moduleChildren
	    if mi_handModule in ml_children:log.info("found match modules: %s"%mi_handModule)
	    
	    ml_controlSnapObjects = []
	    for mi_obj in mi_handModule.templateNull.controlObjects:
		ml_controlSnapObjects.append(mi_obj.helper)  
	    log.info("helperObjects: %s"%[i_obj.getShortName() for i_obj in ml_controlSnapObjects])
	    if ml_controlSnapObjects[1].cgmName != 'palm':
		raise StandardError,"go.build_handShape>>> Expected second snap object to be 'palm'. Found: %s"%ml_controlSnapObjects[1].mNode
	    mi_palm = ml_controlSnapObjects[1]
	    mi_wrist = ml_controlSnapObjects[0]"""
	    
	elif self._partType == 'arm':
	    for obj in self.l_controlSnapObjects:
		if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'wrist':
		    mi_wrist = cgmMeta.cgmObject(obj)
		    break
	    for obj in self.l_controlSnapObjects:
		if cgmMeta.cgmObject(obj).getAttr('cgmName') == 'palm':
		    mi_palm = cgmMeta.cgmObject(obj)
		    break
		
	if not mi_wrist:
	    raise StandardError,"go.build_handShape>>> Haven't found a wrist to build from"
	
	#Get our helper objects
	#============================================================================
	mi_wristLoc = mi_wrist.doLoc()
	d_wristSize = ShapeCast.returnBaseControlSize(mi_wristLoc.mNode,self._targetMesh,[self._jointOrientation[1],self._jointOrientation[2]])
	#Average the wrist size
	dist_wristSize = d_wristSize.get('average')
	log.info("dist_wristSize: %s"%dist_wristSize)	
	
	if mi_palm:
	    mi_palmLoc = mi_palm.doLoc()
	else:
	    mi_palmLoc = mi_wristLoc.doDuplicate()
	    mi_palmLoc.doGroup()
	    mi_palmLoc.__setattr__('t%s'%self._jointOrientation[0],dist_wristSize/2)
	    
	mi_wristLoc.doGroup()
	mi_wristLoc.__setattr__('t%s'%self._jointOrientation[0],-dist_wristSize/2)

	#Get our distance for our casts
	if self._direction == 'left':
	    self.aimAxis = self._jointOrientation[2] + '-'
	    axis_distanceDirectionCast = self._jointOrientation[2] + '+'
	    rootRotate = -30
	else:
	    self.aimAxis = self._jointOrientation[2] + '+'
	    axis_distanceDirectionCast = self._jointOrientation[2] + '-'	    
	    rootRotate = 30	   

	#Distance stuff    
	d_return = RayCast.findFurthestPointInRangeFromObject(self._targetMesh,mi_palmLoc.mNode,axis_distanceDirectionCast,pierceDepth=self._skinOffset*15) or {}
	if not d_return.get('hit'):
	    raise StandardError,"go.build_clavicle>>failed to get hit to measure first distance"
	dist_cast = distance.returnDistanceBetweenPoints(mi_palmLoc.getPosition(),d_return['hit']) * 4
	
	#Cast our stuff
	#============================================================================
	self.posOffset = [0,0,self._skinOffset*3]
	self.latheAxis = self._jointOrientation[0]
	log.info("aim: %s"%self.aimAxis)
	log.info("lathe: %s"%self.latheAxis)
	log.info("dist: %s"%dist_cast)
	
	d_startReturn = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_wristLoc.mNode,offsetMode='vector',maxDistance = dist_cast,
	                                               closedCurve = True,curveDegree=3,midMeshCast=True,axisToCheck=[self._jointOrientation[1],self._jointOrientation[2]],posOffset = self.posOffset,returnDict = True,
	                                               latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=True)
	
	d_endReturn = ShapeCast.createMeshSliceCurve(self._targetMesh,mi_palmLoc.mNode,offsetMode='vector',maxDistance = dist_cast,
	                                             closedCurve = True,curveDegree=3,midMeshCast=True,axisToCheck=[self._jointOrientation[1],self._jointOrientation[2]],posOffset = self.posOffset,returnDict = True,
	                                             latheAxis=self.latheAxis,aimAxis=self.aimAxis,closestInRange=True)
	
	
	#Let's collect the points to join
	l_curvesToCombine = [d_startReturn['curve'],d_endReturn['curve']]	
	joinReturn = ShapeCast.joinCurves(l_curvesToCombine)
	
	l_curvesToCombine.extend(joinReturn)
	
	mc.delete([mi_wristLoc.parent,mi_palmLoc.parent])
	
	#Combine and finale
	#============================================================================
	newCurve = curves.combineCurves(l_curvesToCombine) 
	mi_crv = cgmMeta.cgmObject( rigging.groupMeObject(mi_wrist.mNode,False) )
	curves.parentShapeInPlace(mi_crv.mNode,newCurve)#Parent shape
	mc.delete(newCurve)
	
	#>>> Color
	curves.setCurveColorByName(mi_crv.mNode,self.l_moduleColors[0])                    
	mi_crv.doCopyNameTagsFromObject(mi_wrist.mNode,ignore = ['cgmType'])
	mi_crv.addAttr('cgmType',attrType='string',value = 'hand',lock=True)	    
	mi_crv.doName()
	    
	self.d_returnControls['hand'] = mi_crv.mNode 		
	self.md_ReturnControls['hand'] = mi_crv	
	self.mi_rigNull.connectChildNode(mi_crv,'shape_hand','owner')	
	
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
	self.midMeshCast = True
	self.axisToCheck = [self._jointOrientation[1]]
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
	    """Use influence joints to cast these"""
	    l_objectsToDo = self.l_controlSnapObjects[:-1]
	    self.posOffset = [0,0,self._skinOffset*2]
	    self.points = 12
	    d_kws = {'default':{'closedCurve':True,
	                        'l_specifiedRotates':[],
	                        'insetMult':.15,
	                        'rootRotate':None,
	                        'rootOffset':[],
	                        'rotateBank':[]},
	             0:{'rootOffset':[0,0,self._skinOffset*4]},
	             -1:{'rootOffset':[0,0,-self._skinOffset*4]}}
	    
	    if self._direction == 'left':
		self.aimAxis = 'x+'
		d_kws['default']['aimAxis']= 'x+'
		d_kws[0]['rotateBank'] = -10
	    else:
		self.aimAxis = 'x-'		
		d_kws['default']['aimAxis']= 'x-'
		d_kws[0]['rotateBank'] = 10
		
	elif self._partType == 'arm':
	    self.posOffset = [0,0,self._skinOffset*2]
	    self.points = 12
	    d_kws = {'default':{'closedCurve':True,
	                        'l_specifiedRotates':[],
	                        'insetMult':.15,
	                        'rootRotate':None,
	                        'rootOffset':[],
	                        'rotateBank':[]},
	             0:{'rootOffset':[0,0,self._skinOffset*3]},
	             -1:{'rootOffset':[0,0,-self._skinOffset*3]}}
	    
	    if self._direction == 'left':
		self.aimAxis = 'x+'
		d_kws['default']['aimAxis']= 'x+'
		d_kws[0]['rotateBank'] = -10
	    else:
		self.aimAxis = 'x-'		
		d_kws['default']['aimAxis']= 'x-'
		d_kws[0]['rotateBank'] = 10
		
	if self.ml_targetObjects:
	    l_objectsToDo = [i_o.mNode for i_o in self.ml_targetObjects]
	elif not l_objectsToDo:
	    l_objectsToDo = self.l_controlSnapObjects
	    
	for i,obj in enumerate(l_objectsToDo):
	    log.info(obj)
	    self._pushKWsDict(d_kws,i)

	    log.info(">>>>>>>>>>>aim: %s"%self.aimAxis)
	    log.info(">>>>>>>>>> lathe: %s"%self.latheAxis)
	    log.info(">>>>>>>>>> l_specifiedRotates: %s"%self.l_specifiedRotates)
	    log.info(">>>>>>>>>> distance: %s"%self.maxDistance)
	    #Few more special cases
	    if cgmMeta.cgmObject(obj).getAttr('cgmName') in ['ankle'] and not self.ml_targetObjects:
		log.info('Special rotate mode')
		self.rootRotate = [0,0,0]
		self.latheAxis = 'y'	 
		
	    if cgmMeta.cgmObject(obj).getAttr('cgmName') in ['hip']:
		self.l_specifiedRotates = [-40,-30,-15,0,15,30,40]
		self.closedCurve = False
	    returnBuffer = ShapeCast.createWrapControlShape(obj,self._targetMesh,
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
	                                          midMeshCast = self.midMeshCast,
	                                          l_specifiedRotates = self.l_specifiedRotates,
	                                          joinMode=self.joinMode,
	                                          extendMode='disc',
	                                          axisToCheck = self.axisToCheck)
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
	self.mi_rigNull.connectChildrenNodes(ml_SegmentControls,'shape_segmentIK','owner')
	    
	#except StandardError,error:
	#	log.error("build_segmentIKHandles! | %s"%error) 
	#	return False