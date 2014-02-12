"""
------------------------------------------
cgm.core.rigger: Face.mouthNose
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

mouthNose rig builder
================================================================
"""
__version__ = 'faceAlpha2.01302014'

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

from cgm.core.rigger.lib import rig_Utils as rUtils

from cgm.lib import (attributes,
                     deformers,
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
    self.log_info(">>> %s.__bindSkeletonSetup__ >> "%self._strShortName + "-"*75)            
    try:
	if not self._cgmClass == 'JointFactory.go':
	    self.log_error("Not a JointFactory.go instance: '%s'"%self)
	    raise StandardError
	
    except Exception,error:
	self.log_error("mouthNose.__bindSkeletonSetup__>>bad self!")
	raise StandardError,error
    
    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self.rig_getSkinJoints() or []
    if not self._mi_module.isSkeletonized():
	raise StandardError, "%s is not skeletonized yet."%self._strShortName
    try:
	self._mi_module.rig_getReport()#report	
    except Exception,error:
	self.log_error("build_mouthNose>>__bindSkeletonSetup__ fail!")
	raise StandardError,error   
    
def build_rigSkeleton(*args, **kws):
    class fncWrap(modUtils.rigStep):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'build_rigSkeleton(%s)'%self.d_kws['goInstance']._strShortName	
	    self.__dataBind__()
	    self._b_reportTimes = True
	    self.l_funcSteps = [{'step':'Gather Info','call':self.gatherInfo},
	                        {'step':'Rig Joints','call':self.build_rigJoints},
	                        {'step':'Special Joints','call':self.build_specialJoints},	                        
	                        {'step':'Handle Joints','call':self.build_handleJoints},
	                        {'step':'Connections','call':self.build_connections}
	                        ]	
	    #=================================================================
	
	def gatherInfo(self):
	    mi_go = self._go#Rig Go instance link
	    try:#>> Deformation Plates =======================================================================================
		self.mi_skullPlate = cgmMeta.cgmObject('jawPlate')    
		#self.mi_skullPlate = mi_go._mi_skullPlate
		self.str_skullPlate = self.mi_skullPlate.p_nameShort
		
		self.mi_uprTeethPlate = cgmMeta.cgmObject('uprTeethPlate')    
		self.mi_lwrTeethPlate = cgmMeta.cgmObject('lwrTeethPlate')    
		self.mi_browPlate = cgmMeta.cgmObject('browPlate')    
		
	    except Exception,error:raise StandardError,"[Deformation Plates] | error: {0}".format(error)		    

	    self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    
	    for attr in self.mi_helper.getAttrs(userDefined = True):#Get allof our Helpers
		if "Helper" in attr:
		    try:self.__dict__["mi_%s"%attr.replace('Helper','Crv')] = cgmMeta.validateObjArg(self.mi_helper.getMessage(attr),noneValid=False)
		    except Exception,error:raise StandardError, " Failed to find '%s' | %s"%(attr,error)
		
		
	    #>> Find our joint lists ===================================================================
	    self.md_jointList = {}
	    self.ml_handleJoints = []
	    #list of tags we're gonna check to build our joint lists indexed to the k
	    d_jointListBuldTags = {"smileLeft":'left_smileLineJoint',
	                           "smileRight":'right_smileLineJoint',
	                           "uprCheekLeft":'left_uprCheekJoint',
	                           "uprCheekRight":'right_uprCheekJoint',
	                           "cheekLeft":'left_cheekJoint',
	                           "cheekRight":'right_cheekJoint',
	                           "uprLipLeft":'left_lipUprJoint',
	                           "uprLipRight":'right_lipUprJoint',	    
	                           "lwrLipLeft":'left_lipLwrJoint',
	                           "lwrLipRight":'right_lipLwrJoint',	    
	                           "uprLipCenter": 'center_lipUprJoint',
	                           "lwrLipCenter":'center_lipLwrJoint',	                         
	                           "cornerLipLeft":'left_lipCornerJoint',
	                           "cornerLipRight":'right_lipCornerJoint',
	                           "noseBase":'noseBaseJoint',
	                           "jaw":'jawJoint',
	                           "jawLineLeft":'left_jawLineJoint',
	                           "jawLineRight":'right_jawLineJoint',
	                           "centerJaw":'center_jawLineJoint',	                         
	                           "noseTop":'noseTopJoint',
	                           "noseTip":'noseTipJoint',
	                           "noseUnder":'noseUnderJoint',	                         
	                           "nostrilLeft":'left_nostrilJoint',
	                           "nostrilRight":'right_nostrilJoint',	                         
	                           "tongue":'tongueJoint'}
	    
	    int_lenMax = len(d_jointListBuldTags.keys())
	    for i,k in enumerate(d_jointListBuldTags.iterkeys()):
		self.progressBar_set(status = "Gathering joint data: %s... "%(k), progress = i, maxValue = int_lenMax)		    				    		    		    		
		try:self.md_jointList[k] = cgmMeta.validateObjListArg(mi_go._i_rigNull.msgList_get(d_jointListBuldTags[k]),noneValid = False)
		except Exception,error:raise StandardError,"Failed to find key:'%s'|msgList attr:'%s'|%s"%(k,d_jointListBuldTags[k],error)
	    
	    #Make some rverse lists
	    for str_key in 'lwrLipRight','uprLipRight':
		ml_buffer = copy.copy(self.md_jointList[str_key])
		ml_buffer.reverse()
		self.md_jointList[str_key+"Reversed"] = ml_buffer
		
	    
	    #Build our handle build info stuff...
	    #TODO make this a contditional build for when we don't use all the joints
	    '''
	    self.md_handleBuildInfo = {"uprCheek":{"left":{'crv':self.mi_leftUprCheekCrv,'skinKey':'uprCheekLeft'},
	                                           "right":{'crv':self.mi_rightUprCheekCrv,'skinKey':'uprCheekRight'},
	                                           'tagsPosition':['outer','inner'],
	                                           'mode':'startEnd'},
	                               "uprCheekSegment":{'left':{'skinKey':'uprCheekLeft'},
	                                                   'right':{'skinKey':'uprCheekRight'},
	                                                   'mode':'segmentChain'},
	                               "cheekSegment":{'left':{'skinKey':'cheekLeft'},
	                                                   'right':{'skinKey':'cheekRight'},
	                                                   'mode':'segmentChain'}}'''
	    
	    self.md_handleBuildInfo = {"smileLineSegment":{'left':{'skinKey':'smileLeft'},
	                                                   'right':{'skinKey':'smileRight'},
	                                                   'mode':'segmentChain'},
	                               "uprCheekSegment":{'left':{'skinKey':'uprCheekLeft'},
	                                                   'right':{'skinKey':'uprCheekRight'},
	                                                   'mode':'segmentChain'},
	                               "cheekSegment":{'left':{'skinKey':'cheekLeft'},
	                                                   'right':{'skinKey':'cheekRight'},
	                                                   'mode':'segmentChain'},
	                               "jawLineSegment":{'left':{'skinKey':'jawLineLeft'},
	                                                 'right':{'skinKey':'jawLineRight'},
	                                                 'mode':'segmentChain'},
	                               "uprLipSegment":{'left':{'ml_targets':self.md_jointList['uprLipLeft'] + self.md_jointList['uprLipCenter']},
	                                                'right':{'ml_targets':self.md_jointList['uprLipRight'] + self.md_jointList['uprLipCenter']},
	                                                'mode':'segmentChain'},
	                               "lwrLipSegment":{'left':{'ml_targets':self.md_jointList['lwrLipLeft'] + self.md_jointList['lwrLipCenter']},
	                                                'right':{'ml_targets':self.md_jointList['lwrLipRight'] + self.md_jointList['lwrLipCenter']},
	                                                'mode':'segmentChain'},
	                               "jawAnchor":{"left":{'skinKey':'jawLineLeft'},
	                                            "right":{'skinKey':'jawLineRight'},
	                                            'tags':['jawAnchor'],
	                                            'mode':'zeroDuplicate'},
	                               "cheekAnchor":{"left":{'skinKey':'cheekLeft'},
	                                              "right":{'skinKey':'cheekRight'},
	                                              'tags':['cheekAnchor'],
	                                              'mode':'zeroDuplicate'},	                               
	                               "smile":{"left":{'crv':self.mi_smileLeftCrv,'skinKey':'smileLeft',
	                                                'mi_closeTarget':self.md_jointList['cornerLipLeft'][0]},
	                                        "right":{'crv':self.mi_smileRightCrv,'skinKey':'smileRight',
	                                                 'mi_closeTarget':self.md_jointList['cornerLipRight'][0]},
	                                        "tags":['sneer','smile','smileBase'],'mode':'midSmileLinePoint'},
	                               "uprCheek":{"left":{'crv':self.mi_leftUprCheekCrv,'skinKey':'uprCheekLeft'},
	                                           "right":{'crv':self.mi_rightUprCheekCrv,'skinKey':'uprCheekRight'},
	                                           'tagsPosition':['outer','inner'],
	                                           'mode':'startEnd'},
	                               "chin":{"center":{'skinKey':'centerJaw'},"tags":['chin'],'mode':'chin'},
	                               "mouthMove":{"center":{'holder':False},
	                                            'mode':'mouthMove'},	                               
	                               "lipLwrCenter":{"center":{'skinKey':'lwrLipCenter'},'mode':'simpleDuplicate'},	                               
	                               "lipUprCenter":{"center":{'skinKey':'uprLipCenter'},'mode':'simpleDuplicate'},
	                               "cornerLipLeft":{"center":{'skinKey':'cornerLipLeft'},'mode':'simpleDuplicate'},	
	                               "cornerLipRight":{"center":{'skinKey':'cornerLipRight'},'mode':'simpleDuplicate'},
	                               "nose":{"center":{'skinKey':'noseBase'},'tags':['noseMove'],'mode':'simpleDuplicate'},	                               	                               
	                               "noseTip":{"center":{'skinKey':'noseTip'},'mode':'simpleDuplicate'},
	                               "noseUnder":{"center":{'skinKey':'noseUnder'},'mode':'simpleDuplicate'},
	                               "noseTop":{"center":{'skinKey':'noseTop'},'mode':'simpleDuplicate'},	                               
	                               "nostril":{"left":{'crv':self.mi_noseBaseCastCrv,'skinKey':'nostrilLeft',
	                                                  'minU':.05,'maxU':.4, 'reverse':False},
	                                          "right":{'crv':self.mi_noseBaseCastCrv,'skinKey':'nostrilRight',
	                                                   'minU':.05,'maxU':.4, 'reverse':True},
	                                          'mode':'midSimpleAim',
	                                          'mi_aim':self.md_jointList['noseBase'][0],'v_aim':mi_go._vectorAimNegative,
	                                          'mi_up':self.md_jointList['noseTop'][0],'v_up':mi_go._vectorUp},
	                               "lipUpr":{"left":{'crv':self.mi_lipUprCrv,'skinKey':'uprLipLeft',
	                                                 'mi_aimIn':self.md_jointList['uprLipCenter'][0],'v_aimIn':mi_go._vectorOutNegative,
	                                                 'mi_aimOut':self.md_jointList['cornerLipLeft'][0],'v_aimOut':mi_go._vectorOut,	                                                 
	                                                 'minU':0,'maxU':.5, 'reverse':False},
	                                          "right":{'crv':self.mi_lipUprCrv,'skinKey':'uprLipRight',
	                                                   'mi_aimIn':self.md_jointList['uprLipCenter'][0],'v_aimIn':mi_go._vectorOut,
	                                                   'mi_aimOut':self.md_jointList['cornerLipRight'][0],'v_aimOut':mi_go._vectorOutNegative,		                                                   
	                                                   'minU':0,'maxU':.5, 'reverse':True},
	                                          'mode':'midAimBlend',
	                                          'mi_up':self.md_jointList['noseUnder'][0],'v_up':mi_go._vectorUp},
	                               "lipLwr":{"left":{'crv':self.mi_lipLwrCrv,'skinKey':'lwrLipLeft',
	                                                 'mi_aimIn':self.md_jointList['lwrLipCenter'][0],'v_aimIn':mi_go._vectorOutNegative,
	                                                 'mi_aimOut':self.md_jointList['cornerLipLeft'][0],'v_aimOut':mi_go._vectorOut,	                                                 
	                                                 'minU':0,'maxU':.5, 'reverse':False},
	                                          "right":{'crv':self.mi_lipLwrCrv,'skinKey':'lwrLipRight',
	                                                   'mi_aimIn':self.md_jointList['lwrLipCenter'][0],'v_aimIn':mi_go._vectorOut,
	                                                   'mi_aimOut':self.md_jointList['cornerLipRight'][0],'v_aimOut':mi_go._vectorOutNegative,		                                                   
	                                                   'minU':0,'maxU':.5, 'reverse':True},
	                                          'mode':'midAimBlend',
	                                          'mi_up':self.md_jointList['noseUnder'][0],'v_up':mi_go._vectorUp},
	                               "tongue":{"center":{'skinKey':'tongue'},'mode':'startEnd','orientToSurface':False, 'tags':['tongueBase','tongueTip']},
	                               "jaw":{"center":{'skinKey':'jaw'},'mode':'simpleDuplicate'}}
	                               
	    
	def build_rigJoints(self):
	    #We'll have a rig joint for every joint
	    mi_go = self._go#Rig Go instance link
	    ml_rigJoints = mi_go.build_rigChain()
	    for mJoint in ml_rigJoints:
		if mJoint.parent == mi_go._ml_skinJoints[0].parent:
		    mJoint.parent = False
		mJoint.doName()
		
	    ml_rightRigJoints = metaUtils.get_matchedListFromAttrDict(ml_rigJoints , cgmDirection = 'right')
	    int_lenMax = len(ml_rightRigJoints)
	    for i,mJoint in enumerate(ml_rightRigJoints):
		self.progressBar_set(status = "Flipping right joints: %s... "%(mJoint.p_nameShort), progress = i, maxValue = int_lenMax)		    				    		    		    		
		mJoint.__setattr__("r%s"%mi_go._jointOrientation[1],180)
		jntUtils.freezeJointOrientation(mJoint)
	    self.ml_rigJoints = ml_rigJoints#pass to wrapper
	    
	def build_specialJoints(self):
	    #We'll have a rig joint for every joint
	    mi_go = self._go#Rig Go instance link
	    
	    try:#>>Stretch Chain ===================================================================
		str_crv = mc.curve(d = 1,ep = [self.mi_squashStartCrv.getPosition(),self.mi_squashEndCrv.getPosition()], os = True)
		l_pos = crvUtils.returnSplitCurveList(str_crv,5)
		mc.delete(str_crv)		
		l_joints = joints.createJointsFromPosListName(l_pos)
		joints.orientJointChain(l_joints,mi_go._jointOrientation,"%sup"%mi_go._jointOrientation[1])  
		
		ml_stretchJoints = []
		for i,jnt in enumerate(l_joints):
		    mi_jnt = cgmMeta.cgmObject(jnt,setClass=True)
		    if i == 0:
			mi_jnt.addAttr('cgmPosition','lower')
			mi_jnt.addAttr('cgmName','stretchSegment')
		    mi_jnt.addAttr('cgmIterator',i)
		    mi_jnt.doName()
		    ml_stretchJoints.append(mi_jnt)
		    #self.ml_handleJoints.append(mi_jnt)
		mi_go._i_rigNull.msgList_connect(ml_stretchJoints,'lowerStretchSegment',"rigNull")
		
	    except Exception,error:raise StandardError,"[Stretch Chain | error: {0}]".format(error)
	    
	    try:#>>Stretch handles ===================================================================
		d_segmentHandles = {'start':ml_stretchJoints[0],
		                    'end':ml_stretchJoints[-1]}
		for str_k in d_segmentHandles.keys():
		    mi_target = d_segmentHandles[str_k]
		    mi_jnt = cgmMeta.cgmObject( mc.duplicate(mi_target.mNode,po=True,ic=True,rc=True)[0],setClass=True )
		    mi_jnt.addAttr('cgmTypeModifier',str_k,attrType='string',lock=True)
		    mi_jnt.doName()		
		    mi_jnt.connectChildNode
		    mi_jnt.parent = False	
		    #self.ml_handleJoints.append(mi_jnt)		    
		    mi_go._i_rigNull.connectChildNode(mi_jnt,'lowerStretch%sDriver'%str_k.capitalize(),"rigNull")
		    
	    except Exception,error:raise StandardError,"[Stretch Handles | error: {0}]".format(error)	
	    
	    try:#>> Lip tighteners ===================================================================
		d_cornerTighteners = {'leftCornerSkinJoints':{'skinRootTarget': self.md_jointList['cornerLipLeft'][0],
		                                              'uprDriver': self.md_jointList['uprLipLeft'][0],
		                                              'lwrDriver': self.md_jointList['lwrLipLeft'][0]},
		                      'rightCornerSkinJoints':{'skinRootTarget': self.md_jointList['cornerLipRight'][0],
		                                              'uprDriver': self.md_jointList['uprLipRight'][0],
		                                              'lwrDriver': self.md_jointList['lwrLipRight'][0]}}
		self.ml_tighteners = []
		for str_k in d_cornerTighteners.keys():
		    d_buffer = d_cornerTighteners[str_k]
		    mi_rootTarget = d_buffer['skinRootTarget'].rigJoint
		    for str_tag in 'uprDriver','lwrDriver':
			try:
			    mi_root = cgmMeta.cgmObject( mc.duplicate(mi_rootTarget.mNode,po=True,ic=True,rc=True)[0],setClass=True )
			    mi_end = cgmMeta.cgmObject( mc.duplicate(d_buffer[str_tag].mNode,po=True,ic=True,rc=True)[0],setClass=True )
			    mi_end.parent = mi_root			    				    			    
			    mi_root.addAttr('cgmTypeModifier',str_tag,attrType='string',lock=True)
			    mi_root.doName(nameChildren=True)
			    mi_root.parent = mi_rootTarget
			    
			    mi_rootTarget.connectChildNode(mi_root,str_tag,'owner')
			    mi_rootTarget.connectChildNode(mi_end,"%sSkin"%str_tag,'owner')			
			    self.ml_tighteners.append(mi_root)
			    joints.orientJointChain([mJnt.mNode for mJnt in [mi_root,mi_end]],mi_go._jointOrientation,"%sup"%mi_go._jointOrientation[1])  
			except Exception,error:raise StandardError,"[%s]{%s}"%(str_tag,error)
	    except Exception,error:raise StandardError,"[Lip tighteners | error: {0}]".format(error)
	    
	def build_handleJoints(self):
	    mi_go = self._go#Rig Go instance link	    
	    ml_handleJoints = self.ml_handleJoints
	    l_keys = self.md_handleBuildInfo.keys()
	    int_lenMax = len(l_keys)
	    for i,k_name in enumerate(l_keys):#For each name...
		d_nameBuffer = self.md_handleBuildInfo[k_name]
		for k_direction in ['left','right','center']:#for each direction....
		    ml_skinJoints = []
		    ml_tmpHandles = []		    
		    self.progressBar_set(status = "Building handles: %s %s... "%(k_direction,k_name), progress = i, maxValue = int_lenMax)		    				    		    		    
		    try:
			d_buffer = d_nameBuffer.get(k_direction)
			l_tags = d_nameBuffer.get('tags') or False
			l_tagsPosition = d_nameBuffer.get('tagsPosition') or False			
			str_mode = d_nameBuffer.get('mode') or 'regularMid'
			#if not d_buffer:raise StandardError,"%s %s fail"%(k_name,k_direction)
			if d_buffer:
			    self.log_info("Building '{0}' | '{1}' handle joints | mode: {2}".format(k_name,k_direction,str_mode))
			    if 'skinKey' in d_buffer.keys():
				try:ml_skinJoints = self.md_jointList[d_buffer['skinKey']]
				except Exception,error:raise Exception, "[skin key fail | '%s']{%s}"%(d_buffer['skinKey'],error)
			    self.ml_build = []
			    #Build our copy list -------------------------------------------
			    if str_mode in ['regularMid','midSmileLinePoint']:
				self.ml_build = [ml_skinJoints[0],'mid',ml_skinJoints[-1]]		    
			    elif str_mode == 'startEnd':
				self.ml_build = [ml_skinJoints[0],ml_skinJoints[-1]]
			    elif str_mode == 'zeroDuplicate':
				self.ml_build = [ml_skinJoints[0]]		    
			    else:
				self.ml_build = ml_skinJoints
			    #Build ----------------------------------------------------------
			    if str_mode in ['simpleDuplicate','zeroDuplicate']:
				mi_jnt = cgmMeta.cgmObject( mc.duplicate(self.ml_build[0].mNode,po=True,ic=True,rc=True)[0],setClass=True )
				mi_jnt.parent = False#Parent to world	
				if l_tags:
				    mi_jnt.addAttr('cgmName',l_tags[0],attrType='string',lock=True)				    				    			    
				mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)
				mi_jnt.doName()
				ml_handleJoints.append(mi_jnt)	
				if str_mode == 'zeroDuplicate':
				    mc.delete( mc.normalConstraint(self.mi_skullPlate.mNode,mi_jnt.mNode,
				                                   weight = 1, aimVector = mi_go._vectorAim,
				                                   upVector = mi_go._vectorUp, worldUpType = 'scene' ))			    
				    jntUtils.freezeJointOrientation(mi_jnt)					    
			    elif str_mode == 'segmentChain':
				if not self.ml_build:#Build our list from ml_targets if we don't have them from the skin key
				    self.ml_build = d_buffer['ml_targets']
				ml_segJoints = []
				for i,mJnt in enumerate(self.ml_build):
				    mNewJnt = cgmMeta.cgmObject( mc.duplicate(mJnt.mNode,po=True,ic=True,rc=True)[0],setClass=True )
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
				#d_buffer['handle'] = ml_tmpHandles
				#self.log_info('%s%sJoints'%(k_name,k_direction.capitalize()))
				try:mi_go._i_rigNull.msgList_connect(ml_segJoints,'%s%s'%(k_name,k_direction.capitalize()),"rigNull")
				except Exception,error:raise Exception,"msgList connect fail| error: {0}".format(error)				
			    elif str_mode == 'chin':
				mi_leftCrv = self.mi_smileLeftCrv
				mi_rightCrv = self.mi_smileRightCrv
				#Get our u Values
				str_bufferULeft = mc.ls("%s.u[*]"%mi_leftCrv.mNode)[0]
				#self.log_info("Left >> u list!]{%s}"%(str_bufferULeft))       
				f_maxULeft= float(str_bufferULeft.split(':')[-1].split(']')[0])	
				str_bufferURight = mc.ls("%s.u[*]"%mi_rightCrv.mNode)[0]
				#self.log_info("Right >> u list!]{%s}"%(str_bufferURight))       
				f_maxURight= float(str_bufferURight.split(':')[-1].split(']')[0])	
				
				pos_left = distance.returnWorldSpacePosition("%s.u[%s]"%(mi_leftCrv.mNode,f_maxULeft ))
				pos_right = distance.returnWorldSpacePosition("%s.u[%s]"%(mi_rightCrv.mNode,f_maxURight ))
				pos = distance.returnAveragePointPosition([pos_left,pos_right])
				#self.log_info("pos >> %s"%pos)
				
				mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
				mi_jnt.parent = False
				mi_jnt.addAttr('cgmName',k_name,lock=True)										
				mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)				    
				mi_jnt.doName()	
				
				Snap.go(mi_jnt,self.mi_skullPlate.mNode,snapToSurface=True)					
				constraintBuffer = mc.normalConstraint(self.mi_skullPlate.mNode,mi_jnt.mNode, weight = 1, aimVector = mi_go._vectorAim, upVector = mi_go._vectorUp, worldUpType = 'scene' )
				mc.delete(constraintBuffer)	
				jntUtils.metaFreezeJointOrientation(mi_jnt)				
				ml_tmpHandles.append(mi_jnt)
			    elif str_mode == 'mouthMove':
				try:
				    pos = distance.returnAveragePointPosition([self.md_jointList['cornerLipLeft'][0].getPosition(),
				                                               self.md_jointList['cornerLipRight'][0].getPosition()])
				except Exception,error:raise StandardError,"[mouthMove pos fail]{%s}"%error
				
				mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
				mi_jnt.parent = False
				mi_jnt.addAttr('cgmName',k_name,lock=True)										
				mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)				    
				mi_jnt.doName()	
				
				Snap.go(mi_jnt,self.mi_skullPlate.mNode,snapToSurface=True)					
				mc.delete( mc.normalConstraint(self.mi_skullPlate.mNode,mi_jnt.mNode,
			                                       weight = 1, aimVector = mi_go._vectorAim,
			                                       upVector = mi_go._vectorUp, worldUpType = 'scene' ))
				jntUtils.metaFreezeJointOrientation(mi_jnt)								
				ml_tmpHandles.append(mi_jnt)
				
			    elif str_mode in ['midSimpleAim','midAimBlend']:
				try:#Get our data...
				    minU = d_buffer['minU']
				    maxU = d_buffer['maxU']
				    b_reverse = d_buffer['reverse']
				    mi_crv = d_buffer['crv']
				    v_up = d_nameBuffer['v_up']	
				    
				    mi_upBuffer = d_nameBuffer.get('mi_up')	
				    if mi_upBuffer:
					str_up = mi_upBuffer.mNode
					str_worldUpType = 'object'
				    else:
					str_worldUpType = 'vector'
					self.log_info("Vector up")
					str_up = 'nope'
					
				except Exception,error:raise StandardError,"Failed to get data for simple aim: %s"%error
				try:#Create
				    pos = crvUtils.returnSplitCurveList(mi_crv.mNode, 1, minU = minU, maxU = maxU, reverseCurve = b_reverse, rebuildForSplit=True)[0]				
				    mc.select(cl=True)
				    mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
				    mi_jnt.parent = False
				    mi_jnt.addAttr('cgmName',k_name,lock=True)										
				    mi_jnt.addAttr('cgmDirection',k_direction,lock=True)
				    mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)				    
				    mi_jnt.doName()
				    ml_tmpHandles.append(mi_jnt)				
				except Exception,error:raise StandardError,"[Simple aim build fail]{%s}"%error
				try:#Orient
				    if str_mode == 'midSimpleAim':
					try:
					    mi_aim = d_nameBuffer['mi_aim']
					    v_aim = d_nameBuffer['v_aim']
					    passKWSIn = {'weight' : 1, 'aimVector' : v_aim, 'upVector' : v_up,
					                 'worldUpObject' : str_up, 'worldUpType' : str_worldUpType}
					    if not mi_upBuffer:
						for _d_tmp in passKWSIn:
						    _d_tmp.pop('worldUpObject')
						_d_tmp['worldUpVector'] = [0,1,0]
					    mc.delete( mc.aimConstraint(mi_aim.mNode, mi_jnt.mNode,**passKWSIn))
					                                
					except Exception,error:raise StandardError,"Simple aim fail: %s"%error
				    elif str_mode == 'midAimBlend':
					try:
					    mi_aimIn = d_buffer['mi_aimIn']
					    v_aimIn = d_buffer['v_aimIn']
					    mi_locIn = mi_jnt.doLoc()
					    mi_aimOut = d_buffer['mi_aimOut']
					    v_aimOut = d_buffer['v_aimOut']	
					    mi_locOut = mi_jnt.doLoc()
					    
					    passKWSIn = {'weight' : 1, 'aimVector' : v_aimIn, 'upVector' : v_up,
					                 'worldUpObject' : str_up, 'worldUpType' : str_worldUpType}
					    passKWSOut = {'weight' : 1, 'aimVector' : v_aimOut, 'upVector' : v_up,
					                 'worldUpObject' : str_up, 'worldUpType' : str_worldUpType}
					    
					    if not mi_upBuffer:
						for _d_tmp in passKWSIn,passKWSOut:
						    _d_tmp.pop('worldUpObject')
						_d_tmp['worldUpVector'] = [0,1,0]

					    mc.delete( mc.aimConstraint(mi_aimIn.mNode, mi_locIn.mNode,**passKWSIn))         
					    mc.delete( mc.aimConstraint(mi_aimOut.mNode, mi_locOut.mNode,**passKWSOut))
					    mi_locIn.delete()
					    mi_locOut.delete()
					    '''
					    					    mc.delete( mc.aimConstraint(mi_aimIn.mNode, mi_locIn.mNode,
					                                weight = 1, aimVector = v_aimIn, upVector = v_up,
					                                worldUpObject = str_up, worldUpType = str_worldUpType ) )	
					    mc.delete( mc.aimConstraint(mi_aimOut.mNode, mi_locOut.mNode,
					                                weight = 1, aimVector = v_aimOut, upVector = v_up,
					                                worldUpObject = str_up, worldUpType = str_worldUpType ) )
					    '''
					except Exception,error:raise StandardError,"[midAimBlend aim fail]{%s}"%error
					
				    jntUtils.metaFreezeJointOrientation(mi_jnt)				
				except Exception,error:raise StandardError,"[mid fail]{%s}"%error
			    else:
				for i,mJnt in enumerate(self.ml_build):
				    if mJnt == 'mid':
					mi_crv = d_buffer.get('crv')
					if not mi_crv:
					    raise StandardError,"[Step: '%s' '%s' | failed to find use curve]"%(k_name,k_direction)
					if str_mode == 'midSmileLinePoint':
					    try:
						mi_target = d_buffer['mi_closeTarget']
						#Get initial point to get distance, offset a loc, get new pos
						pos_initial = distance.returnClosestUPosition(mi_target.mNode,mi_crv.mNode)
						f_dist = distance.returnDistanceBetweenPoints(mi_target.getPosition(),pos_initial)
						mi_loc = mi_target.doLoc()
						mi_loc.parent = mi_target
						if k_direction == 'left':
						    mi_loc.__setattr__("t%s"%mi_go._jointOrientation[2],f_dist)
						else:
						    mi_loc.__setattr__("t%s"%mi_go._jointOrientation[2],-f_dist)						
						pos = distance.returnClosestUPosition(mi_loc.mNode,mi_crv.mNode)
						mi_loc.delete()
					    except Exception,error:raise StandardError,"[midClosestCurvePoint failed]{%s}"%error    
					else:
					    pos = crvUtils.getMidPoint(mi_crv)
					mc.select(cl=True)
					mi_jnt = cgmMeta.cgmObject( mc.joint(p = pos),setClass=True )
					mi_jnt.parent = False
					mi_jnt.addAttr('cgmDirection',k_direction,lock=True)
					if l_tags:
					    mi_jnt.addAttr('cgmName',l_tags[1],attrType='string',lock=True)				    				    
					else:
					    mi_jnt.addAttr('cgmName',k_name,lock=True)						
					    mi_jnt.addAttr('cgmNameModifier','mid',attrType='string',lock=True)				    
					mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)				    
					mi_jnt.doName()
					ml_handleJoints.append(mi_jnt)
					
					#Orient
					v_aimVector = mi_go._vectorAim				
					v_upVector = mi_go._vectorUp
					#if k_direction == 'right':
					    #v_upVector = mi_go._vectorUpNegative			
					mc.delete( mc.normalConstraint(self.mi_skullPlate.mNode,mi_jnt.mNode,
				                                       weight = 1, aimVector = v_aimVector, upVector = v_upVector, 
				                                       ))				
					jntUtils.freezeJointOrientation(mi_jnt)
				    else:
					i_j = cgmMeta.cgmObject( mc.duplicate(mJnt.mNode,po=True,ic=True,rc=True)[0],setClass=True )
					i_j.parent = False#Parent to world				
					i_j.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)
					if len(self.ml_build)>1:
					    if l_tags or l_tagsPosition:
						if l_tags:i_j.addAttr('cgmName',l_tags[i],attrType='string',lock=True)
						if l_tagsPosition:
						    i_j.addAttr('cgmPosition',l_tagsPosition[i],attrType='string',lock=True)						
					    else:
						if i == 0:
						    i_j.addAttr('cgmNameModifier','start',attrType='string',lock=True)
						else:
						    i_j.addAttr('cgmNameModifier','end',attrType='string',lock=True)
					try:i_j.doRemove('cgmIterator')#Purge the iterator
					except:pass
					i_j.doName()
					ml_tmpHandles.append(i_j)	
					if d_nameBuffer.get('orientToSurface') is not False:
					    mc.delete( mc.normalConstraint(self.mi_skullPlate.mNode,i_j.mNode,
						                           weight = 1, aimVector = mi_go._vectorAim,
						                           upVector = mi_go._vectorUp, worldUpType = 'scene' ))			    
					    jntUtils.freezeJointOrientation(i_j)			
			    
			    d_buffer['handle'] = ml_tmpHandles
			    ml_handleJoints.extend(ml_tmpHandles)				
		    except Exception,error:raise StandardError,"['{0}' '{1}' failed | error:{2}".format(k_name,k_direction,error)   
	    try:#Flipping
		ml_rightHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints , cgmDirection = 'right')
		for mJoint in ml_rightHandles:
		    #self.log_info("%s flipping"% mJoint.p_nameShort)
		    mJoint.__setattr__("r%s"% mi_go._jointOrientation[1],180)
		    jntUtils.freezeJointOrientation(mJoint)		    
	    except Exception,error:raise StandardError,"[flipping] | error: {2}".format(error)   
   
	def build_connections(self):  
	    mi_go = self._go#Rig Go instance link	    	    
	    ml_jointsToConnect = []
	    ml_jointsToConnect.extend(self.ml_rigJoints) 
	    ml_jointsToConnect.extend(self.ml_tighteners)    
	    mi_go._i_rigNull.msgList_connect(self.ml_handleJoints,'handleJoints',"rigNull")
	    
	    #ml_jointsToConnect.extend(self.ml_handleJoints)
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
	    self._str_funcName = 'build_shapes(%s)'%self.d_kws['goInstance']._strShortName	
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Build Shapes','call':self.buildShapes},
	                        ]	
	    #=================================================================
	
	def buildShapes(self):
	    mi_go = self._go#Rig Go instance link
	    mShapeCast.go(mi_go._mi_module,['mouthNose'], storageInstance=mi_go)#This will store controls to a dict called    
	    
    return fncWrap(*args, **kws).go()

#>>> Controls
#===================================================================
def build_controls(*args, **kws):
    class fncWrap(modUtils.rigStep):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'build_controls(%s)'%self.d_kws['goInstance']._strShortName	
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
	    if not self.mi_helper:raise StandardError,"[No suitable helper found]"
	    
	    #>> Find our joint lists ===================================================================
	    ''' We need left and right direction splits for mirror indexing at their color sorting '''
	    self.md_jointLists = {}	    
	    self.ml_handleJoints = mi_go._i_rigNull.msgList_get('handleJoints')
	    self.ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')
	    self.ml_rigJointsToSetup = []#...joints with curves
	    self.ml_handleJointsToSetup = []#...joints with curves
	    
	    l_missingCurves = []
	    for mJnt in self.ml_handleJoints:
		if mJnt.getMessage('controlShape'):
		    self.ml_handleJointsToSetup.append(mJnt)
		else:l_missingCurves.append(mJnt.p_nameShort)
	    for mJnt in self.ml_rigJoints:
		if mJnt.getMessage('controlShape'):self.ml_rigJointsToSetup.append(mJnt)	
		
	    if l_missingCurves:
		self.log_error("Following joints missing curves: ")
		for obj in l_missingCurves:
		    self.log_error("-"*3 + " %s"%obj)
		#raise StandardError,"Some joints missing controlShape curves"
	    '''
	    self.log_info("#"*100)
	    for ii,ml_list in enumerate( [self.ml_rigJointsToSetup,self.ml_handleJoints] ):
		self.log_info("-"*100)		
		for i,mObj in enumerate(ml_list):
		    print mObj
	    self.log_info("#"*100)
	    '''
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

	def _buildControls_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    ml_rigJoints = self.ml_rigJointsToSetup
	    ml_handleJoints = self.ml_handleJointsToSetup
		
	    l_strTypeModifiers = ['direct',None]
	    for ii,ml_list in enumerate( [ml_rigJoints,ml_handleJoints] ):
		str_typeModifier = l_strTypeModifiers[ii]
		int_lenMax = len(ml_list)		
		for i,mObj in enumerate(ml_list):
		    str_mirrorSide = False
		    try:
			try:#Query --------------------------------------------------------------------------------------------------
			    self.progressBar_set(status = "Registering: '%s'"%mObj.p_nameShort, progress =  i, maxValue = int_lenMax)		    				    		    			
			    #self.log_info("%s On '%s'..."%(self._str_reportStart,mObj.p_nameShort))
			    mObj.parent = mi_go._i_deformNull
			    str_cgmNameTag = mObj.getAttr('cgmName')
			    str_cgmDirection = mObj.getAttr('cgmDirection')
			    str_mirrorSide = mi_go.verify_mirrorSideArg(str_cgmDirection)#Get the mirror side
			    
			    
			    #_addMirrorAttributeBridges = [["fwdBack","t%s"%mi_go._jointOrientation[0]]]
			    
			    if str_cgmDirection in ['center',None]:
				_addMirrorAttributeBridges = None
			    elif ii == 1:
				if str_cgmNameTag in ['lipUpr','lipLwr','nostril']:
				    _addMirrorAttributeBridges = None				    
				else:
				    _addMirrorAttributeBridges = [["fwdBack","t%s"%mi_go._jointOrientation[0]],
					                          ["mirrorRoll","r%s"%mi_go._jointOrientation[2]],
					                          ["mirrorTwist","r%s"%mi_go._jointOrientation[1]],
					                          ]					
			    '''
			    if str_cgmNameTag in ['tongueBase','tongueTip','jaw','noseTip']:_addMirrorAttributeBridges = None
			    elif ii == 0 and str_cgmNameTag in ['noseTop','noseUnder','noseBase']:_addMirrorAttributeBridges = None
			    elif str_cgmDirection == 'center' and ii == 0:_addMirrorAttributeBridges = None
			    elif ii == 1 and str_cgmDirection != 'center':
				_addMirrorAttributeBridges = [["fwdBack","t%s"%mi_go._jointOrientation[0]],
				                              ["mirrorRoll","r%s"%mi_go._jointOrientation[2]],
				                              ["mirrorTwist","r%s"%mi_go._jointOrientation[1]],
				                              ]			    
							      '''
    
			    if str_cgmNameTag in ['jaw','noseMove','mouthMove','noseTop','noseUnder','noseTip','tongueTip','tongueBase']:
				_str_mirrorAxis = 'translateX,rotateY,rotateZ'
			    else:_str_mirrorAxis = 'translateZ,rotateX,rotateY'
			    
			    if str_cgmNameTag in ['tongueTip']:_addDynParentGroup = True
			    else:_addDynParentGroup = False
			except Exception, error:raise StandardError,"[query] | error: {0}".format(error)
			
			#Register  --------------------------------------------------------------------------------------------------
			try:
			    d_buffer = mControlFactory.registerControl(mObj, useShape = mObj.getMessage('controlShape'),addMirrorAttributeBridges = _addMirrorAttributeBridges,
				                                       mirrorSide = str_mirrorSide, mirrorAxis=_str_mirrorAxis,	addDynParentGroup = _addDynParentGroup,	                                           
				                                       makeAimable=False, typeModifier=str_typeModifier)#translateZ,rotateX,rotateY    
			except Exception,error:
			    self.log_error("mObj: %s"%mObj.p_nameShort)
			    self.log_error("useShape: %s"%mObj.getMessage('controlShape'))
			    self.log_error("mirrorSide: %s"%str_mirrorSide)	
			    self.log_error("_str_mirrorAxis: %s"%_str_mirrorAxis)					    
			    raise StandardError,"Register fail!]{%s}"%error
			
			#Vis sub connect --------------------------------------------------------------------------------------------------
			if ii == 0:
			    if mObj.cgmName != 'noseBase':#<<<<<<<<<<<<<<<<<<<<<<<<<<<< NEW TMP
				self.mPlug_result_moduleFaceSubDriver.doConnectOut("%s.visibility"%mObj.mNode)
			    else:#<<<<<<<<<<<<<<<<<<<<<<<<<<<< certain controls need the vis fed to override vis, more connections, so use sparingly
				for shp in mObj.getShapes():
				    mShp = cgmMeta.cgmNode(shp)
				    mShp.overrideEnabled = 1		
				    self.mPlug_result_moduleFaceSubDriver.doConnectOut("%s.overrideVisibility"%mShp.mNode)

			mc.delete(mObj.getMessage('controlShape'))
			mObj.doRemove('controlShape')
			self.md_directionControls[str_mirrorSide].append(mObj)
			
			cgmMeta.cgmAttr(mObj,'radius',value=.01, hidden=True)
			self.ml_directControls.append(mObj)
		    except Exception, error:
			raise StandardError,"[Iterative fail item: %s | obj: %s | mirror side: %s]{%s}"%(i,mObj.p_nameShort,str_mirrorSide,error)
		    
	    self._go._i_rigNull.msgList_connect(self.ml_directControls ,'controlsDirect', 'rigNull')	    
	    self.ml_controlsAll.extend(self.ml_directControls)#append	
	    
	def _buildConnections_(self):
	    #Register our mirror indices ---------------------------------------------------------------------------------------
	    mi_go = self._go#Rig Go instance link	    
	    for str_direction in self.md_directionControls.keys():
		int_start = self._go._i_puppet.get_nextMirrorIndex( self._go._str_mirrorDirection )
		ml_list = self.md_directionControls[str_direction]
		int_lenMax = len(ml_list)				
		for i,mCtrl in enumerate(ml_list):
		    self.progressBar_set(status = "Setting mirror index: '%s'"%mCtrl.p_nameShort, progress =  i, maxValue = int_lenMax)		    				    		    					    
		    try:mCtrl.addAttr('mirrorIndex', value = (int_start + i))		
		    except Exception,error: raise StandardError,"Failed to register mirror index | mCtrl: %s | %s"%(mCtrl,error)

	    try:self._go._i_rigNull.msgList_connect(self.ml_controlsAll,'controlsAll')
	    except Exception,error: raise StandardError,"[Controls all connect]{%s}"%error	    
	    try:self._go._i_rigNull.moduleSet.extend(self.ml_controlsAll)
	    except Exception,error: raise StandardError,"[Failed to set module objectSet]{%s}"%error
	    
    return fncWrap(*args, **kws).go()
	    

def build_rig(*args, **kws):
    class fncWrap(modUtils.rigStep):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'build_rig(%s)'%self.d_kws['goInstance']._strShortName	
	    self._b_reportTimes = True
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	                        {'step':'Build Skull Deformation','call':self._buildSkullDeformation_},	
	                        {'step':'Mouth/Lip Handles','call':self._buildMouthHandles_},
	                        {'step':'Lip Structure','call':self._buildLipStructure_},
	                        #{'step':'Smile Line Build','call':self._buildSmileLines_},	                        	                        
	                        #{'step':'NoseBuild','call':self._buildNose_},
	                        #{'step':'Tongue build','call':self._buildTongue_},	                        	                        
	                        #{'step':'Cheek build','call':self._buildCheeks_},
	                        #{'step':'Lock N hide','call':self._lockNHide_},
	                        ]	
	    #=================================================================
	def _gatherInfo_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    
	    try:#>> Deformation Plates =======================================================================================
		self.mi_skullPlate = mi_go._mi_skullPlate
		self.str_skullPlate = self.mi_skullPlate.p_nameShort
		
		self.mi_jawPlate = cgmMeta.cgmObject('jawPlate')    
		self.mi_uprTeethPlate = cgmMeta.cgmObject('uprTeethPlate')    
		self.mi_lwrTeethPlate = cgmMeta.cgmObject('lwrTeethPlate')    
		self.mi_browPlate = cgmMeta.cgmObject('browPlate')    
		
	    except Exception,error:raise StandardError,"[Deformation Plates] | error: {0}".format(error)	    
	    
	    for attr in self.mi_helper.getAttrs(userDefined = True):#Get allof our Helpers
		if "Helper" in attr:
		    try:self.__dict__["mi_%s"%attr.replace('Helper','Crv')] = cgmMeta.validateObjArg(self.mi_helper.getMessage(attr),noneValid=False)
		    except Exception,error:raise StandardError, " Failed to find '%s' | %s"%(attr,error)
		
	    #>> Get our lists ==========================================================================
	    '''
	    We need lists of handle and a rig joints for each part - We're going to get it by doing a procedural dict search
	    '''
	    ml_handleJoints = mi_go._i_rigNull.msgList_get('handleJoints')
	    ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')
	    self.md_rigList = {"squashSegmentLower":{},
	                       }
	    d_buildArgs = {}
	    
	    self.ml_rigJoints = ml_rigJoints
	    self.ml_handlesJoints = ml_handleJoints
	    _l_directions = 'left','right','center'
	    _l_buildDicts = []
	    
	    try:#Build dicts to check ==================================================================================================
		#>> Nose --------------------------------------------------------------------------------------------------
		d_noseBuild = {'nostrilHandle':{"left":{},"right":{},'check':ml_handleJoints,'tag':'nostril'},
		               'nostrilRig':{"left":{},"right":{},'check':ml_rigJoints,'tag':'nostril'},
		               'noseMoveHandle':{'check':ml_handleJoints,'tag':'noseMove'},
		               'noseMoveRig':{'check':ml_rigJoints,'tag':'noseBase'},	                   
		               'noseTipRig':{'check':ml_rigJoints,'tag':'noseTip'},
		               'noseTipHandle':{'check':ml_handleJoints,'tag':'noseTip'},
		               'noseUnderRig':{'check':ml_rigJoints,'tag':'noseUnder'},
		               'noseUnderHandle':{'check':ml_handleJoints,'tag':'noseUnder'},
		               'noseTopRig':{'check':ml_rigJoints,'tag':'noseTop'},	   
		               'noseTopHandle':{'check':ml_handleJoints,'tag':'noseTop'},	                    	                    	                   
		               }
		_l_buildDicts.append(d_noseBuild)	 	
		
		#>> Smile Line --------------------------------------------------------------------------------------------------
		d_smileBuild = {'sneerHandle':{"left":{},"right":{},'check':ml_handleJoints,'tag':'sneer'},
		                'smileHandle':{"left":{},"right":{},'check':ml_handleJoints,'tag':'smile'},
		                'smileBaseHandle':{"left":{},"right":{},'check':ml_handleJoints,'tag':'smileBase'},
		                'smileLineRig':{"left":{},"right":{},'check':ml_rigJoints,'tag':'smileLine'},	                    
		                }
		_l_buildDicts.append(d_smileBuild)	    
		
			
		#>> Mouth --------------------------------------------------------------------------------------------------
		b_buildMouth = True	    
		d_mouthBuild = {'lipUprHandle':{"left":{},"right":{},'center':{},'check':ml_handleJoints,'tag':'lipUpr'},
		                'lipLwrHandle':{"left":{},"right":{},'center':{},'check':ml_handleJoints,'tag':'lipLwr'},
		                'lipCornerHandle':{"left":{},"right":{},'check':ml_handleJoints,'tag':'lipCorner'},
		                'lipCornerRig':{"left":{},"right":{},'check':ml_rigJoints,'tag':'lipCorner'},	                    
		                'lipUprRig':{"left":{},"right":{},'center':{},'check':ml_rigJoints,'tag':'lipUpr'},
		                'lipOverRig':{"left":{},"right":{},'center':{},'check':ml_rigJoints,'tag':'lipOver'},
		                'lipLwrRig':{"left":{},"right":{},'center':{},'check':ml_rigJoints,'tag':'lipLwr'},
		                'lipUnderRig':{"left":{},"right":{},'center':{},'check':ml_rigJoints,'tag':'lipUnder'},	                    
		                'chin':{'check':ml_handleJoints},
		                'mouthMove':{'check':ml_handleJoints},	 
		                }
		_l_buildDicts.append(d_mouthBuild)
		
		#>> Jaw --------------------------------------------------------------------------------------------------
		b_buildJawLine = True	    
		d_jawBuild = {'jawAnchor':{"left":{},"right":{},'check':ml_handleJoints},
		              'jawHandle':{'check':ml_handleJoints,'tag':'jaw'},
		              'jawRig':{'check':ml_rigJoints,'tag':'jaw'},		              
		              'jawLine':{"left":{},"right":{},"center":{},'check':ml_rigJoints,'checkToggle':b_buildJawLine}}
		_l_buildDicts.append(d_jawBuild)
		    
		#>> uprCheek --------------------------------------------------------------------------------------------------
		b_buildUprCheek = True
		d_uprCheekBuild = {'uprCheekHandles':{"left":{},"right":{},'check':ml_handleJoints,'tag':'uprCheek'},
		                   'uprCheekRig':{"left":{},"right":{},'check':ml_rigJoints,'tag':'uprCheek','checkToggle':b_buildUprCheek}}
		
		_l_buildDicts.append(d_uprCheekBuild)
		
		#>> cheek --------------------------------------------------------------------------------------------------
		b_buildCheek = True
		d_cheekBuild = {'cheekAnchor':{"left":{},"right":{},'check':ml_handleJoints,'checkToggle':b_buildCheek},
		                'cheekRig':{"left":{},"right":{},'check':ml_rigJoints,'tag':'cheek','checkToggle':b_buildCheek}}
		
		_l_buildDicts.append(d_cheekBuild)
			
		#>> tongue --------------------------------------------------------------------------------------------------
		b_buildTongue = True
		d_tongueBuild = {'tongueRig':{'check':ml_rigJoints,'checkToggle':b_buildTongue,'tag':'tongue'},
		                 'tongueBase':{'check':ml_handleJoints,'checkToggle':b_buildTongue},
		                 'tongueTip':{'check':ml_handleJoints,'checkToggle':b_buildTongue}}
		
		_l_buildDicts.append(d_tongueBuild)
	    except:pass

	    #>> Build our md_rigList from our dict stuff ==========================================================
	    for d in _l_buildDicts:
		for k in d.iterkeys():
		    d_buildArgs[k] = d[k]
		
	    l_keys = d_buildArgs.keys()
	    
	    #self.progressBar_setMaxStepValue(len(l_keys))
	    int_keys = (len(l_keys))
	    for i,k_tag in enumerate(l_keys):
		try:#For key loop --------------------------------------------------------------------------------
		    d_tag = d_buildArgs[k_tag]
		    if d_tag.get('tag'):str_tag = d_tag['tag']
		    else:str_tag = k_tag
		    l_keys = d_tag.keys()
		    self.progressBar_set(status = ("Getting: '%s'"%k_tag),progress = i, maxValue = int_keys)
		    if d_tag.get('checkToggle') in [True,None]:
			self.md_rigList[k_tag] = {}
			ml_checkBase = d_tag.get('check')
			if not ml_checkBase:raise StandardError,"No check key data for %s | Possibly not rig skeletonized"%k_tag
			else:
			    ml_checkSub = metaUtils.get_matchedListFromAttrDict(ml_checkBase, cgmName = str_tag)
			    #self.log_info("%s %s ml_checkSub: %s"%(self._str_reportStart,str_tag,ml_checkSub))
			#Check our directions for data --------------------------------------------------------
			_b_directionChecked = False
			for k_direction in _l_directions:
			    if d_tag.has_key(k_direction):
				_b_directionChecked = True
				buffer = metaUtils.get_matchedListFromAttrDict(ml_checkSub,cgmDirection = k_direction)
				if not buffer:raise StandardError,"Failed to find %s %s data"%(str_tag,k_direction)
				self.md_rigList[k_tag][k_direction] = buffer
				#self.log_info("%s - %s!]{%s}"%(k_tag,k_direction,buffer))
			if not _b_directionChecked:
			    self.md_rigList[k_tag] = ml_checkSub
			    if self.md_rigList[k_tag]:_b_directionChecked = True
			    #self.log_info("%s!]{%s}"%(k_tag,self.md_rigList[k_tag]))			    
			if not _b_directionChecked:
			    self.log_error("%s nothing checked"%(k_tag))
		    else:
			self.log_error("[{0} | Check toggle off]".format(k_tag))
		except Exception,error:raise StandardError,"['{0}' loop | error: {1}]".format(k_tag,error)
		
	    #>> Segment Joints --------------------------------------------------------------------------------------------------
	    self.md_rigList['uprLipSegment'] = {}
	    self.md_rigList['lwrLipSegment'] = {}
	    self.md_rigList['uprLipSegment']['left'] = mi_go._i_rigNull.msgList_get('uprLipSegmentLeft')
	    self.md_rigList['uprLipSegment']['right'] = mi_go._i_rigNull.msgList_get('uprLipSegmentRight')
	    
	    self.md_rigList['lwrLipSegment']['left'] = mi_go._i_rigNull.msgList_get('lwrLipSegmentLeft')
	    self.md_rigList['lwrLipSegment']['right'] = mi_go._i_rigNull.msgList_get('lwrLipSegmentRight') 
	    
	    
	    self.md_rigList['smileLineSegment'] = {}
	    self.md_rigList['smileLineSegment']['left'] = mi_go._i_rigNull.msgList_get('smileLineSegmentLeft')
	    self.md_rigList['smileLineSegment']['right'] = mi_go._i_rigNull.msgList_get('smileLineSegmentRight')	    
	    
	    
	    #>> Segment Joints --------------------------------------------------------------------------------------------------
	    self.md_rigList['squashSegmentLower']['center'] = mi_go._i_rigNull.msgList_get('lowerStretchSegment')
	    self.md_rigList['squashSegmentLower']['start'] = mi_go._i_rigNull.lowerStretchStartDriver
	    self.md_rigList['squashSegmentLower']['end'] = mi_go._i_rigNull.lowerStretchEndDriver

		       
	    #>> Lip Tigteners --------------------------------------------------------------------------------------------------
	    self.md_rigList['uprLipTightener'] = {}
	    self.md_rigList['lwrLipTightener'] = {}
	    self.md_rigList['uprLipTightener']['left'] = [self.md_rigList['lipCornerRig']['left'][0].uprDriver]
	    self.md_rigList['uprLipTightener']['right'] = [self.md_rigList['lipCornerRig']['right'][0].uprDriver]
	    
	    self.md_rigList['lwrLipTightener']['left'] = [self.md_rigList['lipCornerRig']['left'][0].lwrDriver]
	    self.md_rigList['lwrLipTightener']['right'] = [self.md_rigList['lipCornerRig']['right'][0].lwrDriver]
	       
	    #>> Calculate ==========================================================================
	    #Width of the skull plate...trying
	    self.f_offsetOfUpLoc = distance.returnBoundingBoxSizeToAverage(self.mi_skullPlate.mNode)

	    #>> Running lists ==========================================================================
	    self.ml_toVisConnect = []
	    self.ml_curves = []
	    self.md_attachReturns = {}
	    #self.report()
	    return True
	
	def _buildSkullDeformation_(self):
	    """
	    Plan of attack
	    1) See if we have stretch setup stuff
	    2) Build simple head def if not
	    """	    	    
	    try:#>> Get some data =======================================================================================
		mi_go = self._go#Rig Go instance link
		mi_skullPlate = self.mi_skullPlate  
		mi_uprTeethPlate = self.mi_uprTeethPlate   
		mi_lwrTeethPlate = self.mi_lwrTeethPlate    
		mi_browPlate = self.mi_browPlate 		
		mi_jawPlate = self.mi_jawPlate
		
		f_offsetOfUpLoc = self.f_offsetOfUpLoc
		mi_helper = self.mi_helper
		mi_parentHeadHandle = mi_go._mi_parentHeadHandle		
		mi_constrainNull =  mi_go._i_faceDeformNull
	    except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)
	    
	    try:#>> Setup =======================================================================================
		self._buildJawDeformation_()
	    except Exception,error:raise StandardError,"[Setup!| error: {0}]".format(error)
	    
	def _buildJawDeformation_(self):
	    try:#>> Get some data =======================================================================================
		mi_go = self._go#Rig Go instance link
		mi_skullPlate = self.mi_skullPlate  
		mi_uprTeethPlate = self.mi_uprTeethPlate   
		mi_lwrTeethPlate = self.mi_lwrTeethPlate    
		mi_browPlate = self.mi_browPlate 		
		mi_jawPlate = self.mi_jawPlate
		
		f_offsetOfUpLoc = self.f_offsetOfUpLoc
		mi_helper = self.mi_helper
		mi_parentHeadHandle = mi_go._mi_parentHeadHandle		
		mi_constrainNull =  mi_go._i_faceDeformNull
		mPlug_multpHeadScale = mi_go.mPlug_multpHeadScale
		
		self.d_buffer = {}
		d_ = self.d_buffer
		mi_jawPivotCrv = self.mi_jawPivotCrv
		mi_squashStartCrv = self.mi_squashStartCrv
		mi_jawHandle = self.md_rigList['jawHandle'][0]
		mi_jawRig = self.md_rigList['jawRig'][0]	
		mi_chinHandle = self.md_rigList['chin'][0]		
		mi_noseMoveHandle = self.md_rigList['noseMoveHandle'][0]
		mi_mouthMove = self.md_rigList['mouthMove'][0]
		
		f_lenJawLine = distance.returnCurveLength(self.mi_jawLineCrv.mNode)
		d_['f_lenJawLine'] = f_lenJawLine
		d_['mi_jawHandle'] = mi_jawHandle
		d_['mi_jawRig'] = mi_jawRig
		d_['mi_noseMoveHandle'] = mi_noseMoveHandle
		d_['mi_mouthMove'] = mi_mouthMove
	    except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)
	    
	    try:#>> Simple def =======================================================================================	
		try:#Dups
		    f_halfLen = f_lenJawLine/2
		    f_quarterLen = f_lenJawLine/4
		    f_eightLen = f_lenJawLine/8		    
		    #[f_quarterLen,0,0],[-f_quarterLen,0,0]
		    d_jointsToCreate = {'uprHeadDef':{'toDup':mi_squashStartCrv,'parent' : False,
		                                       'offsetChildren':[[0,f_halfLen,0]]},                        
		                        'faceBaseDef':{'toDup':mi_squashStartCrv,'parent' : mi_constrainNull},
		                        'stableNose':{'toDup':mi_noseMoveHandle,'parent': False},
		                        }
		    ml_skinJoints = []
		    for k_tag in d_jointsToCreate.iterkeys():
			try:#Query
			    d_sub = d_jointsToCreate[k_tag]
			    _d = {}
			    self.d_buffer = _d
			    str_tmp = "mi_%s"%k_tag
			    _d['str_tmp'] = str_tmp
			    _skin = d_sub.get('skin')
			    if _skin is None: _skin = True
			    _d['_skin'] = _skin
			except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)
			
			if d_sub.get('toDup'):
			    mJoint = cgmMeta.cgmObject(mc.joint(p = d_sub['toDup'].getPosition()),setClass=True)
			    mJoint.addAttr('cgmName',d_sub.get('name') or k_tag,lock=True)			
			    if _skin:mJoint.doStore('cgmTypeModifier','skullDef',True)
			    mJoint.doName()
			    mJoint = mJoint
			    mJoint.parent = d_sub.get('parent') or False
			    self.md_rigList[k_tag] = [mJoint]#Push back to rigList by tag
			    if _skin:ml_skinJoints.append(mJoint)
			    d_[str_tmp] = mJoint
			    mc.select(cl=True)
			elif d_sub.get('toUse'):
			    mJoint = d_sub.get('toUse')
			    d_[str_tmp] = mJoint
			    self.md_rigList[k_tag] = [mJoint]#Push back to rigList by tag
			    
			l_offsets = d_sub.get('offsetChildren') or []
			
			if l_offsets:
			    mi_loc =  mJoint.doLoc()
			    mi_loc.doGroup()
			    ml_children = [] 
			    
			    for i,pos in enumerate(l_offsets):
				self.log_info(pos) 
				mi_loc.translate = pos
				mObj = cgmMeta.cgmObject(mc.joint(p = mi_loc.getPosition()),setClass=True)
				mObj.parent = mJoint
				ml_children.append(mObj)
				mObj.doName()
				if _skin:ml_skinJoints.append(mObj)
			    mc.delete(mi_loc.parent)
			#self.log_infoNestedDict('d_buffer')
		    try:
			self.md_rigList['uprHeadDef'][0].parent = self.md_rigList['faceBaseDef'][0]
			self.md_rigList['stableNose'][0].parent = self.md_rigList['faceBaseDef'][0]			
			mi_jawRig.parent = self.md_rigList['faceBaseDef'][0]	
		    except Exception,error:raise StandardError,"[post parenting! | error: {0}]".format(error)
			
		except Exception,error:raise StandardError,"[def duplication! | error: {0}]".format(error)	
	    except Exception,error:raise StandardError,"[Simple Def ! | error: {0}]".format(error)	
	    
	    try:#Get Segment Data =======================================================================================
		ml_segment = self.md_rigList['squashSegmentLower']['center']
		mi_startInfluence = self.md_rigList['squashSegmentLower']['start']
		mi_endInfluence = self.md_rigList['squashSegmentLower']['end']
		
		#d_segReturn = rUtils.createSegmentCurve(ml_segment, addMidTwist = False, moduleInstance = mi_go._mi_module, connectBy = 'scale')
		
	    except Exception,error:raise StandardError,"[Get Segment data | error: {0}]".format(error) 	 
	    
	    try:#>> Build segment =======================================================================================
		d_segReturn = rUtils.createCGMSegment([i_jnt.mNode for i_jnt in ml_segment],
		                                      addSquashStretch = True,
		                                      addTwist = True,
		                                      influenceJoints = [mi_startInfluence,mi_endInfluence],
		                                      startControl = mi_startInfluence,
		                                      endControl = mi_endInfluence,
		                                      orientation = mi_go._jointOrientation,
		                                      baseName = 'lwrSegmentScale',
		                                      additiveScaleSetup = True,
		                                      connectAdditiveScale = True,		                                      
		                                      moduleInstance = mi_go._mi_module)
		
		try:#post create segmenet process
		    mi_curve = d_segReturn['mi_segmentCurve']
		    mi_anchorEnd = d_segReturn['mi_anchorEnd']
		    mi_anchorStart = d_segReturn['mi_anchorStart']
		    mi_go._i_rigNull.msgList_append(mi_curve,'segmentCurves','rigNull')	
		except Exception,error:raise StandardError,"[post segment query! | {0}]".format(error)
		
		try:#post segment parent
		    mi_curve.segmentGroup.parent = mi_go._i_rigNull.mNode
		    for attr in 'translate','scale','rotate':
			cgmMeta.cgmAttr(mi_curve,attr).p_locked = False
		    mi_curve.parent = mi_go._i_rigNull
		    
		    d_segReturn['ml_driverJoints'][0].parent = self.md_rigList['faceBaseDef'][0]	
		    d_segReturn['ml_drivenJoints'][0].parent = self.md_rigList['faceBaseDef'][0]	
		    mi_anchorEnd.parent = mi_jawHandle#...not sure what we want to parent to yet
		    mi_anchorStart.parent = self.md_rigList['faceBaseDef'][0]
		    
		except Exception,error:raise StandardError,"[post segment parent! | error: {0}]".format(error)
		
		self.d_buffer = d_segReturn
		#self.log_infoNestedDict('d_buffer')
	    except Exception,error:raise StandardError,"[cgmSegment creation | error: {0}]".format(error) 	 
	    			
	    try:#>>>Connect master scale =======================================================================================
		mi_distanceBuffer = mi_curve.scaleBuffer		
		cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn(mPlug_multpHeadScale.p_combinedShortName)    
	    except Exception,error:raise StandardError,"[segment scale connect! | error: {0}]".format(error)
	    
	    try:#Do a few attribute connections =======================================================================================
		#Push squash and stretch multipliers to cog
		try:
		    for k in mi_distanceBuffer.d_indexToAttr.keys():
			attrName = 'scaleMult_%s'%k
			cgmMeta.cgmAttr(mi_distanceBuffer.mNode,'scaleMult_%s'%k,keyable=1,hidden=0).doCopyTo(mi_jawHandle.mNode,attrName,connectSourceToTarget = True)
			cgmMeta.cgmAttr(mi_jawHandle.mNode,attrName,defaultValue = 1)
		except Exception,error:raise StandardError,"[scaleMult transfer! | error: {0}]".format(error)
		
		cgmMeta.cgmAttr(mi_curve,'twistType').doCopyTo(mi_jawHandle.mNode,connectSourceToTarget=True)
		cgmMeta.cgmAttr(mi_curve,'twistExtendToEnd').doCopyTo(mi_jawHandle.mNode,connectSourceToTarget=True)
		cgmMeta.cgmAttr(mi_curve,'scaleMidUp').doCopyTo(mi_jawHandle.mNode,connectSourceToTarget=True)
		cgmMeta.cgmAttr(mi_curve,'scaleMidOut').doCopyTo(mi_jawHandle.mNode,connectSourceToTarget=True)
	    except Exception,error:raise StandardError,"[segment attribute transfer! | error: {0}]".format(error)
	    
	    try:#>> Skin  =======================================================================================
		d_build = {'jawPlate':{'target':mi_jawPlate,'mi':4,'dr':9,
		                       'bindJoints':ml_skinJoints + ml_segment},
		           'lwrTeethPlate':{'target':mi_lwrTeethPlate,'mi':3,'dr':9,
		                            'bindJoints':[mi_jawRig]},
		           'uprTeethPlate':{'target':mi_uprTeethPlate,'mi':3,'dr':9,
		                            'bindJoints':self.md_rigList['uprHeadDef']}}
		self.skin_fromDict(d_build)
		
	    except Exception,error:raise StandardError,"[Skin skull!] | error: {0}".format(error)	
	    
	    try:#>> Connect  =======================================================================================
		mc.parentConstraint(mi_jawHandle.mNode,mi_jawRig.mNode)
		mc.scaleConstraint(mi_jawHandle.mNode,mi_jawRig.mNode)
		
		#ConnectVis
		#mi_go.connect_toRigGutsVis(self.md_rigList['faceBaseDef'],vis = True)#connect to guts vis switches
		
	    except Exception,error:raise StandardError,"[Connect!] | error: {0}".format(error)

	def _buildSimpleSkullDeformation_(self):
	    """
	    Plan of attack
	    1) See if we have stretch setup stuff
	    2) Build simple head def if not
	    """	    
	    try:#>> Get some data =======================================================================================
		mi_go = self._go#Rig Go instance link
		str_skullPlate = self.str_skullPlate
		f_offsetOfUpLoc = self.f_offsetOfUpLoc
		
		mi_helper = self.mi_helper
		mi_constrainNull =  mi_go._i_faceDeformNull
		
		self.d_buffer = {}
		d_ = self.d_buffer
		mi_jawPivotCrv = self.mi_jawPivotCrv
		mi_squashStartCrv = self.mi_squashStartCrv
		mi_jawHandle = self.md_rigList['jawHandle'][0]
		mi_jawRig = self.md_rigList['jawRig'][0]	
		mi_chinHandle = self.md_rigList['chin'][0]		
		mi_noseMoveHandle = self.md_rigList['noseMoveHandle'][0]
		mi_mouthMove = self.md_rigList['mouthMove'][0]
		
		f_lenJawLine = distance.returnCurveLength(self.mi_jawLineCrv.mNode)
		d_['f_lenJawLine'] = f_lenJawLine
		d_['mi_jawHandle'] = mi_jawHandle
		d_['mi_jawRig'] = mi_jawRig
		d_['mi_noseMoveHandle'] = mi_noseMoveHandle
		d_['mi_mouthMove'] = mi_mouthMove
		
	    except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)
	    
	    try:#>> Simple def=======================================================================================	
		try:#Dups
		    f_halfLen = f_lenJawLine/2
		    f_quarterLen = f_lenJawLine/4
		    f_eightLen = f_lenJawLine/8		    
		    #[f_quarterLen,0,0],[-f_quarterLen,0,0]
		    d_jointsToCreate = {'faceBaseDef':{'toDup':mi_squashStartCrv,'parent' : mi_constrainNull,
		                                       'offsetChildren':[[0,-f_quarterLen,-f_quarterLen]]},
		                        'stableJaw':{'toDup':mi_jawRig,'parent' : False,'skin':False,
		                                     'offsetChildren':[[0,0,f_quarterLen]]},		                        
		                        'uprHeadDef':{'toDup':mi_squashStartCrv,'parent' : False,
		                                      'offsetChildren':[[0,f_halfLen,0],[0,0,-f_halfLen],
		                                                        [f_quarterLen,0,-f_quarterLen],[-f_quarterLen,0,-f_quarterLen],
		                                                        [f_quarterLen,f_quarterLen,-f_quarterLen],[-f_quarterLen,f_quarterLen,-f_quarterLen],
		                                                        [f_quarterLen,f_eightLen,0],[-f_quarterLen,f_eightLen,0]]},		                        
		                        'jawDef':{'toUse':mi_jawRig,
		                                  'offsetChildren':[[f_quarterLen,0,0],[-f_quarterLen,0,0],
		                                                    [0,-f_quarterLen,f_quarterLen]]},		                        
		                        #'chinDef':{'toDup':mi_chinHandle,'parent': mi_jawRig},
		                        'stableNose':{'toDup':mi_noseMoveHandle,'parent': False},
		                        'mouthMoveDef':{'toDup':mi_mouthMove,'parent': mi_jawRig}}
		    ml_skinJoints = []
		    for k_tag in d_jointsToCreate.iterkeys():
			try:#Query
			    d_sub = d_jointsToCreate[k_tag]
			    _d = {}
			    self.d_buffer = _d
			    str_tmp = "mi_%s"%k_tag
			    _d['str_tmp'] = str_tmp
			    _skin = d_sub.get('skin')
			    if _skin is None: _skin = True
			    _d['_skin'] = _skin
			except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)
			
			if d_sub.get('toDup'):
			    mJoint = cgmMeta.cgmObject(mc.joint(p = d_sub['toDup'].getPosition()),setClass=True)
			    mJoint.addAttr('cgmName',d_sub.get('name') or k_tag,lock=True)			
			    if _skin:mJoint.doStore('cgmTypeModifier','skullDef',True)
			    mJoint.doName()
			    mJoint = mJoint
			    mJoint.parent = d_sub.get('parent') or False
			    self.md_rigList[k_tag] = [mJoint]#Push back to rigList by tag
			    if _skin:ml_skinJoints.append(mJoint)
			    d_[str_tmp] = mJoint
			    mc.select(cl=True)
			elif d_sub.get('toUse'):
			    mJoint = d_sub.get('toUse')
			    d_[str_tmp] = mJoint
			    self.md_rigList[k_tag] = [mJoint]#Push back to rigList by tag
			    
			l_offsets = d_sub.get('offsetChildren') or []
			
			if l_offsets:
			    mi_loc =  mJoint.doLoc()
			    mi_loc.doGroup()
			    ml_children = [] 
			    
			    for i,pos in enumerate(l_offsets):
				self.log_info(pos) 
				mi_loc.translate = pos
				mObj = cgmMeta.cgmObject(mc.joint(p = mi_loc.getPosition()),setClass=True)
				mObj.parent = mJoint
				ml_children.append(mObj)
				mObj.doName()
				if _skin:ml_skinJoints.append(mObj)
			    mc.delete(mi_loc.parent)
			#self.log_infoNestedDict('d_buffer')
		    try:
			self.md_rigList['uprHeadDef'][0].parent = self.md_rigList['faceBaseDef'][0]
			self.md_rigList['stableJaw'][0].parent = self.md_rigList['faceBaseDef'][0]
			self.md_rigList['stableNose'][0].parent = self.md_rigList['faceBaseDef'][0]			
			
			mi_jawRig.parent = self.md_rigList['faceBaseDef'][0]	
		    except Exception,error:raise StandardError,"[post parenting! | error: {0}]".format(error)
			
		except Exception,error:raise StandardError,"[def duplication! | error: {0}]".format(error)	
		
		#self.log_infoNestedDict('d_buffer')
	    except Exception,error:raise StandardError,"[Get Joints! | error: {0}]".format(error)	
	    '''
	    try:#>> Skin  =======================================================================================
		d_build = {'lwrLipBase':{'target':self.mi_skullPlate,'mi':5,'dr':9,
		                         'bindJoints':ml_skinJoints + [mi_jawRig]}}
		self.skin_fromDict(d_build)
		
	    except Exception,error:raise StandardError,"[Skin skull!] | error: {0}".format(error)	
	    '''
	    try:#>> Connect  =======================================================================================
		mc.parentConstraint(mi_jawHandle.mNode,mi_jawRig.mNode)
		mc.scaleConstraint(mi_jawHandle.mNode,mi_jawRig.mNode)
		
		#ConnectVis
		mi_go.connect_toRigGutsVis(self.md_rigList['faceBaseDef'],vis = True)#connect to guts vis switches
		
	    except Exception,error:raise StandardError,"[Connect!] | error: {0}".format(error)
	    
	    try:#>> StableJaw  =======================================================================================
		mc.orientConstraint(mi_jawRig.mNode,self.md_rigList['stableJaw'][0].mNode,skip = ["%s"%mi_go._jointOrientation[2]])
		mc.pointConstraint(mi_jawRig.mNode,self.md_rigList['stableJaw'][0].mNode,skip = ["%s"%str_axis for str_axis in [mi_go._jointOrientation[0],mi_go._jointOrientation[1]]])		
		self.md_rigList['stableJaw'][0].rotateOrder = mi_go._jointOrientation
	    except Exception,error:raise StandardError,"[Stable!] | error: {0}".format(error)
	    
	def _buildAttachSurfaces_(self):
	    #>> Get some data =======================================================================================
	    """
	    For each of our curves, we're gonna
	    1) get them,
	    2) rebuild them (in case they've been messed with
	    3) cast our surfaces 
	    4)name and store them
	    """
	    mi_go = self._go#Rig Go instance link
	    int_spans = 4
	    '''
	    def returnRebuiltCurveString(crv):
		try:crv.mNode
		except:crv = cgmMeta.cgmObject(crv)
		
		return mc.rebuildCurve (crv.mNode, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=int_spans, d=3, tol=0.001)[0]		
	    '''
	    try:#Ribbons -----------------------------------------------------------------------------	    
		md_ribbonBuilds = {'nostril':{'extrudeCrv':self.mi_noseBaseCastCrv,
		                              'joints':self.md_rigList['sneerHandle']['left'] + self.md_rigList['sneerHandle']['right']},
		                   'uprLip':{'extrudeCrv':self.mi_lipUprCrv,
		                              'joints':self.md_rigList['lipCorner']['left'] + self.md_rigList['lipCorner']['right']},
		                   'lwrLip':{'extrudeCrv':self.mi_lipLwrCrv,
		                             'joints':self.md_rigList['lipCorner']['left'] + self.md_rigList['lipCorner']['right']},		                   
		                   'smileLeft':{'extrudeCrv':self.mi_smileLeftCrv,'mode':'radialLoft','direction':'left',
		                                'aimObj':self.md_rigList['mouthMove'][0]},
		                   'smileRight':{'extrudeCrv':self.mi_smileRightCrv,'mode':'radialLoft','direction':'right',
		                                 'aimObj':self.md_rigList['mouthMove'][0]},		                   
		                  }
		
		self.progressBar_setMaxStepValue(len(md_ribbonBuilds.keys()))		
		for str_name in md_ribbonBuilds.iterkeys():
		    try:
			self.progressBar_iter(status = ("Ribbon build: '%s'"%str_name))			
			d_buffer = md_ribbonBuilds[str_name]#get the dict
			self.d_buffer = d_buffer
			f_dist = mi_go._f_skinOffset*.5
			
			if d_buffer.get('mode') == 'radialLoft':
			    try:mi_obj = surfUtils.create_radialCurveLoft(d_buffer['extrudeCrv'].mNode,d_buffer['aimObj'].mNode,f_dist)
			    except Exception,error:raise StandardError,"[Radial Loft |error: {0}]".format(error)
			else:
			    try:#Regular loft -----------------------------------------------------------------------
				ml_joints = d_buffer['joints']
				mi_crv = d_buffer['extrudeCrv']

				try:#Make our loft loc -----------------------------------------------------------------------
				    #f_dist = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_joints])*.05
				    d_buffer['dist'] = f_dist
				    
				    mi_loc = ml_joints[-1].doLoc()
				    mi_loc.doGroup()
				except Exception,error:raise StandardError,"[loft loc |error: {0}]".format(error)
				
				try:#Cross section creation -----------------------------------------------------------------------
				    l_profileCrvPos = []
				    for dist in [0,f_dist]:
					mi_loc.__setattr__("t%s"%mi_go._jointOrientation[1],dist)
					l_profileCrvPos.append(mi_loc.getPosition())
					
				    str_profileCrv = mc.curve(d = 1,ep = l_profileCrvPos, os = True)
				except Exception,error:raise StandardError,"[Cross section creation |error: {0}]".format(error)
				
				try:#Extrude crv -----------------------------------------------------------------------
				    str_extruded = mc.extrude([str_profileCrv,mi_crv.mNode],et = 1, sc = 1,ch = 1,useComponentPivot = 0,fixedPath=1)[0]
				    mi_obj = cgmMeta.cgmObject(str_extruded)
				    mc.delete(mi_loc.parent,str_profileCrv)
				except Exception,error:raise StandardError,"[Extrude crv |error: {0}]".format(error)	
			    except Exception,error:raise StandardError,"[Regular loft | error: {0}]".format(error)
			try:
			    self.__dict__['mi_%sRibbon'%(str_name)] = mi_obj
			    mi_obj.addAttr('cgmName',str_name,lock=True)
			    mi_obj.addAttr('cgmTypeModifier','ribbon',lock=True)			    
			    try:mi_obj.addAttr('cgmDirection',d_buffer['direction'] ,lock=True)
			    except:pass
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sRibbon"%str_name,'module')			    
			except Exception,error:raise StandardError,"[Naming |error: {0}]".format(error)
			#self.log_infoNestedDict('d_buffer')
			
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)
	    except Exception,error:raise StandardError,"[Ribbons |error: {0}]".format(error)
	    
	    
	    try:#Main plates -----------------------------------------------------------------------------
		md_plateBuilds = {'nose':{'crvs':[self.mi_noseTopCastCrv,self.mi_noseMidCastCrv,self.mi_noseBaseCastCrv,self.mi_mouthTopCastCrv]},
		                  'uprLip':{'crvs':[self.mi_mouthTopCastCrv,self.mi_lipOverTraceCrv,self.mi_lipUprCrv]},
		                  'lwrLip':{'crvs':[self.mi_lipLwrCrv,self.mi_lipUnderTraceCrv,self.mi_mouthLowCastCrv]},
		                  'leftCheek':{'mode':'cheekLoft','direction':'left','name':'cheek',
		                               'smileCrv':self.mi_smileLeftCrv,
		                               },
		                  'rightCheek':{'mode':'cheekLoft','direction':'right','name':'cheek',
		                               'smileCrv':self.mi_smileRightCrv,
		                               }}
		
		self.progressBar_setMaxStepValue(len(md_plateBuilds.keys()))
		for str_name in md_plateBuilds.iterkeys():
		    try:
			self.progressBar_iter(status = ("Plate build: '%s'"%str_name))						
			d_buffer = md_plateBuilds[str_name]#get the dict
			self.d_buffer = d_buffer
			
			if d_buffer.get('mode') == 'cheekLoft':
			    try:#Cheek loft
				l_deleteBuffer = []
				str_direction = d_buffer['direction']
				str_name = d_buffer['name']
				mi_smileCrv = d_buffer['smileCrv']
				d_buffer['uprCheekJoints'] = self.md_rigList['uprCheekRig'][str_direction]
				d_buffer['cheekJoints'] = self.md_rigList['cheekRig'][str_direction]				
				d_buffer['jawLineJoints'] = self.md_rigList['jawLine'][str_direction]
				d_buffer['sneerHandle'] = self.md_rigList['sneerHandle'][str_direction][0]
				d_buffer['smileBaseHandle'] = self.md_rigList['smileBaseHandle'][str_direction][0]				
				    
				try:#Build our rail curves
				    l_railCrvs = []
				    ml_uprCheekRev = copy.copy(d_buffer['uprCheekJoints'])
				    ml_uprCheekRev.reverse()
				    ml_jawLineRev = copy.copy(d_buffer['jawLineJoints'])
				    ml_jawLineRev.reverse()
				    
				    ml_startRailObjs = [d_buffer['sneerHandle']] + ml_uprCheekRev
				    ml_endRailObjs = [d_buffer['smileBaseHandle']] + ml_jawLineRev
				    self.log_info("startRailObjs: %s"%[mObj.p_nameShort for mObj in ml_startRailObjs])
				    self.log_info("endRailObjs: %s"%[mObj.p_nameShort for mObj in ml_endRailObjs])
				    self.log_info("cheekJoints: %s"%[mObj.p_nameShort for mObj in d_buffer['cheekJoints']])
				    
				    str_startRailCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_startRailObjs], os = True)
				    str_endRailCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endRailObjs], os = True)
				    
				    #str_startRailCrv = mc.rebuildCurve (str_startRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    #str_endRailCrv = mc.rebuildCurve (str_endRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    str_startRailCrv = self.returnRebuiltCurveString(str_startRailCrv,5,1)
				    str_endRailCrv = self.returnRebuiltCurveString(str_endRailCrv,5,1)
				    
				except Exception,error:raise StandardError,"[Rail curve build |error: {0}]".format(error)
				
				try:				    
				    ml_endProfileObjs = [ml_startRailObjs[-1],d_buffer['cheekJoints'][0], ml_endRailObjs[-1]]
				    self.log_info("endProfileObjs: %s"%[mObj.p_nameShort for mObj in ml_endProfileObjs])
				    str_endProfileCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endProfileObjs], os = True)
				    str_startProfileCrv = mc.rebuildCurve (mi_smileCrv.mNode, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    str_endProfileCrvRebuilt = mc.rebuildCurve (str_endProfileCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]
				    
				except Exception,error:raise StandardError,"[Profile curves build |error: {0}]".format(error)	
				
				try:
				    str_loft = mc.doubleProfileBirailSurface( str_startProfileCrv, str_endProfileCrvRebuilt,
				                                              str_startRailCrv, str_endRailCrv, 
				                                              blendFactor = .5,constructionHistory=0, object=1, polygon=0, transformMode=0)[0]
				except Exception,error:raise StandardError,"[birail create |error: {0}]".format(error)	
				
				mc.delete([str_startProfileCrv,str_startRailCrv,str_endRailCrv,str_endProfileCrv])#Delete the rebuilt curves
			    except Exception,error:raise StandardError,"[Reg plate loft |error: {0}]".format(error)	
			else:
			    try:#Reg curve loft
				l_crvsRebuilt = []
				for mi_crv in d_buffer['crvs']:#rebuild crvs
				    l_crvsRebuilt.append(self.returnRebuiltCurveString(mi_crv,4))
				
				str_loft = mc.loft(l_crvsRebuilt,uniform = True,degree = 3,ss = 3)[0]
				mc.delete(l_crvsRebuilt)#Delete the rebuilt curves
			    except Exception,error:raise StandardError,"[Reg plate loft |error: {0}]".format(error)	
			
			try:#tag, name, store
			    mi_obj = cgmMeta.cgmObject(str_loft)
			    self.__dict__['mi_%sPlate'%(str_name)] = mi_obj
			    mi_obj.addAttr('cgmName',d_buffer.get('name') or str_name,lock=True)
			    try:mi_obj.addAttr('cgmDirection',str_direction ,lock=True)
			    except:pass
			    mi_obj.addAttr('cgmTypeModifier','plate',lock=True)					    
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sPlate"%str_name,'module')
			except Exception,error:raise StandardError,"[Tag/Name/Store |error: {0}]".format(error)	
			
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)	
		    #self.log_infoNestedDict('d_buffer')		    
	    except Exception,error:raise StandardError,"[Plate |error: {0}]".format(error)
	    
		
	def _buildTongue_(self):
	    """
	    Stuff to setup...
	    1) attach base to skull plate
	    2) What should
	    """
	    try:#>> Get some initial data =======================================================================================
		mi_go = self._go#Rig Go instance link
		mi_tongueBase = self.md_rigList['tongueBase'][0]
		mi_tongueTip = self.md_rigList['tongueTip'][0]
		ml_tongueRig = self.md_rigList['tongueRig']
		mi_jawRig = self.md_rigList['jawRig'][0]
		mi_jawHandle = self.md_rigList['jawHandle'][0]
		mPlug_multpHeadScale = mi_go.mPlug_multpHeadScale
		
		str_capAim = mi_go._jointOrientation[0].capitalize()
		str_partName = mi_go._partName
		self.d_buffer['mi_tongueBase'] = mi_tongueBase
		self.d_buffer['mi_tongueTip'] = mi_tongueTip
		self.d_buffer['ml_tongueRig'] = ml_tongueRig
		self.d_buffer['str_capAim'] = str_capAim
		self.d_buffer['mi_jawRig'] = mi_jawRig
		self.d_buffer['mi_jawHandle'] = mi_jawHandle
		self.d_buffer['mPlug_multpHeadScale'] = mPlug_multpHeadScale
		
		#self.log_infoNestedDict('d_buffer')
	    except Exception,error:raise StandardError,"[Info Gather! | error: {0}]".format(error)
	    
	    try:#>> Build segment =======================================================================================
		#Create segment	
		mi_tongueBase.masterGroup.parent = mi_jawHandle
		mi_tongueTip.masterGroup.parent = mi_jawHandle	
		_str_baseParentBuffer = mi_tongueBase.parent
		_str_tipParentBuffer = mi_tongueTip.parent
		
		d_segReturn = rUtils.createCGMSegment([i_jnt.mNode for i_jnt in ml_tongueRig],
		                                      addSquashStretch = True,
		                                      addTwist = True,
		                                      influenceJoints = [mi_tongueBase,mi_tongueTip],
		                                      startControl = mi_tongueBase,
		                                      endControl = mi_tongueTip,
		                                      orientation = mi_go._jointOrientation,
		                                      baseName = 'tongue',
		                                      additiveScaleSetup = True,
		                                      connectAdditiveScale = True,
		                                      moduleInstance = mi_go._mi_module)
		
		try:#post create segmenet process
		    mi_curve = d_segReturn['mi_segmentCurve']
		    mi_anchorEnd = d_segReturn['mi_anchorEnd']
		    mi_anchorStart = d_segReturn['mi_anchorStart']
		    
		    mi_go._i_rigNull.msgList_connect([mi_curve],'segmentCurves','rigNull')	
		except Exception,error:raise StandardError,"[post segment query! | error: {0}]".format(error)
		
		try:#post segmentparent
		    mi_curve.segmentGroup.parent = mi_go._i_rigNull.mNode
		    for attr in 'translate','scale','rotate':
			cgmMeta.cgmAttr(mi_curve,attr).p_locked = False
		    mi_curve.parent = mi_go._i_rigNull
		    
		    mi_anchorEnd.parent = _str_tipParentBuffer
		    mi_anchorStart.parent = _str_baseParentBuffer
		
		except Exception,error:raise StandardError,"[post segment parent! | error: {0}]".format(error)
		
		self.d_buffer = d_segReturn
		#self.log_infoNestedDict('d_buffer')
				
		'''
		midReturn = rUtils.addCGMSegmentSubControl(ml_influenceJoints[1].mNode,
		                                           segmentCurve = i_curve,
		                                           baseParent=ml_influenceJoints[0],
		                                           endParent=ml_influenceJoints[-1],
		                                           midControls=ml_segmentHandles[1],
		                                           baseName=self._partName,
		                                           controlTwistAxis =  'r'+self._jointOrientation[0],
		                                           orientation=self._jointOrientation)
		for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
		    i_grp.parent = mi_cog.mNode	 '''   
	    except Exception,error:raise StandardError,"[cgmSegment creation! | error: {0}]".format(error)
	    
	    try:#>>>Connect master scale
		mi_distanceBuffer = mi_curve.scaleBuffer		
		cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn(mPlug_multpHeadScale.p_combinedShortName)    
	    except Exception,error:raise StandardError,"[segment scale connect! | error: {0}]".format(error)
	    
	    try:#Do a few attribute connections
		#Push squash and stretch multipliers to cog
		try:
		    for k in mi_distanceBuffer.d_indexToAttr.keys():
			attrName = 'scaleMult_%s'%k
			cgmMeta.cgmAttr(mi_distanceBuffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_tongueTip.mNode,attrName,connectSourceToTarget = True)
			cgmMeta.cgmAttr(mi_tongueTip.mNode,attrName,defaultValue = 1)
			cgmMeta.cgmAttr('cog_anim',attrName, keyable =True, lock = False)    
		except Exception,error:raise StandardError,"[scaleMult transfer! | error: {0}]".format(error)
		
		cgmMeta.cgmAttr(mi_curve,'twistType').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
		cgmMeta.cgmAttr(mi_curve,'twistExtendToEnd').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
		cgmMeta.cgmAttr(mi_curve,'scaleMidUp').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
		cgmMeta.cgmAttr(mi_curve,'scaleMidOut').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
		
	    except Exception,error:raise StandardError,"[segment attribute transfer! | error: {0}]".format(error)

	    
	    try:#>>DynParent ====================================================================================
		ml_tongueDynParents = [mi_jawRig, self.md_rigList['uprHeadDef'][0]]		    
		self.log_info("Dynamic parents to add: %s"%([i_obj.getShortName() for i_obj in ml_tongueDynParents]))
		
		#Add our parents
		mi_dynGroup = mi_tongueTip.dynParentGroup
		mi_dynGroup.dynMode = 0
		
		for o in ml_tongueDynParents:
		    mi_dynGroup.addDynParent(o)
		mi_dynGroup.rebuild()
		
	    except Exception,error:raise StandardError,"[DynParent fail!] | error: {0}".format(error)
	  
    
	def _buildNose_(self):
	    #>> Get some data =======================================================================================
	    """
	    Stuff to setup...
	    1) attach base to skull plate
	    2) What should
	    TODO:
	    1) Nose aiming -under, top
	    2) Nostril joints orienting -- feels off

	    """	    
	    try:#>> Query ========================================================================
		mi_go = self._go#Rig Go instance link	
	    except Exception,error:raise StandardError,"[Query] | error: {0}".format(error)
	    
	    try:#Build Ribbons --------------------------------------------------------------------------------------
		md_ribbonBuilds = {'nostril':{'extrudeCrv':self.mi_noseBaseCastCrv,
		                              'joints':self.md_rigList['sneerHandle']['left'] + self.md_rigList['sneerHandle']['right']}}	
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"[Ribbons! | error: {0}]".format(error)
		
	    try:#Build plates --------------------------------------------------------------------------------------
		md_plateBuilds = {'nose':{'crvs':[self.mi_noseTopCastCrv,self.mi_noseMidCastCrv,self.mi_noseBaseCastCrv,self.mi_mouthTopCastCrv]}}
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"[Plates! | error: {0}]".format(error)
	    
	    try:#Special Locs --------------------------------------------------------------------------------------
		try:#Make a noseMove track loc
		    mi_noseMoveTrackLoc = self.md_rigList['noseMoveHandle'][0].doLoc()
		    i_masterGroup = (cgmMeta.cgmObject(mi_noseMoveTrackLoc.doGroup(True),setClass=True))
		    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
		    i_masterGroup.doName()
		    mi_noseMoveTrackLoc.connectChildNode(i_masterGroup,'masterGroup','groupChild')
		    self.md_rigList['noseMoveTrackLoc'] = [mi_noseMoveTrackLoc]
		    mi_go.connect_toRigGutsVis(mi_noseMoveTrackLoc,vis = 1, doShapes = True)#connect to guts vis switches
		    
		    i_masterGroup.parent = mi_go._i_deformNull
		except Exception,error:raise StandardError,"[NoseMove master group find fail |error: {0}]".format(error)
		    		
		try:str_noseMoveTrackerMasterGroup = self.md_rigList['noseMoveTrackLoc'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"[NoseMoveTrack master group find fail | error: {0}]".format(error)
		
	    except Exception,error:raise StandardError,"[Special Locs!] | error: {0}".format(error)	    
	    
	    try:#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_nosePlate = self.mi_nosePlate.p_nameShort
		str_nostrilRibbon = self.mi_nostrilRibbon.p_nameShort	    
		try:str_noseMoveMasterGroup = self.md_rigList['noseMoveRig'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"[NoseMove master group find fail |error: {0}]".format(error)
		
		mi_uprTeethPlate = cgmMeta.cgmObject('uprTeethPlate')  
		str_uprTeethPlate = self.mi_uprTeethPlate.p_nameShort
		mi_lwrTeethPlate = cgmMeta.cgmObject('lwrTeethPlate')   
		str_skullPlate = self.mi_browPlate.mNode
		self.str_skullPlate#jaw plate
		#'nostrilHandle':{'attachTo':str_nosePlate,'mode':'handleAttach'}
		'''
		'noseMoveRig':{'mode':'blendAttachStable','defaultValue':0,'followSuffix':'Jaw','controlObj':mi_noseMoveTrackLoc,
			       'target0':mi_noseMoveTrackLoc},'''		
		d_build = {'nostrilRig':{'attachTo':str_nosePlate,
		                         0:{'mode':'slideAttach','attachTo':self.mi_jawPlate}},
		           'noseMoveTrackLoc':{'attachTo':str_uprTeethPlate},		           		           
		           'nostrilHandle':{'attachTo':str_nostrilRibbon,'mode':'handleAttach'},
		           'noseMoveHandle':{'mode':'blendAttachStable','defaultValue':0,'followSuffix':'Jaw',
		                             'target0':self.md_rigList['stableNose'][0]},	           
		           'noseMoveRig':{'mode':'parentOnly','attachTo':None,'parentTo':mi_noseMoveTrackLoc.masterGroup},

		           'noseTipRig':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseTipHandle'][0]},
		           'noseTipHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_noseMoveTrackLoc},
		           'noseUnderRig':{'attachTo':str_uprTeethPlate},
		           #'noseUnderHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_noseMoveTrackLoc.mNode},
		           'noseUnderHandle':{'attachTo':str_uprTeethPlate,'controlObj':mi_noseMoveTrackLoc},
		           'noseTopRig':{'attachTo':self.mi_browPlate},
		           'noseTopHandle':{'mode':'handleAttach'}
		           }
		self.attach_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Attach! | error: {0}]".format(error)
	    
	    try:#Build Ribbons --------------------------------------------------------------------------------------
		md_ribbonBuilds = {'nostril':{'extrudeCrv':self.mi_noseBaseCastCrv,
		                              'joints':self.md_rigList['sneerHandle']['left'] + self.md_rigList['sneerHandle']['right']}}	
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"[Ribbons! | error: {0}]".format(error)
		
	    try:#Build plates --------------------------------------------------------------------------------------
		md_plateBuilds = {'nose':{'crvs':[self.mi_noseTopCastCrv,self.mi_noseMidCastCrv,self.mi_noseBaseCastCrv,self.mi_mouthTopCastCrv]}}
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"[Plates! | error: {0}]".format(error)	 
	    
	    try:#>> Skin nose  =======================================================================================
		self.progressBar_setMaxStepValue(4)		
		try:#Build list
		    self.progressBar_set(status = "Skinning Nose", step = 1)
		    l_toBind = [str_nosePlate]	
		    'noseMoveHandle','noseUnderHandle'
		    for tag in ['noseTipRig','noseTopRig','noseMoveHandle','noseUnderRig']:
			l_toBind.append(self.md_rigList[tag][0].p_nameShort)
		    for tag in ['nostrilHandle']:#'smileLineRig',
			for str_side in 'left','right':
			    l_toBind.append(self.md_rigList[tag][str_side][0].mNode)
		except Exception,error:raise StandardError,"[build list |error: {0}]".format(error)
		
		ret_cluster = mc.skinCluster(l_toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
		i_cluster = cgmMeta.cgmNode(ret_cluster[0],setClass=True)
		i_cluster.doStore('cgmName',str_nosePlate)
		i_cluster.doName()
		
	    except Exception,error:raise StandardError,"[Skin nose plate| error: {0}]".format(error)		
	    
	    try:#>> Skin nostril Move =======================================================================================
		try:#Build list
		    self.progressBar_set(status = "Skinning Nostril", step = 2)
		    
		    l_toBind = [str_nostrilRibbon]	
		    for tag in ['noseTipRig','noseMoveHandle','noseUnderRig']:
			l_toBind.append(self.md_rigList[tag][0].p_nameShort)
		    for str_direction in 'left','right':
			l_toBind.append( self.md_rigList['nostrilRig'][str_direction][0].mNode )
		    #for tag in ['smileLineRig']:
			#for str_side in 'left','right':
			    #l_toBind.append(self.md_rigList[tag][str_side][0].p_nameShort)
		except Exception,error:raise StandardError,"[build list |error: {0}]".format(error)
		
		ret_cluster = mc.skinCluster(l_toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
		i_cluster = cgmMeta.cgmNode(ret_cluster[0],setClass=True)
		i_cluster.doStore('cgmName',str_nostrilRibbon)
		i_cluster.doName()
		
	    except Exception,error:raise StandardError,"[Skin nostril plate! | error: {0}]".format(error)	
	    
	    
	    try:#>> Connect rig joints to handles ====================================================
		mi_go = self._go#Rig Go instance link
		d_build = {#'noseMove':{},
		           'noseUnderHandle':{'mode':'pointBlend','targets':[mi_noseMoveTrackLoc]},		           
		           'noseMoveTrackLoc':{'driver':self.md_rigList['noseMoveHandle']}}
		self.connect_fromDict(d_build)	
		
		
		try:#>> Connect corners
		    for str_direction in 'left','right':
			mi_jnt = self.md_rigList['nostrilRig'][str_direction][0]
			mi_controlLoc = self.md_attachReturns[mi_jnt]['controlLoc']
			mi_controlLoc.parent = self.md_rigList['sneerHandleInfluenceJoints'][str_direction][0]
		except Exception,error:raise StandardError,"[Connect Corners] | error: {0}".format(error)	

		d_build = {#'noseMove':{},
		           'noseTop':{},
		           'noseUnder':{}}
		
		self.progressBar_setMaxStepValue(len(d_build.keys()))
		for str_tag in d_build.iterkeys():
		    try:
			self.progressBar_iter(status = "Connecting: '%s'"%str_tag)			
			try:#Get ----------------------------------------------------
			    mi_handle = self.md_rigList[str_tag+'Handle'][0]
			    mi_rigJoint = self.md_rigList[str_tag+'Rig'][0]
			except Exception,error:raise StandardError,"[Quer]{ %s}"%(error)			
			
			try:#Connect the control loc to the center handle
			    mi_controlLoc = self.md_attachReturns[mi_rigJoint]['controlLoc']
			    mc.pointConstraint(mi_handle.mNode,mi_controlLoc.mNode)
			except Exception,error:raise StandardError,"[Control loc connec] | error: {0}".format(error)			
		    
			try:#Setup the offset to push handle rotation to the rig joint control
			    #Create offsetgroup for the mid
			    mi_offsetGroup = cgmMeta.cgmObject( mi_rigJoint.doGroup(True),setClass=True)	 
			    mi_offsetGroup.doStore('cgmName',mi_rigJoint.mNode)
			    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
			    mi_offsetGroup.doName()
			    mi_rigJoint.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
			    
			    cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
			except Exception,error:raise StandardError,"[Offset group] | error: {0}".format(error)
		    except Exception,error:  raise StandardError,"%s | %s"%(str_tag,error)
		    
	    except Exception,error:  raise StandardError,"[Connect] | error: {0}".format(error)	
	    '''
	    try:#>> Nose Move =======================================================================================
		self.progressBar_set(status = "Setting up nose move")
		
		mi_handle = self.md_rigList['noseMoveHandle'][0]
		mi_rigJoint = self.md_rigList['noseMoveRig'][0]
		
		try:#Connect the control loc to the center handle
		    mi_controlLoc = self.md_attachReturns[mi_rigJoint]['controlLoc']
		    mc.pointConstraint(mi_handle.mNode,mi_controlLoc.mNode)
		except Exception,error:raise StandardError,"[Control loc connec]{ %s}"%(error)	
		
		try:#Setup the offset to push handle rotation to the rig joint control
		    #Create offsetgroup for the mid
		    mi_offsetGroup = cgmMeta.cgmObject( mi_rigJoint.doGroup(True),setClass=True)	 
		    mi_offsetGroup.doStore('cgmName',mi_rigJoint.mNode)
		    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		    mi_offsetGroup.doName()
		    mi_rigJoint.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
		    cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
		except Exception,error:raise StandardError,"[Offset grou]{ %s}"%(error)
	    except Exception,error:raise StandardError,"[Nose Move setup] | error: {0}".format(error)
	    '''
	    try:#>> Nose Move Up Loc =======================================================================================
		self.progressBar_set(status = "Setting up nose move up loc")
		mi_noseMove = self.md_rigList['noseMoveHandle'][0]
		mi_noseMoveUpLoc = mi_noseMove.doLoc()
		mi_noseMoveUpLoc.parent = mi_noseMove.masterGroup
		self.md_rigList['noseMoveUpLoc'] = [mi_noseMoveUpLoc]
		mi_noseMove.connectChildNode(mi_noseMoveUpLoc,'handleUpLoc','owner')
		mi_noseMoveUpLoc.__setattr__("t%s"%mi_go._jointOrientation[0],self.f_offsetOfUpLoc)
		mi_go.connect_toRigGutsVis(mi_noseMoveUpLoc,vis = True)#connect to guts vis switches
	    except Exception,error:raise StandardError,"[Nose Move Up Loc] | error: {0}".format(error)
	    
	    try:#>>> Aim some stuff =================================================================================
		'''
		try:mi_noseUnderTarget = self.md_rigList.get('lipOverRig').get('center')[0]
		except Exception,error:
		    self.log_error("[First nose under target fail. Using alternate]{%s}"%error)
		    mi_noseUnderTarget = self.md_rigList['lipRig']['center'][0]'''
		
		#mi_noseUnderTarget = self.md_rigList.get('lipUprHandle').get('center')[0]
		mi_noseUnderTarget = self.md_rigList.get('mouthMove')[0]		
		d_build = {'noseUnderRig':{'mode':'singleTarget','v_aim':mi_go._vectorUpNegative,'v_up':mi_go._vectorAim,
		                           'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseUnderTarget},
		           'noseTopRig':{'mode':'singleTarget','v_aim':mi_go._vectorUpNegative,'v_up':mi_go._vectorAim,
		                         'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseMove}}		           
		self.d_buffer = d_build
		#self.log_infoNestedDict('d_buffer')
		self.aim_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Aim Setup] | error: {0}]".format(error)
	    
	def _buildMouthHandles_(self):
	    try:#>> Query ========================================================================
		mi_go = self._go#Rig Go instance link	
		mi_mouthMove = self.md_rigList['mouthMove'][0]
	    except Exception,error:raise StandardError,"[Query] | error: {0}]".format(error)
	    
	    try:#Special Locs ====================================================================================
		try:#Make a mouthMove track loc ====================================================================================
		    mi_mouthMoveTrackLoc = self.md_rigList['mouthMove'][0].doLoc()
		    mi_mouthMoveTrackLoc.addAttr('cgmTypeModifier','track',lock=True)
		    mi_mouthMoveTrackLoc.doName()		
		    
		    mi_masterGroup = (cgmMeta.cgmObject(mi_mouthMoveTrackLoc.doGroup(True),setClass=True))
		    mi_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
		    mi_masterGroup.doName()
		    mi_mouthMoveTrackLoc.connectChildNode(mi_masterGroup,'masterGroup','groupChild')
		    self.md_rigList['mouthMoveTrackLoc'] = [mi_mouthMoveTrackLoc]
		    mi_go.connect_toRigGutsVis(mi_mouthMoveTrackLoc,vis = 1, doShapes = True)#connect to guts vis switches
		    mi_masterGroup.parent = mi_go._i_deformNull
		except Exception,error:raise StandardError,"[MouthMove loc| error: {0}]".format(error)
				
		try:str_mouthMoveTrackerMasterGroup = self.md_rigList['mouthMoveTrackLoc'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"[MouthMoveTrack master group find fail | error: {0}]".format(error)
		
		try:#Make a mouthMove track loc ====================================================================================
		    mi_mouthMoveJawTrackLoc = self.md_rigList['mouthMove'][0].doLoc()
		    mi_mouthMoveJawTrackLoc.addAttr('cgmTypeModifier','trackJaw',lock=True)
		    mi_mouthMoveJawTrackLoc.doName()		
		    
		    mi_masterGroup = (cgmMeta.cgmObject(mi_mouthMoveJawTrackLoc.doGroup(True),setClass=True))
		    mi_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
		    mi_masterGroup.doName()
		    mi_mouthMoveJawTrackLoc.connectChildNode(mi_masterGroup,'masterGroup','groupChild')
		    self.md_rigList['mouthMoveJawTrackLoc'] = [mi_mouthMoveJawTrackLoc]
		    mi_go.connect_toRigGutsVis(mi_mouthMoveJawTrackLoc,vis = 1, doShapes = True)#connect to guts vis switches
		    mi_masterGroup.parent = mi_go._i_deformNull
		except Exception,error:raise StandardError,"[MouthMove loc| error: {0}]".format(error)
				
		try:str_mouthMoveJawTrackerMasterGroup = self.md_rigList['mouthMoveJawTrackLoc'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"[MouthMoveTrack master group find fail | error: {0}]".format(error)					
		
		try:#Make a chin track loc
		    mi_chinTrackLoc = self.md_rigList['chin'][0].doLoc()
		    mi_chinTrackLoc.addAttr('cgmTypeModifier','track',lock=True)
		    mi_chinTrackLoc.doName()		
		    
		    mi_masterGroup = (cgmMeta.cgmObject(mi_chinTrackLoc.doGroup(True),setClass=True))
		    mi_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
		    mi_masterGroup.doName()
		    mi_chinTrackLoc.connectChildNode(mi_masterGroup,'masterGroup','groupChild')
		    self.md_rigList['chinTrackLoc'] = [mi_chinTrackLoc]
		    
		    mi_go.connect_toRigGutsVis(mi_chinTrackLoc,vis = True)#connect to guts vis switches
		    mi_masterGroup.parent = mi_go._i_deformNull
		except Exception,error:raise StandardError,"[ChinTrack master group find fail |error: {0}]".format(error)
		    		
		try:str_chinTrackerMasterGroup = self.md_rigList['chinTrackLoc'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"[ChinTrack master group find fail |error: {0}]".format(error)			
	    except Exception,error:raise StandardError,"[Special Locs!] | error: {0}]".format(error)

	    try:#Attach stuff to surfaces ====================================================================================
		#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_skullPlate = self.str_skullPlate
		mi_uprTeethPlate = self.mi_uprTeethPlate
		mi_lwrTeethPlate = self.mi_lwrTeethPlate
		d_build = {'mouthMove':{'mode':'blendHandleAttach','defaultValue':.02,'followSuffix':'Jaw',
		                        'attachTo':mi_lwrTeethPlate,'target0':mi_uprTeethPlate},
		           'mouthMoveTrackLoc':{'attachTo':mi_uprTeethPlate},
		           'mouthMoveJawTrackLoc':{'attachTo':mi_lwrTeethPlate},			           
		           'chinTrackLoc':{'attachTo':mi_lwrTeethPlate},		           
		           'chin':{'mode':'handleAttach','attachTo':mi_lwrTeethPlate},
		           #'lipCornerRig':{'attachTo':mi_lwrTeethPlate},#reg, will be driven by...		           
		           #'lipCornerHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode},
		           #'lipCornerHandle':{'mode':'handleAttach','attachTo':mi_lwrTeethPlate},
		           'lipCornerRig':{'mode':'blendAttach','defaultValue':.75,'followSuffix':'Jaw','connectFollicleOffset':True,
		                           'left':{'mode':'blendAttach','attachTo':[mi_uprTeethPlate,mi_lwrTeethPlate],
		                                   'drivers':[self.md_rigList['lipCornerHandle']['left'][0],self.md_rigList['lipCornerHandle']['left'][0]],
		                                   'controlObj':self.md_rigList['lipCornerHandle']['left'][0]},
		                           'right':{'mode':'blendAttach','attachTo':[mi_uprTeethPlate,mi_lwrTeethPlate],
		                                    'drivers':[self.md_rigList['lipCornerHandle']['right'][0],self.md_rigList['lipCornerHandle']['right'][0]],
		                                    'controlObj':self.md_rigList['lipCornerHandle']['right'][0]}},		           
		           'lipCornerHandle':{'mode':'blendAttach','defaultValue':.75,'followSuffix':'Jaw',
		                              'drivers':[mi_mouthMoveTrackLoc,mi_mouthMoveJawTrackLoc],'attachTo':[mi_uprTeethPlate,mi_lwrTeethPlate]},
		           #'lipUprHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode,#...non center handle
		                           #'center':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode}},
		           'lipUprHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode,#...non  center handles
		                           'center':{'mode':'slideHandleAttach','attachTo':mi_uprTeethPlate}},			           
		           'lipLwrHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveJawTrackLoc.mNode,#...non  center handles
		                           'center':{'mode':'slideHandleAttach','attachTo':mi_lwrTeethPlate}},	           		           		           
		           #'lipLwrHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode,#...non  center handles
		           #                'center':{'mode':'blendAttach','defaultValue':.6,'attachTo':mi_lwrTeethPlate.mNode,
		           #                          'followSuffix':'Jaw','target0':mi_mouthMoveTrackLoc}},	           
		           #'mouthMoveTrackLoc':{'mode':'blendAttach','defaultValue':.25,'followSuffix':'Jaw','controlObj':mi_mouthMove,
		                               # 'attachTo':mi_lwrTeethPlate,'target0':mi_uprTeethPlate},
		           }				
		self.attach_fromDict(d_build)
		
	    except Exception,error:raise StandardError,"[Attach! | error: {0}]".format(error)
	    
	    try:#>>> Connect rig joints to handles ==================================================================
		'''
			    d_build = {'lipUprRig':{'mode':'rigToSegment'},
		           'lipLwrRig':{'mode':'rigToSegment'},
		           'lipCornerRig':{},
		           'chinTrackLoc':{'driver':self.md_rigList['chin']},		           
		           'mouthMoveTrackLoc':{'driver':self.md_rigList['mouthMove']}}
		self.connect_fromDict(d_build)
		'''
		d_build = {'mouthMoveTrackLoc':{'driver':self.md_rigList['mouthMove']},
		           'chinTrackLoc':{'driver':self.md_rigList['chin']},
		           #'lipCornerHandle':{'driver':self.md_rigList['mouthMove']},
		           'lipCornerHandle':{'mode':'attrOffsetConnect','driver':self.md_rigList['mouthMove'],'attrsToConnect':['tz'],
		                              'right':{'attrsToMirror':['tz']}},
		           'lipCornerRig':{'mode':'attrOffsetConnect','driver':self.md_rigList['mouthMove'],'attrsToConnect':['tz'],
		                           'right':{'attrsToMirror':['tz']}},
		           'lipLwrHandle':{'skip':['left','right'],
		                           'center':{'mode':'simpleSlideHandle','driver':self.md_rigList['mouthMove']}},
		           'lipUprHandle':{'skip':['left','right'],
		                           'center':{'mode':'simpleSlideHandle','driver':self.md_rigList['mouthMove']}},		           
		           #'lipLwrHandle':{'skip':['left','right'],
		                           #'center':{'mode':'offsetConnect','driver':self.md_rigList['mouthMove']}},
		           #'lipCornerRig':{'rewireFollicleOffset':True},#...will connect to handle
		           }
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Connect!] | error: {0}]".format(error)
	    
	    try:#>> UprLip Center follow  =======================================================================================
		mObj = self.md_rigList['lipUprHandle']['center'][0]
		mi_offsetGroup = cgmMeta.cgmObject(mObj.doGroup(True),setClass=True)
		mi_offsetGroup.doStore('cgmName',mObj.mNode)
		mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		mi_offsetGroup.doName()
		mObj.connectChildNode(mi_offsetGroup,"offsetGroup","childObject")
		"""
		mc.pointConstraint([self.md_rigList['lipCornerHandle']['left'][0].mNode,
		                    self.md_rigList['mouthMove'][0].mNode,
		                    self.md_rigList['lipCornerHandle']['right'][0].mNode],
		                   mi_offsetGroup.mNode,skip = [mi_go._jointOrientation[0],mi_go._jointOrientation[2]],
		                   maintainOffset = True)"""
	    except Exception,error:raise StandardError,"[Center upr lip offsetgroup! | error: {0}]".format(error)
	    
	    try:#>>> Aim some stuff =================================================================================
		mi_mouthMoveUpLoc = self.md_attachReturns[mi_mouthMoveTrackLoc]['upLoc']
		mi_mouthMoveUpLoc.mNode
		mi_noseUnder = self.md_rigList['noseUnderHandle'][0]
		mi_chin = self.md_rigList['chin'][0]
		mi_noseMove = self.md_rigList['noseMoveHandle'][0]
		mi_noseTop = self.md_rigList['noseTopHandle'][0]		
		mi_mouthMove = self.md_rigList.get('mouthMove')[0]		
		mi_lwrCenterHandle = self.md_rigList['lipLwrHandle']['center'][0]
		mi_uprCenterHandle = self.md_rigList['lipUprHandle']['center'][0]
		'''
		str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'lipLineBlend'
		mi_upLoc = d_buffer.get('upLoc') or d_build[str_tag].get('upLoc') or d_current.get('upLoc')
		str_baseKey = d_buffer.get('baseKey') or d_build[str_tag].get('baseKey') or 'uprLipRig'	
		'''
		'''
		d_build = {'noseUnderRig':{'mode':'singleTarget','aimVector':mi_go._vectorUpNegative,'upVector':mi_go._vectorAim,
			   'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseUnderTarget},
	       'noseTopRig':{'mode':'singleTarget','aimVector':mi_go._vectorUpNegative,'upVector':mi_go._vectorAim,
			  'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseMove}}
			  
			  
		'mouthMoveTrackLoc':{'mode':'singleVectorAim','v_aim':mi_go._vectorUp,'v_up':mi_go._vectorUp,
		                                'upLoc':mi_mouthMoveUpLoc,'aimTargets':[mi_noseTop]},
			  
		'''
		#'lipLwrRig':{'mode':'lipLineBlend','upLoc':mi_mouthMoveUpLoc}
		#mi_noseMove,mi_noseMove.masterGroup,
		d_build = {#'chin':{'mode':'singleTarget','v_aim':mi_go._vectorUp,'v_up':mi_go._vectorUp,
		                   #'upLoc':mi_mouthMoveUpLoc,'aimTarget':mi_lwrCenterHandle.masterGroup},
		           'lipUprHandle':{'mode':'singleBlend','upLoc':mi_mouthMoveUpLoc,'skip':['left','right'],
		                           'center':{'offsetGroup':mi_offsetGroup,
		                                     'd_target0':{'target':self.md_rigList['lipCornerHandle']['left'][0],
		                                        'v_aim':mi_go._vectorOut,'v_up':mi_go._vectorAim},
		                                     'd_target1':{'target':self.md_rigList['lipCornerHandle']['right'][0],
		                                                  'v_aim':mi_go._vectorOutNegative,'v_up':mi_go._vectorAim}}}}
		self.aim_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Aim! | error: {0}]".format(error)	
	    
	    try:#constrain mids ====================================================================================
		l_build = [{'obj':self.md_rigList['lipUprHandle']['left'][0],
	                   'targets':[self.md_rigList['lipUprHandle']['center'][0],
	                              self.md_rigList['lipCornerRig']['left'][0].uprDriverSkin],
	                   'mode':'parent'},
	                   {'obj':self.md_rigList['lipLwrHandle']['left'][0],
	                    'targets':[self.md_rigList['lipLwrHandle']['center'][0],
	                               self.md_rigList['lipCornerRig']['left'][0].lwrDriverSkin],
	                    'mode':'parent'},
		           {'obj':self.md_rigList['lipUprHandle']['right'][0],
		            'targets':[self.md_rigList['lipUprHandle']['center'][0],
		                       self.md_rigList['lipCornerRig']['right'][0].uprDriverSkin],
		            'mode':'parent'},
		            {'obj':self.md_rigList['lipLwrHandle']['right'][0],
		             'targets':[self.md_rigList['lipLwrHandle']['center'][0],
		                        self.md_rigList['lipCornerRig']['right'][0].lwrDriverSkin],
		             'mode':'parent'}]
			   
		for d in l_build:
		    mi_obj = d['obj']
		    ml_targets = d['targets']
		    str_mode = d.get('mode') or 'parent'
		    
		    self.d_buffer['mObj'] = mi_obj
		    self.d_buffer['ml_targets'] = ml_targets
		    
		    mi_offsetGroup = cgmMeta.cgmObject(mi_obj.doGroup(True),setClass=True)
		    mi_offsetGroup.doStore('cgmName',mi_obj.mNode)
		    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		    mi_offsetGroup.doName()
		    mObj.connectChildNode(mi_offsetGroup,"offsetGroup","childObject")
		    l_consts = []
		    if str_mode == 'pointOrient':
			l_consts.extend(mc.pointConstraint([mObj.mNode for mObj in ml_targets],mi_offsetGroup.mNode, maintainOffset = 1))
			l_consts.extend(mc.orientConstraint([mObj.mNode for mObj in ml_targets],mi_offsetGroup.mNode, maintainOffset = 1))
		    else:
			l_consts.extend(mc.parentConstraint([mObj.mNode for mObj in ml_targets],mi_offsetGroup.mNode, maintainOffset = 1))
		    for str_const in l_consts:
			try:cgmMeta.cgmNode(str_const).interpType = 0
			except Exception,error:self.log_error("Failed to set interp type: '%s']{%s}"%(str_const,error))	    			
	    except Exception,error:raise StandardError,"[constrain mids! | error: {0}]".format(error)	
	    
	def _buildLipStructure_(self):
	    #>> Get some data =======================================================================================
	    """
	    Stuff to setup...
	    1) attach base to skull plate
	    2) What should
	    
	    """	 
	    try:#>> Query ========================================================================
		mi_go = self._go#Rig Go instance link	
	    except Exception,error:raise StandardError,"[Query | error: {0}]".format(error)  
	    
	    try:#Setup Lip Tighteners ========================================================================	    	    	
		#Gonna setup our connections for the roll setup
		d_build = {'leftTigthen':{'handle':self.md_rigList['lipCornerHandle']['left'][0],
		                          'rigJoint':self.md_rigList['lipCornerRig']['left'][0],
		                          'uprDriver':self.md_rigList['uprLipTightener']['left'][0],
		                          'lwrDriver':self.md_rigList['lwrLipTightener']['left'][0]},
		           'rightTigthen':{'handle':self.md_rigList['lipCornerHandle']['right'][0],
		                          'rigJoint':self.md_rigList['lipCornerRig']['right'][0],
		                          'uprDriver':self.md_rigList['uprLipTightener']['right'][0],
		                          'lwrDriver':self.md_rigList['lwrLipTightener']['right'][0]}}
		
		l_keys = d_build.keys()
		int_lenMax = len(l_keys)
		for i,str_k in enumerate(l_keys):
		    try:
			try:#>> Query --------------------------------------------------------------------------
			    d_buffer = d_build[str_k]
			    mi_handle = d_buffer['handle']
			    str_rollAttr = ".r%s"%mi_go._jointOrientation[2]
			    mi_uprDriver = d_buffer['uprDriver']
			    mi_lwrDriver = d_buffer['lwrDriver']
			    mi_rigJoint = d_buffer['rigJoint']
			except Exception,error:raise StandardError,"[Query] | error: {0}".format(error)  
			
			try:#>> Progress -----------------------------------------------------------------------
			    str_message = "'%s' | Setting up tigtener"%(str_k)
			    self.log_info(str_message)
			    self.progressBar_set(status = str_message, progress = i, maxValue = int_lenMax)				    
			except Exception,error:raise StandardError,"[Progress bar] | error: {0}".format(error)  			    

			try:#>> Up locs -----------------------------------------------------------------------
			    mi_upLoc = mi_rigJoint.doLoc()
			    mi_upLoc.parent = mi_rigJoint
			    mi_go.connect_toRigGutsVis(mi_upLoc)
			except Exception,error:raise StandardError,"[Up locs ] | error: {0}".format(error)  	
			
			try:#>> Get Plugs -----------------------------------------------------------------------
			    self.log_info("'%s' | Setting up plugs"%(str_k))			    
			    mPlug_tightenUpr =  cgmMeta.cgmAttr(mi_handle,'tightenUpr', value= 0.0, attrType='float', defaultValue= 0.0,keyable=True, hidden=False)
			    mPlug_tightenLwr =  cgmMeta.cgmAttr(mi_handle,'tightenLwr', value= 0.0, attrType='float', defaultValue= 0.0,keyable=True, hidden=False)
			except Exception,error:raise StandardError,"[Plugs] | error: {0}".format(error)  
			
			try:#>> Args to nodes -----------------------------------------------------------------------
			    '''
			    l_lipCorner_uprDriver_jnt.rotateX = l_lipCorner_handle_anim.tightUpr;
			    l_lipCorner_lwrDriver_jnt.rotateX = -l_lipCorner_handle_anim.tightLwr;
			    '''				    
			    self.log_info("'%s' | Args to nodes"%(str_k))
			    d_argToBuild = {'upr':"%s%s = %s"%(mi_uprDriver.p_nameShort,str_rollAttr, mPlug_tightenUpr.p_combinedShortName),
			                    'lwr':"%s%s = -%s"%(mi_lwrDriver.p_nameShort,str_rollAttr, mPlug_tightenLwr.p_combinedShortName)}
			    
			    for str_argK in d_argToBuild.keys():
				try: 			    
				    str_arg = d_argToBuild[str_argK]
				    self.log_info("'%s' | argsToNodes..."%(str_argK))									    
				    self.log_info("building: %s"%(str_arg))
				    NodeF.argsToNodes(str_arg).doBuild()				
				except Exception,error:raise Exception,"['%s' fail]{%s}"%(str_argK,error)  			    
			except Exception,error:raise Exception,"[Args to nodes] | error: {0}".format(error) 
			
			try:#>> Setup aim on them -----------------------------------------------------------------------
			    try:#Vectors
				v_aim = mi_go._vectorAim
				if 'left' in str_k:
				    v_up = mi_go._vectorOut
				    mi_upLoc.__setattr__("t%s"%mi_go._jointOrientation[0],10)				    
				else:
				    v_up = mi_go._vectorOutNegative
				    mi_upLoc.__setattr__("t%s"%mi_go._jointOrientation[0],-10)				    
				    									
			    except Exception,error:raise StandardError,"[Vector query!] | error: {0}".format(error)
			    
			    for i,mDriver in enumerate([mi_uprDriver,mi_lwrDriver]):
				try:#For loop
				
				    if i == 0:
					mi_target = self.md_rigList['lipUprHandle']['center'][0]
				    else:
					mi_target = self.md_rigList['lipLwrHandle']['center'][0]
					
				    #Make a group
				    mi_aimOffsetGroup = cgmMeta.cgmObject(mDriver.doGroup(True),setClass=True)
				    mi_aimOffsetGroup.doStore('cgmName',mDriver.mNode)
				    mi_aimOffsetGroup.addAttr('cgmTypeModifier','aimOffset',lock=True)
				    mi_aimOffsetGroup.doName()
				    mDriver.connectChildNode(mi_aimOffsetGroup,"aimOffsetGroup","childObject")
				    
				    mc.aimConstraint(mi_target.mNode, mi_aimOffsetGroup.mNode,
					             weight = 1, aimVector = v_aim, upVector = v_up,
					             maintainOffset = 1, worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) 
				except Exception,error:raise StandardError,"[Driver loop : '%s']{%s}"%(mDriver.p_nameShort,error)
			except Exception,error:raise Exception,"[Aim setup] | error: {0}".format(error)
			
			try:#>> offset rot -----------------------------------------------------------------------
			    for i,mDriver in enumerate([mi_uprDriver,mi_lwrDriver]):
				try:#For loop
				    #Make a group
				    mi_rotOffsetGroup = cgmMeta.cgmObject(mDriver.doGroup(True),setClass=True)
				    mi_rotOffsetGroup.doStore('cgmName',mDriver.mNode)
				    mi_rotOffsetGroup.addAttr('cgmTypeModifier','rotOffset',lock=True)
				    mi_rotOffsetGroup.doName()
				    mDriver.connectChildNode(mi_rotOffsetGroup,"rotOffsetGroup","childObject")
				    
				    #Connect
				    cgmMeta.cgmAttr(mi_rotOffsetGroup,'r%s'%mi_go._jointOrientation[2]).doConnectIn("%s.r%s"%(mi_handle.mNode,mi_go._jointOrientation[0]))
				    
				except Exception,error:raise StandardError,"[Driver loop : '%s']{%s}"%(mDriver.p_nameShort,error)			    
			    
			except Exception,error:raise Exception,"[OffsetRot] | error: {0}".format(error) 			
		    except Exception,error:raise Exception,"[On: '%s']{%s}"%(str_k,error) 
	    except Exception,error:raise StandardError,"[Lip Tigteners | error: {0}]".format(error)  
	    
	    try:#Smart Seal ===================================================================
		try:#Curve creation -------------------------------------------------------
		    self.progressBar_set(status = 'Curve creation!')
		    ml_uprLipRigJoints = self.md_rigList['lipUprRig']['left'] + self.md_rigList['lipUprRig']['center'] + self.md_rigList['lipUprRig']['right']
		    ml_lwrLipRigJoints = self.md_rigList['lipLwrRig']['left'] + self.md_rigList['lipLwrRig']['center'] + self.md_rigList['lipLwrRig']['right']
		    
		    for ml in [ml_uprLipRigJoints]:
			ml.insert(0,self.md_rigList['lipCornerRig']['left'][0])
			ml.append(self.md_rigList['lipCornerRig']['right'][0])
			
		    ml_uprLipHandles = self.md_rigList['lipUprHandle']['left'] + self.md_rigList['lipUprHandle']['center'] + self.md_rigList['lipUprHandle']['right']
		    ml_lwrLipHandles = self.md_rigList['lipLwrHandle']['left'] + self.md_rigList['lipLwrHandle']['center'] + self.md_rigList['lipLwrHandle']['right']
		    
			
		    ml_uprLipHandles.insert(0,self.md_rigList['lipCornerRig']['left'][0].uprDriverSkin)
		    ml_uprLipHandles.append(self.md_rigList['lipCornerRig']['right'][0].uprDriverSkin)
		    ml_lwrLipHandles.insert(0,self.md_rigList['lipCornerRig']['left'][0].lwrDriverSkin)
		    ml_lwrLipHandles.append(self.md_rigList['lipCornerRig']['right'][0].lwrDriverSkin)	
		    
		    for ml in ml_uprLipHandles,ml_lwrLipHandles:
			ml.insert(0,self.md_rigList['lipCornerRig']['left'][0])
			ml.append(self.md_rigList['lipCornerRig']['right'][0])		    
		    '''	
		    d_logs = {'uprLipRig':ml_uprLipRigJoints,
			      'lipLwrRig':ml_lwrLipRigJoints,
			      'uprLipHandle':ml_uprLipHandles,
			      'lwrLipHandle':ml_lwrLipHandles,
			      }
		    
		    for k in d_logs.iterkeys():
			self.log_info("%s..."%k)
			for mObj in d_logs[k]:
			    self.log_info("--> %s "%mObj.p_nameShort)	
			    '''
		    ml_curves = []
		    
		    try:#Upr driven curve
			_str_uprDrivenCurve = mc.curve(d=3,ep=[mi_obj.getPosition() for mi_obj in ml_uprLipRigJoints],os =True)
			mi_uprDrivenCrv = cgmMeta.cgmObject(_str_uprDrivenCurve,setClass=True)
			mi_uprDrivenCrv.addAttr('cgmName','uprLip',lock=True)
			mi_uprDrivenCrv.addAttr('cgmTypeModifier','driven',lock=True)
			mi_uprDrivenCrv.doName()
			ml_curves.append(mi_uprDrivenCrv)
			
			mi_uprLipSealCrv = mi_uprDrivenCrv.doDuplicate(False)
			mi_uprLipSealCrv.addAttr('cgmTypeModifier','lipSeal',lock=True)
			mi_uprLipSealCrv.doName()
			ml_curves.append(mi_uprLipSealCrv)
		    except Exception,error:raise StandardError,"[upper driven curve!] | error: {0}".format(error)  	    
		    
		    try:#Upper driver curve
			_str_uprDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_uprLipHandles],os =True)
			mi_uprDriverCrv = cgmMeta.cgmObject(_str_uprDriverCurve,setClass=True)
			mi_uprDriverCrv.doCopyNameTagsFromObject(mi_uprDrivenCrv.mNode,ignore=['cgmTypeModifier'])
			mi_uprDriverCrv.addAttr('cgmTypeModifier','driver',lock=True)
			mi_uprDriverCrv.doName()
			ml_curves.append(mi_uprDriverCrv)	    
		    except Exception,error:raise StandardError,"[upper driver curve!] | error: {0}".format(error)  	    
		    
		    try:#Lwr driven curve
			_str_lwrDrivenCurve = mc.curve(d=3,ep=[mi_obj.getPosition() for mi_obj in self.md_rigList['lipCornerRig']['left'] + ml_lwrLipRigJoints + self.md_rigList['lipCornerRig']['right']],os =True)
			mi_lwrDrivenCrv = cgmMeta.cgmObject(_str_lwrDrivenCurve,setClass=True)
			mi_lwrDrivenCrv.doCopyNameTagsFromObject(mi_uprDrivenCrv.mNode)
			mi_lwrDrivenCrv.addAttr('cgmName','lwrLip',lock=True)	    
			mi_lwrDrivenCrv.doName()
			ml_curves.append(mi_lwrDrivenCrv)	
			
			mi_lwrLipSealCrv = mi_lwrDrivenCrv.doDuplicate(False)
			mi_lwrLipSealCrv.addAttr('cgmTypeModifier','lipSeal',lock=True)
			mi_lwrLipSealCrv.doName()
			ml_curves.append(mi_lwrLipSealCrv)
		    except Exception,error:raise StandardError,"[upper driven curve!] | error: {0}".format(error)  	    
		    
		    try:#Lwr driver curve
			_str_lwrDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_lwrLipHandles],os =True)
			mi_lwrDriverCrv = cgmMeta.cgmObject(_str_lwrDriverCurve,setClass=True)
			mi_lwrDriverCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
			mi_lwrDriverCrv.addAttr('cgmName','lwrLip',lock=True)	    
			mi_lwrDriverCrv.doName()
			ml_curves.append(mi_lwrDriverCrv)	    	    	    
		    except Exception,error:raise StandardError,"[upper driver curve!] | error: {0}".format(error)  	    
		    
		    try:#SmartLipSeal curve
			_str_smartLipSealCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_lwrLipHandles],os =True)
			mi_smartLipSealCrv = cgmMeta.cgmObject(_str_smartLipSealCurve,setClass=True)
			mi_smartLipSealCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
			mi_smartLipSealCrv.addAttr('cgmName','smartLipSeal',lock=True)	    
			mi_smartLipSealCrv.doName()
			ml_curves.append(mi_smartLipSealCrv)	    	    	    
		    except Exception,error:raise StandardError,"[smartLipSeal curve] | error: {0}".format(error)  
		    
		    try:
			for mi_crv in ml_curves:#Parent to rig null
			    mi_crv.parent = mi_go._i_rigNull#used to be deformNull
			    
			#for mi_crv in [mi_smartLipSealCrv,mi_lwrLipSealCrv,mi_uprLipSealCrv]:
			    #mi_crv.parent = mi_go._i_rigNull
			    
		    except Exception,error:raise StandardError,"[Curve parenting] | error: {0}".format(error)  
		except Exception,error:raise StandardError,"[Curve creation] | error: {0}".format(error)   
	    
		
		'''	
		try:#Locators and aiming -------------------------------------------------------
		    self.progressBar_set(status = 'Locator creation!')
		    
		    #Make a loc group
		    mi_locGroup = cgmMeta.cgmObject(mc.group(em=True))
		    mi_locGroup.parent = mi_go._i_constrainNull
		    mi_locGroup.addAttr('cgmTypeModifier','locGroup')
		    mi_locGroup.doName()
		    mi_locGroup.parent = mi_go._i_rigNull
		    self.ml_toVisConnect.append(mi_locGroup)
		    
		    ml_locs = []
		    self.progressBar_setMaxStepValue(len(ml_uprLipRigJoints + ml_lwrLipRigJoints))	
		    
		    for i,mi_obj in enumerate(ml_uprLipRigJoints + ml_lwrLipRigJoints):
			try:
			    self.progressBar_iter(status = ("Curve locator: '%s'"%mi_obj.p_nameShort))			    
			    
			    try:#Loc creation -----------------------------------------------------------
				mi_loc = mi_obj.doLoc()
				ml_locs.append(mi_loc)
				mi_locShape = cgmMeta.cgmNode(mi_loc.getShapes()[0])
				mi_locShape.localScaleX = mi_go._f_skinOffset
				mi_locShape.localScaleY = mi_go._f_skinOffset
				mi_locShape.localScaleZ = mi_go._f_skinOffset
				mi_loc.parent = mi_locGroup
			    except Exception,error:raise StandardError,"[loc creation] | error: {0}".format(error)  	    
			    #> Aim constraint
			    #mi_root = mi_obj.root
			    #mi_root.parent = self._i_constrainNull
			    #try:mc.aimConstraint(mi_loc.mNode,mi_root.mNode,maintainOffset = False, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
			    #except Exception,error:raise StandardError,"[aim constrai]{%s}%s"%(error)  	    
			    #Attach to curve
			    if i < len(ml_uprLipRigJoints):mi_crv = mi_uprDrivenCrv
			    else:mi_crv = mi_lwrDrivenCrv
			    try:crvUtils.attachObjToCurve(mi_loc.mNode,mi_crv.mNode)
			    except Exception,error:raise StandardError," attach| %s "%(error)  	    
			    self.md_attachReturns[mObj] = {'posLoc':mi_loc,'posLocShape':mi_locShape}#store it
			except Exception,error:raise StandardError,"%s | '%s' loc setup | %s "%(i,mi_obj.p_nameShort,error)  	    
		    
		except Exception,error:
		    raise StandardError,"locator/aim setup | %s"%(error)
		'''
		try:#Lip setup -------------------------------------------------------
		    try:#Wire deformers -------------------------------------------------------------
			self.progressBar_set(status = 'Smart Seal - Wire deformer...')
			_l_return = mc.wire(mi_uprDrivenCrv.mNode, w = mi_uprDriverCrv.mNode, gw = False, en = 1, ce = 0, li =0)
			mi_uprWire = cgmMeta.cgmNode(_l_return[0])
			mi_uprWire.doStore('cgmName',mi_uprDrivenCrv.mNode)
			mi_uprWire.doName()
			_l_return = mc.wire(mi_lwrDrivenCrv.mNode, w = mi_lwrDriverCrv.mNode, gw = False, en = 1, ce = 0, li =0)
			mi_lwrWire = cgmMeta.cgmNode(_l_return[0])
			mi_lwrWire.doStore('cgmName',mi_lwrDrivenCrv.mNode)
			mi_lwrWire.doName()
			
			mi_uprDriverCrv.parent = mi_go._i_rigNull
			mi_lwrDriverCrv.parent = mi_go._i_rigNull			
		    except Exception,error:raise StandardError,"[wire deformer!] | error: {0}".format(error)  	    
		    
		    try:#Skin driver curve ---------------------------------------------------------
			self.progressBar_set(status = 'Smart Seal - Skin lip curves...')
			
			ml_uprSkinJoints = ml_uprLipHandles
			ml_lwrSkinJoints = ml_lwrLipHandles
			md_skinSetup = {'upr':{'ml_joints':ml_uprSkinJoints,'mi_crv':mi_uprDriverCrv},
			                'lwr':{'ml_joints':ml_lwrSkinJoints,'mi_crv':mi_lwrDriverCrv}}
			for k in md_skinSetup.keys():
			    d_crv = md_skinSetup[k]
			    str_crv = d_crv['mi_crv'].p_nameShort
			    l_joints = [mi_obj.p_nameShort for mi_obj in d_crv['ml_joints']]
			    self.log_info(" %s | crv]{%s} | joints: %s"%(k,str_crv,l_joints))
			    try:
				mi_skinNode = cgmMeta.cgmNode(mc.skinCluster ([mi_obj.mNode for mi_obj in d_crv['ml_joints']],
				                                              d_crv['mi_crv'].mNode,
				                                              tsb=True,
				                                              maximumInfluences = 3,
				                                              normalizeWeights = 1,dropoffRate=2.5)[0])
			    except Exception,error:raise StandardError,"skinCluster] | error: {0}".format(error)  	    
			    d_crv['mi_skinNode'] = mi_skinNode
		    except Exception,error:raise StandardError,"[skinning drive]{%s}s"%(error)  	    
		    
		    try:#Blendshape the smart lipSeal curve ---------------------------------------------
			self.progressBar_set(status = 'Smart Seal - Blendshape...')
			
			_str_bsNode = mc.blendShape([mi_uprDriverCrv.mNode,mi_lwrDriverCrv.mNode],mi_smartLipSealCrv.mNode)[0]
			mi_bsNode = cgmMeta.cgmNode(_str_bsNode,setClass=True)
			mi_bsNode.doStore('cgmName',mi_smartLipSealCrv.mNode)
			mi_bsNode.doName()
			mi_sealAttrHolder = self.md_rigList['mouthMove'][0]
			
			mPlug_height = cgmMeta.cgmAttr(mi_sealAttrHolder,'lipSealHeight',attrType = 'float', defaultValue=.5, minValue = 0, maxValue = 1)
			l_bsAttrs = deformers.returnBlendShapeAttributes(mi_bsNode.mNode)
			d_return = NodeF.createSingleBlendNetwork([mi_sealAttrHolder.mNode,'lipSealHeight'],
			                                          [mi_sealAttrHolder.mNode,'lipSealHeight_upr'],
			                                          [mi_sealAttrHolder.mNode,'lipSealHeight_lwr'],
			                                          keyable=True)	
			#Connect                                  
			d_return['d_result1']['mi_plug'].doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[0]))
			d_return['d_result2']['mi_plug'].doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[1]))
		    except Exception,error:raise StandardError,"[smartLipSeal bsNod]{%s}s"%(error)  	
		    
		    try:#Wire deform the uper and lwr lipSeal lids ---------------------------------------------------------
			self.progressBar_set(status = 'Smart Seal - wire deform setup...')		    
			#Build our lipSeal match wire deformers
			mPlug_height.value = 0	    
			_l_return = mc.wire(mi_lwrLipSealCrv.mNode, w = mi_smartLipSealCrv.mNode, gw = False, en = 1, ce = 0, li =0)
			mi_lwrLipSealWire = cgmMeta.cgmNode(_l_return[0])
			mi_lwrLipSealWire.doStore('cgmName',mi_lwrDrivenCrv.mNode)
			mi_lwrLipSealWire.addAttr('cgmTypeModifier','lipSeal')	    
			mi_lwrLipSealWire.doName()
			mc.setAttr("%s.scale[0]"%mi_lwrLipSealWire.mNode,0)
			
			mPlug_height.value = 1
			_l_return = mc.wire(mi_uprLipSealCrv.mNode, w = mi_smartLipSealCrv.mNode, gw = False, en = 1, ce = 0, li =0)
			mi_uprLipSealWire = cgmMeta.cgmNode(_l_return[0])
			mi_uprLipSealWire.doStore('cgmName',mi_uprDrivenCrv.mNode)
			mi_uprLipSealWire.addAttr('cgmTypeModifier','lipSeal')	    
			mi_uprLipSealWire.doName()
			mc.setAttr("%s.scale[0]"%mi_uprLipSealWire.mNode,0)
			
			mPlug_height.value = .5#back to default
		    except Exception,error:raise StandardError,"[lipSeal target wire]{%s}s"%(error)  	
		    
		    try:#Blendshape the upr and lwr curves to smart lipSeal targets------------------------------------
			mPlug_lipSeal = cgmMeta.cgmAttr(mi_sealAttrHolder,'lipSeal',attrType = 'float', keyable=True, minValue=0, maxValue=1, defaultValue=0)
			d_blendshapeLipSeal = {'upr':{'mi_target':mi_uprLipSealCrv,'mi_driven':mi_uprDrivenCrv},
			                       'lwr':{'mi_target':mi_lwrLipSealCrv,'mi_driven':mi_lwrDrivenCrv}}
			for k in d_blendshapeLipSeal.keys():
			    d_buffer = d_blendshapeLipSeal[k]
			    mi_target = d_buffer['mi_target']
			    mi_driven = d_buffer['mi_driven']
			    _str_bsNode = mc.blendShape(mi_target.mNode,mi_driven.mNode)[0]
			    mi_bsNode = cgmMeta.cgmNode(_str_bsNode,setClass=True)
			    mi_bsNode.doStore('cgmName',mi_uprDrivenCrv.mNode)
			    mi_bsNode.doName()
			    l_bsAttrs = deformers.returnBlendShapeAttributes(mi_bsNode.mNode)
			    mPlug_lipSeal.doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[0]))
		    except Exception,error:raise StandardError,"[lipSeal setup!]{%s}s"%(error)  	
		except Exception,error:
		    raise StandardError,"[lip setup |error: {0}]".format(error)   	        
	    except Exception,error:
		raise StandardError,"[Smart Seal setup fail | error: {0}]".format(error)  
	    
	    try:#Template Curve duplication ====================================================================================
		self.progressBar_set(status = 'Template Curve duplication')  
		d_toDup = {'mouthTopTrace':self.mi_mouthTopCastCrv,
		           'mouthBaseTrace':self.mi_mouthLowCastCrv}
		for str_k in d_toDup.iterkeys():
		    mi_dup = cgmMeta.cgmObject( mc.duplicate(d_toDup[str_k].mNode,po=False,ic=True,rc=True)[0],setClass=True )
		    mi_dup.cgmType = 'traceCrv'
		    mi_dup.cgmName = mi_dup.cgmName.replace('Cast','')
		    mi_dup.doName()
		    cgmMeta.cgmAttr(mi_dup,'translate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'rotate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'scale',lock = False, keyable = True)
		    mi_dup.parent = mi_go._i_rigNull
		    
		    ml_curves.append(mi_dup)
		    self.__dict__["mi_%sCrv"%str_k] = mi_dup
		
		#for mi_crv in ml_curves:#Parent to rig null
		    #mi_crv.parent = mi_go._i_rigNull
		#self.ml_toVisConnect.extend(ml_curves)
	    except Exception,error:raise StandardError,"[Template Curve | error: {0}]".format(error)  
	    
	    try:#Build plates ====================================================================================
		md_plateBuilds = {'uprLip':{'crvs':[self.mi_mouthTopCastCrv,self.mi_lipOverTraceCrv,self.mi_lipUprCrv]},
		                  #'uprLipFollow':{'crvs':[self.mi_mouthTopTraceCrv,mi_uprDrivenCrv],'mode':'liveSurface'},
		                  'lwrLip':{'crvs':[self.mi_lipLwrCrv,self.mi_lipUnderTraceCrv,self.mi_mouthLowCastCrv]},}
		                  #'lwrLipFollow':{'crvs':[mi_lwrDrivenCrv,self.mi_mouthBaseTraceCrv],'mode':'liveSurface'}}
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"[Plates | error: {0}]".format(error)  	    
	    
	    try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		d_build = {'uprLipPlate':{'target':self.mi_uprLipPlate,
		                          'bindJoints':ml_uprLipRigJoints + self.md_rigList['noseUnderRig'] + [self.md_rigList['nostrilRig']['left'][0],self.md_rigList['nostrilRig']['right'][0]]},		           	          
		          'lwrLipPlate':{'target':self.mi_lwrLipPlate,
		                         'bindJoints':ml_lwrLipRigJoints + [self.md_rigList['lipCornerRig']['left'][0].lwrDriverSkin,self.md_rigList['lipCornerRig']['right'][0].uprDriverSkin] +self.md_rigList['chin']}}
		self.skin_fromDict(d_build)

	    except Exception,error:raise StandardError,"[Skinning  | error: {0}]".format(error)    
	    
	    try:#Reverse curve ====================================
		'''
		Setup driven reverse curve for upr and lower to drive the right side segments
		'''
		d_toDup = {'uprLipDrivenReverse':mi_uprDrivenCrv,
		           'lwrLipDrivenReverse':mi_lwrDrivenCrv}	
		
		for str_k in d_toDup.iterkeys():
		    mi_dup = cgmMeta.cgmObject( mc.duplicate(d_toDup[str_k].mNode,po=False,ic=1,rc=True)[0],setClass=True )
		    mi_dup.addAttr('cgmTypeModifier','ReverseDriven')
		    mi_dup.doName()
		    
		    mc.reverseCurve(mi_dup.mNode,rpo=True)
		    cgmMeta.cgmAttr(mi_dup,'translate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'rotate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'scale',lock = False, keyable = True)
		    #mi_dup.parent = mi_go._i_rigNull
		    
		    ml_curves.append(mi_dup)
		    self.__dict__["mi_%sCrv"%str_k] = mi_dup
	    except Exception,error:raise StandardError,"[Reverse Curves setup | error: {0}]".format(error)  
	        
	    try:#Setup segments ========================================================================
		d_build = {'uprLipSegment':{'orientation':mi_go._jointOrientation,
		                            'left':{'mi_curve':mi_uprDrivenCrv},
		                            'right':{'mi_curve':self.mi_uprLipDrivenReverseCrv}},
		           'lwrLipSegment':{'orientation':mi_go._jointOrientation,
		                            'left':{'mi_curve':mi_lwrDrivenCrv},
		                            'right':{'mi_curve':self.mi_lwrLipDrivenReverseCrv}}}	
		self.create_segmentfromDict(d_build)
	    except Exception,error:raise StandardError,"[Segments | error: {0}]".format(error)  
	    '''
	    try:#Build mid lip Up Locs ========================================================================	
		d_build = {'uprLipSegment':{'left':{'mi_curve':mi_uprDrivenCrv},
		                            'right':{'mi_curve':self.mi_uprLipDrivenReverseCrv}},
		           'lwrLipSegment':{'left':{'mi_curve':mi_lwrDrivenCrv},
		                            'right':{'mi_curve':self.mi_lwrLipDrivenReverseCrv}}}
		
		#So we are gonna grab the upLocs from our segment returns and make our mid roll up locs from that constrainig between the end rolls
		for i,str_k in enumerate(d_build.keys()):
		    d_buffer = d_build[str_k]
		    ml_locs = []
		    for mi_curve in d_buffer['left']['mi_curve'],d_buffer['right']['mi_curve']:
			try:d_return = self.md_attachReturns[mi_curve]
			except Exception,error:
			    self.log_error(error)
			    raise Exception,"[Failed to find attachReturn: %s | %s]{%s}"%(str_k,i,error)
			try:ml_locs.append(d_return['ml_drivenJoints'][-1].upLoc)
			except Exception,error:
			    self.log_error(error)			    
			    raise Exception,"[Failed to find upLoc: %s | %s]{%s}"%(str_k,i,error)	
		    try:
			#Dup with connections for maintaining toggles
			mi_loc = cgmMeta.cgmObject( mc.duplicate(ml_locs[0].mNode,po=False,ic=True,rc=True)[0],setClass=True )
			mi_loc.parent = mi_go._i_rigNull
			mi_loc.addAttr('cgmTypeModifier','midLoc')
			mi_loc.doName()
		    except Exception,error:
			self.log_error(error)			
			raise Exception,"[%s | loc create]{%s}"%(str_k,error)	
		    mc.pointConstraint([mLoc.mNode for mLoc in ml_locs],mi_loc.mNode,maintainOffset = False)
		    #self.md_rigList["%sMidUpLoc"%str_k]
		    self.__dict__["mi_%sMidUpLoc"%str_k] = mi_loc
		    #d_return['midUpLoc'] = mi_loc#Push to the attachReturn for later pulling
	    except Exception,error:raise StandardError,"[Build mid lip Up Locs] | error: {0}".format(error)  
	    '''
	    try:#Setup Lip Roll ========================================================================
		#Gonna setup our connections for the roll setup
		d_build = {'uprLipRoll':{'handleKey':'lipUprHandle',
		                         'mi_crvLeft':mi_uprDrivenCrv,
		                         'mi_crvRight':self.mi_uprLipDrivenReverseCrv,
		                         'argAverageRoll':"%s = %s >< %s",
		                         'argLeftStart':'%s = -%s - %s',
		                         'argLeftEnd':'%s = -%s - %s%s - %s',
		                         'argRightStart':'%s = %s + %s',
		                         'argRightEnd':'%s = %s + %s%s + %s'},
		           'lwrLipRoll':{'handleKey':'lipLwrHandle',
		                         'mi_crvLeft':mi_lwrDrivenCrv,
		                         'mi_crvRight':self.mi_lwrLipDrivenReverseCrv,
		                         'argAverageRoll':"%s = -%s >< -%s",		                         
		                         'argLeftStart':'%s = %s - %s',
		                         'argLeftEnd':'%s = %s - %s%s - %s',
		                         'argRightStart':'%s = -%s + %s',
		                         'argRightEnd':'%s = -%s + %s%s + %s'}}
		
		l_keys = d_build.keys()
		int_lenMax = len(l_keys)
		#Put some plugs on the mouth move
		
		mi_mouthMove = self.md_rigList['mouthMove'][0]
		for i,str_k in enumerate(l_keys):
		    try:
			try:#>> Query --------------------------------------------------------------------------
			    d_buffer = d_build[str_k]
			    str_rigListKey = d_buffer['handleKey']
			    d_rigListBuffer = self.md_rigList[str_rigListKey]
			    mi_handleLeft = d_rigListBuffer['left'][0]
			    mi_handleRight = d_rigListBuffer['right'][0]
			    mi_handleCenter = d_rigListBuffer['center'][0]
			    mi_crvLeft = d_buffer['mi_crvLeft']
			    mi_crvRight = d_buffer['mi_crvRight']	
			    str_rollAttr = ".r%s"%mi_go._jointOrientation[2]
			    toFill_leftStart = d_buffer['argLeftStart']
			    toFill_leftEnd = d_buffer['argLeftEnd']
			    toFill_rightStart = d_buffer['argRightStart']
			    toFill_rightEnd = d_buffer['argRightEnd']
			    toFill_averageRoll = d_buffer['argAverageRoll']			    
			except Exception,error:raise StandardError,"[Query] | error: {0}".format(error)  
			
			try:#>> Progress -----------------------------------------------------------------------
			    str_message = "'%s' | Setting up roll"%(str_k)
			    self.log_info(str_message)
			    self.progressBar_set(status = str_message, progress = i, maxValue = int_lenMax)				    
			except Exception,error:raise StandardError,"[Progress bar] | error: {0}".format(error)  			    

			try:#>> Get Plugs -----------------------------------------------------------------------
			    self.log_info("'%s' | Setting up plugs"%(str_k))			    
			    mPlug_rollLeftDriver =  cgmMeta.cgmAttr(mi_handleCenter,'rollLeft', value= 0.0, attrType='float', defaultValue= 0.0,keyable=True, hidden=False)
			    mPlug_rollRightDriver =  cgmMeta.cgmAttr(mi_handleCenter,'rollRight', value= 0.0, attrType='float', defaultValue= 0.0,keyable=True, hidden=False)
			    mPlug_extendTwistDriver =  cgmMeta.cgmAttr(mi_handleCenter,'extendTwistToEnd', value= 1.0, attrType='float', defaultValue= 1.0,minValue=0,maxValue=1,keyable=True, hidden=False)
			    
			    mPlug_extendMidToCorner =  cgmMeta.cgmAttr(mi_handleCenter,'extendMidToCorner', value= .2, attrType='float', defaultValue= 0.2,keyable=True,minValue=0,maxValue=1, hidden=False)
			    mPlug_result_extendMidToCornerLeft =  cgmMeta.cgmAttr(mi_handleCenter,'result_extendMidToCornerLeft', attrType='float', hidden=True,lock=True)
			    mPlug_result_extendMidToCornerRight =  cgmMeta.cgmAttr(mi_handleCenter,'result_extendMidToCornerRight', attrType='float', hidden=True,lock=True)
			    
			    mPlug_extendCrossRoll =  cgmMeta.cgmAttr(mi_handleCenter,'extendCrossRoll', value= .3, attrType='float', defaultValue= 0.2,keyable=True,minValue=0,maxValue=1, hidden=False)
			    mPlug_result_extendCrossRollLeft =  cgmMeta.cgmAttr(mi_handleCenter,'result_extendCrossRollLeft', attrType='float', hidden=True,lock=True)
			    mPlug_result_extendCrossRollRight =  cgmMeta.cgmAttr(mi_handleCenter,'result_extendCrossRollRight', attrType='float', hidden=True,lock=True)
			    mPlug_result_averageRoll =  cgmMeta.cgmAttr(mi_handleCenter,'result_averageRoll', attrType='float', hidden=True,lock=True)
			    
			    mPlug_extendTwistToEndLeft = self.md_attachReturns[mi_crvLeft]['mPlug_extendTwist']
			    mPlug_extendTwistToEndRight = self.md_attachReturns[mi_crvRight]['mPlug_extendTwist']
			    mPlug_extendTwistToEndLeft.doConnectIn(mPlug_extendTwistDriver.p_combinedShortName)
			    mPlug_extendTwistToEndRight.doConnectIn(mPlug_extendTwistDriver.p_combinedShortName)
			    
			    mPlug_twistStartLeft = cgmMeta.cgmAttr(mi_crvLeft,'twistStart')
			    mPlug_twistEndLeft = cgmMeta.cgmAttr(mi_crvLeft,'twistEnd')
			    mPlug_twistStartRight = cgmMeta.cgmAttr(mi_crvRight,'twistStart')
			    mPlug_twistEndRight = cgmMeta.cgmAttr(mi_crvRight,'twistEnd')			    
			except Exception,error:raise Exception,"[Get Plugs] | error: {0}".format(error)  			    
			
			try:#>> Args to nodes -----------------------------------------------------------------------
			    self.log_info("'%s' | Args to nodes"%(str_k))
			    '''
			    uprLip_driven_splineIKCurve.twistStart= -center_lipUpr_handle_anim.rollLeft - (center_lipUpr_handle_anim.rotateX/2) ;
			    uprLip_driven_splineIKCurve.twistEnd = -center_lipUpr_handle_anim.rollLeft - center_lipUpr_handle_anim.rotateX - (center_lipUpr_handle_anim.rollRight/3);
			    uprLip_ReverseDriven_splineIKCurve.twistStart = center_lipUpr_handle_anim.rollRight + (center_lipUpr_handle_anim.rotateX/2);	    
			    uprLip_ReverseDriven_splineIKCurve.twistEnd = center_lipUpr_handle_anim.rollRight + center_lipUpr_handle_anim.rotateX + (center_lipUpr_handle_anim.rollLeft/3);
			    '''			    
			    try:#>>Build our dicts --------------------------------------------------------------------
				d_argToBuild = {'averageRoll':{'arg':toFill_averageRoll,
				                               'fill':(mPlug_result_averageRoll.p_combinedShortName,
				                                       mPlug_rollLeftDriver.p_combinedShortName,
				                                       mPlug_rollRightDriver.p_combinedShortName)},
				                'leftMidToStartResult':{'arg':"%s = %s * %s%s",
				                                        'fill':(mPlug_result_extendMidToCornerLeft.p_combinedShortName,
				                                                mPlug_extendMidToCorner.p_combinedShortName,
				                                                mi_handleCenter.p_nameShort,str_rollAttr)},
				                'rightMidToStartResult':{'arg':"%s = %s * %s%s",
				                                    'fill':(mPlug_result_extendMidToCornerRight.p_combinedShortName,
				                                            mPlug_extendMidToCorner.p_combinedShortName,
				                                            mi_handleCenter.p_nameShort,str_rollAttr)},	
				                'leftCrossResult':{'arg':"%s = %s * %s",
				                                   'fill':(mPlug_result_extendCrossRollLeft.p_combinedShortName,
				                                           mPlug_extendCrossRoll.p_combinedShortName,
				                                           mPlug_rollLeftDriver.p_combinedShortName)},
				                'rightCrossResult':{'arg':"%s = %s * %s",
				                                    'fill':(mPlug_result_extendCrossRollRight.p_combinedShortName,
				                                            mPlug_extendCrossRoll.p_combinedShortName,
				                                            mPlug_rollRightDriver.p_combinedShortName)},					                
				                'leftStart':{'arg':toFill_leftStart,
				                             'fill':(mPlug_twistStartLeft.p_combinedShortName,
				                                     mPlug_rollLeftDriver.p_combinedShortName,
				                                     mPlug_result_extendMidToCornerLeft.p_combinedShortName)},
				                'leftEnd':{'arg':toFill_leftEnd,
				                           'fill':(mPlug_twistEndLeft.p_combinedShortName,
				                                   mPlug_rollLeftDriver.p_combinedShortName,
				                                   mi_handleCenter.p_nameShort,str_rollAttr,
				                                   mPlug_result_extendCrossRollRight.p_combinedShortName)},
				                'rightStart':{'arg':toFill_rightStart,
				                              'fill':(mPlug_twistStartRight.p_combinedShortName,
				                                      mPlug_rollRightDriver.p_combinedShortName,
				                                      mPlug_result_extendMidToCornerRight.p_combinedShortName)},
				                'rightEnd':{'arg':toFill_rightEnd,
				                            'fill':(mPlug_twistEndRight.p_combinedShortName,
				                                    mPlug_rollRightDriver.p_combinedShortName,
				                                    mi_handleCenter.p_nameShort,str_rollAttr,				                                    
				                                    mPlug_result_extendCrossRollLeft.p_combinedShortName)}}					     
			    except Exception,error:raise Exception,"[Can't even build dict...] | error: {0}".format(error)  			    
			    
			    
			    for str_argK in d_argToBuild.keys():
				try:
				    try:
					self.log_info("'%s' | query"%(str_argK))					
					str_arg = d_argToBuild[str_argK]['arg']
					l_buffer = d_argToBuild[str_argK]['fill']
				    except Exception,error:raise Exception,"[Query] | error: {0}".format(error)  			    
				    try:
					self.log_info("'%s' | build arg from %s"%(str_argK, str_arg))										
					arg_built = str_arg%l_buffer
				    except Exception,error:
					#self.log_info("'%s' | arg: %s"%(str_argK,str_arg))										
					int_cnt = str_arg.count('%s')	
					raise StandardError,"['%s' | arg: %s | given fillers: %s | count: %s]{%s}"%(str_argK,str_arg,len(l_buffer),int_cnt,error)
				    self.log_info("'%s' | argsToNodes..."%(str_argK))									    
				    self.log_info("building: %s"%(arg_built))
				    NodeF.argsToNodes(arg_built).doBuild()				
				except Exception,error:raise Exception,"['%s' fail]{%s}"%(str_argK,error)  			    
			except Exception,error:raise Exception,"[Args to nodes] | error: {0}".format(error) 
			#Process
		    except Exception,error:raise StandardError,"['%s' fail]{%s}"%(str_k,error)  	    
	    except Exception,error:raise StandardError,"[Lip Roll | error: {0}]".format(error)  

	    try:#>>> Connect rig joints to handles ==================================================================
		d_build = {'lipUprRig':{'mode':'rigToSegment'},
		           'lipLwrRig':{'mode':'rigToSegment'}}
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Connect! | error: {0}]".format(error) 
	    
	    try:#Attach stuff to surfaces ====================================================================================
		#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_skullPlate = self.str_skullPlate
		mi_uprTeethPlate = self.mi_uprTeethPlate
		mi_lwrTeethPlate = self.mi_lwrTeethPlate
		
		str_uprLipPlate = self.mi_uprLipPlate.p_nameShort
		str_lwrLipPlate = self.mi_lwrLipPlate.p_nameShort
		mi_mouthMoveTrackLoc = self.md_rigList['mouthMoveTrackLoc'][0]
			
		d_build = {'lipOverRig':{'mode':'handleAttach','attachTo':str_uprLipPlate},		           
		           'lipUnderRig':{'mode':'handleAttach','attachTo':str_lwrLipPlate}}
		
		self.attach_fromDict(d_build)
		
	    except Exception,error:raise StandardError,"[Attach! | error: {0}]".format(error) 
	    
	    try:#Build mid lip Up Locs ========================================================================	
		d_build = {'uprLipSegment':{'left':{'mi_curve':mi_uprDrivenCrv},
		                            'right':{'mi_curve':self.mi_uprLipDrivenReverseCrv}},
		           'lwrLipSegment':{'left':{'mi_curve':mi_lwrDrivenCrv},
		                            'right':{'mi_curve':self.mi_lwrLipDrivenReverseCrv}}}
		
		#So we are gonna grab the upLocs from our segment returns and make our mid roll up locs from that constrainig between the end rolls
		for i,str_k in enumerate(d_build.keys()):
		    d_buffer = d_build[str_k]
		    ml_locs = []
		    for mi_curve in d_buffer['left']['mi_curve'],d_buffer['right']['mi_curve']:
			try:d_return = self.md_attachReturns[mi_curve]
			except Exception,error:
			    self.log_error(error)
			    raise Exception,"[Failed to find attachReturn: %s | %s]{%s}"%(str_k,i,error)
			try:ml_locs.append(d_return['ml_drivenJoints'][-1].upLoc)
			except Exception,error:
			    self.log_error(error)			    
			    raise Exception,"[Failed to find upLoc: %s | %s]{%s}"%(str_k,i,error)	
		    try:
			#Dup with connections for maintaining toggles
			mi_loc = cgmMeta.cgmObject( mc.duplicate(ml_locs[0].mNode,po=False,ic=True,rc=True)[0],setClass=True )
			mi_loc.parent = mi_go._i_rigNull
			mi_loc.addAttr('cgmTypeModifier','midLoc')
			mi_loc.doName()
		    except Exception,error:
			self.log_error(error)			
			raise Exception,"[%s | loc create]{%s}"%(str_k,error)	
		    mc.pointConstraint([mLoc.mNode for mLoc in ml_locs],mi_loc.mNode,maintainOffset = False)
		    #self.md_rigList["%sMidUpLoc"%str_k]
		    self.__dict__["mi_%sMidUpLoc"%str_k] = mi_loc
		    #d_return['midUpLoc'] = mi_loc#Push to the attachReturn for later pulling
	    except Exception,error:raise StandardError,"[Build mid lip Up Locs | error: {0}]".format(error)  
	    
	    try:#>>> Aim some stuff =================================================================================
		mi_mouthMoveUpLoc = self.md_attachReturns[mi_mouthMoveTrackLoc]['upLoc']
		mi_mouthMoveUpLoc.mNode
		mi_noseUnder = self.md_rigList['noseUnderHandle'][0]
		mi_chin = self.md_rigList['chin'][0]
		mi_noseMove = self.md_rigList['noseMoveHandle'][0]
		mi_noseTop = self.md_rigList['noseTopHandle'][0]		
		mi_mouthMove = self.md_rigList.get('mouthMove')[0]		
		mi_lwrCenterHandle = self.md_rigList['lipLwrHandle']['center'][0]
		'''
		str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'lipLineBlend'
		mi_upLoc = d_buffer.get('upLoc') or d_build[str_tag].get('upLoc') or d_current.get('upLoc')
		str_baseKey = d_buffer.get('baseKey') or d_build[str_tag].get('baseKey') or 'uprLipRig'	
		'''
		'''
		d_build = {'noseUnderRig':{'mode':'singleTarget','aimVector':mi_go._vectorUpNegative,'upVector':mi_go._vectorAim,
			   'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseUnderTarget},
	       'noseTopRig':{'mode':'singleTarget','aimVector':mi_go._vectorUpNegative,'upVector':mi_go._vectorAim,
			  'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseMove}}
			  
			  
		'mouthMoveTrackLoc':{'mode':'singleVectorAim','v_aim':mi_go._vectorUp,'v_up':mi_go._vectorUp,
		                                'upLoc':mi_mouthMoveUpLoc,'aimTargets':[mi_noseTop]}  
		'''
		#'lipLwrRig':{'mode':'lipLineBlend','upLoc':mi_mouthMoveUpLoc}
		#mi_noseMove,mi_noseMove.masterGroup,
		#'midUpLoc':self.mi_uprLipSegmentMidUpLoc,
		d_build = {'lipUprRig':{'mode':'lipLineSegmentBlend','midUpLoc':self.mi_uprLipSegmentMidUpLoc,'midHandle':self.md_rigList['lipUprHandle']['center'][0],'v_up':mi_go._vectorUp},
		           'lipLwrRig':{'mode':'lipLineSegmentBlend','midUpLoc':self.mi_lwrLipSegmentMidUpLoc,'midHandle':self.md_rigList['lipLwrHandle']['center'][0],'v_up':mi_go._vectorUp}}
		self.aim_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Aim!] | error: {0}".format(error)	
	    

	    
	def _buildLipsOld_(self):
	    #>> Get some data =======================================================================================
	    """
	    Stuff to setup...
	    1) attach base to skull plate
	    2) What should
	    
	    """	 
	    try:#>> Query ========================================================================
		mi_go = self._go#Rig Go instance link	
	    except Exception,error:raise StandardError,"[Query | error: {0}".format(error) 
	    
	    try:#Setup Lip Tighteners ========================================================================	    	    	
		#Gonna setup our connections for the roll setup
		d_build = {'leftTigthen':{'handle':self.md_rigList['lipCornerHandle']['left'][0],
		                          'rigJoint':self.md_rigList['lipCornerRig']['left'][0],
		                          'uprDriver':self.md_rigList['uprLipTightener']['left'][0],
		                          'lwrDriver':self.md_rigList['lwrLipTightener']['left'][0]},
		           'rightTigthen':{'handle':self.md_rigList['lipCornerHandle']['right'][0],
		                          'rigJoint':self.md_rigList['lipCornerRig']['right'][0],
		                          'uprDriver':self.md_rigList['uprLipTightener']['right'][0],
		                          'lwrDriver':self.md_rigList['lwrLipTightener']['right'][0]}}
		
		l_keys = d_build.keys()
		int_lenMax = len(l_keys)
		for i,str_k in enumerate(l_keys):
		    try:
			try:#>> Query --------------------------------------------------------------------------
			    d_buffer = d_build[str_k]
			    mi_handle = d_buffer['handle']
			    str_rollAttr = ".r%s"%mi_go._jointOrientation[2]
			    mi_uprDriver = d_buffer['uprDriver']
			    mi_lwrDriver = d_buffer['lwrDriver']
			    mi_rigJoint = d_buffer['rigJoint']
			except Exception,error:raise StandardError,"[Query] | error: {0}".format(error)  
			
			try:#>> Progress -----------------------------------------------------------------------
			    str_message = "'%s' | Setting up tigtener"%(str_k)
			    self.log_info(str_message)
			    self.progressBar_set(status = str_message, progress = i, maxValue = int_lenMax)				    
			except Exception,error:raise StandardError,"[Progress bar] | error: {0}".format(error)  			    

			try:#>> Up locs -----------------------------------------------------------------------
			    mi_upLoc = mi_rigJoint.doLoc()
			    mi_upLoc.parent = mi_rigJoint
			    mi_go.connect_toRigGutsVis(mi_upLoc)
			except Exception,error:raise StandardError,"[Up locs ] | error: {0}".format(error)  	
			
			try:#>> Get Plugs -----------------------------------------------------------------------
			    self.log_info("'%s' | Setting up plugs"%(str_k))			    
			    mPlug_tightenUpr =  cgmMeta.cgmAttr(mi_handle,'tightenUpr', value= 0.0, attrType='float', defaultValue= 0.0,keyable=True, hidden=False)
			    mPlug_tightenLwr =  cgmMeta.cgmAttr(mi_handle,'tightenLwr', value= 0.0, attrType='float', defaultValue= 0.0,keyable=True, hidden=False)
			except Exception,error:raise StandardError,"[Plugs] | error: {0}".format(error)  
			
			try:#>> Args to nodes -----------------------------------------------------------------------
			    '''
			    l_lipCorner_uprDriver_jnt.rotateX = l_lipCorner_handle_anim.tightUpr;
			    l_lipCorner_lwrDriver_jnt.rotateX = -l_lipCorner_handle_anim.tightLwr;
			    '''				    
			    self.log_info("'%s' | Args to nodes"%(str_k))
			    d_argToBuild = {'upr':"%s%s = %s"%(mi_uprDriver.p_nameShort,str_rollAttr, mPlug_tightenUpr.p_combinedShortName),
			                    'lwr':"%s%s = -%s"%(mi_lwrDriver.p_nameShort,str_rollAttr, mPlug_tightenLwr.p_combinedShortName)}
			    
			    for str_argK in d_argToBuild.keys():
				try: 			    
				    str_arg = d_argToBuild[str_argK]
				    self.log_info("'%s' | argsToNodes..."%(str_argK))									    
				    self.log_info("building: %s"%(str_arg))
				    NodeF.argsToNodes(str_arg).doBuild()				
				except Exception,error:raise Exception,"['%s' fail]{%s}"%(str_argK,error)  			    
			except Exception,error:raise Exception,"[Args to nodes] | error: {0}".format(error) 
			
			try:#>> Setup aim on them -----------------------------------------------------------------------
			    try:#Vectors
				v_aim = mi_go._vectorAim
				if 'left' in str_k:
				    v_up = mi_go._vectorOut
				    mi_upLoc.__setattr__("t%s"%mi_go._jointOrientation[0],10)				    
				else:
				    v_up = mi_go._vectorOutNegative
				    mi_upLoc.__setattr__("t%s"%mi_go._jointOrientation[0],-10)				    
				    									
			    except Exception,error:raise StandardError,"[Vector query!] | error: {0}".format(error)
			    
			    for i,mDriver in enumerate([mi_uprDriver,mi_lwrDriver]):
				try:#For loop
				
				    if i == 0:
					mi_target = self.md_rigList['lipUprHandle']['center'][0]
				    else:
					mi_target = self.md_rigList['lipLwrHandle']['center'][0]
					
				    #Make a group
				    mi_aimOffsetGroup = cgmMeta.cgmObject(mDriver.doGroup(True),setClass=True)
				    mi_aimOffsetGroup.doStore('cgmName',mDriver.mNode)
				    mi_aimOffsetGroup.addAttr('cgmTypeModifier','aimOffset',lock=True)
				    mi_aimOffsetGroup.doName()
				    mDriver.connectChildNode(mi_aimOffsetGroup,"aimOffsetGroup","childObject")
				    
				    mc.aimConstraint(mi_target.mNode, mi_aimOffsetGroup.mNode,
					             weight = 1, aimVector = v_aim, upVector = v_up,
					             maintainOffset = 1, worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) 
				except Exception,error:raise StandardError,"[Driver loop : '%s']{%s}"%(mDriver.p_nameShort,error)
			except Exception,error:raise Exception,"[Aim setup] | error: {0}".format(error)
			
			try:#>> offset rot -----------------------------------------------------------------------
			    for i,mDriver in enumerate([mi_uprDriver,mi_lwrDriver]):
				try:#For loop
				    #Make a group
				    mi_rotOffsetGroup = cgmMeta.cgmObject(mDriver.doGroup(True),setClass=True)
				    mi_rotOffsetGroup.doStore('cgmName',mDriver.mNode)
				    mi_rotOffsetGroup.addAttr('cgmTypeModifier','rotOffset',lock=True)
				    mi_rotOffsetGroup.doName()
				    mDriver.connectChildNode(mi_rotOffsetGroup,"rotOffsetGroup","childObject")
				    
				    #Connect
				    cgmMeta.cgmAttr(mi_rotOffsetGroup,'r%s'%mi_go._jointOrientation[2]).doConnectIn("%s.r%s"%(mi_handle.mNode,mi_go._jointOrientation[0]))
				    
				except Exception,error:raise StandardError,"[Driver loop : '%s']{%s}"%(mDriver.p_nameShort,error)			    
			    
			except Exception,error:raise Exception,"[OffsetRot] | error: {0}".format(error) 			
		    except Exception,error:raise Exception,"[On: '%s']{%s}"%(str_k,error) 
	    except Exception,error:raise StandardError,"[Lip Tigteners | error: {0}".format(error) 
	    
	    try:#Smart Seal ===================================================================
		try:#Curve creation -------------------------------------------------------
		    self.progressBar_set(status = 'Curve creation!')
		    ml_uprLipRigJoints = self.md_rigList['lipUprRig']['left'] + self.md_rigList['lipUprRig']['center'] + self.md_rigList['lipUprRig']['right']
		    ml_lwrLipRigJoints = self.md_rigList['lipLwrRig']['left'] + self.md_rigList['lipLwrRig']['center'] + self.md_rigList['lipLwrRig']['right']
		    
		    for ml in [ml_uprLipRigJoints]:
			ml.insert(0,self.md_rigList['lipCornerRig']['left'][0])
			ml.append(self.md_rigList['lipCornerRig']['right'][0])
			
		    ml_uprLipHandles = self.md_rigList['lipUprHandle']['left'] + self.md_rigList['lipUprHandle']['center'] + self.md_rigList['lipUprHandle']['right']
		    ml_lwrLipHandles = self.md_rigList['lipLwrHandle']['left'] + self.md_rigList['lipLwrHandle']['center'] + self.md_rigList['lipLwrHandle']['right']
		    
			
		    ml_uprLipHandles.insert(0,self.md_rigList['lipCornerRig']['left'][0].uprDriverSkin)
		    ml_uprLipHandles.append(self.md_rigList['lipCornerRig']['right'][0].uprDriverSkin)
		    ml_lwrLipHandles.insert(0,self.md_rigList['lipCornerRig']['left'][0].lwrDriverSkin)
		    ml_lwrLipHandles.append(self.md_rigList['lipCornerRig']['right'][0].lwrDriverSkin)	
		    
		    for ml in ml_uprLipHandles,ml_lwrLipHandles:
			ml.insert(0,self.md_rigList['lipCornerRig']['left'][0])
			ml.append(self.md_rigList['lipCornerRig']['right'][0])		    
		    '''	
		    d_logs = {'uprLipRig':ml_uprLipRigJoints,
			      'lipLwrRig':ml_lwrLipRigJoints,
			      'uprLipHandle':ml_uprLipHandles,
			      'lwrLipHandle':ml_lwrLipHandles,
			      }
		    
		    for k in d_logs.iterkeys():
			self.log_info("%s..."%k)
			for mObj in d_logs[k]:
			    self.log_info("--> %s "%mObj.p_nameShort)	
			    '''
		    ml_curves = []
		    
		    try:#Upr driven curve
			_str_uprDrivenCurve = mc.curve(d=3,ep=[mi_obj.getPosition() for mi_obj in ml_uprLipRigJoints],os =True)
			mi_uprDrivenCrv = cgmMeta.cgmObject(_str_uprDrivenCurve,setClass=True)
			mi_uprDrivenCrv.addAttr('cgmName','uprLip',lock=True)
			mi_uprDrivenCrv.addAttr('cgmTypeModifier','driven',lock=True)
			mi_uprDrivenCrv.doName()
			ml_curves.append(mi_uprDrivenCrv)
			
			mi_uprLipSealCrv = mi_uprDrivenCrv.doDuplicate(False)
			mi_uprLipSealCrv.addAttr('cgmTypeModifier','lipSeal',lock=True)
			mi_uprLipSealCrv.doName()
			ml_curves.append(mi_uprLipSealCrv)
		    except Exception,error:raise StandardError,"[upper driven curve!] | error: {0}".format(error)  	    
		    
		    try:#Upper driver curve
			_str_uprDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_uprLipHandles],os =True)
			mi_uprDriverCrv = cgmMeta.cgmObject(_str_uprDriverCurve,setClass=True)
			mi_uprDriverCrv.doCopyNameTagsFromObject(mi_uprDrivenCrv.mNode,ignore=['cgmTypeModifier'])
			mi_uprDriverCrv.addAttr('cgmTypeModifier','driver',lock=True)
			mi_uprDriverCrv.doName()
			ml_curves.append(mi_uprDriverCrv)	    
		    except Exception,error:raise StandardError,"[upper driver curve!] | error: {0}".format(error)  	    
		    
		    try:#Lwr driven curve
			_str_lwrDrivenCurve = mc.curve(d=3,ep=[mi_obj.getPosition() for mi_obj in self.md_rigList['lipCornerRig']['left'] + ml_lwrLipRigJoints + self.md_rigList['lipCornerRig']['right']],os =True)
			mi_lwrDrivenCrv = cgmMeta.cgmObject(_str_lwrDrivenCurve,setClass=True)
			mi_lwrDrivenCrv.doCopyNameTagsFromObject(mi_uprDrivenCrv.mNode)
			mi_lwrDrivenCrv.addAttr('cgmName','lwrLip',lock=True)	    
			mi_lwrDrivenCrv.doName()
			ml_curves.append(mi_lwrDrivenCrv)	
			
			mi_lwrLipSealCrv = mi_lwrDrivenCrv.doDuplicate(False)
			mi_lwrLipSealCrv.addAttr('cgmTypeModifier','lipSeal',lock=True)
			mi_lwrLipSealCrv.doName()
			ml_curves.append(mi_lwrLipSealCrv)
		    except Exception,error:raise StandardError,"[upper driven curve!] | error: {0}".format(error)  	    
		    
		    try:#Lwr driver curve
			_str_lwrDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_lwrLipHandles],os =True)
			mi_lwrDriverCrv = cgmMeta.cgmObject(_str_lwrDriverCurve,setClass=True)
			mi_lwrDriverCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
			mi_lwrDriverCrv.addAttr('cgmName','lwrLip',lock=True)	    
			mi_lwrDriverCrv.doName()
			ml_curves.append(mi_lwrDriverCrv)	    	    	    
		    except Exception,error:raise StandardError,"[upper driver curve!] | error: {0}".format(error)  	    
		    
		    try:#SmartLipSeal curve
			_str_smartLipSealCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_lwrLipHandles],os =True)
			mi_smartLipSealCrv = cgmMeta.cgmObject(_str_smartLipSealCurve,setClass=True)
			mi_smartLipSealCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
			mi_smartLipSealCrv.addAttr('cgmName','smartLipSeal',lock=True)	    
			mi_smartLipSealCrv.doName()
			ml_curves.append(mi_smartLipSealCrv)	    	    	    
		    except Exception,error:raise StandardError,"[smartLipSeal curve] | error: {0}".format(error)  
		    
		    try:
			for mi_crv in ml_curves:#Parent to rig null
			    mi_crv.parent = mi_go._i_rigNull#used to be deformNull
			    
			#for mi_crv in [mi_smartLipSealCrv,mi_lwrLipSealCrv,mi_uprLipSealCrv]:
			    #mi_crv.parent = mi_go._i_rigNull
			    
		    except Exception,error:raise StandardError,"[Curve parenting] | error: {0}".format(error)  
		except Exception,error:raise StandardError,"[Curve creation] | error: {0}".format(error)   
	    
		
		'''	
		try:#Locators and aiming -------------------------------------------------------
		    self.progressBar_set(status = 'Locator creation!')
		    
		    #Make a loc group
		    mi_locGroup = cgmMeta.cgmObject(mc.group(em=True))
		    mi_locGroup.parent = mi_go._i_constrainNull
		    mi_locGroup.addAttr('cgmTypeModifier','locGroup')
		    mi_locGroup.doName()
		    mi_locGroup.parent = mi_go._i_rigNull
		    self.ml_toVisConnect.append(mi_locGroup)
		    
		    ml_locs = []
		    self.progressBar_setMaxStepValue(len(ml_uprLipRigJoints + ml_lwrLipRigJoints))	
		    
		    for i,mi_obj in enumerate(ml_uprLipRigJoints + ml_lwrLipRigJoints):
			try:
			    self.progressBar_iter(status = ("Curve locator: '%s'"%mi_obj.p_nameShort))			    
			    
			    try:#Loc creation -----------------------------------------------------------
				mi_loc = mi_obj.doLoc()
				ml_locs.append(mi_loc)
				mi_locShape = cgmMeta.cgmNode(mi_loc.getShapes()[0])
				mi_locShape.localScaleX = mi_go._f_skinOffset
				mi_locShape.localScaleY = mi_go._f_skinOffset
				mi_locShape.localScaleZ = mi_go._f_skinOffset
				mi_loc.parent = mi_locGroup
			    except Exception,error:raise StandardError,"[loc creation] | error: {0}".format(error)  	    
			    #> Aim constraint
			    #mi_root = mi_obj.root
			    #mi_root.parent = self._i_constrainNull
			    #try:mc.aimConstraint(mi_loc.mNode,mi_root.mNode,maintainOffset = False, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
			    #except Exception,error:raise StandardError,"[aim constrai]{%s}%s"%(error)  	    
			    #Attach to curve
			    if i < len(ml_uprLipRigJoints):mi_crv = mi_uprDrivenCrv
			    else:mi_crv = mi_lwrDrivenCrv
			    try:crvUtils.attachObjToCurve(mi_loc.mNode,mi_crv.mNode)
			    except Exception,error:raise StandardError," attach| %s "%(error)  	    
			    self.md_attachReturns[mObj] = {'posLoc':mi_loc,'posLocShape':mi_locShape}#store it
			except Exception,error:raise StandardError,"%s | '%s' loc setup | %s "%(i,mi_obj.p_nameShort,error)  	    
		    
		except Exception,error:
		    raise StandardError,"locator/aim setup | %s"%(error)
		'''
		try:#Lip setup -------------------------------------------------------
		    try:#Wire deformers -------------------------------------------------------------
			self.progressBar_set(status = 'Smart Seal - Wire deformer...')
			_l_return = mc.wire(mi_uprDrivenCrv.mNode, w = mi_uprDriverCrv.mNode, gw = False, en = 1, ce = 0, li =0)
			mi_uprWire = cgmMeta.cgmNode(_l_return[0])
			mi_uprWire.doStore('cgmName',mi_uprDrivenCrv.mNode)
			mi_uprWire.doName()
			_l_return = mc.wire(mi_lwrDrivenCrv.mNode, w = mi_lwrDriverCrv.mNode, gw = False, en = 1, ce = 0, li =0)
			mi_lwrWire = cgmMeta.cgmNode(_l_return[0])
			mi_lwrWire.doStore('cgmName',mi_lwrDrivenCrv.mNode)
			mi_lwrWire.doName()
			
			mi_uprDriverCrv.parent = mi_go._i_rigNull
			mi_lwrDriverCrv.parent = mi_go._i_rigNull			
		    except Exception,error:raise StandardError,"[wire deformer!] | error: {0}".format(error)  	    
		    
		    try:#Skin driver curve ---------------------------------------------------------
			self.progressBar_set(status = 'Smart Seal - Skin lip curves...')
			
			ml_uprSkinJoints = ml_uprLipHandles
			ml_lwrSkinJoints = ml_lwrLipHandles
			md_skinSetup = {'upr':{'ml_joints':ml_uprSkinJoints,'mi_crv':mi_uprDriverCrv},
			                'lwr':{'ml_joints':ml_lwrSkinJoints,'mi_crv':mi_lwrDriverCrv}}
			for k in md_skinSetup.keys():
			    d_crv = md_skinSetup[k]
			    str_crv = d_crv['mi_crv'].p_nameShort
			    l_joints = [mi_obj.p_nameShort for mi_obj in d_crv['ml_joints']]
			    self.log_info(" %s | crv]{%s} | joints: %s"%(k,str_crv,l_joints))
			    try:
				mi_skinNode = cgmMeta.cgmNode(mc.skinCluster ([mi_obj.mNode for mi_obj in d_crv['ml_joints']],
				                                              d_crv['mi_crv'].mNode,
				                                              tsb=True,
				                                              maximumInfluences = 3,
				                                              normalizeWeights = 1,dropoffRate=2.5)[0])
			    except Exception,error:raise StandardError,"skinCluster] | error: {0}".format(error)  	    
			    d_crv['mi_skinNode'] = mi_skinNode
		    except Exception,error:raise StandardError,"[skinning drive]{%s}s"%(error)  	    
		    
		    try:#Blendshape the smart lipSeal curve ---------------------------------------------
			self.progressBar_set(status = 'Smart Seal - Blendshape...')
			
			_str_bsNode = mc.blendShape([mi_uprDriverCrv.mNode,mi_lwrDriverCrv.mNode],mi_smartLipSealCrv.mNode)[0]
			mi_bsNode = cgmMeta.cgmNode(_str_bsNode,setClass=True)
			mi_bsNode.doStore('cgmName',mi_smartLipSealCrv.mNode)
			mi_bsNode.doName()
			mi_sealAttrHolder = self.md_rigList['mouthMove'][0]
			
			mPlug_height = cgmMeta.cgmAttr(mi_sealAttrHolder,'lipSealHeight',attrType = 'float', defaultValue=.5, minValue = 0, maxValue = 1)
			l_bsAttrs = deformers.returnBlendShapeAttributes(mi_bsNode.mNode)
			d_return = NodeF.createSingleBlendNetwork([mi_sealAttrHolder.mNode,'lipSealHeight'],
			                                          [mi_sealAttrHolder.mNode,'lipSealHeight_upr'],
			                                          [mi_sealAttrHolder.mNode,'lipSealHeight_lwr'],
			                                          keyable=True)	
			#Connect                                  
			d_return['d_result1']['mi_plug'].doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[0]))
			d_return['d_result2']['mi_plug'].doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[1]))
		    except Exception,error:raise StandardError,"[smartLipSeal bsNod]{%s}s"%(error)  	
		    
		    try:#Wire deform the uper and lwr lipSeal lids ---------------------------------------------------------
			self.progressBar_set(status = 'Smart Seal - wire deform setup...')		    
			#Build our lipSeal match wire deformers
			mPlug_height.value = 0	    
			_l_return = mc.wire(mi_lwrLipSealCrv.mNode, w = mi_smartLipSealCrv.mNode, gw = False, en = 1, ce = 0, li =0)
			mi_lwrLipSealWire = cgmMeta.cgmNode(_l_return[0])
			mi_lwrLipSealWire.doStore('cgmName',mi_lwrDrivenCrv.mNode)
			mi_lwrLipSealWire.addAttr('cgmTypeModifier','lipSeal')	    
			mi_lwrLipSealWire.doName()
			mc.setAttr("%s.scale[0]"%mi_lwrLipSealWire.mNode,0)
			
			mPlug_height.value = 1
			_l_return = mc.wire(mi_uprLipSealCrv.mNode, w = mi_smartLipSealCrv.mNode, gw = False, en = 1, ce = 0, li =0)
			mi_uprLipSealWire = cgmMeta.cgmNode(_l_return[0])
			mi_uprLipSealWire.doStore('cgmName',mi_uprDrivenCrv.mNode)
			mi_uprLipSealWire.addAttr('cgmTypeModifier','lipSeal')	    
			mi_uprLipSealWire.doName()
			mc.setAttr("%s.scale[0]"%mi_uprLipSealWire.mNode,0)
			
			mPlug_height.value = .5#back to default
		    except Exception,error:raise StandardError,"[lipSeal target wire]{%s}s"%(error)  	
		    
		    try:#Blendshape the upr and lwr curves to smart lipSeal targets------------------------------------
			mPlug_lipSeal = cgmMeta.cgmAttr(mi_sealAttrHolder,'lipSeal',attrType = 'float', keyable=True, minValue=0, maxValue=1, defaultValue=0)
			d_blendshapeLipSeal = {'upr':{'mi_target':mi_uprLipSealCrv,'mi_driven':mi_uprDrivenCrv},
			                       'lwr':{'mi_target':mi_lwrLipSealCrv,'mi_driven':mi_lwrDrivenCrv}}
			for k in d_blendshapeLipSeal.keys():
			    d_buffer = d_blendshapeLipSeal[k]
			    mi_target = d_buffer['mi_target']
			    mi_driven = d_buffer['mi_driven']
			    _str_bsNode = mc.blendShape(mi_target.mNode,mi_driven.mNode)[0]
			    mi_bsNode = cgmMeta.cgmNode(_str_bsNode,setClass=True)
			    mi_bsNode.doStore('cgmName',mi_uprDrivenCrv.mNode)
			    mi_bsNode.doName()
			    l_bsAttrs = deformers.returnBlendShapeAttributes(mi_bsNode.mNode)
			    mPlug_lipSeal.doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[0]))
		    except Exception,error:raise StandardError,"[lipSeal setup!]{%s}s"%(error)  	
		except Exception,error:
		    raise StandardError,"[lip setup |error: {0}]".format(error)   	        
	    except Exception,error:
		raise StandardError,"[Smart Seal setup fail]{ %s}"%(error) 
	    
	    try:#Template Curve duplication ====================================================================================
		self.progressBar_set(status = 'Template Curve duplication')  
		d_toDup = {'mouthTopTrace':self.mi_mouthTopCastCrv,
		           'mouthBaseTrace':self.mi_mouthLowCastCrv}
		for str_k in d_toDup.iterkeys():
		    mi_dup = cgmMeta.cgmObject( mc.duplicate(d_toDup[str_k].mNode,po=False,ic=True,rc=True)[0],setClass=True )
		    mi_dup.cgmType = 'traceCrv'
		    mi_dup.cgmName = mi_dup.cgmName.replace('Cast','')
		    mi_dup.doName()
		    cgmMeta.cgmAttr(mi_dup,'translate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'rotate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'scale',lock = False, keyable = True)
		    mi_dup.parent = mi_go._i_rigNull
		    
		    ml_curves.append(mi_dup)
		    self.__dict__["mi_%sCrv"%str_k] = mi_dup
		
		#for mi_crv in ml_curves:#Parent to rig null
		    #mi_crv.parent = mi_go._i_rigNull
		#self.ml_toVisConnect.extend(ml_curves)
	    except Exception,error:raise StandardError,"[Template Curve] | error: {0}".format(error)   
	    
	    try:#Build plates ====================================================================================
		md_plateBuilds = {'uprLip':{'crvs':[self.mi_mouthTopCastCrv,self.mi_lipOverTraceCrv,self.mi_lipUprCrv]},
		                  #'uprLipFollow':{'crvs':[self.mi_mouthTopTraceCrv,mi_uprDrivenCrv],'mode':'liveSurface'},
		                  'lwrLip':{'crvs':[self.mi_lipLwrCrv,self.mi_lipUnderTraceCrv,self.mi_mouthLowCastCrv]},}
		                  #'lwrLipFollow':{'crvs':[mi_lwrDrivenCrv,self.mi_mouthBaseTraceCrv],'mode':'liveSurface'}}
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"[Plates] | error: {0}".format(error)	    
	    
	    try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		'''
				          'uprLipRibbon':{'target':self.mi_uprLipRibbon,
		                           'bindJoints':[self.md_rigList['lipCornerRig']['left'][0],
		                                         self.md_rigList['lipUprHandle']['center'][0],
		                                         self.md_rigList['lipCornerRig']['right'][0]]},
		          'lwrLipRibbon':{'target':self.mi_lwrLipRibbon,
		                           'bindJoints':[self.md_rigList['lipCornerRig']['left'][0],
		                                         self.md_rigList['lipLwrHandle']['center'][0],
		                                         self.md_rigList['lipCornerRig']['right'][0]]},	
							 
		1a					 
		d_build = {'uprLipTop':{'target':self.mi_mouthTopTraceCrv,
		                        'bindJoints':[self.md_rigList['smileLineRig']['left'][0],
		                                      self.md_rigList['noseUnderRig'][0],
		                                      self.md_rigList['smileLineRig']['right'][0]]},
		           'uprLipPlate':{'target':self.mi_uprLipPlate,
		                          'bindJoints':ml_uprLipRigJoints + self.md_rigList['noseUnderRig']},		           	          
		          'lwrLipPlate':{'target':self.mi_lwrLipPlate,
		                         'bindJoints':ml_lwrLipRigJoints + self.md_rigList['lipCornerRig']['left'] + self.md_rigList['lipCornerRig']['right'] +self.md_rigList['chin']},#+ [self.md_rigList['smileLineRig']['left'][-1],		           
		           'lwrLipBase':{'target':self.mi_mouthBaseTraceCrv,
		                         'bindJoints':[self.md_rigList['smileLineRig']['left'][-1],
		                                       self.md_rigList['chin'][0],		                                       
		                                       self.md_rigList['smileLineRig']['right'][-1]]},}					 
		'''
		d_build = {'uprLipPlate':{'target':self.mi_uprLipPlate,
		                          'bindJoints':ml_uprLipRigJoints + self.md_rigList['noseUnderRig'] + [self.md_rigList['nostrilRig']['left'][0],self.md_rigList['nostrilRig']['right'][0]]},		           	          
		          'lwrLipPlate':{'target':self.mi_lwrLipPlate,
		                         'bindJoints':ml_lwrLipRigJoints + [self.md_rigList['lipCornerRig']['left'][0].lwrDriverSkin,self.md_rigList['lipCornerRig']['right'][0].uprDriverSkin] +self.md_rigList['chin']}}
		self.skin_fromDict(d_build)

	    except Exception,error:raise StandardError,"[Skinning] | error: {0}".format(error)	    
	    
	    try:#Reverse curve ====================================
		'''
		Setup driven reverse curve for upr and lower to drive the right side segments
		'''
		d_toDup = {'uprLipDrivenReverse':mi_uprDrivenCrv,
		           'lwrLipDrivenReverse':mi_lwrDrivenCrv}	
		
		for str_k in d_toDup.iterkeys():
		    mi_dup = cgmMeta.cgmObject( mc.duplicate(d_toDup[str_k].mNode,po=False,ic=1,rc=True)[0],setClass=True )
		    mi_dup.addAttr('cgmTypeModifier','ReverseDriven')
		    mi_dup.doName()
		    
		    mc.reverseCurve(mi_dup.mNode,rpo=True)
		    cgmMeta.cgmAttr(mi_dup,'translate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'rotate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'scale',lock = False, keyable = True)
		    #mi_dup.parent = mi_go._i_rigNull
		    
		    ml_curves.append(mi_dup)
		    self.__dict__["mi_%sCrv"%str_k] = mi_dup
	    except Exception,error:raise StandardError,"[Reverse Curves setup] | error: {0}".format(error)  	
	    
	    try:#Setup segments ========================================================================
		d_build = {'uprLipSegment':{'orientation':mi_go._jointOrientation,
		                            'left':{'mi_curve':mi_uprDrivenCrv},
		                            'right':{'mi_curve':self.mi_uprLipDrivenReverseCrv}},
		           'lwrLipSegment':{'orientation':mi_go._jointOrientation,
		                            'left':{'mi_curve':mi_lwrDrivenCrv},
		                            'right':{'mi_curve':self.mi_lwrLipDrivenReverseCrv}}}	
		self.create_segmentfromDict(d_build)
	    except Exception,error:raise StandardError,"[Segments] | error: {0}".format(error)  
	    
	    try:#Build mid lip Up Locs ========================================================================	
		d_build = {'uprLipSegment':{'left':{'mi_curve':mi_uprDrivenCrv},
		                            'right':{'mi_curve':self.mi_uprLipDrivenReverseCrv}},
		           'lwrLipSegment':{'left':{'mi_curve':mi_lwrDrivenCrv},
		                            'right':{'mi_curve':self.mi_lwrLipDrivenReverseCrv}}}
		
		#So we are gonna grab the upLocs from our segment returns and make our mid roll up locs from that constrainig between the end rolls
		for i,str_k in enumerate(d_build.keys()):
		    d_buffer = d_build[str_k]
		    ml_locs = []
		    for mi_curve in d_buffer['left']['mi_curve'],d_buffer['right']['mi_curve']:
			try:d_return = self.md_attachReturns[mi_curve]
			except Exception,error:
			    self.log_error(error)
			    raise Exception,"[Failed to find attachReturn: %s | %s]{%s}"%(str_k,i,error)
			try:ml_locs.append(d_return['ml_drivenJoints'][-1].upLoc)
			except Exception,error:
			    self.log_error(error)			    
			    raise Exception,"[Failed to find upLoc: %s | %s]{%s}"%(str_k,i,error)	
		    try:
			#Dup with connections for maintaining toggles
			mi_loc = cgmMeta.cgmObject( mc.duplicate(ml_locs[0].mNode,po=False,ic=True,rc=True)[0],setClass=True )
			mi_loc.parent = mi_go._i_rigNull
			mi_loc.addAttr('cgmTypeModifier','midLoc')
			mi_loc.doName()
		    except Exception,error:
			self.log_error(error)			
			raise Exception,"[%s | loc create]{%s}"%(str_k,error)	
		    mc.pointConstraint([mLoc.mNode for mLoc in ml_locs],mi_loc.mNode,maintainOffset = False)
		    #self.md_rigList["%sMidUpLoc"%str_k]
		    self.__dict__["mi_%sMidUpLoc"%str_k] = mi_loc
		    #d_return['midUpLoc'] = mi_loc#Push to the attachReturn for later pulling
	    except Exception,error:raise StandardError,"[Build mid lip Up Locs] | error: {0}".format(error)  
	    
	    try:#Setup Lip Roll ========================================================================
		#Gonna setup our connections for the roll setup
		d_build = {'uprLipRoll':{'handleKey':'lipUprHandle',
		                         'mi_crvLeft':mi_uprDrivenCrv,
		                         'mi_crvRight':self.mi_uprLipDrivenReverseCrv,
		                         'argAverageRoll':"%s = %s >< %s",
		                         'argLeftStart':'%s = -%s - %s',
		                         'argLeftEnd':'%s = -%s - %s%s - %s',
		                         'argRightStart':'%s = %s + %s',
		                         'argRightEnd':'%s = %s + %s%s + %s'},
		           'lwrLipRoll':{'handleKey':'lipLwrHandle',
		                         'mi_crvLeft':mi_lwrDrivenCrv,
		                         'mi_crvRight':self.mi_lwrLipDrivenReverseCrv,
		                         'argAverageRoll':"%s = -%s >< -%s",		                         
		                         'argLeftStart':'%s = %s - %s',
		                         'argLeftEnd':'%s = %s - %s%s - %s',
		                         'argRightStart':'%s = -%s + %s',
		                         'argRightEnd':'%s = -%s + %s%s + %s'}}
		
		l_keys = d_build.keys()
		int_lenMax = len(l_keys)
		#Put some plugs on the mouth move
		
		mi_mouthMove = self.md_rigList['mouthMove'][0]
		for i,str_k in enumerate(l_keys):
		    try:
			try:#>> Query --------------------------------------------------------------------------
			    d_buffer = d_build[str_k]
			    str_rigListKey = d_buffer['handleKey']
			    d_rigListBuffer = self.md_rigList[str_rigListKey]
			    mi_handleLeft = d_rigListBuffer['left'][0]
			    mi_handleRight = d_rigListBuffer['right'][0]
			    mi_handleCenter = d_rigListBuffer['center'][0]
			    mi_crvLeft = d_buffer['mi_crvLeft']
			    mi_crvRight = d_buffer['mi_crvRight']	
			    str_rollAttr = ".r%s"%mi_go._jointOrientation[2]
			    toFill_leftStart = d_buffer['argLeftStart']
			    toFill_leftEnd = d_buffer['argLeftEnd']
			    toFill_rightStart = d_buffer['argRightStart']
			    toFill_rightEnd = d_buffer['argRightEnd']
			    toFill_averageRoll = d_buffer['argAverageRoll']			    
			except Exception,error:raise StandardError,"[Query] | error: {0}".format(error)  
			
			try:#>> Progress -----------------------------------------------------------------------
			    str_message = "'%s' | Setting up roll"%(str_k)
			    self.log_info(str_message)
			    self.progressBar_set(status = str_message, progress = i, maxValue = int_lenMax)				    
			except Exception,error:raise StandardError,"[Progress bar] | error: {0}".format(error)  			    

			try:#>> Get Plugs -----------------------------------------------------------------------
			    self.log_info("'%s' | Setting up plugs"%(str_k))			    
			    mPlug_rollLeftDriver =  cgmMeta.cgmAttr(mi_handleCenter,'rollLeft', value= 0.0, attrType='float', defaultValue= 0.0,keyable=True, hidden=False)
			    mPlug_rollRightDriver =  cgmMeta.cgmAttr(mi_handleCenter,'rollRight', value= 0.0, attrType='float', defaultValue= 0.0,keyable=True, hidden=False)
			    mPlug_extendTwistDriver =  cgmMeta.cgmAttr(mi_handleCenter,'extendTwistToEnd', value= 1.0, attrType='float', defaultValue= 1.0,minValue=0,maxValue=1,keyable=True, hidden=False)
			    
			    mPlug_extendMidToCorner =  cgmMeta.cgmAttr(mi_handleCenter,'extendMidToCorner', value= .2, attrType='float', defaultValue= 0.2,keyable=True,minValue=0,maxValue=1, hidden=False)
			    mPlug_result_extendMidToCornerLeft =  cgmMeta.cgmAttr(mi_handleCenter,'result_extendMidToCornerLeft', attrType='float', hidden=True,lock=True)
			    mPlug_result_extendMidToCornerRight =  cgmMeta.cgmAttr(mi_handleCenter,'result_extendMidToCornerRight', attrType='float', hidden=True,lock=True)
			    
			    mPlug_extendCrossRoll =  cgmMeta.cgmAttr(mi_handleCenter,'extendCrossRoll', value= .3, attrType='float', defaultValue= 0.2,keyable=True,minValue=0,maxValue=1, hidden=False)
			    mPlug_result_extendCrossRollLeft =  cgmMeta.cgmAttr(mi_handleCenter,'result_extendCrossRollLeft', attrType='float', hidden=True,lock=True)
			    mPlug_result_extendCrossRollRight =  cgmMeta.cgmAttr(mi_handleCenter,'result_extendCrossRollRight', attrType='float', hidden=True,lock=True)
			    mPlug_result_averageRoll =  cgmMeta.cgmAttr(mi_handleCenter,'result_averageRoll', attrType='float', hidden=True,lock=True)
			    
			    mPlug_extendTwistToEndLeft = self.md_attachReturns[mi_crvLeft]['mPlug_extendTwist']
			    mPlug_extendTwistToEndRight = self.md_attachReturns[mi_crvRight]['mPlug_extendTwist']
			    mPlug_extendTwistToEndLeft.doConnectIn(mPlug_extendTwistDriver.p_combinedShortName)
			    mPlug_extendTwistToEndRight.doConnectIn(mPlug_extendTwistDriver.p_combinedShortName)
			    
			    mPlug_twistStartLeft = cgmMeta.cgmAttr(mi_crvLeft,'twistStart')
			    mPlug_twistEndLeft = cgmMeta.cgmAttr(mi_crvLeft,'twistEnd')
			    mPlug_twistStartRight = cgmMeta.cgmAttr(mi_crvRight,'twistStart')
			    mPlug_twistEndRight = cgmMeta.cgmAttr(mi_crvRight,'twistEnd')			    
			except Exception,error:raise Exception,"[Get Plugs] | error: {0}".format(error)  			    
			
			try:#>> Args to nodes -----------------------------------------------------------------------
			    self.log_info("'%s' | Args to nodes"%(str_k))
			    '''
			    uprLip_driven_splineIKCurve.twistStart= -center_lipUpr_handle_anim.rollLeft - (center_lipUpr_handle_anim.rotateX/2) ;
			    uprLip_driven_splineIKCurve.twistEnd = -center_lipUpr_handle_anim.rollLeft - center_lipUpr_handle_anim.rotateX - (center_lipUpr_handle_anim.rollRight/3);
			    uprLip_ReverseDriven_splineIKCurve.twistStart = center_lipUpr_handle_anim.rollRight + (center_lipUpr_handle_anim.rotateX/2);	    
			    uprLip_ReverseDriven_splineIKCurve.twistEnd = center_lipUpr_handle_anim.rollRight + center_lipUpr_handle_anim.rotateX + (center_lipUpr_handle_anim.rollLeft/3);
			    '''			    
			    try:#>>Build our dicts --------------------------------------------------------------------
				d_argToBuild = {'averageRoll':{'arg':toFill_averageRoll,
				                               'fill':(mPlug_result_averageRoll.p_combinedShortName,
				                                       mPlug_rollLeftDriver.p_combinedShortName,
				                                       mPlug_rollRightDriver.p_combinedShortName)},
				                'leftMidToStartResult':{'arg':"%s = %s * %s%s",
				                                        'fill':(mPlug_result_extendMidToCornerLeft.p_combinedShortName,
				                                                mPlug_extendMidToCorner.p_combinedShortName,
				                                                mi_handleCenter.p_nameShort,str_rollAttr)},
				                'rightMidToStartResult':{'arg':"%s = %s * %s%s",
				                                    'fill':(mPlug_result_extendMidToCornerRight.p_combinedShortName,
				                                            mPlug_extendMidToCorner.p_combinedShortName,
				                                            mi_handleCenter.p_nameShort,str_rollAttr)},	
				                'leftCrossResult':{'arg':"%s = %s * %s",
				                                   'fill':(mPlug_result_extendCrossRollLeft.p_combinedShortName,
				                                           mPlug_extendCrossRoll.p_combinedShortName,
				                                           mPlug_rollLeftDriver.p_combinedShortName)},
				                'rightCrossResult':{'arg':"%s = %s * %s",
				                                    'fill':(mPlug_result_extendCrossRollRight.p_combinedShortName,
				                                            mPlug_extendCrossRoll.p_combinedShortName,
				                                            mPlug_rollRightDriver.p_combinedShortName)},					                
				                'leftStart':{'arg':toFill_leftStart,
				                             'fill':(mPlug_twistStartLeft.p_combinedShortName,
				                                     mPlug_rollLeftDriver.p_combinedShortName,
				                                     mPlug_result_extendMidToCornerLeft.p_combinedShortName)},
				                'leftEnd':{'arg':toFill_leftEnd,
				                           'fill':(mPlug_twistEndLeft.p_combinedShortName,
				                                   mPlug_rollLeftDriver.p_combinedShortName,
				                                   mi_handleCenter.p_nameShort,str_rollAttr,
				                                   mPlug_result_extendCrossRollRight.p_combinedShortName)},
				                'rightStart':{'arg':toFill_rightStart,
				                              'fill':(mPlug_twistStartRight.p_combinedShortName,
				                                      mPlug_rollRightDriver.p_combinedShortName,
				                                      mPlug_result_extendMidToCornerRight.p_combinedShortName)},
				                'rightEnd':{'arg':toFill_rightEnd,
				                            'fill':(mPlug_twistEndRight.p_combinedShortName,
				                                    mPlug_rollRightDriver.p_combinedShortName,
				                                    mi_handleCenter.p_nameShort,str_rollAttr,				                                    
				                                    mPlug_result_extendCrossRollLeft.p_combinedShortName)}}					     
			    except Exception,error:raise Exception,"[Can't even build dict...] | error: {0}".format(error)  			    
			    
			    
			    for str_argK in d_argToBuild.keys():
				try:
				    try:
					self.log_info("'%s' | query"%(str_argK))					
					str_arg = d_argToBuild[str_argK]['arg']
					l_buffer = d_argToBuild[str_argK]['fill']
				    except Exception,error:raise Exception,"[Query] | error: {0}".format(error)  			    
				    try:
					self.log_info("'%s' | build arg from %s"%(str_argK, str_arg))										
					arg_built = str_arg%l_buffer
				    except Exception,error:
					#self.log_info("'%s' | arg: %s"%(str_argK,str_arg))										
					int_cnt = str_arg.count('%s')	
					raise StandardError,"['%s' | arg: %s | given fillers: %s | count: %s]{%s}"%(str_argK,str_arg,len(l_buffer),int_cnt,error)
				    self.log_info("'%s' | argsToNodes..."%(str_argK))									    
				    self.log_info("building: %s"%(arg_built))
				    NodeF.argsToNodes(arg_built).doBuild()				
				except Exception,error:raise Exception,"['%s' fail]{%s}"%(str_argK,error)  			    
			except Exception,error:raise Exception,"[Args to nodes] | error: {0}".format(error) 
			#Process
		    except Exception,error:raise StandardError,"['%s' fail]{%s}"%(str_k,error)  	    
	    except Exception,error:raise StandardError,"[Lip Roll] | error: {0}".format(error)  
	    
	    '''
	    #NEW
	    uprLip_driven_splineIKCurve.twistStart= -center_lipUpr_handle_anim.rollLeft - center_lipUpr_handle_anim.rotateX ;
	    uprLip_driven_splineIKCurve.twistEnd = -center_lipUpr_handle_anim.rollLeft - center_lipUpr_handle_anim.rotateX - (center_lipUpr_handle_anim.rollRight/3);
	    uprLip_ReverseDriven_splineIKCurve.twistStart = center_lipUpr_handle_anim.rollRight + center_lipUpr_handle_anim.rotateX;	    
	    uprLip_ReverseDriven_splineIKCurve.twistEnd = center_lipUpr_handle_anim.rollRight + center_lipUpr_handle_anim.rotateX + (center_lipUpr_handle_anim.rollLeft/3);
			
	    
	    uprLip_driven_splineIKCurve.twistStart= -l_lipUpr_handle_anim.rotateX ;
	    uprLip_ReverseDriven_splineIKCurve.twistStart = -r_lipUpr_handle_anim.rotateX;
	    
	    uprLip_driven_splineIKCurve.twistEnd = -l_lipUpr_handle_anim.rotateX - center_lipUpr_handle_anim.rotateX;
	    uprLip_ReverseDriven_splineIKCurve.twistEnd = -r_lipUpr_handle_anim.rotateX + center_lipUpr_handle_anim.rotateX;

	    lwrLip_driven_splineIKCurve.twistStart= -l_lipLwr_handle_anim.rotateX ;
	    lwrLip_ReverseDriven_splineIKCurve.twistStart = -r_lipLwr_handle_anim.rotateX;
	    
	    lwrLip_driven_splineIKCurve.twistEnd = -l_lipLwr_handle_anim.rotateX - center_lipLwr_handle_anim.rotateX;
	    lwrLip_ReverseDriven_splineIKCurve.twistEnd = -r_lipLwr_handle_anim.rotateX + center_lipLwr_handle_anim.rotateX;
	    try:#Build Ribbons --------------------------------------------------------------------------------------
		md_ribbonBuilds = {'uprLip':{'extrudeCrv':self.mi_lipUprCrv,
		                              'joints':self.md_rigList['lipCornerHandle']['left'] + self.md_rigList['lipCornerHandle']['right']},
		                   'lwrLip':{'extrudeCrv':self.mi_lipLwrCrv,
		                             'joints':self.md_rigList['lipCornerHandle']['left'] + self.md_rigList['lipCornerHandle']['right']}}
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"Ribbons | %s"%(error)
	    '''
	    try:#Special Locs ====================================================================================
		try:#Make a mouthMove track loc
		    mi_mouthMoveTrackLoc = self.md_rigList['mouthMove'][0].doLoc()
		    i_masterGroup = (cgmMeta.cgmObject(mi_mouthMoveTrackLoc.doGroup(True),setClass=True))
		    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
		    i_masterGroup.doName()
		    mi_mouthMoveTrackLoc.connectChildNode(i_masterGroup,'masterGroup','groupChild')
		    self.md_rigList['mouthMoveTrackLoc'] = [mi_mouthMoveTrackLoc]
		    mi_go.connect_toRigGutsVis(mi_mouthMoveTrackLoc,vis = 1, doShapes = True)#connect to guts vis switches
		    
		    i_masterGroup.parent = mi_go._i_deformNull
		except Exception,error:raise StandardError,"[MouthMove master group find fail |error: {0}]".format(error)
		    		
		try:str_mouthMoveTrackerMasterGroup = self.md_rigList['mouthMoveTrackLoc'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"[MouthMoveTrack master group find fail |error: {0}]".format(error)
		
		try:#Make a chin track loc
		    mi_chinTrackLoc = self.md_rigList['chin'][0].doLoc()
		    i_masterGroup = (cgmMeta.cgmObject(mi_chinTrackLoc.doGroup(True),setClass=True))
		    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
		    i_masterGroup.doName()
		    mi_chinTrackLoc.connectChildNode(i_masterGroup,'masterGroup','groupChild')
		    self.md_rigList['chinTrackLoc'] = [mi_chinTrackLoc]
		    
		    mi_go.connect_toRigGutsVis(mi_chinTrackLoc,vis = True)#connect to guts vis switches
		    i_masterGroup.parent = mi_go._i_deformNull
		except Exception,error:raise StandardError,"[ChinTrack master group find fail |error: {0}]".format(error)
		    		
		try:str_chinTrackerMasterGroup = self.md_rigList['chinTrackLoc'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"[ChinTrack master group find fail |error: {0}]".format(error)			
	    except Exception,error:raise StandardError,"[Special Locs!] | error: {0}".format(error)
	    
	    try:#Attach stuff to surfaces ====================================================================================
		#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_skullPlate = self.str_skullPlate
		mi_uprTeethPlate = self.mi_uprTeethPlate
		mi_lwrTeethPlate = self.mi_lwrTeethPlate
		
		str_uprLipPlate = self.mi_uprLipPlate.p_nameShort
		str_lwrLipPlate = self.mi_lwrLipPlate.p_nameShort

			
		d_build = {'mouthMove':{'mode':'blendStableAttach','defaultValue':.25,'followSuffix':'Jaw','attachTo':mi_uprTeethPlate.mNode},
		           'mouthMoveTrackLoc':{'attachTo':mi_uprTeethPlate.mNode},
		           'chinTrackLoc':{'attachTo':mi_lwrTeethPlate.mNode},		           
		           'chin':{'mode':'handleAttach','attachTo':mi_lwrTeethPlate.mNode},		           
		           ##'lipUprRig':{'mode':'handleAttach','attachTo':str_uprLipFollowPlate},
		           'lipOverRig':{'mode':'handleAttach','attachTo':str_uprLipPlate},		           
		           'lipUprHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode,
		                           'center':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode}},
		           'lipCornerRig':{'attachTo':mi_uprTeethPlate.mNode},#reg, will be driven by...
		           'lipCornerHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode},
		           ##'lipLwrRig':{'mode':'handleAttach','attachTo':str_lwrLipFollowPlate},
		           'lipUnderRig':{'mode':'handleAttach','attachTo':str_lwrLipPlate},	
		           'lipLwrHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode,
		                           'center':{'mode':'blendStableAttach','defaultValue':.6,'attachTo':mi_lwrTeethPlate.mNode,
		                                     'followSuffix':'Jaw','target0':mi_mouthMoveTrackLoc}}}
		
		"""'lipLwrHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode,
				'center':{'mode':'blendAttach','defaultValue':.6,
					  'followSuffix':'Jaw','target0':mi_mouthMoveTrackLoc}},"""		
		self.attach_fromDict(d_build)
		
	    except Exception,error:raise StandardError,"[Attach!] | error: {0}".format(error)
	    
	    try:#>> UprLip Center follow  =======================================================================================
		mObj = self.md_rigList['lipUprHandle']['center'][0]
		mi_offsetGroup = cgmMeta.cgmObject(mObj.doGroup(True),setClass=True)
		mi_offsetGroup.doStore('cgmName',mObj.mNode)
		mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		mi_offsetGroup.doName()
		mObj.connectChildNode(mi_offsetGroup,"offsetGroup","childObject")
		
		mc.pointConstraint([self.md_rigList['lipCornerHandle']['left'][0].mNode,
		                    self.md_rigList['mouthMove'][0].mNode,
		                    self.md_rigList['lipCornerHandle']['right'][0].mNode],
		                   mi_offsetGroup.mNode,skip = ["%s"%str_axis for str_axis in [mi_go._jointOrientation[0],mi_go._jointOrientation[2]]],
		                   maintainOffset = True)
	    except Exception,error:raise StandardError,"[Center upr lip offsetgroup!] | error: {0}".format(error)
	    
	    #self.log_infoNestedDict('md_attachReturns')	

	    try:#>>> Connect rig joints to handles ==================================================================
		d_build = {'lipUprRig':{'mode':'rigToSegment'},
		           'lipLwrRig':{'mode':'rigToSegment'},
		           'lipCornerRig':{},
		           'chinTrackLoc':{'driver':self.md_rigList['chin']},		           
		           'mouthMoveTrackLoc':{'driver':self.md_rigList['mouthMove']}}
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Connect!] | error: {0}".format(error)	
	    
	    try:#>>> Aim some stuff =================================================================================
		mi_mouthMoveUpLoc = self.md_attachReturns[mi_mouthMoveTrackLoc]['upLoc']
		mi_mouthMoveUpLoc.mNode
		mi_noseUnder = self.md_rigList['noseUnderHandle'][0]
		mi_chin = self.md_rigList['chin'][0]
		mi_noseMove = self.md_rigList['noseMoveHandle'][0]
		mi_noseTop = self.md_rigList['noseTopHandle'][0]		
		mi_mouthMove = self.md_rigList.get('mouthMove')[0]		
		mi_lwrCenterHandle = self.md_rigList['lipLwrHandle']['center'][0]
		'''
		str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'lipLineBlend'
		mi_upLoc = d_buffer.get('upLoc') or d_build[str_tag].get('upLoc') or d_current.get('upLoc')
		str_baseKey = d_buffer.get('baseKey') or d_build[str_tag].get('baseKey') or 'uprLipRig'	
		'''
		'''
		d_build = {'noseUnderRig':{'mode':'singleTarget','aimVector':mi_go._vectorUpNegative,'upVector':mi_go._vectorAim,
			   'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseUnderTarget},
	       'noseTopRig':{'mode':'singleTarget','aimVector':mi_go._vectorUpNegative,'upVector':mi_go._vectorAim,
			  'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseMove}}
			  
			  
		'mouthMoveTrackLoc':{'mode':'singleVectorAim','v_aim':mi_go._vectorUp,'v_up':mi_go._vectorUp,
		                                'upLoc':mi_mouthMoveUpLoc,'aimTargets':[mi_noseTop]},
			  
		'''
		#'lipLwrRig':{'mode':'lipLineBlend','upLoc':mi_mouthMoveUpLoc}
		#mi_noseMove,mi_noseMove.masterGroup,
		d_build = {'chin':{'mode':'singleTarget','v_aim':mi_go._vectorUp,'v_up':mi_go._vectorUp,
		                   'upLoc':mi_mouthMoveUpLoc,'aimTarget':mi_lwrCenterHandle.masterGroup},
		           'lipUprRig':{'mode':'lipLineSegmentBlend','midHandle':self.md_rigList['lipUprHandle']['center'][0],'midUpLoc':self.mi_uprLipSegmentMidUpLoc,'v_up':mi_go._vectorUp},
		           'lipLwrRig':{'mode':'lipLineSegmentBlend','midHandle':self.md_rigList['lipLwrHandle']['center'][0],'midUpLoc':self.mi_lwrLipSegmentMidUpLoc,'v_up':mi_go._vectorUp}}
		self.aim_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Aim!] | error: {0}".format(error)	
	    
	    try:#constrain mids ====================================================================================
		l_build = [{'obj':self.md_rigList['lipUprHandle']['left'][0],
	                   'targets':[self.md_rigList['lipUprHandle']['center'][0],
	                              self.md_rigList['lipCornerRig']['left'][0].uprDriverSkin],
	                   'mode':'parent'},
	                   {'obj':self.md_rigList['lipLwrHandle']['left'][0],
	                    'targets':[self.md_rigList['lipLwrHandle']['center'][0],
	                               self.md_rigList['lipCornerRig']['left'][0].lwrDriverSkin],
	                    'mode':'parent'},
		           {'obj':self.md_rigList['lipUprHandle']['right'][0],
		            'targets':[self.md_rigList['lipUprHandle']['center'][0],
		                       self.md_rigList['lipCornerRig']['right'][0].uprDriverSkin],
		            'mode':'parent'},
		            {'obj':self.md_rigList['lipLwrHandle']['right'][0],
		             'targets':[self.md_rigList['lipLwrHandle']['center'][0],
		                        self.md_rigList['lipCornerRig']['right'][0].lwrDriverSkin],
		             'mode':'parent'}]
			   
		for d in l_build:
		    mi_obj = d['obj']
		    ml_targets = d['targets']
		    str_mode = d.get('mode') or 'parent'
		    
		    self.d_buffer['mObj'] = mi_obj
		    self.d_buffer['ml_targets'] = ml_targets
		    
		    mi_offsetGroup = cgmMeta.cgmObject(mi_obj.doGroup(True),setClass=True)
		    mi_offsetGroup.doStore('cgmName',mi_obj.mNode)
		    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		    mi_offsetGroup.doName()
		    mObj.connectChildNode(mi_offsetGroup,"offsetGroup","childObject")
		    l_consts = []
		    if str_mode == 'pointOrient':
			l_consts.extend(mc.pointConstraint([mObj.mNode for mObj in ml_targets],mi_offsetGroup.mNode, maintainOffset = 1))
			l_consts.extend(mc.orientConstraint([mObj.mNode for mObj in ml_targets],mi_offsetGroup.mNode, maintainOffset = 1))
		    else:
			l_consts.extend(mc.parentConstraint([mObj.mNode for mObj in ml_targets],mi_offsetGroup.mNode, maintainOffset = 1))
		    for str_const in l_consts:
			try:cgmMeta.cgmNode(str_const).interpType = 0
			except Exception,error:self.log_error("Failed to set interp type: '%s']{%s}"%(str_const,error))	    			
	    except Exception,error:raise StandardError,"[constrain mids!] | error: {0}".format(error)	    

	    return
	
	def _buildSmileLines_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    try:#influenceJoints -----------------------------------------------------------------------
		d_build = {'sneerHandle':{},
		           'smileBaseHandle':{}}
		self.create_influenceJoints(d_build)
		self.log_infoDict(self.md_rigList['sneerHandleInfluenceJoints'],'sneerHandle')
	    except Exception,error:raise StandardError,"[influence joints | error: {0}]".format(error)	
	    
	    try:#Attach stuff to surfaces ====================================================================================		
		d_build = {'sneerHandleInfluenceJoints':{'attachTo':self.mi_jawPlate},#...rig attach so that we can drive it's position via the left lip corner
		           'sneerHandle':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseMoveRig'][0].p_nameShort},
		           'smileHandle':{'attachTo':self.mi_jawPlate},#...rig attach so that we can drive it's position via the left lip corner		           
		           'smileBaseHandle':{'attachTo':self.mi_lwrTeethPlate},#...rig attach so that we can drive it's position via the chin           	                         		           	           
		           }
		self.attach_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Attach! | error: {0}]".format(error)
	    
	    try:#>>> Connect rig joints to handles ==================================================================
		d_build = {'sneerHandleInfluenceJoints':{'mode':'pointConstraint','rewireFollicleOffset':True,
		                                         'left':{'targets':[self.md_rigList['sneerHandle']['left'][0]],
		                                                 'rewireHandle':self.md_rigList['sneerHandle']['left'][0]},
		                                         'right':{'targets':[self.md_rigList['sneerHandle']['right'][0]],
		                                                  'rewireHandle':self.md_rigList['sneerHandle']['right'][0]}},		           
		           'smileHandle':{'mode':'pointConstraint','rewireFollicleOffset':True,
		                          'left':{'targets':[self.md_rigList['lipCornerHandle']['left'][0]],
		                                  'rewireHandle':self.md_rigList['lipCornerHandle']['left'][0]},
		                          'right':{'targets':[self.md_rigList['lipCornerHandle']['right'][0]],#was lipCornerRig
		                                   'rewireHandle':self.md_rigList['lipCornerHandle']['right'][0]}},
		           'smileLineRig':{'mode':'rigToSegment'},
		           'smileBaseHandle':{'mode':'parentConstraint',
		                              'targets':[self.md_rigList['chinTrackLoc'][0]]}	           
		           }
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Connect! | error: {0}]".format(error) 	    
	    
	    try:#Setup segments ========================================================================
		d_build = {'smileLineSegment':{'orientation':mi_go._jointOrientation,
		                               'left':{'mi_curve':None},
		                               'right':{'mi_curve':None}}}	
		self.create_segmentfromDict(d_build)
	    except Exception,error:raise StandardError,"[Segments | error: {0}]".format(error)  
	    
	    
	    try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		d_build = {'smileLeft':{'target':self.md_rigList['smileLineSegment']['leftSegmentCurve'],
		                        'bindJoints':[self.md_rigList['sneerHandle']['left'][0].influenceJoint,
		                                      self.md_rigList['smileHandle']['left'][0],
		                                      self.md_rigList['nostrilRig']['left'][0],
		                                      self.md_rigList['smileBaseHandle']['left'][0]]},
		           'smileRight':{'target':self.md_rigList['smileLineSegment']['rightSegmentCurve'],
		                        'bindJoints':[self.md_rigList['sneerHandle']['right'][0].influenceJoint,
		                                      self.md_rigList['smileHandle']['right'][0],
		                                      self.md_rigList['nostrilRig']['right'][0],		                                      
		                                      self.md_rigList['smileBaseHandle']['right'][0]]}}
		self.skin_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Skinning! | error: {0}".format(error)	   


	def _buildSmileLinesOLD_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    try:#Template Curve duplication ====================================================================================
		self.progressBar_set(status = 'Template Curve duplication')  
		d_toDup = {'smileFollowLeft':self.mi_smileLeftCrv,
		           'smileFollowRight':self.mi_smileRightCrv}
		
		int_lenMax = len(d_toDup.keys())
		for i,str_k in enumerate(d_toDup.iterkeys()):
		    self.progressBar_set(status = "Curve duplication : '%s'"%str_k, progress =  i, maxValue = int_lenMax)		    				    		    		    
		    mi_dup = cgmMeta.cgmObject( mc.duplicate(d_toDup[str_k].mNode,po=False,ic=True,rc=True)[0],setClass=True )
		    mi_dup.cgmType = 'traceCrv'
		    mi_dup.cgmName = mi_dup.cgmName.replace('Cast','')
		    mi_dup.doName()
		    cgmMeta.cgmAttr(mi_dup,'translate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'rotate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'scale',lock = False, keyable = True)
		    mi_dup.parent = mi_go._i_rigNull
		    
		    self.__dict__["mi_%sCrv"%str_k] = mi_dup
		'''
		for mi_crv in ml_curves:#Parent to rig null
		    mi_crv.parent = mi_go._i_rigNull
		self.ml_toVisConnect.extend(ml_curves)
		'''
	    except Exception,error:raise StandardError,"[Curve duplication] | error: {0}".format(error)   	    
	    
	    '''
	    try:#Build Ribbons ===================================================================================================
		md_ribbonBuilds = {'smileLeft':{'extrudeCrv':self.mi_smileLeftCrv,'mode':'radialLoft','direction':'left',
		                                'aimObj':self.md_rigList['mouthMove'][0]},
		                   'smileRight':{'extrudeCrv':self.mi_smileRightCrv,'mode':'radialLoft','direction':'right',
		                                 'aimObj':self.md_rigList['mouthMove'][0]}}	
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"[Ribbons |error: {0}]".format(error)
	    '''	    
	    """'smileHandle':{'mode':'parentOnly','attachTo':None,
			   'left':{'parentTo':self.md_rigList['lipCornerHandle']['left'][0].p_nameShort},
			   'right':{'parentTo':self.md_rigList['lipCornerHandle']['right'][0].p_nameShort}},"""	    
	    try:#Attach stuff to surfaces ====================================================================================		
		str_skullPlate = self.str_skullPlate	
		d_build = {'smileLineRig':{},
		           #'sneerHandle':{'mode':'handleAttach'},
		           'sneerHandle':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseMoveRig'][0].masterGroup.p_nameShort},
		           'smileHandle':{},#Rig attach so that we can drive it's position via the left lip corner		           
		           'smileBaseHandle':{},#Rig attach so that we can drive it's position via the chin           	                         		           	           
		           }
		self.attach_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Attach!] | error: {0}".format(error)
	    	    
	    try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		d_build = {'smileLeft':{'target':self.mi_smileFollowLeftCrv,
		                        'bindJoints':[self.md_rigList['sneerHandle']['left'][0],
		                                      self.md_rigList['smileHandle']['left'][0],
		                                      self.md_rigList['smileBaseHandle']['left'][0]]},
		           'smileRight':{'target':self.mi_smileFollowRightCrv,
		                        'bindJoints':[self.md_rigList['sneerHandle']['right'][0],
		                                      self.md_rigList['smileHandle']['right'][0],
		                                      self.md_rigList['smileBaseHandle']['right'][0]]}}
		self.skin_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Skinning!] | error: {0}".format(error)	
	    
	    try:#>>> Connect rig joints to handles ==================================================================
		d_build = {'smileHandle':{'mode':'parentConstraint','rewireFollicleOffset':True,
		                          'left':{'targets':[self.md_rigList['lipCornerHandle']['left'][0]],
		                                  'rewireHandle':self.md_rigList['lipCornerHandle']['left'][0]},
		                          'right':{'targets':[self.md_rigList['lipCornerHandle']['right'][0]],#was lipCornerRig
		                                   'rewireHandle':self.md_rigList['lipCornerHandle']['right'][0]}},
		           'smileLineRig':{'mode':'rigToFollow',
		                           'left':{'attachTo':self.mi_smileFollowLeftCrv},
		                           'right':{'attachTo':self.mi_smileFollowRightCrv}},   
		           'smileBaseHandle':{'mode':'parentConstraint',
		                              'targets':[self.md_rigList['chinTrackLoc'][0]]}}
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Connect!] | error: {0}".format(error)	
	    return	
	
	def _buildCheeks_(self):
	    mi_go = self._go#Rig Go instance link   
	    '''
	    try:#influenceJoints -----------------------------------------------------------------------
		d_build = {'jawLine':{'skip':['left','right']},
		           'cheekRig':{'index':-1},
		           'cheekAnchor':{},
	                   'jawAnchor':{}}
		self.create_influenceJoints(d_build)
		self.log_infoDict(self.md_rigList['cheekRigInfluenceJoints'],'cheekRig')
		self.log_infoDict(self.md_rigList['jawLineInfluenceJoints'],'jawLine')
	    except Exception,error:raise StandardError,"[influence joints | error: {0}]".format(error)	
	    '''
	    
	    '''
	    try:#Attach stuff to surfaces ====================================================================================		
		d_build = {'cheekAnchorInfluenceJoints':{'attachTo':self.mi_jawPlate},#...rig attach so that we can drive it's position via the left lip corner
		           'jawAnchorInfluenceJoints':{'attachTo':self.mi_jawPlate},#...rig attach so that we can drive it's position
	                   'cheekAnchor':{'mode':'handleAttach','attachTo':self.mi_jawPlate},#...rig attach so that we can drive it's position         
	                   'cheekAnchor':{'mode':'handleAttach','attachTo':self.mi_jawPlate},#...rig attach so that we can drive it's position         	                   
	                   }
		self.attach_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Attach! | error: {0}]".format(error)
	    
	    try:#>>> Connect rig joints to handles ==================================================================
		d_build = {'sneerHandleInfluenceJoints':{'mode':'pointConstraint','rewireFollicleOffset':True,
	                                                 'left':{'targets':[self.md_rigList['sneerHandle']['left'][0]],
	                                                         'rewireHandle':self.md_rigList['sneerHandle']['left'][0]},
	                                                 'right':{'targets':[self.md_rigList['sneerHandle']['right'][0]],
	                                                          'rewireHandle':self.md_rigList['sneerHandle']['right'][0]}},		           
	                   'smileHandle':{'mode':'pointConstraint','rewireFollicleOffset':True,
	                                  'left':{'targets':[self.md_rigList['lipCornerHandle']['left'][0]],
	                                          'rewireHandle':self.md_rigList['lipCornerHandle']['left'][0]},
	                                  'right':{'targets':[self.md_rigList['lipCornerHandle']['right'][0]],#was lipCornerRig
	                                           'rewireHandle':self.md_rigList['lipCornerHandle']['right'][0]}},
	                   'smileLineRig':{'mode':'rigToSegment'},
	                   'smileBaseHandle':{'mode':'parentConstraint',
	                                      'targets':[self.md_rigList['chinTrackLoc'][0]]}	           
	                   }
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Connect! | error: {0}]".format(error) 		    
	    '''

	    try:#Build Curves ===================================================================================================
		md_curvesBuilds = {'uprCheekFollowLeft':{'pointTargets':self.md_rigList['uprCheekRig']['left'] + [self.md_rigList['smileLineRig']['left'][0]]},
		                   'uprCheekFollowRight':{'pointTargets':self.md_rigList['uprCheekRig']['right'] + [self.md_rigList['smileLineRig']['right'][0]]}}	
		self.create_curvesFromDict(md_curvesBuilds)
	    except Exception,error:raise StandardError,"[Build Curves!] | error: {0}".format(error)
	    
	    try:#Build plates ===================================================================================================
		md_plateBuilds = {'cheekLeft':{'mode':'cheekLoft','direction':'left','name':'cheek',
		                               'smileCrv':self.mi_smileLeftCrv},
		                  'cheekRight':{'mode':'cheekLoft','direction':'right','name':'cheek',
		                                'smileCrv':self.mi_smileRightCrv}}
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"[Plates!] | error: {0}".format(error)
	    
	    try:#Attach stuff to surfaces ====================================================================================
		#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_skullPlate = self.str_skullPlate
		str_jawPlate = self.mi_jawPlate.p_nameShort
		str_cheekLeftPlate = self.mi_cheekLeftPlate.p_nameShort
		str_cheekRightPlate = self.mi_cheekRightPlate.p_nameShort
		str_uprCheekFollowLeftCrv = self.mi_uprCheekFollowLeftCrv.p_nameShort
		str_uprCheekFollowRightCrv = self.mi_uprCheekFollowRightCrv.p_nameShort
			
		d_build = {'sneerHandle':{'mode':'parentOnly','attachTo':str_jawPlate,'parentTo':self.md_rigList['noseMoveRig'][0].masterGroup.p_nameShort},
		           'jawAnchor':{'mode':'handleAttach','attachTo':str_jawPlate,},
		           'cheekRig':{'mode':'rigAttach','attachTo':str_jawPlate,
		                       'left':{'attachTo':str_cheekLeftPlate},
		                       'right':{'attachTo':str_cheekRightPlate}},
		           'uprCheekRig':{'attachTo':str_jawPlate,},
		           'uprCheekHandles':{'attachTo':str_jawPlate,
		                              'left':{0:{'mode':'handleAttach'},
		                                      1:{}},
		                              'right':{0:{'mode':'handleAttach'},
		                                       1:{}}},		           	                         		           	           
		           'jawLine':{'attachTo':str_jawPlate,'mode':'handleAttach'},
		           }
		"""
		d_build = {'smileHandle':{}}
		"""
		self.attach_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Attach!] | error: {0}".format(error)
	    
	    #self.log_infoNestedDict('md_attachReturns')
	    
	    try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		mi_noseMove = self.md_rigList['noseMoveHandle'][0]		
		d_build = {'cheekFollowLeft':{'target':self.mi_uprCheekFollowLeftCrv,
		                              'bindJoints':[mi_noseMove,
		                                            self.md_rigList['smileLineRig']['left'][0],		                                            
		                                            self.md_rigList['smileLineRig']['left'][1],
		                                            self.md_rigList['uprCheekHandles']['left'][0]]},
		           'cheekFollowRight':{'target':self.mi_uprCheekFollowRightCrv,
		                              'bindJoints':[mi_noseMove,
		                                            self.md_rigList['smileLineRig']['right'][0],		                                            
		                                            self.md_rigList['smileLineRig']['right'][1],
		                                            self.md_rigList['uprCheekHandles']['right'][0]]},
		           'cheekRight':{'target':self.mi_cheekRightPlate,
		                        'bindJoints':self.md_rigList['jawLine']['right'] + self.md_rigList['smileLineRig']['right'] + self.md_rigList['jawAnchor']['right'] + self.md_rigList['uprCheekHandles']['right']},		           
		           'cheekLeft':{'target':self.mi_cheekLeftPlate,
		                        'bindJoints':self.md_rigList['jawLine']['left'] + self.md_rigList['smileLineRig']['left'] + self.md_rigList['jawAnchor']['left'] + self.md_rigList['uprCheekHandles']['left']}}
		self.skin_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Skinning! | error: {0}]".format(error)	
	    
	    try:#>>> Connect rig joints to handles ==================================================================
		'''
		{'lipCornerRig':{},
		           'mouthMoveTrackLoc':{'driver':self.md_rigList['mouthMove']}}
		self.md_rigList['mouthMoveTrackLoc']   
		'''
		"""
		'jawLine':{'mode':'rigToFollow',
		                      'skip':['center'],
		                      'left':{'attachTo':self.mi_cheekLeftPlate},
		                      'right':{'attachTo':self.mi_cheekRightPlate}}
		d_build = {'smileHandle':{'mode':'pointBlend',
		                          'left':{'targets':[self.md_rigList['lipCornerRig']['left'][0].masterGroup,self.md_rigList['mouthMoveTrackLoc'][0]]},
		                          'right':{'targets':[self.md_rigList['lipCornerRig']['right'][0].masterGroup,self.md_rigList['mouthMoveTrackLoc'][0]]}}}		
		"""
		d_build = {'uprCheekRig':{'mode':'rigToFollow',
		                          'left':{'attachTo':self.mi_cheekLeftPlate},
		                          'right':{'attachTo':self.mi_cheekRightPlate}},
		           'uprCheekHandles':{'mode':'rigToFollow',
		                              'index':1,#Only use one index
		                              'left':{'attachTo':self.mi_uprCheekFollowLeftCrv},
		                              'right':{'attachTo':self.mi_uprCheekFollowRightCrv}}}
		                      
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Connect!] | error: {0}".format(error)	
	    return
	
	def _buildCheeksOld_(self):
	    mi_go = self._go#Rig Go instance link    
	    
	    try:#Build Curves ===================================================================================================
		md_curvesBuilds = {'uprCheekFollowLeft':{'pointTargets':self.md_rigList['uprCheekRig']['left'] + [self.md_rigList['smileLineRig']['left'][0]]},
		                   'uprCheekFollowRight':{'pointTargets':self.md_rigList['uprCheekRig']['right'] + [self.md_rigList['smileLineRig']['right'][0]]}}	
		self.create_curvesFromDict(md_curvesBuilds)
	    except Exception,error:raise StandardError,"[Build Curves!] | error: {0}".format(error)
	    
	    try:#Build plates ===================================================================================================
		md_plateBuilds = {'cheekLeft':{'mode':'cheekLoft','direction':'left','name':'cheek',
		                               'smileCrv':self.mi_smileLeftCrv},
		                  'cheekRight':{'mode':'cheekLoft','direction':'right','name':'cheek',
		                                'smileCrv':self.mi_smileRightCrv}}
		
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"[Plates!] | error: {0}".format(error)
	    
	    try:#Attach stuff to surfaces ====================================================================================
		#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_skullPlate = self.str_skullPlate
		
		str_cheekLeftPlate = self.mi_cheekLeftPlate.p_nameShort
		str_cheekRightPlate = self.mi_cheekRightPlate.p_nameShort
		str_uprCheekFollowLeftCrv = self.mi_uprCheekFollowLeftCrv.p_nameShort
		str_uprCheekFollowRightCrv = self.mi_uprCheekFollowRightCrv.p_nameShort
			
		d_build = {'sneerHandle':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseMoveRig'][0].masterGroup.p_nameShort},
		           'jawAnchor':{'mode':'handleAttach'},
		           'cheekRig':{'mode':'rigAttach',
		                       'left':{'attachTo':str_cheekLeftPlate},
		                       'right':{'attachTo':str_cheekRightPlate}},
		           'uprCheekRig':{},
		           'uprCheekHandles':{'left':{0:{'mode':'handleAttach'},
		                                      1:{}},
		                              'right':{0:{'mode':'handleAttach'},
		                                       1:{}}},		           	                         		           	           
		           'jawLine':{'mode':'handleAttach'},
		           }
		"""
		d_build = {'smileHandle':{}}
		"""
		self.attach_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Attach!] | error: {0}".format(error)
	    
	    #self.log_infoNestedDict('md_attachReturns')
	    
	    try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		mi_noseMove = self.md_rigList['noseMoveHandle'][0]		
		d_build = {'cheekFollowLeft':{'target':self.mi_uprCheekFollowLeftCrv,
		                              'bindJoints':[mi_noseMove,
		                                            self.md_rigList['smileLineRig']['left'][0],		                                            
		                                            self.md_rigList['smileLineRig']['left'][1],
		                                            self.md_rigList['uprCheekHandles']['left'][0]]},
		           'cheekFollowRight':{'target':self.mi_uprCheekFollowRightCrv,
		                              'bindJoints':[mi_noseMove,
		                                            self.md_rigList['smileLineRig']['right'][0],		                                            
		                                            self.md_rigList['smileLineRig']['right'][1],
		                                            self.md_rigList['uprCheekHandles']['right'][0]]},
		           'cheekRight':{'target':self.mi_cheekRightPlate,
		                        'bindJoints':self.md_rigList['jawLine']['right'] + self.md_rigList['smileLineRig']['right'] + self.md_rigList['jawAnchor']['right'] + self.md_rigList['uprCheekHandles']['right']},		           
		           'cheekLeft':{'target':self.mi_cheekLeftPlate,
		                        'bindJoints':self.md_rigList['jawLine']['left'] + self.md_rigList['smileLineRig']['left'] + self.md_rigList['jawAnchor']['left'] + self.md_rigList['uprCheekHandles']['left']}}
		self.skin_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Skinning! | error: {0}]".format(error)	
	    
	    try:#>>> Connect rig joints to handles ==================================================================
		'''
		{'lipCornerRig':{},
		           'mouthMoveTrackLoc':{'driver':self.md_rigList['mouthMove']}}
		self.md_rigList['mouthMoveTrackLoc']   
		'''
		"""
		'jawLine':{'mode':'rigToFollow',
		                      'skip':['center'],
		                      'left':{'attachTo':self.mi_cheekLeftPlate},
		                      'right':{'attachTo':self.mi_cheekRightPlate}}
		d_build = {'smileHandle':{'mode':'pointBlend',
		                          'left':{'targets':[self.md_rigList['lipCornerRig']['left'][0].masterGroup,self.md_rigList['mouthMoveTrackLoc'][0]]},
		                          'right':{'targets':[self.md_rigList['lipCornerRig']['right'][0].masterGroup,self.md_rigList['mouthMoveTrackLoc'][0]]}}}		
		"""
		d_build = {'uprCheekRig':{'mode':'rigToFollow',
		                          'left':{'attachTo':self.mi_cheekLeftPlate},
		                          'right':{'attachTo':self.mi_cheekRightPlate}},
		           'uprCheekHandles':{'mode':'rigToFollow',
		                              'index':1,#Only use one index
		                              'left':{'attachTo':self.mi_uprCheekFollowLeftCrv},
		                              'right':{'attachTo':self.mi_uprCheekFollowRightCrv}}}
		                      
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Connect!] | error: {0}".format(error)	
	    return
	
	def _buildUprCheek_(self):
	    try:#>> Attach uprCheek rig joints =======================================================================================
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
			except Exception,error:raise StandardError,"[Failed to attach!] | error: {0}".format(error)
			try:#>> Setup curve locs ------------------------------------------------------------------------------------------
			    mi_controlLoc = d_return['controlLoc']
			    mi_crvLoc = mi_controlLoc.doDuplicate(parentOnly=False)
			    mi_crvLoc.addAttr('cgmTypeModifier','crvAttach',lock=True)
			    mi_crvLoc.doName()
			    mi_crvLoc.parent = mi_go._i_rigNull#parent to rigNull
			    d_return['crvLoc'] = mi_crvLoc #Add the curve loc
			except Exception,error:raise StandardError,"Loc setup. | ] | error: {0}".format(error)
    
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"[Attach rig joint loop. obj: '%s']!]{%s}"%(mObj.p_nameShort,error)	    
		    
		for mObj in ml_handles:
		    try:
			try:#>> Attach ------------------------------------------------------------------------------------------
			    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                    targetSurface = str_skullPlate,
				                                    createControlLoc = False,
				                                    createUpLoc = True,	
			                                            parentToFollowGroup = False,
				                                    orientation = mi_go._jointOrientation)
			except Exception,error:raise StandardError,"[Failed to attach!] | error: {0}".format(error)
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"Attach handle. obj: %s | error !]{%s}"(mObj.p_nameShort,error)	  
	    except Exception,error:
		raise StandardError,"[Attach |error: {0}]".format(error)
	    	    
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
		    mi_crv = cgmMeta.cgmObject(str_crv,setClass=True)
		    mi_crv.doCopyNameTagsFromObject(ml_rigJoints[0].mNode,ignore=['cgmIterator','cgmTypeModifier','cgmType'])
		    mi_crv.addAttr('cgmTypeModifier','driver',lock=True)
		    mi_crv.doName()
		    mi_crv.parent = mi_go._i_rigNull#parent to rigNull
		    self.ml_toVisConnect.append(mi_crv)	
		    d_uprCheekSide['mi_crv'] = mi_crv
		except Exception,error:raise StandardError,"[Failed to build crv. step: '%s'!]{%s}"%(i,error) 
		
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
				
			    except Exception,error:raise StandardError,"Failed to attach to crv. | ] | error: {0}".format(error)
			    try:#>> Aim the offset group  ------------------------------------------------------------------------------------------
				if obj_idx != int_lastIndex:
				    str_upLoc = d_current['upLoc'].mNode
				    str_offsetGroup = d_current['offsetGroup'].mNode				    
				    ml_targets = [ml_rigJoints[obj_idx+1]]	
				    mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup,
				                     maintainOffset = True, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
			    except Exception,error:raise StandardError,"Loc setup. | ] | error: {0}".format(error)
	
			    self.md_attachReturns[mObj] = d_current#push back
			except Exception,error:
			    raise StandardError,"Rig joint setup fail. obj: %s | ]{%s}"%(mObj.p_nameShort,error)	    
		except Exception,error:raise StandardError,"Rig joint setup fail. step: %s | ]{%s}"%(i,error) 
		
		try:#Skin -------------------------------------------------------------------------------------------------
		    mi_skinNode = cgmMeta.cgmNode(mc.skinCluster ([mObj.mNode for mObj in ml_handles],
		                                                  mi_crv.mNode,
		                                                  tsb=True,
		                                                  maximumInfluences = 3,
		                                                  normalizeWeights = 1,dropoffRate=2.5)[0])
		    mi_skinNode.doCopyNameTagsFromObject(mi_crv.mNode,ignore=['cgmType'])
		    mi_skinNode.doName()
		    d_uprCheekSide['mi_skinNode'] = mi_skinNode
		except Exception,error:raise StandardError,"Failed to skinCluster crv. step: %s | ]{%s}"%(i,error) 
		    
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
		    except Exception,error:raise StandardError,"Failed to attach. | ] | error: {0}".format(error)
		    self.md_attachReturns[mObj] = d_return
		except Exception,error:
		    raise StandardError,"Attach rig joint loop. obj: %s | ]{%s}"%(mObj.p_nameShort,error)	
		
	    return True

	def _lockNHide_(self):
	    #Lock and hide all 
	    for mHandle in self.ml_handlesJoints:
		try:
		    if 'jaw' not in mHandle.getAttr('cgmName'):
			cgmMeta.cgmAttr(mHandle,'scale',lock = True, hidden = True)
		    cgmMeta.cgmAttr(mHandle,'v',lock = True, hidden = True)		
		    mHandle._setControlGroupLocks()	
		except Exception,error:self.log_error("[mHandle: '%s']{%s}"%(mJoint.p_nameShort,error))
		
	    for mJoint in self.ml_rigJoints:
		try:
		    mJoint._setControlGroupLocks()	
		    cgmMeta.cgmAttr(mJoint,'v',lock = True, hidden = True)		
		except Exception,error:self.log_error("[mJoint: '%s']{%s}"%(mJoint.p_nameShort,error))
	    mi_go = self._go#Rig Go instance link
	    try:#parent folicles to rignull
		for k in self.md_attachReturns.keys():# we wanna parent 
		    d_buffer = self.md_attachReturns[k]
		    try:d_buffer['follicleFollow'].parent = mi_go._i_rigNull
		    except:pass
		    try:d_buffer['follicleAttach'].parent = mi_go._i_rigNull
		    except:pass	
		    try:
			if d_buffer.get('controlLoc'):
			    mi_go.connect_toRigGutsVis(d_buffer['controlLoc'],vis = True)#connect to guts vis switches
		    except:pass			    
	    except Exception,error:raise StandardError,"Parent follicles. | ] | error: {0}".format(error)
	    
	def returnRebuiltCurveString(self,crv, int_spans = 5, rpo = 0):
	    try:crv.mNode
	    except:crv = cgmMeta.cgmObject(crv)
	    
	    return mc.rebuildCurve (crv.mNode, ch=0, rpo=rpo, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=int_spans, d=3, tol=0.001)[0]		

	def attach_fromDict(self,d_build):
	    """
	    modes
	    rigAttach -- attaches follicle with control loc attached
	    handleAttach -- no control loc, just attach driver with constraint
	    blendAttach -- creates two attach points and a blend between the two -- mainly for the main movers (mouth, nose, eyes)
	    slideAttach -- control loc unattached, 
	    """
	    try:#>> Attach  =======================================================================================
		mi_go = self._go#Rig Go instance link
		str_skullPlate = self.str_skullPlate
		f_offsetOfUpLoc = self.f_offsetOfUpLoc
		
		for i,str_tag in enumerate(d_build.keys()):
		    try:
			md_buffer = {}
			ml_buffer = []
			buffer = self.md_rigList[str_tag]
			if type(buffer) == dict:
			    for str_side in ['left','right','center']:
				bfr_side = buffer.get(str_side)
				if bfr_side:
				    #self.log_info("%s:%s:%s"%(str_tag,str_side,bfr_side))
				    #ml_buffer.extend(bfr_side)
				    md_buffer[str_side] = bfr_side
			else:
			    #ml_buffer = buffer
			    md_buffer['reg'] = buffer
			
			for str_key in md_buffer.iterkeys():
			    ml_buffer = md_buffer[str_key]
			    int_len = len(ml_buffer)
			    
			    if d_build[str_tag].get(str_key):#if we have special instructions for a direction key...
				d_buffer = d_build[str_tag][str_key]
			    else:
				d_buffer = d_build[str_tag]
				
			    for ii,mObj in enumerate(ml_buffer):
				try:
				    if d_buffer.get(ii):#if we have special instructions for a index key...
					self.log_info("%s | %s > Utilizing index key"%(str_tag,str_key))
					d_use = d_buffer[ii]
					#self.log_infoNestedDict('d_buffer')
				    else:d_use = d_buffer
				    
				    self.d_buffer = d_use
				    
				    _attachTo = d_use.get('attachTo')
				    if _attachTo == None:_attachTo = str_skullPlate
				    _parentTo = d_use.get('parentTo') or False
				    str_mode = d_use.get('mode') or 'rigAttach'
				    str_base = mObj.getBaseName() or 'NONAMETAG'
				    b_connectFollicleOffset = d_buffer.get('connectFollicleOffset') or d_build[str_tag].get('connectFollicleOffset') or False 
				    
				    try:#Status update ----------------------------------------------------------------------
					str_message = "Attach : '%s' | mObj: '%s' | mode: '%s' | _attachTo: '%s' | parentTo: '%s' "%(str_tag,mObj.p_nameShort,str_mode, _attachTo,_parentTo)
					self.log_info(str_message)
					self.progressBar_set(status = str_message,progress = ii, maxValue= int_len)
				    except Exception,error:raise StandardError,"[Status Update] | error: {0}".format(error)					    

				    if str_mode == 'rigAttach' and _attachTo:
					try:#Attach
					    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
						                                    targetSurface = _attachTo,
						                                    createControlLoc = True,
						                                    createUpLoc = True,
						                                    f_offset = f_offsetOfUpLoc,
						                                    orientation = mi_go._jointOrientation)
					except Exception,error:raise StandardError,"[Rig mode attach. |error: {0}]".format(error)
					try:#>> Setup curve locs ------------------------------------------------------------------------------------------
					    mi_controlLoc = d_return['controlLoc']
					    mi_crvLoc = mi_controlLoc.doDuplicate(parentOnly=False)
					    mi_crvLoc.addAttr('cgmTypeModifier','followAttach',lock=True)
					    mi_crvLoc.doName()
					    mi_crvLoc.parent = mi_go._i_rigNull#parent to rigNull
					    d_return['followLoc'] = mi_crvLoc #Add the curve loc
					    self.md_attachReturns[mObj] = d_return										
					except Exception,error:raise StandardError,"[Loc setup. |error: {0}]".format(error)
					#self.log_info("%s mode attached!]{%s}"%(str_mode,mObj.p_nameShort))
				    
				    elif str_mode == 'handleAttach' and _attachTo:
					try:
					    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
						                                    targetSurface = _attachTo,
						                                    createControlLoc = False,
						                                    createUpLoc = True,	
						                                    parentToFollowGroup = False,
						                                    orientation = mi_go._jointOrientation)
					    self.md_attachReturns[mObj] = d_return					
					except Exception,error:raise StandardError,"[{0} fail! | error: {1}]".format(str_mode,error)				    
					
				    elif str_mode == 'blendHandleAttach' and _attachTo:
					'''
					This mode is for attaching to two surfaces
					'''
					try:#Blend attach ==================================================================================
					    try:#Query ---------------------------------------------------------------------------------------
						_target0 = d_use['target0'] #or self.md_rigList['stableJaw'][0]
						_defaultValue = d_use.get('defaultValue') or None
						_suffix = d_use.get('followSuffix') or 'Deformation'
						_d = {'handle':mObj,
						      'target0':_target0}
						self.d_buffer = _d						
						d_trackLocs = {'stable':{'attachTo':_target0},
					                       'def':{'attachTo':_attachTo},}
					    
					    except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)	
						
					    try:#Build Tracklocs -----------------------------------------------------------------------------
						for str_t in d_trackLocs.iterkeys():
						    try:
							d_sub = d_trackLocs[str_t]
							mi_loc = mObj.doLoc()
							mi_loc.addAttr('cgmTypeModifier',str_t)
							mi_loc.doName()
							str_tmp = '%s%sLoc'%(str_base,str_t.capitalize())
							_d['%sLoc'%str_t] = mi_loc
							mi_loc.parent = mi_go._i_rigNull#parent to rigNull
							try:#Attach
							    d_return = surfUtils.attachObjToSurface(objToAttach = mi_loc,
								                                    targetSurface = d_sub.get('attachTo'),
								                                    createControlLoc = False,
								                                    createUpLoc = False,	
								                                    attachControlLoc = False,
								                                    parentToFollowGroup = True,
								                                    orientation = mi_go._jointOrientation)
							    self.md_attachReturns[mi_loc] = d_return								
							except Exception,error:raise StandardError,"[Attach! | error: {0}]".format(error)
							self.log_info("'%s' created"%str_tmp)
							self.md_rigList[str_tmp] = [mi_loc]
							self.__dict__['mi_%s'%str_tmp] = mi_loc
							mObj.connectChildNode(mi_loc,'%sLoc'%str_t,'owner')
						    except Exception,error:raise StandardError,"!'%s' loc setup! | %s"%(str_t,error)				
					    except Exception,error:raise StandardError,"[Track locs! | error: {0}]".format(error)	
					    try:#Blend Setup -----------------------------------------------------------------------------
						#Query
						mi_handle = _d['handle']		    
						mi_0Loc = _d['stableLoc']
						mi_1Loc = _d['defLoc']
						mi_stableDef = _d['target0']
						
						if str_mode == 'blendStableAttach':
						    try:#Constrain the stable loc to the face
							mi_controlLoc = self.md_attachReturns[mi_0Loc]['controlLoc']
							#mc.pointConstraint(mi_faceDef.mNode,mi_controlLoc.mNode,maintainOffset = True)
							mi_controlLoc.parent = mi_stableDef
						    except Exception,error:raise StandardError,"[Stable loc controlLoc! | error: {0}]".format(error)
						    
						try:#Create constrain the handle master Group
						    str_parentConstraint = mc.parentConstraint([mi_0Loc.mNode,mi_1Loc.mNode],mi_handle.masterGroup.mNode,
							                                       maintainOffset = True)[0]
						except Exception,error:raise StandardError,"[Parent Constraint! | error: {0}]".format(error)
						
						try:
						    #EndBlend
						    d_blendFollowReturn = NodeF.createSingleBlendNetwork([mi_handle.mNode,'follow%s'%_suffix.capitalize()],
							                                                 [mi_handle.mNode,'resultStableFollow'],
							                                                 [mi_handle.mNode,'resultDefFollow'],
							                                                 keyable=True)
						    l_targetWeights = mc.parentConstraint(str_parentConstraint,q=True, weightAliasList=True)
						    #Connect                                  
						    d_blendFollowReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[1]))
						    d_blendFollowReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[0]))
						    d_blendFollowReturn['d_result1']['mi_plug'].p_hidden = True
						    d_blendFollowReturn['d_result2']['mi_plug'].p_hidden = True	
						    if _defaultValue is not None:
							d_blendFollowReturn['d_driver']['mi_plug'].p_defaultValue = _defaultValue
							d_blendFollowReturn['d_driver']['mi_plug'].value = _defaultValue
						except Exception,error:raise StandardError,"[Blend! | error: {0}]".format(error)
						
					    except Exception,error:
						#self.log_infoNestedDict('d_buffer')
						raise StandardError,"!Setup follow loc blend!|!] | error: {0}".format(error)
					except Exception,error:raise StandardError,"[{0} fail! | error: {1}]".format(str_mode,error)				    
				    elif str_mode == 'blendStableAttach' and _attachTo:
					try:#Blend attach ==================================================================================
					    try:#Query ---------------------------------------------------------------------------------------
						_target0 = d_use.get('target0') or self.md_rigList['stableJaw'][0]
						_d = {'handle':mObj,
	                                              'target0':_target0}
						self.d_buffer = _d
						_defaultValue = d_use.get('defaultValue') or None
						_suffix = d_use.get('followSuffix') or 'Deformation'
					    except Exception,error:raise StandardError,"[Query! | {0}]".format(error)
						
					    try:#Build Tracklocs -----------------------------------------------------------------------------
						d_trackLocs = {'stable':{'attachControlLoc':False,'parentToFollowGroup':False},
	                                                       'def':{'attachControlLoc':True,'parentToFollowGroup':True}}
						for str_t in d_trackLocs.iterkeys():
						    try:
							d_sub = d_trackLocs[str_t]
							mi_loc = mObj.doLoc()
							mi_loc.addAttr('cgmTypeModifier',str_t)
							mi_loc.doName()
							str_tmp = '%s%sLoc'%(str_base,str_t.capitalize())
							_d['%sLoc'%str_t] = mi_loc
							mi_loc.parent = mi_go._i_rigNull#parent to rigNull			    
							try:#Attach
							    d_return = surfUtils.attachObjToSurface(objToAttach = mi_loc,
			                                                                            targetSurface = _attachTo,
			                                                                            createControlLoc = True,
			                                                                            createUpLoc = False,	
			                                                                            attachControlLoc = d_sub.get('attachControlLoc'),
			                                                                            parentToFollowGroup = d_sub.get('parentToFollowGroup'),
			                                                                            orientation = mi_go._jointOrientation)
							    self.md_attachReturns[mi_loc] = d_return								
							except Exception,error:raise StandardError,"[Attach! | {0}]".format(error)
							
							self.log_info("'%s' created"%str_tmp)
							
							self.md_rigList[str_tmp] = [mi_loc]
							self.__dict__['mi_%s'%str_tmp] = mi_loc
							mObj.connectChildNode(mi_loc,'%sLoc'%str_t,'owner')
						    except Exception,error:raise StandardError,"!'%s' loc setup! | %s"%(str_t,error)				
					    except Exception,error:raise StandardError,"[Track locs! | {0}]".format(error)	
					    try:#Blend Setup -----------------------------------------------------------------------------
						#Query
						mi_handle = _d['handle']		    
						mi_stableLoc = _d['stableLoc']
						mi_defLoc = _d['defLoc']
						mi_stableDef = _d['target0']

						try:#Constrain the stable loc to the face
						    mi_controlLoc = self.md_attachReturns[mi_stableLoc]['controlLoc']
						    #mc.pointConstraint(mi_faceDef.mNode,mi_controlLoc.mNode,maintainOffset = True)
						    mi_controlLoc.parent = mi_stableDef
						except Exception,error:raise StandardError,"!Stable loc controlLoc! | %s"%(error)
						
						try:#Create constrain the handle master Group
						    str_parentConstraint = mc.parentConstraint([mi_stableLoc.mNode,mi_defLoc.mNode],mi_handle.masterGroup.mNode,
		                                                                               maintainOffset = True)[0]
						except Exception,error:raise StandardError,"!Parent Constraint! | %s"%(error)
						
						try:
						    #EndBlend
						    d_blendFollowReturn = NodeF.createSingleBlendNetwork([mi_handle.mNode,'follow%s'%_suffix.capitalize()],
		                                                                                         [mi_handle.mNode,'resultStableFollow'],
		                                                                                         [mi_handle.mNode,'resultDefFollow'],
		                                                                                         keyable=True)
						    l_targetWeights = mc.parentConstraint(str_parentConstraint,q=True, weightAliasList=True)
						    #Connect                                  
						    d_blendFollowReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[1]))
						    d_blendFollowReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[0]))
						    d_blendFollowReturn['d_result1']['mi_plug'].p_hidden = True
						    d_blendFollowReturn['d_result2']['mi_plug'].p_hidden = True	
						    if _defaultValue is not None:
							d_blendFollowReturn['d_driver']['mi_plug'].p_defaultValue = _defaultValue
							d_blendFollowReturn['d_driver']['mi_plug'].value = _defaultValue
						except Exception,error:raise StandardError,"[Blend! | {0}]".format(error)
						
					    except Exception,error:
						#self.log_infoNestedDict('d_buffer')
						raise StandardError,"!Setup follow loc blend!|!]{%s}"%(error)
					except Exception,error:raise StandardError,"[{0} fail! | error: {1}]".format(str_mode,error)				    
				    elif str_mode == 'blendAttach' and _attachTo:
					try:#Blend attach ==================================================================================
					    try:#Query ---------------------------------------------------------------------------------------
						try:
						    _ml_drivers = d_use.get('drivers') or d_build[str_tag][str_key].get('drivers') or False
						    if not cgmValid.isListArg(_ml_drivers):raise ValueError,"blend attach drivers must be list"
						    if len(_ml_drivers)!=2:raise ValueError,"blend attach drivers must be len 2"
						except Exception,error:raise StandardError,"[Drivers! | error: {0}]".format(error)	

						try:
						    _mControlObj = d_use.get('controlObj') or mObj
						except Exception,error:raise StandardError,"[controlObj! | error: {0}]".format(error)	
						    
						_d = {'handle':mObj,}
						self.d_buffer = _d
						
						_defaultValue = d_use.get('defaultValue') or None
						_suffix = d_use.get('followSuffix') or 'Deformation'
						if not cgmValid.isListArg(_attachTo):raise ValueError,"blend attach attachTo must be list"
						if len(_attachTo)!=2:raise ValueError,"blend attach attachTo must be len 2"
					    except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)	
						
					    try:#Build Tracklocs -----------------------------------------------------------------------------
						for i in range(2):
						    try:
							str_t = 'targ{0}'.format(i)
							mi_loc = mObj.doLoc()
							mi_loc.addAttr('cgmTypeModifier',str_t)
							mi_loc.doName()
							str_tmp = '%s%sLoc'%(str_base,str_t.capitalize())
							_d['{0}Loc'.format(str_t)] = mi_loc
							mi_loc.parent = mi_go._i_rigNull#parent to rigNull
							try:#Attach
							    d_return = surfUtils.attachObjToSurface(objToAttach = mi_loc,
									                            targetSurface = _attachTo[i],
									                            createControlLoc = True,
									                            createUpLoc = False,	
									                            attachControlLoc = False,
									                            parentToFollowGroup = False,
									                            orientation = mi_go._jointOrientation)							    
							    self.md_attachReturns[mi_loc] = d_return								
							except Exception,error:raise StandardError,"[Attach! | error: {0}]".format(error)
						    
							self.log_info("'%s' created"%str_tmp)
							self.md_rigList[str_tmp] = [mi_loc]
							self.__dict__['mi_%s'%str_tmp] = mi_loc
							mObj.connectChildNode(mi_loc,'%sLoc'%str_t,'owner')
						    except Exception,error:raise StandardError,"!'%s' loc setup! | %s"%(str_t,error)				
					    except Exception,error:raise StandardError,"[Track locs! | error: {0}]".format(error)	
					    try:#Blend Setup -----------------------------------------------------------------------------
						try:#Query
						    mi_handle = _d['handle']		    
						    mi_targ0Loc = _d['targ0Loc']
						    mi_targ1Loc = _d['targ1Loc']
						    mi_targ0Driver = self.md_attachReturns[mi_targ0Loc]['controlLoc']
						    mi_targ1Driver = self.md_attachReturns[mi_targ1Loc]['controlLoc']
						except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)	
						
						try:#Constrain the stable loc to the face
						    mi_targ0Driver.parent = _ml_drivers[0]
						    mi_targ1Driver.parent = _ml_drivers[1]
						except Exception,error:raise StandardError,"[Stable loc controlLoc! | error: {0}]".format(error)
						
						try:#Create constrain the handle master Group
						    str_parentConstraint = mc.parentConstraint([mi_targ0Loc.mNode,mi_targ1Loc.mNode],mi_handle.masterGroup.mNode,
						                                               maintainOffset = True)[0]
						except Exception,error:raise StandardError,"[Parent Constraint! | error: {0}]".format(error)
						
						try:
						    #EndBlend
						    d_blendFollowReturn = NodeF.createSingleBlendNetwork([_mControlObj.mNode,'follow%s'%_suffix.capitalize()],
		                                                                                         [_mControlObj.mNode,'resultTarg0Follow'],
		                                                                                         [_mControlObj.mNode,'resultTarg1Follow'],
		                                                                                         keyable=True)
						    l_targetWeights = mc.parentConstraint(str_parentConstraint,q=True, weightAliasList=True)
						    #Connect                                  
						    d_blendFollowReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[1]))
						    d_blendFollowReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[0]))
						    d_blendFollowReturn['d_result1']['mi_plug'].p_hidden = True
						    d_blendFollowReturn['d_result2']['mi_plug'].p_hidden = True	
						    if _defaultValue is not None:
							d_blendFollowReturn['d_driver']['mi_plug'].p_defaultValue = _defaultValue
							d_blendFollowReturn['d_driver']['mi_plug'].value = _defaultValue
						except Exception,error:raise StandardError,"[Blend! | error: {0}]".format(error)
						
					    except Exception,error:
						#self.log_infoNestedDict('d_buffer')
						raise StandardError,"!Setup follow loc blend!|!] | error: {0}".format(error)
					    
					    try:#connectFollicleOffset ==================================================================================
						if b_connectFollicleOffset:
						    for mi_loc in mi_targ0Loc,mi_targ1Loc:
							mi_follicleOffsetGroup = self.md_attachReturns[mi_loc]['offsetGroup']
							for attr in mi_go._jointOrientation[0]:
							    attributes.doConnectAttr ((_mControlObj.mNode+'.t%s'%attr),(mi_follicleOffsetGroup.mNode+'.t%s'%attr))						    
							
					    except Exception,error:raise StandardError,"[Connect Follicle Offset! | error: {0}]".format(error)					    
					except Exception,error:raise StandardError,"[{0} fail! | error: {1}]".format(str_mode,error)				    
				    elif str_mode == 'blendAttachStable' and _attachTo:
					try:#Blend attach ==================================================================================
					    try:#Query ---------------------------------------------------------------------------------------
						_target0 = d_use.get('target0') or self.md_rigList['stableJaw'][0]
						_mControlObj = d_use.get('controlObj') or mObj
						_d = {'handle':mObj,
					              'target0':_target0}
						self.d_buffer = _d
						_defaultValue = d_use.get('defaultValue') or None
						_suffix = d_use.get('followSuffix') or 'Deformation'
					    except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)	
						
					    try:#Build Tracklocs -----------------------------------------------------------------------------
						d_trackLocs = {'stable':{'attachControlLoc':False,'parentToFollowGroup':False},
					                       'def':{'attachControlLoc':True,'parentToFollowGroup':True}}
						for i,str_t in enumerate(d_trackLocs.keys()):
						    try:
							d_sub = d_trackLocs[str_t]
							mi_loc = mObj.doLoc()
							mi_loc.addAttr('cgmTypeModifier',str_t)
							mi_loc.doName()
							str_tmp = '%s%sLoc'%(str_base,str_t.capitalize())
							_d['%sLoc'%str_t] = mi_loc
							if str_t == 'def':
							    mi_loc.parent = mi_go._i_rigNull#parent to rigNull			    
							    try:#Attach
								d_return = surfUtils.attachObjToSurface(objToAttach = mi_loc,
								                                        targetSurface = _attachTo,
								                                        createControlLoc = True,
								                                        createUpLoc = False,	
								                                        attachControlLoc = d_sub.get('attachControlLoc'),
								                                        parentToFollowGroup = d_sub.get('parentToFollowGroup'),
								                                        orientation = mi_go._jointOrientation)
								self.md_attachReturns[mi_loc] = d_return								
							    except Exception,error:raise StandardError,"[Attach! | error: {0}]".format(error)
							
							self.log_info("'%s' created"%str_tmp)
							
							self.md_rigList[str_tmp] = [mi_loc]
							self.__dict__['mi_%s'%str_tmp] = mi_loc
							mObj.connectChildNode(mi_loc,'%sLoc'%str_t,'owner')
						    except Exception,error:raise StandardError,"!'%s' loc setup! | %s"%(str_t,error)				
					    except Exception,error:raise StandardError,"[Track locs! | error: {0}]".format(error)	
					    try:#Blend Setup -----------------------------------------------------------------------------
						#Query
						mi_handle = _d['handle']		    
						mi_stableLoc = _d['stableLoc']
						mi_defLoc = _d['defLoc']
						mi_stableDef = _d['target0']

						try:#Constrain the stable loc to the face
						    #mi_controlLoc = self.md_attachReturns[mi_stableLoc]['controlLoc']
						    #mc.pointConstraint(mi_faceDef.mNode,mi_controlLoc.mNode,maintainOffset = True)
						    #mi_controlLoc.parent = mi_stableDef
						    mi_stableLoc.parent = mi_stableDef
						except Exception,error:raise StandardError,"[Stable loc controlLoc! | error: {0}]".format(error)
						
						try:#Create constrain the handle master Group
						    str_parentConstraint = mc.parentConstraint([mi_stableLoc.mNode,mi_defLoc.mNode],mi_handle.masterGroup.mNode,
						                                               maintainOffset = True)[0]
						except Exception,error:raise StandardError,"[Parent Constraint! | error: {0}]".format(error)
						
						try:
						    #EndBlend
						    d_blendFollowReturn = NodeF.createSingleBlendNetwork([_mControlObj.mNode,'follow%s'%_suffix.capitalize()],
						                                                         [_mControlObj.mNode,'resultStableFollow'],
						                                                         [_mControlObj.mNode,'resultDefFollow'],
						                                                         keyable=True)
						    l_targetWeights = mc.parentConstraint(str_parentConstraint,q=True, weightAliasList=True)
						    #Connect                                  
						    d_blendFollowReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[1]))
						    d_blendFollowReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[0]))
						    d_blendFollowReturn['d_result1']['mi_plug'].p_hidden = True
						    d_blendFollowReturn['d_result2']['mi_plug'].p_hidden = True	
						    if _defaultValue is not None:
							d_blendFollowReturn['d_driver']['mi_plug'].p_defaultValue = _defaultValue
							d_blendFollowReturn['d_driver']['mi_plug'].value = _defaultValue
						except Exception,error:raise StandardError,"[Blend! | error: {0}]".format(error)
						
					    except Exception,error:
						#self.log_infoNestedDict('d_buffer')
						raise StandardError,"!Setup follow loc blend!|!] | error: {0}".format(error)
					except Exception,error:raise StandardError,"[{0} fail! | error: {1}]".format(str_mode,error)				    
				    elif str_mode == 'slideAttach' and _attachTo:
					try:
					    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
					                                            targetSurface = _attachTo,
					                                            createControlLoc = True,
					                                            createUpLoc = True,	
					                                            attachControlLoc = False,
					                                            parentToFollowGroup = False,
					                                            orientation = mi_go._jointOrientation)
					    self.md_attachReturns[mObj] = d_return					
					except Exception,error:raise StandardError,"[{0} fail! | error: {1}]".format(str_mode,error)
				    elif str_mode == 'slideHandleAttach' and _attachTo:
					'''
					Drive a handle position with offset
					'''
					try:
					    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
	                                                                            targetSurface = _attachTo,
	                                                                            createControlLoc = True,
	                                                                            createUpLoc = True,	
	                                                                            attachControlLoc = True,
	                                                                            parentToFollowGroup = False,
	                                                                            orientation = mi_go._jointOrientation)
					    self.md_attachReturns[mObj] = d_return					
					except Exception,error:raise StandardError,"[{0} fail! | error: {1}]".format(str_mode,error)
				    elif str_mode == 'parentOnly':
					try:mObj.masterGroup.parent = _parentTo
					except Exception,error:raise StandardError,"[parentTo. | error: {0}]".format(error)		    
					#self.log_info("%s parented!]{%s}"%(str_mode,mObj.p_nameShort))
				    else:
					raise NotImplementedError,"mode: %s "%str_mode
				except Exception,error:  raise StandardError,"attaching: %s | %s"%(mObj,error)				
		    except Exception,error:  raise StandardError,"'%s' | %s"%(str_tag,error)			    
	    except Exception,error:  raise StandardError,"[attach_fromDict |error: {0}]".format(error)	
	    
	def create_segmentfromDict(self,d_build):
	    '''
	    Handler for building segments from dicsts
	    
	    Modes:
	    
	    Flags
	    'index'(int) -- root dict flag to specify only using a certain index of a list
	    'skip'(string) -- skip one of the side flags - 'left','right','center'
	    '''
	    try:#>> Connect  =======================================================================================
		mi_go = self._go#Rig Go instance link
		
		for str_tag in d_build.iterkeys():
		    try:
			md_buffer = {}
			ml_buffer = []
			buffer = self.md_rigList[str_tag]
			if type(buffer) == dict:
			    for str_side in ['left','right','center']:
				    bfr_side = buffer.get(str_side)
				    if bfr_side:
					md_buffer[str_side] = bfr_side
			else:
			    md_buffer['reg'] = buffer 
			'''
			d_build = {'uprLipSegment':{'orientation':mi_go._jointOrientation,
			    'left':{'mi_curve':mi_uprDrivenCrv},
			    'right':{'mi_curve':self.mi_uprLipDrivenReverseCrv}}}
			'''
			int_len = len(md_buffer.keys())
			for i,str_key in enumerate(md_buffer.iterkeys()):
			    if d_build[str_tag].get(str_key):#if we have special instructions for a direction key...
				d_buffer = d_build[str_tag][str_key]
			    else:
				d_buffer = d_build[str_tag]	
			    ml_buffer = md_buffer[str_key]
			    int_len = len(ml_buffer)
			    
			    try:#Gather data ----------------------------------------------------------------------
				str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'default'
				str_orientation = d_buffer.get('orientation') or d_build[str_tag].get('orientation') or 'zyx' 
				mi_curve =  d_buffer.get('mi_curve') or d_build[str_tag].get('mi_curve') or None
				if mi_curve:str_curve = mi_curve.p_nameShort
				else:str_curve = None
				str_baseName = "{0}{1}".format(str_tag,str_key.capitalize())
			    except Exception,error:raise StandardError,"[Data gather!] | error: {0}".format(error)	
			    
			    try:#Status update ----------------------------------------------------------------------
				str_message = "Create Segment : '%s' %s | curve: '%s' | mode: '%s' "%(str_tag,str_key,str_curve,str_mode)
				self.log_info(str_message)
				self.progressBar_set(status = (str_message),progress = i, maxValue = int_len)	
			    except Exception,error:raise StandardError,"[Status update] | error: {0}".format(error)	

			    if str_mode == 'default':
				d_segReturn = rUtils.createSegmentCurve(ml_buffer, addMidTwist = False,useCurve = mi_curve, baseName = str_baseName,
				                                        moduleInstance = mi_go._mi_module, connectBy = 'trans')
			    else:
				raise NotImplementedError,"not implemented : mode: %s"%_str_mode
			    
			    try:#>> Store stuff ========================================================================
				'''
				d_return = {'mi_segmentCurve':mi_segmentCurve,'segmentCurve':mi_segmentCurve.mNode,'mi_ikHandle':mi_IK_Handle,'mi_segmentGroup':mi_grp,
				'l_driverJoints':self.l_driverJoints,'ml_driverJoints':ml_driverJoints,
				'scaleBuffer':mi_jntScaleBufferNode.mNode,'mi_scaleBuffer':mi_jntScaleBufferNode,'mPlug_extendTwist':self.mPlug_factorInfluenceIn,
				'l_drivenJoints':self.l_joints,'ml_drivenJoints':ml_joints}
				'''
				d_segReturn['mi_segmentGroup'].parent = mi_go._i_rigNull
				mi_curve = d_segReturn['mi_segmentCurve']
				self.md_rigList[str_tag]['{0}SegmentCurve'.format(str_key)] = mi_curve
				mi_curve.parent = mi_go._i_rigNull
				mi_go._i_rigNull.msgList_append(mi_curve,'segmentCurves','rigNull')
				self.md_attachReturns[mi_curve] = d_segReturn
				d_segReturn['ml_driverJoints'][0].parent = mi_go._i_faceDeformNull				    
			    except Exception,error:
				self.log_error(d_segReturn)
				raise StandardError,"[Return processing | error: {0}]".format(error)			    
				
		    except Exception,error:raise StandardError,"[{0} | error: {1}]".format(str_tag,error)			    
	    except Exception,error:raise StandardError,"[create_segmentfromDict] | error: {0}".format(error)	
	    
	def connect_fromDict(self,d_build):
	    '''
	    handler for connecting stuff to handles,curves,surfaces or whatever
	    Modes:
	    rigToHandle -- given a nameRig kw, it looks through the data sets to find the handle and connect. One to one connection type
	    rigToFollow --
	    pointBlend -- 
	    
	    Flags
	    'index'(int) -- root dict flag to specify only using a certain index of a list
	    'skip'(string) -- skip one of the side flags - 'left','right','center'
	    '''
	    try:#>> Connect  =======================================================================================
		mi_go = self._go#Rig Go instance link
		str_skullPlate = self.str_skullPlate
		f_offsetOfUpLoc = self.f_offsetOfUpLoc
		
		for str_tag in d_build.iterkeys():
		    try:
			md_buffer = {}
			ml_buffer = []
			buffer = self.md_rigList[str_tag]
			if type(buffer) == dict:
			    for str_side in ['left','right','center']:
				    bfr_side = buffer.get(str_side)
				    if bfr_side:
					md_buffer[str_side] = bfr_side
			else:
			    md_buffer['reg'] = buffer
			    
			l_skip = d_build[str_tag].get('skip') or []
			for str_key in md_buffer.iterkeys():
			    if str_key in l_skip:
				self.log_info("%s Skipping connect: %s"%(str_tag,str_key))
			    else:
				if d_build[str_tag].get(str_key):#if we have special instructions for a direction key...
				    d_buffer = d_build[str_tag][str_key]
				else:
				    d_buffer = d_build[str_tag]	
				ml_buffer = md_buffer[str_key]
				try:
				    int_indexBuffer = d_build[str_tag].get('index') or False
				    if int_indexBuffer is not False:
					self.log_info("%s | %s > Utilizing index call"%(str_tag,str_key))					
					ml_buffer = [ml_buffer[int_indexBuffer]]
				except Exception,error:raise StandardError,"[Index call(%s)!| error: {0}]".format(error)
				
				int_len = len(ml_buffer)
				for i,mObj in enumerate(ml_buffer):
				    str_mObj = mObj.p_nameShort
				    try:#Gather data ----------------------------------------------------------------------
					str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'rigToHandle'
					b_rewireFollicleOffset = d_buffer.get('rewireFollicleOffset') or d_build[str_tag].get('rewireFollicleOffset') or False 
					ml_driver = d_buffer.get('driver') or d_build[str_tag].get('driver')  or False
				    except Exception,error:raise StandardError,"[Data gather!] | error: {0}".format(error)

				    try:#Status update ----------------------------------------------------------------------
					str_message = "Connecting : '%s' %s > '%s' | mode: '%s' | rewireFollicleOffset: %s"%(str_tag,str_key,str_mObj,str_mode,b_rewireFollicleOffset)
					self.log_info(str_message)
					self.progressBar_set(status = (str_message),progress = i, maxValue = int_len)	
				    except Exception,error:raise StandardError,"[Status update] | error: {0}".format(error)					    
				    
				    if str_mode == 'rigToSegment':
					try:
					    mi_target = mObj.skinJoint.segJoint
					    mc.pointConstraint(mi_target.mNode,mObj.masterGroup.mNode,maintainOffset = True)
					    #mObj.masterGroup.parent = mi_target
					except Exception,error:raise StandardError,"[Failed!] | error: {0}".format(error)
				    elif str_mode == 'simpleSlideHandle':
					try:
					    try:#See if we have a handle return
						if ml_driver: ml_handles = cgmValid.listArg(ml_driver)
						else:					
						    ml_handles = self.md_rigList[str_tag.replace('Rig','Handle')][str_key]
						if len(ml_handles) != len(ml_buffer):raise StandardError,"len of toConnect(%s) != len handles(%s)"%(len(ml_handles),len(ml_buffer))
						mi_handle = ml_handles[0]
					    except Exception,error:raise StandardError,"[Query!] | error: {0}".format(error)
	
					    try:#Connect the control loc to the center handle
						mi_controlLoc = self.md_attachReturns[mObj]['controlLoc']
						cgmMeta.cgmAttr(mi_controlLoc,'translate').doConnectIn("{0}.translate".format(mi_handle.mNode))						
						cgmMeta.cgmAttr(mi_controlLoc,'rotate').doConnectIn("{0}.rotate".format(mi_handle.mNode))
						
					    except Exception,error:raise StandardError,"[Control loc connect!]%error: {0}]".format(error)

					except Exception,error:raise StandardError,"[{0}! | {1}]".format(str_mode,error)				    
				    elif str_mode == 'rigToHandle':
					try:
					    try:#See if we have a handle return
						if ml_driver: ml_handles = cgmValid.listArg(ml_driver)
						else:					
						    ml_handles = self.md_rigList[str_tag.replace('Rig','Handle')][str_key]
						if len(ml_handles) != len(ml_buffer):raise StandardError,"len of toConnect(%s) != len handles(%s)"%(len(ml_handles),len(ml_buffer))
						mi_handle = ml_handles[0]
					    except Exception,error:raise StandardError,"[Query!] | error: {0}".format(error)
	
					    try:#Connect the control loc to the center handle
						mi_controlLoc = self.md_attachReturns[mObj]['controlLoc']
						mc.pointConstraint(mi_handle.mNode,mi_controlLoc.mNode,maintainOffset = 1)
					    except Exception,error:raise StandardError,"[Control loc connect!]%error: {0}]".format(error)
					    
					    try:#Setup the offset to push handle rotation to the rig joint control
						#Create offsetgroup for the mid
						mi_offsetGroup = cgmMeta.cgmObject( mObj.doGroup(True),setClass=True)	 
						mi_offsetGroup.doStore('cgmName',mObj.mNode)
						mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
						mi_offsetGroup.doName()
						mObj.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
						
						cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
					    except Exception,error:raise StandardError,"[Offset group!] | error: {0}".format(error)
					    
					    try:#rewireFollicleOffset
						if b_rewireFollicleOffset:
						    mi_rewireHandle = d_buffer.get('rewireHandle') or d_build[str_tag].get('rewireHandle') or mi_handle
						    mi_follicleOffsetGroup = self.md_attachReturns[mObj]['offsetGroup']
						    for attr in mi_go._jointOrientation[0]:
							attributes.doConnectAttr ((mi_rewireHandle.mNode+'.t%s'%attr),(mi_follicleOffsetGroup.mNode+'.t%s'%attr))						     
					    except Exception,error:raise StandardError,"[rewire Follicle Offset! | error: {0}]".format(error)
					except Exception,error:raise StandardError,"[{0}! | {1}]".format(str_mode,error)					     				
				    elif str_mode == 'rigToFollow':
					try:
					    try:#See if we have a handle return
						mi_attachTo = d_buffer['attachTo']
						d_current = self.md_attachReturns[mObj]
						mi_followLoc = d_current['followLoc']
						mi_controlLoc = d_current['controlLoc']					    
					    except Exception,error:raise StandardError,"[Query '%s'!]{%s}"%(str_key,error)
					    
					    try:#>> Attach  loc  --------------------------------------------------------------------------------------
						if mi_attachTo.getMayaType() == 'nurbsCurve':
						    crvUtils.attachObjToCurve(mi_followLoc.mNode,mi_attachTo.mNode)
						else:
						    d_return = surfUtils.attachObjToSurface(objToAttach = mi_followLoc,
						                                            targetSurface = mi_attachTo.mNode,
						                                            createControlLoc = False,
						                                            createUpLoc = True,	
						                                            parentToFollowGroup = False,
						                                            orientation = mi_go._jointOrientation)
						    self.md_attachReturns[mi_followLoc] = d_return
						mc.pointConstraint(mi_followLoc.mNode,mi_controlLoc.mNode,maintainOffset = True)
						
					    except Exception,error:raise StandardError,"[Failed to attach to crv.] | error: {0}".format(error)					    
					    
					    
					    '''
					    try:#>> Attach  loc to curve --------------------------------------------------------------------------------------
						mi_crvLoc = d_current['crvLoc']
						mi_controlLoc = d_current['controlLoc']
						crvUtils.attachObjToCurve(mi_crvLoc.mNode,mi_crv.mNode)
						mc.pointConstraint(mi_crvLoc.mNode,mi_controlLoc.mNode,maintainOffset = True)
						
					    except Exception,error:raise StandardError,"Failed to attach to crv. | ] | error: {0}".format(error)
					    try:#>> Aim the offset group  ------------------------------------------------------------------------------------------
						if obj_idx != int_lastIndex:
						    str_upLoc = d_current['upLoc'].mNode
						    str_offsetGroup = d_current['offsetGroup'].mNode				    
						    if obj_idx == 0:
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
						    else:
							ml_targets = [ml_rigJoints[obj_idx+1]]	
							mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup,
									 maintainOffset = True, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
					    except Exception,error:raise StandardError,"Loc setup. | ] | error: {0}".format(error)
					    '''
					except Exception,error:raise StandardError,"[%s!]{%s}"%(str_mode,error)					    
					    
				    elif str_mode == 'pointBlend':
					try:
					    try:#See if we have a handle return
						ml_targets = d_buffer['targets']
						d_current = self.md_attachReturns[mObj]
						#mi_followLoc = d_current['followLoc']
						mi_controlLoc = d_current['controlLoc']					    
					    except Exception,error:raise StandardError,"[Query '%s'!]{%s}"%(str_key,error)
					    
					    try:#>> Attach  loc  --------------------------------------------------------------------------------------
						mc.pointConstraint([mObj.mNode for mObj in ml_targets],mi_controlLoc.mNode,maintainOffset = True)
					    except Exception,error:raise StandardError,"Failed to attach to crv. | ] | error: {0}".format(error)	
					except Exception,error:raise StandardError,"[%s!]{%s}"%(str_mode,error)					    
				    elif str_mode == 'parentConstraint':
					try:
					    try:#See if we have a handle return
						ml_targets = d_buffer['targets']
						d_current = self.md_attachReturns[mObj]
						#mi_followLoc = d_current['followLoc']
						mi_controlLoc = d_current['controlLoc']					    
					    except Exception,error:raise StandardError,"[Query '%s'!]{%s}"%(str_key,error)
					    try:#>> Attach  loc  --------------------------------------------------------------------------------------
						mc.parentConstraint([mObj.mNode for mObj in ml_targets],mi_controlLoc.mNode,maintainOffset = True)
					    except Exception,error:raise StandardError,"Failed to attach to crv. | ] | error: {0}".format(error)	
					except Exception,error:raise StandardError,"[%s!]{%s}"%(str_mode,error)	
				    elif str_mode == 'pointConstraint':
					try:
					    try:#See if we have a handle return
						ml_targets = d_buffer['targets']
						d_current = self.md_attachReturns[mObj]
						mi_controlLoc = d_current['controlLoc']					    
					    except Exception,error:raise StandardError,"[Query '%s'!]{%s}"%(str_key,error)
					    try:#>> Attach  loc  --------------------------------------------------------------------------------------
						mc.pointConstraint([mObj.mNode for mObj in ml_targets],mi_controlLoc.mNode,maintainOffset = True)
					    except Exception,error:raise StandardError,"Failed to attach to crv. | ] | error: {0}".format(error)	
					except Exception,error:raise StandardError,"[%s!]{%s}"%(str_mode,error)
					
				    elif str_mode == 'offsetConnect':
					try:
					    try:#See if we have a handle return
						if ml_driver: ml_handles = cgmValid.listArg(ml_driver)
						else:					
						    ml_handles = self.md_rigList[str_tag.replace('Rig','Handle')][str_key]
						if len(ml_handles) != len(ml_buffer):raise StandardError,"len of toConnect(%s) != len handles(%s)"%(len(ml_handles),len(ml_buffer))
						mi_handle = ml_handles[0]
					    except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)
	

					    try:#Setup the offset to push handle rotation to the rig joint control
						#Create offsetgroup for the mid
						mi_offsetGroup = cgmMeta.cgmObject( mObj.doGroup(True),setClass=True)	 
						mi_offsetGroup.doStore('cgmName',mObj.mNode)
						mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
						mi_offsetGroup.doName()
						mObj.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
						cgmMeta.cgmAttr(mi_offsetGroup,'translate').doConnectIn("%s.translate"%(mi_handle.mNode))						
					    except Exception,error:raise StandardError,"[Offset group!] | error: {0}".format(error)
					    
					    try:#rewireFollicleOffset
						if b_rewireFollicleOffset:
						    mi_rewireHandle = d_buffer.get('rewireHandle') or d_build[str_tag].get('rewireHandle') or mi_handle
						    mi_follicleOffsetGroup = self.md_attachReturns[mObj]['offsetGroup']
						    for attr in mi_go._jointOrientation[0]:
							attributes.doConnectAttr ((mi_rewireHandle.mNode+'.t%s'%attr),(mi_follicleOffsetGroup.mNode+'.t%s'%attr))						    
					    except Exception,error:raise StandardError,"[rewire Follicle Offset!%error: {0}]".format(error)
					    
					except Exception,error:raise StandardError,"[%s!]{%s}"%(str_mode,error)	
					
				    elif str_mode == 'attrOffsetConnect':
					try:
					    try:#See if we have a handle return
						if ml_driver: ml_handles = cgmValid.listArg(ml_driver)
						else:ml_handles = self.md_rigList[str_tag.replace('Rig','Handle')][str_key]
						if len(ml_handles) != len(ml_buffer):raise StandardError,"len of toConnect(%s) != len handles(%s)"%(len(ml_handles),len(ml_buffer))
						mi_handle = ml_handles[0]
						l_attrsToConnect = d_buffer.get('attrsToConnect') or d_build[str_tag].get('attrsToConnect') or ['tx','ty','tz']
						l_attrsToMirror = d_buffer.get('attrsToMirror') or d_build[str_tag].get('attrsToMirror') or []
						self.log_info("{0} | attrOffsetConnect | driver: {1} | attrsToConnect: {2} | attrsToMirror: {3}".format(str_mObj,ml_driver,l_attrsToConnect,l_attrsToMirror))

					    except Exception,error:raise StandardError,"[Query! | error: {0}]".format(error)
	
					    try:#Setup the offset to push handle rotation to the rig joint control
						#Create offsetgroup for the mid
						mi_offsetGroup = cgmMeta.cgmObject( mObj.doGroup(True),setClass=True)	 
						mi_offsetGroup.doStore('cgmName',mObj.mNode)
						mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
						mi_offsetGroup.doName()
						mObj.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')
						
						for a in l_attrsToConnect:
						    if a not in l_attrsToMirror:
							cgmMeta.cgmAttr(mi_offsetGroup,a).doConnectIn("{0}.{1}".format(mi_handle.mNode,a))
						    else:
							mPlug_attrBridgeDriven = cgmMeta.cgmAttr(mi_offsetGroup,a)
							mPlug_attrBridgeDriver = cgmMeta.cgmAttr(mi_handle,a)
							arg_attributeBridge = "%s = -%s"%(mPlug_attrBridgeDriven.p_combinedShortName,
							                                  mPlug_attrBridgeDriver.p_combinedShortName)							
							NodeF.argsToNodes(arg_attributeBridge).doBuild()					
					    except Exception,error:raise StandardError,"[Offset group!] | error: {0}".format(error)

					except Exception,error:raise StandardError,"[{0}! | {1}]".format(str_mode,error)					     				
				    else:
					raise NotImplementedError,"not implemented : mode: %s"%str_mode
		    except Exception,error:  raise StandardError,"[%s]{%s}"%(str_tag,error)			    
	    except Exception,error:  raise StandardError,"[connect_fromDict] | error: {0}".format(error)	
	    
	def get_mdSidesBufferFromTag(self,str_tag):
	    '''
	    Process a dict against to a md_rigList
	    '''
	    md_buffer = {}
	    buffer = self.md_rigList[str_tag]
	    if type(buffer) == dict:
		for str_side in ['left','right','center']:
			bfr_side = buffer.get(str_side)
			if bfr_side:
			    md_buffer[str_side] = bfr_side
	    else:
		md_buffer['reg'] = buffer
	    return md_buffer
	
	def create_influenceJoints(self,d_build):
	    '''
	    '''
	    try:#>> Infuence joints  =======================================================================================
		mi_go = self._go#Rig Go instance link
		str_skullPlate = self.str_skullPlate
		
		for str_tag in d_build.iterkeys():
		    try:
			ml_buffer = []
			md_buffer = self.get_mdSidesBufferFromTag(str_tag)
			    
			l_skip = d_build[str_tag].get('skip') or []
			
			str_newTag = '{0}InfluenceJoints'.format(str_tag)
			self.md_rigList[str_newTag] = {}#...start new dict	
		    
			for str_side in md_buffer.iterkeys():
			    if str_side in l_skip:
				self.log_info("%s Skipping aim: %s"%(str_tag,str_side))
			    else:
				try:
				    if d_build[str_tag].get(str_side):#if we have special instructions for a direction key...
					d_buffer = d_build[str_tag][str_side]
				    else:
					d_buffer = d_build[str_tag]	
				    ml_buffer = md_buffer[str_side]
				    
				    try:
					int_indexBuffer = d_build[str_tag].get('index') or False
					if int_indexBuffer is not False:
					    self.log_info("%s | %s > Utilizing index call"%(str_tag,str_side))					
					    ml_buffer = [ml_buffer[int_indexBuffer]]
				    except Exception,error:raise StandardError,"[Index call!| error: {0}]".format(error)
				    int_len = len(ml_buffer)
				    _d = {}
				    self.d_buffer = _d
				    int_len = len(ml_buffer)			    
				    ml_influenceJoints = []			    
				    for idx,mJnt in enumerate(ml_buffer):
					str_mObj = mJnt.p_nameShort
					
					try:#Status update ----------------------------------------------------------------------
					    str_message = "Creating influence joint : '{0}' {1} > '{2}'".format(str_tag,str_side,str_mObj)
					    self.log_info(str_message)
					    self.progressBar_set(status = (str_message),progress = idx, maxValue = int_len)	
					except Exception,error:raise StandardError,"[Status update] | error: {0}".format(error)	
					
					try:#Create----------------------------------------------------------------------
					    mi_influenceJoint = cgmMeta.cgmObject( mc.joint(),setClass = 1)
					    Snap.go(mi_influenceJoint,mJnt.mNode,orient=True)
					    mi_influenceJoint.rotateOrder = mJnt.rotateOrder
					    mi_influenceJoint.doCopyNameTagsFromObject(mJnt.mNode,ignore=['cgmType'])	
					    mi_influenceJoint.addAttr('cgmTypeModifier','influence',lock=True)
					    mi_influenceJoint.doName()
					    mJnt.connectChildNode(mi_influenceJoint,'influenceJoint','sourceJoint')
					    ml_influenceJoints.append(mi_influenceJoint)
					    mi_influenceJoint.parent = mi_go._i_deformNull	
					except Exception,error:raise StandardError,"[influence joint for '{0}'! | error: {1}]".format(str_mObj,error)				    
					
					try:#Create offsetgroup for the mid
					    mi_offsetGroup = cgmMeta.cgmObject( mi_influenceJoint.doGroup(True),setClass=True)	 
					    mi_offsetGroup.doStore('cgmName',mi_influenceJoint.mNode)
					    mi_offsetGroup.addAttr('cgmTypeModifier','master',lock=True)
					    mi_offsetGroup.doName()
					    mi_influenceJoint.connectChildNode(mi_offsetGroup,'masterGroup','groupChild')
					except Exception,error:raise StandardError,"[masterGroup for '{0}'! | error: {1}]".format(str_mObj,error)				    
					    
				    mi_go.connect_toRigGutsVis(ml_influenceJoints, vis = True)#connect to guts vis switches
				    self.md_rigList[str_newTag][str_side] = ml_influenceJoints#...store
				except Exception,error:raise Exception,"[side: {0} | error: {1}]".format(str_side,error)			     
		    except Exception,error:
			try:self.log_infoNestedDict('d_buffer')
			except:pass
			raise Exception,"[tag: {0} | error: {1}]".format(str_tag,error)			    
	    except Exception,error: raise Exception,"[create_influenceJoint] | error: {0}".format(error)
	    
	def aim_fromDict(self,d_build):
	    '''
	    handler for aiming stuff to handles,curves,surfaces or whatever
	    
	    Modes:
	    lipLineBlend -- special lip line mode
	    singleTarget -- aims at a single target
	    
	    Flags
	    'index'(int) -- root dict flag to specify only using a certain index of a list
	    'skip'(string) -- skip one of the side flags - 'left','right','center'
	    '''
	    try:#>> Aim  =======================================================================================
		mi_go = self._go#Rig Go instance link
		str_skullPlate = self.str_skullPlate
		
		for str_tag in d_build.iterkeys():
		    try:
			md_buffer = {}
			ml_buffer = []
			buffer = self.md_rigList[str_tag]
			if type(buffer) == dict:
			    for str_side in ['left','right','center']:
				    bfr_side = buffer.get(str_side)
				    if bfr_side:
					md_buffer[str_side] = bfr_side
			else:
			    md_buffer['reg'] = buffer
			    
			l_skip = d_build[str_tag].get('skip') or []
			for str_side in md_buffer.iterkeys():
			    if str_side in l_skip:
				self.log_info("%s Skipping aim: %s"%(str_tag,str_side))
			    else:
				try:
				    if d_build[str_tag].get(str_side):#if we have special instructions for a direction key...
					d_buffer = d_build[str_tag][str_side]
				    else:
					d_buffer = d_build[str_tag]	
				    ml_buffer = md_buffer[str_side]
				    
				    try:
					int_indexBuffer = d_build[str_tag].get('index') or False
					if int_indexBuffer is not False:
					    self.log_info("%s | %s > Utilizing index call"%(str_tag,str_side))					
					    ml_buffer = [ml_buffer[int_indexBuffer]]
				    except Exception,error:raise StandardError,"[Index call!| error: {0}]".format(error)
				    int_len = len(ml_buffer)
				    _d = {}
				    self.d_buffer = _d
				    int_last = len(ml_buffer)-1	
				    try:#Vectors
					if str_side == 'right':
					    v_aimIn = mi_go._vectorOut
					    v_aimOut = mi_go._vectorOutNegative	
					    ml_buffer = copy.copy(ml_buffer)
					    ml_buffer.reverse()
					    v_up = mi_go._vectorUp
					else:
					    v_aimIn = mi_go._vectorOutNegative
					    v_aimOut = mi_go._vectorOut	
					    v_up = mi_go._vectorUp
					    
					_d['v_aimIn'] = v_aimIn
					_d['v_aimOut'] = v_aimOut
					_d['v_up'] = v_up										
				    except Exception,error:raise StandardError,"[Vector query!| error: {0}]".format(error)
					
				except Exception,error:raise Exception,"[Side data query! | error: {0}]".format(error)
				
	
				for idx,mObj in enumerate(ml_buffer):
				    str_mObj = mObj.p_nameShort
				    
				    try:#Status update ----------------------------------------------------------------------
					str_message = "Aiming : '%s' %s > '%s'"%(str_tag,str_side,str_mObj)
					self.log_info(str_message)
					self.progressBar_set(status = (str_message),progress = idx, maxValue = int_len)	
				    except Exception,error:raise StandardError,"[Status update] | error: {0}".format(error)	
				    
				    try:#Gather data ----------------------------------------------------------------------
					try:d_current = self.md_attachReturns[mObj]
					except:
					    d_current = {}
					    self.log_warning("'%s' | no attachReturn"%str_mObj)	
					    
					str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'lipLineBlend'
					mi_upLoc = d_buffer.get('upLoc') or d_build[str_tag].get('upLoc') or d_current.get('upLoc') or False
					mi_masterGroup = mObj.masterGroup
					_d['str_mode'] = str_mode
					_d['upLoc'] = mi_upLoc	
				    except Exception,error:raise Exception,"[Gather Data] | error: {0}".format(error)
				    
				    try:#Aim Offset group ----------------------------------------------------------------------
					'''
					We need to first find our target which be a child to our aimOffset group. Sometimes that's the basic offset group
					'''
					mi_offsetTarget = d_buffer.get('offsetGroup') or d_build[str_tag].get('offsetGroup') or False
					if not mi_offsetTarget:
					    try: mi_offsetTarget = d_current['offsetGroup']#See if we have an offset group
					    except:
						self.log_warning("'%s' |No offset group in build dict. Checking object"%str_mObj)
						try:
						    mi_offsetTarget = mObj.offsetGroup
						except:
						    self.log_warning("'%s' | No offset group found. Using object"%str_mObj)					
						    mi_offsetTarget = mObj
			    
					mi_aimOffsetGroup = cgmMeta.cgmObject(mi_offsetTarget.doGroup(True),setClass=True)
					mi_aimOffsetGroup.doStore('cgmName',mObj.mNode)
					mi_aimOffsetGroup.addAttr('cgmTypeModifier','AimOffset',lock=True)
					mi_aimOffsetGroup.doName()
					mObj.connectChildNode(mi_aimOffsetGroup,"aimOffsetGroup","childObject")					    
				    except Exception,error:raise Exception,"[AimOffset group] | error: {0}".format(error)
					    
				    if str_mode == 'lipLineSegmentBlend':#This is pretty much just for the lip rig line for now
					try:#Getting up loc --------------------------------------------------------------------
					    self.log_info("'%s' | getting up loc..."%str_mObj)
					    if str_side == 'center':
						mi_segmentCurve =  mObj.skinJoint.segJoint.segmentCurve
						mi_upLoc = d_buffer['midUpLoc']
						mi_midHandle = d_buffer['midHandle']
					    else:
						mi_upLoc = mObj.skinJoint.segJoint.upLoc
					except Exception,error:raise StandardError,"['%s' upLoc!]{%s}"%(str_mObj,error)
					
					try:
					    str_baseKey = d_buffer.get('baseKey') or d_build[str_tag].get('baseKey') or str_tag
					    if not str_baseKey:raise Exception,"No baseKey found!"
					    self.log_info("'{0}' | baseKey: {1}".format(str_mObj,str_baseKey))					    
    
					    _d['baseKey'] = str_baseKey		
					    try:#Vectors
						self.log_info("'%s' | getting vectors..."%str_mObj)					    						
						v_up = _d.get('v_up') or mi_go.vectorUp
						
						if str_side == 'right':
						    v_aimIn = mi_go._vectorOut
						    v_aimOut = mi_go._vectorOutNegative	
						    ml_buffer = copy.copy(ml_buffer)
						    ml_buffer.reverse()
						else:
						    v_aimIn = mi_go._vectorOutNegative
						    v_aimOut = mi_go._vectorOut	
						    
						_d['v_aimIn'] = v_aimIn
						_d['v_aimOut'] = v_aimOut
						_d['v_up'] = v_up										
					    except Exception,error:raise StandardError,"[Vector query!] | error: {0}".format(error)					    
					    
					except Exception,error:raise StandardError,"[%s query]{%s}"%(str_mode,error)					
					    
					try:
					    self.log_info("'%s' | getting targets..."%str_mObj)					    											    
					    if str_side != 'center':					
						#Get objects
						if idx == 0:
						    mi_aimOut = self.md_rigList['lipCornerRig'][str_side][0]
						    mi_aimIn = ml_buffer[idx+1].masterGroup
						elif idx == int_last:
						    mi_aimOut = ml_buffer[idx-1].masterGroup
						    mi_aimIn = md_buffer['center'][0].masterGroup			    
						else:
						    mi_aimOut = ml_buffer[idx-1].masterGroup
						    mi_aimIn = ml_buffer[idx+1].masterGroup
					    else:
						mi_aimOut = self.md_rigList[str_baseKey]['left'][-1].masterGroup
						mi_aimIn = self.md_rigList[str_baseKey]['right'][-1].masterGroup	
					    _d['aimIn'] = mi_aimIn.mNode
					    _d['aimOut'] = mi_aimOut.mNode
					except Exception,error:raise StandardError,"[Get aim targets] | error: {0}".format(error)
					
					#self.log_info("Side: '%s' | idx: %s | Aiming :'%s' | in:'%s' | out:'%s' | up:'%s' "%(str_side,idx,str_mObj,mi_aimIn.p_nameShort,mi_aimOut.p_nameShort,mi_upLoc.p_nameShort))
					
					#loc creation ------------------------------------------------------------------------
					try:
					    self.log_info("'%s' | making locs..."%str_mObj)					    											    
					    mi_locIn = mObj.doLoc()
					    mi_locIn.addAttr('cgmTypeModifier','aimIn',lock=True)
					    mi_locIn.doName()					    
					    
					    mi_locOut = mObj.doLoc()
					    mi_locOut.addAttr('cgmTypeModifier','aimOut',lock=True)
					    mi_locOut.doName()	
					    
					    mi_go.connect_toRigGutsVis([mi_locIn,mi_locOut],vis = 1, doShapes = True)#connect to guts vis switches
					    
					    mi_locIn.parent = mi_masterGroup
					    mi_locOut.parent = mi_masterGroup
					except Exception,error:raise Exception,"[Aim loc creation!] | error: {0}".format(error)
					try:
					    if str_side == 'center':
						#If it's our center we're going to aim at the up object with the aimout/in as up vectors
						
						mc.aimConstraint(mi_upLoc.mNode, mi_locIn.mNode,
						                 weight = 1, aimVector = v_up, upVector = v_aimIn,
						                 maintainOffset = 0,
						                 worldUpObject = mi_aimIn.mNode, worldUpType = 'object' ) 
						mc.aimConstraint(mi_upLoc.mNode, mi_locOut.mNode,
					                         weight = 1, aimVector = v_up, upVector = v_aimOut,
					                         maintainOffset = 0,					                     
					                         worldUpObject = mi_aimOut.mNode, worldUpType = 'object' )
						mi_contraint = cgmMeta.cgmNode(mc.orientConstraint([mi_locIn.mNode,mi_locOut.mNode], mi_aimOffsetGroup.mNode,
						                                                   maintainOffset = True,					                        
						                                                   weight = 1)[0]) 
						mi_contraint.interpType = 0						
						#mi_contraint = cgmMeta.cgmNode(mc.orientConstraint([mi_midHandle.mNode], mObj.masterGroup.mNode,
						                                                  #maintainOffset = 1,					                        
						                                                  # weight = 1)[0]) 
						
						#cgmMeta.cgmAttr(mi_midHandle,'result_averageRoll').doConnectOut("%s.r%s"%(mi_aimOffsetGroup.mNode,mi_go._jointOrientation[2]))
					    else:
						mc.aimConstraint(mi_aimIn.mNode, mi_locIn.mNode,
						                 weight = 1, aimVector = v_aimIn, upVector = v_up,
						                 maintainOffset = 1,
						                 worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) 
						mc.aimConstraint(mi_aimOut.mNode, mi_locOut.mNode,
						                 weight = 1, aimVector = v_aimOut, upVector = v_up,
						                 maintainOffset = 1,					                     
						                 worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) 
						mi_contraint = cgmMeta.cgmNode(mc.orientConstraint([mi_locIn.mNode,mi_locOut.mNode], mi_aimOffsetGroup.mNode,
						                                                   maintainOffset = True,					                        
						                                                   weight = 1)[0]) 
					    mi_contraint.interpType = 0
					except Exception,error:raise Exception,"[Constraints setup!] | error: {0}".format(error)
					
				    elif str_mode == 'singleBlend':#...single aim blend
					try:#Gather data ----------------------------------------------------------------------
					    d_target0 = d_buffer.get('d_target0') or d_build[str_tag].get('d_target0')
					    d_target1 = d_buffer.get('d_target1') or d_build[str_tag].get('d_target1')
					    if not d_target0:raise StandardError,"Failed to get d_target0"
					    if not d_target1:raise StandardError,"Failed to get d_target1"
					    if not mi_upLoc:raise Exception,"No upLoc found!"										    
					except Exception,error:raise Exception,"[Gather Data] | error: {0}".format(error)											
					try:
					    mi_locIn = mObj.doLoc()
					    mi_locIn.addAttr('cgmTypeModifier','aim0',lock=True)
					    mi_locIn.doName()					    
					    
					    mi_locOut = mObj.doLoc()
					    mi_locOut.addAttr('cgmTypeModifier','aim1',lock=True)
					    mi_locOut.doName()	
					    
					    mi_go.connect_toRigGutsVis([mi_locIn,mi_locOut],vis = 1, doShapes = True)#connect to guts vis switches
					    
					    mi_locIn.parent = mi_masterGroup
					    mi_locOut.parent = mi_masterGroup
					except Exception,error:raise StandardError,"[Aim loc creation!] | error: {0}".format(error)
					try:
					    mc.aimConstraint(d_target0['target'].mNode, mi_locIn.mNode,
						             weight = 1, aimVector = d_target0['v_aim'], upVector = d_target0['v_up'],
					                     maintainOffset = 1,
						             worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) 
					    mc.aimConstraint(d_target1['target'].mNode, mi_locOut.mNode,
					                     weight = 1, aimVector = d_target1['v_aim'], upVector = d_target1['v_up'],
					                     maintainOffset = 1,					                     
						             worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) 
					    mi_contraint = cgmMeta.cgmNode(mc.orientConstraint([mi_locIn.mNode,mi_locOut.mNode], mi_aimOffsetGroup.mNode,
					                                                       maintainOffset = True,					                        
					                                                       weight = 1)[0]) 
					    mi_contraint.interpType = 0
					except Exception,error:raise StandardError,"[Constraints setup!] | error: {0}".format(error)
				    elif str_mode == 'singleTarget':
					try:				
					    '''
					d_build = {'noseUnderRig':{'mode':'singleTarget','aimVector':mi_go._vectorUpNegative,'upVector':mi_go._vectorAim,
		                           'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseUnderTarget}}
					    '''
					    mi_aimTo = d_buffer['aimTarget']
					    v_up = d_buffer['v_up']
					    v_aim = d_buffer['v_aim']
					    _d['mi_aimTo'] = mi_aimTo
					    _d['v_up'] = v_up
					    _d['v_aim'] = v_aim
					except Exception,error:raise StandardError,"[%s query]{%s}"%(str_mode,error)
					self.log_info("Side: '%s' | idx: %s | Aiming :'%s' | to:'%s' | up:'%s' "%(str_side,idx,str_mObj,mi_aimTo.p_nameShort,mi_upLoc.p_nameShort))					
					try:
					    mc.aimConstraint(mi_aimTo.mNode, mi_aimOffsetGroup.mNode,
						             weight = 1, aimVector = v_aimIn, upVector = v_up,
					                     maintainOffset = True,
						             worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
					except Exception,error:raise StandardError,"[Constraints setup!] | error: {0}".format(error)	
				    elif str_mode == 'singleVectorAim':
					try:				
					    ml_aimTo = d_buffer['aimTargets']
					    if type(ml_aimTo) not in [list,tuple]:ml_aimTo = [ml_aimTo]
					    v_up = d_buffer['v_up']
					    v_aim = d_buffer['v_aim']
					    _d['ml_aimTo'] = ml_aimTo
					    _d['v_up'] = v_up
					    _d['v_aim'] = v_aim
					except Exception,error:raise StandardError,"[%s query]{%s}"%(str_mode,error)
					self.log_info("Side: '%s' | idx: %s | Aiming :'%s' | to:'%s' | up:'%s' "%(str_side,idx,str_mObj,[mTarget.mNode for mTarget in ml_aimTo],mi_upLoc.p_nameShort))					
					try:
					    mc.aimConstraint([mTarget.mNode for mTarget in ml_aimTo], mi_aimOffsetGroup.mNode,
					                     weight = 1, aimVector = v_aimIn, upVector = v_up,
					                     maintainOffset = True,
					                     worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
					except Exception,error:raise StandardError,"[singleVectorAim setup!] | error: {0}".format(error)						
					
					
				    else:
					raise NotImplementedError,"Mode not implemented : '%s'"%str_mode
		    except Exception,error:
			try:self.log_infoNestedDict('d_buffer')
			except:pass
			raise Exception,"[tag: '%s']{%s}"%(str_tag,error)			    
	    except Exception,error: raise Exception,"[aim_fromDict] | error: {0}".format(error)
	def skin_fromDict(self,d_build):
	    try:#>> skin  =======================================================================================
		mi_go = self._go#Rig Go instance link
		self.progressBar_setMaxStepValue(len(d_build.keys()))
		
		for str_tag in d_build.iterkeys():
		    try:
			self.progressBar_iter(status = ("Skinning : '%s'"%str_tag))									
			try:#Build list
			    __target = d_build[str_tag]['target']
			    __bindJoints = d_build[str_tag]['bindJoints']
			    __mi = d_build[str_tag].get('mi') or 5
			    __dr = d_build[str_tag].get('dr') or 7
			except Exception,error:raise StandardError,"[get data |error: {0}]".format(error)
			
			try:#Cluster
			    ret_cluster = mc.skinCluster([mObj.mNode for mObj in [__target] + __bindJoints], tsb = True, normalizeWeights = True, mi = __mi, dr = __dr)
			    i_cluster = cgmMeta.cgmNode(ret_cluster[0],setClass=True)
			    i_cluster.doStore('cgmName',__target.mNode)
			    i_cluster.doName()		
			except Exception,error:raise StandardError,"[Cluster |error: {0}]".format(error)
			
		    except Exception,error:  raise StandardError,"%s | %s"%(str_tag,error)			    
	    except Exception,error:  raise StandardError,"[skin_fromDict |error: {0}]".format(error)	
		    
	def create_plateFromDict(self,md_plateBuilds):
	    try:#Main plates -----------------------------------------------------------------------------	
		mi_go = self._go#Rig Go instance link		
		self.progressBar_setMaxStepValue(len(md_plateBuilds.keys()))
		
		for str_name in md_plateBuilds.iterkeys():
		    try:
			self.progressBar_iter(status = ("Plate build: '%s'"%str_name))						
			d_buffer = md_plateBuilds[str_name]#get the dict
			self.d_buffer = d_buffer
			str_mode = d_buffer.get('mode')
			if str_mode == 'cheekLoft':
			    try:#Cheek loft
				l_deleteBuffer = []
				str_direction = d_buffer['direction']
				#str_name = d_buffer['name']
				mi_smileCrv = d_buffer['smileCrv']
				d_buffer['uprCheekJoints'] = self.md_rigList['uprCheekRig'][str_direction]
				d_buffer['cheekJoints'] = self.md_rigList['cheekRig'][str_direction]				
				d_buffer['jawLineJoints'] = self.md_rigList['jawLine'][str_direction]
				d_buffer['sneerHandle'] = self.md_rigList['sneerHandle'][str_direction][0]
				d_buffer['smileBaseHandle'] = self.md_rigList['smileBaseHandle'][str_direction][0]				
				    
				try:#Build our rail curves
				    l_railCrvs = []
				    ml_uprCheekRev = copy.copy(d_buffer['uprCheekJoints'])
				    ml_uprCheekRev.reverse()
				    ml_jawLineRev = copy.copy(d_buffer['jawLineJoints'])
				    ml_jawLineRev.reverse()
				    
				    ml_startRailObjs = [d_buffer['sneerHandle']] + ml_uprCheekRev
				    ml_endRailObjs = [d_buffer['smileBaseHandle']] + ml_jawLineRev
				    #self.log_info("startRailObjs: %s"%[mObj.p_nameShort for mObj in ml_startRailObjs])
				    #self.log_info("endRailObjs: %s"%[mObj.p_nameShort for mObj in ml_endRailObjs])
				    #self.log_info("cheekJoints: %s"%[mObj.p_nameShort for mObj in d_buffer['cheekJoints']])
				    
				    str_startRailCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_startRailObjs], os = True)
				    str_endRailCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endRailObjs], os = True)
				    
				    #str_startRailCrv = mc.rebuildCurve (str_startRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    #str_endRailCrv = mc.rebuildCurve (str_endRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    str_startRailCrv = self.returnRebuiltCurveString(str_startRailCrv,5,1)
				    str_endRailCrv = self.returnRebuiltCurveString(str_endRailCrv,5,1)
				    
				except Exception,error:raise StandardError,"[Rail curve build |error: {0}]".format(error)
				
				try:				    
				    ml_endProfileObjs = [ml_startRailObjs[-1],d_buffer['cheekJoints'][0], ml_endRailObjs[-1]]
				    #self.log_info("endProfileObjs: %s"%[mObj.p_nameShort for mObj in ml_endProfileObjs])
				    str_endProfileCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endProfileObjs], os = True)
				    str_startProfileCrv = mc.rebuildCurve (mi_smileCrv.mNode, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    str_endProfileCrvRebuilt = mc.rebuildCurve (str_endProfileCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]
				    
				except Exception,error:raise StandardError,"[Profile curves build |error: {0}]".format(error)	
				
				try:
				    str_loft = mc.doubleProfileBirailSurface( str_startProfileCrv, str_endProfileCrvRebuilt,
				                                              str_startRailCrv, str_endRailCrv, 
				                                              blendFactor = .5,constructionHistory=0, object=1, polygon=0, transformMode=0)[0]
				except Exception,error:raise StandardError,"[birail create |error: {0}]".format(error)	
				
				mc.delete([str_startProfileCrv,str_startRailCrv,str_endRailCrv,str_endProfileCrv])#Delete the rebuilt curves
			    except Exception,error:raise StandardError,"[Reg plate loft |error: {0}]".format(error)	
			elif str_mode == 'liveSurface':
			    try:
				str_loft = mc.loft([mCrv.mNode for mCrv in d_buffer['crvs']],ch = True, uniform = True,degree = 3,ss = 3)[0]			    
			    except Exception,error:raise StandardError,"[Live Surface loft | error: {0}]".format(error)	
			else:
			    try:#Reg curve loft
				l_crvsRebuilt = []
				for mi_crv in d_buffer['crvs']:#rebuild crvs
				    l_crvsRebuilt.append(self.returnRebuiltCurveString(mi_crv,4))
				
				str_loft = mc.loft(l_crvsRebuilt,uniform = True,degree = 3,ss = 3)[0]
				mc.delete(l_crvsRebuilt)#Delete the rebuilt curves
			    except Exception,error:raise StandardError,"[Reg plate loft |error: {0}]".format(error)	
			
			try:#tag, name, store
			    mi_obj = cgmMeta.cgmObject(str_loft)
			    mi_obj.parent = mi_go._i_rigNull#parent to rigNull
			    self.__dict__['mi_%sPlate'%(str_name)] = mi_obj
			    mi_obj.addAttr('cgmName',d_buffer.get('name') or str_name,lock=True)
			    try:mi_obj.addAttr('cgmDirection',str_direction ,lock=True)
			    except:pass
			    mi_obj.addAttr('cgmTypeModifier','plate',lock=True)					    
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sPlate"%str_name,'module')
			except Exception,error:raise StandardError,"[Tag/Name/Store |error: {0}]".format(error)	
			
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)	
		    #self.log_infoNestedDict('d_buffer')		    
	    except Exception,error:raise StandardError,"[create_plateFromDict | error: {0}]".format(error)
	    
	def create_ribbonsFromDict(self,md_ribbonBuilds):
	    try:#Ribbons -----------------------------------------------------------------------------	
		mi_go = self._go#Rig Go instance link		
		self.progressBar_setMaxStepValue(len(md_ribbonBuilds.keys()))		
		for str_name in md_ribbonBuilds.iterkeys():
		    try:
			self.progressBar_iter(status = ("Ribbon build: '%s'"%str_name))			
			d_buffer = md_ribbonBuilds[str_name]#get the dict
			self.d_buffer = d_buffer
			f_dist = mi_go._f_skinOffset*.5
			
			if d_buffer.get('mode') == 'radialLoft':
			    try:mi_obj = surfUtils.create_radialCurveLoft(d_buffer['extrudeCrv'].mNode,d_buffer['aimObj'].mNode,f_dist)
			    except Exception,error:raise StandardError,"[Radial Loft |error: {0}]".format(error)
			else:
			    try:#Regular loft -----------------------------------------------------------------------
				ml_joints = d_buffer['joints']
				mi_crv = d_buffer['extrudeCrv']

				try:#Make our loft loc -----------------------------------------------------------------------
				    #f_dist = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_joints])*.05
				    d_buffer['dist'] = f_dist
				    
				    mi_loc = ml_joints[-1].doLoc()
				    mi_loc.doGroup()
				except Exception,error:raise StandardError,"[loft loc | error: {0}]".format(error)
				
				try:#Cross section creation -----------------------------------------------------------------------
				    l_profileCrvPos = []
				    for dist in [0,f_dist]:
					mi_loc.__setattr__("t%s"%mi_go._jointOrientation[1],dist)
					l_profileCrvPos.append(mi_loc.getPosition())
					
				    str_profileCrv = mc.curve(d = 1,ep = l_profileCrvPos, os = True)
				except Exception,error:raise StandardError,"[Cross section creation |error: {0}]".format(error)
				
				try:#Extrude crv -----------------------------------------------------------------------
				    str_extruded = mc.extrude([str_profileCrv,mi_crv.mNode],et = 1, sc = 1,ch = 1,useComponentPivot = 0,fixedPath=1)[0]
				    mi_obj = cgmMeta.cgmObject(str_extruded)
				    mc.delete(mi_loc.parent,str_profileCrv)
				except Exception,error:raise StandardError,"[Extrude crv | error: {0}]".format(error)	
			    except Exception,error:raise StandardError,"[Regular loft |error: {0}]".format(error)
			try:
			    self.__dict__['mi_%sRibbon'%(str_name)] = mi_obj
			    mi_obj.parent = mi_go._i_rigNull#parent to rigNull			    
			    mi_obj.addAttr('cgmName',str_name,lock=True)
			    mi_obj.addAttr('cgmTypeModifier','ribbon',lock=True)			    
			    try:mi_obj.addAttr('cgmDirection',d_buffer['direction'] ,lock=True)
			    except:pass
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sRibbon"%str_name,'module')			    
			except Exception,error:raise StandardError,"[Naming | error: {0}]".format(error)
			#self.log_infoNestedDict('d_buffer')
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)
	    except Exception,error:raise StandardError,"[create_ribbonsFromDict |error: {0}]".format(error)
	    
	def create_curvesFromDict(self,d_build):
	    try:#Ribbons -----------------------------------------------------------------------------	
		mi_go = self._go#Rig Go instance link		
		self.progressBar_setMaxStepValue(len(d_build.keys()))		
		for str_name in d_build.iterkeys():
		    try:
			self.progressBar_iter(status = ("Curve build: '%s'"%str_name))			
			d_buffer = d_build[str_name]#get the dict
			self.d_buffer = d_buffer
			f_dist = mi_go._f_skinOffset*.5
			
			if d_buffer.get('mode') == 'asdfasdfasdf':
			    pass
			else:
			    try:#Curve -----------------------------------------------------------------------
				ml_objs = d_buffer['pointTargets']
				str_curve = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_objs], os = True)
				mi_obj = cgmMeta.cgmObject(str_curve,setClass=True)
			    except Exception,error:raise StandardError,"[Regular curve | error: {0}]".format(error)
			try:
			    self.__dict__['mi_%sCrv'%(str_name)] = mi_obj
			    mi_obj.addAttr('cgmName',str_name,lock=True)
			    try:mi_obj.addAttr('cgmDirection',d_buffer['direction'] ,lock=True)
			    except:pass
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sCrv"%str_name,'module')	
			    mi_obj.parent = mi_go._i_rigNull#parent to rigNull			    			    
			except Exception,error:raise StandardError,"[Naming |error: {0}]".format(error)
			#self.log_infoNestedDict('d_buffer')
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)
	    except Exception,error:raise StandardError,"[create_curvesFromDict |error: {0}]".format(error)
	    
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
