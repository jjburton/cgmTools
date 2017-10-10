"""
See class level docstring for more information.
"""

class OverrideManager(object):
    """
    Override manager base class. 
    
    A base class for handling override apply nodes. This class can be derived from in order to 
    add override management to a class. It handles adding and removing of apply nodes when an override is
    applied or unapplied to the derived class.
    The base class has an array of override elements that represents the overrides currently applied to
    the scene. Each such element holds a connection from the target attribute (the attribute being overridden)
    and a connection from the apply node operating on that attribute. If there are more than one apply node 
    operating on the same target attribute they form a chain where the first one in the chain is connected
    to the element.
    """
    
    
    
    def addConnectionOverride(self, overrideNode, name, target, nextOvr=None):
        """
        Add a new override to be handled by the manager.
        """
    
        pass
    
    
    def getOverridesArrayPlug(self):
        pass
    
    
    def updateOverrides(self):
        """
        Update all overrides that are currently applied.
        """
    
        pass
    
    
    def initOverrideManager(cls):
        """
        Initialize the class adding all needed attributes.
        """
    
        pass
    
    
    def removeConnectionOverride(cls, overrideNode):
        """
        Restore the override.
        Removing all apply nodes for this override node.
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None
    
    aApplyNode = None
    
    
    aOverrides = None
    
    
    aTarget = None



def _createNode(nodeName, nodeTypeId):
    """
    Create a node of given name and type.
    """

    pass



