
# IMPORTS ====================================================================
import unittest
import unittest.runner
import maya.standalone

import logging
import time

import cgm.core.cgm_General as cgmGEN
import cgm.core.cgmPy.path_Utils as PATH
import cgm.core.cgmPy.validateArgs as VALID

import maya.cmds as mc

def sceneSetup():
    try:mc.file(new=True,f=True)
    except Exception,err:
        log.error("New File fail!")
        for arg in err.args:
            log.error(arg)                
        raise Exception,err  

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)
#_d_moduleRoots = {'cgmMeta':"cgm.core.tests.test_cgmMeta.test",


_d_modules = {'cgmMeta':['base','mClasses','PuppetMeta'],
              'coreLib':['PATH','ATTR','VALID','NODEFACTORY'],
              'MRS':['RigBlocks']}
_l_all_order = ['coreLib','cgmMeta','MRS']


def main(tests = 'all', verbosity = 1, testCheck = False, **kwargs):	
    """
    Core test runner for us.
    
    :parameters:
        tests(list): Str list of tests to be run. Should be in data lists above in the module. 'all' will run all found tests.
        verbosity(int): 1,2
        testCheck(bool): If True, no tests will run it will just collect the list so you can see what would have run

    """   
    v = verbosity
    
    tests = VALID.listArg(tests)
    
    _l_testModules = []
    _d_testModulePaths = {}
    _d_tests = {}
    
    #...gather up our tests and paths...
    if tests == ['all']:
        log.info("testing all")
        for m in _l_all_order:
            #log.info(m)
            _tests = _d_modules.get(m,False)
            for t in _tests:
                _key = "{0}.{1}".format(m,t)                
                _l_testModules.append(t)
                _d_testModulePaths[t] = "test_{0}.test_{1}".format(m,t)                    
    else:
        for t in tests:
            for k,l in _d_modules.iteritems():
                if t == k:
                    for t2 in l:
                        _key = "{0}.{1}".format(k,t2)                        
                        _l_testModules.append(_key)
                        _d_testModulePaths[_key] = "test_{0}.test_{1}".format(k,t2)                        
                if t in l:
                    _key = "{0}.{1}".format(k,t)
                    _l_testModules.append(_key)
                    _d_testModulePaths[_key] = "test_{0}.test_{1}".format(k,t)
    
    #cgmGEN.log_info_dict(_d_testModulePaths)
    
    if not _l_testModules:
        raise ValueError,"No modules detected to test. Test arg: {0}".format(tests)
    
    #....meat of it...
    if testCheck is not True:
        import cgm
        cgm.core._reload() 
        sceneSetup()
        

    _t_start = time.clock()
    _len_all = 0    
    
    print(cgmGEN._str_hardBreak)
    for mod in _l_testModules:
            suite = unittest.TestSuite()
            module = "cgm.core.tests.{0}".format(_d_testModulePaths[mod])
            print(">>> Testing: {0} | {1}".format(mod,module) + '-'*100)		
    
            try:
                exec("import {0}".format(module))
                exec("reload({0})".format(module))
            except Exception,err:
                log.error("New File fail!")
                for arg in err.args:
                    log.error(arg)                
                raise Exception,err		
    
            tests = unittest.defaultTestLoader.loadTestsFromName(module)
            suite.addTest( tests)		
            if testCheck is not True:
                unittest.TextTestRunner(verbosity=v).run(suite)
    
            #print("Tests: ")
            for t in tests:
                for t2 in t:
                    if v == 1:
                        _class = t2.__class__.__name__.split('Test_')[-1]
                        _test = t2._testMethodName.split('test_')[-1]
                        print( "    > " + "{0} | {1}".format(_class,_test) )
                    _len_all += 1
            #print(cgmGEN._str_subLine)
            if testCheck is not True:
                print("<<< Module complete : {0} | {1} ...".format(mod,format(module)))		
        
    if testCheck is not True:
        print("Completed [{0}] tests in [{1}] modules >> Time >> = {2} seconds".format(_len_all, len(_l_testModules), "%0.3f"%(time.clock()-_t_start))) 
        cgmGEN.report_enviornmentSingleLine()
    else:
        print("Found [{0}] tests in [{1}] modules >> Test check mode. No tests run".format(_len_all, len(_l_testModules)))
        
    print(cgmGEN._str_hardBreak)	






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

