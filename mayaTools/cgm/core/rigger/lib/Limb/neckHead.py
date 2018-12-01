"""
------------------------------------------
cgm.core.rigger: Limb.neckHead
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

neckHead rig builder
================================================================
"""
__version__ = 'beta.08032015'


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
#from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.rigger.lib import module_Utils as modUtils
from cgm.core.rigger.lib import cgmRigs_sharedData as cgmRigsData
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools
from cgm.core.rigger.lib import rig_Utils as rUtils
import cgm.core.rig.segment_utils as SEGMENT
import cgm.core.lib.attribute_utils as ATTR

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

@cgmGeneral.Timer
def __bindSkeletonSetup__(self):
    """
    TODO: Do I need to connect per joint overrides or will the final group setup get them?
    """
    try:
        if not self._cgmClass == 'JointFactory.go':
            log.error("Not a JointFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("neckHead.__bindSkeletonSetup__>>bad self!")
        raise Exception,error

    _str_funcName = "__bindSkeletonSetup__(%s)"%self._strShortName
    #log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()

    #>>> Re parent joints
    #=============================================================  
    try:#Reparent joints		
        ml_moduleJoints = self._mi_module.rigNull.msgList_get('moduleJoints') #Get the module joints
        ml_skinJoints = []

        ml_handleJoints = self._mi_module.rig_getHandleJoints()

        for i,i_jnt in enumerate(ml_moduleJoints):
            ml_skinJoints.append(i_jnt)		
            if i_jnt in ml_handleJoints:
                if i == 0:i_jnt.parent = ml_moduleJoints[0].mNode#Parent head to root
                i_dupJnt = i_jnt.doDuplicate()#Duplicate
                i_dupJnt.addAttr('cgmTypeModifier','scale')#Tag
                #i_jnt.doName()#Rename
                i_dupJnt.doName()#Rename
                i_dupJnt.parent = i_jnt#Parent
                i_dupJnt.connectChildNode(i_jnt,'rootJoint','scaleJoint')#Connect
                #------------------------------------------------------------
                ml_skinJoints.append(i_dupJnt)#Append
                log.info("%s >> Created scale joint for '%s' >> '%s'"%(_str_funcName,i_jnt.getShortName(),i_dupJnt.getShortName()))

        for i,i_jnt in enumerate(ml_handleJoints[1:]):
            i_jnt.parent = ml_handleJoints[i].mNode	

        self._mi_module.rigNull.msgList_connect('skinJoints',ml_skinJoints)    	

        #log.info("moduleJoints: len - %s | %s"%(len(ml_moduleJoints),[i_jnt.getShortName() for i_jnt in ml_moduleJoints]))	
        #log.info("skinJoints: len - %s | %s"%(len(ml_skinJoints),[i_jnt.getShortName() for i_jnt in ml_skinJoints]))			
        #log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     	

    except Exception,error:
        raise Exception,"%s >>> error : %s"%(_str_funcName,error)


#@r9General.Timer
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
            try:		
                ml_skinJoints = mi_go._ml_skinJoints
                ml_moduleJoints = mi_go._ml_moduleJoints
                ml_segmentHandleJoints = []

                #>>Rig chain  
                #=====================================================================	
                ml_rigJoints = mi_go.build_rigChain()
                l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
                ml_handleJoints = mi_go._mi_module.rig_getRigHandleJoints()

                ml_handleJoints[0].parent = False#Parent to world
                ml_handleJoints[-1].parent = False#Parent to world
            except Exception,error:raise Exception,"Create rig chain! | error: {0}".format(error)

            try:#>>Segment chain  
                #=====================================================================		
                l_toCopy = [i_j.p_nameShort for i_j in mi_go._ml_moduleJoints]
                l_segmentJoints = mc.duplicate(l_toCopy,po=True,ic=True,rc=True)
                ml_segmentJoints = []
                for i,j in enumerate(l_segmentJoints):
                    i_j = cgmMeta.cgmObject(j)
                    i_j.addAttr('cgmTypeModifier','segment',attrType='string',lock=True)
                    i_j.addAttr('cgmIterator',i, lock=True)		    
                    i_j.doName()
                    l_rigJoints[i] = i_j.mNode
                    ml_segmentJoints.append(i_j)
                ml_segmentJoints[0].parent = False#Parent to deformGroup	
                ml_segmentJoints[-1].parent = ml_segmentJoints[-2].mNode#Parent to world
            except Exception,error:raise Exception,"Segment chain! | error: {0}".format(error)

            try:#>>Anchor chain
                #=====================================================================	
                ml_anchors = []

                #Start
                i_startJnt = cgmMeta.cgmObject(mc.duplicate((mi_go._ml_moduleJoints[0].mNode),po=True,ic=True,rc=True)[0])
                i_startJnt.addAttr('cgmType','anchor',attrType='string',lock=True)
                i_startJnt.doName()
                i_startJnt.parent = False
                ml_anchors.append(i_startJnt)

                #End
                l_endJoints = mc.duplicate((mi_go._ml_moduleJoints[-1].mNode),po=True,ic=True,rc=True)
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

                #Influence chain for influencing the surface
                ml_influenceJoints = []
                for i_jnt in mi_go._ml_moduleJoints:
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
            except Exception,error:raise Exception,"Anchor chain chain! | error: {0}".format(error)

            try:#Connection
                _str_subFunc = "Connection"
                time_sub = time.clock() 
                log.info(">>> %s..."%_str_subFunc)  

                #>>> Store em all to our instance
                mi_go._i_rigNull.connectChildNode(i_startJnt,'startAnchor','rigNull')
                mi_go._i_rigNull.connectChildNode(i_endJnt,'endAnchor','rigNull')	
                mi_go._i_rigNull.msgList_connect('anchorJoints',ml_anchors,'rigNull')
                mi_go._i_rigNull.msgList_connect('segmentJoints',ml_segmentJoints,'rigNull')	
                mi_go._i_rigNull.msgList_connect('influenceJoints',ml_influenceJoints,'rigNull')


                mi_go.get_report()

            except Exception,error:raise Exception,"Connect! | error: {0}".format(error)


            try:#Gut connect
                _str_subFunc = "Guts connect"	
                ml_jointsToConnect = [i_startJnt,i_endJnt]
                ml_jointsToConnect.extend(ml_rigJoints)
                ml_jointsToConnect.extend(ml_segmentJoints)    
                ml_jointsToConnect.extend(ml_influenceJoints)

                mi_go.connect_toRigGutsVis( ml_jointsToConnect )

            except Exception,error:raise Exception,"Guts connect! | error: {0}".format(error)
            return True

    return fncWrap(*args, **kws).go()

#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['segmentFKLoli','segmentIK']}
#@r9General.Timer
def build_shapes(self):
    """
    """ 
    try:
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("neckHead.build_rig>>bad self!")
        raise Exception,error
    _str_funcName = "build_shapes(%s)"%self._strShortName
    log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()    
    #>>>Build our Shapes
    #=============================================================
    try:
        l_toBuild = ['segmentFK_Loli','segmentIK']

        mShapeCast.go(self._mi_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     	
    except Exception,error:
        log.error("build_neckHead>>Build shapes fail!")
        raise Exception,error    

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

            if not mi_go.isShaped():	
                raise Exception,"build_controls>>> No shapes found connected"

            try:#>>> Get some special pivot xforms 
                ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')
                l_segmentJoints  = mi_go._i_rigNull.msgList_getMessage('moduleJoints')
                tmpCurve = curves.curveFromObjList(l_segmentJoints)
                basePivotPos = distance.returnWorldSpacePosition("%s.u[%f]"%(tmpCurve,.4))
                log.info("basePivotPos : %s"%basePivotPos)   
                mc.delete(tmpCurve)

            except Exception,error:raise Exception,"Special pivots! | error: {0}".format(error)


            ml_controlsAll = []#we'll append to this list and connect them all at the end 

            try:#Get info
                l_shapes_segmentFKLoli = mi_go._i_rigNull.msgList_getMessage('shape_segmentFKLoli')
                ml_shapes_segmentFKLoli = cgmMeta.validateObjListArg(l_shapes_segmentFKLoli,cgmMeta.cgmObject)

                l_shapes_segmentIK = mi_go._i_rigNull.msgList_getMessage('shape_segmentIK')
                ml_shapes_segmentIK = cgmMeta.validateObjListArg(l_shapes_segmentIK,cgmMeta.cgmObject)

            except Exception,error:raise Exception,"Gather Info! | error: {0}".format(error)

            try:#>>>> IK Handle =============================================================================
                i_IKEnd = ml_shapes_segmentFKLoli[-1]
                #i_IKEnd.parent = ml_shapes_segmentFKLoli[i].mNode

                #i_IKEnd.parent = False

                d_buffer = mControlFactory.registerControl(i_IKEnd,
                                                           typeModifier='ik',addSpacePivots = 2,
                                                           addDynParentGroup = True, addConstraintGroup=True,
                                                           mirrorSide=mi_go._str_mirrorDirection,
                                                           mirrorAxis="translateX,rotateY,rotateZ",                                          
                                                           makeAimable = True,setRotateOrder=4)
                i_IKEnd = d_buffer['instance']	
                i_IKEnd.masterGroup.parent = mi_go._i_deformNull.mNode

                mi_go._i_rigNull.connectChildNode(i_IKEnd,'handleIK','rigNull')#connect
                mi_go._i_rigNull.connectChildNode(i_IKEnd,'settings','rigNull')#Store as settings

                ml_controlsAll.append(i_IKEnd)	

                #Set aims
                i_IKEnd.axisAim = 4
                i_IKEnd.axisUp= 2

            except Exception,error:raise Exception,"IK Handle! | error: {0}".format(error)

            try:#visSub ================================================================================================	
                mPlug_result_moduleSubDriver = mi_go.build_visSub()	
            except Exception,error:raise Exception,"visSub! | error: {0}".format(error)


            try:#>>>> FK Segments =============================================================================	
                if len( ml_shapes_segmentFKLoli )<2:
                    raise Exception,"build_controls>> Must have at least two fk controls"

                ml_segmentsFK = ml_shapes_segmentFKLoli[:-1]

                i_loc = ml_segmentsFK[0].doLoc()
                mc.move (basePivotPos[0],basePivotPos[1],basePivotPos[2], i_loc.mNode)	

                for i,i_obj in enumerate(ml_shapes_segmentFKLoli[1:-1]):#parent
                    i_obj.parent = ml_shapes_segmentFKLoli[i].mNode

                for i,i_obj in enumerate(ml_segmentsFK):
                    if i == 0:
                        copyPivot = i_loc.mNode
                        copyTransform = ml_rigJoints[0].mNode
                    else:
                        copyPivot = None
                        copyTransform = None
                    try:
                        d_buffer = mControlFactory.registerControl(i_obj,copyTransform = copyTransform,addExtraGroups=1,setRotateOrder=5,typeModifier='fk',copyPivot=copyPivot,
                                                                   mirrorSide=mi_go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",
                                                                   ) 
                        log.info(d_buffer)
                        i_obj = d_buffer['instance']
                        try:
                            i_obj.drawStyle = 2#Stick joint draw style	    
                        except:
                            self.log_error("{0} Failed to set drawStyle".format(i_obj.p_nameShort))
                        ml_segmentsFK[i] = i_obj
                    except Exception,error:
                        raise Exception,"%s failed | error: %s"%(i_obj.mNode,error)

                i_loc.delete()
                mi_go._i_rigNull.msgList_connect('controlsFK',ml_segmentsFK,'rigNull')
                ml_controlsAll.extend(ml_segmentsFK)	
                ml_segmentsFK[0].masterGroup.parent = mi_go._i_deformNull.mNode

            except Exception,error:raise Exception,"FK Segments! | error: {0}".format(error)


            try:#>>>> IK Segments =============================================================================	 
                for i_obj in ml_shapes_segmentIK:
                    d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='segIK',
                                                               mirrorSide=mi_go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",	                                               
                                                               setRotateOrder=2)       
                    i_obj = d_buffer['instance']
                    i_obj.masterGroup.parent = mi_go._i_deformNull.mNode
                    mPlug_result_moduleSubDriver.doConnectOut("%s.visibility"%i_obj.mNode)	    

                mi_go._i_rigNull.msgList_connect('segmentHandles',ml_shapes_segmentIK,'rigNull')
                ml_controlsAll.extend(ml_shapes_segmentIK)	
            except Exception,error:raise Exception,"IK Segments! | error: {0}".format(error)


            try:#Connect all controls =============================================================================
                int_strt = mi_go._i_puppet.get_nextMirrorIndex( mi_go._str_mirrorDirection )
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
                    try:
                        mCtrl.addAttr('mirrorIndex', value = (int_strt + i))		
                    except Exception,error: raise Exception,"Failed to register mirror index | mCtrl: %s | %s"%(mCtrl,error)

                mi_go._i_rigNull.msgList_connect('controlsAll',ml_controlsAll)
                mi_go._i_rigNull.moduleSet.extend(ml_controlsAll)#Connect to quick select set	
            except Exception,error:raise Exception,"Connect controls! | error: {0}".format(error)
            return True
    return fncWrap(*args, **kws).go()

def build_deformation(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_deformation(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'process','call':self._fncStep_process},
                                ]
            #=================================================================

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            try:#>>>Get data
                ml_influenceJoints = mi_go._i_rigNull.msgList_get('influenceJoints')
                ml_controlsFK =  mi_go._i_rigNull.msgList_get('controlsFK')    
                ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')    
                ml_segmentJoints = mi_go._i_rigNull.msgList_get('segmentJoints')    
                ml_anchorJoints = mi_go._i_rigNull.msgList_get('anchorJoints')
                ml_segmentHandles = mi_go._i_rigNull.msgList_get('segmentHandles')
                aimVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[0])
                upVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[1])
                mi_handleIK = mi_go._i_rigNull.handleIK
                mi_settings = mi_go._i_rigNull.settings

            except Exception,error:raise Exception,"Gather Data! | error: {0}".format(error)


            #Control Segment
            #====================================================================================
            try:#Control Segment		
                log.info(mi_go._jointOrientation)
                capAim = mi_go._jointOrientation[0].capitalize()
                log.info("capAim: %s"%capAim)
                i_startControl = ml_segmentHandles[0]
                i_endControl = ml_segmentHandles[-1]
                #Create segment
                curveSegmentReturn = SEGMENT.create([i_jnt.mNode for i_jnt in ml_segmentJoints],
                                                             addSquashStretch=True,
                                                             addTwist=True,
                                                             influenceJoints=[ml_influenceJoints[0],ml_influenceJoints[-1]],
                                                             startControl=ml_segmentHandles[0],
                                                             endControl=ml_segmentHandles[-1],
                                                             orientation=mi_go._jointOrientation,
                                                             baseName=mi_go._partName,
                                                             additiveScaleSetup=True,
                                                             connectAdditiveScale=True,	                                             
                                                             moduleInstance=mi_go._mi_module)

                i_curve = curveSegmentReturn['mSegmentCurve']
                i_curve.parent = mi_go._i_rigNull.mNode
                mi_go._i_rigNull.msgList_connect('segmentCurves',[i_curve],'rigNull')
                mi_go._i_rigNull.msgList_connect('segmentJoints',ml_segmentJoints,'rigNull')	#Reconnect to reset. Duplication from createCGMSegment causes issues	
                i_curve.segmentGroup.parent = mi_go._i_rigNull.mNode

            except Exception,error:raise Exception,"Control segment! | error: {0}".format(error)

            """
            try:#>>>Connect segment scale
                mi_distanceBuffer = i_curve	
                cgmMeta.cgmAttr(mi_distanceBuffer,
                                'segmentScaleMult').doTransferTo(mi_go._i_rigNull.settings.mNode)    

            except Exception,error:raise Exception,"Connect Segment Scale! | error: {0}".format(error)"""
            ATTR.copy_to(i_curve.mNode,'segmentScaleMult',mi_go._i_rigNull.settings.mNode,'squashStretch',driven='source')
            ATTR.set_keyable(mi_go._i_rigNull.settings.mNode,'squashStretch',False)            
            
            #MidFactor
            l_keys = i_curve.getSequentialAttrDict('midFactor').keys()
            for i,k in enumerate(l_keys):
                a = 'midFactor_{0}'.format(i)
                ATTR.copy_to(i_curve.mNode,a,mi_handleIK.mNode,driven='source')
                ATTR.set_keyable(mi_handleIK.mNode,a,False)
                if i == 1:
                    ATTR.set(mi_handleIK.mNode,a,1)
            '''
	    try:#>>> Main attribute
		mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)

		mi_loc = mi_handleIK.doLoc()
		mi_loc.addAttr('cgmType','headTwistEnd',attrType='string',lock=True)
		mi_loc.doName()

		mi_loc.rotateOrder = mi_go._jointOrientation#Set orientation to twist last
		mc.pointConstraint(mi_handleIK.mNode,mi_loc.mNode)
		mi_loc.parent = mi_go._i_deformNull#Parent to deform null
		mi_go.connect_toRigGutsVis( mi_loc )

		mNode_decomposeMatrix = cgmMeta.cgmNode(nodeType='decomposeMatrix')
		mNode_decomposeMatrix.doStore('cgmName',mi_go._mi_module)
		mNode_decomposeMatrix.addAttr('cgmType','headTwistEnd',attrType='string',lock=True)
		mNode_decomposeMatrix.doName()

		attributes.doConnectAttr("%s.matrix"%(mi_handleIK.mNode),
		                         "%s.%s"%(mNode_decomposeMatrix.mNode,'inputMatrix'))
		attributes.doConnectAttr("%s.%s"%(mNode_decomposeMatrix.mNode,"outputRotate"),
		                         "%s.%s"%(mi_loc.mNode,"rotate"))            

		mPlug_worldIKEndIn.doConnectIn("%s.outputRotate%s"%(mNode_decomposeMatrix.mNode,
		                                                    mi_go._jointOrientation[0].capitalize()))	    
	    except Exception,error:raise Exception,"Decompose Matrix! | error: {0}".format(error)
	    '''

            try:#Setup top twist driver		
                #Create an fk additive attributes
                str_curve = i_curve.getShortName()
                #fk_drivers = ["%s.r%s"%(i_obj.mNode,mi_go._jointOrientation[0]) for i_obj in ml_controlsFK]
                drivers = ["%s.r%s"%(ml_segmentHandles[-1].mNode,mi_go._jointOrientation[0])]
                #drivers.append("%s.r%s"%(mi_handleIK.mNode,mi_go._jointOrientation[0]))
                #drivers.append(mPlug_worldIKEndIn.p_combinedShortName)
                for mObj in [mi_handleIK,mi_handleIK.dynParentGroup]:
                    drivers.append("%s.r%s"%(mObj.mNode,mi_go._jointOrientation[0]))

                NodeF.createAverageNode(drivers,
                                        [i_curve.mNode,"twistEnd"],1)


            except Exception,error:raise Exception,"Top Twist driver! | error: {0}".format(error)

            try:#Setup bottom twist driver		
                log.info("%s.r%s"%(ml_segmentHandles[0].getShortName(),mi_go._jointOrientation[0]))
                drivers = ["%s.r%s"%(ml_segmentHandles[0].mNode,mi_go._jointOrientation[0])]
                #drivers.append("%s.r%s"%(ml_controlsFK[0].mNode,mi_go._jointOrientation[0]))

                NodeF.createAverageNode(drivers,
                                        [i_curve.mNode,"twistStart"],1)

            except Exception,error:raise Exception,"Bottom Twist driver! | error: {0}".format(error)


            try:#Push squash and stretch multipliers to head
                i_buffer = i_curve

                #>>> Move attrs to handle ik ==========================================================                
                for k in i_curve.getSequentialAttrDict('scaleMult').keys():
                    attrName = 'neckHead_%s'%k
                    cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_handleIK.mNode,attrName,connectSourceToTarget = True)
                    cgmMeta.cgmAttr(mi_handleIK.mNode,attrName,defaultValue = 1,keyable=False,hidden=False)

                cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
                cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
                cgmMeta.cgmAttr(i_curve,'twistMid').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
                cgmMeta.cgmAttr(i_curve,'scaleMidUp').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
                cgmMeta.cgmAttr(i_curve,'scaleMidOut').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
            except Exception,error:raise Exception,"Push segment curve attributes! | error: {0}".format(error)

            return True
    return fncWrap(*args, **kws).go()


def build_deformation2(self):
    """
    Rotate orders
    hips = 3
    """     
    try:
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("neckHead.build_deformationRig>>bad self!")
        raise Exception,error
    _str_funcName = "build_deformation(%s)"%self._strShortName
    log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()         
    try:#>>>Get data
        _str_subFunc = "Get Data"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  

        ml_influenceJoints = self._i_rigNull.msgList_get('influenceJoints')
        ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
        ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')    
        ml_segmentJoints = self._i_rigNull.msgList_get('segmentJoints')    
        ml_anchorJoints = self._i_rigNull.msgList_get('anchorJoints')
        ml_segmentHandles = self._i_rigNull.msgList_get('segmentHandles')
        aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
        upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
        mi_handleIK = self._i_rigNull.handleIK
        mi_settings = self._i_rigNull.settings

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #Control Segment
    #====================================================================================
    try:#Control Segment
        _str_subFunc = "Control Segment"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  

        log.info(self._jointOrientation)
        capAim = self._jointOrientation[0].capitalize()
        log.info("capAim: %s"%capAim)
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
        i_curve.parent = self._i_rigNull.mNode
        self._i_rigNull.msgList_connect('segmentCurves',[i_curve],'rigNull')
        self._i_rigNull.msgList_connect('segmentJoints',ml_segmentJoints,'rigNull')	#Reconnect to reset. Duplication from createCGMSegment causes issues	
        i_curve.segmentGroup.parent = self._i_rigNull.mNode

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#>>>Connect segment scale
        _str_subFunc = "Segment Scale transfer"
        time_sub = time.clock() 
        log.debug(">>> %s..."%_str_subFunc) 	
        mi_distanceBuffer = i_curve.scaleBuffer	
        cgmMeta.cgmAttr(mi_distanceBuffer,'segmentScaleMult ').doTransferTo(self._i_rigNull.settings.mNode)    

        log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#>>> Main attribute
        _str_subFunc = "Top twist driver"
        mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)

        mi_loc = mi_handleIK.doLoc()
        mi_loc.addAttr('cgmType','headTwistEnd',attrType='string',lock=True)
        mi_loc.doName()

        mi_loc.rotateOrder = self._jointOrientation#Set orientation to twist last
        mc.pointConstraint(mi_handleIK.mNode,mi_loc.mNode)
        mi_loc.parent = self._i_deformNull#Parent to deform null
        self.connect_toRigGutsVis( mi_loc )

        mNode_decomposeMatrix = cgmMeta.cgmNode(nodeType='decomposeMatrix')
        mNode_decomposeMatrix.doStore('cgmName',self._mi_module)
        mNode_decomposeMatrix.addAttr('cgmType','headTwistEnd',attrType='string',lock=True)
        mNode_decomposeMatrix.doName()

        attributes.doConnectAttr("%s.matrix"%(mi_handleIK.mNode),"%s.%s"%(mNode_decomposeMatrix.mNode,'inputMatrix'))
        attributes.doConnectAttr("%s.%s"%(mNode_decomposeMatrix.mNode,"outputRotate"),"%s.%s"%(mi_loc.mNode,"rotate"))            

        mPlug_worldIKEndIn.doConnectIn("%s.outputRotate%s"%(mNode_decomposeMatrix.mNode,self._jointOrientation[0].capitalize()))

    except Exception,error:
        raise Exception,error	

    try:#Setup top twist driver
        _str_subFunc = "Top Twist driver"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  

        #Create an fk additive attributes
        str_curve = curveSegmentReturn['mi_segmentCurve'].getShortName()
        #fk_drivers = ["%s.r%s"%(i_obj.mNode,self._jointOrientation[0]) for i_obj in ml_controlsFK]
        drivers = ["%s.r%s"%(ml_segmentHandles[-1].mNode,self._jointOrientation[0])]
        #drivers.append("%s.r%s"%(mi_handleIK.mNode,self._jointOrientation[0]))
        drivers.append(mPlug_worldIKEndIn.p_combinedShortName)

        NodeF.createAverageNode(drivers,
                                [curveSegmentReturn['mi_segmentCurve'].mNode,"twistEnd"],1)

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#Setup bottom twist driver
        _str_subFunc = "Bottom twist driver"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  

        log.info("%s.r%s"%(ml_segmentHandles[0].getShortName(),self._jointOrientation[0]))
        drivers = ["%s.r%s"%(ml_segmentHandles[0].mNode,self._jointOrientation[0])]
        #drivers.append("%s.r%s"%(ml_controlsFK[0].mNode,self._jointOrientation[0]))

        NodeF.createAverageNode(drivers,
                                [curveSegmentReturn['mi_segmentCurve'].mNode,"twistStart"],1)

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#Push squash and stretch multipliers to head
        _str_subFunc = "Push multipliers"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  	
        i_buffer = i_curve.scaleBuffer

        #>>> Move attrs to handle ik ==========================================================
        for k in i_buffer.d_indexToAttr.keys():
            attrName = 'neckHead_%s'%k
            cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_handleIK.mNode,
                                                                      attrName,connectSourceToTarget = True)
            cgmMeta.cgmAttr(mi_handleIK.mNode,attrName,defaultValue = 1,keyable=False)

        cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
        cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
        cgmMeta.cgmAttr(i_curve,'twistMid').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
        cgmMeta.cgmAttr(i_curve,'scaleMidUp').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
        cgmMeta.cgmAttr(i_curve,'scaleMidOut').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     

    return True

def build_rig(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_rig(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'process','call':self._fncStep_process},
                                ]
            #=================================================================

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            try:#>>>Get data
                orientation = modules.returnSettingsData('jointOrientation')
                mi_segmentCurve = mi_go._i_rigNull.msgList_get('segmentCurves')[0]
                mi_segmentAnchorStart = cgmMeta.validateObjArg(mi_segmentCurve.anchorStart,'cgmObject')
                mi_segmentAnchorEnd = cgmMeta.validateObjArg(mi_segmentCurve.anchorEnd,'cgmObject')
                mi_segmentAttachStart = cgmMeta.validateObjArg(mi_segmentCurve.attachStart,'cgmObject')
                mi_segmentAttachEnd = cgmMeta.validateObjArg(mi_segmentCurve.attachEnd ,'cgmObject')
                mi_distanceBuffer = mi_segmentCurve
                mi_moduleParent = False
                if mi_go._mi_module.getMessage('moduleParent'):
                    mi_moduleParent = mi_go._mi_module.moduleParent

                ml_influenceJoints = mi_go._i_rigNull.msgList_get('influenceJoints')
                #ml_segmentSplineJoints = mi_segmentCurve.msgList_get('driverJoints',asMeta = True)

                ml_anchorJoints = mi_go._i_rigNull.msgList_get('anchorJoints')
                ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')    
                ml_rigHandleJoints = mi_go._mi_module.rig_getRigHandleJoints()

                ml_segmentJoints = mi_go._i_rigNull.msgList_get('segmentJoints')	
                ml_segmentHandles = mi_go._i_rigNull.msgList_get('segmentHandles')
                aimVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[0])
                upVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[1])
                mi_handleIK = mi_go._i_rigNull.handleIK
                ml_controlsFK =  mi_go._i_rigNull.msgList_get('controlsFK')    

                log.info("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
                log.info("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
                log.info("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
                log.info("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
                log.info("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)
                log.info("ml_segmentHandles: %s"%[i_o.p_nameShort for i_o in ml_segmentJoints])

            except Exception,error:raise Exception,"Gather data! | error: {0}".format(error)


            #Dynamic parent groups
            #====================================================================================
            try:#>>>> Head dynamicParent	
                #Build our dynamic groups
                ml_headDynParents = [ml_controlsFK[0]]
                if mi_moduleParent:
                    mi_parentRigNull = mi_moduleParent.rigNull
                    if mi_parentRigNull.getMessage('handleIK'):
                        ml_headDynParents.append( mi_parentRigNull.handleIK )	    
                    if mi_parentRigNull.getMessage('cog'):
                        ml_headDynParents.append( mi_parentRigNull.cog )
                ml_headDynParents.extend(mi_handleIK.msgList_get('spacePivots',asMeta = True))
                ml_headDynParents.append(mi_go._i_puppet.masterNull.puppetSpaceObjectsGroup)   
                ml_headDynParents.append(mi_go._i_puppet.masterNull.worldSpaceObjectsGroup)
                log.info(ml_headDynParents)
                log.info([i_obj.getShortName() for i_obj in ml_headDynParents])

                #Add our parents
                i_dynGroup = mi_handleIK.dynParentGroup
                log.info("Dyn group at setup: %s"%i_dynGroup)
                i_dynGroup.dynMode = 2

                for o in ml_headDynParents:
                    i_dynGroup.addDynParent(o)
                i_dynGroup.rebuild()

                i_dynGroup.dynFollow.parent = mi_go._i_masterDeformGroup.mNode

                #mi_go.collect_worldDynDrivers()

            except Exception,error:raise Exception,"dynamic parent groups! | error: {0}".format(error)

            try:#Parent and constrain joints
                #====================================================================================
                parentAttach = mi_go._mi_module.moduleParent.rig_getSkinJoints()[-1].mNode
                mc.parentConstraint(parentAttach,mi_go._i_deformNull.mNode,maintainOffset=True)#constrain
                mc.scaleConstraint(parentAttach,mi_go._i_deformNull.mNode,maintainOffset=True)#Constrain

                #ml_segmentJoints[0].parent = mi_go._i_deformNull.mNode
                #ml_segmentSplineJoints[0].parent = mi_go._i_deformNull.mNode
                for mHandle in mi_segmentCurve.msgList_get('ikHandles',asMeta=True):
                    ml_chain = mHandle.msgList_get('drivenJoints',asMeta=True)
                    ml_chain[0].parent = mi_go._i_deformNull.mNode

                #Put the start and end controls in the heirarchy
                mc.parent(ml_segmentHandles[0].masterGroup.mNode,mi_segmentAttachStart.mNode)
                mc.parent(ml_segmentHandles[-1].masterGroup.mNode,mi_segmentAttachEnd.mNode)

                mi_segmentAnchorStart.parent = mi_go._i_deformNull.mNode#Segment anchor to deform null
                mc.parentConstraint(ml_anchorJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#constrain
                mc.scaleConstraint(ml_anchorJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#Constrain

                mi_segmentAnchorEnd.parent = mi_go._i_deformNull.mNode#Segment end to deform null
                mc.parentConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
                mc.scaleConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)

                #method 1
                ml_rigHandleJoints[0].parent = mi_go._i_deformNull.mNode#Root handle to deform null
                ml_rigHandleJoints[-1].parent = ml_anchorJoints[-1].mNode#Top handle to last anchor

                ml_influenceJoints[0].parent = ml_segmentHandles[0].mNode#base influence to base segment handle
                ml_influenceJoints[-1].parent = ml_segmentHandles[-1].mNode#top influence to top segment handle

                #Parent anchors to controls
                ml_rigHandleJoints[0].parent = mi_go._i_deformNull.mNode   
                ml_anchorJoints[0].parent = mi_go._i_deformNull.mNode
                ml_anchorJoints[-1].parent = mi_handleIK.mNode

                l_rigJoints = [i_jnt.getShortName() for i_jnt in mi_go._get_rigDeformationJoints()]
                for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
                    #Don't try scale constraints in here, they're not viable
                    attachJoint = distance.returnClosestObject(i_jnt.mNode,l_rigJoints)
                    log.info("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
                    pntConstBuffer = mc.pointConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
                    orConstBuffer = mc.orientConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
                    mc.connectAttr((i_jnt.mNode+'.s'),(attachJoint+'.s'))

                mc.connectAttr((mi_handleIK.mNode+'.s'),(ml_rigJoints[-1].mNode+'.s'))

            except Exception,error:raise Exception,"parent/constrain! | error: {0}".format(error)


            #Set up heirarchy, connect master scale
            #====================================================================================
            try:#>>>Connect master scale	
                cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(mi_go._i_masterControl.mNode,'scaleY'))    
            except Exception,error:raise Exception,"master scale! | error: {0}".format(error)


            try:#Set up Scale joints
                #====================================================================================  	
                #Connect our last segment to the sternum if we have a scale joint
                if ml_rigHandleJoints[-1].getMessage('scaleJoint'):
                    i_scaleJoint = ml_rigHandleJoints[-1].scaleJoint
                    attributes.doConnectAttr((mi_handleIK.mNode+'.scale'),(i_scaleJoint.mNode+'.scale')) 
                    cgmMeta.cgmAttr(mi_handleIK,"scale",lock=False,hidden=False,keyable=True)  	    
                else:
                    attributes.doSetLockHideKeyableAttr(mi_handleIK.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
            except Exception,error:raise Exception,"Scale joints! | error: {0}".format(error)


            try:#Vis Network, lock and hide
                #====================================================================================	
                for mCtrl in (ml_controlsFK + [mi_handleIK] + ml_segmentHandles):
                    mCtrl._setControlGroupLocks()	

                for mCtrl in ml_segmentHandles:
                    cgmMeta.cgmAttr(mCtrl,"s%s"%orientation[0],lock=True,hidden=True,keyable=False)  
                for mCtrl in ml_segmentHandles:
                    cgmMeta.cgmAttr(mCtrl,"v",lock=True,hidden=True,keyable=False)

                #cgmMeta.cgmAttr(ml_controlsFK[0],"r{0}".format(mi_go._jointOrientation[0]),
                #                lock=True,hidden=True,keyable=False)

            except Exception,error:raise Exception,"Defaults! | error: {0}".format(error)


            #Set up some defaults
            #====================================================================================
            try:
                mPlug_seg0 = cgmMeta.cgmAttr(ml_segmentHandles[0],'followRoot')
                mPlug_seg0.p_defaultValue = .95
                mPlug_seg0.value = .95
                mPlug_segLast = cgmMeta.cgmAttr(ml_segmentHandles[-1],'followRoot')
                mPlug_segLast.p_defaultValue = .2
                mPlug_segLast.value = .2

                mPlug_extendToEnd = cgmMeta.cgmAttr(mi_handleIK,'twistExtendToEnd')
                mPlug_extendToEnd.p_defaultValue = 1
                mPlug_extendToEnd.value = 1
            except Exception,error:raise Exception,"Defaults! | error: {0}".format(error)

            #Final stuff
            mi_go._set_versionToCurrent()
            return True
    return fncWrap(*args, **kws).go()

def build_rig2(self):
    """
    Rotate orders
    hips = 3
    """    
    try:
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("neckHead.build_deformationRig>>bad self!")
        raise Exception,error

    _str_funcName = "build_rig(%s)"%self._strShortName
    log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()  

    try:#>>>Get data
        _str_subFunc = "Get Data"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  	
        orientation = modules.returnSettingsData('jointOrientation')
        mi_segmentCurve = self._i_rigNull.msgList_get('segmentCurves')[0]
        mi_segmentAnchorStart = mi_segmentCurve.anchorStart
        mi_segmentAnchorEnd = mi_segmentCurve.anchorEnd
        mi_segmentAttachStart = mi_segmentCurve.attachStart
        mi_segmentAttachEnd = mi_segmentCurve.attachEnd 
        mi_distanceBuffer = mi_segmentCurve.scaleBuffer
        mi_moduleParent = False
        if self._mi_module.getMessage('moduleParent'):
            mi_moduleParent = self._mi_module.moduleParent

        ml_influenceJoints = self._i_rigNull.msgList_get('influenceJoints')
        ml_segmentSplineJoints = mi_segmentCurve.msgList_get('driverJoints',asMeta = True)

        ml_anchorJoints = self._i_rigNull.msgList_get('anchorJoints')
        ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')    
        ml_rigHandleJoints = self._mi_module.rig_getRigHandleJoints()

        ml_segmentJoints = self._i_rigNull.msgList_get('segmentJoints')	
        ml_segmentHandles = self._i_rigNull.msgList_get('segmentHandles')
        aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
        upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
        mi_handleIK = self._i_rigNull.handleIK
        ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    

        log.info("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
        log.info("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
        log.info("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
        log.info("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
        log.info("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)
        log.info("ml_segmentHandles: %s"%[i_o.p_nameShort for i_o in ml_segmentJoints])

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #Dynamic parent groups
    #====================================================================================
    try:#>>>> Head dynamicParent
        _str_subFunc = "Head dynParent"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  	
        #Build our dynamic groups
        ml_headDynParents = [ml_controlsFK[0]]
        if mi_moduleParent:
            mi_parentRigNull = mi_moduleParent.rigNull
            if mi_parentRigNull.getMessage('handleIK'):
                ml_headDynParents.append( mi_parentRigNull.handleIK )	    
            if mi_parentRigNull.getMessage('cog'):
                ml_headDynParents.append( mi_parentRigNull.cog )
        ml_headDynParents.extend(mi_handleIK.msgList_get('spacePivots',asMeta = True))
        ml_headDynParents.append(self._i_masterControl)
        log.info(ml_headDynParents)
        log.info([i_obj.getShortName() for i_obj in ml_headDynParents])

        #Add our parents
        i_dynGroup = mi_handleIK.dynParentGroup
        log.info("Dyn group at setup: %s"%i_dynGroup)
        i_dynGroup.dynMode = 2

        for o in ml_headDynParents:
            i_dynGroup.addDynParent(o)
        i_dynGroup.rebuild()

        i_dynGroup.dynFollow.parent = self._i_masterDeformGroup.mNode

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)


    try:#Parent and constrain joints
        #====================================================================================
        _str_subFunc = "Parent and constrain"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  

        parentAttach = self._mi_module.moduleParent.rig_getSkinJoints()[-1].mNode
        mc.parentConstraint(parentAttach,self._i_deformNull.mNode,maintainOffset=True)#constrain
        mc.scaleConstraint(parentAttach,self._i_deformNull.mNode,maintainOffset=True)#Constrain

        ml_segmentJoints[0].parent = self._i_deformNull.mNode
        ml_segmentSplineJoints[0].parent = self._i_deformNull.mNode

        #Put the start and end controls in the heirarchy
        mc.parent(ml_segmentHandles[0].masterGroup.mNode,mi_segmentAttachStart.mNode)
        mc.parent(ml_segmentHandles[-1].masterGroup.mNode,mi_segmentAttachEnd.mNode)

        mi_segmentAnchorStart.parent = self._i_deformNull.mNode#Segment anchor to deform null
        mc.parentConstraint(ml_anchorJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#constrain
        mc.scaleConstraint(ml_anchorJoints[0].mNode,mi_segmentAnchorStart.mNode,maintainOffset=True)#Constrain

        mi_segmentAnchorEnd.parent = self._i_deformNull.mNode#Segment end to deform null
        mc.parentConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)
        mc.scaleConstraint(ml_anchorJoints[-1].mNode,mi_segmentAnchorEnd.mNode,maintainOffset=True)

        #method 1
        ml_rigHandleJoints[0].parent = self._i_deformNull.mNode#Root handle to deform null
        ml_rigHandleJoints[-1].parent = ml_anchorJoints[-1].mNode#Top handle to last anchor

        ml_influenceJoints[0].parent = ml_segmentHandles[0].mNode#base influence to base segment handle
        ml_influenceJoints[-1].parent = ml_segmentHandles[-1].mNode#top influence to top segment handle

        #Parent anchors to controls
        ml_rigHandleJoints[0].parent = self._i_deformNull.mNode   
        ml_anchorJoints[0].parent = self._i_deformNull.mNode
        ml_anchorJoints[-1].parent = mi_handleIK.mNode

        l_rigJoints = [i_jnt.getShortName() for i_jnt in self._get_rigDeformationJoints()]
        for i,i_jnt in enumerate(ml_segmentJoints[:-1]):
            #Don't try scale constraints in here, they're not viable
            attachJoint = distance.returnClosestObject(i_jnt.mNode,l_rigJoints)
            log.info("'%s'>>drives>>'%s'"%(i_jnt.getShortName(),attachJoint))
            pntConstBuffer = mc.pointConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
            orConstBuffer = mc.orientConstraint(i_jnt.mNode,attachJoint,maintainOffset=False,weight=1)
            mc.connectAttr((i_jnt.mNode+'.s'),(attachJoint+'.s'))

        mc.connectAttr((mi_handleIK.mNode+'.s'),(ml_rigJoints[-1].mNode+'.s'))

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #Set up heirarchy, connect master scale
    #====================================================================================
    try:#>>>Connect master scale
        _str_subFunc = "Master scale"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  	
        cgmMeta.cgmAttr(mi_distanceBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(self._i_masterControl.mNode,'scaleY'))    

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#Set up Scale joints
        #====================================================================================  
        _str_subFunc = "Scale Joints"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  	
        #Connect our last segment to the sternum if we have a scale joint
        if ml_rigHandleJoints[-1].getMessage('scaleJoint'):
            i_scaleJoint = ml_rigHandleJoints[-1].scaleJoint
            attributes.doConnectAttr((mi_handleIK.mNode+'.scale'),(i_scaleJoint.mNode+'.scale')) 
            cgmMeta.cgmAttr(mi_handleIK,"scale",lock=False,hidden=False,keyable=True)  	    
        else:
            attributes.doSetLockHideKeyableAttr(mi_handleIK.mNode,lock=True, visible=False, keyable=False, channels=['sx','sy','sz'])
        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#Vis Network, lock and hide
        #====================================================================================
        _str_subFunc = "Lock N Hide"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  	

        for mCtrl in (ml_controlsFK + [mi_handleIK] + ml_segmentHandles):
            mCtrl._setControlGroupLocks()	

        for mCtrl in ml_segmentHandles:
            cgmMeta.cgmAttr(mCtrl,"s%s"%orientation[0],lock=True,hidden=True,keyable=False)  

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #Set up some defaults
    #====================================================================================
    try:
        _str_subFunc = "Default Attributes"
        time_sub = time.clock() 
        log.info(">>> %s..."%_str_subFunc)  	
        mPlug_seg0 = cgmMeta.cgmAttr(ml_segmentHandles[0],'followRoot')
        mPlug_seg0.p_defaultValue = .95
        mPlug_seg0.value = .95
        mPlug_segLast = cgmMeta.cgmAttr(ml_segmentHandles[-1],'followRoot')
        mPlug_segLast.p_defaultValue = .2
        mPlug_segLast.value = .2

        mPlug_extendToEnd = cgmMeta.cgmAttr(mi_handleIK,'twistExtendToEnd')
        mPlug_extendToEnd.p_defaultValue = 1
        mPlug_extendToEnd.value = 1

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

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