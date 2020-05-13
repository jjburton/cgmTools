"""
------------------------------------------
cgm_Meta: cgm.core.test
Author: Ryan Porter (edited by Josh Burton)
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
    import cgm.core.cgmPy.validateArgs as validateArgs
    #reload(validateArgs)
    import cgm.core.lib.shared_data as SHARED
    #reload(SHARED)
    import maya.cmds as mc
    
except ImportError:
    raise StandardError('objString test can only be run in Maya')

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)  
    
# CLASSES ====================================================================
class Test_boolArg(unittest.TestCase):
    def test_true(self):
        self.assertTrue(
            validateArgs.boolArg(True),
            "validateArgs.boolArg did not return True for True"
        )

    def test_false(self):
        self.assertFalse(
            validateArgs.boolArg(False),
            "validateArgs.boolArg did not return False for False"
        )

    def test_zero(self):
        self.assertFalse(
            validateArgs.boolArg(0),
            "validateArgs.boolArg did not return False for 0"
        )

    def test_one(self):
        self.assertTrue(
            validateArgs.boolArg(1),
            "validateArgs.boolArg did not return True for 1"
        )

    def test_noneBoolArg(self):
        arg = 3.14

        self.assertRaises(
            StandardError,
            validateArgs.boolArg,
            arg
        )
        
class Test_stringArg(unittest.TestCase):
    '''
    TestCase for validateArgs.stringArgs
    '''
    def test_string(self):
        '''
        Confirm that the function will return the same value if 
        it is passed a string or unicode.
        '''
        arg = "CGMonks"

        self.assertEqual(
            validateArgs.stringArg(arg, noneValid=True), 
            arg,
            "validateArgs.stringArgs did not return the string "+\
            "it was passed when noneValid=True")

        self.assertEqual(
            validateArgs.stringArg(arg, noneValid=False), 
            arg,
            "validateArgs.stringArgs did not return the string "+\
            "it was passed when noneValid=False")

    def test_unicode(self):
        uArg = u"CGMonks"

        self.assertEqual(
            validateArgs.stringArg(uArg, noneValid=True), 
            uArg,
            "validateArgs.stringArgs did not return the unicode "+\
            "it was passed when noneValid=True")

        self.assertEqual(
            validateArgs.stringArg(uArg, noneValid=False), 
            uArg,
            "validateArgs.stringArgs did not return the unicode "+\
            "it was passed when noneValid=False")

    def test_nonStringValidTrue(self):
        '''
        Confirm that the function will return false if the value passed
        is not a string but noneValid is set to True.
        '''
        self.assertFalse(
            validateArgs.stringArg(None, noneValid=True),
            "validateArgs.stringArgs did not return False "+\
            "when passed a nont-string value when noneValid=True"
        )

    def test_nonStringNoneValidFalse(self):
        '''
        Confirm that the function will raise a StandardError
        if it is passed a non-string value and noneValid is False.
        '''
        arg = 3.141
        type_ = type(arg).__name__
        self.assertRaises(
            StandardError,
            validateArgs.stringArg,
            arg, 
            noneValid=False, 
        )
"""
class BaseMayaObjTestCase(unittest.TestCase):
    def setUp(self):
        self.maya_obj = mc.createNode('transform', name='test_node')

    def tearDown(self):
        mc.delete(self.maya_obj)"""

class Test_objStringUniqueName(unittest.TestCase):
    def setUp(self):
        self.maya_obj = mc.createNode('transform', name='test_node')
        left_parent = mc.createNode('transform', name='left', parent=self.maya_obj)
        right_parent = mc.createNode('transform', name='right', parent=self.maya_obj)
        left_child = mc.createNode('transform', name='child', parent=left_parent)
        right_child = mc.createNode('transform', name='child', parent=right_parent)

    def tearDown(self):
        mc.delete(self.maya_obj)

    def runTest(self):
        self.assertRaises(
            StandardError,
            validateArgs.objString,
            "child"
        )

class Test_objStringArguments(unittest.TestCase):
    def test_errorIfArgIsList(self):
        self.assertRaises(
            StandardError,
            validateArgs.objString,
            arg=[1,2]
        )

    def test_errorIfArgIsNoneOrFalse(self):
        self.assertRaises(
            StandardError,
            validateArgs.objString,
            arg=None
        )

        self.assertRaises(
            StandardError,
            validateArgs.objString,
            arg=False
        )


class Test_objStringExists(unittest.TestCase):
    def test_errorIfNotObjExists(self):
        self.assertRaises(
            StandardError,
            validateArgs.objString,
            arg="does_not_exist"
        )

    def test_falseIfNotObjExistsAndNoneValid(self):
        self.assertFalse(
            validateArgs.objString(arg="does_not_exist",
                                   noneValid=True),
            "validateArgs.objString did not return false when the object "+\
            "did not exist and noneValid was set to True"
        )

class test_objStringMayaType(unittest.TestCase):
    def setUp(self):
        self.maya_obj = mc.createNode('multiplyDivide')

    def tearDown(self):
        mc.delete(self.maya_obj)

    def test_errorIfWrongMayaType(self):
        self.assertRaises(
            StandardError,
            validateArgs.objString,
            arg=self.maya_obj,
            mayaType='plusMinusAverage'
        )

    def test_falseIfWrongMayaTypeNoneValid(self):
        self.assertFalse(
            validateArgs.objString(
                arg=self.maya_obj,
                mayaType='plusMinusAverage',
                noneValid=True
            )
        )

    def test_passIfRightMayaType(self):
        self.assertEquals(
            validateArgs.objString(
                arg=self.maya_obj,
                mayaType='multiplyDivide'
            ),
            self.maya_obj
        )

class Test_objStringIsTransform(unittest.TestCase):
    def setUp(self):
        self.maya_obj = mc.createNode('transform', name='test_node')
        self.nonTransform = mc.createNode('multiplyDivide')

    def tearDown(self):
        mc.delete(self.maya_obj)
        mc.delete(self.nonTransform)

    def test_errorIfNotTransform(self):
        self.assertRaises(
            StandardError,
            validateArgs.objString,
            arg=self.nonTransform, 
            isTransform=True
        )

    def test_falseIfNotTransformNoneValid(self):
        print "test_falseIfNotTransformNoneValid"
        self.assertFalse(
            validateArgs.objString(
                arg=self.nonTransform,
                isTransform=True,
                noneValid=True
            )
        )

    def test_passIfIsTransform(self):
        self.assertTrue(
            validateArgs.objString(
                arg=self.maya_obj,
                isTransform=True
            ),
            self.maya_obj
        )
        
class Test_valueArgs(unittest.TestCase):
    def test_simpleInt(self):
        '''
        Confirm that the function will return the same value if 
        it is passed an int.
        '''
        arg = 1

        self.assertEqual(
            validateArgs.valueArg(arg, noneValid=True), 
            arg,
            "validateArgs.valueArg did not return the arg "+\
            "it was passed when noneValid=True")

        self.assertEqual(
            validateArgs.valueArg(arg, noneValid=False), 
            arg,
            "validateArgs.valueArg did not return the arg "+\
            "it was passed when noneValid=False")
        
    def test_simpleFloat(self):
        '''
        Confirm that the function will return the same value if 
        it is passed an int.
        '''
        arg = 1.999999

        self.assertEqual(
            validateArgs.valueArg(arg, noneValid=True), 
            arg,
            "validateArgs.valueArg did not return the arg "+\
            "it was passed when noneValid=True")

        self.assertEqual(
            validateArgs.valueArg(arg, noneValid=False), 
            arg,
            "validateArgs.valueArg did not return the arg "+\
            "it was passed when noneValid=False")
        
    
    def test_numberIsNoneRaisesError(self):
        self.assertRaises(
            StandardError,
            validateArgs.valueArg,
            numberToCheck=None,
            noneValid= False,
        )

    def test_numberIsNotNumberRaisesError(self):
        self.assertRaises(
            TypeError,
            validateArgs.valueArg,
            numberToCheck="not_a_number",
            noneValid = False,
        )

    # def test_invalidRangeRaisesError(self):
    #     self.assertRaises(
    #         StandardError,
    #         validateArgs.valueArg,
    #         numberToCheck=42,
    #         inRange=['dont', 'panic']
    #     )

    def test_numberNotInRangeLow(self):
        self.assertFalse(
            validateArgs.valueArg(
                numberToCheck=42,
                inRange=[44,99]
            )
        )

    def test_numberNotInRangeHigh(self):
        self.assertFalse(
            validateArgs.valueArg(
                numberToCheck=42,
                inRange=[0,41]
            )
        )

    # def test_minValueRaisesError(self):
    #     self.assertRaises(
    #         StandardError,
    #         validateArgs.valueArg,
    #         numberToCheck=42,
    #         minValue="towel"
    #     )

    def test_minValueNoAutoClamp(self):
        self.assertFalse(
            validateArgs.valueArg(
                numberToCheck=42,
                minValue=71,
                autoClamp=False
            )
        )

    # def test_maxValueRaisesError(self):
    #     self.assertRaises(
    #         StandardError,
    #         validateArgs.valueArg,
    #         numberToCheck=42,
    #         maxValue="towel"
    #     )

    def test_maxValueNoAutoClamp(self):
        self.assertFalse(
            validateArgs.valueArg(
                numberToCheck=42,
                maxValue=27,
                autoClamp=False
            )
        )

    # def test_isValueRaisesError(self):
    #     self.assertRaises(
    #         StandardError,
    #         validateArgs.valueArg,
    #         numberToCheck=42,
    #         isValue="salmon"
    #     )

    def test_isValueNotEqual(self):
        self.assertFalse(
            validateArgs.valueArg(
                numberToCheck=42,
                isValue=-42
            )
        )

    # def test_isEquivalentRaisesError(self):
    #     self.assertRaises(
    #         StandardError,
    #         validateArgs.valueArg,
    #         numberToCheck=42,
    #         isEquivalent="trout"
    #     )

    def test_isEquivalentNotEqual(self):
        self.assertFalse(
            validateArgs.valueArg(
                numberToCheck=42,
                isEquivalent=4.2
            )
        )
        
# CLASSES ====================================================================
class Test_simpleAxis(unittest.TestCase):
    '''
    TestCase for validateArgs.stringArgs
    '''
    def test_axisToStrings(self):
        for k,v in SHARED._d_axis_string_to_vector.iteritems():
            self.assertEqual(validateArgs.simpleAxis(k).p_vector,
                             v)
            
        for k,v in SHARED._d_axis_string_to_vector.iteritems():
            self.assertEqual(validateArgs.simpleAxis(v).p_string,
                             k)        
            
    def test_vectorToAxis(self):
        for k,v in SHARED._d_axis_vector_to_string.iteritems():
            self.assertEqual(validateArgs.simpleAxis(k).p_string,
                             v)  

        
        
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