"""
------------------------------------------
cgm_General: cgm.core
Author: Josh Burton
email: jjburton@cgmonks.com
Website : http://www.cgmonks.com
------------------------------------------

For help on cgmFuncCls - cgm.core.examples.help_cgmFuncCls
================================================================
"""
__MAYALOCAL = 'cgmGEN'
__RELEASE = '2020.2 | Release'

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
import datetime
import pprint
# Shared Defaults ========================================================

#=========================================================================
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#=========================================================================

#Strings settings
_str_subLine = '-'*100
_str_hardLine = '='*100
_str_hardBreak = '=' * 125
_str_headerDiv = '///'
_str_baseStart = "--"
_d_KWARG_stopAtStep = {'kw':'stopAtStep',"default":None, 'help':"Step of a cgmFuncToStopAt", "argType":"int/str"}

#Shared data...
_l_moduleStates = ['define','size','template','skeleton','rig']

class cgmFuncCls(object):  
    '''
    Core cgm function class wrapper. Adds a lot of features for maya functions for free. For example usage:
    cgm.core.examples.help_cgmFuncCls

    :parameters:
    args/kws | varied based on self._l_ARGS_KWS_DEFAULTS setup

    :raises:
    Exception | when reached

    :Do not
    Append to self._l_ARGS_KWS_DEFAULTS -- causes pass through issues with *args
    '''    
    def __init__(self,*args, **kws):
        self._str_funcClass = None
        self._str_funcName = None
        self._str_funcCombined = None
        self._str_progressBar = None
        self._str_funcDebug = None
        self._b_WIP = False
        self._b_autoProgressBar = False
        self._b_reportTimes = False
        self._b_pushCleanKWs = False
        self._b_ReturnBreak = False
        self._b_ExceptionInterupt = True#Whether to use the cgmFuncCls Exception Interupt or not
        self._str_lastLog = None
        self._int_stopStep = None
        self._str_substep = None
        self._l_ARGS_KWS_DEFAULTS = []
        self._l_ARGS_KWS_BUILTINS = [{'kw':'reportShow',"default":False,'help':"show report at start of log","argType":"bool"},
                                     {'kw':'reportTimes',"default":False,'help':"show step times in log","argType":"bool"},
                                     {'kw':'reportEnv',"default":False,'help':"Override. Just get maya env info","argType":"bool"},
                                     {'kw':'reportToDo',"default":False,'help':"Override. Get to do list for func","argType":"bool"},	                                 
                                     {'kw':'printHelp',"default":False,'help':"Override.  Get help block for func","argType":"bool"},
                                     {'kw':'setLogLevel',"default":None,'help':"Set the debug level on call","argType":"str"},
                                     {'kw':'autoProgressBar',"default":False,'help':"Show generated progress bar by steps","argType":"bool"},
                                     {'kw':'stopAtStep',"default":None, 'help':"Step of a cgmFuncToStopAt", "argType":"int/str"}]	
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
        self._l_reportMask = ['_b_ReturnBreak','_b_ExceptionInterupt','_b_pushCleanKWs','_str_lastLog','_l_ARGS_KWS_BUILTINS','_l_toDo','_l_warnings','_l_errors','_str_step','int_max','_Exception','_ExceptionError','_str_failStep','_str_failTime','_str_modPath','_go','l_funcSteps','_str_funcHelp','d_return','_str_funcDebug','_str_funcKWs','_l_reportMask','_l_errorMask',
                              '_b_autoProgressBar','_int_stopStep','_b_reportTimes','_str_progressBar','_str_progressBarReportStart',  
                              '_str_funcClass','_str_funcName','d_kws','_str_funcCombined','_l_funcArgs','_b_WIP','_l_funcTimes','_l_ARGS_KWS_DEFAULTS',
                              '_str_mod','_str_substep','mod','_str_funcArgs','_d_funcKWs','_str_reportStart','_str_headerDiv','_str_subLine','_str_hardLine']  

    def __updateFuncStrings__(self):
        self._str_funcCombined = self._str_funcName
        try:self._str_funcName = "{0}- from {1}".format(self._str_funcName,kws['calledFrom'])
        except:pass
        self._str_progressBarReportStart = self._str_funcCombined
        self._str_reportStart = " {0} >> ".format(self._str_funcName)

    def __dataBind__(self,*args,**kws):
        try:self._l_funcArgs = args
        except:self._l_funcArgs = []
        try:self._d_funcKWs = kws
        except:self._d_funcKWs = {}	
        try:self._str_funcArgs = str(args)
        except:self._str_funcArgs = None
        try:self._str_funcKWs = str(kws)
        except:self._str_funcKWs = None

        try:self._str_funcHelp 
        except:
            try:self._str_funcHelp = self.__doc__
            except:self._str_funcHelp = None

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
                        if d_buffer not in self._l_ARGS_KWS_BUILTINS:
                            try:
                                self.d_kws[d_buffer['kw']] = args[ int_argIdx ]#First we try the arg index			
                            except:
                                #self.log_info("Using default [%s] = %s"%(str_kw,d_buffer.get("default")))
                                self.d_kws[str_kw] = d_buffer.get("default")#Lastly, we use the default value
                        else:
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
            except Exception,error:raise StandardError,"{0} failed to store kw: {1} | value: {2} | error: {3}".format(self._str_reportStart,kw,kws[kw],error)
        '''
	self._l_ARGS_KWS_BUILTINS = [{'kw':'reportShow',"default":False,'help':"(BUILTIN) - show report at start of log","argType":"bool"},
	                             {'kw':'reportTimes',"default":False,'help':"(BUILTIN) - show step times in log","argType":"bool"},
	                             {'kw':'reportEnv',"default":False,'help':"(BUILTIN) - Override. Just get maya env info","argType":"bool"},
	                             {'kw':'reportToDo',"default":False,'help':"(BUILTIN) - Override. Get to do list for func","argType":"bool"},	                                 
	                             {'kw':'printHelp',"default":False,'help':"(BUILTIN) - Override.  Get help block for func","argType":"bool"},
	                             {'kw':'setLogLevel',"default":None,'help':"(BUILTIN) - Set the debug level on call","argType":"str"},
	                             {'kw':'autoProgressBar',"default":False,'help':"(BUILTIN) - show generated progress bar by steps","argType":"bool"}]
	'''    
        #Minor validation of built ins
        if self.d_kws.get('autoProgressBar'):self._b_autoProgressBar = True
        if self.d_kws.get('reportTimes'):self._b_reportTimes = True



    def __func__(self,*args,**kws):
        return "{0} No function set".format(self._str_reportStart)

    def validate_stopAtStep(self):
        __stopAtStep = self.d_kws.get('stopAtStep')
        if __stopAtStep is not None:
            if type(__stopAtStep) is int:
                self.log_debug("stopAtStep is int")
                if __stopAtStep is 0:
                    self.log_warning("a stopAtStep of 0 is pointless as no steps will execute. Will stop anyway.")		    
                if __stopAtStep <= (len(self.l_funcSteps)-1):
                    self.log_debug("stopAtStep in range")		    
                    self._int_stopStep = __stopAtStep
                else:self.log_debug("stopAtStep NOT in range")		    

    def _SuccessReturn_(self, res = None):
        '''
        Added as a mid function success break.

        Usage in line would be 
        return self._SuccessReturn_('Cat') if you wanted to return 'Cat' at that step.
        Whatever the return is (if there is) will be stored to the buffer
        '''
        self._b_ReturnBreak = 1
        if res is not None:
            self.log_info("SUCCESS >> {0}".format(res))	    	    
            self.d_return[self._str_step] = res

    def _FailBreak_(self, res = None):
        '''
        Added as a mid function success break.

        Usage in line would be 
        return self._SuccessReturn_('Cat') if you wanted to return 'Cat' at that step.
        Whatever the return is (if there is) will be stored to the buffer
        '''
        self._b_ReturnBreak = 1
        if res is not None:
            self.log_error("FAILURE >> {0}".format(res))	    
            self.d_return[self._str_step] = res

    def _ExceptionHook_(self, etype = None, value = None, tb = None, detail=None):
        # do something here...
        try:
            if tb is None: tb = sys.exc_info()[2]#...http://blog.dscpl.com.au/2015/03/generating-full-stack-traces-for.html
            if detail == None:
                if mel.eval('stackTrace -q -state;') == 1:
                    detail = 2
            str_lastLogBuffer = self._str_lastLog#Buffer this
            if detail == 2:	
                #report_enviornment()
                try:db_file = tb.tb_frame.f_code.co_filename
                except:db_file = "<maya console>"
                self.report_base()
                self.log_info(_str_headerDiv + " Exception Log " + _str_headerDiv + _str_subLine)		
                self.log_info("Step: '{0}'".format(self._str_failStep))
                self.log_info("Time: {0} sec".format(self._str_failTime))
                self.report_selfStored()
                self.report_warnings()		
                self.report_errors()
                if str_lastLogBuffer:
                    try:self.log_info("Last log entry: %s"%str_lastLogBuffer)
                    except Exception, error:
                        log.error("This failed")
                        log.error("Failed to report last log: {0}".format(error))		
                for i,item in enumerate(reversed(inspect.getouterframes(tb.tb_frame)[1:])):
                    print("traceback frame[{0}]".format(i+1) + _str_subLine)		    
                    print ' File "{1}", line {2}, in {3}\n'.format(*item),
                    for item in inspect.getinnerframes(tb):
                        if 'go' not in item:#Path to get our wrapper stuff out of the traceback report
                            if '__func__' not in item:print ' File "{1}", line {2}, in {3}\n'.format(*item),
                    if item[4] is not None:
                        for line in item[4]:
                            print ' ' + line.lstrip(),			
                    #for line in item[4]:
                        #print ' ' + line.lstrip(),		
                '''if db_file != "<maya console>":
		    linecache.clearcache()		
		    lineno = tb.tb_lineno
		    line = linecache.getline(db_file, lineno)
		    self.log_info("Traceback File: %s"%db_file)
		    self.log_info("Line#: %d"%lineno)
		    self.log_info("Line: %s"%line)'''		

                #self.log_info("Exception Type: %s"%etype)
                #self.log_info("Exception value: %s"%value)
                #self.log_info("Exception: {0}".format(self._Exception))		
                #self.log_info("Exception error: {0}".format(self._ExceptionError))
                #self.log_info("Traceback Obj: %s"%tb)
                self.log_info("Detail: %s"%detail)		
            else:
                pass
                #self.log_error("[Step: '{0}' | time: {1} | error: {2}".format(self._str_failStep,self._str_failTime,self._ExceptionError))
            if detail == 2:self.log_info(_str_hardBreak)
            self.progressBar_end()
            #mUtils.formatGuiException = cgmExceptCB#Link back to our orignal overload
            return cgmExceptCB(etype,value,tb,detail,True)
            #return mUtils._formatGuiException(etype, value, tb, detail)	
        except Exception,error:
            #mUtils.formatGuiException = cgmExceptCB#Link back to our orignal overload	    
            print("[{0}._ExceptionHook_ Exception | {1}".format(self._str_funcCombined,error))

    def go(self,*args,**kws):
        """
        """
        self._Exception  = None
        self._ExceptionError = None
        self.validate_stopAtStep()

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
            raise StandardError, ">"*3 + " {0}[FAILURE go start | error: {1}]".format(self._str_funcCombined,error)

        #mc.undoInfo(openChunk=True)
        int_lenSteps = len(self.l_funcSteps)

        if self._b_pushCleanKWs:
            log.debug("Pushing cleanKWs")
            _d_cleanKWS = self.get_cleanKWS()
            if kws:
                for k in _d_cleanKWS:kws[k] = _d_cleanKWS[k]
            else:kws = _d_cleanKWS	

        for i,d_step in enumerate(self.l_funcSteps):
            if self._b_ReturnBreak:
                self.log_debug("Success Break | Step {0}".format(i))
                break
            if self._int_stopStep is not None and i >= self._int_stopStep:
                self.log_info("Stop at step reached ({0}) | Skipped the following...".format(self._int_stopStep))
                for ii,d_step in enumerate(self.l_funcSteps[self._int_stopStep:]):
                    _str_step = d_step.get('step', False)
                    self.log_info("Step: {0} | {1}".format(ii + self._int_stopStep, _str_step))		    
                break
            t1 = time.clock()	    
            try:
                try:
                    _str_step = d_step.get('step',False)
                    if _str_step:
                        self._str_progressBarReportStart = self._str_reportStart #+ " %s "%_str_step
                    else: _str_step = 'Process'

                    self._str_step = _str_step	
                    try:self.log_debug(_str_headerDiv + " Step : %s "%_str_step + _str_headerDiv + _str_subLine)
                    except Exception,error:
                        if self._b_ExceptionInterupt:
                            pass
                            #mUtils.formatGuiException = self._ExceptionHook_#Link our exception hook   			
                        self.log_warning("[debug info! | error: {0}]".format(error))		    
                except Exception,error:raise Exception,"[strStep query]{%s}"%error 

                try:
                    if self._b_autoProgressBar:self.progressBar_set(status = _str_step, progress = i, maxValue = int_lenSteps)
                except Exception,error:self.log_warning("[progress bar! | error: {0}]".format(error))

                res = d_step['call'](*args,**kws)
                if res is not None:
                    self.d_return[_str_step] = res
                """
		if goTo.lower() == str_name:
		    log.debug("%s.doBuild >> Stopped at step : %s"%(self._strShortName,str_name))
		    break"""
            except Exception, error:
                self._str_failStep = _str_step
                self._str_failTime = "%0.3f"%(time.clock()-t1)
                self._Exception = Exception
                self._ExceptionError = error
                break

            t2 = time.clock()
            _str_time = "%0.3f"%(t2-t1)
            pair_time = [_str_step,_str_time]
            self._l_funcTimes.append([_str_step,_str_time])	
            if self._b_reportTimes:
                self.log_info(" [TIME] -- Step: '{0}' >>  {1} ".format(pair_time[0],pair_time[1]))				 
        self.progressBar_end()
        #mc.undoInfo(closeChunk=True)	

        #Reporting and closing out =========================================================================
        if self._b_WIP or self.d_kws.get('reportShow'):
            self.report()

        if self.d_kws.get('reportToDo') or self._l_toDo:
            self.report_toDo() 

        if self.d_kws.get('reportEnv'):
            report_enviornment()   

        if self._b_reportTimes:
            try:
                f_total = (time.clock()-t_start)	    
                if int_lenSteps > 2:
                    self.log_info(_str_headerDiv + " Times " + _str_headerDiv + _str_subLine)			    	    
                    #if self.int_max != 0:
                        #for pair in self._l_funcTimes:
                            #self.log_info(" -- '{0}' >>  {1} ".format(pair[0],pair[1]))				 
                    self.log_warning(_str_headerDiv + " Total : %0.3f sec "%(f_total) + _str_headerDiv + _str_subLine)			    	    
                #else:self.log_warning("[Total = %0.3f sec] " % (f_total))
            except Exception,error:self.log_error("[Failed to report times | error: {0}]".format(error))

        if self._Exception is not None:
            if self._b_ExceptionInterupt:
                self.update_moduleData()			
                #mUtils.formatGuiException = self._ExceptionHook_#Link our exception hook   

            self._ExceptionHook_(self._Exception,self._ExceptionError)
            raise self._Exception, self._ExceptionError
            #raise self._Exception,"{0} >> {1}".format(self._str_funcCombined,str(self._ExceptionError))
            #else:
                #raise self._Exception,"{0} | {1} | {2}".format(self._str_reportStart,self._str_step,self._ExceptionError)

        #mUtils.formatGuiException = cgmExceptCB#Link back to our orignal overload
        return self._return_()

    def _return_(self):
        '''overloadable for special return'''
        if self.int_max == 0:#If it's a one step, return, return the single return
            try:return self.d_return[self.d_return.keys()[0]]
            except:pass

        for k in self.d_return.keys():#Otherise we return the first one with actual data
            buffer = self.d_return.get(k)
            if buffer is not None:
                return buffer

        if self.d_return:return self.d_return

    def subTimer(self, func, *args, **kws):
        '''
        Variation,only outputs on debug
        -- Taken from red9 and modified. Orignal props to our pal Mark Jackson
        '''
        _str_substep = self._str_substep

        t1 = time.time()
        res = func(*args,**kws) 
        t2 = time.time()

        _str_time = "%0.3f"%(t2-t1)
        self._l_funcTimes.append([_str_substep,_str_time])	    
        if self._b_reportTimes:
            self.log_info(" [TIME] -- subStep: '{0}' >>  {1} ".format(_str_substep,_str_time))
        return res	

    def report(self):
        self.update_moduleData()
        self.report_base()
        self.report_selfStored()
        if not self._b_reportTimes:self.report_steps()

    def report_base(self):
        self.update_moduleData()
        self.log_info("="*100)	
        self.log_info(_str_headerDiv + " %s "%self._str_funcCombined + _str_headerDiv)
        self.log_info("="*100)
        self.log_info(" Python Module: %s "%self._str_modPath)
        try:self.log_info(_str_baseStart + " Python Module Version: %s "%self.mod.__version__)
        except:pass		
        self.log_info(_str_headerDiv  + " ArgsKws " + _str_headerDiv + _str_subLine)		
        if self._str_funcArgs:self.log_info(" Args: %s"%self._str_funcArgs)
        if self._str_funcKWs:self.log_info(" KWs: %s"%self._str_funcKWs)	  
        """if self.d_kws:
	    self.log_info(" Active Dict: "+_str_subLine)							    
	    l_keys = self.d_kws.keys()
	    l_keys.sort()	    
	    for k in l_keys:
		self.log_info(_str_baseStart *2 + "['%s'] = %s "%(k,self.d_kws[k]))"""

    def report_selfStored(self):
        l_keys = self.__dict__.keys()
        l_keys.sort()
        if l_keys:
            self.log_info(_str_headerDiv + " Self Stored " + _str_headerDiv + _str_subLine)
            for k in l_keys:
                if k not in self._l_reportMask:
                    buffer = self.__dict__[k]
                    if type(buffer) is dict:
                        self.log_info("('{0}' -- nested dict)".format(k))
                        l_bufferKeys = buffer.keys()
                        l_bufferKeys.sort()
                        for k2 in l_bufferKeys:
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
        print("#" + ">"*3 + " %s "%self._str_funcCombined + _str_hardBreak)
        print("Python Module: %s "%self._str_modPath)	 
        if self._str_funcHelp is not None:
            print(_str_subLine * 2)		
            print("%s "%self._str_funcHelp)
        print(_str_subLine * 2)	
        print("@kws -- [index - argKW(argType - default) | info]") 
        for i,d_buffer in enumerate(self._l_ARGS_KWS_DEFAULTS + self._l_ARGS_KWS_BUILTINS):
            l_tmp = ['    %i - '%i]
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
            try:l_tmp.append(" | %s"%d_buffer['help'])
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
            self._str_lastLog = arg
            print("%s%s"%(self._str_reportStart,str(arg)))
        except:pass	

    def log_toDo(self,arg):
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
            self._str_lastLog = arg	    
            #print("[ERROR]%s%s"%(self._str_reportStart,str(arg)))	    
        except:pass

    def log_warning(self,arg):
        try:
            try:self._l_warnings.append("%s | %s"%(self._str_step,str(arg)))
            except:self._l_warnings.append("%s"%(str(arg)))	    
            log.warning("%s%s"%(self._str_reportStart,str(arg)))
            self._str_lastLog = arg	    
            #print("[WARNING]%s%s"%(self._str_reportStart,str(arg)))	    
        except Exception,error:
            log.error(error)	
    def log_debug(self,arg):
        try:
            if self._str_step:
                log.debug("[DEBUG]{0}{1} | {2}".format(self._str_reportStart,self._str_step,str(arg)))				
            else:
                log.debug("[DEBUG]{0}{1}".format(self._str_reportStart,str(arg)))
            self._str_lastLog = arg	    
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


    def log_infoDict(self,arg = None,tag = 'Stored Dict'):
        '''
        Log a dictionary.

        :parameters:
            arg | dict
            tag | string
        	label for the dict to log.

        :raises:
            TypeError | if not passed a dict
        '''
        try:
            if not isinstance(arg,dict):
                raise TypeError,"[Not a dict. arg: {0}]".format(arg)
            try:
                l_keys = arg.keys()
                self.log_info('Dict: {0} '.format(tag) + _str_subLine)			    
                l_keys.sort()
                for k in l_keys:
                    try:str_key = k.p_nameShort
                    except:str_key = k
                    buffer = arg[k]
                    if isinstance(buffer,dict):
                        self.log_info(" Nested Dict: '{0}' ".format(str_key) + _str_subLine)
                        l_bufferKeys = buffer.keys()
                        l_bufferKeys.sort()
                        for k2 in l_bufferKeys:
                            self.log_info("-"*3 +'>' + " '{0}' : {1} ".format(k2,buffer[k2]))			
                    else:
                        self.log_info(">" + " '{0}' : {1} ".format(str_key,arg[k]))		    
            except Exception,error:
                self.log_warning("[Not a dict. arg: {0} | error: {1} ]".format(arg,error))
        except:pass	

    def log_infoNestedDict(self,arg):
        try:
            if type(arg) not in [list,tuple]:arg = [arg]#attr

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
                            self.log_info(">" + " Nested Dict: '%s' "%(str_key) + _str_subLine)
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
            if self._str_mod  == '__main__':
                self._str_mod = "LocalMayaEnv" 
                self._str_modPath = "Script Editor" 
            self._str_funcCombined = "%s.%s"%(self._str_mod,self._str_funcName)
        except:self._str_funcCombined = self._str_funcName	

def returnCallerFunctionName():
    '''
    Return the function name two frames back in the stack. This enables
    exceptions called to report the function from which they were called.
    '''

    result = '[unknown function]'

    try:
        frame, filename, line_no, s_funcName, lines, index = \
            inspect.getouterframes(inspect.currentframe())[2]

        s_moduleName = inspect.getmodule(frame)
        s_moduleName = "" if s_moduleName is None else s_moduleName.__name__

        result = "{0}.{1}".format(s_moduleName, s_funcName)

        if s_funcName == '<module>':
            s_funcName = "<Script Editor>"

        if filename == "<maya console>":
            result = "<Maya>.{0}".format(s_funcName)
    except StandardError:
        log.exception("Failed to inspect function name")
    return result

def log_start(str_func,split='-',intCount = 80):
    log.debug("{0} >> ...".format(str_func)+split*intCount)
def log_sub(str_func,msg='break',split='_',intCount = 30):
    log.debug("{0} >> {1} ".format(str_func,msg)+split*intCount)
    
def logString_start(str_func,split='-',intCount = 80):
    if str_func:return "{0} >> ".format(str_func)+split*intCount
    return " ".format(str_func)+split*intCount

def logString_sub(str_func,msg='break',split='_',intCount = 80):
    if str_func:return "{0} >> {1} ...".format(str_func,msg)+split*intCount
    return "{0} ...".format(msg)+split*intCount

def logString_msg(str_func,msg=''):
    if str_func:return "{0} >> {1} ...".format(str_func,msg)
    return "{0} ...".format(msg)
    
def log_info_dict(arg = None,tag = 'Stored Dict'):
    '''
    Log a dictionary.

    :parameters:
    arg | dict
    tag | string
    label for the dict to log.

    :raises:
    TypeError | if not passed a dict
    '''
    try:
        if not isinstance(arg,dict):
            raise TypeError,"[Not a dict. arg: {0}]".format(arg)
        try:
            l_keys = arg.keys()
            print('Dict: {0} '.format(tag) + _str_subLine)			    
            l_keys.sort()
            for k in l_keys:
                try:str_key = k.p_nameShort
                except:str_key = k
                buffer = arg[k]
                if isinstance(buffer,dict):
                    print(">" + " Nested Dict: '{0}' ".format(str_key) + _str_subLine)
                    l_bufferKeys = buffer.keys()
                    l_bufferKeys.sort()
                    for k2 in l_bufferKeys:
                        print("-"*2 +'>' + " '{0}' : {1} ".format(k2,buffer[k2]))			
                else:
                    print(">" + " '{0}' : {1} ".format(str_key,arg[k]))		    
        except Exception,error:
            print("[Not a dict. arg: {0} | error: {1} ]".format(arg,error))
    except:pass
    
def walk_dat(arg = None, tag = None, counter = 0):
    '''
    Log a dictionary.

    :parameters:
    arg | dict
    tag | string
    label for the dict to log.

    :raises:
    TypeError | if not passed a dict
    '''
    if isinstance(arg,dict):
        l_keys = arg.keys()
        if counter == 0:
            print('> {0} '.format(tag) + _str_subLine)			                
        elif len(l_keys)<2:
            print('-'* counter + '> {0} '.format(tag))		            
        else:
            print('-'* counter + '> {0} '.format(tag) + _str_subLine)		
        
        counter+=2                
        l_keys.sort()
        for k in l_keys:
            try:str_key = k.p_nameShort
            except:str_key = k
            buffer = arg[k]          
            walk_dat(buffer,str_key,counter)
    elif isinstance(arg,list):
        if counter == 0:
            print('{0} : '.format(tag))			                
        else:
            print(' '* counter + ' {0} : '.format(tag))			                            
        for i,v in enumerate(arg):
            try:str_v = v.p_nameShort
            except:str_v = v                
            print(' '* counter + ' {0} : {1}'.format(i,str_v) + str(arg))		        
    else:
        if counter == 0:
            print('{0} : '.format(tag) + str(arg))			                
        else:
            print(' '* counter + ' {0} : '.format(tag) + str(arg))			                

    return    

def walk_heirarchy_dict_to_list(arg = None, l_return = None):
    '''
    Get an ordered list from a heirarchal dictionary.
    {'blockroot1':{'child1_1':{'child1_1_1':{},'child1_1_2':{}}},'blockroot2':{'child2_1':{}}}

    :parameters:
    arg | dict
    tag | string
    label for the dict to log.

    :raises:
    TypeError | if not passed a dict
    '''
    if l_return is None:
        l_return = []
            
    if isinstance(arg,dict):
        l_keys = arg.keys()	
        l_return.extend(l_keys)
        
        for k in l_keys:
            #l_return.append(k)
            walk_heirarchy_dict_to_list(arg[k],l_return)
		                
    return l_return
        

    
def print_dict(arg = None,tag = 'Stored Dict', module = "Stuff..."):
    '''
    Log a dictionary.

    :parameters:
    arg | dict
    tag | string
    label for the dict to log.

    :raises:
    TypeError | if not passed a dict
    '''
    def p(msg):
        print "{0} : {1}".format(module,msg)
    try:
        if not isinstance(arg,dict):
            raise TypeError,"[Not a dict. arg: {0}]".format(arg)
        try:
            l_keys = arg.keys()
            p('d: {0} '.format(tag) + _str_subLine)			    
            l_keys.sort()
            for k in l_keys:
                try:str_key = k.p_nameShort
                except:str_key = k
                buffer = arg[k]
                if isinstance(buffer,dict):
                    p(">" + "'{0}' ".format(str_key) + _str_subLine)
                    l_bufferKeys = buffer.keys()
                    l_bufferKeys.sort()
                    for k2 in l_bufferKeys:
                        p("-"*2 +'>' + " '{0}' : {1} ".format(k2,buffer[k2]))			
                else:
                    p(">" + " '{0}' : {1} ".format(str_key,arg[k]))		    
        except Exception,error:
            log.warning("[Not a dict. arg: {0} | error: {1} ]".format(arg,error))
    except:pass	

def verify_mirrorSideArg(*args,**kws):
    class fncWrap(cgmFuncCls):
        def __init__(self,*args,**kws):
            """
            """	
            super(fncWrap, self).__init__(*args,**kws)
            self._str_funcName = 'verify_mirrorSideArg'
            self._str_funcHelp = "Validate a mirror side arg for red9 use"	    
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'str_side',"default":None,'help':"The side to validate","argType":"str"}] 	    
            self.__dataBind__(*args,**kws)
        def __func__(self):
            arg = self.d_kws['str_side']
            if arg is None:
                self.log_error("str_side cannot be None")
                return False
            try:
                arg = str(arg)
                if arg.lower() in ['right','left']:
                    return arg.capitalize()
                elif arg.lower() in ['center','centre']:
                    return 'Centre'
                else:
                    return False
                    #raise Exception,"Failed to find match"
            except Exception,error:raise Exception,"[ str_side: %s]{%s}"%(arg,error)	
    return fncWrap(*args,**kws).go()	

def get_mayaEnviornmentDict():
    _d = {}
    for kw in ['cutIdentifier','version','apiVersion','file','product','date',
               'application','buildDirectory','environmentFile','operatingSystem',
               'operatingSystemVersion']:#'codeset'
        try:_d[kw] = mel.eval( 'about -%s'%kw )	
        except Exception,error:log.error("%s | %s"%(kw,error))	
    return _d

__mayaVersion__ = int( mel.eval( 'getApplicationVersionAsFloat' ) )
__mayaApiVersion__ = int( mel.eval( 'about -apiVersion' ) )

def report_enviornment():
    print(_str_headerDiv + " Enviornment Info " + _str_headerDiv + _str_subLine)	
    #print(_str_headerDiv + " Maya Version: %s "%int( mel.eval( 'getApplicationVersionAsFloat' )))
    _d = get_mayaEnviornmentDict()
    for kw,item in _d.iteritems():
        try:print(_str_baseStart + " Maya %s : %s "%(kw,item))	
        except Exception,error:log.error("%s | %s"%(kw,error))	

def report_enviornmentSingleLine():
    print("Maya: {0} | OS: {1}".format(mel.eval( 'about -%s'%'version'), mel.eval( 'about -%s'%'operatingSystemVersion')))


#import sys
def get_func_string():
    #just for reference. this will just return this function. if wanted, need to copy to other functions
    return sys._getframe().f_code.co_name


class Callback(object):
    '''
    By Hamish McKenzie
    stupid little callable object for when you need to "bake" temporary args into a
    callback - useful mainly when creating callbacks for dynamicly generated UI items
    '''
    def __init__( self, func, *a, **kw ):
        self._func = func
        self._args = a
        self._kwargs = kw
    def __call__( self, *args ):
        try:return self._func( *self._args, **self._kwargs )
        except Exception,err:
            try:log.info("Func: {0}".format(self._func.__name__))
            except:log.info("Func: {0}".format(self._func))
            if self._args:
                log.info("args: {0}".format(self._args))
            if self._kwargs:
                log.info("kws: {0}".format(self._kwargs))
            for a in err.args:
                log.info(a)
                
            cgmException(Exception,err)
        finally:del self
            
CB = Callback

class CallbackPlus(object):
    '''
    Same as Callback but additional args and kwargs can be added
    '''
    def __init__( self, func, *a, **kw ):
        self._func = func
        self._args = a
        self._kwargs = kw
    def __call__( self, *args, **kwargs ):
        try:
            self._args = args + self._args
            self._kwargs.update(kwargs)
            return self._func( *self._args, **self._kwargs )
        except Exception,err:
            try:log.info("Func: {0}".format(self._func.__name__))
            except:log.info("Func: {0}".format(self._func))
            if self._args:
                log.info("args: {0}".format(self._args))
            if self._kwargs:
                log.info("kws: {0}".format(self._kwargs))
            for a in err.args:
                log.info(a)
                
            cgmException(Exception,err)
        finally:del self

def stringModuleClassCall(self, module = None,  func = '', *args,**kws):
    """
    Function to call from a given module a function by string name with args and kws. 
    
    self - should be a class instance you want passed forward
    
    """
    try:_short = self.p_nameShort
    except:_short = self.__class__.__name__
    
    _str_func = 'stringModuleClassCall( {0} )'.format(_short)
    _res = None

    if not args:
        _str_args = ''
        args = [self]
    else:
        _str_args = ','.join(str(a) for a in args) + ','
        args = [self] + [a for a in args]

    if not kws:
        kws = {}
        _kwString = ''  
    else:
        _l = []
        for k,v in kws.iteritems():
            _l.append("{0}={1}".format(k,v))
        _kwString = ','.join(_l)  

    try:
        #mc.undoInfo(openChunk=True, chunkName=_str_func)        
        log.debug("|{0}| >> On: {1}.{2}".format(_str_func,module.__name__, _short))     
        log.debug("|{0}| >> {1}.{2}({3}{4})...".format(_str_func,_short,func,_str_args,_kwString))                                    
        _res = getattr(module,func)(*args,**kws)
    except Exception,err:
        #mc.undoInfo(closeChunk=True, chunkName=_str_func)        
        log.error(_str_hardLine)
        log.error("|{0}| >> Failure: {1}".format(_str_func, err.__class__))
        log.error("Self: {0} | func: {1}".format(_short,func))
        log.error("Module: {0} ".format(module))            

        if args:
            log.error("Args...")
            for a in args:
                log.error("      {0}".format(a))
        if kws:
            log.error(" KWS...".format(_str_func))
            for k,v in kws.iteritems():
                log.error("      {0} : {1}".format(k,v))   
        log.error("Errors...")
        for a in err.args:
            log.error(a)
        #cgmExceptCB(Exception,err)
        raise Exception,err
    #mc.undoInfo(closeChunk=True, chunkName=_str_func)            
    return _res    
        
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
        if self._b_reportTimes:
            self.log_info(" [TIME] -- Step: '{0}' >>  {1} ".format(pair_time[0],pair_time[1]))	
        return res
    return wrapper  

def myFirstFuncCls(*args, **kws):
    class fncWrap(cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'myFirstFuncCls'	
            self.__dataBind__(*args, **kws)#...this needs to be here
        def __func__(self):
            raise ValueError, "no"
    return fncWrap(*args, **kws).go()

def testException(message = 'cat'):
    a = range(0,22)
    cat = 1
    try:
        raise Exception, message
    except Exception,err:
        cgmExceptCB(Exception,err,fncDat=vars())
def cgmExceptCB_BAK(etype = None, value = None, tb = None, detail=2, localDat = None, processed = False,tracebackCap=1,**kws):
    if tb is None: tb = sys.exc_info()[2]#...http://blog.dscpl.com.au/2015/03/generating-full-stack-traces-for.html
    
    if localDat is None:
        localDat = kws.get('fncDat',None)
        
    if detail == None:
        if mel.eval('stackTrace -q -state;') == 1:
            detail = 2
    if detail == 2:	
        #report_enviornment()
        try:db_file = tb.tb_frame.f_code.co_filename
        except:db_file = "<maya console>"
        print(_str_headerDiv + " Exception Log " + _str_headerDiv + _str_subLine)		
        
        try:
            for i,item in enumerate(reversed(inspect.getouterframes(tb.tb_frame)[1:])):
                try:
                    if i >= tracebackCap:
                        break
                    print("traceback frame[{0}]".format(i+1) + _str_subLine)		    
                    print ' File "{1}", line {2}, in {3}\n'.format(*item),
                    #for item in inspect.getinnerframes(tb):
                        #print ' File "{1}", line {2}, in {3}\n'.format(*item)
                    if item[4] is not None:
                        for line in item[4]:
                            try:
                                print ' ' + line.lstrip()
                            except Exception,err:
                                print "Item [4] Failed: {0} | {1}".format(i,err)                            
                except Exception,err:
                    print "Failed: {0} | {1}".format(i,err)
                    print item
        except Exception,err:
            print "Traceback Failed: {0}".format(err)
                
    
    if value:
        print(_str_headerDiv + " Error log " + _str_headerDiv + _str_subLine)		        
        for i,a in enumerate(value.args):
            print(" {0} : {1}".format(i,a))
    if localDat:
        print(_str_headerDiv + " Local " + _str_headerDiv + _str_subLine)		
        pprint.pprint(localDat)
    print _str_hardBreak
    if etype:raise etype,value
    
    
def cgmExceptCB2(etype, value, tb = None, detail=2, processed = False):
    # @param processed -- whether this exception has already been processed
    try:
        if tb is None: tb = sys.exc_info()[2]#...http://blog.dscpl.com.au/2015/03/generating-full-stack-traces-for.html

        try:db_file = tb.tb_frame.f_code.co_filename
        except:db_file = "<maya console>"
        #print("-- db_file: %s"%db_file)	
        #db_names = tb.tb_frame.f_code.co_names	
        #print("-- db_names: %s"%db_names)	

        if detail == 2:	    
            if not processed:
                if db_file != "<maya console>":
                    for item in reversed(inspect.getouterframes(tb.tb_frame)[1:]):
                        print ' File "{1}", line {2}, in {3}\n'.format(*item),
                        for line in item[4]:
                            print ' ' + line.lstrip(),
                        for item in inspect.getinnerframes(tb):
                            print ' File "{1}", line {2}, in {3}\n'.format(*item),
                        for line in item[4]:
                            print ' ' + line.lstrip()		    
                    #lineno = tb.tb_lineno
                    #line = linecache.getline(db_file, lineno)
                    #print("-- Traceback File: %s"%db_file)
                    #print("-- Traceback Line #: %d"%lineno)
                    #print("-- Traceback Line: %s"%line)
                print(_str_headerDiv + "Exception encountered..." + _str_headerDiv + _str_hardLine)	    		
                print("-- Coming from cgmExceptCB")		
                print("-- etype: %s"%etype)
                print("-- value: %s"%value)
                #print("-- tb: %s"%tb)
                #print("-- detail: %s"%detail)

            print ""
            #report_enviornment()
        #return value
        return mUtils._formatGuiException(etype, value, tb, detail)
    except Exception,error:
        log.info("Exception Exception....{%s}"%error)

#mUtils.formatGuiException = cgmExceptCB

def reset_mayaException():
    reload(mUtils)    
"""
example subFunctionClass(object)
class sampleClass(cgmFunctionClass):
    def __init__(self,*args, **kws):
        super(sampleClass, self).__init__(*args, **kws)
"""

def example_throwException():
    raise Exception,"Exception!"

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

def func_getTraceString(func):
    str_func = None
    str_module = None
    _l_join = []
    try:
        #module if found
        mod = inspect.getmodule(func)
        #log.debug("mod: %s"%mod)            
        #functionTrace+='%s >> ' % mod.__name__#.split('.')[-1]
        str_module = mod.__name__#.split('.')[-1]
        _l_join.append(str_module)
    except:pass
    
    try:
        #class function is part of, if found
        mClass = False
        mNode = False
        try:
            mClass = func.__self__.mClass
            mNode = func.__self__.mNode
        except:pass
        
        cls = func.__class__
        clsType = type(cls)
        clsString = func.__class__.__name__  
        str_func = func.__name__
        
        if mClass:_l_join.append(mClass)
        if mNode: _l_join.append("('{0}')".format(mNode))
        _l_join.append(str_func)
        
    except Exception,error:
        log.debug('function class inspect failure: %s'%error)
            
    return '.'.join(_l_join)
def Timer2(func):
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

def returnTimeStr(arg = "%m%d%Y"):
    '''
    %d is the day number
    %m is the month number
    %b is the month abbreviation
    %y is the year last two digits
    %Y is the all year
    %H is the hour in local time
    %M is the minute in local time
    %S is the second in local time
    '''
    try:
        #today = datetime.date.today()
        #return today.strftime(arg)  
        return time.strftime(arg)
    except Exception,error:
        raise Exception,"cgmGeneral.returnDateStr(arg = {1}) fail | {0}".format(error,arg)

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
    try:mayaMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
    except:
        return
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
    
from functools import wraps
def Func(func):
    '''
    '''
    @wraps(func)
    def wrapper(*args, **kws):
        res=None
        err=None
        try:
            res=func(*args, **kws)
        except Exception, error:
            err = error
        finally:
            if err:
                #print(_str_headerDiv + " cgmGen.func Log " + _str_headerDiv + _str_hardBreak)		                
                
                try:print("Func: {0}".format(func.__name__))
                except:print("Func: {0}".format(func))                
                if args:
                    print(_str_headerDiv + " Args " + _str_headerDiv + _str_subLine)		        
                    for i, arg in enumerate(args):
                        print("    arg {0}: {1}".format(i, arg))
                if kws:
                    print(_str_headerDiv + " Kws... " + _str_headerDiv + _str_subLine)		        
                    for items in kws.items():
                        print("    kw: {0}".format(items))   
                traceback = sys.exc_info()[2]  # get the full traceback
                cgmException(Exception,err,traceback)
            return res
    return wrapper

def Timer(func):
    '''
    '''
    @wraps(func)
    def wrapper(*args, **kws):
        res=None
        err=None
        try:_str_func = func_getTraceString(func)
        except:_str_func = func
    
        try:
            t1 = time.time()
            res=func(*args,**kws) 
            t2 = time.time()            
            print("|{0}| >> Time >> = {1} seconds".format(_str_func, "%0.4f"%( t2-t1 ))) 
            
        except Exception, error:
            err = error
        finally:
            if err:
                #print(_str_headerDiv + " cgmGen.func Log " + _str_headerDiv + _str_subLine)		                
                try:print("Func: {0}".format(func.__name__))
                except:print("Func: {0}".format(func))                
                if args:
                    print(_str_headerDiv + " Args " + _str_headerDiv + _str_subLine)		        
                    for i, arg in enumerate(args):
                        print("    arg {0}: {1}".format(i, arg))
                if kws:
                    print(_str_headerDiv + " Kws... " + _str_headerDiv + _str_subLine)		        
                    for items in kws.items():
                        print("    kw: {0}".format(items))   
                        
                traceback = sys.exc_info()[2]  # get the full traceback
                cgmException(Exception,err,traceback)
            return res
    return wrapper

@Timer
def testTimer(sleep = .5):
    log.info("Sleep time: {0}".format(sleep))
    time.sleep(float(sleep))   # delays for 5 seconds. You can Also Use Float Value.
    return True


@Func
def testFunc(*args,**kws):
    raise Exception,'test'

def getModule(arg):
    mod = inspect.getmodule(arg)
    #log.debug("mod: %s"%mod)
    print mod
    print mod.__name__
    print mod.__name__.split('.')[-1]
    functionTrace+='%s >> ' % mod.__name__.split('.')[-1]
    
def whoami():
    import sys
    return sys._getframe(1).f_code.co_name
def queryCode(v=1):
    import sys
    print 'name'
    pprint.pprint( sys._getframe(v).f_code.co_name)
    print 'varnames'
    pprint.pprint (sys._getframe(v).f_code.co_varnames)
    print 'filename'
    pprint.pprint(sys._getframe(v).f_code.co_filename)
    print 'flags'
    pprint.pprint(sys._getframe(v).f_code.co_flags)
    print 'names'
    pprint.pprint(sys._getframe(v).f_code.co_names)
    print 'locals'
    pprint.pprint(sys._getframe(v).f_code.co_nlocals)
    print 'cell vars'
    pprint.pprint(sys._getframe(v).f_code.co_cellvars)
    print 'free vars'
    pprint.pprint(sys._getframe(v).f_code.co_freevars)
    print 'constants'
    pprint.pprint(sys._getframe(v).f_code.co_consts)      
def callersname():
    import sys
    return sys._getframe(2).f_code.co_name

def cgmExceptionBAK(etype = None, value = None, localDat = None, func = None, module = None, tb = None):
    #if tb is None: tb = sys.exc_info()[2]#...http://blog.dscpl.com.au/2015/03/generating-full-stack-traces-for.html

    print _str_hardLine
    if module:
        print(_str_headerDiv + " Module: {0} ".format(module) + _str_headerDiv )		        
    if func:
        print(_str_headerDiv + " Func: {0} ".format(func) + _str_headerDiv )		    
    
    if localDat:
        print _str_subLine        
        print(_str_headerDiv + " Local " + _str_headerDiv )		
        pprint.pprint(localDat)
    print _str_subLine
    #print "caller: " + callersname()

    if etype:raise etype,value

def func_snapShot(dat = None):
    import sys    
    if dat is None:        
        print("[ {0} ]snapShot || No dat provided".format(sys._getframe(1).f_code.co_name))
        return
    print _str_hardLine
    print(_str_headerDiv + " call: {0}   ".format(sys._getframe(1).f_code.co_name) + _str_headerDiv + _str_subLine)		
    print(_str_headerDiv + " file: {0}".format(sys._getframe(1).f_code.co_filename))
    
    print(_str_headerDiv + " local dat...")
    #sys._getframe(1).f_code.co_name
    pprint.pprint(dat)
    print("..." + _str_headerDiv)
    print _str_hardLine
    
def test_rawValueError(*args,**kws):
    bye = 'fred'
    _l = range(12)
    raise ValueError,"Bob's not home"

def testExceptionNested(*args,**kws):
    try:
        hi = 'mike'
        _nestedDictTest = {1:2,3:4}
        return testException()
    except Exception,err:cgmException(Exception,err)
    
def test_cgmException(*args,**kws):
    try:
        bye = 'fred'
        _l = range(12)
        raise ValueError,"Bob's not home"
    except Exception,err:cgmException(Exception,err)
    
def test_cgmExceptCB(*args,**kws):
    try:
        bye = 'fred'
        _l = range(12)
        raise ValueError,"Bob's not home"
    except Exception,err:cgmExceptCB(Exception,err)
    
def cgmException(etype = None, value = None, tb = None,msg=None,**kws):
    if tb is None: tb = sys.exc_info()[2]#...http://blog.dscpl.com.au/2015/03/generating-full-stack-traces-for.html

    try:db_file = tb.tb_frame.f_code.co_filename
    except:db_file = "<maya console>"
    
    print(_str_headerDiv + " {0}   ".format(tb.tb_frame.f_code.co_name) + _str_headerDiv + _str_subLine)		
    print(" file: {0}".format(db_file))
    
    _d = tb.tb_frame.f_locals

    if 'args' in _d.keys():
        _args = _d.pop('args')
        if _args:
            print("  Args...")
            for a in _args:
                print("      {0}".format(a))
    if 'kws' in _d.keys():
        _kws = _d.pop('kws')
        if _kws:
            print("  KWS...")
            for k,v in _kws.iteritems():
                print("      {0} : {1}".format(k,v))
            
    print("  Local dat...")
    pprint.pprint(_d)
    #pprint.pprint(tb.tb_frame.f_locals)
    if msg:
        print (msg)
    print("..." + _str_headerDiv)
    """
    if value:
        print(_str_headerDiv + " Error log " + _str_headerDiv + _str_subLine)		        
        for i,a in enumerate(value.args):
            print(" {0} : {1}".format(i,a))
            """
    if etype:raise etype,value,tb

cgmExceptCB = cgmException
