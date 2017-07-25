"""
------------------------------------------
cgm.core.rigger: Limb.finger
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

Finger rig builder
================================================================
"""
__version__ = 0.06242013

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
from cgm.core.rigger.lib import module_Utils as modUtils
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as cgmRigMeta
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import NodeFactory as NodeF
reload(NodeF)

from cgm.core.rigger import ModuleShapeCaster as mShapeCast
from cgm.core.rigger import ModuleControlFactory as mControlFactory
from cgm.core.lib import nameTools
from cgm.core.rigger.lib import rig_Utils as rUtils
from cgm.core.rigger.lib import joint_Utils as jUtils
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
__l_jointAttrs__ = ['rigJoints','fkJoints','ikJoints','blendJoints']   
__d_preferredAngles__ = {'thumb':[0,0,10]}#In terms of aim up out for orientation relative values
__d_controlShapes__ = {'shape':['segmentFK','settings','cap']}

def __bindSkeletonSetup__(self,addHelpers = True):
    """
    TODO: Do I need to connect per joint overrides or will the final group setup get them?
    """
    #log.info(">>> %s.__bindSkeletonSetup__ >> "%self._strShortName + "="*75)    
    return
    try:
        if not self._cgmClass == 'JointFactory.go':
            log.error("Not a JointFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("f.__bindSkeletonSetup__>>bad self!")
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

        if addHelpers:
            ml_pairs = lists.parseListToPairs(ml_moduleJoints)
            #jUtils.add_defHelpJoint(ml_pairs[0][0],ml_pairs[0][1],helperType = 'childRootHold',orientation=self.str_jointOrientation)
            for ml_pair in ml_pairs[1:]:
                jUtils.add_defHelpJoint(ml_pair[0],ml_pair[1],helperType = 'childRootHold',orientation=self.str_jointOrientation)

        #ml_moduleJoints = self._mi_module.rigNull.msgList_get('moduleJoints')
        #self._i_rigNull.msgList_connect(ml_moduleJoints,'skinJoints','module')	
        #self._mi_module.rig_getReport()#report

    except Exception,error:
        log.error("build_thumb>>__bindSkeletonSetup__ fail!")
        raise Exception,error   

def build_rigSkeleton(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_rigSkeleton(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Build Chains','call':self.build}]	
            #=================================================================

        def build(self):#================================================================================   	
            #>>>Create joint chains
            #=============================================================    
            try:
                #>>Rig chain  
                #=====================================================================	
                l_rigJoints = mc.duplicate(self._go._l_skinJoints,po=True,ic=True,rc=True)
                ml_rigJoints = []
                for i,j in enumerate(l_rigJoints):
                    i_j = cgmMeta.cgmObject(j)
                    i_j.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
                    i_j.doName()
                    l_rigJoints[i] = i_j.mNode
                    ml_rigJoints.append(i_j)
                ml_rigJoints[0].parent = False#Parent to deformGroup

                self._go._i_rigNull.msgList_connect('rigJoints',ml_rigJoints,"rigNull")
            except Exception,error:
                log.error("build_rigSkeleton>>Build rig joints fail!")
                raise Exception,error   

            try:#>>FK chain
                #=====================================================================		
                ml_fkJoints = []
                for i,i_ctrl in enumerate(self._go._i_templateNull.msgList_get('controlObjects')):
                    if not i_ctrl.getMessage('handleJoint'):
                        raise Exception,"%s.build_rigSkeleton>>> failed to find a handle joint from: '%s'"%(self._go._mi_module.getShortName(),i_ctrl.getShortName())
                    i_new = cgmMeta.cgmObject(mc.duplicate(i_ctrl.getMessage('handleJoint')[0],po=True,ic=True)[0])
                    i_new.addAttr('cgmTypeModifier','fk',attrType='string',lock=True)
                    i_new.doName()
                    if ml_fkJoints:#if we have data, parent to last
                        i_new.parent = ml_fkJoints[-1]
                    else:i_new.parent = False
                    i_new.rotateOrder = self._go._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations
                    ml_fkJoints.append(i_new)	
            except Exception,error:
                log.error("build_rigSkeleton>>Build fk joints fail!")
                raise Exception,error   

            #==================================================================

            try:#>>Blend chain
                #=====================================================================
                ml_blendJoints = []
                for i_jnt in ml_fkJoints:
                    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
                    i_new.addAttr('cgmTypeModifier','blend',attrType='string',lock=True)
                    i_new.doName()
                    if ml_blendJoints:#if we have data, parent to last
                        i_new.parent = ml_blendJoints[-1]
                    ml_blendJoints.append(i_new)	
            except Exception,error:
                log.error("build_rigSkeleton>>Build blend joints fail!")
                raise Exception,error  

            try:#>>IK chain
                #=====================================================================	
                """Important - we're going to set our preferred angles on the main ik joints so ik works as expected"""
                ml_ikJoints = []
                for i_jnt in ml_fkJoints:
                    i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
                    i_new.addAttr('cgmTypeModifier','ik',attrType='string',lock=True)
                    i_new.doName()
                    if self._go._partType in __d_preferredAngles__.keys():
                        log.info("preferred angles(%s)>>> %s"%(self._go._partType ,__d_preferredAngles__.get(self._go._partType)))
                        for i,v in enumerate(__d_preferredAngles__.get(self._go._partType )):	  
                            i_new.__setattr__('preferredAngle%s'%self._go._jointOrientation[i].upper(),v)
                    if ml_ikJoints:#if we have data, parent to last
                        i_new.parent = ml_ikJoints[-1]
                    ml_ikJoints.append(i_new)	
            except Exception,error:
                log.error("build_rigSkeleton>>Build ik joints fail!")
                raise Exception,error  

            try:#mirror stuff
                if self._go._str_mirrorDirection == 'Right':#mirror control setup
                    self._go.mirrorChainOrientation(ml_fkJoints)#New 

                    ml_fkDriverJoints = self._go.build_handleChain('fkAttach','fkAttachJoints')
                    for i,mJoint in enumerate(ml_fkJoints):
                        log.info("Mirror connect: %s | %s"%(i,mJoint.p_nameShort))
                        mJoint.connectChildNode(ml_fkDriverJoints[i],"attachJoint","rootJoint")
                        cgmMeta.cgmAttr(mJoint.mNode,"rotateOrder").doConnectOut("%s.rotateOrder"%ml_fkDriverJoints[i].mNode)
            except Exception,error: raise Exception,"Failed to create mirror chain | %s"%error


            try:#>>> Store em all to our instance
                #=====================================================================	
                self._go._i_rigNull.msgList_connect('skinJoints',self._go._l_skinJoints,"rigNull")#push back to reset

                self._go._i_rigNull.msgList_connect('fkJoints',ml_fkJoints,"rigNull")
                self._go._i_rigNull.msgList_connect('blendJoints',ml_blendJoints,"rigNull")
                self._go._i_rigNull.msgList_connect('ikJoints',ml_ikJoints,"rigNull")

            except Exception,error:
                log.error("build_finger>>StoreJoints fail!")
                raise Exception,error   

            try:#>>> Connect vis
                #=====================================================================	
                ml_jointsToConnect = []
                ml_jointsToConnect.extend(ml_rigJoints)    
                ml_jointsToConnect.extend(ml_ikJoints)

                self._go.connect_toRigGutsVis(ml_jointsToConnect,vis = True)#connect to guts vis switches
                self._go.connect_toRigGutsVis(ml_blendJoints,vis = False)#connect to guts vis switches

            except Exception,error:
                log.error("build_finger>>Connect to guts fail!")
                raise Exception,error   
    return fncWrap(goInstance).go()

def build_rigSkeleton2(self):

    """
    """
    try:#===================================================
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("thumb.build_deformationRig>>bad self!")
        raise Exception,error

    #>>>Create joint chains
    #=============================================================    
    try:
        #>>Rig chain  
        #=====================================================================	
        l_rigJoints = mc.duplicate(self._l_skinJoints,po=True,ic=True,rc=True)
        ml_rigJoints = []
        for i,j in enumerate(l_rigJoints):
            i_j = cgmMeta.cgmObject(j)
            i_j.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
            i_j.doName()
            l_rigJoints[i] = i_j.mNode
            ml_rigJoints.append(i_j)
        ml_rigJoints[0].parent = False#Parent to deformGroup

        self._i_rigNull.msgList_connect('rigJoints',ml_rigJoints,"rigNull")
    except Exception,error:
        log.error("build_rigSkeleton>>Build rig joints fail!")
        raise Exception,error   

    try:#>>FK chain
        #=====================================================================		
        ml_fkJoints = []
        for i,i_ctrl in enumerate(self._i_templateNull.msgList_get('controlObjects')):
            if not i_ctrl.getMessage('handleJoint'):
                raise Exception,"%s.build_rigSkeleton>>> failed to find a handle joint from: '%s'"%(self._mi_module.getShortName(),i_ctrl.getShortName())
            i_new = cgmMeta.cgmObject(mc.duplicate(i_ctrl.getMessage('handleJoint')[0],po=True,ic=True)[0])
            i_new.addAttr('cgmTypeModifier','fk',attrType='string',lock=True)
            i_new.doName()
            if ml_fkJoints:#if we have data, parent to last
                i_new.parent = ml_fkJoints[-1]
            else:i_new.parent = False
            i_new.rotateOrder = self._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations
            ml_fkJoints.append(i_new)	
    except Exception,error:
        log.error("build_rigSkeleton>>Build fk joints fail!")
        raise Exception,error   

    #==================================================================
    """
    #Finger - aim out up
    try:#>>>Rotate Orders
	for i_obj in ml_fkJoints:
	    i_obj.rotateOrder = 2   		

    except Exception,error:
	log.error("%s.build_controls>>> Rotate orders fail!"%self._strShortName)		
	raise Exception,error
    """
    try:#>>Blend chain
        #=====================================================================
        ml_blendJoints = []
        for i_jnt in ml_fkJoints:
            i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
            i_new.addAttr('cgmTypeModifier','blend',attrType='string',lock=True)
            i_new.doName()
            if ml_blendJoints:#if we have data, parent to last
                i_new.parent = ml_blendJoints[-1]
            ml_blendJoints.append(i_new)	
    except Exception,error:
        log.error("build_rigSkeleton>>Build blend joints fail!")
        raise Exception,error  

    try:#>>IK chain
        #=====================================================================	
        """Important - we're going to set our preferred angles on the main ik joints so ik works as expected"""
        ml_ikJoints = []
        for i_jnt in ml_fkJoints:
            i_new = cgmMeta.cgmObject(mc.duplicate(i_jnt.mNode,po=True,ic=True)[0])
            i_new.addAttr('cgmTypeModifier','ik',attrType='string',lock=True)
            i_new.doName()
            if self._partType in __d_preferredAngles__.keys():
                log.info("preferred angles(%s)>>> %s"%(self._partType ,__d_preferredAngles__.get(self._partType)))
                for i,v in enumerate(__d_preferredAngles__.get(self._partType )):	  
                    i_new.__setattr__('preferredAngle%s'%self._jointOrientation[i].upper(),v)
            if ml_ikJoints:#if we have data, parent to last
                i_new.parent = ml_ikJoints[-1]
            ml_ikJoints.append(i_new)	
    except Exception,error:
        log.error("build_rigSkeleton>>Build ik joints fail!")
        raise Exception,error   

    try:#>>> Store em all to our instance
        #=====================================================================	
        self._i_rigNull.msgList_connect('skinJoints',self._l_skinJoints,"rigNull")#push back to reset

        self._i_rigNull.msgList_connect('fkJoints',ml_fkJoints,"rigNull")
        self._i_rigNull.msgList_connect('blendJoints',ml_blendJoints,"rigNull")
        self._i_rigNull.msgList_connect('ikJoints',ml_ikJoints,"rigNull")

    except Exception,error:
        log.error("build_finger>>StoreJoints fail!")
        raise Exception,error   

    try:#>>> Connect vis
        #=====================================================================	
        ml_jointsToConnect = []
        ml_jointsToConnect.extend(ml_rigJoints)    
        ml_jointsToConnect.extend(ml_ikJoints)

        self.connect_toRigGutsVis(ml_jointsToConnect,vis = True)#connect to guts vis switches
        self.connect_toRigGutsVis(ml_blendJoints,vis = False)#connect to guts vis switches

    except Exception,error:
        log.error("build_finger>>Connect to guts fail!")
        raise Exception,error   

#>>> Shapes
#===================================================================
def build_shapes(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_shapes(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Build NOT BROKEN UP YET','call':self.build}]	
            #=================================================================

        def build(self):#================================================================================   	

            if self._go._i_templateNull.handles not in range(4,6):
                raise Exception, "%s.build_shapes>>> Too many handles. don't know how to rig"%(self._go._strShortName)

            if not self._go.isRigSkeletonized():
                raise Exception, "%s.build_shapes>>> Must be rig skeletonized to shape"%(self._go._strShortName)	

            #>>> Get our segment influence joints
            #=============================================================    
            l_influenceChains = []
            ml_influenceChains = []
            for i in range(50):
                buffer = self._go._i_rigNull.msgList_getMessage('segment%s_InfluenceJoints'%i)
                if buffer:
                    l_influenceChains.append(buffer)
                    ml_influenceChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
                else:
                    break    

            log.info("%s.build_shapes>>> Influence Chains -- cnt: %s | lists: %s"%(self._go._strShortName,len(l_influenceChains),l_influenceChains))

            #>>>Build our Shapes
            #=============================================================
            try:
                #Segment IK
                """
		ml_segmentIKShapes = []
		for i,ml_chain in enumerate(ml_influenceChains):
		    mShapeCast.go(self._go._mi_module,['segmentIK'],targetObjects = [i_jnt.mNode for i_jnt in ml_chain] , storageInstance=self)#This will store controls to a dict called    
		    log.info("%s.build_shapes>>> segmentIK chain %s: %s"%(self._go._strShortName,i,self._go._md_controlShapes))
		    ml_segmentIKShapes.extend(self._go._md_controlShapes['segmentIK'])

		    self._go._i_rigNull.msgList_connect(self._go._md_controlShapes['segmentIK'],'shape_segmentIK_%s'%i,"rigNull")		

		self._go._i_rigNull.msgList_connect(ml_segmentIKShapes,'shape_segmentIK',"rigNull")		
		"""
                #Rest of it
                l_toBuild = __d_controlShapes__['shape']
                mShapeCast.go(self._go._mi_module,l_toBuild, storageInstance=self._go)#This will store controls to a dict called    
                log.info(self._go._md_controlShapes)
                log.info(self._go._md_controlPivots)
                self._go._i_rigNull.msgList_connect('shape_controlsFK',
                                                    self._go._md_controlShapes['segmentFK'],
                                                    "rigNull")	
                self._go._i_rigNull.connectChildNode(self._go._md_controlShapes['settings'],'shape_settings',"rigNull")		
                self._go._i_rigNull.connectChildNode(self._go._md_controlShapes['moduleCap'],'shape_cap',"rigNull")

            except Exception,error:
                log.error("%s.build_shapes>>Build shapes fail!"%self._go._strShortName)
                raise Exception,error  
    return fncWrap(goInstance).go()

def build_shapes2(self):
    """
    """ 
    try:
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("thumb.build_rig>>bad self!")
        raise Exception,error

    if self._i_templateNull.handles not in range(4,6):
        raise Exception, "%s.build_shapes>>> Too many handles. don't know how to rig"%(self._strShortName)

    if not self.isRigSkeletonized():
        raise Exception, "%s.build_shapes>>> Must be rig skeletonized to shape"%(self._strShortName)	

    #>>> Get our segment influence joints
    #=============================================================    
    l_influenceChains = []
    ml_influenceChains = []
    for i in range(50):
        buffer = self._i_rigNull.msgList_getMessage('segment%s_InfluenceJoints'%i)
        if buffer:
            l_influenceChains.append(buffer)
            ml_influenceChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
        else:
            break    

    log.info("%s.build_shapes>>> Influence Chains -- cnt: %s | lists: %s"%(self._strShortName,len(l_influenceChains),l_influenceChains))

    #>>>Build our Shapes
    #=============================================================
    try:
        #Segment IK
        """
	ml_segmentIKShapes = []
	for i,ml_chain in enumerate(ml_influenceChains):
	    mShapeCast.go(self._mi_module,['segmentIK'],targetObjects = [i_jnt.mNode for i_jnt in ml_chain] , storageInstance=self)#This will store controls to a dict called    
	    log.info("%s.build_shapes>>> segmentIK chain %s: %s"%(self._strShortName,i,self._md_controlShapes))
	    ml_segmentIKShapes.extend(self._md_controlShapes['segmentIK'])

	    self._i_rigNull.msgList_connect(self._md_controlShapes['segmentIK'],'shape_segmentIK_%s'%i,"rigNull")		

	self._i_rigNull.msgList_connect(ml_segmentIKShapes,'shape_segmentIK',"rigNull")		
	"""
        #Rest of it
        l_toBuild = __d_controlShapes__['shape']
        mShapeCast.go(self._mi_module,l_toBuild, storageInstance=self)#This will store controls to a dict called    
        log.info(self._md_controlShapes)
        log.info(self._md_controlPivots)
        self._i_rigNull.msgList_connect('shape_controlsFK',
                                        self._md_controlShapes['segmentFK'],
                                        "rigNull")	
        self._i_rigNull.connectChildNode(self._md_controlShapes['settings'],'shape_settings',"rigNull")		
        self._i_rigNull.connectChildNode(self._md_controlShapes['moduleCap'],'shape_cap',"rigNull")

    except Exception,error:
        log.error("%s.build_shapes>>Build shapes fail!"%self._strShortName)
        raise Exception,error  

#>>> Controls
#===================================================================
def build_controls(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_controls(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Build NOT BROKEN UP YET','call':self.build_old},
                                {'step':'Connections','call':self.build_connections}]	
            #=================================================================

        def build_old(self):#================================================================================   	

            if not self._go.isShaped():
                raise Exception,"%s.build_controls>>> needs shapes to build controls"%self._go._strShortName
            if not self._go.isRigSkeletonized():
                raise Exception,"%s.build_controls>>> needs shapes to build controls"%self._go._strShortName
            """
	    __d_controlShapes__ = {'shape':['controlsFK','midIK','settings','hand'],
			     'pivot':['toe','heel','ball','inner','outer
	    for shape in __d_controlShapes__['shape']:
		self._go.__dict__['mi_%s'%shape] = cgmMeta.validateObjArg(self._go._i_rigNull.msgList_getMessage('shape_%s'%shape),noneValid=False)
		log.info(self._go.__dict__['mi_%s'%shape] )"""
            ml_controlsFK = cgmMeta.validateObjListArg(self._go._i_rigNull.msgList_getMessage('shape_controlsFK'),cgmMeta.cgmObject)
            ml_segmentIK = cgmMeta.validateObjListArg(self._go._i_rigNull.msgList_getMessage('shape_segmentIK'),cgmMeta.cgmObject)
            #self._go._i_rigNull.msgList_connect(self._go._md_controlShapes['segmentIK'],'shape_segmentIK_%s'%i,"rigNull")		
            l_segmentIKChains = []
            ml_segmentIKChains = []
            for i in range(50):
                buffer = self._go._i_rigNull.msgList_getMessage('shape_segmentIK_%s'%i)
                if buffer:
                    l_segmentIKChains.append(buffer)
                    ml_segmentIKChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
                else:
                    break  

            #mi_midIK = cgmMeta.validateObjArg(self._go._i_rigNull.getMessage('shape_midIK'),cgmMeta.cgmObject)
            mi_settings= cgmMeta.validateObjArg(self._go._i_rigNull.getMessage('shape_settings'),cgmMeta.cgmObject)
            ml_fkJoints = cgmMeta.validateObjListArg(self._go._i_rigNull.msgList_getMessage('fkJoints'),cgmMeta.cgmObject)
            mi_cap = cgmMeta.validateObjArg(self._go._i_rigNull.getMessage('shape_moduleCap'),cgmMeta.cgmObject)

            log.info("mi_settings: '%s'"%mi_settings.getShortName())
            log.info("mi_cap: '%s'"%mi_cap.getShortName())    
            log.info("ml_fkJoints: %s"%[i_o.getShortName() for i_o in ml_fkJoints])

            #>>>Make a few extra groups for storing controls and what not to in the deform group
            for grp in ['controlsFK','controlsIK']:
                i_dup = self._go._i_constrainNull.doCreateAt(copyAttrs=True)
                i_dup.parent = self._go._i_constrainNull.mNode
                i_dup.addAttr('cgmTypeModifier',grp,lock=True)
                i_dup.doName()

                self._go._i_constrainNull.connectChildNode(i_dup,grp,'owner')

            l_controlsAll = []
            #==================================================================
            try:#>>>> FK Segments
                if len( ml_controlsFK )<3:
                    raise Exception,"%s.build_controls>>> Must have at least three fk controls"%self._go._strShortName	    

                #for i,i_obj in enumerate(ml_controlsFK[1:]):#parent
                    #i_obj.parent = ml_controlsFK[i].mNode
                ml_fkJoints[0].parent = self._go._i_constrainNull.controlsFK.mNode

                for i,i_obj in enumerate(ml_controlsFK):
                    d_buffer = mControlFactory.registerControl(i_obj,shapeParentTo=ml_fkJoints[i],setRotateOrder=3,
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

                #ml_controlsFK[0].masterGroup.parent = self._go._i_constrainNull.mNode
                self._go._i_rigNull.msgList_connect('controlsFK',ml_fkJoints,"rigNull")
                l_controlsAll.extend(ml_fkJoints[:-1])	

            except Exception,error:	
                log.error("%s.build_controls>>> Build fk fail!"%self._go._strShortName)
                raise Exception,error

            #==================================================================    
            try:#>>>> IK Handle
                i_IKEnd = mi_cap
                i_IKEnd.parent = False
                d_buffer = mControlFactory.registerControl(i_IKEnd,copyPivot=ml_fkJoints[-2].mNode,setRotateOrder=3,
                                                           mirrorSide=self._go._str_mirrorDirection, mirrorAxis="translateX,rotateY,rotateZ",	                                               		                                           
                                                           typeModifier='ik',addSpacePivots = 1, addDynParentGroup = True,
                                                           addConstraintGroup=True,
                                                           makeAimable = True)
                i_IKEnd = d_buffer['instance']	
                i_IKEnd.masterGroup.parent = self._go._i_constrainNull.controlsIK.mNode

                #i_loc.delete()#delete
                self._go._i_rigNull.connectChildNode(i_IKEnd,'controlIK',"rigNull")#connect
                l_controlsAll.append(i_IKEnd)	

                #Set aims
                i_IKEnd.axisAim = 'z+'
                i_IKEnd.axisUp= 'y+'

            except Exception,error:
                log.error("%s.build_controls>>> Build ik handle fail!"%self._go._strShortName)	
                raise Exception,error   

            try:#>>>> Settings
                d_buffer = mControlFactory.registerControl(mi_settings,addExtraGroups=0,typeModifier='settings',autoLockNHide=True,
                                                           mirrorSide=self._go._str_mirrorDirection, mirrorAxis="",	                                               		                                           
                                                           setRotateOrder=2)       
                i_obj = d_buffer['instance']
                i_obj.masterGroup.parent = self._go._i_constrainNull.mNode
                self._go._i_rigNull.connectChildNode(mi_settings,'settings',"rigNull")
                l_controlsAll.append(mi_settings)

                mi_settings.addAttr('blend_FKIK', defaultValue = 0, attrType = 'float', minValue = 0, maxValue = 1, keyable = False,hidden = False,lock=True)

                self.mPlug_result_moduleSubDriver = self._go.build_visSub()	

            except Exception,error:
                log.error("%s.build_controls>>> Build settings fail!"%self._go._strShortName)		
                raise Exception,error    


            #==================================================================    
            try:#>>>> Add all of our Attrs
                #Add driving attrs
                mPlug_length = cgmMeta.cgmAttr(i_IKEnd,'length',attrType='float',defaultValue = 1,minValue=0,keyable = True)		
                mPlug_fingerSpin = cgmMeta.cgmAttr(i_IKEnd,'fingerSpin',attrType='float',defaultValue = 0,keyable = True)
                mPlug_stretch = cgmMeta.cgmAttr(i_IKEnd,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
                mPlug_lengthUpr= cgmMeta.cgmAttr(i_IKEnd,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
                mPlug_lengthLwr = cgmMeta.cgmAttr(i_IKEnd,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)	

            except Exception,error:
                log.error("%s.build_controls>>> Add Control Attrs Fail!"%self._go._strShortName)	

            self.ml_controlsAll = l_controlsAll
            return True

        def build_connections(self):
            int_strt = self._go._i_puppet.get_nextMirrorIndex( self._go._str_mirrorDirection )
            for i,mCtrl in enumerate(self.ml_controlsAll):
                try:
                    mCtrl.addAttr('mirrorIndex', value = (int_strt + i))		
                except Exception,error: raise Exception,"Failed to register mirror index | mCtrl: %s | %s"%(mCtrl,error)

            try:self._go._i_rigNull.msgList_connect('controlsAll',self.ml_controlsAll,'rigNull')
            except Exception,error: raise Exception,"Controls all connect| %s"%error	    
            try:self._go._i_rigNull.moduleSet.extend(self.ml_controlsAll)
            except Exception,error: raise Exception,"Failed to set module objectSet | %s"%error

            return True

    return fncWrap(goInstance).go()

def build_controls2(self):
    """
    """    
    try:
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("%s.build_rig>>bad self!"%self._strShortName)
        raise Exception,error

    if not self.isShaped():
        raise Exception,"%s.build_controls>>> needs shapes to build controls"%self._strShortName
    if not self.isRigSkeletonized():
        raise Exception,"%s.build_controls>>> needs shapes to build controls"%self._strShortName
    """
    __d_controlShapes__ = {'shape':['controlsFK','midIK','settings','hand'],
	             'pivot':['toe','heel','ball','inner','outer
    for shape in __d_controlShapes__['shape']:
	self.__dict__['mi_%s'%shape] = cgmMeta.validateObjArg(self._i_rigNull.msgList_getMessage('shape_%s'%shape),noneValid=False)
	log.info(self.__dict__['mi_%s'%shape] )"""
    ml_controlsFK = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('shape_controlsFK'),cgmMeta.cgmObject)
    ml_segmentIK = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('shape_segmentIK'),cgmMeta.cgmObject)
    #self._i_rigNull.msgList_connect(self._md_controlShapes['segmentIK'],'shape_segmentIK_%s'%i,"rigNull")		
    l_segmentIKChains = []
    ml_segmentIKChains = []
    for i in range(50):
        buffer = self._i_rigNull.msgList_getMessage('shape_segmentIK_%s'%i)
        if buffer:
            l_segmentIKChains.append(buffer)
            ml_segmentIKChains.append(cgmMeta.validateObjListArg(buffer,cgmMeta.cgmObject))
        else:
            break  

    #mi_midIK = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_midIK'),cgmMeta.cgmObject)
    mi_settings= cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_settings'),cgmMeta.cgmObject)
    ml_fkJoints = cgmMeta.validateObjListArg(self._i_rigNull.msgList_getMessage('fkJoints'),cgmMeta.cgmObject)
    mi_cap = cgmMeta.validateObjArg(self._i_rigNull.getMessage('shape_moduleCap'),cgmMeta.cgmObject)

    log.info("mi_settings: '%s'"%mi_settings.getShortName())
    log.info("mi_cap: '%s'"%mi_cap.getShortName())    
    log.info("ml_fkJoints: %s"%[i_o.getShortName() for i_o in ml_fkJoints])

    #>>>Make a few extra groups for storing controls and what not to in the deform group
    for grp in ['controlsFK','controlsIK']:
        i_dup = self._i_constrainNull.doCreateAt(copyAttrs=True)
        i_dup.parent = self._i_constrainNull.mNode
        i_dup.addAttr('cgmTypeModifier',grp,lock=True)
        i_dup.doName()

        self._i_constrainNull.connectChildNode(i_dup,grp,'owner')

    l_controlsAll = []
    #==================================================================
    try:#>>>> FK Segments
        if len( ml_controlsFK )<3:
            raise Exception,"%s.build_controls>>> Must have at least three fk controls"%self._strShortName	    

        #for i,i_obj in enumerate(ml_controlsFK[1:]):#parent
            #i_obj.parent = ml_controlsFK[i].mNode
        ml_fkJoints[0].parent = self._i_constrainNull.controlsFK.mNode

        for i,i_obj in enumerate(ml_controlsFK):
            d_buffer = mControlFactory.registerControl(i_obj,shapeParentTo=ml_fkJoints[i],setRotateOrder=3,
                                                       makeAimable=True,typeModifier='fk',) 	    

            i_obj = d_buffer['instance']
            i_obj.axisAim = "%s+"%self._jointOrientation[0]
            i_obj.axisUp= "%s+"%self._jointOrientation[1]	
            i_obj.axisOut= "%s+"%self._jointOrientation[2]
            try:i_obj.drawStyle = 2#Stick joint draw style	    
            except:self.log_error("{0} Failed to set drawStyle".format(i_obj.p_nameShort))	    
            cgmMeta.cgmAttr(i_obj,'radius',hidden=True)

        for i_obj in ml_controlsFK:
            i_obj.delete()

        #ml_controlsFK[0].masterGroup.parent = self._i_constrainNull.mNode
        self._i_rigNull.msgList_connect('controlsFK',ml_fkJoints,"rigNull")
        l_controlsAll.extend(ml_fkJoints)	

    except Exception,error:	
        log.error("%s.build_controls>>> Build fk fail!"%self._strShortName)
        raise Exception,error

    #==================================================================    
    try:#>>>> IK Handle
        i_IKEnd = mi_cap
        i_IKEnd.parent = False
        d_buffer = mControlFactory.registerControl(i_IKEnd,copyPivot=ml_fkJoints[-1].mNode,setRotateOrder=3,
                                                   typeModifier='ik',addSpacePivots = 1, addDynParentGroup = True,
                                                   addConstraintGroup=True,
                                                   makeAimable = True)
        i_IKEnd = d_buffer['instance']	
        i_IKEnd.masterGroup.parent = self._i_constrainNull.controlsIK.mNode

        #i_loc.delete()#delete
        self._i_rigNull.connectChildNode(i_IKEnd,'controlIK',"rigNull")#connect
        l_controlsAll.append(i_IKEnd)	

        #Set aims
        i_IKEnd.axisAim = 'z+'
        i_IKEnd.axisUp= 'y+'

    except Exception,error:
        log.error("%s.build_controls>>> Build ik handle fail!"%self._strShortName)	
        raise Exception,error   

    #==================================================================  
    """
    try:#>>>> midIK Handle
	i_IKmid = mi_midIK
	i_IKmid.parent = False
	d_buffer = mControlFactory.registerControl(i_IKmid,addSpacePivots = 1,
	                                           typeModifier='ik',addDynParentGroup = True, addConstraintGroup=True,
	                                           makeAimable = False,setRotateOrder=4)
	i_IKmid = d_buffer['instance']	
	i_IKmid.masterGroup.parent = self._i_constrainNull.controlsIK.mNode
	i_IKmid.addAttr('scale',lock=True,hidden=True)
	#i_loc.delete()#delete
	self._i_rigNull.connectChildNode(i_IKmid,'midIK',"rigNull")#connect
	l_controlsAll.append(i_IKmid)	

    except Exception,error:
	log.error("%s.build_controls>>> Build ik handle fail!"%self._strShortName)	
	raise Exception,error   """

    #==================================================================
    try:#>>>> Settings
        d_buffer = mControlFactory.registerControl(mi_settings,addExtraGroups=0,typeModifier='settings',autoLockNHide=True,
                                                   setRotateOrder=2)       
        i_obj = d_buffer['instance']
        i_obj.masterGroup.parent = self._i_constrainNull.mNode
        self._i_rigNull.connectChildNode(mi_settings,'settings',"rigNull")
        l_controlsAll.append(mi_settings)

        mi_settings.addAttr('blend_FKIK', defaultValue = 0, attrType = 'float', minValue = 0, maxValue = 1, keyable = False,hidden = False,lock=True)

        #Vis network for stub
        #Add our attrs
        mPlug_moduleSubDriver = cgmMeta.cgmAttr(mi_settings,'visSub', value = 1, defaultValue = 1, attrType = 'bool', keyable = False,hidden = False)
        mPlug_result_moduleSubDriver = cgmMeta.cgmAttr(mi_settings,'visSub_out', defaultValue = 1, attrType = 'bool', keyable = False,hidden = True,lock=True)

        #Get one of the drivers
        if self._mi_module.getAttr('cgmDirection') and self._mi_module.cgmDirection.lower() in ['left','right']:
            str_mainSubDriver = "%s.%sSubControls_out"%(self._i_masterControl.controlVis.getShortName(),
                                                        self._mi_module.cgmDirection)
        else:
            str_mainSubDriver = "%s.subControls_out"%(self._i_masterControl.controlVis.getShortName())

        iVis = self._i_masterControl.controlVis
        visArg = [{'result':[mPlug_result_moduleSubDriver.obj.mNode,mPlug_result_moduleSubDriver.attr],
                   'drivers':[[iVis,"subControls_out"],[mi_settings,mPlug_moduleSubDriver.attr]]}]
        NodeF.build_mdNetwork(visArg)

    except Exception,error:
        log.error("%s.build_controls>>> Build settings fail!"%self._strShortName)		
        raise Exception,error    

    #==================================================================  
    """
    try:#>>>> IK Segments
	for i,chain in enumerate(ml_segmentIKChains):
	    ml_controlChain =[]
	    for i_obj in chain:
		d_buffer = mControlFactory.registerControl(i_obj,addExtraGroups=1,typeModifier='ik',
		                                           setRotateOrder=2)       
		i_obj = d_buffer['instance']
		i_obj.masterGroup.parent = self._i_constrainNull.mNode
		ml_controlChain.append(i_obj)

		mPlug_result_moduleSubDriver.doConnectOut("%s.visibility"%i_obj.mNode)
	    self._i_rigNull.msgList_connect(ml_controlChain,'segmentHandles_%s'%i,"rigNull")
	    l_controlsAll.extend(ml_controlChain)	
	    if i == 1:
		#Need to do a few special things for our main segment handle
		i_mainHandle = chain[0]
		self._i_rigNull.connectChildNode(i_mainHandle,'mainSegmentHandle',"rigNull")
		curves.setCurveColorByName(i_mainHandle.mNode,self._mi_module.getModuleColors()[0])    
		attributes.doBreakConnection(i_mainHandle.mNode,'visibility')

    except Exception,error:
	log.error("%s.build_controls>>> IK segments fail!"%self._strShortName)		
	raise Exception,error"""
    #==================================================================    
    try:#>>>> Add all of our Attrs
        #Add driving attrs
        mPlug_length = cgmMeta.cgmAttr(i_IKEnd,'length',attrType='float',defaultValue = 1,minValue=0,keyable = True)		
        mPlug_fingerSpin = cgmMeta.cgmAttr(i_IKEnd,'fingerSpin',attrType='float',defaultValue = 0,keyable = True)
        mPlug_stretch = cgmMeta.cgmAttr(i_IKEnd,'autoStretch',attrType='float',defaultValue = 1,keyable = True)
        #mPlug_showElbow = cgmMeta.cgmAttr(i_IKEnd,'showElbow',attrType='bool',defaultValue = 0,keyable = False)
        mPlug_lengthUpr= cgmMeta.cgmAttr(i_IKEnd,'lengthUpr',attrType='float',defaultValue = 1,minValue=0,keyable = True)
        mPlug_lengthLwr = cgmMeta.cgmAttr(i_IKEnd,'lengthLwr',attrType='float',defaultValue = 1,minValue=0,keyable = True)	
        #mPlug_lockMid = cgmMeta.cgmAttr(i_IKmid,'lockMid',attrType='float',defaultValue = 0,keyable = True,minValue=0,maxValue=1.0)

    except Exception,error:
        log.error("%s.build_controls>>> Add Control Attrs Fail!"%self._strShortName)	

    #Connect all controls
    self._i_rigNull.msgList_connect('controlsAll',l_controlsAll)

    return True

def build_FKIK(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_FKIK(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Build NOT BROKEN UP YET','call':self.build}]	
            #=================================================================

        def build(self):#================================================================================   	

            #>>>Get data
            ml_controlsFK =  self._go._i_rigNull.msgList_get('controlsFK')   
            ml_rigJoints = self._go._i_rigNull.msgList_get('rigJoints')
            ml_blendJoints = self._go._i_rigNull.msgList_get('blendJoints')
            ml_fkJoints = self._go._i_rigNull.msgList_get('fkJoints')
            ml_ikJoints = self._go._i_rigNull.msgList_get('ikJoints')

            mi_settings = self._go._i_rigNull.settings

            aimVector = dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[0])
            upVector = dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[1])
            outVector = dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[2])

            mi_controlIK = self._go._i_rigNull.controlIK

            for chain in [ml_ikJoints,ml_blendJoints]:
                chain[0].parent = self._go._i_constrainNull.mNode

            self.ml_fkAttachJoints = []
            if self._go._str_mirrorDirection == 'Right':#mirror control setup
                self.ml_fkAttachJoints = self._go._i_rigNull.msgList_get('fkAttachJoints')

            #for more stable ik, we're gonna lock off the lower channels degrees of freedom
            for chain in [ml_ikJoints]:
                for axis in self._go._jointOrientation[:2]:
                    log.info(axis)
                    for i_j in chain[1:]:
                        attributes.doSetAttr(i_j.mNode,"jointType%s"%axis.upper(),1)

            #=============================================================    
            try:#>>>Finger Root Control and root follow
                for attr in ['tx','ty','tz']:#Unlock a few things
                    i_attr = cgmMeta.cgmAttr(ml_fkJoints[0],attr)
                    i_attr.p_keyable = True
                    i_attr.p_locked = False	   	

                #we have to rebuild a little so that we can use our fk base control both for fk and ik
                #Create a orient group that tracks the  module constrain null
                if self._go._partType == 'finger':
                    buffer_fkGroup = ml_fkJoints[0].parent
                    i_orientGroup = cgmMeta.asMeta( ml_fkJoints[1].doGroup(True),'cgmObject',setClass=True )
                    i_orientGroup.addAttr('cgmTypeModifier','toOrient')
                    i_orientGroup.doName()

                    #constrain it 
                    str_orConst = mc.orientConstraint(self._go._i_constrainNull.mNode,i_orientGroup.mNode,maintainOffset = True)[0]
                    self._go._i_constrainNull.connectChildNode(i_orientGroup,'fingerRoot','owner')#Connect
                    i_orientGroup.parent = self._go._i_constrainNull.mNode

                    attributes.doSetLockHideKeyableAttr(i_orientGroup.mNode)#lockNHide

                    i_parentGroup = cgmMeta.asMeta( i_orientGroup.doGroup(True),'cgmObject',setClass=True )
                    i_parentGroup.addAttr('cgmTypeModifier','toParent')
                    i_parentGroup.doName()	
                    str_prntConst = mc.parentConstraint( ml_fkJoints[0].mNode,i_parentGroup.mNode,maintainOffset = True)[0]
                    i_parentGroup.parent = buffer_fkGroup

                    #attributes.doSetLockHideKeyableAttr(ml_fkJoints[0].mNode,lock = False, visible=True, keyable=True, channels=['tx','ty','tz'])

                    #Constrain ik base to fk base
                    mc.orientConstraint(ml_fkJoints[0].mNode,ml_ikJoints[0].mNode,maintainOffset = True)
                    ml_fkJoints[0].parent = self._go._i_constrainNull.mNode

            except Exception,error:
                raise Exception,"%s.build_FKIK>>> Finger Root Control error: %s"%(self._go._strShortName,error)

            #=============================================================    
            try:#>>>FK Length connector
                if self._go._partType == 'finger':
                    ml_fkToDo = ml_fkJoints[1:-1]
                else:#thumb
                    ml_fkToDo = ml_fkJoints[:-1]
                    log.info([i_jnt.getShortName() for i_jnt in ml_fkToDo])

                for i,i_jnt in enumerate(ml_fkToDo):
                    rUtils.addJointLengthAttr(i_jnt,orientation=self._go._jointOrientation)

                #IK
                rUtils.addJointLengthAttr(ml_ikJoints[-2],[mi_controlIK,'length'],orientation=self._go._jointOrientation)

            except Exception,error:
                raise Exception,"%s.build_FKIK>>> fk length connect error: %s"%(self._go._strShortName,error)

            #=============================================================  
            try:#>>>IK No Flip Chain
                mPlug_globalScale = cgmMeta.cgmAttr(self._go._i_masterControl.mNode,'scaleY')
                ml_ikNoFlipJoints = ml_ikJoints#Link
                i_tmpLoc = ml_ikNoFlipJoints[1].doLoc()#loc the first real 
                i_tmpLoc.parent = self._go._i_constrainNull.fingerRoot.mNode
                str_twistGroup = i_tmpLoc.doGroup(True)

                f_dist = distance.returnDistanceBetweenPoints(ml_ikNoFlipJoints[1].getPosition(),ml_ikNoFlipJoints[-1].getPosition()) #Measure first thumb joint to end
                f_dist = f_dist * 1.5
                if self._go._direction == 'left':#if right, rotate the pivots
                    i_tmpLoc.__setattr__('t%s'%self._go._jointOrientation[2],-f_dist)
                else:
                    i_tmpLoc.__setattr__('t%s'%self._go._jointOrientation[2],f_dist)

                #Create no flip thumb IK
                d_ankleNoFlipReturn = rUtils.IKHandle_create(ml_ikNoFlipJoints[1].mNode,ml_ikNoFlipJoints[-2].mNode,lockMid=False,
                                                             nameSuffix = 'noFlip',rpHandle=True,controlObject=mi_controlIK,addLengthMulti=True,
                                                             globalScaleAttr=mPlug_globalScale.p_combinedName, stretch='translate',moduleInstance=self._go._mi_module)

                mi_fingerIKHandleNF = d_ankleNoFlipReturn['mi_handle']
                ml_distHandlesNF = d_ankleNoFlipReturn['ml_distHandles']
                mi_rpHandleNF = d_ankleNoFlipReturn['mi_rpHandle']
                #mPlug_lockMid = d_ankleNoFlipReturn['mPlug_lockMid']

                #No Flip RP handle
                Snap.go(mi_rpHandleNF,i_tmpLoc.mNode,True)#Snape to hand control, then move it out...
                i_tmpLoc.delete()

                mi_rpHandleNF.doCopyNameTagsFromObject(self._go._mi_module.mNode, ignore = ['cgmName','cgmType'])
                mi_rpHandleNF.addAttr('cgmName','%sPoleVector'%self._go._partName, attrType = 'string')
                mi_rpHandleNF.addAttr('cgmTypeModifier','noFlip')
                mi_rpHandleNF.doName()

                #spin
                #=========================================================================================
                #Make a spin group
                i_spinGroup = cgmMeta.cgmObject(str_twistGroup)
                i_spinGroup.doCopyNameTagsFromObject(self._go._mi_module.mNode, ignore = ['cgmName','cgmType'])	
                i_spinGroup.addAttr('cgmName','%sNoFlipSpin'%self._go._partName)
                i_spinGroup.doName()

                i_spinGroup.doZeroGroup()
                mi_rpHandleNF.parent = i_spinGroup.mNode

                #Setup arg
                mPlug_fingerSpin = cgmMeta.cgmAttr(mi_controlIK,'fingerSpin')
                mPlug_fingerSpin.doConnectOut("%s.r%s"%(i_spinGroup.mNode,self._go._jointOrientation[0]))

                #>>>Parent IK handles
                mi_fingerIKHandleNF.parent = mi_controlIK.mNode#handle to control	
                ml_distHandlesNF[-1].parent = mi_controlIK.mNode#handle to control
                ml_distHandlesNF[0].parent = self._go._i_constrainNull.fingerRoot.mNode#start to root
                ml_distHandlesNF[1].parent = self._go._i_constrainNull.fingerRoot.mNode#mid to root

                #>>> Fix our ik_handle twist at the end of all of the parenting
                #poleVector = mc.poleVectorConstraint (mi_rpHandleNF.mNode,mi_fingerIKHandleNF.mNode)  		
                rUtils.IKHandle_fixTwist(mi_fingerIKHandleNF)#Fix the twist

            except Exception,error:
                raise Exception,"%s.build_FKIK>>> IK No Flip error: %s"%(self._go._strShortName,error)

            #=============================================================   
            try:#>>>Constrain IK Finger
                #Create hand IK
                mc.orientConstraint(mi_controlIK.mNode,mi_ikEnd.mNode, maintainOffset = True)

            except Exception,error:
                raise Exception,"%s.build_FKIK>>> IK No Flip error: %s"%(self._go._strShortName,error)

            #=============================================================    
            try:#>>>Connect Blend Chains and connections
                #>>> Main blend
                mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',lock=False,keyable=True)

                if self.ml_fkAttachJoints:
                    ml_fkUse = self.ml_fkAttachJoints
                    for i,mJoint in enumerate(self.ml_fkAttachJoints):
                        mc.pointConstraint(ml_fkJoints[i].mNode,mJoint.mNode,maintainOffset = False)
                        #Connect inversed aim and up
                        NodeF.connectNegativeAttrs(ml_fkJoints[i].mNode, mJoint.mNode,
                                                   ["r%s"%self._go._jointOrientation[0],"r%s"%self._go._jointOrientation[1]]).go()
                        cgmMeta.cgmAttr(ml_fkJoints[i].mNode,"r%s"%self._go._jointOrientation[2]).doConnectOut("%s.r%s"%(mJoint.mNode,self._go._jointOrientation[2]))

                    self.ml_fkAttachJoints[0].parent = ml_controlsFK[0].parent#match parent, for thumb, only root	    

                else:
                    ml_fkUse = ml_fkJoints

                rUtils.connectBlendChainByConstraint(ml_fkUse,ml_ikJoints,ml_blendJoints,
                                                     driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])




                #>>> Settings - constrain
                mi_settings.masterGroup.parent = self._go._i_constrainNull.mNode	
                mc.pointConstraint(ml_blendJoints[1].mNode, mi_settings.masterGroup.mNode, maintainOffset = True)
                mc.orientConstraint(ml_blendJoints[1].mNode, mi_settings.masterGroup.mNode, maintainOffset = True)	

                #>>> Setup a vis blend result
                mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=False)	
                mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=False)	

                NodeF.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,mPlug_IKon.p_combinedName,mPlug_FKon.p_combinedName)

                mPlug_FKon.doConnectOut("%s.visibility"%self._go._i_constrainNull.controlsFK.mNode)
                mPlug_IKon.doConnectOut("%s.visibility"%self._go._i_constrainNull.controlsIK.mNode)

            except Exception,error:
                raise Exception,"%s.build_FKIK>>> blend connect error: %s"%(self._go._strShortName,error)
            log.info("%s.build_FKIK complete!"%self._go._mi_module.getShortName())
            return True
    return fncWrap(goInstance).go()

def build_FKIK2(self):
    """
    """
    try:#===================================================
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("thumb.build_FKIK>>bad self!")
        raise Exception,error

    #>>>Get data
    ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')   
    ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
    ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
    ml_fkJoints = self._i_rigNull.msgList_get('fkJoints')
    ml_ikJoints = self._i_rigNull.msgList_get('ikJoints')


    mi_settings = self._i_rigNull.settings

    aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
    upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1])
    outVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[2])

    mi_controlIK = self._i_rigNull.controlIK

    for chain in [ml_ikJoints,ml_blendJoints]:
        chain[0].parent = self._i_constrainNull.mNode

    #for more stable ik, we're gonna lock off the lower channels degrees of freedom
    for chain in [ml_ikJoints]:
        for axis in self._jointOrientation[:2]:
            log.info(axis)
            for i_j in chain[1:]:
                attributes.doSetAttr(i_j.mNode,"jointType%s"%axis.upper(),1)

    #=============================================================    
    try:#>>>Finger Root Control and root follow
        #we have to rebuild a little so that we can use our fk base control both for fk and ik
        #Create a orient group that tracks the  module constrain null
        buffer_fkGroup = ml_fkJoints[0].parent
        i_orientGroup = cgmMeta.asMeta( ml_fkJoints[1].doGroup(True),'cgmObject',setClass=True )
        i_orientGroup.addAttr('cgmTypeModifier','toOrient')
        i_orientGroup.doName()

        #constrain it 
        str_orConst = mc.orientConstraint(self._i_constrainNull.mNode,i_orientGroup.mNode,maintainOffset = True)[0]
        attributes.doSetLockHideKeyableAttr(i_orientGroup.mNode)#lockNHide
        self._i_constrainNull.connectChildNode(i_orientGroup,'fingerRoot','owner')#Connect
        i_orientGroup.parent = self._i_constrainNull.mNode

        i_parentGroup = cgmMeta.asMeta( i_orientGroup.doGroup(True),'cgmObject',setClass=True )
        i_parentGroup.addAttr('cgmTypeModifier','toParent')
        i_parentGroup.doName()	
        str_prntConst = mc.parentConstraint( ml_fkJoints[0].mNode,i_parentGroup.mNode,maintainOffset = True)[0]
        i_parentGroup.parent = buffer_fkGroup

        for attr in ['tx','ty','tz']:#Unlock a few things
            i_attr = cgmMeta.cgmAttr(ml_fkJoints[0],attr)
            i_attr.p_keyable = True
            i_attr.p_locked = False	    
        #attributes.doSetLockHideKeyableAttr(ml_fkJoints[0].mNode,lock = False, visible=True, keyable=True, channels=['tx','ty','tz'])

        #Constrain ik base to fk base
        mc.orientConstraint(ml_fkJoints[0].mNode,ml_ikJoints[0].mNode,maintainOffset = True)

        ml_fkJoints[0].parent = self._i_constrainNull.mNode

    except Exception,error:
        raise Exception,"%s.build_FKIK>>> Finger Root Control error: %s"%(self._strShortName,error)

    return
    #=============================================================    
    try:#>>>FK Length connector
        for i,i_jnt in enumerate(ml_fkJoints[1:-1]):
            rUtils.addJointLengthAttr(i_jnt,orientation=self._jointOrientation)

        #IK
        rUtils.addJointLengthAttr(ml_ikJoints[-2],[mi_controlIK,'length'],orientation=self._jointOrientation)

    except Exception,error:
        raise Exception,"%s.build_FKIK>>> fk length connect error: %s"%(self._strShortName,error)

    #=============================================================  
    try:#>>>IK No Flip Chain
        mPlug_globalScale = cgmMeta.cgmAttr(self._i_masterControl.mNode,'scaleY')
        ml_ikNoFlipJoints = ml_ikJoints#Link
        i_tmpLoc = ml_ikNoFlipJoints[1].doLoc()#loc the first real 
        i_tmpLoc.parent = self._i_constrainNull.fingerRoot.mNode
        str_twistGroup = i_tmpLoc.doGroup(True)

        f_dist = distance.returnDistanceBetweenPoints(ml_ikNoFlipJoints[1].getPosition(),ml_ikNoFlipJoints[-1].getPosition()) #Measure first thumb joint to end
        f_dist = f_dist * 1.5
        if self._direction == 'left':#if right, rotate the pivots
            i_tmpLoc.__setattr__('t%s'%self._jointOrientation[2],-f_dist)
        else:
            i_tmpLoc.__setattr__('t%s'%self._jointOrientation[2],f_dist)

        #Create no flip thumb IK
        d_ankleNoFlipReturn = rUtils.IKHandle_create(ml_ikNoFlipJoints[1].mNode,ml_ikNoFlipJoints[-2].mNode,lockMid=False,
                                                     nameSuffix = 'noFlip',rpHandle=True,controlObject=mi_controlIK,addLengthMulti=True,
                                                     globalScaleAttr=mPlug_globalScale.p_combinedName, stretch='translate',moduleInstance=self._mi_module)

        mi_fingerIKHandleNF = d_ankleNoFlipReturn['mi_handle']
        ml_distHandlesNF = d_ankleNoFlipReturn['ml_distHandles']
        mi_rpHandleNF = d_ankleNoFlipReturn['mi_rpHandle']
        #mPlug_lockMid = d_ankleNoFlipReturn['mPlug_lockMid']

        #No Flip RP handle
        Snap.go(mi_rpHandleNF,i_tmpLoc.mNode,True)#Snape to hand control, then move it out...
        i_tmpLoc.delete()

        mi_rpHandleNF.doCopyNameTagsFromObject(self._mi_module.mNode, ignore = ['cgmName','cgmType'])
        mi_rpHandleNF.addAttr('cgmName','%sPoleVector'%self._partName, attrType = 'string')
        mi_rpHandleNF.addAttr('cgmTypeModifier','noFlip')
        mi_rpHandleNF.doName()

        #spin
        #=========================================================================================
        #Make a spin group
        i_spinGroup = cgmMeta.cgmObject(str_twistGroup)
        i_spinGroup.doCopyNameTagsFromObject(self._mi_module.mNode, ignore = ['cgmName','cgmType'])	
        i_spinGroup.addAttr('cgmName','%sNoFlipSpin'%self._partName)
        i_spinGroup.doName()

        i_spinGroup.doZeroGroup()
        mi_rpHandleNF.parent = i_spinGroup.mNode

        #Setup arg
        mPlug_fingerSpin = cgmMeta.cgmAttr(mi_controlIK,'fingerSpin')
        mPlug_fingerSpin.doConnectOut("%s.r%s"%(i_spinGroup.mNode,self._jointOrientation[0]))

        #>>>Parent IK handles
        mi_fingerIKHandleNF.parent = mi_controlIK.mNode#handle to control	
        ml_distHandlesNF[-1].parent = mi_controlIK.mNode#handle to control
        ml_distHandlesNF[0].parent = self._i_constrainNull.fingerRoot.mNode#start to root
        ml_distHandlesNF[1].parent = self._i_constrainNull.fingerRoot.mNode#mid to root

        #>>> Fix our ik_handle twist at the end of all of the parenting
        #poleVector = mc.poleVectorConstraint (mi_rpHandleNF.mNode,mi_fingerIKHandleNF.mNode)  		
        rUtils.IKHandle_fixTwist(mi_fingerIKHandleNF)#Fix the twist

    except Exception,error:
        raise Exception,"%s.build_FKIK>>> IK No Flip error: %s"%(self._strShortName,error)

    #=============================================================   
    try:#>>>Constrain IK Finger
        #Create hand IK
        #ml_ikJoints[-2].parent = False
        mc.orientConstraint(mi_controlIK.mNode,ml_ikJoints[-2].mNode, maintainOffset = True)
        #mc.pointConstraint(mi_controlIK.mNode,ml_ikJoints[-2].mNode, maintainOffset = True)


    except Exception,error:
        raise Exception,"%s.build_FKIK>>> IK No Flip error: %s"%(self._strShortName,error)

    #=============================================================    
    try:#>>>Connect Blend Chains and connections
        #>>> Main blend
        mPlug_FKIK = cgmMeta.cgmAttr(mi_settings.mNode,'blend_FKIK',lock=False,keyable=True)

        rUtils.connectBlendChainByConstraint(ml_fkJoints,ml_ikJoints,ml_blendJoints,
                                             driver = mPlug_FKIK.p_combinedName,l_constraints=['point','orient'])

        #>>> Settings - constrain
        #mi_settings.masterGroup.parent = ml_blendJoints[0].mNode	
        mi_settings.masterGroup.parent = self._i_constrainNull.mNode	
        mc.pointConstraint(ml_blendJoints[1].mNode, mi_settings.masterGroup.mNode, maintainOffset = True)
        mc.orientConstraint(ml_blendJoints[1].mNode, mi_settings.masterGroup.mNode, maintainOffset = True)

        #mc.parentConstraint(ml_blendJoints[0].mNode, mi_settings.masterGroup.mNode, maintainOffset = True)

        #>>> Setup a vis blend result
        mPlug_FKon = cgmMeta.cgmAttr(mi_settings,'result_FKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=False)	
        mPlug_IKon = cgmMeta.cgmAttr(mi_settings,'result_IKon',attrType='float',defaultValue = 0,keyable = False,lock=True,hidden=False)	

        NodeF.createSingleBlendNetwork(mPlug_FKIK.p_combinedName,mPlug_IKon.p_combinedName,mPlug_FKon.p_combinedName)

        mPlug_FKon.doConnectOut("%s.visibility"%self._i_constrainNull.controlsFK.mNode)
        mPlug_IKon.doConnectOut("%s.visibility"%self._i_constrainNull.controlsIK.mNode)

    except Exception,error:
        raise Exception,"%s.build_FKIK>>> blend connect error: %s"%(self._strShortName,error)
    log.info("%s.build_FKIK complete!"%self._mi_module.getShortName())
    return True

def build_rig(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_rig(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Build NOT BROKEN UP YET','call':self.build}]	
            #=================================================================

        def build(self):#================================================================================   	

            try:#>>>Get data
                orientation = self._go._jointOrientation or modules.returnSettingsData('jointOrientation')
                mi_moduleParent = False
                if self._go._mi_module.getMessage('moduleParent'):
                    mi_moduleParent = self._go._mi_module.moduleParent

                mi_controlIK = self._go._i_rigNull.controlIK
                ml_controlsFK =  self._go._i_rigNull.msgList_get('controlsFK')    
                ml_rigJoints = self._go._i_rigNull.msgList_get('rigJoints')
                ml_blendJoints = self._go._i_rigNull.msgList_get('blendJoints')
                mi_settings = self._go._i_rigNull.settings

                log.info("mi_controlIK: %s"%mi_controlIK.getShortName())
                log.info("ml_controlsFK: %s"%[o.getShortName() for o in ml_controlsFK])
                log.info("mi_settings: %s"%mi_settings.getShortName())

                log.info("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
                log.info("ml_blendJoints: %s"%[o.getShortName() for o in ml_blendJoints])

                ml_segmentHandleChains = self._go._get_segmentHandleChains()
                ml_segmentChains = self._go._get_segmentChains()
                ml_influenceChains = self._go._get_influenceChains()	

                aimVector = dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[0])
                upVector = dictionary.stringToVectorDict.get("%s+"%self._go._jointOrientation[1]) 

                #Build our contrain to pool
                l_constrainTargetJoints = []
                """
		for ml_chain in ml_segmentChains:
		    l_constrainTargetJoints.extend([i_jnt.mNode for i_jnt in ml_chain[:-1]])
		l_constrainTargetJoints.extend([i_jnt.mNode for i_jnt in ml_blendJoints[-2:]])
		"""
                if not l_constrainTargetJoints:
                    l_constrainTargetJoints = [i_jnt.mNode for i_jnt in ml_blendJoints]

                for i_jnt in ml_blendJoints:
                    attributes.doSetLockHideKeyableAttr(i_jnt.mNode,lock=True, visible=True, keyable=False)
                    i_jnt.radius = 0#This is how we can hide joints without hiding them since we have children we want to ride along
                    i_jnt.drawStyle = 2

                #Set group lockks
                for mCtrl in self._go._i_rigNull.msgList_get('controlsAll'):
                    try:mCtrl._setControlGroupLocks()	
                    except Exception,error:log.error("%s _setControlGroupLocks failed on object: %s"%(self._str_reportStart,mCtrl.p_nameShort))
            except Exception,error:
                log.error("finger.build_rig>> Gather data fail!")
                raise Exception,error


            #Dynamic parent groups
            #====================================================================================
            try:#>>>> IK
                ml_fingerDynParents = []
                #Build our dynamic groups
                """
		1)wrist
		2)fk root
		3)...
		4)world
		"""
                if mi_moduleParent:
                    mi_blendEndJoint = mi_moduleParent.rigNull.msgList_get('blendJoints')[-1]	    
                    mi_parentRigNull = mi_moduleParent.rigNull
                    if mi_moduleParent:
                        mi_parentRigNull = mi_moduleParent.rigNull
                        buffer = mi_parentRigNull.msgList_get('moduleJoints')
                        if buffer:
                            ml_fingerDynParents.append( buffer[-1])	

                ml_fingerDynParents.append( ml_controlsFK[0])	

                mi_spine = self._go._mi_module.modulePuppet.getModuleFromDict(moduleType= ['torso','spine'])
                if mi_spine:
                    log.info("spine found: %s"%mi_spine)	    
                    mi_spineRigNull = mi_spine.rigNull
                    ml_fingerDynParents.append( mi_spineRigNull.handleIK )	    
                    ml_fingerDynParents.append( mi_spineRigNull.cog )
                    ml_fingerDynParents.append( mi_spineRigNull.hips )	    

                ml_fingerDynParents.append(self._go._i_masterControl)
                if mi_controlIK.getMessage('spacePivots'):
                    ml_fingerDynParents.extend(mi_controlIK.msgList_get('spacePivots',asMeta = True))	
                log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._go._strShortName,[i_obj.getShortName() for i_obj in ml_fingerDynParents]))


                #Add our parents
                i_dynGroup = mi_controlIK.dynParentGroup
                log.info("Dyn group at setup: %s"%i_dynGroup)
                i_dynGroup.dynMode = 0

                for o in ml_fingerDynParents:
                    i_dynGroup.addDynParent(o)
                i_dynGroup.rebuild()

            except Exception,error:
                log.error("finger.build_rig>> finger ik dynamic parent setup fail!")
                raise Exception,error

            #Make some connections
            #====================================================================================

            #Parent and constrain joints
            #====================================================================================
            ml_rigJoints[0].parent = self._go._i_deformNull.mNode#shoulder
            #ml_rigJoints[-1].parent = self._go._i_deformNull.mNode#wrist

            #For each of our rig joints, find the closest constraint target joint
            log.info("targetJoints: %s"%l_constrainTargetJoints)
            l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
            for i,i_jnt in enumerate(ml_rigJoints):
                #Don't try scale constraints in here, they're not viable
                log.info("Checking: '%s'"%i_jnt.getShortName())
                attachJoint = distance.returnClosestObject(i_jnt.mNode,l_constrainTargetJoints)
                log.info("'%s'<< drives <<'%s'"%(i_jnt.getShortName(),cgmMeta.cgmNode(attachJoint).getShortName()))
                pntConstBuffer = mc.pointConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
                orConstBuffer = mc.orientConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
                mc.connectAttr((attachJoint+'.s'),(i_jnt.mNode+'.s'))

            #Setup finger scaling
            #==================================================================================== 
            #Parent deform Null to last blend parent
            if mi_moduleParent:
                mi_blendEndJoint = mi_moduleParent.rigNull.msgList_get('blendJoints')[-1]
                mi_parentBlendPlug = cgmMeta.cgmAttr(mi_blendEndJoint,'scale')
                self._go._i_deformNull.parent = mi_blendEndJoint.mNode

                #connect blend joint scale to the finger blend joints
                for i_jnt in ml_blendJoints:
                    mi_parentBlendPlug.doConnectOut("%s.scale"%i_jnt.mNode)

                #intercept world scale on finger IK and add in the blend wrist scale
                mPlug_moduleMasterScale = cgmMeta.cgmAttr(self._go._i_rigNull,'masterScale',value = 1.0,defaultValue=1.0)
                mPlug_globalScale = cgmMeta.cgmAttr(self._go._i_masterControl.mNode,'scaleY')
                mPlug_globalScale.doConnectOut(mPlug_moduleMasterScale)
                NodeF.argsToNodes("%s = %s * %s.sy"%(mPlug_moduleMasterScale.p_combinedShortName,
                                                     mPlug_globalScale.p_combinedShortName,
                                                     mi_blendEndJoint.p_nameShort)).doBuild()

            #Vis Network, lock and hide
            #====================================================================================
            #Segment handles need to lock
            for ml_chain in ml_segmentHandleChains:
                for i_obj in ml_chain:
                    attributes.doSetLockHideKeyableAttr(i_obj.mNode,lock=True, visible=False, keyable=False, channels=['s%s'%orientation[1],'s%s'%orientation[2]])

            attributes.doSetLockHideKeyableAttr(mi_settings.mNode,lock=True, visible=False, keyable=False)
            attributes.doSetLockHideKeyableAttr(ml_blendJoints[0].mNode,lock=True, visible=True, keyable=False)

            try:#Set up some defaults
                #====================================================================================
                mPlug_autoStretch = cgmMeta.cgmAttr(mi_controlIK,'autoStretch')
                mPlug_autoStretch.p_defaultValue = 1.0
                mPlug_autoStretch.value =  1

            except Exception,error:
                raise Exception,"%s.build_rig >> failed to setup defaults | %s"%(self._go._strShortName,error)	     

            #Final stuff
            self._go._set_versionToCurrent()
            return True 
    return fncWrap(goInstance).go()


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
        log.error("thumb.build_deformationRig>>bad self!")
        raise Exception,error

    try:#>>>Get data
        orientation = self._jointOrientation or modules.returnSettingsData('jointOrientation')
        mi_moduleParent = False
        if self._mi_module.getMessage('moduleParent'):
            mi_moduleParent = self._mi_module.moduleParent

        mi_controlIK = self._i_rigNull.controlIK
        ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
        ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
        ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
        mi_settings = self._i_rigNull.settings

        log.info("mi_controlIK: %s"%mi_controlIK.getShortName())
        log.info("ml_controlsFK: %s"%[o.getShortName() for o in ml_controlsFK])
        log.info("mi_settings: %s"%mi_settings.getShortName())

        log.info("ml_rigJoints: %s"%[o.getShortName() for o in ml_rigJoints])
        log.info("ml_blendJoints: %s"%[o.getShortName() for o in ml_blendJoints])

        ml_segmentHandleChains = self._get_segmentHandleChains()
        ml_segmentChains = self._get_segmentChains()
        ml_influenceChains = self._get_influenceChains()	

        aimVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[0])
        upVector = dictionary.stringToVectorDict.get("%s+"%self._jointOrientation[1]) 

        #Build our contrain to pool
        l_constrainTargetJoints = []
        """
	for ml_chain in ml_segmentChains:
	    l_constrainTargetJoints.extend([i_jnt.mNode for i_jnt in ml_chain[:-1]])
	l_constrainTargetJoints.extend([i_jnt.mNode for i_jnt in ml_blendJoints[-2:]])
	"""
        if not l_constrainTargetJoints:
            l_constrainTargetJoints = [i_jnt.mNode for i_jnt in ml_blendJoints]
    except Exception,error:
        log.error("thumb.build_rig>> Gather data fail!")
        raise Exception,error

    #Constrain to pelvis
    #if mi_moduleParent:
        #mc.parentConstraint(mi_moduleParent.rig_getSkinJoints()[-1].mNode,self._i_constrainNull.mNode,maintainOffset = True)

    #Dynamic parent groups
    #====================================================================================
    try:#>>>> IK
        ml_fingerDynParents = []
        #Build our dynamic groups
        """
	1)wrist
	2)fk root
	3)...
	4)world
	"""
        if mi_moduleParent:
            mi_parentRigNull = mi_moduleParent.rigNull
            buffer = mi_parentRigNull.msgList_get('moduleJoints')
            if buffer:
                ml_fingerDynParents.append( buffer[-1])	

        ml_fingerDynParents.append( ml_controlsFK[0])	

        mi_spine = self._mi_module.modulePuppet.getModuleFromDict(moduleType= ['torso','spine'])
        if mi_spine:
            log.info("spine found: %s"%mi_spine)	    
            mi_spineRigNull = mi_spine.rigNull
            ml_fingerDynParents.append( mi_spineRigNull.handleIK )	    
            ml_fingerDynParents.append( mi_spineRigNull.cog )
            ml_fingerDynParents.append( mi_spineRigNull.hips )	    

        ml_fingerDynParents.append(self._i_masterControl)
        if mi_controlIK.getMessage('spacePivots'):
            ml_fingerDynParents.extend(mi_controlIK.msgList_get('spacePivots',asMeta = True))	
        log.info("%s.build_rig>>> Dynamic parents to add: %s"%(self._strShortName,[i_obj.getShortName() for i_obj in ml_fingerDynParents]))


        #Add our parents
        i_dynGroup = mi_controlIK.dynParentGroup
        log.info("Dyn group at setup: %s"%i_dynGroup)
        i_dynGroup.dynMode = 0

        for o in ml_fingerDynParents:
            i_dynGroup.addDynParent(o)
        i_dynGroup.rebuild()

    except Exception,error:
        log.error("thumb.build_rig>> thumb ik dynamic parent setup fail!")
        raise Exception,error

    #Make some connections
    #====================================================================================

    #Parent and constrain joints
    #====================================================================================
    ml_rigJoints[0].parent = self._i_deformNull.mNode#shoulder
    #ml_rigJoints[-1].parent = self._i_deformNull.mNode#wrist

    #For each of our rig joints, find the closest constraint target joint
    log.info("targetJoints: %s"%l_constrainTargetJoints)
    l_rigJoints = [i_jnt.mNode for i_jnt in ml_rigJoints]
    for i,i_jnt in enumerate(ml_rigJoints):
        #Don't try scale constraints in here, they're not viable
        log.info("Checking: '%s'"%i_jnt.getShortName())
        attachJoint = distance.returnClosestObject(i_jnt.mNode,l_constrainTargetJoints)
        log.info("'%s'<< drives <<'%s'"%(i_jnt.getShortName(),cgmMeta.cgmNode(attachJoint).getShortName()))
        pntConstBuffer = mc.pointConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
        orConstBuffer = mc.orientConstraint(attachJoint,i_jnt.mNode,maintainOffset=False,weight=1)
        mc.connectAttr((attachJoint+'.s'),(i_jnt.mNode+'.s'))

    #Vis Network, lock and hide
    #====================================================================================
    #Segment handles need to lock
    for ml_chain in ml_segmentHandleChains:
        for i_obj in ml_chain:
            attributes.doSetLockHideKeyableAttr(i_obj.mNode,lock=True, visible=False, keyable=False, channels=['s%s'%orientation[1],'s%s'%orientation[2]])
    #
    attributes.doSetLockHideKeyableAttr(mi_settings.mNode,lock=True, visible=False, keyable=False)
    attributes.doSetLockHideKeyableAttr(ml_blendJoints[0].mNode,lock=True, visible=True, keyable=False)

    #Final stuff
    mc.parentConstraint('l_wrist_jnt', self._i_constrainNull.mNode,maintainOffset = True)
    #mc.parentConstraint(mi_moduleParent.rig_getSkinJoints()[-1].mNode, self._i_constrainNull.mNode,maintainOffset = True)
    self._i_rigNull.version = str(__version__)
    return True 

def build_matchSystem(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_matchSystem(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Build NOT BROKEN UP YET','call':self.build}]	
            #=================================================================

        def build(self):#================================================================================   	

            #Base info
            mi_moduleParent = False
            if self._go._mi_module.getMessage('moduleParent'):
                mi_moduleParent = self._go._mi_module.moduleParent

            mi_controlIK = self._go._i_rigNull.controlIK
            ml_controlsFK =  self._go._i_rigNull.msgList_get('controlsFK')    
            ml_rigJoints = self._go._i_rigNull.msgList_get('rigJoints')
            ml_blendJoints = self._go._i_rigNull.msgList_get('blendJoints')
            mi_settings = self._go._i_rigNull.settings

            ml_fkJoints = self._go._i_rigNull.msgList_get('fkJoints')
            ml_ikJoints = self._go._i_rigNull.msgList_get('ikJoints')

            mi_dynSwitch = self._go._i_dynSwitch

            #>>> Get the joints
            if self._go._partType == 'finger':
                ml_fkToDo = ml_fkJoints[1:]
                ml_ikToDo = ml_ikJoints[1:]
                ml_blendToDo = ml_blendJoints[1:]	
                ml_fkControlsToDo = ml_controlsFK[1:]
            else:#thumb
                ml_fkToDo = ml_fkJoints
                ml_ikToDo = ml_ikJoints
                ml_fkControlsToDo = ml_controlsFK
                ml_blendToDo = ml_blendJoints	
                log.info([i_jnt.getShortName() for i_jnt in ml_fkToDo])


            #>>> First IK to FK
            i_ikMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlIK,
                                                   dynPrefix = "FKtoIK",
                                                   dynMatchTargets=ml_blendJoints[-2])
            i_ikMatch.addPrematchData({'fingerSpin':0})

            i_ikMatch.addDynIterTarget(drivenObject = ml_ikToDo[1],#seg 1
                                       matchObject = ml_blendToDo[1],
                                       drivenAttr= 't%s'%self._go._jointOrientation[0],
                                       minValue=0.001,
                                       maxValue=30,
                                       maxIter=15,
                                       driverAttr='lengthUpr')    
            i_ikMatch.addDynIterTarget(drivenObject =ml_ikToDo[2],#seg2
                                       matchObject= ml_blendToDo[2],#Make a new one
                                       drivenAttr='t%s'%self._go._jointOrientation[0],
                                       minValue=0.001,
                                       maxValue=30,
                                       maxIter=15,
                                       driverAttr='lengthLwr') 

            i_ikMatch.addDynIterTarget(drivenObject =ml_ikToDo[3],#seg2
                                       matchObject= ml_blendToDo[3],#Make a new one
                                       drivenAttr='t%s'%self._go._jointOrientation[0],
                                       minValue=0.001,
                                       maxValue=30,
                                       maxIter=15,
                                       driverAttr='length') 

            i_ikMatch.addDynIterTarget(drivenObject = ml_ikToDo[1],#knee
                                       matchTarget = ml_blendToDo[1],#Make a new one
                                       minValue=-179,
                                       maxValue=179,
                                       maxIter=75,
                                       driverAttr='fingerSpin') 
            """
	    i_ikHandMatch.addDynAttrMatchTarget(dynObjectAttr='ikScale',
						matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._go._jointOrientation[0]],
						)"""


            #>>> FK to IK
            #============================================================================
            i_fk_match1 = cgmRigMeta.cgmDynamicMatch(dynObject = ml_fkControlsToDo[0],
                                                     dynPrefix = "IKtoFK",
                                                     dynMatchTargets=ml_blendToDo[0])
            i_fk_match1.addDynIterTarget(drivenObject =ml_fkToDo[1],
                                         matchObject = ml_blendToDo[1],
                                         drivenAttr='t%s'%self._go._jointOrientation[0],
                                         minValue=0.001,
                                         maxValue=30,
                                         maxIter=15,
                                         driverAttr='length')  

            i_fk_match2 = cgmRigMeta.cgmDynamicMatch(dynObject = ml_fkControlsToDo[1],
                                                     dynPrefix = "IKtoFK",
                                                     dynMatchTargets=ml_blendToDo[1])
            i_fk_match2.addDynIterTarget(drivenObject =ml_fkToDo[2],
                                         matchObject = ml_blendToDo[2],                                   
                                         drivenAttr='t%s'%self._go._jointOrientation[0],
                                         minValue=0.001,
                                         maxValue=30,
                                         maxIter=15,
                                         driverAttr='length')  

            i_fk_match3 = cgmRigMeta.cgmDynamicMatch(dynObject = ml_fkControlsToDo[2],
                                                     dynPrefix = "IKtoFK",
                                                     dynMatchTargets=ml_blendToDo[2])
            i_fk_match3.addDynIterTarget(drivenObject =ml_fkToDo[3],
                                         matchObject = ml_blendToDo[3],                                   
                                         drivenAttr='t%s'%self._go._jointOrientation[0],
                                         matchAttr = 't%s'%self._go._jointOrientation[0],
                                         minValue=0.001,
                                         maxValue=30,
                                         maxIter=15,
                                         driverAttr='length')  
            """
	    i_fkBallMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[3],
						      dynPrefix = "IKtoFK",
						      dynMatchTargets=ml_blendJoints[3])   

	    i_fkWristMatch.addDynAttrMatchTarget(dynObjectAttr='fkScale',
						 matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._go._jointOrientation[0]],
						 )   
						 """
            #>>> Register the switches
            mi_dynSwitch.addSwitch('snapToFK',[mi_settings.mNode,'blend_FKIK'],
                                   0,
                                   [i_fk_match1,i_fk_match2,i_fk_match3])

            mi_dynSwitch.addSwitch('snapToIK',[mi_settings.mNode,'blend_FKIK'],
                                   1,
                                   [i_ikMatch])

            return True
    return fncWrap(goInstance).go()

def build_matchSystem2(self):
    try:
        if not self._cgmClass == 'RigFactory.go':
            log.error("Not a RigFactory.go instance: '%s'"%self)
            raise Exception
    except Exception,error:
        log.error("thumb.build_deformationRig>>bad self!")
        raise Exception,error

    #Base info
    mi_moduleParent = False
    if self._mi_module.getMessage('moduleParent'):
        mi_moduleParent = self._mi_module.moduleParent

    mi_controlIK = self._i_rigNull.controlIK
    ml_controlsFK =  self._i_rigNull.msgList_get('controlsFK')    
    ml_rigJoints = self._i_rigNull.msgList_get('rigJoints')
    ml_blendJoints = self._i_rigNull.msgList_get('blendJoints')
    mi_settings = self._i_rigNull.settings

    ml_fkJoints = self._i_rigNull.msgList_get('fkJoints')
    ml_ikJoints = self._i_rigNull.msgList_get('ikJoints')

    mi_dynSwitch = self._i_dynSwitch

    #>>> First IK to FK
    i_ikMatch = cgmRigMeta.cgmDynamicMatch(dynObject=mi_controlIK,
                                           dynPrefix = "FKtoIK",
                                           dynMatchTargets=ml_blendJoints[-2])
    i_ikMatch.addPrematchData({'fingerSpin':0})

    i_ikMatch.addDynIterTarget(drivenObject =ml_ikJoints[2],#seg 1
                               matchObject = ml_blendJoints[2],
                               drivenAttr= 't%s'%self._jointOrientation[0],
                               matchAttr = 't%s'%self._jointOrientation[0],
                               minValue=0.001,
                               maxValue=30,
                               maxIter=15,
                               driverAttr='lengthUpr')    
    i_ikMatch.addDynIterTarget(drivenObject =ml_ikJoints[3],#seg2
                               matchObject= ml_blendJoints[3],#Make a new one
                               drivenAttr='t%s'%self._jointOrientation[0],
                               matchAttr = 't%s'%self._jointOrientation[0],
                               minValue=0.001,
                               maxValue=30,
                               maxIter=15,
                               driverAttr='lengthLwr') 

    i_ikMatch.addDynIterTarget(drivenObject =ml_ikJoints[4],#seg2
                               matchObject= ml_blendJoints[4],#Make a new one
                               drivenAttr='t%s'%self._jointOrientation[0],
                               matchAttr = 't%s'%self._jointOrientation[0],
                               minValue=0.001,
                               maxValue=30,
                               maxIter=15,
                               driverAttr='length') 

    i_ikMatch.addDynIterTarget(drivenObject = ml_ikJoints[2],#knee
                               matchTarget = ml_blendJoints[2],#Make a new one
                               minValue=-179,
                               maxValue=179,
                               maxIter=75,
                               driverAttr='fingerSpin') 
    """
    i_ikHandMatch.addDynAttrMatchTarget(dynObjectAttr='ikScale',
                                        matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._jointOrientation[0]],
                                        )"""


    #>>> FK to IK
    #============================================================================
    i_fk_match1 = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[1],
                                             dynPrefix = "IKtoFK",
                                             dynMatchTargets=ml_blendJoints[1])
    i_fk_match1.addDynIterTarget(drivenObject =ml_fkJoints[2],
                                 matchObject = ml_blendJoints[2],
                                 drivenAttr='t%s'%self._jointOrientation[0],
                                 matchAttr = 't%s'%self._jointOrientation[0],
                                 minValue=0.001,
                                 maxValue=30,
                                 maxIter=15,
                                 driverAttr='length')  

    i_fk_match2 = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[2],
                                             dynPrefix = "IKtoFK",
                                             dynMatchTargets=ml_blendJoints[2])
    i_fk_match2.addDynIterTarget(drivenObject =ml_fkJoints[3],
                                 matchObject = ml_blendJoints[3],                                   
                                 drivenAttr='t%s'%self._jointOrientation[0],
                                 matchAttr = 't%s'%self._jointOrientation[0],
                                 minValue=0.001,
                                 maxValue=30,
                                 maxIter=15,
                                 driverAttr='length')  

    i_fk_match3 = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[3],
                                             dynPrefix = "IKtoFK",
                                             dynMatchTargets=ml_blendJoints[3])
    i_fk_match3.addDynIterTarget(drivenObject =ml_fkJoints[4],
                                 matchObject = ml_blendJoints[4],                                   
                                 drivenAttr='t%s'%self._jointOrientation[0],
                                 matchAttr = 't%s'%self._jointOrientation[0],
                                 minValue=0.001,
                                 maxValue=30,
                                 maxIter=15,
                                 driverAttr='length')  
    """
    i_fkBallMatch = cgmRigMeta.cgmDynamicMatch(dynObject = ml_controlsFK[3],
                                              dynPrefix = "IKtoFK",
                                              dynMatchTargets=ml_blendJoints[3])   

    i_fkWristMatch.addDynAttrMatchTarget(dynObjectAttr='fkScale',
                                         matchAttrArg= [ml_blendJoints[-2].mNode,'s%s'%self._jointOrientation[0]],
                                         )   
					 """
    #>>> Register the switches
    mi_dynSwitch.addSwitch('snapToFK',[mi_settings.mNode,'blend_FKIK'],
                           0,
                           [i_fk_match1,i_fk_match2,i_fk_match3])

    mi_dynSwitch.addSwitch('snapToIK',[mi_settings.mNode,'blend_FKIK'],
                           1,
                           [i_ikMatch])

    return True

#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'fkik','function':build_FKIK},
                    4:{'name':'rig','function':build_rig},
                    5:{'name':'match','function':build_matchSystem},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------
