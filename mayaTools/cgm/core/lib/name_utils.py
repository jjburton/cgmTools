"""
name_utils
Josh Burton 
www.cgmonks.com

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

# From cgm ==============================================================
from cgm.core import cgm_General as cgmGeneral
#NO IMPORT: VALID

#>>> Utilities
#===================================================================
def get_short(obj = None):
    """
    Return the short name of an object
    
    :parameters:
        obj(str): Object to return a name for

    :returns
        short name(str)
    """   
    _str_func = "get_short('{0}')".format(obj)
            
    buffer = mc.ls(obj,shortNames=True) 
    if buffer:
        if len(buffer) == 1:
            return buffer[0]
        log.error("Too many objects named '{0}' (Be more specific): ".format(obj))
        for i,o in enumerate(buffer):
            log.error(" "*4 + "{0}:'{1}'".format(i,o))
        raise ValueError,"{0} || More than one object with name".format(_str_func)
    raise ValueError("{0} || No object exists!".format(_str_func))

def get_long(obj = None):
    """
    Return the long name of an object
    
    :parameters:
        obj(str): Object to return a name for

    :returns
        short name(str)
    """   
    _str_func = "get_long('{0}')".format(obj)
    
    buffer = mc.ls(obj,l=True)        
    if buffer:
        if len(buffer) == 1:
            return buffer[0]
        log.error("Too many objects named '{0}' (Be more specific): ".format(obj))
        for i,o in enumerate(buffer):
            log.error(" "*4 + "{0}:'{1}'".format(i,o))
        raise ValueError,"{0} || More than one object with name".format(_str_func)
    raise ValueError("{0} || No object exists!".format(_str_func))

def get_base(obj = None):
    """
    Return the base name of an object. Base being without any '|' or what not
    
    :parameters:
        obj(str): Object to return a name for

    :returns
        short name(str)
    """   
    _str_func = "get_base('{0}')".format(obj)
    buffer = mc.ls(obj,l=True)      
    
    if buffer:
        if len(buffer) == 1:
            return buffer[0].split('|')[-1].split(':')[-1]
        log.error("Too many objects named '{0}' (Be more specific): ".format(obj))
        for i,o in enumerate(buffer):
            log.error(" "*4 + "{0}:'{1}'".format(i,o))
        raise ValueError,"{0} || More than one object with name".format(_str_func)
    raise ValueError("{0} || No object exists!".format(_str_func)) 


