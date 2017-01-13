"""
------------------------------------------
shape_utils: cgm.core.lib.shape_utils
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
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGen
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import name_utils as coreNames
from cgm.core.lib import rigging_utils as RIGGING

reload(SHARED)
from cgm.lib import attributes


#>>> Utilities
#===================================================================
def combine(shapeTranforms):
    """
    Combine shapes to a single transform

    :parameters:
        crvShape(str): Object to describe

    :returns
        Prints commands in script editor
        Commands(list)
    """    
    _str_func = 'combine'
    _transform = shapeTranforms[0]
    
    for t in shapeTranforms:
        try:
            pass
        except Exception,err:
            raise Exception,"|{0}| >> Channel history delete on {2} | err: {1}".format(_str_func,err,t)
        
    for t in shapeTranforms[1:]:
        RIGGING.shapeParent_in_place(_transform, t, 
                                     keepSource=False)   
        
    return _transform
            