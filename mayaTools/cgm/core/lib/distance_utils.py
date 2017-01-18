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

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================

# From cgm ==============================================================
#NO LOC
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATHUTILS
from cgm.core.lib import name_utils as NAMES
reload(POS)
reload(MATHUTILS)

from cgm.lib import attributes
#>>> Utilities
#===================================================================
def get_bb_size(arg = None):
    """
    Get the bb size of a given arg
    
    :parameters:
        arg(str/list): Object(s) to check


    :returns
        boundingBox size(list)
    """   
    _str_func = 'get_bb_size'
    _arg = VALID.stringListArg(arg,False,_str_func)   
    log.debug("|{0}| >> arg: '{1}' ".format(_str_func,_arg))    
    
    _box = mc.exactWorldBoundingBox(_arg)
    return [(_box[3] - _box[0]), (_box[4] - _box[1]), (_box[5] - _box[2])]


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
                log.info("|{0}| >> {1}: {2}".format(_str_func,t,res))
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
    
    _startPos = MATHUTILS.Vector3(startPos[0],startPos[1],startPos[2])
    _dir = MATHUTILS.Vector3(vec[0],vec[1],vec[2])
    
    _new = _startPos + _dir * distance
    
    return _new.x,_new.y,_new.z


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
        _shapes = mc.listRelatives(VALID.get_component(targetSurface)[1], s=True)
    else:
        _shapes = mc.listRelatives(targetSurface, s=True)
    
    if not _shapes:
        log.error("|{0}| >> Unsupported target surface type. Skipping: {1}".format(_str_func,targetSurface))
        mc.delete(_loc)
        return False
    
    _l_res_positions = []
    _l_res_shapes = []
    _l_res_distances = []
    
    for s in _shapes:    
        _type = VALID.get_mayaType(s)
        
        if _type not in ['mesh','nurbsSurface','nurbsCurve']:
            log.error("|{0}| >> Unsupported target surface type. Skipping: {1} |{2}".format(_str_func,s,_type))
            _l_res_positions.append(False)
            continue
        
        if _type == 'mesh':
            _node = mc.createNode ('closestPointOnMesh')
            
            attributes.doConnectAttr((_loc+'.translate'),(_node+'.inPosition'))
            attributes.doConnectAttr((s+'.worldMesh'),(_node+'.inMesh'))
            attributes.doConnectAttr((s+'.worldMatrix'),(_node+'.inputMatrix'))
            
            _pos = attributes.doGetAttr(_node,'position')
            _tmpLoc = mc.spaceLocator(n='tmp')[0]
            attributes.doConnectAttr ((_node+'.position'),(_tmpLoc+'.translate'))            
            
            _l_res_positions.append( POS.get(_tmpLoc)  )
            mc.delete(_node)
            mc.delete(_tmpLoc)

        elif _type == 'nurbsSurface':
            closestPointNode = mc.createNode ('closestPointOnSurface')
            
            attributes.doSetAttr(closestPointNode,'inPositionX',_point[0])
            attributes.doSetAttr(closestPointNode,'inPositionY',_point[1])
            attributes.doSetAttr(closestPointNode,'inPositionZ',_point[2])  
            
            attributes.doConnectAttr((s +'.worldSpace'),(closestPointNode+'.inputSurface'))
            _l_res_positions.append(attributes.doGetAttr(closestPointNode,'position'))
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


def create_closest_point_node(source = None, targetSurface = None):
    """
    Create a closest point on surface node and wire it
    
    :parameters:
        source(str/vector) -- source point or object
        targetSurface -- surface to check transform, nurbsSurface, curve, mesh supported

    :returns
        node(list)
    """         
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
        _shapes = [targetSurface]
    else:
        _shapes = mc.listRelatives(targetSurface, s=True)
    
    if not _shapes:
        raise ValueError,"Must have shapes to check."
    
    _nodes = []
    _locs = []
    for s in _shapes:    
        _type = VALID.get_mayaType(s)
        
        if _type not in ['mesh','nurbsSurface','nurbsCurve']:
            log.error("|{0}| >> Unsupported target surface type. Skipping: {0} |{1}".format(_str_func,s,_type))
            continue
        
        _res_loc = mc.spaceLocator(n='{0}_to_{1}_result_loc'.format(NAMES.get_base(source), NAMES.get_base(s)))[0]
        _locs.append(_res_loc)
        
        if _type == 'mesh':
            _node = mc.createNode ('closestPointOnMesh')
            _node = mc.rename(_node, "{0}_to_{1}_closePntMeshNode".format(NAMES.get_base(source), NAMES.get_base(s)))
            attributes.doConnectAttr((_transform+'.translate'),(_node+'.inPosition'))
            attributes.doConnectAttr((s+'.worldMesh'),(_node+'.inMesh'))
            attributes.doConnectAttr((s+'.worldMatrix'),(_node+'.inputMatrix'))
            
            _pos = attributes.doGetAttr(_node,'position')
            attributes.doConnectAttr ((_node+'.position'),(_res_loc+'.translate'))  
            
            _nodes.append(_node)
            
        elif _type == 'nurbsSurface':
            closestPointNode = mc.createNode ('closestPointOnSurface')
            closestPointNode = mc.rename(closestPointNode, "{0}_to_{1}_closePntSurfNode".format(NAMES.get_base(source), NAMES.get_base(s)))
            
            mc.connectAttr ((_transform+'.translate'),(closestPointNode+'.inPosition'))
            
            #attributes.doSetAttr(closestPointNode,'inPositionX',_point[0])
            #attributes.doSetAttr(closestPointNode,'inPositionY',_point[1])
            #attributes.doSetAttr(closestPointNode,'inPositionZ',_point[2])  
            
            attributes.doConnectAttr((s +'.worldSpace'),(closestPointNode+'.inputSurface'))
            
            attributes.doConnectAttr ((closestPointNode+'.position'),(_res_loc+'.translate'))  
            _nodes.append(closestPointNode)
            
        elif _type == 'nurbsCurve':
            _node = mc.createNode ('nearestPointOnCurve')
            _node = mc.rename(_node, "{0}_to_{1}_nearPntCurveNode".format(NAMES.get_base(source), NAMES.get_base(s)))
            
            p = []
            distances = []
            mc.connectAttr ((_transform+'.translate'),(_node+'.inPosition'))
            mc.connectAttr ((s+'.worldSpace'),(_node+'.inputCurve'))
            
            attributes.doConnectAttr ((_node+'.position'),(_res_loc+'.translate'))  
            _nodes.append(_node)
    return _locs, _nodes
            


    
def get_closest_point_data_from_mesh(targetObj = None, targetPoint = None, mesh = None):
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
    if toPoint is not None:
        _point = toPoint
    elif toObject is not None:
        _point = POS.get(toObject)
    if not _point:raise ValueError,"Must have point of reference"
    _loc = mc.spaceLocator()[0]
    POS.set(_loc,_point)  
        
    _shape = False
    if SEARCH.is_shape(mesh):
        if VALID.get_mayaType(mesh) == 'mesh':
            _shape = mesh
        else:raise ValueError,"Must be a mesh shape"
    else:
        _shapes = mc.listRelatives(mesh, s=True)
        _meshes = []
        for s in _shapes:
            if VALID.get_mayaType(s) == 'mesh':
                _meshes.append(s)
        if len(_meshes) == 1:
            _shape = _meshes[0]
    if not _shape:
        raise ValueError,"Must have a mesh shape by now"
        
        
    """ make the closest point node """
    _node = mc.createNode ('closestPointOnMesh')

    """ to account for target objects in heirarchies """
    attributes.doConnectAttr((targetObj+'.translate'),(_node+'.inPosition'))
    attributes.doConnectAttr((_shape+'.worldMesh'),(_node+'.inMesh'))
    attributes.doConnectAttr((_shape+'.matrix'),(_node+'.inputMatrix'))

    _res = {}
    _res['position']=attributes.doGetAttr(_node,'position')
    _res['normal']=attributes.doGetAttr(_node,'normal')
    _res['parameterU']=mc.getAttr(_node+'.parameterU')
    _res['parameterV']=mc.getAttr(_node+'.parameterV')
    _res['closestFaceIndex']=mc.getAttr(_node+'.closestFaceIndex')
    _res['closestVertexIndex']=mc.getAttr(_node+'.closestVertexIndex')

    mc.delete(_node)
    return _res



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
  
            uMin = attributes.doGetAttr(shape,'mnu')
            uMax = attributes.doGetAttr(shape,'mxu')
            vMin = attributes.doGetAttr(shape,'mnv')
            vMax = attributes.doGetAttr(shape,'mxv')         
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

            uMin = attributes.doGetAttr(l_shapes[0],'mnu')
            uMax = attributes.doGetAttr(l_shapes[0],'mxu')
            vMin = attributes.doGetAttr(l_shapes[0],'mnv')
            vMax = attributes.doGetAttr(l_shapes[0],'mxv')         
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
    
    
