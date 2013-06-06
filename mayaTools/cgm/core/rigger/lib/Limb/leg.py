"""
------------------------------------------
cgm.core.rigger: Limb.leg
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

leg rig builder
================================================================
"""
__version__ = 0.04292013

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
#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['segmentIK','controlsFK','midIK','settings','foot'],
                 'pivot':['toe','heel','ball','inner','outer']}

def build_shapes(self):
    """
    """ 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("leg.build_rig>>bad self!")
	raise StandardError,error
    
    if self._i_templateNull.handles > 4:
	raise StandardError, "%s.build_shapes>>> Too many handles. don't know how to rig"%(self._strShortName)
    
    if not self.isRigSkeletonized():
	raise StandardError, "%s.build_shapes>>> Must be rig skeletonized to shape"%(self._strShortName)	
    
    """    
    #>>> Get our pivots
    #=============================================================
    for pivot in __d_controlShapes__['pivot']:
	l_buffer = self._i_templateNull.getMessage("pivot_%s"%pivot,False)
	if not l_buffer:
	    raise StandardError, "%s.build_shapes>>> Template null missing pivot: '%s'"%(self._strShortName,pivot)
	log.info("pivot (%s) from template: %s"%(pivot,l_buffer))
	#Duplicate and store the nulls
	i_pivot = cgmMeta.validateObjArg(l_buffer)
	i_trans = i_pivot.doDuplicateTransform(True)
	i_trans.parent = False
	self._i_rigNull.connectChildNode(i_trans,"pivot_%s"%pivot,"rigNull")
	
    #Ball Joint pivot
    i_ballJointPivot = self._i_module.rigNull.skinJoints[-1].doDuplicateTransform(True)#dup ball in place
    i_ballJointPivot.parent = False
    i_ballJointPivot.cgmName = 'ballJoint'
    i_ballJointPivot.addAttr('cgmTypeModifier','pivot')
    i_ballJointPivot.doName()
    self._i_rigNull.connectChildNode(i_ballJointPivot,"pivot_ballJoint","rigNull")
    
    #Ball wiggle pivot
    i_ballWigglePivot = i_ballJointPivot.doDuplicate(True)#dup ball in place
    i_ballWigglePivot.parent = False
    i_ballWigglePivot.cgmName = 'ballWiggle'
    i_ballWigglePivot.doName()
    self._i_rigNull.connectChildNode(i_ballWigglePivot,"pivot_ballWiggle","rigNull")    
	""" 
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
	ml_segmentIKShapes = []
	for i,ml_chain in enumerate(ml_influenceChains):
	    mShapeCast.go(self._i_module,['segmentIK'],targetObjects = [i_jnt.mNode for i_jnt in ml_chain] , storageInstance=self)#This will store controls to a dict called    
	    log.info("%s.build_shapes>>> segmentIK chain %s: %s"%(self._strShortName,i,self._md_controlShapes))
	    ml_segmentIKShapes.extend(self._md_controlShapes['segmentIK'])
	    
	    self._i_rigNull.connectChildrenNodes(self._md_controlShapes['segmentIK'],'shape_segmentIK_%s'%i,"rigNull")		
	
	self._i_rigNull.connectChildrenNodes(ml_segmentIKShapes,'shape_segmentIK',"rigNull")		
	
	#Rest of it
	l_toBuild = ['segmentFK_Loli','settings','midIK','foot']
	mShapeCast.go(self._i_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
	log.info(self._md_controlShapes)
	log.info(self._md_controlPivots)
	self._i_rigNull.connectChildrenNodes(self._md_controlShapes['segmentFK_Loli'],'shape_controlsFK',"rigNull")	
	self._i_rigNull.connectChildNode(self._md_controlShapes['midIK'],'shape_midIK',"rigNull")
	self._i_rigNull.connectChildNode(self._md_controlShapes['settings'],'shape_settings',"rigNull")		
	self._i_rigNull.connectChildNode(self._md_controlShapes['foot'],'shape_foot',"rigNull")
	
    except StandardError,error:
	log.error("build_leg>>Build shapes fail!")
	raise StandardError,error   
    

#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['rigJoints','influenceJoints','fkJoints','ikJoints','blendJoints']   
__d_preferredAngles__ = {'hip':[0,0,-10],'knee':[0,0,10]}#In terms of aim up out for orientation relative values

@r9General.Timer
def build_rigSkeleton(self):
    
    """
    """
    try:#===================================================
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("leg.build_deformationRig>>bad self!")
	raise StandardError,error
    
    #>>> Get our pivots
    #=============================================================
    for pivot in __d_controlShapes__['pivot']:
	l_buffer = self._i_templateNull.getMessage("pivot_%s"%pivot,False)
	if not l_buffer:
	    raise StandardError, "%s.build_shapes>>> Template null missing pivot: '%s'"%(self._strShortName,pivot)
	log.info("pivot (%s) from template: %s"%(pivot,l_buffer))
	#Duplicate and store the nulls
	i_pivot = cgmMeta.validateObjArg(l_buffer)
	i_trans = i_pivot.doDuplicateTransform(True)
	i_trans.parent = False
	self._i_rigNull.connectChildNode(i_trans,"pivot_%s"%pivot,"rigNull")
	
    #Ball Joint pivot
    i_ballJointPivot = self._i_module.rigNull.skinJoints[-1].doDuplicateTransform(True)#dup ball in place
    i_ballJointPivot.parent = False
    i_ballJointPivot.cgmName = 'ballJoint'
    i_ballJointPivot.addAttr('cgmTypeModifier','pivot')
    i_ballJointPivot.doName()
    self._i_rigNull.connectChildNode(i_ballJointPivot,"pivot_ballJoint","rigNull")
    
    #Ball wiggle pivot
    i_ballWigglePivot = i_ballJointPivot.doDuplicate(True)#dup ball in place
    i_ballWigglePivot.parent = False
    i_ballWigglePivot.cgmName = 'ballWiggle'
    i_ballWigglePivot.doName()
    self._i_rigNull.connectChildNode(i_ballWigglePivot,"pivot_ballWiggle","rigNull") 
    
    mi_toePivot = self._i_rigNull.pivot_toe or False 
    if not mi_toePivot:
	raise StandardError,"%s.build_rigSkeleton>>> missing our toe pivot"%self._strShortName
	
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
    d_fkRotateOrders = {'hip':0,'ankle':0}#old hip - 5
    try:#>>>Rotate Orders
	for i_obj in ml_fkJoints:
	    if i_obj.getAttr('cgmName') in d_fkRotateOrders.keys():
		i_obj.rotateOrder = d_fkRotateOrders.get(i_obj.cgmName)   		
	
    except StandardError,error:
	log.error("%s.build_controls>>> Rotate orders fail!"%self._strShortName)		
	raise StandardError,error
    
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
	    if i_new.cgmName in __d_preferredAngles__.keys():
		log.info("preferred angles(%s)>>> %s"%(i_new.cgmName,__d_preferredAngles__.get(i_new.cgmName)))
		for i,v in enumerate(__d_preferredAngles__.get(i_new.cgmName)):	  
		    i_new.__setattr__('preferredAngle%s'%self._jointOrientation[i].upper(),v)
	    if ml_ikJoints:#if we have data, parent to last
		i_new.parent = ml_ikJoints[-1]
	    ml_ikJoints.append(i_new)	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build ik joints fail!")
	raise StandardError,error   
    
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
	
	#Do the toe
	i_toeJoint = ml_ikJoints[-1].doDuplicate()
	Snap.go(i_toeJoint, mi_toePivot.mNode,True,False)
	joints.doCopyJointOrient(ml_ikJoints[-1].mNode,i_toeJoint.mNode)
	i_toeJoint.addAttr('cgmName','toe',attrType='string',lock=True)	
	i_toeJoint.addAttr('cgmTypeModifier','ik',attrType='string',lock=True)
	i_toeJoint.doName()
	
	i_toeJoint.parent = ml_ikJoints[-1].mNode
	ml_ikJoints.append(i_toeJoint)
	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build ik no flip joints fail!")
	raise StandardError,error   
		
    try:#>>Influence chain
	#=====================================================================		
	ml_segmentHandleJoints = []#To use later as well
	for i_ctrl in self._i_templateNull.controlObjects:
	    if i_ctrl.getAttr('cgmName') in ['hip','knee','ankle']:
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
	    jFactory.metaFreezeJointOrientation(i_j.mNode,self._jointOrientation)	
    
    except StandardError,error:
	log.error("build_rigSkeleton>>Build influence joints fail!")
	raise StandardError,error    
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
	    jFactory.metaFreezeJointOrientation([i_jnt.mNode for i_jnt in segmentChain],self._jointOrientation)
	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build segment joints fail!")
	raise StandardError,error   

    try:#>>> Store em all to our instance
	#=====================================================================	
	self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints',"rigNull")#push back to reset
	
	self._i_rigNull.connectChildrenNodes(ml_fkJoints,'fkJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_blendJoints,'blendJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_ikJoints,'ikJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_ikNoFlipJoints,'ikNoFlipJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_ikPVJoints,'ikPVJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'influenceJoints',"rigNull")
	##self._i_rigNull.connectChildrenNodes(ml_anchors,'anchorJoints',"rigNull")
	for i,ml_chain in enumerate(ml_segmentChains):
	    log.info("segment chain: %s"%[i_j.getShortName() for i_j in ml_chain])
	    self._i_rigNull.connectChildrenNodes(ml_chain,'segment%s_Joints'%i,"rigNull")
	    log.info("segment%s_Joints>> %s"%(i,self._i_rigNull.getMessage('segment%s_Joints'%i,False)))
	for i,ml_chain in enumerate(ml_influenceChains):
	    log.info("influence chain: %s"%[i_j.getShortName() for i_j in ml_chain])	    
	    self._i_rigNull.connectChildrenNodes(ml_chain,'segment%s_InfluenceJoints'%i,"rigNull")
	    log.info("segment%s_InfluenceJoints>> %s"%(i,self._i_rigNull.getMessage('segment%s_InfluenceJoints'%i,False)))
	    
	##log.info("anchorJoints>> %s"%self._i_rigNull.getMessage('anchorJoints',False))
	log.info("fkJoints>> %s"%self._i_rigNull.getMessage('fkJoints',False))
	log.info("ikJoints>> %s"%self._i_rigNull.getMessage('ikJoints',False))
	log.info("blendJoints>> %s"%self._i_rigNull.getMessage('blendJoints',False))
	log.info("influenceJoints>> %s"%self._i_rigNull.getMessage('influenceJoints',False))
	log.info("ikNoFlipJoints>> %s"%self._i_rigNull.getMessage('ikNoFlipJoints',False))
	log.info("ikPVJoints>> %s"%self._i_rigNull.getMessage('ikPVJoints',False))
   
    except StandardError,error:
	log.error("build_leg>>StoreJoints fail!")
	raise StandardError,error   

    ml_jointsToConnect = []
    ml_jointsToConnect.extend(ml_rigJoints)    
    ml_jointsToConnect.extend(ml_ikJoints)
    ml_jointsToConnect.extend(ml_blendJoints)    
    ml_jointsToConnect.extend(ml_ikNoFlipJoints)    
    ml_jointsToConnect.extend(ml_ikPVJoints)    
    ml_jointsToConnect.extend(ml_influenceJoints)    
    ##ml_jointsToConnect.extend(ml_anchors)  
    for ml_chain in ml_segmentChains + ml_influenceChains:
	ml_jointsToConnect.extend(ml_chain)

    for i_jnt in ml_jointsToConnect:
	i_jnt.overrideEnabled = 1		
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    
	
    
@r9General.Timer
def build_foot(self):
    """
    """
    try:#===================================================
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("leg.build_foot>>bad self!")
	raise StandardError,error
    
    #>>>Get data
    ml_controlsFK =  self._i_rigNull.controlsFK    
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_blendJoints = self._i_rigNull.blendJoints
    ml_fkJoints = self._i_rigNull.fkJoints
    ml_ikJoints = self._i_rigNull.ikJoints
    ml_ikPVJoints = self._i_rigNull.ikPVJoints
    ml_ikNoFlipJoints = self._i_rigNull.ikNoFlipJoints
    
    mi_settings = self._i_rigNull.settings
    
    mi_pivToe = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_toe'),cgmMeta.cgmObject)
    mi_pivHeel = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_heel'),cgmMeta.cgmObject)
    mi_pivBall = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ball'),cgmMeta.cgmObject)
    mi_pivInner = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_inner'),cgmMeta.cgmObject)
    mi_pivOuter = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_outer'),cgmMeta.cgmObject)      
    mi_pivBallJoint = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ballJoint'),cgmMeta.cgmObject)      
    mi_pivBallWiggle = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ballWiggle'),cgmMeta.cgmObject)      
        
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    outVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[2])  
    
    mi_controlIK = self._i_rigNull.controlIK
    
    #=============================================================    
    #try:#>>>Foot setup
    mi_pivHeel.parent = mi_controlIK.mNode#heel to foot
    mi_pivToe.parent = mi_pivHeel.mNode#toe to heel    
    mi_pivOuter.parent = mi_pivToe.mNode#outer to heel
    mi_pivInner.parent = mi_pivOuter.mNode#inner to outer
    mi_pivBall.parent = mi_pivInner.mNode#pivBall to toe
    mi_pivBallJoint.parent = mi_pivBall.mNode#ballJoint to ball        
    mi_pivBallWiggle.parent = mi_pivInner.mNode
    
    #for each of our pivots, we're going to zero group them
    for pivot in [mi_pivToe,mi_pivHeel,mi_pivBall,mi_pivInner,mi_pivOuter,mi_pivBallJoint,mi_pivBallWiggle]:
	pivot.rotateOrder = 0
	pivot.doZeroGroup()
	log.info("pivot: %s"%pivot.getShortName())    
    
    #Add driving attrs
    mPlug_roll = cgmMeta.cgmAttr(mi_controlIK,'roll',attrType='float',defaultValue = 0,keyable = True)
    mPlug_toeLift = cgmMeta.cgmAttr(mi_controlIK,'toeLift',attrType='float',initialValue = 35, defaultValue = 35,keyable = True)
    mPlug_toeStaighten = cgmMeta.cgmAttr(mi_controlIK,'toeStaighten',attrType='float',initialValue = 65,defaultValue = 70,keyable = True)
    mPlug_toeWiggle= cgmMeta.cgmAttr(mi_controlIK,'toeWiggle',attrType='float',defaultValue = 0,keyable = True)
    mPlug_toeSpin = cgmMeta.cgmAttr(mi_controlIK,'toeSpin',attrType='float',defaultValue = 0,keyable = True)
    mPlug_lean = cgmMeta.cgmAttr(mi_controlIK,'lean',attrType='float',defaultValue = 0,keyable = True)
    mPlug_side = cgmMeta.cgmAttr(mi_controlIK,'bank',attrType='float',defaultValue = 0,keyable = True)
    mPlug_kneeSpin = cgmMeta.cgmAttr(mi_controlIK,'kneeSpin',attrType='float',defaultValue = 0,keyable = True)
    mPlug_stretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
    mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee',attrType='bool',defaultValue = 0,keyable = False)
    mPlug_lengthUpr= cgmMeta.cgmAttr(mi_controlIK,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
    mPlug_lengthLwr = cgmMeta.cgmAttr(mi_controlIK,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
    
    try:#heel setup
	#Add driven attrs
	mPlug_heelClampResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_heel',attrType='float',keyable = False,hidden=True)
	#mPlug_heelResult = cgmMeta.cgmAttr(mi_controlIK,'result_heel',attrType='float',keyable = False,hidden=True)
	
	#Setup the heel roll
	#Clamp
	NodeF.argsToNodes("%s = clamp(%s,0,%s)"%(mPlug_heelClampResult.p_combinedShortName,
	                                         mPlug_roll.p_combinedShortName,
	                                         mPlug_roll.p_combinedShortName)).doBuild()
	#Inversion
	#NodeF.argsToNodes("%s = -%s"%(mPlug_heelResult.p_combinedShortName,mPlug_heelClampResult.p_combinedShortName)).doBuild()
	mPlug_heelClampResult.doConnectOut("%s.r%s"%(mi_pivHeel.mNode,self._jointOrientation[2].lower()))
    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> heel setup fail: %s"%error    
    
    try:#ball setup
	"""
	Schleifer's
	ball_loc.rx = (linstep(0,$toeLift, $roll) * (1-(linstep( $toeLift, $toeStraight, $roll))) * $roll;
			ballToeLiftRoll        md   ( pma   toeToeStraightRoll                    md  
				1               4       3             2                            5
	"""
	mPlug_ballToeLiftRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_ballToeLiftRoll',attrType='float',keyable = False,hidden=True)
	mPlug_toeStraightRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_toeStraightRoll',attrType='float',keyable = False,hidden=True)
	mPlug_oneMinusToeResultResult = cgmMeta.cgmAttr(mi_controlIK,'result_pma_one_minus_toeStraitRollRange',attrType='float',keyable = False,hidden=True)
	mPlug_ball_x_toeResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_roll_x_toeResult',attrType='float',keyable = False,hidden=True)
	mPlug_all_x_rollResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_all_x_rollResult',attrType='float',keyable = False,hidden=True)
	
	arg1 = "%s = setRange(0,1,0,%s,%s)"%(mPlug_ballToeLiftRollResult.p_combinedShortName,
	                                     mPlug_toeLift.p_combinedShortName,
	                                     mPlug_roll.p_combinedShortName)
	arg2 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeStraightRollResult.p_combinedShortName,
	                                      mPlug_toeLift.p_combinedShortName,
	                                      mPlug_toeStaighten.p_combinedShortName,
	                                      mPlug_roll.p_combinedShortName)
	arg3 = "%s = 1 - %s"%(mPlug_oneMinusToeResultResult.p_combinedShortName,
	                      mPlug_toeStraightRollResult.p_combinedShortName)
	
	arg4 = "%s = %s * %s"%(mPlug_ball_x_toeResult.p_combinedShortName,
	                       mPlug_oneMinusToeResultResult.p_combinedShortName,
	                       mPlug_ballToeLiftRollResult.p_combinedShortName)
	
	arg5 = "%s = %s * %s"%(mPlug_all_x_rollResult.p_combinedShortName,
	                       mPlug_ball_x_toeResult.p_combinedShortName,
	                       mPlug_roll.p_combinedShortName)
	
	for arg in [arg1,arg2,arg3,arg4,arg5]:
	    NodeF.argsToNodes(arg).doBuild()
	    
	mPlug_all_x_rollResult.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,self._jointOrientation[2].lower()))
	
    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> ball setup fail: %s"%error   
	
    try:#toe setup    
	"""
	Schleifer's
	toe_loc.rotateX = linstep($toeLift, $toeStraight,$roll) * $roll;
			      setRange                           md
				 1                                2
	"""
	mPlug_toeRangeResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_toeLiftStraightRoll',attrType='float',keyable = False,hidden=True)
	mPlug_toe_x_rollResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_toeRange_x_roll',attrType='float',keyable = False,hidden=True)
	
	arg1 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeRangeResult.p_combinedShortName,
	                                     mPlug_toeLift.p_combinedShortName,
	                                     mPlug_toeStaighten.p_combinedShortName,                                         
	                                     mPlug_roll.p_combinedShortName)
	arg2 = "%s = %s * %s"%(mPlug_toe_x_rollResult.p_combinedShortName,
	                                      mPlug_toeRangeResult.p_combinedShortName,
	                                      mPlug_roll.p_combinedShortName)
	for arg in [arg1,arg2]:
	    NodeF.argsToNodes(arg).doBuild()    
	
	mPlug_toe_x_rollResult.doConnectOut("%s.r%s"%(mi_pivToe.mNode,self._jointOrientation[2].lower()))
    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> toe setup fail: %s"%error   
    
    try:#bank setup 
	"""
	Schleifer's
	outside_loc.rotateZ = min($side,0);
	clamp1
	inside_loc.rotateZ = max(0,$side);
	clamp2
	"""    
	mPlug_outerResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_outerBank',attrType='float',keyable = False,hidden=True)
	mPlug_innerResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_innerBank',attrType='float',keyable = False,hidden=True)
	
	arg1 = "%s = clamp(%s,0,%s)"%(mPlug_outerResult.p_combinedShortName,
	                              mPlug_side.p_combinedShortName,                                      
	                              mPlug_side.p_combinedShortName)
	arg2 = "%s = clamp(0,%s,%s)"%(mPlug_innerResult.p_combinedShortName,
	                              mPlug_side.p_combinedShortName,                                      
	                              mPlug_side.p_combinedShortName)
	for arg in [arg1,arg2]:
	    NodeF.argsToNodes(arg).doBuild()   
	  
	mPlug_outerResult.doConnectOut("%s.r%s"%(mi_pivOuter.mNode,self._jointOrientation[0].lower()))
	mPlug_innerResult.doConnectOut("%s.r%s"%(mi_pivInner.mNode,self._jointOrientation[0].lower()))

    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> bank setup fail: %s"%error       
    
    try:#lean setup 
	"""
	Schleifer's
	ball_loc.rotateZ = $lean;
	"""    
	mPlug_lean.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,self._jointOrientation[0].lower()))
	

    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> lean setup fail: %s"%error  
    
    try:#toe spin setup 
	"""
	Schleifer's
	toe_loc.rotateY = $spin;
	"""    
	mPlug_toeSpin.doConnectOut("%s.r%s"%(mi_pivToe.mNode,self._jointOrientation[1].lower()))

    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> toe spin setup fail: %s"%error 
    
    try:#toe wiggle setup 
	"""
	Schleifer's
	toeWiggle_loc.rx = $wiggle;
	"""    
	mPlug_toeWiggle.doConnectOut("%s.r%s"%(mi_pivBallWiggle.mNode,self._jointOrientation[2].lower()))

    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> toe wiggle setup fail: %s"%error 
    
    
    
    
@r9General.Timer
def build_FKIK(self):
    """
    """
    try:#===================================================
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("leg.build_FKIK>>bad self!")
	raise StandardError,error
    
    #>>>Get data
    ml_controlsFK =  self._i_rigNull.controlsFK   
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_blendJoints = self._i_rigNull.blendJoints
    ml_fkJoints = self._i_rigNull.fkJoints
    ml_ikJoints = self._i_rigNull.ikJoints
    ml_ikPVJoints = self._i_rigNull.ikPVJoints
    ml_ikNoFlipJoints = self._i_rigNull.ikNoFlipJoints
    
    mi_settings = self._i_rigNull.settings
    
    mi_pivToe = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_toe'),cgmMeta.cgmObject)
    mi_pivHeel = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_heel'),cgmMeta.cgmObject)
    mi_pivBall = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ball'),cgmMeta.cgmObject)
    mi_pivInner = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_inner'),cgmMeta.cgmObject)
    mi_pivOuter = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_outer'),cgmMeta.cgmObject)      
    mi_pivBallJoint = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ballJoint'),cgmMeta.cgmObject)      
    mi_pivBallWiggle = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ballWiggle'),cgmMeta.cgmObject)      
        
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    outVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[2])
    
    mi_controlIK = self._i_rigNull.controlIK
    mi_controlMidIK = self._i_rigNull.midIK
    mPlug_lockMid = cgmMeta.cgmAttr(mi_controlMidIK,'lockMid',attrType='float',defaultValue = 0,keyable = True,minValue=0,maxValue=1.0)
    
    for chain in [ml_ikJoints,ml_blendJoints,ml_ikNoFlipJoints,ml_ikPVJoints]:
	chain[0].parent = self._i_constrainNull.mNode
	
    #for more stable ik, we're gonna lock off the lower channels degrees of freedom
    for chain in [ml_ikNoFlipJoints,ml_ikPVJoints]:
	for axis in self._jointOrientation[:2]:
	    log.info(axis)
	    for i_j in chain[1:]:
		attributes.doSetAttr(i_j.mNode,"jointType%s"%axis.upper(),0)
    
    #=============================================================    
    try:#>>>FK Length connector
	for i,i_jnt in enumerate(ml_fkJoints[:-2]):
	    rUtils.addJointLengthAttr(i_jnt,orientation=self._jointOrientation)
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> fk length connect error: %s"%(self._strShortName,error)
    
    #=============================================================    
    try:#>>>IK No Flip Chain
	mPlug_globalScale = cgmMeta.cgmAttr(self._i_masterControl.mNode,'scaleY')    
	i_tmpLoc = ml_ikNoFlipJoints[-1].doLoc()
	mc.move(outVector[0]*100,outVector[1]*100,outVector[2]*100,i_tmpLoc.mNode,r=True, rpr = True, os = True, wd = True)	
	
	#Create no flip leg IK
	d_ankleNoFlipReturn = rUtils.IKHandle_create(ml_ikNoFlipJoints[0].mNode,ml_ikNoFlipJoints[-1].mNode, nameSuffix = 'noFlip',
	                                             rpHandle=True,controlObject=mi_controlIK,addLengthMulti=True,
	                                             globalScaleAttr=mPlug_globalScale.p_combinedName, stretch='translate',moduleInstance=self._i_module)
	mi_ankleIKHandleNF = d_ankleNoFlipReturn['mi_handle']
	ml_distHandlesNF = d_ankleNoFlipReturn['ml_distHandles']
	mi_rpHandleNF = d_ankleNoFlipReturn['mi_rpHandle']
	mPlug_lockMid = d_ankleNoFlipReturn['mPlug_lockMid']
	
	#No Flip RP handle
	Snap.go(mi_rpHandleNF,i_tmpLoc.mNode,True)#Snape to foot control, then move it out...
	i_tmpLoc.delete()
	
	mi_rpHandleNF.doCopyNameTagsFromObject(self._i_module.mNode, ignore = ['cgmName','cgmType'])
	mi_rpHandleNF.addAttr('cgmName','kneePoleVector',attrType = 'string')
	mi_rpHandleNF.addAttr('cgmTypeModifier','noFlip')
	mi_rpHandleNF.doName()
	
	#Knee spin
	#=========================================================================================
	#Make a spin group
	i_spinGroup = mi_controlIK.doDuplicateTransform()
	i_spinGroup.doCopyNameTagsFromObject(self._i_module.mNode, ignore = ['cgmName','cgmType'])	
	i_spinGroup.addAttr('cgmName','noFlipKneeSpin')
	i_spinGroup.doName()
	
	i_spinGroup.parent = mi_pivBall.mNode
	i_spinGroup.doZeroGroup()
	mi_rpHandleNF.parent = i_spinGroup.mNode
		
	#Setup arg
	mPlug_kneeSpin = cgmMeta.cgmAttr(mi_controlIK,'kneeSpin')
	mPlug_kneeSpin.doConnectOut("%s.rotateY"%i_spinGroup.mNode)
	
	#>>>Parent IK handles
	mi_ankleIKHandleNF.parent = mi_pivBallJoint.mNode#ankleIK to ball		
	ml_distHandlesNF[-1].parent = mi_pivBallJoint.mNode#ankle distance handle to ball	
	ml_distHandlesNF[0].parent = self._i_constrainNull.mNode#hip distance handle to deform group
	ml_distHandlesNF[1].parent = mi_controlMidIK.mNode#knee distance handle to midIK
	
	#>>> Fix our ik_handle twist at the end of all of the parenting
	rUtils.IKHandle_fixTwist(mi_ankleIKHandleNF)#Fix the twist
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> IK No Flip error: %s"%(self._strShortName,error)
    
    #=============================================================    
    try:#>>>IK PV Chain
	#Create no flip leg IK
	#We're gonna use the no flip stuff for the most part
	d_anklePVReturn = rUtils.IKHandle_create(ml_ikPVJoints[0].mNode,ml_ikPVJoints[-1].mNode,nameSuffix = 'PV',
	                                         rpHandle=ml_distHandlesNF[1],controlObject=mi_controlIK,
	                                         moduleInstance=self._i_module)

	mi_ankleIKHandlePV = d_anklePVReturn['mi_handle']
	mi_rpHandlePV = d_anklePVReturn['mi_rpHandle']
	
	#Stretch -- grab our translate aims from
	for i,i_j in enumerate(ml_ikPVJoints[1:]):
	    driverAttr = attributes.returnDriverAttribute("%s.t%s"%(ml_ikNoFlipJoints[i+1].mNode,self._jointOrientation[0].lower()))
	    d_driverPlug = cgmMeta.validateAttrArg(driverAttr,noneValid=False)#Validdate
	    d_driverPlug['mi_plug'].doConnectOut("%s.t%s"%(i_j.mNode,self._jointOrientation[0].lower()))#Connect the plug to our joint
	
	#RP handle	
	mi_rpHandlePV.doCopyNameTagsFromObject(self._i_module.mNode, ignore = ['cgmName','cgmType'])
	mi_rpHandlePV.addAttr('cgmName','kneePoleVector',attrType = 'string')
	mi_rpHandlePV.doName()
	
	#>>>Parent IK handles
	mi_ankleIKHandlePV.parent = mi_pivBallJoint.mNode#ankleIK to ball	
	
	#Mid fix
	#=========================================================================================			
	mc.move(0,0,25,mi_controlMidIK.mNode,r=True, rpr = True, ws = True, wd = True)#move out the midControl to fix the twist from
	
	#>>> Fix our ik_handle twist at the end of all of the parenting
	rUtils.IKHandle_fixTwist(mi_ankleIKHandlePV)#Fix the twist
	
	#Register our snap to point before we move it back
	i_ikMidMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlMidIK,
	                                          dynPrefix = "FKtoIK",
	                                          dynMatchTargets=ml_blendJoints[1]) 	
	#>>> Reset the translations
	mi_controlMidIK.tx = 0
	mi_controlMidIK.ty = 0
	mi_controlMidIK.tz = 0
	
	#Move the lock mid and add the toggle so it only works with show knee on
	#=========================================================================================				
	mPlug_lockMidResult = cgmMeta.cgmAttr(mi_controlMidIK,'result_lockMidInfluence',attrType='float',keyable = False,hidden=True)
	mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee')
	drivenPlugs = mPlug_lockMid.getDriven()
	arg = "%s = %s * %s"%(mPlug_lockMidResult.p_combinedShortName,
	                      mPlug_showKnee.p_combinedShortName,
	                      mPlug_lockMid.p_combinedShortName)
	NodeF.argsToNodes(arg).doBuild()
	for plug in drivenPlugs:#Connect them back
	    mPlug_lockMidResult.doConnectOut(plug)
	    
	mPlug_lockMid.doTransferTo(mi_controlMidIK.mNode)#move the lock mid	
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> IK No Flip error: %s"%(self._strShortName,error)
    
    #=============================================================    
    try:#>>>Foot chains and connection
	#Create foot IK
	d_ballReturn = rUtils.IKHandle_create(ml_ikJoints[2].mNode,ml_ikJoints[3].mNode,solverType='ikSCsolver',
	                                      baseName=ml_ikJoints[3].cgmName,moduleInstance=self._i_module)
	mi_ballIKHandle = d_ballReturn['mi_handle']
	
	#Create toe IK
	d_toeReturn = rUtils.IKHandle_create(ml_ikJoints[3].mNode,ml_ikJoints[4].mNode,solverType='ikSCsolver',
	                                     baseName=ml_ikJoints[4].cgmName,moduleInstance=self._i_module)
	mi_toeIKHandle = d_toeReturn['mi_handle']
    
	#return {'mi_handle':i_ik_handle,'mi_effector':i_ik_effector,'mi_solver':i_ikSolver}
	
	mi_ballIKHandle.parent = mi_pivInner.mNode#ballIK to toe
	mi_toeIKHandle.parent = mi_pivBallWiggle.mNode#toeIK to wiggle
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> IK No Flip error: %s"%(self._strShortName,error)
    
    #=============================================================    
    try:#>>>Connect Blend Chains and connections
	#Connect Vis of knee
	#=========================================================================================
	mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee',attrType='bool',defaultValue = 0,keyable = True)	
	mPlug_showKnee.doConnectOut("%s.visibility"%mi_controlMidIK.mNode)	
	
	#>>> Main blend
	mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',lock=False,keyable=True)
	
	rUtils.connectBlendJointChain(ml_fkJoints,ml_ikJoints,ml_blendJoints,
	                              driver = mPlug_FKIK.p_combinedName,channels=['translate','rotate'])
	rUtils.connectBlendJointChain(ml_ikNoFlipJoints,ml_ikPVJoints,ml_ikJoints[:3],
	                              driver = mPlug_showKnee.p_combinedName,channels=['translate','rotate'])	
	
	#>>> Settings - constrain
	mc.parentConstraint(ml_blendJoints[2].mNode, mi_settings.masterGroup.mNode, maintainOffset = True)
	
	#>>> Setup a vis blend result
	mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=False)	
	mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=False)	
	
	NodeF.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,mPlug_IKon.p_combinedName,mPlug_FKon.p_combinedName)
	
	mPlug_FKon.doConnectOut("%s.visibility"%self._i_constrainNull.controlsFK.mNode)
	mPlug_IKon.doConnectOut("%s.visibility"%self._i_constrainNull.controlsIK.mNode)
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> blend connect error: %s"%(self._strShortName,error)
    
    
def build_controls(self):
    """
    """    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("leg.build_rig>>bad self!")
	raise StandardError,error
    
    if not self.isShaped():
	raise StandardError,"%s.build_controls>>> needs shapes to build controls"%self._strShortName
    if not self.isRigSkeletonized():
	raise StandardError,"%s.build_controls>>> needs shapes to build controls"%self._strShortName
    """
    __d_controlShapes__ = {'shape':['controlsFK','midIK','settings','foot'],
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
	 
    mi_midIK = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_midIK'),cgmMeta.cgmObject)
    mi_settings= cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_settings'),cgmMeta.cgmObject)
    mi_foot= cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_foot'),cgmMeta.cgmObject)
    mi_pivToe = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_toe'),cgmMeta.cgmObject)
    mi_pivHeel = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_heel'),cgmMeta.cgmObject)
    mi_pivBall = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ball'),cgmMeta.cgmObject)
    mi_pivInner = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_inner'),cgmMeta.cgmObject)
    mi_pivOuter = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_outer'),cgmMeta.cgmObject)
    ml_fkJoints = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('fkJoints'),cgmMeta.cgmObject)
    
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
	    d_buffer = mControlFactory.registerControl(i_obj,shapeParentTo=ml_fkJoints[i],
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
	i_IKEnd = mi_foot
	i_IKEnd.parent = False
	d_buffer = mControlFactory.registerControl(i_IKEnd,
	                                           typeModifier='ik',addSpacePivots = 1, addDynParentGroup = True, addConstraintGroup=True,
	                                           makeAimable = True,setRotateOrder=3)
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
	raise StandardError,error   
        
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
	raise StandardError,error
    #==================================================================    
    try:#>>>> Add all of our Attrs
	#Add driving attrs
	mPlug_roll = cgmMeta.cgmAttr(i_IKEnd,'roll',attrType='float',defaultValue = 0,keyable = True)
	mPlug_toeLift = cgmMeta.cgmAttr(i_IKEnd,'toeLift',attrType='float',initialValue = 35, defaultValue = 35,keyable = True)
	mPlug_toeStaighten = cgmMeta.cgmAttr(i_IKEnd,'toeStaighten',attrType='float',initialValue = 65,defaultValue = 70,keyable = True)
	mPlug_toeWiggle= cgmMeta.cgmAttr(i_IKEnd,'toeWiggle',attrType='float',defaultValue = 0,keyable = True)
	mPlug_toeSpin = cgmMeta.cgmAttr(i_IKEnd,'toeSpin',attrType='float',defaultValue = 0,keyable = True)
	mPlug_lean = cgmMeta.cgmAttr(i_IKEnd,'lean',attrType='float',defaultValue = 0,keyable = True)
	mPlug_side = cgmMeta.cgmAttr(i_IKEnd,'bank',attrType='float',defaultValue = 0,keyable = True)
	mPlug_kneeSpin = cgmMeta.cgmAttr(i_IKEnd,'kneeSpin',attrType='float',defaultValue = 0,keyable = True)
	mPlug_stretch = cgmMeta.cgmAttr(i_IKEnd,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
	mPlug_showKnee = cgmMeta.cgmAttr(i_IKEnd,'showKnee',attrType='bool',defaultValue = 0,keyable = False)
	mPlug_lengthUpr= cgmMeta.cgmAttr(i_IKEnd,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
	mPlug_lengthLwr = cgmMeta.cgmAttr(i_IKEnd,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)	
	
	mPlug_lockMid = cgmMeta.cgmAttr(i_IKmid,'lockMid',attrType='float',defaultValue = 0,keyable = True,minValue=0,maxValue=1.0)
	
    except StandardError,error:
	log.error("%s.build_controls>>> Add Control Attrs Fail!"%self._strShortName)	
	
    #Connect all controls
    self._i_rigNull.connectChildrenNodes(l_controlsAll,'controlsAll')
    
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
	log.error("leg.build_deformationRig>>bad self!")
	raise StandardError,error
    
    #==========================================================================
    try:#Info gathering
	#segmentHandles_%s
	#Get our segment controls
	ml_segmentHandleChains = self.getSegmentHandleChains()

	#Get our segment joints
	ml_segmentChains = self.getSegmentChains()
	if len(ml_segmentChains)>2:
	    raise StandardError, "%s.build_deformation>>> Too many segment chains, not a regular leg."%(self._strShortName)
	
	#>>>Influence Joints
	ml_influenceChains = self.getInfluenceChains()
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
    ###mPlug_InvertedKneeSpin = cgmMeta.cgmAttr(mi_settings,"result_invertKneeSpin" , attrType='float' , lock = True)
    mPlug_KneeSpinResult = cgmMeta.cgmAttr(mi_settings,"result_kneeSpinInfluence" , attrType='float' , lock = True)
    ###mPlug_KneeAnkleNegate = cgmMeta.cgmAttr(mi_settings,"result_kneeAnkleNegate" , attrType='float' , lock = True)
    ###mPlug_InvertedHipBlendInfluence= cgmMeta.cgmAttr(mi_settings,"result_invertHipBlendInfluence" , attrType='float' , lock = True)    
    mPlug_MidIKSpaceFootInfluence = cgmMeta.cgmAttr(mi_settings,"result_midIKSpaceFootInfluence" , attrType='float' , lock = True)	    
    mPlug_FootInfluence = cgmMeta.cgmAttr(mi_settings,"result_footInfluence" , attrType='float' , lock = True)	    
    mPlug_InvertedIKFoot = cgmMeta.cgmAttr(mi_settings,"result_invertIKFoot" , attrType='float' , lock = True)	    
    ##mPlug_worldIKFootResult = cgmMeta.cgmAttr(mi_settings,"result_worldIKFoot" , attrType='float' , lock = True)	    
    
    mPlug_ShowKneeMidTwist = cgmMeta.cgmAttr(mi_settings,"result_ShowKneeMidTwist" , attrType='float' , lock = True)
    
    #Existing
    mPlug_kneeSpin = cgmMeta.cgmAttr(mi_controlIK,'kneeSpin',attrType='float')
    mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee',attrType='bool')
    
    #Invert the knee spin
    """
    NodeF.argsToNodes("%s = -%s"%(mPlug_InvertedKneeSpin.p_combinedShortName,
                                  mPlug_kneeSpin.p_combinedShortName)).doBuild() """ 
    #invert the foot
    NodeF.argsToNodes("%s = -%s"%(mPlug_InvertedIKFoot.p_combinedShortName,
                                  "%s.ry"%(mi_controlIK.getShortName()))).doBuild()
    #invert the blend hip
    """
    NodeF.argsToNodes("%s = -%s.%s"%(mPlug_InvertedHipBlend.p_combinedShortName,
                                     ml_blendJoints[0].getShortName(),
                                     str_twistOrientation)).doBuild()"""
    
    #Value to pull from when the knee is being shown
    """
    NodeF.argsToNodes("%s = %s * %s"%(mPlug_KneeAnkleNegate.p_combinedShortName,
                                      mPlug_showKnee.p_combinedShortName,
                                      "%s.ry"%(mi_controlIK.getShortName()))).doBuild()  """
    
    #Show knee * blend joint 0's twist
    NodeF.argsToNodes("%s = %s * %s.%s"%(mPlug_ShowKneeMidTwist.p_combinedShortName,
                                         mPlug_showKnee.p_combinedShortName,
                                         ml_blendJoints[0].getShortName(),
                                         str_twistOrientation)).doBuild()  
    
    #Knee spin result -- if show knee, is 0, use it. Adds the knee spin in if the
    NodeF.argsToNodes("%s = if %s == 0: %s else 0 "%(mPlug_KneeSpinResult.p_combinedShortName,
                                                     mPlug_showKnee.p_combinedShortName,
                                                     mPlug_kneeSpin.p_combinedShortName)).doBuild()
    
    #Foot influence based on knee space
    """
    If the knee is visible AND knee in foot space, use blendJoint, else, use inverted foot
    If the knee is not visible, use inverted foot
    mPlug_FootInfluence
    mPlug_MidIKSpaceFootInfluence
    mi_controlMidIK space
    mPlug_InvertedIKFoot
    mPlug_MidIKSpace
    mPlug_worldIKFootResult
    """
    """
    mPlug_Blend0 = cgmMeta.cgmAttr(ml_blendJoints[0],str_twistOrientation)
    mPlug_KneeSpaceHolder = cgmMeta.cgmAttr(mi_settings,"kneeSpace_in" , attrType='int' , lock = True)    
    NodeF.argsToNodes("%s = if %s == 1:%s else %s"%(mPlug_FootInfluence.p_combinedShortName,#result
                                                    mPlug_showKnee.p_combinedShortName,#driver
                                                    mPlug_MidIKSpaceFootInfluence.p_combinedShortName,#option 1
                                                    mPlug_InvertedIKFoot.p_combinedShortName)).doBuild()#option 2
    
    NodeF.argsToNodes("%s = if %s == 0:%s else %s"%(mPlug_MidIKSpaceFootInfluence.p_combinedShortName,#result
                                                    mPlug_KneeSpaceHolder.p_combinedShortName,#driver
                                                    mPlug_InvertedIKFoot.p_combinedShortName,#option 1
                                                    mPlug_InvertedIKFoot.p_combinedShortName)).doBuild()#option 2
    
    NodeF.argsToNodes("%s = %s + %s"%(mPlug_worldIKFootResult.p_combinedShortName,#result
                                      mPlug_InvertedIKFoot.p_combinedShortName,#option 1
                                      mPlug_Blend0.p_combinedShortName)).doBuild()#option 2
    
    
    #Mid IK
    mPlug_midIKResult = cgmMeta.cgmAttr(mi_settings,'result_midIK',attrType='float',defaultValue = 0,keyable = True,hidden=False, lock = True)
    NodeF.argsToNodes("%s = %s * %s"%(mPlug_midIKResult.p_combinedShortName,
                                      mPlug_showKnee.p_combinedShortName,
                                      "%s.%s"%(mi_controlMidIK.getShortName(),str_twistOrientation))).doBuild()        
    """
    #New method for getting proper foot twist
    """
    The gist is that we create a loc of the last segment joint of seg 1, we orient constrain that to the ik control
    This is our base value for the foot twist. The problem is that an ik chain can flip at 180 cause issues on our second segment.
    
    IF blend0>0 : use +baseValue + blend
    else: use -baseValue + blend

    """ 
    mPlug_Blend0 = cgmMeta.cgmAttr(ml_blendJoints[0],str_twistOrientation)
    mPlug_ConstrainGroupTwist = cgmMeta.cgmAttr(self._i_constrainNull,str_twistOrientation)
    
    mPlug_KneeSpaceHolder = cgmMeta.cgmAttr(mi_settings,"kneeSpace_in" , attrType='int' , lock = True) #REMOVE THIS  
    
    mPlug_worldIKFootResultNew = cgmMeta.cgmAttr(mi_settings,"result_worldIKFoot" , attrType='float' , lock = True)	    
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
    
    NodeF.argsToNodes("%s = %s + %s"%(mPlug_worldIKFootResultNew.p_combinedShortName,#result
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
	    ik result = ik.y + knee twist?
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
		ik -- no knee 
		start = blendjoint 0
		end = blendjoint 0
		
		ik -- show knee
		start = blendjoint 0
		end = blendjoint 0
		"""
		#l_ikStartDrivers.append(mPlug_InvertedHipBlendInfluence.p_combinedShortName)
		l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		
		#l_ikEndDrivers.append(mPlug_FootInfluence.p_combinedShortName)		
		l_ikEndDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))		
		
		"""
		l_ikEndDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))		

		l_ikEndDrivers.append(mPlug_midIKResult.p_combinedShortName)
		l_ikEndDrivers.append(mPlug_KneeSpinResult.p_combinedShortName)
		l_ikEndDrivers.append(mPlug_InvertedIKFoot.p_combinedShortName)
		l_ikEndDrivers.append(mPlug_KneeAnkleNegate.p_combinedShortName)
		l_ikEndDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		
		l_ikEndDrivers.append(mPlug_InvertedHipBlendInfluence.p_combinedShortName)
		l_ikEndDrivers.append(mPlug_ShowKneeMidTwist.p_combinedShortName)
		
		l_ikEndDrivers.append(mPlug_TestValue.p_combinedShortName)
		l_ikStartDrivers.append(mPlug_InvertedHipBlend.p_combinedShortName)
		l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		"""
		l_endDrivers.append("%s.%s"%(self._i_rigNull.mainSegmentHandle.getShortName(),str_twistOrientation))
		#l_endDrivers.append(mPlug_midIKResult.p_combinedShortName)
		
		#
	    if i == 1:#if seg 1
		"""
		ik -- no knee 
		start = blendjoint 0
		end = blendjoint 0
		
		ik -- show knee
		start = blendjoint 0
		end = blendjoint 0
		"""	
		l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		#l_ikStartDrivers.append(mPlug_midIKResult.p_combinedShortName)
		
		#l_ikStartDrivers.append(mPlug_midIKResult.p_combinedShortName)
		#l_ikStartDrivers.append(mPlug_KneeSpinResult.p_combinedShortName)
		#l_ikStartDrivers.append(mPlug_InvertedIKFoot.p_combinedShortName)##	
		#l_ikStartDrivers.append(mPlug_KneeAnkleNegate.p_combinedShortName)##pulls value out when knee is shown		
		
		###l_ikStartDrivers.append(mPlug_InvertedHipBlendInfluence.p_combinedShortName)
		#l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		#l_ikEndDrivers.append(mPlug_FootInfluence.p_combinedShortName)##Tmp change
		#l_ikEndDrivers.append(mPlug_KneeSpinResult.p_combinedShortName)
		#l_ikEndDrivers.append(mPlug_InvertedIKFoot.p_combinedShortName)
		
		#l_ikEndDrivers.append(mPlug_worldIKFootResultNew.p_combinedShortName)
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
		#attrName = 'leg_%s'%k
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
	log.error("leg.build_deformationRig>>bad self!")
	raise StandardError,error
    
    try:#>>>Get data
	orientation = self._jointOrientation or modules.returnSettingsData('jointOrientation')
	mi_moduleParent = False
	if self._i_module.getMessage('moduleParent'):
	    mi_moduleParent = self._i_module.moduleParent
	    
	mi_controlIK = self._i_rigNull.controlIK
	mi_controlMidIK = self._i_rigNull.midIK 
	ml_controlsFK =  self._i_rigNull.controlsFK    
	ml_rigJoints = self._i_rigNull.rigJoints
	ml_blendJoints = self._i_rigNull.blendJoints
	mi_settings = self._i_rigNull.settings
    
	mi_controlIK = self._i_rigNull.controlIK
	mi_controlMidIK = self._i_rigNull.midIK
	
	log.info("mi_controlIK: %s"%mi_controlIK.mNode)
	log.info("mi_controlMidIK: %s"%mi_controlMidIK.mNode)	
	log.info("ml_controlsFK: %s"%[o.getShortName() for o in ml_controlsFK])
	log.info("mi_settings: %s"%mi_settings.mNode)
	
	log.info("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
	log.info("ml_blendJoints: %s"%[o.getShortName() for o in ml_blendJoints])
	
	ml_segmentHandleChains = self.getSegmentHandleChains()
	ml_segmentChains = self.getSegmentChains()
	ml_influenceChains = self.getInfluenceChains()	
	
	aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1]) 
	
	#Build our contrain to pool
	l_constrainTargetJoints = []
	for ml_chain in ml_segmentChains:
	    l_constrainTargetJoints.extend([i_jnt.mNode for i_jnt in ml_chain[:-1]])
	l_constrainTargetJoints.extend([i_jnt.mNode for i_jnt in ml_blendJoints[-2:]])
	
    except StandardError,error:
	log.error("leg.build_rig>> Gather data fail!")
	raise StandardError,error
    
    #Constrain to pelvis
    if mi_moduleParent:
	mc.parentConstraint(mi_moduleParent.rigNull.skinJoints[0].mNode,self._i_constrainNull.mNode,maintainOffset = True)
    
    #Dynamic parent groups
    #====================================================================================
    try:#>>>> Foot
	#Build our dynamic groups
	ml_footDynParents = [self._i_masterControl]
	if mi_moduleParent:
	    mi_parentRigNull = mi_moduleParent.rigNull
	    if mi_parentRigNull.getMessage('cog'):
		ml_footDynParents.append( mi_parentRigNull.cog )	    
	    if mi_parentRigNull.getMessage('hips'):
		ml_footDynParents.append( mi_parentRigNull.hips )	    
	if mi_controlIK.getMessage('spacePivots'):
	    ml_footDynParents.extend(mi_controlIK.spacePivots)
	    
	log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._strShortName,[i_obj.getShortName() for i_obj in ml_footDynParents]))
	
	#Add our parents
	i_dynGroup = mi_controlIK.dynParentGroup
	log.info("Dyn group at setup: %s"%i_dynGroup)
	i_dynGroup.dynMode = 0
	
	for o in ml_footDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()
	
	#i_dynGroup.dynFollow.parent = self._i_masterDeformGroup.mNode
    except StandardError,error:
	log.error("leg.build_rig>> foot dynamic parent setup fail!")
	raise StandardError,error
    
    #Dynamic parent groups
    #====================================================================================
    try:#>>>> Knee
	#Build our dynamic groups
	ml_kneeDynParents = [mi_controlIK]
	ml_kneeDynParents.append(self._i_masterControl)
	if mi_moduleParent:
	    mi_parentRigNull = mi_moduleParent.rigNull
	    if mi_parentRigNull.getMessage('cog'):
		ml_kneeDynParents.append( mi_parentRigNull.cog )	    
	    if mi_parentRigNull.getMessage('hips'):
		ml_kneeDynParents.append( mi_parentRigNull.hips )	    
	if mi_controlIK.getMessage('spacePivots'):
	    ml_kneeDynParents.extend(mi_controlIK.spacePivots)
	    
	log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._strShortName,[i_obj.getShortName() for i_obj in ml_kneeDynParents]))
	
	#Add our parents
	i_dynGroup = mi_controlMidIK.dynParentGroup
	log.info("Dyn group at setup: %s"%i_dynGroup)
	i_dynGroup.dynMode = 0
	
	for o in ml_kneeDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()
	
	#i_dynGroup.dynFollow.parent = self._i_masterDeformGroup.mNode
    except StandardError,error:
	log.error("leg.build_rig>> knee dynamic parent setup fail!")
	raise StandardError,error
    
    #Make some connections
    #=
    cgmMeta.cgmAttr(mi_settings,"kneeSpace_in").doConnectIn("%s.space"%mi_controlMidIK.mNode)#This connects to one of our twist fixes from the deformation setup
    

    #Parent and constrain joints
    #====================================================================================
    ml_rigJoints[0].parent = self._i_deformNull.mNode#hip
    ml_rigJoints[-2].parent = self._i_deformNull.mNode#ankle
    #ml_rigJoints[-2].parent = self._i_deformNull.mNode#ankle
    #Need to grab knee and parent to deform Null


    #For each of our rig joints, find the closest constraint target joint
    l_constrainTargetJoints
    l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
    for i,i_jnt in enumerate(ml_rigJoints):
	#Don't try scale constraints in here, they're not viable
	attachJoint = distance.returnClosestObject(i_jnt.mNode,l_constrainTargetJoints)
	log.info("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
	pntConstBuffer = mc.pointConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
	orConstBuffer = mc.orientConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
	mc.connectAttr((attachJoint+'.s'),(i_jnt.mNode+'.s'))
        
    #Setup foot Scaling
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
    mPlug_ikFootScale = cgmMeta.cgmAttr(mi_controlIK,'sy')
    mPlug_ikFootScale.p_nameAlias = 'ikScale'
    mPlug_ikFootScale.p_keyable = True

    #FK Scale
    attributes.doSetLockHideKeyableAttr(ml_controlsFK[-2].mNode,lock=False,visible=True,keyable=True,channels=['s%s'%orientation[0]])
    for attr in orientation[1:]:
	cgmMeta.cgmAttr(ml_controlsFK[-2],'s%s'%orientation[0]).doConnectOut("%s.s%s"%(ml_controlsFK[-2].mNode,attr))
	
    cgmMeta.cgmAttr(ml_controlsFK[-2],'scale').doConnectOut("%s.scale"%ml_controlsFK[-1].mNode)
    cgmMeta.cgmAttr(ml_controlsFK[-2],'scale').doConnectOut("%s.inverseScale"%ml_controlsFK[-1].mNode)
    
    mPlug_fkFootScale = cgmMeta.cgmAttr(ml_controlsFK[-2],'s%s'%orientation[0])
    mPlug_fkFootScale.p_nameAlias = 'fkScale'
    mPlug_fkFootScale.p_keyable = True
    
    #Blend the two
    mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK')
    rUtils.connectBlendJointChain(ml_fkJoints[-2:],ml_ikJoints[-3:-1],ml_blendJoints[-2:],
                                  driver = mPlug_FKIK.p_combinedName,channels=['scale'])    
    
    #Vis Network, lock and hide
    #====================================================================================
    #Segment handles need to lock
    for ml_chain in ml_segmentHandleChains:
	for i_obj in ml_chain:
	    attributes.doSetLockHideKeyableAttr(i_obj.mNode,lock=True, visible=False, keyable=False, channels=['s%s'%orientation[1],'s%s'%orientation[2]])
    
    #
    attributes.doSetLockHideKeyableAttr(mi_settings.mNode,lock=True, visible=False, keyable=False)
     
    #Final stuff
    self._i_rigNull.version = str(__version__)
    return True 


@r9General.Timer
def build_matchSystem(self):
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("leg.build_deformationRig>>bad self!")
	raise StandardError,error
    
    #Base info
    mi_moduleParent = False
    if self._i_module.getMessage('moduleParent'):
	mi_moduleParent = self._i_module.moduleParent
	
    mi_controlIK = self._i_rigNull.controlIK
    mi_controlMidIK = self._i_rigNull.midIK 
    ml_controlsFK =  self._i_rigNull.controlsFK    
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_blendJoints = self._i_rigNull.blendJoints
    mi_settings = self._i_rigNull.settings

    mi_controlIK = self._i_rigNull.controlIK
    mi_controlMidIK = self._i_rigNull.midIK  
    
    ml_fkJoints = self._i_rigNull.fkJoints
    ml_ikJoints = self._i_rigNull.ikJoints
    ml_ikPVJoints = self._i_rigNull.ikPVJoints
    ml_ikNoFlipJoints = self._i_rigNull.ikNoFlipJoints
    
    mi_dynSwitch = self._i_dynSwitch
    
    #>>> First IK to FK
    i_ikFootMatch_noKnee = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlIK,
                                                      dynPrefix = "FKtoIK",
                                                      dynMatchTargets=ml_blendJoints[-2])
    i_ikFootMatch_noKnee.addPrematchData({'roll':0,'toeSpin':0,'lean':0,'bank':0})
    
    #Toe iter
    i_ikFootMatch_noKnee.addDynIterTarget(drivenObject =ml_ikJoints[-1],
                                          matchTarget = ml_blendJoints[-1],#Make a new one
                                          minValue=-90,
                                          maxValue=90,
                                          maxIter=15,
                                          driverAttr='toeWiggle')
    
    i_ikFootMatch_noKnee.addDynIterTarget(drivenObject =ml_ikJoints[1],#knee
                                          matchObject = ml_blendJoints[1],
                                          drivenAttr= 't%s'%self._jointOrientation[0],
                                          matchAttr = 't%s'%self._jointOrientation[0],
                                          minValue=0.001,
                                          maxValue=30,
                                          maxIter=15,
                                          driverAttr='lengthUpr')    
    i_ikFootMatch_noKnee.addDynIterTarget(drivenObject =ml_ikJoints[2],#ankle
                                          matchObject= ml_blendJoints[2],#Make a new one
                                          drivenAttr='t%s'%self._jointOrientation[0],
                                          matchAttr = 't%s'%self._jointOrientation[0],
                                          minValue=0.001,
                                          maxValue=30,
                                          maxIter=15,
                                          driverAttr='lengthLwr')  
    
    i_ikFootMatch_noKnee.addDynIterTarget(drivenObject =ml_ikNoFlipJoints[1],#knee
                                          matchTarget = ml_blendJoints[1],#Make a new one
                                          minValue=-179,
                                          maxValue=179,
                                          maxIter=15,
                                          driverAttr='kneeSpin') 
    

    i_ikFootMatch_noKnee.addDynAttrMatchTarget(dynObjectAttr='ikScale',
                                               matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._jointOrientation[0]],#Make a new one
                                               )
    #>> Foot
    """
    i_ikMidMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlMidIK,
                                              dynPrefix = "FKtoIK",
                                              dynMatchTargets=ml_blendJoints[1]) """
    
    i_ikMidMatch = mi_controlMidIK.FKtoIK_dynMatchDriver
    #>>> FK to IK
    i_fkHipMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[0],
                                              dynPrefix = "IKtoFK",
                                              dynMatchTargets=ml_blendJoints[0])
    i_fkHipMatch.addDynIterTarget(drivenObject =ml_fkJoints[1],
                                  #matchTarget = ml_blendJoints[1],#Make a new one
                                  matchObject = ml_blendJoints[1],
                                  drivenAttr='t%s'%self._jointOrientation[0],
                                  matchAttr = 't%s'%self._jointOrientation[0],
                                  minValue=0.001,
                                  maxValue=30,
                                  maxIter=15,
                                  driverAttr='length')  
    
    i_fkKneeMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[1],
                                               dynPrefix = "IKtoFK",
                                               dynMatchTargets=ml_blendJoints[1])
    i_fkKneeMatch.addDynIterTarget(drivenObject =ml_fkJoints[2],
                                   #matchTarget = ml_blendJoints[2],#Make a new one
                                   matchObject = ml_blendJoints[2],                                   
                                   drivenAttr='t%s'%self._jointOrientation[0],
                                   matchAttr = 't%s'%self._jointOrientation[0],
                                   minValue=0.001,
                                   maxValue=30,
                                   maxIter=15,
                                   driverAttr='length')  
    
    i_fkAnkleMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[2],
                                              dynPrefix = "IKtoFK",
                                              dynMatchTargets=ml_blendJoints[2])
    i_fkBallMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[3],
                                              dynPrefix = "IKtoFK",
                                              dynMatchTargets=ml_blendJoints[3])   
      
    i_fkAnkleMatch.addDynAttrMatchTarget(dynObjectAttr='fkScale',
                                         matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._jointOrientation[0]],
                                         )    
    #>>> Register the switches
    mi_dynSwitch.addSwitch('snapToFK',[mi_settings.mNode,'blend_FKIK'],
                           0,
                           [i_fkHipMatch,i_fkKneeMatch,i_fkAnkleMatch,i_fkBallMatch])
    
    mi_dynSwitch.addSwitch('snapToIK_noKnee',[mi_settings.mNode,'blend_FKIK'],
                           1,
                           [i_ikFootMatch_noKnee,i_ikMidMatch])
    mi_dynSwitch.addSwitch('snapToIK_knee',[mi_settings.mNode,'blend_FKIK'],
                           1,
                           [i_ikFootMatch_noKnee,i_ikMidMatch])
    
    mi_dynSwitch.setPostmatchAliasAttr('snapToIK_noKnee',[mi_controlIK.mNode,'showKnee'],0)
    mi_dynSwitch.setPostmatchAliasAttr('snapToIK_knee',[mi_controlIK.mNode,'showKnee'],1)
    
    
@r9General.Timer
def __build__(self, buildTo='',*args,**kws): 
    """
    For the leg, build order is skeleton first as we need our mid segment handle joints created to cast from
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
    
    #build_deformation(self)
    #build_rig(self)    
    
    return True