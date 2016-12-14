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
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import position_utils as POS
reload(POS)
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

def get_bb_center(arg = None):
    """
    Get the bb center of a given arg
    
    :parameters:
        arg(str/list): Object(s) to check

    :returns
        boundingBox size(list)
    """   
    _str_func = 'get_bb_center'
    _arg = VALID.stringListArg(arg,False,_str_func)   
    log.debug("|{0}| >> arg: '{1}' ".format(_str_func,_arg))   
    
    _box = mc.exactWorldBoundingBox(_arg)
    
    return [((_box[0] + _box[3])/2),((_box[4] + _box[1])/2), ((_box[5] + _box[2])/2)]


def get_by_dist(source = None, targets = None, mode = 'closest', resMode = 'point',
                sourcePivot = 'rp', targetPivot = 'rp'):
    """
    Get the the closest return based on a source and target and variable modes
    
    :parameters:
        source(str): Our base object to measure from
        targets(list): List of object types
        mode(str):What mode are we checking data from
            object -- return the closest object
            component -- return the closest base component
            pointOnSurface -- closest point on the target shape(s)
    :returns
        [res,distance]
    """   
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
    if _resMode == 'object':
        log.debug("|{0}| >> object resMode...".format(_str_func))
        _l_distances = []
        for t in _l_targets:
            _tarPos = POS.get(t,_targetPivot,space='world')
            _d = get_distance_between_points(_sourcePos,_tarPos)
            log.debug("|{0}| >> target: {1} | pivot: {4} | dist: {3} | pos: {2}...".format(_str_func,t,_tarPos,_d,_targetPivot))
            _l_distances.append(_d)
        if _mode == 'closest':
            _minDist = min(_l_distances)
            _minIdx = _l_distances.index(_minDist)
            return _l_targets[_minIdx], _minDist
        else:
            _maxDist = max(_l_distances)
            _maxIdx = _l_distances.index(_maxDist)
            return _l_targets[_maxIdx], _maxDist
    elif _resMode == 'pointOnSurface':
        log.debug("|{0}| >> pointOnSurface...".format(_str_func))        
        #Targets=============================================================
        log.debug("|{0}| >> Targets processing...".format(_str_func))
        _d_targetTypes = {}
        for t in _l_targets:
            _type = SEARCH.get_mayaType(t)
            if _type not in _d_targetTypes.keys():
                _d_targetTypes[_type] = [t]
            else:
                _d_targetTypes[_type].append(t)
            log.debug("|{0}| >> obj: {1} | type: {2}".format(_str_func,t,_type))
        cgmGen.log_info_dict(_d_targetTypes,'Targets to type')        
    
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
