import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_General as r9General

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
from cgm.core import cgm_Meta as cgmMeta
from cgm.lib.classes import NameFactory as nFactory
from cgm.core.classes import SnapFactory as Snap
from cgm.core.classes import GuiFactory as gui
from cgm.core.rigger import TemplateFactory as tFactory
from cgm.core.cgmPy import validateArgs as cgmValid
from cgm.core.classes import NodeFactory as cgmNodeFactory
from cgm.core.rigger.lib import morpheus_sharedData as MORPHYDATA
from cgm.lib import (curves,
                     deformers,
                     distance,
                     search,
                     lists,
                     modules,
                     constraints,
                     rigging,
                     attributes,
                     joints)


def headRig_connectToBody(*args, **kws):
    """
    Function to split a curve up u positionally 

    @kws
    Arg 0 | kw 'curve'(None)  -- Curve to split
    Arg 1 | kw 'points'(3)  -- Number of points to generate positions for
    
    Parts
    Skeleton
    Transform transfers
    Rig Stuffs
    """
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            """
            """	
            super(fncWrap, self).__init__(*args, **kws)
            self._b_reportTimes = True
            self._str_funcName = 'lbs_utils.headRig_connectToBody'	
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'attributeHolder',"default":None,
                                          'help':"Name of the attribute Holder"},]	    
            self.l_funcSteps = [{'step':'Data Gather','call':self._fncStep_dataCheck_},
                                {'step':'Parts Transfer','call':self._fncStep_parts_},
                                {'step':'Parenting','call':self._fncStep_parenting_},      
                                {'step':'Repair','call':self._fncStep_repair_},                                                                
                                ]	    
            self.__dataBind__(*args, **kws)
            
        def _fncStep_dataCheck_(self):
            #Key to object name dict
            _d_stuffToFind = {'headModule':'head_part',
                              'neckModule':'neck_part',
                              'l_eyeModule':'l_eye_part',
                              'r_eyeModule':'r_eye_part',
                              'headMasterAnim':'Head_masterAnim',
                              'headPuppet':'Head_puppetNetwork',
                              'BodyPuppet':'MK1_puppetNetwork',
                              'faceGui':'facialRig_gui_grp',
                              'faceCam':'faceCam',
                              'world_eyeLook':'world_driving_head_eyeLook_dynDriver',
                              'world_leftEye':'world_driving_right_eye_ik_dynDriver',
                              'world_rightEye':'world_driving_left_eye_ik_dynDriver',
                              'SDKface':'face_attrHolder',
                              'SDKcustomize':'sdk_custom_attrHolder',
                              'joint_bodyHead':'head_jnt',
                              'joint_faceRigHead':'headRoot_jnt',
                              'ik_eyes':'head_eyeLook_anim',
                              'ik_l_eye':'l_eye_ik_anim',
                              'ik_r_eye':'r_eye_ik_anim',
                              'ik_shoulders':'shoulders_ik_anim',
                              'ik_cog':'cog_anim',
                              }
            self.md_objs = {}
            for k in _d_stuffToFind.keys():
                _obj = cgmValid.objString(arg=_d_stuffToFind[k], noneValid=True, 
                                          calledFrom=self._str_funcName)
                if not _obj:
                    return self._FailBreak_("key: {0} | name: ('{1}') | missing".format(k,_d_stuffToFind[k]))
                self.md_objs[k] = cgmMeta.cgmNode(_obj)
                self.log_info("'{0}' found".format(k))
            
            self.log_infoNestedDict('md_objs')
            
        def _fncStep_parts_(self):
            """
            """
            #Change the module puppet of the head module to the body
            _mi_headModule = self.md_objs['headModule']
            _mi_neckModule = self.md_objs['neckModule']
            _mi_bodyPuppet = self.md_objs['BodyPuppet']
            _mi_headPuppet = self.md_objs['headPuppet']
            
            _mi_bodyPuppet.connectModule(_mi_headModule)#Connect head to the puppet
            _mi_headModule.doSetParentModule(_mi_neckModule)#Set the parent module
            _mi_bodyPuppet.gatherModules()
            
            try:#Eye look --------------------------------------------------------------------
                ml_eyeLooks = _mi_headPuppet.msgList_get('eyeLook')#...buffer the list
                _mi_bodyPuppet.msgList_connect('eyeLook',ml_eyeLooks)#...store to the new one
                for mObj in ml_eyeLooks:
                    mObj.connectParentNode(_mi_bodyPuppet,'puppet')
            except Exception,error:raise Exception,"Eye look transfer fail | error: {0}".format(error)
            
            try:#FaceDeform --------------------------------------------------------------------
                _mi_headModule.faceDeformNull.parent = _mi_bodyPuppet.masterNull.deformGroup
            except Exception,error:raise Exception,"Geo | error: {0}".format(error)  
            
        def _fncStep_parenting_(self):
            """
            """
            _mi_headMasterAnim = self.md_objs['headMasterAnim']
            _mi_bodyMasterAnim = self.md_objs['BodyPuppet'].masterControl
            _mi_bodyPuppet = self.md_objs['BodyPuppet']
            _mi_headPuppet = self.md_objs['headPuppet']
            
            try:#Geo --------------------------------------------------------------------
                for mObj in _mi_headPuppet.masterNull.geoGroup.getChildren(asMeta = True):
                    mObj.parent = _mi_bodyPuppet.masterNull.geoGroup
            except Exception,error:raise Exception,"Geo | error: {0}".format(error)    
            
            try:#Face Rig/gui --------------------------------------------------------------------
                for k in ['faceGui','faceCam']:
                    rigging.doParentReturnName(self.md_objs[k].mNode, _mi_bodyPuppet.masterNull.noTransformGroup.mNode)
            except Exception,error:raise Exception,"Face Rig/GUI | error: {0}".format(error)              
            
            try:#to Master control --------------------------------------------------------------------
                for k in ['world_eyeLook','world_leftEye','world_rightEye','SDKface','SDKcustomize']:
                    rigging.doParentReturnName(self.md_objs[k].mNode, _mi_bodyMasterAnim.mNode)
            except Exception,error:raise Exception,"...to master Control | error: {0}".format(error)         
            
            try:#Skeleton --------------------------------------------------------------------
                rigging.doParentReturnName(self.md_objs['joint_faceRigHead'].mNode, self.md_objs['joint_bodyHead'].mNode)
            except Exception,error:raise Exception,"...to master Control | error: {0}".format(error)  
            
            try:#Object Sets --------------------------------------------------------------------
                _mi_bodyPuppet = self.md_objs['BodyPuppet']
                
                for k in ['l_eyeModule','r_eyeModule','headModule']:
                    _mi_bodyPuppet.puppetSet.addObj(self.md_objs[k].rigNull.moduleSet.mNode)
                
            except Exception,error:raise Exception,"...to master Control | error: {0}".format(error)   
            
        def _fncStep_repair_(self):
            """
            """
            _mi_headMasterAnim = self.md_objs['headMasterAnim']
            _mi_bodyMasterAnim = self.md_objs['BodyPuppet'].masterControl
            
            try:#Reindex controls for mirroring --------------------------------------------------------------------
                _mi_bodyPuppet = self.md_objs['BodyPuppet']
                _mi_bodyPuppet._UTILS.mirrorSetup_verify(_mi_bodyPuppet,'anim')
                
            except Exception,error:raise Exception,"...reindex | error: {0}".format(error)   

            try:#Vis stuff? --------------------------------------------------------------------
                self.log_toDo('Vis stuff?')
            except Exception,error:raise Exception,"...to vis stuff| error: {0}".format(error)   
            
            try:#Register head as a space --------------------------------------------------------------------
                for k in ['ik_eyes']:#'ik_l_eye','ik_r_eye'
                    _mObj = self.md_objs[k]
                    _dynGroup = _mObj.dynParentGroup
                    for k2 in ['joint_faceRigHead','ik_shoulders','ik_cog']:
                        try:
                            _dynGroup.addDynParent(self.md_objs[k2].mNode)
                        except Exception,error:
                            raise Exception,"Add parent {0} fail!".format(k2)
                    try:
                        _dynGroup.rebuild()
                    except Exception,error:
                        raise Exception,"Rebuild fail! | {0}".format(error)                       
            except Exception,error:raise Exception,"...register spaces | error: {0}".format(error)   
            
            #self.report_toDo()
            try:#Vis stuff? --------------------------------------------------------------------
                self.log_toDo('Delete Old groups, lock skeleton/geo')
            except Exception,error:raise Exception,"...delete old stuff | error: {0}".format(error)  
            
    return fncWrap(*args,**kws).go()