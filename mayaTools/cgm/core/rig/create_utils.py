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
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc

# From cgm ==============================================================
from cgm.core import cgm_Meta as cgmMeta
from cgm.core import cgm_General as cgmGEN
import cgm.core.lib.snap_utils as SNAP
import cgm.core.lib.rigging_utils as RIG
import cgm.core.lib.distance_utils as DIST
#reload(DIST)


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
    except Exception,err:cgmGEN.cgmExceptCB(Exception,err)


def get_meshFromNurbs(nurbSurface = None, mode = 'default', uNumber = 10, vNumber = 10):
    mMesh = cgmMeta.validateObjArg(nurbSurface,mayaType='nurbsSurface')
    mDup = mMesh.doDuplicate(po=False)
    
    
    #mNew = self.doCreateAt(setClass='cgmObject')
    newShapes = []
    for mShape in mDup.getShapes(asMeta=1):
        if mode == 'default':
            d_kws = {}
            _res = mc.nurbsToPoly(mShape.mNode, mnd=1,ch=0,f=3,pt =1,pc =200,
                                  chr =0.9,ft =0.01,mel =0.001,d =0.1,ut =1,un =3,
                                  vt =1,vn =3,uch =0,ucr =0,cht =0.2,es =0,ntr =0,
                                  mrt =0,uss =1)            
        elif mode == 'general':
            d_kws = {'mnd' :1,
                     'ch':0 ,
                     'f': 2,
                     'pt': 1,#quad
                     'pc':200,
                     'chr':0.9,
                     'ft':0.01,
                     'mel': 0.001,
                     'd':0.1,
                     'ut': 1,
                     'un': uNumber,
                     'vt':1,
                     'vn': vNumber,
                     'uch': 0,
                     'ucr':0,
                     'cht':0.2,
                     'es':0,
                     'ntr':0,
                     'mrt':0,
                     'uss':1}
            _res = mc.nurbsToPoly(mShape.mNode, **d_kws)
        else:
            raise ValueError,"get_meshFromNurbs | Unknown mode: {0}".format(mode)
        newShapes.append(_res[0])

    if len(newShapes)>1:
        _mesh = mc.polyUnite(newShapes,ch=False)[0]
    else:
        _mesh = newShapes[0]

    mNew = cgmMeta.asMeta(_mesh)

    #for s in newShapes:
    mDup.delete()
    
    return mNew

