"""
------------------------------------------
Builder: cgm.core.mrs
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import random
import re
import copy
import time

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#========================================================================

import maya.cmds as mc


# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_RigMeta as RIGMETA
from cgm.core import cgm_PuppetMeta as PUPPETMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.classes import NodeFactory as NODEFAC
reload(SNAP)

from cgm.core.mrs import RigBlocks as RIGBLOCKS
reload(RIGBLOCKS)
from cgm.core.mrs.blocks import box
reload(box)

_d_blockTypes = {'box':box}
_l_requiredModuleDat = ['__version__','__d_controlShapes','_l_jointAttrs__','__d_buildOrder__']#...data required in a given module

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Factory
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
class go(object):
    def __init__(self, rigBlock = None, forceNew = True, autoBuild = True, ignoreRigCheck = False,
                 *a,**kws):
        """
        Core rig block builder factory

        :parameters:
            rigBlock(str) | base rigBlock

        :returns
            factory instance
            
            
        """
        _str_func = 'go._init_'
        
        #>>Initial call ---------------------------------------------------------------------------------
        self._callBlock = None
        self._call_kws = {}
        self._rigBlock = None
        self._d_block = {}
        self._d_module = {}
        self._d_joints = {}
        self._d_orientation = {}         
        
        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:#...intial population
            self._call_kws = kws
            #log.debug("|{0}| >> kws: {1}".format(_str_func,kws))
        
        self._call_kws['forceNew'] = forceNew
        self._call_kws['rigBlock'] = rigBlock
        self._call_kws['autoBuild'] = autoBuild
        self._call_kws['ignoreRigCheck'] = ignoreRigCheck
        cgmGEN.log_info_dict(self._call_kws,_str_func)
        
        if not fnc_check_rigBlock(self):
            raise RuntimeError,"|{0}| >> RigBlock checks failed. See warnings and errors.".format(_str_func)
        log.debug("|{0}| >> RigBlock check passed".format(_str_func) + cgmGEN._str_subLine)
   
        if not fnc_check_module(self):
            raise RuntimeError,"|{0}| >> Module checks failed. See warnings and errors.".format(_str_func)
        log.debug("|{0}| >> Module check passed...".format(_str_func)+ cgmGEN._str_subLine)
        
        if not fnc_rigNeed(self):
            raise RuntimeError,"|{0}| >> No rig need see errors".format(_str_func)
        log.debug("|{0}| >> Rig needed...".format(_str_func)+ cgmGEN._str_subLine)
        
        if not fnc_bufferDat(self):
            raise RuntimeError,"|{0}| >> Failed to buffer data. See warnings and errors.".format(_str_func)
            
        if not fnc_moduleRigChecks(self):
            raise RuntimeError,"|{0}| >> Failed to process module rig Checks. See warnings and errors.".format(_str_func)
            
        
            
        #_verify = kws.get('verify',False)
        #log.debug("|{0}| >> verify: {1}".format(_str_func,_verify))
        
    def __repr__(self):
        try:return "{0}(rigBlock: {1})".format(self.__class__, self._rigBlock)
        except:return self

def fnc_check_rigBlock(self):
    """
    Check the rig block data 
    """
    _str_func = 'fnc_check_rigBlock' 
    _d = {}
    _res = True
    
    if not self._call_kws['rigBlock']:
        log.error("|{0}| >> No rigBlock stored in call kws".format(_str_func))
        return False
    
    BlockFactory = RIGBLOCKS.factory(self._call_kws['rigBlock'])
    BlockFactory.verify()
    
    _d['mBlock'] = BlockFactory._mi_root
    _d['mFactory'] = BlockFactory
    _d['shortName'] = BlockFactory._mi_root.getShortName()
    
    _buildModule = is_buildable(_d['mBlock'].blockType)
    if not _buildModule:
        log.error("|{0}| >> No build module found for: {1}".format(_str_func,_d['mBlock'].blockType))        
        return False
    _d['buildModule'] =  _buildModule   #if not is_buildable
    _d['buildVersion'] = _buildModule.__version__

    self._d_block = _d    
    cgmGEN.log_info_dict(_d,_str_func + " blockDat")   
    
    return True
    

def fnc_check_module(self):
    _str_func = 'fnc_check_module'  
    _res = True
    BlockFactory = self._d_block['mFactory']
    
    #>>Module -----------------------------------------------------------------------------------  
    _d = {}    
    BlockFactory.module_verify()
    _mModule = BlockFactory._mi_module
    self._mi_module = _mModule
    
    _mRigNull = _mModule.rigNull
    _d['mModule'] = _mModule
    _d['mRigNull'] = _mRigNull
    _d['shortName'] = _mModule.getShortName()
    _d['version'] = _mModule.rigNull.version
    
    _d['mModuleParent'] = False
    if _mModule.getMessage('moduleParent'):
        _d['mModuleParent'] = _mModule.moduleParent
        
        
    if not _mRigNull.getMessage('dynSwitch'):
        _mDynSwitch = RIGMETA.cgmDynamicSwitch(dynOwner=_mRigNull.mNode)
        log.debug("|{0}| >> Created dynSwitch: {1}".format(_str_func,_mDynSwitch))        
    else:
        _mDynSwitch = _mRigNull.dynSwitch  
    _d['mDynSwitch'] = _mDynSwitch
        
    #>>Puppet -----------------------------------------------------------------------------------    
    BlockFactory.puppet_verify()
    _mPuppet = _mModule.modulePuppet
    self._mi_puppet = _mPuppet
    
    _d['mPuppet'] = _mPuppet
    _mPuppet.__verifyGroups__()
    
    if not _mModule.isSkeletonized():
        log.warning("|{0}| >> Module isn't skeletonized. Attempting".format(_str_func))
        
        BlockFactory.skeletonize(True)
        if not _mModule.isSkeletonized():
            log.warning("|{0}| >> Skeletonization failed".format(_str_func))            
            _res = False
    
    self._d_module = _d    
    #cgmGEN.log_info_dict(_d,_str_func + " moduleDat")    
    return _res    


def fnc_moduleRigChecks(self):
    _str_func = 'fnc_moduleRigChecks'  
    _res = True
    _start = time.clock()
    
    
    #>>Connect switches ----------------------------------------------------------------------------------- 
    _str_settings = self._d_module['mMasterSettings'].getShortName()
    _str_partBase = self._d_module['partName'] + '_rig'
    _str_moduleRigNull = self._d_module['mRigNull'].getShortName()
    
    _mMasterSettings = self._d_module['mMasterSettings']
    
    _mMasterSettings.addAttr(_str_partBase,enumName = 'off:lock:on', defaultValue = 0, attrType = 'enum',keyable = False,hidden = False)
    
    try:NODEFAC.argsToNodes("{0}.gutsVis = if {1}.{2} > 0".format(_str_moduleRigNull,
                                                                _str_settings,
                                                                _str_partBase)).doBuild()
    except Exception,err:
        raise Exception,"|{0}| >> visArg failed [{1}]".format(_str_func,err)
    
    try:NODEFAC.argsToNodes("{0}.gutsLock = if {1}.{2} == 2:0 else 2".format(_str_moduleRigNull,
                                                                          _str_settings,
                                                                          _str_partBase)).doBuild()
    except Exception,err:
        raise Exception,"|{0}| >> lock arg failed [{1}]".format(_str_func,err)

    self._d_module['mRigNull'].overrideEnabled = 1		
    cgmMeta.cgmAttr(_str_moduleRigNull,'gutsVis',lock=False).doConnectOut("%s.%s"%(_str_moduleRigNull,'overrideVisibility'))
    cgmMeta.cgmAttr(_str_moduleRigNull,'gutsLock',lock=False).doConnectOut("%s.%s"%(_str_moduleRigNull,'overrideDisplayType'))    

    #log.debug("%s >> Time >> = %0.3f seconds " % (_str_funcName,(time.clock()-start)) + "-"*75)   
    
   
    #>>> Object Set -----------------------------------------------------------------------------------
    self._mi_module.__verifyObjectSet__()
    
    log.debug("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.3f seconds"%(time.clock()-_start)))            
    
    return _res
    

    
    
def _fncStep_moduleRigChecks_(self):
    #>>>Connect switches
    try: verify_moduleRigToggles(self)
    except Exception,error:raise Exception,"Module rig toggle fail | error: {0}".format(error)

    #>>> Object Set
    try: self._mi_module.__verifyObjectSet__()
    except Exception,error:raise Exception,"Object set fail | error: {0}".format(error)
    
    
def is_buildable(blockType = 'box'):
    """
    Function to check if a givin block module is buildable or not
    
    """
    _str_func = 'is_buildable'  
    
    if blockType not in _d_blockTypes.keys():
        log.warning("|{0}| >> [{1}] Module not in dict".format(_str_func,blockType))            
        return False
    
    _res = True
    _buildModule = _d_blockTypes[blockType]
    return _buildModule
    for a in _l_requiredModuleDat:
        if not _buildModule.__dict__.get(a):
            log.warning("|{0}| >> [{1}] Missing data: {2}".format(_str_func,blockType,a))
            _res = False
            
    if _res:return _buildModule
    return _res
            
def fnc_rigNeed(self):
    """
    Function to check if a go instance needs to be rigged
    
    """
    _str_func = 'fnc_rigNeed'  
    
    _mModule = self._d_module['mModule']    
    _mModuleParent = self._d_module['mModuleParent']
    _version = self._d_module['version']
    _buildVersion = self._d_block['buildVersion']
    
    _d_callKWS = self._call_kws
    
    if _mModuleParent:
        _str_moduleParent = _mModuleParent.getShortName()
        if not _mModuleParent.isRigged():
            log.warning("|{0}| >> [{1}] ModuleParent not rigged".format(_str_func,_str_moduleParent))            
            return False
        
    _b_rigged = _mModule.isRigged()
    log.debug("|{0}| >> Rigged: {1}".format(_str_func,_b_rigged))            
    
    if _b_rigged and not _d_callKWS['forceNew'] and _d_callKWS['ignoreRigCheck'] is not True:
        log.warning("|{0}| >> Already rigged and not forceNew".format(_str_func))                    
        return False
             
    _b_outOfDate = False
    if _version != _buildVersion:
        _b_outOfDate = True
        log.warning("|{0}| >> Versions don't match: rigNull: {1} | buildModule: {2}".format(_str_func,_version,_buildVersion))                            
    else:
        if _d_callKWS['forceNew'] and _mModule.isRigged():
            log.warning("|{0}| >> Force new and is rigged. Deleting rig...".format(_str_func))                    
            #_mModule.rigDelete()
        else:
            log.info("|{0}| >> Up to date.".format(_str_func))                    
            return False
    
    return True
    
    
def fnc_bufferDat(self):
    """
    Function to check if a go instance needs to be rigged
    
    """
    _str_func = 'fnc_bufferDat'  
    
    _mModule = self._d_module['mModule']    
    _mModuleParent = self._d_module['mModuleParent']
    _mPuppet = self._d_module['mPuppet']
    _mRigNull = self._d_module['mRigNull']
    _version = self._d_module['version']
    _buildVersion = self._d_block['buildVersion']
    
    _d_callKWS = self._call_kws
    
    #>>Module dat ------------------------------------------------------------------------------
    _d = {}
    _d['partName'] = _mModule.getPartNameBase()
    _d['partType'] = _mModule.moduleType.lower() or False
    
    _d['l_moduleColors'] = _mModule.getModuleColors() 
    _d['l_coreNames'] = []#...need to do this
    _d['mTemplateNull'] = _mModule.templateNull
    _d['bodyGeo'] = _mPuppet.getGeo() or ['Morphy_Body_GEO']
    _d['direction'] = _mModule.getAttr('cgmDirection')
    
    _d['mirrorDirection'] = _mModule.get_mirrorSideAsString()
    _d['f_skinOffset'] = _mPuppet.getAttr('skinDepth') or 1
    _d['mMasterNull'] = _mPuppet.masterNull
    
    #>MasterControl....
    if not _mPuppet.getMessage('masterControl'):
        log.info("|{0}| >> Creating masterControl...".format(_str_func))                    
        _mPuppet._verifyMasterControl(size = 5)
        
    _d['mMasterControl'] = _mPuppet.masterControl
    _d['mPlug_globalScale'] =  cgmMeta.cgmAttr(_d['mMasterControl'].mNode,'scaleY')	 
    _d['mMasterSettings'] = _d['mMasterControl'].controlSettings
    _d['mMasterDeformGroup'] = _mPuppet.masterNull.deformGroup
    
    _d['mMasterNull'].worldSpaceObjectsGroup.parent = _mPuppet.masterControl
      
    self._d_module.update(_d)
    
    cgmGEN.log_info_dict(self._d_module,_str_func + " moduleDat")      
    log.info(cgmGEN._str_subLine)
    

    #>>Joint dat ------------------------------------------------------------------------------
    _d = {}
    
    _d['ml_moduleJoints'] = _mRigNull.msgList_get('moduleJoints',cull=True)
    if not _d['ml_moduleJoints']:
        log.warning("|{0}| >> No module joints found".format(_str_func))                    
        return False
    
    _d['l_moduleJoints'] = []
    
    for mJnt in _d['ml_moduleJoints']:
        _d['l_moduleJoints'].append(mJnt.p_nameShort)
        ATTR.set(mJnt.mNode,'displayLocalAxis',0)
        
    _d['ml_skinJoints'] = _mModule.rig_getSkinJoints()
    if not _d['ml_skinJoints']:
        log.warning("|{0}| >> No skin joints found".format(_str_func))                    
        return False      
    
    
    self._d_joints = _d
    cgmGEN.log_info_dict(self._d_joints,_str_func + " jointsDat")      
    log.info(cgmGEN._str_subLine)    
    
    #>>Orientation dat ------------------------------------------------------------------------------
    _d = {}
    
    _mOrientation = VALID.simpleOrientation('zyx')#cgmValid.simpleOrientation(str(modules.returnSettingsData('jointOrientation')) or 'zyx')
    _d['str'] = _mOrientation.p_string
    _d['vectorAim'] = _mOrientation.p_aim.p_vector
    _d['vectorUp'] = _mOrientation.p_up.p_vector
    _d['vectorOut'] = _mOrientation.p_out.p_vector
    
    _d['vectorAimNeg'] = _mOrientation.p_aimNegative.p_vector
    _d['vectorUpNeg'] = _mOrientation.p_upNegative.p_vector
    _d['vectorOutNeg'] = _mOrientation.p_outNegative.p_vector    
    
    self._d_orientation = _d
    cgmGEN.log_info_dict(self._d_orientation,_str_func + " orientationDat")      
    log.info(cgmGEN._str_subLine)    
    
    return True
    
    """
    try:#Master control ---------------------------------------------------------
        self._i_masterControl = self._mi_module.modulePuppet.masterControl
        self.mPlug_globalScale = cgmMeta.cgmAttr(self._i_masterControl.mNode,'scaleY')	    
        self._i_masterSettings = self._i_masterControl.controlSettings
        self._i_masterDeformGroup = self._mi_module.modulePuppet.masterNull.deformGroup	 
    except Exception,error:raise Exception,"Master control | error: {0}".format(error)


    #>>> Some place holders ----------------------------------------------------	    
    self._md_controlShapes = {}    
    """
    

    
    


   
    
    
    
    






