"""
------------------------------------------
builder_utils: cgm.core.mrs.lib
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
import os

#From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
#from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#========================================================================

import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core.mrs.lib import shared_dat as BLOCKSHARED
from cgm.core import cgm_Meta as cgmMeta
#from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
#from cgm.core.lib import position_utils as POS
#from cgm.core.lib import math_utils as MATH
#from cgm.core.lib import distance_utils as DIST
#from cgm.core.lib import snap_utils as SNAP
#from cgm.core.lib import rigging_utils as RIGGING
#from cgm.core.rigger.lib import joint_Utils as JOINTS
#from cgm.core.lib import search_utils as SEARCH
#from cgm.core.lib import rayCaster as RAYS
#from cgm.core.cgmPy import validateArgs as VALID
#from cgm.core.cgmPy import path_Utils as PATH
#from cgm.core.cgmPy import os_Utils as cgmOS

def validate_stateArg(stateArg = None):
    _str_func = 'valid_stateArg'
    _failMsg = "|{0}| >> Invalid: {1} | valid: {2}".format(_str_func,stateArg,BLOCKSHARED._l_blockStates)
    
    if type(stateArg) in [str,unicode]:
        stateArg = stateArg.lower()
        if stateArg in BLOCKSHARED._l_blockStates:
            stateIndex = BLOCKSHARED._l_blockStates.index(stateArg)
            stateName = stateArg
        else:            
            log.warning(_failMsg)
            return False
    elif type(stateArg) is int:
        if stateArg<= len(BLOCKSHARED._l_blockStates)-1:
            stateIndex = stateArg
            stateName = BLOCKSHARED._l_blockStates[stateArg]         
        else:
            log.warning(_failMsg)
            return False        
    else:
        log.warning(_failMsg)        
        return False
    return stateIndex,stateName  

def get_from_scene():
    """
    Gather all rig blocks data in scene

    :parameters:

    :returns
        metalist(list)
    """
    _str_func = 'get_from_scene'
    
    _ml_rigBlocks = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock')
    
    return _ml_rigBlocks

def get_scene_block_heirarchy(asMeta = True):
    _str_func = 'get_scene_block_heirarchy'

    _md_heirachy = {}
    _ml_rigBlocks = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock')
    
    for mBlock in _ml_rigBlocks:#...find our roots
        if not mBlock.p_blockParent:
            log.info("|{0}| >> Root: {1}".format(_str_func,mBlock.mNode))    
            if asMeta:
                k = mBlock
            else:
                k = mBlock.mNode
            _md_heirachy[k] = mBlock.getBlockHeirarchyBelow(asMeta = asMeta)

    #cgmGEN.walk_dat(_md_heirachy, _str_func)
    return _md_heirachy


def get_uiScollList_dat(arg = None, tag = None, counter = 0, blockList=None, stringList=None):
    '''
    Log a dictionary.

    :parameters:
    arg | dict
    tag | string
    label for the dict to log.

    :raises:
    TypeError | if not passed a dict
    '''
    _str_func = 'walk_blockDict'
    
    if arg == None:
        arg = get_scene_block_heirarchy(True)
        
    if not isinstance(arg,dict):
        raise ValueError, "need dict: {0}".format(arg)
    
    if blockList is None:
        blockList = []
    if stringList is None:
        stringList = []
        
    l_keys = arg.keys()
    if not l_keys:
        return False
        
    l_keys.sort()
    counter+=1
    
    for k in l_keys:
        mBlock = k
    
        #>>>Build strings
        _short = mBlock.p_nameShort
        #log.info("|{0}| >> scroll list update: {1}".format(_str_func, _short))  

        _l_report = []

        #_l_parents = mBlock.getBlockParents(True)

        #log.info("{0} : {1}".format(mBlock.mNode, _l_parents))

        s_start = ''
        #_len = len(_l_parents)
        if counter:
            if counter == 1:
                s_start = ">"            
            else:
                s_start = "-"*counter + '>'

        if mBlock.getMayaAttr('position'):
            _l_report.append( mBlock.getEnumValueString('position') )
        if mBlock.getMayaAttr('direction'):
            _l_report.append( mBlock.getEnumValueString('direction') )

        _l_report.append( ATTR.get(_short,'blockType') )
        if mBlock.hasAttr('puppetName'):
            _l_report.append(mBlock.puppetName)   
        #_l_report.append(ATTR.get(_short,'blockState'))
        _l_report.append("[{0}]".format(mBlock.getState()))

        """
        if mObj.hasAttr('baseName'):
            _l_report.append(mObj.baseName)                
        else:
            _l_report.append(mObj.p_nameBase)"""                
    
        if mBlock.isReferenced():
            _l_report.append("Referenced")

        _str = s_start + " - ".join(_l_report)
        print _str
        #log.info("|{0}| >> str: {1}".format(_str_func, _str))      
        stringList.append(_str)        
        blockList.append(mBlock)
 
        buffer = arg[k]
        if buffer:
            get_uiScollList_dat(buffer,k,counter,blockList,stringList)   
            

    """if counter == 0:
        print('> {0} '.format(mBlock.mNode))			                	            
    else:
        print('-'* counter + '> {0} '.format(mBlock.mNode) )"""	
        
   

    
                            

    return blockList,stringList

def walk_rigBlockHeirarchyDict(mBlock,dataDict = None, asMeta = True):
    """
    
    https://stackoverflow.com/questions/22241679/display-hierarchy-of-selected-object-only    
    """
    #def walk_down(mBlock,dataDict,asMeta):
        
    _str_func = 'walk_rigBlockHeirarchyDict'
    mBlock = cgmMeta.validateObjArg(mBlock,'cgmRigBlock')
    
    if not mBlock:
        raise ValueError,"No block"
    if dataDict is None:
        dataDict = {}
    if not asMeta:
        key = mBlock.mNode
    else:
        key = mBlock
        
    ml_children = mBlock.getBlockChildren(asMeta) or []
    
    if not dataDict.get(key):
        dataDict[key] = {}        
        for k in ml_children:
            dataDict[key][k] = {}
    
    log.debug("|{0}| >> [{1}] Children: {2}".format(_str_func,key,ml_children))
        
    for mChild in ml_children:
        walk_rigBlockHeirarchyDict(mChild,dataDict[key] ,asMeta)
    
    #cgmGEN.walk_dat(dataDict)
    return dataDict
