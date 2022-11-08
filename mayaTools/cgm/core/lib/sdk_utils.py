"""
------------------------------------------
snap_utils: cgm.core.lib.sdk_utils
Author: Josh Burton & David Bokser
email: cgmonks.info@gmail.com
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

"""
__MAYALOCAL = 'SDK'

# From Python =============================================================
import copy
import re
import random
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# From Maya =============================================================
import maya.cmds as mc
from maya import mel


import cgm.core.lib.search_utils as SEARCH
#reload(SEARCH)
import cgm.core.lib.attribute_utils as ATTR
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.list_utils as LISTS
from cgm.core import cgm_General as cgmGEN

log_start = cgmGEN.logString_start
log_sub = cgmGEN.logString_sub
log_msg = cgmGEN.logString_msg

def get_driven(driver = None, getPlug = True, select = True):
    """
    Get the driven objects or plugs by following the anim curve out of our intial driver
    
    :parameters:
        driver(str): Attribute to map. If none provided, checks selection
        getPlug(bool): Whether to get plug or node
        select(bool): Select the result

    :returns
        driven
    """   
    _str_func = 'get_driven'
    
    driver = VALID.listArg(driver)
    if not driver:
        driver = SEARCH.get_selectedFromChannelBox(False) or []
        
    log.debug("|{0}| >> Driver: {1}".format(_str_func, driver))
    if not driver:
        log.error("|{0}| >> No driver found or offered. Try selecting an attribute that is an sdk driver".format(_str_func))            
        return False
    l_driven = []
    for d in driver:
        _buffer = mc.listConnections(d, scn = True, s = False, t = 'animCurve') or []
        if not _buffer:
            log.error("|{0}| >> Driver: {1} | No data found".format(_str_func, d))            
        for c in _buffer:
            log.debug("|{0}| >> Checking: {1}".format(_str_func, c))
            #b_transform = VALID.is_transform(c)
            #if not b_transform:
            l_driven.append( SEARCH.seek_downStream(c, mode='isTransform', getPlug=getPlug) )

    l_driven = LISTS.get_noDuplicates(l_driven)
    if not l_driven:
        log.error("|{0}| >> No driven found".format(_str_func))            
        return False        
    if select:
        mc.select(l_driven)
        pprint.pprint(l_driven)
    return l_driven

def get_driver(driven = None, getPlug = True, select = True):
    """
    Get the driver objects or plugs by following the anim curve out of our intial driven
    
    :parameters:
        driven(str): Attribute to map. If none provided, checks selection
        getPlug(bool): Whether to get plug or node
        select(bool): Select the result

    :returns
        driven
    """   
    _str_func = 'get_driver'
    
    driven = VALID.listArg(driven)
    if not driven:
        driven = SEARCH.get_selectedFromChannelBox(False) or []
        
    log.debug("|{0}| >> Driven: {1}".format(_str_func, driven))
    if not driven:
        log.error("|{0}| >> No driven found or offered. Try selecting an attribute that is an sdk driven".format(_str_func))            
        return False
    l_driver = []
    for d in driven:
        _buffer = mc.listConnections(d, scn = True, s = True, d= False) or []
        if not _buffer:
            log.error("|{0}| >> Driven: {1} | No data found".format(_str_func, d))            
        for c in _buffer:
            log.debug("|{0}| >> Checking: {1}".format(_str_func, c))
            #b_transform = VALID.is_transform(c)
            #if not b_transform:
            l_driver.append( SEARCH.seek_upStream(c, mode='isTransform', getPlug=getPlug) )

    l_driver = LISTS.get_noDuplicates(l_driver)
    if not l_driver:
        log.error("|{0}| >> No driver found".format(_str_func))            
        return False        
    if select:
        mc.select(l_driver)
        pprint.pprint(l_driver)
    return l_driver

def get_animCurve(driverAttribute,drivenObject):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
    ACKNOWLEDGEMENT:
    Jason Schleifer's AFR Materials.

    DESCRIPTION:
    Returns the anim curve from a driver to a driven object

    ARGUMENTS:
    driverAttribute(string)
    drivenObject(string)

    RETURNS:
    driverCurves(list)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    driverFuture = mc.listConnections(driverAttribute,type = 'animCurve')
    buffer = mc.listConnections(drivenObject,s=True)
    drivenPast = mc.listHistory(buffer[0])
    
    #reload(LISTS)
    return LISTS.get_matchList(driverFuture,drivenPast)


def walk_sdkInfo(driverAttribute,stripObj=True):
    _str_func = 'walk_sdkInfo'
    
    l_driven = get_driven(driverAttribute,True)
    if not l_driven:
        return log.error( log_msg(_str_func, "No driven") )
    
    _res = {}
    
    for o in l_driven:
        if stripObj:
            _o = o.split('.')[1]
        else:
            _o = o
            
        _res[_o] = get_sdkInfo(driverAttribute, o)
        
    
    #pprint.pprint(_res)
    return _res
        
    

    
def get_sdkInfo(driverAttribute,drivenObject, simple = True):
    """ 
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
    DESCRIPTION:
    Returns the info for a sdk curve

    ARGUMENTS:
    driverAttribute(string)
    drivenObject(string)

    RETURNS:
    curveInfo(dict){time:value,etc...}
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    driverCurve = get_animCurve(driverAttribute,drivenObject)
    
    if driverCurve:
        _res = {}
        keyCnt = mc.keyframe(driverCurve[0],q=True, keyframeCount = True)
        curveValues = mc.keyframe(driverCurve[0],q=True, vc=True)
        #pprint.pprint([keyCnt,curveValues])
        _d = {}
        _l = ['lock','ia','ix','iy','oy','ox','ow','itt','ott','iw','wl']
        
        for k in _l:
            _d[k] = mc.keyTangent(driverCurve[0], q=1,**{k:1})
        
        #for i in range(keyCnt):
            #_t = mc.keyframe(driverCurve[0], index = (i,[i]), query=True, fc=True)
            #_res[curveValues[i]] = {'v':curveValues[i],'kf':_t}
        
        
        for cnt in range(keyCnt):
            _d_tmp = {}
            # Because maya is stupid and the syntax for this in python unfathomable my mere mortals such as I
            mel.eval('string $animCurve = "%s";' %driverCurve[0])
            mel.eval('int $cnt = %i;' %cnt)
            keyTimeValue = mel.eval('keyframe -index $cnt -query -fc $animCurve')
            
            _d_tmp['v'] = curveValues[cnt]
            
            if not simple:
                #_d_tmp['curve'] = driverCurve[0]
                for k in _l:
                    _d_tmp[k] = _d[k][cnt]
            
            _res[keyTimeValue[0]] = _d_tmp
            
        #pprint.pprint(_res)
        return _res
    
def set_sdk_fromDict(driverAttribute,targets, dat = {}):
    _str_func = 'set_sdk_fromDict'
    log.info(log_start(_str_func))
    
    for o in targets:
        log.info(log_sub(_str_func,o))
        
        for a,d in dat.iteritems():
            for dv,d2 in d.iteritems():
                mc.setDrivenKeyframe("{0}.{1}".format(o,a),
                                     currentDriver = driverAttribute,
                                     driverValue = dv, value = d2['v'])        
            
