"""
------------------------------------------
constraint_utils: cgm.core.lib.constraint_utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

Unified location for transform calls. metanode instances may by passed
"""

# From Python =============================================================
import copy
import re
import random

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
from maya import mel
# From Red9 =============================================================

# From cgm ==============================================================
#CANNOT import Rigging
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import list_utils as LISTS
from cgm.core.lib import name_utils as NAMES
import cgm.core.lib.math_utils as MATH
import cgm.core.lib.transform_utils as TRANS
import cgm.core.lib.distance_utils as DIST
#returnObjectConstraints
#returnObjectDrivenConstraints
#returnConstraintTargets

_d_type_to_call = {'parentConstraint':mc.parentConstraint,
                    'orientConstraint':mc.orientConstraint,
                    'pointConstraint':mc.pointConstraint,
                    'scaleConstraint':mc.scaleConstraint,
                    'aimConstraint':mc.aimConstraint}

def get_constraintsTo(node=None, fullPath = True):
    """
    Get the constraints on a given node
    
    :parameters:
        node(str): node to query
        fullPath(bool): How you want list
    :returns
        list of constraints(list)
    """   
    _str_func = 'get_constraintsTo'
    
    node = VALID.mNodeString(node)
    
    _res = mc.listRelatives(node,type='constraint',fullPath=fullPath) or []
    _res = LISTS.get_noDuplicates(_res)
    if fullPath:
        return [NAMES.long(o) for o in _res]
    return _res

def get_constraintsFrom(node=None, fullPath = True):
    """
    Get the constraints a given node drives
    
    :parameters:
        node(str): node to query
        fullPath(bool): How you want list

    :returns
        list of constraints(list)
    """   
    _str_func = 'get_constraintsFrom'
    
    node = VALID.mNodeString(node)
    
    _res = mc.listConnections(node,source = False, destination = True,skipConversionNodes = True, type='constraint') or []

    _res = LISTS.get_noDuplicates(_res)
    #_l_objectConstraints = get(node)
    #for c in _l_objectConstraints:
        #if c in _res:_res.remove(c)
    
    if fullPath:
        return [NAMES.long(o) for o in _res]
    return _res

def get_targets(node=None, fullPath = True, select = False):
    """
    Get the constraints a given node drives
    
    :parameters:
        node(str): node to query

    :returns
        list of targets(list)
    """   
    _str_func = 'get_targets'
    if node == None:
        _sel = mc.ls(sl=True,long=True)
        if _sel:
            node = _sel[0]
        else:
            raise ValueError,"|{0}| >> No node arg. None selected".format(_str_func)
            
    node = VALID.mNodeString(node)
    _type = VALID.get_mayaType(node)

    _call = _d_type_to_call.get(_type,False)
    if not _call:
        _to = get_constraintsTo(node,True)
        if _to:
            log.info("|{0}| >> Not a constraint node. Found contraints to. Returning first".format(_str_func))
            return get_targets(_to[0],fullPath,select)
            
        raise ValueError,"|{0}| >> {1} not a known type of constraint. node: {2}".format(_str_func,_type,node)

    _res = _call(node,q=True,targetList=True)
    if select:
        mc.select(_res)
    if fullPath:
        return [NAMES.long(o) for o in _res]
    return _res

def get_targetWeightsDict(node=None):
    """
    Get the constraints a given node drives
    
    :parameters:
        node(str): node to query

    :returns
        list of targets(list)
    """   
    _str_func = 'get_targetWeightsDict'
    
    node = VALID.mNodeString(node)
    
    _type = VALID.get_mayaType(node)
    _d = {}
    _l = []

    _call = _d_type_to_call.get(_type,False)
    if not _call:
        raise ValueError,"|{0}| >> {1} not a known type of constraint. node: {2}".format(_str_func,_type,node)

    aliasList = _call(node,q=True, weightAliasList=True)
    if aliasList:
        for o in aliasList:
            _d[o] = ATTR.get(node,o)

    return _d

def get_targetWeightsAttrs(node=None):
    """
    Get the constraints a given node drives
    
    :parameters:
        node(str): node to query

    :returns
        list of attrs(list)
    """   
    _str_func = 'get_targetWeightsDict'
    
    node = VALID.mNodeString(node)
    
    _type = VALID.get_mayaType(node)
    _d = {}
    _l = []

    _call = _d_type_to_call.get(_type,False)
    if not _call:
        raise ValueError,"|{0}| >> {1} not a known type of constraint. node: {2}".format(_str_func,_type,node)

    return _call(node,q=True, weightAliasList=True)

def get_constraintsByDrivingObject(node=None, driver = None, fullPath = False):
    """
    Get a list of constraints driving a node by the drivers of those constraints.
    node 1 is driven by 3 constraints. 2 of those constraints use our driver as a target.
    Those 2 will be returned.
    
    :parameters:
        node(str): node to query
        driver(str): driver to check against
        fullPath(bool): How you want list
    :returns
        list of constraints(list)
    """   
    _str_func = 'get_constraintsTo'
    
    node = VALID.mNodeString(node)
    
    driver = VALID.mNodeString(driver)
    _long = NAMES.long(driver)   
    log.debug("|{0}| >> node: {1} | target: {2}".format(_str_func,node, _long))             
    
    l_constraints = get_constraintsTo(node,True)
    _res = False
    
    if l_constraints:
        _res = []
        for c in l_constraints:
            targets = get_targets(c,True)
            log.debug("|{0}| >> targets: {1}".format(_str_func, targets))              
            if _long in targets:
                log.debug("|{0}| >> match found: {1}".format(_str_func, c))                  
                _res.append(c)
    if _res and not fullPath:
        return [NAMES.short(o) for o in _res]
    return _res   


def get_driven(constraint = None):
    """    
    Get driven transforms from a given transform
    
    :parameters:
        constraint(str): node to query
        
    :returns
        driven transform(str)
    """       
    _str_func = 'get_driven'
    return ATTR.get_driver('{0}.constraintParentInverseMatrix'.format(constraint),getNode=True) or None
    

def set_weightsByDistance(constraint=None,vList = None):
    """    
    :parameters:
        node(str): node to query

    :returns
        list of constraints(list)
    """   
    _str_func = 'set_weightsByDistance'
    
    log.debug("|{0}| >> constraint: {1} ".format(_str_func,constraint))             
    
    #if vList:
        #raise NotImplementedError,'Not yet'
        
    _attrs = get_targetWeightsAttrs(constraint)
        
    if not vList:
        pos_obj = TRANS.position_get(get_driven(constraint))
        targets = get_targets(constraint)
        _l_dist = []
        for t in targets:
            _l_dist.append(DIST.get_distance_between_points(pos_obj,TRANS.position_get(t)))
        vList = MATH.normalizeList(_l_dist)
        log.debug("|{0}| >> targets: {1} ".format(_str_func,targets))                     
        log.debug("|{0}| >> raw: {1} ".format(_str_func,_l_dist))             
    log.debug("|{0}| >> normalize: {1} ".format(_str_func,vList))             
    log.debug("|{0}| >> attrs: {1} ".format(_str_func,_attrs))             
    
    if len(_attrs) != len(vList):
        raise ValueError,"Len of attrs and valueList do not match: {0} | {1}".format(len(_attrs),len(vList))

    for i,v in enumerate(vList):
        ATTR.set(constraint,_attrs[i],v)

    return vList

def get_datDict(constraint = None):
    _str_func = 'get_datDict'
        
    log.debug("|{0}| >> constraint: {1} ".format(_str_func,constraint))
    result = {}
    
    result['driven'] = get_driven(constraint)
    result['targets']= get_targets(constraint)
    result['attrs']= get_targetWeightsAttrs(constraint)
    result['type'] = VALID.get_mayaType(constraint)
    result['attrWeights'] = get_targetWeightsDict(constraint)
    
    result['attrDrivers'] = []
    for a in result['attrs']:
        result['attrDrivers'].append(ATTR.get_driver("{0}.{1}".format(constraint,a)))
    
    return result

def copy_constraint(sourceConstraint=None, targetObj=None, constraintType=None, maintainOffset = True):
    """
    Copy the constraint settings from a constraint to another object
    :parameters:
        node(str): node to query

    :returns
        list of constraints(list)
    """   
    _str_func = 'copy_constraint'
    
    log.debug("|{0}| >> constraint: {1} ".format(_str_func,sourceConstraint))
    
    d_source = get_datDict(sourceConstraint)
    _type = d_source['type']

    if constraintType is None:
        if targetObj is None:
            raise ValueError,"|{0}| >> Must have targetObject or constraintType ".format(_str_func)
        else:
            log.info("|{0}| >> No constraintType passed. Using source's: '{1}' ".format(_str_func,_type))            
            constraintType = _type
            
    _call = _d_type_to_call.get(constraintType,False)
    
    if not _call:
        raise ValueError,"|{0}| >> {1} not a known type of constraint. node: {2}".format(_str_func,_type,sourceConstraint)
    
    
    if targetObj is None:
        targetObj = d_source['driven']
        log.info("|{0}| >> No target object passed. Using source's: '{1}' ".format(_str_func,targetObj))
        
    cgmGeneral.func_snapShot(vars())
    result = _call(d_source['targets'], targetObj, maintainOffset=maintainOffset)
    d_result = get_datDict(result[0])
    
    for i,a in enumerate(d_result['attrs']):
        if d_source['attrDrivers'][i]:
            ATTR.connect("{0}".format(d_source['attrDrivers'][i]), "{0}.{1}".format(result[0],d_result['attrs'][i]) )
        else:
            ATTR.set(result[0], d_result['attrs'][i], d_source['attrWeights'][ d_source['attrs'][i] ] )
    
    return result
    
    
    
    

 
