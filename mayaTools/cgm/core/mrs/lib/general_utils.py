"""
------------------------------------------
builder_utils: cgm.core.mrs.lib
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

================================================================
"""
import random
import re
import copy
import time
import os

# From Red9 =============================================================
#from Red9.core import Red9_Meta as r9Meta
#from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#========================================================================

import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core.mrs.lib import shared_dat as BLOCKSHARED
#from cgm.core import cgm_Meta as cgmMeta
#from cgm.core.lib import curve_Utils as CURVES
#from cgm.core.lib import attribute_utils as ATTR
#from cgm.core.lib import position_utils as POS
#from cgm.core.lib import math_utils as MATH
#from cgm.core.lib import distance_utils as DIST
#from cgm.core.lib import snap_utils as SNAP
#from cgm.core.lib import rigging_utils as RIGGING
#from cgm.core.rigger.lib import joint_Utils as JOINTS
#from cgm.core.lib import search_utils as SEARCH
#from cgm.core.lib import rayCaster as RAYS
#from cgm.core.cgmPy import validateArgs as VALID
#from cgm.core.cgmPy import path_Utils as PATH
#from cgm.core.cgmPy import os_Utils as cgmOS

def validate_stateArg(stateArg = None):
    _str_func = 'valid_stateArg'
    _failMsg = "|{0}| >> Invalid: {1} | valid: {2}".format(_str_func,stateArg,BLOCKSHARED._l_blockStates)
    
    if type(stateArg) in [str,unicode]:
        stateArg = stateArg.lower()
        if stateArg in BLOCKSHARED._l_blockStates:
            stateIndex = BLOCKSHARED._l_blockStates.index(stateArg)
            stateName = stateArg
        else:            
            log.warning(_failMsg)
            return False
    elif type(stateArg) is int:
        if stateArg<= len(BLOCKSHARED._l_blockStates)-1:
            stateIndex = stateArg
            stateName = BLOCKSHARED._l_blockStates[stateArg]         
        else:
            log.warning(_failMsg)
            return False        
    else:
        log.warning(_failMsg)        
        return False
    return stateIndex,stateName  



