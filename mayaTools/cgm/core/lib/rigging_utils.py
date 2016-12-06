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
from cgm.core.lib import attribute_utils as coreAttr

#>>> Utilities
#===================================================================
def copy_transform(target = None, source = None):
    """
    Copy the pivot and axis from one object to another
    
    :parameters:
        target(str): Object to modify
        sourceObject(str): object to copy from

    :returns
        success(bool)
    """   
    _str_func = 'copy_transform'
        
    log.debug("{0} || target:{1}".format(_str_func,target))    
    log.debug("{0} || source:{1}".format(_str_func,source))
    
    #First gather children to parent away and shapes so they don't get messed up either
    _l_children = mc.listRelatives (target, children = True,type='transform')
    _l_shapes = mc.listRelatives (target, shapes = True)
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
   
    copy_pivot(target,source)
    
    #Take care of rotation
    mc.makeIdentity(target,a = True, rotate = True)
    
    objRot = mc.xform (source, q=True, ws=True, ro=True)
    #mc.xform(target, ws = True, ra = objRot)
    for i,a in enumerate(['X','Y','Z']):
        attributes.doSetAttr(target, 'rotateAxis{0}'.format(a), objRot[i])
                
    if _dup:
        mc.delete(_l_shapes)
        #from cgm.lib import curves
        #curves.parentShapeInPlace(target, _dup)
        parentShape_in_place(target,_dup)
        mc.delete(_dup)
        
    for c in _l_children:
        log.info("{0} || parent back...: '{1}'".format(_str_func,c))  
        log.info("{0} || target:{1}".format(_str_func,target))    
        
        parent_set(c,target)  
        
    return target

def copy_pivot(target = None, source = None, rp = True):
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
        
    log.debug("{0} || target:{1}".format(_str_func,target))    
    log.debug("{0} || source:{1}".format(_str_func,source))
    
    pos = mc.xform(source, q=True, ws=True, rp = rp)
    mc.xform(target,ws=True, piv = pos)   

    return True

def parent_set(target = None, parent = False):
    """
    Takes care of parenting transforms and returning new names
    
    :parameters:
        target(str): Object to modify
        parent(str): Parent object or False for world

    :returns
        new name(str)
    """   
    _str_func = 'parent_obj'
        
    log.debug("{0} || target:{1}".format(_str_func,target))    
    log.debug("{0} || parent:{1}".format(_str_func,parent))
    
    _parents = mc.listRelatives(target,parent=True,type='transform')
    
    if parent:
        try:
            return mc.parent(target,parent)[0]
        except Exception,err:
            log.error("{0} || Failed to parent: {1}".format(_str_func, err))    
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

def parent_set(target = None, parent = False):
    """
    Takes care of parenting transforms and returning new names
    
    :parameters:
        target(str): Object to modify
        parent(str): Parent object or False for world

    :returns
        new name(str)
    """   
    _str_func = 'parent_obj'
        
    log.debug("{0} || target:{1}".format(_str_func,target))    
    log.debug("{0} || parent:{1}".format(_str_func,parent))
    
    _parents = mc.listRelatives(target,parent=True,type='transform')
    
    if parent:
        try:
            return mc.parent(target,parent)[0]
        except Exception,err:
            log.error("{0} || Failed to parent: {1}".format(_str_func, err))    
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

    workingCurve = parent_set(_dup_curve,group)

    # zero out the group 
    mc.setAttr((group+'.tx'),pos[0])
    mc.setAttr((group+'.ty'),pos[1])
    mc.setAttr((group+'.tz'),pos[2])
    mc.setAttr((group+'.rx'),0)
    mc.setAttr((group+'.ry'),0)
    mc.setAttr((group+'.rz'),0)
    mc.setAttr((group+'.rotateAxisX'),0)
    mc.setAttr((group+'.rotateAxisY'),0)
    mc.setAttr((group+'.rotateAxisZ'),0)
     
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
    shape = mc.listRelatives (_dup_curve, f= True,shapes=True)
    mc.parent (shape,target,add=True,shape=True)
    mc.delete(_dup_curve)

    return True



    