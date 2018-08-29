"""
------------------------------------------
snap_utils: cgm.core.lib.transform_utils
Author: Josh Burton & David Bokser
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
#CANNOT import Rigging, CURVES, SEARCH, NAMETOOLS
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.distance_utils as DIST
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import position_utils as POS
reload(POS)
from cgm.core.lib import name_utils as NAME
from cgm.core.lib import snap_utils as SNAP

from cgm.core.lib import euclid as EUCLID
from cgm.core.lib import attribute_utils as ATTR
reload(MATH)
reload(DIST)

#Link up some of our ther functions for ease of call
position_get = POS.get
position_set = POS.set

translate_get = POS.get_local
translate_set = POS.set_local

snap = SNAP.go
aim = SNAP.aim
aim_atPoint = SNAP.aim_atPoint
aim_atMidPoint = SNAP.aim_atMidPoint
verify_aimAttrs = SNAP.verify_aimAttrs

bbSize_get = POS.get_bb_size
bbCenter_get = POS.get_bb_center

vector_byAxis = MATH.get_obj_vector
position_getByAxisDistance = DIST.get_pos_by_axis_dist

"""
    _d ['scalePivot']=get(target,'sp','world')
    _d ['rotation']= mc.xform (_target, q=True, ws=True, ro=True)
    _d ['rotateOrder']=mc.xform (_target, q=True, roo=True )
    _d ['rotateAxis'] = mc.xform(_target, q=True, os = True, ra=True)
"""


"""

"""
_d_set_modes = {'local':['l','object','os'],'world':['w','absolute']}
def set_random(node=None, posLocal = False, rotLocal = False, posWorld = False, rotWorld = False, 
               relative = False, 
               scale = False, scaleUniform = False, rotateOrder = False,
               posRange = [1,10], rotRange = [-45,45], scaleRange = [.5,5]):
    """
    Set random values on a given node. Useful for testing purposes
    
    :parameters:
        node(str): node to query
        posLocal(bool) - local move
        rotLocal(bool) - local rotate
        
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'set_random'
    
    _node = VALID.mNodeString(node)
    #_mode = VALID.kw_fromDict(mode,_d_set_modes,noneValid=False,calledFrom=_str_func)
    log.debug("|{0}| >> node: [{1}] | posLocal: {2}| posWorld: {3} | rotLocal: {4} | rotWorld: {5} | scale: {6} | rotOrder: {7}".format(_str_func,_node,posLocal,posWorld,rotLocal,rotWorld,scale,rotateOrder))
    log.debug("|{0}| >> relative: {4} | posRange: {1} | rotRange: {2} | scaleRange: {3}".format(_str_func,posRange,rotRange,scaleRange,relative))
             
    
    if posLocal + posWorld + rotLocal + rotWorld + scale + scaleUniform + rotateOrder == 0:
        raise ValueError,"No options specified"
    if relative:
        raise NotImplemented,"relative not implemented"
    
    if posLocal or posWorld:
        _pos = [random.uniform(posRange[0],posRange[1]) for i in range(3)]
        log.debug("|{0}| >> randomPos: {1}".format(_str_func,_pos)) 
        
        if posLocal:
            translate_set(_node, _pos)
        if posWorld:
            position_set(_node, _pos)
            
    if rotLocal or rotWorld:
        _rot = [random.uniform(rotRange[0],rotRange[1]) for i in range(3)]
        log.debug("|{0}| >> randomRot: {1}".format(_str_func,_rot)) 
        
        if rotLocal:
            rotate_set(_node,_rot)
        if rotWorld:
            orient_set(_node,_rot)
            
    if scale:
        _scale = [random.uniform(scaleRange[0],scaleRange[1]) for i in range(3)]
        log.debug("|{0}| >> randomScale: {1}".format(_str_func,_scale)) 
        
        ATTR.set(_node,'scale',_scale)
        
    if scaleUniform:
        _v = random.uniform(scaleRange[0],scaleRange[1]) 
        _scale = [_v,_v,_v]
        log.debug("|{0}| >> randomScale: {1}".format(_str_func,_scale)) 
        ATTR.set(_node,'scale',_scale)
        
    if rotateOrder:
        ATTR.set(_node,'rotateOrder', random.choice(range(1,5)))
        
    
    return
    """
    for attr in 'translateX','translateY','translateZ','rotateX','rotateY','rotateZ':
    self.pCube.__setattr__(attr,random.choice(range(1,10)))
    for attr in 'scaleX','scaleY','scaleZ':
        self.pCube.__setattr__(attr,random.choice([1,.5,.75]))
    self.pCube.rotateOrder = random.choice(range(1,5))#0 not an option for accurate testing

    for attr in 'translateX','translateY','translateZ','rotateX','rotateY','rotateZ':
        self.nCube.__setattr__(attr,random.choice(range(1,10)))
    for attr in 'scaleX','scaleY','scaleZ':
        self.nCube.__setattr__(attr,random.choice([1,.5,.75]))
    self.nCube.rotateOrder = random.choice(range(1,5))"""


def rotatePivot_get(node=None, asEuclid = False):
    """
    Query the world space rotatePivot of a given node
    
    :parameters:
        node(str): node to query
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'rotatePivot_get'
    
    node = VALID.mNodeString(node)
    
    _res = mc.xform(node, q=True, ws=True, rp = True)
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,_res,node))
    
    if asEuclid:
        return EUCLID.Vector3(_res[0],_res[1],_res[2])
    return _res




def scalePivot_get(node=None, asEuclid = False):
    """
    Query the world space rotatePivot of a given node
    
    :parameters:
        node(str): node to query
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'scalePivot_get'
    
    node = VALID.mNodeString(node)
    
    _res = mc.xform(node, q=True, ws=True, sp = True)
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,_res,node))
    
    if asEuclid:
        return EUCLID.Vector3(_res[0],_res[1],_res[2])
    return _res

def pivots_recenter(node=None):
    """
    Recenter the rp and scp viots
    
    :parameters:
        node(str): node to query

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'pivots_recenter'
    
    _node = VALID.mNodeString(node)
    
    mc.xform (_node,  ws=True, cp= True, p=True)
    
def pivots_zeroTransform(node=None):
    """
    Recenter the rp and scp pivots using ztp xform call
    
    :parameters:
        node(str): node to query

    """   
    _str_func = 'rotatePivot_set'
    
    _node = VALID.mNodeString(node)
    
    mc.xform (_node,  ws=True, ztp= True, p=False)
    
def rotatePivot_set(node=None, new_pos = None):
    """
    Set the rotatePivot of a given obj in worldSpace
    
    :parameters:
        node(str): node to query
        new_pos(double3): Value to set. May be Euclid.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'rotatePivot_set'
    
    _node = VALID.mNodeString(node)
    
    try:new_pos = VALID.euclidVector3List(new_pos)
    except:pass
    
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,new_pos,_node))
    
    mc.xform (_node,  ws=True, rp= new_pos, p=False)
    
def scalePivot_set(node=None, new_pos = None):
    """
    Set the rotatePivot of a given obj in worldSpace
    
    :parameters:
        node(str): node to query
        new_pos(double3): Value to set. May be Euclid.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'rotatePivot_set'
    
    _node = VALID.mNodeString(node)
    
    try:new_pos = VALID.euclidVector3List(new_pos)
    except:pass
    
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,new_pos,_node))
    
    mc.xform (_node,  ws=True, sp= new_pos, p=True)

def rotateOrder_get(node=None):
    """
    Query the local rotation/euler of a given obj
    
    :parameters:
        node(str): node to query
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'rotateOrder_get'
    
    node = VALID.mNodeString(node)
    
    _res = mc.xform (node, q=True, roo=True )
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,_res,node))
    
    return _res

def rotateOrder_set(node=None, rotateOrder = None, preserve = True):
    """
    Set the rotateOrder of an object
    
    :parameters:
        node(str): node to query
        rotateOrder(str)
        preserve(bool) - Whether to set with preserve or not
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'rotateOrder_set'
    
    node = VALID.mNodeString(node)
    
    _res = mc.xform(node, roo=rotateOrder,p=preserve)
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,_res,node))
    
    return _res


def rotateAxis_get(node=None, asEuclid = False):
    """
    Query the local rotateAxis of a given node
    
    :parameters:
        node(str): node to query
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'rotateAxis_get'
    
    node = VALID.mNodeString(node)
    
    _res = mc.xform(node, q=True, ws = True, ra=True)
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,_res,node))
    
    if asEuclid:
        return EUCLID.Vector3(_res[0],_res[1],_res[2])
    return _res

def rotateAxis_set(node=None, new_rot = None, preserve = False):
    """
    Set the rotateAxis of a given obj
    
    :parameters:
        node(str): node to query
        new_rot(double3): Value to set. May be Euclid.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'rotateAxis_set'
    
    _node = VALID.mNodeString(node)
    
    try:new_rot = VALID.euclidVector3List(new_rot)
    except:pass
    
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,new_rot,_node))
    
    mc.xform (_node,  ws=True, ra= new_rot,p=preserve)


def rotate_get(node=None, asEuclid = False):
    """
    Query the local rotation/euler of a given obj
    
    :parameters:
        node(str): node to query
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'rotate_get'
    
    node = VALID.mNodeString(node)
    
    _res = ATTR.get(node,'rotate')
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,_res,node))
    
    if asEuclid:
        return EUCLID.Vector3(_res[0],_res[1],_res[2])
    return _res

eulerAngles_get = rotate_get#...for you Dave

def rotate_set(node=None, new_rot = None):
    """
    Set the local rotation/euler of a given obj
    
    :parameters:
        node(str): node to query
        new_rot(double3): Value to set. May be Euclid.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'rotate_set'
    
    _node = VALID.mNodeString(node)
    
    try:new_rot = VALID.euclidVector3List(new_rot)
    except:pass
    
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,new_rot,_node))
    
    ATTR.set(_node,'rotate',new_rot)
    

eulerAngles_get = rotate_get#...for you Dave
eulerAngles_set = rotate_set



def orient_get(node=None, asEuclid = False):
    """
    Query the world orientation of a given transform
    
    :parameters:
        node(str): node to query
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'orientWorld_get'
    
    node = VALID.mNodeString(node)
    
    _res = mc.xform (node, q=True, ws=True, ro=True)
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,_res,node))
    
    if asEuclid:
        return EUCLID.Vector3(_res[0],_res[1],_res[2])
    return _res

def orient_set(node=None, new_rot = None):
    """
    Set the worldspace orientation of a given obj
    
    :parameters:
        node(str): node to query
        new_rot(double3): Value to set. May be Euclid.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'orient_set'
    
    _node = VALID.mNodeString(node)
    
    try:new_rot = VALID.euclidVector3List(new_rot)
    except:pass
    
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,new_rot,_node))
    mc.xform (_node,  ws=True, ro=new_rot, p = False)

def orientObject_get(node=None, asEuclid = False):
    """
    Query the local rotation/euler of a given obj
    
    :parameters:
        node(str): node to query
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'orient_get'
    
    node = VALID.mNodeString(node)
    
    _res = mc.xform (node, q=True, os=True, ro=True)
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,_res,node))
    
    if asEuclid:
        return EUCLID.Vector3(_res[0],_res[1],_res[2])
    return _res

def orientObject_set(node=None, new_rot = None):
    """
    Set the object space orientation of a given obj
    
    :parameters:
        node(str): node to query
        new_rot(double3): Value to set. May be Euclid.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'orient_set'
    
    _node = VALID.mNodeString(node)
    
    try:new_rot = VALID.euclidVector3List(new_rot)
    except:pass
    
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,new_rot,_node))
    mc.xform (_node,  os=True, ro=new_rot, p = False) 
    
    
def scale_to_size(node = None, size = 1.0, mode = 'bb'):
    _str_func = 'scale_to_size'
    if mode == 'shape':
        currentSize = DIST.get_bb_size(node,True,True)
    else:
        boundingBoxSize =  DIST.get_bb_size(node)
        log.info("|{0}| >> boundingBoxSize = {1}".format(_str_func,boundingBoxSize))        
        currentSize = max(boundingBoxSize)
    log.info('currentSize: {0}'.format(currentSize))
    
    multiplier = size/currentSize
    mc.scale(multiplier,multiplier,multiplier, node, relative = True)
    #mc.makeIdentity(node,apply=True,scale=True)   
    
def scale_to_boundingBox(node = None, box = [1,1,1],shapes=True):
    """
    Scale an object to a bounding box size
    
    :parameters:
        node(str): node to modify
        box(double3): Box to scale to

    :returns
        None
    """
    _str_func = 'orient_set'
    
    mc.makeIdentity(node, apply =True, scale = True)    
    _bb_current = DIST.get_bb_size(node,shapes)
    _l_scale = []
    for i,v in enumerate(_bb_current):
        v_b = box[i]
        if v_b is None:
            _l_scale.append( v )            
        else:
            try:_l_scale.append( box[i]/v )
            except:_l_scale.append( v ) 
    #mc.scale(_l_scale[0],_l_scale[1],_l_scale[2], node, absolute = True)
    mc.xform(node, scale = _l_scale, worldSpace = True, absolute = True)
    
    
    
def scaleLocal_get(node=None, asEuclid = False):
    """
    Query the local scale of a given obj
    
    :parameters:
        node(str): node to query
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'scaleLocal_get'
    
    node = VALID.mNodeString(node)
    
    _res = ATTR.get(node,'scale')
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,_res,node))
    
    if asEuclid:
        return EUCLID.Vector3(_res[0],_res[1],_res[2])
    return _res
def scaleLocal_set(node=None, new_scale = [1,1,1]):
    """
    Set the local scale of a given obj
    
    :parameters:
        node(str): node to query
        new_scale(double3): Value to set. May be Euclid.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'scaleLocal_set'
    
    _node = VALID.mNodeString(node)
    
    try:new_scale = VALID.euclidVector3List(new_scale)
    except:pass
    
    log.debug("|{0}| >> [{2}] = {1}".format(_str_func,new_scale,_node))
    
    ATTR.set(_node,'scale',new_scale)
    
    
def scaleLossy_get(node=None, asEuclid = False):
    """
    Query the local scale of a given obj
    
    :parameters:
        node(str): node to query
        asEuclid(bool): whether to return a EUCLID.Vector3

    :returns
        rotation(vector/asEuclid.Vector3)
    """   
    _str_func = 'scaleLossy_get'
    
    _node = VALID.mNodeString(node)
    
    _res = scaleLocal_get(_node,True)
    
    for p in parents_get(_node):
        log.debug("|{0}| >> [{1}] | * {3} || lossyScale: [{2}].".format(_str_func,_node,_res,p))        
        _res = _res * scaleLocal_get(p,True)
    
    if asEuclid:
        return _res
    return [_res.x,_res.y,_res.z]

"""
lossyScale = self.localScale
    for parent in self.parents:
        lossyScale = lossyScale * parent.localScale
    return lossyScale
"""


#>>>Heirarchy ===================================================================================================
def parent_set(node = None, parent = False):
    """
    Takes care of parenting transforms and returning new names.
    
    :parameters:
        node(str): Object to modify
        parent(str): Parent nodeect or False for world

    :returns
        correct name(str)
    """   
    _str_func = 'parent_set'
    node = VALID.mNodeString(node)
    if parent:
        parent = VALID.mNodeString(parent)
   
    log.debug("|{0}| >> node:{1}".format(_str_func,node))    
    log.debug("|{0}| >> parent:{1}".format(_str_func,parent))
    
    _parents = mc.listRelatives(node,parent=True,type='transform')
    
    if parent:
        try:
            return mc.parent(node,parent)[0]
        except Exception,err:
            log.debug("|{0}| >> Failed to parent '{1}' to '{2}' | err: {3}".format(_str_func, node,parent, err))    
            return node
    else:
        if _parents:
            return mc.parent(node, world = True)[0]
        else:
            return node
    raise ValueError,"Shouldn't have arrived here."

def parent_get(node = None, fullPath = True):
    """
    Takes care of parenting transforms and returning new names
    
    :parameters:
        node(str): Object to modify
        
    :returns
        correct name(str)
    """   
    _str_func = 'parent_get'
    
    node = VALID.mNodeString(node)
        
    log.debug("|{0}| >> node:{1}".format(_str_func,node))    
    
    _parents = mc.listRelatives(node,parent=True, type='transform', fullPath = fullPath) or False
    
    if _parents:
        return _parents[0]
    return False

parents_get = SNAP.SEARCH.parents_get
'''
def parents_get(node = None, fullPath = True):
    _str_func = 'parents_get'
    _node =  VALID.mNodeString(node)
    
    _l_parents = []
    tmpObj = _node
    noParent = False
    while noParent == False:
        tmpParent = mc.listRelatives(tmpObj,allParents=True,fullPath=True)
        if tmpParent:
            if len(tmpParent) > 1:
                raise ValueError,"Resolve what to do with muliple parents...{0} | {1}".format(_node,tmpParent)
            _l_parents.append(tmpParent[0])
            tmpObj = tmpParent[0]
        else:
            noParent = True
    if not fullPath:
        return [NAME.get_short(o) for o in _l_parents]
    return _l_parents 
'''
def shapes_get(node = None, fullPath = False):
    """
    Get the immediate children of a given node
    
    :parameters:
        node(str): Object to check
        fullPath(bool): Whether you just want full path names or not

    :returns
        children(list)
    """   
    _str_func = 'shapes_get'
    _node =  VALID.mNodeString(node)

    return mc.listRelatives(_node, s=True, fullPath = fullPath) or []
  
def children_get(node = None, fullPath = False):
    """
    Get the immediate children of a given node
    
    :parameters:
        node(str): Object to check
        fullPath(bool): Whether you just want full path names or not

    :returns
        children(list)
    """   
    _str_func = 'children_get'
    _node =  VALID.mNodeString(node)
    return mc.listRelatives (_node, children = True,type='transform',fullPath=fullPath) or []

def descendents_get(node = None, fullPath = False):
    """
    Get all children of a given node
    
    :parameters:
        node(str): Object to check
        fullPath(bool): Whether you just want full path names or not

    :returns
        children(list)
    """   
    _str_func = 'descendents_get'
    _node =  VALID.mNodeString(node)

    return  mc.listRelatives (_node, allDescendents = True,type='transform',fullPath=fullPath) or []

def child_create(node, childName = None):
    """
    Create a child transform 
    
    :parameters:
        node(str): Object to check
        childName(str): what to call it

    :returns
        newChild(str)
    """   
    _str_func = 'child_create'
    _node =  VALID.mNodeString(node)  
    
    if childName == None:
        childName = NAME.short(_node)+"_child"
        
    child = mc.group(em=True,n = childName)
    snap(child,_node,rotateAxis=True,rotateOrder=True)

    parent_set(child,_node)
    rotate_set(child,[0,0,0])
    scaleLocal_set(child,[0,0,0])
    return child    

def parent_create(node,parentName = None):
    """
    Create a child transform 
    
    :parameters:
        node(str): Object to check
        parentName(str): what to call it
    
    :returns
        newParent(str)
    """   
    _str_func = 'parent_create'
    _node =  VALID.mNodeString(node)  
    
    if parentName == None:
        parentName = NAME.short(_node)+"_grp"
        
    parent = mc.group(em=True,n = parentName)
    snap(parent,_node,rotateAxis=True,rotateOrder=True)
    
    parent = parent_set(parent, parent_get(_node))
    parent_set(_node,parent)

    return parent

def parent_orderedTargets(targetList=None, reverse = False):
    """
    """
    _str_func = 'parent_orderedTargets'
    _sel =False
    if not targetList:
        targetList = mc.ls(sl=True,flatten = False)
        _sel=True
        log.info("|{0}| >> targetList: {1}".format(_str_func,targetList))
        
    for i,o in enumerate(targetList):
        targetList[i] = parent_set(o,False)
        
    if len(targetList) <= 1:
        raise ValueError("|{0}| >> Must have more objects. targetList: {1}".format(_str_func,targetList))
    
    if reverse is False:
        targetList.reverse()
        log.info("|{0}| >> reverse: {1}".format(_str_func,targetList))
    
    for i,o in enumerate(targetList[:-1]):
        targetList[i] = parent_set(o,targetList[i+1])
    #else:
    #    for i,o in enumerate(targetList[1:]):
    #        targetList[i] = parent_set(o,targetList[i-1])        
    
    if _sel:
        targetList.reverse()
        mc.select(targetList)
    return targetList


    
def is_childTo(node, parent):
    """
    Query whether a node is child to a given parent
    
    :parameters:
        node(str): node to query
        parent(str): parent to check against

    :returns
        status(bool)
    """   
    _str_func = 'is_childTo'
    _node =  VALID.mNodeString(node)
    if parent in [None,False]:
        return False
    
    _parent = VALID.mNodeString(parent)
    _p_long = NAME.get_long(_parent)
    
    for p in parents_get(_node,True):
        if p == _p_long:
            return True
        
    return False

def is_parentTo(node, child):
    """
    Query whether a node is parent to a given child
    
    :parameters:
        node(str): node to query
        child(str): parent to check against

    :returns
        status(bool)
    """   
    _str_func = 'is_parentTo'
    _node =  VALID.mNodeString(node)
    if child in [None,False]:
        return False
    
    _child = VALID.mNodeString(child)
    _c_long = NAME.get_long(_child)
    
    for p in descendents_get(_node,True):
        if p == _c_long:
            return True
    return False

def get_listPathTo(node, node2,fullPath = True):
    """
    Get the list path from one object to another
    
    :parameters:
        node(str): node to query
        node2(str): node to check against

    :returns
        status(bool)
    """   
    _str_func = 'get_listPathTo'
    _node =  VALID.mNodeString(node)
    _node2 = VALID.mNodeString(node2)
    
    _nodeLong = NAME.get_long(_node)
    
    _res = []
    if is_parentTo(_node, _node2):
        log.debug("|{0}| >> isParent mode".format(_str_func))
        _node2Long = NAME.get_long(_node2)
        l_parents = parents_get(_node2,True)
        
        self_index = l_parents.index(_nodeLong)
        l_parents = l_parents[:self_index+1]
        
        log.debug("|{0}| >> index {1} | {2}".format(_str_func,self_index,l_parents))
        
        l_parents.reverse()

        for o in l_parents:
            _res.append(o)		    
            if o == _node2Long:
                break	
        _res.append(_node2Long)

    elif is_childTo(_node,_node2):
        log.debug("|{0}| >> isChild mode".format(_str_func))
        
        l_parents = parents_get(_node,True)
        #l_parents.reverse()
        _res.append(_nodeLong)
        for o in l_parents:
            _res.append(o)		    
            if o == _nodeLong:
                break	
    else:
        return False
    
    if not fullPath:
        return [NAME.get_short(o) for o in _res]
    return _res

def siblings_get(node = None, fullPath = True):
    """
    Get all the parents of a given node where the last parent is the top of the heirarchy
    
    :parameters:
        node(str): Object to check
        fullPath(bool): Whether you want long names or not

    :returns
        siblings(list)
    """   
    _str_func = 'siblings_get'
    _node =  VALID.mNodeString(node)
    
    _l_res = []
    _type = VALID.get_mayaType(_node)
    
    log.debug("|{0}| >> node: [{1}] | type: {2}".format(_str_func,_node,_type))

    if VALID.is_shape(_node):
        log.debug("|{0}| >> shape...".format(_str_func))
        _long = NAME.long(_node)
        for s in shapes_get(_node,True):
            if s != _long:
                _l_res.append(s)
        
    elif not VALID.is_transform(_node):
        log.debug("|{0}| >> not a transform...".format(_str_func))   
        if VALID.is_component(_node):
            log.debug("|{0}| >> component...".format(_str_func))   
            _comp = VALID.get_component(_node)
            log.debug("|{0}| >> component: {1}".format(_str_func,_comp))   
            _comb = "{0}.{1}".format(_comp[1],_comp[0])
            for c in mc.ls("{0}.{1}[*]".format(_comp[1],_comp[2]),flatten=True):
                if str(c) != _comb:
                    _l_res.append(c)
        else:
            _long = NAME.long(_node)            
            log.debug("|{0}| >> something else...".format(_str_func))     
            _l = mc.ls(type=_type)
            for o in _l:
                if NAME.long(o) != _long:
                    _l_res.append(o)
            #raise ValueError,"Shouldn't have arrived. node: [{0}] | type: {1}".format(_node,_type)
    elif parents_get(_node):
        log.debug("|{0}| >> parented...".format(_str_func))
        _long = NAME.long(_node)
        for c in children_get(parent_get(node),True):
            if c != _long:
                _l_res.append(c)        
    else:
        log.debug("|{0}| >> root transform...".format(_str_func))
        l_rootTransforms = get_rootList()
        _short = NAME.short(_node)
        for o in l_rootTransforms:
            if o != _short and VALID.get_mayaType(o) == _type:
                _l_res.append(o)  
    
    if not fullPath:
        return [NAME.short(o) for o in _l_res]
    return _l_res
        
        
def get_rootList():
    """
    Get a list of root transform nodes in the scene
    
    :parameters:

    :returns
        rootList(list)
    """   
    _str_func = 'get_rootList'
    
    _l =  mc.ls(assemblies=True, dag = True) or []
    _res = []
    for o in _l:
        if not parent_get(o):
            _res.append(o)
    return _res
    
#Transformations bridges =========================================================================================
vector_byAxis = MATH.get_obj_vector


def euclidVector3Arg(arg):
    _str_func = 'euclidVector3Arg'    
    if not issubclass(type(arg),EUCLID.Vector3):
        if VALID.isListArg(arg) and len(arg) == 3:
            return EUCLID.Vector3(float(arg[0]),float(arg[1]),float(arg[2]))
        else:
            raise ValueError,"|{0}| >> arg: {1}".format(_str_func,arg)
    return arg
    
def transformDirection(node = None, v = None):
    """
    Get local position of vector transformed from world space of Transform
    
    :parameters:
        node(str): Object to check
        v(d3): vector

    :returns
        new value(Vector3)
    """   
    _str_func = 'transformDirection'
    _node =  VALID.mNodeString(node)
    
    v = euclidVector3Arg(v)
    
    log.debug("|{0}| >> node: [{1}] | {2}".format(_str_func,_node,v))
    
    current_matrix = worldMatrix_get(_node,True)
    current_matrix.m = 0
    current_matrix.n = 0
    current_matrix.o = 0

    s = scaleLocal_get(_node,True)

    transform_matrix = EUCLID.Matrix4()
    transform_matrix.m = v.x
    transform_matrix.n = v.y
    transform_matrix.o = v.z

    scale_matrix = EUCLID.Matrix4()
    scale_matrix.a = s.x
    scale_matrix.f = s.y
    scale_matrix.k = s.z
    scale_matrix.p = 1

    result_matrix = transform_matrix * current_matrix * scale_matrix

    return EUCLID.Vector3(result_matrix.m, result_matrix.n, result_matrix.o) - EUCLID.Vector3(current_matrix.m, current_matrix.n, current_matrix.o)
    
def transformPoint(node = None, v = None):
    """
    Get world position of vector transformed from local space of Transform
    
    :parameters:
        node(str): Object to check
        v(d3): vector

    :returns
        new value(Vector3)
    """   
    _str_func = 'transformDirection'
    _node =  VALID.mNodeString(node)
    
    v = euclidVector3Arg(v)
    
    log.debug("|{0}| >> node: [{1}] | {2}".format(_str_func,_node,v))
    
    current_matrix = worldMatrix_get(_node,True)
    
    s = scaleLocal_get(_node,True)

    transform_matrix = EUCLID.Matrix4()
    transform_matrix.m = v.x
    transform_matrix.n = v.y
    transform_matrix.o = v.z

    scale_matrix = EUCLID.Matrix4()
    scale_matrix.a = s.x
    scale_matrix.f = s.y
    scale_matrix.k = s.z
    scale_matrix.p = 1

    result_matrix = transform_matrix * current_matrix * scale_matrix

    return EUCLID.Vector3(result_matrix.m, result_matrix.n, result_matrix.o) - EUCLID.Vector3(current_matrix.m, current_matrix.n, current_matrix.o)
    
def transformInverseDirection(node = None, v = None):
    """
    Get local position of vector transformed from world space of Transform
    
    :parameters:
        node(str): Object to check
        v(d3): vector

    :returns
        new value(Vector3)
    """   
    _str_func = 'transformInverseDirection'
    _node =  VALID.mNodeString(node)
    
    v = euclidVector3Arg(v)
    
    log.debug("|{0}| >> node: [{1}] | {2}".format(_str_func,_node,v))
    
    current_matrix = worldMatrix_get(_node,True)
    s = scaleLocal_get(_node,True)
    
    current_matrix.m = 0
    current_matrix.n = 0
    current_matrix.o = 0

    transform_matrix = EUCLID.Matrix4()
    transform_matrix.m = v.x
    transform_matrix.n = v.y
    transform_matrix.o = v.z

    scale_matrix = EUCLID.Matrix4()
    scale_matrix.a = s.x
    scale_matrix.f = s.y
    scale_matrix.k = s.z
    scale_matrix.p = 1

    result_matrix = transform_matrix * current_matrix.inverse() * scale_matrix
    return EUCLID.Vector3(result_matrix.m, result_matrix.n, result_matrix.o)    


def transformInversePoint(node = None, v = None):
    """
    Get local position of vector transformed from world space of Transform
    
    :parameters:
        node(str): Object to check
        v(d3): vector

    :returns
        new value(Vector3)
    """   
    _str_func = 'transformInversePoint'
    _node =  VALID.mNodeString(node)
    
    v = euclidVector3Arg(v)
    
    log.debug("|{0}| >> node: [{1}] | {2}".format(_str_func,_node,v))
    
    current_matrix = worldMatrix_get(_node,True)
    s = scaleLocal_get(_node,True)
    
    transform_matrix = EUCLID.Matrix4()
    transform_matrix.m = v.x
    transform_matrix.n = v.y
    transform_matrix.o = v.z

    scale_matrix = EUCLID.Matrix4()
    scale_matrix.a = s.x
    scale_matrix.f = s.y
    scale_matrix.k = s.z
    scale_matrix.p = 1

    result_matrix = transform_matrix * current_matrix.inverse() * scale_matrix
    return EUCLID.Vector3(result_matrix.m, result_matrix.n, result_matrix.o) 


#Matrix stuff ============================================================================================  
def worldMatrix_get(node = None, asEuclid = False):
    """
    Query the worldMatrix of a given node
    
    :parameters:
        node(str): node to query
        asMatrix(bool): whether to return a EUCLID.Matrix4

    :returns
        matrix
    """   
    _str_func = 'worldMatrix_get'
    
    node = VALID.mNodeString(node)

    try:matrix_a = mc.xform( node,q=True,m=True, ws=True )
    except Exception, e:
        if not VALID.is_transform(node):
            log.error("|{0}| >> Not a transform: '{1}'".format(_str_func,node))                        
            return False
        
        log.error("|{0}| >> Failed: '{1}'".format(_str_func,node))
        #for arg in e.args:
            #log.error(arg)
        raise Exception,e 
        
    if not asEuclid:
        return matrix_a
    
    current_matrix = EUCLID.Matrix4()
    current_matrix.a = matrix_a[0]
    current_matrix.b = matrix_a[1]
    current_matrix.c = matrix_a[2]
    current_matrix.d = matrix_a[3]
    current_matrix.e = matrix_a[4]
    current_matrix.f = matrix_a[5]
    current_matrix.g = matrix_a[6]
    current_matrix.h = matrix_a[7]
    current_matrix.i = matrix_a[8]
    current_matrix.j = matrix_a[9]
    current_matrix.k = matrix_a[10]
    current_matrix.l = matrix_a[11]
    current_matrix.m = matrix_a[12]
    current_matrix.n = matrix_a[13]
    current_matrix.o = matrix_a[14]
    current_matrix.p = matrix_a[15]
    
    return current_matrix


def group_me(obj = None,
             parent = False, maintainParent = True, rotateAxis = True,
             rotatePivot = True, scalePivot = True, zeroScale = False, cleanRotates = True):
    """
    A bridge function utilizing both copy_pivot and copy_orientation in a single call

    :parameters:
        obj(str): Object to modify
        parent(str): Whether to parent the object to the new group
        maintainParent(bool): Whether to maintain parent of the object
        rotateAxis(bool): whether to copy the rotateAxis
        rotatePivot(bool): whether to copy the rotatePivot
        scalePivot(bool): whether to copy the scalePivot
        zeroScale(bool): whether to take the childs scale to zero it
        cleanRotates(bool): whether to zero the rotate data after parent
    :returns
        success(bool)
    """   
    _str_func = 'group_me'

    obj = VALID.mNodeString(obj)

    log.debug("|{0}| >> obj:{1}".format(_str_func,obj))    

    _oldParent = False
    if maintainParent:
        _oldParent = parent_get(obj)

    group = mc.group(em=True)
    
    #objRot = mc.xform (obj, q=True, ws=True, ro=True)
    #objRotAxis = mc.xform(obj, q=True, ws = True, ra=True)    
    
    mc.xform(group, roo = mc.xform(obj, q=True, roo=True ))#...match rotateOrder    
    
    position_set(group, position_get(obj))
    orient_set(group, orient_get(obj))
    rotateAxis_set(group, rotateAxis_get(obj))
    
    #mc.xform(group, ws=True, ro= objRot,p=False)
    #mc.xform(group, ws=True, ra= objRotAxis,p=False)      

    if zeroScale:
        scaleLocal_set(group, scaleLossy_get(obj))

    if maintainParent == True and _oldParent:
        group = parent_set(group,_oldParent)

    if parent:
        _wasLocked = []
            
        for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:#'rx','ry','rz'
            attrBuffer = '%s.%s'%(obj,attr)
            if mc.getAttr(attrBuffer,lock=True):
                _wasLocked.append(attr)
                mc.setAttr(attrBuffer,lock=False)                
            #attributes.doSetAttr(obj,attr,0)    
            
        obj = parent_set(obj,group)
        
        if cleanRotates:
            ATTR.reset(obj,['rotate','rotateAxis'])

        if _wasLocked:
            for attr in _wasLocked:
                attrBuffer = '%s.%s'%(obj,attr)
                mc.setAttr(attrBuffer,lock=True)     
                
    if zeroScale:#After all the parenting we'll push the reset
        scaleLocal_set(obj)        

    return mc.rename(group, "{0}_grp".format(NAME.base(obj))) 





