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
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)
from cgm.core.lib import rayCaster as RayCast
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
reload(mShapeCast)
from cgm.core.lib import nameTools
from cgm.core.rigger.lib import joint_Utils as jntUtils

from cgm.core.rigger.lib.Limb import (spine,neckHead,leg,clavicle,arm,finger)

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
reload(rigging)
l_modulesDone  = ['torso','neckhead']

#>>> Register rig functions
#=====================================================================
d_moduleTypeToBuildModule = {'leg':leg,
                             'torso':spine,
                             'neckhead':neckHead,
                             'clavicle':clavicle,
                             'arm':arm,
                             'finger':finger,
                             'thumb':finger,
                            } 
for module in d_moduleTypeToBuildModule.keys():
    reload(d_moduleTypeToBuildModule[module])
    
#>>> Main class function
#=====================================================================
class go(object):
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
	try:
	    if moduleInstance.isModule():
		i_module = moduleInstance
	except StandardError,error:
	    raise StandardError,"RigFactory.go.init. Module call failure. Probably not a module: '%s'"%error	    
	if not i_module:
	    raise StandardError,"RigFactory.go.init Module instance no longer exists: '%s'"%moduleInstance
	
        assert moduleInstance.isTemplated(),"Module is not templated: '%s'"%moduleInstance.getShortName()        
        assert moduleInstance.isSkeletonized(),"Module is not skeletonized: '%s'"%moduleInstance.getShortName()
        
        log.debug(">>> RigFactory.go.__init__")
        log.debug(">>> forceNew: %s"%forceNew)	
        self._i_module = moduleInstance# Link for shortness
	self._i_module.__verify__()
	self._cgmClass = 'RigFactory.go'
	
	#First we want to see if we have a moduleParent to see if it's rigged yet
	if self._i_module.getMessage('moduleParent'):
	    if not self._i_module.moduleParent.isRigged():
		raise StandardError,"RigFactory.go.init>>> '%s's module parent is not rigged yet: '%s'"%(self._i_module.getShortName(),self._i_module.moduleParent.getShortName())
	
	#First we want to see if we have a moduleParent to see if it's rigged yet
	if self._i_module.isRigged() and forceNew is not True:
	    raise StandardError,"RigFactory.go.init>>> '%s' already rigged and not forceNew"%(self._i_module.getShortName())
	
	#Verify we have a puppet and that puppet has a masterControl which we need for or master scale plug
	if not self._i_module.modulePuppet._verifyMasterControl():
	    raise StandardError,"RigFactory.go.init masterControl failed to verify"
	
	#Verify a dynamic switch
	if not self._i_module.rigNull.getMessage('dynSwitch'):
	    self._i_dynSwitch = cgmRigMeta.cgmDynamicSwitch(dynOwner=self._i_module.rigNull.mNode)
	else:
	    self._i_dynSwitch = self._i_module.rigNull.dynSwitch
	log.debug("switch: '%s'"%self._i_dynSwitch.getShortName())
	
	self._i_masterControl = self._i_module.modulePuppet.masterControl
	self._i_masterSettings = self._i_masterControl.controlSettings
	self._i_masterDeformGroup = self._i_module.modulePuppet.masterNull.deformGroup
	
        #>>> Gather info
        #=========================================================	
        self._l_moduleColors = self._i_module.getModuleColors()
        self._l_coreNames = self._i_module.coreNames.value
        self._i_templateNull = self._i_module.templateNull#speed link
	self._i_rigNull = self._i_module.rigNull#speed link
        self._bodyGeo = self._i_module.modulePuppet.getGeo() or ['Morphy_Body_GEO'] #>>>>>>>>>>>>>>>>>this needs better logic   
        self._version = self._i_rigNull.version
        #Joints
        self._l_skinJoints = self._i_rigNull.getMessage('skinJoints')
        self._ml_skinJoints = self._i_rigNull.skinJoints #We buffer this because when joints are duplicated, the multiAttrs extend with duplicates
        self._l_moduleJoints = self._i_rigNull.getMessage('moduleJoints')
        self._ml_moduleJoints = self._i_rigNull.moduleJoints #We buffer this because when joints are duplicated, the multiAttrs extend with duplicates

        #>>> part name 
        self._partName = self._i_module.getPartNameBase()
        self._partType = self._i_module.moduleType.lower() or False
        self._strShortName = self._i_module.getShortName() or False
	
        #>>> See if we have a buildable module -- do we have a builder
	if not isBuildable(self):
	    raise StandardError,"The builder for module type '%s' is not ready"%self._partType
	
        #>>>Version Check
	#TO DO: move to moduleFactory
	self._outOfDate = False
	if self._version != self._buildVersion:
	    self._outOfDate = True	    
	    log.warning("RigFactory.go>>> '%s'(%s) rig version out of date: %s != %s"%( self._strShortName,self._partType,self._version,self._buildVersion))	
	else:
	    if forceNew and self._i_module.isRigged():
		self._i_module.rigDelete()
	    log.info("RigFactory.go>>> '%s' rig version up to date !"%(self.buildModule.__name__))	
	
	self._direction = self._i_module.getAttr('cgmDirection')
        #self._direction = None
        #if self._i_module.hasAttr('cgmDirection'):
            #self._direction = self._i_module.cgmDirection or None
               
        #>>> Instances and joint stuff
        self._jointOrientation = str(modules.returnSettingsData('jointOrientation')) or 'zyx'       
	
	#>>>Connect switches
	try: verify_moduleRigToggles(self)
	except StandardError,error:
	    raise StandardError,"init.verify_moduleRigToggles>> fail: %s"%error	
	
	#>>> Deform group for the module
	#=========================================================	
	if not self._i_module.getMessage('deformNull'):
	    #Make it and link it
	    buffer = rigging.groupMeObject(self._ml_skinJoints[0].mNode,False)
	    i_grp = cgmMeta.cgmObject(buffer,setClass=True)
	    i_grp.addAttr('cgmName',self._partName,lock=True)
	    i_grp.addAttr('cgmTypeModifier','deform',lock=True)	 
	    i_grp.doName()
	    i_grp.parent = self._i_masterDeformGroup.mNode
	    self._i_module.connectChildNode(i_grp,'deformNull','module')
	    
	self._i_deformNull = self._i_module.deformNull
	
	#>>> Constrain Deform group for the module
	#=========================================================	
	if not self._i_module.getMessage('constrainNull'):
	    #Make it and link it
	    buffer = rigging.groupMeObject(self._ml_skinJoints[0].mNode,False)
	    i_grp = cgmMeta.cgmObject(buffer,setClass=True)
	    i_grp.addAttr('cgmName',self._partName,lock=True)
	    i_grp.addAttr('cgmTypeModifier','constrain',lock=True)	 
	    i_grp.doName()
	    i_grp.parent = self._i_deformNull.mNode
	    self._i_module.connectChildNode(i_grp,'constrainNull','module')
	    
	self._i_constrainNull = self._i_module.constrainNull
	
        #Make our stuff
	self._md_controlShapes = {}
	if self._partType in l_modulesDone:
	    if self._outOfDate:
		self.build(self,**kws)
	    else:
		log.info("'%s' Up to date. No force."%self._strShortName)
	else:
	    log.warning("'%s' module type not in done list. No auto build"%self.buildModule.__name__)

    def isShaped(self):
	"""
	Return if a module is shaped or not
	"""
	if self._partType in d_moduleTypeToBuildModule.keys():
	    checkShapes = d_moduleTypeToBuildModule[self._partType].__d_controlShapes__
	else:
	    log.debug("%s.isShaped>>> Don't have a shapeDict, can't check. Passing..."%(self._strShortName))	    
	    return True
	for key in checkShapes.keys():
	    for subkey in checkShapes[key]:
		if not self._i_rigNull.getMessage('%s_%s'%(key,subkey)):
		    log.debug("%s.isShaped>>> Missing %s '%s' "%(self._strShortName,key,subkey))
		    return False		
	return True
    
    def isRigSkeletonized(self):
	"""
	Return if a module is rig skeletonized or not
	"""
	for key in self._l_jointAttrs:
	    if not self._i_rigNull.getMessage('%s'%(key)):
		log.debug("%s.isSkeletonized>>> Missing key '%s'"%(self._strShortName,key))
		return False		
	return True
    
    def cleanTempAttrs(self):
	for key in self._shapesDict.keys():
	    for subkey in self._shapesDict[key]:
		self._i_rigNull.doRemove('%s_%s'%(key,subkey))
	return True
    
    def getInfluenceChains(self):
	#>>>Influence Joints
	l_influenceChains = []
	ml_influenceChains = []
	for i in range(100):
	    buffer = self._i_rigNull.getMessage('segment%s_InfluenceJoints'%i)
	    if buffer:
		l_influenceChains.append(buffer)
		ml_influenceChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	    else:
		break 
	log.info("%s.getInfluenceChains>>> Segment Influence Chains -- cnt: %s | lists: %s"%(self._strShortName,len(l_influenceChains),l_influenceChains)) 		
	return ml_influenceChains
	
    def getSegmentHandleChains(self):
	l_segmentHandleChains = []
	ml_segmentHandleChains = []
	for i in range(50):
	    buffer = self._i_rigNull.getMessage('segmentHandles_%s'%i,False)
	    if buffer:
		l_segmentHandleChains.append(buffer)
		ml_segmentHandleChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	    else:
		break
	log.info("%s.getSegmentHandleChains>>> Segment Handle Chains -- cnt: %s | lists: %s"%(self._strShortName,len(l_segmentHandleChains),l_segmentHandleChains)) 	
	return ml_segmentHandleChains
	
    def getSegmentChains(self):
	#Get our segment joints
	l_segmentChains = []
	ml_segmentChains = []
	for i in range(50):
	    buffer = self._i_rigNull.getMessage('segment%s_Joints'%i)
	    if buffer:
		l_segmentChains.append(buffer)
		ml_segmentChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	    else:
		break
	log.info("%s.getSegmentChains>>> Segment Chains -- cnt: %s | lists: %s"%(self._strShortName,len(l_segmentChains),l_segmentChains)) 
	return ml_segmentChains
        
    def get_rigDeformationJoints(self):
	#Get our joints that segment joints will connect to
	try:
	    if not self._i_rigNull.getMessage('rigJoints'):
		log.error("%s.get_rigDeformationJoints >> no rig joints found"%self._strShortName)
		return []	    
	    ml_defJoints = []
	    if not self._i_rigNull.getMessage('rigJoints'):raise StandardError,"%s.get_rigDeformationJoints >> no rig joints found"%self._strShortName	    
	    ml_rigJoints = self._i_rigNull.rigJoints or []
	    for i_jnt in ml_rigJoints:
		if not i_jnt.getMessage('scaleJoint'):
		    ml_defJoints.append(i_jnt)	    
	    return ml_defJoints
	
	except StandardError,error:
	    raise StandardError,"%s.get_rigDeformationJoints >> Failure: %s"%(self._strShortName,error)
	
    def get_handleJoints(self):
	return get_rigHandleJoints(self._i_module)
    
    @cgmGeneral.Timer
    def get_report(self):
	self._i_module.rig_getReport()
	
	
    #>>> Joint chains
    #=====================================================================    
    def build_rigChain(self):
	#Get our segment joints
	l_rigJointsExist = self._i_rigNull.getMessage('rigJoints') or []
	if l_rigJointsExist:
	    log.error("Deleting existing rig chain")
	    mc.delete(l_rigJointsExist)
	
	l_rigJoints = mc.duplicate(self._l_skinJoints,po=True,ic=True,rc=True)
	ml_rigJoints = []
	for i,j in enumerate(l_rigJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
	    i_j.doName()
	    l_rigJoints[i] = i_j.mNode
	    ml_rigJoints.append(i_j)
	    i_j.connectChildNode(self._l_skinJoints[i],'skinJoint','rigJoint')#Connect	    
	    if i_j.hasAttr('scaleJoint'):
		if i_j.scaleJoint in self._ml_skinJoints:
		    int_index = self._ml_skinJoints.index(i_j.scaleJoint)
		    i_j.connectChildNode(l_rigJoints[int_index],'scaleJoint','rootJoint')#Connect
		    
	    if i_j.hasAttr('rigJoint'):i_j.doRemove('rigJoint')
	
	self._i_rigNull.connectChildrenNodes(ml_rigJoints,'rigJoints','rigNull')
	self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints','rigNull')#Push back
	self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back
	
	return ml_rigJoints
    
    def build_handleChain(self,typeModifier = 'handle',connectNodesAs = False):    
	try:
	    ml_handleJoints = self._i_module.rig_getHandleJoints()
	    ml_handleChain = []
	    
	    for i,i_handle in enumerate(ml_handleJoints):
		i_new = i_handle.doDuplicate()
		if ml_handleChain:#if we have data, parent to last
		    i_new.parent = ml_handleChain[-1]
		else:i_new.parent = False
		
		i_new.addAttr('cgmTypeModifier',typeModifier,attrType='string',lock=True)
		i_new.doName()
		
		#i_new.rotateOrder = self._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations
		ml_handleChain.append(i_new)
		
	    self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints','rigNull')#Push back
	    self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back
	    log.info("%s.buildHandleChain >> built '%s handle chain: %s"%(self._strShortName,typeModifier,[i_j.getShortName() for i_j in ml_handleChain]))
	    if connectNodesAs not in [None,False] and type(connectNodesAs) in [str,unicode]:
		self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,connectNodesAs,'rigNull')#Push back		
	    return ml_handleChain

	except StandardError,error:
	    raise StandardError,"%s.build_rigChain >> Failure: %s"%(self._strShortName,error)

    def build_segmentChains(self, ml_segmentHandleJoints = None, connectNodes = True):
	ml_segmentChains = []
	if ml_segmentHandleJoints is None:
	    ml_segmentHandleJoints = get_segmentHandleTargets(self._i_module)
	    
	if not ml_segmentHandleJoints:raise StandardError,"%s.build_segmentChains>> failed to get ml_segmentHandleJoints"%self._strShortName
	
	l_segPairs = lists.parseListToPairs(ml_segmentHandleJoints)
	
	for i,ml_pair in enumerate(l_segPairs):
	    index_start = self._ml_moduleJoints.index(ml_pair[0])
	    index_end = self._ml_moduleJoints.index(ml_pair[-1]) + 1
	    buffer_segmentTargets = self._ml_moduleJoints[index_start:index_end]
	    
	    log.info("segment %s: %s"%(i,buffer_segmentTargets))
	    
	    ml_newChain = []
	    for i2,j in enumerate(buffer_segmentTargets):
		i_j = j.doDuplicate()
		i_j.addAttr('cgmTypeModifier','seg_%s'%i,attrType='string',lock=True)
		i_j.doName()
		if ml_newChain:
		    i_j.parent = ml_newChain[-1].mNode
		ml_newChain.append(i_j)
		
	    ml_newChain[0].parent = False#Parent to deformGroup
	    ml_segmentChains.append(ml_newChain)
	
	#Sometimes last segement joints have off orientaions, we're gonna fix
	joints.doCopyJointOrient(ml_segmentChains[-1][-2].mNode,ml_segmentChains[-1][-1].mNode)
	for segmentChain in ml_segmentChains:
	    jntUtils.metaFreezeJointOrientation([i_jnt.mNode for i_jnt in segmentChain])
	    
	#Connect stuff ============================================================================================    
	self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints','rigNull')#Push back
	self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back	
	if connectNodes:
	    for i,ml_chain in enumerate(ml_segmentChains):
		l_chain = [i_jnt.getShortName() for i_jnt in ml_chain]
		log.info("segment chain %s: %s"%(i,l_chain))
		self._i_rigNull.connectChildrenNodes(ml_chain,'segment%s_Joints'%i,"rigNull")
		log.info("segment%s_Joints>> %s"%(i,self._i_rigNull.getMessage('segment%s_Joints'%i,False)))
		
	return ml_segmentChains
	
    @cgmGeneral.Timer
    def build_simpleInfluenceChains(self,addMidInfluence = True):
	"""
	
	"""
	ml_handleJoints = self._i_module.rig_getHandleJoints()
	ml_segmentHandleJoints = get_segmentHandleTargets(self._i_module)
	
	#>> Make influence joints ================================================================================
	l_influencePairs = lists.parseListToPairs(ml_segmentHandleJoints)
	ml_influenceJoints = []
	ml_influenceChains = []
	
	for i,m_pair in enumerate(l_influencePairs):#For each pair
	    str_nameModifier = 'seg_%s'%i	    
	    l_tmpChain = []
	    ml_midJoints = []	    
	    for ii,i_jnt in enumerate(m_pair):
		i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
		i_new.parent = False
		i_new.addAttr('cgmNameModifier',str_nameModifier,attrType='string',lock=True)
		i_new.addAttr('cgmTypeModifier','influence',attrType='string',lock=True)		
		if l_tmpChain:
		    i_new.parent = l_tmpChain[-1].mNode
		i_new.doName()
		i_new.rotateOrder = self._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations    
		l_tmpChain.append(i_new)
		
	    if addMidInfluence:
		log.info("%s.build_simpleInfuenceChains>>> Splitting influence segment: 2 |'%s' >> '%s'"%(self._i_module.getShortName(),m_pair[0].getShortName(),m_pair[1].getShortName()))
		l_new_chain = joints.insertRollJointsSegment(l_tmpChain[0].mNode,l_tmpChain[1].mNode,1)
		#Let's name our new joints
		for ii,jnt in enumerate(l_new_chain):
		    i_jnt = cgmMeta.cgmObject(jnt,setClass=True)
		    i_jnt.doCopyNameTagsFromObject(m_pair[0].mNode)
		    i_jnt.addAttr('cgmName','%s_mid_%s'%(m_pair[0].cgmName,ii),lock=True)
		    i_jnt.addAttr('cgmNameModifier',str_nameModifier,attrType='string',lock=True)		
		    i_jnt.addAttr('cgmTypeModifier','influence',attrType='string',lock=True)		
		    i_jnt.doName()
		    ml_midJoints.append(i_jnt)
		
	    #Build the chain lists -------------------------------------------------------------------------------------------
	    ml_segmentChain = [l_tmpChain[0]]
	    if ml_midJoints:
		ml_segmentChain.extend(ml_midJoints)
	    ml_segmentChain.append(l_tmpChain[-1])
	    for i_j in ml_segmentChain:ml_influenceJoints.append(i_j)
	    ml_influenceChains.append(ml_segmentChain)#append to influence chains
	    
	    log.info("%s.buildHandleChain >> built handle chain %s: %s"%(self._strShortName,i,[i_j.getShortName() for i_j in ml_segmentChain]))
	    
	#Copy orientation of the very last joint to the second to last
	joints.doCopyJointOrient(ml_influenceChains[-1][-2].mNode,ml_influenceChains[-1][-1].mNode)

	#Figure out how we wanna store this, ml_influence joints 
	for i_jnt in ml_influenceJoints:
	    i_jnt.parent = False
	    
	for i_j in ml_influenceJoints:
	    jntUtils.metaFreezeJointOrientation(i_j.mNode)#Freeze orientations
	
	#Connect stuff ============================================================================================    
	self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints','rigNull')#Push back
	self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back
	for i,ml_chain in enumerate(ml_influenceChains):
	    l_chain = [i_jnt.getShortName() for i_jnt in ml_chain]
	    log.info("%s.build_simpleInfuenceChains>>> split chain: %s"%(self._i_module.getShortName(),l_chain))
	    self._i_rigNull.connectChildrenNodes(ml_chain,'segment%s_InfluenceJoints'%i,"rigNull")
	    log.info("segment%s_InfluenceJoints>> %s"%(i,self._i_rigNull.getMessage('segment%s_InfluenceJoints'%i,False)))
	
	return {'ml_influenceChains':ml_influenceChains,'ml_influenceJoints':ml_influenceJoints,'ml_segmentHandleJoints':ml_segmentHandleJoints}

#>>> Functions
#=============================================================================================================
def isBuildable(goInstance):
    if not issubclass(type(goInstance),go):
	log.error("Not a RigFactory.go instance: '%s'"%goInstance)
	raise StandardError
    self = goInstance#Link
    
    if self._partType not in d_moduleTypeToBuildModule.keys():
	log.error("%s.isBuildable>>> Not in d_moduleTypeToBuildModule"%(self._strShortName))	
	return False
    
    try:#Version
	self._buildVersion = d_moduleTypeToBuildModule[self._partType].__version__    
    except:
	log.error("%s.isBuildable>>> Missing version"%(self._strShortName))	
	return False	
    try:#Shapes dict
	self._shapesDict = d_moduleTypeToBuildModule[self._partType].__d_controlShapes__    
    except:
	log.error("%s.isBuildable>>> Missing shape dict in module"%(self._strShortName))	
	return False	
    try:#Joints list
	self._l_jointAttrs = d_moduleTypeToBuildModule[self._partType].__l_jointAttrs__    
    except:
	log.error("%s.isBuildable>>> Missing joint attr list in module"%(self._strShortName))	
	return False
    try:#Joints list
	self.build = d_moduleTypeToBuildModule[self._partType].__build__
	self.buildModule = d_moduleTypeToBuildModule[self._partType]
    except:
	log.error("%s.isBuildable>>> Missing Build Function"%(self._strShortName))	
	return False	
    
    return True
    
#@r9General.Timer
def verify_moduleRigToggles(goInstance):
    """
    Rotate orders
    hips = 3
    """    
    if not issubclass(type(goInstance),go):
	log.error("Not a RigFactory.go instance: '%s'"%goInstance)
	raise StandardError
    self = goInstance#Link
    
    str_settings = str(self._i_masterSettings.getShortName())
    str_partBase = str(self._partName + '_rig')
    str_moduleRigNull = str(self._i_rigNull.getShortName())
    
    self._i_masterSettings.addAttr(str_partBase,enumName = 'off:lock:on', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
    try:NodeF.argsToNodes("%s.gutsVis = if %s.%s > 0"%(str_moduleRigNull,str_settings,str_partBase)).doBuild()
    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> vis arg fail: %s"%error
    try:NodeF.argsToNodes("%s.gutsLock = if %s.%s == 2:0 else 2"%(str_moduleRigNull,str_settings,str_partBase)).doBuild()
    except StandardError,error:
	raise StandardError,"verify_moduleRigToggles>> lock arg fail: %s"%error

    self._i_rigNull.overrideEnabled = 1		
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(self._i_rigNull.mNode,'overrideVisibility'))
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(self._i_rigNull.mNode,'overrideDisplayType'))    

    return True

def bindJoints_connect(goInstance):
    if not issubclass(type(goInstance),go):
	log.error("Not a RigFactory.go instance: '%s'"%goInstance)
	raise StandardError
    self = goInstance#Link
    
    l_rigJoints = self._i_rigNull.getMessage('rigJoints') or False
    l_skinJoints = self._i_rigNull.getMessage('skinJoints',False) or False
    log.info("%s.connect_ToBind>> skinJoints:  len: %s | joints: %s"%(self._i_module.getShortName(),len(l_skinJoints),l_skinJoints))
    if not l_rigJoints:
	raise StandardError,"connect_ToBind>> No Rig Joints: %s "%(self._i_module.getShortName())
    if len(l_skinJoints)!=len(l_rigJoints):
	raise StandardError,"connect_ToBind>> Rig/Skin joint chain lengths don't match: %s | len(skinJoints): %s | len(rigJoints): %s"%(self._i_module.getShortName(),len(l_skinJoints),len(l_rigJoints))
    
    for i,i_jnt in enumerate(self._i_rigNull.skinJoints):
	log.info("'%s'>>drives>>'%s'"%(self._i_rigNull.rigJoints[i].getShortName(),i_jnt.getShortName()))
	pntConstBuffer = mc.parentConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)        
	#pntConstBuffer = mc.pointConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=False,weight=1)
	#orConstBuffer = mc.orientConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=False,weight=1)        
        
        attributes.doConnectAttr((self._i_rigNull.rigJoints[i].mNode+'.s'),(i_jnt.mNode+'.s'))
	#scConstBuffer = mc.scaleConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)                
        #Scale constraint connect doesn't work
    
    return True

def bindJoints_connectToBlend(goInstance):
    if not issubclass(type(goInstance),go):
	log.error("Not a RigFactory.go instance: '%s'"%goInstance)
	raise StandardError
    self = goInstance#Link
    
    l_rigJoints = self._i_rigNull.getMessage('blendJoints') or False
    l_skinJoints = self._i_rigNull.getMessage('skinJoints') or False
    if len(l_skinJoints)!=len(l_rigJoints):
	raise StandardError,"bindJoints_connectToBlend>> Blend/Skin joint chain lengths don't match: %s"%self._i_module.getShortName()
    
    for i,i_jnt in enumerate(self._i_rigNull.skinJoints):
	log.info("'%s'>>drives>>'%s'"%(self._i_rigNull.blendJoints[i].getShortName(),i_jnt.getShortName()))
	pntConstBuffer = mc.parentConstraint(self._i_rigNull.blendJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)        
	#pntConstBuffer = mc.pointConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=False,weight=1)
	#orConstBuffer = mc.orientConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=False,weight=1)        
        
        attributes.doConnectAttr((self._i_rigNull.blendJoints[i].mNode+'.s'),(i_jnt.mNode+'.s'))
	#scConstBuffer = mc.scaleConstraint(self._i_rigNull.rigJoints[i].mNode,i_jnt.mNode,maintainOffset=True,weight=1)                
        #Scale constraint connect doesn't work
    
    return True


#>>> Module rig functions
"""
You should only pass modules into these 
"""
def get_rigHandleJoints(self):
    #Get our segment joints
    try:
	if not self.rigNull.getMessage('rigJoints'):
	    log.error("%s.get_rigHandleJoints >> no rig joints found"%self.getShortName())
	    return []
	ml_handleJoints = []
	ml_rigJoints = self.rigNull.rigJoints or []
	if not ml_rigJoints:raise StandardError,"%s.get_rigHandleJoints >> no rig joints found"%self.getShortName()
	for i_jnt in ml_rigJoints:
	    if i_jnt.d_jointFlags.get('isHandle'):ml_handleJoints.append(i_jnt) 
	return ml_handleJoints
    except StandardError,error:
	raise StandardError,"get_rigHandleJoints >> self: %s | error: %s"%(self,error)
    
def get_rigDeformationJoints(self):
    #Get our joints that segment joints will connect to
    try:
	if not self.rigNull.getMessage('rigJoints'):
	    log.error("%s.get_rigDeformationJoints >> no rig joints found"%self.getShortName())
	    return []	    
	ml_defJoints = []
	if not self.rigNull.getMessage('rigJoints'):raise StandardError,"%s.get_rigDeformationJoints >> no rig joints found"%self.getShortName()	    
	ml_rigJoints = self.rigNull.rigJoints or []
	for i_jnt in ml_rigJoints:
	    if not i_jnt.getMessage('scaleJoint'):
		ml_defJoints.append(i_jnt)	    
	return ml_defJoints
    
    except StandardError,error:
	raise StandardError,"get_rigDeformationJoints >> self: %s | error: %s"%(self,error)
    
def get_handleJoints(self):
    #Get our segment joints
    try:
	ml_handleJoints = []
	for i_obj in self.templateNull.controlObjects:
	    ml_handleJoints.append( i_obj.handleJoint )
	return ml_handleJoints
    except StandardError,error:
	raise StandardError,"get_handleJoints >> self: %s | error: %s"%(self,error)

def get_segmentHandleTargets(self):
    """
    Figure out which segment handle target joints
    """
    try:
	ml_handleJoints = self.rig_getHandleJoints()
	ml_segmentHandleJoints = []#To use later as well
	
	#>> Find our segment handle joints ======================================================================
	#Get our count of roll joints
	l_segmentRollCounts = self.get_rollJointCountList()
	for i,int_i in enumerate(l_segmentRollCounts):
	    if int_i > 0:
		ml_segmentHandleJoints.extend([ml_handleJoints[i],ml_handleJoints[i+1]])
		
	ml_segmentHandleJoints = lists.returnListNoDuplicates(ml_segmentHandleJoints)
	l_segmentHandleJoints = [i_jnt.getShortName() for i_jnt in ml_segmentHandleJoints]
	log.info("%s.get_segmentHandleTargets >> segmentHandleJoints : %s"%(self.getShortName(),l_segmentHandleJoints))
	
	return ml_segmentHandleJoints    
    
    except StandardError,error:
	raise StandardError,"get_segmentHandleTargets >> self: %s | error: %s"%(self,error)
    
@cgmGeneral.Timer
def get_report(self):
    try:
	l_moduleJoints = self.rigNull.getMessage('moduleJoints',False) or []
	l_skinJoints = self.rigNull.getMessage('skinJoints',False) or []
	ml_handleJoints = get_handleJoints(self) or []
	l_rigJoints = self.rigNull.getMessage('rigJoints',False) or []
	ml_rigHandleJoints = get_rigHandleJoints(self)
	ml_rigDefJoints = get_rigDeformationJoints(self)
	ml_segmentHandleTargets = get_segmentHandleTargets(self) or []
	
	log.info("%s.get_report >> "%self.getShortName() + "="*50)
	log.info("moduleJoints: len - %s | %s"%(len(l_moduleJoints),l_moduleJoints))	
	log.info("skinJoints: len - %s | %s"%(len(l_skinJoints),l_skinJoints))	
	log.info("handleJoints: len - %s | %s"%(len(ml_handleJoints),[i_jnt.getShortName() for i_jnt in ml_handleJoints]))	
	log.info("rigJoints: len - %s | %s"%(len(l_rigJoints),l_rigJoints))	
	log.info("rigHandleJoints: len - %s | %s"%(len(ml_rigHandleJoints),[i_jnt.getShortName() for i_jnt in ml_rigHandleJoints]))	
	log.info("rigDeformationJoints: len - %s | %s"%(len(ml_rigDefJoints),[i_jnt.getShortName() for i_jnt in ml_rigDefJoints]))	
	log.info("segmentHandleTargets: len - %s | %s"%(len(ml_segmentHandleTargets),[i_jnt.getShortName() for i_jnt in ml_segmentHandleTargets]))	
	
	log.info("="*75)
	
    except StandardError,error:
	raise StandardError,"get_report >> self: %s | error: %s"%(self,error)	
"""	
@r9General.Timer
def build_spine(goInstance, buildTo='',): 
    if not issubclass(type(goInstance),go):
        log.error("Not a RigFactory.go instance: '%s'"%goInstance)
        raise StandardError
    self = goInstance#Link
    
    spine.build_shapes(self)
    if buildTo.lower() == 'shapes':return
    spine.build_rigSkeleton(self)  
    if buildTo.lower() == 'skeleton':return
    return 'pickle'
    spine.build_controls(self)    
    spine.build_deformation(self)
    spine.build_rig(self)    
        
    return 

@r9General.Timer
def build_neckHead(goInstance,buildShapes = False, buildControls = False,buildSkeleton = False, buildDeformation = False, buildRig= False): 
    if not issubclass(type(goInstance),go):
        log.error("Not a RigFactory.go instance: '%s'"%goInstance)
        raise StandardError
    self = goInstance#Link
    
    if buildShapes: neckHead.build_shapes(self)
    if buildSkeleton: neckHead.build_rigSkeleton(self)    
    if buildControls: neckHead.build_controls(self)    
    if buildDeformation: neckHead.build_deformation(self)
    if buildRig: neckHead.build_rig(self)    
        
    return 

@r9General.Timer
def build_leg(goInstance,buildShapes = False, buildControls = False,buildSkeleton = False, buildDeformation = False, buildRig= False):
    Rotate orders
    hips = 3
    if not issubclass(type(goInstance),go):
        log.error("Not a RigFactory.go instance: '%s'"%goInstance)
        raise StandardError
    self = goInstance#Link
    
    if buildShapes: leg.build_shapes(self)
    if buildSkeleton: leg.build_rigSkeleton(self)    
    if buildControls: leg.build_controls(self)    
    if buildDeformation: leg.build_deformation(self)
    if buildRig: leg.build_rig(self)    
        
    return """

