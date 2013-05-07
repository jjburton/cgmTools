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
                     dictionary,
                     distance,
                     modules,
                     search,
                     curves,
                     )

#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['controlsFK','midIK','settings','foot'],
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
    
__l_jointAttrs__ = ['anchorJoints','rigJoints','influenceJoints','fkJoints','ikJoints','blendJoints']   

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
    
    if not self.isShaped():
	raise StandardError,"%s.build_rigSkeleton>>> needs shapes to build rig skeleton"%self._strShortName
    
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
	
	#>>FK chain
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
	
	#>>Blend chain
	#=====================================================================	
	ml_blendJoints = []
	for i_jnt in ml_fkJoints:
	    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
	    i_new.addAttr('cgmTypeModifier','blend',attrType='string',lock=True)
	    i_new.doName()
	    if ml_blendJoints:#if we have data, parent to last
		i_new.parent = ml_blendJoints[-1]
	    ml_blendJoints.append(i_new)	
	    
	#>>IK chain
	#=====================================================================	
	ml_ikJoints = []
	for i_jnt in ml_fkJoints:
	    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
	    i_new.addAttr('cgmTypeModifier','ik',attrType='string',lock=True)
	    i_new.doName()
	    if ml_ikJoints:#if we have data, parent to last
		i_new.parent = ml_ikJoints[-1]
	    ml_ikJoints.append(i_new)	
	
	#Do the toe
	i_toeJoint = ml_ikJoints[-1].doDuplicate()
	Snap.go(i_toeJoint, mi_toePivot.mNode,True,False)
	joints.doCopyJointOrient(ml_ikJoints[-1].mNode,i_toeJoint.mNode)
	i_toeJoint.addAttr('cgmName','toe',attrType='string',lock=True)	
	i_toeJoint.addAttr('cgmTypeModifier','ik',attrType='string',lock=True)
	i_toeJoint.doName()
	
	i_toeJoint.parent = ml_ikJoints[-1].mNode
	ml_ikJoints.append(i_toeJoint)	
	
		
	#>>Influence chain
	#=====================================================================		
	ml_influenceJoints = []
	for i_ctrl in self._i_templateNull.controlObjects:
	    if i_ctrl.getAttr('cgmName') in ['hip','knee','ankle']:
		if not i_ctrl.getMessage('handleJoint'):
		    raise StandardError,"%s.build_rigSkeleton>>> failed to find a handle joint from: '%s'"%(self._i_module.getShortName(),i_ctrl.getShortName())
		i_new = cgmMeta.cgmObject(mc.duplicate(i_ctrl.getMessage('handleJoint')[0],po=True,ic=True)[0])
		i_new.addAttr('cgmTypeModifier','influence',attrType='string',lock=True)
		i_new.parent = False
		i_new.doName()
		#if ml_influenceJoints:#if we have data, parent to last
		    #i_new.parent = ml_influenceJoints[-1]
		#else:i_new.parent = False
		i_new.rotateOrder = self._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations
		ml_influenceJoints.append(i_new)
	
	joints.doCopyJointOrient(ml_influenceJoints[-2].mNode,ml_influenceJoints[-1].mNode)
	    
	if len(ml_influenceJoints)!=3:
	    raise StandardError,"%s.build_rigSkeleton>>> don't have 3 influence joints: '%s'"%(self._i_module.getShortName(),ml_influenceJoints)
	    
	for i_jnt in ml_influenceJoints:
	    i_jnt.parent = False
	    

	#>>Anchor chain
	#=====================================================================	
	ml_anchors = []
	for i_jnt in ml_influenceJoints:
	    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
	    i_new.addAttr('cgmTypeModifier','anchor',attrType='string',lock=True)
	    i_new.parent = False
	    i_new.doName()

	    ml_anchors.append(i_new)	 
	    

	"""
	#>>Segment chain  
	#=====================================================================
	l_segmentJoints = mc.duplicate(self._l_skinJoints,po=True,ic=True,rc=True)
	ml_segmentJoints = []
	for i,j in enumerate(l_segmentJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','segment',attrType='string',lock=True)
	    i_j.doName()
	    l_rigJoints[i] = i_j.mNode
	    ml_segmentJoints.append(i_j)
	ml_segmentJoints[0].parent = False#Parent to deformGroup
	
	"""
	#>>> Store em all to our instance
	#=====================================================================	
	self._i_rigNull.connectChildrenNodes(ml_fkJoints,'fkJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_blendJoints,'blendJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_ikJoints,'ikJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'influenceJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'anchorJoints','module')
	
	log.info("anchorJoints>> %s"%self._i_rigNull.getMessage('anchorJoints',False))
	log.info("fkJoints>> %s"%self._i_rigNull.getMessage('fkJoints',False))
	log.info("ikJoints>> %s"%self._i_rigNull.getMessage('ikJoints',False))
	log.info("blendJoints>> %s"%self._i_rigNull.getMessage('blendJoints',False))
	log.info("influenceJoints>> %s"%self._i_rigNull.getMessage('influenceJoints',False))
	
    except StandardError,error:
	log.error("build_leg>>Build rig joints fail!")
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
    mi_settings = self._i_rigNull.settings
    
    mi_pivToe = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_toe'),cgmMeta.cgmObject)
    mi_pivHeel = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_heel'),cgmMeta.cgmObject)
    mi_pivBall = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ball'),cgmMeta.cgmObject)
    mi_pivInner = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_inner'),cgmMeta.cgmObject)
    mi_pivOuter = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_outer'),cgmMeta.cgmObject)
    
    for pivot in [mi_pivToe,mi_pivHeel,mi_pivBall,mi_pivInner,mi_pivOuter]:
	pivot.rotateOrder = 0
    
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    mi_handleIK = self._i_rigNull.handleIK
    
    for chain in [ml_fkJoints,ml_ikJoints,ml_blendJoints]:
	chain[0].parent = self._i_deformNull.mNode
    
    
    #=============================================================    
    try:#>>>Connect Blend Chain
	rUtils.connectBlendJointChain(ml_fkJoints,ml_ikJoints,ml_blendJoints,driver = "%s.state"%mi_settings.mNode,channels=['translate','rotate'])
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> blend connect error: %s"%(self._strShortName,error)
    
    
    #=============================================================    
    try:#>>>FK Length connector
	for i,i_jnt in enumerate(ml_fkJoints[:-1]):
	    rUtils.addJointLengthAttr(i_jnt,orientation=self._jointOrientation)
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> fk length connect error: %s"%(self._strShortName,error)
    
    
    #=============================================================    
    try:#>>>IK Chain Builds
	#Create ankle IK
	d_ankleReturn = rUtils.create_IKHandle(ml_ikJoints[0].mNode,ml_ikJoints[2].mNode,baseName=ml_ikJoints[2].cgmName)
	mi_ankleIKHandle = d_ankleReturn['mi_handle']
	
	#Create ankle IK
	d_ballReturn = rUtils.create_IKHandle(ml_ikJoints[2].mNode,ml_ikJoints[3].mNode,baseName=ml_ikJoints[3].cgmName)
	mi_ballIKHandle = d_ballReturn['mi_handle']
	
	#Create ankle IK
	d_toeReturn = rUtils.create_IKHandle(ml_ikJoints[3].mNode,ml_ikJoints[4].mNode,baseName=ml_ikJoints[4].cgmName)
	mi_toeIKHandle = d_toeReturn['mi_handle']

	#return {'mi_handle':i_ik_handle,'mi_effector':i_ik_effector,'mi_solver':i_ikSolver}
	
    except StandardError,error:
	raise StandardError,"%s.build_FKIK>>> IK Chains error: %s"%(self._strShortName,error)
    
    #=============================================================    
    #try:#>>>Foot setup
    mi_pivHeel.parent = mi_handleIK.mNode#heel to foot
    mi_pivOuter.parent = mi_pivHeel.mNode#outer to heel
    mi_pivInner.parent = mi_pivOuter.mNode#inner to outer
    
    mi_pivToe.parent = mi_pivInner.mNode#toe to inner
    mi_ballIKHandle.parent = mi_pivToe.mNode#ballIK to toe
    mi_toeIKHandle.parent = mi_pivToe.mNode#toeIK to toe
    mi_pivBall.parent = mi_pivToe.mNode#pivBall to toe
    mi_ankleIKHandle.parent = mi_pivBall.mNode#ankleIK to ball
    
    #Add driving attrs
    mi_plug_roll = cgmMeta.cgmAttr(mi_handleIK,'roll',attrType='float',defaultValue = 0,keyable = True)
    mi_plug_toeLift = cgmMeta.cgmAttr(mi_handleIK,'toeLift',attrType='float',defaultValue = 30,keyable = True)
    mi_plug_toeStaighten = cgmMeta.cgmAttr(mi_handleIK,'toeStaighten',attrType='float',defaultValue = 70,keyable = True)
    mi_plug_lean = cgmMeta.cgmAttr(mi_handleIK,'lean',attrType='float',defaultValue = 0,keyable = True)
    mi_plug_side = cgmMeta.cgmAttr(mi_handleIK,'side',attrType='float',defaultValue = 0,keyable = True)
    
    """
    $roll = l_ankle_ik_anim.roll;
    $toeLift = l_ankle_ik_anim.toeLift;
    $toeStraight = l_ankle_ik_anim.toeStaighten;
    $lean =l_ankle_ik_anim.lean;
    $side = l_ankle_ik_anim.side;
    
    
    l_heel_pivot_null.rotateX = min($roll,0);
    l_ball_pivot_null.rotateX = (linstep(0,$toeLift, $roll) * (1-(linstep( $toeLift, $toeStraight, $roll)))) * $roll;
    l_toe_pivot_null.rotateX = linstep($toeLift, $toeStraight,$roll) * $roll;

    """
    try:#heel setup
	#Add driven attrs
	mi_plug_heelClampResult = cgmMeta.cgmAttr(mi_handleIK,'result_clamp_heel',attrType='float',keyable = False,hidden=True)
	#mi_plug_heelResult = cgmMeta.cgmAttr(mi_handleIK,'result_heel',attrType='float',keyable = False,hidden=True)
	
	#Setup the heel roll
	#Clamp
	NodeF.argsToNodes("%s = clamp(%s,0,%s)"%(mi_plug_heelClampResult.p_combinedShortName,
	                                         mi_plug_roll.p_combinedShortName,
	                                         mi_plug_roll.p_combinedShortName)).doBuild()
	#Inversion
	#NodeF.argsToNodes("%s = -%s"%(mi_plug_heelResult.p_combinedShortName,mi_plug_heelClampResult.p_combinedShortName)).doBuild()
	mi_plug_heelClampResult.doConnectOut("%s.r%s"%(mi_pivHeel.mNode,self._jointOrientation[2].lower()))
    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> heel setup fail: %s"%error    
    
    #ball setup
    """
    Schleifer's
    ball_loc.rx = (linstep(0,$toeLift, $roll) * (1-(linstep( $toeLift, $toeStraight, $roll))) * $roll;
		    ballToeLiftRoll        md   ( pma   toeToeStraightRoll                    md  
		            1               4       3             2                            5
    """
    mi_plug_ballToeLiftRollResult = cgmMeta.cgmAttr(mi_handleIK,'result_range_ballToeLiftRoll',attrType='float',keyable = False,hidden=True)
    mi_plug_toeStraightRollResult = cgmMeta.cgmAttr(mi_handleIK,'result_range_toeStraightRoll',attrType='float',keyable = False,hidden=True)
    mi_plug_oneMinusToeResultResult = cgmMeta.cgmAttr(mi_handleIK,'result_pma_one_minus_toeStraitRollRange',attrType='float',keyable = False,hidden=True)
    mi_plug_ball_x_toeResult = cgmMeta.cgmAttr(mi_handleIK,'result_md_roll_x_toeResult',attrType='float',keyable = False,hidden=True)
    mi_plug_all_x_rollResult = cgmMeta.cgmAttr(mi_handleIK,'result_md_all_x_rollResult',attrType='float',keyable = False,hidden=True)
    
    arg1 = "%s = setRange(0,1,0,%s,%s)"%(mi_plug_ballToeLiftRollResult.p_combinedShortName,
                                         mi_plug_toeLift.p_combinedShortName,
                                         mi_plug_roll.p_combinedShortName)
    arg2 = "%s = setRange(0,1,%s,%s,%s)"%(mi_plug_toeStraightRollResult.p_combinedShortName,
                                          mi_plug_toeLift.p_combinedShortName,
                                          mi_plug_toeStaighten.p_combinedShortName,
                                          mi_plug_roll.p_combinedShortName)
    arg3 = "%s = 1 - %s"%(mi_plug_oneMinusToeResultResult.p_combinedShortName,
                          mi_plug_toeStraightRollResult.p_combinedShortName)
    
    arg4 = "%s = %s * %s"%(mi_plug_ball_x_toeResult.p_combinedShortName,
                           mi_plug_oneMinusToeResultResult.p_combinedShortName,
                           mi_plug_ballToeLiftRollResult.p_combinedShortName)
    
    arg5 = "%s = %s * %s"%(mi_plug_all_x_rollResult.p_combinedShortName,
                           mi_plug_ball_x_toeResult.p_combinedShortName,
                           mi_plug_roll.p_combinedShortName)
    
    for arg in [arg1,arg2,arg3,arg4,arg5]:
	NodeF.argsToNodes(arg).doBuild()
	
    mi_plug_all_x_rollResult.doConnectOut("%s.r%s"%(mi_pivBall.mNode,self._jointOrientation[2].lower()))
    
    #except StandardError,error:
	#raise StandardError,"verify_moduleRigToggles>> vis arg fail: %s"%error   
	
    #ball setup
    """
    Schleifer's
    toe_loc.rotateX = linstep($toeLift, $toeStraight,$roll) * $roll;
                          setRange                           md
			     1                                2
    """
    mi_plug_toeRangeResult = cgmMeta.cgmAttr(mi_handleIK,'result_range_toeLiftStraightRoll',attrType='float',keyable = False,hidden=True)
    mi_plug_toe_x_rollResult = cgmMeta.cgmAttr(mi_handleIK,'result_md_toeRange_x_roll',attrType='float',keyable = False,hidden=True)
    
    arg1 = "%s = setRange(0,1,%s,%s,%s)"%(mi_plug_toeRangeResult.p_combinedShortName,
                                         mi_plug_toeLift.p_combinedShortName,
                                         mi_plug_toeStaighten.p_combinedShortName,                                         
                                         mi_plug_roll.p_combinedShortName)
    arg2 = "%s = %s * %s"%(mi_plug_toe_x_rollResult.p_combinedShortName,
                                          mi_plug_toeRangeResult.p_combinedShortName,
                                          mi_plug_roll.p_combinedShortName)
    for arg in [arg1,arg2]:
	NodeF.argsToNodes(arg).doBuild()    
    
    mi_plug_toe_x_rollResult.doConnectOut("%s.r%s"%(mi_pivToe.mNode,self._jointOrientation[2].lower()))
    
	
	
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
    mi_midIK = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_midIK'),cgmMeta.cgmObject)
    mi_settings= cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_settings'),cgmMeta.cgmObject)
    mi_foot= cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_foot'),cgmMeta.cgmObject)
    mi_pivToe = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_toe'),cgmMeta.cgmObject)
    mi_pivHeel = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_heel'),cgmMeta.cgmObject)
    mi_pivBall = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ball'),cgmMeta.cgmObject)
    mi_pivInner = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_inner'),cgmMeta.cgmObject)
    mi_pivOuter = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_outer'),cgmMeta.cgmObject)
    ml_fkJoints = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('fkJoints'),cgmMeta.cgmObject)
    
    l_controlsAll = []
    #==================================================================
    try:#>>>> FK Segments
	if len( ml_controlsFK )<3:
	    raise StandardError,"%s.build_controls>>> Must have at least three fk controls"%self._strShortName	    
	
	#for i,i_obj in enumerate(ml_controlsFK[1:]):#parent
	    #i_obj.parent = ml_controlsFK[i].mNode
	ml_fkJoints[0].parent = self._i_deformNull.mNode
		
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
	i_IKEnd.masterGroup.parent = self._i_deformNull.mNode
	
	#i_loc.delete()#delete
	self._i_rigNull.connectChildNode(i_IKEnd,'handleIK','module')#connect
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
	i_IKmid.masterGroup.parent = self._i_deformNull.mNode
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
	mi_settings.addAttr('state',enumName = 'fk:ik', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False,lock=True)
	
	
    except StandardError,error:
	log.error("%s.build_controls>>> Build settings fail!"%self._strShortName)		
	raise StandardError,error
    
    #==================================================================
    #Connect all controls
    self._i_rigNull.connectChildrenNodes(l_controlsAll,'controlsAll')
    
    return True


def build_deformation(self):
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
    
    #>>>Get data
    ml_influenceJoints = self._i_rigNull.influenceJoints
    ml_controlsFK =  self._i_rigNull.controlsFK    
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_segmentJoints = self._i_rigNull.segmentJoints    
    ml_anchorJoints = self._i_rigNull.anchorJoints
    ml_segmentHandles = self._i_rigNull.segmentHandles
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    mi_handleIK = self._i_rigNull.handleIK
    

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
	drivers.append("%s.r%s"%(mi_handleIK.mNode,self._jointOrientation[0]))

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
	cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_handleIK.mNode,attrName,connectSourceToTarget = True)
	cgmMeta.cgmAttr(mi_handleIK.mNode,attrName,defaultValue = 1,keyable=True)
    
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
	mi_handleIK = self._i_rigNull.handleIK
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
	    if mi_parentRigNull.getMessage('handleIK'):
		ml_headDynParents.append( mi_parentRigNull.handleIK )	    
	    if mi_parentRigNull.getMessage('cog'):
		ml_headDynParents.append( mi_parentRigNull.cog )
	ml_headDynParents.extend(mi_handleIK.spacePivots)
	ml_headDynParents.append(self._i_masterControl)
	log.info(ml_headDynParents)
	log.info([i_obj.getShortName() for i_obj in ml_headDynParents])
	
	#Add our parents
	i_dynGroup = mi_handleIK.dynParentGroup
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
    ml_anchorJoints[-1].parent = mi_handleIK.mNode
        
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
    #attributes.doSetLockHideKeyableAttr(mi_handleIK.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
     

    #Final stuff
    self._i_rigNull.version = str(__version__)
    return True 


@r9General.Timer
def __build__(self, buildTo='',*args,**kws): 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.build_deformationRig>>bad self!")
	raise StandardError,error
    
    if not self.isShaped():
	build_shapes(self)
    if buildTo.lower() == 'shapes':return True
    if not self.isRigSkeletonized():
	build_rigSkeleton(self)  
    if buildTo.lower() == 'skeleton':return True
    build_controls(self)
    if buildTo.lower() == 'controls':return True    
    
    #build_deformation(self)
    #build_rig(self)    
    
    return True