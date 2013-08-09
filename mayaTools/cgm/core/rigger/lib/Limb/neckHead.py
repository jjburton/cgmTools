"""
------------------------------------------
cgm.core.rigger: Limb.neckHead
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

neckHead rig builder
================================================================
"""
__version__ = 0.0782013


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
#from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta

from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF

from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools

from cgm.core.rigger.lib import rig_Utils as rUtils

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
	log.error("neckHead.__bindSkeletonSetup__>>bad self!")
	raise StandardError,error
    
    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self._i_module.rigNull.skinJoints or []
    if not self._i_module.isSkeletonized():
	raise StandardError, "%s is not skeletonized yet."%self._strShortName
    try:#Reparent joints
	"""
	ml_skinJoints = self._i_module.rigNull.skinJoints	
	if ml_skinJoints[0].parent:
	    ml_skinJoints[-1].parent = ml_skinJoints[0].parent
	else:
	    ml_skinJoints[-1].parent = ml_skinJoints[0].mNode"""
		
	ml_moduleJoints = self._i_module.rigNull.moduleJoints #Get the module joints
	ml_skinJoints = []
	
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
		    
	#We have to connect back our lists because duplicated joints with message connections duplicate those connections
	self._i_rigNull.connectChildrenNodes(ml_moduleJoints,'moduleJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_skinJoints,'skinJoints','module')
	#self._i_rigNull.connectChildrenNodes(ml_handleJoints,'handleJoints','module')
	
	log.info("moduleJoints: len - %s | %s"%(len(ml_moduleJoints),[i_jnt.getShortName() for i_jnt in ml_moduleJoints]))	
	log.info("skinJoints: len - %s | %s"%(len(ml_skinJoints),[i_jnt.getShortName() for i_jnt in ml_skinJoints]))	
	#log.info("handleJoints: len - %s | %s"%(len(ml_handleJoints),[i_jnt.getShortName() for i_jnt in ml_handleJoints]))	
		

    except StandardError,error:
	log.error("build_neckHead>>__bindSkeletonSetup__ fail!")
	raise StandardError,error   
    
#@r9General.Timer
def build_rigSkeleton(self):
    """
    """
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("neckHead.build_deformationRig>>bad self!")
	raise StandardError,error
    
    #>>>Create joint chains
    #=============================================================    
    try:
	ml_skinJoints = self._ml_skinJoints
	ml_moduleJoints = self._ml_moduleJoints
	ml_segmentHandleJoints = []
	
	#>>Rig chain  
	#=====================================================================	
	ml_rigJoints = self.build_rigChain()
	l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
	ml_handleJoints = self._i_module.rig_getRigHandleJoints()
	
	ml_handleJoints[0].parent = False#Parent to world
	ml_handleJoints[-1].parent = False#Parent to world
    except StandardError,error:
	log.error("build_neckHead>>Build rig chain fail!")
	raise StandardError,error  
    try:
	#>>Segment chain  
	#=====================================================================
	l_toCopy = [i_j.p_nameShort for i_j in self._ml_moduleJoints]
	l_segmentJoints = mc.duplicate(l_toCopy,po=True,ic=True,rc=True)
	ml_segmentJoints = []
	for i,j in enumerate(l_segmentJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','segment',attrType='string',lock=True)
	    i_j.doName()
	    l_rigJoints[i] = i_j.mNode
	    ml_segmentJoints.append(i_j)
	ml_segmentJoints[0].parent = False#Parent to deformGroup	
	ml_segmentJoints[-1].parent = ml_segmentJoints[-2].mNode#Parent to world
    except StandardError,error:
	log.error("build_neckHead>>Build segment joints fail!")
	raise StandardError,error  
    
    try:#>>Anchor chain
	#=====================================================================	
	ml_anchors = []
	
	#Start
	i_startJnt = cgmMeta.cgmObject(mc.duplicate((self._ml_moduleJoints[0].mNode),po=True,ic=True,rc=True)[0])
	i_startJnt.addAttr('cgmType','anchor',attrType='string',lock=True)
	i_startJnt.doName()
	i_startJnt.parent = False
	ml_anchors.append(i_startJnt)
	
	#End
	l_endJoints = mc.duplicate((self._ml_moduleJoints[-1].mNode),po=True,ic=True,rc=True)
	i_endJnt = cgmMeta.cgmObject(l_endJoints[0])
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
	for i_jnt in self._ml_moduleJoints:
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
    except StandardError,error:
	log.error("build_neckHead>>Build anchor fail!")
	raise StandardError,error   
    try:
	#>>> Store em all to our instance
	self._i_rigNull.connectChildNode(i_startJnt,'startAnchor','rigNull')
	self._i_rigNull.connectChildNode(i_endJnt,'endAnchor','rigNull')	
	self._i_rigNull.connectChildrenNodes(ml_anchors,'anchorJoints','rigNull')
	self._i_rigNull.connectChildrenNodes(ml_segmentJoints,'segmentJoints','rigNull')	
	self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'influenceJoints','rigNull')
	
	self.connect_restoreJointLists()
	#self._i_rigNull.connectChildrenNodes(ml_rigJoints,'rigJoints','rigNull')#Push back
	#self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints','rigNull')#Push back
	#self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back		
	
	"""
	log.info("startAnchor>> %s"%i_startJnt.getShortName())
	log.info("endAnchor>> %s"%i_endJnt.getShortName())
	log.info("anchorJoints>> %s"%self._i_rigNull.getMessage('anchorJoints',False))
	log.info("rigJoints>> %s"%self._i_rigNull.getMessage('rigJoints',False))
	log.info("segmentJoints>> %s"%self._i_rigNull.getMessage('segmentJoints',False))
	log.info("influenceJoints>> %s"%self._i_rigNull.getMessage('influenceJoints',False))
	log.info("skinJoints>> %s"%self._i_rigNull.getMessage('skinJoints',False))
	"""
	self.get_report()

	
    except StandardError,error:
	log.error("build_neckHead>>Connect rig joints fail!")
	raise StandardError,error   
    
    ml_jointsToConnect = [i_startJnt,i_endJnt]
    ml_jointsToConnect.extend(ml_rigJoints)
    ml_jointsToConnect.extend(ml_segmentJoints)    
    ml_jointsToConnect.extend(ml_influenceJoints)

    for i_jnt in ml_jointsToConnect:
	i_jnt.overrideEnabled = 1		
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
	cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    
    
    if self._ml_skinJoints != self._i_rigNull.skinJoints:
	log.error("Stored skin joints don't equal buffered")
	    
#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['segmentFKLoli','segmentIK']}
#@r9General.Timer
def build_shapes(self):
    """
    """ 
    try:
	
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("neckHead.build_rig>>bad self!")
	raise StandardError,error
    
    #>>>Build our Shapes
    #=============================================================
    try:
	l_toBuild = ['segmentFK_Loli','segmentIK']
	
	mShapeCast.go(self._i_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
	log.info(self._md_controlShapes)
	
    except StandardError,error:
	log.error("build_neckHead>>Build shapes fail!")
	raise StandardError,error    
    
def build_controls(self):
    """
    """    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("neckHead.build_rig>>bad self!")
	raise StandardError,error
    
    try: self._md_controlShapes['segmentIK']
    except StandardError,error:    
	log.warning("neckHead.build_controls>>>Shapes issue, rebuilding. Error: %s"%error)
	build_shapes(self)
	
    #>>> Get some special pivot xforms
    ml_segmentJoints = self._i_rigNull.rigJoints 
    l_segmentJoints  = [i_jnt.mNode for i_jnt in ml_segmentJoints] 
    tmpCurve = curves.curveFromObjList(l_segmentJoints)
    midPivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.5))
    log.info("midPivotPos : %s"%midPivotPos)   
    mc.delete(tmpCurve)
	    
    l_controlsAll = []#we'll append to this list and connect them all at the end 
    
    #==================================================================
    try:#>>>> FK Segments
	if len( self._md_controlShapes['segmentFK_Loli'] )<2:
	    raise StandardError,"build_controls>> Must have at least two fk controls"
	
	ml_shapes = self._md_controlShapes['segmentFK_Loli']
	ml_segmentsFK = ml_shapes[:-1]
	log.info(ml_segmentsFK)
	
	for i,i_obj in enumerate(ml_segmentsFK[1:]):#parent
	    i_obj.parent = ml_segmentsFK[i].mNode
	    	
	for i,i_obj in enumerate(ml_segmentsFK):
	    d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,setRotateOrder=5,typeModifier='fk',) 	    
		
	    i_obj = d_buffer['instance']
	
	self._i_rigNull.connectChildrenNodes(ml_segmentsFK,'controlsFK','rigNull')
	l_controlsAll.extend(ml_segmentsFK)	
	ml_segmentsFK[0].masterGroup.parent = self._i_deformNull.mNode
    
    except StandardError,error:
	log.error("build_neckHead>>Build fk fail!")
	raise StandardError,error
    
    #==================================================================    
    try:#>>>> IK Segments
	ml_segmentsIK = self._md_controlShapes['segmentIK']
	
	for i_obj in ml_segmentsIK:
	    d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='ik',
		                                       setRotateOrder=2)       
	    i_obj = d_buffer['instance']
	    i_obj.masterGroup.parent = self._i_deformNull.mNode
	self._i_rigNull.connectChildrenNodes(ml_segmentsIK,'segmentHandles','rigNull')
	l_controlsAll.extend(ml_segmentsIK)	
	
	
    except StandardError,error:
	log.error("build_neckHead>>Build ik handle fail!")
	raise StandardError,error
    
    #==================================================================
    try:#>>>> IK Handle
	i_IKEnd = ml_shapes[-1]
	i_IKEnd.parent = False

	d_buffer = mControlFactory.registerControl(i_IKEnd,
	                                           typeModifier='ik',addSpacePivots = 2, addDynParentGroup = True, addConstraintGroup=True,
	                                           makeAimable = True,setRotateOrder=4)
	i_IKEnd = d_buffer['instance']	
	i_IKEnd.masterGroup.parent = self._i_deformNull.mNode
	
	self._i_rigNull.connectChildNode(i_IKEnd,'handleIK','rigNull')#connect
	l_controlsAll.append(i_IKEnd)	

	#Set aims
	i_IKEnd.axisAim = 4
	i_IKEnd.axisUp= 2
	
	
    except StandardError,error:
	log.error("build_neckHead>>Build ik handle fail!")
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
	log.error("neckHead.build_deformationRig>>bad self!")
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
	                                             additiveScaleSetup=True,
	                                             connectAdditiveScale=True,	                                             
	                                             moduleInstance=self._i_module)
	
	i_curve = curveSegmentReturn['mi_segmentCurve']
	i_curve.parent = self._i_rigNull.mNode
	self._i_rigNull.connectChildrenNodes([i_curve],'segmentCurves','rigNull')
	self._i_rigNull.connectChildrenNodes(ml_segmentJoints,'segmentJoints','rigNull')	#Reconnect to reset. Duplication from createCGMSegment causes issues	
	i_curve.segmentGroup.parent = self._i_rigNull.mNode
	

	    
    except StandardError,error:
	log.error("build_neckHead>>Control Segment build fail")
	raise StandardError,error
    
    
    try:#Setup top twist driver
	#Create an fk additive attributes
	str_curve = curveSegmentReturn['mi_segmentCurve'].getShortName()
	#fk_drivers = ["%s.r%s"%(i_obj.mNode,self._jointOrientation[0]) for i_obj in ml_controlsFK]
	drivers = ["%s.r%s"%(ml_segmentHandles[-1].mNode,self._jointOrientation[0])]
	drivers.append("%s.r%s"%(mi_handleIK.mNode,self._jointOrientation[0]))

	NodeF.createAverageNode(drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistEnd"],1)
	
    except StandardError,error:
	log.error("build_neckHead>>Top Twist driver fail")
	raise StandardError,error
    
    try:#Setup bottom twist driver
	log.info("%s.r%s"%(ml_segmentHandles[0].getShortName(),self._jointOrientation[0]))
	drivers = ["%s.r%s"%(ml_segmentHandles[0].mNode,self._jointOrientation[0])]
	drivers.append("%s.r%s"%(ml_controlsFK[0].mNode,self._jointOrientation[0]))

	NodeF.createAverageNode(drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistStart"],1)
    
    except StandardError,error:
	log.error("build_neckHead>>Bottom Twist driver fail")
	raise StandardError,error
    
        
    #Push squash and stretch multipliers to head
    i_buffer = i_curve.scaleBuffer
    
    #>>> Move attrs to handle ik ==========================================================
    for k in i_buffer.d_indexToAttr.keys():
	attrName = 'neckHead_%s'%k
	cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_handleIK.mNode,attrName,connectSourceToTarget = True)
	cgmMeta.cgmAttr(mi_handleIK.mNode,attrName,defaultValue = 1,keyable=True)
    
    cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
    cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
    cgmMeta.cgmAttr(i_curve,'twistMid').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
    cgmMeta.cgmAttr(i_curve,'scaleMidUp').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
    cgmMeta.cgmAttr(i_curve,'scaleMidOut').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)

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
	log.error("neckHead.build_deformationRig>>bad self!")
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
	ml_segmentSplineJoints = mi_segmentCurve.msgList_get('driverJoints',asMeta = True)
	
	ml_anchorJoints = self._i_rigNull.anchorJoints
	ml_rigJoints = self._i_rigNull.rigJoints
	ml_rigHandleJoints = self._i_module.rig_getRigHandleJoints()
	
	ml_segmentJoints = self._i_rigNull.segmentJoints	
	ml_segmentHandles = self._i_rigNull.segmentHandles
	aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
	mi_handleIK = self._i_rigNull.handleIK
	ml_controlsFK =  self._i_rigNull.controlsFK    
	
    except StandardError,error:
	log.error("neckHead.build_rig>> Gather data fail!")
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
	ml_headDynParents.extend(mi_handleIK.msgList_get('spacePivots',asMeta = True))
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
	log.error("neckHead.build_rig>> head dynamic parent setup fail!")
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
    
    mi_segmentAnchorStart.parent = self._i_deformNull.mNode#Segment anchor to deform null
    mc.parentConstraint(ml_anchorJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#constrain
    mc.scaleConstraint(ml_anchorJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#Constrain
    
    mi_segmentAnchorEnd.parent = self._i_deformNull.mNode#Segment end to deform null
    mc.parentConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
    mc.scaleConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
    
    #method 1
    ml_rigHandleJoints[0].parent = self._i_deformNull.mNode#Root handle to deform null
    ml_rigHandleJoints[-1].parent = ml_anchorJoints[-1].mNode#Top handle to last anchor
    
    ml_influenceJoints[0].parent = ml_segmentHandles[0].mNode#base influence to base segment handle
    ml_influenceJoints[-1].parent = ml_segmentHandles[-1].mNode#top influence to top segment handle
    
    #Parent anchors to controls
    ml_rigHandleJoints[0].parent = self._i_deformNull.mNode   
    ml_anchorJoints[0].parent = self._i_deformNull.mNode
    ml_anchorJoints[-1].parent = mi_handleIK.mNode
        
    
    l_rigJoints = [i_jnt.getShortName() for i_jnt in self._get_rigDeformationJoints()]
    for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
	#Don't try scale constraints in here, they're not viable
	attachJoint = distance.returnClosestObject(i_jnt.mNode,l_rigJoints)
	log.info("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
	pntConstBuffer = mc.pointConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
	orConstBuffer = mc.orientConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
	mc.connectAttr((i_jnt.mNode+'.s'),(attachJoint+'.s'))
    
    #mc.pointConstraint(ml_anchorJoints[-1].mNode,ml_rigHandleJoints[-1].mNode,maintainOffset=False)
    #mc.orientConstraint(ml_anchorJoints[-1].mNode,ml_rigHandleJoints[-1].mNode,maintainOffset=False)
    #mc.connectAttr((ml_anchorJoints[-1].mNode+'.s'),(ml_rigHandleJoints[-1].mNode+'.s'))
    
    #Set up heirarchy, connect master scale
    #====================================================================================
    #>>>Connect master scale
    cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(self._i_masterControl.mNode,'scaleY'))    
    
    #Set up Scale joints
    #====================================================================================     
    #Connect our last segment to the sternum if we have a scale joint
    if ml_rigHandleJoints[-1].getMessage('scaleJoint'):
	i_scaleJoint = ml_rigHandleJoints[-1].scaleJoint
	mc.connectAttr((mi_handleIK.mNode+'.scale'),(i_scaleJoint.mNode+'.scale'))        
    else:
	attributes.doSetLockHideKeyableAttr(mi_handleIK.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
    
    #Vis Network, lock and hide
    #====================================================================================
    #Lock and hide hips and shoulders
    #attributes.doSetLockHideKeyableAttr(mi_handleIK.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
    
    #
    #====================================================================================
    
    
    #Set up some defaults
    #====================================================================================
    mPlug_seg0 = cgmMeta.cgmAttr(ml_segmentHandles[0],'followRoot')
    mPlug_seg0.p_defaultValue = .95
    mPlug_seg0.value = .95
    mPlug_segLast = cgmMeta.cgmAttr(ml_segmentHandles[-1],'followRoot')
    mPlug_segLast.p_defaultValue = .5
    mPlug_segLast.value = .5

    #Final stuff
    self._set_versionToCurrent()
    
    return True 


"""
#@r9General.Timer
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
    build_deformation(self)
    build_rig(self)    
    
    return True"""

#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'shapes','function':build_shapes},
                    1:{'name':'skeleton','function':build_rigSkeleton},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'deformation','function':build_deformation},
                    4:{'name':'rig','function':build_rig},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------
