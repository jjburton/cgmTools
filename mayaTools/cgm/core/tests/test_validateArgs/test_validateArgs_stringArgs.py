"""
------------------------------------------
cgm_Meta: cgm.core.test
Author: Ryan Porter
email: ryan.m.porter@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Unit Tests for the validateArgs.stringArgs function
================================================================
"""
# IMPORTS ====================================================================
import unittest
import logging

import cgm.core.cgmPy.validateArgs as validateArgs
reload(validateArgs)

# LOGGING ====================================================================
log = logging.getLogger(__name__.split('.')[-1])
log.setLevel(logging.INFO)

# CLASSES ====================================================================
class TestStringArgs(unittest.TestCase):
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



# FUNCTIONS ==================================================================
def main():
    suite = unittest.defaultTestLoader.loadTestsFromModule(__name__)
    unittest.TextTestRunner(verbosity=2).run(suite)