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
from cgm.core.rigger import ModuleCurveFactory as mCurveFactory
reload(mCurveFactory)
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
def createConstraintSurfaceSegment(jointList,orientation = 'zyx',baseName ='test', moduleInstance = None):
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
def createControlSurfaceSegment(jointList,orientation = 'zyx',baseName ='test', moduleInstance = None):
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
        self._i_module = moduleInstance# Link for shortness
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
        self._l_moduleColors = self._i_module.getModuleColors()
        self._l_coreNames = self._i_module.coreNames.value
        self._im_templateNull = self._i_module.templateNull#speed link
	self._im_rigNull = self._i_module.rigNull#speed link
        self._bodyGeo = self._i_module.modulePuppet.getGeo() or ['Morphy_Body_GEO'] #>>>>>>>>>>>>>>>>>this needs better logic   
        
        #Joints
        self._l_skinJoints = self._im_rigNull.getMessage('skinJoints')
        self._ml_skinJoints = self._im_rigNull.skinJoints
        
        #>>> part name 
        self._partName = self._i_module.getPartNameBase()
        self._partType = self._i_module.moduleType or False
        
        self._direction = None
        if self._i_module.hasAttr('cgmDirection'):
            self._direction = self._i_module.cgmDirection or None
               
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
            raise NotImplementedError,"haven't implemented '%s' rigging yet"%self._i_module.mClass


def rig_segmentFK(md_controlShapes):
    ml_fkControls = mc.duplicate(md_controlShapes.get('segmentControls'),po=False,ic=True,rc=True)
    l_fkCcontrols = [mObj.mNode for mObj in ml_fkControls ]#instance the list    
    
    #Parent to heirarchy
    rigging.parentListToHeirarchy(l_fkControls)
    
    for i_obj in il_fkCcontrols:
	registerControl(i_obj,typeModifier='fk')
	
@r9General.Timer
def build_spine(goInstance):
    """
    Rotate orders
    hips = 3
    """ 
    __version__ = 0.03272013
    
    if not issubclass(type(goInstance),go):
        log.error("Not a RigFactory.go instance: '%s'"%goInstance)
        raise StandardError
    self = goInstance#Link
    
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
    try:
	#Cog
	i_cog = self._md_controlShapes['cog']
	mControlFactory.registerControl(i_cog,addGroups = True,addConstraintGroup=True,
	                                freezeAll=True,
	                                controlType='cog')
    except StandardError,error:
	log.error("build_spine>>Build cog fail!")
	raise StandardError,error
        
    #>FK Segments
    try:
	ml_segmentsFK = self._md_controlShapes['segmentFK']
	for i,i_obj in enumerate(ml_segmentsFK[1:]):#parent
	    i_obj.parent = ml_segmentsFK[i].mNode
	    
	ml_segmentsFK[0].parent = i_cog.mNode
	for i_obj in ml_segmentsFK:
	    mControlFactory.registerControl(i_obj,addGroups=1,setRotateOrder=5,typeModifier='fk',) 
    except StandardError,error:
	log.error("build_spine>>Build fk fail!")
	raise StandardError,error
    
    #>IK Segments
    ml_segmentsIK = self._md_controlShapes['segmentIK']
    for i_obj in ml_segmentsIK:
	mControlFactory.registerControl(i_obj,addGroups=1,typeModifier='ik',
	                                setRotateOrder=5)       
    
    #>IK Handle
    try:
	i_IKEnd = self._md_controlShapes['segmentIKEnd']
	i_IKEnd.parent = i_cog.mNode
	i_loc = i_IKEnd.doLoc()#Make loc for a new transform
	i_loc.rx = i_loc.rx + 90#offset       
	mControlFactory.registerControl(i_IKEnd,copyTransform=i_loc,
	                                copyPivot=ml_segmentsIK[-2].mNode,typeModifier='ik',
	                                addGroups = 1,addConstraintGroup=True,
	                                setRotateOrder=5)
	i_loc.delete()#delete
	
    except StandardError,error:
	log.error("build_spine>>Build ik handle fail!")
	raise StandardError,error
      
    #>Hips
    try:
	i_hips = self._md_controlShapes['hips']
	i_hips.parent = i_cog.mNode#parent
	mControlFactory.registerControl(i_hips,addGroups = True,
	                                copyPivot=ml_segmentsFK[1].mNode,
	                                addConstraintGroup=True)
    except StandardError,error:
	log.error("build_spine>>Build hips fail!")
	raise StandardError,error
    
    
    return
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
	    
	#Start
	i_startJnt = cgmMeta.cgmObject(mc.duplicate(self._l_skinJoints[0],po=True,ic=True,rc=True)[0])
	i_startJnt.addAttr('cgmType','deformationJoint',attrType='string',lock=True)
	i_startJnt.doName()
	
	#End
	l_endJoints = mc.duplicate(self._l_skinJoints[-2],ic=True,rc=True)
	i_endJnt = cgmMeta.cgmObject(l_endJoints[0])
	for j in l_endJoints:
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmType','deformationJoint',attrType='string',lock=True)
	    i_j.doName()
	i_endJnt.parent = False
	
	#Influence chain for influencing the surface
	ml_influenceJoints = []
	for i_jnt in self._ml_skinJoints[:-1]:
	    if i_jnt.hasAttr('cgmName') and i_jnt.cgmName in self._l_coreNames:
		i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
		i_new.addAttr('cgmType','influenceJoint',attrType='string',lock=True)
		i_new.parent = False
		i_new.doName()
		if ml_influenceJoints:#if we have data, parent to last
		    i_new.parent = ml_influenceJoints[-1]
		else:i_new.parent = False
		
		ml_influenceJoints.append(i_new)
		
	l_influenceJoints = [i_jnt.mNode for i_jnt in ml_influenceJoints]    
    except StandardError,error:
	log.error("build_spine>>Build rig joints fail!")
	raise StandardError,error    
    
    #>>>Create a constraint surface for the influence joints
    #====================================================================================    
    try:
	d_constraintSurfaceReturn = createConstraintSurfaceSegment(l_influenceJoints[1:],
	                                                           self._jointOrientation,
	                                                           self._partName+'_constraint',
	                                                           moduleInstance=self._i_module)    
	for i_jnt in ml_influenceJoints:
	    i_jnt.parent = False#Parent to world
	    
	for i_jnt in ml_influenceJoints[1:-1]:#Snap our ones with follow groups to them
	    if i_jnt.getMessage('snapToGroup'):
		i_jnt.parent = i_jnt.getMessage('snapToGroup')[0]
	
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
 
    #Control Surface
    #====================================================================================
    try:
	#Create surface
	surfaceReturn = createControlSurfaceSegment([i_jnt.mNode for i_jnt in ml_surfaceJoints],
	                                            self._jointOrientation,
	                                            self._partName,
	                                            moduleInstance=self._i_module)
	#Add squash
	addSquashAndStretchToControlSurfaceSetup(surfaceReturn['surfaceScaleBuffer'],[i_jnt.mNode for i_jnt in ml_surfaceJoints],moduleInstance=self._i_module)
	log.info(surfaceReturn)
    
	#Surface influence joints cluster#
	i_controlSurfaceCluster = cgmMeta.cgmNode(mc.skinCluster ([i_jnt.mNode for i_jnt in ml_influenceJoints],
	                                                          surfaceReturn['i_controlSurface'].mNode,
	                                                          tsb=True,
	                                                          maximumInfluences = 3,
	                                                          normalizeWeights = 1,dropoffRate=4.0)[0])
	
	i_controlSurfaceCluster.addAttr('cgmName', str(self._partName), lock=True)
	i_controlSurfaceCluster.addAttr('cgmTypeModifier','controlSurface', lock=True)
	i_controlSurfaceCluster.doName()
	
	log.info(i_controlSurfaceCluster.mNode)
	# smooth skin weights #
	#skinning.simpleControlSurfaceSmoothWeights(i_controlSurfaceCluster.mNode)   
	
    except StandardError,error:
	log.error("build_spine>>Control surface build fail")
	raise StandardError,error


#>>> Register rig functions
#=====================================================================
d_moduleRigFunctions = {'torso':build_spine,
                        }
    
 