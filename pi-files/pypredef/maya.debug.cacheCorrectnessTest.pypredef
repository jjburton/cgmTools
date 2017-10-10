"""
Utility to verify that the background evaluation and caching system are
yielding the same results as the Maya parallel evaluation.

It is a simple wrapper around run_correctness_test().  See its documentation
for more details.

Sample usage to run the tests on a single file:

    from maya.debug.cacheCorrectnessTest import cacheCorrectnessTest
    cacheErrors = cacheCorrectnessTest(fileName='MyDir/MyFile.ma', resultsPath='MyDir/cacheCorrectness', modes=[['transform', 'mesh', 'curves']])

Sample usage to run the tests on the current scene and ignore output:

    from maya.debug.cacheCorrectnessTest import cacheCorrectnessTest
    cacheErrors = cacheCorrectnessTest(modes=[['transform', 'mesh', 'curves']])
"""

from maya.debug.correctnessUtils import run_correctness_test
from maya.debug.TODO import TODO

class CacheEvaluatorContext(object):
    """
    This class configures the cache evaluator according to a set of options.
    
    It enables the evaluator for a given set of nodes.  The supported values are:
    - 'transform' : to enable the evaluator on transforms and derived types.
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, type, value, traceback):
        pass
    
    
    def __init__(self, mode, cacheTimeout):
        pass
    
    
    def getEvaluationCache(types):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class CacheCorrectnessMode(object):
    """
    This class represents a mode to be tested in cache correctness tests.
    
    It knows about the cache mode (i.e. what caching point to be enabled).
    
    It always requires the same evaluation mode:
    - Parallel evaluation
    - Cache evaluator enabled
    """
    
    
    
    def __init__(self, cacheMode, cacheTimeout):
        pass
    
    
    def getContext(self):
        """
        Returns the context object that will set up and tear down the required
        caching configuration to be tested.
        """
    
        pass
    
    
    def getEmMode(self):
        """
        Returns the evaluation mode in which the cache correctness test must
        be run, which is the same for all tests:
        - Parallel evaluation
        - Cache evaluator enabled
        """
    
        pass
    
    
    def getTitle(self):
        """
        Returns the identifying string for this cache mode.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def getModeString(mode):
    """
    Returns the identifying string for this cache mode, which is just the
    list of activated options separated by a '+' sign.
    """

    pass


def cacheCorrectnessTest(fileName=None, resultsPath=None, verbose=False, modes=[['transform', 'mesh', 'curves']], maxFrames=200, dataTypes=['matrix', 'vertex', 'screen'], emSetup=0, cacheTimeout=1800):
    """
    Evaluate the file in multiple caching modes and compare the results.
    
    fileName:     See fileName parameter in run_correctness_test.
    resultsPath:  See resultsPath parameter in run_correctness_test.
    verbose:      See verbose parameter in run_correctness_test.
    modes:        List of modes to run the tests in.  A mode is a list of options to activate
                  in the cache system.  The only valid ones are:
                  transform: caches transforms
                  mesh: caches meshes
                  curves: caches NURBS curves
                  meshOnlyVP2: activates VP2 mesh caching
    maxFrames:    See maxFrames parameter in run_correctness_test.
    dataTypes:    See dataTypes parameter in run_correctness_test.
    emSetup:      See emSetup parameter in run_correctness_test.
    cacheTimeout: The maximum amount of time to wait for cache to fill.
    
    Returns the output of run_correctness_test().
    """

    pass



CORRECTNESS_NO_SETUP = 0

CORRECTNESS_MAX_FRAMECOUNT = 200

CACHE_TIMEOUT = 1800


