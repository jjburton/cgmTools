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
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.rigger.lib import joint_Utils as jntUtils
from cgm.core.lib import curve_Utils as crvUtils
reload(crvUtils)
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools

from cgm.core.rigger.lib import rig_Utils as rUtils

from cgm.lib import (attributes,
                     deformers,
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
		if k == 'upr':mi_mid.addAttr('isMain',True)#Flag this for later
		
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
			if k == 'lwr':mObj.addAttr('isSubControl',True,lock=True)
			if b_iterate and ii > 0:
			    mObj.addAttr('cgmTypeModifier','sub',lock=True)			    
			    mObj.addAttr('cgmIterator',ii-1,lock=True,hidden = True)
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
__d_controlShapes__ = {'shape':['handleCurves']}
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
    
    if self._i_templateNull.handles != 5:
	raise StandardError, "%s >>> Expecting 5 handles. don't know how to rig"%(_str_funcName)    
    if not self.isRigSkeletonized():
	raise StandardError, "%s.build_shapes>>> Must be rig skeletonized to shape"%(self._strShortName)	
    
    #>>>Build our Shapes
    #=============================================================
    try:
	#Rest of it
	mShapeCast.go(self._i_module,['eyelids'], storageInstance=self)#This will store controls to a dict called    
	
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
    try:#>>> Data gather ================================================================================================
	try:ml_uprLidHandles = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('handleJoints_upr'),noneValid=False)
	except StandardError,error:raise StandardError,"Missing uprlid handleJoints | error: %s "%(error)
	try:ml_lwrLidHandles = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('handleJoints_lwr'),noneValid=False)
	except StandardError,error:raise StandardError,"Missing lwrlid handleJoints | error: %s "%(error)  
	log.info("%s >>> ml_uprLidHandles : %s "%(_str_funcName,[mObj.mNode for mObj in ml_uprLidHandles]))	
	log.info("%s >>> ml_lwrLidHandles : %s"%(_str_funcName,[mObj.mNode for mObj in ml_lwrLidHandles]))		
	#ml_curveHandles = self._i_rigNull.msgList_get('handleCurves')
	#Check our cumulative len
	"""
	if len(ml_curveHandles) != (len(ml_lwrLidHandles) + len(ml_uprLidHandles)):
	    raise StandardError,"len(curveHandles) %s != len of lwr (%s) +  len of upwr (%s)"%(len(ml_curveHandles),
	                                                                                       len(ml_lwrLidHandles),
	                                                                                       len(ml_uprLidHandles))
											   """    
    except StandardError,error:	
	raise StandardError,"%s >>> Data gather fail! | error: %s"%(_str_funcName,error)
    
    try:#>>>> Handles 
	#==================================================================	
	ml_controlsAll = []
	md_controls = {'upr':[],'lwr':[]}	
	md_subControls = {'upr':[],'lwr':[]}
	for i,ml in enumerate([ml_uprLidHandles,ml_lwrLidHandles]):
	    if not i:_str_key = 'upr'
	    else:_str_key = 'lwr'
	    for ii,mi_handle in enumerate(ml):
		try:
		    mi_crv = mi_handle.controlCurve
		    log.debug("On %s | '%s' >> '%s'"%(ii,mi_handle.p_nameShort,mi_crv.p_nameShort))
		    mi_crv.parent = self._i_constrainNull#Parent to constrainNull
		    try:
			if mi_handle.getAttr('isSubControl'):
			    md_subControls[_str_key].append(mi_crv)
			d_buffer = mControlFactory.registerControl(mi_crv,addConstraintGroup=True)
		    except StandardError,error:raise StandardError,"register fail build : %s"%error
		    md_controls[_str_key].append(mi_crv)#append
		    if mi_handle.getAttr('cgmTypeModifier') == 'main':
			self._i_rigNull.connectChildNode(mi_crv,'%sMain'%_str_key)
			#mi_handle.doRemove('isMain')
		    ml_controlsAll.append(mi_crv)
		except StandardError,error:raise StandardError," %s : %s | error: %s"%(ii,mi_handle.p_nameShort,error)
	#Purge our shapes list
	#self._i_rigNull.msgList_purge('handleCurves')
	    
    except StandardError,error:	
	raise StandardError,"%s >>> Build controls fail! | error: %s"%(_str_funcName,error)    
   
    try:#>>>> Parent constrain sub controls 
	#==================================================================	
	log.info(">>> Setting up sub constraints")
	for k in md_subControls.keys():
	    log.debug(">>> md_subControls: %s | '%s'"%(k,[mi_obj.p_nameShort for mi_obj in md_subControls.get(k)]))		
	ml_uprCullList = md_controls['upr']
	try:ml_lwrCullList = [ml_uprCullList[0]] + md_controls['lwr'] + [ml_uprCullList[-1]]
	except StandardError,error:raise StandardError,"lwr cull list build : %s"%error
	md_cullLists = {'upr':ml_uprCullList,'lwr':ml_lwrCullList}
	for k in md_subControls.keys():
	    for i_ctrl in md_subControls[k]:
		log.info(">>> On %s : %s"%(k,i_ctrl.p_nameShort))		
		ml_cull = md_cullLists[k]#get our list
		int_idx = ml_cull.index(i_ctrl)#get our index
		ml_targets = [ml_cull[int_idx-1],ml_cull[int_idx+1]]#get the one before and after
		try:
		    _str_const = mc.parentConstraint([mi_obj.mNode for mi_obj in ml_targets],i_ctrl.getMessage('constraintGroup')[0],maintainOffset = True)[0]
		    l_weightTargets = mc.parentConstraint(_str_const,q=True,weightAliasList = True)
		    for t in l_weightTargets:
			if 'main' not in t:attributes.doSetAttr(_str_const,t,.5)
		except StandardError,error:raise StandardError,"constraint fail | sub: %s | targets: %s"%(i_ctrl.p_nameShort,[mi_obj.p_nameShort for mi_obj in ml_targets],error)
    
    except StandardError,error:	
	raise StandardError,"%s >>> constrain sub fail! | error: %s"%(_str_funcName,error)    
   
   
   
    #==================================================================   
    #Connect all controls
    self._i_rigNull.msgList_connect(ml_controlsAll,'controlsAll','rigNull')
    
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
    
    try:#>>>Get data ==============================================================================================
	_str_orientation = self._jointOrientation or modules.returnSettingsData('jointOrientation')
	v_aim = cgmValid.simpleAxis("%s+"%_str_orientation[0]).p_vector
	v_up = cgmValid.simpleAxis("%s+"%_str_orientation[1]).p_vector
	ml_toVisConnect = []
	
	mi_moduleParent = False
	if self._i_module.getMessage('moduleParent'):
	    mi_moduleParent = self._i_module.moduleParent
	    
	mi_helper = cgmMeta.validateObjArg(self._i_module.getMessage('helper'),noneValid=True)
	if not mi_helper:raise StandardError,"No suitable helper found"    
	mi_settings = self._i_module.getSettingsControl()
	
	try:ml_moduleUprLidJoints = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('moduleJoints_upr'),noneValid=False)
	except StandardError,error:raise StandardError,"Missing uprlid moduleJoints | error: %s "%(error)
	try:ml_moduleLwrLidJoints = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('moduleJoints_lwr'),noneValid=False)
	except StandardError,error:raise StandardError,"Missing lwrlid moduleJoints | error: %s "%(error)  	    
	log.info("%s >>> ml_moduleUprLidJoints : %s "%(_str_funcName,[mObj.p_nameShort for mObj in ml_moduleUprLidJoints]))	
	log.info("%s >>> ml_moduleLwrLidJoints : %s"%(_str_funcName,[mObj.p_nameShort for mObj in ml_moduleLwrLidJoints]))
	
	try:mi_mainUprCtrl = self._i_rigNull.uprMain
	except StandardError,error:raise StandardError,"mi_mainUprCtrl | %s"%(error)	
	
	try:mi_mainLwrCtrl = self._i_rigNull.lwrMain
	except StandardError,error:raise StandardError,"mi_mainLwrCtrl | %s"%(error)	
	
	try:#Need to get our rig joints from the module joints -------------------------------------------
	    ml_rigUprLidJoints = []
	    for i,mi_jnt in enumerate(ml_moduleUprLidJoints):
		try:ml_rigUprLidJoints.append( cgmMeta.validateObjArg(mi_jnt.getMessage('rigJoint'),cgmMeta.cgmObject) )
		except StandardError,error:raise StandardError,"'%s' failed to find rigJoint | error: %s"%(mi_jnt.p_nameShort,error)
	    log.info("%s >>> ml_rigUprLidJoints : %s "%(_str_funcName,[mObj.p_nameShort for mObj in ml_rigUprLidJoints]))	
	    ml_rigLwrLidJoints = []
	    for i,mi_jnt in enumerate(ml_moduleLwrLidJoints):
		try:ml_rigLwrLidJoints.append( cgmMeta.validateObjArg(mi_jnt.getMessage('rigJoint'),cgmMeta.cgmObject) )
		except StandardError,error:raise StandardError,"'%s' failed to find rigJoint | error: %s"%(mi_jnt.p_nameShort,error)
	    log.info("%s >>> ml_rigLwrLidJoints : %s "%(_str_funcName,[mObj.p_nameShort for mObj in ml_rigLwrLidJoints]))	
	except StandardError,error:raise StandardError,"Find rig joint fail | error: %s"%(error)
	try:ml_uprLidHandles = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('handleJoints_upr'),noneValid=False)
	except StandardError,error:raise StandardError,"Missing uprlid handleJoints | error: %s "%(error)
	try:ml_lwrLidHandles = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('handleJoints_lwr'),noneValid=False)
	except StandardError,error:raise StandardError,"Missing lwrlid handleJoints | error: %s "%(error)  
	log.info("%s >>> ml_uprLidHandles : %s "%(_str_funcName,[mObj.p_nameShort for mObj in ml_uprLidHandles]))	
	log.info("%s >>> ml_lwrLidHandles : %s"%(_str_funcName,[mObj.p_nameShort for mObj in ml_lwrLidHandles]))		
	
	try:#Need to get our curves from our handle joints
	    ml_uprLidControls = []
	    for i,mi_jnt in enumerate(ml_uprLidHandles):
		try:ml_uprLidControls.append( cgmMeta.validateObjArg(mi_jnt.getMessage('controlCurve'),cgmMeta.cgmObject) )
		except StandardError,error:raise StandardError,"'%s' failed to find handleJoint | error: %s"%(mi_jnt.p_nameShort,error)
	    log.info("%s >>> ml_uprLidControls : %s "%(_str_funcName,[mObj.p_nameShort for mObj in ml_uprLidControls]))	
	    ml_lwrLidControls = []
	    for i,mi_jnt in enumerate(ml_lwrLidHandles):
		try:ml_lwrLidControls.append( cgmMeta.validateObjArg(mi_jnt.getMessage('controlCurve'),cgmMeta.cgmObject) )
		except StandardError,error:raise StandardError,"'%s' failed to find handleJoint | error: %s"%(mi_jnt.p_nameShort,error)
	    log.info("%s >>> ml_lwrLidControls : %s "%(_str_funcName,[mObj.p_nameShort for mObj in ml_lwrLidControls]))	
	except StandardError,error:raise StandardError,"Find control curve fail | error: %s"%(error)
	
	#Size info
	__baseDistance = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_rigUprLidJoints]) /2 

    except StandardError,error:
	raise StandardError,"%s >> Gather data fail! | error: %s"%(_str_funcName,error)
            
    #>>> Setup Lids
    try:#Build our Curves ===================================================================
	ml_curves = []
	try:#Upr driven curve
	    _str_uprDrivenCurve = mc.curve(d=3,ep=[mi_obj.getPosition() for mi_obj in ml_rigUprLidJoints],os =True)
	    mi_uprDrivenCrv = cgmMeta.cgmObject(_str_uprDrivenCurve,setClass=True)
	    mi_uprDrivenCrv.doCopyNameTagsFromObject(self._i_module.mNode,ignore=['cgmType'])
	    mi_uprDrivenCrv.addAttr('cgmName','uprLid',lock=True)
	    mi_uprDrivenCrv.addAttr('cgmTypeModifier','driven',lock=True)
	    mi_uprDrivenCrv.doName()
	    ml_curves.append(mi_uprDrivenCrv)
	    
	    mi_uprBlinkCrv = mi_uprDrivenCrv.doDuplicate(False)
	    mi_uprBlinkCrv.addAttr('cgmTypeModifier','blink',lock=True)
	    mi_uprBlinkCrv.doName()
	    ml_curves.append(mi_uprBlinkCrv)
	except StandardError,error:raise StandardError,"upper driven curve : %s"%(error)  	    
	
	try:#Upper driver curve
	    _str_uprDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_uprLidHandles],os =True)
	    mi_uprDriverCrv = cgmMeta.cgmObject(_str_uprDriverCurve,setClass=True)
	    mi_uprDriverCrv.doCopyNameTagsFromObject(mi_uprDrivenCrv.mNode,ignore=['cgmTypeModifier'])
	    mi_uprDriverCrv.addAttr('cgmTypeModifier','driver',lock=True)
	    mi_uprDriverCrv.doName()
	    ml_curves.append(mi_uprDriverCrv)	    
	except StandardError,error:raise StandardError,"upper driver curve : %s"%(error)  	    
	
	try:#Lwr driven curve
	    _str_lwrDrivenCurve = mc.curve(d=3,ep=[mi_obj.getPosition() for mi_obj in [ml_rigUprLidJoints[0]] + ml_rigLwrLidJoints + [ml_rigUprLidJoints[-1]]],os =True)
	    mi_lwrDrivenCrv = cgmMeta.cgmObject(_str_lwrDrivenCurve,setClass=True)
	    mi_lwrDrivenCrv.doCopyNameTagsFromObject(mi_uprDrivenCrv.mNode)
	    mi_lwrDrivenCrv.addAttr('cgmName','lwrLid',lock=True)	    
	    mi_lwrDrivenCrv.doName()
	    ml_curves.append(mi_lwrDrivenCrv)	
	    
	    mi_lwrBlinkCrv = mi_lwrDrivenCrv.doDuplicate(False)
	    mi_lwrBlinkCrv.addAttr('cgmTypeModifier','blink',lock=True)
	    mi_lwrBlinkCrv.doName()
	    ml_curves.append(mi_lwrBlinkCrv)
	except StandardError,error:raise StandardError,"upper driven curve : %s"%(error)  	    
	
	try:#Lwr driver curve
	    _str_lwrDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in [ml_uprLidHandles[0]] + ml_lwrLidHandles + [ml_uprLidHandles[-1]]],os =True)
	    mi_lwrDriverCrv = cgmMeta.cgmObject(_str_lwrDriverCurve,setClass=True)
	    mi_lwrDriverCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
	    mi_lwrDriverCrv.addAttr('cgmName','lwrLid',lock=True)	    
	    mi_lwrDriverCrv.doName()
	    ml_curves.append(mi_lwrDriverCrv)	    	    	    
	except StandardError,error:raise StandardError,"upper driver curve : %s"%(error)  	    
	
	try:#SmartBlink curve
	    _str_smartBlinkCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in [ml_uprLidHandles[0]] + ml_lwrLidHandles + [ml_uprLidHandles[-1]]],os =True)
	    mi_smartBlinkCrv = cgmMeta.cgmObject(_str_smartBlinkCurve,setClass=True)
	    mi_smartBlinkCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
	    mi_smartBlinkCrv.addAttr('cgmName','smartBlink',lock=True)	    
	    mi_smartBlinkCrv.doName()
	    ml_curves.append(mi_smartBlinkCrv)	    	    	    
	except StandardError,error:raise StandardError,"smartBlink curve : %s"%(error)  	
	
	for mi_crv in ml_curves:#Parent to rig null
	    mi_crv.parent = self._i_rigNull
	
	ml_toVisConnect.extend(ml_curves)
    except StandardError,error:raise StandardError,"%s >> Curve creation fail! | error: %s"%(_str_funcName,error)   
    
    try:#Locators and aiming ================================================================
	try:#Create up loc -------------------------------------------------------------
	    _str_upLoc = locators.locMeCvFromCvIndex(mi_helper.getShapes()[0],2)  
	    mi_upLoc = cgmMeta.cgmObject(_str_upLoc)
	    mi_locShape = cgmMeta.cgmNode(mi_upLoc.getShapes()[0])
	    mi_locShape.localScaleX = __baseDistance
	    mi_locShape.localScaleY = __baseDistance
	    mi_locShape.localScaleZ = __baseDistance	
	    mi_upLoc.parent = self._i_constrainNull.mNode
	    ml_toVisConnect.append(mi_upLoc)
	except StandardError,error:raise StandardError,"up loc : %s"%(error)  	    
	
	#Make a loc group
	mi_locGroup = cgmMeta.cgmObject(mc.group(em=True))
	mi_locGroup.parent = self._i_constrainNull
	mi_locGroup.addAttr('cgmTypeModifier','locGroup')
	mi_locGroup.doName()
	mi_locGroup.parent = self._i_rigNull
	ml_toVisConnect.append(mi_locGroup)
	
	ml_locs = []
	for i,mi_obj in enumerate(ml_rigUprLidJoints + ml_rigLwrLidJoints):
	    try:
		try:#Loc creation -----------------------------------------------------------
		    mi_loc = mi_obj.doLoc()
		    ml_locs.append(mi_loc)
		    mi_locShape = cgmMeta.cgmNode(mi_loc.getShapes()[0])
		    mi_locShape.localScaleX = __baseDistance
		    mi_locShape.localScaleY = __baseDistance
		    mi_locShape.localScaleZ = __baseDistance
		    mi_loc.parent = mi_locGroup
		except StandardError,error:raise StandardError,"loc creation : %s"%(error)  	    
		#> Aim constraint
		mi_root = mi_obj.root
		mi_root.parent = self._i_constrainNull
		try:mc.aimConstraint(mi_loc.mNode,mi_root.mNode,maintainOffset = False, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
		except StandardError,error:raise StandardError,"aim constraint : %s"%(error)  	    
		#Attach to curve
		if i < len(ml_rigUprLidJoints):mi_crv = mi_uprDrivenCrv
		else:mi_crv = mi_lwrDrivenCrv
		crvUtils.attachObjToCurve(mi_loc.mNode,mi_crv.mNode)
	    except StandardError,error:raise StandardError,"%s | '%s' failed | error: %s "%(i,mi_obj.p_nameShort,error)  	    
	    
    except StandardError,error:
	raise StandardError,"%s >> locator/aim setup fail! | error: %s"%(_str_funcName,error)   
    
    try:#Lid setup ===================================================================
	try:#Wire deformers -------------------------------------------------------------
	    _l_return = mc.wire(mi_uprDrivenCrv.mNode, w = mi_uprDriverCrv.mNode, gw = False, en = 1, ce = 0, li =0)
	    mi_uprWire = cgmMeta.cgmNode(_l_return[0])
	    mi_uprWire.doStore('cgmName',mi_uprDrivenCrv.mNode)
	    mi_uprWire.doName()
	    _l_return = mc.wire(mi_lwrDrivenCrv.mNode, w = mi_lwrDriverCrv.mNode, gw = False, en = 1, ce = 0, li =0)
	    mi_lwrWire = cgmMeta.cgmNode(_l_return[0])
	    mi_lwrWire.doStore('cgmName',mi_lwrDrivenCrv.mNode)
	    mi_lwrWire.doName()

	except StandardError,error:raise StandardError,">> wire deformer : %s"%(error)  	    
	
	try:#Skin driver curve ---------------------------------------------------------
	    ml_uprSkinJoints = ml_uprLidHandles
	    ml_lwrSkinJoints = [ml_uprLidHandles[0]] + ml_lwrLidHandles + [ml_uprLidHandles[-1]]
	    md_skinSetup = {'upr':{'ml_joints':ml_uprSkinJoints,'mi_crv':mi_uprDriverCrv},
	                    'lwr':{'ml_joints':ml_lwrSkinJoints,'mi_crv':mi_lwrDriverCrv}}
	    for k in md_skinSetup.keys():
		d_crv = md_skinSetup[k]
		str_crv = d_crv['mi_crv'].p_nameShort
		l_joints = [mi_obj.p_nameShort for mi_obj in d_crv['ml_joints']]
		log.info(" %s | crv : %s | joints: %s"%(k,str_crv,l_joints))
		try:
		    mi_skinNode = cgmMeta.cgmNode(mc.skinCluster ([mi_obj.mNode for mi_obj in d_crv['ml_joints']],
		                                                  d_crv['mi_crv'].mNode,
		                                                  tsb=True,
		                                                  maximumInfluences = 3,
		                                                  normalizeWeights = 1,dropoffRate=2.5)[0])
		except StandardError,error:raise StandardError,"skinCluster : %s"%(error)  	    
		d_crv['mi_skinNode'] = mi_skinNode
	except StandardError,error:raise StandardError,"skinning driver : %s"%(error)  	    
	
	try:#Blendshape the smart blink curve ---------------------------------------------
	    _str_bsNode = mc.blendShape([mi_uprDriverCrv.mNode,mi_lwrDriverCrv.mNode],mi_smartBlinkCrv.mNode)[0]
	    mi_bsNode = cgmMeta.cgmNode(_str_bsNode,setClass=True)
	    mi_bsNode.doStore('cgmName',mi_smartBlinkCrv.mNode)
	    mi_bsNode.doName()
	    
	    mPlug_height = cgmMeta.cgmAttr(mi_settings,'blinkHeight',attrType = 'float', defaultValue=.1, minValue = 0, maxValue = 1)
	    l_bsAttrs = deformers.returnBlendShapeAttributes(mi_bsNode.mNode)
	    log.info(l_bsAttrs)
	    d_return = NodeF.createSingleBlendNetwork([mi_settings.mNode,'blinkHeight'],
	                                              [mi_settings.mNode,'blinkHeight_upr'],
	                                              [mi_settings.mNode,'blinkHeight_lwr'],
	                                              keyable=True)	
	    #Connect                                  
	    d_return['d_result1']['mi_plug'].doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[0]))
	    d_return['d_result2']['mi_plug'].doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[1]))
	except StandardError,error:raise StandardError,"smartBlink bsNode : %s"%(error)  	
	
	try:#Wire deform the uper and lwr blink lids ---------------------------------------------------------
	    #Build our blink match wire deformers
	    mPlug_height.value = 0	    
	    _l_return = mc.wire(mi_lwrBlinkCrv.mNode, w = mi_smartBlinkCrv.mNode, gw = False, en = 1, ce = 0, li =0)
	    mi_lwrBlinkWire = cgmMeta.cgmNode(_l_return[0])
	    mi_lwrBlinkWire.doStore('cgmName',mi_lwrDrivenCrv.mNode)
	    mi_lwrBlinkWire.addAttr('cgmTypeModifier','blink')	    
	    mi_lwrBlinkWire.doName()
	    mc.setAttr("%s.scale[0]"%mi_lwrBlinkWire.mNode,0)
	    
	    mPlug_height.value = 1
	    _l_return = mc.wire(mi_uprBlinkCrv.mNode, w = mi_smartBlinkCrv.mNode, gw = False, en = 1, ce = 0, li =0)
	    mi_uprBlinkWire = cgmMeta.cgmNode(_l_return[0])
	    mi_uprBlinkWire.doStore('cgmName',mi_uprDrivenCrv.mNode)
	    mi_uprBlinkWire.addAttr('cgmTypeModifier','blink')	    
	    mi_uprBlinkWire.doName()
	    mc.setAttr("%s.scale[0]"%mi_uprBlinkWire.mNode,0)
	    
	    mPlug_height.value = .1#back to default
	except StandardError,error:raise StandardError,"blink target wires : %s"%(error)  	

	try:#Blendshape the upr and lwr curves to smart blink targets------------------------------------
	    mPlug_blink = cgmMeta.cgmAttr(mi_settings,'blink',attrType = 'float', keyable=True, minValue=0, maxValue=1, defaultValue=0)
	    d_blendshapeBlink = {'upr':{'mi_target':mi_uprBlinkCrv,'mi_driven':mi_uprDrivenCrv},
	                         'lwr':{'mi_target':mi_lwrBlinkCrv,'mi_driven':mi_lwrDrivenCrv}}
	    for k in d_blendshapeBlink.keys():
		d_buffer = d_blendshapeBlink[k]
		mi_target = d_buffer['mi_target']
		mi_driven = d_buffer['mi_driven']
		_str_bsNode = mc.blendShape(mi_target.mNode,mi_driven.mNode)[0]
		mi_bsNode = cgmMeta.cgmNode(_str_bsNode,setClass=True)
		mi_bsNode.doStore('cgmName',mi_uprDrivenCrv.mNode)
		mi_bsNode.doName()
		l_bsAttrs = deformers.returnBlendShapeAttributes(mi_bsNode.mNode)
		mPlug_blink.doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[0]))
	except StandardError,error:raise StandardError,"blink setup : %s"%(error)  	

    except StandardError,error:
	raise StandardError,"%s >> Lids setup fail! | error: %s"%(_str_funcName,error)   
    try:#Lid follow ======================================================================
	try:#Initial setup----------------------------------------------------------------
	    mPlug_autoFollow = cgmMeta.cgmAttr(mi_settings,"autoFollow",attrType = 'float', value = 1.0, hidden = False,keyable=True,maxValue=1.0,minValue=0)	    
	    mi_blendLoc = self._mi_moduleParent.rigNull.locBlend
	    
	    mi_zeroLoc = mi_blendLoc.doLoc()
	    mi_zeroLoc.addAttr('cgmName','zero')
	    mi_zeroLoc.doName()
	    	    
	    mi_drivenUprLoc = mi_blendLoc.doLoc()
	    mi_drivenUprLoc.addAttr('cgmName','uprDriven')
	    mi_drivenUprLoc.doName()
	    
	    mi_drivenLwrLoc = mi_blendLoc.doLoc()
	    mi_drivenLwrLoc.addAttr('cgmName','lwrDriven')
	    mi_drivenLwrLoc.doName()	    
	    for mLoc in [mi_zeroLoc,mi_drivenUprLoc,mi_drivenLwrLoc]:
		mLoc.parent = self._i_constrainNull
	    
	    ml_toVisConnect.extend([mi_drivenLwrLoc,mi_drivenUprLoc,mi_zeroLoc])
	    
	    mi_clampUpr = cgmMeta.cgmNode(nodeType='clamp')
	    mi_clampUpr.doStore('cgmName',self._i_module.mNode)
	    mi_clampUpr.addAttr('cgmTypeModifier','upr')
	    mi_clampUpr.doName()
	    
	    mi_clampLwr = cgmMeta.cgmNode(nodeType='clamp')
	    mi_clampLwr.doStore('cgmName',self._i_module.mNode)
	    mi_clampLwr.addAttr('cgmTypeModifier','lwr')	    
	    mi_clampLwr.doName()
	    
	    mi_remapLwr = cgmMeta.cgmNode(nodeType='remapValue')
	    mi_remapLwr.doStore('cgmName',self._i_module.mNode)
	    mi_remapLwr.addAttr('cgmTypeModifier','lwr')	    
	    mi_remapLwr.doName()	    
	except StandardError,error:raise StandardError,"initial setup : %s"%(error) 
	try:#uprLid up -------------------------------------------------------------------
	    mPlug_driverUp = cgmMeta.cgmAttr(mi_blendLoc.mNode,"r%s"%_str_orientation[2])
	    mPlug_uprUpLimit = cgmMeta.cgmAttr(mi_settings,"uprUpLimit",attrType='float',value=-60,keyable=False,hidden=False)
	    mPlug_uprDnLimit = cgmMeta.cgmAttr(mi_settings,"uprDnLimit",attrType='float',value=50,keyable=False,hidden=False)
	    mPlug_driverUp.doConnectOut("%s.inputR"%mi_clampUpr.mNode)
	    mPlug_uprDnLimit.doConnectOut("%s.maxR"%mi_clampUpr.mNode)
	    mPlug_uprUpLimit.doConnectOut("%s.minR"%mi_clampUpr.mNode)
	    mc.connectAttr("%s.outputR"%mi_clampUpr.mNode,"%s.r%s"%(mi_drivenUprLoc.mNode,_str_orientation[2]))
	except StandardError,error:raise StandardError,"uprLid up | %s"%(error) 	
	try:#uprLid out -------------------------------------------------------------------
	    mPlug_driverSide = cgmMeta.cgmAttr(mi_blendLoc.mNode,"r%s"%_str_orientation[1])
	    mPlug_leftLimit = cgmMeta.cgmAttr(mi_settings,"uprLeftLimit",value=20,attrType='float',keyable=False,hidden=False)
	    mPlug_rightLimit = cgmMeta.cgmAttr(mi_settings,"uprRightLimit",value=-20,attrType='float',keyable=False,hidden=False)
	    mPlug_driverSide.doConnectOut("%s.inputG"%mi_clampUpr.mNode)
	    mPlug_leftLimit.doConnectOut("%s.maxG"%mi_clampUpr.mNode)
	    mPlug_rightLimit.doConnectOut("%s.minG"%mi_clampUpr.mNode)
	    mc.connectAttr("%s.outputG"%mi_clampUpr.mNode,"%s.r%s"%(mi_drivenUprLoc.mNode,_str_orientation[1]))
	except StandardError,error:raise StandardError,"uprLid out | %s"%(error) 		
	try:#lwrLid -----------------------------------------------------------------------    
	    mPlug_lwrUpLimit = cgmMeta.cgmAttr(mi_settings,"lwrUpLimit",attrType='float',value=-26,keyable=False,hidden=False)
	    mPlug_lwrDnLimit = cgmMeta.cgmAttr(mi_settings,"lwrDnLimit",attrType='float',value=35,keyable=False,hidden=False)
	    mPlug_lwrDnStart = cgmMeta.cgmAttr(mi_settings,"lwrDnStart",attrType='float',value=5,keyable=False,hidden=False)    
	    mPlug_driverUp.doConnectOut("%s.inputValue"%mi_remapLwr.mNode)
	    mPlug_lwrDnStart.doConnectOut("%s.inputMin"%mi_remapLwr.mNode)
	    
	    mi_remapLwr.inputMax = 50
	    mPlug_lwrDnLimit.doConnectOut("%s.outputLimit"%mi_remapLwr.mNode)
	    mPlug_lwrDnLimit.doConnectOut("%s.inputMax"%mi_remapLwr.mNode)
	    mPlug_lwrDnLimit.doConnectOut("%s.outputMax"%mi_remapLwr.mNode)
	    
	    attributes.doConnectAttr("%s.outValue"%mi_remapLwr.mNode,"%s.inputR"%mi_clampLwr.mNode)
	    
	    mPlug_lwrDnLimit.doConnectOut("%s.maxR"%mi_clampLwr.mNode)
	    mPlug_lwrUpLimit.doConnectOut("%s.minR"%mi_clampLwr.mNode)
	    attributes.doConnectAttr("%s.outputR"%mi_clampLwr.mNode,"%s.r%s"%(mi_drivenLwrLoc.mNode,_str_orientation[2]))
	    attributes.doConnectAttr("%s.outputG"%mi_clampUpr.mNode,"%s.r%s"%(mi_drivenLwrLoc.mNode,_str_orientation[1]))
	    
	except StandardError,error:raise StandardError,"lwr lid | %s"%(error) 		
	try:#Constraint and autolid follow on /off -----------------------------------------------------------
	    _str_constUpr = mc.parentConstraint([mi_zeroLoc.mNode,mi_drivenUprLoc.mNode],mi_mainUprCtrl.constraintGroup.mNode, maintainOffset = True)[0]
	    _str_constLwr = mc.parentConstraint([mi_zeroLoc.mNode,mi_drivenLwrLoc.mNode],mi_mainLwrCtrl.constraintGroup.mNode, maintainOffset = True)[0]
            
            d_autolidBlend = NodeF.createSingleBlendNetwork(mPlug_autoFollow,
	                                                    [mi_settings.mNode,'resultAutoFollowOff'],
	                                                    [mi_settings.mNode,'resultAutoFollowOn'],
	                                                    hidden = True,keyable=False)

            #Connect                                  

	    for sConst in [_str_constLwr,_str_constUpr]:
		l_weightTargets = mc.parentConstraint(sConst,q=True,weightAliasList = True)
		d_autolidBlend['d_result1']['mi_plug'].doConnectOut('%s.%s' % (sConst,l_weightTargets[1]))
		d_autolidBlend['d_result2']['mi_plug'].doConnectOut('%s.%s' % (sConst,l_weightTargets[0]))
	
	    
	    
	except StandardError,error:raise StandardError,"constraints | %s"%(error) 		
	    
    except StandardError,error:
	raise StandardError,"%s >>Lid Follow fail! | error: %s"%(_str_funcName,error)  
    
    try:#Control setup ===================================================================
	for i,mi_handle in enumerate(ml_uprLidHandles + ml_lwrLidHandles):
	    mi_crv = mi_handle.controlCurve
	    log.info("On %s | '%s' >> '%s'"%(i,mi_handle.p_nameShort,mi_crv.p_nameShort))
	    try:mc.parentConstraint([mi_crv.mNode],mi_handle.mNode,maintainOffset = True)
	    except StandardError,error:raise StandardError,"constraint | ctrl: '%s' | target: '%s' | %s"%(mi_crv.p_nameShort,mi_handle.p_nameShort,error)
	self.connect_toRigGutsVis(ml_toVisConnect)#visConnect
    except StandardError,error:
	raise StandardError,"%s >>control setup fail! | error: %s"%(_str_funcName,error)   
    
    self.connect_toRigGutsVis(ml_toVisConnect)
    
    try:#Settings vis sub setup ============================================================
	#Add our attrs
	mPlug_moduleSubDriver = cgmMeta.cgmAttr(mi_settings,'visSub', value = 0, defaultValue = 0, attrType = 'int', minValue=0,maxValue=1,keyable = False,hidden = False)
	mPlug_result_moduleSubDriver = cgmMeta.cgmAttr(mi_settings,'visSub_out', attrType = 'int', minValue=0,maxValue=1,keyable = False,hidden = True,lock=True)
	
	#Get one of the drivers
	if self._i_module.getAttr('cgmDirection') and self._i_module.cgmDirection.lower() in ['left','right']:
	    str_mainSubDriver = "%s.%sSubControls_out"%(self._i_masterControl.controlVis.getShortName(),
                                                        self._i_module.cgmDirection)
	else:
	    str_mainSubDriver = "%s.subControls_out"%(self._i_masterControl.controlVis.getShortName())

	iVis = self._i_masterControl.controlVis
	visArg = [{'result':[mPlug_result_moduleSubDriver.obj.mNode,mPlug_result_moduleSubDriver.attr],
                   'drivers':[[iVis,"subControls_out"],[mi_settings,mPlug_moduleSubDriver.attr]]}]
	NodeF.build_mdNetwork(visArg)	
	
    except StandardError,error:
	raise StandardError,"%s >> vis sub setup! | error: %s"%(_str_funcName,error)    
    
    try:#Parent and constraining bits ============================================================
	for mi_obj in (ml_uprLidHandles + ml_lwrLidHandles):
	    mi_obj.parent = self._i_constrainNull
	    
	for i,mi_obj in enumerate(ml_rigUprLidJoints + ml_rigLwrLidJoints):
	    mi_skinJoint = mi_obj.skinJoint
	    log.info(" '%s' >> '%s'"%(mi_obj.p_nameShort,mi_skinJoint.p_nameShort))
	    mc.pointConstraint(mi_obj.p_nameShort,mi_skinJoint.p_nameShort,maintainOffset = True)
	    mc.orientConstraint(mi_obj.p_nameShort,mi_skinJoint.p_nameShort,maintainOffset = True)
    except StandardError,error:
	raise StandardError,"%s >>constrain skin joints | error: %s"%(_str_funcName,error) 
    
    #sub vis,control groups
    #====================================================================================
    try:#Constrain to parent module
	for mCtrl in (ml_lwrLidControls + ml_uprLidControls):
	    l_attrLockMap = ['scale']
	    mCtrl._setControlGroupLocks(constraintGroup = True)	    
	    if mCtrl.handleJoint.getAttr('isSubControl'):
		mPlug_result_moduleSubDriver.doConnectOut([mCtrl,'v'])
		l_attrLockMap.append('rotate')
	    for a in l_attrLockMap:
		cgmMeta.cgmAttr(mCtrl,a,lock=True,hidden=True,keyable=False)
    except StandardError,error:
	raise StandardError,"%s >>sub vis/lock control groups | error: %s"%(_str_funcName,error)   
    try:#attr hides
	for attr in ['result_ikOn','result_fkOn','blinkHeight_upr','blinkHeight_lwr']:
	    cgmMeta.cgmAttr(mi_settings,attr,hidden=True)
    except StandardError,error:
	raise StandardError,"%s >> attr hides | error: %s"%(_str_funcName,error)  
    
    #Final stuff
    self._set_versionToCurrent()
    return True 
        
#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'rig','function':build_rig},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------
