"""
------------------------------------------
builder_utils: cgm.core.mrs.lib
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
__MAYALOCAL = 'BLOCKGEN'

import random
import re
import copy
import time
import os
import pprint

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
from cgm.core.classes import GuiFactory as CGMUI
import cgm.core.lib.string_utils as STR
from cgm.core.lib import attribute_utils as ATTR

#from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
#from cgm.core.lib import position_utils as POS
#from cgm.core.lib import math_utils as MATH
#from cgm.core.lib import distance_utils as DIST
#from cgm.core.lib import snap_utils as SNAP
#from cgm.core.lib import rigging_utils as RIGGING
#from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
#from cgm.core.lib import rayCaster as RAYS
#from cgm.core.cgmPy import validateArgs as VALID
#from cgm.core.cgmPy import path_Utils as PATH
#from cgm.core.cgmPy import os_Utils as cgmOS
from cgm.core.cgmPy import path_Utils as PATH


def verify_sceneBlocks():
    """
    Gather all rig blocks data in scene

    :parameters:

    :returns
        metalist(list)
    """
    _str_func = 'verify_sceneBlocks'
    
    for mBlock in r9Meta.getMetaNodes(mTypes = 'cgmRigBlock',nTypes=['transform','network']):
        mBlock.atUtils('verify_blockAttrs',queryMode=False)
        

def get_orphanedRigModules(select = True, delete=False):
    """
    Find all rigModules that have no rigBlock connected

    :parameters:

    :returns
        metalist(list)
    """
    ml = []
    for mObj in r9Meta.getMetaNodes(mTypes = 'cgmRigModule',nTypes=['transform','network']):
        if not mObj.getMessageAsMeta('rigBlock'):
            ml.append(mObj) 
            
    if select and ml:
        mc.select([mObj.mNode for mObj in ml])

    if delete and ml:
        mc.delete([mObj.mNode for mObj in ml])
    
        
    return ml or log.warning("No orphaned rigModules  found.")


def block_getFromSelected(multi=False,sort=True):
    _str_func = 'block_getFromSelected'
    _res = []
    
    mL = cgmMeta.asMeta(sl=1,noneValid=True) or []
    for mObj in mL:
        if mObj.getMayaAttr('mClass') == 'cgmRigBlock':
            if not multi:
                return mObj
            else:
                _res.append(mObj)
        
        _found = SEARCH.seek_upStream(mObj.mNode,matchAttrValue = {'mClass':'cgmRigBlock'})
        log.info(_found)
        if _found:
            mObj = cgmMeta.asMeta(_found)            
            if not multi:
                return mObj
            else:
                if mObj not in _res:
                    _res.append(mObj)
                    
    if multi and _res:
        if sort:
            return sort_blockList_by_parentLen(_res)
        return _res
    
    return False

        
    
        

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


def get_scene_module_heirarchy(asMeta = True):
    _str_func = 'get_scene_module_heirarchy'

    _md_heirachy = {}
    _ml_puppets = r9Meta.getMetaNodes(mTypes = ['cgmRigPuppet'],nTypes=['transform','network'])
    
    for mPuppet in _ml_puppets:#...find our roots
        if asMeta:
            k = mPuppet
        else:
            k = mPuppet.mNode
        
        ml_initialModules = mPuppet.UTILS.modules_get(mPuppet)
        
        if not ml_initialModules:
            _md_heirachy[k] = {}
        else:
            _md_heirachy[k] = get_puppet_heirarchy_context(ml_initialModules[0],'root',asList=False,report=False)

    #cgmGEN.walk_dat(_md_heirachy, _str_func)
    return _md_heirachy


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
                        'rear':'REAR',
                        'upper':'UPR',
                        'lower':'LWR',
                        'back':'BCK',
                        'front':'FRNT',
                        'define':'def',
                        'form':'frm',
                        'prerig':'pre',
                        'bottom':'BTM',
                        'skeleton':'skl'}

def get_uiScollList_dat(arg = None, tag = None, counter = 0, blockList=None, stringList=None, showSide = True, presOnly = False, showState=True,showProfile =False):
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
                    #s_start = s_start + ' ^-' + '--'*(counter-1) + ' '
                    s_start = s_start + ' ' + '  '*(counter-1) + ' '
                
                if presOnly:
                    _str = copy.copy(s_start)
                else:
                    if showSide:
                        if mBlock.getMayaAttr('side'):
                            _v = mBlock.getEnumValueString('side')
                            _l_report.append( _d_scrollList_shorts.get(_v,_v))
                        
                    if mBlock.getMayaAttr('position'):
                        _v = mBlock.getMayaAttr('position')
                        if _v.lower() not in ['','none']:
                            _l_report.append( _d_scrollList_shorts.get(_v,_v) )
                            
                                                
                    l_name = []
                    
                    #l_name.append( ATTR.get(_short,'blockType').capitalize() )
                    _cgmName = mBlock.getMayaAttr('cgmName')
                    l_name.append('"{0}"'.format(_cgmName))
    
                    #_l_report.append(STR.camelCase(' '.join(l_name)))
                    _l_report.append(' - '.join(l_name))
                    
                        
                    #_l_report.append(ATTR.get(_short,'blockState'))
                    if showState:
                        if mBlock.getMayaAttr('isBlockFrame'):
                            _l_report.append("[FRAME]")
                        else:
                            _state = mBlock.getEnumValueString('blockState')
                            _blockState = _d_scrollList_shorts.get(_state,_state)
                            _l_report.append("[{0}]".format(_blockState.upper()))
                    
                    """
                    if mObj.hasAttr('baseName'):
                        _l_report.append(mObj.baseName)                
                    else:
                        _l_report.append(mObj.p_nameBase)"""                
                
                    if mBlock.isReferenced():
                        _l_report.append("Referenced")
                        
                    _str = s_start + " | ".join(_l_report)
                    
                    
                    #Block dat
                    l_block = []
                    _blockProfile = mBlock.getMayaAttr('blockProfile')
                    l_block.append(ATTR.get(_short,'blockType').capitalize())
                    
                    if _blockProfile and showProfile:
                        if _cgmName in _blockProfile:
                            _blockProfile = _blockProfile.replace(_cgmName,'')
                        _blockProfile= STR.camelCase(_blockProfile)                    
                        l_block.append(_blockProfile)
                        
                        _str = _str + (' - [{0}]'.format("-".join(l_block)))
                    else:
                        _str = _str + "| [{}]".format(l_block[0])
                    
                        
        
                log.debug(_str + "   >> " + mBlock.mNode)
                #log.debug("|{0}| >> str: {1}".format(_str_func, _str))      
                stringList.append(_str)        
                blockList.append(mBlock)
         
                buffer = arg[k]
                if buffer:
                    get_uiScollList_dat(buffer,k,counter,blockList,stringList,showSide,presOnly,showState,showProfile)   
                    
        
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
        

def get_uiModuleScollList_dat(arg = None, tag = None, counter = 0, blockList=None, stringList=None, showSide = True, presOnly = False):
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
        _str_func = 'get_uiModuleScollList_dat'
        
        if arg == None:
            arg = get_scene_module_heirarchy(True)
            
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
                
                if mBlock.mClass == 'cgmRigPuppet':
                    _l_parents = []
                else:
                    _l_parents = mBlock.UTILS.parentModules_get(mBlock)
                    
                log.debug("{0} : {1}".format(mBlock.mNode, _l_parents))
                
                _len = len(_l_parents)
                
                
                if _len:
                    s_start = '  '*_len +' '
                else:
                    s_start = ''
                    
                if counter == 1:
                    s_start = s_start + " "            
                else:
                    #s_start = s_start + '-[{0}] '.format(counter-1)
                    #s_start = s_start + '  ^-' + '--'*(counter-1) + ' '
                    s_start = s_start + ' ' + ' '*(counter-1) + ' '
                
                if presOnly:
                    _str = copy.copy(s_start)
                else:
                    if showSide:
                        _v = mBlock.getMayaAttr('cgmDirection')
                        if _v:
                            _l_report.append( _d_scrollList_shorts.get(_v,_v))
                        
                    _pos = mBlock.getMayaAttr('cgmPosition')
                    if _pos:
                        if _pos.lower() not in ['','none']:
                            _l_report.append( _d_scrollList_shorts.get(_pos,_pos) )
                            
                                                
                    l_name = []
                    
                    #l_name.append( ATTR.get(_short,'blockType').capitalize() )
                    _cgmName = mBlock.getMayaAttr('cgmName')
                    l_name.append('"{0}"'.format(_cgmName))
    
                    #_l_report.append(STR.camelCase(' '.join(l_name)))
                    _l_report.append(' - '.join(l_name))
                    

                    """
                    if mObj.hasAttr('baseName'):
                        _l_report.append(mObj.baseName)                
                    else:
                        _l_report.append(mObj.p_nameBase)"""                
                
                    if mBlock.isReferenced():
                        _l_report.append("Referenced")
                        
                    _str = s_start + " | ".join(_l_report)
 
        
                log.debug(_str + "   >> " + mBlock.mNode)
                #log.debug("|{0}| >> str: {1}".format(_str_func, _str))      
                stringList.append(_str)        
                blockList.append(mBlock)
         
                buffer = arg[k]
                if buffer:
                    get_uiModuleScollList_dat(buffer,k,counter,blockList,stringList,showSide,presOnly)   
                    
        
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

        
def walk_module_heirarchy(mModule,dataDict = None, asMeta = True,l_processed = None):
    """
    
    https://stackoverflow.com/questions/22241679/display-hierarchy-of-selected-object-only    
    """
    #def walk_down(mBlock,dataDict,asMeta):
        
    _str_func = 'walk_mModule_heirarchy'
    
    mModule = cgmMeta.validateObjArg(mModule,'cgmRigModule')
    log.debug("|{0}| >> mModule: {1}".format(_str_func,mModule.mNode)  )      
    
    if not mModule:
        raise ValueError,"No block"
    
    if dataDict is None:
        dataDict = {}
    if l_processed is None:
        l_processed = []
        
    if mModule in l_processed:
        log.debug("|{0}| >> Already processed: {1}".format(_str_func,mModule.mNode)  )      
        return    
    
    else:l_processed.append(mModule)
                
    if not asMeta:
        key = mModule.mNode
    else:
        key = mModule
        
    ml_children = mModule.moduleChildren or []
    
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
        walk_module_heirarchy(mChild,dataDict[key],asMeta,l_processed)
    
    #cgmGEN.walk_dat(dataDict)
    return dataDict
        
        
        
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
        return sort_blockList_by_parentLen(cgmGEN.walk_heirarchy_dict_to_list(_res))
    return _res

def sort_blockList_by_parentLen(ml = []):
    d = {}
    _res = []
    for mObj in ml:
        mParents = mObj.getBlockParents()
        _len = len(mParents)
        if not d.get(_len):
            d[_len] = []
            
        d[_len].append(mObj)
    
    _keys = d.keys()
    _keys.sort()
    _res = []
    for k in _keys:
        _res.extend(d[k])    
    return _res

def get_puppet_heirarchy_context(mModule, context = 'below', asList = False, report = True):
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
        
    _str_func = 'get_puppet_heirarchy_context'
    
    #blocks = VALID.listArg(mBlock)
    ml_modulesRaw = cgmMeta.validateObjListArg(mModule)
    #mBlock = cgmMeta.validateObjArg(mBlock,'cgmRigBlock')
    _res = {}
    
    if context == 'scene':
        raise NotImplementedError,'{0} || scene mode not done'.format(_str_func)
        _res = get_scene_block_heirarchy()
        
    elif context == 'root':
        ml_roots = []
        ml_puppets = []
        for mObj in ml_modulesRaw:
            if mObj.mClass == 'cgmRigPuppet':
                ml_puppets.append(mObj)
            else:
                mPuppet = mObj.modulePuppet
                if mPuppet not in ml_puppets:
                    ml_puppets.append(mPuppet)
        
        for mPuppet in ml_puppets:
            for mChild in mPuppet.UTILS.modules_get(mPuppet):
                if not mChild.moduleParent:
                    ml_roots.append(mChild)

                
        for mRoot in ml_roots:
            _res.update( walk_module_heirarchy(mRoot))

    elif context in ['self','below']:
        for mObj in ml_modulesRaw:
            log.debug("|{0}| >> mModule: {1} | context: {2}".format(_str_func,mObj.mNode,context)  )  
            if context == 'self':
                _res.update({mObj:{}})
            elif context == 'below':
                _res.update(walk_module_heirarchy(mObj))

    else:
        raise ValueError,"|{0}| >> unknown context: {1}".format(_str_func,context)
        
    if report:
        log.debug("|{0}| >> report...".format(_str_func))        
        #cgmGEN.walk_dat(_res,"Walking rigBLock: {0} | context: {1}".format(mBlock.mNode,context))
        print_heirarchy_dict(_res,"Walking context: {0}".format(context))
        
    if asList:
        log.debug("|{0}| >> asList...".format(_str_func))
        #reload(cgmGEN)
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

def patch_templateToForm():
    try:
        _str_func = 'patch_templateToForm'
        log.debug(cgmGEN.logString_start(_str_func))
        _l = mc.ls()
        _progressBar = CGMUI.doStartMayaProgressBar(stepMaxValue=len(_l))
        
        for i,o in enumerate(_l):
            _str = "{0} | {1} ".format(i,o)
            log.debug(cgmGEN.logString_sub(_str_func,_str))
            CGMUI.progressBar_set(_progressBar,step=1,
                                  status = _str)
            mObj = cgmMeta.asMeta(o)
            for a in mc.listAttr(o,ud=True) or []:
                log.debug(cgmGEN.logString_msg(_str_func,str(a)))
                if 'template' in a:
                    log.info(cgmGEN.logString_msg(_str_func,"{0} | {1} | template in".format(_str,a)))
                    ATTR.rename(o,a,a.replace('template','form'))
                elif 'Template' in a:
                    log.info(cgmGEN.logString_msg(_str_func,"{0} | {1} | Template in".format(_str,a)))
                    ATTR.rename(o,a,a.replace('Template','Form'))                    
                v = ATTR.get(o,a)
                if 'template' == str(v):
                    log.info(cgmGEN.logString_msg(_str_func,"{0} | {1} | template value".format(_str,str(a))))
                    ATTR.set(o,a,'form')


    except Exception,err:
        cgmGEN.cgmExceptCB(Exception,err)
    finally:
        CGMUI.doEndMayaProgressBar()


#====================================================================================	
#>> Utilities
#====================================================================================	
global CGM_RIGBLOCK_DAT
CGM_RIGBLOCK_DAT = None

def get_modules_dict(update=False):
    return get_modules_dat(update)[0]

#@cgmGEN.Timer
def get_modules_dat(update = False):
    """
    Data gather for available blocks.

    :parameters:

    :returns
        _d_modules, _d_categories, _l_unbuildable
        _d_modules(dict) - keys to modules
        _d_categories(dict) - categories to list of entries
        _l_unbuildable(list) - list of unbuildable modules
    """
    _str_func = 'get_modules_dict'    
    global CGM_RIGBLOCK_DAT

    if CGM_RIGBLOCK_DAT and not update:
        log.debug("|{0}| >> passing buffer...".format(_str_func))          
        return CGM_RIGBLOCK_DAT
    
    _b_debug = log.isEnabledFor(logging.DEBUG)

    import cgm.core.mrs.blocks as blocks
    _path = PATH.Path(blocks.__path__[0])
    _l_duplicates = []
    _l_unbuildable = []
    _base = _path.split()[-1]
    _d_files =  {}
    _d_modules = {}
    _d_import = {}
    _d_categories = {}

    log.info("|{0}| >> Checking base: {1} | path: {2}".format(_str_func,_base,_path))   
    _i = 0
    for root, dirs, files in os.walk(_path, True, None):
        # Parse all the files of given path and reload python modules
        _mBlock = PATH.Path(root)
        _split = _mBlock.split()
        _subRoot = _split[-1]
        _splitUp = _split[_split.index(_base):]

        log.debug("|{0}| >> On subroot: {1} | path: {2}".format(_str_func,_subRoot,root))   
        log.debug("|{0}| >> On split: {1}".format(_str_func,_splitUp))   

        if len(_split) == 1:
            _cat = 'base'
        else:_cat = _split[-1]
        _l_cat = []
        _d_categories[_cat]=_l_cat

        for f in files:
            key = False

            if f.endswith('.py'):

                if f == '__init__.py':
                    continue
                else:
                    name = f[:-3]    
            else:
                continue

            if _i == 'cat':
                key = '.'.join([_base,name])                            
            else:
                key = '.'.join(_splitUp + [name])    
                if key:
                    log.debug("|{0}| >> ... {1}".format(_str_func,key))                      
                    if name not in _d_modules.keys():
                        _d_files[key] = os.path.join(root,f)
                        _d_import[name] = key
                        _l_cat.append(name)
                        try:
                            module = __import__('cgm.core.mrs.{0}'.format(key), globals(), locals(), ['*'], -1)
                            #reload(module) 
                            _d_modules[name] = module
                            #if not is_buildable(module):
                                #_l_unbuildable.append(name)
                        except Exception, e:
                            log.warning("|{0}| >> Module failed: {1}".format(_str_func,key))
                            log.error(e)
                            cgmGEN.cgmExceptCB(Exception,e,msg=vars())
                    else:
                        _l_duplicates.append("{0} >> {1} ".format(key, os.path.join(root,f)))
            _i+=1


    if _b_debug:
        cgmGEN.walk_dat(_d_modules,"Modules")        
        cgmGEN.walk_dat(_d_files,"Files")
        cgmGEN.walk_dat(_d_import,"Imports")
        cgmGEN.walk_dat(_d_categories,"Categories")

    if _l_duplicates and _b_debug:
        log.debug(cgmGEN._str_subLine)
        log.debug("|{0}| >> DUPLICATE MODULES....".format(_str_func))
        for m in _l_duplicates:
            print(m)
        raise Exception,"Must resolve"
    log.debug("|{0}| >> Found {1} modules under: {2}".format(_str_func,len(_d_files.keys()),_path))     
    if _l_unbuildable and _b_debug:
        log.debug(cgmGEN._str_subLine)
        log.debug("|{0}| >> ({1}) Unbuildable modules....".format(_str_func,len(_l_unbuildable)))
        for m in _l_unbuildable:
            print(">>>    " + m) 
            
    CGM_RIGBLOCK_DAT = _d_modules, _d_categories, _l_unbuildable
    return _d_modules, _d_categories, _l_unbuildable
