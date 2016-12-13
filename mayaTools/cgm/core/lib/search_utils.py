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
from cgm.core.lib import rigging_utils as coreRigging
from cgm.core.lib import name_utils as NAME

from cgm.lib import attributes

#>>> Utilities
#===================================================================
def get_mayaType(node = None):
    """
    What kind of nodeect is this as maya's type return isn't always great
    
    :parameters:
        node(str): Object to check

    :returns
        type(str)
    """   
    def simpleTransformShapeCheck(node = None):
        _shapes = mc.listRelatives(node,shapes=True,fullPath=True) or []
        _len = len(_shapes)
        
        if _len == 1:
            return mc.objectType(_shapes[0])
        elif _len > 1:
            log.warning("|{0}| >> node: '{1}' has multiple shapes. returning type for '{2}'. Remaining shapes:{3}".format(_str_func,_node,_shapes[0],_shapes[1:]))    
            return mc.objectType(_shapes[0])
        else:
            """
            _parent = coreRigging.parent_get(_node)
            if not _parent:
                _parentShapes = mc.listRelatives(_parent,shapes=True,fullPath=True)
                if parentShapes != None:
                    matchObjName = mc.ls(_node, long=True)
                    if matchObjName[0] in parentShapes:
                        isShape = True
            if isShape == True:
                return 'shape'
            else:
                # Case specific"""
                
    
            if mc.listRelatives(node,children = True):#if just a tranform with children, it's a group
                return 'group'
            return 'transform' 
        
    _str_func = 'get_mayaType'
    _node = coreValid.stringArg(node,False,_str_func)
    
    log.debug("|{0}| >> node: '{1}' ".format(_str_func,_node))    
    
    _intialCheck = mc.objectType(_node)

    if _intialCheck in ['nodeectSet']:
        return _intialCheck

    #Easiest to check component...
    if _intialCheck == 'transform':
        return simpleTransformShapeCheck(_node)

    elif is_component(_node):
        log.debug("|{0}| >> component mode...".format(_str_func))
        _split = _node.split('.')[-1]
        if 'vtx[' in _split:
            return 'polyVertex'

        if 'cv[' in _split:
            if _intialCheck == 'nurbsCurve':
                return 'curveCV'
            else:
                return 'surfaceCV'

        if 'e[' in _split:
            return 'polyEdge'
        if 'f[' in _split:
            return 'polyFace'
        if 'map[' in _split:
            return 'polyUV'
        if 'uv[' in _split:
            return 'surfacePoint'
        if 'sf[' in _split:
            return 'surfacePatch'
        if 'u[' in _split or 'v[' in _split:
            _root = _node.split('.')[0]
            _rootType = simpleTransformShapeCheck(_root)
            if _rootType == 'nurbsCurve':
                return 'curvePoint'
            if _rootType == 'nurbsSurface':
                return 'isoparm'
        if 'ep[' in _split:
            return 'editPoint' 
        
        raise RuntimeError,"Shouldn't have gotten here. Need another check for component type. '{0}'".format(_node)
    return _intialCheck

def is_component(arg = None):
    """
    Check to see if an arg is a component
    
    :parameters:
        node(str): Object to check

    :returns
        status(bool)
    """   
    _str_func = 'is_component'
    _arg = coreValid.stringArg(arg,False,_str_func)   
    log.debug("|{0}| >> arg: '{1}' ".format(_str_func,_arg))    
    
    if mc.objExists(_arg):
        if '.' in _arg and '[' in _arg and ']' in _arg:
            return True
    return False
    
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




    
    