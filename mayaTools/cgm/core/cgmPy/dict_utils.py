"""
dict_utils
www.cgmonastery.com


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
from maya import OpenMaya

# From Red9 =============================================================
from cgm.core.cgmPy import validateArgs as VALID

# From cgm ==============================================================
#from cgm.core import cgm_General as cgmGeneral
#reload(cgmValid)

#>>> Utilities
def blendDat(dPrimary,dBlend):
    """
    Assumes two lists of
    """
    _res  = {}
    for k,v1 in dPrimary.iteritems():
        v2 = dBlend.get(k)
        v_use = v1
        
        if v2:
            if VALID.isListArg(v1) and VALID.isListArg(v2):
                for v in v2:
                    if v not in v_use:
                        v_use.append(v)
            if issubclass(type(v1),dict) and issubclass(type(v2),dict):
                v_use = blendDat(v1,v2)
        _res[k] = v_use
                        
    for k,v2 in dBlend.iteritems():
        if not _res.get(k):
            _res[k] = v2
        
    return _res
            
        