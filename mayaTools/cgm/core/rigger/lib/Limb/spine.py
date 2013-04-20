"""
------------------------------------------
cgm.core.rigger: Limb.spine
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

spine rig builder
================================================================
"""
__version__ = 0.04062013


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
from cgm.core import cgm_PuppetMeta as cgmPM
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as nodeF
reload(nodeF)

from cgm.core.rigger import ModuleCurveFactory as mCurveFactory
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools
reload(mCurveFactory)
reload(mControlFactory)
from cgm.core.rigger.lib import rig_Utils as rUtils
reload(rUtils)
from cgm.lib import (attributes,
                     joints,
                     skinning,
                     dictionary,
                     distance,
                     search,
                     curves,
                     )

#>>> Utilities
#===================================================================
@r9General.Timer
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
	l_segmentJoints = mc.duplicate(self._l_skinJoints[1:-1],po=True,ic=True,rc=True)
	ml_segmentJoints = []
	for i,j in enumerate(l_segmentJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','segment',attrType='string')
	    i_j.doName()
	    l_segmentJoints[i] = i_j.mNode
	    ml_segmentJoints.append(i_j)
	ml_segmentJoints[0].parent = False#Parent to world
	
	#>>Deformation chain    
	l_rigJoints = mc.duplicate(self._l_skinJoints,po=True,ic=True,rc=True)
	ml_rigJoints = []
	for i,j in enumerate(l_rigJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
	    i_j.doName()
	    l_rigJoints[i] = i_j.mNode
	    ml_rigJoints.append(i_j)
	ml_rigJoints[0].parent = self._i_deformGroup.mNode#Parent to deformGroup
	
	#>>Anchor chain
	ml_anchors = []
	i_rootJnt = cgmMeta.cgmObject(mc.duplicate(self._l_skinJoints[0],po=True,ic=True,rc=True)[0])
	i_rootJnt.addAttr('cgmTypeModifier','anchor',attrType='string',lock=True)
	i_rootJnt.doName()
	i_rootJnt.parent = False	
	ml_anchors.append(i_rootJnt)
	
	#Start
	i_startJnt = cgmMeta.cgmObject(mc.duplicate(self._l_skinJoints[1],po=True,ic=True,rc=True)[0])
	i_startJnt.addAttr('cgmTypeModifier','anchor',attrType='string',lock=True)
	i_startJnt.doName()
	i_startJnt.parent = False
	ml_anchors.append(i_startJnt)
	
	#End
	l_endJoints = mc.duplicate(self._l_skinJoints[-2],po=True,ic=True,rc=True)
	i_endJnt = cgmMeta.cgmObject(l_endJoints[0])
	for j in l_endJoints:
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','anchor',attrType='string',lock=True)
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
	self._i_rigNull.connectChildNode(i_startJnt,'startAnchor','module')
	self._i_rigNull.connectChildNode(i_endJnt,'endAnchor','module')	
	self._i_rigNull.connectChildrenNodes(ml_anchors,'anchorJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_rigJoints,'rigJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'influenceJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_segmentJoints,'segmentJoints','module')
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

    
    
    
@r9General.Timer
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
    try:
	mCurveFactory.go(self._i_module,storageInstance=self)#This will store controls to a dict called    
	log.info(self._md_controlShapes)
    except StandardError,error:
	log.error("build_spine>>Build shapes fail!")
	raise StandardError,error    
    
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
    
    try: self._md_controlShapes['cog']
    except StandardError,error:    
	log.warning("spine.build_controls>>>Shapes issue, rebuilding. Error: %s"%error)
	build_shapes(self)
	
    #>>> Get some special pivot xforms
    ml_segmentJoints = self._i_rigNull.segmentJoints 
    l_segmentJoints  = [i_jnt.mNode for i_jnt in ml_segmentJoints] 
    tmpCurve = curves.curveFromObjList(l_segmentJoints)
    hipPivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.15))
    shouldersPivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.8))
    log.info("hipPivotPos : %s"%hipPivotPos)
    log.info("shouldersPivotPos : %s"%shouldersPivotPos)   
    mc.delete(tmpCurve)
	
    #log.info(self.__dict__.keys())
    #>>> Figure out what's what
    #Add some checks like at least 3 handles
    
    #>>>Build our controls
    #=============================================================
    #>>>Set up structure
    try:#>>>> Cog
	i_cog = self._md_controlShapes['cog']
	d_buffer = mControlFactory.registerControl(i_cog,addExtraGroups = True,addConstraintGroup=True,
	                                           freezeAll=True,makeAimable=True,autoLockNHide=True,
	                                           controlType='cog')
	i_cog = d_buffer['instance']
	self._i_rigNull.connectChildNode(i_cog,'cog','module')#Store
	i_cog.masterGroup.parent = self._i_deformGroup.mNode
	#Set aims
	
    except StandardError,error:
	log.error("build_spine>>Build cog fail!")
	raise StandardError,error
    
    #==================================================================
    try:#>>>> FK Segments
	ml_segmentsFK = self._md_controlShapes['segmentFK']
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
	self._i_rigNull.connectChildrenNodes(ml_segmentsFK,'controlsFK','module')
	
    
    except StandardError,error:
	log.error("build_spine>>Build fk fail!")
	raise StandardError,error
        
    #==================================================================    
    try:#>>>> IK Segments
	ml_segmentsIK = self._md_controlShapes['segmentIK']
	#ml_segmentsIK[-1].parent = self._md_controlShapes['segmentIKEnd'].mNode
	
	for i_obj in ml_segmentsIK:
	    d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='ik',
		                                       setRotateOrder=2)       
	    i_obj = d_buffer['instance']
	    i_obj.masterGroup.parent = self._i_deformGroup.mNode
	self._i_rigNull.connectChildrenNodes(ml_segmentsIK,'segmentHandles','module')
	
	
    except StandardError,error:
	log.error("build_spine>>Build ik handle fail!")
	raise StandardError,error
    
    #==================================================================
    try:#>>>> IK Handle
	i_IKEnd = self._md_controlShapes['segmentIKEnd']
	i_IKEnd.parent = i_cog.mNode
	i_loc = i_IKEnd.doLoc()#Make loc for a new transform
	i_loc.rx = i_loc.rx + 90#offset   
	mc.move (shouldersPivotPos[0],shouldersPivotPos[1],shouldersPivotPos[2], i_loc.mNode)
	
	d_buffer = mControlFactory.registerControl(i_IKEnd,copyTransform=i_loc.mNode,
	                                           typeModifier='ik',addSpacePivots = 2, addDynParentGroup = True, addConstraintGroup=True,
	                                           makeAimable = True,setRotateOrder=3)
	i_IKEnd = d_buffer['instance']	
	
	#Parent last handle to IK Handle
	#mc.parent(ml_segmentsIK[-1].getAllParents()[-1],i_IKEnd.mNode)
	
	i_loc.delete()#delete
	self._i_rigNull.connectChildNode(i_IKEnd,'handleIK','module')#connect
	
	#Set aims
	#Default currently working
	
	
    except StandardError,error:
	log.error("build_spine>>Build ik handle fail!")
	raise StandardError,error   
      
    #==================================================================
    try:#>>>> Hips
	i_hips = self._md_controlShapes['hips']
	i_hips.parent = i_cog.mNode#parent
	i_loc = i_hips.doLoc()
	mc.move (hipPivotPos[0],hipPivotPos[1],hipPivotPos[2], i_loc.mNode)
	
	d_buffer =  mControlFactory.registerControl(i_hips,addSpacePivots = 2, addDynParentGroup = True, addConstraintGroup=True,
	                                            makeAimable = True,copyPivot=i_loc.mNode,setRotateOrder=5)
	self._i_rigNull.connectChildNode(i_hips,'hips','module')
	i_hips = d_buffer['instance']
	i_loc.delete()
	
	#Set aims
	i_hips.axisAim = 'y-'
	i_hips.axisUp = 'z+'
	
    except StandardError,error:
	log.error("build_spine>>Build hips fail!")
	raise StandardError,error
    
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
	
	log.info("curveSegmentReturn: %s"%curveSegmentReturn)
	i_curve = curveSegmentReturn['mi_segmentCurve']
	self._i_rigNull.connectChildrenNodes([i_curve],'segmentCurves','module')	
	i_curve.segmentGroup.parent = self._i_rigNull
	"""
	for o in  [ml_influenceJoints[1].mNode,
	           curveSegmentReturn['mi_segmentCurve'].mNode,
	           ml_influenceJoints[0].mNode,
	           ml_influenceJoints[-1].mNode,
	           ml_segmentHandles[1].mNode,
	           self._partName,
	           self._jointOrientation]:
	    log.info(o)
	return"""
	
	midReturn = rUtils.addCGMSegmentSubControl(ml_influenceJoints[1].mNode,
	                                           segmentCurve = i_curve,
	                                           baseParent=ml_influenceJoints[0],
	                                           endParent=ml_influenceJoints[-1],
	                                           midControls=ml_segmentHandles[1],
	                                           baseName=self._partName,
	                                           orientation=self._jointOrientation)
	
	for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
	    i_grp.parent = self._i_deformGroup.mNode
	    
    except StandardError,error:
	log.error("build_spine>>Control Segment build fail")
	raise StandardError,error
    
    
    try:#Setup top twist driver
	drivers = ["%s.r%s"%(i_obj.mNode,self._jointOrientation[0]) for i_obj in ml_controlsFK]
	drivers.append("%s.r%s"%(ml_segmentHandles[-1].mNode,self._jointOrientation[0]))
	drivers.append("%s.ry"%(mi_handleIK.mNode))
	for d in drivers:
	    log.info(d)
	nodeF.createAverageNode(drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistEnd"],1)
	#Old driven[ml_anchorJoints[-1].mNode,"r%s"%self._jointOrientation[0]]
    
    except StandardError,error:
	log.error("build_spine>>Top Twist driver fail")
	raise StandardError,error
    
    try:#Setup bottom twist driver
	log.info("%s.r%s"%(ml_segmentHandles[0].getShortName(),self._jointOrientation[0]))
	log.info("%s.r%s"%(mi_hips.getShortName(),self._jointOrientation[0]))
	drivers = ["%s.r%s"%(ml_segmentHandles[0].mNode,self._jointOrientation[0])]
	drivers.append("%s.r%s"%(mi_hips.mNode,self._jointOrientation[0]))
	for d in drivers:
	    log.info(d)
	log.info("driven: %s"%("%s.r%s"%(ml_anchorJoints[1].mNode,self._jointOrientation[0])))
	nodeF.createAverageNode(drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistStart"],1)
    
    except StandardError,error:
	log.error("build_spine>>Bottom Twist driver fail")
	raise StandardError,error
        
    #Push squash and stretch multipliers to cog
    i_buffer = i_curve.scaleBuffer
    
    for k in i_buffer.d_indexToAttr.keys():
	attrName = 'spine_%s'%k
	cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_cog.mNode,attrName,connectSourceToTarget = True)
	cgmMeta.cgmAttr('cog_anim',attrName, keyable =True, lock = False)    
    
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
	mi_segmentCurve = self._i_rigNull.segmentCurves[0]
	mi_segmentAnchorStart = mi_segmentCurve.anchorStart
	mi_segmentAnchorEnd = mi_segmentCurve.anchorEnd
	mi_segmentAttachStart = mi_segmentCurve.attachStart
	mi_segmentAttachEnd = mi_segmentCurve.attachEnd 
	mi_distanceBuffer = mi_segmentCurve.scaleBuffer
    
	log.info("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
	log.info("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
	log.info("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
	log.info("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
	log.info("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)
	
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
	log.info(ml_shoulderDynParents)
	log.info([i_obj.getShortName() for i_obj in ml_shoulderDynParents])
	
	#Add our parents
	i_dynGroup = mi_handleIK.dynParentGroup
	for o in ml_shoulderDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()
    except StandardError,error:
	log.error("spine.build_rig>> shoulder dynamic parent setup fail!")
	raise StandardError,error
    
    try:#>>>> Shoulder dynamicParent
	ml_hipsDynParents = [mi_cog]
	ml_hipsDynParents.extend(mi_hips.spacePivots)
	ml_hipsDynParents.append(self._i_masterControl)
	log.info(ml_hipsDynParents)
	log.info([i_obj.getShortName() for i_obj in ml_hipsDynParents])  
	
	#Add our parents
	i_dynGroup = mi_hips.dynParentGroup
	for o in ml_hipsDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()    
    except StandardError,error:
	log.error("spine.build_rig>> hips dynamic parent setup fail!")
	raise StandardError,error
    
    
    #Parent and constrain joints
    #====================================================================================
    ml_segmentJoints[0].parent = mi_cog.mNode
    ml_segmentSplineJoints[0].parent = mi_cog.mNode
    
    
    #Put the start and end controls in the heirarchy
    mc.parent(ml_segmentHandles[0].parent,mi_segmentAttachStart.mNode)
    mc.parent(ml_segmentHandles[-1].parent,mi_segmentAttachEnd.mNode)
    
    #parent the segment anchors
    mi_segmentAnchorStart.parent = ml_anchorJoints[1].mNode#Pelvis
    mi_segmentAnchorEnd.parent = ml_anchorJoints[-1].mNode#Sternum
    ml_rigJoints[-2].parent = ml_anchorJoints[-1].mNode
    
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
    #mc.connectAttr((ml_anchorJoints[0].mNode+'.s'),(ml_rigJoints[0].mNode+'.s'))
    
    
    l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
    for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
        attachJoint = distance.returnClosestObject(i_jnt.mNode,l_rigJoints)
	log.info("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
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
    
    #Set up heirarchy, connect master scale
    #====================================================================================
    #>>>Connect master scale
    cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(self._i_masterControl.mNode,'scaleY'))    
    #cgmMeta.cgmAttr(self._i_masterControl,'scaleY',lock=False).doConnectOut("%s.%s"%(mi_distanceBuffer.mNode,'masterScale'))    
    
    #Vis Network, lock and hide
    #====================================================================================
    #Cog control fk hide
    
    #Setup Cog vis control for fk controls
    mi_cog.addAttr('visFK', defaultValue = 1, attrType = 'bool',keyable = False,hidden = False, initialValue = 1)
    cgmMeta.cgmAttr( ml_controlsFK[0].mNode,'visibility').doConnectIn('%s.%s'%(mi_cog.mNode,'visFK'))    
    #cgmMeta.cgmAttr( ml_segmentsFK[0].mNode,'visibility').doConnectIn(i_cog.mNode,'visFK')
    
    #Final stuff
    self._i_rigNull.version = str(__version__)
    return True 

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
    log.info("midFollow...")   
    log.info("rotPlug: %s"%rotPlug)
    log.info("aimVector: '%s'"%aimVector)
    log.info("upVector: '%s'"%upVector)    
    log.info("upLoc: '%s'"%upLoc)
    log.info("rotDriven: '%s'"%rotDriven)
    
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
    i_pmaAdd = nodeF.createAverageNode([driverNodeAttr,
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
    
    log.info("baseFollow...")
    log.info("aimVector: '%s'"%aimVector)
    log.info("upVector: '%s'"%upVector)  
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
	log.info("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
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
	log.info(self._jointOrientation)
	capAim = self._jointOrientation[0].capitalize()
	log.info("capAim: %s"%capAim)
	rUtils.addRibbonTwistToControlSurfaceSetup([i_jnt.mNode for i_jnt in ml_segmentJoints],
	                                           [ml_anchorJoints[1].mNode,'rotate%s'%capAim],#Spine1
	                                           [ml_anchorJoints[-1].mNode,'rotate%s'%capAim])#Sternum
	log.info(surfaceReturn)
    
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
	
	log.info(i_controlSurfaceCluster.mNode)
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
	    log.info(d)
	nodeF.createAverageNode(drivers,
	                        [ml_anchorJoints[-1].mNode,"r%s"%self._jointOrientation[0]],1)
	
    except StandardError,error:
	log.error("build_spine>>Top Twist driver fail")
	raise StandardError,error
    
    try:#Setup bottom twist driver
	log.info("%s.r%s"%(ml_segmentHandles[0].getShortName(),self._jointOrientation[0]))
	log.info("%s.r%s"%(mi_hips.getShortName(),self._jointOrientation[0]))
	drivers = ["%s.r%s"%(ml_segmentHandles[0].mNode,self._jointOrientation[0])]
	drivers.append("%s.r%s"%(mi_hips.mNode,self._jointOrientation[0]))
	for d in drivers:
	    log.info(d)
	log.info("driven: %s"%("%s.r%s"%(ml_anchorJoints[1].mNode,self._jointOrientation[0])))
	nodeF.createAverageNode(drivers,
	                        "%s.r%s"%(ml_anchorJoints[1].mNode,self._jointOrientation[0]),1)
	
    except StandardError,error:
	log.error("build_spine>>Bottom Twist driver fail")
	raise StandardError,error
    

    
    return True
