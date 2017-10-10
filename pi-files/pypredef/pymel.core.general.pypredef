import exceptions

"""
For the rest of the class hierarchy, including `DependNode <pymel.core.nodetypes.DependNode>`, `Transform <pymel.core.nodetypes.Transform>`,
and `Attribute <pymel.core.nodetypes.Attribute>`, see :mod:`pymel.core.nodetypes`.
"""

from pymel.internal.plogging import getLogger as _getLogger

class NodeTracker(object):
    """
    A class for tracking Maya Objects as they are created and deleted.
    Can (and probably should) be used as a context manager
    """
    
    
    
    def __enter__(self):
        pass
    
    
    def __exit__(self, exctype, excval, exctb):
        pass
    
    
    def __init__(self):
        pass
    
    
    def endTrack(self):
        """
        Stop tracking and remove the callback
        """
    
        pass
    
    
    def getNodes(self, returnType='PyNode'):
        """
        Return a list of maya objects as strings.
        
        Parameters
        ----------
        returnType : {'PyNode', 'str', 'MObject'}
        """
    
        pass
    
    
    def isTracking(self):
        """
        Return True/False
        """
    
        pass
    
    
    def reset(self):
        pass
    
    
    def startTrack(self):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


import pymel.util as _util

class PyNode(_util.ProxyUnicode):
    """
    Abstract class that is base for all pymel nodes classes.
    
    The names of nodes and attributes can be passed to this class, and the appropriate subclass will be determined.
    
        >>> PyNode('persp')
        nt.Transform(u'persp')
        >>> PyNode('persp.tx')
        Attribute(u'persp.translateX')
    
    If the passed node or attribute does not exist an error will be raised.
    """
    
    
    
    def __apimfn__(self):
        """
        Get a ``maya.OpenMaya*.MFn*`` instance
        """
    
        pass
    
    
    def __eq__(self, other):
        """
        :rtype: `bool`
        """
    
        pass
    
    
    def __ge__(self, other):
        pass
    
    
    def __getitem__(*args, **kwargs):
        """
        The function 'pymel.core.general.PyNode.__getitem__' is deprecated and will become unavailable in future pymel versions. Convert to string first using str() or PyNode.name()
        
        deprecated
        """
    
        pass
    
    
    def __gt__(self, other):
        pass
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def __le__(self, other):
        pass
    
    
    def __lt__(self, other):
        pass
    
    
    def __melobject__(self):
        """
        Special method for returning a mel-friendly representation.
        """
    
        pass
    
    
    def __ne__(self, other):
        """
        :rtype: `bool`
        """
    
        pass
    
    
    def __nonzero__(self):
        """
        :rtype: `bool`
        """
    
        pass
    
    
    def __radd__(self, other):
        pass
    
    
    def __reduce__(self):
        """
        allows PyNodes to be pickled
        """
    
        pass
    
    
    def __repr__(self):
        """
        :rtype: `unicode`
        """
    
        pass
    
    
    def addPrefix(self, prefix):
        """
        Returns the object's name with a prefix added to the beginning of the name
        
        :rtype: `other.NameParser`
        """
    
        pass
    
    
    def connections(*args, **kwargs):
        """
        This command returns a list of all attributes/objects of a specified type that are connected to the given object(s). If
        no objects are specified then the command lists the connections on selected nodes.
        
        Modifications:
          - returns an empty list when the result is None
          - returns an empty list (with a warning) when the arg is an empty list, tuple,
                set, or frozenset, making it's behavior consistent with when None is
                passed, or no args and nothing is selected (would formerly raise a
                TypeError)
          - When 'connections' flag is True, the attribute pairs are returned in a 2D-array::
        
                [['checker1.outColor', 'lambert1.color'], ['checker1.color1', 'fractal1.outColor']]
        
          - added sourceFirst keyword arg. when sourceFirst is true and connections is also true,
                the paired list of plugs is returned in (source,destination) order instead of (thisnode,othernode) order.
                this puts the pairs in the order that disconnectAttr and connectAttr expect.
          - added ability to pass a list of types
        
            :rtype: `PyNode` list
        
        Flags:
          - connections : c                (bool)          [create]
              If true, return both attributes involved in the connection. The one on the specified object is given first.  Default
              false.
        
          - destination : d                (bool)          [create]
              Give the attributes/objects that are on the destinationside of connection to the given object.  Default true.
        
          - exactType : et                 (bool)          [create]
              When set to true, -t/type only considers node of this exact type. Otherwise, derived types are also taken into account.
        
          - plugs : p                      (bool)          [create]
              If true, return the connected attribute names; if false, return the connected object names only.  Default false;
        
          - shapes : sh                    (bool)          [create]
              Actually return the shape name instead of the transform when the shape is selected.  Default false.
        
          - skipConversionNodes : scn      (bool)          [create]
              If true, skip over unit conversion nodes and return the node connected to the conversion node on the other side.
              Default false.
        
          - source : s                     (bool)          [create]
              Give the attributes/objects that are on the sourceside of connection to the given object.  Default true.
        
          - type : t                       (unicode)       [create]
              If specified, only take objects of a specified type.                               Flag can have multiple arguments,
              passed either as a tuple or a list.
        
        
        Derived from mel command `maya.cmds.listConnections`
        """
    
        pass
    
    
    def deselect(self):
        pass
    
    
    def exists(self, **kwargs):
        """
        objExists
        """
    
        pass
    
    
    def future(*args, **kwargs):
        """
        Modifications:
          - returns an empty list when the result is None
          - added a much needed 'type' filter
          - added an 'exactType' filter (if both 'exactType' and 'type' are present, 'type' is ignored)
        
            :rtype: `DependNode` list
        """
    
        pass
    
    
    def history(*args, **kwargs):
        """
        This command traverses backwards or forwards in the graph from the specified node and returns all of the nodes whose
        construction history it passes through. The construction history consists of connections to specific attributes of a
        node defined as the creators and results of the node's main data, eg. the curve for a Nurbs Curve node. For information
        on history connections through specific plugs use the listConnectionscommand first to find where the history begins then
        use this command on the resulting node.
        
        Modifications:
          - returns an empty list when the result is None
          - raises a RuntimeError when the arg is an empty list, tuple, set, or
                frozenset, making it's behavior consistent with when None is passed, or
                no args and nothing is selected (would formerly raise a TypeError)
          - added a much needed 'type' filter
          - added an 'exactType' filter (if both 'exactType' and 'type' are present, 'type' is ignored)
        
            :rtype: `DependNode` list
        
        Flags:
          - allConnections : ac            (bool)          [create]
              If specified, the traversal that searches for the history or future will not restrict its traversal across nodes to only
              dependent plugs. Thus it will reach all upstream nodes (or all downstream nodes for f/future).
        
          - allFuture : af                 (bool)          [create]
              If listing the future, list all of it. Otherwise if a shape has an attribute that represents its output geometry data,
              and that plug is connected, only list the future history downstream from that connection.
        
          - allGraphs : ag                 (bool)          [create]
              This flag is obsolete and has no effect.
        
          - breadthFirst : bf              (bool)          [create]
              The breadth first traversal will return the closest nodes in the traversal first. The depth first traversal will follow
              a complete path away from the node, then return to any other paths from the node. Default is depth first.
        
          - future : f                     (bool)          [create]
              List the future instead of the history.
        
          - futureLocalAttr : fl           (bool)          [query]
              This flag allows querying of the local-space future-related attribute(s) on shape nodes.
        
          - futureWorldAttr : fw           (bool)          [query]
              This flag allows querying of the world-space future-related attribute(s) on shape nodes.
        
          - groupLevels : gl               (bool)          [create]
              The node names are grouped depending on the level.  1 is the lead, the rest are grouped with it.
        
          - historyAttr : ha               (bool)          [query]
              This flag allows querying of the attribute where history connects on shape nodes.
        
          - interestLevel : il             (int)           [create]
              If this flag is set, only nodes whose historicallyInteresting attribute value is not less than the value will be listed.
              The historicallyInteresting attribute is 0 on nodes which are not of interest to non-programmers.  1 for the TDs, 2 for
              the users.
        
          - leaf : lf                      (bool)          [create]
              If transform is selected, show history for its leaf shape. Default is true.
        
          - levels : lv                    (int)           [create]
              Levels deep to traverse. Setting the number of levels to 0 means do all levels. All levels is the default.
        
          - pruneDagObjects : pdo          (bool)          [create]
              If this flag is set, prune at dag objects.                  Flag can have multiple arguments, passed either as a tuple
              or a list.
        
        
        Derived from mel command `maya.cmds.listHistory`
        """
    
        pass
    
    
    def listConnections(*args, **kwargs):
        """
        This command returns a list of all attributes/objects of a specified type that are connected to the given object(s). If
        no objects are specified then the command lists the connections on selected nodes.
        
        Modifications:
          - returns an empty list when the result is None
          - returns an empty list (with a warning) when the arg is an empty list, tuple,
                set, or frozenset, making it's behavior consistent with when None is
                passed, or no args and nothing is selected (would formerly raise a
                TypeError)
          - When 'connections' flag is True, the attribute pairs are returned in a 2D-array::
        
                [['checker1.outColor', 'lambert1.color'], ['checker1.color1', 'fractal1.outColor']]
        
          - added sourceFirst keyword arg. when sourceFirst is true and connections is also true,
                the paired list of plugs is returned in (source,destination) order instead of (thisnode,othernode) order.
                this puts the pairs in the order that disconnectAttr and connectAttr expect.
          - added ability to pass a list of types
        
            :rtype: `PyNode` list
        
        Flags:
          - connections : c                (bool)          [create]
              If true, return both attributes involved in the connection. The one on the specified object is given first.  Default
              false.
        
          - destination : d                (bool)          [create]
              Give the attributes/objects that are on the destinationside of connection to the given object.  Default true.
        
          - exactType : et                 (bool)          [create]
              When set to true, -t/type only considers node of this exact type. Otherwise, derived types are also taken into account.
        
          - plugs : p                      (bool)          [create]
              If true, return the connected attribute names; if false, return the connected object names only.  Default false;
        
          - shapes : sh                    (bool)          [create]
              Actually return the shape name instead of the transform when the shape is selected.  Default false.
        
          - skipConversionNodes : scn      (bool)          [create]
              If true, skip over unit conversion nodes and return the node connected to the conversion node on the other side.
              Default false.
        
          - source : s                     (bool)          [create]
              Give the attributes/objects that are on the sourceside of connection to the given object.  Default true.
        
          - type : t                       (unicode)       [create]
              If specified, only take objects of a specified type.                               Flag can have multiple arguments,
              passed either as a tuple or a list.
        
        
        Derived from mel command `maya.cmds.listConnections`
        """
    
        pass
    
    
    def listFuture(*args, **kwargs):
        """
        Modifications:
          - returns an empty list when the result is None
          - added a much needed 'type' filter
          - added an 'exactType' filter (if both 'exactType' and 'type' are present, 'type' is ignored)
        
            :rtype: `DependNode` list
        """
    
        pass
    
    
    def listHistory(*args, **kwargs):
        """
        This command traverses backwards or forwards in the graph from the specified node and returns all of the nodes whose
        construction history it passes through. The construction history consists of connections to specific attributes of a
        node defined as the creators and results of the node's main data, eg. the curve for a Nurbs Curve node. For information
        on history connections through specific plugs use the listConnectionscommand first to find where the history begins then
        use this command on the resulting node.
        
        Modifications:
          - returns an empty list when the result is None
          - raises a RuntimeError when the arg is an empty list, tuple, set, or
                frozenset, making it's behavior consistent with when None is passed, or
                no args and nothing is selected (would formerly raise a TypeError)
          - added a much needed 'type' filter
          - added an 'exactType' filter (if both 'exactType' and 'type' are present, 'type' is ignored)
        
            :rtype: `DependNode` list
        
        Flags:
          - allConnections : ac            (bool)          [create]
              If specified, the traversal that searches for the history or future will not restrict its traversal across nodes to only
              dependent plugs. Thus it will reach all upstream nodes (or all downstream nodes for f/future).
        
          - allFuture : af                 (bool)          [create]
              If listing the future, list all of it. Otherwise if a shape has an attribute that represents its output geometry data,
              and that plug is connected, only list the future history downstream from that connection.
        
          - allGraphs : ag                 (bool)          [create]
              This flag is obsolete and has no effect.
        
          - breadthFirst : bf              (bool)          [create]
              The breadth first traversal will return the closest nodes in the traversal first. The depth first traversal will follow
              a complete path away from the node, then return to any other paths from the node. Default is depth first.
        
          - future : f                     (bool)          [create]
              List the future instead of the history.
        
          - futureLocalAttr : fl           (bool)          [query]
              This flag allows querying of the local-space future-related attribute(s) on shape nodes.
        
          - futureWorldAttr : fw           (bool)          [query]
              This flag allows querying of the world-space future-related attribute(s) on shape nodes.
        
          - groupLevels : gl               (bool)          [create]
              The node names are grouped depending on the level.  1 is the lead, the rest are grouped with it.
        
          - historyAttr : ha               (bool)          [query]
              This flag allows querying of the attribute where history connects on shape nodes.
        
          - interestLevel : il             (int)           [create]
              If this flag is set, only nodes whose historicallyInteresting attribute value is not less than the value will be listed.
              The historicallyInteresting attribute is 0 on nodes which are not of interest to non-programmers.  1 for the TDs, 2 for
              the users.
        
          - leaf : lf                      (bool)          [create]
              If transform is selected, show history for its leaf shape. Default is true.
        
          - levels : lv                    (int)           [create]
              Levels deep to traverse. Setting the number of levels to 0 means do all levels. All levels is the default.
        
          - pruneDagObjects : pdo          (bool)          [create]
              If this flag is set, prune at dag objects.                  Flag can have multiple arguments, passed either as a tuple
              or a list.
        
        
        Derived from mel command `maya.cmds.listHistory`
        """
    
        pass
    
    
    def listSets(self, *args, **kwargs):
        """
        Returns list of sets this object belongs
        
        listSets -o $this
        
        :rtype: 'PyNode' list
        """
    
        pass
    
    
    def namespaceList(self):
        """
        Useful for cascading references.  Returns all of the namespaces of the calling object as a list
        
        :rtype: `unicode` list
        """
    
        pass
    
    
    def nodeType(*args, **kwargs):
        pass
    
    
    def objExists(self, **kwargs):
        """
        objExists
        """
    
        pass
    
    
    def select(self, **kwargs):
        pass
    
    
    def stripNamespace(self, *args, **kwargs):
        """
        Returns the object's name with its namespace removed.  The calling instance is unaffected.
        The optional levels keyword specifies how many levels of cascading namespaces to strip, starting with the topmost (leftmost).
        The default is 0 which will remove all namespaces.
        
        :rtype: `other.NameParser`
        """
    
        pass
    
    
    def swapNamespace(self, prefix):
        """
        Returns the object's name with its current namespace replaced with the provided one.
        The calling instance is unaffected.
        
        :rtype: `other.NameParser`
        """
    
        pass
    
    
    def __new__(cls, *args, **kwargs):
        """
        Catch all creation for PyNode classes, creates correct class depending on type passed.
        
        
        For nodes:
            MObject
            MObjectHandle
            MDagPath
            string/unicode
        
        For attributes:
            MPlug
            MDagPath, MPlug
            string/unicode
        """
    
        pass
    
    
    __apiobjects__ = {}


class ComponentIndex(tuple):
    """
    Class used to specify a multi-dimensional component index.
    
    If the length of a ComponentIndex object < the number of dimensions,
    then the remaining dimensions are taken to be 'complete' (ie, have not yet
    had indices specified).
    """
    
    
    
    def __add__(self, other):
        pass
    
    
    def __repr__(self):
        pass
    
    
    def __new__(cls, *args, **kwargs):
        """
        :Parameters:
        label : `string`
            Component label for this index.
            Useful for components whose 'mel name' may vary - ie, an isoparm
            may be specified as u, v, or uv.
        """
    
        pass
    
    
    __dict__ = None


class MayaObjectError(exceptions.TypeError):
    """
    #--------------------------
    # PyNode Exceptions
    #--------------------------
    """
    
    
    
    def __init__(self, node=None):
        pass
    
    
    def __str__(self):
        pass
    
    
    __weakref__ = None


class AmbiguityWarning(exceptions.Warning):
    __weakref__ = None


class Scene(object):
    """
    The Scene class provides an attribute-based method for retrieving `PyNode` instances of
    nodes in the current scene.
    
        >>> SCENE = Scene()
        >>> SCENE.persp
        nt.Transform(u'persp')
        >>> SCENE.persp.t
        Attribute(u'persp.translate')
    
    An instance of this class is provided for you with the name `SCENE`.
    """
    
    
    
    def __getattr__(self, obj):
        pass
    
    
    def __init__(self, *p, **k):
        pass
    
    
    def __new__(cls, *p, **k):
        """
        # redefine __new__
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class ProxySlice(object):
    """
    slice(stop)
    slice(start, stop[, step])
    
    Create a slice object.  This is used for extended slicing (e.g. a[0:10:2]).
    """
    
    
    
    def __cmp__(self, *args, **kwargs):
        """
        x.__cmp__(y) <==> cmp(x,y)
        """
    
        pass
    
    
    def __delattr__(self, *args, **kwargs):
        """
        x.__delattr__('name') <==> del x.name
        """
    
        pass
    
    
    def __format__(self, *args, **kwargs):
        """
        default object formatter
        """
    
        pass
    
    
    def __hash__(self, *args, **kwargs):
        """
        x.__hash__() <==> hash(x)
        """
    
        pass
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def __repr__(self, *args, **kwargs):
        """
        x.__repr__() <==> repr(x)
        """
    
        pass
    
    
    def __str__(self, *args, **kwargs):
        """
        x.__str__() <==> str(x)
        """
    
        pass
    
    
    def indices(self, *args, **kwargs):
        """
        S.indices(len) -> (start, stop, stride)
        
        Assuming a sequence of length len, calculate the start and stop
        indices, and the stride length of the extended slice described by
        S. Out of bounds indices are clipped in a manner consistent with the
        handling of normal slices.
        """
    
        pass
    
    
    start = None
    
    step = None
    
    stop = None
    
    __dict__ = None
    
    __weakref__ = None


class Component(PyNode):
    """
    Abstract base class for pymel components.
    """
    
    
    
    def __apicomponent__(self):
        pass
    
    
    def __apihandle__(self):
        pass
    
    
    def __apimdagpath__(self):
        """
        Return the MDagPath for the node of this component, if it is valid
        """
    
        pass
    
    
    def __apimfn__(self):
        pass
    
    
    def __apimobject__(self):
        """
        get the MObject for this component if it is valid
        """
    
        pass
    
    
    def __apiobject__(self):
        pass
    
    
    def __eq__(self, other):
        pass
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def __melobject__(self):
        pass
    
    
    def __nonzero__(self):
        """
        :rtype: `bool`
        """
    
        pass
    
    
    def __str__(self):
        pass
    
    
    def __unicode__(self):
        pass
    
    
    def isComplete(self, *args, **kwargs):
        pass
    
    
    def name(self):
        pass
    
    
    def namespace(self, *args, **kwargs):
        pass
    
    
    def node(self):
        pass
    
    
    def plugAttr(self):
        pass
    
    
    def plugNode(self):
        pass
    
    
    def numComponentsFromStrings(*componentStrings):
        """
        Does basic string processing to count the number of components
        given a number of strings, which are assumed to be the valid mel names
        of components.
        """
    
        pass
    
    
    
    
    __readonly__ = {}


class AttributeDefaults(PyNode):
    def __apimdagpath__(self):
        """
        Return the MDagPath for the node of this attribute, if it is valid
        """
    
        pass
    
    
    def __apimobject__(self):
        """
        Return the MObject for this attribute, if it is valid
        """
    
        pass
    
    
    def __apimplug__(self):
        """
        Return the MPlug for this attribute, if it is valid
        """
    
        pass
    
    
    def __apiobject__(self):
        """
        Return the default API object for this attribute, if it is valid
        """
    
        pass
    
    
    def accepts(self, type):
        """
        Returns true if this attribute can accept a connection of the given type.
        
        :Parameters:
            type : `Data.Type`
                data type 
        
                values: 'numeric', 'plugin', 'pluginGeometry', 'string', 'matrix', 'stringArray', 'doubleArray', 'floatArray', 'intArray', 'pointArray', 'vectorArray', 'matrixArray', 'componentList', 'mesh', 'lattice', 'nurbsCurve', 'nurbsSurface', 'sphere', 'dynArrayAttrs', 'dynSweptGeometry', 'subdSurface', 'NObject', 'NId', 'any'
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnData.accepts`
        """
    
        pass
    
    
    def addToCategory(self, category):
        """
        Add the attribute to the named category. 
        
        
        :Parameters:
            category : `unicode`
                New category to which the attribute is to be added 
        
        Derived from api method `maya.OpenMaya.MFnAttribute.addToCategory`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def getAddAttrCmd(self, useLongName=False):
        """
        Returns a string containing the  addAttr  command which would be required to recreate the  attribute  on a node. The command includes the terminating semicolon and is formatted as if for use with a selected node, meaning that it contains no node name.
        
        :Parameters:
            useLongName : `bool`
                if true, use the attribute's long name rather than its short name 
        
        
        :rtype: `unicode`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.getAddAttrCmd`
        """
    
        pass
    
    
    def getAffectsAppearance(self):
        """
        Returns true if this attribute affects the appearance of the object when rendering in the viewport.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.affectsAppearance`
        """
    
        pass
    
    
    def getCategories(self):
        """
        Get all of the categories to which this attribute belongs. 
        
        
        :rtype: `list` list
        
        Derived from api method `maya.OpenMaya.MFnAttribute.getCategories`
        """
    
        pass
    
    
    def getDisconnectBehavior(self):
        """
        Returns the behavior of this attribute when it is disconnected. The possible settings are as follows:
        
        :rtype: `AttributeDefaults.DisconnectBehavior`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.disconnectBehavior`
        """
    
        pass
    
    
    def getIndexMatters(self):
        """
        Determines whether the user must specify an index when connecting to this attribute, or whether the next available index can be used. This method only applies to array attributes which are non readable, i.e. destination attributes.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.indexMatters`
        """
    
        pass
    
    
    def getInternal(self):
        """
        Returns true if a node has internal member data representing this attribute.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.internal`
        """
    
        pass
    
    
    def getUsesArrayDataBuilder(self):
        """
        Returns true if this attribute uses an array data builder. If so, then the  MArrayDataBuilder  class may be used with this attribute.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.usesArrayDataBuilder`
        """
    
        pass
    
    
    def hasCategory(self, category):
        """
        Check to see if the attribute belongs to the named category. 
        
        
        :Parameters:
            category : `unicode`
                Category to check for attribute membership 
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.hasCategory`
        """
    
        pass
    
    
    def isAffectsWorldSpace(self):
        """
        Returns true if this attribute affects worldspace.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isAffectsWorldSpace`
        """
    
        pass
    
    
    def isArray(self):
        """
        Returns true if this attribute supports an array of data.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isArray`
        """
    
        pass
    
    
    def isCached(self):
        """
        Returns true if this attribute is cached locally in the node's data block. The default for this is true. Caching a node locally causes a copy of the attribute value for the node to be cached with the node. This removes the need to traverse through the graph to get the value each time it is requested.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isCached`
        """
    
        pass
    
    
    def isChannelBoxFlagSet(self):
        """
        Returns true if this attribute has its channel box flag set. Attributes will appear in the channel box if their channel box flag is set or if they are keyable.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isChannelBoxFlagSet`
        """
    
        pass
    
    
    def isConnectable(self):
        """
        Returns true if this attribute accepts dependency graph connections. If it does, then the readable and writable methods will indicate what types of connections are accepted.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isConnectable`
        """
    
        pass
    
    
    def isDynamic(self):
        """
        Returns true if this attribute is a dynamic attribute.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isDynamic`
        """
    
        pass
    
    
    def isExtension(self):
        """
        Returns true if this attribute is an extension attribute.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isExtension`
        """
    
        pass
    
    
    def isHidden(self):
        """
        Returns true if this attribute is to hidden from the UI. The attribute will not show up in attribute editors.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isHidden`
        """
    
        pass
    
    
    def isIndeterminant(self):
        """
        Returns true if this attribute is indeterminant. If an attribute may or may not be used during an evaluation then it is indeterminant. This attribute classification is mainly used on rendering nodes to indicate that some attributes are not always used.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isIndeterminant`
        """
    
        pass
    
    
    def isKeyable(self):
        """
        Returns true if this attribute is keyable. Keyable attributes will be keyed by AutoKey and the Set Keyframe UI. Non-keyable attributes prevent the user from setting keys via the obvious UI provided for keying. Being non-keyable is not a hard block against adding keys to an attribute.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isKeyable`
        """
    
        pass
    
    
    def isReadable(self):
        """
        Returns true if this attribute is readable. If an attribute is readable, then it can be used as the source in a dependency graph connection.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isReadable`
        """
    
        pass
    
    
    def isRenderSource(self):
        """
        Returns true if this attribute is a render source. This attribute is used on rendering nodes to override the rendering sampler info.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isRenderSource`
        """
    
        pass
    
    
    def isStorable(self):
        """
        Returns true if this attribute is to be stored when the node is saved to a file.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isStorable`
        """
    
        pass
    
    
    def isUsedAsColor(self):
        """
        Returns true if this attribute is to be presented as a color in the UI.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isUsedAsColor`
        """
    
        pass
    
    
    def isUsedAsFilename(self):
        """
        Returns true if this attribute is to be used as a filename. In the UI this attr will be presented as a file name.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isUsedAsFilename`
        """
    
        pass
    
    
    def isWorldSpace(self):
        """
        Returns true if this attribute is worldspace.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isWorldSpace`
        """
    
        pass
    
    
    def isWritable(self):
        """
        Returns true if this attribute is writable. If an attribute is writable, then it can be used as the destination in a dependency graph connection.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.isWritable`
        """
    
        pass
    
    
    def name(self):
        pass
    
    
    def parent(self):
        """
        Get the parent of this attribute, if it has one.
        
        :rtype: `PyNode`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.parent`
        """
    
        pass
    
    
    def removeFromCategory(self, category):
        """
        Remove the attribute from the named category. 
        
        
        :Parameters:
            category : `unicode`
                Category from which the attribute is to be removed 
        
        Derived from api method `maya.OpenMaya.MFnAttribute.removeFromCategory`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def setAffectsAppearance(self, state):
        """
        Sets whether this attribute affects the appearance of the object when rendering in the viewport.
        
        :Parameters:
            state : `bool`
                whether the attribute affects the appearance of the object when rendering in the viewport.
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setAffectsAppearance`
        """
    
        pass
    
    
    def setAffectsWorldSpace(self, state):
        """
        Sets whether this attribute should affect worldspace. NOTES: This property is ignored on non-dag nodes.
        
        :Parameters:
            state : `bool`
                whether the attribute should affect worldspace
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setAffectsWorldSpace`
        """
    
        pass
    
    
    def setArray(self, state):
        """
        Sets whether this attribute should have an array of data. This should be set to true if the attribute needs to accept multiple incoming connections.
        
        :Parameters:
            state : `bool`
                whether the attribute is to have an array of data
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setArray`
        """
    
        pass
    
    
    def setCached(self, state):
        """
        Sets whether the data for this attribute is cached locally in the node's data block. The default for this is true. Caching a node locally causes a copy of the attribute value for the node to be cached with the node. This removes the need to traverse through the graph to get the value each time it is requested. This should only get called in the initialize call of your node creator.
        
        :Parameters:
            state : `bool`
                whether the attribute is to be cached locally
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setCached`
        """
    
        pass
    
    
    def setChannelBox(self, state):
        """
        Sets whether this attribute should appear in the channel box when the node is selected. This should only get called in the initialize call of your node creator. Keyable attributes are always shown in the channel box so this flag is ignored on keyable attributes. It is for intended for use on non-keyable attributes which you want to appear in the channel box.
        
        :Parameters:
            state : `bool`
                whether the attribute is to appear in the channel box
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setChannelBox`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def setConnectable(self, state):
        """
        Sets whether this attribute should allow dependency graph connections. This should only get called in the initialize call of your node creator.
        
        :Parameters:
            state : `bool`
                whether the attribute is to be connectable
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setConnectable`
        """
    
        pass
    
    
    def setDisconnectBehavior(self, behavior):
        """
        Sets the disconnection behavior for this attribute. This determines what happens when a connection to this attribute is deleted. This should only get called in the initialize call of your node creator.
        
        :Parameters:
            behavior : `AttributeDefaults.DisconnectBehavior`
                the new disconnect behavior
        
                values: 'delete', 'reset', 'nothing'
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setDisconnectBehavior`
        """
    
        pass
    
    
    def setHidden(self, state):
        """
        Sets whether this attribute should be hidden from the UI. This is useful if the attribute is being used for blind data, or if it is being used as scratch space for a geometry calculation (should also be marked non-connectable in that case).
        
        :Parameters:
            state : `bool`
                whether the attribute is to be hidden
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setHidden`
        """
    
        pass
    
    
    def setIndeterminant(self, state):
        """
        Sets whether this attribute is indeterminant. If an attribute may or may not be used during an evaluation then it is indeterminant. This attribute classification is mainly used on rendering nodes to indicate that some attributes are not always used.
        
        :Parameters:
            state : `bool`
                whether the attribute indeterminant
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setIndeterminant`
        """
    
        pass
    
    
    def setIndexMatters(self, state):
        """
        If the attribute is an array, then this method specifies whether to force the user to specify an index when connecting to this attribute, or to use the next available index.
        
        :Parameters:
            state : `bool`
                whether the attribute's index must be specified when connecting to this attribute using the connectAttr command
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setIndexMatters`
        """
    
        pass
    
    
    def setInternal(self, state):
        """
        The function controls an attribute's data storage. When set to true, the virtual methods  MPxNode::setInternalValueInContext()  and  MPxNode::getInternalValueInContext()  are invoked whenever the attribute value is set or queried, respectively. By default, attributes are not internal.
        
        :Parameters:
            state : `bool`
                whether the attribute uses internal data
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setInternal`
        """
    
        pass
    
    
    def setKeyable(self, state):
        """
        Sets whether this attribute should accept keyframe data. This should only get called in the initialize call of your node creator. Keyable attributes will be keyed by AutoKey and the Set Keyframe UI. Non-keyable attributes prevent the user from setting keys via the obvious UI provided for keying. Being non-keyable is not a hard block against adding keys to an attribute.
        
        :Parameters:
            state : `bool`
                whether the attribute is to be keyable
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setKeyable`
        """
    
        pass
    
    
    def setNiceNameOverride(self, localizedName):
        """
        Sets the localized string which should be used for this attribute in the UI.
        
        :Parameters:
            localizedName : `unicode`
                The name to use for the current locale.
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setNiceNameOverride`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def setReadable(self, state):
        """
        Sets whether this attribute should be readable. If an attribute is readable, then it can be used as the source in a dependency graph connection.
        
        :Parameters:
            state : `bool`
                whether the attribute is to be readable
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setReadable`
        """
    
        pass
    
    
    def setRenderSource(self, state):
        """
        Sets whether this attribute should be used as a render source attribute. When writing shader plug-ins, it is sometimes useful to be able to modify the sampler info, so upstream shading network can be re- evaluated with different sampler info values.
        
        :Parameters:
            state : `bool`
                whether the attribute is to be a render source
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setRenderSource`
        """
    
        pass
    
    
    def setStorable(self, state):
        """
        Sets whether this attribute should be storable. If an attribute is storable, then it will be writen out when the node is stored to a file. This should only get called in the initialize call of your node creator.
        
        :Parameters:
            state : `bool`
                whether the attribute is to be storable
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setStorable`
        """
    
        pass
    
    
    def setUsedAsColor(self, state):
        """
        Sets whether this attribute should be presented as a color in the UI.
        
        :Parameters:
            state : `bool`
                whether the attribute is to be presented as a color
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setUsedAsColor`
        """
    
        pass
    
    
    def setUsedAsFilename(self, state):
        """
        Sets whether this attribute should be presented as a filename in the UI.
        
        :Parameters:
            state : `bool`
                whether the attribute is to be presented as a filename
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setUsedAsFilename`
        """
    
        pass
    
    
    def setUsesArrayDataBuilder(self, state):
        """
        Sets whether this attribute uses an array data builder. If true, then the  MArrayDataBuilder  class may be used with this attribute to generate its data. If false,  MArrayDataHandle::builder  will fail.
        
        :Parameters:
            state : `bool`
                whether the attribute uses an array data builder
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setUsesArrayDataBuilder`
        """
    
        pass
    
    
    def setWorldSpace(self, state):
        """
        Sets whether this attribute should be treated as worldspace. Being worldspace indicates the attribute is dependent on the worldSpace transformation of this node, and will be marked dirty by any attribute changes in the hierarchy that affects the worldSpace transformation. The attribute needs to be an array since during instancing there are multiple worldSpace paths to the node & Maya requires one array element per path for worldSpace attributes.
        
        :Parameters:
            state : `bool`
                whether the attribute is to be presented as worldspace
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setWorldSpace`
        """
    
        pass
    
    
    def setWritable(self, state):
        """
        Sets whether this attribute should be writable. If an attribute is writable, then it can be used as the destination in a dependency graph connection. If an attribute is not writable then  setAttr  commands will fail to change the attribute.
        
        :Parameters:
            state : `bool`
                whether the attribute is to be writable
        
        Derived from api method `maya.OpenMaya.MFnAttribute.setWritable`
        """
    
        pass
    
    
    def shortName(self):
        """
        Returns the short name of the attribute. If the attribute has no short name then its long name is returned.
        
        :rtype: `unicode`
        
        Derived from api method `maya.OpenMaya.MFnAttribute.shortName`
        """
    
        pass
    
    
    DisconnectBehavior = {}
    
    
    __apicls__ = None
    
    
    
    
    __readonly__ = {}


class MayaNodeError(MayaObjectError):
    pass


class HashableSlice(ProxySlice):
    """
    # Really, don't need to have another class inheriting from
    # the proxy class, but do this so I can define a method using
    # normal class syntax...
    """
    
    
    
    def __cmp__(self, other):
        pass
    
    
    def __hash__(self):
        pass
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    start = None
    
    step = None
    
    stop = None


class MayaAttributeError(MayaObjectError, exceptions.AttributeError):
    pass


class Attribute(PyNode):
    """
    Attribute class
    
    see pymel docs for details on usage
    """
    
    
    
    def __apimattr__(self):
        """
        Return the MFnAttribute for this attribute, if it is valid
        """
    
        pass
    
    
    def __apimdagpath__(self):
        """
        Return the MDagPath for the node of this attribute, if it is valid
        """
    
        pass
    
    
    def __apimobject__(self):
        """
        Return the MObject for this attribute, if it is valid
        """
    
        pass
    
    
    def __apimplug__(self):
        """
        Return the MPlug for this attribute, if it is valid
        """
    
        pass
    
    
    def __apiobject__(self):
        """
        Return the default API object (MPlug) for this attribute, if it is valid
        """
    
        pass
    
    
    def __call__(self, *args, **kwargs):
        pass
    
    
    def __delitem__(self, index=None, break_=False):
        pass
    
    
    def __eq__(self, other):
        """
        :rtype: `bool`
        """
    
        pass
    
    
    def __floordiv__(self, other):
        """
        operator for 'disconnectAttr'
        
            >>> from pymel.core import *
            >>> SCENE.persp.tx >> SCENE.top.tx  # connect
            >>> SCENE.persp.tx // SCENE.top.tx  # disconnect
        """
    
        pass
    
    
    def __getattr__(self, attr):
        pass
    
    
    def __getitem__(self, index):
        """
        This method will find and return a plug with the given logical index. The logical index is the sparse array index used in MEL scripts. If a plug does not exist at the given Index, Maya will create a plug at that index. This is not the case with  elementByPhysicalIndex() . If needed, elementByLogicalIndex can be used to expand an array plug on a node. It is important to note that Maya assumes that all such plugs serve a purpose and it will not free non-networked plugs that result from such an array expansion.
        
        :Parameters:
            index : `int`
                The index of the plug to be found 
        
        
        :rtype: `PyNode`
        
        Derived from api method `maya.OpenMaya.MPlug.elementByLogicalIndex`
        """
    
        pass
    
    
    def __hash__(self):
        """
        :rtype: `int`
        """
    
        pass
    
    
    def __iter__(self):
        """
        iterator for multi-attributes
        
            >>> from pymel.core import *
            >>> f=newFile(f=1) #start clean
            >>>
            >>> at = PyNode( 'defaultLightSet.dagSetMembers' )
            >>> nt.SpotLight()
            nt.SpotLight(u'spotLightShape1')
            >>> nt.SpotLight()
            nt.SpotLight(u'spotLightShape2')
            >>> nt.SpotLight()
            nt.SpotLight(u'spotLightShape3')
            >>> for x in at: print x
            ...
            defaultLightSet.dagSetMembers[0]
            defaultLightSet.dagSetMembers[1]
            defaultLightSet.dagSetMembers[2]
        """
    
        pass
    
    
    def __ne__(self, other):
        """
        :rtype: `bool`
        """
    
        pass
    
    
    def __rshift__(self, other):
        """
        operator for 'connectAttr'
        
            >>> from pymel.core import *
            >>> SCENE.persp.tx >> SCENE.top.tx  # connect
            >>> SCENE.persp.tx // SCENE.top.tx  # disconnect
        """
    
        pass
    
    
    def __str__(self):
        """
        :rtype: `str`
        """
    
        pass
    
    
    def __unicode__(self):
        """
        :rtype: `unicode`
        """
    
        pass
    
    
    def affected(self, **kwargs):
        pass
    
    
    def affects(self, **kwargs):
        pass
    
    
    def array(self):
        """
        Returns the array (multi) attribute of the current element:
        
            >>> n = Attribute(u'initialShadingGroup.groupNodes[0]')
            >>> n.isElement()
            True
            >>> n.array()
            Attribute(u'initialShadingGroup.groupNodes')
        
        This method will raise an error for attributes which are not elements of
        an array:
        
            >>> m = Attribute(u'initialShadingGroup.groupNodes')
            >>> m.isElement()
            False
            >>> m.array()
            Traceback (most recent call last):
            ...
            TypeError: initialShadingGroup.groupNodes is not an array (multi) attribute
        
        :rtype: `Attribute`
        """
    
        pass
    
    
    def attr(self, attr):
        """
        :rtype: `Attribute`
        """
    
        pass
    
    
    def attrName(self, longName=False, includeNode=False):
        """
        Just the name of the attribute for this plug
        
        This will have no indices, no parent attributes, etc...
        This is suitable for use with cmds.attributeQuery
        
            >>> at = SCENE.persp.instObjGroups.objectGroups
            >>> at.name()
            u'persp.instObjGroups[-1].objectGroups'
            >>> at.attrName()
            u'og'
            >>> at.attrName(longName=True)
            u'objectGroups'
        """
    
        pass
    
    
    def children(self):
        """
        attributeQuery -listChildren
        
        :rtype: `Attribute` list
        """
    
        pass
    
    
    def connect(source, destination, **kwargs):
        """
        Connect the attributes of two dependency nodes and return the names of the two connected attributes. The connected
        attributes must be be of compatible types. First argument is the source attribute, second one is the destination. Refer
        to dependency node documentation.
        
        Maya Bug Fix:
          - even with the 'force' flag enabled, the command would raise an error if the connection already existed.
        
        Flags:
          - force : f                      (bool)          [create]
              Forces the connection.  If the destination is already connected, the old connection is broken and the new one made.
        
          - lock : l                       (bool)          [create]
              If the argument is true, the destination attribute is locked after making the connection. If the argument is false, the
              connection is unlocked before making the connection.
        
          - nextAvailable : na             (bool)          [create]
              If the destination multi-attribute has set the indexMatters to be false with this flag specified, a connection is made
              to the next available index. No index need be specified.
        
          - referenceDest : rd             (unicode)       [create]
              This flag is used for file io only. The flag indicates that the connection replaces a connection made in a referenced
              file, and the flag argument indicates the original destination from the referenced file. This flag is used so that if
              the reference file is modified, maya can still attempt to make the appropriate connections in the main scene to the
              referenced object.                  Flag can have multiple arguments, passed either as a tuple or a list.
        
        
        Derived from mel command `maya.cmds.connectAttr`
        """
    
        pass
    
    
    def delete(self):
        """
        deleteAttr
        """
    
        pass
    
    
    def disconnect(source, destination=None, inputs=None, outputs=None, **kwargs):
        """
        Disconnects two connected attributes. First argument is the source attribute, second is the destination.
        
        Modifications:
          - If no destination is passed, then all inputs will be disconnected if inputs
              is True, and all outputs will be disconnected if outputs is True; if
              neither are given (or both are None), both all inputs and all outputs
              will be disconnected
        
        Flags:
          - nextAvailable : na             (bool)          [create]
              If the destination multi-attribute has set the indexMatters to be false, the command will disconnect the first matching
              connection.  No index needs to be specified.                  Flag can have multiple arguments, passed either as a tuple
              or a list.
        
        
        Derived from mel command `maya.cmds.disconnectAttr`
        """
    
        pass
    
    
    def elementByLogicalIndex(self, index):
        """
        This method will find and return a plug with the given logical index. The logical index is the sparse array index used in MEL scripts. If a plug does not exist at the given Index, Maya will create a plug at that index. This is not the case with  elementByPhysicalIndex() . If needed, elementByLogicalIndex can be used to expand an array plug on a node. It is important to note that Maya assumes that all such plugs serve a purpose and it will not free non-networked plugs that result from such an array expansion.
        
        :Parameters:
            index : `int`
                The index of the plug to be found 
        
        
        :rtype: `PyNode`
        
        Derived from api method `maya.OpenMaya.MPlug.elementByLogicalIndex`
        """
    
        pass
    
    
    def elementByPhysicalIndex(self, index):
        """
        This method will find and return a plug with the given physical index. The index can range from 0 to  numElements()  - 1. This function is particularly useful for iteration through the element plugs of an array plug. It is equivalent to operator [] (int) This method is only valid for array plugs.
        
        :Parameters:
            index : `int`
                The physical array index of the plug to be found 
        
        
        :rtype: `PyNode`
        
        Derived from api method `maya.OpenMaya.MPlug.elementByPhysicalIndex`
        """
    
        pass
    
    
    def elements(self):
        """
        ``listAttr -multi``
        
        Return a list of strings representing all the attributes in the array.
        
        If you don't need actual strings, it is recommended that you simply iterate through the elements in the array.
        See `Attribute.__iter__`.
        
        Modifications:
          - returns an empty list when the result is None
        """
    
        pass
    
    
    def evaluate(self, **kwargs):
        pass
    
    
    def evaluateNumElements(self):
        """
        Return the total number of elements in the datablock of this array plug. The return count will include both connected and non-connected elements, and will perform an evaluate in order to make sure that the datablock is as up-to-date as possible since some nodes do not place array elements into the datablock until the attribute is evaluated.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MPlug.evaluateNumElements`
        """
    
        pass
    
    
    def exists(self):
        """
        Whether the attribute actually exists.
        
        In spirit, similar to 'attributeQuery -exists'...
        ...however, also handles multi (array) attribute elements, such as plusMinusAverage.input1D[2]
        
        :rtype: `bool`
        """
    
        pass
    
    
    def firstParent(*args, **kwargs):
        """
        The function 'pymel.core.general.Attribute.firstParent' is deprecated and will become unavailable in future pymel versions. use Attribute.getParent instead
        
        deprecated: use getParent instead
        """
    
        pass
    
    
    def get(attr, default=None, **kwargs):
        """
        This command returns the value of the named object's attribute. UI units are used where applicable. Currently, the types
        of attributes that can be displayed are: numeric attributesstring attributesmatrix attributesnumeric compound attributes
        (whose children are all numeric)vector array attributesdouble array attributesint32 array attributespoint array
        attributesdata component list attributesOther data types cannot be retrieved. No result is returned if the attribute
        contains no data.
        
        Maya Bug Fix:
          - maya pointlessly returned vector results as a tuple wrapped in a list ( ex.  '[(1,2,3)]' ). This command unpacks the vector for you.
        
        Modifications:
          - casts double3 datatypes to `Vector`
          - casts matrix datatypes to `Matrix`
          - casts vectorArrays from a flat array of floats to an array of Vectors
          - when getting a multi-attr, maya would raise an error, but pymel will return a list of values for the multi-attr
          - added a default argument. if the attribute does not exist and this argument is not None, this default value will be returned
          - added support for getting message attributes
        
        Flags:
          - asString : asString            (bool)          [create]
              This flag is only valid for enum attributes. It allows you to get the attribute values as strings instead of integer
              values. Note that the returned string value is dependent on the UI language Maya is running in (about -uiLanguage).
        
          - caching : ca                   (bool)          [create]
              Returns whether the attribute is set to be cached internally
        
          - channelBox : cb                (bool)          [create]
              Returns whether the attribute is set to show in the channelBox. Keyable attributes also show in the channel box.
        
          - expandEnvironmentVariables : x (bool)          [create]
              Expand any environment variable and (tilde characters on UNIX) found in string attributes which are returned.
        
          - keyable : k                    (bool)          [create]
              Returns the keyable state of the attribute.
        
          - lock : l                       (bool)          [create]
              Returns the lock state of the attribute.
        
          - multiIndices : mi              (bool)          [create]
              If the attribute is a multi, this will return a list containing all of the valid indices for the attribute.
        
          - settable : se                  (bool)          [create]
              Returns 1 if this attribute is currently settable by setAttr, 0 otherwise. An attribute is settable if it's not locked
              and either not connected, or has only keyframed animation.
        
          - silent : sl                    (bool)          [create]
              When evaluating an attribute that is not a numeric or string value, suppress the error message saying that the data
              cannot be displayed. The attribute will be evaluated even though its data cannot be displayed. This flag does not
              suppress all error messages, only those that are benign.
        
          - size : s                       (bool)          [create]
              Returns the size of a multi-attribute array.  Returns 1 if non-multi.
        
          - time : t                       (time)          [create]
              Evaluate the attribute at the given time instead of the current time.
        
          - type : typ                     (bool)          [create]
              Returns the type of data currently in the attribute. Attributes of simple types such as strings and numerics always
              contain data, but attributes of complex types (arrays, meshes, etc) may contain no data if none has ever been assigned
              to them. When this happens the command will return with no result: not an empty string, but no result at all. Attempting
              to directly compare this non-result to another value or use it in an expression will result in an error, but you can
              assign it to a variable in which case the variable will be set to the default value for its type (e.g. an empty string
              for a string variable, zero for an integer variable, an empty array for an array variable). So to be safe when using
              this flag, always assign its result to a string variable, never try to use it directly.                   Flag can have
              multiple arguments, passed either as a tuple or a list.
        
        
        Derived from mel command `maya.cmds.getAttr`
        """
    
        pass
    
    
    def getAlias(self, **kwargs):
        """
        Returns the alias for this attribute, or None.
        
        The alias of the attribute is set through
        Attribute.setAlias, or the aliasAttr command.
        """
    
        pass
    
    
    def getAllParents(self, arrays=False):
        """
        Return a list of all parents above this.
        
        Starts from the parent immediately above, going up.
        
        :rtype: `Attribute` list
        """
    
        pass
    
    
    def getArrayIndices(self):
        """
        Get all set or connected array indices. Raises an error if this is not an array Attribute
        
        :rtype: `int` list
        """
    
        pass
    
    
    def getChildren(self):
        """
        attributeQuery -listChildren
        
        :rtype: `Attribute` list
        """
    
        pass
    
    
    def getEnums(attr):
        """
        Get the enumerators for an enum attribute.
        
        :rtype: `util.enum.EnumDict`
        
        >>> addAttr( "persp", ln='numbers', at='enum', enumName="zero:one:two:thousand=1000:three")
        >>> numbers = Attribute('persp.numbers').getEnums()
        >>> sorted(numbers.items())
        [(u'one', 1), (u'thousand', 1000), (u'three', 1001), (u'two', 2), (u'zero', 0)]
        >>> numbers[1]
        u'one'
        >>> numbers['thousand']
        1000
        """
    
        pass
    
    
    def getMax(self):
        """
        attributeQuery -max
            Returns None if max does not exist.
        
        :rtype: `float`
        """
    
        pass
    
    
    def getMin(self):
        """
        attributeQuery -min
            Returns None if min does not exist.
        
        :rtype: `float`
        """
    
        pass
    
    
    def getNumElements(self):
        """
        Return the total number of elements in the datablock of this array plug. The return count will include all existing non-connected elements plus connected elements if they have been evaluated. It will not include connected elements that have not yet been placed into the datablock. The method  MPlug::evaluateNumElements  can be used in the sitution where you want an accurate count that includes all connected elements.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MPlug.numElements`
        """
    
        pass
    
    
    def getParent(self, generations=1, arrays=False):
        """
        Modifications:
            - added optional generations keyword arg, which gives the number of
              levels up that you wish to go for the parent
        
              Negative values will traverse from the top.
        
              A value of 0 will return the same node.
              The default value is 1.
        
              If generations is None, it will be interpreted as 'return all
              parents', and a list will be returned.
        
              Since the original command returned None if there is no parent,
              to sync with this behavior, None will be returned if generations
              is out of bounds (no IndexError will be thrown).
        
            - added optional arrays keyword arg, which if True, will also
              traverse from an array element to an array plug
        
        :rtype: `Attribute`
        """
    
        pass
    
    
    def getRange(self):
        """
        attributeQuery -range
            returns a two-element list containing min and max. if the attribute does not have
            a softMin or softMax the corresponding element will be set to None.
        
        :rtype: `float`
        """
    
        pass
    
    
    def getSetAttrCmds(self, valueSelector='all', useLongNames=False):
        """
        Returns an array of strings containing  setAttr  commands for this plug and all of its descendent plugs.
        
        :Parameters:
            valueSelector : `Attribute.MValueSelector`
                " cellpadding="3">  kAll- return setAttr commands for the plug and its children, regardless of their values.    kNonDefault- only return setAttr commands for the plug or its children if they are not at their default values.    kChanged- for nodes from referenced files, setAttr commands are only returned if the plug or one of its children has changed since its file was loaded. For all other nodes, the behaviour is the same a kNonDefault.   Note that if the plug is compound and one of its children has changed, then setAttrs will be generated for *all* of its children, even those which have not changed.   (default: kAll)   
        
                values: 'all', 'nonDefault', 'changed', 'lastAttrSelector'
            useLongNames : `bool`
                Normally, the returned commands will use the short names for flags and attributes. If this parameter is true then their long names will be used instead. (default: false)
        
        
        :rtype: `list` list
        
        Derived from api method `maya.OpenMaya.MPlug.getSetAttrCmds`
        """
    
        pass
    
    
    def getSiblings(self):
        """
        attributeQuery -listSiblings
        
        :rtype: `Attribute` list
        """
    
        pass
    
    
    def getSoftMax(self):
        """
        attributeQuery -softMax
            Returns None if softMax does not exist.
        
        :rtype: `float`
        """
    
        pass
    
    
    def getSoftMin(self):
        """
        attributeQuery -softMin
            Returns None if softMin does not exist.
        
        :rtype: `float`
        """
    
        pass
    
    
    def getSoftRange(self):
        """
        attributeQuery -softRange
            returns a two-element list containing softMin and softMax. if the attribute does not have
            a softMin or softMax the corresponding element in the list will be set to None.
        
        :rtype: [`float`, `float`]
        """
    
        pass
    
    
    def index(self):
        """
        Returns the logical index of the element this plug refers to. The logical index is a sparse index, equivalent to the array index used in MEL.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MPlug.logicalIndex`
        """
    
        pass
    
    
    def indexMatters(self):
        pass
    
    
    def info(self):
        """
        This method returns a string containing the name of the node this plug belongs to and the attributes that the plug refers to. The string is of the form dependNode:atr1.atr2[].attr3 ...
        
        :rtype: `unicode`
        
        Derived from api method `maya.OpenMaya.MPlug.info`
        """
    
        pass
    
    
    def inputs(self, **kwargs):
        """
        ``listConnections -source 1 -destination 0``
        
        see `Attribute.connections` for the full ist of flags.
        
        :rtype: `PyNode` list
        """
    
        pass
    
    
    def insertInput(self, node, nodeOutAttr, nodeInAttr):
        """
        connect the passed node.outAttr to this attribute and reconnect
        any pre-existing connection into node.inAttr.  if there is no
        pre-existing connection, this method works just like connectAttr.
        
        for example, for two nodes with the connection::
        
            a.out-->b.in
        
        running this command::
        
            b.in.insertInput( 'c', 'out', 'in' )
        
        causes the new connection order (assuming 'c' is a node with 'in' and 'out' attributes)::
        
            a.out-->c.in
            c.out-->b.in
        """
    
        pass
    
    
    def isArray(self):
        """
        This method determines if the plug is an array plug. Array plugs refer to array attributes and contain element plugs.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isArray`
        """
    
        pass
    
    
    def isCaching(self):
        """
        Returns true if this plug or its attribute has its caching flag set.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isCachingFlagSet`
        """
    
        pass
    
    
    def isChild(self):
        """
        This method determines if the plug is a child plug. A child plug's parent is always a compound plug.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isChild`
        """
    
        pass
    
    
    def isCompound(self):
        """
        This method determines if the plug is a compound plug. Compound plugs refer to compound attributes and have child plugs.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isCompound`
        """
    
        pass
    
    
    def isConnectable(self):
        """
        attributeQuery -connectable
        
        :rtype: `bool`
        """
    
        pass
    
    
    def isConnected(self):
        """
        Determines if this plug is connected to one or more plugs.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isConnected`
        """
    
        pass
    
    
    def isConnectedTo(self, other, ignoreUnitConversion=False, checkLocalArray=False, checkOtherArray=False):
        """
        Determine if the attribute is connected to the passed attribute.
        
        If checkLocalArray is True and the current attribute is a multi/array, the current attribute's elements will also be tested.
        
        If checkOtherArray is True and the passed attribute is a multi/array, the passed attribute's elements will also be tested.
        
        If checkLocalArray and checkOtherArray are used together then all element combinations will be tested.
        """
    
        pass
    
    
    def isDestination(self):
        """
        Determines if this plug is connected as a destination.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isDestination`
        """
    
        pass
    
    
    def isDirty(self, **kwargs):
        """
        :rtype: `bool`
        """
    
        pass
    
    
    def isDynamic(self):
        """
        Determines whether the attribute is of dynamic type or not.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isDynamic`
        """
    
        pass
    
    
    def isElement(self):
        """
        This method determines if the plug is an element plug. Element plugs refer to array attributes and are members of array plugs.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isElement`
        """
    
        pass
    
    
    def isFreeToChange(self, checkParents=True, checkChildren=True):
        """
        Returns true if the plug's value is allowed to be set directly. A plug isFreeToChange if it is not locked, and it is not a destination or if it is a destination, then it must be a special case (such as connected to an anim curve).
        
        :Parameters:
            checkParents : `bool`
                Check parent plugs. 
            checkChildren : `bool`
                Check child plugs. 
        
        
        :rtype: `Attribute.FreeToChangeState`
        
        Derived from api method `maya.OpenMaya.MPlug.isFreeToChange`
        """
    
        pass
    
    
    def isFromReferencedFile(self):
        """
        This method determines whether this plug came from a referenced file. A plug is considered to have come from a referenced file if it is connected and that connection was made within a referenced file.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isFromReferencedFile`
        """
    
        pass
    
    
    def isHidden(self):
        """
        attributeQuery -hidden
        
        :rtype: `bool`
        """
    
        pass
    
    
    def isIgnoredWhenRendering(self):
        """
        Determines whether a connection to the attribute should be ignored during rendering.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isIgnoredWhenRendering`
        """
    
        pass
    
    
    def isInChannelBox(self):
        """
        Returns true if this plug or its attribute has its channel box flag set. Attributes will appear in the channel box if their channel box flag is set or if they are keyable.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isChannelBoxFlagSet`
        """
    
        pass
    
    
    def isKeyable(self):
        """
        Determines if this plug is keyable. The default keyability of a plug is determined by its attribute, and can be retrieved using  MFnAttribute::isKeyable . Keyable plugs will be keyed by AutoKey and the Set Keyframe UI. Non-keyable plugs prevent the user from setting keys via the obvious UI provided for keying. Being non-keyable is not a hard block against adding keys to an attribute.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isKeyable`
        """
    
        pass
    
    
    def isLocked(self):
        """
        Determines the locked state of this plug's value. A plug's locked state determines whether or not the plug's value can be changed.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isLocked`
        """
    
        pass
    
    
    def isMulti(self):
        """
        This method determines if the plug is an array plug. Array plugs refer to array attributes and contain element plugs.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isArray`
        """
    
        pass
    
    
    def isMuted(self):
        """
        mute -q
        
        :rtype: `bool`
        """
    
        pass
    
    
    def isNetworked(self):
        """
        This method determines if the plug is networked or non-networked.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isNetworked`
        """
    
        pass
    
    
    def isNull(self):
        """
        This method determines whether this plug is valid. A plug is valid if it refers to an attribute.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isNull`
        """
    
        pass
    
    
    def isProcedural(self):
        """
        This method determines if the plug is a procedural plug. A procedural plug is one which is created by Maya's internal procedures or by the nodes themselves and which should not be saved to or restored from files.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isProcedural`
        """
    
        pass
    
    
    def isSettable(self):
        """
        getAttr -settable
        
        :rtype: `bool`
        """
    
        pass
    
    
    def isSource(self):
        """
        Determines if this plug is connected as a source.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MPlug.isSource`
        """
    
        pass
    
    
    def isUsedAsColor(self):
        """
        attributeQuery -usedAsColor
        """
    
        pass
    
    
    def item(self):
        """
        Returns the logical index of the element this plug refers to. The logical index is a sparse index, equivalent to the array index used in MEL.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MPlug.logicalIndex`
        """
    
        pass
    
    
    def iterDescendants(self, levels=None, leavesOnly=False):
        """
        Yields all attributes "below" this attribute, recursively,
        traversing down both through multi/array elements, and through
        compound attribute children.
        
        Parameters
        ----------
        levels : int or None
            the number of levels deep to descend; each descent from an array
            to an array element, and from a compound to it's child, counts as
            one level (so, if you have a compound-multi attr parentAttr, to get
            to parentAttr[0].child would require levels to be at least 2); None
            means no limit
        leavesOnly : bool
            if True, then results will only be returned if they do not have any
            children to recurse into (either because it's not an arry or
            compound, or because we've hit the levels limit)
        """
    
        pass
    
    
    def lastPlugAttr(self, longName=False):
        """
            >>> from pymel.core import *
            >>> at = SCENE.persp.t.tx
            >>> at.lastPlugAttr(longName=False)
            u'tx'
            >>> at.lastPlugAttr(longName=True)
            u'translateX'
        
        :rtype: `unicode`
        """
    
        pass
    
    
    def lock(self, checkReference=False):
        """
        setAttr -locked 1
        """
    
        pass
    
    
    def logicalIndex(self):
        """
        Returns the logical index of the element this plug refers to. The logical index is a sparse index, equivalent to the array index used in MEL.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MPlug.logicalIndex`
        """
    
        pass
    
    
    def longName(self, fullPath=False):
        """
            >>> from pymel.core import *
            >>> at = SCENE.persp.t.tx
            >>> at.longName(fullPath=False)
            u'translateX'
            >>> at.longName(fullPath=True)
            u'translate.translateX'
        
        :rtype: `unicode`
        """
    
        pass
    
    
    def mute(self, **kwargs):
        """
        mute
         Mutes the attribute.
        """
    
        pass
    
    
    def name(self, includeNode=True, longName=True, fullAttrPath=False, fullDagPath=False, placeHolderIndices=True):
        """
        Returns the name of the attribute (plug)
        
            >>> tx = SCENE.persp.t.tx
            >>> tx.name()
            u'persp.translateX'
            >>> tx.name(includeNode=False)
            u'translateX'
            >>> tx.name(longName=False)
            u'persp.tx'
            >>> tx.name(fullAttrPath=True, includeNode=False)
            u'translate.translateX'
        
            >>> vis = SCENE.perspShape.visibility
            >>> vis.name()
            u'perspShape.visibility'
            >>> vis.name(fullDagPath=True)
            u'|persp|perspShape.visibility'
        
            >>> og = SCENE.persp.instObjGroups.objectGroups
            >>> og.name()
            u'persp.instObjGroups[-1].objectGroups'
            >>> og.name(placeHolderIndices=False)
            u'persp.instObjGroups.objectGroups'
        
        :rtype: `unicode`
        """
    
        pass
    
    
    def namespace(self, *args, **kwargs):
        pass
    
    
    def node(self):
        """
        plugNode
        
        :rtype: `DependNode`
        """
    
        pass
    
    
    def nodeName(self):
        """
        The node part of this plug as a string
        
        :rtype: `unicode`
        """
    
        pass
    
    
    def numChildren(self):
        """
        Return the total number of children of this compound plug.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MPlug.numChildren`
        """
    
        pass
    
    
    def numConnectedChildren(self):
        """
        Return the number of children of this plug that are connected in the dependency graph.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MPlug.numConnectedChildren`
        """
    
        pass
    
    
    def numConnectedElements(self):
        """
        Return the total number of connected element plugs belonging to this array plug.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MPlug.numConnectedElements`
        """
    
        pass
    
    
    def numElements(self):
        """
        The number of elements in an array attribute. Raises an error if this is not an array Attribute
        
        Be aware that ``getAttr(..., size=1)`` does not always produce the expected value. It is recommend
        that you use `Attribute.numElements` instead.  This is a maya bug, *not* a pymel bug.
        
            >>> from pymel.core import *
            >>> f=newFile(f=1) #start clean
            >>>
            >>> dls = SCENE.defaultLightSet
            >>> dls.dagSetMembers.numElements()
            0
            >>> nt.SpotLight() # create a light, which adds to the lightSet
            nt.SpotLight(u'spotLightShape1')
            >>> dls.dagSetMembers.numElements()
            1
            >>> nt.SpotLight() # create another light, which adds to the lightSet
            nt.SpotLight(u'spotLightShape2')
            >>> dls.dagSetMembers.numElements()
            2
        
        :rtype: `int`
        """
    
        pass
    
    
    def outputs(self, **kwargs):
        """
        ``listConnections -source 0 -destination 1``
        
        see `Attribute.connections` for the full ist of flags.
        
        :rtype: `PyNode` list
        """
    
        pass
    
    
    def parent(self, generations=1, arrays=False):
        """
        Modifications:
            - added optional generations keyword arg, which gives the number of
              levels up that you wish to go for the parent
        
              Negative values will traverse from the top.
        
              A value of 0 will return the same node.
              The default value is 1.
        
              If generations is None, it will be interpreted as 'return all
              parents', and a list will be returned.
        
              Since the original command returned None if there is no parent,
              to sync with this behavior, None will be returned if generations
              is out of bounds (no IndexError will be thrown).
        
            - added optional arrays keyword arg, which if True, will also
              traverse from an array element to an array plug
        
        :rtype: `Attribute`
        """
    
        pass
    
    
    def plugAttr(self, longName=False, fullPath=False):
        """
            >>> from pymel.core import *
            >>> at = SCENE.persp.t.tx
            >>> at.plugAttr(longName=False, fullPath=False)
            u'tx'
            >>> at.plugAttr(longName=False, fullPath=True)
            u't.tx'
            >>> at.plugAttr(longName=True, fullPath=True)
            u'translate.translateX'
        
        :rtype: `unicode`
        """
    
        pass
    
    
    def plugNode(self):
        """
        plugNode
        
        :rtype: `DependNode`
        """
    
        pass
    
    
    def remove(self, **kwargs):
        """
        removeMultiInstance
        """
    
        pass
    
    
    def removeMultiInstance(self, index=None, break_=False):
        pass
    
    
    def set(attr, *args, **kwargs):
        """
        Sets the value of a dependency node attribute.  No value for the the attribute is needed when the -l/-k/-s flags are
        used. The -type flag is only required when setting a non-numeric attribute. The following chart outlines the syntax of
        setAttr for non-numeric data types: TYPEbelow means any number of values of type TYPE, separated by a space[TYPE]means
        that the value of type TYPEis optionalA|Bmeans that either of Aor Bmay appearIn order to run its examples, first execute
        these commands to create the sample attribute types:sphere -n node; addAttr -ln short2Attr -at short2; addAttr -ln
        short2a -p short2Attr -at short; addAttr -ln short2b -p short2Attr -at short; addAttr -ln short3Attr -at short3; addAttr
        -ln short3a -p short3Attr -at short; addAttr -ln short3b -p short3Attr -at short; addAttr -ln short3c -p short3Attr -at
        short; addAttr -ln long2Attr -at long2; addAttr -ln long2a -p long2Attr -at long; addAttr -ln long2b -p long2Attr -at
        long; addAttr -ln long3Attr -at long3; addAttr -ln long3a -p long3Attr -at long; addAttr -ln long3b -p long3Attr -at
        long; addAttr -ln long3c -p long3Attr -at long; addAttr -ln float2Attr -at float2; addAttr -ln float2a -p float2Attr -at
        float; addAttr -ln float2b -p float2Attr -at float; addAttr -ln float3Attr -at float3; addAttr -ln float3a -p float3Attr
        -at float; addAttr -ln float3b -p float3Attr -at float; addAttr -ln float3c -p float3Attr -at float; addAttr -ln
        double2Attr -at double2; addAttr -ln double2a -p double2Attr -at double; addAttr -ln double2b -p double2Attr -at double;
        addAttr -ln double3Attr -at double3; addAttr -ln double3a -p double3Attr -at double; addAttr -ln double3b -p double3Attr
        -at double; addAttr -ln double3c -p double3Attr -at double; addAttr -ln int32ArrayAttr -dt Int32Array; addAttr -ln
        doubleArrayAttr -dt doubleArray; addAttr -ln pointArrayAttr -dt pointArray; addAttr -ln vectorArrayAttr -dt vectorArray;
        addAttr -ln stringArrayAttr -dt stringArray; addAttr -ln stringAttr -dt string; addAttr -ln matrixAttr -dt matrix;
        addAttr -ln sphereAttr -dt sphere; addAttr -ln coneAttr -dt cone; addAttr -ln meshAttr -dt mesh; addAttr -ln latticeAttr
        -dt lattice; addAttr -ln spectrumRGBAttr -dt spectrumRGB; addAttr -ln reflectanceRGBAttr -dt reflectanceRGB; addAttr -ln
        componentListAttr -dt componentList; addAttr -ln attrAliasAttr -dt attributeAlias; addAttr -ln curveAttr -dt nurbsCurve;
        addAttr -ln surfaceAttr -dt nurbsSurface; addAttr -ln trimFaceAttr -dt nurbsTrimface; addAttr -ln polyFaceAttr -dt
        polyFaces; -type short2Array of two short integersValue Syntaxshort shortValue Meaningvalue1 value2Mel ExamplesetAttr
        node.short2Attr -type short2 1 2;Python Examplecmds.setAttr('node.short2Attr',1,2,type='short2')-type short3Array of
        three short integersValue Syntaxshort short shortValue Meaningvalue1 value2 value3Mel ExamplesetAttr node.short3Attr
        -type short3 1 2 3;Python Examplecmds.setAttr('node.short3Attr',1,2,3,type='short3')-type long2Array of two long
        integersValue Syntaxlong longValue Meaningvalue1 value2Mel ExamplesetAttr node.long2Attr -type long2 1000000
        2000000;Python Examplecmds.setAttr('node.long2Attr',1000000,2000000,type='long2')-type long3Array of three long
        integersValue Syntaxlong long longValue Meaningvalue1 value2 value3Mel ExamplesetAttr node.long3Attr -type long3 1000000
        2000000 3000000;Python Examplecmds.setAttr('node.long3Attr',1000000,2000000,3000000,type='long3')-type
        Int32ArrayVariable length array of long integersValue SyntaxValue MeaningMel ExamplesetAttr node.int32ArrayAttr -type
        Int32Array 2 12 75;Python Examplecmds.setAttr('node.int32ArrayAttr',[2,12,75],type='Int32Array')-type float2Array of two
        floatsValue Syntaxfloat floatValue Meaningvalue1 value2Mel ExamplesetAttr node.float2Attr -type float2 1.1 2.2;Python
        Examplecmds.setAttr('node.float2Attr',1.1,2.2,type='float2')-type float3Array of three floatsValue Syntaxfloat float
        floatValue Meaningvalue1 value2 value3Mel ExamplesetAttr node.float3Attr -type float3 1.1 2.2 3.3;Python
        Examplecmds.setAttr('node.float3Attr',1.1,2.2,3.3,type='float3')-type double2Array of two doublesValue Syntaxdouble
        doubleValue Meaningvalue1 value2Mel ExamplesetAttr node.double2Attr -type double2 1.1 2.2;Python
        Examplecmds.setAttr('node.double2Attr',1.1,2.2,type='double2')-type double3Array of three doublesValue Syntaxdouble
        double doubleValue Meaningvalue1 value2 value3Mel ExamplesetAttr node.double3Attr -type double3 1.1 2.2 3.3;Python
        Examplecmds.setAttr('node.double3Attr',1.1,2.2,3.3,type='double3')-type doubleArrayVariable length array of doublesValue
        SyntaxValue MeaningMel ExamplesetAttr node.doubleArrayAttr -type doubleArray 2 3.14159 2.782;Python Examplecmds.setAttr(
        node.doubleArrayAttr, (2, 3.14159, 2.782,), type=doubleArray)-type matrix4x4 matrix of doublesValue Syntaxdouble double
        double doubledouble double double doubledouble double double doubledouble double double doubleValue Meaningrow1col1
        row1col2 row1col3 row1col4row2col1 row2col2 row2col3 row2col4row3col1 row3col2 row3col3 row3col4row4col1 row4col2
        row4col3 row4col4Alternate Syntaxstring double double doubledouble double doubleintegerdouble double doubledouble double
        doubledouble double doubledouble double doubledouble double doubledouble double doubledouble double double doubledouble
        double double doubledouble double doublebooleanAlternate MeaningxformscaleX scaleY scaleZrotateX rotateY
        rotateZrotationOrder (0=XYZ, 1=YZX, 2=ZXY, 3=XZY, 4=YXZ, 5=ZYX)translateX translateY translateZshearXY shearXZ
        shearYZscalePivotX scalePivotY scalePivotZscaleTranslationX scaleTranslationY scaleTranslationZrotatePivotX rotatePivotY
        rotatePivotZrotateTranslationX rotateTranslationY rotateTranslationZrotateOrientW rotateOrientX rotateOrientY
        rotateOrientZjointOrientW jointOrientX jointOrientY jointOrientZinverseParentScaleX inverseParentScaleY
        inverseParentScaleZcompensateForParentScale Mel ExamplesetAttr node.matrixAttr -type matrix1 0 0 0 0 1 0 0 0 0 1 0 2 3 4
        1;setAttr node.matrixAttr -type matrixxform1 1 1 0 0 0 0 2 3 4 0 0 00 0 0 0 0 0 0 0 0 0 0 1 1 0 0 1 0 1 0 1 1 1 0
        false;Python Examplecmds.setAttr('node.matrixAttr',(1,0,0,0,0,1,0,0,0,0,1,0,2,3,4,1),type='matrix')cmds.setAttr('node.ma
        trixAttr','xform',(1,1,1),(0,0,0),0,(2,3,4),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,1,1),(0,0,1,0),(1,0,1,0),(1,2,3),False,ty
        pe=matrix)-type pointArrayVariable length array of pointsValue SyntaxValue MeaningMel ExamplesetAttr node.pointArrayAttr
        -type pointArray 2 1 1 1 1 2 2 2 1;Python
        Examplecmds.setAttr('node.pointArrayAttr',2,(1,1,1,1),(2,2,2,1),type='pointArray')-type vectorArrayVariable length array
        of vectorsValue SyntaxValue MeaningMel ExamplesetAttr node.vectorArrayAttr -type vectorArray 2 1 1 1 2 2 2;Python
        Examplecmds.setAttr('node.vectorArrayAttr',2,(1,1,1),(2,2,2),type='vectorArray')-type stringCharacter stringValue
        SyntaxstringValue MeaningcharacterStringValueMel ExamplesetAttr node.stringAttr -type stringblarg;Python
        Examplecmds.setAttr('node.stringAttr',blarg,type=string)-type stringArrayVariable length array of stringsValue
        SyntaxValue MeaningMel ExamplesetAttr node.stringArrayAttr -type stringArray 3 abc;Python
        Examplecmds.setAttr('node.stringArrayAttr',3,a,b,c,type='stringArray')-type sphereSphere dataValue SyntaxdoubleValue
        MeaningsphereRadiusExamplesetAttr node.sphereAttr -type sphere 5.0;-type coneCone dataValue Syntaxdouble doubleValue
        MeaningconeAngle coneCapMel ExamplesetAttr node.coneAttr -type cone 45.0 5.0;Python
        Examplecmds.setAttr('node.coneAttr',45.0,5.0,type='cone')-type reflectanceRGBReflectance dataValue Syntaxdouble double
        doubleValue MeaningredReflect greenReflect blueReflectMel ExamplesetAttr node.reflectanceRGBAttr -type reflectanceRGB
        0.5 0.5 0.1;Python Examplecmds.setAttr('node.reflectanceRGBAttr',0.5,0.5,0.1,type='reflectanceRGB')-type
        spectrumRGBSpectrum dataValue Syntaxdouble double doubleValue MeaningredSpectrum greenSpectrum blueSpectrumMel
        ExamplesetAttr node.spectrumRGBAttr -type spectrumRGB 0.5 0.5 0.1;Python
        Examplecmds.setAttr('node.spectrumRGBAttr',0.5,0.5,0.1,type='spectrumRGB')-type componentListVariable length array of
        componentsValue SyntaxValue MeaningMel ExamplesetAttr node.componentListAttr -type componentList 3 cv[1] cv[12]
        cv[3];Python Examplecmds.setAttr('node.componentListAttr',3,'cv[1]','cv[12]','cv[3]',type='componentList')-type
        attributeAliasString alias dataValue Syntaxstring stringValue MeaningnewAlias currentNameMel ExamplesetAttr
        node.attrAliasAttr -type attributeAliasGoUp, translateY, GoLeft, translateX;Python
        Examplecmds.setAttr('node.attrAliasAttr',(GoUp, translateY,GoLeft, translateX),type='attributeAlias')-type
        nurbsCurveNURBS curve dataValue SyntaxValue MeaningMel Example// degree is the degree of the curve(range 1-7)// spans is
        the number of spans // form is open (0), closed (1), periodic (2)// dimension is 2 or 3, depending on the dimension of
        the curve// isRational is true if the curve CVs contain a rational component // knotCount is the size of the knot list//
        knotValue is a single entry in the knot list// cvCount is the number of CVs in the curve//  xCVValue,yCVValue,[zCVValue]
        [wCVValue] is a single CV.//  zCVValue is only present when dimension is 3.//  wCVValue is only present when isRational
        is true.//setAttr node.curveAttr -type nurbsCurve 3 1 0 no 36 0 0 0 1 1 14 -2 3 0 -2 1 0 -2 -1 0 -2 -3 0;-type
        nurbsSurfaceNURBS surface dataValue Syntaxint int int int bool Value MeaninguDegree vDegree uForm vForm
        isRationalTRIM|NOTRIMExample// uDegree is degree of the surface in U direction (range 1-7)// vDegree is degree of the
        surface in V direction (range 1-7)// uForm is open (0), closed (1), periodic (2) in U direction// vForm is open (0),
        closed (1), periodic (2) in V direction// isRational is true if the surface CVs contain a rational component//
        uKnotCount is the size of the U knot list//  uKnotValue is a single entry in the U knot list// vKnotCount is the size of
        the V knot list//  vKnotValue is a single entry in the V knot list// If TRIMis specified then additional trim
        information is expected// If NOTRIMis specified then the surface is not trimmed// cvCount is the number of CVs in the
        surface//  xCVValue,yCVValue,zCVValue [wCVValue]is a single CV.//  zCVValue is only present when dimension is 3.//
        wCVValue is only present when isRational is true//setAttr node.surfaceAttr -type nurbsSurface 3 3 0 0 no 6 0 0 0 1 1 16
        0 0 0 1 1 116 -2 3 0 -2 1 0 -2 -1 0 -2 -3 0-1 3 0 -1 1 0 -1 -1 0 -1 -3 01 3 0 1 1 0 1 -1 0 1 -3 03 3 0 3 1 0 3 -1 0 3 -3
        0;-type nurbsTrimfaceNURBS trim face dataValue SyntaxValue MeaningExample// flipNormal if true turns the surface inside
        out// boundaryCount: number of boundaries// boundaryType: // tedgeCountOnBoundary    : number of edges in a boundary//
        splineCountOnEdge    : number of splines in an edge in// edgeTolerance        : tolerance used to build the 3d edge//
        isEdgeReversed        : if true, the edge is backwards// geometricContinuity    : if true, the edge is tangent
        continuous// splineCountOnPedge    : number of splines in a 2d edge// isMonotone            : if true, curvature is
        monotone// pedgeTolerance        : tolerance for the 2d edge//-type polyFacePolygon face dataValue SyntaxfhmfmhmufcValue
        MeaningfhmfmhmufcExample// This data type (polyFace) is meant to be used in file I/O// after setAttrs have been written
        out for vertex position// arrays, edge connectivity arrays (with corresponding start// and end vertex descriptions),
        texture coordinate arrays and// color arrays.  The reason is that this data type references// all of its data through
        ids created by the former types.//// fspecifies the ids of the edges making up a face -//     negative value if the edge
        is reversed in the face// hspecifies the ids of the edges making up a hole -//     negative value if the edge is
        reversed in the face// mfspecifies the ids of texture coordinates (uvs) for a face.//     This data type is obsolete as
        of version 3.0. It is replaced by mu.// mhspecifies the ids of texture coordinates (uvs) for a hole//     This data type
        is obsolete as of version 3.0. It is replaced by mu.// muThe  first argument refers to the uv set. This is a zero-
        based//     integer number. The second argument refers to the number of vertices (n)//     on the face which have valid
        uv values. The last n values are the uv//     ids of the texture coordinates (uvs) for the face. These indices//     are
        what used to be represented by the mfand mhspecification.//     There may be more than one muspecification, one for each
        unique uv set.// fcspecifies the color index values for a face//setAttr node.polyFaceAttr -type polyFaces f3 1 2 3 fc3 4
        4 6;-type meshPolygonal meshValue SyntaxValue Meaningvvn[vtesmooth|hard]Example// vspecifies the vertices of the
        polygonal mesh// vnspecifies the normal of each vertex// vtis optional and specifies a U,V texture coordinate for each
        vertex// especifies the edge connectivity information between vertices//setAttr node.meshAttr -type mesh v3 0 0 0 0 1 0
        0 0 1vn3 1 0 0 1 0 0 1 0 0vt3 0 0 0 1 1 0e3 0 1 hard1 2 hard2 0 hard;-type latticeLattice dataValue SyntaxValue
        MeaningsDivisionCount tDivisionCount uDivisionCountExample// sDivisionCount is the horizontal lattice division count//
        tDivisionCount is the vertical lattice division count// uDivisionCount is the depth lattice division count// pointCount
        is the total number of lattice points// pointX,pointY,pointZ is one lattice point.  The list is//   specified varying
        first in S, then in T, last in U so the//   first two entries are (S=0,T=0,U=0) (s=1,T=0,U=0)//setAttr node.latticeAttr
        -type lattice 2 5 2 20-2 -2 -2 2 -2 -2 -2 -1 -2 2 -1 -2 -2 0 -22 0 -2 -2 1 -2 2 1 -2 -2 2 -2 2 2 -2-2 -2 2 2 -2 2 -2 -1
        2 2 -1 2 -2 0 22 0 2 -2 1 2 2 1 2 -2 2 2 2 2 2;In query mode, return type is based on queried flag.
        
        Maya Bug Fix:
          - setAttr did not work with type matrix.
        
        Modifications:
          - No need to set type, this will automatically be determined
          - Adds support for passing a list or tuple as the second argument for datatypes such as double3.
          - When setting stringArray datatype, you no longer need to prefix the list with the number of elements - just pass a list or tuple as with other arrays
          - Added 'force' kwarg, which causes the attribute to be added if it does not exist.
                - if no type flag is passed, the attribute type is based on type of value being set (if you want a float, be sure to format it as a float, e.g.  3.0 not 3)
                - currently does not support compound attributes
                - currently supported python-to-maya mappings:
        
                    ============ ===========
                    python type  maya type
                    ============ ===========
                    float        double
                    ------------ -----------
                    int          long
                    ------------ -----------
                    str          string
                    ------------ -----------
                    bool         bool
                    ------------ -----------
                    Vector       double3
                    ------------ -----------
                    Matrix       matrix
                    ------------ -----------
                    [str]        stringArray
                    ============ ===========
        
        
            >>> addAttr( 'persp', longName= 'testDoubleArray', dataType='doubleArray')
            >>> setAttr( 'persp.testDoubleArray', [0,1,2])
            >>> setAttr( 'defaultRenderGlobals.preMel', 'sfff')
        
          - Added ability to set enum attributes using the string values; this may be
            done either by setting the 'asString' kwarg to True, or simply supplying
            a string value for an enum attribute.
        
        Flags:
          - alteredValue : av              (bool)          [create]
              The value is only the current value, which may change in the next evalution (if the attribute has an incoming
              connection). This flag is only used during file I/O, so that attributes with incoming connections do not have their data
              overwritten during the first evaluation after a file is opened.
        
          - caching : ca                   (bool)          [create]
              Sets the attribute's internal caching on or off. Not all attributes can be defined as caching. Only those attributes
              that are not defined by default to be cached can be made caching.  As well, multi attribute elements cannot be made
              caching. Caching also affects child attributes for compound attributes.
        
          - capacityHint : ch              (int)           [create]
              Used to provide a memory allocation hint to attributes where the -size flag cannot provide enough information. This flag
              is optional and is primarily intended to be used during file I/O. Only certain attributes make use of this flag, and the
              interpretation of the flag value varies per attribute. This flag is currently used by (node.attribute): mesh.face -
              hints the total number of elements in the face edge lists
        
          - channelBox : cb                (bool)          [create]
              Sets the attribute's display in the channelBox on or off. Keyable attributes are always display in the channelBox
              regardless of the channelBox settting.
        
          - clamp : c                      (bool)          [create]
              For numeric attributes, if the value is outside the range of the attribute, clamp it to the min or max instead of
              failing
        
          - keyable : k                    (bool)          [create]
              Sets the attribute's keyable state on or off.
        
          - lock : l                       (bool)          [create]
              Sets the attribute's lock state on or off.
        
          - size : s                       (int)           [create]
              Defines the size of a multi-attribute array. This is only a hint, used to help allocate memory as efficiently as
              possible.
        
          - type : typ                     (unicode)       [create]
              Identifies the type of data.  If the -type flag is not present, a numeric type is assumed.                  Flag can
              have multiple arguments, passed either as a tuple or a list.
        
        
        Derived from mel command `maya.cmds.setAttr`
        """
    
        pass
    
    
    def setAlias(self, alias):
        """
        Sets the alias for this attribute (similar to aliasAttr).
        """
    
        pass
    
    
    def setCaching(self, isCaching):
        """
        Sets whether this plug is cached internally. Note: turning caching on for a plug will force the plug to become networked. Network plugs take longer to look up in the DG; therefore you should only make a plug cached only if you are certain that the network plug look-up will take less than the saved evaluation cost.
        
        :Parameters:
            isCaching : `bool`
                True if this plug should be cached
        
        Derived from api method `maya.OpenMaya.MPlug.setCaching`
        """
    
        pass
    
    
    def setDirty(self, **kwargs):
        pass
    
    
    def setEnums(attr, enums):
        """
        Set the enumerators for an enum attribute.
        """
    
        pass
    
    
    def setKey(self, **kwargs):
        """
        This command creates keyframes for the specified objects, or the active objects if none are specified on the command
        line. The default time for the new keyframes is the current time. Override this behavior with the -tflag on the command
        line. The default value for the keyframe is the current value of the attribute for which a keyframe is set.  Override
        this behavior with the -vflag on the command line. When setting keyframes on animation curves that do not have timeas an
        input attribute (ie, they are unitless animation curves), use -f/-floatto specify the unitless value at which to set a
        keyframe. The -time and -float flags may be combined in one command. This command sets up Dependency Graph relationships
        for proper evaluation of a given attribute at a given time.
        
        Flags:
          - animLayer : al                 (unicode)       [create]
              Specifies that the new key should be placed in the specified animation layer. Note that if the objects being keyframed
              are not already part of the layer, this flag will be ignored.
        
          - animated : an                  (bool)          [create]
              Add the keyframe only to the attribute(s) that have already a keyframe on. Default: false
        
          - attribute : at                 (unicode)       [create]
              Attribute name to set keyframes on.
        
          - breakdown : bd                 (bool)          [create,query,edit]
              Sets the breakdown state for the key.  Default is false
        
          - clip : c                       (unicode)       [create]
              Specifies that the new key should be placed in the specified clip. Note that if the objects being keyframed are not
              already part of the clip, this flag will be ignored.
        
          - controlPoints : cp             (bool)          [create]
              Explicitly specify whether or not to include the control points of a shape (see -sflag) in the list of attributes.
              Default: false.
        
          - dirtyDG : dd                   (bool)          [create]
              Allow dirty messages to be sent out when a keyframe is set.
        
          - float : f                      (float)         [create]
              Float time at which to set a keyframe on float-based animation curves.
        
          - hierarchy : hi                 (unicode)       [create]
              Controls the objects this command acts on, relative to the specified (or active) target objects. Valid values are
              above,below,both,and none.Default is hierarchy -query
        
          - identity : id                  (bool)          [create]
              Sets an identity key on an animation layer.  An identity key is one that nullifies the effect of the anim layer.  This
              flag has effect only when the attribute being keyed is being driven by animation layers.
        
          - inTangentType : itt            (unicode)       [create]
              The in tangent type for keyframes set by this command. Valid values are: auto, clamped, fast, flat, linear, plateau,
              slow, spline, and stepnextDefault is keyTangent -q -g -inTangentType
        
          - insert : i                     (bool)          [create]
              Insert keys at the given time(s) and preserve the shape of the animation curve(s). Note: the tangent type on inserted
              keys will be fixed so that the curve shape can be preserved.
        
          - insertBlend : ib               (bool)          [create]
              If true, a pairBlend node will be inserted for channels that have nodes other than animCurves driving them, so that such
              channels can have blended animation. If false, these channels will not have keys inserted. If the flag is not specified,
              the blend will be inserted based on the global preference for blending animation.
        
          - minimizeRotation : mr          (bool)          [create]
              For rotations, ensures that the key that is set is a minimum distance away from the previous key.  Default is false
        
          - noResolve : nr                 (bool)          [create]
              When used with the -value flag, causes the specified value to be set directly onto the animation curve, without
              attempting to resolve the value across animation layers.
        
          - outTangentType : ott           (unicode)       [create]
              The out tangent type for keyframes set by this command. Valid values are: auto, clamped, fast, flat, linear, plateau,
              slow, spline, step, and stepnext. Default is keyTangent -q -g -outTangentType
        
          - respectKeyable : rk            (bool)          [create]
              When used with the -attribute flag, prevents the keying of the non keyable attributes.
        
          - shape : s                      (bool)          [create]
              Consider attributes of shapes below transforms as well, except controlPoints.  Default: true
        
          - time : t                       (time)          [create]
              Time at which to set a keyframe on time-based animation curves.
        
          - useCurrentLockedWeights : lw   (bool)          [create]
              If we are setting a key over an existing key, use that key tangent's locked weight value for the new locked weight
              value.  Default is false
        
          - value : v                      (float)         [create]
              Value at which to set the keyframe. Using the value flag will not cause the keyed attribute to change to the specified
              value until the scene re-evaluates. Therefore, if you want the attribute to update to the new value immediately, use the
              setAttr command in addition to setting the key.                  Flag can have multiple arguments, passed either as a
              tuple or a list.
        
        
        Derived from mel command `maya.cmds.setKeyframe`
        """
    
        pass
    
    
    def setKeyable(self, keyable):
        """
        This overrides the default keyability of a plug set with  MFnAttribute::setKeyable . Keyable plugs will be keyed by AutoKey and the Set Keyframe UI. Non-keyable plugs prevent the user from setting keys via the obvious UI provided for keying. Being non-keyable is not a hard block against adding keys to an attribute.
        
        :Parameters:
            keyable : `bool`
                True if this plug should be keyable
        
        Derived from api method `maya.OpenMaya.MPlug.setKeyable`
        """
    
        pass
    
    
    def setLocked(self, locked, checkReference=False):
        """
        Sets the locked state for this plug's value. A plug's locked state determines whether or not the plug's value can be changed.
        
        :Parameters:
            locked : `bool`
                True if this plug's value is to be locked
            checkReference : `bool`
                Set True to raise errors on referenced attributes.
        
                By default pymel and the maya api do not check if the node is referenced before
                setting the locked state. This is unsafe because changes to the locked state on
                referenced nodes are not saved with the scene.
        """
    
        pass
    
    
    def setMax(self, newMax):
        pass
    
    
    def setMin(self, newMin):
        pass
    
    
    def setNumElements(self, elements):
        """
        The method is used to pre-allocate the number of elements that an array plug will contain. The plug passed to this method must be an array plug and there must be no elements already allocated.
        
        :Parameters:
            elements : `int`
                new array size
        
        Derived from api method `maya.OpenMaya.MPlug.setNumElements`
        """
    
        pass
    
    
    def setRange(self, *args):
        """
        provide a min and max value as a two-element tuple or list, or as two arguments to the
        method. To remove a limit, provide a None value.  for example:
        
            >>> from pymel.core import *
            >>> s = polyCube()[0]
            >>> s.addAttr( 'new' )
            >>> s.new.setRange( -2, None ) #sets just the min to -2 and removes the max limit
            >>> s.new.setMax( 3 ) # sets just the max value and leaves the min at its previous default
            >>> s.new.getRange()
            [-2.0, 3.0]
        """
    
        pass
    
    
    def setSoftMax(self, newMax):
        pass
    
    
    def setSoftMin(self, newMin):
        pass
    
    
    def setSoftRange(self, *args):
        pass
    
    
    def shortName(self, fullPath=False):
        """
            >>> from pymel.core import *
            >>> at = SCENE.persp.t.tx
            >>> at.shortName(fullPath=False)
            u'tx'
            >>> at.shortName(fullPath=True)
            u't.tx'
        
        :rtype: `unicode`
        """
    
        pass
    
    
    def showInChannelBox(self, inChannelBox):
        """
        Sets whether this plug is displayed in the channel box. This overrides the default display of a plug set with  MFnAttribute::setChannelBox . Keyable attributes are always shown in the channel box so this flag is ignored on keyable plugs.
        
        :Parameters:
            inChannelBox : `bool`
                True if this plug should be displayed in the channel box
        
        Derived from api method `maya.OpenMaya.MPlug.setChannelBox`
        """
    
        pass
    
    
    def siblings(self):
        """
        attributeQuery -listSiblings
        
        :rtype: `Attribute` list
        """
    
        pass
    
    
    def type(self):
        """
        getAttr -type
        
        :rtype: `unicode`
        """
    
        pass
    
    
    def unlock(self, checkReference=False):
        """
        setAttr -locked 0
        """
    
        pass
    
    
    def unmute(self, **kwargs):
        """
        mute -disable -force
         Unmutes the attribute
        """
    
        pass
    
    
    FreeToChangeState = {}
    
    
    MValueSelector = {}
    
    
    __apicls__ = None
    
    
    
    
    __readonly__ = {}
    
    
    attrItemReg = None


class MayaComponentError(MayaAttributeError):
    pass


class MItComponent(Component):
    """
    Abstract base class for pymel components that can be accessed via iterators.
    
    (ie, `MeshEdge`, `MeshVertex`, and `MeshFace` can be wrapped around
    MItMeshEdge, etc)
    
    If deriving from this class, you should set __apicls__ to an appropriate
    MIt* type - ie, for MeshEdge, you would set __apicls__ = _api.MItMeshEdge
    """
    
    
    
    def __apimfn__(self):
        pass
    
    
    def __apimit__(self, alwaysUnindexed=False):
        pass
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    __readonly__ = {}


class Pivot(Component):
    __readonly__ = {}


class MayaAttributeEnumError(MayaAttributeError):
    def __init__(self, node=None, enum=None):
        pass
    
    
    def __str__(self):
        pass


class DimensionedComponent(Component):
    """
    Components for which having a __getitem__ of some sort makes sense
    
    ie, myComponent[X] would be reasonable.
    """
    
    
    
    def __getitem__(self, item):
        pass
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def currentDimension(self):
        """
        Returns the dimension index that an index operation - ie, self[...] /
        self.__getitem__(...) - will operate on.
        
        If the component is completely specified (ie, all dimensions are
        already indexed), then None is returned.
        """
    
        pass
    
    
    VALID_SINGLE_INDEX_TYPES = []
    
    
    __readonly__ = {}
    
    
    dimensions = 0


class DiscreteComponent(DimensionedComponent):
    """
    Components whose dimensions are discretely indexed.
    
    Ie, there are a finite number of possible components, referenced by integer
    indices.
    
    Example: polyCube.vtx[38], f.cv[3][2]
    
    Derived classes should implement:
    _dimLength
    """
    
    
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def __iter__(self):
        pass
    
    
    def __len__(self):
        pass
    
    
    def count(self):
        pass
    
    
    def currentItem(self):
        pass
    
    
    def currentItemIndex(self):
        """
        Returns the component indices for the current item in this component
        group
        
        If the component type has more then one dimension, the return result
        will be a ComponentIndex object which is a sub-class of tuple; otherwise,
        it will be a single int.
        
        These values correspond to the indices that you would use when selecting
        components in mel - ie, vtx[5], cv[3][2]
        """
    
        pass
    
    
    def getIndex(self):
        """
        Returns the current 'flat list' index for this group of components -
        ie, if this component holds the vertices:
            [5, 7, 12, 13, 14, 25]
        then if the 'flat list' index is 2, then we are pointing to vertex 12.
        """
    
        pass
    
    
    def indices(self):
        """
        A list of all the indices contained by this component.
        """
    
        pass
    
    
    def indicesIter(self):
        """
        An iterator over all the indices contained by this component,
        as ComponentIndex objects (which are a subclass of tuple).
        """
    
        pass
    
    
    def next(self):
        pass
    
    
    def reset(self):
        pass
    
    
    def setIndex(self, index):
        pass
    
    
    def totalSize(self):
        """
        The maximum possible number of components
        
        ie, for a polygon cube, the totalSize for verts would be 8, for edges
        would be 12, and for faces would be 6
        """
    
        pass
    
    
    VALID_SINGLE_INDEX_TYPES = ()
    
    
    __readonly__ = {}


class ContinuousComponent(DimensionedComponent):
    """
    Components whose dimensions are continuous.
    
    Ie, there are an infinite number of possible components, referenced by
    floating point parameters.
    
    Example: nurbsCurve.u[7.48], nurbsSurface.uv[3.85][2.1]
    
    Derived classes should implement:
    _dimRange
    """
    
    
    
    def __iter__(self):
        pass
    
    
    VALID_SINGLE_INDEX_TYPES = ()
    
    
    __readonly__ = {}


class MayaParticleAttributeError(MayaComponentError):
    pass


class Component3D(DiscreteComponent):
    __readonly__ = {}
    
    
    dimensions = 3


class Component1D64(DiscreteComponent):
    def __len__(self):
        pass
    
    
    def totalSize(self):
        pass
    
    
    __readonly__ = {}
    
    
    dimensions = 2


class Component1DFloat(ContinuousComponent):
    def index(self):
        pass
    
    
    __readonly__ = {}
    
    
    dimensions = 1


class Component2D(DiscreteComponent):
    __readonly__ = {}
    
    
    dimensions = 2


class Component1D(DiscreteComponent):
    def currentItem(self):
        pass
    
    
    def currentItemIndex(self):
        """
        Returns the component indices for the current item in this component
        group
        
        If the component type has more then one dimension, the return result
        will be a ComponentIndex object which is a sub-class of tuple; otherwise,
        it will be a single int.
        
        These values correspond to the indices that you would use when selecting
        components in mel - ie, vtx[5], cv[3][2]
        """
    
        pass
    
    
    def index(self):
        pass
    
    
    def indicesIter(self):
        """
        An iterator over all the indices contained by this component,
        as integers.
        """
    
        pass
    
    
    def name(self):
        pass
    
    
    __readonly__ = {}
    
    
    dimensions = 1


class Component2DFloat(ContinuousComponent):
    __readonly__ = {}
    
    
    dimensions = 2


class MeshUV(Component1D):
    __readonly__ = {}


class SubdEdge(Component1D64):
    __readonly__ = {}


class NurbsSurfaceEP(Component2D):
    __readonly__ = {}


class ParticleComponent(Component1D):
    def __getattr__(self, attr):
        pass
    
    
    def attr(self, attr):
        pass
    
    
    __readonly__ = {}


class SubdVertex(Component1D64):
    __readonly__ = {}


class NurbsSurfaceFace(Component2D):
    __readonly__ = {}


class NurbsCurveKnot(Component1D):
    __readonly__ = {}


class NurbsSurfaceIsoparm(Component2DFloat):
    def __init__(self, *args, **kwargs):
        pass
    
    
    __readonly__ = {}


class NurbsCurveParameter(Component1DFloat):
    __readonly__ = {}


class MeshVertexFace(Component2D):
    def __melobject__(self):
        """
        # getting all the mel strings for MeshVertexFace is SLLOOOWW - so check if
        # it's complete, and if so, just return the .vtxFace[*] form
        """
    
        pass
    
    
    def totalSize(self):
        pass
    
    
    __readonly__ = {}


class NurbsSurfaceCV(Component2D):
    __readonly__ = {}


class SubdUV(Component1D):
    def totalSize(self):
        pass
    
    
    __readonly__ = {}


class SubdFace(Component1D64):
    __readonly__ = {}


class NurbsCurveEP(Component1D):
    __readonly__ = {}


class LatticePoint(Component3D):
    __readonly__ = {}


class NurbsSurfaceKnot(Component2D):
    __readonly__ = {}


class MItComponent1D(MItComponent, Component1D):
    __readonly__ = {}


class MeshEdge(MItComponent1D):
    def connectedEdges(self):
        """
        :rtype: `MeshEdge` list
        """
    
        pass
    
    
    def connectedFaces(self):
        """
        :rtype: `MeshFace` list
        """
    
        pass
    
    
    def connectedVertices(self):
        """
        :rtype: `MeshVertex` list
        """
    
        pass
    
    
    def getLength(self, space='preTransform'):
        """
        This method returns the length of the current edge.
        
        :Parameters:
            space : `Space.Space`
                Coordinate space in which to perform the operation.
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `float`
        
        Derived from api method `maya.OpenMaya.MSpace.getLength`
        """
    
        pass
    
    
    def getPoint(self, index, space='preTransform'):
        """
        Return the position of the specified vertex of the current edge.
        
        :Parameters:
            index : `int`
                The vertex of the edge we wish to examine (0 or 1) 
            space : `Space.Space`
                The coordinate system for this operation 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Point`
        
        Derived from api method `maya.OpenMaya.MSpace.point`
        """
    
        pass
    
    
    def isConnectedTo(self, component):
        """
        :rtype: bool
        """
    
        pass
    
    
    def isConnectedToEdge(self, index):
        """
        This method determines whether the given edge is connected to the current edge
        
        :Parameters:
            index : `int`
                Index of edge to check. 
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshEdge.connectedToEdge`
        """
    
        pass
    
    
    def isConnectedToFace(self, index):
        """
        This method determines whether the given face contains the current edge
        
        :Parameters:
            index : `int`
                Index of face to check. 
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshEdge.connectedToFace`
        """
    
        pass
    
    
    def isOnBoundary(self):
        """
        This method checks to see if the current edge is a border edge.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshEdge.onBoundary`
        """
    
        pass
    
    
    def isSmooth(self):
        """
        This method determines if the current edge in the iteration is smooth (soft).
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshEdge.isSmooth`
        """
    
        pass
    
    
    def numConnectedEdges(self):
        """
        This method returns the number of edges connected to the current edge.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshEdge.numConnectedEdges`
        """
    
        pass
    
    
    def numConnectedFaces(self):
        """
        This method returns the number of faces (1 or 2 ) connected to the current edge.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshEdge.numConnectedFaces`
        """
    
        pass
    
    
    def setPoint(self, point, index, space='preTransform'):
        """
        Set the specified vertex of the current edge to the given value.
        
        :Parameters:
            point : `Point`
                The new value for the edge 
            index : `int`
                The vertex index of the current edge we wish to set (0 or 1) 
            space : `Space.Space`
                The coordinate system for this operation
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.setPoint`
        """
    
        pass
    
    
    def setSmoothing(self, smooth=True):
        """
        This method sets the current edge to be hard or smooth (soft). The  cleanupSmoothing  method is no longer required to be called after setSmoothing in Maya3.0 and later versions.
        
        :Parameters:
            smooth : `bool`
                if true the edge will be smooth (soft), otherwise the edge will be hard.
        
        Derived from api method `maya.OpenMaya.MItMeshEdge.setSmoothing`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def updateSurface(self):
        """
        Signal that this polygonal surface has changed and needs to redraw itself.
        Derived from api method `maya.OpenMaya.MItMeshEdge.updateSurface`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    __apicls__ = None
    
    
    __readonly__ = {}


class MeshFace(MItComponent1D):
    def connectedEdges(self):
        """
        :rtype: `MeshEdge` list
        """
    
        pass
    
    
    def connectedFaces(self):
        """
        :rtype: `MeshFace` list
        """
    
        pass
    
    
    def connectedVertices(self):
        """
        :rtype: `MeshVertex` list
        """
    
        pass
    
    
    def geomChanged(self):
        """
        Reset the geom pointer in the  MItMeshPolygon . This is now being handled automatically inside the iterator, and users should no longer need to call this method directly to sync up the iterator to changes made by  MFnMesh
        Derived from api method `maya.OpenMaya.MItMeshPolygon.geomChanged`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def getArea(self, space='preTransform'):
        """
        This method gets the area of the face
        
        :Parameters:
            space : `Space.Space`
                World Space or Object Space
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `float`
        
        Derived from api method `maya.OpenMaya.MSpace.getArea`
        """
    
        pass
    
    
    def getAxisAtUV(self, uvPoint, space='preTransform', uvSet=None, tolerance=0.0):
        """
        Return the axis of the point at the given UV value in the current polygon.
        
        :Parameters:
            uvPoint : (`float`, `float`)
                The UV value to try to locate 
            space : `Space.Space`
                The coordinate system for this operation 
        
                values: 'transform', 'preTransform', 'object', 'world'
            uvSet : `unicode`
                UV set to work with 
            tolerance : `float`
                tolerance value to compare float data type
        
        
        :rtype: (`Vector`, `Vector`, `Vector`)
        
        Derived from api method `maya.OpenMaya.MSpace.getAxisAtUV`
        """
    
        pass
    
    
    def getColor(self, colorSetName=None):
        """
        This method gets the average color of the all the vertices in this face
        
        :Parameters:
            colorSetName : `unicode`
                Name of the color set.
        
        
        :rtype: `Color`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getColor`
        """
    
        pass
    
    
    def getColorIndex(self, vertexIndex, colorSetName=None):
        """
        This method returns the colorIndex for a vertex of the current face.
        
        :Parameters:
            vertexIndex : `int`
                Face-relative index of vertex. 
            colorSetName : `unicode`
                Name of the color set.
        
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getColorIndex`
        """
    
        pass
    
    
    def getColorIndices(self, colorSetName=None):
        """
        This method returns the colorIndices for each vertex on the face.
        
        :Parameters:
            colorSetName : `unicode`
                Name of the color set.
        
        
        :rtype: `int` list
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getColorIndices`
        """
    
        pass
    
    
    def getColors(self, colorSetName=None):
        """
        This method gets the color of the each vertex in the current face.
        
        :Parameters:
            colorSetName : `unicode`
                Name of the color set.
        
        
        :rtype: `Color` list
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getColors`
        """
    
        pass
    
    
    def getEdges(self):
        """
        This method gets the indices of the edges contained in the current face.
        
        :rtype: `int` list
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getEdges`
        """
    
        pass
    
    
    def getNormal(self, space='preTransform'):
        """
        Return the face normal of the current polygon.
        
        :Parameters:
            space : `Space.Space`
                The transformation space
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Vector`
        
        Derived from api method `maya.OpenMaya.MSpace.getNormal`
        """
    
        pass
    
    
    def getNormals(self, space='preTransform'):
        """
        Returns the normals for all vertices in the current face
        
        :Parameters:
            space : `Space.Space`
                The transformation space
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Vector` list
        
        Derived from api method `maya.OpenMaya.MSpace.getNormals`
        """
    
        pass
    
    
    def getPoint(self, index, space='preTransform'):
        """
        Return the position of the vertex at  index  in the current polygon.
        
        :Parameters:
            index : `int`
                The face-relative index of the vertex in the current polygon 
            space : `Space.Space`
                The coordinate system for this operation 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Point`
        
        Derived from api method `maya.OpenMaya.MSpace.point`
        """
    
        pass
    
    
    def getPointAtUV(self, uvPoint, space='preTransform', uvSet=None, tolerance=0.0):
        """
        Return the position of the point at the given UV value in the current polygon.
        
        :Parameters:
            uvPoint : (`float`, `float`)
                The UV value to try to locate 
            space : `Space.Space`
                The coordinate system for this operation 
        
                values: 'transform', 'preTransform', 'object', 'world'
            uvSet : `unicode`
                UV set to work with 
            tolerance : `float`
                tolerance value to compare float data type
        
        
        :rtype: `Point`
        
        Derived from api method `maya.OpenMaya.MSpace.getPointAtUV`
        """
    
        pass
    
    
    def getPoints(self, space='preTransform'):
        """
        Retrieves the positions of the vertices on the current face/polygon that the iterator is pointing to. Vertex positions will be inserted into the given array and will be indexed using face-relative vertex IDs (ie. ordered from 0 to (vertexCount of the face) - 1), which should not be confused with the vertexIDs of each vertex in relation to the entire mesh object.
        
        :Parameters:
            space : `Space.Space`
                The coordinate system for this operation 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Point` list
        
        Derived from api method `maya.OpenMaya.MSpace.getPoints`
        """
    
        pass
    
    
    def getUV(self, vertex, uvSet=None):
        """
        Return the texture coordinate for the given vertex.
        
        :Parameters:
            vertex : `int`
                The face-relative vertex index to get UV for 
            uvSet : `unicode`
                UV set to work with
        
        
        :rtype: (`float`, `float`)
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getUV`
        """
    
        pass
    
    
    def getUVArea(self, uvSet=None):
        """
        This method gets the UV area of the face
        
        :Parameters:
            uvSet : `unicode`
                UV set to work with
        
        
        :rtype: `float`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getUVArea`
        """
    
        pass
    
    
    def getUVAtPoint(self, pt, space='preTransform', uvSet=None):
        """
        Find the point closest to the given point in the current polygon, and return the UV value at that point.
        
        :Parameters:
            pt : `Point`
                The point to try to get UV for 
            space : `Space.Space`
                The coordinate system for this operation 
        
                values: 'transform', 'preTransform', 'object', 'world'
            uvSet : `unicode`
                UV set to work with
        
        
        :rtype: (`float`, `float`)
        
        Derived from api method `maya.OpenMaya.MSpace.getUVAtPoint`
        """
    
        pass
    
    
    def getUVIndex(self, vertex, uvSet=None):
        """
        Returns the index of the texture coordinate for the given vertex. This index refers to an element of the texture coordinate array for the polygonal object returned by  MFnMesh::getUVs .
        
        :Parameters:
            vertex : `int`
                The face-relative vertex index of the current polygon 
            uvSet : `unicode`
                UV set to work with
        
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getUVIndex`
        """
    
        pass
    
    
    def getUVSetNames(self):
        """
        This method is used to find the UV set names mapped to the current face.
        
        :rtype: `list` list
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getUVSetNames`
        """
    
        pass
    
    
    def getUVs(self, uvSet=None):
        """
        Return the all the texture coordinates for the vertices of this face (in local vertex order).
        
        :Parameters:
            uvSet : `unicode`
                UV set to work with
        
        
        :rtype: (`float` list, `float` list)
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getUVs`
        """
    
        pass
    
    
    def getVertices(self):
        """
        This method gets the indices of the vertices of the current face
        
        :rtype: `int` list
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.getVertices`
        """
    
        pass
    
    
    def hasColor(self):
        """
        This method determines whether the current face has color-per-vertex set for any vertex.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.hasColor`
        """
    
        pass
    
    
    def hasUVs(self):
        """
        Tests whether this face has UV's mapped or not (either all the vertices for a face should have UV's, or none of them do, so the UV count for a face is either 0, or equal to the number of vertices).
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.hasUVs`
        """
    
        pass
    
    
    def hasValidTriangulation(self):
        """
        This method checks if the face has a valid triangulation. If it doesn't, then the face was bad geometry: it may gave degenerate points or cross over itself.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.hasValidTriangulation`
        """
    
        pass
    
    
    def isConnectedTo(self, component):
        """
        :rtype: bool
        """
    
        pass
    
    
    def isConnectedToEdge(self, index):
        """
        This method determines whether the given edge is connected to a vertex in the current face
        
        :Parameters:
            index : `int`
                Index of the edge to be tested for 
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.isConnectedToEdge`
        """
    
        pass
    
    
    def isConnectedToFace(self, index):
        """
        This method determines whether the given face is adjacent to the current face
        
        :Parameters:
            index : `int`
                Index of the face to be tested for 
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.isConnectedToFace`
        """
    
        pass
    
    
    def isConnectedToVertex(self, index):
        """
        This method determines whether the given vertex shares an edge with a vertex in the current face.
        
        :Parameters:
            index : `int`
                Index of the vertex to be tested for 
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.isConnectedToVertex`
        """
    
        pass
    
    
    def isConvex(self):
        """
        This method checks if the face is convex.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.isConvex`
        """
    
        pass
    
    
    def isHoled(self):
        """
        This method checks if the face has any holes.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.isHoled`
        """
    
        pass
    
    
    def isLamina(self):
        """
        This method checks if the face is a lamina (the face is folded over onto itself).
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.isLamina`
        """
    
        pass
    
    
    def isOnBoundary(self):
        """
        This method determines whether the current face is on a boundary
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.onBoundary`
        """
    
        pass
    
    
    def isPlanar(self):
        """
        This method checks if the face is planar
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.isPlanar`
        """
    
        pass
    
    
    def isStarlike(self):
        """
        This method checks if the face is starlike. That is, a line from the centre to any vertex lies entirely within the face.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.isStarlike`
        """
    
        pass
    
    
    def isZeroArea(self):
        """
        This method checks if its a zero area face
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.zeroArea`
        """
    
        pass
    
    
    def isZeroUVArea(self):
        """
        This method checks if the UV area of the face is zero
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.zeroUVArea`
        """
    
        pass
    
    
    def normalIndex(self, localVertexIndex):
        """
        Returns the normal index for the specified vertex. This index refers to an element in the normal array returned by  MFnMesh::getNormals . These normals are per-polygon per-vertex normals. See the  MFnMesh  description for more information on normals.
        
        :Parameters:
            localVertexIndex : `int`
                The face-relative index of the vertex to examine for the current polygon 
        
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.normalIndex`
        """
    
        pass
    
    
    def numColors(self, colorSetName=None):
        """
        This method checks for the number of colors on vertices in this face.
        
        :Parameters:
            colorSetName : `unicode`
                Name of the color set.
        
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.numColors`
        """
    
        pass
    
    
    def numConnectedEdges(self):
        """
        This method checks for the number of connected edges on the vertices of this face
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.numConnectedEdges`
        """
    
        pass
    
    
    def numConnectedFaces(self):
        """
        This method checks for the number of connected faces
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.numConnectedFaces`
        """
    
        pass
    
    
    def numTriangles(self):
        """
        This Method checks for the number of triangles in this face in the current triangulation
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.numTriangles`
        """
    
        pass
    
    
    def numVertices(self):
        """
        Return the number of vertices for the current polygon.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.polygonVertexCount`
        """
    
        pass
    
    
    def polygonVertexCount(self):
        """
        Return the number of vertices for the current polygon.
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.polygonVertexCount`
        """
    
        pass
    
    
    def setPoint(self, point, index, space='preTransform'):
        """
        Set the vertex at the given index in the current polygon.
        
        :Parameters:
            point : `Point`
                The new position for the vertex 
            index : `int`
                The face-relative index of the vertex in the current polygon 
            space : `Space.Space`
                The coordinate system for this operation
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.setPoint`
        """
    
        pass
    
    
    def setPoints(self, pointArray, space='preTransform'):
        """
        Sets new locations for vertices of the current polygon that the iterator is pointing to.
        
        :Parameters:
            pointArray : `Point` list
                The new positions for the vertices. 
            space : `Space.Space`
                The coordinate system for this operation.
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.setPoints`
        """
    
        pass
    
    
    def setUV(self, vertexId, uvPoint, uvSet=None):
        """
        Modify the UV value for the given vertex in the current face. If the face is not already mapped, this method will fail.
        
        :Parameters:
            vertexId : `int`
                face-relative index of the vertex to set UV for. 
            uvPoint : (`float`, `float`)
                The UV values to set it to 
            uvSet : `unicode`
                UV set to work with
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.setUV`
        """
    
        pass
    
    
    def setUVs(self, uArray, vArray, uvSet=None):
        """
        Modify the UV value for all vertices in the current face. If the face has not already been mapped, this method will fail.
        
        :Parameters:
            uArray : `float` list
                All the U values - in local face order 
            vArray : `float` list
                The corresponding V values 
            uvSet : `unicode`
                UV set to work with
        
        Derived from api method `maya.OpenMaya.MItMeshPolygon.setUVs`
        """
    
        pass
    
    
    def updateSurface(self):
        """
        Signal that this polygonal surface has changed and needs to redraw itself.
        Derived from api method `maya.OpenMaya.MItMeshPolygon.updateSurface`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    __apicls__ = None
    
    
    __readonly__ = {}


class MeshVertex(MItComponent1D):
    def connectedEdges(self):
        """
        :rtype: `MeshEdge` list
        """
    
        pass
    
    
    def connectedFaces(self):
        """
        :rtype: `MeshFace` list
        """
    
        pass
    
    
    def connectedVertices(self):
        """
        :rtype: `MeshVertex` list
        """
    
        pass
    
    
    def geomChanged(self):
        """
        Reset the geom pointer in the  MItMeshVertex . If you're using  MFnMesh  to update Normals or Color per vertex while iterating, you must call geomChanged on the iteratior immediately after the  MFnMesh  call to make sure that your geometry is up to date. A crash may result if this method is not called. A similar approach must be taken for updating upstream vertex tweaks with an  MPlug . After the update, call this method.
        Derived from api method `maya.OpenMaya.MItMeshVertex.geomChanged`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def getColor(self, *args, **kwargs):
        pass
    
    
    def getColorIndices(self, colorSetName=None):
        """
        This method returns the colorIndices into the color array see  MFnMesh::getColors()  of the current vertex.
        
        :Parameters:
            colorSetName : `unicode`
                Name of the color set.
        
        
        :rtype: `int` list
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.getColorIndices`
        """
    
        pass
    
    
    def getColors(self, colorSetName=None):
        """
        This method gets the colors of the current vertex for each face it belongs to. If no colors are assigned to the vertex at all, the return values will be (-1 -1 -1 1). If some but not all of the vertex/face colors have been explicitly set, the ones that have not been set will be (0, 0, 0, 1).
        
        :Parameters:
            colorSetName : `unicode`
                Name of the color set.
        
        
        :rtype: `Color` list
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.getColors`
        """
    
        pass
    
    
    def getNormal(self, space='preTransform'):
        """
        Return the normal or averaged normal if unshared of the current vertex.
        
        :Parameters:
            space : `Space.Space`
                The transformation space.
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Vector`
        
        Derived from api method `maya.OpenMaya.MSpace.getNormal`
        """
    
        pass
    
    
    def getNormalIndices(self):
        """
        This method returns the normal indices of the face/vertex associated with the current vertex.
        
        :rtype: `int` list
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.getNormalIndices`
        """
    
        pass
    
    
    def getNormals(self, space='preTransform'):
        """
        Return the normals of the current vertex for all faces
        
        :Parameters:
            space : `Space.Space`
                The transformation space.
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Vector` list
        
        Derived from api method `maya.OpenMaya.MSpace.getNormals`
        """
    
        pass
    
    
    def getPosition(self, space='preTransform'):
        """
        Return the position of the current vertex in the specified space. Object space ignores all transformations for the polygon, world space includes all such transformations.
        
        :Parameters:
            space : `Space.Space`
                The transformation space 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Point`
        
        Derived from api method `maya.OpenMaya.MSpace.position`
        """
    
        pass
    
    
    def getUV(self, uvSet=None):
        """
        Get the shared UV value at this vertex
        
        :Parameters:
            uvSet : `unicode`
                Name of the uv set to work with.
        
        
        :rtype: (`float`, `float`)
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.getUV`
        """
    
        pass
    
    
    def getUVIndices(self, uvSet=None):
        """
        This method returns the uv indices into the normal array see  MFnMesh::getUVs()  of the current vertex.
        
        :Parameters:
            uvSet : `unicode`
                Name of the uv set.
        
        
        :rtype: `int` list
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.getUVIndices`
        """
    
        pass
    
    
    def getUVs(self, uvSet=None):
        """
        Get the UV values for all mapped faces at the current vertex. If at least one face was mapped the method will succeed.
        
        :Parameters:
            uvSet : `unicode`
                Name of the uv set to work with
        
        
        :rtype: (`float` list, `float` list, `int` list)
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.getUVs`
        """
    
        pass
    
    
    def hasColor(self):
        """
        This method determines whether the current Vertex has a color set for one or more faces.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.hasColor`
        """
    
        pass
    
    
    def isConnectedTo(self, component):
        """
        pass a component of type `MeshVertex`, `MeshEdge`, `MeshFace`, with a single element
        
        :rtype: bool
        """
    
        pass
    
    
    def isConnectedToEdge(self, index):
        """
        This method determines whether the given edge contains the current vertex
        
        :Parameters:
            index : `int`
                Index of edge to check. 
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.connectedToEdge`
        """
    
        pass
    
    
    def isConnectedToFace(self, index):
        """
        This method determines whether the given face contains the current vertex
        
        :Parameters:
            index : `int`
                Index of face to check. 
        
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.connectedToFace`
        """
    
        pass
    
    
    def isOnBoundary(self):
        """
        This method determines whether the current vertex is on a Boundary
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.onBoundary`
        """
    
        pass
    
    
    def numConnectedEdges(self):
        """
        This Method checks for the number of connected Edges on this vertex
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.numConnectedEdges`
        """
    
        pass
    
    
    def numConnectedFaces(self):
        """
        This Method checks for the number of Connected Faces
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.numConnectedFaces`
        """
    
        pass
    
    
    def numUVs(self, uvSet=None):
        """
        This method returns the number of unique UVs mapped on this vertex
        
        :Parameters:
            uvSet : `unicode`
                Name of the uv set to work with
        
        
        :rtype: `int`
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.numUVs`
        """
    
        pass
    
    
    def setColor(self, color):
        pass
    
    
    def setPosition(self, point, space='preTransform'):
        """
        Set the position of the current vertex in the given space.
        
        :Parameters:
            point : `Point`
                The new position for the current vertex 
            space : `Space.Space`
                Transformation space
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.setPosition`
        """
    
        pass
    
    
    def setUV(self, uvPoint, uvSet=None):
        """
        Set the shared UV value at this vertex
        
        :Parameters:
            uvPoint : (`float`, `float`)
                The UV value to set. 
            uvSet : `unicode`
                Name of the UV set to work with
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.setUV`
        """
    
        pass
    
    
    def setUVs(self, uArray, vArray, faceIds, uvSet=None):
        """
        Set the UV value for the specified faces at the current vertex. If the face is not already mapped, the value will not be set. If at least ne face was previously mapped, the method should succeed. If no faces were mapped, the method will fail.
        
        :Parameters:
            uArray : `float` list
                All the U values - in local face order 
            vArray : `float` list
                The corresponding V values 
            faceIds : `int` list
                The corresponding face Ids 
            uvSet : `unicode`
                Name of the uv set to work with
        
        Derived from api method `maya.OpenMaya.MItMeshVertex.setUVs`
        """
    
        pass
    
    
    def translateBy(self, vector, space='preTransform'):
        """
        Translate the current vertex by the amount specified by the given vector.
        
        :Parameters:
            vector : `Vector`
                The amount of translation 
            space : `Space.Space`
                The transformation space
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.translateBy`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def updateSurface(self):
        """
        Signal that this polygonal surface has changed and needs to redraw itself.
        Derived from api method `maya.OpenMaya.MItMeshVertex.updateSurface`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    __apicls__ = None
    
    
    __readonly__ = {}


class NurbsSurfaceRange(NurbsSurfaceIsoparm):
    def __getitem__(self, item):
        pass
    
    
    __readonly__ = {}


class NurbsCurveCV(MItComponent1D):
    def getPosition(self, space='preTransform'):
        """
        Return the position of the current CV.
        
        :Parameters:
            space : `Space.Space`
                the co-oordinate system for the returned point 
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        
        :rtype: `Point`
        
        Derived from api method `maya.OpenMaya.MSpace.position`
        """
    
        pass
    
    
    def hasHistoryOnCreate(self):
        """
        This method determines if the shape was created with history.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItCurveCV.hasHistoryOnCreate`
        """
    
        pass
    
    
    def isDone(self):
        """
        Returns  true  if the iteration is finished, i.e. there are no more CVs to iterate on.
        
        :rtype: `bool`
        
        Derived from api method `maya.OpenMaya.MItCurveCV.isDone`
        """
    
        pass
    
    
    def setPosition(self, pt, space='preTransform'):
        """
        Set the position of the current CV to the specified point.
        
        :Parameters:
            pt : `Point`
                new position of CV 
            space : `Space.Space`
                the co-ordinate system for this transformation.
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.setPosition`
        """
    
        pass
    
    
    def translateBy(self, vec, space='preTransform'):
        """
        Translates the current CV by the amount specified in  vec .
        
        :Parameters:
            vec : `Vector`
                translation to be applied to the CV 
            space : `Space.Space`
                the co-oordinate system for this transformation.
        
                values: 'transform', 'preTransform', 'object', 'world'
        
        Derived from api method `maya.OpenMaya.MSpace.translateBy`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    def updateCurve(self):
        """
        This method is used to signal the curve that it has been changed and needs to redraw itself.
        Derived from api method `maya.OpenMaya.MItCurveCV.updateCurve`
        
        **Undo is not currently supported for this method**
        """
    
        pass
    
    
    __apicls__ = None
    
    
    __readonly__ = {}



def attributeInfo(*args, **kwargs):
    """
    This command lists all of the attributes that are marked with certain flags.  Combinations of flags may be specified and
    all will be considered. (The method of combination depends on the state of the logicalAnd/andflag.) When the
    allAttributes/allflag is specified, attributes of all types will be listed.
    
    Flags:
      - allAttributes : all            (bool)          [create]
          Show all attributes associated with the node regardless of type. Use of this flag overrides any other attribute type
          flags and logical operation that may be specified on the command.
    
      - bool : b                       (bool)          [create]
          Show the attributes that are of type boolean. Use the 'on' state to get only boolean attributes; the 'off' state to
          ignore boolean attributes.
    
      - enumerated : e                 (bool)          [create]
          Show the attributes that are of type enumerated. Use the 'on' state to get only enumerated attributes; the 'off' state
          to ignore enumerated attributes.
    
      - hidden : h                     (bool)          [create]
          Show the attributes that are marked as hidden. Use the 'on' state to get hidden attributes; the 'off' state to get non-
          hidden attributes.
    
      - inherited : inherited          (bool)          [create]
          Filter the attributes based on whether they belong to the node type directly or have been inherited from a root type
          (e.g. meshShape/direct or dagObject/inherited). Use the 'on' state to get only inherited attributes, the 'off' state to
          get only directly owned attributes, and leave the flag unspecified to get both.
    
      - internal : i                   (bool)          [create]
          Show the attributes that are marked as internal to the node. Use the 'on' state to get internal attributes; the 'off'
          state to get non-internal attributes.
    
      - leaf : l                       (bool)          [create]
          Show the attributes that are complex leaves (ie. that have parent attributes and have no children themselves). Use the
          'on' state to get leaf attributes; the 'off' state to get non-leaf attributes.
    
      - logicalAnd : logicalAnd        (bool)          [create]
          The default is to take the logical 'or' of the above conditions. Specifying this flag switches to the logical 'and'
          instead.
    
      - multi : m                      (bool)          [create]
          Show the attributes that are multis. Use the 'on' state to get multi attributes; the 'off' state to get non-multi
          attributes.
    
      - short : s                      (bool)          [create]
          Show the short attribute names instead of the long names.
    
      - type : t                       (unicode)       [create]
          static node type from which to get 'affects' information                                   Flag can have multiple
          arguments, passed either as a tuple or a list.
    
      - userInterface : ui             (bool)          [create]
          Show the UI-friendly attribute names instead of the Maya ASCII names. Takes precedence over the -s/-short flag if both
          are specified.
    
      - writable : w                   (bool)          [create]
          Show the attributes that are writable (ie. can have input connections). Use the 'on' state to get writable attributes;
          the 'off' state to get non-writable attributes.
    
    
    Derived from mel command `maya.cmds.attributeInfo`
    """

    pass


def makePaintable(*args, **kwargs):
    """
    Make attributes of nodes paintable to Attribute Paint Tool. This command is used to register new attributes to the
    Attribute Paint tool as paintable. Once registered the attributes will be recognized by the Attribute Paint tool and the
    user will be able to paint them.             In query mode, return type is based on queried flag.
    
    Flags:
      - activate : ac                  (bool)          [create,query]
          Activate / deactivate the given paintable attribute. Used to filter out some nodes in the attribute paint tool.
    
      - activateAll : aca              (bool)          [create,query]
          Activate / deactivate all the registered paintable attributes. Used to filter out some nodes in the attribute paint
          tool.
    
      - altAttribute : aa              (unicode)       [create,query]
          Define an alternate attribute which will also receive the same values. There can be multiple such flags.
    
      - attrType : at                  (unicode)       [create,query]
          Paintable attribute type.    Supported types: intArray, doubleArray, vectorArray, multiInteger, multiFloat, multiDouble,
          multiVector.
    
      - clearAll : ca                  (bool)          [create,query]
          Removes all paintable attribute definitions.
    
      - remove : rm                    (bool)          [create,query]
          Make the attribute not paintable any more.
    
      - shapeMode : sm                 (unicode)       [create,query]
          This flag controls how Artisan correlates the paintable node to a corresponding shape node.  It is used for attributes
          of type multi of multi, where the first multi dimension corresponds to the shape index (i.e. cluster nodes). At present,
          only one value of this flag is supported: deformer. By default this flag is an empty string, which means that there is a
          direct indexing (no special mapping required) of the attribute with respect to vertices on the shape.
    
      - uiName : ui                    (unicode)       [create,query]
          UI name. Default is the attribute name.                                    Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.makePaintable`
    """

    pass


def isolateSelect(*args, **kwargs):
    """
    This command turns on/off isolate select mode in a specified modeling view, specified as the argument. Isolate select
    mode is a display mode where the currently selected objects are added to a list and only those objects are displayed in
    the view. It allows for selective viewing of specific objects and object components.
    
    Flags:
      - addDagObject : ado             (PyNode)        []
          Add the specified object to the set of objects to be displayed in the view.
    
      - addSelected : addSelected      (bool)          []
          Add the currently active objects to the set of objects to be displayed in the view.
    
      - addSelectedObjects : aso       (bool)          []
          Add selected objects to the set of objects to be displayed in the view. This flag differs from addSelected in that it
          will ignore selected components and add the entire object.
    
      - loadSelected : ls              (bool)          []
          Replace the objects being displayed with the currently active objects.
    
      - removeDagObject : rdo          (PyNode)        []
          Remove the specified object from the set of objects to be displayed in the view.
    
      - removeSelected : rs            (bool)          []
          Remove the currently active objects to the set of objects to be displayed in the view.
    
      - state : s                      (bool)          [query]
          Turns isolate select mode on/off.
    
      - update : u                     (bool)          []
          Update the view's list of objects due to a change to the set of objects to be displayed.
    
      - viewObjects : vo               (bool)          [query]
          Returns the name (if any) of the objectSet which contains the list of objects visible in the view if isolate select mode
          is on. If isolate select mode is off, an empty string is returned.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.isolateSelect`
    """

    pass


def createNode(*args, **kwargs):
    """
    This command creates a new node in the dependency graph of the specified type.
    
    Flags:
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created node. If it contains namespace path, the new node will be created under the specified
          namespace; if the namespace doesn't exist, we will create the namespace.
    
      - parent : p                     (unicode)       [create]
          Specifies the parent in the DAG under which the new node belongs.
    
      - shared : s                     (bool)          [create]
          This node is shared across multiple files, so only create it if it does not already exist.
    
      - skipSelect : ss                (bool)          [create]
          This node is not to be selected after creation, the original selection will be preserved.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.createNode`
    """

    pass


def vnnCopy(*args, **kwargs):
    """
    Copy a set of VNN nodes to clipper board. The first parameter is the full name of the DG node that contains the VNN
    graph. The second parameter is the full path of the parent VNN compound. The source VNN nodes must be set by the flag
    -sourceNode.
    
    Flags:
      - sourceNode : src               (unicode)       [create]
          Set the source node to copy. This node should be a child of the specified parent compound. This command should be used
          with vnnPastecommand.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.vnnCopy`
    """

    pass


def listTransforms(*args, **kwargs):
    """
    Modifications:
      - returns wrapped classes
    
        :rtype: `Transform` list
    """

    pass


def addAttr(*args, **kwargs):
    """
    This command is used to add a dynamic attribute to a node or nodes. Either the longName or the shortName or both must be
    specified. If neither a dataType nor an attributeType is specified, a double attribute will be added.  The dataType flag
    can be specified more than once indicating that any of the supplied types will be accepted (logical-or).  To add a non-
    double attribute the following criteria can be used to determine whether the dataType or the attributeType flag is
    appropriate.  Some types, such as double3can use either. In these cases the -dtflag should be used when you only wish to
    access the data as an atomic entity (eg. you never want to access the three individual values that make up a double3).
    In general it is best to use the -atin these cases for maximum flexibility. In most cases the -dtversion will not
    display in the attribute editor as it is an atomic type and you are not allowed to change individual parts of it.  All
    attributes flagged as (compound)below or the compound attribute itself are not actually added to the node until all of
    the children are defined (using the -pflag to set their parent to the compound being created).  See the EXAMPLES section
    for more details.  Type of attribute              Flag and argument to use      boolean
    -at bool                      32 bit integer                                 -at long                      16 bit
    integer                                 -at short                     8 bit integer                                  -at
    byte                      char                                                   -at char                      enum
    -at enum (specify the enum names using the enumName flag) float                                                  -at
    float(use quotes                                                                         since float is a mel keyword)
    double                                                 -at double            angle value
    -at doubleAngle       linear value                                   -at doubleLinear      string
    -dt string(use quotes                                                                         since string is a mel
    keyword)  array of strings                               -dt stringArray       compound
    -at compound          message (no data)                              -at message           time
    -at time                      4x4 double matrix                              -dt matrix(use quotes
    since matrix is a mel keyword)  4x4 float matrix                               -at fltMatrix         reflectance
    -dt reflectanceRGBreflectance (compound)                 -at reflectance       spectrum
    -dt spectrumRGB       spectrum (compound)                    -at spectrum          2 floats
    -dt float2            2 floats (compound)                    -at float2            3 floats
    -dt float3            3 floats (compound)                    -at float3            2 doubles
    -dt double2           2 doubles (compound)                   -at double2           3 doubles
    -dt double3           3 doubles (compound)                   -at double3           2 32-bit integers
    -dt long2                     2 32-bit integers (compound)   -at long2                     3 32-bit integers
    -dt long3                     3 32-bit integers (compound)   -at long3                     2 16-bit integers
    -dt short2            2 16-bit integers (compound)   -at short2            3 16-bit integers
    -dt short3            3 16-bit integers (compound)   -at short3            array of doubles
    -dt doubleArray       array of floats                                -dt floatArray        array of 32-bit ints
    -dt Int32Array        array of vectors                               -dt vectorArray       nurbs curve
    -dt nurbsCurve        nurbs surface                                  -dt nurbsSurface      polygonal mesh
    -dt mesh                      lattice                                                -dt lattice           array of
    double 4D points              -dt pointArray        In query mode, return type is based on queried flag.
    
    Modifications:
      - allow python types to be passed to set -at type
                str         string
                float       double
                int         long
                bool        bool
                Vector      double3
      - when querying dataType, the dataType is no longer returned as a list
      - when editing hasMinValue, hasMaxValue, hasSoftMinValue, or hasSoftMaxValue the passed boolean value was ignored
        and the command instead behaved as a toggle.  The behavior is now more intuitive::
    
            >>> addAttr('persp', ln='test', at='double', k=1)
            >>> addAttr('persp.test', query=1, hasMaxValue=True)
            False
            >>> addAttr('persp.test', edit=1, hasMaxValue=False)
            >>> addAttr('persp.test', query=1, hasMaxValue=True)
            False
            >>> addAttr('persp.test', edit=1, hasMaxValue=True)
            >>> addAttr('persp.test', query=1, hasMaxValue=True)
            True
    
      - allow passing a list or dict instead of a string for enumName
      - allow user to pass in type and determine whether it is a dataType or
        attributeType. Types that may be both, such as float2, float3, double2,
        double3, long2, long3, short2, and short3 are all treated as
        attributeTypes. In addition, as a convenience, since these attributeTypes
        are actually treated as compound attributes, the child attributes are
        automatically created, with X/Y/Z appended, unless usedAsColor is set, in
        which case R/G/B is added. Alternatively, the suffices can explicitly
        specified with childSuffixes:
    
            >>> addAttr('persp', ln='autoDouble', type='double', k=1)
            >>> addAttr('persp.autoDouble', query=1, attributeType=1)
            u'double'
            >>> addAttr('persp.autoDouble', query=1, dataType=1)
            u'TdataNumeric'
            >>> addAttr('persp', ln='autoMesh', type='mesh', k=1)
            >>> addAttr('persp.autoMesh', query=1, attributeType=1)
            u'typed'
            >>> addAttr('persp.autoMesh', query=1, dataType=1)
            u'mesh'
            >>> addAttr('persp', ln='autoDouble3Vec', type='double3', k=1)
            >>> [x.attrName() for x in PyNode('persp').listAttr() if 'autoDouble3' in x.name()]
            [u'autoDouble3Vec', u'autoDouble3VecX', u'autoDouble3VecY', u'autoDouble3VecZ']
            >>> addAttr('persp', ln='autoFloat3Col', type='float3', usedAsColor=1)
            >>> [x.attrName() for x in PyNode('persp').listAttr() if 'autoFloat3' in x.name()]
            [u'autoFloat3Col', u'autoFloat3ColR', u'autoFloat3ColG', u'autoFloat3ColB']
            >>> addAttr('persp', ln='autoLong2', type='long2', childSuffixes=['_first', '_second'])
            >>> [x.attrName() for x in PyNode('persp').listAttr() if 'autoLong2' in x.name()]
            [u'autoLong2', u'autoLong2_first', u'autoLong2_second']
    
    Flags:
      - attributeType : at             (unicode)       [create,query]
          Specifies the attribute type, see above table for more details. Note that the attribute types float, matrixand stringare
          also MEL keywords and must be enclosed in quotes.
    
      - binaryTag : bt                 (unicode)       [create,query]
          This flag is obsolete and does not do anything any more
    
      - cachedInternally : ci          (bool)          [create,query]
          Whether or not attribute data is cached internally in the node. This flag defaults to true for writable attributes and
          false for non-writable attributes. A warning will be issued if users attempt to force a writable attribute to be
          uncached as this will make it impossible to set keyframes.
    
      - category : ct                  (unicode)       [create,query,edit]
          An attribute category is a string associated with the attribute to identify it. (e.g. the name of a plugin that created
          the attribute, version information, etc.) Any attribute can be associated with an arbitrary number of categories however
          categories can not be removed once associated.
    
      - dataType : dt                  (unicode)       [create,query]
          Specifies the data type.  See setAttrfor more information on data type names.
    
      - defaultValue : dv              (float)         [create,query,edit]
          Specifies the default value for the attribute (can only be used for numeric attributes).
    
      - disconnectBehaviour : dcb      (int)           [create,query]
          defines the Disconnect Behaviour 2 Nothing, 1 Reset, 0 Delete
    
      - enumName : en                  (unicode)       [create,query,edit]
          Flag used to specify the ui names corresponding to the enum values. The specified string should contain a colon-
          separated list of the names, with optional values. If values are not specified, they will treated as sequential integers
          starting with 0. For example: -enumName A:B:Cwould produce options: A,B,C with values of 0,1,2; -enumName
          zero:one:two:thousand=1000would produce four options with values 0,1,2,1000; and -enumName
          solo=1:triplet=3:quintet=5would produce three options with values 1,3,5.  (Note that there is a current limitation of
          the Channel Box that will sometimes incorrectly display an enumerated attribute's pull-down menu.  Extra menu items can
          appear that represent the numbers inbetween non-sequential option values.  To avoid this limitation, specify sequential
          values for the options of any enumerated attributes that will appear in the Channel Box.  For example:
          solo=1:triplet=2:quintet=3.)
    
      - exists : ex                    (bool)          [create,query]
          Returns true if the attribute queried is a user-added, dynamic attribute; false if not.
    
      - fromPlugin : fp                (bool)          [create,query]
          Was the attribute originally created by a plugin? Normally set automatically when the API call is made - only added here
          to support storing it in a file independently from the creating plugin.
    
      - hasMaxValue : hxv              (bool)          [create,query,edit]
          Flag indicating whether an attribute has a maximum value. (can only be used for numeric attributes).
    
      - hasMinValue : hnv              (bool)          [create,query,edit]
          Flag indicating whether an attribute has a minimum value. (can only be used for numeric attributes).
    
      - hasSoftMaxValue : hsx          (bool)          [create,query]
          Flag indicating whether a numeric attribute has a soft maximum.
    
      - hasSoftMinValue : hsn          (bool)          [create,query]
          Flag indicating whether a numeric attribute has a soft minimum.
    
      - hidden : h                     (bool)          [create,query]
          Will this attribute be hidden from the UI?
    
      - indexMatters : im              (bool)          [create,query]
          Sets whether an index must be used when connecting to this multi-attribute. Setting indexMatters to false forces the
          attribute to non-readable.
    
      - internalSet : internalSet      (bool)          [create,query]
          Whether or not the internal cached value is set when this attribute value is changed.  This is an internal flag used for
          updating UI elements.
    
      - keyable : k                    (bool)          [create,query]
          Is the attribute keyable by default?
    
      - longName : ln                  (unicode)       [create,query]
          Sets the long name of the attribute.
    
      - maxValue : max                 (float)         [create,query,edit]
          Specifies the maximum value for the attribute (can only be used for numeric attributes).
    
      - minValue : min                 (float)         [create,query,edit]
          Specifies the minimum value for the attribute (can only be used for numeric attributes).
    
      - multi : m                      (bool)          [create,query]
          Makes the new attribute a multi-attribute.
    
      - niceName : nn                  (unicode)       [create,query,edit]
          Sets the nice name of the attribute for display in the UI.  Setting the attribute's nice name to a non-empty string
          overrides the default behaviour of looking up the nice name from Maya's string catalog.   (Use the MEL commands
          attributeNiceNameand attributeQuery -niceNameto lookup an attribute's nice name in the catalog.)
    
      - numberOfChildren : nc          (int)           [create,query]
          How many children will the new attribute have?
    
      - parent : p                     (unicode)       [create,query]
          Attribute that is to be the new attribute's parent.
    
      - proxy : pxy                    (unicode)       [create,query]
          Proxy another node's attribute. Proxied plug will be connected as source. The UsedAsProxy flag is automatically set in
          this case.
    
      - readable : r                   (bool)          [create,query]
          Can outgoing connections be made from this attribute?
    
      - shortName : sn                 (unicode)       [create,query]
          Sets the short name of the attribute.
    
      - softMaxValue : smx             (float)         [create,query,edit]
          Soft maximum, valid for numeric attributes only.  Specifies the upper default limit used in sliders for this attribute.
    
      - softMinValue : smn             (float)         [create,query,edit]
          Soft minimum, valid for numeric attributes only.  Specifies the upper default limit used in sliders for this attribute.
    
      - storable : s                   (bool)          [create,query]
          Can the attribute be stored out to a file?
    
      - usedAsColor : uac              (bool)          [create,query]
          Is the attribute to be used as a color definition? Must have 3 DOUBLE or 3 FLOAT children to use this flag.  The
          attribute type -atshould be double3or float3as appropriate.  It can also be used to less effect with data types -dtas
          double3or float3as well but some parts of the code do not support this alternative.  The special attribute types/data
          spectrumand reflectancealso support the color flag and on them it is set by default.
    
      - usedAsFilename : uaf           (bool)          [create,query]
          Is the attribute to be treated as a filename definition? This flag is only supported on attributes with data type -dtof
          string.
    
      - usedAsProxy : uap              (bool)          [create,query]
          Set if the specified attribute should be treated as a proxy to another attributes.
    
      - writable : w                   (bool)          [create,query]
          Can incoming connections be made to this attribute?                                Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.addAttr`
    """

    pass


def condition(*args, **kwargs):
    """
    This command creates a new named condition object whose true/false value is calculated by running a mel script. This new
    condition can then be used for dimming, or controlling other scripts, or whatever. In query mode, return type is based
    on queried flag.
    
    Flags:
      - delete : delete                (bool)          [create]
          Deletes the condition.
    
      - dependency : d                 (unicode)       [create]
          Each -dependency flag specifies another condition that the new condition will be dependent on.  When any of these
          conditions change, the new-state-script will run, and the state of this condition will be set accordingly.  It is
          possible to define infinite loops, but they will be caught and handled correctly at run-time.
    
      - initialize : i                 (bool)          [create]
          Initializes the condition, by forcing it to run its script as soon as it is created.  If this flag is not specified, the
          script will not run until one of the dependencies is triggered.
    
      - script : s                     (unicode)       [create]
          The script that determines the new state of the condition.
    
      - state : st                     (bool)          [create,query,edit]
          Sets the state of the condition. This can be used to create a manually triggered condition: you could create a condition
          without any dependencies and without a new-state-script. This condition would only change state in response to the
          -st/state flag.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.condition`
    """

    pass


def transformLimits(*args, **kwargs):
    """
    The transformLimits command allows us to set, edit, or query the limits of the transformation that can be applied to
    objects. We can also turn any limits off which may have been previously set. When an object is first created, all the
    transformation limits are off by default.Transformation limits allow us to control how much an object can be
    transformed. This is most useful for joints, although it can be used any place we would like to limit the movement of an
    object.Default values are:( -1, 1) for translation, ( -1, 1) for scaling, and (-45,45) for rotation. In query mode,
    return type is based on queried flag.
    
    Flags:
      - enableRotationX : erx          (bool, bool)    [query]
          enable/disable the lower and upper x-rotation limitsWhen queried, it returns boolean boolean
    
      - enableRotationY : ery          (bool, bool)    [query]
          enable/disable the lower and upper y-rotation limitsWhen queried, it returns boolean boolean
    
      - enableRotationZ : erz          (bool, bool)    [query]
          enable/disable the lower and upper z-rotation limitsWhen queried, it returns boolean boolean
    
      - enableScaleX : esx             (bool, bool)    [query]
          enable/disable the lower and upper x-scale limitsWhen queried, it returns boolean boolean
    
      - enableScaleY : esy             (bool, bool)    [query]
          enable/disable the lower and upper y-scale limitsWhen queried, it returns boolean boolean
    
      - enableScaleZ : esz             (bool, bool)    [query]
          enable/disable the lower and upper z-scale limitsWhen queried, it returns boolean boolean
    
      - enableTranslationX : etx       (bool, bool)    [query]
          enable/disable the  ower and upper x-translation limitsWhen queried, it returns boolean boolean
    
      - enableTranslationY : ety       (bool, bool)    [query]
          enable/disable the lower and upper y-translation limitsWhen queried, it returns boolean boolean
    
      - enableTranslationZ : etz       (bool, bool)    [query]
          enable/disable the lower and upper z-translation limitsWhen queried, it returns boolean boolean
    
      - remove : rm                    (bool)          [create]
          turn all the limits off and reset them to their default values
    
      - rotationX : rx                 (float, float)  [query]
          set the lower and upper x-rotation limitsWhen queried, it returns angle angle
    
      - rotationY : ry                 (float, float)  [query]
          set the lower and upper y-rotation limitsWhen queried, it returns angle angle
    
      - rotationZ : rz                 (float, float)  [query]
          set the lower and upper z-rotation limitsWhen queried, it returns angle angle
    
      - scaleX : sx                    (float, float)  [query]
          set the lower and upper x-scale limitsWhen queried, it returns float float
    
      - scaleY : sy                    (float, float)  [query]
          set the lower and upper y-scale limitsWhen queried, it returns float float
    
      - scaleZ : sz                    (float, float)  [query]
          set the lower and upper z-scale limitsWhen queried, it returns float float
    
      - translationX : tx              (float, float)  [query]
          set the lower and upper x-translation limitsWhen queried, it returns linear linear
    
      - translationY : ty              (float, float)  [query]
          set the lower and upper y-translation limitsWhen queried, it returns linear linear
    
      - translationZ : tz              (float, float)  [query]
          set the lower and upper z-translation limitsWhen queried, it returns linear linearFlag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.transformLimits`
    """

    pass


def stringArrayIntersector(*args, **kwargs):
    """
    The stringArrayIntersector command creates and edits an object which is able to efficiently intersect large string
    arrays. The intersector object maintains a sense of the intersection so far, and updates the intersection when new
    string arrays are provided using the -i/intersect flag. Note that the string intersector object may be deleted using the
    deleteUI command.
    
    Flags:
      - allowDuplicates : ad           (bool)          [create]
          Should the intersector allow duplicates in the input arrays (true), or combine all duplicate entries into a single,
          unique entry (false). This flag must be used when initially creating the intersector. Default is 'false'.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - intersect : i                  (<type 'unicode'>, ...) [create,edit]
          Intersect the specified string array with the current intersection being maintained by the intersector.
    
      - reset : r                      (bool)          [edit]
          Reset the intersector to begin a new intersection.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.stringArrayIntersector`
    """

    pass


def pause(*args, **kwargs):
    """
    Pause for a specified number of seconds for canned demos or for test scripts to allow user to view results.
    
    Flags:
      - seconds : sec                  (int)           [create]
          Pause for the specified number of seconds.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.pause`
    """

    pass


def upAxis(*args, **kwargs):
    """
    The upAxis command changes the world up direction. Current implementation provides only two choices of axis (the Y-axis
    or the Z-axis) as the world up direction.By default, the ground plane in Maya is on the XY plane. Hence, the default up-
    direction is the direction of the positive Z-axis.The -ax flag is mandatory. In conjunction with the -ax flag, when the
    -rv flag is specified, the camera of currently active view is revolved about the X-axis such that the position of the
    groundplane in the view will remain the same as before the the up direction is changed.The screen update is applied to
    all cameras of all views.In query mode, return type is based on queried flag.
    
    Flags:
      - axis : ax                      (unicode)       [query]
          This flag specifies the axis as the world up direction. The valid axis are either yor z.When queried, it returns a
          string.
    
      - rotateView : rv                (bool)          [create]
          This flag specifies to rotate the view as well.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.upAxis`
    """

    pass


def rename(obj, newname, **kwargs):
    """
    Renames the given object to have the new name. If only one argument is supplied the command will rename the (first)
    selected object. If the new name conflicts with an existing name, the object will be given a unique name based on the
    supplied name. It is not legal to rename an object to the empty string. When a transform is renamed then any shape nodes
    beneath the transform that have the same prefix as the old transform name are renamed. For example, rename nurbsSphere1
    ballwould rename nurbsSphere1|nurbsSphereShape1to ball|ballShape. If the new name ends in a single '#' then the rename
    command will replace the  trailing '#' with a number that ensures the new name is unique.
    
    Modifications:
        - if the full path to an object is passed as the new name, the shortname of the object will automatically be used
    
    Flags:
      - ignoreShape : ignoreShape      (bool)          [create]
          Indicates that renaming of shape nodes below transform nodes should be prevented.
    
      - uuid : uid                     (bool)          [create]
          Indicates that the new name is actually a UUID, and that the command should change the node's UUID. (In which case its
          name remains unchanged.)                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.rename`
    """

    pass


def symmetricModelling(*args, **kwargs):
    """
    This command allows you to change the symmetric modelling options. Symmetric modelling is an option that allows for
    reflection of basic manipulator actions such as move, rotate, and scale. In query mode, return type is based on queried
    flag.
    
    Flags:
      - about : a                      (unicode)       [create,query,edit]
          Set the space in which symmetry should be calculated (object or world or topo). When queried, returns a string which is
          the current space being used.
    
      - allowPartial : ap              (bool)          [create,query,edit]
          Specifies whether partial symmetry should be allowed when enabling topological symmetry.
    
      - axis : ax                      (unicode)       [create,query,edit]
          Set the current axis to be reflected over. When queried, returns a string which is the current axis.
    
      - preserveSeam : ps              (int)           [create,query,edit]
          Controls whether selection or symmetry should take priority on the plane of symmetry. When queried, returns an int for
          the option.
    
      - reset : r                      (bool)          [create,edit]
          Reset the redo information before starting.
    
      - seamFalloffCurve : sf          (unicode)       [create,query,edit]
          Set the seam's falloff curve, used to control the seam strength within the seam tolerance. The string is a comma
          separated list of sets of 3 values for each curve point. When queried, returns a string which is the current space being
          used.
    
      - seamTolerance : st             (float)         [create,query,edit]
          Set the seam tolerance used for reflection. When preserveSeam is enabled, this tolerance controls the width of the
          enforced seam. When queried, returns a float of the seamTolerance.
    
      - symmetry : s                   (int)           [create,query,edit]
          Set the symmetry option on or off. When queried, returns an int for the option.
    
      - tolerance : t                  (float)         [create,query,edit]
          Set the tolerance of reflection. When queried, returns a float of the tolerance.
    
      - topoSymmetry : ts              (bool)          [create,query,edit]
          Enable/disable topological symmetry. When enabled, the supplied component/active list will be used to define the
          topological symmetry seam. When queried, returns the name of the active topological symmetry object.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.symmetricModelling`
    """

    pass


def hilite(*args, **kwargs):
    """
    Hilites/Unhilites the specified object(s).  Hiliting an object makes it possible to select the components of the object.
    If no objects are specified then the selection list is used.
    
    Flags:
      - replace : r                    (bool)          [create]
          Hilite the specified objects.  Any objects previously hilited will no longer be hilited.
    
      - toggle : tgl                   (bool)          [create]
          Toggle the hilite state of the specified objects.
    
      - unHilite : u                   (bool)          [create]
          Remove the specified objects from the hilite list.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.hilite`
    """

    pass


def toolDropped(*args, **kwargs):
    """
    This command builds and executes the commands necessary to recreate the specified tool button.  It is invoked when a
    tool is dropped on the shelf.
    
    
    Derived from mel command `maya.cmds.toolDropped`
    """

    pass


def transformCompare(*args, **kwargs):
    """
    Compares two transforms passed as arguments. If they are the same, returns 0. If they are different, returns 1. If no
    transforms are specified in the command line, then the transforms from the active list are used.
    
    Flags:
      - root : r                       (bool)          [create]
          Compare the root only, rather than the entire hierarchy below the roots.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.transformCompare`
    """

    pass


def _toEnumStr(enums):
    pass


def threadCount(*args, **kwargs):
    """
    This command sets the number of threads to be used by Maya in regions of code that are multithreaded. By default the
    number of threads is equal to the number of logical CPUs, not the number of physical CPUs. Logical CPUs are different
    from physical CPUs in the following ways:A physical CPU with hyperthreading counts as two logical CPUsA dual-core CPU
    counts as two logical CPUsWith some workloads, using one thread per logical CPU may not perform well. This is sometimes
    the case with hyperthreading. It is worth experimenting with different numbers of threads to see which gives the best
    performance. Note that having more threads can mean Maya uses more memory. Setting a value of zero means the number of
    threads used will equal the number of logical processors in the system. In query mode, return type is based on queried
    flag.
    
    Flags:
      - numberOfThreads : n            (int)           [create,query]
          Sets the number of threads to use                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.threadCount`
    """

    pass


def selectionConnection(*args, **kwargs):
    """
    This command creates a named selectionConnection object. This object is simply a shared selection list. It may be used
    by editors to share their highlight data. For example, an outliner may attach its selected list to one of these objects,
    and a graph editor may use the same object as a list source. Then, the graph editor would only display objects that are
    selected in the outliner. Selection connections are UI objects which contain a list of model objects. Selection
    connections are useful for specifying which objects are to be displayed within a particular editor. Editor's have three
    plug socketswhere a selection connection may be attached. They are: mainListConnectionan inputsocket which contains a
    list of objects that are to be displayed within the editorselectionConnectionan outputsocket which contains a list of
    objects that are selectedwithin the editorhighlightConnectionan inputsocket which contains a list of objects that are to
    be highlightedwithin the editorThere are several different types of selection connections that may be created. They
    include: activeLista selection connection which contains a list of everything in the model which is active (which
    includes geometry objects and keys)modelLista selection connection which contains a list of all the geometry (i.e.
    excluding keys) objects that are currently activekeyframeLista selection connection which contains a list of all the
    keys that are currently activeworldLista selection connection which contains a list of all the objects in the
    worldobjectLista selection connection which contains one model object (which may be a set)listLista selection connection
    which contains a list of selection connectionseditorLista selection connection which contains a list of objects that are
    attached to the mainListConnection of the specified editorsetLista selection connection which contains a list of all the
    sets in the worldcharacterLista selection connection which contains a list of all the characters in the
    worldhighlightLista selection connection which contains a list of objects to be highlighted in some fashionBelow is an
    example selectionConnection network between two editors. Editor 1 is setup to display objects on the activeList. Editor
    2 is setup to display objects which are selected within Editor 1, and objects that are selected in Editor 2 are
    highlighted within Editor 1: -- Editor 1--       -- Editor 2-- inputList--| main |      |  |-| main |      | |      |
    sele |--|  |      | sele |--| |-| high |      |     | high |      |  | |   -------------       -------------   |
    |------------- fromEditor2 -------------| The following commands will establish this network: selectionConnection
    -activeList inputList; selectionConnection fromEditor1; selectionConnection fromEditor2; editor -edit
    -mainListConnection inputList Editor1; editor -edit -selectionConnection fromEditor1 Editor1; editor -edit
    -mainListConnection fromEditor1 Editor2; editor -edit -selectionConnection fromEditor2 Editor2; editor -edit
    -highlightConnection fromEditor2 Editor1; Note: to delete a selection connectionuse the deleteUI commandNote: commands
    which expect objects may be given a selection connection instead, and the command will operate upon the objects wrapped
    by the selection connectionNote: the graph editor and the dope sheet are the only editors which can use the editor
    connection to the highlightConnection of another editorWARNING: some flag combinations may not behave as you expect.
    The command is really intended for internal use for managing the outliner used by the various editors.
    
    Flags:
      - activeCacheList : atc          (bool)          [create]
          Specifies that this connection should reflect the cache that objects on the active list belong to.
    
      - activeCharacterList : acl      (bool)          [create]
          Specifies that this connection should reflect the characters that objects on the active list belong to.
    
      - activeList : act               (bool)          [create]
          Specifies that this connection should reflect the active list (geometry objects and keys).
    
      - addScript : addScript          (script)        [create,query,edit]
          Specify a script to be called when something is added to the selection.
    
      - addTo : add                    (unicode)       [create,edit]
          The name of a selection connection that should be added to this list of connections.
    
      - characterList : cl             (bool)          [create]
          Specifies that this connection should reflect all the characters in the world.
    
      - clear : clr                    (bool)          [create,edit]
          Remove everything from the selection connection.
    
      - connectionList : lst           (bool)          [create,query]
          Specifies that this connection should contain a list of selection connections.
    
      - defineTemplate : dt            (unicode)       [create]
          Puts the command in a mode where any other flags and args are parsed and added to the command template specified in the
          argument. They will be used as default arguments in any subsequent invocations of the command when templateName is set
          as the current template.
    
      - deselect : d                   (PyNode)        [create,edit]
          Remove something from the selection.
    
      - editor : ed                    (unicode)       [create,query,edit]
          Specifies that this connection should reflect the -mainListConnection of the specified editor.
    
      - exists : ex                    (bool)          [create]
          Returns whether the specified object exists or not. Other flags are ignored.
    
      - filter : f                     (unicode)       [create,query,edit]
          Optionally specifies an itemFilter for this connection. An empty string () clears the current filter. If a filter is
          specified, all the information going into the selectionConnection must first pass through the filter before being
          accepted.  NOTE: filters can only be attached to regular selectionConnections. They cannot be attached to any connection
          created using the -act, -mdl, -key, -wl, -sl, -cl, -lst, -obj, or -ren flags. We strongly recommend that you do not
          attach filters to a selectionConnection --- it is better to attach your filter to the editor that is using the
          selectionConnection instead.
    
      - findObject : fo                (PyNode)        [query]
          Find a selection connection in this list that wraps the specified object.
    
      - g : g                          (bool)          [create,query,edit]
          A global selection connection cannot be deleted by any script commands.
    
      - highlightList : hl             (bool)          [create]
          Specifies that this connection is being used as a highlight list.
    
      - identify : id                  (bool)          [query]
          Find out what type of selection connection this is.  May be: activeList | modelList | keyframeList | worldList |
          objectList listList | editorList | connection | unknown
    
      - keyframeList : key             (bool)          [create]
          Specifies that this connection should reflect the animation portion of the active list.
    
      - lock : lck                     (bool)          [create,query,edit]
          For activeList connections, locking the connection means that it will not listen to activeList changes.
    
      - modelList : mdl                (bool)          [create]
          Specifies that this connection should reflect the modeling (i.e. excluding keys) portion of the active list.
    
      - object : obj                   (PyNode)        [create,query,edit]
          Specifies that this connection should wrap around the specified object (which may be a set).  Query will return all the
          members of the selection connection (if the connection wraps a set, the set members will be returned)
    
      - parent : p                     (unicode)       [create,query,edit]
          The name of a UI object this should be attached to.  When the parent is destroyed, the selectionConnection will auto-
          delete. If no parent is specified, the connection is created in the current controlLayout.
    
      - remove : rm                    (unicode)       [create,edit]
          The name of a selection connection that should be removed from this list of connections.
    
      - removeScript : rs              (script)        [create,query,edit]
          Specify a script to be called when something is removed from the selection.
    
      - select : s                     (PyNode)        [create,edit]
          Add something to the selection. This does not replace the existing selection.
    
      - setList : sl                   (bool)          [create]
          Specifies that this connection should reflect all the sets in the world.
    
      - switch : sw                    (bool)          [create,query]
          Acts as a modifier to -connectionList which sets the list of objects to be the first non-empty selection connection.
          selection connections are tested in the order in which they are added.
    
      - useTemplate : ut               (unicode)       [create]
          Forces the command to use a command template other than the current one.
    
      - worldList : wl                 (bool)          [create]
          Specifies that this connection should reflect all objects in the world.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.selectionConnection`
    """

    pass


def toolHasOptions(*args, **kwargs):
    """
    This command queries a tool to see if it has options. If it does, it returns true. Otherwise it returns false.
    
    
    Derived from mel command `maya.cmds.toolHasOptions`
    """

    pass


def pickWalk(*args, **kwargs):
    """
    The pickWalk command allows you to quickly change the selection list relative to the nodes that are currently selected.
    It is called pickWalk, because it walks from one selection list to another by unselecting what's currently selected, and
    selecting nodes that are in the specified direction from the currently selected list. If you specify objects on the
    command line, the pickWalk command will walk from those objects instead of the selected list. If the -type flag is
    instances, then the left and right direction will walk to the previous or next instance of the same selected dag node.
    
    Flags:
      - direction : d                  (unicode)       [create]
          The direction to walk from the node. The choices are up | down | left | right | in | out. up walks to the parent node,
          down to the child node, and left and right to the sibling nodes. If a CV on a surface is selected, the left and right
          directions walk in the U parameter direction of the surface, and the up and down directions walk in the V parameter
          direction. In and out are only used if the type flag is 'latticepoints'. Default is right.
    
      - recurse : r                    (bool)          []
    
      - type : typ                     (unicode)       [create]
          The choices are nodes | instances | edgeloop | edgering | faceloop | keys | latticepoints | motiontrailpoints. If type
          is nodes, then the left and right direction walk to the next dag siblings. If type is instances, the left and right
          direction walk to the previous or next instance of the same dag node. If type is edgeloop, then the edge loop starting
          at the first selected edge will be selected. If type is edgering, then the edge ring starting at the first selected edge
          will be selected. If type is faceloop, and there are two connected quad faces selected which define a face loop, then
          that face loop will be selected.  edgeloop, edgering and faceloop all remember which was the first edge or faces
          selected for as long as consecutive selections are made by this command.  They use this information to determine what
          the nextloop or ring selection should be.  Users can make selections forwards and backwards by using the direction flag
          with leftor right.  If type is motiontrailpoints, then the left and right direction walk to the previous or next motion
          trail points respectively.  Default is nodes.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.pickWalk`
    """

    pass


def connectionInfo(*args, **kwargs):
    """
    The connectionInfocommand is used to get information about connection sources and destinations.  Unlike the isConnected
    command, this command needs only one end of the connection.
    
    Flags:
      - destinationFromSource : dfs    (bool)          [create]
          If the specified plug (or its ancestor) is a source, this flag returns the list of destinations connected from the
          source. (array of strings, empty array if none)
    
      - getExactDestination : ged      (bool)          [create]
          If the plug or its ancestor is connection destination, this returns the name of the plug that is the exact destination.
          (empty string if there is no such connection).
    
      - getExactSource : ges           (bool)          [create]
          If the plug or its ancestor is a connection source, this returns the name of the plug that is the exact source. (empty
          string if there is no such connection).
    
      - getLockedAncestor : gla        (bool)          [create]
          If the specified plug is locked, its name is returned.  If an ancestor of the plug is locked, its name is returned.  If
          more than one ancestor is locked, only the name of the closest one is returned.  If neither this plug nor any ancestors
          are locked, an empty string is returned.
    
      - isDestination : id             (bool)          [create]
          Returns true if the plug (or its ancestor) is the destination of a connection, false otherwise.
    
      - isExactDestination : ied       (bool)          [create]
          Returns true if the plug is the exact destination of a connection, false otherwise.
    
      - isExactSource : ies            (bool)          [create]
          Returns true if the plug is the exact source of a connection, false otherwise.
    
      - isLocked : il                  (bool)          [create]
          Returns true if this plug (or its ancestor) is locked
    
      - isSource : isSource            (bool)          [create]
          Returns true if the plug (or its ancestor) is the source of a connection, false otherwise.
    
      - sourceFromDestination : sfd    (bool)          [create]
          If the specified plug (or its ancestor) is a destination, this flag returns the source of the connection. (string, empty
          if none)                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.connectionInfo`
    """

    pass


def evalDeferred(*args, **kwargs):
    """
    This command takes the string it is given and evaluates it during the next available idle time.  It is useful for
    attaching commands to controls that can change or delete the control.
    
    Flags:
      - evaluateNext : en              (bool)          []
    
      - list : ls                      (bool)          [create]
          Return a list of the command strings that are currently pending on the idle queue. By default, it will return the list
          of commands for all priorities. The -lowestPriority and -lowPriority can be used to restrict the list of commands to a
          given priority level.
    
      - lowPriority : low              (bool)          [create]
          Specified that the command to be executed should be deferred with the low priority. That is, it will be executed
          whenever Maya is idle.
    
      - lowestPriority : lp            (bool)          [create]
          Specified that the command to be executed should be deferred with the lowest priority. That is, it will be executed when
          no other idle events are scheduled.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.evalDeferred`
    """

    pass


def selectPriority(*args, **kwargs):
    """
    The selectPrioritycommand is used to change the selection priority of particular types of objects that can be selected
    when using the select tool. It accepts no other arguments besides the flags. These flags are the same as used by the
    'selectType' command.
    
    Flags:
      - allComponents : alc            (int)           [create,query]
          Set all component selection priority
    
      - allObjects : alo               (int)           [create,query]
          Set all object selection priority
    
      - animBreakdown : abd            (int)           [create,query]
          Set animation breakdown selection priority
    
      - animCurve : ac                 (int)           [create,query]
          Set animation curve selection priority
    
      - animInTangent : ait            (int)           [create,query]
          Set animation in-tangent selection priority
    
      - animKeyframe : ak              (int)           [create,query]
          Set animation keyframe selection priority
    
      - animOutTangent : aot           (int)           [create,query]
          Set animation out-tangent selection priority
    
      - byName : bn                    (unicode, bool) [create]
          Set selection priority for the specified user-defined selection type
    
      - camera : ca                    (int)           [create,query]
          Set camera selection priority
    
      - cluster : cl                   (int)           [create,query]
          Set cluster selection priority
    
      - collisionModel : clm           (int)           [create,query]
          Set collision model selection priority
    
      - controlVertex : cv             (int)           [create,query]
          Set control vertex selection priority
    
      - curve : c                      (int)           [create,query]
          Set curve selection priority
    
      - curveKnot : ck                 (int)           [create,query]
          Set curve knot selection priority
    
      - curveOnSurface : cos           (int)           [create,query]
          Set curve-on-surface selection priority
    
      - curveParameterPoint : cpp      (int)           [create,query]
          Set curve parameter point selection priority
    
      - dimension : dim                (int)           [create,query]
          Set dimension shape selection priority
    
      - dynamicConstraint : dc         (int)           [create,query]
          Set dynamicConstraint selection priority
    
      - edge : eg                      (int)           [create,query]
          Set mesh edge selection priority
    
      - editPoint : ep                 (int)           [create,query]
          Set edit-point selection priority
    
      - emitter : em                   (int)           [create,query]
          Set emitter selection priority
    
      - facet : fc                     (int)           [create,query]
          Set mesh face selection priority
    
      - field : fi                     (int)           [create,query]
          Set field selection priority
    
      - fluid : fl                     (int)           [create,query]
          Set fluid selection priority
    
      - follicle : fo                  (int)           [create,query]
          Set follicle selection priority
    
      - hairSystem : hs                (int)           [create,query]
          Set hairSystem selection priority
    
      - handle : ha                    (int)           [create,query]
          Set object handle selection priority
    
      - hull : hl                      (int)           [create,query]
          Set hull selection priority
    
      - ikEndEffector : iee            (int)           [create,query]
          Set ik end effector selection priority
    
      - ikHandle : ikh                 (int)           [create,query]
          Set ik handle selection priority
    
      - imagePlane : ip                (int)           [create,query]
          Set image plane selection mask priority
    
      - implicitGeometry : ig          (int)           [create,query]
          Set implicit geometry selection priority
    
      - isoparm : iso                  (int)           [create,query]
          Set surface iso-parm selection priority
    
      - joint : j                      (int)           [create,query]
          Set ik handle selection priority
    
      - jointPivot : jp                (int)           [create,query]
          Set joint pivot selection priority
    
      - lattice : la                   (int)           [create,query]
          Set lattice selection priority
    
      - latticePoint : lp              (int)           [create,query]
          Set lattice point selection priority
    
      - light : lt                     (int)           [create,query]
          Set light selection priority
    
      - localRotationAxis : ra         (int)           [create,query]
          Set local rotation axis selection priority
    
      - locator : lc                   (int)           [create,query]
          Set locator (all types) selection priority
    
      - locatorUV : luv                (int)           [create,query]
          Set uv locator selection priority
    
      - locatorXYZ : xyz               (int)           [create,query]
          Set xyz locator selection priority
    
      - meshUVShell : msh              (int)           [create,query]
          Set uv shell component mask on/off.
    
      - motionTrailPoint : mtp         (int)           [create,query]
          Set motion point selection priority
    
      - motionTrailTangent : mtt       (int)           [create,query]
          Set motion point tangent priority
    
      - nCloth : ncl                   (int)           [create,query]
          Set nCloth selection priority
    
      - nParticle : npr                (int)           [create,query]
          Set nParticle point selection priority
    
      - nParticleShape : nps           (int)           [create,query]
          Set nParticle shape selection priority
    
      - nRigid : nr                    (int)           [create,query]
          Set nRigid selection priority
    
      - nonlinear : nl                 (int)           [create,query]
          Set nonlinear selection priority
    
      - nurbsCurve : nc                (int)           [create,query]
          Set nurbs-curve selection priority
    
      - nurbsSurface : ns              (int)           [create,query]
          Set nurbs-surface selection priority
    
      - orientationLocator : ol        (int)           [create,query]
          Set orientation locator selection priority
    
      - particle : pr                  (int)           [create,query]
          Set particle point selection priority
    
      - particleShape : ps             (int)           [create,query]
          Set particle shape selection priority
    
      - plane : pl                     (int)           [create,query]
          Set sketch plane selection priority
    
      - polymesh : p                   (int)           [create,query]
          Set poly-mesh selection priority
    
      - polymeshEdge : pe              (int)           [create,query]
          Set poly-mesh edge selection priority
    
      - polymeshFace : pf              (int)           [create,query]
          Set poly-mesh face selection priority
    
      - polymeshFreeEdge : pfe         (int)           [create,query]
          Set poly-mesh free-edge selection priority
    
      - polymeshUV : puv               (int)           [create,query]
          Set poly-mesh UV point selection priority
    
      - polymeshVertex : pv            (int)           [create,query]
          Set poly-mesh vertex selection priority
    
      - polymeshVtxFace : pvf          (int)           [create,query]
          Set poly-mesh vtxFace selection priority
    
      - queryByName : qbn              (unicode)       [query]
          Query selection priority for the specified user-defined selection type
    
      - rigidBody : rb                 (int)           [create,query]
          Set rigid body selection priority
    
      - rigidConstraint : rc           (int)           [create,query]
          Set rigid constraint selection priority
    
      - rotatePivot : rp               (int)           [create,query]
          Set rotate pivot selection priority
    
      - scalePivot : sp                (int)           [create,query]
          Set scale pivot selection priority
    
      - sculpt : sc                    (int)           [create,query]
          Set sculpt selection priority
    
      - selectHandle : sh              (int)           [create,query]
          Set select handle selection priority
    
      - spring : spr                   (int)           [create,query]
          Set spring shape selection priority
    
      - springComponent : spc          (int)           [create,query]
          Set individual spring selection priority
    
      - stroke : str                   (int)           [create,query]
          Set stroke selection priority
    
      - subdiv : sd                    (int)           [create,query]
          Set subdivision surface selection priority
    
      - subdivMeshEdge : sme           (int)           [create,query]
          Set subdivision surface mesh edge selection priority
    
      - subdivMeshFace : smf           (int)           [create,query]
          Set subdivision surface mesh face selection priority
    
      - subdivMeshPoint : smp          (int)           [create,query]
          Set subdivision surface mesh point selection priority
    
      - subdivMeshUV : smu             (int)           [create,query]
          Set subdivision surface mesh UV map selection priority
    
      - surfaceEdge : se               (int)           [create,query]
          Set surface edge selection priority
    
      - surfaceFace : sf               (int)           [create,query]
          Set surface face selection priority
    
      - surfaceKnot : sk               (int)           [create,query]
          Set surface knot selection priority
    
      - surfaceParameterPoint : spp    (int)           [create,query]
          Set surface parameter point selection priority
    
      - surfaceRange : sr              (int)           [create,query]
          Set surface range selection priority
    
      - texture : tx                   (int)           [create,query]
          Set texture selection priority
    
      - vertex : v                     (int)           [create,query]
          Set mesh vertex selection priority                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.selectPriority`
    """

    pass


def vnnPaste(*args, **kwargs):
    """
    Paste the copied VNN nodes to target VNN compound. The first parameter is the full name of the DG node that contains the
    VNN graph. The second parameter is the full path of the target VNN compound. A vnnCopymust be called before this command
    is called.
    
    
    Derived from mel command `maya.cmds.vnnPaste`
    """

    pass


def listNodeTypes(*args, **kwargs):
    """
    Lists dependency node types satisfying a specified classification string. See the 'getClassification' command for a list
    of the standard classification strings.
    
    Flags:
      - exclude : ex                   (unicode)       [create]
          Nodes that satisfies this exclude classification will be filtered out.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.listNodeTypes`
    """

    pass


def _getParent(getter, obj, generations):
    """
    If generations is None, then a list of all the parents is returned.
    """

    pass


def colorManagementCatalog(*args, **kwargs):
    """
    This non-undoable action performs additions and removals of custom color transforms from the Autodesk native color
    transform catalog.  Once a custom color transform has been added to the catalog, it can be used in the same way as the
    builtin Autodesk native color transforms.
    
    Flags:
      - addTransform : adt             (unicode)       [create]
          Add transform to collection.
    
      - editUserTransformPath : eut    (unicode)       [create]
          Edit the user transform directory. By changing the directory, all custom transforms currently added could be changed,
          and new ones could appear.
    
      - listSupportedExtensions : lse  (bool)          [create]
          List the file extensions that are supported by add transform.  This list is valid for all transform types, and therefore
          this flag does not require use of the type flag.
    
      - listTransformConnections : ltc (bool)          [create]
          List the transforms that can be used as source (for viewand outputtypes) or destination (for inputand rendering
          spacetypes) to connect a custom transform to the rest of the transform collection.
    
      - path : pth                     (unicode)       [create]
          In addTransform mode, the path to the transform data file.
    
      - queryUserTransformPath : qut   (bool)          [create]
          Query the user transform directory.
    
      - removeTransform : rmt          (unicode)       [create]
          Remove transform from collection.
    
      - transformConnection : tcn      (unicode)       [create]
          In addTransform mode, an existing transform to which the added transform will be connected. For an input transform or
          rendering space transform, this will be a destination. For a view or output transform, this will be a source.
    
      - type : typ                     (unicode)       [create]
          The type of transform added, removed, or whose transform connections are to be listed. Must be one of view, rendering
          space, input, or output.                             Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.colorManagementCatalog`
    """

    pass


def getEnums(attr):
    """
    Get the enumerators for an enum attribute.
    
    :rtype: `util.enum.EnumDict`
    
    >>> addAttr( "persp", ln='numbers', at='enum', enumName="zero:one:two:thousand=1000:three")
    >>> numbers = Attribute('persp.numbers').getEnums()
    >>> sorted(numbers.items())
    [(u'one', 1), (u'thousand', 1000), (u'three', 1001), (u'two', 2), (u'zero', 0)]
    >>> numbers[1]
    u'one'
    >>> numbers['thousand']
    1000
    """

    pass


def curveRGBColor(*args, **kwargs):
    """
    This command creates, changes or removes custom curve colors, which are used to draw the curves in the Graph Editor. The
    custom curve names may contain the wildcards ?, which marches a single character, and \*, which matches any number of
    characters. These colors are part of the UI and not part of the saved data for a model.  This command is not undoable.
    
    Flags:
      - hueSaturationValue : hsv       (bool)          [create,query]
          Indicates that rgb values are really hsv values.
    
      - list : l                       (bool)          [create]
          Writes out a list of all curve color names and their values.
    
      - listNames : ln                 (bool)          [create]
          Returns an array of all curve color names.
    
      - remove : r                     (bool)          [create]
          Removes the named curve color.
    
      - resetToFactory : rf            (bool)          [create]
          Resets all the curve colors to their factory defaults.
    
      - resetToSaved : rs              (bool)          [create]
          Resets all the curve colors to their saved values.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.curveRGBColor`
    """

    pass


def displaySmoothness(*args, **kwargs):
    """
    This command is responsible for setting the display smoothness of NURBS curves and surfaces to either predefined or
    custom values. It also sets display modes for smoothness such as hulls and the hull simplification factors. At present,
    this command is NOT un-doable. In query mode, return type is based on queried flag.
    
    Flags:
      - all : all                      (bool)          [create,query]
          Change smoothness for all curves and surfaces
    
      - boundary : bn                  (bool)          [create,query]
          Display wireframe surfaces using only the boundaries of the surface Not fully implemented yet
    
      - defaultCreation : dc           (bool)          [create,query]
          The default values at creation (applies only -du, -dv, -pw, -ps)
    
      - divisionsU : du                (int)           [create,query]
          Number of isoparm divisions per span in the U direction. The valid range of values is [0,64].
    
      - divisionsV : dv                (int)           [create,query]
          Number of isoparm divisions per span in the V direction. The valid range of values is [0,64].
    
      - full : f                       (bool)          [create,query]
          Display surface at full resolution - the default.
    
      - hull : hl                      (bool)          [create,query]
          Display surface using the hull (control points are drawn rather than surface knot points). This mode is a useful display
          performance improvement when modifying a surface since it doesn't require evaluating points on the surface.
    
      - pointsShaded : ps              (int)           [create,query]
          Number of points per surface span in shaded mode. The valid range of values is [1,64].
    
      - pointsWire : pw                (int)           [create,query]
          Number of points per surface isoparm span or the number of points per curve span in wireframe mode. The valid range of
          values is [1,128]. Note: This is the only flag that also applies to nurbs curves.
    
      - polygonObject : po             (int)           [create,query]
          Display the polygon objects with the given resolution
    
      - renderTessellation : rt        (bool)          [create,query]
          Display using render tesselation parameters when in shaded mode.
    
      - simplifyU : su                 (int)           [create,query]
          Number of spans to skip in the U direction when in hull display mode.
    
      - simplifyV : sv                 (int)           [create,query]
          Number of spans to skip in the V direction when in hull display mode.                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.displaySmoothness`
    """

    pass


def setToolTo(*args, **kwargs):
    """
    This command switches control to the named context.
    
    
    Derived from mel command `maya.cmds.setToolTo`
    """

    pass


def listNodesWithIncorrectNames(*args, **kwargs):
    """
    List all nodes with incorrect names in the Script Editor.
    
    
    Derived from mel command `maya.cmds.listNodesWithIncorrectNames`
    """

    pass


def _MObjectIn(x):
    pass


def affects(*args, **kwargs):
    """
    This command returns the list of attributes on a node or node type which affect the named attribute.
    
    Flags:
      - by : boolean                   (Show attributes that are affected by the given one rather than the
    ones that affect it.) [create]
    
      - type : t                       (unicode)       [create]
          static node type from which to get 'affects' information                                   Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.affects`
    """

    pass


def listConnections(*args, **kwargs):
    """
    This command returns a list of all attributes/objects of a specified type that are connected to the given object(s). If
    no objects are specified then the command lists the connections on selected nodes.
    
    Modifications:
      - returns an empty list when the result is None
      - returns an empty list (with a warning) when the arg is an empty list, tuple,
            set, or frozenset, making it's behavior consistent with when None is
            passed, or no args and nothing is selected (would formerly raise a
            TypeError)
      - When 'connections' flag is True, the attribute pairs are returned in a 2D-array::
    
            [['checker1.outColor', 'lambert1.color'], ['checker1.color1', 'fractal1.outColor']]
    
      - added sourceFirst keyword arg. when sourceFirst is true and connections is also true,
            the paired list of plugs is returned in (source,destination) order instead of (thisnode,othernode) order.
            this puts the pairs in the order that disconnectAttr and connectAttr expect.
      - added ability to pass a list of types
    
        :rtype: `PyNode` list
    
    Flags:
      - connections : c                (bool)          [create]
          If true, return both attributes involved in the connection. The one on the specified object is given first.  Default
          false.
    
      - destination : d                (bool)          [create]
          Give the attributes/objects that are on the destinationside of connection to the given object.  Default true.
    
      - exactType : et                 (bool)          [create]
          When set to true, -t/type only considers node of this exact type. Otherwise, derived types are also taken into account.
    
      - plugs : p                      (bool)          [create]
          If true, return the connected attribute names; if false, return the connected object names only.  Default false;
    
      - shapes : sh                    (bool)          [create]
          Actually return the shape name instead of the transform when the shape is selected.  Default false.
    
      - skipConversionNodes : scn      (bool)          [create]
          If true, skip over unit conversion nodes and return the node connected to the conversion node on the other side.
          Default false.
    
      - source : s                     (bool)          [create]
          Give the attributes/objects that are on the sourceside of connection to the given object.  Default true.
    
      - type : t                       (unicode)       [create]
          If specified, only take objects of a specified type.                               Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.listConnections`
    """

    pass


def displayColor(*args, **kwargs):
    """
    This command changes or queries the display color for anything in the application that allows the user to set its color.
    The color is defined by a color index into either the dormant or active color palette. These colors are part of the UI
    and not part of the saved data for a model.  This command is not undoable. In query mode, return type is based on
    queried flag.
    
    Flags:
      - active : a                     (bool)          [create]
          Specifies the color index applies to active color palette. name Specifies the name of color to change. index The color
          index for the color.
    
      - create : c                     (bool)          [create]
          Creates a new display color which can be queried or set. If is used only when saving color preferences.
    
      - dormant : d                    (bool)          [create]
          Specifies the color index applies to dormant color palette. If neither of the dormant or active flags is specified,
          dormant is the default.
    
      - list : l                       (bool)          [create]
          Writes out a list of all color names and their value.
    
      - queryIndex : qi                (int)           [create]
          Allows you to obtain a list of color names with the given color indices.
    
      - resetToFactory : rf            (bool)          [create]
          Resets all display colors to their factory defaults.
    
      - resetToSaved : rs              (bool)          [create]
          Resets all display colors to their saved values.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.displayColor`
    """

    pass


def listSets(*args, **kwargs):
    """
    The listSets command is used to get a list of all the sets an object belongs to. To get sets of a specific type for an
    object use the type flag as well. To get a list of all sets in the scene then don't use an object in the command line
    but use one of the flags instead.
    
    Modifications:
      - returns wrapped classes
      - if called without arguments and keys works as with allSets=True
      :rtype: `PyNode` list
    
    Flags:
      - allSets : allSets              (bool)          [create]
          Returns all sets in the scene.
    
      - extendToShape : ets            (bool)          [create]
          When requesting a transform's sets also walk down to the shape immediately below it for its sets.
    
      - object : o                     (PyNode)        [create]
          Returns all sets which this object is a member of.
    
      - type : t                       (int)           [create]
          Returns all sets in the scene of the given type: 1 - all rendering sets2 - all deformer setsFlag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.listSets`
    """

    pass


def format(*args, **kwargs):
    """
    This command takes a format string, where the format string contains format specifiers.  The format specifiers have a
    number associated with them relating to which parameter they represent to allow for alternate ordering of the passed-in
    values for other languages by merely changing the format string
    
    Flags:
      - stringArg : s                  (unicode)       [create]
          Specify the arguments for the format string.                               Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.format`
    """

    pass


def artAttrTool(*args, **kwargs):
    """
    The artAttrTool command manages the list of tool types which are         used for attribute painting. This command
    supports querying the         list contents as well as adding new tools to the list. Note that         there is a set of
    built-in tools. The list of built-ins can         be queried by starting Maya and doing an artAttrTool -q. The tools
    which are managed by this command are all intended for         attribute painting via Artisan: when you create a new
    context via         artAttrCtx you specify the tool name via artAttrCtx's -whichToolflag. Typically the user may wish to
    simply use one of the built-in         tools. However, if you need to have custom Properties and Values sheets
    asscociated with your tool, you will need to define a custom tool         via artAttrTool -add toolName. For an example
    of a custom         attribute painting tool, see the devkit example customtoolPaint.mel.           In query mode, return
    type is based on queried flag.
    
    Flags:
      - add : string                   (Adds the named tool to the internal list of tools.) [create]
    
      - exists : ex                    (unicode)       [create,query]
          Checks if the named tool exists, returning true if found, and false otherwise.
    
      - remove : rm                    (unicode)       [create]
          Removes the named tool from the internal list of tools.                                    Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.artAttrTool`
    """

    pass


def timeCode(*args, **kwargs):
    """
    Use this command to query and set the time code information in the file
    
    Flags:
      - mayaStartFrame : msf           (float)         [create,query,edit]
          Sets the Maya start time of the time code, in frames. In query mode, returns the Maya start frame of the time code.
    
      - productionStartFrame : psf     (float)         [create,query,edit]
          Sets the production start time of the time code, in terms of frames. In query mode, returns the sub-second frame of
          production start time.
    
      - productionStartHour : psh      (float)         [create,query,edit]
          Sets the production start time of the time code, in terms of hours. In query mode, returns the hour of production start
          time.
    
      - productionStartMinute : psm    (float)         [create,query,edit]
          Sets the production start time of the time code, in terms of minutes. In query mode, returns the minute of production
          start time.
    
      - productionStartSecond : pss    (float)         [create,query,edit]
          Sets the production start time of the time code, in terms of seconds. In query mode, returns the second of production
          start time.                                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.timeCode`
    """

    pass


def saveToolSettings(*args, **kwargs):
    """
    This command causes all the tools not on the shelf to save their settings as optionVars.  This is called automatically
    by the system when Maya exits.
    
    
    Derived from mel command `maya.cmds.saveToolSettings`
    """

    pass


def listHistory(*args, **kwargs):
    """
    This command traverses backwards or forwards in the graph from the specified node and returns all of the nodes whose
    construction history it passes through. The construction history consists of connections to specific attributes of a
    node defined as the creators and results of the node's main data, eg. the curve for a Nurbs Curve node. For information
    on history connections through specific plugs use the listConnectionscommand first to find where the history begins then
    use this command on the resulting node.
    
    Modifications:
      - returns an empty list when the result is None
      - raises a RuntimeError when the arg is an empty list, tuple, set, or
            frozenset, making it's behavior consistent with when None is passed, or
            no args and nothing is selected (would formerly raise a TypeError)
      - added a much needed 'type' filter
      - added an 'exactType' filter (if both 'exactType' and 'type' are present, 'type' is ignored)
    
        :rtype: `DependNode` list
    
    Flags:
      - allConnections : ac            (bool)          [create]
          If specified, the traversal that searches for the history or future will not restrict its traversal across nodes to only
          dependent plugs. Thus it will reach all upstream nodes (or all downstream nodes for f/future).
    
      - allFuture : af                 (bool)          [create]
          If listing the future, list all of it. Otherwise if a shape has an attribute that represents its output geometry data,
          and that plug is connected, only list the future history downstream from that connection.
    
      - allGraphs : ag                 (bool)          [create]
          This flag is obsolete and has no effect.
    
      - breadthFirst : bf              (bool)          [create]
          The breadth first traversal will return the closest nodes in the traversal first. The depth first traversal will follow
          a complete path away from the node, then return to any other paths from the node. Default is depth first.
    
      - future : f                     (bool)          [create]
          List the future instead of the history.
    
      - futureLocalAttr : fl           (bool)          [query]
          This flag allows querying of the local-space future-related attribute(s) on shape nodes.
    
      - futureWorldAttr : fw           (bool)          [query]
          This flag allows querying of the world-space future-related attribute(s) on shape nodes.
    
      - groupLevels : gl               (bool)          [create]
          The node names are grouped depending on the level.  1 is the lead, the rest are grouped with it.
    
      - historyAttr : ha               (bool)          [query]
          This flag allows querying of the attribute where history connects on shape nodes.
    
      - interestLevel : il             (int)           [create]
          If this flag is set, only nodes whose historicallyInteresting attribute value is not less than the value will be listed.
          The historicallyInteresting attribute is 0 on nodes which are not of interest to non-programmers.  1 for the TDs, 2 for
          the users.
    
      - leaf : lf                      (bool)          [create]
          If transform is selected, show history for its leaf shape. Default is true.
    
      - levels : lv                    (int)           [create]
          Levels deep to traverse. Setting the number of levels to 0 means do all levels. All levels is the default.
    
      - pruneDagObjects : pdo          (bool)          [create]
          If this flag is set, prune at dag objects.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.listHistory`
    """

    pass


def copyAttr(*args, **kwargs):
    """
    Given two nodes, transfer the connections and/or the values from the first node to the second for all attributes whose
    names and data types match. When values are transferred, they are transferred directly. They are not mapped or modified
    in any way. The transferAttributes command can be used to transfer and remap some mesh attributes. The attributes flag
    can be used to specify a list of attributes to be processed. If the attributes flag is unused, all attributes will be
    processed. For dynamic attributes, the values and/or connections will only be transferred if the attributes names on
    both nodes match. This command does not support geometry shape nodes such as meshes, subds and nurbs. This command does
    not support transfer of multi-attribute values such as weight arrays.           In query mode, return type is based on
    queried flag.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          The name of the attribute(s) for which connections and/or values will be transferred. If no attributes are specified,
          then all attributes will be transferred.
    
      - containerParentChild : cpc     (bool)          [create]
          For use when copying from one container to another only. This option indicates that the published parent and/or child
          relationships on the original container should be transferred to the target container if the published names match.
    
      - inConnections : ic             (bool)          [create]
          Indicates that incoming connections should be transferred.
    
      - keepSourceConnections : ksc    (bool)          [create]
          For use with the outConnections flag only. Indicates that the connections should be maintained on the first node, in
          addition to making them to the second node. If outConnections is used and keepSourceConnections is not used, the out
          connections on the source node will be broken and made to the target node.
    
      - outConnections : oc            (bool)          [create]
          Indicates that outgoing connections should be transferred.
    
      - renameTargetContainer : rtc    (bool)          [create]
          For use when copying from one container to another only. This option will rename the target container to the name of the
          original container, and rename the original container to its old name + Orig. You would want to use this option if your
          original container was referenced and edited, and you want those edits from the main scene to now apply to the new
          container.
    
      - values : v                     (bool)          [create]
          Indicates that values should be transferred.                               Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.copyAttr`
    """

    pass


def colorIndex(*args, **kwargs):
    """
    The index specifies a color index in the color palette. The r, g, and b values (between 0-1) specify the RGB values (or
    the HSV values if the -hsv flag is used) for the color.
    
    Flags:
      - hueSaturationValue : hsv       (bool)          [create,query]
          Indicates that rgb values are really hsv values. Upon query, returns the HSV valuses as an array of 3 floats.
    
      - resetToFactory : rf            (bool)          [create]
          Resets all color index palette entries to their factory defaults.
    
      - resetToSaved : rs              (bool)          [create]
          Resets all color palette entries to their saved values.                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.colorIndex`
    """

    pass


def renameAttr(*args, **kwargs):
    """
    Renames the given user-defined attribute to the name given in the string argument. If the new name conflicts with an
    existing name then this command will fail. Note that it is not legal to rename an attribute to the empty string.
    
    
    Derived from mel command `maya.cmds.renameAttr`
    """

    pass


def baseView(*args, **kwargs):
    """
    A view defines the layout information for the attributes of a particular node type or container.  Views can be selected
    from a set of built-in views or may be defined on an associated container template. This command queries the view-
    related information for a container node or for a given template.  The information returned from this command will be
    based on the view-related settings in force on the container node at the time of the query (i.e. the container's view
    mode, template name, view name attributes), when applicable.               In query mode, return type is based on
    queried flag.
    
    Flags:
      - itemInfo : ii                  (unicode)       [query]
          Used in query mode in conjunction with the itemList flag. The command will return a list of information for each item in
          the view, the information fields returned for each item are determined by this argument value. The information fields
          will be listed in the string array returned. The order in which the keyword is specified will determine the order in
          which the data will be returned by the command. One or more of the following keywords, separated by colons ':' are used
          to specify the argument value. itemIndex  : sequential item number (0-based)itemName   : item name (string)itemLabel  :
          item display label (string)itemDescription : item description field (string)itemLevel  : item hierarchy level
          (0-n)itemIsGroup : (boolean 0 or 1) indicates whether or not this item is a groupitemIsAttribute : (boolean 0 or 1)
          indicates whether or not this item is an attributeitemNumChildren: number of immediate children (groups or attributes)
          of this itemitemAttrType : item attribute type (string)itemCallback : item callback field (string)
    
      - itemList : il                  (bool)          [query]
          Used in query mode, the command will return a list of information for each item in the view.  The viewName flag is used
          to select the view to query. The information returned about each item is determined by the itemInfo argument value. For
          efficiency, it is best to query all necessary item information at one time (to avoid recomputing the view information on
          each call).
    
      - viewDescription : vd           (bool)          [query]
          Used in query mode, returns the description field associated with the selected view. If no description was defined for
          this view, the value will be empty.
    
      - viewLabel : vb                 (bool)          [query]
          Used in query mode, returns the display label associated with the view. An appropriate label suitable for the user
          interface will be returned based on the selected view.  Use of the view label is usually more suitable than the view
          name for display purposes.
    
      - viewList : vl                  (bool)          [query]
          Used in query mode, command will return a list of all views defined for the given target (container or template).
    
      - viewName : vn                  (unicode)       [query]
          Used in query mode, specifies the name of the queried view when used in conjunction with a template target. When used in
          conjunction with a container target, it requires no string argument, and returns the name of the currently active view
          associated with the container; this value may be empty if the current view is not a valid template view or is generated
          by one of the built-in views modes. For this reason, the view label is generally more suitable for display purposes. In
          query mode, this flag can accept a value.Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.baseView`
    """

    pass


def displaySurface(*args, **kwargs):
    """
    This command toggles display options on the specified or active surfaces. Typically this command applies to NURBS or
    poly mesh surfaces and ignores other type of objects.
    
    Flags:
      - flipNormals : flp              (bool)          [query]
          flip normal direction on the surface
    
      - twoSidedLighting : two         (bool)          [query]
          toggle if the surface should be considered two-sided.  If it's single-sided, drawing and rendering may use single sided
          lighting and back face cull to improve performance.
    
      - xRay : x                       (bool)          [query]
          toggle X ray mode (make surface transparent)                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.displaySurface`
    """

    pass


def refresh(*args, **kwargs):
    """
    This command is used to force a redraw during script execution. Normally, redraw is suspended while scripts are
    executing but sometimes it is useful to show intermediate results for purposes such as capturing images from the screen.
    If the -cv flag is specified, then only the current active view is redrawn.
    
    Flags:
      - currentView : cv               (bool)          [create]
          Redraw only the current view (default redraws all views).
    
      - fileExtension : fe             (unicode)       []
    
      - filename : fn                  (unicode)       []
    
      - force : f                      (bool)          [create]
          Force the refresh regardless of the state of the model.
    
      - suspend : su                   (bool)          [create]
          Suspends or resumes Maya's handling of refresh events. Specify onto suspend refreshing, and offto resume refreshing.
          Note that resuming refresh does not itself cause a refresh -- the next natural refresh event in Maya after refresh
          -suspend offis issued will cause the refresh to occur. Use this flag with caution: although it provides opportunities to
          enhance performance, much of Maya's dependency graph evaluation in interactive mode is refresh driven, thus use of this
          flag may lead to slight solve differences when you have a complex dependency graph with interrelations.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.refresh`
    """

    pass


def strDeprecateDecorator(func):
    """
    #@decorator
    """

    pass


def containerBind(*args, **kwargs):
    """
    This is an accessory command to the container command which is used for some automated binding operations on the
    container. A container's published interface can be bound using a bindingSet on the associated container template.
    In query mode, return type is based on queried flag.
    
    Flags:
      - allNames : all                 (bool)          [create]
          Specifies that all published names on the container should be considered during the binding operation.  By default only
          unbound published names will be operated on.  Additionally specifying the 'force' option with 'all' will cause all
          previously bound published names to be reset (or unbound) before the binding operation is performed; in the event that
          there is no appropriate binding found for the published name, it will be left in the unbound state.
    
      - bindingSet : bs                (unicode)       [query]
          Specifies the name of the template binding set to use for the bind or query operation. This flag is not available in
          query mode.
    
      - bindingSetConditions : bsc     (bool)          [query]
          Used in query mode, returns a list of binding set condition entries from the specified template binding set.  The list
          returned is composed of of all published name / condition string pairs for each entry in the binding set. This flag
          returns all entries in the associated binding set and does not take into account the validity of each entry with respect
          to the container's list of published names, bound or unbound state, etc.
    
      - bindingSetList : bsl           (bool)          [query,edit]
          Used in query mode, returns a list of available binding sets that are defined on the associated container template.
    
      - force : f                      (bool)          [create]
          This flag is used to force certain operations to proceed that would normally not be performed.
    
      - preview : p                    (bool)          [create]
          This flag will provide a preview of the results of a binding operation but will not actually perform it.  A list of
          publishedName/boundName pairs are returned for each published name that would be affected by the binding action. If the
          binding of a published name will not change as a result of the action it will not be listed. Published names that were
          bound but will become unbound are also listed, in this case the associated boundName will be indicated by an empty
          string.                              Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.containerBind`
    """

    pass


def baseTemplate(*args, **kwargs):
    """
    This is the class for the commands that edit and/or query templates.             In query mode, return type is based on
    queried flag.
    
    Flags:
      - exists : ex                    (bool)          [query]
          Returns true or false depending upon whether the specified template exists. When used with the matchFile argument, the
          query will return true if the template exists and the filename it was loaded from matches the filename given.
    
      - fileName : fn                  (unicode)       [create,query]
          Specifies the filename associated with the template.  This argument can be used in conjunction with load, save or query
          modes. If no filename is associated with a template, a default file name based on the template name will be used.  It is
          recommended but not required that the filename and template name correspond.
    
      - force : f                      (bool)          [create]
          This flag is used with some actions to allow them to proceed with an overwrite or destructive operation. When used with
          load, it will allow an existing template to be reloaded from a file.  When used in create mode, it will allow an
          existing template to be recreated (for example when using fromContainer argument to regenerate a template).
    
      - load : l                       (bool)          []
          Load an existing template from a file. If a filename is specified for the template, the entire file (and all templates
          in it) will be loaded. If no file is specified, a default filename will be assumed, based on the template name.
    
      - matchFile : mf                 (unicode)       [query]
          Used in query mode in conjunction with other flags this flag specifies an optional file name that is to be matched as
          part of the query operation.
    
      - silent : si                    (bool)          [create,query,edit]
          Silent mode will suppress any error or warning messages that would normally be reported from the command execution.  The
          return values are unaffected.
    
      - unload : u                     (bool)          [create]
          Unload the specified template.  This action will not delete the associated template file if one exists, it merely
          removes the template definition from the current session.
    
      - viewList : vl                  (unicode)       [create,query]
          Used in query mode, returns a list of all views defined on the template.                                   Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.baseTemplate`
    """

    pass


def currentUnit(*args, **kwargs):
    """
    This command allows you to change the units in which you will work in Maya. There are three types of units: linear,
    angular and time. The current unit affects how all commands in Maya interpret their numeric values. For example, if the
    current linear unit is cm, then the command: move 5 -2 3; sphere -radius 4; will be interpreted as moving 5cm in X, -2cm
    in Y, 3cm in Z, and as creating a sphere with radius 4cm. Similarly, if the current time unit is Film (24 frames per
    second), then the command: currentTime 6; will be interpreted as setting the current time to frame 6 in the Film unit,
    which is 6/24 or 0.25 seconds. You can always override the unit of a particular numeric value to a command be specifying
    it one the command. For example, using the above examples: move 5m -2mm 3cm; sphere -radius 4inch; currentTime 6ntsc;
    would move the object 5 meters in X, -2 millimeters in Y, 3 centimeters in Z, create a sphere of radius 4 inches, and
    change the current time to 6 frames in the NTSC unit, which would be 0.2 seconds, or 4.8 frames in the current (Film)
    unit.
    
    Flags:
      - angle : a                      (unicode)       [create,query]
          Set the current angular unit. Valid strings are: [deg | degree | rad | radian] When queried, returns a string which is
          the current angular unit
    
      - fullName : f                   (bool)          [query]
          A query only flag. When specified in conjunction with any of the -linear/-angle/-time flags, will return the long form
          of the unit. For example, mmand millimeterare the same unit, but the former is the short form of the unit name, and the
          latter is the long form of the unit name.
    
      - linear : l                     (unicode)       [create,query]
          Set the current linear unit. Valid strings are: [mm | millimeter | cm | centimeter | m | meter | km | kilometer | in |
          inch | ft | foot | yd | yard | mi | mile] When queried, returns a string which is the current linear unit
    
      - time : t                       (unicode)       [create,query]
          Set the current time unit. Valid strings are: [hour | min | sec | millisec | game | film | pal | ntsc | show | palf |
          ntscf] When queried, returns a string which is the current time unit Note that there is no long form for any of the time
          units. The non-seconds based time units are interpreted as the following frames per second: game: 15 fpsfilm: 24 fpspal:
          25 fpsntsc: 30 fpsshow: 48 fpspalf: 50 fpsntscf: 60 fps
    
      - updateAnimation : ua           (bool)          [create]
          An edit only flag.  When specified in conjunction with the -time flag indicates that times for keys are not updated.  By
          default when the current time unit is changed, the times for keys are modified so that playback timing is preserved.
          For example a key set a frame 12film is changed to frame 15ntsc when the current time unit is changed to ntsc, since
          they both represent a key at a time of 0.5 seconds.  Specifying -updateAnimation false would leave the key at frame
          12ntsc. Default is -updateAnimation true.                  Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.currentUnit`
    """

    pass


def containerProxy(*args, **kwargs):
    """
    Creates a new container with the same published interface, dynamic attributes and attribute values as the specified
    container but with fewer container members. This proxy container can be used as a reference proxy so that values can be
    set on container attributes without loading in the full container. The proxy container will contain one or more locator
    nodes. The first locator has dynamic attributes that serve as stand-ins for the original published attributes. The
    remaining locators serve as stand-ins for any dag nodes that have been published as parent or as child and will be
    placed at the world space location of the published parent/child nodes. The expected usage of container proxies is to
    serve as a reference proxy for a referenced container. For automated creation, export and setup of the proxy see the
    doExportContainerProxy.mel script which is invoked by the Export Container Proxymenu item.                  In query
    mode, return type is based on queried flag.
    
    Flags:
      - fromTemplate : ft              (unicode)       [create]
          Specifies the name of a template file which will be used to create the new container proxy. Stand-in attributes will be
          created and published for all the numeric attributes on the proxy.
    
      - type : typ                     (unicode)       [create]
          Specifies the type of container node to use for the proxy. This flag is only valid in conjunction with the fromTemplate
          flag. When creating a proxy for an existing container, the type created will always be identical to that of the source
          container. The default value for this flag is 'container'.                                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.containerProxy`
    """

    pass


def addExtension(*args, **kwargs):
    """
    This command is used to add an extension attribute to a node type. Either the longName or the shortName or both must be
    specified. If neither a dataType nor an attributeType is specified, a double attribute will be added.  The dataType flag
    can be specified more than once indicating that any of the supplied types will be accepted (logical-or).  To add a non-
    double attribute the following criteria can be used to determine whether the dataType or the attributeType flag is
    appropriate.  Some types, such as double3can use either. In these cases the -dtflag should be used when you only wish to
    access the data as an atomic entity (eg. you never want to access the three individual values that make up a double3).
    In general it is best to use the -atin these cases for maximum flexibility. In most cases the -dtversion will not
    display in the attribute editor as it is an atomic type and you are not allowed to change individual parts of it.  All
    attributes flagged as (compound)below or the compound attribute itself are not actually added to the node until all of
    the children are defined (using the -pflag to set their parent to the compound being created).  See the EXAMPLES section
    for more details.  Type of attribute              Flag and argument to use      boolean
    -at bool                      32 bit integer                                 -at long                      16 bit
    integer                                 -at short                     8 bit integer                                  -at
    byte                      char                                                   -at char                      enum
    -at enum (specify the enum names using the enumName flag) float                                                  -at
    float(use quotes                                                                         since float is a mel keyword)
    double                                                 -at double            angle value
    -at doubleAngle       linear value                                   -at doubleLinear      string
    -dt string(use quotes                                                                         since string is a mel
    keyword)  array of strings                               -dt stringArray       compound
    -at compound          message (no data)                              -at message           time
    -at time                      4x4 double matrix                              -dt matrix(use quotes
    since matrix is a mel keyword)  4x4 float matrix                               -at fltMatrix         reflectance
    -dt reflectanceRGBreflectance (compound)                 -at reflectance       spectrum
    -dt spectrumRGB       spectrum (compound)                    -at spectrum          2 floats
    -dt float2            2 floats (compound)                    -at float2            3 floats
    -dt float3            3 floats (compound)                    -at float3            2 doubles
    -dt double2           2 doubles (compound)                   -at double2           3 doubles
    -dt double3           3 doubles (compound)                   -at double3           2 32-bit integers
    -dt long2                     2 32-bit integers (compound)   -at long2                     3 32-bit integers
    -dt long3                     3 32-bit integers (compound)   -at long3                     2 16-bit integers
    -dt short2            2 16-bit integers (compound)   -at short2            3 16-bit integers
    -dt short3            3 16-bit integers (compound)   -at short3            array of doubles
    -dt doubleArray       array of floats                                -dt floatArray        array of 32-bit ints
    -dt Int32Array        array of vectors                               -dt vectorArray       nurbs curve
    -dt nurbsCurve        nurbs surface                                  -dt nurbsSurface      polygonal mesh
    -dt mesh                      lattice                                                -dt lattice           array of
    double 4D points              -dt pointArray
    
    Flags:
      - attributeType : at             (unicode)       [create,query]
          Specifies the attribute type, see above table for more details. Note that the attribute types float, matrixand stringare
          also MEL keywords and must be enclosed in quotes.
    
      - binaryTag : bt                 (unicode)       [create,query]
          This flag is obsolete and does not do anything any more
    
      - cachedInternally : ci          (bool)          [create,query]
          Whether or not attribute data is cached internally in the node. This flag defaults to true for writable attributes and
          false for non-writable attributes. A warning will be issued if users attempt to force a writable attribute to be
          uncached as this will make it impossible to set keyframes.
    
      - category : ct                  (unicode)       [create,query,edit]
          An attribute category is a string associated with the attribute to identify it. (e.g. the name of a plugin that created
          the attribute, version information, etc.) Any attribute can be associated with an arbitrary number of categories however
          categories can not be removed once associated.
    
      - dataType : dt                  (unicode)       [create,query]
          Specifies the data type.  See setAttrfor more information on data type names.
    
      - defaultValue : dv              (float)         [create,query,edit]
          Specifies the default value for the attribute (can only be used for numeric attributes).
    
      - disconnectBehaviour : dcb      (int)           [create,query]
          defines the Disconnect Behaviour 2 Nothing, 1 Reset, 0 Delete
    
      - enumName : en                  (unicode)       [create,query,edit]
          Flag used to specify the ui names corresponding to the enum values. The specified string should contain a colon-
          separated list of the names, with optional values. If values are not specified, they will treated as sequential integers
          starting with 0. For example: -enumName A:B:Cwould produce options: A,B,C with values of 0,1,2; -enumName
          zero:one:two:thousand=1000would produce four options with values 0,1,2,1000; and -enumName
          solo=1:triplet=3:quintet=5would produce three options with values 1,3,5.  (Note that there is a current limitation of
          the Channel Box that will sometimes incorrectly display an enumerated attribute's pull-down menu.  Extra menu items can
          appear that represent the numbers inbetween non-sequential option values.  To avoid this limitation, specify sequential
          values for the options of any enumerated attributes that will appear in the Channel Box.  For example:
          solo=1:triplet=2:quintet=3.)
    
      - exists : ex                    (bool)          [create,query]
          Returns true if the attribute queried is a user-added, dynamic attribute; false if not.
    
      - fromPlugin : fp                (bool)          [create,query]
          Was the attribute originally created by a plugin? Normally set automatically when the API call is made - only added here
          to support storing it in a file independently from the creating plugin.
    
      - hasMaxValue : hxv              (bool)          [create,query,edit]
          Flag indicating whether an attribute has a maximum value. (can only be used for numeric attributes).
    
      - hasMinValue : hnv              (bool)          [create,query,edit]
          Flag indicating whether an attribute has a minimum value. (can only be used for numeric attributes).
    
      - hasSoftMaxValue : hsx          (bool)          [create,query]
          Flag indicating whether a numeric attribute has a soft maximum.
    
      - hasSoftMinValue : hsn          (bool)          [create,query]
          Flag indicating whether a numeric attribute has a soft minimum.
    
      - hidden : h                     (bool)          [create,query]
          Will this attribute be hidden from the UI?
    
      - indexMatters : im              (bool)          [create,query]
          Sets whether an index must be used when connecting to this multi-attribute. Setting indexMatters to false forces the
          attribute to non-readable.
    
      - internalSet : internalSet      (bool)          [create,query]
          Whether or not the internal cached value is set when this attribute value is changed.  This is an internal flag used for
          updating UI elements.
    
      - keyable : k                    (bool)          [create,query]
          Is the attribute keyable by default?
    
      - longName : ln                  (unicode)       [create,query]
          Sets the long name of the attribute.
    
      - maxValue : max                 (float)         [create,query,edit]
          Specifies the maximum value for the attribute (can only be used for numeric attributes).
    
      - minValue : min                 (float)         [create,query,edit]
          Specifies the minimum value for the attribute (can only be used for numeric attributes).
    
      - multi : m                      (bool)          [create,query]
          Makes the new attribute a multi-attribute.
    
      - niceName : nn                  (unicode)       [create,query,edit]
          Sets the nice name of the attribute for display in the UI.  Setting the attribute's nice name to a non-empty string
          overrides the default behaviour of looking up the nice name from Maya's string catalog.   (Use the MEL commands
          attributeNiceNameand attributeQuery -niceNameto lookup an attribute's nice name in the catalog.)
    
      - nodeType : nt                  (unicode)       [create,edit]
          Specifies the type of node to which the attribute will be added. See the nodeType command for the names of different
          node types.
    
      - numberOfChildren : nc          (int)           [create,query]
          How many children will the new attribute have?
    
      - parent : p                     (unicode)       [create,query]
          Attribute that is to be the new attribute's parent.
    
      - proxy : pxy                    (unicode)       [create,query]
          Proxy another node's attribute. Proxied plug will be connected as source. The UsedAsProxy flag is automatically set in
          this case.
    
      - readable : r                   (bool)          [create,query]
          Can outgoing connections be made from this attribute?
    
      - shortName : sn                 (unicode)       [create,query]
          Sets the short name of the attribute.
    
      - softMaxValue : smx             (float)         [create,query,edit]
          Soft maximum, valid for numeric attributes only.  Specifies the upper default limit used in sliders for this attribute.
    
      - softMinValue : smn             (float)         [create,query,edit]
          Soft minimum, valid for numeric attributes only.  Specifies the upper default limit used in sliders for this attribute.
    
      - storable : s                   (bool)          [create,query]
          Can the attribute be stored out to a file?
    
      - usedAsColor : uac              (bool)          [create,query]
          Is the attribute to be used as a color definition? Must have 3 DOUBLE or 3 FLOAT children to use this flag.  The
          attribute type -atshould be double3or float3as appropriate.  It can also be used to less effect with data types -dtas
          double3or float3as well but some parts of the code do not support this alternative.  The special attribute types/data
          spectrumand reflectancealso support the color flag and on them it is set by default.
    
      - usedAsFilename : uaf           (bool)          [create,query]
          Is the attribute to be treated as a filename definition? This flag is only supported on attributes with data type -dtof
          string.
    
      - usedAsProxy : uap              (bool)          [create,query]
          Set if the specified attribute should be treated as a proxy to another attributes.
    
      - writable : w                   (bool)          [create,query]
          Can incoming connections be made to this attribute?                                Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.addExtension`
    """

    pass


def containerPublish(*args, **kwargs):
    """
    This is an accessory command to the container command which is used for some advanced publishing operations on the
    container. For example, the publishConnectionsflag on the container will publish all the connections, but this command
    can be used to publish just the inputs, outputs, or to collapse the shared inputs into a single attribute before
    publishing.           In query mode, return type is based on queried flag.
    
    Flags:
      - bindNode : bn                  (unicode, unicode) [create,query,edit]
          Bind the specified node to the published node name.
    
      - bindTemplateStandins : bts     (bool)          [create,query,edit]
          This flag will create a temporary stand-in attribute for any attributes that exist in the template but are not already
          bound. This enables you to set values for unbound attributes.
    
      - inConnections : ic             (bool)          [create]
          Specifies that the unpublished connections to nodes in the container from external nodes should be published.
    
      - mergeShared : ms               (bool)          [create]
          For use with the inConnections flag. Indicates that when an external attribute connects to multiple internal attributes
          within the container, a single published attribute should be used to correspond to all of the internal attributes.
    
      - outConnections : oc            (bool)          [create]
          Specifies that the unpublished connections from nodes in the container to external nodes should be published.
    
      - publishNode : pn               (unicode, unicode) [create,query,edit]
          Publish a name and type. When first published, nothing will be bound. To bind a node to the published name, use the
          bindNode flag.
    
      - unbindNode : ubn               (unicode)       [create,query,edit]
          Unbind the node that is published with the name specified by the flag.
    
      - unpublishNode : upn            (unicode)       [create,query,edit]
          Unpublish the specified published node name.                               Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.containerPublish`
    """

    pass


def hide(*args, **kwargs):
    """
    The hidecommand is used to make objects invisible. If no flags are used, the objects specified, or the active objects if
    none are specified, will be made invisible.
    
    Flags:
      - allObjects : all               (bool)          [create]
          Make everything invisible (top level objects).
    
      - clearLastHidden : clh          (bool)          []
    
      - clearSelection : cs            (bool)          [create]
          Clear selection after the operation.
    
      - invertComponents : ic          (bool)          [create]
          Hide components that are not specified.
    
      - returnHidden : rh              (bool)          [create]
          Hide objects, but also return list of hidden objects.
    
      - testVisibility : tv            (bool)          [create]
          Do not change visibility, just test it (returns 1 is invisible, 2 if visible, 3 if partially visible).
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.hide`
    """

    pass


def createDisplayLayer(*args, **kwargs):
    """
    Create a new display layer.  The display layer number will be assigned based on the first unassigned number not less
    than the base index number found in the display layer global parameters.  Normally all objects and their descendants
    will be added to the new display layer but if the '-nr' flag is specified then only the objects themselves will be
    added.
    
    Modifications:
      - returns a PyNode object
    
    Flags:
      - empty : e                      (bool)          [create]
          If set then create an empty display layer.  ie. Do not add the selected items to the new display layer.
    
      - makeCurrent : mc               (bool)          [create]
          If set then make the new display layer the current one.
    
      - name : n                       (unicode)       [create]
          Name of the new display layer being created.
    
      - noRecurse : nr                 (bool)          [create]
          If set then only add selected objects to the display layer.  Otherwise all descendants of the selected objects will also
          be added.
    
      - number : num                   (int)           [create]
          Number for the new display layer being created.                                    Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.createDisplayLayer`
    """

    pass


def colorManagementConvert(*args, **kwargs):
    """
    This command can be used to convert rendering (a.k.a. working) space color values to display space color values. This is
    useful if you create custom UI with colors painted to screen, where you need to handle color management yourself. The
    current view transform set in the Color Management user preferences will be used.
    
    Flags:
      - toDisplaySpace : tds           (float, float, float) [create]
          Converts the given RGB value to display space.                             Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.colorManagementConvert`
    """

    pass


def ls(*args, **kwargs):
    """
    The lscommand returns the names (and optionally the type names) of objects in the scene. The most common use of lsis to
    filter or match objects based on their name (using wildcards) or based on their type. By default lswill match any object
    in the scene but it can also be used to filter or list the selected objects when used in conjunction with the -selection
    flag. If type names are requested, using the showType flag, they will be interleaved with object names so the result
    will be pairs of object, typevalues. Internal nodes (for example itemFilter nodes) are typically filtered so that only
    scene objects are returned. However, using a wildcard will cause all the nodes matching the wild card to show up,
    including internal nodes.  For example, ls \*will list all nodes whether internal or not. When Maya is in relativeNames
    mode, the lscommand will return names relativeto the current namespace and ls \*will list from the the current
    namespace. For more details, please refer to the -relativeNamesflag of the namespacecommand. The command may also be
    passed node UUIDs instead of names/paths, and can return UUIDs instead of names via the -uuid flag.
    
    Modifications:
      - Returns PyNode objects, not "names" - all flags which do nothing but modify
        the string name of returned objects are ignored (ie, 'long'); note that
        the 'allPaths' flag DOES have an effect, as PyNode objects are aware of
        their dag paths (ie, two different instances of the same object will result
        in two unique PyNodes)
      - Added new keyword: 'editable' - this will return the inverse set of the readOnly flag. i.e. non-read-only nodes
      - Added new keyword: 'regex' - pass a valid regular expression string, compiled regex pattern, or list thereof.
    
            >>> group('top')
            nt.Transform(u'group1')
            >>> duplicate('group1')
            [nt.Transform(u'group2')]
            >>> group('group2')
            nt.Transform(u'group3')
            >>> ls(regex='group\d+\|top') # don't forget to escape pipes `|`
            [nt.Transform(u'group1|top'), nt.Transform(u'group2|top')]
            >>> ls(regex='group\d+\|top.*')
            [nt.Transform(u'group1|top'), nt.Camera(u'group1|top|topShape'), nt.Transform(u'group2|top'), nt.Camera(u'group2|top|topShape')]
            >>> ls(regex='group\d+\|top.*', cameras=1)
            [nt.Camera(u'group2|top|topShape'), nt.Camera(u'group1|top|topShape')]
            >>> ls(regex='\|group\d+\|top.*', cameras=1) # add a leading pipe to search for full path
            [nt.Camera(u'group1|top|topShape')]
    
        The regular expression will be used to search the full DAG path, starting from the right, in a similar fashion to how globs currently work.
        Technically speaking, your regular expression string is used like this::
    
            re.search( '(\||^)' + yourRegexStr + '$', fullNodePath )
    
        :rtype: `PyNode` list
    
    Flags:
      - absoluteName : an              (bool)          [create]
          This flag can be used in conjunction with the showNamespace flag to specify that the namespace(s) returned by the
          command be in absolute namespace format. The absolute name of the namespace is a full namespace path, starting from the
          root namespace :and including all parent namespaces.  For example :ns:ballis an absolute namespace name while ns:ballis
          not. The absolute namespace name is invariant and is not affected by the current namespace or relative namespace modes.
    
      - allPaths : ap                  (bool)          [create]
          List all paths to nodes in DAG. This flag only works if -dagis also specified or if an object name is supplied.
    
      - assemblies : assemblies        (bool)          [create]
          List top level transform Dag objects
    
      - cameras : ca                   (bool)          [create]
          List camera shapes.
    
      - containerType : ct             (unicode)       [create]
          List containers with the specified user-defined type. This flag cannot be used in conjunction with the type or exactType
          flag.
    
      - containers : con               (bool)          [create]
          List containers. Includes both standard containers as well as other types of containers such as dagContainers.
    
      - dagObjects : dag               (bool)          [create]
          List Dag objects of any type. If object name arguments are passed to the command then this flag will list all Dag
          objects below the specified object(s).
    
      - defaultNodes : dn              (bool)          [create]
          Returns default nodes. A default node is one that Maya creates automatically and does not get saved out with the scene,
          although some of its attribute values may.
    
      - dependencyNodes : dep          (bool)          [create]
          List dependency nodes. (including Dag objects)
    
      - exactType : et                 (unicode)       [create]
          List all objects of the specified type, but notobjects that are descendents of that type. This flag can appear multiple
          times on the command line. Note: the type passed to this flag is the same type name returned from the showType flag.
          This flag cannot be used in conjunction with the type or excludeType flag.
    
      - excludeType : ext              (unicode)       [create]
          List all objects that are not of the specified type. This flag can appear multiple times on the command line. Note: the
          type passed to this flag is the same type name returned from the showType flag. This flag cannot be used in conjunction
          with the type or exactType flag.
    
      - flatten : fl                   (bool)          [create]
          Flattens the returned list of objects so that each component is identified individually.
    
      - geometry : g                   (bool)          [create]
          List geometric Dag objects.
    
      - ghost : gh                     (bool)          [create]
          List ghosting objects.
    
      - head : hd                      (int)           [create]
          This flag  specifies the maximum number of elements to be returned from the beginning of the list of items. Note: each
          type flag will return at most this many items so if multiple type flags are specified then the number of items returned
          can be greater than this amount.
    
      - hilite : hl                    (bool)          [create]
          List objects that are currently hilited for component selection.
    
      - intermediateObjects : io       (bool)          [create]
          List only intermediate dag nodes.
    
      - invisible : iv                 (bool)          [create]
          List only invisible dag nodes.
    
      - leaf : lf                      (bool)          [create]
          List all leaf nodes in Dag. This flag is a modifier and must be used in conjunction with the -dag flag.
    
      - lights : lt                    (bool)          [create]
          List light shapes.
    
      - live : lv                      (bool)          [create]
          List objects that are currently live.
    
      - lockedNodes : ln               (bool)          [create]
          Returns locked nodes, which cannot be deleted or renamed. However, their status may change.
    
      - long : l                       (bool)          [create]
          Return full path names for Dag objects. By default the shortest unique name is returned.
    
      - materials : mat                (bool)          [create]
          List materials or shading groups.
    
      - modified : mod                 (bool)          [create]
          When this flag is set, only nodes modified since the last save will be returned.
    
      - noIntermediate : ni            (bool)          [create]
          List only non intermediate dag nodes.
    
      - nodeTypes : nt                 (bool)          [create]
          Lists all registered node types.
    
      - objectsOnly : o                (bool)          [create]
          When this flag is set only object names will be returned and components/attributes will be ignored.
    
      - orderedSelection : os          (bool)          [create]
          List objects and components that are currently selected in their order of selection.  This flag depends on the value of
          the -tso/trackSelectionOrder flag of the selectPref command.  If that flag is not enabled than this flag will return the
          same thing as the -sl/selection flag would.
    
      - partitions : pr                (bool)          [create]
          List partitions.
    
      - persistentNodes : pn           (bool)          [create]
          Returns persistent nodes, which are nodes that stay in the Maya session after a file new. These are a special class of
          default nodes that do not get reset on file new. Ex: itemFilter and selectionListOperator nodes.
    
      - planes : pl                    (bool)          [create]
          List construction plane shapes.
    
      - preSelectHilite : psh          (bool)          [create]
          List components that are currently hilited for pre-selection.
    
      - readOnly : ro                  (bool)          [create]
          Returns referenced nodes. Referenced nodes are read only. NOTE: Obsolete. Please use -referencedNodes.
    
      - recursive : r                  (bool)          [create]
          When set to true, this command will look for name matches in all namespaces. When set to false, this command will only
          look for matches in namespaces that are requested (e.g. by specifying a name containing the ':'... ns1:pSphere1).
    
      - referencedNodes : rn           (bool)          [create]
          Returns referenced nodes. Referenced nodes are read only.
    
      - references : rf                (bool)          [create]
          List references associated with files. Excludes special reference nodes such as the sharedReferenceNode and unknown
          reference nodes.
    
      - renderGlobals : rg             (bool)          [create]
          List render globals.
    
      - renderQualities : rq           (bool)          [create]
          List named render qualities.
    
      - renderResolutions : rr         (bool)          [create]
          List render resolutions.
    
      - renderSetups : rs              (bool)          [create]
          Alias for -renderGlobals.
    
      - selection : sl                 (bool)          [create]
          List objects that are currently selected.
    
      - sets : set                     (bool)          [create]
          List sets.
    
      - shapes : s                     (bool)          [create]
          List shape objects.
    
      - shortNames : sn                (bool)          [create]
          Return short attribute names. By default long attribute names are returned.
    
      - showNamespace : sns            (bool)          [create]
          Show the namespace of each object after the object name. This flag cannot be used in conjunction with the showType flag.
    
      - showType : st                  (bool)          [create]
          List the type of each object after its name.
    
      - tail : tl                      (int)           [create]
          This flag specifies the maximum number of elements to be returned from the end of the list of items. Note: each    type
          flag will return at most this many items so if multiple type flags are specified then the number of items returned can
          be greater than this amount
    
      - templated : tm                 (bool)          [create]
          List only templated dag nodes.
    
      - textures : tex                 (bool)          [create]
          List textures.
    
      - transforms : tr                (bool)          [create]
          List transform objects.
    
      - type : typ                     (unicode)       [create]
          List all objects of the specified type. This flag can appear multiple times on the command line. Note: the type passed
          to this flag is the same type name returned from the showType flag. Note: some selection items in Maya do not have a
          specific object/data type associated with them and will return untypedwhen listed with this flag. This flag cannot be
          used in conjunction with the exactType or excludeType flag.
    
      - undeletable : ud               (bool)          [create]
          Returns nodes that cannot be deleted (which includes locked nodes). These nodes also cannot be renamed.
    
      - untemplated : ut               (bool)          [create]
          List only un-templated dag nodes.
    
      - uuid : uid                     (bool)          [create]
          Return node UUIDs instead of names. Note that there are no UUID paths- combining this flag with e.g. the -long flag will
          not result in a path formed of node UUIDs.
    
      - visible : v                    (bool)          [create]
          List only visible dag nodes.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.ls`
    """

    pass


def color(*args, **kwargs):
    """
    This command sets the dormant wireframe color of the specified objects to be their class color or if the -ud/userDefined
    flag is specified, one of the user defined colors. The -rgb/rgbColor flags can be specified if the user requires
    floating point RGB colors.
    
    Flags:
      - rgbColor : rgb                 (float, float, float) [create]
          Specifies and rgb color to set the selected object to.
    
      - userDefined : ud               (int)           [create]
          Specifies the user defined color index to set selected object to. The valid range of numbers is [1-8].
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.color`
    """

    pass


def listAttrPatterns(*args, **kwargs):
    """
    Attribute patterns are plain text descriptions of an entire Maya attribute forest. (forestbecause there could be an
    arbitrary number of root level attributes, it's not restricted to having a single common parent though in general that
    practice is a good idea.) This command lists the various pattern types available, usually created via plugin, as well as
    any specific patterns that have already been instantiated. A pattern type is a thing that knows how to take some textual
    description of an attribute tree, e.g. XML or plaintext, and convert it into an attribute pattern that can be applied to
    any node or node type in Maya.
    
    Flags:
      - patternType : pt               (bool)          [create]
          If turned on then show the list of pattern types rather than actual instantiated patterns.
    
      - verbose : v                    (bool)          [create]
          If turned on then show detailed information about the patterns or pattern types. The same list of instance or pattern
          names is returned as for the non-verbose case.                               Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.listAttrPatterns`
    """

    pass


def xformConstraint(*args, **kwargs):
    """
    This command allows you to change the transform constraint used by the transform tools during component transforms.
    In query mode, return type is based on queried flag.
    
    Flags:
      - alongNormal : n                (int)           [query,edit]
          When set the transform constraint will first be applied along the vertex normals of the components being transformed.
          When queried, returns the current state of this option.
    
      - live : l                       (bool)          [query]
          Query-only flag that can be used to check whether the current live surface will be used as a transform constraint.
    
      - type : t                       (unicode)       [create,query,edit]
          Set the type of transform constraint to use. When queried, returns the current transform constraint as a string. none -
          no constraintsurface - constrain components to their surfaceedge - constrain components to surface edgesFlag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.xformConstraint`
    """

    pass


def ungroup(*args, **kwargs):
    """
    This command ungroups the specified objects. The objects will be placed at the same level in the hierarchy the group
    node occupied unless the -w flag is specified, in which case they will be placed under the world. If an object is
    ungrouped and there is an object in the new group with the same name then this command will rename the ungrouped object.
    See also:group, parent, instance, duplicate
    
    Flags:
      - absolute : a                   (bool)          [create]
          preserve existing world object transformations (overall object transformation is preserved by modifying the objects
          local transformation) [default]
    
      - parent : p                     (unicode)       [create]
          put the ungrouped objects under the given parent
    
      - relative : r                   (bool)          [create]
          preserve existing local object transformations (don't modify local transformation)
    
      - world : w                      (bool)          [create]
          put the ungrouped objects under the world                  Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.ungroup`
    """

    pass


def contextInfo(*args, **kwargs):
    """
    This command allows you to get information on named contexts.
    
    Flags:
      - apiImage1 : ip1                (unicode)       []
    
      - c : c                          (bool)          [create]
          Return the class type of the named context.
    
      - escapeContext : esc            (bool)          [create]
          Return the command string that will allow you to exit the current tool.
    
      - exists : ex                    (bool)          [create]
          Return true if the context exists, false if it does not exists (or is internal and therefore untouchable)
    
      - image1 : i1                    (bool)          [create]
          Returns the name of an xpm associated with the named context.
    
      - image2 : i2                    (bool)          [create]
          Returns the name of an xpm associated with the named context.
    
      - image3 : i3                    (bool)          [create]
          Returns the name of an xpm associated with the named context.
    
      - title : t                      (bool)          [create]
          Return the title string of the named context.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.contextInfo`
    """

    pass


def itemFilterAttr(*args, **kwargs):
    """
    This command creates a named itemFilterAttr object.  This object can be attached to editors, in order to filter the
    attributes going through them. Using union and intersection filters, complex composite filters can be created.
    
    Flags:
      - byName : bn                    (unicode)       [create,query,edit]
          The filter will only pass items whose names match the given regular expression string.  This string can contain the
          special characters \* and ?.  '?' matches any one character, and '\*' matches any substring. This flag cannot be used in
          conjunction with the -byScript or -secondScript flags.
    
      - byNameString : bns             (unicode)       [create,query,edit]
          The filter will only pass items whose names match the given string. This is a multi-use flag which allows the user to
          specify several strings. The filter will pass items that match any of the strings. This flag cannot be used in
          conjunction with the -byScript or -secondScript flags.
    
      - byScript : bs                  (unicode)       [create,query,edit]
          The filter will run a MEL script named by the given string on each attribute name.  Attributes will pass the filter if
          the script returns a non-zero value. The script name string must be the name of a proc whose signature is:global proc
          int procName( string $nodeName string $attrName )This flag cannot be used in conjunction with the -byName or
          -byNameString flags.
    
      - classification : cls           (unicode)       [create,query,edit]
          Indicates whether the filter is a built-in or user filter. The string argument must be either builtInor user. The
          otherfilter classification is deprecated. Use userinstead.  Filters created by Maya should be classified as builtIn.
          Filters created by plugins or user scripts should be classified as user.  Filters will not be deleted by a file new.
          Filter nodes will be hidden from the UI (ex: Attribute Editor, Hypergraph etc) and will not be accessible from the
          command-line.
    
      - dynamic : dy                   (bool)          []
    
      - exists : ex                    (bool)          []
    
      - hasCurve : hc                  (bool)          [create,query,edit]
          The filter will only pass attributes that are driven by animation curves.
    
      - hasDrivenKey : hdk             (bool)          [create,query,edit]
          The filter will only pass attributes that are driven by driven keys
    
      - hasExpression : he             (bool)          [create,query,edit]
          The filter will only pass attributes that are driven by expressions
    
      - hidden : h                     (bool)          [create,query,edit]
          The filter will only pass attributes that are hidden to the user
    
      - intersect : intersect          (unicode, unicode) [create,query,edit]
          The filter will consist of the intersection of two other filters, whose names are the given strings. Attributes will
          pass this filter if and only if they pass both of the contained filters.
    
      - keyable : k                    (bool)          [create,query,edit]
          The filter will only pass attributes that are keyable
    
      - listBuiltInFilters : lbf       (bool)          [query]
          Returns an array of all attribute filters with classification builtIn.
    
      - listOtherFilters : lof         (bool)          [query]
          The otherclassification has been deprecated. Use userinstead. Returns an array of all attribute filters with
          classification other.
    
      - listUserFilters : luf          (bool)          [query]
          Returns an array of all attribute filters with classification user.
    
      - negate : neg                   (bool)          [create,query,edit]
          This flag can be used to cause the filter to invert itself, and reverse what passes and what fails.
    
      - parent : p                     (unicode)       []
          This flag is no longer supported.
    
      - published : pub                (bool)          [create,query,edit]
          The filter will only pass attributes that are published on the container.
    
      - readable : r                   (bool)          [create,query,edit]
          The filter will only pass attributes that are readable (outputs)
    
      - scaleRotateTranslate : srt     (bool)          [create,query,edit]
          The filter will show only SRT attributes: scale, rotate, translate and their children
    
      - secondScript : ss              (unicode)       [create,query,edit]
          Can be used in conjunction with the -bs flag.  The second script is for filtering whole lists at once, rather than
          individually.  Its signature must be:global proc string[] procName( string[] $nodeName string[] $attrName )It should
          take in a list of attributes, and return a filtered list of attributes. This flag cannot be used in conjunction with the
          -byName or -byNameString flags.
    
      - text : t                       (unicode)       [create,query,edit]
          Defines an annotation string to be stored with the filter
    
      - union : un                     (unicode, unicode) [create,query,edit]
          The filter will consist of the union of two other filters, whose names are the given strings. Attributes will pass this
          filter if they pass at least one of the contained filters.
    
      - writable : w                   (bool)          [create,query,edit]
          The filter will only pass attributes that are writable (inputs)                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.itemFilterAttr`
    """

    pass


def selectMode(*args, **kwargs):
    """
    The selectModecommand is used to change the selection mode.  Object, component, root, leaf and template modes are
    mutually exclusive.
    
    Flags:
      - component : co                 (bool)          [create,query]
          Set component selection on. Component selection mode allows filtered selection based on the component selection mask.
          The component selection mask is the set of selection masks related to objects that indicate which components are
          selectable.
    
      - hierarchical : h               (bool)          [create,query]
          Set hierarchical selection on. There are three types of hierarchical selection: root, leaf and template.  Hierarchical
          mode is set if root, leaf or template mode is set. Setting to hierarchical mode will set the mode to whichever of root,
          leaf, or template was last on.
    
      - leaf : l                       (bool)          [create,query]
          Set leaf selection mode on.  This mode allows the leaf level objects to be selected.  It is similar to object selection
          mode but ignores the object selection mask.
    
      - object : o                     (bool)          [create,query]
          Set object selection on. Object selection mode allows filtered selection based on the object selection mask. The object
          selection mask is the set of selection masks related to objects that indicate which objects are selectable.  The masks
          are controlled by the selectTypecommand.  Object selection mode selects the leaf level objects.
    
      - preset : p                     (bool)          [create,query]
          Allow selection of anything with the mask set, independent of it being an object or a component.
    
      - root : r                       (bool)          [create,query]
          Set root selection mode on.  This mode allows the root of a hierarchy to be selected by selecting any of its
          descendents.  It ignores the object selection mask.
    
      - template : t                   (bool)          [create,query]
          Set template selection mode on.  This mode allows selection of templated objects.  It selects the templated object
          closest to the root of the hierarchy.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.selectMode`
    """

    pass


def aliasAttr(*args, **kwargs):
    """
    Allows aliases (alternate names) to be defined for any attribute of a specified node. When an attribute is aliased, the
    alias will be used by the system to display information about the attribute. The user may, however, freely use either
    the alias or the original name of the attribute. Only a single alias can be specified for an attribute so setting an
    alias on an already-aliased attribute destroys the old alias.
    
    Flags:
      - remove : rm                    (bool)          [create]
          Specifies that aliases listed should be removed (otherwise new aliases are added).                                 Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.aliasAttr`
    """

    pass


def isDirty(*args, **kwargs):
    """
    The isDirtycommand is used to check if a plug is dirty.  The return value is 0 if it is not and 1 if it is.  If more
    than one plug is specified then the result is the logical orof all objects (ie. returns 1 if \*any\* of the plugs are
    dirty).
    
    Flags:
      - connection : c                 (bool)          [create]
          Check the connection of the plug (default).
    
      - datablock : d                  (bool)          [create]
          Check the datablock entry for the plug.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.isDirty`
    """

    pass


def nodeType(node, **kwargs):
    """
    This command returns a string which identifies the given node's type. When no flags are used, the unique type name is
    returned.  This can be useful for seeing if two nodes are of the same type. When the apiflag is used, the MFn::Type of
    the node is returned. This can be useful for seeing if a plug-in node belongs to a given class. The apiflag cannot be
    used in conjunction with any other flags. When the derivedflag is used, the command returns a string array containing
    the names of all the currently known node types which derive from the node type of the given object. When the
    inheritedflag is used, the command returns a string array containing the names of all the base node types inherited by
    the the given node. If the isTypeNameflag is present then the argument provided to the command is taken to be the name
    of a node type rather than the name of a specific node. This makes it possible to query the hierarchy of node types
    without needing to have instances of each node type.
    
    Note: this will return the dg node type for an object, like maya.cmds.nodeType,
        NOT the pymel PyNode class.  For objects like components or attributes,
        nodeType will return the dg type of the node to which the PyNode is attached.
    
        :rtype: `unicode`
    
    Flags:
      - apiType : api                  (bool)          [create]
          Return the MFn::Type value (as a string) corresponding to the given node.  This is particularly useful when the given
          node is defined by a plug-in, since in this case, the MFn::Type value corresponds to the underlying proxy class. This
          flag cannot be used in combination with any of the other flags.
    
      - derived : d                    (bool)          [create]
          Return a string array containing the names of all the currently known node types which derive from the type of the
          specified node.
    
      - inherited : i                  (bool)          [create]
          Return a string array containing the names of all the base node types inherited by the specified node.
    
      - isTypeName : itn               (bool)          [create]
          If this flag is present, then the argument provided to the command is the name of a node type rather than the name of a
          specific node.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nodeType`
    """

    pass


def polySplitCtx2(*args, **kwargs):
    """
    Create a new context to split facets on polygonal objects                In query mode, return type is based on queried
    flag.
    
    Flags:
      - adjustEdgeFlow : aef           (float)         []
    
      - constrainToEdges : cte         (bool)          [create,query,edit]
          Enable/disable snapping to edge. If enabled any click in the current face will snap to the closest valid edge. If there
          is no valid edge, the click will be ignored. NOTE: This is different from magnet snapping, which causes the click to
          snap to certain points along the edge.
    
      - detachEdges : de               (bool)          []
    
      - edgeMagnets : em               (int)           [create,query,edit]
          number of extra magnets to snap onto, regularly spaced along the edge
    
      - exists : ex                    (bool)          []
    
      - highlightPointColor : hpc      (float, float, float) []
    
      - image1 : i1                    (unicode)       []
    
      - image2 : i2                    (unicode)       []
    
      - image3 : i3                    (unicode)       []
    
      - insertWithEdgeFlow : ief       (bool)          []
    
      - snapTolerance : st             (float)         [create,query,edit]
          precision for custom magnet snapping. Range[0,1]. Value 1 means any click on an edge will snap to either extremities or
          magnets.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
      - snappedToEdgeColor : sec       (float, float, float) []
    
      - snappedToFaceColor : sfc       (float, float, float) []
    
      - snappedToMagnetColor : smc     (float, float, float) []
    
      - snappedToVertexColor : svc     (float, float, float) []
    
      - snappingTolerance : st         (float)         []
    
      - splitLineColor : slc           (float, float, float) []
    
    
    Derived from mel command `maya.cmds.polySplitCtx2`
    """

    pass


def scale(obj, *args, **kwargs):
    """
    The scale command is used to change the sizes of geometric objects. The default behaviour, when no objects or flags are
    passed, is to do a relative scale on each currently selected object object using each object's existing scale pivot
    point.
    
    Modifications:
      - allows any iterable object to be passed as first argument::
    
            scale("pSphere1", [0,1,2])
    
    NOTE: this command also reorders the argument order to be more intuitive, with the object first
    
    Flags:
      - absolute : a                   (bool)          [create]
          Perform an absolute operation.
    
      - centerPivot : cp               (bool)          [create]
          Let the pivot be the center of the bounding box of all objects
    
      - constrainAlongNormal : xn      (bool)          [create]
          When true, transform constraints are applied along the vertex normal first and only use the closest point when no
          intersection is found along the normal.
    
      - deletePriorHistory : dph       (bool)          [create]
          If true then delete the history prior to the current operation.
    
      - distanceOnly : dso             (bool)          [create]
          Scale only the distance between the objects.
    
      - localSpace : ls                (bool)          [create]
          Use local space for scaling
    
      - objectCenterPivot : ocp        (bool)          [create]
          Let the pivot be the center of the bounding box of each object
    
      - objectSpace : os               (bool)          [create]
          Use object space for scaling
    
      - orientAxes : oa                (float, float, float) [create]
          Use the angles for the orient axes.
    
      - pivot : p                      (float, float, float) [create]
          Define the pivot point for the transformation
    
      - preserveChildPosition : pcp    (bool)          [create]
          When true, transforming an object will apply an opposite transform to its child transform to keep them at the same
          world-space position. Default is false.
    
      - preserveGeometryPosition : pgp (bool)          [create]
          When true, transforming an object will apply an opposite transform to its geometry points to keep them at the same
          world-space position. Default is false.
    
      - preserveUV : puv               (bool)          [create]
          When true, UV values on scaled components are projected along the axis of scaling in 3d space. For small edits, this
          will freeze the world space texture mapping on the object. When false, the UV values will not change for a selected
          vertices. Default is false.
    
      - reflection : rfl               (bool)          [create]
          To move the corresponding symmetric components also.
    
      - reflectionAboutBBox : rab      (bool)          [create]
          Sets the position of the reflection axis  at the geometry bounding box
    
      - reflectionAboutOrigin : rao    (bool)          [create]
          Sets the position of the reflection axis  at the origin
    
      - reflectionAboutX : rax         (bool)          [create]
          Specifies the X=0 as reflection plane
    
      - reflectionAboutY : ray         (bool)          [create]
          Specifies the Y=0 as reflection plane
    
      - reflectionAboutZ : raz         (bool)          [create]
          Specifies the Z=0 as reflection plane
    
      - reflectionTolerance : rft      (float)         [create]
          Specifies the tolerance to findout the corresponding reflected components
    
      - relative : r                   (bool)          [create]
          Perform a operation relative to the object's current position
    
      - scaleX : x                     (bool)          [create]
          Scale in X direction
    
      - scaleXY : xy                   (bool)          [create]
          Scale in X and Y direction
    
      - scaleXYZ : xyz                 (bool)          [create]
          Scale in all directions (default)
    
      - scaleXZ : xz                   (bool)          [create]
          Scale in X and Z direction
    
      - scaleY : y                     (bool)          [create]
          Scale in Y direction
    
      - scaleYZ : yz                   (bool)          [create]
          Scale in Y and Z direction
    
      - scaleZ : z                     (bool)          [create]
          Scale in Z direction
    
      - symNegative : smn              (bool)          [create]
          When set the component transformation is flipped so it is relative to the negative side of the symmetry plane. The
          default (no flag) is to transform components relative to the positive side of the symmetry plane.
    
      - worldSpace : ws                (bool)          [create]
          Use world space for scaling
    
      - xformConstraint : xc           (unicode)       [create]
          Apply a transform constraint to moving components. none - no constraintsurface - constrain components to the surfaceedge
          - constrain components to surface edgeslive - constraint components to the live surfaceFlag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.scale`
    """

    pass


def _MDagPathIn(x):
    pass


def instance(*args, **kwargs):
    """
    Instancing is a way of making the same object appear twice in the scene. This is accomplished by creation of a new
    transform node that points to an exisiting object. Changes to the transform are independent but changes to the
    instancedobject affect all instances since the node is shared. If no objects are given, then the selected list is
    instanced. When an object is instanced a  new transform node is created that points to the selected object. The smart
    transform feature allows instance to transform newly instanced objects based on previous transformations between
    instances. Example: Instance an object and move it to a new location.  Instance it again with the smart transform flag.
    It should have moved once again the distance you had previously moved it. Note: changing the selected list between smart
    instances will cause the transform information to be deleted. It returns a list of the new objects created by the
    instance operation. See also:duplicate
    
    Modifications:
      - returns a list of PyNode objects
    
    Flags:
      - leaf : lf                      (bool)          [create]
          Instances leaf-level objects. Acts like duplicate except leaf-level objects are instanced.
    
      - name : n                       (unicode)       [create]
          Name to give new instance
    
      - smartTransform : st            (bool)          [create]
          Transforms instances item based on movements between transforms                  Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.instance`
    """

    pass


def colorManagementPrefs(*args, **kwargs):
    """
    This command allows querying and editing the color management global data in a scene.  It also allows for setting the
    view transform and rendering space which automatically configures the color processing in the enabled views.
    In query mode, return type is based on queried flag.
    
    Flags:
      - cmConfigFileEnabled : cfe      (bool)          [query,edit]
          Turn on or off applying an OCIO configuration file.  If set, the color management configuration set in the preferences
          is used.
    
      - cmEnabled : cme                (bool)          [query,edit]
          Turn on or off color management in general.  If set, the color management configuration set in the preferences is used.
    
      - colorManagePots : cmp          (bool)          [query,edit]
          Turn on or off color management of color pots in the UI.  If set, colors in color pots are taken to be in rendering
          space, and are displayed after being transformed by the view transform set in the preferences.
    
      - colorManagedNodes : cmn        (bool)          [query,edit]
          Gets the names of all nodes that apply color management to bring pixels from an input color space to the rendering
          space. Examples include file texture node.
    
      - colorManagementSDKVersion : cmv (unicode)       [query,edit]
          Obtain the version of the color management SDK used by Maya.
    
      - configFilePath : cfp           (unicode)       [query,edit]
          The configuration file to be used, if color management is enabled.
    
      - defaultInputSpaceName : din    (unicode)       [query,edit]
          This flag is obsolete.  See the colorManagementFileRules command for more information.
    
      - equalsToPolicyFile : etp       (unicode)       [query,edit]
          Query if the current loaded policy settings is the same with the settings described in the policy file which is the
          argument of the command.
    
      - exportPolicy : epy             (unicode)       [create,query,edit]
          Export the color management parameters to policy file
    
      - inputSpaceNames : iss          (bool)          [query,edit]
          Returns the list of available input color spaces. Used to populate the input color spaces UI popup.
    
      - loadPolicy : lpy               (unicode)       [create,query,edit]
          Load the color management policy file. This file overides the color management settings.
    
      - loadedDefaultInputSpaceName : ldn (unicode)       [query,edit]
          This flag is obsolete.
    
      - loadedOutputTransformName : lon (unicode)       [query,edit]
          Gets the loaded output transform.  Used by file open, import, and reference to check for missing color spaces or
          transforms.
    
      - loadedRenderingSpaceName : lrn (unicode)       [query,edit]
          Gets the loaded rendering space.  Used by file open, import, and reference to check for missing color spaces or
          transforms.
    
      - loadedViewTransformName : lvn  (unicode)       [query,edit]
          Gets the loaded view transform.  Used by file open, import, and reference to check for missing color spaces or
          transforms.
    
      - missingColorSpaceNodes : mcn   (bool)          [query,edit]
          Gets the names of the nodes that have color spaces not defined in the selected transform collection.
    
      - ocioRulesEnabled : ore         (bool)          [query,edit]
          Turn on or off the use of colorspace assignment rules from the OCIO library.
    
      - outputTarget : ott             (unicode)       [query,edit]
          Indicates to which output the outputTransformEnabled or the outputTransformName flags are to be applied. Valid values
          are rendereror playblast.
    
      - outputTransformEnabled : ote   (bool)          [query,edit]
          Turn on or off applying the output transform for out of viewport renders. If set, the output transform set in the
          preferences is used.
    
      - outputTransformName : otn      (unicode)       [query,edit]
          The output transform to be applied for out of viewport renders.  Disables output use view transform mode.
    
      - outputTransformNames : ots     (bool)          [query,edit]
          Returns the list of available output transforms.
    
      - outputUseViewTransform : ovt   (bool)          [query,edit]
          Turns use view transform mode on.  In this mode, the output transform is set to match the view transform.  To turn the
          mode off, set an output transform using the outputTransformName flag.
    
      - policyFileName : pfn           (unicode)       [query,edit]
          Set the policy file name
    
      - popupOnError : poe             (bool)          [query,edit]
          Turn on or off displaying a modal popup on error (as well as the normal script editor reporting of the error), for this
          invocation of the command.  Default is off.
    
      - renderingSpaceName : rsn       (unicode)       [query,edit]
          The color space to be used during rendering.  This is the source color space to the viewing transform, for color managed
          viewers and color managed UI controls, and the destination color space for color managed input pixels.
    
      - renderingSpaceNames : rss      (bool)          [query,edit]
          Returns the list of available rendering spaces.  Used to populate the color management preference UI popup.
    
      - restoreDefaults : rde          (bool)          [create,query,edit]
          Restore the color management settings to their default value.
    
      - viewTransformName : vtn        (unicode)       [query,edit]
          The view transform to be applied by color managed viewers and color managed UI controls.
    
      - viewTransformNames : vts       (bool)          [query,edit]
          Returns the list of available view transforms.  Used to populate the color management preference UI popup.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.colorManagementPrefs`
    """

    pass


def _getPymelType(arg, name):
    """
    Get the correct Pymel Type for an object that can be a MObject, PyNode or name of an existing Maya object,
    if no correct type is found returns DependNode by default.
    
    If the name of an existing object is passed, the name and MObject will be returned
    If a valid MObject is passed, the name will be returned as None
    If a PyNode instance is passed, its name and MObject will be returned
    """

    pass


def listFuture(*args, **kwargs):
    """
    Modifications:
      - returns an empty list when the result is None
      - added a much needed 'type' filter
      - added an 'exactType' filter (if both 'exactType' and 'type' are present, 'type' is ignored)
    
        :rtype: `DependNode` list
    """

    pass


def vnn(*args, **kwargs):
    """
    This command is used for operations that apply to a whole VNN runtime, for example Bifrost.  The Create Node window uses
    it to build its list of nodes.
    
    Flags:
      - flushProxies : fp              (unicode)       [create,query]
          Flush proxies for the named VNN runtime, for example Bifrost. This is a flag used for developers to ask a given runtime
          to release all of its proxy VNN nodes so that they can be re-created the next time they are requested.  This is used to
          verify that the VNN graph corresponds to the graph that is being virtualized, or proxied.  The maya node editor or any
          other UI that uses VNN should be closed before this called is made.  Failure to do so will result in that UI failure to
          recongnize changes made to the VNN graph, because the changes will be made on another set of proxies.
    
      - libraries : lib                (unicode)       [create,query]
          List of the libraries in runTime.
    
      - listPortTypes : lpt            (unicode)       [create,query]
          List all the possible port types for the given VNN runtime, for example Bifrost. The list of port types is not fixed and
          could grow as new definitions are added to the runtime.
    
      - nodes : nd                     (unicode, unicode) [create,query]
          List of the nodes from the runTime library. First argument is the name of the runtime, like Bifrost, second is the name
          of the library, obtained with -libraries
    
      - runTimes : rt                  (bool)          [create,query]
          List all the runTimes registered with VNN.                                 Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.vnn`
    """

    pass


def container(*args, **kwargs):
    """
    This command can be used to create and query container nodes. It is also used to perform operations on containers such
    as: add and remove nodes from the containerpublish attributes from nodes inside the containerreplace the connections and
    values from one container onto another oneremove a container without removing its member nodes
    
    Modifications:
      - returns a list of PyNode objects for flags: (query and (nodeList or connectionList))
      - returns a PyNode object for flags: (query and (findContainer or asset))
      - <lambda>(result) for flags: (query and bindAttr and not (publishName or publishAsParent or publishAsChild))
      - f(result) for flags: (query and unbindAttr and not (publishName or publishAsParent or publishAsChild))
    
    Flags:
      - addNode : an                   (<type 'unicode'>, ...) [create,edit]
          Specifies the list of nodes to add to container.
    
      - asset : a                      (<type 'unicode'>, ...) [query]
          When queried, if all the nodes in nodeList belong to the same container, returns container's name. Otherwise returns
          empty string. This flag is functionally equivalent to the findContainer flag.
    
      - assetMember : am               (unicode)       [query]
          Can be used during query in conjunction with the bindAttr flag to query for the only published attributes related to the
          specified node within the container.
    
      - bindAttr : ba                  (unicode, unicode) [query,edit]
          Bind a contained attribute to an unbound published name on the interface of the container; returns a list of bound
          published names. The first string specifies the node and attribute name to be bound in node.attrformat. The second
          string specifies the name of the unbound published name. In query mode, returns a string array of the published names
          and their corresponding attributes. The flag can also be used in query mode in conjunction with the -publishName,
          -publishAsParent, and -publishAsChild flags.
    
      - connectionList : cl            (bool)          [query]
          Returns a list of the exterior connections to the container node.
    
      - current : c                    (bool)          [create,query,edit]
          In create mode, specify that the newly created asset should be current. In edit mode, set the selected asset as current.
          In query, return the current asset.
    
      - fileName : fn                  (<type 'unicode'>, ...) [query]
          Used to query for the assets associated with a given file name.
    
      - findContainer : fc             (<type 'unicode'>, ...) [query]
          When queried, if all the nodes in nodeList belong to the same container, returns container's name. Otherwise returns
          empty string.
    
      - force : f                      (bool)          [create,edit]
          This flag can be used in conjunction with -addNode and -removeNode flags only. If specified with -addNode, nodes will be
          disconnected from their current containers before they are added to new one. If specified with -removeNode, nodes will
          be removed from all containers, instead of remaining in the parent container if being removed from a nested container.
    
      - includeHierarchyAbove : iha    (bool)          [create,edit]
          Used to specify that the parent hierarchy of the supplied node list should also be included in the container (or deleted
          from the container). Hierarchy inclusion will stop at nodes which are members of other containers.
    
      - includeHierarchyBelow : ihb    (bool)          [create,edit]
          Used to specify that the hierarchy below the supplied node list should also be included in the container (or delete from
          the container). Hierarchy inclusion will stop at nodes which are members of other containers.
    
      - includeNetwork : inc           (bool)          [create,edit]
          Used to specify that the node network connected to supplied node list should also be included in the container. Network
          traversal will stop at default nodes and nodes which are members of other containers.
    
      - includeNetworkDetails : ind    (unicode)       [create,edit]
          Used to specify specific parts of the network that should be included. Valid arguments to this flag are: channels, sdk,
          constraints, historyand expressions, inputs, outputs. The difference between this flag and the includeNetwork flag, is
          that it will include all connected nodes regardless of their type. Note that dag containers include their children, so
          they will always include constraint nodes that are parented beneath the selected objects, even when constraints are not
          specified as an input.
    
      - includeShaders : isd           (bool)          [create,edit]
          Used to specify that for any shapes included, their shaders will also be included in the container.
    
      - includeShapes : ish            (bool)          [create,edit]
          Used to specify that for any transforms selected, their direct child shapes will be included in the container (or
          deleted from the container). This flag is not necessary when includeHierarchyBelow is used since the child shapes and
          all other descendents will automatically be included.
    
      - includeTransform : it          (bool)          [create,edit]
          Used to specify that for any shapes selected, their parent transform will be included in the container (or deleted from
          the container). This flag is not necessary when includeHierarchyAbove is used since the parent transform and all of its
          parents will automatically be included.
    
      - isContainer : isc              (bool)          [query]
          Return true if the selected or specified node is a container node. If multiple containers are queried, only the state of
          the first will be returned.
    
      - name : n                       (unicode)       [create]
          Sets the name of the newly-created container.
    
      - nodeList : nl                  (bool)          [query]
          When queried, returns a list of nodes in container. The list will be sorted in the order they were added to the
          container. This will also display any reordering done with the reorderContainer command.
    
      - nodeNamePrefix : nnp           (bool)          [create,edit]
          Specifies that the name of published attributes should be of the form node_attr. Must be used with the
          -publishConnections/-pc flag.
    
      - parentContainer : par          (bool)          [query]
          Flag to query the parent container of a specified container.
    
      - preview : p                    (bool)          [create]
          This flag is valid in create mode only. It indicates that you do not want the container to be created, instead you want
          to preview its contents. When this flag is used, Maya will select the nodes that would be put in the container if you
          did create the container. For example you can see what would go into the container with -includeNetwork, then modify
          your selection as desired, and do a create container with the selected objects only.
    
      - publishAndBind : pb            (unicode, unicode) [edit]
          Publish the given name and bind the attribute to the given name. First string specifies the node and attribute name in
          node.attrformat. Second string specifies the name it should be published with.
    
      - publishAsChild : pac           (unicode, unicode) [query,edit]
          Publish contained node to the interface of the container to indicate it can be a child of external nodes. The second
          string is the name of the published node. In query mode, returns a string of the published names and the corresponding
          nodes. If -publishName flag is used in query mode, only returns the published names; if -bindAttr flag is used in query
          mode, only returns the name of the published nodes.
    
      - publishAsParent : pap          (unicode, unicode) [query,edit]
          Publish contained node to the interface of the container to indicate it can be a parent to external nodes. The second
          string is the name of the published node. In query mode, returns a string of array of the published names and the
          corresponding nodes. If -publishName flag is used in query mode, only returns the published names; if -bindAttr flag is
          used in query mode, only returns the name of the published nodes.
    
      - publishAsRoot : pro            (unicode, bool) [query,edit]
          Publish or unpublish a node as a root. The significance of root transform node is twofold. When container-centric
          selection is enabled, the root transform will be selected if a container node in the hierarchy below it is selected in
          the main scene view. Also, when exporting a container proxy, any published root transformation attributes such as
          translate, rotate or scale will be hooked up to attributes on a stand-in node. In query mode, returns the node that has
          been published as root.
    
      - publishAttr : pa               (unicode)       [query]
          In query mode, can only be used with the -publishName(-pn) flag, and takes an attribute as an argument; returns the
          published name of the attribute, if any.
    
      - publishConnections : pc        (bool)          [create,edit]
          Publish all connections from nodes inside the container to nodes outside the container.
    
      - publishName : pn               (unicode)       [query,edit]
          Publish a name to the interface of the container, and returns the actual name published to the interface.  In query
          mode, returns the published names for the container. If the -bindAttr flag is specified, returns only the names that are
          bound; if the -unbindAttr flag is specified, returns only the names that are not bound; if the
          -publishAsParent/-publishAsChild flags are specified, returns only names of published parents/children. if the
          -publishAttr is specified with an attribute argument in the node.attrformat, returns the published name for that
          attribute, if any.
    
      - removeContainer : rc           (bool)          [edit]
          Disconnects all the nodes from container and deletes container node.
    
      - removeNode : rn                (<type 'unicode'>, ...) [edit]
          Specifies the list of nodes to remove from container. If node is a member of a nested container, it will be added to the
          parent container. To remove from all containers completely, use the -force flag.
    
      - type : typ                     (unicode)       [create,query]
          By default, a container node will be created. Alternatively, the type flag can be used to indicate that a different type
          of container should be created. At the present time, the only other valid type of container node is dagContainer.
    
      - unbindAndUnpublish : ubp       (unicode)       [edit]
          Unbind the given attribute (in node.attrformat) and unpublish its associated name. Unbinding a compound may trigger
          unbinds of its compound parents/children. So the advantage of using this one flag is that it will automatically
          unpublish the names associated with these automatic unbinds.
    
      - unbindAttr : ua                (unicode, unicode) [query,edit]
          Unbind a published attribute from its published name on the interface of the container, leaving an unbound published
          name on the interface of the container; returns a list of unbound published names. The first string specifies the node
          and attribute name to be unbound in node.attrformat, and the second string specifies the name of the bound published
          name. In query mode, can only be used with the -publishName, -publishAsParent and -publishAsChild flags.
    
      - unbindChild : unc              (unicode)       [edit]
          Unbind the node published as child, but do not remove its published name from the interface of the container.
    
      - unbindParent : unp             (unicode)       [edit]
          Unbind the node published as parent, but do not remove its published name from the interface of the container.
    
      - unpublishChild : upc           (unicode)       [edit]
          Unpublish node published as child from the interface of the container
    
      - unpublishName : un             (unicode)       [edit]
          Unpublish an unbound name from the interface of the container.
    
      - unpublishParent : upp          (unicode)       [edit]
          Unpublish node published as parent from the interface of the container
    
      - unsortedOrder : uso            (bool)          [query]
          This flag has no effect on the operation of the container command (OBSOLETE).                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.container`
    """

    pass


def encodeString(*args, **kwargs):
    """
    This action will take a string and encode any character that would need to be escaped before being sent to some other
    command. Such characters include:double quotesnewlinestabs
    
    
    Derived from mel command `maya.cmds.encodeString`
    """

    pass


def webView(*args, **kwargs):
    """
    This command allows the user to bring up a web page view
    
    Flags:
      - urlAddress : url               (unicode)       [create]
          Bring up webView on given URL
    
      - windowHeight : wh              (int)           [create]
          Set the window height
    
      - windowWidth : ww               (int)           [create]
          Set the window width                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.webView`
    """

    pass


def objectCenter(*args, **kwargs):
    """
    This command returns the coordinates of the center of the bounding box of the specified object. If one coordinate only
    is specified, it will be returned as a float. If no coordinates are specified, an array of floats is returned,
    containing x, y, and z. If you specify multiple coordinates, only one will be returned.
    
    Flags:
      - gl : gl                        (bool)          [create]
          Return positional values in global coordinates (default).
    
      - local : l                      (bool)          [create]
          Return positional values in local coordinates.
    
      - x : x                          (bool)          [create]
          Return X value only
    
      - y : y                          (bool)          [create]
          Return Y value only
    
      - z : z                          (bool)          [create]
          Return Z value only                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.objectCenter`
    """

    pass


def resetTool(*args, **kwargs):
    """
    This command resets a tool back to its factory settings
    
    
    Derived from mel command `maya.cmds.resetTool`
    """

    pass


def deleteAttrPattern(*args, **kwargs):
    """
    After a while the list of attribute patterns could become cluttered. This command provides a way to remove patterns from
    memory so that only the ones of interest will show.
    
    Flags:
      - allPatterns : all              (bool)          [create]
          If specified it means delete all known attribute patterns.
    
      - patternName : pn               (unicode)       [create]
          The name of the pattern to be deleted.
    
      - patternType : pt               (unicode)       [create]
          Delete all patterns of the given type.                             Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.deleteAttrPattern`
    """

    pass


def reorder(*args, **kwargs):
    """
    This command reorders (moves) objects relative to their siblings. For relative moves, both positive and negative numbers
    may be specified.  Positive numbers move the object forward and negative numbers move the object backward amoung its
    siblings. When an object is at the end (beginning) of the list of siblings, a relative move of 1 (-1) will put the
    object at the beginning (end) of the list of siblings.  That is, relative moves will wrap if necessary. If a shape is
    specified and it is the only child then its parent will be reordered.
    
    Flags:
      - back : b                       (bool)          [create]
          Move object(s) to back of sibling list.
    
      - front : f                      (bool)          [create]
          Move object(s) to front of sibling list.
    
      - relative : r                   (int)           [create]
          Move object(s) relative to other siblings.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.reorder`
    """

    pass


def deleteAttr(*args, **kwargs):
    """
    This command is used to delete a dynamic attribute from a node or nodes. The attribute can be specified by using either
    the long or short name. Only one dynamic attribute can be deleted at a time. Static attributes cannot be deleted.
    Children of a compound attribute cannot be deleted. You must delete the complete compound attribute. This command has no
    edit capabilities. The only query ability is to list all the dynamic attributes of a node. In query mode, return type is
    based on queried flag.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          Specify either the long or short name of the attribute.
    
      - name : n                       (unicode)       [create]
          The name of the node.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.deleteAttr`
    """

    pass


def xform(*args, **kwargs):
    """
    This command can be used query/set any element in a transformation node. It can also be used to query some values that
    cannot be set directly such as the transformation matrix or the bounding box. It can also set both pivot points to
    convenient values. All values are specified in transformation coordinates. (attribute-space) In addition, the attributes
    are applied/returned in the order in which they appear in the flags section. (which corresponds to the order they appear
    in the transformation matrix as given below) See also:move, rotate, scale where: [sp] = |  1      0        0       0 | =
    scale pivot matrix |  0      1        0       0 | |  0      0        1       0 | | -spx   -spy     -spz     1 | [s]  = |
    sx     0        0       0 | = scale matrix |  0      sy       0       0 | |  0      0        sz      0 | |  0      0
    0       1 | [sh] = |  1      0        0       0 | = shear matrix |  xy     1        0       0 | |  xz     yz       1
    0 | |  0      0        0       1 | -1 [sp] = |  1       0       0       0 | = scale pivot inverse matrix |  0       1
    0       0 | |  0       0       1       0 | |  spx     spy     spz     1 | [st] = |  1       0       0       0 | = scale
    translate matrix |  0       1       0       0 | |  0       0       1       0 | |  stx     sty     stz     1 | [rp] = |
    1       0       0       0 | = rotate pivot matrix |  0       1       0       0 | |  0       0       1       0 | | -rpx
    -rpy    -rpz     1 | [ar] = |  \*       \*       \*       0 | = axis rotation matrix |  \*       \*       \*       0 |
    (composite rotation, |  \*       \*       \*       0 |    see [rx], [ry], [rz] |  0       0       0       1 |    below
    for details) [rx] = |  1       0       0       0 | = rotate X matrix |  0       cos(x)  sin(x)  0 | |  0      -sin(x)
    cos(x)  0 | |  0       0       0       1 | [ry] = |  cos(y)  0      -sin(y)  0 | = rotate Y matrix |  0       1       0
    0 | |  sin(y)  0       cos(y)  0 | |  0       0       0       1 | [rz] = |  cos(z)  sin(z)  0       0 | = rotate Z
    matrix | -sin(z)  cos(z)  0       0 | |  0       0       1       0 | |  0       0       0       1 | -1 [rp] = |  1
    0       0       0 | = rotate pivot matrix |  0       1       0       0 | |  0       0       1       0 | |  rpx     rpy
    rpz     1 | [rt] = |  1       0       0       0 | = rotate translate matrix |  0       1       0       0 | |  0       0
    1       0 | |  rtx     rty     rtz     1 | [t]  = |  1       0       0       0 | = translation matrix |  0       1
    0       0 | |  0       0       1       0 | |  tx      ty      tz      1 | In query mode, return type is based on queried
    flag.
    
    Flags:
      - absolute : a                   (bool)          [create]
          perform absolute transformation (default)
    
      - boundingBox : bb               (bool)          [query]
          Returns the bounding box of an object. The values returned are in the following order: xmin ymin zmin xmax ymax zmax.
    
      - boundingBoxInvisible : bbi     (bool)          [query]
          Returns the bounding box of an object. This includes the bounding boxes of all invisible children which are not included
          using the boundingBox flag. The values returned are in following order: xmin ymin zmin xmax ymax zmax.
    
      - centerPivots : cp              (bool)          [create]
          Set pivot points to the center of the object's bounding box. (see -p flag)
    
      - centerPivotsOnComponents : cpc (bool)          [create]
          Set pivot points to the center of the component's bounding box. (see -p flag)
    
      - deletePriorHistory : dph       (bool)          [create]
          If true then delete the construction history before the operation is performed.
    
      - euler : eu                     (bool)          [create]
          modifer for -relative flag that specifies rotation values should be added to current XYZ rotation values.
    
      - matrix : m                     (float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float) [create,query]
          Sets/returns the composite transformation matrix. \*Note\* the matrix is represented by 16 double arguments that are
          specified in row order.
    
      - objectSpace : os               (bool)          [create,query]
          treat values as object-space transformation values (only works for pivots, translations, rotation, rotation axis,
          matrix, and bounding box flags)
    
      - pivots : piv                   (float, float, float) [create,query]
          convenience method that changes both the rotate and scale pivots simultaneously. (see -rp -sp flags for more info)
    
      - preserve : p                   (bool)          [create]
          preserve overall transformation. used to prevent object from jumpingwhen changing pivots or rotation order. the default
          value is true. (used with -sp, -rp, -roo, -cp, -ra)
    
      - preserveUV : puv               (bool)          [create]
          When true, UV values on rotated components are projected across the rotation in 3d space. For small edits, this will
          freeze the world space texture mapping on the object. When false, the UV values will not change for a selected vertices.
          Default is false.
    
      - reflection : rfl               (bool)          [create]
          To move the corresponding symmetric components also.
    
      - reflectionAboutBBox : rab      (bool)          [create]
          Sets the position of the reflection axis  at the geometry bounding box
    
      - reflectionAboutOrigin : rao    (bool)          [create]
          Sets the position of the reflection axis  at the origin
    
      - reflectionAboutX : rax         (bool)          [create]
          Specifies the X=0 as reflection plane
    
      - reflectionAboutY : ray         (bool)          [create]
          Specifies the Y=0 as reflection plane
    
      - reflectionAboutZ : raz         (bool)          [create]
          Specifies the Z=0 as reflection plane
    
      - reflectionTolerance : rft      (float)         [create]
          Specifies the tolerance to findout the corresponding reflected components
    
      - relative : r                   (bool)          [create]
          perform relative transformation
    
      - rotateAxis : ra                (float, float, float) [create,query]
          rotation axis orientation (when used with the -p flag the overall rotation is preserved by modifying the rotation to
          compensate for the axis rotation)
    
      - rotateOrder : roo              (unicode)       [create,query]
          rotation order (when used with the -p flag the overall rotation is preserved by modifying the local rotation to be
          quivalent to the old one) Valid values for this flag are xyz | yzx | zxy | xzy | yxz | zyx
    
      - rotatePivot : rp               (float, float, float) [create,query]
          rotate pivot point transformation (when used with the -p flag the overall transformation is preserved by modifying the
          rotation translation)
    
      - rotateTranslation : rt         (float, float, float) [create,query]
          rotation translation
    
      - rotation : ro                  (float, float, float) [create,query]
          rotation transformation
    
      - scale : s                      (float, float, float) [create,query]
          scale transformation
    
      - scalePivot : sp                (float, float, float) [create,query]
          scale pivot point transformation (when used with the -p flag the overall transformation is preserved by modifying the
          scale translation)
    
      - scaleTranslation : st          (float, float, float) [create,query]
          scale translation
    
      - shear : sh                     (float, float, float) [create,query]
          shear transformation. The values represent the shear xy,xz,yz
    
      - translation : t                (float, float, float) [create,query]
          translation
    
      - worldSpace : ws                (bool)          [create,query]
          (works for pivots, translations, rotation, rotation axis, matrix, and bounding box flags). Note that, when querying the
          scale, that this calculation is cumulative and is only valid if there are all uniform scales and no rotation. In a
          hierarchy with non-uniform scale and rotation, this value may not correspond entirely with the perceived global scale.
    
      - worldSpaceDistance : wd        (bool)          [create,query]
          Values for -sp, -rp, -st, -rt, -t, -piv flags are treated as world space distances to move along the local axis. (where
          the local axis depends on whether the command is operating in local-space or object-space. This flag has no effect for
          world space.
    
      - zeroTransformPivots : ztp      (bool)          [create]
          reset pivot points and pivot translations without changing the overall matrix by applying these values into the
          translation channel.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.xform`
    """

    pass


def shapeCompare(*args, **kwargs):
    """
    Compares two shapes. If no shapes are specified in the command line, then the shapes from the active list are used.
    
    
    Derived from mel command `maya.cmds.shapeCompare`
    """

    pass


def assembly(*args, **kwargs):
    """
    Command to register assemblies for the scene assembly framework, to create them, and to edit and query them. Assembly
    nodes are DAG nodes, and are therefore shown in the various DAG editors (Outliner, Hypergraph, Node Editor). At assembly
    creation time, the node name defaults to the node type name. The assembly command can create any node that is derived
    from the assembly node base class.  It also acts as a registry of these types, so that various scripting callbacks can
    be defined and registered with the assembly command.  These callbacks are invoked by Maya during operations on assembly
    nodes, and can be used to customize behavior. In query mode, return type is based on queried flag.
    
    Flags:
      - active : a                     (unicode)       [query,edit]
          Set the active representation by name, or query the name of the active representation. Edit mode can be applied to more
          than one assembly. Query mode will return a single string when only a single assembly is specified, and will return an
          array of strings when multiple assemblies are specified. Using an empty string as name means to inactivate the currently
          active representation.
    
      - activeLabel : al               (unicode)       [query,edit]
          Set the active representation by label, or query the label of the active representation. Edit mode can be applied to
          more than one assembly. Query mode will return a single string when only a single assembly is specified, and will return
          an array of strings when multiple assemblies are specified.
    
      - canCreate : cc                 (unicode)       [query]
          Query the representation types the specific assembly can create.
    
      - createOptionBoxProc : cob      (script)        [query,edit]
          Set or query the option box menu procedure for a specific assembly type. The assembly type will be the default type,
          unless the -type flag is used to specify an explicit assembly type.
    
      - createRepresentation : cr      (unicode)       [edit]
          Create and add a specific type of representation for an assembly. If the representation type needs additional
          parameters, they must be specified using the inputflag. For example, the Maya scene assembly reference implementation
          Cache and Scene representations need an input file.
    
      - defaultType : dt               (unicode)       [query,edit]
          Set or query the default type of assembly.  When the assembly command is used to perform an operation on an assembly
          type rather than on an assembly object, it will be performed on the default type, unless the -type flag is used to
          specify an explicit assembly type.
    
      - deleteRepresentation : dr      (unicode)       [edit]
          Delete a specific representation from an assembly.
    
      - deregister : d                 (unicode)       [edit]
          Deregister a registered assembly type. If the deregistered type is the default type, the default type will be set to the
          empty string.
    
      - input : input                  (unicode)       [edit]
          Specify the additional parameters of representation creation procedure when creating a representation. This flag must be
          used with createRepresentation flag.
    
      - isAType : isa                  (unicode)       [query]
          Query whether the given object is of an assembly type.
    
      - isTrackingMemberEdits : ite    (unicode)       [query]
          Query whether the given object is tracking member edits.
    
      - label : lbl                    (unicode)       [query,edit]
          Set or query the label for an assembly type. Assembly type is specified with flag type. If no type specified, the
          default type is used.
    
      - listRepTypes : lrt             (bool)          [query]
          Query the supported representation types for a given assembly type.  The assembly type will be the default type, unless
          the -type flag is used to specify an explicit assembly type.
    
      - listRepTypesProc : lrp         (script)        [query,edit]
          Set or query the procedure that provides the representation type list which an assembly type supports.  This procedure
          takes no argument, and returns a string array of representation types that represents the full set of representation
          types this assembly type can create.  The assembly type for which this procedure applies will be the default type,
          unless the type flag is used to specify an explicit assembly type.
    
      - listRepresentations : lr       (bool)          [query]
          Query the created representations list for a specific assembly.  The -repType flag can be used to filter the list and
          return representations for a single representation type.  If the -repType flag is not used, all created representations
          will be returned.
    
      - listTypes : lt                 (bool)          [query]
          Query the supported assembly types.
    
      - name : n                       (unicode)       [create]
          Specify the name of the assembly when creating it.
    
      - newRepLabel : nrl              (unicode)       [edit]
          Specify the representation label to set on representation label edit.
    
      - postCreateUIProc : aoc         (script)        [query,edit]
          Set or query the UI post-creation procedure for a given assembly type. This procedure will be invoked by Maya
          immediately after an assembly of the specified type is created from the UI, but not through scripting.  It can be used
          to invoke a dialog, to obtain and set initial parameters on a newly-created assembly.  The assembly type will be the
          default type, unless the -type flag is used to specify an explicit assembly type.
    
      - proc : prc                     (script)        [edit]
          Specify the procedure when setting the representation UI post- or pre-creation procedure, for a given assembly type.
          The assembly type will be the default type, unless the -type flag is used to specify an explicit assembly type.
    
      - renameRepresentation : rnr     (unicode)       [edit]
          Renames the representation that is the argument to this flag.  The repName flag must be used to provide the new name.
    
      - repLabel : rl                  (unicode)       [query,edit]
          Query or edit the label of the representation that is the argument to this flag, for a given assembly.  In both query
          and edit modes, the -repLabel flag specifies the name of the representation.  In edit mode, the -newRepLabel flag must
          be used to specify the new representation label.
    
      - repName : rnm                  (unicode)       [edit]
          Specify the representation name to set on representation creation or rename. This flag is optional with the
          createRepresentation flag: if omitted, the assembly will name the representation.  It is mandatory with the
          renameRepresentation flag.
    
      - repNamespace : rns             (unicode)       [query]
          Query the representation namespace of this assembly node. The value returned is used by Maya for creating the namespace
          where nodes created by the activation of a representation will be added. If a name clash occurs when the namespace is
          added to its parent namespace, Maya will update repNamespace with the new name. Two namespaces are involved when dealing
          with an assembly node: the namespace of the assembly node itself (which this flag does not affect or query), and the
          namespace of its representations. The representation namespace is a child of its assembly node's namespace. The assembly
          node's namespace is set by its containing assembly, if it is nested, or by the top-level file. Either the assembly
          node's namespace, or the representation namespace, or both, can be the empty string. It should be noted that if the
          assembly node is nested, the assembly node's namespace will be (by virtue of its nesting) the representation namespace
          of its containing assembly.
    
      - repPostCreateUIProc : poc      (unicode)       [query,edit]
          Set or query the UI post-creation procedure for a specific representation type, and for a specific assembly type.  This
          procedure takes two arguments, the first the DAG path to the assembly, and the second the name of the representation.
          It returns no value.  It will be invoked by Maya immediately after a representation of the specified type is created
          from the UI, but not through scripting.  It can be used to invoke a dialog, to obtain and set initial parameters on a
          newly-created representation.  The representation type is the argument of this flag. The -proc flag must be used to
          specify the procedure name.  The assembly type will be the default type, unless the -type flag is used to specify an
          explicit assembly type.
    
      - repPreCreateUIProc : pec       (unicode)       [query,edit]
          Set or query the UI pre-creation procedure for a specific representation type, and for a specific assembly type.  This
          procedure takes no argument, and returns a string that is passed as an argument to the -input flag when Maya invokes the
          assembly command with the -createRepresentation flag. The representation pre-creation procedure is invoked by Maya
          immediately before creating a representation of the specified type from the UI, but not through scripting.  It can be
          used to invoke a dialog, to obtain the creation argument for a new representation.  The representation type is the
          argument of this flag.  The -proc flag must be used to specify the procedure name.  The assembly type will be the
          default type, unless the -type flag is used to specify an explicit assembly type.
    
      - repType : rt                   (unicode)       [query]
          Specify a representation type to use as a filter for the -listRepresentations query.  The representation type is the
          argument to this flag.
    
      - repTypeLabel : rtl             (unicode)       [query]
          Query the label of the specific representation type.
    
      - repTypeLabelProc : rtp         (script)        [query,edit]
          Set or query the procedure that provides the representation type label, for a given assembly type.  The procedure takes
          the representation type as its sole argument, and returns a localized representation type label. The assembly type for
          which this procedure applies will be the default type, unless the -type flag is used to specify an explicit assembly
          type.
    
      - type : typ                     (unicode)       [create,query,edit]
          Set or query properties for the specified registered assembly type. Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.assembly`
    """

    pass


def createAttrPatterns(*args, **kwargs):
    """
    Create a new instance of an attribute pattern given a pattern type (e.g. XML) and a string or data file containing the
    description of the attribute tree in the pattern's format.
    
    Flags:
      - patternDefinition : pd         (unicode)       [create]
          Hardcoded string containing the pattern definition, for simpler formats that don't really need a separate file for
          definition.
    
      - patternFile : pf               (unicode)       [create]
          File where the pattern information can be found
    
      - patternType : pt               (unicode)       [create]
          Name of the pattern definition type to use in creating this instance of the pattern.                               Flag
          can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.createAttrPatterns`
    """

    pass


def _objectError(objectName):
    pass


def showHidden(*args, **kwargs):
    """
    The showHiddencommand is used to make invisible objects visible.  If no flags are specified, only the objects given to
    the command will be made visible. If a parent of an object is invisible, the object will still be invisible.
    Invisibility is inherited. To ensure the object becomes visible, use the -a/above flag. This forces all invisible
    ancestors of the object(s) to be visible. If the -b/below flag is used, any invisible objects below the object will be
    made visible.  To make all objects visible, use the -all/allObjects flag. See also:hide
    
    Flags:
      - above : a                      (bool)          [create]
          Make objects and all their invisible ancestors visible.
    
      - allObjects : all               (bool)          [create]
          Make all invisible objects visible.
    
      - below : b                      (bool)          [create]
          Make objects and all their invisible descendants visible.
    
      - lastHidden : lh                (bool)          [create]
          Show everything that was hidden with the last hide command.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.showHidden`
    """

    pass


def relationship(*args, **kwargs):
    """
    This is primarily for use with file IO. Rather than write out the specific attributes/connections required to maintain a
    relationship, a description of the related nodes/plugs is written instead. The relationship must have an owner node, and
    have a specific type. During file read, maya will make the connections and/or set the data necessary to represent the
    realtionship in the dependency graph.            In query mode, return type is based on queried flag.
    
    Flags:
      - b : b                          (bool)          [create,query,edit]
          Break the specified relationship instead of creating it
    
      - relationshipData : rd          (unicode)       [create,query,edit]
          Provide relationship data to be used when creating the relationship.                               Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.relationship`
    """

    pass


def pixelMove(*args, **kwargs):
    """
    The pixelMove command moves objects by what appears as pixel units based on the current view. It takes two integer
    arguments which specify the direction in screen space an object should appear to move. The vector between the center
    pixel of the view and the specified offset is mapped to some world space vector which defines the relative amount to
    move the selected objects. The mapping is dependent upon the view.
    
    
    Derived from mel command `maya.cmds.pixelMove`
    """

    pass


def nodeCast(*args, **kwargs):
    """
    Given two nodes, a source node of type A and a target node of type B, where type A is either type B or a sub-type of B,
    this command will replace the target node with the source node. That is, all node connections, DAG hierarchy and
    attribute values on the target node will be removed from the target node and placed on the source node. This operation
    will fail if either object is referenced, locked or if the nodes do not share a common sub-type. This operation is
    atomic. If the given parameters fail, then the source and target nodes will remain in their initial state prior to
    execution of the command. IMPORTANT: the command will currently ignore instance connections and instance objects.  It
    will also ignore reference nodes.
    
    Flags:
      - copyDynamicAttrs : cda         (bool)          [create]
          If the target node contains any dynamic attributes that are not defined on the source node, then create identical
          dynamic attricutes on the source node and copy the values and connections from the target node into them.
    
      - disableAPICallbacks : dsa      (bool)          [create]
          add comment
    
      - disableScriptJobCallbacks : dsj (bool)          [create]
          add comment
    
      - disconnectUnmatchedAttrs : dua (bool)          [create]
          If the node that is being swapped out has any connections that do not exist on the target node, then indicate if the
          connection should be disconnected. By default these connections are not removed because they cannot be restored if the
          target node is swapped back with the source node.
    
      - force : f                      (bool)          [create]
          Forces the command to do the node cast operation even if the nodes do not share a common base object. When this flag is
          specified the command will try to do the best possible attribute matching when swapping the command.  It is
          notrecommended to use the '-swapValues/sv' flag with this flag.
    
      - swapNames : sn                 (bool)          [create]
          Swap the names of the nodes. By default names are not swapped.
    
      - swapValues : sv                (bool)          [create]
          Indicates if the commands should exchange attributes on the common attributes between the two nodes.  For example, if
          the nodes are the same base type as a transform node, then rotate, scale, translate values would be copied over.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.nodeCast`
    """

    pass


def group(*args, **kwargs):
    """
    This command groups the specified objects under a new group and returns the name of the new group. If the -em flag is
    specified, then an empty group (with no objects) is created. If the -w flag is specified then the new group is placed
    under the world, otherwise if -p is specified it is placed under the specified node. If neither -w or -p is specified
    the new group is placed under the lowest common group they have in common. (or the world if no such group exists) If an
    object is grouped with another object that has the same name then one of the objects will be renamed by this command.
    
    Modifications
      - if no objects are passed or selected, the empty flag is automatically set
    Maya Bug Fix:
      - corrected to return a unique name
    
    Flags:
      - absolute : a                   (bool)          [create]
          preserve existing world object transformations (overall object transformation is preserved by modifying the objects
          local transformation) [default]
    
      - empty : em                     (bool)          [create]
          create an empty group (with no objects in it)
    
      - name : n                       (unicode)       [create]
          Assign given name to new group node.
    
      - parent : p                     (unicode)       [create]
          put the new group under the given parent
    
      - relative : r                   (bool)          [create]
          preserve existing local object transformations (relative to the new group node)
    
      - useAsGroup : uag               (unicode)       [create]
          Use the specified node as the group node. The specified node must be derived from the transform node and must not have
          any existing parents or children.
    
      - world : w                      (bool)          [create]
          put the new group under the world                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.group`
    """

    pass


def containerTemplate(*args, **kwargs):
    """
    A container template is a description of a container's published interface. This command provides the ability to create
    and save a template file for a container or load an existing template file.  Once a template exists, the user can query
    the template information.                In query mode, return type is based on queried flag.
    
    Flags:
      - addBindingSet : abs            (unicode)       [create,edit]
          This argument is used to add a new binding set with the given name to a template. A default binding set will be created.
          If the binding set already exists, the force flag must be used to replace the existing binding set. When used with the
          fromContainer option, default bindings will be entered based on the current bindings of the designated container. When
          used without a reference container, the binding set will be made with placeholder entries. The template must be saved
          before the new binding set is permanently stored with the template file.
    
      - addNames : an                  (bool)          [edit]
          In edit mode, when used with the fromContainer flag, any published name on the container not present as an attribute on
          the template will be added to the template.
    
      - addView : av                   (unicode)       [create,edit]
          This argument is used to add a new view with the given name to a template. By default a view containing a flat list of
          all template attributes will be created.  The layoutMode flag provides more layout options. The template must be saved
          before the new view is permanently stored with the template file.
    
      - allKeyable : ak                (bool)          [create,edit]
          Used when the fromSelection flag is true and fromContainer is false. If true we will use all keyable attributes to
          define the template or the view, if false we use the attributes passed in with the attribute flag.
    
      - attribute : at                 (unicode)       [create,edit]
          If fromSelection is true and allKeyable is false, this attribute name will be used to create an attribute item in the
          template file.
    
      - attributeList : al             (unicode)       [create,query,edit]
          Used in query mode, returns a list of attributes contained in the template definition.
    
      - baseName : bn                  (unicode)       [create,query]
          Used in query mode, returns the base name of the template. The basename is the template name with any package qualifiers
          stripped off.
    
      - bindingSetList : bsl           (unicode)       [create,query]
          Used in query mode, returns a list of all binding sets defined on the template.
    
      - childAnchor : can              (bool)          [create,query]
          This flag can be optionally specified when querying the publishedNodeList. The resulting list will contain only
          childAnchor published nodes.
    
      - delete : d                     (bool)          [create]
          Delete the specified template and its file. All objects that are associated with this template or contained in the same
          template file will be deleted. To simply unload a template without permanently deleting its file, use unload instead.
    
      - exists : ex                    (bool)          [query]
          Returns true or false depending upon whether the specified template exists. When used with the matchFile argument, the
          query will return true if the template exists and the filename it was loaded from matches the filename given.
    
      - expandCompounds : ec           (bool)          [create,edit]
          This argument is used to determine how compound parent attributes and their children will be added to generated views
          when both are published to the container. When true, the compound parent and all compound child attributes published to
          the container will be included in the view. When false, only the parent attribute is included in the view. Note: if only
          the child attributes are published and not the parent, the children will be included in the view, this flag is only used
          in the situation where both parent and child attributes are published to the container. The default value is false.
    
      - fileName : fn                  (unicode)       [create,query]
          Specifies the filename associated with the template.  This argument can be used in conjunction with load, save or query
          modes. If no filename is associated with a template, a default file name based on the template name will be used.  It is
          recommended but not required that the filename and template name correspond.
    
      - force : f                      (bool)          [create]
          This flag is used with some actions to allow them to proceed with an overwrite or destructive operation. When used with
          load, it will allow an existing template to be reloaded from a file.  When used in create mode, it will allow an
          existing template to be recreated (for example when using fromContainer argument to regenerate a template).
    
      - fromContainer : fc             (unicode)       [create]
          This argument is used in create or edit mode to specify a container node to be used for generating the template
          contents. In template creation mode, the template definition will be created based on the list of published attributes
          in the specified container. In edit mode, when used with the addNames flag or with no other flag, any published name on
          the container not present as an attribute on the template will be added to the template. This flag is also used in
          conjunction with flags such as addView.
    
      - fromSelection : fs             (bool)          [create,edit]
          If true, we will use the active selection list to create the template or the view. If allKeyable is also true then we
          will create the template from all keyable attributes in the selection, otherwise we will create the template using the
          attributes specified with the attribute flag.
    
      - layoutMode : lm                (int)           [create]
          This argument is used to specify the layout mode when creating a view. Values correspond as follows: 0: layout in flat
          list (default when not creating view from container) 1: layout grouped by node (default if creating view from container)
          The fromContainer or fromSelection argument is required to provide the reference container or selection for layout modes
          that require node information.  Note that views can only refer to defined template attributes. This means that when
          using the fromContainer or from Selection flag to add a view to an existing template, only attributes that are defined
          on both the template and the container or the current selection will be included in the view (i.e. published attributes
          on the container that are not defined in the template will be ignored).
    
      - load : l                       (bool)          []
          Load an existing template from a file. If a filename is specified for the template, the entire file (and all templates
          in it) will be loaded. If no file is specified, a default filename will be assumed, based on the template name.
    
      - matchFile : mf                 (unicode)       [query]
          Used in query mode in conjunction with other flags this flag specifies an optional file name that is to be matched as
          part of the query operation.
    
      - matchName : mn                 (unicode)       [query]
          Used in query mode in conjunction with other flags this flag specifies an optional template name that is to be matched
          as part of the query operation. The base template name is used for matching, any template with the same basename will be
          matched even across different packages.
    
      - parentAnchor : pan             (bool)          [create,query]
          This flag can be optionally specified when querying the publishedNodeList. The resulting list will contain only
          parentAnchor published nodes.
    
      - publishedNodeList : pnl        (unicode)       [create,query,edit]
          Used in query mode, returns a list of published nodes contained in the template definition. By default all published
          nodes on the template will be returned. The list of published nodes can be limited to only include certain types of
          published nodes using one of the childAnchor, parentAnchor or rootTransform flags. If an optional flag is are specified,
          only nodes of the specified type will be returned.
    
      - removeBindingSet : rbs         (unicode)       [create,edit]
          This argument is used to remove the named binding set from the template. The template must be saved before the binding
          set is permanently removed from the template file.
    
      - removeView : rv                (unicode)       [create,edit]
          This argument is used to remove the named view from the template. The template must be saved before the view is
          permanently removed from the template file.
    
      - rootTransform : rtn            (bool)          [create,query]
          This flag can be optionally specified when querying the publishedNodeList. The resulting list will contain only
          rootTransform published nodes.
    
      - save : s                       (bool)          [create]
          Save the specified template to a file. If a filename is specified for the template, the entire file (and all templates
          associated with it) will be saved. If no file name is specified, a default filename will be assumed, based on the
          template name.
    
      - searchPath : sp                (unicode)       [query,edit]
          The template searchPath is an ordered list of all locations that are being searched to locate template files (first
          location searched to last location searched). The template search path setting is stored in the current workspace and
          can also be set and queried as the file rule entry for 'templates' (see the workspace command for more information). In
          edit mode, this flag allows the search path setting to be customized. When setting the search path value, the list
          should conform to a path list format expected on the current platform.  This means that paths should be separated by a
          semicolon (;) on Windows and a colon (:) on Linux and MacOSX. Environment variables can also be used. Additional built-
          in paths may be added automatically by maya to the customized settings. In query mode, this flag returns the current
          contents of the search path; all paths, both customized and built-in, will be included in the query return value.
    
      - silent : si                    (bool)          [create,query,edit]
          Silent mode will suppress any error or warning messages that would normally be reported from the command execution.  The
          return values are unaffected.
    
      - templateList : tl              (unicode)       [query]
          Used in query mode, returns a list of all loaded templates. This query can be used with optional matchFile and matchName
          flags. When used with the matchFile flag, the list of templates will be restricted to those associated with the
          specified file.  When used with the matchName flag, the list of templates will be restricted to those matching the
          specified template name.
    
      - unload : u                     (bool)          [create]
          Unload the specified template.  This action will not delete the associated template file if one exists, it merely
          removes the template definition from the current session.
    
      - updateBindingSet : ubs         (unicode)       [create,edit]
          This argument is used to update an existing binding set with new bindings. When used with the fromContainer argument
          binding set entries with be replaced or merged in the binding set based on the bindings of the designated container. If
          the force flag is used, existing entries in the binding set are replaced with new values. When force is not used, only
          new entries are merged into the binding set, any existing entries will be left as-is. When used without a reference
          container, the binding set will be updated with placeholder entries. The template must be saved before the new binding
          set is permanently stored with the template file.
    
      - useHierarchy : uh              (bool)          [create,edit]
          If true, and the fromSelection flag is set, the selection list will expand to include it's hierarchy also.
    
      - viewList : vl                  (unicode)       [create,query]
          Used in query mode, returns a list of all views defined on the template.                                   Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.containerTemplate`
    """

    pass


def removeMultiInstance(*args, **kwargs):
    """
    Removes a particular instance of a multiElement. This is only useful for input attributes since outputs will get
    regenerated the next time the node gets executed. This command will remove the instance and optionally break all
    incoming and outgoing connections to that instance. If the connections are not broken (with the -b true) flag, then the
    command will fail if connections exist.
    
    Flags:
      - b : b                          (bool)          [create]
          If the argument is true, all connections to the attribute will be broken before the element is removed. If false, then
          the command will fail if the element is connected.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.removeMultiInstance`
    """

    pass


def _getPymelTypeFromObject(obj, name):
    pass


def _pathFromMObj(mObj, fullPath=False):
    """
    Return a unique path to an mObject
    """

    pass


def selectPref(*args, **kwargs):
    """
    This command controls state variables used to selection UI behavior.
    
    Flags:
      - affectsActive : aa             (bool)          [create,query]
          Set affects-active toggle which when on causes the active list to be affected when changing between object and component
          selection mode.
    
      - allowHiliteSelection : ahs     (bool)          [create,query]
          When in component selection mode, allow selection of objects for editing.  If an object is selected for editing, it
          appears in the hilite color and its selectable components are automatically displayed.
    
      - autoSelectContainer : asc      (bool)          [query]
          When enabled, with container centric selection also on, whenever the root transform is selected in the viewport, the
          container node will automatically be selected as well.
    
      - autoUseDepth : aud             (bool)          [query]
          When enabled, useDepth and paintSelectWithDepth will be automatically enabled in shaded display mode and disabled in
          wireframe display mode.
    
      - clickBoxSize : cbs             (int)           [create,query]
          When click selecting, this value defines the size of square picking region surrounding the cursor. The size of the
          square is twice the specified value. That is, the value defines the amount of space on all four sides of the cursor
          position. The size must be positive.
    
      - clickDrag : cld                (bool)          [create,query]
          Set click/drag selection interaction on/off
    
      - containerCentricSelection : ccs (bool)          [query]
          When enabled, selecting any DAG node in a container in the viewport will select the container's root transform if there
          is one.  If there is no root transform then the highest DAG node in the container will be selected.  There is no effect
          when selecting nodes which are not in a container.
    
      - disableComponentPopups : dcp   (bool)          [create,query]
          A separate preference to allow users to disable popup menus when selecting components.  This pref is only meaningful if
          the popupMenuSelection pref is enabled.
    
      - expandPopupList : epl          (bool)          [create,query]
          When in popup selection mode, if this is set then all selection items that contain multiple objects or components will
          be be expanded such that each object or component will be a single new selection item.
    
      - ignoreSelectionPriority : isp  (bool)          [create,query]
          If this is set, selection priority will be ignored when performing selection.
    
      - manipClickBoxSize : mcb        (int)           [create,query]
          When selecting a manipulator, this value defines the size of square picking region surrounding the cursor. The size of
          the square is twice the specified value. That is, the value defines the amount of space on all four sides of the cursor
          position. The size must be positive.
    
      - paintSelect : ps               (bool)          [query]
          When enabled, the select tool will use drag selection instead of marquee selection.
    
      - paintSelectRefine : psf        (bool)          []
    
      - paintSelectWithDepth : psd     (bool)          [query]
          When enabled, paint selection will not select components that are behind the surface in the current camera view.
    
      - popupMenuSelection : pms       (bool)          [create,query]
          If this is set, a popup menu will be displayed and used to determine the object to select. The menu lists the current
          user box (marquee) of selected candidate objects.
    
      - preSelectBackfacing : psb      (bool)          [query]
          When enabled preselection will highlight backfacing components whose normals face away from the camera.
    
      - preSelectClosest : psc         (bool)          [query]
          When enabled and the cursor is over a surface, preselection highlighting will try to preselect the closest component to
          the cursor regardless of distance.
    
      - preSelectDeadSpace : pds       (int)           [query]
          This value defines the size of the region around the cursor used for preselection highlighting when the cursor is
          outside the surface.
    
      - preSelectHilite : psh          (bool)          [query]
          When enabled, the closest component under the cursor will be highlighted to indicate that clicking will select that
          component.
    
      - preSelectHiliteSize : phs      (float)         [query]
          This value defines the size of the region around the cursor used for preselection highlighting. Within this region the
          closest component to the cursor will be highlighted.
    
      - preSelectSize : pss            (int)           []
    
      - preSelectTweakDeadSpace : pdt  (int)           [query]
          This value defines the size of the region around the cursor used for preselection highlighting when the cursor is
          outside the surface in tweak mode.
    
      - selectTypeChangeAffectsActive : stc (bool)          [query]
          If true then the active list will be updated according to the new selection preferences.
    
      - selectionChildHighlightMode : sch (int)           [create,query]
          Controls the highlighting of the children of a selected object. Valid modes are:  0: Always highlight children 1: Never
          highlight children 2: Use per-object Selection Child Highlightsetting.  Default mode is (0): Always highlight children.
          For (2), each DAG object has an individual Selection Child Highlightboolean flag. By default, this flag will be TRUE.
          When mode (2) is enabled, the control is deferred to the selected object's Selection Child Highlightflag.
    
      - singleBoxSelection : sbs       (bool)          [create,query]
          Set single box selection on/off. This flag indicates whether just single object will be selected when the user box
          (marquee) selects several objects if flag set to true.  Otherwise, all those objects inside the box will be selected.
    
      - straightLineDistance : sld     (bool)          [query]
          If true then use straight line distances for selection proximity.
    
      - trackSelectionOrder : tso      (bool)          [query]
          When enabled, the order of selected objects and components will be tracked.  The 'ls' command will be able to return the
          active list in the order of selection which will allow scripts to be written that depend on the order.
    
      - useDepth : ud                  (bool)          [query]
          When enabled, marquee selection will not select components that are behind the surface in the current camera view.
    
      - xformNoSelect : xns            (bool)          [create,query]
          Disable selection in xform tools                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.selectPref`
    """

    pass


def deleteExtension(*args, **kwargs):
    """
    This command is used to delete an extension attribute from a node type. The attribute can be specified by using either
    the long or short name. Only one extension attribute can be deleted at a time. Children of a compound attribute cannot
    be deleted, you must delete the complete compound attribute. This command has no undo, edit, or query capabilities.
    
    Flags:
      - attribute : at                 (unicode)       [create]
          Specify either the long or short name of the attribute.
    
      - forceDelete : fd               (bool)          [create]
          If this flag is set and turned ON then data values for the extension attributes are all deleted without confirmation. If
          it's set and turned OFF then any extension attributes that have non-default values set on any node will remain in place.
          If this flag is not set at all then the user will be asked if they wish to preserve non-default values on this
          attribute.
    
      - nodeType : nt                  (unicode)       [create]
          The name of the node type.                                 Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.deleteExtension`
    """

    pass


def distanceDimension(*args, **kwargs):
    """
    This command is used to create a distance dimension to display the distance between two specified points.
    
    Modifications:
      - returns a PyNode object
    
    Flags:
      - endPoint : ep                  (float, float, float) [create]
          Specifies the point to measure distance to, from the startPoint.
    
      - startPoint : sp                (float, float, float) [create]
          Specifies the point to start measuring distance from.                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.distanceDimension`
    """

    pass


def license(*args, **kwargs):
    """
    This command displays version information about the application if it is executed without flags.  If one of the above
    flags is specified then the specified version information is returned.
    
    Flags:
      - borrow : b                     (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - info : i                       (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - isBorrowed : ib                (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - isExported : ie                (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - isTrial : it                   (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - licenseMethod : lm             (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - productChoice : pc             (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - r : r                          (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - showBorrowInfo : sbi           (bool)          [create]
          This flag is obsolete and no longer supported.
    
      - showProductInfoDialog : spi    (bool)          [create]
          Show the Product Information Dialog
    
      - status : s                     (bool)          []
    
      - usage : u                      (bool)          [create]
          This flag is obsolete and no longer supported.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.license`
    """

    pass


def isConnected(*args, **kwargs):
    """
    The isConnectedcommand is used to check if two plugs are connected in the dependency graph. The return value is falseif
    they are not and trueif they are. The first string specifies the source plug to check for connection. The second one
    specifies the destination plug to check for connection.
    
    Flags:
      - ignoreUnitConversion : iuc     (bool)          [create]
          In looking for connections, skip past unit conversion nodes.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.isConnected`
    """

    pass


def selectType(*args, **kwargs):
    """
    The selectTypecommand is used to change the set of allowable types of objects that can be selected when using the select
    tool. It accepts no other arguments besides the flags. There are basically two different types of items that are
    selectable when interactively selecting objects in the 3D views.  They are classified as objects (entire objects) or
    components (parts of objects).  The objectand componentcommand flags control which class of objects are selectable. It
    is possible to select components while in the object selection mode. To set the components which are selectable in
    object selection mode you must use the -ocm flag when specifying the component flags.
    
    Flags:
      - allComponents : alc            (bool)          [create,query]
          Set all component selection masks on/off
    
      - allObjects : alo               (bool)          [create,query]
          Set all object selection masks on/off
    
      - animBreakdown : abd            (bool)          [create,query]
          Set animation breakdown selection mask on/off.
    
      - animCurve : ac                 (bool)          [create,query]
          Set animation curve selection mask on/off.
    
      - animInTangent : ait            (bool)          [create,query]
          Set animation in-tangent selection mask on/off.
    
      - animKeyframe : ak              (bool)          [create,query]
          Set animation keyframe selection mask on/off.
    
      - animOutTangent : aot           (bool)          [create,query]
          Set animation out-tangent selection mask on/off.
    
      - byName : bn                    (unicode, bool) [create]
          Set the specified user-defined selection mask on/off. (object flag)
    
      - camera : ca                    (bool)          [create,query]
          Set camera selection mask on/off. (object flag)
    
      - cluster : cl                   (bool)          [create,query]
          Set cluster selection mask on/off. (object flag)
    
      - collisionModel : clm           (bool)          [create,query]
          Set collision model selection mask on/off. (object flag)
    
      - controlVertex : cv             (bool)          [create,query]
          Set control vertex selection mask on/off. (component flag)
    
      - curve : c                      (bool)          [create,query]
          Set curve selection mask on/off. (object flag)
    
      - curveKnot : ck                 (bool)          [create,query]
          Set curve knot selection mask on/off. (component flag)
    
      - curveOnSurface : cos           (bool)          [create,query]
          Set curve-on-surface selection mask on/off. (object flag)
    
      - curveParameterPoint : cpp      (bool)          [create,query]
          Set curve parameter point selection mask on/off. (component flag)
    
      - dimension : dim                (bool)          [create,query]
          Set dimension shape selection mask on/off. (object flag)
    
      - dynamicConstraint : dc         (bool)          [create,query]
          Set dynamicConstraint selection mask on/off. (object flag)
    
      - edge : eg                      (bool)          [create,query]
          Set mesh edge selection mask on/off. (component flag)
    
      - editPoint : ep                 (bool)          [create,query]
          Set edit-point selection mask on/off. (component flag)
    
      - emitter : em                   (bool)          [create,query]
          Set emitter selection mask on/off. (object flag)
    
      - facet : fc                     (bool)          [create,query]
          Set mesh face selection mask on/off. (component flag)
    
      - field : fi                     (bool)          [create,query]
          Set field selection mask on/off. (object flag)
    
      - fluid : fl                     (bool)          [create,query]
          Set fluid selection mask on/off. (object flag)
    
      - follicle : fo                  (bool)          [create,query]
          Set follicle selection mask on/off. (object flag)
    
      - hairSystem : hs                (bool)          [create,query]
          Set hairSystem selection mask on/off. (object flag)
    
      - handle : ha                    (bool)          [create,query]
          Set object handle selection mask on/off. (object flag)
    
      - hull : hl                      (bool)          [create,query]
          Set hull selection mask on/off. (component flag)
    
      - ikEndEffector : iee            (bool)          [create,query]
          Set ik end effector selection mask on/off. (object flag)
    
      - ikHandle : ikh                 (bool)          [create,query]
          Set ik handle selection mask on/off. (object flag)
    
      - imagePlane : ip                (bool)          [create,query]
          Set image plane selection mask on/off. (component flag)
    
      - implicitGeometry : ig          (bool)          [create,query]
          Set implicit geometry selection mask on/off. (object flag)
    
      - isoparm : iso                  (bool)          [create,query]
          Set surface iso-parm selection mask on/off. (component flag)
    
      - joint : j                      (bool)          [create,query]
          Set ik handle selection mask on/off. (object flag)
    
      - jointPivot : jp                (bool)          [create,query]
          Set joint pivot selection mask on/off. (component flag)
    
      - lattice : la                   (bool)          [create,query]
          Set lattice selection mask on/off. (object flag)
    
      - latticePoint : lp              (bool)          [create,query]
          Set lattice point selection mask on/off. (component flag)
    
      - light : lt                     (bool)          [create,query]
          Set light selection mask on/off. (object flag)
    
      - localRotationAxis : ra         (bool)          [create,query]
          Set local rotation axis selection mask on/off. (component flag)
    
      - locator : lc                   (bool)          [create,query]
          Set locator (all types) selection mask on/off. (object flag)
    
      - locatorUV : luv                (bool)          [create,query]
          Set uv locator selection mask on/off. (object flag)
    
      - locatorXYZ : xyz               (bool)          [create,query]
          Set xyz locator selection mask on/off. (object flag)
    
      - meshComponents : mc            (bool)          []
    
      - meshUVShell : msh              (bool)          [create,query]
          Set uv shell component mask on/off.
    
      - motionTrailPoint : mtp         (bool)          [create,query]
          Set motion point selection mask on/off.
    
      - motionTrailTangent : mtt       (bool)          [create,query]
          Set motion point tangent mask on/off.
    
      - nCloth : ncl                   (bool)          [create,query]
          Set nCloth selection mask on/off. (object flag)
    
      - nParticle : npr                (bool)          [create,query]
          Set nParticle point selection mask on/off. (component flag)
    
      - nParticleShape : nps           (bool)          [create,query]
          Set nParticle shape selection mask on/off. (object flag)
    
      - nRigid : nr                    (bool)          [create,query]
          Set nRigid selection mask on/off. (object flag)
    
      - nonlinear : nl                 (bool)          [create,query]
          Set nonlinear selection mask on/off. (object flag)
    
      - nurbsCurve : nc                (bool)          [create,query]
          Set nurbs-curve selection mask on/off. (object flag)
    
      - nurbsSurface : ns              (bool)          [create,query]
          Set nurbs-surface selection mask on/off. (object flag)
    
      - objectComponent : ocm          (bool)          [create,query]
          Component flags apply to object mode.
    
      - orientationLocator : ol        (bool)          [create,query]
          Set orientation locator selection mask on/off. (object flag)
    
      - particle : pr                  (bool)          [create,query]
          Set particle point selection mask on/off. (component flag)
    
      - particleShape : ps             (bool)          [create,query]
          Set particle shape selection mask on/off. (object flag)
    
      - plane : pl                     (bool)          [create,query]
          Set sketch plane selection mask on/off. (object flag)
    
      - polymesh : p                   (bool)          [create,query]
          Set poly-mesh selection mask on/off. (object flag)
    
      - polymeshEdge : pe              (bool)          [create,query]
          Set poly-mesh edge selection mask on/off. (component flag)
    
      - polymeshFace : pf              (bool)          [create,query]
          Set poly-mesh face selection mask on/off. (component flag)
    
      - polymeshFreeEdge : pfe         (bool)          [create,query]
          Set poly-mesh free-edge selection mask on/off. (component flag)
    
      - polymeshUV : puv               (bool)          [create,query]
          Set poly-mesh UV point selection mask on/off. (component flag)
    
      - polymeshVertex : pv            (bool)          [create,query]
          Set poly-mesh vertex selection mask on/off. (component flag)
    
      - polymeshVtxFace : pvf          (bool)          [create,query]
          Set poly-mesh vertexFace selection mask on/off. (component flag)
    
      - queryByName : qbn              (unicode)       [query]
          Query the specified user-defined selection mask. (object flag)
    
      - rigidBody : rb                 (bool)          [create,query]
          Set rigid body selection mask on/off. (object flag)
    
      - rigidConstraint : rc           (bool)          [create,query]
          Set rigid constraint selection mask on/off. (object flag)
    
      - rotatePivot : rp               (bool)          [create,query]
          Set rotate pivot selection mask on/off. (component flag)
    
      - scalePivot : sp                (bool)          [create,query]
          Set scale pivot selection mask on/off. (component flag)
    
      - sculpt : sc                    (bool)          [create,query]
          Set sculpt selection mask on/off. (object flag)
    
      - selectHandle : sh              (bool)          [create,query]
          Set select handle selection mask on/off. (component flag)
    
      - spring : spr                   (bool)          [create,query]
          Set spring shape selection mask on/off. (object flag)
    
      - springComponent : spc          (bool)          [create,query]
          Set individual spring selection mask on/off. (component flag)
    
      - stroke : str                   (bool)          [create,query]
          Set the Paint Effects stroke selection mask on/off. (object flag)
    
      - subdiv : sd                    (bool)          [create,query]
          Set subdivision surfaces selection mask on/off. (object flag)
    
      - subdivMeshEdge : sme           (bool)          [create,query]
          Set subdivision surfaces mesh edge selection mask on/off. (component flag)
    
      - subdivMeshFace : smf           (bool)          [create,query]
          Set subdivision surfaces mesh face selection mask on/off. (component flag)
    
      - subdivMeshPoint : smp          (bool)          [create,query]
          Set subdivision surfaces mesh point selection mask on/off. (component flag)
    
      - subdivMeshUV : smu             (bool)          [create,query]
          Set subdivision surfaces mesh UV map selection mask on/off. (component flag)
    
      - surfaceEdge : se               (bool)          [create,query]
          Set surface edge selection mask on/off. (component flag)
    
      - surfaceFace : sf               (bool)          [create,query]
          Set surface face selection mask on/off. (component flag)
    
      - surfaceKnot : sk               (bool)          [create,query]
          Set surface knot selection mask on/off. (component flag)
    
      - surfaceParameterPoint : spp    (bool)          [create,query]
          Set surface parameter point selection mask on/off. (component flag)
    
      - surfaceRange : sr              (bool)          [create,query]
          Set surface range selection mask on/off. (component flag)
    
      - surfaceUV : suv                (bool)          [create,query]
          Set surface uv selection mask on/off. (component flag)
    
      - texture : tx                   (bool)          [create,query]
          Set texture selection mask on/off. (object flag)
    
      - vertex : v                     (bool)          [create,query]
          Set mesh vertex selection mask on/off. (component flag)                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.selectType`
    """

    pass


def hasAttr(pyObj, attr, checkShape=True):
    """
    convenience function for determining if an object has an attribute.
    If checkShape is enabled, the shape node of a transform will also be checked for the attribute.
    
    :rtype: `bool`
    """

    pass


def instancer(*args, **kwargs):
    """
    This command is used to create a instancer node and set the proper attributes in the node.
    
    Maya Bug Fix:
      - name of newly created instancer was not returned
    
    Flags:
      - addObject : a                  (bool)          [create,edit]
          This flag indicates that objects specified by the -object flag will be added to the instancer node as instanced objects.
    
      - cycle : c                      (unicode)       [create,query,edit]
          This flag sets or queries the cycle attribute for the instancer node. The options are noneor sequential.  The default is
          none.
    
      - cycleStep : cs                 (float)         [create,query,edit]
          This flag sets or queries the cycle step attribute for the instancer node.  This attribute indicates the size of the
          step in frames or seconds (see cycleStepUnit).
    
      - cycleStepUnits : csu           (unicode)       [create,query,edit]
          This flag sets or queries the cycle step unit attribute for the instancer node.  The options are framesor seconds.  The
          default is frames.
    
      - index : i                      (int)           [query]
          This flag is used to query the name of the ith instanced object.
    
      - levelOfDetail : lod            (unicode)       [create,query,edit]
          This flag sets or queries the level of detail of the instanced objects.  The options are geometry, boundingBox,
          boundingBoxes.  The default is geometry.
    
      - name : n                       (unicode)       [create,query]
          This flag sets or queries the name of the instancer node.
    
      - object : obj                   (unicode)       [create,query,edit]
          This flag indicates which objects will be add/removed from the list of instanced objects.  The flag is used in
          conjuction with the -add and -remove flags.  If neither of these flags is specified on the command line then -add is
          assumed.
    
      - objectPosition : op            (unicode)       [query]
          This flag queries the given objects position.  This object can be any instanced object or sub-object.
    
      - objectRotation : objectRotation (unicode)       [query]
          This flag queries the given objects rotation.  This object can be any instanced object or sub-object.
    
      - objectScale : os               (unicode)       [query]
          This flag queries the given objects scale.  This object can be any instanced object or sub-object.
    
      - pointDataSource : pds          (bool)          [query]
          This flag is used to query the source node supply the data for the input points.
    
      - removeObject : rm              (bool)          [edit]
          This flag indicates that objects specified by the -object flag will be removed from the instancer node as instanced
          objects.
    
      - rotationOrder : ro             (unicode)       [create,query,edit]
          This flag specifies the rotation order associated with the rotation flag.  The options are XYZ, XZY, YXZ, YZX, ZXY, or
          ZYX.  By default the attribute is XYZ.
    
      - rotationUnits : ru             (unicode)       [create,query,edit]
          This flag specifies the rotation units associated with the rotation flag.  The options are degrees or radians.  By
          default the attribute is degrees.
    
      - valueName : vn                 (unicode)       [query]
          This flag is used to query the value(s) of the array associated with the given name.  If the -index flag is used in
          conjuction with this flag then the ith value will be returned.  Otherwise, the entire array will be returned.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.instancer`
    """

    pass


def align(*args, **kwargs):
    """
    Align or spread objects along X Y and Z axis.
    
    Flags:
      - alignToLead : atl              (bool)          [create]
          When set, the min, center or max values are computed from the lead object. Otherwise, the values are averaged for all
          objects. Default is false
    
      - coordinateSystem : cs          (PyNode)        [create]
          Defines the X, Y, and Z coordinates. Default is the world coordinates
    
      - xAxis : x                      (unicode)       [create]
          Any of none, min, mid, max, dist, stack. This defines the kind of alignment to perfom, default is none.
    
      - yAxis : y                      (unicode)       [create]
          Any of none, min, mid, max, dist, stack. This defines the kind of alignment to perfom, default is none.
    
      - zAxis : z                      (unicode)       [create]
          Any of none, min, mid, max, dist, stack. This defines the kind of alignment to perfom, default is none.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.align`
    """

    pass


def instanceable(*args, **kwargs):
    """
    Flags one or more DAG nodes so that they can (or cannot) be instanced. This command sets an internal state on the
    specified DAG nodes which is checked whenever Maya attempts an instancing operation. If no node names are provided on
    the command line then the current selection list is used.  Sets are automatically expanded to their constituent objects.
    Nodes which are already instanced (or have children which are already instanced) cannot be marked as non-instancable.
    
    Flags:
      - allow : a                      (bool)          [create,query]
          Specifies the new instanceable state for the node. Specify true to allow the node to be instanceable, and false to
          prevent it from being instanced. The default is true (i.e. nodes can be instanced by default).
    
      - recursive : r                  (bool)          [create]
          Can be specified with the -allow flag in create or edit mode to recursively apply the -allow setting to all non-shape
          children of the selected node(s). To also affect shapes, also specify the -shape flag along with -recursive.
    
      - shape : s                      (bool)          [create]
          Can be specified with the -allow flag in create or edit mode to apply the -allow setting to all shape children of the
          selected node(s). This flag can be specified in conjunction with the -recursive flag.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.instanceable`
    """

    pass


def makeIdentity(*args, **kwargs):
    """
    The makeIdentity command is a quick way to reset the selected transform and all of its children down to the shape level
    by the identity transformation.  You can also specify which of transform, rotate or scale is applied down from the
    selected transform. The identity transformation means: translate = 0, 0, 0rotate = 0, 0, 0scale = 1, 1, 1shear = 1, 1,
    1If a transform is a joint, then the translateattribute may not be 0, but will be used to position the joints so that
    they preserve their world space positions.  The translate flag doesn't apply to joints, since joints must preserve their
    world space positions.  Only the rotate and scale flags are meaningful when applied to joints. If the -a/apply flag is
    true, then the transforms that are reset are accumulated and applied to the all shapes below the modified transforms, so
    that the shapes will not move. The pivot positions are recalculated so that they also will not move in world space. If
    this flag is false, then the transformations are reset to identity, without any changes to preserve position.
    
    Flags:
      - apply : a                      (bool)          [create]
          If this flag is true, the accumulated transforms are applied to the shape after the transforms are made identity, such
          that the world space positions of the transforms pivots are preserved, and the shapes do not move. The default is false.
    
      - jointOrient : jo               (bool)          [create]
          If this flag is set, the joint orient on joints will be reset to align with worldspace.
    
      - normal : n                     (int)           [create]
          If this flag is set to 1, the normals on polygonal objects will be frozen.  This flag is valid only when the -apply flag
          is on. If this flag is set to 2, the normals on polygonal objects will be frozen only if its a non-rigid transformation
          matrix. ie, a transformation that does not contain shear, skew or non-proportional scaling. The default behaviour is not
          to freeze normals.
    
      - preserveNormals : pn           (bool)          [create]
          If this flag is true, the normals on polygonal objects will be reversed if the objects are negatively scaled
          (reflection). This flag is valid only when the -apply flag is on.
    
      - rotate : r                     (bool)          [create]
          If this flag is true, only the rotation is applied to the shape. The rotation will be changed to 0, 0, 0. If neither
          translate nor rotate nor scale flags are specified, then all (t, r, s) are applied.
    
      - scale : s                      (bool)          [create]
          If this flag is true, only the scale is applied to the shape. The scale factor will be changed to 1, 1, 1. If neither
          translate nor rotate nor scale flags are specified, then all (t, r, s) are applied.
    
      - translate : t                  (bool)          [create]
          If this flag is true, only the translation is applied to the shape. The translation will be changed to 0, 0, 0. If
          neither translate nor rotate nor scale flags are specified, then all (t, r, s)  are applied.  (Note: the translate flag
          is not meaningful when applied to joints, since joints are made to preserve their world space position.  This flag will
          have no effect on joints.)                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.makeIdentity`
    """

    pass


def _nodeAddedCallback(list_):
    pass


def vnnNode(*args, **kwargs):
    """
    The vnnNodecommand is used to operate vnnNode and query its port and connections. The first argument is the full name of
    the DG node that the VNN node is in. The second argument is the name of the full path of the VNN node.
    
    Flags:
      - connected : c                  (bool)          [create]
          Used with listPortsto query the connected or unconnected ports.
    
      - connectedTo : ct               (unicode)       [create]
          Used with listConnectedNodesto query the nodes that are connected to the specified ports.
    
      - listConnectedNodes : lcn       (bool)          [create]
          Used to list nodes which are connected to the specified node. The returned result is a list of node names.
    
      - listPortChildren : lpc         (unicode)       [create]
          List the children of specified port.
    
      - listPorts : lp                 (bool)          [create]
          List ports on the specified node. Can be used with connectedto determine if the returned ports have connections.
    
      - portDefaultValue : pdv         (unicode, unicode) [create]
          Set the default value to a node port The port cannot be connected.
    
      - queryAcceptablePortDataTypes : qat (unicode)       [create]
          Get the list of acceptable types for the given port of an unresolved node. The acceptable types are based on the
          overloads that match the current defined ports of the node.
    
      - queryIsUnresolved : qiu        (bool)          [create]
          Query if the node is unresolved. A node is considered unresolved if it is part of overload set, and have at least one
          port that is both unconnected and has an undefined type.
    
      - queryPortDataType : qpt        (unicode)       [create]
          Query the data type of a specified port.
    
      - queryPortDefaultValue : qpv    (unicode)       [create]
          Query the default value of a node port
    
      - queryTypeName : qtn            (bool)          [create]
          Used to query the fundamental type of a node such as runtimeName,libraryName,typeName
    
      - setPortDataType : spt          (unicode, unicode) [create]
          Set the data type of a specified port.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.vnnNode`
    """

    pass


def delete(*args, **kwargs):
    """
    This command is used to delete selected objects, or all objects, or objects specified along with the command. Flags are
    available to filter the type of objects that the command acts on. At times, more than just specified items will be
    deleted.  For example, deleting two CVs in the same rowon a NURBS surface will delete the whole row.
    
    Modifications:
      - the command will not fail on an empty list
    
    Flags:
      - all : all                      (bool)          [create]
          Remove all objects of specified kind, in the scene. This flag is to be used in conjunction with the following flags.
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - channels : c                   (bool)          [create]
          Remove animation channels in the scene. Either all channels can be removed, or the scope can be narrowed down by
          specifying some of the above mentioned options.
    
      - constraints : cn               (bool)          [create]
          Remove selected constraints and constraints attached to the selected nodes, or remove all constraints in the scene.
    
      - constructionHistory : ch       (bool)          [create]
          Remove the construction history on the objects specified or selected.
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - expressions : e                (bool)          [create]
          Remove expressions in the scene. Either all expressions can be removed, or the scope can be narrowed down by specifying
          some of the above mentioned options.
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - inputConnectionsAndNodes : icn (bool)          [create]
          Break input connection to specified attribute and delete all unconnected nodes that are left behind. The graph will be
          traversed until a node that cannot be deleted is encountered.
    
      - motionPaths : mp               (bool)          []
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - staticChannels : sc            (bool)          [create]
          Remove static animation channels in the scene. Either all static channels can be removed, or the scope can be narrowed
          down by specifying some of the above mentioned options.
    
      - timeAnimationCurves : tac      (bool)          [create]
          Modifies the -c/channels and -sc/staticChannels flags. When true, only channels connected to time-input animation curves
          (for instance, those created by 'setKeyframe' will be deleted.  When false, no time-input animation curves will be
          deleted. Default: true.
    
      - unitlessAnimationCurves : uac  (bool)          [create]
          Modifies the -c/channels and -sc/staticChannels flags. When true, only channels connected to unitless-input animation
          curves (for instance, those created by 'setDrivenKeyframe' will be deleted.  When false, no unitless-input animation
          curves will be deleted.  Default: true.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.delete`
    """

    pass


def displayPref(*args, **kwargs):
    """
    This command sets/queries the state of global display parameters.                In query mode, return type is based on
    queried flag.
    
    Flags:
      - activeObjectPivots : aop       (bool)          [create,query]
          Sets the display state for drawing pivots for active objects.
    
      - defaultFontSize : dfs          (int)           []
    
      - displayAffected : da           (bool)          [create,query]
          Turns on/off the special coloring of objects that are affected by the objects that are currently in the selection list.
          If one of the curves in a loft were selected and this feature were turned on, then the lofted surface would be
          highlighted because it is affected by the loft curve.
    
      - displayGradient : dgr          (bool)          [create,query]
          Set whether to display the background using a colored gradient as opposed to a constant background color.
    
      - fontSettingMode : fm           (int)           []
    
      - ghostFrames : gf               (int, int, int) [create,query]
          Sets the ghosting frame preferences: steps before, steps after and step size.
    
      - lineWidth : lw                 (float)         []
    
      - materialLoadingMode : mld      (unicode)       [create,query]
          Sets the material loading mode when loading the scene.  Possible values for the string argument are immediate,
          deferredand parallel.
    
      - maxHardwareTextureResolution : mhr (bool)          [query]
          Query the maximum allowable hardware texture resolution available on the current video card. This maximum can vary
          between different video cards and different operating systems.
    
      - maxTextureResolution : mtr     (int)           [create,query]
          Sets the maximum hardware texture resolution to be used when creating hardware textures for display. The maximum will be
          clamped to the maximum allowable texture determined for the hardware at the time this command is invoked. Use the
          -maxHardwareTextureResolution to retrieve this maximum value. Existing hardware textures are not affected. Only newly
          created textures will be clamped to this maximum.
    
      - purgeExistingTextures : pet    (bool)          [create]
          Purge any existing hardware textures. This will force a re-evaluation of hardware textures used for display, and thus
          may take some time to evaluate.
    
      - regionOfEffect : roe           (bool)          [create,query]
          Turns on/off the display of the region of curves/surfaces that is affected by changes to selected CVs and edit points.
    
      - shadeTemplates : st            (bool)          [create,query]
          Turns on/off the display of templated surfaces as shaded in shaded display mode. If its off, templated surfaces appear
          in wireframe.
    
      - smallFontSize : sfs            (int)           []
    
      - textureDrawPixel : tdp         (bool)          [create,query]
          Sets the display mode for drawing image planes. True for use of gltexture calls for perspective views. This flag should
          not normally be needed. Image Planes may display faster on Windows but can result in some display artifacts.
    
      - wireframeOnShadedActive : wsa  (unicode)       [create,query]
          Sets the display state for drawing the wireframe on active shaded objects.  Possible values for the string argument are
          full, reducedand none.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.displayPref`
    """

    pass


def paramDimension(*args, **kwargs):
    """
    This command is used to create a param dimension to display the parameter value of a curve/surface at a specified point
    on the curve/surface.
    
    
    Derived from mel command `maya.cmds.paramDimension`
    """

    pass


def rotate(obj, *args, **kwargs):
    """
    The rotate command is used to change the rotation of geometric objects. The rotation values are specified as Euler
    angles (rx, ry, rz). The values are interpreted based on the current working unit for Angular measurements. Most often
    this is degrees. The default behaviour, when no objects or flags are passed, is to do a absolute rotate on each
    currently selected object in the world space.
    
    Modifications:
      - allows any iterable object to be passed as first argument::
    
            rotate("pSphere1", [0,1,2])
    
    NOTE: this command also reorders the argument order to be more intuitive, with the object first
    
    Flags:
      - absolute : a                   (bool)          [create]
          Perform an absolute operation.
    
      - centerPivot : cp               (bool)          [create]
          Let the pivot be the center of the bounding box of all objects
    
      - constrainAlongNormal : xn      (bool)          [create]
          When true, transform constraints are applied along the vertex normal first and only use the closest point when no
          intersection is found along the normal.
    
      - deletePriorHistory : dph       (bool)          [create]
          If true then delete the history prior to the current operation.
    
      - euler : eu                     (bool)          [create]
          Modifer for -relative flag that specifies rotation values should be added to current XYZ rotation values.
    
      - forceOrderXYZ : fo             (bool)          [create]
          When true, euler rotation value will be understood in XYZ rotation order not per transform node basis.
    
      - objectCenterPivot : ocp        (bool)          [create]
          Let the pivot be the center of the bounding box of each object
    
      - objectSpace : os               (bool)          [create]
          Perform rotation about object-space axis.
    
      - orientAxes : oa                (float, float, float) []
    
      - pivot : p                      (float, float, float) [create]
          Define the pivot point for the transformation
    
      - preserveChildPosition : pcp    (bool)          [create]
          When true, transforming an object will apply an opposite transform to its child transform to keep them at the same
          world-space position. Default is false.
    
      - preserveGeometryPosition : pgp (bool)          [create]
          When true, transforming an object will apply an opposite transform to its geometry points to keep them at the same
          world-space position. Default is false.
    
      - preserveUV : puv               (bool)          [create]
          When true, UV values on rotated components are projected across the rotation in 3d space. For small edits, this will
          freeze the world space texture mapping on the object. When false, the UV values will not change for a selected vertices.
          Default is false.
    
      - reflection : rfl               (bool)          [create]
          To move the corresponding symmetric components also.
    
      - reflectionAboutBBox : rab      (bool)          [create]
          Sets the position of the reflection axis  at the geometry bounding box
    
      - reflectionAboutOrigin : rao    (bool)          [create]
          Sets the position of the reflection axis  at the origin
    
      - reflectionAboutX : rax         (bool)          [create]
          Specifies the X=0 as reflection plane
    
      - reflectionAboutY : ray         (bool)          [create]
          Specifies the Y=0 as reflection plane
    
      - reflectionAboutZ : raz         (bool)          [create]
          Specifies the Z=0 as reflection plane
    
      - reflectionTolerance : rft      (float)         [create]
          Specifies the tolerance to findout the corresponding reflected components
    
      - relative : r                   (bool)          [create]
          Perform a operation relative to the object's current position
    
      - rotateX : x                    (bool)          [create]
          Rotate in X direction
    
      - rotateXY : xy                  (bool)          [create]
          Rotate in X and Y direction
    
      - rotateXYZ : xyz                (bool)          [create]
          Rotate in all directions (default)
    
      - rotateXZ : xz                  (bool)          [create]
          Rotate in X and Z direction
    
      - rotateY : y                    (bool)          [create]
          Rotate in Y direction
    
      - rotateYZ : yz                  (bool)          [create]
          Rotate in Y and Z direction
    
      - rotateZ : z                    (bool)          [create]
          Rotate in Z direction
    
      - symNegative : smn              (bool)          [create]
          When set the component transformation is flipped so it is relative to the negative side of the symmetry plane. The
          default (no flag) is to transform components relative to the positive side of the symmetry plane.
    
      - translate : t                  (bool)          [create]
          When true, the command will modify the node's translate attribute instead of its rotateTranslate attribute, when
          rotating around a pivot other than the object's own rotate pivot.
    
      - worldSpace : ws                (bool)          [create]
          Perform rotation about global world-space axis.
    
      - xformConstraint : xc           (unicode)       [create]
          Apply a transform constraint to moving components. none - no constraintsurface - constrain components to the surfaceedge
          - constrain components to surface edgeslive - constraint components to the live surfaceFlag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.rotate`
    """

    pass


def _deprecatePyNode():
    pass


def bakePartialHistory(*args, **kwargs):
    """
    This command is used to bake sections of the construction history of a shape node when possible. A typical usage would
    be on a shape that has both modelling operations and deformers in its history. Using this command with the
    -prePostDeformers flag will bake the modeling portions of the graph, so that only the deformers remain. Note that not
    all modeling operations can be baked such that they create exactly the same effect after baking. For example, imagine
    the history contains a skinning operation followed by a smooth. Before baking, the smooth operation is performed each
    time the skin deforms, so it will smooth differently depending on the output of the skin. When the smooth operation is
    baked into the skinning, the skin will be reweighted based on the smooth points to attempt to approximate the original
    behavior. However, the skin node does not perform the smooth operation, it merely performs skinning with the newly
    calculated weights and the result will not be identical to before the bake. In general, modeling operations that occur
    before deformers can be baked precisely. Those which occur after can only be approximated. The -pre and -post flags
    allow you to control whether only the operations before or after the deformers are baked. When the command is used on an
    object with no deformers, the entire history will be deleted.
    
    Flags:
      - allShapes : all                (bool)          [create,query]
          Specifies that the bake operation should be performed on all shapes in the entire scene. By default, only selected
          objects are baked. If this option is specified and there are no shapes in the scene, then this command will do nothing
          and end successfully.
    
      - postSmooth : nps               (bool)          [create,query]
          Specifies whether or not a smoothing operation should be done on skin vertices. This smoothing is only done on vertices
          that are found to deviate largely from other vertex values.  The default is false.
    
      - preCache : pc                  (bool)          [create,query]
          Specifies baking of any history operations that occur before the caching operation, including deformers. In query mode,
          returns a list of the nodes that will be baked.
    
      - preDeformers : pre             (bool)          [create,query]
          Specifies baking of any modeling operations in the history that occur before the deformers. In query mode, returns a
          list of the nodes that will be baked.
    
      - prePostDeformers : ppt         (bool)          [create,query]
          Specifies baking of all modeling operations in the history whether they are before or after the deformers in the
          history. If neither the -prePostDeformers nor the -preDeformers flag is specified, prePostDeformers will be used as the
          default. In query mode, returns a list of the nodes that will be baked.                                   Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.bakePartialHistory`
    """

    pass


def setAttr(attr, *args, **kwargs):
    """
    Sets the value of a dependency node attribute.  No value for the the attribute is needed when the -l/-k/-s flags are
    used. The -type flag is only required when setting a non-numeric attribute. The following chart outlines the syntax of
    setAttr for non-numeric data types: TYPEbelow means any number of values of type TYPE, separated by a space[TYPE]means
    that the value of type TYPEis optionalA|Bmeans that either of Aor Bmay appearIn order to run its examples, first execute
    these commands to create the sample attribute types:sphere -n node; addAttr -ln short2Attr -at short2; addAttr -ln
    short2a -p short2Attr -at short; addAttr -ln short2b -p short2Attr -at short; addAttr -ln short3Attr -at short3; addAttr
    -ln short3a -p short3Attr -at short; addAttr -ln short3b -p short3Attr -at short; addAttr -ln short3c -p short3Attr -at
    short; addAttr -ln long2Attr -at long2; addAttr -ln long2a -p long2Attr -at long; addAttr -ln long2b -p long2Attr -at
    long; addAttr -ln long3Attr -at long3; addAttr -ln long3a -p long3Attr -at long; addAttr -ln long3b -p long3Attr -at
    long; addAttr -ln long3c -p long3Attr -at long; addAttr -ln float2Attr -at float2; addAttr -ln float2a -p float2Attr -at
    float; addAttr -ln float2b -p float2Attr -at float; addAttr -ln float3Attr -at float3; addAttr -ln float3a -p float3Attr
    -at float; addAttr -ln float3b -p float3Attr -at float; addAttr -ln float3c -p float3Attr -at float; addAttr -ln
    double2Attr -at double2; addAttr -ln double2a -p double2Attr -at double; addAttr -ln double2b -p double2Attr -at double;
    addAttr -ln double3Attr -at double3; addAttr -ln double3a -p double3Attr -at double; addAttr -ln double3b -p double3Attr
    -at double; addAttr -ln double3c -p double3Attr -at double; addAttr -ln int32ArrayAttr -dt Int32Array; addAttr -ln
    doubleArrayAttr -dt doubleArray; addAttr -ln pointArrayAttr -dt pointArray; addAttr -ln vectorArrayAttr -dt vectorArray;
    addAttr -ln stringArrayAttr -dt stringArray; addAttr -ln stringAttr -dt string; addAttr -ln matrixAttr -dt matrix;
    addAttr -ln sphereAttr -dt sphere; addAttr -ln coneAttr -dt cone; addAttr -ln meshAttr -dt mesh; addAttr -ln latticeAttr
    -dt lattice; addAttr -ln spectrumRGBAttr -dt spectrumRGB; addAttr -ln reflectanceRGBAttr -dt reflectanceRGB; addAttr -ln
    componentListAttr -dt componentList; addAttr -ln attrAliasAttr -dt attributeAlias; addAttr -ln curveAttr -dt nurbsCurve;
    addAttr -ln surfaceAttr -dt nurbsSurface; addAttr -ln trimFaceAttr -dt nurbsTrimface; addAttr -ln polyFaceAttr -dt
    polyFaces; -type short2Array of two short integersValue Syntaxshort shortValue Meaningvalue1 value2Mel ExamplesetAttr
    node.short2Attr -type short2 1 2;Python Examplecmds.setAttr('node.short2Attr',1,2,type='short2')-type short3Array of
    three short integersValue Syntaxshort short shortValue Meaningvalue1 value2 value3Mel ExamplesetAttr node.short3Attr
    -type short3 1 2 3;Python Examplecmds.setAttr('node.short3Attr',1,2,3,type='short3')-type long2Array of two long
    integersValue Syntaxlong longValue Meaningvalue1 value2Mel ExamplesetAttr node.long2Attr -type long2 1000000
    2000000;Python Examplecmds.setAttr('node.long2Attr',1000000,2000000,type='long2')-type long3Array of three long
    integersValue Syntaxlong long longValue Meaningvalue1 value2 value3Mel ExamplesetAttr node.long3Attr -type long3 1000000
    2000000 3000000;Python Examplecmds.setAttr('node.long3Attr',1000000,2000000,3000000,type='long3')-type
    Int32ArrayVariable length array of long integersValue SyntaxValue MeaningMel ExamplesetAttr node.int32ArrayAttr -type
    Int32Array 2 12 75;Python Examplecmds.setAttr('node.int32ArrayAttr',[2,12,75],type='Int32Array')-type float2Array of two
    floatsValue Syntaxfloat floatValue Meaningvalue1 value2Mel ExamplesetAttr node.float2Attr -type float2 1.1 2.2;Python
    Examplecmds.setAttr('node.float2Attr',1.1,2.2,type='float2')-type float3Array of three floatsValue Syntaxfloat float
    floatValue Meaningvalue1 value2 value3Mel ExamplesetAttr node.float3Attr -type float3 1.1 2.2 3.3;Python
    Examplecmds.setAttr('node.float3Attr',1.1,2.2,3.3,type='float3')-type double2Array of two doublesValue Syntaxdouble
    doubleValue Meaningvalue1 value2Mel ExamplesetAttr node.double2Attr -type double2 1.1 2.2;Python
    Examplecmds.setAttr('node.double2Attr',1.1,2.2,type='double2')-type double3Array of three doublesValue Syntaxdouble
    double doubleValue Meaningvalue1 value2 value3Mel ExamplesetAttr node.double3Attr -type double3 1.1 2.2 3.3;Python
    Examplecmds.setAttr('node.double3Attr',1.1,2.2,3.3,type='double3')-type doubleArrayVariable length array of doublesValue
    SyntaxValue MeaningMel ExamplesetAttr node.doubleArrayAttr -type doubleArray 2 3.14159 2.782;Python Examplecmds.setAttr(
    node.doubleArrayAttr, (2, 3.14159, 2.782,), type=doubleArray)-type matrix4x4 matrix of doublesValue Syntaxdouble double
    double doubledouble double double doubledouble double double doubledouble double double doubleValue Meaningrow1col1
    row1col2 row1col3 row1col4row2col1 row2col2 row2col3 row2col4row3col1 row3col2 row3col3 row3col4row4col1 row4col2
    row4col3 row4col4Alternate Syntaxstring double double doubledouble double doubleintegerdouble double doubledouble double
    doubledouble double doubledouble double doubledouble double doubledouble double doubledouble double double doubledouble
    double double doubledouble double doublebooleanAlternate MeaningxformscaleX scaleY scaleZrotateX rotateY
    rotateZrotationOrder (0=XYZ, 1=YZX, 2=ZXY, 3=XZY, 4=YXZ, 5=ZYX)translateX translateY translateZshearXY shearXZ
    shearYZscalePivotX scalePivotY scalePivotZscaleTranslationX scaleTranslationY scaleTranslationZrotatePivotX rotatePivotY
    rotatePivotZrotateTranslationX rotateTranslationY rotateTranslationZrotateOrientW rotateOrientX rotateOrientY
    rotateOrientZjointOrientW jointOrientX jointOrientY jointOrientZinverseParentScaleX inverseParentScaleY
    inverseParentScaleZcompensateForParentScale Mel ExamplesetAttr node.matrixAttr -type matrix1 0 0 0 0 1 0 0 0 0 1 0 2 3 4
    1;setAttr node.matrixAttr -type matrixxform1 1 1 0 0 0 0 2 3 4 0 0 00 0 0 0 0 0 0 0 0 0 0 1 1 0 0 1 0 1 0 1 1 1 0
    false;Python Examplecmds.setAttr('node.matrixAttr',(1,0,0,0,0,1,0,0,0,0,1,0,2,3,4,1),type='matrix')cmds.setAttr('node.ma
    trixAttr','xform',(1,1,1),(0,0,0),0,(2,3,4),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,1,1),(0,0,1,0),(1,0,1,0),(1,2,3),False,ty
    pe=matrix)-type pointArrayVariable length array of pointsValue SyntaxValue MeaningMel ExamplesetAttr node.pointArrayAttr
    -type pointArray 2 1 1 1 1 2 2 2 1;Python
    Examplecmds.setAttr('node.pointArrayAttr',2,(1,1,1,1),(2,2,2,1),type='pointArray')-type vectorArrayVariable length array
    of vectorsValue SyntaxValue MeaningMel ExamplesetAttr node.vectorArrayAttr -type vectorArray 2 1 1 1 2 2 2;Python
    Examplecmds.setAttr('node.vectorArrayAttr',2,(1,1,1),(2,2,2),type='vectorArray')-type stringCharacter stringValue
    SyntaxstringValue MeaningcharacterStringValueMel ExamplesetAttr node.stringAttr -type stringblarg;Python
    Examplecmds.setAttr('node.stringAttr',blarg,type=string)-type stringArrayVariable length array of stringsValue
    SyntaxValue MeaningMel ExamplesetAttr node.stringArrayAttr -type stringArray 3 abc;Python
    Examplecmds.setAttr('node.stringArrayAttr',3,a,b,c,type='stringArray')-type sphereSphere dataValue SyntaxdoubleValue
    MeaningsphereRadiusExamplesetAttr node.sphereAttr -type sphere 5.0;-type coneCone dataValue Syntaxdouble doubleValue
    MeaningconeAngle coneCapMel ExamplesetAttr node.coneAttr -type cone 45.0 5.0;Python
    Examplecmds.setAttr('node.coneAttr',45.0,5.0,type='cone')-type reflectanceRGBReflectance dataValue Syntaxdouble double
    doubleValue MeaningredReflect greenReflect blueReflectMel ExamplesetAttr node.reflectanceRGBAttr -type reflectanceRGB
    0.5 0.5 0.1;Python Examplecmds.setAttr('node.reflectanceRGBAttr',0.5,0.5,0.1,type='reflectanceRGB')-type
    spectrumRGBSpectrum dataValue Syntaxdouble double doubleValue MeaningredSpectrum greenSpectrum blueSpectrumMel
    ExamplesetAttr node.spectrumRGBAttr -type spectrumRGB 0.5 0.5 0.1;Python
    Examplecmds.setAttr('node.spectrumRGBAttr',0.5,0.5,0.1,type='spectrumRGB')-type componentListVariable length array of
    componentsValue SyntaxValue MeaningMel ExamplesetAttr node.componentListAttr -type componentList 3 cv[1] cv[12]
    cv[3];Python Examplecmds.setAttr('node.componentListAttr',3,'cv[1]','cv[12]','cv[3]',type='componentList')-type
    attributeAliasString alias dataValue Syntaxstring stringValue MeaningnewAlias currentNameMel ExamplesetAttr
    node.attrAliasAttr -type attributeAliasGoUp, translateY, GoLeft, translateX;Python
    Examplecmds.setAttr('node.attrAliasAttr',(GoUp, translateY,GoLeft, translateX),type='attributeAlias')-type
    nurbsCurveNURBS curve dataValue SyntaxValue MeaningMel Example// degree is the degree of the curve(range 1-7)// spans is
    the number of spans // form is open (0), closed (1), periodic (2)// dimension is 2 or 3, depending on the dimension of
    the curve// isRational is true if the curve CVs contain a rational component // knotCount is the size of the knot list//
    knotValue is a single entry in the knot list// cvCount is the number of CVs in the curve//  xCVValue,yCVValue,[zCVValue]
    [wCVValue] is a single CV.//  zCVValue is only present when dimension is 3.//  wCVValue is only present when isRational
    is true.//setAttr node.curveAttr -type nurbsCurve 3 1 0 no 36 0 0 0 1 1 14 -2 3 0 -2 1 0 -2 -1 0 -2 -3 0;-type
    nurbsSurfaceNURBS surface dataValue Syntaxint int int int bool Value MeaninguDegree vDegree uForm vForm
    isRationalTRIM|NOTRIMExample// uDegree is degree of the surface in U direction (range 1-7)// vDegree is degree of the
    surface in V direction (range 1-7)// uForm is open (0), closed (1), periodic (2) in U direction// vForm is open (0),
    closed (1), periodic (2) in V direction// isRational is true if the surface CVs contain a rational component//
    uKnotCount is the size of the U knot list//  uKnotValue is a single entry in the U knot list// vKnotCount is the size of
    the V knot list//  vKnotValue is a single entry in the V knot list// If TRIMis specified then additional trim
    information is expected// If NOTRIMis specified then the surface is not trimmed// cvCount is the number of CVs in the
    surface//  xCVValue,yCVValue,zCVValue [wCVValue]is a single CV.//  zCVValue is only present when dimension is 3.//
    wCVValue is only present when isRational is true//setAttr node.surfaceAttr -type nurbsSurface 3 3 0 0 no 6 0 0 0 1 1 16
    0 0 0 1 1 116 -2 3 0 -2 1 0 -2 -1 0 -2 -3 0-1 3 0 -1 1 0 -1 -1 0 -1 -3 01 3 0 1 1 0 1 -1 0 1 -3 03 3 0 3 1 0 3 -1 0 3 -3
    0;-type nurbsTrimfaceNURBS trim face dataValue SyntaxValue MeaningExample// flipNormal if true turns the surface inside
    out// boundaryCount: number of boundaries// boundaryType: // tedgeCountOnBoundary    : number of edges in a boundary//
    splineCountOnEdge    : number of splines in an edge in// edgeTolerance        : tolerance used to build the 3d edge//
    isEdgeReversed        : if true, the edge is backwards// geometricContinuity    : if true, the edge is tangent
    continuous// splineCountOnPedge    : number of splines in a 2d edge// isMonotone            : if true, curvature is
    monotone// pedgeTolerance        : tolerance for the 2d edge//-type polyFacePolygon face dataValue SyntaxfhmfmhmufcValue
    MeaningfhmfmhmufcExample// This data type (polyFace) is meant to be used in file I/O// after setAttrs have been written
    out for vertex position// arrays, edge connectivity arrays (with corresponding start// and end vertex descriptions),
    texture coordinate arrays and// color arrays.  The reason is that this data type references// all of its data through
    ids created by the former types.//// fspecifies the ids of the edges making up a face -//     negative value if the edge
    is reversed in the face// hspecifies the ids of the edges making up a hole -//     negative value if the edge is
    reversed in the face// mfspecifies the ids of texture coordinates (uvs) for a face.//     This data type is obsolete as
    of version 3.0. It is replaced by mu.// mhspecifies the ids of texture coordinates (uvs) for a hole//     This data type
    is obsolete as of version 3.0. It is replaced by mu.// muThe  first argument refers to the uv set. This is a zero-
    based//     integer number. The second argument refers to the number of vertices (n)//     on the face which have valid
    uv values. The last n values are the uv//     ids of the texture coordinates (uvs) for the face. These indices//     are
    what used to be represented by the mfand mhspecification.//     There may be more than one muspecification, one for each
    unique uv set.// fcspecifies the color index values for a face//setAttr node.polyFaceAttr -type polyFaces f3 1 2 3 fc3 4
    4 6;-type meshPolygonal meshValue SyntaxValue Meaningvvn[vtesmooth|hard]Example// vspecifies the vertices of the
    polygonal mesh// vnspecifies the normal of each vertex// vtis optional and specifies a U,V texture coordinate for each
    vertex// especifies the edge connectivity information between vertices//setAttr node.meshAttr -type mesh v3 0 0 0 0 1 0
    0 0 1vn3 1 0 0 1 0 0 1 0 0vt3 0 0 0 1 1 0e3 0 1 hard1 2 hard2 0 hard;-type latticeLattice dataValue SyntaxValue
    MeaningsDivisionCount tDivisionCount uDivisionCountExample// sDivisionCount is the horizontal lattice division count//
    tDivisionCount is the vertical lattice division count// uDivisionCount is the depth lattice division count// pointCount
    is the total number of lattice points// pointX,pointY,pointZ is one lattice point.  The list is//   specified varying
    first in S, then in T, last in U so the//   first two entries are (S=0,T=0,U=0) (s=1,T=0,U=0)//setAttr node.latticeAttr
    -type lattice 2 5 2 20-2 -2 -2 2 -2 -2 -2 -1 -2 2 -1 -2 -2 0 -22 0 -2 -2 1 -2 2 1 -2 -2 2 -2 2 2 -2-2 -2 2 2 -2 2 -2 -1
    2 2 -1 2 -2 0 22 0 2 -2 1 2 2 1 2 -2 2 2 2 2 2;In query mode, return type is based on queried flag.
    
    Maya Bug Fix:
      - setAttr did not work with type matrix.
    
    Modifications:
      - No need to set type, this will automatically be determined
      - Adds support for passing a list or tuple as the second argument for datatypes such as double3.
      - When setting stringArray datatype, you no longer need to prefix the list with the number of elements - just pass a list or tuple as with other arrays
      - Added 'force' kwarg, which causes the attribute to be added if it does not exist.
            - if no type flag is passed, the attribute type is based on type of value being set (if you want a float, be sure to format it as a float, e.g.  3.0 not 3)
            - currently does not support compound attributes
            - currently supported python-to-maya mappings:
    
                ============ ===========
                python type  maya type
                ============ ===========
                float        double
                ------------ -----------
                int          long
                ------------ -----------
                str          string
                ------------ -----------
                bool         bool
                ------------ -----------
                Vector       double3
                ------------ -----------
                Matrix       matrix
                ------------ -----------
                [str]        stringArray
                ============ ===========
    
    
        >>> addAttr( 'persp', longName= 'testDoubleArray', dataType='doubleArray')
        >>> setAttr( 'persp.testDoubleArray', [0,1,2])
        >>> setAttr( 'defaultRenderGlobals.preMel', 'sfff')
    
      - Added ability to set enum attributes using the string values; this may be
        done either by setting the 'asString' kwarg to True, or simply supplying
        a string value for an enum attribute.
    
    Flags:
      - alteredValue : av              (bool)          [create]
          The value is only the current value, which may change in the next evalution (if the attribute has an incoming
          connection). This flag is only used during file I/O, so that attributes with incoming connections do not have their data
          overwritten during the first evaluation after a file is opened.
    
      - caching : ca                   (bool)          [create]
          Sets the attribute's internal caching on or off. Not all attributes can be defined as caching. Only those attributes
          that are not defined by default to be cached can be made caching.  As well, multi attribute elements cannot be made
          caching. Caching also affects child attributes for compound attributes.
    
      - capacityHint : ch              (int)           [create]
          Used to provide a memory allocation hint to attributes where the -size flag cannot provide enough information. This flag
          is optional and is primarily intended to be used during file I/O. Only certain attributes make use of this flag, and the
          interpretation of the flag value varies per attribute. This flag is currently used by (node.attribute): mesh.face -
          hints the total number of elements in the face edge lists
    
      - channelBox : cb                (bool)          [create]
          Sets the attribute's display in the channelBox on or off. Keyable attributes are always display in the channelBox
          regardless of the channelBox settting.
    
      - clamp : c                      (bool)          [create]
          For numeric attributes, if the value is outside the range of the attribute, clamp it to the min or max instead of
          failing
    
      - keyable : k                    (bool)          [create]
          Sets the attribute's keyable state on or off.
    
      - lock : l                       (bool)          [create]
          Sets the attribute's lock state on or off.
    
      - size : s                       (int)           [create]
          Defines the size of a multi-attribute array. This is only a hint, used to help allocate memory as efficiently as
          possible.
    
      - type : typ                     (unicode)       [create]
          Identifies the type of data.  If the -type flag is not present, a numeric type is assumed.                  Flag can
          have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.setAttr`
    """

    pass


def attributeName(*args, **kwargs):
    """
    This command takes one node.attribute-style specifier on the command line and returns either the attribute's long,
    short, or nice name.  (The nicename, or UI name, is the name used to display the attribute in Maya's interface, and may
    be localized when running Maya in a language other than English.) If more than one node.attributespecifier is given on
    the command line, only the first valid specifier is processed.
    
    Flags:
      - leaf : lf                      (bool)          [create]
          When false, shows parent multi attributes (like controlPoints[2].xValue).  When true, shows only the leaf-level
          attribute name (like xValue).  Default is true. Note that for incomplete attribute strings, like a missing multi-parent
          index (controlPoints.xValue) or an incorrectly named compound (cntrlPnts[2].xValue), this flag defaults to true and
          provides a result as long as the named leaf-level attribute is defined for the node.
    
      - long : l                       (bool)          [create]
          Returns names in long nameformat like translateX
    
      - nice : n                       (bool)          [create]
          Returns names in nice nameformat like Translate X
    
      - short : s                      (bool)          [create]
          Returns names in short nameformat like txFlag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.attributeName`
    """

    pass


def duplicate(*args, **kwargs):
    """
    This command duplicates the given objects. If no objects are given, then the selected list is duplicated. The smart
    transform feature allows duplicate to transform newly duplicated objects based on previous transformations between
    duplications. Example: Duplicate an object and move it to a new location. Duplicate it again with the smart duplicate
    flag. It should have moved once again the distance you had previously moved it. Note: changing the selected list between
    smart duplications will cause the transform information to be deleted The upstream Nodes option forces duplication of
    all upstream nodes leading upto the selected objects.. Upstream nodes are defined as all nodes feeding into selected
    nodes. During traversal of Dependency graph, if another dagObject is encountered, then that node and all it's parent
    transforms are also duplicated. The inputConnections option forces the duplication of input connections to the nodes
    that are to be duplicated. This is very useful especially in cases where two nodes that are connected to each other are
    specified as nodes to be duplicated. In that situation, the connection between the nodes is also duplicated. See
    also:instance
    
    Modifications:
      - new option: addShape
            If addShape evaluates to True, then all arguments fed in must be shapes, and each will be duplicated and added under
            the existing parent transform, instead of duplicating the parent transform.
            The following arguments are incompatible with addShape, and will raise a ValueError if enabled along with addShape:
                renameChildren (rc), instanceLeaf (ilf), parentOnly (po), smartTransform (st)
      - returns wrapped classes
      - returnRootsOnly is forced on for dag objects. This is because the duplicate command does not use full paths when returning
        the names of duplicated objects and will fail if the name is not unique.
    
    Flags:
      - inputConnections : ic          (bool)          [create]
          Input connections to the node to be duplicated, are also duplicated. This would result in a fan-out scenario as the
          nodes at the input side are not duplicated (unlike the -un option).
    
      - instanceLeaf : ilf             (bool)          [create]
          instead of duplicating leaf DAG nodes, instance them.
    
      - name : n                       (unicode)       [create]
          name to give duplicated object(s)
    
      - parentOnly : po                (bool)          [create]
          Duplicate only the specified DAG node and not any of its children.
    
      - renameChildren : rc            (bool)          [create]
          rename the child nodes of the hierarchy, to make them unique.
    
      - returnRootsOnly : rr           (bool)          [create]
          return only the root nodes of the new hierarchy. When used with upstreamNodes flag, the upstream nodes will be omitted
          in the result.  This flag controls only what is returned in the output string[], and it does NOT change the behaviour of
          the duplicate command.
    
      - smartTransform : st            (bool)          [create]
          remembers last transformation and applies it to duplicated object(s)
    
      - upstreamNodes : un             (bool)          [create]
          the upstream nodes leading upto the selected nodes (along with their connections) are also duplicated.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.duplicate`
    """

    pass


def setEnums(attr, enums):
    """
    Set the enumerators for an enum attribute.
    """

    pass


def commandPort(*args, **kwargs):
    """
    Opens or closes the Maya command port. The command port comprises a socket to which a client program may connect. An
    example command port client mcpis included in the Motion Capture developers kit. It supports multi-byte commands and
    uses utf-8 as its transform format. It will receive utf8 command string and decode it to Maya native coding. The result
    will also be encoded to utf-8 before sending back. Care should be taken regarding INET domain sockets as no user
    identification, or authorization is required to connect to a given socket, and all commands (including system(...)) are
    allowed and executed with the user id and permissions of the Maya user. The prefix flag can be used to reduce this
    security risk, as only the prefix command is executed. The query flag can be used to determine if a given command port
    exists. See examples below.
    
    Flags:
      - bufferSize : bs                (int)           [create]
          Commands and results are each subject to size limits. This option allows the user to specify the size of the buffer used
          to communicate with Maya. If unspecified the default buffer size is 4096 characters. Commands longer than bufferSize
          characters will cause the client connection to close. Results longer that bufferSize characters are replaced with an
          error message.
    
      - close : cl                     (bool)          [create]
          Closes the commandPort, deletes the pipes
    
      - echoOutput : eo                (bool)          [create]
          Sends a copy of all command output to the command port. Typically only the result is transmitted. This option provides a
          copy of all output.
    
      - listPorts : lp                 (bool)          []
    
      - name : n                       (unicode)       [create]
          Specifies the name of the command port which this command creates. CommandPort names of the form namecreate a UNIX
          domain socket on the localhost corresponding to name. If namedoes not begin with /, then /tmp/nameis used. If namebegins
          with /, namedenotes the full path to the socket.  Names of the form :port numbercreate an INET domain on the local host
          at the given port.
    
      - noreturn : nr                  (bool)          [create]
          Do not write the results from executed commands back to the command port socket. Instead, the results from executed
          commands are written to the script editor window. As no information passes back to the command port client regarding the
          execution of the submitted commands, care must be taken not to overflow the command buffer, which would cause the
          connection to close.
    
      - pickleOutput : po              (bool)          [create]
          Python output will be pickled.
    
      - prefix : pre                   (unicode)       [create]
          The string argument is the name of a Maya command taking one string argument. This command is called each time data is
          sent to the command port. The data written to the command port is passed as the argument to the prefix command. The data
          from the command port is encoded as with enocodeString and enclosed in quotes.  If newline characters are embedded in
          the command port data, the input is split into individual lines. These lines are treated as if they were separate writes
          to the command port. Only the result to the last prefix command is returned.
    
      - returnNumCommands : rnc        (bool)          [create]
          Ignore the result of the command, but return the number of commands that have been read and executed in this call. This
          is a simple way to track buffer overflow. This flag is ignored when the noreturnflag is specified.
    
      - securityWarning : sw           (bool)          [create]
          Enables security warning on command port input.
    
      - sourceType : stp               (unicode)       [create]
          The string argument is used to indicate which source type would be passed to the commandPort, like mel, python. The
          default source type is mel.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.commandPort`
    """

    pass


def displayStats(*args, **kwargs):
    """
    Flags:
      - frameRate : fr                 (bool)          []
    
    
    Derived from mel command `maya.cmds.displayStats`
    """

    pass


def suitePrefs(*args, **kwargs):
    """
    This command sets the mouse and keyboard interaction mode for Maya and other Suites applications (if Maya is part of a
    Suites install).
    
    Flags:
      - applyToSuite : ats             (unicode)       [create]
          Apply the mouse and keyboard interaction settings for the given application to all applications in the Suite (if Maya is
          part of a Suites install). Valid values are Maya, 3dsMax, or undefined, which signifies that each app is to use their
          own settings.
    
      - installedAsSuite : ias         (bool)          [create]
          Returns true if Maya is part of a Suites install, false otherwise.
    
      - isCompleteSuite : ics          (bool)          [create]
          Returns true if the Suites install contains all Entertainment Creation Suite products, false otherwise.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.suitePrefs`
    """

    pass


def listAttr(*args, **kwargs):
    """
    This command lists the attributes of a node.  If no flags are specified all attributes are listed.
    
    Modifications:
      - returns an empty list when the result is None
    
    Flags:
      - array : a                      (bool)          [create]
          only list array (not multi) attributes
    
      - caching : ca                   (bool)          [create]
          only show attributes that are cached internally
    
      - category : ct                  (unicode)       [create]
          only show attributes belonging to the given category. Category string can be a regular expression.
    
      - changedSinceFileOpen : cfo     (bool)          [create]
          Only list the attributes that have been changed since the file they came from was opened. Typically useful only for
          objects/attributes coming from referenced files.
    
      - channelBox : cb                (bool)          [create]
          only show non-keyable attributes that appear in the channelbox
    
      - connectable : c                (bool)          [create]
          only show connectable attributes
    
      - extension : ex                 (bool)          [create]
          list user-defined attributes for all nodes of this type (extension attributes)
    
      - fromPlugin : fp                (bool)          [create]
          only show attributes that were created by a plugin
    
      - hasData : hd                   (bool)          [create]
          list only attributes that have data (all attributes except for message attributes)
    
      - hasNullData : hnd              (bool)          [create]
          list only attributes that have null data. This will list all attributes that have data (see hasData flag) but the data
          value is uninitialized. A common example where an attribute may have null data is when a string attribute is created but
          not yet assigned an initial value. Similarly array attribute data is often null until it is initialized.
    
      - inUse : iu                     (bool)          [create]
          only show attributes that are currently marked as in use. This flag indicates that an attribute affects the scene data
          in some way. For example it has a non-default value or it is connected to another attribute.  This is the general
          concept though the precise implementation is subject to change.
    
      - keyable : k                    (bool)          [create]
          only show attributes that can be keyframed
    
      - leaf : lf                      (bool)          [create]
          Only list the leaf-level name of the attribute. controlPoints[44].xValue would be listed as xValue.
    
      - locked : l                     (bool)          [create]
          list only attributes which are locked
    
      - multi : m                      (bool)          [create]
          list each currently existing element of a multi-attribute
    
      - output : o                     (bool)          [create]
          List only the attributes which are numeric or which are compounds of numeric attributes.
    
      - ramp : ra                      (bool)          [create]
          list only attributes which are ramps
    
      - read : r                       (bool)          [create]
          list only attributes which are readable
    
      - readOnly : ro                  (bool)          [create]
          List only the attributes which are readable and not writable.
    
      - scalar : s                     (bool)          [create]
          only list scalar numerical attributes
    
      - scalarAndArray : sa            (bool)          [create]
          only list scalar and array attributes
    
      - settable : se                  (bool)          [create]
          list attribute which are settable
    
      - shortNames : sn                (bool)          [create]
          list short attribute names (default is to list long names)
    
      - string : st                    (unicode)       [create]
          List only the attributes that match the other criteria AND match the string(s) passed from this flag. String can be a
          regular expression.
    
      - unlocked : u                   (bool)          [create]
          list only attributes which are unlocked
    
      - usedAsFilename : uf            (bool)          [create]
          list only attributes which are designated to be treated as filenames
    
      - userDefined : ud               (bool)          [create]
          list user-defined (dynamic) attributes
    
      - visible : v                    (bool)          [create]
          only show visible or non-hidden attributes
    
      - write : w                      (bool)          [create]
          list only attributes which are writable                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.listAttr`
    """

    pass


def select(*args, **kwargs):
    """
    This command is used to put objects onto or off of the active list. If none of the five flags [-add, -af, -r, -d, -tgl]
    are specified, the default is to replace the objects on the active list with the given list of objects. When selecting a
    set as in select set1, the behaviour is for all the members of the set to become selected instead of the set itself. If
    you want to select a set, the -ne/noExpandflag must be used. With the advent of namespaces, selection by name may be
    confusing.  To clarify, without a qualified namespace, name lookup is limited to objects in the root namespace :. There
    are really two parts of a name: the namespace and the name itself which is unique within the namespace. If you want to
    select objects in a specific namespace, you need to include the namespace separator :. For example, 'select -r foo\*' is
    trying to look for an object with the fooprefix in the root namespace. It is not trying to look for all objects in the
    namespace with the fooprefix. If you want to select all objects in a namespace (foo), use 'select foo:\*'. Note: When
    the application starts up, there are several dependency nodes created by the system which must exist. These objects are
    not deletable but are selectable.  All objects (dag and dependency nodes) in the scene can be obtained using the
    lscommand without any arguments. When using the -all, adn/allDependencyNodesor -ado/allDagObjectsflags, only the
    deletable objects are selected.  The non deletable object can still be selected by explicitly specifying their name as
    in select time1;.
    
    Modifications:
      - passing an empty list no longer causes an error.
          instead, the selection is cleared if the selection mod is replace (the default);
          otherwise, it does nothing
    
    Flags:
      - add : add                      (bool)          [create]
          Indicates that the specified items should be added to the active list without removing existing items from the active
          list.
    
      - addFirst : af                  (bool)          [create]
          Indicates that the specified items should be added to the front of the active list without removing existing items from
          the active list.
    
      - all : all                      (bool)          [create]
          Indicates that all deletable root level dag objects and all deletable non-dag dependency nodes should be selected.
    
      - allDagObjects : ado            (bool)          [create]
          Indicates that all deletable root level dag objects should be selected.
    
      - allDependencyNodes : adn       (bool)          [create]
          Indicates that all deletable dependency nodes including all deletable dag objects should be selected.
    
      - clear : cl                     (bool)          [create]
          Clears the active list.  This is more efficient than select -d;.  Also select -d;will not remove sets from the active
          list unless the -neflag is also specified.
    
      - containerCentric : cc          (bool)          [create]
          Specifies that the same selection rules as apply to selection in the main viewport will also be applied to the select
          command. In particular, if the specified objects are members of a black-boxed container and are not published as nodes,
          Maya will not select them. Instead, their first parent valid for selection will be selected.
    
      - deselect : d                   (bool)          [create]
          Indicates that the specified items should be removed from the active list if they are on the active list.
    
      - hierarchy : hi                 (bool)          [create]
          Indicates that all children, grandchildren, ... of the specified dag objects should also be selected.
    
      - noExpand : ne                  (bool)          [create]
          Indicates that any set which is among the specified items should not be expanded to its list of members. This allows
          sets to be selected as opposed to the members of sets which is the default behaviour.
    
      - replace : r                    (bool)          [create]
          Indicates that the specified items should replace the existing items on the active list.
    
      - symmetry : sym                 (bool)          [create]
          Specifies that components should be selected symmetrically using the current symmetricModelling command settings. If
          symmetric modeling is not enabled then this flag has no effect.
    
      - symmetrySide : sys             (int)           [create]
          Indicates that components involved in the current symmetry object should be selected, according to the supplied
          parameter. Valid values for the parameter are: -1 : Select components in the unsymmetrical region. 0 : Select components
          on the symmetry seam. 1 : Select components on side 1. 2 : Select components on side 2. If symmetric modeling is not
          enabled then this flag has no effect. Note: currently only works for topological symmetry.
    
      - toggle : tgl                   (bool)          [create]
          Indicates that those items on the given list which are on the active list should be removed from the active list and
          those items on the given list which are not on the active list should be added to the active list.
    
      - visible : vis                  (bool)          [create]
          Indicates that of the specified items only those that are visible should be affected.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.select`
    """

    pass


def attributeQuery(*args, **kwargs):
    """
    attributeQuery returns information about the configuration of an attribute. It handles both boolean flags, returning
    true or false, as well as other return values. Specifying more than one boolean flag will return the logical andof all
    the specified boolean flags.  You may not specify any two flags when both do not provide a boolean return type.  (eg.
    -internal -hiddenis okay but -range -hiddenor -range -softRangeis not.)
    
    Flags:
      - affectsAppearance : aa         (bool)          [create]
          Return true if the attribute affects the appearance of the node
    
      - affectsWorldspace : aws        (bool)          [create]
          Return the status of the attribute flag marking attributes affecting worldspace
    
      - attributeType : at             (bool)          [create]
          Return the name of the attribute type (will be the same type names as described in the addAttr and addExtension
          commands).
    
      - cachedInternally : ci          (bool)          [create]
          Return whether the attribute is cached within the node as well as in the datablock
    
      - categories : ct                (bool)          [create]
          Return the categories to which the attribute belongs or an empty list if it does not belong to any.
    
      - channelBox : ch                (bool)          [create]
          Return whether the attribute should show up in the channelBox or not
    
      - connectable : c                (bool)          [create]
          Return the connectable status of the attribute
    
      - enum : e                       (bool)          [create]
          Return true if the attribute is a enum attribute
    
      - exists : ex                    (bool)          [create]
          Return true if the attribute exists
    
      - hidden : h                     (bool)          [create]
          Return the hidden status of the attribute
    
      - indeterminant : idt            (bool)          [create]
          Return true if this attribute might be used in evaluation but it's not known for sure until evaluation time
    
      - indexMatters : im              (bool)          [create]
          Return the indexMatters status of the attribute
    
      - internal : i                   (bool)          [create]
          Return true if the attribute is either internalSet or internalGet
    
      - internalGet : ig               (bool)          [create]
          Return true if the attribute come from getCachedValue
    
      - internalSet : internalSet      (bool)          [create]
          Return true if the attribute must be set through setCachedValue
    
      - keyable : k                    (bool)          [create]
          Return the keyable status of the attribute
    
      - listChildren : lc              (bool)          [create]
          Return the list of children attributes of the given attribute.
    
      - listDefault : ld               (bool)          [create]
          Return the default values of numeric and compound numeric attributes.
    
      - listEnum : le                  (bool)          [create]
          Return the list of enum strings for the given attribute.
    
      - listParent : lp                (bool)          [create]
          Return the parent of the given attribute.
    
      - listSiblings : ls              (bool)          [create]
          Return the list of sibling attributes of the given attribute.
    
      - longName : ln                  (bool)          [create]
          Return the long name of the attribute.
    
      - maxExists : mxe                (bool)          [create]
          Return true if the attribute has a hard maximum. A min does not have to be present.
    
      - maximum : max                  (bool)          [create]
          Return the hard maximum of the attribute's value
    
      - message : msg                  (bool)          [create]
          Return true if the attribute is a message attribute
    
      - minExists : mne                (bool)          [create]
          Return true if the attribute has a hard minimum. A max does not have to be present.
    
      - minimum : min                  (bool)          [create]
          Return the hard minimum of the attribute's value
    
      - multi : m                      (bool)          [create]
          Return true if the attribute is a multi-attribute
    
      - niceName : nn                  (bool)          [create]
          Return the nice name (or UI name) of the attribute.
    
      - node : n                       (PyNode)        [create]
          Use all attributes from node named NAME
    
      - numberOfChildren : nc          (bool)          [create]
          Return the number of children the attribute has
    
      - range : r                      (bool)          [create]
          Return the hard range of the attribute's value
    
      - rangeExists : re               (bool)          [create]
          Return true if the attribute has a hard range. Both min and max must be present.
    
      - readable : rd                  (bool)          [create]
          Return the readable status of the attribute
    
      - renderSource : rs              (bool)          [create]
          Return whether this attribute is marked as a render source or not
    
      - shortName : sn                 (bool)          [create]
          Return the short name of the attribute.
    
      - softMax : smx                  (bool)          [create]
          Return the soft max (slider range) of the attribute's value
    
      - softMaxExists : sxe            (bool)          [create]
          Return true if the attribute has a soft maximum. A min does not have to be present.
    
      - softMin : smn                  (bool)          [create]
          Return the soft min (slider range) of the attribute's value
    
      - softMinExists : sme            (bool)          [create]
          Return true if the attribute has a soft minimum. A max does not have to be present.
    
      - softRange : s                  (bool)          [create]
          Return the soft range (slider range) of the attribute's value
    
      - softRangeExists : se           (bool)          [create]
          Return true if the attribute has a soft range. Both min and max must be present.
    
      - storable : st                  (bool)          [create]
          Return true if the attribute is storable
    
      - type : typ                     (unicode)       [create]
          Use static attributes from nodes of type TYPE.  Includes attributes inherited from parent class nodes.
    
      - typeExact : tex                (unicode)       [create]
          Use static attributes only from nodes of type TYPE.  Does not included inherited attributes.
    
      - usedAsColor : uac              (bool)          [create]
          Return true if the attribute should bring up a color picker
    
      - usedAsFilename : uaf           (bool)          [create]
          Return true if the attribute should bring up a file browser
    
      - usesMultiBuilder : umb         (bool)          [create]
          Return true if the attribute is a multi-attribute and it uses the multi-builder to handle its data
    
      - worldspace : ws                (bool)          [create]
          Return the status of the attribute flag marking worldspace attribute
    
      - writable : w                   (bool)          [create]
          Return the writable status of the attribute                                Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.attributeQuery`
    """

    pass


def containerView(*args, **kwargs):
    """
    A container view defines the layout information for the published attributes of a particular container.  Container views
    can be selected from a set of built-in views or may be defined on an associated container template. This command queries
    the view-related information for a container node. The information returned from this command will be based on the view-
    related settings in force on the container node at the time of the query (i.e. the container's view mode, template name,
    view name attributes).                In query mode, return type is based on queried flag.
    
    Flags:
      - itemInfo : ii                  (unicode)       [query]
          Used in query mode in conjunction with the itemList flag. The command will return a list of information for each item in
          the view, the information fields returned for each item are determined by this argument value. The information fields
          will be listed in the string array returned. The order in which the keyword is specified will determine the order in
          which the data will be returned by the command. One or more of the following keywords, separated by colons ':' are used
          to specify the argument value. itemIndex  : sequential item number (0-based)itemName   : item name (string)itemLabel  :
          item display label (string)itemDescription : item description field (string)itemLevel  : item hierarchy level
          (0-n)itemIsGroup : (boolean 0 or 1) indicates whether or not this item is a groupitemIsAttribute : (boolean 0 or 1)
          indicates whether or not this item is an attributeitemNumChildren: number of immediate children (groups or attributes)
          of this itemitemAttrType : item attribute type (string)itemCallback : item callback field (string)
    
      - itemList : il                  (bool)          [query]
          Used in query mode, the command will return a list of information for each item in the view.  The viewName flag is used
          to select the view to query. The information returned about each item is determined by the itemInfo argument value. For
          efficiency, it is best to query all necessary item information at one time (to avoid recomputing the view information on
          each call).
    
      - viewDescription : vd           (bool)          [query]
          Used in query mode, returns the description field associated with the selected view. If no description was defined for
          this view, the value will be empty.
    
      - viewLabel : vb                 (bool)          [query]
          Used in query mode, returns the display label associated with the view. An appropriate label suitable for the user
          interface will be returned based on the selected view.  Use of the view label is usually more suitable than the view
          name for display purposes.
    
      - viewList : vl                  (bool)          [query]
          Used in query mode, command will return a list of all views defined for the given target (container or template).
    
      - viewName : vn                  (unicode)       [query]
          Used in query mode, specifies the name of the queried view when used in conjunction with a template target. When used in
          conjunction with a container target, it requires no string argument, and returns the name of the currently active view
          associated with the container; this value may be empty if the current view is not a valid template view or is generated
          by one of the built-in views modes. For this reason, the view label is generally more suitable for display purposes. In
          query mode, this flag can accept a value.Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.containerView`
    """

    pass


def commandLogging(*args, **kwargs):
    """
    This command controls logging of Maya commands, in memory and on disk. Note that if commands are logged in memory, they
    will be available to the crash reporter and appear in crash logs.                In query mode, return type is based on
    queried flag.
    
    Flags:
      - historySize : hs               (int)           [create,query]
          Sets the number of entries in the in-memory command history.
    
      - logCommands : lc               (bool)          [create,query]
          Enables or disables the on-disk logging of commands.
    
      - logFile : lf                   (unicode)       [create,query]
          Sets the filename to use for the on-disk log. If logging is active, the current file will be closed before the new one
          is opened.
    
      - recordCommands : rc            (bool)          [create,query]
          Enables or disables the in-memory logging of commands.
    
      - resetLogFile : rl              (bool)          [create,query]
          Reset the log filename to the default ('mayaCommandLog.txt' in the application folder, alongside 'Maya.env' and the
          default projects folder).                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.commandLogging`
    """

    pass


def partition(*args, **kwargs):
    """
    This command is used to create, query or add/remove sets to a partition. If a partition name needs to be specified, it
    is the first argument, other arguments represent the set names. Without any flags, the command will create a partition
    with a default name.  Any sets which are arguments to the command will be added to the partition. A set can be added to
    a partition only if none of its members are in any of the other sets in the partition. If the -re/render flag is
    specified when the partition is created, only 'renderable' sets can be added to the partition. Sets can be added and
    removed from a partition by using the -addSet or -removeSet flags. Note:If a set is already selected, and the partition
    command is executed, the set will be added to the created partition.
    
    Flags:
      - addSet : add                   (PyNode)        [create]
          Adds the list of sets to the named partition.
    
      - name : n                       (unicode)       [create]
          Assigns the given name to new partition. Valid only for create mode.
    
      - removeSet : rm                 (PyNode)        [create]
          Removes the list of sets from the named partition.
    
      - render : re                    (bool)          [create,query]
          New partition can contain render sets. For use in creation mode only. Default is false.  Can also be used with query
          flag - returns boolean.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.partition`
    """

    pass


def parent(*args, **kwargs):
    """
    This command parents (moves) objects under a new group, removes objects from an existing group, or adds/removes parents.
    If the -w flag is specified all the selected or specified objects are parented to the world (unparented first). If the
    -rm flag is specified then all the selected or specified instances are removed. If there are more than two objects
    specified all the objects are parented to the last object specified. If the -add flag is specified, the objects are not
    reparented but also become children of the last object specified. If there is only a single object specified then the
    selected objects are parented to that object. If an object is parented under a different group and there is an object in
    that group with the same name then this command will rename the parented object.
    
    Modifications:
        - if parent is `None`, world=True is automatically set
        - if the given parent is the current parent, don't error (similar to mel)
    
    Flags:
      - absolute : a                   (bool)          [create]
          preserve existing world object transformations (overall object transformation is preserved by modifying the objects
          local transformation) If the object to parent is a joint, it will alter the translation and joint orientation of the
          joint to preserve the world object transformation if this suffices. Otherwise, a transform will be inserted between the
          joint and the parent for this purpose. In this case, the transformation inside the joint is not altered. [default]
    
      - addObject : add                (bool)          [create]
          preserve existing local object transformations but don't reparent, just add the object(s) under the parent. Use -world
          to add the world as a parent of the given objects.
    
      - noConnections : nc             (bool)          [create]
          The parent command will normally generate new instanced set connections when adding instances. (ie. make a connection to
          the shading engine for new instances) This flag suppresses this behaviour and is primarily used by the file format.
    
      - noInvScale : nis               (bool)          [create]
          The parent command will normally connect inverseScale to its parent scale on joints. This is used to compensate scale on
          joint. The connection of inverseScale will occur if both child and parent are joints and no connection is present on
          child's inverseScale. In case of a reparenting, the old inverseScale will only get broken if the old parent is a joint.
          Otherwise connection will remain intact. This flag suppresses this behaviour.
    
      - relative : r                   (bool)          [create]
          preserve existing local object transformations (relative to the parent node)
    
      - removeObject : rm              (bool)          [create]
          Remove the immediate parent of every object specified. To remove only a single instance of a shape from a parent, the
          path to the shape should be specified. Note: if there is a single parent then the object is effectively deleted from the
          scene. Use -world to remove the world as a parent of the given object.
    
      - shape : s                      (bool)          [create]
          The parent command usually only operates on transforms.  Using this flags allows a shape that is specified to be
          directly parented under the given transform.  This is used to instance a shape node. (ie. parent -add -shapeis
          equivalent to the instancecommand). This flag is primarily used by the file format.
    
      - world : w                      (bool)          [create]
          unparent given object(s) (parent to world)                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.parent`
    """

    pass


def commandEcho(*args, **kwargs):
    """
    This command controls what is echoed to the command window.              In query mode, return type is based on queried
    flag.
    
    Flags:
      - addFilter : af                 (<type 'unicode'>, ...) [create]
          This flag allows you to append filters to the current list of filtered commands when echo all commands is enabled. Just
          like the filter flag, you can provide a partial command name, so all commands that start with a substring specified in
          the addFilter entry will be filtered out.
    
      - filter : f                     (<type 'unicode'>, ...) [create,query]
          This flag allows you to filter out unwanted commands when echo all commands is enabled. You can provide a partial
          command name, so all commands that start with a substring specified in filter entry will be filtered out. If filter is
          empty, all commands are echoed to the command window.
    
      - lineNumbers : ln               (bool)          [create,query]
          If true then file name and line number information is provided in error and warning messages. If false then no file name
          and line number information is provided in error and warning messages.
    
      - state : st                     (bool)          [create,query]
          If true then all commands are echoed to the command window. If false then only relevant commands are echoed.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.commandEcho`
    """

    pass


def makeLive(*args, **kwargs):
    """
    This commmand makes an object live.  A live object defines the surface on which to create objects and to move object
    relative to.  Only construction planes, nurbs surfaces and polygon meshes can be made live. The makeLive command expects
    one of these types of objects as an explicit argument.  If no argument is explicitly specified, then there are a number
    of default behaviours based on what is currently active.  The command will fail if there is more than one object active
    or the active object is not one of the valid types of objects.  If there is nothing active, the current live object will
    become dormant. Otherwise, the active object will become the live object.
    
    Flags:
      - none : n                       (bool)          [create]
          If the -n/none flag, the live object will become dormant. Use of this flag causes any arguments to be ignored.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.makeLive`
    """

    pass


def performanceOptions(*args, **kwargs):
    """
    Sets the global performance options for the application.  The options allow the disabling of features such as stitch
    surfaces or deformers to cut down on computation time in the scene. Performance options that are in effect may be on all
    the time, or they can be turned on only for interaction.  In the latter case, the options will only take effect during
    UI interaction or playback. Note that none of these performance options will affect rendering.
    
    Flags:
      - clusterResolution : cr         (float)         [query]
          Sets the global cluster resolution.  This value may range between 0.0 (exact calculation) and 10.0 (rough approximation)
    
      - disableStitch : ds             (unicode)       [query]
          Sets the state of stitch surface disablement.  Setting this to onsuppresses the generation of stitch surfaces. Valid
          values are on, off, interactive.
    
      - disableTrimBoundaryDisplay : dtb (unicode)       []
    
      - disableTrimDisplay : dt        (unicode)       [query]
          Sets the state of trim drawing disablement.  Setting this to onsuppresses the drawing of surface trims. Valid values are
          on, off, interactive.
    
      - latticeResolution : lr         (float)         [query]
          Sets the global lattice resolution.  This value may range between 0.0 (exact calculation) and 1.0 (rough approximation)
    
      - passThroughBindSkinAndFlexors : pbf (unicode)       [query]
          Sets the state of bind skin and all flexors pass through. Valid values are on, off, interactive.
    
      - passThroughBlendShape : pbs    (unicode)       [query]
          Sets the state of blend shape deformer pass through. Valid values are on, off, interactive.
    
      - passThroughCluster : pc        (unicode)       [query]
          Sets the state of cluster deformer pass through. Valid values are on, off, interactive.
    
      - passThroughDeltaMush : pdm     (unicode)       [query]
          Sets the state of delta mush deformer pass through. Valid values are on, off, interactive.
    
      - passThroughFlexors : pf        (unicode)       [query]
          Sets the state of flexor pass through. Valid values are on, off, interactive.
    
      - passThroughLattice : pl        (unicode)       [query]
          Sets the state of lattice deformer pass through. Valid values are on, off, interactive.
    
      - passThroughPaintEffects : pp   (unicode)       [query]
          Sets the state of paint effects pass through. Valid values are on, off, interactive.
    
      - passThroughSculpt : ps         (unicode)       [query]
          Sets the state of sculpt deformer pass through. Valid values are on, off, interactive.
    
      - passThroughWire : pw           (unicode)       [query]
          Sets the state of wire deformer pass through. Valid values are on, off, interactive.
    
      - skipHierarchyTraversal : sht   (bool)          [query]
          When enabled, hierarchy traversal of invisible objects in the scene will be disabled in order to increase performance
          however this has a side effect of performing redundant viewport refreshes on certain actions such as manipulations,
          start/end of playback, idle refresh calls, etc.
    
      - useClusterResolution : ucr     (unicode)       [query]
          Sets the state of cluster deformer global resolution.  This allows clusters to be calculated at a lower resolution.
          Valid values are on, off, interactive.
    
      - useLatticeResolution : ulr     (unicode)       [query]
          Sets the state of lattice deformer global resolution.  This allows lattices to be calculated at a lower resolution.
          Valid values are on, off, interactive.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.performanceOptions`
    """

    pass


def move(*args, **kwargs):
    """
    The move command is used to change the positions of geometric objects. The default behaviour, when no objects or flags
    are passed, is to do a absolute move on each currently selected object in the world space. The value of the coordinates
    are interpreted as being defined in the current linear unit unless the unit is explicitly mentioned. When using
    -objectSpace there are two ways to use this command. If numbers are typed without units then the internal values of the
    object are set to these values. If, on the other hand a unit is specified then the internal value is set to the
    equivalent internal value that represents that world-space distance. The -localSpace flag moves the object in its parent
    space. In this space the x,y,z values correspond directly to the tx, ty, tz channels on the object. The
    -rotatePivotRelative/-scalePivotRelative flags can be used with the -absolute flag to translate an object so that its
    pivot point ends up at the given absolute position. These flags will be ignored if components are specified. The
    -worldSpaceDistance flag is a modifier flag that may be used in conjunction with the -objectSpace/-localSpace flags.
    When this flag is specified the command treats the x,y,z values as world space units so the object will move the
    specified world space distance but it will move along the axis specified by the -objectSpace/-localSpace flag. The
    default behaviour, without this flag, is to treat the x,y,z values as units in object space or local space. In other
    words, the worldspace distance moved will depend on the transformations applied to the object unless this flag is
    specified.
    
    Modifications:
      - allows any iterable object to be passed as first argument::
    
            move("pSphere1", [0,1,2])
    
    NOTE: this command also reorders the argument order to be more intuitive, with the object first
    
    Flags:
      - absolute : a                   (bool)          [create]
          Perform an absolute operation.
    
      - componentSpace : cs            (bool)          [create]
          Move in component space
    
      - constrainAlongNormal : xn      (bool)          [create]
          When true, transform constraints are applied along the vertex normal first and only use the closest point when no
          intersection is found along the normal.
    
      - deletePriorHistory : dph       (bool)          [create]
          If true then delete the history prior to the current operation.
    
      - localSpace : ls                (bool)          [create]
          Move in local space
    
      - moveX : x                      (bool)          [create]
          Move in X direction
    
      - moveXY : xy                    (bool)          [create]
          Move in XY direction
    
      - moveXYZ : xyz                  (bool)          [create]
          Move in all directions (default)
    
      - moveXZ : xz                    (bool)          [create]
          Move in XZ direction
    
      - moveY : y                      (bool)          [create]
          Move in Y direction
    
      - moveYZ : yz                    (bool)          [create]
          Move in YZ direction
    
      - moveZ : z                      (bool)          [create]
          Move in Z direction
    
      - objectSpace : os               (bool)          [create]
          Move in object space
    
      - orientJoint : oj               (unicode)       [create]
          Default is xyz.
    
      - parameter : p                  (bool)          [create]
          Move in parametric space
    
      - preserveChildPosition : pcp    (bool)          [create]
          When true, transforming an object will apply an opposite transform to its child transform to keep them at the same
          world-space position. Default is false.
    
      - preserveGeometryPosition : pgp (bool)          [create]
          When true, transforming an object will apply an opposite transform to its geometry points to keep them at the same
          world-space position. Default is false.
    
      - preserveUV : puv               (bool)          [create]
          When true, UV values on translated components are projected along the translation in 3d space. For small edits, this
          will freeze the world space texture mapping on the object. When false, the UV values will not change for a selected
          vertices. Default is false.
    
      - reflection : rfl               (bool)          [create]
          To move the corresponding symmetric components also.
    
      - reflectionAboutBBox : rab      (bool)          [create]
          Sets the position of the reflection axis  at the geometry bounding box
    
      - reflectionAboutOrigin : rao    (bool)          [create]
          Sets the position of the reflection axis  at the origin
    
      - reflectionAboutX : rax         (bool)          [create]
          Specifies the X=0 as reflection plane
    
      - reflectionAboutY : ray         (bool)          [create]
          Specifies the Y=0 as reflection plane
    
      - reflectionAboutZ : raz         (bool)          [create]
          Specifies the Z=0 as reflection plane
    
      - reflectionTolerance : rft      (float)         [create]
          Specifies the tolerance to findout the corresponding reflected components
    
      - relative : r                   (bool)          [create]
          Perform a operation relative to the object's current position
    
      - rotatePivotRelative : rpr      (bool)          [create]
          Move relative to the object's rotate pivot point.
    
      - scalePivotRelative : spr       (bool)          [create]
          Move relative to the object's scale pivot point.
    
      - secondaryAxisOrient : sao      (unicode)       [create]
          Default is xyz.
    
      - symNegative : smn              (bool)          [create]
          When set the component transformation is flipped so it is relative to the negative side of the symmetry plane. The
          default (no flag) is to transform components relative to the positive side of the symmetry plane.
    
      - worldSpace : ws                (bool)          [create]
          Move in world space
    
      - worldSpaceDistance : wd        (bool)          [create]
          Move is specified in world space units
    
      - xformConstraint : xc           (unicode)       [create]
          Apply a transform constraint to moving components. none - no constraintsurface - constrain components to the surfaceedge
          - constrain components to surface edgeslive - constraint components to the live surfaceFlag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.move`
    """

    pass


def itemFilter(*args, **kwargs):
    """
    This command creates a named itemFilter object.  This object can be attached to selectionConnection objects, or to
    editors, in order to filter the item lists going through them.  Using union, intersection and difference filters,
    complex composite filters can be created.
    
    Flags:
      - byBin : bk                     (unicode)       [create,query,edit]
          The filter will only pass items whose bin list contains the given string as a bin name.This is a multi-use flag.If more
          than one occurance of this flag is used in a single command, the filter will accept a node if it matches at least one of
          the given bins (in other words, a union or logical or of all given bins.
    
      - byName : bn                    (unicode)       [create,query,edit]
          The filter will only pass items whose names match the given regular expression string.  This string can contain the
          special characters \* and ?.  '?' matches any one character, and '\*' matches any substring.
    
      - byScript : bs                  (unicode)       [create,query,edit]
          The filter will run a MEL script named by the given string on each item name.  Items will pass the filter if the script
          returns a non-zero value. The script name string must be the name of a proc whose signature is:global proc int procName(
          string $name )or def procName(\*args, \*\*keywordArgs)if -pym/pythonModuleis specified. Note that if -secondScript is
          also used, it will always take precedence.
    
      - byType : bt                    (unicode)       [create,query,edit]
          The filter will only pass items whose typeName matches the given string.  The typeName of an object can be found using
          the nodeTypecommand.  This is a multi-use flag. If more than one occurance of this flag is used in a single command, the
          filter will accept a node if it matches at least one of the given types (in other words, a union or logical or of all
          given types.
    
      - category : cat                 (unicode)       [create,query,edit]
          A string for categorizing the filter.
    
      - classification : cls           (unicode)       [create,query,edit]
          Indicates whether the filter is a built-in or user filter. The string argument must be either builtInor user. The
          otherclassification is deprecated. Use userinstead.  Filters will not be deleted by a file new, and filter nodes will be
          hidden from the UI (ex: Attribute Editor, Hypergraph etc) and will not be accessible from the command-line.
    
      - clearByBin : cbk               (bool)          [create,edit]
          This flag will clear any existing bins associated with this filter.
    
      - clearByType : cbt              (bool)          [create,edit]
          This flag will clear any existing typeNames associated with this filter.
    
      - difference : di                (unicode, unicode) [create,query,edit]
          The filter will consist of the set difference of two other filters, whose names are the given strings. Items will pass
          this filter if and only if they pass the first filter but not the second filter.
    
      - exists : ex                    (bool)          [create]
          Returns true|false depending upon whether the specified object exists. Other flags are ignored.
    
      - intersect : intersect          (unicode, unicode) [create,query,edit]
          The filter will consist of the intersection of two other filters, whose names are the given strings. Items will pass
          this filter if and only if they pass both of the contained filters.
    
      - listBuiltInFilters : lbf       (bool)          [query]
          Returns an array of all item filters with classification builtIn.
    
      - listOtherFilters : lof         (bool)          [query]
          The otherclassification is deprecated. Use userinstead. Returns an array of all item filters with classification other.
    
      - listUserFilters : luf          (bool)          [query]
          Returns an array of all item filters with classification user.
    
      - negate : neg                   (bool)          [create,query,edit]
          This flag can be used to cause the filter to invert itself, and reverse what passes and what fails.
    
      - parent : p                     (unicode)       [create,query,edit]
          Optional.  If specified, the filter's life-span is linked to that of the parent.  When the parent goes out of scope, so
          does the filter.  If not specified, the filter will exist until explicitly deleted.
    
      - pythonModule : pym             (unicode)       [create,query,edit]
          Treat -bs/byScriptand -ss/secondScriptas Python functions located in the specified module.
    
      - secondScript : ss              (unicode)       [create,query,edit]
          Cannot be used in conjunction with the -bs flag.  The second script is for filtering whole lists at once, rather than
          individually.  Its signature must be:global proc string[] procName( string[] $name )or def procName(\*args,
          \*\*keywordArgs)if -pym/pythonModuleis specified. It should take in a list of items, and return a filtered list of
          items.
    
      - text : t                       (unicode)       [create,query,edit]
          Defines an annotation string to be stored with the filter
    
      - union : un                     (unicode, unicode) [create,query,edit]
          The filter will consist of the union of two other filters, whose names are the given strings. Items will pass this
          filter if they pass at least one of the contained filters.
    
      - uniqueNodeNames : unn          (bool)          [create,query,edit]
          Returns unique node names to script filters so there are no naming conflicts.                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.itemFilter`
    """

    pass


def about(*args, **kwargs):
    """
    This command displays version information about the application if it is executed without flags.  If one of the above
    flags is specified then the specified version information is returned.
    
    Flags:
      - apiVersion : api               (bool)          [create]
          Returns the api version.
    
      - application : a                (bool)          [create]
          Returns the application name string.
    
      - batch : b                      (bool)          [create]
          Returns true if application is in batch mode.
    
      - buildDirectory : bd            (bool)          [create]
          Returns the build directory string.
    
      - buildVariant : bv              (bool)          [create]
          Returns the build variant string.
    
      - codeset : cs                   (bool)          [create]
          Returns a string identifying the codeset (codepage) of the locale that Maya is running in. Example return values include
          UTF-8, ISO-8859-1, 1252. Note that the codeset values and naming conventions are highly platform dependent.  They may
          differ in format even if they have the same meaning (e.g. utf8vs. UTF-8).
    
      - compositingManager : cm        (bool)          [create]
          On Linux, returns true if there is a compositing manager running; on all other platforms, it always returns true.
    
      - connected : cnt                (bool)          [create]
          Return whether the user is connected or not to the Internet.
    
      - ctime : cti                    (bool)          [create]
          Returns the current time in the format Wed Jan 02 02:03:55 1980\n\0
    
      - currentDate : cd               (bool)          [create]
          Returns the current date in the format yyyy/mm/dd, e.g. 2003/05/04.
    
      - currentTime : ct               (bool)          [create]
          Returns the current time in the format hh:mm:ss, e.g. 14:27:53.
    
      - cutIdentifier : c              (bool)          [create]
          Returns the cut string.
    
      - date : d                       (bool)          [create]
          Returns the build date string.
    
      - environmentFile : env          (bool)          [create]
          Returns the location of the application defaults file.
    
      - evalVersion : ev               (bool)          [create]
          This flag is now deprecated. Always returns false, as the eval version is no longer supported.
    
      - file : f                       (bool)          [create]
          Returns the file version string.
    
      - fontInfo : foi                 (bool)          [create]
          Returns a string of the specifications of the fonts requested, and the specifications of the fonts that are actually
          being used.
    
      - helpDataDirectory : hdd        (bool)          [create]
          Returns the help data directory.
    
      - installedVersion : iv          (bool)          [create]
          Returns the product version string.
    
      - irix : ir                      (bool)          [create]
          Returns true if the operating system is Irix. Always false with support for Irix removed.
    
      - is64 : x64                     (bool)          [create]
          Returns true if the application is 64 bit.
    
      - languageResources : lr         (bool)          [create]
          Returns a string array of the currently installed language resources. Each string entry consists of three elements
          delimited with a colon (':'). The first token is the locale code (ISO 639-1 language code followed by ISO 3166-1 country
          code).  The second token is the language name in English. This third token is the alpha-3 code (ISO 639-2).  For example
          English is represented as en_US:English:enu.
    
      - linux : li                     (bool)          [create]
          Returns true if the operating system is Linux.
    
      - linux64 : l64                  (bool)          [create]
          Returns true if the operating system is Linux 64 bit.
    
      - liveUpdate : lu                (bool)          [create]
          Returns Autodesk formatted product information.
    
      - localizedResourceLocation : lrl (bool)          [create]
          Returns the path to the top level of the localized resource directory, if we are running in an alternate language.
          Returns an empty string if we are running in the default language.
    
      - ltVersion : lt                 (bool)          [create]
          Returns true if this is the Maya LT version of the application.
    
      - macOS : mac                    (bool)          [create]
          Returns true if the operating system is Macintosh.
    
      - macOSppc : ppc                 (bool)          [create]
          Returns true if the operating system is a PowerPC Macintosh.
    
      - macOSx86 : x86                 (bool)          [create]
          Returns true if the operating system is an Intel Macintosh.
    
      - ntOS : nt                      (bool)          [create]
          Returns true if the operating system is Windows.
    
      - operatingSystem : os           (bool)          [create]
          Returns the operating system type. Valid return types are nt, win64, mac, linuxand linux64
    
      - operatingSystemVersion : osv   (bool)          [create]
          Returns the operating system version. on Linux this returns the equivalent of uname -srvm
    
      - preferences : pd               (bool)          [create]
          Returns the location of the preferences directory.
    
      - product : p                    (bool)          [create]
          Returns the license product name.
    
      - qtVersion : qt                 (bool)          [create]
          Returns Qt version string.
    
      - tablet : tab                   (bool)          [create]
          Windows only.  Returns true if the PC is a Tablet PC.
    
      - tabletMode : tm                (bool)          [create]
          Windows 8 (and above) only.  If your device is a Tablet PC, then the convertible mode the device is currently running
          in.  Returns  either: tablet or laptop (keyboard attached). See the tabletflag.
    
      - uiLanguage : uil               (bool)          [create]
          Returns the language that Maya's running in.  Example return values include en_USfor English and ja_JPfor Japanese.
    
      - uiLanguageForStartup : uis     (bool)          [create]
          Returns the language that is used for Maya's next start up. This is read from config file and is rewritten after setting
          ui language in preference.
    
      - uiLanguageIsLocalized : uii    (bool)          [create]
          Returns true if we are running in an alternate language, not the default (English).
    
      - uiLocaleLanguage : ull         (bool)          [create]
          Returns the language locale of the OS. English is default.
    
      - version : v                    (bool)          [create]
          Returns the version string.
    
      - win64 : w64                    (bool)          [create]
          Returns true if the operating system is Windows x64 based.
    
      - windowManager : wm             (bool)          [create]
          Returns the name of the Window Manager that is assumed to be running.
    
      - windows : win                  (bool)          [create]
          Returns true if the operating system is Windows based.                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.about`
    """

    pass


def snapMode(*args, **kwargs):
    """
    The snapMode command is used to control snapping.  It toggles the snapping modes in effect and sets information used for
    snapping.
    
    Flags:
      - curve : c                      (bool)          [create,query]
          Set curve snap mode
    
      - distanceIncrement : dsi        (float)         [create,query]
          Set the distance for the snapping to objects such as a lines or planes.
    
      - edgeMagnet : em                (int)           [create,query]
          Number of extra magnets to snap onto, regularly spaced along the edge.
    
      - edgeMagnetTolerance : emt      (float)         [create,query]
          Precision for edge magnet snapping.
    
      - grid : gr                      (bool)          [create,query]
          Set grid snap mode
    
      - liveFaceCenter : lfc           (bool)          [create,query]
          While moving on live polygon objects, snap to its face centers.
    
      - livePoint : lp                 (bool)          [create,query]
          While moving on live polygon objects, snap to its vertices.
    
      - meshCenter : mc                (bool)          [create,query]
          While moving, snap on the center of the mesh that intersect the line from the camera to the cursor.
    
      - pixelCenter : pc               (bool)          [create,query]
          Snap UV to the center of the pixel instead of the corner.
    
      - pixelSnap : ps                 (bool)          [create,query]
          Snap UVs to the nearest pixel center or corner.
    
      - point : p                      (bool)          [create,query]
          Set point snap mode
    
      - tolerance : t                  (int)           [create,query]
          Tolerance defines the size of the square region in which points must lie in order to be snapped to. The tolerance value
          is the distance from the cursor position to the boundary of the square (in all four directions).
    
      - useTolerance : ut              (bool)          [create,query]
          If useTolerance is set, then point snapping is limited to points that are within a square region surrounding the cursor
          position. The size of the square is determined by the tolerance value.
    
      - uvTolerance : uvt              (int)           [create,query]
          uvTolerance defines the size of the square region in which points must lie in order to be snapped to, in the UV Editor.
          The tolerance value is the distance from the cursor position to the boundary of the square (in all four directions).
    
      - viewPlane : vp                 (bool)          [create,query]
          Set view-plane snap mode                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.snapMode`
    """

    pass


def selectKey(*args, **kwargs):
    """
    This command operates on a keyset.  A keyset is defined as a group of keys within a specified time range on one or more
    animation curves. The animation curves comprising a keyset depend on the value of the -animationflag: keysOrObjects: Any
    active keys, when no target objects or -attribute flags appear on the command line, orAll animation curves connected to
    all keyframable attributes of objects specified as the command line's targetList, when there are no active keys.keys:
    Only act on active keys or tangents. If there are no active keys or tangents, don't do anything. objects: Only act on
    specified objects.  If there are no objects specified, don't do anything. Note that the -animationflag can be used to
    override the curves uniquely identified by the multi-use -attributeflag, which takes an argument of the form
    attributeName, such as translateX. Keys on animation curves are identified by either their time values or their indices.
    Times and indices can be given individually or as part of a list or range. -time 10palmeans the key at frame 10 (PAL
    format).-time 1.0sec -time 15ntsc -time 20means the keys at time 1.0 second, frame 15 (in NTSC format), and time 20 (in
    the currently defined global time unit).-time 10:20means all keys in the range from 10 to 20, inclusive, in the current
    time unit.Omitting one end of a range means go to infinity, as in the following examples: -time 10:means all keys from
    time 10 (in the current time unit) onwards.-time :10means all keys up to (and including) time 10 (in the current time
    unit).-time :is a short form to specify all keys.-index 0means the first key of each animation curve. (Indices are
    0-based.)-index 2 -index 5 -index 7means the 3rd, 6th, and 8th keys.-index 1:5means the 2nd, 3rd, 4th, 5th, and 6th keys
    of each animation curve.This command places keyframes and/or keyframe tangents on the active list.
    
    Flags:
      - addTo : add                    (bool)          [create]
          Add to the current selection of keyframes/tangents
    
      - animation : an                 (unicode)       [create]
          Where this command should get the animation to act on.  Valid values are objects,keys,and keysOrObjectsDefault:
          keysOrObjects.(See Description for details.)
    
      - attribute : at                 (unicode)       [create]
          List of attributes to select
    
      - clear : cl                     (bool)          [create]
          Remove all keyframes and tangents from the active list.
    
      - controlPoints : cp             (bool)          [create]
          This flag explicitly specifies whether or not to include the control points of a shape (see -sflag) in the list of
          attributes. Default: false.  (Not valid for pasteKeycmd.)
    
      - float : f                      (floatrange)    [create]
          value uniquely representing a non-time-based key (or key range) on a time-based animCurve.  Valid floatRange include
          single values (-f 10) or a string with a lower and upper bound, separated by a colon (-f 10:20
    
      - hierarchy : hi                 (unicode)       [create]
          Hierarchy expansion options.  Valid values are above,below,both,and none.(Not valid for pasteKeycmd.)
    
      - inTangent : it                 (bool)          [create]
          Select in-tangents of keyframes in the specified time range
    
      - includeUpperBound : iub        (bool)          [create]
          When the -t/time or -f/float flags represent a range of keys, this flag determines whether the keys at the upper bound
          of the range are included in the keyset. Default value: true.  This flag is only valid when the argument to the -t/time
          flag is a time range with a lower and upper bound.  (When used with the pasteKeycommand, this flag refers only to the
          time range of the target curve that is replaced, when using options such as replace,fitReplace,or scaleReplace.This flag
          has no effect on the curve pasted from the clipboard.)
    
      - index : index                  (int)           [create]
          index of a key on an animCurve
    
      - keyframe : k                   (bool)          [create]
          select only keyframes (cannot be combined with -in/-out)
    
      - outTangent : ot                (bool)          [create]
          Select out-tangents of keyframes in the specified time range
    
      - remove : rm                    (bool)          [create]
          Remove from the current selection of keyframes/tangents
    
      - replace : r                    (bool)          [create]
          Replace the current selection of keyframes/tangents
    
      - shape : s                      (bool)          [create]
          Consider attributes of shapes below transforms as well, except controlPoints.  Default: true.  (Not valid for
          pasteKeycmd.)
    
      - time : t                       (timerange)     [create]
          time uniquely representing a key (or key range) on a time-based animCurve.  Valid timeRanges include single values (-t
          10) or a string with a lower and upper bound, separated by a colon (-t 10:20
    
      - toggle : tgl                   (bool)          [create]
          Toggle the picked state of the specified keyset
    
      - unsnappedKeys : uk             (float)         [create]
          Select only keys that have times that are not a multiple of the specified numeric value.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.selectKey`
    """

    pass


def inheritTransform(*args, **kwargs):
    """
    This command toggles the inherit state of an object. If this flag is off the object will not inherit transformations
    from its parent. In other words transformations applied to the parent node will not affect the object and it will act as
    though it is under the world. If the -p flag is specified then the object's transformation will be modified to
    compensate when changing the inherit flag so the object will not change its world-space location. In query mode, return
    type is based on queried flag.
    
    Flags:
      - off : off                      (bool)          []
    
      - on : on                        (bool)          []
    
      - preserve : p                   (bool)          [create,query]
          preserve the objects world-space position by modifying the object(s) transformation matrix.
    
      - toggle : tgl                   (bool)          [create,query]
          toggle the inherit state for the given object(s) (default if no flags are given) -on turn on inherit state for the given
          object(s) -off turn off inherit state for the given object(s)                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.inheritTransform`
    """

    pass


def _about(*args, **kwargs):
    pass


def _MPlugIn(x):
    pass


def objectType(*args, **kwargs):
    """
    This command returns the type of elements. Warning: This command is incomplete and may not be supported by all object
    types.
    
    Flags:
      - convertTag : ct                (unicode)       []
    
      - isAType : isa                  (unicode)       [create]
          Returns true if the object is the specified type or derives from an object that is of the specified type. This flag will
          only work with dependency nodes.
    
      - isType : i                     (unicode)       [create]
          Returns true if the object is exactly of the specified type. False otherwise.
    
      - tagFromType : tgt              (unicode)       [create]
          Returns the type tag given a type name.
    
      - typeFromTag : tpt              (int)           [create]
          Returns the type name given an integer type tag.
    
      - typeTag : tt                   (bool)          [create]
          Returns an integer tag that is unique for that object type.  Not all object types will have tags.  This is the unique
          4-byte value that is used to identify nodes of a given type in the binary file format.                  Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.objectType`
    """

    pass


def matchTransform(*args, **kwargs):
    """
    This command modifies the source object's transform to match the target object's transform. If no flags are specified
    then the command will match position, rotation and scaling.
    
    Flags:
      - pivots : piv                   (bool)          [create]
          Match the source object(s) scale/rotate pivot positions to the target transform's pivot.
    
      - position : pos                 (bool)          [create]
          Match the source object(s) position to the target object.
    
      - rotation : rot                 (bool)          [create]
          Match the source object(s) rotation to the target object.
    
      - scale : scl                    (bool)          [create]
          Match the source object(s) scale to the target transform.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.matchTransform`
    """

    pass


def selectedNodes(*args, **kwargs):
    """
    Flags:
      - dagObjects : do                (bool)          []
    
    
    Derived from mel command `maya.cmds.selectedNodes`
    """

    pass


def lockNode(*args, **kwargs):
    """
    Locks or unlocks one or more dependency nodes. A locked node is restricted in the following ways:  It may not be
    deleted.It may not be renamed.Its parenting may not be changed.Attributes may not be added to or removed from it.Locked
    attributes may not be unlocked.Unlocked attributes may not be locked.Note that an unlocked attribute of a locked node
    may still have its value set, or connections to it made or broken. For more information on attribute locking, see the
    setAttrcommand.  If no node names are specified then the current selection list is used.  There are a few special
    behaviors when locking containers. Containers are automatically expanded to their constituent objects. When a container
    is locked, members of the container may not be unlocked and the container membership may not be modified. Containers may
    also be set to lock unpublished attributes. When in this state, unpublished member attributes may not have existing
    connections broken, new connections cannot be made, and values on unconnected attributes may not be modified. Parenting
    is allowed to change on members of locked containers that have been published as parent or child anchors.
    
    Flags:
      - ignoreComponents : ic          (bool)          [create,query]
          Normally, the presence of a component in the list of objects to be locked will cause the command to fail with an error.
          But if this flag is supplied then components will be silently ignored.
    
      - lock : l                       (bool)          [create,query]
          Specifies the new lock state for the node. The default is true.
    
      - lockName : ln                  (bool)          [create,query]
          Specifies the new lock state for the node's name.
    
      - lockUnpublished : lu           (bool)          [create,query]
          Used in conjunction with the lock flag. On a container, lock or unlock all unpublished attributes on the members of the
          container. For non-containers, lock or unlock unpublished attributes on the specified node.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.lockNode`
    """

    pass


def paramLocator(*args, **kwargs):
    """
    The command creates a locator in the underworld of a NURBS curve or NURBS surface at the specified parameter value.  If
    no object is specified, then a locator will be created on the first valid selected item (either a curve point or a
    surface point).
    
    Flags:
      - position : p                   (bool)          [create]
          Whether to set the locator position in normalized space.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.paramLocator`
    """

    pass


def toggle(*args, **kwargs):
    """
    The toggle command is used to toggle the display of various object features for objects which have these components. For
    example, CV and edit point display may be toggled for those listed     NURB curves or surfaces. Note: This command is
    not undoable.
    
    Flags:
      - above : a                      (bool)          [create]
          Toggle state for all objects above listed objects.
    
      - below : b                      (bool)          [create]
          Toggle state for all objects below listed objects.
    
      - boundary : bn                  (bool)          [create,query]
          Toggle boundary display of listed mesh objects.
    
      - boundingBox : box              (bool)          [create,query]
          Toggle or query the bounding box display of listed objects.
    
      - controlVertex : cv             (bool)          [create,query]
          Toggle CV display of listed curves and surfaces.
    
      - doNotWrite : dnw               (bool)          [create,query]
          Toggle the this should be written to the filestate.
    
      - editPoint : ep                 (bool)          [create,query]
          Toggle edit point display of listed curves and surfaces.
    
      - extent : et                    (bool)          [create,query]
          Toggle display of extents of listed mesh objects.
    
      - facet : f                      (bool)          [create,query]
          For use with normalflag. Set the normal display style to facet display.
    
      - geometry : g                   (bool)          [create,query]
          Toggle geometry display of listed objects.
    
      - gl : gl                        (bool)          [create]
          Toggle state for all objects
    
      - highPrecisionNurbs : hpn       (bool)          [create,query]
          Toggle high precision display for Nurbs
    
      - hull : hl                      (bool)          [create,query]
          Toggle hull display of listed curves and surfaces.
    
      - latticePoint : lp              (bool)          [create,query]
          Toggle point display of listed lattices
    
      - latticeShape : ls              (bool)          [create,query]
          Toggle display of listed lattices
    
      - localAxis : la                 (bool)          [create,query]
          Toggle local axis display of listed objects.
    
      - newCurve : nc                  (bool)          [create,query]
          Set component display state of new curve objects
    
      - newPolymesh : np               (bool)          [create,query]
          Set component display state of new polymesh objects
    
      - newSurface : ns                (bool)          [create,query]
          Set component display state of new surface objects
    
      - normal : nr                    (bool)          [create,query]
          Toggle display of normals of listed surface and mesh objects.
    
      - origin : o                     (bool)          [create,query]
          Toggle origin display of listed surfaces.
    
      - point : pt                     (bool)          [create,query]
          For use with normal flag. Set the normal display style to vertex display.
    
      - pointDisplay : pd              (bool)          [create,query]
          Toggle point display of listed surfaces.
    
      - pointFacet : pf                (bool)          [create,query]
          For use with normalflag. Set the normal display style to vertex and face display.
    
      - rotatePivot : rp               (bool)          [create,query]
          Toggle rotate pivot display of listed objects.
    
      - scalePivot : sp                (bool)          [create,query]
          Toggle scale pivot display of listed objects.
    
      - selectHandle : sh              (bool)          [create,query]
          Toggle select handle display of listed objects.
    
      - state : st                     (bool)          [create]
          Explicitly set the state to true or false instead of toggling the state. Can not be queried.
    
      - surfaceFace : sf               (bool)          [create,query]
          Toggle surface face handle display of listed surfaces.
    
      - template : te                  (bool)          [create,query]
          Toggle template state of listed objects
    
      - uvCoords : uv                  (bool)          [create,query]
          Toggle display uv coords of listed mesh objects.
    
      - vertex : vt                    (bool)          [create,query]
          Toggle vertex display of listed mesh objects.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.toggle`
    """

    pass


def _formatSlice(sliceObj):
    pass


def scaleComponents(*args, **kwargs):
    """
    This is a limited version of the scale command.  First, it only works on selected components. You provide a pivot in
    world space, and you can provide a rotation.  This rotation affects the scaling, so that rather than scaling in X, Y, Z,
    this is scaling in X, Y, and Z after they have been rotated by the given rotation. This allows selected components to be
    scaled in any arbitrary space, not just object or world space as the regular scale allows. Scale values are always
    relative, not absolute.
    
    Flags:
      - pivot : p                      (float, float, float) [create]
          The pivot position in world space (default is origin)
    
      - rotation : ro                  (float, float, float) [create]
          The rotational offset for the scaling (default is none)                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.scaleComponents`
    """

    pass


def isTrue(*args, **kwargs):
    """
    This commmand returns the state of the named condition. If the condition is true, it returns 1.  Otherwise it returns 0.
    
    
    Derived from mel command `maya.cmds.isTrue`
    """

    pass


def itemFilterRender(*args, **kwargs):
    """
    Flags:
      - anyTextures : at               (bool)          []
    
      - category : cat                 (unicode)       []
    
      - classification : cls           (unicode)       []
    
      - exclusiveLights : exl          (bool)          []
    
      - exists : ex                    (bool)          []
    
      - lightSets : ls                 (bool)          []
    
      - lights : l                     (bool)          []
    
      - linkedLights : ll              (bool)          []
    
      - listBuiltInFilters : lbf       (bool)          []
    
      - listOtherFilters : lof         (bool)          []
    
      - listUserFilters : luf          (bool)          []
    
      - negate : neg                   (bool)          []
    
      - nodeClassification : nc        (unicode)       []
    
      - nonExclusiveLights : nxl       (bool)          []
    
      - nonIlluminatingLights : nil    (bool)          []
    
      - parent : p                     (unicode)       []
    
      - postProcess : pp               (bool)          []
    
      - renderUtilityNode : run        (bool)          []
    
      - renderableObjectSets : ros     (bool)          []
    
      - renderingNode : rn             (bool)          []
    
      - shaders : s                    (bool)          []
    
      - text : t                       (unicode)       []
    
      - textures2d : t2d               (bool)          []
    
      - textures3d : t3d               (bool)          []
    
      - texturesProcedural : tp        (bool)          []
    
    
    Derived from mel command `maya.cmds.itemFilterRender`
    """

    pass


def displayLevelOfDetail(*args, **kwargs):
    """
    This command is responsible for setting the display level-of-detail for edit refreshes.  If enabled, objects will draw
    with lower detail based on their distance from the camera. When disabled objects will display at full resolution at all
    times.  This is not an undoable command In query mode, return type is based on queried flag.
    
    Flags:
      - levelOfDetail : lod            (bool)          []
          Enable/disable level of detail.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.displayLevelOfDetail`
    """

    pass


def displayRGBColor(*args, **kwargs):
    """
    This command changes or queries the display color for anything in the application that allows the user to set its color.
    These colors are part of the UI and not part of the saved data for a model.  This command is not undoable.
    
    Flags:
      - create : c                     (bool)          [create]
          Creates a new RGB display color which can be queried or set. If is used only when saving color preferences. name
          Specifies the name of color to change.
    
      - hueSaturationValue : hsv       (bool)          [create,query]
          Indicates that rgb values are really hsv values. Upon query, returns the HSV valuses as an array of 3 floats. r g b The
          RGB values for the color.  (Between 0-1)
    
      - list : l                       (bool)          [create]
          Writes out a list of all RGB color names and their value.
    
      - resetToFactory : rf            (bool)          [create]
          Resets all the RGB display colors to their factory defaults.
    
      - resetToSaved : rs              (bool)          [create]
          Resets all the RGB display colors to their saved values.                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.displayRGBColor`
    """

    pass


def exactWorldBoundingBox(*args, **kwargs):
    """
    This command figures out an exact-fit bounding box for the specified objects (or selected objects if none are specified)
    This bounding box is always in world space.
    
    Flags:
      - calculateExactly : ce          (bool)          []
    
      - ignoreInvisible : ii           (bool)          [create]
          Should the bounding box calculation include or exclude invisible objects?                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.exactWorldBoundingBox`
    """

    pass


def vnnConnect(*args, **kwargs):
    """
    Makes a connection between two VNN node ports. The first parameter is the full name of the DG node that contains the VNN
    graph. The next two parameters are the full path of the ports from the root of the VNN container. This command can be
    used for compound or node connections, and the parameters can be out-of-order.
    
    Flags:
      - disconnect : d                 (bool)          [create]
          delete the connection if it exists, rather than creating a new connection                  Flag can have multiple
          arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.vnnConnect`
    """

    pass


def itemFilterType(*args, **kwargs):
    """
    This command queries a named itemFilter object.  This object can be attached to selectionConnection objects, or to
    editors, in order to filter the item lists going through them.  Using union and intersection filters, complex composite
    filters can be created.
    
    Flags:
      - text : t                       (unicode)       [query,edit]
          Defines an annotation string to be stored with the filter
    
      - type : typ                     (bool)          [query]
          Query the type of the filter object. Possible return values are: itemFilter, attributeFilter, renderFilter, or
          unknownFilter.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.itemFilterType`
    """

    pass


def connectAttr(source, destination, **kwargs):
    """
    Connect the attributes of two dependency nodes and return the names of the two connected attributes. The connected
    attributes must be be of compatible types. First argument is the source attribute, second one is the destination. Refer
    to dependency node documentation.
    
    Maya Bug Fix:
      - even with the 'force' flag enabled, the command would raise an error if the connection already existed.
    
    Flags:
      - force : f                      (bool)          [create]
          Forces the connection.  If the destination is already connected, the old connection is broken and the new one made.
    
      - lock : l                       (bool)          [create]
          If the argument is true, the destination attribute is locked after making the connection. If the argument is false, the
          connection is unlocked before making the connection.
    
      - nextAvailable : na             (bool)          [create]
          If the destination multi-attribute has set the indexMatters to be false with this flag specified, a connection is made
          to the next available index. No index need be specified.
    
      - referenceDest : rd             (unicode)       [create]
          This flag is used for file io only. The flag indicates that the connection replaces a connection made in a referenced
          file, and the flag argument indicates the original destination from the referenced file. This flag is used so that if
          the reference file is modified, maya can still attempt to make the appropriate connections in the main scene to the
          referenced object.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.connectAttr`
    """

    pass


def cycleCheck(*args, **kwargs):
    """
    This command searches for plug cycles in the dependency graph. If a plug or node is selected then it searches for cycles
    that that plug or node is involved with. Plugs or nodes can also be passed as arguments. If the -all flag is used then
    the entire graph is searched. Normally the return value is a boolean indicating whether or not the given items were
    involved in a cycle.  If the -list flag is used then the return value is the list of all plugs in cycles (involving the
    selected plug or node if any). Note that it is possible for evaluation cycles to occur even where no DG connections
    exist. Here are some examples: 1) Nodes with evaluation-time dependent connections: An example is expression nodes,
    because we cannot tell what an expression node is actually referring to until it is evaluated, and such evaluation-time
    dependent nodes may behave differently based on the context (e.g. time) they are evaluated at. If you suspect a cycle
    due to such a connection, the best way to detect the cycle is through manual inspection. 2) Cycles due to DAG hierarchy:
    noting that DAG nodes are implicitely connected through parenting, if a child DAG node connects an output into the input
    of a parent node, a cycle will exist if the plugs involved also affect each other. In order to enable detection of
    cycles involving the DAG, add the -dag flag to the command line. Note also that this command may incorrectly report a
    cycle on an instanced skeleton where some of the instances use IK. You will have to examine the reported cycle yourself
    to determine if it is truly a cycle or not. The evaluation time cycle checking will not report false cycles.
    
    Flags:
      - all : all                      (bool)          [create]
          search the entire graph for cycles instead of the selection list. (Note: if nothing is selected, -all is assumed).
    
      - children : c                   (bool)          [create]
          Do not consider cycles on the children, only the specified plugs
    
      - dag : dag                      (bool)          [create]
          Also look for cycles due to relationships in the DAG. For each DAG node, the parenting connection on its children is
          also considered when searching for cycles.
    
      - evaluation : e                 (bool)          [create,query]
          Turn on and off cycle detection during graph evaluation
    
      - firstCycleOnly : fco           (bool)          [create]
          When -list is used to return a plug list, the list may contain multiple cycles or partial cycles. When -firstCycleOnly
          is specified only the first such cycle (which will be a full cycle) is returned.
    
      - firstPlugPerNode : fpn         (bool)          [create]
          When -list is used to return a plug list, the list will typically contain multiple plugs per node (e.g. ... A.output
          B.input B.output C.input ...), reflecting internal affectsrelationships rather than external DG connections. When
          -firstPlugPerNode is specified, only the first plug in the list for each node is returned (B.input in the example).
    
      - lastPlugPerNode : lpn          (bool)          [create]
          When -list is used to return a plug list, the list will typically contain multiple plugs per node (e.g. ... A.output
          B.input B.output C.input ...), reflecting internal affectsrelationships rather than external DG connections. When
          -lastPlugPerNode is specified, only the last plug in the list for each node is returned (B.output in the example).
    
      - list : l                       (bool)          [create]
          Return all plugs involved in one or more cycles.  If not specified, returns a boolean indicating whether a cycle exists.
    
      - listSeparator : ls             (unicode)       [create]
          When -list is used to return a plug list, the list may contain multiple cycles or partial cycles. Use -listSeparator to
          specify a string that will be inserted into the returned string array to separate the cycles.
    
      - parents : p                    (bool)          [create]
          Do not consider cycles on the parents, only the specified plugs
    
      - secondary : s                  (bool)          [create]
          Look for cycles on related plugs as well as the specified plugs Default is onfor the -allcase and offfor others
    
      - timeLimit : tl                 (time)          [create]
          Limit the search to the given amount of time                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.cycleCheck`
    """

    pass


def displayAffected(*args, **kwargs):
    """
    Turns on/off the special coloring of objects that are affected by the objects that are currently in the selection list.
    If one of the curves in a loft were selected and this feature were turned on, then the lofted surface would be
    highlighted because it is affected by the loft curve.
    
    
    Derived from mel command `maya.cmds.displayAffected`
    """

    pass


def uniqueObjExists(name):
    """
    Returns True if name uniquely describes an object in the scene.
    """

    pass


def disconnectAttr(source, destination=None, inputs=None, outputs=None, **kwargs):
    """
    Disconnects two connected attributes. First argument is the source attribute, second is the destination.
    
    Modifications:
      - If no destination is passed, then all inputs will be disconnected if inputs
          is True, and all outputs will be disconnected if outputs is True; if
          neither are given (or both are None), both all inputs and all outputs
          will be disconnected
    
    Flags:
      - nextAvailable : na             (bool)          [create]
          If the destination multi-attribute has set the indexMatters to be false, the command will disconnect the first matching
          connection.  No index needs to be specified.                  Flag can have multiple arguments, passed either as a tuple
          or a list.
    
    
    Derived from mel command `maya.cmds.disconnectAttr`
    """

    pass


def editDisplayLayerGlobals(*args, **kwargs):
    """
    Edit the parameter values common to all display layers.  Some of these paremeters, eg. baseId and mergeType, are stored
    as preferences and some, eg. currentDisplayLayer, are stored in the file.
    
    Flags:
      - baseId : bi                    (int)           [create,query]
          Set base layer ID.  This is the number at which new layers start searching for a unique ID.
    
      - currentDisplayLayer : cdl      (PyNode)        [create,query]
          Set current display layer; ie. the one that all new objects are added to.
    
      - mergeType : mt                 (int)           [create,query]
          Set file import merge type.  Valid values are 0, none, 1, by number, and 2, by name.
    
      - useCurrent : uc                (bool)          [create,query]
          Set whether or not to enable usage of the current display layer as the destination for all new nodes.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.editDisplayLayerGlobals`
    """

    pass


def getClassification(*args):
    """
    Returns the classification string for a given node type. Classification strings look like file pathnames
    (shader/reflectiveor texture/2D, for example).  Multiple classifications can be combined into a single compound
    classification string by joining the individual classifications with ':'. For example, the classification string
    shader/reflective:texture/2Dmeans that the node is both a reflective shader and a 2D texture. The classification string
    is used to determine how rendering nodes are categorized in various UI, such as the Create Render Node and HyperShade
    windows: CategoryClassification String2D Texturestexture/2d3D Texturestexture/3dEnv Texturestexture/environmentSurface
    Materialsshader/surfaceVolumetric Materialsshader/volumeDisplacement Materialsshader/displacementLightslightGeneral
    Utilitiesutility/generalColor Utilitiesutility/colorParticle Utilitiesutility/particleImage
    PlanesimageplaneGlowpostprocess/opticalFXThe classification string is also used to determine how Viewport 2.0 will
    interpret the node. CategoryClassification StringGeometrydrawdb/geometryTransformdrawdb/geometry/transformSub-Scene
    Objectdrawdb/subsceneShaderdrawdb/shaderSurface Shaderdrawdb/shader/surface
    
    Modifications:
      - previously returned a list with a single colon-separated string of classifications. now returns a list of classifications
    
        :rtype: `unicode` list
    
    Flags:
      - satisfies : sat                (unicode)       [create]
          Returns true if the given node type's classification satisfies the classification string which is passed with the flag.
          A non-compound classification string A is said to satisfy a non-compound classification string B if A is a
          subclassification of B (for example, shaders/reflectivesatisfies shaders). A compound classification string A satisfies
          a compound classification string B iff: every component of A satisfies at least one component of B and every component
          of B is satisfied by at least one component of AHence, shader/reflective/phong:texturesatisfies shader:texture, but
          shader/reflective/phongdoes not satisfy shader:texture.                  Flag can have multiple arguments, passed either
          as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.getClassification`
    """

    pass


def listRelatives(*args, **kwargs):
    """
    This command lists parents and children of DAG objects. The flags -c/children, -ad/allDescendents, -s/shapes, -p/parent
    and -ap/allParents are mutually exclusive. Only one can be used in a command. When listing parents of objects directly
    under the world, the command will return an empty parent list. Listing parents of objects directly under a shape
    (underworld objects) will return their containing shape node in the list of parents. Listing parents of components of
    objects will return the object. When listing children, shape nodes will return their underworld objects in the list of
    children. Listing children of components of objects returns nothing. The -ni/noIntermediate flag works with the
    -s/shapes flag. It causes any intermediate shapes among the descendents to be ignored.
    
    Maya Bug Fix:
      - allDescendents and shapes flags did not work in combination
      - noIntermediate doesn't appear to work
    
    Modifications:
      - returns an empty list when the result is None
      - returns an empty list when the arg is an empty list, tuple, set, or
            frozenset, making it's behavior consistent with when None is passed, or
            no args and nothing is selected (would formerly raise a TypeError)
      - returns wrapped classes
      - fullPath is forced on to ensure that all returned node paths are unique
    
        :rtype: `DependNode` list
    
    Flags:
      - allDescendents : ad            (bool)          [create]
          Returns all the children, grand-children etc. of this dag node.  If a descendent is instanced, it will appear only once
          on the list returned. Note that it lists grand-children before children.
    
      - allParents : ap                (bool)          [create]
          Returns all the parents of this dag node. Normally, this command only returns the parent corresponding to the first
          instance of the object
    
      - children : c                   (bool)          [create]
          List all the children of this dag node (default).
    
      - fullPath : f                   (bool)          [create]
          Return full pathnames instead of object names.
    
      - noIntermediate : ni            (bool)          [create]
          No intermediate objects
    
      - parent : p                     (bool)          [create]
          Returns the parent of this dag node
    
      - path : pa                      (bool)          [create]
          Return a proper object name that can be passed to other commands.
    
      - shapes : s                     (bool)          [create]
          List all the children of this dag node that are shapes (ie, not transforms)
    
      - type : typ                     (unicode)       [create]
          List all relatives of the specified type.                  Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.listRelatives`
    """

    pass


def displayCull(*args, **kwargs):
    """
    This command is responsible for setting the display culling property of back faces of surfaces. In query mode, return
    type is based on queried flag.
    
    Flags:
      - backFaceCulling : bfc          (bool)          [create,query]
          Enable/disable culling of back faces.                  Flag can have multiple arguments, passed either as a tuple or a
          list.
    
    
    Derived from mel command `maya.cmds.displayCull`
    """

    pass


def applyAttrPattern(*args, **kwargs):
    """
    Take the attribute structure described by a pre-defined pattern and apply it either to a node (as dynamic attributes) or
    a node type (as extension attributes). The same pattern can be applied more than once to different nodes or node types
    as the operation duplicates the attribute structure described by the pattern.  See the 'createAttrPatterns' command for
    a description of how to create a pattern.
    
    Flags:
      - nodeType : nt                  (unicode)       [create]
          Name of the node type to which the attribute pattern is to be applied. This flag will cause a new extension attribute
          tree to be created, making the new attributes available on all nodes of the given type. If it is not specified then
          either a node name must be specified or a node must be selected for application of dynamic attributes.
    
      - patternName : pn               (unicode)       [create]
          The name of the pattern to apply. The pattern with this name must have been previously created using the
          createAttrPatterns command.                               Flag can have multiple arguments, passed either as a tuple or
          a list.
    
    
    Derived from mel command `maya.cmds.applyAttrPattern`
    """

    pass


def toolPropertyWindow(*args, **kwargs):
    """
    End users should only call this command as 1. a query (in the custom tool property sheet code) or 2. with no arguments
    to create the default tool property sheet.  The more complex uses of it are internal. In query mode, return type is
    based on queried flag.
    
    Flags:
      - field : fld                    (unicode)       [query,edit]
          Sets/returns the name of the text field used to store the tool name in the property sheet.
    
      - helpButton : hb                (unicode)       [query,edit]
          Sets/returns the name of the button used to show help on the tool in the property sheet.
    
      - icon : icn                     (unicode)       [query,edit]
          Sets/returns the name of the static picture object (used to display the tool icon in the property sheet).
    
      - inMainWindow : imw             (bool)          [create]
          Specify true if you want the tool settings to appear in the main window rather than a separate window.
    
      - location : loc                 (unicode)       [query,edit]
          Sets/returns the location of the current tool property sheet, or an empty string if there is none.
    
      - noviceMode : nm                (bool)          [query,edit]
          Sets/returns the 'novice mode' flag.(unused at the moment)
    
      - resetButton : rb               (unicode)       [query,edit]
          Sets/returns the name of the button used to restore the tool settings in the property sheet.
    
      - selectCommand : sel            (unicode)       [query,edit]
          Sets/returns the property sheet's select command.
    
      - showCommand : shw              (unicode)       [query,edit]
          Sets/returns the property sheet's display command.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.toolPropertyWindow`
    """

    pass


def reorderContainer(*args, **kwargs):
    """
    This command reorders (moves) objects relative to their siblings in a container. For relative moves, both positive and
    negative numbers may be specified.  Positive numbers move the object forward and negative numbers move the object
    backward amoung its siblings. When an object is at the end (beginning) of the list of siblings, a relative move of 1
    (-1) will put the object at the beginning (end) of the list of siblings.  That is, relative moves will wrap if
    necessary. Only nodes within one container can be moved at a time. Note: The container command's -nodeList flag will
    return a sorted list of contained nodes. To see the effects of reordering, use the -unsortedOrder flag in conjunction
    with the -nodeList flag.                 In query mode, return type is based on queried flag.
    
    Flags:
      - back : b                       (bool)          [create,query,edit]
          Move object(s) to back of container contents list
    
      - front : f                      (bool)          [create,query,edit]
          Move object(s) to front of container contents list
    
      - relative : r                   (int)           [create,query,edit]
          Move object(s) relative to other container contents                                Flag can have multiple arguments,
          passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.reorderContainer`
    """

    pass


def getAttr(attr, default=None, **kwargs):
    """
    This command returns the value of the named object's attribute. UI units are used where applicable. Currently, the types
    of attributes that can be displayed are: numeric attributesstring attributesmatrix attributesnumeric compound attributes
    (whose children are all numeric)vector array attributesdouble array attributesint32 array attributespoint array
    attributesdata component list attributesOther data types cannot be retrieved. No result is returned if the attribute
    contains no data.
    
    Maya Bug Fix:
      - maya pointlessly returned vector results as a tuple wrapped in a list ( ex.  '[(1,2,3)]' ). This command unpacks the vector for you.
    
    Modifications:
      - casts double3 datatypes to `Vector`
      - casts matrix datatypes to `Matrix`
      - casts vectorArrays from a flat array of floats to an array of Vectors
      - when getting a multi-attr, maya would raise an error, but pymel will return a list of values for the multi-attr
      - added a default argument. if the attribute does not exist and this argument is not None, this default value will be returned
      - added support for getting message attributes
    
    Flags:
      - asString : asString            (bool)          [create]
          This flag is only valid for enum attributes. It allows you to get the attribute values as strings instead of integer
          values. Note that the returned string value is dependent on the UI language Maya is running in (about -uiLanguage).
    
      - caching : ca                   (bool)          [create]
          Returns whether the attribute is set to be cached internally
    
      - channelBox : cb                (bool)          [create]
          Returns whether the attribute is set to show in the channelBox. Keyable attributes also show in the channel box.
    
      - expandEnvironmentVariables : x (bool)          [create]
          Expand any environment variable and (tilde characters on UNIX) found in string attributes which are returned.
    
      - keyable : k                    (bool)          [create]
          Returns the keyable state of the attribute.
    
      - lock : l                       (bool)          [create]
          Returns the lock state of the attribute.
    
      - multiIndices : mi              (bool)          [create]
          If the attribute is a multi, this will return a list containing all of the valid indices for the attribute.
    
      - settable : se                  (bool)          [create]
          Returns 1 if this attribute is currently settable by setAttr, 0 otherwise. An attribute is settable if it's not locked
          and either not connected, or has only keyframed animation.
    
      - silent : sl                    (bool)          [create]
          When evaluating an attribute that is not a numeric or string value, suppress the error message saying that the data
          cannot be displayed. The attribute will be evaluated even though its data cannot be displayed. This flag does not
          suppress all error messages, only those that are benign.
    
      - size : s                       (bool)          [create]
          Returns the size of a multi-attribute array.  Returns 1 if non-multi.
    
      - time : t                       (time)          [create]
          Evaluate the attribute at the given time instead of the current time.
    
      - type : typ                     (bool)          [create]
          Returns the type of data currently in the attribute. Attributes of simple types such as strings and numerics always
          contain data, but attributes of complex types (arrays, meshes, etc) may contain no data if none has ever been assigned
          to them. When this happens the command will return with no result: not an empty string, but no result at all. Attempting
          to directly compare this non-result to another value or use it in an expression will result in an error, but you can
          assign it to a variable in which case the variable will be set to the default value for its type (e.g. an empty string
          for a string variable, zero for an integer variable, an empty array for an array variable). So to be safe when using
          this flag, always assign its result to a string variable, never try to use it directly.                   Flag can have
          multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.getAttr`
    """

    pass


def softSelect(*args, **kwargs):
    """
    This command allows you to change the soft modelling options. Soft modelling is an option that allows for reflection of
    basic manipulator actions such as move, rotate, and scale. In query mode, return type is based on queried flag.
    
    Flags:
      - compressUndo : cu              (int)           [create,query,edit]
          Controls how soft selection settings behave in undo: 0 means all changes undo individually1 means all consecutive
          changes undo as a group2 means only interactive changes undo as a groupWhen queried, returns an int indicating the
          current undo behaviour.
    
      - enableFalseColor : efc         (int)           [create,query,edit]
          Set soft select color feedback on or off. When queried, returns an int indicating whether color feedback is currently
          enabled.
    
      - softSelectColorCurve : scc     (unicode)       [create,query,edit]
          Sets the color ramp used to display false color feedback for soft selected components in the viewport. The color curve
          is encoded as a string of comma separated floating point values representing the falloff curve CVs. Each CV is
          represented by 5 successive values: 3 RGB values (the color to use), an input value (the selection weight), and a curve
          interpolation type. When queried, returns a string containing the encoded CVs of the current color feedback curve.
    
      - softSelectCurve : ssc          (unicode)       [create,query,edit]
          Sets the falloff curve used to calculate selection weights for components within the falloff distance. The curve is
          encoded as a string of comma separated floating point values representing the falloff curve CVs. Each CV is represented
          by 3 successive values: an output value (the selection weight at this point), an input value (the normalised falloff
          distance) and a curve interpolation type. When queried, returns a string containing the encoded CVs of the current
          falloff curve.
    
      - softSelectDistance : ssd       (float)         [create,query,edit]
          Sets the falloff distance (radius) used for world and object space soft selection. When queried, returns a float
          indicating the current falloff distance.
    
      - softSelectEnabled : sse        (int)           [create,query,edit]
          Sets soft selection based modeling on or off. When queried, returns an int indicating the current state of the option.
    
      - softSelectFalloff : ssf        (int)           [create,query,edit]
          Sets the falloff mode: 0 for volume based falloff1 for surface based falloff2 for global falloffWhen queried, returns an
          int indicating the falloff mode.
    
      - softSelectReset : ssr          (bool)          [create,edit]
          Resets soft selection to its default settings.
    
      - softSelectUVDistance : sud     (float)         [create,query,edit]
          Sets the falloff distance (radius) used for UV space soft selection. When queried, returns a float indicating the
          current falloff distance.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.softSelect`
    """

    pass


def validComponentIndexType(argObj, allowDicts=True, componentIndexTypes=None):
    """
    True if argObj is of a suitable type for specifying a component's index.
    False otherwise.
    
    Dicts allow for components whose 'mel name' may vary - ie, a single
    isoparm component may have, u, v, or uv elements; or, a single pivot
    component may have scalePivot and rotatePivot elements.  The key of the
    dict would indicate the 'mel component name', and the value the actual
    indices.
    
    Thus:
       {'u':3, 'v':(4,5), 'uv':ComponentIndex((1,4)) }
    would represent single component that contained:
       .u[3]
       .v[4]
       .v[5]
       .uv[1][4]
    
    Derived classes should implement:
    _dimLength
    """

    pass


def sets(*args, **kwargs):
    """
    This command is used to create a set, query some state of a set, or perform operations to update the membership of a
    set. A set is a logical grouping of an arbitrary collection of objects, attributes, or components of objects. Sets are
    dependency nodes. Connections from objects to a set define membership in the set. Sets are used throughout Maya in a
    multitude of ways. They are used to define an association of material properties to objects, to define an association of
    lights to objects, to define a bookmark or named collection of objects, to define a character, and to define the
    components to be deformed by some deformation operation. Sets can be connected to any number of partitions. A partition
    is a node which enforces mutual exclusivity amoung the sets in the partition. That is, if an object is in a set which is
    in a partition, that object cannot be a member of any other set that is in the partition. Without any flags, the
    setscommand will create a set with a default name of set#(where # is an integer). If no items are specified on the
    command line, the currently selected items are added to the set. The -em/empty flag can be used to create an empty set
    and not have the selected items added to the set. Sets can be created to have certain restrictions on membership. There
    can be renderablesets which only allow renderable objects (such as nurbs geometry or polymesh faces) to be members of
    the set. There can also be vertex (or control point), edit point, edge, or face sets which only allow those types of
    components to be members of a set. Note that for these sets, if an object with a valid type of component is to be added
    to a set, the components of the object are added to the set instead. Sets can have an associated color which is only of
    use when creating vertex sets. The color can be one of the eight user defined colors defined in the color preferences.
    This color can be used, for example to distinguish which vertices are being deformed by a particular deformation.
    Objects, components, or attributes can be added to a set using one of three flags. The -add/addElement flag will add the
    objects to a set as long as this won't break any mutual exclusivity constraints. If there are any items which can't be
    added, the command will fail. The -in/include flag will only add those items which can be added and warn of those which
    can't. The -fe/forceElement flag will add all the items to the set but will also remove any of those items that are in
    any other set which is in the same partition as the set. There are several operations on sets that can be performed with
    the setscommand. Membership can be queried. Tests for whether an item is in a set or whether two sets share the same
    item can be performed. Also, the union, intersection and difference of sets can be performed which returns a list of
    members of the sets which are a result of the operation.
    
    Modifications
      - resolved confusing syntax: operating set is always the first and only arg:
    
            >>> from pymel.core import *
            >>> f=newFile(f=1) #start clean
            >>>
            >>> shdr, sg = createSurfaceShader( 'blinn' )
            >>> shdr
            nt.Blinn(u'blinn1')
            >>> sg
            nt.ShadingEngine(u'blinn1SG')
            >>> s,h = polySphere()
            >>> s
            nt.Transform(u'pSphere1')
            >>> sets( sg, forceElement=s ) # add the sphere
            nt.ShadingEngine(u'blinn1SG')
            >>> sets( sg, q=1)  # check members
            [nt.Mesh(u'pSphereShape1')]
            >>> sets( sg, remove=s )
            nt.ShadingEngine(u'blinn1SG')
            >>> sets( sg, q=1)
            []
    
      - returns wrapped classes
    
    Flags:
      - addElement : add               (PyNode)        [edit]
          Adds the list of items to the given set.  If some of the items cannot be added to the set because they are in another
          set which is in the same partition as the set to edit, the command will fail.
    
      - afterFilters : af              (bool)          [edit]
          Default state is false. This flag is valid in edit mode only. This flag is for use on sets that are acted on by
          deformers such as sculpt, lattice, blendShape. The default edit mode is to edit the membership of the group acted on by
          the deformer. If you want to edit the group but not change the membership of the deformer, set the flag to true.
    
      - clear : cl                     (PyNode)        [edit]
          An operation which removes all items from the given set making the set empty.
    
      - color : co                     (int)           [create,query,edit]
          Defines the hilite color of the set. Must be a value in range [-1, 7] (one of the user defined colors).  -1 marks the
          color has being undefined and therefore not having any affect. Only the vertices of a vertex set will be displayed in
          this color.
    
      - copy : cp                      (PyNode)        [create]
          Copies the members of the given set to a new set. This flag is for use in creation mode only.
    
      - edges : eg                     (bool)          [create,query]
          Indicates the new set can contain edges only. This flag is for use in creation or query mode only. The default value is
          false.
    
      - editPoints : ep                (bool)          [create,query]
          Indicates the new set can contain editPoints only. This flag is for use in creation or query mode only. The default
          value is false.
    
      - empty : em                     (bool)          [create]
          Indicates that the set to be created should be empty. That is, it ignores any arguments identifying objects to be added
          to the set. This flag is only valid for operations that create a new set.
    
      - facets : fc                    (bool)          [create,query]
          Indicates the new set can contain facets only. This flag is for use in creation or query mode only. The default value is
          false.
    
      - flatten : fl                   (PyNode)        [edit]
          An operation that flattens the structure of the given set. That is, any sets contained by the given set will be replaced
          by its members so that the set no longer contains other sets but contains the other sets' members.
    
      - forceElement : fe              (PyNode)        [edit]
          For use in edit mode only. Forces addition of the items to the set. If the items are in another set which is in the same
          partition as the given set, the items will be removed from the other set in order to keep the sets in the partition
          mutually exclusive with respect to membership.
    
      - include : include              (PyNode)        [edit]
          Adds the list of items to the given set.  If some of the items cannot be added to the set, a warning will be issued.
          This is a less strict version of the -add/addElement operation.
    
      - intersection : int             (PyNode)        [create]
          An operation that returns a list of items which are members of all the sets in the list.
    
      - isIntersecting : ii            (PyNode)        [create]
          An operation which tests whether the sets in the list have common members.
    
      - isMember : im                  (PyNode)        [create]
          An operation which tests whether all the given items are members of the given set.
    
      - layer : l                      (bool)          [create]
          OBSOLETE. DO NOT USE.
    
      - name : n                       (unicode)       [create]
          Assigns string as the name for a new set. This flag is only valid for operations that create a new set.
    
      - noSurfaceShader : nss          (bool)          [create]
          If set is renderable, do not connect it to the default surface shader.  Flag has no meaning or effect for non renderable
          sets. This flag is for use in creation mode only. The default value is false.
    
      - noWarnings : nw                (bool)          [create]
          Indicates that warning messages should not be reported such as when trying to add an invalid item to a set. (used by UI)
    
      - nodesOnly : no                 (bool)          [query]
          This flag is usable with the -q/query flag but is ignored if used with another queryable flags. This flag modifies the
          results of the set membership query such that when there are attributes (e.g. sphere1.tx) or components of nodes
          included in the set, only the nodes will be listed. Each node will only be listed once, even if more than one attribute
          or component of the node exists in the set.
    
      - remove : rm                    (PyNode)        [edit]
          Removes the list of items from the given set.
    
      - renderable : r                 (bool)          [create,query]
          This flag indicates that a special type of set should be created. This type of set (shadingEngine as opposed to
          objectSet) has certain restrictions on its membership in that it can only contain renderable elements such as lights and
          geometry. These sets are referred to as shading groups and are automatically connected to the renderPartitionnode when
          created (to ensure mutual exclusivity of the set's members with the other sets in the partition). This flag is for use
          in creation or query mode only. The default value is false which means a normal set is created.
    
      - size : s                       (bool)          [query]
          Use the size flag to query the length of the set.
    
      - split : sp                     (PyNode)        [create]
          Produces a new set with the list of items and removes each item in the list of items from the given set.
    
      - subtract : sub                 (PyNode)        [create]
          An operation between two sets which returns the members of the first set that are not in the second set.
    
      - text : t                       (unicode)       [create,query,edit]
          Defines an annotation string to be stored with the set.
    
      - union : un                     (PyNode)        [create]
          An operation that returns a list of all the members of all sets listed.
    
      - vertices : v                   (bool)          [create,query]
          Indicates the new set can contain vertices only. This flag is for use in creation or query mode only. The default value
          is false.                  Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.sets`
    """

    pass


def _MPlugOut(self, x):
    pass


def vnnCompound(*args, **kwargs):
    """
    The vnnCompoundcommand is used to operate compound and its VNN graph. The first parameter is the full name of the DG
    node that contains the VNN graph. The second parameter is the name of the compound.
    
    Flags:
      - addNode : an                   (unicode)       [create]
          Add a node into the compound.
    
      - addStatePortUI : spu           (bool)          [create]
          Pop up a window to add iteration state port.
    
      - canResetToFactory : crf        (unicode)       [create]
          Query if the specified compound can be reset to its initial status.
    
      - connected : cn                 (bool)          [create]
          Used with listNodesor listPortsto query the nodes or internal ports that have connections when the argument is true. If
          the arguments is false, return all nodes which have no connection. The other side of the connection could be another
          node or port.
    
      - connectedTo : ct               (unicode)       [create]
          Used with listNodesto query all nodes that connect to the specified ports.
    
      - connectedToInput : cti         (bool)          [create]
          Used with listNodesto query all nodes which connect to any input ports.
    
      - connectedToOutput : cto        (bool)          [create]
          Used with listNodesto query all nodes that connect to any output ports.
    
      - create : c                     (unicode)       [create]
          Create a sub compound in the specified compound. The name of the created sub compound cannot be used before in the
          specified compound.
    
      - createInputPort : cip          (unicode, unicode) [create]
          Create an input port in the compound. The first argument is the name of the port. The second argument is the data type
          of the port.
    
      - createOutputPort : cop         (unicode, unicode) [create]
          Create an output port in the compound. The first argument is the name of the port. The second argument is the data type
          of the port.
    
      - deletePort : dp                (unicode)       [create]
          Delete a input or output port from the compound.
    
      - explode : ec                   (unicode)       [create]
          Explode a specified compound and move the nodes from it to its parent.
    
      - inputPort : ip                 (bool)          [create]
          Used with listPortsto query all internal ports which connect to any input ports in the compound.
    
      - listNodes : ln                 (bool)          [create]
          List all nodes in the compound. Can be used with other flags, such as dataType, connectedToInputto query some specified
          nodes. The returned result is a list of node names.
    
      - listPortChildren : lpc         (unicode)       [create]
          List the children of specified port.
    
      - listPorts : lp                 (bool)          [create]
          List all internal ports in the compound, including input and output ports. Can be used with other flags, such as output,
          connectedto query some specified ports.
    
      - moveNodeIn : mi                (unicode)       [create]
          Move the specified node into the compound.
    
      - movePort : mp                  (unicode, int)  [create]
          Move a port to the specified index in the compound
    
      - nodeType : nt                  (unicode)       [create]
          Used with listNodesto query all nodes which are specified node type in the compound.
    
      - outputPort : op                (bool)          [create]
          Used with listPortsto query all nodes which connect to any output ports in the compound.
    
      - portDefaultValue : pdv         (unicode, unicode) [create]
          Set the default value to a specified port The port cannot be connected.
    
      - publish : pub                  (unicode, unicode, unicode, bool) [create]
          Used to publish the compound. The arguments are, in order, the file path where to save, the namespace where to store the
          compound, the name to use for the nodedef and whether or not the compound should be referenced upon publishing.
    
      - queryIsImported : qii          (bool)          [create]
          Query if the compound is imported.
    
      - queryIsReferenced : qir        (bool)          [create]
          Query if the compound is referenced.
    
      - queryMetaData : qmd            (unicode)       [create]
          Query the value(s) of a metadata.
    
      - queryPortDataType : qpt        (unicode)       [create]
          Query the data type of a specified port.
    
      - queryPortDefaultValue : qpv    (unicode)       [create]
          Query the default value of a specified port
    
      - queryPortMetaDataValue : qpm   (unicode, unicode) [create]
          Query the metadata value of a specified port. The first argument is the port to query, the second is the type of
          metadata to query.
    
      - removeNode : rmn               (unicode)       [create]
          Remove the specified node from the compound.
    
      - renameNode : rn                (unicode, unicode) [create]
          Rename a node in the compound. The first argument is the old name of the node. The second argument is the new name.
    
      - renamePort : rp                (unicode, unicode) [create]
          Rename a port of the compound. The first argument is the old name of the port. The second argument is the new name.
    
      - resetToFactory : rtf           (unicode)       [create]
          Reset the specified compound to its initial status. The specified compound must be able to be reset.
    
      - saveAs : sa                    (unicode)       [create]
          Used to export Compound in the Compound menu of the Node Editor. The argument is the file path to save.
    
      - setIsReferenced : sir          (bool)          [create]
          Change the referenced status of the compound. If -sir/setIsReferencedis true, the compound will be made public, else the
          compound will be made private to its parent compound.
    
      - setMetaData : smd              (unicode, unicode) [create]
          Set the value of a metatada. The arguments are, in order, metadata name, metadata value to be set.
    
      - setPortDataType : spt          (unicode, unicode) [create]
          Set the data type of a specified compound port.
    
      - setPortMetaDataValue : spm     (unicode, unicode, unicode) [create]
          Set the metadata value of a specified compound port. The arguments are, in order, port name, metadata name, metadata
          value to be set.
    
      - specializedTypeName : stn      (bool)          [create]
          Used to query the specialized implementation class names such as Bifrost_DoWhile, or Compoundfor a normal compound
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.vnnCompound`
    """

    pass


def toggleAxis(*args, **kwargs):
    """
    Toggles the state of the display axis. Note: the display of the axis in the bottom left corner has been rendered
    obsolete by the headsUpDisplay command.
    
    Flags:
      - origin : o                     (bool)          [create,query]
          Turns display of the axis at the origin of the ground plane on or off.
    
      - view : v                       (bool)          [create,query]
          Turns display of the axis at the bottom left of each view on or off. (Obsolete - refer to the headsUpDisplay command)
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.toggleAxis`
    """

    pass


def objExists(*args, **kwargs):
    """
    This command simply returns true or false depending on whether an object with the given name exists.
    
    
    Derived from mel command `maya.cmds.objExists`
    """

    pass


def affectedNet(*args, **kwargs):
    """
    This command gets the list of attributes on a node or node type and creates nodes of type TdnAffect, one for each
    attribute, that are connected iff the source node's attribute affects the destination node's attribute. In query mode,
    return type is based on queried flag.
    
    Flags:
      - name : n                       (unicode)       []
    
      - type : t                       (unicode)       [create]
          Get information from the given node type instead of one node                  Flag can have multiple arguments, passed
          either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.affectedNet`
    """

    pass


def colorManagementFileRules(*args, **kwargs):
    """
    This non-undoable action manages the list of rules that Maya uses to assign an initial input color space to dependency
    graph nodes that read in color information from a file.  Rules are structured in a chain of responsibility, from highest
    priority rule to lowest priority rule, each rule matching a file path pattern and extension.  If a rule matches a given
    file path, its color space is returned as the result of rules evaluation, and no further rule is considered.  The lowest
    priority rule will always return a match. Rules can be added, removed, and changed in priority in the list.  Each rule
    can have its file path pattern, extension, and color space changed. The rule list can be saved to user preferences, and
    loaded from user preferences.            In query mode, return type is based on queried flag.
    
    Flags:
      - addRule : add                  (unicode)       [create,edit]
          Add a rule with the argument name to the list of rules, as the highest-priority rule.  If this flag is used, the
          pattern, extension, and colorSpace flags must be used as well, to specify the file rule pattern, extension, and color
          space, respectively.
    
      - colorSpace : cs                (unicode)       [create,query,edit]
          The input color space for the rule.  If the rule matches a file path, this is the color space that is returned.  This
          color space must match an existing color space in the input color space list.
    
      - down : dwn                     (unicode)       [create,edit]
          Move the rule with the argument name down one position towards lower priority.
    
      - evaluate : ev                  (unicode)       [create,edit]
          Evaluates the list of rules and returns the input color space name that corresponds to the argument file path.
    
      - extension : ext                (unicode)       [create,query,edit]
          The file extension for the rule, expressed as a glob pattern: for example, '\*' matches all extensions.  For more
          information about glob pattern syntax, see http://en.wikipedia.org/wiki/Glob_%28programming%29.
    
      - listRules : lsr                (bool)          [create,edit]
          Returns an array of rule name strings, in order, from lowest-priority (rule 0) to highest-priority (last rule in array).
    
      - load : ld                      (bool)          [create,edit]
          Read the rules from Maya preferences.  Any existing rules are cleared.
    
      - moveUp : up                    (unicode)       [create,edit]
          Move the rule with the argument name up one position towards higher priority.
    
      - pattern : pat                  (unicode)       [create,query,edit]
          The file path pattern for the rule.  This is the substring to match in the file path, expressed as a glob pattern: for
          example, '\*' matches all files. For more information about glob pattern syntax, see
          http://en.wikipedia.org/wiki/Glob_%28programming%29.
    
      - remove : rm                    (unicode)       [create,edit]
          Remove the rule with the argument name from the list of rules.
    
      - save : sav                     (bool)          [create,edit]
          Save the rules to Maya preferences.                                Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.colorManagementFileRules`
    """

    pass


def selected(**kwargs):
    """
    ls -sl
    """

    pass


def spaceLocator(*args, **kwargs):
    """
    The command creates a locator at the specified position in space. By default it is created at (0,0,0).
    
    Modifications:
            - returns a single Transform instead of a list with a single locator
    
    Flags:
      - absolute : a                   (bool)          [create,edit]
          If set, the locator's position is in world space.
    
      - name : n                       (unicode)       [create,edit]
          Name for the locator.
    
      - position : p                   (float, float, float) [create,query,edit]
          Location in  3-dimensional space where locator is to be created.
    
      - relative : r                   (bool)          [create,edit]
          If set, the locator's position is relative to its local space. The locator is created in relative mode by default.
          Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.spaceLocator`
    """

    pass


def editDisplayLayerMembers(*args, **kwargs):
    """
    This command is used to query and edit membership of display layers.  No equivalent 'remove' command is necessary since
    all objects must be in exactly one display layer.  Removing an object from a layer can be accomplished by adding it to a
    different layer.
    
    Flags:
      - fullNames : fn                 (bool)          [query]
          (Query only.) If set then return the full DAG paths of the objects in the layer.  Otherwise return just the name of the
          object.
    
      - noRecurse : nr                 (bool)          [create,query]
          If set then only add selected objects to the display layer.  Otherwise all descendants of the selected objects will also
          be added.                                 Flag can have multiple arguments, passed either as a tuple or a list.
    
    
    Derived from mel command `maya.cmds.editDisplayLayerMembers`
    """

    pass


def assignCommand(*args, **kwargs):
    """
    This command allows the user to assign hotkeys and manipulate the internal array of named command objects. Each object
    in the array has an 1-based index which is used for referencing. Under expected usage you should not need to use this
    command directly as the Hotkey Editor may be used to assign hotkeys. This command is obsolete for setting new hotkeys,
    instead please use the hotkeycommand. In query mode, return type is based on queried flag.
    
    Flags:
      - addDivider : ad                (unicode)       [edit]
          Appends an annotated divideritem to the end of the list of commands.
    
      - altModifier : alt              (bool)          [edit]
          This flag specifies if an alt modifier is used for the key.
    
      - annotation : ann               (unicode)       [query,edit]
          The string is the english name describing the command.
    
      - command : c                    (script)        [query,edit]
          This is the command that is executed when this object is mapped to a key or menuItem.
    
      - commandModifier : cmd          (bool)          [edit]
          This flag specifies if a command modifier is used for the key. This is only available on systems which support a
          separate command key.
    
      - ctrlModifier : ctl             (bool)          [edit]
          This flag specifies if a ctrl modifier is used for the key.
    
      - data1 : da1                    (unicode)       [query,edit]
          Optional, user-defined data strings may be attached to the nameCommand objects.
    
      - data2 : da2                    (unicode)       [query,edit]
          Optional, user-defined data strings may be attached to the nameCommand objects.
    
      - data3 : da3                    (unicode)       [query,edit]
          Optional, user-defined data strings may be attached to the nameCommand objects.
    
      - delete : d                     (int)           [edit]
          This tells the Manager to delete the object at position index.
    
      - dividerString : ds             (unicode)       [query]
          If the passed index corresponds to a divideritem, then the divider's annotation is returned.  Otherwise, a null string
          is returned.
    
      - enableCommandRepeat : ecr      (bool)          []
    
      - factorySettings : fs           (bool)          [edit]
          This flag sets the manager back to factory settings.
    
      - index : i                      (int)           [edit]
          The index of the object to operate on. The index value ranges from 1 to the number of name command objects.
    
      - keyArray : ka                  (bool)          []
    
      - keyString : k                  (unicode)       [query,edit]
          This specifies a key to assign a command to in edit mode. In query mode this flag returns the key string, modifiers and
          indicates if the command is mapped to keyUp or keyDown.
    
      - keyUp : kup                    (bool)          [edit]
          This flag specifies if the command is executed on keyUp or keyDown.
    
      - name : n                       (bool)          [query]
          The name of the command object.
    
      - numDividersPreceding : ndp     (int)           [query]
          If the index of a namedCommand object Cis passed in, then this flag returns the number of divideritems preceding Cwhen
          the namedCommands are sorted by category.
    
      - numElements : num              (bool)          [query]
          This command returns the number of namedCommands in the system. This flag doesn't require the index to be specified.
    
      - optionModifier : opt           (bool)          [edit]
          This flag specifies if an option modifier is used for the key.
    
      - sortByKey : sbk                (bool)          [query,edit]
          This key tells the manager to sort by key or by order of creation.
    
      - sourceUserCommands : suc       (bool)          [edit]
          This command sources the user named command file.                  Flag can have multiple arguments, passed either as a
          tuple or a list.
    
    
    Derived from mel command `maya.cmds.assignCommand`
    """

    pass



CHECK_ATTR_BEFORE_LOCK = False

deprecated_str_methods = []

with_statement = None

SCENE = Scene()

_logger = None


