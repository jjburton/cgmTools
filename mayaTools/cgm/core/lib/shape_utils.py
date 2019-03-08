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
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From Red9 =============================================================
from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core.lib import shared_data as SHARED
from cgm.core.lib import search_utils as SEARCH
from cgm.core.lib import name_utils as coreNames
from cgm.core.lib import rigging_utils as RIGGING
from cgm.core.lib import attribute_utils as ATTR
reload(SEARCH)
reload(SHARED)



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

def get_nonintermediate(shape):
    """
    Get the nonintermediate shape on a transform
    
    :parameters:
        shape(str): Shape to check

    :returns
        non intermediate shape(string)
    """   
    _str_func = "get_nonintermediate"
    try:
        if not VALID.is_shape(shape):
            _shapes = mc.listRelatives(shape, fullPath = True)
            _l_matches = []
            for s in _shapes:
                if not ATTR.get(s,'intermediateObject'):
                    _l_matches.append(s)
            if len(_l_matches) == 1:
                return _l_matches[0]
            else:
                raise ValueError,"Not sure what to do with this many intermediate shapes: {0}".format(_l_matches)        
        elif ATTR.get(shape,'intermediateObject'):
            _type = VALID.get_mayaType(shape)
            _trans = SEARCH.get_transform(shape)
            _shapes = mc.listRelatives(_trans,s=True,type=_type, fullPath = True)
            _l_matches = []
            for s in _shapes:
                if not ATTR.get(s,'intermediateObject'):
                    _l_matches.append(s)
            if len(_l_matches) == 1:
                return _l_matches[0]
            else:
                raise ValueError,"Not sure what to do with this many intermediate shapes: {0}".format(_l_matches)
        else:
            return shape
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)
