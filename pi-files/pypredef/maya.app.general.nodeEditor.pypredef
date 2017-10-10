"""
Plugin Support:

Plugins providing nodes with a custom creation script should add
callbacks to the lists:

pluginNodeClassificationCallbacks
pluginNodeCreationCallbacks

Following the Mentalray example at the bottom of this file.
"""

class NodeEditor(object):
    """
    Encapsulates one Node Editor panel instance.
    """
    
    
    
    def __init__(self, ned):
        pass
    
    
    def buildMenus(self):
        """
        Create any required UI for this editor
        """
    
        pass
    
    
    __dict__ = None
    
    __weakref__ = None



def mrClassificationCB():
    """
    eturn classification root of all nodes handled by the corresponding create callback.
    """

    pass


def mrNodeCategories():
    pass


def _findCustomCreateCommand2012(nodeType):
    """
    Implementation of _findCustomCreateCommand for 2012
    """

    pass


def _findStandardCreateCommand(nodeType):
    """
    Locate a standard create command based on classification cateogries
    """

    pass


def _findCustomCreateCommand(nodeType):
    """
    Locate a custom command to create this nodeType, based on registered 
    custom classification categories. Return None if no match.
    """

    pass


def createNode(nodeType):
    """
    Called by the editor to create a new node based on the supplied type.
    """

    pass


def addCallback(ned):
    """
    Create any required UI
    """

    pass


def removeCallback(ned):
    """
    Clean up any UI
    """

    pass


def createCallback(ned):
    """
    Do non-UI initialization
    """

    pass


def mrCreateNodeCB(postCmd, nodeType):
    """
    If the given node is Mentalray, return a MEL command which will create
    an instance of the supplied node type.  Return None if the given node
    is not handled by Mayatomr.
    
    \param[in] postCmd - MEL code to be executed after creation
    \param[in] nodeType - The type of the node to be created
    eturn MEL command which creates the given node, or None
    """

    pass


def nEd(*args, **kwargs):
    pass


def buildPanelMenus(ned):
    """
    Do the python menu creation.
    This is called by nodeEdBuildPanelMenus
    """

    pass


def mayaNodeCategories():
    pass



pluginNodeCreationCallbacks = []

editors = {}

_createNodeTable = []

_mrCreateNodeTable = []

pluginNodeClassificationCallbacks = []


