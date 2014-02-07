"""
------------------------------------------
cgm_Meta: cgm.core.test
Author: Ryan Porter
email: ryan.m.porter@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Unit Tests for the validateArgs.valueArgs function
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
class TestValueArgs(unittest.TestCase):
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
            StandardError,
            validateArgs.valueArg,
            numberToCheck="not_a_number"
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


# FUNCTIONS ==================================================================
def main():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestValueArgs)
    unittest.TextTestRunner(verbosity=2).run(suite)