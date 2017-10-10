"""
Utility to run a playback equivalent on the current or named file and force
the evaluation manager to rebuild its graph every frame. The graphs are then
compared to see what, if anything, changes between frames.

Ideally the graphs are consistent but there are some cases where differences
arise due to changing dirty propagation for optimization purposes. This
utility will help track those down.

If resultsPath is set then the graph output and differences are dumped to
files using that path as the base name.  For example:

        resultsPath               = MyDirectory/emConsistency_animCone
        graph at frame N  = MyDirectory/emConsistency_animCone_N.eg
        graph comparisons = MyDirectory/emConsistency_animCone_diff.txt

If resultsPath is not set then no output is stored, everything is live.

The return value is always a simple True/False indicating whether all
of the frames in the animation yielded the same graph or not.

If fileName is not set then the current scene is analyzed.

Sample usage to run the tests on a single file:

        from maya.debug.emConsistencyTest import emConsistencyTest
        emConsistencyTest(fileName='MyDirectory/MyFile', resultsPath='MyDirectory/emConsistency_MyFile', doParallel=False)

Sample usage to run the tests on the current scene in parallel mode and ignore output:

        from maya.debug.emConsistencyTest import emConsistencyTest
        emConsistencyTest(doParallel=True)
"""

from maya.debug.graphStructure import graphStructure

def _hasEvaluationManager():
    """
    Check to see if the evaluation manager is available
    """

    pass


def emConsistencyTest(fileName=None, resultsPath=None, doParallel=False, maxFrames=10):
    """
    Run a simulated playback, forcing a rebuild the evaluation manager graph
    every frame and dumping the graph structure into a Python object for
    later comparison.
    
    Compare successive frames, pushing the output to the named resultsPath if
    it was specified. A "_N.eg" suffix is added for the contents of the graph
    at frame "N" and a "_diff.txt" suffix is added for the comparisons between
    the different graphs (with appropriate markers within the file indicating
    which frames are being compared).
    
    If doParallel is set to True then use the EM parallel evaluation mode
    instead of the serial mode. It's less stable at the moment but will
    also allow dumping and comparison of the scheduling graph.
    
    maxFrames is used to define the maximum number of frames to run in the
    playback test. Set it to 0 to indicate that every available frame should
    be used. The playback will run from startFrame to startFrame+maxFrames-1
    
    Returns True if all frames generated the same graph, otherwise False.
    """

    pass


def _testPlayback(outputFile=None, maxFrames=10, resultsPath=None):
    """
    Run a simluated playback sequence. Since Maya has no script-based
    per-frame callback the playback has to be faked by changing the
    current frame and forcing a refresh, for each frame in the playback.
    
    This isn't a precise representation of what playback does but since
    the EM rebuilds the graph on any global time change it should give
    exactly the same results as though it were measured right within a
    playback sequence.
    
    maxFrames indicates the most frames that will be played back.
    Generally speaking the tests should only need a few frames to get an
    accurate picture but you may want more to catch odd conditions. Set
    it to 0 to run all frames specified by the playback options.
    
    If outputFile is set then dump the graph comparison results to that
    file.
    
    If resultsPath is set then the graph outputs will be dumped to a file
    whose base name is that with the suffix "_N.eg" for frame "N".
    """

    pass


def _isMayaFile(fileName):
    pass



EMCONSISTENCY_MAX_FRAMECOUNT = 10


