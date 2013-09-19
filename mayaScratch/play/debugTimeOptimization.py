testDebugCalls()
#Trying to see if debug calls get called
import time
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def testDebugCalls(maxTest = 500):
    ifDebug = False
    def logTest():
        _str_funcName = 'logger'
        time_start = time.clock()
        for i,n in enumerate(range(1,maxTest)):
            log.info("log >>> %s"%(pow(n,i)))
        return "%s >> Time >> = %0.3f seconds " % (_str_funcName,(time.clock()-time_start))
    def debugTest():
        _str_funcName = 'debug'
        time_start = time.clock()
        for i,n in enumerate(range(1,maxTest)):
            log.debug("debug >>> %s"%(pow(n,i)))
        return "%s >> Time >> = %0.3f seconds " % (_str_funcName,(time.clock()-time_start))
    def ifDebugTest():
        _str_funcName = 'if debug'
        time_start = time.clock()
        for i,n in enumerate(range(1,maxTest)):
            if log.getEffectiveLevel() == 10:log.debug("debug EFFECTIVELEVEL >>> %s"%(pow(n,i)))
        return "%s >> Time >> = %0.3f seconds " % (_str_funcName,(time.clock()-time_start))
    def printTest():
        _str_funcName = 'print'
        time_start = time.clock()
        for i,n in enumerate(range(1,maxTest)):
            print("print >>> %s"%(pow(n,i)))
        return "%s >> Time >> = %0.3f seconds " % (_str_funcName,(time.clock()-time_start))  
    def calcTest():
        _str_funcName = 'calc'
        time_start = time.clock()
        for i,n in enumerate(range(1,maxTest)):
            x = (pow(n,i))
        return "%s >> Time >> = %0.3f seconds " % (_str_funcName,(time.clock()-time_start))
    
    time_log = logTest()
    time_debug = debugTest()
    time_ifDebug = ifDebugTest()    
    time_print = printTest()
    time_calc = calcTest()
    
    for l in [time_log,time_debug,time_ifDebug,time_print,time_calc]:
        print l
  