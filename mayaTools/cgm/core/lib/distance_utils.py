"""
------------------------------------------
distance_utils: cgm.core.lib.distance_utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
# From Python =============================================================
import copy
import re
from math import sqrt,pow
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
import Red9.core.Red9_Meta as r9Meta

# From cgm ==============================================================
#NO LOC
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
reload(SEARCH)
import cgm.core.lib.attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATHUTILS
from cgm.core.lib import name_utils as NAMES
from cgm.core.lib import list_utils as LIST
#import cgm.core.lib.shape_utils as SHAPE
reload(POS)
reload(MATHUTILS)

#from cgm.lib import attributes
#>>> Utilities
#===================================================================
def scale_to_axisSize(arg = None, size = None):
    _str_func = 'scale_to_axisSize'
    log.debug(cgmGEN.logString_start(_str_func))
    _currentSize = get_axisSize(arg)
    _currentScale = ATTR.get(arg,'scale')
    _targetScale = []
    for i,s in enumerate(size):
        if s is not None:
            v = (_currentScale[i] * s) / _currentSize[i]
            _targetScale.append(v)
        else:
            _targetScale.append(_currentScale[i])
    #log.info(_targetScale)
    
    for i,a in enumerate('xyz'):
        if size[i]:
            ATTR.set(arg,'s{0}'.format(a),_targetScale[i])

def get_axisSize(arg):
    try:
        _str_func = 'get_axisSize'
        bbSize = get_bb_size(arg)
        
        d_res = {'x':[],'y':[],'z':[]}
        
        _startPoint = POS.get(arg,'bb')
        _res = []
        for i,k in enumerate('xyz'):
            log.debug("|{0}| >> On t: {1} | {2}".format(_str_func,arg,k))
            
            pos_pos = get_pos_by_axis_dist(arg,k+'+',bbSize[i]*1.5)
            pos_neg = get_pos_by_axis_dist(arg,k+'-',bbSize[i]*1.5)
            
            pos1 = get_closest_point(pos_pos,arg)
            pos2 = get_closest_point(pos_neg,arg)
    
            dist = get_distance_between_points(pos1[0],pos2[0])
            _res.append(dist)
            
        return (_res)
    except Exception,err:cgmGEN.cgmException(Exception,err)



get_bb_size = POS.get_bb_size

def get_bb_sizeOLD(arg = None, shapes = False, mode = None):
    """
    Get the bb size of a given arg
    
    :parameters:
        arg(str/list): Object(s) to check
        shapes(bool): Only check dag node shapes
        mode(varied): 
            True/'max': Only return max value
            'min': Only min

    :returns
        boundingBox size(list)
    """   
    _str_func = 'get_bb_size'
    #_arg = VALID.stringListArg(arg,False,_str_func)   
    
    if shapes:
        log.debug("|{0}| >> shapes mode ".format(_str_func))        
        arg = VALID.listArg(arg)
        l_use = []
        for o in arg:
            log.debug("|{0}| >> o: '{1}' ".format(_str_func,o))
            l_shapes = mc.listRelatives(o,s=True) or []
            if l_shapes: l_use.extend(l_shapes)
            else:
                l_use.append(o)
        arg = l_use
        
    log.debug("|{0}| >> arg: '{1}' ".format(_str_func,arg))
    _box = mc.exactWorldBoundingBox(arg)
    _res = [(_box[3] - _box[0]), (_box[4] - _box[1]), (_box[5] - _box[2])]
    
    if mode is None:
        return _res
    elif mode in [True, 'max']:
        return max(_res)
    elif mode in ['min']:
        return min(_res)
    else:
        log.error("|{0}| >> Unknown mode. Returning default. {1} ".format(_str_func,mode))
    return _res


def get_size_byShapes(arg, mode = 'max'):
    _str_func = 'get_sizeByShapes'
    _arg = VALID.mNodeString(arg)   
    log.debug("|{0}| >> arg: '{1}' ".format(_str_func,_arg))  
    
    _l_bb = []
    _sizeX = []
    _sizeY = []
    _sizeZ = []
    
    _shapes = mc.listRelatives(_arg,s=True,fullPath=True)
    if not _shapes:
        if VALID.is_shape(arg):
            _shapes = [arg]
        else:
            raise ValueError,"|{0}| >> '{1}' has no shapes.".format(_str_func,_arg)
    for s in _shapes:
        _bfr = get_bb_size(s)
        _l_bb.append(_bfr)
        _sizeX.append(_bfr[0])
        _sizeY.append(_bfr[1])
        _sizeZ.append(_bfr[2])
    
    log.debug("|{0}| >> sx: '{1}' ".format(_str_func,_sizeX))  
    log.debug("|{0}| >> sy: '{1}' ".format(_str_func,_sizeY))  
    log.debug("|{0}| >> sz: '{1}' ".format(_str_func,_sizeZ))  
    
    
    if mode == 'max':
        return max(max(_sizeX), max(_sizeY), max(_sizeZ))
    elif mode == 'bb':
        return [max(_sizeX), max(_sizeY), max(_sizeZ)]       
    else:
        raise ValueError,"|{0}| >> unknown mode: {1}".format(_str_func,mode)
        
    

def get_createSize(arg = None, mode = None):
    """
    Attempt to find a good size for control creation or 
    
    :parameters:
        arg(str/list): Object(s) to check


    :returns
        boundingBox size(list)
    """     
    def is_resGood(res = None):
        if MATHUTILS.is_float_equivalent(res,0.000) or res == -2e+20:
            return False
        return True
    
    _str_func = 'get_createSize'
    _arg = VALID.objString(arg,noneValid=False,calledFrom=_str_func)
    log.debug("|{0}| >> arg: '{1}' ".format(_str_func,_arg))    
    
    _bb_max = get_bb_size(_arg,True,True)
    log.debug("|{0}| >> bbSize: {1} ".format(_str_func,_bb_max))  
    if not MATHUTILS.is_float_equivalent(_bb_max,0.000) and not _bb_max == -2e+20:
        return _bb_max
    
    log.debug("|{0}| >> Zero boundingBox object...".format(_str_func))
    
    _children = mc.listRelatives(_arg,children = True, type='transform') or False
    if _children:
        _closestChild = get_by_dist(_arg, _children,'close','object')
        log.debug("|{0}| >> closest child mode. | closest: {1} ".format(_str_func,_closestChild))
        _res = get_distance_between_points(POS.get(_arg),POS.get(_closestChild))
        if is_resGood(_res):
            return _res
        log.debug("|{0}| >> child mode fail...".format(_str_func))
    
    _parent = mc.listRelatives(_arg,parent = True, type='transform') or False
    if _parent:
        log.debug("|{0}| >> Parent mode...".format(_str_func))
        _res =  get_distance_between_points(POS.get(_arg),POS.get(_parent))
        if is_resGood(_res):
            return _res        
        log.debug("|{0}| >> Parent mode fail...".format(_str_func))
        
    raise RuntimeError,"Shouldn't have gotten here. Failed at finding value"
        
    
    
    
    
    


def get_by_dist(source = None, targets = None, mode = 'close', resMode = 'point',
                sourcePivot = 'rp', targetPivot = 'rp'):
    """
    Get the the closest return based on a source and target and variable modes
    
    :parameters:
        :source(str): Our base object to measure from
        :targets(list): List of object types
        :mode(str):What mode are we checking data from
            close
            far
        :resMode(str):
            object -- return the [closest] target
            point -- return the [closest] point
            #component -- return [the closest] base component
            pointOnSurface -- [closest] point on the target shape(s)
            pointOnSurfaceLoc -- [closest] point on target shape(s) Loc'd
            shape -- gets closest point on every shape, returns closest
        resMode(str)
    :returns
        [res,distance]
    """   
    def get_fromTargets(sourcePos,targets,targetPivot,resMode,mode):
        _l_distances = []
        _l_pos = []
        for t in targets:
            _tarPos = POS.get(t,targetPivot,space='world')
            _l_pos.append(_tarPos)
            _d = get_distance_between_points(sourcePos,_tarPos)
            log.debug("|{0}| >> target: {1} | pivot: {4} | dist: {3} | pos: {2}...| mode: {5}".format(_str_func,t,_tarPos,_d,targetPivot,mode))
            _l_distances.append(_d)
        if mode == 'close':
            _minDist = min(_l_distances)
            _minIdx = _l_distances.index(_minDist)
            if resMode == 'point':return _l_pos[_minIdx], _minDist
            return targets[_minIdx], _minDist
        else:
            _maxDist = max(_l_distances)
            _maxIdx = _l_distances.index(_maxDist)
            if resMode == 'point':return _l_pos[_maxIdx], _maxDist      
            return targets[_maxIdx], _maxDist
        
    _d_by_dist_modes = {'close':['closest','c','near'],'far':['furthest','long']}
    
    _str_func = 'get_by_dist'
    _source = VALID.objString(source,noneValid=False,calledFrom= __name__ + _str_func + ">> validate targets")   
    _mode = VALID.kw_fromDict(mode, _d_by_dist_modes, noneValid=False,calledFrom= __name__ + _str_func + ">> validate mode")
    _resMode = resMode
    _l_targets = VALID.objStringList(targets,noneValid=False,calledFrom= __name__ + _str_func + ">> validate targets")
    
    _sourcePivot = VALID.kw_fromDict(sourcePivot, SHARED._d_pivotArgs, noneValid=False,calledFrom= __name__ + _str_func + ">> validate sourcePivot")
    _targetPivot = VALID.kw_fromDict(targetPivot, SHARED._d_pivotArgs, noneValid=False,calledFrom= __name__ + _str_func + ">> validate targetPivot")
    
    log.debug("|{0}| >> source: {1} | mode:{2} | resMode:{3}".format(_str_func,_source,_mode,_resMode))
    
    #Source==============================================================
    _sourcePos = POS.get(_source,_sourcePivot,space='ws')
    log.debug("|{0}| >> Source pos({2}): {1}...".format(_str_func,_sourcePos,_sourcePivot))
    
    #Modes
    if _resMode in ['object','point']:
        log.debug("|{0}| >> object resMode...".format(_str_func))
        mc.select(cl=True)
        
        _res = get_fromTargets(_sourcePos,_l_targets,_targetPivot,_resMode,_mode)
        if resMode == 'object':
            mc.select(_res[0])
            return _res[0]
        return _res[0]
    elif _resMode == 'component':
        raise NotImplementedError,"component mode"
    elif _resMode in ['pointOnSurface','shape','pointOnSurfaceLoc']:
        log.debug("|{0}| >> Shape processing...".format(_str_func))        
        #Targets=============================================================
        log.debug("|{0}| >> Targets processing...".format(_str_func))
        _d_targetTypes = {}
        _l_pos = []
        _l_dist = []
        _l_shapes = []
        
        """for t in _l_targets:
            _t = t
            _bfr_component = VALID.get_component(t)
            if _bfr_component:
                _t = _bfr_component[1]#...shape
            _type = VALID.get_mayaType(_t)
            if _type not in _d_targetTypes.keys():
                _d_targetTypes[_type] = [_t]
            else:
                _d_targetTypes[_type].append(_t)
            log.debug("|{0}| >> obj: {1} | type: {2}".format(_str_func,t,_type))"""
        #cgmGen.log_info_dict(_d_targetTypes,'Targets to type') 
        
        for t in _l_targets:
            res = get_closest_point(_sourcePos, t)
            if not res:
                log.error("|{0}| >> {1} -- failed".format(_str_func,t))
            else:
                log.debug("|{0}| >> {1}: {2}".format(_str_func,t,res))
                _l_pos.append(res[0])
                _l_dist.append(res[1])
                _l_shapes.append(res[2])
                

        if not _l_dist:
            log.error("|{0}| >> Failed to find any points".format(_str_func))
            return False
        closest = min(_l_dist)
        _idx = _l_dist.index(closest)    
        
        if _resMode == 'pointOnSurfaceLoc':
            _loc = mc.spaceLocator(n='get_by_dist_loc')[0]
            POS.set(_loc,_l_pos[_idx])
            return _loc
        if _resMode == 'shape':
            mc.select(_l_shapes[_idx])            
            return _l_shapes[_idx]
        return _l_pos[_idx]
        
def get_distance_between_targets(targetList=None, average = False):
    """
    """
    _str_func = 'get_distance_between_targets'
    if not targetList:
        targetList = mc.ls(sl=True,flatten = False)
    l_pos = []
    l_dist = []
    for o in targetList:
        l_pos.append(POS.get(o))
    
    if len(l_pos) <= 1:
        raise ValueError("|{0}| >> Must have more positions. targetList: {1}".format(_str_func,targetList))
    
    for i,p in enumerate(l_pos[:-1]):
        d = get_distance_between_points(p,l_pos[i+1])
        log.debug("|{0}| >> {1} |---------| {2} : {3}".format(_str_func,targetList[i],targetList[i+1],d))
        l_dist.append(d)
        
    if average:
        
        return sum(l_dist)/len(l_dist)
    
    return sum(l_dist)

def get_vector_between_targets(targetList=None):
    """
    """
    _str_func = 'get_vector_between_targets'
    if not targetList:
        targetList = mc.ls(sl=True,flatten = False)
    l_pos = []
    l_vec = []
    for o in targetList:
        l_pos.append(POS.get(o))
    
    if len(l_pos) <= 1:
        raise ValueError("|{0}| >> Must have more positions. targetList: {1}".format(_str_func,targetList))
    
    for i,p in enumerate(l_pos[:-1]):
        d = MATHUTILS.get_vector_of_two_points(p,l_pos[i+1])
        log.debug("|{0}| >> {1} |---------| {2} : {3}".format(_str_func,targetList[i],targetList[i+1],d))
        l_vec.append(d)
        
    return l_vec

def get_vectorOffset(obj = None, origin = None, distance = 0, asEuclid = False):
    """
    Get the vector offset of a given object with a distance. Designed as a replacment
    for maya's curve offset as it's finicky coupled with
    
    :parameters:
        obj(str): obj to query
        origin(d3) - origin to calculate vector from
        distance(f)
        asEuclid(bool) - whether to return as Vector or not

    :returns
        pos(list/Vector3)
    """   
    _str_func = 'get_vectorOffset'
    
    pos = POS.get(obj)
    vec = MATHUTILS.get_vector_of_two_points(origin,pos)
    newPos = get_pos_by_vec_dist(pos,vec,distance)
            
    if asEuclid:
        return MATHUTILS.Vector3(newPos[0],newPos[1],newPos[2])
    return newPos

def set_vectorOffset(obj = None, origin = None, distance = 0, vector = None, mode = 'origin', asEuclid = False):
    """
    Set the vector offset of a given object with a distance. Designed as a replacment
    for maya's curve offset as it's finicky coupled with
    
    :parameters:
        obj(str): obj to query
        origin(d3) - origin to calculate vector from
        distance(f)
        asEuclid(bool) - whether to return as Vector or not

    :returns
        pos(list/Vector3)
    """   
    if mode == 'origin':
        newPos = get_vectorOffset(obj,origin,distance)
    else:
        newPos = get_pos_by_vec_dist(POS.get(obj),vector,distance)
    POS.set(obj,newPos)
    return newPos

def offsetShape_byVector(dag=None, distance = 1, origin = None, component = 'cv', vector = None, mode = 'origin'):
    """
    Attempt for more consistency 
    
    If origin is None, juse the center of each shape
    """
    _str_func = 'offsetShape_byVector'
    log.debug("|{0}| >> dag: {1} | distance: {2} | origin: {3} | component: {4}".format(_str_func,
                                                                                       dag,
                                                                                       distance,
                                                                                       origin,
                                                                                       component))
    
    _originUse = None
    
    if VALID.isListArg(origin):
        _originUse = origin
    elif VALID.objString(origin,noneValid=True):
        log.debug("|{0}| >> Getting origin from transform of origin string: {1}".format(_str_func, origin))
        _originUse = POS.get(origin)
    
    if VALID.is_shape(dag):
        l_shapes = [dag]
    else:
        l_shapes = mc.listRelatives(dag,shapes=True, fullPath= True)
        
    
    for i,s in enumerate(l_shapes):
        log.debug("|{0}| >> On shape: {1}".format(_str_func, s))        
        if _originUse is None:
            #_trans = VALID.getTransform(dag)
            _origin = POS.get_bb_center(s)
            log.debug("|{0}| >> Getting origin from center of s: {1}".format(_str_func, _origin))
        else:
            _origin = _originUse
    
        _l_source = mc.ls("{0}.{1}[*]".format(s,component),flatten=True,long=True)
        
        for ii,c in enumerate(_l_source):
            log.debug("|{0}| >> Shape {1} | Comp: {2} | {3}".format(_str_func, i, ii, c))            
            set_vectorOffset(c,_origin,distance,vector,mode=mode)

        
    return True

def get_distance_between_points(point1,point2):
    """
    Gets the distance bewteen two points  
    
    :parameters:
        point1(list): [x,x,x]
        point2(list): [x,x,x]

    :returns
        distance(float)
    """       
    return sqrt( pow(point1[0]-point2[0], 2) + pow(point1[1]-point2[1], 2) + pow(point1[2]-point2[2], 2) )

def get_average_position(posList):
    """
    Gets the average point given a list of points 
    
    :parameters:
        pointList(list): [[x,x,x],...]

    :returns
        pos(double3)
    """       
    posX = []
    posY = []
    posZ = []
    for pos in posList:
        posBuffer = pos
        posX.append(posBuffer[0])
        posY.append(posBuffer[1])
        posZ.append(posBuffer[2])
    return [float(sum(posX)/len(posList)), float(sum(posY)/len(posList)), float(sum(posZ)/len(posList))]


def get_pos_by_vec_dist(startPos,vec,distance = 1):
    """
    Get a point along a ray given a point, ray and distance along that ray 
    
    :parameters:
        point(list): [x,x,x]
        vector(list): [x,x,x]

    :returns
        distance(float)
    """         
    _str_func = 'get_pos_by_vec_dist'
    vec = VALID.euclidVector3Arg(vec)
    
    _startPos = MATHUTILS.Vector3(startPos[0],startPos[1],startPos[2])
    _dir = MATHUTILS.Vector3(vec[0],vec[1],vec[2])
    
    _new = _startPos + _dir * distance
    
    return _new.x,_new.y,_new.z

def get_pos_by_axis_dist(obj, axis, distance = 1):
    """
    Get a point in space given an object, an axis and a distance
    
    :parameters:
        obj(string)
        axis(str)
        asEuclid(bool) - data return format   
    :returns
        distance(float)
    """
    obj =  VALID.mNodeString(obj)
    _vector = MATHUTILS.get_obj_vector(obj,axis,False)
    return get_pos_by_vec_dist(POS.get(obj),_vector,distance)


    
def get_posList_fromStartEnd(start=[0,0,0],end=[0,1,0],split = 1):
    _str_func = 'get_posList_fromStartEnd'

    #>>Get positions ==================================================================================    
    _l_pos = []

    if split == 1:
        _l_pos = [get_average_position([start,end])]
    elif split == 2:
        _l_pos = [start,end]
    else:
        _vec = MATHUTILS.get_vector_of_two_points(start, end)
        _max = get_distance_between_points(start,end)

        log.debug("|{0}| >> start: {1} | end: {2} | vector: {3}".format(_str_func,start,end,_vec))   

        _split = _max/(split-1)
        for i in range(split-1):
            _p = get_pos_by_vec_dist(start, _vec, _split * i)
            _l_pos.append( _p)
        _l_pos.append(end)
        _radius = _split/4    
    return _l_pos

def get_closestTarget(source = None, objects = None):
    """
    Get the closest object to a give source
    
    :parameters:
        source(str/vector) -- source point or object
        targetSurface -- surface to check transform, nurbsSurface, curve, mesh supported
        loc -- whether to loc point found

    :returns
        position, distance, shape (list)
    """         
    _str_func = 'get_closestTarget'
    _point = False
    
    if VALID.vectorArg(source) is not False:
        _point = source   
    elif mc.objExists(source):
        _point = POS.get(source)

    if not _point:raise ValueError,"Must have point of reference"
    
    l_dists = []
    for obj in objects:
        pos = POS.get(obj)
        l_dists.append (get_distance_between_points(_point, pos))
    return objects[(l_dists.index ((min(l_dists))))]    

def get_closest_point(source = None, targetSurface = None, loc = False):
    """
    Get the closest point on a target surface/curve/mesh to a given point or object.
    Evaluates to all sub shapes to get closest point for multi shape targets.
    
    :parameters:
        source(str/vector) -- source point or object
        targetSurface -- surface to check transform, nurbsSurface, curve, mesh supported
        loc -- whether to loc point found

    :returns
        position, distance, shape (list)
    """         
    _str_func = 'get_closest_point'
    _point = False
    if VALID.vectorArg(source) is not False:
        _point = source   
    elif mc.objExists(source):
        _point = POS.get(source)

    if not _point:raise ValueError,"Must have point of reference"
    _loc = mc.spaceLocator(n='get_closest_point_loc')[0]
    POS.set(_loc,_point)
    
    if SEARCH.is_shape(targetSurface):
        _shapes = [targetSurface]
    elif VALID.is_component(targetSurface):
        _shapes = mc.listRelatives(VALID.get_component(targetSurface)[1], s=True, fullPath = True)
    else:
        _shapes = mc.listRelatives(targetSurface, s=True, fullPath = True)
    
    if not _shapes:
        log.error("|{0}| >> No shapes found. Skipping: {1}".format(_str_func,targetSurface))
        mc.delete(_loc)
        return False
    
    _l_res_positions = []
    _l_res_shapes = []
    _l_res_distances = []
    
    for s in _shapes:    
        _type = VALID.get_mayaType(s)
        
        if _type not in ['mesh','nurbsSurface','nurbsCurve']:
            log.error("|{0}| >> Unsupported target surface type. Skipping: {1} |{2} | {3}".format(_str_func,s,_type))
            _l_res_positions.append(False)
            continue
        
        if _type == 'mesh':
            _node = mc.createNode ('closestPointOnMesh')
            
            ATTR.connect((_loc+'.translate'),(_node+'.inPosition'))
            ATTR.connect((s+'.worldMesh'),(_node+'.inMesh'))
            ATTR.connect((s+'.worldMatrix'),(_node+'.inputMatrix'))
            
            _pos = ATTR.get(_node,'position')
            _tmpLoc = mc.spaceLocator(n='tmp')[0]
            ATTR.connect ((_node+'.position'),(_tmpLoc+'.translate'))            
            
            _l_res_positions.append( POS.get(_tmpLoc)  )
            mc.delete(_node)
            mc.delete(_tmpLoc)

        elif _type == 'nurbsSurface':
            closestPointNode = mc.createNode ('closestPointOnSurface')
            
            ATTR.set(closestPointNode,'inPositionX',_point[0])
            ATTR.set(closestPointNode,'inPositionY',_point[1])
            ATTR.set(closestPointNode,'inPositionZ',_point[2])  
            
            ATTR.connect((s +'.worldSpace'),(closestPointNode+'.inputSurface'))
            _l_res_positions.append(ATTR.get(closestPointNode,'position'))
            mc.delete(closestPointNode)
            
        elif _type == 'nurbsCurve':
            _node = mc.createNode ('nearestPointOnCurve')
            p = []
            distances = []
            mc.connectAttr ((_loc+'.translate'),(_node+'.inPosition'))
            mc.connectAttr ((s+'.worldSpace'),(_node+'.inputCurve'))
            p = [mc.getAttr (_node+'.positionX'), mc.getAttr (_node+'.positionY'), mc.getAttr (_node+'.positionZ') ]
            _l_res_positions.append(p)
            mc.delete (_node)
    
    mc.delete(_loc)
    
    if not _l_res_positions:
        raise ValueError,"No positions found"
    
    for p in _l_res_positions:
        if p:
            _l_res_distances.append( get_distance_between_points(_point, p))
        else:
            _l_res_distances.append('no')
    closest = min(_l_res_distances)
    _idx = _l_res_distances.index(closest)
    
    _pos = _l_res_positions[_idx]
    if not _pos:
        return False
        #raise ValueError,"Failed to find point"
    
    if loc:
        _loc = mc.spaceLocator(n='get_closest_point_loc')[0]
        POS.set(_loc,_pos) 
        
    return _pos, _l_res_distances[_idx], _shapes[_idx]

def create_distanceMeasure(start = None, end = None, baseName = 'measure'):
    """
    Get the the closest return based on a source and target and variable modes
    
    :parameters:
        :start(str): Our start obj
        :end(str): End obj
        :baseName(str):What mode are we checking data from
    
    :returns
        {shape,dag,loc_start,loc_end,start,end}
    """
    try:
        _str_func = 'create_distanceMeasure'
        
        #Create ====================================================================================
        plug_start = POS.get_positionPlug(start)
        plug_end = POS.get_positionPlug(end)
        _res = {'start':start,'end':end}
        
        if not plug_start:
            pos_start = POS.get(start)
            loc_start = mc.spaceLocator(name="{0}_{1}_start_loc".format(NAMES.get_base(start),baseName))[0]
            POS.set(loc_start,pos_start)  
            plug_start = POS.get_positionPlug(loc_start)
            _res['loc_start'] = loc_start
        if not plug_end:
            pos_end = POS.get(end)
            loc_end = mc.spaceLocator(name="{0}_{1}_end_loc".format(NAMES.get_base(end),baseName))[0]
            POS.set(loc_end,pos_end)  
            plug_end = POS.get_positionPlug(loc_end)
            _res['loc_end'] = loc_end
            
            
        mDistShape = r9Meta.MetaClass( mc.createNode ('distanceDimShape') )
        mDistShape.rename("{0}_distShape".format(baseName))
        
        mDistTrans = r9Meta.MetaClass( VALID.getTransform(mDistShape.mNode) )
        mDistTrans.rename("{0}_dist".format(baseName))
        
        _res['dag'] = mDistTrans.mNode
        _res['shape'] = mDistShape.mNode
        
        ATTR.set_message(_res['dag'],'distShape',_res['shape'],simple = True)

        ATTR.connect(plug_start, "{0}.startPoint".format(_res['shape']))
        ATTR.connect(plug_end, "{0}.endPoint".format(_res['shape']))
    

        return _res
    except Exception,err:cgmGen.cgmExceptCB(Exception,err)

def create_closest_point_node(source = None, targetSurface = None, singleReturn = False):
    """
    Create a closest point on surface node and wire it
    
    :parameters:
        source(str/vector) -- source point or object
        targetSurface -- surface to check transform, nurbsSurface, curve, mesh supported
        singleReturn - only return single return if we have
    :returns
        node(list)
    """
    try:
        _str_func = 'create_closest_point_node'
        _transform = False
        
        if VALID.vectorArg(source) is not False:
            _transform = mc.spaceLocator(n='closest_point_source_loc')[0]   
            POS.set(_transform,source)  
        elif mc.objExists(source):
            if SEARCH.is_transform(source):
                _transform = source
            elif VALID.is_component(source):
                _transform = mc.spaceLocator(n='{0}_loc'.format(NAMES.get_base(source)))[0]
                POS.set(_transform, POS.get(source))
            else:
                _transform = SEARCH.get_transform(source)
    
        if not _transform:raise ValueError,"Must have a transform"
        
        if SEARCH.is_shape(targetSurface):
            l_shapes = [targetSurface]
        else:
            l_shapes = mc.listRelatives(targetSurface, s=True, fullPath = True)
        
        if not l_shapes:
            raise ValueError,"Must have shapes to check."
        
        _nodes = []
        _locs = []
        _types = []
        _shapes = []
        
        for s in l_shapes:    
            _type = VALID.get_mayaType(s)
            
            if _type not in ['mesh','nurbsSurface','nurbsCurve']:
                log.error("|{0}| >> Unsupported target surface type. Skipping: {1} |{2} ".format(_str_func,s,_type))
                continue
            
            _loc = mc.spaceLocator()[0]
            _res_loc = mc.rename(_loc,'{0}_to_{1}_result_loc'.format(NAMES.get_base(source),
                                                                        NAMES.get_base(s)))
            _locs.append(_res_loc)
            _types.append(_type)
            _shapes.append(s)
            
            if _type == 'mesh':
                _node = mc.createNode ('closestPointOnMesh')
                _node = mc.rename(_node, "{0}_to_{1}_closePntMeshNode".format(NAMES.get_base(source),
                                                                              NAMES.get_base(s)))
                ATTR.connect((_transform+'.translate'),(_node+'.inPosition'))
                ATTR.connect((s+'.worldMesh'),(_node+'.inMesh'))
                ATTR.connect((s+'.worldMatrix'),(_node+'.inputMatrix'))
                
                _pos = ATTR.get(_node,'position')
                ATTR.connect((_node+'.position'),(_res_loc+'.translate'))  
                
                _nodes.append(_node)
                
            elif _type == 'nurbsSurface':
                closestPointNode = mc.createNode ('closestPointOnSurface')
                closestPointNode = mc.rename(closestPointNode, "{0}_to_{1}_closePntSurfNode".format(NAMES.get_base(source), NAMES.get_base(s)))
                
                mc.connectAttr ((_transform+'.translate'),(closestPointNode+'.inPosition'))
                
                #attributes.doSetAttr(closestPointNode,'inPositionX',_point[0])
                #attributes.doSetAttr(closestPointNode,'inPositionY',_point[1])
                #attributes.doSetAttr(closestPointNode,'inPositionZ',_point[2])  
                
                ATTR.connect((s +'.worldSpace'),(closestPointNode+'.inputSurface'))
                
                ATTR.connect ((closestPointNode+'.position'),(_res_loc+'.translate'))  
                _nodes.append(closestPointNode)
                
            elif _type == 'nurbsCurve':
                _node = mc.createNode ('nearestPointOnCurve')
                _node = mc.rename(_node, "{0}_to_{1}_nearPntCurveNode".format(NAMES.get_base(source), NAMES.get_base(s)))
                
                p = []
                distances = []
                mc.connectAttr ((_transform+'.translate'),(_node+'.inPosition'))
                mc.connectAttr ((s+'.worldSpace'),(_node+'.inputCurve'))
                
                ATTR.connect((_node+'.position'),(_res_loc+'.translate'))  
                _nodes.append(_node)
                
        if not singleReturn:
            return _locs, _nodes, _shapes, _types
        
        _l_distances = []
        pos_base = POS.get(_transform)
        for i,n in enumerate(_nodes):
            p2 = POS.get(_locs[i])
            _l_distances.append(get_distance_between_points(pos_base, p2))
        
        if not _l_distances:
            raise ValueError,"No distance value found"
        closest = min(_l_distances)
        _idx = _l_distances.index(closest)
        
        for i,n in enumerate(_nodes):
            if i != _idx:
                mc.delete(n, _locs[i])
        
        return _locs[_idx], _nodes[_idx], _shapes[_idx], _types[_idx]
    except Exception,err:cgmGen.cgmExceptCB(Exception,err)


    
def get_closest_point_data_from_mesh(mesh = None, targetObj = None, targetPoint = None):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns pertinent info of the closest point of a mesh to a target object -
    position, normal, parameterU,parameterV,closestFaceIndex,closestVertexIndex

    ARGUMENTS:
    targetObj(string)
    mesh(string)

    RETURNS:
    closestPointInfo(dict)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    _str_func = 'get_closest_point_data_from_mesh'
    
    _point = False
    if targetObj is not None:
        _point = POS.get(targetObj)
    elif targetPoint:
        _point = targetPoint
    if not _point:raise ValueError,"Must have point of reference"
    
    _loc = mc.spaceLocator()[0]
    POS.set(_loc,_point)  
        
    _shape = False
    if SEARCH.is_shape(mesh):
        if VALID.get_mayaType(mesh) == 'mesh':
            _shape = mesh
        else:raise ValueError,"Must be a mesh shape"
    else:
        _shape = SEARCH.get_nonintermediateShape(mesh)
        _shapes = mc.listRelatives(mesh, s=True, fullPath = True)
        """_meshes = []
        for s in _shapes:
            if VALID.get_mayaType(s) == 'mesh':
                _meshes.append(s)
        if len(_meshes) > 1:
            _shape = _meshes[0]"""
    if not _shape:
        log.error("|{0}| >> Shapes...".format(_str_func))
        for s in _shapes:
            print "{0} : {1}".format(s,VALID.get_mayaType(s))
        raise ValueError,"Must have a mesh shape by now"
        
        
    """ make the closest point node """
    _node = mc.createNode ('closestPointOnMesh')

    """ to account for target objects in heirarchies """
    ATTR.connect((targetObj+'.translate'),(_node+'.inPosition'))
    ATTR.connect((_shape+'.worldMesh'),(_node+'.inMesh'))
    ATTR.connect((_shape+'.matrix'),(_node+'.inputMatrix'))
    _u = mc.getAttr(_node+'.parameterU')
    _v = mc.getAttr(_node+'.parameterV')
    
    #_norm = get_normalized_uv(_shape, _u,_v)
    _res = {}
    
    _res['shape'] = _shape
    _res['position']=ATTR.get(_node,'position')
    _res['normal']=ATTR.get(_node,'normal')
    _res['parameterU']= _u
    _res['parameterV']= _v
    #_res['normalizedU'] = _norm[0]
    #_res['normalizedV'] = _norm[1]
    _res['closestFaceIndex']=mc.getAttr(_node+'.closestFaceIndex')
    _res['closestVertexIndex']=mc.getAttr(_node+'.closestVertexIndex')
    

    mc.delete([_node,_loc])
    return _res

def get_closest_point_data(targetSurface = None, targetObj = None, targetPoint = None):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Returns pertinent info of the closest point of a mesh to a target object -
    position, normal, parameterU,parameterV,closestFaceIndex,closestVertexIndex

    ARGUMENTS:
    targetObj(string)
    mesh(string)

    RETURNS:
    closestPointInfo(dict)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    try:
        _str_func = 'get_closest_point_data'
        
        _point = False
        if targetObj is not None:
            _point = POS.get(targetObj)
        elif targetPoint:
            _point = targetPoint
        if not _point:raise ValueError,"Must have point of reference"
        
        _loc = mc.spaceLocator()[0]
        POS.set(_loc,_point)  
        
        _created = create_closest_point_node(_loc, targetSurface,singleReturn=True)
            
        _node = _created[1]
        _shape = _created[2]
        _type = _created[3]
        
        

        #_norm = get_normalized_uv(_shape, _u,_v)
        _res = {}
        
        _res['shape'] = _shape
        _res['type'] = _type
        _res['position']=ATTR.get(_node,'position')
        _res['normal']=ATTR.get(_node,'normal')
        
        if _type == 'nurbsCurve':
            _res['parameter']= ATTR.get(_node,'parameter')
        else:
            _u = mc.getAttr(_node+'.parameterU')
            _v = mc.getAttr(_node+'.parameterV')
            _res['parameterU']= _u
            _res['parameterV']= _v
            
            if _type == 'nurbsSurface':
                _norm = get_normalized_uv(_shape, _u,_v)
                _res['normUV'] = _norm['uv']
                _res['normalizedU'] = _norm['uValue']
                _res['normalizedV'] = _norm['vValue']
            else:
                _res['closestFaceIndex']=mc.getAttr(_node+'.closestFaceIndex')
                _res['closestVertexIndex']=mc.getAttr(_node+'.closestVertexIndex')
        mc.delete([_loc],_created[0],_node)
        return _res
    except Exception,err:cgmGen.cgmExceptCB(Exception,err)

def get_normalizedWeightsByDistance(obj,targets,normalizeTo=1.0):
    _str_func = 'get_normalizedWeightsByDistance'
    
    pos_obj = POS.get(VALID.mNodeString(obj))
    targets = VALID.mNodeStringList(targets)
    
    _l_dist = []
    for t in targets:
        _l_dist.append(get_distance_between_points(pos_obj,POS.get(t)))
    vList = MATHUTILS.normalizeListToSum(_l_dist,normalizeTo)
    log.debug("|{0}| >> targets: {1} ".format(_str_func,targets))                     
    log.debug("|{0}| >> raw: {1} ".format(_str_func,_l_dist))             
    log.debug("|{0}| >> normalize: {1} ".format(_str_func,vList))  
    vList = [normalizeTo - v for v in vList]
    
    return vList
    

def get_normalizedWeightsByDistanceToObj(obj,targets):
    """
    Returns a normalized weight set based on distance from object to targets.
    Most useful for setting up constaints by weight value
    
    :parameters:
        obj(str): base object
        targets(list): 


    :returns
        normalized weights(list)
    """   
    _str_func = 'get_normalizedWeightsByDistanceToObj'
    
    obj = VALID.mNodeString(obj)
    _p_base = POS.get(obj)
    
    targets = VALID.mNodeStringList(targets)
    
    weights = []
    distances = []
    distanceObjDict = {}
    objDistanceDict = {}
    
    for t in targets:
        _p = POS.get(t)
        buffer = get_distance_between_points(_p_base,_p) # get the distance
        distances.append(buffer)
        distanceObjDict[buffer] = t
        objDistanceDict[t] = buffer
        
    normalizedDistances = MATHUTILS.normalizeListToSum(distances) # get normalized distances to 1
    
    #normalizedSorted = copy.copy(normalizedDistances)
    #normalizedSorted.sort() #sort our distances
    #normalizedSorted.reverse() # reverse the sort for weight values    
    
    for i,t in enumerate(targets):
        dist = objDistanceDict[t] 
        index = distances.index(dist)
        weights.append( normalizedDistances[index] )
    
    return weights    
 


def get_normalized_uv(mesh, uValue, vValue):
    """
    uv Values from many functions need to be normalized to be correct when using those values for other functions

    The calculcaion for doing so is 
    size = maxV - minV
    sum = rawV + minV
    normalValue = sum / size
    
    :parameters:
        mesh(string) | Surface to normalize to
        uValue(float) | uValue to normalize 
        vValue(float) | vValue to normalize 

    :returns
        Dict ------------------------------------------------------------------
        'uv'(double2) |  point from which we cast
        'uValue'(float) | normalized uValue
        'vValue'(float) | normalized vValue

    :raises:
        Exception | if reached
    """        
    _str_func = 'get_normalized_uv'
    
    try:
        try:#Validation ----------------------------------------------------------------
            reload(VALID)
            _mesh = VALID.objString(mesh,'nurbsSurface', calledFrom = _str_func)
            #log.debug("|{0}| >> mesh arg: {1} | validated: {2}".format(_str_func,mesh,_mesh))            
            
            if not SEARCH.is_shape(_mesh):
                shape = mc.listRelatives(_mesh, shapes=True)[0]
                log.debug("|{0}| >> Transform provided. using first shape: {1}".format(_str_func,shape))
            else:shape = _mesh
  
            uMin = ATTR.get(shape,'mnu')
            uMax = ATTR.get(shape,'mxu')
            vMin = ATTR.get(shape,'mnv')
            vMax = ATTR.get(shape,'mxv')         
            """uMin = mi_shape.mnu
            uMax = mi_shape.mxu
            vMin = mi_shape.mnv
            vMax = mi_shape.mxv"""

        except Exception,error:raise Exception,"Validation failure | {0}".format(error) 		

        try:#Calculation ----------------------------------------------------------------
            uSize = uMax - uMin
            vSize = vMax - vMin

            uSum = uMin + uValue
            vSum = vMin + vValue

            uNormal = uSum / uSize
            vNormal = vSum / vSize
        except Exception,error:raise Exception,"Calculation |{0}".format(error) 		

        try:
            d_return = {'uv':[uNormal,vNormal],'uValue':uNormal,'vValue':vNormal}
            return d_return 
        except Exception,error:raise Exception,"Return prep |{0}".format(error) 		

    except Exception,error:
        log.error(">>> {0} >> Failure! mesh: '{1}' | uValue: {2} | vValue {3}".format(_str_func,mesh,uValue,vValue))
        log.error(">>> {0} >> error: {1}".format(_str_func,error))        
        return None


def returnNormalizedUV(mesh, uValue, vValue):
    """
    uv Values from many functions need to be normalized to be correct when using those values for other functions

    The calculcaion for doing so is 
    size = maxV - minV
    sum = rawV + minV
    normalValue = sum / size

    :parameters:
    mesh(string) | Surface to normalize to
    uValue(float) | uValue to normalize 
    vValue(float) | vValue to normalize 

    :returns:
    Dict ------------------------------------------------------------------
    'uv'(double2) |  point from which we cast
    'uValue'(float) | normalized uValue
    'vValue'(float) | normalized vValue

    :raises:
    Exception | if reached

    """      
    try:
        _str_funcName = 'returnNormalizedUV'

        try:#Validation ----------------------------------------------------------------
            mesh = cgmValid.objString(mesh,'nurbsSurface', calledFrom = _str_funcName)
            if len(mc.ls(mesh))>1:
                raise StandardError,"{0}>>> More than one mesh named: {1}".format(_str_funcName,mesh)
            _str_objType = search.returnObjectType(mesh)

            l_shapes = mc.listRelatives(mesh, shapes=True)
            if len(l_shapes)>1:
                log.debug( "More than one shape found. Using 0. targetSurface : %s | shapes: %s"%(mesh,l_shapes) )
            #mi_shape = cgmMeta.validateObjArg(l_shapes[0],cgmMeta.cgmNode,noneValid=False)

            uMin = ATTR.get(l_shapes[0],'mnu')
            uMax = ATTR.get(l_shapes[0],'mxu')
            vMin = ATTR.get(l_shapes[0],'mnv')
            vMax = ATTR.get(l_shapes[0],'mxv')         
            """uMin = mi_shape.mnu
            uMax = mi_shape.mxu
            vMin = mi_shape.mnv
            vMax = mi_shape.mxv"""

        except Exception,error:raise Exception,"Validation failure | {0}".format(error) 		

        try:#Calculation ----------------------------------------------------------------
            uSize = uMax - uMin
            vSize = vMax - vMin

            uSum = uMin + uValue
            vSum = vMin + vValue

            uNormal = uSum / uSize
            vNormal = vSum / vSize
        except Exception,error:raise Exception,"Calculation |{0}".format(error) 		

        try:
            d_return = {'uv':[uNormal,vNormal],'uValue':uNormal,'vValue':vNormal}
            return d_return 
        except Exception,error:raise Exception,"Return prep |{0}".format(error) 		

    except Exception,error:
        log.error(">>> {0} >> Failure! mesh: '{1}' | uValue: {2} | vValue {3}".format(_str_funcName,mesh,uValue,vValue))
        log.error(">>> {0} >> error: {1}".format(_str_funcName,error))        
        return None
    
    
