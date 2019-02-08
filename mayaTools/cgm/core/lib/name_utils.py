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
    try:obj = obj.mNode
    except:pass
    
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
short = get_short
def get_long(obj = None):
    """
    Return the long name of an object
    
    :parameters:
        obj(str): Object to return a name for

    :returns
        short name(str)
    """   
    try:obj = obj.mNode
    except:pass    
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
long = get_long

def get_base(obj = None):
    """
    Return the base name of an object. Base being without any '|' or what not
    
    :parameters:
        obj(str): Object to return a name for

    :returns
        short name(str)
    """   
    try:obj = obj.mNode
    except:pass    
    _str_func = "get_base('{0}')".format(obj)
    
    return obj.split('|')[-1].split(':')[-1]
    
    buffer = mc.ls(obj,l=True)      
    
    if buffer:
        if len(buffer) == 1:
            return buffer[0].split('|')[-1].split(':')[-1]
        log.error("Too many objects named '{0}' (Be more specific): ".format(obj))
        for i,o in enumerate(buffer):
            log.error(" "*4 + "{0}:'{1}'".format(i,o))
        raise ValueError,"{0} || More than one object with name".format(_str_func)
    raise ValueError("{0} || No object exists!".format(_str_func)) 
base = get_base


def get_refPrefix(node = None):
    """
    Return reference prefix if a node has one
    
    :parameters:
        obj(str): Object to return a name for

    :returns
        short name(str)
    """   
    try:node = node.mNode
    except:pass    
    _str_func = "get_refPrefix('{0}')".format(node)
    if mc.referenceQuery(node, isNodeReferenced=True) == True:
        splitBuffer = node.split(':')
        return (':'.join(splitBuffer[:-1]))
    return False

    
d_functionStringSwaps = {'.':'_attr_', ' ':'',',':'_',
                         '+':'_add_','-':'_minus_','><':'_avg_',#pma                                                 
                         '==':'_isEqualTo_','!=':'_isNotEqualTo_','>':'_isGreaterThan_','>=':'_isGreaterOrEqualTo_','<':'_isLessThan_','<=':'_isLessThanOrEqualTo_',#condition
                         '*':'_multBy_','/':'_divBy_','^':'_pow_',}

def clean(arg = None,invalidChars = """`~!@#$%^&*()-+=[]\\{}|;':"/?><., """, noNumberStart = True,
          functionSwap = False, replaceChar = '', cleanDoubles = True, stripTailing=True):
    """
    Modified from Hamish MacKenzie's zoo one

    :parameters:
    arg(str) - String to clean
    invalidChars(str) - Sequence of characters to remove
    	noNumberStart(bool) - remove numbers at start
    	functionSwap(bool) - whether to replace functions with string from dict
    	replaceChar(str) - Character to use to replace with
    	cleanDoubles(bool) - remove doubles
    	stripTrailing(bool) - remove trailing '_'

    returns l_pos
    """
    _str_funcName = 'clean'
    try:
        str_Clean = arg

        for char in invalidChars:
            if functionSwap and char in d_functionStringSwaps.keys():
                str_Clean = str_Clean.replace( char, d_functionStringSwaps.get(char) )
            else:
                str_Clean = str_Clean.replace( char, replaceChar )

        if noNumberStart:
            for n in range(10):		
                while str_Clean.startswith( str(n) ):
                    log.debug("Cleaning : %s"%str(n))
                    str_Clean = str_Clean[ 1: ]	
        if cleanDoubles and replaceChar:
            doubleChar = replaceChar + replaceChar
            while doubleChar in cleanStr:
                str_Clean = str_Clean.replace( doubleChar, replaceChar )

        if stripTailing:
            while str_Clean.endswith( '_' ):
                str_Clean = str_Clean[ :-1 ]
        return str_Clean		
    except Exception,err:
        cgmGeneral.cgmExceptCB(Exception,err,msg=vars())
