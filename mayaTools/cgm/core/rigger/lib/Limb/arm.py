"""
------------------------------------------
cgm.core.rigger: Limb.arm
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

arm rig builder
================================================================
"""
__version__ = 'beta.08032015'

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
#from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.rigger.lib import module_Utils as modUtils
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.rigger.lib import cgmRigs_sharedData as cgmRigsData
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools
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
import cgm.core.rig.segment_utils as SEGMENT
import cgm.core.lib.attribute_utils as ATTR
import cgm.core.lib.distance_utils as DIST


#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['rigJoints','influenceJoints','fkJoints','ikJoints','blendJoints']   
__d_preferredAngles__ = {'shoulder':[0,-10,10],'elbow':[0,-10,0]}#In terms of aim up out for orientation relative values, stored left, if right, it will invert
__d_controlShapes__ = {'shape':['segmentIK','controlsFK','midIK','settings','hand']}

def __bindSkeletonSetup__(self):
    """
    TODO: Do I need to connect per joint overrides or will the final group setup get them?
    """
    log.info(">>> %s.__bindSkeletonSetup__ >> "%self._strShortName + "="*75)            
    try:
        if not self._cgmClass == 'JointFactory.go':
            log.error("Not a JointFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("arm.__bindSkeletonSetup__>>bad self!")
        raise Exception,error

    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self.rig_getSkinJoints() or []
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
            if i_jnt in ml_handleJoints and i_jnt.getMayaAttr('cgmName') not in ['ball']:
                if i == 0:i_jnt.parent = ml_moduleJoints[0].mNode#Parent head to root
                i_dupJnt = i_jnt.doDuplicate(parentOnly = True)#Duplicate
                i_dupJnt.addAttr('cgmTypeModifier','scale')#Tag
                #i_jnt.doName()#Rename
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

    except Exception,error:
        log.error("build_arm>>__bindSkeletonSetup__ fail!")
        raise Exception,error   

def build_rigSkeleton(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_rigSkeleton(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Build Chains','call':self.build_chains},
                                {'step':'FK Chain','call':self.build_fkJoints},
                                {'step':'Rotate Orders','call':self.build_rotateOrders},
                                {'step':'Influence Chains','call':self.build_influenceChains},
                                {'step':'Segment Chains','call':self.build_segmentChains},
                                {'step':'Connections','call':self.build_connections}]	
            #=================================================================

        def build_chains(self):#================================================================================
            self.ml_jointsToConnect = []

            try:#Rig chain
                ml_rigJoints = self._go.build_rigChain()
                ml_rigJoints[0].parent = False#Parent to world
                self._go._i_rigNull.msgList_connect('rigJoints',ml_rigJoints,"rigNull")

                self.ml_rigJoints = ml_rigJoints#pass to wrapper
            except Exception,error: raise Exception,"Rig chain | %s"%error

            try:#Blend Chain 
                self.ml_blendJoints = self._go.build_handleChain('blend','blendJoints')	   

            except Exception,error: raise Exception,"Blend chain | %s"%error

            try:#Ik chain
                self.ml_ikJoints = self._go.build_handleChain('ik','ikJoints')

                for i_jnt in self.ml_ikJoints:
                    if i_jnt.cgmName in __d_preferredAngles__.keys():
                        #log.info("preferred angles(%s)>>> %s"%(i_jnt.cgmName,__d_preferredAngles__.get(i_jnt.cgmName)))
                        for i,v in enumerate(__d_preferredAngles__.get(i_jnt.cgmName)):	
                            if self._go._direction.lower() == 'right':#negative value
                                i_jnt.__setattr__('preferredAngle%s'%self._go._jointOrientation[i].upper(),-v)				
                            else:
                                i_jnt.__setattr__('preferredAngle%s'%self._go._jointOrientation[i].upper(),v)


            except Exception,error: raise Exception,"Ik chain | %s"%error

        def build_fkJoints(self):#==============================================================================
            ml_fkJoints = self._go.build_handleChain('fk','fkJoints')

            try:
                self.ml_fkDriverJoints = []
                if self._go._str_mirrorDirection == 'Right':#mirror control setup
                    self._go.mirrorChainOrientation(ml_fkJoints)#New 

                    self.ml_fkDriverJoints = self._go.build_handleChain('fkAttach','fkAttachJoints')
                    for i,mJoint in enumerate(ml_fkJoints):
                        log.info("Mirror connect: %s | %s"%(i,mJoint.p_nameShort))
                        mJoint.connectChildNode(self.ml_fkDriverJoints[i],"attachJoint","rootJoint")
                        cgmMeta.cgmAttr(mJoint.mNode,"rotateOrder").doConnectOut("%s.rotateOrder"%self.ml_fkDriverJoints[i].mNode)
            except Exception,error: raise Exception,"Failed to create mirror chain | %s"%error

            self._go._i_rigNull.msgList_connect('fkJoints',ml_fkJoints,"rigNull")
            self.ml_fkJoints = ml_fkJoints#pass to wrapper

        def build_rotateOrders(self):#==========================================================================
            d_fkRotateOrders = {'elbow':2}#old hip - 5

            for i_obj in self.ml_fkJoints:
                if i_obj.getMayaAttr('cgmName') in d_fkRotateOrders.keys():
                    i_obj.rotateOrder = d_fkRotateOrders.get(i_obj.cgmName)   		
                else:
                    i_obj.rotateOrder = self._go._jointOrientation

        def build_influenceChains(self):#=======================================================================
            #>>Influence chain
            #=====================================================================
            d_influenceChainReturns = self._go.build_simpleInfluenceChains(True)
            self.ml_influenceChains = d_influenceChainReturns['ml_influenceChains']
            self.ml_influenceJoints= d_influenceChainReturns['ml_influenceJoints']	
            self.ml_segmentHandleJoints = d_influenceChainReturns['ml_segmentHandleJoints']

            self._go._i_rigNull.msgList_connect('influenceJoints',self.ml_influenceJoints,"rigNull")

            if len(self.ml_segmentHandleJoints)!=3:
                raise Exception,"Don't have 3 influence joints: '%s'"%(self.ml_segmentHandleJoints)

        def build_segmentChains(self):
            self.ml_segmentChains = self._go.build_segmentChains(self.ml_segmentHandleJoints,True)

        def build_connections(self):#=========================================================================== 	    
            ml_jointsToConnect = []
            ml_jointsToConnect.extend(self.ml_rigJoints)    
            ml_jointsToConnect.extend(self.ml_ikJoints)
            ml_jointsToConnect.extend(self.ml_influenceJoints)
            if self.ml_fkDriverJoints:
                ml_jointsToConnect.extend(self.ml_fkDriverJoints)
            for ml_chain in self.ml_segmentChains + self.ml_influenceChains:
                ml_jointsToConnect.extend(ml_chain)    

            self._go.connect_toRigGutsVis(ml_jointsToConnect )

    return fncWrap(goInstance).go()

#>>> Shapes
#===================================================================
def build_shapes(self):
    if self._i_templateNull.handles > 4:
        raise Exception, "Too many handles. don't know how to rig"

    if not self.isRigSkeletonized():
        raise Exception, "Must be rig skeletonized to shape"

    l_influenceChains = []
    ml_influenceChains = []
    try:#Influence Chains get
        for i in range(50):
            buffer = self._i_rigNull.msgList_get('segment%s_InfluenceJoints'%i)
            if buffer:
                ml_influenceChains.append(buffer)
            else:break    
    except Exception,error: raise Exception,"Failed to get influence chains | %s"%error
    if not ml_influenceChains:raise Exception,"Found no influence chains"
    try:
        ml_segmentIKShapes = []
        for i,ml_chain in enumerate(ml_influenceChains):
            mShapeCast.go(self._mi_module,['segmentIK'],targetObjects = [i_jnt.mNode for i_jnt in ml_chain] , storageInstance=self)#This will store controls to a dict called    
            log.debug("%s.build_shapes>>> segmentIK chain %s: %s"%(self._strShortName,i,self._md_controlShapes))
            ml_segmentIKShapes.extend(self._md_controlShapes['segmentIK'])

            self._i_rigNull.msgList_connect('shape_segmentIK_%s'%i,self._md_controlShapes['segmentIK'],"rigNull")		
    except Exception,error: raise Exception,"Failed to generate initial shapes | %s"%error

    self._i_rigNull.msgList_connect('shape_segmentIK',ml_segmentIKShapes,"rigNull")		

    #Rest of it
    l_toBuild = ['segmentFK_Loli','settings','midIK','hand']
    mShapeCast.go(self._mi_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
    self._i_rigNull.msgList_connect('shape_controlsFK',
                                    self._md_controlShapes['segmentFK_Loli'],
                                    "rigNull")	
    self._i_rigNull.connectChildNode(self._md_controlShapes['midIK'],'shape_midIK',"rigNull")
    self._i_rigNull.connectChildNode(self._md_controlShapes['settings'],'shape_settings',"rigNull")		
    self._i_rigNull.connectChildNode(self._md_controlShapes['hand'],'shape_hand',"rigNull")




#>>> Controls
#===================================================================
def build_controls(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_controls(%s)'%self._go._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Verify','call':self.verify},
                                {'step':'Control Groups','call':self.build_groups},
                                {'step':'FK','call':self.build_fk},
                                {'step':'IK','call':self.build_ik},
                                {'step':'Mid','call':self.build_midIK},	  
                                {'step':'Settings','call':self.build_settings},	                        	                        
                                {'step':'IK Segments','call':self.build_ikSegments},
                                {'step':'attributes','call':self.build_attributes},	                        
                                {'step':'Connections','call':self.build_connections}]
            #=================================================================

        def verify(self):  
            self.ml_controlsAll = []

            if not self._go.isShaped():
                raise Exception, "Must be shaped"	    

            self.ml_controlsFK = cgmMeta.validateObjListArg(self._go._i_rigNull.msgList_get('shape_controlsFK'),cgmMeta.cgmObject)
            self.ml_segmentIK = cgmMeta.validateObjListArg(self._go._i_rigNull.msgList_get('shape_segmentIK'),cgmMeta.cgmObject)

            try:
                self.l_segmentIKChains = []
                self.ml_segmentIKChains = []
                for i in range(50):
                    buffer = self._go._i_rigNull.msgList_get('shape_segmentIK_%s'%i,asMeta=False)
                    if buffer:
                        self.l_segmentIKChains.append(buffer)
                        self.ml_segmentIKChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
                    else:
                        break  
            except Exception,error: raise Exception,"Get segment shapes | %s"%error
            if not self.ml_segmentIKChains:raise Exception,"No segment chains found"

            self.mi_midIK = cgmMeta.validateObjArg(self._go._i_rigNull.getMessage('shape_midIK'),cgmMeta.cgmObject)
            self.mi_settings= cgmMeta.validateObjArg(self._go._i_rigNull.getMessage('shape_settings'),cgmMeta.cgmObject)
            self.mi_hand = cgmMeta.validateObjArg(self._go._i_rigNull.getMessage('shape_hand'),cgmMeta.cgmObject)
            self.ml_fkJoints = cgmMeta.validateObjListArg(self._go._i_rigNull.msgList_get('fkJoints'),cgmMeta.cgmObject)


        def build_groups(self):
            for grp in ['controlsFK','controlsIK']:
                i_dup = self._go._i_constrainNull.doCreateAt(copyAttrs=True)
                i_dup.parent = self._go._i_constrainNull.mNode
                i_dup.addAttr('cgmTypeModifier',grp,lock=True)
                i_dup.doName()

                self._go._i_constrainNull.connectChildNode(i_dup,grp,'owner')

        def build_fk(self):
            ml_controlsFK = self.ml_controlsFK
            ml_fkJoints = self.ml_fkJoints

            if len( ml_controlsFK )<3:
                raise Exception,"Must have at least three fk controls"	    

            ml_fkJoints[0].parent = self._go._i_constrainNull.controlsFK.mNode

            for i,i_obj in enumerate(ml_controlsFK):
                d_buffer = mControlFactory.registerControl(i_obj,shapeParentTo=ml_fkJoints[i],
                                                           mirrorSide=self._go._str_mirrorDirection, mirrorAxis="translateX",		                                           
                                                           makeAimable=True,typeModifier='fk',) 	    

                i_obj = d_buffer['instance']
                i_obj.axisAim = "%s+"%self._go._jointOrientation[0]
                i_obj.axisUp= "%s+"%self._go._jointOrientation[1]	
                i_obj.axisOut= "%s+"%self._go._jointOrientation[2]
                try:i_obj.drawStyle = 2#Stick joint draw style	    
                except:self.log_error("{0} Failed to set drawStyle".format(i_obj.p_nameShort))
                cgmMeta.cgmAttr(i_obj,'radius',hidden=True)

            for i_obj in ml_controlsFK:
                i_obj.delete()

            log.info("%s fk: %s"%(self._str_reportStart,self.ml_fkJoints))
            self._go._i_rigNull.msgList_connect('controlsFK',ml_fkJoints,"rigNull")	    
            self.ml_controlsAll.extend(ml_fkJoints)#append	

        def build_ik(self):
            i_IKEnd = self.mi_hand
            i_IKEnd.parent = False
            d_buffer = mControlFactory.registerControl(i_IKEnd,
                                                       mirrorSide=self._go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",	                                               
                                                       typeModifier='ik',addSpacePivots = 1, addDynParentGroup = True, addConstraintGroup=True,
                                                       makeAimable = True,setRotateOrder=2)
            i_IKEnd = d_buffer['instance']	
            i_IKEnd.masterGroup.parent = self._go._i_constrainNull.controlsIK.mNode

            #Set aims
            i_IKEnd.axisAim = 'z+'
            i_IKEnd.axisUp= 'x+'

            log.info("%s hand: %s"%(self._str_reportStart,self.mi_hand))	    
            self._go._i_rigNull.connectChildNode(i_IKEnd,'controlIK',"rigNull")#connect
            self.ml_controlsAll.append(i_IKEnd)	

        def build_midIK(self):
            i_IKmid = self.mi_midIK
            i_IKmid.parent = False
            d_buffer = mControlFactory.registerControl(i_IKmid,addSpacePivots = 1,
                                                       mirrorSide=self._go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",	                                               
                                                       typeModifier='ik',addDynParentGroup = True, addConstraintGroup=True,
                                                       makeAimable = False,setRotateOrder=4)
            i_IKmid = d_buffer['instance']	
            i_IKmid.masterGroup.parent = self._go._i_constrainNull.controlsIK.mNode
            i_IKmid.addAttr('scale',lock=True,hidden=True)

            log.info("%s mid: %s"%(self._str_reportStart,self.mi_midIK))	    
            self._go._i_rigNull.connectChildNode(i_IKmid,'midIK',"rigNull")#connect
            self.ml_controlsAll.append(i_IKmid)	

        def build_settings(self):
            mi_settings = self.mi_settings

            d_buffer = mControlFactory.registerControl(mi_settings,addExtraGroups=0,typeModifier='settings',autoLockNHide=True,
                                                       mirrorSide=self._go._str_mirrorDirection, mirrorAxis="",	                                               
                                                       setRotateOrder=2)       
            i_obj = d_buffer['instance']
            i_obj.masterGroup.parent = self._go._i_constrainNull.mNode
            self._go._i_rigNull.connectChildNode(mi_settings,'settings',"rigNull")
            self.ml_controlsAll.append(mi_settings)	
            log.info("%s settings: %s"%(self._str_reportStart,self.mi_settings))	    

            mi_settings.addAttr('blend_FKIK', defaultValue = 0, attrType = 'float', minValue = 0, maxValue = 1, keyable = False,hidden = False,lock=True)

            self.mPlug_result_moduleSubDriver = self._go.build_visSub()	


        def build_ikSegments(self):
            ml_segmentIKChains = self.ml_segmentIKChains
            for i,chain in enumerate(ml_segmentIKChains):
                ml_controlChain =[]
                for i_obj in chain:
                    d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='segIK',
                                                               mirrorSide=self._go._str_mirrorDirection,mirrorAxis="translateX, rotateY, rotateZ",
                                                               setRotateOrder=2)       
                    i_obj = d_buffer['instance']
                    i_obj.masterGroup.parent = self._go._i_constrainNull.mNode
                    ml_controlChain.append(i_obj)

                    self.mPlug_result_moduleSubDriver.doConnectOut("%s.visibility"%i_obj.mNode)
                self._go._i_rigNull.msgList_connect('segmentHandles_%s'%i,ml_controlChain,"rigNull")
                self.ml_controlsAll.extend(ml_controlChain)
                log.info("%s control chain %s: %s"%(self._str_reportStart,i,ml_controlChain))	    

                if i == 1:
                    #Need to do a few special things for our main segment handle
                    i_mainHandle = chain[0]
                    self._go._i_rigNull.connectChildNode(i_mainHandle,'mainSegmentHandle',"rigNull")
                    curves.setCurveColorByName(i_mainHandle.mNode,self._go._mi_module.getModuleColors()[0])    
                    attributes.doBreakConnection(i_mainHandle.mNode,'visibility')

        def build_attributes(self):
            i_IKEnd = self.mi_hand
            i_IKmid = self.mi_midIK

            mPlug_stretch = cgmMeta.cgmAttr(i_IKEnd,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
            mPlug_lengthUpr= cgmMeta.cgmAttr(i_IKEnd,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
            mPlug_lengthLwr = cgmMeta.cgmAttr(i_IKEnd,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)	
            mPlug_lockMid = cgmMeta.cgmAttr(i_IKmid,'lockMid',attrType='float',defaultValue = 0,keyable = True,minValue=0,maxValue=1.0)

        def build_connections(self):
            try:#>> Extra controls gather...
                ml_extraControls = []
                for i,mCtrl in enumerate(self.ml_controlsAll):
                    try:
                        for str_a in cgmRigsData.__l_moduleControlMsgListHooks__:
                            buffer = mCtrl.msgList_get(str_a)
                            if buffer:
                                ml_extraControls.extend(buffer)
                                log.info("Extra controls : {0}".format(buffer))
                    except Exception,error:
                        self.log_error("mCtrl failed to search for msgList : {0}".format(mCtrl))
                        self.log_error("Fail error : {0}".format(error))
                self.ml_controlsAll.extend(ml_extraControls)			
            except Exception,error:raise Exception,"Extra control gather fail! | error: {0}".format(error)          

            int_strt = self._go._i_puppet.get_nextMirrorIndex( self._go._str_mirrorDirection )
            for i,mCtrl in enumerate(self.ml_controlsAll):
                try:
                    mCtrl.addAttr('mirrorIndex', value = (int_strt + i))		
                except Exception,error: raise Exception,"Failed to register mirror index | mCtrl: %s | %s"%(mCtrl,error)

            try:self._go._i_rigNull.msgList_connect('controlsAll',self.ml_controlsAll)
            except Exception,error: raise Exception,"Controls all connect| %s"%error	    
            try:self._go._i_rigNull.moduleSet.extend(self.ml_controlsAll)
            except Exception,error: raise Exception,"Failed to set module objectSet | %s"%error

    return fncWrap(goInstance).go()   

def build_hand(self):
    """
    """
    try:#===================================================
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("arm.build_hand>>bad self!")
        raise Exception,error

    raise NotImplementedError,"%s.build_hand>> not implemented"%self._strShortName

    #>>>Get data
    ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
    ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
    ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
    ml_fkJoints = self._i_rigNull.msgList_get('fkJoints')
    ml_ikJoints = self._i_rigNull.msgList_get('ikJoints')
    ml_ikPVJoints = self._i_rigNull.ikPVJoints
    ml_ikNoFlipJoints = self._i_rigNull.ikNoFlipJoints

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

    #=============================================================    
    #try:#>>>Hand setup
    mi_pivHeel.parent = mi_controlIK.mNode#heel to hand
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
    #mPlug_elbowSpin = cgmMeta.cgmAttr(mi_controlIK,'elbowSpin',attrType='float',defaultValue = 0,keyable = True)
    mPlug_stretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
    mPlug_showElbow = cgmMeta.cgmAttr(mi_controlIK,'showElbow',attrType='bool',defaultValue = 0,keyable = False)
    mPlug_lengthUpr= cgmMeta.cgmAttr(mi_controlIK,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
    mPlug_lengthLwr = cgmMeta.cgmAttr(mi_controlIK,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)

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
        mPlug_heelClampResult.doConnectOut("%s.r%s"%(mi_pivHeel.mNode,self._jointOrientation[2].lower()))
    except Exception,error:
        raise Exception,"verify_moduleRigToggles>> heel setup fail: %s"%error    

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

        mPlug_all_x_rollResult.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,self._jointOrientation[2].lower()))

    except Exception,error:
        raise Exception,"verify_moduleRigToggles>> ball setup fail: %s"%error   

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

        mPlug_toe_x_rollResult.doConnectOut("%s.r%s"%(mi_pivToe.mNode,self._jointOrientation[2].lower()))
    except Exception,error:
        raise Exception,"verify_moduleRigToggles>> toe setup fail: %s"%error   

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

        mPlug_outerResult.doConnectOut("%s.r%s"%(mi_pivOuter.mNode,self._jointOrientation[0].lower()))
        mPlug_innerResult.doConnectOut("%s.r%s"%(mi_pivInner.mNode,self._jointOrientation[0].lower()))

    except Exception,error:
        raise Exception,"verify_moduleRigToggles>> bank setup fail: %s"%error       

    try:#lean setup 
        """
	Schleifer's
	ball_loc.rotateZ = $lean;
	"""    
        mPlug_lean.doConnectOut("%s.r%s"%(mi_pivBallJoint.mNode,self._jointOrientation[0].lower()))


    except Exception,error:
        raise Exception,"verify_moduleRigToggles>> lean setup fail: %s"%error  

    try:#toe spin setup 
        """
	Schleifer's
	toe_loc.rotateY = $spin;
	"""    
        mPlug_toeSpin.doConnectOut("%s.r%s"%(mi_pivToe.mNode,self._jointOrientation[1].lower()))

    except Exception,error:
        raise Exception,"verify_moduleRigToggles>> toe spin setup fail: %s"%error 

    try:#toe wiggle setup 
        """
	Schleifer's
	toeWiggle_loc.rx = $wiggle;
	"""    
        mPlug_toeWiggle.doConnectOut("%s.r%s"%(mi_pivBallWiggle.mNode,self._jointOrientation[2].lower()))

    except Exception,error:
        raise Exception,"verify_moduleRigToggles>> toe wiggle setup fail: %s"%error 







def build_FKIK(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_FKIK(%s)'%self._go._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Verify','call':self.verify},
                                {'step':'FK Length','call':self.build_fkJointLength},
                                {'step':'IK Setup','call':self.build_pvIK},
                                {'step':'Connections','call':self.build_connections}]
            #=================================================================

        def verify(self):      
            self.ml_controlsFK =  self._go._i_rigNull.msgList_get('controlsFK')   
            self.ml_rigJoints = self._go._i_rigNull.msgList_get('rigJoints')
            self.ml_blendJoints = self._go._i_rigNull.msgList_get('blendJoints')
            self.ml_fkJoints = self._go._i_rigNull.msgList_get('fkJoints')
            self.ml_ikJoints = self._go._i_rigNull.msgList_get('ikJoints')

            self.mi_settings = self._go._i_rigNull.settings

            self.aimVector = cgmValid.simpleAxis("%s+"%self._go._jointOrientation[0]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[0])
            self.upVector = cgmValid.simpleAxis("%s+"%self._go._jointOrientation[1]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[1])
            self.outVector = cgmValid.simpleAxis("%s+"%self._go._jointOrientation[2]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[2])

            self.mi_controlIK = self._go._i_rigNull.controlIK
            self.mi_controlMidIK = self._go._i_rigNull.midIK
            self.mPlug_lockMid = cgmMeta.cgmAttr(self.mi_controlMidIK,'lockMid',attrType='float',defaultValue = 0,keyable = True,minValue=0,maxValue=1.0)

            #for more stable ik, we're gonna lock off the lower channels degrees of freedom
            for chain in [self.ml_ikJoints]:
                for axis in self._go._jointOrientation[:2]:
                    for i_j in chain[1:]:
                        attributes.doSetAttr(i_j.mNode,"jointType%s"%axis.upper(),1)

            self.ml_toParentChains = []
            self.ml_fkAttachJoints = []
            if self._go._str_mirrorDirection == 'Right':#mirror control setup
                self.ml_fkAttachJoints = self._go._i_rigNull.msgList_get('fkAttachJoints')
                self.ml_toParentChains.append(self.ml_fkAttachJoints)

            self.ml_toParentChains.extend([self.ml_ikJoints,self.ml_blendJoints])
            for chain in self.ml_toParentChains:
                chain[0].parent = self._go._i_constrainNull.mNode

        def build_fkJointLength(self):      
            for i,i_jnt in enumerate(self.ml_fkJoints[:-1]):
                rUtils.addJointLengthAttr(i_jnt,orientation=self._go._jointOrientation)

        def build_pvIK(self):
            self.mPlug_globalScale = cgmMeta.cgmAttr(self._go._i_masterControl.mNode,'scaleY')    

            #Create no flip arm IK
            #We're gonna use the no flip stuff for the most part
            d_anklePVReturn = rUtils.IKHandle_create(self.ml_ikJoints[0].mNode,self.ml_ikJoints[-1].mNode,nameSuffix = 'PV',
                                                     rpHandle=True, controlObject=self.mi_controlIK, addLengthMulti=True,
                                                     globalScaleAttr=self.mPlug_globalScale.p_combinedName, stretch='translate',
                                                     moduleInstance=self._go._mi_module)	

            self.mi_ankleIKHandlePV = d_anklePVReturn['mi_handle']
            self.ml_distHandlesPV = d_anklePVReturn['ml_distHandles']
            self.mi_rpHandlePV = d_anklePVReturn['mi_rpHandle']
            self.mPlug_lockMid = d_anklePVReturn['mPlug_lockMid']

            self.mi_ankleIKHandlePV.parent = self.mi_controlIK.mNode#ankleIK to ball		
            self.ml_distHandlesPV[-1].parent = self.mi_controlIK.mNode#ankle distance handle to ball	
            self.ml_distHandlesPV[0].parent = self._go._i_constrainNull.mNode#hip distance handle to deform group
            self.ml_distHandlesPV[1].parent = self.mi_controlMidIK.mNode#elbow distance handle to midIK
            self.mi_rpHandlePV.parent = self.mi_controlMidIK

            #RP handle	
            self.mi_rpHandlePV.doCopyNameTagsFromObject(self._go._mi_module.mNode, ignore = ['cgmName','cgmType'])
            self.mi_rpHandlePV.addAttr('cgmName','elbowPoleVector',attrType = 'string')
            self.mi_rpHandlePV.doName()

            #Mid fix
            #=========================================================================================			
            mc.move(0,0,-25,self.mi_controlMidIK.mNode,r=True, rpr = True, ws = True, wd = True)#move out the midControl to fix the twist from

            #>>> Fix our ik_handle twist at the end of all of the parenting
            rUtils.IKHandle_fixTwist(self.mi_ankleIKHandlePV)#Fix the twist
            log.info("rUtils.IKHandle_fixTwist('%s')"%self.mi_ankleIKHandlePV.getShortName())
            #Register our snap to point before we move it back
            i_ikMidMatch = cgmRigMeta.cgmDynamicMatch(dynObject=self.mi_controlMidIK,
                                                      dynPrefix = "FKtoIK",
                                                      dynMatchTargets=self.ml_blendJoints[1]) 	
            #>>> Reset the translations
            self.mi_controlMidIK.translate = [0,0,0]

            #Move the lock mid and add the toggle so it only works with show elbow on
            self.mPlug_lockMid.doTransferTo(self.mi_controlMidIK.mNode)#move the lock mid	

            #Parent constain the ik wrist joint to the ik wrist
            #=========================================================================================				
            mc.orientConstraint(self.mi_controlIK.mNode,self.ml_ikJoints[-1].mNode, maintainOffset = False)	    

        def build_connections(self):
            try:
                self.mPlug_FKIK = cgmMeta.cgmAttr(self.mi_settings.mNode,'blend_FKIK',lock=False,keyable=True)


                if self.ml_fkAttachJoints:
                    ml_fkUse = self.ml_fkAttachJoints
                    for i,mJoint in enumerate(self.ml_fkAttachJoints):
                        mc.pointConstraint(self.ml_fkJoints[i].mNode,mJoint.mNode,maintainOffset = False)
                        #Connect inversed aim and up
                        NodeF.connectNegativeAttrs(self.ml_fkJoints[i].mNode, mJoint.mNode,
                                                   ["r%s"%self._go._jointOrientation[0],"r%s"%self._go._jointOrientation[1]]).go()
                        cgmMeta.cgmAttr(self.ml_fkJoints[i].mNode,"r%s"%self._go._jointOrientation[2]).doConnectOut("%s.r%s"%(mJoint.mNode,self._go._jointOrientation[2]))
                else:
                    ml_fkUse = self.ml_fkJoints

                rUtils.connectBlendChainByConstraint(ml_fkUse,self.ml_ikJoints,self.ml_blendJoints,
                                                     driver = self.mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])
            except Exception,error: raise Exception,"Connect joint chains | %s "%error



            #>>> Settings - constrain
            mc.parentConstraint(self.ml_blendJoints[0].mNode, self.mi_settings.masterGroup.mNode, maintainOffset = True)

            #>>> Setup a vis blend result
            self.mPlug_FKon = cgmMeta.cgmAttr(self.mi_settings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	
            self.mPlug_IKon = cgmMeta.cgmAttr(self.mi_settings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=True)	

            NodeF.createSingleBlendNetwork(self.mPlug_FKIK.p_combinedName,
                                           self.mPlug_IKon.p_combinedName,
                                           self.mPlug_FKon.p_combinedName)

            self.mPlug_FKon.doConnectOut("%s.visibility"%self._go._i_constrainNull.controlsFK.mNode)
            self.mPlug_IKon.doConnectOut("%s.visibility"%self._go._i_constrainNull.controlsIK.mNode)	    

    return fncWrap(goInstance).go()

def build_deformation(self):
    ml_segmentHandleChains = self._get_segmentHandleChains()

    #Get our segment joints
    ml_segmentChains = self._get_segmentChains()
    if len(ml_segmentChains)>2:
        raise Exception, "Too many segment chains, not a regular leg."

    #>>>Influence Joints
    ml_influenceChains = self._get_influenceChains()
    if len(ml_influenceChains)!=len(ml_segmentChains):
        raise Exception, "Segment chains don't equal segment influence chains"

    #>>>Get data
    ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
    ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
    ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
    mi_settings = self._i_rigNull.settings

    mi_controlIK = self._i_rigNull.controlIK
    mi_controlMidIK = self._i_rigNull.midIK

    self.aimVector = cgmValid.simpleAxis("%s+"%self._jointOrientation[0]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    self.upVector = cgmValid.simpleAxis("%s+"%self._jointOrientation[1]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])	    

    ml_driversFK = ml_controlsFK
    if self._str_mirrorDirection == 'Right':
        ml_driversFK = self._i_rigNull.msgList_get('fkAttachJoints')	

    ml_controlsFK = ml_controlsFK   
    ml_rigJoints = ml_rigJoints
    ml_blendJoints = ml_blendJoints
    mi_settings = mi_settings

    mi_controlIK = mi_controlIK
    mi_controlMidIK = mi_controlMidIK

    aimVector = self.aimVector
    upVector = self.upVector	    
    ml_segmentHandleChains = ml_segmentHandleChains 
    ml_segmentChains = ml_segmentChains
    ml_influenceChains = ml_influenceChains

    #Main Attributes
    #==================================================================================== 
    #This is a bit of a complicated setup, pretty much we're gathering and splitting out potential drivers of the twist per segment
    str_twistOrientation = "r%s"%self._jointOrientation[0]   

    mPlug_Blend0 = cgmMeta.cgmAttr(ml_blendJoints[0],str_twistOrientation)
    mPlug_constraintNullRotate = cgmMeta.cgmAttr(self._i_constrainNull,str_twistOrientation)    
    mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
    mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)
    mPlug_worldIKEndOut = cgmMeta.cgmAttr(mi_settings,"out_worldIKEnd" , attrType='float' , lock = True) 

    mPlug_worldIKEndIn.doConnectOut(mPlug_worldIKEndOut.p_combinedShortName)

    try:#Control Segment
        #====================================================================================
        ml_segmentCurves = []
        ml_segmentReturns = []
        ml_segmentJointChainsReset = []

        log.debug(self._jointOrientation)
        capAim = self._jointOrientation[0].capitalize()
        log.debug("capAim: %s"%capAim)
        for i,ml_segmentHandles in enumerate(ml_segmentHandleChains):
            try:
                try:
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
                except Exception,error:
                    raise Exception,"[Initial Get | {0}]".format(error)
                
                #Create segment ========================================================================================
                curveSegmentReturn = SEGMENT.create(l_jointChain,
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

                i_curve = curveSegmentReturn['mSegmentCurve']
                i_curve.parent = self._i_rigNull.mNode
                i_curve.segmentGroup.parent = self._i_rigNull.mNode
                ml_segmentCurves.append(i_curve)

                midReturn = SEGMENT.add_subControl_toCurve(ml_influenceChains[i][1],
                                                           segmentCurve = i_curve,
                                                           baseParent = l_infuenceJoints[0],
                                                           endParent = l_infuenceJoints[-1],
                                                           midControls = ml_segmentHandles[1].mNode,
                                                           baseName = str_baseName,
                                                           orientation = self._jointOrientation,
                                                           controlTwistAxis =  'r'+self._jointOrientation[0],	                                               
                                                           moduleInstance=self._mi_module)

                for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
                    i_grp.parent = self._i_constrainNull.mNode

                #Parent our joint chains
                #i_curve.msgList_get('driverJoints',asMeta = True)[0].parent = ml_blendJoints[i].mNode#driver chain
                #ml_segmentChains[i][0].parent = ml_blendJoints[i].mNode#segment chain    
                for mHandle in i_curve.msgList_get('ikHandles',asMeta=True):
                    ml_chain = mHandle.msgList_get('drivenJoints',asMeta=True)
                    ml_chain[0].parent =  ml_blendJoints[i].mNode   
                    
                #>>> Attach stuff
                #==============================================================================================
                try:#We're gonna attach to the blend chain
                    mi_segmentAnchorStart = cgmMeta.validateObjArg(i_curve.anchorStart,'cgmObject')
                    mi_segmentAnchorEnd = cgmMeta.validateObjArg(i_curve.anchorEnd,'cgmObject')
                    mi_segmentAttachStart = cgmMeta.validateObjArg(i_curve.attachStart,'cgmObject')
                    mi_segmentAttachEnd = cgmMeta.validateObjArg(i_curve.attachEnd,'cgmObject') 
                    #mi_distanceBuffer = cgmMeta.validateObjArg(i_curve.scaleBuffer)

                    log.debug("mi_segmentAnchorStart: %s"%mi_segmentAnchorStart.mNode)
                    log.debug("mi_segmentAnchorEnd: %s"%mi_segmentAnchorEnd.mNode)
                    log.debug("mi_segmentAttachStart: %s"%mi_segmentAttachStart.mNode)
                    log.debug("mi_segmentAttachEnd: %s"%mi_segmentAttachEnd.mNode)
                    #log.debug("mi_distanceBuffer: %s"%mi_distanceBuffer.mNode)

                    #>>> parent the anchors to the deform null
                    mi_segmentAnchorStart.parent =  self._i_constrainNull.mNode
                    mi_segmentAnchorEnd.parent =  self._i_constrainNull.mNode	

                    #>>> parent handle anchors
                    mi_segmentAnchorStart.parent = ml_blendJoints[i].mNode
                    if i == 0:
                        #mi_segmentAnchorEnd.parent = self._i_rigNull.mainSegmentHandle.mNode
                        mi_segmentAnchorEnd.parent = ml_blendJoints[i].mNode		
                        mc.parentConstraint(self._i_rigNull.mainSegmentHandle.mNode,mi_segmentAnchorEnd.mNode)
                        #...was point before beta
                    else:
                        mi_segmentAnchorEnd.parent = ml_blendJoints[i+1].mNode	

                    #segment handles to influence parents
                    i_startControl.masterGroup.parent = ml_influenceChains[i][0].parent
                    i_endControl.masterGroup.parent = ml_influenceChains[i][-1].parent

                except Exception,error:
                    log.error("Failed to connect anchor: %s"%(mi_segmentAnchorStart))
                    raise Exception,error


                #Influence joint to segment handles		
                ml_influenceChains[i][0].parent = i_startControl.mNode
                ml_influenceChains[i][-1].parent = i_endControl.mNode

                #>>> Build fk and ik drivers

                #fk result = fk1 + fk2 + fk3 + -fk4
                #ik result = ik.y + knee twist?
                #Need sums, multiply by the fk/ikon

                try:#>>>Attrs
                    #>>> Setup a vis blend result
                    mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon')	
                    mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon')	                    
                    mPlug_TwistStartResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStart'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistEndResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEnd'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
    
                    mPlug_TwistStartFKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStartFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistEndFKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEndFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistStartFKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistStartFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistEndFKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistEndFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
    
                    mPlug_TwistStartIKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStartIK'%str_segCount ,hidden=True, attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistEndIKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEndIK'%str_segCount ,hidden=True, attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistStartIKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistStartIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                    mPlug_TwistEndIKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistEndIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)

                    #start twist driver
                    l_startDrivers = ["%s.%s"%(i_startControl.getShortName(),str_twistOrientation)]
                    l_startDrivers.append("%s"%mPlug_TwistStartFKResult.p_combinedShortName )
                    l_startDrivers.append("%s"%mPlug_TwistStartIKResult.p_combinedShortName )	    
                    l_fkStartDrivers = []
                    l_ikStartDrivers = []
    
                    #end twist driver
                    l_endDrivers = ["%s.%s"%(i_endControl.getShortName(),str_twistOrientation)]	    
                    l_endDrivers.append("%s"%mPlug_TwistEndFKResult.p_combinedShortName )
                    l_endDrivers.append("%s"%mPlug_TwistEndIKResult.p_combinedShortName )		    
                    l_fkEndDrivers = []
                    l_ikEndDrivers = []
    
                    l_fkEndDrivers.append("%s.%s"%(ml_driversFK[i+1].getShortName(),str_twistOrientation))    
                except Exception,error:
                    raise Exception,["Get Plugs | error: {0}".format(error)]
            
                try:
                    if i == 0:#if seg 0
                        l_ikStartDrivers.append(mPlug_worldIKStartIn.p_combinedShortName)
                        l_fkStartDrivers.append(mPlug_worldIKStartIn.p_combinedShortName)
                        str_mainHandleTwist = "%s.%s"%(self._i_rigNull.mainSegmentHandle.getShortName(),str_twistOrientation)
                        l_ikEndDrivers.append(str_mainHandleTwist)
                        l_fkEndDrivers.append(str_mainHandleTwist)
                    if i == 1:#if seg 1	
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
                except Exception,error:
                    raise Exception,["Wire | error: {0}".format(error)]
                
                try:#>>> Attributes 
                    #================================================================================================================
                    #Connect master scale
                    cgmMeta.cgmAttr(i_curve,'masterScale',lock=True).doConnectIn("%s.%s"%(self._i_masterControl.mNode,'scaleY'))    	    
    
                    #Push squash and stretch multipliers to head
                    l_keys = i_curve.getSequentialAttrDict('midFactor').keys()
                    for ii,k in enumerate(l_keys):
                        a = 'midFactor_{0}'.format(ii)
                        a1 = 'midFactor_{0}_{1}'.format(i,ii)
                        ATTR.copy_to(i_curve.mNode,a,mi_settings.mNode,a1,driven='source')
                        ATTR.set_keyable(mi_settings.mNode,a1,False)
                        if ii == 1:
                            ATTR.set(mi_settings.mNode,a1,1)    
                    
                    ATTR.copy_to(i_curve.mNode,'segmentScaleMult',mi_settings.mNode,'squashStretch_{0}'.format(i),driven='source')
                    ATTR.set_keyable(mi_settings.mNode,'squashStretch_{0}'.format(i),False)   
                    #Segement scale 
                    #cgmMeta.cgmAttr(i_buffer,'segmentScaleMult').doCopyTo(mi_settings.mNode,"segmentScaleMult_%s"%i,connectSourceToTarget=True)	    
    
                    #Other attributes transfer
                    #cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(i_midControl.mNode,connectSourceToTarget=True)
                    #cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(i_midControl.mNode,connectSourceToTarget=True)
                except Exception,error:
                    raise Exception,["Attributes fail | error: {0}".format(error)]
            except Exception,error:
                raise Exception,["Segment {0} |  {1}".format(i,error)] 
        self._i_rigNull.msgList_connect('segmentCurves',
                                        ml_segmentCurves,"rigNull")            
    except Exception,error:
        raise Exception,["Control Segment | error: {0}".format(error)]            



def build_deformation2(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_deformation(%s)'%self._go._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Verify','call':self.verify},
                                {'step':'Build Segments','call':self.build_segments}]
            #=================================================================

        def verify(self):      
            self.ml_segmentHandleChains = self._go._get_segmentHandleChains()

            #Get our segment joints
            self.ml_segmentChains = self._go._get_segmentChains()
            if len(self.ml_segmentChains)>2:
                raise Exception, "Too many segment chains, not a regular leg."

            #>>>Influence Joints
            self.ml_influenceChains = self._go._get_influenceChains()
            if len(self.ml_influenceChains)!=len(self.ml_segmentChains):
                raise Exception, "Segment chains don't equal segment influence chains"

            #>>>Get data
            self.ml_controlsFK =  self._go._i_rigNull.msgList_get('controlsFK')    
            self.ml_rigJoints = self._go._i_rigNull.msgList_get('rigJoints')
            self.ml_blendJoints = self._go._i_rigNull.msgList_get('blendJoints')
            self.mi_settings = self._go._i_rigNull.settings

            self.mi_controlIK = self._go._i_rigNull.controlIK
            self.mi_controlMidIK = self._go._i_rigNull.midIK

            self.aimVector = cgmValid.simpleAxis("%s+"%self._go._jointOrientation[0]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[0])
            self.upVector = cgmValid.simpleAxis("%s+"%self._go._jointOrientation[1]).p_vector#dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[1])	    

            self.ml_driversFK = self.ml_controlsFK
            if self._go._str_mirrorDirection == 'Right':
                self.ml_driversFK = self._go._i_rigNull.msgList_get('fkAttachJoints')	

        def build_segments(self):
            ml_controlsFK = self.ml_controlsFK   
            ml_rigJoints = self.ml_rigJoints
            ml_blendJoints = self.ml_blendJoints
            mi_settings = self.mi_settings

            mi_controlIK = self.mi_controlIK
            mi_controlMidIK = self.mi_controlMidIK

            aimVector = self.aimVector
            upVector = self.upVector	    
            ml_segmentHandleChains = self.ml_segmentHandleChains 
            ml_segmentChains = self.ml_segmentChains
            ml_influenceChains = self.ml_influenceChains

            #Main Attributes
            #==================================================================================== 
            #This is a bit of a complicated setup, pretty much we're gathering and splitting out potential drivers of the twist per segment
            str_twistOrientation = "r%s"%self._go._jointOrientation[0]   

            mPlug_Blend0 = cgmMeta.cgmAttr(ml_blendJoints[0],str_twistOrientation)
            mPlug_constraintNullRotate = cgmMeta.cgmAttr(self._go._i_constrainNull,str_twistOrientation)    
            mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
            mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)
            mPlug_worldIKEndOut = cgmMeta.cgmAttr(mi_settings,"out_worldIKEnd" , attrType='float' , lock = True) 

            mPlug_worldIKEndIn.doConnectOut(mPlug_worldIKEndOut.p_combinedShortName)

            try:#Control Segment
                #====================================================================================
                ml_segmentCurves = []
                ml_segmentReturns = []
                ml_segmentJointChainsReset = []
    
                log.debug(self._go._jointOrientation)
                capAim = self._go._jointOrientation[0].capitalize()
                log.debug("capAim: %s"%capAim)
                for i,ml_segmentHandles in enumerate(ml_segmentHandleChains):
                    try:
                        try:
                            i_startControl = ml_segmentHandles[0]
                            i_midControl = ml_segmentHandles[1]
                            i_endControl = ml_segmentHandles[-1]
                            l_jointChain = [i_jnt.mNode for i_jnt in ml_segmentChains[i]]
                            l_infuenceJoints = [ml_influenceChains[i][0].getShortName(),ml_influenceChains[i][-1].getShortName()]
                            log.info("startControl: %s"%i_startControl.getShortName())
                            log.info("endControl: %s"%i_endControl.getShortName())
                            log.info("jointChain: %s"%l_jointChain)
                            log.info("influenceJoints: %s"%l_infuenceJoints)
                            str_baseName = self._go._partName+"_seg%s"%i
                            str_segCount = "seg%s"%i
                        except Exception,error:
                            raise Exception,"[Initial Get | {0}]".format(error)
                        
                        #Create segment ========================================================================================
                        curveSegmentReturn = rUtils.createCGMSegment(l_jointChain,
                                                                     addSquashStretch=True,
                                                                     addTwist=True,
                                                                     influenceJoints=[l_infuenceJoints[0],l_infuenceJoints[-1]],
                                                                     startControl= i_startControl,
                                                                     endControl= i_endControl,
                                                                     orientation=self._go._jointOrientation,
                                                                     additiveScaleSetup=True,
                                                                     connectAdditiveScale=True,                                                 
                                                                     baseName = str_baseName,
                                                                     moduleInstance=self._go._mi_module)
        
                        ml_segmentReturns.append(curveSegmentReturn)
        
                        i_curve = curveSegmentReturn['mi_segmentCurve']
                        i_curve.parent = self._go._i_rigNull.mNode
                        i_curve.segmentGroup.parent = self._go._i_rigNull.mNode
                        ml_segmentCurves.append(i_curve)
        
                        midReturn = rUtils.addCGMSegmentSubControl(ml_influenceChains[i][1],
                                                                   segmentCurve = i_curve,
                                                                   baseParent = l_infuenceJoints[0],
                                                                   endParent = l_infuenceJoints[-1],
                                                                   midControls = ml_segmentHandles[1].mNode,
                                                                   baseName = str_baseName,
                                                                   orientation = self._go._jointOrientation,
                                                                   controlTwistAxis =  'r'+self._go._jointOrientation[0],	                                               
                                                                   moduleInstance=self._go._mi_module)
        
                        for i_grp in midReturn['ml_followGroups']:#parent our follow Groups
                            i_grp.parent = self._go._i_constrainNull.mNode
        
                        #Parent our joint chains
                        i_curve.msgList_get('driverJoints',asMeta = True)[0].parent = ml_blendJoints[i].mNode#driver chain
                        ml_segmentChains[i][0].parent = ml_blendJoints[i].mNode#segment chain    
        
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
                            mi_segmentAnchorStart.parent =  self._go._i_constrainNull.mNode
                            mi_segmentAnchorEnd.parent =  self._go._i_constrainNull.mNode	
        
                            #>>> parent handle anchors
                            mi_segmentAnchorStart.parent = ml_blendJoints[i].mNode
                            if i == 0:
                                #mi_segmentAnchorEnd.parent = self._go._i_rigNull.mainSegmentHandle.mNode
                                mi_segmentAnchorEnd.parent = ml_blendJoints[i].mNode		
                                mc.parentConstraint(self._go._i_rigNull.mainSegmentHandle.mNode,mi_segmentAnchorEnd.mNode)
                                #...was point before beta
                            else:
                                mi_segmentAnchorEnd.parent = ml_blendJoints[i+1].mNode	
        
                            #segment handles to influence parents
                            i_startControl.masterGroup.parent = ml_influenceChains[i][0].parent
                            i_endControl.masterGroup.parent = ml_influenceChains[i][-1].parent
        
                        except Exception,error:
                            log.error("Failed to connect anchor: %s"%(mi_segmentAnchorStart))
                            raise Exception,error
        
        
                        #Influence joint to segment handles		
                        ml_influenceChains[i][0].parent = i_startControl.mNode
                        ml_influenceChains[i][-1].parent = i_endControl.mNode
        
                        #>>> Build fk and ik drivers
        
                        #fk result = fk1 + fk2 + fk3 + -fk4
                        #ik result = ik.y + knee twist?
                        #Need sums, multiply by the fk/ikon
        
                        try:#>>>Attrs
                            #>>> Setup a vis blend result
                            mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon')	
                            mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon')	                    
                            mPlug_TwistStartResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStart'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                            mPlug_TwistEndResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEnd'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
            
                            mPlug_TwistStartFKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStartFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                            mPlug_TwistEndFKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEndFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                            mPlug_TwistStartFKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistStartFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                            mPlug_TwistEndFKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistEndFK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
            
                            mPlug_TwistStartIKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistStartIK'%str_segCount ,hidden=True, attrType='float' , defaultValue = 1 , lock = True)
                            mPlug_TwistEndIKResult = cgmMeta.cgmAttr(mi_settings,'result_%s_twistEndIK'%str_segCount ,hidden=True, attrType='float' , defaultValue = 1 , lock = True)
                            mPlug_TwistStartIKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistStartIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
                            mPlug_TwistEndIKSum = cgmMeta.cgmAttr(mi_settings,'sum_%s_twistEndIK'%str_segCount , attrType='float' , defaultValue = 1 , lock = True)
        
                            #start twist driver
                            l_startDrivers = ["%s.%s"%(i_startControl.getShortName(),str_twistOrientation)]
                            l_startDrivers.append("%s"%mPlug_TwistStartFKResult.p_combinedShortName )
                            l_startDrivers.append("%s"%mPlug_TwistStartIKResult.p_combinedShortName )	    
                            l_fkStartDrivers = []
                            l_ikStartDrivers = []
            
                            #end twist driver
                            l_endDrivers = ["%s.%s"%(i_endControl.getShortName(),str_twistOrientation)]	    
                            l_endDrivers.append("%s"%mPlug_TwistEndFKResult.p_combinedShortName )
                            l_endDrivers.append("%s"%mPlug_TwistEndIKResult.p_combinedShortName )		    
                            l_fkEndDrivers = []
                            l_ikEndDrivers = []
            
                            l_fkEndDrivers.append("%s.%s"%(self.ml_driversFK[i+1].getShortName(),str_twistOrientation))    
                        except Exception,error:
                            raise Exception,["Get Plugs | error: {0}".format(error)]
                    
                        try:
                            if i == 0:#if seg 0
                                l_ikStartDrivers.append(mPlug_worldIKStartIn.p_combinedShortName)
                                l_fkStartDrivers.append(mPlug_worldIKStartIn.p_combinedShortName)
                                str_mainHandleTwist = "%s.%s"%(self._go._i_rigNull.mainSegmentHandle.getShortName(),str_twistOrientation)
                                l_ikEndDrivers.append(str_mainHandleTwist)
                                l_fkEndDrivers.append(str_mainHandleTwist)
                            if i == 1:#if seg 1	
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
                        except Exception,error:
                            raise Exception,["Wire | error: {0}".format(error)]
                        
                        try:#>>> Attributes 
                            #================================================================================================================
                            #Connect master scale
                            cgmMeta.cgmAttr(i_curve.scaleBuffer,'masterScale',lock=True).doConnectIn("%s.%s"%(self._go._i_masterControl.mNode,'scaleY'))    	    
            
                            #Push squash and stretch multipliers to head
                            i_buffer = i_curve.scaleBuffer	    
                            for ii,k in enumerate(i_buffer.d_indexToAttr.keys()):
                                attrName = "seg_%s_%s_mult"%(i,ii)
                                cgmMeta.cgmAttr(i_buffer.mNode,'scaleMult_%s'%k).doCopyTo(mi_settings.mNode,attrName,connectSourceToTarget = True)
                                cgmMeta.cgmAttr(mi_settings.mNode,attrName,defaultValue = 1,keyable=True)
            
                            #Segement scale 
                            cgmMeta.cgmAttr(i_buffer,'segmentScaleMult').doCopyTo(mi_settings.mNode,"segmentScaleMult_%s"%i,connectSourceToTarget=True)	    
            
                            #Other attributes transfer
                            cgmMeta.cgmAttr(i_curve,'twistType').doCopyTo(i_midControl.mNode,connectSourceToTarget=True)
                            cgmMeta.cgmAttr(i_curve,'twistExtendToEnd').doCopyTo(i_midControl.mNode,connectSourceToTarget=True)
                        except Exception,error:
                            raise Exception,["Attributes fail | error: {0}".format(error)]
                    except Exception,error:
                        raise Exception,["Segment {0} |  {1}".format(i,error)]                    
            except Exception,error:
                raise Exception,["Control Segment | error: {0}".format(error)]            
    return fncWrap(goInstance).go()




def build_rig(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_rig(%s)'%self._go._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Verify','call':self.verify},
                                {'step':'Constrain to parent','call':self.build_parentConnect},
                                {'step':'dynParent Groups','call':self.build_dynParentGroups},
                                {'step':'Rig Structure','call':self.build_rigStructure},
                                {'step':'Lock N Hide','call':self.build_lockNHide},
                                {'step':'Finalize','call':self.build_finalize}]
            #=================================================================

        def verify(self):      
            self.orientation = self._go._jointOrientation or modules.returnSettingsData('jointOrientation')
            self.mi_moduleParent = False
            if self._go._mi_module.getMessage('moduleParent'):
                self.mi_moduleParent = self._go._mi_module.moduleParent

            self.mi_controlIK = self._go._i_rigNull.controlIK
            self.mi_controlMidIK = self._go._i_rigNull.midIK 
            self.ml_controlsFK =  self._go._i_rigNull.msgList_get('controlsFK')    
            self.ml_rigJoints = self._go._i_rigNull.msgList_get('rigJoints')
            self.ml_blendJoints = self._go._i_rigNull.msgList_get('blendJoints')
            self.mi_settings = self._go._i_rigNull.settings

            self.mi_controlIK = self._go._i_rigNull.controlIK
            self.mi_controlMidIK = self._go._i_rigNull.midIK

            log.info("mi_controlIK: %s"%self.mi_controlIK.getShortName())
            log.info("mi_controlMidIK: %s"%self.mi_controlMidIK.getShortName())	
            log.info("ml_controlsFK: %s"%[o.getShortName() for o in self.ml_controlsFK])
            log.info("mi_settings: %s"%self.mi_settings.getShortName())

            log.info("ml_rigJoints: %s"%[o.getShortName() for o in self.ml_rigJoints])
            log.info("ml_blendJoints: %s"%[o.getShortName() for o in self.ml_blendJoints])

            self.ml_rigHandleJoints = self._go._get_handleJoints()
            self.ml_segmentHandleChains = self._go._get_segmentHandleChains()
            self.ml_segmentChains = self._go._get_segmentChains()
            self.ml_influenceChains = self._go._get_influenceChains()	

            self.aimVector = dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[0])
            self.upVector = dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[1]) 

            self.d_indexRigJointToDriver = self._go._get_simpleRigJointDriverDict()	

        def build_parentConnect(self):
            #Constrain Parent
            #====================================================================================    
            if self.mi_moduleParent:
                #With the clav, it only has one skin joint
                mc.parentConstraint(self.mi_moduleParent.rigNull.msgList_get('moduleJoints')[0].mNode,self._go._i_constrainNull.mNode,maintainOffset = True)

        def build_dynParentGroups(self):
            #Dynamic parent groups
            #====================================================================================
            try:#>>>> Hand
                ml_handDynParents = []
                #Build our dynamic groups
                mi_spine = self._go._mi_module.modulePuppet.getModuleFromDict(moduleType= ['torso','spine'])
                log.info("spine found: %s"%mi_spine)
                if mi_spine:
                    mi_spineRigNull = mi_spine.rigNull
                    ml_handDynParents.append( mi_spineRigNull.handleIK )	    
                    ml_handDynParents.append( mi_spineRigNull.cog )
                    ml_handDynParents.append( mi_spineRigNull.hips )	

                if self.mi_moduleParent:
                    mi_parentRigNull = self.mi_moduleParent.rigNull
                    ml_buffer = mi_parentRigNull.msgList_get('moduleJoints')
                    if ml_buffer:
                        ml_handDynParents.append( ml_buffer[0])	    

                #ml_handDynParents.append(self._go._i_masterControl)
                ml_handDynParents.append(self._go._i_puppet.masterNull.puppetSpaceObjectsGroup)   
                ml_handDynParents.append(self._go._i_puppet.masterNull.worldSpaceObjectsGroup)                   
                if self.mi_controlIK.getMessage('spacePivots'):
                    ml_handDynParents.extend(self.mi_controlIK.msgList_get('spacePivots',asMeta = True))	
                log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._go._strShortName,[i_obj.getShortName() for i_obj in ml_handDynParents]))

                #Add our parents
                i_dynGroup = self.mi_controlIK.dynParentGroup
                log.info("Dyn group at setup: %s"%i_dynGroup)
                i_dynGroup.dynMode = 0

                for o in ml_handDynParents:
                    i_dynGroup.addDynParent(o)
                i_dynGroup.rebuild()

            except Exception,error:
                raise Exception,"hand ik dynamic parent setup fail | %s "%error

            #====================================================================================
            try:#>>>> elbow
                #Build our dynamic groups
                ml_elbowDynParents = []

                if mi_spine:
                    ml_elbowDynParents.append( mi_spineRigNull.handleIK )	    
                    ml_elbowDynParents.append( mi_spineRigNull.cog )
                    ml_elbowDynParents.append( mi_spineRigNull.hips )	

                if self.mi_moduleParent:
                    mi_parentRigNull = self.mi_moduleParent.rigNull
                    ml_buffer = mi_parentRigNull.msgList_get('moduleJoints')
                    if ml_buffer:
                        ml_elbowDynParents.append(ml_buffer[0])

                ml_elbowDynParents.insert(1,self.mi_controlIK)
                #ml_elbowDynParents.append(self._go._i_masterControl)
                ml_elbowDynParents.append(self._go._i_puppet.masterNull.puppetSpaceObjectsGroup)   
                ml_elbowDynParents.append(self._go._i_puppet.masterNull.worldSpaceObjectsGroup)   
                if self.mi_controlIK.getMessage('spacePivots'):
                    ml_elbowDynParents.extend(self.mi_controlIK.msgList_get('spacePivots',asMeta = True))

                log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._go._strShortName,[i_obj.getShortName() for i_obj in ml_elbowDynParents]))

                #Add our parents
                i_dynGroup = self.mi_controlMidIK.dynParentGroup
                log.info("Dyn group at setup: %s"%i_dynGroup)
                i_dynGroup.dynMode = 0

                for o in ml_elbowDynParents:
                    i_dynGroup.addDynParent(o)
                i_dynGroup.rebuild()

                #i_dynGroup.dynFollow.parent = self._go._i_masterDeformGroup.mNode
            except Exception,error:
                raise Exception,"elbow ik dynamic parent setup fail | %s "%error

            #====================================================================================
            try:#>>>> fk shoulder orient
                #Build our dynamic groups
                ml_shoulderDynParents = []

                if mi_spine:
                    ml_shoulderDynParents.append( mi_spineRigNull.handleIK )	    
                    ml_shoulderDynParents.append( mi_spineRigNull.cog )

                if self.mi_moduleParent:
                    mi_parentRigNull = self.mi_moduleParent.rigNull
                    ml_buffer = mi_parentRigNull.msgList_get('moduleJoints')
                    if ml_buffer:
                        if ml_shoulderDynParents:
                            ml_shoulderDynParents.insert(1,ml_buffer[-1])
                        else:
                            ml_shoulderDynParents.append(ml_buffer[-1])			    
                ml_shoulderDynParents.append(self._go._i_masterControl)

                log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._go._strShortName,[i_obj.getShortName() for i_obj in ml_shoulderDynParents]))

                #Add our parents
                i_dynGroup = (cgmMeta.cgmObject(self.ml_controlsFK[0].doGroup(True)))
                i_dynGroup = cgmRigMeta.cgmDynParentGroup(dynChild=self.ml_controlsFK[0],dynGroup=i_dynGroup)
                i_dynGroup.doName()

                log.info("Dyn group at setup: %s"%i_dynGroup)
                i_dynGroup.dynMode = 1

                for o in ml_shoulderDynParents:
                    i_dynGroup.addDynParent(o)
                i_dynGroup.rebuild()

                #i_dynGroup.dynFollow.parent = self._go._i_masterDeformGroup.mNode
            except Exception,error:
                raise Exception," fk shoulder | %s "%error

            #self._go.collect_worldDynDrivers()#...collect world dyn drivers

        def build_rigStructure(self):
            #Parent and constrain joints
            #====================================================================================
            orientation = self.orientation

            if self._go._str_mirrorDirection == 'Right':#We need to paren the attach joint to the parent of the fk root, usually the dynamic parent
                self._go._i_rigNull.msgList_get('fkAttachJoints')[0].parent = self.ml_controlsFK[0].parent		    

            self.ml_rigJoints[0].parent = self._go._i_deformNull.mNode#shoulder

            for i,i_jnt in enumerate(self.d_indexRigJointToDriver.keys()):
                #Don't try scale constraints in here, they're not viable
                attachJoint = self.d_indexRigJointToDriver[i_jnt].getShortName()
                log.info("'%s'>>drives>>'%s'"%(attachJoint,i_jnt.getShortName()))
                pntConstBuffer = mc.pointConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
                orConstBuffer = mc.orientConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
                if i_jnt.hasAttr('scaleJoint') and i_jnt.cgmName != 'wrist':
                    try:attributes.doConnectAttr((attachJoint+'.s'),(i_jnt.getMessage('scaleJoint')[0] +'.s'))
                    except:log.warning("Failed to connect: %s >> %s"%(attachJoint,i_jnt.getMessage('scaleJoint')[0]))
                else:
                    mc.connectAttr((attachJoint+'.s'),(i_jnt.mNode+'.s'))

            if self.ml_rigHandleJoints[-1].getMessage('scaleJoint'):#If our wrist has a scale joint, we need to connect it to our last joint of our last segment
                attributes.doConnectAttr((self.ml_segmentChains[-1][-1].mNode + '.s'),(self.ml_rigHandleJoints[-1].scaleJoint.mNode+'.s'))


            #Now we need to make an average for the extra elbow that averages the seg0,1 knees
            i_pma = cgmMeta.cgmNode(nodeType = 'plusMinusAverage')
            i_pma.operation = 3#average
            mc.connectAttr("%s.s"%self.ml_segmentChains[0][-1].mNode,"%s.%s"%(i_pma.mNode,'input3D[0]'))
            mc.connectAttr("%s.s"%self.ml_segmentChains[-1][0].mNode,"%s.%s"%(i_pma.mNode,'input3D[1]'))
            mc.connectAttr("%s.%s"%(i_pma.mNode,'output3D'),"%s.s"%(self.ml_rigHandleJoints[1].scaleJoint.mNode),force=True)



            #Setup hand Scaling
            #====================================================================================
            ml_fkJoints = self._go._i_rigNull.msgList_get('fkJoints')
            ml_ikJoints = self._go._i_rigNull.msgList_get('ikJoints')
            
            for mObj in ml_ikJoints[2:]:
                self.mi_controlIK.doConnectOut('scale', mObj.mNode + '.scale',)
            #for mObj in ml_fkJoints[2:]:
                #self.ml_controlsFK[-1].doConnectOut('scale',mObj.mNode + '.scale')
            """
            mPlug_ikHandScale = cgmMeta.cgmAttr(self.mi_controlIK,'s%s'%orientation[1])	    
            for attr in [self.orientation[0],self.orientation[2]]:
                #Ik Scale Object
                for mObj in ml_ikJoints[2:]:
                    mPlug_ikHandScale.doConnectOut("{0}.s{1}".format(mObj.mNode,attr))
                
                #mPlug_ikHandScale.doConnectOut("%s.s%s"%(self.mi_controlIK.mNode,attr))
                #attributes.doSetLockHideKeyableAttr(self.mi_controlIK.mNode,lock=True,visible=False,keyable=False,channels=['s%s'%attr])   
                mPlug = cgmMeta.cgmAttr(self.mi_controlIK,"s{0}".format(attr))
                mPlug_ikHandScale.doConnectOut(mPlug.p_combinedShortName)
                mPlug.p_hidden = True
                mPlug.p_locked = True		
            mPlug_ikHandScale.p_nameAlias = 'ikScale'
            mPlug_ikHandScale.p_keyable = True

            #FK Scale
            mPlug_fkHandScale = cgmMeta.cgmAttr(self.ml_controlsFK[-1],'s%s'%self.orientation[1])
            
            self.ml_controlsFK[-1].segmentScaleCompensate = 0#Fix cycle error
            
            for attr in [self.orientation[0],self.orientation[2]]:
                mPlug = cgmMeta.cgmAttr(self.ml_controlsFK[-1],"s%s"%attr)
                mPlug_fkHandScale.doConnectOut(mPlug.p_combinedShortName)
                mPlug.p_hidden = True
                mPlug.p_locked = True

            mPlug_fkHandScale.p_nameAlias = 'fkScale'
            mPlug_fkHandScale.p_keyable = True
            mPlug_fkHandScale.p_locked = False"""
            
            

            mPlug_FKIK = cgmMeta.cgmAttr(self.mi_settings.mNode,'blend_FKIK')
            rUtils.connectBlendJointChain(ml_fkJoints[-1],ml_ikJoints[2:],self.ml_blendJoints[2:],
                                          driver = mPlug_FKIK.p_combinedName,channels=['scale'])    


            try:#Set up some defaults
                #====================================================================================
                mPlug_autoStretch = cgmMeta.cgmAttr(self.mi_controlIK,'autoStretch')
                mPlug_autoStretch.p_defaultValue = 1.0
                mPlug_autoStretch.value =  1

                mPlug_seg0end = cgmMeta.cgmAttr(self.ml_segmentHandleChains[0][-1],'followRoot')
                mPlug_seg0end.p_defaultValue = 0
                mPlug_seg0end.value = 0

                mPlug_seg1end = cgmMeta.cgmAttr(self.ml_segmentHandleChains[1][-1],'followRoot')
                mPlug_seg1end.p_defaultValue = 0
                mPlug_seg1end.value = 0	

                #mid segment handles
                mPlug_seg0mid = cgmMeta.cgmAttr(self.ml_segmentHandleChains[0][1],'twistExtendToEnd')
                mPlug_seg0mid.p_defaultValue = 1
                mPlug_seg0mid.value = 1	

                mPlug_seg1mid = cgmMeta.cgmAttr(self.ml_segmentHandleChains[1][1],'twistExtendToEnd')
                mPlug_seg1mid.p_defaultValue = 0
                mPlug_seg1mid.value = 0		

            except Exception,error:
                raise Exception,"failed to setup defaults | %s"%(error)	     

        def build_lockNHide(self):
            #Vis Network, lock and hide
            #====================================================================================
            #Segment handles need to lock
            attributes.doSetLockHideKeyableAttr(self.mi_settings.mNode,lock=True, visible=False, keyable=False)

            for i_jnt in self.ml_blendJoints:
                attributes.doSetLockHideKeyableAttr(i_jnt.mNode,lock=True, visible=True, keyable=False)
                i_jnt.radius = 0#This is how we can hide joints without hiding them since we have children we want to ride along
                i_jnt.drawStyle = 2
                                
            #Set group lockks
            for mCtrl in self._go._i_rigNull.msgList_get('controlsAll'):
                mCtrl._setControlGroupLocks()	
                                   
            for mCtrl in self.ml_controlsFK:
                cgmMeta.cgmAttr(mCtrl,"translate",lock=True,hidden=True,keyable=False)  
                if mCtrl != self.ml_controlsFK[-1]:
                    cgmMeta.cgmAttr(mCtrl,"scale",lock=True,hidden=True,keyable=False)
                cgmMeta.cgmAttr(mCtrl,"v",lock=True,hidden=True,keyable=False)  	                
                mCtrl.radius = 0

            #Aim Scale locking on segment handles
            for mChain in self.ml_segmentHandleChains:
                for mCtrl in mChain:
                    cgmMeta.cgmAttr(mCtrl,"s%s"%self.orientation[0],lock=True,hidden=True,keyable=False)  
                    cgmMeta.cgmAttr(mCtrl,"v",lock=True,hidden=True,keyable=False)  	                


        def build_finalize(self):
            #Final stuff
            self._go._set_versionToCurrent()

    return fncWrap(goInstance).go()


#------------------------------------------------------------------------------------------------------------#    
def build_twistDriver_shoulder(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_twistDriver_shoulder(%s)'%self._go._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Verify','call':self.verify}]
            #=================================================================

        def verify(self):      
            try:
                mi_settings = self._go._i_rigNull.settings	
                mPlug_worldIKStartIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKStart" , attrType='float' , lock = True)
            except Exception,error:
                raise Exception,"failed to setup start attr | %s"%error	
            try:
                mi_parentRigNull = self._go._mi_module.moduleParent.rigNull
                i_target = mi_parentRigNull.msgList_get('moduleJoints')[0]	
            except Exception,error:
                raise Exception,"failed to find target | %s"%(error)	

            try:
                outVector = self._go._vectorOut
                upVector = self._go._vectorUp      
                ml_blendJoints = self._go._i_rigNull.msgList_get('blendJoints')
                ml_handleJoints = self._go._mi_module.rig_getHandleJoints()
                mi_mainSegmentHandle = self._go._i_rigNull.mainSegmentHandle
                fl_baseDist = DIST.get_distance_between_points(ml_blendJoints[0].p_position, ml_blendJoints[-1].p_position)

                #Create joints -------------------------------------------------------------------
                i_startRoot = ml_handleJoints[0].doDuplicate(inputConnections = False)
                i_startRoot.addAttr('cgmName',self._go._partName)	
                i_startRoot.addAttr('cgmTypeModifier','twistDriver')
                i_startRoot.doName()
                i_startRoot.parent = self._go._i_constrainNull.mNode

                i_startEnd = ml_handleJoints[0].doDuplicate(inputConnections = False)
                i_startEnd.addAttr('cgmTypeModifier','twistDriverEnd')
                i_startEnd.doName() 
                i_startEnd.parent = i_startRoot.mNode

                i_driver = ml_handleJoints[0].doDuplicate(inputConnections = False)
                i_driver.addAttr('cgmName',self._go._partName)	
                i_driver.addAttr('cgmTypeModifier','twistDriverResult')
                i_driver.doName()
                i_driver.parent = ml_blendJoints[0]#parent to the root blend to get it in the same space

                #Loc -------------------------------------------------------------------
                i_upLoc = i_startRoot.doLoc()	
                i_upLoc.parent = self._go._i_constrainNull.mNode#parent
                self._go.connect_toRigGutsVis(i_upLoc)

                ml_twistObjects = [i_startRoot,i_startEnd,i_upLoc,i_driver]
                #i_upLoc.__setattr__('t%s'%self._go._jointOrientation[1],fl_baseDist)	
                ATTR.set(i_upLoc.mNode,'t%s'%self._go._jointOrientation[1],fl_baseDist)
                #Move aim joint out
                #i_startEnd.__setattr__('t%s'%self._go._jointOrientation[0],fl_baseDist)
                ATTR.set(i_startEnd.mNode,'t%s'%self._go._jointOrientation[0],fl_baseDist)

            except Exception,error:
                raise Exception,"Failed joint creation,positioning | %s"%(error)	    

            #=============================================================================
            try:#setup stable shoulder rotate group  
                i_rotGroup = self._go._i_constrainNull.doCreateAt()
                i_rotGroup.addAttr('cgmType','stableShoulderTwistRotGroup')
                i_rotGroup.doName()
                ml_twistObjects.append(i_rotGroup)
                i_upLoc.parent = i_rotGroup.mNode

                i_rotGroup.parent = self._go._i_constrainNull.mNode
                mc.parentConstraint(i_target.mNode,i_upLoc.mNode,maintainOffset = True)

            except Exception,error:
                raise Exception,"failed to create stable rotate group: %s"%(error)

            #=============================================================================
            #Create IK handle
            try:
                pos = i_startRoot.getPosition()
                mc.move (0,pos[1],pos[2], i_startRoot.mNode, ws = True)#zero out aim joint's x pos

                buffer = mc.ikHandle( sj=i_startRoot.mNode, ee=i_startEnd.mNode,
                                      solver = 'ikRPsolver', forceSolver = True,
                                      snapHandleFlagToggle=True )  

                #>>> Name
                str_baseName = self._go._partName + "_startTwistDriver"
                i_ik_handle = cgmMeta.cgmObject(buffer[0],setClass=True)
                i_ik_handle.addAttr('cgmName',str_baseName ,attrType='string',lock=True)    
                i_ik_handle.doName()
                i_ik_handle.parent = self._go._i_rigNull.mNode
                mc.pointConstraint(mi_mainSegmentHandle.mNode,i_ik_handle.mNode,maintainOffset = False)

                ml_twistObjects.append(i_ik_handle)

                i_ik_effector = cgmMeta.asMeta(buffer[1],'cgmNode',setClass=True)
                i_ik_effector.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
                i_ik_effector.doName()

                cBuffer = mc.poleVectorConstraint(i_upLoc.mNode,i_ik_handle.mNode)#Polevector	
                rUtils.IKHandle_fixTwist(i_ik_handle.mNode)#Fix the wist

            except:
                raise Exception,"failed to create ik handle: %s"%(error)

            #>>> Control	
            try:
                #>>> Connect in
                mc.orientConstraint(i_startRoot.mNode,i_driver.mNode,maintainOffset = True, skip = [self._go._jointOrientation[1],self._go._jointOrientation[2]])
                cgmMeta.cgmAttr(self._go._mi_module.rigNull.settings,'in_worldIKStart').doConnectIn("%s.r%s"%(i_driver.mNode,self._go._jointOrientation[0]))
                self._go.connect_toRigGutsVis(ml_twistObjects)#connect to guts vis switches
            except Exception,error:
                raise Exception,"finish failed| %s"%(error)
            return True
    return fncWrap(goInstance).go()


#------------------------------------------------------------------------------------------------------------#    
def build_twistDriver_wrist(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_twistDriver_wrist(%s)'%self._go._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Verify','call':self.verify}]
            #=================================================================

        def verify(self):      
            try:
                mi_controlIK = self._go._i_rigNull.controlIK	
                mi_settings = self._go._i_rigNull.settings	
                mPlug_worldIKEndIn = cgmMeta.cgmAttr(mi_settings,"in_worldIKEnd" , attrType='float' , lock = True)
            except Exception,error:
                raise Exception,"failed to setup start attr | %s"%(error)	

            try:
                outVector = self._go._vectorOut
                upVector = self._go._vectorUp      
                ml_blendJoints = self._go._i_rigNull.msgList_get('blendJoints')
                ml_ikJoints = self._go._i_rigNull.msgList_get('ikJoints')	
                fl_baseDist = DIST.get_distance_between_points(ml_blendJoints[0].p_position, ml_blendJoints[-1].p_position)

                ml_rigHandleJoints = self._go._get_handleJoints()	
                i_targetJoint = ml_rigHandleJoints[2]#This should be the wrist
                i_blendWrist = ml_blendJoints[2]
                if i_targetJoint.cgmName != 'wrist':
                    raise Exception,"target not wrist? | %s"%(i_targetJoint.p_nameShort)	
                if i_blendWrist.cgmName != 'wrist':
                    raise Exception,"blend target not wrist? | %s"%(i_blendWrist.p_nameShort)	

                #Create joints
                i_startRoot = i_targetJoint.doDuplicate(inputConnections = False)
                i_startRoot.addAttr('cgmName',self._go._partName)	
                i_startRoot.addAttr('cgmTypeModifier','endtwistDriver')
                i_startRoot.doName()
                i_startEnd = i_targetJoint.doDuplicate(inputConnections = False)
                i_startEnd.addAttr('cgmTypeModifier','endtwistDriverEnd')
                i_startEnd.doName()    

                i_upLoc = i_startRoot.doLoc()	
                i_upLoc.parent = self._go._i_constrainNull.mNode#parent

                #Restore out lists

                i_startEnd.parent = i_startRoot.mNode
                ml_twistObjects = [i_startRoot,i_startEnd,i_upLoc]
                
                if self._go._direction == 'left':#if right, rotate the pivots
                    #i_upLoc.__setattr__('t%s'%self._go._jointOrientation[2],fl_baseDist)
                    ATTR.set(i_upLoc.mNode,'t%s'%self._go._jointOrientation[2],fl_baseDist)
                    
                else:
                    #i_upLoc.__setattr__('t%s'%self._go._jointOrientation[2],-fl_baseDist)
                    ATTR.set(i_upLoc.mNode,'t%s'%self._go._jointOrientation[2],-fl_baseDist)
                    

                #i_startEnd.__setattr__('t%s'%self._go._jointOrientation[0],-(fl_baseDist))
                ATTR.set(i_startEnd.mNode,'t%s'%self._go._jointOrientation[0],-fl_baseDist)

                i_startRoot.parent = ml_ikJoints[1].mNode
                i_startRoot.rotateOrder = 0 #xyz
                mc.pointConstraint(i_blendWrist.mNode,i_startRoot.mNode,mo=True)#constrain

            except Exception,error:
                raise Exception,"Failed joint creation,positioning | %s"%(error)	    

            #=============================================================================
            try:#setup stable wrist rotate group  
                i_rotGroup = mi_controlIK.doCreateAt()
                i_rotGroup.addAttr('cgmType','stableShoulderTwistRotGroup')
                i_rotGroup.doName()
                ml_twistObjects.append(i_rotGroup)
                i_upLoc.parent = i_rotGroup.mNode

                """
		NodeF.argsToNodes("%s.ry = -%s.ry"%(i_rotGroup.p_nameShort,
						    mi_controlIK.p_nameShort)).doBuild()	
		NodeF.argsToNodes("%s.rx = -%s.rx"%(i_rotGroup.p_nameShort,
						    mi_controlIK.p_nameShort)).doBuild()	"""
                i_rotGroup.parent = i_blendWrist.mNode
                mc.orientConstraint(mi_controlIK.mNode,i_rotGroup.mNode,skip = ["%s"%r for r in self._go._jointOrientation[1:]])
            except Exception,error:
                raise Exception,"failed to create stable rotate group: %s"%(error)

            #=============================================================================
            #Create IK handle
            try:
                buffer = mc.ikHandle( sj=i_startRoot.mNode, ee=i_startEnd.mNode,
                                      solver = 'ikRPsolver', forceSolver = True,
                                      snapHandleFlagToggle=True )  

                #>>> Name
                str_baseName = self._go._partName + "_endTwistDriver"
                i_ik_handle = cgmMeta.asMeta(buffer[0],'cgmObject',setClass=True)
                i_ik_handle.addAttr('cgmName',str_baseName ,attrType='string',lock=True)    
                i_ik_handle.doName()
                i_ik_handle.parent = self._go._i_rigNull.mNode
                mc.pointConstraint(ml_blendJoints[1].mNode,i_ik_handle.mNode)

                ml_twistObjects.append(i_ik_handle)

                i_ik_effector = cgmMeta.asMeta(buffer[1],'cgmNode',setClass=True)
                i_ik_effector.addAttr('cgmName',str_baseName,attrType='string',lock=True)    
                i_ik_effector.doName()

                cBuffer = mc.poleVectorConstraint(i_upLoc.mNode,i_ik_handle.mNode)#Polevector	
                rUtils.IKHandle_fixTwist(i_ik_handle.mNode)#Fix the wist

            except:
                raise Exception,"failed to create ik handle: %s"%(error)

            #>>> Control	
            try:
                #>>> Connect in
                cgmMeta.cgmAttr(self._go._mi_module.rigNull.settings,'in_worldIKEnd').doConnectIn("%s.r%s"%(i_startRoot.mNode,self._go._jointOrientation[0]))
                self._go.connect_toRigGutsVis(ml_twistObjects)#connect to guts vis switches
            except Exception,error:
                raise Exception,"finish failed| %s"%(error)
            return True	    
    return fncWrap(goInstance).go()



def build_matchSystem(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_matchSystem(%s)'%self._go._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Verify','call':self.verify}]
            #=================================================================

        def verify(self):      
            #Base info
            mi_moduleParent = False
            if self._go._mi_module.getMessage('moduleParent'):
                mi_moduleParent = self._go._mi_module.moduleParent

            mi_controlIK = self._go._i_rigNull.controlIK
            mi_controlMidIK = self._go._i_rigNull.midIK 
            ml_controlsFK =  self._go._i_rigNull.msgList_get('controlsFK')    
            ml_rigJoints = self._go._i_rigNull.msgList_get('rigJoints')
            ml_blendJoints = self._go._i_rigNull.msgList_get('blendJoints')
            mi_settings = self._go._i_rigNull.settings

            mi_controlIK = self._go._i_rigNull.controlIK
            mi_controlMidIK = self._go._i_rigNull.midIK  

            ml_fkJoints = self._go._i_rigNull.msgList_get('fkJoints')
            ml_ikJoints = self._go._i_rigNull.msgList_get('ikJoints')

            mi_dynSwitch = self._go._i_dynSwitch

            try:#>>> First IK to FK
                i_ikHandMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlIK,
                                                           dynPrefix = "FKtoIK",
                                                           dynMatchTargets=ml_blendJoints[-1])	    
    
                i_ikHandMatch.addDynIterTarget(drivenObject =ml_ikJoints[1],#elbow
                                               matchObject = ml_blendJoints[1],
                                               drivenAttr= 't%s'%self._go._jointOrientation[0],
                                               matchAttr = 't%s'%self._go._jointOrientation[0],
                                               minValue=0.001,
                                               maxValue=30,
                                               maxIter=15,
                                               driverAttr='lengthUpr')    
                i_ikHandMatch.addDynIterTarget(drivenObject =ml_ikJoints[2],#wrist
                                               matchObject= ml_blendJoints[2],#Make a new one
                                               drivenAttr='t%s'%self._go._jointOrientation[0],
                                               matchAttr = 't%s'%self._go._jointOrientation[0],
                                               minValue=0.001,
                                               maxValue=30,
                                               maxIter=15,
                                               driverAttr='lengthLwr')  
            except Exception,error:raise Exception,"ik to fk fail! | {0}".format(error)
            
            try:#>> Hand
                i_ikMidMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlMidIK,
                                                          dynPrefix = "FKtoIK",
                                                          dynMatchTargets=ml_blendJoints[1])
            except Exception,error:raise Exception,"hand fail! | {0}".format(error)


            try:#>>> FK to IK
                #============================================================================
                i_fkShoulderMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[0],
                                                               dynPrefix = "IKtoFK",
                                                               dynMatchTargets=ml_blendJoints[0])
                i_fkShoulderMatch.addDynIterTarget(drivenObject =ml_fkJoints[1],
                                                   matchObject = ml_blendJoints[1],
                                                   drivenAttr='t%s'%self._go._jointOrientation[0],
                                                   matchAttr = 't%s'%self._go._jointOrientation[0],
                                                   minValue=0.001,
                                                   maxValue=30,
                                                   maxIter=15,
                                                   driverAttr='length')  
    
                i_fkElbowMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[1],
                                                            dynPrefix = "IKtoFK",
                                                            dynMatchTargets=ml_blendJoints[1])
                i_fkElbowMatch.addDynIterTarget(drivenObject =ml_fkJoints[2],
                                                matchObject = ml_blendJoints[2],                                   
                                                drivenAttr='t%s'%self._go._jointOrientation[0],
                                                matchAttr = 't%s'%self._go._jointOrientation[0],
                                                minValue=0.001,
                                                maxValue=30,
                                                maxIter=15,
                                                driverAttr='length')  
    
                i_fkWristMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[2],
                                                            dynPrefix = "IKtoFK",
                                                            dynMatchTargets=ml_blendJoints[2])
            except Exception,error:raise Exception,"fk to ik fail! | {0}".format(error)
                
            """
	    i_fkBallMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[3],
						      dynPrefix = "IKtoFK",
						      dynMatchTargets=ml_blendJoints[3])   

	    i_fkWristMatch.addDynAttrMatchTarget(dynObjectAttr='fkScale',
						 matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._go._jointOrientation[0]],
						 )   
						 """
            try:#>>> Register the switches
                mi_dynSwitch.addSwitch('snapToFK',[mi_settings.mNode,'blend_FKIK'],
                                       0,
                                       [i_fkShoulderMatch,i_fkElbowMatch,i_fkWristMatch])
    
                mi_dynSwitch.addSwitch('snapToIK',[mi_settings.mNode,'blend_FKIK'],
                                       1,
                                       [i_ikHandMatch,i_ikMidMatch])
            except Exception,error:raise Exception,"Register switches! | {0}".format(error)

            return True
    return fncWrap(goInstance).go()


#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'fkik','function':build_FKIK},
                    4:{'name':'deformation','function':build_deformation},
                    5:{'name':'rig','function':build_rig},
                    6:{'name':'match','function':build_matchSystem},
                    7:{'name':'shoulderDriver','function':build_twistDriver_shoulder},
                    8:{'name':'wristDriver','function':build_twistDriver_wrist},                    
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------