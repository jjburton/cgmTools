"""
------------------------------------------
cgm_Meta: cgm.core.test.test_coreLib.test_PATH
Author: Josh Burton
email: jjburton@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Unit Tests for the validateArgs.objString function
================================================================
"""
# IMPORTS ====================================================================
import unittest
import logging
import unittest.runner
import maya.standalone
import os

try:
    import maya.cmds as mc   
    
except ImportError:
    raise StandardError('objString test can only be run in Maya')
import cgm.core.cgmPy.path_Utils as PATH
import cgm.core.cgmPy.os_Utils as cgmOS

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)  
    
# CLASSES ====================================================================
class Test_cgmOS(unittest.TestCase):            
    def test_queries(self):
        self.assertIsNotNone(cgmOS.get_module_data(__file__))      
        
class Test_Path(unittest.TestCase):            
    def test_queries(self):
        import cgm
        _dir = PATH.Path(cgm.__path__[0])
        _file = os.path.join(_dir.up(),'cgmToolbox.py')
        
        self.assertEquals(os.path.exists(_dir),True)
        self.assertEquals(os.path.exists(_file),True)
        
        self.assertEquals(_file.isFile(),True)
        self.assertEquals(_file.asFile().endswith('cgmToolbox.py'),
                          True)
    
    def hold(self):
        pass
        
        
    def test_walk(self):
        import cgm.core as CORE
        _test = PATH.Path(CORE.__path__[0])
        for root,dirs,files in os.walk(_test,True,True):
            pass      


        
# FUNCTIONS ==================================================================       
"""def main(**kwargs):
    #testCases = [Test_r9Issues,]
    
    suite = unittest.TestSuite()

    #for testCase in testCases:
        #suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testCase))

    debug = kwargs.get('debug', False)

    if debug:
        suite.debug()
    else:
        unittest.TextTestRunner(verbosity=2).run(suite)"""