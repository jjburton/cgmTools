"""
rigging_utils
Josh Burton 
www.cgmonks.com

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
from cgm.core import cgm_General as cgmGeneral
from cgm.core.cgmPy import validateArgs as cgmValid

from cgm.lib import attributes
from cgm.lib import search
from cgm.lib import rigging
#from cgm.lib import locators #....CANNOT IMPORT LOCATORS - loop
from cgm.core.lib import attribute_utils as coreAttr
from cgm.core.lib import name_utils as coreNames

#>>> Utilities
#===================================================================
d_rotationOrder_to_index = {'xyz':0,'yzx':1 ,'zxy':2 ,'xzy':3 ,'yxz':4,'zyx':5,'none':6}

def valid_arg_single(arg = None, tag = None, calledFrom = None):
    """
    Simple validator to make sure a passed arg is a single entry
    
    :parameters:
        arg(varied): Arg to pass along
        tag(str): Usually the kw of the arg in the calling function
        calledFrom(str): Name of function calling for better error messaging...

    :returns
        arg
    """ 
    if not arg:
        raise ValueError,"{0} || Must have a {1}. | {1}: {2}".format(calledFrom,tag,arg) 
    if issubclass(type(arg),list or tuple):
        arg = arg[0]
    return arg

def copy_orientation(target = None, source = None,
                     rotateOrder = True, rotateAxis = True):
    """
    Copy the axis from one object to another. For rotation axis -- 
    a locator is created from the source to get local space values for pushing
    to the rotate axis of the target object. 
    
    We do this cleanly by removing children from our target during our processing and then
    reparenting at the end as well as restoring shapes from a place holder duplicate.
    
    :parameters:
        target(str): Object to modify
        sourceObject(str): object to copy from
        rotateOrder(bool): whether to copy the rotateOrder while preserving rotations
        rotateAxis(bool): whether to copy the rotateAxis

    :returns
        success(bool)
    """   
    _str_func = 'copy_orientation'
    
    target = valid_arg_single(target, 'target', _str_func)
    source = valid_arg_single(source, 'source', _str_func) 
    
    log.debug("{0} || target:{1}".format(_str_func,target))    
    log.debug("{0} || source:{1}".format(_str_func,source))
    log.debug("{0} || rotateOrder:{1}".format(_str_func,rotateOrder))
    log.debug("{0} || rotateAxis:{1}".format(_str_func,rotateAxis))
    
    if not rotateOrder and not rotateAxis:
        raise ValueError,"{0} || Both rotateOrder and rotateAxis are False. Nothing to do...".format(_str_func) 
    
    #First gather children to parent away and shapes so they don't get messed up either
    _l_children = mc.listRelatives (target, children = True,type='transform') or []
    _l_shapes = mc.listRelatives (target, shapes = True, fullPath = True) or []
    _dup = False
    
    log.info("{0} || children:{1}".format(_str_func,_l_children))
    log.info("{0} || shapes:{1}".format(_str_func,_l_shapes))
    
    if _l_children:#...parent children to world as we'll be messing with stuff
        for i,c in enumerate(_l_children):
            _l_children[i] = parent_set(c,False)
    log.info("{0} || children:{1}".format(_str_func,_l_children))
            
    if _l_shapes:#...dup our shapes to properly shape parent them back
        _dup = mc.duplicate(target, parentOnly = False)[0]
        log.info("{0} || dup:{1}".format(_str_func,_dup))
        
    #The meat of it...
    _restorePivotRP = False
    _restorePivotSP = False
    
    if rotateAxis:
        log.info("{0} || rotateAxis...".format(_str_func))        
        
        #There must be a better way to do this. Storing to be able to restore after matrix ops
        _restorePivotRP = mc.xform(target, q=True, ws=True, rp = True)
        _restorePivotSP = mc.xform(target, q=True, ws=True, sp = True)
        _restoreRO = mc.xform (target, q=True, roo=True )
                    
        #We do our stuff with a locator to get simple transferrable values after matching parents and what not...
        loc = locators.locMeObject(source)
        #..match ro before starting to do values
        
        parent_set(loc, parent_get(target))#...match parent
        
        mc.xform(loc, ws = True, t = mc.xform(target, q=True, ws = True, rp = True))#...snap
        #mc.xform(loc, roo = mc.xform (target, q=True, roo=True ), p=True)#...match rotateOrder
        mc.xform(loc, roo = 'xyz', p=True)
        mc.xform(target, roo = 'xyz', p=True)
        
        mc.makeIdentity(target,a = True, rotate = True)
        
        #...push matrix
        _matrix = mc.xform (loc, q=True, m =True)
        mc.xform(target, m = _matrix)
        
        objRot = mc.xform (target, q=True, os = True, ro=True)
        
        mc.xform(target, ra=[v for v in objRot], os=True)
        mc.xform(target,os=True, ro = [0,0,0])#...clear"""
            
        mc.delete(loc)
        
        mc.xform(target, roo = _restoreRO)
        mc.xform(target,ws=True, rp = _restorePivotRP)   
        mc.xform(target,ws=True, sp = _restorePivotSP) 
            
    if rotateOrder:   
        log.info("{0} || rotateOrder...".format(_str_func))                  
        mc.xform(target, roo = mc.xform (source, q=True, roo=True ), p=True)#...match rotateOrder
                
    if _dup:
        log.info("{0} || shapes back...: {1}".format(_str_func,_l_shapes))          
        mc.delete(_l_shapes)
        parentShape_in_place(target,_dup)
        mc.delete(_dup)
        
    for c in _l_children:
        log.info("{0} || parent back...: '{1}'".format(_str_func,c))  
        log.debug("{0} || target:{1}".format(_str_func,target))    
        
        parent_set(c,target)  
        
    return True

def match_transformNOTDONE(target = None, source = None,
                   rotateOrder = True, rotateAxis = True,
                   rotatePivot = True, scalePivot = True):
    """
    A bridge function utilizing both copy_pivot and copy_orientation in a single call
    
    :parameters:
        target(str): Object to modify
        sourceObject(str): object to copy from
        rotateOrder(bool): whether to copy the rotateOrder while preserving rotations
        rotateAxis(bool): whether to copy the rotateAxis
        rotatePivot(bool): whether to copy the rotatePivot
        scalePivot(bool): whether to copy the scalePivot

    :returns
        success(bool)
    """   
    _str_func = 'match_transform'
    
    target = valid_arg_single(target, 'target', _str_func)
    source = valid_arg_single(source, 'source', _str_func) 
    
    log.debug("{0} || target:{1}".format(_str_func,target))    
    log.debug("{0} || source:{1}".format(_str_func,source))
    
    #First gather children to parent away and shapes so they don't get messed up either
    _l_children = mc.listRelatives (target, children = True,type='transform') or []
    _l_shapes = mc.listRelatives (target, shapes = True, fullPath = True) or []
    _dup = False
    
    log.info("{0} || children:{1}".format(_str_func,_l_children))
    log.info("{0} || shapes:{1}".format(_str_func,_l_shapes))
    
    if _l_children:#...parent children to world as we'll be messing with stuff
        for i,c in enumerate(_l_children):
            _l_children[i] = parent_set(c,False)
    log.info("{0} || children:{1}".format(_str_func,_l_children))
            
    if _l_shapes:#...dup our shapes to properly shape parent them back
        _dup = mc.duplicate(target, parentOnly = False)[0]
        log.info("{0} || dup:{1}".format(_str_func,_dup))
        
        
    #The meat of it...        
    if rotateOrder or rotateAxis:
        log.info("{0} || orientation copy...".format(_str_func))                                  
        copy_orientation(target,source,rotateOrder,rotateAxis)
        
    if rotatePivot or scalePivot:    
        log.info("{0} || pivot copy...".format(_str_func))                                  
        copy_pivot(target,source, rotatePivot, scalePivot)    
        

    if _dup:
        log.info("{0} || shapes back...: {1}".format(_str_func,_l_shapes))          
        mc.delete(_l_shapes)
        parentShape_in_place(target,_dup)
        mc.delete(_dup)
        
    for c in _l_children:
        log.info("{0} || parent back...: '{1}'".format(_str_func,c))  
        log.debug("{0} || target:{1}".format(_str_func,target))    
        
        parent_set(c,target)  
        
    return True

def copy_transformOLD(target = None, source = None,
                   rotateOrder = True, rotateAxis = True,
                   rotatePivot = True, scalePivot = True):
    """
    A bridge function utilizing both copy_pivot and copy_orientation in a single call
    
    :parameters:
        target(str): Object to modify
        sourceObject(str): object to copy from
        rotateOrder(bool): whether to copy the rotateOrder while preserving rotations
        rotateAxis(bool): whether to copy the rotateAxis
        rotatePivot(bool): whether to copy the rotatePivot
        scalePivot(bool): whether to copy the scalePivot

    :returns
        success(bool)
    """   
    _str_func = 'copy_transform'
    
    target = valid_arg_single(target, 'target', _str_func)
    source = valid_arg_single(source, 'source', _str_func) 
    
    log.debug("{0} || target:{1}".format(_str_func,target))    
    log.debug("{0} || source:{1}".format(_str_func,source))
    log.info("{0} || rotateAxis:{1}".format(_str_func,rotateAxis))
    
    #First gather children to parent away and shapes so they don't get messed up either
    _l_children = mc.listRelatives (target, children = True,type='transform') or []
    _l_shapes = mc.listRelatives (target, shapes = True, fullPath = True) or []
    _dup = False
    
    log.info("{0} || children:{1}".format(_str_func,_l_children))
    log.info("{0} || shapes:{1}".format(_str_func,_l_shapes))
    
    if _l_children:#...parent children to world as we'll be messing with stuff
        for i,c in enumerate(_l_children):
            _l_children[i] = parent_set(c,False)
    log.info("{0} || children:{1}".format(_str_func,_l_children))
            
    if _l_shapes:#...dup our shapes to properly shape parent them back
        _dup = mc.duplicate(target, parentOnly = False)[0]
        log.info("{0} || dup:{1}".format(_str_func,_dup))
        
    
    #The meat of it...
    if rotatePivot or scalePivot and not rotateAxis:    
        log.info("{0} || pivot copy...".format(_str_func))                                  
        copy_pivot(target,source, rotatePivot, scalePivot)
        
    _restorePivotRP = False
    _restorePivotSP = False
    
    if rotateAxis:
        log.info("{0} || rotateAxis...".format(_str_func))                          
        if not rotatePivot:
            #There must be a better way to do this. Storing to be able to restore after matrix ops
            _restorePivotRP = mc.xform(target, q=True, ws=True, rp = True)
        if not scalePivot:
            _restorePivotSP = mc.xform(target, q=True, ws=True, sp = True)
                    
        #We do our stuff with a locator to get simple transferrable values after matching parents and what not...
        loc = locators.locMeObject(source)
        #..match ro before starting to do values
        
        parent_set(loc, parent_get(target))#...match parent
        mc.xform(loc, roo = mc.xform (target, q=True, roo=True ), p=True)#...match rotateOrder
        
        mc.makeIdentity(target,a = True, rotate = True)
        
        #...push matrix
        _matrix = mc.xform (loc, q=True, m =True)
        mc.xform(target, m = _matrix)
        
        objRot = mc.xform (target, q=True, os = True, ro=True)
        for i,a in enumerate(['X','Y','Z']):
            attributes.doSetAttr(target, 'rotateAxis{0}'.format(a), objRot[i])  
        mc.xform(target,os=True, ro = [0,0,0])#...clear
            
        mc.delete(loc)
        #mc.xform(target, p = False, os = True, ra = objRotAxis)
        #mc.xform(target, os = True, ro = objRot)
        
        if not rotatePivot:
            log.info("{0} || restore rotatePivot...".format(_str_func))                                      
            mc.xform(target,ws=True, rp = _restorePivotRP)
        if not scalePivot:
            log.info("{0} || restore scalePivot...".format(_str_func))                                      
            mc.xform(target,ws=True, sp = _restorePivotSP)
            
    if rotateOrder:   
        log.info("{0} || rotateOrder...".format(_str_func))                  
        mc.xform(target, roo = mc.xform (source, q=True, roo=True ), p=True)#...match rotateOrder
                
    if _dup:
        log.info("{0} || shapes back...: {1}".format(_str_func,_l_shapes))          
        mc.delete(_l_shapes)
        parentShape_in_place(target,_dup)
        mc.delete(_dup)
        
    for c in _l_children:
        log.info("{0} || parent back...: '{1}'".format(_str_func,c))  
        log.debug("{0} || target:{1}".format(_str_func,target))    
        
        parent_set(c,target)  
        
    return True

def copy_pivot(target = None, source = None, rotatePivot = True, scalePivot = True):
    """
    Copy the pivot from one object to another
    
    :parameters:
        target(str): Object to modify
        sourceObject(str): object to copy from
        rp(bool): Use the rotation pivot rather than scale

    :returns
        success(bool)
    """   
    _str_func = 'copy_pivot'
    target = valid_arg_single(target, 'target', _str_func)
    source = valid_arg_single(source, 'source', _str_func) 
    
    log.debug("{0} || target:{1}".format(_str_func,target))    
    log.debug("{0} || source:{1}".format(_str_func,source))
    
    if rotatePivot:
        pos = mc.xform(source, q=True, ws=True, rp = True)
        mc.xform(target,ws=True, rp = pos)   
    if scalePivot:
        pos = mc.xform(source, q=True, ws=True, sp = True)
        mc.xform(target,ws=True, sp = pos)   
    return True

def parent_set(target = None, parent = False):
    """
    Takes care of parenting transforms and returning new names.
    
    :parameters:
        target(str): Object to modify
        parent(str): Parent object or False for world

    :returns
        correct name(str)
    """   
    _str_func = 'parent_set'
    target = valid_arg_single(target, 'target', _str_func)
    if parent:
        parent = valid_arg_single(parent, 'parent', _str_func)    
        
    log.debug("{0} || target:{1}".format(_str_func,target))    
    log.debug("{0} || parent:{1}".format(_str_func,parent))
    
    _parents = mc.listRelatives(target,parent=True,type='transform')
    
    if parent:
        try:
            return mc.parent(target,parent)[0]
        except Exception,err:
            log.error("{0} || Failed to parent '{1}' to '{2}' | err: {3}".format(_str_func, target,parent, err))    
            return target
        #if parent in str(mc.ls(target,long=True)):
            #return target
        #else:
            #return mc.parent(target,parent)[0]
    else:
        if _parents:
            return mc.parent(target, world = True)[0]
        else:
            return target
    raise ValueError,"Shouldn't have arrived here."

def parent_get(target = None):
    """
    Takes care of parenting transforms and returning new names
    
    :parameters:
        target(str): Object to modify
        
    :returns
        correct name(str)
    """   
    _str_func = 'parent_get'
    
    target = valid_arg_single(target, 'target', _str_func)
        
    log.debug("{0} || target:{1}".format(_str_func,target))    
    
    _parents = mc.listRelatives(target,parent=True, type='transform') or False
    
    if _parents:
        return _parents[0]
    return False

def parentShape_in_place(target = None, curve = None):
    """
    Shape parent a curve in place to a target transform

    :parameters:
        target(str): Object to modify
        curve(str): Curve to shape parent

    :returns
        success(bool)
    """   
    _str_func = 'parentShape_in_place'
    target = valid_arg_single(target, 'target', _str_func)
    curve = valid_arg_single(curve, 'curve', _str_func)

    log.debug("{0} || target:{1}".format(_str_func,target))    
    log.debug("{0} || curve:{1}".format(_str_func,curve))

    mc.select (cl=True)
    _dup_curve = mc.duplicate(curve)[0]
    _l_parents = search.returnAllParents(target)

    _dup_curve = parent_set(_dup_curve,False)

    copy_pivot(_dup_curve,target)
    pos = mc.xform(target, q=True, os=True, rp = True)

    curveScale =  mc.xform(_dup_curve,q=True, s=True,r=True)
    objScale =  mc.xform(target,q=True, s=True,r=True)

    #account for freezing
    #mc.makeIdentity(_dup_curve,apply=True,translate =True, rotate = True, scale=False)

    # make our zero out group
    group = rigging.groupMeObject(target,False)

    _dup_curve = parent_set(_dup_curve,group)

    # zero out the group 
    mc.xform(group, ws=True, t = pos)
    #mc.xform(group,roo = 'xyz', p=True)
    mc.xform(group, ra=[0,0,0], p = False)
    mc.xform(group,ro=[0,0,0], p =False)
    
    mc.makeIdentity(_dup_curve,apply=True,translate =True, rotate = True, scale=False)
    
    """mc.setAttr((group+'.tx'),pos[0])
    mc.setAttr((group+'.ty'),pos[1])
    mc.setAttr((group+'.tz'),pos[2])
    mc.setAttr((group+'.rx'),0)
    mc.setAttr((group+'.ry'),0)
    mc.setAttr((group+'.rz'),0)
    mc.setAttr((group+'.rotateAxisX'),0)
    mc.setAttr((group+'.rotateAxisY'),0)
    mc.setAttr((group+'.rotateAxisZ'),0)"""
     
    #main scale fix 
    baseMultiplier = [0,0,0]
    baseMultiplier[0] = ( curveScale[0]/objScale[0] )
    baseMultiplier[1] = ( curveScale[1]/objScale[1] )
    baseMultiplier[2] = ( curveScale[2]/objScale[2] )
    mc.setAttr(_dup_curve+'.sx',baseMultiplier[0])
    mc.setAttr(_dup_curve+'.sy',baseMultiplier[1])
    mc.setAttr(_dup_curve+'.sz',baseMultiplier[2])
    
    #parent scale fix  
    if _l_parents:
        _l_parents.reverse()
        multiplier = [baseMultiplier[0],baseMultiplier[1],baseMultiplier[2]]
        for p in _l_parents:
            scaleBuffer = mc.xform(p,q=True, s=True,r=True)
            multiplier[0] = ( (multiplier[0]/scaleBuffer[0]) )
            multiplier[1] = ( (multiplier[1]/scaleBuffer[1]) )
            multiplier[2] = ( (multiplier[2]/scaleBuffer[2])  )
        mc.setAttr(_dup_curve+'.sx',multiplier[0])
        mc.setAttr(_dup_curve+'.sy',multiplier[1])
        mc.setAttr(_dup_curve+'.sz',multiplier[2])	

    _dup_curve = parent_set(_dup_curve,False)
    mc.delete(group)
    
    #freeze for parent shaping 
    mc.makeIdentity(_dup_curve,apply=True,translate =True, rotate = True, scale=True)
    shape = mc.listRelatives (_dup_curve, f= True,shapes=True, fullPath = True)
    mc.parent (shape,target,add=True,shape=True)
    #mc.delete(_dup_curve)

    return True


def create_at(target = None, create = 'null'):
    """
    Create a null matching a given target
    
    :parameters:
        target(str): Object to modify
        create(str): What to create

    :returns
        name(str)
    """   
    _str_func = 'create_at'
    
    target = valid_arg_single(target, 'target', _str_func)
    _l_toCreate = ['null','joint','locator']
    _create = cgmValid.kw_fromList(create, _l_toCreate, calledFrom=_str_func)
    
    log.debug("{0} || target:{1}".format(_str_func,target))  
    log.info("{0} || create:{1}".format(_str_func,_create))  
    
    objTrans = mc.xform (target, q=True, ws=True, rp=True)
    objRot = mc.xform (target, q=True, ws=True, ro=True)
    objRotAxis = mc.xform(target, q=True, ws = True, ra=True)

    #return rotation order
    if _create == 'null':
        _created = mc.group (w=True, empty=True)
        #mc.setAttr ((groupBuffer+'.rotateOrder'), correctRo)
        mc.xform(_created, roo = mc.xform(target, q=True, roo=True ))#...match rotateOrder    
        mc.move (objTrans[0],objTrans[1],objTrans[2], [_created])
        #for i,a in enumerate(['X','Y','Z']):
                        #attributes.doSetAttr(groupBuffer, 'rotateAxis{0}'.format(a), objRotAxis[i])    
        #mc.rotate(objRot[0], objRot[1], objRot[2], [groupBuffer], ws=True)
        mc.xform(_created, ws=True, ro= objRot,p=False)
        mc.xform(_created, ws=True, ra= objRotAxis,p=False)  
        
    elif _create == 'joint':
        raise NotImplementedError,"joints not done yet"
        mc.select(cl=True)
        _created = mc.joint()
        attributes.doSetAttr(_created,'displayLocalAxis',True)

    return _created
    

def group_me(target = None,
             parent = False, maintainParent = False, rotateAxis = True,
             rotatePivot = True, scalePivot = True):
    """
    A bridge function utilizing both copy_pivot and copy_orientation in a single call
    
    :parameters:
        target(str): Object to modify
        sourceObject(str): object to copy from
        rotateOrder(bool): whether to copy the rotateOrder while preserving rotations
        rotateAxis(bool): whether to copy the rotateAxis
        rotatePivot(bool): whether to copy the rotatePivot
        scalePivot(bool): whether to copy the scalePivot

    :returns
        success(bool)
    """   
    _str_func = 'group_me'
    
    target = valid_arg_single(target, 'target', _str_func)
    
    log.debug("{0} || target:{1}".format(_str_func,target))    
    
    _oldParent = False
    if maintainParent:
        _oldParent = parent_get(target)
        
    group = create_at(target)
    

    if maintainParent == True and oldParent:
        group = parent_set(group,oldParent)
        
    if parent:
        _wasLocked = []  
        for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            attrBuffer = '%s.%s'%(target,attr)
            if mc.getAttr(attrBuffer,lock=True):
                _wasLocked.append(attr)
                mc.setAttr(attrBuffer,lock=False)                
            #attributes.doSetAttr(obj,attr,0)          
        target = parent_set(target,group)        
    
        if _wasLocked:
            for attr in _wasLocked:
                attrBuffer = '%s.%s'%(target,attr)
                mc.setAttr(attrBuffer,lock=True)                

    return mc.rename(group, "{0}_grp".format(coreNames.get_base(target)))  



    