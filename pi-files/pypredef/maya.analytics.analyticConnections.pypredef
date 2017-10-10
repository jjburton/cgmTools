from maya.analytics.decorators import addHelp
from maya.analytics.dg_utilities import node_type_hierarchy_list
from maya.analytics.BaseAnalytic import BaseAnalytic
from maya.analytics.decorators import makeAnalytic
from maya.analytics.decorators import addMethodDocs
from maya.analytics.dg_utilities import plug_level_connections

class analyticConnections(BaseAnalytic):
    """
    This analytic looks at all connections in the DG and reports on them.
    
    In full detail mode the CSV file consists of the following columns with
    one connection per row:
        Source           : Source plug of the connection
        Source Type      : Node type of the source plug's node
        Destination      : Destination plug of the connection
        Destination Type : Node type of the destination plug's node
    
    In regular mode the CSV file consists of the following columns with
    one node type per row:
        Node Type         : Type of node involved in connections
        Source Count      : Number of outgoing connections on nodes of that type
        Destination Count : Number of incoming connections on nodes of that type
    """
    
    
    
    def run(self):
        """
        Run the analytic and output the results.
        """
    
        pass
    
    
    def help():
        """
        Call this method to print the class documentation, including all methods.
        """
    
        pass
    
    
    ANALYTIC_NAME = 'Connections'
    
    
    __fulldocs__ = "This analytic looks at all connections in the DG and reports on them.\n\nIn full detail mode the CSV file consists of the following columns with\none connection per row:\n    Source           : Source plug of the connection\n    Source Type      : Node type of the source plug's node\n    Destination      : Destination plug of the connection\n    Destination Type : Node type of the destination plug's node\n\nIn regular mode the CSV file consists of the following columns with\none node type per row:\n    Node Type         : Type of node involved in connections\n    Source Count      : Number of outgoing connections on nodes of that type\n    Destination Count : Number of incoming connections on nodes of that type\nBase class for output for analytics.\n\nThe default location for the anlaytic output is in a subdirectory\ncalled 'MayaAnalytics' in your temp directory. You can change that\nat any time by calling set_output_directory().\n\nClass static member:\n     ANALYTIC_NAME : Name of the analytic\n\nClass members:\n     directory     : Directory the output will go to\n     is_static     : True means this analytic doesn't require a file to run\n     logger        : Logging object for errors, warnings, and messages\n     plug_namer    : Object creating plug names, possibly anonymous\n     node_namer    : Object creating node names, possibly anonymous\n     csv_output    : Location to store legacy CSV output\n     plug_namer    : Set by option 'anonymous' - if True then make plug names anonymous\n     node_namer    : Set by option 'anonymous' - if True then make node names anonymous\n     __options     : List of per-analytic options\n\n\tMethods\n\t-------\n\tdebug : Utility to standardize debug messages coming from analytics.\n\n\terror : Utility to standardize errors coming from analytics.\n\n\testablish_baseline : This is run on an empty scene, to give the analytic a chance to\n\t                     establish any baseline data it might need (e.g. the nodes in an\n\t                     empty scene could all be ignored by the analytic)\n\t                     \n\t                     Base implementation does nothing. Derived classes should call\n\t                     their super() method though, in case something does get added.\n\n\thelp : Call this method to print the class documentation, including all methods.\n\n\tjson_file : Although an analytic is free to create any set of output files it\n\t            wishes there will always be one master JSON file containing the\n\n\tlog : Utility to standardize logging messages coming from analytics.\n\n\tmarker_file : Returns the name of the marker file used to indicate that the\n\t              computation of an analytic is in progress. If this file remains\n\t              in a directory after the analytic has run that means it was\n\t              interrupted and the data is not up to date.\n\t              \n\t              This file provides a safety measure against machines going down\n\t              or analytics crashing.\n\n\tname : Get the name of this type of analytic\n\n\toption : Return TRUE if the option specified has been set on this analytic.\n\t         option: Name of option to check\n\n\toutput_files : This is used to get the list of files the analytic will generate.\n\t               There will always be a JSON file generated which contains at minimum\n\t               the timing information. An analytic should override this method only\n\t               if they are adding more output files (e.g. a .jpg file).\n\t               \n\t               This should only be called after the final directory has been set.\n\n\trun : Run the analytic and output the results.\n\n\tset_options : Modify the settings controlling the run operation of the analytic.\n\t              Override this method if your analytic has some different options\n\t              available to it, but be sure to call this parent version after since\n\t              it sets common options.\n\n\tset_output_directory : Call this method to set a specific directory as the output location.\n\t                       The special names 'stdout' and 'stderr' are recognized as the\n\t                       output and error streams respectively rather than a directory.\n\n\twarning : Utility to standardize warnings coming from analytics.\n"
    
    
    is_static = False



OPTION_DETAILS = 'details'

OPTION_SUMMARY = 'summary'


