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
reload(cgmGeneral)
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.classes import GuiFactory as gui
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)
from cgm.core.lib import rayCaster as RayCast
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
reload(mShapeCast)
from cgm.core.lib import nameTools
from cgm.core.rigger.lib import joint_Utils as jntUtils
reload(jntUtils)
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
l_modulesDone  = ['torso','neckhead','leg','clavicle','arm','finger','thumb']
#l_modulesDone = []
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
    
__l_moduleJointSingleHooks__ = ['scaleJoint']
__l_moduleJointMsgListHooks__ = ['helperJoints']

#>>> Main class function
#=====================================================================
class go(object):
    def __init__(self,moduleInstance,forceNew = True,autoBuild = True, ignoreRigCheck = False, **kws): 
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
	b_rigged = self._i_module.isRigged()
	if b_rigged and forceNew is not True and ignoreRigCheck is not True:
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
        self._ml_moduleJoints = self._i_rigNull.msgList_get('moduleJoints',asMeta = True,cull = True)
	if not self._ml_moduleJoints:raise StandardError, "No module joints found!"
        self._l_moduleJoints = [j.p_nameShort for j in self._ml_moduleJoints]
        self._ml_skinJoints = get_skinJoints(self._i_module,asMeta=True)
	if not self._ml_moduleJoints:raise StandardError, "No module joints found!"        
        self._l_skinJoints = [j.p_nameShort for j in self._ml_skinJoints]
	
        #self._ml_rigJoints = self._i_rigNull.msgList_get('rigJoints',asMeta = True,cull = True)	
	#self._l_rigJoints = [j.p_nameShort for j in self._ml_rigJoints]
	
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
	self._vectorAim = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	self._vectorUp = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
	self._vectorOut = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[2])
	
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
	    if self._outOfDate and autoBuild:
		self.doBuild(**kws)
	    else:
		log.info("'%s' No autobuild."%self._strShortName)
	else:
	    log.warning("'%s' module type not in done list. No auto build"%self.buildModule.__name__)
    
    @cgmGeneral.Timer
    def doBuild(self,buildTo = '',**kws):
	"""
	Return if a module is shaped or not
	"""
	d_build = self.buildModule.__d_buildOrder__
	int_keys = d_build.keys()
	
	#Build our progress Bar
	mayaMainProgressBar = gui.doStartMayaProgressBar(len(int_keys))
	#mc.progressBar(mayaMainProgressBar, edit=True, progress=0) 
	for k in int_keys:
	    try:
		str_name = d_build[k].get('name') or 'noName'
		func_current = d_build[k].get('function')
    
		mc.progressBar(mayaMainProgressBar, edit=True, status = "%s >>Rigging>> step:'%s'..."%(self._strShortName,str_name), progress=k+1)    
		func_current(self)
    
		if buildTo.lower() == str_name:
		    log.info("%s.doBuild >> Stopped at step : %s"%(self._strShortName,str_name))
		    break
	    except StandardError,error:
		raise StandardError,"%s.doBuild >> Step %s failed! | %s"%(self._strShortName,str_name,error)
	    
	gui.doEndMayaProgressBar(mayaMainProgressBar)#Close out this progress bar        
	
	    
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
		    if not self._i_rigNull.msgList_get('%s_%s'%(key,subkey),False):
			log.warning("%s.isShaped>>> Missing %s '%s' "%(self._strShortName,key,subkey))
			return False		
	return True
    
    def isRigSkeletonized(self):
	"""
	Return if a module is rig skeletonized or not
	"""
	for key in self._l_jointAttrs:
	    if not self._i_rigNull.getMessage('%s'%(key)) and not self._i_rigNull.msgList_getMessage('%s'%(key)):
		log.error("%s.isRigSkeletonized>>> Missing key '%s'"%(self._strShortName,key))
		return False		
	return True
    
    def cleanTempAttrs(self):
	for key in self._shapesDict.keys():
	    for subkey in self._shapesDict[key]:
		self._i_rigNull.doRemove('%s_%s'%(key,subkey))
	return True
    
    def _get_influenceChains(self):
	return get_influenceChains(self._i_module)	
	
    def _get_segmentHandleChains(self):
	return get_segmentHandleChains(self._i_module)
	
    def _get_segmentChains(self):
	return get_segmentChains(self._i_module)
        
    def _get_rigDeformationJoints(self):
	return get_rigDeformationJoints(self._i_module)
	
    def _get_handleJoints(self):
	return get_rigHandleJoints(self._i_module)
    
    def _get_simpleRigJointDriverDict(self):
	return get_simpleRigJointDriverDict(self._i_module)
    
    @cgmGeneral.Timer
    def get_report(self):
	self._i_module.rig_getReport()
	
    def _set_versionToCurrent(self):
	self._i_rigNull.version = str(self._buildVersion)	
	
    #>> Connections
    #=====================================================================
    def connect_toRigGutsVis(self, ml_objects, vis = True):
	try:
	    for i_obj in ml_objects:
		i_obj.overrideEnabled = 1		
		if vis: cgmMeta.cgmAttr(self._i_module.rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideVisibility'))
		cgmMeta.cgmAttr(self._i_module.rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_obj.mNode,'overrideDisplayType'))    
	except StandardError,error:
	    raise StandardError,"%s.connect_toRigGutsVis >> Failure: %s"%(self._strShortName,error)
    
    def connect_restoreJointLists(self):
	raise DeprecationWarning, "Please remove this instance of 'connect_restoreJointLists'"
	try:
	    if self._ml_rigJoints:
		log.info("%s.connect_restoreJointLists >> Found rig joints to store back"%self._strShortName)
		self._i_rigNull.connectChildrenNodes(self._ml_rigJoints,'rigJoints','rigNull')
	    self._i_rigNull.connectChildrenNodes(self._ml_skinJoints,'skinJoints','rigNull')#Push back
	    self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back
	except StandardError,error:
	    raise StandardError,"%s.connect_restoreJointLists >> Failure: %s"%(self._strShortName,error)
    
    #>> Attributes
    #=====================================================================
    def _verify_moduleMasterScale(self):
	log.info(">>> %s._verify_compoundScale >> "%self._strShortName + "="*75)            	
	mPlug_moduleMasterScale = cgmMeta.cgmAttr(self._i_rigNull,'masterScale',value = 1.0,defaultValue=1.0)
	mPlug_globalScale = cgmMeta.cgmAttr(self._i_masterControl.mNode,'scaleY')
	mPlug_globalScale.doConnectOut(mPlug_moduleMasterScale)
	
    def _get_masterScalePlug(self):
	log.info(">>> %s._get_masterScalePlug >> "%self._strShortName + "="*75)
	if self._i_rigNull.hasAttr('masterScale'):
	    return cgmMeta.cgmAttr(self._i_rigNull,'masterScale')
	return cgmMeta.cgmAttr(self._i_masterControl.mNode,'scaleY')
	
			    
    #>>> Joint chains
    #=====================================================================    
    def build_rigChain(self):
	#Get our segment joints
	l_rigJointsExist = self._i_rigNull.msgList_get('rigJoints',asMeta = False, cull = True)
	if l_rigJointsExist:
	    log.error("Deleting existing rig chain")
	    mc.delete(l_rigJointsExist)
	    
	l_rigJoints = mc.duplicate([i_jnt.mNode for i_jnt in self._ml_skinJoints],po=True,ic=True,rc=True)
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
		    i_j.connectChildNode(l_rigJoints[int_index],'scaleJoint','sourceJoint')#Connect
		    
	    if i_j.hasAttr('rigJoint'):i_j.doRemove('rigJoint')
	
	self._ml_rigJoints = ml_rigJoints
	self._l_rigJoints = [i_jnt.p_nameShort for i_jnt in ml_rigJoints]
	self._i_rigNull.msgList_connect(ml_rigJoints,'rigJoints','rigNull')#connect	
	return ml_rigJoints
    
    def build_handleChain(self,typeModifier = 'handle',connectNodesAs = False):    
	try:
	    ml_handleJoints = self._i_module.rig_getHandleJoints()
	    ml_handleChain = []
	    
	    for i,i_handle in enumerate(ml_handleJoints):
		i_new = i_handle.doDuplicate()
		if ml_handleChain:i_new.parent = ml_handleChain[-1]#if we have data, parent to last
		else:i_new.parent = False
		i_new.addAttr('cgmTypeModifier',typeModifier,attrType='string',lock=True)
		i_new.doName()
		
		#i_new.rotateOrder = self._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations
		ml_handleChain.append(i_new)
		
	    #self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints','rigNull')#Push back
	    #self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back
	    log.info("%s.buildHandleChain >> built '%s handle chain: %s"%(self._strShortName,typeModifier,[i_j.getShortName() for i_j in ml_handleChain]))
	    if connectNodesAs not in [None,False] and type(connectNodesAs) in [str,unicode]:
		self._i_rigNull.msgList_connect(ml_handleChain,connectNodesAs,'rigNull')#Push back		
	    return ml_handleChain

	except StandardError,error:
	    raise StandardError,"%s.build_rigChain >> Failure: %s"%(self._strShortName,error)
    
    def duplicate_moduleJoint(self, index = None, typeModifier = 'duplicate', connectNodesAs = False):    
	"""
	This is only necessary because message connections are duplicated and make duplicating connected joints problematic
	"""
	try:
	    if index is None:
		raise StandardError, "%s.duplicate_moduleJoint >> No index specified"%(self._strShortName)
	    if type(index) is not int:
		raise StandardError, "%s.duplicate_moduleJoint >> index not int: %s | %s"%(self._strShortName,index,type(index))
	    if index > len(self._ml_moduleJoints)+1:
		raise StandardError, "%s.duplicate_moduleJoint >> index > len(moduleJoints): %s | %s"%(self._strShortName,index,(len(self._ml_moduleJoints)+1))
	    
	    i_target = self._ml_moduleJoints[index]
	    buffer = mc.duplicate(i_target.mNode,po=True,ic=True)[0]
	    i_new = cgmMeta.validateObjArg(buffer,cgmMeta.cgmObject)
	    i_new.parent = False
	    
	    i_new.addAttr('cgmTypeModifier',typeModifier,attrType='string',lock=True)
	    i_new.doName()
		
	    #Push back our nodes
	    self.connect_restoreJointLists()#Push back
	    log.info("%s.duplicate_moduleJoint >> created: %s"%(self._strShortName,i_new.p_nameShort))
	    if connectNodesAs not in [None,False] and type(connectNodesAs) in [str,unicode]:
		self._i_rigNull.connectChildNode(i_new,connectNodesAs,'rigNull')#Push back		
	    return i_new

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
	#self._i_rigNull.connectChildrenNodes(self._l_skinJoints,'skinJoints','rigNull')#Push back
	#self._i_rigNull.connectChildrenNodes(self._ml_moduleJoints,'moduleJoints','rigNull')#Push back	
	if connectNodes:
	    for i,ml_chain in enumerate(ml_segmentChains):
		l_chain = [i_jnt.getShortName() for i_jnt in ml_chain]
		log.info("segment chain %s: %s"%(i,l_chain))
		self._i_rigNull.msgList_connect(ml_chain,'segment%s_Joints'%i,"rigNull")
		log.info("segment%s_Joints>> %s"%(i,self._i_rigNull.msgList_getMessage('segment%s_Joints'%i,False)))
		
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
	for i,ml_chain in enumerate(ml_influenceChains):
	    l_chain = [i_jnt.getShortName() for i_jnt in ml_chain]
	    log.info("%s.build_simpleInfuenceChains>>> split chain: %s"%(self._i_module.getShortName(),l_chain))
	    self._i_rigNull.msgList_connect(ml_chain,'segment%s_InfluenceJoints'%i,"rigNull")
	    log.info("segment%s_InfluenceJoints>> %s"%(i,self._i_rigNull.msgList_getMessage('segment%s_InfluenceJoints'%i,False)))
	
	return {'ml_influenceChains':ml_influenceChains,'ml_influenceJoints':ml_influenceJoints,'ml_segmentHandleJoints':ml_segmentHandleJoints}

#>>> Functions
#=============================================================================================================
@cgmGeneral.Timer
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
    try:#Build Module
	#self.build = d_moduleTypeToBuildModule[self._partType].__build__
	self.buildModule = d_moduleTypeToBuildModule[self._partType]
    except:
	log.error("%s.isBuildable>>> Missing Build Module"%(self._strShortName))	
	return False	    
    try:#Build Dict
	d_moduleTypeToBuildModule[self._partType].__d_buildOrder__
    except:
	log.error("%s.isBuildable>>> Missing Build Function Dictionary"%(self._strShortName))	
	return False	    

    
    return True
    
@cgmGeneral.Timer
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

@cgmGeneral.Timer
def bindJoints_connect(goInstance):
    if not issubclass(type(goInstance),go):
	log.error("Not a RigFactory.go instance: '%s'"%goInstance)
	raise StandardError
    self = goInstance#Link
    
    l_rigJoints = self._i_rigNull.msgList_get('rigJoints',False) or False
    l_skinJoints = self._i_rigNull.msgList_get('skinJoints',False) or False
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

@cgmGeneral.Timer
def bindJoints_connectToBlend(goInstance):
    if not issubclass(type(goInstance),go):
	log.error("Not a RigFactory.go instance: '%s'"%goInstance)
	raise StandardError
    self = goInstance#Link
    
    l_rigJoints = self._i_rigNull.msgList_get('blendJoints',False) or False
    l_skinJoints = self._i_rigNull.msgList_get('skinJoints',False) or False
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
@cgmGeneral.Timer
def get_skinJoints(self, asMeta = True):
    try:
	log.debug(">>> %s.get_skinJoints() >> "%(self.p_nameShort) + "="*75) 
	"""
	if not self.isSkeletonized():
	    raise StandardError,"%s.get_skinJoints >> not skeletonized."%(self.p_nameShort)"""
	ml_skinJoints = []
	ml_moduleJoints = self.rigNull.msgList_get('moduleJoints',asMeta = True, cull = True)
	for i,i_j in enumerate(ml_moduleJoints):
	    ml_skinJoints.append(i_j)
	    for attr in __l_moduleJointSingleHooks__:
		str_attrBuffer = i_j.getMessage(attr)
		if str_attrBuffer:ml_skinJoints.append( cgmMeta.validateObjArg(str_attrBuffer) )
	    for attr in __l_moduleJointMsgListHooks__:
		l_buffer = i_j.msgList_get(attr,asMeta = asMeta,cull = True)
		
	if asMeta:return ml_skinJoints
	if ml_skinJoints:
	    return [obj.p_nameShort for obj in ml_skinJoints]
    except StandardError,error:
	raise StandardError, "%s.get_skinJoints >>[Error]<< : %s"(self.p_nameShort,error)	
@cgmGeneral.Timer    
def get_rigHandleJoints(self, asMeta = True):
    #Get our rig handle joints
    try:
	log.debug(">>> %s.get_rigHandleJoints() >> "%(self.p_nameShort) + "="*75)
	"""
	if not self.isSkeletonized():
	    raise StandardError,"%s.get_rigHandleJoints >> not skeletonized."%(self.p_nameShort)"""	
	#ml_rigJoints = self.rigNull.msgList_get('rigJoints')
	#if not ml_rigJoints:
	    #log.error("%s.get_rigHandleJoints >> no rig joints found"%self.getShortName())
	    #return []	
	l_rigHandleJoints = []
	for i_j in self.rigNull.msgList_get('handleJoints'):
	    str_attrBuffer = i_j.getMessage('rigJoint')
	    if str_attrBuffer:
		l_rigHandleJoints.append(str_attrBuffer)
		
	if asMeta:return cgmMeta.validateObjListArg(l_rigHandleJoints,noneValid=True)	    
	return l_rigHandleJoints
    except StandardError,error:
	raise StandardError,"get_rigHandleJoints >> Probably isn't skeletonized. self: %s | error: %s"%(self,error)
@cgmGeneral.Timer    
def get_rigDeformationJoints(self,asMeta = True):
    #Get our joints that segment joints will connect to
    try:
	ml_rigJoints = self.rigNull.msgList_get('rigJoints')
	if not ml_rigJoints:
	    log.error("%s.get_rigDeformationJoints >> no rig joints found"%self.getShortName())
	    return []	    
	ml_defJoints = []
	for i_jnt in ml_rigJoints:
	    if not i_jnt.getMessage('scaleJoint'):
		ml_defJoints.append(i_jnt)	    
	if asMeta:return ml_defJoints
	elif ml_defJoints:return [j.p_nameShort for j in ml_defJoints]
	return []
    
    except StandardError,error:
	raise StandardError,"get_rigDeformationJoints >> self: %s | error: %s"%(self,error)
@cgmGeneral.Timer    
def get_handleJoints(self,asMeta = True):
    #Get our segment joints
    try:
	log.debug(">>> %s.get_handleJoints() >> "%(self.p_nameShort) + "="*75) 	
	return self.rigNull.msgList_get('handleJoints',asMeta = asMeta, cull = True)
	"""
	ml_handleJoints = []
	for i_obj in self.templateNull.controlObjects:
	    buffer = i_obj.handleJoint
	    if not buffer:
		log.error("%s.get_handleJoints >> '%s' missing handle joint"%(self.p_nameShort,i_obj.p_nameShort))
		return False
	    ml_handleJoints.append( buffer )
	return ml_handleJoints"""
    except StandardError,error:
	raise StandardError,"get_handleJoints >> self: %s | error: %s"%(self,error)
@cgmGeneral.Timer
def get_segmentHandleTargets(self):
    """
    Figure out which segment handle target joints
    """
    try:
	log.debug(">>> %s.get_segmentHandleTargets() >> "%(self.p_nameShort) + "="*75) 		
	ml_handleJoints = self.rig_getHandleJoints()
	log.info(ml_handleJoints)
	if not ml_handleJoints:
	    log.error("%s.get_segmentHandleTargets >> failed to find any handle joints at all"%(self.p_nameShort))
	    raise StandardError
	ml_segmentHandleJoints = []#To use later as well
	
	#>> Find our segment handle joints ======================================================================
	#Get our count of roll joints
	l_segmentRollCounts = self.get_rollJointCountList()
	log.info(l_segmentRollCounts)
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
def get_influenceChains(self):
    try:
	#>>>Influence Joints
	log.debug(">>> %s.get_influenceChains() >> "%(self.p_nameShort) + "="*75) 		
	
	l_influenceChains = []
	ml_influenceChains = []
	for i in range(100):
	    str_check = 'segment%s_InfluenceJoints'%i
	    buffer = self.rigNull.msgList_getMessage(str_check)
	    log.debug("Checking %s: %s"%(str_check,buffer))
	    if buffer:
		l_influenceChains.append(buffer)
		ml_influenceChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	    else:
		break 
	log.info("%s._get_influenceChains>>> Segment Influence Chains -- cnt: %s | lists: %s"%(self.getShortName(),len(l_influenceChains),l_influenceChains)) 		
	return ml_influenceChains
    except StandardError,error:
	raise StandardError,"_get_influenceChains >> self: %s | error: %s"%(self,error)
@cgmGeneral.Timer    
def get_segmentHandleChains(self):
    try:
	log.debug(">>> %s.get_segmentHandleChains() >> "%(self.p_nameShort) + "="*75) 			
	l_segmentHandleChains = []
	ml_segmentHandleChains = []
	for i in range(50):
	    buffer = self.rigNull.msgList_getMessage('segmentHandles_%s'%i,False)
	    if buffer:
		l_segmentHandleChains.append(buffer)
		ml_segmentHandleChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	    else:
		break
	log.info("%s._get_segmentHandleChains>>> Segment Handle Chains -- cnt: %s | lists: %s"%(self.getShortName(),len(l_segmentHandleChains),l_segmentHandleChains)) 	
	return ml_segmentHandleChains
    except StandardError,error:
	raise StandardError,"_get_segmentHandleChains >> self: %s | error: %s"%(self,error)
@cgmGeneral.Timer    
def get_segmentChains(self):
    try:
	#Get our segment joints
	log.debug(">>> %s.get_segmentChains() >> "%(self.p_nameShort) + "="*75) 				
	l_segmentChains = []
	ml_segmentChains = []
	for i in range(50):
	    buffer = self.rigNull.msgList_getMessage('segment%s_Joints'%i,False)
	    if buffer:
		l_segmentChains.append(buffer)
		ml_segmentChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
	    else:
		break
	log.info("%s.get_segmentChains>>> Segment Chains -- cnt: %s | lists: %s"%(self.getShortName(),len(l_segmentChains),l_segmentChains)) 
	return ml_segmentChains
    except StandardError,error:
	raise StandardError,"get_segmentChains >> self: %s | error: %s"%(self,error)
    
@cgmGeneral.Timer    
def get_rigJointDriversDict(self,printReport = True):
    """
    Figure out what drives skin joints. BLend joints should have the priority, then segment joints
    """
    log.debug(">>> %s.get_rigJointDriversDict() >> "%(self.p_nameShort) + "="*75) 				
    
    def __findDefJointFromRigJoint(i_jnt):	    
	if i_jnt.getMessage('rigJoint'):
	    i_rigJoint = cgmMeta.validateObjArg(i_jnt.rigJoint,cgmMeta.cgmObject)
	    if i_rigJoint.hasAttr('scaleJoint'):
		i_scaleJnt = cgmMeta.validateObjArg(i_jnt.scaleJoint,cgmMeta.cgmObject)
		if i_scaleJnt.getShortName() in l_cullRigJoints:
		    #log.info("Checking: %s | %s"%(i_jnt,i_rigJnt))
		    d_rigIndexToDriverInstance[ml_rigJoints.index(i_scaleJnt)] = i_jnt	
		    return
		else:log.warning("%s no in cull list"%i_rigJnt.getShortName())	    	    
		
	    
	    if i_rigJoint.getShortName() in l_cullRigJoints:
		d_rigIndexToDriverInstance[ml_rigJoints.index(i_scaleJnt)] = i_jnt			
		return
	    else:log.warning("%s no in cull list"%i_rigJnt.getShortName())	    	    
	return False
	    
    #>>>Initial checks
    ml_blendJoints = []
    mll_segmentChains = []
    
    try:
	ml_rigJoints = self.rigNull.msgList_get('rigJoints')
    except:
	log.error("%s.get_deformationRigDriversDict >> no rig joints found"%self.getShortName())
	return {}
    
    try:ml_blendJoints = self.rigNull.msgList_get('rigJoints')
    except:log.warning("%s.get_deformationRigDriversDict >> no blend joints found"%self.getShortName())
	 
    try:mll_segmentChains = get_segmentChains(self)
    except StandardError,error:
	log.error("%s.get_deformationRigDriversDict >> mll_segmentChains failure: %s"%(self.getShortName(),error))
    
    if not ml_blendJoints:log.warning("%s.get_deformationRigDriversDict >> no blend joints found"%self.getShortName())
    if not mll_segmentChains:log.warning("%s.get_deformationRigDriversDict >> no segment found"%self.getShortName())
    
    #>>>Declare
    l_cullRigJoints = [i_jnt.getShortName() for i_jnt in ml_rigJoints]	
    d_rigIndexToDriverInstance = {}
    ml_matchTargets = []
    if mll_segmentChains:
	l_matchTargets = []
	for i,ml_chain in enumerate(mll_segmentChains):
	    if i == len(mll_segmentChains)-1:
		ml_matchTargets.extend([i_jnt for i_jnt in ml_chain])
	    else:
		ml_matchTargets.extend([i_jnt for i_jnt in ml_chain[:-1]])		
		
    
    #First let's get our blend joints taken care of:
    if ml_blendJoints:
	for i,i_jnt in enumerate(ml_blendJoints):
	    if i_jnt.getMessage('rigJoint'):
		i_rigJnt = cgmMeta.validateObjArg(i_jnt.rigJoint,cgmMeta.cgmObject)
		if i_rigJnt.getShortName() in l_cullRigJoints:
		    #log.info("Checking: %s | %s"%(i_jnt,i_rigJnt))
		    d_rigIndexToDriverInstance[ml_rigJoints.index(i_rigJnt)] = i_jnt
		    try:l_cullRigJoints.remove(i_rigJnt.getShortName())
		    except:log.error("%s failed to remove from cull list: %s"%(i_rigJnt.getShortName(),l_cullRigJoints))
		else:
		    log.warning("%s no in cull list"%i_rigJnt.getShortName())
	
		        
    #If we have matchTargets, we're going to match them	
    if ml_matchTargets:
	for i,i_jnt in enumerate(ml_matchTargets):
	    if i_jnt.getMessage('rigJoint'):
		i_rigJnt = cgmMeta.validateObjArg(i_jnt.rigJoint,cgmMeta.cgmObject)
		if i_rigJnt.getMessage('scaleJoint'):
		    log.info("Scale joint found!")
		    i_scaleJnt = cgmMeta.validateObjArg(i_rigJnt.scaleJoint,cgmMeta.cgmObject)
		    if i_scaleJnt.getShortName() in l_cullRigJoints:
			#log.info("Checking: %s | %s"%(i_jnt,i_rigJnt))
			d_rigIndexToDriverInstance[ml_rigJoints.index(i_scaleJnt)] = i_jnt	
			try:l_cullRigJoints.remove(i_scaleJnt.getShortName())
			except:log.error("%s failed to remove from cull list: %s"%(i_scaleJnt.getShortName(),l_cullRigJoints))			
		    else:log.warning("scale joint %s not in cull list"%i_rigJnt.getShortName())	   		    
    
		elif i_rigJnt.getShortName() in l_cullRigJoints:
		    #log.info("Checking: %s | %s"%(i_jnt,i_rigJnt))
		    d_rigIndexToDriverInstance[ml_rigJoints.index(i_rigJnt)] = i_jnt
		    try:l_cullRigJoints.remove(i_rigJnt.getShortName())
		    except:log.error("%s failed to remove from cull list: %s"%(i_rigJnt.getShortName(),l_cullRigJoints))	
		else:
		    log.warning("%s no in cull list"%i_rigJnt.getShortName())
		    
    #If we have any left, do a distance check
    l_matchTargets = [i_jnt.mNode for i_jnt in ml_matchTargets]
    for i,jnt in enumerate(l_cullRigJoints):
	i_jnt = cgmMeta.cgmObject(jnt)
	attachJoint = distance.returnClosestObject(jnt,l_matchTargets)
	int_match = l_matchTargets.index(attachJoint)
	d_rigIndexToDriverInstance[ml_rigJoints.index(i_jnt)] = ml_matchTargets[int_match]    
	l_cullRigJoints.remove(jnt)

    if printReport or l_cullRigJoints:
	log.info("%s.get_rigJointDriversDict >> "%self.getShortName() + "="*50)
	for i,i_jnt in enumerate(ml_rigJoints):
	    if d_rigIndexToDriverInstance.has_key(i):
		log.info("'%s'  << driven by << '%s'"%(i_jnt.getShortName(),d_rigIndexToDriverInstance[i].getShortName()))		    
	    else:
		log.info("%s  << HAS NO KEY STORED"%(i_jnt.getShortName()))	
		
	log.info("No matches found for %s | %s "%(len(l_cullRigJoints),l_cullRigJoints))	    
	log.info("="*75)
	    
    if l_cullRigJoints:
	raise StandardError,"%s to find matches for all rig joints: %s"%(i_scaleJnt.getShortName())
    
    return d_rigIndexToDriverInstance
    
    #except StandardError,error:
	#raise StandardError,"get_rigJointDriversDict >> self: %s | error: %s"%(self,error)
	
@cgmGeneral.Timer    
def get_simpleRigJointDriverDict(self,printReport = True):
    log.debug(">>> %s.get_simpleRigJointDriverDict() >> "%(self.p_nameShort) + "="*75) 				    
    """
    Figure out what drives skin joints. BLend joints should have the priority, then segment joints
    """
    #>>>Initial checks
    ml_blendJoints = []
    mll_segmentChains = []
    try:
	ml_moduleJoints = self.rigNull.msgList_get('moduleJoints')
	#ml_moduleJoints = cgmMeta.validateObjListArg(self.rigNull.moduleJoints,cgmMeta.cgmObject,noneValid=False)
    except:
	log.error("%s.get_simpleRigJointDriverDict >> no rig joints found"%self.getShortName())
	return {}
    try:
	ml_rigJoints = self.rigNull.msgList_get('rigJoints')
    except:
	log.error("%s.get_simpleRigJointDriverDict >> no rig joints found"%self.getShortName())
	return {}
    
    try:
	ml_blendJoints = self.rigNull.msgList_get('blendJoints')
    except:log.warning("%s.get_simpleRigJointDriverDict >> no blend joints found"%self.getShortName())
	 
    try:mll_segmentChains = get_segmentChains(self)
    except StandardError,error:
	log.error("%s.get_simpleRigJointDriverDict >> mll_segmentChains failure: %s"%(self.getShortName(),error))
    
    if not ml_blendJoints:log.error("%s.get_simpleRigJointDriverDict >> no blend joints found"%self.getShortName())
    if not mll_segmentChains:log.error("%s.get_simpleRigJointDriverDict >> no segment found"%self.getShortName())
    if not ml_blendJoints or not mll_segmentChains:
	return False
    
    #>>>Declare
    d_rigJointDrivers = {}
    
    ml_moduleRigJoints = []#Build a list of our module rig joints
    for i,i_j in enumerate(ml_moduleJoints):
	ml_moduleRigJoints.append(i_j.rigJoint)
	
    l_cullRigJoints = [i_jnt.getShortName() for i_jnt in ml_moduleRigJoints]	
    
    ml_matchTargets = []
    if mll_segmentChains:
	l_matchTargets = []
	for i,ml_chain in enumerate(mll_segmentChains):
	    ml_matchTargets.extend([i_jnt for i_jnt in ml_chain[:-1]])	
    
    #First time we just check segment chains
    l_matchTargets = [i_jnt.getShortName() for i_jnt in ml_matchTargets]
    for i,i_jnt in enumerate(ml_moduleRigJoints):
	attachJoint = distance.returnClosestObject(i_jnt.mNode,l_matchTargets)
	i_match = cgmMeta.cgmObject(attachJoint)
	if cgmMath.isVectorEquivalent(i_match.getPosition(),i_jnt.getPosition()):
	    d_rigJointDrivers[i_jnt.mNode] = i_match
	    l_cullRigJoints.remove(i_jnt.getShortName())
	    if i_match in ml_matchTargets:
		ml_matchTargets.remove(i_match)
	else:
	    log.debug("'%s' is not in same place as '%s'. Going to second match"%(i_match.getShortName(),i_jnt.getShortName()))
    
    #Now we add blend joints to search list and check again
    ml_matchTargets.extend(ml_blendJoints)    
    l_matchTargets = [i_jnt.getShortName() for i_jnt in ml_matchTargets]
    ml_cullList = cgmMeta.validateObjListArg(l_cullRigJoints,cgmMeta.cgmObject)
    for i,i_jnt in enumerate(ml_cullList):
	attachJoint = distance.returnClosestObject(i_jnt.mNode,l_matchTargets)
	i_match = cgmMeta.cgmObject(attachJoint)
	log.info("Second match: '%s':'%s'"%(i_jnt.getShortName(),i_match.getShortName()))	
	d_rigJointDrivers[i_jnt.mNode] = i_match
	l_cullRigJoints.remove(i_jnt.getShortName())
	ml_matchTargets.remove(i_match)

    if printReport or l_cullRigJoints:
	log.info("%s.get_simpleRigJointDriverDict >> "%self.getShortName() + "="*50)
	for i,i_jnt in enumerate(ml_moduleRigJoints):
	    if d_rigJointDrivers.has_key(i_jnt.mNode):
		log.info("'%s'  << driven by << '%s'"%(i_jnt.getShortName(),d_rigJointDrivers[i_jnt.mNode].getShortName()))		    
	    else:
		log.info("%s  << HAS NO KEY STORED"%(i_jnt.getShortName()))	
		
	log.info("No matches found for %s | %s "%(len(l_cullRigJoints),l_cullRigJoints))	    
	log.info("="*75)
	    
    if l_cullRigJoints:
	raise StandardError,"%s.get_simpleRigJointDriverDict >> failed to find matches for all rig joints: %s"%(self.getShortName(),l_cullRigJoints)
    
    d_returnBuffer = {}
    for str_mNode in d_rigJointDrivers.keys():
	d_returnBuffer[cgmMeta.cgmObject(str_mNode)] = d_rigJointDrivers[str_mNode]
    return d_returnBuffer
    
    #except StandardError,error:
	#raise StandardError,"get_rigJointDriversDict >> self: %s | error: %s"%(self,error)
    
    
@cgmGeneral.Timer
def get_report(self):
    #try:
    if not self.isSkeletonized():
	log.error("%s.get_report >> Not skeletonized. Wrong report."%(self.p_nameShort))
	return False
    l_moduleJoints = self.rigNull.msgList_get('moduleJoints',False) or []
    l_skinJoints = get_skinJoints(self,False)
    ml_handleJoints = get_handleJoints(self) or []
    l_rigJoints = self.rigNull.msgList_get('rigJoints',False) or []
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
	
    #except StandardError,error:
	#raise StandardError,"get_report >> self: %s | error: %s"%(self,error)	


