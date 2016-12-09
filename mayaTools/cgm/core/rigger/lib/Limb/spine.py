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
__version__ = 'beta.11112016'

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
from cgm.core.rigger.lib import module_Utils as modUtils
from cgm.core.rigger.lib import cgmRigs_sharedData as cgmRigsData
from cgm.core.rigger.lib import segment_utils as cgmSegment
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools

from cgm.core.rigger.lib import rig_Utils as rUtils
reload(rUtils)
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
__l_jointAttrs__ = ['startAnchor','endAnchor','anchorJoints','rigJoints',
                    'influenceJoints','segmentJoints']   

def __bindSkeletonSetup__(self):
    """
    The idea at the end of this is that we have create our skin joints from our
    module joints
    """
    try:
        if not self._cgmClass == 'JointFactory.go':
            log.error("Not a JointFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("spine.__bindSkeletonSetup__>>bad self!")
        raise Exception,error

    _str_funcName = "__bindSkeletonSetup__(%s)"%self._strShortName
    #log.debug(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()

    #>>> Re parent joints
    #=============================================================  
    if not self._mi_module.isSkeletonized():
        raise Exception, "%s is not skeletonized yet."%self._strShortName

    try:#Reparent joints
        ml_moduleJoints = self._mi_module.rigNull.msgList_get('moduleJoints',
                                                              asMeta = True)#Get the module joints
        ml_skinJoints = []

        for i,i_jnt in enumerate(ml_moduleJoints):
            ml_skinJoints.append(i_jnt)
            if i_jnt.hasAttr('cgmName'):
                #ml_handleJoints.append(i_jnt)		
                if i_jnt.cgmName in ['sternum','pelvis']:
                    i_jnt.parent = ml_moduleJoints[0].mNode#Parent sternum to root
                    i_dupJnt = i_jnt.doDuplicate(parentOnly = True)#Duplicate
                    i_dupJnt.addAttr('cgmNameModifier','scale')#Tag
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
        #log.debug("moduleJoints: len - %s | %s"%(len(ml_moduleJoints),[i_jnt.getShortName() for i_jnt in ml_moduleJoints]))	
        #log.debug("skinJoints: len - %s | %s"%(len(ml_skinJoints),[i_jnt.getShortName() for i_jnt in ml_skinJoints]))
        #log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     	
    except Exception,error:
        raise Exception,"%s >>> error : %s"%(_str_funcName,error)

def build_rigSkeleton(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_rigSkeleton(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Process','call':self._fncStep_process}]
            #=================================================================

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            #>>>Create joint chains
            #=============================================================    



            try:#>>Rig chain ----------------------------------------------------------- 	
                ml_rigJoints = mi_go.build_rigChain()
                """
		l_rigJoints = mc.duplicate(mi_go._l_skinJoints,po=True,ic=True,rc=True)
		ml_rigJoints = []
		for i,j in enumerate(l_rigJoints):
		    i_j = cgmMeta.cgmObject(j)
		    i_j.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
		    i_j.doName()
		    l_rigJoints[i] = i_j.mNode
		    ml_rigJoints.append(i_j)
		    if i_j.hasAttr('scaleJoint'):
			if i_j.scaleJoint in mi_go._ml_skinJoints:
			    int_index = mi_go._ml_skinJoints.index(i_j.scaleJoint)
			    i_j.connectChildNode(l_rigJoints[int_index],'scaleJoint','sourceJoint')#Connect
				"""	
                ml_rigJoints[0].parent = mi_go._i_deformNull.mNode#Parent to deformGroup
            except Exception,error:raise Exception,"rig chain fail! | error: {0}".format(error)

            try:#>>Anchor chain -----------------------------------------------------------	
                ml_anchors = []
                ml_handleJoints = mi_go._get_handleJoints()
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
            except Exception,error:raise Exception,"Anchor chain fail! | error: {0}".format(error)

            try:#>>Segment chain -----------------------------------------------------------            		
                ml_skinJoints = mi_go._ml_skinJoints
                ml_moduleJoints = mi_go._ml_moduleJoints

                l_segmentJoints = mc.duplicate(mi_go._l_moduleJoints[1:-1],po=True,ic=True,rc=True)
                ml_segmentJoints = []
                for i,j in enumerate(l_segmentJoints):
                    i_j = cgmMeta.asMeta(j,'cgmObject',setClass = True)
                    i_j.addAttr('cgmTypeModifier','segment',attrType='string')
                    i_j.addAttr('cgmIterator',i,lock = 1)	    
                    i_j.doName()
                    l_segmentJoints[i] = i_j.mNode
                    ml_segmentJoints.append(i_j)
                    
                    mi_skinJoint = ml_moduleJoints[1+i]
                    i_j.connectParentNode(mi_skinJoint.mNode, 'skinJoint')
                    #i_j.connectParentNode(mi_skinJoint.rigJoint, 'rigJoint')
                    
                    i_j.delAttr('scaleJoint')
                    
                    if i == 0:
                        ml_segmentJoints[0].parent = False#Parent to world
                    else:
                        ml_segmentJoints[i].parent = ml_segmentJoints[i-1].mNode#Parent to Last	
            except Exception,error:raise Exception,"segment chain fail!  | error: {0}".format(error)
            
            try:#Influence chain for influencing the surface ----------------------------------------------------------- 
                ml_influenceJoints = []
                for i_jnt in ml_handleJoints[1:-1]:
                    if i_jnt.hasAttr('cgmName') and i_jnt.cgmName in mi_go._l_coreNames:
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
                    
                if mi_go._b_noRollMode:
                    mJnt = ml_influenceJoints.pop(1)
                    mJnt.delete()
                    

                #>>> Store em all to our instance -----------------------------------------------------------
                mi_go._i_rigNull.connectChildNode(i_startJnt,'startAnchor','rigNull')
                mi_go._i_rigNull.connectChildNode(i_endJnt,'endAnchor','rigNull')
                mi_go._i_rigNull.msgList_connect(ml_anchors,'anchorJoints','rigNull')
                mi_go._i_rigNull.msgList_connect(ml_influenceJoints,'influenceJoints','rigNull')
                mi_go._i_rigNull.msgList_connect(ml_segmentJoints,'segmentJoints','rigNull')
            except Exception,error:raise Exception,"Influence joints fail! | error: {0}".format(error)

            try:#connections	
                ml_jointsToConnect = [i_startJnt,i_endJnt]
                ml_jointsToConnect.extend(ml_anchors)
                ml_jointsToConnect.extend(ml_rigJoints)
                ml_jointsToConnect.extend(ml_influenceJoints)
                ml_jointsToConnect.extend(ml_segmentJoints)

                for i_jnt in ml_jointsToConnect:
                    i_jnt.overrideEnabled = 1		
                    cgmMeta.cgmAttr(mi_go._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
                    cgmMeta.cgmAttr(mi_go._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    

            except Exception,error:raise Exception,"Connections fail! | error: {0}".format(error)
            return True

    return fncWrap(*args, **kws).go()

#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['cog','hips','segmentFK','segmentIK','handleIK']}

def build_shapes(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_shapes({0})'.format(self.d_kws['goInstance']._strShortName)	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Shapes','call':self.build_shapes}]
            #=================================================================

        def build_shapes(self):
            try:#>>>Build our Shapes =============================================================
                mi_go = self.d_kws['goInstance']
                mShapeCast.go(mi_go._mi_module,['cog','hips','torsoIK','segmentFK_Loli'],storageInstance=mi_go)#This will store controls to a dict called    
            except Exception,error:raise Exception,"build shapes | error : {0}".format(error)  
    return fncWrap(*args, **kws).go()


def build_controls(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_shapes(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'process','call':self._fncStep_process},
                                ]
            #=================================================================

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            #if not mi_go.isShaped():	
                #raise Exception,"build_controls>>> No shapes found connected"

            try:#>>> Get some special pivot xforms
                ml_segmentJoints = mi_go._i_rigNull.msgList_get('segmentJoints',asMeta=True,cull=True) 
                l_segmentJoints  = [i_jnt.mNode for i_jnt in ml_segmentJoints] 
                tmpCurve = curves.curveFromObjList(l_segmentJoints)
                hipPivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.1))#... .3
                shouldersPivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.8))#... .8	
                #hipPivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.4))
                #shouldersPivotPos = hipPivotPos
                log.debug("hipPivotPos : %s"%hipPivotPos)
                log.debug("shouldersPivotPos : %s"%shouldersPivotPos)   
                mc.delete(tmpCurve)
            except Exception,error:raise Exception,"Pivots fail | error: {0}".format(error)

            try:#>>> Get our shapes
                #__d_controlShapes__ = {'shape':['cog','hips','segmentFK','segmentIK','handleIK']}

                mi_cogShape = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_cog'),cgmMeta.cgmObject)
                mi_hipsShape = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_hips'),cgmMeta.cgmObject)
                ml_segmentFKShapes = cgmMeta.validateObjListArg(mi_go._i_rigNull.msgList_get('shape_segmentFKLoli',asMeta = False, cull = True),cgmMeta.cgmObject)
                ml_segmentIKShapes = cgmMeta.validateObjListArg(mi_go._i_rigNull.msgList_get('shape_segmentIK',asMeta = False, cull = True),cgmMeta.cgmObject)
                mi_handleIKShape = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_handleIK'),cgmMeta.cgmObject)

                ml_controlsAll = []#we'll append to this list and connect them all at the end 
            except Exception,error:raise Exception,"Gather shapes | error: {0}".format(error)


            #>>>Build our controls
            #=============================================================
            #>>>Set up structure
            try:#>>>> Cog
                i_cog = mi_cogShape
                d_buffer = mControlFactory.registerControl(i_cog,addExtraGroups = True,addConstraintGroup=True,
                                                           mirrorSide=mi_go._str_mirrorDirection,mirrorAxis="translateX,translateZ,rotateY,rotateZ",
                                                           freezeAll=True,makeAimable=True,autoLockNHide=True,
                                                           controlType='cog')
                i_cog = d_buffer['instance']
                ml_controlsAll.append(i_cog)
                mi_go._i_rigNull.connectChildNode(i_cog,'cog','rigNull')#Store
                mi_go._i_rigNull.connectChildNode(i_cog,'settings','rigNull')#Store as settings
                i_cog.masterGroup.parent = mi_go._i_deformNull.mNode
            except Exception,error:raise Exception,"Cog fail | error: {0}".format(error)


            try:	
                mPlug_result_moduleSubDriver = mi_go.build_visSub()	
            except Exception,error:raise Exception,"subVis fail | error: {0}".format(error)

            #==================================================================
            try:#>>>> FK Segments
                ml_segmentsFK = ml_segmentFKShapes
                for i,i_obj in enumerate(ml_segmentsFK[1:]):#parent
                    i_obj.parent = ml_segmentsFK[i].mNode
                ml_segmentsFK[0].parent = i_cog.mNode
                for i,i_obj in enumerate(ml_segmentsFK):
                    if i == 0:
                        #i_loc = ml_segmentsFK[i].doLoc(fastMode = True)
                        #copyPivot=str_pelvis,
                        #mc.move (hipPivotPos[0],hipPivotPos[1],hipPivotPos[2], i_loc.mNode)	
                        str_pelvis = mi_go._i_rigNull.msgList_getMessage('moduleJoints')[0]
                        log.info(str_pelvis)
                        d_buffer = mControlFactory.registerControl(i_obj,addConstraintGroup=1,
                                                                   mirrorSide=mi_go._str_mirrorDirection,mirrorAxis="translateX,rotateY,rotateZ",
                                                                   setRotateOrder=5,
                                                                   typeModifier='fk') 
                        #i_loc.delete()

                    else:
                        d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,setRotateOrder=5,typeModifier='fk',
                                                                   mirrorSide=mi_go._str_mirrorDirection,mirrorAxis="translateX,rotateY,rotateZ",) 
                    i_obj = d_buffer['instance']
                    i_obj.drawStyle = 6#Stick joint draw style	    
                mi_go._i_rigNull.msgList_connect(ml_segmentsFK,'controlsFK','rigNull')
                ml_controlsAll.extend(ml_segmentsFK)	

            except Exception,error:raise Exception,"FK Segments fail | error: {0}".format(error)


            #==================================================================    
            try:#>>>> IK Segments
                ml_segmentsIK = ml_segmentIKShapes

                for i_obj in ml_segmentsIK:
                    d_buffer = mControlFactory.registerControl(i_obj,addConstraintGroup=1,
                                                               mirrorSide=mi_go._str_mirrorDirection,mirrorAxis="translateX,rotateY,rotateZ",
                                                               typeModifier='segIK',
                                                               setRotateOrder=2) 

                    i_obj = d_buffer['instance']
                    mPlug_result_moduleSubDriver.doConnectOut("%s.visibility"%i_obj.mNode)	    
                    i_obj.masterGroup.parent = mi_go._i_deformNull.mNode
                mi_go._i_rigNull.msgList_connect(ml_segmentsIK,'segmentHandles','rigNull')
                ml_controlsAll.extend(ml_segmentsIK)	

            except Exception,error:raise Exception,"IK Segments fail | error: {0}".format(error)


            #==================================================================
            try:#>>>> IK Handle	
                i_IKEnd = mi_handleIKShape
                i_IKEnd.parent = i_cog.mNode
                i_loc = i_IKEnd.doLoc(fastMode = True)#Make loc for a new transform
                #i_loc.rx = i_loc.rx + 90#offset   
                mc.move (shouldersPivotPos[0],shouldersPivotPos[1],shouldersPivotPos[2], i_loc.mNode)

                d_buffer = mControlFactory.registerControl(i_IKEnd,copyTransform = i_loc.mNode,
                                                           mirrorSide=mi_go._str_mirrorDirection,mirrorAxis="translateX,rotateY,rotateZ",
                                                           typeModifier = 'ik',addSpacePivots = 2, addDynParentGroup = True, addConstraintGroup=True,
                                                           makeAimable = True,setRotateOrder=5)
                i_IKEnd = d_buffer['instance']	
                self.log_error("IK END HERE: {0}".format(i_IKEnd))
                i_loc.delete()#delete
                mi_go._i_rigNull.connectChildNode(i_IKEnd,'handleIK','rigNull')#connect
                ml_controlsAll.append(i_IKEnd)	

                #Set aims
                i_IKEnd.axisAim = mi_go._jointOrientation[1]+'-'
                i_IKEnd.axisUp = mi_go._jointOrientation[0]+'+'	

            except Exception,error:raise Exception,"ikHandle fail | error: {0}".format(error)


            #==================================================================
            try:#>>>> Hips	
                i_hips = mi_hipsShape
                i_hips.parent = i_cog.mNode#parent
                i_loc = i_hips.doLoc(fastMode = True)
                mc.move (hipPivotPos[0],hipPivotPos[1],hipPivotPos[2], i_loc.mNode)

                d_buffer =  mControlFactory.registerControl(i_hips,addSpacePivots = 2, addDynParentGroup = True,
                                                            mirrorSide=mi_go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",
                                                            addConstraintGroup=True, makeAimable = True,copyPivot=i_loc.mNode,setRotateOrder=5)
                mi_go._i_rigNull.connectChildNode(i_hips,'hips','rigNull')
                i_hips = d_buffer['instance']
                i_loc.delete()
                ml_controlsAll.append(i_hips)	

                #Set aims
                i_hips.axisAim = mi_go._jointOrientation[1]+'-'
                i_hips.axisUp = mi_go._jointOrientation[0]+'+'	

            except Exception,error:raise Exception,"hips fail | error: {0}".format(error)

            try:#Connect all controls	
                ml_extraControls = []
                for i,mCtrl in enumerate(ml_controlsAll):
                    try:
                        for str_a in cgmRigsData.__l_moduleControlMsgListHooks__:
                            buffer = mCtrl.msgList_get(str_a)
                            if buffer:
                                ml_extraControls.extend(buffer)
                                log.info("Extra controls : {0}".format(buffer))
                    except Exception,error:
                        self.log_error("mCtrl failed to search for msgList : {0}".format(mCtrl))
                        self.log_error("Fail error : {0}".format(error))
                ml_controlsAll.extend(ml_extraControls)	

                for i,mCtrl in enumerate(ml_controlsAll):
                    mCtrl.mirrorIndex = i
                #Push connections
                mi_go._i_rigNull.msgList_connect(ml_controlsAll,'controlsAll')
                mi_go._i_rigNull.moduleSet.extend(ml_controlsAll)
            except Exception,error:raise Exception,"connect fail | error: {0}".format(error)

            return True	    

    return fncWrap(*args, **kws).go()

def build_deformation(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_deformation({0})'.format(self.d_kws['goInstance']._strShortName)	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Process','call':self._fncStep_process}]
            #=================================================================
            #except Exception,error:raise Exception,"build shapes | error : {0}".format(error)  

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            try:#>>>Get data
                ml_influenceJoints = mi_go._i_rigNull.msgList_get('influenceJoints')
                ml_controlsFK =  mi_go._i_rigNull.msgList_get('controlsFK')    
                ml_segmentJoints = mi_go._i_rigNull.msgList_get('segmentJoints')
                ml_anchorJoints = mi_go._i_rigNull.msgList_get('anchorJoints')
                ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')
                ml_segmentHandles = mi_go._i_rigNull.msgList_get('segmentHandles')
                aimVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[0])
                upVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[1])
                mi_hips = mi_go._i_rigNull.hips
                mi_handleIK = mi_go._i_rigNull.handleIK
                mi_cog = mi_go._i_rigNull.cog

            except Exception,error:raise Exception,"get data fail! | error : {0}".format(error)  
            

            #====================================================================================
            try:#Control Segment
                capAim = mi_go._jointOrientation[0].capitalize()
                i_startControl = ml_segmentHandles[0]
                i_endControl = ml_segmentHandles[-1]
                #Create segment
                curveSegmentReturn = cgmSegment.create_basic([i_jnt.mNode for i_jnt in ml_segmentJoints],
                                                             addSquashStretch=True,
                                                             addTwist=True,
                                                             connectBy = 'scale',
                                                             addMidTwist = not mi_go._b_noRollMode,
                                                             influenceJoints=[ml_influenceJoints[0],ml_influenceJoints[-1]],
                                                             startControl=ml_segmentHandles[0],
                                                             endControl=ml_segmentHandles[-1],
                                                             orientation=mi_go._jointOrientation,
                                                             baseName=mi_go._partName,
                                                             additiveScaleSetup = True,#mi_go._b_addMidTwist,
                                                             additiveScaleConnect=True,
                                                             moduleInstance=mi_go._mi_module)

                i_curve = curveSegmentReturn['mi_segmentCurve']
                mi_go._i_rigNull.msgList_connect([i_curve],'segmentCurves','rigNull')	
                i_curve.segmentGroup.parent = mi_go._i_rigNull
                i_curve.parent = mi_go._i_rigNull
                """
                for o in  [ml_influenceJoints[1].mNode,
                       curveSegmentReturn['mi_segmentCurve'].mNode,
                       ml_influenceJoints[0].mNode,
                       ml_influenceJoints[-1].mNode,
                       ml_segmentHandles[1].mNode,
                       mi_go._partName,
                       mi_go._jointOrientation]:
                    log.debug(o)
                return"""
                if mi_go._b_addMidTwist:
                    midReturn = rUtils.addCGMSegmentSubControl(ml_influenceJoints[1].mNode,
                                                               segmentCurve = i_curve,
                                                               baseParent=ml_influenceJoints[0],
                                                               endParent=ml_influenceJoints[-1],
                                                               midControls=ml_segmentHandles[1],
                                                               baseName=mi_go._partName,
                                                               controlTwistAxis =  'r'+mi_go._jointOrientation[0],
                                                               orientation=mi_go._jointOrientation)
                    for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
                        i_grp.parent = mi_cog.mNode

            except Exception,error:raise Exception,"Control segment fail! | error : {0}".format(error)  

            try:#Setup top twist driver	
                #Create an fk additive attributes
                str_curve = curveSegmentReturn['mi_segmentCurve'].getShortName()
                fk_drivers = ["%s.r%s"%(i_obj.mNode,mi_go._jointOrientation[0]) for i_obj in ml_controlsFK]
                NodeF.createAverageNode(fk_drivers,
                                        [curveSegmentReturn['mi_segmentCurve'].mNode,"fkTwistSum"],1)#Raw fk twist

                try:NodeF.argsToNodes("%s.fkTwistResult = %s.fkTwistSum * %s.fkTwistInfluence"%(str_curve,str_curve,str_curve)).doBuild()
                except Exception,error:
                    raise Exception,"fkTwistResult node arg fail: %s"%error	


                drivers = ["%s.%s"%(curveSegmentReturn['mi_segmentCurve'].mNode,"fkTwistResult")]

                for mObj in ml_segmentHandles[-1],mi_handleIK,mi_handleIK.dynParentGroup:
                    drivers.append("%s.r%s"%(mObj.mNode,mi_go._jointOrientation[0]))

                NodeF.createAverageNode(drivers,
                                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistEnd"],1)

            except Exception,error:raise Exception,"Top twist driver fail! | error : {0}".format(error)  

            
            try:#Setup bottom twist driver
                #log.debug("%s.r%s"%(ml_segmentHandles[0].getShortName(),mi_go._jointOrientation[0]))
                #log.debug("%s.r%s"%(mi_hips.getShortName(),mi_go._jointOrientation[0]))
                drivers = []

                for mObj in ml_segmentHandles[0],mi_hips,mi_hips.dynParentGroup:
                    drivers.append("%s.r%s"%(mObj.mNode,mi_go._jointOrientation[0]))

                #log.debug("driven: %s"%("%s.r%s"%(ml_anchorJoints[1].mNode,mi_go._jointOrientation[0])))
                NodeF.createAverageNode(drivers,
                                        [curveSegmentReturn['mi_segmentCurve'].mNode,"twistStart"],1)

            except Exception,error:raise Exception,"Bottom twist driver fail! | error : {0}".format(error)  


            try:#>>>Connect segment scale
                mi_distanceBuffer = i_curve.scaleBuffer	
                cgmMeta.cgmAttr(mi_distanceBuffer,'segmentScaleMult').doTransferTo(mi_cog.mNode)    
            except Exception,error:raise Exception,"Connect segment scale fail! | error : {0}".format(error)  


            try:#Do a few attribute connections
                #Push squash and stretch multipliers to cog	
                i_buffer = i_curve.scaleBuffer
                l_keys = i_buffer.d_indexToAttr.keys()
                f_factor = 3.0/len(l_keys)
                for i,k in enumerate(l_keys):
                    v_use = abs(len(l_keys) - (f_factor * (i+1)))
                    attrName = 'spine_%s'%k
                    cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_cog.mNode,attrName,connectSourceToTarget = True)
                    cgmMeta.cgmAttr(mi_cog.mNode,attrName,value =v_use, defaultValue = v_use, keyable = False, hidden = False)
                cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(mi_cog.mNode,connectSourceToTarget=True)
                #cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(mi_cog.mNode,connectSourceToTarget=True)
            except Exception,error:raise Exception,"Attribute connections fail! | error : {0}".format(error)  
            return True	    

    return fncWrap(*args, **kws).go()

def build_rig(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_rig({0})'.format(self.d_kws['goInstance']._strShortName)	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Process','call':self._fncStep_process}]
            #=================================================================

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            try:#>>>Get data
                orientation = modules.returnSettingsData('jointOrientation')

                mi_segmentCurve = mi_go._i_rigNull.msgList_get('segmentCurves',asMeta = True)[0]
                mi_segmentAnchorStart = cgmMeta.validateObjArg(mi_segmentCurve.anchorStart,'cgmObject')
                mi_segmentAnchorEnd = cgmMeta.validateObjArg(mi_segmentCurve.anchorEnd,'cgmObject')
                mi_segmentAttachStart = cgmMeta.validateObjArg(mi_segmentCurve.attachStart,'cgmObject')
                mi_segmentAttachEnd = cgmMeta.validateObjArg(mi_segmentCurve.attachEnd,'cgmObject') 
                mi_distanceBuffer = cgmMeta.validateObjArg(mi_segmentCurve.scaleBuffer,'cgmBufferNode')

                log.debug("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
                log.debug("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
                log.debug("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
                log.debug("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
                log.debug("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)

                ml_influenceJoints = mi_go._i_rigNull.msgList_get('influenceJoints',asMeta = True)
                ml_segmentJoints = mi_segmentCurve.msgList_get('drivenJoints',asMeta = True)
                ml_segmentSplineJoints = mi_segmentCurve.msgList_get('driverJoints',asMeta = True)

                ml_anchorJoints = mi_go._i_rigNull.msgList_get('anchorJoints',asMeta = True)
                ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints',asMeta = True)
                ml_handleJoints = mi_go._get_handleJoints()

                ml_segmentHandles = mi_go._i_rigNull.msgList_get('segmentHandles',asMeta = True)
                aimVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[0])
                upVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[1])
                mi_hips = mi_go._i_rigNull.hips
                mi_handleIK = mi_go._i_rigNull.handleIK
                ml_controlsFK =  mi_go._i_rigNull.msgList_get('controlsFK',asMeta = True)  
                mi_cog = mi_go._i_rigNull.cog

            except Exception,error:raise Exception,"Get data fail! | error : {0}".format(error)  


            #Dynamic parent groups
            #====================================================================================
            try:#>>>> Shoulder dynamicParent	
                #Build our dynamic groups
                ml_shoulderDynParents = [ml_controlsFK[-1], mi_cog,]
                ml_shoulderDynParents.extend(mi_handleIK.msgList_get('spacePivots',asMeta = True))
                ml_shoulderDynParents.append(mi_go._i_masterControl)
                log.debug(ml_shoulderDynParents)
                log.debug([i_obj.getShortName() for i_obj in ml_shoulderDynParents])

                #Add our parents
                i_dynGroup = mi_handleIK.dynParentGroup
                for o in ml_shoulderDynParents:
                    i_dynGroup.addDynParent(o)
                i_dynGroup.rebuild()
            except Exception,error:raise Exception,"Shoulder dynamic parent fail! | error : {0}".format(error)  

            try:#>>>> Hips dynamicParent
                ml_hipsDynParents = [mi_cog]
                ml_hipsDynParents.extend(mi_hips.msgList_get('spacePivots',asMeta = True))
                ml_hipsDynParents.append(mi_go._i_masterControl)
                log.debug(ml_hipsDynParents)
                log.debug([i_obj.getShortName() for i_obj in ml_hipsDynParents])  

                #Add our parents
                i_dynGroup = mi_hips.dynParentGroup
                for o in ml_hipsDynParents:
                    i_dynGroup.addDynParent(o)
                i_dynGroup.rebuild()   
            except Exception,error:raise Exception,"Hips dynamic parent fail! | error : {0}".format(error)  

            mi_go.collect_worldDynDrivers()

            #moving this to rig section and there's no reason for it to be an extra condition node??
            #FK influence on twist from the space it's in
            try:
                str_curve = mi_segmentCurve.getShortName()
                NodeF.argsToNodes("%s.fkTwistInfluence = if %s.space == 0:1 else 0"%(str_curve,mi_handleIK.getShortName())).doBuild()
            except Exception,error:raise Exception,"Twist influence fail! | error : {0}".format(error)

            try:#Set up some defaults
                #====================================================================================	
                mPlug_segStart = cgmMeta.cgmAttr(ml_segmentHandles[0],'followRoot')
                mPlug_segStart.p_defaultValue = .3
                mPlug_segStart.value = .3
                if mi_go._b_noRollMode:
                    mPlug_segMid = cgmMeta.cgmAttr(ml_segmentHandles[1],'linearSplineFollow')
                    mPlug_segMid.p_defaultValue = 1
                    mPlug_segMid.value = 1
                    mPlug_segMidAim = cgmMeta.cgmAttr(ml_segmentHandles[1],'startEndAim')
                    mPlug_segMidAim.p_defaultValue = .5
                    mPlug_segMidAim.value = .5   
                mPlug_segEnd = cgmMeta.cgmAttr(ml_segmentHandles[-1],'followRoot')
                mPlug_segEnd.p_defaultValue = .8
                mPlug_segEnd.value = .8
            except Exception,error:raise Exception,"Defaults fail! | error : {0}".format(error)  

            try:#Parent and constrain joints
                #====================================================================================
                ml_segmentJoints[0].parent = mi_cog.mNode#Segment to cog
                #ml_segmentSplineJoints[0].parent = mi_cog.mNode#Spline Segment to cog <<<<OLD METHOD

                #Put the start and end controls in the heirarchy
                ml_segmentHandles[0].masterGroup.parent = mi_segmentAttachStart.mNode
                ml_segmentHandles[-1].masterGroup.parent = mi_segmentAttachEnd.mNode

                mi_segmentAnchorStart.parent = mi_hips.mNode#Segment anchor start to cog
                '''
		mi_segmentAnchorStart.parent = mi_cog.mNode#Segment anchor start to cog
		mc.parentConstraint(ml_rigJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#constrain
		mc.scaleConstraint(ml_rigJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#Constrain
		'''
                mi_segmentAnchorEnd.parent = mi_handleIK.mNode#Anchor end to cog
                '''
		mc.parentConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
		mc.scaleConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
		'''
                #Parent the sternum to the anchor
                ml_handleJoints[-2].parent = ml_anchorJoints[-1]
                #ml_rigJoints[-1].parent = mi_handleIK.mNode
                

                #Parent the influence joints --------------------------------------------------------------
                ml_influenceJoints[0].parent = ml_segmentHandles[0]
                ml_influenceJoints[-1].parent = ml_segmentHandles[-1]

                if ml_handleJoints[-2].getMessage('scaleJoint'):#
                    ml_handleJoints[-2].scaleJoint.parent = ml_segmentHandles[-1]


                #Parent anchors to controls ---------------------------------------------------------------
                ml_anchorJoints[0].parent = mi_hips#parent pelvis anchor to hips
                ml_anchorJoints[1].parent = mi_hips
                ml_anchorJoints[-1].parent = mi_handleIK

                #Connect rig pelvis to anchor pelvis ---------------------------------------------------------------
                mc.pointConstraint(ml_anchorJoints[0].mNode,ml_handleJoints[0].mNode,maintainOffset=False)
                mc.orientConstraint(ml_anchorJoints[0].mNode,ml_handleJoints[0].mNode,maintainOffset=False)
                mc.scaleConstraint(ml_anchorJoints[0].mNode,ml_handleJoints[0].mNode,maintainOffset=False)#Maybe hips    

                l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
                """for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
                    #Don't try scale constraints in here, they're not viable
                    if i == 1 and mi_go._b_noRollMode:
                        continue
                    attachJoint = distance.returnClosestObject(i_jnt.mNode,l_rigJoints)
                    log.debug("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
                    pntConstBuffer = mc.pointConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
                    orConstBuffer = mc.orientConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
                    mc.connectAttr((i_jnt.mNode+'.s'),(attachJoint+'.s'))
                    for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
                    self.log_info("On " + i_jnt.p_nameShort)                    
                    if i == 1 and mi_go._b_noRollMode:
                        self.log_info("Skipping " + i_jnt.p_nameShort)
                        continue                    
                    mi_rigJoint = i_jnt.rigJoint
                    mi_rigJoint.parent = i_jnt                    
                    """
                
                if mi_go._b_noRollMode:#If no roll mode
                    for i,i_jnt in enumerate(ml_segmentJoints):
                        self.log_info("On " + i_jnt.p_nameShort) 
                        mi_rigJoint = i_jnt.rigJoint
                        if i == 1:
                            mi_rigJoint.parent = ml_segmentHandles[i]
                        else:
                            mi_rigJoint.parent = i_jnt
                    #ml_segmentHandles[1].masterGroup.parent = ml_segmentJoints[1]                
                    #pntConstBuffer = mc.parentConstraint(ml_segmentHandles[1].masterGroup.mNode,ml_segmentJoints[1].mNode,maintainOffset=False,weight=1)
                    pntConstBuffer = mc.parentConstraint(ml_segmentJoints[1].mNode,ml_segmentHandles[1].masterGroup.mNode,maintainOffset=True,weight=1)
                    pntConstBuffer = mc.scaleConstraint(ml_segmentJoints[1].mNode,ml_segmentHandles[1].masterGroup.mNode,maintainOffset=True,weight=1)                        
                else:
                    for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
                        self.log_info("On " + i_jnt.p_nameShort)                                       
                        mi_rigJoint = i_jnt.rigJoint
                        mi_rigJoint.parent = i_jnt
                       
                mc.pointConstraint(ml_anchorJoints[-1].mNode,ml_handleJoints[-2].mNode,maintainOffset=False)
                mc.orientConstraint(ml_anchorJoints[-1].mNode,ml_handleJoints[-2].mNode,maintainOffset=False)
                mc.connectAttr((ml_anchorJoints[-1].mNode+'.s'),(ml_handleJoints[-2].mNode+'.s'))
            except Exception,error:raise Exception,"parent fail! | error : {0}".format(error)  


            #Set up heirarchy, connect master scale
            #====================================================================================
            try:#>>>Connect master scale
                cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(mi_go._i_masterControl.mNode,'scaleY'))    
            except Exception,error:raise Exception,"Master scale connect fail! | error : {0}".format(error)  

            #Vis Network, lock and hide
            #====================================================================================   
            try:#Setup Cog vis control for fk controls	
                cgmMeta.cgmAttr(mi_cog,'visFK', value = 1, defaultValue = 1, attrType = 'int', minValue=0,maxValue=1,keyable = False,hidden = False)
                cgmMeta.cgmAttr( ml_controlsFK[0].mNode,'visibility').doConnectIn('%s.%s'%(mi_cog.mNode,'visFK'))    
            except Exception,error:raise Exception,"Vis connectfail! | error : {0}".format(error)  

            #Lock and hide hips and shoulders    
            try:#Set up Scale joints
                #====================================================================================     
                #Connect our last segment to the sternum if we have a scale joint
                if ml_handleJoints[-2].getMessage('scaleJoint'):
                    i_scaleJoint = ml_handleJoints[-2].scaleJoint
                    mc.connectAttr((ml_segmentHandles[-1].mNode+'.s%s'%mi_go._jointOrientation[1]),(i_scaleJoint.mNode+'.s%s'%mi_go._jointOrientation[1]))    
                    mc.connectAttr((ml_segmentHandles[-1].mNode+'.s%s'%mi_go._jointOrientation[2]),(i_scaleJoint.mNode+'.s%s'%mi_go._jointOrientation[2]))    

                if ml_handleJoints[0].getMessage('scaleJoint'):
                    i_scaleJoint = ml_handleJoints[0].scaleJoint
                    mc.connectAttr((mi_hips.mNode+'.scale'),(i_scaleJoint.mNode+'.scale'))    
                    #Move a couple of joints out and parent constrain them
                    for i_jnt in [ml_anchorJoints[0],ml_anchorJoints[1]]:
                        i_jnt.parent = mi_cog.mNode
                        mc.parentConstraint(mi_hips.mNode,i_jnt.mNode,maintainOffset=True)	    
                else:
                    attributes.doSetLockHideKeyableAttr(mi_hips.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
                    
            except Exception,error:raise Exception,"Scale joint fail! | error : {0}".format(error)  


            #sub vis,control groups
            #====================================================================================
            try:#Vis/locks	
                #attributes.doSetLockHideKeyableAttr(mi_handleIK.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
                for mCtrl in (ml_controlsFK + [mi_cog,mi_hips,mi_handleIK] + ml_segmentHandles):
                    try:
                        mCtrl._setControlGroupLocks()	
                    except Exception,error:
                        raise Exception,"mCtrl: {0}".format(mCtrl)
                for mCtrl in ml_segmentHandles:
                    cgmMeta.cgmAttr(mCtrl,"s%s"%orientation[0],lock=True,hidden=True,keyable=False)

                for mCtrl in ml_controlsFK + [mi_hips, mi_handleIK]:
                    cgmMeta.cgmAttr(mCtrl,"v",lock=True,hidden=True,keyable=False)
                    cgmMeta.cgmAttr(mCtrl,"scale",lock=True,hidden=True,keyable=False)
                    
            except Exception,error:raise Exception,"subVis fail! | error : {0}".format(error)  

            #Final stuff
            mi_go._set_versionToCurrent()
            return True 	    
    return fncWrap(*args, **kws).go()


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
	    raise Exception
    except Exception,error:
	log.error("spine.build_deformationRig>>bad self!")
	raise Exception,error

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
            raise Exception
    except Exception,error:
        log.error("spine.build_deformationRig>>bad self!")
        raise Exception,error

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
    i_midAim = ml_influenceJoints[1].doLoc(fastMode = True)
    i_midAim.addAttr('cgmTypeModifier','midAim')
    i_midAim.doName()
    i_midAim.overrideEnabled = 1
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'visLocs',lock=False).doConnectOut("%s.%s"%(i_midAim.mNode,'overrideVisibility'))

    i_midPoint = ml_influenceJoints[1].doLoc(fastMode = True)#midPoint
    i_midPoint.addAttr('cgmTypeModifier','midPoint')
    i_midPoint.doName()
    i_midPoint.overrideEnabled = 1
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'visLocs',lock=False).doConnectOut("%s.%s"%(i_midPoint.mNode,'overrideVisibility'))

    #Mid up constraint
    i_midUp = ml_influenceJoints[1].doLoc(fastMode = True)#midUp
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
    i_topAnchorAttachPivot = ml_influenceJoints[1].doLoc(fastMode = True)#Top Anchor
    i_topAnchorAttachPivot.addAttr('cgmTypeModifier','sternumAnchor')
    i_topAnchorAttachPivot.doName()
    i_topAnchorAttachPivot.parent =  ml_segmentHandles[-1].mNode
    mc.move(0,0,dist/2,i_topAnchorAttachPivot.mNode,os=True, r=True)
    i_topAnchorAttachPivot.overrideEnabled = 1
    cgmMeta.cgmAttr(self._i_rigNull.mNode,'visLocs',lock=False).doConnectOut("%s.%s"%(i_topAnchorAttachPivot.mNode,'overrideVisibility'))

    #Bottom Anchor 
    i_bottomAnchorAttachPivot = ml_influenceJoints[1].doLoc(fastMode = True)
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
    i_midFollowGrp = cgmMeta.asMeta( self._i_rigNull.msgList_get('segmentHandles')[1].doGroup(True),'cgmObject',setClass=True)
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
    i_baseUp = ml_influenceJoints[0].doLoc(fastMode = True)
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
    i_baseFollowGrp = cgmMeta.asMeta( self._i_rigNull.msgList_get('segmentHandles')[0].doGroup(True),'cgmObject',setClass=True)
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
            raise Exception
    except Exception,error:
        log.error("spine.build_deformationRig>>bad self!")
        raise Exception,error

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

    except Exception,error:
	log.error("build_spine>>Constraint surface build fail")
	raise Exception,error
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

    except Exception,error:
        log.error("build_spine>>Control surface build fail")
        raise Exception,error
    try:#Setup top twist driver
        drivers = ["%s.r%s"%(i_obj.mNode,self._jointOrientation[0]) for i_obj in ml_controlsFK]
        drivers.append("%s.r%s"%(ml_segmentHandles[-1].mNode,self._jointOrientation[0]))
        drivers.append("%s.ry"%(mi_handleIK.mNode))
        for d in drivers:
            log.debug(d)
        NodeF.createAverageNode(drivers,
                                [ml_anchorJoints[-1].mNode,"r%s"%self._jointOrientation[0]],1)

    except Exception,error:
        log.error("build_spine>>Top Twist driver fail")
        raise Exception,error

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

    except Exception,error:
        log.error("build_spine>>Bottom Twist driver fail")
        raise Exception,error



    return True