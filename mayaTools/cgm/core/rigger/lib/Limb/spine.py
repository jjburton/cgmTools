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

from cgm.core.rigger import ModuleCurveFactory as mCurveFactory
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools
reload(mCurveFactory)
reload(mControlFactory)
from cgm.core.rigger.lib import rig_Utils as rUtils
reload(rUtils)
from cgm.lib import (joints,
                     skinning,
                     dictionary,
                     distance,
                     search,
                     curves,
                     )

#>>> Utilities
#===================================================================
__version__ = 0.03272013
@r9General.Timer
def build_rigSkeleton(self):
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
	#>>Surface chain    
	l_surfaceJoints = mc.duplicate(self._l_skinJoints[1:-1],po=True,ic=True,rc=True)
	log.info(l_surfaceJoints)
	ml_surfaceJoints = []
	for i,j in enumerate(l_surfaceJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmType','surfaceJoint',attrType='string')
	    i_j.doName()
	    l_surfaceJoints[i] = i_j.mNode
	    ml_surfaceJoints.append(i_j)
	ml_surfaceJoints[0].parent = False#Parent to world
	
	#>>Deformation chain    
	l_rigJoints = mc.duplicate(self._l_skinJoints,po=True,ic=True,rc=True)
	log.info(l_surfaceJoints)
	ml_rigJoints = []
	for i,j in enumerate(l_rigJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmType','rigJoint',attrType='string',lock=True)
	    i_j.doName()
	    l_rigJoints[i] = i_j.mNode
	    ml_rigJoints.append(i_j)
	ml_rigJoints[0].parent = False#Parent to world
	
	
	#>>Anchor chain 	    
	#Start
	i_startJnt = cgmMeta.cgmObject(mc.duplicate(self._l_skinJoints[0],po=True,ic=True,rc=True)[0])
	i_startJnt.addAttr('cgmType','anchorJoint',attrType='string',lock=True)
	i_startJnt.doName()
	
	#End
	l_endJoints = mc.duplicate(self._l_skinJoints[-2],po=True,ic=True,rc=True)
	i_endJnt = cgmMeta.cgmObject(l_endJoints[0])
	for j in l_endJoints:
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmType','anchorJoint',attrType='string',lock=True)
	    i_j.doName()
	i_endJnt.parent = False
	
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
		
		ml_influenceJoints.append(i_new)
		
	#>>> Store em all to our instance
	self._i_rigNull.connectChildNode(i_startJnt,'startAnchor','module')
	self._i_rigNull.connectChildNode(i_endJnt,'endAnchor','module')	
	self._i_rigNull.connectChildrenNodes(ml_rigJoints,'rigJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_influenceJoints,'influenceJoints','module')
	self._i_rigNull.connectChildrenNodes(ml_surfaceJoints,'surfaceJoints','module')
	
    except StandardError,error:
	log.error("build_spine>>Build rig joints fail!")
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
    
    #>>> Get some special pivot xforms
    ml_surfaceJoints = self._i_rigNull.surfaceJoints 
    l_surfaceJoints  = [i_jnt.mNode for i_jnt in ml_surfaceJoints] 
    tmpCurve = curves.curveFromObjList(l_surfaceJoints)
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
    #>>>Shapes
    try:
	mCurveFactory.go(self._i_module,storageInstance=self)#This will store controls to a dict called    
	log.info(self._md_controlShapes)
    except StandardError,error:
	log.error("build_spine>>Build shapes fail!")
	raise StandardError,error
    
    #>>>Set up structure
    try:#Cog
	i_cog = self._md_controlShapes['cog']
	d_buffer = mControlFactory.registerControl(i_cog,addGroups = True,addConstraintGroup=True,
	                                           freezeAll=True,
	                                           controlType='cog')
	i_cog = d_buffer['instance']
	self._i_rigNull.connectChildNode(i_cog,'cog','module')
	
    except StandardError,error:
	log.error("build_spine>>Build cog fail!")
	raise StandardError,error
        
    try:#>FK Segments
	ml_segmentsFK = self._md_controlShapes['segmentFK']
	for i,i_obj in enumerate(ml_segmentsFK[1:]):#parent
	    i_obj.parent = ml_segmentsFK[i].mNode
	    
	ml_segmentsFK[0].parent = i_cog.mNode
	for i_obj in ml_segmentsFK:
	    d_buffer = mControlFactory.registerControl(i_obj,addGroups=1,setRotateOrder=5,typeModifier='fk',) 
	    i_obj = d_buffer['instance']
	self._i_rigNull.connectChildrenNodes(ml_segmentsFK,'controlsFK','module')
    
    except StandardError,error:
	log.error("build_spine>>Build fk fail!")
	raise StandardError,error
        
    
    try:#>IK Segments
	ml_segmentsIK = self._md_controlShapes['segmentIK']
	#ml_segmentsIK[-1].parent = self._md_controlShapes['segmentIKEnd'].mNode
	
	for i_obj in ml_segmentsIK:
	    d_buffer = mControlFactory.registerControl(i_obj,addGroups=1,typeModifier='ik',
		                                       setRotateOrder=2)       
	    i_obj = d_buffer['instance']
	self._i_rigNull.connectChildrenNodes(ml_segmentsIK,'segmentHandles','module')
    except StandardError,error:
	log.error("build_spine>>Build ik handle fail!")
	raise StandardError,error
    
    
    try:#>IK Handle
	i_IKEnd = self._md_controlShapes['segmentIKEnd']
	i_IKEnd.parent = i_cog.mNode
	i_loc = i_IKEnd.doLoc()#Make loc for a new transform
	i_loc.rx = i_loc.rx + 90#offset   
	mc.move (shouldersPivotPos[0],shouldersPivotPos[1],shouldersPivotPos[2], i_loc.mNode)
	
	d_buffer = mControlFactory.registerControl(i_IKEnd,copyTransform=i_loc.mNode,
	                                           typeModifier='ik',
	                                           addGroups = 1,addConstraintGroup=True,
	                                           setRotateOrder=3)
	i_IKEnd = d_buffer['instance']	
	
	#Parent last handle to IK Handle
	mc.parent(ml_segmentsIK[-1].getAllParents()[-1],i_IKEnd.mNode)
	
	i_loc.delete()#delete
	self._i_rigNull.connectChildNode(i_IKEnd,'handleIK','module')
	
    except StandardError,error:
	log.error("build_spine>>Build ik handle fail!")
	raise StandardError,error   
      
    
    try:#>Hips
	i_hips = self._md_controlShapes['hips']
	i_hips.parent = i_cog.mNode#parent
	i_loc = i_hips.doLoc()
	mc.move (hipPivotPos[0],hipPivotPos[1],hipPivotPos[2], i_loc.mNode)
	
	d_buffer =  mControlFactory.registerControl(i_hips,addGroups = True,
	                                            copyPivot=i_loc.mNode,
	                                            addConstraintGroup=True)
	self._i_rigNull.connectChildNode(i_hips,'hips','module')
	i_hips = d_buffer['instance']
	i_loc.delete()
	
    except StandardError,error:
	log.error("build_spine>>Build hips fail!")
	raise StandardError,error
    
    #>>> Store em all to our instance    
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
    ml_surfaceJoints = self._i_rigNull.surfaceJoints
    ml_rigJoints = self._i_rigNull.rigJoints
    
    ml_segmentHandles = self._i_rigNull.segmentHandles
    
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
	surfaceReturn = rUtils.createControlSurfaceSegment([i_jnt.mNode for i_jnt in ml_surfaceJoints],
	                                                   self._jointOrientation,
	                                                   self._partName,
	                                                   moduleInstance=self._i_module)
	#Add squash
	rUtils.addSquashAndStretchToControlSurfaceSetup(surfaceReturn['surfaceScaleBuffer'],[i_jnt.mNode for i_jnt in ml_surfaceJoints],moduleInstance=self._i_module)
	#Twist
	log.info(self._jointOrientation)
	capAim = self._jointOrientation[0].capitalize()
	log.info("capAim: %s"%capAim)
	rUtils.addRibbonTwistToControlSurfaceSetup([i_jnt.mNode for i_jnt in ml_surfaceJoints],[ml_influenceJoints[0].mNode,'rotate%s'%capAim],[ml_influenceJoints[-1].mNode,'rotate%s'%capAim])
	
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
	
	log.info(i_controlSurfaceCluster.mNode)
	# smooth skin weights #
	#skinning.simpleControlSurfaceSmoothWeights(i_controlSurfaceCluster.mNode)   
	
    except StandardError,error:
	log.error("build_spine>>Control surface build fail")
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
    
    #>>>Get data
    ml_influenceJoints = self._i_rigNull.influenceJoints
    ml_surfaceJoints = self._i_rigNull.surfaceJoints
    ml_rigJoints = self._i_rigNull.rigJoints
    ml_segmentHandles = self._i_rigNull.segmentHandles
        
    #Mid follow Setup
    #====================================================================================    
    #>>>Create some locs
    i_midAim = ml_influenceJoints[1].doLoc()
    i_midAim.doAddAttr('cgmTypeModifier','midAim')
    i_midAim.doName()
    
    i_midPoint = ml_influenceJoints[1].doLoc()
    i_midPoint.doAddAttr('cgmTypeModifier','midPoint')
    i_midPoint.doName()

    i_midUp = ml_influenceJoints[1].doLoc()
    i_midUp.doAddAttr('cgmTypeModifier','midUp')
    i_midPoint.doName()

    i_midUp.parent = i_midPoint.mNode
    
    #Mid point constraint
    i_midPointConstraint = cgmMeta.cgmNode(mc.parentConstraint([ml_influenceJoints[0].mNode,
                                                                ml_influenceJoints[-1].mNode],
                                                               i_midPoint.mNode,maintainOffset=True)[0])
    
    targetWeights = mc.parentConstraint(i_midPointConstraint.mNode,q=True, weightAliasList=True)      
    mc.setAttr(('%s.%s' % (i_midPointConstraint.mNode,targetWeights[0])),.5 )
    mc.setAttr(('%s.%s' % (i_midPointConstraint.mNode,targetWeights[1])),1.0 )
    
    #Aim loc constraint
    i_midAimConstraint = cgmMeta.cgmNode(mc.parentConstraint([ml_influenceJoints[0].mNode,
                                                              ml_influenceJoints[-1].mNode],
                                                             i_midAim.mNode,maintainOffset=True)[0])
    
    targetWeights = mc.parentConstraint(i_midAimConstraint.mNode,q=True, weightAliasList=True)      
    mc.setAttr(('%s.%s' % (i_midAimConstraint.mNode,targetWeights[0])),.1)
    mc.setAttr(('%s.%s' % (i_midAimConstraint.mNode,targetWeights[1])),1.0 )  
    
    #Create an point/aim group
    i_midFollowGrp = cgmMeta.cgmObject( self._i_rigNull.segmentHandles[1].doGroup(True),setClass=True)
    i_midFollowGrp.addAttr('cgmTypeModifier','follow')
    i_midFollowGrp.doName()
    
    i_midFollowPointConstraint = cgmMeta.cgmNode(mc.pointConstraint([i_midPoint.mNode],
                                                                    i_midFollowGrp.mNode,maintainOffset=True)[0])
    
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    closestJoint = distance.returnClosestObject(i_followGrp.mNode,[i_jnt.mNode for i_jnt in ml_surfaceJoints])
    upLoc = cgmMeta.cgmObject(closestJoint).rotateUpGroup.upLoc.mNode
    log.info("aimVector: '%s'"%aimVector)
    log.info("upVector: '%s'"%upVector)    
    log.info("upLoc: '%s'"%upLoc)
    aimConstraintBuffer = mc.aimConstraint(ml_influenceJoints[-1].mNode,
                                           i_midFollowGrp.mNode,
                                           maintainOffset = True, weight = 1,
                                           aimVector = aimVector,
                                           upVector = upVector,
                                           worldUpObject = i_midUp.mNode,
                                           worldUpType = 'object' )    
    i_midFollowAimConstraint = cgmMeta.cgmNode(aimConstraintBuffer[0])    
    
    #Base follow Setup
    #====================================================================================    
    #>>>Create some locs
    i_baseUp = ml_influenceJoints[0].doLoc()
    i_baseUp.doAddAttr('cgmTypeModifier','baseUp')
    i_baseUp.doName()
    
    #Create an point/aim group
    i_baseFollowGrp = cgmMeta.cgmObject( self._i_rigNull.segmentHandles[0].doGroup(True),setClass=True)
    i_baseFollowGrp.addAttr('cgmTypeModifier','follow')
    i_baseFollowGrp.doName()
    
    i_midFollowPointConstraint = cgmMeta.cgmNode(mc.pointConstraint([i_midPoint.mNode],
                                                                    i_baseFollowGrp.mNode,maintainOffset=True)[0])
    
    
    
    #Connect Twist rotate
    #Setup add to mid twist pma
    return
    
    #Parent and constrain joints
    #====================================================================================
    ml_influenceJoints[0].parent = self._i_rigNull.hips.mNode#parent pelvis influence to hips
    ml_influenceJoints[-1].parent = self._i_rigNull.segmentHandles[-1].mNode#parent top influence to top
    
    mc.pointConstraint(ml_influenceJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)
    mc.orientConstraint(ml_influenceJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)
    #mc.scaleConstraint(ml_influenceJoints[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False)
    mc.connectAttr((ml_influenceJoints[0].mNode+'.s'),(ml_rigJoints[0].mNode+'.s'))
    
    l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
    
    for i,i_jnt in enumerate(ml_surfaceJoints[:-1]):
        attachJoint = distance.returnClosestObject(i_jnt.mNode,l_rigJoints)
	log.info("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
        pntConstBuffer = mc.pointConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
        orConstBuffer = mc.orientConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
        #scConstBuffer = mc.scaleConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)        
        #mc.connectAttr((attachJoint+'.t'),(joint+'.t'))
        #mc.connectAttr((attachJoint+'.r'),(joint+'.r'))
        mc.connectAttr((i_jnt.mNode+'.s'),(attachJoint+'.s'))
	
    mc.pointConstraint(ml_influenceJoints[-1].mNode,ml_rigJoints[-2].mNode,maintainOffset=False)
    mc.orientConstraint(ml_influenceJoints[-1].mNode,ml_rigJoints[-2].mNode,maintainOffset=False)
    #mc.scaleConstraint(ml_influenceJoints[-1].mNode,ml_rigJoints[-2].mNode,maintainOffset=False)
    mc.connectAttr((ml_influenceJoints[-1].mNode+'.s'),(ml_rigJoints[-2].mNode+'.s'))
    
    return True 