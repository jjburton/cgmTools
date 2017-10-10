"""
This module provides the drag and drop base and concrete classes.

They are derived from the API class MPxDragAndDropBehavior and are
used to handle the connections to make when the user drops a node 
or an attribute on to another node or attribute.

The interface to implement for each derived class is the following:

    - shouldBeUsedFor(sourceNode, destinationNode, sourcePlug, destinationPlug) -> bool
        # Returns True if the class should be used for this connection

    - connectAttrToAttr(sourcePlug, destinationPlug, force) -> None
        # Create all connections needed when sourcePlug is dropped on destinationPlug

    - connectAttrToNode(sourcePlug, destinationNode, force) -> None
        # Create all connections needed when sourcePlug is dropped on destinationNode

    - connectNodeToAttr(sourceNode, destinationPlug, force) -> None
        # Create all connections needed when sourceNode is dropped on destinationPlug

    - connectNodeToNode(sourceNode, destinationNode, force) -> None
        # Create all connections needed when sourceNode is dropped on destinationNode
"""

from maya.app.renderSetup.model.connectionOverride import *

class _MPxDragAndDropBehavior(object):
    """
    This is the base class for user defined drag and drop behaviors.
    """
    
    
    
    def __init__(*args, **kwargs):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
    
        pass
    
    
    def connectAttrToAttr(*args, **kwargs):
        """
        connectAttrToAttr(sourcePlug, destinationPlug, force) -> None
        
        This method is called by the defaultNavigation command to connect a source attribute to a destination attribute.
        
        If this method is overidden it should attempt to determine what the user probably wants this connection to be, and set up the connection appropriately. If the force argument is true it is intended to notify the user to break any existing connections to the plug, similar to what the mel command 'connectAttr' -f flag is used for.
        
        * sourcePlug (MPlug) - Source plug in the connection.
        * destinationPlug (MPlug) - Destination plug in the connection.
        * force (bool) - Tells whether or not to break any existing connections to the destination attribute.
        """
    
        pass
    
    
    def connectAttrToNode(*args, **kwargs):
        """
        connectAttrToNode(sourcePlug, destinationNode, force) -> None
        
        This method is called by the defaultNavigation command to connect a source attribute to a destination node.
        
        You should override this method if you can determine from the type of source node and attribute and the type of destination node what the user is trying to do and you know the appropriate connections that must be made for the end result to be what the user expects.
        
        * sourcePlug (MPlug) - Source plug in the connection.
        * destinationNode (MObject) - Destination node for the connection.
        * force (bool) - Tells whether or not to break any existing connections to the destination node.
        """
    
        pass
    
    
    def connectNodeToAttr(*args, **kwargs):
        """
        connectNodeToAttr(sourceNode, destinationPlug, force) -> None
        
        This method is called by the defaultNavigation command to connect a source node to a destination attribute.
        
        You should override this method if you can determine from the type of source node and the type of destination node and attribute what the user is trying to do and you know the appropriate connections that must be made for the end result to be what the user expects.
        
        * sourceNode (MObject) - Source node in the connection.
        * destinationPlug (MPlug) - Destination plug for the connection.
        * force (bool) - Tells whether or not to break any existing connections to the destination attribute.
        """
    
        pass
    
    
    def connectNodeToNode(*args, **kwargs):
        """
        connectNodeToNode(sourceNode, destinationNode, force) -> None
        
        This method is called by the defaultNavigation command to connect a source node to a destination node.
        
        You should override this method if you can determine from the type of source node and the type of destination node what the user is trying to do and you know the appropriate connections that must be made for the end result to be what the user expects.
        
        * sourceNode (MObject) - Source node in the connection.
        * destinationNode (MObject) - Destination node for the connection.
        * force (bool) - Tells whether or not to break any existing connections to the destination node.
        """
    
        pass
    
    
    def shouldBeUsedFor(*args, **kwargs):
        """
        shouldBeUsedFor(sourceNode, destinationNode, sourcePlug, destinationPlug) -> bool
        
        This method must be overridden in order to use a drag and drop behavior.
        
        The overridden method will be called by the defaultNavigation command to determine wether or not to use this drag and drop behavior to finish a connection. If the user would like to handle the connection between sourceNode/Plug and destinationNode/Plug then this routine must pass back true, otherwise the routine must pass back false in order for the default connection mechanism to work between these two nodes. sourcePlug and destinationPlug may be null depending on if there were any attributes given in the drag and drop. Use the isNull() method on MPlug to assure the plugs are valid.
        
        * sourceNode (MObject) - The source node of the drag and drop or the node being dragged.
        * destinationNode (MObject) - the destination node of the drag and drop or the node being dropped upon.
        * sourcePlug (MPlug) - The source plug of the drag and drop or the plug being dragged (this may be null).
        * destinationPlug (MPlug) - The destination plug of the drag and drop or the plug being dropped upon (this may be null).
        """
    
        pass
    
    
    __new__ = None


class DragAndDropBehavior(_MPxDragAndDropBehavior):
    """
    Base class for drag and drop behavior for render setup nodes.
    """
    
    
    
    def connect(sourcePlug, destinationPlug):
        """
        Try to connect two plugs and catch any plug type mismatches.
        """
    
        pass
    
    
    def findCandidatePlug(sourceNode, destinationPlug):
        """
        Return a plug to the first matching attribute in the candidate list.
        If no attribute is found, None is returned.
        """
    
        pass
    
    
    def findNode(node, typeId=4, acceptor=None):
        """
        Find a node of given type in a network, starting with the given node
        and searching downstream if needed. If an acceptor, user defined callable,
        is given we use that to accept or reject nodes during the search.
        
        The acceptor signature should be: func(MObject) -> bool
        """
    
        pass
    
    
    def isMatchingClass(node, classificationString):
        """
        Returns True if the given node has a matching classification string.
        """
    
        pass
    
    
    def raiseWarning(msg):
        """
        Give an warning message to the user to avoid raising an exception here.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    kAttributeCandidates = []
    
    
    kErrorMsg_IncompatibleTypes = []
    
    
    kErrorMsg_NoAttributeFound = []
    
    
    kErrorMsg_NoShadingGroup = []
    
    
    kErrorMsg_NoShadingGroupFound = []
    
    
    kErrorMsg_NoSurfaceShader = []
    
    
    kErrorMsg_NoSurfaceShaderFound = []


class ConnectionOverrideDragAndDrop(DragAndDropBehavior):
    """
    Class handling drag and drop for connection override nodes.
    """
    
    
    
    def __init__(self):
        pass
    
    
    def connectAttrToAttr(self, sourcePlug, destinationPlug, force):
        """
        Handle connection requests from source attribute to destination attribute.
        """
    
        pass
    
    
    def connectAttrToNode(self, sourcePlug, destinationNode, force):
        """
        Handle connection requests from source attribute to destination node.
        """
    
        pass
    
    
    def connectNodeToAttr(self, sourceNode, destinationPlug, force):
        """
        Handle connection requests from source node to destination attribute.
        """
    
        pass
    
    
    def connectNodeToNode(self, sourceNode, destinationNode, force):
        """
        Handle connection requests from source node to destination node.
        """
    
        pass
    
    
    def shouldBeUsedFor(self, sourceNode, destinationNode, sourcePlug, destinationPlug):
        """
        Return True if the given nodes/plugs are handled by this class.
        """
    
        pass
    
    
    def creator():
        pass
    
    
    kNodeSearchIgnoreList = []
    
    
    kTypeName = 'connectionOverrideDragAndDrop'



