"""
------------------------------------------
cgm_Meta: cgm.core.test
Author: Ryan Porter
email: ryan.m.porter@gmail.com

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
import time
try:
    import maya.cmds as mc   
    from Red9.core import Red9_Meta as r9Meta
    from cgm.core import cgm_Meta as cgmMeta
    from cgm.core.cgmPy import validateArgs as VALID
    from cgm.core.lib import attribute_utils as ATTR
    #from cgm.core.lib import transform_utils as TRANS
    #from cgm.core.lib import math_utils as MATH
    #from cgm.core import cgm_PuppetMeta as PUPPETMETA
    from cgm.core.mrs import RigBlocks as RBLOCKS
    #from cgm.core.mrs.lib import general_utils as RBLOCKGEN
    
except ImportError:
    raise StandardError('objString test can only be run in Maya')

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)  
    
# CLASSES ====================================================================
class Test_RigBlocks(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_get_from_scene(self):
        _buffer = RBLOCKS.get_from_scene()
        _RigBlock = False
        if not _buffer:
            self.assertEqual(RBLOCKS.get_from_scene(),
                             [])             
            _RigBlock = cgmMeta.createMetaNode('cgmRigBlock',blockType = 'master')
            self.assertEqual(RBLOCKS.get_from_scene(),
                             [_RigBlock])
            _RigBlock.delete()
        else:
            self.assertIsNotNone(_buffer)        
        
    def test_get_modules_dict(self):
        _d_moduleDat = RBLOCKS.get_modules_dat()
        self.assertIsNotNone(_d_moduleDat)
        
    def test_get_blockModule(self):
        self.assertIsNotNone(RBLOCKS.get_blockModule('master'))
        self.assertEqual(RBLOCKS.get_blockModule('okra'),
                         False)          
        #self.assertRaises(ValueError,RBLOCKS.get_blockModule,'okra')
        
    def test_is_buidable(self):
        self.assertIsNot(RBLOCKS.is_buildable('master'),
                         False)
        self.assertEqual(RBLOCKS.is_buildable('okra'),
                         False)  
    def test_is_blockType_valid(self):
        pass

        
    def test_blockTypes(self):
        _l_modulesToTest = ['master','doodad']
        
        for blockType in _l_modulesToTest:
            _t_start = time.clock()
            mBlock = RBLOCKS.cgmRigBlock(blockType = blockType)
            #...initial...
            self.assertEqual(mBlock.blockType,
                             blockType)
            self.assertGreaterEqual(mBlock.getState(False),
                                    1)
            _state = mBlock.getState(False)
            if not RBLOCKS.is_buildable(blockType):
                log.error("[{0}] not a buildable blocktype. FIX")
                continue
            for i in range(_state,4):
                _t_step = time.clock()
                mBlock.changeState(i)
                print("[{0}] Step: {1} complate in {2} seconds".format(blockType, i, "%0.3f"%(time.clock()-_t_step)) + '-'*80) 
            print("[{0}] completed in  {1} seconds".format(blockType, "%0.3f"%(time.clock()-_t_start))) 
    
    
      

       
# FUNCTIONS ==================================================================       
def main(**kwargs):
    #testCases = [Test_r9Issues,]
    
    suite = unittest.TestSuite()

    #for testCase in testCases:
        #suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testCase))

    debug = kwargs.get('debug', False)

    if debug:
        suite.debug()
    else:
        unittest.TextTestRunner(verbosity=2).run(suite)