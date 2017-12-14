"""
------------------------------------------
block: cgm.core.mrs.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

These are functions with self assumed to be a cgmRigBlock
================================================================
"""
import random
import re
import copy
import time
import os
import pprint
import sys
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

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
import cgm.core.classes.NodeFactory as NODEFACTORY
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.cgmPy import path_Utils as PATH
import cgm.core.rig.joint_utils as COREJOINTS
import cgm.core.lib.transform_utils as TRANS

#=============================================================================================================
#>> Queries
#=============================================================================================================

def example(self):
    try:
        _short = self.p_nameShort
        _str_func = ' example [{0}]'.format(self)
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def modules_get(self):
    try:
        _str_func = ' modules_get [{0}]'.format(self)
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        
        try:ml_initialModules = self._mi_puppet.moduleChildren
        except:ml_initialModules = []
        
        int_lenModules = len(ml_initialModules)  
    
        ml_allModules = copy.copy(ml_initialModules)
        for i,m in enumerate(ml_initialModules):
            _str_module = m.p_nameShort
            self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)
            #for m in m.get_allModuleChildren():
                #if m not in ml_allModules:
                    #ml_allModules.append(m)
        #self.i_modules = ml_allModules
        return ml_allModules        
     
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
    
#=============================================================================================================
#>> Mirror
#=============================================================================================================
def mirror_getNextIndex(self,side):
    try:
        _str_func = ' mirror_getNextIndex [{0}]'.format(self)
        log.debug("|{0}| >> ...".format(_str_func)+ '-'*80)
        
        l_return = []
        ml_modules = modules_get(self)
        int_lenModules = len(ml_modules)
        
        for i,mModule in enumerate(ml_modules):
            #self.log_info("Checking: '%s'"%mModule.p_nameShort)
            _str_module = mModule.p_nameShort
            if mModule.get_mirrorSideAsString() == self.str_side :
                #self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)		    				    
                #self.log_info("Match Side '%s' >> '%s'"%(self.str_side,_str_module))		    
                try:mi_moduleSet = mModule.rigNull.moduleSet.getMetaList()
                except:mi_moduleSet = []
                for mObj in mi_moduleSet:
                    int_side = mObj.getAttr('mirrorSide')
                    int_idx = mObj.getAttr('mirrorIndex')
                    str_side = mObj.getEnumValueString('mirrorSide')		    
                    l_return.append(int_idx)
                    l_return.sort()

        if l_return:
            return max(l_return)+1
        else:return 0        
     
    except Exception,err:cgmGEN.cgmException(Exception,err)
