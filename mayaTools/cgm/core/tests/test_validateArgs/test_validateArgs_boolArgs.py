"""
------------------------------------------
cgm_Meta: cgm.core.test
Author: Ryan Porter
email: ryan.m.porter@gmail.com

Website : http://www.cgmonks.com
------------------------------------------

Unit Tests for the validateArgs.boolArgs function
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
class TestBoolArgs(unittest.TestCase):
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



# FUNCTIONS ==================================================================
def main():
    suite = unittest.defaultTestLoader.loadTestsFromModule(__name__)
    unittest.TextTestRunner(verbosity=2).run(suite)