from unittest.loader import TestLoader
from unittest.loader import findTestCases
from unittest.loader import makeSuite
from unittest.case import expectedFailure
from unittest.runner import TextTestResult
from unittest.runner import TextTestRunner
from unittest.signals import removeResult
from unittest.signals import registerResult
from unittest.signals import removeHandler
from StringIO import StringIO
from unittest.case import SkipTest
from unittest.case import TestCase
from unittest.signals import installHandler
from unittest.case import skip
from unittest.case import FunctionTestCase
from unittest.case import skipIf
from unittest.main import TestProgram as main
from unittest.result import TestResult
from unittest.suite import TestSuite
from unittest.loader import getTestCaseNames
from unittest.case import skipUnless

class SuiteFromModule(TestSuite):
    def __init__(self, module, testImport=True):
        """
        Set testImport to True to have the suite automatically contain a test case that
        checks if we were able to find any tests in the given module.
        """
    
        pass


class TestCaseExtended(TestCase):
    def assertIteration(self, iterable, expectedResults, orderMatters=True, onlyMembershipMatters=False):
        """
        Asserts that the iterable yields the expectedResults.
        
        'expectedResults' should be a sequence of items, where each item matches
        an item returned while iterating 'iterable'.
        
        If onlyMembershipMatters is True, then as long as the results of
        iterable are containined within expectedResults, and every member of
        expectedResults is returned by iterable at least once, the test will
        pass. (Ie, onlyMembershipMatters will override orderMatters.)
        
        If onlyMembershipMatters is False and orderMatters is True, then the
        items in expectedResults should match the order of items returned by the
        iterable.
        
        If onlyMembershipMatters is False and orderMatters is False, the
        assertion will pass as long as there is a one-to-one correspondence
        between the items of expectedResults and the items returned by
        iterable. Note that in this case, duplicate return values from the
        iterable will still need duplicate results in the expectedResults.
        
        Examples:
        
        # orderMatters=True, onlyMembershipMatters=False by default
        
        #################################################
        ## orderMatters=True, onlyMembershipMatters=False
        #################################################
        
        # will PASS
        assertIteration( "foo", ['f', 'o', 'o'])
        
        # will FAIL - last 'o' not present in expectedResults
        assertIteration( "foo", ['f', 'o'])
        
        # will FAIL - 'x' not present in iterable
        assertIteration( "foo", ['f', 'o', 'o', 'x'])
        
        # will FAIL - order incorrect
        assertIteration( "foo", ['o', 'f', 'o'])
        
        #################################################
        
        
        
        #################################################
        ## orderMatters=True, onlyMembershipMatters=True
        #################################################
        
        # will PASS - if onlyMembershipMatters, duplicate entries are ignored
        assertIteration( "foo", ['f', 'o', 'o'], onlyMemberShipMatters=True)
        
        #will PASS
        assertIteration( "foo", ['f', 'o'], onlyMemberShipMatters=True)
        
        #will FAIL - 'o' not present in expectedResults
        assertIteration( "foo", ['f'], onlyMemberShipMatters=True)
        
        # will FAIL - 'x' not present in iterable
        assertIteration( "foo", ['f', 'o', 'x'], onlyMemberShipMatters=True)
        
        # will PASS - order irrelevant
        assertIteration( "foo", ['o', 'f', 'o'], onlyMemberShipMatters=True)
        #################################################
        
        
        
        #################################################
        ## orderMatters=False, onlyMembershipMatters=False
        #################################################
        
        # will PASS
        assertIteration( "foo", ['f', 'o', 'o'], orderMatters=False)
        
        #will FAIL - second 'o' not in expectedResults
        assertIteration( "foo", ['f', 'o'], orderMatters=False)
        
        # will FAIL - 'x' not present in iterable
        assertIteration( "foo", ['f', 'o', 'o', 'x'], orderMatters=False))
        
        # will PASS - order irrelevant
        assertIteration( "foo", ['o', 'f', 'o'], orderMatters=False)
        #################################################
        """
    
        pass
    
    
    def assertNoError(self, function, *args, **kwargs):
        """
        # def addTestFunc(self, function):
        """
    
        pass
    
    
    def assertVectorsEqual(self, v1, v2, places=5):
        pass
    
    
    DO_NOT_LOAD = False


class MayaTestRunner(TextTestRunner):
    def __init__(self, stream='<maya.Output object>', descriptions=True, verbosity=2):
        pass
    
    
    def run(*args, **kwargs):
        pass


class DoctestSuiteFromModule(SuiteFromModule):
    def __init__(self, moduleName, packageRecurse=False, alreadyRecursed=None, **kwargs):
        pass


class UnittestSuiteFromModule(SuiteFromModule):
    def __init__(self, moduleName, suiteFuncName='suite', **kwargs):
        pass



def setupUnittestModule(moduleName, suiteFuncName='suite', testMainName='test_main', filterTestCases='<function startsWithDoubleUnderscore>'):
    """
    Add basic unittest functions to the given module.
    
    Will add a 'suite' function that returns a suite object for the module,
    and a 'test_main' function which runs the suite.
    
    If a filterTestCases function is given, then this is applied to all objects in the module which
    inherit from TestCase, and if it returns true, removes them from the module dictionary,
    so that they are not automatically loaded.
    
    By default, it will filter all TestCases whose name starts with a double-underscore, ie
    '__AbstractTestCase'
    
    Will then call 'test_main' if moduleName == '__main__'
    """

    pass


def setCompare(iter1, iter2):
    """
    Compares two groups of objects, returning the sets:
        onlyIn1, inBoth, onlyIn2
    """

    pass


def permutations(sequence, length=None):
    """
    Given a sequence, will return an iterator over the possible permutations.
    
    If length is 'None', the permutations will default to having the same length
    as the sequence; otherwise, the returned permtuations will have the given length.
    
    Note that every element in the sequence is considered unique, so that there may be
    'duplicate' permutations if there are duplicate elements in seq, ie:
    
    perumutations("aa") -> ['a', 'a'] and ['a', 'a']
    """

    pass


def addFuncToModule(func, module):
    pass


def suite():
    pass


def warn(*args, **kwargs):
    """
    Issue a warning, or maybe ignore it or raise an exception.
    """

    pass


def doctestmod(*args, **kwargs):
    pass


def startsWithDoubleUnderscore(testcase):
    pass


def doctestobj(*args, **kwargs):
    pass


def isOneToOne(dict):
    """
    Tests if the given dictionary is one to one (if dict[x]==dict[y], x==y)
    """

    pass


def doctestFriendly(func):
    """
    Decorator which prepares maya to run doctests.
    """

    pass


def isEquivalenceRelation(inputs, outputs, dict):
    """
    Tests if the given dictionary defines an equivalence relation from between inputs and outputs.
    
    Technically, tests if the dict is bijective: ie, one-to-one (if dict[x]==dict[y], x==y) and
    onto (for every y in outputs, exists an x such that dict[x] == y)
    """

    pass



SUITE_FUNC_NAME = 'suite'

defaultTestLoader = None

TEST_MAIN_FUNC_NAME = 'test_main'


