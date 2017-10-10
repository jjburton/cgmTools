"""
The render setup node is the main entry point for the render setup
system.  Render setup is a singleton that manages a list of render
layers, each one of which can have different overrides to
non-destructively change the scene.

The data model for render setup is the following:

- A render setup singleton node, which has a list of render layers.
- Each render layer has a list of collections, and an optional list of 
  overrides.
- Each collection has a selector, a list of overrides, and an optional 
  list of child collections.

A render setup can also be imported and exported, to be shared between
different scenes.
"""

from collections import deque

class _Subject(object):
    """
    Subject class to observe overall render setup behavior.
    
    The renderSetup._Subject class is observed for render setup creation,
    deletion, and other overall events.  See
    
    https://en.wikipedia.org/wiki/Observer_pattern
    
    for more information on the Observer pattern.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def addObserver(self, obs):
        """
        Add a render setup observer.
        
        Observers are kept as weak references.  The order in which
        observers are called is unspecified.
        """
    
        pass
    
    
    def clearObservers(self):
        pass
    
    
    def finalize(self):
        pass
    
    
    def removeObserver(self, obs):
        """
        Remove an observer from this list.
        
        Observers are kept as weak references.  ValueError is raised by the 
        remove listItem method if the argument observer is not found.
        """
    
        pass
    
    
    def renderSetupAdded(self):
        """
        Call the renderSetupAdded() methods on render setup observers.
        
        The order in which observers are called is not specified.
        """
    
        pass
    
    
    def renderSetupPreDelete(self):
        """
        Call the renderSetupPreDelete() methods on render setup observers.
        
        The order in which observers are called is not specified.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class _MPxNode(object):
    """
    Base class for user defined dependency nodes.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def addExternalContentForFileAttr(*args, **kwargs):
        """
        addExternalContentForFileAttr(table, attr) -> bool
        
        This method is a helper for derived clases implementing getExternalContent().  It augments the external content info table passed in with an entry describing external content whose location is described by the specified attribute.
        
        The method will not overwrite existing items, i.e. items with the same key. (attribute name).  In this context, overwriting an item means the caller has called this function twice with the same attribute, or that two separate but identically named attributes were used.  If replacing an entry is the desired effect, it is the caller's responsibility to erase the previous item first.
        
        * table [OUT] (MExternalContentInfoTable) - table The table in which the new entry will be added.
        * attr (MObject) - The attribute for which the plug value will be queried for a location.
        
        Returns True if an item was sucessfully added to the table.  False if the attribute does not describe a non-empty location, or an item with the same key was already present in the table.
        """
    
        pass
    
    
    def compute(*args, **kwargs):
        """
        compute(plug, dataBlock) -> self
        
        This method should be overridden in user defined nodes.
        
        Recompute the given output based on the nodes inputs.  The plug represents the data value that needs to be recomputed, and the data block holds the storage for all of the node's attributes.
        
        The MDataBlock will provide smart handles for reading and writing this node's attribute values.  Only these values should be used when performing computations.
        
        When evaluating the dependency graph, Maya will first call the compute method for this node.  If the plug that is provided to the compute indicates that that the attribute was defined by the Maya parent node, the compute method should return None.  When this occurs, Maya will call the internal Maya node from which the user-defined node is derived to compute the plug's value.
        
        This means that a user defined node does not need to be concerned with computing inherited output attributes.  However, if desired, these can be safely recomputed by this method to change the behaviour of the node.
        
        * plug (MPlug) - plug representing the attribute that needs to be recomputed.
        * block (MDataBlock) - data block containing storage for the node's attributes.
        """
    
        pass
    
    
    def connectionBroken(*args, **kwargs):
        """
        connectionBroken( plug, otherPlug, asSrc) -> self
        
        This method gets called when connections are broken with attributes of this node.
        
        * plug (MPlug) - attribute on this node.
        * otherPlug (MPlug) - attribute on other node.
        * asSrc (bool) - is this plug a source of the connection.
        """
    
        pass
    
    
    def connectionMade(*args, **kwargs):
        """
        connectionMade(plug, otherPlug, asSrc) -> self
        
        This method gets called when connections are made to attributes of this node.
        
        * plug (MPlug) - attribute on this node.
        * otherPlug (MPlug) - attribute on other node.
        * asSrc (bool) - is this plug a source of the connection.
        """
    
        pass
    
    
    def copyInternalData(*args, **kwargs):
        """
        copyInternalData(node) -> self
        
        This method is overriden by nodes that store attribute data in some internal format.
        
        On duplication this method is called on the duplicated node with the node being duplicated passed as the parameter.  Overriding this method gives your node a chance to duplicate any internal data you've been storing and manipulating outside of normal attribute data.
        
        * node (MPxNode) - the node that is being duplicated.
        """
    
        pass
    
    
    def dependsOn(*args, **kwargs):
        """
        dependsOn( plug, otherPlug) -> bool/None
        
        This method may be overridden by the user defined node. It should only be required to override this on rare occasions.
        
        This method determines whether a specific attribute depends on another attribute.
        
        You should return None to specify that Maya should determines the dependency (default).
        
        This is mainly to define dependency of dynamic attributes, since attributeAffects does not work with dynamic attributes.
        
        * plug (MPlug) - attribute on this node.
        * otherPlug (MPlug) - attribute on other node.
        """
    
        pass
    
    
    def doNotWrite(*args, **kwargs):
        """
        doNotWrite() -> bool
        
        use this method to query the "do not write" state of this proxy node. True is returned if this node will not be saved when the maya model is written out.
        """
    
        pass
    
    
    def forceCache(*args, **kwargs):
        """
        forceCache(ctx=fsNormal) -> MDataBlock
        
        Get the datablock for this node. If there is no datablock then one will be created.
        NOTE: This should be used only in places where fast access to the datablock outside of a compute is critical such as the transformUsing method of MPxSurfaceShape.
        
        * ctx (MDGContext) - The context in which the node will evaluate.
        """
    
        pass
    
    
    def getExternalContent(*args, **kwargs):
        """
        getExternalContent(table) -> self
        
        The table populated by this method must include the location of all the content (files) used by this node, including those that do not exist.  See MExternalContentInfoTable for details.
        
        Keys used to add items to this table will be the same that get passed to setExternalContent through its MExternalContentLocationTable parameter to perform a batched change of content location.
        
        When implementing getExternalContent, you are responsible for forwarding the call to the base class when it makes sense to do so, so that base classes  can also add their external content to the table.
        
        The default implementation does nothing.
        
        * table [OUT] (MExternalContentInfoTable) - Content information table that this method must populate.
        """
    
        pass
    
    
    def getFilesToArchive(*args, **kwargs):
        """
        getFilesToArchive(shortName=False, unresolvedName=False, markCouldBeImageSequence=False) -> list of strings
        
        Use this method to return all external files used by this node. This file list will be used by the File > Archive zip feature, maya.exe -archive and the `file -q -list` mel command.
        
        Only include files that exist.
        
        If shortName is True, return just the filename portion of the path. Otherwise, return a full path.
        
        If unresolvedName is True, return the path before any resolution has been done (i.e leave it as a relative path, include unexpanded environment variables,  tildes, ".."s etc). Otherwise, resolve the file     path and return an absolute path (to resolve with standard Maya path resolution, use MFileObject.resolvedFullName()).
        
        * shortName (bool) - If True, only add the filename of the path.
        * unresolvedName (bool) - If True, add paths before any resolution, rather than absolute paths.
        * markCouldBeImageSequence (bool) - If True, append an asterisk after any file path that could be an image sequence (note: only used by maya.exe -archive).
        """
    
        pass
    
    
    def getInternalValueInContext(*args, **kwargs):
        """
        getInternalValueInContext(plug, dataHandle, ctx) -> bool
        
        This method is overriden by nodes that store attribute data in some internal format.
        
        The internal state of attributes can be set or queried using the setInternal and internal methods of MFnAttribute.
        
        When internal attribute values are queried via getAttr or MPlug.getValue() this method is called.
        
        * plug (MPlug) - the attribute that is being queried.
        * dataHandle [OUT] (MDataHandle) - the dataHandle to store the attribute value.
        * ctx (MDGContext) - the context the method is being evaluated in.
        """
    
        pass
    
    
    def internalArrayCount(*args, **kwargs):
        """
        internalArrayCount(plug, ctx) -> int
        
        This method is overriden by nodes that have internal array attributes which are not stored in Maya's datablock. This method is used by Maya to determine the non-sparse count of array elements during file io. If the internal array is stored sparsely, you should return the maximum index of the array plus one. If the internal array is non-sparse then return the length of the array.
        
        This method does not need to be implemented for attributes that are stored in the datablock since Maya will use the datablock size.
        
        If this method is overriden, it should return -1 for attributes which it does not handle. Maya will use the datablock size to determine the array length when -1 is returned.
        
        * plug (MPlug) - the array plug.
        * ctx (MDGContext) - the context.
        """
    
        pass
    
    
    def isAbstractClass(*args, **kwargs):
        """
        isAbstractClass() -> bool
        
        Override this class to return True if this node is an abstract node. An abstract node can only be used as a base class.  It cannot be created using the 'createNode' command.
        
        It is not necessary to override this method.
        """
    
        pass
    
    
    def isPassiveOutput(*args, **kwargs):
        """
        isPassiveOutput(plug) -> bool
        
        This method may be overridden by the user defined node if it wants to provide output attributes which do not prevent value modifications to the destination attribute. For example, output plugs on animation curve nodes are passive. This allows the attributes driven by the animation curves to be set to new values by the user.
        
        * plug (MPlug) - plug representing output in question.
        """
    
        pass
    
    
    def legalConnection(*args, **kwargs):
        """
        legalConnection(plug, otherPlug, asSrc) -> bool/None
        
        This method allows you to check for legal connections being made to attributes of this node.
        
        You should return None to specify that maya should handle this connection if you are unable to determine if it is legal.
        
        * plug (MPlug) - attribute on this node.
        * otherPlug (MPlug) - attribute on other node.
        * asSrc (bool) - is this plug a source of the connection.
        """
    
        pass
    
    
    def legalDisconnection(*args, **kwargs):
        """
        legalDisconnection(plug, otherPlug, arsSrc) -> bool/None
        
        This method allows you to check for legal disconnections being made to attributes of this node.
        
        You should return None to specify that maya should handle this disconnection if you are unable to determine if it is legal.
        
        * plug (MPlug) - attribute on this node.
        * otherPlug (MPlug) - attribute on other node.
        * asSrc (boool) - is this plug a source of the connection.
        """
    
        pass
    
    
    def name(*args, **kwargs):
        """
        name() -> string
        
        Returns the name of this particular instance of this class.  Each objectin the dependency graph has a name.  This name will be used by the UIand by MEL.
        
        It is not necessary to override this method.
        
        Returns the name of the node
        """
    
        pass
    
    
    def passThroughToMany(*args, **kwargs):
        """
        passThroughToMany(plug, plugArray) -> bool
        
        This method is overriden by nodes that want to control the traversal behavior of some Maya search algorithms which traverse the history/future of shape nodes looking for directly related nodes. In particular, the Artisan paint code uses this method when searching for paintable nodes, and the disk cache code uses this method when searching for upstream cacheFile nodes.
        
        If this method is not implemented or returns False, the base class Maya implementation of this method calls passThroughToOne and returns the results of that call.
        
        * plug (MPlug) - the plug.
        * plugArray (MPlugArray) - the corresponding plugs.
        """
    
        pass
    
    
    def passThroughToOne(*args, **kwargs):
        """
        passThroughToOne(plug) -> plug
        
        This method may be overriden by nodes that have a one-to-one relationship between an input attribute and a corresponding output attribute. This method is used by Maya to perform the following capabilities:
        
        - When this node is deleted, the delete command will rewire the source of the input attribute to the destination of the output attribute if the source and destination are connected to nodes that are not deleted.
        - History traversal algorithms such as the bakePartialHistory command use this method to direct its traversal through a shape's construction history.
        - The base class Maya implementation of passThroughToAll will call this method if passThroughToAll returns False.
        
        * plug (MPlug) - the plug.
        """
    
        pass
    
    
    def postConstructor(*args, **kwargs):
        """
        postConstructor() -> self
        
        Internally maya creates two objects when a user defined node is created, the internal MObject and the user derived object.
        The association between the these two objects is not made until after the MPxNode constructor is called. This implies that no MPxNode member function can be called from the MPxNode constructor.
        The postConstructor will get called immediately after the constructor when it is safe to call any MPxNode member function.
        """
    
        pass
    
    
    def setDependentsDirty(*args, **kwargs):
        """
        setDependentsDirty(plug, plugArray) -> self
        
        This method can be overridden in user defined nodes to specify which plugs should be set dirty based upon an input plug which Maya is marking dirty. The list of plugs for Maya to mark dirty is returned by the plug array. This method handles both dynamic as well as non-dynamic plugs and is useful in the following ways:
        
        
        
        - Allows attributeAffects-style relationships to be handled for dynamically-added attributes. Since MPxNode.attributeAffects() can only be used with non-dynamic attributes, use of this method allows a way for all attributes of a node to affect one another, both dynamic and non-dynamic.
        
        - Provides more flexible relationships than what is available with MPxNode.attributeAffects(). For example, you may wish to not dirty plugs when the current frame is one. However, as the routine is called during dirty propagation, there are restrictions on what can be done within the routine, most importantly you must not cause any dependency graph computation. For details, see the IMPORTANT NOTE below.
        
        
        
        This method is designed to work harmoniously with MPxNode.attributeAffects() on the same node. Alternately, you can do all affects relationships within a yourNode.setDependentsDirty() implementation.
        
        The body of a user-implemented setDependentsDirty() implementation might look like the following example, which causes the plug called "B" to be set dirty whever plug "A" is changed, i.e. A affects B.
        
        * plug (MPlug) - plug which is being set dirty by Maya.
        * plugArray the programmer should add any plugs which they want to set dirty to this list.
        """
    
        pass
    
    
    def setDoNotWrite(*args, **kwargs):
        """
        setDoNotWrite(bool) -> self
        
        Use this method to mark the "do not write" state of this proxy node.  If set, this node will not be saved when the Maya model is written out. 
        
        NOTES:
        1. Plug-in "requires" information will be written out with the model when saved.  But a subsequent reload and resave of the file will cause these to go away.
        2. If this node is a DAG and has a parent or children, the "do not write" flag of the parent or children will not be set. It is the developer's responsibility to ensure that the resulting scene file is capable of being read in without errors due to unwritten nodes.
        """
    
        pass
    
    
    def setExternalContent(*args, **kwargs):
        """
        setExternalContent(table) -> self
        
        This is useful in the context of content relocation.  This will be called while the scene is being loaded to apply path changes performed externally. Consequently, interaction with the rest of the scene must be kept to a minimum.  It is however valid to call this method outside of scene loading contexts.
        
        The keys in the map must be the same as the ones provided by the node in getExternalContent.  The values are the new locations.
        
        When implementing setExternalContent, you are responsible for forwarding the call to the base class when it makes sense to do so, so that base classes  can also set their external content.
        
        The default implementation does nothing.
        
        * table Key->location table with new content locations.
        """
    
        pass
    
    
    def setExternalContentForFileAttr(*args, **kwargs):
        """
        setExternalContentForFileAttr(attr, table) -> bool
        
        This method is a helper for derived clases implementing setExternalContent().  It assigns a value to a plug with the one from the table whose key is the same as the passed in attribute name.
        
        The method will not write to the plug if the attribute is not found in the  table.
        
        * attr (MObject) - The attribute of the plug we want to write to.
        * table (MExternalContentLocationTable) - A table which may hold or not the value for a given plug.
        
        Returns True if the plug was successfully written to. False if no entry in the table was named after the attribute or if no plug was found.
        """
    
        pass
    
    
    def setInternalValueInContext(*args, **kwargs):
        """
        setInternalValueInContext(plug, dataHandle, ctx) -> bool
        
        This method is overriden by nodes that store attribute data in some internal format.
        
        The internal state of attributes can be set or queried using the setInternal and internal methods of MFnAttribute.
        
        When internal attribute values are set via setAttr or MPlug.setValue() this method is called.
        
        Another use for this method is to impose attribute limits.
        
        * plug (MPlug) - the attribute that is being set.
        * dataHandle (MDataHandle) - the dataHandle containing the value to set.
        * ctx (MDGContext) - the context the method is being evaluated in.
        """
    
        pass
    
    
    def setMPSafe(*args, **kwargs):
        """
        setMPSafe(bool) -> self
        
        Set a flag to specify if a user defined shading node is safe for multi-processor rendering. For a shading node to be MP safe, it cannot access any shared global data and should only use attributes in the datablock to get input data and store output data. 
        
        This flag does NOT mark a node thread safe for parallel DG evaluation in Viewport 2.0.  To mark a node thread safe for parallel DG evaluation see the setNodeTypeFlag mel command. 
        
        NOTE: This should be called from the postConstructor() method for shading node plug-ins only. If a shading node is non-safe, then it will only be useful during single processor rendering.
        """
    
        pass
    
    
    def shouldSave(*args, **kwargs):
        """
        shouldSave(plug) -> bool/None
        
        This method may be overridden by the user defined node.  It should only be required to override this on rare occasions.
        
        This method determines whether a specific attribute of this node should be written out during a file save.  The default behavior is to only write the value if it differs from the default and is not being supplied by a connection.  This behavior should be sufficient in most cases.
        This method is not called for ramp attributes since they should always be written.
        
        * plug (MPlug) - plug representing the attribute to be saved.
        """
    
        pass
    
    
    def thisMObject(*args, **kwargs):
        """
        thisMObject() -> MObject
        
        Returns the MObject associated with this user defined node.  This makes it possible to use MFnDependencyNode or to construct plugs to this node's attributes.
        """
    
        pass
    
    
    def type(*args, **kwargs):
        """
        type() -> int
        
        Returns the type of node that this is.  This is used to differentiate user defined nodes that are derived off different MPx base classes.
        
        It is not necessary to override this method.
        
          kDependNode                    Custom node derived from MPxNode
          kLocatorNode                   Custom locator derived from MPxLocatorNode
          kDeformerNode                  Custom deformer derived from MPxDeformerNode
          kManipContainer                Custom container derived from MPxManipContainer
          kSurfaceShape                  Custom shape derived from MPxSurfaceShape
          kFieldNode                     Custom field derived from MPxFieldNode
          kEmitterNode                   Custom emitter derived from MPxEmitterNode
          kSpringNode                    Custom spring derived from MPxSpringNode
          kIkSolverNode                  Custom IK solver derived from MPxIkSolverNode
          kHardwareShader                Custom shader derived from MPxHardwareShader
          kHwShaderNode                  Custom shader derived from MPxHwShaderNode
          kTransformNode                 Custom transform derived from MPxTransform
          kObjectSet                     Custom set derived from MPxObjectSet
          kFluidEmitterNode              Custom fluid emitter derived from MpxFluidEmitterNode
          kImagePlaneNode                Custom image plane derived from MPxImagePlane
          kParticleAttributeMapperNode   Custom particle attribute mapper derived from MPxParticleAttributeMapperNode
          kCameraSetNode                 Custom director derived from MPxCameraSet
          kConstraintNode                Custom constraint derived from MPxConstraint
          kManipulatorNode               Custom manipulator derived from MPxManipulatorNode
          kClientDeviceNode              Custom threaded device derived from MPxThreadedDeviceNode
          kThreadedDeviceNode            Custom threaded device node
          kAssembly                      Custom assembly derived from MPxAssembly
          kSkinCluster                                  Custom deformer derived from MPxSkinCluster
          kGeometryFilter                               Custom deformer derived from MPxGeometryFilter
                 kBlendShape                                    Custom deformer derived from MPxBlendShape
        """
    
        pass
    
    
    def typeId(*args, **kwargs):
        """
        typeId() -> MTypeId
        
        Returns the TYPEID of this node.
        """
    
        pass
    
    
    def typeName(*args, **kwargs):
        """
        typeName() -> string
        
        Returns the type name of this node.  The type name identifies the node type to the ASCII file format
        """
    
        pass
    
    
    def addAttribute(*args, **kwargs):
        """
        addAttribute(attr) -> None
        
        This method adds a new attribute to a user defined node type during the type's initialization.
        
        This method will only work during the static initialization method of the user defined node class.  The initialization method is the one that is passed into  MFnPlugin.registerNode(). The attributes must first be created using one of the MFnAttribute classes, and can then be added using this method.
        
        For compound attributes, the proper way to use this method is by calling it with the parent attribute. If a compound attribute is passed, this method will add all of its children.
        NOTE: A failure will occur if you attempt to call addAttribute() on the children of a compound attribute.
        
        * attr (MObject) - new attribute to add.
        """
    
        pass
    
    
    def attributeAffects(*args, **kwargs):
        """
        attributeAffects(whenChanges, isAffected) -> None
        
        This method specifies that a particular input attribute affects a specific output attribute.  This is required to make evaluation efficient.  When an input changes, only the affected outputs will be computed. Output attributes cannot be keyable - if they are keyable, this method will fail.
        
        This method must be called for every attribute dependency when initializing the node's attributes.  The attributes must first be added using the MPxNode.addAttribute() method.  Failing to call this method will cause the node not to update when its inputs change. If there are no calls to this method in a node's initialization, then the compute method will never be called.
        
        This method will only work during the static initialization method of the user defined node class.  The initialization method is the one that is passed into MFnPlugin.registerNode().  As a result, it does not work with dynamic attributes. For an alternate solution which handles dynamic as well as non-dynamic attributes refer to MPxNode.setDependentsDirty.()
        
        * whenChanges (MObject) - input attribute - MObject that points to an input attribute that has already been added.
        * isAffected (MObject) - affected output attribute - MObject that points to an output attribute that has already been added.
        """
    
        pass
    
    
    def inheritAttributesFrom(*args, **kwargs):
        """
        inheritAttributesFrom(parentClassName) -> None
        
        This method allows a class of plugin node to inherit all of the attributes of a second class of plugin node.
        
        This method will only work during the static initialization method of the user defined node class and must be called before any other attributes have been added.  The initialization method is the one that is passed into  MFnPlugin.registerNode().
        
        A plugin node may only inherit attributes from one other class of plugin node. Attempting to call this method multiple times within a node's initialization method will result in an error.
        
        Both node classes must be registered using the same MPxNode type, listed in MPxNode.type().
        
        * parentClassName (string) - class of node to inherit attributes from.
        """
    
        pass
    
    
    __new__ = None
    
    
    kAssembly = 22
    
    
    kBlendShape = 25
    
    
    kCameraSetNode = 16
    
    
    kClientDeviceNode = 20
    
    
    kConstraintNode = 17
    
    
    kDeformerNode = 2
    
    
    kDependNode = 0
    
    
    kEmitterNode = 6
    
    
    kFieldNode = 5
    
    
    kFluidEmitterNode = 13
    
    
    kGeometryFilter = 24
    
    
    kHardwareShader = 9
    
    
    kHwShaderNode = 10
    
    
    kIkSolverNode = 8
    
    
    kImagePlaneNode = 14
    
    
    kLast = 26
    
    
    kLocatorNode = 1
    
    
    kManipContainer = 3
    
    
    kManipulatorNode = 18
    
    
    kMotionPathNode = 19
    
    
    kObjectSet = 12
    
    
    kParticleAttributeMapperNode = 15
    
    
    kSkinCluster = 23
    
    
    kSpringNode = 7
    
    
    kSurfaceShape = 4
    
    
    kThreadedDeviceNode = 21
    
    
    kTransformNode = 11


from . import nodeList
from . import nodeNotes
from . import serializableNode

class RenderSetup(nodeList.ListBase, nodeNotes.NodeNotes, serializableNode.SerializableNode, _MPxNode):
    """
    Singleton node that manages a list of render layers.
    
    The render setup node is a singleton: at most one can exist in a scene.
    It is not implemented as a default node, and therefore is not created
    on file new, but rather created on demand.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def acceptImport(*args, **kwargs):
        pass
    
    
    def addActiveLayerObserver(self, obsMethod):
        pass
    
    
    def addSceneObserver(self, obsMethod):
        pass
    
    
    def ancestors(self):
        """
        Returns a single-element deque with the render setup node itself.
        """
    
        pass
    
    
    def appendRenderLayer(self, renderLayer):
        pass
    
    
    def attachRenderLayer(self, pos, renderLayer):
        """
        Attach a render layer at a specific position
        """
    
        pass
    
    
    def clearAll(self):
        """
        Clear the render setup by deleting all its render layers
        """
    
        pass
    
    
    def createRenderLayer(*args, **kwargs):
        pass
    
    
    def decode(*args, **kwargs):
        pass
    
    
    def detachRenderLayer(self, renderLayer):
        """
        Detach a render layer whatever is its position
        """
    
        pass
    
    
    def dispose(self):
        pass
    
    
    def encode(self, notes=None, includeSceneSettings=True):
        pass
    
    
    def getDefaultRenderLayer(self):
        pass
    
    
    def getRenderLayer(self, renderLayerName):
        """
        Look for an existing render layer by name.
        
        @type renderLayerName: string
        @param renderLayerName: Name of render layer to look for
        @rtype: RenderLayer model instance
        @return: Found instance or throw an exception
        """
    
        pass
    
    
    def getRenderLayers(self):
        pass
    
    
    def getVisibleRenderLayer(self):
        pass
    
    
    def parent(self):
        """
        Returns None, as the render setup node is the root of the hierarchy.
        """
    
        pass
    
    
    def removeActiveLayerObserver(self, obsMethod):
        pass
    
    
    def removeSceneObserver(self, obsMethod):
        pass
    
    
    def switchToLayer(*args, **kwargs):
        pass
    
    
    def switchToLayerUsingLegacyName(self, renderLayerName):
        """
        Set the argument render layer as the visible render layer
        """
    
        pass
    
    
    def typeName(self):
        pass
    
    
    def canOverride(nodeName, attrName):
        """
        The method checks if an override could be 'applied' to the specified node/attribute
        """
    
        pass
    
    
    def creator():
        pass
    
    
    def initializer():
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    firstRenderLayer = None
    
    
    kTypeId = None
    
    
    kTypeName = 'renderSetup'
    
    
    lastRenderLayer = None
    
    
    renderLayers = None



def initialize():
    pass


def removeObserver(obs):
    """
    Remove an observer from this list.
    
    Observers are kept as weak references.  ValueError is raised by the 
    remove listItem method if the argument observer is not found.
    """

    pass


def instance():
    """
    Return the render setup singleton node, creating it if required.
    """

    pass


def _createInstance(*args, **kwargs):
    pass


def addObserver(obs):
    """
    Add a render setup observer.
    
    Observers are kept as weak references.  The order in which
    observers are called is unspecified.
    """

    pass


def hasInstance():
    """
    Return true if the render setup node exists
    """

    pass


def finalize():
    pass


def _fileRefErrMsg(when, what, resolvedRefPath):
    pass



DECODE_AND_OVERWRITE = 0

kRenderSetupNodeNameMismatch = []

kUnknownRenderLayer = []

kFileRefCbFailed = []

kSyncingActiveLayerMessage = []

kLoading = []

kInvalidRenderLayerName = []

_RENDER_SETUP_TYPE = 'renderSetup'

kRenderSetupNodeTypeMismatch = []

kUnloading = []

_RENDER_SETUP_NAME = ':renderSetup'

kAfter = []

DECODE_AND_RENAME = 2

_subject = _Subject()

kBefore = []

_autoAdjustements = False

DECODE_AND_MERGE = 1


