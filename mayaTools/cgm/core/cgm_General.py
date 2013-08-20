"""
------------------------------------------
cgm_Meta: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com

Website : http://www.cgmonks.com
------------------------------------------

This is the Core of the MetaNode implementation of the systems.
It is uses Mark Jackson (Red 9)'s as a base.
================================================================
"""
import maya.cmds as mc
import maya.mel as mel
import copy
import time
import inspect
import sys

# From Red9 =============================================================

# From cgm ==============================================================
from cgm.lib import search
# Shared Defaults ========================================================

#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   
# cgmMeta - MetaClass factory for figuring out what to do with what's passed to it
#=========================================================================    
def Timer(func):
    '''
    Simple timer decorator 
    -- Taken from red9 and modified. Orignal props to our pal Mark Jackson
    '''

    def wrapper( *args, **kws):
        t1 = time.time()
        res=func(*args,**kws) 
        t2 = time.time()

        functionTrace=''
        str_arg = False
        try:
            #module if found
            mod = inspect.getmodule(args[0])
            #log.debug("mod: %s"%mod)            
            functionTrace+='%s >> ' % mod.__name__.split('.')[-1]
        except:
            log.debug('function module inspect failure')
        try:
            #class function is part of, if found
            cls = args[0].__class__
            #log.debug("cls: %s"%cls)
            #log.debug("arg[0]: %s"%args[0])
            if type(args[0]) in [str,unicode]:
                str_first = args[0]
            else:
                str_first = args[0].__class__.__name__  
                
            try:
                log.debug("args]0] : %s"%args[0])                
                if args[0].p_nameShort:
                    str_arg = args[0].p_nameShort
            except:
                log.debug("arg[0] failed to call: %s"%args[0])
            functionTrace+='%s.' % str_first
        except StandardError,error:
            log.debug('function class inspect failure: %s'%error)
        functionTrace+=func.__name__ 
        if str_arg:functionTrace+='(%s)'%str_arg      
        log.info('>'*5 + ' TIMER : %s: %0.4f sec ' % (functionTrace,(t2-t1))+ '<'*5)
        #log.debug('%s: took %0.3f ms' % (func.func_name, (t2-t1)*1000.0))
        return res
    return wrapper  

def TimerDebug(func):
    '''
    Variation,only outputs on debug
    -- Taken from red9 and modified. Orignal props to our pal Mark Jackson
    '''
    def wrapper( *args, **kws):
        t1 = time.time()
        res=func(*args,**kws) 
        t2 = time.time()

        functionTrace=''
        try:
            #module if found
            mod = inspect.getmodule(args[0])
            functionTrace+='%s >>' % mod.__name__.split('.')[-1]
        except:
            log.debug('function module inspect failure')
        try:
            #class function is part of, if found
            cls = args[0].__class__
            functionTrace+='%s.' % args[0].__class__.__name__
        except:
            log.debug('function class inspect failure')
        functionTrace+=func.__name__ 
        log.debug('TIMER : %s: %0.4f sec' % (functionTrace,(t2-t1)))
        #log.debug('%s: took %0.3f ms' % (func.func_name, (t2-t1)*1000.0))
        return res
    return wrapper


def doStartMayaProgressBar(stepMaxValue = 100, statusMessage = 'Calculating....',interruptableState = True):
    """
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    DESCRIPTION:
    Tools to do a maya progress bar. This function and doEndMayaProgressBar are a part of a set. Example
    usage:

    mayaMainProgressBar = guiFactory.doStartMayaProgressBar(int(number))
    for n in range(int(number)):
    if mc.progressBar(mayaMainProgressBar, query=True, isCancelled=True ) :
    break
    mc.progressBar(mayaMainProgressBar, edit=True, status = (n), step=1)

    guiFactory.doEndMayaProgressBar(mayaMainProgressBar)

    ARGUMENTS:
    stepMaxValue(int) - max number of steps (defualt -  100)
    statusMessage(string) - starting status message
    interruptableState(bool) - is it interuptible or not (default - True)

    RETURNS:
    mayaMainProgressBar(string)
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    """
    mayaMainProgressBar = mel.eval('$tmp = $gMainProgressBar');
    mc.progressBar( mayaMainProgressBar,
                    edit=True,
                    beginProgress=True,
                    isInterruptable=interruptableState,
                    status=statusMessage,
                    minValue = 0,
                    maxValue= stepMaxValue )
    return mayaMainProgressBar

def doEndMayaProgressBar(mayaMainProgressBar):
    mc.progressBar(mayaMainProgressBar, edit=True, endProgress=True)
    
#>>> Validation ============================================================== 
def validateString(arg = None,noneValid = True):
    """
    Simple string validation
    """
    log.debug(">>> validateString >> arg = %s"%arg + "="*75)   
    if type(arg) in [str,unicode]:
	return arg
    elif noneValid:
	return False
    else: raise StandardError, ">>> validateString >> Arg failed: arg = %s | type: %s"%(arg,type(arg))
    
def validateBool(arg = None, calledFrom = None):
    """
    Bool validation
    """
    log.debug(">>> validateBool >> arg = %s"%arg + "="*75)   
    calledFrom = validateString(calledFrom,noneValid=True)
    if calledFrom: _str_funcName = "%s.validateObjArg(%s)"%(calledFrom,arg)
    else:_str_funcName = "validateBool(%s)"%arg
    
    if type(arg) is bool:
	return arg
    elif type(arg) is int and arg in [0,1]:
	return bool(arg)
    else: raise StandardError, ">>> %s >> Arg failed"%(_str_funcName)
	
def validateObjArg(arg = None, mayaType = None, noneValid = False, calledFrom = None):
    """
    validate an objArg. Use cgmMeta version for instances
    
    arg -- obj or instance
    mayaType -- maya type to validate to
    noneValid -- whether none is a valid arg
    """
    log.debug(">>> validateObjListArg >> arg = %s"%arg + "="*75)
    
    calledFrom = validateString(calledFrom,noneValid=True)
    if calledFrom: _str_funcName = "%s.validateObjArg(%s)"%(calledFrom,arg)
    else:_str_funcName = "validateObjArg(%s)"%arg
    
    if len(mc.ls(arg)) > 1:
	raise StandardError,"More than one object named %s"%arg
    try:
	argType = type(arg)
	if argType in [list,tuple]:#make sure it's not a list
	    if len(arg) ==1:
		arg = arg[0]
	    elif arg == []:
		arg = None
	    else:
		raise StandardError,"%s >>> arg cannot be list or tuple"%_str_funcName	
	if not noneValid:
	    if arg in [None,False]:
		raise StandardError,"%s >>> arg cannot be None"%_str_funcName
	else:
	    if arg in [None,False]:
		if arg not in [None,False]:log.warning("%s >>> arg fail"%_str_funcName)
		return False
			
	if not mc.objExists(arg):
	    if noneValid: return False
	    else:
		raise StandardError,"%s>>> Doesn't exist: '%s'"%(_str_funcName,arg)
			
	if mayaType is not None and len(mayaType):
	    if type(mayaType) not in [tuple,list]:l_mayaTypes = [mayaType]
	    else: l_mayaTypes = mayaType	    
	    str_type = search.returnObjectType(arg)
	    if str_type not in l_mayaTypes:
		if noneValid:
		    log.warning("%s >>> '%s' Not correct mayaType: mayaType: '%s' != currentType: '%s'"%(_str_funcName,arg,str_type,l_mayaTypes))
		    return False
		raise StandardError,"%s >>> '%s' Not correct mayaType: mayaType: '%s' != currentType: '%s'"%(_str_funcName,arg,str_type,l_mayaTypes)			    	
	return arg
    
    except StandardError,error:
	log.error("%s >>Failure! arg: %s | mayaType: %s"%(_str_funcName,arg,mayaType))
	raise StandardError,error  
    
def validateObjListArg(l_args = None, mayaType = None, noneValid = False,calledFrom = None):
    log.debug(">>> validateObjListArg >> l_args = %s"%l_args + "="*75) 
    calledFrom = validateString(calledFrom,noneValid=True)    
    if calledFrom: _str_funcName = "%s.validateObjArg"%(calledFrom)
    else:_str_funcName = "validateObjArg"    
    try:
	if type(l_args) not in [list,tuple]:l_args = [l_args]
	returnList = []
	for arg in l_args:
	    buffer = validateObjArg(arg,mayaType,noneValid,calledFrom)
	    if buffer:returnList.append(buffer)
	    else:log.warning("%s >> failed: '%s'"%(_str_funcName,arg))
	return returnList
    except StandardError,error:
	log.error("%s >>Failure! l_args: %s | mayaType: %s"%(_str_funcName,l_args,mayaType))
	raise StandardError,error    