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
    from cgm.core import cgm_General as cgmGEN
    
except ImportError:
    raise StandardError('objString test can only be run in Maya')

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)  
    
# CLASSES ====================================================================
class Test_r9Issues(unittest.TestCase):
    def setUp(self):
        self.r9Node1 = r9Meta.MetaClass(name = 'net',nodeType = 'network')
    
    def tearDown(self):
        self.r9Node1.delete()
        
        #return 'ok'
        
    def test_caching(self):
        self.assertEquals(self.r9Node1.cached,None,)
        
        self.r9Node1.addAttr('mClass','MetaClass')
        r9Node1Cached = r9Meta.MetaClass(self.r9Node1.mNode)
        
        self.assertEquals(self.r9Node1.cached,True)
        self.assertEquals(self.r9Node1,r9Node1Cached)
        
    def test_duplicate(self):
        self.r9Node1_dup = r9Meta.MetaClass(mc.duplicate(self.r9Node1.mNode)[0])        
        self.assertNotEqual(self.r9Node1,self.r9Node1_dup)
        self.r9Node1_dup.delete()


class Test_general(unittest.TestCase):   
    def test_mClassConversion_r9(self):
        n1 = cgmMeta.cgmNode(name='test_setClass',nodeType = 'transform')
        self.assertEqual(type(n1),cgmMeta.cgmNode)
        
        n1 = r9Meta.convertMClassType(n1,'cgmObject')
        self.assertEqual(type(n1),cgmMeta.cgmObject)
        
        n1 = r9Meta.convertMClassType(n1,'cgmControl')
        self.assertEqual(type(n1),cgmMeta.cgmControl)
        
        n1 = r9Meta.convertMClassType(n1,'MetaClass')
        self.assertEqual(type(n1),r9Meta.MetaClass)
        
        n1.delete()
        
    def test_mClassConversion_cgm(self):
        _str_grp = mc.group(em=True)		
        
        n1 = cgmMeta.cgmNode(_str_grp)
        n1 = r9Meta.convertMClassType(n1,'cgmControl')
        
        self.assertEqual(type(n1),cgmMeta.cgmControl)
        
        n1 = cgmMeta.validateObjArg(n1.mNode,'cgmObject',setClass = True)
        self.assertEqual(type(n1),cgmMeta.cgmObject)
        
        n1 = cgmMeta.validateObjArg(n1.mNode,'cgmControl',setClass = True)
        self.assertEqual(type(n1),cgmMeta.cgmControl)
        
        
        n1.delete() 
        
    def test_validateObjArg(self):
        null = mc.group(em=True)    
        i_node = cgmMeta.cgmNode(nodeType='transform')
        i_obj = cgmMeta.cgmObject(nodeType='transform')

        
        self.assertRaises(
            ValueError,
            cgmMeta.validateObjArg,
            arg=None
        )          
        
        self.assertEqual(i_obj, cgmMeta.validateObjArg(i_obj.mNode))#...string arg
        self.assertEqual(i_obj, cgmMeta.validateObjArg(i_obj))#...intance arg
        
        i_obj = cgmMeta.validateObjArg(i_obj.mNode,'cgmObject',setClass=True)
        self.assertEqual(issubclass(type(i_obj),cgmMeta.cgmObject), True)#...String + mType
        
        self.assertEqual(i_obj, cgmMeta.validateObjArg(i_obj,'cgmObject'))#...Instance + mType 

        self.assertEqual(issubclass(type(cgmMeta.validateObjArg(null)),cgmMeta.cgmNode),True)#...null string failed

        i_null = cgmMeta.validateObjArg(null,'cgmObject')
        
        self.assertEqual(issubclass(type(i_null),cgmMeta.cgmObject),True)#..."Null as cgmObject

        _objs = [mc.joint(), mc.group(em=True), mc.createNode('multiplyDivide',name='multiplyDivideValideObjArg')]
        for i,obj in enumerate(_objs):
            if i == 2:
                self.assertRaises(ValueError,
                                  cgmMeta.validateObjArg,
                                  obj,'cgmObject')
                mc.delete(obj)
                                  
                #issubclass(type(n1),cgmMeta.cgmNode),True, type(n1))
            else:
                n1 = cgmMeta.validateObjArg(obj,'cgmObject')                
                self.assertEqual(issubclass(type(n1),cgmMeta.cgmObject),True, type(n1))
                n1.delete()  
            
    def test_validateObjListArg(self):
        pass
    
    def test_createMetaNode(self):
        _r9ClassRegistry = r9Meta.getMClassMetaRegistry()
        _l_mask = ['cgmBlendShape','cgmBufferNode',
                   'cgmPuppet','cgmDynParentGroup','cgmDynamicMatch',#RESOLVE ASAP
                   'cgmMorpheusPuppet',
                   'cgmInfoNode2','cgmModuleBufferNode','cgmTest',
                   'cgmMasterControl',
                   'cgmEyeballBlock','cgmMouthNoseBlock','cgmEyebrowBlock',
                   #...these pass but don't need
                   'cgmNodeOLD','cgmEyelids','cgmMouthNose','cgmEyebrow','cgmSimpleBSFace','cgmEyeball','cgmObjectOLD']
        #for mType in ['cgmNode','cgmObject','cgmControl','cgmObjectList']:
        for mType in _r9ClassRegistry.keys():
            if 'cgm' in mType and mType not in _l_mask:
                _t_start = time.clock()
                try:
                    mObj = cgmMeta.createMetaNode(mType,name = 'createTest_{0}'.format(mType))
                except Exception,err:
                    log.error("{0} failure...".format(mType))
                    for arg in err.args:
                        log.error(arg)  
                    #log.error(cgmGEN._str_subLine)
                    raise Exception,err
                
                self.assertEqual(issubclass(type(mObj),_r9ClassRegistry[mType]),True, mObj)
                mObj.delete()   
                print("[{0}] completed in  {1} seconds".format(mType, "%0.3f"%(time.clock()-_t_start))) 
                
            
        
class Test_NameFactory(unittest.TestCase):
    pass

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