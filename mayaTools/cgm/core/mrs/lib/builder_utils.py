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

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta
from Red9.core import Red9_AnimationUtils as r9Anim

#========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#========================================================================

import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_PuppetMeta as PUPPETMETA

from cgm.core.lib import curve_Utils as CURVES
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import position_utils as POS
from cgm.core.lib import math_utils as MATH
from cgm.core.lib import distance_utils as DIST
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.rigger.lib import joint_Utils as JOINTS
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import rayCaster as RAYS
from cgm.core.cgmPy import validateArgs as VALID




#Dave, here's the a few calls we need...
#Here's some code examples when I initially looked at it...
from cgm.core.cgmPy import os_Utils as cgmOS
cgmOS.get_lsFromPath(cgm.core.mrs.blocks.__file__,'*.py')

import cgm.core.mrs.blocks.box
cgm.core.mrs.blocks
cgm.core.mrs.blocks.box.__name__.split('.')[-1]

#Both of these should 'walk' the appropriate dirs to get their updated data. They'll be used for both ui and regular stuff
def get_rigBlocks_dict():
    """
    This module needs to return a dict like this:
    
    {'blockName':moduleInstance(ex mrs.blocks.box),
    }
    """
    pass
def get_rigBLocks_byCategory():
    """
    This module needs to return a dict like this:
    
    {blocks:[box,bank,etc],
     blocksSubdir:[1,2,3,etc]
    }
    """    
    pass
