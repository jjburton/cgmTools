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
                   'mm':['milimeter','mili']}
    _arg = VALID.kw_fromDict(arg,d_validArgs, calledFrom=_str_func)
    
    log.debug(cgmGEN.logString_msg(_str_func,"| arg: {0} | validated: {1}".format(arg,_arg)))

    mc.currentUnit(linear = _arg)
    
    '''
    if arg == "millimeter" :
        mc.currentUnit(linear = "mm")
        print "Working units set to " + units
    elif units == "centimeter" :
        mc.currentUnit(linear = "cm")
        print "Working units set to " + units
    elif units == "meter" :
        mc.currentUnit(linear = "m")
        print "Working units set to " + units
    elif units == "yard" :
        mc.currentUnit(linear = "yd")
        print "Working units set to " + units
    elif units == "inch" :
        mc.currentUnit(linear = "in")
        print "Working units set to " + units
    elif units == "foot" :
        mc.currentUnit(linear = "ft")
        print "Working units set to " + units
    else :
        print "!!! Please choose either:" +'\n' + "millimeter, centimeter, meter, yard, inch, or foot !!!!"
        '''


    
