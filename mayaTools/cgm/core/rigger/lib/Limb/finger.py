"""
------------------------------------------
cgm.core.rigger: Limb.finger
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Finger rig builder
================================================================
"""
__version__ = 0.06242013

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
reload(NodeF)

from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools
reload(mShapeCast)
reload(mControlFactory)
from cgm.core.rigger.lib import rig_Utils as rUtils
from cgm.core.rigger.lib import joint_Utils as jUtils

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
__l_jointAttrs__ = ['rigJoints','fkJoints','ikJoints','blendJoints']   
__d_preferredAngles__ = {'finger':[0,0,10],'thumb':[0,0,10]}#In terms of aim up out for orientation relative values
__d_controlShapes__ = {'shape':['segmentFK','settings','cap']}

@cgmGeneral.Timer
def __bindSkeletonSetup__(self):
    """
    TODO: Do I need to connect per joint overrides or will the final group setup get them?
    """
    log.info(">>> %s.__bindSkeletonSetup__ >> "%self._strShortName + "="*75)            
    try:
	if not self._cgmClass == 'JointFactory.go':
	    log.error("Not a JointFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("f.__bindSkeletonSetup__>>bad self!")
	raise StandardError,error
    
    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self._i_module.rigNull.skinJoints or []
    if not self._i_module.isSkeletonized():
	raise StandardError, "%s is not skeletonized yet."%self._strShortName
    
    try:#Reparent joints
	"""
	ml_skinJoints = self._i_module.rigNull.skinJoints
	last_i_jnt = False
	for i,i_jnt in enumerate(ml_skinJoints):
	    if i_jnt.hasAttr('cgmName'):
		if last_i_jnt:i_jnt.parent = last_i_jnt.mNode
		last_i_jnt = i_jnt"""
		
	ml_moduleJoints = self._i_module.rigNull.moduleJoints #Get the module joints
	ml_skinJoints = []
	ml_handleJoints = self._i_module.rig_getHandleJoints()
	ml_pairs = lists.parseListToPairs(ml_moduleJoints)
	
	jUtils.add_defHelpJoint(ml_pairs[1][0],ml_pairs[1][1],helperType = 'childRootHold',orientation=self.jointOrientation)
	
	for ml_pair in ml_pairs[1:]:
	    jUtils.add_defHelpJoint(ml_pair[0],ml_pair[1],helperType = 'halfPush',orientation=self.jointOrientation)
	    
	"""
	for i,i_jnt in enumerate(ml_moduleJoints):
	    ml_skinJoints.append(i_jnt)		
	    if i_jnt.hasAttr('d_jointFlags'):
		if i_jnt.d_jointFlags.get('isHandle'):
		    if i == 0:i_jnt.parent = ml_moduleJoints[0].mNode#Parent head to root
		    i_dupJnt = i_jnt.doDuplicate()#Duplicate
		    i_dupJnt.addAttr('cgmNameModifier','extra')#Tag
		    i_jnt.doName()#Rename
		    i_dupJnt.doName()#Rename
		    i_dupJnt.parent = i_jnt#Parent
		    i_dupJnt.connectChildNode(i_jnt,'rootJoint','scaleJoint')#Connect
		    #Fix the isHandle Flag -------------------------------------
		    d_buffer = i_dupJnt.d_jointFlags
		    d_buffer.pop('isHandle')
		    i_dupJnt.d_jointFlags = d_buffer
		    #------------------------------------------------------------
		    ml_skinJoints.append(i_dupJnt)#Append
		    log.info("%s.__bindSkeletonSetup__ >> Created scale joint for '%s' >> '%s'"%(self._strShortName,i_jnt.getShortName(),i_dupJnt.getShortName()))
	
	for i,i_jnt in enumerate(ml_handleJoints[1:]):
	    i_jnt.parent = ml_handleJoints[i].mNode
		    
	#We have to connect back our lists because duplicated joints with message connections duplicate those connections
	self._i_rigNull.connectChildrenNodes(ml_moduleJoints,'moduleJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_skinJoints,'skinJoints','module')
	
	self._i_module.rig_getReport()#report
	"""
	ml_moduleJoints = self._i_module.rigNull.moduleJoints
	self._i_rigNull.connectChildrenNodes(ml_moduleJoints,'skinJoints','module')	
	self._i_module.rig_getReport()#report
	
    except StandardError,error:
	log.error("build_arm>>__bindSkeletonSetup__ fail!")
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
	log.error("finger.build_deformationRig>>bad self!")
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
	ml_rigJoints[0].parent = False#Parent to deformGroup
	
	self._i_rigNull.connectChildrenNodes(ml_rigJoints,'rigJoints',"rigNull")
    except StandardError,error:
	log.error("build_rigSkeleton>>Build rig joints fail!")
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
	log.error("build_rigSkeleton>>Build fk joints fail!")
	raise StandardError,error   
    
    #==================================================================
    """
    #Finger - aim out up
    try:#>>>Rotate Orders
	for i_obj in ml_fkJoints:
	    i_obj.rotateOrder = 2   		
	
    except StandardError,error:
	log.error("%s.build_controls>>> Rotate orders fail!"%self._strShortName)		
	raise StandardError,error
    """
    try:#>>Blend chain
	#=====================================================================
	ml_blendJoints = []
	for i_jnt in ml_fkJoints:
	    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
	    i_new.addAttr('cgmTypeModifier','blend',attrType='string',lock=True)
	    i_new.doName()
	    if ml_blendJoints:#if we have data, parent to last
		i_new.parent = ml_blendJoints[-1]
	    ml_blendJoints.append(i_new)	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build blend joints fail!")
	raise StandardError,error  
    
    try:#>>IK chain
	#=====================================================================	
	"""Important - we're going to set our preferred angles on the main ik joints so ik works as expected"""
	ml_ikJoints = []
	for i_jnt in ml_fkJoints:
	    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
	    i_new.addAttr('cgmTypeModifier','ik',attrType='string',lock=True)
	    i_new.doName()
	    if self._partType in __d_preferredAngles__.keys():
		log.info("preferred angles(%s)>>> %s"%(self._partType ,__d_preferredAngles__.get(self._partType)))
		for i,v in enumerate(__d_preferredAngles__.get(self._partType )):	  
		    i_new.__setattr__('preferredAngle%s'%self._jointOrientation[i].upper(),v)
	    if ml_ikJoints:#if we have data, parent to last
		i_new.parent = ml_ikJoints[-1]
	    ml_ikJoints.append(i_new)	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build ik joints fail!")
	raise StandardError,error   
    """
    try:#>>IK PV chain
	#=====================================================================	
	ml_ikPVJoints = []
	for i_jnt in ml_ikJoints[:3]:
	    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
	    i_new.addAttr('cgmTypeModifier','ikPV',attrType='string',lock=True)
	    i_new.doName()
	    if ml_ikPVJoints:#if we have data, parent to last
		i_new.parent = ml_ikPVJoints[-1]
	    ml_ikPVJoints.append(i_new)	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build ik pv joints fail!")
	raise StandardError,error   
    
    try:#>>IK NoFlip chain
	#=====================================================================	
	ml_ikNoFlipJoints = []
	for i_jnt in ml_ikJoints[:3]:
	    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
	    i_new.addAttr('cgmTypeModifier','ikNoFlip',attrType='string',lock=True)
	    i_new.doName()
	    if ml_ikNoFlipJoints:#if we have data, parent to last
		i_new.parent = ml_ikNoFlipJoints[-1]
	    ml_ikNoFlipJoints.append(i_new)	
	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build ik no flip joints fail!")
	raise StandardError,error   
    """ 
    """
    try:#>>Influence chain
	#=====================================================================		
	ml_segmentHandleJoints = []#To use later as well
	for i_ctrl in self._i_templateNull.controlObjects:
	    if i_ctrl.getAttr('cgmName') in ['shoulder','elbow','wrist']:
		if not i_ctrl.getMessage('handleJoint'):
		    raise StandardError,"%s.build_rigSkeleton>>> failed to find a handle joint from: '%s'"%(self._i_module.getShortName(),i_ctrl.getShortName())
		i_handle = i_ctrl.handleJoint
		ml_segmentHandleJoints.append(i_handle)

	if len(ml_segmentHandleJoints)!=3:
	    raise StandardError,"%s.build_rigSkeleton>>> don't have 3 influence joints: '%s'"%(self._i_module.getShortName(),ml_segmentHandleJoints)
	    
	#Make influence joints
	l_influencePairs = lists.parseListToPairs(ml_segmentHandleJoints)
	ml_influenceJoints = []
	ml_influenceChains = []
	
	log.info(l_influencePairs)
	for i,m_pair in enumerate(l_influencePairs):
	    str_nameModifier = 'seg_%s'%i	    
	    #tmp_chain = [m_pair[0]]
	    tmp_chain = []
	    #Make our base joints
	    for ii,i_jnt in enumerate(m_pair):
		i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
		i_new.parent = False
		i_new.addAttr('cgmNameModifier',str_nameModifier,attrType='string',lock=True)
		i_new.addAttr('cgmTypeModifier','influence',attrType='string',lock=True)		
		if tmp_chain:
		    i_new.parent = tmp_chain[-1].mNode
		i_new.doName()
		i_new.rotateOrder = self._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations    
		tmp_chain.append(i_new)
		
	    log.info("%s.build_rigSkeleton>>> Splitting influence segment: 2 |'%s' >> '%s'"%(self._i_module.getShortName(),m_pair[0].getShortName(),m_pair[1].getShortName()))
	    l_new_chain = joints.insertRollJointsSegment(tmp_chain[0].mNode,tmp_chain[1].mNode,1)
	    log.info("%s.build_rigSkeleton>>> split chain: %s"%(self._i_module.getShortName(),l_new_chain))
	    ml_midJoints = []
	    #Let's name our new joints
	    for ii,jnt in enumerate(l_new_chain):
		i_jnt = cgmMeta.cgmObject(jnt,setClass=True)
		i_jnt.doCopyNameTagsFromObject(m_pair[0].mNode)
		i_jnt.addAttr('cgmName','%s_mid_%s'%(m_pair[0].cgmName,ii),lock=True)
		i_jnt.addAttr('cgmNameModifier',str_nameModifier,attrType='string',lock=True)		
		i_jnt.addAttr('cgmTypeModifier','influence',attrType='string',lock=True)		
		i_jnt.doName()
		ml_midJoints.append(i_jnt)
		#ml_influenceJoints.insert(startIndex + ii + 1,i_jnt)
	    ml_segmentChain = [tmp_chain[0]]
	    ml_segmentChain.extend(ml_midJoints)
	    ml_segmentChain.append(tmp_chain[-1])
	    for i_j in ml_segmentChain:ml_influenceJoints.append(i_j)
	    ml_influenceChains.append(ml_segmentChain)#append to influence chains
    
	joints.doCopyJointOrient(ml_influenceChains[-1][-2].mNode,ml_influenceChains[-1][-1].mNode)

	#Figure out how we wanna store this, ml_influence joints 
	for i_jnt in ml_influenceJoints:
	    i_jnt.parent = False
	    
	for i_j in ml_influenceJoints:
	    log.info(i_j.getShortName())
	    jFactory.metaFreezeJointOrientation(i_j.mNode)	
    
    except StandardError,error:
	log.error("build_rigSkeleton>>Build influence joints fail!")
	raise StandardError,error  """  
    """
    try:#>>Anchor chain
	#=====================================================================	
	ml_anchors = []
	for i_jnt in ml_segmentHandleJoints:
	    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
	    i_new.addAttr('cgmTypeModifier','anchor',attrType='string',lock=True)
	    i_new.parent = False
	    i_new.doName()

	    ml_anchors.append(i_new)	 
    except StandardError,error:
	log.error("build_rigSkeleton>>Build anchor joints fail!")
	raise StandardError,error """
    """
    try:#>>Segment chain  
	#=====================================================================
	ml_segmentChains = []
	
	for i,i_handle in enumerate(ml_segmentHandleJoints[:-1]):
	    log.info(i_handle)
	    buffer_segmentTargets = i_handle.getListPathTo(ml_segmentHandleJoints[i+1].mNode)	
	    log.info("segment %s: %s"%(i,buffer_segmentTargets))
	    #l_newChain = mc.duplicate(buffer_segmentTargets,po=True,ic=True)
	    #log.info(l_newChain)
	    ml_newChain = []
	    for i2,j in enumerate(buffer_segmentTargets):
		i_j = cgmMeta.cgmObject(j,setClass=True).doDuplicate()
		i_j.addAttr('cgmTypeModifier','seg_%s'%i,attrType='string',lock=True)
		i_j.doName()
		if ml_newChain:
		    i_j.parent = ml_newChain[-1].mNode
		ml_newChain.append(i_j)
		
	    ml_newChain[0].parent = False#Parent to deformGroup
	    ml_segmentChains.append(ml_newChain)
	
	#Sometimes last segement joints have off orientaions, we're gonna fix
	joints.doCopyJointOrient(ml_segmentChains[-1][-2].mNode,ml_segmentChains[-1][-1].mNode)
	for segmentChain in ml_segmentChains:
	    jFactory.metaFreezeJointOrientation([i_jnt.mNode for i_jnt in segmentChain])
	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build segment joints fail!")
	raise StandardError,error   
    """
    try:#>>> Store em all to our instance
	#=====================================================================	
	self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints',"rigNull")#push back to reset
	
	self._i_rigNull.connectChildrenNodes(ml_fkJoints,'fkJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_blendJoints,'blendJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_ikJoints,'ikJoints',"rigNull")
	#self._i_rigNull.connectChildrenNodes(ml_ikNoFlipJoints,'ikNoFlipJoints',"rigNull")
	#self._i_rigNull.connectChildrenNodes(ml_ikPVJoints,'ikPVJoints',"rigNull")
	#self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'influenceJoints',"rigNull")
	#for i,ml_chain in enumerate(ml_segmentChains):
	    #log.info("segment chain: %s"%[i_j.getShortName() for i_j in ml_chain])
	    #self._i_rigNull.connectChildrenNodes(ml_chain,'segment%s_Joints'%i,"rigNull")
	    #log.info("segment%s_Joints>> %s"%(i,self._i_rigNull.getMessage('segment%s_Joints'%i,False)))
	#for i,ml_chain in enumerate(ml_influenceChains):
	    #log.info("influence chain: %s"%[i_j.getShortName() for i_j in ml_chain])	    
	    #self._i_rigNull.connectChildrenNodes(ml_chain,'segment%s_InfluenceJoints'%i,"rigNull")
	    #log.info("segment%s_InfluenceJoints>> %s"%(i,self._i_rigNull.getMessage('segment%s_InfluenceJoints'%i,False)))
	    
	##log.info("anchorJoints>> %s"%self._i_rigNull.getMessage('anchorJoints',False))
	log.info("fkJoints>> %s"%self._i_rigNull.getMessage('fkJoints',False))
	log.info("ikJoints>> %s"%self._i_rigNull.getMessage('ikJoints',False))
	log.info("blendJoints>> %s"%self._i_rigNull.getMessage('blendJoints',False))
	#log.info("influenceJoints>> %s"%self._i_rigNull.getMessage('influenceJoints',False))
	#log.info("ikNoFlipJoints>> %s"%self._i_rigNull.getMessage('ikNoFlipJoints',False))
	#log.info("ikPVJoints>> %s"%self._i_rigNull.getMessage('ikPVJoints',False))
   
    except StandardError,error:
	log.error("build_finger>>StoreJoints fail!")
	raise StandardError,error   

    ml_jointsToConnect = []
    ml_jointsToConnect.extend(ml_rigJoints)    
    ml_jointsToConnect.extend(ml_ikJoints)
    ml_jointsToConnect.extend(ml_blendJoints)       
    ##ml_jointsToConnect.extend(ml_anchors)  
    #for ml_chain in ml_segmentChains + ml_influenceChains:
	#ml_jointsToConnect.extend(ml_chain)

    for i_jnt in ml_jointsToConnect:
	i_jnt.overrideEnabled = 1		
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    
	
#>>> Shapes
#===================================================================
def build_shapes(self):
    """
    """ 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("finger.build_rig>>bad self!")
	raise StandardError,error
    
    if self._i_templateNull.handles not in range(4,6):
	raise StandardError, "%s.build_shapes>>> Too many handles. don't know how to rig"%(self._strShortName)
    
    if not self.isRigSkeletonized():
	raise StandardError, "%s.build_shapes>>> Must be rig skeletonized to shape"%(self._strShortName)	
    
    #>>> Get our segment influence joints
    #=============================================================    
    l_influenceChains = []
    ml_influenceChains = []
    for i in range(50):
	buffer = self._i_rigNull.getMessage('segment%s_InfluenceJoints'%i)
	if buffer:
	    l_influenceChains.append(buffer)
	    ml_influenceChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	else:
	    break    
	
    log.info("%s.build_shapes>>> Influence Chains -- cnt: %s | lists: %s"%(self._strShortName,len(l_influenceChains),l_influenceChains))
    
    #>>>Build our Shapes
    #=============================================================
    try:
	#Segment IK
	"""
	ml_segmentIKShapes = []
	for i,ml_chain in enumerate(ml_influenceChains):
	    mShapeCast.go(self._i_module,['segmentIK'],targetObjects = [i_jnt.mNode for i_jnt in ml_chain] , storageInstance=self)#This will store controls to a dict called    
	    log.info("%s.build_shapes>>> segmentIK chain %s: %s"%(self._strShortName,i,self._md_controlShapes))
	    ml_segmentIKShapes.extend(self._md_controlShapes['segmentIK'])
	    
	    self._i_rigNull.connectChildrenNodes(self._md_controlShapes['segmentIK'],'shape_segmentIK_%s'%i,"rigNull")		
	
	self._i_rigNull.connectChildrenNodes(ml_segmentIKShapes,'shape_segmentIK',"rigNull")		
	"""
	#Rest of it
	l_toBuild = __d_controlShapes__['shape']
	mShapeCast.go(self._i_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
	log.info(self._md_controlShapes)
	log.info(self._md_controlPivots)
	self._i_rigNull.connectChildrenNodes(self._md_controlShapes['segmentFK'],'shape_controlsFK',"rigNull")	
	self._i_rigNull.connectChildNode(self._md_controlShapes['settings'],'shape_settings',"rigNull")		
	self._i_rigNull.connectChildNode(self._md_controlShapes['moduleCap'],'shape_cap',"rigNull")
	
    except StandardError,error:
	log.error("%s.build_shapes>>Build shapes fail!"%self._strShortName)
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
	log.error("%s.build_rig>>bad self!"%self._strShortName)
	raise StandardError,error
    
    if not self.isShaped():
	raise StandardError,"%s.build_controls>>> needs shapes to build controls"%self._strShortName
    if not self.isRigSkeletonized():
	raise StandardError,"%s.build_controls>>> needs shapes to build controls"%self._strShortName
    """
    __d_controlShapes__ = {'shape':['controlsFK','midIK','settings','hand'],
	             'pivot':['toe','heel','ball','inner','outer
    for shape in __d_controlShapes__['shape']:
	self.__dict__['mi_%s'%shape] = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_%s'%shape),noneValid=False)
	log.info(self.__dict__['mi_%s'%shape] )"""
    ml_controlsFK = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('shape_controlsFK'),cgmMeta.cgmObject)
    ml_segmentIK = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('shape_segmentIK'),cgmMeta.cgmObject)
    #self._i_rigNull.connectChildrenNodes(self._md_controlShapes['segmentIK'],'shape_segmentIK_%s'%i,"rigNull")		
    l_segmentIKChains = []
    ml_segmentIKChains = []
    for i in range(50):
	buffer = self._i_rigNull.getMessage('shape_segmentIK_%s'%i)
	if buffer:
	    l_segmentIKChains.append(buffer)
	    ml_segmentIKChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	else:
	    break  
	 
    #mi_midIK = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_midIK'),cgmMeta.cgmObject)
    mi_settings= cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_settings'),cgmMeta.cgmObject)
    ml_fkJoints = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('fkJoints'),cgmMeta.cgmObject)
    mi_cap = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_moduleCap'),cgmMeta.cgmObject)
    
    log.info("mi_settings: '%s'"%mi_settings.getShortName())
    log.info("mi_cap: '%s'"%mi_cap.getShortName())    
    log.info("ml_fkJoints: %s"%[i_o.getShortName() for i_o in ml_fkJoints])
    
    #>>>Make a few extra groups for storing controls and what not to in the deform group
    for grp in ['controlsFK','controlsIK']:
	i_dup = self._i_constrainNull.doDuplicateTransform(True)
	i_dup.parent = self._i_constrainNull.mNode
	i_dup.addAttr('cgmTypeModifier',grp,lock=True)
	i_dup.doName()
	
	self._i_constrainNull.connectChildNode(i_dup,grp,'owner')
	
    l_controlsAll = []
    #==================================================================
    try:#>>>> FK Segments
	if len( ml_controlsFK )<3:
	    raise StandardError,"%s.build_controls>>> Must have at least three fk controls"%self._strShortName	    
	
	#for i,i_obj in enumerate(ml_controlsFK[1:]):#parent
	    #i_obj.parent = ml_controlsFK[i].mNode
	ml_fkJoints[0].parent = self._i_constrainNull.controlsFK.mNode
		
	for i,i_obj in enumerate(ml_controlsFK):
	    d_buffer = mControlFactory.registerControl(i_obj,shapeParentTo=ml_fkJoints[i],setRotateOrder=3,
	                                               makeAimable=True,typeModifier='fk',) 	    
	    
	    i_obj = d_buffer['instance']
	    i_obj.axisAim = "%s+"%self._jointOrientation[0]
	    i_obj.axisUp= "%s+"%self._jointOrientation[1]	
	    i_obj.axisOut= "%s+"%self._jointOrientation[2]
	    
	    cgmMeta.cgmAttr(i_obj,'radius',hidden=True)
	    
	for i_obj in ml_controlsFK:
	    i_obj.delete()
	    
	#ml_controlsFK[0].masterGroup.parent = self._i_constrainNull.mNode
	self._i_rigNull.connectChildrenNodes(ml_fkJoints,'controlsFK',"rigNull")
	l_controlsAll.extend(ml_fkJoints)	
    
    except StandardError,error:	
	log.error("%s.build_controls>>> Build fk fail!"%self._strShortName)
	raise StandardError,error
    
    #==================================================================    
    try:#>>>> IK Handle
	i_IKEnd = mi_cap
	i_IKEnd.parent = False
	d_buffer = mControlFactory.registerControl(i_IKEnd,copyPivot=ml_fkJoints[-2].mNode,setRotateOrder=3,
	                                           typeModifier='ik',addSpacePivots = 1, addDynParentGroup = True,
	                                           addConstraintGroup=True,
	                                           makeAimable = True)
	i_IKEnd = d_buffer['instance']	
	i_IKEnd.masterGroup.parent = self._i_constrainNull.controlsIK.mNode
	
	#i_loc.delete()#delete
	self._i_rigNull.connectChildNode(i_IKEnd,'controlIK',"rigNull")#connect
	l_controlsAll.append(i_IKEnd)	

	#Set aims
	i_IKEnd.axisAim = 'z+'
	i_IKEnd.axisUp= 'y+'
	
    except StandardError,error:
	log.error("%s.build_controls>>> Build ik handle fail!"%self._strShortName)	
	raise StandardError,error   
    
    #==================================================================  
    """
    try:#>>>> midIK Handle
	i_IKmid = mi_midIK
	i_IKmid.parent = False
	d_buffer = mControlFactory.registerControl(i_IKmid,addSpacePivots = 1,
	                                           typeModifier='ik',addDynParentGroup = True, addConstraintGroup=True,
	                                           makeAimable = False,setRotateOrder=4)
	i_IKmid = d_buffer['instance']	
	i_IKmid.masterGroup.parent = self._i_constrainNull.controlsIK.mNode
	i_IKmid.addAttr('scale',lock=True,hidden=True)
	#i_loc.delete()#delete
	self._i_rigNull.connectChildNode(i_IKmid,'midIK',"rigNull")#connect
	l_controlsAll.append(i_IKmid)	
	
    except StandardError,error:
	log.error("%s.build_controls>>> Build ik handle fail!"%self._strShortName)	
	raise StandardError,error   """
        
    #==================================================================
    try:#>>>> Settings
	d_buffer = mControlFactory.registerControl(mi_settings,addExtraGroups=0,typeModifier='settings',autoLockNHide=True,
                                                   setRotateOrder=2)       
	i_obj = d_buffer['instance']
	i_obj.masterGroup.parent = self._i_constrainNull.mNode
	self._i_rigNull.connectChildNode(mi_settings,'settings',"rigNull")
	l_controlsAll.append(mi_settings)
	
	mi_settings.addAttr('blend_FKIK', defaultValue = 0, attrType = 'float', minValue = 0, maxValue = 1, keyable = False,hidden = False,lock=True)
	
	#Vis network for stub
	#Add our attrs
	mPlug_moduleSubDriver = cgmMeta.cgmAttr(mi_settings,'visSub', value = 1, defaultValue = 1, attrType = 'bool', keyable = False,hidden = False)
	mPlug_result_moduleSubDriver = cgmMeta.cgmAttr(mi_settings,'visSub_out', defaultValue = 1, attrType = 'bool', keyable = False,hidden = True,lock=True)
	
	#Get one of the drivers
	if self._i_module.getAttr('cgmDirection') and self._i_module.cgmDirection.lower() in ['left','right']:
	    str_mainSubDriver = "%s.%sSubControls_out"%(self._i_masterControl.controlVis.getShortName(),
	                                                self._i_module.cgmDirection)
	else:
	    str_mainSubDriver = "%s.subControls_out"%(self._i_masterControl.controlVis.getShortName())

	iVis = self._i_masterControl.controlVis
	visArg = [{'result':[mPlug_result_moduleSubDriver.obj.mNode,mPlug_result_moduleSubDriver.attr],
	           'drivers':[[iVis,"subControls_out"],[mi_settings,mPlug_moduleSubDriver.attr]]}]
	NodeF.build_mdNetwork(visArg)
	
    except StandardError,error:
	log.error("%s.build_controls>>> Build settings fail!"%self._strShortName)		
	raise StandardError,error    
    
    #==================================================================  
    """
    try:#>>>> IK Segments
	for i,chain in enumerate(ml_segmentIKChains):
	    ml_controlChain =[]
	    for i_obj in chain:
		d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='ik',
		                                           setRotateOrder=2)       
		i_obj = d_buffer['instance']
		i_obj.masterGroup.parent = self._i_constrainNull.mNode
		ml_controlChain.append(i_obj)
		
		mPlug_result_moduleSubDriver.doConnectOut("%s.visibility"%i_obj.mNode)
	    self._i_rigNull.connectChildrenNodes(ml_controlChain,'segmentHandles_%s'%i,"rigNull")
	    l_controlsAll.extend(ml_controlChain)	
	    if i == 1:
		#Need to do a few special things for our main segment handle
		i_mainHandle = chain[0]
		self._i_rigNull.connectChildNode(i_mainHandle,'mainSegmentHandle',"rigNull")
		curves.setCurveColorByName(i_mainHandle.mNode,self._i_module.getModuleColors()[0])    
		attributes.doBreakConnection(i_mainHandle.mNode,'visibility')
	
    except StandardError,error:
	log.error("%s.build_controls>>> IK segments fail!"%self._strShortName)		
	raise StandardError,error"""
    #==================================================================    
    try:#>>>> Add all of our Attrs
	#Add driving attrs
	mPlug_length = cgmMeta.cgmAttr(i_IKEnd,'length',attrType='float',defaultValue = 1,minValue=0,keyable = True)		
	mPlug_fingerSpin = cgmMeta.cgmAttr(i_IKEnd,'fingerSpin',attrType='float',defaultValue = 0,keyable = True)
	mPlug_stretch = cgmMeta.cgmAttr(i_IKEnd,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
	#mPlug_showElbow = cgmMeta.cgmAttr(i_IKEnd,'showElbow',attrType='bool',defaultValue = 0,keyable = False)
	mPlug_lengthUpr= cgmMeta.cgmAttr(i_IKEnd,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
	mPlug_lengthLwr = cgmMeta.cgmAttr(i_IKEnd,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)	
	#mPlug_lockMid = cgmMeta.cgmAttr(i_IKmid,'lockMid',attrType='float',defaultValue = 0,keyable = True,minValue=0,maxValue=1.0)
	
    except StandardError,error:
	log.error("%s.build_controls>>> Add Control Attrs Fail!"%self._strShortName)	
	
    #Connect all controls
    self._i_rigNull.connectChildrenNodes(l_controlsAll,'controlsAll')
    
    return True
    

    
@cgmGeneral.Timer
def build_FKIK(self):
    """
    """
    try:#===================================================
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("finger.build_FKIK>>bad self!")
	raise StandardError,error
    
    #>>>Get data
    ml_controlsFK =  self._i_rigNull.controlsFK   
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_blendJoints = self._i_rigNull.blendJoints
    ml_fkJoints = self._i_rigNull.fkJoints
    ml_ikJoints = self._i_rigNull.ikJoints

    
    mi_settings = self._i_rigNull.settings
        
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    outVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[2])
    
    mi_controlIK = self._i_rigNull.controlIK

    for chain in [ml_ikJoints,ml_blendJoints]:
	chain[0].parent = self._i_constrainNull.mNode
	
    #for more stable ik, we're gonna lock off the lower channels degrees of freedom
    for chain in [ml_ikJoints]:
	for axis in self._jointOrientation[:2]:
	    log.info(axis)
	    for i_j in chain[1:]:
		attributes.doSetAttr(i_j.mNode,"jointType%s"%axis.upper(),1)
	
    #=============================================================    
    try:#>>>Finger Root Control and root follow
	for attr in ['tx','ty','tz']:#Unlock a few things
	    i_attr = cgmMeta.cgmAttr(ml_fkJoints[0],attr)
	    i_attr.p_keyable = True
	    i_attr.p_locked = False	   	

	#we have to rebuild a little so that we can use our fk base control both for fk and ik
	#Create a orient group that tracks the  module constrain null
	if self._partType == 'finger':
	    buffer_fkGroup = ml_fkJoints[0].parent
	    i_orientGroup = cgmMeta.cgmObject( ml_fkJoints[1].doGroup(True),setClass=True )
	    i_orientGroup.addAttr('cgmTypeModifier','toOrient')
	    i_orientGroup.doName()
	    
	    #constrain it 
	    str_orConst = mc.orientConstraint(self._i_constrainNull.mNode,i_orientGroup.mNode,maintainOffset = True)[0]
	    attributes.doSetLockHideKeyableAttr(i_orientGroup.mNode)#lockNHide
	    self._i_constrainNull.connectChildNode(i_orientGroup,'fingerRoot','owner')#Connect
	    i_orientGroup.parent = self._i_constrainNull.mNode
	    
	    i_parentGroup = cgmMeta.cgmObject( i_orientGroup.doGroup(True),setClass=True )
	    i_parentGroup.addAttr('cgmTypeModifier','toParent')
	    i_parentGroup.doName()	
	    str_prntConst = mc.parentConstraint( ml_fkJoints[0].mNode,i_parentGroup.mNode,maintainOffset = True)[0]
	    i_parentGroup.parent = buffer_fkGroup
	    
 
	    #attributes.doSetLockHideKeyableAttr(ml_fkJoints[0].mNode,lock = False, visible=True, keyable=True, channels=['tx','ty','tz'])
	    
	    #Constrain ik base to fk base
	    mc.orientConstraint(ml_fkJoints[0].mNode,ml_ikJoints[0].mNode,maintainOffset = True)
	    ml_fkJoints[0].parent = self._i_constrainNull.mNode

    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> Finger Root Control error: %s"%(self._strShortName,error)
    
    #=============================================================    
    try:#>>>FK Length connector
	if self._partType == 'finger':
	    ml_fkToDo = ml_fkJoints[1:-1]
	else:#thumb
	    ml_fkToDo = ml_fkJoints[:-1]
	    log.info([i_jnt.getShortName() for i_jnt in ml_fkToDo])
	    
	for i,i_jnt in enumerate(ml_fkToDo):
	    rUtils.addJointLengthAttr(i_jnt,orientation=self._jointOrientation)
	
	#IK
	rUtils.addJointLengthAttr(ml_ikJoints[-2],[mi_controlIK,'length'],orientation=self._jointOrientation)
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> fk length connect error: %s"%(self._strShortName,error)
    
    #=============================================================  
    try:#>>>IK No Flip Chain
	mPlug_globalScale = cgmMeta.cgmAttr(self._i_masterControl.mNode,'scaleY')
	ml_ikNoFlipJoints = ml_ikJoints#Link
	if self._partType == 'finger':
	    mi_ikStart = ml_ikNoFlipJoints[1]
	    mi_ikEnd = ml_ikNoFlipJoints[-2]
	    mi_constraintGroup = self._i_constrainNull.fingerRoot
	else:#thumb 
	    mi_ikStart = ml_ikNoFlipJoints[0]
	    mi_ikEnd = ml_ikNoFlipJoints[-2]
	    mi_constraintGroup = self._i_constrainNull
	
	#i_tmpLoc = mi_ikStart.doLoc()#loc the first real
	#i_tmpLoc.parent = mi_constraintGroup.mNode
	#str_twistGroup = i_tmpLoc.doGroup(True)
	i_tmpLoc = mi_ikEnd.doLoc()#loc the first real
	i_tmpLoc.parent = mi_controlIK.mNode
	str_twistGroup = i_tmpLoc.doGroup(True)
	
	f_dist = distance.returnDistanceBetweenPoints(mi_ikStart.getPosition(),ml_ikNoFlipJoints[-1].getPosition()) #Measure first finger joint to end
	f_dist = f_dist * 1.5
	if self._direction == 'left':#if right, rotate the pivots
	    i_tmpLoc.__setattr__('t%s'%self._jointOrientation[2],-f_dist)
	else:
	    i_tmpLoc.__setattr__('t%s'%self._jointOrientation[2],f_dist)
	
	#Create no flip finger IK
	d_ankleNoFlipReturn = rUtils.IKHandle_create(mi_ikStart.mNode,mi_ikEnd.mNode,lockMid=False,
	                                             nameSuffix = 'noFlip',rpHandle=True,controlObject=mi_controlIK,addLengthMulti=True,
	                                             globalScaleAttr=mPlug_globalScale.p_combinedName, stretch='translate',moduleInstance=self._i_module)
	
	mi_fingerIKHandleNF = d_ankleNoFlipReturn['mi_handle']
	ml_distHandlesNF = d_ankleNoFlipReturn['ml_distHandles']
	mi_rpHandleNF = d_ankleNoFlipReturn['mi_rpHandle']
	#mPlug_lockMid = d_ankleNoFlipReturn['mPlug_lockMid']
	
	#No Flip RP handle
	Snap.go(mi_rpHandleNF,i_tmpLoc.mNode,True)#Snape to hand control, then move it out...
	i_tmpLoc.delete()
	
	mi_rpHandleNF.doCopyNameTagsFromObject(self._i_module.mNode, ignore = ['cgmName','cgmType'])
	mi_rpHandleNF.addAttr('cgmName','%sPoleVector'%self._partName, attrType = 'string')
	mi_rpHandleNF.addAttr('cgmTypeModifier','noFlip')
	mi_rpHandleNF.doName()
	
	#spin
	#=========================================================================================
	#Make a spin group
	i_spinGroup = cgmMeta.cgmObject(str_twistGroup)
	i_spinGroup.doCopyNameTagsFromObject(self._i_module.mNode, ignore = ['cgmName','cgmType'])	
	i_spinGroup.addAttr('cgmName','%sNoFlipSpin'%self._partName)
	i_spinGroup.doName()
	
	i_spinGroup.doZeroGroup()
	mi_rpHandleNF.parent = i_spinGroup.mNode
		
	#Setup arg
	mPlug_fingerSpin = cgmMeta.cgmAttr(mi_controlIK,'fingerSpin')
	mPlug_fingerSpin.doConnectOut("%s.r%s"%(i_spinGroup.mNode,self._jointOrientation[0]))
	
	#>>>Parent IK handles
	mi_fingerIKHandleNF.parent = mi_controlIK.mNode#handle to control	
	ml_distHandlesNF[-1].parent = mi_controlIK.mNode#handle to control
	ml_distHandlesNF[0].parent = mi_constraintGroup.mNode#start to root
	ml_distHandlesNF[1].parent = mi_constraintGroup.mNode#mid to root
	
	#>>> Fix our ik_handle twist at the end of all of the parenting
	#poleVector = mc.poleVectorConstraint (mi_rpHandleNF.mNode,mi_fingerIKHandleNF.mNode)  		
	rUtils.IKHandle_fixTwist(mi_fingerIKHandleNF)#Fix the twist
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> IK No Flip error: %s"%(self._strShortName,error)
    
    #=============================================================   
    try:#>>>Constrain IK Finger
	#Create hand IK
	#ml_ikJoints[-2].parent = False
	mc.orientConstraint(mi_controlIK.mNode,mi_ikEnd.mNode, maintainOffset = True)
	#mc.pointConstraint(mi_controlIK.mNode,ml_ikJoints[-2].mNode, maintainOffset = True)

	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> IK No Flip error: %s"%(self._strShortName,error)
    
    #=============================================================    
    try:#>>>Connect Blend Chains and connections
	#>>> Main blend
	mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',lock=False,keyable=True)
	
	rUtils.connectBlendChainByConstraint(ml_fkJoints,ml_ikJoints,ml_blendJoints,
	                                     driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])
	
	#>>> Settings - constrain
	mc.parentConstraint(ml_blendJoints[0].mNode, mi_settings.masterGroup.mNode, maintainOffset = True)
	
	#>>> Setup a vis blend result
	mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=False)	
	mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=False)	
	
	NodeF.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,mPlug_IKon.p_combinedName,mPlug_FKon.p_combinedName)
	
	mPlug_FKon.doConnectOut("%s.visibility"%self._i_constrainNull.controlsFK.mNode)
	mPlug_IKon.doConnectOut("%s.visibility"%self._i_constrainNull.controlsIK.mNode)
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> blend connect error: %s"%(self._strShortName,error)
    log.info("%s.build_FKIK complete!"%self._i_module.getShortName())
    return True

def build_deformation(self):
    """
    Rotate orders
    hips = 3
    """     
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("finger.build_deformationRig>>bad self!")
	raise StandardError,error
    
    #==========================================================================
    try:#Info gathering
	#segmentHandles_%s
	#Get our segment controls
	ml_segmentHandleChains = self._get_segmentHandleChains()

	#Get our segment joints
	ml_segmentChains = self._get_segmentChains()
	if len(ml_segmentChains)>2:
	    raise StandardError, "%s.build_deformation>>> Too many segment chains, not a regular finger."%(self._strShortName)
	
	#>>>Influence Joints
	ml_influenceChains = self._get_influenceChains()
	if len(ml_influenceChains)!=len(ml_segmentChains):
	    raise StandardError, "%s.build_deformation>>> Segment chains don't equal segment influence chains"%(self._strShortName)
	
	#>>>Get data
	ml_controlsFK =  self._i_rigNull.controlsFK    
	ml_rigJoints = self._i_rigNull.rigJoints
	ml_blendJoints = self._i_rigNull.blendJoints
	mi_settings = self._i_rigNull.settings
    
	mi_controlIK = self._i_rigNull.controlIK
	mi_controlMidIK = self._i_rigNull.midIK
	
	aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
	
    except StandardError,error:
	log.error("%s.build_deformation>>> data gather fail!"%(self._strShortName))
	raise StandardError,error
    
    #Main Attributes
    #==================================================================================== 
    #This is a bit of a complicated setup, pretty much we're gathering and splitting out potential drivers of the twist per segment
    str_twistOrientation = "r%s"%self._jointOrientation[0]   
    
    ###mPlug_TestValue = cgmMeta.cgmAttr(mi_settings,"result_testValue" , attrType='float' , keyable = True)        
    ###mPlug_InvertedHipBlend= cgmMeta.cgmAttr(mi_settings,"result_invertHipBlend" , attrType='float' , lock = True)    
    ###mPlug_InvertedAnkle = cgmMeta.cgmAttr(mi_settings,"result_invertAnkle" , attrType='float' , lock = True)
    ###mPlug_InvertedelbowSpin = cgmMeta.cgmAttr(mi_settings,"result_invertelbowSpin" , attrType='float' , lock = True)
    mPlug_elbowSpinResult = cgmMeta.cgmAttr(mi_settings,"result_elbowSpinInfluence" , attrType='float' , lock = True)
    ###mPlug_elbowAnkleNegate = cgmMeta.cgmAttr(mi_settings,"result_elbowAnkleNegate" , attrType='float' , lock = True)
    ###mPlug_InvertedHipBlendInfluence= cgmMeta.cgmAttr(mi_settings,"result_invertHipBlendInfluence" , attrType='float' , lock = True)    
    mPlug_MidIKSpaceHandInfluence = cgmMeta.cgmAttr(mi_settings,"result_midIKSpaceHandInfluence" , attrType='float' , lock = True)	    
    mPlug_HandInfluence = cgmMeta.cgmAttr(mi_settings,"result_handInfluence" , attrType='float' , lock = True)	    
    mPlug_InvertedIKHand = cgmMeta.cgmAttr(mi_settings,"result_invertIKHand" , attrType='float' , lock = True)	    
    ##mPlug_worldIKHandResult = cgmMeta.cgmAttr(mi_settings,"result_worldIKHand" , attrType='float' , lock = True)	    
    
    mPlug_showElbowMidTwist = cgmMeta.cgmAttr(mi_settings,"result_showElbowMidTwist" , attrType='float' , lock = True)
    
    #Existing
    mPlug_elbowSpin = cgmMeta.cgmAttr(mi_controlIK,'elbowSpin',attrType='float')
    mPlug_showElbow = cgmMeta.cgmAttr(mi_controlIK,'showElbow',attrType='bool')
    
    #Invert the elbow spin
    """
    NodeF.argsToNodes("%s = -%s"%(mPlug_InvertedelbowSpin.p_combinedShortName,
                                  mPlug_elbowSpin.p_combinedShortName)).doBuild() """ 
    #invert the hand
    NodeF.argsToNodes("%s = -%s"%(mPlug_InvertedIKHand.p_combinedShortName,
                                  "%s.ry"%(mi_controlIK.getShortName()))).doBuild()
    #invert the blend hip
    """
    NodeF.argsToNodes("%s = -%s.%s"%(mPlug_InvertedHipBlend.p_combinedShortName,
                                     ml_blendJoints[0].getShortName(),
                                     str_twistOrientation)).doBuild()"""
    
    #Value to pull from when the elbow is being shown
    """
    NodeF.argsToNodes("%s = %s * %s"%(mPlug_elbowAnkleNegate.p_combinedShortName,
                                      mPlug_showElbow.p_combinedShortName,
                                      "%s.ry"%(mi_controlIK.getShortName()))).doBuild()  """
    
    #Show elbow * blend joint 0's twist
    NodeF.argsToNodes("%s = %s * %s.%s"%(mPlug_showElbowMidTwist.p_combinedShortName,
                                         mPlug_showElbow.p_combinedShortName,
                                         ml_blendJoints[0].getShortName(),
                                         str_twistOrientation)).doBuild()  
    
    #elbow spin result -- if show elbow, is 0, use it. Adds the elbow spin in if the
    NodeF.argsToNodes("%s = if %s == 0: %s else 0 "%(mPlug_elbowSpinResult.p_combinedShortName,
                                                     mPlug_showElbow.p_combinedShortName,
                                                     mPlug_elbowSpin.p_combinedShortName)).doBuild()
    
    #Hand influence based on elbow space
    """
    If the elbow is visible AND elbow in hand space, use blendJoint, else, use inverted hand
    If the elbow is not visible, use inverted hand
    mPlug_HandInfluence
    mPlug_MidIKSpaceHandInfluence
    mi_controlMidIK space
    mPlug_InvertedIKHand
    mPlug_MidIKSpace
    mPlug_worldIKHandResult
    """
    """
    mPlug_Blend0 = cgmMeta.cgmAttr(ml_blendJoints[0],str_twistOrientation)
    mPlug_elbowSpaceHolder = cgmMeta.cgmAttr(mi_settings,"elbowSpace_in" , attrType='int' , lock = True)    
    NodeF.argsToNodes("%s = if %s == 1:%s else %s"%(mPlug_HandInfluence.p_combinedShortName,#result
                                                    mPlug_showElbow.p_combinedShortName,#driver
                                                    mPlug_MidIKSpaceHandInfluence.p_combinedShortName,#option 1
                                                    mPlug_InvertedIKHand.p_combinedShortName)).doBuild()#option 2
    
    NodeF.argsToNodes("%s = if %s == 0:%s else %s"%(mPlug_MidIKSpaceHandInfluence.p_combinedShortName,#result
                                                    mPlug_elbowSpaceHolder.p_combinedShortName,#driver
                                                    mPlug_InvertedIKHand.p_combinedShortName,#option 1
                                                    mPlug_InvertedIKHand.p_combinedShortName)).doBuild()#option 2
    
    NodeF.argsToNodes("%s = %s + %s"%(mPlug_worldIKHandResult.p_combinedShortName,#result
                                      mPlug_InvertedIKHand.p_combinedShortName,#option 1
                                      mPlug_Blend0.p_combinedShortName)).doBuild()#option 2
    
    
    #Mid IK
    mPlug_midIKResult = cgmMeta.cgmAttr(mi_settings,'result_midIK',attrType='float',defaultValue = 0,keyable = True,hidden=False, lock = True)
    NodeF.argsToNodes("%s = %s * %s"%(mPlug_midIKResult.p_combinedShortName,
                                      mPlug_showElbow.p_combinedShortName,
                                      "%s.%s"%(mi_controlMidIK.getShortName(),str_twistOrientation))).doBuild()        
    """
    #New method for getting proper hand twist
    """
    The gist is that we create a loc of the last segment joint of seg 1, we orient constrain that to the ik control
    This is our base value for the hand twist. The problem is that an ik chain can flip at 180 cause issues on our second segment.
    
    IF blend0>0 : use +baseValue + blend
    else: use -baseValue + blend

    """ 
    mPlug_Blend0 = cgmMeta.cgmAttr(ml_blendJoints[0],str_twistOrientation)
    mPlug_ConstrainGroupTwist = cgmMeta.cgmAttr(self._i_constrainNull,str_twistOrientation)
    
    mPlug_elbowSpaceHolder = cgmMeta.cgmAttr(mi_settings,"elbowSpace_in" , attrType='int' , lock = True) #REMOVE THIS  
    
    mPlug_worldIKHandResultNew = cgmMeta.cgmAttr(mi_settings,"result_worldIKHand" , attrType='float' , lock = True)	    
    mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKIn" , attrType='float' , lock = True)
    mPlug_worldIKEndInInverted = cgmMeta.cgmAttr(mi_settings,"result_worldIKInverted" , attrType='float' , lock = True)
    mPlug_worldIKEndUseValue = cgmMeta.cgmAttr(mi_settings,"result_worldIKEndUseValue" , attrType='float' , lock = True)
    
    mPlug_constrainInvert = cgmMeta.cgmAttr(mi_settings,"result_constrainInvert" , attrType='float' , lock = True)    
    mPlug_constrainUseValue = cgmMeta.cgmAttr(mi_settings,"result_constrainUseValue" , attrType='float' , lock = True)
    
    NodeF.argsToNodes("%s = -%s"%(mPlug_worldIKEndInInverted.p_combinedShortName,#result
                                  mPlug_worldIKEndIn.p_combinedShortName,#driver
                                  )).doBuild()#    
    NodeF.argsToNodes("%s = -%s"%(mPlug_constrainInvert.p_combinedShortName,#result
                                  mPlug_ConstrainGroupTwist.p_combinedShortName,#driver
                                  )).doBuild()#    
    
    NodeF.argsToNodes("%s = %s + %s"%(mPlug_worldIKHandResultNew.p_combinedShortName,#result
                                      mPlug_Blend0.p_combinedShortName,#driver2
                                      mPlug_worldIKEndUseValue.p_combinedShortName,#driver                                                
                                      )).doBuild()#   

    
    NodeF.argsToNodes("%s = if %s < 0:%s else %s"%(mPlug_worldIKEndUseValue.p_combinedShortName,#result
                                                   mPlug_Blend0.p_combinedShortName,#driver
                                                   mPlug_worldIKEndIn.p_combinedShortName,#option 1
                                                   mPlug_worldIKEndInInverted.p_combinedShortName)).doBuild()#option 2  
    
    NodeF.argsToNodes("%s = if %s < 0:%s else %s"%(mPlug_constrainUseValue.p_combinedShortName,#result
                                                   mPlug_Blend0.p_combinedShortName,#driver
                                                   mPlug_ConstrainGroupTwist.p_combinedShortName,#option 1
                                                   mPlug_constrainInvert.p_combinedShortName)).doBuild()#option 2  
    #Control Segment
    #====================================================================================
    ml_segmentCurves = []
    ml_segmentReturns = []
    ml_segmentJointChainsReset = []
    try:#Control Segment
	log.info(self._jointOrientation)
	capAim = self._jointOrientation[0].capitalize()
	log.info("capAim: %s"%capAim)
	for i,ml_segmentHandles in enumerate(ml_segmentHandleChains):
	    i_startControl = ml_segmentHandles[0]
	    i_endControl = ml_segmentHandles[-1]
	    l_jointChain = [i_jnt.mNode for i_jnt in ml_segmentChains[i]]
	    l_infuenceJoints = [ml_influenceChains[i][0].getShortName(),ml_influenceChains[i][-1].getShortName()]
	    log.info("startControl: %s"%i_startControl.getShortName())
	    log.info("endControl: %s"%i_endControl.getShortName())
	    log.info("jointChain: %s"%l_jointChain)
	    log.info("influenceJoints: %s"%l_infuenceJoints)
	    str_baseName = self._partName+"_seg%s"%i
	    str_segCount = "seg%s"%i
	    #Create segment
	    curveSegmentReturn = rUtils.createCGMSegment(l_jointChain,
		                                         addSquashStretch=True,
		                                         addTwist=True,
		                                         influenceJoints=[l_infuenceJoints[0],l_infuenceJoints[-1]],
		                                         startControl= i_startControl,
		                                         endControl= i_endControl,
		                                         orientation=self._jointOrientation,
		                                         baseName = str_baseName,
	                                                 moduleInstance=self._i_module)
	    
	    ml_segmentReturns.append(curveSegmentReturn)
	    
	    i_curve = curveSegmentReturn['mi_segmentCurve']
	    i_curve.parent = self._i_rigNull.mNode
	    i_curve.segmentGroup.parent = self._i_rigNull.mNode
	    ml_segmentCurves.append(i_curve)
	    
	    midReturn = rUtils.addCGMSegmentSubControl(ml_influenceChains[i][1],
						       segmentCurve = i_curve,
						       baseParent = l_infuenceJoints[0],
						       endParent = l_infuenceJoints[-1],
						       midControls = ml_segmentHandles[1].mNode,
						       baseName = str_baseName,
						       orientation = self._jointOrientation,
	                                               moduleInstance=self._i_module)
	    
	    for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
		i_grp.parent = self._i_constrainNull.mNode
		
	    #Parent our joint chains
	    i_curve.driverJoints[0].parent = self._i_constrainNull.mNode
	    #ml_segmentChains[i][0].parent = self._i_deformNull.mNode
	    ml_segmentChains[i][0].parent = self._i_constrainNull.mNode
	    
	    try:#We're gonna attach to the blend chain
		mi_segmentAnchorStart = i_curve.anchorStart
		mi_segmentAnchorEnd = i_curve.anchorEnd
		mi_segmentAttachStart = i_curve.attachStart
		mi_segmentAttachEnd = i_curve.attachEnd 
		mi_distanceBuffer = i_curve.scaleBuffer
	    
		log.debug("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
		log.debug("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
		log.debug("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
		log.debug("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
		log.debug("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)
		
		#>>> parent the anchors to the deform null
		mi_segmentAnchorStart.parent =  self._i_constrainNull.mNode
		mi_segmentAnchorEnd.parent =  self._i_constrainNull.mNode	
		
		#>>> parent constrain handle anchor
		mc.parentConstraint( ml_blendJoints[i].mNode,mi_segmentAnchorStart.mNode,maintainOffset = True)
		if i == 0:
		    mc.parentConstraint( self._i_rigNull.mainSegmentHandle.mNode,mi_segmentAnchorEnd.mNode,maintainOffset = True)
		else:	
		    mc.parentConstraint( ml_blendJoints[i+1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset = True)
		
		#segment handles to influence parents
		i_startControl.masterGroup.parent = ml_influenceChains[i][0].parent
		i_endControl.masterGroup.parent = ml_influenceChains[i][-1].parent
		
	    except StandardError,error:
		log.error("%s.build_deformation>>> Failed to connect anchor: %s"%(self._strShortName,mi_segmentAnchorStart.getShortName()))
		raise StandardError,error
	    

	    #Influence joint to segment handles		
	    ml_influenceChains[i][0].parent = i_startControl.mNode
	    ml_influenceChains[i][-1].parent = i_endControl.mNode
		    	    
	    	    
	    #>>> Build fk and ik drivers
	    """
	    fk result = fk1 + fk2 + fk3 + -fk4
	    ik result = ik.y + elbow twist?
	    Need sums, multiply by the fk/ikon
	    """
	    #>>> Setup a vis blend result
	    mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon')	
	    mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon')	
	    
	    #>>>Attrs
	    mPlug_TwistStartResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStart'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
	    mPlug_TwistEndResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEnd'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
	    
	    mPlug_TwistStartFKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStartFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
	    mPlug_TwistEndFKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEndFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
	    mPlug_TwistStartFKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistStartFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
	    mPlug_TwistEndFKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistEndFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
	    
	    mPlug_TwistStartIKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStartIK'%str_segCount ,hidden=False, attrType='float' , defaultValue = 1 , lock = True)
	    mPlug_TwistEndIKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEndIK'%str_segCount ,hidden=False, attrType='float' , defaultValue = 1 , lock = True)
	    mPlug_TwistStartIKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistStartIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
	    mPlug_TwistEndIKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistEndIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
	    
	    #start twist driver
	    l_startDrivers = ["%s.%s"%(i_startControl.getShortName(),str_twistOrientation)]
	    l_startDrivers.append("%s"%mPlug_TwistStartFKResult.p_combinedShortName )
	    l_startDrivers.append("%s"%mPlug_TwistStartIKResult.p_combinedShortName )	    
	    l_fkStartDrivers = []
	    l_ikStartDrivers = []
	    for ii in range(i+1):
		#if i !=  0:
		l_fkStartDrivers.append("%s.%s"%(ml_controlsFK[ii].getShortName(),str_twistOrientation))
	    
	    #end twist driver
	    l_endDrivers = ["%s.%s"%(i_endControl.getShortName(),str_twistOrientation)]	    
	    l_endDrivers.append("%s"%mPlug_TwistEndFKResult.p_combinedShortName )
	    l_endDrivers.append("%s"%mPlug_TwistEndIKResult.p_combinedShortName )		    
	    l_fkEndDrivers = []
	    l_ikEndDrivers = []	    
	    for ii in range(i+2):
		l_fkEndDrivers.append("%s.%s"%(ml_controlsFK[ii].getShortName(),str_twistOrientation))
		"""
		if ml_controlsFK[ii].getAttr('cgmName') == 'ankle':
		    #We need to invert our fk ankle
		    arg = "%s = -%s.%s"%(mPlug_InvertedAnkle.p_combinedShortName,ml_controlsFK[ii].getShortName(),"r%s"%self._jointOrientation[1])
		    NodeF.argsToNodes(arg).doBuild()
		    l_fkEndDrivers.append("%s"%mPlug_InvertedAnkle.p_combinedShortName)
		    #l_fkEndDrivers.append("%s.%s"%(ml_controlsFK[ii].getShortName(),"r%s"%self._jointOrientation[1]))
		else:
		    l_fkEndDrivers.append("%s.%s"%(ml_controlsFK[ii].getShortName(),str_twistOrientation))"""
	    
	    if i == 0:#if seg 0
		"""
		ik -- no elbow 
		start = blendjoint 0
		end = blendjoint 0
		
		ik -- show elbow
		start = blendjoint 0
		end = blendjoint 0
		"""
		#l_ikStartDrivers.append(mPlug_InvertedHipBlendInfluence.p_combinedShortName)
		l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		
		#l_ikEndDrivers.append(mPlug_HandInfluence.p_combinedShortName)		
		l_ikEndDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))		
		
		"""
		l_ikEndDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))		

		l_ikEndDrivers.append(mPlug_midIKResult.p_combinedShortName)
		l_ikEndDrivers.append(mPlug_elbowSpinResult.p_combinedShortName)
		l_ikEndDrivers.append(mPlug_InvertedIKHand.p_combinedShortName)
		l_ikEndDrivers.append(mPlug_elbowAnkleNegate.p_combinedShortName)
		l_ikEndDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		
		l_ikEndDrivers.append(mPlug_InvertedHipBlendInfluence.p_combinedShortName)
		l_ikEndDrivers.append(mPlug_showElbowMidTwist.p_combinedShortName)
		
		l_ikEndDrivers.append(mPlug_TestValue.p_combinedShortName)
		l_ikStartDrivers.append(mPlug_InvertedHipBlend.p_combinedShortName)
		l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		"""
		l_endDrivers.append("%s.%s"%(self._i_rigNull.mainSegmentHandle.getShortName(),str_twistOrientation))
		#l_endDrivers.append(mPlug_midIKResult.p_combinedShortName)
		
		#
	    if i == 1:#if seg 1
		"""
		ik -- no elbow 
		start = blendjoint 0
		end = blendjoint 0
		
		ik -- show elbow
		start = blendjoint 0
		end = blendjoint 0
		"""	
		l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		#l_ikStartDrivers.append(mPlug_midIKResult.p_combinedShortName)
		
		#l_ikStartDrivers.append(mPlug_midIKResult.p_combinedShortName)
		#l_ikStartDrivers.append(mPlug_elbowSpinResult.p_combinedShortName)
		#l_ikStartDrivers.append(mPlug_InvertedIKHand.p_combinedShortName)##	
		#l_ikStartDrivers.append(mPlug_elbowAnkleNegate.p_combinedShortName)##pulls value out when elbow is shown		
		
		###l_ikStartDrivers.append(mPlug_InvertedHipBlendInfluence.p_combinedShortName)
		#l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		#l_ikEndDrivers.append(mPlug_HandInfluence.p_combinedShortName)##Tmp change
		#l_ikEndDrivers.append(mPlug_elbowSpinResult.p_combinedShortName)
		#l_ikEndDrivers.append(mPlug_InvertedIKHand.p_combinedShortName)
		
		#l_ikEndDrivers.append(mPlug_worldIKHandResultNew.p_combinedShortName)
		l_ikEndDrivers.append(mPlug_worldIKEndIn.p_combinedShortName)
		
		#We need to make our world driver for our main IKControl
		i_endLoc = ml_segmentChains[i][-1].doLoc()#Make our loc
		i_endLoc.parent = self._i_constrainNull#Parent it
		mc.parentConstraint(mi_controlIK.mNode,i_endLoc.mNode,maintainOffset = True)#Contrain it
		mPlug_worldIKEndIn.doConnectIn("%s.%s"%(i_endLoc.mNode,str_twistOrientation))#Connect our rotate in
		
		
		#l_ikEndDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		
	    log.info("#>>> %s "%str_segCount+"="*70)
	    log.info("startDrivers %s: %s"%(i,l_startDrivers))
	    str_ArgStartDrivers_Result = "%s = %s"%(mPlug_TwistStartResult.p_combinedShortName," + ".join(l_startDrivers))
	    log.info("start sum arg: '%s'"%(str_ArgStartDrivers_Result))
	    NodeF.argsToNodes(str_ArgStartDrivers_Result).doBuild()		
	    
	    log.info("ikStart Drivers %s: %s"%(i,l_ikStartDrivers))
	    if l_ikStartDrivers:
		str_ArgIKStart_Sum = "%s = %s"%(mPlug_TwistStartIKSum.p_combinedShortName," + ".join(l_ikStartDrivers))
		log.info("start IK sum arg: '%s'"%(str_ArgIKStart_Sum))
		NodeF.argsToNodes(str_ArgIKStart_Sum).doBuild()		
		str_ArgIKStart_Result = "%s = %s * %s"%(mPlug_TwistStartIKResult.p_combinedShortName,mPlug_TwistStartIKSum.p_combinedShortName,mPlug_IKon.p_combinedShortName)
		log.info("start IK result arg: '%s'"%(str_ArgIKStart_Result))
		NodeF.argsToNodes(str_ArgIKStart_Result).doBuild()		
		
	    log.info("fkStart Drivers %s: %s"%(i,l_fkStartDrivers))
	    if l_fkStartDrivers:
		str_ArgFKStart_Sum = "%s = %s"%(mPlug_TwistStartFKSum.p_combinedShortName," + ".join(l_fkStartDrivers))
		log.info("start FK sum arg: '%s'"%(str_ArgFKStart_Sum))
		NodeF.argsToNodes(str_ArgFKStart_Sum).doBuild()		
		str_ArgFKStart_Result = "%s = %s * %s"%(mPlug_TwistStartFKResult.p_combinedShortName,mPlug_TwistStartFKSum.p_combinedShortName,mPlug_FKon.p_combinedShortName)
		log.info("start FK result arg: '%s'"%(str_ArgFKStart_Result))
		NodeF.argsToNodes(str_ArgFKStart_Result).doBuild()		
		
	    #><
	    log.info("#"+"-"*70)
	    log.info("endDrivers %s: %s"%(i,l_endDrivers))	    
	    str_ArgEndDrivers = "%s = %s"%(mPlug_TwistEndResult.p_combinedShortName," + ".join(l_endDrivers))
	    log.info("end sum arg: '%s'"%(str_ArgEndDrivers))	    
	    log.info("ikEnd Drivers %s: %s"%(i,l_ikEndDrivers))
	    NodeF.argsToNodes(str_ArgEndDrivers).doBuild()		
	    
	    if l_ikEndDrivers:
		str_ArgIKEnd_Sum = "%s = %s"%(mPlug_TwistEndIKSum.p_combinedShortName," + ".join(l_ikEndDrivers))
		log.info("end IK sum arg: '%s'"%(str_ArgIKEnd_Sum))
		NodeF.argsToNodes(str_ArgIKEnd_Sum).doBuild()				
		str_ArgIKEnd_Result = "%s = %s * %s"%(mPlug_TwistEndIKResult.p_combinedShortName,mPlug_TwistEndIKSum.p_combinedShortName,mPlug_IKon.p_combinedShortName)
		log.info("end IK result arg: '%s'"%(str_ArgIKEnd_Result))
		NodeF.argsToNodes(str_ArgIKEnd_Result).doBuild()				
	    
	    log.info("fkEnd Drivers %s: %s"%(i,l_fkEndDrivers))
	    if l_fkEndDrivers:
		str_ArgFKEnd_Sum = "%s = %s"%(mPlug_TwistEndFKSum.p_combinedShortName," + ".join(l_fkEndDrivers))
		log.info("end FK sum arg: '%s'"%(str_ArgFKEnd_Sum))
		NodeF.argsToNodes(str_ArgFKEnd_Sum).doBuild()				
		str_ArgFKEnd_Result = "%s = %s * %s"%(mPlug_TwistEndFKResult.p_combinedShortName,mPlug_TwistEndFKSum.p_combinedShortName,mPlug_FKon.p_combinedShortName)
		log.info("end FK result arg: '%s'"%(str_ArgFKEnd_Result))
		NodeF.argsToNodes(str_ArgFKEnd_Result).doBuild()				
	    
	    log.info("#"+"="*70)
	    mPlug_TwistStartResult.doConnectOut("%s.twistStart"%i_curve.mNode)
	    mPlug_TwistEndResult.doConnectOut("%s.twistEnd"%i_curve.mNode)
	    
	    
	    #Reconnect children nodes
	    self._i_rigNull.connectChildrenNodes(ml_segmentChains[i],'segment%s_Joints'%i,"rigNull")#Reconnect to reset. Duplication from createCGMSegment causes issues	

	    #>>>Connect master scale
	    cgmMeta.cgmAttr(i_curve.scaleBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(self._i_masterControl.mNode,'scaleY'))    	    
	    #Push squash and stretch multipliers to head
	    i_buffer = i_curve.scaleBuffer	    
	    for ii,k in enumerate(i_buffer.d_indexToAttr.keys()):
		#attrName = 'finger_%s'%k
		attrName = "seg_%s_%s_mult"%(i,ii)
		cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_settings.mNode,attrName,connectSourceToTarget = True)
		cgmMeta.cgmAttr(mi_settings.mNode,attrName,defaultValue = 1,keyable=True)
		
    except StandardError,error:
	log.error("%s.build_deformation>>> Segment fail!"%(self._strShortName))
	raise StandardError,error	
    
    #TODO	
    self._i_rigNull.connectChildrenNodes(ml_segmentCurves,'segmentCurves',"rigNull")
    
    return True

def build_rig(self):
    """
    Rotate orders
    hips = 3
    """    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("finger.build_deformationRig>>bad self!")
	raise StandardError,error
    
    try:#>>>Get data
	orientation = self._jointOrientation or modules.returnSettingsData('jointOrientation')
	mi_moduleParent = False
	if self._i_module.getMessage('moduleParent'):
	    mi_moduleParent = self._i_module.moduleParent
	    
	mi_controlIK = self._i_rigNull.controlIK
	ml_controlsFK =  self._i_rigNull.controlsFK    
	ml_rigJoints = self._i_rigNull.rigJoints
	ml_blendJoints = self._i_rigNull.blendJoints
	mi_settings = self._i_rigNull.settings
	
	log.info("mi_controlIK: %s"%mi_controlIK.getShortName())
	log.info("ml_controlsFK: %s"%[o.getShortName() for o in ml_controlsFK])
	log.info("mi_settings: %s"%mi_settings.getShortName())
	
	log.info("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
	log.info("ml_blendJoints: %s"%[o.getShortName() for o in ml_blendJoints])
	
	ml_segmentHandleChains = self._get_segmentHandleChains()
	ml_segmentChains = self._get_segmentChains()
	ml_influenceChains = self._get_influenceChains()	
	
	aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1]) 
	
	#Build our contrain to pool
	l_constrainTargetJoints = []
	"""
	for ml_chain in ml_segmentChains:
	    l_constrainTargetJoints.extend([i_jnt.mNode for i_jnt in ml_chain[:-1]])
	l_constrainTargetJoints.extend([i_jnt.mNode for i_jnt in ml_blendJoints[-2:]])
	"""
	if not l_constrainTargetJoints:
	    l_constrainTargetJoints = [i_jnt.mNode for i_jnt in ml_blendJoints]
    except StandardError,error:
	log.error("finger.build_rig>> Gather data fail!")
	raise StandardError,error
    
    #Constrain to pelvis
    if mi_moduleParent:
	mc.parentConstraint(mi_moduleParent.rigNull.skinJoints[-1].mNode,self._i_constrainNull.mNode,maintainOffset = True)
    
    #Dynamic parent groups
    #====================================================================================
    try:#>>>> IK
	ml_fingerDynParents = []
	#Build our dynamic groups
	"""
	1)wrist
	2)fk root
	3)...
	4)world
	"""
	if mi_moduleParent:
	    mi_parentRigNull = mi_moduleParent.rigNull
	    if mi_parentRigNull.getMessage('skinJoints'):
		ml_fingerDynParents.append( mi_parentRigNull.skinJoints[-1])	
		
	ml_fingerDynParents.append( ml_controlsFK[0])	
		
	mi_spine = self._i_module.modulePuppet.getModuleFromDict(moduleType= ['torso','spine'])
	if mi_spine:
	    log.info("spine found: %s"%mi_spine)	    
	    mi_spineRigNull = mi_spine.rigNull
	    ml_fingerDynParents.append( mi_spineRigNull.handleIK )	    
	    ml_fingerDynParents.append( mi_spineRigNull.cog )
	    ml_fingerDynParents.append( mi_spineRigNull.hips )	    
	    
	ml_fingerDynParents.append(self._i_masterControl)
	if mi_controlIK.getMessage('spacePivots'):
	    ml_fingerDynParents.extend(mi_controlIK.spacePivots)	
	log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._strShortName,[i_obj.getShortName() for i_obj in ml_fingerDynParents]))
	
    
	#Add our parents
	i_dynGroup = mi_controlIK.dynParentGroup
	log.info("Dyn group at setup: %s"%i_dynGroup)
	i_dynGroup.dynMode = 0
	
	for o in ml_fingerDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()
	
    except StandardError,error:
	log.error("finger.build_rig>> finger ik dynamic parent setup fail!")
	raise StandardError,error

    #Make some connections
    #====================================================================================
    
    #Parent and constrain joints
    #====================================================================================
    ml_rigJoints[0].parent = self._i_deformNull.mNode#shoulder
    #ml_rigJoints[-1].parent = self._i_deformNull.mNode#wrist

    #For each of our rig joints, find the closest constraint target joint
    log.info("targetJoints: %s"%l_constrainTargetJoints)
    l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
    for i,i_jnt in enumerate(ml_rigJoints):
	#Don't try scale constraints in here, they're not viable
	log.info("Checking: '%s'"%i_jnt.getShortName())
	attachJoint = distance.returnClosestObject(i_jnt.mNode,l_constrainTargetJoints)
	log.info("'%s'<< drives <<'%s'"%(i_jnt.getShortName(),cgmMeta.cgmNode(attachJoint).getShortName()))
	pntConstBuffer = mc.pointConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
	orConstBuffer = mc.orientConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
	mc.connectAttr((attachJoint+'.s'),(i_jnt.mNode+'.s'))
     
    """   
    #Setup hand Scaling
    #====================================================================================
    ml_fkJoints = self._i_rigNull.fkJoints
    ml_ikJoints = self._i_rigNull.ikJoints
    ml_ikPVJoints = self._i_rigNull.ikPVJoints
    ml_ikNoFlipJoints = self._i_rigNull.ikNoFlipJoints
    
    #Ik Scale Object
    mi_controlIK.scalePivotY = 0
    vBuffer = mc.xform(mi_controlIK.mNode,q=True,sp=True,ws=True)	    
    mc.xform(mi_controlIK.mNode,sp=(vBuffer[0],0,vBuffer[2]),ws=True)
    for obj in ml_ikJoints[-3:-1]:
	cgmMeta.cgmAttr(mi_controlIK,'scale').doConnectOut("%s.scale"%obj.mNode)
    for attr in ['x','z']:
	cgmMeta.cgmAttr(mi_controlIK,'sy').doConnectOut("%s.s%s"%(mi_controlIK.mNode,attr))
    
    attributes.doSetLockHideKeyableAttr(mi_controlIK.mNode,lock=True,visible=False,keyable=False,channels=['sz','sx'])    
    mPlug_ikHandScale = cgmMeta.cgmAttr(mi_controlIK,'sy')
    mPlug_ikHandScale.p_nameAlias = 'ikScale'
    mPlug_ikHandScale.p_keyable = True

    #FK Scale
    attributes.doSetLockHideKeyableAttr(ml_controlsFK[-2].mNode,lock=False,visible=True,keyable=True,channels=['s%s'%orientation[0]])
    for attr in orientation[1:]:
	cgmMeta.cgmAttr(ml_controlsFK[-2],'s%s'%orientation[0]).doConnectOut("%s.s%s"%(ml_controlsFK[-2].mNode,attr))
	
    cgmMeta.cgmAttr(ml_controlsFK[-2],'scale').doConnectOut("%s.scale"%ml_controlsFK[-1].mNode)
    cgmMeta.cgmAttr(ml_controlsFK[-2],'scale').doConnectOut("%s.inverseScale"%ml_controlsFK[-1].mNode)
    
    mPlug_fkHandScale = cgmMeta.cgmAttr(ml_controlsFK[-2],'s%s'%orientation[0])
    mPlug_fkHandScale.p_nameAlias = 'fkScale'
    mPlug_fkHandScale.p_keyable = True
    
    #Blend the two
    mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK')
    rUtils.connectBlendJointChain(ml_fkJoints[-2:],ml_ikJoints[-3:-1],ml_blendJoints[-2:],
                                  driver = mPlug_FKIK.p_combinedName,channels=['scale'])    
    """
    #Vis Network, lock and hide
    #====================================================================================
    #Segment handles need to lock
    for ml_chain in ml_segmentHandleChains:
	for i_obj in ml_chain:
	    attributes.doSetLockHideKeyableAttr(i_obj.mNode,lock=True, visible=False, keyable=False, channels=['s%s'%orientation[1],'s%s'%orientation[2]])
    #
    attributes.doSetLockHideKeyableAttr(mi_settings.mNode,lock=True, visible=False, keyable=False)
     
    #Final stuff
    log.error("FIX ARM SKIN JOINTS AND WHAT NOT")
    mc.parentConstraint('l_wrist_jnt', self._i_constrainNull.mNode,maintainOffset = True)
    #mc.parentConstraint(mi_moduleParent.rigNull.skinJoints[-1].mNode, self._i_constrainNull.mNode,maintainOffset = True)
    self._i_rigNull.version = str(__version__)
    return True 


@cgmGeneral.Timer
def build_matchSystem(self):
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("finger.build_deformationRig>>bad self!")
	raise StandardError,error
    
    #Base info
    mi_moduleParent = False
    if self._i_module.getMessage('moduleParent'):
	mi_moduleParent = self._i_module.moduleParent
	
    mi_controlIK = self._i_rigNull.controlIK
    ml_controlsFK =  self._i_rigNull.controlsFK    
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_blendJoints = self._i_rigNull.blendJoints
    mi_settings = self._i_rigNull.settings
    
    ml_fkJoints = self._i_rigNull.fkJoints
    ml_ikJoints = self._i_rigNull.ikJoints
    
    mi_dynSwitch = self._i_dynSwitch
    
    #>>> Get the joints
    if self._partType == 'finger':
	ml_fkToDo = ml_fkJoints[1:]
	ml_ikToDo = ml_ikJoints[1:]
	ml_blendToDo = ml_blendJoints[1:]	
	ml_fkControlsToDo = ml_controlsFK[1:]
    else:#thumb
	ml_fkToDo = ml_fkJoints
	ml_ikToDo = ml_ikJoints
	ml_fkControlsToDo = ml_controlsFK
	ml_blendToDo = ml_blendJoints	
	log.info([i_jnt.getShortName() for i_jnt in ml_fkToDo])

    
    #>>> First IK to FK
    i_ikMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlIK,
                                           dynPrefix = "FKtoIK",
                                           dynMatchTargets=ml_blendJoints[-2])
    i_ikMatch.addPrematchData({'fingerSpin':0})
       
    i_ikMatch.addDynIterTarget(drivenObject =ml_ikToDo[1],#seg 1
                               matchObject = ml_blendToDo[1],
                               drivenAttr= 't%s'%self._jointOrientation[0],
                               matchAttr = 't%s'%self._jointOrientation[0],
                               minValue=0.001,
                               maxValue=30,
                               maxIter=15,
                               driverAttr='lengthUpr')    
    i_ikMatch.addDynIterTarget(drivenObject =ml_ikToDo[2],#seg2
                               matchObject= ml_blendToDo[2],#Make a new one
                               drivenAttr='t%s'%self._jointOrientation[0],
                               matchAttr = 't%s'%self._jointOrientation[0],
                               minValue=0.001,
                               maxValue=30,
                               maxIter=15,
                               driverAttr='lengthLwr') 
    
    i_ikMatch.addDynIterTarget(drivenObject =ml_ikToDo[3],#seg2
                               matchObject= ml_blendToDo[3],#Make a new one
                               drivenAttr='t%s'%self._jointOrientation[0],
                               matchAttr = 't%s'%self._jointOrientation[0],
                               minValue=0.001,
                               maxValue=30,
                               maxIter=15,
                               driverAttr='length') 
    
    i_ikMatch.addDynIterTarget(drivenObject = ml_ikToDo[1],#knee
                               matchTarget = ml_blendToDo[1],#Make a new one
                               minValue=-179,
                               maxValue=179,
                               maxIter=75,
                               driverAttr='fingerSpin') 
    """
    i_ikHandMatch.addDynAttrMatchTarget(dynObjectAttr='ikScale',
                                        matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._jointOrientation[0]],
                                        )"""
    
    
    #>>> FK to IK
    #============================================================================
    i_fk_match1 = cgmRigMeta.cgmDynamicMatch(dynObject = ml_fkControlsToDo[0],
                                              dynPrefix = "IKtoFK",
                                              dynMatchTargets=ml_blendToDo[0])
    i_fk_match1.addDynIterTarget(drivenObject =ml_fkToDo[1],
                                 matchObject = ml_blendToDo[1],
                                 drivenAttr='t%s'%self._jointOrientation[0],
                                 matchAttr = 't%s'%self._jointOrientation[0],
                                 minValue=0.001,
                                 maxValue=30,
                                 maxIter=15,
                                 driverAttr='length')  
    
    i_fk_match2 = cgmRigMeta.cgmDynamicMatch(dynObject = ml_fkControlsToDo[1],
                                             dynPrefix = "IKtoFK",
                                             dynMatchTargets=ml_blendToDo[1])
    i_fk_match2.addDynIterTarget(drivenObject =ml_fkToDo[2],
                                 matchObject = ml_blendToDo[2],                                   
                                 drivenAttr='t%s'%self._jointOrientation[0],
                                 matchAttr = 't%s'%self._jointOrientation[0],
                                 minValue=0.001,
                                 maxValue=30,
                                 maxIter=15,
                                 driverAttr='length')  
    
    i_fk_match3 = cgmRigMeta.cgmDynamicMatch(dynObject = ml_fkControlsToDo[2],
                                             dynPrefix = "IKtoFK",
                                             dynMatchTargets=ml_blendToDo[2])
    i_fk_match3.addDynIterTarget(drivenObject =ml_fkToDo[3],
                                 matchObject = ml_blendToDo[3],                                   
                                 drivenAttr='t%s'%self._jointOrientation[0],
                                 matchAttr = 't%s'%self._jointOrientation[0],
                                 minValue=0.001,
                                 maxValue=30,
                                 maxIter=15,
                                 driverAttr='length')  
    """
    i_fkBallMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[3],
                                              dynPrefix = "IKtoFK",
                                              dynMatchTargets=ml_blendJoints[3])   
      
    i_fkWristMatch.addDynAttrMatchTarget(dynObjectAttr='fkScale',
                                         matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._jointOrientation[0]],
                                         )   
					 """
    #>>> Register the switches
    mi_dynSwitch.addSwitch('snapToFK',[mi_settings.mNode,'blend_FKIK'],
                           0,
                           [i_fk_match1,i_fk_match2,i_fk_match3])
    
    mi_dynSwitch.addSwitch('snapToIK',[mi_settings.mNode,'blend_FKIK'],
                           1,
                           [i_ikMatch])
    
    return True
    
@cgmGeneral.Timer
def __build__(self, buildTo='',*args,**kws): 
    """
    For the finger, build order is skeleton first as we need our mid segment handle joints created to cast from
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
    build_FKIK(self)    
    if buildTo.lower() == 'fkik':return True 
    #build_deformation(self)
    #if buildTo.lower() == 'deformation':return True 
    build_rig(self)
    if buildTo.lower() == 'rig':return True 
    build_matchSystem(self)
    if buildTo.lower() == 'match':return True     
    #build_deformation(self)
    #build_rig(self)    
    
    return True