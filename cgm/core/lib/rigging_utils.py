"""
rigging_utils
Josh Burton 
www.cgmonastery.com

"""
__MAYALOCAL = 'CORERIG'

# From Python =============================================================
import copy
import re
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID

from cgm.lib import search
from cgm.lib import rigging
from cgm.lib import locators #....CANNOT IMPORT LOCATORS - loop
from cgm.core.lib import attribute_utils as ATTR
#reload(ATTR)
from cgm.core.lib import name_utils as coreNames
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import transform_utils as TRANS
import cgm.core.lib.list_utils as LISTS

import cgm.core.lib.name_utils as NAMES
import cgm.core.lib.position_utils as POS
import cgm.core.lib.math_utils as COREMATH
#reload(COREMATH)
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
        raise ValueError("|{0}| >> Must have a {1}. | {1}: {2}".format(calledFrom,tag,arg)) 
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
        raise ValueError("|{0}| >> Must have a {1}. | {1}: {2}".format(calledFrom,tag,arg)) 
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
    
    obj = VALID.mNodeString(obj)
    source = VALID.mNodeString(source)
    
    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
    log.debug("|{0}| >> source:{1}".format(_str_func,source))
    log.debug("|{0}| >> rotateOrder:{1}".format(_str_func,rotateOrder))
    log.debug("|{0}| >> rotateAxis:{1}".format(_str_func,rotateAxis))
    
    if not rotateOrder and not rotateAxis:
        raise ValueError("|{0}| >> Both rotateOrder and rotateAxis are False. Nothing to do...".format(_str_func)) 
    
    #First gather children to parent away and shapes so they don't get messed up either
    _l_children = mc.listRelatives (obj, children = True,type='transform') or []
    _l_shapes = mc.listRelatives (obj, shapes = True, fullPath = True) or []
    _dup = False
    
    log.debug("|{0}| >> children:{1}".format(_str_func,_l_children))
    log.debug("|{0}| >> shapes:{1}".format(_str_func,_l_shapes))
    
    if _l_children:#...parent children to world as we'll be messing with stuff
        for i,c in enumerate(_l_children):
            _l_children[i] = parent_set(c,False)
    log.debug("|{0}| >> children:{1}".format(_str_func,_l_children))
            
    if _l_shapes:#...dup our shapes to properly shape parent them back
        _dup = mc.duplicate(obj, parentOnly = False)[0]
        #log.debug("|{0}| >> dup:{1}".format(_str_func,_dup))
        for s in _l_shapes:
            mc.delete(s)
            #shapeParent_in_place(_dup,s,keepSource=False)        
        
    #The meat of it...
    _restorePivotRP = False
    _restorePivotSP = False
    
    if rotateAxis:
        log.debug("|{0}| >> rotateAxis...".format(_str_func))        
        
        #There must be a better way to do this. Storing to be able to restore after matrix ops
        _restorePivotRP = mc.xform(obj, q=True, ws=True, rp = True)
        _restorePivotSP = mc.xform(obj, q=True, ws=True, sp = True)
        _restoreRO = mc.xform (obj, q=True, roo=True )
                    
        #We do our stuff with a locator to get simple transferrable values after matching parents and what not...
        loc = simpleLoc(source)
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
        log.debug("|{0}| >> rotateOrder...".format(_str_func))                  
        mc.xform(obj, roo = mc.xform (source, q=True, roo=True ), p=True)#...match rotateOrder
                
    if _dup:
        log.debug("|{0}| >> shapes back...: {1}".format(_str_func,_l_shapes))          
        #mc.delete(_l_shapes)
        shapeParent_in_place(obj,_dup)
        mc.delete(_dup)
        
    for c in _l_children:
        log.debug("|{0}| >> parent back...: '{1}'".format(_str_func,c))  
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
    
    obj = VALID.mNodeString(obj)
    source = VALID.mNodeString(source)
    
    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
    log.debug("|{0}| >> source:{1}".format(_str_func,source))
    
    #First gather children to parent away and shapes so they don't get messed up either
    _l_children = mc.listRelatives (obj, children = True,type='transform') or []
    _l_shapes = mc.listRelatives (obj, shapes = True, fullPath = True) or []
    _dup = False
    
    log.debug("|{0}| >> children:{1}".format(_str_func,_l_children))
    log.debug("|{0}| >> shapes:{1}".format(_str_func,_l_shapes))
    
    if _l_children:#...parent children to world as we'll be messing with stuff
        for i,c in enumerate(_l_children):
            _l_children[i] = parent_set(c,False)
    log.debug("|{0}| >> children:{1}".format(_str_func,_l_children))
            
    if _l_shapes:#...dup our shapes to properly shape parent them back
        _dup = mc.duplicate(obj, parentOnly = True)[0]
        for s in _l_shapes:
            shapeParent_in_place(_dup,s,keepSource=False)
        log.debug("|{0}| >> dup:{1}".format(_str_func,_dup))
        
        
    #The meat of it...        
    if rotateOrder or rotateAxis:
        log.debug("|{0}| >> orientation copy...".format(_str_func))                                  
        match_orientation(obj,source,rotateOrder,rotateAxis)
        
    if rotatePivot or scalePivot:    
        log.debug("|{0}| >> pivot copy...".format(_str_func))                                  
        copy_pivot(obj,source, rotatePivot, scalePivot)    
        

    if _dup:
        log.debug("|{0}| >> shapes back...: {1}".format(_str_func,_l_shapes))          
        #mc.delete(_l_shapes)
        shapeParent_in_place(obj,_dup,)
        mc.delete(_dup)
        
    for c in _l_children:
        log.debug("|{0}| >> parent back...: '{1}'".format(_str_func,c))  
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
    obj = VALID.mNodeString(obj)
    source = VALID.mNodeString(source)
    
    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    
    log.debug("|{0}| >> source:{1}".format(_str_func,source))
    
    if rotatePivot:
        pos = mc.xform(source, q=True, ws=True, rp = True)
        mc.xform(obj,ws=True, rp = pos)   
    if scalePivot:
        pos = mc.xform(source, q=True, ws=True, sp = True)
        mc.xform(obj,ws=True, sp = pos)   
    return True

parent_get = TRANS.parent_get
parent_set = TRANS.parent_set

def combineShapes(targets = [], keepSource = True, replaceShapes = False, snapFirst = False):
    try:
        for o in targets[:-1]:
            shapeParent_in_place(targets[-1],o,keepSource,replaceShapes,snapFirst)
        return targets[-1]
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())

@cgmGEN.Timer
def shapeParent_in_placeBAK(obj, shapeSource, keepSource = True, replaceShapes = False, snapFirst = False):
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
    obj = VALID.mNodeString(obj)
    log.debug("|{0}|  >> obj: {1} | shapeSource: {2} | keepSource: {3} | replaceShapes: {4}".format(_str_func,obj,shapeSource,keepSource,replaceShapes))  
    
    if replaceShapes:
        _l_objShapes = mc.listRelatives(obj, s=True, fullPath = True)    
        if _l_objShapes:
            log.debug("|{0}|  >> Removing obj shapes...| {1}".format(_str_func,_l_objShapes))
            mc.delete(_l_objShapes)
    
    mc.select (cl=True)
    #mc.refresh()    
    for c in l_shapes:
        try:
            _shapeCheck = SEARCH.is_shape(c)
            if not _shapeCheck and not mc.listRelatives(c, f= True,shapes=True, fullPath = True):
                raise ValueError("Has no shapes")
            if coreNames.get_long(obj) == coreNames.get_long(c):
                raise ValueError("Cannot parentShape self")
            
            if VALID.get_mayaType(c) == 'nurbsCurve':
                mc.ls(['%s.ep[*]'%(c)],flatten=True)
                #This is for a really weird bug in 2016 where offset curve shapes don't work right unless they're components are queried.
                
            if _shapeCheck:
                _dup_curve = duplicate_shape(c)[0]
                log.debug("|{0}|  >> shape duplicate".format(_str_func))                                  
                if snapFirst:
                    SNAP.go(_dup_curve,obj)
            else:
                log.debug("|{0}|  >> regular duplicate".format(_str_func))                  
                _dup_curve =  mc.duplicate(c)[0]
                for child in TRANS.children_get(_dup_curve,True):
                    mc.delete(child)
                if snapFirst:
                    SNAP.go(_dup_curve,obj)                
                
            _l_parents = SEARCH.get_all_parents(obj)
            ATTR.set_standardFlags(_dup_curve,lock=False,visible=True,keyable=True)
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
        except Exception as err:
            cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    return True

@cgmGEN.Timer
def shapeParent_in_place_matrix(obj, shapeSource, keepSource = True, replaceShapes = False, snapFirst = False):
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
    
    l_source = VALID.listArg(shapeSource)
    obj = VALID.mNodeString(obj)
    log.debug("|{0}|  >> obj: {1} | shapeSource: {2} | keepSource: {3} | replaceShapes: {4}".format(_str_func,obj,shapeSource,keepSource,replaceShapes))  
    
    if replaceShapes:
        _l_objShapes = mc.listRelatives(obj, s=True, fullPath = True)    
        if _l_objShapes:
            log.debug("|{0}|  >> Removing obj shapes...| {1}".format(_str_func,_l_objShapes))
            mc.delete(_l_objShapes)
    
    mc.select (cl=True)
    #mc.refresh()
    matrix_me = TRANS.worldMatrix_get(obj)
    pprint.pprint(matrix_me)
    for c in l_source:
        try:
            _shapeCheck = SEARCH.is_shape(c)
            if _shapeCheck:
                _dupBase = duplicate_shape(c)[0]
                log.debug("|{0}|  >> shape duplicate".format(_str_func))                                  
                if snapFirst:
                    SNAP.go(_dup_curve,obj)
                                        
            else:
                log.debug("|{0}|  >> regular duplicate".format(_str_func))                  
                _dupBase = mc.duplicate(c,po=False)[0]
                for child in TRANS.children_get(_dupBase,True):
                    mc.delete(child)
                if snapFirst:
                    SNAP.go(_dupBase,obj)
                
            mc.makeIdentity(_dupBase, apply=True,  scale=True)#translate=True, rotate=True,
            #TRANS.pivots_zeroTransform(_dupBase)
            matrix_tar = TRANS.worldMatrix_get(_dupBase)
            matrix_res = []
            for i,v in enumerate(matrix_tar):
                matrix_res.append(v * (matrix_me[i]*-1))

            mc.xform( _dupBase,m=matrix_res, ws=True,p=True)

            l_baseShapes = mc.listRelatives (_dupBase, f= True,shapes=True, fullPath = True)
            for i,s in enumerate(l_baseShapes):
                mc.parent (s,obj,add=True,shape=True)

            #mc.delete(_dupBase)
            #mc.delete(obj,ch=True)
            if not keepSource:
                mc.delete(c)
        except Exception as err:
            cgmGEN.cgmException(Exception,err)
    return True


#@cgmGEN.Timer
def shapeParent_in_place(obj, shapeSource, keepSource = True, replaceShapes = False, snapFirst = False):
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
    
    l_source = VALID.listArg(shapeSource)
    obj = VALID.mNodeString(obj)
    log.debug("|{0}|  >> obj: {1} | shapeSource: {2} | keepSource: {3} | replaceShapes: {4}".format(_str_func,obj,shapeSource,keepSource,replaceShapes))  
    
    if replaceShapes:
        _l_objShapes = mc.listRelatives(obj, s=True, fullPath = True)    
        if _l_objShapes:
            log.debug("|{0}|  >> Removing obj shapes...| {1}".format(_str_func,_l_objShapes))
            mc.delete(_l_objShapes)
    
    mc.select (cl=True)
    #mc.refresh()    
    for i,c in enumerate(l_source):
        try:
            l_nodes = []
            _shapeCheck = SEARCH.is_shape(c)
            #if not _shapeCheck and not mc.listRelatives(c, f= True,shapes=True, fullPath = True):
            #    raise ValueError,"Has no shapes"
            #if coreNames.get_long(obj) == coreNames.get_long(c):
                #raise ValueError,"Cannot parentShape self"
            #l_startShapes = mc.listRelatives (obj, f= True,shapes=True, fullPath = True)
 
            if _shapeCheck:
                _dup_curve = duplicate_shape(c)[0]
                _dupBase = duplicate_shape(c)[0]
                
                log.debug("|{0}|  >> shape duplicate".format(_str_func))                                  
                if snapFirst:
                    SNAP.go(_dup_curve,obj)
                                        
            else:
                log.debug("|{0}|  >> regular duplicate".format(_str_func))                  
                _dup_curve =  mc.duplicate(c,po=False,rc=True)[0]
                for child in TRANS.children_get(_dup_curve,True):
                    log.debug("|{0}|  >> Removing child: {1}".format(_str_func,child))
                    mc.delete(child)
                if snapFirst:
                    SNAP.go(_dup_curve,obj)
                    
                _dupBase = mc.duplicate(_dup_curve,po=False)
            
                #matrix_a = mc.xform( obj,q=True,m=True, ws=True )
                #mc.xform(_dup_curve, m=matrix_a,ws=True,p=True)
                #mc.makeIdentity(_dup_curve,apply=True,translate =True, rotate = True, scale=True)
            l_dupShapes = mc.listRelatives (_dup_curve, f= True,shapes=True, fullPath = True)
            l_baseShapes = mc.listRelatives (_dupBase, f= True,shapes=True, fullPath = True)
                
            for ii,s in enumerate(l_dupShapes):
                log.debug("|{0}|  >> blendshaping [{1}] | {2} | {3}".format(_str_func,i,ii,s))                                  
                newShape = mc.parent (s,obj,add=True,shape=True)
                try:node= mc.blendShape(l_baseShapes[ii],newShape[0], origin ='world')
                except:
                    node = None
                    log.error("|{0}|  >> FAILED to blendshape [{1}] | {2} | {3}".format(_str_func,i,ii,l_baseShapes[ii]))
                    shapeParent_in_placeBAK(obj,l_baseShapes[ii],False,False)
                if node:
                    mc.blendShape(node, edit=True, w=[(0,1.0)])
                    l_nodes.extend(node)
                    mc.delete(newShape,ch=True)                    

                #mc.delete(l_baseShapes[i])
                #mc.delete(node)

            mc.delete(_dup_curve,_dupBase)
            #mc.delete(l_nodes)
            #mc.delete(obj,ch=True)#...can't do this. Breaks other bits
            """
            for n in l_nodes:
                for plug in ATTR.get_driven(n,'outputGeometry') or []:
                    log.debug("|{0}|  >> Removing plug: {1}".format(_str_func,child))
                    ATTR.break_connection(plug)
                mc.delete(n)"""
            
            if not keepSource:
                mc.delete(c)
        except Exception as err:
            cgmGEN.cgmException(Exception,err)
    return True


def create_axisProxy(obj=None):
    """
    Make a local axis box around a given object so that you can then 
    
    """
    try:
        _str_func = 'create_axisProxy'
        _dag = VALID.getTransform(obj)
        if not _dag:
            raise ValueError("Must have a dag node. Obj: {0}".format(obj))
        if VALID.is_shape(obj):
            l_shapes = [obj]
        else:
            l_shapes = TRANS.shapes_get(_dag,True)
            
        _parent = TRANS.parent_get(_dag)
        _dup = mc.duplicate(l_shapes,po=False,rc=True)[0]
        #TRANS.pivots_recenter(_dup)
        _dup = TRANS.parent_set(_dup,False)
        ATTR.set_standardFlags(_dup,lock=False,keyable=True)
        #Get some values...
        l_reset = ['t','r','s','shear','rotateAxis']
        t = ATTR.get(_dup,'translate')
        r = ATTR.get(_dup,'rotate')
        s = ATTR.get(_dup,'scale')
        ra = ATTR.get(_dup,'rotateAxis')
        if ATTR.has_attr(_dup,'jointOrient'):
            l_reset.append('jointOrient')
            jo = ATTR.get(_dup,'jointOrient')
        o = TRANS.orient_get(_dup)
        shear = ATTR.get(_dup,'shear')
        _scaleLossy = TRANS.scaleLossy_get(_dag)
        
        #Reset our stuff before we make our bb...
        ATTR.reset(_dup,l_reset)        
        _size = POS.get_bb_size(_dup,True)

        #_proxy = create_proxyGeo('cube',COREMATH.list_div(_scaleLossy,_size))
        _proxy = create_proxyGeo('cube',_size)
        mc.makeIdentity(_proxy, apply=True, scale=True)
        
        
        #Now Put it back
        _dup = TRANS.parent_set(_dup, TRANS.parent_get(_dag))
        _proxy = TRANS.parent_set(_proxy, _dup)
        
        #_dup = TRANS.parent_set(_dup, TRANS.parents_get(_dag))
        SNAP.go(_dup,_dag)
        #ATTR.set(_dup,'s',(0,0,0))
        ATTR.reset(_dup,['s','shear'])

        
        ATTR.reset(_proxy,['t','r','s','shear','rotateAxis'])
        _proxy = TRANS.parent_set(_proxy, _dag)
        ATTR.reset(_proxy,['t','r','s','shear','rotateAxis'])
        #match_transform(_proxy,_dag)
        
        #SNAP.go(_proxy,_dag,pivot='bb')

        #cgmGEN.func_snapShot(vars())
        
        _proxy = TRANS.parent_set(_proxy, False)
        mc.delete(_dup)
        #match_transform(_proxy,_dag)
        return mc.rename(_proxy, "{0}_localAxisProxy".format(NAMES.get_base(_dag)))
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
def create_localAxisProxyBAK(obj=None):
    """
    Make a local axis box around a given object so that you can then 
    
    """
    try:
        _str_func = 'create_localAxisProxy'
        _dag = VALID.getTransform(obj)
        if not _dag:
            raise ValueError("Must have a dag node")
        l_shapes = TRANS.shapes_get(_dag)
        
        _dup = mc.duplicate(l_shapes,po=False,rc=True)[0]
        #_dup = TRANS.parent_set(_dup,False)
        
        #Get some values...
        t = ATTR.get(_dup,'translate')
        r = ATTR.get(_dup,'rotate')
        s = ATTR.get(_dup,'scale')
        o = TRANS.orient_get(_dup)
        shear = ATTR.get(_dup,'shear')
        _scaleLossy = TRANS.scaleLossy_get(_dag)
        
        #Reset our stuff before we make our bb...
        TRANS.orient_set(_dup,(0,0,0))
        ATTR.set(_dup,'scale',[1,1,1])
        _size = POS.get_bb_size(_dup,True)
        import cgm.core.lib.math_utils as COREMATH
        #reload(COREMATH)
        #_proxy = create_proxyGeo('cube',COREMATH.list_div(_scaleLossy,_size))
        _proxy = create_proxyGeo('cube',_size)
        mc.makeIdentity(_proxy, apply=True, scale=True)
        return
        #mc.xform(_proxy, scale = _size, worldSpace = True, absolute = True)
        
        #Parent it to the dup...
        _proxy = TRANS.parent_set(_proxy, _dup)
        ATTR.reset(_proxy,['t','r','shear'])
        
        #_dup = TRANS.parent_set(_dup, TRANS.parents_get(_dag))
        SNAP.go(_dup,_dag)
        ATTR.set(_dup,'shear',shear)
        #TRANS.scaleLocal_set(_dup, s)
        
        #mc.delete(_dup)
        #_scaleLossy = TRANS.scaleLossy_get(_dag)
        #import cgm.core.lib.math_utils as COREMATH
        #TRANS.scaleLocal_set(_dup, COREMATH.list_mult([-1.0,-1.0,-1.0],_scaleLossy,))
        #proxy = TRANS.parent_set(_proxy, False)
        cgmGEN.func_snapShot(vars())
        
        #ATTR.set(_dup,'translate',t)
        #ATTR.set(_dup,'rotate',r)
        #SNAP.go(_proxy[0],_dag)
        #ATTR.set(_proxy[0],'scale',_scaleLossy)
        
        #TRANS.scaleLocal_set(_dup,[1,1,1])
        #ATTR.set(_dup,'shear',[0,0,0])
        
        #_proxy = TRANS.parent_set(_proxy, False)        
        #TRANS.scaleLocal_set(_proxy,_scaleLossy)
        #ATTR.set(_dup,'scale',s)

        return mc.rename(_proxy, "{0}_localAxisProxy".format(NAMES.get_base(_dag)))
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())
    
        
_d_proxyCreate = {'cube':'nurbsCube',
                  'sphere':'sphere',
                  'cylinder':'cylinder',
                  'prism':'polyPrism',
                  'cone':'cone',
                  'torus':'torus'}

def create_proxyGeo(proxyShape = 'cube', size = [1,1,1], direction = 'z+',ch=True, bakeScale = True):
    try:
        #cube:sphere:cylinder:cone:torus
        _str_func = 'create_proxyGeo'
        
        _proxyShape = _d_proxyCreate.get(proxyShape,proxyShape)
        _call = getattr(mc,_proxyShape,None)
        if not _call:
            raise ValueError("Failed to find maya.cmds call {0}".format(_proxyShape))
        #if proxyShape not in _d_create.keys():
            #raise ValueError,"Unknown shape: {0}".format(proxyShape)
        
        _kws = {'ch':ch}
        
        
        if proxyShape in ['cube']:
            _kws['width'] = 1.0#size[0]
            _kws['ch'] = False
        if proxyShape in ['cylinder','sphere','cone','cylinder','torus']:
            _kws['radius'] =  1.0#max(size)/2.0
            _kws['axis'] = VALID.simpleAxis(direction).p_vector

        _res = _call(**_kws )
        
        if proxyShape == 'cube':
            _children = TRANS.children_get(_res[0])
            for i,c in enumerate(_children):
                _children[i] = TRANS.parent_set(c,False)
            combineShapes(_children + [_res[0]],keepSource=False,replaceShapes=False)        
        
        if size is not None:
            if VALID.isListArg(size):
                TRANS.scale_to_boundingBox(_res[0],size)
            else:
                if absoluteSize:
                    _f_current = DIST.get_bb_size(_res[0],True,True)
                    multiplier = size/_f_current
                    mc.scale(multiplier,multiplier,multiplier, _res[0],relative = True)
                    
                else:
                    mc.scale(size,size,size,_res[0],os=True)
            if bakeScale:
                mc.makeIdentity(_res[0], apply=True,s=1)    
        """
        if proxyShape == 'cube':
            _d_directionXRotates = {'x+':[0,0,0],'x-':[0,180,0],'y+':[0,0,90],'y-':[0,0,-90],'z+':[0,-90,0],'z-':[0,90,0]}
            _r_factor = _d_directionXRotates.get(direction)
            mc.rotate (_r_factor[0], _r_factor[1], _r_factor[2], _res[0], ws=True)"""
            #mc.makeIdentity(_res[0], apply=True,r =1, n= 1)        
        

        
        return _res
    except Exception as err:
        cgmGEN.cgmExceptCB(Exception,err,msg=vars())


def create_at(obj = None, create = 'null',midPoint = False, l_pos = [], baseName = 'created'):
    """
    Create a null matching a given obj
    
    :parameters:
        obj(str): Object to modify
        create(str): What to create

    :returns
        name(str)
    """
    try:
        
        _str_func = 'create_at'
        
        obj = VALID.mNodeString(obj)
        _create = create
        
        log.debug("|{0}| >> obj:{1}".format(_str_func,obj))  
        log.debug("|{0}| >> create:{1}".format(_str_func,_create))  
        
        if l_pos:
            l_use = []
            i_end = len(l_pos) +1
            for i,v in enumerate(l_pos):
                if i==i_end and v not in l_use:
                    l_use.append(v)
                else:
                    l_match = []
                    _key = i+1
                    for v2 in l_pos[_key:]:
                        if COREMATH.is_vector_equivalent(v,v2):
                            log.debug(cgmGEN.logString_msg(_str_func,"Matching values: {0} | {1}".format(v,v2)))
                            l_match.append(_key)
                    if _key not in l_match:
                        l_use.append(v)
            if not l_use:
                l_use = l_pos
        else:
            l_use = l_pos
            
        if midPoint:
            _d = TRANS.POS.get_midPointDict(obj)
            objTrans = _d['position']
            objRot = _d['rotation']
            objRotAxis = None
            
        elif _create in ['null','joint']:
            objTrans = TRANS.position_get(obj)#mc.xform (obj, q=True, ws=True, rp=True)
            objRot = TRANS.orient_get(obj)#mc.xform (obj, q=True, ws=True, ro=True)
            objRotAxis = mc.xform(obj, q=True, ws = True, ra=True)   
                
        if _create == 'null':
            _created = mc.group (w=True, empty=True)
            if not midPoint:
                mc.xform(_created, roo = mc.xform(obj, q=True, roo=True ))#...match rotateOrder    
                
            mc.move (objTrans[0],objTrans[1],objTrans[2], [_created])
            mc.xform(_created, ws=True, ro= objRot,p=False)
            if objRotAxis:
                mc.xform(_created, ws=True, ra= objRotAxis,p=False)  
            
            ATTR.set(_created,'scale',[1,1,1])
            
        elif _create == 'joint':
            mc.select(cl=True)
            _created = mc.joint()
            if not midPoint:        
                mc.xform(_created, roo = mc.xform(obj, q=True, roo=True ))#...match rotateOrder    
            mc.move (objTrans[0],objTrans[1],objTrans[2], [_created])
            mc.xform(_created, ws=True, ro= objRot,p=False)
            if objRotAxis:
                mc.xform(_created, ws=True, ra= objRotAxis,p=False)
            
        elif _create in ['curve','curveLinear','linearTrack','cubicTrack']:
            if not l_use:
                l_use = []
                #_sel = mc.ls(sl=True,flatten=True)
                for i,o in enumerate(obj):
                    p = TRANS.position_get(o)
                    if p not in l_use:
                        log.debug("|{0}| >> {3}: {1} | pos: {2}".format(_str_func,o,p,i)) 
                        l_use.append(p)
            
            if len(l_use) <= 1:
                raise ValueError("Must have more than one position to create curve")
            if _create in ['linearTrack','cubicTrack']:
                _d = 1
                _trackCurve = mc.curve(d=1,p=l_use)
                
                _trackCurve = mc.rename(_trackCurve,"{0}_trackCurve".format(baseName))
        
                l_clusters = []
                #_l_clusterParents = [mStartHandle,mEndHandle]
                for i,cv in enumerate(mc.ls(['{0}.cv[*]'.format(_trackCurve)],flatten=True)):
                    _res = mc.cluster(cv, n = '{0}_{1}_cluster'.format(baseName,i))
                    _res[1] = TRANS.parent_set( "|{0}".format(_res[1]), obj[i])
                    ATTR.set(_res[1],'visibility',0)
                    l_clusters.append(_res)
                    ATTR.set(_res[1],'visibility',False)
                    
                if _create == 'cubicTrack':
                    mc.rebuildCurve(_trackCurve, d=3, keepControlPoints=0,ch=1,n="reparamRebuild")
                    
                return _trackCurve,l_clusters
                
                    
                    
            elif _create == 'curve':
                if len(l_use) >= 3:
                    knot_len = len(l_use)+2#-1		                    
                    _created = mc.curve (d=3, ep = l_use, k = [i for i in range(0,knot_len)], os=True)
                else:
                    knot_len = len(l_use)+1#-1		                    
                    _created = mc.curve (d=2, ep = l_use, k = [i for i in range(0,knot_len)], os=True)
                    
            else:
                _created = mc.curve (d=1, ep = l_use, k = [i for i in range(0,len(l_use))], os=True)
                
            log.debug("|{0}| >> created: {1}".format(_str_func,_created))  
            
        elif _create == 'locator':
            raise NotImplementedError("locators not done yet")
        else: 
            raise NotImplementedError("|{0}| >> unknown mode: {1}".format(_str_func,_create))  
    
        mc.select(_created)
        return _created
    except Exception as err:
        cgmGEN.cgmException(Exception,err)
    
def create_joint_at(obj = None):
    """
    Create a joint matching a given obj
    
    :parameters:
        obj(str): Object to modify

    :returns
        name(str)
    """

    return create_at(obj, create = 'joint')

 
group_me = TRANS.group_me


def mirror_controlShape(source = None, target=None, colorDirection = 'right',controlType = 'main'):
    _str_func = "mirror_controlShape"
    if target is None:
        _sel = mc.ls(sl=True)
        if len(_sel) == 2:
            return mirror_controlShape(_sel[0],_sel[1])

    if not source:raise ValueError("|{0}|  >> Must have a source".format(_str_func))
    if not target:raise ValueError("|{0}|  >> Must have a target".format(_str_func))    
    _dup_curve =  mc.duplicate(source)[0]
    for child in TRANS.children_get(_dup_curve,True):
        mc.delete(child)
    ATTR.set_standardFlags(_dup_curve,lock=False,keyable=True,visible=True)
    _grp = mc.group(em=True)
    _dup_curve = TRANS.parent_set(_dup_curve,_grp)
    ATTR.set(_grp,'scaleX',-1)
    _dup_curve = TRANS.parent_set(_dup_curve,False)  
    mc.makeIdentity(_dup_curve,apply=True,translate =True, rotate = True, scale=False)
    return
    shapeParent_in_place(target,_dup_curve,True,True)
    mc.delete(_grp)
    
    colorControl(target,colorDirection,controlType)
    mc.select(target)
    return target
    

def push_controlResizeObj(target = None):
    _str_func = "push_controlResizeObj"
    if target is None:
        _sel = mc.ls(sl=True)
        if _sel:
            _res = []
            for t in _sel:
                _res.append(push_controlResizeObj(t))
            mc.select(_res)
            return _res   
    if not target:raise ValueError("|{0}|  >> Must have a target".format(_str_func))
    
    if ATTR.has_attr(target, 'cgmControlResizerSource'):
        source = ATTR.get_message(target,'cgmControlResizerSource')
        if not source:
            raise ValueError("|{0}|  >> no cgmControlResizerSource data on target: {1}".format(_str_func,target))
        source = source[0]
        shapeParent_in_place(source,target,keepSource=False,replaceShapes=True)
        if ATTR.has_attr(source,'cgmControlResizer'):
            ATTR.delete(source,'cgmControlResizer')
        ATTR.set(source,'template',0)        
        mc.select(source)
        return source

        
    else:
        raise ValueError("|{0}|  >> no cgmControlResizerSource attr on target: {1}".format(_str_func,target))
    



def create_controlResizeObj(target=None):
    _str_func = "create_controlResizeObj"
    if target is None:
        _sel = mc.ls(sl=True)
        if _sel:
            _res = []
            for t in _sel:
                _res.append(create_controlResizeObj(t))
            return _res
                
    if not target:raise ValueError("|{0}|  >> Must have a target".format(_str_func))
    
    if ATTR.get_message(target,'cgmControlResizer'):
        return ATTR.get_message(target,'cgmControlResizer')
    
    handle = create_at(target,'null')
    ATTR.set_message(target,'cgmControlResizer',handle)
    ATTR.set_message(handle,'cgmControlResizerSource',target)
    
    handle = mc.rename(handle, NAMES.base(target) + '_cgmResizer')
    
    shapeParent_in_place(handle,target)
    
    ATTR.set(target,'template',1)
    
    return handle
    
    
def get_curve_color(target = None):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns the colors used on the shapes of a curve as a list in order
    of volume used

    ARGUMENTS:
    curve(string

    RETURNS:
    Success(bool)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    """ first get the shapes """
    _str_func = "get_curve_color"
    
    if not target:raise ValueError("|{0}|  >> Must have a target".format(_str_func))
        
    l_targets = VALID.listArg(target)
    
    _res = []
    _b_RBGMode = False
    _b_2016Plus = False
    if cgmGEN.__mayaVersion__ >=2016:
        _b_2016Plus = True
    
    _colors = {}
    _color = False
    for t in l_targets:
        _shapes = []
        #If it's accepable target to color
        
        #mTarget = r9Meta.MetaClass(target, autoFill=False)
        
        if ATTR.has_attr(t,'overrideEnabled'):
            log.debug("|{0}|  >> overrideEnabled  on target...".format(_str_func))            
            _shapes.append(t)
            _bfr = mc.listRelatives(t, s=True, fullPath=True)
            if _bfr:
                _shapes.extend(_bfr)
                
        if not _shapes:
            raise ValueError("|{0}|  >> Not a shape and has no shapes: '{1}'".format(_str_func,t))        
        
        for i,s in enumerate(_shapes):
            mShape = r9Meta.MetaClass(s)
            if mShape.overrideEnabled:
                if _b_2016Plus:
                    if mShape.overrideRGBColors:
                        #if mShape.overrideRGBColors:
                        _color = mShape.overrideColorRGB
                    else:
                        _color = mShape.overrideColor
                else:
                    _color = mShape.overrideColor
                    
                if _color:
                    return _color
    return _color
    
    
    """
    try:
        shapes = mc.listRelatives(curve,shapes=True,fullPath=True)
        colorsCatcher = []
        for shape in shapes:
            colorsCatcher.append(mc.getAttr(shape+'.overrideColor'))
        colorVolumes = {}
        for color in colorsCatcher:
            volmesBuffer = 0
            for shape in shapes:
                if (mc.getAttr(shape+'.overrideColor')) == color:
                    volmesBuffer = volmesBuffer + mc.arclen(shape)
            colorVolumes[color] = volmesBuffer

        orderedDictList = dictionary.returnDictionarySortedToList (colorVolumes,True)
        returnList = []
        orderedDictList.reverse()
        for set in orderedDictList:
            returnList.append(set[0])
        return returnList
    except Exception as error:
        log.error("%s >> Failed to find color, returning default. Error: %s"%(_str_func,error))
        return [17]"""
    
    
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
    if not target:raise ValueError("|{0}|  >> Must have a target".format(_str_func))
    
    l_targets = VALID.listArg(target)
    
    for t in l_targets:
        _shapes = []
        #If it's accepable target to color
        
        #mTarget = r9Meta.MetaClass(target, autoFill=False)
        
        if ATTR.has_attr(t,'overrideEnabled'):
            log.debug("|{0}|  >> overrideEnabled  on target...".format(_str_func))            
            _shapes.append(t)
        if pushToShapes:
            _bfr = mc.listRelatives(t, s=True, fullPath=True)
            if _bfr:
                _shapes.extend(_bfr)
                
        if not _shapes:
            raise ValueError("|{0}|  >> Not a shape and has no shapes: '{1}'".format(_str_func,t))        
        
        #log.debug(key)
        #log.debug(index)
        #log.debug(rgb)
        if index is None and rgb is None and key is None:
            raise ValueError("|{0}|  >> Must have a value for index,rgb or key".format(_str_func))
        
        #...little dummy proofing..
        if key:
            _type = type(key)
            
            if not VALID.stringArg(key):#_type not in [str,str] :
                log.debug("|{0}|  >> Not a string arg for key...".format(_str_func))
                
                if rgb is None and issubclass(_type,list) or issubclass(_type,tuple):
                    log.debug("|{0}|  >> vector arg for key...".format(_str_func))            
                    rgb = key
                    key = None
                elif index is None and issubclass(_type,int):
                    log.debug("|{0}|  >> int arg for key...".format(_str_func))            
                    index = key
                    key = None
                else:
                    raise ValueError("|{0}|  >> Not sure what to do with this key arg: {1}".format(_str_func,key))
        
        _b_RBGMode = False
        _b_2016Plus = False
        if cgmGEN.__mayaVersion__ >=2016:
            _b_2016Plus = True
            
        if key is not None:
            _color = False
            if _b_2016Plus:
                log.debug("|{0}|  >> 2016+ ...".format(_str_func))            
                _color = SHARED._d_colors_to_RGB.get(key,False)
                
                if _color:
                    rgb = _color
            
            if _color is False:
                log.debug("|{0}|  >> Color key not found in rgb dict checking index...".format(_str_func))
                _color = SHARED._d_colors_to_index.get(key,False)
                if _color is False:
                    raise ValueError("|{0}|  >> Unknown color key: '{1}'".format(_str_func,key)) 
                    
        if rgb is not None:
            if not _b_2016Plus:
                raise ValueError("|{0}|  >> RGB values introduced in maya 2016. Current version: {1}".format(_str_func,cgmGEN.__mayaVersion__)) 
            
            _b_RBGMode = True        
            if len(rgb) == 3:
                _color = rgb
            else:
                raise ValueError("|{0}|  >> Too many rgb values: '{1}'".format(_str_func,rgb)) 
            
        if index is not None:
            _color = index
    
        log.debug("|{0}|  >> Color: {1} | rgbMode: {2}".format(_str_func,_color,_b_RBGMode))
        
    
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
    
def override_clear(target = None, pushToShapes = True):
    """
    Clear override flags on target and shapes if you choose
    
    :parameters
        target(str): What to color - shape or transform with shapes
        pushToShapes(bool): Push the overrides to shapes of passed transforms

    :returns
        info(dict)
    """   
    _str_func = "override_clear"
    if not target:raise ValueError("|{0}|  >> Must have a target".format(_str_func))

    _shapes = []
    
    mTarget = r9Meta.MetaClass(target, autoFill=False)
    
    if mTarget.hasAttr('overrideEnabled'):
        log.debug("|{0}|  >> overrideEnabled  on target...".format(_str_func))            
        _shapes.append(mTarget.mNode)
        
    if pushToShapes:
        _bfr = mc.listRelatives(target, s=True, fullPath=True)
        if _bfr:
            _shapes.extend(_bfr)
            
    if not _shapes:
        raise ValueError("|{0}|  >> Not a shape and has no shapes: '{1}'".format(_str_func,target))        

    for i,s in enumerate(_shapes):
        mShape = r9Meta.MetaClass(s)
        try:
            mShape.overrideEnabled = False
        except Exception as err:
            log.warning("|{0}|  >> target failed: {1} | err: {2}".format(_str_func,s,err))        
            
    return True
        
            
def getControlShader(direction = 'center', controlType = 'main',
                     transparent = False, proxy = False,
                     directProxy = False,shaderNode='phong'):
    """
    Proxy mode modifies the base value and setups up a different shader
    """
    _str_func = getControlShader
    
    if directProxy:
        _node = "cgmShader_directProxy"
    else:
        if controlType == 'puppetmesh':
            _node = "cgmShader_{0}".format(controlType.capitalize())
        else:
            _node = "cgmShader_{0}{1}".format(direction,controlType.capitalize())
            
        if transparent:
            _node = _node + '_trans'
        if proxy:
            _node = _node + '_proxy'
        
    log.debug(_node)
    _set = False
    if not mc.objExists(_node):
        _node = mc.shadingNode(shaderNode,n =_node, asShader = True)
        _set = mc.sets(renderable=True, noSurfaceShader = True, em=True, name = _node + 'SG')
        ATTR.connect("{0}.outColor".format(_node), "{0}.surfaceShader".format(_set))
        
        if directProxy:
            ATTR.set(_node,'ambientColorR',0)
            ATTR.set(_node,'ambientColorG',0)
            ATTR.set(_node,'ambientColorB',0)
            ATTR.set(_node,'transparency',1.0)
            ATTR.set(_node,'incandescence',0)
        else:
            if controlType == 'puppetmesh':
                
                _rgb = [.5,.5,.5]
                
                _d = {'diffuse':.65,
                      'specularColor':[0.142857,0.142857,0.142857]}
                for a,v in list(_d.items()):
                    try:
                        ATTR.set(_node,a,v)
                    except Exception as err:
                        log.error(err)
            else:
                _color = SHARED._d_side_colors[direction][controlType]
                _rgb = SHARED._d_colors_to_RGB[_color]

            if proxy and controlType not in ['pupil']:
                #_rgb = [v * .75 for v in _rgb]
                _hsv = [v for v in get_HSV_fromRGB(_rgb[0],_rgb[1],_rgb[2])]
                _hsv[1] = .6
                _hsv[2] = .8                
                #_hsv = [v * .5]
                _rgb = get_RGB_fromHSV(_hsv[0],_hsv[1],_hsv[2])
                ATTR.set(_node,'diffuse',.8)
            else:
                ATTR.set(_node,'diffuse',.497)
                
            ATTR.set(_node,'colorR',_rgb[0])
            ATTR.set(_node,'colorG',_rgb[1])
            ATTR.set(_node,'colorB',_rgb[2])
            
            ATTR.set(_node,'ambientColorR',_rgb[0]*.1)
            ATTR.set(_node,'ambientColorG',_rgb[1]*.1)
            ATTR.set(_node,'ambientColorB',_rgb[2]*.1)
            
            ATTR.set(_node,'specularColorR',.16)
            ATTR.set(_node,'specularColorG',.16)
            ATTR.set(_node,'specularColorB',.16)
            
            if transparent:
                _d = {'transparency':.6,
                      'incandescence':0,
                      'diffuse':0.1,
                      'cosinePower':.95,
                      'specularColorR':0,
                      'specularColorG':0,
                      'specularColorB':0,
                      'reflectivity':0
                      }
                
                for a,v in list(_d.items()):
                    try:
                        ATTR.set(_node,a,v)
                    except Exception as err:
                        log.error(cgmGEN.logString_msg(_str_func, "Failed to set: {0} | {1} | {2}".format(a,v,err)))


            if controlType in ['pupil']:
                ATTR.set(_node,'diffuse',0)
                ATTR.set(_node,'specularColorR',0)
                ATTR.set(_node,'specularColorG',0)
                ATTR.set(_node,'specularColorB',0)                
                
      
    if not _set:
        _set = ATTR.get_driven(_node,'outColor',True)[0] 
        
    return _node, _set
    
def get_HSV_fromRGB(rValue = 0, gValue = 0, bValue = 0, getNode = False):
    _node = mc.createNode('rgbToHsv')
    ATTR.set(_node,'inRgbR',COREMATH.Clamp(float(rValue),0,1.0))
    ATTR.set(_node,'inRgbG',COREMATH.Clamp(float(gValue),0,1.0))
    ATTR.set(_node,'inRgbB',COREMATH.Clamp(float(bValue),0,1.0))
    res = ATTR.get(_node,'outHsv')[0]
    
    if getNode:
        return _node,res
    
    mc.delete(_node)
    return res
    
def get_RGB_fromHSV(rValue = 0, gValue = 0, bValue = 0, getNode = False):
    _node = mc.createNode('hsvToRgb')
    ATTR.set(_node,'inHsvB',COREMATH.Clamp(float(bValue),0.0001,1.0))
    ATTR.set(_node,'inHsvG',COREMATH.Clamp(float(gValue),0.0001,1.0))
    ATTR.set(_node,'inHsvR',COREMATH.Clamp(float(rValue),0.000001,360.0))
    res = ATTR.get(_node,'outRgb')[0]
    
    if getNode:
        return _node, res
    
    mc.delete(_node)
    return res
    
def colorControl(target = None, direction = 'center', controlType = 'main', pushToShapes = True,
                 rgb = True, shaderSetup = True,shaderOnly=False,transparent = False,proxy=False, directProxy=False):
    """
    Sets the override color on shapes and more
    
    :parameters
        target(str): What to color - shape or transform with shapes
        direction
        controlType
        pushToShapes
        rgb
        shaderSetup
        transparent
        proxy - offsets the color down to not match curve color exactly
        directProxy(bool) - Setpu transparent shader for 'invisible' controls
        

    :returns
        info(dict)
    """   
    
    _str_func = "color_control"
    if not target:raise ValueError("|{0}|  >> Must have a target".format(_str_func))
    l_targets = VALID.listArg(target)
    
    if rgb:
        _color = SHARED._d_side_colors[direction][controlType]
    else:
        _color = SHARED._d_side_colors_index[direction][controlType]
        
            
    _shader = False
    _set = False

    if shaderSetup:
        _shader, _set = getControlShader(direction,controlType,transparent,proxy,directProxy)
        
    for t in l_targets:
        log.debug("|{0}| >> t: {1} ...".format(_str_func,t))
        _type = VALID.get_mayaType(t)
        log.debug("|{0}| >> shapes: {1} ...".format(_str_func,TRANS.shapes_get(t,True)))  
        log.debug("|{0}| >> type: {1} ...".format(_str_func,_type))
        
        if not shaderOnly:
            if rgb:
                override_color(t,_color,pushToShapes=pushToShapes )
            else:
                _v = SHARED._d_colors_to_index[_color]
                override_color(t,index=_v,pushToShapes=pushToShapes )
            
        if shaderSetup:
            mc.sets(t, edit=True, remove = 'initialShadingGroup')
            
            if _type in ['nurbsSurface','mesh']:
                mc.sets(t, e=True, forceElement = _set)                
            else:
                for s in TRANS.shapes_get(t,True):
                    log.debug("|{0}| >> s: {1} ...".format(_str_func,s))  
                    _type = VALID.get_mayaType(s)
                    if _type in ['nurbsSurface','mesh']:
                        mc.sets(s, edit=True, forceElement = _set)
                        mc.sets(s, remove = 'initialShadingGroup')
                        try:
                            mc.disconnectAttr ('{0}.instObjGroups.objectGroups'.format(s),
                                               'initialShadingGroup.dagSetMembers')
                        except:pass
                        
                        
                    else:
                        log.debug("|{0}|  >> Not a valid target: {1} | {2}".format(_str_func,s,_type))
                    
        mc.sets(t, edit=True, remove = 'initialShadingGroup')
    return True

def color_mesh(target=None, direction = 'center', controlType = 'main', transparent = False,proxy=False, directProxy=False):
    _str_func = "color_mesh"    
    if not target:raise ValueError("|{0}|  >> Must have a target".format(_str_func))
    l_targets = VALID.listArg(target)
    
    _shader, _set = getControlShader(direction,controlType,transparent,proxy,directProxy)    
    #_shader, _set = getControlShader(None,'puppetmesh',False,False,False)
            
    for t in l_targets:
        log.debug("|{0}| >> t: {1} ...".format(_str_func,t))
        _type = VALID.get_mayaType(t)
        log.debug("|{0}| >> shapes: {1} ...".format(_str_func,TRANS.shapes_get(t,True)))  
        log.debug("|{0}| >> type: {1} ...".format(_str_func,_type))
        
            
        mc.sets(t, edit=True, remove = 'initialShadingGroup')
        
        if _type in ['nurbsSurface','mesh']:
            mc.sets(t, e=True, forceElement = _set)                
        else:
            for s in TRANS.shapes_get(t,True):
                log.debug("|{0}| >> s: {1} ...".format(_str_func,s))  
                _type = VALID.get_mayaType(s)
                if _type in ['nurbsSurface','mesh']:
                    mc.sets(s, edit=True, forceElement = _set)
                    mc.sets(s, remove = 'initialShadingGroup')
                    try:
                        mc.disconnectAttr ('{0}.instObjGroups.objectGroups'.format(s),
                                           'initialShadingGroup.dagSetMembers')
                    except:pass
                else:
                    log.debug("|{0}|  >> Not a valid target: {1} | {2}".format(_str_func,s,_type))
        mc.sets(t, edit=True, remove = 'initialShadingGroup')
    return True             


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
            _l_shapes = mc.listRelatives(_bfr[0],s=True,f=True)
            
            return [_bfr[0]] + _l_shapes
        else:
            log.debug("|{0}|  >> mesh shape assumed...".format(_str_func))            
            _transform = SEARCH.get_transform(shape)
            _shapes = mc.listRelatives(_transform,s=True, fullPath = True)
            _idx = _shapes.index(coreNames.get_long(shape))

            
            _bfr = mc.duplicate(shape)
            _newShapes = mc.listRelatives(_bfr[0], s=True, fullPath = True)
            _dupShape = _newShapes[_idx]
            _newShapes.pop(_idx)
            mc.delete(_newShapes)
            
            return [_bfr[0],_dupShape]
            
        
    except Exception as err:
        pprint.pprint(vars())
        if not SEARCH.is_shape(shape):
            log.error("|{0}|  >> Failure >> Not a shape: {1}".format(_str_func,shape))
        raise Exception("|{0}|  >> failed! | err: {1}".format(_str_func,err))  
    
def is_mirrorable(obj = None):
    """
    Return if an object is tagged for mirrorable
        
    :returns
        status(bool)
    """   
    _str_func = 'is_mirrorable'
    
    obj = valid_arg_single(obj, 'obj', _str_func)
        
    l_ = ['mirrorSide','mirrorIndex','mirrorAxis']
    for a in l_:
        if not ATTR.has_attr(obj,a):
            log.debug("|{0}| lacks attr: {1}".format(_str_func,a))
            return False
    return True

def mirror(obj = None, mode = ''):
    """
    Use r9anim call to mirror
        
    :returns
        status(bool)
    """   
    _str_func = 'mirror'
    
    obj = valid_arg_single(obj, 'obj', _str_func)
    try:    
        r9Anim.MirrorHierarchy([obj]).mirrorData(mode = mode)
    except Exception as err:
        _mirrorable = is_mirrorable(obj)
        log.error("|{0}| >> failure. obj: {1} | mirrorable: {2} | mode: {3} | err: {4}".format(_str_func,obj,_mirrorable,mode,err))



def matchValue_iterator(matchObj = None, matchAttr = None, drivenObj = None, drivenAttr = None, driverAttr = None, 
                        minIn = -180, maxIn = 180, maxIterations = 40, matchValue = None):
    """
    Started with Jason Schleifer's afr js_iterator and have 'tweaked'
    """
    if type(minIn) not in [float,int]:raise Exception("matchValue_iterator>>> bad minIn: %s"%minIn)
    if type(maxIn) not in [float,int]:raise Exception("matchValue_iterator>>> bad maxIn: %s"%maxIn)

    __matchMode__ = False
    #>>> Data gather and arg check        
    mi_matchObj = cgmMeta.validateObjArg(matchObj,cgmMeta.cgmObject,noneValid=True)
    d_matchAttr = cgmMeta.validateAttrArg(matchAttr,noneValid=True)
    if mi_matchObj:
        __matchMode__ = 'matchObj'
        minValue = minIn
        maxValue = maxIn 

    elif d_matchAttr:
        __matchMode__ = 'matchAttr'
    elif matchValue is not None:
        __matchMode__ = 'value'
    else:
        raise Exception("matchValue_iterator>>> No match given. No matchValue given")

    __drivenMode__ = False
    mi_drivenObj = cgmMeta.validateObjArg(drivenObj,cgmMeta.cgmObject,noneValid=True)
    d_drivenAttr = cgmMeta.validateAttrArg(drivenAttr,noneValid=True)    
    if mi_drivenObj:#not an object match but a value
        __drivenMode__ = 'object'
    elif d_drivenAttr:
        __drivenMode__ = 'attr'
        mPlug_driven = d_drivenAttr['mi_plug']
        f_baseValue = mPlug_driven.value	
        minRange = float(f_baseValue - 10)
        maxRange = float(f_baseValue + 10)  
        mPlug_driven
        log.debug("matchValue_iterator>>> Attr mode. Attr: %s  | baseValue: %s "%(mPlug_driven.p_combinedShortName,f_baseValue))						
    else:
        raise Exception("matchValue_iterator>>> No driven given")

    d_driverAttr = cgmMeta.validateAttrArg(driverAttr,noneValid=False)
    mPlug_driver = d_driverAttr['mi_plug']
    if not mPlug_driver:
        raise Exception("matchValue_iterator>>> No driver")	

    log.debug("matchValue_iterator>>> Source mode: %s | Target mode: %s | Driver: %s"%(__matchMode__,__drivenMode__,mPlug_driver.p_combinedShortName))  
    #===========================================================================================================
    #>>>>>>> Meat
    #>>> Check autokey
    b_autoFrameState = mc.autoKeyframe(q=True, state = True)
    if b_autoFrameState:
        mc.autoKeyframe(state = False)

    minValue = float(minIn)
    maxValue = float(maxIn)  
    f_lastClosest = None
    f_lastValue = None
    cnt_sameValue = 0
    b_matchFound = None
    b_firstIter = True
    d_valueToSetting = {}

    #Source type: value
    for i in range(maxIterations):
        if __matchMode__ == 'value':
            if __drivenMode__ == 'attr':
                log.debug("matchValue_iterator>>> Step : %s | min: %s | max: %s | baseValue: %s | current: %s"%(i,minValue,maxValue,f_baseValue,mPlug_driven.value))  					
                if cgmMath.isFloatEquivalent(mPlug_driven.value,matchValue,3):
                    log.debug("matchValue_iterator>>> Match found: %s == %s | %s: %s | step: %s"%(mPlug_driven.p_combinedShortName,matchValue,mPlug_driver.p_combinedShortName,minValue,i))  			    
                    b_matchFound = minValue
                    break
                f_currentDist = abs(matchValue-mPlug_driven.value)
                mPlug_driver.value = minValue#Set to min
                f_minDist = abs(matchValue-mPlug_driven.value)#get Dif
                f_minSetValue = mPlug_driven.value
                mPlug_driver.value = maxValue#Set to max
                f_maxDist = abs(matchValue-mPlug_driven.value)#Get dif
                f_maxSetValue = mPlug_driven.value

                f_half = ((maxValue-minValue)/2.0) + minValue#get half
                #First find range
                if f_minSetValue > matchValue or f_maxSetValue < matchValue:
                    log.error("Bad range, alternate range find. minSetValue = %s > %s < maxSetValue = %s"%(f_minSetValue,matchValue,f_maxSetValue))

                if not cgmMath.isFloatEquivalent(matchValue,0) and not cgmMath.isFloatEquivalent(minValue,0) and not cgmMath.isFloatEquivalent(f_minSetValue,0):
                    #if none of our values are 0, this is really fast
                    minValue = (minValue * matchValue)/f_minSetValue
                    log.debug("matchValue_iterator>>> Equated: %s"%minValue)		    
                    f_closest = f_minDist
                    mPlug_driver.value = minValue#Set to min			
                else:	
                    if f_minDist>f_maxDist:#if min dif greater, use half as new min
                        if f_half < minIn:
                            raise Exception("half min less than minValue")
                            f_half = minIn
                        minValue = f_half
                        #log.debug("matchValue_iterator>>>Going up")
                        f_closest = f_minDist
                    else:
                        if f_half > maxIn:
                            raise Exception("half max less than maxValue")			    
                            f_half = maxIn			
                        maxValue = f_half
                        #log.debug("matchValue_iterator>>>Going down")  
                        f_closest = f_maxDist

                #Old method
                """
		mPlug_driver.value = minValue#Set to min
		f_minDist = abs(matchValue-mPlug_driven.value)#get Dif
		f_minSetValue = mPlug_driven.value
		mPlug_driver.value = maxValue#Set to max
		f_maxDist = abs(matchValue-mPlug_driven.value)#Get dif
		f_maxSetValue = mPlug_driven.value

		f_half = ((maxValue-minValue)/2.0) + minValue#get half	

		#First find range
		if not cgmMath.isFloatEquivalent(matchValue,0) and not cgmMath.isFloatEquivalent(minValue,0) and not cgmMath.isFloatEquivalent(f_minSetValue,0):
		    #if none of our values are 0, this is really fast
		    minValue = (minValue * matchValue)/f_minSetValue
		    log.debug("matchValue_iterator>>> Equated: %s"%minValue)		    
		    f_closest = f_minDist
		    mPlug_driver.value = minValue#Set to min		    
		elif b_firstIter:
		    log.debug("matchValue_iterator>>> first iter. Trying matchValue: %s"%minValue)		    		    
		    b_firstIter = False
		    minValue = matchValue
		    f_closest = f_minDist		    
		elif f_minSetValue > matchValue or f_maxSetValue < matchValue:
		    log.debug("matchValue_iterator>>> Finding Range....")		    
		    if matchValue < mPlug_driven.value:
			#Need to shift our range down
			log.debug("matchValue_iterator>>> Down range: minSetValue: %s"%f_minSetValue)
			f_baseValue = f_maxDist		    
			minValue = f_baseValue - f_minDist
			maxValue = f_baseValue + f_minDist
			f_closest = f_minDist			
		    elif matchValue > mPlug_driven.value:
			#Need to shift our range up
			log.debug("matchValue_iterator>>> Up range: maxSetValue: %s"%f_maxSetValue)  
			f_baseValue = f_minDist		    
			minValue = f_baseValue - f_maxDist
			maxValue = f_baseValue + f_maxDist
			f_closest = f_maxDist			
		else:	
		    if f_minDist>f_maxDist:#if min dif greater, use half as new min
			if f_half < minIn:f_half = minIn
			minValue = f_half
			#log.debug("matchValue_iterator>>>Going up")
			f_closest = f_minDist
		    else:
			if f_half > maxIn:f_half = maxIn			
			maxValue = f_half
			#log.debug("matchValue_iterator>>>Going down")  
			f_closest = f_maxDist"""

                log.debug("matchValue_iterator>>>f1: %s | f2: %s | f_half: %s"%(f_minDist,f_maxDist,f_half))  
                log.debug("#"+'-'*50)

                if f_closest == f_lastClosest:
                    cnt_sameValue +=1
                    if cnt_sameValue >3:
                        log.error("matchValue_iterator>>> Value unchanged. Bad Driver. lastValue: %s | currentValue: %s"%(f_lastValue,mPlug_driven.value))		
                        break
                else:
                    cnt_sameValue = 0 
                f_lastClosest = f_closest
            else:
                log.warning("matchValue_iterator>>> driven mode not implemented with value mode: %s"%__drivenMode__)
                break		

        #>>>>>matchObjMode
        elif __matchMode__ == 'matchObj':
            pos_match = mc.xform(mi_matchObj.mNode, q=True, ws=True, rp=True)
            pos_driven = mc.xform(mi_drivenObj.mNode, q=True, ws=True, rp=True)
            log.debug("matchValue_iterator>>> min: %s | max: %s | pos_match: %s | pos_driven: %s"%(minValue,maxValue,pos_match,pos_driven))  						    
            if cgmMath.isVectorEquivalent(pos_match,pos_driven,2):
                log.debug("matchValue_iterator>>> Match found: %s <<pos>> %s | %s: %s | step: %s"%(mi_matchObj.getShortName(),mi_drivenObj.getShortName(),mPlug_driver.p_combinedShortName,minValue,i))  			    
                b_matchFound = mPlug_driver.value
                break

            mPlug_driver.value = minValue#Set to min
            pos_min = mc.xform(mi_drivenObj.mNode, q=True, ws=True, rp=True)
            #f_minDist = cgmMath.mag( cgmMath.list_subtract(pos_match,pos_min))#get Dif
            f_minDist = distance.returnDistanceBetweenObjects(mi_drivenObj.mNode,mi_matchObj.mNode)

            mPlug_driver.value = maxValue#Set to max
            pos_max = mc.xform(mi_drivenObj.mNode, q=True, ws=True, rp=True)
            f_maxDist = distance.returnDistanceBetweenObjects(mi_drivenObj.mNode,mi_matchObj.mNode)
            f_half = ((maxValue-minValue)/2.0) + minValue#get half	

            if f_minDist>f_maxDist:#if min dif greater, use half as new min
                minValue = f_half
                f_closest = f_minDist
            else:
                maxValue = f_half
                f_closest = f_maxDist	

            if f_minDist==f_maxDist:
                minValue = minValue + .1

            if f_closest == f_lastClosest:
                cnt_sameValue +=1
                if cnt_sameValue >3:
                    log.error("matchValue_iterator>>> Value unchanged. Bad Driver. lastValue: %s | currentValue: %s"%(f_lastValue,mPlug_driver.value))		
                    break
            else:
                cnt_sameValue = 0 
            f_lastClosest = f_closest

            log.debug("matchValue_iterator>>>f1: %s | f2: %s | f_half: %s"%(f_minDist,f_maxDist,f_half))  
            log.debug("#"+'-'*50)	    

        else:
            log.warning("matchValue_iterator>>> matchMode not implemented: %s"%__matchMode__)
            break

    #>>> Check autokey back on
    if b_autoFrameState:
        mc.autoKeyframe(state = True) 

    if b_matchFound is not None:
        return b_matchFound
    #log.warning("matchValue_iterator>>> Failed to find value for: %s"%mPlug_driven.p_combinedShortName)    
    return False

def simpleLoc(obj,forceBBCenter=False):
    _loc = mc.spaceLocator()[0]
    
    _d = POS.get_info(obj,forceBBCenter)

    ATTR.set(_loc,'rotateOrder', _d['rotateOrder'])
    objRot = _d['rotation']
    objRotAxis = _d['rotateAxis']
    
    POS.set(_loc,_d['position'])
    
    mc.rotate (objRot[0], objRot[1], objRot[2], _loc, ws=True)
    for i,a in enumerate(['X','Y','Z']):
        ATTR.set(_loc, 'rotateAxis{0}'.format(a), objRotAxis[i])
        
    return mc.rename(_loc, "{}_loc".format(NAMES.clean(NAMES.get_base(obj))))


