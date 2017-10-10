"""
Utility to read and analyze dependency graph or evaluation graph structure
information. Allows you to produce a visualization of a single graph, a
text comparision of two graphs, or a merged comparison of two graphs.

    from maya.debug.graphStructure import graphStructure

    # Store the current scene's graph structure in a file
    g = graphStructure()
    g.write( 'FileForGraph.dg' )

    # Get a new scene and get its structure directly
    cmds.file( 'MyTestFile.ma', force=True, open=True )
    graph1 = graphStructure()

    # Retrieve the stored graph structure
    graph2 = graphStructure( structure_file_name='FileForGraph.dg' )

    # Compare them to see if they are the same
    if not graph1.compare(graph2):
        print 'Oh noooes, the graph structure has changed!'
        # Now visualize the differences
        graph1.compare_as_dot(graph2, structure_file_name='GraphCompare.dot', show_only_differences=True)
"""

class graphStructure(object):
    """
    Provides access and manipulation on graph structure data that has been
    produced by the 'dbpeek -op graph' or 'dbpeek -op evaluation_graph' commands.
    """
    
    
    
    def __init__(self, structure_file_name=None, long_names=False, evaluation_graph=False, inclusions=['connections']):
        """
        Create a graph structure object from a file or the current scene.
        
        The graph data is read in and stored internally in a format that makes
        formatting and comparison easy.
        
        structure_file_name: if 'None' then the current scene will be used,
        otherwise the named file will be read.
        
        long_names: if True then don't attempt to shorten the node names by
        removing namespaces and DAG path elements.
        
        evaluation_graph: if True then get the structure of the evaluation
        manager graph, not the DG. This requires that the graph has already
        been created of course, e.g. by playing back a frame or two in EM
        serial or EM parallel mode.
        
        inclusions: A list representing which parts of the graph to include
        in the structure information. Valid members are the argument types
        to the dbpeek(op='graph') command:
            'nodes'       : List of nodes in the graph
            'plugs'       : DG mode - List of networked plugs
                            (not so useful as these are at the whim of the DG)
                            EM mode - List of plugs to dirty
            'connections' : List of connections in the graph
            'scheduling'  : DG mode - Scheduling types for the nodes
                            EM mode - Scheduling types plus the list of
                            clusters and the nodes they control during
                            evaluation.
        
        The more inclusions there are the slower any comparison will be so
        keep the amount of data collected to a minimum if you are concerned
        about performance. For simple graph structure verification a good
        minimal set is just the connection values.
        """
    
        pass
    
    
    def compare(self, other):
        """
        Compare this graph structure against another one and generate a
        summary of how the two graphs differ. Differences will be returned
        as a JSON structure consisting of difference types. If no differences
        are found in any category then None is returned so that a quick
        test for "identical" can be made.
        
        Otherwise the changes found are layered:
        {
            'original' : 'SELF_NAME',
            'compared_with' : 'OTHER_NAME',
            'nodes' :
                {
                    'added' : [ NODES_IN_SELF_BUT_NOT_OTHER ],
                    'removed' : [ NODES_IN_OTHER_BUT_NOT_SELF ]
                },
            'plugs_in' :
                {
                    'added' : [ INPUT_PLUGS_IN_SELF_BUT_NOT_OTHER ],
                    'removed' : [ INPUT_PLUGS_IN_OTHER_BUT_NOT_SELF ]
                },
            'plugs_out' :
                {
                    'added' : [ INPUT_PLUGS_IN_SELF_BUT_NOT_OTHER ],
                    'removed' : [ INPUT_PLUGS_IN_OTHER_BUT_NOT_SELF ]
                },
            'plugs_world' :
                {
                    'added' : [ WORLDSPACE_PLUGS_IN_SELF_BUT_NOT_OTHER ],
                    'removed' : [ WORLDSPACE_PLUGS_IN_OTHER_BUT_NOT_SELF ]
                },
            'connections' :
                {
                    'added' : [ OUTGOING_CONNECTIONS_IN_SELF_BUT_NOT_OTHER ],
                    'removed' : [ OUTGOING_CONNECTIONS_IN_OTHER_BUT_NOT_SELF ]
                }
        }
        
        All of the 'plugs' lists are for evaluation graph mode only.
        """
    
        pass
    
    
    def compare_after_operation(self, operation, operation_arguments=None):
        """
        Compare a graph before and after an operation (Python function).
        This method takes a snapshot of the graph, performs the operation, takes another snapshot of
        the graph, and then compares the two versions of the graph.
        
        operation:           Function to call between graph captures.
        operation_arguments: Arguments to pass to the operation() function. This is passed as-is so
                             if you need multiple arguments use a dictionary and the **args syntax.
                             If "None" then the operation is called with no arguments.
        
        Usage:
            def my_operation( **args ):
                pass
            g = graphStructure()
            g.compare_after_operation( my_operation, operation_arguments={ 'arg1' : 6, 'arg2' : 4 } )
        """
    
        pass
    
    
    def compare_as_dot(self, other, fileName=None, show_only_differences=False):
        """
        Compare this graph structure against another one and print out a
        .dot format for visualization in an application such as graphViz.
        
        The two graphs are overlayed so that the union of the graphs is
        present. Colors for nodes and connetions are:
        
            Black      : They are present in both graphs
            Red/Dotted : They are present in this graph but not the alternate graph
            Green/Bold : They are present in the alternate graph but not this graph
        
        If the fileName is specified then the output is sent
        to that file, otherwise it is printed to stdout.
        
        If show_only_differences is set to True then the output will omit all of
        the nodes and connections the two graphs have in common. Some common
        nodes may be output anyway if there is a new connection between them.
        
        Plugs have no dot format as yet.
        """
    
        pass
    
    
    def current_graph(self):
        """
        Returns a new graphStructure object with all of the same options as
        this one, except that it will always use the current scene even if
        the original came from a file.
        """
    
        pass
    
    
    def write(self, fileName=None):
        """
        Dump the graph in the .dg format it uses for reading. Useful for
        creating a dump file from the current scene, or just viewing the
        graph generated from the current scene. If the fileName is specified
        then the output is sent to that file, otherwise it goes to stdout.
        """
    
        pass
    
    
    def write_as_dot(self, fileName=None):
        """
        Dump the graph in .dot format for visualization in an application
        such as graphViz. If the fileName is specified then the output is
        sent to that file, otherwise it is printed to stdout.
        
        Plugs have no dot format as yet.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class DotFormatting(object):
    """
    Encapsulation of all of the .dot formatting decisions made for this
    type of graph output.
    """
    
    
    
    def __init__(self, long_names=False):
        """
        If long_names is True then don't attempt to shorten the node names by
        removing namespaces and DAG path elements.
        """
    
        pass
    
    
    def node(self, node):
        """
        Print out a graph node with a simplified label.
        """
    
        pass
    
    
    def nodeLabel(self, node):
        """
        Provide a label for a node. Uses the basename if use_long_names is not
        turned on, otherwise the full name.
        
        e.g.  Original:   grandparent|parent:ns1|:child
              Label:      child
        """
    
        pass
    
    
    def altered_connection(src, dst, inOriginal):
        """
        Print out code for a connection that was in one graph but not the other.
        If inOriginal is True the connection was in the original graph but not
        the secondary one, otherwise vice versa.
        """
    
        pass
    
    
    def altered_node_format(inOriginal):
        """
        Print out formatting instruction for nodes that were in one graph
        but not the other. If inOriginal is True the nodes were in the
        original graph but not the secondary one, otherwise vice versa.
        """
    
        pass
    
    
    def context_node_format():
        """
        Print out the formatting instruction to make nodes visible in the
        comparison graph but faded to indicate that they are actually the
        same and only present for context.
        """
    
        pass
    
    
    def footer():
        """
        Print this only once, at the end of the .dot file
        """
    
        pass
    
    
    def header():
        """
        Print this only once, at the beginning of the .dot file
        """
    
        pass
    
    
    def legend(dot_file):
        """
        Print out a legend node. In the case of a graph dump this is only
        the title, containing the name of the file analyzed.
        """
    
        pass
    
    
    def legend_for_compare(file1, file2, show_only_differences):
        """
        Print out a legend node showing the formatting information for a
        comparison of two graphs.
        """
    
        pass
    
    
    def simple_connection(src, dst):
        """
        Print out a simple connection
        """
    
        pass
    
    
    def simple_node_format():
        """
        Print out the formatting instruction to make nodes the default format.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    label = '__context [label="In both graphs, shown for context", penwidth="1.0", style="solid", color="#CCCCCC", fontcolor="#CCCCCC"] ;'
    
    
    legend_compare = '    {\n        rank = sink ;\n        node [shape=box] ;\n        __bothGraphs [label="In both graphs", penwidth="1.0", style="solid", color="#000000", fontcolor="#000000"] ;\n        __aButNotb [label="In graph 1 but not graph 2", penwidth="1.0", style="dotted", color="#CC0000", fontcolor="#CC0000"] ;\n        __bButNota [label="In graph 2 but not graph 1", penwidth="4.0", style="solid", color="#127F12", fontcolor="#127F12"] ;\n        \n    }'
    
    
    legend_compare_only_differences = '    {\n        rank = sink ;\n        node [shape=box] ;\n        __bothGraphs [label="In both graphs", penwidth="1.0", style="solid", color="#000000", fontcolor="#000000"] ;\n        __aButNotb [label="In graph 1 but not graph 2", penwidth="1.0", style="dotted", color="#CC0000", fontcolor="#CC0000"] ;\n        __bButNota [label="In graph 2 but not graph 1", penwidth="4.0", style="solid", color="#127F12", fontcolor="#127F12"] ;\n        __context [label="In both graphs, shown for context", penwidth="1.0", style="solid", color="#CCCCCC", fontcolor="#CCCCCC"] ;\n    }'
    
    
    legend_fmt = '    {\n        rank = sink ;\n        node [shape=box] ;\n        __bothGraphs [label="In both graphs", penwidth="1.0", style="solid", color="#000000", fontcolor="#000000"] ;\n        __aButNotb [label="In graph 1 but not graph 2", penwidth="1.0", style="dotted", color="#CC0000", fontcolor="#CC0000"] ;\n        __bButNota [label="In graph 2 but not graph 1", penwidth="4.0", style="solid", color="#127F12", fontcolor="#127F12"] ;\n        %s\n    }'
    
    
    style_a_and_b = 'penwidth="1.0", style="solid", color="#000000", fontcolor="#000000"'
    
    
    style_a_not_b = 'penwidth="1.0", style="dotted", color="#CC0000", fontcolor="#CC0000"'
    
    
    style_b_not_a = 'penwidth="4.0", style="solid", color="#127F12", fontcolor="#127F12"'
    
    
    style_context = 'penwidth="1.0", style="solid", color="#CCCCCC", fontcolor="#CCCCCC"'



def split_connection(connection):
    """
    Extract the name of a node and its attribute specification from
    one side of a connection.
    """

    pass


def checkMaya():
    """
    Check to see if Maya Python libraries are available
    """

    pass



KEY_PLUGS_INPUT = 'input'

KEY_ADDED = 'added'

MAYA_IS_AVAILABLE = True

KEY_CONNECTIONS = 'connections'

KEY_PLUGS = 'plugs'

KEY_NODES = 'nodes'

KEY_PLUGS_WORLD = 'affectsWorld'

KEY_REMOVED = 'removed'

KEY_PLUGS_OUTPUT = 'output'


