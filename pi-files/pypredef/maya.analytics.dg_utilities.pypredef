"""
A collection of utilities to help manage the basic information in the DG in a
common way. This includes extracting node types from nodes and plugs, parsing
connection information, etc.
"""

def node_type_hierarchy_list():
    """
    Extract the list of all node types in the hierarchy below the root
    node. The list is returned with full hierarchy information,
    separated by a vertical bar '|'. For example the time-to-linear
    animcurve node type will look like '|animCurve|animCurveTL'.
    
    The root 'node' is omitted from all hierarchies since it would be
    redundant to include it everywhere. The leading vertical bar is
    used as a placeholder. The root type will be the one and only entry
    in the list without the leading vertical bar.
    
    e.g. return for the one-type hierarchy above would be:
        [ 'node' : 'node'
        , 'animCurve'   : '|animCurve'
        , 'animCurveTL' : '|animCurve|animCurveTL'
        ]
    """

    pass


def node_level_connections(node_name):
    """
    Get the source and destination connection list on a node. Handles
    all of the error and return cases so that calles can just use the
    result directly without having to duplicate the exception handling.
    
    node_name: Name of node on which to find connections
    returns:  A pair of lists of connected nodes, (sources,destinations)
              A list is empty if no connections in that direction exist.
    """

    pass


def default_nodes_and_connections():
    """
    Find what Maya believes to be all of the default and persistent nodes.
    This may not be the same as all of the nodes present in an empty scene
    but in cases where the empty scene couldn't be measured directly this
    is the next best thing.
    
    Returns a 2-tuple where the first element is a set of all default nodes
    and the second is a list of pairs of (src,dst) for connections going
    between default nodes.
    """

    pass


def __inheritance_list(leaf):
    """
    Returns the list of all node types inherited from "leaf", not
    including the root "node". Uses the member variable inheritance{}
    to allow recursive construction of the list while avoiding O(N^2)
    duplication of work.
    
    Returned list will be in order from base to most derived class.
    """

    pass


def plug_level_connections(node):
    """
    Given the name of a node find all of the connections to and from it.
    The return value is a pair of arrays, connections coming in and
    connections going out of this node, each consisting of pairs with
    the names of the source and destination plug names.
    
    This is an easier to understand format than the flat list with
    inconsistent ordering of source and destination.
    
    e.g. for connections A.o -> X.iA, B.o -> X.iB, and X.o -> C.i
    the return value will be:
    
        (
            [("A.o","X.iA"), ("B.o", "X.iB")],
            [("X.o","C.i"])
        )
    """

    pass



NODE_TYPE_ROOT = 'node'


