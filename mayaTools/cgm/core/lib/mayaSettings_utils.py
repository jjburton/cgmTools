"""
------------------------------------------
arrange_utils: cgm.core.lib.mayaSettings_utils
Author: Benn Garnish
email: 
Website : http://www.cgmonks.com
------------------------------------------

"""
#__MAYALOCAL = 'MAYASETTINGS'

# From Python =============================================================
#import copy
#import re
#import sys
#import os
import pprint

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc
#import maya.mel as mel

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGEN
from cgm.core.cgmPy import validateArgs as VALID

#>>> Utilities
#===================================================================
def distanceUnit_get():
    _str_func = 'distanceUnit_get'
    log.debug(cgmGEN.logString_start(_str_func))    
    return mc.currentUnit(q=1, linear=True)

def distanceUnit_set(arg) :
    _str_func = 'distanceUnit_set'
    log.debug(cgmGEN.logString_start(_str_func))
    
    d_validArgs = {'m':['meter','metre'],
                   'cm':['centimeter','centi'],
                   'mm':['milimeter','mili'],
                   'yd':['yard'],
                   'in':['inch','inches'],
                   'ft':['feet', 'foot']
                   }
    
    _arg = VALID.kw_fromDict(arg,d_validArgs, calledFrom=_str_func)
    
    log.debug(cgmGEN.logString_msg(_str_func,"| arg: {0} | validated: {1}".format(arg,_arg)))

    mc.currentUnit(linear = _arg)
    
def frameRate_get():
    _str_func = 'frameRate_get'
    log.debug(cgmGEN.logString_start(_str_func))    
    return mc.currentUnit(q=1, time=True)    

def frameRate_set(arg):
    _str_func = 'frameRate_set'
    log.debug(cgmGEN.logString_start(_str_func))
    
    d_validArgs = {'ntsc':['n','ntsc'],
                   'pal':['p','pal'],
                   'film':['f', 'film'],
                   'game':['g','game'],
                   'ntscf':['ntscf']
                   }
    
    _arg = VALID.kw_fromDict(arg,d_validArgs, calledFrom=_str_func)
    
    log.debug(cgmGEN.logString_msg(_str_func,"| arg: {0} | validated: {1}".format(arg,_arg)))

    mc.currentUnit(time = _arg)
    
def sceneUp_get():
    _str_func = 'sceneUp_get'
    log.debug(cgmGEN.logString_start(_str_func))    
    return mc.upAxis(q=1, ax=True)

def sceneUp_set(arg):
    _str_func = 'sceneUp_set'
    log.debug(cgmGEN.logString_start(_str_func))
    
    d_validArgs = {'y':['y'],
                   'z':['z']
                   }
    
    _arg = VALID.kw_fromDict(arg,d_validArgs, calledFrom=_str_func)
    
    log.debug(cgmGEN.logString_msg(_str_func,"| arg: {0} | validated: {1}".format(arg,_arg)))

    mc.upAxis(ax = _arg, rv = 1)

def defaultTangents_get():
    _str_func = 'defaultTangents_get'
    log.debug(cgmGEN.logString_start(_str_func))    
    return mc.keyTangent(q = 1, itt = True, ott = True)  

def defaultTangents_set(arg):
    _str_func = 'defaultTangents_set'
    log.debug(cgmGEN.logString_start(_str_func))
    
    d_validArgs = {'linear':['ln','linear'],
                   'spline':['sp','spline'],
                   'clamped':['cl','clamped'],
                   'flat':['fl','flat'],
                   'plateau':['pl','plateau'],
                   'auto':['au','auto']
                   }
    _arg = VALID.kw_fromDict(arg,d_validArgs, calledFrom=_str_func)
    
    log.debug(cgmGEN.logString_msg(_str_func,"| arg: {0} | validated: {1}".format(arg,_arg)))
    
    #Couldn't use True for setting the Tangent type had to use _arg
    mc.keyTangent(g= 1, itt = _arg, ott = _arg)
    
def weightedTangents_get():
    _str_func = 'weightedTangents_get'
    log.debug(cgmGEN.logString_start(_str_func))    
    return mc.keyTangent(q = 1, wt = True)    
    
def weightedTangets_set(arg):
    _str_func = 'weightedTangets_set'
    log.debug(cgmGEN.logString_start(_str_func))
    
    d_validArgs = {'false':['False','0'],
                   'True':['True','1']                   
                   }
    _arg = VALID.kw_fromDict(arg,d_validArgs, calledFrom=_str_func)
    
    log.debug(cgmGEN.logString_msg(_str_func,"| arg: {0} | validated: {1}".format(arg,_arg)))
    
    mc.keyTangent(edit = 1, g= 1, wt = _arg)