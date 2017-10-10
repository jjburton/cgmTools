"""
Utiity to run a set of performance tests on files in a directory and report
the results in a CSV file for graphing.

Sample usage to run the tests on a bunch of files in a directory and show
progress as the tests are run:

    from maya.debug.emPerformanceTest import emPerformanceTest
    from maya.debug.emPerformanceTest import emPerformanceOptions as emo
    options = emo()
    options.setViewports( emo.VIEWPORT_2 )
    options.setReportProgress( True )
    emPerformanceTest(['MyDirectory'], resultsFileName='MyDirectory/emPerformance.csv', options)

It tries to be intelligent about defaults for resultsFileName - if a single
directory was specified in the locations parameter then the output is sent to
that directory with the file name "emPerformance.csv". Otherwise it defaults
to the same file name in the current working directory.

Results are posted in seconds for a single evaluation (min, max, and/or
average times when mutiple frames are evaluated).
"""

from maya.debug.emModeManager import emModeManager
from maya.debug.TODO import TODO

class emPerformanceOptions(object):
    """
    Simple holder class to manage all of the test run options in a single
    location. All of the members are orthogonal : they all specify a new
    set of combinations in which to run the others.
    
        iterationCount   : Number of iterations per playback/refresh (default 3).
                           Refresh uses 10x this number to get more consistent results.
    
        allColumns       : If True then only include file name and timing columns.
                           Excludes min/max, file load/new times, and playback range.
    
        reportProgress   : If True then put up a dialog window showing test run progress.
                           Will not affect the timing results. It also
                           provides a button that will let you terminate the
                           test run early if it turns out to be taking too long.
    
        evalModes        : List of modes to run (EVALUATION_MODE_XX)
                            EVALUATION_MODE_DG            Regular Maya DG Evaluation
                            EVALUATION_MODE_EM_SERIAL    Evaluation Manager serial mode
                            EVALUATION_MODE_EM_PARALLEL    Evaluation Manager parallel mode
    
        testTypes        : List of test types to run (TEST_TYPE_XX)
                            TEST_PLAYBACK        Run a playback (max 50 frames)
                            TEST_DIRTY            Dirty all before a refresh
                            TEST_REFRESH        Do refresh without dirty in between
                            TEST_DIRTY_REFRESH    Do refresh with dirty in between
    
        viewports        : List of viewports in which to run (VIEWPORT_X)
                            VIEWPORT_1            Run tests in original viewport
                            VIEWPORT_2            Run tests in VP2 (OGS)
    
    Total number of tests run will be:
        len(evalModes) * len(testTypes) * len(viewports)
    """
    
    
    
    def __init__(self):
        """
        #----------------------------------------------------------------------
        """
    
        pass
    
    
    def columnTitles(self):
        """
        Build the list of column titles defined by the currently active options.
        """
    
        pass
    
    
    def setAllColumns(self, newAllColumns):
        """
        Toggles the amount of data that will appear in the output CSV file.
        If turned off then only the bare minimum will be included:
            Name of File
            Timing Rate for each mode
        Noticeably omitted are start/end of playback ranges (if requested),
        file load and new times, and min/max timing.
        
        When you just want local comparisons of simple timing then turn
        this mode off. Full runs that will be backed up to databases should
        keep it on.
        """
    
        pass
    
    
    def setEvalModes(self, newEvalModes):
        """
        Define the evaluation modes to be used for the test runs. Valid values are:
            emPerformanceOptions.EVALUATION_MODE_DG
            emPerformanceOptions.EVALUATION_MODE_EM_SERIAL
            emPerformanceOptions.EVALUATION_MODE_EM_PARALLEL
        You can pass in a single value or a list of values.
        """
    
        pass
    
    
    def setIterationCount(self, newIterationCount):
        """
        Set the number of iterations that the playback will do in order to get
        a reasonable average. Refresh will do 10x this number since it is so
        much faster (i.e. equivalent to 10 frames of playback)
        """
    
        pass
    
    
    def setReportProgress(self, newReportProgress):
        """
        Turn on or off reporting of progress. When on the test run will put up
        a dialog indicating how much work is done and how much is lest. The
        dialog is updated outside of timing tests to it will not influence
        results.  It also provides a button that will let you terminate the
        test run early if it turns out to be taking too long.
        """
    
        pass
    
    
    def setTestTypes(self, newTestTypes):
        """
        Define the test types to be used for the test runs. Valid values are:
            emPerformanceOptions.TEST_PLAYBACK
            emPerformanceOptions.TEST_REFRESH
            emPerformanceOptions.TEST_DIRTY
            emPerformanceOptions.TEST_DIRTY_REFRESH
        You can pass in a single value or a list of values.
        """
    
        pass
    
    
    def setViewports(self, newViewports):
        """
        Define the viewports to be used for the test runs. Valid values are:
            emPerformanceOptions.VIEWPORT_1
            emPerformanceOptions.VIEWPORT_2
        You can pass in a single value or a list of values.
        """
    
        pass
    
    
    def usesEvaluationManager(self):
        """
        Check to see if any of the active modes use the EM
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    EVALUATION_MODE_DG = 'DG'
    
    
    EVALUATION_MODE_EM_PARALLEL = 'EMP'
    
    
    EVALUATION_MODE_EM_SERIAL = 'EMS'
    
    
    TEST_DIRTY = 'Dirty'
    
    
    TEST_DIRTY_REFRESH = 'Dirty Refresh'
    
    
    TEST_GRAPH_CREATION = 'Graph Creation'
    
    
    TEST_GRAPH_SCHEDULING = 'Graph Scheduling'
    
    
    TEST_PLAYBACK = 'Playback'
    
    
    TEST_REFRESH = 'Refresh'
    
    
    VIEWPORT_1 = 'VP1'
    
    
    VIEWPORT_2 = 'VP2'


class progressState(object):
    """
    Helper class that manages the information relevant to the progress window.
        enable                : Turn on the window
        fileCount            : Total number of files to be processed
        currentFileName        : Name of file currently being processed
        progressPerFile        : Percentage of the whole (0-1) each file takes
        totalProgress        : Current total progress (0-1)
        currentFile            : Current file number
        currentPhase        : Current phase number
        currentPhaseName    : Name of the current phase
        progressPerPhase    : Percentage of the whole (0-1) each phase takes
                              Should be <= progressPerFile since a file will
                              consist of one or more phases.
    """
    
    
    
    def __del__(self):
        """
        Close the progress window if it was opened
        """
    
        pass
    
    
    def __init__(self, fileCount, phaseCount, enable):
        """
        Initialize all of the progress information and open the window if requested
        """
    
        pass
    
    
    def aborting(self):
        """
        Call this when looping through the phases if you want to allow
        cancellation of tests at any particular time.
        """
    
        pass
    
    
    def reportProgress(self):
        """
        If the window is enabled put progress information consisting of the
        percentage done, the current file, and the current phase
        """
    
        pass
    
    
    def startFile(self, newFileName):
        """
        Checkpoint a new file is starting
        """
    
        pass
    
    
    def startPhase(self, phaseName):
        """
        Checkpoint a new phase of the performance run is starting
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class emPerformanceRun(object):
    """
    Utility class to facilitate various types of performance timing.
    
    # Sample to run and gather playback results for two files
    timing = emPerformanceRun( fileName=file1, refresh=False )
    timing.runTests()
    print timing.columnTitles()
    print timing.columns()
    
    timing = emPerformanceRun( fileName=file2, refresh=False )
    timing.runTests()
    print timingResults.columns()
    
        fileNam        : Name of file on which to run the tests
                      If None then use the current file
        options        : Options for running the tests
        progress    : Progress object for reporting current status
    """
    
    
    
    def __init__(self, fileName=None, options=None, progress=None):
        """
        Nothing to initialize for the timing tester
        """
    
        pass
    
    
    def columnTitles(self):
        """
        Get the CSV titles given the types of timing test requested.
        """
    
        pass
    
    
    def columns(self):
        """
        Get the CSV columns with timing information from the types of timing test requested.
        """
    
        pass
    
    
    def runTests(self):
        """
        Run the tests specified by the options
        """
    
        pass
    
    
    def setEvaluationMode(self, newMode):
        """
        Helper to switch evaluation modes. Handles DG evaluation and both
        serial and parallel evaluation manager modes. Degrades gracefully
        when the evaluation manager is not present.
        """
    
        pass
    
    
    def testDirtyRefresh(self):
        """
        Force a refresh "iterationCount" times to get an overall average.
        Dump all of the results into a emPerformanceResults class and return it.
        Unlike testRefresh() this method dirties the entire DG before each
        refresh to force the maximum evaluation.
        
            Returns emPerformanceResults object where timing will be stored
        """
    
        pass
    
    
    def testPlayback(self):
        """
        Run a playback sequence, repeating 'iterationCount' times to get an overall average.
        Dump all of the results into the object's emPerformanceResults member.
        
            For EM modes returns a 3-tuple of emPerformanceResults object where timing will be stored
                1. Timing for evaluation graph creation (0 in DG mode) - 1 repetition
                2. Timing for scheduling graph creation (0 in DG mode) - 1 repetition
                3. Timing for playback - self.options.iterationCount repetitions
            For DG mode just returns the third element of the tuple.
        
        In the EM modes there is a bootstrapping process for evaluation that
        works as follows:
            - First frame of animation is used to build the evaluation graph
            - Second frame of animation is used to build the scheduling graph
            - Third frame of animation may be used to clean up any uninitialized caches in some scenes
        
        We want to separate the timing of the graph creation with the
        playback. The graph creation is a one-time cost whereas the playback
        is a repeating cost. Keeping these times separate lets us distinguish
        between per-frame evaluation speed and startup cost.
        """
    
        pass
    
    
    def testRefresh(self):
        """
        Force a refresh "iterationCount" times to get an overall average.
        Dump all of the results into a emPerformanceResults class and return it.
        It dirties everything once before starting so that refresh has
        a consistent place to start, but the first refresh is not measured.
        
            Returns emPerformanceResults object where timing will be stored
        """
    
        pass
    
    
    def testTheType(self, theTestType):
        """
        Simple redirect function to allow iteration over test modes
        """
    
        pass
    
    
    def timingColumns(self, results):
        """
        Return the list of average, min, and max timing information from the
        results object passed in.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class emPerformanceResults(object):
    """
    Utility class to hold results of emPerformance runs of all types.
    Mostly used to print out results but can also be used to store
    them for later use and/or reformatting.
    """
    
    
    
    def __init__(self):
        """
        Clear out the current results
        """
    
        pass
    
    
    def averageTime(self):
        """
        Calculate the average time of all the repetitions.
        """
    
        pass
    
    
    def endRep(self, rep):
        """
        Finish a repetition, storing the timing data
        """
    
        pass
    
    
    def reset(self):
        """
        Clear out the current results
        """
    
        pass
    
    
    def startRep(self, rep):
        """
        Start a repetition, initializing the timing data
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    RepData = None



def switchMayaViewport(newMode):
    """
    Helper to switch viewport modes. Only handles VP1 or VP2.
    """

    pass


def evaluationManagerExists():
    """
    Check to see if the evaluation manager is available
    """

    pass


def findMayaFiles(directory):
    """
    Search a directory and return a list of all Maya files beneath it
    """

    pass


def emPerformance(filesAndDirectories=None, resultsFileName=None, iterationCount=3, modes=None, testTypes=None, viewports=None, verbose=False):
    """
    Same as emPerformanceTest but the options separated into different
    arguments. Legacy support.
    
        filesAndDirectories : List of locations in which to find Maya files to test
        resultsFileName     : Location of results.  Default is stdout.
                              Also correctly interprets the names 'stderr',
                              'cout', and 'cerr', plus if you use the
                              destination 'csv' it will return a Python list
                              of the CSV data.
    
    See the emPerformanceOptions class for a description of the other args.
    """

    pass


def emPerformanceTest(filesAndDirectories=None, resultsFileName=None, options=None):
    """
    Run a set of performance tests on files in a directory and report
    the results in a CSV file for graphing.
    
        filesAndDirectories : List of locations in which to find Maya files to test
        resultsFileName     : Location of results.  Default is stdout.
                              Also correctly interprets the names 'stderr',
                              'cout', and 'cerr', plus if you use the
                              destination 'csv' it will return a Python list
                              of the CSV data.
        options             : Set of options being used for the test run. See
                              the emPerformanceOptions class for details.
    
    The selected test types are run a number of times, collecting the min,
    max, and average timing. The stats dumped will depend on the options
    member 'allColumns'.
    
    The CSV file will contain timing information in several columns. Only the
    columns matching the requested flags are output. Every file found is put
    into its own row (so be careful about interpreting directories containing
    referenced files):
    
        File                    Name of the file being tested
        Load                    Load time
        New                        Time to do a "file -f -new"
        Start Frame                Start frame of the playback used by the file
        End Frame                End frame of the playback used by the file
        ...followed by multiple columns as selected in the format:
            VP MODE TYPE STAT
    
            VP        =    "VP1" or "VP2", for the viewport being tested
            MODE    =    "DG" for Maya evaluation
                        "EMP" for Evaluation Manager Parallel
                        "EMS" for Evaluation Manager Serial
            TYPE    =    "Playback" for timing of a playback sequence
                        "Refresh" for timing of simple refresh repeated
                        "Dirty Refresh" for timing of refresh after 'dgdirty -a'
            STAT    =    "Avg" for the average timing of all iterations
                        "Min" for the shortest timing over all iterations
                        "Max" for the longest timing over all iterations
    """

    pass


def isMayaFile(potentialMayaFile):
    """
    Check to see if a given file is a valid Maya file
    """

    pass



EMPERFORMANCE_PLAYBACK_MAX = 50


