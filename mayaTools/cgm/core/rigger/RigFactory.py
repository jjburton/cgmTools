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
        if not issubclass(type(moduleInstance),cgmPM.cgmModule):
            log.error("Not a cgmModule: '%s'"%moduleInstance)
            return 
	if not mc.objExists(moduleInstance.mNode):
	    raise StandardError,"RigFactory.go.init Module instance no longer exists: '%s'"%moduleInstance
        
        assert moduleInstance.mClass in ['cgmModule','cgmLimb'],"Not a module"
        assert moduleInstance.isTemplated(),"Module is not templated: '%s'"%moduleInstance.getShortName()        
        assert moduleInstance.isSkeletonized(),"Module is not skeletonized: '%s'"%moduleInstance.getShortName()
        
        log.info(">>> ModuleControlFactory.go.__init__")
        self.m = moduleInstance# Link for shortness
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
        self.l_moduleColors = self.m.getModuleColors()
        self.l_coreNames = self.m.coreNames.value
        self.i_templateNull = self.m.templateNull#speed link
	self.i_rigNull = self.m.rigNull#speed link
        self.bodyGeo = self.m.modulePuppet.getGeo() or ['Morphy_Body_GEO'] #>>>>>>>>>>>>>>>>>this needs better logic   
        
        #Joints
        self.l_skinJoints = self.i_rigNull.getMessage('skinJoints')
        self.l_iSkinJoints = self.i_rigNull.skinJoints
        
        #>>> part name 
        self.partName = self.m.getPartNameBase()
        self.partType = self.m.moduleType or False
        
        self.direction = None
        if self.m.hasAttr('cgmDirection'):
            self.direction = self.m.cgmDirection or None
               
        #>>> Instances and joint stuff
        self.jointOrientation = str(modules.returnSettingsData('jointOrientation')) or 'zyx'       
        
        #>>> We need to figure out which control to make
        self.l_controlsToMakeArg = []
        if not self.m.getMessage('moduleParent'):
            self.l_controlsToMakeArg.append('cog')
        #if self.i_rigNull.ik:
            #self.l_controlsToMakeArg.extend(['vectorHandles'])
            #if self.partType == 'torso':#Maybe move to a dict?
                #self.l_controlsToMakeArg.append('spineIKHandle')            
        if self.i_rigNull.fk:
            self.l_controlsToMakeArg.extend(['segmentControls'])
            if self.partType == 'torso':#Maybe move to a dict?
                self.l_controlsToMakeArg.append('hips')
        log.info("l_controlsToMakeArg: %s"%self.l_controlsToMakeArg)
        
        self.d_controlShapes = mControlFactory.limbControlMaker(self.m,self.l_controlsToMakeArg)
        for key in self.l_controlsToMakeArg:
	    if key not in self.d_controlShapes:
		log.warning("Necessary control shape(s) was not built: '%s'"%key)
	    
        #Make our stuff
        if self.partType in d_moduleRigFunctions.keys():
            log.info("mode: cgmLimb control building")
            d_moduleRigFunctions[self.partType](self)
            #if not limbControlMaker(self,self.l_controlsToMakeArg):
                #raise StandardError,"limbControlMaker failed!"
        else:
            raise NotImplementedError,"haven't implemented '%s' rigging yet"%self.m.mClass

@r9General.Timer
def registerControl(controlObject,typeModifier = None,copyTransform = None):
    """ Function to register a control and get it ready for the rig"""
    if issubclass(type(controlObject),cgmMeta.cgmObject):
	i_control = controlObject
    elif mc.objExists(controlObject):
	i_control = cgmMeta.cgmObject(controlObject)
    else:
	raise StandardError,"Not a cgmObject or not an existing object: '%s'"%controlObject
    
    #Name stuff
    i_control.addAttr('mClass','cgmObject',lock=True)
    i_control.addAttr('cgmType','controlAnim',lock=True)    
    if typeModifier is not None:
	i_control.addAttr('cgmTypeModifier',str(typeModifier),lock=True)
    i_control.doName()
    
    #Freeze stuff
    i_control.doGroup(True)   
    mc.makeIdentity(i_control.mNode, apply=True,t=1,r=0,s=1,n=0)	

    
    return i_control

def rig_segmentFK(d_controlShapes):
    l_fkControls = mc.duplicate(d_controlShapes.get('segmentControls'),po=False,ic=True,rc=True)
    il_fkCcontrols = [cgmMeta.cgmObject(o) for o in l_fkControls]#instance the list    
    
    #Parent to heirarchy
    rigging.parentListToHeirarchy(l_fkControls)
    
    for i_obj in il_fkCcontrols:
	registerControl(i_obj,typeModifier='fk')
	
	
@r9General.Timer
def rigSpine(goInstance):
    """
    Rotate orders
    hips = 3
    """ 
    if not issubclass(type(goInstance),go):
        log.error("Not a RigFactory.go instance: '%s'"%goInstance)
        return False        
    self = goInstance#Link
    
    #>>> Figure out what's what
    #Add some checks like at least 3 handles
    
    #>>>Build our controls
    log.info(self.d_controlShapes)
  
    
    #>>>Set up structure
    
    #>>>Create joint chains
    #=============================================================
    #>>Surface chain    
    l_surfaceJoints = mc.duplicate(self.l_skinJoints[:-1],po=True,ic=True,rc=True)
    l_iSurfaceJoints = []
    for i,j in enumerate(l_surfaceJoints):
        i_j = cgmMeta.cgmObject(j)
        i_j.addAttr('cgmType','surfaceJoint',attrType='string')
        i_j.doName()
        l_surfaceJoints[i] = i_j.mNode
        l_iSurfaceJoints.append(i_j)
        
    #Start
    i_startJnt = cgmMeta.cgmObject(mc.duplicate(self.l_skinJoints[0],po=True,ic=True,rc=True)[0])
    i_startJnt.addAttr('cgmType','deformationJoint',attrType='string',lock=True)
    i_startJnt.doName()
    
    #End
    l_endJoints = mc.duplicate(self.l_skinJoints[-2],ic=True,rc=True)
    i_endJnt = cgmMeta.cgmObject(l_endJoints[0])
    for j in l_endJoints:
        i_j = cgmMeta.cgmObject(j)
        i_j.addAttr('cgmType','deformationJoint',attrType='string',lock=True)
        i_j.doName()
    i_endJnt.parent = False
    
    #Influence chain for influencing the surface
    l_iInfluenceJoints = []
    for i_jnt in self.l_iSkinJoints:
        if i_jnt.hasAttr('cgmName') and i_jnt.cgmName in self.l_coreNames:
            i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
            i_new.addAttr('cgmType','influenceJoint',attrType='string',lock=True)
            i_new.parent = False
            i_new.doName()
            l_iInfluenceJoints.append(i_new)
    
    #Control Surface
    #====================================================================================
    #Create surface
    surfaceReturn = createControlSurfaceSegment(l_surfaceJoints,
                                                self.jointOrientation,
                                                self.partName,
                                                moduleInstance=self.m)
    #Add squash
    addSquashAndStretchToControlSurfaceSetup(surfaceReturn['surfaceScaleBuffer'],l_surfaceJoints,moduleInstance=self.m)
    log.info(surfaceReturn)

    #surface influence joints cluster#
    i_controlSurfaceCluster = cgmMeta.cgmNode(mc.skinCluster ([i_jnt.mNode for i_jnt in l_iInfluenceJoints],
                                                              surfaceReturn['i_controlSurface'].mNode,
                                                              tsb=True,
                                                              maximumInfluences = 3,
                                                              normalizeWeights = 1,dropoffRate=4.0)[0])
    
    i_controlSurfaceCluster.addAttr('cgmName', str(self.partName), lock=True)
    i_controlSurfaceCluster.addAttr('cgmTypeModifier','controlSurface', lock=True)
    i_controlSurfaceCluster.doName()
    
    log.info(i_controlSurfaceCluster.mNode)
    # smooth skin weights #
    #skinning.simpleControlSurfaceSmoothWeights(i_controlSurfaceCluster.mNode)   
    


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
    
    l_iJointList = [cgmMeta.cgmObject(j) for j in jointList]
    #Create folicles
    l_iFollicleTransforms = []
    l_iFollicleShapes = []
    
    #First thing we're going to do is create our follicles
    for i_jnt in l_iJointList:       
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
        
        l_iFollicleShapes.append(i_follicleShape)
        l_iFollicleTransforms.append(i_follicleTrans)
	
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
    l_iDistanceShapes = []  
    for i,i_jnt in enumerate(l_iJointList[:-1]):
        ik_buffer = mc.ikHandle (startJoint=i_jnt.mNode,
                                 endEffector = l_iJointList[i+1].mNode,
                                 setupForRPsolver = True, solver = 'ikRPsolver',
                                 enableHandles=True )
        #Handle
        i_IK_Handle = cgmMeta.cgmObject(ik_buffer[0])
        i_IK_Handle.parent = l_iFollicleTransforms[i+1].mNode
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
        mc.connectAttr ((l_iFollicleTransforms[i].mNode+'.translate'),(i_distanceShape.mNode+'.startPoint'))
        mc.connectAttr ((l_iFollicleTransforms[i+1].mNode+'.translate'),(i_distanceShape.mNode+'.endPoint'))
        
        l_iDistanceObjects.append(i_distanceObject)
        l_iDistanceShapes.append(i_distanceShape)
            
    #Connect the first joint's position since an IK handle isn't controlling it    
    attributes.doConnectAttr('%s.translate'%l_iFollicleTransforms[0].mNode,'%s.translate'%l_iJointList[0].mNode)
    
    #>>>Hook up scales
    #World scale
    
    #Buffer
    i_jntScaleBufferNode = cgmMeta.cgmBufferNode(name = str(baseName),overideMessageCheck=True)
    i_jntScaleBufferNode.addAttr('cgmType','distanceBuffer')
    i_jntScaleBufferNode.addAttr('masterScale',value = 1.0, attrType='float')        
    i_jntScaleBufferNode.doName()
    
    i_jntScaleBufferNode.connectParentNode(i_controlSurface.mNode,'surface','scaleBuffer')
    
    for i,i_jnt in enumerate(l_iJointList[:-1]):
	#Store our distance base to our buffer
        try:i_jntScaleBufferNode.store(l_iDistanceShapes[i].distance)#Store to our buffer
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to store joint distance: %s"%l_iDistanceShapes[i].mNode
	
	#Create the mdNode
	i_md = cgmMeta.cgmNode(mc.createNode('multiplyDivide'))
	i_md.operation = 2
	i_md.doStore('cgmName',i_jnt.mNode)
	i_md.addAttr('cgmTypeModifier','masterScale')
	i_md.doName()
	attributes.doConnectAttr('%s.%s'%(l_iDistanceShapes[i].mNode,'distance'),#>>
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
	mdArg = [{'result':[i_jnt.mNode,'sy'],'drivers':[[l_iDistanceShapes[i].mNode,'distance'],[i_jntScaleBufferNode,i_jntScaleBufferNode.d_indexToAttr[i]]],'driven':[]},
	         {'result':[i_jnt.mNode,'sx'],'drivers':[[l_iDistanceShapes[i].mNode,'distance'],[i_jntScaleBufferNode,i_jntScaleBufferNode.d_indexToAttr[i]]],'driven':[]}]
	#mdArg = [{'drivers':[[i_jntScaleBufferNode,'masterScale'],[i_jntScaleBufferNode,i_jntScaleBufferNode.d_indexToAttr[i]]],
	          #'driven':[[i_jnt.mNode,'sy'],[i_jnt.mNode,'sx']]}]
        
        try:NodeF.build_mdNetwork(mdArg, defaultAttrType='float',operation=2)
	except StandardError,error:
	    log.error(error)
	    raise StandardError,"Failed to build network: %s"%mdArg 
	"""
	
    #Connect last joint scale to second to last
    for axis in ['scaleX','scaleY','scaleZ']:
	attributes.doConnectAttr('%s.%s'%(l_iJointList[-2].mNode,axis),#>>
                                 '%s.%s'%(l_iJointList[-1].mNode,axis))	 
	
    return {'i_controlSurface':i_controlSurface,'controlSurface':i_controlSurface.mNode,'surfaceScaleBuffer':i_jntScaleBufferNode.mNode,'i_surfaceScaleBuffer':i_jntScaleBufferNode,'l_joints':jointList,'l_iJoints':l_iJointList}
    """
    # connect joints to surface#
    surfaceConnectReturn = joints.attachJointChainToSurface(surfaceJoints,controlSurface,jointOrientation,upChannel,'animCrv')
    print surfaceConnectReturn 
    """
    
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
    l_iJointList = [cgmMeta.cgmObject(j) for j in jointList]
    
    l_iScaleNodes = []
    l_iSqrtNodes = []
    l_iAttrs = []
    for i,i_jnt in enumerate(l_iJointList[:-1]):
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
	
	l_iAttrs.append(i_attr)

#>>> Register rig functions
#=====================================================================
d_moduleRigFunctions = {'torso':rigSpine,
                        }
    
 