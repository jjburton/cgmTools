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
        self._d_dat_block = {}
        self._d_dat_module = {}

        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:#...intial population
            self._call_kws = kws
            #log.debug("|{0}| >> kws: {1}".format(_str_func,kws))
        
        self._call_kws['forceNew'] = forceNew
        self._call_kws['rigBlock'] = rigBlock
        self._call_kws['autoBuild'] = autoBuild
        self._call_kws['ignoreRigCheck'] = ignoreRigCheck
        #cgmGEN.log_info_dict(self._call_kws,_str_func)
        
        if not fnc_check_rigBlock(self):
            raise RuntimeError,"|{0}| >> RigBlock checks failed. See warnings and errors.".format(_str_func)
            
        if not fnc_check_module(self):
            raise RuntimeError,"|{0}| >> Module checks failed. See warnings and errors.".format(_str_func)
        
        if not fnc_rigNeed(self):
            raise RuntimeError,"|{0}| >> No rig need see errors".format(_str_func)
            
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

    self._d_dat_block = _d    
    cgmGEN.log_info_dict(_d,_str_func + " blockDat")   
    
    return True
    

def fnc_check_module(self):
    _str_func = 'fnc_check_module'  
    _res = True
    BlockFactory = self._d_dat_block['mFactory']
    
    #>>Module -----------------------------------------------------------------------------------  
    _d = {}    
    BlockFactory.module_verify()
    _mModule = BlockFactory._mi_module
    _d['mModule'] = _mModule
    _d['mRigNull'] = _mModule.rigNull
    _d['shortName'] = _mModule.getShortName()
    
    _d['mModuleParent'] = False
    if _mModule.getMessage('moduleParent'):
        _d['mModuleParent'] = _mModule.moduleParent
        
    #>>Puppet -----------------------------------------------------------------------------------    
    BlockFactory.puppet_verify()
    _mPuppet = _mModule.modulePuppet
    _d['mPuppet'] = _mPuppet
    _mPuppet.__verifyGroups__()
    
    if not _mModule.isSkeletonized():
        log.warning("|{0}| >> Module isn't skeletonized. Attempting".format(_str_func))
        
        BlockFactory.skeletonize(True)
        if not _mModule.isSkeletonized():
            log.warning("|{0}| >> Skeletonization failed".format(_str_func))            
            _res = False
    
    self._d_dat_module = _d    
    cgmGEN.log_info_dict(_d,_str_func + " moduleDat")    
    return _res    
    
    
    
    
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
    
    _mModule = self._d_dat_module['mModule']    
    _mModuleParent = self._d_dat_module['mModuleParent']
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
        
    #if not is_buildable
     
    _b_outOfDate = False
    
    return True
    
    
    """
    if self._mi_moduleParent:
                if not self._mi_moduleParent.isRigged():
                    raise StandardError,"'module parent is not rigged yet: '{0}'".format(self._mi_moduleParent.getShortName())

            #Then we want to see if we have a moduleParent to see if it's rigged yet
            __b_rigged = self._mi_module.isRigged()
            if __b_rigged and not self._b_forceNew and self._b_ignoreRigCheck is not True:
                return self._SuccessReturn_("Aready rigged and not forceNew")

            if not isBuildable(self):
                raise StandardError,"The builder for module type '{0}' is not ready".format(self._partType)

            try:
                self._outOfDate = False
                if self._version != self._buildVersion:
                    self._outOfDate = True	    
                    self.log_warning("Rig version out of date: {0} != {1}".format(self._version,self._buildVersion))	
                else:
                    if self._b_forceNew and self._mi_module.isRigged():
                        self._mi_module.rigDelete()
                    self.log_debug("Rig version up to date !")
            except Exception,error:raise Exception,"Version check fail | error: {0}".format(error)    
    
    """

    
    


   
    
    
    
    






