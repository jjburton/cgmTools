"""
------------------------------------------
cgm.core.rigger: Face.eyelids
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

eyelids rig builder
================================================================
"""
__version__ = 0.08112013

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
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.lib import validateArgs as cgmValid
from cgm.core.rigger.lib import joint_Utils as jntUtils
from cgm.core.lib import curve_Utils as crvUtils
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools

from cgm.core.rigger.lib import rig_Utils as rUtils

from cgm.lib import (attributes,
                     joints,
                     skinning,
                     locators,
                     lists,
                     dictionary,
                     distance,
                     modules,
                     search,
                     curves,
                     )
reload(joints)
reload(lists)
#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['rigJoints']   
@cgmGeneral.Timer
def __bindSkeletonSetup__(self):
    """
    TODO: Do I need to connect per joint overrides or will the final group setup get them?
    """
    log.info(">>> %s.__bindSkeletonSetup__ >> "%self._strShortName + "-"*75)            
    try:
	if not self._cgmClass == 'JointFactory.go':
	    log.error("Not a JointFactory.go instance: '%s'"%self)
	    raise StandardError
	
    except StandardError,error:
	log.error("eyelids.__bindSkeletonSetup__>>bad self!")
	raise StandardError,error
    
    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self.rig_getSkinJoints() or []
    if not self._i_module.isSkeletonized():
	raise StandardError, "%s is not skeletonized yet."%self._strShortName
    try:pass
    except StandardError,error:
	log.error("build_eyelids>>__bindSkeletonSetup__ fail!")
	raise StandardError,error   
    
@cgmGeneral.Timer
def build_rigSkeleton(self):
    """
    """
    try:#===================================================
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("%s.build_rigSkeleton>>bad self!"%self._strShortName)
	raise StandardError,error
    
    _str_funcName = "build_rigSkeleton(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)
    
    try:#>>Info gather =====================================================================
	_str_orientation = self._jointOrientation #Link	
	mi_helper = cgmMeta.validateObjArg(self._i_module.getMessage('helper'),noneValid=True)
	if not mi_helper:raise StandardError,"%s >>> No suitable helper found"%(_str_funcName)    
	
	try:mi_uprLidBase = cgmMeta.validateObjArg(mi_helper.getMessage('uprLidHelper'),noneValid=False)
	except StandardError,error:raise StandardError,"%s >>> Missing uprlid helper | error: %s "%(_str_funcName,error)
	try:mi_lwrLidBase = cgmMeta.validateObjArg(mi_helper.getMessage('lwrLidHelper'),noneValid=False)
	except StandardError,error:raise StandardError,"%s >>> Missing uprlid helper | error: %s "%(_str_funcName,error)    
	int_handles = cgmValid.valueArg(self._i_templateNull.handles)
	d_buildCurves = {'upr':{'crv':mi_uprLidBase,'count':int_handles},
	                 'lwr':{'crv':mi_lwrLidBase,'count':int_handles}}
	
	#Orient info
	_str_upLoc = locators.locMeCvFromCvIndex(mi_helper.getShapes()[0],2)   
	v_aim = cgmValid.simpleAxis(_str_orientation[0]+"-").p_vector
	v_up = cgmValid.simpleAxis(_str_orientation[1]).p_vector	
	
    except StandardError,error:
	raise StandardError,"%s>>Gather Data fail! | error: %s"%(_str_funcName,error)   
    
    try:#>>Handle joints =====================================================================
	for k in d_buildCurves.keys():
	    mi_upLoc = cgmMeta.cgmObject(_str_upLoc)  
	    mi_crv = d_buildCurves[k].get('crv')#get instance
	    int_count = d_buildCurves[k].get('count')#get int
	    log.info("%s >>> building joints for %s curve | count: %s"%(_str_funcName,k, int_count))
	    try:l_pos = crvUtils.returnSplitCurveList(mi_crv.mNode,int_count,rebuildSpans=10)
	    except StandardError,error:raise StandardError,"%s >>> Crv split fail | error: %s "%(_str_funcName,error)       
	    if k == 'lwr':l_pos = l_pos[1:-1]#remove start and end for lwr	    
	    int_last = len(l_pos) -1 #last count
	    int_mid = int(len(l_pos)/2)#mid count	 
	    d_buildCurves[k]['l_pos'] = l_pos#Store it
	    log.info("%s >>> '%s' pos list: %s"%(_str_funcName,k, l_pos))
	    ml_handles = []
	    for i,pos in enumerate(l_pos):
		try:#Create and name
		    mc.select(cl=True)
		    mi_end = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
		    mi_end.parent = False
		    ml_buffer = [mi_end]
		    mi_end.doCopyNameTagsFromObject( self._i_module.mNode,ignore=['cgmTypeModifier','cgmType','cgmIterator'] )#copy Tags
		    mi_end.addAttr('cgmName',"%s_lid"%(k),lock=True)		    		    
		    mi_end.addAttr('cgmType','handleJoint',lock=True)
		    ml_handles.append(mi_end)
		    log.info("%s >>> curve: %s | pos count: %s | joints: %s"%(_str_funcName,k,i,[o.p_nameShort for o in ml_handles]))
		except StandardError,error:
		    raise StandardError,"curve: %s | pos count: %s | error: %s "%(k,i,error)       
		try:#aim constraint
		    constraintBuffer = mc.aimConstraint(mi_helper.mNode,mi_end.mNode,maintainOffset = False, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
		    mc.delete(constraintBuffer[0])  		
		except StandardError,error:raise StandardError,"curve: %s | pos count: %s | Constraint fail | error: %s "%(k,i,error)
		try:jntUtils.metaFreezeJointOrientation(mi_end)
		except StandardError,error:raise StandardError,"curve: %s | pos count: %s | Freeze orientation fail | error: %s "%(k,i,error)       
	    try:#Naming loop =======================================================================
		#First we need to split our list
		mi_mid = ml_handles[int_mid]
		mi_mid.addAttr('cgmTypeModifier',"main",lock=True)
		mi_mid.doName()
		
		#Split the lists down for inner/outer
		l_buffer = lists.returnSplitList(ml_handles,popMid=True)
		ml_start = l_buffer[0]
		ml_end = l_buffer[-1]
		ml_end.reverse()
		for i,l in enumerate([ml_start,ml_end]):
		    if len(l) > 1:
			b_iterate = True
		    else:b_iterate = False
		    for ii,mObj in enumerate(l):
			if i == 0:mObj.addAttr('cgmDirectionModifier',"inner",lock=True)
			else:mObj.addAttr('cgmDirectionModifier',"outer",lock=True)
			if b_iterate and ii > 0:
			    mObj.addAttr('cgmTypeModifier','sub',lock=True)			    
			    mObj.addAttr('cgmIterator',ii-1,lock=True)
			    mObj.addAttr('isSubControl',True,lock=True)			    
			mObj.doName()
				
	    except StandardError,error:raise StandardError,"Naming fail | error: %s "%(error)       
	    
	    self._i_rigNull.msgList_connect(ml_handles,'handleJoints_%s'%k,'rigNull')
	mi_upLoc.delete()
    except StandardError,error:
	raise StandardError,"%s>>Build handle joints fail! | error: %s"%(_str_funcName,error)   
   
    
    #>>>Create joint chains
    try:#>>Rig chain =====================================================================
	ml_rigJoints = self.build_rigChain()	
    except StandardError,error:
	raise StandardError,"%s>>Build rig joints fail! | error: %s"%(_str_funcName,error)   
    
    try:#>>Root joints =====================================================================
	ml_rootJoints = []
	for mObj in ml_rigJoints:
	    mc.select(cl=True)#clear so joints to parent to one another
	    mi_root = cgmMeta.cgmObject( mc.joint(p = mi_helper.getPosition()),setClass=True )
	    mi_root.doCopyNameTagsFromObject(mObj.mNode)#copy tags
	    mi_root.addAttr('cgmTypeModifier','rigRoot',lock=True)#Tag as root
	    joints.doCopyJointOrient(mObj.mNode,mi_root.mNode)
	    mObj.parent = mi_root
	    mi_root.doName()
	    jntUtils.metaFreezeJointOrientation([mi_root])
	    mObj.connectChildNode(mi_root,'root')#Connect
	    ml_rootJoints.append(mi_root)
	    
    except StandardError,error:
	raise StandardError,"%s>>Build rig joints fail! | error: %s"%(_str_funcName,error)   
    
    try:#>>> Store em all to our instance
	#=====================================================================	
	ml_jointsToConnect = []
	ml_jointsToConnect.extend(ml_rigJoints)    
	ml_jointsToConnect.extend(ml_rootJoints)    	
	for i_jnt in ml_jointsToConnect:
	    i_jnt.overrideEnabled = 1		
	    cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
	    cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    
	    
    except StandardError,error:
	raise StandardError,"%s>> Store joints fail! | error: %s"%(_str_funcName,error)   
    return True
	
#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['eyelidsFK','eyelidsIK']}
@cgmGeneral.Timer
def build_shapes(self):
    """
    """ 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("eyelids.build_rig>>bad self!")
	raise StandardError,error
    
    _str_funcName = "build_shapes(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)   
    
    if self._i_templateNull.handles > 3:
	raise StandardError, "%s >>> Too many handles. don't know how to rig"%(_str_funcName)    
    
    if not self.isRigSkeletonized():
	raise StandardError, "%s.build_shapes>>> Must be rig skeletonized to shape"%(self._strShortName)	
    
    #>>>Build our Shapes
    #=============================================================
    try:
	#Rest of it
	l_toBuild = ['eyelidsIK','eyelidsFK']
	mShapeCast.go(self._i_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
	#self._i_rigNull.connectChildNode(self._md_controlShapes['eyelids'],'shape_eyelids',"rigNull")
	
    except StandardError,error:
	log.error("build_eyelids>>Build shapes fail!")
	raise StandardError,error 
    return True
    
#>>> Controls
#===================================================================
@cgmGeneral.Timer
def build_controls(self):
    """
    """    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("eyelids.build_rig>>bad self!")
	raise StandardError,error
    
    _str_funcName = "build_controls(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75)   
    
    if not self.isShaped():
	raise StandardError,"%s >>> needs shapes to build controls"%_str_funcName
    if not self.isRigSkeletonized():
	raise StandardError,"%s >>> needs shapes to build controls"%_str_funcName

    mi_fkShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_eyelidsFK'),cgmMeta.cgmObject) 
    mi_ikShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_eyelidsIK'),cgmMeta.cgmObject) 
    ml_rigJoints = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('rigJoints'),cgmMeta.cgmObject)
    l_controlsAll = []
    
    try:#Group setup
	#>>>Make a few extra groups for storing controls and what not to in the deform group
	for grp in ['controlsFK','controlsIK']:
	    i_dup = self._i_constrainNull.doDuplicateTransform(True)
	    i_dup.parent = self._i_constrainNull.mNode
	    i_dup.addAttr('cgmTypeModifier',grp,lock=True)
	    i_dup.doName()
	    self._i_constrainNull.connectChildNode(i_dup,grp,'owner')
    except StandardError,error:	
	raise StandardError,"%s >>> Build groups fail! | error: %s"%(_str_funcName,error)
    
    try:#>>>> FK 
	#==================================================================	
	if not mi_fkShape:
	    raise StandardError,"%s >>> Must have at least one fk control"%_str_funcName    
	
	mi_fkShape.parent = self._i_constrainNull.controlsFK.mNode
	i_obj = mi_fkShape
	
	d_buffer = mControlFactory.registerControl(i_obj,copyTransform = ml_rigJoints[0],
                                                   makeAimable=True,typeModifier='fk',) 	    
	i_obj = d_buffer['instance']
	i_obj.axisAim = "%s+"%self._jointOrientation[0]
	i_obj.axisUp= "%s+"%self._jointOrientation[1]	
	i_obj.axisOut= "%s+"%self._jointOrientation[2]
	
	#We're gonna lock the aim rot
	cgmMeta.cgmAttr(i_obj,'r%s'%self._jointOrientation[0], keyable = False, lock=True,hidden=True)
	
	    
	self._i_rigNull.msgList_connect(i_obj,'controlsFK',"rigNull")
	l_controlsAll.extend([i_obj])	
    
    except StandardError,error:	
	raise StandardError,"%s >>> Build fk fail! | error: %s"%(_str_funcName,error)
    
    try:#>>>> IK 
	#==================================================================	
	if not mi_ikShape:
	    raise StandardError,"%s >>> Must have at least one ik control"%_str_funcName    
	
	mi_ikShape.parent = self._i_constrainNull.controlsIK.mNode
	i_obj = mi_ikShape
	
	d_buffer = mControlFactory.registerControl(i_obj,makeAimable=False,typeModifier='ik',
	                                           addDynParentGroup=True) 	    
	i_obj = d_buffer['instance']	
	    
	self._i_rigNull.connectChildNode(i_obj,'controlIK',"rigNull")
	l_controlsAll.extend([i_obj])	
    
    except StandardError,error:	
	raise StandardError,"%s >>> Build ik fail! | error: %s"%(_str_funcName,error)    
   
    try:#>>>> Settings
	#==================================================================	
	mi_settings = self._i_module.getSettingsControl()
	if not mi_settings:raise StandardError,"No settings found"
	self._i_rigNull.connectChildNode(mi_settings,'settings')#No connect back in case we're using another module's
	
	l_controlsAll.append(mi_settings)
    
    except StandardError,error:	
	raise StandardError,"%s >>> Build settings! | error: %s"%(_str_funcName,error)    

    #==================================================================   
    #Connect all controls
    self._i_rigNull.msgList_connect(l_controlsAll,'controlsAll')
    
    return True

@cgmGeneral.Timer
def build_rig(self):
    """
    """    
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("%s.build_rig>>bad self!"%self._strShortName)
	raise StandardError,error
    
    _str_funcName = "build_rig(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75) 
    
    try:#>>>Get data
	_str_orientation = self._jointOrientation or modules.returnSettingsData('jointOrientation')
	mi_moduleParent = False
	if self._i_module.getMessage('moduleParent'):
	    mi_moduleParent = self._i_module.moduleParent
	    
	try:mi_controlIK = cgmMeta.validateObjArg(self._i_rigNull.getMessage('controlIK'),cgmMeta.cgmObject)
	except StandardError,error:raise StandardError,"controlIK fail! | %s"%(error)
	
	try:ml_controlsFK = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('controlsFK'),cgmMeta.cgmObject)	
	except StandardError,error:raise StandardError,"controlFK fail! | %s"%(error)
	
	try:ml_rigJoints = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('rigJoints'),cgmMeta.cgmObject)
	except StandardError,error:raise StandardError,"rigJoints fail! | %s"%(error)
	
	try:mi_helper = cgmMeta.validateObjArg(self._i_module.getMessage('helper'),cgmMeta.cgmObject)
	except StandardError,error:raise StandardError,"helper fail! | %s"%(error)
	
	log.info("ml_controlsFK: %s"%[o.getShortName() for o in ml_controlsFK])	
	log.info("mi_controlIK: %s"%mi_controlIK.p_nameShort)		
	log.info("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
	log.info("mi_helper: %s"%mi_helper)		
		
	v_aim = cgmValid.simpleAxis("%s+"%self._jointOrientation[0]).p_vector
	v_up = cgmValid.simpleAxis("%s+"%self._jointOrientation[1]).p_vector
	#aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	#upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1]) 
	
	#Settings
	mi_settings = self._i_module.getSettingsControl()
	mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',attrType='float',lock=False,keyable=True)
	
    except StandardError,error:
	raise StandardError,"%s >> Gather data fail! | error: %s"%(_str_funcName,error)
    
    #Setup eye rig
    #====================================================================================
    try:#Base eye setup
	d_return = rUtils.createEyeballRig(mi_helper,ballJoint = ml_rigJoints[0],
	                                   ikControl = mi_controlIK,fkControl = ml_controlsFK[0],
	                                   buildIK=True, driverAttr=mPlug_FKIK,
	                                   setupVisBlend = True,
	                                   moduleInstance = self._i_module)
	d_return['mi_rigGroup'].parent = self._i_constrainNull.mNode#parent rig group to constrain null
	mi_fkLoc = d_return['md_locs']['fk']#Grab the fk loc
	self._i_rigNull.connectChildNode(mi_fkLoc,'mi_locFK','rigNull')
	log.info("%s >> fkLoc: %s "%(_str_funcName,mi_fkLoc.p_nameShort)) 
	
	mi_blendLoc = d_return['md_locs']['blend']#Grab the blend loc	
	self._i_rigNull.connectChildNode(mi_blendLoc,'mi_locBlend','rigNull')
	log.info("%s >> blendLoc: %s "%(_str_funcName,mi_blendLoc.p_nameShort)) 
	
    except StandardError,error:
	raise StandardError,"%s >> base rig setup fail! | error: %s"%(_str_funcName,error)   
    
    try:#Connect vis blend between fk/ik
	#>>> Setup a vis blend result
	mPlug_FKon = d_return['mPlug_fkVis']
	mPlug_IKon = d_return['mPlug_ikVis']
	log.info("%s >> mPlug_FKon: %s "%(_str_funcName,mPlug_FKon.p_combinedShortName)) 
	log.info("%s >> mPlug_IKon: %s "%(_str_funcName,mPlug_IKon.p_combinedShortName)) 
	
	mPlug_FKon.doConnectOut("%s.visibility"%self._i_constrainNull.controlsFK.mNode)
	mPlug_IKon.doConnectOut("%s.visibility"%self._i_constrainNull.controlsIK.mNode)
	
    except StandardError,error:
	raise StandardError,"%s >> fk/ik blend setup fail! | error: %s"%(_str_funcName,error)       
    
    #Setup pupil and iris
    #=====================================================================================
    #The gist of what we'll do is setup identical attributes on both fk and ik controls
    #and then blend between the two to drive what is actually influencing the joints
    #scale = (fk_result * fk_pupil) + (ik_result *ik_pupil)
    try:#pupil   mPlug_FKIK
	l_extraSetups = ['pupil','iris']
	for i,n in enumerate(l_extraSetups):
	    if len(ml_rigJoints)> i+1:#We need to set up a pupil
		log.info("%s >> Seting up %s"%(_str_funcName,n)) 
		mi_tmpJoint = ml_rigJoints[i+1]
		mPlug_FK_in = cgmMeta.cgmAttr(ml_controlsFK[0],'%s'%n,attrType='float',initialValue=1,keyable=True, defaultValue=1)
		mPlug_FK_out = cgmMeta.cgmAttr(ml_controlsFK[0],'%s_fkResult'%n,attrType='float',hidden=False,lock=True)	    
		mPlug_IK_in = cgmMeta.cgmAttr(mi_controlIK,'%s'%n,attrType='float',initialValue=1,keyable=True,defaultValue=1)
		mPlug_IK_out = cgmMeta.cgmAttr(mi_controlIK,'%s_ikResult'%n,attrType='float',hidden=False,lock=True)	    
		mPlug_Blend_out = cgmMeta.cgmAttr(mi_tmpJoint,'%s_blendResult'%n,attrType='float',hidden=False,lock=True)	    
		NodeF.argsToNodes("%s = %s * %s"%(mPlug_FK_out.p_combinedShortName,
		                                  mPlug_FKon.p_combinedShortName,
		                                  mPlug_FK_in.p_combinedShortName)).doBuild()
		NodeF.argsToNodes("%s = %s * %s"%(mPlug_IK_out.p_combinedShortName,
		                                  mPlug_IKon.p_combinedShortName,
		                                  mPlug_IK_in.p_combinedShortName)).doBuild()	 
		NodeF.argsToNodes("%s = %s + %s"%(mPlug_Blend_out.p_combinedShortName,
		                                  mPlug_FK_out.p_combinedShortName,
		                                  mPlug_IK_out.p_combinedShortName)).doBuild()	
		for a in self._jointOrientation[1:]:
		    mPlug_Blend_out.doConnectOut("%s.s%s"%(mi_tmpJoint.mNode,a))
	    
    except StandardError,error:
	raise StandardError,"%s >> pupil setup fail! | error: %s"%(_str_funcName,error)   

    #Dynamic parent groups
    #====================================================================================
    try:#>>>> eye
	ml_eyeDynParents = []
	"""
	#Build our dynamic groups
	mi_spine = self._i_module.modulePuppet.getModuleFromDict(moduleType= ['torso','spine'])
	log.info("spine found: %s"%mi_spine)
	if mi_spine:
	    mi_spineRigNull = mi_spine.rigNull
	    ml_eyeDynParents.append( mi_spineRigNull.eyeleIK )	    
	    ml_eyeDynParents.append( mi_spineRigNull.cog )
	    ml_eyeDynParents.append( mi_spineRigNull.hips )	
	
	if mi_moduleParent:
	    mi_parentRigNull = mi_moduleParent.rigNull
	    if mi_parentRigNull.getMessage('skinJoints'):
		ml_eyeDynParents.append( mi_parentRigNull.skinJoints[0])	    
	    
	ml_eyeDynParents.append(self._i_masterControl)
	if mi_controlIK.getMessage('spacePivots'):
	    ml_eyeDynParents.extend(mi_controlIK.msgList_get('spacePivots',asMeta = True))	
	log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._strShortName,[i_obj.getShortName() for i_obj in ml_eyeDynParents]))
	"""
	#Add our parents
	i_dynGroup = mi_controlIK.dynParentGroup
	log.info("Dyn group at setup: %s"%i_dynGroup)
	i_dynGroup.dynMode = 0
	
	for o in ml_eyeDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()
	
    except StandardError,error:
	raise StandardError,"%s >> ik dynamic parent setup fail! | error: %s"%(_str_funcName,error)   

    #Parent and constraining bits
    #====================================================================================
    try:#Constrain to parent module
	ml_rigJoints[0].parent = self._i_constrainNull.mNode
	if mi_moduleParent:
	    mc.parentConstraint(mi_moduleParent.rig_getSkinJoints()[-1].mNode,self._i_constrainNull.mNode,maintainOffset = True)
    except StandardError,error:
	raise StandardError,"%s >> Connect to parent fail! | error: %s"%(_str_funcName,error)

    #Final stuff
    self._set_versionToCurrent()
    return True 
    
@cgmGeneral.Timer
def build_matchSystem(self):
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("eye.build_deformationRig>>bad self!")
	raise StandardError,error
    _str_funcName = "build_rig(%s)"%self._strShortName
    log.info(">>> %s >>> "%(_str_funcName) + "="*75) 
    
    try:#Gather Data
	mi_moduleParent = False
	if self._i_module.getMessage('moduleParent'):
	    mi_moduleParent = self._i_module.moduleParent
	    
	try:mi_controlIK = self._i_rigNull.controlIK
	except StandardError,error:raise StandardError,"controlIK fail! | %s"%(error)
	
	try:ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')   
	except StandardError,error:raise StandardError,"controlFK fail! | %s"%(error)
	
	try:ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
	except StandardError,error:raise StandardError,"rigJoints fail! | %s"%(error)
	
	try:mi_settings = self._i_rigNull.settings
	except StandardError,error:raise StandardError,"settings fail! | %s"%(error)
	
	try:mi_locBlend= self._i_rigNull.mi_locBlend
	except StandardError,error:raise StandardError,"mi_locBlend fail! | %s"%(error)
	
	try:mi_locFK= self._i_rigNull.mi_locFK
	except StandardError,error:raise StandardError,"mi_locFK fail! | %s"%(error)	
	
	ml_fkJoints = self._i_rigNull.msgList_get('fkJoints')
	ml_ikJoints = self._i_rigNull.msgList_get('ikJoints')
	
	try:mi_dynSwitch = self._i_dynSwitch
	except StandardError,error:raise StandardError,"dynSwitch fail! | %s"%(error)
	
    except StandardError,error:
	raise StandardError,"%s >> Gather data fail! | error: %s"%(_str_funcName,error)        
    try:#>>> First IK to FK
	i_ikMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlIK,
	                                       dynPrefix = "FKtoIK",
	                                       dynMatchTargets=mi_locBlend)
    except StandardError,error:
	raise StandardError,"%s >> ik to fk fail! | error: %s"%(_str_funcName,error)       
    try:#>>> FK to IK
	#============================================================================
	i_fkMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[0],
	                                       dynPrefix = "IKtoFK",
	                                       dynMatchTargets=mi_locBlend)
    except StandardError,error:
	raise StandardError,"%s >> fk to ik fail! | error: %s"%(_str_funcName,error)   
        
    #>>> Register the switches
    try:
	mi_dynSwitch.addSwitch('snapToFK',[mi_settings.mNode,'blend_FKIK'],
	                       0,
	                       [i_fkMatch])
    
	mi_dynSwitch.addSwitch('snapToIK',[mi_settings.mNode,'blend_FKIK'],
	                       1,
	                       [i_ikMatch])
    except StandardError,error:
	raise StandardError,"%s >> switch setup fail! | error: %s"%(_str_funcName,error)   
    return True
    
#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'rig','function':build_rig},
                    4:{'name':'match','function':build_matchSystem},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------
