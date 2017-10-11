"""
------------------------------------------
snap_utils: cgm.core.lib.sdk_utils
Author: Josh Burton & David Bokser
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

"""
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
reload(SEARCH)
import cgm.core.lib.attribute_utils as ATTR
from cgm.core.cgmPy import validateArgs as VALID
import cgm.core.lib.list_utils as LISTS

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
