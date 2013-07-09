"""
------------------------------------------
cgm.core.rigger: Limb.spine
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

spine rig builder

The basics of a module rig build are as follows:
1) Skeleton build - necessary joints for arig
2) Shapes build - build the control shapes for the rig
3) Deformation build - build the deformation parts of the rig
4) Rig build - finally connects everything
5) doBuild -- the final func to build the module rig

Necessary variables:
1) __version__
2) __d_controlShapes__
3) __l_jointAttrs__
================================================================
"""
__version__ = 0.07062013

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
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGeneral

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

#>>> Skeleton
#===================================================================
__l_jointAttrs__ = ['startAnchor','endAnchor','anchorJoints','rigJoints','influenceJoints','segmentJoints']   

@cgmGeneral.Timer
def __bindSkeletonSetup__(self):
    """
    TODO: Do I need to connect per joint overrides or will the final group setup get them?
    """
    try:
	if not self._cgmClass == 'JointFactory.go':
	    log.error("Not a JointFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.__bindSkeletonSetup__>>bad self!")
	raise StandardError,error
    
    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self._i_module.rigNull.skinJoints or []
    if not self._i_module.isSkeletonized():
	raise StandardError, "%s is not skeletonized yet."%self._strShortName
    
    try:#Reparent joints
	ml_skinJoints = self._i_module.rigNull.skinJoints
	
	for i,i_jnt in enumerate(ml_skinJoints[1:]):
	    if i_jnt.hasAttr('cgmName'):
		if i_jnt.cgmName == 'spine_1':
		    i_jnt.parent = ml_skinJoints[0].mNode
	
	ml_skinJoints[-2].parent = ml_skinJoints[0].mNode #Sternum to pelvis
	ml_skinJoints[-1].parent = ml_skinJoints[0].mNode #Shoulders to pelvis
	
	"""if i_jnt.cgmName in self._l_coreNames:
		i_jnt.parent = ml_skinJoints[0].mNode"""		

    except StandardError,error:
	log.error("build_spine>>__bindSkeletonSetup__ fail!")
	raise StandardError,error   

@cgmGeneral.Timer
def build_rigSkeleton(self):
    """
    TODO: Do I need to connect per joint overrides or will the final group setup get them?
    """
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.build_deformationRig>>bad self!")
	raise StandardError,error
    
    #>>>Create joint chains
    #=============================================================    
    try:
	#>>Segment chain
	ml_skinJoints = self._ml_skinJoints
	l_segmentJoints = mc.duplicate(self._l_skinJoints[1:-1],po=True,ic=True,rc=True)
	ml_segmentJoints = []
	for i,j in enumerate(l_segmentJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','segment',attrType='string')
	    i_j.doName()
	    l_segmentJoints[i] = i_j.mNode
	    ml_segmentJoints.append(i_j)
	    if i == 0:
		ml_segmentJoints[0].parent = False#Parent to world
	    else:
		ml_segmentJoints[i].parent = ml_segmentJoints[i-1].mNode#Parent to Last
	
	#>>Deformation chain    
	l_rigJoints = mc.duplicate(self._l_skinJoints,po=True,ic=True,rc=True)
	ml_rigJoints = []
	for i,j in enumerate(l_rigJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
	    i_j.doName()
	    l_rigJoints[i] = i_j.mNode
	    ml_rigJoints.append(i_j)
	ml_rigJoints[0].parent = self._i_deformNull.mNode#Parent to deformGroup
	
	#>>Anchor chain
	ml_anchors = []
	i_rootJnt = cgmMeta.cgmObject(mc.duplicate(self._l_skinJoints[0],po=True,ic=True,rc=True)[0])
	#i_rootJnt = self._ml_skinJoints[0].doDuplicateTransform(False)
	
	i_rootJnt.addAttr('cgmType','anchor',attrType='string',lock=True)
	i_rootJnt.doName()
	i_rootJnt.parent = False	
	ml_anchors.append(i_rootJnt)
	
	#Start
	i_startJnt = cgmMeta.cgmObject(mc.duplicate(self._l_skinJoints[1],po=True,ic=True,rc=True)[0])
	#i_startJnt = self._ml_skinJoints[1].doDuplicateTransform(False)	
	i_startJnt.addAttr('cgmType','anchor',attrType='string',lock=True)
	i_startJnt.doName()
	i_startJnt.parent = False
	ml_anchors.append(i_startJnt)
	
	#End
	l_endJoints = mc.duplicate(self._l_skinJoints[-2],po=True,ic=True,rc=True)
	i_endJnt = cgmMeta.cgmObject(l_endJoints[0])
	#i_endJnt = self._ml_skinJoints[-2].doDuplicateTransform(False)
	for j in l_endJoints:
	    #for i_j in [i_endJnt]:
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmType','anchor',attrType='string',lock=True)
	    i_j.doName()
	i_endJnt.parent = False
	ml_anchors.append(i_endJnt)
	for i_obj in ml_anchors:
	    i_obj.rotateOrder = 2#<<<<<<<<<<<<<<<<This would have to change for other orientations
	
	#Influence chain for influencing the surface
	ml_influenceJoints = []
	for i_jnt in self._ml_skinJoints[1:-1]:
	    if i_jnt.hasAttr('cgmName') and i_jnt.cgmName in self._l_coreNames:
		i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
		i_new.addAttr('cgmType','influenceJoint',attrType='string',lock=True)
		i_new.parent = False
		i_new.doName()
		if ml_influenceJoints:#if we have data, parent to last
		    i_new.parent = ml_influenceJoints[-1]
		else:i_new.parent = False
		i_new.rotateOrder = 'zxy'#<<<<<<<<<<<<<<<<This would have to change for other orientations
		ml_influenceJoints.append(i_new)
	for i_jnt in ml_influenceJoints:
	    i_jnt.parent = False		
	#>>> Store em all to our instance
	self._i_rigNull.connectChildNode(i_startJnt,'startAnchor','rigNull')
	self._i_rigNull.connectChildNode(i_endJnt,'endAnchor','rigNull')	
	self._i_rigNull.connectChildrenNodes(ml_anchors,'anchorJoints','rigNull')
	self._i_rigNull.connectChildrenNodes(ml_rigJoints,'rigJoints','rigNull')
	self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'influenceJoints','rigNull')
	self._i_rigNull.connectChildrenNodes(ml_segmentJoints,'segmentJoints','rigNull')
	self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints')#Restore our list since duplication extendes message attrs
	
    except StandardError,error:
	log.error("build_spine>>Build rig joints fail!")
	raise StandardError,error   
    
    ml_jointsToConnect = [i_startJnt,i_endJnt]
    ml_jointsToConnect.extend(ml_anchors)
    ml_jointsToConnect.extend(ml_rigJoints)
    ml_jointsToConnect.extend(ml_influenceJoints)
    ml_jointsToConnect.extend(ml_segmentJoints)

    for i_jnt in ml_jointsToConnect:
	i_jnt.overrideEnabled = 1		
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    

    if self._ml_skinJoints != self._i_rigNull.skinJoints:
	log.error("Stored skin joints don't equal buffered")
#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['cog','hips','segmentFK','segmentIK','handleIK']}
@cgmGeneral.Timer
def build_shapes(self):
    """
    Rotate orders
    hips = 3
    """ 
    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.build_rig>>bad self!")
	raise StandardError,error
    
    #>>>Build our Shapes
    #=============================================================
    mShapeCast.go(self._i_module,['cog','hips','torsoIK','segmentFK'],storageInstance=self)#This will store controls to a dict called    
    log.debug(self._md_controlShapes)
    #except StandardError,error:
	#log.error("build_spine>>Build shapes fail!")
	#raise StandardError,error    
    
def build_controls(self):
    """
    Rotate orders
    hips = 3
    """ 
    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.build_rig>>bad self!")
	raise StandardError,error
    
    if not self.isShaped():	
	raise StandardError,"%s.build_controls>>> No shapes found connected"%(self._strShortName)
	
    #>>> Get some special pivot xforms
    ml_segmentJoints = self._i_rigNull.segmentJoints 
    l_segmentJoints  = [i_jnt.mNode for i_jnt in ml_segmentJoints] 
    tmpCurve = curves.curveFromObjList(l_segmentJoints)
    hipPivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.15))
    shouldersPivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.8))
    log.debug("hipPivotPos : %s"%hipPivotPos)
    log.debug("shouldersPivotPos : %s"%shouldersPivotPos)   
    mc.delete(tmpCurve)
    
    #>>> Get our shapes
    #__d_controlShapes__ = {'shape':['cog','hips','segmentFK','segmentIK','handleIK']}
    
    mi_cogShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_cog'),cgmMeta.cgmObject)
    mi_hipsShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_hips'),cgmMeta.cgmObject)
    ml_segmentFKShapes = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('shape_segmentFK'),cgmMeta.cgmObject)
    ml_segmentIKShapes = cgmMeta.validateObjListArg(self._i_rigNull.getMessage('shape_segmentIK'),cgmMeta.cgmObject)
    mi_handleIKShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_handleIK'),cgmMeta.cgmObject)
    
    log.info('>'*50)
    log.info(mi_handleIKShape)
    log.info(mi_handleIKShape.mNode)
    
    l_controlsAll = []#we'll append to this list and connect them all at the end 
    #>>>Build our controls
    #=============================================================
    #>>>Set up structure
    try:#>>>> Cog
	i_cog = mi_cogShape
	log.info(i_cog)
	d_buffer = mControlFactory.registerControl(i_cog.mNode,addExtraGroups = True,addConstraintGroup=True,
	                                           freezeAll=True,makeAimable=True,autoLockNHide=True,
	                                           controlType='cog')
	i_cog = d_buffer['instance']
	l_controlsAll.append(i_cog)
	self._i_rigNull.connectChildNode(i_cog,'cog','rigNull')#Store
	log.info(i_cog)
	log.info(i_cog.masterGroup)
	i_cog.masterGroup.parent = self._i_deformNull.mNode
	#Set aims
	
    except StandardError,error:
	log.error("build_spine>>Build cog fail!")
	raise StandardError,error
    
    #==================================================================
    try:#>>>> FK Segments
	ml_segmentsFK = ml_segmentFKShapes
	for i,i_obj in enumerate(ml_segmentsFK[1:]):#parent
	    i_obj.parent = ml_segmentsFK[i].mNode
	ml_segmentsFK[0].parent = i_cog.mNode
	for i,i_obj in enumerate(ml_segmentsFK):
	    if i == 0:
		i_loc = ml_segmentsFK[i].doLoc()
		mc.move (hipPivotPos[0],hipPivotPos[1],hipPivotPos[2], i_loc.mNode)		
		d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,setRotateOrder=5,
		                                           copyPivot=i_loc.mNode,typeModifier='fk') 
		i_loc.delete()
		
	    else:
		d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,setRotateOrder=5,typeModifier='fk',) 
	    i_obj = d_buffer['instance']
	self._i_rigNull.connectChildrenNodes(ml_segmentsFK,'controlsFK','rigNull')
	l_controlsAll.extend(ml_segmentsFK)	
    
    except StandardError,error:
	log.error("build_spine>>Build fk fail!")
	raise StandardError,error
        
    #==================================================================    
    try:#>>>> IK Segments
	ml_segmentsIK = ml_segmentIKShapes
	
	for i_obj in ml_segmentsIK:
	    d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='ik',
		                                       setRotateOrder=2)       
	    i_obj = d_buffer['instance']
	    i_obj.masterGroup.parent = self._i_deformNull.mNode
	self._i_rigNull.connectChildrenNodes(ml_segmentsIK,'segmentHandles','rigNull')
	l_controlsAll.extend(ml_segmentsIK)	
	
	
    except StandardError,error:
	log.error("build_spine>>Build ik handle fail!")
	raise StandardError,error
    
    #==================================================================
    try:#>>>> IK Handle
	i_IKEnd = mi_handleIKShape
	i_IKEnd.parent = i_cog.mNode
	i_loc = i_IKEnd.doLoc()#Make loc for a new transform
	#i_loc.rx = i_loc.rx + 90#offset   
	mc.move (shouldersPivotPos[0],shouldersPivotPos[1],shouldersPivotPos[2], i_loc.mNode)
	
	d_buffer = mControlFactory.registerControl(i_IKEnd,copyTransform = i_loc.mNode,
	                                           typeModifier = 'ik',addSpacePivots = 2, addDynParentGroup = True, addConstraintGroup=True,
	                                           makeAimable = True,setRotateOrder=4)
	i_IKEnd = d_buffer['instance']	
		
	i_loc.delete()#delete
	self._i_rigNull.connectChildNode(i_IKEnd,'handleIK','rigNull')#connect
	l_controlsAll.append(i_IKEnd)	

	#Set aims
	i_IKEnd.axisAim = self._jointOrientation[1]+'-'
	i_IKEnd.axisUp = self._jointOrientation[0]+'+'	
	
    except StandardError,error:
	log.error("build_spine>>Build ik handle fail!")
	raise StandardError,error   
      
    #==================================================================
    try:#>>>> Hips
	i_hips = mi_hipsShape
	i_hips.parent = i_cog.mNode#parent
	i_loc = i_hips.doLoc()
	mc.move (hipPivotPos[0],hipPivotPos[1],hipPivotPos[2], i_loc.mNode)
	
	d_buffer =  mControlFactory.registerControl(i_hips,addSpacePivots = 2, addDynParentGroup = True, addConstraintGroup=True,
	                                            makeAimable = True,copyPivot=i_loc.mNode,setRotateOrder=5)
	self._i_rigNull.connectChildNode(i_hips,'hips','rigNull')
	i_hips = d_buffer['instance']
	i_loc.delete()
	l_controlsAll.append(i_hips)	
	
	#Set aims
	i_hips.axisAim = self._jointOrientation[1]+'-'
	i_hips.axisUp = self._jointOrientation[0]+'+'	
	
    except StandardError,error:
	log.error("build_spine>>Build hips fail!")
	raise StandardError,error
    
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
	log.error("spine.build_deformationRig>>bad self!")
	raise StandardError,error
    
    #>>>Get data
    ml_influenceJoints = self._i_rigNull.influenceJoints
    ml_controlsFK =  self._i_rigNull.controlsFK    
    ml_segmentJoints = self._i_rigNull.segmentJoints
    ml_anchorJoints = self._i_rigNull.anchorJoints
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_segmentHandles = self._i_rigNull.segmentHandles
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    mi_hips = self._i_rigNull.hips
    mi_handleIK = self._i_rigNull.handleIK
    mi_cog = self._i_rigNull.cog
    
    #>>>Create a constraint surface for the influence joints
    #====================================================================================    

    #Control Segment
    #====================================================================================
    try:#Control Segment
	log.debug(self._jointOrientation)
	capAim = self._jointOrientation[0].capitalize()
	log.debug("capAim: %s"%capAim)
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
	                                             additiveScaleSetup=True,
	                                             connectAdditiveScale=True,
	                                             moduleInstance=self._i_module)
	
	i_curve = curveSegmentReturn['mi_segmentCurve']
	self._i_rigNull.connectChildrenNodes([i_curve],'segmentCurves','rigNull')	
	i_curve.segmentGroup.parent = self._i_rigNull.mNode
	"""
	for o in  [ml_influenceJoints[1].mNode,
	           curveSegmentReturn['mi_segmentCurve'].mNode,
	           ml_influenceJoints[0].mNode,
	           ml_influenceJoints[-1].mNode,
	           ml_segmentHandles[1].mNode,
	           self._partName,
	           self._jointOrientation]:
	    log.debug(o)
	return"""
	
	midReturn = rUtils.addCGMSegmentSubControl(ml_influenceJoints[1].mNode,
	                                           segmentCurve = i_curve,
	                                           baseParent=ml_influenceJoints[0],
	                                           endParent=ml_influenceJoints[-1],
	                                           midControls=ml_segmentHandles[1],
	                                           baseName=self._partName,
	                                           controlTwistAxis =  'r'+self._jointOrientation[0],
	                                           orientation=self._jointOrientation)
	
	for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
	    i_grp.parent = mi_cog.mNode
	    
    except StandardError,error:
	log.error("build_spine>>Control Segment build fail")
	raise StandardError,error
    
    
    try:#Setup top twist driver
	#Create an fk additive attributes
	str_curve = curveSegmentReturn['mi_segmentCurve'].getShortName()
	fk_drivers = ["%s.r%s"%(i_obj.mNode,self._jointOrientation[0]) for i_obj in ml_controlsFK]
	NodeF.createAverageNode(fk_drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"fkTwistSum"],1)#Raw fk twist
	
	try:NodeF.argsToNodes("%s.fkTwistResult = %s.fkTwistSum * %s.fkTwistInfluence"%(str_curve,str_curve,str_curve)).doBuild()
	except StandardError,error:
	    raise StandardError,"verify_moduleRigToggles>> fkwistResult node arg fail: %s"%error	
	
	
	drivers = ["%s.%s"%(curveSegmentReturn['mi_segmentCurve'].mNode,"fkTwistResult")]
	drivers.append("%s.r%s"%(ml_segmentHandles[-1].mNode,self._jointOrientation[0]))
	drivers.append("%s.r%s"%(mi_handleIK.mNode,self._jointOrientation[0]))

	NodeF.createAverageNode(drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistEnd"],1)
	

    except StandardError,error:
	log.error("build_spine>>Top Twist driver fail")
	raise StandardError,error
    
    try:#Setup bottom twist driver
	log.debug("%s.r%s"%(ml_segmentHandles[0].getShortName(),self._jointOrientation[0]))
	log.debug("%s.r%s"%(mi_hips.getShortName(),self._jointOrientation[0]))
	drivers = ["%s.r%s"%(ml_segmentHandles[0].mNode,self._jointOrientation[0])]
	drivers.append("%s.r%s"%(mi_hips.mNode,self._jointOrientation[0]))

	log.debug("driven: %s"%("%s.r%s"%(ml_anchorJoints[1].mNode,self._jointOrientation[0])))
	NodeF.createAverageNode(drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistStart"],1)
    
    except StandardError,error:
	log.error("build_spine>>Bottom Twist driver fail")
	raise StandardError,error
    
    try:#Do a few attribute connections
	#Push squash and stretch multipliers to cog
	i_buffer = i_curve.scaleBuffer
	
	for k in i_buffer.d_indexToAttr.keys():
	    attrName = 'spine_%s'%k
	    cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_cog.mNode,attrName,connectSourceToTarget = True)
	    cgmMeta.cgmAttr(mi_cog.mNode,attrName,defaultValue = 1)
	    cgmMeta.cgmAttr('cog_anim',attrName, keyable =True, lock = False)    
	
	cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(mi_cog.mNode,connectSourceToTarget=True)
	cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(mi_cog.mNode,connectSourceToTarget=True)
	
    except StandardError,error:
	log.error("build_spine>>Attribute connection fail")
	raise StandardError,error
    
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
	log.error("spine.build_deformationRig>>bad self!")
	raise StandardError,error
    
    try:#>>>Get data
	orientation = modules.returnSettingsData('jointOrientation')
	
	mi_segmentCurve = self._i_rigNull.segmentCurves[0]
	mi_segmentAnchorStart = mi_segmentCurve.anchorStart
	mi_segmentAnchorEnd = mi_segmentCurve.anchorEnd
	mi_segmentAttachStart = mi_segmentCurve.attachStart
	mi_segmentAttachEnd = mi_segmentCurve.attachEnd 
	mi_distanceBuffer = mi_segmentCurve.scaleBuffer
    
	log.debug("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
	log.debug("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
	log.debug("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
	log.debug("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
	log.debug("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)
	
	ml_influenceJoints = self._i_rigNull.influenceJoints
	ml_segmentJoints = mi_segmentCurve.drivenJoints
	ml_segmentSplineJoints = mi_segmentCurve.driverJoints
	
	ml_anchorJoints = self._i_rigNull.anchorJoints
	ml_rigJoints = self._i_rigNull.rigJoints
	ml_segmentHandles = self._i_rigNull.segmentHandles
	aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
	mi_hips = self._i_rigNull.hips
	mi_handleIK = self._i_rigNull.handleIK
	ml_controlsFK =  self._i_rigNull.controlsFK    
	mi_cog = self._i_rigNull.cog
	
    except StandardError,error:
	log.error("spine.build_rig>> Gather data fail!")
	raise StandardError,error
    
    #Dynamic parent groups
    #====================================================================================
    try:#>>>> Shoulder dynamicParent
	#Build our dynamic groups
	ml_shoulderDynParents = [ml_controlsFK[-1], mi_cog,]
	ml_shoulderDynParents.extend(mi_handleIK.spacePivots)
	ml_shoulderDynParents.append(self._i_masterControl)
	log.debug(ml_shoulderDynParents)
	log.debug([i_obj.getShortName() for i_obj in ml_shoulderDynParents])
	
	#Add our parents
	i_dynGroup = mi_handleIK.dynParentGroup
	for o in ml_shoulderDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()
    except StandardError,error:
	log.error("spine.build_rig>> shoulder dynamic parent setup fail!")
	raise StandardError,error
    
    try:#>>>> Hips dynamicParent
	ml_hipsDynParents = [mi_cog]
	ml_hipsDynParents.extend(mi_hips.spacePivots)
	ml_hipsDynParents.append(self._i_masterControl)
	log.debug(ml_hipsDynParents)
	log.debug([i_obj.getShortName() for i_obj in ml_hipsDynParents])  
	
	#Add our parents
	i_dynGroup = mi_hips.dynParentGroup
	for o in ml_hipsDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()    
    except StandardError,error:
	log.error("spine.build_rig>> hips dynamic parent setup fail!")
	raise StandardError,error
    
    #FK influence on twist from the space it's in
    try:
	str_curve = mi_segmentCurve.getShortName()
	NodeF.argsToNodes("%s.fkTwistInfluence = if %s.space == 0:1 else 0"%(str_curve,mi_handleIK.getShortName())).doBuild()
    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> fkTwistInfluencecond node arg fail: %s"%error    
    
    #Parent and constrain joints
    #====================================================================================
    ml_segmentJoints[0].parent = mi_cog.mNode#Segment to cog
    ml_segmentSplineJoints[0].parent = mi_cog.mNode#Spline Segment to cog
    
    #Put the start and end controls in the heirarchy
    mc.parent(ml_segmentHandles[0].parent,mi_segmentAttachStart.mNode)
    mc.parent(ml_segmentHandles[-1].parent,mi_segmentAttachEnd.mNode)
    
    #parent the segment anchors
    #mi_segmentAnchorStart.parent = ml_anchorJoints[1].mNode#Pelvis
    
    
    mi_segmentAnchorStart.parent = mi_cog.mNode#Anchor start to cog
    mc.parentConstraint(ml_rigJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#constrain
    mc.scaleConstraint(ml_rigJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#Constrain
    
    mi_segmentAnchorEnd.parent = mi_cog.mNode#Anchor end to cog
    mc.parentConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
    mc.scaleConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
    
    #method 1
    ml_rigJoints[-2].parent = ml_anchorJoints[-1].mNode
    ml_rigJoints[-1].parent = mi_handleIK.mNode
    
    #mi_segmentAnchorStart.parent = ml_anchorJoints[1].mNode#Pelvis
    #mi_segmentAnchorEnd.parent = ml_anchorJoints[-1].mNode#Sternum
    #mc.parentConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
    #mc.scaleConstraint(ml_rigJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)
    
    ##method 2
    #ml_rigJoints[-2].parent = mi_cog.mNode
    #mc.parentConstraint(mi_handleIK.mNode,ml_rigJoints[-2].mNode,maintainOffset=True)
    #mc.scaleConstraint(mi_handleIK.mNode,ml_rigJoints[-2].mNode,maintainOffset=True)    
    
    #Parent the influence joints
    ml_influenceJoints[0].parent = ml_segmentHandles[0].mNode
    ml_influenceJoints[-1].parent = ml_segmentHandles[-1].mNode
    
    #Parent anchors to controls
    ml_anchorJoints[0].parent = mi_hips.mNode#parent pelvis anchor to hips
    ml_anchorJoints[1].parent = mi_hips.mNode
    ml_anchorJoints[-1].parent = mi_handleIK.mNode
    	    
    #Connect rig pelvis to anchor pelvis
    mc.pointConstraint(ml_anchorJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)
    mc.orientConstraint(ml_anchorJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)
    mc.scaleConstraint(ml_anchorJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)#Maybe hips    
    
    l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
    for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
	#Don't try scale constraints in here, they're not viable
        attachJoint = distance.returnClosestObject(i_jnt.mNode,l_rigJoints)
	log.debug("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
        pntConstBuffer = mc.pointConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
        orConstBuffer = mc.orientConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
        mc.connectAttr((i_jnt.mNode+'.s'),(attachJoint+'.s'))
	
    mc.pointConstraint(ml_anchorJoints[-1].mNode,ml_rigJoints[-2].mNode,maintainOffset=False)
    mc.orientConstraint(ml_anchorJoints[-1].mNode,ml_rigJoints[-2].mNode,maintainOffset=False)
    #mc.scaleConstraint(ml_anchorJoints[-1].mNode,ml_rigJoints[-2].mNode,maintainOffset=True)
    mc.connectAttr((ml_anchorJoints[-1].mNode+'.s'),(ml_rigJoints[-2].mNode+'.s'))
    
    #Set up heirarchy, connect master scale
    #====================================================================================
    #>>>Connect master scale
    cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(self._i_masterControl.mNode,'scaleY'))    
    
    #Vis Network, lock and hide
    #====================================================================================
    #Cog control fk hide
    
    #Setup Cog vis control for fk controls
    mi_cog.addAttr('visFK', defaultValue = 1, attrType = 'bool',keyable = False,hidden = False, initialValue = 1)
    cgmMeta.cgmAttr( ml_controlsFK[0].mNode,'visibility').doConnectIn('%s.%s'%(mi_cog.mNode,'visFK'))    
    
    #Segment handles need to lock
    #for i_obj in ml_segmentHandles:
	#attributes.doSetLockHideKeyableAttr(i_obj.mNode,lock=True, visible=False, keyable=False, channels=['s%s'%orientation[1],'s%s'%orientation[2]])
    
    #Lock and hide hips and shoulders
    attributes.doSetLockHideKeyableAttr(mi_hips.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
    attributes.doSetLockHideKeyableAttr(mi_handleIK.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
     
    #Connect our last segment to the sternum
    mc.connectAttr((ml_segmentHandles[-1].mNode+'.s%s'%self._jointOrientation[1]),(ml_rigJoints[-2].mNode+'.s%s'%self._jointOrientation[1]))    
    mc.connectAttr((ml_segmentHandles[-1].mNode+'.s%s'%self._jointOrientation[2]),(ml_rigJoints[-2].mNode+'.s%s'%self._jointOrientation[2]))    
    
    #Set up some defaults
    #====================================================================================
    mPlug_segStart = cgmMeta.cgmAttr(ml_segmentHandles[0],'followRoot')
    mPlug_segStart.p_defaultValue = .5
    mPlug_segStart.value = .5
    mPlug_segMid = cgmMeta.cgmAttr(ml_segmentHandles[1],'linearSplineFollow')
    mPlug_segMid.p_defaultValue = 1
    mPlug_segMid.value = 1
    mPlug_segMidAim = cgmMeta.cgmAttr(ml_segmentHandles[1],'startEndAim')
    mPlug_segMidAim.p_defaultValue = 1
    mPlug_segMidAim.value = 1    
    mPlug_segEnd = cgmMeta.cgmAttr(ml_segmentHandles[-1],'followRoot')
    mPlug_segEnd.p_defaultValue = .5
    mPlug_segEnd.value = .5
    
    #Final stuff
    self._i_rigNull.version = str(__version__)
    return True 

@cgmGeneral.Timer
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
    build_deformation(self)
    if buildTo.lower() == 'deformation':return True    
    build_rig(self)    
            
    return True


#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================

def build_rigOLDSurface(self):
    """
    Rotate orders
    hips = 3
    """ 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.build_deformationRig>>bad self!")
	raise StandardError,error
    
    #>>>Get data
    ml_influenceJoints = self._i_rigNull.influenceJoints
    ml_segmentJoints = self._i_rigNull.segmentJoints
    ml_anchorJoints = self._i_rigNull.anchorJoints
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_segmentHandles = self._i_rigNull.segmentHandles
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    mi_hips = self._i_rigNull.hips
    mi_handleIK = self._i_rigNull.handleIK
    ml_controlsFK =  self._i_rigNull.controlsFK    
    
    #Mid follow Setup
    #====================================================================================  
    dist = distance.returnDistanceBetweenObjects(ml_influenceJoints[-2].mNode,ml_influenceJoints[-1].mNode)/1    
    #>>>Create some locs
    i_midAim = ml_influenceJoints[1].doLoc()
    i_midAim.addAttr('cgmTypeModifier','midAim')
    i_midAim.doName()
    i_midAim.overrideEnabled = 1
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'visLocs',lock=False).doConnectOut("%s.%s"%(i_midAim.mNode,'overrideVisibility'))
    
    i_midPoint = ml_influenceJoints[1].doLoc()#midPoint
    i_midPoint.addAttr('cgmTypeModifier','midPoint')
    i_midPoint.doName()
    i_midPoint.overrideEnabled = 1
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'visLocs',lock=False).doConnectOut("%s.%s"%(i_midPoint.mNode,'overrideVisibility'))
    
    #Mid up constraint
    i_midUp = ml_influenceJoints[1].doLoc()#midUp
    i_midUp.addAttr('cgmTypeModifier','midUp')
    i_midUp.doName()
    i_midUp.parent = ml_controlsFK[1].mNode
    attributes.doSetAttr(i_midUp.mNode,'t%s'%self._jointOrientation[1],dist)
    i_midUp.parent = ml_controlsFK[1].mNode
    i_midUp.overrideEnabled = 1
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'visLocs',lock=False).doConnectOut("%s.%s"%(i_midUp.mNode,'overrideVisibility'))
    constBuffer = mc.parentConstraint([mi_handleIK.mNode,ml_controlsFK[1].mNode,ml_controlsFK[-1].mNode],
                                      i_midUp.mNode,maintainOffset=True)[0]
    i_midUpConstraint = cgmMeta.cgmNode(constBuffer)
    
    
    #Top Anchor
    i_topAnchorAttachPivot = ml_influenceJoints[1].doLoc()#Top Anchor
    i_topAnchorAttachPivot.addAttr('cgmTypeModifier','sternumAnchor')
    i_topAnchorAttachPivot.doName()
    i_topAnchorAttachPivot.parent =  ml_segmentHandles[-1].mNode
    mc.move(0,0,dist/2,i_topAnchorAttachPivot.mNode,os=True, r=True)
    i_topAnchorAttachPivot.overrideEnabled = 1
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'visLocs',lock=False).doConnectOut("%s.%s"%(i_topAnchorAttachPivot.mNode,'overrideVisibility'))
    
    #Bottom Anchor 
    i_bottomAnchorAttachPivot = ml_influenceJoints[1].doLoc()
    i_bottomAnchorAttachPivot.addAttr('cgmTypeModifier','spine1Anchor')
    i_bottomAnchorAttachPivot.doName()
    i_bottomAnchorAttachPivot.parent =  ml_anchorJoints[0].mNode    
    mc.move(0,0,-dist/2,i_bottomAnchorAttachPivot.mNode,os=True, r=True)
    i_bottomAnchorAttachPivot.overrideEnabled = 1
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'visLocs',lock=False).doConnectOut("%s.%s"%(i_bottomAnchorAttachPivot.mNode,'overrideVisibility'))
    
    #Mid point constraint
    #i_topAnchorAttachPivot.mNode
    constBuffer = mc.pointConstraint([ml_anchorJoints[0].mNode,
                                      ml_anchorJoints[-1].mNode],
                                      i_midAim.mNode,maintainOffset=True)[0]
    #targetWeights = mc.parentConstraint(i_midPointConstraint.mNode,q=True, weightAliasList=True)      
    #mc.setAttr(('%s.%s' % (i_midPointConstraint.mNode,targetWeights[0])),.5 )
    #mc.setAttr(('%s.%s' % (i_midPointConstraint.mNode,targetWeights[1])),1.0 )
    
    #Aim loc constraint
    i_midPointConstraint = cgmMeta.cgmNode(mc.pointConstraint([i_topAnchorAttachPivot.mNode,
                                                               ml_anchorJoints[1].mNode,
                                                               ml_anchorJoints[-1].mNode],
                                                              i_midPoint.mNode,maintainOffset=True)[0])
    
    #targetWeights = mc.parentConstraint(i_midAimConstraint.mNode,q=True, weightAliasList=True)      
    #mc.setAttr(('%s.%s' % (i_midAimConstraint.mNode,targetWeights[0])),.1)
    #mc.setAttr(('%s.%s' % (i_midAimConstraint.mNode,targetWeights[1])),1.0 )  
    

    #Create an point/aim group
    i_midFollowGrp = cgmMeta.cgmObject( self._i_rigNull.segmentHandles[1].doGroup(True),setClass=True)
    i_midFollowGrp.addAttr('cgmTypeModifier','follow')
    i_midFollowGrp.doName()
    i_midFollowGrp.rotateOrder = 0
    
    i_midFollowPointConstraint = cgmMeta.cgmNode(mc.pointConstraint([i_midPoint.mNode],
                                                                    i_midFollowGrp.mNode,maintainOffset=True)[0])
    
    closestJoint = distance.returnClosestObject(i_midFollowGrp.mNode,[i_jnt.mNode for i_jnt in ml_segmentJoints])
    upLoc = cgmMeta.cgmObject(closestJoint).rotateUpGroup.upLoc.mNode
    i_midUpGroup = cgmMeta.cgmObject(closestJoint).rotateUpGroup
    #Twist setup start
    #grab driver
    driverNodeAttr = attributes.returnDriverAttribute("%s.r%s"%(i_midUpGroup.mNode,self._jointOrientation[0]),True)    
    #get driven
    rotDriven = attributes.returnDrivenAttribute(driverNodeAttr,True)
    
    rotPlug = attributes.doBreakConnection(i_midUpGroup.mNode,
                                           'r%s'%self._jointOrientation[0])
    #Get the driven so that we can bridge to them 
    log.debug("midFollow...")   
    log.debug("rotPlug: %s"%rotPlug)
    log.debug("aimVector: '%s'"%aimVector)
    log.debug("upVector: '%s'"%upVector)    
    log.debug("upLoc: '%s'"%upLoc)
    log.debug("rotDriven: '%s'"%rotDriven)
    
    #Constrain the group   
    """constraintBuffer = mc.aimConstraint(ml_anchorJoints[-1].mNode,
                                        i_midFollowGrp.mNode,
                                        maintainOffset = True, weight = 1,
                                        aimVector = aimVector,
                                        upVector = upVector,
                                        worldUpObject = ml_segmentHandles[0].mNode,
                                        worldUpType = 'objectRotation' )"""
    constraintBuffer = mc.aimConstraint(ml_anchorJoints[-1].mNode,
                                        i_midFollowGrp.mNode,
                                        maintainOffset = True, weight = 1,
                                        aimVector = aimVector,
                                        upVector = upVector,
                                        worldUpObject = i_midUp.mNode,
                                        worldUpType = 'object' )       
    i_midFollowAimConstraint = cgmMeta.cgmNode(constraintBuffer[0]) 
    
    #>>>Twist setup 
    #Connect To follow group
    #attributes.doConnectAttr(rotPlug,"%s.r%s"%(i_midFollowGrp.mNode,
     #                                          self._jointOrientation[0]))
                             
    #Create the add node
    i_pmaAdd = NodeF.createAverageNode([driverNodeAttr,
                                       "%s.r%s"%(self._i_rigNull.segmentHandles[1].mNode,#mid handle
                                                 self._jointOrientation[0])],
                                       [i_midUpGroup.mNode,#ml_influenceJoints[1].mNode
                                        'r%s'%self._jointOrientation[0]],operation=1)
    for a in rotDriven:#BridgeBack
	attributes.doConnectAttr("%s.output1D"%i_pmaAdd.mNode,a)
	
    #Base follow Setup
    #====================================================================================    
    #>>>Create some locs
    """
    i_baseUp = ml_influenceJoints[0].doLoc()
    i_baseUp.addAttr('cgmTypeModifier','baseUp')
    i_baseUp.doName()
    i_baseUp.parent = ml_controlsFK[0].mNode#Fk one
    attributes.doSetAttr(i_baseUp.mNode,'t%s'%self._jointOrientation[1],dist)
    i_baseUp.overrideEnabled = 1
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'visLocs',lock=False).doConnectOut("%s.%s"%(i_baseUp.mNode,'overrideVisibility'))
    
    constBuffer = mc.parentConstraint([mi_hips.mNode,ml_controlsFK[0].mNode],
                                      i_baseUp.mNode,maintainOffset=True)[0]
    i_midUpConstraint = cgmMeta.cgmNode(constBuffer)    
    """
    
    #Create an point/aim group
    i_baseFollowGrp = cgmMeta.cgmObject( self._i_rigNull.segmentHandles[0].doGroup(True),setClass=True)
    i_baseFollowGrp.addAttr('cgmTypeModifier','follow')
    i_baseFollowGrp.doName()
    i_baseFollowGrp.rotateOrder = 0
    
    i_baseFollowPointConstraint = cgmMeta.cgmNode(mc.pointConstraint([ml_anchorJoints[1].mNode],
                                                                     i_baseFollowGrp.mNode,maintainOffset=True)[0])
    
    log.debug("baseFollow...")
    log.debug("aimVector: '%s'"%aimVector)
    log.debug("upVector: '%s'"%upVector)  
    mc.orientConstraint([mi_hips.mNode,ml_controlsFK[0].mNode],
                        i_baseFollowGrp.mNode,
                        maintainOffset = True, weight = 1)    
    """constraintBuffer = mc.aimConstraint(i_midPoint.mNode,
                                        i_baseFollowGrp.mNode,
                                        maintainOffset = True, weight = 1,
                                        aimVector = aimVector,
                                        upVector = upVector)"""     
    """constraintBuffer = mc.aimConstraint(i_midPoint.mNode,
                                        i_baseFollowGrp.mNode,
                                        maintainOffset = True, weight = 1,
                                        aimVector = aimVector,
                                        upVector = upVector,
                                        worldUpObject = i_baseUp.mNode,
                                        worldUpType = 'object' )"""    
    #i_baseFollowAimConstraint = cgmMeta.cgmNode(constraintBuffer[0]) 
    
    #Parent and constrain joints
    #====================================================================================
    #Constrain influence joints
    for i_jnt in ml_influenceJoints:#unparent influence joints
	i_jnt.parent = False
    ml_rigJoints[-2].parent = False
    mc.parentConstraint(self._i_rigNull.segmentHandles[0].mNode,
                        ml_influenceJoints[0].mNode,skipRotate = 'z',
                        maintainOffset = True)        
    mc.parentConstraint(self._i_rigNull.segmentHandles[-1].mNode,
                        ml_influenceJoints[-1].mNode,skipRotate = 'z',
                        maintainOffset = True) 
    mc.parentConstraint(self._i_rigNull.segmentHandles[1].mNode,
                        ml_influenceJoints[1].mNode,skipRotate = 'z',
                        maintainOffset = True)     
    #constrain Anchors
    mc.parentConstraint(mi_hips.mNode,
                        ml_anchorJoints[1].mNode,#pelvis
                        skipRotate = 'z',
                        maintainOffset = True)     
    mc.parentConstraint(mi_handleIK.mNode,#Shoulers
                        ml_anchorJoints[-1].mNode,
                        skipRotate = 'z',                        
                        maintainOffset = True)       
    
    ml_anchorJoints[0].parent = mi_hips.mNode#parent pelvis anchor to hips
    
    mc.pointConstraint(ml_anchorJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)
    mc.orientConstraint(ml_anchorJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)
    mc.scaleConstraint(ml_anchorJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)
    #mc.connectAttr((ml_influenceJoints[0].mNode+'.s'),(ml_rigJoints[0].mNode+'.s'))
    
    l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
    
    for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
        attachJoint = distance.returnClosestObject(i_jnt.mNode,l_rigJoints)
	log.debug("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
        pntConstBuffer = mc.pointConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
        orConstBuffer = mc.orientConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
        #scConstBuffer = mc.scaleConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)        
        #mc.connectAttr((attachJoint+'.t'),(joint+'.t'))
        #mc.connectAttr((attachJoint+'.r'),(joint+'.r'))
        mc.connectAttr((i_jnt.mNode+'.s'),(attachJoint+'.s'))
	
    mc.pointConstraint(ml_anchorJoints[-1].mNode,ml_rigJoints[-2].mNode,maintainOffset=False)
    mc.orientConstraint(ml_anchorJoints[-1].mNode,ml_rigJoints[-2].mNode,maintainOffset=False)
    #mc.scaleConstraint(ml_influenceJoints[-1].mNode,ml_rigJoints[-2].mNode,maintainOffset=False)
    mc.connectAttr((ml_anchorJoints[-1].mNode+'.s'),(ml_rigJoints[-2].mNode+'.s'))
    
    #Final stuff
    self._i_rigNull.version = __version__
    
    return True 
def build_deformationOLDSurface(self):
    """
    Rotate orders
    hips = 3
    """ 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.build_deformationRig>>bad self!")
	raise StandardError,error
    
    #>>>Get data
    ml_influenceJoints = self._i_rigNull.influenceJoints
    ml_controlsFK =  self._i_rigNull.controlsFK    
    ml_segmentJoints = self._i_rigNull.segmentJoints
    ml_anchorJoints = self._i_rigNull.anchorJoints
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_segmentHandles = self._i_rigNull.segmentHandles
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    mi_hips = self._i_rigNull.hips
    mi_handleIK = self._i_rigNull.handleIK
    
    #>>>Create a constraint surface for the influence joints
    #====================================================================================    
    """
    try:
	l_influenceJoints = [i_jnt.mNode for i_jnt in ml_influenceJoints] 
	d_constraintSurfaceReturn = rUtils.createConstraintSurfaceSegment(l_influenceJoints[1:],
	                                                                  self._jointOrientation,
	                                                                  self._partName+'_constraint',
	                                                                  moduleInstance=self._i_module)    
	for i_jnt in ml_influenceJoints:
	    i_jnt.parent = False#Parent to world
	    
	for i,i_jnt in enumerate(ml_influenceJoints[1:-1]):#Snap our ones with follow groups to them
	    if i_jnt.getMessage('snapToGroup'):
		pBuffer = i_jnt.getMessage('snapToGroup')[0]
		#Parent the control to the snapToGroup of the joint
		mc.parent( search.returnAllParents(ml_segmentHandles[i].mNode)[-1],pBuffer)
		i_jnt.parent = ml_segmentHandles[i].mNode#Parent to control group
	
	#Skin cluster to first and last influence joints
	i_constraintSurfaceCluster = cgmMeta.cgmNode(mc.skinCluster ([ml_influenceJoints[0].mNode,ml_influenceJoints[-1].mNode],
	                                                             d_constraintSurfaceReturn['i_controlSurface'].mNode,
	                                                             tsb=True,
	                                                             maximumInfluences = 3,
	                                                             normalizeWeights = 1,dropoffRate=4.0)[0])
	i_constraintSurfaceCluster.addAttr('cgmName', str(self._partName), lock=True)
	i_constraintSurfaceCluster.addAttr('cgmTypeModifier','constraintSurface', lock=True)
	i_constraintSurfaceCluster.doName()   
	
    except StandardError,error:
	log.error("build_spine>>Constraint surface build fail")
	raise StandardError,error
	"""
    #Control Surface
    #====================================================================================
    try:
	#Create surface
	surfaceReturn = rUtils.createControlSurfaceSegment([i_jnt.mNode for i_jnt in ml_segmentJoints],
	                                                   self._jointOrientation,
	                                                   self._partName,
	                                                   moduleInstance=self._i_module)
	#Add squash
	rUtils.addSquashAndStretchToControlSurfaceSetup(surfaceReturn['surfaceScaleBuffer'],[i_jnt.mNode for i_jnt in ml_segmentJoints],moduleInstance=self._i_module)
	#Twist
	log.debug(self._jointOrientation)
	capAim = self._jointOrientation[0].capitalize()
	log.debug("capAim: %s"%capAim)
	rUtils.addRibbonTwistToControlSurfaceSetup([i_jnt.mNode for i_jnt in ml_segmentJoints],
	                                           [ml_anchorJoints[1].mNode,'rotate%s'%capAim],#Spine1
	                                           [ml_anchorJoints[-1].mNode,'rotate%s'%capAim])#Sternum
	log.debug(surfaceReturn)
    
	#Surface influence joints cluster#
	i_controlSurfaceCluster = cgmMeta.cgmNode(mc.skinCluster ([i_jnt.mNode for i_jnt in ml_influenceJoints],
	                                                          surfaceReturn['i_controlSurface'].mNode,
	                                                          tsb=True,
	                                                          maximumInfluences = 2,
	                                                          normalizeWeights = 1,dropoffRate=6.0)[0])
	
	i_controlSurfaceCluster.addAttr('cgmName', str(self._partName), lock=True)
	i_controlSurfaceCluster.addAttr('cgmTypeModifier','controlSurface', lock=True)
	i_controlSurfaceCluster.doName()
	
	rUtils.controlSurfaceSmoothWeights(surfaceReturn['i_controlSurface'].mNode,start = ml_influenceJoints[0].mNode,
	                                    end = ml_influenceJoints[-1].mNode, blendLength = 5)
	
	log.debug(i_controlSurfaceCluster.mNode)
	# smooth skin weights #
	#skinning.simpleControlSurfaceSmoothWeights(i_controlSurfaceCluster.mNode)   
	
    except StandardError,error:
	log.error("build_spine>>Control surface build fail")
	raise StandardError,error
    try:#Setup top twist driver
	drivers = ["%s.r%s"%(i_obj.mNode,self._jointOrientation[0]) for i_obj in ml_controlsFK]
	drivers.append("%s.r%s"%(ml_segmentHandles[-1].mNode,self._jointOrientation[0]))
	drivers.append("%s.ry"%(mi_handleIK.mNode))
	for d in drivers:
	    log.debug(d)
	NodeF.createAverageNode(drivers,
	                        [ml_anchorJoints[-1].mNode,"r%s"%self._jointOrientation[0]],1)
	
    except StandardError,error:
	log.error("build_spine>>Top Twist driver fail")
	raise StandardError,error
    
    try:#Setup bottom twist driver
	log.debug("%s.r%s"%(ml_segmentHandles[0].getShortName(),self._jointOrientation[0]))
	log.debug("%s.r%s"%(mi_hips.getShortName(),self._jointOrientation[0]))
	drivers = ["%s.r%s"%(ml_segmentHandles[0].mNode,self._jointOrientation[0])]
	drivers.append("%s.r%s"%(mi_hips.mNode,self._jointOrientation[0]))
	for d in drivers:
	    log.debug(d)
	log.debug("driven: %s"%("%s.r%s"%(ml_anchorJoints[1].mNode,self._jointOrientation[0])))
	NodeF.createAverageNode(drivers,
	                        "%s.r%s"%(ml_anchorJoints[1].mNode,self._jointOrientation[0]),1)
	
    except StandardError,error:
	log.error("build_spine>>Bottom Twist driver fail")
	raise StandardError,error
    

    
    return True
