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
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.lib import rayCaster as RayCast
from cgm.core.rigger.lib import rig_Utils as rUtils
reload(rUtils)

from cgm.lib import (attributes,
                     cgmMath,
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
    def __init__(self,moduleInstance,controlTypes = [],storageInstance = False,**kws): 
        """
	Class factor generating module controls
	
        @kws
	moduleInstance -- must be a module instance
        """
	self.d_controlBuildFunctions = {'cog':self.build_cog,
	                                'hips':self.build_hips,
	                                'segmentFK':self.build_segmentFKHandles,
	                                'segmentIK':self.build_segmentIKHandles}
	
        # Get our base info
        #==============	        
        #>>> module null data
	try:
	    if moduleInstance.isModule():
		i_module = moduleInstance
	except StandardError,error:
	    raise StandardError,"RigFactory.go.init. Module call failure. Probably not a module: '%s'"%error	    
		
	if not mc.objExists(moduleInstance.mNode):
	    raise StandardError,"RigFactory.go.init Module instance no longer exists: '%s'"%moduleInstance
	
	if type(controlTypes) is not list:controlTypes = [controlTypes]
        assert moduleInstance.isTemplated(),"Module is not templated: '%s'"%moduleInstance.getShortName()        
        assert moduleInstance.isSkeletonized(),"Module is not skeletonized: '%s'"%moduleInstance.getShortName()
        
        log.debug(">>> ModuleControlFactory.go.__init__")
        self._i_module = moduleInstance# Link for shortness	
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
        self.l_moduleColors = self._i_module.getModuleColors()
        self.l_coreNames = self._i_module.coreNames.value
        self.i_templateNull = self._i_module.templateNull#speed link
	self.i_rigNull = self._i_module.rigNull#speed link
        self._targetMesh = self._i_module.modulePuppet.getGeo() or 'Morphy_Body_GEO1'#>>>>>>>>>>>>>>>>>this needs better logic   
               
        #>>> part name 
        self._partName = self._i_module.getPartNameBase()
        self._partType = self._i_module.moduleType or False
	
        self._direction = None
        if self._i_module.hasAttr('cgmDirection'):
            self._direction = self._i_module.cgmDirection or None
               
        #>>> Instances and joint stuff
        self._jointOrientation = str(modules.returnSettingsData('jointOrientation')) or 'zyx'#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<   
	self.l_controlSnapObjects = []
	for i_obj in self.i_templateNull.controlObjects:
	    self.l_controlSnapObjects.append(i_obj.helper.mNode)  
	self._skinOffset = 3 #Need to get from puppet!<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	self.l_segmentControls = []
	self.l_segmentHandles = []
	self.l_indexPairs = lists.parseListToPairs(list(range(len(self.l_controlSnapObjects))))
	self.l_segments = lists.parseListToPairs(self.l_controlSnapObjects)		
	self.d_returnControls = {}	
	self.md_ReturnControls = {}	
        
        #>>> We need to figure out which control to make
	#===================================================================================
	self.l_controlsToMakeArg = []	
	
	if controlTypes:#If we get an override
	    for c in controlTypes:
		if self.validateControlArg(c):
		    self.l_controlsToMakeArg.append(c)
	else:
	    if not self._i_module.getMessage('moduleParent'):
		self.l_controlsToMakeArg.append('cog')
	    #if self.i_rigNull.ik:
		#self.l_controlsToMakeArg.extend(['vectorHandles'])
		#if self._partType == 'torso':#Maybe move to a dict?
		    #self.l_controlsToMakeArg.append('spineIKHandle')            
	    if self.i_rigNull.fk:
		self.l_controlsToMakeArg.extend(['segmentFK','segmentIK'])
		if self._partType == 'torso':#Maybe move to a dict?
		    self.l_controlsToMakeArg.append('hips')
		    
	log.debug("l_controlsToMakeArg: %s"%self.l_controlsToMakeArg)
	    
	#self.d_controlShapes = mControlFactory.limbControlMaker(self.m,self.l_controlsToMakeArg)
	
	for key in self.l_controlsToMakeArg:
	    self.d_controlBuildFunctions[key]()#Run it
	    if key not in self.d_returnControls:
		log.warning("Necessary control shape(s) was not built: '%s'"%key)
		raise StandardError,"Did not get all necessary controls built"
	if storageInstance:
	    try:
		storageInstance._d_controlShapes = self.d_returnControls
		storageInstance._md_controlShapes = self.md_ReturnControls
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
	    orientRoot = self.i_templateNull.orientRootHelper.mNode
	    i_loc = cgmMeta.cgmNode(orientRoot).doLoc()#make loc for sizing
	    i_loc.doGroup()#group to zero
	    sizeReturn = returnBaseControlSize(i_loc,self._targetMesh,axis=['x','y'])#Get size
	    l_size = [sizeReturn['x']+(self._skinOffset*2),sizeReturn['y']+(self._skinOffset*2)]
	    mc.delete(i_loc.parent)#delete loc
	    
	    i_crv = cgmMeta.cgmObject( curves.createControlCurve('circleArrow',direction = 'y+',size = max(l_size),absoluteSize=False))
	    Snap.go(i_crv, orientRoot) #Snap it
	    
	    #>>Copy tags and name
	    i_crv.addAttr('cgmName',attrType='string',value = 'cog')        
	    i_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
	    i_crv.doName()        
    
	    #>>> Color
	    curves.setCurveColorByName(i_crv.mNode,self.l_moduleColors[0])    
	    self.d_returnControls['cog'] = i_crv.mNode
	    self.md_ReturnControls['cog'] = i_crv
	except StandardError,error:
		log.error("build_cog fail! | %s"%error) 
		return False
	
    def build_hips(self):
	try:
	    distanceMult = .5	    
	    orientHelper = self.l_controlSnapObjects[0]
	    log.debug(orientHelper)
	    i_loc = cgmMeta.cgmNode(orientHelper).doLoc()#make loc for sizing
	    i_loc.doGroup()#group to zero
	    d_size = returnBaseControlSize(i_loc,self._targetMesh,axis=['x','y','z-'])#Get size
	    l_size = [d_size['x']+(self._skinOffset*2),d_size['y']+(self._skinOffset*2),d_size['z']+(self._skinOffset*2)]
	    
	    i_crv = cgmMeta.cgmObject( curves.createControlCurve('semiSphere',direction = 'y-',size = 1))
	    i_crv.doGroup()
	    mc.scale(l_size[0],l_size[2],l_size[1],i_crv.mNode,os = True, relative = True)
	    i_crv.sy = d_size['z'] * 1.25
	    
	    if len(self.l_controlSnapObjects)>2:#offset
		distanceToMove = distance.returnDistanceBetweenObjects(orientHelper,self.l_controlSnapObjects[1])
		i_loc.tz = -(distanceToMove*distanceMult)#Offset it	
	    
	    mc.makeIdentity(i_crv.mNode,apply=True, scale=True)
	    Snap.go(i_crv, i_loc.mNode)#Snap it	    
	    mc.delete(i_loc.parent)#delete loc
	    
	    pBuffer = i_crv.parent
	    i_crv.parent = False
	    mc.delete(pBuffer)
	    
	    #>>Copy tags and name
	    i_crv.addAttr('cgmName',attrType='string',value = 'hips')        
	    i_crv.addAttr('cgmType',attrType='string',value = 'controlAnim')
	    i_crv.doName()        
	    
	    #>>> Color
	    curves.setCurveColorByName(i_crv.mNode,self.l_moduleColors[0])    
	    self.d_returnControls['hips'] = i_crv.mNode
	    self.md_ReturnControls['hips'] = i_crv
	    	    
	except StandardError,error:
		log.error("build_hips fail! | %s"%error) 
		return False
    	    
    @r9General.Timer    
    def build_segmentFKHandles(self):
	try:
	    l_segmentControls = []
	    l_iSegmentControls = []
	    for i,seg in enumerate(self.l_segments):
		returnBuffer = createWrapControlShape(seg,self._targetMesh,
		                                      points = 8,
		                                      curveDegree=1,
		                                      insetMult = .3,
		                                      posOffset = [0,0,self._skinOffset],
		                                      joinMode=True,
		                                      extendMode='segment')
		i_crv = returnBuffer['instance']	    
		#>>> Color
		curves.setCurveColorByName(i_crv.mNode,self.l_moduleColors[0])                    
		i_crv.addAttr('cgmTypeModifier',attrType='string',value = 'segFK')	
		i_crv.doName()
		
		#Store for return
		l_segmentControls.append( i_crv.mNode )
		l_iSegmentControls.append( i_crv )
		
	    self.d_returnControls['segmentFK'] = l_segmentControls 
	    self.md_ReturnControls['segmentFK'] = l_iSegmentControls
	    
	except StandardError,error:
		log.error("build_segmentIKHandles fail! | %s"%error) 
		return False
	    
    @r9General.Timer	
    def build_segmentIKHandles(self):
	try:
	    l_segmentControls = []
	    l_iSegmentControls = []	    
	    for i,seg in enumerate(self.l_segments):
		returnBuffer = createWrapControlShape(seg,self._targetMesh,
		                                      points = 8,
		                                      curveDegree=3,
		                                      insetMult = .2,
		                                      posOffset = [0,0,self._skinOffset*1.5],
		                                      joinMode=True,
		                                      extendMode='radial')
		i_crv = returnBuffer['instance']	    
		#>>> Color
		curves.setCurveColorByName(i_crv.mNode,self.l_moduleColors[1])                    
		i_crv.addAttr('cgmTypeModifier',attrType='string',value = 'segIK')	
		i_crv.doName()
		
		#Store for return
		l_segmentControls.append( i_crv.mNode )
		l_iSegmentControls.append( i_crv )
		
	    self.d_returnControls['segmentIK'] = l_segmentControls 
	    self.md_ReturnControls['segmentIK'] = l_iSegmentControls
	    
	    if len(self.l_segments)>2:
		objects = self.l_controlSnapObjects[-2:]
	    else:
		objects = self.l_segments[-1]
	    returnBuffer = createWrapControlShape(self.l_segments[-1],self._targetMesh,
	                                          points = 8,
	                                          curveDegree=3,
	                                          posOffset = [0,0,self._skinOffset],
	                                          joinMode=True,
	                                          extendMode='segment')
	    i_crv = returnBuffer['instance']	    
	    #>>> Color
	    curves.setCurveColorByName(i_crv.mNode,self.l_moduleColors[0])                    
	    i_crv.doCopyNameTagsFromObject(self.l_controlSnapObjects[-1],ignore = ['cgmType'])
	    i_crv.addAttr('cgmTypeModifier',attrType='string',value = 'ik')	    
	    i_crv.doName()
		
	    self.d_returnControls['segmentIKEnd'] = i_crv.mNode 		
	    self.md_ReturnControls['segmentIKEnd'] = i_crv
		
	except StandardError,error:
		log.error("build_segmentIKHandles! | %s"%error) 
		return False
	    
@r9General.Timer
def registerControl(controlObject,typeModifier = None,copyTransform = None,copyPivot = None,
                    setRotateOrder = None, autoLockNHide = True,
                    addDynParentGroup = False, addExtraGroups = False, addConstraintGroup = False, freezeAll = False,
                    addSpacePivots = False, controlType = None, aim = None, up = None, out = None, makeAimable = False):
    """
    Function to register a control and get it ready for the rig
    toDo: rotate order set?
    
    """
    assert type(addExtraGroups) in [int,bool]
    assert type(addSpacePivots) in [int,bool]
    
    l_fullFreezeTypes = ['cog']
    d_rotateOrderDefaults = {'cog':3,#xzy
                             'master':3,
                             'hips':0,#xyz
                             'shoulders':2#zyx,
                             }
    i_obj = cgmMeta.validateObjArg(controlObject,cgmMeta.cgmObject,noneValid=False)
    i_obj.addAttr('mClass','cgmControl',lock=True)
    i_control = cgmMeta.cgmControl(i_obj.mNode,setClass=True)
    log.info(i_control)
    
    ml_groups = []#Holder for groups
    ml_constraintGroups = []
    
    #>>>Copy Transform
    #====================================================    
    if copyTransform is not None:
	if issubclass(type(copyTransform),cgmMeta.cgmNode):
	    i_target = copyTransform
	elif mc.objExists(copyTransform):
	    i_target = cgmMeta.cgmObject(copyTransform)
	else:
	    raise StandardError,"Failed to find suitable copyTransform object: '%s"%copyTransform
	
	#Need to move this to default cgmNode stuff
	mBuffer = i_control
	i_newTransform = cgmMeta.cgmObject( rigging.groupMeObject(i_target.mNode,False) )
	for a in mc.listAttr(i_control.mNode, userDefined = True):
	    attributes.doCopyAttr(i_control.mNode,a,i_newTransform.mNode)
	#i_newTransform.doCopyNameTagsFromObject(i_control.mNode)
	curves.parentShapeInPlace(i_newTransform.mNode,i_control.mNode)#Parent shape
	i_newTransform.parent = i_control.parent#Copy parent
	i_control = cgmMeta.cgmControl(i_newTransform.mNode,setClass=True)
	mc.delete(mBuffer.mNode)
	
    #>>>Copy Pivot
    #====================================================    
    if copyPivot is not None:
	if issubclass(type(copyPivot),cgmMeta.cgmNode):
	    i_target = copyPivot
	elif mc.objExists(copyPivot):
	    i_target = cgmMeta.cgmObject(copyPivot)
	else:
	    raise StandardError,"Failed to find suitable copyTransform object: '%s"%copyPivot
	
	#Need to move this to default cgmNode stuff
	i_control.doCopyPivot(i_target.mNode)

    #>>>Name stuff
    #====================================================
    i_control.addAttr('cgmType','controlAnim',lock=True)    
    if typeModifier is not None:
	i_control.addAttr('cgmTypeModifier',str(typeModifier),lock=True)
    i_control.doName(nameShapes=True)
    str_shortName = i_control.getShortName()
    	
    #>>>Add aiming info
    #====================================================
    if aim is not None or up is not None or makeAimable:
	i_control._verifyAimable()
	    
    #>>>Rotate Order
    #====================================================   
    if setRotateOrder is not None:
	i_control.rotateOrder = setRotateOrder
    elif controlType in d_rotateOrderDefaults.keys():
	i_control.rotateOrder = d_rotateOrderDefaults[controlType]
    elif i_control.getAttr('cgmName') in d_rotateOrderDefaults.keys():
	i_control.rotateOrder = d_rotateOrderDefaults[i_control.getAttr('cgmName')]
    else:
	log.info("Need to set rotateOrder: '%s'"%str_shortName)
	
	
    #>>>Freeze stuff 
    #====================================================  
    if freezeAll:
	mc.makeIdentity(i_control.mNode, apply=True,t=1,r=1,s=1,n=0)		
	
    if addDynParentGroup or addSpacePivots or i_control.cgmName.lower() == 'cog':
	i_control.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)
	
    #==================================================== 
    """ All controls have a master group to zero them """
    try:#>>>Grouping

	#First our master group:
	i_masterGroup = (cgmMeta.cgmObject(i_control.doGroup(True),setClass=True))
	i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
	i_masterGroup.doName()
	i_control.connectChildNode(i_masterGroup,'masterGroup','groupChild')
	log.info("masterGroup: '%s'"%i_masterGroup.getShortName())
	
	if addDynParentGroup:
	    i_dynGroup = (cgmMeta.cgmObject(i_control.doGroup(True)))
	    i_dynGroup = cgmMeta.cgmDynParentGroup(dynChild=i_control,dynGroup=i_dynGroup)
	    i_dynGroup.doName()
	    log.info("dynParentGroup: '%s'"%i_dynGroup.getShortName())
	    
	    i_zeroGroup = (cgmMeta.cgmObject(i_control.doGroup(True)))
	    i_zeroGroup.addAttr('cgmTypeModifier','zero',lock=True)
	    i_zeroGroup.doName()
	    i_control.connectChildNode(i_masterGroup,'zeroGroup','groupChild')
	    log.info("zeroGroup: '%s'"%i_zeroGroup.getShortName())	    
	
	if addExtraGroups:
	    for i in range(addExtraGroups):
		i_group = (cgmMeta.cgmObject(i_control.doGroup(True),setClass=True))
		if type(addExtraGroups)==int and addExtraGroups>1:#Add iterator if necessary
		    i_group.addAttr('cgmIterator',str(i+1),lock=True)
		    i_group.doName()
		ml_groups.append(i_group)
		log.info("group %s: '%s'"%(i,i_group.getShortName()))
	    
	if addConstraintGroup:#ConstraintGroups
	    i_constraintGroup = (cgmMeta.cgmObject(i_control.doGroup(True),setClass=True))
	    i_constraintGroup.addAttr('cgmTypeModifier','constraint',lock=True)
	    i_constraintGroup.doName()
	    ml_constraintGroups.append(i_constraintGroup)
	    i_control.connectChildNode(i_constraintGroup,'constraintGroup','groupChild')	    
	    log.info("constraintGroup: '%s'"%i_constraintGroup.getShortName())	
	    
    except StandardError,error:
	log.error("ModuleControlFactory.registerControl>>grouping fail")
	raise StandardError,error
    
    #====================================================  
    #try:#>>>Space Pivots
    if addSpacePivots:
	ml_spaceLocators = []
	parent = i_control.getMessage('masterGroup')[0]
	for i in range(addSpacePivots):
	    i_pivot = rUtils.create_spaceLocatorForObject(i_control,parent)
	    ml_spaceLocators.append(i_pivot)
   
    
    #====================================================  
    try:#>>>Freeze stuff 
	if not freezeAll:
	    if i_control.getAttr('cgmName') == 'cog' or controlType in l_fullFreezeTypes:
		mc.makeIdentity(i_control.mNode, apply=True,t=1,r=1,s=1,n=0)	
	    else:
		mc.makeIdentity(i_control.mNode, apply=True,t=1,r=0,s=1,n=0)
	else:
	    mc.makeIdentity(i_control.mNode, apply=True,t=1,r=1,s=1,n=0)	
	    
    except StandardError,error:
	log.error("ModuleControlFactory.registerControl>>freeze fail")
	raise StandardError,error
	    
    #>>>Lock and hide
    #====================================================  
    if autoLockNHide:
	if i_control.hasAttr('cgmTypeModifier'):
	    if i_control.cgmTypeModifier.lower() == 'fk':
		attributes.doSetLockHideKeyableAttr(i_control.mNode,channels=['tx','ty','tz','sx','sy','sz'])
	if i_control.cgmName.lower() == 'cog':
	    attributes.doSetLockHideKeyableAttr(i_control.mNode,channels=['sx','sy','sz'])
	cgmMeta.cgmAttr(i_control,'visibility',lock=True,hidden=True)   
    return {'instance':i_control,'mi_groups':ml_groups,'mi_constraintGroups':ml_constraintGroups}

    
