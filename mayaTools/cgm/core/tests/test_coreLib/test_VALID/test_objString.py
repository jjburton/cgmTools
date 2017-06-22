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

try:
    from maya import cmds
except ImportError:
    raise StandardError('objString test can only be run in Maya')

import cgm.core.cgmPy.validateArgs as validateArgs
reload(validateArgs)

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)

# CLASSES ====================================================================
class BaseMayaObjTestCase(unittest.TestCase):
    def setUp(self):
        self.maya_obj = cmds.createNode('transform', name='test_node')

    def tearDown(self):
        cmds.delete(self.maya_obj)

class TestObjStringUniqueName(unittest.TestCase):
    def setUp(self):
        self.maya_obj = cmds.createNode('transform', name='test_node')
        left_parent = cmds.createNode('transform', name='left', parent=self.maya_obj)
        right_parent = cmds.createNode('transform', name='right', parent=self.maya_obj)
        left_child = cmds.createNode('transform', name='child', parent=left_parent)
        right_child = cmds.createNode('transform', name='child', parent=right_parent)

    def tearDown(self):
        cmds.delete(self.maya_obj)

    def runTest(self):
        self.assertRaises(
            StandardError,
            validateArgs.objString,
            "child"
        )

class TestObjStringArguments(unittest.TestCase):
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


class TestObjStringExists(unittest.TestCase):
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

class TestObjStringMayaType(unittest.TestCase):
    def setUp(self):
        self.maya_obj = cmds.createNode('multiplyDivide')

    def tearDown(self):
        cmds.delete(self.maya_obj)

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

class TestObjStringIsTransform(unittest.TestCase):
    def setUp(self):
        self.maya_obj = cmds.createNode('transform', name='test_node')
        self.nonTransform = cmds.createNode('multiplyDivide')

    def tearDown(self):
        cmds.delete(self.maya_obj)
        cmds.delete(self.nonTransform)

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

# FUNCTIONS ==================================================================
def main(**kwargs):
    testCases = [
        TestObjStringUniqueName,
        TestObjStringArguments,
        TestObjStringExists,
        TestObjStringMayaType,
        TestObjStringIsTransform
    ]

    suite = unittest.TestSuite()

    for testCase in testCases:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testCase))

    debug = kwargs.get('debug', False)

    if debug:
        suite.debug()
    else:
        unittest.TextTestRunner(verbosity=2).run(suite)