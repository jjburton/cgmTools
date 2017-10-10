"""
The information regarding the evaluation graph and scheduling information
for the current scene is output. The evaluation graph is updated before
dumping the information so it is guaranteed to be current. If no options
are selected the format shows the names of the nodes grouped by scheduling
types as well as a list of the node clusters created for scheduling.

    "BuildTime"      : GRAPH_BUILD_TIME_IN_MICROSECONDS
    "Parallel"       : [ LIST_OF_NODES_SCHEDULED_AS_PARALLEL ],
    "Serial"         : [ LIST_OF_NODES_SCHEDULED_AS_SERIAL ],
    "GloballySerial" : [ LIST_OF_NODES_SCHEDULED_AS_GLOBALLY_SERIAL ],
    "Untrusted"      : [ LIST_OF_NODES_SCHEDULED_AS_UNTRUSTED ]
    "Clusters"       : [ { CLUSTER_NAME : [ LIST_OF_NODES_IN_CLUSTER ] },
                         { CLUSTER_NAME : [ LIST_OF_NODES_IN_CLUSTER ] }
                         ...
                       ]
    The last is presented as an array of objects because the cluster
    names are not necessarily unique.

Options Available
    summary = Show a count of the various scheduling and cluster types
              in the graph. Appends this section to the above.

              "summary" : {
                  "Parallel" : COUNT_OF_PARALLEL_NODES,
                  "Serial" : COUNT_OF_SERIAL_NODES,
                  "GloballySerial" : COUNT_OF_GLOBALLY_SERIAL_NODES,
                  "Untrusted" : COUNT_OF_UNTRUSTED_NODES,
                  "Clusters" : [ COUNT_OF_NODES_PER_CLUSTER ]
              }

    details = Include all of the plug and connection information for each
              evaluation node. Instead of a list of node names each node
              will be an object containing plug and connection information:

              "NODE_NAME" : {
                 "inputPlugs"            : [ LIST_OF_INPUT_PLUGS_TO_DIRTY ],
                 "outputPlugs"           : [ LIST_OF_OUTPUT_PLUGS_TO_DIRTY ],
                 "affectsWorldPlugs"     : [ LIST_OF_WORLD_AFFECTING_PLUGS_TO_DIRTY ],
                 "upstreamConnections"   : [ LIST_OF_NODES_CONNECTED_UPSTREAM ],
                 "downstreamConnections" : [ LIST_OF_NODES_CONNECTED_DOWNSTREAM ]
              }

Example of a graph with two nodes in one cluster dumped with the 'summary' option:

    "output" : {
        "summary" : {
            "Parallel" : 1,
            "Serial" : 1,
            "GloballySerial" : 0,
            "Untrusted" : 0,
            "Clusters" : [1,1]
        },
        "BuildTime" : 12318,
        "Parallel" : [ "node1" ],
        "Serial" : [ "node2" ],
        "GloballySerial" : [],
        "Untrusted" : [],
        "Clusters" : [
            { "pruneRootsEvaluator" : [ "node1" ] },
            { "cacheEvaluator" : [ "node2" ] }
        ]
    }

The same graph with no options:

    output" : {
        "BuildTime" : 12318,
        "Parallel" : [ "node1" ],
        "Serial" : [ "node2" ],
        "GloballySerial" : [],
        "Untrusted" : [],
        "Clusters" : [
            { "pruneRootsEvaluator" : [ "node1" ] },
            { "cacheEvaluator" : [ "node2" ] }
        ]
    }

The same graph with both 'summary' and 'details' options:

    "output" : {
        "summary" : {
            "Parallel" : 1,
            "Serial" : 1,
            "GloballySerial" : 0,
            "Untrusted" : 0,
            "Clusters" : [1,1]
        },
        "BuildTime" : 12318,
        "Parallel" : {
            "node1" : {
                "inputPlugs" : [ "node1.i" ],
                "outputPlugs" : [ "node1.wm", "node1.pm" ],
                "affectsWorldPlugs" : [],
                "upstreamConnections" : [ "node2" ],
                "downstreamConnections" : []
                }
            },
        },
        "Serial" : {
            "node2" : {
                "inputPlugs" : [],
                "outputPlugs" : [ "node2.o" ],
                "affectsWorldPlugs" : [],
                "upstreamConnections" : [],
                "downstreamConnections" : [ "node1" ]
            }
        },
        "GloballySerial" : {},
        "Untrusted" : {},
        "Clusters" : [
            { "pruneRootsEvaluator" : ["node1"] },
            { "cacheEvaluator" : ["node2"] }
        ]
    }
"""

from maya.analytics.decorators import addHelp
from maya.analytics.BaseAnalytic import BaseAnalytic
from maya.analytics.decorators import makeAnalytic
from maya.analytics.decorators import addMethodDocs
from maya.debug.emModeManager import emModeManager

class analyticEvalManager(BaseAnalytic):
    """
    Create information specific to the evaluation manager:
        - list of nodes, plugs, and connections in the evaluation graph
        - scheduling type information for all nodes
    """
    
    
    
    def run(self):
        """
        Generates a JSON structure containing the evaluation graph information
        
        If the 'details' option is set then include the extra information as described
        in the analytic help information.
        """
    
        pass
    
    
    def help():
        """
        Call this method to print the class documentation, including all methods.
        """
    
        pass
    
    
    ANALYTIC_NAME = 'EvalManager'
    
    
    CONNECTION_TYPES = []
    
    
    PLUG_TYPES = []
    
    
    __fulldocs__ = "Create information specific to the evaluation manager:\n    - list of nodes, plugs, and connections in the evaluation graph\n    - scheduling type information for all nodes\nBase class for output for analytics.\n\nThe default location for the anlaytic output is in a subdirectory\ncalled 'MayaAnalytics' in your temp directory. You can change that\nat any time by calling set_output_directory().\n\nClass static member:\n     ANALYTIC_NAME : Name of the analytic\n\nClass members:\n     directory     : Directory the output will go to\n     is_static     : True means this analytic doesn't require a file to run\n     logger        : Logging object for errors, warnings, and messages\n     plug_namer    : Object creating plug names, possibly anonymous\n     node_namer    : Object creating node names, possibly anonymous\n     csv_output    : Location to store legacy CSV output\n     plug_namer    : Set by option 'anonymous' - if True then make plug names anonymous\n     node_namer    : Set by option 'anonymous' - if True then make node names anonymous\n     __options     : List of per-analytic options\n\n\tMethods\n\t-------\n\tdebug : Utility to standardize debug messages coming from analytics.\n\n\terror : Utility to standardize errors coming from analytics.\n\n\testablish_baseline : This is run on an empty scene, to give the analytic a chance to\n\t                     establish any baseline data it might need (e.g. the nodes in an\n\t                     empty scene could all be ignored by the analytic)\n\t                     \n\t                     Base implementation does nothing. Derived classes should call\n\t                     their super() method though, in case something does get added.\n\n\thelp : Call this method to print the class documentation, including all methods.\n\n\tjson_file : Although an analytic is free to create any set of output files it\n\t            wishes there will always be one master JSON file containing the\n\n\tlog : Utility to standardize logging messages coming from analytics.\n\n\tmarker_file : Returns the name of the marker file used to indicate that the\n\t              computation of an analytic is in progress. If this file remains\n\t              in a directory after the analytic has run that means it was\n\t              interrupted and the data is not up to date.\n\t              \n\t              This file provides a safety measure against machines going down\n\t              or analytics crashing.\n\n\tname : Get the name of this type of analytic\n\n\toption : Return TRUE if the option specified has been set on this analytic.\n\t         option: Name of option to check\n\n\toutput_files : This is used to get the list of files the analytic will generate.\n\t               There will always be a JSON file generated which contains at minimum\n\t               the timing information. An analytic should override this method only\n\t               if they are adding more output files (e.g. a .jpg file).\n\t               \n\t               This should only be called after the final directory has been set.\n\n\trun : Generates a JSON structure containing the evaluation graph information\n\t      \n\t      If the 'details' option is set then include the extra information as described\n\t      in the analytic help information.\n\n\tset_options : Modify the settings controlling the run operation of the analytic.\n\t              Override this method if your analytic has some different options\n\t              available to it, but be sure to call this parent version after since\n\t              it sets common options.\n\n\tset_output_directory : Call this method to set a specific directory as the output location.\n\t                       The special names 'stdout' and 'stderr' are recognized as the\n\t                       output and error streams respectively rather than a directory.\n\n\twarning : Utility to standardize warnings coming from analytics.\n"
    
    
    is_static = False



OPTION_DETAILS = 'details'

OPTION_SUMMARY = 'summary'


