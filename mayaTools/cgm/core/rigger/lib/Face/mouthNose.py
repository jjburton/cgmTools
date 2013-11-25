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
    log.info(">>> %s.__bindSkeletonSetup__ >> "%self._strShortName + "-"*75)            
    try:
	if not self._cgmClass == 'JointFactory.go':
	    log.error("Not a JointFactory.go instance: '%s'"%self)
	    raise StandardError
	
    except Exception,error:
	log.error("mouthNose.__bindSkeletonSetup__>>bad self!")
	raise StandardError,error
    
    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self.rig_getSkinJoints() or []
    if not self._i_module.isSkeletonized():
	raise StandardError, "%s is not skeletonized yet."%self._strShortName
    try:
	self._i_module.rig_getReport()#report	
    except Exception,error:
	log.error("build_mouthNose>>__bindSkeletonSetup__ fail!")
	raise StandardError,error   
    
def build_rigSkeleton(*args, **kws):
    class fncWrap(modUtils.rigStep):
	def __init__(self,*args, **kws):
	    super(fncWrap, self).__init__(*args, **kws)
	    self._str_funcName = 'build_rigSkeleton(%s)'%self.d_kws['goInstance']._strShortName	
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self.gatherInfo},
	                        {'step':'Rig Joints','call':self.build_rigJoints},
	                        {'step':'Handle Joints','call':self.build_handleJoints},
	                        {'step':'Connections','call':self.build_connections}
	                        ]	
	    #=================================================================
	
	def gatherInfo(self):
	    mi_go = self._go#Rig Go instance link
	    self.mi_skullPlate = mi_go._mi_skullPlate
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._i_module.getMessage('helper'),noneValid=True)
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
	    
	    for k in d_jointListBuldTags.iterkeys():
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
	    for mJoint in ml_rightRigJoints:
		log.info(mJoint.p_nameShort)
		mJoint.__setattr__("r%s"%mi_go._jointOrientation[1],180)
		jntUtils.freezeJointOrientation(mJoint)
	    self.ml_rigJoints = ml_rigJoints#pass to wrapper
	    
	def build_handleJoints(self):
	    mi_go = self._go#Rig Go instance link	    
	    ml_moduleHandleJoints = []
	    for k_name in self.md_handleBuildInfo.keys():#For each name...
		d_nameBuffer = self.md_handleBuildInfo[k_name]
		for k_direction in ['left','right','center']:#for each direction....
		    try:
			d_buffer = d_nameBuffer.get(k_direction)
			l_tags = d_nameBuffer.get('tags') or False
			if l_tags:log.info(l_tags)
			l_tagsPosition = d_nameBuffer.get('tagsPosition') or False			
			str_mode = d_nameBuffer.get('mode') or 'regularMid'
			#if not d_buffer:raise StandardError,"%s %s fail"%(k_name,k_direction)
			if d_buffer:
			    log.info("Building '%s' | '%s' handle joints | mode: %s"%(k_name,k_direction,str_mode))
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
				log.info("Left >> u list : %s"%(str_bufferULeft))       
				f_maxULeft= float(str_bufferULeft.split(':')[-1].split(']')[0])	
				str_bufferURight = mc.ls("%s.u[*]"%mi_rightCrv.mNode)[0]
				log.info("Right >> u list : %s"%(str_bufferURight))       
				f_maxURight= float(str_bufferURight.split(':')[-1].split(']')[0])	
				
				pos_left = distance.returnWorldSpacePosition("%s.u[%s]"%(mi_leftCrv.mNode,f_maxULeft ))
				pos_right = distance.returnWorldSpacePosition("%s.u[%s]"%(mi_rightCrv.mNode,f_maxURight ))
				pos = distance.returnAveragePointPosition([pos_left,pos_right])
				log.info("pos >> %s"%pos)
				
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
				except Exception,error:raise StandardError,"mouthMove pos fail: %s"%error
				
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
				except Exception,error:raise StandardError,"Simple aim build fail: %s"%error
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
					except Exception,error:raise StandardError,"midAimBlend aim fail: %s"%error
					
				    jntUtils.metaFreezeJointOrientation(mi_jnt)				
				except Exception,error:raise StandardError,"mid fail: %s"%error
			    else:
				for i,mJnt in enumerate(self.l_build):
				    if mJnt == 'mid':
					mi_crv = d_buffer.get('crv')
					if not mi_crv:
					    raise StandardError,"Step: '%s' '%s' | failed to find use curve"%(k_name,k_direction)
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
					    except Exception,error:raise StandardError,"midClosestCurvePoint failed: %s"%error    
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
				#log.info("%s flipping"% mJoint.p_nameShort)
				mJoint.__setattr__("r%s"% mi_go._jointOrientation[1],180)
				jntUtils.freezeJointOrientation(mJoint)			
		    except Exception,error:raise StandardError,"%s | %s failed: %s"%(k_name,k_direction,error)    
				
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
	    mShapeCast.go(mi_go._i_module,['mouthNose'], storageInstance=mi_go)#This will store controls to a dict called    
	    
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
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._i_module.getMessage('helper'),noneValid=True)
	    if not self.mi_helper:raise StandardError,"No suitable helper found"
	    
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
		log.error("Following joints missing curves: ")
		for obj in l_missingCurves:
		    log.error(">"*5 + " %s"%obj)
		raise StandardError,"Some joints missing controlShape curves"
	    '''
	    log.info("#"*100)
	    for ii,ml_list in enumerate( [self.ml_rigJointsToSetup,self.ml_handleJoints] ):
		log.info("-"*100)		
		for i,mObj in enumerate(ml_list):
		    print mObj
	    log.info("#"*100)
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
		for i,mObj in enumerate(ml_list):
		    str_mirrorSide = False
		    try:
			log.info("%s On '%s'..."%(self._str_reportStart,mObj.p_nameShort))
			mObj.parent = mi_go._i_deformNull
			str_mirrorSide = mi_go.verify_mirrorSideArg(mObj.getAttr('cgmDirection'))#Get the mirror side
			_addForwardBack = "t%s"%mi_go._jointOrientation[0]
			if mObj.cgmName in ['tongueBase','tongueTip','jaw']:_addForwardBack = False

			#Register 
			try:
			    d_buffer = mControlFactory.registerControl(mObj, useShape = mObj.getMessage('controlShape'),addForwardBack = _addForwardBack,
				                                       mirrorSide = str_mirrorSide, mirrorAxis="translateZ,rotateX,rotateY",		                                           
				                                       makeAimable=False, typeModifier=l_strTypeModifiers[ii]) 	    
			except Exception,error:
			    log.error("mObj: %s"%mObj.p_nameShort)
			    log.error("useShape: %s"%mObj.getMessage('controlShape'))
			    log.error("mirrorSide: %s"%str_mirrorSide)		
			    log.error("forwardBack flag: %s"%_addForwardBack)						    
			    raise StandardError,"Register fail : %s"%error
			
			#Vis sub connect
			if ii == 0:
			    self.mPlug_result_moduleFaceSubDriver.doConnectOut("%s.visibility"%mObj.mNode)

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
		    try:mCtrl.addAttr('mirrorIndex', value = (int_start + i))		
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
	    self._str_funcName = 'build_rig(%s)'%self.d_kws['goInstance']._strShortName	
	    self.__dataBind__()
	    self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	                        #{'step':'Lip build','call':self._buildLips_},
	                        #{'step':'NoseBuild','call':self._buildNose_},
	                        {'step':'Cheek build','call':self._buildCheeks_},
	                        #{'step':'Lock N hide','call':self._lockNHide_},
	                        
	                        ]	
	    #=================================================================
	def _gatherInfo_(self):
	    mi_go = self._go#Rig Go instance link
	    
	    self.mi_helper = cgmMeta.validateObjArg(mi_go._i_module.getMessage('helper'),noneValid=True)
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
		              'jaw':{'check':ml_handleJoints},
		              'jawLine':{"left":{},"right":{},"center":{},'check':ml_rigJoints,'checkToggle':b_buildJawLine}}
		_l_buildDicts.append(d_jawBuild)
		    
		#>> uprCheek --------------------------------------------------------------------------------------------------
		b_buildUprCheek = True
		d_uprCheekBuild = {'uprCheekHandle':{"left":{},"right":{},'check':ml_handleJoints,'tag':'uprCheek'},
		                   'uprCheekRig':{"left":{},"right":{},'check':ml_rigJoints,'tag':'uprCheek','checkToggle':b_buildUprCheek}}
		
		_l_buildDicts.append(d_uprCheekBuild)
		
		#>> uprCheek --------------------------------------------------------------------------------------------------
		b_buildCheek = True
		d_cheekBuild = {#'cheekHandle':{"left":{},"right":{},'check':ml_handleJoints,'tag':'cheek'},
		                'cheekRig':{"left":{},"right":{},'check':ml_rigJoints,'tag':'cheek','checkToggle':b_buildCheek}}
		
		_l_buildDicts.append(d_cheekBuild)
			
		#>> tongue --------------------------------------------------------------------------------------------------
		b_buildTongue = True
		d_tongueBuild = {'tongueBase':{'check':ml_handleJoints,'checkToggle':b_buildTongue},
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
			if not ml_checkBase:raise StandardError,"No check key for %s"%k_tag
			else:
			    ml_checkSub = metaUtils.get_matchedListFromAttrDict(ml_checkBase, cgmName = str_tag)
			    #log.info("%s %s ml_checkSub: %s"%(self._str_reportStart,str_tag,ml_checkSub))
			#Check our directions for data --------------------------------------------------------
			_b_directionChecked = False
			for k_direction in _l_directions:
			    if d_tag.has_key(k_direction):
				_b_directionChecked = True
				buffer = metaUtils.get_matchedListFromAttrDict(ml_checkSub,cgmDirection = k_direction)
				if not buffer:raise StandardError,"Failed to find %s %s data"%(str_tag,k_direction)
				self.md_rigList[k_tag][k_direction] = buffer
				#log.info("%s - %s : %s"%(k_tag,k_direction,buffer))
			if not _b_directionChecked:
			    self.md_rigList[k_tag] = ml_checkSub
			    if self.md_rigList[k_tag]:_b_directionChecked = True
			    #log.info("%s : %s"%(k_tag,self.md_rigList[k_tag]))			    
			if not _b_directionChecked:
			    log.error("%s nothing checked"%(k_tag))
		    else:
			log.error("%s | Check toggle off"%(k_tag))
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
			self.log_infoNestedDict('d_buffer')
			
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
				    log.info("startRailObjs: %s"%[mObj.p_nameShort for mObj in ml_startRailObjs])
				    log.info("endRailObjs: %s"%[mObj.p_nameShort for mObj in ml_endRailObjs])
				    log.info("cheekJoints: %s"%[mObj.p_nameShort for mObj in d_buffer['cheekJoints']])
				    
				    str_startRailCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_startRailObjs], os = True)
				    str_endRailCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endRailObjs], os = True)
				    
				    #str_startRailCrv = mc.rebuildCurve (str_startRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    #str_endRailCrv = mc.rebuildCurve (str_endRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    str_startRailCrv = self.returnRebuiltCurveString(str_startRailCrv,5,1)
				    str_endRailCrv = self.returnRebuiltCurveString(str_endRailCrv,5,1)
				    
				except Exception,error:raise StandardError,"Rail curve build | %s"%(error)
				
				try:				    
				    ml_endProfileObjs = [ml_startRailObjs[-1],d_buffer['cheekJoints'][0], ml_endRailObjs[-1]]
				    log.info("endProfileObjs: %s"%[mObj.p_nameShort for mObj in ml_endProfileObjs])
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
		    self.log_infoNestedDict('d_buffer')		    
	    except Exception,error:raise StandardError,"Plate | %s"%(error)
	    
		
	def _buildNose_(self):
	    #>> Get some data =======================================================================================
	    """
	    Stuff to setup...
	    1) attach base to skull plate
	    2) What should
	    """	    
	    try:#Build Ribbons --------------------------------------------------------------------------------------
		md_ribbonBuilds = {'nostril':{'extrudeCrv':self.mi_noseBaseCastCrv,
		                              'joints':self.md_rigList['sneerHandle']['left'] + self.md_rigList['sneerHandle']['right']}}	
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"Ribbons | %s"%(error)
		
	    try:#Build plates --------------------------------------------------------------------------------------
		md_plateBuilds = {'nose':{'crvs':[self.mi_noseTopCastCrv,self.mi_noseMidCastCrv,self.mi_noseBaseCastCrv,self.mi_mouthTopCastCrv]}}
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"Plates | %s"%(error)

	    try:#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_nosePlate = self.mi_nosePlate.p_nameShort
		str_nostrilRibbon = self.mi_nostrilRibbon.p_nameShort	    
		try:str_noseMoveMasterGroup = self.md_rigList['noseMoveRig'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"NoseMove master group find fail | %s"%(error)
		#'nostrilHandle':{'attachTo':str_nosePlate,'mode':'handleAttach'}
		
		d_build = {'nostrilRig':{'attachTo':str_nosePlate},
		           'nostrilHandle':{'attachTo':str_nostrilRibbon,'mode':'handleAttach'},
		           'noseMoveHandle':{'mode':'handleAttach'},
		           'noseMoveRig':{},	               
		           'noseTipRig':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseTipHandle'][0]},
		           'noseTipHandle':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseMoveRig'][0]},
		           'noseUnderRig':{},
		           'noseUnderHandle':{'mode':'parentOnly','attachTo':None,'parentTo':str_noseMoveMasterGroup},
		           'noseTopRig':{},
		           'noseTopHandle':{'mode':'handleAttach'}
		           }	
		
		self.attach_fromDict(d_build)
	    except Exception,error:raise StandardError,"Attach | %s"%(error)
	    
	    
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
		
	    except Exception,error:raise StandardError,"Skin nose plate| error: %s"%(error)		
	    
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
		
	    except Exception,error:raise StandardError,"Skin nose plate| error: %s"%(error)	
	    
	    #>>> Connect build dict ==================================================================
	    d_build = {'noseMove':{},
	               'noseTop':{},
	               'noseUnder':{}}
	    
	    try:#>> Connect rig joints to handles ====================================================
		mi_go = self._go#Rig Go instance link
		
		self.progressBar_setMaxStepValue(len(d_build.keys()))
		for str_tag in d_build.iterkeys():
		    try:
			self.progressBar_iter(status = ("Connecting : '%s'"%str_tag))
			try:#Get ----------------------------------------------------
			    mi_handle = self.md_rigList[str_tag+'Handle'][0]
			    mi_rigJoint = self.md_rigList[str_tag+'Rig'][0]
			except Exception,error:raise StandardError,"Query | error: %s"%(error)			
			
			try:#Connect the control loc to the center handle
			    mi_controlLoc = self.md_attachReturns[mi_rigJoint]['controlLoc']
			    mc.pointConstraint(mi_handle.mNode,mi_controlLoc.mNode)
			except Exception,error:raise StandardError,"Control loc connect | error: %s"%(error)			
		    
			try:#Setup the offset to push handle rotation to the rig joint control
			    #Create offsetgroup for the mid
			    mi_offsetGroup = cgmMeta.cgmObject( mi_rigJoint.doGroup(True),setClass=True)	 
			    mi_offsetGroup.doStore('cgmName',mi_rigJoint.mNode)
			    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
			    mi_offsetGroup.doName()
			    mi_rigJoint.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
			    
			    cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
			except Exception,error:raise StandardError,"Offset group | error: %s"%(error)
			
		    except Exception,error:  raise StandardError,"%s | %s"%(str_tag,error)
		    
	    except Exception,error:  raise StandardError,"Connect rig>handle | %s"%(error)	
			
	    try:#>> Nose Move =======================================================================================
		self.progressBar_set(status = "Setting up nose move")
		
		mi_handle = self.md_rigList['noseMoveHandle'][0]
		mi_rigJoint = self.md_rigList['noseMoveRig'][0]
		
		try:#Connect the control loc to the center handle
		    mi_controlLoc = self.md_attachReturns[mi_rigJoint]['controlLoc']
		    mc.pointConstraint(mi_handle.mNode,mi_controlLoc.mNode)
		except Exception,error:raise StandardError,"Control loc connect | error: %s"%(error)	
		
		try:#Setup the offset to push handle rotation to the rig joint control
		    #Create offsetgroup for the mid
		    mi_offsetGroup = cgmMeta.cgmObject( mi_rigJoint.doGroup(True),setClass=True)	 
		    mi_offsetGroup.doStore('cgmName',mi_rigJoint.mNode)
		    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		    mi_offsetGroup.doName()
		    mi_rigJoint.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
		    
		    cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
		except Exception,error:raise StandardError,"Offset group | error: %s"%(error)
		
		'''
		try:#Create the brow up loc and parent it to the 
		    mi_browFrontUpLoc = mi_offsetGroup.doLoc()
		    mi_browFrontUpLoc.parent = mi_offsetGroup.parent
		    mi_browFrontUpLoc.tz = f_offsetOfUpLoc
		    self.mi_browFrontUpLoc = mi_browFrontUpLoc
		except Exception,error:raise StandardError,"Offset group | error: %s"%(error)
		'''
	    except Exception,error:
		raise StandardError,"Center Nose | %s"%(error)
	    
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
		    for k in d_logs.iterkeys():
			log.info("%s..."%k)
			for mObj in d_logs[k]:
			    log.info("--> %s "%mObj.p_nameShort)		
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
		    except Exception,error:raise StandardError,"upper driven curve : %s"%(error)  	    
		    
		    try:#Upper driver curve
			_str_uprDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_uprLipHandles],os =True)
			mi_uprDriverCrv = cgmMeta.cgmObject(_str_uprDriverCurve,setClass=True)
			mi_uprDriverCrv.doCopyNameTagsFromObject(mi_uprDrivenCrv.mNode,ignore=['cgmTypeModifier'])
			mi_uprDriverCrv.addAttr('cgmTypeModifier','driver',lock=True)
			mi_uprDriverCrv.doName()
			ml_curves.append(mi_uprDriverCrv)	    
		    except Exception,error:raise StandardError,"upper driver curve : %s"%(error)  	    
		    
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
		    except Exception,error:raise StandardError,"upper driven curve : %s"%(error)  	    
		    
		    try:#Lwr driver curve
			_str_lwrDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_lwrLipHandles],os =True)
			mi_lwrDriverCrv = cgmMeta.cgmObject(_str_lwrDriverCurve,setClass=True)
			mi_lwrDriverCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
			mi_lwrDriverCrv.addAttr('cgmName','lwrLip',lock=True)	    
			mi_lwrDriverCrv.doName()
			ml_curves.append(mi_lwrDriverCrv)	    	    	    
		    except Exception,error:raise StandardError,"upper driver curve : %s"%(error)  	    
		    
		    try:#SmartLipSeal curve
			_str_smartLipSealCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_lwrLipHandles],os =True)
			mi_smartLipSealCrv = cgmMeta.cgmObject(_str_smartLipSealCurve,setClass=True)
			mi_smartLipSealCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
			mi_smartLipSealCrv.addAttr('cgmName','smartLipSeal',lock=True)	    
			mi_smartLipSealCrv.doName()
			ml_curves.append(mi_smartLipSealCrv)	    	    	    
		    except Exception,error:raise StandardError,"smartLipSeal curve : %s"%(error)  	
		    '''
		    for mi_crv in ml_curves:#Parent to rig null
			mi_crv.parent = mi_go._i_rigNull
		    self.ml_toVisConnect.extend(ml_curves)
		    '''
		except Exception,error:raise StandardError,"Curve creation | %s"%(error)   
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
			    except Exception,error:raise StandardError,"loc creation : %s"%(error)  	    
			    #> Aim constraint
			    #mi_root = mi_obj.root
			    #mi_root.parent = self._i_constrainNull
			    #try:mc.aimConstraint(mi_loc.mNode,mi_root.mNode,maintainOffset = False, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
			    #except Exception,error:raise StandardError,"aim constraint : %s"%(error)  	    
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
		    except Exception,error:raise StandardError,">> wire deformer : %s"%(error)  	    
		    
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
			    log.info(" %s | crv : %s | joints: %s"%(k,str_crv,l_joints))
			    try:
				mi_skinNode = cgmMeta.cgmNode(mc.skinCluster ([mi_obj.mNode for mi_obj in d_crv['ml_joints']],
				                                              d_crv['mi_crv'].mNode,
				                                              tsb=True,
				                                              maximumInfluences = 3,
				                                              normalizeWeights = 1,dropoffRate=2.5)[0])
			    except Exception,error:raise StandardError,"skinCluster : %s"%(error)  	    
			    d_crv['mi_skinNode'] = mi_skinNode
		    except Exception,error:raise StandardError,"skinning driver : %s"%(error)  	    
		    
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
		    except Exception,error:raise StandardError,"smartLipSeal bsNode : %s"%(error)  	
		    
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
		    except Exception,error:raise StandardError,"lipSeal target wires : %s"%(error)  	
		    
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
		    except Exception,error:raise StandardError,"lipSeal setup : %s"%(error)  	
	    
		except Exception,error:
		    raise StandardError,"lip setup | %s"%(error)   	        
	    except Exception,error:
		raise StandardError,"Smart Seal setup fail! | error: %s"%(error)   		    
	    
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
		    mi_dup.parent = False
		    
		    ml_curves.append(mi_dup)
		    self.__dict__["mi_%sCrv"%str_k] = mi_dup
		'''
		for mi_crv in ml_curves:#Parent to rig null
		    mi_crv.parent = mi_go._i_rigNull
		self.ml_toVisConnect.extend(ml_curves)
		'''
	    except Exception,error:raise StandardError,"Curve creation | %s"%(error)   	    
	    
	    try:#Build Ribbons --------------------------------------------------------------------------------------
		md_ribbonBuilds = {'uprLip':{'extrudeCrv':self.mi_lipUprCrv,
		                              'joints':self.md_rigList['lipCornerHandle']['left'] + self.md_rigList['lipCornerHandle']['right']},
		                   'lwrLip':{'extrudeCrv':self.mi_lipLwrCrv,
		                             'joints':self.md_rigList['lipCornerHandle']['left'] + self.md_rigList['lipCornerHandle']['right']}}
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"Ribbons | %s"%(error)
	    
	    try:#Build plates ====================================================================================
		md_plateBuilds = {'uprLip':{'crvs':[self.mi_mouthTopCastCrv,self.mi_lipOverTraceCrv,self.mi_lipUprCrv]},
		                  'uprLipFollow':{'crvs':[self.mi_mouthTopTraceCrv,mi_uprDrivenCrv],'mode':'liveSurface'},
		                  'lwrLip':{'crvs':[self.mi_lipLwrCrv,self.mi_lipUnderTraceCrv,self.mi_mouthLowCastCrv]},
		                  'lwrLipFollow':{'crvs':[mi_lwrDrivenCrv,self.mi_mouthBaseTraceCrv],'mode':'liveSurface'}}
		
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"Plates | %s"%(error)
	    
	    try:#Attach stuff to surfaces ====================================================================================
		#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_skullPlate = self.str_skullPlate
		
		str_uprLipPlate = self.mi_uprLipPlate.p_nameShort
		str_uprLipFollowPlate = self.mi_uprLipFollowPlate.p_nameShort		
		str_uprLipRibbon = self.mi_uprLipRibbon.p_nameShort
		
		str_lwrLipPlate = self.mi_lwrLipPlate.p_nameShort
		str_lwrLipFollowPlate = self.mi_lwrLipFollowPlate.p_nameShort				
		str_lwrLipRibbon = self.mi_lwrLipRibbon.p_nameShort
		
		try:#Make a mouthMove track loc
		    mi_mouthMoveTrackLoc = self.md_rigList['mouthMove'][0].doLoc()
		    i_masterGroup = (cgmMeta.cgmObject(mi_mouthMoveTrackLoc.doGroup(True),setClass=True))
		    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
		    i_masterGroup.doName()
		    mi_mouthMoveTrackLoc.connectChildNode(i_masterGroup,'masterGroup','groupChild')
		    self.md_rigList['mouthMoveTrackLoc'] = [mi_mouthMoveTrackLoc]
		except Exception,error:raise StandardError,"MouthMove master group find fail | %s"%(error)
		    		
		try:str_mouthMoveTrackerMasterGroup = self.md_rigList['mouthMoveTrackLoc'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"MouthMoveTrack master group find fail | %s"%(error)
		
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
		d_build = {'mouthMove':{'mode':'handleAttach'},
		           'mouthMoveTrackLoc':{},
		           'lipUprRig':{'mode':'handleAttach','attachTo':str_uprLipFollowPlate},
		           'lipOverRig':{'mode':'handleAttach','attachTo':str_uprLipPlate},		           
		           'lipUprHandle':{'mode':'handleAttach', 'attachTo':str_uprLipRibbon,
		                           'center':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode}},
		           'lipCornerRig':{},#reg, will be driven by...
		           'lipCornerHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode},
		           'lipLwrRig':{'mode':'handleAttach','attachTo':str_lwrLipFollowPlate},
		           'lipUnderRig':{'mode':'handleAttach','attachTo':str_lwrLipPlate},		           
		           'lipLwrHandle':{'mode':'handleAttach', 'attachTo':str_lwrLipRibbon,
		                           'center':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode}},
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
	    except Exception,error:raise StandardError,"Attach | %s"%(error)
	    
	    #self.log_infoNestedDict('md_attachReturns')

	    try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		d_build = {'uprLipTop':{'target':self.mi_mouthTopTraceCrv,
		                        'bindJoints':[self.md_rigList['smileLineRig']['left'][0],
		                                      self.md_rigList['noseUnderRig'][0],
		                                      self.md_rigList['smileLineRig']['right'][0]]},
		           'uprLipPlate':{'target':self.mi_uprLipPlate,
		                          'bindJoints':ml_uprLipRigJoints + self.md_rigList['noseUnderRig']},		           

		          'uprLipRibbon':{'target':self.mi_uprLipRibbon,
		                           'bindJoints':[self.md_rigList['lipCornerRig']['left'][0],
		                                         self.md_rigList['lipUprHandle']['center'][0],
		                                         self.md_rigList['lipCornerRig']['right'][0]]},
		          'lwrLipRibbon':{'target':self.mi_lwrLipRibbon,
		                           'bindJoints':[self.md_rigList['lipCornerRig']['left'][0],
		                                         self.md_rigList['lipLwrHandle']['center'][0],
		                                         self.md_rigList['lipCornerRig']['right'][0]]},		          
		          'lwrLipPlate':{'target':self.mi_lwrLipPlate,
		                         'bindJoints':ml_lwrLipRigJoints + self.md_rigList['lipCornerRig']['left'] + self.md_rigList['lipCornerRig']['right'] + [self.md_rigList['smileLineRig']['left'][-1],
		                                       self.md_rigList['chin'][0],		                                       
		                                       self.md_rigList['smileLineRig']['right'][-1]]},		           
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
		d_build = {'lipCornerRig':{},
		           'mouthMoveTrackLoc':{'driver':self.md_rigList['mouthMove']}}
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"!Connect! | %s"%(error)	
	    return
	
	def _buildCheeks_(self):
	    mi_go = self._go#Rig Go instance link
	    try:#Build Curves --------------------------------------------------------------------------------------
		md_curvesBuilds = {'cheekFollowLeft':{'pointTargets':self.md_rigList['uprCheekRig']['left'] + [self.md_rigList['smileLineRig']['left'][0]]},
		                   'cheekFollowRight':{'pointTargets':self.md_rigList['uprCheekRig']['right'] + [self.md_rigList['smileLineRig']['right'][0]]}}	
		self.create_curvesFromDict(md_curvesBuilds)
	    except Exception,error:raise StandardError,"Curves | %s"%(error)
	    
	
	    try:#Build Ribbons --------------------------------------------------------------------------------------
		md_ribbonBuilds = {'smileLeft':{'extrudeCrv':self.mi_smileLeftCrv,'mode':'radialLoft','direction':'left',
		                                'aimObj':self.md_rigList['mouthMove'][0]},
		                   'smileRight':{'extrudeCrv':self.mi_smileRightCrv,'mode':'radialLoft','direction':'right',
		                                 'aimObj':self.md_rigList['mouthMove'][0]}}	
		self.create_ribbonsFromDict(md_ribbonBuilds)
	    except Exception,error:raise StandardError,"Ribbons | %s"%(error)
	    
	    
	    try:#Build plates ====================================================================================
		md_plateBuilds = {'cheekLeft':{'mode':'cheekLoft','direction':'left','name':'cheek',
		                               'smileCrv':self.mi_smileLeftCrv},
		                  'cheekRight':{'mode':'cheekLoft','direction':'right','name':'cheek',
		                                'smileCrv':self.mi_smileRightCrv}}
		
		self.create_plateFromDict(md_plateBuilds)
	    except Exception,error:raise StandardError,"Plates | %s"%(error)
	    
	    return
	    try:#Attach stuff to surfaces ====================================================================================
		#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
		str_skullPlate = self.str_skullPlate
		
		str_cheekLeftPlate = self.mi_cheekLeftPlate.p_nameShort
		str_cheekRightPlate = self.mi_cheekRightPlate.p_nameShort

		
		try:#Make a mouthMove track loc
		    mi_mouthMoveTrackLoc = self.md_rigList['mouthMove'][0].doLoc()
		    i_masterGroup = (cgmMeta.cgmObject(mi_mouthMoveTrackLoc.doGroup(True),setClass=True))
		    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
		    i_masterGroup.doName()
		    mi_mouthMoveTrackLoc.connectChildNode(i_masterGroup,'masterGroup','groupChild')
		    self.md_rigList['mouthMoveTrackLoc'] = [mi_mouthMoveTrackLoc]
		except Exception,error:raise StandardError,"MouthMove master group find fail | %s"%(error)
		    		
		try:str_mouthMoveTrackerMasterGroup = self.md_rigList['mouthMoveTrackLoc'][0].masterGroup.p_nameShort
		except Exception,error:raise StandardError,"MouthMoveTrack master group find fail | %s"%(error)
		
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
		d_build = {'mouthMove':{'mode':'handleAttach'},
		           'mouthMoveTrackLoc':{},
		           'lipUprRig':{'mode':'handleAttach','attachTo':str_uprLipFollowPlate},
		           'lipOverRig':{'mode':'handleAttach','attachTo':str_uprLipPlate},		           
		           'lipUprHandle':{'mode':'handleAttach', 'attachTo':str_uprLipRibbon,
		                           'center':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode}},
		           'lipCornerRig':{},#reg, will be driven by...
		           'lipCornerHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode},
		           'lipLwrRig':{'mode':'handleAttach','attachTo':str_lwrLipFollowPlate},
		           'lipUnderRig':{'mode':'handleAttach','attachTo':str_lwrLipPlate},		           
		           'lipLwrHandle':{'mode':'handleAttach', 'attachTo':str_lwrLipRibbon,
		                           'center':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode}},
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
	    except Exception,error:raise StandardError,"Attach | %s"%(error)
	    
	    #self.log_infoNestedDict('md_attachReturns')

	    try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		d_build = {'uprLipTop':{'target':self.mi_mouthTopTraceCrv,
		                        'bindJoints':[self.md_rigList['smileLineRig']['left'][0],
		                                      self.md_rigList['noseUnderRig'][0],
		                                      self.md_rigList['smileLineRig']['right'][0]]},
		           'uprLipPlate':{'target':self.mi_uprLipPlate,
		                          'bindJoints':ml_uprLipRigJoints + self.md_rigList['noseUnderRig']},		           

		          'uprLipRibbon':{'target':self.mi_uprLipRibbon,
		                           'bindJoints':[self.md_rigList['lipCornerRig']['left'][0],
		                                         self.md_rigList['lipUprHandle']['center'][0],
		                                         self.md_rigList['lipCornerRig']['right'][0]]},
		          'lwrLipRibbon':{'target':self.mi_lwrLipRibbon,
		                           'bindJoints':[self.md_rigList['lipCornerRig']['left'][0],
		                                         self.md_rigList['lipLwrHandle']['center'][0],
		                                         self.md_rigList['lipCornerRig']['right'][0]]},		          
		          'lwrLipPlate':{'target':self.mi_lwrLipPlate,
		                         'bindJoints':ml_lwrLipRigJoints + self.md_rigList['lipCornerRig']['left'] + self.md_rigList['lipCornerRig']['right'] + [self.md_rigList['smileLineRig']['left'][-1],
		                                       self.md_rigList['chin'][0],		                                       
		                                       self.md_rigList['smileLineRig']['right'][-1]]},		           
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
		d_build = {'lipCornerRig':{},
		           'mouthMoveTrackLoc':{'driver':self.md_rigList['mouthMove']}}
		self.connect_fromDict(d_build)
	    except Exception,error:raise StandardError,"!Connect! | %s"%(error)	
	    return
	
	    pass
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
		    mi_crv = cgmMeta.cgmObject(str_crv,setClass=True)
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
	    #Lock and hide all 
	    for mHandle in self.ml_handlesJoints:
		cgmMeta.cgmAttr(mHandle,'scale',lock = True, hidden = True)
		cgmMeta.cgmAttr(mHandle,'v',lock = True, hidden = True)		
		mHandle._setControlGroupLocks()	
		
	    for mJoint in self.ml_rigJoints:
		mJoint._setControlGroupLocks()	
		cgmMeta.cgmAttr(mJoint,'v',lock = True, hidden = True)		

	    mi_go = self._go#Rig Go instance link
	    try:#parent folicles to rignull
		for k in self.md_attachReturns.keys():# we wanna parent 
		    d_buffer = self.md_attachReturns[k]
		    try:d_buffer['follicleFollow'].parent = mi_go._i_rigNull
		    except:pass
		    try:d_buffer['follicleAttach'].parent = mi_go._i_rigNull
		    except:pass				
	    except Exception,error:raise StandardError,"Parent follicles. | error : %s"%(error)
	    
	def returnRebuiltCurveString(self,crv, int_spans = 5, rpo = 0):
	    try:crv.mNode
	    except:crv = cgmMeta.cgmObject(crv)
	    
	    return mc.rebuildCurve (crv.mNode, ch=0, rpo=rpo, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=int_spans, d=3, tol=0.001)[0]		

	def attach_fromDict(self,d_build):
	    try:#>> Attach  =======================================================================================
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
				    #log.info("%s:%s:%s"%(str_tag,str_side,bfr_side))
				    #ml_buffer.extend(bfr_side)
				    md_buffer[str_side] = bfr_side
			else:
			    #ml_buffer = buffer
			    md_buffer['reg'] = buffer
			
			for str_key in md_buffer.iterkeys():
			    ml_buffer = md_buffer[str_key]
			    self.progressBar_setMaxStepValue(len(ml_buffer))
			    
			    if d_build[str_tag].get(str_key):#if we have special instructions for a direction key...
				d_buffer = d_build[str_tag][str_key]
			    else:
				d_buffer = d_build[str_tag]
				
			    for mObj in ml_buffer:
				self.progressBar_iter(status = ("Attaching : %s %s > '%s'"%(str_tag,str_key,mObj.p_nameShort)))
				try:
				    _attachTo = d_buffer.get('attachTo')
				    if _attachTo == None:_attachTo = str_skullPlate
				    _parentTo = d_buffer.get('parentTo') or False
				    str_mode = d_buffer.get('mode') or 'rigAttach'				
				    log.info("%s | mObj: %s | mode: %s | _attachTo: %s | parentTo: %s "%(str_tag,mObj.p_nameShort,str_mode, _attachTo,_parentTo))
				    
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
					    mi_crvLoc.addAttr('cgmTypeModifier','crvAttach',lock=True)
					    mi_crvLoc.doName()
					    mi_crvLoc.parent = mi_go._i_rigNull#parent to rigNull
					    d_return['crvLoc'] = mi_crvLoc #Add the curve loc
					    self.md_attachReturns[mObj] = d_return										
					except Exception,error:raise StandardError,"Loc setup. | %s"%(error)
					#log.info("%s mode attached : %s"%(str_mode,mObj.p_nameShort))
				    elif str_mode == 'handleAttach' and _attachTo:
					try:
					    d_return = surfUtils.attachObjToSurface(objToAttach = mObj.getMessage('masterGroup')[0],
						                                    targetSurface = _attachTo,
						                                    createControlLoc = False,
						                                    createUpLoc = True,	
						                                    parentToFollowGroup = False,
						                                    orientation = mi_go._jointOrientation)
					    self.md_attachReturns[mObj] = d_return					
					except Exception,error:raise StandardError,"Handle attach. | error : %s"%(error)		    
					#log.info("%s mode attached : %s"%(str_mode,mObj.p_nameShort))				
				    
				    elif str_mode == 'parentOnly':
					try:
					    mObj.masterGroup.parent = _parentTo
					except Exception,error:raise StandardError,"parentTo. | error : %s"%(error)		    
					#log.info("%s parented : %s"%(str_mode,mObj.p_nameShort))
				    else:
					raise NotImplementedError,"mode: %s "%str_mode
				except Exception,error:  raise StandardError,"%s | %s"%(mObj,error)				
		    except Exception,error:  raise StandardError,"%s | %s"%(str_tag,error)			    
	    except Exception,error:  raise StandardError,"attach_fromDict | %s"%(error)	
	    
	def connect_fromDict(self,d_build):
	    '''
	    handler for connecting stuff to handles,curves,surfaces or whatever
	    Modes:
	    rigToHandle -- given a nameRig kw, it looks through the data sets to find the handle and connect. One to one connection type
	    
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
		
			for str_key in md_buffer.iterkeys():
			    
			    if d_build[str_tag].get(str_key):#if we have special instructions for a direction key...
				d_buffer = d_build[str_tag][str_key]
			    else:
				d_buffer = d_build[str_tag]	
			    ml_buffer = md_buffer[str_key]
			
			    self.progressBar_setMaxStepValue(len(ml_buffer))
			    for i,mObj in enumerate(ml_buffer):
				str_mObj = mObj.p_nameShort
				self.progressBar_iter(status = ("Connecting : '%s' %s > '%s'"%(str_tag,str_key,str_mObj)))	
				
				try:#Gather data ----------------------------------------------------------------------
				    #_attachTo = d_buffer.get('attachTo')
				    #if _attachTo == None:_attachTo = str_skullPlate
				    #_parentTo = d_buffer.get('parentTo') or False
				    str_mode = d_buffer.get('mode') or 'rigToHandle'		
				    ml_driver = d_buffer.get('driver') or False
				    log.info("%s | mObj: %s | mode: %s | "%(str_tag,str_mObj,str_mode))
				except Exception,error:raise StandardError,"!Data gather!| %s"%(error)
			
				if str_mode == 'rigToHandle':
				    try:#See if we have a handle return
					if ml_driver: ml_handles = ml_driver
					else:					
					    ml_handles = self.md_rigList[str_tag.replace('Rig','Handle')][str_key]
					if len(ml_handles) != len(ml_buffer):raise StandardError,"len of toConnect(%s) != len handles(%s)"%(len(ml_handles),len(ml_buffer))
					mi_handle = ml_handles[0]
				    except Exception,error:raise StandardError,"Query | error: %s"%(error)

				    try:#Connect the control loc to the center handle
					mi_controlLoc = self.md_attachReturns[mObj]['controlLoc']
					mc.pointConstraint(mi_handle.mNode,mi_controlLoc.mNode)
				    except Exception,error:raise StandardError,"Control loc connect | error: %s"%(error)
				    
				    try:#Setup the offset to push handle rotation to the rig joint control
					#Create offsetgroup for the mid
					mi_offsetGroup = cgmMeta.cgmObject( mObj.doGroup(True),setClass=True)	 
					mi_offsetGroup.doStore('cgmName',mObj.mNode)
					mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
					mi_offsetGroup.doName()
					mObj.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
					
					cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
				    except Exception,error:raise StandardError,"Offset group | error: %s"%(error)
				else:
				    raise NotImplementedError,"mode: %s"%str_mode
		    except Exception,error:  raise StandardError,"%s | %s"%(str_tag,error)			    
	    except Exception,error:  raise StandardError,"connect_fromDict | %s"%(error)	
	    
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
			    
			except Exception,error:raise StandardError,"get data | %s"%(error)
			
			try:#Cluster
			    ret_cluster = mc.skinCluster([mObj.mNode for mObj in [__target] + __bindJoints], tsb = True, normalizeWeights = True, mi = 4, dr = 5)
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
				    #log.info("startRailObjs: %s"%[mObj.p_nameShort for mObj in ml_startRailObjs])
				    #log.info("endRailObjs: %s"%[mObj.p_nameShort for mObj in ml_endRailObjs])
				    #log.info("cheekJoints: %s"%[mObj.p_nameShort for mObj in d_buffer['cheekJoints']])
				    
				    str_startRailCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_startRailObjs], os = True)
				    str_endRailCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endRailObjs], os = True)
				    
				    #str_startRailCrv = mc.rebuildCurve (str_startRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    #str_endRailCrv = mc.rebuildCurve (str_endRailCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
				    str_startRailCrv = self.returnRebuiltCurveString(str_startRailCrv,5,1)
				    str_endRailCrv = self.returnRebuiltCurveString(str_endRailCrv,5,1)
				    
				except Exception,error:raise StandardError,"Rail curve build | %s"%(error)
				
				try:				    
				    ml_endProfileObjs = [ml_startRailObjs[-1],d_buffer['cheekJoints'][0], ml_endRailObjs[-1]]
				    #log.info("endProfileObjs: %s"%[mObj.p_nameShort for mObj in ml_endProfileObjs])
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
			    self.__dict__['mi_%sPlate'%(str_name)] = mi_obj
			    mi_obj.addAttr('cgmName',d_buffer.get('name') or str_name,lock=True)
			    try:mi_obj.addAttr('cgmDirection',str_direction ,lock=True)
			    except:pass
			    mi_obj.addAttr('cgmTypeModifier','plate',lock=True)					    
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sPlate"%str_name,'module')
			except Exception,error:raise StandardError,"Tag/Name/Store | %s"%(error)	
			
		    except Exception,error:raise StandardError,"%s | %s"%(str_name,error)	
		    self.log_infoNestedDict('d_buffer')		    
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
			    mi_obj.addAttr('cgmName',str_name,lock=True)
			    mi_obj.addAttr('cgmTypeModifier','ribbon',lock=True)			    
			    try:mi_obj.addAttr('cgmDirection',d_buffer['direction'] ,lock=True)
			    except:pass
			    mi_obj.doName()
			    mi_go._i_rigNull.connectChildNode(mi_obj,"%sRibbon"%str_name,'module')			    
			except Exception,error:raise StandardError,"Naming | %s"%(error)
			self.log_infoNestedDict('d_buffer')
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
			except Exception,error:raise StandardError,"Naming | %s"%(error)
			self.log_infoNestedDict('d_buffer')
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
