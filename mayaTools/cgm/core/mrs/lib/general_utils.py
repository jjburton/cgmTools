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
from cgm.core.cgmPy import validateArgs as VALID
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

def validate_stateArg(stateArg = None,):
    """
    returns [stateIndex,stateName]  
    """
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
    return [stateIndex,stateName]  

def get_from_scene():
    """
    Gather all rig blocks data in scene

    :parameters:

    :returns
        metalist(list)
    """
    _str_func = 'get_from_scene'
    
    _ml_rigBlocks = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',nTypes=['transform','network'])
    
    return _ml_rigBlocks

def get_scene_block_heirarchy(asMeta = True):
    _str_func = 'get_scene_block_heirarchy'

    _md_heirachy = {}
    _ml_rigBlocks = r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',nTypes=['transform','network'])
    
    for mBlock in _ml_rigBlocks:#...find our roots
        if not mBlock.p_blockParent:
            log.debug("|{0}| >> Root: {1}".format(_str_func,mBlock.mNode))    
            if asMeta:
                k = mBlock
            else:
                k = mBlock.mNode
            _md_heirachy[k] = mBlock.getBlockHeirarchyBelow(asMeta = asMeta)

    #cgmGEN.walk_dat(_md_heirachy, _str_func)
    return _md_heirachy


_d_scrollList_shorts = {'left':'L',
                        'right':'R',
                        'center':'C',
                        'front':'FRNT',
                        'define':'def',
                        'template':'tmp',
                        'prerig':'pre',
                        'skeleton':'skl'}
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
    try:
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
            return [],[]
            
        d_keys_to_idx = {}
        d_idx_to_keys = {}
        l_mNodeKeys = []
        for i,k in enumerate(l_keys):
            l_mNodeKeys.append(k.mNode)
            d_keys_to_idx[k.mNode] = i
            d_idx_to_keys[i] = k
            
        l_mNodeKeys.sort()
        l_keys = []#.reset and fill...
        for KmNode in l_mNodeKeys:
            l_keys.append( d_idx_to_keys[ d_keys_to_idx[KmNode]] )
            
        
        counter+=1
        
        for k in l_keys:
            try:
            
                mBlock = k
                #>>>Build strings
                _short = mBlock.p_nameShort
                #log.debug("|{0}| >> scroll list update: {1}".format(_str_func, _short))  
        
                _l_report = []
        
                _l_parents = mBlock.getBlockParents(False)
                log.debug("{0} : {1}".format(mBlock.mNode, _l_parents))
                
                _len = len(_l_parents)
                
                if _len:
                    s_start = ' '*_len +' '
                else:
                    s_start = ''
                    
                if counter == 1:
                    s_start = s_start + " "            
                else:
                    #s_start = s_start + '-[{0}] '.format(counter-1)
                    s_start = s_start + '  ^-' + '--'*(counter-1) + ' '
                    
                
                if mBlock.getMayaAttr('position'):
                    _v = mBlock.getMayaAttr('position')
                    if _v.lower() not in ['','none']:
                        _l_report.append( _d_scrollList_shorts.get(_v,_v) )
                    
                if mBlock.getMayaAttr('side'):
                    _v = mBlock.getEnumValueString('side')
                    _l_report.append( _d_scrollList_shorts.get(_v,_v))
                    
                l_name = []
                _cgmName = mBlock.getMayaAttr('cgmName')
                if _cgmName:
                    l_name.append(_cgmName)
                l_name.append( ATTR.get(_short,'blockType').capitalize() )
                
                _l_report.append(''.join(l_name))
                    
                #_l_report.append(ATTR.get(_short,'blockState'))
                if mBlock.getMayaAttr('isBlockFrame'):
                    _l_report.append("[FRAME]")
                else:
                    _blockState = _d_scrollList_shorts.get(mBlock.blockState,mBlock.blockState)
                    _l_report.append("[{0}]".format(_blockState.upper()))
                
                """
                if mObj.hasAttr('baseName'):
                    _l_report.append(mObj.baseName)                
                else:
                    _l_report.append(mObj.p_nameBase)"""                
            
                if mBlock.isReferenced():
                    _l_report.append("Referenced")
                    
        
                _str = s_start + " - ".join(_l_report)
                log.debug(_str + "   >> " + mBlock.mNode)
                #log.debug("|{0}| >> str: {1}".format(_str_func, _str))      
                stringList.append(_str)        
                blockList.append(mBlock)
         
                buffer = arg[k]
                if buffer:
                    get_uiScollList_dat(buffer,k,counter,blockList,stringList)   
                    
        
                    """if counter == 0:
                        print('> {0} '.format(mBlock.mNode))			                	            
                    else:
                        print('-'* counter + '> {0} '.format(mBlock.mNode) )"""	
            except Exception,err:
                log.error("Failed: {0} | {1}".format(k, err))
                log.error("List: {0}".format(_l_report))
                
    
        return blockList,stringList
    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
def walk_rigBlock_heirarchy(mBlock,dataDict = None, asMeta = True,l_processed = None):
    """
    
    https://stackoverflow.com/questions/22241679/display-hierarchy-of-selected-object-only    
    """
    #def walk_down(mBlock,dataDict,asMeta):
        
    _str_func = 'walk_rigBlock_heirarchy'
    
    mBlock = cgmMeta.validateObjArg(mBlock,'cgmRigBlock')
    log.debug("|{0}| >> mBlock: {1}".format(_str_func,mBlock.mNode)  )      
    
    if not mBlock:
        raise ValueError,"No block"
    
    if dataDict is None:
        dataDict = {}
    if l_processed is None:
        l_processed = []
        
    if mBlock in l_processed:
        log.debug("|{0}| >> Already processed: {1}".format(_str_func,mBlock.mNode)  )      
        return    
    
    else:l_processed.append(mBlock)
                
    if not asMeta:
        key = mBlock.mNode
    else:
        key = mBlock
        
    ml_children = mBlock.getBlockChildren(asMeta) or []
    
    if not dataDict.get(key):
        dataDict[key] = {} 
    else:
        log.debug("|{0}| >> Already processed key: {1}".format(_str_func,key)  )      
        return
    
    log.debug("|{0}| >> [{1}] Children: {2} | {3}".format(_str_func,key,len(ml_children),ml_children))
 
    for mChild in ml_children:
        #if not dataDict[key].get(mChild):
            #dataDict[key][mChild] = {}   
        """if dataDict[key].get(mChild):
            log.info("|{0}| >> Already processed child key: {1}".format(_str_func,mChild)  )      
            continue
        dataDict[key][mChild] = {}"""
        walk_rigBlock_heirarchy(mChild,dataDict[key],asMeta,l_processed)
    
    #cgmGEN.walk_dat(dataDict)
    return dataDict

def get_rigBlock_heirarchy_context(mBlock, context = 'below', asList = False, report = True):
    """

    Get a contextual heirarchal dict/list of an mBlock. 
    
    :parameters:
        mBlock(str): RigBlock
        context(str):
            self
            below
            root
            scene
            
        asList(bool): Whether you want an ordered list or a dict
        report(bool): Reports the data in a useful format

    :returns
        parents(list)
           
    """
    #def walk_down(mBlock,dataDict,asMeta):
        
    _str_func = 'get_rigBlock_heirarchy_context'
    
    #blocks = VALID.listArg(mBlock)
    ml_blocksRaw = cgmMeta.validateObjListArg(mBlock)
    #mBlock = cgmMeta.validateObjArg(mBlock,'cgmRigBlock')
    _res = {}
    
    if context == 'scene':
        _res = get_scene_block_heirarchy()
    elif context == 'root':
        ml_roots = []
        for mObj in ml_blocksRaw:
            _root = mObj.p_blockRoot
            if not _root:
                if mObj not in ml_roots:
                    ml_roots.append(mObj)
            else:
                mRoot = mObj.p_blockRoot
                if mRoot not in ml_roots:ml_roots.append(mRoot)
                
        for mRoot in ml_roots:
            _res.update( walk_rigBlock_heirarchy(mRoot))

    elif context in ['self','below']:
        for mObj in ml_blocksRaw:
            log.debug("|{0}| >> mBlock: {1} | context: {2}".format(_str_func,mObj.mNode,context)  )  
            if context == 'self':
                _res.update({mObj:{}})
            elif context == 'below':
                _res.update(walk_rigBlock_heirarchy(mObj))

    else:
        raise ValueError,"|{0}| >> unknown context: {1}".format(_str_func,context)
        
    if report:
        log.debug("|{0}| >> report...".format(_str_func))        
        #cgmGEN.walk_dat(_res,"Walking rigBLock: {0} | context: {1}".format(mBlock.mNode,context))
        print_heirarchy_dict(_res,"Walking context: {0}".format(context))
        
    if asList:
        log.debug("|{0}| >> asList...".format(_str_func))
        return cgmGEN.walk_heirarchy_dict_to_list(_res)
    return _res

def print_heirarchy_dict(arg = None, tag = None, counter = 0):
    '''
    Log a dictionary.

    :parameters:
    arg | dict
    tag | string
    label for the dict to log.

    :raises:
    TypeError | if not passed a dict
    '''
    if isinstance(arg,dict):
        l_keys = arg.keys()
        _int = int(counter+1/2)
        if counter == 0:
            print('# {0} '.format(tag) + cgmGEN._str_hardLine)	
        elif counter == 1:
            print('{0} '.format(tag))	
        else:
            print(' '* (_int*2) + ' |'+'_'* 2 + ' {0} '.format(tag))
            #print('-'* counter + '> {0} '.format(tag))		            
        #else:
            #print(' '* _int + '|||'+'_'* _int + ' {0} '.format(tag) + cgmGEN._str_subLine)		
    
   
        counter +=1
            
        l_keys.sort()
        for k in l_keys:
            try:str_key = k.p_nameShort
            except:str_key = k
            buffer = arg[k]          
            print_heirarchy_dict(buffer,str_key,counter)
    else:
        if counter == 0:
            print('{0} : '.format(tag) + str(arg))			                
        else:
            print(' '* counter + ' {0} : '.format(tag) + str(arg))			                

    return   
