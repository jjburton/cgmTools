from cgm.core import cgm_General as cgmGeneral
import cgm.core.tests.test_cgmMeta as cgmMetaTest
import cgm.core.tests.test_coreLib as test_coreLib

def go(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'test_AllTheThings'	
            self._b_autoProgressBar = 1
            self._b_reportTimes = 1
            self._b_pushCleanKWs = 1
            self._b_ExceptionInterupt = False
            self.__dataBind__(*args, **kws)
            self.l_funcSteps = [{'step':'cgmCore','call':self.ut_core},
                                {'step':'cgmMeta','call':self.ut_meta},	                        
                                ]                       
        def ut_meta(self):
            reload(cgmMetaTest)
            cgmMetaTest.main(verbosity = 1)
        def ut_core(self):
            reload(test_coreLib)
            test_coreLib.main(verbosity = 1)
            
            
    return fncWrap(*args, **kws).go()

"""def ut_cgmLibraries(*args, **kws):
    class fncWrap(cgmGeneral.cgmFuncCls):
        '''
        Batch tester for cgm core library of functions
        '''
        def __init__(self,*args, **kws):
            super(fncWrap, self).__init__(*args, **kws)
            self._str_funcName = 'ut_cgmLibraries'	
            self._b_autoProgressBar = 1
            self._b_reportTimes = 1
            self.__dataBind__(*args, **kws)
            self.l_funcSteps = [{'step':'validateArgs','call':test_validateArgs.main},
                                ]
    return fncWrap(*args, **kws).go()"""

