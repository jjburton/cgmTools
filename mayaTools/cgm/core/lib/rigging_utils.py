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
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as VALID

from cgm.lib import search
from cgm.lib import rigging
from cgm.lib import locators #....CANNOT IMPORT LOCATORS - loop
from cgm.core.lib import attribute_utils as coreAttr
from cgm.core.lib import name_utils as coreNames
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import snap_utils as SNAP
#NO DIST

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
        raise ValueError,"|{0}| >> Must have a {1}. | {1}: {2}".format(calledFrom,tag,arg) 
    if issubclass(type(arg),list or tuple):
        arg = arg[0]
    return arg

def valid_arg_multi(arg = None, tag = None, calledFrom = None):
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
        raise ValueError,"|{0}| >> Must have a {1}. | {1}: {2}".format(calledFrom,tag,arg) 
    if not issubclass(type(arg),list or tuple):
        arg = [arg]
    return arg

def match_orientation(obj = None, source = None,
                     rotateOrder = True, rotateAxis = True):
    """
    Copy the axis from one object to another. For rotation axis -- 
    a locator is created from the source to get local space values for pushing
    to the rotate axis of the obj object. 
    
    We do this cleanly by removing children from our obj during our processing and then
    reparenting at the end as well as restoring shapes from a place holder duplicate.
    
    :parameters:
        obj(str): Object to modify
        sourceObject(str): object to copy from
        rotateOrder(bool): whether to copy the rotateOrder while preserving rotations
        rotateAxis(bool): whether to copy the rotateAxis

    :returns
        success(bool)
    """   
    _str_func = 'match_orientation'
    
    obj = valid_arg_single(obj, 'obj', _str_func)
    source = valid_arg_single(source, 'source', _str_func) 
    
    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
    log.debug("|{0}| >> source:{1}".format(_str_func,source))
    log.debug("|{0}| >> rotateOrder:{1}".format(_str_func,rotateOrder))
    log.debug("|{0}| >> rotateAxis:{1}".format(_str_func,rotateAxis))
    
    if not rotateOrder and not rotateAxis:
        raise ValueError,"|{0}| >> Both rotateOrder and rotateAxis are False. Nothing to do...".format(_str_func) 
    
    #First gather children to parent away and shapes so they don't get messed up either
    _l_children = mc.listRelatives (obj, children = True,type='transform') or []
    _l_shapes = mc.listRelatives (obj, shapes = True, fullPath = True) or []
    _dup = False
    
    log.info("|{0}| >> children:{1}".format(_str_func,_l_children))
    log.info("|{0}| >> shapes:{1}".format(_str_func,_l_shapes))
    
    if _l_children:#...parent children to world as we'll be messing with stuff
        for i,c in enumerate(_l_children):
            _l_children[i] = parent_set(c,False)
    log.info("|{0}| >> children:{1}".format(_str_func,_l_children))
            
    if _l_shapes:#...dup our shapes to properly shape parent them back
        _dup = mc.duplicate(obj, parentOnly = True)[0]
        log.info("|{0}| >> dup:{1}".format(_str_func,_dup))
        for s in _l_shapes:
            shapeParent_in_place(_dup,s,keepSource=False)        
        
    #The meat of it...
    _restorePivotRP = False
    _restorePivotSP = False
    
    if rotateAxis:
        log.info("|{0}| >> rotateAxis...".format(_str_func))        
        
        #There must be a better way to do this. Storing to be able to restore after matrix ops
        _restorePivotRP = mc.xform(obj, q=True, ws=True, rp = True)
        _restorePivotSP = mc.xform(obj, q=True, ws=True, sp = True)
        _restoreRO = mc.xform (obj, q=True, roo=True )
                    
        #We do our stuff with a locator to get simple transferrable values after matching parents and what not...
        loc = locators.locMeObject(source)
        #..match ro before starting to do values
        
        parent_set(loc, parent_get(obj))#...match parent
        
        mc.xform(loc, ws = True, t = mc.xform(obj, q=True, ws = True, rp = True))#...snap
        #mc.xform(loc, roo = mc.xform (obj, q=True, roo=True ), p=True)#...match rotateOrder
        mc.xform(loc, roo = 'xyz', p=True)
        mc.xform(obj, roo = 'xyz', p=True)
        
        mc.makeIdentity(obj,a = True, rotate = True)
        
        #...push matrix
        _matrix = mc.xform (loc, q=True, m =True)
        mc.xform(obj, m = _matrix)
        
        objRot = mc.xform (obj, q=True, os = True, ro=True)
        
        mc.xform(obj, ra=[v for v in objRot], os=True)
        mc.xform(obj,os=True, ro = [0,0,0])#...clear"""
            
        mc.delete(loc)
        
        mc.xform(obj, roo = _restoreRO)
        mc.xform(obj,ws=True, rp = _restorePivotRP)   
        mc.xform(obj,ws=True, sp = _restorePivotSP) 
            
    if rotateOrder:   
        log.info("|{0}| >> rotateOrder...".format(_str_func))                  
        mc.xform(obj, roo = mc.xform (source, q=True, roo=True ), p=True)#...match rotateOrder
                
    if _dup:
        log.info("|{0}| >> shapes back...: {1}".format(_str_func,_l_shapes))          
        #mc.delete(_l_shapes)
        shapeParent_in_place(obj,_dup)
        mc.delete(_dup)
        
    for c in _l_children:
        log.info("|{0}| >> parent back...: '{1}'".format(_str_func,c))  
        log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
        
        parent_set(c,obj)  
        
    return True

def match_transform(obj = None, source = None,
                    rotateOrder = True, rotateAxis = True,
                    rotatePivot = True, scalePivot = True):
    """
    A bridge function utilizing both copy_pivot and copy_orientation in a single call
    
    :parameters:
        obj(str): Object to modify
        sourceObject(str): object to copy from
        rotateOrder(bool): whether to copy the rotateOrder while preserving rotations
        rotateAxis(bool): whether to copy the rotateAxis
        rotatePivot(bool): whether to copy the rotatePivot
        scalePivot(bool): whether to copy the scalePivot

    :returns
        success(bool)
    """   
    _str_func = 'match_transform'
    
    obj = valid_arg_single(obj, 'obj', _str_func)
    source = valid_arg_single(source, 'source', _str_func) 
    
    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
    log.debug("|{0}| >> source:{1}".format(_str_func,source))
    
    #First gather children to parent away and shapes so they don't get messed up either
    _l_children = mc.listRelatives (obj, children = True,type='transform') or []
    _l_shapes = mc.listRelatives (obj, shapes = True, fullPath = True) or []
    _dup = False
    
    log.info("|{0}| >> children:{1}".format(_str_func,_l_children))
    log.info("|{0}| >> shapes:{1}".format(_str_func,_l_shapes))
    
    if _l_children:#...parent children to world as we'll be messing with stuff
        for i,c in enumerate(_l_children):
            _l_children[i] = parent_set(c,False)
    log.info("|{0}| >> children:{1}".format(_str_func,_l_children))
            
    if _l_shapes:#...dup our shapes to properly shape parent them back
        _dup = mc.duplicate(obj, parentOnly = True)[0]
        for s in _l_shapes:
            shapeParent_in_place(_dup,s,keepSource=False)
        log.info("|{0}| >> dup:{1}".format(_str_func,_dup))
        
        
    #The meat of it...        
    if rotateOrder or rotateAxis:
        log.info("|{0}| >> orientation copy...".format(_str_func))                                  
        match_orientation(obj,source,rotateOrder,rotateAxis)
        
    if rotatePivot or scalePivot:    
        log.info("|{0}| >> pivot copy...".format(_str_func))                                  
        copy_pivot(obj,source, rotatePivot, scalePivot)    
        

    if _dup:
        log.info("|{0}| >> shapes back...: {1}".format(_str_func,_l_shapes))          
        #mc.delete(_l_shapes)
        shapeParent_in_place(obj,_dup,)
        mc.delete(_dup)
        
    for c in _l_children:
        log.info("|{0}| >> parent back...: '{1}'".format(_str_func,c))  
        log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
        parent_set(c,obj)  
        
    return True

def copy_pivot(obj = None, source = None, rotatePivot = True, scalePivot = True):
    """
    Copy the pivot from one object to another
    
    :parameters:
        obj(str): Object to modify
        sourceObject(str): object to copy from
        rp(bool): Use the rotation pivot rather than scale

    :returns
        success(bool)
    """   
    _str_func = 'copy_pivot'
    obj = valid_arg_single(obj, 'obj', _str_func)
    source = valid_arg_single(source, 'source', _str_func) 
    
    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
    log.debug("|{0}| >> source:{1}".format(_str_func,source))
    
    if rotatePivot:
        pos = mc.xform(source, q=True, ws=True, rp = True)
        mc.xform(obj,ws=True, rp = pos)   
    if scalePivot:
        pos = mc.xform(source, q=True, ws=True, sp = True)
        mc.xform(obj,ws=True, sp = pos)   
    return True

def parent_set(obj = None, parent = False):
    """
    Takes care of parenting transforms and returning new names.
    
    :parameters:
        obj(str): Object to modify
        parent(str): Parent object or False for world

    :returns
        correct name(str)
    """   
    _str_func = 'parent_set'
    obj = valid_arg_single(obj, 'obj', _str_func)
    if parent:
        parent = valid_arg_single(parent, 'parent', _str_func)    
        
    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
    log.debug("|{0}| >> parent:{1}".format(_str_func,parent))
    
    _parents = mc.listRelatives(obj,parent=True,type='transform')
    
    if parent:
        try:
            return mc.parent(obj,parent)[0]
        except Exception,err:
            log.error("|{0}| >> Failed to parent '{1}' to '{2}' | err: {3}".format(_str_func, obj,parent, err))    
            return obj
        #if parent in str(mc.ls(obj,long=True)):
            #return obj
        #else:
            #return mc.parent(obj,parent)[0]
    else:
        if _parents:
            return mc.parent(obj, world = True)[0]
        else:
            return obj
    raise ValueError,"Shouldn't have arrived here."

def parent_get(obj = None):
    """
    Takes care of parenting transforms and returning new names
    
    :parameters:
        obj(str): Object to modify
        
    :returns
        correct name(str)
    """   
    _str_func = 'parent_get'
    
    obj = valid_arg_single(obj, 'obj', _str_func)
        
    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
    
    _parents = mc.listRelatives(obj,parent=True, type='transform') or False
    
    if _parents:
        return _parents[0]
    return False

def shapeParent_in_place(obj = None, shapeSource = None, keepSource = True, replaceShapes = False, snapFirst = False):
    """
    Shape parent a curve in place to a obj transform

    :parameters:
        obj(str): Object to modify
        shapeSource(str): Curve to shape parent
        keepSource(bool): Keep the curve shapeParented as well
        replaceShapes(bool): Whether to remove the obj's original shapes or not
        snapFirst(bool): whether to snap source to obj before transfer

    :returns
        success(bool)
    """   
    _str_func = 'shapeParent_in_place'
    
    l_shapes = VALID.listArg(shapeSource)
    
    log.debug(">>{0}>> >> obj: {1} | shapeSource: {2} | keepSource: {3} | replaceShapes: {4}".format(_str_func,obj,shapeSource,keepSource,replaceShapes))  
    
    if replaceShapes:
        _l_objShapes = mc.listRelatives(obj, s=True, fullPath = True)    
        if _l_objShapes:
            log.debug(">>{0}>> >> Removing obj shapes...| {1}".format(_str_func,_l_objShapes))
            mc.delete(_l_objShapes)
    
    mc.select (cl=True)
    for c in l_shapes:
        try:
            _shapeCheck = SEARCH.is_shape(c)
            if not _shapeCheck and not mc.listRelatives(c, f= True,shapes=True, fullPath = True):
                raise ValueError,"Has no shapes"
            if coreNames.get_long(obj) == coreNames.get_long(c):
                raise ValueError,"Cannot parentShape self"
            
            
            if _shapeCheck:
                _dup_curve = duplicate_shape(c)[0]
                if snapFirst:
                    SNAP.go(_dup_curve,obj)                    
            else:
                _dup_curve =  mc.duplicate(c)[0]
                if snapFirst:
                    SNAP.go(_dup_curve,obj)                
                
            _l_parents = SEARCH.get_all_parents(obj)
        
            _dup_curve = parent_set(_dup_curve, False)
     
            
            copy_pivot(_dup_curve,obj)
            #piv_pos = mc.xform(obj, q=True, ws=True, rp = True)
            #mc.xform(_dup_curve,ws=True, rp = piv_pos)  
            
            pos = mc.xform(obj, q=True, os=True, rp = True)
        
            curveScale =  mc.xform(_dup_curve,q=True, s=True,r=True)
            objScale =  mc.xform(obj,q=True, s=True,r=True)
        
            #account for freezing
            #mc.makeIdentity(_dup_curve,apply=True,translate =True, rotate = True, scale=False)
        
            # make our zero out group
            #group = rigging.groupMeObject(obj,False)
            group = create_at(obj,'null')
        
            _dup_curve = mc.parent(_dup_curve,group)[0]
        
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
        
            _dup_curve = parent_set(_dup_curve, False)
            
            mc.delete(group)
            
            #freeze for parent shaping 
            mc.makeIdentity(_dup_curve,apply=True,translate =True, rotate = True, scale=True)
            shape = mc.listRelatives (_dup_curve, f= True,shapes=True, fullPath = True)
            mc.parent (shape,obj,add=True,shape=True)
            mc.delete(_dup_curve)
            if not keepSource:
                mc.delete(c)
        except Exception,err:
            log.error("|{0}| >> obj:{1} failed to parentShape {2} >> err: {3}".format(_str_func,obj,c,err))  
    return True

def create_at(obj = None, create = 'null'):
    """
    Create a null matching a given obj
    
    :parameters:
        obj(str): Object to modify
        create(str): What to create

    :returns
        name(str)
    """   
    _str_func = 'create_at'
    
    obj = valid_arg_single(obj, 'obj', _str_func)
    _l_toCreate = ['null','joint','locator']
    _create = VALID.kw_fromList(create, _l_toCreate, calledFrom=_str_func)
    
    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))  
    log.debug("|{0}| >> create:{1}".format(_str_func,_create))  
    
    objTrans = mc.xform (obj, q=True, ws=True, rp=True)
    objRot = mc.xform (obj, q=True, ws=True, ro=True)
    objRotAxis = mc.xform(obj, q=True, ws = True, ra=True)

    #return rotation order
    if _create == 'null':
        _created = mc.group (w=True, empty=True)
        #mc.setAttr ((groupBuffer+'.rotateOrder'), correctRo)
        mc.xform(_created, roo = mc.xform(obj, q=True, roo=True ))#...match rotateOrder    
        mc.move (objTrans[0],objTrans[1],objTrans[2], [_created])
        #for i,a in enumerate(['X','Y','Z']):
                        #attributes.doSetAttr(groupBuffer, 'rotateAxis|{0}|'.format(a), objRotAxis[i])    
        #mc.rotate(objRot[0], objRot[1], objRot[2], [groupBuffer], ws=True)
        mc.xform(_created, ws=True, ro= objRot,p=False)
        mc.xform(_created, ws=True, ra= objRotAxis,p=False)  
        
    elif _create == 'joint':
        #raise NotImplementedError,"joints not done yet"
        #mc.select(cl=True)
        #_created = mc.joint()
        #coreAttr.set(_created,'displayLocalAxis',True)

        mc.select(cl=True)
        _created = mc.joint()
        #mc.setAttr ((groupBuffer+'.rotateOrder'), correctRo)
        mc.xform(_created, roo = mc.xform(obj, q=True, roo=True ))#...match rotateOrder    
        mc.move (objTrans[0],objTrans[1],objTrans[2], [_created])
        #for i,a in enumerate(['X','Y','Z']):
                        #attributes.doSetAttr(groupBuffer, 'rotateAxis|{0}|'.format(a), objRotAxis[i])    
        #mc.rotate(objRot[0], objRot[1], objRot[2], [groupBuffer], ws=True)
        mc.xform(_created, ws=True, ro= objRot,p=False)
        mc.xform(_created, ws=True, ra= objRotAxis,p=False)  
        
    elif _create == 'locator':
        raise NotImplementedError,"locators not done yet"
        

    return _created
    
def create_joint_at(obj = None):
    """
    Create a joint matching a given obj
    
    :parameters:
        obj(str): Object to modify

    :returns
        name(str)
    """

    return create_at(obj, create = 'joint')

def group_me(obj = None,
             parent = False, maintainParent = False, rotateAxis = True,
             rotatePivot = True, scalePivot = True):
    """
    A bridge function utilizing both copy_pivot and copy_orientation in a single call
    
    :parameters:
        obj(str): Object to modify
        parent(str): Whether to parent the object to the new group
        maintainParent(bool): Whether to maintain parent of the object
        rotateAxis(bool): whether to copy the rotateAxis
        rotatePivot(bool): whether to copy the rotatePivot
        scalePivot(bool): whether to copy the scalePivot

    :returns
        success(bool)
    """   
    _str_func = 'group_me'
    
    obj = valid_arg_single(obj, 'obj', _str_func)
    
    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
    
    _oldParent = False
    if maintainParent:
        _oldParent = parent_get(obj)
        
    group = create_at(obj)
    

    if maintainParent == True and _oldParent:
        group = parent_set(group,_oldParent)
        
    if parent:
        _wasLocked = []  
        for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            attrBuffer = '%s.%s'%(obj,attr)
            if mc.getAttr(attrBuffer,lock=True):
                _wasLocked.append(attr)
                mc.setAttr(attrBuffer,lock=False)                
            #attributes.doSetAttr(obj,attr,0)          
        obj = parent_set(obj,group)        
    
        if _wasLocked:
            for attr in _wasLocked:
                attrBuffer = '%s.%s'%(obj,attr)
                mc.setAttr(attrBuffer,lock=True)                

    return mc.rename(group, "|{0}|_grp".format(coreNames.get_base(obj)))  

def snapDEPRECIATE(obj = None, source = None,
         position = True, rotation = True, rotateAxis = True,
         objPivot = 'rp', sourcePivot = 'rp'):
    """
    A bridge function utilizing both copy_pivot and copy_orientation in a single call
    
    :parameters:
        obj(str): Object to modify
        sourceObject(str): object to copy from
        rotateOrder(bool): whether to copy the rotateOrder while preserving rotations
        rotateAxis(bool): whether to copy the rotateAxis
        rotatePivot(bool): whether to copy the rotatePivot
        scalePivot(bool): whether to copy the scalePivot

    :returns
        success(bool)
    """   
    _str_func = 'match_transform'
    
    obj = valid_arg_single(obj, 'obj', _str_func)
    source = valid_arg_single(source, 'source', _str_func)
    
def override_color(target = None, key = None, index = None, rgb = None, pushToShapes = True):
    """
    Sets the color of a shape or object via override. In Maya 2016, they introduced 
    rgb value override.
    
    :parameters
        target(str): What to color - shape or transform with shapes
        key(varied): if str will check against our shared color dict definitions for rgb and index entries
        index(int): Color index
        rgb(list): rgb values to set in Maya 2016 or above
        pushToShapes(bool): Push the overrides to shapes of passed transforms

    :returns
        info(dict)
    """   
    _str_func = "set_color"
    if not target:raise ValueError,">>{0}>> >> Must have a target".format(_str_func)

    _shapes = []
    #If it's accepable target to color
    
    mTarget = r9Meta.MetaClass(target, autoFill=False)
    
    if mTarget.hasAttr('overrideEnabled'):
        log.debug(">>{0}>> >> overrideEnabled  on target...".format(_str_func))            
        _shapes.append(mTarget.mNode)
    if pushToShapes:
        _bfr = mc.listRelatives(target, s=True)
        if _bfr:
            _shapes.extend(_bfr)
            
    if not _shapes:
        raise ValueError,">>{0}>> >> Not a shape and has no shapes: '{1}'".format(_str_func,target)        
    
    if index is None and rgb is None and key is None:
        raise ValueError,">>{0}>> >> Must have a value for index,rgb or key".format(_str_func)
    
    #...little dummy proofing..
    _type = type(key)
    
    if not issubclass(_type,str):
        log.debug(">>{0}>> >> Not a string arg for key...".format(_str_func))
        
        if rgb is None and issubclass(_type,list) or issubclass(_type,tuple):
            log.debug(">>{0}>> >> vector arg for key...".format(_str_func))            
            rgb = key
            key = None
        elif index is None and issubclass(_type,int):
            log.debug(">>{0}>> >> int arg for key...".format(_str_func))            
            index = key
            key = None
        else:
            raise ValueError,">>{0}>> >> Not sure what to do with this key arg: {1}".format(_str_func,key)
    
    _b_RBGMode = False
    _b_2016Plus = False
    if cgmGen.__mayaVersion__ >=2016:
        _b_2016Plus = True
        
    if key is not None:
        _color = False
        if _b_2016Plus:
            log.debug(">>{0}>> >> 2016+ ...".format(_str_func))            
            _color = SHARED._d_colors_to_RGB.get(key,False)
            
            if _color:
                rgb = _color
        
        if _color is False:
            log.debug(">>{0}>> >> Color key not found in rgb dict checking index...".format(_str_func))
            _color = SHARED._d_colors_to_index.get(key,False)
            if _color is False:
                raise ValueError,">>{0}>> >> Unknown color key: '{1}'".format(_str_func,key) 
                
    if rgb is not None:
        if not _b_2016Plus:
            raise ValueError,">>{0}>> >> RGB values introduced in maya 2016. Current version: {1}".format(_str_func,cgmGen.__mayaVersion__) 
        
        _b_RBGMode = True        
        if len(rgb) == 3:
            _color = rgb
        else:
            raise ValueError,">>{0}>> >> Too many rgb values: '{1}'".format(_str_func,rgb) 
        
    if index is not None:
        _color = index

    log.debug(">>{0}>> >> Color: {1} | rgbMode: {2}".format(_str_func,_color,_b_RBGMode))
    

    for i,s in enumerate(_shapes):
        mShape = r9Meta.MetaClass(s)
        
        mShape.overrideEnabled = True
        #attributes.doSetAttr(s,'overrideEnabled',True)
        
    
        if _b_RBGMode:
            mShape.overrideRGBColors = 1
            mShape.overrideColorRGB = _color
            #attributes.doSetAttr(s,'overrideRGBColors','RGB')#...brilliant attr naming here Autodesk...            
            #attributes.doSetAttr(s,'overrideColorsRGB',[1,1,1])

        else:
            if _b_2016Plus:
                mShape.overrideRGBColors = 0
            mShape.overrideColor = _color

def duplicate_shape(shape):
    """
    mc.duplicate can't duplicate a shape. This provides for it

    :parameters:
    	shape(str): shape to dupliate

    :returns
    	[shape,transform]

    """
    try:
        _str_func = 'duplicate_shape'
        _type = VALID.get_mayaType(shape)
        if _type == 'nurbsCurve':
            _bfr = mc.duplicateCurve(shape)
    
            parentObj = mc.listRelatives(shape, p=True, fullPath=True)
            mc.delete( mc.parentConstraint(parentObj,_bfr[0]))
    
            return _bfr
        else:
            log.debug(">>{0}>> >> mesh shape assumed...".format(_str_func))            
            _transform = SEARCH.get_transform(shape)
            _shapes = mc.listRelatives(_transform,s=True, fullPath = True)
            _idx = _shapes.index(coreNames.get_long(shape))
            log.info(_shapes)
            log.info(_idx)
            
            _bfr = mc.duplicate(shape)
            _newShapes = mc.listRelatives(_bfr[0], s=True, fullPath = True)
            _dupShape = _newShapes[_idx]
            _newShapes.pop(_idx)
            mc.delete(_newShapes)
            
            return [_bfr[0],_dupShape]
            
        
    except Exception,err:
        if not SEARCH.is_shape(shape):
            log.error(">>{0}>> >> Failure >> Not a shape: {1}".format(_str_func,shape))
        raise Exception,">>{0}>> >> failed! | err: {1}".format(_str_func,err)  
    
