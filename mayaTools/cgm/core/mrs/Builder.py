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
        self._d_dat_rigBlock = {}
        self._d_dat_module = {}

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
            
        if not fnc_check_module(self):
            raise RuntimeError,"|{0}| >> Module checks failed. See warnings and errors.".format(_str_func)
        
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
    
    if not self._call_kws['rigBlock']:
        log.error("|{0}| >> No rigBlock stored in call kws".format(_str_func))
        return False
    
    mFactory = RIGBLOCKS.factory(self._call_kws['rigBlock'])
    
    mFactory.verify()
    mFactory.module_verify()
    mFactory.puppet_verify()
    
    return True
    
        
def fnc_check_module(self):
    _str_func = 'fnc_check_module'  
    
    return True
    assert self.d_kws['mModule'].isModule(),"Not a module"
    self._mi_module = self.d_kws['mModule']# Link for shortness
    self._i_rigNull = self._mi_module.rigNull#speed link

    self._strShortName = self._mi_module.getShortName() or False	    
    self._str_funcName = "{0}('{1}')".format(self._str_funcName,self._strShortName)
    self.__updateFuncStrings__()

    self._i_puppet = self._mi_module.modulePuppet
    self._i_puppet.__verifyGroups__()

    self._mi_moduleParent = False
    if self._mi_module.getMessage('moduleParent'):
        self._mi_moduleParent = self._mi_module.moduleParent    
    pass

   
    
    
    
    






