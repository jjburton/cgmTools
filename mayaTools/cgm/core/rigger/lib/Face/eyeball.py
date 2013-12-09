"""
------------------------------------------
cgm.core.rigger: Face.eyeball
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

eyeball rig builder
================================================================
"""
__version__ = 0.08312013

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

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.rigger.lib import module_Utils as modUtils
from cgm.core.lib import meta_Utils as metaUtils

from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools

from cgm.core.rigger.lib import rig_Utils as rUtils

from cgm.lib import (attributes,
                     joints,
                     skinning,
                     lists,
                     dictionary,
                     distance,
                     modules,
                     search,
                     curves,
                     )

#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['rigJoints']   
def __bindSkeletonSetup__(self):
    """
    TODO: Do I need to connect per joint overrides or will the final group setup get them?
    """
    log.info(">>> %s.__bindSkeletonSetup__ >> "%self._strShortName + "-"*75)            
    try:
	if not self._cgmClass == 'JointFactory.go':
	    log.error("Not a JointFactory.go instance: '%s'"%self)
	    raise StandardError
	
    except StandardError,error:
	log.error("eyeball.__bindSkeletonSetup__>>bad self!")
	raise StandardError,error
    
    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self.rig_getSkinJoints() or []
    if not self._i_module.isSkeletonized():
	raise StandardError, "%s is not skeletonized yet."%self._strShortName
    try:
	self._i_module.rig_getReport()#report	
    except StandardError,error:
	log.error("build_eyeball>>__bindSkeletonSetup__ fail!")
	raise StandardError,error   
    
def build_rigSkeleton(*args, **kws):
    class fncWrap(modUtils.rigStep):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'build_rigSkeleton(%s)'%self.d_kws['goInstance']._strShortName	
	    self._b_autoProgressBar = True
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self.gatherInfo},
	                        {'step':'Rig Joints','call':self.build_rigJoints},
	                        {'step':'Connections','call':self.build_connections}
	                        ]	
	    #=================================================================
	
	def gatherInfo(self):
	    mi_go = self._go#Rig Go instance link
	    self.mi_skullPlate = mi_go._mi_skullPlate
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._i_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    		    
	def build_rigJoints(self):
	    #We'll have a rig joint for every joint
	    mi_go = self._go#Rig Go instance link
	    ml_rigJoints = mi_go.build_rigChain()	
	    ml_rigJoints[0].parent = False
	    self.ml_rigJoints = ml_rigJoints
	    
	def build_connections(self):    
	    #ml_jointsToConnect = []
	    #ml_jointsToConnect.extend(self.ml_rigJoints)   
	    mi_go = self._go#Rig Go instance link	    
	    mi_go.connect_toRigGutsVis(self.ml_rigJoints)
    return fncWrap(*args, **kws).go()    
    
def build_rigSkeleton2(self):
    """
    """
    try:#===================================================
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("%s.build_rigSkeleton>>bad self!"%self._strShortName)
	raise StandardError,error
    _str_funcName = "build_rigSkeleton(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)
    
    
    #>>>Create joint chains
    try:#>>Rig chain =====================================================================
	ml_rigJoints = self.build_rigChain()	
	ml_rigJoints[0].parent = False
    except StandardError,error:
	raise StandardError,"%s>>Build rig joints fail! | error: %s"%(_str_funcName,error)   

    try:#>>> Store em all to our instance
	#=====================================================================	
	ml_jointsToConnect = []
	ml_jointsToConnect.extend(ml_rigJoints)    
	for i_jnt in ml_jointsToConnect:
	    i_jnt.overrideEnabled = 1		
	    cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
	    cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    
	    
    except StandardError,error:
	raise StandardError,"%s>> Store joints fail! | error: %s"%(_str_funcName,error)   
    return True
	
#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['eyeballFK','eyeballIK','settings']}

def build_shapes(self):
    """
    """ 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("eyeball.build_rig>>bad self!")
	raise StandardError,error
    
    _str_funcName = "build_shapes(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)   
    
    if self._i_templateNull.handles > 3:
	raise StandardError, "%s >>> Too many handles. don't know how to rig"%(_str_funcName)    
    
    if not self.isRigSkeletonized():
	raise StandardError, "%s.build_shapes>>> Must be rig skeletonized to shape"%(self._strShortName)	
    
    #>>>Build our Shapes
    #=============================================================
    try:
	#Rest of it
	#l_toBuild = ['eyeballIK','eyeballFK','eyeballSettings']
	mShapeCast.go(self._i_module,['eyeball'], storageInstance=self)#This will store controls to a dict called    
	#self._i_rigNull.connectChildNode(self._md_controlShapes['eyeball'],'shape_eyeball',"rigNull")
	
    except StandardError,error:
	log.error("build_eyeball>>Build shapes fail!")
	raise StandardError,error 
    return True
    
#>>> Controls
#===================================================================
def build_controls(*args, **kws):
    class fncWrap(modUtils.rigStep):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'build_controls(%s)'%self.d_kws['goInstance']._strShortName
	    self._b_autoProgressBar = True	
	    self._b_reportTimes = True	    	    
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	                        {'step':'Build Groups','call':self._buildGroups_},
	                        {'step':'Build Controls','call':self._buildControls_},	                        
	                        #{'step':'Settings','call':self._buildSettings_},	                        
	                        #{'step':'Direct Controls','call':self._buildControls_},
	                        #{'step':'Build Connections','call':self._buildConnections_}	                        
	                        ]	
	    #=================================================================
	
	def _gatherInfo_(self):
	    mi_go = self._go#Rig Go instance link
	    self.md_rigList = {}
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._i_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    
	    if not mi_go.isShaped():
		raise StandardError,"Needs shapes to build controls"
	    if not mi_go.isRigSkeletonized():
		raise StandardError,"Needs shapes to build controls"
	
	    self.md_rigList['fk_shape'] = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_eyeballFK'),cgmMeta.cgmObject) 
	    self.md_rigList['ik_shape'] = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_eyeballIK'),cgmMeta.cgmObject) 
	    self.md_rigList['settings_shape'] = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_settings'),cgmMeta.cgmObject)
	    self.md_rigList['eyeMove_shape'] = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_eyeMove'),cgmMeta.cgmObject)     
	    
	    self.ml_rigJoints = cgmMeta.validateObjListArg(mi_go._i_rigNull.msgList_getMessage('rigJoints'),cgmMeta.cgmObject)
	    
	    #>> Find our joint lists ===================================================================
	    self.md_jointLists = {}	    
	    self.ml_handleJoints = mi_go._i_module.rigNull.msgList_get('handleJoints')
	    self.ml_rigJoints = mi_go._i_module.rigNull.msgList_get('rigJoints')
	    
	    self.md_rigList['eyeOrb'] = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
	                                                                      cgmName = 'eyeOrb')[0]    
	    self.md_rigList['pupil'] = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
	                                                                     cgmName = 'pupil')[0]	 
	    self.md_rigList['iris'] = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
	                                                                    cgmName = 'iris')[0]
	    self.md_rigList['eye'] = metaUtils.get_matchedListFromAttrDict(self.ml_rigJoints,
	                                                                   cgmName = 'eye')[0]	    
	    #>> Running lists ===========================================================================
	    self.ml_directControls = []
	    self.ml_controlsAll = []
	    
	
	def _buildGroups_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    for grp in ['controlsFKNull','controlsIKNull']:
		i_dup = mi_go._i_constrainNull.doDuplicateTransform(True)
		i_dup.parent = mi_go._i_constrainNull.mNode
		i_dup.addAttr('cgmTypeModifier',grp,lock=True)
		i_dup.doName()
		mi_go._i_constrainNull.connectChildNode(i_dup,grp,'owner')
		self.md_rigList[grp] = i_dup
		
	def _buildPupil_(self):
	    mi_go = self._go#Rig Go instance link
	    if not self.mi_helper.buildPupil:
		log.info("%s >>> Build pupil toggle: off"%(self._str_reportStart))
		return True	
	    
	def _buildControls_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    try:#Query ====================================================================================
		ml_rigJoints = self.ml_rigJoints
		ml_handleJoints = self.ml_handleJoints
		
		mi_fkShape = self.md_rigList['fk_shape']
		mi_ikShape = self.md_rigList['ik_shape']
		mi_settingsShape = self.md_rigList['settings_shape']
		mi_eyeMove = self.md_rigList['eyeMove_shape']

	    except Exception,error:raise Exception,"!Query! | %s"%error	
	    self.log_infoNestedDict('md_rigList')
	    
	    try:#>>>> FK #==================================================================	
		mi_fkShape.parent = mi_go._i_constrainNull.controlsFKNull.mNode
		i_obj = mi_fkShape
		d_buffer = mControlFactory.registerControl(i_obj,copyTransform = ml_rigJoints[0],
			                                   makeAimable=True,setRotateOrder ='zxy',typeModifier='fk',) 	    
		mi_controlFK = d_buffer['instance']
		mi_controlFK.axisAim = "%s+"%mi_go._jointOrientation[0]
		mi_controlFK.axisUp= "%s+"%mi_go._jointOrientation[1]	
		mi_controlFK.axisOut= "%s+"%mi_go._jointOrientation[2]
		
		#We're gonna lock the aim rot
		cgmMeta.cgmAttr(mi_controlFK,'r%s'%mi_go._jointOrientation[0], keyable = False, lock=True,hidden=True)
		mi_go._i_rigNull.connectChildNode(mi_controlFK,'controlFK',"rigNull")
		self.ml_controlsAll.append(mi_controlFK)	
	    
	    except Exception,error:raise Exception,"!Build fk fail! | %s"%(error)
	    
	    try:#>>>> IK 
		#==================================================================	
		mi_ikShape.parent = mi_go._i_constrainNull.controlsIKNull.mNode	
		d_buffer = mControlFactory.registerControl(mi_ikShape,typeModifier='ik',addDynParentGroup=True) 	    
		mi_ikControl = d_buffer['instance']	
		
		mi_go._i_rigNull.connectChildNode(mi_ikControl,'controlIK',"rigNull")
		self.ml_controlsAll.append(mi_ikControl)	
	    
	    except Exception,error:raise Exception,"!Build ik fail! | %s"%(error)

	   
	    try:#>>>> Settings
		#==================================================================	
		mi_settingsShape.parent = mi_go._i_constrainNull.mNode
		
		try:#Register the control
		    d_buffer = mControlFactory.registerControl(mi_settingsShape,makeAimable=True,typeModifier='settings') 
		    mi_settings = d_buffer['instance']
		    mi_go._i_rigNull.connectChildNode(mi_settings,'settings','rigNull')
		    self.ml_controlsAll.append(mi_settings)
		except StandardError,error:raise StandardError,"registration | %s"%error	
		
		try:#Set up some attributes
		    attributes.doSetLockHideKeyableAttr(mi_settings.mNode)
		    mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',attrType='float',lock=False,keyable=True,
			                         minValue=0,maxValue=1.0)
		except StandardError,error:raise StandardError,"attribute setup | %s"%error	
		
	    except Exception,error:raise Exception,"!Build Settings fail! | %s"%(error)
  	    
	    '''
	    l_strTypeModifiers = ['direct',None]
	    for ii,ml_list in enumerate( [ml_rigJoints,ml_handleJoints] ):
		for i,mObj in enumerate(ml_list):
		    str_mirrorSide = False
		    try:
			mObj.parent = mi_go._i_deformNull
			str_mirrorSide = mi_go.verify_mirrorSideArg(mObj.getAttr('cgmDirection'))#Get the mirror side
			str_cgmDirection = mObj.getAttr('cgmDirection')			
			_addForwardBack = "t%s"%mi_go._jointOrientation[0]			
			if str_cgmDirection == 'center' and ii == 0:_addForwardBack = False#other center controls			
			#Register 
			try:
			    d_buffer = mControlFactory.registerControl(mObj, useShape = mObj.getMessage('controlShape'),addForwardBack = _addForwardBack,
				                                       mirrorSide = str_mirrorSide, mirrorAxis="translateZ,rotateX,rotateY",		                                           
				                                       makeAimable=False, typeModifier=l_strTypeModifiers[ii]) 	    
			except Exception,error:
			    log.error("mObj: %s"%mObj.p_nameShort)
			    log.error("useShape: %s"%mObj.getMessage('controlShape'))
			    log.error("mirrorSide: %s"%str_mirrorSide)			
			    raise StandardError,"Register fail : %s"%error
			
			#Vis sub connect
			if ii == 0:
			    self.mPlug_result_moduleFaceSubDriver.doConnectOut("%s.visibility"%mObj.mNode)
			
			#
			mc.delete(mObj.getMessage('controlShape'))
			mObj.doRemove('controlShape')
			self.md_directionControls[str_mirrorSide].append(mObj)
			
			#i_obj.drawStyle = 6#Stick joint draw style
			cgmMeta.cgmAttr(mObj,'radius',value=.01, hidden=True)
			self.ml_directControls.append(mObj)
			
		    except Exception, error:
			raise StandardError,"Iterative fail item: %s | obj: %s | mirror side: %s | error: %s"%(i,mObj.p_nameShort,str_mirrorSide,error)
		 '''   
	    
	def _buildConnections_(self):
	    #Register our mirror indices ---------------------------------------------------------------------------------------
	    mi_go = self._go#Rig Go instance link	    
	    for str_direction in self.md_directionControls.keys():
		int_start = self._go._i_puppet.get_nextMirrorIndex( self._go._str_mirrorDirection )
		for i,mCtrl in enumerate(self.md_directionControls[str_direction]):
		    try:
			mCtrl.addAttr('mirrorIndex', value = (int_start + i))		
		    except Exception,error: raise StandardError,"Failed to register mirror index | mCtrl: %s | %s"%(mCtrl,error)

	    try:self._go._i_rigNull.msgList_connect(self.ml_controlsAll,'controlsAll')
	    except Exception,error: raise StandardError,"Controls all connect| %s"%error	    
	    try:self._go._i_rigNull.moduleSet.extend(self.ml_controlsAll)
	    except Exception,error: raise StandardError,"Failed to set module objectSet | %s"%error
	    
    return fncWrap(*args, **kws).go()

def build_controls2(self):
    """
    """    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("eyeball.build_rig>>bad self!")
	raise StandardError,error
    
    _str_funcName = "build_controls(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)   
    
    if not self.isShaped():
	raise StandardError,"%s >>> needs shapes to build controls"%_str_funcName
    if not self.isRigSkeletonized():
	raise StandardError,"%s >>> needs shapes to build controls"%_str_funcName

    mi_fkShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_eyeballFK'),cgmMeta.cgmObject) 
    mi_ikShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_eyeballIK'),cgmMeta.cgmObject) 
    mi_settingsShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_settings'),cgmMeta.cgmObject)     
    ml_rigJoints = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('rigJoints'),cgmMeta.cgmObject)
    l_controlsAll = []
    
    try:#Group setup
	#>>>Make a few extra groups for storing controls and what not to in the deform group
	for grp in ['controlsFKNull','controlsIKNull']:
	    i_dup = self._i_constrainNull.doDuplicateTransform(True)
	    i_dup.parent = self._i_constrainNull.mNode
	    i_dup.addAttr('cgmTypeModifier',grp,lock=True)
	    i_dup.doName()
	    self._i_constrainNull.connectChildNode(i_dup,grp,'owner')
    except StandardError,error:	
	raise StandardError,"%s >>> Build groups fail! | error: %s"%(_str_funcName,error)
    
    try:#>>>> FK 
	#==================================================================	
	if not mi_fkShape:
	    raise StandardError,"%s >>> Must have at least one fk control"%_str_funcName    
	
	mi_fkShape.parent = self._i_constrainNull.controlsFKNull.mNode
	i_obj = mi_fkShape
	
	d_buffer = mControlFactory.registerControl(i_obj,copyTransform = ml_rigJoints[0],
                                                   makeAimable=True,setRotateOrder ='zxy',typeModifier='fk',) 	    
	mi_controlFK = d_buffer['instance']
	mi_controlFK.axisAim = "%s+"%self._jointOrientation[0]
	mi_controlFK.axisUp= "%s+"%self._jointOrientation[1]	
	mi_controlFK.axisOut= "%s+"%self._jointOrientation[2]
	
	#We're gonna lock the aim rot
	cgmMeta.cgmAttr(mi_controlFK,'r%s'%self._jointOrientation[0], keyable = False, lock=True,hidden=True)
	self._i_rigNull.connectChildNode(mi_controlFK,'controlFK',"rigNull")
	l_controlsAll.append(mi_controlFK)	
    
    except StandardError,error:	
	raise StandardError,"%s >>> Build fk fail! | error: %s"%(_str_funcName,error)
    
    try:#>>>> IK 
	#==================================================================	
	mi_ikShape.parent = self._i_constrainNull.controlsIKNull.mNode	
	d_buffer = mControlFactory.registerControl(mi_ikShape,typeModifier='ik',addDynParentGroup=True) 	    
	mi_ikControl = d_buffer['instance']	
	self._i_rigNull.connectChildNode(mi_ikControl,'controlIK',"rigNull")
	l_controlsAll.append(mi_ikControl)	
    
    except StandardError,error:	
	raise StandardError,"%s >>> Build ik fail! | error: %s"%(_str_funcName,error)    
   
    try:#>>>> Settings
	#==================================================================	
	mi_settingsShape.parent = self._i_constrainNull.mNode
	
	try:#Register the control
	    d_buffer = mControlFactory.registerControl(mi_settingsShape,makeAimable=True,typeModifier='settings') 
	    mi_settings = d_buffer['instance']
	    self._i_rigNull.connectChildNode(mi_settings,'settings','rigNull')
	    l_controlsAll.append(mi_settings)
	except StandardError,error:raise StandardError,"registration | %s"%error	
	
	try:#Set up some attributes
	    attributes.doSetLockHideKeyableAttr(mi_settings.mNode)
	    mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',attrType='float',lock=False,keyable=True,
		                         minValue=0,maxValue=1.0)
	except StandardError,error:raise StandardError,"attribute setup | %s"%error	
	
    except StandardError,error:	
	raise StandardError,"%s >>> Build settings! | error: %s"%(_str_funcName,error)    

    #==================================================================   
    #Connect all controls
    self._i_rigNull.msgList_connect(l_controlsAll,'controlsAll')
    
    return True

def build_rig(self):
    """
    """    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("%s.build_rig>>bad self!"%self._strShortName)
	raise StandardError,error
    
    _str_funcName = "build_rig(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75) 
    
    try:#>>>Get data
	_str_orientation = self._jointOrientation or modules.returnSettingsData('jointOrientation')
	
	try:mi_eyeLook = self._get_eyeLook()
	except StandardError,error:raise StandardError,"eyeLook fail! | %s"%(error)	    
	try:mi_controlIK = self._i_rigNull.controlIK
	except StandardError,error:raise StandardError,"controlIK fail! | %s"%(error)
	try:mi_controlFK = self._i_rigNull.controlFK
	except StandardError,error:raise StandardError,"controlFK fail! | %s"%(error)
	try:ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
	except StandardError,error:raise StandardError,"rigJoints fail! | %s"%(error)
	try:mi_helper = self._i_module.helper
	except StandardError,error:raise StandardError,"helper fail! | %s"%(error)
	try:mi_settings = self._i_rigNull.settings
	except StandardError,error:raise StandardError,"controlIK fail! | %s"%(error)
	log.info("ml_controlsFK: %s"%mi_controlFK.p_nameShort)
	log.info("mi_controlIK: %s"%mi_controlIK.p_nameShort)		
	log.info("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
	log.info("mi_helper: %s"%mi_helper)		
		
	v_aim = cgmValid.simpleAxis("%s+"%self._jointOrientation[0]).p_vector
	v_up = cgmValid.simpleAxis("%s+"%self._jointOrientation[1]).p_vector
	
	#Settings
	mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK')
	
    except StandardError,error:
	raise StandardError,"%s >> Gather data fail! | error: %s"%(_str_funcName,error)
    #Setup eye rig
    #====================================================================================
    try:#Base eye setup
	d_return = rUtils.createEyeballRig(mi_helper,ballJoint = ml_rigJoints[1],
	                                   ikControl = mi_controlIK,fkControl = mi_controlFK,
	                                   buildIK=True, driverAttr=mPlug_FKIK,
	                                   setupVisBlend = True,
	                                   moduleInstance = self._i_module)
	d_return['mi_rigGroup'].parent = self._i_constrainNull.mNode#parent rig group to constrain null
	mi_fkLoc = d_return['md_locs']['fk']#Grab the fk loc
	self._i_rigNull.connectChildNode(mi_fkLoc,'locFK','rigNull')
	log.info("%s >> fkLoc: %s "%(_str_funcName,mi_fkLoc.p_nameShort)) 
	
	mi_blendLoc = d_return['md_locs']['blend']#Grab the blend loc	
	self._i_rigNull.connectChildNode(mi_blendLoc,'locBlend','rigNull')
	log.info("%s >> blendLoc: %s "%(_str_funcName,mi_blendLoc.p_nameShort)) 
	
    except StandardError,error:
	raise StandardError,"%s >> base rig setup fail! | error: %s"%(_str_funcName,error)   
    
    try:#Connect vis blend between fk/ik
	#>>> Setup a vis blend result
	mPlug_FKon = d_return['mPlug_fkVis']
	mPlug_IKon = d_return['mPlug_ikVis']
	log.info("%s >> mPlug_FKon: %s "%(_str_funcName,mPlug_FKon.p_combinedShortName)) 
	log.info("%s >> mPlug_IKon: %s "%(_str_funcName,mPlug_IKon.p_combinedShortName)) 
	
	mPlug_FKon.doConnectOut("%s.visibility"%self._i_constrainNull.controlsFKNull.mNode)
	mPlug_IKon.doConnectOut("%s.visibility"%self._i_constrainNull.controlsIKNull.mNode)
	
	try:#Setup constain loc
	    mi_settingsFKLoc = mi_settings.doLoc()
	    mi_settingsFKLoc.parent = mi_controlFK
	    self.connect_toRigGutsVis(mi_settingsFKLoc)
	    _str_const = mc.parentConstraint([mi_settingsFKLoc.mNode,mi_controlIK.mNode],mi_settings.masterGroup.mNode,maintainOffset = False)[0]
	    l_weightTargets = mc.parentConstraint(_str_const,q=True,weightAliasList = True)
	    
	    mPlug_FKon.doConnectOut("%s.%s"%(_str_const,l_weightTargets[0]))
	    mPlug_IKon.doConnectOut("%s.%s"%(_str_const,l_weightTargets[1])) 
	        
	except StandardError,error:raise StandardError,"constrain loc | %s"%error	
	
    except StandardError,error:
	raise StandardError,"%s >> fk/ik blend setup fail! | error: %s"%(_str_funcName,error)       
    
    #Setup pupil and iris
    #=====================================================================================
    #The gist of what we'll do is setup identical attributes on both fk and ik controls
    #and then blend between the two to drive what is actually influencing the joints
    #scale = (fk_result * fk_pupil) + (ik_result *ik_pupil)
    try:#pupil   mPlug_FKIK
	l_extraSetups = ['pupil','iris']
	for i,n in enumerate(l_extraSetups):
	    buffer = self._i_rigNull.getMessage('%sJoint'%n)
	    if buffer:    
		log.info("%s >> Seting up %s"%(_str_funcName,n)) 
		mi_tmpJoint = cgmMeta.cgmObject(buffer[0])
		mi_rigJoint = mi_tmpJoint.rigJoint
		mPlug_tmp = cgmMeta.cgmAttr(mi_settings,'%s'%n,attrType='float',initialValue=1,keyable=True, defaultValue=1)
		for a in self._jointOrientation[1:]:
		    mPlug_tmp.doConnectOut("%s.s%s"%(mi_rigJoint.mNode,a))		
		"""
		mPlug_FK_in = cgmMeta.cgmAttr(ml_controlsFKNull[0],'%s'%n,attrType='float',initialValue=1,keyable=True, defaultValue=1)
		mPlug_FK_out = cgmMeta.cgmAttr(ml_controlsFKNull[0],'%s_fkResult'%n,attrType='float',hidden=False,lock=True)	    
		mPlug_IK_in = cgmMeta.cgmAttr(mi_controlIK,'%s'%n,attrType='float',initialValue=1,keyable=True,defaultValue=1)
		mPlug_IK_out = cgmMeta.cgmAttr(mi_controlIK,'%s_ikResult'%n,attrType='float',hidden=False,lock=True)	    
		mPlug_Blend_out = cgmMeta.cgmAttr(mi_tmpJoint,'%s_blendResult'%n,attrType='float',hidden=False,lock=True)	    
		NodeF.argsToNodes("%s = %s * %s"%(mPlug_FK_out.p_combinedShortName,
		                                  mPlug_FKon.p_combinedShortName,
		                                  mPlug_FK_in.p_combinedShortName)).doBuild()
		NodeF.argsToNodes("%s = %s * %s"%(mPlug_IK_out.p_combinedShortName,
		                                  mPlug_IKon.p_combinedShortName,
		                                  mPlug_IK_in.p_combinedShortName)).doBuild()	 
		NodeF.argsToNodes("%s = %s + %s"%(mPlug_Blend_out.p_combinedShortName,
		                                  mPlug_FK_out.p_combinedShortName,
		                                  mPlug_IK_out.p_combinedShortName)).doBuild()	
		for a in self._jointOrientation[1:]:
		    mPlug_Blend_out.doConnectOut("%s.s%s"%(mi_tmpJoint.mNode,a))
		"""
		
    except StandardError,error:
	raise StandardError,"%s >> pupil setup fail! | error: %s"%(_str_funcName,error)   
	
    #Dynamic parent groups
    #====================================================================================
    try:#>>>> eye
	ml_eyeDynParents = [mi_eyeLook]
	if self._mi_moduleParent:
	    ml_eyeDynParents.append(self._mi_moduleParent.rigNull.rigJoints[0])	    
	ml_eyeDynParents.append(self._i_masterControl)
		
	#Add our parents
	i_dynGroup = mi_controlIK.dynParentGroup
	log.info("Dyn group at setup: %s"%i_dynGroup)
	i_dynGroup.dynMode = 0
	
	for o in ml_eyeDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()
	
    except StandardError,error:
	raise StandardError,"%s >> ik dynamic parent setup fail! | error: %s"%(_str_funcName,error)   

    #Parent and constraining bits
    #====================================================================================
    try:#Constrain to parent module
	ml_rigJoints[0].parent = self._i_constrainNull.mNode
	if self._mi_moduleParent:
	    mc.parentConstraint(self._mi_moduleParent.rig_getSkinJoints()[-1].mNode,self._i_constrainNull.mNode,maintainOffset = True)
    except StandardError,error:
	raise StandardError,"%s >> Connect to parent fail! | error: %s"%(_str_funcName,error)
    
    try:#Lock Groups ======================================================================
	for mi_ctrl in [mi_controlFK,mi_controlIK,mi_settings]:
	    mi_ctrl._setControlGroupLocks(True)
    except StandardError,error:
	raise StandardError,"%s >> lock groups fail! | error: %s"%(_str_funcName,error)
    
    #Final stuff
    self._set_versionToCurrent()
    return True 
    
@cgmGeneral.Timer
def build_matchSystem(self):
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("eye.build_deformationRig>>bad self!")
	raise StandardError,error
    _str_funcName = "build_rig(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75) 
    
    try:#Gather Data    
	try:
	    mi_eyeLook = self._get_eyeLook()
	    mi_eyeLookDynSwitch = mi_eyeLook.dynSwitch
	except StandardError,error:raise StandardError,"eyeLook fail! | %s"%(error)	
	
	try:mi_controlIK = self._i_rigNull.controlIK
	except StandardError,error:raise StandardError,"controlIK fail! | %s"%(error)
	
	try:mi_controlFK=  self._i_rigNull.controlFK 
	except StandardError,error:raise StandardError,"controlFK fail! | %s"%(error)
	
	try:ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
	except StandardError,error:raise StandardError,"rigJoints fail! | %s"%(error)
	
	try:mi_settings = self._i_rigNull.settings
	except StandardError,error:raise StandardError,"settings fail! | %s"%(error)
	
	try:mi_locBlend= self._i_rigNull.locBlend
	except StandardError,error:raise StandardError,"mi_locBlend fail! | %s"%(error)
	
	try:mi_locFK= self._i_rigNull.locFK
	except StandardError,error:raise StandardError,"mi_locFK fail! | %s"%(error)	
	
	ml_fkJoints = self._i_rigNull.msgList_get('fkJoints')
	ml_ikJoints = self._i_rigNull.msgList_get('ikJoints')
	
	try:mi_dynSwitch = self._i_dynSwitch
	except StandardError,error:raise StandardError,"dynSwitch fail! | %s"%(error)
	
    except StandardError,error:
	raise StandardError,"%s >> Gather data fail! | error: %s"%(_str_funcName,error)        
    try:#>>> First IK to FK
	i_ikMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlIK,
	                                       dynPrefix = "FKtoIK",
	                                       dynMatchTargets=mi_locBlend)
    except StandardError,error:
	raise StandardError,"%s >> ik to fk fail! | error: %s"%(_str_funcName,error)       
    try:#>>> FK to IK
	#============================================================================
	i_fkMatch = cgmRigMeta.cgmDynamicMatch(dynObject = mi_controlFK,
	                                       dynPrefix = "IKtoFK",
	                                       dynMatchTargets=mi_locBlend)
    except StandardError,error:
	raise StandardError,"%s >> fk to ik fail! | error: %s"%(_str_funcName,error)   
        
    #>>> Register the switches
    try:
	mi_dynSwitch.addSwitch('snapToFK',[mi_settings.mNode,'blend_FKIK'],
	                       0,
	                       [i_fkMatch])
    
	mi_dynSwitch.addSwitch('snapToIK',[mi_settings.mNode,'blend_FKIK'],
	                       1,
	                       [i_ikMatch])
	
	mi_eyeLookDynSwitch.addSwitch('snapToFK',[mi_settings.mNode,'blend_FKIK'],
	                              0,
	                              [i_fkMatch])
	mi_eyeLookDynSwitch.addSwitch('snapToIK',[mi_settings.mNode,'blend_FKIK'],
	                              1,
	                              [i_ikMatch])	
    except StandardError,error:
	raise StandardError,"%s >> switch setup fail! | error: %s"%(_str_funcName,error)   
    return True
    
#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'rig','function':build_rig},
                    4:{'name':'match','function':build_matchSystem},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------
