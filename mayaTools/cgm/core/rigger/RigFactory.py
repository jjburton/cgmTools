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
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)
from cgm.core.lib import rayCaster as RayCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools
reload(mControlFactory)
from cgm.lib import (cgmMath,
                     attributes,
                     deformers,
                     locators,
                     constraints,
                     modules,
                     nodes,
                     distance,
                     dictionary,
                     joints,
                     skinning,
                     rigging,
                     search,
                     curves,
                     lists,
                     )

#from cgm.lib.classes import NameFactory

#>>> Utilities
#===================================================================
@r9General.Timer
def controlSurfaceSmoothWeights(controlSurface):
    if issubclass(type(controlSurface),cgmMeta.cgmNode):
	mi_surface = controlSurface
    elif mc.objExists(controlSurface):
	mi_surface = cgmMeta.cgmNode(controlSurface)
    else:
	raise StandardError,"controlSurfaceSmoothWeights failed. Surface doesn't exist: '%s'"%controlSurface
    l_cvs = mi_surface.getComponents('cv')
    l_skinClusters = deformers.returnObjectDeformers(mi_surface.mNode,deformerTypes = 'skinCluster')
    mi_skinCluster = cgmMeta.cgmNode(l_skinClusters[0])
    l_influenceObjects = skinning.queryInfluences(mi_skinCluster.mNode) or []
    
    log.info("l_skinClusters: '%s'"%l_skinClusters)
    log.info("mi_skinCluster: '%s'"%mi_skinCluster)
    log.info("l_influenceObjects: '%s'"%l_influenceObjects)
    
    if not mi_skinCluster and l_influenceObjects:
	raise StandardError,"controlSurfaceSmoothWeights failed. Not enough info found"
	
@r9General.Timer
def createConstraintSurfaceSegment(jointList,orientation = 'zyx',baseName ='test', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]
    
    mi_module = False
    mi_rigNull = False
    if moduleInstance is not None:
	if issubclass(type(moduleInstance),cgmPM.cgmModule):
	    mi_module = moduleInstance
	    mi_rigNull = mi_module.rigNull
	else:
	    log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    
    #Create our group
    mi_grp = cgmMeta.cgmObject(name = 'newgroup')
    mi_grp.addAttr('cgmName', str(baseName), lock=True)
    mi_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    mi_grp.doName()
    
    #Create surface
    l_surfaceReturn = joints.loftSurfaceFromJointList(jointList,outChannel)
    
    mi_controlSurface = cgmMeta.cgmObject( l_surfaceReturn[0] )
    mi_controlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    mi_controlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
    mi_controlSurface.doName()
    mi_controlSurface.addAttr('mClass','cgmObject')
    
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Create folicles
    ml_follicleTransforms = []
    ml_follicleShapes = []
    l_snapToGroups = []
    il_snapToGroups = []
    il_upLocs = []
    
    #First thing we're going to do is create our follicles
    for mi_jnt in ml_jointList:       
        l_closestInfo = distance.returnClosestPointOnSurfaceInfo(mi_jnt.mNode,mi_controlSurface.mNode)
        log.debug("%s : %s"%(mi_jnt.mNode,l_closestInfo))
        #>>> Follicle =======================================================
        l_follicleInfo = nodes.createFollicleOnMesh(mi_controlSurface.mNode)
        mi_follicleTrans = cgmMeta.cgmObject(l_follicleInfo[1])
        mi_follicleShape = cgmMeta.cgmNode(l_follicleInfo[0])
        #> Name
        mi_follicleTrans.doStore('cgmName',mi_jnt.mNode)
        mi_follicleTrans.doName()
        #>Set follicle value
        mi_follicleShape.parameterU = l_closestInfo['normalizedU']
        mi_follicleShape.parameterV = l_closestInfo['normalizedV']
        
        ml_follicleShapes.append(mi_follicleShape)
        ml_follicleTransforms.append(mi_follicleTrans)
	
	mi_follicleTrans.parent = mi_grp.mNode	
	
        #>> Surface Anchor ===================================================
        mi_grpPos = cgmMeta.cgmObject( rigging.groupMeObject(mi_jnt.mNode,False) )
        mi_grpPos.doStore('cgmName',mi_jnt.mNode)        
        mi_grpOrient = cgmMeta.cgmObject( mc.duplicate(mi_grpPos.mNode,returnRootsOnly=True,ic=True)[0] )
        mi_grpPos.addAttr('cgmType','surfaceAnchor',attrType='string',lock=True)
        mi_grpOrient.addAttr('cgmType','surfaceOrient',attrType='string',lock=True)
        mi_grpPos.doName()
        mi_grpOrient.doName()
        mi_grpOrient.parent = mi_grpPos.mNode
	
	mi_jnt.connectParentNode(mi_grpOrient.mNode,'snapToGroup','snapTarget')	
	
	#Contrain pos group
        constraint = mc.parentConstraint(mi_follicleTrans.mNode,mi_grpPos.mNode, maintainOffset=False)
	
	mi_upLoc = mi_jnt.doLoc()#Make up Loc
	mi_upLoc.parent = mi_grpPos.mNode
	mc.move(0,2,0,mi_upLoc.mNode,os=True)
	
	#mc.aimConstraint(ml_jointList[],objGroup,maintainOffset = False, weight = 1, aimVector = aimVector, upVector = upVector, worldUpObject = upLoc, worldUpType = 'object' )        
        l_snapToGroups.append(mi_grpOrient.mNode)
	il_snapToGroups.append(mi_grpOrient)
	il_upLocs.append(mi_upLoc)
	
    for i,mi_grp in enumerate(il_snapToGroups[:-1]):
	mc.aimConstraint(il_snapToGroups[i+1].mNode,mi_grp.mNode,
	                 maintainOffset = False, weight = 1,
	                 aimVector = [0,0,1], upVector = [0,1,0],
	                 worldUpObject = il_upLocs[i].mNode,
	                 worldUpType = 'object' )        
	
	
    return {'mi_controlSurface':mi_controlSurface,'controlSurface':mi_controlSurface.mNode,
            'il_snapToGroups':il_snapToGroups,'l_snapToGroups':l_snapToGroups}
    
@r9General.Timer
def createControlSurfaceSegment(jointList,orientation = 'zyx',baseName ='test', moduleInstance = None):
    """
    """
    #Good way to verify an instance list?
    #validate orientation
    outChannel = orientation[2]
    upChannel = '%sup'%orientation[1]
    
    mi_module = False
    mi_rigNull = False
    if moduleInstance is not None:
	if issubclass(type(moduleInstance),cgmPM.cgmModule):
	    mi_module = moduleInstance
	    mi_rigNull = mi_module.rigNull
	else:
	    log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    
    #Create our group
    mi_grp = cgmMeta.cgmObject(name = 'newgroup')
    mi_grp.addAttr('cgmName', str(baseName), lock=True)
    mi_grp.addAttr('cgmTypeModifier','surfaceFollow', lock=True)
    mi_grp.doName()
    
    #Create surface
    l_surfaceReturn = joints.loftSurfaceFromJointList(jointList,outChannel)
    
    mi_controlSurface = cgmMeta.cgmObject( l_surfaceReturn[0] )
    mi_controlSurface.addAttr('cgmName',str(baseName),attrType='string',lock=True)    
    mi_controlSurface.addAttr('cgmType','controlSurface',attrType='string',lock=True)
    mi_controlSurface.doName()
    mi_controlSurface.addAttr('mClass','cgmObject')
    
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Create folicles
    ml_follicleTransforms = []
    ml_follicleShapes = []
    
    #First thing we're going to do is create our follicles
    for mi_jnt in ml_jointList:       
        l_closestInfo = distance.returnClosestPointOnSurfaceInfo(mi_jnt.mNode,mi_controlSurface.mNode)
        log.debug("%s : %s"%(mi_jnt.mNode,l_closestInfo))
        #>>> Follicle =======================================================
        l_follicleInfo = nodes.createFollicleOnMesh(mi_controlSurface.mNode)
        mi_follicleTrans = cgmMeta.cgmObject(l_follicleInfo[1])
        mi_follicleShape = cgmMeta.cgmNode(l_follicleInfo[0])
        #> Name
        mi_follicleTrans.doStore('cgmName',mi_jnt.mNode)
        mi_follicleTrans.doName()
        #>Set follicle value
        mi_follicleShape.parameterU = l_closestInfo['normalizedU']
        mi_follicleShape.parameterV = l_closestInfo['normalizedV']
        
        ml_follicleShapes.append(mi_follicleShape)
        ml_follicleTransforms.append(mi_follicleTrans)
	
	mi_follicleTrans.parent = mi_grp.mNode	
	
        #>> Surface Anchor ===================================================
        """
        mi_grpPos = cgmMeta.cgmObject( rigging.groupMeObject(mi_jnt.mNode,False) )
        mi_grpPos.doStore('cgmName',mi_jnt.mNode)        
        mi_grpOrient = cgmMeta.cgmObject( mc.duplicate(mi_grpPos.mNode,returnRootsOnly=True)[0] )
        mi_grpPos.addAttr('cgmType','surfaceAnchor',attrType='string',lock=True)
        mi_grpOrient.addAttr('cgmType','surfaceOrient',attrType='string',lock=True)
        mi_grpPos.doName()
        mi_grpOrient.doName()
        mi_grpOrient.parent = mi_grpPos.mNode
        
        constraint = mc.pointConstraint(mi_transFollicle.mNode,mi_grpPos.mNode, maintainOffset=False)
        constraint = mc.orientConstraint(mi_transFollicle.mNode,mi_grpPos.mNode, maintainOffset=False)
        """
        
        #>>>Connect via constraint - no worky
        #constraint = mc.pointConstraint(mi_grpOrient.mNode,mi_jnt.mNode, maintainOffset=True)
        #constraint = mc.orientConstraint(mi_grpOrient.mNode,mi_jnt.mNode, maintainOffset=True)
        
        #constraints.doConstraintObjectGroup(mi_transFollicle.mNode,transform,['point','orient'])
        #>>> Connect the joint
        #attributes.doConnectAttr('%s.translate'%mi_grpPos.mNode,'%s.translate'%mi_jnt.mNode)
        
    #>>>Create scale stuff
    #>>>Create IK effectors,Create distance nodes
    l_iIK_effectors = []
    l_iIK_handles = []  
    l_iDistanceObjects = []
    mi_distanceShapes = []  
    for i,mi_jnt in enumerate(ml_jointList[:-1]):
        ik_buffer = mc.ikHandle (startJoint=mi_jnt.mNode,
                                 endEffector = ml_jointList[i+1].mNode,
                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                 enableHandles=True )
        #Handle
        mi_IK_Handle = cgmMeta.cgmObject(ik_buffer[0])
        mi_IK_Handle.parent = ml_follicleTransforms[i+1].mNode
        mi_IK_Handle.doStore('cgmName',mi_jnt.mNode)    
        mi_IK_Handle.doName()
        
        #Effector
        mi_IK_Effector = cgmMeta.cgmObject(ik_buffer[1])        
        #i_IK_Effector.doStore('cgmName',mi_jnt.mNode)    
        mi_IK_Effector.doName()
        
        l_iIK_handles.append(mi_IK_Handle)
        l_iIK_effectors.append(mi_IK_Effector)
        
        #>> create up loc
        #mi_loc = mi_jnt.doLoc()
        #mc.move(0, 10, 0, mi_loc.mNode, r=True,os=True,wd=True)
        
        #>> Distance nodes
        mi_distanceShape = cgmMeta.cgmNode( mc.createNode ('distanceDimShape') )        
        mi_distanceObject = cgmMeta.cgmObject( mi_distanceShape.getTransform() )
        mi_distanceObject.doStore('cgmName',mi_jnt.mNode)
        mi_distanceObject.addAttr('cgmType','measureNode',lock=True)
        mi_distanceObject.doName(nameShapes = True)
	mi_distanceObject.parent = mi_grp.mNode#parent it
        mi_distanceObject.overrideEnabled = 1
        mi_distanceObject.overrideVisibility = 0
	
        #Connect things
        mc.connectAttr ((ml_follicleTransforms[i].mNode+'.translate'),(mi_distanceShape.mNode+'.startPoint'))
        mc.connectAttr ((ml_follicleTransforms[i+1].mNode+'.translate'),(mi_distanceShape.mNode+'.endPoint'))
        
        l_iDistanceObjects.append(mi_distanceObject)
        mi_distanceShapes.append(mi_distanceShape)
            
    #Connect the first joint's position since an IK handle isn't controlling it    
    attributes.doConnectAttr('%s.translate'%ml_follicleTransforms[0].mNode,'%s.translate'%ml_jointList[0].mNode)
    
    #>>>Hook up scales
    #World scale
    
    #Buffer
    mi_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
    mi_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
    mi_jntScaleBufferNode.addAttr('masterScale',value = 1.0, attrType='float')        
    mi_jntScaleBufferNode.doName()
    
    mi_jntScaleBufferNode.connectParentNode(mi_controlSurface.mNode,'surface','scaleBuffer')
    
    for i,mi_jnt in enumerate(ml_jointList[:-1]):
	#Store our distance base to our buffer
        try:mi_jntScaleBufferNode.store(mi_distanceShapes[i].distance)#Store to our buffer
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to store joint distance: %s"%mi_distanceShapes[i].mNode
	
	#Create the mdNode
	mi_md = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	mi_md.operation = 2
	mi_md.doStore('cgmName',mi_jnt.mNode)
	mi_md.addAttr('cgmTypeModifier','masterScale')
	mi_md.doName()
	attributes.doConnectAttr('%s.%s'%(mi_distanceShapes[i].mNode,'distance'),#>>
	                         '%s.%s'%(mi_md.mNode,'input1X'))
	attributes.doConnectAttr('%s.%s'%(mi_jntScaleBufferNode.mNode,mi_jntScaleBufferNode.d_indexToAttr[i]),#>>
	                         '%s.%s'%(mi_md.mNode,'input2X'))
	
	#Connect to the joint
	try:
	    attributes.doConnectAttr('%s.%s'%(mi_md.mNode,'output.outputX'),#>>
		                     '%s.s%s'%(mi_jnt.mNode,orientation[0]))
	    for axis in orientation[1:]:
		attributes.doConnectAttr('%s.%s'%(mi_jntScaleBufferNode.mNode,'masterScale'),#>>
		                         '%s.s%s'%(mi_jnt.mNode,axis))	    
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to connect joint attrs: %s"%mi_jnt.mNode
	
	"""
	mdArg = [{'result':[mi_jnt.mNode,'sy'],'drivers':[[mi_distanceShapes[i].mNode,'distance'],[mi_jntScaleBufferNode,mi_jntScaleBufferNode.d_indexToAttr[i]]],'driven':[]},
	         {'result':[mi_jnt.mNode,'sx'],'drivers':[[mi_distanceShapes[i].mNode,'distance'],[mi_jntScaleBufferNode,mi_jntScaleBufferNode.d_indexToAttr[i]]],'driven':[]}]
	#mdArg = [{'drivers':[[mi_jntScaleBufferNode,'masterScale'],[mi_jntScaleBufferNode,mi_jntScaleBufferNode.d_indexToAttr[i]]],
	          #'driven':[[mi_jnt.mNode,'sy'],[mi_jnt.mNode,'sx']]}]
        
        try:NodeF.build_mdNetwork(mdArg, defaultAttrType='float',operation=2)
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to build network: %s"%mdArg 
	"""
	
    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
	attributes.doConnectAttr('%s.%s'%(ml_jointList[-2].mNode,axis),#>>
                                 '%s.%s'%(ml_jointList[-1].mNode,axis))	 
	
    return {'mi_controlSurface':mi_controlSurface,'controlSurface':mi_controlSurface.mNode,'surfaceScaleBuffer':mi_jntScaleBufferNode.mNode,'mi_surfaceScaleBuffer':mi_jntScaleBufferNode,'l_joints':jointList,'l_iJoints':ml_jointList}
    
    
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
    mi_module = False
    mi_rigNull = False
    if moduleInstance is not None:
	if issubclass(type(moduleInstance),cgmPM.cgmModule):
	    mi_module = moduleInstance
	    mi_rigNull = mi_module.rigNull
	else:
	    log.error("Not a module instance, ignoring: '%s'"%moduleInstance)
    #attributeHolder
    mi_holder = cgmMeta.cgmNode(attributeHolder)
    
    #Initialize joint list
    ml_jointList = [cgmMeta.cgmObject(j) for j in jointList]
    
    l_iScaleNodes = []
    l_iSqrtNodes = []
    l_iAttrs = []
    for i,mi_jnt in enumerate(ml_jointList[:-1]):
	#make sure attr exists
	mi_attr = cgmMeta.cgmAttr(mi_holder,"scaleMult_%s"%i,attrType = 'float',initialValue=1)
	outScalePlug = attributes.doBreakConnection(mi_jnt.mNode,"scale%s"%outChannel)
	upScalePlug = attributes.doBreakConnection(mi_jnt.mNode,"scale%s"%upChannel)
	
	#Create the multScale
	mi_mdScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	mi_mdScale.operation = 2
	mi_mdScale.doStore('cgmName',mi_jnt.mNode)
	mi_mdScale.addAttr('cgmTypeModifier','multScale')
	mi_mdScale.doName()
	for channel in [outChannel,upChannel]:
	    attributes.doConnectAttr('%s.scale%s'%(mi_jnt.mNode,aimChannel),#>>
		                     '%s.input1%s'%(mi_mdScale.mNode,channel))
	    attributes.doConnectAttr('%s'%(outScalePlug),#>>
		                     '%s.input2%s'%(mi_mdScale.mNode,channel))
	    
	#Create the sqrtNode
	mi_sqrtScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	mi_sqrtScale.operation = 3#set to power
	mi_sqrtScale.doStore('cgmName',mi_jnt.mNode)
	mi_sqrtScale.addAttr('cgmTypeModifier','sqrtScale')
	mi_sqrtScale.doName()
	for channel in [outChannel,upChannel]:
	    attributes.doConnectAttr('%s.output%s'%(mi_mdScale.mNode,channel),#>>
	                             '%s.input1%s'%(mi_sqrtScale.mNode,channel))
	    mc.setAttr("%s.input2"%(mi_sqrtScale.mNode)+channel,.5)
	    
	#Create the invScale
	mi_invScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	mi_invScale.operation = 2
	mi_invScale.doStore('cgmName',mi_jnt.mNode)
	mi_invScale.addAttr('cgmTypeModifier','invScale')
	mi_invScale.doName()
	for channel in [outChannel,upChannel]:
	    mc.setAttr("%s.input1"%(mi_invScale.mNode)+channel,1)	    
	    attributes.doConnectAttr('%s.output%s'%(mi_sqrtScale.mNode,channel),#>>
	                             '%s.input2%s'%(mi_invScale.mNode,channel))
	
	#Create the powScale
	mi_powScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	mi_powScale.operation = 3
	mi_powScale.doStore('cgmName',mi_jnt.mNode)
	mi_powScale.addAttr('cgmTypeModifier','powScale')
	mi_powScale.doName()
	for channel in [outChannel,upChannel]:
	    attributes.doConnectAttr('%s.output%s'%(mi_invScale.mNode,channel),#>>
		                     '%s.input1%s'%(mi_powScale.mNode,channel))
	    attributes.doConnectAttr('%s'%(mi_attr.p_combinedName),#>>
		                     '%s.input2%s'%(mi_powScale.mNode,channel))
	
	#Create the worldScale multiplier node
	mi_worldScale = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	mi_worldScale.operation = 1
	mi_worldScale.doStore('cgmName',mi_jnt.mNode)
	mi_worldScale.addAttr('cgmTypeModifier','worldScale')
	mi_worldScale.doName()
	for channel in [outChannel,upChannel]:
	    mc.setAttr("%s.input1"%(mi_worldScale.mNode)+channel,1)
	    #Connect powScale to the worldScale
	    attributes.doConnectAttr('%s.output%s'%(mi_powScale.mNode,channel),#>>
	                             '%s.input1%s'%(mi_worldScale.mNode,channel))
	#Connect original plugs
	attributes.doConnectAttr('%s'%(outScalePlug),#>>
                                 '%s.input2%s'%(mi_worldScale.mNode,outChannel))  
	attributes.doConnectAttr('%s'%(upScalePlug),#>>
                                 '%s.input2%s'%(mi_worldScale.mNode,upChannel)) 
	
	#Connect to joint
	attributes.doConnectAttr('%s.output%s'%(mi_worldScale.mNode,outChannel),#>>
                                 '%s.scale%s'%(mi_jnt.mNode,outChannel))  
	attributes.doConnectAttr('%s.output%s'%(mi_worldScale.mNode,upChannel),#>>
                                 '%s.scale%s'%(mi_jnt.mNode,upChannel)) 	
	
	l_iAttrs.append(mi_attr)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Modules
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    @r9General.Timer
    def __init__(self,moduleInstance,forceNew = True,**kws): 
        """
        To do:
        Add rotation order settting
        Add module parent check to make sure parent is templated to be able to move forward, or to constrain
        Add any other piece meal data necessary
        Add a cleaner to force a rebuild
        """
        # Get our base info
        #==============	        
        #>>> module null data
	"""
	try:moduleInstance
	except StandardError,error:
	    log.error("RigFactory.go.__init__>>module instance isn't working!")
	    raise StandardError,error    
	"""
        if not issubclass(type(moduleInstance),cgmPM.cgmModule):
            log.error("Not a cgmModule: '%s'"%moduleInstance)
            return 
	if not mc.objExists(moduleInstance.mNode):
	    raise StandardError,"RigFactory.go.init Module instance no longer exists: '%s'"%moduleInstance
        
        assert moduleInstance.isTemplated(),"Module is not templated: '%s'"%moduleInstance.getShortName()        
        assert moduleInstance.isSkeletonized(),"Module is not skeletonized: '%s'"%moduleInstance.getShortName()
        
        log.info(">>> RigFactory.go.__init__")
        self._mi_module = moduleInstance# Link for shortness
        """
        if moduleInstance.hasControls():
            if forceNew:
                deleteControls(moduleInstance)
            else:
                log.warning("'%s' has already been skeletonized"%moduleInstance.getShortName())
                return        
        """
        #>>> Gather info
        #=========================================================	
        self._l_moduleColors = self._mi_module.getModuleColors()
        self._l_coreNames = self._mi_module.coreNames.value
        self._im_templateNull = self._mi_module.templateNull#speed link
	self._im_rigNull = self._mi_module.rigNull#speed link
        self._bodyGeo = self._mi_module.modulePuppet.getGeo() or ['Morphy_Body_GEO'] #>>>>>>>>>>>>>>>>>this needs better logic   
        
        #Joints
        self._l_skinJoints = self._im_rigNull.getMessage('skinJoints')
        self._ml_skinJoints = self._im_rigNull.skinJoints
        
        #>>> part name 
        self._partName = self._mi_module.getPartNameBase()
        self._partType = self._mi_module.moduleType or False
        
        self._direction = None
        if self._mi_module.hasAttr('cgmDirection'):
            self._direction = self._mi_module.cgmDirection or None
               
        #>>> Instances and joint stuff
        self._jointOrientation = str(modules.returnSettingsData('jointOrientation')) or 'zyx'       

        #Make our stuff
        if self._partType in d_moduleRigFunctions.keys():
	    self._md_controlShapes = {}
            log.info("mode: cgmLimb control building")
            d_moduleRigFunctions[self._partType](self)
            #if not limbControlMaker(self,self.l_controlsToMakeArg):
                #raise StandardError,"limbControlMaker failed!"
        else:
            raise NotImplementedError,"haven't implemented '%s' rigging yet"%self._mi_module.mClass

@r9General.Timer
def registerControl(controlObject,typeModifier = None,copyTransform = None):
    """
    Function to register a control and get it ready for the rig
    toDo: rotate order set?
    
    """
    if issubclass(type(controlObject),cgmMeta.cgmObject):
	i_control = controlObject
    elif mc.objExists(controlObject):
	i_control = cgmMeta.cgmObject(controlObject)
    else:
	raise StandardError,"Not a cgmObject or not an existing object: '%s'"%controlObject
    
    #Name stuff
    mi_control.addAttr('mClass','cgmObject',lock=True)
    mi_control.addAttr('cgmType','controlAnim',lock=True)    
    if typeModifier is not None:
	i_control.addAttr('cgmTypeModifier',str(typeModifier),lock=True)
    mi_control.doName()
    
    #Freeze stuff
    mi_control.doGroup(True)   
    mc.makeIdentity(mi_control.mNode, apply=True,t=1,r=0,s=1,n=0)	
    
    return mi_control

def rig_segmentFK(d_controlShapes):
    l_fkControls = mc.duplicate(d_controlShapes.get('segmentControls'),po=False,ic=True,rc=True)
    il_fkCcontrols = [cgmMeta.cgmObject(o) for o in l_fkControls]#instance the list    
    
    #Parent to heirarchy
    rigging.parentListToHeirarchy(l_fkControls)
    
    for mi_obj in il_fkCcontrols:
	registerControl(mi_obj,typeModifier='fk')
	
@r9General.Timer
def build_spine(goInstance):
    """
    Rotate orders
    hips = 3
    """ 
    if not issubclass(type(goInstance),go):
        log.error("Not a RigFactory.go instance: '%s'"%goInstance)
        raise StandardError
    self = goInstance#Link
    
    #log.info(self.__dict__.keys())
    #>>> Figure out what's what
    #Add some checks like at least 3 handles
    
    #>>>Build our controls
    #=============================================================
    #mControlFactory.go(self._mi_module,storageInstance=self)#This will store controls to a dict called    
    log.info(self._md_controlShapes)
    
    #>>>Set up structure
    
    #>>>Create joint chains
    #=============================================================
    try:
	#>>Surface chain    
	l_surfaceJoints = mc.duplicate(self._l_skinJoints[1:-1],po=True,ic=True,rc=True)
	log.info(l_surfaceJoints)
	ml_surfaceJoints = []
	for i,j in enumerate(l_surfaceJoints):
	    mi_j = cgmMeta.cgmObject(j)
	    mi_j.addAttr('cgmType','surfaceJoint',attrType='string')
	    mi_j.doName()
	    l_surfaceJoints[i] = mi_j.mNode
	    ml_surfaceJoints.append(mi_j)
	ml_surfaceJoints[0].parent = False#Parent to world
	    
	#Start
	mi_startJnt = cgmMeta.cgmObject(mc.duplicate(self._l_skinJoints[0],po=True,ic=True,rc=True)[0])
	mi_startJnt.addAttr('cgmType','deformationJoint',attrType='string',lock=True)
	mi_startJnt.doName()
	
	#End
	l_endJoints = mc.duplicate(self._l_skinJoints[-2],ic=True,rc=True)
	mi_endJnt = cgmMeta.cgmObject(l_endJoints[0])
	for j in l_endJoints:
	    mi_j = cgmMeta.cgmObject(j)
	    mi_j.addAttr('cgmType','deformationJoint',attrType='string',lock=True)
	    mi_j.doName()
	mi_endJnt.parent = False
	
	#Influence chain for influencing the surface
	ml_influenceJoints = []
	for mi_jnt in self._ml_skinJoints[:-1]:
	    if mi_jnt.hasAttr('cgmName') and mi_jnt.cgmName in self._l_coreNames:
		mi_new = cgmMeta.cgmObject(mc.duplicate(mi_jnt.mNode,po=True,ic=True)[0])
		mi_new.addAttr('cgmType','influenceJoint',attrType='string',lock=True)
		mi_new.parent = False
		mi_new.doName()
		if ml_influenceJoints:#if we have data, parent to last
		    mi_new.parent = ml_influenceJoints[-1]
		else:mi_new.parent = False
		
		ml_influenceJoints.append(mi_new)
		
	l_influenceJoints = [mi_jnt.mNode for mi_jnt in ml_influenceJoints]    
    except StandardError,error:
	log.error("build_spine>>Build rig joints fail!")
	raise StandardError,error    
    #>>>Create a constraint surface for the influence joints
    #====================================================================================    
    try:
	d_constraintSurfaceReturn = createConstraintSurfaceSegment(l_influenceJoints[1:],
	                                                           self._jointOrientation,
	                                                           self._partName+'_constraint',
	                                                           moduleInstance=self._mi_module)    
	for mi_jnt in ml_influenceJoints:
	    mi_jnt.parent = False#Parent to world
	    
	for mi_jnt in ml_influenceJoints[1:-1]:#Snap our ones with follow groups to them
	    if mi_jnt.getMessage('snapToGroup'):
		mi_jnt.parent = mi_jnt.getMessage('snapToGroup')[0]
	
	#Skin cluster to first and last influence joints
	mi_constraintSurfaceCluster = cgmMeta.cgmNode(mc.skinCluster ([ml_influenceJoints[0].mNode,ml_influenceJoints[-1].mNode],
	                                                             d_constraintSurfaceReturn['mi_controlSurface'].mNode,
	                                                             tsb=True,
	                                                             maximumInfluences = 3,
	                                                             normalizeWeights = 1,dropoffRate=4.0)[0])
	mi_constraintSurfaceCluster.addAttr('cgmName', str(self._partName), lock=True)
	mi_constraintSurfaceCluster.addAttr('cgmTypeModifier','constraintSurface', lock=True)
	mi_constraintSurfaceCluster.doName()   
    except StandardError,error:
	log.error("build_spine>>Constraint surface build fail")
	raise StandardError,error
 
    #Control Surface
    #====================================================================================
    try:
	#Create surface
	surfaceReturn = createControlSurfaceSegment([mi_jnt.mNode for mi_jnt in ml_surfaceJoints],
	                                            self._jointOrientation,
	                                            self._partName,
	                                            moduleInstance=self._mi_module)
	#Add squash
	addSquashAndStretchToControlSurfaceSetup(surfaceReturn['surfaceScaleBuffer'],[mi_jnt.mNode for mi_jnt in ml_surfaceJoints],moduleInstance=self._mi_module)
	log.info(surfaceReturn)
    
	#Surface influence joints cluster#
	mi_controlSurfaceCluster = cgmMeta.cgmNode(mc.skinCluster ([mi_jnt.mNode for mi_jnt in ml_influenceJoints],
	                                                          surfaceReturn['mi_controlSurface'].mNode,
	                                                          tsb=True,
	                                                          maximumInfluences = 3,
	                                                          normalizeWeights = 1,dropoffRate=4.0)[0])
	
	mi_controlSurfaceCluster.addAttr('cgmName', str(self._partName), lock=True)
	mi_controlSurfaceCluster.addAttr('cgmTypeModifier','controlSurface', lock=True)
	mi_controlSurfaceCluster.doName()
	
	log.info(mi_controlSurfaceCluster.mNode)
	# smooth skin weights #
	#skinning.simpleControlSurfaceSmoothWeights(mi_controlSurfaceCluster.mNode)   
	
    except StandardError,error:
	log.error("build_spine>>Control surface build fail")
	raise StandardError,error


#>>> Register rig functions
#=====================================================================
d_moduleRigFunctions = {'torso':build_spine,
                        }
    
 