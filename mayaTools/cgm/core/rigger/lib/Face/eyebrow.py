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
__version__ = 'faceAlpha2.03292014'

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
from cgm.core.lib import meta_Utils as metaUtils

from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.rigger.lib import joint_Utils as jntUtils
reload(jntUtils)
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
reload(mControlFactory)
from cgm.core.lib import nameTools
from cgm.core.lib import curve_Utils as crvUtils
from cgm.core.lib import rayCaster as rayCast
from cgm.core.lib import surface_Utils as surfUtils
from cgm.core.rigger.lib.Face import faceMod_Utils as faceUtils
reload(faceUtils)
from cgm.core.rigger.lib import rig_Utils as rUtils

from cgm.lib import (attributes,
                     joints,
                     cgmMath,
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
	
    except Exception,error:
	log.error("eyebrow.__bindSkeletonSetup__>>bad self!")
	raise StandardError,error
    
    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self.rig_getSkinJoints() or []
    if not self._mi_module.isSkeletonized():
	raise StandardError, "%s is not skeletonized yet."%self._strShortName
    try:
	self._mi_module.rig_getReport()#report	
    except Exception,error:
	log.error("build_eyebrow>>__bindSkeletonSetup__ fail!")
	raise StandardError,error   
    
def build_rigSkeleton(*args, **kws):
    class fncWrap(modUtils.rigStep):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'build_rigSkeleton(%s)'%self.d_kws['goInstance']._strShortName	
	    self._b_autoProgressBar = True
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self.gatherInfo},
	                        {'step':'Segment Joints','call':self.build_segmentJoints},	                        
	                        {'step':'Rig Joints','call':self.build_rigJoints},
	                        {'step':'Influence Joints','call':self.build_handleJoints},
	                        {'step':'Connections','call':self.build_connections}
	                        ]	
	    #=================================================================
	
	def gatherInfo(self):
	    mi_go = self._go#Rig Go instance link
	    #self.mi_skullPlate = mi_go._mi_skullPlate
	    self.mi_skullPlate = cgmMeta.cgmObject('browPlate')
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
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
		
	    ml_rightRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints , cgmDirection = 'right')
	    for mJoint in ml_rightRigJoints:
		mJoint.__setattr__("r%s"%mi_go._jointOrientation[1],180)
		jntUtils.freezeJointOrientation(mJoint)
	    self.ml_rigJoints = ml_rigJoints#pass to wrapper
	    
	def build_segmentJoints(self):
	    mi_go = self._go#Rig Go instance link	    
	    
	    k_name = 'brow'
	    for k_direction in ['left','right']:
		ml_skinJoints = self.md_sortedJoints[k_name][k_direction]['skin']	
		ml_segJoints = []
		for i,mJnt in enumerate(ml_skinJoints):
		    mNewJnt = cgmMeta.asMeta( mc.duplicate(mJnt.mNode,po=True,ic=True,rc=True)[0],'cgmObject',setClass=True )
		    mNewJnt.parent = False#Parent to world		
		    mNewJnt.cgmName = mNewJnt.cgmName + "Seg"			
		    mNewJnt.addAttr('cgmTypeModifier', 'segJoint',attrType='string',lock=True)
		    mNewJnt.addAttr('cgmDirection', k_direction, attrType='string',lock=True)				    
		    if ml_segJoints:
			mNewJnt.parent = ml_segJoints[-1]
		    try:mNewJnt.doRemove('cgmIterator')#Purge the iterator
		    except:pass
		    mNewJnt.doName()			
		    ml_segJoints.append(mNewJnt)
		    mNewJnt.connectParentNode(mJnt,'sourceJoint','segJoint')
		try:
		    log.info([mJnt.mNode for mJnt in ml_segJoints])
		    log.info(mi_go._jointOrientation)
		    log.info(mi_go._jointOrientation[1])
		    joints.orientJointChain([mJnt.mNode for mJnt in ml_segJoints],mi_go._jointOrientation,"%sup"%mi_go._jointOrientation[1])  
		except Exception,error:raise Exception,"orient fail | error: {0}".format(error)

		try:mi_go._i_rigNull.msgList_connect(ml_segJoints,'{0}{1}'.format('browLineSegment',k_direction.capitalize()),"rigNull")
		except Exception,error:raise Exception,"msgList connect fail| error: {0}".format(error)			
			
	def build_handleJoints(self):
	    mi_go = self._go#Rig Go instance link	    
	    ml_moduleHandleJoints = []
	    ml_influenceJoints = []
	    for k_name in self.md_sortedJoints.keys():#For each name...
		for k_direction in self.md_sortedJoints[k_name].keys():#for each direction....
		    if k_name in ['brow','uprCheek','temple']:
			log.info("Building '{0}' | '{1}' handle joints".format(k_name,k_direction))
			ml_skinJoints = self.md_sortedJoints[k_name][k_direction]['skin']
			ml_handleJoints = []
			self.l_build = []
			#Build our copy list -------------------------------------------
			if k_name == 'brow' and k_direction in ['left','right']:
			    self.l_build = [ml_skinJoints[0],'mid',ml_skinJoints[-1]]
			elif k_name == 'brow' and k_direction in ['center']:
			    self.l_build = [ml_skinJoints[0]]			    
			elif k_name == 'uprCheek' and k_direction in ['left','right']:
			    self.l_build = [ml_skinJoints[0],ml_skinJoints[-1]]
			elif k_name == 'temple' and k_direction in ['left','right']:
			    self.l_build = [ml_skinJoints[0]]
			#Build ----------------------------------------------------------
			int_lenMax = len(self.l_build)			
			for i,mJnt in enumerate(self.l_build):
			    if mJnt == 'mid':_strJoint = 'mid'
			    else:_strJoint = mJnt.p_nameShort
			    
			    self.progressBar_set(status = "Handle Joints: '%s'... "%_strJoint, progress =  i, maxValue = int_lenMax)		    				    		    			    
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
				mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject',setClass=True )
				mi_jnt.parent = False
				mi_jnt.addAttr('cgmName',k_name,lock=True)	
				mi_jnt.addAttr('cgmDirection',k_direction,lock=True)
				mi_jnt.addAttr('cgmNameModifier','mid',attrType='string',lock=True)				    
				mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)				    
				mi_jnt.doName()
				ml_handleJoints.append(mi_jnt)
			    else:
				mi_jnt = cgmMeta.asMeta( mc.duplicate(mJnt.mNode,po=True,ic=True,rc=True)[0],'cgmObject',setClass=True )
				mi_jnt.parent = False#Parent to world				
				mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)
				if len(self.l_build)>1:
				    if i == 0:
					mi_jnt.addAttr('cgmNameModifier','start',attrType='string',lock=True)
				    else:
					mi_jnt.addAttr('cgmNameModifier','end',attrType='string',lock=True)
				    
				try:mi_jnt.doRemove('cgmIterator')#Purge the iterator
				except:pass
				mi_jnt.doName()
				ml_handleJoints.append(mi_jnt)
				
			    if k_name == 'brow':
				try:#influenceJoint -----------------------------------------------------------------------
				    mi_dup = mi_jnt.doDuplicate()
				    mi_dup.addAttr('cgmTypeModifier','infl',attrType='string',lock=True)				    
				    mi_dup.doName()
				    mi_jnt.connectChildNode(mi_dup,'influenceJoint','sourceJoint')
				    ml_influenceJoints.append(mi_dup)
				    mi_dup.parent = mi_go._i_deformNull	
				    #mi_dup.__setattr__("r{0}".format(mi_go._jointOrientation[1]),180)
				    #jntUtils.freezeJointOrientation(mi_dup)				    
				    mi_go.connect_toRigGutsVis(mi_dup,vis = True)#connect to guts vis switches
				except Exception,error:raise StandardError,"[influence joint for '%s']{%s}"%(mJnt.p_nameShort,error)				

			for mJnt in ml_handleJoints + ml_influenceJoints:
			    #Orient
			    v_aimVector = mi_go._vectorAim				
			    v_upVector = mi_go._vectorUp
			    mc.delete( mc.normalConstraint(self.mi_skullPlate.mNode, mJnt.mNode,
			                                   weight = 1, aimVector = v_aimVector, upVector = v_upVector,
			                                   worldUpVector = [0,1,0],worldUpType = 'scene' ))			
			    jntUtils.freezeJointOrientation(mJnt)			    
			
			for mJnt in ml_influenceJoints:
			    try:#Create offsetgroup for the mid
				mi_offsetGroup = cgmMeta.asMeta( mJnt.doGroup(True),'cgmObject',setClass=True)	 
				mi_offsetGroup.doStore('cgmName',mJnt)
				mi_offsetGroup.addAttr('cgmTypeModifier','master',lock=True)
				mi_offsetGroup.doName()
				mJnt.connectChildNode(mi_offsetGroup,'masterGroup','groupChild')
			    except Exception,error:raise Exception,"[masterGroup for '{0}'! | error: {1}]".format(mi_dup.p_nameShort,error)				    
			    
			self.md_sortedJoints[k_name][k_direction]['handle'] = ml_handleJoints
			ml_moduleHandleJoints.extend(ml_handleJoints)
			
			ml_rightHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints , cgmDirection = 'right')
			for mJoint in ml_rightHandles:
			    log.info("{0} flipping".format(mJoint.p_nameShort))
			    mJoint.__setattr__("r{0}".format(mi_go._jointOrientation[1]),180)
			    jntUtils.freezeJointOrientation(mJoint)			
	    mi_go._i_rigNull.msgList_connect(ml_moduleHandleJoints,'handleJoints',"rigNull")
	    self.ml_moduleHandleJoints = ml_moduleHandleJoints
		    
	def build_connections(self):    
	    ml_jointsToConnect = []
	    ml_jointsToConnect.extend(self.ml_rigJoints)    
	    #ml_jointsToConnect.extend(self.ml_moduleHandleJoints)
	    #self._go.connect_toRigGutsVis(ml_jointsToConnect,vis = True)#connect to guts vis switches
	    """
	    for i_jnt in ml_jointsToConnect:
		i_jnt.overrideEnabled = 1		
		cgmMeta.cgmAttr(self._go._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
		cgmMeta.cgmAttr(self._go._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    
		"""
    return fncWrap(*args, **kws).go()
	
#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['shape_handleCurves','shape_pinCurves']}
def build_shapes(*args, **kws):
    class fncWrap(modUtils.rigStep):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'build_shapes({0})'.format(self.d_kws['goInstance']._strShortName)	
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Build Shapes','call':self.buildShapes},
	                        ]	
	    #=================================================================
	
	def buildShapes(self):
	    mi_go = self._go#Rig Go instance link
	    mShapeCast.go(mi_go._mi_module,['eyebrow'], storageInstance=mi_go)#This will store controls to a dict called    
	    
    return fncWrap(*args, **kws).go()

#>>> Controls
#===================================================================
def build_controls(*args, **kws):
    class fncWrap(modUtils.rigStep):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'build_controls({0})'.format(self.d_kws['goInstance']._strShortName)
	    self._b_autoProgressBar = True	    
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	                        {'step':'Settings','call':self._buildSettings_},	                        
	                        {'step':'Direct Controls','call':self._buildControls_},
	                        {'step':'Build Connections','call':self._buildConnections_}	                        
	                        ]	
	    #=================================================================
	
	def _gatherInfo_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    
	    #>> Find our joint lists ===================================================================
	    ''' We need left and right direction splits for mirror indexing at their color sorting '''
	    self.md_jointLists = {}	    
	    self.ml_handleJoints = mi_go._mi_module.rigNull.msgList_get('handleJoints')
	    self.ml_rigJoints = mi_go._mi_module.rigNull.msgList_get('rigJoints')
	    
	    l_missingCurves = []
	    for mJnt in self.ml_handleJoints + self.ml_rigJoints:
		if not mJnt.getMessage('controlShape'):l_missingCurves.append(mJnt.p_nameShort)

	    if l_missingCurves:
		log.error("Following joints missing curves: ")
		for obj in l_missingCurves:
		    log.error(">"*5 + " {0}".format(obj))
		raise StandardError,"Some joints missing controlShape curves"
	    
	    #>> Running lists ===========================================================================
	    self.md_directionControls = {"Left":[],"Right":[],"Centre":[]}
	    self.ml_directControls = []
	    self.ml_controlsAll = []
	    return True
	    	    
	def _buildSettings_(self):
	    mi_go = self._go#Rig Go instance link
	    mi_go.verify_faceSettings()
	    
	    #>>> Verify out vis controls	    
	    self.mPlug_result_moduleFaceSubDriver = mi_go.build_visSubFace()	
	    #self.mPlug_result_moduleFaceSubDriver = self._go.build_visSubFace()	

	def _buildControls_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    ml_rigJoints = self.ml_rigJoints
	    ml_handleJoints = self.ml_handleJoints
		
	    l_strTypeModifiers = ['direct',None]
	    for ii,ml_list in enumerate( [ml_rigJoints,ml_handleJoints] ):
		int_lenMax = len(ml_list)
		for i,mObj in enumerate(ml_list):
		    self.progressBar_set(status = "Control: '%s'... "%mObj.p_nameShort, progress =  i, maxValue = int_lenMax)		    				    		    			    
		    str_mirrorSide = False
		    try:
			mObj.parent = mi_go._i_deformNull
			str_mirrorSide = mi_go.verify_mirrorSideArg(mObj.getAttr('cgmDirection'))#Get the mirror side
			str_cgmDirection = mObj.getAttr('cgmDirection')	
			_addMirrorAttributeBridges = None
			'''
			if str_cgmDirection == 'center':
			    if ii == 0:
				_addMirrorAttributeBridges = None#other center controls	
			    else:
				_addMirrorAttributeBridges = None#other center controls	'''
				
			if ii == 1:
			    _addMirrorAttributeBridges = [["fwdBack","t%s"%mi_go._jointOrientation[0]],
				                          #["mirrorRoll","r%s"%mi_go._jointOrientation[2]],
				                          #["mirrorTwist","r%s"%mi_go._jointOrientation[1]],
			                                  ]
			if str_cgmDirection == 'center' and ii == 0:
			    _addMirrorAttributeBridges = None#other center controls			
			#Register 
			try:
			    d_buffer = mControlFactory.registerControl(mObj, useShape = mObj.getMessage('controlShape'),
			                                               addMirrorAttributeBridges = _addMirrorAttributeBridges,
				                                       mirrorSide = str_mirrorSide, mirrorAxis="translateZ,rotateX,rotateY",		                                           
				                                       makeAimable=False, typeModifier=l_strTypeModifiers[ii]) 	    
			except Exception,error:
			    log.error("mObj: %s"%mObj.p_nameShort)
			    log.error("useShape: %s"%mObj.getMessage('controlShape'))
			    log.error("mirrorSide: %s"%str_mirrorSide)			
			    raise StandardError,"Register fail : %s"%error
			
			#Vis sub connect
			if ii == 0:
			    self.mPlug_result_moduleFaceSubDriver.doConnectOut("%s.visibility"%mObj.mNode)
			
			if str_cgmDirection == 'center' and ii != 0:#Register our settings control to brow center handle
			    mi_go._i_rigNull.connectChildNode(mObj,'browSettings','rigNull')
			    mObj.addAttr('________________',attrType = 'int',keyable = False,hidden = False,lock=True)			    			    
			if ii == 1:
			    l_lock = ['scale','v']
			    if i == 1:l_lock.append('rotate')
			    for a in l_lock:
				cgmMeta.cgmAttr(mObj,a,lock=True,hidden=True,keyable=False)
				
			mc.delete(mObj.getMessage('controlShape'))
			mObj.doRemove('controlShape')
			self.md_directionControls[str_mirrorSide].append(mObj)
			
			#i_obj.drawStyle = 6#Stick joint draw style
			cgmMeta.cgmAttr(mObj,'radius',value=.01, hidden=True)
			self.ml_directControls.append(mObj)
			
		    except Exception, error:
			raise StandardError,"Iterative fail item: %s | obj: %s | mirror side: %s | error: %s"%(i,mObj.p_nameShort,str_mirrorSide,error)
		    
	    self._go._i_rigNull.msgList_connect(self.ml_directControls ,'controlsDirect', 'rigNull')	    
	    self.ml_controlsAll.extend(self.ml_directControls)#append	
	    
	def _buildConnections_(self):
	    #Register our mirror indices ---------------------------------------------------------------------------------------
	    mi_go = self._go#Rig Go instance link	    
	    for str_direction in self.md_directionControls.keys():
		int_start = self._go._i_puppet.get_nextMirrorIndex( self._go._str_mirrorDirection )
		for i,mCtrl in enumerate(self.md_directionControls[str_direction]):
		    try:
			mCtrl.addAttr('mirrorIndex', value = (int_start + i))		
		    except Exception,error: raise StandardError,"Failed to register mirror index | mCtrl: %s | %s"%(mCtrl,error)

	    try:self._go._i_rigNull.msgList_connect(self.ml_controlsAll,'controlsAll')
	    except Exception,error: raise StandardError,"Controls all connect| %s"%error	    
	    try:self._go._i_rigNull.moduleSet.extend(self.ml_controlsAll)
	    except Exception,error: raise StandardError,"Failed to set module objectSet | %s"%error
	    
    return fncWrap(*args, **kws).go()
	    

def build_rig(*args, **kws):
    class fncWrap(modUtils.rigStep):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'build_rig({0})'.format(self.d_kws['goInstance']._strShortName)
	    self._b_autoProgressBar = True	
	    self._b_reportTimes = True
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	                        {'step':'Special Locs','call':self._buildSpecialLocs_},	                        
	                        {'step':'Rig Brows','call':self._buildBrows_},
	                        {'step':'Setup Brow Volume','call':self._buildBrowVolume_},	                        
	                        #{'step':'Rig Upr Cheek','call':self._buildUprCheek_},
	                        {'step':'Rig Temple','call':self._buildTemple_},
	                        {'step':'Attach Squash','call':self._attachSquash_},
	                        {'step':'Lock N hide','call':self._lockNHide_},
	                        ]	
	    #=================================================================
	
	def _gatherInfo_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    	    
            try:#>> Deformation Plates =======================================================================================
                self.mi_skullPlate = mi_go._mi_skullPlate
		mi_go._i_rigNull.connectChildNode(self.mi_skullPlate,'skullPlate')#Connect it
		
                self.str_skullPlate = self.mi_skullPlate.mNode

                #self.mi_jawPlate = cgmMeta.cgmObject('jawPlate')    
                #self.mi_uprTeethPlate = cgmMeta.cgmObject('uprTeethPlate')    
                #self.mi_lwrTeethPlate = cgmMeta.cgmObject('lwrTeethPlate') 
		self.mi_jawPlate = cgmMeta.validateObjArg(self.mi_helper.getMessage('jawPlate'),noneValid=True)		
                self.mi_browPlate = cgmMeta.cgmObject('browPlate')    

            except Exception,error:raise Exception,"[Deformation Plates] | error: {0}".format(error)	    	    
	    
	    
	    #>> Get our lists ==========================================================================
	    '''
	    We need lists of handle and a rig joints for each segment - brow, upr cheek temple
	    md_joints = {'leftBrow:{'ml_handleJoints':[],'ml_rigJoints':[],'mi_crv'}}
	    '''
	    ml_handleJoints = mi_go._mi_module.rigNull.msgList_get('handleJoints')
	    ml_rigJoints = mi_go._mi_module.rigNull.msgList_get('rigJoints')
	    self.md_rigList = {"brow":{"left":{},"right":{},"center":{}},
	                       "uprCheek":{"left":{},"right":{}},
	                       "squash":{},
	                       "temple":{"left":{},"right":{}}}
	    
	    self.ml_rigJoints = ml_rigJoints
	    self.ml_handlesJoints = ml_handleJoints
	    #>> Brow --------------------------------------------------------------------------------------------------
	    self.md_rigList['brow']['left']['ml_handles'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                                          cgmDirection = 'left',
	                                                                                          cgmName = 'brow')
	    self.md_rigList['brow']['right']['ml_handles'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                                           cgmDirection = 'right',
	                                                                                           cgmName = 'brow') 
	    self.md_rigList['brow']['center']['ml_handles'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                                           cgmDirection = 'center',
	                                                                                           cgmName = 'brow') 
	    self.md_rigList['brow']['left']['ml_rigJoints'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                                            cgmDirection = 'left',
	                                                                                            cgmName = 'brow')
	    self.md_rigList['brow']['right']['ml_rigJoints'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                                             cgmDirection = 'right',
	                                                                                             cgmName = 'brow') 
	    self.md_rigList['brow']['center']['ml_rigJoints'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                                              cgmDirection = 'center',
	                                                                                              cgmName = 'brow') 	    
	    if not self.md_rigList['brow']['left'].get('ml_handles'):raise StandardError,"Failed to find left brow handle joints"
	    if not self.md_rigList['brow']['right'].get('ml_handles'):raise StandardError,"Failed to find right brow handle joints"
	    if not self.md_rigList['brow']['center'].get('ml_handles'):raise StandardError,"Failed to find center brow handle joints"
	    
	    #>>Brow push to new format
	    self.md_rigList['browRig'] = {}
	    self.md_rigList['browHandles'] = {}
	    self.md_rigList['browInfluenceJoints'] = {}
	    
	    self.md_rigList['browRig']['left'] = self.md_rigList['brow']['left']['ml_rigJoints']
	    self.md_rigList['browRig']['right'] = self.md_rigList['brow']['right']['ml_rigJoints']
	    self.md_rigList['browRig']['center'] = self.md_rigList['brow']['center']['ml_rigJoints']
	    
	    self.md_rigList['browHandles']['left'] = self.md_rigList['brow']['left']['ml_handles']
	    self.md_rigList['browHandles']['right'] = self.md_rigList['brow']['right']['ml_handles']	    
	    self.md_rigList['browHandles']['center'] = self.md_rigList['brow']['center']['ml_handles']	    
	    
	    self.md_rigList['browSegment'] = {}
	    self.md_rigList['browSegment']['left'] = mi_go._i_rigNull.msgList_get('browLineSegmentLeft')
	    self.md_rigList['browSegment']['right'] = mi_go._i_rigNull.msgList_get('browLineSegmentRight')
	    
	    #Get influenceJoints
	    try:
		self.md_rigList['browInfluenceJoints']['left'] = [mObj.influenceJoint for mObj in self.md_rigList['browHandles']['left']]
		self.md_rigList['browInfluenceJoints']['right'] = [mObj.influenceJoint for mObj in self.md_rigList['browHandles']['right']]
	    except Exception,error:raise Exception,"[Influence Joints fail | error: {0}".format(error)

	    #>> Cheek --------------------------------------------------------------------------------------------------
	    self.md_rigList['uprCheek']['left']['ml_handles'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                                              cgmDirection = 'left',
	                                                                                              cgmName = 'uprCheek')
	    self.md_rigList['uprCheek']['right']['ml_handles'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                                               cgmDirection = 'right',
	                                                                                               cgmName = 'uprCheek') 		    
	    self.md_rigList['uprCheek']['left']['ml_rigJoints'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                                                cgmDirection = 'left',
	                                                                                                cgmName = 'uprCheek')
	    self.md_rigList['uprCheek']['right']['ml_rigJoints'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                                                 cgmDirection = 'right',
	                                                                                                 cgmName = 'uprCheek') 	    
	    #>> Temple --------------------------------------------------------------------------------------------------
	    self.md_rigList['temple']['left']['ml_handles'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                                              cgmDirection = 'left',
	                                                                                              cgmName = 'temple')
	    self.md_rigList['temple']['right']['ml_handles'] = metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
	                                                                                               cgmDirection = 'right',
	                                                                                               cgmName = 'temple') 	
	    
	    self.md_rigList['temple']['left']['ml_rigJoints'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                                                cgmDirection = 'left',
	                                                                                                cgmName = 'temple')
	    self.md_rigList['temple']['right']['ml_rigJoints'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                                                 cgmDirection = 'right',
	                                                                                                 cgmName = 'temple') 	 	    
	    #>> Squash --------------------------------------------------------------------------------------------------
	    self.md_rigList['squash']['ml_rigJoints'] = metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
	                                                                                      cgmNameModifier = 'squash')
	    
	    self.mi_squashCastHelper = cgmMeta.validateObjArg(self.mi_helper.getMessage('squashCastHelper'),noneValid=True)	    

	    #>> Calculate ==========================================================================
	    self.f_offsetOfUpLoc = distance.returnDistanceBetweenObjects(self.md_rigList['brow']['left']['ml_handles'][0].mNode,
	                                                                 self.md_rigList['brow']['left']['ml_handles'][-1].mNode)
	    
	    #>> Running lists ==========================================================================
	    self.ml_toVisConnect = []
	    self.ml_curves = []
	    self.md_attachReturns = {}
	    return True
	
	def _buildSpecialLocs_(self):
	    #>> Need to build some up locs =======================================================================================
	    mi_go = self._go#Rig Go instance link
	    """
	    str_cast = mi_go._jointOrientation[1]+"+"
	    d_return = rayCast.findMeshIntersectionFromObjectAxis(self.mi_skullPlate.mNode,self.mi_squashCastHelper.mNode,str_cast)
	    log.info(d_return)
	    pos = d_return.get('hit')
	    if not pos:
		log.warning("rayCast.findMeshIntersectionFromObjectAxis(%s,%s,%s)"%(self.l_targetMesh[0],self.mi_squashCastHelper.mNode,str_cast))
		raise StandardError, "Failed to find hit." 
		"""
	    try:#Brow up loc
		str_skullPlate = self.str_skullPlate
		d_section = self.md_rigList['brow']		
		#Some measurements
		#From the outer brow to outer brow
		f_distBrowToBrow = distance.returnDistanceBetweenObjects(d_section['left']['ml_rigJoints'][-1].mNode,
		                                                         d_section['right']['ml_rigJoints'][-1].mNode)		
		mi_browUpLoc = self.mi_helper.doLoc()
		#mi_browUpLoc.parent = False
		str_grp = mi_browUpLoc.doGroup()
		mi_browUpLoc.__setattr__("t%s"%mi_go._jointOrientation[0],-f_distBrowToBrow/2)
		mi_browUpLoc.__setattr__("t%s"%mi_go._jointOrientation[1],f_distBrowToBrow/2)
		mi_browUpLoc.addAttr('cgmTypeModifier','moduleUp',lock = True)
		mi_browUpLoc.doName()
		
		#mi_browUpLoc.parent = mi_go._i_rigNull#parent to rigNull
		self.mi_browUpLoc = mi_browUpLoc #Link
		try:
		    d_return = surfUtils.attachObjToSurface(objToAttach = mi_browUpLoc.mNode,
			                                    targetSurface = str_skullPlate,
			                                    createControlLoc = False,
			                                    createUpLoc = False,	
		                                            parentToFollowGroup = True,		                                            
			                                    orientation = mi_go._jointOrientation)
		except Exception,error:raise StandardError,"Failed to attach. | error : %s"%(error)
		self.md_attachReturns[mi_browUpLoc] = d_return		
		mc.delete(str_grp)
		mi_go.connect_toRigGutsVis(mi_browUpLoc,vis = True)#connect to guts vis switches
		
	    except Exception,error:raise StandardError,"Brow up setup. | error : %s"%(error)
	    
	def _buildBrows_(self):
            try:#Query ====================================================================================		
		mi_go = self._go#Rig Go instance link
                try:#>> plate queries ---------------------------------------------------------------
		    str_skullPlate = self.str_skullPlate		    
                    mi_browPlate = self.mi_browPlate
                except Exception,error:raise Exception,"[Plate query | error: {0}]".format(error)
		f_offsetOfUpLoc = self.f_offsetOfUpLoc
		
		str_centerBrowRigJoint = self.md_rigList['brow']['center']['ml_rigJoints'][0].mNode
		if not str_centerBrowRigJoint:raise StandardError,"Missing center brow rig joint"
		
            except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)	    

            try:#Attach stuff to surfaces ====================================================================================		
                #'browHandles':{'mode':'handleAttach','attachTo':mi_browPlate}
                d_build = {'browHandles':{'mode':'handleAttach','attachTo':mi_browPlate},
		           'browRig':{'mode':'slideAttach','attachTo':mi_browPlate,'skip':['left','right']},
		           'browInfluenceJoints':{'mode':'slideAttach','attachTo':mi_browPlate},#...rig attach so that we can drive it's position via the left lip corner
                           }
                faceUtils.attach_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error)

            try:#>>> Connect rig joints to handles ==================================================================
                d_build = {'browInfluenceJoints':{'mode':'toConnectedMsg','messageTag':'sourceJoint'},
		           'browRig':{'skip':['center'],'mode':'rigToSegment'},           
                           }
                faceUtils.connect_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Connect! | error: {0}]".format(error) 	    
	    
	
            try:#Setup segments ========================================================================
                d_build = {'browSegment':{'orientation':mi_go._jointOrientation,
		                          'left':{'mi_curve':None},
		                          'right':{'mi_curve':None}}}	
                faceUtils.create_segmentfromDict(self,d_build)
            except Exception,error:raise Exception,"[Segments | error: {0}]".format(error)  
	    
            try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
                d_build = {'browLeft':{'target':self.md_rigList['browSegment']['leftSegmentCurve'],
		                       'bindJoints':self.md_rigList['browInfluenceJoints']['left']},
                           'browRight':{'target':self.md_rigList['browSegment']['rightSegmentCurve'],
                                        'bindJoints':self.md_rigList['browInfluenceJoints']['right']}}
                faceUtils.skin_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Skinning! | error: {0}".format(error)	
	    
	    try:#>>> Aim  =================================================================================
		str_centerBrowRigJoint = self.md_rigList['browRig']['center'][0].p_nameShort
		
		
		for i,str_side in enumerate(['left','right']):
		    try:
			ml_rigJoints = self.md_rigList['browRig'][str_side]
			int_lenMax = len(ml_rigJoints)
			int_lastIndex = int_lenMax - 1	
			
			str_side = ml_rigJoints[0].cgmDirection
			v_up = mi_go._vectorAim
			if str_side == 'left':
			    v_aim = mi_go._vectorOut
			else:
			    v_aim = mi_go._vectorOutNegative			
		    except Exception,error:raise StandardError,"[side query | {0}]".format(error) 

		    for obj_idx,mObj in enumerate( ml_rigJoints ):
			#d_current = self.md_attachReturns[mObj]
			#self.progressBar_set(status = "Connecting: '%s'... "%mObj.p_nameShort, progress = obj_idx, maxValue = int_lenMax)		    				    		    						
			try:
			    try:
				#mi_upLoc = mObj.segJoint.upLoc
				#str_upLoc = mi_upLoc.p_nameShort
				mi_offsetGroup = mi_go.verify_offsetGroup(mObj)
				str_offsetGroup = mi_offsetGroup.p_nameShort
				mi_masterGroup = mObj.masterGroup
			    except Exception,error:raise StandardError,"[mObj query | {0}]".format(error) 
			    
			    try:
				mi_trackLoc = mObj.doLoc()
				mi_trackLoc.addAttr('cgmTypeModifier','surfTrack')
				mi_trackLoc.doName()
				mi_trackLoc.parent = mi_go._i_rigNull
				
				d_return = surfUtils.attachObjToSurface(objToAttach = mi_trackLoc,
				                                        targetSurface = mi_browPlate,
				                                        createControlLoc = True,
				                                        createUpLoc = True,	
				                                        attachControlLoc = False,
				                                        f_offset = self.f_offsetOfUpLoc,					                                        
				                                        parentToFollowGroup = False,
				                                        orientation = mi_go._jointOrientation)
				
				d_return['controlLoc'].parent = mObj.segJoint
				mi_upLoc = d_return['upLoc']
				str_upLoc = mi_upLoc.p_nameShort
				
				self.md_attachReturns[mi_trackLoc] = d_return												
			    except Exception,error:raise StandardError,"[upLoc | {0}]".format(error) 
			    
			    try:#>> Aim the offset group  ------------------------------------------------------------------------------------------
				if obj_idx == 0:
				    #If it's the interior brow, we need to aim forward and back on the chain
				    d_tomake = {'aimIn':{'target':str_centerBrowRigJoint,
				                         'aimVector':[v *-1 for v in v_aim]},
				                'aimOut':{'target':ml_rigJoints[1].mNode,
				                          'aimVector':v_aim}}
				    for d in d_tomake.keys():
					d_sub = d_tomake[d]
					str_target = d_sub['target']
					mi_loc = mObj.doLoc()
					mi_loc.addAttr('cgmTypeModifier',d,lock=True)
					mi_loc.doName()
					mi_loc.parent = mi_masterGroup
					d_sub['aimLoc'] = mi_loc
					v_aimVector = d_sub['aimVector']
					mi_go.connect_toRigGutsVis(mi_loc,vis = True)#connect to guts vis switches					
					if str_side == 'right':
					    v_aimVector = [v *-1 for v in v_aimVector]

					if d == 'aimIn':
					    mc.aimConstraint(str_target,mi_loc.mNode,
						             maintainOffset = True,skip = [mi_go._jointOrientation[1],mi_go._jointOrientation[2]],
						             weight = 1,
						             aimVector = v_aimVector, upVector = v_up,
						             worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )
					else:
					    mc.aimConstraint(str_target,mi_loc.mNode,
						             maintainOffset = True,
						             weight = 1,
						             aimVector = v_aimVector, upVector = v_up,
						             worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )					    
				    mc.orientConstraint([d_tomake['aimIn']['aimLoc'].mNode, d_tomake['aimOut']['aimLoc'].mNode],str_offsetGroup,maintainOffset = True)					
				elif obj_idx == int_lastIndex:
				    ml_targets = [ml_rigJoints[-2]]
				    mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup,
				                     maintainOffset = True, weight = 1, aimVector = cgmMath.multiplyLists([v_aim,[-1,-1,-1]]), upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
				    
				else:
				    #skip = [mi_go._jointOrientation[1],mi_go._jointOrientation[2]]
				    #ml_targets = [ml_rigJoints[obj_idx-1].masterGroup]
				    #mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup,
				    #                 maintainOffset = True, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
				    d_tomake = {'aimIn':{'target':ml_rigJoints[obj_idx-1].masterGroup,
				                         'aimVector':[v *-1 for v in v_aim]},
				                'aimOut':{'target':ml_rigJoints[obj_idx+1].masterGroup,
				                          'aimVector':v_aim}}
				    for d in d_tomake.keys():
					d_sub = d_tomake[d]
					mi_loc = mObj.doLoc()
					mi_loc.addAttr('cgmTypeModifier',d,lock=True)
					mi_loc.doName()
					mi_loc.parent = mi_masterGroup
					d_sub['aimLoc'] = mi_loc
					v_aimVector = d_sub['aimVector']
					mi_go.connect_toRigGutsVis(mi_loc,vis = True)#connect to guts vis switches										
					if str_side == 'right':
					    v_aimVector = [v *-1 for v in v_aimVector]
					mc.aimConstraint( d_sub['target'].mNode,mi_loc.mNode,
                                                         maintainOffset = True,
                                                         weight = 1,
                                                         aimVector = v_aimVector, upVector = v_up,
                                                         worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
				    mc.orientConstraint([d_tomake['aimIn']['aimLoc'].mNode, d_tomake['aimOut']['aimLoc'].mNode],str_offsetGroup,maintainOffset = True)					
			    
			    except Exception,error:raise StandardError,"Loc setup. | error : %s"%(error)
	
			except Exception,error:
			    raise StandardError,"Rig joint setup fail. obj: {0} | error : {1}".format(mObj.p_nameShort,error)	    
	    except Exception,error:raise Exception,"[Aim! | error: {0}]".format(error)	    
    
	    '''
	    #>> Left and Right =======================================================================================
	    for i,d_browSide in enumerate([self.md_rigList['brow']['left'],self.md_rigList['brow']['right']] ):
		ml_handles = d_browSide['ml_handles']
		ml_rigJoints = d_browSide['ml_rigJoints']

		if len(ml_handles) != 3:
		    raise StandardError,"Only know how to rig a 3 handle brow segment. step: %s"%(i) 	
		
		str_side = ml_rigJoints[0].cgmDirection
		v_up = mi_go._vectorAim
		if str_side == 'left':
		    v_aim = mi_go._vectorOut
		else:
		    v_aim = mi_go._vectorOutNegative
		    
		try:#Create our curves ------------------------------------------------------------------------------------
		    str_crv = mc.curve(d=1,ep=[mObj.getPosition() for mObj in ml_rigJoints],os =True)
		    mi_crv = cgmMeta.cgmObject(str_crv,setClass=True)
		    mi_crv.doCopyNameTagsFromObject(ml_rigJoints[0].mNode,ignore=['cgmIterator','cgmTypeModifier','cgmType'])
		    mi_crv.addAttr('cgmTypeModifier','driver',lock=True)
		    mi_crv.doName()
		    mi_crv.parent = mi_go._i_rigNull#parent to rigNull
		    self.ml_toVisConnect.append(mi_crv)	
		    d_browSide['mi_crv'] = mi_crv
		except Exception,error:raise StandardError,"Failed to build crv. step: %s | error : %s"%(i,error) 
		
		try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		    if i == 0:
			str_side = 'left'
		    else:
			str_side = 'right'
		    d_build = {'brow{0}'.format(str_side):{'target':mi_crv,
		                                           'bindJoints':self.md_rigList['browInfluenceJoints'][str_side]}}
		    faceUtils.skin_fromDict(self,d_build)
		except Exception,error:raise Exception,"[Skinning! | error: {0}".format(error)	
		
		try:# Setup rig joints ------------------------------------------------------------------------------------
		    int_lastIndex = len(ml_rigJoints) - 1
		    int_lenMax = len(ml_rigJoints)
		    for obj_idx,mObj in enumerate( ml_rigJoints ):
			d_current = self.md_attachReturns[mObj]
			self.progressBar_set(status = "Connecting: '%s'... "%mObj.p_nameShort, progress = obj_idx, maxValue = int_lenMax)		    				    		    						
			try:
			    try:#>> Attach  loc to curve --------------------------------------------------------------------------------------
				mi_controlLoc = d_current['controlLoc']
				mi_crvLoc = mi_controlLoc.doDuplicate(parentOnly=False)
				mi_crvLoc.addAttr('cgmTypeModifier','crvAttach',lock=True)
				mi_crvLoc.doName()
				mi_crvLoc.parent = mi_go._i_rigNull#parent to rigNull				
				crvUtils.attachObjToCurve(mi_crvLoc.mNode,mi_crv.mNode)
				mc.pointConstraint(mi_crvLoc.mNode,mi_controlLoc.mNode,maintainOffset = True)
				
			    except Exception,error:raise StandardError,"Failed to attach to crv. | error : %s"%(error)

			    try:#>> Aim the offset group  ------------------------------------------------------------------------------------------
				str_upLoc = d_current['upLoc'].mNode
				str_offsetGroup = d_current['offsetGroup'].mNode				    
				if obj_idx == 0:
				    str_offsetGroup = d_current['offsetGroup'].mNode		    				    
				    #If it's the interior brow, we need to aim forward and back on the chain
				    #We need to make a couple of locs
				    d_tomake = {'aimIn':{'target':str_centerBrowRigJoint,
				                         'aimVector':cgmMath.multiplyLists([v_aim,[-1,-1,-1]])},
				                'aimOut':{'target':ml_rigJoints[1].mNode,
				                          'aimVector':v_aim}}
				    for d in d_tomake.keys():
					d_sub = d_tomake[d]
					str_target = d_sub['target']
					mi_loc = mObj.doLoc()
					mi_loc.addAttr('cgmTypeModifier',d,lock=True)
					mi_loc.doName()
					mi_loc.parent = d_current['zeroGroup']
					d_sub['aimLoc'] = mi_loc
					v_aimVector = d_sub['aimVector']
					if str_side == 'right':
					    v_aimVector = cgmMath.multiplyLists([v_aimVector,[-1,-1,-1]])
					mc.aimConstraint(str_target,mi_loc.mNode,
				                         maintainOffset = True,
				                         weight = 1,
				                         aimVector = v_aimVector, upVector = v_up,
				                         worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )
				    mc.orientConstraint([d_tomake['aimIn']['aimLoc'].mNode, d_tomake['aimOut']['aimLoc'].mNode],str_offsetGroup,maintainOffset = True)					

				elif obj_idx == int_lastIndex:
				    ml_targets = [ml_rigJoints[obj_idx-1]]
				    #ml_targets = [ ml_handles[1].influenceJoint ]
				    #ml_targets = [ml_rigJoints[obj_idx-1].masterGroup.follicleFollow]
				    
				    str_offsetGroup = d_current['offsetGroup'].mNode		    
				    str_upLoc = d_current['upLoc'].mNode				    

				    mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup, skip = [mi_go._jointOrientation[1],mi_go._jointOrientation[2]],
		                                     maintainOffset = True, weight = 1, aimVector = cgmMath.multiplyLists([v_aim,[-1,-1,-1]]), upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
				    
				else:
				    ml_targets = [ml_rigJoints[obj_idx-1].masterGroup.follicleFollow]
				    str_offsetGroup = d_current['offsetGroup'].mNode	
				    str_upLoc = d_current['upLoc'].mNode				    				    			    
				    mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup, skip = [mi_go._jointOrientation[1],mi_go._jointOrientation[2]],
				                     maintainOffset = True, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
			
			    except Exception,error:raise StandardError,"Loc setup. | error : %s"%(error)
	
			    self.md_attachReturns[mObj] = d_current#push back
			except Exception,error:
			    raise StandardError,"Rig joint setup fail. obj: %s | error : %s"%(mObj.p_nameShort,error)	    
		except Exception,error:raise StandardError,"Rig joint setup fail. step: %s | error : %s"%(i,error) 
	    
	    '''
	    
	    
	    
	    
	    
	    try:#>> Center Brow =======================================================================================
		ml_handles = self.md_rigList['browHandles']['center']
		ml_rigJoints = self.md_rigList['browRig']['center']
		mi_centerHandle = ml_handles[0]
		mi_centerRigJoint = ml_rigJoints[0]
		
		try:#Connect the control loc to the center handle
		    d_attachReturn = self.md_attachReturns[ml_rigJoints[0]]
		    mi_controlLoc = d_attachReturn['controlLoc']
		    mi_follicleOffset = d_attachReturn['offsetGroup']
		    mc.pointConstraint(mi_centerHandle.mNode,mi_controlLoc.mNode)
		    
		    cgmMeta.cgmAttr(mi_follicleOffset,'rotate').doConnectIn("%s.rotate"%(mi_centerHandle.mNode))
		    str_tAim = "t{0}".format(mi_go._jointOrientation[0])
		    cgmMeta.cgmAttr(mi_follicleOffset,str_tAim).doConnectIn("{0}.{1}".format(mi_centerHandle.mNode,str_tAim))
		    
		except Exception,error:raise StandardError,"Control loc connect | error: %s"%(error)			
		    
		try:#Setup the offset group which will take half the left/right handles
		    #Create offsetgroup for the mid
		    mi_offsetGroup = cgmMeta.asMeta( mi_centerHandle.doGroup(True),'cgmObject',setClass=True)	 
		    mi_offsetGroup.doStore('cgmName',mi_centerHandle)
		    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		    mi_offsetGroup.doName()
		    mi_centerHandle.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
		    
		    arg = "{0}.ty = {1}.ty >< {2}.ty".format(mi_offsetGroup.p_nameShort,
		                                             self.md_rigList['brow']['left']['ml_handles'][0].p_nameShort,
		                                             self.md_rigList['brow']['right']['ml_handles'][0].p_nameShort,
		                                             )
		    NodeF.argsToNodes(arg).doBuild()
		except Exception,error:raise StandardError,"Offset group | error: %s"%(error)			
		try:#Create the brow up loc and parent it to the 
		    mi_browFrontUpLoc = mi_offsetGroup.doLoc()
		    mi_browFrontUpLoc.parent = mi_offsetGroup.parent
		    mi_browFrontUpLoc.tz = f_offsetOfUpLoc
		    self.mi_browFrontUpLoc = mi_browFrontUpLoc
		    mi_go.connect_toRigGutsVis(mi_browFrontUpLoc,vis = True)#connect to guts vis switches		    
		except Exception,error:raise StandardError,"Offset group | error: %s"%(error)			
		
	    except Exception,error:
		raise StandardError,"[Center brow] | error: {0}".format(error)	    
	    
	    try:#>> Influence joints =======================================================================================
		for i,str_side in enumerate(['left','right']):
		    try:
			try:
			    ml_handles = self.md_rigList['browHandles'][str_side]
			    ml_rigJoints = self.md_rigList['browRig'][str_side]	 
			    ml_influenceJoints = self.md_rigList['browInfluenceJoints'][str_side]
			    mi_midHandleInfluence = ml_influenceJoints[1]			    
			except Exception,error:raise StandardError,"[side query | {0}]".format(error) 
			
			for ii,mHandle in enumerate(ml_handles):
			    self.log_info("handle: {0}".format(mHandle))
			    try:#Setup influence jiontshandle --------------------------------------------------------------------------------------------
				try:#query
				    mi_influenceJoint = ml_influenceJoints[ii]
				    d_return = self.md_attachReturns[mi_influenceJoint]
				    #str_upLoc = self.mi_browUpLoc.mNode
				except Exception,error:raise StandardError,"[handle query | {0}]".format(error) 
		
				if ii == 1:#Create offsetgroup for the mid
				    mi_offsetGroup = cgmMeta.asMeta( mHandle.doGroup(True),'cgmObject',setClass=True)	 
				    mi_offsetGroup.doStore('cgmName',mHandle)
				    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
				    mi_offsetGroup.doName()
				    mHandle.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')
				    #skip = mi_go._jointOrientation[0]
				    mc.pointConstraint([ml_handles[0].mNode,ml_handles[-1].mNode],mi_offsetGroup.mNode,maintainOffset = True,
					                )
				
				try:#Influence Joint
				    if ii > 0:
					try:#aim ---- mid influence ------------------------------------------------------------------------------------------
					    if str_side == 'left':
						v_aim = mi_go._vectorOutNegative
					    else:
						v_aim = mi_go._vectorOut			    
		    
					    #ml_targets = [ ml_handles[1] ]			    
					    str_offsetGroup = d_return['offsetGroup'].mNode		    
					    str_upLoc = d_return['upLoc'].mNode		
					    mi_target = ml_handles[0].influenceJoint			    					    
					    #skip = [mi_go._jointOrientation[1],mi_go._jointOrientation[2]],
					    mc.aimConstraint(mi_target.mNode, str_offsetGroup,
						             maintainOffset = True, weight = 1,aimVector = v_aim,
						             upVector = mi_go._vectorUp, worldUpVector = [0,1,0],
						             worldUpObject = str_upLoc, worldUpType = 'object' )
						     
					except Exception,error:raise StandardError,"[Aim mid | {0}]".format(error)			    
				except Exception,error:raise StandardError,"[influence setup | {0}]".format(error) 
				try:#Connect mid handle to influence ------------------------------------------------------------------------------------------					
				    #for attr in ['rotate']:
					#cgmMeta.cgmAttr(str_offsetGroup,attr).doConnectIn("%s.%s"%(ml_handles[1].mNode,attr))
				    for attr in ['scale']:
					cgmMeta.cgmAttr(ml_influenceJoints[ii],attr).doConnectIn("%s.%s"%(mHandle.mNode,attr))				
				except Exception,error:raise StandardError,"[Connect mid handle to influence]{%s}"%(error)
				
				try:#Wire offset ------------------------------------------------------------------------------------------
				    if ii == 1:
					mPlug_midInfluenceOffset = cgmMeta.cgmAttr(d_return['offsetGroup'],'t{0}'.format(mi_go._jointOrientation[0]))
					arg_av = "{0} = {2}.t{1} >< {3}.t{1} <> {4}.t{1}".format(mPlug_midInfluenceOffset.p_combinedShortName,
					                                                         mi_go._jointOrientation[0],
					                                                         ml_handles[0].p_nameShort, ml_handles[1].p_nameShort,ml_handles[0].p_nameShort)
					#self.log_info(arg_div)
					NodeF.argsToNodes(arg_av).doBuild()					
				    else:
					self.log_info("connecting: {0} '{1}' to {2}.{1}".format(d_return['offsetGroup'].p_nameShort, mi_go._jointOrientation[0], mHandle.mNode))
					cgmMeta.cgmAttr(d_return['offsetGroup'],'t{0}'.format(mi_go._jointOrientation[0])).doConnectIn("{0}.t{1}".format(mHandle.mNode,mi_go._jointOrientation[0]))
				except Exception,error:raise StandardError,"[wire fwd/back | {0}]".format(error) 				
				'''
				if ii > 0:
				    #Create aim offsetgroup for the mid
				    mi_aimGroup = cgmMeta.cgmObject( mHandle.doGroup(True),setClass=True)	 
				    mi_aimGroup.doStore('cgmName',mHandle)
				    mi_aimGroup.addAttr('cgmTypeModifier','aim',lock=True)
				    mHandle.connectChildNode(mi_aimGroup,'aimGroup','groupChild')		    
				    mi_aimGroup.doName()
				    #str_upLoc = self.mi_browUpLoc.mNode
				    str_upLoc = d_return['upLoc'].mNode	
				    
				    if str_side == 'left':
					v_aim = mi_go._vectorOutNegative
				    else:
					v_aim = mi_go._vectorOut
					
				    mc.aimConstraint(mi_target.mNode, mi_aimGroup.mNode,
					             maintainOffset = True, weight = 1, aimVector = v_aim, upVector = mi_go._vectorUp, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' ) 
						     '''
			    except Exception,error:raise StandardError,"['{0}' | step: {1} |  error {2}]".format(mHandle.p_nameShort,ii,error) 	    
		    except Exception,error:raise StandardError,"['{0}' | error {1}]".format(str_side,error) 	    
	    except Exception,error:raise StandardError,"[Influence setup | error: {0}]".format(error)
	    
	def _buildBrowsOld_(self):
	    try:#>> Attach brow rig joints =======================================================================================
		mi_go = self._go#Rig Go instance link
		#str_skullPlate = self.str_skullPlate
		str_skullPlate = 'browPlate'
		if not mc.objExists(str_skullPlate):raise StandardError,"Missing test skull plate"
		d_section = self.md_rigList['brow']
		ml_rigJoints = d_section['center']['ml_rigJoints'] + d_section['left']['ml_rigJoints'] + d_section['right']['ml_rigJoints']
		if not ml_rigJoints:raise StandardError,"No rigJoints"
		ml_handles = d_section['center']['ml_handles'] + d_section['left']['ml_handles'] + d_section['right']['ml_handles']
		if not ml_handles:raise StandardError,"No handles"
		str_centerBrowRigJoint = d_section['center']['ml_rigJoints'][0].mNode
		if not str_centerBrowRigJoint:raise StandardError,"Missing center brow rig joint"
		
		
		f_offsetOfUpLoc = distance.returnDistanceBetweenObjects(d_section['left']['ml_rigJoints'][0].mNode,
		                                                        d_section['left']['ml_rigJoints'][-1].mNode)
		int_lenMax = len(ml_rigJoints)
		for i,mObj in enumerate(ml_rigJoints):
		    try:
			self.progressBar_set(status = "Attaching: '%s'... "%mObj.p_nameShort, progress = i, maxValue = int_lenMax)		    				    		    			
			try:#>> Attach ------------------------------------------------------------------------------------------
			    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                    targetSurface = str_skullPlate,
				                                    createControlLoc = True,
				                                    createUpLoc = True,
			                                            attachControlLoc = True,
			                                            #parentToFollowGroup = 1,#NEW, trying
				                                    f_offset = f_offsetOfUpLoc,
				                                    orientation = mi_go._jointOrientation)
			except Exception,error:raise StandardError,"Failed to attach. | error : %s"%(error)
			try:#>> Setup curve locs ------------------------------------------------------------------------------------------
			    mi_controlLoc = d_return['controlLoc']
			    mi_crvLoc = mi_controlLoc.doDuplicate(parentOnly=False)
			    mi_crvLoc.addAttr('cgmTypeModifier','crvAttach',lock=True)
			    mi_crvLoc.doName()
			    mi_crvLoc.parent = mi_go._i_rigNull#parent to rigNull
			    d_return['crvLoc'] = mi_crvLoc #Add the curve loc
			except Exception,error:raise StandardError,"Loc setup. | error : %s"%(error)
    
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"Attach rig joint loop. obj: %s | error : %s"%(mObj.p_nameShort,error)	    
		    
		for mObj in ml_handles:
		    try:
			try:#>> Attach ------------------------------------------------------------------------------------------
			    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                    targetSurface = str_skullPlate,
				                                    createControlLoc = False,
				                                    createUpLoc = True,	
			                                            parentToFollowGroup = 0,#NEW, trying
				                                    orientation = mi_go._jointOrientation)
			except Exception,error:raise StandardError,"Failed to attach. | error : %s"%(error)
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"Attach handle. obj: %s | error : %s"%(mObj.p_nameShort,error)	  
	    except Exception,error:
		raise StandardError,"[Attach] | error: {0}".format(error)
	    
	    try:#>> Center Brow =======================================================================================
		ml_handles = d_section['center']['ml_handles']
		ml_rigJoints = d_section['center']['ml_rigJoints'] 
		mi_centerHandle = ml_handles[0]
		mi_centerRigJoint = ml_rigJoints[0]
		
		try:#Connect the control loc to the center handle
		    mi_controlLoc = self.md_attachReturns[ml_rigJoints[0]]['controlLoc']
		    mc.pointConstraint(mi_centerHandle.mNode,mi_controlLoc.mNode)
		    #cgmMeta.cgmAttr(mi_controlLoc,"translate").doConnectIn("%s.translate"%mi_centerHandle.mNode)
		except Exception,error:raise StandardError,"Control loc connect | error: %s"%(error)			
		    
		try:#Setup the offset group which will take half the left/right handles
		    #Create offsetgroup for the mid
		    mi_offsetGroup = cgmMeta.asMeta( mi_centerHandle.doGroup(True),'cgmObject',setClass=True)	 
		    mi_offsetGroup.doStore('cgmName',mi_centerHandle)
		    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		    mi_offsetGroup.doName()
		    mi_centerHandle.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
		    
		    arg = "{0}.ty = {1}.ty >< {2}.ty".format(mi_offsetGroup.p_nameShort,
		                                             self.md_rigList['brow']['left']['ml_handles'][0].p_nameShort,
		                                             self.md_rigList['brow']['right']['ml_handles'][0].p_nameShort,
		                                             )
		    NodeF.argsToNodes(arg).doBuild()
		except Exception,error:raise StandardError,"Offset group | error: %s"%(error)			
		try:#Create the brow up loc and parent it to the 
		    mi_browFrontUpLoc = mi_offsetGroup.doLoc()
		    mi_browFrontUpLoc.parent = mi_offsetGroup.parent
		    mi_browFrontUpLoc.tz = f_offsetOfUpLoc
		    self.mi_browFrontUpLoc = mi_browFrontUpLoc
		    mi_go.connect_toRigGutsVis(mi_browFrontUpLoc,vis = True)#connect to guts vis switches		    
		except Exception,error:raise StandardError,"Offset group | error: %s"%(error)			
		
	    except Exception,error:
		raise StandardError,"[Center brow] | error: {0}".format(error)
	    
	    #>> Left and Right =======================================================================================
	    for i,d_browSide in enumerate([self.md_rigList['brow']['left'],self.md_rigList['brow']['right']] ):
		ml_handles = d_browSide['ml_handles']
		ml_rigJoints = d_browSide['ml_rigJoints']
		"""
		log.info("%s Handles >>>>"%self._str_reportStart)
		for mObj in ml_handles:
		    log.info(">>> %s "%mObj.p_nameShort)
		log.info("%s Rig Joints >>>>"%self._str_reportStart)
		for mObj in ml_rigJoints:
		    log.info(">>> %s "%mObj.p_nameShort)
		    """
		if len(ml_handles) != 3:
		    raise StandardError,"Only know how to rig a 3 handle brow segment. step: %s"%(i) 	
		
		str_side = ml_rigJoints[0].cgmDirection
		v_up = mi_go._vectorAim
		if str_side == 'left':
		    v_aim = mi_go._vectorOut
		else:
		    v_aim = mi_go._vectorOutNegative
		    
		try:#Create our curves ------------------------------------------------------------------------------------
		    str_crv = mc.curve(d=1,ep=[mObj.getPosition() for mObj in ml_rigJoints],os =True)
		    mi_crv = cgmMeta.asMeta(str_crv,'cgmObject',setClass=True)
		    mi_crv.doCopyNameTagsFromObject(ml_rigJoints[0].mNode,ignore=['cgmIterator','cgmTypeModifier','cgmType'])
		    mi_crv.addAttr('cgmTypeModifier','driver',lock=True)
		    mi_crv.doName()
		    mi_crv.parent = mi_go._i_rigNull#parent to rigNull
		    self.ml_toVisConnect.append(mi_crv)	
		    d_browSide['mi_crv'] = mi_crv
		except Exception,error:raise StandardError,"Failed to build crv. step: %s | error : %s"%(i,error) 
		
		try:# Setup rig joints ------------------------------------------------------------------------------------
		    int_lastIndex = len(ml_rigJoints) - 1
		    int_lenMax = len(ml_rigJoints)
		    for obj_idx,mObj in enumerate( ml_rigJoints ):
			d_current = self.md_attachReturns[mObj]
			self.progressBar_set(status = "Connecting: '%s'... "%mObj.p_nameShort, progress = obj_idx, maxValue = int_lenMax)		    				    		    						
			try:
			    try:#>> Attach  loc to curve --------------------------------------------------------------------------------------
				mi_crvLoc = d_current['crvLoc']
				mi_controlLoc = d_current['controlLoc']
				crvUtils.attachObjToCurve(mi_crvLoc.mNode,mi_crv.mNode)
				mc.pointConstraint(mi_crvLoc.mNode,mi_controlLoc.mNode,maintainOffset = True)
				
			    except Exception,error:raise StandardError,"Failed to attach to crv. | error : %s"%(error)
			    '''
			    try:#Aim Offset group ----------------------------------------------------------------------
				mi_aimOffsetGroup = cgmMeta.cgmObject(mObj.doGroup(True),setClass=True)
				mi_aimOffsetGroup.doStore('cgmName',mObj)
				mi_aimOffsetGroup.addAttr('cgmTypeModifier','AimOffset',lock=True)
				mi_aimOffsetGroup.doName()
				mObj.connectChildNode(mi_aimOffsetGroup,"aimOffsetGroup","childObject")					    
			    except Exception,error:raise StandardError,"[AimOffset group]{%s}"%(error)			    
			    '''
			    try:#>> Aim the offset group  ------------------------------------------------------------------------------------------
				str_upLoc = d_current['upLoc'].mNode
				str_offsetGroup = d_current['offsetGroup'].mNode				    
				if obj_idx == 0:
				    str_offsetGroup = d_current['offsetGroup'].mNode		    				    
				    #If it's the interior brow, we need to aim forward and back on the chain
				    #We need to make a couple of locs
				    d_tomake = {'aimIn':{'target':str_centerBrowRigJoint,
				                         'aimVector':cgmMath.multiplyLists([v_aim,[-1,-1,-1]])},
				                'aimOut':{'target':ml_rigJoints[1].mNode,
				                          'aimVector':v_aim}}
				    for d in d_tomake.keys():
					d_sub = d_tomake[d]
					str_target = d_sub['target']
					mi_loc = mObj.doLoc()
					mi_loc.addAttr('cgmTypeModifier',d,lock=True)
					mi_loc.doName()
					mi_loc.parent = d_current['zeroGroup']
					d_sub['aimLoc'] = mi_loc
					v_aimVector = d_sub['aimVector']
					if str_side == 'right':
					    v_aimVector = cgmMath.multiplyLists([v_aimVector,[-1,-1,-1]])
					mc.aimConstraint(str_target,mi_loc.mNode,
				                         maintainOffset = True,
				                         weight = 1,
				                         aimVector = v_aimVector, upVector = v_up,
				                         worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )
				    mc.orientConstraint([d_tomake['aimIn']['aimLoc'].mNode, d_tomake['aimOut']['aimLoc'].mNode],str_offsetGroup,maintainOffset = True)					
				    '''
				    ml_targets = [ml_rigJoints[obj_idx+1]]
				    #ml_targets = [ ml_handles[1].influenceJoint ]
				    
				    str_offsetGroup = d_current['offsetGroup'].mNode		    
				    str_upLoc = d_current['upLoc'].mNode				    

				    mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup,
                                                     maintainOffset = True, weight = 1, aimVector = cgmMath.multiplyLists([v_aim,[-1,-1,-1]]), upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
				    '''
				elif obj_idx == int_lastIndex:
				    ml_targets = [ml_rigJoints[obj_idx-1]]
				    #ml_targets = [ ml_handles[1].influenceJoint ]
				    #ml_targets = [ml_rigJoints[obj_idx-1].masterGroup.follicleFollow]
				    
				    str_offsetGroup = d_current['offsetGroup'].mNode		    
				    str_upLoc = d_current['upLoc'].mNode				    

				    mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup, skip = [mi_go._jointOrientation[1],mi_go._jointOrientation[2]],
		                                     maintainOffset = True, weight = 1, aimVector = cgmMath.multiplyLists([v_aim,[-1,-1,-1]]), upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
				    
				else:
				    ml_targets = [ml_rigJoints[obj_idx-1].masterGroup.follicleFollow]
				    str_offsetGroup = d_current['offsetGroup'].mNode	
				    str_upLoc = d_current['upLoc'].mNode				    				    			    
				    mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup, skip = [mi_go._jointOrientation[1],mi_go._jointOrientation[2]],
				                     maintainOffset = True, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
			
			    except Exception,error:raise StandardError,"Loc setup. | error : %s"%(error)
	
			    self.md_attachReturns[mObj] = d_current#push back
			except Exception,error:
			    raise StandardError,"Rig joint setup fail. obj: %s | error : %s"%(mObj.p_nameShort,error)	    
		except Exception,error:raise StandardError,"Rig joint setup fail. step: %s | error : %s"%(i,error) 
		
		try:#Setup mid handle --------------------------------------------------------------------------------------------
		    try:#query
			d_firstRigJoint = self.md_attachReturns[ml_rigJoints[0]]
			d_firstHandle = self.md_attachReturns[ml_handles[0]]		    
			self.d_buffer = d_firstRigJoint	    
			mi_midHandle = ml_handles[1]
			str_upLoc = self.mi_browUpLoc.mNode
		    except Exception,error:raise StandardError,"[Query]{%s}"%(error) 

		    #Create offsetgroup for the mid
		    mi_offsetGroup = cgmMeta.asMeta( mi_midHandle.doGroup(True),'cgmObject',setClass=True)	 
		    mi_offsetGroup.doStore('cgmName',mi_midHandle)
		    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		    mi_offsetGroup.doName()
		    mi_midHandle.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')
		    mc.pointConstraint([ml_handles[0].mNode,ml_handles[-1].mNode],mi_offsetGroup.mNode,maintainOffset = True,
		                        skip = mi_go._jointOrientation[0])
		    
		    try:#Influence Joint
			mi_midHandleInfluence = ml_handles[1].influenceJoint
			try:#>> Attach ------------------------------------------------------------------------------------------
			    d_return = surfUtils.attachObjToSurface(objToAttach = mi_midHandleInfluence,
			                                            targetSurface = str_skullPlate,
				                                    createControlLoc = True,
				                                    createUpLoc = True,
				                                    f_offset = f_offsetOfUpLoc,
				                                    orientation = mi_go._jointOrientation)
			except Exception,error:raise StandardError,"[Failed to attach]{%s}"%(error)
			self.md_attachReturns[mi_midHandleInfluence] = d_return	
			
			mi_controlLoc = d_return['controlLoc']
			mc.pointConstraint([ml_handles[1].mNode], mi_controlLoc.mNode,maintainOffset = True)
			
			try:#aim ---- mid influence ------------------------------------------------------------------------------------------
			    if str_side == 'left':
				v_aim = mi_go._vectorOutNegative
			    else:
				v_aim = mi_go._vectorOut			    

			    ml_targets = [ ml_handles[1] ]			    
			    str_offsetGroup = d_return['offsetGroup'].mNode		    
			    str_upLoc = d_return['upLoc'].mNode				    

			    mc.aimConstraint(ml_handles[0].mNode, str_offsetGroup,
				             maintainOffset = True, weight = 1, skip = [mi_go._jointOrientation[1],mi_go._jointOrientation[2]],
			                     aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )
				     
			except Exception,error:raise StandardError,"[Aim mid]{%s}"%(error)
			
			try:#Connect mid handle to influence ------------------------------------------------------------------------------------------
			    str_offsetGroup = d_return['offsetGroup'].mNode		    
			    
			    #for attr in ['rotate']:
				#cgmMeta.cgmAttr(str_offsetGroup,attr).doConnectIn("%s.%s"%(ml_handles[1].mNode,attr))
			    for attr in ['scale']:
				cgmMeta.cgmAttr(mi_midHandleInfluence,attr).doConnectIn("%s.%s"%(ml_handles[1].mNode,attr))				
			except Exception,error:raise StandardError,"[Connect mid handle to influence]{%s}"%(error)

		    except Exception,error:raise StandardError,"[Mid Influence]{%s}"%(error) 
		    
		    #Create aim offsetgroup for the mid
		    
		    mi_aimGroup = cgmMeta.asMeta( mi_midHandle.doGroup(True),'cgmObject',setClass=True)	 
		    mi_aimGroup.doStore('cgmName',mi_midHandle)
		    mi_aimGroup.addAttr('cgmTypeModifier','aim',lock=True)
		    mi_midHandle.connectChildNode(mi_aimGroup,'aimGroup','groupChild')		    
		    mi_aimGroup.doName()
		    str_upLoc = self.mi_browUpLoc.mNode
		    
		    if str_side == 'left':
			v_aim = mi_go._vectorOutNegative
		    else:
			v_aim = mi_go._vectorOut
			
		    mc.aimConstraint(ml_handles[0].mNode, mi_aimGroup.mNode,
		                     maintainOffset = True, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )
		     
		except Exception,error:raise StandardError,"[Mid failed. step: %s ]{%s}"%(i,error) 
		
		try:#Skin -------------------------------------------------------------------------------------------------
		    ml_influenceHandles = [ml_handles[0],ml_handles[1].influenceJoint,ml_handles[-1]]
		    mi_skinNode = cgmMeta.cgmNode(mc.skinCluster ([mObj.mNode for mObj in ml_influenceHandles],
		                                                  mi_crv.mNode,
		                                                  tsb=True,
		                                                  maximumInfluences = 3,
		                                                  normalizeWeights = 1,dropoffRate=2.5)[0])
		    mi_skinNode.doCopyNameTagsFromObject(mi_crv.mNode,ignore=['cgmType'])
		    mi_skinNode.doName()
		    d_browSide['mi_skinNode'] = mi_skinNode
		except Exception,error:raise StandardError,"Failed to skinCluster crv. step: %s | error : %s"%(i,error) 
		

	
	def _buildBrowVolume_(self):
	    try:#>> Attach brow rig joints =======================================================================================
		mi_go = self._go#Rig Go instance link
		#str_skullPlate = self.str_skullPlate
		str_skullPlate = 'testSkullOnlyPlate'		
		d_section = self.md_rigList['brow']
		mi_browSettings = mi_go._mi_module.rigNull.browSettings			
	    except Exception,error:raise Exception,"[Query]{%s}"%error

	    for str_direction in 'left','right':
		try:
		    ml_influenceJoints = self.md_rigList['browInfluenceJoints'][str_direction]
		    ml_innerOuterOffsetPlugs = []
		    
		    try:#inner/outer fail! ----------------------------------------------------------------------------------
			ml_handles =  d_section[str_direction]['ml_handles']
			_d_handles = {ml_handles[0]:{'label':'inner','targetValue':-4.0,'maxOut': 1.5,'inflIdx':0},
			              ml_handles[-1]:{'label':'outer','targetValue':-2.0,'maxOut': 1.0,'inflIdx':-1}}
			for mi_handle in _d_handles.keys():
			    try:#Query----------------------------------------------------------------------------------
				str_label = _d_handles[mi_handle]['label']
				f_targetValue = _d_handles[mi_handle]['targetValue']
				f_maxOut = _d_handles[mi_handle]['maxOut']
				idx_infl =  _d_handles[mi_handle]['inflIdx']
				mi_influenceJnt = ml_influenceJoints[idx_infl]
			    except Exception,error:raise Exception,"[Query]{%s}"%error	
			    
			    try:# Get Plugs ----------------------------------------------------------------------------------
				mPlug_driver = cgmMeta.cgmAttr(mi_handle,"t{0}".format(mi_go._jointOrientation[1]))
				
				mPlug_maxPush = cgmMeta.cgmAttr(mi_browSettings,"%s_maxOut"%(str_label),value=f_maxOut, attrType='float',keyable=0,hidden=False)			    
				mPlug_targetValue = cgmMeta.cgmAttr(mi_browSettings,"%s_targetValue"%(str_label), value=f_targetValue,attrType='float',keyable=0,hidden=False)			    
				mPlug_result = cgmMeta.cgmAttr(mi_browSettings,"res_%s%s"%(str_direction,str_label.capitalize()), attrType='float',keyable=0,hidden=False,lock = True)			    
				mPlug_resultClamp = cgmMeta.cgmAttr(mi_browSettings,"res_%s%sClamp"%(str_direction,str_label.capitalize()),attrType='float',keyable=0,hidden=False,lock = True)			    
				mPlug_resultDiv = cgmMeta.cgmAttr(mi_browSettings,"res_%s%sDiv"%(str_direction,str_label.capitalize()), attrType='float',keyable=0,hidden=False,lock = True)			    
				mPlug_resultMult = cgmMeta.cgmAttr(mi_browSettings,"res_%s%sMult"%(str_direction,str_label.capitalize()), attrType='float',keyable=0,hidden=False,lock = True)			    
			    
			    except Exception,error:raise Exception,"[Get Plugs]{%s}"%error	
			    
			    try:# Offset ----------------------------------------------------------------------------------
				d_return = self.md_attachReturns[mi_influenceJnt]
				mi_offsetGroup = d_return['offsetGroup']
				#mi_offsetGroup = cgmMeta.cgmObject( mi_handle.doGroup(True),setClass=True)	 
				#mi_offsetGroup.doStore('cgmName',mi_handle)
				#mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
				#mi_offsetGroup.doName()
				#mi_handle.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')	
	
			    except Exception,error:raise Exception,"[Offset group]{%s}"%error			    
			    
			    try:# Nodal Args ----------------------------------------------------------------------------------
				'''
				clamp(mPlug_targetValue,0,ty)/mPlug_targetValue) * mPlug_maxValue
				'''
				try:#Clamp ----------------------------------------------------------------------------------
				    arg_clamp = "{0} = clamp({1},0,{2})".format(mPlug_resultClamp.p_combinedShortName,
				                                                mPlug_targetValue.p_combinedShortName,
				                                                "{0}.t{1}".format(mi_handle.p_nameShort,mi_go._jointOrientation[1]))
				    #self.log_info(arg_clamp)
				    NodeF.argsToNodes(arg_clamp).doBuild()
				except Exception,error:
				    #self.log_error(arg_clamp)
				    raise Exception,"[clamp setup | {0}]".format(error)
				
				try:#Div ----------------------------------------------------------------------------------
				    arg_div = "{0} = {1} / {2}".format(mPlug_resultDiv.p_combinedShortName,
				                                       mPlug_resultClamp.p_combinedShortName,
				                                       mPlug_targetValue.p_combinedShortName)
				    #self.log_info(arg_div)
				    NodeF.argsToNodes(arg_div).doBuild()		    
				except Exception,error:
				    self.log_error(arg_div)
				    raise Exception,"[div setup | {0}]".format(error)
		
				try:#Mult ---------------------------------------------------------------------------------- 
				    arg_mult = "{0} = {1} * {2}".format(mPlug_resultMult.p_combinedShortName,
				                                        mPlug_resultDiv.p_combinedShortName,
				                                        mPlug_maxPush.p_combinedShortName)
				    #self.log_info(arg_mult)
				    NodeF.argsToNodes(arg_mult).doBuild()		    
				except Exception,error:
				    self.log_error(arg_mult)
				    raise Exception,"[mult setup | {0}]".format(error)
				
				try:#Condition ---------------------------------------------------------------------------------- 
				    arg_cond = "{0} = if {1} <= 0: {2} else 0".format(mPlug_result.p_combinedShortName,
				                                                      mPlug_driver.p_combinedShortName,
				                                                      mPlug_resultMult.p_combinedShortName)
				    self.log_info("cond: {0}".format(arg_cond))
				    NodeF.argsToNodes(arg_cond).doBuild()		    
				except Exception,error:
				    self.log_error(arg_cond)
				    raise Exception,"[Condition setup | {0}]".format(error)
				
				
				try:#add ---------------------------------------------------------------------------------- 
				    mPlug_driven = cgmMeta.cgmAttr(mi_offsetGroup,"t{0}".format(mi_go._jointOrientation[0]))                     				    
				    mPlug_aimDriver = cgmMeta.cgmAttr(mi_handle,"t{0}".format(mi_go._jointOrientation[0]))                     
				    ml_innerOuterOffsetPlugs.append(mPlug_driven)
				    
				    if str_direction == 'left':
					str_rawAdd = "{0} = {1} + {2}"
				    else:
					str_rawAdd = "{0} = {1} + -{2}"
					
				    arg_add = str_rawAdd.format(mPlug_driven.p_combinedShortName,
				                                mPlug_result.p_combinedShortName,
				                                mPlug_aimDriver.p_combinedShortName)
				    self.log_info("add: {0}".format(arg_add))
				    NodeF.argsToNodes(arg_add).doBuild()		    
				except Exception,error:
				    self.log_error(arg_add)
				    raise Exception,"[add setup | {0}]".format(error)				
				'''
				try:#Connect ---------------------------------------------------------------------------------- 
				    mPlug_driven = cgmMeta.cgmAttr(mi_offsetGroup,"t{0}".format(mi_go._jointOrientation[0]))                     
				    ml_innerOuterOffsetPlugs.append(mPlug_driven)
				    
				    if str_direction == 'left':
					arg_connect = "{0} = {1}".format(mPlug_driven.p_combinedShortName,
					                                 mPlug_result.p_combinedShortName)
				    else:
					arg_connect = "{0} = -{1}".format(mPlug_driven.p_combinedShortName,
					                                  mPlug_result.p_combinedShortName)				
				    #self.log_info(arg_mult)
				    NodeF.argsToNodes(arg_connect).doBuild()		    
				except Exception,error:
				    self.log_error(arg_connect)
				    raise Exception,"[connect setup | {0}]".format(error)
				    '''
			    except Exception,error:raise Exception,"[Nodal Args | {0}]".format(error)
		    except Exception,error:raise Exception,"[inner/outer fail! | {0}]".format(error)
		    
		    try:#Mid ----------------------------------------------------------------------------------
			try:#>> Query ----------------------------------------------------------------------------------	
			    mi_handle = d_section[str_direction]['ml_handles'][1]
			    mi_influenceJnt
			    mi_midHandleInfluence = ml_influenceJoints[1]
			    mi_midMasterGroup = mi_midHandleInfluence
			    d_return = self.md_attachReturns[mi_midHandleInfluence]
			    mi_follicleOffsetGroup = d_return['offsetGroup']
			except Exception,error:raise Exception,"[Query]{%s}"%error
			
			try:# Offset ----------------------------------------------------------------------------------
			    mi_offsetGroup = cgmMeta.asMeta( mi_follicleOffsetGroup.doGroup(True),'cgmObject',setClass=True)	 
			    mi_offsetGroup.doStore('cgmName',mi_handle)
			    mi_offsetGroup.addAttr('cgmTypeModifier','pushOffset',lock=True)
			    mi_offsetGroup.doName()
			    mi_midHandleInfluence.connectChildNode(mi_offsetGroup,'pushOffsetGroup','groupChild')	
    
			except Exception,error:raise Exception,"[Offset group]{%s}"%error				
			
	
			try:# Nodal Args ----------------------------------------------------------------------------------		    
			    try:#Connect ---------------------------------------------------------------------------------- 
				arg_averageStartEnd = "{0} = {1} >< {2}".format("%s.t%s"%(mi_offsetGroup.p_nameShort,mi_go._jointOrientation[0]),
				                                                ml_innerOuterOffsetPlugs[0].p_combinedShortName,
				                                                ml_innerOuterOffsetPlugs[1].p_combinedShortName)
				#else:
				    #arg_connect = "%s = -%s"%("%s.t%s"%(mi_offsetGroup.p_nameShort,mi_go._jointOrientation[0]),
				                             #mPlug_result.p_combinedShortName)				
				#self.log_info(arg_mult)
				NodeF.argsToNodes(arg_averageStartEnd).doBuild()		    
			    except Exception,error:
				#self.log_error(arg_averageStartEnd)
				raise Exception,"[connect mid offset]{%s}"%error				    
			except Exception,error:raise Exception,"[Nodal Args ]{%s}"%error
		    
		    except Exception,error:raise Exception,"[mid fail!]{%s}"%(error)		    
		    '''
		    try:#Mid ----------------------------------------------------------------------------------
			try:#>> Query ----------------------------------------------------------------------------------	
			    mi_handle = d_section[str_direction]['ml_handles'][1]
			    mi_influenceJnt
			    mi_midHandleInfluence = ml_influenceJoints[1]
			    mi_midMasterGroup = mi_midHandleInfluence
			    d_return = self.md_attachReturns[mi_midHandleInfluence]
			    mi_follicleOffsetGroup = d_return['offsetGroup']
			except Exception,error:raise Exception,"[Query]{%s}"%error
			
			try:# Offset ----------------------------------------------------------------------------------
			    mi_offsetGroup = cgmMeta.cgmObject( mi_follicleOffsetGroup.doGroup(True),setClass=True)	 
			    mi_offsetGroup.doStore('cgmName',mi_handle)
			    mi_offsetGroup.addAttr('cgmTypeModifier','pushOffset',lock=True)
			    mi_offsetGroup.doName()
			    mi_midHandleInfluence.connectChildNode(mi_offsetGroup,'pushOffsetGroup','groupChild')	
    
			except Exception,error:raise Exception,"[Offset group]{%s}"%error				
			
			try:# Get Plugs ----------------------------------------------------------------------------------
			    mPlug_maxPush = cgmMeta.cgmAttr(mi_browSettings,"mid_maxOut",value = 2.0, attrType='float',keyable=0,hidden=False)			    
			    mPlug_targetDist = cgmMeta.cgmAttr(mi_browSettings,"mid_targetDist", value = 3.0,attrType='float',keyable=0,hidden=False)			    
			    mPlug_result = cgmMeta.cgmAttr(mi_browSettings,"result_%sMidBrow"%(str_direction),attrType='float',lock=1,keyable=0)
			    mPlug_resultClamp = cgmMeta.cgmAttr(mi_browSettings,"result_%sMidBrow_clamp"%(str_direction),attrType='float',lock=1,hidden = 0)		
			    mPlug_resultByTargetDist = cgmMeta.cgmAttr(mi_browSettings,"result_%sMidBrow_divDist"%(str_direction),attrType='float',lock=False,hidden = 0)		
			    mPlug_resultOutValue = cgmMeta.cgmAttr(mi_browSettings,"result_%sMidBrow_outVal"%(str_direction),attrType='float',lock=1,hidden = 0)		
		       
			except Exception,error:raise Exception,"[Get Plugs]{%s}"%error
			
			try:# Build and setup locs ----------------------------------------------------------------------------------
			    try:# Track loc ----------------------------------------------------------------------------------
				mi_trackLoc = mi_handle.doLoc()
				mi_trackLoc.addAttr('cgmName','%s_track'%'left')
				mi_trackLoc.doName()
				mc.pointConstraint(mi_handle.mNode, mi_trackLoc.mNode, maintainOffset = 1)
				mi_trackLoc.parent = mi_handle.masterGroup
			    except Exception,error:raise Exception,"[trackLoc fail!]{%s}"%error
			    
			    try:# Distance setup ----------------------------------------------------------------------------------
				_d = {'baseDist':{'start':mi_trackLoc}}
				
				try:# Build distance objects ----------------------------------------------------------------------------------
				    d_traveledDist = rUtils.create_distanceMeasure(baseName = 'traveledDist')
				    d_baseDist = rUtils.create_distanceMeasure(startObj = mi_trackLoc, baseName = 'baseDist')
				    
				except Exception,error:raise Exception,"[Build distance objects!]{%s}"%error
				
				try:# Snap locs ----------------------------------------------------------------------------------
				    for d__ in d_traveledDist,d_baseDist:
					for k in 'mi_start','mi_end':
					    try:Snap.go(d__[k],mi_trackLoc.mNode)
					    except Exception,error:self.log_warning("[Snapping dist loc: '%s']{%s}"%(k,error))
					    d__[k].parent = mi_handle.masterGroup
					    mi_go.connect_toRigGutsVis(d__[k],vis = True)#connect to guts vis switches
					    
					d__['mi_object'].parent = mi_go._i_rigNull
					
				except Exception,error:raise Exception,"[Snap locs!]{%s}"%error		    
				
				
				try:# Base Dist Setup ----------------------------------------------------------------------------------
				    #ptConst - end to control on x,z, y offset should be enough that it never passes this point
				    mi_start = d_baseDist['mi_start']
				    mi_end = d_baseDist['mi_end']
				    
				    #mPlug_targetDist.doConnectOut("%s.%s"%(mi_end.mNode,"t%s"%mi_go._jointOrientation[1]))
				    #mi_end.__setattr__("t%s"%mi_go._jointOrientation[1],-self.f_offsetOfUpLoc)#Offset, then constrain
				    mc.pointConstraint(mi_handle.mNode, mi_end.mNode, maintainOffset = 1,
				                       skip = [mi_go._jointOrientation[1]])
				except Exception,error:raise Exception,"[Base Dist Setup!]{%s}"%error	
				
				try:#Travel Dist Setup ----------------------------------------------------------------------------------
				    mi_start = d_traveledDist['mi_start']
				    mi_end = d_traveledDist['mi_end']
				    mc.pointConstraint(mi_handle.mNode, mi_end.mNode, maintainOffset = 1,#ptConst - end to control on x,y
				                       skip = [mi_go._jointOrientation[0]])
				    mc.pointConstraint(mi_handle.mNode, mi_start.mNode, maintainOffset = 1,#ptConst - end to control on x,y
				                       skip = [mi_go._jointOrientation[1]])			
				except Exception,error:raise Exception,"[Base Dist Setup!]{%s}"%error		    
			    except Exception,error:raise Exception,"[Distance setup]{%s}"%error	 
			except Exception,error:raise Exception,"[Build and setup locs/distance]{%s}"%error
			
			
			try:# Nodal Args ----------------------------------------------------------------------------------
			    try:#baseDist  ----------------------------------------------------------------------------------
				arg_baseDist = "%s = -%s"%("%s.t%s"%(d_baseDist['mi_end'].p_nameShort,mi_go._jointOrientation[1]),
				                           mPlug_targetDist.p_combinedShortName)
				#self.log_info(arg_baseDist)
				NodeF.argsToNodes(arg_baseDist).doBuild()
				
			    except Exception,error:
				#self.log_error(arg_baseDist)
				raise Exception,"[base dist setup]{%s}"%error			    
			    """
			    if f_maxDistance <= mPlug_maxDistance:
				mPlug_result = ((clamp(0,f_targetDist,mPlug_actualDist)/f_targetDist) * mPlug_maxValue
			    else:
				mPlug_result = 0
			    """
			    try:#Clamp ----------------------------------------------------------------------------------
				arg_clamp = "%s = clamp(0,%s,%s.distance)"%(mPlug_resultClamp.p_combinedShortName,
			                                                    mPlug_targetDist.p_combinedShortName,
			                                                    d_traveledDist['mi_shape'].p_nameShort)
				#self.log_info(arg_clamp)
				NodeF.argsToNodes(arg_clamp).doBuild()
				
			    except Exception,error:
				self.log_error(arg_clamp)
				raise Exception,"[clamp setup]{%s}"%error
			    
			    try:#Div ----------------------------------------------------------------------------------
				arg_div = "%s = %s / %s"%(mPlug_resultByTargetDist.p_combinedShortName,
			                                  mPlug_resultClamp.p_combinedShortName,
			                                  mPlug_targetDist.p_combinedShortName)
				#self.log_info(arg_div)
				NodeF.argsToNodes(arg_div).doBuild()		    
			    except Exception,error:
				self.log_error(arg_div)
				raise Exception,"[div setup]{%s}"%error
	    
			    try:#Mult ---------------------------------------------------------------------------------- 
				arg_mult = "%s = %s * %s"%(mPlug_resultOutValue.p_combinedShortName,
			                                   mPlug_resultByTargetDist.p_combinedShortName,
			                                   mPlug_maxPush.p_combinedShortName)
				#self.log_info(arg_mult)
				NodeF.argsToNodes(arg_mult).doBuild()		    
			    except Exception,error:
				self.log_error(arg_mult)
				raise Exception,"[mult setup]{%s}"%error
			    
			    try:#Cond ---------------------------------------------------------------------------------- 
				arg_cond= "%s = if %s.distance <= %s:%s else 0"%(mPlug_result.p_combinedShortName,
			                                                         d_baseDist['mi_shape'].p_nameShort,
			                                                         self.f_offsetOfUpLoc,
			                                                         mPlug_resultOutValue.p_combinedShortName)
				self.log_info(arg_cond)
				NodeF.argsToNodes(arg_cond).doBuild()		    
			    except Exception,error:
				self.log_error(arg_cond)
				raise Exception,"[cond setup]{%s}"%error
			    
			    try:#Connect ---------------------------------------------------------------------------------- 
				#if str_direction == 'left':
				arg_connect = "%s = %s"%("%s.t%s"%(mi_offsetGroup.p_nameShort,mi_go._jointOrientation[0]),
			                                 mPlug_result.p_combinedShortName)
				#else:
				    #arg_connect = "%s = -%s"%("%s.t%s"%(mi_offsetGroup.p_nameShort,mi_go._jointOrientation[0]),
				                             #mPlug_result.p_combinedShortName)				
				#self.log_info(arg_mult)
				NodeF.argsToNodes(arg_connect).doBuild()		    
			    except Exception,error:
				self.log_error(arg_connect)
				raise Exception,"[connect setup]{%s}"%error				    
			except Exception,error:raise Exception,"[Nodal Args ]{%s}"%error
		    
		    except Exception,error:raise Exception,"[mid fail!]{%s}"%(error)
		    '''
		except Exception,error:raise Exception,"['%s' side fail!]{%s}"%(str_direction,error)
	    
	def _buildUprCheek_(self):
	    try:#>> Attach uprCheek rig joints =======================================================================================
		if not self.mi_helper.buildUprCheek:
		    log.info("%s >>> Build cheek toggle: off"%(self._str_reportStart))
		    return True	
		
		mi_go = self._go#Rig Go instance link
		str_skullPlate = self.str_skullPlate
		d_section = self.md_rigList['uprCheek']
		ml_rigJoints = d_section['left']['ml_rigJoints'] + d_section['right']['ml_rigJoints']
		ml_handles = d_section['left']['ml_handles'] + d_section['right']['ml_handles']
		f_offsetOfUpLoc = self.f_offsetOfUpLoc
		
		for mObj in ml_rigJoints:
		    try:
			try:#>> Attach ------------------------------------------------------------------------------------------
			    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                    targetSurface = str_skullPlate,
				                                    createControlLoc = True,
				                                    createUpLoc = True,
				                                    f_offset = f_offsetOfUpLoc,
				                                    orientation = mi_go._jointOrientation)
			except Exception,error:raise StandardError,"Failed to attach. | error : %s"%(error)
			try:#>> Setup curve locs ------------------------------------------------------------------------------------------
			    mi_controlLoc = d_return['controlLoc']
			    mi_crvLoc = mi_controlLoc.doDuplicate(parentOnly=False)
			    mi_crvLoc.addAttr('cgmTypeModifier','crvAttach',lock=True)
			    mi_crvLoc.doName()
			    mi_crvLoc.parent = mi_go._i_rigNull#parent to rigNull
			    d_return['crvLoc'] = mi_crvLoc #Add the curve loc
			except Exception,error:raise StandardError,"Loc setup. | error : %s"%(error)
    
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"Attach rig joint loop. obj: %s | error : %s"%(mObj.p_nameShort,error)	    
		    
		for mObj in ml_handles:
		    try:
			try:#>> Attach ------------------------------------------------------------------------------------------
			    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                    targetSurface = str_skullPlate,
				                                    createControlLoc = False,
				                                    createUpLoc = True,	
			                                            parentToFollowGroup = False,
				                                    orientation = mi_go._jointOrientation)
			except Exception,error:raise StandardError,"Failed to attach. | error : %s"%(error)
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"Attach handle. obj: %s | error : %s"%(mObj.p_nameShort,error)	  
	    except Exception,error:
		raise StandardError,"Attach | %s"%(error)
	    	    
	    #>> Left and Right =======================================================================================
	    for i,d_uprCheekSide in enumerate([self.md_rigList['uprCheek']['left'],self.md_rigList['uprCheek']['right']] ):
		ml_handles = d_uprCheekSide['ml_handles']
		ml_rigJoints = d_uprCheekSide['ml_rigJoints']

		if len(ml_handles) != 2:
		    raise StandardError,"Only know how to rig a 2 handle uprCheek segment. step: %s"%(i) 	
		
		str_side = ml_rigJoints[0].cgmDirection
		v_up = mi_go._vectorAim
		if str_side == 'left':
		    v_aim = mi_go._vectorOut
		else:
		    v_aim = mi_go._vectorOutNegative
		    
		try:#Create our curves ------------------------------------------------------------------------------------
		    str_crv = mc.curve(d=1,ep=[mObj.getPosition() for mObj in ml_rigJoints],os =True)
		    mi_crv = cgmMeta.asMeta(str_crv,'cgmObject',setClass=True)
		    mi_crv.doCopyNameTagsFromObject(ml_rigJoints[0].mNode,ignore=['cgmIterator','cgmTypeModifier','cgmType'])
		    mi_crv.addAttr('cgmTypeModifier','driver',lock=True)
		    mi_crv.doName()
		    mi_crv.parent = mi_go._i_rigNull#parent to rigNull
		    self.ml_toVisConnect.append(mi_crv)	
		    d_uprCheekSide['mi_crv'] = mi_crv
		except Exception,error:raise StandardError,"Failed to build crv. step: %s | error : %s"%(i,error) 
		
		try:# Setup rig joints ------------------------------------------------------------------------------------
		    int_lastIndex = len(ml_rigJoints) - 1
		    for obj_idx,mObj in enumerate( ml_rigJoints ):
			d_current = self.md_attachReturns[mObj]
			try:
			    try:#>> Attach  loc to curve --------------------------------------------------------------------------------------
				mi_crvLoc = d_current['crvLoc']
				mi_controlLoc = d_current['controlLoc']
				crvUtils.attachObjToCurve(mi_crvLoc.mNode,mi_crv.mNode)
				mc.pointConstraint(mi_crvLoc.mNode,mi_controlLoc.mNode,maintainOffset = True)
				
			    except Exception,error:raise StandardError,"Failed to attach to crv. | error : %s"%(error)
			    try:#>> Aim the offset group  ------------------------------------------------------------------------------------------
				if obj_idx != int_lastIndex:
				    str_upLoc = d_current['upLoc'].mNode
				    str_offsetGroup = d_current['offsetGroup'].mNode				    
				    ml_targets = [ml_rigJoints[obj_idx+1]]	
				    mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup,
				                     maintainOffset = True, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
			    except Exception,error:raise StandardError,"Loc setup. | error : %s"%(error)
	
			    self.md_attachReturns[mObj] = d_current#push back
			except Exception,error:
			    raise StandardError,"Rig joint setup fail. obj: %s | error : %s"%(mObj.p_nameShort,error)	    
		except Exception,error:raise StandardError,"Rig joint setup fail. step: %s | error : %s"%(i,error) 
		
		try:#Skin -------------------------------------------------------------------------------------------------
		    mi_skinNode = cgmMeta.cgmNode(mc.skinCluster ([mObj.mNode for mObj in ml_handles],
		                                                  mi_crv.mNode,
		                                                  tsb=True,
		                                                  maximumInfluences = 3,
		                                                  normalizeWeights = 1,dropoffRate=2.5)[0])
		    mi_skinNode.doCopyNameTagsFromObject(mi_crv.mNode,ignore=['cgmType'])
		    mi_skinNode.doName()
		    d_uprCheekSide['mi_skinNode'] = mi_skinNode
		except Exception,error:raise StandardError,"Failed to skinCluster crv. step: %s | error : %s"%(i,error) 
		    
	    return True
	    
	def _attachSquash_(self):
	    mi_go = self._go#Rig Go instance link
	    str_skullPlate = self.str_skullPlate
	    d_section = self.md_rigList['squash']
	    ml_rigJoints = d_section['ml_rigJoints']	
	    for mObj in ml_rigJoints:
		try:
		    try:#>> Attach ------------------------------------------------------------------------------------------
			d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
		                                                targetSurface = str_skullPlate,
		                                                createControlLoc = False,
		                                                createUpLoc = False,
		                                                orientation = mi_go._jointOrientation)
		    except Exception,error:raise StandardError,"Failed to attach. | error : %s"%(error)
		    self.md_attachReturns[mObj] = d_return
		except Exception,error:
		    raise StandardError,"Attach rig joint loop. obj: %s | error : %s"%(mObj.p_nameShort,error)	
		
	    return True
		
	def _buildTemple_(self):
	    try:#>> Attach temple rig joints =======================================================================================
		mi_go = self._go#Rig Go instance link
		#str_skullPlate = self.str_skullPlate
		str_skullPlate = 'browPlate'
		if not mc.objExists(str_skullPlate):raise StandardError,"Missing test skull plate"		
		d_section = self.md_rigList['temple']
		ml_rigJoints = d_section['left']['ml_rigJoints'] + d_section['right']['ml_rigJoints']
		ml_handles = d_section['left']['ml_handles'] + d_section['right']['ml_handles']
    
		for mObj in ml_rigJoints:
		    try:
			try:#>> Attach ------------------------------------------------------------------------------------------
			    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                    targetSurface = str_skullPlate,
				                                    createControlLoc = True,
				                                    createUpLoc = True,
				                                    f_offset = self.f_offsetOfUpLoc,
				                                    orientation = mi_go._jointOrientation)
			except Exception,error:raise StandardError,"Failed to attach. | error : %s"%(error)
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"Attach rig joint loop. obj: %s | error : %s"%(mObj.p_nameShort,error)	    
		    
		for mObj in ml_handles:
		    try:
			try:#>> Attach ------------------------------------------------------------------------------------------
			    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                    targetSurface = str_skullPlate,
				                                    createControlLoc = False,
				                                    createUpLoc = True,	
				                                    parentToFollowGroup = False,
				                                    orientation = mi_go._jointOrientation)
			except Exception,error:raise StandardError,"Failed to attach. | error : %s"%(error)
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"Attach handle. obj: %s | error : %s"%(mObj.p_nameShort,error)	  
	    except Exception,error:
		raise StandardError,"Attach | %s"%(error)		
	    
	    try:#>> Setup handle =======================================================================================
		for i,mObj in enumerate(ml_handles):
		    try:#Connect the control loc to the center handle
			mi_controlLoc = self.md_attachReturns[ml_rigJoints[i]]['controlLoc']
			mc.pointConstraint(mObj.mNode,mi_controlLoc.mNode,maintainOffset = True)
			#cgmMeta.cgmAttr(mi_controlLoc,"translate").doConnectIn("%s.translate"%mi_centerHandle.mNode)
		    except Exception,error:raise StandardError,"Control loc connect | error: %s"%(error)			
				
	    except Exception,error:
		raise StandardError,"Setup handle | %s"%(error)
	
	def _lockNHide_(self):
	    mi_go = self._go#Rig Go instance link
	    mPlug_multpHeadScale = mi_go.mPlug_multpHeadScale
	    
	    #Lock and hide all ------------------------------------------------------------------------
	    for mHandle in self.ml_handlesJoints:
		cgmMeta.cgmAttr(mHandle,'scale',lock = True, hidden = True)
		cgmMeta.cgmAttr(mHandle,'v',lock = True, hidden = True)		
		mHandle._setControlGroupLocks()	
		
	    for mJoint in self.ml_rigJoints:
		mJoint._setControlGroupLocks()	
		mi_masterGroup = mJoint.masterGroup
		cgmMeta.cgmAttr(mJoint,'v',lock = True, hidden = True)		
		#for attr in 'xyz':
		    #mi_go.mPlug_globalScale.doConnectOut("%s.s%s"%(mi_masterGroup.mNode,attr))
		#for attr in 'XYZ':
		    #mi_go.mPlug_multpHeadScale.doConnectOut("%s.inverseScale%s"%(mJoint.mNode,attr))	
		    #mi_go.mPlug_globalScale.doConnectOut("%s.inverseScale%s"%(mJoint.mNode,attr))	
		    
	    try:#parent folicles to rignull ------------------------------------------------------------------------
		for k in self.md_attachReturns.keys():# we wanna parent 
		    d_buffer = self.md_attachReturns[k]
		    try:d_buffer['follicleFollow'].parent = mi_go._i_rigNull
		    except:pass
		    try:d_buffer['follicleAttach'].parent = mi_go._i_rigNull
		    except:pass	
		    try:
			if d_buffer.get('follicleFollow'):
			    cgmMeta.cgmAttr(d_buffer.get('follicleFollow'),'scale').doConnectIn(mPlug_multpHeadScale.p_combinedShortName)
			if d_buffer.get('follicleAttach'):
			    cgmMeta.cgmAttr(d_buffer.get('follicleAttach'),'scale').doConnectIn(mPlug_multpHeadScale.p_combinedShortName)
		    except Exception,error:
			self.log_error("[follicle scale connect. | error: {0}]".format(error))		    
		    try:
			if d_buffer.get('controlLoc'):
			    mi_go.connect_toRigGutsVis(d_buffer['controlLoc'],vis = True)#connect to guts vis switches
			    if not d_buffer['controlLoc'].parent:
				d_buffer['controlLoc'].parent = mi_go._i_rigNull
		    except:pass				    
	    except Exception,error:raise StandardError,"Parent follicles. | error : %s"%(error)
	    
	    try:#collect stuff ------------------------------------------------------------------------
		for str_type in 'locator','follicle','nurbsCurve','nurbsSurface':
		    mi_go.collectObjectTypeInRigNull(str_type)
	    except Exception,error:raise StandardError,"Collect. | error : {0}".format(error)
	    
    return fncWrap(*args, **kws).go()
    
#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'rig','function':build_rig},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------
