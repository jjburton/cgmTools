"""
------------------------------------------
cgm.core.rigger: Limb.leg
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

leg rig builder
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

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta

from cgm.core.rigger.lib import module_Utils as modUtils
from cgm.core.rigger.lib import cgmRigs_sharedData as cgmRigsData

from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF

from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
reload(mControlFactory)
from cgm.core.lib import nameTools

from cgm.core.rigger.lib import rig_Utils as rUtils
from cgm.core.rigger.lib import joint_Utils as jntUtils
reload(rUtils)

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
reload(joints)
#>>> Shapes
#===================================================================
def build_shapes(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_shapes(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Process','call':self._fncStep_process}]
            #=================================================================

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            if mi_go._i_templateNull.handles > 4:
                raise ValueError, "%s.build_shapes>>> Too many handles. don't know how to rig"%(mi_go._strShortName)

            if not mi_go.isRigSkeletonized():
                raise Exception, "%s.build_shapes>>> Must be rig skeletonized to shape"%(mi_go._strShortName)	

            #>>> Get our segment influence joints
            #=============================================================    
            l_influenceChains = []
            ml_influenceChains = []
            for i in range(50):
                buffer = mi_go._i_rigNull.msgList_getMessage('segment%s_InfluenceJoints'%i)
                if buffer:
                    l_influenceChains.append(buffer)
                    ml_influenceChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
                else:
                    break    

            log.info("%s.build_shapes>>> Influence Chains -- cnt: %s | lists: %s"%(mi_go._strShortName,len(l_influenceChains),l_influenceChains))

            #>>>Build our Shapes
            #=============================================================
            try:
                #Segment IK
                ml_segmentIKShapes = []
                for i,ml_chain in enumerate(ml_influenceChains):
                    mShapeCast.go(mi_go._mi_module,['segmentIK'],targetObjects = [i_jnt.mNode for i_jnt in ml_chain] , storageInstance=mi_go)#This will store controls to a dict called    
                    log.info("%s.build_shapes>>> segmentIK chain %s: %s"%(mi_go._strShortName,i,mi_go._md_controlShapes))
                    ml_segmentIKShapes.extend(mi_go._md_controlShapes['segmentIK'])

                    mi_go._i_rigNull.msgList_connect(mi_go._md_controlShapes['segmentIK'],'shape_segmentIK_%s'%i,"rigNull")		

                mi_go._i_rigNull.msgList_connect(ml_segmentIKShapes,'shape_segmentIK',"rigNull")		

                #Rest of it
                l_toBuild = ['segmentFK_Loli','settings','midIK','foot']
                mShapeCast.go(mi_go._mi_module,l_toBuild, storageInstance=mi_go)#This will store controls to a dict called    
                log.info(mi_go._md_controlShapes)
                log.info(mi_go._md_controlPivots)
                mi_go._i_rigNull.msgList_connect(mi_go._md_controlShapes['segmentFK_Loli'],'shape_controlsFK',"rigNull")	
                mi_go._i_rigNull.connectChildNode(mi_go._md_controlShapes['midIK'],'shape_midIK',"rigNull")
                mi_go._i_rigNull.connectChildNode(mi_go._md_controlShapes['settings'],'shape_settings',"rigNull")		
                mi_go._i_rigNull.connectChildNode(mi_go._md_controlShapes['foot'],'shape_foot',"rigNull")

            except Exception,error:raise Exception,"Build shapes fail! | error: {0}".format(error)


            return True	    


    return fncWrap(*args, **kws).go()


#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['rigJoints','influenceJoints','fkJoints','ikJoints','blendJoints']   
__d_preferredAngles__ = {'hip':[0,0,-10],'knee':[0,0,10]}#In terms of aim up out for orientation relative values
__d_controlShapes__ = {'shape':['segmentIK','controlsFK','midIK','settings','foot'],
                       'pivot':['toe','heel','ball','inner','outer']}

def __bindSkeletonSetup__(self):
    """
    TODO: Do I need to connect per joint overrides or will the final group setup get them?
    """
    try:
        if not self._cgmClass == 'JointFactory.go':
            log.error("Not a JointFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("leg.__bindSkeletonSetup__>>bad self!")
        raise Exception,error

    _str_funcName = "__bindSkeletonSetup__(%s)"%self._strShortName
    log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()

    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self._ml_skinJoints or []
    if not self._mi_module.isSkeletonized():
        raise Exception, "%s is not skeletonized yet."%self._strShortName

    try:#Reparent joints
        """
	ml_skinJoints = self.rig_getSkinJoints()
	last_i_jnt = False
	for i,i_jnt in enumerate(ml_skinJoints):
	    if i_jnt.hasAttr('cgmName'):
		if last_i_jnt:i_jnt.parent = last_i_jnt.mNode
		last_i_jnt = i_jnt"""

        ml_moduleJoints = self._mi_module.rigNull.msgList_get('moduleJoints') #Get the module joints
        ml_skinJoints = []

        ml_handleJoints = self._mi_module.rig_getHandleJoints()

        for i,i_jnt in enumerate(ml_moduleJoints):
            ml_skinJoints.append(i_jnt)		
            if i_jnt in ml_handleJoints and i_jnt.getAttr('cgmName') not in ['ball']:
                if i == 0:i_jnt.parent = ml_moduleJoints[0].mNode#Parent head to root
                i_dupJnt = i_jnt.doDuplicate()#Duplicate
                i_dupJnt.addAttr('cgmNameModifier','scale')#Tag
                i_jnt.doName()#Rename
                i_dupJnt.doName()#Rename
                i_dupJnt.parent = i_jnt#Parent
                i_dupJnt.connectChildNode(i_jnt,'rootJoint','scaleJoint')#Connect
                #------------------------------------------------------------
                ml_skinJoints.append(i_dupJnt)#Append
                log.info("%s.__bindSkeletonSetup__ >> Created scale joint for '%s' >> '%s'"%(self._strShortName,i_jnt.getShortName(),i_dupJnt.getShortName()))

        for i,i_jnt in enumerate(ml_handleJoints[1:]):
            i_jnt.parent = ml_handleJoints[i].mNode

        #We have to connect back our lists because duplicated joints with message connections duplicate those connections
        #self._i_rigNull.msgList_connect(ml_moduleJoints,'moduleJoints','module')
        #self._i_rigNull.msgList_connect(ml_skinJoints,'skinJoints','module')

        #self._mi_module.rig_getReport()#report
        log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     	

    except Exception,error:
        log.error("build_leg>>__bindSkeletonSetup__ fail!")
        raise Exception,error   

def build_EXAMPLE(*args, **kws):
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

            try:#connections	
                return True
            except Exception,error:raise Exception,"Connections fail! | error: {0}".format(error)

    return fncWrap(*args, **kws).go()

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

            try:#>>> Get our pivots
                #=============================================================
                for pivot in __d_controlShapes__['pivot']:
                    l_buffer = mi_go._i_templateNull.getMessage("pivot_%s"%pivot,False)
                    if not l_buffer:
                        raise Exception, "%s.build_shapes>>> Template null missing pivot: '%s'"%(mi_go._strShortName,pivot)
                    log.info("pivot (%s) from template: %s"%(pivot,l_buffer))
                    #Duplicate and store the nulls
                    i_pivot = cgmMeta.validateObjArg(l_buffer)
                    i_trans = i_pivot.doDuplicateTransform(True)
                    i_trans.parent = False
                    if pivot in ['inner','outer'] and mi_go._direction == 'right':#if right, rotate the pivots
                        mc.rotate(0,180,0,i_trans.mNode,relative = True, os = True)
                    mi_go._i_rigNull.connectChildNode(i_trans,"pivot_%s"%pivot,"rigNull")

                #Ball Joint pivot
                i_ballJointPivot = mi_go._ml_skinJoints[-1].doDuplicateTransform(True)#dup ball in place
                i_ballJointPivot.parent = False
                i_ballJointPivot.cgmName = 'ballJoint'
                i_ballJointPivot.addAttr('cgmTypeModifier','pivot')
                i_ballJointPivot.doName()
                mi_go._i_rigNull.connectChildNode(i_ballJointPivot,"pivot_ballJoint","rigNull")

                #Ball wiggle pivot
                i_ballWigglePivot = i_ballJointPivot.doDuplicate(po = True)#dup ball in place
                i_ballWigglePivot.parent = False
                i_ballWigglePivot.cgmName = 'ballWiggle'
                i_ballWigglePivot.doName()
                mi_go._i_rigNull.connectChildNode(i_ballWigglePivot,"pivot_ballWiggle","rigNull") 

                mi_toePivot = mi_go._i_rigNull.getMessageAsMeta('pivot_toe') 
                if not mi_toePivot:
                    raise Exception,"%s.build_rigSkeleton>>> missing our toe pivot"%mi_go._strShortName

            except Exception,error:raise Exception,"Pivots fail! | error: {0}".format(error)


            #>>>Create joint chains
            #=============================================================    
            try:#>>Rig chain #=====================================================================	
                ml_rigJoints = mi_go.build_rigChain()
                ml_rigJoints[0].parent = False#Parent to world

            except Exception,error:raise Exception,"Rig chain fail! | error: {0}".format(error)


            try:#>>FK chain#=====================================================================
                ml_fkJoints = mi_go.build_handleChain('fk','fkJoints')
                d_fkRotateOrders = {'hip':0,'ankle':0}#old hip - 5
                ml_fkDriverJoints = []
                for mObj in ml_fkJoints:
                    log.info("ro check: %s"%(mObj.p_nameShort))	    
                    if mObj.getAttr('cgmName') in d_fkRotateOrders.keys():
                        mObj.rotateOrder = d_fkRotateOrders.get(mObj.cgmName)   	

                if mi_go._str_mirrorDirection == 'Right':#mirror control setup
                    mi_go.mirrorChainOrientation(ml_fkJoints)#New 

                    ml_fkDriverJoints = mi_go.build_handleChain('fkAttach','fkAttachJoints')
                    for i,mJoint in enumerate(ml_fkJoints):
                        log.info("Mirror connect: %s | %s"%(i,mJoint.p_nameShort))
                        mJoint.connectChildNode(ml_fkDriverJoints[i],"attachJoint","rootJoint")
                        #attributes.doConnectAttr(("%s.rotateOrder"%mJoint.mNode),("%s.rotateOrder"%ml_fkDriverJoints[i].mNode))
                        cgmMeta.cgmAttr(mJoint.mNode,"rotateOrder").doConnectOut("%s.rotateOrder"%ml_fkDriverJoints[i].mNode)
                        #mJoint.rotateOrder = ml_fkDriverJoints[i].rotateOrder

            except Exception,error:raise Exception,"FK Chain fail! | error: {0}".format(error)


            try:#>>Blend chain #=====================================================================	
                ml_blendJoints = mi_go.build_handleChain('blend','blendJoints')

            except Exception,error:raise Exception,"Blend chain fail! | error: {0}".format(error)


            try:#>>IK chain #=====================================================================
                """Important - we're going to set our preferred angles on the main ik joints so ik works as expected"""
                ml_ikJoints = mi_go.build_handleChain('ik','ikJoints')

                for i_jnt in ml_ikJoints:
                    if i_jnt.cgmName in __d_preferredAngles__.keys():
                        log.info("preferred angles(%s)>>> %s"%(i_jnt.cgmName,__d_preferredAngles__.get(i_jnt.cgmName)))
                        for i,v in enumerate(__d_preferredAngles__.get(i_jnt.cgmName)):	  
                            i_jnt.__setattr__('preferredAngle%s'%mi_go._jointOrientation[i].upper(),v)	    

            except Exception,error:raise Exception,"IK Chain fail! | error: {0}".format(error)


            try:#>>IK PV chain #=====================================================================	
                ml_ikPVJoints = []
                for i_jnt in ml_ikJoints[:3]:
                    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
                    i_new.addAttr('cgmTypeModifier','ikPV',attrType='string',lock=True)
                    i_new.doName()
                    if ml_ikPVJoints:#if we have data, parent to last
                        i_new.parent = ml_ikPVJoints[-1]
                    ml_ikPVJoints.append(i_new)	

            except Exception,error:raise Exception,"IK PV Chain fail! | error: {0}".format(error)


            try:#>>IK NoFlip chain #=====================================================================
                ml_ikNoFlipJoints = []
                for i_jnt in ml_ikJoints[:3]:
                    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
                    i_new.addAttr('cgmTypeModifier','ikNoFlip',attrType='string',lock=True)
                    i_new.doName()
                    if ml_ikNoFlipJoints:#if we have data, parent to last
                        i_new.parent = ml_ikNoFlipJoints[-1]
                    ml_ikNoFlipJoints.append(i_new)		

            except Exception,error:raise Exception,"No flip chain fail! | error: {0}".format(error)

            try:#>>Make our toe #=====================================================================
                #Do the toe
                i_toeJoint = ml_ikJoints[-1].doDuplicate()
                log.info("i_toeJoint: {0}".format(i_toeJoint))
                log.info("mi_toePivot: {0}".format(mi_toePivot))                
                Snap.go(i_toeJoint, mi_toePivot.mNode,True,False)
                joints.doCopyJointOrient(ml_ikJoints[-1].mNode,i_toeJoint.mNode)
                i_toeJoint.addAttr('cgmName','toe',attrType='string',lock=True)	
                i_toeJoint.addAttr('cgmTypeModifier','ik',attrType='string',lock=True)
                i_toeJoint.doName()

                i_toeJoint.parent = ml_ikJoints[-1].mNode
                ml_ikJoints.append(i_toeJoint)
                mi_go._i_rigNull.msgList_append(i_toeJoint,'ikJoints','rigNull')

            except Exception,error:raise Exception,"Toe creation fail! | error: {0}".format(error)


            try:#>>Influence chain #=====================================================================
                d_influenceChainReturns = mi_go.build_simpleInfluenceChains(True)
                ml_influenceChains = d_influenceChainReturns['ml_influenceChains']
                ml_influenceJoints= d_influenceChainReturns['ml_influenceJoints']	
                ml_segmentHandleJoints = d_influenceChainReturns['ml_segmentHandleJoints']

                if len(ml_segmentHandleJoints)!=3:
                    raise Exception,"Don't have 3 influence joints: '%s'"%(l_segmentHandleJoints)

            except Exception,error:raise Exception,"Influence chain fail! | error: {0}".format(error)

            try:#>>Segment chain  #=====================================================================
                ml_segmentChains = mi_go.build_segmentChains(ml_segmentHandleJoints,True)

            except Exception,error:raise Exception,"Segment chain fail! | error: {0}".format(error)


            try:#>>> Store em all to our instance #=====================================================================
                mi_go._i_rigNull.msgList_connect(ml_ikNoFlipJoints,'ikNoFlipJoints',"rigNull")
                mi_go._i_rigNull.msgList_connect(ml_ikPVJoints,'ikPVJoints',"rigNull")
                mi_go._i_rigNull.msgList_connect(ml_influenceJoints,'influenceJoints',"rigNull")

                log.info("fkJoints>> %s"%mi_go._i_rigNull.msgList_getMessage('fkJoints',False))
                log.info("ikJoints>> %s"%mi_go._i_rigNull.msgList_getMessage('ikJoints',False))
                log.info("blendJoints>> %s"%mi_go._i_rigNull.msgList_getMessage('blendJoints',False))
                log.info("influenceJoints>> %s"%mi_go._i_rigNull.msgList_getMessage('influenceJoints',False))
                log.info("ikNoFlipJoints>> %s"%mi_go._i_rigNull.msgList_getMessage('ikNoFlipJoints',False))
                log.info("ikPVJoints>> %s"%mi_go._i_rigNull.msgList_getMessage('ikPVJoints',False))
            except Exception,error:raise Exception,"Storage fail! | error: {0}".format(error)

            try:#Vis connect =====================================================================
                ml_jointsToConnect = []
                ml_jointsToConnect.extend(ml_rigJoints)    
                ml_jointsToConnect.extend(ml_ikJoints)
                ml_jointsToConnect.extend(ml_ikNoFlipJoints)    
                ml_jointsToConnect.extend(ml_ikPVJoints)    
                ml_jointsToConnect.extend(ml_influenceJoints)   
                if ml_fkDriverJoints:ml_jointsToConnect.extend(ml_fkDriverJoints)    

                for ml_chain in ml_segmentChains + ml_influenceChains:
                    ml_jointsToConnect.extend(ml_chain)

                #Vis only
                mi_go.connect_toRigGutsVis(ml_jointsToConnect,vis=True)
            except Exception,error:raise Exception,"Vis connect fail! | error: {0}".format(error)

            return True	    

    return fncWrap(*args, **kws).go()

def build_foot(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_foot(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Process','call':self._fncStep_process}]
            #=================================================================

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            try:#>>>Get data
                ml_controlsFK =  mi_go._i_rigNull.msgList_get('controlsFK')    
                ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')
                ml_blendJoints = mi_go._i_rigNull.msgList_get('blendJoints')
                ml_fkJoints = mi_go._i_rigNull.msgList_get('fkJoints')
                ml_ikJoints = mi_go._i_rigNull.msgList_get('ikJoints')
                ml_ikPVJoints = mi_go._i_rigNull.msgList_get('ikPVJoints')
                ml_ikNoFlipJoints = mi_go._i_rigNull.msgList_get('ikNoFlipJoints')

                mi_settings = mi_go._i_rigNull.settings

                mi_pivToe = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_toe'),cgmMeta.cgmObject)
                mi_pivHeel = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_heel'),cgmMeta.cgmObject)
                mi_pivBall = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_ball'),cgmMeta.cgmObject)
                mi_pivInner = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_inner'),cgmMeta.cgmObject)
                mi_pivOuter = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_outer'),cgmMeta.cgmObject)      
                mi_pivBallJoint = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_ballJoint'),cgmMeta.cgmObject)      
                mi_pivBallWiggle = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_ballWiggle'),cgmMeta.cgmObject)      

                aimVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[0])
                upVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[1])
                outVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[2])  

                mi_controlIK = mi_go._i_rigNull.controlIK

            except Exception,error:raise Exception,"Gather Data fail! | error: {0}".format(error)

            #=============================================================    
            try:#>>>Attr setup
                mi_pivHeel.parent = mi_controlIK.mNode#heel to foot
                mi_pivToe.parent = mi_pivHeel.mNode#toe to heel    
                mi_pivOuter.parent = mi_pivToe.mNode#outer to heel
                mi_pivInner.parent = mi_pivOuter.mNode#inner to outer
                mi_pivBall.parent = mi_pivInner.mNode#pivBall to toe
                mi_pivBallJoint.parent = mi_pivBall.mNode#ballJoint to ball        
                mi_pivBallWiggle.parent = mi_pivInner.mNode

                #for each of our pivots, we're going to zero group them
                for pivot in [mi_pivToe,mi_pivHeel,mi_pivBall,mi_pivInner,mi_pivOuter,mi_pivBallJoint,mi_pivBallWiggle]:
                    pivot.rotateOrder = 0
                    pivot.doZeroGroup()
                    log.info("pivot: %s"%pivot.getShortName())    

                #Add driving attrs
                mPlug_roll = cgmMeta.cgmAttr(mi_controlIK,'roll',attrType='float',defaultValue = 0,keyable = True)
                mPlug_toeLift = cgmMeta.cgmAttr(mi_controlIK,'toeLift',attrType='float',initialValue = 35, defaultValue = 35,keyable = True)
                mPlug_toeStaighten = cgmMeta.cgmAttr(mi_controlIK,'toeStaighten',attrType='float',initialValue = 65,defaultValue = 70,keyable = True)
                mPlug_toeWiggle= cgmMeta.cgmAttr(mi_controlIK,'toeWiggle',attrType='float',defaultValue = 0,keyable = True)
                mPlug_toeSpin = cgmMeta.cgmAttr(mi_controlIK,'toeSpin',attrType='float',defaultValue = 0,keyable = True)
                mPlug_lean = cgmMeta.cgmAttr(mi_controlIK,'lean',attrType='float',defaultValue = 0,keyable = True)
                mPlug_side = cgmMeta.cgmAttr(mi_controlIK,'bank',attrType='float',defaultValue = 0,keyable = True)
                mPlug_kneeSpin = cgmMeta.cgmAttr(mi_controlIK,'kneeSpin',attrType='float',defaultValue = 0,keyable = True)
                mPlug_stretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
                mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee',attrType='int',defaultValue = 0,minValue=0,maxValue=1,keyable = True)
                mPlug_lengthUpr= cgmMeta.cgmAttr(mi_controlIK,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
                mPlug_lengthLwr = cgmMeta.cgmAttr(mi_controlIK,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)

            except Exception,error:raise Exception,"Attr setup fail! | error: {0}".format(error)

            try:#heel setup
                #Add driven attrs
                mPlug_heelClampResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_heel',attrType='float',keyable = False,hidden=True)
                #mPlug_heelResult = cgmMeta.cgmAttr(mi_controlIK,'result_heel',attrType='float',keyable = False,hidden=True)

                #Setup the heel roll
                #Clamp
                NodeF.argsToNodes("%s = clamp(%s,0,%s)"%(mPlug_heelClampResult.p_combinedShortName,
                                                         mPlug_roll.p_combinedShortName,
                                                         mPlug_roll.p_combinedShortName)).doBuild()
                #Inversion
                #NodeF.argsToNodes("%s = -%s"%(mPlug_heelResult.p_combinedShortName,mPlug_heelClampResult.p_combinedShortName)).doBuild()
                mPlug_heelClampResult.doConnectOut("%s.r%s"%(mi_pivHeel.mNode,mi_go._jointOrientation[2].lower()))

            except Exception,error:raise Exception,"Heel setup fail! | error: {0}".format(error)


            try:#ball setup
                """
		Schleifer's
		ball_loc.rx = (linstep(0,$toeLift, $roll) * (1-(linstep( $toeLift, $toeStraight, $roll))) * $roll;
				ballToeLiftRoll        md   ( pma   toeToeStraightRoll                    md  
					1               4       3             2                            5
		"""
                mPlug_ballToeLiftRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_ballToeLiftRoll',attrType='float',keyable = False,hidden=True)
                mPlug_toeStraightRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_toeStraightRoll',attrType='float',keyable = False,hidden=True)
                mPlug_oneMinusToeResultResult = cgmMeta.cgmAttr(mi_controlIK,'result_pma_one_minus_toeStraitRollRange',attrType='float',keyable = False,hidden=True)
                mPlug_ball_x_toeResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_roll_x_toeResult',attrType='float',keyable = False,hidden=True)
                mPlug_all_x_rollResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_all_x_rollResult',attrType='float',keyable = False,hidden=True)

                arg1 = "%s = setRange(0,1,0,%s,%s)"%(mPlug_ballToeLiftRollResult.p_combinedShortName,
                                                     mPlug_toeLift.p_combinedShortName,
                                                     mPlug_roll.p_combinedShortName)
                arg2 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeStraightRollResult.p_combinedShortName,
                                                      mPlug_toeLift.p_combinedShortName,
                                                      mPlug_toeStaighten.p_combinedShortName,
                                                      mPlug_roll.p_combinedShortName)
                arg3 = "%s = 1 - %s"%(mPlug_oneMinusToeResultResult.p_combinedShortName,
                                      mPlug_toeStraightRollResult.p_combinedShortName)

                arg4 = "%s = %s * %s"%(mPlug_ball_x_toeResult.p_combinedShortName,
                                       mPlug_oneMinusToeResultResult.p_combinedShortName,
                                       mPlug_ballToeLiftRollResult.p_combinedShortName)

                arg5 = "%s = %s * %s"%(mPlug_all_x_rollResult.p_combinedShortName,
                                       mPlug_ball_x_toeResult.p_combinedShortName,
                                       mPlug_roll.p_combinedShortName)

                for arg in [arg1,arg2,arg3,arg4,arg5]:
                    NodeF.argsToNodes(arg).doBuild()

                mPlug_all_x_rollResult.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,mi_go._jointOrientation[2].lower()))

            except Exception,error:raise Exception,"Ball setup fail! | error: {0}".format(error)

            try:#toe setup    
                """
		Schleifer's
		toe_loc.rotateX = linstep($toeLift, $toeStraight,$roll) * $roll;
				      setRange                           md
					 1                                2
		"""
                mPlug_toeRangeResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_toeLiftStraightRoll',attrType='float',keyable = False,hidden=True)
                mPlug_toe_x_rollResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_toeRange_x_roll',attrType='float',keyable = False,hidden=True)

                arg1 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeRangeResult.p_combinedShortName,
                                                      mPlug_toeLift.p_combinedShortName,
                                                      mPlug_toeStaighten.p_combinedShortName,                                         
                                                      mPlug_roll.p_combinedShortName)
                arg2 = "%s = %s * %s"%(mPlug_toe_x_rollResult.p_combinedShortName,
                                       mPlug_toeRangeResult.p_combinedShortName,
                                       mPlug_roll.p_combinedShortName)
                for arg in [arg1,arg2]:
                    NodeF.argsToNodes(arg).doBuild()    

                mPlug_toe_x_rollResult.doConnectOut("%s.r%s"%(mi_pivToe.mNode,mi_go._jointOrientation[2].lower()))

            except Exception,error:raise Exception,"Toe Setup fail! | error: {0}".format(error)


            try:#bank setup 
                """
		Schleifer's
		outside_loc.rotateZ = min($side,0);
		clamp1
		inside_loc.rotateZ = max(0,$side);
		clamp2
		"""    
                mPlug_outerResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_outerBank',attrType='float',keyable = False,hidden=True)
                mPlug_innerResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_innerBank',attrType='float',keyable = False,hidden=True)

                arg1 = "%s = clamp(-180,0,%s)"%(mPlug_outerResult.p_combinedShortName,                                  
                                                mPlug_side.p_combinedShortName)
                arg2 = "%s = clamp(0,180,%s)"%(mPlug_innerResult.p_combinedShortName,
                                               mPlug_side.p_combinedShortName)
                for arg in [arg1,arg2]:
                    NodeF.argsToNodes(arg).doBuild()   

                mPlug_outerResult.doConnectOut("%s.r%s"%(mi_pivOuter.mNode,mi_go._jointOrientation[0].lower()))
                mPlug_innerResult.doConnectOut("%s.r%s"%(mi_pivInner.mNode,mi_go._jointOrientation[0].lower()))

            except Exception,error:raise Exception,"Bank setup fail! | error: {0}".format(error)


            try:#lean setup 
                """
		Schleifer's
		ball_loc.rotateZ = $lean;
		"""    
                if mi_go._mi_module.getAttr('cgmDirection') and mi_go._mi_module.cgmDirection.lower() in ['right']:
                    str_leanDriver = "%s.r%s = -%s"%(mi_pivBallJoint.mNode,mi_go._jointOrientation[0].lower(),
                                                     mPlug_lean.p_combinedShortName)
                    NodeF.argsToNodes(str_leanDriver).doBuild()
                else:
                    mPlug_lean.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,mi_go._jointOrientation[0].lower()))

            except Exception,error:raise Exception,"lean setup fail! | error: {0}".format(error)


            try:#toe spin setup 
                """
		Schleifer's
		toe_loc.rotateY = $spin;
		"""  
                if mi_go._mi_module.getAttr('cgmDirection') and mi_go._mi_module.cgmDirection.lower() in ['right']:
                    str_leanDriver = "%s.r%s = -%s"%(mi_pivToe.mNode,mi_go._jointOrientation[1].lower(),
                                                     mPlug_toeSpin.p_combinedShortName)
                    NodeF.argsToNodes(str_leanDriver).doBuild()
                else:
                    mPlug_toeSpin.doConnectOut("%s.r%s"%(mi_pivToe.mNode,mi_go._jointOrientation[1].lower()))

            except Exception,error:raise Exception,"Toe spin fail! | error: {0}".format(error)


            try:#toe wiggle setup 
                """
		Schleifer's
		toeWiggle_loc.rx = $wiggle;
		""" 
                mPlug_toeWiggle.doConnectOut("%s.r%s"%(mi_pivBallWiggle.mNode,mi_go._jointOrientation[2].lower()))

            except Exception,error:raise Exception,"Toe wiggle fail! | error: {0}".format(error)

            return True	    

    return fncWrap(*args, **kws).go()

def build_foot2(self):
    """
    """
    try:#===================================================
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("leg.build_foot>>bad self!")
        raise Exception,error

    _str_funcName = "build_foot(%s)"%self._strShortName
    log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()

    try:#>>>Get data
        _str_subFunc = "Get Data"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
        ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
        ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
        ml_fkJoints = self._i_rigNull.msgList_get('fkJoints')
        ml_ikJoints = self._i_rigNull.msgList_get('ikJoints')
        ml_ikPVJoints = self._i_rigNull.msgList_get('ikPVJoints')
        ml_ikNoFlipJoints = self._i_rigNull.msgList_get('ikNoFlipJoints')

        mi_settings = self._i_rigNull.settings

        mi_pivToe = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_toe'),cgmMeta.cgmObject)
        mi_pivHeel = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_heel'),cgmMeta.cgmObject)
        mi_pivBall = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ball'),cgmMeta.cgmObject)
        mi_pivInner = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_inner'),cgmMeta.cgmObject)
        mi_pivOuter = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_outer'),cgmMeta.cgmObject)      
        mi_pivBallJoint = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ballJoint'),cgmMeta.cgmObject)      
        mi_pivBallWiggle = cgmMeta.validateObjArg(self._i_rigNull.getMessage('pivot_ballWiggle'),cgmMeta.cgmObject)      

        aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
        upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
        outVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[2])  

        mi_controlIK = self._i_rigNull.controlIK

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #=============================================================    
    try:#>>>Attr setup
        _str_subFunc = "Attribute Setup"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        mi_pivHeel.parent = mi_controlIK.mNode#heel to foot
        mi_pivToe.parent = mi_pivHeel.mNode#toe to heel    
        mi_pivOuter.parent = mi_pivToe.mNode#outer to heel
        mi_pivInner.parent = mi_pivOuter.mNode#inner to outer
        mi_pivBall.parent = mi_pivInner.mNode#pivBall to toe
        mi_pivBallJoint.parent = mi_pivBall.mNode#ballJoint to ball        
        mi_pivBallWiggle.parent = mi_pivInner.mNode

        #for each of our pivots, we're going to zero group them
        for pivot in [mi_pivToe,mi_pivHeel,mi_pivBall,mi_pivInner,mi_pivOuter,mi_pivBallJoint,mi_pivBallWiggle]:
            pivot.rotateOrder = 0
            pivot.doZeroGroup()
            log.info("pivot: %s"%pivot.getShortName())    

        #Add driving attrs
        mPlug_roll = cgmMeta.cgmAttr(mi_controlIK,'roll',attrType='float',defaultValue = 0,keyable = True)
        mPlug_toeLift = cgmMeta.cgmAttr(mi_controlIK,'toeLift',attrType='float',initialValue = 35, defaultValue = 35,keyable = True)
        mPlug_toeStaighten = cgmMeta.cgmAttr(mi_controlIK,'toeStaighten',attrType='float',initialValue = 65,defaultValue = 70,keyable = True)
        mPlug_toeWiggle= cgmMeta.cgmAttr(mi_controlIK,'toeWiggle',attrType='float',defaultValue = 0,keyable = True)
        mPlug_toeSpin = cgmMeta.cgmAttr(mi_controlIK,'toeSpin',attrType='float',defaultValue = 0,keyable = True)
        mPlug_lean = cgmMeta.cgmAttr(mi_controlIK,'lean',attrType='float',defaultValue = 0,keyable = True)
        mPlug_side = cgmMeta.cgmAttr(mi_controlIK,'bank',attrType='float',defaultValue = 0,keyable = True)
        mPlug_kneeSpin = cgmMeta.cgmAttr(mi_controlIK,'kneeSpin',attrType='float',defaultValue = 0,keyable = True)
        mPlug_stretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
        mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee',attrType='int',defaultValue = 0,minValue=0,maxValue=1,keyable = True)
        mPlug_lengthUpr= cgmMeta.cgmAttr(mi_controlIK,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
        mPlug_lengthLwr = cgmMeta.cgmAttr(mi_controlIK,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#heel setup
        _str_subFunc = "Heel Setup"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50) 

        #Add driven attrs
        mPlug_heelClampResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_heel',attrType='float',keyable = False,hidden=True)
        #mPlug_heelResult = cgmMeta.cgmAttr(mi_controlIK,'result_heel',attrType='float',keyable = False,hidden=True)

        #Setup the heel roll
        #Clamp
        NodeF.argsToNodes("%s = clamp(%s,0,%s)"%(mPlug_heelClampResult.p_combinedShortName,
                                                 mPlug_roll.p_combinedShortName,
                                                 mPlug_roll.p_combinedShortName)).doBuild()
        #Inversion
        #NodeF.argsToNodes("%s = -%s"%(mPlug_heelResult.p_combinedShortName,mPlug_heelClampResult.p_combinedShortName)).doBuild()
        mPlug_heelClampResult.doConnectOut("%s.r%s"%(mi_pivHeel.mNode,self._jointOrientation[2].lower()))

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)  

    try:#ball setup
        """
	Schleifer's
	ball_loc.rx = (linstep(0,$toeLift, $roll) * (1-(linstep( $toeLift, $toeStraight, $roll))) * $roll;
			ballToeLiftRoll        md   ( pma   toeToeStraightRoll                    md  
				1               4       3             2                            5
	"""
        _str_subFunc = "Ball setup"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        mPlug_ballToeLiftRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_ballToeLiftRoll',attrType='float',keyable = False,hidden=True)
        mPlug_toeStraightRollResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_toeStraightRoll',attrType='float',keyable = False,hidden=True)
        mPlug_oneMinusToeResultResult = cgmMeta.cgmAttr(mi_controlIK,'result_pma_one_minus_toeStraitRollRange',attrType='float',keyable = False,hidden=True)
        mPlug_ball_x_toeResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_roll_x_toeResult',attrType='float',keyable = False,hidden=True)
        mPlug_all_x_rollResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_all_x_rollResult',attrType='float',keyable = False,hidden=True)

        arg1 = "%s = setRange(0,1,0,%s,%s)"%(mPlug_ballToeLiftRollResult.p_combinedShortName,
                                             mPlug_toeLift.p_combinedShortName,
                                             mPlug_roll.p_combinedShortName)
        arg2 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeStraightRollResult.p_combinedShortName,
                                              mPlug_toeLift.p_combinedShortName,
                                              mPlug_toeStaighten.p_combinedShortName,
                                              mPlug_roll.p_combinedShortName)
        arg3 = "%s = 1 - %s"%(mPlug_oneMinusToeResultResult.p_combinedShortName,
                              mPlug_toeStraightRollResult.p_combinedShortName)

        arg4 = "%s = %s * %s"%(mPlug_ball_x_toeResult.p_combinedShortName,
                               mPlug_oneMinusToeResultResult.p_combinedShortName,
                               mPlug_ballToeLiftRollResult.p_combinedShortName)

        arg5 = "%s = %s * %s"%(mPlug_all_x_rollResult.p_combinedShortName,
                               mPlug_ball_x_toeResult.p_combinedShortName,
                               mPlug_roll.p_combinedShortName)

        for arg in [arg1,arg2,arg3,arg4,arg5]:
            NodeF.argsToNodes(arg).doBuild()

        mPlug_all_x_rollResult.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,self._jointOrientation[2].lower()))

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#toe setup    
        """
	Schleifer's
	toe_loc.rotateX = linstep($toeLift, $toeStraight,$roll) * $roll;
			      setRange                           md
				 1                                2
	"""
        _str_subFunc = "Toe setup"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        mPlug_toeRangeResult = cgmMeta.cgmAttr(mi_controlIK,'result_range_toeLiftStraightRoll',attrType='float',keyable = False,hidden=True)
        mPlug_toe_x_rollResult = cgmMeta.cgmAttr(mi_controlIK,'result_md_toeRange_x_roll',attrType='float',keyable = False,hidden=True)

        arg1 = "%s = setRange(0,1,%s,%s,%s)"%(mPlug_toeRangeResult.p_combinedShortName,
                                              mPlug_toeLift.p_combinedShortName,
                                              mPlug_toeStaighten.p_combinedShortName,                                         
                                              mPlug_roll.p_combinedShortName)
        arg2 = "%s = %s * %s"%(mPlug_toe_x_rollResult.p_combinedShortName,
                               mPlug_toeRangeResult.p_combinedShortName,
                               mPlug_roll.p_combinedShortName)
        for arg in [arg1,arg2]:
            NodeF.argsToNodes(arg).doBuild()    

        mPlug_toe_x_rollResult.doConnectOut("%s.r%s"%(mi_pivToe.mNode,self._jointOrientation[2].lower()))

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error) 

    try:#bank setup 
        """
	Schleifer's
	outside_loc.rotateZ = min($side,0);
	clamp1
	inside_loc.rotateZ = max(0,$side);
	clamp2
	"""    
        _str_subFunc = "Bank setup"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  	

        mPlug_outerResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_outerBank',attrType='float',keyable = False,hidden=True)
        mPlug_innerResult = cgmMeta.cgmAttr(mi_controlIK,'result_clamp_innerBank',attrType='float',keyable = False,hidden=True)

        arg1 = "%s = clamp(-180,0,%s)"%(mPlug_outerResult.p_combinedShortName,                                  
                                        mPlug_side.p_combinedShortName)
        arg2 = "%s = clamp(0,180,%s)"%(mPlug_innerResult.p_combinedShortName,
                                       mPlug_side.p_combinedShortName)
        for arg in [arg1,arg2]:
            NodeF.argsToNodes(arg).doBuild()   

        mPlug_outerResult.doConnectOut("%s.r%s"%(mi_pivOuter.mNode,self._jointOrientation[0].lower()))
        mPlug_innerResult.doConnectOut("%s.r%s"%(mi_pivInner.mNode,self._jointOrientation[0].lower()))

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)      

    try:#lean setup 
        """
	Schleifer's
	ball_loc.rotateZ = $lean;
	"""    
        _str_subFunc = "Lean setup"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        if self._mi_module.getAttr('cgmDirection') and self._mi_module.cgmDirection.lower() in ['right']:
            str_leanDriver = "%s.r%s = -%s"%(mi_pivBallJoint.mNode,self._jointOrientation[0].lower(),
                                             mPlug_lean.p_combinedShortName)
            NodeF.argsToNodes(str_leanDriver).doBuild()
        else:
            mPlug_lean.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,self._jointOrientation[0].lower()))

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#toe spin setup 
        """
	Schleifer's
	toe_loc.rotateY = $spin;
	"""  
        _str_subFunc = "Toe spin setup"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        if self._mi_module.getAttr('cgmDirection') and self._mi_module.cgmDirection.lower() in ['right']:
            str_leanDriver = "%s.r%s = -%s"%(mi_pivToe.mNode,self._jointOrientation[1].lower(),
                                             mPlug_toeSpin.p_combinedShortName)
            NodeF.argsToNodes(str_leanDriver).doBuild()
        else:
            mPlug_toeSpin.doConnectOut("%s.r%s"%(mi_pivToe.mNode,self._jointOrientation[1].lower()))

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#toe wiggle setup 
        """
	Schleifer's
	toeWiggle_loc.rx = $wiggle;
	""" 
        _str_subFunc = "Toe wiggle setup"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        mPlug_toeWiggle.doConnectOut("%s.r%s"%(mi_pivBallWiggle.mNode,self._jointOrientation[2].lower()))

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     	
    return True

def build_FKIK(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_FKIK(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Process','call':self._fncStep_process}]
            #=================================================================

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']
            try:#>>>Get data
                ml_toParentChains = []

                ml_controlsFK =  mi_go._i_rigNull.msgList_get('controlsFK')   
                ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')
                ml_blendJoints = mi_go._i_rigNull.msgList_get('blendJoints')
                ml_fkJoints = mi_go._i_rigNull.msgList_get('fkJoints')
                ml_fkAttachJoints = []
                if mi_go._str_mirrorDirection == 'Right':#mirror control setup
                    log.info("getting attach joints")  
                    ml_fkAttachJoints = mi_go._i_rigNull.msgList_get('fkAttachJoints')
                    ml_toParentChains.append(ml_fkAttachJoints)

                ml_ikJoints = mi_go._i_rigNull.msgList_get('ikJoints')
                if len(ml_ikJoints) != 5:raise Exception,"Length of ikJoints is wrong. %s != 4"%(len(ml_ikJoints))
                ml_ikPVJoints = mi_go._i_rigNull.msgList_get('ikPVJoints')
                ml_ikNoFlipJoints = mi_go._i_rigNull.msgList_get('ikNoFlipJoints')

                mi_settings = mi_go._i_rigNull.settings

                mi_pivToe = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_toe'),cgmMeta.cgmObject)
                mi_pivHeel = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_heel'),cgmMeta.cgmObject)
                mi_pivBall = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_ball'),cgmMeta.cgmObject)
                mi_pivInner = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_inner'),cgmMeta.cgmObject)
                mi_pivOuter = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_outer'),cgmMeta.cgmObject)      
                mi_pivBallJoint = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_ballJoint'),cgmMeta.cgmObject)      
                mi_pivBallWiggle = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_ballWiggle'),cgmMeta.cgmObject)      

                aimVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[0])
                upVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[1])
                outVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[2])

                mi_controlIK = mi_go._i_rigNull.controlIK
                "mi_controlIK"
                mi_controlMidIK = mi_go._i_rigNull.midIK
                mPlug_lockMid = cgmMeta.cgmAttr(mi_controlMidIK,'lockMid',attrType='float',defaultValue = 0,keyable = True,minValue=0,maxValue=1.0)

                ml_toParentChains.extend([ml_ikJoints,ml_blendJoints,ml_ikNoFlipJoints,ml_ikPVJoints])
                for chain in ml_toParentChains:
                    chain[0].parent = mi_go._i_constrainNull.mNode

                #for more stable ik, we're gonna lock off the lower channels degrees of freedom
                for chain in [ml_ikNoFlipJoints,ml_ikPVJoints]:
                    for axis in mi_go._jointOrientation[:2]:
                        log.info(axis)
                        for i_j in chain[1:]:
                            attributes.doSetAttr(i_j.mNode,"jointType%s"%axis.upper(),0)

            except Exception,error:raise Exception,"Gather data fail! | error: {0}".format(error)

            #=============================================================    
            try:#>>>FK Length connector
                for i,i_jnt in enumerate(ml_fkJoints[:-2]):
                    rUtils.addJointLengthAttr(i_jnt,orientation=mi_go._jointOrientation)

            except Exception,error:raise Exception,"Length connection fail! | error: {0}".format(error)


            #=============================================================    
            try:#>>>IK No Flip Chain
                mPlug_globalScale = cgmMeta.cgmAttr(mi_go._i_masterControl.mNode,'scaleY')    
                i_tmpLoc = ml_ikNoFlipJoints[-1].doLoc()
                if mi_go._direction == 'left':#if right, rotate the pivots
                    mc.move(outVector[0]*100,outVector[1]*100,outVector[2]*100,i_tmpLoc.mNode,r=True, rpr = True, os = True, wd = True)	
                else:
                    mc.move(-outVector[0]*100,outVector[1]*100,outVector[2]*100,i_tmpLoc.mNode,r=True, rpr = True, os = True, wd = True)	

                #Create no flip leg IK
                d_ankleNoFlipReturn = rUtils.IKHandle_create(ml_ikNoFlipJoints[0].mNode,ml_ikNoFlipJoints[-1].mNode, nameSuffix = 'noFlip',
                                                             rpHandle=True,controlObject=mi_controlIK,addLengthMulti=True,
                                                             globalScaleAttr=mPlug_globalScale.p_combinedName, stretch='translate',moduleInstance=mi_go._mi_module)

                mi_ankleIKHandleNF = d_ankleNoFlipReturn['mi_handle']
                ml_distHandlesNF = d_ankleNoFlipReturn['ml_distHandles']
                mi_rpHandleNF = d_ankleNoFlipReturn['mi_rpHandle']
                mPlug_lockMid = d_ankleNoFlipReturn.get('mPlug_lockMid')
                log.info("IK No Flip lockMid: %s"%mPlug_lockMid)

                #No Flip RP handle
                Snap.go(mi_rpHandleNF,i_tmpLoc.mNode,True)#Snape to foot control, then move it out...
                i_tmpLoc.delete()

                mi_rpHandleNF.doCopyNameTagsFromObject(mi_go._mi_module.mNode, ignore = ['cgmName','cgmType'])
                mi_rpHandleNF.addAttr('cgmName','kneePoleVector',attrType = 'string')
                mi_rpHandleNF.addAttr('cgmTypeModifier','noFlip')
                mi_rpHandleNF.doName()

                #Knee spin
                #=========================================================================================
                #Make a spin group
                i_spinGroup = mi_controlIK.doDuplicateTransform()
                i_spinGroup.doCopyNameTagsFromObject(mi_go._mi_module.mNode, ignore = ['cgmName','cgmType'])	
                i_spinGroup.addAttr('cgmName','noFlipKneeSpin')
                i_spinGroup.doName()

                i_spinGroup.parent = mi_pivBall.mNode
                i_spinGroup.doZeroGroup()
                mi_rpHandleNF.parent = i_spinGroup.mNode

                #Setup arg
                mPlug_kneeSpin = cgmMeta.cgmAttr(mi_controlIK,'kneeSpin')

                #Pull out the bank for a more stable setup
                NodeF.argsToNodes("%s.rz = -%s.rz"%(i_spinGroup.p_nameShort,
                                                    mi_controlIK.p_nameShort)).doBuild()		
                #Spin groups rotate
                if mi_go._mi_module.getAttr('cgmDirection') and mi_go._mi_module.cgmDirection.lower() in ['right']:
                    str_spinDriver = "%s.ry = -%s"%(i_spinGroup.mNode,
                                                    mPlug_kneeSpin.p_combinedShortName)
                    NodeF.argsToNodes(str_spinDriver).doBuild()
                else:
                    mPlug_kneeSpin.doConnectOut("%s.rotateY"%i_spinGroup.mNode)

                #>>>Parent IK handles
                mi_ankleIKHandleNF.parent = mi_pivBallJoint.mNode#ankleIK to ball		
                ml_distHandlesNF[-1].parent = mi_pivBallJoint.mNode#ankle distance handle to ball	
                ml_distHandlesNF[0].parent = mi_go._i_constrainNull.mNode#hip distance handle to deform group
                ml_distHandlesNF[1].parent = mi_controlMidIK.mNode#knee distance handle to midIK

                #>>> Fix our ik_handle twist at the end of all of the parenting
                rUtils.IKHandle_fixTwist(mi_ankleIKHandleNF)#Fix the twist

            except Exception,error:raise Exception,"IK - No flip fail! | error: {0}".format(error)


            #=============================================================    
            try:#>>>IK PV Chain
                #Create no flip leg IK
                #We're gonna use the no flip stuff for the most part
                d_anklePVReturn = rUtils.IKHandle_create(ml_ikPVJoints[0].mNode,ml_ikPVJoints[-1].mNode,nameSuffix = 'PV',
                                                         rpHandle=ml_distHandlesNF[1],controlObject=mi_controlIK,
                                                         moduleInstance=mi_go._mi_module)

                mi_ankleIKHandlePV = d_anklePVReturn['mi_handle']
                mi_rpHandlePV = d_anklePVReturn['mi_rpHandle']

                #Stretch -- grab our translate aims from
                for i,i_j in enumerate(ml_ikPVJoints[1:]):
                    driverAttr = attributes.returnDriverAttribute("%s.t%s"%(ml_ikNoFlipJoints[i+1].mNode,mi_go._jointOrientation[0].lower()))
                    d_driverPlug = cgmMeta.validateAttrArg(driverAttr,noneValid=False)#Validdate
                    d_driverPlug['mi_plug'].doConnectOut("%s.t%s"%(i_j.mNode,mi_go._jointOrientation[0].lower()))#Connect the plug to our joint

                #RP handle	
                mi_rpHandlePV.doCopyNameTagsFromObject(mi_go._mi_module.mNode, ignore = ['cgmName','cgmType'])
                mi_rpHandlePV.addAttr('cgmName','kneePoleVector',attrType = 'string')
                mi_rpHandlePV.doName()

                #>>>Parent IK handles
                mi_ankleIKHandlePV.parent = mi_pivBallJoint.mNode#ankleIK to ball	

                #Mid fix
                #=========================================================================================			
                mc.move(0,0,25,mi_controlMidIK.mNode,r=True, rpr = True, ws = True, wd = True)#move out the midControl to fix the twist from

                #>>> Fix our ik_handle twist at the end of all of the parenting
                rUtils.IKHandle_fixTwist(mi_ankleIKHandlePV)#Fix the twist

                #Register our snap to point before we move it back
                i_ikMidMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlMidIK,
                                                          dynPrefix = "FKtoIK",
                                                          dynMatchTargets=ml_blendJoints[1]) 	
                #>>> Reset the translations
                mi_controlMidIK.tx = 0
                mi_controlMidIK.ty = 0
                mi_controlMidIK.tz = 0

                #Move the lock mid and add the toggle so it only works with show knee on
                #=========================================================================================				
                mPlug_lockMidResult = cgmMeta.cgmAttr(mi_controlMidIK,'result_lockMidInfluence',attrType='float',keyable = False,hidden=True)
                mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee')
                drivenPlugs = mPlug_lockMid.getDriven()
                arg = "%s = %s * %s"%(mPlug_lockMidResult.p_combinedShortName,
                                      mPlug_showKnee.p_combinedShortName,
                                      mPlug_lockMid.p_combinedShortName)
                NodeF.argsToNodes(arg).doBuild()
                for plug in drivenPlugs:#Connect them back
                    mPlug_lockMidResult.doConnectOut(plug)

                mPlug_lockMid.doTransferTo(mi_controlMidIK.mNode)#move the lock mid	

            except Exception,error:raise Exception,"IK PV Setup fail! | error: {0}".format(error)


            #=============================================================    
            try:#>>>Foot chains and connection
                #Create foot IK
                d_ballReturn = rUtils.IKHandle_create(ml_ikJoints[2].mNode,ml_ikJoints[3].mNode,solverType='ikSCsolver',
                                                      baseName=ml_ikJoints[3].cgmName,moduleInstance=mi_go._mi_module)
                mi_ballIKHandle = d_ballReturn['mi_handle']

                #Create toe IK
                d_toeReturn = rUtils.IKHandle_create(ml_ikJoints[3].mNode,ml_ikJoints[4].mNode,solverType='ikSCsolver',
                                                     baseName=ml_ikJoints[4].cgmName,moduleInstance=mi_go._mi_module)
                mi_toeIKHandle = d_toeReturn['mi_handle']

                #return {'mi_handle':i_ik_handle,'mi_effector':i_ik_effector,'mi_solver':i_ikSolver}

                mi_ballIKHandle.parent = mi_pivInner.mNode#ballIK to toe
                mi_toeIKHandle.parent = mi_pivBallWiggle.mNode#toeIK to wiggle

            except Exception,error:raise Exception,"Foot chains fail! | error: {0}".format(error)


            #=============================================================    
            try:#>>>Connect Blend Chains and connections
                #Connect Vis of knee
                #=========================================================================================
                mPlug_showKnee = cgmMeta.cgmAttr(mi_controlIK,'showKnee')	
                mPlug_showKnee.doConnectOut("%s.visibility"%mi_controlMidIK.mNode)	

                #>>> Main blend
                mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',lock=False,keyable=True)
                """
		rUtils.connectBlendJointChain(ml_fkJoints,ml_ikJoints,ml_blendJoints,
					      driver = mPlug_FKIK.p_combinedName,channels=['translate','rotate'])"""
                if ml_fkAttachJoints:
                    ml_fkUse = ml_fkAttachJoints
                    for i,mJoint in enumerate(ml_fkAttachJoints):
                        mc.pointConstraint(ml_fkJoints[i].mNode,mJoint.mNode,maintainOffset = False)
                        #Connect inversed aim and up
                        NodeF.connectNegativeAttrs(ml_fkJoints[i].mNode, mJoint.mNode,
                                                   ["r%s"%mi_go._jointOrientation[0],"r%s"%mi_go._jointOrientation[1]]).go()
                        cgmMeta.cgmAttr(ml_fkJoints[i].mNode,"r%s"%mi_go._jointOrientation[2]).doConnectOut("%s.r%s"%(mJoint.mNode,mi_go._jointOrientation[2]))
                else:
                    ml_fkUse = ml_fkJoints
                rUtils.connectBlendChainByConstraint(ml_fkUse,ml_ikJoints,ml_blendJoints,
                                                     driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])

                rUtils.connectBlendJointChain(ml_ikNoFlipJoints,ml_ikPVJoints,ml_ikJoints[:3],
                                              driver = mPlug_showKnee.p_combinedName,channels=['translate','rotate'])	

                #>>> Settings - constrain
                mc.parentConstraint(ml_blendJoints[2].mNode, mi_settings.masterGroup.mNode, maintainOffset = True)

                #>>> Setup a vis blend result
                mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
                mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	

                NodeF.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,mPlug_IKon.p_combinedName,mPlug_FKon.p_combinedName)

                mPlug_FKon.doConnectOut("%s.visibility"%mi_go._i_constrainNull.controlsFK.mNode)
                mPlug_IKon.doConnectOut("%s.visibility"%mi_go._i_constrainNull.controlsIK.mNode)

            except Exception,error:raise Exception,"Connect blend chains fail! | error: {0}".format(error)

            return True	  

    return fncWrap(*args, **kws).go()

def build_controls(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_controls(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Process','call':self._fncStep_process}]
            #=================================================================

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            if not mi_go.isShaped():
                raise Exception,"%s.build_controls>>> needs shapes to build controls"%mi_go._strShortName
            if not mi_go.isRigSkeletonized():
                raise Exception,"%s.build_controls>>> needs shapes to build controls"%mi_go._strShortName
            """
	    __d_controlShapes__ = {'shape':['controlsFK','midIK','settings','foot'],
			     'pivot':['toe','heel','ball','inner','outer
	    for shape in __d_controlShapes__['shape']:
		mi_go.__dict__['mi_%s'%shape] = cgmMeta.validateObjArg(mi_go._i_rigNull.msgList_getMessage('shape_%s'%shape),noneValid=False)
		log.info(mi_go.__dict__['mi_%s'%shape] )"""

            try:#Data gather
                ml_controlsFK = mi_go._i_rigNull.msgList_get('shape_controlsFK')
                ml_segmentIK = mi_go._i_rigNull.msgList_get('shape_segmentIK')
                #mi_go._i_rigNull.msgList_connect(mi_go._md_controlShapes['segmentIK'],'shape_segmentIK_%s'%i,"rigNull")		
                l_segmentIKChains = []
                ml_segmentIKChains = []
                for i in range(50):
                    buffer = mi_go._i_rigNull.msgList_getMessage('shape_segmentIK_%s'%i)
                    if buffer:
                        l_segmentIKChains.append(buffer)
                        ml_segmentIKChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
                    else:
                        break  

                mi_midIK = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_midIK'),cgmMeta.cgmObject)
                mi_settings= cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_settings'),cgmMeta.cgmObject)
                mi_foot= cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('shape_foot'),cgmMeta.cgmObject)
                mi_pivToe = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_toe'),cgmMeta.cgmObject)
                mi_pivHeel = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_heel'),cgmMeta.cgmObject)
                mi_pivBall = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_ball'),cgmMeta.cgmObject)
                mi_pivInner = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_inner'),cgmMeta.cgmObject)
                mi_pivOuter = cgmMeta.validateObjArg(mi_go._i_rigNull.getMessage('pivot_outer'),cgmMeta.cgmObject)
                ml_fkJoints = cgmMeta.validateObjListArg(mi_go._i_rigNull.msgList_get('fkJoints'),cgmMeta.cgmObject)

                #>>>Make a few extra groups for storing controls and what not to in the deform group
                for grp in ['controlsFK','controlsIK']:
                    i_dup = mi_go._i_constrainNull.doDuplicateTransform(True)
                    i_dup.parent = mi_go._i_constrainNull.mNode
                    i_dup.addAttr('cgmTypeModifier',grp,lock=True)
                    i_dup.doName()

                    mi_go._i_constrainNull.connectChildNode(i_dup,grp,'owner')

            except Exception,error:raise Exception,"Data gather fail! | error: {0}".format(error)


            ml_controlsAll = []
            #==================================================================
            try:#>>>> FK Segments
                if len( ml_controlsFK )<3:
                    raise Exception,"%s.build_controls>>> Must have at least three fk controls"%mi_go._strShortName	    

                #for i,i_obj in enumerate(ml_controlsFK[1:]):#parent
                    #i_obj.parent = ml_controlsFK[i].mNode
                ml_fkJoints[0].parent = mi_go._i_constrainNull.controlsFK.mNode

                for i,i_obj in enumerate(ml_controlsFK):
                    d_buffer = mControlFactory.registerControl(i_obj,shapeParentTo = ml_fkJoints[i],
                                                               mirrorSide=mi_go._str_mirrorDirection, mirrorAxis="translateX",
                                                               makeAimable=True,typeModifier='fk',) 	    
                    i_obj = d_buffer['instance']
                    i_obj.axisAim = "%s+"%mi_go._jointOrientation[0]
                    i_obj.axisUp= "%s+"%mi_go._jointOrientation[1]	
                    i_obj.axisOut= "%s+"%mi_go._jointOrientation[2]
                    try:i_obj.drawStyle = 2#Stick joint draw style	    
                    except:self.log_error("{0} Failed to set drawStyle".format(i_obj.p_nameShort))
                    cgmMeta.cgmAttr(i_obj,'radius',hidden=True)

                for i_obj in ml_controlsFK:
                    i_obj.delete()

                #ml_controlsFK[0].masterGroup.parent = mi_go._i_constrainNull.mNode
                mi_go._i_rigNull.msgList_connect(ml_fkJoints,'controlsFK',"rigNull")
                ml_controlsAll.extend(ml_fkJoints)	

            except Exception,error:raise Exception,"fk segment fail! | error: {0}".format(error)


            #==================================================================    
            try:#>>>> IK Handle
                i_IKEnd = mi_foot
                i_IKEnd.parent = False
                d_buffer = mControlFactory.registerControl(i_IKEnd,
                                                           mirrorSide=mi_go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",
                                                           typeModifier='ik',addSpacePivots = 1, addDynParentGroup = True, addConstraintGroup=True,
                                                           makeAimable = True,setRotateOrder=3)
                i_IKEnd = d_buffer['instance']	
                i_IKEnd.masterGroup.parent = mi_go._i_constrainNull.controlsIK.mNode

                #i_loc.delete()#delete
                mi_go._i_rigNull.connectChildNode(i_IKEnd,'controlIK',"rigNull")#connect
                ml_controlsAll.append(i_IKEnd)	

                #Set aims
                i_IKEnd.axisAim = 'z+'
                i_IKEnd.axisUp= 'y+'

            except Exception,error:raise Exception,"IK Handle fail! | error: {0}".format(error)


            #==================================================================    
            try:#>>>> midIK Handle
                i_IKmid = mi_midIK
                i_IKmid.parent = False
                d_buffer = mControlFactory.registerControl(i_IKmid,addSpacePivots = 1,
                                                           mirrorSide=mi_go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",
                                                           typeModifier='ik',addDynParentGroup = True, addConstraintGroup=True,
                                                           makeAimable = False,setRotateOrder=4)
                i_IKmid = d_buffer['instance']	
                i_IKmid.masterGroup.parent = mi_go._i_constrainNull.controlsIK.mNode
                i_IKmid.addAttr('scale',lock=True,hidden=True)
                #i_loc.delete()#delete
                mi_go._i_rigNull.connectChildNode(i_IKmid,'midIK',"rigNull")#connect
                ml_controlsAll.append(i_IKmid)	

            except Exception,error:raise Exception,"midIK fail! | error: {0}".format(error)


            #==================================================================
            try:#>>>> Settings
                d_buffer = mControlFactory.registerControl(mi_settings,addExtraGroups=0,mirrorSide=mi_go._str_mirrorDirection,
                                                           typeModifier='settings',autoLockNHide=True,
                                                           setRotateOrder=2)       
                i_obj = d_buffer['instance']
                i_obj.masterGroup.parent = mi_go._i_constrainNull.mNode
                mi_go._i_rigNull.connectChildNode(mi_settings,'settings',"rigNull")
                ml_controlsAll.append(mi_settings)

                mi_settings.addAttr('blend_FKIK', defaultValue = 0, attrType = 'float', minValue = 0, maxValue = 1, keyable = False,hidden = False,lock=True)

            except Exception,error:raise Exception,"Settings fail! | error: {0}".format(error)


            try:#visSub ================================================================================================
                mPlug_result_moduleSubDriver = mi_go.build_visSub()	

            except Exception,error:raise Exception,"visSub fail! | error: {0}".format(error)


            #==================================================================    
            try:#>>>> IK Segments
                for i,chain in enumerate(ml_segmentIKChains):
                    ml_controlChain =[]
                    for i_obj in chain:
                        d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='segIK',
                                                                    mirrorSide=self._go._str_mirrorDirection,mirrorAxis="translateX, rotateY, rotateZ",
                                                                   setRotateOrder=2)       
                        i_obj = d_buffer['instance']
                        i_obj.masterGroup.parent = mi_go._i_constrainNull.mNode
                        ml_controlChain.append(i_obj)

                        mPlug_result_moduleSubDriver.doConnectOut("%s.visibility"%i_obj.mNode)
                    mi_go._i_rigNull.msgList_connect(ml_controlChain,'segmentHandles_%s'%i,"rigNull")
                    ml_controlsAll.extend(ml_controlChain)	
                    if i == 1:
                        #Need to do a few special things for our main segment handle
                        i_mainHandle = chain[0]
                        mi_go._i_rigNull.connectChildNode(i_mainHandle,'mainSegmentHandle',"rigNull")
                        curves.setCurveColorByName(i_mainHandle.mNode,mi_go._mi_module.getModuleColors()[0])    
                        attributes.doBreakConnection(i_mainHandle.mNode,'visibility')

            except Exception,error:raise Exception,"SegIK fail! | error: {0}".format(error)


            #==================================================================    
            try:#>>>> Add all of our Attrs
                #Add driving attrs
                mPlug_roll = cgmMeta.cgmAttr(i_IKEnd,'roll',attrType='float',defaultValue = 0,keyable = True)
                mPlug_toeLift = cgmMeta.cgmAttr(i_IKEnd,'toeLift',attrType='float',initialValue = 35, defaultValue = 35,keyable = True)
                mPlug_toeStaighten = cgmMeta.cgmAttr(i_IKEnd,'toeStaighten',attrType='float',initialValue = 65,defaultValue = 70,keyable = True)
                mPlug_toeWiggle= cgmMeta.cgmAttr(i_IKEnd,'toeWiggle',attrType='float',defaultValue = 0,keyable = True)
                mPlug_toeSpin = cgmMeta.cgmAttr(i_IKEnd,'toeSpin',attrType='float',defaultValue = 0,keyable = True)
                mPlug_lean = cgmMeta.cgmAttr(i_IKEnd,'lean',attrType='float',defaultValue = 0,keyable = True)
                mPlug_side = cgmMeta.cgmAttr(i_IKEnd,'bank',attrType='float',defaultValue = 0,keyable = True)
                mPlug_kneeSpin = cgmMeta.cgmAttr(i_IKEnd,'kneeSpin',attrType='float',defaultValue = 0,keyable = True)
                mPlug_stretch = cgmMeta.cgmAttr(i_IKEnd,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
                mPlug_showKnee = cgmMeta.cgmAttr(i_IKEnd,'showKnee')
                mPlug_lengthUpr= cgmMeta.cgmAttr(i_IKEnd,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
                mPlug_lengthLwr = cgmMeta.cgmAttr(i_IKEnd,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)	

                mPlug_lockMid = cgmMeta.cgmAttr(i_IKmid,'lockMid',attrType='float',defaultValue = 0,keyable = True,minValue=0,maxValue=1.0)

            except Exception,error:raise Exception,"Attributes creation fail! | error: {0}".format(error)


            try:#Connect all controls
                try:#>> Extra controls gather...
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
                except Exception,error:raise Exception,"Extra control gather fail! | error: {0}".format(error)

                for i,mCtrl in enumerate(ml_controlsAll):
                    mCtrl.mirrorIndex = i

                mi_go._i_rigNull.msgList_connect(ml_controlsAll,'controlsAll')
                mi_go._i_rigNull.moduleSet.extend(ml_controlsAll)#Connect to quick select set	

            except Exception,error:raise Exception,"Connect/mirror index fail! | error: {0}".format(error)
            return True	

    return fncWrap(*args, **kws).go()




def build_deformation(*args, **kws):
    class fncWrap(modUtils.rigStep):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'build_deformation(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__(*args,**kws)
            self._b_reportTimes = True
            self.l_funcSteps = [{'step':'Process','call':self._fncStep_process}]
            #=================================================================


        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            #==========================================================================
            try:#Info gathering
                #segmentHandles_%s
                #Get our segment controls
                ml_segmentHandleChains = mi_go._get_segmentHandleChains()

                #Get our segment joints
                ml_segmentChains = mi_go._get_segmentChains()
                if len(ml_segmentChains)>2:
                    raise Exception, "%s.build_deformation>>> Too many segment chains, not a regular leg."%(mi_go._strShortName)

                #>>>Influence Joints
                ml_influenceChains = mi_go._get_influenceChains()
                if len(ml_influenceChains)!=len(ml_segmentChains):
                    raise Exception, "%s.build_deformation>>> Segment chains don't equal segment influence chains"%(mi_go._strShortName)

                #>>>Get data
                ml_controlsFK =  mi_go._i_rigNull.msgList_get('controlsFK')    
                ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')
                ml_blendJoints = mi_go._i_rigNull.msgList_get('blendJoints')
                mi_settings = mi_go._i_rigNull.settings

                mi_controlIK = mi_go._i_rigNull.controlIK
                mi_controlMidIK = mi_go._i_rigNull.midIK

                aimVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[0])
                upVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[1])

                ml_driversFK = ml_controlsFK
                if mi_go._str_mirrorDirection == 'Right':
                    ml_driversFK = mi_go._i_rigNull.msgList_get('fkAttachJoints')

            except Exception,error:raise Exception,"Gather data fail! | error: {0}".format(error)


            try:#Main Attributes
                #==================================================================================== 
                #This is a bit of a complicated setup, pretty much we're gathering and splitting out potential drivers of the twist per segment
                str_twistOrientation = "r%s"%mi_go._jointOrientation[0]   

                mPlug_Blend0 = cgmMeta.cgmAttr(ml_blendJoints[0],str_twistOrientation)
                mPlug_constraintNullRotate = cgmMeta.cgmAttr(mi_go._i_constrainNull,str_twistOrientation)    
                mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
                mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)
                mPlug_worldIKEndOut = cgmMeta.cgmAttr(mi_settings,"out_worldIKEnd" , attrType='float' , lock = True) 

                mPlug_worldIKEndIn.doConnectOut(mPlug_worldIKEndOut.p_combinedShortName)

            except Exception,error:raise Exception,"Attributes fail! | error: {0}".format(error)


            #Control Segment
            #====================================================================================
            ml_segmentCurves = []
            ml_segmentReturns = []
            ml_segmentJointChainsReset = []
            try:#Control Segment		
                capAim = mi_go._jointOrientation[0].capitalize()
                log.debug("capAim: %s"%capAim)
                for i,ml_segmentHandles in enumerate(ml_segmentHandleChains):
                    i_startControl = ml_segmentHandles[0]
                    i_midControl = ml_segmentHandles[1]
                    i_endControl = ml_segmentHandles[-1]
                    l_jointChain = [i_jnt.mNode for i_jnt in ml_segmentChains[i]]
                    l_infuenceJoints = [ml_influenceChains[i][0].getShortName(),ml_influenceChains[i][-1].getShortName()]
                    log.info("startControl: %s"%i_startControl.getShortName())
                    log.info("endControl: %s"%i_endControl.getShortName())
                    log.info("jointChain: %s"%l_jointChain)
                    log.info("influenceJoints: %s"%l_infuenceJoints)
                    str_baseName = mi_go._partName+"_seg%s"%i
                    str_segCount = "seg%s"%i
                    #Create segment
                    curveSegmentReturn = rUtils.createCGMSegment(l_jointChain,
                                                                 addSquashStretch=True,
                                                                 addTwist=True,
                                                                 influenceJoints=[l_infuenceJoints[0],l_infuenceJoints[-1]],
                                                                 startControl= i_startControl,
                                                                 endControl= i_endControl,
                                                                 orientation=mi_go._jointOrientation,
                                                                 additiveScaleSetup=True,
                                                                 connectAdditiveScale=True,                                                 
                                                                 baseName = str_baseName,
                                                                 moduleInstance=mi_go._mi_module)

                    ml_segmentReturns.append(curveSegmentReturn)

                    i_curve = curveSegmentReturn['mi_segmentCurve']
                    i_curve.parent = mi_go._i_rigNull.mNode
                    i_curve.segmentGroup.parent = mi_go._i_rigNull.mNode
                    ml_segmentCurves.append(i_curve)

                    midReturn = rUtils.addCGMSegmentSubControl(ml_influenceChains[i][1],
                                                               segmentCurve = i_curve,
                                                               baseParent = l_infuenceJoints[0],
                                                               endParent = l_infuenceJoints[-1],
                                                               midControls = ml_segmentHandles[1].mNode,
                                                               baseName = str_baseName,
                                                               orientation = mi_go._jointOrientation,
                                                               controlTwistAxis =  'r'+mi_go._jointOrientation[0],	                                               
                                                               moduleInstance=mi_go._mi_module)

                    for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
                        i_grp.parent = ml_blendJoints[i].mNode

                    #Parent our joint chains
                    i_curve.msgList_get('driverJoints',asMeta = True)[0].parent = ml_blendJoints[i].mNode
                    ml_segmentChains[i][0].parent = ml_blendJoints[i].mNode    

                    #>>> Attach stuff
                    #==============================================================================================
                    try:#We're gonna attach to the blend chain
                        mi_segmentAnchorStart = cgmMeta.validateObjArg(i_curve.anchorStart,'cgmObject')
                        mi_segmentAnchorEnd = cgmMeta.validateObjArg(i_curve.anchorEnd,'cgmObject')
                        mi_segmentAttachStart = cgmMeta.validateObjArg(i_curve.attachStart,'cgmObject')
                        mi_segmentAttachEnd = cgmMeta.validateObjArg(i_curve.attachEnd,'cgmObject') 
                        mi_distanceBuffer = cgmMeta.validateObjArg(i_curve.scaleBuffer)

                        log.debug("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
                        log.debug("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
                        log.debug("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
                        log.debug("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
                        log.debug("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)

                        #>>> parent the anchors to the deform null
                        mi_segmentAnchorStart.parent =  mi_go._i_constrainNull.mNode
                        mi_segmentAnchorEnd.parent =  mi_go._i_constrainNull.mNode	

                        #>>> parent handle anchors
                        mi_segmentAnchorStart.parent = ml_blendJoints[i].mNode
                        if i == 0:
                            #mi_segmentAnchorEnd.parent = mi_go._i_rigNull.mainSegmentHandle.mNode
                            mi_segmentAnchorEnd.parent = ml_blendJoints[i].mNode
                            mc.parentConstraint(mi_go._i_rigNull.mainSegmentHandle.mNode,mi_segmentAnchorEnd.mNode)
                            #...was point before beta
                        else:
                            mi_segmentAnchorEnd.parent = ml_blendJoints[i+1].mNode	

                        #segment handles to influence parents
                        i_startControl.masterGroup.parent = ml_influenceChains[i][0].parent
                        i_endControl.masterGroup.parent = ml_influenceChains[i][-1].parent

                    except Exception,error:
                        raise Exception,"Failed to connect anchor: %s | %s"%(mi_segmentAnchorStart.p_nameShort,error)


                    #Influence joint to segment handles		
                    ml_influenceChains[i][0].parent = i_startControl.mNode
                    ml_influenceChains[i][-1].parent = i_endControl.mNode


                    #>>> Build fk and ik drivers
                    """
		    fk result = fk1 + fk2 + fk3 + -fk4
		    ik result = ik.y + knee twist?
		    Need sums, multiply by the fk/ikon
		    """
                    #>>> Setup a vis blend result
                    mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon')	
                    mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon')	

                    #>>>Attrs
                    mPlug_TwistStartResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStart'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistEndResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEnd'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)

                    mPlug_TwistStartFKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStartFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistEndFKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEndFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistStartFKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistStartFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistEndFKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistEndFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)

                    mPlug_TwistStartIKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStartIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistEndIKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEndIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistStartIKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistStartIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistEndIKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistEndIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)

                    #start twist driver
                    l_startDrivers = ["%s.%s"%(i_startControl.getShortName(),str_twistOrientation)]
                    l_startDrivers.append("%s"%mPlug_TwistStartFKResult.p_combinedShortName )
                    l_startDrivers.append("%s"%mPlug_TwistStartIKResult.p_combinedShortName )	    
                    l_fkStartDrivers = []
                    l_ikStartDrivers = []
                    """
		    for ii in range(i+1):
			if ii !=  0:
			    l_fkStartDrivers.append("%s.%s"%(ml_controlsFK[ii].getShortName(),str_twistOrientation))"""

                    #end twist driver
                    l_endDrivers = ["%s.%s"%(i_endControl.getShortName(),str_twistOrientation)]	    
                    l_endDrivers.append("%s"%mPlug_TwistEndFKResult.p_combinedShortName )
                    l_endDrivers.append("%s"%mPlug_TwistEndIKResult.p_combinedShortName )		    
                    l_fkEndDrivers = []
                    l_ikEndDrivers = []


                    l_fkEndDrivers.append("%s.%s"%(ml_driversFK[i+1].getShortName(),str_twistOrientation))   

                    """
		    for ii in range(i+2):
			if ii !=  0:	
			    l_fkEndDrivers.append("%s.%s"%(ml_controlsFK[ii].getShortName(),str_twistOrientation))"""

                    if i == 0:#if seg 0
                        l_ikStartDrivers.append(mPlug_worldIKStartIn.p_combinedShortName)
                        l_fkStartDrivers.append(mPlug_worldIKStartIn.p_combinedShortName)		
                        l_endDrivers.append("%s.%s"%(mi_go._i_rigNull.mainSegmentHandle.getShortName(),str_twistOrientation))

                        #If it's our first one we wann


                        #We need to make our world driver start twist
                        #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<;laksdjf;alskjdf;lasjkdflaj

                    if i == 1:#if seg 1	
                        #l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
                        l_ikEndDrivers.append(mPlug_worldIKEndOut.p_combinedShortName)

                    log.info("#>>> %s "%str_segCount+"="*70)
                    log.info("startDrivers %s: %s"%(i,l_startDrivers))
                    str_ArgStartDrivers_Result = "%s = %s"%(mPlug_TwistStartResult.p_combinedShortName," + ".join(l_startDrivers))
                    log.info("start sum arg: '%s'"%(str_ArgStartDrivers_Result))
                    NodeF.argsToNodes(str_ArgStartDrivers_Result).doBuild()		

                    log.info("ikStart Drivers %s: %s"%(i,l_ikStartDrivers))
                    if l_ikStartDrivers:
                        str_ArgIKStart_Sum = "%s = %s"%(mPlug_TwistStartIKSum.p_combinedShortName," + ".join(l_ikStartDrivers))
                        log.info("start IK sum arg: '%s'"%(str_ArgIKStart_Sum))
                        NodeF.argsToNodes(str_ArgIKStart_Sum).doBuild()		
                        str_ArgIKStart_Result = "%s = %s * %s"%(mPlug_TwistStartIKResult.p_combinedShortName,mPlug_TwistStartIKSum.p_combinedShortName,mPlug_IKon.p_combinedShortName)
                        log.info("start IK result arg: '%s'"%(str_ArgIKStart_Result))
                        NodeF.argsToNodes(str_ArgIKStart_Result).doBuild()		

                    log.info("fkStart Drivers %s: %s"%(i,l_fkStartDrivers))
                    if l_fkStartDrivers:
                        str_ArgFKStart_Sum = "%s = %s"%(mPlug_TwistStartFKSum.p_combinedShortName," + ".join(l_fkStartDrivers))
                        log.info("start FK sum arg: '%s'"%(str_ArgFKStart_Sum))
                        NodeF.argsToNodes(str_ArgFKStart_Sum).doBuild()				

                        str_ArgFKStart_Result = "%s = %s * %s"%(mPlug_TwistStartFKResult.p_combinedShortName,mPlug_TwistStartFKSum.p_combinedShortName,mPlug_FKon.p_combinedShortName)
                        log.info("start FK result arg: '%s'"%(str_ArgFKStart_Result))
                        NodeF.argsToNodes(str_ArgFKStart_Result).doBuild()		

                    #><
                    log.info("#"+"-"*70)
                    log.info("endDrivers %s: %s"%(i,l_endDrivers))	    
                    str_ArgEndDrivers = "%s = %s"%(mPlug_TwistEndResult.p_combinedShortName," + ".join(l_endDrivers))
                    log.info("end sum arg: '%s'"%(str_ArgEndDrivers))	    
                    log.info("ikEnd Drivers %s: %s"%(i,l_ikEndDrivers))
                    NodeF.argsToNodes(str_ArgEndDrivers).doBuild()		

                    if l_ikEndDrivers:
                        str_ArgIKEnd_Sum = "%s = %s"%(mPlug_TwistEndIKSum.p_combinedShortName," + ".join(l_ikEndDrivers))
                        log.info("end IK sum arg: '%s'"%(str_ArgIKEnd_Sum))
                        NodeF.argsToNodes(str_ArgIKEnd_Sum).doBuild()				
                        str_ArgIKEnd_Result = "%s = %s * %s"%(mPlug_TwistEndIKResult.p_combinedShortName,mPlug_TwistEndIKSum.p_combinedShortName,mPlug_IKon.p_combinedShortName)
                        log.info("end IK result arg: '%s'"%(str_ArgIKEnd_Result))
                        NodeF.argsToNodes(str_ArgIKEnd_Result).doBuild()				

                    log.info("fkEnd Drivers %s: %s"%(i,l_fkEndDrivers))
                    if l_fkEndDrivers:
                        str_ArgFKEnd_Sum = "%s = %s"%(mPlug_TwistEndFKSum.p_combinedShortName," + ".join(l_fkEndDrivers))
                        log.info("end FK sum arg: '%s'"%(str_ArgFKEnd_Sum))
                        NodeF.argsToNodes(str_ArgFKEnd_Sum).doBuild()	

                        str_ArgFKEnd_Result = "%s = %s * %s"%(mPlug_TwistEndFKResult.p_combinedShortName,mPlug_TwistEndFKSum.p_combinedShortName,mPlug_FKon.p_combinedShortName)
                        log.info("end FK result arg: '%s'"%(str_ArgFKEnd_Result))
                        NodeF.argsToNodes(str_ArgFKEnd_Result).doBuild()				

                    log.info("#"+"="*70)
                    mPlug_TwistStartResult.doConnectOut("%s.twistStart"%i_curve.mNode)
                    mPlug_TwistEndResult.doConnectOut("%s.twistEnd"%i_curve.mNode)

                    #Reconnect children nodes
                    mi_go._i_rigNull.msgList_connect(ml_segmentChains[i],'segment%s_Joints'%i,"rigNull")#Reconnect to reset. Duplication from createCGMSegment causes issues	

                    #>>> Attributes 
                    #================================================================================================================
                    #Connect master scale
                    cgmMeta.cgmAttr(i_curve.scaleBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(mi_go._i_masterControl.mNode,'scaleY'))    	    

                    #Push squash and stretch multipliers to head
                    i_buffer = i_curve.scaleBuffer	    
                    for ii,k in enumerate(i_buffer.d_indexToAttr.keys()):
                        attrName = "seg_%s_%s_mult"%(i,ii)
                        cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_settings.mNode,attrName,connectSourceToTarget = True)
                        cgmMeta.cgmAttr(mi_settings.mNode,attrName,defaultValue = 1,keyable=True)

                    #Other attributes transfer
                    cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(i_midControl.mNode,connectSourceToTarget=True)
                    cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(i_midControl.mNode,connectSourceToTarget=True)
                    #Segment scale
                    cgmMeta.cgmAttr(i_buffer,
                                    'segmentScaleMult').doCopyTo(mi_settings.mNode,
                                                                 "segmentScaleMult_%s"%i,
                                                                 connectSourceToTarget=True)	    
                    #cgmMeta.cgmAttr(i_curve,'twistMid').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
                    #cgmMeta.cgmAttr(i_curve,'scaleMidUp').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
                    #cgmMeta.cgmAttr(i_curve,'scaleMidOut').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)	    

            except Exception,error:raise Exception,"Segment fail! | error: {0}".format(error)

            """

	    try:#>>>Connect segment scale
		_str_subFunc = "Segment Scale transfer"
		time_sub = time.clock() 
		log.debug(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50) 	
		mi_distanceBuffer = i_curve.scaleBuffer	
		cgmMeta.cgmAttr(mi_distanceBuffer,'segmentScale').doTransferTo(mi_go._i_rigNull.settings.mNode)    

		log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
	    except Exception,error:
		raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
	    """
            #TODO
            try:#Connection		
                mi_go._i_rigNull.msgList_connect(ml_segmentCurves,'segmentCurves',"rigNull")

            except Exception,error:raise Exception,"Connections fail! | error: {0}".format(error)
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
        log.error("leg.build_deformationRig>>bad self!")
        raise Exception,error

    _str_funcName = "build_deformation(%s)"%self._strShortName
    log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock() 

    #==========================================================================
    try:#Info gathering
        _str_subFunc = "Get Data"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        #segmentHandles_%s
        #Get our segment controls
        ml_segmentHandleChains = self._get_segmentHandleChains()

        #Get our segment joints
        ml_segmentChains = self._get_segmentChains()
        if len(ml_segmentChains)>2:
            raise Exception, "%s.build_deformation>>> Too many segment chains, not a regular leg."%(self._strShortName)

        #>>>Influence Joints
        ml_influenceChains = self._get_influenceChains()
        if len(ml_influenceChains)!=len(ml_segmentChains):
            raise Exception, "%s.build_deformation>>> Segment chains don't equal segment influence chains"%(self._strShortName)

        #>>>Get data
        ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
        ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
        ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
        mi_settings = self._i_rigNull.settings

        mi_controlIK = self._i_rigNull.controlIK
        mi_controlMidIK = self._i_rigNull.midIK

        aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
        upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])

        ml_driversFK = ml_controlsFK
        if self._str_mirrorDirection == 'Right':
            ml_driversFK = self._i_rigNull.msgList_get('fkAttachJoints')

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#Main Attributes
        #==================================================================================== 
        _str_subFunc = "Main Attributes"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        #This is a bit of a complicated setup, pretty much we're gathering and splitting out potential drivers of the twist per segment
        str_twistOrientation = "r%s"%self._jointOrientation[0]   

        mPlug_Blend0 = cgmMeta.cgmAttr(ml_blendJoints[0],str_twistOrientation)
        mPlug_constraintNullRotate = cgmMeta.cgmAttr(self._i_constrainNull,str_twistOrientation)    
        mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
        mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)
        mPlug_worldIKEndOut = cgmMeta.cgmAttr(mi_settings,"out_worldIKEnd" , attrType='float' , lock = True) 

        mPlug_worldIKEndIn.doConnectOut(mPlug_worldIKEndOut.p_combinedShortName)

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)    
    #=========================================================================================

    #Control Segment
    #====================================================================================
    ml_segmentCurves = []
    ml_segmentReturns = []
    ml_segmentJointChainsReset = []
    try:#Control Segment
        _str_subFunc = "Control Segment"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        capAim = self._jointOrientation[0].capitalize()
        log.debug("capAim: %s"%capAim)
        for i,ml_segmentHandles in enumerate(ml_segmentHandleChains):
            i_startControl = ml_segmentHandles[0]
            i_midControl = ml_segmentHandles[1]
            i_endControl = ml_segmentHandles[-1]
            l_jointChain = [i_jnt.mNode for i_jnt in ml_segmentChains[i]]
            l_infuenceJoints = [ml_influenceChains[i][0].getShortName(),ml_influenceChains[i][-1].getShortName()]
            log.info("startControl: %s"%i_startControl.getShortName())
            log.info("endControl: %s"%i_endControl.getShortName())
            log.info("jointChain: %s"%l_jointChain)
            log.info("influenceJoints: %s"%l_infuenceJoints)
            str_baseName = self._partName+"_seg%s"%i
            str_segCount = "seg%s"%i
            #Create segment
            curveSegmentReturn = rUtils.createCGMSegment(l_jointChain,
                                                         addSquashStretch=True,
                                                         addTwist=True,
                                                         influenceJoints=[l_infuenceJoints[0],l_infuenceJoints[-1]],
                                                         startControl= i_startControl,
                                                         endControl= i_endControl,
                                                         orientation=self._jointOrientation,
                                                         additiveScaleSetup=True,
                                                         connectAdditiveScale=True,                                                 
                                                         baseName = str_baseName,
                                                         moduleInstance=self._mi_module)

            ml_segmentReturns.append(curveSegmentReturn)

            i_curve = curveSegmentReturn['mi_segmentCurve']
            i_curve.parent = self._i_rigNull.mNode
            i_curve.segmentGroup.parent = self._i_rigNull.mNode
            ml_segmentCurves.append(i_curve)

            midReturn = rUtils.addCGMSegmentSubControl(ml_influenceChains[i][1],
                                                       segmentCurve = i_curve,
                                                       baseParent = l_infuenceJoints[0],
                                                       endParent = l_infuenceJoints[-1],
                                                       midControls = ml_segmentHandles[1].mNode,
                                                       baseName = str_baseName,
                                                       orientation = self._jointOrientation,
                                                       controlTwistAxis =  'r'+self._jointOrientation[0],	                                               
                                                       moduleInstance=self._mi_module)

            for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
                i_grp.parent = ml_blendJoints[i].mNode

            #Parent our joint chains
            i_curve.msgList_get('driverJoints',asMeta = True)[0].parent = ml_blendJoints[i].mNode
            ml_segmentChains[i][0].parent = ml_blendJoints[i].mNode    

            #>>> Attach stuff
            #==============================================================================================
            try:#We're gonna attach to the blend chain
                mi_segmentAnchorStart = i_curve.anchorStart
                mi_segmentAnchorEnd = i_curve.anchorEnd
                mi_segmentAttachStart = i_curve.attachStart
                mi_segmentAttachEnd = i_curve.attachEnd 
                mi_distanceBuffer = i_curve.scaleBuffer

                log.debug("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
                log.debug("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
                log.debug("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
                log.debug("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
                log.debug("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)

                #>>> parent the anchors to the deform null
                mi_segmentAnchorStart.parent =  self._i_constrainNull.mNode
                mi_segmentAnchorEnd.parent =  self._i_constrainNull.mNode	

                #>>> parent handle anchors
                mi_segmentAnchorStart.parent = ml_blendJoints[i].mNode
                if i == 0:
                    #mi_segmentAnchorEnd.parent = self._i_rigNull.mainSegmentHandle.mNode
                    mi_segmentAnchorEnd.parent = ml_blendJoints[i].mNode
                    mc.pointConstraint(self._i_rigNull.mainSegmentHandle.mNode,mi_segmentAnchorEnd.mNode)
                else:
                    mi_segmentAnchorEnd.parent = ml_blendJoints[i+1].mNode	

                #segment handles to influence parents
                i_startControl.masterGroup.parent = ml_influenceChains[i][0].parent
                i_endControl.masterGroup.parent = ml_influenceChains[i][-1].parent

            except Exception,error:
                raise Exception,"Failed to connect anchor: %s | %s"%(mi_segmentAnchorStart.p_nameShort,error)


            #Influence joint to segment handles		
            ml_influenceChains[i][0].parent = i_startControl.mNode
            ml_influenceChains[i][-1].parent = i_endControl.mNode


            #>>> Build fk and ik drivers
            """
	    fk result = fk1 + fk2 + fk3 + -fk4
	    ik result = ik.y + knee twist?
	    Need sums, multiply by the fk/ikon
	    """
            #>>> Setup a vis blend result
            mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon')	
            mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon')	

            #>>>Attrs
            mPlug_TwistStartResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStart'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
            mPlug_TwistEndResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEnd'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)

            mPlug_TwistStartFKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStartFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
            mPlug_TwistEndFKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEndFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
            mPlug_TwistStartFKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistStartFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
            mPlug_TwistEndFKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistEndFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)

            mPlug_TwistStartIKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStartIK'%str_segCount ,hidden=False, attrType='float' , defaultValue = 1 , lock = True)
            mPlug_TwistEndIKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEndIK'%str_segCount ,hidden=False, attrType='float' , defaultValue = 1 , lock = True)
            mPlug_TwistStartIKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistStartIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
            mPlug_TwistEndIKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistEndIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)

            #start twist driver
            l_startDrivers = ["%s.%s"%(i_startControl.getShortName(),str_twistOrientation)]
            l_startDrivers.append("%s"%mPlug_TwistStartFKResult.p_combinedShortName )
            l_startDrivers.append("%s"%mPlug_TwistStartIKResult.p_combinedShortName )	    
            l_fkStartDrivers = []
            l_ikStartDrivers = []
            """
	    for ii in range(i+1):
		if ii !=  0:
		    l_fkStartDrivers.append("%s.%s"%(ml_controlsFK[ii].getShortName(),str_twistOrientation))"""

            #end twist driver
            l_endDrivers = ["%s.%s"%(i_endControl.getShortName(),str_twistOrientation)]	    
            l_endDrivers.append("%s"%mPlug_TwistEndFKResult.p_combinedShortName )
            l_endDrivers.append("%s"%mPlug_TwistEndIKResult.p_combinedShortName )		    
            l_fkEndDrivers = []
            l_ikEndDrivers = []


            l_fkEndDrivers.append("%s.%s"%(ml_driversFK[i+1].getShortName(),str_twistOrientation))   

            """
	    for ii in range(i+2):
		if ii !=  0:	
		    l_fkEndDrivers.append("%s.%s"%(ml_controlsFK[ii].getShortName(),str_twistOrientation))"""

            if i == 0:#if seg 0
                l_ikStartDrivers.append(mPlug_worldIKStartIn.p_combinedShortName)
                l_fkStartDrivers.append(mPlug_worldIKStartIn.p_combinedShortName)		
                l_endDrivers.append("%s.%s"%(self._i_rigNull.mainSegmentHandle.getShortName(),str_twistOrientation))

                #If it's our first one we wann


                #We need to make our world driver start twist
                #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<;laksdjf;alskjdf;lasjkdflaj

            if i == 1:#if seg 1	
                #l_ikStartDrivers.append("%s.%s"%(ml_blendJoints[0].getShortName(),str_twistOrientation))
                l_ikEndDrivers.append(mPlug_worldIKEndOut.p_combinedShortName)

            log.info("#>>> %s "%str_segCount+"="*70)
            log.info("startDrivers %s: %s"%(i,l_startDrivers))
            str_ArgStartDrivers_Result = "%s = %s"%(mPlug_TwistStartResult.p_combinedShortName," + ".join(l_startDrivers))
            log.info("start sum arg: '%s'"%(str_ArgStartDrivers_Result))
            NodeF.argsToNodes(str_ArgStartDrivers_Result).doBuild()		

            log.info("ikStart Drivers %s: %s"%(i,l_ikStartDrivers))
            if l_ikStartDrivers:
                str_ArgIKStart_Sum = "%s = %s"%(mPlug_TwistStartIKSum.p_combinedShortName," + ".join(l_ikStartDrivers))
                log.info("start IK sum arg: '%s'"%(str_ArgIKStart_Sum))
                NodeF.argsToNodes(str_ArgIKStart_Sum).doBuild()		
                str_ArgIKStart_Result = "%s = %s * %s"%(mPlug_TwistStartIKResult.p_combinedShortName,mPlug_TwistStartIKSum.p_combinedShortName,mPlug_IKon.p_combinedShortName)
                log.info("start IK result arg: '%s'"%(str_ArgIKStart_Result))
                NodeF.argsToNodes(str_ArgIKStart_Result).doBuild()		

            log.info("fkStart Drivers %s: %s"%(i,l_fkStartDrivers))
            if l_fkStartDrivers:
                str_ArgFKStart_Sum = "%s = %s"%(mPlug_TwistStartFKSum.p_combinedShortName," + ".join(l_fkStartDrivers))
                log.info("start FK sum arg: '%s'"%(str_ArgFKStart_Sum))
                NodeF.argsToNodes(str_ArgFKStart_Sum).doBuild()				

                str_ArgFKStart_Result = "%s = %s * %s"%(mPlug_TwistStartFKResult.p_combinedShortName,mPlug_TwistStartFKSum.p_combinedShortName,mPlug_FKon.p_combinedShortName)
                log.info("start FK result arg: '%s'"%(str_ArgFKStart_Result))
                NodeF.argsToNodes(str_ArgFKStart_Result).doBuild()		

            #><
            log.info("#"+"-"*70)
            log.info("endDrivers %s: %s"%(i,l_endDrivers))	    
            str_ArgEndDrivers = "%s = %s"%(mPlug_TwistEndResult.p_combinedShortName," + ".join(l_endDrivers))
            log.info("end sum arg: '%s'"%(str_ArgEndDrivers))	    
            log.info("ikEnd Drivers %s: %s"%(i,l_ikEndDrivers))
            NodeF.argsToNodes(str_ArgEndDrivers).doBuild()		

            if l_ikEndDrivers:
                str_ArgIKEnd_Sum = "%s = %s"%(mPlug_TwistEndIKSum.p_combinedShortName," + ".join(l_ikEndDrivers))
                log.info("end IK sum arg: '%s'"%(str_ArgIKEnd_Sum))
                NodeF.argsToNodes(str_ArgIKEnd_Sum).doBuild()				
                str_ArgIKEnd_Result = "%s = %s * %s"%(mPlug_TwistEndIKResult.p_combinedShortName,mPlug_TwistEndIKSum.p_combinedShortName,mPlug_IKon.p_combinedShortName)
                log.info("end IK result arg: '%s'"%(str_ArgIKEnd_Result))
                NodeF.argsToNodes(str_ArgIKEnd_Result).doBuild()				

            log.info("fkEnd Drivers %s: %s"%(i,l_fkEndDrivers))
            if l_fkEndDrivers:
                str_ArgFKEnd_Sum = "%s = %s"%(mPlug_TwistEndFKSum.p_combinedShortName," + ".join(l_fkEndDrivers))
                log.info("end FK sum arg: '%s'"%(str_ArgFKEnd_Sum))
                NodeF.argsToNodes(str_ArgFKEnd_Sum).doBuild()	

                str_ArgFKEnd_Result = "%s = %s * %s"%(mPlug_TwistEndFKResult.p_combinedShortName,mPlug_TwistEndFKSum.p_combinedShortName,mPlug_FKon.p_combinedShortName)
                log.info("end FK result arg: '%s'"%(str_ArgFKEnd_Result))
                NodeF.argsToNodes(str_ArgFKEnd_Result).doBuild()				

            log.info("#"+"="*70)
            mPlug_TwistStartResult.doConnectOut("%s.twistStart"%i_curve.mNode)
            mPlug_TwistEndResult.doConnectOut("%s.twistEnd"%i_curve.mNode)

            #Reconnect children nodes
            self._i_rigNull.msgList_connect(ml_segmentChains[i],'segment%s_Joints'%i,"rigNull")#Reconnect to reset. Duplication from createCGMSegment causes issues	

            #>>> Attributes 
            #================================================================================================================
            #Connect master scale
            cgmMeta.cgmAttr(i_curve.scaleBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(self._i_masterControl.mNode,'scaleY'))    	    

            #Push squash and stretch multipliers to head
            i_buffer = i_curve.scaleBuffer	    
            for ii,k in enumerate(i_buffer.d_indexToAttr.keys()):
                attrName = "seg_%s_%s_mult"%(i,ii)
                cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_settings.mNode,attrName,connectSourceToTarget = True)
                cgmMeta.cgmAttr(mi_settings.mNode,attrName,defaultValue = 1,keyable=True)

            #Other attributes transfer
            cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(i_midControl.mNode,connectSourceToTarget=True)
            cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(i_midControl.mNode,connectSourceToTarget=True)
            #Segment scale
            cgmMeta.cgmAttr(i_buffer,'segmentScale').doCopyTo(mi_settings.mNode,"segmentScale_%s"%i,connectSourceToTarget=True)	    
            #cgmMeta.cgmAttr(i_curve,'twistMid').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
            #cgmMeta.cgmAttr(i_curve,'scaleMidUp').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)
            #cgmMeta.cgmAttr(i_curve,'scaleMidOut').doCopyTo(mi_handleIK.mNode,connectSourceToTarget=True)	    

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    """

    try:#>>>Connect segment scale
	_str_subFunc = "Segment Scale transfer"
	time_sub = time.clock() 
	log.debug(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50) 	
	mi_distanceBuffer = i_curve.scaleBuffer	
	cgmMeta.cgmAttr(mi_distanceBuffer,'segmentScale').doTransferTo(self._i_rigNull.settings.mNode)    

	log.debug("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
	raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    """
    #TODO
    try:#Connection
        _str_subFunc = "Connection"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        self._i_rigNull.msgList_connect(ml_segmentCurves,'segmentCurves',"rigNull")

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
            self.l_funcSteps = [{'step':'Process','call':self._fncStep_process}]
            #=================================================================

        def _fncStep_process(self):
            mi_go = self.d_kws['goInstance']

            try:#>>>Get data
                orientation = mi_go._jointOrientation or modules.returnSettingsData('jointOrientation')
                mi_moduleParent = False
                if mi_go._mi_module.getMessage('moduleParent'):
                    mi_moduleParent = mi_go._mi_module.moduleParent

                mi_controlIK = mi_go._i_rigNull.controlIK
                mi_controlMidIK = mi_go._i_rigNull.midIK 
                ml_controlsFK =  mi_go._i_rigNull.msgList_get('controlsFK')    
                ml_rigJoints = mi_go._i_rigNull.msgList_get('rigJoints')
                ml_blendJoints = mi_go._i_rigNull.msgList_get('blendJoints')
                mi_settings = mi_go._i_rigNull.settings

                mi_controlIK = mi_go._i_rigNull.controlIK
                mi_controlMidIK = mi_go._i_rigNull.midIK

                log.debug("mi_controlIK: %s"%mi_controlIK.mNode)
                log.debug("mi_controlMidIK: %s"%mi_controlMidIK.mNode)	
                log.debug("ml_controlsFK: %s"%[o.getShortName() for o in ml_controlsFK])
                log.debug("mi_settings: %s"%mi_settings.mNode)

                log.debug("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
                log.debug("ml_blendJoints: %s"%[o.getShortName() for o in ml_blendJoints])

                ml_segmentHandleChains = mi_go._get_segmentHandleChains()
                ml_segmentChains = mi_go._get_segmentChains()
                ml_influenceChains = mi_go._get_influenceChains()	
                ml_rigHandleJoints = mi_go._get_handleJoints()
                aimVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[0])
                upVector = dictionary.stringToVectorDict.get("%s+"%mi_go._jointOrientation[1]) 

                ml_fkJoints = mi_go._i_rigNull.msgList_get('fkJoints')
                ml_ikJoints = mi_go._i_rigNull.msgList_get('ikJoints')
                ml_ikPVJoints = mi_go._i_rigNull.msgList_get('ikPVJoints')
                ml_ikNoFlipJoints = mi_go._i_rigNull.msgList_get('ikNoFlipJoints')		
                #Build our contrain to pool
                d_indexRigJointToDriver = mi_go._get_simpleRigJointDriverDict()

            except Exception,error:raise Exception,"Gather data fail! | error: {0}".format(error)


            try:#Constrain to pelvis
                if mi_moduleParent:
                    mc.parentConstraint(mi_moduleParent.rigNull.msgList_getMessage('moduleJoints')[0],mi_go._i_constrainNull.mNode,maintainOffset = True)
            except Exception,error:raise Exception,"Constrain to pelvis fail! | error: {0}".format(error)


            #Dynamic parent groups
            #====================================================================================
            try:#>>>> Foot
                #Build our dynamic groups
                ml_footDynParents = [mi_go._i_masterControl]
                if mi_moduleParent:
                    mi_parentRigNull = mi_moduleParent.rigNull
                    if mi_parentRigNull.getMessage('cog'):
                        ml_footDynParents.append( mi_parentRigNull.cog )	    
                    if mi_parentRigNull.getMessage('hips'):
                        ml_footDynParents.append( mi_parentRigNull.hips )	    
                if mi_controlIK.msgList_getMessage('spacePivots'):
                    ml_footDynParents.extend(mi_controlIK.msgList_get('spacePivots',asMeta = True))

                log.info("%s.build_rig>>> Dynamic parents to add: %s"%(mi_go._strShortName,[i_obj.getShortName() for i_obj in ml_footDynParents]))

                #Add our parents
                i_dynGroup = mi_controlIK.dynParentGroup
                log.info("Dyn group at setup: %s"%i_dynGroup)
                i_dynGroup.dynMode = 0

                for o in ml_footDynParents:
                    i_dynGroup.addDynParent(o)
                i_dynGroup.rebuild()

                #i_dynGroup.dynFollow.parent = mi_go._i_masterDeformGroup.mNode
            except Exception,error:raise Exception,"Foot dynParent group fail! | error: {0}".format(error)


            #Dynamic parent groups
            #====================================================================================
            try:#>>>> Knee
                #Build our dynamic groups
                ml_kneeDynParents = [mi_controlIK]
                ml_kneeDynParents.append(mi_go._i_masterControl)
                if mi_moduleParent:
                    mi_parentRigNull = mi_moduleParent.rigNull
                    if mi_parentRigNull.getMessage('cog'):
                        ml_kneeDynParents.append( mi_parentRigNull.cog )	    
                    if mi_parentRigNull.getMessage('hips'):
                        ml_kneeDynParents.append( mi_parentRigNull.hips )	    
                if mi_controlIK.msgList_getMessage('spacePivots'):
                    ml_kneeDynParents.extend(mi_controlIK.msgList_get('spacePivots',asMeta = True))

                log.info("%s.build_rig>>> Dynamic parents to add: %s"%(mi_go._strShortName,[i_obj.getShortName() for i_obj in ml_kneeDynParents]))

                #Add our parents
                i_dynGroup = mi_controlMidIK.dynParentGroup
                log.info("Dyn group at setup: %s"%i_dynGroup)
                i_dynGroup.dynMode = 0

                for o in ml_kneeDynParents:
                    i_dynGroup.addDynParent(o)
                i_dynGroup.rebuild()

                #i_dynGroup.dynFollow.parent = mi_go._i_masterDeformGroup.mNode

            except Exception,error:raise Exception,"Knee dynParent fail! | error: {0}".format(error)

            mi_go.collect_worldDynDrivers()#...collect world dyn drivers

            #Make some connections
            #=
            #cgmMeta.cgmAttr(mi_settings,"kneeSpace_in").doConnectIn("%s.space"%mi_controlMidIK.mNode)#This connects to one of our twist fixes from the deformation setup


            try:#Parent and constrain joints
                #====================================================================================
                ml_rigJoints[0].parent = mi_go._i_deformNull.mNode#hip

                for i,i_jnt in enumerate(d_indexRigJointToDriver.keys()):
                    #Don't try scale constraints in here, they're not viable
                    attachJoint = d_indexRigJointToDriver[i_jnt].getShortName()
                    log.info("'%s'>>drives>>'%s'"%(attachJoint,i_jnt.getShortName()))
                    pntConstBuffer = mc.pointConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
                    orConstBuffer = mc.orientConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
                    if i_jnt.hasAttr('scaleJoint') and i_jnt.cgmName != 'ankle':
                        mc.connectAttr((attachJoint+'.s'),(i_jnt.getMessage('scaleJoint')[0] +'.s'))	    
                    else:
                        mc.connectAttr((attachJoint+'.s'),(i_jnt.mNode+'.s'))

                if ml_rigHandleJoints[-2].getMessage('scaleJoint'):#If our ankle has a scale joint, we need to connect it to our last joint of our last segment
                    attributes.doConnectAttr((ml_segmentChains[-1][-1].mNode + '.s'),(ml_rigHandleJoints[-2].scaleJoint.mNode+'.s'))


                #Now we need to make an average for the extra knee that averages the seg0,1 knees
                i_pma = cgmMeta.cgmNode(nodeType = 'plusMinusAverage')
                i_pma.operation = 3#average
                mc.connectAttr("%s.s"%ml_segmentChains[0][-1].mNode,"%s.%s"%(i_pma.mNode,'input3D[0]'))
                mc.connectAttr("%s.s"%ml_segmentChains[-1][0].mNode,"%s.%s"%(i_pma.mNode,'input3D[1]'))
                mc.connectAttr("%s.%s"%(i_pma.mNode,
                                        'output3D'),
                               "%s.s"%(ml_rigHandleJoints[1].scaleJoint.mNode),force=True)

            except Exception,error:raise Exception,"Parent joints fail! | error: {0}".format(error)


            try:#Vis Network, lock and hide
                #====================================================================================
                #Segment handles need to lock
                attributes.doSetLockHideKeyableAttr(mi_settings.mNode,lock=True, visible=False, keyable=False)

                attributes.doSetLockHideKeyableAttr(mi_controlIK.mNode,channels=['sx','sy','sz','v'],lock=True, visible=False, keyable=False)

                attributes.doSetLockHideKeyableAttr(mi_controlMidIK.mNode,channels=['v'],lock=True, visible=False, keyable=False)


                for mJnt in ml_fkJoints:
                    cgmMeta.cgmAttr(mJnt,"translate",lock=True,hidden=True,keyable=False)  	
                    cgmMeta.cgmAttr(mJnt,"scale",lock=True,hidden=True,keyable=False)  	
                    mJnt.radius = 0
                    
                for mJnt in ml_blendJoints:
                    attributes.doSetLockHideKeyableAttr(mJnt.mNode,lock=True, visible=True, keyable=False)
                    mJnt.radius = 0#This is how we can hide joints without hiding them since we have children we want to ride along
                    mJnt.drawStyle = 2
                                        
                #Set group lockks
                for mCtrl in mi_go._i_rigNull.msgList_get('controlsAll'):
                    mCtrl._setControlGroupLocks()	

                #Aim Scale locking on segment handles
                for mChain in ml_segmentHandleChains:
                    for mCtrl in mChain:
                        cgmMeta.cgmAttr(mCtrl,"s%s"%orientation[0],lock=True,hidden=True,keyable=False)  	
                        cgmMeta.cgmAttr(mCtrl,"v",lock=True,hidden=True,keyable=False)
            except Exception,error:raise Exception,"Vis/Lock/Hide fail! | error: {0}".format(error)


            try:#Setup foot Scaling
                #===================================================================================		
                #Ik Scale Object
                mPlug_ikFootScale = cgmMeta.cgmAttr(mi_controlIK,'sy')

                mi_controlIK.scalePivotY = 0
                vBuffer = mc.xform(mi_controlIK.mNode,q=True,sp=True,ws=True)	    
                mc.xform(mi_controlIK.mNode,sp=(vBuffer[0],0,vBuffer[2]),ws=True)
                
                for obj in ml_ikJoints[-3:-1]:
                    cgmMeta.cgmAttr(mi_controlIK,'scale').doConnectOut("%s.scale"%obj.mNode)
                for attr in ['x','z']:
                    cgmMeta.cgmAttr(mi_controlIK,'sy').doConnectOut("%s.s%s"%(mi_controlIK.mNode,attr))

                #attributes.doSetLockHideKeyableAttr(mi_controlIK.mNode,lock=True,visible=False,keyable=False,channels=['sz','sx'])    
                mPlug_ikFootScale.p_nameAlias = 'ikScale'
                mPlug_ikFootScale.p_keyable = True
                mPlug_ikFootScale.p_lock = False

                #FK Scale
                mPlug_fkFootScale = cgmMeta.cgmAttr(ml_controlsFK[-2],'s%s'%orientation[0])

                #attributes.doSetLockHideKeyableAttr(ml_controlsFK[-2].mNode,lock=False,visible=True,keyable=True, channels=['s%s'%orientation[0]])
                for attr in orientation[1:]:
                    mPlug_fkFootScale.doConnectOut("%s.s%s"%(ml_controlsFK[-2].mNode,attr))

                mPlug_fkFootScale.doConnectOut("%s.scale"%ml_controlsFK[-1].mNode)
                mPlug_fkFootScale.doConnectOut("%s.inverseScale"%ml_controlsFK[-1].mNode)

                mPlug_fkFootScale.p_nameAlias = 'fkScale'
                mPlug_fkFootScale.p_keyable = True
                mPlug_fkFootScale.p_lock = False

                #Blend the two
                mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK')
                rUtils.connectBlendJointChain(ml_fkJoints[-2:],ml_ikJoints[-3:-1],ml_blendJoints[-2:],
                                              driver = mPlug_FKIK.p_combinedName,channels=['scale'])    

            except Exception,error:raise Exception,"Foot scaling setup fail! | error: {0}".format(error)



            try:#Set up some defaults
                #====================================================================================
                mPlug_autoStretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch')
                mPlug_autoStretch.p_defaultValue = 1.0
                mPlug_autoStretch.value =  1

                mPlug_seg0end = cgmMeta.cgmAttr(ml_segmentHandleChains[0][-1],'followRoot')
                mPlug_seg0end.p_defaultValue = .5
                mPlug_seg0end.value = .5

                mPlug_seg1end = cgmMeta.cgmAttr(ml_segmentHandleChains[1][-1],'followRoot')
                mPlug_seg1end.p_defaultValue = .5
                mPlug_seg1end.value = .5	

                #mid segment handles
                mPlug_seg0mid = cgmMeta.cgmAttr(ml_segmentHandleChains[0][1],'twistExtendToEnd')
                mPlug_seg0mid.p_defaultValue = 0
                mPlug_seg0mid.value = 0	

                mPlug_seg1mid = cgmMeta.cgmAttr(ml_segmentHandleChains[1][1],'twistExtendToEnd')
                mPlug_seg1mid.p_defaultValue = 0
                mPlug_seg1mid.value = 0		

            except Exception,error:raise Exception,"Defaults fail! | error: {0}".format(error)

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
        log.error("leg.build_deformationRig>>bad self!")
        raise Exception,error

    _str_funcName = "build_rig(%s)"%self._strShortName
    log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()     


    try:#>>>Get data
        _str_subFunc = "Get Data"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        orientation = self._jointOrientation or modules.returnSettingsData('jointOrientation')
        mi_moduleParent = False
        if self._mi_module.getMessage('moduleParent'):
            mi_moduleParent = self._mi_module.moduleParent

        mi_controlIK = self._i_rigNull.controlIK
        mi_controlMidIK = self._i_rigNull.midIK 
        ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
        ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
        ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
        mi_settings = self._i_rigNull.settings

        mi_controlIK = self._i_rigNull.controlIK
        mi_controlMidIK = self._i_rigNull.midIK

        log.debug("mi_controlIK: %s"%mi_controlIK.mNode)
        log.debug("mi_controlMidIK: %s"%mi_controlMidIK.mNode)	
        log.debug("ml_controlsFK: %s"%[o.getShortName() for o in ml_controlsFK])
        log.debug("mi_settings: %s"%mi_settings.mNode)

        log.debug("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
        log.debug("ml_blendJoints: %s"%[o.getShortName() for o in ml_blendJoints])

        ml_segmentHandleChains = self._get_segmentHandleChains()
        ml_segmentChains = self._get_segmentChains()
        ml_influenceChains = self._get_influenceChains()	
        ml_rigHandleJoints = self._get_handleJoints()
        aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
        upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1]) 

        #Build our contrain to pool
        d_indexRigJointToDriver = self._get_simpleRigJointDriverDict()

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#Constrain to pelvis
        _str_subFunc = "Parent constrain"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        if mi_moduleParent:
            mc.parentConstraint(mi_moduleParent.rigNull.msgList_getMessage('moduleJoints')[0],self._i_constrainNull.mNode,maintainOffset = True)
        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)   

    #Dynamic parent groups
    #====================================================================================
    try:#>>>> Foot
        _str_subFunc = "Foot dynParent"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        #Build our dynamic groups
        ml_footDynParents = [self._i_masterControl]
        if mi_moduleParent:
            mi_parentRigNull = mi_moduleParent.rigNull
            if mi_parentRigNull.getMessage('cog'):
                ml_footDynParents.append( mi_parentRigNull.cog )	    
            if mi_parentRigNull.getMessage('hips'):
                ml_footDynParents.append( mi_parentRigNull.hips )	    
        if mi_controlIK.msgList_getMessage('spacePivots'):
            ml_footDynParents.extend(mi_controlIK.msgList_get('spacePivots',asMeta = True))

        log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._strShortName,[i_obj.getShortName() for i_obj in ml_footDynParents]))

        #Add our parents
        i_dynGroup = mi_controlIK.dynParentGroup
        log.info("Dyn group at setup: %s"%i_dynGroup)
        i_dynGroup.dynMode = 0

        for o in ml_footDynParents:
            i_dynGroup.addDynParent(o)
        i_dynGroup.rebuild()

        #i_dynGroup.dynFollow.parent = self._i_masterDeformGroup.mNode
        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #Dynamic parent groups
    #====================================================================================
    try:#>>>> Knee
        _str_subFunc = "Knee dynParent"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        #Build our dynamic groups
        ml_kneeDynParents = [mi_controlIK]
        ml_kneeDynParents.append(self._i_masterControl)
        if mi_moduleParent:
            mi_parentRigNull = mi_moduleParent.rigNull
            if mi_parentRigNull.getMessage('cog'):
                ml_kneeDynParents.append( mi_parentRigNull.cog )	    
            if mi_parentRigNull.getMessage('hips'):
                ml_kneeDynParents.append( mi_parentRigNull.hips )	    
        if mi_controlIK.msgList_getMessage('spacePivots'):
            ml_kneeDynParents.extend(mi_controlIK.msgList_get('spacePivots',asMeta = True))

        log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._strShortName,[i_obj.getShortName() for i_obj in ml_kneeDynParents]))

        #Add our parents
        i_dynGroup = mi_controlMidIK.dynParentGroup
        log.info("Dyn group at setup: %s"%i_dynGroup)
        i_dynGroup.dynMode = 0

        for o in ml_kneeDynParents:
            i_dynGroup.addDynParent(o)
        i_dynGroup.rebuild()

        #i_dynGroup.dynFollow.parent = self._i_masterDeformGroup.mNode

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #Make some connections
    #=
    #cgmMeta.cgmAttr(mi_settings,"kneeSpace_in").doConnectIn("%s.space"%mi_controlMidIK.mNode)#This connects to one of our twist fixes from the deformation setup


    try:#Parent and constrain joints
        #====================================================================================
        _str_subFunc = "Parent joints"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        ml_rigJoints[0].parent = self._i_deformNull.mNode#hip

        for i,i_jnt in enumerate(d_indexRigJointToDriver.keys()):
            #Don't try scale constraints in here, they're not viable
            attachJoint = d_indexRigJointToDriver[i_jnt].getShortName()
            log.info("'%s'>>drives>>'%s'"%(attachJoint,i_jnt.getShortName()))
            pntConstBuffer = mc.pointConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
            orConstBuffer = mc.orientConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
            if i_jnt.hasAttr('scaleJoint') and i_jnt.cgmName != 'ankle':
                mc.connectAttr((attachJoint+'.s'),(i_jnt.getMessage('scaleJoint')[0] +'.s'))	    
            else:
                mc.connectAttr((attachJoint+'.s'),(i_jnt.mNode+'.s'))

        if ml_rigHandleJoints[-2].getMessage('scaleJoint'):#If our ankle has a scale joint, we need to connect it to our last joint of our last segment
            attributes.doConnectAttr((ml_segmentChains[-1][-1].mNode + '.s'),(ml_rigHandleJoints[-2].scaleJoint.mNode+'.s'))


        #Now we need to make an average for the extra knee that averages the seg0,1 knees
        i_pma = cgmMeta.cgmNode(nodeType = 'plusMinusAverage')
        i_pma.operation = 3#average
        mc.connectAttr("%s.s"%ml_segmentChains[0][-1].mNode,"%s.%s"%(i_pma.mNode,'input3D[0]'))
        mc.connectAttr("%s.s"%ml_segmentChains[-1][0].mNode,"%s.%s"%(i_pma.mNode,'input3D[1]'))
        mc.connectAttr("%s.%s"%(i_pma.mNode,'output3D'),"%s.s"%(ml_rigHandleJoints[1].scaleJoint.mNode),force=True)

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)    

    try:#Setup foot Scaling
        #====================================================================================
        _str_subFunc = "Foot Scaling"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        ml_fkJoints = self._i_rigNull.msgList_get('fkJoints')
        ml_ikJoints = self._i_rigNull.msgList_get('ikJoints')
        ml_ikPVJoints = self._i_rigNull.msgList_get('ikPVJoints')
        ml_ikNoFlipJoints = self._i_rigNull.msgList_get('ikNoFlipJoints')

        #Ik Scale Object
        mi_controlIK.scalePivotY = 0
        vBuffer = mc.xform(mi_controlIK.mNode,q=True,sp=True,ws=True)	    
        mc.xform(mi_controlIK.mNode,sp=(vBuffer[0],0,vBuffer[2]),ws=True)
        for obj in ml_ikJoints[-3:-1]:
            cgmMeta.cgmAttr(mi_controlIK,'scale').doConnectOut("%s.scale"%obj.mNode)
        for attr in ['x','z']:
            cgmMeta.cgmAttr(mi_controlIK,'sy').doConnectOut("%s.s%s"%(mi_controlIK.mNode,attr))

        attributes.doSetLockHideKeyableAttr(mi_controlIK.mNode,lock=True,visible=False,keyable=False,channels=['sz','sx'])    
        mPlug_ikFootScale = cgmMeta.cgmAttr(mi_controlIK,'sy')
        mPlug_ikFootScale.p_nameAlias = 'ikScale'
        mPlug_ikFootScale.p_keyable = True

        #FK Scale
        attributes.doSetLockHideKeyableAttr(ml_controlsFK[-2].mNode,lock=False,visible=True,keyable=True,channels=['s%s'%orientation[0]])
        for attr in orientation[1:]:
            cgmMeta.cgmAttr(ml_controlsFK[-2],'s%s'%orientation[0]).doConnectOut("%s.s%s"%(ml_controlsFK[-2].mNode,attr))

        cgmMeta.cgmAttr(ml_controlsFK[-2],'scale').doConnectOut("%s.scale"%ml_controlsFK[-1].mNode)
        cgmMeta.cgmAttr(ml_controlsFK[-2],'scale').doConnectOut("%s.inverseScale"%ml_controlsFK[-1].mNode)

        mPlug_fkFootScale = cgmMeta.cgmAttr(ml_controlsFK[-2],'s%s'%orientation[0])
        mPlug_fkFootScale.p_nameAlias = 'fkScale'
        mPlug_fkFootScale.p_keyable = True

        #Blend the two
        mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK')
        rUtils.connectBlendJointChain(ml_fkJoints[-2:],ml_ikJoints[-3:-1],ml_blendJoints[-2:],
                                      driver = mPlug_FKIK.p_combinedName,channels=['scale'])    

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)	     

    try:#Vis Network, lock and hide
        #====================================================================================
        _str_subFunc = "Lock and Hide"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        #Segment handles need to lock
        attributes.doSetLockHideKeyableAttr(mi_settings.mNode,lock=True, visible=False, keyable=False)

        for i_jnt in ml_blendJoints:
            attributes.doSetLockHideKeyableAttr(i_jnt.mNode,lock=True, visible=True, keyable=False)
            i_jnt.radius = 0#This is how we can hide joints without hiding them since we have children we want to ride along
            i_jnt.drawStyle = 2

        #Set group lockks
        for mCtrl in self._i_rigNull.msgList_get('controlsAll'):
            mCtrl._setControlGroupLocks()	

        #Aim Scale locking on segment handles
        for mChain in ml_segmentHandleChains:
            for mCtrl in mChain:
                cgmMeta.cgmAttr(mCtrl,"s%s"%orientation[0],lock=True,hidden=True,keyable=False)  	

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)


    try:#Set up some defaults
        #====================================================================================
        _str_subFunc = "Attribute Defaults"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        mPlug_autoStretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch')
        mPlug_autoStretch.p_defaultValue = 1.0
        mPlug_autoStretch.value =  1

        mPlug_seg0end = cgmMeta.cgmAttr(ml_segmentHandleChains[0][-1],'followRoot')
        mPlug_seg0end.p_defaultValue = .5
        mPlug_seg0end.value = .5

        mPlug_seg1end = cgmMeta.cgmAttr(ml_segmentHandleChains[1][-1],'followRoot')
        mPlug_seg1end.p_defaultValue = .5
        mPlug_seg1end.value = .5	

        #mid segment handles
        mPlug_seg0mid = cgmMeta.cgmAttr(ml_segmentHandleChains[0][1],'twistExtendToEnd')
        mPlug_seg0mid.p_defaultValue = 1
        mPlug_seg0mid.value = 1	

        mPlug_seg1mid = cgmMeta.cgmAttr(ml_segmentHandleChains[1][1],'twistExtendToEnd')
        mPlug_seg1mid.p_defaultValue = 1
        mPlug_seg1mid.value = 1		

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)     

    #Final stuff
    self._set_versionToCurrent()

    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     	

    return True 
#------------------------------------------------------------------------------------------------------------#    
def build_twistDriver_hip(self):
    try:
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("build_twistDriver_hip>>bad self!")
        raise Exception,error

    _str_funcName = "build_twistDriver_hip(%s)"%self._strShortName
    log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()      

    try:#Data gather
        _str_subFunc = "Get Data"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        mi_settings = self._i_rigNull.settings	
        mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#Parenting
        _str_subFunc = "Parenting"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        mi_parentRigNull = self._mi_module.moduleParent.rigNull
        mi_hips = mi_parentRigNull.hips	

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#Create
        _str_subFunc = "Create"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        outVector = self._vectorOut
        upVector = self._vectorUp      
        ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')


        #Create joints
        #i_startAim = self.duplicate_moduleJoint(0,'startAim')
        #i_startEnd = self.duplicate_moduleJoint(0,'startAimEnd')
        i_startRoot = self._ml_moduleJoints[0].doDuplicate(inputConnections = False,)
        i_startRoot.addAttr('cgmName',self._partName)	
        i_startRoot.addAttr('cgmTypeModifier','twistDriver')
        i_startRoot.doName()
        i_startEnd = self._ml_moduleJoints[0].doDuplicate(inputConnections = False,)
        i_startEnd.addAttr('cgmTypeModifier','twistDriverEnd')
        i_startEnd.doName()    

        i_upLoc = i_startRoot.doLoc()	

        i_startEnd.parent = i_startRoot.mNode
        ml_twistObjects = [i_startRoot,i_startEnd,i_upLoc]
        fl_dist = 25
        if self._direction == 'left':#if right, rotate the pivots
            i_upLoc.__setattr__('t%s'%self._jointOrientation[2],fl_dist)	
        else:
            i_upLoc.__setattr__('t%s'%self._jointOrientation[2],fl_dist)		

        #Move up
        i_startEnd.__setattr__('t%s'%self._jointOrientation[0],(fl_dist))

        i_startRoot.parent = ml_blendJoints[0].mNode

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    #=============================================================================
    try:#setup stable hip rotate group  
        _str_subFunc = "Stable hit rotate group"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        i_rotGroup = self._i_constrainNull.doDuplicateTransform(False)
        i_rotGroup.addAttr('cgmType','stableHipTwistRotGroup')
        i_rotGroup.doName()
        ml_twistObjects.append(i_rotGroup)
        i_upLoc.parent = i_rotGroup.mNode

        i_rotGroup.parent = self._i_constrainNull.mNode
        '''
	NodeF.argsToNodes("%s.ry = %s.ry"%(i_rotGroup.p_nameShort,
	                                   self._i_constrainNull.p_nameShort)).doBuild()'''	

        NodeF.argsToNodes("%s.ry = -%s.ry + %s.ry"%(i_rotGroup.p_nameShort,
                                                    self._i_constrainNull.p_nameShort,
                                                    ml_blendJoints[0].p_nameShort)).doBuild()	

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)
    #=============================================================================
    #Create IK handle
    try:
        _str_subFunc = "IK Handle"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        buffer = mc.ikHandle( sj=i_startRoot.mNode, ee=i_startEnd.mNode,
                              solver = 'ikRPsolver', forceSolver = True,
                              snapHandleFlagToggle=True )  

        #>>> Name
        str_baseName = self._partName + "_startTwistDriver"
        i_ik_handle = cgmMeta.asMeta(buffer[0],'cgmObject',setClass=True)
        i_ik_handle.addAttr('cgmName',str_baseName ,attrType='string',lock=True)    
        i_ik_handle.doName()
        i_ik_handle.parent = self._i_rigNull.mNode
        mc.pointConstraint(ml_blendJoints[1].mNode,i_ik_handle.mNode)

        ml_twistObjects.append(i_ik_handle)

        i_ik_effector = cgmMeta.asMeta(buffer[1],'cgmNode',setClass=True)
        i_ik_effector.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
        i_ik_effector.doName()

        cBuffer = mc.poleVectorConstraint(i_upLoc.mNode,i_ik_handle.mNode)#Polevector	
        rUtils.IKHandle_fixTwist(i_ik_handle.mNode)#Fix the wist

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #>>> Control	
    try:#>>> Connect in
        _str_subFunc = "Connect Control"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        cgmMeta.cgmAttr(self._mi_module.rigNull.settings,'in_worldIKStart').doConnectIn("%s.r%s"%(i_startRoot.mNode,self._jointOrientation[0]))
        self.connect_toRigGutsVis(ml_twistObjects)#connect to guts vis switches

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     	

    return True
#------------------------------------------------------------------------------------------------------------#    
def build_twistDriver_ankle(self):
    try:
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("build_ankleTwistDriver>>bad self!")
        raise Exception,error

    _str_funcName = "build_twistDriver_ankle(%s)"%self._strShortName
    log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()   

    try:#Get Data
        _str_subFunc = "Get Data"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        mi_controlIK = self._i_rigNull.controlIK
        mi_settings = self._i_rigNull.settings
        mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)
        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 

    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:
        _str_subFunc = "Create"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        str_baseName = self._partName + "_endTwistDriver"

        outVector = self._vectorOut
        upVector = self._vectorUp      
        ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
        ml_ikJoints = self._i_rigNull.msgList_get('ikJoints')	
        ml_rigHandleJoints = self._get_handleJoints()
        i_targetJoint = ml_rigHandleJoints[2]#This should be the ankle
        i_blendAnkle = ml_blendJoints[2]
        if i_targetJoint.cgmName != 'ankle':
            raise Exception,"%s.build_ankleTwistDriver >> target not ankle? | %s"%(self._strShortName,i_targetJoint.p_nameShort)	
        if i_blendAnkle.cgmName != 'ankle':
            raise Exception,"%s.build_ankleTwistDriver >> target not ankle? | %s"%(self._strShortName,i_blendAnkle.p_nameShort)	

        #Create joints
        #i_startAim = self.duplicate_moduleJoint(0,'startAim')
        #i_startEnd = self.duplicate_moduleJoint(0,'startAimEnd')
        i_startRoot = i_targetJoint.doDuplicate(inputConnections = False,)
        i_startRoot.addAttr('cgmName',str_baseName)
        i_startRoot.addAttr('cgmTypeModifier','twistDriver')
        i_startRoot.doName()
        i_startEnd = i_targetJoint.doDuplicate(inputConnections = False,)
        i_startEnd.addAttr('cgmTypeModifier','twistDriverEnd')
        i_startEnd.doName()    

        i_upLoc = i_startRoot.doLoc()

        i_startEnd.parent = i_startRoot.mNode
        ml_twistObjects = [i_startRoot,i_startEnd,i_upLoc]
        fl_dist = 25
        if self._direction == 'left':#if right, rotate the pivots
            i_upLoc.__setattr__('t%s'%self._jointOrientation[2],fl_dist)	
        else:
            i_upLoc.__setattr__('t%s'%self._jointOrientation[2],-fl_dist)

        i_startEnd.__setattr__('t%s'%self._jointOrientation[0],-(fl_dist))

        #Move up
        #i_startEnd.__setattr__('t%s'%self._jointOrientation[0],-(fl_dist))
        #mc.move(upVector[0]*fl_dist,upVector[1]*(fl_dist),upVector[2]*fl_dist,i_startEnd.mNode,r=True, rpr = True, os = True, wd = True)	

        i_startRoot.parent = ml_ikJoints[1].mNode
        i_startRoot.rotateOrder = 0 #xyz
        mc.pointConstraint(i_blendAnkle.mNode,i_startRoot.mNode,mo=True)#constrain

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #=============================================================================
    #Create IK handle
    try:
        _str_subFunc = "IK Handle"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        buffer = mc.ikHandle( sj=i_startRoot.mNode, ee=i_startEnd.mNode,
                              solver = 'ikRPsolver', forceSolver = True,
                              snapHandleFlagToggle=True )  

        #>>> Name
        i_ik_handle = cgmMeta.asMeta(buffer[0],'cgmObject',setClass=True)
        i_ik_handle.addAttr('cgmName',str_baseName ,attrType='string',lock=True)    
        i_ik_handle.doName()
        i_ik_handle.parent = self._i_rigNull.mNode
        mc.pointConstraint(ml_blendJoints[1].mNode,i_ik_handle.mNode)
        ml_twistObjects.append(i_ik_handle)

        i_ik_effector = cgmMeta.asMeta(buffer[1],'cgmNode',setClass=True)
        i_ik_effector.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
        i_ik_effector.doName()

        cBuffer = mc.poleVectorConstraint(i_upLoc.mNode,i_ik_handle.mNode)#Polevector	
        rUtils.IKHandle_fixTwist(i_ik_handle.mNode)#Fix the wist

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    #>>> Control	
    try:
        _str_subFunc = "Control"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        i_rotGroup = mi_controlIK.doDuplicateTransform(False)
        i_rotGroup.addAttr('cgmType','ikEndRotGroup')
        i_rotGroup.doName()
        ml_twistObjects.append(i_rotGroup)
        i_upLoc.parent = i_rotGroup.mNode

        #invert the foot
        NodeF.argsToNodes("%s.rz = -%s.rz"%(i_rotGroup.p_nameShort,
                                            mi_controlIK.p_nameShort)).doBuild()	

        i_rotGroup.parent = self._i_rigNull.pivot_ball

        #>>> Connect in
        mPlug_worldIKEndIn.doConnectIn("%s.r%s"%(i_startRoot.mNode,self._jointOrientation[0]))
        self.connect_toRigGutsVis(ml_twistObjects)#connect to guts vis switches

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     	    
    return True

def build_matchSystem(self):
    try:
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("leg.build_deformationRig>>bad self!")
        raise Exception,error

    _str_funcName = "build_matchSystem(%s)"%self._strShortName
    log.info(">>> %s "%(_str_funcName) + "="*75)
    start = time.clock()    

    try:#Base info
        _str_subFunc = "Get Data"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        mi_moduleParent = False
        if self._mi_module.getMessage('moduleParent'):
            mi_moduleParent = self._mi_module.moduleParent

        mi_controlIK = self._i_rigNull.controlIK
        mi_controlMidIK = self._i_rigNull.midIK 
        ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
        ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
        ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
        mi_settings = self._i_rigNull.settings

        mi_controlIK = self._i_rigNull.controlIK
        mi_controlMidIK = self._i_rigNull.midIK  

        ml_fkJoints = self._i_rigNull.msgList_get('fkJoints')
        ml_ikJoints = self._i_rigNull.msgList_get('ikJoints')
        ml_ikPVJoints = self._i_rigNull.msgList_get('ikPVJoints')
        ml_ikNoFlipJoints = self._i_rigNull.msgList_get('ikNoFlipJoints')

        mi_dynSwitch = self._i_dynSwitch

        if self._str_mirrorDirection == 'Right':
            ml_fkJoints = self._i_rigNull.msgList_get('fkAttachJoints')	

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error) 

    try:#>>> First IK to FK
        _str_subFunc = "IK to FK"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        i_ikFootMatch_noKnee = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlIK,
                                                          dynPrefix = "FKtoIK",
                                                          dynMatchTargets=ml_blendJoints[-2])
        i_ikFootMatch_noKnee.addPrematchData({'roll':0,'toeSpin':0,'lean':0,'bank':0})
        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 

    except Exception,error:
        raise Exception,"%s >> %s | %s"(_str_funcName,_str_subFunc,error)

    try:#Toe iter
        _str_subFunc = "Toe iter"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  
        log.info(1)
        i_ikFootMatch_noKnee.addDynIterTarget(drivenObject =ml_ikJoints[-1],
                                              matchTarget = ml_blendJoints[-1],#Make a new one
                                              minValue=-90,
                                              maxValue=90,
                                              maxIter=15,
                                              driverAttr='toeWiggle')
        log.info(2)
        i_ikFootMatch_noKnee.addDynIterTarget(drivenObject =ml_ikJoints[1],#knee
                                              matchObject = ml_blendJoints[1],
                                              drivenAttr= 't%s'%self._jointOrientation[0],
                                              matchAttr = 't%s'%self._jointOrientation[0],
                                              minValue=0.001,
                                              maxValue=30,
                                              maxIter=15,
                                              driverAttr='lengthUpr')   
        log.info(3)
        i_ikFootMatch_noKnee.addDynIterTarget(drivenObject =ml_ikJoints[2],#ankle
                                              matchObject= ml_blendJoints[2],#Make a new one
                                              drivenAttr='t%s'%self._jointOrientation[0],
                                              matchAttr = 't%s'%self._jointOrientation[0],
                                              minValue=0.001,
                                              maxValue=30,
                                              maxIter=15,
                                              driverAttr='lengthLwr')  
        log.info(4)
        i_ikFootMatch_noKnee.addDynIterTarget(drivenObject =ml_ikNoFlipJoints[1],#knee
                                              matchTarget = ml_blendJoints[1],#Make a new one
                                              minValue=-179,
                                              maxValue=179,
                                              maxIter=15,
                                              driverAttr='kneeSpin') 
        log.info(5)

        i_ikFootMatch_noKnee.addDynAttrMatchTarget(dynObjectAttr='ikScale',
                                                   matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._jointOrientation[0]],#Make a new one
                                                   )
        log.info('end')
        
        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"{0} >> {1} | {2}".format(_str_funcName,_str_subFunc,error)

    try:#>> Mid...
        _str_subFunc = "Mid"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        """
	i_ikMidMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlMidIK,
						  dynPrefix = "FKtoIK",
						  dynMatchTargets=ml_blendJoints[1]) """

        i_ikMidMatch = mi_controlMidIK.FKtoIK_dynMatchDriver

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"{0} >> {1} | {2}".format(_str_funcName,_str_subFunc,error)

    try:#>>> FK to IK
        _str_subFunc = "FK to IK"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        i_fkHipMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[0],
                                                  dynPrefix = "IKtoFK",
                                                  dynMatchTargets=ml_blendJoints[0])

        i_fkHipMatch.addDynIterTarget(drivenObject = ml_fkJoints[1],
                                      #matchTarget = ml_blendJoints[1],#Make a new one
                                      matchObject = ml_blendJoints[1],
                                      drivenAttr='t%s'%self._jointOrientation[0],
                                      matchAttr = 't%s'%self._jointOrientation[0],
                                      minValue=0.001,
                                      maxValue=30,
                                      maxIter=15,
                                      driverAttr='length')  

        i_fkKneeMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[1],
                                                   dynPrefix = "IKtoFK",
                                                   dynMatchTargets=ml_blendJoints[1])

        i_fkKneeMatch.addDynIterTarget(drivenObject =ml_fkJoints[2],
                                       #matchTarget = ml_blendJoints[2],#Make a new one
                                       matchObject = ml_blendJoints[2],                                   
                                       drivenAttr='t%s'%self._jointOrientation[0],
                                       matchAttr = 't%s'%self._jointOrientation[0],
                                       minValue=0.001,
                                       maxValue=30,
                                       maxIter=15,
                                       driverAttr='length')  

        i_fkAnkleMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[2],
                                                    dynPrefix = "IKtoFK",
                                                    dynMatchTargets=ml_blendJoints[2])
        i_fkBallMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[3],
                                                   dynPrefix = "IKtoFK",
                                                   dynMatchTargets=ml_blendJoints[3])   

        i_fkAnkleMatch.addDynAttrMatchTarget(dynObjectAttr='fkScale',
                                             matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._jointOrientation[0]],
                                             )    

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"{0} >> {1} | {2}".format(_str_funcName,_str_subFunc,error)

    try:#>>> Register the switches
        _str_subFunc = "Register switches"
        time_sub = time.clock() 
        log.info(">>> %s >> %s "%(_str_funcName,_str_subFunc) + "="*50)  

        mi_dynSwitch.addSwitch('snapToFK',[mi_settings.mNode,'blend_FKIK'],
                               0,
                               [i_fkHipMatch,i_fkKneeMatch,i_fkAnkleMatch,i_fkBallMatch])

        mi_dynSwitch.addSwitch('snapToIK_noKnee',[mi_settings.mNode,'blend_FKIK'],
                               1,
                               [i_ikFootMatch_noKnee,i_ikMidMatch])
        mi_dynSwitch.addSwitch('snapToIK_knee',[mi_settings.mNode,'blend_FKIK'],
                               1,
                               [i_ikFootMatch_noKnee,i_ikMidMatch])

        mi_dynSwitch.setPostmatchAliasAttr('snapToIK_noKnee',[mi_controlIK.mNode,'showKnee'],0)
        mi_dynSwitch.setPostmatchAliasAttr('snapToIK_knee',[mi_controlIK.mNode,'showKnee'],1)

        log.info("%s >> Time >> %s = %0.3f seconds " % (_str_funcName,_str_subFunc,(time.clock()-time_sub)) + "-"*75) 
    except Exception,error:
        raise Exception,"{0} >> {1} | {2}".format(_str_funcName,_str_subFunc,error)

    log.info("%s >> Complete Time >> %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)     	    
    return True

"""
def __build__(self, buildTo='',*args,**kws): 
    try:
	if not self._cgmClass == 'RigFactory.go':
	    log.error("Not a RigFactory.go instance: '%s'"%self)
	    raise Exception
    except Exception,error:
	log.error("spine.build_deformationRig>>bad self!")
	raise Exception,error

    if not self.isRigSkeletonized():
	build_rigSkeleton(self)  
    if buildTo.lower() == 'skeleton':return True    
    if not self.isShaped():
	build_shapes(self)
    if buildTo.lower() == 'shapes':return True
    build_controls(self)
    if buildTo.lower() == 'controls':return True    
    build_foot(self)
    if buildTo.lower() == 'foot':return True
    build_FKIK(self)
    if buildTo.lower() == 'fkik':return True 
    build_deformation(self)
    if buildTo.lower() == 'deformation':return True 
    build_rig(self)
    if buildTo.lower() == 'rig':return True   
    build_matchSystem(self)
    if buildTo.lower() == 'match':return True 
    build_twistDriver_hip(self)
    if buildTo.lower() == 'hipDriver':return True   
    build_twistDriver_ankle(self)
    if buildTo.lower() == 'ankleDriver':return True       
    #build_deformation(self)
    #build_rig(self)    

    return True"""

#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'foot','function':build_foot},
                    4:{'name':'fkik','function':build_FKIK},
                    5:{'name':'deformation','function':build_deformation},
                    6:{'name':'rig','function':build_rig},
                    7:{'name':'match','function':build_matchSystem},
                    8:{'name':'hipDriver','function':build_twistDriver_hip},
                    9:{'name':'ankleDriver','function':build_twistDriver_ankle},                    
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------