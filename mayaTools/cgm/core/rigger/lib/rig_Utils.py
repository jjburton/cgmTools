"""
cgmLimb
Josh Burton (under the supervision of David Bokser:)
www.cgmonks.com
1/12/2011

Key:
1) Class - Limb
    Creates our rig objects
2)  


"""
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
from cgm.core.lib import nameTools

from cgm.lib import (distance,
                     attributes,
                     deformers,
                     lists,
                     rigging,
                     skinning,
                     dictionary,
                     nodes,
                     joints,
                     cgmMath)
#>>> Utilities
#===================================================================
@r9General.Timer
def controlSurfaceSmoothWeights(controlSurface):
    if issubclass(type(controlSurface),cgmMeta.cgmNode):
	i_surface = controlSurface
    elif mc.objExists(controlSurface):
	i_surface = cgmMeta.cgmNode(controlSurface)
    else:
	raise StandardError,"controlSurfaceSmoothWeights failed. Surface doesn't exist: '%s'"%controlSurface
    l_cvs = i_surface.getComponents('cv')
    l_skinClusters = deformers.returnObjectDeformers(i_surface.mNode,deformerTypes = 'skinCluster')
    i_skinCluster = cgmMeta.cgmNode(l_skinClusters[0])
    l_influenceObjects = skinning.queryInfluences(i_skinCluster.mNode) or []
    
    log.info("l_skinClusters: '%s'"%l_skinClusters)
    log.info("i_skinCluster: '%s'"%i_skinCluster)
    log.info("l_influenceObjects: '%s'"%l_influenceObjects)
    
    if not i_skinCluster and l_influenceObjects:
	raise StandardError,"controlSurfaceSmoothWeights failed. Not enough info found"
@r9General.Timer
def createControlSurfaceSegment(jointList,orientation = 'zyx',secondaryAxis = None,
                                baseName ='test', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]
    
    i_module = False
    i_rigNull = False
    if moduleInstance is not None:
	if issubclass(type(moduleInstance),cgmPM.cgmModule):
	    i_module = moduleInstance
	    i_rigNull = i_module.rigNull
	else:
	    log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    
    #Create our group
    i_grp = cgmMeta.cgmObject(name = 'newgroup')
    i_grp.addAttr('cgmName', str(baseName), lock=True)
    i_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    i_grp.doName()
    
    #Create surface
    l_surfaceReturn = joints.loftSurfaceFromJointList(jointList,outChannel)
    
    i_controlSurface = cgmMeta.cgmObject( l_surfaceReturn[0] )
    i_controlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_controlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
    i_controlSurface.doName()
    i_controlSurface.addAttr('mClass','cgmObject')
    
    if i_module:#if we have a module, connect vis
	i_controlSurface.overrideEnabled = 1		
	cgmMeta.cgmAttr(i_module.rigNull.mNode,'visSegment',lock=False).doConnectOut("%s.%s"%(i_controlSurface.mNode,'overrideVisibility'))
    
    
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    if not moduleInstance:#if it is, we can assume it's right
	if secondaryAxis is None:
	    raise StandardError,"createControlSurfaceSegment>>> Must have secondaryAxis arg if no moduleInstance is passed"
	for i_jnt in ml_jointList:
	    """
	    Cannot iterate how important this step is. Lost a day trying to trouble shoot why one joint chain worked and another didn't.
	    WILL NOT connect right without this.
	    """
    	    joints.orientJoint(i_jnt.mNode,orientation,secondaryAxis)
	
    #Create folicles
    ml_follicleTransforms = []
    ml_follicleShapes = []
    ml_upGroups = []
    
    #First thing we're going to do is create our follicles
    for i,i_jnt in enumerate(ml_jointList):       
        l_closestInfo = distance.returnClosestPointOnSurfaceInfo(i_jnt.mNode,i_controlSurface.mNode)
        log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
        #>>> Follicle =======================================================
        l_follicleInfo = nodes.createFollicleOnMesh(i_controlSurface.mNode)
        i_follicleTrans = cgmMeta.cgmObject(l_follicleInfo[1],setClass=True)
        i_follicleShape = cgmMeta.cgmNode(l_follicleInfo[0])
        #> Name
        i_follicleTrans.doStore('cgmName',i_jnt.mNode)
        i_follicleTrans.doName()
        #>Set follicle value
        i_follicleShape.parameterU = l_closestInfo['normalizedU']
        i_follicleShape.parameterV = l_closestInfo['normalizedV']
        
        ml_follicleShapes.append(i_follicleShape)
        ml_follicleTransforms.append(i_follicleTrans)
	
	i_follicleTrans.parent = i_grp.mNode	
	
	if i_module:#if we have a module, connect vis
	    i_follicleTrans.overrideEnabled = 1		
	    cgmMeta.cgmAttr(i_module.rigNull.mNode,'visRig',lock=False).doConnectOut("%s.%s"%(i_follicleTrans.mNode,'overrideVisibility'))
	
	
	#>>> loc
	"""
	First part of full ribbon wist setup
	"""
	if i_jnt != ml_jointList[-1]:
	    i_upLoc = i_jnt.doLoc()#Make up Loc
	    i_locRotateGroup = i_jnt.duplicateTransform(False)#group in place
	    i_locRotateGroup.parent = i_follicleTrans.mNode
	    i_locRotateGroup.doStore('cgmName',i_jnt.mNode)	    
	    i_locRotateGroup.addAttr('cgmTypeModifier','rotate',lock=True)
	    i_locRotateGroup.doName()
	    
	    #Store the rotate group to the joint
	    i_jnt.connectChildNode(i_locRotateGroup,'rotateUpGroup','drivenJoint')
	    i_zeroGrp = cgmMeta.cgmObject( i_locRotateGroup.doGroup(True),setClass=True )
	    i_zeroGrp.addAttr('cgmTypeModifier','zero',lock=True)
	    i_zeroGrp.doName()
	    #connect some other data
	    i_locRotateGroup.connectChildNode(i_follicleTrans,'follicle','drivenGroup')
	    i_locRotateGroup.connectChildNode(i_locRotateGroup.parent,'zeroGroup')
	    i_locRotateGroup.connectChildNode(i_upLoc,'upLoc')
	    
	    mc.makeIdentity(i_locRotateGroup.mNode, apply=True,t=1,r=1,s=1,n=0)
	    
	    
	    i_upLoc.parent = i_locRotateGroup.mNode
	    mc.move(0,10,0,i_upLoc.mNode,os=True)	
	    ml_upGroups.append(i_upLoc)
	    
	    if i_module:#if we have a module, connect vis
		i_upLoc.overrideEnabled = 1		
		cgmMeta.cgmAttr(i_module.rigNull.mNode,'visRig',lock=False).doConnectOut("%s.%s"%(i_upLoc.mNode,'overrideVisibility'))
	    
	
        #>> Surface Anchor ===================================================
    #Orient constrain our last joint to our last follicle
    #>>>DON'T Like this method --- mc.orientConstraint(ml_follicleTransforms[-1].mNode,ml_jointList[-1].mNode,maintainOffset = True)
    
    #>>>Create scale stuff
    #>>>Create IK effectors,Create distance nodes
    l_iIK_effectors = []
    l_iIK_handles = []  
    l_iDistanceObjects = []
    i_distanceShapes = []  
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        ik_buffer = mc.ikHandle (startJoint=i_jnt.mNode,
                                 endEffector = ml_jointList[i+1].mNode,
                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                 enableHandles=True )
        #Handle
        i_IK_Handle = cgmMeta.cgmObject(ik_buffer[0])
        i_IK_Handle.parent = ml_follicleTransforms[i+1].mNode
        i_IK_Handle.doStore('cgmName',i_jnt.mNode)    
        i_IK_Handle.doName()
        
        #Effector
        i_IK_Effector = cgmMeta.cgmObject(ik_buffer[1])        
        #i_IK_Effector.doStore('cgmName',i_jnt.mNode)    
        i_IK_Effector.doName()
        
        l_iIK_handles.append(i_IK_Handle)
        l_iIK_effectors.append(i_IK_Effector)
        
	if i_module:#if we have a module, connect vis
	    i_IK_Handle.overrideEnabled = 1		
	    cgmMeta.cgmAttr(i_module.rigNull.mNode,'visRig',lock=False).doConnectOut("%s.%s"%(i_IK_Handle.mNode,'overrideVisibility'))
        
        #>> Distance nodes
        i_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
        i_distanceObject = cgmMeta.cgmObject( i_distanceShape.getTransform() )
        i_distanceObject.doStore('cgmName',i_jnt.mNode)
        i_distanceObject.addAttr('cgmType','measureNode',lock=True)
        i_distanceObject.doName(nameShapes = True)
	i_distanceObject.parent = i_grp.mNode#parent it
        i_distanceObject.overrideEnabled = 1
        i_distanceObject.overrideVisibility = 0
	
        #Connect things
        mc.connectAttr ((ml_follicleTransforms[i].mNode+'.translate'),(i_distanceShape.mNode+'.startPoint'))
        mc.connectAttr ((ml_follicleTransforms[i+1].mNode+'.translate'),(i_distanceShape.mNode+'.endPoint'))
        
        l_iDistanceObjects.append(i_distanceObject)
        i_distanceShapes.append(i_distanceShape)
	
	if i_module:#Connect hides if we have a module instance:
	    cgmMeta.cgmAttr(i_module.rigNull.mNode,'visRig',lock=False).doConnectOut("%s.%s"%(i_distanceObject.mNode,'overrideVisibility'))
	
            
    #Connect the first joint's position since an IK handle isn't controlling it    
    attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[0].mNode,'%s.translate'%ml_jointList[0].mNode)
    #attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[-1].mNode,'%s.translate'%ml_jointList[-1].mNode)
    
    #>> Second part for the full twist setup
    aimChannel = orientation[0]  
    fixOptions = [0,90,180,-90,-180]      

    for i,i_jnt in enumerate(ml_jointList[:-1]):
	rotBuffer = mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)
	log.info("rotBuffer: %s"%rotBuffer)
	#Create the poleVector
	poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,l_iIK_handles[i].mNode)  	
	optionCnt = 0
	while not cgmMath.isFloatEquivalent((mc.getAttr(i_jnt.mNode+'.r'+aimChannel)),0):
	    log.info("%s.r%s: %s"%(i_jnt.getShortName(),aimChannel,mc.getAttr(i_jnt.mNode+'.r'+aimChannel)))
	    log.info ("Trying the following for '%s':%s" %(l_iIK_handles[i].getShortName(),fixOptions[optionCnt]))
	    attributes.doSetAttr(l_iIK_handles[i].mNode,'twist',fixOptions[optionCnt])
	    optionCnt += 1
	    if optionCnt == 4:
		raise StandardError,"failed to find a good twist value to zero out poleVector: %s"%(i_jnt.getShortName())
	    
	if mc.xform (i_jnt.mNode, q=True, ws=True, ro=True) != rotBuffer:
	    log.info("Found the following on '%s': %s"%(i_jnt.getShortName(),mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)))

    #>>>Hook up scales
    #==========================================================================
    #Translate scale
    """
    for i,i_jnt in enumerate(ml_jointList[1:]):
	#i is already offset, which we need as we want i to be the partn
	attributes.doConnectAttr('%s.%s'%(i_distanceShapes[i].mNode,'distance'),#>>
                                 '%s.t%s'%(i_jnt.mNode,orientation[0]))	   """ 
    
    #Buffer
    i_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
    i_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
    i_jntScaleBufferNode.addAttr('masterScale',value = 1.0, attrType='float')        
    i_jntScaleBufferNode.doName()
    
    i_jntScaleBufferNode.connectParentNode(i_controlSurface.mNode,'surface','scaleBuffer')
    ml_mainMDs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):
	
	#Store our distance base to our buffer
        try:i_jntScaleBufferNode.store(i_distanceShapes[i].distance)#Store to our buffer
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to store joint distance: %s"%i_distanceShapes[i].mNode
	
	#Create the mdNode
	i_md = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_md.operation = 2
	i_md.doStore('cgmName',i_jnt.mNode)
	i_md.addAttr('cgmTypeModifier','masterScale')
	i_md.doName()
	attributes.doConnectAttr('%s.%s'%(i_distanceShapes[i].mNode,'distance'),#>>
	                         '%s.%s'%(i_md.mNode,'input1X'))
	attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
	                         '%s.%s'%(i_md.mNode,'input2X'))
	
	#Connect to the joint
	i_attr = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"distance_%s"%i,attrType = 'float',initialValue=0,lock=True)		
	i_attrResult = cgmMeta.cgmAttr(i_jntScaleBufferNode.mNode,"scaleResult_%s"%i,attrType = 'float',initialValue=0,lock=True)	
	try:
	    i_attr.doConnectIn('%s.%s'%(i_distanceShapes[i].mNode,'distance'))
	    i_attrResult.doConnectIn('%s.%s'%(i_md.mNode,'output.outputX'))
	    i_attrResult.doConnectOut('%s.s%s'%(i_jnt.mNode,orientation[0]))
	    
	    for axis in orientation[1:]:
		attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,'masterScale'),#>>
		                         '%s.s%s'%(i_jnt.mNode,axis))	    
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to connect joint attrs: %s"%i_jnt.mNode
	
	#mc.pointConstraint(ml_follicleTransforms[i].mNode,i_jnt.mNode,maintainOffset = False)
	ml_mainMDs.append(i_md)#store the md
	

	
    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
	attributes.doConnectAttr('%s.%s'%(ml_jointList[-2].mNode,axis),#>>
                                 '%s.%s'%(ml_jointList[-1].mNode,axis))	 
	
    return {'i_controlSurface':i_controlSurface,'controlSurface':i_controlSurface.mNode,'surfaceScaleBuffer':i_jntScaleBufferNode.mNode,'i_surfaceScaleBuffer':i_jntScaleBufferNode,'l_joints':jointList,'l_iJoints':ml_jointList}
@r9General.Timer
def createConstraintSurfaceSegmentTranslatePosition(jointList,orientation = 'zyx',baseName ='test', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]
    
    i_module = False
    i_rigNull = False
    if moduleInstance is not None:
	if issubclass(type(moduleInstance),cgmPM.cgmModule):
	    i_module = moduleInstance
	    i_rigNull = i_module.rigNull
	else:
	    log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    
    #Create our group
    i_grp = cgmMeta.cgmObject(name = 'newgroup')
    i_grp.addAttr('cgmName', str(baseName), lock=True)
    i_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    i_grp.doName()
    
    #Create surface
    l_surfaceReturn = joints.loftSurfaceFromJointList(jointList,outChannel)
    
    i_controlSurface = cgmMeta.cgmObject( l_surfaceReturn[0] )
    i_controlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_controlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
    i_controlSurface.doName()
    i_controlSurface.addAttr('mClass','cgmObject')
    
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Create folicles
    ml_follicleTransforms = []
    ml_follicleShapes = []
    l_snapToGroups = []
    il_snapToGroups = []
    il_upLocs = []
    
    #First thing we're going to do is create our follicles
    for i_jnt in ml_jointList:       
        l_closestInfo = distance.returnClosestPointOnSurfaceInfo(i_jnt.mNode,i_controlSurface.mNode)
        log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
        #>>> Follicle =======================================================
        l_follicleInfo = nodes.createFollicleOnMesh(i_controlSurface.mNode)
        i_follicleTrans = cgmMeta.cgmObject(l_follicleInfo[1])
        i_follicleShape = cgmMeta.cgmNode(l_follicleInfo[0])
        #> Name
        i_follicleTrans.doStore('cgmName',i_jnt.mNode)
        i_follicleTrans.doName()
        #>Set follicle value
        i_follicleShape.parameterU = l_closestInfo['normalizedU']
        i_follicleShape.parameterV = l_closestInfo['normalizedV']
        
        ml_follicleShapes.append(i_follicleShape)
        ml_follicleTransforms.append(i_follicleTrans)
	
	i_follicleTrans.parent = i_grp.mNode	
	
        #>> Surface Anchor ===================================================
        i_grpPos = cgmMeta.cgmObject( rigging.groupMeObject(i_jnt.mNode,False) )
        i_grpPos.doStore('cgmName',i_jnt.mNode)        
        i_grpOrient = cgmMeta.cgmObject( mc.duplicate(i_grpPos.mNode,returnRootsOnly=True,ic=True)[0] )
        i_grpPos.addAttr('cgmType','surfaceAnchor',attrType='string',lock=True)
        i_grpOrient.addAttr('cgmType','surfaceOrient',attrType='string',lock=True)
        i_grpPos.doName()
        i_grpOrient.doName()
        i_grpOrient.parent = i_grpPos.mNode
	
	i_jnt.connectParentNode(i_grpOrient.mNode,'snapToGroup','snapTarget')	
	
	#Contrain pos group
        constraint = mc.parentConstraint(i_follicleTrans.mNode,i_grpPos.mNode, maintainOffset=False)
	
	i_upLoc = i_jnt.doLoc()#Make up Loc
	i_upLoc.parent = i_grpPos.mNode
	mc.move(0,2,0,i_upLoc.mNode,os=True)
	
	#mc.aimConstraint(ml_jointList[],objGroup,maintainOffset = False, weight = 1, aimVector = aimVector, upVector = upVector, worldUpObject = upLoc, worldUpType = 'object' )        
        l_snapToGroups.append(i_grpOrient.mNode)
	il_snapToGroups.append(i_grpOrient)
	il_upLocs.append(i_upLoc)
	
    for i,i_grp in enumerate(il_snapToGroups[:-1]):
	mc.aimConstraint(il_snapToGroups[i+1].mNode,i_grp.mNode,
	                 maintainOffset = False, weight = 1,
	                 aimVector = [0,0,1], upVector = [0,1,0],
	                 worldUpObject = il_upLocs[i].mNode,
	                 worldUpType = 'object' )        
	
	
    return {'i_controlSurface':i_controlSurface,'controlSurface':i_controlSurface.mNode,
            'il_snapToGroups':il_snapToGroups,'l_snapToGroups':l_snapToGroups}
    
@r9General.Timer
def createControlSurfaceSegment2(jointList,orientation = 'zyx',baseName ='test', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]
    
    i_module = False
    i_rigNull = False
    if moduleInstance is not None:
	if issubclass(type(moduleInstance),cgmPM.cgmModule):
	    i_module = moduleInstance
	    i_rigNull = i_module.rigNull
	else:
	    log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    
    #Create our group
    i_grp = cgmMeta.cgmObject(name = 'newgroup')
    i_grp.addAttr('cgmName', str(baseName), lock=True)
    i_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    i_grp.doName()
    
    #Create surface
    l_surfaceReturn = joints.loftSurfaceFromJointList(jointList,outChannel)
    
    i_controlSurface = cgmMeta.cgmObject( l_surfaceReturn[0] )
    i_controlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_controlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
    i_controlSurface.doName()
    i_controlSurface.addAttr('mClass','cgmObject')
    
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Create folicles
    ml_follicleTransforms = []
    ml_follicleShapes = []
    ml_upGroups = []
    
    #First thing we're going to do is create our follicles
    for i,i_jnt in enumerate(ml_jointList):       
        l_closestInfo = distance.returnClosestPointOnSurfaceInfo(i_jnt.mNode,i_controlSurface.mNode)
        log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
        #>>> Follicle =======================================================
        l_follicleInfo = nodes.createFollicleOnMesh(i_controlSurface.mNode)
        i_follicleTrans = cgmMeta.cgmObject(l_follicleInfo[1],setClass=True)
        i_follicleShape = cgmMeta.cgmNode(l_follicleInfo[0])
        #> Name
        i_follicleTrans.doStore('cgmName',i_jnt.mNode)
        i_follicleTrans.doName()
        #>Set follicle value
        i_follicleShape.parameterU = l_closestInfo['normalizedU']
        i_follicleShape.parameterV = l_closestInfo['normalizedV']
        
        ml_follicleShapes.append(i_follicleShape)
        ml_follicleTransforms.append(i_follicleTrans)
	
	i_follicleTrans.parent = i_grp.mNode	
	
	#>>> loc
	"""
	First part of full ribbon wist setup
	"""
	if i_jnt != ml_jointList[-1]:
	    i_upLoc = i_jnt.doLoc()#Make up Loc
	    i_locRotateGroup = i_jnt.duplicateTransform(False)#group in place
	    i_locRotateGroup.parent = i_follicleTrans.mNode
	    i_locRotateGroup.doStore('cgmName',i_jnt.mNode)	    
	    i_locRotateGroup.addAttr('cgmTypeModifier','rotate',lock=True)
	    i_locRotateGroup.doName()
	    
	    #Store the rotate group to the joint
	    i_jnt.connectChildNode(i_locRotateGroup,'rotateUpGroup','drivenJoint')
	    i_zeroGrp = cgmMeta.cgmObject( i_locRotateGroup.doGroup(True),setClass=True )
	    i_zeroGrp.addAttr('cgmTypeModifier','zero',lock=True)
	    i_zeroGrp.doName()
	    #connect some other data
	    i_locRotateGroup.connectChildNode(i_follicleTrans,'follicle','drivenGroup')
	    i_locRotateGroup.connectChildNode(i_locRotateGroup.parent,'zeroGroup')
	    
	    mc.makeIdentity(i_locRotateGroup.mNode, apply=True,t=1,r=1,s=1,n=0)
	    
	    
	    i_upLoc.parent = i_locRotateGroup.mNode
	    mc.move(0,10,0,i_upLoc.mNode,os=True)	
	    ml_upGroups.append(i_upLoc)
	    
	
        #>> Surface Anchor ===================================================
        """
        i_grpPos = cgmMeta.cgmObject( rigging.groupMeObject(i_jnt.mNode,False) )
        i_grpPos.doStore('cgmName',i_jnt.mNode)        
        i_grpOrient = cgmMeta.cgmObject( mc.duplicate(i_grpPos.mNode,returnRootsOnly=True)[0] )
        i_grpPos.addAttr('cgmType','surfaceAnchor',attrType='string',lock=True)
        i_grpOrient.addAttr('cgmType','surfaceOrient',attrType='string',lock=True)
        i_grpPos.doName()
        i_grpOrient.doName()
        i_grpOrient.parent = i_grpPos.mNode
        
        constraint = mc.pointConstraint(i_transFollicle.mNode,i_grpPos.mNode, maintainOffset=False)
        constraint = mc.orientConstraint(i_transFollicle.mNode,i_grpPos.mNode, maintainOffset=False)
        """

    #Orient constrain our last joint to our last follicle
    #>>>DON'T Like this method --- mc.orientConstraint(ml_follicleTransforms[-1].mNode,ml_jointList[-1].mNode,maintainOffset = True)
    
    #>>>Create scale stuff
    #>>>Create IK effectors,Create distance nodes
    l_iIK_effectors = []
    l_iIK_handles = []  
    l_iDistanceObjects = []
    i_distanceShapes = []  
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        ik_buffer = mc.ikHandle (startJoint=i_jnt.mNode,
                                 endEffector = ml_jointList[i+1].mNode,
                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                 enableHandles=True )
        #Handle
        i_IK_Handle = cgmMeta.cgmObject(ik_buffer[0],setClass=True)
        i_IK_Handle.parent = ml_follicleTransforms[i+1].mNode
        i_IK_Handle.doStore('cgmName',i_jnt.mNode)    
        i_IK_Handle.doName()
        
        #Effector
        i_IK_Effector = cgmMeta.cgmObject(ik_buffer[1],setClass=True)        
        i_IK_Effector.doName()
        
        l_iIK_handles.append(i_IK_Handle)
        l_iIK_effectors.append(i_IK_Effector)	
        
        #>> Distance nodes
        i_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
        i_distanceObject = cgmMeta.cgmObject( i_distanceShape.getTransform() )
        i_distanceObject.doStore('cgmName',i_jnt.mNode)
        i_distanceObject.addAttr('cgmType','measureNode',lock=True)
        i_distanceObject.doName(nameShapes = True)
	i_distanceObject.parent = i_grp.mNode#parent it
        i_distanceObject.overrideEnabled = 1
        i_distanceObject.overrideVisibility = 0
	
        #Connect things
        mc.connectAttr ((ml_follicleTransforms[i].mNode+'.translate'),(i_distanceShape.mNode+'.startPoint'))
        mc.connectAttr ((ml_follicleTransforms[i+1].mNode+'.translate'),(i_distanceShape.mNode+'.endPoint'))
        
        l_iDistanceObjects.append(i_distanceObject)
        i_distanceShapes.append(i_distanceShape)
            
    #Connect the first joint's position since an IK handle isn't controlling it    
    attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[0].mNode,'%s.translate'%ml_jointList[0].mNode)
    #attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[-1].mNode,'%s.translate'%ml_jointList[-1].mNode)
    
    #>> Second part for the full twist setup
    aimChannel = orientation[0]  
    fixOptions = [0,90,180,-90,-180]      

    for i,i_jnt in enumerate(ml_jointList[:-1]):
	rotBuffer = mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)
	log.info("rotBuffer: %s"%rotBuffer)
	#Create the poleVector
	poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,l_iIK_handles[i].mNode)  	
	optionCnt = 0
	while not cgmMath.isFloatEquivalent((mc.getAttr(i_jnt.mNode+'.r'+aimChannel)),0):
	    log.info("%s.r%s: %s"%(i_jnt.getShortName(),aimChannel,mc.getAttr(i_jnt.mNode+'.r'+aimChannel)))
	    log.info ("Trying the following for '%s':%s" %(l_iIK_handles[i].getShortName(),fixOptions[optionCnt]))
	    attributes.doSetAttr(l_iIK_handles[i].mNode,'twist',fixOptions[optionCnt])
	    optionCnt += 1
	    if optionCnt == 4:
		raise StandardError,"failed to find a good twist value to zero out poleVector: %s"%(i_jnt.getShortName())
	    
	if mc.xform (i_jnt.mNode, q=True, ws=True, ro=True) != rotBuffer:
	    log.info("Found the following on '%s': %s"%(i_jnt.getShortName(),mc.xform (i_jnt.mNode, q=True, ws=True, ro=True)))

    #>>>Hook up scales
    #===================================================================
    #World scale
    
    #Buffer
    i_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
    i_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
    i_jntScaleBufferNode.addAttr('masterScale',value = 1.0, attrType='float')        
    i_jntScaleBufferNode.doName()
    
    i_jntScaleBufferNode.connectParentNode(i_controlSurface.mNode,'surface','scaleBuffer')
    ml_mainMDs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):
	#Store our distance base to our buffer
        try:i_jntScaleBufferNode.store(i_distanceShapes[i].distance)#Store to our buffer
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to store joint distance: %s"%i_distanceShapes[i].mNode
	
	#Create the mdNode
	i_md = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_md.operation = 2
	i_md.doStore('cgmName',i_jnt.mNode)
	i_md.addAttr('cgmTypeModifier','masterScale')
	i_md.doName()
	attributes.doConnectAttr('%s.%s'%(i_distanceShapes[i].mNode,'distance'),#>>
	                         '%s.%s'%(i_md.mNode,'input1X'))
	attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
	                         '%s.%s'%(i_md.mNode,'input2X'))
	
	#Connect to the joint
	try:
	    attributes.doConnectAttr('%s.%s'%(i_md.mNode,'output.outputX'),#>>
		                     '%s.s%s'%(i_jnt.mNode,orientation[0]))
	    for axis in orientation[1:]:
		attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,'masterScale'),#>>
		                         '%s.s%s'%(i_jnt.mNode,axis))	    
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to connect joint attrs: %s"%i_jnt.mNode
	
	ml_mainMDs.append(i_md)#store the md
	
	#If second to last we need to add an extra md
	
    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
	attributes.doConnectAttr('%s.%s'%(ml_jointList[-2].mNode,axis),#>>
                                 '%s.%s'%(ml_jointList[-1].mNode,axis))	 
	
    return {'i_controlSurface':i_controlSurface,'controlSurface':i_controlSurface.mNode,'surfaceScaleBuffer':i_jntScaleBufferNode.mNode,'i_surfaceScaleBuffer':i_jntScaleBufferNode,'l_joints':jointList,'l_iJoints':ml_jointList}
    
@r9General.Timer
def createControlSurfaceSegmentBAK2(jointList,orientation = 'zyx',baseName ='test', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]
    
    i_module = False
    i_rigNull = False
    if moduleInstance is not None:
	if issubclass(type(moduleInstance),cgmPM.cgmModule):
	    i_module = moduleInstance
	    i_rigNull = i_module.rigNull
	else:
	    log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    
    #Create our group
    i_grp = cgmMeta.cgmObject(name = 'newgroup')
    i_grp.addAttr('cgmName', str(baseName), lock=True)
    i_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    i_grp.doName()
    
    #Create surface
    l_surfaceReturn = joints.loftSurfaceFromJointList(jointList,outChannel)
    
    i_controlSurface = cgmMeta.cgmObject( l_surfaceReturn[0] )
    i_controlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    i_controlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
    i_controlSurface.doName()
    i_controlSurface.addAttr('mClass','cgmObject')
    
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Create folicles
    ml_follicleTransforms = []
    ml_follicleShapes = []
    ml_upGroups = []
    
    #First thing we're going to do is create our follicles
    for i,i_jnt in enumerate(ml_jointList):       
        l_closestInfo = distance.returnClosestPointOnSurfaceInfo(i_jnt.mNode,i_controlSurface.mNode)
        log.debug("%s : %s"%(i_jnt.mNode,l_closestInfo))
        #>>> Follicle =======================================================
        l_follicleInfo = nodes.createFollicleOnMesh(i_controlSurface.mNode)
        i_follicleTrans = cgmMeta.cgmObject(l_follicleInfo[1])
        i_follicleShape = cgmMeta.cgmNode(l_follicleInfo[0])
        #> Name
        i_follicleTrans.doStore('cgmName',i_jnt.mNode)
        i_follicleTrans.doName()
        #>Set follicle value
        i_follicleShape.parameterU = l_closestInfo['normalizedU']
        i_follicleShape.parameterV = l_closestInfo['normalizedV']
        
        ml_follicleShapes.append(i_follicleShape)
        ml_follicleTransforms.append(i_follicleTrans)
	
	i_follicleTrans.parent = i_grp.mNode	
	
	#>>> loc
	"""
	i_upLoc = i_jnt.doLoc()#Make up Loc
	i_upLoc.parent = i_follicleTrans.mNode
	mc.move(0,2,0,i_upLoc.mNode,os=True)	
	ml_upGroups.append(i_upLoc)
	"""
	
        #>> Surface Anchor ===================================================
        """
        i_grpPos = cgmMeta.cgmObject( rigging.groupMeObject(i_jnt.mNode,False) )
        i_grpPos.doStore('cgmName',i_jnt.mNode)        
        i_grpOrient = cgmMeta.cgmObject( mc.duplicate(i_grpPos.mNode,returnRootsOnly=True)[0] )
        i_grpPos.addAttr('cgmType','surfaceAnchor',attrType='string',lock=True)
        i_grpOrient.addAttr('cgmType','surfaceOrient',attrType='string',lock=True)
        i_grpPos.doName()
        i_grpOrient.doName()
        i_grpOrient.parent = i_grpPos.mNode
        
        constraint = mc.pointConstraint(i_transFollicle.mNode,i_grpPos.mNode, maintainOffset=False)
        constraint = mc.orientConstraint(i_transFollicle.mNode,i_grpPos.mNode, maintainOffset=False)
        """
        
        #>>>Connect via constraint - no worky
        #constraint = mc.pointConstraint(i_grpOrient.mNode,i_jnt.mNode, maintainOffset=True)
        #constraint = mc.orientConstraint(i_grpOrient.mNode,i_jnt.mNode, maintainOffset=True)
        
        #constraints.doConstraintObjectGroup(i_transFollicle.mNode,transform,['point','orient'])
        #>>> Connect the joint
        #attributes.doConnectAttr('%s.translate'%i_grpPos.mNode,'%s.translate'%i_jnt.mNode)
        
    #>>>Create scale stuff
    #>>>Create IK effectors,Create distance nodes
    l_iIK_effectors = []
    l_iIK_handles = []  
    l_iDistanceObjects = []
    i_distanceShapes = []  
    for i,i_jnt in enumerate(ml_jointList[:-1]):
        ik_buffer = mc.ikHandle (startJoint=i_jnt.mNode,
                                 endEffector = ml_jointList[i+1].mNode,
                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                 enableHandles=True )
        #Handle
        i_IK_Handle = cgmMeta.cgmObject(ik_buffer[0])
        i_IK_Handle.parent = ml_follicleTransforms[i+1].mNode
        i_IK_Handle.doStore('cgmName',i_jnt.mNode)    
        i_IK_Handle.doName()
        
        #Effector
        i_IK_Effector = cgmMeta.cgmObject(ik_buffer[1])        
        #i_IK_Effector.doStore('cgmName',i_jnt.mNode)    
        i_IK_Effector.doName()
        
        l_iIK_handles.append(i_IK_Handle)
        l_iIK_effectors.append(i_IK_Effector)
        
        #>> create up loc
        #i_loc = i_jnt.doLoc()
        #mc.move(0, 10, 0, i_loc.mNode, r=True,os=True,wd=True)
	
        """poleVector = mc.poleVectorConstraint (ml_upGroups[i].mNode,i_IK_Handle.mNode)"""
        
        #>> Distance nodes
        i_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
        i_distanceObject = cgmMeta.cgmObject( i_distanceShape.getTransform() )
        i_distanceObject.doStore('cgmName',i_jnt.mNode)
        i_distanceObject.addAttr('cgmType','measureNode',lock=True)
        i_distanceObject.doName(nameShapes = True)
	i_distanceObject.parent = i_grp.mNode#parent it
        i_distanceObject.overrideEnabled = 1
        i_distanceObject.overrideVisibility = 0
	
        #Connect things
        mc.connectAttr ((ml_follicleTransforms[i].mNode+'.translate'),(i_distanceShape.mNode+'.startPoint'))
        mc.connectAttr ((ml_follicleTransforms[i+1].mNode+'.translate'),(i_distanceShape.mNode+'.endPoint'))
        
        l_iDistanceObjects.append(i_distanceObject)
        i_distanceShapes.append(i_distanceShape)
            
    #Connect the first joint's position since an IK handle isn't controlling it    
    attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[0].mNode,'%s.translate'%ml_jointList[0].mNode)
    
    #>>>Hook up scales
    #World scale
    
    #Buffer
    i_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
    i_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
    i_jntScaleBufferNode.addAttr('masterScale',value = 1.0, attrType='float')        
    i_jntScaleBufferNode.doName()
    
    i_jntScaleBufferNode.connectParentNode(i_controlSurface.mNode,'surface','scaleBuffer')
    
    for i,i_jnt in enumerate(ml_jointList[:-1]):
	#Store our distance base to our buffer
        try:i_jntScaleBufferNode.store(i_distanceShapes[i].distance)#Store to our buffer
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to store joint distance: %s"%i_distanceShapes[i].mNode
	
	#Create the mdNode
	i_md = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_md.operation = 2
	i_md.doStore('cgmName',i_jnt.mNode)
	i_md.addAttr('cgmTypeModifier','masterScale')
	i_md.doName()
	attributes.doConnectAttr('%s.%s'%(i_distanceShapes[i].mNode,'distance'),#>>
	                         '%s.%s'%(i_md.mNode,'input1X'))
	attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,i_jntScaleBufferNode.d_indexToAttr[i]),#>>
	                         '%s.%s'%(i_md.mNode,'input2X'))
	
	#Connect to the joint
	try:
	    attributes.doConnectAttr('%s.%s'%(i_md.mNode,'output.outputX'),#>>
		                     '%s.s%s'%(i_jnt.mNode,orientation[0]))
	    for axis in orientation[1:]:
		attributes.doConnectAttr('%s.%s'%(i_jntScaleBufferNode.mNode,'masterScale'),#>>
		                         '%s.s%s'%(i_jnt.mNode,axis))	    
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to connect joint attrs: %s"%i_jnt.mNode
	
	"""
	mdArg = [{'result':[i_jnt.mNode,'sy'],'drivers':[[i_distanceShapes[i].mNode,'distance'],[i_jntScaleBufferNode,i_jntScaleBufferNode.d_indexToAttr[i]]],'driven':[]},
	         {'result':[i_jnt.mNode,'sx'],'drivers':[[i_distanceShapes[i].mNode,'distance'],[i_jntScaleBufferNode,i_jntScaleBufferNode.d_indexToAttr[i]]],'driven':[]}]
	#mdArg = [{'drivers':[[i_jntScaleBufferNode,'masterScale'],[i_jntScaleBufferNode,i_jntScaleBufferNode.d_indexToAttr[i]]],
	          #'driven':[[i_jnt.mNode,'sy'],[i_jnt.mNode,'sx']]}]
        
        try:NodeF.build_mdNetwork(mdArg, defaultAttrType='float',operation=2)
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to build network: %s"%mdArg 
	"""
	
    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
	attributes.doConnectAttr('%s.%s'%(ml_jointList[-2].mNode,axis),#>>
                                 '%s.%s'%(ml_jointList[-1].mNode,axis))	 
	
    return {'i_controlSurface':i_controlSurface,'controlSurface':i_controlSurface.mNode,'surfaceScaleBuffer':i_jntScaleBufferNode.mNode,'i_surfaceScaleBuffer':i_jntScaleBufferNode,'l_joints':jointList,'l_iJoints':ml_jointList}
    
        
@r9General.Timer
def addRibbonTwistToControlSurfaceSetup(jointList,
                                        startControlDriver = None, endControlDriver = None,
                                        rotateGroupAxis = 'rotateZ',
                                        orientation = 'zyx', moduleInstance = None):
    """
    Implementing this ribbon method to or control surface setup:
    http://faithofthefallen.wordpress.com/2008/10/08/awesome-spine-setup/
    """
    def createAverageNode(driver1,driver2,driven = None):
	#Create the mdNode
	log.info("driver1: %s"%driver1)
	log.info("driver2: %s"%driver2)
	assert type(driver1) is list and len(driver1) == 2,"Driver1 wrong: %s"%driver1
	assert type(driver2) is list and len(driver1) == 2,"Driver2 wrong: %s"%driver2
	driver1Combined = "%s.%s"%(driver1[0],driver1[1])
	driver2Combined = "%s.%s"%(driver2[0],driver2[1])
	assert mc.objExists(driver1Combined)	
	assert mc.objExists(driver2Combined)
	
	if driven is not None:
	    assert type(driven) is list and len(driver1) == 2,"Driven wrong: %s"%driven	    
	    drivenCombined = "%s.%s"%(driven[0],driven[1])
	    assert mc.objExists(drivenCombined)	    
	    log.info("drivenCombined: %s"%drivenCombined)
	    
	log.info("driver1Combined: %s"%driver1Combined)
	log.info("driver2Combined: %s"%driver2Combined)
	
	#Create the node
	i_pma = cgmMeta.cgmNode(mc.createNode('plusMinusAverage'))
	i_pma.operation = 3
	nameBuffer = "%s_to_%s"%(mc.ls(driver1[0],sn = True)[0],mc.ls(driver2[0],sn = True)[0])
	i_pma.addAttr('cgmName',nameBuffer,lock=True)	
	#i_pma.doStore('cgmName',i_jnt.mNode)
	i_pma.addAttr('cgmTypeModifier','twist')
	i_pma.doName()
	
	#Make our connections
	attributes.doConnectAttr(driver1Combined,'%s.input1D[0]'%i_pma.mNode)
	attributes.doConnectAttr(driver2Combined,'%s.input1D[1]'%i_pma.mNode)
	
	if driven is not None:
	    attributes.doConnectAttr('%s.output1D'%i_pma.mNode,drivenCombined)
	    
	return i_pma

    def averageNetwork_three(indices):
	""" """
	log.info("averageNetwork_three: %s"%indices)
	assert len(indices) == 3,"averageNetwork_three requires 3 indices"
	for i in indices:
	    if i not in d_drivenPlugs.keys():
		raise StandardError,"Index doesn't exist in d_drivenPlugs: %s"%i
	d1 = d_driverPlugs[indices[0]]
	d2 = d_driverPlugs[indices[-1]]
	driven = d_drivenPlugs[indices[1]]
	
	i_buffer = createAverageNode(d1,d2,driven)
	#Register network
	d_driverPlugs[indices[1]] = [i_buffer.mNode,"output1D"]
	
    def averageNetwork_four(indices):
	""" 
	If we don't have an actual middle object we still need to average
	ex[0,1,2,3]
	[0,3]
	[0,3],1 | [0,3],2
	"""
	log.info("averageNetwork_four: %s"%indices)
	assert len(indices) == 4,"averageNetwork_four requires 4 indices"
	for i in indices:
	    if i not in d_drivenPlugs.keys():
		raise StandardError,"Index doesn't exist in d_drivenPlugs: %s"%i
	assert indices[0] in d_drivenPlugs.keys(),"four mode indice not in d_drivenPlugs: %s"%indices[0]
	assert indices[-1] in d_drivenPlugs.keys(),"four mode indice not in d_drivenPlugs: %s"%indices[-1]
	
	#Get the middle driven
	driven1 = d_drivenPlugs[indices[1]]	
	driven2 = d_drivenPlugs[indices[2]]	
	driver1 = d_driverPlugs[indices[0]]
	driver2 = d_driverPlugs[indices[-1]]
	
	#Blend average
	blendDriverIndex = (indices[0],indices[-1])	
	try:
	    if blendDriverIndex not in d_drivenPlugs.keys():
		#If our blend driver isn't in the keys, we need to make it. first check the drivers exist
		i_blendPMA = createAverageNode(driver1,driver2)
		blendConnection = [i_blendPMA.mNode,"output1D"]
	    else:
		blendConnection = d_drivenPlugs[blendDriverIndex]
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"averageNetwork_four>failed to find or build blendDriver: %s"%blendDriverIndex
	
	
	#Hook up first
	createAverageNode(blendConnection,
                          driver1,
                          d_drivenPlugs[1])	
	#Hook up second
	createAverageNode(blendConnection,
                          driver2,
                          d_drivenPlugs[2])	
	
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2].capitalize()
    upChannel = orientation[1].capitalize()
    aimChannel = orientation[0].capitalize()
    if len(jointList) <3:
	raise StandardError,"addRibbonTwistToControlSurfaceSetup requires 3 joints to work" 
    
    #moduleInstance
    i_module = False
    i_rigNull = False
    if moduleInstance is not None:
	if issubclass(type(moduleInstance),cgmPM.cgmModule):
	    i_module = moduleInstance
	    i_rigNull = i_module.rigNull
	else:
	    log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
	    
    #Initialize joint list
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Gather info:
    #d_driverPlugs = {index:['obj','ry']....}
    #d_drivenPlugs = {index:['rotateGroup','.r']...}
    #twistStartPlug,twistEndPlug
    #For each joint to be connected, we need a connection plug and a rotate group
    #We need a driver start and end plug    
    d_drivenPlugs = {}
    d_driverPlugs = {}
    d_mi_jointToIndex = {}
    #Make sure all but the last have rotate groups,grab those plugs
    for i,i_jnt in enumerate(ml_jointList):
	d_mi_jointToIndex[i_jnt]=i
	if i_jnt == ml_jointList[-1]:#If it's the last
	    d_drivenPlugs[i] = [i_jnt.getShortName(),"rotate%s"%aimChannel]
	else:   
	    rotateGroupBuffer = i_jnt.getMessage('rotateUpGroup',False)[0]
	    if not rotateGroupBuffer:
		raise StandardError,"'%s' lacks a connected rotateUpGroup!"%i_jnt.getShortName()
	    if mc.objExists('%s.%s'%(rotateGroupBuffer,rotateGroupAxis)):
		d_drivenPlugs[i] = [rotateGroupBuffer,rotateGroupAxis]
		#We need to reparent and point constrain our rotate zero groups
		i_zeroGroup = i_jnt.rotateUpGroup.zeroGroup#Get zero
		i_follicle = i_jnt.rotateUpGroup.follicle#get follicle
		i_zeroGroup.parent = i_follicle.parent#parent zerogroup to follicle
		"""mc.pointConstraint(i_follicle.mNode,i_zeroGroup.mNode,
		                   maintainOffset=False)"""		
		mc.parentConstraint(i_follicle.mNode,i_zeroGroup.mNode,
		                    skipRotate = orientation[0],maintainOffset=True)
		
		
	    else:
		raise StandardError,"Rotate group has no axis: %s!"%rotateGroupAxis
	
    #replace our start and end with our drivers
    d_driverPlugs[0] = startControlDriver
    d_driverPlugs[len(ml_jointList)-1] = endControlDriver

    log.info("drivenPlugs: %s"%d_drivenPlugs)
    log.info("driverPlugs: %s"%d_driverPlugs)
    
    #>>>Setup
    #Connect first and last
    #mc.pointConstraint(i_transFollicle.mNode,i_grpPos.mNode, maintainOffset=False)
    attributes.doConnectAttr('%s.%s'%(startControlDriver[0],startControlDriver[1]),
                             '%s.%s'%(d_drivenPlugs[0][0],d_drivenPlugs[0][1]))
    index = ml_jointList.index(ml_jointList[-1]) 
    mc.orientConstraint(endControlDriver[0],ml_jointList[-1].mNode, maintainOffset=False)
    #Direct connect no worky
    #attributes.doConnectAttr('%s.%s'%(endControlDriver[0],endControlDriver[1]),
                             #'%s.%s'%(d_drivenPlugs[index][0],d_drivenPlugs[index][1]))
    
    #Connect rest
    if len(ml_jointList) == 3:
	#Grab two control drivers, blend between them, drive mid
	index = ml_jointList.index(ml_jointList[1])
	createAverageNode(startControlDriver,endControlDriver,d_drivenPlugs[index])
    elif len(ml_jointList) == 4:
	#Grab two control drivers, blend
	i_blendPMA = createAverageNode(startControlDriver,endControlDriver)
	
	#Hook up first
	createAverageNode([i_blendPMA.mNode,"output1D"],
                          startControlDriver,
                          d_drivenPlugs[1])	
	#Hook up second
	createAverageNode([i_blendPMA.mNode,"output1D"],
                          endControlDriver,
                          d_drivenPlugs[2])		
	"""
	for i in [1,2]:
	    index = ml_jointList.index(ml_jointList[i])
	    createAverageNode("%s.output1D"%i_blendPMA.mNode,
	                      endControlDriver,
	                      d_drivenPlugs[index])"""	    
	
	#averageNetwork_four()
	
    else:#factor and run
	#Make a factored list
	l_factored = lists.returnFactoredConstraintList(range(len(jointList)),3)
	log.info(l_factored)
	try:
	    for chunk in l_factored:
		log.info("On chunk: %s"%chunk)	    
		if len(chunk) == 3:
		    averageNetwork_three(chunk)
		elif len(chunk) == 4:
		    averageNetwork_four(chunk)
		else:
		    raise StandardError,"Chunk too long: %s"%chunk
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Chunk failed to network: %s"%chunk
    """
    #Finally build full sum
    i_pma = cgmMeta.cgmNode(mc.createNode('plusMinusAverage'))
    i_pma.operation = 1#Sum
    if moduleInstance:
	i_pma.addAttr('cgmName',moduleInstance.cgmName,lock=True)	
    i_pma.addAttr('cgmTypeModifier','sum')
    i_pma.doName()
        
    #Make our connections
    for key in d_drivenPlugs.keys():
	log.info(d_drivenPlugs[key])
	log.info('%s.%s'%(d_drivenPlugs[key][0],d_drivenPlugs[key][1]))
	log.info('%s.input1D[%s]'%(i_pma.mNode,i))
	attributes.doConnectAttr('%s.%s'%(d_drivenPlugs[key][0],d_drivenPlugs[key][1]),'%s.input1D[%s]'%(i_pma.mNode,i))
	"""

@r9General.Timer
def addSquashAndStretchToControlSurfaceSetupSCALETRANSLATE(attributeHolder,jointList,orientation = 'zyx', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2].capitalize()
    upChannel = orientation[1].capitalize()
    aimChannel = orientation[0].capitalize()
    
    #moduleInstance
    i_module = False
    i_rigNull = False
    if moduleInstance is not None:
	if issubclass(type(moduleInstance),cgmPM.cgmModule):
	    i_module = moduleInstance
	    i_rigNull = i_module.rigNull
	else:
	    log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    #attributeHolder
    i_holder = cgmMeta.cgmNode(attributeHolder)
    
    #Initialize joint list
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    
    ml_scaleNodes = []
    ml_sqrtNodes = []
    ml_attrs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):
	#make sure attr exists
	i_attr = cgmMeta.cgmAttr(i_holder,"scaleMult_%s"%i,attrType = 'float',initialValue=1)
	outScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%outChannel)
	upScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%upChannel)
	
	#Create the multScale
	i_mdScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_mdScale.operation = 2
	i_mdScale.doStore('cgmName',i_jnt.mNode)
	i_mdScale.addAttr('cgmTypeModifier','multScale')
	i_mdScale.doName()
	for channel in [aimChannel,outChannel,upChannel]:
	    attributes.doConnectAttr('%s.scaleResult_%s'%(i_holder.mNode,i),#>>
	                             '%s.input1%s'%(i_mdScale.mNode,channel))	    
	    """attributes.doConnectAttr('%s.scale%s'%(i_jnt.mNode,aimChannel),#>>
	                             '%s.input1%s'%(i_mdScale.mNode,channel))"""
	    attributes.doConnectAttr('%s'%(outScalePlug),#>>
	                             '%s.input2%s'%(i_mdScale.mNode,channel))
	    
	#Create the sqrtNode
	i_sqrtScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_sqrtScale.operation = 3#set to power
	i_sqrtScale.doStore('cgmName',i_jnt.mNode)
	i_sqrtScale.addAttr('cgmTypeModifier','sqrtScale')
	i_sqrtScale.doName()
	for channel in [aimChannel,outChannel,upChannel]:
	    attributes.doConnectAttr('%s.output%s'%(i_mdScale.mNode,channel),#>>
	                             '%s.input1%s'%(i_sqrtScale.mNode,channel))
	    mc.setAttr("%s.input2"%(i_sqrtScale.mNode)+channel,.5)
	    
	#Create the invScale
	i_invScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_invScale.operation = 2
	i_invScale.doStore('cgmName',i_jnt.mNode)
	i_invScale.addAttr('cgmTypeModifier','invScale')
	i_invScale.doName()
	for channel in [aimChannel,outChannel,upChannel]:
	    mc.setAttr("%s.input1"%(i_invScale.mNode)+channel,1)	    
	    attributes.doConnectAttr('%s.output%s'%(i_sqrtScale.mNode,channel),#>>
	                             '%s.input2%s'%(i_invScale.mNode,channel))
	
	#Create the powScale
	i_powScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_powScale.operation = 3
	i_powScale.doStore('cgmName',i_jnt.mNode)
	i_powScale.addAttr('cgmTypeModifier','powScale')
	i_powScale.doName()
	for channel in [aimChannel,outChannel,upChannel]:
	    attributes.doConnectAttr('%s.output%s'%(i_invScale.mNode,channel),#>>
	                             '%s.input1%s'%(i_powScale.mNode,channel))
	    attributes.doConnectAttr('%s'%(i_attr.p_combinedName),#>>
	                             '%s.input2%s'%(i_powScale.mNode,channel))
	
	#Create the worldScale multiplier node
	i_worldScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_worldScale.operation = 1
	i_worldScale.doStore('cgmName',i_jnt.mNode)
	i_worldScale.addAttr('cgmTypeModifier','worldScale')
	i_worldScale.doName()
	
	for channel in [aimChannel,outChannel,upChannel]:
	    mc.setAttr("%s.input1"%(i_worldScale.mNode)+channel,1)
	    #Connect powScale to the worldScale
	    attributes.doConnectAttr('%s.output%s'%(i_powScale.mNode,channel),#>>
	                             '%s.input1%s'%(i_worldScale.mNode,channel))
	#Connect original plugs
	attributes.doConnectAttr('%s'%(outScalePlug),#>>
                                 '%s.input2%s'%(i_worldScale.mNode,outChannel))  
	attributes.doConnectAttr('%s'%(upScalePlug),#>>
                                 '%s.input2%s'%(i_worldScale.mNode,upChannel)) 
	
	#Connect to joint
	attributes.doConnectAttr('%s.output%s'%(i_worldScale.mNode,outChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,outChannel))  
	attributes.doConnectAttr('%s.output%s'%(i_worldScale.mNode,upChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,upChannel))
	
	'''attributes.doConnectAttr('%s.output%s'%(i_worldScale.mNode,aimChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,aimChannel))	'''
	
	#>>>Fix the translate aim scale
	'''if i>0:
	    aimTransScalePlug = attributes.doBreakConnection(i_jnt.mNode,"translate%s"%aimChannel)
	    log.info(aimTransScalePlug)
	    i_aimScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	    i_aimScale.operation = 2
	    i_aimScale.doStore('cgmName',i_jnt.mNode)
	    i_aimScale.addAttr('cgmTypeModifier','aimScale')
	    i_aimScale.doName()
	    """attributes.doConnectAttr('%s.scaleResult_%s'%(i_holder.mNode,i-1),#>>
		                     '%s.input1%s'%(i_aimScale.mNode,aimChannel))"""
	    attributes.doConnectAttr('%s.scale%s'%(ml_jointList[i-1].mNode,aimChannel),#>>
		                     '%s.input1%s'%(i_aimScale.mNode,aimChannel))	    
	    attributes.doConnectAttr('%s'%aimTransScalePlug,#>>
		                     '%s.input2%s'%(i_aimScale.mNode,aimChannel))	
	    attributes.doConnectAttr('%s.output%s'%(i_aimScale.mNode,aimChannel),#>>
		                     '%s.translate%s'%(i_jnt.mNode,aimChannel))	
	    '''
	ml_attrs.append(i_attr)

@r9General.Timer
def addSquashAndStretchToControlSurfaceSetup(attributeHolder,jointList,orientation = 'zyx', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2].capitalize()
    upChannel = orientation[1].capitalize()
    aimChannel = orientation[0].capitalize()
    
    #moduleInstance
    i_module = False
    i_rigNull = False
    if moduleInstance is not None:
	if issubclass(type(moduleInstance),cgmPM.cgmModule):
	    i_module = moduleInstance
	    i_rigNull = i_module.rigNull
	else:
	    log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    #attributeHolder
    i_holder = cgmMeta.cgmNode(attributeHolder)
    
    #Initialize joint list
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    
    ml_scaleNodes = []
    ml_sqrtNodes = []
    ml_attrs = []
    for i,i_jnt in enumerate(ml_jointList[:-1]):
	#make sure attr exists
	i_attr = cgmMeta.cgmAttr(i_holder,"scaleMult_%s"%i,attrType = 'float',initialValue=1)
	outScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%outChannel)
	upScalePlug = attributes.doBreakConnection(i_jnt.mNode,"scale%s"%upChannel)
	
	#Create the multScale
	i_mdScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_mdScale.operation = 2
	i_mdScale.doStore('cgmName',i_jnt.mNode)
	i_mdScale.addAttr('cgmTypeModifier','multScale')
	i_mdScale.doName()
	for channel in [outChannel,upChannel]:
	    attributes.doConnectAttr('%s.scale%s'%(i_jnt.mNode,aimChannel),#>>
		                     '%s.input1%s'%(i_mdScale.mNode,channel))
	    attributes.doConnectAttr('%s'%(outScalePlug),#>>
		                     '%s.input2%s'%(i_mdScale.mNode,channel))
	    
	#Create the sqrtNode
	i_sqrtScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_sqrtScale.operation = 3#set to power
	i_sqrtScale.doStore('cgmName',i_jnt.mNode)
	i_sqrtScale.addAttr('cgmTypeModifier','sqrtScale')
	i_sqrtScale.doName()
	for channel in [outChannel,upChannel]:
	    attributes.doConnectAttr('%s.output%s'%(i_mdScale.mNode,channel),#>>
	                             '%s.input1%s'%(i_sqrtScale.mNode,channel))
	    mc.setAttr("%s.input2"%(i_sqrtScale.mNode)+channel,.5)
	    
	#Create the invScale
	i_invScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_invScale.operation = 2
	i_invScale.doStore('cgmName',i_jnt.mNode)
	i_invScale.addAttr('cgmTypeModifier','invScale')
	i_invScale.doName()
	for channel in [outChannel,upChannel]:
	    mc.setAttr("%s.input1"%(i_invScale.mNode)+channel,1)	    
	    attributes.doConnectAttr('%s.output%s'%(i_sqrtScale.mNode,channel),#>>
	                             '%s.input2%s'%(i_invScale.mNode,channel))
	
	#Create the powScale
	i_powScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_powScale.operation = 3
	i_powScale.doStore('cgmName',i_jnt.mNode)
	i_powScale.addAttr('cgmTypeModifier','powScale')
	i_powScale.doName()
	for channel in [outChannel,upChannel]:
	    attributes.doConnectAttr('%s.output%s'%(i_invScale.mNode,channel),#>>
		                     '%s.input1%s'%(i_powScale.mNode,channel))
	    attributes.doConnectAttr('%s'%(i_attr.p_combinedName),#>>
		                     '%s.input2%s'%(i_powScale.mNode,channel))
	
	#Create the worldScale multiplier node
	i_worldScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_worldScale.operation = 1
	i_worldScale.doStore('cgmName',i_jnt.mNode)
	i_worldScale.addAttr('cgmTypeModifier','worldScale')
	i_worldScale.doName()
	for channel in [outChannel,upChannel]:
	    mc.setAttr("%s.input1"%(i_worldScale.mNode)+channel,1)
	    #Connect powScale to the worldScale
	    attributes.doConnectAttr('%s.output%s'%(i_powScale.mNode,channel),#>>
	                             '%s.input1%s'%(i_worldScale.mNode,channel))
	#Connect original plugs
	attributes.doConnectAttr('%s'%(outScalePlug),#>>
                                 '%s.input2%s'%(i_worldScale.mNode,outChannel))  
	attributes.doConnectAttr('%s'%(upScalePlug),#>>
                                 '%s.input2%s'%(i_worldScale.mNode,upChannel)) 
	
	#Connect to joint
	attributes.doConnectAttr('%s.output%s'%(i_worldScale.mNode,outChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,outChannel))  
	attributes.doConnectAttr('%s.output%s'%(i_worldScale.mNode,upChannel),#>>
                                 '%s.scale%s'%(i_jnt.mNode,upChannel)) 	
	
	ml_attrs.append(i_attr)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Module and Puppet axis settings
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>      
def doSetAimAxis(self,i):
    """
    Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
    Then Up, and Out is last.
    
    """
    assert i < 6,"%i isn't a viable aim axis integer"%i
    
    self.optionAimAxis.set(i)
    if self.optionUpAxis.get() == self.optionAimAxis.get():
        doSetUpAxis(self,i)
    if self.optionOutAxis.get() == self.optionAimAxis.get():
        doSetOutAxis(self,i)
        
    return True
    
def doSetUpAxis(self,i):
    """
    Set the aim axis. if up or out have that axis. They will be changed. Aim is the priority.
    Then Up, and Out is last.
    
    """        
    assert i < 6,"%i isn't a viable up axis integer"%i
    axisBuffer = range(6)
    axisBuffer.remove(self.optionAimAxis.get())
    
    if i != self.optionAimAxis.get():
        self.optionUpAxis.set(i)  
    else:
        self.optionUpAxis.set(axisBuffer[0]) 
        guiFactory.warning("Aim axis has '%s'. Changed up axis to '%s'. Change aim setting if you want this seeting"%(dictionary.axisDirectionsByString[self.optionAimAxis.get()],dictionary.axisDirectionsByString[self.optionUpAxis.get()]))                  
        axisBuffer.remove(axisBuffer[0])
        
    if self.optionOutAxis.get() in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
        for i in axisBuffer:
            if i not in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
                doSetOutAxis(self,i)
                guiFactory.warning("Setting conflict. Changed out axis to '%s'"%dictionary.axisDirectionsByString[i])                    
                break
    return True        
    
    
def doSetOutAxis(self,i):
    assert i < 6,"%i isn't a viable aim axis integer"%i
    
    if i not in [self.optionAimAxis.get(),self.optionUpAxis.get()]:
        self.optionOutAxis.set(i)
    else:
        axisBuffer = range(6)
        axisBuffer.remove(self.optionAimAxis.get())
        axisBuffer.remove(self.optionUpAxis.get())
        self.optionOutAxis.set(axisBuffer[0]) 
        guiFactory.warning("Setting conflict. Changed out axis to '%s'"%dictionary.axisDirectionsByString[ axisBuffer[0] ])                    



def copyAxisOptions(self,target):
    target.optionAimAxis
    target.optionUpAxis
    target.optionOutAxis
    self.optionAimAxis
    self.optionUpAxis
    self.optionOutAxis 
    
    doSetAimAxis(self,target.optionAimAxis.get())
    doSetUpAxis(self,target.optionUpAxis.get())
    doSetOutAxis(self,target.optionOutAxis.get())
    
    
    
