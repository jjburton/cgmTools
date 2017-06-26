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

try:
    import maya.cmds as mc   
    from Red9.core import Red9_Meta as r9Meta
    from cgm.core import cgm_Meta as cgmMeta
    from cgm.core.cgmPy import validateArgs as VALID
    from cgm.core.lib import attribute_utils as ATTR
    #from cgm.core.lib import transform_utils as TRANS
    #from cgm.core.lib import math_utils as MATH
    from cgm.core import cgm_PuppetMeta as PUPPETMETA
    
except ImportError:
    raise StandardError('objString test can only be run in Maya')

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)  
    
# CLASSES ====================================================================
class Test_cgmPuppet(unittest.TestCase):
    def setUp(self):
        try:
            self.mi_puppet = PUPPETMETA.cgmPuppet('cgmPuppetTesting_puppetNetwork')
        except:
            self.mi_puppet = cgmMeta.createMetaNode('cgmPuppet',name = 'cgmPuppetTesting')
            
    def test_a_network(self):
        mPuppet = self.mi_puppet
        
        self.assertEqual(issubclass(type(mPuppet),PUPPETMETA.cgmPuppet),
                         True)
        
        try:mPuppet._UTILS
        except Exception,error:
            raise Exception,"No _Utils found | error: {0}".format(error)     
        
        self.assertEqual(mc.nodeType(mPuppet.mNode), 'network')
        
        #Attrs -----------------------------------------------------------------------------------------
        puppetDefaultValues = {'cgmName':['string','cgmPuppetTesting'],
                               'cgmType':['string','puppetNetwork'],
                               'mClass':['string','cgmPuppet'],
                               'version':['double',1.0],
                               'masterNull':['message',[u'cgmPuppetTesting']],
                               'font':['string','Arial'],
                               'axisAim':['enum',2],
                               'axisUp':['enum',1],
                               'axisOut':['enum',0]}                                   
    
        for attr in puppetDefaultValues.keys():
            try:
                self.assertEqual(ATTR.has_attr(mPuppet.mNode, attr),
                                 True, attr)
                self.assertEqual(ATTR.get_type(mPuppet.mNode, attr),
                                 puppetDefaultValues.get(attr)[0])            
                self.assertEqual(ATTR.get(mPuppet.mNode, attr),
                                 puppetDefaultValues.get(attr)[1])#"{0} value test fail".format(attr) 
            except Exception,err:
                print "{0} attr failed...".format(attr)
                for arg in err:
                    log.error(arg)
                raise Exception,err        
        
        
            
    def test_b_masterNull(self):
            mPuppet = self.mi_puppet
            mMasterNull = mPuppet.masterNull
            
            self.assertEqual(mPuppet.masterNull.puppet.mNode,
                             mPuppet.mNode,'mNode walk...')
            self.assertEqual(mPuppet.masterNull.puppet,
                             mPuppet,'meta walk...')
            
            masterDefaultValues = {'cgmType':['string','ignore'],
                                   'cgmModuleType':['string','master']}                                   
    
            for attr in masterDefaultValues.keys():
                try:
                    self.assertEqual(ATTR.has_attr(mMasterNull.mNode, attr),
                                     True, attr)
                    self.assertEqual(ATTR.get_type(mMasterNull.mNode, attr),
                                     masterDefaultValues.get(attr)[0])            
                    self.assertEqual(ATTR.get(mMasterNull.mNode, attr),
                                     masterDefaultValues.get(attr)[1])#"{0} value test fail".format(attr) 
                except Exception,err:
                    print "{0} attr failed...".format(attr)
                    for arg in err:
                        log.error(arg)
                    raise Exception,err
    
      

       
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