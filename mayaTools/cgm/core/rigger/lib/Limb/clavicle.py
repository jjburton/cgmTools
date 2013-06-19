"""
------------------------------------------
cgm.core.rigger: Limb.clavicle
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

clavicle rig builder
================================================================
"""
__version__ = 0.06172013

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
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)

from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.rigger import JointFactory as jFactory
from cgm.core.lib import nameTools
reload(mShapeCast)
reload(mControlFactory)
from cgm.core.rigger.lib import rig_Utils as rUtils
reload(rUtils)
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
__l_jointAttrs__ = ['rigJoints','fkJoints']   

@r9General.Timer
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
    
    #>>>Create joint chains
    #=============================================================    
    try:
	#>>Rig chain  
	#=====================================================================	
	l_rigJoints = mc.duplicate(self._l_skinJoints,po=True,ic=True,rc=True)
	ml_rigJoints = []
	for i,j in enumerate(l_rigJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
	    i_j.doName()
	    l_rigJoints[i] = i_j.mNode
	    ml_rigJoints.append(i_j)
	ml_rigJoints[0].parent = False
	
	self._i_rigNull.connectChildrenNodes(ml_rigJoints,'rigJoints',"rigNull")
    except StandardError,error:
	log.error("%s.build_rigSkeleton>>Build rig joints fail!"%self._strShortName)
	raise StandardError,error   
    
    try:#>>FK chain
	#=====================================================================		
	ml_fkJoints = []
	for i,i_ctrl in enumerate(self._i_templateNull.controlObjects):
	    if not i_ctrl.getMessage('handleJoint'):
		raise StandardError,"%s.build_rigSkeleton>>> failed to find a handle joint from: '%s'"%(self._i_module.getShortName(),i_ctrl.getShortName())
	    i_new = cgmMeta.cgmObject(mc.duplicate(i_ctrl.getMessage('handleJoint')[0],po=True,ic=True)[0])
	    i_new.addAttr('cgmTypeModifier','fk',attrType='string',lock=True)
	    i_new.doName()
	    if ml_fkJoints:#if we have data, parent to last
		i_new.parent = ml_fkJoints[-1]
	    else:i_new.parent = False
	    i_new.rotateOrder = self._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations
	    ml_fkJoints.append(i_new)	
    except StandardError,error:
	log.error("%s.build_rigSkeleton>>Build fk joints fail!"%self._strShortName)
	raise StandardError,error   
    
    #==================================================================  
    d_fkRotateOrders = {'hip':0,'ankle':0}#old hip - 5    
    try:#>>>Rotate Orders
	for i_obj in ml_fkJoints:
	    if i_obj.getAttr('cgmName') in d_fkRotateOrders.keys():
		i_obj.rotateOrder = d_fkRotateOrders.get(i_obj.cgmName)   		
	
    except StandardError,error:
	log.error("%s.build_rigSkeleton>>> Rotate orders fail!"%self._strShortName)		
	raise StandardError,error
    

    try:#>>> Store em all to our instance
	#=====================================================================	
	self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints',"rigNull")#push back to reset
	self._i_rigNull.connectChildrenNodes(ml_fkJoints,'fkJoints',"rigNull")

	##log.info("anchorJoints>> %s"%self._i_rigNull.getMessage('anchorJoints',False))
	log.info("fkJoints>> %s"%self._i_rigNull.getMessage('fkJoints',False))
   
    except StandardError,error:
	log.error("%s.build_clavicle>>StoreJoints fail!"%self._strShortName)
	raise StandardError,error   

    ml_jointsToConnect = []
    ml_jointsToConnect.extend(ml_rigJoints)    
    
    for i_jnt in ml_jointsToConnect:
	i_jnt.overrideEnabled = 1		
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    
	
	
#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['clavicle']}
def build_shapes(self):
    """
    """ 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("clavicle.build_rig>>bad self!")
	raise StandardError,error
    
    if self._i_templateNull.handles > 2:
	raise StandardError, "%s.build_shapes>>> Too many handles. don't know how to rig"%(self._strShortName)
    
    if not self.isRigSkeletonized():
	raise StandardError, "%s.build_shapes>>> Must be rig skeletonized to shape"%(self._strShortName)	
       
    #>>>Build our Shapes
    #=============================================================
    try:
	#Rest of it
	l_toBuild = ['clavicle']
	mShapeCast.go(self._i_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
	self._i_rigNull.connectChildNode(self._md_controlShapes['clavicle'],'shape_clavicle',"rigNull")
	
    except StandardError,error:
	log.error("build_clavicle>>Build shapes fail!")
	raise StandardError,error 
    
#>>> Controls
#===================================================================
def build_controls(self):
    """
    """    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("clavicle.build_rig>>bad self!")
	raise StandardError,error
    
    if not self.isShaped():
	raise StandardError,"%s.build_controls>>> needs shapes to build controls"%self._strShortName
    if not self.isRigSkeletonized():
	raise StandardError,"%s.build_controls>>> needs shapes to build controls"%self._strShortName

    ml_controlsFK = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('shape_clavicle'),cgmMeta.cgmObject) 
    ml_fkJoints = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('fkJoints'),cgmMeta.cgmObject)
    
    #>>>Make a few extra groups for storing controls and what not to in the deform group
    for grp in ['controlsFK']:
	i_dup = self._i_constrainNull.doDuplicateTransform(True)
	i_dup.parent = self._i_constrainNull.mNode
	i_dup.addAttr('cgmTypeModifier',grp,lock=True)
	i_dup.doName()
	
	self._i_constrainNull.connectChildNode(i_dup,grp,'owner')
    
    log.info(ml_controlsFK)
    log.info(ml_fkJoints)    
    
    l_controlsAll = []
    #==================================================================
    try:#>>>> FK Segments
	if len( ml_controlsFK ) != 1:
	    raise StandardError,"%s.build_controls>>> Must have at least one fk control"%self._strShortName	    
	
	ml_fkJoints[0].parent = self._i_constrainNull.controlsFK.mNode
	
	i_obj = ml_controlsFK[0]
	
	d_buffer = mControlFactory.registerControl(i_obj,shapeParentTo=ml_fkJoints[0],
                                                   makeAimable=True,typeModifier='fk',) 	    
	i_obj = d_buffer['instance']
	i_obj.axisAim = "%s+"%self._jointOrientation[0]
	i_obj.axisUp= "%s+"%self._jointOrientation[1]	
	i_obj.axisOut= "%s+"%self._jointOrientation[2]
	
	cgmMeta.cgmAttr(i_obj,'radius',hidden=True)
	    
	for i_obj in ml_controlsFK:
	    i_obj.delete()
	    
	self._i_rigNull.connectChildrenNodes([ml_fkJoints[0]],'controlsFK',"rigNull")
	l_controlsAll.extend([ml_fkJoints[0]])	
    
    except StandardError,error:	
	log.error("%s.build_controls>>> Build fk fail!"%self._strShortName)
	raise StandardError,error
    
    #==================================================================   
    """
    try:#>>>> Add all of our Attrs
	#Add driving attrs
	mPlug_roll = cgmMeta.cgmAttr(i_IKEnd,'roll',attrType='float',defaultValue = 0,keyable = True)

    except StandardError,error:
	log.error("%s.build_controls>>> Add Control Attrs Fail!"%self._strShortName)	
    """
    #Connect all controls
    self._i_rigNull.connectChildrenNodes(l_controlsAll,'controlsAll')
    
    return True

def build_rig(self):
    """
    """    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("%s.build_deformationRig>>bad self!"%self._strShortName)
	raise StandardError,error
    
    try:#>>>Get data
	orientation = self._jointOrientation or modules.returnSettingsData('jointOrientation')
	mi_moduleParent = False
	if self._i_module.getMessage('moduleParent'):
	    mi_moduleParent = self._i_module.moduleParent
	    
	ml_controlsFK = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('controlsFK'),cgmMeta.cgmObject)	
	ml_rigJoints = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('rigJoints'),cgmMeta.cgmObject)
	
	log.info("ml_controlsFK: %s"%[o.getShortName() for o in ml_controlsFK])	
	log.info("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
		
	aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1]) 
	
    except StandardError,error:
	log.error("clavicle.build_rig>> Gather data fail!")
	raise StandardError,error
    
    #Constrain to pelvis
    if mi_moduleParent:
	mc.parentConstraint(mi_moduleParent.rigNull.skinJoints[-1].mNode,self._i_constrainNull.mNode,maintainOffset = True)
    

    #Parent and constrain joints
    #====================================================================================
    ml_rigJoints[0].parent = self._i_deformNull.mNode#hip

    #For each of our rig joints, find the closest constraint target joint
    pntConstBuffer = mc.pointConstraint(ml_controlsFK[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False,weight=1)
    orConstBuffer = mc.orientConstraint(ml_controlsFK[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False,weight=1)
    mc.connectAttr((ml_controlsFK[0].mNode+'.s'),(ml_rigJoints[0].mNode+'.s'))   
    
    #Final stuff
    self._i_rigNull.version = str(__version__)
    return True 

    
@r9General.Timer
def __build__(self, buildTo='',*args,**kws): 
    """
    For the clavicle, build order is skeleton first as we need our mid segment handle joints created to cast from
    """
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.build_deformationRig>>bad self!")
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