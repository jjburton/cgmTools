"""
This module provides the render layer class, as well as utility
functions to operate on render layers.


Note:
    In order to better control the update of the render layer, two flags were added 
    to each render layer instance to control the update of 1) the list of nodes owned
    by the legacy layer and 2) the rendering. The controls were introduced to avoid
    performance penalty on any user requests.
    
    The flag RenderLayer.needsMembershipUpdate is set to True when the list of nodes 
    part of the render layer changed meaning that the legacy layer must be updated. 
    The update is managed by an evalDeferred() so it will only be executed during 
    the next idle time. If an update is already planned, 
    the flag RenderLayer.isUpdatingMembership will be True. These flags only apply
    to the visible render layer. No updates are performed on the not visible ones.
    
    The flag RenderLayer.needsRenderingUpdate is set to True when the rendering must be updated. 
    The default dirty mechanism of the scene is not enough as the render setup behavior implies
    to sometime apply or unapply some overrides. The first 'not optimized' implementation 
    of the rendering refresh is to impose a switchToLayer() 
    (i.e. unapply and apply all overrides). This flag only applies to the visible render layer. 
    No updates are performed on the not visible ones.
"""

from maya.app.renderSetup.model.observable import Observable

class RenderLayerBase(object):
    """
    Abstract base class for RenderLayer and DefaultRenderLayer classes
    Defines functions for toggling visibility and renderability.
    Children must implement:
      - _getLegacyNodeName()
      - _updateLegacyRenderLayerVisibility()
      - apply()
      - unapply()
    """
    
    
    
    def __init__(self):
        pass
    
    
    def isRenderable(self):
        pass
    
    
    def isVisible(self):
        pass
    
    
    def makeVisible(self):
        pass
    
    
    def setRenderable(self, value):
        pass
    
    
    __dict__ = None
    
    __weakref__ = None


class DefaultRenderLayer(RenderLayerBase, Observable):
    """
    Singleton class to access and modify default render layer properties
    This singleton instance is also observable: it will notify observers
    on visibility and renderability changes.
    
    Singleton instance belongs to renderSetup instance
    Access it using renderSetup.instance().getDefaultRenderLayer()
    """
    
    
    
    def __init__(self):
        pass
    
    
    def apply(self):
        pass
    
    
    def clearMemberNodesCache(self):
        pass
    
    
    def hasLightsCollectionInstance(self):
        pass
    
    
    def hasOverride(self, nodeName, attrName):
        pass
    
    
    def name(self):
        pass
    
    
    def needsRefresh(self):
        pass
    
    
    def unapply(self):
        pass


from . import nodeList
from . import overrideManager
from . import childNode

class RenderLayer(RenderLayerBase, nodeList.ListBase, overrideManager.OverrideManager, childNode.ChildNode):
    """
    Render layer node.
    
    A render layer has an ordered list of collections.  It can
    optionally have an ordered list of overrides.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def acceptImport(self):
        pass
    
    
    def aovCollectionInstance(self):
        """
        Get the AOV collection instance for this render layer,
        creating it if it doesn't exists as long as renderer 
        callbacks are registered for the current renderer.
        """
    
        pass
    
    
    def appendChild(*args, **kwargs):
        pass
    
    
    def appendCollection(*args, **kwargs):
        pass
    
    
    def apply(*args, **kwargs):
        pass
    
    
    def attachChild(self, pos, child):
        """
        Attach a collection at a specific position
        """
    
        pass
    
    
    def attachCollection(self, pos, child):
        """
        Attach a collection at a specific position
        """
    
        pass
    
    
    def attachOverride(self, overrideName):
        pass
    
    
    def clearMemberNodesCache(self):
        pass
    
    
    def createAbsoluteOverride(*args, **kwargs):
        pass
    
    
    def createCollection(*args, **kwargs):
        pass
    
    
    def createRelativeOverride(*args, **kwargs):
        pass
    
    
    def detachChild(*args, **kwargs):
        pass
    
    
    def detachCollection(*args, **kwargs):
        pass
    
    
    def getChildren(self):
        """
        Get list of all existing Collections
        """
    
        pass
    
    
    def getCollection(self, collectionName):
        """
        Look for an existing collection by name
        """
    
        pass
    
    
    def getCollections(self):
        """
        Get list of all existing Collections
        """
    
        pass
    
    
    def getDefaultCollection(self):
        """
        Get the default collection where newly created nodes are placed
        """
    
        pass
    
    
    def getEnabledSelectedNodeNames(self):
        """
        Get a list of all selected node names in the layer 
        based on whether a collection is enabled or solo'ed. 
        
        @rtype: list
        @return: list of node names. Empty if none found.
        """
    
        pass
    
    
    def getFirstCollectionIndex(self):
        pass
    
    
    def getOverrides(self):
        pass
    
    
    def hasAOVCollectionInstance(self):
        """
        Returns True if this layer has the AOV collection instance created.
        """
    
        pass
    
    
    def hasCollection(self, collectionName):
        pass
    
    
    def hasDefaultCollection(self):
        """
        Get the default collection where newly created nodes are placed
        """
    
        pass
    
    
    def hasLightsCollectionInstance(self):
        """
        Returns True if this layer has the lights collection instance created.
        """
    
        pass
    
    
    def hasOverride(self, nodeName, attrName):
        """
        Check if at least one collection holds an override
        """
    
        pass
    
    
    def hasRenderSettingsCollectionInstance(self):
        """
        Returns True if this layer has the render settings collection instance created.
        """
    
        pass
    
    
    def isAbstractClass(self):
        pass
    
    
    def isAcceptableChild(self, model):
        """
        Check if the model could be a child of the render layer model
        """
    
        pass
    
    
    def lightsCollectionInstance(self):
        """
        Get the lights collection instance for this render layer,
        creating it if it doesn't exists.
        """
    
        pass
    
    
    def needsRefresh(self):
        """
        Following some changes the instance must be updated.
        """
    
        pass
    
    
    def renderSettingsCollectionInstance(self):
        """
        Get the render settings collection instance for this render layer,
        creating it if it doesn't exists.
        """
    
        pass
    
    
    def setName(*args, **kwargs):
        pass
    
    
    def typeId(self):
        pass
    
    
    def typeName(self):
        pass
    
    
    def unapply(*args, **kwargs):
        pass
    
    
    def creator():
        pass
    
    
    def initializer():
        pass
    
    
    collectionHighest = None
    
    
    collectionLowest = None
    
    
    collections = None
    
    
    kTypeId = None
    
    
    kTypeName = 'renderSetupLayer'
    
    
    legacyRenderLayer = None
    
    
    numIsolatedChildren = None



def delete(*args, **kwargs):
    pass


def _syncLegacyRenderLayers(layerName):
    pass


def create(*args, **kwargs):
    pass



kSetRenderability = []

kCreateAOVChildCollection = []

kCreateAOVCollection = []

kInvalidCollectionName = []

kCreateRenderSettingsCollection = []

kCollectionDetached = []

kCollectionUnicity = []

kCollectionAttached = []

kAttachCollection = []

kUnknownCollection = []

kCreateLightsCollection = []


