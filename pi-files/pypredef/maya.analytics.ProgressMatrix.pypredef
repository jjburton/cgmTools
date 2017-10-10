"""
Module containing a simple class object encapsulating an n-dimensional
progress window allowing for generic stepping through the dimensions of
evaluation.

Example for progress walking along a 4x4 matrix:

    progress_object = ProgressMatrix([4,4], 'Matrix iteration', 'Row {0:d}, Column {0:d}' )
    progress_object.start()
    for row in range(0,4):
        for col in range(0,4):
            do_operation(row, col)
            progress_object.report( [row, col] )
    progress_object.end()
"""

class ProgressMatrix(object):
    """
    Class to handle progress reporting for a fixed number of steps. The steps
    are assumed to be n-dimensional and multiplicative, so a list of (L,M,N)
    steps indicates a total of L*M*N steps following a 3-dimensional matrix
    of progress calls.
    
    enable:       True means display the window, else don't do anything
    total_steps:  Number of total steps in the progress operations
    title:        Title of the progress window
    progress_fmt: Format string which includes all of the n-dimensional index
                  values. e.g. 'Row {0:d}, Column {1:d}, Level {2:d}" for the
                  [L,M,N] steps described above
    testing:      True if the object is in testing mode, only reporting
                  results instead of updating an actual window.
    """
    
    
    
    def __init__(self, step_counts, title, progress_fmt):
        """
        step_counts:  List of total counts for each dimension of progress
                      This is the [L,M,N] as described above
        title:        Title of the progress window
        progress_fmt: Progress message format
        """
    
        pass
    
    
    def end(self):
        """
        If the window is enabled close it.
        """
    
        pass
    
    
    def report(self, step_counts):
        """
        If the window is enabled put progress information consisting of the
        percentage done and the formatted progress string.
        
        step_counts: List of counts for each dimension being stepped
        """
    
        pass
    
    
    def start(self):
        """
        Define whether the analytics should put up a progress report window
        or not. If enabled the window will update itself for every analytic
        run on every file.
        
        The completion steps are divided equally at one per analytic per
        file. Progress speed will be uneven since analytics may be skipped
        if already completed, files will take varying amounts of time to
        load, and analytics will take varying amounts of time to run, but
        it's as good an estimate of progress as any.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


import unittest

class TestProgressMatrix(unittest.TestCase):
    """
    Unit tests for the ProgressMatrix object
    """
    
    
    
    def test_1_dimension(self):
        """
        Test the ProgressMatrix object using one dimensional steps
        """
    
        pass
    
    
    def test_2_dimensions(self):
        """
        Test the ProgressMatrix object using two-dimensional steps
        """
    
        pass



TESTING = False


