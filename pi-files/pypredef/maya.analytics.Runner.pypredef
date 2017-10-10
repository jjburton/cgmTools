"""
File containing class that handles the process of running analytics,
including management of the options for running.
"""

from maya.analytics.ObjectNamer import ObjectNamer
from maya.analytics.ProgressMatrix import ProgressMatrix
from maya.analytics.Logger import Logger
from maya.analytics.utilities import analytic_by_name
from maya.analytics.utilities import list_analytics
from maya.analytics.maya_file_generator import get_maya_files
from maya.analytics.maya_file_generator import maya_file_generator

class Runner(object):
    """
    Class containing information required to run analytics, including
    options and temporary state information.
    
    Class Members You Can Set
    {
        analytics      : List of names of all analytics to be run.
                         Default: [] (run all available analytics)
        descend        : If True then for all directories that are included in
                         "paths" also include all of the subdirectories below them.
                         Default: True
        force          : If True run the analytic even if up-to-date results exist.
                         Default: False
        return_json    : If True then return all JSON results from the analytics,
                         aggregated by indexing them on the file and analytic name.
                         Use with caution as long runs can make this string huge.
                         Default: False
        list_only      : True means list the analytics to be run and the files to
                         run them on without actually running the analytic.
                         Return value will be a dictionary of {FILE, [ANALYTICS]}
                         Default: False
        paths          : List of paths on which to run the analytics. If
                         any elements are directories they will be walked
                         to find matching files. Use in conjunction with
                         "descend" to find all files below a root directory.
                         Default: []
        report_progress: If True then put up a progress report dialog while
                         running. This works for the list_only mode as well
                         since that too could take some time on a large tree.
                         Default: False
        results_path   : If specified then dump the analytics with this
                         directory as the root. Otherwise use the subdirectory
                         "MayaAnalytics" in the same directory as the file(s)
                         Default: None
        skip           : List of file patterns to ignore when walking directories.
                         e.g. ".mb$" to ignore all Maya Binary files, or
                         "/reference/" to ignore everything in the subdirectory
                         named "reference". Forward-slash separator is assumed.
                         Default: []
        static         : If True then run the Static analytics, otherwise run the
                         scene-based analytics. When Static analytics are run
                         if "paths" are specified a ValueError exception is
                         raised.
                         Default: False
        logger       : Message output destination.
                         Default: message object pointing to stdout
    }
    
    Analytic Options, used here and/or passed in to analytics
    Add new options by calling Runner.set_option( 'name', 'value' )
    {
        summary:    Include a summary of the output (usually a list of counts)
                    Default: False
        details:    Include full details in the output.
                    Default: False
        anonymous : True if identifying information is to be made
                    anonymous. At the top level this will include file
                    and directory names, for example, output the path
                    "dir1/dir2/file1.ma" instead of "scene1/shot2/dinosaur.ma"
                    Individual analytics may add other anonymizers, for
                    example anonymizing the names of nodes.
                    Default: False.
    }
    
    Simple example for running the "evalManager" analytic on all files below
    directory "/Volumes/animFiles/filesToAnalyze", dumping the output in the
    sibling directory "/Volumes/animFiles/filesToAnalyze_MayaAnalytics".
    
        import maya.analytics.Runner as Runner
        runner = Runner()
        runner.analytics = ['EvalManager']
        runner.paths = ['/Volumes/animFiles/filesToAnalyze']
        runner.results_path = '/Volumes/animFiles/filesToAnalyze_MayaAnalytics'
        runner.report_progress = True
        runner.run()
    """
    
    
    
    def __init__(self):
        """
        Start out the analytic options with all defaults
        """
    
        pass
    
    
    def __str__(self):
        """
        Pretty-print the current options
        """
    
        pass
    
    
    def run(self):
        """
        Run analytics as appropriate based on the options present.
        
        Analytics will return JSON result information to be stored in a file
        named "ANALYTIC.json" and may also create other files they can name
        themselves (e.g. ANALYTIC.png for a screenshot).
        
        Timing information for running the analytic and, if required, loading
        the file are appended to the JSON output data.
        """
    
        pass
    
    
    def set_option(self, option_name, option_value):
        """
        Define a new option for analytics to use. All analytics being run
        use the same set of options so put the union of options in here before
        running.
        
        "summary", "details", and "anonymous", are common boolean options on
        all analytics and already present. Other options can be any data type
        you wish but the analytic is responsible for accessing it.
        
        The safe way for analytics to extract options is to override the
        analytic's set_options() method, look for the option(s) of interest,
        and set a class variable based on the option settings for use
        during the analytic's run.
        
        option_name:  Name of option to pass along
        option_value: Current value of the option
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



