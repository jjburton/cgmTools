"""
------------------------------------------
cgm_Meta: cgm.core.test.test_coreLib.test_ATTR
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

try:
    import maya.cmds as mc   
    from Red9.core import Red9_Meta as r9Meta
    from cgm.core import cgm_Meta as cgmMeta
    from cgm.core.cgmPy import validateArgs as VALID
    
except ImportError:
    raise StandardError('objString test can only be run in Maya')

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)  
    
# CLASSES ====================================================================
class Test_base(unittest.TestCase):            
    def test_create(self):
        pass
        #raise Exception,'To do...' 
        
class Test_msgList(unittest.TestCase):     
    def test_create(self):
        pass
        #raise Exception,'To do...' 

        
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