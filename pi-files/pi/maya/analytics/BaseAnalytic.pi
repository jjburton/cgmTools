from maya.analytics.ObjectNamer import ObjectNamer

class BaseAnalytic(object):
    """
    Base class for output for analytics.
    
    The default location for the anlaytic output is in a subdirectory
    called 'MayaAnalytics' in your temp directory. You can change that
    at any time by calling set_output_directory().
    
    Class static member:
         ANALYTIC_NAME : Name of the analytic
    
    Class members:
         directory     : Directory the output will go to
         is_static     : True means this analytic doesn't require a file to run
         logger        : Logging object for errors, warnings, and messages
         plug_namer    : Object creating plug names, possibly anonymous
         node_namer    : Object creating node names, possibly anonymous
         csv_output    : Location to store legacy CSV output
         plug_namer    : Set by option 'anonymous' - if True then make plug names anonymous
         node_namer    : Set by option 'anonymous' - if True then make node names anonymous
         __options     : List of per-analytic options
    """
    
    
    
    def __init__(self):
        """
        Start out the analytic with no data and pointing to stdout
        """
    
        pass
    
    
    def debug(self, msg):
        """
        Utility to standardize debug messages coming from analytics.
        """
    
        pass
    
    
    def error(self, msg):
        """
        Utility to standardize errors coming from analytics.
        """
    
        pass
    
    
    def establish_baseline(self):
        """
        This is run on an empty scene, to give the analytic a chance to
        establish any baseline data it might need (e.g. the nodes in an
        empty scene could all be ignored by the analytic)
        
        Base implementation does nothing. Derived classes should call
        their super() method though, in case something does get added.
        """
    
        pass
    
    
    def json_file(self):
        """
        Although an analytic is free to create any set of output files it
        wishes there will always be one master JSON file containing the
        """
    
        pass
    
    
    def log(self, msg):
        """
        Utility to standardize logging messages coming from analytics.
        """
    
        pass
    
    
    def marker_file(self):
        """
        Returns the name of the marker file used to indicate that the
        computation of an analytic is in progress. If this file remains
        in a directory after the analytic has run that means it was
        interrupted and the data is not up to date.
        
        This file provides a safety measure against machines going down
        or analytics crashing.
        """
    
        pass
    
    
    def name(self):
        """
        Get the name of this type of analytic
        """
    
        pass
    
    
    def option(self, option):
        """
        Return TRUE if the option specified has been set on this analytic.
        option: Name of option to check
        """
    
        pass
    
    
    def output_files(self):
        """
        This is used to get the list of files the analytic will generate.
        There will always be a JSON file generated which contains at minimum
        the timing information. An analytic should override this method only
        if they are adding more output files (e.g. a .jpg file).
        
        This should only be called after the final directory has been set.
        """
    
        pass
    
    
    def set_options(self, options):
        """
        Modify the settings controlling the run operation of the analytic.
        Override this method if your analytic has some different options
        available to it, but be sure to call this parent version after since
        it sets common options.
        """
    
        pass
    
    
    def set_output_directory(self, directory):
        """
        Call this method to set a specific directory as the output location.
        The special names 'stdout' and 'stderr' are recognized as the
        output and error streams respectively rather than a directory.
        """
    
        pass
    
    
    def warning(self, msg):
        """
        Utility to standardize warnings coming from analytics.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    ANALYTIC_NAME = 'Unknown'



OPTION_SUMMARY = 'summary'

OPTION_ANONYMOUS = 'anonymous'

OPTION_DETAILS = 'details'


