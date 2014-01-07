"""
------------------------------------------
cgm_General: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

This is for general purpose python code. The most important of which is cgmFuncCls - the core function class of the cgm created toolkit

#Sample cgmFuncCls
from cgm.core import cgm_General as cgmGeneral
def testFunc(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
    	def __init__(self,*args, **kws):
    	    super(fncWrap, self).__init__(*args, **kws)
    	    self._str_funcName = 'testFunc'	
    	    self.int_test = 10000
    	    #self._b_autoProgressBar = 1
	    #self._b_reportTimes = 1
    	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'stringTest',"default":None}]	    
    	    self.__dataBind__(*args, **kws)
    	    self.l_funcSteps = [{'step':'Our first step','call':self.testSubFunc},
    	                        {'step':'Pass two','call':self.testSubFunc2},
    	                        {'step':'Pass progressBar set','call':self.testProgressBarSet},
    	                        {'step':'Pass progressBar iter','call':self.testProgressBarIter}]
    	def testSubFunc(self):
    	    self.log_info(self.d_kws['stringTest'])
    	    self.d_test = {"maya":"yay!"}
    	    for i in range(50):
    	        self.log_warning(i)
    	def testSubFunc2(self):
    	    self.log_infoNestedDict('d_test')
    	    #raise StandardError, "Sopped"
    	def testProgressBarSet(self):
    	   for i in range(self.int_test):
    	       self.progressBar_set(status = ("Getting: '%s'"%i), progress = i, maxValue = self.int_test)
    	def testProgressBarIter(self):
    	   self.progressBar_setMaxStepValue(self.int_test)
    	   for i in range(self.int_test):
    	       self.progressBar_iter(status = ("Getting: '%s'"%i))
    return fncWrap(*args, **kws).go()
reload(cgmGeneral)
testFunc()
testFunc(printHelp = True)#Let's you see a break down of the arg/kws of a function
testFunc(reportTimes = True,reportEnv = True)#Here we wanna see the enviornment report as well
testFunc(reportTimes = True)#Show times for steps of functions
testFunc(reportShow = True)#Show a report of a function before running it
testFunc(autoProgressBar = True)#automatically generate a progress bar of the steps of a function

#Example code
'''
try:#Name ===============================================================================
    try:#Sub ===============================================================================		
    except Exception,error:raise StandardError, "%s | %s"%('a',error)
except Exception,error:raise StandardError, "[Name]{%s}"%(error)
'''
================================================================
"""
import maya.cmds as mc
import maya.mel as mel
import maya.utils as mUtils
import copy
import time
import inspect
import platform
import sys
import traceback
import linecache

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
_str_subLine = '-'*75
_str_hardLine = '='*75
_str_hardBreak = '=' * 100
_str_headerDiv = '///'
_str_baseStart = "--"
class cgmFuncCls(object):  
    """
    Examples:
    self._l_ARGS_KWS_DEFAULTS = [{'kw':'kwString',"default":None,'help':"FillINToHelp","argType":"mObject"}
				 {'kw':'targetSurface',"default":None},
				 {'kw':"createControlLoc","default":True},
				 {'kw':"createUpLoc","default":False},
				 {'kw':"parentToFollowGroup","default":False},	                  
				 {'kw':'f_offset',"default":1.0},
				 {'kw':'orientation',"default":'zyx'}]
				 
    Don't:
    -- append to self._l_ARGS_KWS_DEFAULTS -- causes pass through issues with *args
    """
    def __init__(self,*args, **kws):
        self._str_funcClass = None
	self._str_funcCombined = None
        self._str_funcName = None
        self._str_funcHelp = None	
	self._str_progressBar = None
        self._str_funcDebug = None
	self._b_WIP = False
	self._b_autoProgressBar = False
	self._b_reportTimes = False
	self._b_pushCleanKWs = False
	self._l_ARGS_KWS_DEFAULTS = []
	self._l_ARGS_KWS_BUILTINS = [{'kw':'reportShow',"default":False,'help':"show report at start of log","argType":"bool"},
	                             {'kw':'reportTimes',"default":False,'help':"show step times in log","argType":"bool"},
	                             {'kw':'reportEnv',"default":False,'help':"Override. Just get maya env info","argType":"bool"},
	                             {'kw':'reportToDo',"default":False,'help':"Override. Get to do list for func","argType":"bool"},	                                 
	                             {'kw':'printHelp',"default":False,'help':"Override.  Get help block for func","argType":"bool"},
	                             {'kw':'setLogLevel',"default":None,'help':"Set the debug level on call","argType":"str"},
	                             {'kw':'autoProgressBar',"default":False,'help':"Show generated progress bar by steps","argType":"bool"}]	
	self.d_kws  = {}
	self.l_funcSteps = []
	self.d_return = {}
	self._str_modPath = None
	self._str_mod = None	
	self._l_funcTimes = []
	self._l_toDo = []
	self._l_errors = []
	self._l_warnings = []
	#These are our mask so that the fail report ignores them
	self._l_reportMask = ['_b_pushCleanKWs','_l_ARGS_KWS_BUILTINS','_l_toDo','_l_warnings','_l_errors','_str_step','int_max','_Exception','_ExceptionError','_str_failStep','_str_failTime','_str_modPath','_go','l_funcSteps','_str_funcHelp','d_return','_str_funcDebug','_str_funcKWs','_l_reportMask','_l_errorMask',
	                      '_b_autoProgressBar','_b_reportTimes','_str_progressBar','_str_progressBarReportStart',  
	                      '_str_funcClass','_str_funcName','d_kws','_str_funcCombined','_l_funcArgs','_b_WIP','_l_funcTimes','_l_ARGS_KWS_DEFAULTS',
	                      '_str_mod','mod','_str_funcArgs','_d_funcKWs','_str_reportStart','_str_headerDiv','_str_subLine','_str_hardLine']  

	#List of kws to ignore when a function wants to use kws for special purposes in the function call -- like attr:value
	#self._l_kwMask = ['reportTimes','reportShow','autoProgressBar']
	
    def __updateFuncStrings__(self):
	self._str_funcCombined = self._str_funcName
	try:self._str_funcName = "%s - from %s"%(self._str_funcName,kws['calledFrom'])
	except:pass
	self._str_progressBarReportStart = self._str_funcCombined
	self._str_reportStart = " %s >> "%(self._str_funcName)
	
    def __dataBind__(self,*args,**kws):
	try:self._l_funcArgs = args
	except:self._l_funcArgs = []
	try:self._d_funcKWs = kws
	except:self._d_funcKWs = {}	
	try:self._str_funcArgs = str(args)
	except:self._str_funcArgs = None
	try:self._str_funcKWs = str(kws)
	except:self._str_funcKWs = None
	
	self.__updateFuncStrings__()
		
	#KW/ARG handling
	#Built our data sets
	#self.log_infoNestedDict('d_kws')
	if self._l_ARGS_KWS_DEFAULTS:
	    l_argCull = copy.copy(list(args))
	    int_argIdx = 0	    
	    for i,d_buffer in enumerate(self._l_ARGS_KWS_DEFAULTS + self._l_ARGS_KWS_BUILTINS):
		str_kw = d_buffer['kw']		
		#self.log_info("Checking: [%s] | args: %s | l_argsCull: %s"%(str_kw,args,l_argCull))
		l_argCull = copy.copy(list(args))
		if not self._d_funcKWs.has_key(str_kw):
		    try:
			self.d_kws[str_kw] = kws[str_kw]#Then we try a kw call
		    except:
			try:
			    self.d_kws[d_buffer['kw']] = args[ int_argIdx ]#First we try the arg index			
			except:
			    #self.log_info("Using default [%s] = %s"%(str_kw,d_buffer.get("default")))
			    self.d_kws[str_kw] = d_buffer.get("default")#Lastly, we use the default value
		else:
		    self.d_kws[str_kw] = self._d_funcKWs[str_kw]
		    int_argIdx -=1 #We'll be keep pushing down the arg start as we find kws
		    #self.log_info("Has key [%s] = %s | New argIdx: %s "%(str_kw,self._d_funcKWs[str_kw],int_argIdx +1))
		int_argIdx +=1
		
	l_storedKeys = self.d_kws.keys()
	for kw in kws:
	    try:
		if kw not in l_storedKeys:self.d_kws[kw] = kws[kw]
	    except Exception,error:raise StandardError,"%s failed to store kw: %s | value: %s | error: %s"%(self._str_reportStart,kw,kws[kw],error)
	'''
	self._l_ARGS_KWS_BUILTINS = [{'kw':'reportShow',"default":False,'help':"(BUILTIN) - show report at start of log","argType":"bool"},
	                             {'kw':'reportTimes',"default":False,'help':"(BUILTIN) - show step times in log","argType":"bool"},
	                             {'kw':'reportEnv',"default":False,'help':"(BUILTIN) - Override. Just get maya env info","argType":"bool"},
	                             {'kw':'reportToDo',"default":False,'help':"(BUILTIN) - Override. Get to do list for func","argType":"bool"},	                                 
	                             {'kw':'printHelp',"default":False,'help':"(BUILTIN) - Override.  Get help block for func","argType":"bool"},
	                             {'kw':'setLogLevel',"default":None,'help':"(BUILTIN) - Set the debug level on call","argType":"str"},
	                             {'kw':'autoProgressBar',"default":False,'help':"(BUILTIN) - show generated progress bar by steps","argType":"bool"}]
	'''    
	if self.d_kws.get('autoProgressBar'):self._b_autoProgressBar = True
	if self.d_kws.get('reportTimes'):self._b_reportTimes = True
		
    def __func__(self,*args,**kws):
	raise StandardError,"%s No function set"%self._str_reportStart
        
    def _ExceptionHook_(self, etype, value, tb, detail=2):
	# do something here...
	try:
	    if detail == 2:	    
		db_file = tb.tb_frame.f_code.co_filename
		self.report_base()
		self.log_info(_str_headerDiv + " Exception " + _str_headerDiv + _str_subLine)		
		self.log_info("Step: '%s'"%self._str_failStep)
		self.log_info("Time: %s sec"%self._str_failTime)
		if db_file != "<maya console>":
		    linecache.clearcache()		
		    lineno = tb.tb_lineno
		    line = linecache.getline(db_file, lineno)
		    self.log_info("Traceback File: %s"%db_file)
		    self.log_info("Line#: %d"%lineno)
		    self.log_info("Line: %s"%line)		
		self.log_info("Exception Type: %s"%etype)
		self.log_info("Exception value: %s"%value)
		#self.log_info("Traceback Obj: %s"%tb)
		#self.log_info("Detail: %s"%detail)		
		self.report_selfStored()
		self.report_warnings()		
		self.report_errors()
	    else:self.log_error("[Step: '%s' | time: %s]{%s}"%(self._str_failStep,self._str_failTime,self._ExceptionError))
	    if detail == 2:self.log_info(_str_hardBreak)
	    self.progressBar_end()
	    mUtils.formatGuiException = cgmExceptCB#Link back to our orignal overload
	    return cgmExceptCB(etype,value,tb,detail,True)
	    #return mUtils._formatGuiException(etype, value, tb, detail)	
	    #raise self._Exception,self._ExceptionError
	except Exception,error:
	    print("[%s._ExceptionHook_ Exception]{%s}"%(self._str_funcCombined,error))
	        
    def go(self,*args,**kws):
	"""
	"""
	self._Exception  = None
	self._ExceptionError = None
	
	if self.d_kws.get('printHelp'):
	    self.printHelp()
	    return   	
	
	if self.d_kws.get('setLogLevel'):
	    self.set_logging(self.d_kws.get('setLogLevel'))
	    
	t_start = time.clock()
	try:
	    if not self.l_funcSteps: self.l_funcSteps = [{'call':self.__func__}]
	    int_keys = range(0,len(self.l_funcSteps)-1)
	    self.int_max = len(self.l_funcSteps)-1
	except Exception,error:
	    raise StandardError, ">"*3 + " %s[FAILURE go start]{%s}"%(self._str_funcCombined,error)
	
	mc.undoInfo(openChunk=True)
	int_lenSteps = len(self.l_funcSteps)
	
	if self._b_pushCleanKWs:
	    log.debug("Pushing cleanKWs")
	    _d_cleanKWS = self.get_cleanKWS()
	    if kws:
		for k in _d_cleanKWS:kws[k] = _d_cleanKWS[k]
	    else:kws = _d_cleanKWS	
	    
	for i,d_step in enumerate(self.l_funcSteps):
	    t1 = time.clock()	    
	    try:
		_str_step = d_step.get('step') or False
		if _str_step:
		    self._str_progressBarReportStart = self._str_funcCombined + " %s "%_str_step
		else: _str_step = 'process'
		if self._b_autoProgressBar:self.progressBar_set(status = _str_step, progress = i, maxValue = int_lenSteps)
		
		self._str_step = _str_step	

		res = d_step['call'](*args,**kws)
		if res is not None:
		    self.d_return[_str_step] = res
		"""
		if goTo.lower() == str_name:
		    log.debug("%s.doBuild >> Stopped at step : %s"%(self._strShortName,str_name))
		    break"""
	    except Exception,error:
		#self._str_fail = "[Step: '%s' | time: %0.3f] > %s"%(_str_step,(time.clock()-t1),error)#stored the failed step string		
		self._str_failStep = _str_step
		self._str_failTime = "%0.3f"%(time.clock()-t1)
		self._Exception = Exception
		self._ExceptionError = error
		break
	    
	    t2 = time.clock()
	    _str_time = "%0.3f"%(t2-t1)
	    self._l_funcTimes.append([_str_step,_str_time])	
	self.progressBar_end()
	mc.undoInfo(closeChunk=True)	
	
	#Reporting and closing out =========================================================================
	if self._b_WIP or self.d_kws.get('reportShow'):
	    self.report()
	    
	if self.d_kws.get('reportToDo'):
	    self.report_toDo() 
		
	if self.d_kws.get('reportEnv'):
	    report_enviornment()   
	    
	if self._Exception is not None:
	    mUtils.formatGuiException = self._ExceptionHook_#Link our exception hook   	
	    self.update_moduleData()	    
	    raise self._Exception,"%s >> %s"%(self._str_funcCombined,str(self._ExceptionError))
	
	if self._b_reportTimes:
	    f_total = (time.clock()-t_start)	    
	    if int_lenSteps > 1:
		self.log_info(_str_headerDiv + " Times " + _str_headerDiv + _str_subLine)			    	    
		if self.int_max != 0:
		    for pair in self._l_funcTimes:
			self.log_info(" -- '%s' >>  %s " % (pair[0],pair[1]))				 
		self.log_warning(_str_headerDiv + " Total : %0.3f sec "%(f_total) + _str_headerDiv + _str_subLine)			    	    
	    else:self.log_warning("[Total = %0.3f sec] " % (f_total))
	    	    
	#mUtils.formatGuiException = cgmExceptCB#Link back to our orignal overload	
	return self._return_()
	
    def _return_(self):
	'''overloadable for special return'''
	if self.int_max == 0:#If it's a one step, return, return the single return
	    try:return self.d_return[self.d_return.keys()[0]]
	    except:pass
	    
	for k in self.d_return.keys():#Otherise we return the first one with actual data
	    buffer = self.d_return.get(k)
	    if buffer:
		return buffer
	if self.d_return:return self.d_return
	
    def report(self):
	self.update_moduleData()
	self.report_base()
	self.report_selfStored()
	if not self._b_reportTimes:self.report_steps()
		
    def report_base(self):
	self.update_moduleData()
	self.log_info("="*100)	
	self.log_info(_str_headerDiv + " %s "%self._str_funcCombined + _str_headerDiv + _str_hardLine)
	self.log_info("="*100)
	self.log_info(" Python Module: %s "%self._str_modPath)
	try:self.log_info(_str_baseStart + " Python Module Version: %s "%self.mod.__version__)
	except:pass		
	self.log_info(_str_headerDiv  + " ArgsKws " + _str_headerDiv + _str_subLine)		
	if self._str_funcArgs:self.log_info(" Args: %s"%self._str_funcArgs)
	if self._str_funcKWs:self.log_info(" KWs: %s"%self._str_funcKWs)	  
	if self.d_kws:
	    self.log_info(" Active Dict: "+_str_subLine)							    
	    l_keys = self.d_kws.keys()
	    l_keys.sort()	    
	    for k in l_keys:
		self.log_info(_str_baseStart *2 + "['%s'] = %s "%(k,self.d_kws[k]))
		
    def report_selfStored(self):
	l_keys = self.__dict__.keys()
	l_keys.sort()
	if l_keys:
	    self.log_info(_str_headerDiv + " Self Stored " + _str_headerDiv + _str_subLine)
	    for k in l_keys:
		if k not in self._l_reportMask:
		    buffer = self.__dict__[k]
		    if type(buffer) is dict:
			self.log_info("{'%s'}(nested) "%k)
			l_bufferKeys = buffer.keys()
			l_bufferKeys.sort()
			for k2 in buffer.keys():
			    self.log_info(_str_baseStart * 2 + "[%s] = %s "%(k2,buffer[k2]))			
		    else:
			self.log_info("['%s'] = %s "%(k,self.__dict__[k]))
		    
    def report_steps(self):	    
	if self.l_funcSteps:
	    self.log_info(_str_headerDiv + " Steps " + _str_headerDiv + _str_subLine)	  	    
	    for i,d in enumerate(self.l_funcSteps):
		try:self.log_info("'%s' : %s "%(i,d.get('step')))
		except:pass
		
    def report_toDo(self):	    
	if self._l_toDo:
	    self.log_info(_str_headerDiv + " To Do: " + _str_headerDiv + _str_subLine)	  	    
	    for i,d in enumerate(self._l_toDo):
		try:self.log_info(" -- %s : %s "%(i,d))
		except:pass    
		
    def report_errors(self):	    
	if self._l_errors:
	    self.log_info(_str_headerDiv + " Errors : " + _str_headerDiv + _str_subLine)	  	    
	    for i,d in enumerate(self._l_errors):
		try:self.log_info(" -- %s : %s "%(i,d))
		except:pass   
		
    def report_warnings(self):	    
	if self._l_warnings:
	    self.log_info(_str_headerDiv + " Warnings : " + _str_headerDiv + _str_subLine)	  	    
	    for i,d in enumerate(self._l_warnings):
		try:self.log_info(" -- %s : %s "%(i,d))
		except:pass    
		
    def report_argsKwsDefaults(self):
	if self._l_ARGS_KWS_DEFAULTS:
	    log.info(">"*3 + " Args/KWs/Defaults " + _str_subLine)	  	    	    
	    for i,d_buffer in enumerate(self._l_ARGS_KWS_DEFAULTS):
		l_tmp = [['Arg',i,]]
		try:l_tmp.append(['kw',"'%s'"%d_buffer.get('kw')])
		except:pass
		try:l_tmp.append(['default',d_buffer.get('default')])
		except:pass	
		try:l_tmp.append(['argType',d_buffer.get('argType')])
		except:pass		
		l_build = ["%s : %s"%(s[0],s[1]) for s in l_tmp]
		log.info(" | ".join(l_build))
	
	log.info(">"*3 + " Args/KWs/Defaults BUILTINS" + _str_subLine)	  	    	    
	for i,d_buffer in enumerate(self._l_ARGS_KWS_BUILTINS):
	    l_tmp = [['Arg',i,]]
	    try:l_tmp.append(['kw',"'%s'"%d_buffer.get('kw')])
	    except:pass
	    try:l_tmp.append(['default',d_buffer.get('default')])
	    except:pass	
	    try:l_tmp.append(['argType',d_buffer.get('argType')])
	    except:pass		
	    l_build = ["%s : %s"%(s[0],s[1]) for s in l_tmp]
	    log.info(" | ".join(l_build))	
    
    def printHelp(self):
	self.update_moduleData()		
	print("#" + ">"*3 + " %s "%self._str_funcCombined + "="*50)
	print("Python Module: %s "%self._str_modPath)	 
	print(_str_subLine * 2)		
	if self._str_funcHelp is not None:print("%s "%self._str_funcHelp)
	print(_str_subLine * 2)	
	print("@kws -- [index - argKW(argType - default) -- info]")
	for i,d_buffer in enumerate(self._l_ARGS_KWS_DEFAULTS + self._l_ARGS_KWS_BUILTINS):
	    l_tmp = ['%i - '%i]
	    if d_buffer in self._l_ARGS_KWS_BUILTINS:
		l_tmp.append("(BUILTIN) - ")
	    try:l_tmp.append("'%s'"%d_buffer['kw'])
	    except:pass
	    #arg default/type -------------------------------
	    l_buffer = ["("]
	    try:l_buffer.append("%s - "%(d_buffer['argType']))
	    except:pass			
	    try:l_buffer.append("%s"%(d_buffer['default']))
	    except:pass	
	    l_buffer.append(")")
	    l_tmp.append("".join(l_buffer))
	    #-------------------------------------------------
	    try:l_tmp.append(" -- %s"%d_buffer['help'])
	    except:pass		
	    #l_build = ["%s : %s"%(s[0],s[1]) for s in l_tmp]
	    print("".join(l_tmp))	
		
    def set_logging(self,arg):
	try:
	    d_logging = {'info':logging.INFO,
	                 'debug':logging.DEBUG}	    
	    str_key = str(arg).lower()
	    if str_key in d_logging.keys():
		log.setLevel(d_logging.get(str_key))
	    else:
		self.log_warning("Logging arg not understood : %s"%arg)
	except Exception,error:
	    self.log_warning("set_logging Exception: %s"%error)
	
    def log_info(self,arg):
	try:
	    #log.info("%s%s"%(self._str_reportStart,str(arg)))
	    print("%s%s"%(self._str_reportStart,str(arg)))
	except:pass	
	
    def log_todo(self,arg):
	try:
	    try:self._l_toDo.append("%s | %s"%(self._str_step,str(arg)))
	    except:self._l_toDo.append("%s"%(str(arg)))
	    #log.info("[TODO]%s%s"%(self._str_reportStart,str(arg)))
	    #print("[ERROR]%s%s"%(self._str_reportStart,str(arg)))	    
	except:pass
	
    def log_error(self,arg):
	try:
	    try:self._l_errors.append("%s | %s"%(self._str_step,str(arg)))
	    except:self._l_errors.append("%s"%(str(arg)))	    
	    log.error("%s%s"%(self._str_reportStart,str(arg)))
	    #print("[ERROR]%s%s"%(self._str_reportStart,str(arg)))	    
	except:pass
	
    def log_warning(self,arg):
	try:
	    try:self._l_warnings.append("%s | %s"%(self._str_step,str(arg)))
	    except:self._l_warnings.append("%s"%(str(arg)))	    
	    log.warning("%s%s"%(self._str_reportStart,str(arg)))
	    #print("[WARNING]%s%s"%(self._str_reportStart,str(arg)))	    
	except:pass	
    def log_debug(self,arg):
	try:
	    log.debug("[DEBUG]%s%s"%(self._str_reportStart,str(arg)))
	except:pass	
    #>>> Progress bar stuff =====================================================================
    def progressBar_start(self,stepMaxValue = 100, statusMessage = 'Calculating....',interruptableState = False):
	str_bfr = statusMessage
	statusMessage = "%s > %s"%(self._str_progressBarReportStart,str_bfr) 	
	self._str_progressBar = doStartMayaProgressBar(stepMaxValue, statusMessage, interruptableState)
	
    def progressBar_iter(self,**kws):
	if not self._str_progressBar:self.progressBar_start()
	if kws.get('status'):
	    str_bfr = kws.get('status')
	    kws['status'] = "%s > %s"%(self._str_progressBarReportStart,str_bfr) 
	if 'step' not in kws.keys():kws['step'] = 1
	if 'beginProgress' not in kws.keys():kws['beginProgress'] = 1
	kws['edit'] = 1
	mc.progressBar(self._str_progressBar, **kws)
	
    def progressBar_end(self,**kws):
	try:doEndMayaProgressBar(self._str_progressBar)
	except:pass	
    def progressBar_setMaxStepValue(self,int_value):
	if not self._str_progressBar:self.progressBar_start()
	try:mc.progressBar(self._str_progressBar,edit = True, progress = 0, maxValue = int_value)	
	except Exception,error:log.error("%s > failed to set progress bar maxValue | %s"%(self._str_reportStart,error))	
    def progressBar_setMinStepValue(self,int_value):
	if not self._str_progressBar:self.progressBar_start()	
	try:mc.progressBar(self._str_progressBar,edit = True, minValue = int_value)	
	except Exception,error:log.error("%s > failed to set progress bar minValue | %s"%(self._str_reportStart,error))	
    def progressBar_set(self,**kws):
	if not self._str_progressBar:self.progressBar_start()	
	if kws.get('status'):
	    str_bfr = kws.get('status')
	    kws['status'] = "%s > %s"%(self._str_progressBarReportStart,str_bfr) 
	if 'beginProgress' not in kws.keys():kws['beginProgress'] = 1
	try:mc.progressBar(self._str_progressBar,edit = True,**kws)	
	except Exception,error:log.error("%s > failed to set progress bar status | %s"%(self._str_reportStart,error))	
    
    def log_infoNestedDict(self,arg):
	try:
	    if type(arg) not in [list,tuple]:arg = [arg]
	    for atr in arg:
		try:
		    l_keys = self.__dict__[atr].keys()
		    log.info('%s'%self._str_funcCombined +" Self Stored: '%s' "%atr + _str_subLine)			    
		    l_keys.sort()
		    for k in l_keys:
			try:str_key = k.p_nameShort
			except:str_key = k
			buffer = self.__dict__[atr][k]
			if type(buffer) is dict:
			    self.log_info('%s '%self._str_funcCombined + ">" + " Nested Dict: '%s' "%(str_key) + _str_subLine)
			    l_bufferKeys = buffer.keys()
			    l_bufferKeys.sort()
			    for k2 in l_bufferKeys:
				self.log_info("-"*2 +'>' + " '%s' : %s "%(k2,buffer[k2]))			
			else:
			    self.log_info(">" + " '%s' : %s "%(str_key,self.__dict__[atr][k]))		    
		except Exception,error:
		    log.warning("Key not found or not dict: %s | %s"%(atr,error))
	except:pass
	
    def get_cleanKWS(self):
	"""
	Fuction to return the _d_funcKWS cleaned of all registered arg 'kws'. Useful for using kws as a pass through for other things
	"""
	try:
	    d_kws = copy.copy(self._d_funcKWs)
	    for arg in self._l_ARGS_KWS_DEFAULTS + self._l_ARGS_KWS_BUILTINS:
		str_key = arg['kw']
		if str_key in d_kws.keys():d_kws.pop(str_key)
	    self.log_debug("Clean kws : %s" %d_kws)
	    return d_kws
	except Exception, error:
	    log.error("[%s | func: get_cleanKWS]{%s}"%(self._str_funcName,error))
	    return {}
	
    def update_moduleData(self):
	try:
	    self.mod = inspect.getmodule(self)
	    self._str_modPath = str(self.mod)
	    self._str_mod = '%s' % self.mod.__name__.split('.')[-1]
	    self._str_funcCombined = "%s.%s"%(self._str_mod,self._str_funcName)
	except:self._str_funcCombined = self._str_funcName	
	
def verify_mirrorSideArg(*args,**kws):
    class fncWrap(cgmFuncCls):
	def __init__(self,*args,**kws):
	    """
	    """	
	    super(fncWrap, self).__init__(*args,**kws)
	    self._str_funcName = 'cgmGeneral.verify_mirrorSideArg'
	    self._l_ARGS_KWS_DEFAULTS = [{'kw':'str_side',"default":None,'help':"The side to validate","argType":"str"}] 	    
	    self.__dataBind__(*args,**kws)
	def __func__(self):
	    arg = self.d_kws['str_side']
	    if arg is None:
		self.log_error("str_side cannot be None")
		return False
	    try:
		if arg.lower() in ['right','left']:
		    return arg.capitalize()
		elif arg.lower() in ['center','centre']:
		    return 'Centre'
		else:raise StandardError,"Failed to find match"
	    except Exception,error:raise StandardError,"[ str_side: %s]{%s}"%(arg,error)	
    return fncWrap(*args,**kws).go()	

def report_enviornment():
    print(_str_headerDiv + " Enviornment Info " + _str_headerDiv + _str_subLine)	
    #print(_str_headerDiv + " Maya Version: %s "%int( mel.eval( 'getApplicationVersionAsFloat' )))
    for kw in ['cutIdentifier','version','apiVersion','file','product','date',
               'application','buildDirectory','environmentFile','operatingSystem',
               'operatingSystemVersion']:#'codeset'
	try:print(_str_baseStart + " Maya %s : %s "%(kw, mel.eval( 'about -%s'%kw )))	
	except Exception,error:log.error("%s | %s"%(kw,error))	
	
#>>> Sub funcs ==============================================================================
def subTimer(func):
    '''
    Simple timer decorator 
    -- Taken from red9 and modified. Orignal props to our pal Mark Jackson
    '''
    def wrapper( *args, **kws):
	t1 = time.time()
	res=func(*args,**kws) 
	t2 = time.time()
	log.info("here!")
	functionTrace=func.__name__ 
	_str_time = "%0.3f seconds"%(t2-t1)
	self._l_funcTimes.append([functionTrace,_str_time])	
	return res
    return wrapper  

def cgmExceptCB(etype, value, tb, detail=2, processed = False):
    # @param processed -- whether this exception has already been processed
    try:
	db_file = tb.tb_frame.f_code.co_filename
	#print("-- db_file: %s"%db_file)	
	#db_names = tb.tb_frame.f_code.co_names	
	#print("-- db_names: %s"%db_names)	
	
	if detail == 2:	    
	    if not processed:
		if db_file != "<maya console>":
		    lineno = tb.tb_lineno
		    line = linecache.getline(db_file, lineno)
		    print("-- Traceback File: %s"%db_file)
		    print("-- Traceback Line #: %d"%lineno)
		    print("-- Traceback Line: %s"%line)		
		print(_str_headerDiv + "Exception encountered..." + _str_headerDiv + _str_hardLine)	    		
		print("-- Coming from cgmExceptCB")		
		print("-- etype: %s"%etype)
		print("-- value: %s"%value)
		#print("-- tb: %s"%tb)
		#print("-- detail: %s"%detail)
	    print ""
	    report_enviornment()
	return value
	#return mUtils._formatGuiException(etype, value, tb, detail)
    except Exception,error:
	log.info("Exception Exception....{%s}"%error)
mUtils.formatGuiException = cgmExceptCB

def reset_mayaException():
    reload(mUtils)    
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
	    log.info(">"*3 + " %s "%_str_funcName + _str_hardLine)	    
	    log.error(">"*3 + " Step: %s "%args[0]._str_funcStep)	    
	    log.error(">"*3 + " Args: %s "%args[0]._str_funcArgs)
	    log.error(">"*3 + " KWs: %s "%args[0]._str_funcKWs)	    
	    log.info("%s >> Time to Fail >> = %0.3f seconds " % (_str_funcName,(time.clock()-t1)) + _str_subLine)			    
	    raise error            
        t2 = time.clock()
	
	#Initial print
	log.info(">"*3 + " %s "%_str_funcName + _str_hardLine)
	log.info(">"*3 + " Args: %s "%args[0]._str_funcArgs)
	log.info(">"*3 + " KWs: %s "%args[0]._str_funcKWs)		
		    
	log.info("%s >> Time >> = %0.3f seconds " % (_str_funcName,(t2-t1)) + _str_subLine)		
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
	    pass
            #log.debug('function module inspect failure')
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
	    pass
            #log.debug('function module inspect failure')
        try:
            #class function is part of, if found
            cls = args[0].__class__
            functionTrace+='%s.' % args[0].__class__.__name__
        except:
	    pass
            #log.debug('function class inspect failure')
        functionTrace+=func.__name__ 
        #log.debug('DEBUG TIMER : %s: %0.4f sec' % (functionTrace,(t2-t1)))
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
    mc.progressBar(mayaMainProgressBar, edit=True, endProgress=True)
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