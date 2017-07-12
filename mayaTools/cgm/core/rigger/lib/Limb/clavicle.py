"""
------------------------------------------
cgm.core.rigger: Limb.clavicle
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

clavicle rig builder
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

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core.rigger.lib import module_Utils as modUtils
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

#>>> Skeleton
#=========================================================================================================
__l_jointAttrs__ = ['rigJoints','fkJoints']   

def __bindSkeletonSetup__(self):
    pass
'''
    log.info(">>> %s.__bindSkeletonSetup__ >> "%self._strShortName + "-"*75)            
    try:
	if not self._cgmClass == 'JointFactory.go':
	    log.error("Not a JointFactory.go instance: '%s'"%self)
	    raise Exception
    except Exception,error:
	log.error("clavicle.__bindSkeletonSetup__>>bad self!")
	raise Exception,error

    #>>> Re parent joints
    #=============================================================  
    #ml_skinJoints = self.rig_getSkinJoints() or []
    if not self._mi_module.isSkeletonized():
	raise Exception, "%s is not skeletonized yet."%self._strShortName
    try:pass
    except Exception,error:
	log.error("build_clavicle>>__bindSkeletonSetup__ fail!")
	raise Exception,error   
    '''
def build_rigSkeleton(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_rigSkeleton(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Rig Chain','call':self.build_rigJoints},
                                {'step':'FK Chain','call':self.build_fkJoints},
                                {'step':'Rotate Orders','call':self.build_rotateOrders},
                                {'step':'Connections','call':self.build_connections}]	
            #=================================================================

        def build_rigJoints(self):
            go = self.d_kws['goInstance']
            ml_rigJoints = []
            for i,j in enumerate(self._go._ml_skinJoints):
                i_j = j.doDuplicate(parentOnly = True)
                i_j.addAttr('cgmTypeModifier','rig',attrType='string',lock=True)
                i_j.doName()
                ml_rigJoints.append(i_j)
            ml_rigJoints[0].parent = False#Parent to world		
            self._go._i_rigNull.msgList_connect('rigJoints',ml_rigJoints,"rigNull")

            self.ml_rigJoints = ml_rigJoints#pass to wrapper

        def build_fkJoints(self):
            ml_fkJoints = []
            for i,i_ctrl in enumerate(self._go._i_templateNull.msgList_get('controlObjects')):
                if not i_ctrl.getMessage('handleJoint'):
                    raise Exception,"%s.build_rigSkeleton>>> failed to find a handle joint from: '%s'"%(self._go._mi_module.getShortName(),i_ctrl.getShortName())
                i_new = cgmMeta.cgmObject((i_ctrl.getMessage('handleJoint')[0])).doDuplicate()
                i_new.addAttr('cgmTypeModifier','fk',attrType='string',lock=True)
                i_new.doName()
                if ml_fkJoints:#if we have data, parent to last
                    i_new.parent = ml_fkJoints[-1]
                else:i_new.parent = False
                i_new.rotateOrder = self._go._jointOrientation#<<<<<<<<<<<<<<<<This would have to change for other orientations
                ml_fkJoints.append(i_new)	

            ml_fkJoints[-1].addAttr('cgmName','clavicleEnd')
            ml_fkJoints[-1].doName()

            try:
                if self._go._str_mirrorDirection == 'Right':#mirror control setup
                    #ml_fkDriverJoints = self._go.duplicate_jointChain(ml_fkJoints,'fkAttach','fkAttachJoints')
                    self._go.mirrorChainOrientation(ml_fkJoints)#Mirror 
                    """
		    for i,mJoint in enumerate(ml_fkJoints):
			log.info("Mirror connect: %s | %s"%(i,mJoint.p_nameShort))
			mJoint.connectChildNode(ml_fkDriverJoints[i],"attachJoint","rootJoint")
			cgmMeta.cgmAttr(mJoint.mNode,"rotateOrder").doConnectOut("%s.rotateOrder"%ml_fkDriverJoints[i].mNode)
			"""
            except Exception,error: raise Exception,"Failed to create mirror chain | %s"%error

            self._go._i_rigNull.msgList_connect('fkJoints',ml_fkJoints,"rigNull")
            self.ml_fkJoints = ml_fkJoints#pass to wrapper

        def build_rotateOrders(self):
            d_fkRotateOrders = {'hip':0,'ankle':0}#old hip - 5    
            for i_obj in self.ml_fkJoints:
                if i_obj.getAttr('cgmName') in d_fkRotateOrders.keys():
                    i_obj.rotateOrder = d_fkRotateOrders.get(i_obj.cgmName) 

        def build_connections(self):    
            ml_jointsToConnect = []
            ml_jointsToConnect.extend(self.ml_rigJoints)    

            for i_jnt in ml_jointsToConnect:
                i_jnt.overrideEnabled = 1		
                cgmMeta.cgmAttr(self._go._i_rigNull.mNode,'gutsVis',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideVisibility'))
                cgmMeta.cgmAttr(self._go._i_rigNull.mNode,'gutsLock',lock=False).doConnectOut("%s.%s"%(i_jnt.mNode,'overrideDisplayType'))    

    return fncWrap(goInstance).go()

#>>> Shapes
#===================================================================
__d_controlShapes__ = {'shape':['clavicle']}

def build_shapes(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_shapes(%s)'%self.d_kws['goInstance']._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Verify','call':self.verify},
                                {'step':'Shapes','call':self.build_shapes}]
            #=================================================================

        def verify(self):
            if self._go._i_templateNull.handles > 2:
                raise Exception, "Too many handles. don't know how to rig"
            if not self._go.isRigSkeletonized():
                raise Exception, "Must be rig skeletonized to shape"

        def build_shapes(self):
            l_toBuild = ['clavicle']
            mShapeCast.go(self._go._mi_module,l_toBuild, storageInstance= self._go )#This will store controls to a dict called    

    return fncWrap(goInstance).go()

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
                                {'step':'Connections','call':self.build_connections}]
            #=================================================================

        def verify(self):
            self.ml_controlsFK = cgmMeta.validateObjListArg(self._go._i_rigNull.getMessage('shape_clavicle'),cgmMeta.cgmObject,noneValid=False) 
            self.ml_fkJoints = cgmMeta.validateObjListArg(self._go._i_rigNull.msgList_getMessage('fkJoints'),cgmMeta.cgmObject,noneValid=False)

            if len(  self.ml_controlsFK  ) != 1:
                raise Exception,"Must have at least one fk control"

            self.ml_controlsAll = []

        def build_groups(self):
            for grp in ['controlsFK']:
                i_dup = self._go._i_constrainNull.doCreateAt(copyAttrs=True)
                i_dup.parent = self._go._i_constrainNull.mNode
                i_dup.addAttr('cgmTypeModifier',grp,lock=True)
                i_dup.doName()

                self._go._i_constrainNull.connectChildNode(i_dup,grp,'owner')

        def build_fk(self):
            #>>>> FK Segments
            ml_fkJoints = self.ml_fkJoints
            ml_controlsFK = self.ml_controlsFK

            ml_fkJoints[0].parent = self._go._i_constrainNull.controlsFK.mNode

            i_obj = ml_controlsFK[0]
            log.info(" %s controlFK : %s"%(self._str_reportStart,i_obj.p_nameShort))
            log.info(" %s controlFK : %s"%(self._str_reportStart,ml_fkJoints[0].p_nameShort))	    
            try:
                d_buffer = mControlFactory.registerControl(i_obj.mNode,shapeParentTo=ml_fkJoints[0].mNode,
                                                           mirrorSide=self._go._str_mirrorDirection, mirrorAxis="translateX",		                                           
                                                           makeAimable=True,typeModifier='fk') 
            except Exception,error: raise Exception,"Register control | %s"%error

            try:
                i_obj = d_buffer['instance']
                i_obj.axisAim = "%s+"%self._go._jointOrientation[0]
                i_obj.axisUp= "%s+"%self._go._jointOrientation[1]	
                i_obj.axisOut= "%s+"%self._go._jointOrientation[2]
                try:i_obj.drawStyle = 2#Stick joint draw style	    
                except:self.log_error("{0} Failed to set drawStyle".format(i_obj.p_nameShort))
                cgmMeta.cgmAttr(i_obj,'radius',hidden=True)
            except Exception,error: raise Exception,"Failed to set attrs | %s"%error

            try:
                for i_obj in ml_controlsFK:
                    i_obj.delete()
            except Exception,error: raise Exception,"Failed to delete | %s"%error

            self.ml_controlsAll.extend([ml_fkJoints[0]])	

        def build_connections(self):
            self._go._i_rigNull.msgList_connect('controlsFK',[self.ml_fkJoints[0]],"rigNull")	    
            self._go._i_rigNull.msgList_connect('controlsAll',self.ml_controlsAll)
            int_strt = self._go._i_puppet.get_nextMirrorIndex( self._go._str_mirrorDirection )

            try:
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


            try:
                for i,mCtrl in enumerate(self.ml_controlsAll):
                    mCtrl.mirrorIndex = int_strt + i		
            except Exception,error: raise Exception,"Failed to register mirror index | %s"%error

            try:self._go._i_rigNull.moduleSet.extend(self.ml_controlsAll)
            except Exception,error: raise Exception,"Failed to set module objectSet | %s"%error


    return fncWrap(goInstance).go()


def build_rig(goInstance = None):
    class fncWrap(modUtils.rigStep):
        def __init__(self,goInstance = None):
            super(fncWrap, self).__init__(goInstance)
            self._str_funcName = 'build_rig(%s)'%self._go._strShortName	
            self.__dataBind__()
            self.l_funcSteps = [{'step':'Verify','call':self.verify},
                                {'step':'Parent','call':self.build_structure},
                                {'step':'Lock N Hide','call':self.build_lockNHide},
                                {'step':'Finalize','call':self.finalize}]
            #=================================================================

        def verify(self):
            orientation = self._go._jointOrientation

            self.mi_moduleParent = False
            if self._go._mi_module.getMessage('moduleParent'):
                self.mi_moduleParent = self._go._mi_module.moduleParent

            self.ml_controlsFK = self._go._i_rigNull.msgList_get('controlsFK')	
            self.ml_rigJoints = self._go._i_rigNull.msgList_get('rigJoints')

            aimVector = dictionary.stringToVectorDict.get("%s+"%orientation)
            upVector = dictionary.stringToVectorDict.get("%s+"%orientation) 

        def build_structure(self):
            ml_controlsFK = self.ml_controlsFK
            ml_rigJoints = self.ml_rigJoints

            if self.mi_moduleParent:
                mc.parentConstraint(self.mi_moduleParent.rig_getSkinJoints()[-1].mNode,self._go._i_constrainNull.mNode,maintainOffset = True)

            #Parent and constrain joints
            #====================================================================================
            self.ml_rigJoints[0].parent = self._go._i_deformNull.mNode#hip

            #For each of our rig joints, find the closest constraint target joint
            pntConstBuffer = mc.pointConstraint(ml_controlsFK[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False,weight=1)
            orConstBuffer = mc.orientConstraint(ml_controlsFK[0].mNode,ml_rigJoints[0].mNode,maintainOffset=False,weight=1)
            mc.connectAttr((ml_controlsFK[0].mNode+'.s'),(ml_rigJoints[0].mNode+'.s'))   

        def build_lockNHide(self):
            ml_controlsFK = self.ml_controlsFK

            #Lock set groups
            for mCtrl in ml_controlsFK:
                mCtrl._setControlGroupLocks()	
                cgmMeta.cgmAttr(mCtrl,"translate",lock=True,hidden=True,keyable=False)  	
                cgmMeta.cgmAttr(mCtrl,"v",lock=True,hidden=True,keyable=False) 

        def finalize(self):
            self._go._set_versionToCurrent()

    return fncWrap(goInstance).go()

#----------------------------------------------------------------------------------------------
# Important info ==============================================================================
__d_buildOrder__ = {0:{'name':'skeleton','function':build_rigSkeleton},
                    1:{'name':'shapes','function':build_shapes},
                    2:{'name':'controls','function':build_controls},
                    3:{'name':'rig','function':build_rig},
                    } 
#===============================================================================================
#----------------------------------------------------------------------------------------------