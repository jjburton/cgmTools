"""
------------------------------------------
cgm.core.rigger: Limb.spine
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

spine rig builder

The basics of a module rig build are as follows:
1) Skeleton build - necessary joints for arig
2) Shapes build - build the control shapes for the rig
3) Deformation build - build the deformation parts of the rig
4) Rig build - finally connects everything
5) doBuild -- the final func to build the module rig

Necessary variables:
1) __version__
2) __d_controlShapes__
3) __l_jointAttrs__
================================================================
"""
__version__ = 01.09142013

# From Python =============================================================
import copy
import re
import time
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

from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF

from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools

from cgm.core.rigger.lib import rig_Utils as rUtils

from cgm.lib import (attributes,
                     joints,
                     skinning,
                     dictionary,
                     distance,
                     modules,
                     search,
                     curves,
                     )

#>>> Skeleton
#===================================================================
__l_jointAttrs__ = ['startAnchor','endAnchor','anchorJoints','rigJoints','influenceJoints','segmentJoints']   

def __bindSkeletonSetup__(self):
    """
    The idea at the end of this is that we have create our skin joints from our module joints
    """
    try:
	if not self._cgmClass == 'JointFactory.go':
	    log.error("Not a JointFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.__bindSkeletonSetup__>>bad self!")
	raise StandardError,error
    
    _str_funcName = "__bindSkeletonSetup__(%s)"%self._strShortName
    log.debug(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()
    
    #>>> Re parent joints
    #=============================================================  
    if not self._mi_module.isSkeletonized():
	raise StandardError, "%s is not skeletonized yet."%self._strShortName
    
    try:#Reparent joints
	ml_moduleJoints = self._mi_module.rigNull.msgList_get('moduleJoints',asMeta = True)  #Get the module joints
	ml_skinJoints = []
	
	for i,i_jnt in enumerate(ml_moduleJoints):
	    ml_skinJoints.append(i_jnt)
	    if i_jnt.hasAttr('cgmName'):
		#ml_handleJoints.append(i_jnt)		
		if i_jnt.cgmName in ['sternum','pelvis']:
		    i_jnt.parent = ml_moduleJoints[0].mNode#Parent sternum to root
		    i_dupJnt = i_jnt.doDuplicate()#Duplicate
		    i_dupJnt.addAttr('cgmNameModifier','extra')#Tag
		    i_jnt.doName()#Rename
		    i_dupJnt.doName()#Rename
		    i_dupJnt.parent = i_jnt#Parent
		    i_dupJnt.connectChildNode(i_jnt,'sourceJoint','scaleJoint')#Connect
		    if i_dupJnt.d_jointFlags.get('isHandle'):
			d_buffer = i_dupJnt.d_jointFlags
			d_buffer.pop('isHandle')
			i_dupJnt.d_jointFlags = d_buffer
		    ml_skinJoints.append(i_dupJnt)#Append
		    log.debug("%s.__bindSkeletonSetup__ >> Created scale joint for '%s' >> '%s'"%(self._strShortName,i_jnt.getShortName(),i_dupJnt.getShortName()))
	
	self._mi_module.rigNull.msgList_connect(ml_skinJoints,'skinJoints')    	
	log.debug("moduleJoints: len - %s | %s"%(len(ml_moduleJoints),[i_jnt.getShortName() for i_jnt in ml_moduleJoints]))	
	log.debug("skinJoints: len - %s | %s"%(len(ml_skinJoints),[i_jnt.getShortName() for i_jnt in ml_skinJoints]))
	log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     	
    except StandardError,error:
	raise StandardError,"%s >>> error : %s"%(_str_funcName,error)


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
    
    _str_funcName = "build_rigSkeleton(%s)"%self._strShortName
    log.debug(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()
    
    #>>>Create joint chains
    #=============================================================    
    try:#>>Segment chain -----------------------------------------------------------
	_str_subFunc = "Segment chain"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc)                		
	
	ml_skinJoints = self._ml_skinJoints
	ml_moduleJoints = self._ml_moduleJoints
	ml_handleJoints = []
	ml_segmentHandleJoints = []
	
	l_segmentJoints = mc.duplicate(self._l_moduleJoints[1:-1],po=True,ic=True,rc=True)
	ml_segmentJoints = []
	for i,j in enumerate(l_segmentJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','segment',attrType='string')
	    i_j.doName()
	    l_segmentJoints[i] = i_j.mNode
	    ml_segmentJoints.append(i_j)
	    if i == 0:
		ml_segmentJoints[0].parent = False#Parent to world
	    else:
		ml_segmentJoints[i].parent = ml_segmentJoints[i-1].mNode#Parent to Last
		
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#>>Rig chain -----------------------------------------------------------
	_str_subFunc = "Rig chain"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc)    	
	ml_rigJoints = self.build_rigChain()
	"""
	l_rigJoints = mc.duplicate(self._l_skinJoints,po=True,ic=True,rc=True)
	ml_rigJoints = []
	for i,j in enumerate(l_rigJoints):
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
	    i_j.doName()
	    l_rigJoints[i] = i_j.mNode
	    ml_rigJoints.append(i_j)
	    if i_j.hasAttr('scaleJoint'):
		if i_j.scaleJoint in self._ml_skinJoints:
		    int_index = self._ml_skinJoints.index(i_j.scaleJoint)
		    i_j.connectChildNode(l_rigJoints[int_index],'scaleJoint','sourceJoint')#Connect
			"""	
	ml_rigJoints[0].parent = self._i_deformNull.mNode#Parent to deformGroup
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    try:#>>Anchor chain -----------------------------------------------------------
	_str_subFunc = "Anchor chain"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc)   	
	ml_anchors = []
	ml_handleJoints = self._get_handleJoints()
	i_rootJnt = cgmMeta.cgmObject(mc.duplicate(ml_handleJoints[0].mNode,po=True,ic=True,rc=True)[0])
	
	i_rootJnt.addAttr('cgmType','anchor',attrType='string',lock=True)
	i_rootJnt.doName()
	i_rootJnt.parent = False	
	ml_anchors.append(i_rootJnt)
	
	#Start
	i_startJnt = cgmMeta.cgmObject(mc.duplicate(ml_handleJoints[1].mNode,po=True,ic=True,rc=True)[0])
	i_startJnt.addAttr('cgmType','anchor',attrType='string',lock=True)
	i_startJnt.doName()
	i_startJnt.parent = False
	ml_anchors.append(i_startJnt)
	
	#End
	l_endJoints = mc.duplicate(ml_handleJoints[-2].mNode,po=True,ic=True,rc=True)
	i_endJnt = cgmMeta.cgmObject(l_endJoints[0])
	for j in l_endJoints:
	    #for i_j in [i_endJnt]:
	    i_j = cgmMeta.cgmObject(j)
	    i_j.addAttr('cgmType','anchor',attrType='string',lock=True)
	    i_j.doName()
	i_endJnt.parent = False
	ml_anchors.append(i_endJnt)
	for i_obj in ml_anchors:
	    i_obj.rotateOrder = 2#<<<<<<<<<<<<<<<<This would have to change for other orientations
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#Influence chain for influencing the surface -----------------------------------------------------------
	_str_subFunc = "Influence chain"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc)   
	
	ml_influenceJoints = []
	for i_jnt in ml_handleJoints[1:-1]:
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
	    
	#>>> Store em all to our instance -----------------------------------------------------------
	self._i_rigNull.connectChildNode(i_startJnt,'startAnchor','rigNull')
	self._i_rigNull.connectChildNode(i_endJnt,'endAnchor','rigNull')
	self._i_rigNull.msgList_connect(ml_anchors,'anchorJoints','rigNull')
	self._i_rigNull.msgList_connect(ml_influenceJoints,'influenceJoints','rigNull')
	self._i_rigNull.msgList_connect(ml_segmentJoints,'segmentJoints','rigNull')
	
	#self._i_rigNull.msgList_connect(ml_anchors,'anchorJoints','rigNull')
	#self._i_rigNull.msgList_connect(ml_rigJoints,'rigJoints','rigNull')
	#self._i_rigNull.msgList_connect(ml_influenceJoints,'influenceJoints','rigNull')
	#self._i_rigNull.msgList_connect(ml_segmentJoints,'segmentJoints','rigNull')
	
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#connections
	_str_subFunc = "Connections"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc)   	
	ml_jointsToConnect = [i_startJnt,i_endJnt]
	ml_jointsToConnect.extend(ml_anchors)
	ml_jointsToConnect.extend(ml_rigJoints)
	ml_jointsToConnect.extend(ml_influenceJoints)
	ml_jointsToConnect.extend(ml_segmentJoints)
    
	for i_jnt in ml_jointsToConnect:
	    i_jnt.overrideEnabled = 1		
	    cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
	    cgmMeta.cgmAttr(self._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    
    
	log.debug("moduleJoints: len - %s | %s"%(len(ml_moduleJoints),[i_jnt.getShortName() for i_jnt in ml_moduleJoints]))	
	log.debug("skinJoints: len - %s | %s"%(len(ml_skinJoints),[i_jnt.getShortName() for i_jnt in ml_skinJoints]))	
	log.debug("handleJoints: len - %s | %s"%(len(ml_handleJoints),[i_jnt.getShortName() for i_jnt in ml_handleJoints]))	
	
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     
    return True

#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['cog','hips','segmentFK','segmentIK','handleIK']}

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
    _str_funcName = "build_shapes(%s)"%self._strShortName
    log.debug(">>> %s "%(_str_funcName) + "="*75) 
    start = time.clock()
    
    try:#>>>Build our Shapes =============================================================
	mShapeCast.go(self._mi_module,['cog','hips','torsoIK','segmentFK'],storageInstance=self)#This will store controls to a dict called    
	log.debug(self._md_controlShapes)
    except StandardError,error:
	raise StandardError,"%s >>> build shapes | error : %s"%(_str_funcName,error) 
    
    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)         
    return True


def build_controls(self):
    """
    """ 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.build_rig>>bad self!")
	raise StandardError,error
    _str_funcName = "build_controls(%s)"%self._strShortName
    log.debug(">>> %s "%(_str_funcName) + "="*75)    
    start = time.clock()
    
    if not self.isShaped():	
	raise StandardError,"%s.build_controls>>> No shapes found connected"%(self._strShortName)
	
    try:#>>> Get some special pivot xforms
	_str_subFunc = "Special Pivot"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc)   	
	ml_segmentJoints = self._i_rigNull.msgList_get('segmentJoints',asMeta=True,cull=True) 
	l_segmentJoints  = [i_jnt.mNode for i_jnt in ml_segmentJoints] 
	tmpCurve = curves.curveFromObjList(l_segmentJoints)
	hipPivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.15))
	shouldersPivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.8))
	log.debug("hipPivotPos : %s"%hipPivotPos)
	log.debug("shouldersPivotPos : %s"%shouldersPivotPos)   
	mc.delete(tmpCurve)
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#>>> Get our shapes
	#__d_controlShapes__ = {'shape':['cog','hips','segmentFK','segmentIK','handleIK']}
	_str_subFunc = "Gather shapes"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc)   
	
	mi_cogShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_cog'),cgmMeta.cgmObject)
	mi_hipsShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_hips'),cgmMeta.cgmObject)
	ml_segmentFKShapes = cgmMeta.validateObjListArg(self._i_rigNull.msgList_get('shape_segmentFK',asMeta = False, cull = True),cgmMeta.cgmObject)
	ml_segmentIKShapes = cgmMeta.validateObjListArg(self._i_rigNull.msgList_get('shape_segmentIK',asMeta = False, cull = True),cgmMeta.cgmObject)
	mi_handleIKShape = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_handleIK'),cgmMeta.cgmObject)
	
	l_controlsAll = []#we'll append to this list and connect them all at the end 
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    #>>>Build our controls
    #=============================================================
    #>>>Set up structure
    try:#>>>> Cog
	_str_subFunc = "Cog"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	i_cog = mi_cogShape
	d_buffer = mControlFactory.registerControl(i_cog.mNode,addExtraGroups = True,addConstraintGroup=True,
	                                           mirrorSide=self._str_mirrorDirection,mirrorAxis="translateX,translateZ,rotateY,rotateZ",
	                                           freezeAll=True,makeAimable=True,autoLockNHide=True,
	                                           controlType='cog')
	i_cog = d_buffer['instance']
	l_controlsAll.append(i_cog)
	self._i_rigNull.connectChildNode(i_cog,'cog','rigNull')#Store
	self._i_rigNull.connectChildNode(i_cog,'settings','rigNull')#Store as settings
	i_cog.masterGroup.parent = self._i_deformNull.mNode
	#Set aims
	
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:
	_str_subFunc = "visSub"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	mPlug_result_moduleSubDriver = self.build_visSub()	
    except StandardError,error:
	raise StandardError,"%s >>> buildVis | %s"%(_str_funcName,error)   
    
    #==================================================================
    try:#>>>> FK Segments
	_str_subFunc = "FK Segments"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	ml_segmentsFK = ml_segmentFKShapes
	for i,i_obj in enumerate(ml_segmentsFK[1:]):#parent
	    i_obj.parent = ml_segmentsFK[i].mNode
	ml_segmentsFK[0].parent = i_cog.mNode
	for i,i_obj in enumerate(ml_segmentsFK):
	    if i == 0:
		#i_loc = ml_segmentsFK[i].doLoc()
		#mc.move (hipPivotPos[0],hipPivotPos[1],hipPivotPos[2], i_loc.mNode)	
		str_pelvis = self._i_rigNull.msgList_getMessage('moduleJoints')[0]
		log.info(str_pelvis)
		d_buffer = mControlFactory.registerControl(i_obj,addConstraintGroup=1,
		                                           mirrorSide=self._str_mirrorDirection,mirrorAxis="translateX,rotateY,rotateZ",
		                                           setRotateOrder=5,
		                                           copyPivot=str_pelvis,typeModifier='fk') 
		#i_loc.delete()
		
	    else:
		d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,setRotateOrder=5,typeModifier='fk',
		                                           mirrorSide=self._str_mirrorDirection,mirrorAxis="translateX,rotateY,rotateZ",) 
	    i_obj = d_buffer['instance']
	    i_obj.drawStyle = 6#Stick joint draw style	    
	self._i_rigNull.msgList_connect(ml_segmentsFK,'controlsFK','rigNull')
	l_controlsAll.extend(ml_segmentsFK)	
    
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
        
    #==================================================================    
    try:#>>>> IK Segments
	_str_subFunc = "IK Segments"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	ml_segmentsIK = ml_segmentIKShapes
	
	for i_obj in ml_segmentsIK:
	    d_buffer = mControlFactory.registerControl(i_obj,addConstraintGroup=1,
	                                               mirrorSide=self._str_mirrorDirection,mirrorAxis="translateX,rotateY,rotateZ",
	                                               typeModifier='segIK',
		                                       setRotateOrder=2) 
	    
	    i_obj = d_buffer['instance']
	    mPlug_result_moduleSubDriver.doConnectOut("%s.visibility"%i_obj.mNode)	    
	    i_obj.masterGroup.parent = self._i_deformNull.mNode
	self._i_rigNull.msgList_connect(ml_segmentsIK,'segmentHandles','rigNull')
	l_controlsAll.extend(ml_segmentsIK)	
	
	
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    #==================================================================
    try:#>>>> IK Handle
	_str_subFunc = "IK Handle"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	i_IKEnd = mi_handleIKShape
	i_IKEnd.parent = i_cog.mNode
	i_loc = i_IKEnd.doLoc()#Make loc for a new transform
	#i_loc.rx = i_loc.rx + 90#offset   
	mc.move (shouldersPivotPos[0],shouldersPivotPos[1],shouldersPivotPos[2], i_loc.mNode)
	
	d_buffer = mControlFactory.registerControl(i_IKEnd,copyTransform = i_loc.mNode,
	                                           mirrorSide=self._str_mirrorDirection,mirrorAxis="translateX,rotateY,rotateZ",
	                                           typeModifier = 'ik',addSpacePivots = 2, addDynParentGroup = True, addConstraintGroup=True,
	                                           makeAimable = True,setRotateOrder=5)
	i_IKEnd = d_buffer['instance']	
		
	i_loc.delete()#delete
	self._i_rigNull.connectChildNode(i_IKEnd,'handleIK','rigNull')#connect
	l_controlsAll.append(i_IKEnd)	

	#Set aims
	i_IKEnd.axisAim = self._jointOrientation[1]+'-'
	i_IKEnd.axisUp = self._jointOrientation[0]+'+'	
	
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
      
    #==================================================================
    try:#>>>> Hips
	_str_subFunc = "Hips"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	i_hips = mi_hipsShape
	i_hips.parent = i_cog.mNode#parent
	i_loc = i_hips.doLoc()
	mc.move (hipPivotPos[0],hipPivotPos[1],hipPivotPos[2], i_loc.mNode)
	
	d_buffer =  mControlFactory.registerControl(i_hips,addSpacePivots = 2, addDynParentGroup = True,
	                                            mirrorSide=self._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",
	                                            addConstraintGroup=True, makeAimable = True,copyPivot=i_loc.mNode,setRotateOrder=5)
	self._i_rigNull.connectChildNode(i_hips,'hips','rigNull')
	i_hips = d_buffer['instance']
	i_loc.delete()
	l_controlsAll.append(i_hips)	
	
	#Set aims
	i_hips.axisAim = self._jointOrientation[1]+'-'
	i_hips.axisUp = self._jointOrientation[0]+'+'	
	
    except StandardError,error:
	raise StandardError,"%s >>> hips | error : %s"%(_str_funcName,error) 
    
    try:#Connect all controls
	_str_subFunc = "Connection"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	for i,mCtrl in enumerate(l_controlsAll):
	    mCtrl.mirrorIndex = i
	    
	self._i_rigNull.msgList_connect(l_controlsAll,'controlsAll')
	self._i_rigNull.moduleSet.extend(l_controlsAll)
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)         
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
    _str_funcName = "build_deformation(%s)"%self._strShortName
    log.debug(">>> %s "%(_str_funcName) + "="*75)       
    start = time.clock()
    
    try:#>>>Get data
	_str_subFunc = "Data"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 
	
	ml_influenceJoints = self._i_rigNull.msgList_get('influenceJoints')
	ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
	ml_segmentJoints = self._i_rigNull.msgList_get('segmentJoints')
	ml_anchorJoints = self._i_rigNull.msgList_get('anchorJoints')
	ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
	ml_segmentHandles = self._i_rigNull.msgList_get('segmentHandles')
	aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
	mi_hips = self._i_rigNull.hips
	mi_handleIK = self._i_rigNull.handleIK
	mi_cog = self._i_rigNull.cog
	
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    #>>>Create a constraint surface for the influence joints
    #====================================================================================    

    #Control Segment
    #====================================================================================
    try:#Control Segment
	_str_subFunc = "Control Segment"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 
	
	log.debug(self._jointOrientation)
	capAim = self._jointOrientation[0].capitalize()
	log.debug("capAim: %s"%capAim)
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
	                                             additiveScaleSetup=True,
	                                             connectAdditiveScale=True,
	                                             moduleInstance=self._mi_module)
	
	i_curve = curveSegmentReturn['mi_segmentCurve']
	self._i_rigNull.msgList_connect([i_curve],'segmentCurves','rigNull')	
	i_curve.segmentGroup.parent = self._i_rigNull.mNode
	"""
	for o in  [ml_influenceJoints[1].mNode,
	           curveSegmentReturn['mi_segmentCurve'].mNode,
	           ml_influenceJoints[0].mNode,
	           ml_influenceJoints[-1].mNode,
	           ml_segmentHandles[1].mNode,
	           self._partName,
	           self._jointOrientation]:
	    log.debug(o)
	return"""
	midReturn = rUtils.addCGMSegmentSubControl(ml_influenceJoints[1].mNode,
	                                           segmentCurve = i_curve,
	                                           baseParent=ml_influenceJoints[0],
	                                           endParent=ml_influenceJoints[-1],
	                                           midControls=ml_segmentHandles[1],
	                                           baseName=self._partName,
	                                           controlTwistAxis =  'r'+self._jointOrientation[0],
	                                           orientation=self._jointOrientation)
	for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
	    i_grp.parent = mi_cog.mNode
	    
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#Setup top twist driver
	_str_subFunc = "Top twist"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	#Create an fk additive attributes
	str_curve = curveSegmentReturn['mi_segmentCurve'].getShortName()
	fk_drivers = ["%s.r%s"%(i_obj.mNode,self._jointOrientation[0]) for i_obj in ml_controlsFK]
	NodeF.createAverageNode(fk_drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"fkTwistSum"],1)#Raw fk twist
	
	try:NodeF.argsToNodes("%s.fkTwistResult = %s.fkTwistSum * %s.fkTwistInfluence"%(str_curve,str_curve,str_curve)).doBuild()
	except StandardError,error:
	    raise StandardError,"verify_moduleRigToggles>> fkwistResult node arg fail: %s"%error	
	
	
	drivers = ["%s.%s"%(curveSegmentReturn['mi_segmentCurve'].mNode,"fkTwistResult")]
	drivers.append("%s.r%s"%(ml_segmentHandles[-1].mNode,self._jointOrientation[0]))
	drivers.append("%s.r%s"%(mi_handleIK.mNode,self._jointOrientation[0]))

	NodeF.createAverageNode(drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistEnd"],1)
	
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#Setup bottom twist driver
	_str_subFunc = "Bottom Twist"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	log.debug("%s.r%s"%(ml_segmentHandles[0].getShortName(),self._jointOrientation[0]))
	log.debug("%s.r%s"%(mi_hips.getShortName(),self._jointOrientation[0]))
	drivers = ["%s.r%s"%(ml_segmentHandles[0].mNode,self._jointOrientation[0])]
	drivers.append("%s.r%s"%(mi_hips.mNode,self._jointOrientation[0]))

	log.debug("driven: %s"%("%s.r%s"%(ml_anchorJoints[1].mNode,self._jointOrientation[0])))
	NodeF.createAverageNode(drivers,
	                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistStart"],1)
    
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#>>>Connect segment scale
	_str_subFunc = "Segment Scale transfer"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	mi_distanceBuffer = i_curve.scaleBuffer	
	cgmMeta.cgmAttr(mi_distanceBuffer,'segmentScale').doTransferTo(mi_cog.mNode)    
	
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    try:#Do a few attribute connections
	#Push squash and stretch multipliers to cog
	_str_subFunc = "Attributes Connection"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	i_buffer = i_curve.scaleBuffer
	
	for k in i_buffer.d_indexToAttr.keys():
	    attrName = 'spine_%s'%k
	    cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_cog.mNode,attrName,connectSourceToTarget = True)
	    cgmMeta.cgmAttr(mi_cog.mNode,attrName,defaultValue = 1)
	    cgmMeta.cgmAttr('cog_anim',attrName, keyable =True, lock = False)    
	
	cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(mi_cog.mNode,connectSourceToTarget=True)
	cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(mi_cog.mNode,connectSourceToTarget=True)
	
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)         
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
    _str_funcName = "build_rig(%s)"%self._strShortName
    log.debug(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()
    
    try:#>>>Get data
	_str_subFunc = "Data"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 
	
	orientation = modules.returnSettingsData('jointOrientation')
	
	mi_segmentCurve = self._i_rigNull.msgList_get('segmentCurves',asMeta = True)[0]
	mi_segmentAnchorStart = mi_segmentCurve.anchorStart
	mi_segmentAnchorEnd = mi_segmentCurve.anchorEnd
	mi_segmentAttachStart = mi_segmentCurve.attachStart
	mi_segmentAttachEnd = mi_segmentCurve.attachEnd 
	mi_distanceBuffer = mi_segmentCurve.scaleBuffer
    
	log.debug("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
	log.debug("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
	log.debug("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
	log.debug("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
	log.debug("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)
	
	ml_influenceJoints = self._i_rigNull.msgList_get('influenceJoints',asMeta = True)
	ml_segmentJoints = mi_segmentCurve.msgList_get('drivenJoints',asMeta = True)
	ml_segmentSplineJoints = mi_segmentCurve.msgList_get('driverJoints',asMeta = True)
	
	ml_anchorJoints = self._i_rigNull.msgList_get('anchorJoints',asMeta = True)
	ml_rigJoints = self._i_rigNull.msgList_get('rigJoints',asMeta = True)
	ml_handleJoints = self._get_handleJoints()
	
	ml_segmentHandles = self._i_rigNull.msgList_get('segmentHandles',asMeta = True)
	aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
	upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
	mi_hips = self._i_rigNull.hips
	mi_handleIK = self._i_rigNull.handleIK
	ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK',asMeta = True)  
	mi_cog = self._i_rigNull.cog
	
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)     

    #Dynamic parent groups
    #====================================================================================
    try:#>>>> Shoulder dynamicParent
	_str_subFunc = "Shoulder dynParent"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	#Build our dynamic groups
	ml_shoulderDynParents = [ml_controlsFK[-1], mi_cog,]
	ml_shoulderDynParents.extend(mi_handleIK.msgList_get('spacePivots',asMeta = True))
	ml_shoulderDynParents.append(self._i_masterControl)
	log.debug(ml_shoulderDynParents)
	log.debug([i_obj.getShortName() for i_obj in ml_shoulderDynParents])
	
	#Add our parents
	i_dynGroup = mi_handleIK.dynParentGroup
	for o in ml_shoulderDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)    

    
    try:#>>>> Hips dynamicParent
	_str_subFunc = "Hips dynParent"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	ml_hipsDynParents = [mi_cog]
	ml_hipsDynParents.extend(mi_hips.msgList_get('spacePivots',asMeta = True))
	ml_hipsDynParents.append(self._i_masterControl)
	log.debug(ml_hipsDynParents)
	log.debug([i_obj.getShortName() for i_obj in ml_hipsDynParents])  
	
	#Add our parents
	i_dynGroup = mi_hips.dynParentGroup
	for o in ml_hipsDynParents:
	    i_dynGroup.addDynParent(o)
	i_dynGroup.rebuild()    
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)     

    
    #FK influence on twist from the space it's in
    try:
	_str_subFunc = "FK space switch"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	str_curve = mi_segmentCurve.getShortName()
	NodeF.argsToNodes("%s.fkTwistInfluence = if %s.space == 0:1 else 0"%(str_curve,mi_handleIK.getShortName())).doBuild()
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)     
    
    try:#Parent and constrain joints
	#====================================================================================
	_str_subFunc = "Parent and constrain"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	ml_segmentJoints[0].parent = mi_cog.mNode#Segment to cog
	ml_segmentSplineJoints[0].parent = mi_cog.mNode#Spline Segment to cog
	
	#Put the start and end controls in the heirarchy
	ml_segmentHandles[0].masterGroup.parent = mi_segmentAttachStart.mNode
	ml_segmentHandles[-1].masterGroup.parent = mi_segmentAttachEnd.mNode
	
	mi_segmentAnchorStart.parent = mi_cog.mNode#Segment anchor start to cog
	mc.parentConstraint(ml_rigJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#constrain
	mc.scaleConstraint(ml_rigJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#Constrain
	
	mi_segmentAnchorEnd.parent = mi_cog.mNode#Anchor end to cog
	mc.parentConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
	mc.scaleConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
	
	#Parent the sternum to the anchor
	ml_handleJoints[-2].parent = ml_anchorJoints[-1].mNode
	#ml_rigJoints[-1].parent = mi_handleIK.mNode
	
	#Parent the influence joints --------------------------------------------------------------
	ml_influenceJoints[0].parent = ml_segmentHandles[0].mNode
	ml_influenceJoints[-1].parent = ml_segmentHandles[-1].mNode
	
	if ml_handleJoints[-2].getMessage('scaleJoint'):#
	    ml_handleJoints[-2].scaleJoint.parent = ml_segmentHandles[-1].mNode
	
	
	#Parent anchors to controls ---------------------------------------------------------------
	ml_anchorJoints[0].parent = mi_hips.mNode#parent pelvis anchor to hips
	ml_anchorJoints[1].parent = mi_hips.mNode
	ml_anchorJoints[-1].parent = mi_handleIK.mNode
		
	#Connect rig pelvis to anchor pelvis ---------------------------------------------------------------
	mc.pointConstraint(ml_anchorJoints[0].mNode,ml_handleJoints[0].mNode,maintainOffset=False)
	mc.orientConstraint(ml_anchorJoints[0].mNode,ml_handleJoints[0].mNode,maintainOffset=False)
	mc.scaleConstraint(ml_anchorJoints[0].mNode,ml_handleJoints[0].mNode,maintainOffset=False)#Maybe hips    
	
	l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
	for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
	    #Don't try scale constraints in here, they're not viable
	    attachJoint = distance.returnClosestObject(i_jnt.mNode,l_rigJoints)
	    log.debug("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
	    pntConstBuffer = mc.pointConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
	    orConstBuffer = mc.orientConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
	    mc.connectAttr((i_jnt.mNode+'.s'),(attachJoint+'.s'))
	    
	mc.pointConstraint(ml_anchorJoints[-1].mNode,ml_handleJoints[-2].mNode,maintainOffset=False)
	mc.orientConstraint(ml_anchorJoints[-1].mNode,ml_handleJoints[-2].mNode,maintainOffset=False)
	mc.connectAttr((ml_anchorJoints[-1].mNode+'.s'),(ml_handleJoints[-2].mNode+'.s'))
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)      
	
    #Set up heirarchy, connect master scale
    #====================================================================================
    try:#>>>Connect master scale
	_str_subFunc = "Master Scale"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(self._i_masterControl.mNode,'scaleY'))    
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)  
    
    #Vis Network, lock and hide
    #====================================================================================   
    try:#Setup Cog vis control for fk controls
	_str_subFunc = "Cog/fk vis"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	cgmMeta.cgmAttr(mi_cog,'visFK', value = 1, defaultValue = 1, attrType = 'int', minValue=0,maxValue=1,keyable = False,hidden = False)
	cgmMeta.cgmAttr( ml_controlsFK[0].mNode,'visibility').doConnectIn('%s.%s'%(mi_cog.mNode,'visFK'))    
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)      

    #Lock and hide hips and shoulders    
    try:#Set up Scale joints
	#====================================================================================     
	#Connect our last segment to the sternum if we have a scale joint
	_str_subFunc = "Scale joints"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	if ml_handleJoints[-2].getMessage('scaleJoint'):
	    i_scaleJoint = ml_handleJoints[-2].scaleJoint
	    mc.connectAttr((ml_segmentHandles[-1].mNode+'.s%s'%self._jointOrientation[1]),(i_scaleJoint.mNode+'.s%s'%self._jointOrientation[1]))    
	    mc.connectAttr((ml_segmentHandles[-1].mNode+'.s%s'%self._jointOrientation[2]),(i_scaleJoint.mNode+'.s%s'%self._jointOrientation[2]))    
	    
	if ml_handleJoints[0].getMessage('scaleJoint'):
	    i_scaleJoint = ml_handleJoints[0].scaleJoint
	    mc.connectAttr((mi_hips.mNode+'.scale'),(i_scaleJoint.mNode+'.scale'))    
	    #Move a couple of joints out and parent constrain them
	    for i_jnt in [ml_anchorJoints[0],ml_anchorJoints[1]]:
		i_jnt.parent = mi_cog.mNode
		mc.parentConstraint(mi_hips.mNode,i_jnt.mNode,maintainOffset=True)	    
	else:
	    attributes.doSetLockHideKeyableAttr(mi_hips.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)     
	
    try:#Set up some defaults
	#====================================================================================
	_str_subFunc = "Attributes Defaults"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
	mPlug_segStart = cgmMeta.cgmAttr(ml_segmentHandles[0],'followRoot')
	mPlug_segStart.p_defaultValue = .5
	mPlug_segStart.value = .5
	mPlug_segMid = cgmMeta.cgmAttr(ml_segmentHandles[1],'linearSplineFollow')
	mPlug_segMid.p_defaultValue = 1
	mPlug_segMid.value = 1
	mPlug_segMidAim = cgmMeta.cgmAttr(ml_segmentHandles[1],'startEndAim')
	mPlug_segMidAim.p_defaultValue = .5
	mPlug_segMidAim.value = .5   
	mPlug_segEnd = cgmMeta.cgmAttr(ml_segmentHandles[-1],'followRoot')
	mPlug_segEnd.p_defaultValue = .5
	mPlug_segEnd.value = .5
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    
    #sub vis,control groups
    #====================================================================================
    try:#Vis/locks
	_str_subFunc = "sub vis/lock control groups"
	time_sub = time.clock() 
	log.debug(">>> %s..."%_str_subFunc) 	
        attributes.doSetLockHideKeyableAttr(mi_handleIK.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
	for mCtrl in (ml_controlsFK + [mi_cog,mi_hips,mi_handleIK] + ml_segmentHandles):
	    mCtrl._setControlGroupLocks()	
	    
	for mCtrl in ml_segmentHandles:
	    cgmMeta.cgmAttr(mCtrl,"s%s"%orientation[0],lock=True,hidden=True,keyable=False)
	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except StandardError,error:
	raise StandardError,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)     
    
    #Final stuff
    self._set_versionToCurrent()
    
    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)         
    return True 

#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'shapes','function':build_shapes},
                    1:{'name':'skeleton','function':build_rigSkeleton},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'deformation','function':build_deformation},
                    4:{'name':'rig','function':build_rig},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------

"""

def __build__(self, buildTo='',*args,**kws): 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise StandardError
    except StandardError,error:
	log.error("spine.build_deformationRig>>bad self!")
	raise StandardError,error
    
    if not self.isShaped():
	build_shapes(self)
    if buildTo.lower() == 'shapes':return True
    if not self.isRigSkeletonized():
	build_rigSkeleton(self)  
    if buildTo.lower() == 'skeleton':return True
    build_controls(self)    
    if buildTo.lower() == 'controls':return True    
    build_deformation(self)
    if buildTo.lower() == 'deformation':return True    
    build_rig(self)    
            
    return True
"""

#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================

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
    ml_influenceJoints = self._i_rigNull.msgList_get('influenceJoints')
    ml_segmentJoints = self._i_rigNull.msgList_get('segmentJoints')
    ml_anchorJoints = self._i_rigNull.msgList_get('anchorJoints')
    ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
    ml_segmentHandles = self._i_rigNull.msgList_get('segmentHandles')
    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    mi_hips = self._i_rigNull.hips
    mi_handleIK = self._i_rigNull.handleIK
    ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
    
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
    i_midFollowGrp = cgmMeta.cgmObject( self._i_rigNull.msgList_get('segmentHandles')[1].doGroup(True),setClass=True)
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
    log.debug("midFollow...")   
    log.debug("rotPlug: %s"%rotPlug)
    log.debug("aimVector: '%s'"%aimVector)
    log.debug("upVector: '%s'"%upVector)    
    log.debug("upLoc: '%s'"%upLoc)
    log.debug("rotDriven: '%s'"%rotDriven)
    
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
    i_pmaAdd = NodeF.createAverageNode([driverNodeAttr,
                                       "%s.r%s"%(self._i_rigNull.msgList_get('segmentHandles')[1].mNode,#mid handle
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
    i_baseFollowGrp = cgmMeta.cgmObject( self._i_rigNull.msgList_get('segmentHandles')[0].doGroup(True),setClass=True)
    i_baseFollowGrp.addAttr('cgmTypeModifier','follow')
    i_baseFollowGrp.doName()
    i_baseFollowGrp.rotateOrder = 0
    
    i_baseFollowPointConstraint = cgmMeta.cgmNode(mc.pointConstraint([ml_anchorJoints[1].mNode],
                                                                     i_baseFollowGrp.mNode,maintainOffset=True)[0])
    
    log.debug("baseFollow...")
    log.debug("aimVector: '%s'"%aimVector)
    log.debug("upVector: '%s'"%upVector)  
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
    mc.parentConstraint(self._i_rigNull.msgList_get('segmentHandles')[0].mNode,
                        ml_influenceJoints[0].mNode,skipRotate = 'z',
                        maintainOffset = True)        
    mc.parentConstraint(self._i_rigNull.msgList_get('segmentHandles')[-1].mNode,
                        ml_influenceJoints[-1].mNode,skipRotate = 'z',
                        maintainOffset = True) 
    mc.parentConstraint(self._i_rigNull.msgList_get('segmentHandles')[1].mNode,
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
	log.debug("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
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
    ml_influenceJoints = self._i_rigNull.msgList_get('influenceJoints')
    ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
    ml_segmentJoints = self._i_rigNull.msgList_get('segmentJoints')
    ml_anchorJoints = self._i_rigNull.msgList_get('anchorJoints')
    ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
    ml_segmentHandles = self._i_rigNull.msgList_get('segmentHandles')
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
	                                                                  moduleInstance=self._mi_module)    
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
	                                                   moduleInstance=self._mi_module)
	#Add squash
	rUtils.addSquashAndStretchToControlSurfaceSetup(surfaceReturn['surfaceScaleBuffer'],[i_jnt.mNode for i_jnt in ml_segmentJoints],moduleInstance=self._mi_module)
	#Twist
	log.debug(self._jointOrientation)
	capAim = self._jointOrientation[0].capitalize()
	log.debug("capAim: %s"%capAim)
	rUtils.addRibbonTwistToControlSurfaceSetup([i_jnt.mNode for i_jnt in ml_segmentJoints],
	                                           [ml_anchorJoints[1].mNode,'rotate%s'%capAim],#Spine1
	                                           [ml_anchorJoints[-1].mNode,'rotate%s'%capAim])#Sternum
	log.debug(surfaceReturn)
    
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
	
	log.debug(i_controlSurfaceCluster.mNode)
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
	    log.debug(d)
	NodeF.createAverageNode(drivers,
	                        [ml_anchorJoints[-1].mNode,"r%s"%self._jointOrientation[0]],1)
	
    except StandardError,error:
	log.error("build_spine>>Top Twist driver fail")
	raise StandardError,error
    
    try:#Setup bottom twist driver
	log.debug("%s.r%s"%(ml_segmentHandles[0].getShortName(),self._jointOrientation[0]))
	log.debug("%s.r%s"%(mi_hips.getShortName(),self._jointOrientation[0]))
	drivers = ["%s.r%s"%(ml_segmentHandles[0].mNode,self._jointOrientation[0])]
	drivers.append("%s.r%s"%(mi_hips.mNode,self._jointOrientation[0]))
	for d in drivers:
	    log.debug(d)
	log.debug("driven: %s"%("%s.r%s"%(ml_anchorJoints[1].mNode,self._jointOrientation[0])))
	NodeF.createAverageNode(drivers,
	                        "%s.r%s"%(ml_anchorJoints[1].mNode,self._jointOrientation[0]),1)
	
    except StandardError,error:
	log.error("build_spine>>Bottom Twist driver fail")
	raise StandardError,error
    

    
    return True
