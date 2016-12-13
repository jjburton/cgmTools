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


def get_closest(source = None, targets = None, mode = 'point',
                sourcePivot = 'rp', targetPivot = 'rp'):
    """
    Get the the closest return based on a source and target and variable modes
    
    :parameters:
        arg(str/list): Object(s) to check

    :returns
        boundingBox size(list)
    """   
    _str_func = 'get_closest'
    
    _source = VALID.objString(source,noneValid=False,calledFrom= __name__ + _str_func + ">> validate targets")   
    _targets = VALID.objStringList(targets,noneValid=False,calledFrom= __name__ + _str_func + ">> validate targets")
    _mode = mode
    
    _sourcePivot = VALID.kw_fromDict(sourcePivot, SHARED._d_pivotArgs, noneValid=False,calledFrom= __name__ + _str_func + ">> validate sourcePivot")
    _targetPivot = VALID.kw_fromDict(sourcePivot, SHARED._d_pivotArgs, noneValid=False,calledFrom= __name__ + _str_func + ">> validate targetPivot")
    
    log.debug("|{0}| >> source: {1} | targets: {2} | mode:{3} | sourcePivot: {4} | targetPivot: {5}".format(_str_func,_source,targets,_mode,_sourcePivot,_targetPivot))
    
    #Source
    _sourceType = SEARCH.get_mayaType(_source)
    _sourcePos = 
    
    
def get_distance_between_points():
    """
    Gets the distance bewteen two points  
    
    :parameters:
        point1(list): [x,x,x]
        point2(list): [x,x,x]

    :returns
        distance(float)
    """       
    return sqrt( pow(point1[0]-point2[0], 2) + pow(point1[1]-point2[1], 2) + pow(point1[2]-point2[2], 2) )
