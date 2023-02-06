"""
------------------------------------------
cgm_Meta: cgm.core.test.test_coreLib.test_PATH
Author: Josh Burton
email: cgmonks.info@gmail.com

Website : https://github.com/jjburton/cgmTools/wiki
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
    raise Exception('objString test can only be run in Maya')
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
        
        self.assertTrue(issubclass(type(_dir.up()),str))
        _file = PATH.Path(os.path.join(_dir.up().asString(),'cgmToolbox.py'))
        
        self.assertEqual(os.path.exists(_dir),True)
        self.assertEqual(os.path.exists(_file),True)
        
        self.assertEqual(_file.isFile(),True)
        self.assertEqual(_file.asFile().endswith('cgmToolbox.py'),
                          True)
    
    def hold(self):
        pass
        
        
    def test_walk(self):
        import cgm.core as CORE
        _test = PATH.Path(CORE.__path__[0])
        for root,dirs,files in os.walk(_test.asString(),True,True):
            #print(root)
            for d in dirs:
                #print(d)
                for f in files:
                    print(f)


        
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