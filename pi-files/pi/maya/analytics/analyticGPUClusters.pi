from maya.analytics.analyticGPUDeformers import *

from . import BaseAnalytic as _BaseAnalytic

class analyticGPUClusters(_BaseAnalytic.BaseAnalytic):
    """
    Analyze the usage mode of cluster node.
    """
    
    
    
    def run(self):
        """
        Examine animated cluster nodes and check how they are used.  It checks
        whether they are used for fixed rigid transform, weighted rigid transform
        or per-vertex-weighted transform.
        
        When the 'details' option is set the CSV columns are:
            ClusterNode         : Name of the animated cluster node
            envelope_is_static : True if the envelope is not animated and its value is 1
            uses_weights         : True if weights are used in the node
            uses_same_weight      : True if weight is the same for all vertices
            Mode                : Mode for this node
            supported_geometry   : True if the geometry processed by animated cluster node
                                  is supported by deformer evaluator
        
        otherwise the CSV columns are:
            ClusterMode        : Description of the usage for the animated cluster node
            Mode               : Mode for animated cluster nodes meeting this criteria
            supported_geometry  : True if the geometry processed by animated cluster nodes
                                 meeting this criteria is supported by deformer evaluator
            Count              : Number of animated cluster nodes in this mode
        
            See is_supported_geometry() for what criteria a geometry must meet to be supported.
        
        One row is output for every animated cluster node.
        
        The "Mode" is an integer value with the following meaning:
        - 1 => Rigid transform          : cluster node only performs a rigid transform
        - 2 => Weighted rigid transform : cluster node performs a rigid transform, but it
                                          is weighted down by a factor
        - 3 => Per-vertex transform     : cluster node computes a different transform for
                                          each individually-weighted vertex
        
        Return True if the analysis succeeded, else False
        """
    
        pass
    
    
    def help():
        """
        Call this method to print the class documentation, including all methods.
        """
    
        pass
    
    
    ANALYTIC_NAME = 'GPUClusters'
    
    
    __fulldocs__ = 'Analyze the usage mode of cluster node.\nBase class for output for analytics.\n\nThe default location for the anlaytic output is in a subdirectory\ncalled \'MayaAnalytics\' in your temp directory. You can change that\nat any time by calling set_output_directory().\n\nClass static member:\n     ANALYTIC_NAME : Name of the analytic\n\nClass members:\n     directory     : Directory the output will go to\n     is_static     : True means this analytic doesn\'t require a file to run\n     logger        : Logging object for errors, warnings, and messages\n     plug_namer    : Object creating plug names, possibly anonymous\n     node_namer    : Object creating node names, possibly anonymous\n     csv_output    : Location to store legacy CSV output\n     plug_namer    : Set by option \'anonymous\' - if True then make plug names anonymous\n     node_namer    : Set by option \'anonymous\' - if True then make node names anonymous\n     __options     : List of per-analytic options\n\n\tMethods\n\t-------\n\tdebug : Utility to standardize debug messages coming from analytics.\n\n\terror : Utility to standardize errors coming from analytics.\n\n\testablish_baseline : This is run on an empty scene, to give the analytic a chance to\n\t                     establish any baseline data it might need (e.g. the nodes in an\n\t                     empty scene could all be ignored by the analytic)\n\t                     \n\t                     Base implementation does nothing. Derived classes should call\n\t                     their super() method though, in case something does get added.\n\n\thelp : Call this method to print the class documentation, including all methods.\n\n\tjson_file : Although an analytic is free to create any set of output files it\n\t            wishes there will always be one master JSON file containing the\n\n\tlog : Utility to standardize logging messages coming from analytics.\n\n\tmarker_file : Returns the name of the marker file used to indicate that the\n\t              computation of an analytic is in progress. If this file remains\n\t              in a directory after the analytic has run that means it was\n\t              interrupted and the data is not up to date.\n\t              \n\t              This file provides a safety measure against machines going down\n\t              or analytics crashing.\n\n\tname : Get the name of this type of analytic\n\n\toption : Return TRUE if the option specified has been set on this analytic.\n\t         option: Name of option to check\n\n\toutput_files : This is used to get the list of files the analytic will generate.\n\t               There will always be a JSON file generated which contains at minimum\n\t               the timing information. An analytic should override this method only\n\t               if they are adding more output files (e.g. a .jpg file).\n\t               \n\t               This should only be called after the final directory has been set.\n\n\trun : Examine animated cluster nodes and check how they are used.  It checks\n\t      whether they are used for fixed rigid transform, weighted rigid transform\n\t      or per-vertex-weighted transform.\n\t      \n\t      When the \'details\' option is set the CSV columns are:\n\t          ClusterNode         : Name of the animated cluster node\n\t          envelope_is_static : True if the envelope is not animated and its value is 1\n\t          uses_weights         : True if weights are used in the node\n\t          uses_same_weight      : True if weight is the same for all vertices\n\t          Mode                : Mode for this node\n\t          supported_geometry   : True if the geometry processed by animated cluster node\n\t                                is supported by deformer evaluator\n\t      \n\t      otherwise the CSV columns are:\n\t          ClusterMode        : Description of the usage for the animated cluster node\n\t          Mode               : Mode for animated cluster nodes meeting this criteria\n\t          supported_geometry  : True if the geometry processed by animated cluster nodes\n\t                               meeting this criteria is supported by deformer evaluator\n\t          Count              : Number of animated cluster nodes in this mode\n\t      \n\t          See is_supported_geometry() for what criteria a geometry must meet to be supported.\n\t      \n\t      One row is output for every animated cluster node.\n\t      \n\t      The "Mode" is an integer value with the following meaning:\n\t      - 1 => Rigid transform          : cluster node only performs a rigid transform\n\t      - 2 => Weighted rigid transform : cluster node performs a rigid transform, but it\n\t                                        is weighted down by a factor\n\t      - 3 => Per-vertex transform     : cluster node computes a different transform for\n\t                                        each individually-weighted vertex\n\t      \n\t      Return True if the analysis succeeded, else False\n\n\tset_options : Modify the settings controlling the run operation of the analytic.\n\t              Override this method if your analytic has some different options\n\t              available to it, but be sure to call this parent version after since\n\t              it sets common options.\n\n\tset_output_directory : Call this method to set a specific directory as the output location.\n\t                       The special names \'stdout\' and \'stderr\' are recognized as the\n\t                       output and error streams respectively rather than a directory.\n\n\twarning : Utility to standardize warnings coming from analytics.\n'
    
    
    is_static = False



