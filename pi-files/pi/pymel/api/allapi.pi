from maya.OpenMayaMPx import *
from maya.OpenMayaFX import *
from maya.OpenMayaAnim import *
from maya.OpenMayaRender import *
from maya.OpenMaya import *
from maya.OpenMayaUI import *

class SafeApiPtr(object):
    """
    A wrapper for api pointers which also contains a reference
    to the MScriptUtil which contains the storage. This helps
    ensure that the 'storage' for the pointer doesn't get
    wiped out before the pointer does. Pass the SafeApiPtr
    around in place of the 'true' pointer - then, when
    the 'true' pointer is needed (ie, immediately
    before feeding it into an api function), 'call'
    the SafeApiPtr object to return the 'true'
    pointer.
    
    Examples
    --------
    >>> from pymel.api.allapi import *
    >>> sel = MSelectionList()
    >>> sel.add('perspShape')
    >>> dag = MDagPath()
    >>> sel.getDagPath(0, dag)
    >>> cam = MFnCamera(dag)
    
    >>> aperMin = SafeApiPtr('double')
    >>> aperMax = SafeApiPtr('double')
    >>> cam.getFilmApertureLimits(aperMin(), aperMax())
    >>> print '%.5f, %.5f' % (aperMin.get(), aperMax.get())
    0.01378, 20.28991
    """
    
    
    
    def __call__(self):
        pass
    
    
    def __getitem__(self, index):
        pass
    
    
    def __init__(self, valueType, scriptUtil=None, size=1, asTypeNPtr=False):
        """
        :Parameters:
        valueType : `string`
            The name of the maya pointer type you would like
            returned - ie, 'int', 'short', 'float'.
        scriptUtil : `MScriptUtil`
            If you wish to use an existing MScriptUtil as
            the 'storage' for the value returned, specify it
            here - otherwise, a new MScriptUtil object is
            created.
        size : `int`
            If we want a pointer to an array, size indicates
            the number of items the array holds.  If we are
            creating an MScriptUtil, it will be initialized
            to hold this many items - if we are fed an
            MScriptUtil, then it is your responsibility to
            make sure it can hold the necessary number of items,
            or else maya will crash!
        asTypeNPtr : `bool`
            If we want a call to this SafeApiPtr to return a pointer
            for an argument such as:
               int2 &myArg;
            then we need to set asTypeNPtr to True:
               SafeApiPtr('int', size=2, asTypeNPtr=True)
            Otherwise, it is assumed that calling the object returns array
            ptrs:
               int myArg[2];
        """
    
        pass
    
    
    def __len__(self):
        pass
    
    
    def __setitem__(self, index, value):
        pass
    
    
    def get(self):
        """
        Dereference the pointer - ie, get the actual value we're pointing to.
        """
    
        pass
    
    
    def set(self, value):
        """
        Store the actual value we're pointing to.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def isValidMObject(obj):
    pass


def isValidMDagNode(obj):
    pass


def isValidMDagPath(obj):
    pass


def MItGraph(nodeOrPlug, *args, **kwargs):
    """
    Iterate over MObjects of Dependency Graph (DG) Nodes or Plugs starting at a specified root Node or Plug,
    If a list of types is provided, then only nodes of these types will be returned,
    if no type is provided all connected nodes will be iterated on.
    Types are specified as Maya API types.
    The following keywords will affect order and behavior of traversal:
    upstream: if True connections will be followed from destination to source,
              if False from source to destination
              default is False (downstream)
    breadth: if True nodes will be returned as a breadth first traversal of the connection graph,
             if False as a preorder (depth first)
             default is False (depth first)
    plug: if True traversal will be at plug level (no plug will be traversed more than once),
          if False at node level (no node will be traversed more than once),
          default is False (node level)
    prune : if True will stop the iteration on nodes than do not fit the types list,
            if False these nodes will be traversed but not returned
            default is False (do not prune)
    """

    pass


def isValidMObjectHandle(obj):
    """
    # fast convenience tests on API objects
    """

    pass


def toApiObject(nodeName, dagPlugs=True):
    """
    Get the API MPlug, MObject or (MObject, MComponent) tuple given the name
    of an existing node, attribute, components selection
    
    Parameters
    ----------
    dagPlugs : bool
        if True, plug result will be a tuple of type (MDagPath, MPlug)
    
    If we were unable to retrieve the node/attribute/etc, returns None
    """

    pass


def getPlugValue(plug):
    """
    given an MPlug, get its value
    """

    pass


def isValidMNodeOrPlug(obj):
    pass


def toComponentMObject(dagPath):
    """
    get an MObject representing all components of the passed dagPath
    
    The component type that will be returned depends on the exact type of
    object passed in - for instance, a poly mesh will return a component
    representing all the kMeshVertComponents.
    
    The exact choice of component type is determined by MItGeometry.
    """

    pass


def isValidMNode(obj):
    pass


def toMDagPath(nodeName):
    """
    Get an API MDagPAth to the node, given the name of an existing dag node
    """

    pass


def nameToMObject(*args):
    """
    Get the API MObjects given names of existing nodes
    """

    pass


def isValidMPlug(obj):
    pass


def MItDag(root=None, *args, **kwargs):
    """
    Iterate over the hierarchy under a root dag node, if root is None, will iterate on whole Maya scene
    If a list of types is provided, then only nodes of these types will be returned,
    if no type is provided all dag nodes under the root will be iterated on.
    Types are specified as Maya API types.
    The following keywords will affect order and behavior of traversal:
    breadth: if True nodes Mobjects will be returned as a breadth first traversal of the hierarchy tree,
             if False as a preorder (depth first)
             default is False (depth first)
    underworld: if True traversal will include a shape's underworld (dag object parented to the shape),
          if False underworld will not be traversed,
          default is False (do not traverse underworld )
    depth : if True will return depth of each node.
    prune : if True will stop the iteration on nodes than do not fit the types list,
            if False these nodes will be traversed but not returned
            default is False (do not prune)
    """

    pass


def toMPlug(plugName):
    """
    Get the API MObject given the name of an existing plug (node.attribute)
    """

    pass


def MItNodes(*args, **kwargs):
    """
    Iterator on MObjects of nodes of the specified types in the Maya scene,
    if a list of tyes is passed as args, then all nodes of a type included in the list will be iterated on,
    if no types are specified, all nodes of the scene will be iterated on
    the types are specified as Maya API types
    """

    pass


def toMObject(nodeName):
    """
    Get the API MObject given the name of an existing node
    """

    pass


def MObjectName(obj):
    """
    Get the name of an existing MPlug, MDagPath or MObject representing a dependency node
    """

    pass



