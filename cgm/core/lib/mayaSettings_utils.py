"""
------------------------------------------
arrange_utils: cgm.core.lib.mayaSettings_utils
Author: Benn Garnish
email: 
Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------

NOTES:
Will need to make sure we save settings in the project manager to force maya to save our settings:

setFocus prefsSaveBtn; savePrefsChanges;
saveToolSettings;
saveViewportSettings;

*** If the user has maya's settings UI open and we are setting our own via the project manager then our settings will be overwritten!!***

"""
__MAYALOCAL = 'MAYASETTINGS'

import cgm.core.lib.search_utils as SEARCH

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
log.setLevel(logging.INFO)

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
    
def angularUnit_get():
    _str_func = 'angularUnit_get'
    log.debug(cgmGEN.logString_start(_str_func))    
    return mc.currentUnit(q=1, angle=True)

def angularUnit_set(arg) :
    _str_func = 'angularUnit_set'
    log.debug(cgmGEN.logString_start(_str_func))
    
    d_validArgs = {'deg':['deg','degree','degrees'],
                   'rad':['rad','radian']
                   }
    
    _arg = VALID.kw_fromDict(arg,d_validArgs, calledFrom=_str_func)
    
    log.debug(cgmGEN.logString_msg(_str_func,"| arg: {0} | validated: {1}".format(arg,_arg)))

    mc.currentUnit(angle = _arg)

def frameRate_get():
    _str_func = 'frameRate_get'
    log.debug(cgmGEN.logString_start(_str_func))    
    return mc.currentUnit(q=1, time=True)    

def frameRate_set(arg, fixFractionalSlider = True):
    _str_func = 'frameRate_set'
    log.debug(cgmGEN.logString_start(_str_func))
    
    if VALID.valueArg(arg):
        _arg = '{0}fps'.format(arg)
        
    else:
        d_validArgs = {'ntsc':['n','ntsc'],
                       'pal':['p','pal'],
                       'film':['f', 'film'],
                       'game':['g','game'],
                       'ntscf':['ntscf']
                       }
        
        _arg = VALID.kw_fromDict(arg,d_validArgs, calledFrom=_str_func,noneValid=True)
    
    if not _arg:
        _arg=arg
    
    log.debug(cgmGEN.logString_msg(_str_func,"| arg: {0} | validated: {1}".format(arg,_arg)))

    mc.currentUnit(time = _arg)
    
    if fixFractionalSlider:
        log.debug(cgmGEN.logString_msg(_str_func,'fixFractionalSlider...'))        
        _current = mc.currentTime(q=True)
        mc.playbackOptions(animationStartTime= int(mc.playbackOptions(q=True,animationStartTime=True)),
                           animationEndTime= int(mc.playbackOptions(q=True,animationEndTime=True)),
                           max =int(mc.playbackOptions(q=True,max=True)),
                           min =int(mc.playbackOptions(q=True,min=True)),
                           )
        mc.currentTime(int(_current))
    
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
    return mc.keyTangent(q = 1, g=1, itt = True, ott = True)  

def defaultInTangent_set(arg):
    return defaultTangents_set(arg,True,False)
def defaultOutTangent_set(arg):
    return defaultTangents_set(arg,False,True)

def defaultInTangent_get():
    return mc.keyTangent(q = 1, g=1, itt = True, ott = True)[0]
def defaultOutTangent_get():
    return mc.keyTangent(q = 1, g=1, itt = True, ott = True)[1]  

def defaultTangents_set(arg, inTangent=True,outTangent=True):
    _str_func = 'defaultTangents_set'
    log.debug(cgmGEN.logString_start(_str_func))
    
    d_validArgs = {'linear':['ln','linear'],
                   'spline':['sp','spline'],
                   'clamped':['cl','clamped'],
                   'flat':['fl','flat'],
                   'step':['st','step','stepped'],
                   'plateau':['pl','plateau'],
                   'auto':['au','auto']
                   }
    _arg = VALID.kw_fromDict(arg,d_validArgs, calledFrom=_str_func)
    
    log.debug(cgmGEN.logString_msg(_str_func,"| arg: {0} | validated: {1}".format(arg,_arg)))
    
    #Couldn't use True for setting the Tangent type had to use _arg
    
    _d = {'g':1}
    if inTangent:
        _d['itt']= _arg
    if outTangent:
        _d['ott'] = _arg
        
    if inTangent and _arg == 'step':
        _d['itt'] = 'flat'
        
    mc.keyTangent(**_d)
    
def weightedTangents_get():
    _str_func = 'weightedTangents_get'
    log.debug(cgmGEN.logString_start(_str_func))    
    return mc.keyTangent(q = 1, wt = bool(True))    
    
def weightedTangets_set(arg):
    _str_func = 'weightedTangets_set'
    log.debug(cgmGEN.logString_start(_str_func))
    
    mc.keyTangent(edit = 1, g = 1, wt = bool(arg))