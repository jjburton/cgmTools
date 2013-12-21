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
__version__ = 0.11222013

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
	                        {'step':'Handle Joints','call':self.build_handleJoints},
	                        {'step':'Connections','call':self.build_connections}
	                        ]	
	    #=================================================================
	
	def gatherInfo(self):
	    mi_go = self._go#Rig Go instance link
	    self.mi_skullPlate = mi_go._mi_skullPlate
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    
	    for attr in self.mi_helper.getAttrs(userDefined = True):#Get allof our Helpers
		if "Helper" in attr:
		    try:self.__dict__["mi_%s"%attr.replace('Helper','Crv')] = cgmMeta.validateObjArg(self.mi_helper.getMessage(attr),noneValid=False)
		    except Exception,error:raise StandardError, " Failed to find '%s' | %s"%(attr,error)
		
		
	    #>> Find our joint lists ===================================================================
	    self.md_jointList = {}
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
	    #Build our handle build info stuff...
	    #TODO make this a contditional build for when we don't use all the joints
	    self.md_handleBuildInfo = {"jawAnchor":{"left":{'skinKey':'jawLineLeft'},
	                                            "right":{'skinKey':'jawLineRight'},
	                                            'tags':['jawAnchor'],
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
	                               "tongue":{"center":{'skinKey':'tongue'},'mode':'startEnd','tags':['tongueBase','tongueTip']},
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
	    
	def build_handleJoints(self):
	    mi_go = self._go#Rig Go instance link	    
	    ml_moduleHandleJoints = []
	    l_keys = self.md_handleBuildInfo.keys()
	    int_lenMax = len(l_keys)
	    for i,k_name in enumerate(l_keys):#For each name...
		d_nameBuffer = self.md_handleBuildInfo[k_name]
		for k_direction in ['left','right','center']:#for each direction....
		    self.progressBar_set(status = "Building handles: %s %s... "%(k_direction,k_name), progress = i, maxValue = int_lenMax)		    				    		    		    
		    try:
			d_buffer = d_nameBuffer.get(k_direction)
			l_tags = d_nameBuffer.get('tags') or False
			#if l_tags:self.log_info(l_tags)
			l_tagsPosition = d_nameBuffer.get('tagsPosition') or False			
			str_mode = d_nameBuffer.get('mode') or 'regularMid'
			#if not d_buffer:raise StandardError,"%s %s fail"%(k_name,k_direction)
			if d_buffer:
			    #self.log_info("Building '%s' | '%s' handle joints | mode: %s"%(k_name,k_direction,str_mode))
			    try:ml_skinJoints = self.md_jointList[d_buffer['skinKey']]
			    except:ml_skinJoints = []
			    ml_handleJoints = []
			    self.l_build = []
			    #Build our copy list -------------------------------------------
			    if str_mode in ['regularMid','midSmileLinePoint']:
				self.l_build = [ml_skinJoints[0],'mid',ml_skinJoints[-1]]		    
			    elif str_mode == 'startEnd':
				self.l_build = [ml_skinJoints[0],ml_skinJoints[-1]]
			    elif str_mode == 'zeroDuplicate':
				self.l_build = [ml_skinJoints[0]]		    
			    else:
				self.l_build = ml_skinJoints
			    #Build ----------------------------------------------------------
			    if str_mode in ['simpleDuplicate','zeroDuplicate']:
				mi_jnt = cgmMeta.cgmObject( mc.duplicate(self.l_build[0].mNode,po=True,ic=True,rc=True)[0],setClass=True )
				mi_jnt.parent = False#Parent to world	
				if l_tags:
				    mi_jnt.addAttr('cgmName',l_tags[0],attrType='string',lock=True)				    				    			    
				mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)
				mi_jnt.doName()
				ml_handleJoints.append(mi_jnt)
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
				ml_handleJoints.append(mi_jnt)
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
				ml_handleJoints.append(mi_jnt)
				
			    elif str_mode in ['midSimpleAim','midAimBlend']:
				try:#Get our data...
				    minU = d_buffer['minU']
				    maxU = d_buffer['maxU']
				    b_reverse = d_buffer['reverse']
				    mi_crv = d_buffer['crv']
				    mi_up = d_nameBuffer['mi_up']	
				    v_up = d_nameBuffer['v_up']					
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
				    ml_handleJoints.append(mi_jnt)				
				except Exception,error:raise StandardError,"[Simple aim build fail]{%s}"%error
				try:#Orient
				    if str_mode == 'midSimpleAim':
					try:
					    mi_aim = d_nameBuffer['mi_aim']
					    v_aim = d_nameBuffer['v_aim']			
					    mc.delete( mc.aimConstraint(mi_aim.mNode, mi_jnt.mNode,
						                        weight = 1, aimVector = v_aim, upVector = v_up,
						                        worldUpObject = mi_up.mNode, worldUpType = 'object' ) )
					except Exception,error:raise StandardError,"Simple aim fail: %s"%error
				    elif str_mode == 'midAimBlend':
					try:
					    mi_aimIn = d_buffer['mi_aimIn']
					    v_aimIn = d_buffer['v_aimIn']
					    mi_locIn = mi_jnt.doLoc()
					    mi_aimOut = d_buffer['mi_aimOut']
					    v_aimOut = d_buffer['v_aimOut']	
					    mi_locOut = mi_jnt.doLoc()
					    mc.delete( mc.aimConstraint(mi_aimIn.mNode, mi_locIn.mNode,
						                        weight = 1, aimVector = v_aimIn, upVector = v_up,
						                        worldUpObject = mi_up.mNode, worldUpType = 'object' ) )	
					    mc.delete( mc.aimConstraint(mi_aimOut.mNode, mi_locOut.mNode,
						                        weight = 1, aimVector = v_aimOut, upVector = v_up,
						                        worldUpObject = mi_up.mNode, worldUpType = 'object' ) )
					    mc.delete( mc.orientConstraint([mi_locIn.mNode,mi_locOut.mNode], mi_jnt.mNode,
						                           weight = 1) )
					    mc.delete([mi_locIn.mNode,mi_locOut.mNode])
					except Exception,error:raise StandardError,"[midAimBlend aim fail]{%s}"%error
					
				    jntUtils.metaFreezeJointOrientation(mi_jnt)				
				except Exception,error:raise StandardError,"[mid fail]{%s}"%error
			    else:
				for i,mJnt in enumerate(self.l_build):
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
					if len(self.l_build)>1:
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
					ml_handleJoints.append(i_j)			
			    
			    d_buffer['handle'] = ml_handleJoints
			    ml_moduleHandleJoints.extend(ml_handleJoints)
			    
			    ml_rightHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints , cgmDirection = 'right')
			    for mJoint in ml_rightHandles:
				#self.log_info("%s flipping"% mJoint.p_nameShort)
				mJoint.__setattr__("r%s"% mi_go._jointOrientation[1],180)
				jntUtils.freezeJointOrientation(mJoint)			
		    except Exception,error:raise StandardError,"[%s | %s failed]{%s}"%(k_name,k_direction,error)    
				
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
	    self.ml_rigJointsToSetup = []
	    
	    l_missingCurves = []
	    for mJnt in self.ml_handleJoints:
		if not mJnt.getMessage('controlShape'):l_missingCurves.append(mJnt.p_nameShort)
	    for mJnt in self.ml_rigJoints:
		if mJnt.getMessage('controlShape'):self.ml_rigJointsToSetup.append(mJnt)	
		
	    if l_missingCurves:
		self.log_error("Following joints missing curves: ")
		for obj in l_missingCurves:
		    self.log_error(">"*5 + " %s"%obj)
		raise StandardError,"Some joints missing controlShape curves"
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
	    ml_handleJoints = self.ml_handleJoints
		
	    l_strTypeModifiers = ['direct',None]
	    for ii,ml_list in enumerate( [ml_rigJoints,ml_handleJoints] ):
		str_typeModifier = l_strTypeModifiers[ii]
		int_lenMax = len(ml_list)		
		for i,mObj in enumerate(ml_list):
		    str_mirrorSide = False
		    try:
			self.progressBar_set(status = "Registering: '%s'"%mObj.p_nameShort, progress =  i, maxValue = int_lenMax)		    				    		    			
			#self.log_info("%s On '%s'..."%(self._str_reportStart,mObj.p_nameShort))
			mObj.parent = mi_go._i_deformNull
			str_mirrorSide = mi_go.verify_mirrorSideArg(mObj.getAttr('cgmDirection'))#Get the mirror side
			_addForwardBack = "t%s"%mi_go._jointOrientation[0]
			str_cgmNameTag = mObj.getAttr('cgmName')
			str_cgmDirection = mObj.getAttr('cgmDirection')
			if str_cgmNameTag in ['tongueBase','tongueTip','jaw','noseTip']:_addForwardBack = False
			elif ii == 0 and str_cgmNameTag in ['noseTop','noseUnder','noseBase']:_addForwardBack = False#nose controls
			elif str_cgmDirection == 'center' and ii == 0:_addForwardBack = False#other center controls

			if str_cgmNameTag in ['jaw','noseMove','mouthMove','noseTop','noseUnder','noseTip','tongueTip','tongueBase']:_str_mirrorAxis = 'translateX,rotateY,rotateZ'
			else:_str_mirrorAxis = 'translateZ,rotateX,rotateY'

			#Register 
			try:
			    d_buffer = mControlFactory.registerControl(mObj, useShape = mObj.getMessage('controlShape'),addForwardBack = _addForwardBack,
				                                       mirrorSide = str_mirrorSide, mirrorAxis=_str_mirrorAxis,		                                           
				                                       makeAimable=False, typeModifier=str_typeModifier) 	#translateZ,rotateX,rotateY    
			except Exception,error:
			    self.log_error("mObj: %s"%mObj.p_nameShort)
			    self.log_error("useShape: %s"%mObj.getMessage('controlShape'))
			    self.log_error("mirrorSide: %s"%str_mirrorSide)	
			    self.log_error("_str_mirrorAxis: %s"%_str_mirrorAxis)					    
			    self.log_error("forwardBack flag: %s"%_addForwardBack)						    
			    raise StandardError,"Register fail!]{%s}"%error
			
			#Vis sub connect
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
	                        {'step':'Tongue build','call':self._buildTongue_},	                        
	                        {'step':'Lip build','call':self._buildLips_},
	                        {'step':'NoseBuild','call':self._buildNose_},
	                        {'step':'Smile Line Build','call':self._buildSmileLines_},	                        
	                        {'step':'Cheek build','call':self._buildCheeks_},
	                        {'step':'Lock N hide','call':self._lockNHide_},
	                        
	                        ]	
	    #=================================================================
	def _gatherInfo_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    
	    self.mi_skullPlate = mi_go._mi_skullPlate
	    self.str_skullPlate = mi_go._mi_skullPlate.p_nameShort
	    
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
	    self.md_rigList = {"squash":{},
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
		d_cheekBuild = {#'cheekHandle':{"left":{},"right":{},'check':ml_handleJoints,'tag':'cheek'},
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
			self.log_error("%s | Check toggle off"%(k_tag))
		except Exception,error:raise StandardError,"%s loop | %s"%(k_tag,error)
	    #self.log_infoNestedDict('md_rigList')
		
	    #>> Squash --------------------------------------------------------------------------------------------------

	    #>> Calculate ==========================================================================
	    #Width of the skull plate...trying
	    self.f_offsetOfUpLoc = distance.returnBoundingBoxSizeToAverage(self.mi_skullPlate.mNode)
	    '''
	    self.f_offsetOfUpLoc = distance.returnDistanceBetweenObjects(self.md_rigList['brow']['left']['ml_rigJoints'][0].mNode,
	                                                                 self.md_rigList['brow']['left']['ml_rigJoints'][-1].mNode)
	    '''
	    #>> Running lists ==========================================================================
	    self.ml_toVisConnect = []
	    self.ml_curves = []
	    self.md_attachReturns = {}

	    return True
	
	def _buildSkullDeformation_(self):
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
		mi_parentHeadHandle = mi_go._mi_parentHeadHandle		
		mi_constrainNull =  mi_go._i_faceDeformNull
	    except Exception,error:raise StandardError,"!Query! | %s"%(error)
	    
	    try:#>> Simple def=======================================================================================
		self._buildSimpleSkullDeformation_()
	    except Exception,error:raise StandardError,"!setup simple def! | %s"%(error)	

	    
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
		
	    except Exception,error:raise StandardError,"!Query! | %s"%(error)
	    
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
		                        'noseMoveDef':{'toDup':mi_noseMoveHandle,'parent': False},
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
			except Exception,error:raise StandardError,"!Query! | %s"%(error)
			
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
			self.md_rigList['noseMoveDef'][0].parent = self.md_rigList['faceBaseDef'][0]			
			
			mi_jawRig.parent = self.md_rigList['faceBaseDef'][0]	
		    except Exception,error:raise StandardError,"!post parenting! | %s"%(error)
			
		except Exception,error:raise StandardError,"!def duplication! | %s"%(error)	
		
		#self.log_infoNestedDict('d_buffer')
	    except Exception,error:raise StandardError,"!Get Joints! | %s"%(error)	
	    
	    try:#>> Skin  =======================================================================================
		d_build = {'lwrLipBase':{'target':self.mi_skullPlate,'mi':5,'dr':5,
		                         'bindJoints':ml_skinJoints + [mi_jawRig]}}
		self.skin_fromDict(d_build)
		
	    except Exception,error:raise StandardError,"[Skin skull!]{%s}"%(error)	
	    
	    try:#>> Connect  =======================================================================================
		mc.parentConstraint(mi_jawHandle.mNode,mi_jawRig.mNode)
		mc.scaleConstraint(mi_jawHandle.mNode,mi_jawRig.mNode)
		
		#ConnectVis
		mi_go.connect_toRigGutsVis(self.md_rigList['faceBaseDef'],vis = True)#connect to guts vis switches
		
	    except Exception,error:raise StandardError,"[Connect!]{%s}"%(error)
	    
	    try:#>> StableJaw  =======================================================================================
		mc.orientConstraint(mi_jawRig.mNode,self.md_rigList['stableJaw'][0].mNode,skip = ["%s"%mi_go._jointOrientation[2]])
		mc.pointConstraint(mi_jawRig.mNode,self.md_rigList['stableJaw'][0].mNode,skip = ["%s"%str_axis for str_axis in [mi_go._jointOrientation[0],mi_go._jointOrientation[1]]])		
		self.md_rigList['stableJaw'][0].rotateOrder = mi_go._jointOrientation
	    except Exception,error:raise StandardError,"[Stable!]{%s}"%(error)
	    
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
			    except Exception,error:raise StandardError,"Radial Loft | %s"%(error)
			else:
			    try:#Regular loft -----------------------------------------------------------------------
				ml_joints = d_buffer['joints']
				mi_crv = d_buffer['extrudeCrv']

				try:#Make our loft loc -----------------------------------------------------------------------
				    #f_dist = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_joints])*.05
				    d_buffer['dist'] = f_dist
				    
				    mi_loc = ml_joints[-1].doLoc()
				    mi_loc.doGroup()
				except Exception,error:raise StandardError,"loft loc | %s"%(error)
				
				try:#Cross section creation -----------------------------------------------------------------------
				    l_profileCrvPos = []
				    for dist in [0,f_dist]:
					mi_loc.__setattr__("t%s"%mi_go._jointOrientation[1],dist)
					l_profileCrvPos.append(mi_loc.getPosition())
					
				    str_profileCrv = mc.curve(d = 1,ep = l_profileCrvPos, os = True)
				except Exception,error:raise StandardError,"Cross section creation | %s"%(error)
				
				try:#Extrude crv -----------------------------------------------------------------------
				    str_extruded = mc.extrude([str_profileCrv,mi_crv.mNode],et = 1, sc = 1,ch = 1,useComponentPivot = 0,fixedPath=1)[0]
				    mi_obj = cgmMeta.cgmObject(str_extruded)
				    mc.delete(mi_loc.parent,str_profileCrv)
				except Exception,error:raise StandardError,"Extrude crv | %s"%(error)	
			    except Exception,error:raise StandardError,"Regular loft | %s"%(error)
			try:
			    self.__dict__['mi_%sRibbon'%(str_name)] = mi_obj
			    mi_obj.addAttr('cgmName',str_name,lock=True)
			    mi_obj.addAttr('cgmTypeModifier','ribbon',lock=True)			    
			    try:mi_obj.addAttr('cgmDirection',d_buffer['direction'] ,lock=True)
			    except:pass
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sRibbon"%str_name,'module')			    
			except Exception,error:raise StandardError,"Naming | %s"%(error)
			#self.log_infoNestedDict('d_buffer')
			
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)
	    except Exception,error:raise StandardError,"Ribbons | %s"%(error)
	    
	    
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
				    
				except Exception,error:raise StandardError,"Rail curve build | %s"%(error)
				
				try:				    
				    ml_endProfileObjs = [ml_startRailObjs[-1],d_buffer['cheekJoints'][0], ml_endRailObjs[-1]]
				    self.log_info("endProfileObjs: %s"%[mObj.p_nameShort for mObj in ml_endProfileObjs])
				    str_endProfileCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endProfileObjs], os = True)
				    str_startProfileCrv = mc.rebuildCurve (mi_smileCrv.mNode, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    str_endProfileCrvRebuilt = mc.rebuildCurve (str_endProfileCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]
				    
				except Exception,error:raise StandardError,"Profile curves build | %s"%(error)	
				
				try:
				    str_loft = mc.doubleProfileBirailSurface( str_startProfileCrv, str_endProfileCrvRebuilt,
				                                              str_startRailCrv, str_endRailCrv, 
				                                              blendFactor = .5,constructionHistory=0, object=1, polygon=0, transformMode=0)[0]
				except Exception,error:raise StandardError,"birail create | %s"%(error)	
				
				mc.delete([str_startProfileCrv,str_startRailCrv,str_endRailCrv,str_endProfileCrv])#Delete the rebuilt curves
			    except Exception,error:raise StandardError,"Reg plate loft | %s"%(error)	
			else:
			    try:#Reg curve loft
				l_crvsRebuilt = []
				for mi_crv in d_buffer['crvs']:#rebuild crvs
				    l_crvsRebuilt.append(self.returnRebuiltCurveString(mi_crv,4))
				
				str_loft = mc.loft(l_crvsRebuilt,uniform = True,degree = 3,ss = 3)[0]
				mc.delete(l_crvsRebuilt)#Delete the rebuilt curves
			    except Exception,error:raise StandardError,"Reg plate loft | %s"%(error)	
			
			try:#tag, name, store
			    mi_obj = cgmMeta.cgmObject(str_loft)
			    self.__dict__['mi_%sPlate'%(str_name)] = mi_obj
			    mi_obj.addAttr('cgmName',d_buffer.get('name') or str_name,lock=True)
			    try:mi_obj.addAttr('cgmDirection',str_direction ,lock=True)
			    except:pass
			    mi_obj.addAttr('cgmTypeModifier','plate',lock=True)					    
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sPlate"%str_name,'module')
			except Exception,error:raise StandardError,"Tag/Name/Store | %s"%(error)	
			
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)	
		    #self.log_infoNestedDict('d_buffer')		    
	    except Exception,error:raise StandardError,"Plate | %s"%(error)
	    
		
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
	    except Exception,error:raise StandardError,"!Info Gather! | %s"%(error)
	    
	    try:#>> Build segment =======================================================================================
		#Create segment
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
		except Exception,error:raise StandardError,"!post segment query! | %s"%(error)
		
		try:#post segmentparent
		    mi_curve.segmentGroup.parent = mi_go._i_rigNull.mNode
		    for attr in 'translate','scale','rotate':
			cgmMeta.cgmAttr(mi_curve,attr).p_locked = False
		    mi_curve.parent = mi_go._i_rigNull
		    
		    mi_anchorEnd.parent = mi_jawHandle
		    mi_anchorStart.parent = mi_jawHandle
		
		except Exception,error:raise StandardError,"!post segment parent! | %s"%(error)
		
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
	    except Exception,error:raise StandardError,"!cgmSegment creation! | %s"%(error)
	    
	    try:#>>>Connect master scale
		mi_distanceBuffer = mi_curve.scaleBuffer		
		cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn(mPlug_multpHeadScale.p_combinedShortName)    
	    except Exception,error:raise StandardError,"!segment scale connect! | %s"%(error)
	    
	    try:#Do a few attribute connections
		#Push squash and stretch multipliers to cog
		try:
		    for k in mi_distanceBuffer.d_indexToAttr.keys():
			attrName = 'scaleMult_%s'%k
			cgmMeta.cgmAttr(mi_distanceBuffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_tongueTip.mNode,attrName,connectSourceToTarget = True)
			cgmMeta.cgmAttr(mi_tongueTip.mNode,attrName,defaultValue = 1)
			cgmMeta.cgmAttr('cog_anim',attrName, keyable =True, lock = False)    
		except Exception,error:raise StandardError,"!scaleMult transfer! | %s"%(error)
		
		cgmMeta.cgmAttr(mi_curve,'twistType').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
		cgmMeta.cgmAttr(mi_curve,'twistExtendToEnd').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
		cgmMeta.cgmAttr(mi_curve,'scaleMidUp').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
		cgmMeta.cgmAttr(mi_curve,'scaleMidOut').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
		
	    except Exception,error:raise StandardError,"!segment attribute transfer! | %s"%(error)

	    
	    return
	    try:#Build Ribbons --------------------------------------------------------------------------------------
		md_ribbonBuilds = {'nostril':{'extrudeCrv':self.mi_noseBaseCastCrv,
	                                      'joints':self.md_rigList['sneerHandle']['left'] + self.md_rigList['sneerHandle']['right']}}	
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"!Ribbons! | %s"%(error)
		
	    try:#Build plates --------------------------------------------------------------------------------------
		md_plateBuilds = {'nose':{'crvs':[self.mi_noseTopCastCrv,self.mi_noseMidCastCrv,self.mi_noseBaseCastCrv,self.mi_mouthTopCastCrv]}}
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"!Plates! | %s"%(error)
	    """
	    try:#Build Tracklocs ===================================================================================================
		str_base = 'noseMove'
		d_trackLocs = {'target':self.md_rigList['noseMoveHandle'][0],
			       'tags':['stable','def']}
		for str_tag in d_trackLocs['tags']:
		    try:
			mi_loc = d_trackLocs['target'].doLoc()
			mi_loc.addAttr('cgmTypeModifier',str_tag)
			mi_loc.doName()
			str_tmp = '%s%sLoc'%(str_base,str_tag.capitalize())
			
			try:
			    i_masterGroup = (cgmMeta.cgmObject(mi_loc.doGroup(True),setClass=True))
			    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
			    i_masterGroup.doName()
			    mi_loc.connectChildNode(i_masterGroup,'masterGroup','groupChild')			
			except Exception,error:raise StandardError,"!masterGroup! | %s"%(error)
			
			self.log_info("'%s' created"%str_tmp)
			
			self.md_rigList[str_tmp] = [mi_loc]
			self.__dict__['mi_%s'%str_tmp] = mi_loc
			d_trackLocs['target'].connectChildNode(mi_loc,'%sLoc'%str_tag,'owner')
		    except Exception,error:raise StandardError,";%s' !loc setup! | %s"%(str_tag,error)
		    
	    except Exception,error:raise StandardError,"!Track locs! | %s"%(error)
	    """
	    
	    try:#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_nosePlate = self.mi_nosePlate.p_nameShort
		str_nostrilRibbon = self.mi_nostrilRibbon.p_nameShort	    
		try:str_noseMoveMasterGroup = self.md_rigList['noseMoveRig'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"NoseMove master group find fail | %s"%(error)
		#'nostrilHandle':{'attachTo':str_nosePlate,'mode':'handleAttach'}
		d_build = {'nostrilRig':{'attachTo':str_nosePlate},
	                   'nostrilHandle':{'attachTo':str_nostrilRibbon,'mode':'handleAttach'},
	                   'noseMoveHandle':{'mode':'blendAttach','defaultValue':.1,'followSuffix':'Jaw'},
	                   #'noseMoveStableLoc':{'mode':'stableAttach'},
	                   #'noseMoveDefLoc':{'mode':'handleAttach'},		           
	                   'noseMoveRig':{},	               
	                   'noseTipRig':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseTipHandle'][0]},
	                   'noseTipHandle':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseMoveRig'][0]},
	                   'noseUnderRig':{},
	                   'noseUnderHandle':{'mode':'parentOnly','attachTo':None,'parentTo':str_noseMoveMasterGroup},
	                   'noseTopRig':{},
	                   'noseTopHandle':{'mode':'handleAttach'}
	                   }
		self.attach_fromDict(d_build)
	    except Exception,error:raise StandardError,"!Attach! | %s"%(error)
	    
	    #self.log_infoNestedDict('md_attachReturns')
	    try:#>> Skin nose  =======================================================================================
		self.progressBar_setMaxStepValue(4)		
		try:#Build list
		    self.progressBar_set(status = "Skinning Nose", step = 1)
		    
		    l_toBind = [str_nosePlate]	
		    'noseMoveHandle','noseUnderHandle'
		    for tag in ['noseTipRig','noseTopRig','noseMoveHandle','noseUnderRig']:
			l_toBind.append(self.md_rigList[tag][0].p_nameShort)
		    for tag in ['smileLineRig','nostrilHandle']:
			for str_side in 'left','right':
			    l_toBind.append(self.md_rigList[tag][str_side][0].p_nameShort)
		except Exception,error:raise StandardError,"build list | %s"%(error)
		
		ret_cluster = mc.skinCluster(l_toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
		i_cluster = cgmMeta.cgmNode(ret_cluster[0],setClass=True)
		i_cluster.doStore('cgmName',str_nosePlate)
		i_cluster.doName()
		
	    except Exception,error:raise StandardError,"!Skin nose plate| %s"%(error)		
	    
	    try:#>> Skin nostril Move =======================================================================================
		try:#Build list
		    self.progressBar_set(status = "Skinning Nostril", step = 3)
		    
		    l_toBind = [str_nostrilRibbon]	
		    for tag in ['noseTipRig','noseMoveHandle','noseUnderRig']:
			l_toBind.append(self.md_rigList[tag][0].p_nameShort)
		    for tag in ['smileLineRig']:
			for str_side in 'left','right':
			    l_toBind.append(self.md_rigList[tag][str_side][0].p_nameShort)
		except Exception,error:raise StandardError,"build list | %s"%(error)
		
		ret_cluster = mc.skinCluster(l_toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
		i_cluster = cgmMeta.cgmNode(ret_cluster[0],setClass=True)
		i_cluster.doStore('cgmName',str_nostrilRibbon)
		i_cluster.doName()
		
	    except Exception,error:raise StandardError,"!Skin nostril plate! | %s"%(error)	
	    
	    #>>> Connect build dict ==================================================================
	    d_build = {'noseMove':{},
                       'noseTop':{},
                       'noseUnder':{}}
	    
	    try:#>> Connect rig joints to handles ====================================================
		
		self.progressBar_setMaxStepValue(len(d_build.keys()))
		for str_tag in d_build.iterkeys():
		    try:
			self.progressBar_iter(status = ("Connecting : '%s'"%str_tag))
			try:#Get ----------------------------------------------------
			    mi_handle = self.md_rigList[str_tag+'Handle'][0]
			    mi_rigJoint = self.md_rigList[str_tag+'Rig'][0]
			except Exception,error:raise StandardError,"[Quer]{ %s}"%(error)			
			
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
			except Exception,error:raise StandardError,"[Offset grou]{%s}"%(error)
			
		    except Exception,error:  raise StandardError,"%s | %s"%(str_tag,error)
		    
	    except Exception,error:  raise StandardError,"[Connect rig>handle!]{%s}"%(error)	
			
	    try:#>> Nose Move =======================================================================================
		self.progressBar_set(status = "Setting up nose move")
		
		mi_handle = self.md_rigList['noseMoveHandle'][0]
		mi_rigJoint = self.md_rigList['noseMoveRig'][0]
		
		try:#Connect the control loc to the center handle
		    mi_controlLoc = self.md_attachReturns[mi_rigJoint]['controlLoc']
		    mc.pointConstraint(mi_handle.mNode,mi_controlLoc.mNode)
		except Exception,error:raise StandardError,"[Control loc connect]{%s}"%(error)	
		
		try:#Setup the offset to push handle rotation to the rig joint control
		    #Create offsetgroup for the mid
		    mi_offsetGroup = cgmMeta.cgmObject( mi_rigJoint.doGroup(True),setClass=True)	 
		    mi_offsetGroup.doStore('cgmName',mi_rigJoint.mNode)
		    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		    mi_offsetGroup.doName()
		    mi_rigJoint.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
		    
		    cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
		except Exception,error:raise StandardError,"[Offset grou]{ %s}"%(error)
		
		'''
		try:#Blend move handle
		    #Query
		    mi_handle = self.md_rigList['noseMoveHandle'][0]		    
		    mi_stableLoc = self.md_rigList['noseMoveStableLoc'][0]
		    mi_defLoc = self.md_rigList['noseMoveDefLoc'][0]
		    mi_faceDef = self.md_rigList['faceBaseDef'][0]
		    
		    self.d_buffer['mi_handle'] = mi_handle		    
		    self.d_buffer['mi_stableLoc'] = mi_stableLoc
		    self.d_buffer['mi_defLoc'] = mi_defLoc
		    self.d_buffer['mi_faceDef'] = mi_faceDef
		    
		    try:#Constrain the stable loc to the face
			mi_controlLoc = self.md_attachReturns[mi_stableLoc]['controlLoc']
			mc.pointConstraint(mi_faceDef.mNode,mi_controlLoc.mNode,maintainOffset = True)
		    except Exception,error:raise StandardError,"!Stable loc controlLoc! | %s"%(error)
		    
		    try:#Create constrain the handle master Group
			str_parentConstraint = mc.parentConstraint([mi_stableLoc.mNode,mi_defLoc.mNode],mi_handle.masterGroup.mNode,
								   maintainOffset = True)[0]
		    except Exception,error:raise StandardError,"!Parent Constraint! | %s"%(error)
		    
		    try:
			#EndBlend
			d_blendFollowReturn = NodeF.createSingleBlendNetwork([mi_handle.mNode,'followDeformation'],
									     [mi_handle.mNode,'resultStableFollow'],
									     [mi_handle.mNode,'resultDefFollow'],
									     keyable=True)
			l_targetWeights = mc.parentConstraint(str_parentConstraint,q=True, weightAliasList=True)
			#Connect                                  
			d_blendFollowReturn['d_result1']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[1]))
			d_blendFollowReturn['d_result2']['mi_plug'].doConnectOut('%s.%s' % (str_parentConstraint,l_targetWeights[0]))
			d_blendFollowReturn['d_result1']['mi_plug'].p_hidden = True
			d_blendFollowReturn['d_result2']['mi_plug'].p_hidden = True			
		    except Exception,error:raise StandardError,"!Blend setup! | %s"%(error)
		    
		except Exception,error:
		    self.log_infoNestedDict('d_buffer')
		    raise StandardError,"!Setup follow loc blend!|!]{%s}"%(error)'''		
		
		
		'''
		try:#Create the brow up loc and parent it to the 
		    mi_browFrontUpLoc = mi_offsetGroup.doLoc()
		    mi_browFrontUpLoc.parent = mi_offsetGroup.parent
		    mi_browFrontUpLoc.tz = f_offsetOfUpLoc
		    self.mi_browFrontUpLoc = mi_browFrontUpLoc
		except Exception,error:raise StandardError,"[Offset grou]{ %s}"%(error)
		'''
	    except Exception,error:
		raise StandardError,"!Center Nose! | %s"%(error)
    
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
	    try:#Build Ribbons --------------------------------------------------------------------------------------
		md_ribbonBuilds = {'nostril':{'extrudeCrv':self.mi_noseBaseCastCrv,
		                              'joints':self.md_rigList['sneerHandle']['left'] + self.md_rigList['sneerHandle']['right']}}	
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"!Ribbons! | %s"%(error)
		
	    try:#Build plates --------------------------------------------------------------------------------------
		md_plateBuilds = {'nose':{'crvs':[self.mi_noseTopCastCrv,self.mi_noseMidCastCrv,self.mi_noseBaseCastCrv,self.mi_mouthTopCastCrv]}}
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"!Plates! | %s"%(error)
	    
	    try:#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_nosePlate = self.mi_nosePlate.p_nameShort
		str_nostrilRibbon = self.mi_nostrilRibbon.p_nameShort	    
		try:str_noseMoveMasterGroup = self.md_rigList['noseMoveRig'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"NoseMove master group find fail | %s"%(error)
		#'nostrilHandle':{'attachTo':str_nosePlate,'mode':'handleAttach'}
		d_build = {'nostrilRig':{'attachTo':str_nosePlate},
		           'nostrilHandle':{'attachTo':str_nostrilRibbon,'mode':'handleAttach'},
		           'noseMoveHandle':{'mode':'blendAttach','defaultValue':.9,'followSuffix':'Jaw'},	           
		           'noseMoveRig':{},	               
		           'noseTipRig':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseTipHandle'][0]},
		           'noseTipHandle':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseMoveRig'][0]},
		           'noseUnderRig':{},
		           'noseUnderHandle':{'mode':'parentOnly','attachTo':None,'parentTo':str_noseMoveMasterGroup},
		           'noseTopRig':{},
		           'noseTopHandle':{'mode':'handleAttach'}
		           }
		self.attach_fromDict(d_build)
	    except Exception,error:raise StandardError,"!Attach! | %s"%(error)
	    
	    #self.log_infoNestedDict('md_attachReturns')
	    try:#>> Skin nose  =======================================================================================
		self.progressBar_setMaxStepValue(4)		
		try:#Build list
		    self.progressBar_set(status = "Skinning Nose", step = 1)
		    l_toBind = [str_nosePlate]	
		    'noseMoveHandle','noseUnderHandle'
		    for tag in ['noseTipRig','noseTopRig','noseMoveHandle','noseUnderRig']:
			l_toBind.append(self.md_rigList[tag][0].p_nameShort)
		    for tag in ['smileLineRig','nostrilHandle']:
			for str_side in 'left','right':
			    l_toBind.append(self.md_rigList[tag][str_side][0].p_nameShort)
		except Exception,error:raise StandardError,"build list | %s"%(error)
		
		ret_cluster = mc.skinCluster(l_toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
		i_cluster = cgmMeta.cgmNode(ret_cluster[0],setClass=True)
		i_cluster.doStore('cgmName',str_nosePlate)
		i_cluster.doName()
		
	    except Exception,error:raise StandardError,"!Skin nose plate| %s"%(error)		
	    
	    try:#>> Skin nostril Move =======================================================================================
		try:#Build list
		    self.progressBar_set(status = "Skinning Nostril", step = 2)
		    
		    l_toBind = [str_nostrilRibbon]	
		    for tag in ['noseTipRig','noseMoveHandle','noseUnderRig']:
			l_toBind.append(self.md_rigList[tag][0].p_nameShort)
		    for tag in ['smileLineRig']:
			for str_side in 'left','right':
			    l_toBind.append(self.md_rigList[tag][str_side][0].p_nameShort)
		except Exception,error:raise StandardError,"build list | %s"%(error)
		
		ret_cluster = mc.skinCluster(l_toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
		i_cluster = cgmMeta.cgmNode(ret_cluster[0],setClass=True)
		i_cluster.doStore('cgmName',str_nostrilRibbon)
		i_cluster.doName()
		
	    except Exception,error:raise StandardError,"!Skin nostril plate! | %s"%(error)	
	    
	    #>>> Connect build dict ==================================================================
	    d_build = {'noseMove':{},
	               'noseTop':{},
	               'noseUnder':{}}
	    
	    try:#>> Connect rig joints to handles ====================================================
		mi_go = self._go#Rig Go instance link
		
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
			except Exception,error:raise StandardError,"[Control loc connec]{%s}"%(error)			
		    
			try:#Setup the offset to push handle rotation to the rig joint control
			    #Create offsetgroup for the mid
			    mi_offsetGroup = cgmMeta.cgmObject( mi_rigJoint.doGroup(True),setClass=True)	 
			    mi_offsetGroup.doStore('cgmName',mi_rigJoint.mNode)
			    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
			    mi_offsetGroup.doName()
			    mi_rigJoint.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
			    
			    cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
			except Exception,error:raise StandardError,"[Offset group]{%s}"%(error)
		    except Exception,error:  raise StandardError,"%s | %s"%(str_tag,error)
		    
	    except Exception,error:  raise StandardError,"!Connect rig>handle! | %s"%(error)	
			
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
	    except Exception,error:raise StandardError,"[Nose Move setup]{%s}"%(error)
	    
	    try:#>> Nose Move Up Loc =======================================================================================
		self.progressBar_set(status = "Setting up nose move up loc")
		mi_noseMove = self.md_rigList['noseMoveHandle'][0]
		mi_noseMoveUpLoc = mi_noseMove.doLoc()
		mi_noseMoveUpLoc.parent = mi_noseMove.masterGroup
		self.md_rigList['noseMoveUpLoc'] = [mi_noseMoveUpLoc]
		mi_noseMove.connectChildNode(mi_noseMoveUpLoc,'handleUpLoc','owner')
		mi_noseMoveUpLoc.__setattr__("t%s"%mi_go._jointOrientation[0],self.f_offsetOfUpLoc)
		mi_go.connect_toRigGutsVis(mi_noseMoveUpLoc,vis = True)#connect to guts vis switches
		
	    except Exception,error:raise StandardError,"[Nose Move Up Loc]{%s}"%(error)
	    
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
	    except Exception,error:raise StandardError,"[Aim Setup]{%s}"%(error)
	    
	    '''
	    try:#Create the brow up loc and parent it to the 
		mi_browFrontUpLoc = mi_offsetGroup.doLoc()
		mi_browFrontUpLoc.parent = mi_offsetGroup.parent
		mi_browFrontUpLoc.tz = f_offsetOfUpLoc
		self.mi_browFrontUpLoc = mi_browFrontUpLoc
	    except Exception,error:raise StandardError,"[Offset group]{%s}"%(error)
	    '''
	def _buildLips_(self):
	    #>> Get some data =======================================================================================
	    """
	    Stuff to setup...
	    1) attach base to skull plate
	    2) What should
	    
	    """	 
	    mi_go = self._go#Rig Go instance link	
	    
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
		    
		    for ml in ml_uprLipHandles,ml_lwrLipHandles:
			ml.insert(0,self.md_rigList['lipCornerRig']['left'][0])
			ml.append(self.md_rigList['lipCornerRig']['right'][0])
			
		    d_logs = {'uprLipRig':ml_uprLipRigJoints,
			      'lipLwrRig':ml_lwrLipRigJoints,
			      'uprLipHandle':ml_uprLipHandles,
			      'lwrLipHandle':ml_lwrLipHandles,
			      }
		    '''
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
		    except Exception,error:raise StandardError,"upper driven curve!]{%s}"%(error)  	    
		    
		    try:#Upper driver curve
			_str_uprDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_uprLipHandles],os =True)
			mi_uprDriverCrv = cgmMeta.cgmObject(_str_uprDriverCurve,setClass=True)
			mi_uprDriverCrv.doCopyNameTagsFromObject(mi_uprDrivenCrv.mNode,ignore=['cgmTypeModifier'])
			mi_uprDriverCrv.addAttr('cgmTypeModifier','driver',lock=True)
			mi_uprDriverCrv.doName()
			ml_curves.append(mi_uprDriverCrv)	    
		    except Exception,error:raise StandardError,"upper driver curve!]{%s}"%(error)  	    
		    
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
		    except Exception,error:raise StandardError,"upper driven curve!]{%s}"%(error)  	    
		    
		    try:#Lwr driver curve
			_str_lwrDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_lwrLipHandles],os =True)
			mi_lwrDriverCrv = cgmMeta.cgmObject(_str_lwrDriverCurve,setClass=True)
			mi_lwrDriverCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
			mi_lwrDriverCrv.addAttr('cgmName','lwrLip',lock=True)	    
			mi_lwrDriverCrv.doName()
			ml_curves.append(mi_lwrDriverCrv)	    	    	    
		    except Exception,error:raise StandardError,"upper driver curve!]{%s}"%(error)  	    
		    
		    try:#SmartLipSeal curve
			_str_smartLipSealCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_lwrLipHandles],os =True)
			mi_smartLipSealCrv = cgmMeta.cgmObject(_str_smartLipSealCurve,setClass=True)
			mi_smartLipSealCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
			mi_smartLipSealCrv.addAttr('cgmName','smartLipSeal',lock=True)	    
			mi_smartLipSealCrv.doName()
			ml_curves.append(mi_smartLipSealCrv)	    	    	    
		    except Exception,error:raise StandardError,"[smartLipSeal curve]{%s}"%(error)  
		    
		    try:
			for mi_crv in ml_curves:#Parent to rig null
			    mi_crv.parent = mi_go._i_deformNull
			    
			for mi_crv in [mi_smartLipSealCrv,mi_lwrLipSealCrv,mi_uprLipSealCrv]:
			    mi_crv.parent = mi_go._i_rigNull
			    
		    except Exception,error:raise StandardError,"[Curve parenting]{%s}"%(error)  
		except Exception,error:raise StandardError,"[Curve creation]{%s}"%(error)   
		    
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
			    except Exception,error:raise StandardError,"[loc creation]{%s}"%(error)  	    
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
		    except Exception,error:raise StandardError,"[wire deformer!]{%s}"%(error)  	    
		    
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
			    except Exception,error:raise StandardError,"skinCluster]{%s}"%(error)  	    
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
		    except Exception,error:raise StandardError,"[lipSeal setu!]{%s}s"%(error)  	
	    
		except Exception,error:
		    raise StandardError,"lip setup | %s"%(error)   	        
	    except Exception,error:
		raise StandardError,"[Smart Seal setup fail]{ %s}"%(error)   		    
	    
	    #Now we need to create a duplicate of our nasil curve and chin curve for our lip follow surface tracker
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
		'''
		for mi_crv in ml_curves:#Parent to rig null
		    mi_crv.parent = mi_go._i_rigNull
		self.ml_toVisConnect.extend(ml_curves)
		'''
	    except Exception,error:raise StandardError,"Curve creation | %s"%(error)   	    
	    '''
	    try:#Build Ribbons --------------------------------------------------------------------------------------
		md_ribbonBuilds = {'uprLip':{'extrudeCrv':self.mi_lipUprCrv,
		                              'joints':self.md_rigList['lipCornerHandle']['left'] + self.md_rigList['lipCornerHandle']['right']},
		                   'lwrLip':{'extrudeCrv':self.mi_lipLwrCrv,
		                             'joints':self.md_rigList['lipCornerHandle']['left'] + self.md_rigList['lipCornerHandle']['right']}}
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"Ribbons | %s"%(error)
	    '''
	    try:#Build plates ====================================================================================
		md_plateBuilds = {'uprLip':{'crvs':[self.mi_mouthTopCastCrv,self.mi_lipOverTraceCrv,self.mi_lipUprCrv]},
		                  'uprLipFollow':{'crvs':[self.mi_mouthTopTraceCrv,mi_uprDrivenCrv],'mode':'liveSurface'},
		                  'lwrLip':{'crvs':[self.mi_lipLwrCrv,self.mi_lipUnderTraceCrv,self.mi_mouthLowCastCrv]},
		                  'lwrLipFollow':{'crvs':[mi_lwrDrivenCrv,self.mi_mouthBaseTraceCrv],'mode':'liveSurface'}}
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"Plates | %s"%(error)
	    
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
		except Exception,error:raise StandardError,"MouthMove master group find fail | %s"%(error)
		    		
		try:str_mouthMoveTrackerMasterGroup = self.md_rigList['mouthMoveTrackLoc'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"MouthMoveTrack master group find fail | %s"%(error)
		
		try:#Make a chin track loc
		    mi_chinTrackLoc = self.md_rigList['chin'][0].doLoc()
		    i_masterGroup = (cgmMeta.cgmObject(mi_chinTrackLoc.doGroup(True),setClass=True))
		    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
		    i_masterGroup.doName()
		    mi_chinTrackLoc.connectChildNode(i_masterGroup,'masterGroup','groupChild')
		    self.md_rigList['chinTrackLoc'] = [mi_chinTrackLoc]
		    
		    mi_go.connect_toRigGutsVis(mi_chinTrackLoc,vis = True)#connect to guts vis switches
		    i_masterGroup.parent = mi_go._i_deformNull
		except Exception,error:raise StandardError,"ChinTrack master group find fail | %s"%(error)
		    		
		try:str_chinTrackerMasterGroup = self.md_rigList['chinTrackLoc'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"ChinTrack master group find fail | %s"%(error)			
	    except Exception,error:raise StandardError,"[Spcial Locs!]{%s}"%(error)
		
	    try:#Attach stuff to surfaces ====================================================================================
		#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_skullPlate = self.str_skullPlate
		
		str_uprLipPlate = self.mi_uprLipPlate.p_nameShort
		str_uprLipFollowPlate = self.mi_uprLipFollowPlate.p_nameShort		
		#str_uprLipRibbon = self.mi_uprLipRibbon.p_nameShort
		
		str_lwrLipPlate = self.mi_lwrLipPlate.p_nameShort
		str_lwrLipFollowPlate = self.mi_lwrLipFollowPlate.p_nameShort				
		#str_lwrLipRibbon = self.mi_lwrLipRibbon.p_nameShort
			
		'''
		{'lipUprHandle':{"left":{},"right":{},'center':{},'check':ml_handleJoints,'tag':'lipUpr'},
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
		'''
		d_build = {'mouthMove':{'mode':'blendAttach','defaultValue':.25,'followSuffix':'Jaw'},
		           'mouthMoveTrackLoc':{},
		           'chinTrackLoc':{},		           
		           'chin':{'mode':'handleAttach'},		           
		           'lipUprRig':{'mode':'handleAttach','attachTo':str_uprLipFollowPlate},
		           'lipOverRig':{'mode':'handleAttach','attachTo':str_uprLipPlate},		           
		           'lipUprHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode,
		                           'center':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode}},
		           'lipCornerRig':{},#reg, will be driven by...
		           'lipCornerHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode},
		           'lipLwrRig':{'mode':'handleAttach','attachTo':str_lwrLipFollowPlate},
		           'lipUnderRig':{'mode':'handleAttach','attachTo':str_lwrLipPlate},		           
		           'lipLwrHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode,
		                           'center':{'mode':'blendAttach','defaultValue':.6,
		                                     'followSuffix':'Jaw','target0':mi_mouthMoveTrackLoc}},
		           }		
		'''
		d_build = {'nostrilRig':{'attachTo':str_nosePlate},
		           'nostrilHandle':{'attachTo':str_nostrilRibbon,'mode':'handleAttach'},
		           'noseMoveHandle':{'mode':'handleAttach'},
		           'noseMoveRig':{},	               
		           'noseTipRig':{},
		           'noseTipHandle':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseMoveRig'][0]},
		           'noseUnderRig':{},
		           'noseUnderHandle':{'mode':'parentOnly','attachTo':None,'parentTo':str_noseMoveMasterGroup},
		           'noseTopRig':{},
		           'noseTopHandle':{'mode':'handleAttach'}
		           }
		'''
		self.attach_fromDict(d_build)
		
	    except Exception,error:raise StandardError,"[Attach!]{%s}"%(error)
	    
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
	    except Exception,error:raise StandardError,"!Center upr lip offsetgroup! | %s"%(error)
	    
	    #self.log_infoNestedDict('md_attachReturns')

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
		'''
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
		self.skin_fromDict(d_build)
		'''
		 'uprLipPlate':{'target':self.mi_uprLipPlate,
		                          'bindJoints':ml_uprLipHandles + self.md_rigList['smileLineRig']['left'] + self.md_rigList['noseUnderRig'] + self.md_rigList['smileLineRig']['right']},		           
		           
		'''
	    except Exception,error:raise StandardError,"!Skinning! | %s"%(error)	
	    
	        
	    try:#>>> Connect rig joints to handles ==================================================================
		d_build = {'lipCornerRig':{'rewireFollicleOffset':True},
		           'chinTrackLoc':{'driver':self.md_rigList['chin']},		           
		           'mouthMoveTrackLoc':{'driver':self.md_rigList['mouthMove']}}
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"!Connect! | %s"%(error)	
	    
	    try:#>>> Aim some stuff =================================================================================
		mi_mouthMoveUpLoc = self.md_attachReturns[mi_mouthMoveTrackLoc]['upLoc']
		mi_mouthMoveUpLoc.mNode
		mi_noseUnder = self.md_rigList['noseUnderHandle'][0]
		mi_chin = self.md_rigList['chin'][0]
		mi_noseMove = self.md_rigList['noseMoveHandle'][0]
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
		'''
		#'lipLwrRig':{'mode':'lipLineBlend','upLoc':mi_mouthMoveUpLoc}
		
		d_build = {'mouthMoveTrackLoc':{'mode':'singleVectorAim','v_aim':mi_go._vectorUp,'v_up':mi_go._vectorUp,
		                                'upLoc':mi_mouthMoveUpLoc,'aimTargets':[mi_noseMove,mi_noseMove.masterGroup,mi_noseMove.masterGroup]},
		           'chin':{'mode':'singleTarget','v_aim':mi_go._vectorUp,'v_up':mi_go._vectorUp,
		                   'upLoc':mi_mouthMoveUpLoc,'aimTarget':mi_lwrCenterHandle.masterGroup},
		           'lipUprRig':{'mode':'lipLineBlend','upLoc':mi_noseUnder,'v_up':mi_go._vectorUp},
		           'lipLwrRig':{'mode':'lipLineBlend','upLoc':mi_chin,'v_up':mi_go._vectorUpNegative}}
		self.aim_fromDict(d_build)
	    except Exception,error:raise StandardError,"!Aim! | %s"%(error)	
	    
	    try:#constrain mids ====================================================================================
		l_build = [{'obj':self.md_rigList['lipUprHandle']['left'][0],
	                   'targets':[self.md_rigList['lipUprHandle']['center'][0],
	                              self.md_rigList['lipCornerRig']['left'][0]],
	                   'mode':'parent'},
	                   {'obj':self.md_rigList['lipLwrHandle']['left'][0],
	                    'targets':[self.md_rigList['lipLwrHandle']['center'][0],
	                               self.md_rigList['lipCornerRig']['left'][0]],
	                    'mode':'pointOrient'},
		           {'obj':self.md_rigList['lipUprHandle']['right'][0],
		            'targets':[self.md_rigList['lipUprHandle']['center'][0],
		                       self.md_rigList['lipCornerRig']['right'][0]],
		            'mode':'parent'},
		            {'obj':self.md_rigList['lipLwrHandle']['right'][0],
		             'targets':[self.md_rigList['lipLwrHandle']['center'][0],
		                        self.md_rigList['lipCornerRig']['right'][0]],
		             'mode':'pointOrient'}]
			   
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
	    except Exception,error:raise StandardError,"[constrain mids!]{%s}"%(error)	    
	    
	    
	    return
	
	def _buildSmileLines_(self):
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
	    except Exception,error:raise StandardError,"[Curve duplication]{%s}"%(error)   	    
	    
	    '''
	    try:#Build Ribbons ===================================================================================================
		md_ribbonBuilds = {'smileLeft':{'extrudeCrv':self.mi_smileLeftCrv,'mode':'radialLoft','direction':'left',
		                                'aimObj':self.md_rigList['mouthMove'][0]},
		                   'smileRight':{'extrudeCrv':self.mi_smileRightCrv,'mode':'radialLoft','direction':'right',
		                                 'aimObj':self.md_rigList['mouthMove'][0]}}	
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"Ribbons | %s"%(error)
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
	    except Exception,error:raise StandardError,"[Attach!]{%s}"%(error)
	    	    
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
	    except Exception,error:raise StandardError,"[Skinning!]{%s}"%(error)	
	    
	    try:#>>> Connect rig joints to handles ==================================================================
		d_build = {'smileHandle':{'mode':'parentConstraint','rewireFollicleOffset':True,
		                          'left':{'targets':[self.md_rigList['lipCornerRig']['left'][0].masterGroup],
		                                  'rewireHandle':self.md_rigList['lipCornerHandle']['left'][0]},
		                          'right':{'targets':[self.md_rigList['lipCornerRig']['right'][0].masterGroup],
		                                   'rewireHandle':self.md_rigList['lipCornerHandle']['right'][0]}},
		           'smileLineRig':{'mode':'rigToFollow',
		                           'left':{'attachTo':self.mi_smileFollowLeftCrv},
		                           'right':{'attachTo':self.mi_smileFollowRightCrv}},   
		           'smileBaseHandle':{'mode':'parentConstraint',
		                              'targets':[self.md_rigList['chinTrackLoc'][0]]}}
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"[Connect!]{%s}"%(error)	
	    return	
	
	def _buildCheeks_(self):
	    mi_go = self._go#Rig Go instance link    
	    
	    try:#Build Curves ===================================================================================================
		md_curvesBuilds = {'uprCheekFollowLeft':{'pointTargets':self.md_rigList['uprCheekRig']['left'] + [self.md_rigList['smileLineRig']['left'][0]]},
		                   'uprCheekFollowRight':{'pointTargets':self.md_rigList['uprCheekRig']['right'] + [self.md_rigList['smileLineRig']['right'][0]]}}	
		self.create_curvesFromDict(md_curvesBuilds)
	    except Exception,error:raise StandardError,"[Build Curves!]{%s}"%(error)
	    
	    try:#Build plates ===================================================================================================
		md_plateBuilds = {'cheekLeft':{'mode':'cheekLoft','direction':'left','name':'cheek',
		                               'smileCrv':self.mi_smileLeftCrv},
		                  'cheekRight':{'mode':'cheekLoft','direction':'right','name':'cheek',
		                                'smileCrv':self.mi_smileRightCrv}}
		
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"[Plates!]{%s}"%(error)
	    
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
	    except Exception,error:raise StandardError,"[Attach!]{%s}"%(error)
	    
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
	    except Exception,error:raise StandardError,"!Skinning! | %s"%(error)	
	    
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
	    except Exception,error:raise StandardError,"[Connect!]{%s}"%(error)	
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
			except Exception,error:raise StandardError,"[Failed to attach!]{%s}"%(error)
			try:#>> Setup curve locs ------------------------------------------------------------------------------------------
			    mi_controlLoc = d_return['controlLoc']
			    mi_crvLoc = mi_controlLoc.doDuplicate(parentOnly=False)
			    mi_crvLoc.addAttr('cgmTypeModifier','crvAttach',lock=True)
			    mi_crvLoc.doName()
			    mi_crvLoc.parent = mi_go._i_rigNull#parent to rigNull
			    d_return['crvLoc'] = mi_crvLoc #Add the curve loc
			except Exception,error:raise StandardError,"Loc setup. | ]{%s}"%(error)
    
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
			except Exception,error:raise StandardError,"[Failed to attach!]{%s}"%(error)
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"Attach handle. obj: %s | error !]{%s}"(mObj.p_nameShort,error)	  
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
				
			    except Exception,error:raise StandardError,"Failed to attach to crv. | ]{%s}"%(error)
			    try:#>> Aim the offset group  ------------------------------------------------------------------------------------------
				if obj_idx != int_lastIndex:
				    str_upLoc = d_current['upLoc'].mNode
				    str_offsetGroup = d_current['offsetGroup'].mNode				    
				    ml_targets = [ml_rigJoints[obj_idx+1]]	
				    mc.aimConstraint([o.mNode for o in ml_targets],str_offsetGroup,
				                     maintainOffset = True, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = str_upLoc, worldUpType = 'object' )				    
			    except Exception,error:raise StandardError,"Loc setup. | ]{%s}"%(error)
	
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
		    except Exception,error:raise StandardError,"Failed to attach. | ]{%s}"%(error)
		    self.md_attachReturns[mObj] = d_return
		except Exception,error:
		    raise StandardError,"Attach rig joint loop. obj: %s | ]{%s}"%(mObj.p_nameShort,error)	
		
	    return True
		
	def _buildTemple_(self):
	    try:#>> Attach temple rig joints =======================================================================================
		mi_go = self._go#Rig Go instance link
		str_skullPlate = self.str_skullPlate
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
			except Exception,error:raise StandardError,"Failed to attach. | ]{%s}"%(error)
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"Attach rig joint loop. obj: %s | ]{%s}"%(mObj.p_nameShort,error)	    
		    
		for mObj in ml_handles:
		    try:
			try:#>> Attach ------------------------------------------------------------------------------------------
			    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
				                                    targetSurface = str_skullPlate,
				                                    createControlLoc = False,
				                                    createUpLoc = True,	
				                                    parentToFollowGroup = False,
				                                    orientation = mi_go._jointOrientation)
			except Exception,error:raise StandardError,"Failed to attach. | ]{%s}"%(error)
			self.md_attachReturns[mObj] = d_return
		    except Exception,error:
			raise StandardError,"Attach handle. obj: %s | ]{%s}"%(mObj.p_nameShort,error)	  
	    except Exception,error:
		raise StandardError,"Attach | %s"%(error)		
	    
	    try:#>> Setup handle =======================================================================================
		for i,mObj in enumerate(ml_handles):
		    try:#Connect the control loc to the center handle
			mi_controlLoc = self.md_attachReturns[ml_rigJoints[i]]['controlLoc']
			mc.pointConstraint(mObj.mNode,mi_controlLoc.mNode,maintainOffset = True)
			#cgmMeta.cgmAttr(mi_controlLoc,"translate").doConnectIn("%s.translate"%mi_centerHandle.mNode)
		    except Exception,error:raise StandardError,"[Control loc connec]{ %s}"%(error)			
				
	    except Exception,error:
		raise StandardError,"[Setup handle]{%s}"%(error)
	
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
	    except Exception,error:raise StandardError,"Parent follicles. | ]{%s}"%(error)
	    
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
					self.d_buffer = d_use
					#self.log_infoNestedDict('d_buffer')
				    else:d_use = d_buffer
				    
				    
				    _attachTo = d_use.get('attachTo')
				    if _attachTo == None:_attachTo = str_skullPlate
				    _parentTo = d_use.get('parentTo') or False
				    str_mode = d_use.get('mode') or 'rigAttach'
				    
				    self.log_info("Attach : '%s' | mObj: '%s' | mode: '%s' | _attachTo: '%s' | parentTo: '%s' "%(str_tag,mObj.p_nameShort,str_mode, _attachTo,_parentTo))
				    self.progressBar_set(status = ("Attaching : %s %s > '%s' | mode: %s"%(str_tag,str_key,mObj.p_nameShort,str_mode)),progress = ii, maxValue= int_len)
				    
				    if str_mode == 'rigAttach' and _attachTo:
					try:#Attach
					    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
						                                    targetSurface = _attachTo,
						                                    createControlLoc = True,
						                                    createUpLoc = True,
						                                    f_offset = f_offsetOfUpLoc,
						                                    orientation = mi_go._jointOrientation)
					except Exception,error:raise StandardError,"Rig mode attach. | %s"%(error)
					try:#>> Setup curve locs ------------------------------------------------------------------------------------------
					    mi_controlLoc = d_return['controlLoc']
					    mi_crvLoc = mi_controlLoc.doDuplicate(parentOnly=False)
					    mi_crvLoc.addAttr('cgmTypeModifier','followAttach',lock=True)
					    mi_crvLoc.doName()
					    mi_crvLoc.parent = mi_go._i_rigNull#parent to rigNull
					    d_return['followLoc'] = mi_crvLoc #Add the curve loc
					    self.md_attachReturns[mObj] = d_return										
					except Exception,error:raise StandardError,"Loc setup. | %s"%(error)
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
					except Exception,error:raise StandardError,"Handle attach. | ]{%s}"%(error)
					
				    elif str_mode == 'blendAttach' and _attachTo:
					try:#Blend attach ==================================================================================
					    try:#Query ---------------------------------------------------------------------------------------
						_target0 = d_use.get('target0') or self.md_rigList['stableJaw'][0]
						_d = {'handle':mObj,
						      'target0':_target0}
						self.d_buffer = _d
						_defaultValue = d_use.get('defaultValue') or None
						_suffix = d_use.get('followSuffix') or 'Deformation'
					    except Exception,error:raise StandardError,"!Query! | %s"%(error)	
						
					    try:#Build Tracklocs -----------------------------------------------------------------------------
						str_base = mObj.getAttr('cgmName') or 'NONAMETAG'
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
							
							'''
							try:
							    i_masterGroup = (cgmMeta.cgmObject(mi_loc.doGroup(True),setClass=True))
							    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
							    i_masterGroup.doName()
							    mi_loc.connectChildNode(i_masterGroup,'masterGroup','groupChild')			
							except Exception,error:raise StandardError,"!masterGroup! | %s"%(error)
							'''
							try:#Attach
							    d_return = surfUtils.attachObjToSurface(objToAttach = mi_loc,
								                                    targetSurface = _attachTo,
								                                    createControlLoc = True,
								                                    createUpLoc = False,	
								                                    attachControlLoc = d_sub.get('attachControlLoc'),
								                                    parentToFollowGroup = d_sub.get('parentToFollowGroup'),
								                                    orientation = mi_go._jointOrientation)
							    self.md_attachReturns[mi_loc] = d_return								
							except Exception,error:raise StandardError,"!Attach! | %s"%(error)
							
							self.log_info("'%s' created"%str_tmp)
							
							self.md_rigList[str_tmp] = [mi_loc]
							self.__dict__['mi_%s'%str_tmp] = mi_loc
							mObj.connectChildNode(mi_loc,'%sLoc'%str_t,'owner')
						    except Exception,error:raise StandardError,"!'%s' loc setup! | %s"%(str_t,error)				
					    except Exception,error:raise StandardError,"!Track locs! | %s"%(error)	
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
						except Exception,error:raise StandardError,"!Blend! | %s"%(error)
						
					    except Exception,error:
						#self.log_infoNestedDict('d_buffer')
						raise StandardError,"!Setup follow loc blend!|!]{%s}"%(error)
					except Exception,error:raise StandardError,"!Blend Attach Mode! | %s"%(error)	
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
					except Exception,error:raise StandardError,"Handle attach. | ]{%s}"%(error)	
				    elif str_mode == 'parentOnly':
					try:mObj.masterGroup.parent = _parentTo
					except Exception,error:raise StandardError,"parentTo. | ]{%s}"%(error)		    
					#self.log_info("%s parented!]{%s}"%(str_mode,mObj.p_nameShort))
				    else:
					raise NotImplementedError,"mode: %s "%str_mode
				except Exception,error:  raise StandardError,"attaching: %s | %s"%(mObj,error)				
		    except Exception,error:  raise StandardError,"'%s' | %s"%(str_tag,error)			    
	    except Exception,error:  raise StandardError,"attach_fromDict | %s"%(error)	
	    
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
				except Exception,error:raise StandardError,"!Index call(%s)!| %s"%(error)
				
				int_len = len(ml_buffer)
				for i,mObj in enumerate(ml_buffer):
				    str_mObj = mObj.p_nameShort
				    try:#Gather data ----------------------------------------------------------------------
					str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'rigToHandle'
					b_rewireFollicleOffset = d_buffer.get('rewireFollicleOffset') or d_build[str_tag].get('rewireFollicleOffset') or False 
					ml_driver = d_buffer.get('driver') or False
				    except Exception,error:raise StandardError,"[Data gather!]{%s}"%(error)
				    
				    self.log_info("Connecting : '%s' %s > '%s' | mode: '%s' | rewireFollicleOffset: %s"%(str_tag,str_key,str_mObj,str_mode,b_rewireFollicleOffset))
				    self.progressBar_set(status = ("Connecting : '%s' %s > '%s' | mode: '%s' | rewireFollicleOffset: %s"%(str_tag,str_key,str_mObj,str_mode,b_rewireFollicleOffset)),progress = i, maxValue = int_len)	
			    
				    if str_mode == 'rigToHandle':
					try:
					    try:#See if we have a handle return
						if ml_driver: ml_handles = ml_driver
						else:					
						    ml_handles = self.md_rigList[str_tag.replace('Rig','Handle')][str_key]
						if len(ml_handles) != len(ml_buffer):raise StandardError,"len of toConnect(%s) != len handles(%s)"%(len(ml_handles),len(ml_buffer))
						mi_handle = ml_handles[0]
					    except Exception,error:raise StandardError,"[Query!]{%s}"%(error)
	
					    try:#Connect the control loc to the center handle
						mi_controlLoc = self.md_attachReturns[mObj]['controlLoc']
						mc.pointConstraint(mi_handle.mNode,mi_controlLoc.mNode)
					    except Exception,error:raise StandardError,"[Control loc connect!]{%s"%(error)
					    
					    try:#Setup the offset to push handle rotation to the rig joint control
						#Create offsetgroup for the mid
						mi_offsetGroup = cgmMeta.cgmObject( mObj.doGroup(True),setClass=True)	 
						mi_offsetGroup.doStore('cgmName',mObj.mNode)
						mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
						mi_offsetGroup.doName()
						mObj.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
						
						cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
					    except Exception,error:raise StandardError,"[Offset group!]{%s}"%(error)
					    
					    try:#rewireFollicleOffset
						if b_rewireFollicleOffset:
						    mi_rewireHandle = d_buffer.get('rewireHandle') or d_build[str_tag].get('rewireHandle') or mi_handle
						    mi_follicleOffsetGroup = self.md_attachReturns[mObj]['offsetGroup']
						    for attr in mi_go._jointOrientation[0]:
							attributes.doConnectAttr ((mi_rewireHandle.mNode+'.t%s'%attr),(mi_follicleOffsetGroup.mNode+'.t%s'%attr))						    
						    
					    except Exception,error:raise StandardError,"[rewire Follicle Offset!]{%s"%(error)
					    
					except Exception,error:raise StandardError,"[%s!]{%s}"%(str_mode,error)					    
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
						
					    except Exception,error:raise StandardError,"[Failed to attach to crv.]{%s}"%(error)					    
					    
					    
					    '''
					    try:#>> Attach  loc to curve --------------------------------------------------------------------------------------
						mi_crvLoc = d_current['crvLoc']
						mi_controlLoc = d_current['controlLoc']
						crvUtils.attachObjToCurve(mi_crvLoc.mNode,mi_crv.mNode)
						mc.pointConstraint(mi_crvLoc.mNode,mi_controlLoc.mNode,maintainOffset = True)
						
					    except Exception,error:raise StandardError,"Failed to attach to crv. | ]{%s}"%(error)
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
					    except Exception,error:raise StandardError,"Loc setup. | ]{%s}"%(error)
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
					    except Exception,error:raise StandardError,"Failed to attach to crv. | ]{%s}"%(error)	
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
					    except Exception,error:raise StandardError,"Failed to attach to crv. | ]{%s}"%(error)	
					except Exception,error:raise StandardError,"[%s!]{%s}"%(str_mode,error)	
				    else:
					raise NotImplementedError,"not implemented : mode: %s"%str_mode
		    except Exception,error:  raise StandardError,"[%s]{%s}"%(str_tag,error)			    
	    except Exception,error:  raise StandardError,"[connect_fromDict]{%s}"%(error)	
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
				self.log_info("%s Skipping connect: %s"%(str_tag,str_side))
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
				    except Exception,error:raise StandardError,"!Index call(%s)!| %s"%(error)
				    
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
				    except Exception,error:raise StandardError,"!Vector query!| %s"%(error)
					
				except Exception,error:raise StandardError,"!Side data query! | %s"%(error)
				
	
				for idx,mObj in enumerate(ml_buffer):
				    str_mObj = mObj.p_nameShort
				    self.progressBar_set(status = ("Aiming : '%s' %s > '%s'"%(str_tag,str_side,str_mObj)),progress = idx, maxValue = int_len)	
				    try:#Gather data ----------------------------------------------------------------------
					try:d_current = self.md_attachReturns[mObj]
					except:raise Exception,"No attachReturn found"
					str_mode = d_buffer.get('mode') or d_build[str_tag].get('mode') or 'lipLineBlend'
					mi_upLoc = d_buffer.get('upLoc') or d_build[str_tag].get('upLoc') or d_current.get('upLoc')
					mi_masterGroup = mObj.masterGroup
					if not mi_upLoc:raise Exception,"No upLoc found!"
					_d['str_mode'] = str_mode
					_d['upLoc'] = mi_upLoc	
				    except Exception,error:raise StandardError,"[Gather Data]{%s}"%(error)
				    
				    try:#Aim Offset group ----------------------------------------------------------------------
					'''
					We need to first find our target which be a child to our aimOffset group. Sometimes that's the basic offset group
					'''
					try: mi_offsetTarget = d_current['offsetGroup']#See if we have an offset group
					except:
					    self.log_warning("No offset group in build dict. Checking object")
					    try:
						mi_offsetTarget = mObj.offsetGroup
					    except:
						self.log_warning("No offset group found. Using object")					
						mi_offsetTarget = mObj
			
					mi_aimOffsetGroup = cgmMeta.cgmObject(mi_offsetTarget.doGroup(True),setClass=True)
					mi_aimOffsetGroup.doStore('cgmName',mObj.mNode)
					mi_aimOffsetGroup.addAttr('cgmTypeModifier','AimOffset',lock=True)
					mi_aimOffsetGroup.doName()
					mObj.connectChildNode(mi_aimOffsetGroup,"aimOffsetGroup","childObject")					    
				    except Exception,error:raise StandardError,"[AimOffset group]{%s}"%(error)
				    
				    if str_mode == 'lipLineBlend':#This is pretty much just for the lip rig line for now
					try:
					    str_baseKey = d_buffer.get('baseKey') or d_build[str_tag].get('baseKey') or str_tag
					    if not str_baseKey:raise Exception,"No baseKey found!"					
					    _d['baseKey'] = str_baseKey		
					    
					    try:#Vectors
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
					    except Exception,error:raise StandardError,"!Vector query!| %s"%(error)					    
					    
					except Exception,error:raise StandardError,"[%s query]{%s}"%(str_mode,error)					
					    
					try:
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
					except Exception,error:raise StandardError,"!Get aim targets!| %s"%(error)
					
					self.log_info("Side: '%s' | idx: %s | Aiming :'%s' | in:'%s' | out:'%s' | up:'%s' "%(str_side,idx,str_mObj,mi_aimIn.p_nameShort,mi_aimOut.p_nameShort,mi_upLoc.p_nameShort))
					
					#up loc ------------------------------------------------------------------------
					'''
					mi_upLoc = mi_jnt.doLoc()
					mi_upLoc.parent = mi_jnt
					mi_upLoc.__setattr__("t%s"%self.str_orientation[1],10)
					mi_upLoc.parent = False
					'''
					try:
					    mi_locIn = mObj.doLoc()
					    mi_locIn.addAttr('cgmTypeModifier','aimIn',lock=True)
					    mi_locIn.doName()					    
					    
					    mi_locOut = mObj.doLoc()
					    mi_locOut.addAttr('cgmTypeModifier','aimOut',lock=True)
					    mi_locOut.doName()	
					    
					    mi_go.connect_toRigGutsVis([mi_locIn,mi_locOut],vis = 1, doShapes = True)#connect to guts vis switches
					    
					    mi_locIn.parent = mi_masterGroup
					    mi_locOut.parent = mi_masterGroup
					except Exception,error:raise StandardError,"[Aim loc creation!]{%s}"%(error)
					try:
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
					except Exception,error:raise StandardError,"[Constraints setup!]{%s}"%(error)
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
					except Exception,error:raise StandardError,"[Constraints setup!]{%s}"%(error)	
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
					except Exception,error:raise StandardError,"[singleVectorAim setup!]{%s}"%(error)						
					
					
				    else:
					raise NotImplementedError,"Mode not implemented : '%s'"%str_mode
		    except Exception,error:
			#try:self.log_infoNestedDict('d_buffer')
			#except:pass
			raise Exception,"[tag: '%s']{%s}"%(str_tag,error)			    
	    except Exception,error:  raise Exception,"[aim_fromDict]{%s}"%(error)
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
			except Exception,error:raise StandardError,"get data | %s"%(error)
			
			try:#Cluster
			    ret_cluster = mc.skinCluster([mObj.mNode for mObj in [__target] + __bindJoints], tsb = True, normalizeWeights = True, mi = __mi, dr = __dr)
			    i_cluster = cgmMeta.cgmNode(ret_cluster[0],setClass=True)
			    i_cluster.doStore('cgmName',__target.mNode)
			    i_cluster.doName()		
			except Exception,error:raise StandardError,"Cluster | %s"%(error)
			
		    except Exception,error:  raise StandardError,"%s | %s"%(str_tag,error)			    
	    except Exception,error:  raise StandardError,"skin_fromDict | %s"%(error)	
		    
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
				    
				except Exception,error:raise StandardError,"Rail curve build | %s"%(error)
				
				try:				    
				    ml_endProfileObjs = [ml_startRailObjs[-1],d_buffer['cheekJoints'][0], ml_endRailObjs[-1]]
				    #self.log_info("endProfileObjs: %s"%[mObj.p_nameShort for mObj in ml_endProfileObjs])
				    str_endProfileCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endProfileObjs], os = True)
				    str_startProfileCrv = mc.rebuildCurve (mi_smileCrv.mNode, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    str_endProfileCrvRebuilt = mc.rebuildCurve (str_endProfileCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]
				    
				except Exception,error:raise StandardError,"Profile curves build | %s"%(error)	
				
				try:
				    str_loft = mc.doubleProfileBirailSurface( str_startProfileCrv, str_endProfileCrvRebuilt,
				                                              str_startRailCrv, str_endRailCrv, 
				                                              blendFactor = .5,constructionHistory=0, object=1, polygon=0, transformMode=0)[0]
				except Exception,error:raise StandardError,"birail create | %s"%(error)	
				
				mc.delete([str_startProfileCrv,str_startRailCrv,str_endRailCrv,str_endProfileCrv])#Delete the rebuilt curves
			    except Exception,error:raise StandardError,"Reg plate loft | %s"%(error)	
			elif str_mode == 'liveSurface':
			    try:
				str_loft = mc.loft([mCrv.mNode for mCrv in d_buffer['crvs']],ch = True, uniform = True,degree = 3,ss = 3)[0]			    
			    except Exception,error:raise StandardError,"Live Surface loft | %s"%(error)	
			else:
			    try:#Reg curve loft
				l_crvsRebuilt = []
				for mi_crv in d_buffer['crvs']:#rebuild crvs
				    l_crvsRebuilt.append(self.returnRebuiltCurveString(mi_crv,4))
				
				str_loft = mc.loft(l_crvsRebuilt,uniform = True,degree = 3,ss = 3)[0]
				mc.delete(l_crvsRebuilt)#Delete the rebuilt curves
			    except Exception,error:raise StandardError,"Reg plate loft | %s"%(error)	
			
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
			except Exception,error:raise StandardError,"Tag/Name/Store | %s"%(error)	
			
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)	
		    #self.log_infoNestedDict('d_buffer')		    
	    except Exception,error:raise StandardError,"create_plateFromDict | %s"%(error)
	    
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
			    except Exception,error:raise StandardError,"Radial Loft | %s"%(error)
			else:
			    try:#Regular loft -----------------------------------------------------------------------
				ml_joints = d_buffer['joints']
				mi_crv = d_buffer['extrudeCrv']

				try:#Make our loft loc -----------------------------------------------------------------------
				    #f_dist = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_joints])*.05
				    d_buffer['dist'] = f_dist
				    
				    mi_loc = ml_joints[-1].doLoc()
				    mi_loc.doGroup()
				except Exception,error:raise StandardError,"loft loc | %s"%(error)
				
				try:#Cross section creation -----------------------------------------------------------------------
				    l_profileCrvPos = []
				    for dist in [0,f_dist]:
					mi_loc.__setattr__("t%s"%mi_go._jointOrientation[1],dist)
					l_profileCrvPos.append(mi_loc.getPosition())
					
				    str_profileCrv = mc.curve(d = 1,ep = l_profileCrvPos, os = True)
				except Exception,error:raise StandardError,"Cross section creation | %s"%(error)
				
				try:#Extrude crv -----------------------------------------------------------------------
				    str_extruded = mc.extrude([str_profileCrv,mi_crv.mNode],et = 1, sc = 1,ch = 1,useComponentPivot = 0,fixedPath=1)[0]
				    mi_obj = cgmMeta.cgmObject(str_extruded)
				    mc.delete(mi_loc.parent,str_profileCrv)
				except Exception,error:raise StandardError,"Extrude crv | %s"%(error)	
			    except Exception,error:raise StandardError,"Regular loft | %s"%(error)
			try:
			    self.__dict__['mi_%sRibbon'%(str_name)] = mi_obj
			    mi_obj.parent = mi_go._i_rigNull#parent to rigNull			    
			    mi_obj.addAttr('cgmName',str_name,lock=True)
			    mi_obj.addAttr('cgmTypeModifier','ribbon',lock=True)			    
			    try:mi_obj.addAttr('cgmDirection',d_buffer['direction'] ,lock=True)
			    except:pass
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sRibbon"%str_name,'module')			    
			except Exception,error:raise StandardError,"Naming | %s"%(error)
			#self.log_infoNestedDict('d_buffer')
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)
	    except Exception,error:raise StandardError,"create_ribbonsFromDict | %s"%(error)
	    
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
			    except Exception,error:raise StandardError,"Regular curve | %s"%(error)
			try:
			    self.__dict__['mi_%sCrv'%(str_name)] = mi_obj
			    mi_obj.addAttr('cgmName',str_name,lock=True)
			    try:mi_obj.addAttr('cgmDirection',d_buffer['direction'] ,lock=True)
			    except:pass
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sCrv"%str_name,'module')	
			    mi_obj.parent = mi_go._i_rigNull#parent to rigNull			    			    
			except Exception,error:raise StandardError,"Naming | %s"%(error)
			#self.log_infoNestedDict('d_buffer')
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)
	    except Exception,error:raise StandardError,"create_curvesFromDict | %s"%(error)
	    
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
