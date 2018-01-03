"""
------------------------------------------
create_utils: cgm.core.rig
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------


================================================================
"""
# From Python =============================================================
import copy
import re
import time
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGEN
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rigging_utils as RIG
import cgm.core.lib.distance_utils as DIST
reload(DIST)


def distanceMeasure(start = None, end = None, baseName = 'measureThis',asMeta=True):
    """
    Get the the closest return based on a source and target and variable modes
    
    :parameters:
        :start(str): Our start obj
        :end(str): End obj
        :baseName(str):What mode are we checking data from
        :asMeta(bool)
    :returns
        {shape,dag,loc_start,loc_end,start,end}
    """
    try:
        _str_func = 'create_distanceMeasure'
        
        _res = DIST.create_distanceMeasure(start,end,baseName)
        
        if not asMeta:
            return _res
        
        _res['mShape'] = cgmMeta.asMeta(_res['shape'])
        _res['mDag'] = cgmMeta.asMeta(_res['dag'])
        _res['mStart'] = cgmMeta.asMeta(_res['start'])
        _res['mEnd'] = cgmMeta.asMeta(_res['end'])        
        if _res.get('loc_start'):
            _res['mLoc_start'] = cgmMeta.asMeta(_res['loc_start'])
        if _res.get('loc_end'):
            _res['mLoc_end'] = cgmMeta.asMeta(_res['loc_end'])            
        return _res
    except Exception,err:cgmGEN.cgmException(Exception,err)




