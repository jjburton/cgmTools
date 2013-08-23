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
__version__ = 0.08112013

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
from cgm.core.lib import validateArgs as cgmValid

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
reload(joints)

#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['rigJoints']   
@cgmGeneral.Timer
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
    try:pass
    except StandardError,error:
	log.error("build_eyeball>>__bindSkeletonSetup__ fail!")
	raise StandardError,error   
    
@cgmGeneral.Timer
def build_rigSkeleton(self):
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
__d_controlShapes__ = {'shape':['eyeballFK','eyeballIK']}
@cgmGeneral.Timer
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
	l_toBuild = ['eyeballIK','eyeballFK']
	mShapeCast.go(self._i_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
	#self._i_rigNull.connectChildNode(self._md_controlShapes['eyeball'],'shape_eyeball',"rigNull")
	
    except StandardError,error:
	log.error("build_eyeball>>Build shapes fail!")
	raise StandardError,error 
    return True
    
#>>> Controls
#===================================================================
@cgmGeneral.Timer
def build_controls(self):
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
    ml_rigJoints = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('rigJoints'),cgmMeta.cgmObject)
    
    #>>>Make a few extra groups for storing controls and what not to in the deform group
    for grp in ['controlsFK','controlsIK']:
	i_dup = self._i_constrainNull.doDuplicateTransform(True)
	i_dup.parent = self._i_constrainNull.mNode
	i_dup.addAttr('cgmTypeModifier',grp,lock=True)
	i_dup.doName()
	self._i_constrainNull.connectChildNode(i_dup,grp,'owner')
        
    l_controlsAll = []
    #==================================================================
    try:#>>>> FK 
	if not mi_fkShape:
	    raise StandardError,"%s >>> Must have at least one fk control"%_str_funcName    
	
	mi_fkShape.parent = self._i_constrainNull.controlsFK.mNode
	i_obj = mi_fkShape
	
	d_buffer = mControlFactory.registerControl(i_obj,copyTransform = ml_rigJoints[0],
                                                   makeAimable=True,typeModifier='fk',) 	    
	i_obj = d_buffer['instance']
	i_obj.axisAim = "%s+"%self._jointOrientation[0]
	i_obj.axisUp= "%s+"%self._jointOrientation[1]	
	i_obj.axisOut= "%s+"%self._jointOrientation[2]
	
	#We're gonna lock the aim rot
	cgmMeta.cgmAttr(i_obj,'r%s'%self._jointOrientation[0], keyable = False, lock=True,hidden=True)
	
	    
	self._i_rigNull.msgList_connect(i_obj,'controlsFK',"rigNull")
	l_controlsAll.extend([i_obj])	
    
    except StandardError,error:	
	raise StandardError,"%s >>> Build fk fail! | error: %s"%(_str_funcName,error)
    
    #==================================================================
    try:#>>>> IK 
	if not mi_ikShape:
	    raise StandardError,"%s >>> Must have at least one ik control"%_str_funcName    
	
	mi_ikShape.parent = self._i_constrainNull.controlsIK.mNode
	i_obj = mi_ikShape
	
	d_buffer = mControlFactory.registerControl(i_obj,makeAimable=False,typeModifier='ik',
	                                           addDynParentGroup=True) 	    
	i_obj = d_buffer['instance']	
	    
	self._i_rigNull.msgList_connect(i_obj,'controlsIK',"rigNull")
	l_controlsAll.extend([i_obj])	
    
    except StandardError,error:	
	raise StandardError,"%s >>> Build ik fail! | error: %s"%(_str_funcName,error)    

    #==================================================================   
    #Connect all controls
    self._i_rigNull.msgList_connect(l_controlsAll,'controlsAll')
    
    return True

@cgmGeneral.Timer
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
	mi_moduleParent = False
	if self._i_module.getMessage('moduleParent'):
	    mi_moduleParent = self._i_module.moduleParent
	    
	ml_controlsIK = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('controlsIK'),cgmMeta.cgmObject)
	ml_controlsFK = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('controlsFK'),cgmMeta.cgmObject)	
	ml_rigJoints = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('rigJoints'),cgmMeta.cgmObject)
	
	log.info("ml_controlsFK: %s"%[o.getShortName() for o in ml_controlsFK])	
	log.info("ml_controlsIK: %s"%[o.getShortName() for o in ml_controlsIK])		
	log.info("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
		
	v_aim = cgmValid.simpleAxis("%s+"%self._jointOrientation[0]).p_vector
	v_up = cgmValid.simpleAxis("%s+"%self._jointOrientation[1]).p_vector
	#aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	#upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1]) 
	
    except StandardError,error:
	raise StandardError,"%s >> Gather data fail! | error: %s"%(_str_funcName,error)
    
    
    try:#Constrain to pelvis
	if mi_moduleParent:
	    mc.parentConstraint(mi_moduleParent.rig_getSkinJoints()[-1].mNode,self._i_constrainNull.mNode,maintainOffset = True)
    except StandardError,error:
	raise StandardError,"%s >> Connect to parent fail! | error: %s"%(_str_funcName,error)
    

    #Parent and constrain joints
    #====================================================================================
    ml_rigJoints[0].parent = self._i_deformNull.mNode#hip

    #For each of our rig joints, find the closest constraint target joint
    pntConstBuffer = mc.pointConstraint(ml_controlsFK[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False,weight=1)
    orConstBuffer = mc.orientConstraint(ml_controlsFK[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False,weight=1)
    mc.connectAttr((ml_controlsFK[0].mNode+'.s'),(ml_rigJoints[0].mNode+'.s'))   
    
    #Final stuff
    self._set_versionToCurrent()
    return True 

    
@cgmGeneral.Timer
def __build__(self, buildTo='',*args,**kws): 
    """
    For the eyeball, build order is skeleton first as we need our mid segment handle joints created to cast from
    """
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("eyeball.build_deformationRig>>bad self!")
	raise StandardError,error
    
    if not self.isRigSkeletonized():
	build_rigSkeleton(self)  
    if buildTo.lower() == 'skeleton':return True    
    if not self.isShaped():
	build_shapes(self)
    if buildTo.lower() == 'shapes':return True
    build_controls(self)
    if buildTo.lower() == 'controls':return True    
    build_rig(self)
    if buildTo.lower() == 'rig':return True    
    
    return True

#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'rig','function':build_rig},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------
