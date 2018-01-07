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
        _str_func = ' example'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def get_shapeOffset(self):
    """
    Get the shape offset value 
    """
    try:
        _str_func = ' get_shapeOffset'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        l_attrs = ['loftOffset','skinOffset']
        for a in l_attrs:
            if self.hasAttr(a):
                v = self.getMayaAttr(a)
                log.debug("|{0}| >> {1} attr found: {2}".format(_str_func,a,v))                
                return v
        
        if self.getMessage('masterControl'):
            log.debug("|{0}| >> Master control found...".format(_str_func))
            _bb = DIST.get_bb_size(self.getMessage('masterControl'))
            return MATH.average(_bb[0],_bb[2])/50
            
        log.debug("|{0}| >> default return".format(_str_func))
        return 1
        
        
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def modules_get(self):
    try:
        _str_func = ' modules_get'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        try:ml_initialModules = self.moduleChildren
        except:ml_initialModules = []
        
        int_lenModules = len(ml_initialModules)  
    
        ml_allModules = copy.copy(ml_initialModules)
        for i,m in enumerate(ml_initialModules):
            log.debug("|{0}| >> checking: {1}".format(_str_func,m))
            _str_module = m.p_nameShort
            for m in m.get_allModuleChildren():
                if m not in ml_allModules:
                    ml_allModules.append(m)
                    
        return ml_allModules        
     
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def modules_gather(self,**kws):
    try:
        _short = self.p_nameShort
        _str_func = ' modules_gather'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        ml_modules = modules_get(self)
        int_lenModules = len(ml_modules)
    
        for i,mModule in enumerate(ml_modules):
            _str_module = mModule.p_nameShort
            module_connect(self,mModule,**kws)
        return ml_modules
    except Exception,err:cgmGEN.cgmException(Exception,err)
    
def module_connect(self,mModule,**kws):
    try:
        _short = self.p_nameShort
        _str_func = ' module_connect'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        ml_buffer = copy.copy(self.getMessage('moduleChildren',asMeta=True)) or []#Buffer till we have have append functionality	
            #self.i_masterNull = self.masterNull
        

        mModule = cgmMeta.validateObjArg(mModule,'cgmRigModule')


        if mModule not in ml_buffer:
            ml_buffer.append(mModule)
            self.__setMessageAttr__('moduleChildren',[mObj.mNode for mObj in ml_buffer]) #Going to manually maintaining these so we can use simpleMessage attr  parents
        
        mModule.modulePuppet = self.mNode

        mModule.parent = self.masterNull.partsGroup.mNode
    
        if mModule.getMessage('moduleMirror'):
            log.debug("|{0}| >> moduleMirror found. connecting...".format(_str_func))
            module_connect(self,mi_module.moduleMirror)        
    
        return True        
       
    except Exception,err:cgmGEN.cgmException(Exception,err)
    

    
    
#=============================================================================================================
#>> Mirror
#=============================================================================================================
def mirror_getNextIndex(self,side):
    try:
        _str_func = ' mirror_getNextIndex'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        l_return = []
        ml_modules = modules_get(self)
        int_lenModules = len(ml_modules)
        str_side = cgmGEN.verify_mirrorSideArg(side)
        for i,mModule in enumerate(ml_modules):
            #self.log_info("Checking: '%s'"%mModule.p_nameShort)
            _str_module = mModule.p_nameShort
            if mModule.get_mirrorSideAsString() == str_side :
                #self.progressBar_set(status = "Checking Module: '%s' "%(_str_module),progress = i, maxValue = int_lenModules)		    				    
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
    
def mirror_getDict(self):
    try:
        _str_func = ' mirror_getDict'.format(self)
        log.debug("|{0}| >> ... [{1}]".format(_str_func,self)+ '-'*80)
        
        d_return = {}
        ml_modules = modules_get(self)
        int_lenModules = len(ml_modules)
    
        for i,mModule in enumerate(ml_modules):
            _str_module = mModule.p_nameShort
            try:mi_moduleSet = mModule.rigNull.moduleSet.getMetaList()
            except:mi_moduleSet = []
            for mObj in mi_moduleSet:
    
                if mObj.hasAttr('mirrorSide') and mObj.hasAttr('mirrorIndex'):
                    int_side = mObj.getAttr('mirrorSide')
                    int_idx = mObj.getAttr('mirrorIndex')
                    str_side = mObj.getEnumValueString('mirrorSide')
    
                    if not d_return.get(int_side):
                        d_return[int_side] = []
    
                    if int_idx in d_return[int_side]:
                        pass
                        #self.log_debug("%s mModule: %s | side: %s | idx :%s already stored"%(self._str_reportStart,_str_module, str_side,int_idx))
                    else:
                        d_return[int_side].append(int_idx)
        return d_return
     
    except Exception,err:cgmGEN.cgmException(Exception,err)