"""
------------------------------------------
position_utils: cgm.core.lib.distance_utils
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
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
import maya.mel as mel

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as VALID
#from cgm.core.lib import name_utils as NAME
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import node_utils as NODE
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import list_utils as LISTS
from cgm.core.lib import euclid as EUCLID
import cgm.core.lib.name_utils as NAMES

reload(LISTS)
reload(SHARED)
#Cannot import: DIST, TRANS
#>>> Utilities
#===================================================================
_d_pos_modes = {'xform':['x']}

def get(obj = None, pivot = 'rp', space = 'ws', targets = None, mode = 'xform', asEuclid = False):
    """
    General call for querying position data in maya.
    Note -- pivot and space are ingored in boundingBox mode which returns the center pivot in worldSpace
    
    :parameters:
        obj(str): Object to check
            Transform, components supported
        pivot(str): Which pivot to use. (rotate,scale,boundingBox)
            rotatePivot
            scalePivot
            boundingBox -- Returns the calculated center pivot position based on bounding box
        space(str): World,Object,Local
        mode(str):
            xform -- Utilizes tranditional checking with xForm or pointPosition for components
        asEuclid(bool) - whether to return as Vector or not
    :returns
        success(bool)
    """
    try:
        _str_func = 'get_pos'
        _obj = VALID.mNodeString(obj)
        _pivot = VALID.kw_fromDict(pivot, SHARED._d_pivotArgs, noneValid=False,calledFrom=_str_func)
        _targets = VALID.stringListArg(targets, noneValid=True,calledFrom=_str_func)    
        _space = VALID.kw_fromDict(space,SHARED._d_spaceArgs,noneValid=False,calledFrom=_str_func)
        _mode = VALID.kw_fromDict(mode,_d_pos_modes,noneValid=False,calledFrom=_str_func)
        _res = False
        
        if _pivot == 'boundingBox':
            log.debug("|{0}|...boundingBox pivot...".format(_str_func))                
            _res = get_bb_center(_obj)
            if MATH.is_vector_equivalent(_res,[0,0,0]) and not mc.listRelatives(_obj,s=True):
                _pivot = 'rp'
                log.warning("|{0}|...boundingBox pivot is zero, using rp....".format(_str_func))                
              
        if '[' in _obj:
            log.debug("|{0}| >> component mode...".format(_str_func))        
            if ":" in _obj.split('[')[-1]:
                raise ValueError,"|{0}| >>Please specify one obj. Component list found: {1}".format(_str_func,_obj)
            #_cType = VALID.get_mayaType(_obj)
            _l_comp = VALID.get_component(_obj)
            _root = _l_comp[1]
            _cType = _l_comp[3]
            if not VALID.is_shape(_root):
                _shapes = mc.listRelatives (_root, s=True, fullPath=True) or []
                if len(_shapes) > 1:
                    log.warning("|{0}| >>More than one shape found. To be more accurate, specify: {1} | shapes: {2}".format(_str_func,_obj,_shapes))
                _root = _shapes[0]
                
            _OBJ = '.'.join([_root,_l_comp[0]])
            
            log.debug("|{0}| >> obj: {1}({6}) | type: {2} | pivot: {3} | space: {4} | mode: {5}".format(_str_func,_OBJ,_cType,_pivot,_space,_mode,_obj)) 
            
            kws_pp = {'world':False,'local':False}
            if _space == 'world':kws_pp['world'] = True
            else: kws_pp['local'] = True      
                        
            if _cType == 'polyVertex':
                _res = mc.pointPosition(_OBJ,**kws_pp)
            elif _cType == 'polyEdge':
                mc.select(cl=True)
                mc.select(_OBJ)
                mel.eval("PolySelectConvert 3")
                edgeVerts = mc.ls(sl=True,fl=True)
                posList = []
                for vert in edgeVerts:
                    posList.append(mc.pointPosition(vert,**kws_pp))
                _res = MATH.get_average_pos(posList)
            elif _cType == 'polyFace':
                mc.select(cl=True)
                mc.select(_OBJ)
                mel.eval("PolySelectConvert 3")
                edgeVerts = mc.ls(sl=True,fl=True)
                posList = []
                for vert in edgeVerts:
                    posList.append(mc.pointPosition(vert,**kws_pp))
                _res = MATH.get_average_pos(posList)
            elif _cType in ['surfaceCV','curveCV','editPoint','surfacePoint','curvePoint']:
                _res = mc.pointPosition (_OBJ,**kws_pp)
                #_res =  mc.pointPosition(_OBJ)            
            else:
                raise RuntimeError,"|{0}| >> Shouldn't have gotten here. Need another check for component type. '{1}'".format(_str_func,_cType)
    
        else:
            log.debug("|{0}| >> obj: {1} | pivot: {2} | space: {3} | mode: {4} | asEuclid: {5}".format(_str_func,_obj,_pivot,_space,_mode,asEuclid))             
            if _space == 'local' or _pivot == 'local':
                _res  = ATTR.get(_obj,'translate')            
            #elif _pivot == 'local':
                #if _space == 'world':
                #    _res = mc.xform(_obj, q=True, rp = True, ws=True )
                #else:
                #    _res = ATTR.get(_obj,'translate')            
            else:
                kws = {'q':True,'rp':False,'sp':False,'os':False,'ws':False}
                if _pivot == 'rp':kws['rp'] = True
                else: kws['sp'] = True
                
                if _space == 'object':kws['os']=True
                else:kws['ws']=True
                
                log.debug("|{0}| >> xform kws: {1}".format(_str_func, kws)) 
            
                _res = mc.xform(_obj,**kws )
        
        if _res is not None:
            if asEuclid:
                log.debug("|{0}| >> asEuclid...".format(_str_func))             
                return EUCLID.Vector3(_res[0], _res[1], _res[2])
            return _res
        raise RuntimeError,"|{0}| >> Shouldn't have gotten here: obj: {1}".format(_str_func,_obj)
    except Exception,err:cgmGen.cgmExceptCB(Exception,err)
    
def set(obj = None, pos = None, pivot = 'rp', space = 'ws', relative = False):
    """
    General call for querying position data in maya.
    Note -- pivot and space are ingored in boundingBox mode which returns the center pivot in worldSpace
    
    :parameters:
        obj(str): Object to check
            Transform, components supported
        pivot(str): Which pivot to use to base movement from (rotate,scale)
        space(str): World,Object
    :returns
        success(bool)
    """
    try:
        _str_func = 'set_pos'
        _obj = VALID.mNodeString(obj)
        _pivot = VALID.kw_fromDict(pivot, SHARED._d_pivotArgs, noneValid=False,calledFrom=_str_func)
        _space = VALID.kw_fromDict(space,SHARED._d_spaceArgs,noneValid=False,calledFrom=_str_func)
        
        try:pos = [pos.x,pos.y,pos.z]
        except:pass
        _pos = pos
                  
        if VALID.is_component(_obj):
            kws = {'ws':False,'os':False, 'r':relative}
            if _space == 'object':
                kws['os']=True
                #kws['rpr'] = False
            else:kws['ws']=True
            
            log.debug("|{0}| >> xform kws: {1}".format(_str_func, kws)) 
        
            return mc.move(_pos[0],_pos[1],_pos[2], _obj,**kws)#mc.xform(_obj,**kws )        
        else:
            log.debug("|{0}| >> obj: {1} | pos: {4} | pivot: {2} | space: {3}".format(_str_func,_obj,_pivot,_space,_pos))             
            if _space == 'local' or _pivot == 'local':
                ATTR.set(_obj,'translate',pos) 
            else:
                kws = {'rpr':False,'spr':False,'os':False,'ws':False,'r':relative}
                
                if _pivot == 'rp':kws['rpr'] = True
                else: kws['spr'] = True
                
                if _space == 'object':
                    kws['os']=True
                    kws['rpr'] = False
                else:kws['ws']=True
                
                log.debug("|{0}| >> xform kws: {1}".format(_str_func, kws)) 
            
                return mc.move(_pos[0],_pos[1],_pos[2], _obj,**kws)#mc.xform(_obj,**kws )  
    except Exception,err:cgmGen.cgmExceptCB(Exception,err)
    
def get_local(obj = None, asEuclid = False):
    """
    Query the local translate
    
    :parameters:
        obj(str): obj to query
        asEuclid(bool) - whether to return as Vector or not

    :returns
        pos(list/Vector3)
    """   
    _str_func = 'get_local'
        
    return get(VALID.mNodeString(obj),'local',asEuclid = asEuclid)

def set_local(obj = None, pos = None):
    """
    Set the local translate
    
    :parameters:
        obj(str): obj to set

    :returns
        pos(list/Vector3)
    """   
    _str_func = 'set_local'
        
    return set(VALID.mNodeString(obj), pos, 'local')


def get_bb_center(obj = None, asEuclid =False):
    """
    Get the bb center of a given arg
    
    :parameters:
        obj(str/list): Object(s) to check
        asEuclid(bool) - whether to return as Vector or not

    :returns
        boundingBox size(list)
    """   
    _str_func = 'get_bb_center'
    log.debug("|{0}| >> Change this call to get_bb_pos mode center".format(_str_func))
    return get_bb_pos(obj,mode='center', asEuclid=asEuclid)

def get_bb_pos(arg = None, shapes = False, mode = 'center', mark = False, asEuclid = False):
    """
    Get points relative to a bounding box where z is forward
    
    :parameters:
        arg(str/list): Object(s) to check
        shapes(bool): Only check dag node shapes
        mode(varied): 
            center
            bottom
            top
            left
            right
            front
            back
        mark(bool): whether to add a locator at the position for testing
        asEuclid(bool) - whether to return as Vector or not

    :returns
        boundingBox size(list)
    """   
    _str_func = 'get_bb_pos'
    #_arg = VALID.stringListArg(arg,False,_str_func)
    _sel = mc.ls(sl=True)
    bb_raw = get_bb_size(arg, shapes, mode = 'raw')
    _mode = mode.lower()
    if _mode == 'center':
        log.debug("|{0}| >> Center mode".format(_str_func))
        _res = [((bb_raw[0] + bb_raw[3])/2),((bb_raw[4] + bb_raw[1])/2), ((bb_raw[5] + bb_raw[2])/2)]
    elif _mode in ['bottom','y-']:
        log.debug("|{0}| >> Bottom mode".format(_str_func))
        _res = [((bb_raw[0] + bb_raw[3])/2), bb_raw[1], ((bb_raw[5] + bb_raw[2])/2)]
    elif _mode in ['top','y+']:
        log.debug("|{0}| >> Top mode".format(_str_func))
        _res = [((bb_raw[0] + bb_raw[3])/2), bb_raw[4], ((bb_raw[5] + bb_raw[2])/2)]
    elif _mode  in ['front','z+']:
        log.debug("|{0}| >> Front mode".format(_str_func))
        _res = [((bb_raw[0] + bb_raw[3])/2),((bb_raw[4] + bb_raw[1])/2), bb_raw[5]]
    elif _mode in ['back','z-']:
        log.debug("|{0}| >> Back mode".format(_str_func))        
        _res = [((bb_raw[0] + bb_raw[3])/2),((bb_raw[4] + bb_raw[1])/2), bb_raw[2]]
    elif _mode  in ['left','x+']:
        log.debug("|{0}| >> Left mode".format(_str_func))
        _res = [bb_raw[3] ,((bb_raw[4] + bb_raw[1])/2), ((bb_raw[5] + bb_raw[2])/2)]        
    elif _mode  in ['right','x-']:
        log.debug("|{0}| >> Right mode".format(_str_func))
        _res = [bb_raw[0] ,((bb_raw[4] + bb_raw[1])/2), ((bb_raw[5] + bb_raw[2])/2)]                
    else:
        raise ValueError,"|{0}| >> Unknown mode: {1}".format(_str_func,_mode)

            
    if mark:
        _size = get_bb_size(arg, shapes)
        _loc = mc.spaceLocator()[0]
        ATTR.set(_loc,'scale', [v/4 for v in _size])        
        mc.move (_res[0],_res[1],_res[2], _loc, ws=True)        
        mc.rename(_loc, '{0}_loc'.format(_mode))
    if _sel:
        mc.select(_sel)
    if asEuclid:
        log.debug("|{0}| >> asEuclid...".format(_str_func))             
        return EUCLID.Vector3(_res[0], _res[1], _res[2])
    return _res


def get_bb_size(arg = None, shapes = False, mode = None, asEuclid = False):
    """
    Get the bb size of a given arg
    
    :parameters:
        arg(str/list): Object(s) to check
        shapes(bool): Only check dag node shapes
        mode(varied): 
            True/'max': Only return max value
            'min': Only min
            maxFill - [max,max.max]

    :returns
        boundingBox size(list)
    """   
    _str_func = 'get_bb_size'
    #_arg = VALID.stringListArg(arg,False,_str_func)   
    arg = VALID.mNodeString(arg)
    if shapes:
        log.debug("|{0}| >> shapes mode ".format(_str_func))        
        arg = VALID.listArg(arg)
        l_use = []
        for o in arg:
            log.debug("|{0}| >> o: '{1}' ".format(_str_func,o))
            l_shapes = mc.listRelatives(o,s=True,fullPath = True) or []
            if l_shapes: l_use.extend(l_shapes)
            else:
                l_use.append(o)
        arg = l_use
        
    log.debug("|{0}| >> arg: '{1}' ".format(_str_func,arg))
    _box = mc.exactWorldBoundingBox(arg)
    
    if mode == 'raw':
        if asEuclid:
            log.debug("|{0}| >> asEuclid...".format(_str_func))             
            return EUCLID.Vector3(_box[0], _box[1], _box[2])                
        return _box
    _res = [(_box[3] - _box[0]), (_box[4] - _box[1]), (_box[5] - _box[2])]
    
    if mode is None:
        if asEuclid:
            log.debug("|{0}| >> asEuclid...".format(_str_func))             
            return EUCLID.Vector3(_res[0], _res[1], _res[2])        
        return _res
    elif mode in [True, 'max']:
        return max(_res)
    elif mode in ['min']:
        return min(_res)
    elif mode == 'maxFill':
        _max = max(_res)
        return [_max,_max,_max]
    else:
        log.error("|{0}| >> Unknown mode. Returning default. {1} ".format(_str_func,mode))
    return _res    

def get_axisBox_size(arg = None, children = False, mode = None, asEuclid = False):
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
    _str_func = 'get_axisBox_size'
    #_arg = VALID.stringListArg(arg,False,_str_func)   
    try:
        log.debug("|{0}| >> shapes mode ".format(_str_func))        
        arg = VALID.listArg(arg)
        
        _dag = VALID.getTransform(arg[0])
        if not _dag:
            raise ValueError,"Must have a dag node. Obj: {0}".format(_dag)
        if VALID.is_shape(_dag):
            l_shapes = [_dag]
        else:
            l_shapes = mc.listRelatives(_dag, s=True, fullPath = True) or []
        
        _dup = mc.duplicate(l_shapes,po=False,rc=True)[0]
        if not children:
            for o in mc.listRelatives (_dup, children = True,type='transform',fullPath=True) or []:
                mc.delete(o)
        try:_dup =  mc.parent(_dup, world = True)[0]
        except:pass
        
        #Reset our stuff before we make our bb...
        ATTR.reset(_dup,['t','r','shear'])        
        _size = get_bb_size(_dup,True)

        mc.delete(_dup)
        
        _res = _size
        
        if mode is None:
            if asEuclid:
                log.debug("|{0}| >> asEuclid...".format(_str_func))             
                return EUCLID.Vector3(_res[0], _res[1], _res[2])        
            return _res
        elif mode in [True, 'max']:
            return max(_res)
        elif mode in ['min']:
            return min(_res)
        else:
            log.error("|{0}| >> Unknown mode. Returning default. {1} ".format(_str_func,mode))
        return _res            
    except Exception,err:
        cgmGen.cgmExceptCB(Exception,err,msg=vars())

def get_uv_position(mesh, uvValue,asEuclid = False):
    """
    Get a uv position in world space. UV should be normalized.
    
    :parameters:
        mesh(string) | Surface uv resides on
        uValue(float) | uValue  
        vValue(float) | vValue 
        asEuclid(bool) - whether to return as Vector or not

    :returns
        pos(double3)

    """        
    _str_func = 'get_uv_position'
    
    _follicle = NODE.add_follicle(mesh)
    ATTR.set(_follicle[0],'parameterU', uvValue[0])
    ATTR.set(_follicle[0],'parameterV', uvValue[1])
    
    _pos = get(_follicle[1])
    mc.delete(_follicle)
    
    if asEuclid:
        log.debug("|{0}| >> asEuclid...".format(_str_func))             
        return EUCLID.Vector3(_pos[0], _pos[1], _pos[2])    
    return _pos

def get_uv_normal(mesh, uvValue,asEuclid = False):
    """
    Get a normal at a uv
    
    :parameters:
        mesh(string) | Surface uv resides on
        uValue(float) | uValue  
        vValue(float) | vValue 
        asEuclid(bool) - whether to return as Vector or not

    :returns
        pos(double3)

    """        
    _str_func = 'get_uv_position'
    
    _follicle = NODE.add_follicle(mesh)
    ATTR.set(_follicle[0],'parameterU', uvValue[0])
    ATTR.set(_follicle[0],'parameterV', uvValue[1])
    
    _normal = ATTR.get(_follicle[0],'outNormal')
    mc.delete(_follicle)
    if asEuclid:
        log.debug("|{0}| >> asEuclid...".format(_str_func))             
        return EUCLID.Vector3(_normal[0], _normal[1], _normal[2])    
    return _normal

def get_info(target = None, boundingBox = False):
    """
    Get data for updating a transform
    
    :parameters
        target(str): What to use for updating our loc

    :returns
        info(dict)
    """   
    _str_func = "get_info"
    _target = VALID.objString(target, noneValid=True, calledFrom = __name__ + _str_func + ">> validate target")
    
    _posPivot = 'rp'
    if boundingBox:
        _posPivot = 'boundingBox'
        
    _transform = VALID.getTransform(target)
    
    log.debug("|{0}| >> Target: {1}  | tranform: {2}".format(_str_func, _target,_transform))                             
        
        
    _d = {}
    _d ['createdFrom']=_target
    _d ['objectType']=VALID.get_mayaType(_target)
    _d ['position']=get(target,_posPivot,'world')
    _d ['translate']=get(target,_posPivot,'local')    
    _d ['scalePivot']=get(_transform,'sp','world')
    _d ['rotation']= mc.xform (_transform, q=True, ws=True, ro=True)
    _d ['rotateOrder']=mc.xform (_transform, q=True, roo=True )
    _d ['rotateAxis'] = mc.xform(_transform, q=True, os = True, ra=True)
    _d ['rotateLocal'] = mc.xform(_transform,q=True, os=True, ro=True)
    
    #cgmGen.log_info_dict(_d,'|{0}.{1}| info...'.format(__name__,_str_func))

    return _d


def layout_byColumn(objList = None,columns=3,startPos = [0,0,0]):
    """
    Get a uv position in world space. UV should be normalized.
    
    :parameters:
        objList(list) | list of objects to arrange
        uValue(float) | uValue  
        vValue(float) | vValue 

    :returns
        pos(double3)

    """        
    _str_func = 'layout_byColumn'
    
    if objList is None:
        objList = mc.ls(sl=True)
    
    if not objList:
        raise ValueError,"|{0}| >> No objList'".format(_str_func)
    
    _l_x = []
    _l_y = []
    
    for obj in objList:
        _bfr = get_bb_size(obj)
        log.debug("|{0}| >> obj: {1} | size: {2}'".format(_str_func,obj,_bfr))
        _l_x.append(_bfr[0])
        _l_y.append(_bfr[1])

    for obj in objList:
        mc.move(0,0,0,obj,a=True)

    sizeX = max(_l_x) * 1.75
    sizeY = max(_l_y) * 1.75

    startX = startPos[0]
    startY = startPos[1]
    startZ = startPos[2]

    col=1
    objectCnt = 0
    #sort the list
    
    _l_sorted = LISTS.get_chunks(objList,columns)
    
    bufferY = startY
    for row in _l_sorted:
        bufferX = startX
        for obj in row:
            mc.xform(obj,os=True,t=[bufferX,bufferY,startZ])
            bufferX += sizeX
        bufferY -= sizeY    
    
def get_midPointDict(sourceList,forceBBCenter = False):
    _str_func = 'get_midPointDict'    
    _d_info = {}
    _l_pos = []
    _l_rot = []
    for s in sourceList:
        log.debug("|{0}| >> Checking source: {1}'".format(_str_func,s))        
        _d_shape = get_info(s,boundingBox=forceBBCenter)
        _l_pos.append(_d_shape['position'])
        _l_rot.append(_d_shape['rotation'])
        _d_info[s] = _d_shape
    #_d_info['info'] = _d_info
    _d_info['positions'] = _l_pos
    _d_info['rotations'] = _l_rot
    _d_info['position'] = MATH.get_average_pos(_l_pos)
    _d_info['rotation'] = MATH.get_average_pos(_l_rot)
    return _d_info


def get_curveMidPointFromDagList(sourceList):
    _str_func = 'get_curveMidPointFromDagList'

    l_pos = [get(o) for o in sourceList]
    knot_len = len(l_pos)+3-1
    _created = mc.curve (d=3, ep = l_pos, k = [i for i in range(0,knot_len)], os=True)    
    shp =  mc.listRelatives(_created, s=True, fullPath = True)[0]
    _min = ATTR.get(shp,'minValue')
    _max = ATTR.get(shp,'maxValue')
    _mid = (_max - _min)/2.0
    
    pos = mc.pointPosition("{0}.u[{1}]".format(shp,_mid), w=True)
    mc.delete(_created)
    return pos
    
    
def get_positionPlug(obj):
    _str_func = 'get_positionPlug'
    
    l_elibiblePlugs = ['worldPosition','position'] 
    d_plugTypes= {'worldPosition':'worldPosition[0]','position':'position'}
    _res = False
    for attr in l_elibiblePlugs:
        if mc.objExists("{0}.{1}".format(obj,attr)):#ATTR.has_attr(obj,attr):
            _res = "{0}.{1}".format(obj,d_plugTypes.get(attr))
    return _res

def create_loc(obj):
    _str_func = 'create_loc'
    infoDict = get_info(obj)
    
    _loc = mc.spaceLocator(name="{0}_loc".format(NAMES.get_base(obj)))[0]
    pos =infoDict['position']
    mc.move (pos[0],pos[1],pos[2], _loc, ws=True)
    mc.xform(_loc, roo=infoDict['rotateOrder'],p=True)
    mc.xform(_loc, ro=infoDict['rotation'], ws = True)
    mc.xform(_loc, ra=infoDict['rotateAxis'],p=True)

    #mTarget = r9Meta.getMObject(target)
    mc.xform(_loc, rp=infoDict['position'], ws = True, p=True)        
    if infoDict.get('scalePivot'):mc.xform(_loc, sp=infoDict['scalePivot'], ws = True, p=True)
    
    return _loc
    

#Vector ===================================================================================================
