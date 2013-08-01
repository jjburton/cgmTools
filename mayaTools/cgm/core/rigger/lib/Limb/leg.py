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
__version__ = 0.07102013

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

from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools

from cgm.core.rigger.lib import rig_Utils as rUtils
from cgm.core.rigger.lib import joint_Utils as jntUtils
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
def build_shapes(self):
    """
    """ 
    log.info(">>> %s.build_shapes >> "%self._strShortName + "="*75)        
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
__d_controlShapes__ = {'shape':['segmentIK','controlsFK','midIK','settings','foot'],
                       'pivot':['toe','heel','ball','inner','outer']}

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
	log.error("leg.__bindSkeletonSetup__>>bad self!")
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
	
	for i,i_jnt in enumerate(ml_moduleJoints):
	    ml_skinJoints.append(i_jnt)		
	    if i_jnt.hasAttr('d_jointFlags') and i_jnt.getAttr('cgmName') not in ['ball']:
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

    except StandardError,error:
	log.error("build_leg>>__bindSkeletonSetup__ fail!")
	raise StandardError,error   
    
@cgmGeneral.Timer
def build_rigSkeleton(self):
    """
    """
    log.info(">>> %s.build_rigSkeleton >> "%self._strShortName + "="*75)                
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
	if pivot in ['inner','outer'] and self._direction == 'right':#if right, rotate the pivots
	    mc.rotate(0,180,0,i_trans.mNode,relative = True, os = True)
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
	ml_rigJoints = self.build_rigChain()
	ml_rigJoints[0].parent = False#Parent to world
		
    except StandardError,error:
	log.error("build_rigSkeleton>>Build rig joints fail!")
	raise StandardError,error   
    
    try:#>>FK chain
	#=====================================================================		
	ml_fkJoints = self.build_handleChain('fk','fkJoints')
	
	d_fkRotateOrders = {'hip':0,'ankle':0}#old hip - 5
	for i_obj in ml_fkJoints:
	    if i_obj.getAttr('cgmName') in d_fkRotateOrders.keys():
		i_obj.rotateOrder = d_fkRotateOrders.get(i_obj.cgmName)   	

    except StandardError,error:
	log.error("build_rigSkeleton>>Build fk joints fail!")
	raise StandardError,error   
    
    try:#>>Blend chain
	#=====================================================================	
	ml_blendJoints = self.build_handleChain('blend','blendJoints')
	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build blend joints fail!")
	raise StandardError,error  
    
    try:#>>IK chain
	#=====================================================================	
	"""Important - we're going to set our preferred angles on the main ik joints so ik works as expected"""
	ml_ikJoints = self.build_handleChain('ik','ikJoints')
	
	for i_jnt in ml_ikJoints:
	    if i_jnt.cgmName in __d_preferredAngles__.keys():
		log.info("preferred angles(%s)>>> %s"%(i_jnt.cgmName,__d_preferredAngles__.get(i_jnt.cgmName)))
		for i,v in enumerate(__d_preferredAngles__.get(i_jnt.cgmName)):	  
		    i_jnt.__setattr__('preferredAngle%s'%self._jointOrientation[i].upper(),v)	    

    except StandardError,error:
	log.error("%s.build_rigSkeleton>>Build ik joints fail!"%self._strShortName)
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
	d_influenceChainReturns = self.build_simpleInfluenceChains(True)
	ml_influenceChains = d_influenceChainReturns['ml_influenceChains']
	ml_influenceJoints= d_influenceChainReturns['ml_influenceJoints']	
	ml_segmentHandleJoints = d_influenceChainReturns['ml_segmentHandleJoints']
	
	if len(ml_segmentHandleJoints)!=3:
	    raise StandardError,"%s.build_rigSkeleton>>> don't have 3 influence joints: '%s'"%(self._i_module.getShortName(),l_segmentHandleJoints)
	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build influence joints fail!")
	raise StandardError,error    

    
    try:#>>Segment chain  
	#=====================================================================
	ml_segmentChains = self.build_segmentChains(ml_segmentHandleJoints,True)
	
    except StandardError,error:
	log.error("build_rigSkeleton>>Build segment joints fail!")
	raise StandardError,error   

    try:#>>> Store em all to our instance
	#=====================================================================	
	self.connect_restoreJointLists()#Restore out lists
	
	self._i_rigNull.connectChildrenNodes(ml_fkJoints,'fkJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_blendJoints,'blendJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_ikJoints,'ikJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_ikNoFlipJoints,'ikNoFlipJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_ikPVJoints,'ikPVJoints',"rigNull")
	self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'influenceJoints',"rigNull")

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
    #ml_jointsToConnect.extend(ml_blendJoints)>>> this needs to be locked/hid   
    ml_jointsToConnect.extend(ml_ikNoFlipJoints)    
    ml_jointsToConnect.extend(ml_ikPVJoints)    
    ml_jointsToConnect.extend(ml_influenceJoints)    
    ##ml_jointsToConnect.extend(ml_anchors)  
    for ml_chain in ml_segmentChains + ml_influenceChains:
	ml_jointsToConnect.extend(ml_chain)

    #Vis only
    self.connect_toRigGutsVis(ml_jointsToConnect,vis=True)
    
    if self._ml_skinJoints != self._i_rigNull.skinJoints:
	raise StandardError,"%s.build_rigSkeleton>>> Stored skin joints don't equal buffered"%(self._strShortName)

@cgmGeneral.Timer
def build_foot(self):
    """
    """
    log.info(">>> %s.build_foot >> "%self._strShortName + "="*75)                        
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
	
	arg1 = "%s = clamp(-180,0,%s)"%(mPlug_outerResult.p_combinedShortName,                                  
	                                mPlug_side.p_combinedShortName)
	arg2 = "%s = clamp(0,180,%s)"%(mPlug_innerResult.p_combinedShortName,
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
	if self._i_module.getAttr('cgmDirection') and self._i_module.cgmDirection.lower() in ['right']:
	    str_leanDriver = "%s.r%s = -%s"%(mi_pivBallJoint.mNode,self._jointOrientation[0].lower(),
	                                     mPlug_lean.p_combinedShortName)
	    NodeF.argsToNodes(str_leanDriver).doBuild()
	else:
	    mPlug_lean.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,self._jointOrientation[0].lower()))
	    
    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> lean setup fail: %s"%error  
    
    try:#toe spin setup 
	"""
	Schleifer's
	toe_loc.rotateY = $spin;
	"""   
	if self._i_module.getAttr('cgmDirection') and self._i_module.cgmDirection.lower() in ['right']:
	    str_leanDriver = "%s.r%s = -%s"%(mi_pivToe.mNode,self._jointOrientation[1].lower(),
	                                     mPlug_toeSpin.p_combinedShortName)
	    NodeF.argsToNodes(str_leanDriver).doBuild()
	else:
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
    
    
    
    
#@cgmGeneral.Timer
def build_FKIK(self):
    """
    """
    log.info(">>> %s.build_FKIK >> "%self._strShortName + "="*75)                    
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
	if self._direction == 'left':#if right, rotate the pivots
	    mc.move(outVector[0]*100,outVector[1]*100,outVector[2]*100,i_tmpLoc.mNode,r=True, rpr = True, os = True, wd = True)	
	else:
	    mc.move(-outVector[0]*100,outVector[1]*100,outVector[2]*100,i_tmpLoc.mNode,r=True, rpr = True, os = True, wd = True)	
	    
	#Create no flip leg IK
	d_ankleNoFlipReturn = rUtils.IKHandle_create(ml_ikNoFlipJoints[0].mNode,ml_ikNoFlipJoints[-1].mNode, nameSuffix = 'noFlip',
	                                             rpHandle=True,controlObject=mi_controlIK,addLengthMulti=True,
	                                             globalScaleAttr=mPlug_globalScale.p_combinedName, stretch='translate',moduleInstance=self._i_module)
	
	mi_ankleIKHandleNF = d_ankleNoFlipReturn['mi_handle']
	ml_distHandlesNF = d_ankleNoFlipReturn['ml_distHandles']
	mi_rpHandleNF = d_ankleNoFlipReturn['mi_rpHandle']
	mPlug_lockMid = d_ankleNoFlipReturn.get('mPlug_lockMid')
	log.info("IK No Flip lockMid: %s"%mPlug_lockMid)
	
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
	
	#Pull out the bank for a more stable setup
	NodeF.argsToNodes("%s.rz = -%s.rz"%(i_spinGroup.p_nameShort,
	                                    mi_controlIK.p_nameShort)).doBuild()		
	#Spin groups rotate
	if self._i_module.getAttr('cgmDirection') and self._i_module.cgmDirection.lower() in ['right']:
	    str_spinDriver = "%s.ry = -%s"%(i_spinGroup.mNode,
	                                    mPlug_kneeSpin.p_combinedShortName)
	    NodeF.argsToNodes(str_spinDriver).doBuild()
	else:
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
	raise StandardError,"%s.build_FKIK>>> IK PV error: %s"%(self._strShortName,error)
    
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
	raise StandardError,"%s.build_FKIK>>> Foot chains error: %s"%(self._strShortName,error)
    
    #=============================================================    
    try:#>>>Connect Blend Chains and connections
	#Connect Vis of knee
	#=========================================================================================
	mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee',attrType='bool',defaultValue = 0,keyable = True)	
	mPlug_showKnee.doConnectOut("%s.visibility"%mi_controlMidIK.mNode)	
	
	#>>> Main blend
	mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',lock=False,keyable=True)
	"""
	rUtils.connectBlendJointChain(ml_fkJoints,ml_ikJoints,ml_blendJoints,
	                              driver = mPlug_FKIK.p_combinedName,channels=['translate','rotate'])"""
	rUtils.connectBlendChainByConstraint(ml_fkJoints,ml_ikJoints,ml_blendJoints,
	                                     driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])
	
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
    log.info("%s.build_FKIK complete!"%self._i_module.getShortName())
    return True
    
def build_controls(self):
    """
    """    
    log.info(">>> %s.build_controls >> "%self._strShortName + "="*75)            
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
    log.info(">>> %s.build_deformation >> "%self._strShortName + "="*75)                
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
	ml_segmentHandleChains = self._get_segmentHandleChains()

	#Get our segment joints
	ml_segmentChains = self._get_segmentChains()
	if len(ml_segmentChains)>2:
	    raise StandardError, "%s.build_deformation>>> Too many segment chains, not a regular leg."%(self._strShortName)
	
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
    
    mPlug_Blend0 = cgmMeta.cgmAttr(ml_blendJoints[0],str_twistOrientation)
    mPlug_constraintNullRotate = cgmMeta.cgmAttr(self._i_constrainNull,str_twistOrientation)    
    mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
    mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)
    mPlug_worldIKEndOut = cgmMeta.cgmAttr(mi_settings,"out_worldIKEnd" , attrType='float' , lock = True) 
    
    mPlug_worldIKEndIn.doConnectOut(mPlug_worldIKEndOut.p_combinedShortName)
    
    #=========================================================================================
    
    #Control Segment
    #====================================================================================
    ml_segmentCurves = []
    ml_segmentReturns = []
    ml_segmentJointChainsReset = []
    try:#Control Segment
	log.debug(self._jointOrientation)
	capAim = self._jointOrientation[0].capitalize()
	log.debug("capAim: %s"%capAim)
	for i,ml_segmentHandles in enumerate(ml_segmentHandleChains):
	    i_startControl = ml_segmentHandles[0]
	    i_midControl = ml_segmentHandles[1]
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
	                                                 additiveScaleSetup=True,
	                                                 connectAdditiveScale=True,                                                 
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
	                                               controlTwistAxis =  'r'+self._jointOrientation[0],	                                               
	                                               moduleInstance=self._i_module)
	    
	    for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
		i_grp.parent = self._i_constrainNull.mNode
		
	    #Parent our joint chains
	    i_curve.driverJoints[0].parent = ml_blendJoints[i].mNode
	    ml_segmentChains[i][0].parent = ml_blendJoints[i].mNode    
	    
	    #>>> Attach stuff
	    #==============================================================================================
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
		
		#>>> parent handle anchors
		mi_segmentAnchorStart.parent = ml_blendJoints[i].mNode
		if i == 0:
		    mi_segmentAnchorEnd.parent = self._i_rigNull.mainSegmentHandle.mNode			    
		else:
		    mi_segmentAnchorEnd.parent = ml_blendJoints[i+1].mNode	

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
	    """
	    for ii in range(i+1):
		if ii !=  0:
		    l_fkStartDrivers.append("%s.%s"%(ml_controlsFK[ii].getShortName(),str_twistOrientation))"""
	    
	    #end twist driver
	    l_endDrivers = ["%s.%s"%(i_endControl.getShortName(),str_twistOrientation)]	    
	    l_endDrivers.append("%s"%mPlug_TwistEndFKResult.p_combinedShortName )
	    l_endDrivers.append("%s"%mPlug_TwistEndIKResult.p_combinedShortName )		    
	    l_fkEndDrivers = []
	    l_ikEndDrivers = []

	    l_fkEndDrivers.append("%s.%s"%(ml_controlsFK[i+1].getShortName(),str_twistOrientation))    
	    """
	    for ii in range(i+2):
		if ii !=  0:	
		    l_fkEndDrivers.append("%s.%s"%(ml_controlsFK[ii].getShortName(),str_twistOrientation))"""

	    if i == 0:#if seg 0
		l_ikStartDrivers.append(mPlug_worldIKStartIn.p_combinedShortName)
		l_fkStartDrivers.append(mPlug_worldIKStartIn.p_combinedShortName)		
		l_endDrivers.append("%s.%s"%(self._i_rigNull.mainSegmentHandle.getShortName(),str_twistOrientation))
		
		#If it's our first one we wann
		
		
		#We need to make our world driver start twist
		#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<;laksdjf;alskjdf;lasjkdflaj
		
	    if i == 1:#if seg 1	
		#l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
		l_ikEndDrivers.append(mPlug_worldIKEndOut.p_combinedShortName)
						
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
	    
	    #>>> Attributes 
	    #================================================================================================================
	    #Connect master scale
	    cgmMeta.cgmAttr(i_curve.scaleBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(self._i_masterControl.mNode,'scaleY'))    	    
	    
	    #Push squash and stretch multipliers to head
	    i_buffer = i_curve.scaleBuffer	    
	    for ii,k in enumerate(i_buffer.d_indexToAttr.keys()):
		#attrName = 'leg_%s'%k
		attrName = "seg_%s_%s_mult"%(i,ii)
		cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_settings.mNode,attrName,connectSourceToTarget = True)
		cgmMeta.cgmAttr(mi_settings.mNode,attrName,defaultValue = 1,keyable=True)
		
	    #Other attributes transfer
	    cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(i_midControl.mNode,connectSourceToTarget=True)
	    cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(i_midControl.mNode,connectSourceToTarget=True)
	    #cgmMeta.cgmAttr(i_curve,'twistMid').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
	    #cgmMeta.cgmAttr(i_curve,'scaleMidUp').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
	    #cgmMeta.cgmAttr(i_curve,'scaleMidOut').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)	    

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
    log.info(">>> { %s.build_rig } >> "%self._strShortName + "="*75)        
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
	
	log.debug("mi_controlIK: %s"%mi_controlIK.mNode)
	log.debug("mi_controlMidIK: %s"%mi_controlMidIK.mNode)	
	log.debug("ml_controlsFK: %s"%[o.getShortName() for o in ml_controlsFK])
	log.debug("mi_settings: %s"%mi_settings.mNode)
	
	log.debug("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
	log.debug("ml_blendJoints: %s"%[o.getShortName() for o in ml_blendJoints])
	
	ml_segmentHandleChains = self._get_segmentHandleChains()
	ml_segmentChains = self._get_segmentChains()
	ml_influenceChains = self._get_influenceChains()	
	ml_rigHandleJoints = self._get_handleJoints()
	aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1]) 
	
	#Build our contrain to pool
	d_indexRigJointToDriver = self._get_simpleRigJointDriverDict()
	
    except StandardError,error:
	log.error("leg.build_rig>> Gather data fail!")
	raise StandardError,error
    
    #Constrain to pelvis
    if mi_moduleParent:
	mc.parentConstraint(mi_moduleParent.rigNull.moduleJoints[0].mNode,self._i_constrainNull.mNode,maintainOffset = True)
    
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
    
    for i,i_jnt in enumerate(d_indexRigJointToDriver.keys()):
	#Don't try scale constraints in here, they're not viable
	attachJoint = d_indexRigJointToDriver[i_jnt].getShortName()
	log.info("'%s'>>drives>>'%s'"%(attachJoint,i_jnt.getShortName()))
	pntConstBuffer = mc.pointConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
	orConstBuffer = mc.orientConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
	if i_jnt.hasAttr('scaleJoint') and i_jnt.cgmName != 'ankle':
	    mc.connectAttr((attachJoint+'.s'),(i_jnt.getMessage('scaleJoint')[0] +'.s'))	    
	else:
	    mc.connectAttr((attachJoint+'.s'),(i_jnt.mNode+'.s'))
	    
    if ml_rigHandleJoints[-2].getMessage('scaleJoint'):#If our ankle has a scale joint, we need to connect it to our last joint of our last segment
	attributes.doConnectAttr((ml_segmentChains[-1][-1].mNode + '.s'),(ml_rigHandleJoints[-2].scaleJoint.mNode+'.s'))
    
    
    #Now we need to make an average for the extra knee that averages the seg0,1 knees
    i_pma = cgmMeta.cgmNode(nodeType = 'plusMinusAverage')
    i_pma.operation = 3#average
    mc.connectAttr("%s.s"%ml_segmentChains[0][-1].mNode,"%s.%s"%(i_pma.mNode,'input3D[0]'))
    mc.connectAttr("%s.s"%ml_segmentChains[-1][0].mNode,"%s.%s"%(i_pma.mNode,'input3D[1]'))
    mc.connectAttr("%s.%s"%(i_pma.mNode,'output3D'),"%s.s"%(ml_rigHandleJoints[1].scaleJoint.mNode),force=True)
    
    try:#Setup foot Scaling
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
    except StandardError,error:
	raise StandardError,"%s.build_rig >> failed to setup foot scale | %s"%(self._strShortName,error)	     
     
    #Vis Network, lock and hide
    #====================================================================================
    #Segment handles need to lock
    attributes.doSetLockHideKeyableAttr(mi_settings.mNode,lock=True, visible=False, keyable=False)
    
    for i_jnt in ml_blendJoints:
        attributes.doSetLockHideKeyableAttr(i_jnt.mNode,lock=True, visible=True, keyable=False)

     
    try:#Set up some defaults
	#====================================================================================
	mPlug_autoStretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch')
	mPlug_autoStretch.p_defaultValue = 1.0
	mPlug_autoStretch.value =  1
	
	mPlug_seg0end = cgmMeta.cgmAttr(ml_segmentHandleChains[0][-1],'followRoot')
	mPlug_seg0end.p_defaultValue = .5
	mPlug_seg0end.value = .5
	
	mPlug_seg1end = cgmMeta.cgmAttr(ml_segmentHandleChains[1][-1],'followRoot')
	mPlug_seg1end.p_defaultValue = .5
	mPlug_seg1end.value = .5	
	
	#mid segment handles
	mPlug_seg0mid = cgmMeta.cgmAttr(ml_segmentHandleChains[0][1],'twistExtendToEnd')
	mPlug_seg0mid.p_defaultValue = 1
	mPlug_seg0mid.value = 1	
	
	mPlug_seg1mid = cgmMeta.cgmAttr(ml_segmentHandleChains[1][1],'twistExtendToEnd')
	mPlug_seg1mid.p_defaultValue = 1
	mPlug_seg1mid.value = 1		

    except StandardError,error:
	raise StandardError,"%s.build_rig >> failed to setup defaults | %s"%(self._strShortName,error)	     
     
    #Final stuff
    self._set_versionToCurrent()
    return True 
#------------------------------------------------------------------------------------------------------------#    
def build_twistDriver_hip(self):
    log.info(">>> %s.build_twistDriver_hip >> "%self._strShortName + "="*75)
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("build_twistDriver_hip>>bad self!")
	raise StandardError,error
    
    try:
	mi_settings = self._i_rigNull.settings	
	mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
    except StandardError,error:
	raise StandardError,"%s.build_twistDriver_hip >> failed to setup start attr | %s"%(self._strShortName,error)	
    try:
	mi_parentRigNull = self._i_module.moduleParent.rigNull
	mi_hips = mi_parentRigNull.hips	
    except StandardError,error:
	raise StandardError,"%s.build_twistDriver_hip >> failed to find hips | %s"%(self._strShortName,error)	
    
    try:
	outVector = self._vectorOut
	upVector = self._vectorUp      
	ml_blendJoints = self._i_rigNull.blendJoints
	

	#Create joints
	#i_startAim = self.duplicate_moduleJoint(0,'startAim')
	#i_startEnd = self.duplicate_moduleJoint(0,'startAimEnd')
	i_startRoot = self._ml_moduleJoints[0].doDuplicate(incomingConnections = False)
	i_startRoot.addAttr('cgmName',self._partName)	
	i_startRoot.addAttr('cgmTypeModifier','twistDriver')
	i_startRoot.doName()
	i_startEnd = self._ml_moduleJoints[0].doDuplicate(incomingConnections = False)
	i_startEnd.addAttr('cgmTypeModifier','twistDriverEnd')
	i_startEnd.doName()    
	
	i_upLoc = i_startRoot.doLoc()	
	
	self.connect_restoreJointLists()#Restore out lists
	
	i_startEnd.parent = i_startRoot.mNode
	ml_twistObjects = [i_startRoot,i_startEnd,i_upLoc]
	fl_dist = 25
	if self._direction == 'left':#if right, rotate the pivots
	    i_upLoc.__setattr__('t%s'%self._jointOrientation[2],fl_dist)	
	else:
	    i_upLoc.__setattr__('t%s'%self._jointOrientation[2],-fl_dist)		
	
	#Move up
	i_startEnd.__setattr__('t%s'%self._jointOrientation[0],(fl_dist))
	
	i_startRoot.parent = ml_blendJoints[0].mNode
    except StandardError,error:
	raise StandardError,"%s.build_twistDriver_hip >> Failed joint creation,positioning | %s"%(self._strShortName,error)	    
    
    #=============================================================================
    try:#setup stable hip rotate group  
	i_rotGroup = self._i_constrainNull.doDuplicateTransform(False)
	i_rotGroup.addAttr('cgmType','stableHipTwistRotGroup')
	i_rotGroup.doName()
	ml_twistObjects.append(i_rotGroup)
	i_upLoc.parent = i_rotGroup.mNode
	
	i_rotGroup.parent = self._i_constrainNull.mNode
		
	NodeF.argsToNodes("%s.ry = -%s.ry + %s.ry"%(i_rotGroup.p_nameShort,
	                                            self._i_constrainNull.p_nameShort,
	                                            ml_blendJoints[0].p_nameShort)).doBuild()	
	
    except StandardError,error:
	raise StandardError,"%s.build_twistDriver_hip >> failed to create stable roteate group: %s"%(self._strShortName,error)
    
    #=============================================================================
    #Create IK handle
    try:
	buffer = mc.ikHandle( sj=i_startRoot.mNode, ee=i_startEnd.mNode,
	                      solver = 'ikRPsolver', forceSolver = True,
	                      snapHandleFlagToggle=True )  
	
	#>>> Name
	str_baseName = self._partName + "_startTwistDriver"
	i_ik_handle = cgmMeta.cgmObject(buffer[0],setClass=True)
	i_ik_handle.addAttr('cgmName',str_baseName ,attrType='string',lock=True)    
	i_ik_handle.doName()
	i_ik_handle.parent = self._i_rigNull.mNode
	mc.pointConstraint(ml_blendJoints[1].mNode,i_ik_handle.mNode)
	
	ml_twistObjects.append(i_ik_handle)
	
	i_ik_effector = cgmMeta.cgmNode(buffer[1],setClass=True)
	i_ik_effector.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
	i_ik_effector.doName()
	
	cBuffer = mc.poleVectorConstraint(i_upLoc.mNode,i_ik_handle.mNode)#Polevector	
	rUtils.IKHandle_fixTwist(i_ik_handle.mNode)#Fix the wist
	
    except:
	raise StandardError,"%s.build_twistDriver_hip >> failed to create ik handle: %s"%(self._strShortName,error)
       
    #>>> Control	
    try:
	#>>> Connect in
	cgmMeta.cgmAttr(self._i_module.rigNull.settings,'in_worldIKStart').doConnectIn("%s.r%s"%(i_startRoot.mNode,self._jointOrientation[0]))
	self.connect_toRigGutsVis(ml_twistObjects)#connect to guts vis switches
    except StandardError,error:
	raise StandardError,"%s.build_twistDriver_hip >> finish failed| %s"%(self._strShortName,error)

#------------------------------------------------------------------------------------------------------------#    
def build_twistDriver_ankle(self):
    log.info(">>> %s.build_ankleTwistDriver >> "%self._strShortName + "="*75)
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("build_ankleTwistDriver>>bad self!")
	raise StandardError,error
    
    try:
	mi_controlIK = self._i_rigNull.controlIK
	mi_settings = self._i_rigNull.settings
	mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)
    except StandardError,error:
	raise StandardError,"%s.build_ankleTwistDriver >> failed to setup start attr | %s"%(self._strShortName,error)	

    try:
	str_baseName = self._partName + "_endTwistDriver"
	
	outVector = self._vectorOut
	upVector = self._vectorUp      
	ml_blendJoints = self._i_rigNull.blendJoints
	ml_ikJoints = self._i_rigNull.ikJoints	
	ml_rigHandleJoints = self._get_handleJoints()
	i_targetJoint = ml_rigHandleJoints[2]#This should be the ankle
	i_blendAnkle = ml_blendJoints[2]
	if i_targetJoint.cgmName != 'ankle':
	    raise StandardError,"%s.build_ankleTwistDriver >> target not ankle? | %s"%(self._strShortName,i_targetJoint.p_nameShort)	
	if i_blendAnkle.cgmName != 'ankle':
	    raise StandardError,"%s.build_ankleTwistDriver >> target not ankle? | %s"%(self._strShortName,i_blendAnkle.p_nameShort)	
	
	#Create joints
	#i_startAim = self.duplicate_moduleJoint(0,'startAim')
	#i_startEnd = self.duplicate_moduleJoint(0,'startAimEnd')
	i_startRoot = i_targetJoint.doDuplicate(incomingConnections = False)
	i_startRoot.addAttr('cgmName',str_baseName)
	i_startRoot.addAttr('cgmTypeModifier','twistDriver')
	i_startRoot.doName()
	i_startEnd = i_targetJoint.doDuplicate(incomingConnections = False)
	i_startEnd.addAttr('cgmTypeModifier','twistDriverEnd')
	i_startEnd.doName()    
	
	i_upLoc = i_startRoot.doLoc()
	self.connect_restoreJointLists()#Restore out lists
	
	i_startEnd.parent = i_startRoot.mNode
	ml_twistObjects = [i_startRoot,i_startEnd,i_upLoc]
	fl_dist = 25
	if self._direction == 'left':#if right, rotate the pivots
	    i_upLoc.__setattr__('t%s'%self._jointOrientation[2],fl_dist)	
	else:
	    i_upLoc.__setattr__('t%s'%self._jointOrientation[2],-fl_dist)
	    
	i_startEnd.__setattr__('t%s'%self._jointOrientation[0],-(fl_dist))
	
	#Move up
	#i_startEnd.__setattr__('t%s'%self._jointOrientation[0],-(fl_dist))
	#mc.move(upVector[0]*fl_dist,upVector[1]*(fl_dist),upVector[2]*fl_dist,i_startEnd.mNode,r=True, rpr = True, os = True, wd = True)	
	
	i_startRoot.parent = ml_ikJoints[1].mNode
	i_startRoot.rotateOrder = 0 #xyz
	mc.pointConstraint(i_blendAnkle.mNode,i_startRoot.mNode,mo=True)#constrain
	
    except StandardError,error:
	raise StandardError,"%s.build_ankleTwistDriver >> Failed joint creation,positioning | %s"%(self._strShortName,error)	    
    #=============================================================================
    #Create IK handle
    try:
	buffer = mc.ikHandle( sj=i_startRoot.mNode, ee=i_startEnd.mNode,
	                      solver = 'ikRPsolver', forceSolver = True,
	                      snapHandleFlagToggle=True )  
	
	#>>> Name
	i_ik_handle = cgmMeta.cgmObject(buffer[0],setClass=True)
	i_ik_handle.addAttr('cgmName',str_baseName ,attrType='string',lock=True)    
	i_ik_handle.doName()
	i_ik_handle.parent = self._i_rigNull.mNode
	mc.pointConstraint(ml_blendJoints[1].mNode,i_ik_handle.mNode)
	ml_twistObjects.append(i_ik_handle)
	    
	i_ik_effector = cgmMeta.cgmNode(buffer[1],setClass=True)
	i_ik_effector.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
	i_ik_effector.doName()
	
	cBuffer = mc.poleVectorConstraint(i_upLoc.mNode,i_ik_handle.mNode)#Polevector	
	rUtils.IKHandle_fixTwist(i_ik_handle.mNode)#Fix the wist
	
    except:
	raise StandardError,"%s.build_ankleTwistDriver >> failed to create ik handle: %s"%(self._strShortName,error)
       
    #>>> Control	
    try:
	i_rotGroup = mi_controlIK.doDuplicateTransform(False)
	i_rotGroup.addAttr('cgmType','ikEndRotGroup')
	i_rotGroup.doName()
	ml_twistObjects.append(i_rotGroup)
	i_upLoc.parent = i_rotGroup.mNode
	
	#invert the foot
	NodeF.argsToNodes("%s.rz = -%s.rz"%(i_rotGroup.p_nameShort,
	                                    mi_controlIK.p_nameShort)).doBuild()	
	
	i_rotGroup.parent = self._i_rigNull.pivot_ball.mNode
	
	#>>> Connect in
	mPlug_worldIKEndIn.doConnectIn("%s.r%s"%(i_startRoot.mNode,self._jointOrientation[0]))
	self.connect_toRigGutsVis(ml_twistObjects)#connect to guts vis switches
    except StandardError,error:
	raise StandardError,"%s.build_ankleTwistDriver >> finish failed| %s"%(self._strShortName,error)	
    
@cgmGeneral.Timer
def build_matchSystem(self):
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("leg.build_deformationRig>>bad self!")
	raise StandardError,error
    log.info(">>> %s.build_matchSystem >> "%self._strShortName + "="*75)    
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
    return True
    
@cgmGeneral.Timer
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
    build_foot(self)
    if buildTo.lower() == 'foot':return True
    build_FKIK(self)
    if buildTo.lower() == 'fkik':return True 
    build_deformation(self)
    if buildTo.lower() == 'deformation':return True 
    build_rig(self)
    if buildTo.lower() == 'rig':return True   
    build_matchSystem(self)
    if buildTo.lower() == 'match':return True 
    build_twistDriver_hip(self)
    if buildTo.lower() == 'hipDriver':return True   
    build_twistDriver_ankle(self)
    if buildTo.lower() == 'ankleDriver':return True       
    #build_deformation(self)
    #build_rig(self)    
    
    return True