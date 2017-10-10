from maya.analytics.decorators import addHelp
from maya.analytics.BaseAnalytic import BaseAnalytic
from maya.analytics.decorators import makeAnalytic
from maya.analytics.decorators import addMethodDocs
from maya.debug.emModeManager import emModeManager

class analyticGPUDeformers(BaseAnalytic):
    """
    Analyze the usage mode of deformer nodes.
    """
    
    
    
    def run(self):
        """
        Examine animated deformers nodes and check how they are used.
        
        If the 'details' option is set the CSV columns are:
            DeformerNode      : Name of the animated deformer node
            Type              : Type for this node
            SupportedGeometry : True if the geometry processed by animated
                                deformer node is supported by deformer evaluator
        
        otherwise the CSV columns are:
            DeformerMode       : Description of the usage for the animated deformer node
            Type               : Deformer type
            SupportedGeometry  : True if the geometry processed by animated
                                 deformer nodes is supported by deformer evaluator
            Count              : Number of animated deformer nodes in this mode
        
            See is_supported_geometry() for what criteria a geometry must meet to be supported.
        
        One row is output for every animated deformer node.
        
        Return True if the analysis succeeded, else False
        """
    
        pass
    
    
    def help():
        """
        Call this method to print the class documentation, including all methods.
        """
    
        pass
    
    
    def is_supported_geometry(geometry):
        """
        Checks if the geometry is supported by deformer evaluator.
        
        For it to be supported, it must:
            1) Be a mesh
            2) Not have a connected output
            3) Have at least k vertices, where k=2000 on NVidia hardware (hard-coded value)
        """
    
        pass
    
    
    ANALYTIC_NAME = 'GPUDeformers'
    
    
    __fulldocs__ = "Analyze the usage mode of deformer nodes.\nBase class for output for analytics.\n\nThe default location for the anlaytic output is in a subdirectory\ncalled 'MayaAnalytics' in your temp directory. You can change that\nat any time by calling set_output_directory().\n\nClass static member:\n     ANALYTIC_NAME : Name of the analytic\n\nClass members:\n     directory     : Directory the output will go to\n     is_static     : True means this analytic doesn't require a file to run\n     logger        : Logging object for errors, warnings, and messages\n     plug_namer    : Object creating plug names, possibly anonymous\n     node_namer    : Object creating node names, possibly anonymous\n     csv_output    : Location to store legacy CSV output\n     plug_namer    : Set by option 'anonymous' - if True then make plug names anonymous\n     node_namer    : Set by option 'anonymous' - if True then make node names anonymous\n     __options     : List of per-analytic options\n\n\tMethods\n\t-------\n\tdebug : Utility to standardize debug messages coming from analytics.\n\n\terror : Utility to standardize errors coming from analytics.\n\n\testablish_baseline : This is run on an empty scene, to give the analytic a chance to\n\t                     establish any baseline data it might need (e.g. the nodes in an\n\t                     empty scene could all be ignored by the analytic)\n\t                     \n\t                     Base implementation does nothing. Derived classes should call\n\t                     their super() method though, in case something does get added.\n\n\thelp : Call this method to print the class documentation, including all methods.\n\n\tis_supported_geometry : Checks if the geometry is supported by deformer evaluator.\n\t                        \n\t                        For it to be supported, it must:\n\t                            1) Be a mesh\n\t                            2) Not have a connected output\n\t                            3) Have at least k vertices, where k=2000 on NVidia hardware (hard-coded value)\n\n\tjson_file : Although an analytic is free to create any set of output files it\n\t            wishes there will always be one master JSON file containing the\n\n\tlog : Utility to standardize logging messages coming from analytics.\n\n\tmarker_file : Returns the name of the marker file used to indicate that the\n\t              computation of an analytic is in progress. If this file remains\n\t              in a directory after the analytic has run that means it was\n\t              interrupted and the data is not up to date.\n\t              \n\t              This file provides a safety measure against machines going down\n\t              or analytics crashing.\n\n\tname : Get the name of this type of analytic\n\n\toption : Return TRUE if the option specified has been set on this analytic.\n\t         option: Name of option to check\n\n\toutput_files : This is used to get the list of files the analytic will generate.\n\t               There will always be a JSON file generated which contains at minimum\n\t               the timing information. An analytic should override this method only\n\t               if they are adding more output files (e.g. a .jpg file).\n\t               \n\t               This should only be called after the final directory has been set.\n\n\trun : Examine animated deformers nodes and check how they are used.\n\t      \n\t      If the 'details' option is set the CSV columns are:\n\t          DeformerNode      : Name of the animated deformer node\n\t          Type              : Type for this node\n\t          SupportedGeometry : True if the geometry processed by animated\n\t                              deformer node is supported by deformer evaluator\n\t      \n\t      otherwise the CSV columns are:\n\t          DeformerMode       : Description of the usage for the animated deformer node\n\t          Type               : Deformer type\n\t          SupportedGeometry  : True if the geometry processed by animated\n\t                               deformer nodes is supported by deformer evaluator\n\t          Count              : Number of animated deformer nodes in this mode\n\t      \n\t          See is_supported_geometry() for what criteria a geometry must meet to be supported.\n\t      \n\t      One row is output for every animated deformer node.\n\t      \n\t      Return True if the analysis succeeded, else False\n\n\tset_options : Modify the settings controlling the run operation of the analytic.\n\t              Override this method if your analytic has some different options\n\t              available to it, but be sure to call this parent version after since\n\t              it sets common options.\n\n\tset_output_directory : Call this method to set a specific directory as the output location.\n\t                       The special names 'stdout' and 'stderr' are recognized as the\n\t                       output and error streams respectively rather than a directory.\n\n\twarning : Utility to standardize warnings coming from analytics.\n"
    
    
    is_static = False



OPTION_DETAILS = 'details'


