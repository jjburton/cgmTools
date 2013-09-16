"""
Module for building controls for cgmModules

"""
# From Python =============================================================
import copy
import re
import time
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.cgmPy import validateArgs as cgmValid
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

from cgm.core.lib import nameTools
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
'''
class go(object):
    #@r9General.Timer
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
	except Exception,error:
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
	    except Exception,error:
		log.error("storage fail! | %s"%storageInstance) 
		raise StandardError,"Did not get all necessary controls built"

    def validateControlArg(self,arg):
	"""returns function"""
	if arg in self.d_controlBuildFunctions.keys():
	    return True
	log.warning("validateControlArg couldn't find: %s"%arg)
	return False
    
    #@r9General.Timer    
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
	except Exception,error:
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
	    	    
	except Exception,error:
		log.error("build_hips fail! | %s"%error) 
		return False
    	    
    #@r9General.Timer    
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
	    
	except Exception,error:
		log.error("build_segmentIKHandles fail! | %s"%error) 
		return False
	    
    #@r9General.Timer	
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
		
	except Exception,error:
		log.error("build_segmentIKHandles! | %s"%error) 
		return False
'''	    
#@cgmGeneral.TimerDebug
def registerControl(controlObject,typeModifier = None,copyTransform = None,copyPivot = None,shapeParentTo = None,
                    setRotateOrder = None, autoLockNHide = True, mirrorAxis = None, mirrorSide = None, makeMirrorable = True,
                    addDynParentGroup = False, addExtraGroups = False, addConstraintGroup = False, freezeAll = False,
                    addSpacePivots = False, controlType = None, aim = None, up = None, out = None, makeAimable = False):
    """
    Function to register a control and get it ready for the rig
    toDo: rotate order set?
    
    """
    start = time.clock()    
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
    log.debug(i_control)
    
    _str_funcName = "registerControl(%s)"%i_obj.p_nameShort  
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)  
    
    ml_groups = []#Holder for groups
    ml_constraintGroups = []
    
    str_mirrorAxis = cgmValid.stringArg(mirrorAxis,calledFrom =_str_funcName)
    str_mirrorSide = cgmValid.stringArg(mirrorSide,calledFrom =_str_funcName)
    b_makeMirrorable = cgmValid.boolArg(makeMirrorable,calledFrom =_str_funcName)
    
    
    try:#>>>Copy Transform ====================================================
	_str_subFunc = "Copy Transform"
	time_sub = time.clock()  
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
	log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#>>>Shape Parent #====================================================
	_str_subFunc = "Shape Parent "
	time_sub = time.clock()  	
	if shapeParentTo:
	    i_target = cgmMeta.validateObjArg(shapeParentTo,cgmMeta.cgmObject)
	    curves.parentShapeInPlace(i_target.mNode,i_control.mNode)
	    i_target.addAttr('mClass','cgmControl',lock=True)
	    i_target = cgmMeta.cgmControl(i_target.mNode)
	    #i_control.delete()
	    i_control = i_target#replace the control with the joint    
	    log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
      
    try:#>>>Copy Pivot #====================================================
	_str_subFunc = "Copy Pivot"
	time_sub = time.clock()  	
	if copyPivot is not None:
	    if issubclass(type(copyPivot),cgmMeta.cgmNode):
		i_target = copyPivot
	    elif mc.objExists(copyPivot):
		i_target = cgmMeta.cgmObject(copyPivot)
	    else:
		raise StandardError,"Failed to find suitable copyTransform object: '%s"%copyPivot
	    
	    #Need to move this to default cgmNode stuff
	    i_control.doCopyPivot(i_target.mNode)
	    log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#>>>Name stuff #====================================================
	_str_subFunc = "Naming"
	time_sub = time.clock()  	
	log.debug(">>> %s..."%_str_subFunc)                		
	i_control.addAttr('cgmType','controlAnim',lock=True)    
	if typeModifier is not None:
	    i_control.addAttr('cgmTypeModifier',str(typeModifier),lock=True)
	i_control.doName()#i_control.doName(nameShapes=True)
	str_shortName = i_control.getShortName()
	log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#>>>Add aiming info #====================================================
	_str_subFunc = "Aiming"
	time_sub = time.clock()  	
	log.debug(">>> %s..."%_str_subFunc)               			
	if aim is not None or up is not None or makeAimable:
	    i_control._verifyAimable()
	    log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#>>>Add mirror info #====================================================
	_str_subFunc = "Mirror"
	time_sub = time.clock()  	
	log.debug(">>> %s..."%_str_subFunc)          			
	if str_mirrorSide is not None or b_makeMirrorable:
	    log.debug("%s >> %s >> str_mirrorSide : %s"%(_str_funcName,_str_subFunc,str_mirrorSide))
	    log.debug("%s >> %s >> str_mirrorAxis : %s"%(_str_funcName,_str_subFunc,str_mirrorAxis))
	    log.debug("%s >> %s >> b_makeMirrorable : %s"%(_str_funcName,_str_subFunc,b_makeMirrorable))
	    try:i_control._verifyMirrorable()
	    except Exception,error:raise StandardError,"_verifyMirror | %s"%(error)
	    l_enum = cgmMeta.cgmAttr(i_control,'mirrorSide').p_enum
	    if str_mirrorSide in l_enum:
		log.debug("%s >> %s >> found in : %s"%(_str_funcName,_str_subFunc,l_enum))		
		try:
		    i_control.mirrorSide = l_enum.index(str_mirrorSide)
		    log.debug("%s >> %s >> mirrorSide set to: %s"%(_str_funcName,_str_subFunc,i_control.mirrorSide ))						    
		except Exception,error:raise StandardError,"str_mirrorSide : %s | %s"%(str_mirrorSide,error)
	    if str_mirrorAxis:
		try:
		    i_control.mirrorAxis = str_mirrorAxis
		    log.debug("%s >> %s >> str_mirrorAxis set: %s"%(_str_funcName,_str_subFunc,str_mirrorAxis))				    
		except Exception,error:raise StandardError,"str_mirrorAxis : %s | %s"%(str_mirrorAxis,error)
		
	    log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#>>>Rotate Order #====================================================
	_str_subFunc = "Rotate Order"
	time_sub = time.clock()  	
	log.debug(">>> %s..."%_str_subFunc)            	
	_rotateOrder = False
	if setRotateOrder is not None:
	    _rotateOrder = setRotateOrder
	elif controlType in d_rotateOrderDefaults.keys():
	    _rotateOrder = d_rotateOrderDefaults[controlType]
	elif i_control.getAttr('cgmName') in d_rotateOrderDefaults.keys():
	    _rotateOrder = d_rotateOrderDefaults[i_control.getAttr('cgmName')]
	else:
	    log.debug("rotateOrder not set on: '%s'"%str_shortName)
	    
	#set it
	if _rotateOrder:
	    _rotateOrder = dictionary.validateRotateOrderString(_rotateOrder)
	    mc.xform(i_control.mNode, rotateOrder = _rotateOrder)
	log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    #>>>Freeze stuff 
    #====================================================  
    try:
	_str_subFunc = "Freezing"
	time_sub = time.clock()  	
	log.debug(">>> %s..."%_str_subFunc)              	
	if freezeAll:
	    mc.makeIdentity(i_control.mNode, apply=True,t=1,r=1,s=1,n=0)
	log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:
	if addDynParentGroup or addSpacePivots or i_control.cgmName.lower() == 'cog':
	    i_control.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)
    except Exception,error:
	raise StandardError,"%s >> spacer | %s"%(_str_funcName,error)       
	
    #==================================================== 
    """ All controls have a master group to zero them """
    _str_subFunc = "Grouping"
    time_sub = time.clock()  	
    log.debug(">>> %s..."%_str_subFunc)            
    try:#>>>Grouping
	if not shapeParentTo:
	    #First our master group:
	    i_masterGroup = (cgmMeta.cgmObject(i_control.doGroup(True),setClass=True))
	    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
	    i_masterGroup.doName()
	    i_control.connectChildNode(i_masterGroup,'masterGroup','groupChild')
	    log.debug("masterGroup: '%s'"%i_masterGroup.getShortName())
	    
	    if addDynParentGroup:
		log.debug("addDynParentGroup...")
		i_dynGroup = (cgmMeta.cgmObject(i_control.doGroup(True)))
		i_dynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=i_control,dynGroup=i_dynGroup)
		i_dynGroup.doName()
		log.debug("dynParentGroup: '%s'"%i_dynGroup.getShortName())
		
		i_zeroGroup = (cgmMeta.cgmObject(i_control.doGroup(True)))
		i_zeroGroup.addAttr('cgmTypeModifier','zero',lock=True)
		i_zeroGroup.doName()
		i_control.connectChildNode(i_zeroGroup,'zeroGroup','groupChild')
		log.debug("zeroGroup: '%s'"%i_zeroGroup.getShortName())	    
	    
	    if addExtraGroups:
		log.debug("addExtraGroups...")	    
		for i in range(addExtraGroups):
		    i_group = (cgmMeta.cgmObject(i_control.doGroup(True),setClass=True))
		    if type(addExtraGroups)==int and addExtraGroups>1:#Add iterator if necessary
			i_group.addAttr('cgmIterator',str(i+1),lock=True)
			i_group.doName()
		    ml_groups.append(i_group)
		    log.debug("group %s: '%s'"%(i,i_group.getShortName()))
		i_control.msgList_connect(ml_groups,"extraGroups",'groupChild')
		
	    if addConstraintGroup:#ConstraintGroups
		log.debug("addConstraintGroup...")	    
		i_constraintGroup = (cgmMeta.cgmObject(i_control.doGroup(True),setClass=True))
		i_constraintGroup.addAttr('cgmTypeModifier','constraint',lock=True)
		i_constraintGroup.doName()
		ml_constraintGroups.append(i_constraintGroup)
		i_control.connectChildNode(i_constraintGroup,'constraintGroup','groupChild')	    
		log.debug("constraintGroup: '%s'"%i_constraintGroup.getShortName())	
		
	log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)    
    
    #try:#>>>Space Pivots #====================================================  
    _str_subFunc = "Space Pivots"
    time_sub = time.clock()  	
    log.debug(">>> %s..."%_str_subFunc)   
    try:
	if addSpacePivots:
	    ml_spaceLocators = []
	    parent = i_control.getMessage('masterGroup')[0]
	    for i in range(int(addSpacePivots)):
		try:
		    log.info("%s >> %s | obj: %s | parent: %s"%(_str_funcName,i,i_control.p_nameShort,parent))
		    i_pivot = rUtils.create_spaceLocatorForObject(i_control.mNode,parent)
		    ml_spaceLocators.append(i_pivot)
		except Exception,error:
		    raise StandardError,"space pivot %s | %s"%(i,error)
	    log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)   
    
    try:#>>>Freeze stuff  #====================================================
	_str_subFunc = "Freezing"
	time_sub = time.clock()  	
	log.debug(">>> %s..."%_str_subFunc)   
	if not shapeParentTo:
	    if not freezeAll:
		if i_control.getAttr('cgmName') == 'cog' or controlType in l_fullFreezeTypes:
		    mc.makeIdentity(i_control.mNode, apply=True,t=1,r=1,s=1,n=0)	
		else:
		    mc.makeIdentity(i_control.mNode, apply=True,t=1,r=0,s=1,n=0)
	    else:
		mc.makeIdentity(i_control.mNode, apply=True,t=1,r=1,s=1,n=0)	
	    
	log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)  
    
    try:#>>>Lock and hide #====================================================
	_str_subFunc = "lockNHide"
	time_sub = time.clock()  	
	log.debug(">>> %s..."%_str_subFunc)   	
	if autoLockNHide:
	    if i_control.hasAttr('cgmTypeModifier'):
		if i_control.cgmTypeModifier.lower() == 'fk':
		    attributes.doSetLockHideKeyableAttr(i_control.mNode,channels=['tx','ty','tz','sx','sy','sz'])
	    if i_control.cgmName.lower() == 'cog':
		attributes.doSetLockHideKeyableAttr(i_control.mNode,channels=['sx','sy','sz'])
	    cgmMeta.cgmAttr(i_control,'visibility',lock=True,hidden=True)   
	log.info("%s >>> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)  
    
    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)             
    return {'instance':i_control,'ml_groups':ml_groups,'ml_constraintGroups':ml_constraintGroups}

    
