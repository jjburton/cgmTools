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
class clsFunc(object):
    """Simple class for use with TimerSimple"""	    
    def __init__(self,*args, **kws):
        self._str_funcClass = None
	self._str_funcCombined = None
        self._str_funcName = None
        self._str_funcDebug = None
	self.d_kwsDefined  = {}
	self.l_funcSteps = []
	self.d_return = {}
	self._str_modPath = None
	self._str_mod = None	
    
    def __dataBind__(self,*args,**kws):
	try:self._d_funcArgs = args
	except:self._d_funcArgs = {}
	try:self._d_funcKWs = kws
	except:self._d_funcKWs = {}	
	try:self._str_funcArgs = "%s"%args
	except:self._str_funcArgs = None
	try:self._str_funcKWs = "%s"%kws
	except:self._str_funcKWs = None
        try:
            mod = inspect.getmodule(self)
	    self._str_modPath = inspect.getmodule(self)
            self._str_mod = '%s' % mod.__name__.split('.')[-1]
	    self._str_funcCombined = "%s.%s"%(self._str_mod,self._str_funcName)
        except:self._str_funcCombined = self._str_funcName
	self._str_reportStart = " %s >> "%(self._str_funcName)
	
    def __func__(self,*args,**kws):
	raise StandardError,"%s No function set"%self._str_reportStart

    def go(self,goTo = '',**kws):
	"""
	"""
	t_start = time.clock()
	try:
	    if not self.l_funcSteps: l_funcSteps = [{'call':self.__func__}]
	    else: l_funcSteps = self.l_funcSteps
	    int_keys = range(0,len(l_funcSteps)-1)
	    int_max = len(l_funcSteps)-1
	except Exception,error:
	    raise StandardError, ">"*3 + " %s >!FAILURE!> go start | Error: %s"%(self._str_funcCombined,error)
	
	for i,d_step in enumerate(l_funcSteps):
	    t1 = time.clock()	    
	    try:	
		_str_step = d_step.get('step') or self._str_funcName
		res = d_step['call']()
		if res is not None:
		    self.d_return[_str_step] = res
		"""
		if goTo.lower() == str_name:
		    log.debug("%s.doBuild >> Stopped at step : %s"%(self._strShortName,str_name))
		    break"""
	    except Exception,error:
		log.error(">"*3 + " %s "%self._str_funcCombined + "="*75)
		log.error(">"*3 + " Module: %s "%self._str_modPath)	    		    
		if self._str_funcArgs:log.error(">"*3 + " Args: %s "%self._str_funcArgs)
		if self._str_funcKWs:log.error(">"*3 + " KWs: %s "%self._str_funcKWs)	 
		if self.d_kwsDefined:
		    for k in self.d_kwsDefined.keys():
			log.error(">"*3 + " '%s' : %s "%(k,self.d_kwsDefined[k]))		
		_str_fail = ">"*3 + " %s >!FAILURE!> Step: '%s' | Error: %s"%(self._str_funcCombined,_str_step,error)
		log.error(_str_fail)
		log.error("%s >> Fail Time >> = %0.3f seconds " % (self._str_funcCombined,(time.clock()-t1)) + "-"*75)
		self.d_return[_str_step] = None	
		raise StandardError, _str_fail
	    t2 = time.clock()
	    if int_max != 0: log.info("%s | '%s' >> Time >> = %0.3f seconds " % (self._str_funcCombined,_str_step,(t2-t1)) + "-"*75)		
	
	log.info("%s >> Complete Time >> = %0.3f seconds " % (self._str_funcCombined,(time.clock()-t_start)) + "-"*75)		
	if int_max == 0:#If it's a one step, return, return the single return
	    try:return self.d_return[self.d_return.keys()[0]]
	    except:pass
	return self.d_return
    
    def report(self):
	log.info(">"*3 + " %s "%self._str_funcCombined + "="*75)
	log.info(">"*3 + " Module: %s "%self._str_modPath)	
	log.info(">"*3 + " l_funcSteps: %s "%self.l_funcSteps)	    			
	if self._str_funcArgs:log.info(">"*3 + " Args: %s "%self._str_funcArgs)
	if self._str_funcKWs:log.info(">"*3 + " KWs: %s "%self._str_funcKWs)	  
	if self.d_kwsDefined:
	    log.info(">"*3 + " KWs Defined " + "-"*75)	  	    
	    for k in self.d_kwsDefined.keys():
		log.info(">"*3 + " '%s' : %s "%(k,self.d_kwsDefined[k]))
	if self.l_funcSteps:
	    log.info(">"*3 + " Steps " + "-"*75)	  	    
	    for i,d in enumerate(l_funcSteps):
		try:log.info(">"*3 + " '%s' : %s "%(i,d.get('step')))
		except:pass
	log.info("#" + "-" *100)
		
class cgmFunctionClass2(object):
    """Simple class for use with TimerSimple"""
    def __init__(self,*args, **kws):
        self._str_funcClass = 'Default cgmFunctionClass'	
        self._str_funcName = 'Default func'
        self._str_funcStep = 'Default sub'
        self._str_funcDebug = 'Default debug'
	try:self._str_funcArgs = "%s"%args
	except:self._str_funcArgs = None
	try:self._str_funcKWs = "%s"%kws
	except:self._str_funcKWs = None

"""
example subFunctionClass(object)
class sampleClass(cgmFunctionClass):
    def __init__(self,*args, **kws):
        super(sampleClass, self).__init__(*args, **kws)
"""
        
        
def funcClassWrap(funcClass):
    '''
    Simple timer decorator 
    -- Taken from red9 and modified. Orignal props to our pal Mark Jackson
    '''        
    def wrapper( *args, **kws):
	#Data Gather
        _str_funcName = 'No Func found'
        try:_str_funcName = args[0]._str_funcName
        except Exception,error:log.info(error)

        t1 = time.clock()
        try:res=funcClass(*args,**kws) 
        except Exception,error:
	    log.info(">"*3 + " %s "%_str_funcName + "="*75)	    
	    log.error(">"*3 + " Step: %s "%args[0]._str_funcStep)	    
	    log.error(">"*3 + " Args: %s "%args[0]._str_funcArgs)
	    log.error(">"*3 + " KWs: %s "%args[0]._str_funcKWs)	    
	    log.info("%s >> Time to Fail >> = %0.3f seconds " % (_str_funcName,(time.clock()-t1)) + "-"*75)			    
	    raise error            
        t2 = time.clock()
	
	#Initial print
	log.info(">"*3 + " %s "%_str_funcName + "="*75)
	log.info(">"*3 + " Args: %s "%args[0]._str_funcArgs)
	log.info(">"*3 + " KWs: %s "%args[0]._str_funcKWs)		
		    
	log.info("%s >> Time >> = %0.3f seconds " % (_str_funcName,(t2-t1)) + "-"*75)		
        return res
    return wrapper  

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
                str_arg = args[0].p_nameShort
            except:
                log.debug("arg[0] failed to call: %s"%args[0])
            functionTrace+='%s.' % str_first
        except StandardError,error:
            log.debug('function class inspect failure: %s'%error)
        functionTrace+=func.__name__ 
        if str_arg:functionTrace+='(%s)'%str_arg      
        log.info('>'*3 + ' TIMER : %s: %0.4f sec ' % (functionTrace,(t2-t1))+ '<'*3)
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
        log.debug('DEBUG TIMER : %s: %0.4f sec' % (functionTrace,(t2-t1)))
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