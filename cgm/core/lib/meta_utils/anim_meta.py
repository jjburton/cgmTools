"""
------------------------------------------
anim_utils: cgm.core.lib
Author: David Bokser, Josh Burton
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

================================================================
"""
import logging
import pprint

import maya.cmds as mc

import cgm.core.cgm_Meta as cgmMeta
import cgm.core.cgm_General as cgmGEN
import cgm.core.lib.search_utils as SEARCH
import cgm.core.lib.math_utils as COREMATH
import cgm.core.lib.position_utils as POS
import cgm.core.lib.distance_utils as DIST
import cgm.core.lib.attribute_utils as ATTR

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

log_msg = cgmGEN.logString_msg
log_sub = cgmGEN.logString_sub
log_start = cgmGEN.logString_start



def rotateOrder_change(nodes=None,rotateOrder='zyx',timeContext='all',report=True):
    _str_func = 'rotateOrder_change'
    ml_nodes = cgmMeta.validateObjListArg(nodes,noneValid =True) or cgmMeta.asMeta(sl=1)
    current_time = mc.currentTime(query=True)
    _res = {}
    for mObj in ml_nodes:
        d_dat = {}
        _keys = SEARCH.get_key_indices_from(mObj.mNode,timeContext)        
        if mObj.getEnumValueString('rotateOrder') == rotateOrder:
            print(cgmGEN.logString_msg(_str_func,"Already has rotateOrder: {} | {}".format(rotateOrder,mObj.p_nameShort)))
            continue
            
        _res[mObj] = []
        if not _keys:#...just do it now
            mc.currentTime(current_time)#...set in case another obj offset this
            mc.xform(mObj.mNode,rotateOrder=rotateOrder,p=True)
            _res[mObj].append(current_time)
            continue
            
        for k in _keys:#...first loop get our values
            _dat = {}
            d_dat[k] = _dat
            mc.currentTime(k)
            _res[mObj].append(k)
            _dat['aim'] = mObj.getPositionByAxisDistance('{}+'.format(rotateOrder[0]),10)
            _dat['up'] = mObj.getAxisVector('{}+'.format(rotateOrder[1]))
        
        mc.xform(mObj.mNode,rotateOrder=rotateOrder,p=True)
        for i,k in enumerate(_keys):
            mc.currentTime(k)
            mObj.doAimAtPoint(d_dat[k]['aim'], '{}+'.format(rotateOrder[0]), '{}+'.format(rotateOrder[1]), mode='vector', vectorUp = d_dat[k]['up'], ignoreAimAttrs=True)

            
    mc.currentTime(current_time)
    if report:
        pprint.pprint(_res)
    if not nodes:
        mc.select([mObj.mNode for mObj in ml_nodes])
        
    return  bool(_res)