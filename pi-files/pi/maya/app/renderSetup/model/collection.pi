"""
This module provides the collection class, as well as utility
functions to operate on collections.

The collection owns its associated selector node: on collection
delete, the collection is deleted as well.
"""

from . import nodeList
from . import childNode

class Collection(nodeList.ListBase, childNode.TreeOrderedItem, childNode.ChildNode):
    """
    Collection node.
    
    A collection has an ordered list of children, and a selector to
    determine nodes to which the children apply.
    
    MAYA-59277: 
      - When we start implementing proper hierarchical collections we 
        need to decide on the relationship between parent and child
        selectors. Do we always consider a parent collection to be the 
        union of its child collections, and propagate the selector 
        information upwards when a child collection is added or changed?
        Or do we go the opposite direction and restrict the child collection
        to use the intersection between its selector and its parent's selector?
    
      - Light child collections always have a single light source member.
        We should utilize this and create a specific selector for such
        use cases for better performance.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def acceptImport(self):
        pass
    
    
    def activate(self):
        """
        Called when this list item is inserted into the list.
        Override this method to do any scene specific initialization.
        """
    
        pass
    
    
    def appendChild(*args, **kwargs):
        pass
    
    
    def apply(self, parentSelection=None):
        """
        Apply all children in this collection.
        """
    
        pass
    
    
    def attachChild(*args, **kwargs):
        pass
    
    
    def compute(self, plug, dataBlock):
        pass
    
    
    def createAbsoluteOverride(*args, **kwargs):
        pass
    
    
    def createCollection(self, collectionName):
        """
        Add a child collection to the Collection.
        """
    
        pass
    
    
    def createOverride(*args, **kwargs):
        pass
    
    
    def createRelativeOverride(*args, **kwargs):
        pass
    
    
    def deactivate(self):
        """
        Called when this list item is removed from the list.
        Override this method to do any scene specific teardown.
        """
    
        pass
    
    
    def detachChild(*args, **kwargs):
        pass
    
    
    def enabledChanged(self):
        pass
    
    
    def getChild(self, childName, cls="<class 'maya.app.renderSetup.model.childNode.ChildNode'>"):
        """
        Look for an existing child by name and optionally class.
        
        @type childName: string
        @param childName: Name of child to look for
        @type cls: class name
        @param cls: Class name for the type of class to look for
        @rtype: Child model instance
        @return: Found instance or throw an exception
        """
    
        pass
    
    
    def getChildren(self, cls="<class 'maya.app.renderSetup.model.childNode.ChildNode'>"):
        """
        Get the list of all children. 
        Optionally only the children matching the given class.
        """
    
        pass
    
    
    def getOverrides(self):
        pass
    
    
    def getRenderLayer(self):
        pass
    
    
    def getSelector(self):
        """
        Return the selector user node for this collection.
        """
    
        pass
    
    
    def hasOverride(self, nodeName, attrName):
        """
        Check if an attribute of a node has at least one associated override
        """
    
        pass
    
    
    def isAbstractClass(self):
        pass
    
    
    def isAcceptableChild(self, model):
        """
        Check if the model could be a child
        """
    
        pass
    
    
    def isEnabled(self):
        pass
    
    
    def isIsolateSelected(self):
        """
        Get if isolate selected. Will always return False in batch mode
        """
    
        pass
    
    
    def isSelfEnabled(self):
        pass
    
    
    def postConstructor(self):
        pass
    
    
    def setIsolateSelected(self, val):
        pass
    
    
    def setSelfEnabled(self, value):
        pass
    
    
    def typeId(self):
        pass
    
    
    def typeName(self):
        pass
    
    
    def unapply(self):
        """
        Unapply all children in this collection.
        """
    
        pass
    
    
    def creator():
        pass
    
    
    def initializer():
        pass
    
    
    childHighest = None
    
    
    childLowest = None
    
    
    children = None
    
    
    enabled = None
    
    
    isolateSelected = None
    
    
    kTypeId = None
    
    
    kTypeName = 'collection'
    
    
    parentEnabled = None
    
    
    parentNumIsolatedChildren = None
    
    
    selector = None
    
    
    selfEnabled = None


class RenderSettingsCollection(Collection):
    """
    Render Settings Collection node.
    
    This collection has an ordered list of children, and a static & const selector
    to determine nodes to which the children apply. The list of nodes is based
    on the selected renderer at the time of creation.
    
    MAYA-66757:
    - A base collection will be needed to factorize commonalities and segregate differences.
    - A static selector is needed which could be the existing static selection or an object set.
    - The name is read-only.
    - The selector content is read-only
    - The render name should be part of the collection so that the settings are clearly linked 
      to the used renderer, or linked using a plug
    """
    
    
    
    def __init__(self):
        pass
    
    
    def appendChild(self, child):
        pass
    
    
    def attachChild(self, pos, child):
        pass
    
    
    def compute(self, plug, dataBlock):
        pass
    
    
    def typeId(self):
        pass
    
    
    def typeName(self):
        pass
    
    
    def containsNodeName(nodeName):
        pass
    
    
    def creator():
        pass
    
    
    def initializer():
        pass
    
    
    kTypeId = None
    
    
    kTypeName = 'renderSettingsCollection'


class LightsCollection(Collection):
    """
    LightsCollection node.
    
    A collection node specific for grouping light sources
    and overrides on those light sources.
    
    This collection should have all light sources as member by default. All nodes 
    matching the light classification should be returned by the selector
    on this collection.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def compute(self, plug, dataBlock):
        pass
    
    
    def createCollection(self, collectionName):
        """
        Add a lights child collection to the Collection.
        """
    
        pass
    
    
    def isAcceptableChild(self, model):
        """
        Check if the model could be a child of the render layer model
        """
    
        pass
    
    
    def typeId(self):
        pass
    
    
    def typeName(self):
        pass
    
    
    def creator():
        pass
    
    
    def initializer():
        pass
    
    
    kTypeId = None
    
    
    kTypeName = 'lightsCollection'


class AOVChildCollection(Collection):
    """
    AOV (arbitrary output variable) Child Collection node.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def compute(self, plug, dataBlock):
        pass
    
    
    def containsNodeName(self, nodeName):
        pass
    
    
    def typeId(self):
        pass
    
    
    def typeName(self):
        pass
    
    
    def creator():
        pass
    
    
    def initializer():
        pass
    
    
    kTypeId = None
    
    
    kTypeName = 'aovChildCollection'


class LightsChildCollection(Collection):
    """
    LightsChildCollection node.
    
    A child collection node specific for one single light source
    and overrides on this light source.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def compute(self, plug, dataBlock):
        pass
    
    
    def typeId(self):
        pass
    
    
    def typeName(self):
        pass
    
    
    def creator():
        pass
    
    
    def initializer():
        pass
    
    
    kTypeId = None
    
    
    kTypeName = 'lightsChildCollection'


class AOVCollection(Collection):
    """
    AOV (arbitrary output variable) parent collection node.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def appendChild(self, child):
        pass
    
    
    def attachChild(self, pos, child):
        pass
    
    
    def compute(self, plug, dataBlock):
        pass
    
    
    def containsNodeName(self, nodeName):
        pass
    
    
    def hasOverride(self, nodeName, attrName):
        """
        # An AOVCollection has no overrides, the child collections have them.
        """
    
        pass
    
    
    def typeId(self):
        pass
    
    
    def typeName(self):
        pass
    
    
    def creator():
        pass
    
    
    def initializer():
        pass
    
    
    kTypeId = None
    
    
    kTypeName = 'aovCollection'



def create(*args, **kwargs):
    pass


def delete(*args, **kwargs):
    pass


def unapply(*args, **kwargs):
    pass



kCollectionMissingSelector = []

kRendererMismatch = []

kInvalidChildName = []

kChildDetached = []

kOverrideCreationFailed = []

CREATE_CMD_NAME = 'Create collection'

kChildAttached = []

kSet = []

kUnknownChild = []

kIncorrectChildType = []


