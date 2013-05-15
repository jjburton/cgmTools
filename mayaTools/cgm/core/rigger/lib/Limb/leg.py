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
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)

from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
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
	self._i_rigNull.connectChildNode(i_trans,"pivot_%s"%pivot,'module')
	
    #Ball Joint pivot
    i_ballJointPivot = self._i_module.rigNull.skinJoints[-1].doDuplicateTransform(True)#dup ball in place
    i_ballJointPivot.parent = False
    i_ballJointPivot.cgmName = 'ballJoint'
    i_ballJointPivot.addAttr('cgmTypeModifier','pivot')
    i_ballJointPivot.doName()
    self._i_rigNull.connectChildNode(i_ballJointPivot,"pivot_ballJoint",'module')
    
    #Ball wiggle pivot
    i_ballWigglePivot = i_ballJointPivot.doDuplicate(True)#dup ball in place
    i_ballWigglePivot.parent = False
    i_ballWigglePivot.cgmName = 'ballWiggle'
    i_ballWigglePivot.doName()
    self._i_rigNull.connectChildNode(i_ballWigglePivot,"pivot_ballWiggle",'module')    
	""" 
    #>>> Build our Mid Handle Shapes
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
    
    return
    #>>>Build our Shapes
    #=============================================================
    try:
	l_toBuild = ['segmentIK','segmentFK_Loli','settings','midIK','foot']
	mShapeCast.go(self._i_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
	log.info(self._md_controlShapes)
	log.info(self._md_controlPivots)
	self._i_rigNull.connectChildrenNodes(self._md_controlShapes['segmentFK_Loli'],'shape_controlsFK','module')	
	self._i_rigNull.connectChildNode(self._md_controlShapes['midIK'],'shape_midIK','module')
	self._i_rigNull.connectChildNode(self._md_controlShapes['settings'],'shape_settings','module')		
	self._i_rigNull.connectChildNode(self._md_controlShapes['foot'],'shape_foot','module')
	
    except StandardError,error:
	log.error("build_leg>>Build shapes fail!")
	raise StandardError,error   
    

#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['anchorJoints','rigJoints','influenceJoints','fkJoints','ikJoints','blendJoints']   
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
	self._i_rigNull.connectChildNode(i_trans,"pivot_%s"%pivot,'module')
	
    #Ball Joint pivot
    i_ballJointPivot = self._i_module.rigNull.skinJoints[-1].doDuplicateTransform(True)#dup ball in place
    i_ballJointPivot.parent = False
    i_ballJointPivot.cgmName = 'ballJoint'
    i_ballJointPivot.addAttr('cgmTypeModifier','pivot')
    i_ballJointPivot.doName()
    self._i_rigNull.connectChildNode(i_ballJointPivot,"pivot_ballJoint",'module')
    
    #Ball wiggle pivot
    i_ballWigglePivot = i_ballJointPivot.doDuplicate(True)#dup ball in place
    i_ballWigglePivot.parent = False
    i_ballWigglePivot.cgmName = 'ballWiggle'
    i_ballWigglePivot.doName()
    self._i_rigNull.connectChildNode(i_ballWigglePivot,"pivot_ballWiggle",'module') 
    
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
	
	self._i_rigNull.connectChildrenNodes(ml_rigJoints,'rigJoints','module')
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
	ml_influenceJoints = []
	ml_segmentHandleJoints = []#To use later as well
	for i_ctrl in self._i_templateNull.controlObjects:
	    if i_ctrl.getAttr('cgmName') in ['hip','knee','ankle']:
		if not i_ctrl.getMessage('handleJoint'):
		    raise StandardError,"%s.build_rigSkeleton>>> failed to find a handle joint from: '%s'"%(self._i_module.getShortName(),i_ctrl.getShortName())
		i_handle = i_ctrl.handleJoint
		ml_segmentHandleJoints.append(i_handle)
		i_new = cgmMeta.cgmObject(mc.duplicate(i_ctrl.getMessage('handleJoint')[0],po=True,ic=True)[0])
		i_new.addAttr('cgmTypeModifier','influence',attrType='string',lock=True)
		i_new.parent = False
		i_new.doName()
		i_new.rotateOrder = self._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations
		ml_influenceJoints.append(i_new)
	joints.doCopyJointOrient(ml_influenceJoints[-2].mNode,ml_influenceJoints[-1].mNode)
	if len(ml_influenceJoints)!=3:
	    raise StandardError,"%s.build_rigSkeleton>>> don't have 3 influence joints: '%s'"%(self._i_module.getShortName(),ml_influenceJoints)
	    
	#Make influence joints
	l_influencePairs = lists.parseListToPairs(ml_influenceJoints)
	ml_influenceChains = []
	log.info(l_influencePairs)
	for i,m_pair in enumerate(l_influencePairs):
	    tmp_chain = [m_pair[0]]
	    startIndex = ml_influenceJoints.index(m_pair[0])#index our start so we an insert our new joints
	    log.info("%s.build_rigSkeleton>>> Splitting influence segment: 2 |'%s' >> '%s'"%(self._i_module.getShortName(),m_pair[0].getShortName(),m_pair[1].getShortName()))
	    m_pair[1].parent = m_pair[0].mNode
	    l_new_chain = joints.insertRollJointsSegment(m_pair[0].mNode,m_pair[1].mNode,1)
	    log.info("%s.build_rigSkeleton>>> split chain: %s"%(self._i_module.getShortName(),l_new_chain))
	    #Let's name our new joints
	    for ii,jnt in enumerate(l_new_chain):
		i_jnt = cgmMeta.cgmObject(jnt,setClass=True)
		i_jnt.doCopyNameTagsFromObject(m_pair[0].mNode)
		i_jnt.addAttr('cgmName','%s_mid_%s'%(m_pair[0].cgmName,ii),lock=True)
		i_jnt.doName()
		tmp_chain.append(i_jnt)
		ml_influenceJoints.insert(startIndex + ii + 1,i_jnt)
	    tmp_chain.append(m_pair[1])#append to running list
	    ml_influenceChains.append(tmp_chain)#append to influence chains
	
	for i_j in ml_influenceJoints:
	    log.info(i_j.getShortName())
		
	#Figure out how we wanna store this, ml_influence joints 
	for i_jnt in ml_influenceJoints:
	    i_jnt.parent = False
    except StandardError,error:
	log.error("build_rigSkeleton>>Build influence joints fail!")
	raise StandardError,error    
    
    try:#>>Anchor chain
	#=====================================================================	
	ml_anchors = []
	for i_jnt in ml_influenceJoints:
	    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
	    i_new.addAttr('cgmTypeModifier','anchor',attrType='string',lock=True)
	    i_new.parent = False
	    i_new.doName()

	    ml_anchors.append(i_new)	 
    except StandardError,error:
	log.error("build_rigSkeleton>>Build anchor joints fail!")
	raise StandardError,error 
    
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
	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build segment joints fail!")
	raise StandardError,error   

    try:#>>> Store em all to our instance
	#=====================================================================	
	self._i_rigNull.connectChildrenNodes(ml_fkJoints,'fkJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_blendJoints,'blendJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_ikJoints,'ikJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_ikNoFlipJoints,'ikNoFlipJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_ikPVJoints,'ikPVJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'influenceJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'anchorJoints','module')
	for i,ml_chain in enumerate(ml_segmentChains):
	    self._i_rigNull.connectChildrenNodes(ml_chain,'segment%s_Joints'%i,'module')
	    log.info("segment%s_Joints>> %s"%(i,self._i_rigNull.getMessage('segment%sJoints'%i,False)))
	for i,ml_chain in enumerate(ml_influenceChains):
	    self._i_rigNull.connectChildrenNodes(ml_chain,'segment%s_InfluenceJoints'%i,'module')
	    log.info("segment%s_InfluenceJoints>> %s"%(i,self._i_rigNull.getMessage('segment%sInfluenceJoints'%i,False)))
	    
	log.info("anchorJoints>> %s"%self._i_rigNull.getMessage('anchorJoints',False))
	log.info("fkJoints>> %s"%self._i_rigNull.getMessage('fkJoints',False))
	log.info("ikJoints>> %s"%self._i_rigNull.getMessage('ikJoints',False))
	log.info("blendJoints>> %s"%self._i_rigNull.getMessage('blendJoints',False))
	log.info("influenceJoints>> %s"%self._i_rigNull.getMessage('influenceJoints',False))
	log.info("ikNoFlipJoints>> %s"%self._i_rigNull.getMessage('ikNoFlipJoints',False))
	log.info("ikPVJoints>> %s"%self._i_rigNull.getMessage('ikPVJoints',False))
   
    except StandardError,error:
	log.error("build_leg>>StoreJoints fail!")
	raise StandardError,error   

    """
    ml_jointsToConnect = [i_startJnt,i_endJnt]
    ml_jointsToConnect.extend(ml_rigJoints)
    ml_jointsToConnect.extend(ml_segmentJoints)    
    ml_jointsToConnect.extend(ml_influenceJoints)

    for i_jnt in ml_jointsToConnect:
	i_jnt.overrideEnabled = 1		
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    
	"""
    
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
    mPlug_toeStaighten = cgmMeta.cgmAttr(mi_controlIK,'toeStaighten',attrType='float',initialValue = 70,defaultValue = 70,keyable = True)
    mPlug_toeWiggle= cgmMeta.cgmAttr(mi_controlIK,'toeWiggle',attrType='float',defaultValue = 0,keyable = True)
    mPlug_toeSpin = cgmMeta.cgmAttr(mi_controlIK,'toeSpin',attrType='float',defaultValue = 0,keyable = True)
    mPlug_lean = cgmMeta.cgmAttr(mi_controlIK,'lean',attrType='float',defaultValue = 0,keyable = True)
    mPlug_side = cgmMeta.cgmAttr(mi_controlIK,'bank',attrType='float',defaultValue = 0,keyable = True)
    mPlug_kneeSpin = cgmMeta.cgmAttr(mi_controlIK,'kneeSpin',attrType='float',defaultValue = 0,keyable = True)
    mPlug_lockMid = cgmMeta.cgmAttr(mi_controlIK,'lockMid',attrType='float',defaultValue = 0,keyable = True)
    mPlug_stretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
    mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee',attrType='bool',defaultValue = 0,keyable = True)
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
    
    for chain in [ml_ikJoints,ml_blendJoints,ml_ikNoFlipJoints,ml_ikPVJoints]:
	chain[0].parent = self._i_deformNull.mNode
	
    #for more stable ik, we're gonna lock off the lower channels degrees of freedom
    for chain in [ml_ikNoFlipJoints,ml_ikPVJoints]:
	for axis in self._jointOrientation[:2]:
	    log.info(axis)
	    for i_j in chain[1:]:
		attributes.doSetAttr(i_j.mNode,"jointType%s"%axis.upper(),0)
    
    #=============================================================    
    try:#>>>FK Length connector
	for i,i_jnt in enumerate(ml_fkJoints[:-1]):
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
	ml_distHandlesNF[0].parent = self._i_deformNull.mNode#hip distance handle to deform group
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
	
	#>>> Reset the translations
	mi_controlMidIK.tx = 0
	mi_controlMidIK.ty = 0
	mi_controlMidIK.tz = 0
	
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
	
	mPlug_FKon.doConnectOut("%s.visibility"%self._i_deformNull.controlsFK.mNode)
	mPlug_IKon.doConnectOut("%s.visibility"%self._i_deformNull.controlsIK.mNode)
	
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
	i_dup = self._i_deformNull.doDuplicateTransform(True)
	i_dup.parent = self._i_deformNull.mNode
	i_dup.addAttr('cgmTypeModifier',grp,lock=True)
	i_dup.doName()
	
	self._i_deformNull.connectChildNode(i_dup,grp,'owner')
	
    l_controlsAll = []
    #==================================================================
    try:#>>>> FK Segments
	if len( ml_controlsFK )<3:
	    raise StandardError,"%s.build_controls>>> Must have at least three fk controls"%self._strShortName	    
	
	#for i,i_obj in enumerate(ml_controlsFK[1:]):#parent
	    #i_obj.parent = ml_controlsFK[i].mNode
	ml_fkJoints[0].parent = self._i_deformNull.controlsFK.mNode
		
	for i,i_obj in enumerate(ml_controlsFK):
	    d_buffer = mControlFactory.registerControl(i_obj,shapeParentTo=ml_fkJoints[i],setRotateOrder=5,typeModifier='fk',) 	    
	    i_obj = d_buffer['instance']
	    
	for i_obj in ml_controlsFK:
	    i_obj.delete()
	    
	#ml_controlsFK[0].masterGroup.parent = self._i_deformNull.mNode
	self._i_rigNull.connectChildrenNodes(ml_fkJoints,'controlsFK','module')
	l_controlsAll.extend(ml_fkJoints)	
    
    except StandardError,error:	
	log.error("%s.build_controls>>> Build fk fail!"%self._strShortName)
	raise StandardError,error
    
    #==================================================================    
    try:#>>>> IK Handle
	i_IKEnd = mi_foot
	i_IKEnd.parent = False
	d_buffer = mControlFactory.registerControl(i_IKEnd,
	                                           typeModifier='ik',addSpacePivots = 0, addDynParentGroup = True, addConstraintGroup=True,
	                                           makeAimable = True,setRotateOrder=4)
	i_IKEnd = d_buffer['instance']	
	i_IKEnd.masterGroup.parent = self._i_deformNull.controlsIK.mNode
	
	#i_loc.delete()#delete
	self._i_rigNull.connectChildNode(i_IKEnd,'controlIK','module')#connect
	l_controlsAll.append(i_IKEnd)	

	#Set aims
	i_IKEnd.axisAim = 4
	i_IKEnd.axisUp= 2
	
    except StandardError,error:
	log.error("%s.build_controls>>> Build ik handle fail!"%self._strShortName)	
	raise StandardError,error   
    
    #==================================================================    
    try:#>>>> midIK Handle
	i_IKmid = mi_midIK
	i_IKmid.parent = False
	d_buffer = mControlFactory.registerControl(i_IKmid,
	                                           typeModifier='ik',addDynParentGroup = True, addConstraintGroup=True,
	                                           makeAimable = False,setRotateOrder=4)
	i_IKmid = d_buffer['instance']	
	i_IKmid.masterGroup.parent = self._i_deformNull.controlsIK.mNode
	i_IKmid.addAttr('scale',lock=True,hidden=True)
	#i_loc.delete()#delete
	self._i_rigNull.connectChildNode(i_IKmid,'midIK','module')#connect
	l_controlsAll.append(i_IKmid)	
	
    except StandardError,error:
	log.error("%s.build_controls>>> Build ik handle fail!"%self._strShortName)	
	raise StandardError,error   
    
    #==================================================================
    try:#>>>> Settings
	d_buffer = mControlFactory.registerControl(mi_settings,addExtraGroups=0,typeModifier='settings',autoLockNHide=True,
                                                   setRotateOrder=2)       
	i_obj = d_buffer['instance']
	i_obj.masterGroup.parent = self._i_deformNull.mNode
	self._i_rigNull.connectChildNode(mi_settings,'settings','module')
	l_controlsAll.append(mi_settings)
	
	#Add our attrs
	mi_settings.addAttr('blend_FKIK', defaultValue = 0, attrType = 'float', minValue = 0, maxValue = 1, keyable = False,hidden = False,lock=True)
	#mi_settings.addAttr('state',enumName = 'fk:ik', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False,lock=True)
	#mi_settings.addAttr('kneeVis', defaultValue = 0, attrType = 'bool',keyable = False,hidden = False,lock=True)
	
	
    except StandardError,error:
	log.error("%s.build_controls>>> Build settings fail!"%self._strShortName)		
	raise StandardError,error
    
    #==================================================================    
    try:#>>>> IK Segments
	ml_segmentsIK = ml_segmentIKShapes
	
	for i_obj in ml_segmentsIK:
	    d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='ik',
		                                       setRotateOrder=2)       
	    i_obj = d_buffer['instance']
	    i_obj.masterGroup.parent = self._i_deformNull.mNode
	self._i_rigNull.connectChildrenNodes(ml_segmentsIK,'segmentHandles','module')
	l_controlsAll.extend(ml_segmentsIK)	
	
	
    except StandardError,error:
	log.error("build_spine>>Build ik handle fail!")
	raise StandardError,error
    
    
    
    
    #==================================================================
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
    
    #>>>Get data
    ml_influenceJoints = self._i_rigNull.influenceJoints
    ml_controlsFK =  self._i_rigNull.controlsFK    
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_anchorJoints = self._i_rigNull.anchorJoints
    #ml_segmentHandles = self._i_rigNull.segmentHandles

    mi_controlIK = self._i_rigNull.controlIK
    mi_controlMidIK = self._i_rigNull.midIK
    
    #Get our segment joints
    l_segmentChains = []
    ml_segmentChains = []
    for i in range(50):
	buffer = self._i_rigNull.getMessage('segment%s_Joints'%i)
	if buffer:
	    l_segmentChains.append(buffer)
	    ml_segmentChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	else:
	    break
    log.info("%s.build_deformation>>> Segment Chains -- cnt: %s | lists: %s"%(self._strShortName,len(l_segmentChains),l_segmentChains))
    if len(l_segmentChains)>2:
	raise StandardError, "%s.build_deformation>>> Too many segment chains, not a regular leg."%(self._strShortName)
    
    
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    
    return

    #Control Segment
    #====================================================================================
    try:#Control Segment
	log.info(self._jointOrientation)
	capAim = self._jointOrientation[0].capitalize()
	log.info("capAim: %s"%capAim)
	i_startControl = ml_segmentHandles[0]
	i_endControl = ml_segmentHandles[-1]
	#Create segment
	curveSegmentReturn = rUtils.createCGMSegment([i_jnt.mNode for i_jnt in ml_segmentJoints],
	                                             addSquashStretch=True,
	                                             addTwist=True,
	                                             influenceJoints=[ml_influenceJoints[0],ml_influenceJoints[-1]],
	                                             startControl=ml_segmentHandles[0],
	                                             endControl=ml_segmentHandles[-1],
	                                             orientation=self._jointOrientation,
	                                             baseName=self._partName,
	                                             moduleInstance=self._i_module)
	
	i_curve = curveSegmentReturn['mi_segmentCurve']
	i_curve.parent = self._i_rigNull.mNode
	self._i_rigNull.connectChildrenNodes([i_curve],'segmentCurves','module')
	self._i_rigNull.connectChildrenNodes(ml_segmentJoints,'segmentJoints','module')	#Reconnect to reset. Duplication from createCGMSegment causes issues	
	i_curve.segmentGroup.parent = self._i_rigNull.mNode
	
	"""
	midReturn = rUtils.addCGMSegmentSubControl(ml_influenceJoints[1].mNode,
	                                           segmentCurve = i_curve,
	                                           baseParent=ml_influenceJoints[0],
	                                           endParent=ml_influenceJoints[-1],
	                                           midControls=ml_segmentHandles[1],
	                                           baseName=self._partName,
	                                           orientation=self._jointOrientation)
	
	for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
	    i_grp.parent = self._i_deformNull.mNode"""
	    
    except StandardError,error:
	log.error("build_leg>>Control Segment build fail")
	raise StandardError,error
    
    
    try:#Setup top twist driver
	#Create an fk additive attributes
	str_curve = curveSegmentReturn['mi_segmentCurve'].getShortName()
	#fk_drivers = ["%s.r%s"%(i_obj.mNode,self._jointOrientation[0]) for i_obj in ml_controlsFK]
	"""fk_drivers = ["%s.r%s"%(i_obj.mNode,self._jointOrientation[0]) for i_obj in ml_controlsFK]	
	NodeF.createAverageNode(fk_drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"fkTwistSum"],1)#Raw fk twist
	
	try:NodeF.argsToNodes("%s.fkTwistResult = %s.fkTwistSum * %s.fkTwistInfluence"%(str_curve,str_curve,str_curve)).doBuild()
	except StandardError,error:
	    raise StandardError,"verify_moduleRigToggles>> fkwistResult node arg fail: %s"%error"""	
	
	drivers = ["%s.r%s"%(ml_segmentHandles[-1].mNode,self._jointOrientation[0])]
	drivers.append("%s.r%s"%(mi_controlIK.mNode,self._jointOrientation[0]))

	NodeF.createAverageNode(drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistEnd"],1)
	
    except StandardError,error:
	log.error("build_leg>>Top Twist driver fail")
	raise StandardError,error
    
    try:#Setup bottom twist driver
	log.info("%s.r%s"%(ml_segmentHandles[0].getShortName(),self._jointOrientation[0]))
	drivers = ["%s.r%s"%(ml_segmentHandles[0].mNode,self._jointOrientation[0])]
	drivers.append("%s.r%s"%(ml_controlsFK[0].mNode,self._jointOrientation[0]))

	NodeF.createAverageNode(drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistStart"],1)
    
    except StandardError,error:
	log.error("build_leg>>Bottom Twist driver fail")
	raise StandardError,error
    
        
    #Push squash and stretch multipliers to head
    i_buffer = i_curve.scaleBuffer
    
    for k in i_buffer.d_indexToAttr.keys():
	attrName = 'leg_%s'%k
	cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_controlIK.mNode,attrName,connectSourceToTarget = True)
	cgmMeta.cgmAttr(mi_controlIK.mNode,attrName,defaultValue = 1,keyable=True)
    
    return True

def build_rig(self):
    raise NotImplementedError    
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
	orientation = modules.returnSettingsData('jointOrientation')
	mi_segmentCurve = self._i_rigNull.segmentCurves[0]
	mi_segmentAnchorStart = mi_segmentCurve.anchorStart
	mi_segmentAnchorEnd = mi_segmentCurve.anchorEnd
	mi_segmentAttachStart = mi_segmentCurve.attachStart
	mi_segmentAttachEnd = mi_segmentCurve.attachEnd 
	mi_distanceBuffer = mi_segmentCurve.scaleBuffer
	mi_moduleParent = False
	if self._i_module.getMessage('moduleParent'):
	    mi_moduleParent = self._i_module.moduleParent
    
	log.info("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
	log.info("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
	log.info("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
	log.info("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
	log.info("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)
	
	ml_influenceJoints = self._i_rigNull.influenceJoints
	#ml_segmentJoints = mi_segmentCurve.drivenJoints
	ml_segmentSplineJoints = mi_segmentCurve.driverJoints
	
	ml_anchorJoints = self._i_rigNull.anchorJoints
	ml_rigJoints = self._i_rigNull.rigJoints
	ml_segmentJoints = self._i_rigNull.segmentJoints	
	ml_segmentHandles = self._i_rigNull.segmentHandles
	aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
	mi_controlIK = self._i_rigNull.controlIK
	ml_controlsFK =  self._i_rigNull.controlsFK    
	
    except StandardError,error:
	log.error("leg.build_rig>> Gather data fail!")
	raise StandardError,error
    
    #Dynamic parent groups
    #====================================================================================
    try:#>>>> Head dynamicParent
	#Build our dynamic groups
	ml_headDynParents = [ml_controlsFK[0]]
	if mi_moduleParent:
	    mi_parentRigNull = mi_moduleParent.rigNull
	    if mi_parentRigNull.getMessage('controlIK'):
		ml_headDynParents.append( mi_parentRigNull.controlIK )	    
	    if mi_parentRigNull.getMessage('cog'):
		ml_headDynParents.append( mi_parentRigNull.cog )
	ml_headDynParents.extend(mi_controlIK.spacePivots)
	ml_headDynParents.append(self._i_masterControl)
	log.info(ml_headDynParents)
	log.info([i_obj.getShortName() for i_obj in ml_headDynParents])
	
	#Add our parents
	i_dynGroup = mi_controlIK.dynParentGroup
	log.info("Dyn group at setup: %s"%i_dynGroup)
	i_dynGroup.dynMode = 2
	
	for o in ml_headDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()
	
	i_dynGroup.dynFollow.parent = self._i_masterDeformGroup.mNode
    except StandardError,error:
	log.error("leg.build_rig>> head dynamic parent setup fail!")
	raise StandardError,error

	
    #Parent and constrain joints
    #====================================================================================
    parentAttach = self._i_module.moduleParent.rigNull.skinJoints[-1].mNode
    mc.parentConstraint(parentAttach,self._i_deformNull.mNode,maintainOffset=True)#constrain
    mc.scaleConstraint(parentAttach,self._i_deformNull.mNode,maintainOffset=True)#Constrain
    
    ml_segmentJoints[0].parent = self._i_deformNull.mNode
    ml_segmentSplineJoints[0].parent = self._i_deformNull.mNode
    
    #Put the start and end controls in the heirarchy
    mc.parent(ml_segmentHandles[0].masterGroup.mNode,mi_segmentAttachStart.mNode)
    mc.parent(ml_segmentHandles[-1].masterGroup.mNode,mi_segmentAttachEnd.mNode)
    
    mi_segmentAnchorStart.parent = self._i_deformNull.mNode
    mc.parentConstraint(ml_anchorJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#constrain
    mc.scaleConstraint(ml_anchorJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#Constrain
    
    mi_segmentAnchorEnd.parent = self._i_deformNull.mNode
    mc.parentConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
    mc.scaleConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
    
    #method 1
    ml_rigJoints[0].parent = self._i_deformNull.mNode
    
    ml_rigJoints[-1].parent = ml_anchorJoints[-1].mNode
    
    ml_influenceJoints[0].parent = ml_segmentHandles[0].mNode
    ml_influenceJoints[-1].parent = ml_segmentHandles[-1].mNode
    
    #Parent anchors to controls
    ml_anchorJoints[0].parent = self._i_deformNull.mNode   
    #ml_anchorJoints[0].parent = ml_controlsFK[0].mNode
    ml_anchorJoints[-1].parent = mi_controlIK.mNode
        
    #Connect rig pelvis to anchor pelvis
    #mc.pointConstraint(ml_anchorJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)
    #mc.orientConstraint(ml_anchorJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)
    #mc.scaleConstraint(ml_anchorJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)#Maybe hips    
    
    l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
    for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
	#Don't try scale constraints in here, they're not viable
	attachJoint = distance.returnClosestObject(i_jnt.mNode,l_rigJoints)
	log.info("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
	pntConstBuffer = mc.pointConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
	orConstBuffer = mc.orientConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
	mc.connectAttr((i_jnt.mNode+'.s'),(attachJoint+'.s'))
    
    mc.pointConstraint(ml_anchorJoints[-1].mNode,ml_rigJoints[-1].mNode,maintainOffset=False)
    mc.orientConstraint(ml_anchorJoints[-1].mNode,ml_rigJoints[-1].mNode,maintainOffset=False)
    #mc.scaleConstraint(ml_anchorJoints[-1].mNode,ml_rigJoints[-2].mNode,maintainOffset=True)
    mc.connectAttr((ml_anchorJoints[-1].mNode+'.s'),(ml_rigJoints[-1].mNode+'.s'))
    
    #Set up heirarchy, connect master scale
    #====================================================================================
    #>>>Connect master scale
    cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(self._i_masterControl.mNode,'scaleY'))    
    
    #Vis Network, lock and hide
    #====================================================================================
    #Segment handles need to lock
    for i_obj in ml_segmentHandles:
	attributes.doSetLockHideKeyableAttr(i_obj.mNode,lock=True, visible=False, keyable=False, channels=['s%s'%orientation[1],'s%s'%orientation[2]])
    
    #Lock and hide hips and shoulders
    #attributes.doSetLockHideKeyableAttr(mi_controlIK.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
     

    #Final stuff
    self._i_rigNull.version = str(__version__)
    return True 


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