"""
------------------------------------------
cgm.core.rigger: Face.mouthNose
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

mouthNose rig builder
=================================s===============================
"""
__version__ = 'faceAlpha3.12182015'

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
from cgm.core.rigger.lib.Face import faceMod_Utils as faceUtils
reload(faceUtils)
reload(mControlFactory)
from cgm.core.lib import nameTools
from cgm.core.lib import curve_Utils as crvUtils
from cgm.core.lib import rayCaster as rayCast
from cgm.core.lib import surface_Utils as surfUtils
reload(surfUtils)
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
                                #{'step':'Special Joints','call':self.build_specialJoints},	                        
                                {'step':'Handle Joints','call':self.build_handleJoints},
                                {'step':'Connections','call':self.build_connections}
                                ]	
            #=================================================================

        def gatherInfo(self):
            mi_go = self._go#Rig Go instance link
	    
            '''try:#>> Deformation Plates =======================================================================================
                self.mi_skullPlate = cgmMeta.cgmObject('jawPlate')    
                #self.mi_skullPlate = mi_go._mi_skullPlate
                self.str_skullPlate = self.mi_skullPlate.p_nameShort

                self.mi_uprTeethPlate = cgmMeta.cgmObject('uprTeethPlate')    
                self.mi_lwrTeethPlate = cgmMeta.cgmObject('lwrTeethPlate')    
                self.mi_browPlate = cgmMeta.cgmObject('browPlate')    

            except Exception,error:raise Exception,"[Deformation Plates] | error: {0}".format(error)'''		    

            self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise StandardError,"No suitable helper found"

            for attr in self.mi_helper.getAttrs(userDefined = True):#Get allof our Helpers
                if "Helper" in attr:
                    try:self.__dict__["mi_%s"%attr.replace('Helper','Crv')] = cgmMeta.validateObjArg(self.mi_helper.getMessage(attr),noneValid=False)
                    except Exception,error:raise Exception, " Failed to find '%s' | %s"%(attr,error)


            #>> Find our joint lists ===================================================================
            self.md_jointList = {}
            self.ml_handleJoints = []
            #list of tags we're gonna check to build our joint lists indexed to the k
            d_jointListBuldTags = {#"smileLeft":'left_smileLineJoint',
                                   #"smileRight":'right_smileLineJoint',
                                   ##"uprCheekLeft":'left_uprCheekJoint',
                                   #"uprCheekRight":'right_uprCheekJoint',
                                   #"cheekLeft":'left_cheekJoint',
                                   #"cheekRight":'right_cheekJoint',
                                   #"uprLipLeft":'left_lipUprJoint',
                                   #"uprLipRight":'right_lipUprJoint',	    
                                   #"lwrLipLeft":'left_lipLwrJoint',
                                   #"lwrLipRight":'right_lipLwrJoint',	    
                                   #"uprLipCenter": 'center_lipUprJoint',
                                   #"lwrLipCenter":'center_lipLwrJoint',	                         
                                   #"cornerLipLeft":'left_lipCornerJoint',
                                   #"cornerLipRight":'right_lipCornerJoint',
                                   #"noseBase":'noseBaseJoint',
                                   "jaw":'jawJoint',
	                           "teethUpr":'teethUprJoint',
	                           "teethLwr":'teethLwrJoint',
                                   #"jawLineLeft":'left_jawLineJoint',
                                   #"jawLineRight":'right_jawLineJoint',
                                   #"centerJaw":'center_jawLineJoint',	                         
                                   #"noseTop":'noseTopJoint',
                                   #"noseTip":'noseTipJoint',
                                   #"noseUnder":'noseUnderJoint',	                         
                                   #"nostrilLeft":'left_nostrilJoint',
                                   #"nostrilRight":'right_nostrilJoint',	                         
                                   "tongue":'tongueJoint'}

            int_lenMax = len(d_jointListBuldTags.keys())
            for i,k in enumerate(d_jointListBuldTags.iterkeys()):
                self.progressBar_set(status = "Gathering joint data: %s... "%(k), progress = i, maxValue = int_lenMax)		    				    		    		    		
                try:
		    self.md_jointList[k] = cgmMeta.validateObjListArg(mi_go._i_rigNull.msgList_get(d_jointListBuldTags[k]),noneValid = False)
                except Exception,error:
		    raise Exception,"Failed to find key:'%s'|msgList attr:'%s'|%s"%(k,d_jointListBuldTags[k],error)

            #Make some rverse lists
            """ for str_key in 'lwrLipRight','uprLipRight':
                ml_buffer = copy.copy(self.md_jointList[str_key])
                ml_buffer.reverse()
                self.md_jointList[str_key+"Reversed"] = ml_buffer"""


            #Build our handle build info stuff...
            #TODO make this a contditional build for when we don't use all the joints
            '''
	                                           "uprCheekSegment":{'left':{'skinKey':'uprCheekLeft'},
                                                          'right':{'skinKey':'uprCheekRight'},
                                                          'mode':'segmentChain'},
                                       "cheekSegment":{'left':{'skinKey':'cheekLeft'},
                                                       'right':{'skinKey':'cheekRight'},
                                                       'mode':'segmentChain'},
                                       "jawLineSegment":{'left':{'skinKey':'jawLineLeft'},
                                                         'right':{'skinKey':'jawLineRight'},
                                                         'mode':'segmentChain'},
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

            self.md_handleBuildInfo = {#'teethUpr':{"center":{'skinKey':'teethUpr','mode':'simpleDuplicate'}},
	                               "tongue":{"center":{'skinKey':'tongue'},'mode':'startEnd','orientToSurface':False, 'tags':['tongueBase','tongueTip']},
                                       "jaw":{"center":{'skinKey':'jaw'},'mode':'zeroDuplicate'},
	                               }


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
	    
	    return

            try:#>>Stretch Chain ===================================================================
                str_crv = mc.curve(d = 1,ep = [self.mi_squashStartCrv.getPosition(),self.mi_squashEndCrv.getPosition()], os = True)
                l_pos = crvUtils.returnSplitCurveList(str_crv,5)
                mc.delete(str_crv)		
                l_joints = joints.createJointsFromPosListName(l_pos)
                joints.orientJointChain(l_joints,mi_go._jointOrientation,"%sup"%mi_go._jointOrientation[1])  

                ml_stretchJoints = []
                for i,jnt in enumerate(l_joints):
                    mi_jnt = cgmMeta.asMeta(jnt,'cgmObject',setClass=True)
                    if i == 0:
                        mi_jnt.addAttr('cgmPosition','lower')
                        mi_jnt.addAttr('cgmName','stretchSegment')
                    mi_jnt.addAttr('cgmIterator',i)
                    mi_jnt.doName()
                    ml_stretchJoints.append(mi_jnt)
                    #self.ml_handleJoints.append(mi_jnt)
                mi_go._i_rigNull.msgList_connect(ml_stretchJoints,'lowerStretchSegment',"rigNull")

            except Exception,error:raise Exception,"[Stretch Chain | error: {0}]".format(error)

            try:#>>Stretch handles ===================================================================
                d_segmentHandles = {'start':ml_stretchJoints[0],
                                    'end':ml_stretchJoints[-1]}
                for str_k in d_segmentHandles.keys():
                    mi_target = d_segmentHandles[str_k]
                    mi_jnt = cgmMeta.asMeta( mc.duplicate(mi_target.mNode,po=True,ic=True,rc=True)[0],'cgmObject',setClass=True )
                    mi_jnt.addAttr('cgmTypeModifier',str_k,attrType='string',lock=True)
                    mi_jnt.doName()		
                    mi_jnt.connectChildNode
                    mi_jnt.parent = False	
                    #self.ml_handleJoints.append(mi_jnt)		    
                    mi_go._i_rigNull.connectChildNode(mi_jnt,'lowerStretch%sDriver'%str_k.capitalize(),"rigNull")

            except Exception,error:raise Exception,"[Stretch Handles | error: {0}]".format(error)	

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
                            mi_root = cgmMeta.asMeta( mc.duplicate(mi_rootTarget.mNode,po=True,ic=True,rc=True)[0],'cgmObject',setClass=True )
                            mi_end = cgmMeta.asMeta( mc.duplicate(d_buffer[str_tag].mNode,po=True,ic=True,rc=True)[0],'cgmObject',setClass=True )
                            mi_end.parent = mi_root			    				    			    
                            mi_root.addAttr('cgmTypeModifier',str_tag,attrType='string',lock=True)
                            mi_root.doName(nameChildren=True)
                            mi_root.parent = mi_rootTarget

                            mi_rootTarget.connectChildNode(mi_root,str_tag,'owner')
                            mi_rootTarget.connectChildNode(mi_end,"%sSkin"%str_tag,'owner')			
                            self.ml_tighteners.append(mi_root)
                            joints.orientJointChain([mJnt.mNode for mJnt in [mi_root,mi_end]],mi_go._jointOrientation,"%sup"%mi_go._jointOrientation[1])  
                        except Exception,error:raise Exception,"[%s]{%s}"%(str_tag,error)
            except Exception,error:raise Exception,"[Lip tighteners | error: {0}]".format(error)

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
			    elif str_mode == 'smileLine':
                                self.ml_build = [ml_skinJoints[0],'uprMid','mid',ml_skinJoints[-1]]				
                            elif str_mode == 'startEnd':
                                self.ml_build = [ml_skinJoints[0],ml_skinJoints[-1]]
                            elif str_mode == 'zeroDuplicate':
                                self.ml_build = [ml_skinJoints[0]]		    
                            else:
                                self.ml_build = ml_skinJoints
                            #Build ----------------------------------------------------------
                            if str_mode in ['simpleDuplicate','zeroDuplicate']:
                                mi_jnt = cgmMeta.asMeta( mc.duplicate(self.ml_build[0].mNode,po=True,ic=True,rc=True)[0],'cgmObject',setClass=True )
                                mi_jnt.parent = False#Parent to world	
                                if l_tags:
                                    mi_jnt.addAttr('cgmName',l_tags[0],attrType='string',lock=True)				    				    			    
                                ml_handleJoints.append(mi_jnt)
				if str_mode == 'zeroDuplicate':
				    #mi_jnt.parent = self.ml_build[0].parent
				    self.ml_build[0].rigJoint.parent = mi_jnt
				    mi_jnt.addAttr('cgmNameModifier','zero',attrType='string',lock=True)
				    mi_jnt.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)				    				    
				    mi_jnt.connectParentNode(self.ml_build[0],'sourceJoint','zeroJoint')
				else:
				    mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)
				mi_jnt.doName()
				    
                                """if str_mode == 'zeroDuplicate':
                                    mc.delete( mc.normalConstraint(self.mi_skullPlate.mNode,mi_jnt.mNode,
                                                                   weight = 1, aimVector = mi_go._vectorAim,
                                                                   upVector = mi_go._vectorUp, worldUpType = 'scene' ))			    
                                    jntUtils.freezeJointOrientation(mi_jnt)"""					    
                            elif str_mode == 'segmentChain':
                                if not self.ml_build:#Build our list from ml_targets if we don't have them from the skin key
                                    self.ml_build = d_buffer['ml_targets']
                                ml_segJoints = []
                                for i,mJnt in enumerate(self.ml_build):
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

                                mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject',setClass=True )
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
                                except Exception,error:raise Exception,"[mouthMove pos fail]{%s}"%error

                                mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject',setClass=True )
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

                                except Exception,error:raise Exception,"Failed to get data for simple aim: %s"%error
                                try:#Create
                                    pos = crvUtils.returnSplitCurveList(mi_crv.mNode, 1, minU = minU, maxU = maxU, reverseCurve = b_reverse, rebuildForSplit=True)[0]				
                                    mc.select(cl=True)
                                    mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject',setClass=True )
                                    mi_jnt.parent = False
                                    mi_jnt.addAttr('cgmName',k_name,lock=True)										
                                    mi_jnt.addAttr('cgmDirection',k_direction,lock=True)
                                    mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)				    
                                    mi_jnt.doName()
                                    ml_tmpHandles.append(mi_jnt)				
                                except Exception,error:raise Exception,"[Simple aim build fail]{%s}"%error
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

                                        except Exception,error:raise Exception,"Simple aim fail: %s"%error
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
                                        except Exception,error:raise Exception,"[midAimBlend aim fail]{%s}"%error

                                    jntUtils.metaFreezeJointOrientation(mi_jnt)				
                                except Exception,error:raise Exception,"[mid fail]{%s}"%error
                            else:
                                for i,mJnt in enumerate(self.ml_build):
                                    if mJnt in ['mid','uprMid']:
                                        mi_crv = d_buffer.get('crv')
                                        if not mi_crv:
                                            raise StandardError,"[Step: '%s' '%s' | failed to find use curve]"%(k_name,k_direction)
                                        
                                        if str_mode in ['smileLine','midSmileLinePoint']:
					    if mJnt == 'mid':
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
						except Exception,error:raise Exception,"[midClosestCurvePoint failed | error: {0}]".format(error)    
					    else:
						try:
						    #Get initial point to get distance, offset a loc, get new pos
						    pos = crvUtils.getPercentPointOnCurve(mi_crv,.25)
						except Exception,error:raise Exception,"[midClosestCurvePoint failed | error: {0}]".format(error)   						
                                        else:
                                            pos = crvUtils.getMidPoint(mi_crv)
                                        mc.select(cl=True)
                                        mi_jnt = cgmMeta.asMeta( mc.joint(p = pos),'cgmObject',setClass=True )
                                        mi_jnt.parent = False
                                        mi_jnt.addAttr('cgmDirection',k_direction,lock=True)
                                        if l_tags:
                                            mi_jnt.addAttr('cgmName',l_tags[i],attrType='string',lock=True)				    				    
                                        else:
                                            mi_jnt.addAttr('cgmName',k_name,lock=True)						
                                            mi_jnt.addAttr('cgmNameModifier','mid',attrType='string',lock=True)				    
                                        mi_jnt.addAttr('cgmTypeModifier','handle',attrType='string',lock=True)				    
                                        mi_jnt.doName()
                                        ml_handleJoints.append(mi_jnt)

                                        #Orient
                                        v_aimVector = mi_go._vectorAim				
                                        v_upVector = mi_go._vectorUp
					'''
                                        mc.delete( mc.normalConstraint(self.mi_skullPlate.mNode,mi_jnt.mNode,
                                                                       weight = 1, aimVector = v_aimVector, upVector = v_upVector, 
                                                                       ))
					                               '''
                                        jntUtils.freezeJointOrientation(mi_jnt)
                                    else:
                                        i_j = cgmMeta.asMeta( mc.duplicate(mJnt.mNode,po=True,ic=True,rc=True)[0],'cgmObject',setClass=True )
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
                    except Exception,error:raise Exception,"['{0}' '{1}' failed | error:{2}".format(k_name,k_direction,error)   
            try:#Flipping
                ml_rightHandles = metaUtils.get_matchedListFromAttrDict(ml_handleJoints , cgmDirection = 'right')
                for mJoint in ml_rightHandles:
                    #self.log_info("%s flipping"% mJoint.p_nameShort)
                    mJoint.__setattr__("r%s"% mi_go._jointOrientation[1],180)
                    jntUtils.freezeJointOrientation(mJoint)		    
            except Exception,error:raise Exception,"[flipping] | error: {2}".format(error)   

        def build_connections(self):  
            mi_go = self._go#Rig Go instance link	    	    
            ml_jointsToConnect = []
            ml_jointsToConnect.extend(self.ml_rigJoints) 
            #ml_jointsToConnect.extend(self.ml_tighteners)    
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
                            self.progressBar_set(status = "Registering: '{0}'".format(mObj.p_nameShort), progress =  i, maxValue = int_lenMax)		    				    		    			
                            self.log_info("%s On '%s'..."%(self._str_reportStart,mObj.p_nameShort))
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
                                                                  #["mirrorRoll","r%s"%mi_go._jointOrientation[2]],
                                                                  #["mirrorTwist","r%s"%mi_go._jointOrientation[1]],
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

                            if str_cgmNameTag in ['jaw','noseMove','mouthMove','noseTop','noseUnder','noseTip','tongueTip','tongueBase','teethUpr','teethLwr']:
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
                        raise StandardError,"[Iterative fail item: {0} | obj: {1} | mirror side: {2}] -- {3}".format(i,mObj.p_nameShort,str_mirrorSide,error)

            self._go._i_rigNull.msgList_connect(self.ml_directControls ,'controlsDirect', 'rigNull')	    
            self.ml_controlsAll.extend(self.ml_directControls)#append	

        def _buildConnections_(self):
            #Register our mirror indices ---------------------------------------------------------------------------------------
            mi_go = self._go#Rig Go instance link	
	    #Need to move the mirror registration setup as the stuff is getting off
	    """
            for str_direction in self.md_directionControls.keys():
                int_start = self._go._i_puppet.get_nextMirrorIndex( str_direction )
		self.log_info("{0} start: {1}".format(str_direction,int_start))
		
                ml_list = self.md_directionControls[str_direction]
                int_lenMax = len(ml_list)				
                for i,mCtrl in enumerate(ml_list):
                    self.progressBar_set(status = "Setting mirror index: '{0}'".format(mCtrl.p_nameShort), progress =  i, maxValue = int_lenMax)		    				    		    					    
                    try:mCtrl.addAttr('mirrorIndex', value = (int_start + i))		
                    except Exception,error: raise StandardError,"Failed to register mirror index | mCtrl: {0} | {1}".format(mCtrl,error)
		    """
            try:self._go._i_rigNull.msgList_connect(self.ml_controlsAll,'controlsAll')
            except Exception,error: raise StandardError,"[Controls all connect]{%s}"%error	    
            try:self._go._i_rigNull.moduleSet.extend(self.ml_controlsAll)
            except Exception,error: raise StandardError,"[Failed to set module objectSet]{%s}"%error

    return fncWrap(*args, **kws).go()


def build_rig(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_rig({0})'.format(self.d_kws['goInstance']._strShortName)	
            self._b_reportTimes = True
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Gather Info','call':self._gatherInfo_},
	                        {'step':'Mirror Indexing','call':self._mirrorIndex_},
                                #OLD BUILD#{'step':'Build Skull Deformation','call':self._buildSkullDeformation_},	
                                #OLD BUILD#{'step':'Build Lip Up loc structure','call':self._buildLipUpLocStructure_},	                                
                                #OLD BUILD#{'step':'Mouth/Lip Handles','call':self._buildMouthHandles_},
                                #OLD BUILD# {'step':'Lip Structure','call':self._buildLipStructure_},
                                #OLD BUILD#{'step':'Lip Over/Under','call':self._buildLipOverUnder_},	                        
                                #OLD BUILD#{'step':'Smile Line Build','call':self._buildSmileLines_},	                        	                        
                                #OLD BUILD#{'step':'NoseBuild','call':self._buildNose_},#Smile lines must be built and mouth handles
                                {'step':'Tongue build','call':self._buildTongue_},
	                        {'step':'Teeth build','call':self._buildTeeth_},
                                ###{'step':'Upper Cheek','call':self._buildUprCheek_},
                                ###{'step':'Mid Cheek','call':self._buildMidCheek_},	  
                                #OLD BUILD#{'step':'JawLine build','call':self._buildJawLines_},
                                #OLD BUILD#{'step':'Cheek Surface Build','call':self._buildCheekSurface_},
                                {'step':'Lock N hide','call':self._lockNHide_},
                                ]	
            #=================================================================
        def _gatherInfo_(self):
            mi_go = self._go#Rig Go instance link

            self.mi_helper = cgmMeta.validateObjArg(mi_go._mi_module.getMessage('helper'),noneValid=True)
            if not self.mi_helper:raise StandardError,"No suitable helper found"

            for attr in self.mi_helper.getAttrs(userDefined = True):#Get allof our Helpers
                if "Helper" in attr:
                    try:self.__dict__["mi_%s"%attr.replace('Helper','Crv')] = cgmMeta.validateObjArg(self.mi_helper.getMessage(attr),noneValid=False)
                    except Exception,error:raise Exception, " Failed to find '%s' | %s"%(attr,error)

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
	    self._l_baseHandleKeys = []
	    self.d_buffer = {}
	    
            try:#Build dicts to check ==================================================================================================
		#>> Jaw --------------------------------------------------------------------------------------------------
		b_buildJawLine = True	    
		d_jawBuild = {'jawRig':{'bypass': metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
		                                                                        cgmName = 'jaw',
		                                                                        cgmTypeModifier = 'rig')},
		              'jawZero':{'bypass': metaUtils.get_matchedListFromAttrDict(ml_handleJoints,
		                                                                         cgmName = 'jaw',
		                                                                         cgmNameModifier = 'zero')},}
		_l_buildDicts.append(d_jawBuild)

                #>> tongue --------------------------------------------------------------------------------------------------
                b_buildTongue = True
                d_tongueBuild = {'tongueRig':{'check':ml_rigJoints,'checkToggle':b_buildTongue,'tag':'tongue'},
                                 'tongueBase':{'check':ml_handleJoints,'checkToggle':b_buildTongue},
                                 'tongueTip':{'check':ml_handleJoints,'checkToggle':b_buildTongue}}

                _l_buildDicts.append(d_tongueBuild)
		
		#>> tongue --------------------------------------------------------------------------------------------------
		b_buildTeeth = True
		d_teethUprBuild = {'teethUprRig':{'bypass': metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
		                                                                                  cgmName = 'teeth',
		                                                                                  cgmPosition = 'upper')},
		                   'teethLwrRig':{'bypass': metaUtils.get_matchedListFromAttrDict(ml_rigJoints,
		                                                                                  cgmName = 'teeth',
		                                                                                  cgmPosition = 'lower') }}
	    
		_l_buildDicts.append(d_teethUprBuild)		
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
		    self._l_baseHandleKeys.append(k_tag)
                    if d_tag.get('tag'):str_tag = d_tag['tag']
                    else:str_tag = k_tag
                    l_keys = d_tag.keys()
                    self.progressBar_set(status = ("Getting: '%s'"%k_tag),progress = i, maxValue = int_keys)
                    if d_tag.get('checkToggle') in [True,None]:
			self.md_rigList[k_tag] = {}
			
			if d_tag.get('bypass'):
			    ml_checkSub = d_tag.get('bypass')
			else:
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
                except Exception,error:raise Exception,"['{0}' loop | error: {1}]".format(k_tag,error)
	    self.report()

            #>> Calculate ==========================================================================
            #Width of the skull plate...trying
            #self.f_offsetOfUpLoc = distance.returnBoundingBoxSizeToAverage(self.mi_skullPlate.mNode)
	    self.f_offsetOfUpLoc = 3.0
            
            #>> Data buffers =======================================================================
            self.d_dataBuffer = {}            
            self.d_dataBuffer['f_lenJawLine'] = distance.returnCurveLength(self.mi_jawLineCrv.mNode)

            #>> Running lists ==========================================================================
            self.md_rigList['specialLocs'] = {}
            self.ml_toVisConnect = []
            self.ml_curves = []
            self.md_attachReturns = {}
            #self.report()
            return True
	
        def _mirrorIndex_(self):   
            try:#>> Get some data =======================================================================================
                mi_go = self._go
                l_keys = self._l_baseHandleKeys
		for k in ['tongueRig','jawRig','jawZero']:
		    l_keys.remove(k)
		_d_directionToMirrorSide = {'left':'Left','right':'Right','center':'Centre'}
		_d_sideIndices = {'Left':0,'Right':0,'Centre':0}
		_d_matchTest = {'Left':{},'Right':{},'Center':{}}
            except Exception,error:raise Exception,"[Get Info! | error: {0}]".format(error)
            
            try:#>> Get some data =======================================================================================
		for k_side in _d_sideIndices.keys():
		    int_start = mi_go._i_puppet.get_nextMirrorIndex( k_side )
		    _d_sideIndices[k_side] = int_start
		    self.log_info("{0} start: {1}".format(k_side,int_start))
            except Exception,error:raise Exception,"[Side info! | error: {0}]".format(error)	    
	    
            try:#>> Set indices =======================================================================================
		for k_tag in l_keys:
		    try:
			d_tagFromRigList = self.md_rigList[k_tag]
			if type(d_tagFromRigList) is dict:
			    for k_dir in _d_directionToMirrorSide.keys():
				try:
				    str_mirrorSide = _d_directionToMirrorSide[k_dir]
				    int_start = _d_sideIndices[str_mirrorSide]
				    ml_buffer = d_tagFromRigList.get(k_dir) or []
				    for i,mCtrl in enumerate(ml_buffer):
					int_running = int_start + i
					self.log_info("{0} - '{1}' | sidestart: {2} | idx: {3}".format(str_mirrorSide,mCtrl.p_nameShort,
					                                                               int_start,int_running))
					try:mCtrl.addAttr('mirrorIndex', value = (int_running))		
					except Exception,error: raise Exception,"Failed to register mirror index | mCtrl: {0} | {1}".format(mCtrl,error)			    
				    _d_sideIndices[str_mirrorSide] = int_running + 1#...push back
				except Exception,error: raise Exception,"'{0}' | {1}".format(k_dir,error)
			else:
			    try:
				int_start = _d_sideIndices['Centre']
				ml_buffer = d_tagFromRigList
				for i,mCtrl in enumerate(d_tagFromRigList):
				    int_running = int_start + i
				    self.log_info("{0} - '{1}' | sidestart: {2} | idx: {3}".format('Centre',mCtrl.p_nameShort,
				                                                                   int_start,int_running))
				    try:mCtrl.addAttr('mirrorIndex', value = (int_running))		
				    except Exception,error: raise Exception,"Failed to register mirror index | mCtrl: {0} | {1}".format(mCtrl,error)			    
				_d_sideIndices['Centre'] = int_running + 1#...push back
			    except Exception,error: raise Exception,"Nondict | {0}".format(error)
		    except Exception,error: raise Exception,"'{0}' | {1}".format(k_tag,error)			    
            except Exception,error:raise Exception,"[Set indices! | error: {0}]".format(error)		    
	    
	    """
            for str_direction in self.md_directionControls.keys():
                int_start = self._go._i_puppet.get_nextMirrorIndex( str_direction )
		self.log_info("{0} start: {1}".format(str_direction,int_start))
		
                ml_list = self.md_directionControls[str_direction]
                int_lenMax = len(ml_list)				
                for i,mCtrl in enumerate(ml_list):
                    self.progressBar_set(status = "Setting mirror index: '{0}'".format(mCtrl.p_nameShort), progress =  i, maxValue = int_lenMax)		    				    		    					    
                    try:mCtrl.addAttr('mirrorIndex', value = (int_start + i))		
                    except Exception,error: raise StandardError,"Failed to register mirror index | mCtrl: {0} | {1}".format(mCtrl,error)
		    """
	    
        def _buildSkullDeformation_(self):   
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
            except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)

            try:#>> Setup =======================================================================================
                self._buildJawDeformation_()
            except Exception,error:raise Exception,"[Jaw Deformation!| error: {0}]".format(error)

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

                d_ = self.d_buffer
                mi_jawPivotCrv = self.mi_jawPivotCrv
                mi_squashStartCrv = self.mi_squashStartCrv
                mi_jawHandle = self.md_rigList['jawHandle'][0]
                mi_jawRig = self.md_rigList['jawRig'][0]	
                mi_chinHandle = self.md_rigList['chin'][0]		
                mi_noseMoveHandle = self.md_rigList['noseMoveHandle'][0]
                mi_mouthMove = self.md_rigList['mouthMove'][0]

                f_lenJawLine = self.d_dataBuffer['f_lenJawLine']
                d_['f_lenJawLine'] = f_lenJawLine
                d_['mi_jawHandle'] = mi_jawHandle
                d_['mi_jawRig'] = mi_jawRig
                d_['mi_noseMoveHandle'] = mi_noseMoveHandle
                d_['mi_mouthMove'] = mi_mouthMove
            except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)

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
                        except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)

                        if d_sub.get('toDup'):
                            mJoint = cgmMeta.asMeta(mc.joint(p = d_sub['toDup'].getPosition()),'cgmObject',setClass=True)
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
                                mObj = cgmMeta.asMeta(mc.joint(p = mi_loc.getPosition()),'cgmObject',setClass=True)
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
                    except Exception,error:raise Exception,"[post parenting! | error: {0}]".format(error)

                except Exception,error:raise Exception,"[def duplication! | error: {0}]".format(error)	
            except Exception,error:raise Exception,"[Simple Def ! | error: {0}]".format(error)	
            
            try:#Build Some Special Locs =======================================================================================
                mi_uprHeadDef = self.md_rigList['uprHeadDef'][0]
                d_directions = {'left':{'vector':[-2,0,0]},
                                'right':{'vector':[2,0,0]}}
                
                d_toDo = {'uprHeadDef':mi_uprHeadDef,
                          'jawRig':mi_jawRig}

                for k_tag in d_toDo.keys():
                    self.md_rigList['specialLocs'][k_tag] = {}
                    __d = self.md_rigList['specialLocs'][k_tag] 
                    mObj = d_toDo[k_tag]
                    
                    for k_dir in d_directions.keys():
                        mi_loc = mObj.doLoc()
                        str_locKey = "{0}Loc{1}".format(k_tag,k_dir.capitalize())
                        log.info(str_locKey)
                        v_offset = cgmMath.multiplyLists([d_directions[k_dir]['vector'],[f_lenJawLine,f_lenJawLine,f_lenJawLine]])
                        try:mc.move(v_offset[0],v_offset[1],v_offset[2],mi_loc.mNode,relative = 1)
                        except Exception,error:"[Move fail | error: {0}]".format(error)
                        try:
                            mi_loc.addAttr('cgmName',str_locKey)
                            mi_loc.doName()
                        except Exception,error:"[Name | error: {0}]".format(error)
                        
                        mi_loc.parent = mObj
                        __d[k_dir] = mi_loc
                        mi_uprHeadDef.connectChildNode(mi_loc,str_locKey,'source')
                        self._go.connect_toRigGutsVis(mi_loc,vis = True)#connect to guts vis switches
                    
            except Exception,error:raise Exception,"[Build Skull up locs | error: {0}]".format(error) 	             
             
            try:#Get Segment Data =======================================================================================
                ml_segment = self.md_rigList['squashSegmentLower']['center']
                mi_startInfluence = self.md_rigList['squashSegmentLower']['start']
                mi_endInfluence = self.md_rigList['squashSegmentLower']['end']

                #d_segReturn = rUtils.createSegmentCurve(ml_segment, addMidTwist = False, moduleInstance = mi_go._mi_module, connectBy = 'scale')

            except Exception,error:raise Exception,"[Get Segment data | error: {0}]".format(error) 	 

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
                except Exception,error:raise Exception,"[post segment query! | {0}]".format(error)

                try:#post segment parent
                    mi_curve.segmentGroup.parent = mi_go._i_rigNull.mNode
                    for attr in 'translate','scale','rotate':
                        cgmMeta.cgmAttr(mi_curve,attr).p_locked = False
                    mi_curve.parent = mi_go._i_rigNull

                    d_segReturn['ml_driverJoints'][0].parent = self.md_rigList['faceBaseDef'][0]	
                    d_segReturn['ml_drivenJoints'][0].parent = self.md_rigList['faceBaseDef'][0]	
                    mi_anchorEnd.parent = mi_jawHandle#...not sure what we want to parent to yet
                    mi_anchorStart.parent = self.md_rigList['faceBaseDef'][0]

                except Exception,error:raise Exception,"[post segment parent! | error: {0}]".format(error)

                self.d_buffer = d_segReturn
                #self.log_infoNestedDict('d_buffer')
            except Exception,error:raise Exception,"[cgmSegment creation | error: {0}]".format(error) 	 

            try:#>>>Connect master scale =======================================================================================
                mi_distanceBuffer = mi_curve.scaleBuffer		
                cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn(mPlug_multpHeadScale.p_combinedShortName)    
            except Exception,error:raise Exception,"[segment scale connect! | error: {0}]".format(error)

            try:#Do a few attribute connections =======================================================================================
                #Push squash and stretch multipliers to cog
                try:
                    for k in mi_distanceBuffer.d_indexToAttr.keys():
                        attrName = 'scaleMult_%s'%k
                        cgmMeta.cgmAttr(mi_distanceBuffer.mNode,'scaleMult_%s'%k,keyable=1,hidden=0).doCopyTo(mi_jawHandle.mNode,attrName,connectSourceToTarget = True)
                        cgmMeta.cgmAttr(mi_jawHandle.mNode,attrName,defaultValue = 1)
                except Exception,error:raise Exception,"[scaleMult transfer! | error: {0}]".format(error)

                cgmMeta.cgmAttr(mi_curve,'twistType').doCopyTo(mi_jawHandle.mNode,connectSourceToTarget=True)
                cgmMeta.cgmAttr(mi_curve,'twistExtendToEnd').doCopyTo(mi_jawHandle.mNode,connectSourceToTarget=True)
                cgmMeta.cgmAttr(mi_curve,'scaleMidUp').doCopyTo(mi_jawHandle.mNode,connectSourceToTarget=True)
                cgmMeta.cgmAttr(mi_curve,'scaleMidOut').doCopyTo(mi_jawHandle.mNode,connectSourceToTarget=True)
            except Exception,error:raise Exception,"[segment attribute transfer! | error: {0}]".format(error)

            try:#>> Skin  =======================================================================================
                d_build = {'browPlate':{'target':mi_browPlate,'mi':3,'dr':9,
                                            'bindJoints':self.md_rigList['uprHeadDef']},
		           'jawPlate':{'target':mi_jawPlate,'mi':4,'dr':9,
                                       'bindJoints':ml_skinJoints + ml_segment},
                           'lwrTeethPlate':{'target':mi_lwrTeethPlate,'mi':3,'dr':9,
                                            'bindJoints':[mi_jawRig]},
                           'uprTeethPlate':{'target':mi_uprTeethPlate,'mi':3,'dr':9,
                                            'bindJoints':self.md_rigList['uprHeadDef']}}
		faceUtils.skin_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Skin skull!] | error: {0}".format(error)	

            try:#>> Connect  =======================================================================================
                mc.parentConstraint(mi_jawHandle.mNode,mi_jawRig.mNode)
                mc.scaleConstraint(mi_jawHandle.mNode,mi_jawRig.mNode)

                #ConnectVis
                #mi_go.connect_toRigGutsVis(self.md_rigList['faceBaseDef'],vis = True)#connect to guts vis switches
            except Exception,error:raise Exception,"[Connect!] | error: {0}".format(error)
            
        def _buildLipUpLocStructure_(self):
            try:#>> Get some data =======================================================================================
                mi_go = self._go#Rig Go instance link

                f_offsetOfUpLoc = self.f_offsetOfUpLoc      
		f_lenJawLine = self.d_dataBuffer['f_lenJawLine']
            except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)

            try:#>> Build chains =======================================================================================
		#'parent':self.md_rigList['uprHeadDef']
		self.md_rigList['lipOverUnderJnts'] = {}		
                d_jointsToCreate = {'uprLipUpDriver':{'center':{'start':self.md_rigList['noseMoveHandle'][0],
		                                                'end':self.md_rigList['lipUprHandle']['center'][0],
		                                                'offsetMultiplier':1},
		                                      'left':{'start':self.md_rigList['nostrilRig']['left'][0],
		                                              'end':self.md_rigList['lipUprHandle']['left'][0],
		                                              'offsetMultiplier':1},		        
		                                      'right':{'start':self.md_rigList['nostrilRig']['right'][0],
		                                               'end':self.md_rigList['lipUprHandle']['right'][0],
		                                               'offsetMultiplier':1}},		                    
		                    'lwrLipUpDriver':{'center':{'start':self.md_rigList['chin'][0],
		                                                'end':self.md_rigList['lipLwrHandle']['center'][0],
		                                                'offsetMultiplier':1},
		                                      'left':{'start':self.md_rigList['smileBaseHandle']['left'][0],
		                                              'end':self.md_rigList['lipLwrHandle']['left'][0],
		                                              'offsetMultiplier':1},		        
		                                      'right':{'start':self.md_rigList['smileBaseHandle']['right'][0],
		                                                             'end':self.md_rigList['lipLwrHandle']['right'][0],
		                                                             'offsetMultiplier':1}}}          
                for k_tag in d_jointsToCreate.iterkeys():
		    try:
			self.md_rigList['specialLocs'][k_tag] = {}
			self.md_rigList['lipOverUnderJnts'][k_tag] = {}
			
			for k_dir in d_jointsToCreate[k_tag].iterkeys():
			    try:
				try:#Query					
				    d_sub = d_jointsToCreate[k_tag][k_dir]
				    str_tagDir = "{0}{1}".format(k_tag,k_dir.capitalize())
				    self.log_info("building '{0}".format(str_tagDir))
				    ml_toLock = []
				    ml_toVisConnect = []
				    #self.md_rigList['specialLocs'][k_tag] = {}
				    #__d = self.md_rigList['specialLocs'][k_tag] 			    
				except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)
				
				try:#>>Create --------------------------------------------------------------------
				    ml_buffer = []
				    
				    mi_start = cgmMeta.asMeta(mc.joint(p = d_sub['start'].getPosition()),'cgmObject',setClass=True)
				    mi_end = cgmMeta.asMeta(mc.joint(p = d_sub['end'].getPosition()),'cgmObject',setClass=True)
				    ml_buffer = [mi_start,mi_end]
	    
				    mi_start.parent = d_sub.get('parent') or d_sub['start']
				    ml_toVisConnect.extend(ml_buffer)
				except Exception,error:raise Exception,"[Create! | error: {0}]".format(error)
				
				try:#>>Name --------------------------------------------------------------------
				    l_n = ['start','end']
				    for i,mJnt in enumerate(ml_buffer):
					mJnt.addAttr('cgmName',k_tag,lock=True)			
					mJnt.addAttr('cgmNameModifier',l_n[i],lock=True)	
					mJnt.doName()
					
					#ml_toLock.append(mJnt)				
				except Exception,error:raise Exception,"[Name! | error: {0}]".format(error)
				
				try:#>>Orient --------------------------------------------------------------------
				    joints.orientJointChain([mJnt.mNode for mJnt in ml_buffer],mi_go._jointOrientation,"{0}up".format(mi_go._jointOrientation[0]))  
				except Exception,error:raise Exception,"[Orient! | error: {0}]".format(error)                        
				
				try:#>>Create IK handle --------------------------------------------------------------------
				    buffer = mc.ikHandle( sj=mi_start.mNode, ee=mi_end.mNode,
					                  solver = 'ikRPsolver', forceSolver = True,
					                  snapHandleFlagToggle=True )  	
				    #>>> Name --------------------------------------------------------------------
				    log.debug(buffer)
				    mi_ik_handle = cgmMeta.asMeta(buffer[0],'cgmObject',setClass=True)
				    mi_ik_handle.addAttr('cgmName',k_tag,attrType='string',lock=True)    
				    mi_ik_handle.doName()
							
				    mi_ik_effector = cgmMeta.asMeta(buffer[1],'cgmNode',setClass=True)
				    mi_ik_effector.addAttr('cgmName',k_tag,attrType='string',lock=True)    
				    mi_ik_effector.doName()   
				    
				    mi_ik_handle.parent = d_sub['end']#...parent
				    ml_toVisConnect.append(mi_ik_handle)				
				    
				except Exception,error:raise Exception,"[ikHandle creation! | error: {0}]".format(error)
				
				try:#>>rpLoc --------------------------------------------------------------------
				    mi_rpLoc = mi_start.doLoc()
				    mi_rpLoc.addAttr('cgmName',k_tag,lock=True)			
				    mi_rpLoc.addAttr('cgmTypeModifier','rp',lock=True)
				    mi_rpLoc.doName()
				    ml_toLock.append(mi_rpLoc)	
				    ml_toVisConnect.append(mi_rpLoc)				
							    
				    setattr(mi_rpLoc,"t{0}".format(mi_go._jointOrientation[2]),(f_lenJawLine * d_sub['offsetMultiplier']))
				    mi_rpLoc.parent = d_sub.get('parent') or d_sub['start']
				except Exception,error:raise Exception,"[upLoc! | error: {0}]".format(error) 
				
				try:#>>poleVector --------------------------------------------------------------------
				    cBuffer = mc.poleVectorConstraint(mi_rpLoc.mNode,mi_ik_handle.mNode)
				    rUtils.IKHandle_fixTwist(mi_ik_handle)#...Fix the twist
				    f_buffer = getattr(mi_end,"t{0}".format(mi_go._jointOrientation[0]))
				    setattr(mi_end,"t{0}".format(mi_go._jointOrientation[0]),f_buffer * .25)
				    
				except Exception,error:raise Exception,"[poleVector! | error: {0}]".format(error) 
				
				try:#>>upLoc --------------------------------------------------------------------
				    mi_upLoc = mi_start.doLoc()
				    mi_upLoc.addAttr('cgmName',k_tag,lock=True)			
				    mi_upLoc.addAttr('cgmTypeModifier','up',lock=True)
				    mi_upLoc.doName()
				    ml_toLock.append(mi_upLoc)				
				    ml_toVisConnect.append(mi_upLoc)				
				    
				    mi_upLoc.parent = mi_start
				    setattr(mi_upLoc,"t{0}".format(mi_go._jointOrientation[1]),(f_lenJawLine * d_sub['offsetMultiplier']))
				except Exception,error:raise Exception,"[upLoc! | error: {0}]".format(error) 
				
				try:#>>cleanup --------------------------------------------------------------------
				    mi_go.connect_toRigGutsVis(ml_toVisConnect,vis = True)#connect to guts vis switches
				    
				    self.md_rigList['specialLocs'][str_tagDir] = [mi_upLoc]
				    self.md_rigList['specialLocs'][k_tag][k_dir] = [mi_upLoc]
				    
				    self.md_rigList['lipOverUnderJnts'][str_tagDir] = [mi_start]
				    self.md_rigList['lipOverUnderJnts'][k_tag][k_dir] = [mi_start]
				    
				    for mObj in ml_toLock:
					for channel in ['translate','scale','rotate']:
					    mc.setAttr ((mObj.mNode+'.'+channel),lock=1)          
				    mc.select(cl=1)                                        
				    
				except Exception,error:raise Exception,"[clean up! | error: {0}]".format(error) 
				
			    except Exception,error:raise Exception,"[{0} fail | error: {1}]".format(k_dir,error)
		    except Exception,error:raise Exception,"[{0} fail | error: {1}]".format(k_tag,error)
	    except Exception,error:raise Exception,"[Build chains! | error: {0}]".format(error)            
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

            except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)

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
                        except Exception,error:raise Exception,"[Query! | error: {0}]".format(error)

                        if d_sub.get('toDup'):
                            mJoint = cgmMeta.asMeta(mc.joint(p = d_sub['toDup'].getPosition()),'cgmObject',setClass=True)
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
                                mObj = cgmMeta.asMeta(mc.joint(p = mi_loc.getPosition()),'cgmObject',setClass=True)
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
                    except Exception,error:raise Exception,"[post parenting! | error: {0}]".format(error)

                except Exception,error:raise Exception,"[def duplication! | error: {0}]".format(error)	

                #self.log_infoNestedDict('d_buffer')
            except Exception,error:raise Exception,"[Get Joints! | error: {0}]".format(error)	
            '''
	    try:#>> Skin  =======================================================================================
		d_build = {'lwrLipBase':{'target':self.mi_skullPlate,'mi':5,'dr':9,
		                         'bindJoints':ml_skinJoints + [mi_jawRig]}}
		self.skin_fromDict(d_build)

	    except Exception,error:raise Exception,"[Skin skull!] | error: {0}".format(error)	
	    '''
            try:#>> Connect  =======================================================================================
                mc.parentConstraint(mi_jawHandle.mNode,mi_jawRig.mNode)
                mc.scaleConstraint(mi_jawHandle.mNode,mi_jawRig.mNode)

                #ConnectVis
                mi_go.connect_toRigGutsVis(self.md_rigList['faceBaseDef'],vis = True)#connect to guts vis switches

            except Exception,error:raise Exception,"[Connect!] | error: {0}".format(error)

            try:#>> StableJaw  =======================================================================================
                mc.orientConstraint(mi_jawRig.mNode,self.md_rigList['stableJaw'][0].mNode,skip = ["%s"%mi_go._jointOrientation[2]])
                mc.pointConstraint(mi_jawRig.mNode,self.md_rigList['stableJaw'][0].mNode,skip = ["%s"%str_axis for str_axis in [mi_go._jointOrientation[0],mi_go._jointOrientation[1]]])		
                self.md_rigList['stableJaw'][0].rotateOrder = mi_go._jointOrientation
            except Exception,error:raise Exception,"[Stable!] | error: {0}".format(error)

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
                            except Exception,error:raise Exception,"[Radial Loft |error: {0}]".format(error)
                        else:
                            try:#Regular loft -----------------------------------------------------------------------
                                ml_joints = d_buffer['joints']
                                mi_crv = d_buffer['extrudeCrv']

                                try:#Make our loft loc -----------------------------------------------------------------------
                                    #f_dist = distance.returnAverageDistanceBetweenObjects([mObj.mNode for mObj in ml_joints])*.05
                                    d_buffer['dist'] = f_dist

                                    mi_loc = ml_joints[-1].doLoc()
                                    mi_loc.doGroup()
                                except Exception,error:raise Exception,"[loft loc |error: {0}]".format(error)

                                try:#Cross section creation -----------------------------------------------------------------------
                                    l_profileCrvPos = []
                                    for dist in [0,f_dist]:
                                        mi_loc.__setattr__("t%s"%mi_go._jointOrientation[1],dist)
                                        l_profileCrvPos.append(mi_loc.getPosition())

                                    str_profileCrv = mc.curve(d = 1,ep = l_profileCrvPos, os = True)
                                except Exception,error:raise Exception,"[Cross section creation |error: {0}]".format(error)

                                try:#Extrude crv -----------------------------------------------------------------------
                                    str_extruded = mc.extrude([str_profileCrv,mi_crv.mNode],et = 1, sc = 1,ch = 1,useComponentPivot = 0,fixedPath=1)[0]
                                    mi_obj = cgmMeta.cgmObject(str_extruded)
                                    mc.delete(mi_loc.parent,str_profileCrv)
                                except Exception,error:raise Exception,"[Extrude crv |error: {0}]".format(error)	
                            except Exception,error:raise Exception,"[Regular loft | error: {0}]".format(error)
                        try:
                            self.__dict__['mi_%sRibbon'%(str_name)] = mi_obj
                            mi_obj.addAttr('cgmName',str_name,lock=True)
                            mi_obj.addAttr('cgmTypeModifier','ribbon',lock=True)			    
                            try:mi_obj.addAttr('cgmDirection',d_buffer['direction'] ,lock=True)
                            except:pass
                            mi_obj.doName()
                            mi_go._i_rigNull.connectChildNode(mi_obj,"%sRibbon"%str_name,'module')			    
                        except Exception,error:raise Exception,"[Naming |error: {0}]".format(error)
                        #self.log_infoNestedDict('d_buffer')

                    except Exception,error:raise Exception,"%s | %s"%(str_name,error)
            except Exception,error:raise Exception,"[Ribbons |error: {0}]".format(error)


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

                                except Exception,error:raise Exception,"[Rail curve build |error: {0}]".format(error)

                                try:				    
                                    ml_endProfileObjs = [ml_startRailObjs[-1],d_buffer['cheekJoints'][0], ml_endRailObjs[-1]]
                                    self.log_info("endProfileObjs: %s"%[mObj.p_nameShort for mObj in ml_endProfileObjs])
                                    str_endProfileCrv = mc.curve(d = 3,ep = [mObj.getPosition() for mObj in ml_endProfileObjs], os = True)
                                    str_startProfileCrv = mc.rebuildCurve (mi_smileCrv.mNode, ch=0, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]		
                                    str_endProfileCrvRebuilt = mc.rebuildCurve (str_endProfileCrv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=5, d=3, tol=0.001)[0]

                                except Exception,error:raise Exception,"[Profile curves build |error: {0}]".format(error)	

                                try:
                                    str_loft = mc.doubleProfileBirailSurface( str_startProfileCrv, str_endProfileCrvRebuilt,
                                                                              str_startRailCrv, str_endRailCrv, 
                                                                              blendFactor = .5,constructionHistory=0, object=1, polygon=0, transformMode=0)[0]
                                except Exception,error:raise Exception,"[birail create |error: {0}]".format(error)	

                                mc.delete([str_startProfileCrv,str_startRailCrv,str_endRailCrv,str_endProfileCrv])#Delete the rebuilt curves
                            except Exception,error:raise Exception,"[Reg plate loft |error: {0}]".format(error)	
                        else:
                            try:#Reg curve loft
                                l_crvsRebuilt = []
                                for mi_crv in d_buffer['crvs']:#rebuild crvs
                                    l_crvsRebuilt.append(self.returnRebuiltCurveString(mi_crv,4))

                                str_loft = mc.loft(l_crvsRebuilt,uniform = True,degree = 3,ss = 3)[0]
                                mc.delete(l_crvsRebuilt)#Delete the rebuilt curves
                            except Exception,error:raise Exception,"[Reg plate loft |error: {0}]".format(error)	

                        try:#tag, name, store
                            mi_obj = cgmMeta.cgmObject(str_loft)
                            self.__dict__['mi_%sPlate'%(str_name)] = mi_obj
                            mi_obj.addAttr('cgmName',d_buffer.get('name') or str_name,lock=True)
                            try:mi_obj.addAttr('cgmDirection',str_direction ,lock=True)
                            except:pass
                            mi_obj.addAttr('cgmTypeModifier','plate',lock=True)					    
                            mi_obj.doName()
                            mi_go._i_rigNull.connectChildNode(mi_obj,"%sPlate"%str_name,'module')
                        except Exception,error:raise Exception,"[Tag/Name/Store |error: {0}]".format(error)	

                    except Exception,error:raise Exception,"%s | %s"%(str_name,error)	
                    #self.log_infoNestedDict('d_buffer')		    
            except Exception,error:raise Exception,"[Plate |error: {0}]".format(error)
	    
	def _buildTeeth_(self):
	    try:#>> Get some initial data =======================================================================================
		mi_go = self._go#Rig Go instance link
		mi_teethUprRig = self.md_rigList['teethUprRig'][0]
		mi_teethLwrRig = self.md_rigList['teethLwrRig'][0]
		mi_jawRig = self.md_rigList['jawRig'][0]
		mi_constrainNull =  mi_go._i_faceDeformNull
		mPlug_multpHeadScale = mi_go.mPlug_multpHeadScale
    
		str_capAim = mi_go._jointOrientation[0].capitalize()
		str_partName = mi_go._partName
    
	    except Exception,error:raise Exception,"[Info Gather! | error: {0}]".format(error)
    
	    try:#>> Build segment =======================================================================================
		#Create segment	
		mi_teethLwrRig.masterGroup.parent = mi_jawRig
		mi_teethUprRig.masterGroup.parent = mi_constrainNull	
		
	    except Exception,error:raise Exception,"[Parent fail! | error: {0}]".format(error)
    

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
                #mi_jawHandle = self.md_rigList['jawHandle'][0]
                mPlug_multpHeadScale = mi_go.mPlug_multpHeadScale

                str_capAim = mi_go._jointOrientation[0].capitalize()
                str_partName = mi_go._partName
                self.d_buffer['mi_tongueBase'] = mi_tongueBase
                self.d_buffer['mi_tongueTip'] = mi_tongueTip
                self.d_buffer['ml_tongueRig'] = ml_tongueRig
                self.d_buffer['str_capAim'] = str_capAim
                self.d_buffer['mi_jawRig'] = mi_jawRig
                #self.d_buffer['mi_jawHandle'] = mi_jawHandle
                self.d_buffer['mPlug_multpHeadScale'] = mPlug_multpHeadScale

                #self.log_infoNestedDict('d_buffer')
            except Exception,error:raise Exception,"[Info Gather! | error: {0}]".format(error)

            try:#>> Build segment =======================================================================================
                #Create segment	
                mi_tongueBase.masterGroup.parent = mi_jawRig
                mi_tongueTip.masterGroup.parent = mi_jawRig	
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
                except Exception,error:raise Exception,"[post segment query! | error: {0}]".format(error)

                try:#post segmentparent
                    mi_curve.segmentGroup.parent = mi_go._i_rigNull.mNode
                    for attr in 'translate','scale','rotate':
                        cgmMeta.cgmAttr(mi_curve,attr).p_locked = False
                    mi_curve.parent = mi_go._i_rigNull

                    mi_anchorEnd.parent = _str_tipParentBuffer
                    mi_anchorStart.parent = _str_baseParentBuffer

                except Exception,error:raise Exception,"[post segment parent! | error: {0}]".format(error)

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
            except Exception,error:raise Exception,"[cgmSegment creation! | error: {0}]".format(error)
	    
	    try:#Set up some defaults
		#===================================================================================		
		mPlug_tipFollow = cgmMeta.cgmAttr(mi_tongueTip,'followRoot')
		mPlug_tipFollow.p_defaultValue = 1
		mPlug_tipFollow.value = 1	
			
		#for mCtrl in mi_tongueBase,mi_tongueTip:
		    #attributes.doSetLockHideKeyableAttr(mCtrl.mNode,lock= False, visible=True, keyable=True, channels = ['sx','sy','sz'])
		    
	    except StandardError,error:
		raise StandardError,"failed to setup defaults | %s"%(error)	   
	    
            try:#>>>Connect master scale
                mi_distanceBuffer = mi_curve.scaleBuffer		
                cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn(mPlug_multpHeadScale.p_combinedShortName)    
            except Exception,error:raise Exception,"[segment scale connect! | error: {0}]".format(error)

            try:#Do a few attribute connections
                #Push squash and stretch multipliers to cog
                try:
                    for k in mi_distanceBuffer.d_indexToAttr.keys():
                        attrName = 'scaleMult_%s'%k
                        cgmMeta.cgmAttr(mi_distanceBuffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_tongueTip.mNode,attrName,connectSourceToTarget = True)
                        cgmMeta.cgmAttr(mi_tongueTip.mNode,attrName,defaultValue = 1)
                        cgmMeta.cgmAttr('cog_anim',attrName, keyable =True, lock = False)    
                except Exception,error:raise Exception,"[scaleMult transfer! | error: {0}]".format(error)

                cgmMeta.cgmAttr(mi_curve,'twistType').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
                cgmMeta.cgmAttr(mi_curve,'twistExtendToEnd').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
                cgmMeta.cgmAttr(mi_curve,'scaleMidUp').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)
                cgmMeta.cgmAttr(mi_curve,'scaleMidOut').doCopyTo(mi_tongueTip.mNode,connectSourceToTarget=True)

            except Exception,error:raise Exception,"[segment attribute transfer! | error: {0}]".format(error)


            try:#>>DynParent ====================================================================================
                ml_tongueDynParents = [mi_jawRig,
		                       self.md_rigList['teethUprRig'][0],
		                       self._go._mi_parentHeadHandle,
		                       self._go._i_masterControl]		    
                self.log_info("Dynamic parents to add: %s"%([i_obj.getShortName() for i_obj in ml_tongueDynParents]))

                #Add our parents
                mi_dynGroup = mi_tongueTip.dynParentGroup
                mi_dynGroup.dynMode = 0

                for o in ml_tongueDynParents:
                    mi_dynGroup.addDynParent(o)
                mi_dynGroup.rebuild()

            except Exception,error:raise Exception,"[DynParent fail!] | error: {0}".format(error)


        def _buildNose_(self):
            #>> Get some data =======================================================================================
            try:#>> Query ========================================================================
                mi_go = self._go#Rig Go instance link	
                if not self.md_rigList.get('chinTrackLoc'):
                    raise RuntimeError,"Mouth handles step necessary to build nose"		
                if not self.md_rigList.get('sneerHandleInfluenceJoints'):
                    raise RuntimeError,"Smile line must be rigged to build nose"
            except Exception,error:raise Exception,"[Query] | error: {0}".format(error)

            try:#Build Ribbons --------------------------------------------------------------------------------------
                md_ribbonBuilds = {'nostril':{'extrudeCrv':self.mi_noseBaseCastCrv,
                                              'joints':self.md_rigList['sneerHandle']['left'] + self.md_rigList['sneerHandle']['right']}}	
                
                #self.create_ribbonsFromDict(md_ribbonBuilds)
		faceUtils.create_ribbonsFromDict(self,md_ribbonBuilds)
		
            except Exception,error:raise Exception,"[Ribbons! | error: {0}]".format(error)

            try:#Build plates --------------------------------------------------------------------------------------
                md_plateBuilds = {'nose':{'crvs':[self.mi_noseTopCastCrv,self.mi_noseMidCastCrv,self.mi_noseBaseCastCrv,self.mi_mouthTopCastCrv]}}
		faceUtils.create_plateFromDict(self,md_plateBuilds)
		
            except Exception,error:raise Exception,"[Plates! | error: {0}]".format(error)

            try:#Special Locs --------------------------------------------------------------------------------------
                try:#Make a noseMove track loc
                    mi_noseMoveTrackLoc = self.md_rigList['noseMoveHandle'][0].doLoc()
                    i_masterGroup = (cgmMeta.asMeta(mi_noseMoveTrackLoc.doGroup(True),'cgmObject',setClass=True))
                    i_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
                    i_masterGroup.doName()
                    mi_noseMoveTrackLoc.connectChildNode(i_masterGroup,'masterGroup','groupChild')
                    self.md_rigList['noseMoveTrackLoc'] = [mi_noseMoveTrackLoc]
                    mi_go.connect_toRigGutsVis(mi_noseMoveTrackLoc,vis = 1, doShapes = True)#connect to guts vis switches

                    i_masterGroup.parent = mi_go._i_deformNull
                except Exception,error:raise Exception,"[NoseMove master group find fail |error: {0}]".format(error)

                try:str_noseMoveTrackerMasterGroup = self.md_rigList['noseMoveTrackLoc'][0].masterGroup.p_nameShort
                except Exception,error:raise Exception,"[NoseMoveTrack master group find fail | error: {0}]".format(error)

            except Exception,error:raise Exception,"[Special Locs!] | error: {0}".format(error)	    

            try:#Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
                str_nosePlate = self.mi_nosePlate.p_nameShort
                str_nostrilRibbon = self.mi_nostrilRibbon.p_nameShort	    
                try:str_noseMoveMasterGroup = self.md_rigList['noseMoveRig'][0].masterGroup.p_nameShort
                except Exception,error:raise Exception,"[NoseMove master group find fail |error: {0}]".format(error)

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
                           'sneerHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_noseMoveTrackLoc},                           
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
		faceUtils.attach_fromDict(self,d_build)
		
            except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error)

            try:#Build Ribbons --------------------------------------------------------------------------------------
                md_ribbonBuilds = {'nostril':{'extrudeCrv':self.mi_noseBaseCastCrv,
                                              'joints':self.md_rigList['sneerHandle']['left'] + self.md_rigList['sneerHandle']['right']}}	
		faceUtils.create_ribbonsFromDict(self,md_ribbonBuilds)
		
            except Exception,error:raise Exception,"[Ribbons! | error: {0}]".format(error)
	    '''
            try:#Build plates --------------------------------------------------------------------------------------
                md_plateBuilds = {'nose':{'crvs':[self.mi_noseTopCastCrv,self.mi_noseMidCastCrv,self.mi_noseBaseCastCrv,self.mi_mouthTopCastCrv]}}
                #self.create_plateFromDict(md_plateBuilds)
		faceUtils.create_plateFromDict(self,md_plateBuilds)
		
            except Exception,error:raise Exception,"[Plates! | error: {0}]".format(error)	 
	    '''
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
                except Exception,error:raise Exception,"[build list |error: {0}]".format(error)

                ret_cluster = mc.skinCluster(l_toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
                i_cluster = cgmMeta.asMeta(ret_cluster[0],'cgmNode',setClass=True)
                i_cluster.doStore('cgmName',str_nosePlate)
                i_cluster.doName()

            except Exception,error:raise Exception,"[Skin nose plate| error: {0}]".format(error)		

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
                except Exception,error:raise Exception,"[build list |error: {0}]".format(error)

                ret_cluster = mc.skinCluster(l_toBind, tsb = True, normalizeWeights = True, mi = 4, dr = 5)
                i_cluster = cgmMeta.asMeta(ret_cluster[0],'cgmNode',setClass=True)
                i_cluster.doStore('cgmName',str_nostrilRibbon)
                i_cluster.doName()

            except Exception,error:raise Exception,"[Skin nostril plate! | error: {0}]".format(error)	


            try:#>> Connect rig joints to handles ====================================================
                mi_go = self._go#Rig Go instance link
                d_build = {#'noseMove':{},
                           'noseUnderHandle':{'mode':'pointBlend','targets':[mi_noseMoveTrackLoc]},		           
                           'noseMoveTrackLoc':{'driver':self.md_rigList['noseMoveHandle']}}
		faceUtils.connect_fromDict(self,d_build)

                try:#>> Connect corners
                    for str_direction in 'left','right':
                        mi_jnt = self.md_rigList['nostrilRig'][str_direction][0]
                        mi_controlLoc = self.md_attachReturns[mi_jnt]['controlLoc']
                        mi_controlLoc.parent = self.md_rigList['sneerHandleInfluenceJoints'][str_direction][0]
                except Exception,error:raise Exception,"[Connect Corners] | error: {0}".format(error)	

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
                        except Exception,error:raise Exception,"[Query]{ %s}"%(error)			

                        try:#Connect the control loc to the center handle
                            mi_controlLoc = self.md_attachReturns[mi_rigJoint]['controlLoc']
                            mc.pointConstraint(mi_handle.mNode,mi_controlLoc.mNode)
                        except Exception,error:raise Exception,"[Control loc connec] | error: {0}".format(error)			

                        try:#Setup the offset to push handle rotation to the rig joint control
                            #Create offsetgroup for the mid
                            mi_offsetGroup = cgmMeta.asMeta( mi_rigJoint.doGroup(True),'cgmObject',setClass=True)	 
                            mi_offsetGroup.doStore('cgmName',mi_rigJoint.mNode)
                            mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
                            mi_offsetGroup.doName()
                            mi_rigJoint.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    

                            cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
                        except Exception,error:raise Exception,"[Offset group] | error: {0}".format(error)
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
		except Exception,error:raise Exception,"[Control loc connec]{ %s}"%(error)	

		try:#Setup the offset to push handle rotation to the rig joint control
		    #Create offsetgroup for the mid
		    mi_offsetGroup = cgmMeta.cgmObject( mi_rigJoint.doGroup(True),setClass=True)	 
		    mi_offsetGroup.doStore('cgmName',mi_rigJoint.mNode)
		    mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
		    mi_offsetGroup.doName()
		    mi_rigJoint.connectChildNode(mi_offsetGroup,'offsetGroup','groupChild')		    
		    cgmMeta.cgmAttr(mi_offsetGroup,'rotate').doConnectIn("%s.rotate"%(mi_handle.mNode))
		except Exception,error:raise Exception,"[Offset grou]{ %s}"%(error)
	    except Exception,error:raise Exception,"[Nose Move setup] | error: {0}".format(error)
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
            except Exception,error:raise Exception,"[Nose Move Up Loc] | error: {0}".format(error)

            try:#>>> Aim some stuff =================================================================================
		'''
		'noseUnderRig':{'mode':'singleTarget','v_aim':mi_go._vectorUpNegative,'v_up':mi_go._vectorAim,
                                           'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseUnderTarget},
		'''
                #mi_noseUnderTarget = self.md_rigList.get('lipUprHandle').get('center')[0]
                mi_noseUnderTarget = self.md_rigList.get('mouthMove')[0]		
                d_build = {'noseTopRig':{'mode':'singleTarget','v_aim':mi_go._vectorUpNegative,'v_up':mi_go._vectorAim,
                                         'upLoc':mi_noseMoveUpLoc,'aimTarget':mi_noseMove}}		           
                self.d_buffer = d_build
		faceUtils.aim_fromDict(self,d_build)
		
            except Exception,error:raise Exception,"[Aim Setup] | error: {0}]".format(error)

        def _buildMouthHandles_(self):
            try:#>> Query ========================================================================
                mi_go = self._go#Rig Go instance link	
                mi_mouthMove = self.md_rigList['mouthMove'][0]
            except Exception,error:raise Exception,"[Query] | error: {0}]".format(error)

            try:#Special Locs ====================================================================================
                try:#Make a mouthMove track loc ====================================================================================
                    mi_mouthMoveTrackLoc = self.md_rigList['mouthMove'][0].doLoc()
                    mi_mouthMoveTrackLoc.addAttr('cgmTypeModifier','track',lock=True)
                    mi_mouthMoveTrackLoc.doName()		

                    mi_masterGroup = (cgmMeta.asMeta(mi_mouthMoveTrackLoc.doGroup(True),'cgmObject',setClass=True))
                    mi_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
                    mi_masterGroup.doName()
                    mi_mouthMoveTrackLoc.connectChildNode(mi_masterGroup,'masterGroup','groupChild')
                    self.md_rigList['mouthMoveTrackLoc'] = [mi_mouthMoveTrackLoc]
                    mi_go.connect_toRigGutsVis(mi_mouthMoveTrackLoc,vis = 1, doShapes = True)#connect to guts vis switches
                    mi_masterGroup.parent = mi_go._i_deformNull
                except Exception,error:raise Exception,"[MouthMove loc| error: {0}]".format(error)

                try:str_mouthMoveTrackerMasterGroup = self.md_rigList['mouthMoveTrackLoc'][0].masterGroup.p_nameShort
                except Exception,error:raise Exception,"[MouthMoveTrack master group find fail | error: {0}]".format(error)

                try:#Make a mouthMove track loc ====================================================================================
                    mi_mouthMoveJawTrackLoc = self.md_rigList['mouthMove'][0].doLoc()
                    mi_mouthMoveJawTrackLoc.addAttr('cgmTypeModifier','trackJaw',lock=True)
                    mi_mouthMoveJawTrackLoc.doName()		

                    mi_masterGroup = (cgmMeta.asMeta(mi_mouthMoveJawTrackLoc.doGroup(True),'cgmObject',setClass=True))
                    mi_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
                    mi_masterGroup.doName()
                    mi_mouthMoveJawTrackLoc.connectChildNode(mi_masterGroup,'masterGroup','groupChild')
                    self.md_rigList['mouthMoveJawTrackLoc'] = [mi_mouthMoveJawTrackLoc]
                    mi_go.connect_toRigGutsVis(mi_mouthMoveJawTrackLoc,vis = 1, doShapes = True)#connect to guts vis switches
                    mi_masterGroup.parent = mi_go._i_deformNull
                except Exception,error:raise Exception,"[MouthMove loc| error: {0}]".format(error)

                try:str_mouthMoveJawTrackerMasterGroup = self.md_rigList['mouthMoveJawTrackLoc'][0].masterGroup.p_nameShort
                except Exception,error:raise Exception,"[MouthMoveTrack master group find fail | error: {0}]".format(error)					

                try:#Make a chin track loc
                    mi_chinTrackLoc = self.md_rigList['chin'][0].doLoc()
                    mi_chinTrackLoc.addAttr('cgmTypeModifier','track',lock=True)
                    mi_chinTrackLoc.doName()		

                    mi_masterGroup = (cgmMeta.asMeta(mi_chinTrackLoc.doGroup(True),'cgmObject',setClass=True))
                    mi_masterGroup.addAttr('cgmTypeModifier','master',lock=True)
                    mi_masterGroup.doName()
                    mi_chinTrackLoc.connectChildNode(mi_masterGroup,'masterGroup','groupChild')
                    self.md_rigList['chinTrackLoc'] = [mi_chinTrackLoc]

                    mi_go.connect_toRigGutsVis(mi_chinTrackLoc,vis = True)#connect to guts vis switches
                    mi_masterGroup.parent = mi_go._i_deformNull
                except Exception,error:raise Exception,"[ChinTrack master group find fail |error: {0}]".format(error)

                try:str_chinTrackerMasterGroup = self.md_rigList['chinTrackLoc'][0].masterGroup.p_nameShort
                except Exception,error:raise Exception,"[ChinTrack master group find fail |error: {0}]".format(error)			
            except Exception,error:raise Exception,"[Special Locs! | error: {0}]".format(error)

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
                           'lipCornerRig':{'mode':'blendAttach','defaultValue':.5,'followSuffix':'Jaw','connectFollicleOffset':True,
                                           'left':{'mode':'blendAttach','attachTo':[mi_uprTeethPlate,mi_lwrTeethPlate],
                                                   'drivers':[self.md_rigList['lipCornerHandle']['left'][0],self.md_rigList['lipCornerHandle']['left'][0]],
                                                   'controlObj':self.md_rigList['lipCornerHandle']['left'][0]},
                                           'right':{'mode':'blendAttach','attachTo':[mi_uprTeethPlate,mi_lwrTeethPlate],
                                                    'drivers':[self.md_rigList['lipCornerHandle']['right'][0],self.md_rigList['lipCornerHandle']['right'][0]],
                                                    'controlObj':self.md_rigList['lipCornerHandle']['right'][0]}},		           
                           'lipCornerHandle':{'mode':'blendAttach','defaultValue':.5,'followSuffix':'Jaw',
                                              'drivers':[mi_mouthMoveTrackLoc,mi_mouthMoveJawTrackLoc],'attachTo':[mi_uprTeethPlate,mi_lwrTeethPlate]},
                           'lipUprHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveTrackLoc.mNode,#...non  center handles
                                           'center':{'mode':'slideHandleAttach','attachTo':mi_uprTeethPlate}},			           
                           'lipLwrHandle':{'mode':'parentOnly','attachTo':None,'parentTo':mi_mouthMoveJawTrackLoc.mNode,#...non  center handles
                                           'center':{'mode':'slideHandleAttach','attachTo':mi_lwrTeethPlate}},	           		           		           
                           }				
                #self.attach_fromDict(d_build)
		faceUtils.attach_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error)

            try:#>>> Connect rig joints to handles ==================================================================
                d_build = {'mouthMoveTrackLoc':{'driver':self.md_rigList['mouthMove']},
                           'chinTrackLoc':{'driver':self.md_rigList['chin']},
                           #'lipCornerHandle':{'driver':self.md_rigList['mouthMove']},
                           'lipCornerHandle':{'mode':'attrOffsetConnect','driver':self.md_rigList['mouthMove'],'attrsToConnect':['tz'],
                                              'right':{'attrsToMirror':['tz']}},
                           'lipCornerRig':{'mode':'attrOffsetFactorConnect','attrName':'mouthMoveFactor',
		                           'driver':self.md_rigList['mouthMove'],'attrsToConnect':["t%s"%mi_go._jointOrientation[0]],
                                           'right':{'attrsToMirror':["t%s"%mi_go._jointOrientation[0]]}},
                           'smileHandle':{'mode':'smileHandleOffset',
                                          'left':{'driver':self.md_rigList['lipCornerHandle']['left'][0],'attrsToConnect':['tx','tz']},
                                          'right':{'driver':self.md_rigList['lipCornerHandle']['right'][0],'attrsToConnect':['tx','tz']}},                            
                           'lipLwrHandle':{'skip':['left','right'],
                                           'center':{'mode':'simpleSlideHandle','driver':self.md_rigList['mouthMove']}},
                           'lipUprHandle':{'skip':['left','right'],
                                           'center':{'mode':'simpleSlideHandle','driver':self.md_rigList['mouthMove']}},		           
                           }
                #self.connect_fromDict(d_build)
		faceUtils.connect_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Connect!] | error: {0}]".format(error)
            
            try:#>> UprLip Center follow  =======================================================================================
                mObj = self.md_rigList['lipUprHandle']['center'][0]
                mi_offsetGroup = cgmMeta.asMeta(mObj.doGroup(True),'cgmObject',setClass=True)
                mi_offsetGroup.doStore('cgmName',mObj.mNode)
                mi_offsetGroup.addAttr('cgmTypeModifier','offset',lock=True)
                mi_offsetGroup.doName()
                mObj.connectChildNode(mi_offsetGroup,"offsetGroup","childObject")
            except Exception,error:raise Exception,"[Center upr lip offsetgroup! | error: {0}]".format(error)

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

                d_build = {'lipUprHandle':{'mode':'singleBlend','upLoc':mi_mouthMoveUpLoc,'skip':['left','right'],
                                           'center':{'offsetGroup':mi_offsetGroup,
                                                     'd_target0':{'target':self.md_rigList['lipCornerHandle']['left'][0],
                                                                  'v_aim':mi_go._vectorOut,'v_up':mi_go._vectorAim},
                                                     'd_target1':{'target':self.md_rigList['lipCornerHandle']['right'][0],
                                                                  'v_aim':mi_go._vectorOutNegative,'v_up':mi_go._vectorAim}}}}
                faceUtils.aim_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Aim! | error: {0}]".format(error)	

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

                    mi_offsetGroup = cgmMeta.asMeta(mi_obj.doGroup(True),'cgmObject',setClass=True)
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
            except Exception,error:raise Exception,"[constrain mids! | error: {0}]".format(error)	

        def _buildLipStructure_(self):
            #>> Get some data =======================================================================================
            try:#>> Query ========================================================================
                mi_go = self._go#Rig Go instance link	
            except Exception,error:raise Exception,"[Query | error: {0}]".format(error)  

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
                        except Exception,error:raise Exception,"[Query] | error: {0}".format(error)  

                        try:#>> Progress -----------------------------------------------------------------------
                            str_message = "'%s' | Setting up tigtener"%(str_k)
                            self.log_info(str_message)
                            self.progressBar_set(status = str_message, progress = i, maxValue = int_lenMax)				    
                        except Exception,error:raise Exception,"[Progress bar] | error: {0}".format(error)  			    

                        try:#>> Up locs -----------------------------------------------------------------------
                            mi_upLoc = mi_rigJoint.doLoc()
                            mi_upLoc.parent = mi_rigJoint
                            mi_go.connect_toRigGutsVis(mi_upLoc)
                        except Exception,error:raise Exception,"[Up locs ] | error: {0}".format(error)  	

                        try:#>> Get Plugs -----------------------------------------------------------------------
                            self.log_info("'%s' | Setting up plugs"%(str_k))			    
                            mPlug_tightenUpr =  cgmMeta.cgmAttr(mi_handle,'tightenUpr', value= 0.0, attrType='float', defaultValue= 0.0,keyable=True, hidden=False)
                            mPlug_tightenLwr =  cgmMeta.cgmAttr(mi_handle,'tightenLwr', value= 0.0, attrType='float', defaultValue= 0.0,keyable=True, hidden=False)
                        except Exception,error:raise Exception,"[Plugs] | error: {0}".format(error)  

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

                            except Exception,error:raise Exception,"[Vector query!] | error: {0}".format(error)

                            for i,mDriver in enumerate([mi_uprDriver,mi_lwrDriver]):
                                try:#For loop

                                    if i == 0:
                                        mi_target = self.md_rigList['lipUprHandle']['center'][0]
                                    else:
                                        mi_target = self.md_rigList['lipLwrHandle']['center'][0]

                                    #Make a group
                                    mi_aimOffsetGroup = cgmMeta.asMeta(mDriver.doGroup(True),'cgmObject',setClass=True)
                                    mi_aimOffsetGroup.doStore('cgmName',mDriver.mNode)
                                    mi_aimOffsetGroup.addAttr('cgmTypeModifier','aimOffset',lock=True)
                                    mi_aimOffsetGroup.doName()
                                    mDriver.connectChildNode(mi_aimOffsetGroup,"aimOffsetGroup","childObject")

                                    mc.aimConstraint(mi_target.mNode, mi_aimOffsetGroup.mNode,
                                                     weight = 1, aimVector = v_aim, upVector = v_up,
                                                     maintainOffset = 1, worldUpObject = mi_upLoc.mNode, worldUpType = 'object' ) 
                                except Exception,error:raise Exception,"[Driver loop : '%s']{%s}"%(mDriver.p_nameShort,error)
                        except Exception,error:raise Exception,"[Aim setup] | error: {0}".format(error)

                        try:#>> offset rot -----------------------------------------------------------------------
                            for i,mDriver in enumerate([mi_uprDriver,mi_lwrDriver]):
                                try:#For loop
                                    #Make a group
                                    mi_rotOffsetGroup = cgmMeta.asMeta(mDriver.doGroup(True),'cgmObject',setClass=True)
                                    mi_rotOffsetGroup.doStore('cgmName',mDriver.mNode)
                                    mi_rotOffsetGroup.addAttr('cgmTypeModifier','rotOffset',lock=True)
                                    mi_rotOffsetGroup.doName()
                                    mDriver.connectChildNode(mi_rotOffsetGroup,"rotOffsetGroup","childObject")

                                    #Connect
                                    cgmMeta.cgmAttr(mi_rotOffsetGroup,'r%s'%mi_go._jointOrientation[2]).doConnectIn("%s.r%s"%(mi_handle.mNode,mi_go._jointOrientation[0]))

                                except Exception,error:raise Exception,"[Driver loop : '%s']{%s}"%(mDriver.p_nameShort,error)			    

                        except Exception,error:raise Exception,"[OffsetRot] | error: {0}".format(error) 			
                    except Exception,error:raise Exception,"[On: '%s']{%s}"%(str_k,error) 
            except Exception,error:raise Exception,"[Lip Tigteners | error: {0}]".format(error)  

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

                    #Links
                    self.ml_uprLipRigJoints = ml_uprLipRigJoints
                    self.ml_lwrLipRigJoints = ml_lwrLipRigJoints
                    self.ml_uprLipHandles = ml_uprLipHandles
                    self.ml_lwrLipHandles = ml_lwrLipHandles

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
                        mi_uprDrivenCrv = cgmMeta.asMeta(_str_uprDrivenCurve,'cgmObject',setClass=True)
                        mi_uprDrivenCrv.addAttr('cgmName','uprLip',lock=True)
                        mi_uprDrivenCrv.addAttr('cgmTypeModifier','driven',lock=True)
                        mi_uprDrivenCrv.doName()
                        ml_curves.append(mi_uprDrivenCrv)

                        mi_uprLipSealCrv = mi_uprDrivenCrv.doDuplicate(po = False)
                        mi_uprLipSealCrv.addAttr('cgmTypeModifier','lipSeal',lock=True)
                        mi_uprLipSealCrv.doName()
                        ml_curves.append(mi_uprLipSealCrv)
                    except Exception,error:raise Exception,"[upper driven curve!] | error: {0}".format(error)  	    

                    try:#Upper driver curve
                        _str_uprDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_uprLipHandles],os =True)
                        mi_uprDriverCrv = cgmMeta.asMeta(_str_uprDriverCurve,'cgmObject',setClass=True)
                        mi_uprDriverCrv.doCopyNameTagsFromObject(mi_uprDrivenCrv.mNode,ignore=['cgmTypeModifier'])
                        mi_uprDriverCrv.addAttr('cgmTypeModifier','driver',lock=True)
                        mi_uprDriverCrv.doName()
                        ml_curves.append(mi_uprDriverCrv)	    
                    except Exception,error:raise Exception,"[upper driver curve!] | error: {0}".format(error)  	    

                    try:#Lwr driven curve
                        _str_lwrDrivenCurve = mc.curve(d=3,ep=[mi_obj.getPosition() for mi_obj in self.md_rigList['lipCornerRig']['left'] + ml_lwrLipRigJoints + self.md_rigList['lipCornerRig']['right']],os =True)
                        mi_lwrDrivenCrv = cgmMeta.asMeta(_str_lwrDrivenCurve,'cgmObject',setClass=True)
                        mi_lwrDrivenCrv.doCopyNameTagsFromObject(mi_uprDrivenCrv.mNode)
                        mi_lwrDrivenCrv.addAttr('cgmName','lwrLip',lock=True)	    
                        mi_lwrDrivenCrv.doName()
                        ml_curves.append(mi_lwrDrivenCrv)	

                        mi_lwrLipSealCrv = mi_lwrDrivenCrv.doDuplicate(po = False)
                        mi_lwrLipSealCrv.addAttr('cgmTypeModifier','lipSeal',lock=True)
                        mi_lwrLipSealCrv.doName()
                        ml_curves.append(mi_lwrLipSealCrv)
                    except Exception,error:raise Exception,"[upper driven curve!] | error: {0}".format(error)  	    

                    try:#Lwr driver curve
                        _str_lwrDriverCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_lwrLipHandles],os =True)
                        mi_lwrDriverCrv = cgmMeta.asMeta(_str_lwrDriverCurve,'cgmObject',setClass=True)
                        mi_lwrDriverCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
                        mi_lwrDriverCrv.addAttr('cgmName','lwrLip',lock=True)	    
                        mi_lwrDriverCrv.doName()
                        ml_curves.append(mi_lwrDriverCrv)	    	    	    
                    except Exception,error:raise Exception,"[upper driver curve!] | error: {0}".format(error)  	    

                    try:#SmartLipSeal curve
                        _str_smartLipSealCurve = mc.curve(d=1,ep=[mi_obj.getPosition() for mi_obj in ml_lwrLipHandles],os =True)
                        mi_smartLipSealCrv = cgmMeta.asMeta(_str_smartLipSealCurve,'cgmObject',setClass=True)
                        mi_smartLipSealCrv.doCopyNameTagsFromObject(mi_uprDriverCrv.mNode)
                        mi_smartLipSealCrv.addAttr('cgmName','smartLipSeal',lock=True)	    
                        mi_smartLipSealCrv.doName()
                        ml_curves.append(mi_smartLipSealCrv)	    	    	    
                    except Exception,error:raise Exception,"[smartLipSeal curve] | error: {0}".format(error)  

                    try:
                        for mi_crv in ml_curves:#Parent to rig null
                            mi_crv.parent = mi_go._i_rigNull#used to be deformNull

                        #for mi_crv in [mi_smartLipSealCrv,mi_lwrLipSealCrv,mi_uprLipSealCrv]:
                            #mi_crv.parent = mi_go._i_rigNull

                    except Exception,error:raise Exception,"[Curve parenting] | error: {0}".format(error)  
                except Exception,error:raise Exception,"[Curve creation] | error: {0}".format(error)   


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
                        except Exception,error:raise Exception,"[loc creation] | error: {0}".format(error)  	    
                        #> Aim constraint
                        #mi_root = mi_obj.root
                        #mi_root.parent = self._i_constrainNull
                        #try:mc.aimConstraint(mi_loc.mNode,mi_root.mNode,maintainOffset = False, weight = 1, aimVector = v_aim, upVector = v_up, worldUpVector = [0,1,0], worldUpObject = mi_upLoc.mNode, worldUpType = 'object' )
                        #except Exception,error:raise Exception,"[aim constrai]{%s}%s"%(error)  	    
                        #Attach to curve
                        if i < len(ml_uprLipRigJoints):mi_crv = mi_uprDrivenCrv
                        else:mi_crv = mi_lwrDrivenCrv
                        try:crvUtils.attachObjToCurve(mi_loc.mNode,mi_crv.mNode)
                        except Exception,error:raise Exception," attach| %s "%(error)  	    
                        self.md_attachReturns[mObj] = {'posLoc':mi_loc,'posLocShape':mi_locShape}#store it
                    except Exception,error:raise Exception,"%s | '%s' loc setup | %s "%(i,mi_obj.p_nameShort,error)  	    
        
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
                        try:
                            attributes.doSetAttr(mi_uprWire.mNode,"dropoffDistance[0]",50)
                            attributes.doSetAttr(mi_lwrWire.mNode,"dropoffDistance[0]",50)
                            attributes.doSetAttr(mi_uprWire.mNode,"scale[0]",0)#...this get's rid of some weird scale stuff...
                            attributes.doSetAttr(mi_lwrWire.mNode,"scale[0]",0)                            
                        except Exception,error:raise Exception,"[Failed to set dropoffDistance] | error:{0}".format(error)			
                    except Exception,error:raise Exception,"[wire deformer!] | error: {0}".format(error)  	    

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
                            except Exception,error:raise Exception,"skinCluster] | error: {0}".format(error)  	    
                            d_crv['mi_skinNode'] = mi_skinNode
                    except Exception,error:raise Exception,"[skinning drive]{%s}s"%(error)  	    

                    try:#Blendshape the smart lipSeal curve ---------------------------------------------
                        self.progressBar_set(status = 'Smart Seal - Blendshape...')

                        _str_bsNode = mc.blendShape([mi_uprDriverCrv.mNode,mi_lwrDriverCrv.mNode],mi_smartLipSealCrv.mNode)[0]
                        mi_bsNode = cgmMeta.asMeta(_str_bsNode,'cgmNode',setClass=True)
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
                    except Exception,error:raise Exception,"[smartLipSeal bsNod]{%s}s"%(error)  	

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
                        try:
                            attributes.doSetAttr(mi_uprLipSealWire.mNode,"dropoffDistance[0]",50)
                            attributes.doSetAttr(mi_lwrLipSealWire.mNode,"dropoffDistance[0]",50)
                        except Exception,error:raise Exception,"[Failed to set dropoffDistance] | error:{0}".format(error)			
                    except Exception,error:raise Exception,"[lipSeal target wire]{%s}s"%(error)  	

                    try:#Blendshape the upr and lwr curves to smart lipSeal targets------------------------------------
                        mPlug_lipSeal = cgmMeta.cgmAttr(mi_sealAttrHolder,'lipSeal',attrType = 'float', keyable=True, minValue=0, maxValue=1, defaultValue=0)
                        d_blendshapeLipSeal = {'upr':{'mi_target':mi_uprLipSealCrv,'mi_driven':mi_uprDrivenCrv},
                                               'lwr':{'mi_target':mi_lwrLipSealCrv,'mi_driven':mi_lwrDrivenCrv}}
                        for k in d_blendshapeLipSeal.keys():
                            d_buffer = d_blendshapeLipSeal[k]
                            mi_target = d_buffer['mi_target']
                            mi_driven = d_buffer['mi_driven']
                            _str_bsNode = mc.blendShape(mi_target.mNode,mi_driven.mNode)[0]
                            mi_bsNode = cgmMeta.asMeta(_str_bsNode,'cgmNode',setClass=True)
                            mi_bsNode.doStore('cgmName',mi_uprDrivenCrv.mNode)
                            mi_bsNode.doName()
                            l_bsAttrs = deformers.returnBlendShapeAttributes(mi_bsNode.mNode)
                            mPlug_lipSeal.doConnectOut('%s.%s' % (mi_bsNode.mNode,l_bsAttrs[0]))
                    except Exception,error:raise Exception,"[lipSeal setup!]{%s}s"%(error)  	
                except Exception,error:
                    raise StandardError,"[lip setup |error: {0}]".format(error)   	        
            except Exception,error:
                raise StandardError,"[Smart Seal setup fail | error: {0}]".format(error)  

            try:#Reverse curve ====================================
                '''
                Setup driven reverse curve for upr and lower to drive the right side segments
                '''
                d_toDup = {'uprLipDrivenReverse':mi_uprDrivenCrv,
                           'lwrLipDrivenReverse':mi_lwrDrivenCrv}	

                for str_k in d_toDup.iterkeys():
                    mi_dup = cgmMeta.asMeta( mc.duplicate(d_toDup[str_k].mNode,po=False,ic=1,rc=True)[0],'cgmObject',setClass=True )
                    mi_dup.addAttr('cgmTypeModifier','ReverseDriven')
                    mi_dup.doName()

                    mc.reverseCurve(mi_dup.mNode,rpo=True)
                    cgmMeta.cgmAttr(mi_dup,'translate',lock = False, keyable = True)
                    cgmMeta.cgmAttr(mi_dup,'rotate',lock = False, keyable = True)
                    cgmMeta.cgmAttr(mi_dup,'scale',lock = False, keyable = True)
                    #mi_dup.parent = mi_go._i_rigNull

                    ml_curves.append(mi_dup)
                    self.__dict__["mi_%sCrv"%str_k] = mi_dup
            except Exception,error:raise Exception,"[Reverse Curves setup | error: {0}]".format(error)  

            try:#Setup segments ========================================================================
                d_build = {'uprLipSegment':{'orientation':mi_go._jointOrientation,
                                            'left':{'mi_curve':mi_uprDrivenCrv},
                                            'right':{'mi_curve':self.mi_uprLipDrivenReverseCrv}},
                           'lwrLipSegment':{'orientation':mi_go._jointOrientation,
                                            'left':{'mi_curve':mi_lwrDrivenCrv},
                                            'right':{'mi_curve':self.mi_lwrLipDrivenReverseCrv}}}	
		faceUtils.create_segmentfromDict(self,d_build)
            except Exception,error:raise Exception,"[Segments | error: {0}]".format(error)  
            
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
                        except Exception,error:raise Exception,"[Query] | error: {0}".format(error)  

                        try:#>> Progress -----------------------------------------------------------------------
                            str_message = "'%s' | Setting up roll"%(str_k)
                            self.log_info(str_message)
                            self.progressBar_set(status = str_message, progress = i, maxValue = int_lenMax)				    
                        except Exception,error:raise Exception,"[Progress bar] | error: {0}".format(error)  			    

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
                                        int_cnt = str_arg.count('%s')	
                                        raise StandardError,"['%s' | arg: %s | given fillers: %s | count: %s]{%s}"%(str_argK,str_arg,len(l_buffer),int_cnt,error)
                                    self.log_info("'%s' | argsToNodes..."%(str_argK))									    
                                    self.log_info("building: %s"%(arg_built))
                                    NodeF.argsToNodes(arg_built).doBuild()				
                                except Exception,error:raise Exception,"['%s' fail]{%s}"%(str_argK,error)  			    
                        except Exception,error:raise Exception,"[Args to nodes] | error: {0}".format(error) 
                        #Process
                    except Exception,error:raise Exception,"['%s' fail]{%s}"%(str_k,error)  	    
            except Exception,error:raise Exception,"[Lip Roll | error: {0}]".format(error)  

            try:#>>> Connect rig joints to handles ==================================================================
                d_build = {'lipUprRig':{'mode':'rigToSegment'},
                           'lipLwrRig':{'mode':'rigToSegment'}}
		faceUtils.connect_fromDict(self,d_build)

            except Exception,error:raise Exception,"[Connect! | error: {0}]".format(error) 
            
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
                        mi_loc = cgmMeta.asMeta( mc.duplicate(ml_locs[0].mNode,po=False,ic=True,rc=True)[0],'cgmObject',setClass=True )
                        mi_loc.parent = mi_go._i_rigNull
                        mi_loc.addAttr('cgmTypeModifier','midLoc')
                        mi_loc.doName()
                    except Exception,error:
                        self.log_error(error)			
                        raise Exception,"[%s | loc create]{%s}"%(str_k,error)	
                    mc.pointConstraint([mLoc.mNode for mLoc in ml_locs],mi_loc.mNode,maintainOffset = False)
                    #self.md_rigList["%sMidUpLoc"%str_k]
                    self.__dict__["mi_{0}MidUpLoc".format(str_k)] = mi_loc
                    #d_return['midUpLoc'] = mi_loc#Push to the attachReturn for later pulling
            except Exception,error:raise Exception,"[Build mid lip Up Locs | error: {0}]".format(error)  

            try:#>>> Aim some stuff =================================================================================
                d_build = {'lipUprRig':{'mode':'lipLineSegmentBlend','midUpLoc':self.mi_uprLipSegmentMidUpLoc,
                                        'centerTargets':[self.md_rigList['uprLipSegment']['left'][-1].mNode,
                                                         self.md_rigList['uprLipSegment']['right'][-1].mNode],
                                        'midHandle':self.md_rigList['lipUprHandle']['center'][0],'v_up':mi_go._vectorUp},
                           'lipLwrRig':{'mode':'lipLineSegmentBlend','midUpLoc':self.mi_lwrLipSegmentMidUpLoc,
                                        'centerTargets':[self.md_rigList['lwrLipSegment']['left'][-1].mNode,
                                                         self.md_rigList['lwrLipSegment']['right'][-1].mNode],                                        
                                        'midHandle':self.md_rigList['lipLwrHandle']['center'][0],'v_up':mi_go._vectorUp}}
		faceUtils.aim_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Aim! | error: {0}]".format(error)
            
        def _buildLipOverUnder_(self):
            #>> Get some data =======================================================================================
            try:#>> Query ========================================================================
                mi_go = self._go#Rig Go instance link	

		md_upr_upLocs = self.md_rigList['specialLocs']['uprLipUpDriver']
		md_overSkinJoints = self.md_rigList['lipOverUnderJnts']['uprLipUpDriver']
		md_lwr_upLocs = self.md_rigList['specialLocs']['lwrLipUpDriver']
		md_underSkinJoints = self.md_rigList['lipOverUnderJnts']['lwrLipUpDriver']
		
            except Exception,error:raise Exception,"[Query | error: {0}]".format(error)  
	    
	    try:#Template Curve duplication ====================================================================================
		self.progressBar_set(status = 'Template Curve duplication')  
		d_toDup = {'mouthTopTrace':self.mi_mouthTopCastCrv,
	                   'mouthBaseTrace':self.mi_mouthLowCastCrv}
		for str_k in d_toDup.iterkeys():
		    mi_dup = cgmMeta.asMeta( mc.duplicate(d_toDup[str_k].mNode,po=False,ic=True,rc=True)[0],'cgmObject',setClass=True )
		    mi_dup.cgmType = 'traceCrv'
		    mi_dup.cgmName = mi_dup.cgmName.replace('Cast','')
		    mi_dup.doName()
		    cgmMeta.cgmAttr(mi_dup,'translate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'rotate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'scale',lock = False, keyable = True)
		    mi_dup.parent = mi_go._i_rigNull

		    #ml_curves.append(mi_dup)
		    self.__dict__["mi_{0}Crv".format(str_k)] = mi_dup

	    except Exception,error:raise Exception,"[Template Curve | error: {0}]".format(error)  

	    try:#Build plates ====================================================================================
		md_plateBuilds = {'uprLip':{'crvs':[self.mi_mouthTopCastCrv,self.mi_lipOverTraceCrv,self.mi_lipUprCrv]},
	                          'lwrLip':{'crvs':[self.mi_lipLwrCrv,self.mi_lipUnderTraceCrv,self.mi_mouthLowCastCrv]},}
		faceUtils.create_plateFromDict(self,md_plateBuilds)
	    except Exception,error:raise Exception,"[Plates | error: {0}]".format(error)  	    

	    try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		'''
		d_build = {'uprLipPlate':{'target':self.mi_uprLipPlate,
	                                  'bindJoints': [self.md_rigList['lipCornerRig']['left'][0].uprDriverSkin,
	                                                 md_overSkinJoints['center'][0],md_overSkinJoints['left'][0],
	                                                 md_overSkinJoints['right'][0],self.md_rigList['lipCornerRig']['right'][0].uprDriverSkin] + self.ml_uprLipRigJoints},		           	          
	                   'lwrLipPlate':{'target':self.mi_lwrLipPlate,
	                                  'bindJoints':[self.md_rigList['lipCornerRig']['left'][0].lwrDriverSkin,
	                                                 md_underSkinJoints['center'][0],md_underSkinJoints['left'][0],
	                                                 md_underSkinJoints['right'][0],self.md_rigList['lipCornerRig']['right'][0].lwrDriverSkin] + self.ml_lwrLipRigJoints}}
		
		'''
		d_build = {'uprLipPlate':{'target':self.mi_uprLipPlate,
	                                  'bindJoints': [md_overSkinJoints['center'][0],md_overSkinJoints['left'][0],
	                                                 md_overSkinJoints['right'][0]] + self.ml_uprLipRigJoints},		           	          
	                   'lwrLipPlate':{'target':self.mi_lwrLipPlate,
	                                  'bindJoints':[md_underSkinJoints['center'][0],md_underSkinJoints['left'][0],
		                                        md_underSkinJoints['right'][0]] + self.ml_lwrLipRigJoints}}
		faceUtils.skin_fromDict(self,d_build)
	    except Exception,error:raise Exception,"[Skinning  | error: {0}]".format(error)    
	    
	    try:#>> Create some surfaceTrack locs =======================================================================================
		'''we need these locs to get some of the lip roll movement into the over under'''
		d_build = {'lipUnderRig':{'mode':'surfTrackLoc','storeCreatedToRigList':True},
		           'lipOverRig':{'mode':'surfTrackLoc','storeCreatedToRigList':True}}
		faceUtils.create_specialLocsFromDict(self,d_build)
	    except Exception,error:raise Exception,"[SurfaceTrack locs  | error: {0}]".format(error)    	    

	    try:#Attach stuff to surfaces ====================================================================================
		str_uprLipPlate = self.mi_uprLipPlate.p_nameShort
		str_lwrLipPlate = self.mi_lwrLipPlate.p_nameShort
		d_build = {'lipOverRig_surfTrackLoc':{'mode':'pointAttach','attachTo':str_uprLipPlate},		           
	                   'lipUnderRig_surfTrackLoc':{'mode':'pointAttach','attachTo':str_lwrLipPlate}}
		faceUtils.attach_fromDict(self,d_build)
		
	    except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error) 

            try:#Contrain some stuff ====================================================================================
		'''
				                                             #self.md_rigList['lipCornerRig']['left'][0],
		                                             #self.md_rigList['uprSmileHandle']['left'][0],
							     self.md_rigList['lipUprHandle']['center'][0],
		'''
		d_build = {'lipOverRig':{'mode':'point',
		                         'center':{'targets':[self.md_rigList['noseUnderRig'][0],
		                                              self.md_rigList['lipOverRig']['center'][0].surfTrackLoc]},                                          
		                         'left':{'targets':[self.md_rigList['lipOverRig']['left'][0].surfTrackLoc,
		                                            self.md_rigList['lipUprHandle']['left'][0],
		                                            self.md_rigList['nostrilRig']['left'][0]]},                                          
		                         'right':{'targets':[self.md_rigList['lipOverRig']['right'][0].surfTrackLoc,
		                                             self.md_rigList['lipUprHandle']['right'][0],
		                                             self.md_rigList['nostrilRig']['right'][0]]}}, 
		           'lipUnderRig':{'mode':'point',
		                          'center':{'targets':[self.md_rigList['lipUnderRig']['center'][0].surfTrackLoc]},                                          
		                          'left':{'targets':[self.md_rigList['lipUnderRig']['left'][0].surfTrackLoc,		                                               		                                             
		                                             self.md_rigList['smileBaseHandle']['left'][0]]},                                          
		                          'right':{'targets':[self.md_rigList['lipUnderRig']['right'][0].surfTrackLoc,		                                               		                                              
		                                              self.md_rigList['smileBaseHandle']['right'][0]]}}}		
		faceUtils.constrain_fromDict(self,d_build)
		
            except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error) 
	    #singleTarget

            try:#>>> Aim some stuff =================================================================================
		'''
				           'lipOverRig':{'mode':'singleBlend',
		                         'center':{'d_target0':{'target':self.md_rigList['noseUnderRig'][0],
		                                                'upLoc':md_upr_upLocs['center'][0],
		                                                'v_aim':mi_go._vectorUp,
		                                                'v_up':mi_go._vectorAim},
		                                   'd_target1':{'target':self.md_rigList['lipUprHandle']['center'][0],
		                                                'upLoc':md_upr_upLocs['center'][0],
		                                                'v_aim':mi_go._vectorUpNegative,
		                                                'v_up':mi_go._vectorAim}},                                          
		                          'left':{'d_target0':{'target':self.md_rigList['nostrilRig']['left'][0],
                                                               'upLoc':md_upr_upLocs['left'][0],
                                                               'v_aim':mi_go._vectorUp,
                                                               'v_up':mi_go._vectorAim},
                                                  'd_target1':{'target':self.md_rigList['lipUprHandle']['left'][0],
                                                               'upLoc':md_upr_upLocs['left'][0],
                                                               'v_aim':mi_go._vectorUpNegative,
                                                               'v_up':mi_go._vectorAim}},
                                          'right':{'d_target0':{'target':self.md_rigList['nostrilRig']['right'][0],
                                                               'upLoc':md_upr_upLocs['right'][0],
                                                               'v_aim':mi_go._vectorUp,
                                                               'v_up':mi_go._vectorAimNegative},
                                                  'd_target1':{'target':self.md_rigList['lipUprHandle']['right'][0],
                                                               'upLoc':md_upr_upLocs['right'][0],
                                                               'v_aim':mi_go._vectorUpNegative,
                                                               'v_up':mi_go._vectorAimNegative}}}}
							       
					    'center':{'d_target0':{'target':self.md_rigList['noseUnderRig'][0],
		                                                'upLoc':md_upr_upLocs['center'][0],
		                                                'v_aim':mi_go._vectorUp,
		                                                'v_up':mi_go._vectorAim},
		                                   'd_target1':{'target':self.md_rigList['lipUprHandle']['center'][0],
		                                                'upLoc':md_upr_upLocs['center'][0],
		                                                'v_aim':mi_go._vectorUpNegative,
		                                                'v_up':mi_go._vectorAim}},  
		
		'lipUnderRig':{'mode':'singleTarget',
		                         'center':{'aimTarget':self.md_rigList['lipLwrHandle']['center'][0],
		                                   'upLoc':md_lwr_upLocs['center'][0],
		                                   'v_aim':mi_go._vectorUp,
		                                   'v_up':mi_go._vectorAim},                                          
		                         'left':{'aimTarget':self.md_rigList['lipUnderRig']['center'][0],
		                                 'upLoc':md_lwr_upLocs['left'][0],
		                                 'v_aim':mi_go._vectorOutNegative,
		                                 'v_up':mi_go._vectorUp},
                                          'right':{'aimTarget':self.md_rigList['lipUnderRig']['center'][0],
		                                   'upLoc':md_lwr_upLocs['right'][0],
		                                   'v_aim':mi_go._vectorOut,
		                                   'v_up':mi_go._vectorUp}},
		'''
                d_build = {'lipUnderRig':{'mode':'singleBlend',
		                          'center':{'d_target0':{'target':self.md_rigList['lipLwrRig']['center'][0],
		                                                 'upLoc':self.md_rigList['lipUnderRig']['right'][0].masterGroup,
		                                                 'v_aim':mi_go._vectorUp,
		                                                 'v_up':mi_go._vectorOutNegative},
		                                    'd_target1':{'target':self.md_rigList['lipLwrRig']['center'][0],
		                                                 'upLoc':self.md_rigList['lipUnderRig']['left'][0].masterGroup,
		                                                 'v_aim':mi_go._vectorUp,
		                                                 'v_up':mi_go._vectorOut}},                                          
		                           'left':{'d_target0':{'target':self.md_rigList['lipUnderRig']['center'][0],
		                                                'upLoc':md_lwr_upLocs['left'][0],
		                                                'v_aim':mi_go._vectorOutNegative,
		                                                'v_up':mi_go._vectorAim},
		                                   'd_target1':{'target':self.md_rigList['lipUnderRig']['center'][0],
		                                                'upLoc':md_lwr_upLocs['left'][0],
		                                                'v_aim':mi_go._vectorOutNegative,
		                                                'v_up':mi_go._vectorAim}},
		                           'right':{'d_target0':{'target':self.md_rigList['lipUnderRig']['center'][0],
		                                                 'upLoc':md_lwr_upLocs['right'][0],
		                                                 'v_aim':mi_go._vectorOut,
		                                                 'v_up':mi_go._vectorAimNegative},
		                                    'd_target1':{'target':self.md_rigList['lipUnderRig']['center'][0],
		                                                 'upLoc':md_lwr_upLocs['right'][0],
		                                                 'v_aim':mi_go._vectorOut,
		                                                 'v_up':mi_go._vectorAimNegative}}},		           
		           'lipOverRig':{'mode':'singleBlend',
		                         'center':{'d_target0':{'target':self.md_rigList['lipOverRig']['left'][0].masterGroup,
		                                                'upLoc':self.md_rigList['lipUprRig']['center'][0],
		                                                'v_aim':mi_go._vectorOut,
		                                                'v_up':mi_go._vectorUpNegative},
		                                   'd_target1':{'target':self.md_rigList['lipOverRig']['right'][0].masterGroup,
		                                                'upLoc':self.md_rigList['lipUprRig']['center'][0],
		                                                'v_aim':mi_go._vectorOutNegative,
		                                                'v_up':mi_go._vectorUpNegative}},                                          
		                          'left':{'d_target0':{'target':self.md_rigList['nostrilRig']['left'][0],
                                                               'upLoc':md_upr_upLocs['left'][0],
                                                               'v_aim':mi_go._vectorUp,
                                                               'v_up':mi_go._vectorAim},
                                                  'd_target1':{'target':self.md_rigList['lipOverRig']['center'][0],
                                                               'upLoc':md_upr_upLocs['left'][0],
                                                               'v_aim':mi_go._vectorOutNegative,
                                                               'v_up':mi_go._vectorAim}},
                                          'right':{'d_target0':{'target':self.md_rigList['nostrilRig']['right'][0],
                                                               'upLoc':md_upr_upLocs['right'][0],
                                                               'v_aim':mi_go._vectorUp,
                                                               'v_up':mi_go._vectorAimNegative},
                                                  'd_target1':{'target':self.md_rigList['lipOverRig']['center'][0],
                                                               'upLoc':md_upr_upLocs['right'][0],
                                                               'v_aim':mi_go._vectorOut,
                                                               'v_up':mi_go._vectorAimNegative}}}}
		faceUtils.aim_fromDict(self,d_build)
		
            except Exception,error:raise Exception,"[Aim! | error: {0}]".format(error)     
	def _buildLipOverUnderOLD_(self):
	    #>> Get some data =======================================================================================
	    try:#>> Query ========================================================================
		mi_go = self._go#Rig Go instance link	
		#mi_uprLipUpLoc = self.md_rigList['specialLocs']['uprLipUpDriver']
		#mi_lwrLipUpLoc = self.md_rigList['specialLocs']['lwrLipUpDriver']

		md_upr_upLocs = self.md_rigList['specialLocs']['uprLipUpDriver']
		md_overSkinJoints = self.md_rigList['lipOverUnderJnts']['uprLipUpDriver']
		md_lwr_upLocs = self.md_rigList['specialLocs']['lwrLipUpDriver']
		md_underSkinJoints = self.md_rigList['lipOverUnderJnts']['lwrLipUpDriver']
		
		#self.md_rigList['specialLocs']['uprLipUpDriver']['left']		
	    except Exception,error:raise Exception,"[Query | error: {0}]".format(error)  

	    try:#Template Curve duplication ====================================================================================
		self.progressBar_set(status = 'Template Curve duplication')  
		d_toDup = {'mouthTopTrace':self.mi_mouthTopCastCrv,
	                   'mouthBaseTrace':self.mi_mouthLowCastCrv}
		for str_k in d_toDup.iterkeys():
		    mi_dup = cgmMeta.asMeta( mc.duplicate(d_toDup[str_k].mNode,po=False,ic=True,rc=True)[0],'cgmObject',setClass=True )
		    mi_dup.cgmType = 'traceCrv'
		    mi_dup.cgmName = mi_dup.cgmName.replace('Cast','')
		    mi_dup.doName()
		    cgmMeta.cgmAttr(mi_dup,'translate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'rotate',lock = False, keyable = True)
		    cgmMeta.cgmAttr(mi_dup,'scale',lock = False, keyable = True)
		    mi_dup.parent = mi_go._i_rigNull

		    #ml_curves.append(mi_dup)
		    self.__dict__["mi_{0}Crv".format(str_k)] = mi_dup

	    except Exception,error:raise Exception,"[Template Curve | error: {0}]".format(error)  

	    try:#Build plates ====================================================================================
		md_plateBuilds = {'uprLip':{'crvs':[self.mi_mouthTopCastCrv,self.mi_lipOverTraceCrv,self.mi_lipUprCrv]},
	                          'lwrLip':{'crvs':[self.mi_lipLwrCrv,self.mi_lipUnderTraceCrv,self.mi_mouthLowCastCrv]},}
		#self.create_plateFromDict(md_plateBuilds)
		faceUtils.create_plateFromDict(self,md_plateBuilds)
	    except Exception,error:raise Exception,"[Plates | error: {0}]".format(error)  	    

	    try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
		#                                          'bindJoints': [self.md_rigList['lipCornerRig']['left'][0].lwrDriverSkin,self.md_rigList['lipCornerRig']['right'][0].uprDriverSkin] + self.ml_uprLipRigJoints + self.md_rigList['noseMoveRig'] + [self.md_rigList['nostrilRig']['left'][0],self.md_rigList['nostrilRig']['right'][0]] + [self.md_rigList['noseUnderRig'][0]]},		           	          
		d_build = {'uprLipPlate':{'target':self.mi_uprLipPlate,
	                                  'bindJoints': [self.md_rigList['lipCornerRig']['left'][0].uprDriverSkin,
	                                                 md_overSkinJoints['center'][0],md_overSkinJoints['left'][0],
	                                                 md_overSkinJoints['right'][0],self.md_rigList['lipCornerRig']['right'][0].uprDriverSkin] + self.ml_uprLipRigJoints},		           	          
	                   'lwrLipPlate':{'target':self.mi_lwrLipPlate,
	                                  'bindJoints':[self.md_rigList['lipCornerRig']['left'][0].lwrDriverSkin,
	                                                 md_underSkinJoints['center'][0],md_underSkinJoints['left'][0],
	                                                 md_underSkinJoints['right'][0],self.md_rigList['lipCornerRig']['right'][0].lwrDriverSkin] + self.ml_lwrLipRigJoints}}
		faceUtils.skin_fromDict(self,d_build)
	    except Exception,error:raise Exception,"[Skinning  | error: {0}]".format(error)    

	    try:#Attach stuff to surfaces ====================================================================================
		str_uprLipPlate = self.mi_uprLipPlate.p_nameShort
		str_lwrLipPlate = self.mi_lwrLipPlate.p_nameShort
		d_build = {'lipOverRig':{'mode':'pointAttach','attachTo':str_uprLipPlate},		           
	                   'lipUnderRig':{'mode':'pointAttach','attachTo':str_lwrLipPlate}}
		faceUtils.attach_fromDict(self,d_build)
		
	    except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error) 
	    #singleTarget

	    try:#>>> Aim some stuff =================================================================================
		d_build = {'lipUnderRig':{'mode':'singleTarget',
	                                 'center':{'aimTarget':self.md_rigList['lipLwrHandle']['center'][0],
	                                           'upLoc':md_lwr_upLocs['center'][0],
	                                           'v_aim':mi_go._vectorUp,
	                                           'v_up':mi_go._vectorAim},                                          
	                                 'left':{'aimTarget':self.md_rigList['smileBaseHandle']['left'][0],
	                                         'upLoc':self.md_rigList['lipUnderRig']['center'][0],
	                                         'v_aim':mi_go._vectorUpNegative,
	                                         'v_up':mi_go._vectorOutNegative},
	                                  'right':{'aimTarget':self.md_rigList['smileBaseHandle']['right'][0],
	                                           'upLoc':self.md_rigList['lipUnderRig']['center'][0],
	                                           'v_aim':mi_go._vectorUpNegative,
	                                           'v_up':mi_go._vectorOut}},
	                   'lipOverRig':{'mode':'singleBlend',
	                                 'center':{'d_target0':{'target':self.md_rigList['noseUnderRig'][0],
	                                                        'upLoc':md_upr_upLocs['center'][0],
	                                                        'v_aim':mi_go._vectorUp,
	                                                        'v_up':mi_go._vectorAim},
	                                           'd_target1':{'target':self.md_rigList['lipUprHandle']['center'][0],
	                                                        'upLoc':md_upr_upLocs['center'][0],
	                                                        'v_aim':mi_go._vectorUpNegative,
	                                                        'v_up':mi_go._vectorAim}},                                          
	                                  'left':{'d_target0':{'target':self.md_rigList['nostrilRig']['left'][0],
	                                                       'upLoc':md_upr_upLocs['left'][0],
	                                                       'v_aim':mi_go._vectorUp,
	                                                       'v_up':mi_go._vectorAim},
	                                          'd_target1':{'target':self.md_rigList['lipUprHandle']['left'][0],
	                                                       'upLoc':md_upr_upLocs['left'][0],
	                                                       'v_aim':mi_go._vectorUpNegative,
	                                                       'v_up':mi_go._vectorAim}},
	                                  'right':{'d_target0':{'target':self.md_rigList['nostrilRig']['right'][0],
	                                                       'upLoc':md_upr_upLocs['right'][0],
	                                                       'v_aim':mi_go._vectorUp,
	                                                       'v_up':mi_go._vectorAimNegative},
	                                          'd_target1':{'target':self.md_rigList['lipUprHandle']['right'][0],
	                                                       'upLoc':md_upr_upLocs['right'][0],
	                                                       'v_aim':mi_go._vectorUpNegative,
	                                                       'v_up':mi_go._vectorAimNegative}}}}
		faceUtils.aim_fromDict(self,d_build)
		
	    except Exception,error:raise Exception,"[Aim! | error: {0}]".format(error)   	    
        def _buildJawLines_(self):
            mi_go = self._go#Rig Go instance link
            try:#Pull Local ========================================================================
                f_lenJawLine = self.d_dataBuffer['f_lenJawLine']
            except Exception,error:raise Exception,"[Pull local | error: {0}]".format(error)  
            
            '''
            try:#make special up locs for handles -----------------------------------------------------------------------
                d_build = {'jawAnchor':{'mode':'handleAimOut','offsetDist':f_lenJawLine}}
                self.create_specialLocsFromDict(d_build)
            except Exception,error:raise Exception,"[influence joints | error: {0}]".format(error)	           
            
            try:#Setup segments ========================================================================
                d_build = {'jawLineSegment':{'orientation':mi_go._jointOrientation,
                                             'left':{'mi_curve':None},
                                             'right':{'mi_curve':None}}}	
                self.create_segmentfromDict(d_build)
            except Exception,error:raise Exception,"[Segments | error: {0}]".format(error)  
            '''

            try:#Attach stuff to surfaces ====================================================================================
		#'jawAnchor':{'mode':'handleAttach','attachTo':str_jawPlate},
                str_jawPlate = self.mi_jawPlate.p_nameShort  
                mi_lwrTeethPlate = self.mi_lwrTeethPlate		
                d_build = {'jawLine':{'attachTo':str_jawPlate,'mode':'pointAttach',
                                      'center':{'attachTo':mi_lwrTeethPlate,'mode':'handleAttach'}}}
		faceUtils.attach_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error)
            
            try:#>>> Aim some stuff =================================================================================
                d_build = {'jawLine':{'mode':'segmentSingleAim','skip':['center'],
                                      'left':{'v_aim':mi_go._vectorOutNegative,'v_up':mi_go._vectorAim,
                                              'upLoc':self.md_rigList['specialLocs']['jawRig']['left']},
                                      'right':{'v_aim':mi_go._vectorOut,'v_up':mi_go._vectorAimNegative,
                                               'upLoc':self.md_rigList['specialLocs']['jawRig']['right']}}}
                #self.aim_fromDict(d_build)
		faceUtils.aim_fromDict(self,d_build)
		
            except Exception,error:raise Exception,"[Aim! | error: {0}]".format(error)      
            
            '''
                self.md_rigList['specialLocs']['uprHeadDef']['left']
                self.md_rigList['specialLocs']['jawRig']['left']
			'''
            
            
            '''
            try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
                d_build = {'jawLineLeft':{'target':self.md_rigList['jawLineSegment']['leftSegmentCurve'],
                                        'bindJoints':[self.md_rigList['jawAnchor']['left'][0],
                                                      self.md_rigList['jawLine']['center'][0]
                                                      ]},
                           'jawLineRight':{'target':self.md_rigList['jawLineSegment']['rightSegmentCurve'],
                                         'bindJoints':[self.md_rigList['jawAnchor']['right'][0],
                                                       self.md_rigList['jawLine']['center'][0]]}}
                self.skin_fromDict(d_build)
            except Exception,error:raise Exception,"[Skinning! | error: {0}".format(error)	  
            '''
            try:#>>> Connect rig joints to handles ==================================================================
                d_build = {'jawLine':{'skip':['left','right'],
                                      'mode':'attrOffsetConnect','driver':self.md_rigList['chin'][0],'attrsToConnect':['tz']}}
                           #'jawLine':{'skip':['center'],
                                      #'mode':'rigToSegment'}}
		faceUtils.connect_fromDict(self,d_build)
		
            except Exception,error:raise Exception,"[Connect! | error: {0}]".format(error) 	    
            
            
        def _buildSmileLines_(self):
            mi_go = self._go#Rig Go instance link

            try:#influenceJoints -----------------------------------------------------------------------
                d_build = {'sneerHandle':{},
                           'smileBaseHandle':{}}
		faceUtils.create_influenceJoints(self,d_build)
                #self.create_influenceJoints(d_build)
                self.log_infoDict(self.md_rigList['sneerHandleInfluenceJoints'],'sneerHandle')
            except Exception,error:raise Exception,"[influence joints | error: {0}]".format(error)
	    
	    try:#Contrain some stuff ====================================================================================
		d_build = {'smileHandle':{'mode':'point',
		                         'left':{'targets':[self.md_rigList['lipCornerRig']['left'][0]]},                                          
		                         'right':{'targets':[self.md_rigList['lipCornerRig']['right'][0]]}}}		
		faceUtils.constrain_fromDict(self,d_build)
		
	    except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error) 
	    
            try:#Attach stuff to surfaces ====================================================================================		
                d_build = {'sneerHandleInfluenceJoints':{'attachTo':self.mi_jawPlate},#...rig attach so that we can drive it's position via the left lip corner
                           'sneerHandle':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseMoveRig'][0].p_nameShort},
                           'uprSmileHandle':{'attachTo':self.mi_jawPlate,'mode':'slideHandleAttach'},    
                           #'uprSmileHandle':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['noseMoveRig'][0].p_nameShort},		           
                           #'smileHandle':{'attachTo':self.mi_jawPlate,'mode':'slideHandleAttach'},#...rig attach so that we can drive it's position via the left lip corner		           
                           #'smileHandle':{'left':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['lipCornerRig']['left'][0]},
		           #               'right':{'mode':'parentOnly','attachTo':None,'parentTo':self.md_rigList['lipCornerRig']['right'][0]}},#...rig attach so that we can drive it's position via the left lip corner		                                      
                           'smileBaseHandle':{'attachTo':self.mi_lwrTeethPlate,'mode':'slideHandleAttach'},#...rig attach so that we can drive it's position via the chin           	                         		           	           
                           }
		faceUtils.attach_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error)

            try:#>>> Connect rig joints to handles ==================================================================
                d_build = {'sneerHandleInfluenceJoints':{'mode':'parentConstraint',
                                                         'rewireFollicleOffset':True,
                                                         'rewireFollicleOffsetRotate':True,
                                                         'left':{'targets':[self.md_rigList['sneerHandle']['left'][0]],
                                                                 'rewireHandle':self.md_rigList['sneerHandle']['left'][0]},
                                                         'right':{'targets':[self.md_rigList['sneerHandle']['right'][0]],
                                                                  'rewireHandle':self.md_rigList['sneerHandle']['right'][0]}},		           
		           'uprSmileHandle':{'mode':'parentConstraint',#'rewireFollicleOffset':True,
		                             'left':{'targets':[self.md_rigList['noseMoveRig'][0],#self.md_rigList['lipCornerHandle']['left'][0],
		                                                self.md_rigList['nostrilRig']['left'][0],self.md_rigList['sneerHandle']['left'][0]]},
		                             'right':{'targets':[self.md_rigList['noseMoveRig'][0],#self.md_rigList['lipCornerHandle']['right'][0],
		                                                 self.md_rigList['nostrilRig']['right'][0],self.md_rigList['sneerHandle']['right'][0]]}},		           
		           #'smileHandle':{'mode':'pointConstraint','rewireFollicleOffset':True,
                           #               'left':{'targets':[self.md_rigList['lipCornerHandle']['left'][0]],
                           #                       'rewireHandle':self.md_rigList['lipCornerHandle']['left'][0]},
                           #               'right':{'targets':[self.md_rigList['lipCornerHandle']['right'][0]],#was lipCornerRig
                           #                        'rewireHandle':self.md_rigList['lipCornerHandle']['right'][0]}},
                           'smileLineRig':{'mode':'rigToSegment'},
                           'smileBaseHandle':{'mode':'parentConstraint',
                                              'targets':[self.md_rigList['chinTrackLoc'][0]]}	           
                           }
		faceUtils.connect_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Connect! | error: {0}]".format(error) 	    

            try:#Setup segments ========================================================================
                d_build = {'smileLineSegment':{'orientation':mi_go._jointOrientation,
                                               'left':{'mi_curve':None},
                                               'right':{'mi_curve':None}}}	
		faceUtils.create_segmentfromDict(self,d_build)
		
            except Exception,error:raise Exception,"[Segments | error: {0}]".format(error)  

            try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
                d_build = {'smileLeft':{'target':self.md_rigList['smileLineSegment']['leftSegmentCurve'],
                                        'bindJoints':[self.md_rigList['sneerHandle']['left'][0].influenceJoint,
                                                      self.md_rigList['smileHandle']['left'][0],
                                                      self.md_rigList['uprSmileHandle']['left'][0],		                                      
                                                      self.md_rigList['nostrilRig']['left'][0],
                                                      self.md_rigList['smileBaseHandle']['left'][0]]},
                           'smileRight':{'target':self.md_rigList['smileLineSegment']['rightSegmentCurve'],
                                         'bindJoints':[self.md_rigList['sneerHandle']['right'][0].influenceJoint,
                                                       self.md_rigList['smileHandle']['right'][0],
		                                       self.md_rigList['uprSmileHandle']['right'][0],		                                      		                                       
                                                       self.md_rigList['nostrilRig']['right'][0],		                                      
                                                       self.md_rigList['smileBaseHandle']['right'][0]]}}
		faceUtils.skin_fromDict(self,d_build)
		
            except Exception,error:raise Exception,"[Skinning! | error: {0}".format(error)	   


        
        def _buildCheekSurface_(self):
            try:#>> Query ========================================================================
                mi_go = self._go#Rig Go instance link
                str_skullPlate = self.str_skullPlate

                try:#>> plate queries ---------------------------------------------------------------
                    mi_browPlate = self.mi_browPlate
                    mi_uprTeethPlate = self.mi_uprTeethPlate
                    mi_lwrTeethPlate = self.mi_lwrTeethPlate	
                    mi_jawPlate = self.mi_jawPlate
                except Exception,error:raise Exception,"[Plate query | error: {0}]".format(error)
                mi_l_eyeMove = cgmMeta.cgmObject('l_eye_eyeMove_anim')
                mi_r_eyeMove = cgmMeta.cgmObject('r_eye_eyeMove_anim')
            except Exception,error:raise Exception,"[Query | error: {0}]".format(error)
            '''
            try:#Build Curves ===================================================================================================
                md_curvesBuilds = {'uprCheekFollowLeft':{'pointTargets':self.md_rigList['uprCheekRig']['left'][:-1] + [self.md_rigList['smileLineRig']['left'][0]]},
                                   'uprCheekFollowRight':{'pointTargets':self.md_rigList['uprCheekRig']['right'][:-1] + [self.md_rigList['smileLineRig']['right'][0]]}}	
                self.create_curvesFromDict(md_curvesBuilds)
            except Exception,error:raise Exception,"[Build Curves! | error: {0}".format(error)
            '''
            try:#Build plates ===================================================================================================
                md_plateBuilds = {'cheekLeft':{'mode':'cheekLoft','direction':'left','name':'cheek',
                                               'smileCrv':self.mi_smileLeftCrv},
                                  'cheekRight':{'mode':'cheekLoft','direction':'right','name':'cheek',
                                                'smileCrv':self.mi_smileRightCrv}}
		faceUtils.create_plateFromDict(self,md_plateBuilds)
            except Exception,error:raise Exception,"[Plates!] | error: {0}".format(error)
	    
            try:#influenceJoints -----------------------------------------------------------------------
		self.md_rigList['outerUprCheekHandle'] = {'left':[self.md_rigList['uprCheekHandles']['left'][0]],
		                                          'right':[self.md_rigList['uprCheekHandles']['right'][0]]}
                d_build = {'outerUprCheekHandle':{'parentToHandle':True}}
		faceUtils.create_influenceJoints(self,d_build)
                self.log_infoDict(self.md_rigList['outerUprCheekHandleInfluenceJoints'],'outerUprCheekHandle')
            except Exception,error:raise Exception,"[influence joints | error: {0}]".format(error)	
	    
            try:#Attach stuff to surfaces ====================================================================================
                #Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
                str_skullPlate = self.str_skullPlate
                str_jawPlate = self.mi_jawPlate.p_nameShort
                str_cheekLeftPlate = self.mi_cheekLeftPlate.p_nameShort
                str_cheekRightPlate = self.mi_cheekRightPlate.p_nameShort
		'''
		'outerUprCheekHandleInfluenceJoints':{'left':{'mode':'parentOnly','attachTo':None,'parentTo':mi_l_eyeMove.mNode},
				      'right':{'mode':'parentOnly','attachTo':None,'parentTo':mi_r_eyeMove.mNode}},	
		'''
                d_build = {'cheekRig':{'left':{'mode':'pointAttach','attachTo':str_cheekLeftPlate},
                                       'right':{'mode':'pointAttach','attachTo':str_cheekRightPlate}},
                           'uprCheekRig':{'left':{'mode':'handleAttach','attachTo':str_cheekLeftPlate},
                                          'right':{'mode':'handleAttach','attachTo':str_cheekRightPlate}},
                           'cheekAnchor':{'mode':'slideAttach','attachTo':str_jawPlate},	           
                           'uprCheekHandles':{'left':{0:{'mode':'parentOnly','attachTo':None,'parentTo':mi_l_eyeMove.mNode},
                                                      1:{'mode':'slideHandleAttach','attachTo':str_jawPlate}},
                                              'right':{0:{'mode':'parentOnly','attachTo':None,'parentTo':mi_r_eyeMove.mNode},
                                                       1:{'mode':'slideHandleAttach','attachTo':str_jawPlate}}}                           
                           }
		faceUtils.attach_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Attach!] | error: {0}".format(error)
	    
            try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
                mi_noseMove = self.md_rigList['noseMoveHandle'][0]
                # self.md_rigList['smileLineRig']['left']
		#self.md_rigList['uprSmileHandle']['right']
                d_build = {'cheekRight':{'target':self.mi_cheekRightPlate,
                                         'bindJoints':self.md_rigList['jawLine']['right'] + self.md_rigList['cheekAnchor']['right'] + self.md_rigList['smileHandle']['right'] + [self.md_rigList['uprCheekHandles']['right'][-1]] + self.md_rigList['outerUprCheekHandleInfluenceJoints']['right']},		           
                           'cheekLeft':{'target':self.mi_cheekLeftPlate,
                                        'bindJoints':self.md_rigList['jawLine']['left'] + self.md_rigList['cheekAnchor']['left'] + self.md_rigList['smileHandle']['left'] + [self.md_rigList['uprCheekHandles']['left'][-1]] + self.md_rigList['outerUprCheekHandleInfluenceJoints']['left']}}
		faceUtils.skin_fromDict(self,d_build)
            except Exception,error:raise Exception,"[Skinning! | error: {0}]".format(error)	
                        
            try:#>>> Influence push Offset  ==================================================================
		'''
		'outerUprCheekHandleInfluenceJoints':{'left':{'mode':'parentConstraint','targets':[self.md_rigList['outerUprCheekHandle']['left'][0]]},
		                                                 'right':{'mode':'parentConstraint','targets':[self.md_rigList['outerUprCheekHandle']['right'][0]]}},
		           
		'outerUprCheekHandleInfluenceJoints':{'mode':'outerUprCheekOffset',
		                                                 'left':{'driver':self.md_rigList['outerUprCheekHandle']['left'][0],'attrsToConnect':['tx','tz']},
		                                                 'right':{'driver':self.md_rigList['outerUprCheekHandle']['right'][0],'attrsToConnect':['tx','tz']}},                          
		'''
		for str_direction in 'left','right':
		    try:
			try:#Query! ----------------------------------------------------------------------------------
		    
			    mi_influenceJoint = self.md_rigList['outerUprCheekHandleInfluenceJoints'][str_direction][0]
			    mi_handle = self.md_rigList['outerUprCheekHandle'][str_direction][0]
			    
			    try:mi_offsetGroup = mi_go.verify_offsetGroup(mi_influenceJoint)#..Create offsetgroup
			    except Exception,error:raise Exception,"[offset verify fail! | error: {0}]".format(error)	
				    
			    str_attr = "t{0}".format(mi_go._jointOrientation[0])
			    ml_innerOuterOffsetPlugs = []
			    l_nodalArgs = []		    
			except Exception,error:raise Exception,"[Query! | {0}]".format(error)			

			try:#Get Plugs! ----------------------------------------------------------------------------------
			    mPlug_attrDriven = cgmMeta.cgmAttr(mi_offsetGroup,str_attr)
			    mPlug_attrDriver = cgmMeta.cgmAttr(mi_handle,"t{0}".format(mi_go._jointOrientation[1]))   
			    
			    mPlug_outFactor = cgmMeta.cgmAttr(mi_handle,'pushMax',attrType='float',value = .25,hidden = False,defaultValue = .25)
			    mPlug_upTarget = cgmMeta.cgmAttr(mi_handle,'upTarget',attrType='float',value = 1.3,hidden = False,defaultValue = 1.3)
			    
			    mPlug_upOnResult = cgmMeta.cgmAttr(mi_handle,'res_upOn',attrType='float',value = 0.0, keyable=False, hidden=True)
			    mPlug_outUseResult = cgmMeta.cgmAttr(mi_handle,'res_upUse',attrType='float',value = 0.0, keyable=False, hidden=True)
			    mPlug_outFactorResult = cgmMeta.cgmAttr(mi_handle,'res_pushFactor',attrType='float',value = 0.0, keyable=False, hidden=True)
			    mPlug_outMultResult = cgmMeta.cgmAttr(mi_handle,'res_multOut',attrType='float',value = 0.0, keyable=False, hidden=True)			    
			    mPlug_outResult = cgmMeta.cgmAttr(mi_handle,'res_out',attrType='float',value = 0.0, keyable=False, hidden=True)
			    
			except Exception,error:raise Exception,"[Get Plugs fail! | {0}]".format(error)
			
			try:#Nodal Args! ----------------------------------------------------------------------------------
			    try:
				arg_upOn = "{0} = if {1} >= 0: 1 else 0".format(mPlug_upOnResult.p_combinedShortName,
				                                                mPlug_attrDriver.p_combinedShortName)
				l_nodalArgs.append(arg_upOn)
			    except Exception,error:raise Exception,"[upOn arg! | {0}]".format(error)
			    
			    try:
				arg_outFactor = "{0} = {2} / {1}".format(mPlug_outFactorResult.p_combinedShortName,
				                                         mPlug_upTarget.p_combinedShortName,
				                                         mPlug_attrDriver.p_combinedShortName)
				l_nodalArgs.append(arg_outFactor)
			    except Exception,error:raise Exception,"[out factor arg! | {0}]".format(error)			    
			    
			    try:
				if mi_handle.cgmDirection == 'left':
				    arg_outFactorValue = "{0} = {1} * {2}".format(mPlug_outUseResult.p_combinedShortName,
					                                          mPlug_outFactorResult.p_combinedShortName,
					                                          mPlug_outFactor.p_combinedShortName) 
				    
				else:
				    arg_outFactorValue = "{0} = {1} * -{2}".format(mPlug_outUseResult.p_combinedShortName,
					                                           mPlug_outFactorResult.p_combinedShortName,
					                                           mPlug_outFactor.p_combinedShortName) 
				l_nodalArgs.append(arg_outFactorValue)
			    except Exception,error:raise Exception,"[out use arg! | {0}]".format(error)
			    
			    try:
				arg_outMultResult = "{0} = {1} * {2}".format(mPlug_outMultResult.p_combinedShortName,
				                                             mPlug_upOnResult.p_combinedShortName,
				                                             mPlug_outUseResult.p_combinedShortName)
				l_nodalArgs.append(arg_outMultResult)				
			    except Exception,error:raise Exception,"[out use arg! | {0}]".format(error)
			    
			    try:
				arg_outResult = "{0} = clamp(0,{1},{2})".format(mPlug_attrDriven.p_combinedShortName,
				                                                mPlug_outFactor.p_combinedShortName,
				                                                mPlug_outMultResult.p_combinedShortName)
				l_nodalArgs.append(arg_outResult)				
			    except Exception,error:raise Exception,"[out use arg! | {0}]".format(error)
			    
			    for str_arg in l_nodalArgs:
				self.log_info("Building: {0}".format(str_arg))
				NodeF.argsToNodes(str_arg).doBuild()	
				
			except Exception,error:raise Exception,"[Nodal args fail! | {0}]".format(error)
		    except Exception,error:raise Exception,"['{0} | {1}]".format(str_direction,error)
            except Exception,error:raise Exception,"[Influence push Offset!] | error: {0}".format(error)            
            
	    try:#>>> Connect  ==================================================================
		'''
		'outerUprCheekHandleInfluenceJoints':{'left':{'mode':'parentConstraint','targets':[self.md_rigList['outerUprCheekHandle']['left'][0]]},
								 'right':{'mode':'parentConstraint','targets':[self.md_rigList['outerUprCheekHandle']['right'][0]]}},
			   
		'outerUprCheekHandleInfluenceJoints':{'mode':'outerUprCheekOffset',
								 'left':{'driver':self.md_rigList['outerUprCheekHandle']['left'][0],'attrsToConnect':['tx','tz']},
								 'right':{'driver':self.md_rigList['outerUprCheekHandle']['right'][0],'attrsToConnect':['tx','tz']}},                          
		'''
		d_build = {'uprCheekHandles':{'left':{0:{'mode':'skip'},
		                                      1:{'mode':'pointConstraint','targets':[mi_l_eyeMove,self.md_rigList['sneerHandleInfluenceJoints']['left'][0]]}},
		                              'right':{0:{'mode':'skip'},
		                                       1:{'mode':'pointConstraint','targets':[mi_r_eyeMove,self.md_rigList['sneerHandleInfluenceJoints']['right'][0]]}}}, 
		           'cheekAnchor':{'mode':'pointConstraint',
		                          'left':{'targets':[self.md_rigList['jawLine']['left'][0],self.md_rigList['uprCheekHandles']['left'][0]]},
		                          'right':{'targets':[self.md_rigList['jawLine']['right'][0],self.md_rigList['uprCheekHandles']['right'][0]]}}}
		faceUtils.connect_fromDict(self,d_build)
	    except Exception,error:raise Exception,"[Connect!] | error: {0}".format(error)		
	    
            try:#>>> Aim some stuff =================================================================================
                d_build = {'cheekAnchor':{'mode':'singleBlend',
                                          'left':{'d_target0':{'target':self.md_rigList['smileHandle']['left'][0],
                                                               'upLoc':self.md_rigList['uprCheekHandles']['left'][0],
                                                               'v_aim':mi_go._vectorUp,
                                                               'v_up':mi_go._vectorOutNegative},
                                                  'd_target1':{'target':self.md_rigList['smileHandle']['left'][0],
                                                               'upLoc':self.md_rigList['jawLine']['left'][0],
                                                               'v_aim':mi_go._vectorUpNegative,
                                                               'v_up':mi_go._vectorOutNegative}},
                                          'right':{'d_target0':{'target':self.md_rigList['smileHandle']['right'][0],
                                                               'upLoc':self.md_rigList['uprCheekHandles']['right'][0],
                                                               'v_aim':mi_go._vectorUp,
                                                               'v_up':mi_go._vectorOutNegative},
                                                  'd_target1':{'target':self.md_rigList['smileHandle']['right'][0],
                                                               'upLoc':self.md_rigList['jawLine']['right'][0],
                                                               'v_aim':mi_go._vectorUpNegative,
                                                               'v_up':mi_go._vectorOutNegative}}},
                            'cheekRig':{'mode':'segmentSingleAim',
                                        'left':{'v_aim':mi_go._vectorOutNegative,'v_up':mi_go._vectorAim,
                                                'upLoc':self.md_rigList['specialLocs']['uprHeadDef']['left']},
                                        'right':{'v_aim':mi_go._vectorOut,'v_up':mi_go._vectorAimNegative,
                                                 'upLoc':self.md_rigList['specialLocs']['uprHeadDef']['right']}}}
		faceUtils.aim_fromDict(self,d_build)
		
            except Exception,error:raise Exception,"[Aim! | error: {0}]".format(error)      
            
        
        def _buildUprCheek_(self):
            try:#>> Query ========================================================================
                mi_go = self._go#Rig Go instance link
                str_skullPlate = self.str_skullPlate

                try:#>> plate queries ---------------------------------------------------------------
                    mi_browPlate = self.mi_browPlate
                    mi_uprTeethPlate = self.mi_uprTeethPlate
                    mi_lwrTeethPlate = self.mi_lwrTeethPlate	
                    mi_jawPlate = self.mi_jawPlate
                except Exception,error:raise Exception,"[Plate query | error: {0}]".format(error)
                mi_l_eyeMove = cgmMeta.cgmObject('l_eye_eyeMove_anim')
                mi_r_eyeMove = cgmMeta.cgmObject('r_eye_eyeMove_anim')
            except Exception,error:raise Exception,"[Query | error: {0}]".format(error)

            try:#Attach stuff to surfaces ====================================================================================
                #Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
                #'uprCheekRig':{'attachTo':str_jawPlate,},
                d_build = {'uprCheekHandles':{'left':{0:{'mode':'parentOnly','attachTo':None,'parentTo':mi_l_eyeMove.mNode},
                                                      1:{'mode':'slideHandleAttach','attachTo':mi_browPlate}},
                                              'right':{0:{'mode':'parentOnly','attachTo':None,'parentTo':mi_r_eyeMove.mNode},
                                                       1:{'mode':'slideHandleAttach','attachTo':mi_browPlate}}}}				
                self.attach_fromDict(d_build)
            except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error)
            
            try:#Setup segments ========================================================================
                d_build = {'uprCheekSegment':{'orientation':mi_go._jointOrientation,
                                              'left':{'mi_curve':None},
                                              'right':{'mi_curve':None}}}	                
                self.create_segmentfromDict(d_build)
            except Exception,error:raise Exception,"[Segments | error: {0}]".format(error)  
            
            try:#>>> Connect rig joints to handles ==================================================================
                # 'driver':self.md_rigList['mouthMove']
                d_build = {'uprCheekHandles':{'left':{0:{'mode':'skip'},
                                                      1:{'mode':'simpleSlideHandle','driver':mi_l_eyeMove}},
                                              'right':{0:{'mode':'skip'},
                                                       1:{'mode':'simpleSlideHandle','driver':mi_r_eyeMove}}},
                           'uprCheekRig':{'mode':'rigToSegment'}}	
                self.connect_fromDict(d_build)
            except Exception,error:raise Exception,"[Connect! | error: {0}]".format(error)
            
            try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
                d_build = {'uprCheekLeft':{'target':self.md_rigList['uprCheekSegment']['leftSegmentCurve'],
                                           'bindJoints':[self.md_rigList['uprCheekHandles']['left'][0],
                                                         self.md_rigList['uprCheekHandles']['left'][1]]},
                           'uprCheekRight':{'target':self.md_rigList['uprCheekSegment']['rightSegmentCurve'],
                                            'bindJoints':[self.md_rigList['uprCheekHandles']['right'][0],
                                                          self.md_rigList['uprCheekHandles']['right'][1]]}}
                self.skin_fromDict(d_build)
            except Exception,error:raise Exception,"[Skinning! | error: {0}]".format(error)	               
            return
        
        def _buildMidCheekSegmentTrial_(self):
            try:#>> Query ========================================================================
                mi_go = self._go#Rig Go instance link
                try:#>> plate queries ---------------------------------------------------------------
                    str_skullPlate = self.str_skullPlate                    
                    mi_browPlate = self.mi_browPlate
                    mi_uprTeethPlate = self.mi_uprTeethPlate
                    mi_lwrTeethPlate = self.mi_lwrTeethPlate	
                    mi_jawPlate = self.mi_jawPlate
                except Exception,error:raise Exception,"[Plate query | error: {0}]".format(error)
            except Exception,error:raise Exception,"[Query | error: {0}]".format(error)

            try:#Attach stuff to surfaces ====================================================================================
                #Define our keys and any special settings for the build, if attach surface is not set, set to skull, if None, then none
                d_build = {'cheekAnchor':{'left':{'mode':'pointAttach','attachTo':mi_jawPlate},
                                          'right':{'mode':'pointAttach','attachTo':mi_jawPlate}}}				
                self.attach_fromDict(d_build)
            except Exception,error:raise Exception,"[Attach! | error: {0}]".format(error)
            
            try:#Setup segments ========================================================================
                d_build = {'cheekSegment':{'orientation':mi_go._jointOrientation,
                                           'left':{'mi_curve':None},
                                           'right':{'mi_curve':None}}}	                
                self.create_segmentfromDict(d_build)
            except Exception,error:raise Exception,"[Segments | error: {0}]".format(error) 
            
            #smileHandle
            try:#>>> Connect rig joints to handles ==================================================================
                # 'driver':self.md_rigList['mouthMove']
                d_build = {'cheekRig':{'mode':'rigToSegment'}}	
                self.connect_fromDict(d_build)
            except Exception,error:raise Exception,"[Connect! | error: {0}]".format(error)
            
            try:#>> Skinning Plates/Curves/Ribbons  =======================================================================================
                d_build = {'cheekLeft':{'target':self.md_rigList['cheekSegment']['leftSegmentCurve'],
                                        'bindJoints':[self.md_rigList['cheekAnchor']['left'][0],
                                                      self.md_rigList['smileHandle']['left'][0]]},
                           'cheekRight':{'target':self.md_rigList['cheekSegment']['rightSegmentCurve'],
                                         'bindJoints':[self.md_rigList['cheekAnchor']['right'][0],
                                                       self.md_rigList['smileHandle']['right'][0]]}}
                self.skin_fromDict(d_build)
            except Exception,error:raise Exception,"[Skinning! | error: {0}]".format(error)	               
            return
            try:#>>> Aim some stuff =================================================================================
                d_build = {'uprCheekRig':{'mode':'lipLineSegmentBlend',
                                          'v_up':mi_go._vectorUp}}
                self.aim_fromDict(d_build)
            except Exception,error:raise Exception,"[Aim! | error: {0}]".format(error)
            
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
                    except Exception,error:raise Exception,"Failed to attach. | ] | error: {0}".format(error)
                    self.md_attachReturns[mObj] = d_return
                except Exception,error:
                    raise StandardError,"Attach rig joint loop. obj: %s | ]{%s}"%(mObj.p_nameShort,error)	

            return True

	def _lockNHide_(self):
	    try:
		mi_go = self._go#Rig Go instance link		
		mi_jawZero = self.md_rigList['jawZero'][0]
		mi_constrainNull =  mi_go._i_faceDeformNull		
		mi_jawZero.parent = mi_constrainNull
	    except Exception,error:
		self.log_error("Jaw parent fail! {0}".format(error))
		
	    #Lock and hide all 
	    for mHandle in self.ml_handlesJoints:
		try:
		    if mHandle.getAttr('cgmName') not in ['jaw','tongueTip','tongueBase']:
			cgmMeta.cgmAttr(mHandle,'scale',lock = True, hidden = True)
		    cgmMeta.cgmAttr(mHandle,'v',lock = True, hidden = True)		
		    mHandle._setControlGroupLocks()	
		except Exception,error:self.log_error("[mHandle: '%s']{%s}"%(mHandle.p_nameShort,error))
    
	    for mJoint in self.ml_rigJoints:
		try:
		    mJoint._setControlGroupLocks()	
		    cgmMeta.cgmAttr(mJoint,'v',lock = True, hidden = True)		
		except Exception,error:self.log_error("[mJoint: '%s']{%s}"%(mJoint.p_nameShort,error))
    
	    
        def _lockNHideOLD_(self):
		
            #Lock and hide all 
            for mHandle in self.ml_handlesJoints:
                try:
                    if mHandle.getAttr('cgmName') not in ['jaw','tongueTip','tongueBase']:
                        cgmMeta.cgmAttr(mHandle,'scale',lock = True, hidden = True)
                    cgmMeta.cgmAttr(mHandle,'v',lock = True, hidden = True)		
                    mHandle._setControlGroupLocks()	
                except Exception,error:self.log_error("[mHandle: '%s']{%s}"%(mJoint.p_nameShort,error))
		
            for mJoint in self.ml_rigJoints:
                try:
                    mJoint._setControlGroupLocks()	
                    cgmMeta.cgmAttr(mJoint,'v',lock = True, hidden = True)		
                except Exception,error:self.log_error("[mJoint: '%s']{%s}"%(mJoint.p_nameShort,error))
	    
	    try:#>> Lock rotates...
		for mObj in [self.md_rigList['mouthMove'][0],
		             self.md_rigList['lipUprHandle']['left'][0],self.md_rigList['lipUprHandle']['right'][0],
		             self.md_rigList['lipLwrHandle']['left'][0],self.md_rigList['lipLwrHandle']['right'][0]]:
		    attributes.doSetLockHideKeyableAttr(mObj.mNode,channels = ['rx','ry','rz'])
	    except Exception,error:raise Exception,"[Lock rotates. | error: {0}]".format(error)
		
            mi_go = self._go#Rig Go instance link
	    mPlug_multpHeadScale = mi_go.mPlug_multpHeadScale
            try:#parent folicles to rignull
                for k in self.md_attachReturns.keys():# we wanna parent 
                    d_buffer = self.md_attachReturns[k]
                    try:d_buffer['follicleFollow'].parent = mi_go._i_rigNull
                    except:pass
		    try:
			if d_buffer.get('follicleFollow'):
			    cgmMeta.cgmAttr(d_buffer.get('follicleFollow'),'scale').doConnectIn(mPlug_multpHeadScale.p_combinedShortName)
			if d_buffer.get('follicleAttach'):
			    cgmMeta.cgmAttr(d_buffer.get('follicleAttach'),'scale').doConnectIn(mPlug_multpHeadScale.p_combinedShortName)
		    except Exception,error:
			self.log_error("[follicle scale connect. | error: {0}]".format(error))
			    
                    try:d_buffer['follicleAttach'].parent = mi_go._i_rigNull
                    except:pass	
                    try:
                        if d_buffer.get('controlLoc'):
                            mi_go.connect_toRigGutsVis(d_buffer['controlLoc'],vis = True)#connect to guts vis switches
			    if not d_buffer['controlLoc'].parent:
				d_buffer['controlLoc'].parent = mi_go._i_rigNull
                    except:pass			    
            except Exception,error:raise Exception,"Parent follicles. | ] | error: {0}".format(error)
	    
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