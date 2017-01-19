"""
------------------------------------------
locinator: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------
2.0 rewrite
================================================================
"""
# From Python =============================================================
import copy
import re

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGen
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
reload(SNAP)
reload(LOC)


def update_obj(obj = None, move = True, rotate = True, boundingBox = False):
    """
    Updates an tagged loc or matches a tagged object
    
    :parameters:
        obj(str): Object to modify
        target(str): Target to match

    :returns
        success(bool)
    """     
    _str_func = 'update_obj'
    
    _obj = VALID.objString(obj, noneValid=False, calledFrom = __name__ + _str_func + ">> validate obj")
    
    _locMode = ATTR.get(_obj,'cgmLocMode')
    if _locMode:
        log.info("|{0}| >> loc mode. updating {1}".format(_str_func,NAMES.get_short(_obj)))
        return LOC.update(_obj)
    if mc.objExists(_obj +'.cgmMatchTarget'):
        log.info("|{0}| >> Match mode. Matching {1} | move: {2} | rotate: {3} | bb: {4}".format(_str_func,NAMES.get_short(_obj),move,rotate,boundingBox))
        return SNAP.matchTarget_snap(_obj,move,rotate,boundingBox)
    
    log.info("|{0}| >> Not updatable: {1}".format(_str_func,NAMES.get_short(_obj)))    
    return False
        




