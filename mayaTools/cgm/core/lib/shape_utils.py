"""
------------------------------------------
shape_utils: cgm.core.lib.shape_utils
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
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import name_utils as coreNames

reload(SHARED)
from cgm.lib import attributes
#NO...
#rig_utils, 

#>>> Utilities
#===================================================================
def parentShape_in_place(obj = None, shapeSource = None, keepSource = True, replaceShapes = False):
    """
    Shape parent a curve in place to a obj transform

    :parameters:
        obj(str): Object to modify
        shapeSource(str): Curve to shape parent
        keepSource(bool): Keep the curve shapeParented as well
        replaceShapes(bool): Whether to remove the obj's original shapes or not

    :returns
        success(bool)
    """   
    _str_func = 'parentShape_in_place'
    
    l_shapes = VALID.listArg(shapeSource)
    
    log.debug("|{0}| >> obj: {1} | shapeSource: {2} | keepSource: {3} | replaceShapes: {4}".format(_str_func,obj,shapeSource,keepSource,replaceShapes))  
    
    if replaceShapes:
        _l_objShapes = mc.listRelatives(obj, s=True)    
        if _l_objShapes:
            log.debug("|{0}| >> Removing obj shapes...| {1}".format(_str_func,_l_objShapes))
            mc.delete(_l_objShapes)
    
    mc.select (cl=True)
    for c in l_shapes:
        try:
            if not SEARCH.is_shape(c) and not mc.listRelatives(c, f= True,shapes=True, fullPath = True):
                raise ValueError,"Has no shapes"
            if coreNames.get_long(obj) == coreNames.get_long(c):
                raise ValueError,"Cannot parentShape self"
            
            _dup_curve = mc.duplicate(c)[0]
            _l_parents = SEARCH.get_all_parents(obj)
        
            try:_dup_curve = mc.parent(_dup_curve, world = True)[0]
            except:pass        
            
            #copy_pivot(_dup_curve,obj)
            piv_pos = mc.xform(obj, q=True, ws=True, rp = True)
            mc.xform(_dup_curve,ws=True, rp = piv_pos)  
            
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
        
            try:_dup_curve = mc.parent(_dup_curve, world = True)[0]
            except:pass
            
            mc.delete(group)
            
            #freeze for parent shaping 
            mc.makeIdentity(_dup_curve,apply=True,translate =True, rotate = True, scale=True)
            shape = mc.listRelatives (_dup_curve, f= True,shapes=True, fullPath = True)
            mc.parent (shape,obj,add=True,shape=True)
            mc.delete(_dup_curve)
            if not keepCurve:
                mc.delete(c)
        except Exception,err:
            log.error("{0} || obj:{1} failed to parentShape {2} >> err: {3}".format(_str_func,obj,c,err))  
    return True


def replace_shapes(obj = None, shapeSource = None, keepSource = True):
    """
    Replace the shapes of a transform with another

    :parameters:
        obj(str): Object to modify
        shapeSource(str): Shapes to shape parent to our target
        keepSource(bool): Keep the curve shapeParented as well

    :returns
        success(bool)
    """   
    _str_func = "replace_shapes"
    
    log.debug("|{0}| >> obj: {1} | shapeSource: {2} | keepSource: {3}".format(_str_func,obj,shapeSource,keepSource))  
    
    
    #Get shapes or target, remove them
    _l_objShapes = mc.listRelatives(obj, s=True)    
    if _l_objShapes:
        log.debug("|{0}| >> Removing obj shapes...| {1}".format(_str_func,_l_objShapes))
        mc.delete(_l_objShapes)
        
    #Parent shape source shapes
    parentShape_in_place(obj, shapeSource, )
    #KeepSource. Whether to delete the shapes when we've used them

    