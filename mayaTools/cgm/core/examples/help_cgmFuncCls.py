"""
------------------------------------------
cgm.core.examples
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Help for learning the basics of cgmGeneral.cgmFuncCls
================================================================
"""
#==============================================================================================
#>> cgmMeta.cgmAttr
#==============================================================================================
from cgm.core import cgm_General as cgmGeneral
#reload(cgmGeneral)
import maya.cmds as mc


#>>My First FuncCls func =========================================================================
def myFirstFuncCls(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'myFirstFuncCls'	
            self.__dataBind__(*args, **kws)#...this needs to be here
        def __func__(self):
            print 'hello world'
    return fncWrap(*args, **kws).go()

myFirstFuncCls()
myFirstFuncCls(reportTimes = 1)
myFirstFuncCls(printHelp = 1)#...this is a built in that will report registered arg/kw help
myFirstFuncCls(setLogLevel = 'debug')#...hmmm setLogLevel, what's that do...neat. 
#The awesome thing is that when cgmGeneral's log level is set to debug, all functions passing through will inherit that
myFirstFuncCls(reportEnv = 1)#...the maya env report.
myFirstFuncCls(reportShow = 1)#...shows an organized report on what's going on in our function, this will be more intersting later...
#==============================================================================================

#>>My Second FuncCls func =========================================================================
#Let's dig in a little more and make a comparison func to compare some things.
#Say we have two functions we want to see which is faster....
from cgm.core.cgmPy import validateArgs as cgmValid

def mySecondFuncCls(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'mySecondFuncCls'	
            self._str_funcHelp = "This is a comparison func"
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'value',"default":100,"argType":'int'}]	    
            self.__dataBind__(*args, **kws)
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Buffering','call':self._validate_},
                                {'step':'Print Speed no buffer','call':self.test_printSpeedNoBuffer},
                                {'step':'Print Speed w/ buffer','call':self.test_printSpeedBuffer},
                                {'step':'Log Speed no buffer','call':self.test_logSpeedNoBuffer},
                                {'step':'Log Speed w/ buffer','call':self.test_logSpeedBuffer},
                                {'step':'Progress Bar Set','call':self.test_ProgressBarSet},
                                {'step':'Progress Bar Iter','call':self.test_ProgressBarIter}
                                ]
        def _validate_(self):
            self.int_value = int(cgmValid.valueArg(self.d_kws['value'],noneValid=False))
            self.l_valueBuffer = [i for i in range(self.int_value)]
            self.log_debug("Debug in _validate_")
        def test_printSpeedNoBuffer(self):
            for i in range(self.int_value):
                print(i)    	    
        def test_printSpeedBuffer(self):
            for i in self.l_valueBuffer:
                print(i)    
        def test_logSpeedNoBuffer(self):
            for i in range(self.int_value):
                log.info(i)    
        def test_logSpeedBuffer(self):
            for i in self.l_valueBuffer:
                log.info(i)    
        #Let's look at some progress bar stuff
        def test_ProgressBarSet(self):
            self.log_debug("Debug in test_ProgressBarSet")	    
            for i in self.l_valueBuffer:
                self.progressBar_set(status = ("Getting: '%s'"%i), progress = i, maxValue = self.int_value)
        def test_ProgressBarIter(self):
            self.log_debug("Debug in test_ProgressBarIter")	    	    
            self.progressBar_setMaxStepValue(self.int_value)
            for i in range(self.int_value):
                self.progressBar_iter(status = ("Getting: '%s'"%i))
    return fncWrap(*args, **kws).go()

#Before delving in, let's see what we have in terms of new info 
mySecondFuncCls(printHelp = 1)#...this is a built in that will report registered arg/kw help
cgmGeneral.verify_mirrorSideArg(printHelp = 1)#...let's see a real function

#In your script editor, go History>show stack trace, toggle it on and off and try
mySecondFuncCls('cat')#...note the variance in what's reported

mySecondFuncCls(reportShow = 1)#...take a look at how our report is fleshing out more

valueToPass = 50 # set it in one place so we can play around
mySecondFuncCls(valueToPass)
mySecondFuncCls(valueToPass,setLogLevel = 'debug')#...we can set on the fly
mySecondFuncCls(valueToPass,setLogLevel = 'info')#...or set it back
#Note how much faster log is than print, crazy no?
#==============================================================================================



#>>My Third FuncCls func =========================================================================
#Let's get even more advanced and start playing with meta data storing and what not. One huge
#benefit of this it that when we get error reports from users we can get a better snapshot of what
#they were doing and find where things break easier without the benefit of an ide running on users machine
from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as cgmValid

def myThirdFuncCls(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'myThirdFuncCls'	
            self._str_funcHelp = "This is func to expand our learning on cgmFuncCls"
            self._b_reportTimes = 1 #..we always want this on so we're gonna set it on
            self._b_autoProgressBar = True
            self._l_ARGS_KWS_DEFAULTS = [{'kw':'value',"default":10,"argType":'int','help':"How many iterations to do whatever we're going to do"},
                                         {'kw':'testException',"default":False,"argType":'bool','help':"Whether we want to auto throw and exception to test exception report"}]	    
            self.__dataBind__(*args, **kws)
            #Now we're gonna register some steps for our function...
            self.l_funcSteps = [{'step':'Validating Args','call':self._validate_},
                                {'step':'Build stuffs','call':self._buildStuff_}]

        def _validate_(self):
            self.int_value = int(cgmValid.valueArg(self.d_kws['value'],noneValid=False))
            self.l_valueBuffer = [i for i in range(self.int_value)]
            self.b_testException = cgmValid.boolArg(self.d_kws['testException'])
            self.log_debug("Debug in _validate_")
            #For each of our test values, we're gonna create a transform and store it
            self.md_idxToObj = {}
            self.md_shortNameToIdx = {}
            self.log_error("Test error")
            self.log_warning("Test warning")	    
            self.log_toDo("Note to self -- do this sometime")

        def _buildStuff_(self):
            for i in range(self.int_value):
                self.progressBar_set(status = ("Creating obj %s"%i), progress = i, maxValue = self.int_value)
                mi_obj = cgmMeta.cgmObject(name = "TestObj_%s"%i)
                #now we store...
                self.md_idxToObj[i] = mi_obj
                self.md_shortNameToIdx[mi_obj.p_nameShort] = i
                self.log_debug("Just built '%s'"%mi_obj.p_nameShort)
            if self.b_testException:
                self.log_warning("Test exception warning")	    		
                self.log_error("Test exception error")		
                raise Exception,"Just throwing this out there..."
    return fncWrap(*args, **kws).go()

#Before delving in, let's see what we have in terms of new info 
myThirdFuncCls(printHelp = 1)#...we'll look at this one, just to round things out
myThirdFuncCls(reportToDo = 1)#...been playing with a code based to do list

myThirdFuncCls(15)#...let's give it 15
myThirdFuncCls(testException = True)#...Try this with and without stack trace on
myThirdFuncCls(reportShow = 1)#...take a look at how our report is fleshing out more

myThirdFuncCls(10,setLogLevel = 'debug')
myThirdFuncCls(10,setLogLevel = 'info')
#Note how  debug slows things down somewhat
#==============================================================================================
