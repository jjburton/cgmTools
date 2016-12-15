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

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as VALID
#from cgm.core.lib import name_utils as NAME
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
#Cannot import: DIST,
#>>> Utilities
#===================================================================
_d_pos_modes = {'xform':['x']}

def get(obj = None, pivot = 'rp', space = 'ws', targets = None, mode = 'xform'):
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
        space(str): World,Object
        mode(str):
            xform -- Utilizes tranditional checking with xForm or pointPosition for components
            boundingBox -- Returns the calculated center pivot position based on bounding box 

    :returns
        success(bool)
    """   
    _str_func = 'get_pos'
    _obj = VALID.stringArg(obj,False,_str_func)
    _pivot = VALID.kw_fromDict(pivot, SHARED._d_pivotArgs, noneValid=False,calledFrom=_str_func)
    _targets = VALID.stringListArg(targets, noneValid=True,calledFrom=_str_func)    
    _space = VALID.kw_fromDict(space,SHARED._d_spaceArgs,noneValid=False,calledFrom=_str_func)
    _mode = VALID.kw_fromDict(mode,_d_pos_modes,noneValid=False,calledFrom=_str_func)
        
    if _pivot == 'boundingBox':
        log.debug("|{0}|...boundingBox pivot...".format(_str_func))                
        return DIST.get_bb_center(_obj)
    elif _pivot == 'closestPoint':
        log.debug("|{0}|...closestPoint pivot...".format(_str_func))
        _d_targets = {}
        for t in _targets:
            log.debug("|{0}| target: {1}".format(_str_func,t))                

        #_targetType = SEARCH.get_mayaType(_target)    
    else:
        if '[' in _obj:
            if ":" in _obj:
                raise ValueError,"|{0}| >>Please specify one obj. Component list found: {1}".format(_str_func,_obj)
            _cType = SEARCH.get_mayaType(_obj)
            log.debug("|{0}| >> component mode...".format(_str_func))
            log.debug("|{0}| >> obj: {1} | type: {2} | pivot: {3} | space: {4} | mode: {5}".format(_str_func,_obj,_cType,_pivot,_space,_mode)) 
            
            kws_pp = {'world':False,'local':False}
            if _space == 'world':kws_pp['world'] = True
            else: kws_pp['local'] = True      
                        
            if _cType == 'polyVertex':
                return mc.pointPosition(_obj,**kws_pp)
            elif _cType == 'polyEdge':
                mc.select(cl=True)
                mc.select(_obj)
                mel.eval("PolySelectConvert 3")
                edgeVerts = mc.ls(sl=True,fl=True)
                posList = []
                for vert in edgeVerts:
                    posList.append(mc.pointPosition(vert,**kws_pp))
                return MATH.get_average_pos(posList)
            elif _cType == 'polyFace':
                mc.select(cl=True)
                mc.select(_obj)
                mel.eval("PolySelectConvert 3")
                edgeVerts = mc.ls(sl=True,fl=True)
                posList = []
                for vert in edgeVerts:
                    posList.append(mc.pointPosition(vert,**kws_pp))
                return MATH.get_average_pos(posList)
            elif _cType in ['surfaceCV','curveCV','editPoint','surfacePoint','curvePoint']:
                return mc.pointPosition (_obj,**kws_pp)
            raise RuntimeError,"|{0}| >> Shouldn't have gotten here. Need another check for component type. '{1}'".format(_str_func,_cType)

        else:
            log.debug("|{0}| >> obj: {1} | pivot: {2} | space: {3} | mode: {4}".format(_str_func,_obj,_pivot,_space,_mode))             
            kws = {'q':True,'rp':False,'sp':False,'os':False,'ws':False}
            if _pivot == 'rp':kws['rp'] = True
            else: kws['sp'] = True
            
            if _space == 'object':kws['os']=True
            else:kws['ws']=True
            
            log.debug("|{0}| >> xform kws: {1}".format(_str_func, kws)) 
        
            return mc.xform(_obj,**kws )
    
    raise RuntimeError,"|{0}| >> Shouldn't have gotten here: obj: {1}".format(_str_func,_obj)
    
def set(obj = None, pos = None, pivot = 'rp', space = 'ws'):
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
    _str_func = 'set_pos'
    _obj = VALID.stringArg(obj,False,_str_func)
    _pivot = VALID.kw_fromDict(pivot, SHARED._d_pivotArgs, noneValid=False,calledFrom=_str_func)
    _space = VALID.kw_fromDict(space,SHARED._d_spaceArgs,noneValid=False,calledFrom=_str_func)
    _pos = pos
              
    if SEARCH.is_component(_obj):
        raise NotImplementedError,"Haven't implemented component move"
    else:
        log.debug("|{0}| >> obj: {1} | pos: {4} | pivot: {2} | space: {3}".format(_str_func,_obj,_pivot,_space,_pos))             
        kws = {'rpr':False,'spr':False,'os':False,'ws':False}
        
        if _pivot == 'rotate':kws['rpr'] = True
        else: kws['spr'] = True
        
        if _space == 'object':kws['os']=True
        else:kws['ws']=True
        
        log.debug("|{0}| >> xform kws: {1}".format(_str_func, kws)) 
    
        return mc.move(_pos[0],_pos[1],_pos[2], _obj,**kws)#mc.xform(_obj,**kws )    

def get_info(target = None):
    """
    Get data for updating a transform
    
    :parameters
        target(str): What to use for updating our loc

    :returns
        info(dict)
    """   
    _str_func = "get_dat"
    _target = VALID.objString(target, noneValid=True, calledFrom = __name__ + _str_func + ">> validate target")

    _d = {}
    _d ['createdFrom']=_target
    _d ['objectType']=SEARCH.get_mayaType(_target)
    _d ['position']=POS.get(target,'rp','world')
    _d ['scalePivot']=POS.get(target,'sp','world')
    _d ['rotation']= mc.xform (_target, q=True, ws=True, ro=True)
    _d ['rotateOrder']=mc.xform (_target, q=True, roo=True )
    _d ['rotateAxis'] = mc.xform(_target, q=True, os = True, ra=True)
    
    cgmGeneral.log_info_dict(_d,'|{0}.{1}| info...'.format(__name__,_str_func))

    return _d