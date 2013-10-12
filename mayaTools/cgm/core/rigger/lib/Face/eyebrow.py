"""
------------------------------------------
cgm.core.rigger: Face.eyebrow
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

eyebrow rig builder
================================================================
"""
__version__ = 0.10112013

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
from cgm.core.rigger.lib import module_Utils as modUtils

from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.rigger.lib import joint_Utils as jntUtils
reload(jntUtils)
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools
from cgm.core.lib import curve_Utils as crvUtils

from cgm.core.rigger.lib import rig_Utils as rUtils

from cgm.lib import (attributes,
                     joints,
                     skinning,
                     lists,
                     dictionary,
                     distance,
                     modules,
                     search,
                     curves,
                     )

#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['rigJoints','handleJoints']   

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
	log.error("eyebrow.__bindSkeletonSetup__>>bad self!")
	raise StandardError,error
    
    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self.rig_getSkinJoints() or []
    if not self._i_module.isSkeletonized():
	raise StandardError, "%s is not skeletonized yet."%self._strShortName
    try:
	self._i_module.rig_getReport()#report	
    except StandardError,error:
	log.error("build_eyebrow>>__bindSkeletonSetup__ fail!")
	raise StandardError,error   
    
def build_rigSkeleton(goInstance = None):
    class fncWrap(modUtils.rigStep):
	def __init__(self,goInstance = None):
	    super(fncWrap, self).__init__(goInstance)
	    self._str_funcName = 'build_rigSkeleton(%s)'%self.d_kwsDefined['goInstance']._strShortName	
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self.gatherInfo},
	                        {'step':'Rig Joints','call':self.build_rigJoints},
	                        {'step':'Influence Joints','call':self.build_handleJoints},
	                        {'step':'Connections','call':self.build_connections}
	                        ]	
	    #=================================================================
	    if log.getEffectiveLevel() == 10:self.report()#If debug
	
	def gatherInfo(self):
	    mi_go = self._go#Rig Go instance link
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._i_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    
	    self.mi_leftBrowCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('leftBrowHelper'),noneValid=False)
	    self.mi_rightBrowCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('rightBrowHelper'),noneValid=False)
	    
	    if self.mi_helper.buildTemple:
		self.mi_leftTempleCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('leftTempleHelper'),noneValid=False)
		self.mi_rightTempleCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('rightTempleHelper'),noneValid=False)
	    
	    if self.mi_helper.buildUprCheek:
		self.mi_leftUprCheekCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('leftUprCheekHelper'),noneValid=False)
		self.mi_rightUprCheekCrv = cgmMeta.validateObjArg(self.mi_helper.getMessage('rightUprCheekHelper'),noneValid=False)
		
	    #>>> Sorting ==========================================================
	    #We need to sort our joints and figure out what our options are
	    self.md_sortedJoints = {}
	    
	    for mJnt in mi_go._ml_skinJoints:
		str_nameTag = mJnt.getAttr('cgmName')
		str_directionTag = mJnt.getAttr('cgmDirection') 
		#Verify our dict can store
		if str_nameTag not in self.md_sortedJoints.keys():
		    self.md_sortedJoints[str_nameTag] = {}
		if str_directionTag not in self.md_sortedJoints[str_nameTag].keys():
		    self.md_sortedJoints[str_nameTag][str_directionTag] = {'skin':[]}
		    
		#log.info("Checking: '%s' | nameTag: '%s'  | directionTag: '%s' "%(mJnt.p_nameShort,str_nameTag,str_directionTag)) 
		self.md_sortedJoints[str_nameTag][str_directionTag]['skin'].append(mJnt)	
	    	    
	def build_rigJoints(self):
	    #We'll have a rig joint for every joint
	    mi_go = self._go#Rig Go instance link
	    ml_rigJoints = mi_go.build_rigChain()
	    for mJnt in ml_rigJoints:
		mJnt.parent = False
	    """
	    ml_rigJoints = []
	    for i,mJoint in enumerate(mi_go._ml_skinJoints):
		i_j = cgmMeta.cgmObject( mc.duplicate(mJoint.mNode,po=True,ic=True,rc=True)[0],setClass=True )
		i_j.parent = False#Parent to world				
		i_j.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
		i_j.doName()
		ml_rigJoints.append(i_j)
	    mi_go._i_rigNull.msgList_connect(ml_rigJoints,'rigJoints',"rigNull")
	    """
	    self.ml_rigJoints = ml_rigJoints#pass to wrapper
	    
	def build_handleJoints(self):
	    mi_go = self._go#Rig Go instance link	    
	    ml_moduleHandleJoints = []
	    for k_name in self.md_sortedJoints.keys():#For each name...
		for k_direction in self.md_sortedJoints[k_name].keys():#for each direction....
		    if k_name in ['brow','uprCheek']:
			log.info("Building '%s' | '%s' handle joints"%(k_name,k_direction))
			ml_skinJoints = self.md_sortedJoints[k_name][k_direction]['skin']
			ml_handleJoints = []
			self.l_build = []
			#Build our copy list -------------------------------------------
			if k_name == 'brow' and k_direction in ['left','right']:
			    self.l_build = [ml_skinJoints[0],'mid',ml_skinJoints[-1]]
			elif k_name == 'uprCheek' and k_direction in ['left','right']:
			    self.l_build = [ml_skinJoints[0],ml_skinJoints[-1]]
			    
			#Build ----------------------------------------------------------
			for i,mJnt in enumerate(self.l_build):
			    if mJnt == 'mid':
				useCurve = False
				if k_direction == 'left':
				    useCurve = self.mi_leftBrowCrv
				elif k_direction == 'right':
				    useCurve = self.mi_rightBrowCrv
				if not useCurve:
				    raise StandardError,"Step: '%s' '%s' | failed to find use curve"%(k_name,k_direction)
				pos = crvUtils.getMidPoint(useCurve)
				mc.select(cl=True)
				mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
				mi_jnt.parent = False
				mi_jnt.addAttr('cgmName',k_name,lock=True)	
				mi_jnt.addAttr('cgmDirection',k_direction,lock=True)
				mi_jnt.addAttr('cgmNameModifier','mid',attrType='string',lock=True)				    
				mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)				    
				mi_jnt.doName()
				ml_handleJoints.append(mi_jnt)
				
				#Orient
				mc.delete( mc.orientConstraint([ml_skinJoints[0].mNode,ml_skinJoints[-1].mNode],mi_jnt.mNode, maintainOffset = False))
				jntUtils.freezeJointOrientation(mi_jnt)
				
			    else:
				i_j = cgmMeta.cgmObject( mc.duplicate(mJnt.mNode,po=True,ic=True,rc=True)[0],setClass=True )
				i_j.parent = False#Parent to world				
				i_j.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)
				if i == 0:
				    i_j.addAttr('cgmNameModifier','start',attrType='string',lock=True)
				else:
				    i_j.addAttr('cgmNameModifier','end',attrType='string',lock=True)
				
				try:i_j.doRemove('cgmIterator')#Purge the iterator
				except:pass
				
				i_j.doName()
				ml_handleJoints.append(i_j)			
			
			self.md_sortedJoints[k_name][k_direction]['handle'] = ml_handleJoints
			ml_moduleHandleJoints.extend(ml_handleJoints)
	    mi_go._i_rigNull.msgList_connect(ml_moduleHandleJoints,'handleJoints',"rigNull")
	    self.ml_moduleHandleJoints = ml_moduleHandleJoints
		    
	def build_connections(self):    
	    ml_jointsToConnect = []
	    ml_jointsToConnect.extend(self.ml_rigJoints)    
	    ml_jointsToConnect.extend(self.ml_moduleHandleJoints)
	    
	    self._go.connect_toRigGutsVis(ml_jointsToConnect,vis = True)#connect to guts vis switches
	    
	    """
	    for i_jnt in ml_jointsToConnect:
		i_jnt.overrideEnabled = 1		
		cgmMeta.cgmAttr(self._go._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
		cgmMeta.cgmAttr(self._go._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    
		"""
    return fncWrap(goInstance).go()
	
#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['shape_handleCurves','shape_pinCurves']}
def build_shapes(goInstance = None):
    class fncWrap(modUtils.rigStep):
	def __init__(self,goInstance = None):
	    super(fncWrap, self).__init__(goInstance)
	    self._str_funcName = 'build_shapes(%s)'%self.d_kwsDefined['goInstance']._strShortName	
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Build Shapes','call':self.buildShapes},
	                        ]	
	    #=================================================================
	    if log.getEffectiveLevel() == 10:self.report()#If debug
	
	def buildShapes(self):
	    mi_go = self._go#Rig Go instance link
	    mShapeCast.go(mi_go._i_module,['eyebrow'], storageInstance=mi_go)#This will store controls to a dict called    
	    
    return fncWrap(goInstance).go()

#>>> Controls
#===================================================================
def build_controls(goInstance = None):
    class fncWrap(modUtils.rigStep):
	def __init__(self,goInstance = None):
	    super(fncWrap, self).__init__(goInstance)
	    self._str_funcName = 'build_controls(%s)'%self.d_kwsDefined['goInstance']._strShortName	
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	                        ]	
	    #=================================================================
	    if log.getEffectiveLevel() == 10:self.report()#If debug
	
	def _gatherInfo_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._i_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    
	    #>> Find our joint lists ===================================================================
	    ''' We need left and right direction splits for mirror indexing at their color sorting '''
	    self.md_jointLists = {}	    
	    self.ml_handleJoints = mi_go._i_module.rigNull.msgList_get('handleJoints')
	    self.ml_rigJoints = mi_go._i_module.rigNull.msgList_get('rigJoints')
	    
	    l_missingCurves = []
	    for mJnt in self.ml_handleJoints + self.ml_rigJoints:
		if not mJnt.getMessage('controlShape'):l_missingCurves.append(mJnt.p_nameShort)

	    if l_missingCurves:
		log.error("Following joints missing curves: ")
		for obj in l_missingCurves:
		    log.error(">"*5 + " %s"%obj)
		raise StandardError,"Some joints missing controlShape curves"
	
	    #>> Running lists ===========================================================================
	    self.ml_leftControls = []
	    self.ml_rightControls = []
	    self.ml_centerJoints = []
	    
	    """
	    self.ml_browLeftHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                    cgmDirection = 'left',
	                                                                    cgmName = 'brow')
	    self.ml_browRightHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                    cgmDirection = 'right',
	                                                                    cgmName = 'brow')	 
	    self.ml_browCenterHandles = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                      cgmDirection = 'center',
	                                                                      cgmName = 'brow')
	    if not self.ml_browLeftHandles:raise StandardError,"Failed to find left brow handle joints"
	    if not self.ml_browRightHandles:raise StandardError,"Failed to find right brow handle joints"
	    if not self.ml_browCenterHandles:raise StandardError,"Failed to find center brow rig joints"
	    
	    #>> Cheek --------------------------------------------------------------------------
	    self.ml_cheekLeftHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                     cgmDirection = 'left',
	                                                                     cgmName = 'uprCheek')
	    self.ml_cheekRightHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                      cgmDirection = 'right',
	                                                                      cgmName = 'uprCheek')		    
	    
	    #Rig joints... ---------------------------------------------------------------------
	    self.ml_leftRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                  cgmDirection = 'left')
	    self.ml_rightRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                  cgmDirection = 'right')
	    self.ml_centerRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                    cgmDirection = 'center')	
	    self.ml_topRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                 cgmDirection = 'top')	
	    self.ml_backRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                  cgmDirection = 'back')		    
	    if not self.ml_leftRigJoints:raise StandardError,"Failed to find left rig joints"
	    if not self.ml_rightRigJoints:raise StandardError,"Failed to find right rig joints"
	    if not self.ml_centerRigJoints:raise StandardError,"Failed to find center rig joints"	    
	    """
	    self.report()
	    return True
	    	    
	def build_rigJoints(self):
	    #We'll have a rig joint for every joint
	    mi_go = self._go#Rig Go instance link
	    ml_rigJoints = mi_go.build_rigChain()
	    
	def build_controls(self):
	    ml_rigJoints = self.ml_rigJoints
	    ml_handleJoints = self.ml_handleJoints
	    	    
	    
	    ml_fkJoints[0].parent = self._go._i_constrainNull.controlsFK.mNode
		    
	    for i,i_obj in enumerate(ml_controlsFK):
		d_buffer = mControlFactory.registerControl(i_obj,shapeParentTo=ml_fkJoints[i],
		                                           mirrorSide=self._go._str_mirrorDirection, mirrorAxis="",		                                           
		                                           makeAimable=True,typeModifier='fk',) 	    
		
		i_obj = d_buffer['instance']
		i_obj.axisAim = "%s+"%self._go._jointOrientation[0]
		i_obj.axisUp= "%s+"%self._go._jointOrientation[1]	
		i_obj.axisOut= "%s+"%self._go._jointOrientation[2]
		i_obj.drawStyle = 6#Stick joint draw style
		cgmMeta.cgmAttr(i_obj,'radius',hidden=True)
		
	    for i_obj in ml_controlsFK:
		i_obj.delete()
		
	    log.info("%s fk: %s"%(self._str_reportStart,self.ml_fkJoints))
	    self._go._i_rigNull.msgList_connect(ml_fkJoints,'controlsFK',"rigNull")	    
	    self.ml_controlsAll.extend(ml_fkJoints)#append	
	    
    return fncWrap(goInstance).go()
	    

def build_rig(self):
    pass
    
#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'rig','function':build_rig},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------
