"""
------------------------------------------
list_utils: cgm.core.lib.list_utils
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
#from Red9.core import Red9_Meta as r9Meta

# From cgm ==============================================================



#>>> Utilities
#===================================================================
def get_noDuplicates(l):
    """
    Get a list with no duplicates
    """    
    _l = []
    for v in l:
        if v not in _l:
            _l.append(v)
    return _l

