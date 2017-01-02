"""
------------------------------------------
search_utils: cgm.core.lib.search_utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
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

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as coreValid
reload(coreValid)
from cgm.core.lib import shared_data as coreShared
from cgm.core.lib import name_utils as NAME

from cgm.lib import attributes

#>>> Utilities
#===================================================================   
def is_shape(node = None):
    """
    Check to see if an node is a shape
    
    :parameters:
        node(str): Object to check

    :returns
        status(bool)
    """   
    _str_func = 'is_shape'
    _node = coreValid.stringArg(node,False,_str_func)
    log.debug("|{0}| >> node: '{1}' ".format(_str_func,_node))    
    
    _shape = mc.ls(node,type='shape',long=True)
    if _shape:
        if len(_shape) == 1:
            if _shape[0] == NAME.get_long(_node):
                return True
    return False
    
def is_transform(node = None):
    """
    Is an node a transform?
    
    :parameters:
        node(str): Object to check

    :returns
        status(bool)
    """   
    _str_func = 'is_transform'
    _node = coreValid.stringArg(node,False,_str_func) 
    log.debug("|{0}| >> node: '{1}' ".format(_str_func,_node))    
    
    buffer = mc.ls(_node,type = 'transform',long = True)
    if buffer and buffer[0]==NAME.get_long(_node):
        return True
    if not mc.objExists(_node):
        log.error("|{0}| >> node: '{1}' doesn't exist".format(_str_func,_node))    
    return False

def get_transform(node = None):
    """
    Get transform of given node
    
    :parameters:
        node(str): Object to check

    :returns
        status(bool)
    """   
    _str_func = 'is_transform'
    _node = coreValid.stringArg(node,False,_str_func) 
    
    if '.' in node:
        _buffer = node.split('.')[0]
    else:
        _buffer = node
        
    _buffer = mc.ls(_buffer, type = 'transform') or False
    if _buffer:
        return _buffer[0]
    else:
        _buffer = mc.listRelatives(node,parent=True,type='transform') or False
    if _buffer:
        return _buffer[0]
    return False    

def get_tag(node = None, tag = None):
    """
    Get the info on a given node with a provided tag
    
    :parameters:
        node(str): Object to check

    :returns
        status(bool)
    """   
    _str_func = 'get_tag'
    _node = coreValid.stringArg(node,False,_str_func) 
    
    if (mc.objExists('%s.%s' %(_node,tag))) == True:
        messageQuery = (mc.attributeQuery (tag,node=_node,msg=True))
        if messageQuery == True:
            returnBuffer = attributes.returnMessageData(_node,tag,False)
            if not returnBuffer:
                return False
            elif get_mayaType(returnBuffer[0]) == 'reference':
                if attributes.repairMessageToReferencedTarget(_node,tag):
                    return attributes.returnMessageData(_node,tag,False)[0]
                return returnBuffer[0]
            return returnBuffer[0]
        else:
            infoBuffer = mc.getAttr('%s.%s' % (_node,tag))
            if infoBuffer is not None and len(list(str(infoBuffer))) > 0:
                return infoBuffer
            else:
                return False
    else:
        return False    
    
def get_all_parents(node = None, shortNames = True):
    """
    Get all the parents of a given node where the last parent is the top of the heirarchy
    
    :parameters:
        node(str): Object to check
        shortNames(bool): Whether you just want short names or long

    :returns
        parents(list)
    """   
    _str_func = 'get_all_parents'
    _node = coreValid.stringArg(node,False,_str_func) 
    
    _l_parents = []
    tmpObj = node
    noParent = False
    while noParent == False:
        tmpParent = mc.listRelatives(tmpObj,allParents=True,fullPath=True)
        if tmpParent:
            if len(tmpParent) > 1:
                raise ValueError,"Resolve what to do with muliple parents...{0} | {1}".format(node,tmpParent)
            _l_parents.append(tmpParent[0])
            tmpObj = tmpParent[0]
        else:
            noParent = True
    if shortNames:
        return [NAME.get_short(o) for o in _l_parents]
    return _l_parents 
    




    
    